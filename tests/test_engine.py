from concurrent.futures.process import BrokenProcessPool
from dataclasses import replace

import pytest
from openfisca_core.model_api import YEAR, Variable
from openfisca_france.entities import Famille, FoyerFiscal

from simulator import engine
from simulator.consommation import (
    CATEGORIES,
    CODES_2017,
    DEPENSES_2017,
    LOYER,
    Profil,
    decile,
    depenses_imputees,
    multiplicateurs,
    par_categorie,
    par_usage,
    taux_d_epargne,
)
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
from simulator.logement import loyer_au_m2, surface_moyenne
from simulator.mesures import CATALOGUE, Cout, Mesure, ajouter_impot, ajouter_prestation
from simulator.persona import ANNEE, Adulte, Depenses, Persona, vieillir


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
    # 17 700 € et 20 980 € de 2024 bornent le 3e dixième ; un niveau de vie de 20 000 € de 2025, soit 19 813 € de 2024, y tombe.
    assert (decile(5_000), decile(20_000), decile(100_000)) == (1, 3, 10)


def test_une_depense_absente_est_imputee_selon_le_revenu_et_le_profil():
    persona = Persona(adultes=(Adulte(au_smic=True),), depenses=Depenses(electricite=1800))
    m = calculer(LOI_ACTUELLE, persona)
    # Une personne seule compte pour une unité de consommation : son niveau de vie est son revenu disponible.
    imputees = depenses_imputees(m["revenu_disponible"], engine.profil(persona), engine.hors_loyer(persona, m))
    assert m["depense_electricite"] == 1800 and m["depense_carburants"] == imputees["carburants"] > 0
    assert imputees["carburants"] < depenses_imputees(m["revenu_disponible"])["carburants"]  # elle roule moins que le ménage moyen


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
    m = {"salaire_net": 20_000, "retraite_nette": 0, "prestations_sociales": 1000, "impots_directs": -500, "tva": -2100}
    m |= {"depense_electricite": 700, "depense_gaz": 300, "depense_fioul": 0, "depense_autres_energies_logement": 100, "depense_carburants": 900}
    charges = {"loyer": 7200, "remboursement_emprunt": 0, "taxe_fonciere": 0}
    b = engine.bilan(m, {"logement": 1000, "transports": 2000, "alimentation": 3000}, charges, tva_actuelle=-2000)
    assert b["entrees"] == {"salaires": 20_000, "retraites": 0, "prestations": 1000}
    # Les mêmes achats coûtent 100 € de TVA de plus avec le scénario.
    achats = {"logement": 1000 + 7200 + 1100, "transports": 2900, "alimentation": 3000, "tva_du_scenario": 100}
    assert b["sorties"] == achats | {"impots_directs": 500, "taxe_fonciere": 0, "remboursement_emprunt": 0}
    assert b["solde"] == 21_000 - 15_800 and b["loyer"] == 7200
    # Un accédant : son remboursement et sa taxe foncière sortent à part, hors du logement.
    accedant = engine.bilan(m, {"logement": 1000, "transports": 0}, {"loyer": 0, "remboursement_emprunt": 9000, "taxe_fonciere": 800}, tva_actuelle=-2100)
    assert (accedant["sorties"]["logement"], accedant["sorties"]["remboursement_emprunt"], accedant["sorties"]["taxe_fonciere"]) == (2100, 9000, 800)


def test_le_foyer_recoit_en_nature_l_ecole_de_ses_enfants_et_la_sante_selon_leur_age():
    famille = Persona(adultes=(Adulte(age=45), Adulte(age=82)), enfants=(2, 5, 8, 12, 16, 19))
    m = dict.fromkeys(("salaire_brut", "retraite_brute", "salaire_net", "retraite_nette", "impots_directs", "tva", "prestations_sociales"), 0)
    en_nature = engine.finances_publiques(m, famille)["en_nature"]
    # Pas d'école à 2 ans ; puis maternelle, élémentaire, collège, lycée, supérieur : la part publique de la dépense par élève de chaque niveau.
    assert en_nature["enseignement"] == round(0.94 * (8990 + 9130) + 0.89 * (10_450 + 13_020) + 0.68 * 13_300)
    # La dépense publique de santé par habitant, pondérée selon l'âge : 41-50 ans, plus de 80 ans, trois enfants de 0 à 10 ans, trois de 11 à 20 ans.
    assert en_nature["sante"] == round(261e9 / 68.6e6 * (1713 + 7858 + 3 * 925 + 3 * 887) / 2496)
    assert engine.sante(80) < engine.sante(81) and engine.sante(10) > engine.sante(11)


def test_la_simulation_porte_le_bilan_avant_et_apres():
    r = simuler(seul(2500), Scenario(mesures=("tva_sociale",)))
    avant, apres = r["avant"], r["apres"]
    assert avant["bilan"]["solde"] == pytest.approx(avant["revenu_disponible"] - sum(avant["bilan"]["sorties"].values()) - avant["impots_directs"], abs=2)
    assert avant["bilan"]["sorties"]["tva_du_scenario"] == 0 < apres["bilan"]["sorties"]["tva_du_scenario"] == avant["tva"] - apres["tva"]
    # La hausse de TVA ne change que le prix des achats : le solde baisse d'autant que le pouvoir d'achat.
    assert apres["bilan"]["solde"] - avant["bilan"]["solde"] == r["ecart_pouvoir_achat"]


def test_le_profil_ne_deplace_que_la_repartition_des_depenses():
    assert set(multiplicateurs(3, None).values()) == {1.0}
    moyen, m = par_categorie(3), multiplicateurs(3, Profil(adultes=1, enfants=False, age=40, locataire=True, zone=2))
    assert sum(moyen[c] * m[c] for c in CATEGORIES) == pytest.approx(sum(moyen.values()))
    # Le total vient d'ailleurs : la dépense hors loyer du foyer, que les postes soumis à la TVA et les usages se partagent, énergie comprise.
    seul = Profil(adultes=1, enfants=False, age=40, locataire=True, zone=2)
    postes, usages = depenses_imputees(20_000, seul, 12_000), par_usage(20_000, seul, 12_000)
    assert sum(usages.values()) + sum(postes[p] for p in ("electricite", "gaz", "fioul", "autres_energies_logement", "carburants")) == pytest.approx(
        12_000, abs=10
    )
    assert depenses_imputees(20_000, seul, 6000)["carburants"] == pytest.approx(postes["carburants"] / 2, abs=1)


def test_le_profil_deplace_les_depenses_comme_l_enquete():
    def famille(age=40, locataire=False, zone=None):
        return Profil(adultes=2, enfants=True, age=age, locataire=locataire, zone=zone)

    # À la campagne, on roule plus qu'à Paris ; à 78 ans, on dépense plus pour se chauffer et moins pour s'habiller qu'à 30 ans.
    assert depenses_imputees(20_000, famille(zone=3))["carburants"] > 2 * depenses_imputees(20_000, famille(zone=1))["carburants"]
    jeune, age = (depenses_imputees(20_000, famille(age=a)) for a in (30, 78))
    assert age["electricite"] > jeune["electricite"] and par_usage(20_000, famille(age=78))["habillement"] < par_usage(20_000, famille(age=30))["habillement"]


def test_le_taux_d_epargne_suit_le_niveau_de_vie():
    prix = 120.95 / 119.82  # de 2024 à 2025
    # Au niveau de vie médian d'un cinquième (déciles 1, 3, 5, 7, 9 de 2024), son taux ; entre deux, l'interpolation ; au-delà, le dernier.
    assert taux_d_epargne(13_970 * prix) == pytest.approx(0.0271) and taux_d_epargne(26_740 * prix) == pytest.approx(0.0965)
    assert taux_d_epargne((20_980 + 26_740) / 2 * prix) == pytest.approx((0.0499 + 0.0965) / 2)
    assert taux_d_epargne(5000) == pytest.approx(0.0271) and taux_d_epargne(200_000) == pytest.approx(0.2837)


def test_un_proprietaire_paie_la_taxe_fonciere_et_un_accedant_rembourse_son_emprunt():
    m = {"revenu_disponible": 30_000, "impots_directs": -2000, "aides_logement": 0}  # 32 000 € de revenus avant impôts, entre le 2e et le 3e quart
    sans_emprunt, accedant = (engine.logement(Persona(adultes=(Adulte(),), accedant=a), m) for a in (False, True))
    assert sans_emprunt["loyer"] == sans_emprunt["remboursement_emprunt"] == 0 and 0.025 * 32_000 < sans_emprunt["taxe_fonciere"] < 0.032 * 32_000
    assert 0.191 * 32_000 < accedant["remboursement_emprunt"] < 0.216 * 32_000 and 0.019 * 32_000 < accedant["taxe_fonciere"] < 0.023 * 32_000
    # Une mensualité saisie est prise telle quelle ; un locataire ne paie ni l'un ni l'autre.
    assert engine.logement(Persona(adultes=(Adulte(),), remboursement_mensuel=900), m)["remboursement_emprunt"] == 10_800
    locataire = Persona(adultes=(Adulte(),), loyer_mensuel=700, code_commune="69123")
    assert engine.logement(locataire, m) == {"loyer": 8400, "remboursement_emprunt": 0, "taxe_fonciere": 0}
    with pytest.raises(ValueError, match="pas les deux"):
        Persona(adultes=(Adulte(),), loyer_mensuel=700, code_commune="69123", accedant=True)


def test_la_depense_hors_loyer_suit_le_revenu_et_le_taux_d_epargne():
    m = {"revenu_disponible": 30_000, "impots_directs": -2000, "aides_logement": 0}
    locataire = Persona(adultes=(Adulte(),), loyer_mensuel=700, code_commune="69123")
    assert engine.hors_loyer(locataire, m) == pytest.approx((1 - taux_d_epargne(30_000)) * 30_000 - 8400)
    # Le remboursement d'un accédant tient lieu de loyer, et la taxe foncière vient en déduction du revenu.
    accedant = Persona(adultes=(Adulte(),), remboursement_mensuel=900)
    taxe = engine.logement(accedant, m)["taxe_fonciere"]
    assert engine.hors_loyer(accedant, m) == pytest.approx((1 - taux_d_epargne(30_000)) * (30_000 - taxe) - 10_800)
    # Un loyer plus lourd que la dépense totale ne laisse rien.
    assert engine.hors_loyer(Persona(adultes=(Adulte(),), loyer_mensuel=3000, code_commune="69123"), m) == 0


def test_le_solde_du_bilan_est_l_epargne_des_menages_du_meme_niveau_de_vie():
    avant = simuler(seul(2500), Scenario())["avant"]
    taxe = avant["bilan"]["sorties"]["taxe_fonciere"]
    assert taxe > 0  # sans loyer, le foyer est tenu pour propriétaire
    # Aux arrondis de chaque poste près.
    assert avant["bilan"]["solde"] == pytest.approx(taux_d_epargne(avant["revenu_disponible"]) * (avant["revenu_disponible"] - taxe), abs=20)


def test_le_loyer_au_metre_carre_suit_la_zone_et_le_secteur():
    irl = 145.93 / 130.56  # de 2020 à 2025
    # Parc privé : 10,50 € en 2020, 16,11 € à Paris pour 8,59 € en moyenne en 2013. Une commune inconnue est en zone 2, comme pour OpenFisca.
    assert loyer_au_m2(1, social=False) == pytest.approx(10.5 * 16.11 / 8.59 * irl)
    assert loyer_au_m2(None, social=False) == loyer_au_m2(2, social=False) == pytest.approx(10.5 * 8.79 / 8.59 * irl)
    # Zone 3 : entre les communes rurales et les petites agglomérations, selon leurs ménages locataires.
    assert 6.5 * 4.98 / 5.51 * irl < loyer_au_m2(3, social=True) < 6.5 * 5.02 / 5.51 * irl
    assert loyer_au_m2(3, social=False) < loyer_au_m2(2, social=False) < loyer_au_m2(1, social=False)


def test_la_surface_moyenne_suit_le_type_de_menage_et_l_age():
    assert [surface_moyenne(False, 1, 0, age) for age in (64, 65)] == [46.7, 58.8]
    assert [surface_moyenne(False, 2, enfants, 40) for enfants in (0, 2, 3)] == [67.0, 87.1, 99.8]
    assert (surface_moyenne(True, 1, 2, 70), surface_moyenne(True, 2, 0, 70)) == (73.7, 71.9)


def test_le_loyer_d_un_locataire_est_le_sien_ou_a_defaut_estime():
    def locataire(**logement):
        return Persona(adultes=(Adulte(age=42, au_smic=True),), code_commune="31555", **logement)

    assert Persona(adultes=(Adulte(),)).loyer == 0 and locataire(loyer_mensuel=616, locataire=True, surface_logement=30).loyer == 616
    # Toulouse est en zone 2 : une personne seule de moins de 65 ans y loue 46,7 m² dans le parc privé, à défaut de dire sa surface.
    assert locataire(locataire=True).zone == 2
    assert locataire(locataire=True).loyer == round(46.7 * loyer_au_m2(2, social=False))
    assert locataire(locataire=True, surface_logement=30, logement_social=True).loyer == round(30 * loyer_au_m2(2, social=True))
    with pytest.raises(ValueError, match="commune"):
        Persona(adultes=(Adulte(),), locataire=True)
    # Le loyer estimé ouvre les aides au logement et entre dans le bilan, comme un loyer saisi.
    r = simuler(locataire(locataire=True), Scenario())["avant"]
    assert r["aides_logement"] > 0 and r["bilan"]["loyer"] == 12 * locataire(locataire=True).loyer


def test_le_foyer_vieillit_sans_que_rien_d_autre_ne_lui_arrive():
    famille = Persona(adultes=(Adulte(age=40, salaire_brut_mensuel=3000), Adulte(age=61, salaire_brut_mensuel=2000)), enfants=(3, 12, 19))
    departs = [None, {"age_annees": 63, "age_mois": 6, "pension_mensuelle": 1400, "cumul": 0}]
    dans_2_ans, dans_3_ans = (vieillir(famille, annees, 0.01, departs) for annees in (2, 3))
    # Chacun vieillit ; l'enfant de 19 ans a 21 ans et quitte le foyer ; les salaires montent de 1 % par an au-delà des prix.
    assert [a.age for a in dans_2_ans.adultes] == [42, 63] and dans_2_ans.enfants == (5, 14)
    assert dans_2_ans.adultes[0].salaire_brut_mensuel == pytest.approx(3000 * 1.01**2)
    # À 63 ans, le second adulte travaille encore ; à 64 ans, il a passé les 63 ans et 6 mois de son départ et touche sa pension.
    assert dans_2_ans.adultes[1].retraite_brute_mensuelle == 0 and dans_2_ans.adultes[1].salaire_brut_mensuel > 2000
    assert (dans_3_ans.adultes[1].salaire_brut_mensuel, dans_3_ans.adultes[1].retraite_brute_mensuelle) == (0, 1400)
    # Le SMIC suit les prix : un salarié au SMIC y reste, sans salaire saisi à faire monter.
    smicard = vieillir(Persona(adultes=(Adulte(age=30, au_smic=True, annees_travail_france=2),)), 10, 0.01, [None]).adultes[0]
    assert (smicard.age, smicard.au_smic, smicard.salaire_brut_mensuel, smicard.annees_travail_france) == (40, True, 0, 12)


def test_a_l_horizon_le_salarie_qui_a_atteint_son_depart_touche_sa_pension():
    # Né en 1964, entré à 22 ans : il travaille aujourd'hui, à 61 ans, et sera parti dans cinq ans.
    salarie = Persona(adultes=(Adulte(age=61, salaire_brut_mensuel=2500),))
    aujourd_hui, dans_5_ans = engine.calculer_selon(Scenario(), salarie), engine.calculer_selon(Scenario(), salarie, 5, 0.007)
    assert aujourd_hui["salaire_net"] > 0 and aujourd_hui["retraite_nette"] == 0 and aujourd_hui["foyer"]["adultes"][0]["age"] == 61
    assert dans_5_ans["salaire_net"] == 0 and dans_5_ans["foyer"]["adultes"][0]["age"] == 66 and dans_5_ans["retraites"] == [None]
    assert dans_5_ans["retraite_brute"] == 12 * aujourd_hui["retraites"][0]["pension_mensuelle"]


def test_une_reforme_des_retraites_change_qui_travaille_encore_a_l_horizon():
    # Au SMIC, entré à 22 ans : départ à 65 ans selon la loi actuelle, à 63 ans avec la mesure. À 64 ans, il travaille ou il est retraité.
    smicard = Persona(adultes=(Adulte(age=40, au_smic=True),))
    r = simuler(smicard, Scenario(mesures=("retraite_62_ans_60_ans_carrieres_longues",)), annees=24)
    assert (r["horizon"], r["croissance"]) == (24, 0.007)
    assert r["avant"]["salaire_net"] > 0 == r["avant"]["retraite_nette"] and r["apres"]["retraite_nette"] > 0 == r["apres"]["salaire_net"]
    assert r["ecart_revenu_disponible"] < 0  # parti deux ans plus tôt, il vit cette année-là de sa pension
    # Aujourd'hui, la même mesure ne change rien à ses revenus.
    assert simuler(smicard, Scenario(mesures=("retraite_62_ans_60_ans_carrieres_longues",)))["ecart_revenu_disponible"] == 0


def test_la_projection_fait_monter_les_salaires_avec_la_productivite():
    r = simuler(seul(2500), Scenario(), annees=10)
    assert r["avant"]["salaire_brut"] == pytest.approx(2500 * 12 * 1.007**10, abs=1) and r["avant"]["foyer"]["adultes"][0]["age"] == 50
    assert simuler(seul(2500), Scenario())["horizon"] == 0 and simuler(seul(2500), Scenario())["croissance"] == 0
