import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("taxe_zucman_melenchon",))


def test_au_dela_de_100_millions_le_foyer_paie_la_difference_avec_2_pourcent_du_patrimoine():
    fortune = Persona(adultes=(Adulte(salaire_brut_mensuel=8000),), patrimoine_financier=120e6, patrimoine_immobilier=30e6)
    avant, apres = calculer(LOI_ACTUELLE, fortune), calculer(loi(SCENARIO), fortune)
    crds = 0.005 * 8000 * 12 * 0.9825
    deja_paye = -avant["impots_directs"] - avant["csg"] + crds  # impôt sur le revenu et IFI, CSG, CRDS
    assert apres["impots_mesures"] == pytest.approx(0.02 * 150e6 - deja_paye, abs=1)
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == -apres["impots_mesures"]


def test_jusqu_a_100_millions_rien_ne_change():
    fortune = Persona(adultes=(Adulte(salaire_brut_mensuel=8000),), patrimoine_financier=99e6, patrimoine_immobilier=1e6)
    assert calculer(loi(SCENARIO), fortune) == calculer(LOI_ACTUELLE, fortune)
