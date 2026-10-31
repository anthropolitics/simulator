from concurrent.futures.process import BrokenProcessPool
from dataclasses import replace

import pytest
from openfisca_core.model_api import YEAR, Variable
from openfisca_france.entities import Famille, FoyerFiscal

from simulator import engine
from simulator.consommation import CODES_2017, DEPENSES_2017, decile, depenses_imputees
from simulator.engine import LOI_ACTUELLE, SMIC_ACTUEL, TAUX_ACTUEL, Scenario, brut_depuis_net, calculer, loi, parametres_retraite, retraites, simuler
from simulator.mesures import CATALOGUE, Mesure, ajouter_impot, ajouter_prestation
from simulator.persona import Adulte, Depenses, Persona


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
    imputees = depenses_imputees(m["revenu_disponible"])  # une personne seule compte pour une unité de consommation
    assert m["depense_electricite"] == 1800 and m["depense_carburants"] == imputees["carburants"] > 0


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
