import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("hausse_salaires_nets_8_pourcent",))


def seul(salaire):
    return Persona(adultes=(Adulte(salaire_brut_mensuel=salaire),))


def test_le_net_gagne_8_pourcent_sans_changer_le_cout_du_travail():
    avant, apres = calculer(LOI_ACTUELLE, seul(2500)), calculer(loi(SCENARIO), seul(2500))
    assert apres["salaire_net"] == pytest.approx(avant["salaire_net"] * 1.08, abs=1)
    assert apres["cout_du_travail"] == avant["cout_du_travail"]


def test_au_dessus_de_3_smic_rien_ne_change():
    assert calculer(loi(SCENARIO), seul(6000)) == calculer(LOI_ACTUELLE, seul(6000))
