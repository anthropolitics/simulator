import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("taxe_zucman_melenchon",))
CADRE = Adulte(salaire_brut_mensuel=8000)


def test_au_dela_de_100_millions_le_foyer_paie_la_difference_avec_2_pourcent_du_patrimoine_apres_abattement():
    fortune = Persona(adultes=(CADRE,), patrimoine_financier=120e6, patrimoine_immobilier=30e6, residence_principale=5e6)
    avant, apres = calculer(LOI_ACTUELLE, fortune), calculer(loi(SCENARIO), fortune)
    crds = 0.005 * 8000 * 12 * 0.9825
    deja_paye = -avant["impots_directs"] - avant["csg"] + crds  # impôt sur le revenu et IFI, CSG, CRDS
    assert apres["impots_mesures"] == pytest.approx(0.02 * (150e6 - 1e6) - deja_paye, abs=1)
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == -apres["impots_mesures"]


def test_jusqu_a_100_millions_apres_abattement_sur_la_residence_principale_rien_ne_change():
    fortune = Persona(adultes=(CADRE,), patrimoine_financier=99.5e6, patrimoine_immobilier=1.2e6, residence_principale=1.2e6)  # 99,7 M€ après abattement
    assert calculer(loi(SCENARIO), fortune) == calculer(LOI_ACTUELLE, fortune)
