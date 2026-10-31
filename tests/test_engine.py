from concurrent.futures.process import BrokenProcessPool

import pytest
from openfisca_core.model_api import YEAR, Variable
from openfisca_france.entities import Famille, FoyerFiscal

from simulator import engine
from simulator.engine import LOI_ACTUELLE, TAUX_ACTUEL, Scenario, brut_depuis_net, calculer, loi, simuler
from simulator.mesures import CATALOGUE, Mesure, ajouter_impot, ajouter_prestation
from simulator.persona import Adulte, Persona


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


def test_le_salaire_au_smic_suit_le_smic(monkeypatch):
    def smic_a_13_euros(reforme):
        def modifier(parametres):
            parametres.marche_travail.salaire_minimum.smic.smic_b_horaire.update(start="2025-01-01", value=13.0)
            return parametres

        reforme.modify_parameters(modifier_function=modifier)

    mesure_de_test(monkeypatch, "test_smic", smic_a_13_euros)
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, au_smic), calculer(loi(Scenario(mesures=("test_smic",))), au_smic)
    assert apres["salaire_net"] / avant["salaire_net"] == pytest.approx(13.0 / 11.88, rel=0.02)


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
