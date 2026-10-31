from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("minimum_vieillesse_1000",))


def aspa_seule(legislation):
    return legislation.parameters("2025-01-01").prestations_sociales.solidarite_insertion.minimum_vieillesse.aspa.montant_maximum_annuel.personnes_seules


def test_l_aspa_2025_depasse_deja_1000_euros():
    assert aspa_seule(loi(SCENARIO)) == aspa_seule(LOI_ACTUELLE) > 12_000


def test_un_retraite_au_minimum_vieillesse_ne_change_pas():
    retraite = Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=600),))
    assert calculer(loi(SCENARIO), retraite) == calculer(LOI_ACTUELLE, retraite)
