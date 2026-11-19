from concurrent.futures.process import BrokenProcessPool
from dataclasses import replace

import pytest
from openfisca_core.model_api import YEAR, Variable
from openfisca_france.entities import Famille, FoyerFiscal

from simulator import engine
from simulator.consommation import CODES_2017, DEPENSES_2017, LOYER, PART_DU_TYPE, decile, depenses_imputees, par_usage
from simulator.engine import (
    DEPENSES_PUBLIQUES,
    LOI_ACTUELLE,
    RECETTES,
    SMIC_ACTUEL,
    TAUX_ACTUEL,
    Scenario,
    brut_depuis_net,
    budget,
    calculer,
    loi,
    parametres_retraite,
    retraites,
    simuler,
)
from simulator.mesures import CATALOGUE, Cout, Mesure, ajouter_impot, ajouter_prestation
from simulator.persona import ANNEE, Adulte, Depenses, Persona


def seul(salaire, enfants=()):
    return Persona(adultes=(Adulte(salaire_brut_mensuel=salaire),), enfants=enfants)


def test_scenario_au_taux_actuel_ne_change_rien():
    r = simuler(seul(3000), Scenario(taux_troisieme_tranche_ir=TAUX_ACTUEL))
    assert r["avant"] == r["apres"] and r["ecart_revenu_disponible"] == 0


def test_hausse_du_taux_baisse_le_revenu_dans_la_tranche():
    r = simuler(seul(6000), Scenario(taux_troisieme_tranche_ir=0.35))
    assert r["ecart_revenu_disponible"] < 0
    assert r["apres"]["impot_revenu"] < r["avant"]["impot_revenu"]


def test_revenu_disponible_additionne_ses_composantes():
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=2500), Adulte(salaire_brut_mensuel=2000)), enfants=(10, 10))
    m = simuler(couple, Scenario())["avant"]
    # Chaque montant est arrondi à l'euro séparément.
    assert abs(m["revenu_disponible"] - (m["salaire_net"] + m["impots_directs"] + m["prestations_sociales"])) <= 1


def test_pas_de_rsa_fantome_pour_un_haut_salaire():
    assert simuler(seul(6000), Scenario())["avant"]["prestations_sociales"] == 0


def test_deux_enfants_ouvrent_les_allocations_familiales():
    sans, avec = (
        simuler(Persona(adultes=(Adulte(salaire_brut_mensuel=2500), Adulte(salaire_brut_mensuel=2000)), enfants=e), Scenario())["avant"] for e in ((), (10, 10))
    )
    assert avec["prestations_familiales"] > sans["prestations_familiales"] == 0


def test_ancien_format_de_persona():
    ancien = Persona.model_validate({"salaire_brut_mensuel": 2500, "salaire_brut_mensuel_conjoint": 2000, "enfants": 2})
    assert ancien == Persona(adultes=(Adulte(salaire_brut_mensuel=2500), Adulte(salaire_brut_mensuel=2000)), enfants=(10, 10))


def test_un_loyer_demande_la_commune():
    with pytest.raises(ValueError, match="commune"):
        Persona(adultes=(Adulte(),), loyer_mensuel=600)


def test_un_loyer_ouvre_les_aides_au_logement():
    persona = Persona(adultes=(Adulte(salaire_brut_mensuel=1800),), enfants=(5,), loyer_mensuel=700, code_commune="69123")
    assert calculer(LOI_ACTUELLE, persona)["aides_logement"] > 0


def test_un_retraite_touche_sa_pension_nette():
    m = calculer(LOI_ACTUELLE, Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=1500),)))
    assert 1500 * 12 * 0.85 < m["retraite_nette"] < 1500 * 12


def test_des_parents_etrangers_sans_titre_de_cinq_ans_n_ont_pas_la_prime_d_activite():
    def famille(annees):
        return Persona(adultes=(Adulte(salaire_brut_mensuel=1500, nationalite="MA", annees_titre_sejour=annees),), enfants=(4,))

    assert calculer(LOI_ACTUELLE, famille(2))["minima_sociaux"] == 0 < calculer(LOI_ACTUELLE, famille(6))["minima_sociaux"]


def test_net_et_brut_se_correspondent():
    brut = brut_depuis_net(2000)
    assert abs(calculer(LOI_ACTUELLE, seul(brut))["salaire_net"] / 12 - 2000) < 1


def mesure_de_test(monkeypatch, id, appliquer):
    monkeypatch.setitem(CATALOGUE, id, Mesure(id=id, titre=id, candidats=(), source="", citation="", traduction="", appliquer=appliquer))


def smic_a_13_euros(reforme):
    def modifier(parametres):
        parametres.marche_travail.salaire_minimum.smic.smic_b_horaire.update(start="2025-01-01", value=13.0)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


def test_le_salaire_au_smic_suit_le_smic(monkeypatch):
    mesure_de_test(monkeypatch, "test_smic", smic_a_13_euros)
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, au_smic), calculer(loi(Scenario(mesures=("test_smic",))), au_smic)
    assert apres["salaire_net"] / avant["salaire_net"] == pytest.approx(13.0 / 11.88, rel=0.02)


def test_un_temps_plein_passe_sous_le_nouveau_smic_y_est_releve(monkeypatch):
    mesure_de_test(monkeypatch, "test_smic", smic_a_13_euros)
    scenario = loi(Scenario(mesures=("test_smic",)))
    au_smic, juste_au_dessus, temps_partiel = (calculer(scenario, seul(s))["salaire_net"] for s in (13.0 * 35 * 52 / 12, 1900, 1500))
    assert juste_au_dessus == pytest.approx(au_smic, abs=2)
    assert temps_partiel == calculer(LOI_ACTUELLE, seul(1500))["salaire_net"]


def test_l_ifi_porte_sur_le_patrimoine_immobilier():
    persona = Persona(adultes=(Adulte(salaire_brut_mensuel=6000),), patrimoine_immobilier=2_500_000, residence_principale=1_100_000)
    m = calculer(LOI_ACTUELLE, persona)
    # Base : 70 % de 1,1 M€ + 1,4 M€ = 2,17 M€ ; barème : 0,5 % de 0,8 à 1,3 M€, puis 0,7 % jusqu'à 2,17 M€.
    assert m["impots_directs"] - m["impot_revenu"] == pytest.approx(-(500_000 * 0.005 + 870_000 * 0.007), abs=1)


def test_pas_d_ifi_jusqu_a_1_3_million():
    persona = Persona(adultes=(Adulte(salaire_brut_mensuel=6000),), patrimoine_immobilier=1_200_000)
    m = calculer(LOI_ACTUELLE, persona)
    assert m["impots_directs"] == m["impot_revenu"]


def test_le_decile_de_niveau_de_vie():
    # 16 680 € et 18 990 € de 2018 bornent le 4e décile ; en euros de 2025, un niveau de vie de 20 000 € y tombe.
    assert (decile(5_000), decile(20_000), decile(100_000)) == (1, 4, 10)


def test_une_depense_absente_est_imputee_selon_le_niveau_de_vie():
    m = calculer(LOI_ACTUELLE, Persona(adultes=(Adulte(au_smic=True),), depenses=Depenses(electricite=1800)))
    # Une personne seule compte pour une unité de consommation, et dépense 63 % de ce que dépense le ménage moyen de son décile.
    imputees = depenses_imputees(m["revenu_disponible"], PART_DU_TYPE[1, False])
    assert m["depense_electricite"] == 1800 and m["depense_carburants"] == imputees["carburants"] > 0
    assert imputees["carburants"] == pytest.approx(0.632 * depenses_imputees(m["revenu_disponible"])["carburants"], abs=1)


def test_imputation_hors_energie_d_un_menage_du_premier_decile():
    imputees, prix = depenses_imputees(5_000), 120.95 / 101.22  # euros de 2017 portés à 2025 par l'indice d'ensemble
    assert imputees["hors_energie_taux_particulier"] == round(32 * prix)  # presse (09521)
    # Pharmacie (0611Z), transports (073ZZ), horticulture (09321), services culturels (0942Z), restauration (11111, 11112, 1113Z), hébergement (11211).
    assert imputees["hors_energie_taux_intermediaire"] == round((139 + 457 + 71 + 290 + 150 + 274 + 81 + 88) * prix)


def test_la_consommation_hors_energie_exclut_l_energie_et_complete_le_total_de_l_insee():
    ctotale = (16123, 18322, 20071, 22638, 23787, 27081, 29059, 32645, 35867, 48353)  # TF106, total de la consommation, déciles 1 à 10
    assert not [code for code in CODES_2017 if code.startswith("045") or code == "07221"]
    for i, total in enumerate(ctotale):
        energie = DEPENSES_2017["energie_logement"][i] + DEPENSES_2017["carburants"][i]
        assert energie + sum(valeurs[i] for taux, valeurs in CODES_2017.values() if taux) <= total
        assert energie + sum(valeurs[i] for _, valeurs in CODES_2017.values()) == pytest.approx(total, abs=5)  # arrondis du TF106


def test_le_scenario_garde_la_consommation_de_la_loi_actuelle():
    r = simuler(seul(3000), Scenario(taux_troisieme_tranche_ir=0.31))
    assert r["apres"]["tva"] == r["avant"]["tva"] and r["ecart_pouvoir_achat"] == r["ecart_revenu_disponible"]


def test_la_residence_principale_fait_partie_du_patrimoine_immobilier():
    with pytest.raises(ValueError, match="résidence principale"):
        Persona(adultes=(Adulte(),), patrimoine_immobilier=100_000, residence_principale=200_000)


def test_les_impots_et_prestations_des_mesures_se_cumulent(monkeypatch):
    class taxe_test(Variable):
        value_type = float
        entity = FoyerFiscal
        definition_period = YEAR

        def formula(foyer_fiscal, period):
            return foyer_fiscal("patrimoine_financier", period) * 0.01

    class cheque_test(Variable):
        value_type = float
        entity = Famille
        definition_period = YEAR

        def formula(famille, period):
            return famille.nb_persons() * 100

    class cheque_test_bis(Variable):
        value_type = float
        entity = Famille
        definition_period = YEAR

        def formula(famille, period):
            return famille.nb_persons() * 10

    mesure_de_test(monkeypatch, "test_taxe", lambda r: ajouter_impot(r, taxe_test))
    mesure_de_test(monkeypatch, "test_cheque", lambda r: ajouter_prestation(r, cheque_test))
    mesure_de_test(monkeypatch, "test_cheque_bis", lambda r: ajouter_prestation(r, cheque_test_bis))
    persona = Persona(adultes=(Adulte(salaire_brut_mensuel=5000), Adulte()), enfants=(8,), patrimoine_financier=200_000)
    avant = calculer(LOI_ACTUELLE, persona)
    apres = calculer(loi(Scenario(mesures=("test_taxe", "test_cheque", "test_cheque_bis"))), persona)
    assert (apres["impots_mesures"], apres["prestations_mesures"]) == (2000, 330)
    assert apres["impots_directs"] - avant["impots_directs"] == -2000
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == 330 - 2000


def test_une_prestation_va_a_une_famille_ou_un_individu():
    class mauvaise(Variable):
        value_type = float
        entity = FoyerFiscal
        definition_period = YEAR

    with pytest.raises(ValueError, match="famille ou à un individu"):
        ajouter_prestation(None, mauvaise)  # type: ignore[arg-type]


def test_une_mesure_inconnue_est_refusee():
    with pytest.raises(ValueError, match="inconnues"):
        Scenario(mesures=("n_existe_pas",))


def test_un_processus_de_calcul_tue_est_relance():
    simuler(seul(3000), Scenario(taux_troisieme_tranche_ir=0.31))
    for processus in engine.PROCESSUS["scenario"]._processes.values():
        processus.kill()
    for _ in range(2):  # au pire, le calcul en cours au moment de la panne échoue
        try:
            assert simuler(seul(3100), Scenario(taux_troisieme_tranche_ir=0.31))["avant"]["revenu_disponible"] > 0
            return
        except BrokenProcessPool:
            pass
    raise AssertionError("le processus de calcul n'a pas été relancé")


def test_chaque_salarie_a_son_depart_a_la_retraite():
    couple = Persona(adultes=(Adulte(age=40, au_smic=True, age_debut_carriere=21), Adulte(age=70, retraite_brute_mensuelle=1500)))
    salarie, retraite = simuler(couple, Scenario())["avant"]["retraites"]
    # Né en 1985, début à 21 ans au SMIC : 172 trimestres à 64 ans (voir test_retraites).
    assert (salarie["age_annees"], salarie["age_mois"], salarie["pension_mensuelle"]) == (64, 0, 1243) and retraite is None


def test_une_mesure_change_les_parametres_de_retraite(monkeypatch):
    def a_62_ans(parametres):
        return replace(parametres, age_legal_cible=62 * 12, duree_requise_cible=168)

    # Les processus de calcul ne voient pas une mesure ajoutée par le test : le calcul de la retraite se fait ici.
    monkeypatch.setitem(CATALOGUE, "test_62", Mesure(id="test_62", titre="", candidats=(), source="", citation="", traduction="", retraites=a_62_ans))
    persona = Persona(adultes=(Adulte(age=40, salaire_brut_mensuel=3000, age_debut_carriere=20),))
    (avant,), (apres,) = (retraites(persona, SMIC_ACTUEL, parametres_retraite(Scenario(mesures=m))) for m in ((), ("test_62",)))
    # Début à 20 ans : carrière longue à 63 ans aujourd'hui ; 168 trimestres à 62 ans avec la mesure.
    assert (avant["age_annees"], apres["age_annees"]) == (63, 62) and apres["cumul"] > avant["cumul"]


def test_les_parametres_des_mesures_se_cumulent():
    p = loi(Scenario(mesures=("smic_2000_brut", "tva_sociale"))).parameters(f"{ANNEE}-01-01")
    assert p.marche_travail.salaire_minimum.smic.smic_b_mensuel == pytest.approx(2000)  # perdu tant que chaque mesure repartait de la loi actuelle
    assert p.taxation_indirecte.tva.taux_normal == pytest.approx(0.215)


def test_le_budget_additionne_les_couts_et_les_rapporte_au_foyer(monkeypatch):
    for id, cout in (("depense", Cout(9, 38.5, "candidat ; institut")), ("recette", Cout(-4, -4, "candidat")), ("muette", None)):
        monkeypatch.setitem(CATALOGUE, id, Mesure(id=id, titre=id, candidats=(), source="", citation="", traduction="", cout=cout))
    # Un foyer qui paie un cent-millionième de la TVA et de la CSG du pays, et pas d'impôt sur le revenu.
    apres = {"tva": -2088, "csg": -1566, "impot_revenu": 0}
    b = budget(Scenario(mesures=("depense", "recette", "muette")), apres)
    assert b is not None and b["cout"] == {"bas": 5, "haut": 34.5} and b["non_chiffrees"] == ["muette"]
    # Financer 5 Md€ par la seule TVA la relève de 5 / 208,8 : le foyer en paie sa part, 50 € ; rien par un impôt qu'il ne paie pas.
    assert b["contreparties"] == {"tva": {"bas": -50, "haut": -345}, "csg": {"bas": -50, "haut": -345}, "impot_revenu": {"bas": 0, "haut": 0}}
    assert set(b["contreparties"]) == set(RECETTES)
    # Une économie se lit dans l'autre sens : ce que le foyer gagnerait si elle lui était rendue.
    assert budget(Scenario(mesures=("recette",)), apres)["contreparties"]["tva"] == {"bas": 40, "haut": 40}
    assert budget(Scenario(mesures=("muette",)), apres) is None and budget(Scenario(), apres) is None


def test_un_cout_cite_sa_source_et_va_du_plus_bas_au_plus_haut():
    for bas, haut, source in ((2, 1, "candidat"), (1, 2, "")):
        with pytest.raises(AssertionError):
            Cout(bas, haut, source)


def test_la_simulation_porte_le_budget_du_scenario():
    r = simuler(seul(2500), Scenario(mesures=("part_fiscale_deuxieme_enfant",)))
    assert r["budget"]["cout"] == {"bas": 2.86, "haut": 2.86}
    assert r["budget"]["contreparties"]["tva"]["haut"] == round(r["apres"]["tva"] * 2.86 / RECETTES["tva"]) < 0
    assert simuler(seul(2500), Scenario())["budget"] is None


def test_le_foyer_verse_ses_prelevements_repartis_comme_la_depense_publique():
    m = simuler(seul(2500), Scenario())["avant"]
    f = m["finances_publiques"]
    # Un salarié seul : l'écart du brut au net (cotisations, CSG, CRDS), ses impôts directs et sa TVA ; il ne reçoit que ses prestations.
    assert f["verse"] == 2500 * 12 - m["salaire_net"] - m["impots_directs"] - m["tva"] and f["recu"] == m["prestations_sociales"]
    assert f["verse"] > -(m["csg"] + m["impots_directs"] + m["tva"]) > 0
    assert set(f["depenses"]) == set(DEPENSES_PUBLIQUES) and sum(f["depenses"].values()) == pytest.approx(f["verse"], abs=len(DEPENSES_PUBLIQUES))
    assert f["depenses"]["charge_de_la_dette"] == round(f["verse"] * 60 / sum(DEPENSES_PUBLIQUES.values())) > 0
    # L'Insee compte 1 672 Md€ de dépenses, arrondis de chaque fonction compris.
    assert sum(DEPENSES_PUBLIQUES.values()) == pytest.approx(1672, abs=2)


def test_un_retraite_recoit_sa_pension_brute_et_verse_ses_prelevements():
    m = engine.calculer_selon(Scenario(), Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=1500),)))
    f = m["finances_publiques"]
    assert f["recu"] == 18_000 + m["prestations_sociales"]
    assert f["verse"] == 18_000 - m["retraite_nette"] - m["impots_directs"] - m["tva"]


def test_la_consommation_par_usage_reprend_l_enquete_sans_le_loyer():
    # Premier décile : 14 538 € de consommation hors énergie en 2017, dont 1 840 € de loyer ; le reste est porté aux prix de 2025.
    usages = par_usage(10_000)
    assert sum(usages.values()) == pytest.approx((14_538 - CODES_2017[LOYER][1][0]) * 120.95 / 101.22, abs=len(usages))
    assert usages["alimentation"] == round(2863 * 120.95 / 101.22) and usages["enseignement"] == round(296 * 120.95 / 101.22)


def test_le_bilan_met_le_loyer_et_l_energie_au_logement_et_solde_les_entrees_et_les_sorties():
    locataire = Persona(adultes=(Adulte(),), loyer_mensuel=600, code_commune="69123")
    m = {"salaire_net": 20_000, "retraite_nette": 0, "prestations_sociales": 1000, "impots_directs": -500, "tva": -2100}
    m |= {"depense_electricite": 700, "depense_gaz": 300, "depense_fioul": 0, "depense_autres_energies_logement": 100, "depense_carburants": 900}
    b = engine.bilan(locataire, m, {"logement": 1000, "transports": 2000, "alimentation": 3000}, tva_actuelle=-2000)
    assert b["entrees"] == {"salaires": 20_000, "retraites": 0, "prestations": 1000}
    # Les mêmes achats coûtent 100 € de TVA de plus avec le scénario.
    assert b["sorties"] == {"logement": 1000 + 7200 + 1100, "transports": 2900, "alimentation": 3000, "impots_directs": 500, "tva_du_scenario": 100}
    assert b["solde"] == 21_000 - 15_800


def test_le_foyer_recoit_en_nature_l_ecole_de_ses_enfants_et_la_sante():
    famille = Persona(adultes=(Adulte(), Adulte()), enfants=(2, 5, 12, 19))
    m = dict.fromkeys(("salaire_brut", "retraite_brute", "salaire_net", "retraite_nette", "impots_directs", "tva", "prestations_sociales"), 0)
    en_nature = engine.finances_publiques(m, famille)["en_nature"]
    # À l'école de 3 à 17 ans : un enfant dans le premier degré, un dans le second ; la santé, pour les six.
    assert en_nature == {"enseignement": round(0.82 * (9080 + 11_660)), "sante": round(261e9 / 68.6e6 * 6)}


def test_la_simulation_porte_le_bilan_avant_et_apres():
    r = simuler(seul(2500), Scenario(mesures=("tva_sociale",)))
    avant, apres = r["avant"], r["apres"]
    assert avant["bilan"]["solde"] == pytest.approx(avant["revenu_disponible"] - sum(avant["bilan"]["sorties"].values()) - avant["impots_directs"], abs=2)
    assert avant["bilan"]["sorties"]["tva_du_scenario"] == 0 < apres["bilan"]["sorties"]["tva_du_scenario"] == avant["tva"] - apres["tva"]
    # La hausse de TVA ne change que le prix des achats : le solde baisse d'autant que le pouvoir d'achat.
    assert apres["bilan"]["solde"] - avant["bilan"]["solde"] == r["ecart_pouvoir_achat"]
