import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.mesures.cotisations_salariales_500_euros_salaire_median import BAISSE
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("cotisations_salariales_500_euros_salaire_median",)))


def test_le_taux_rend_500_euros_au_salaire_median_et_337_au_smic():
    assert BAISSE * 2671.81 * 12 == pytest.approx(500)
    assert BAISSE * 11.88 * 35 * 52 == pytest.approx(337.2, abs=0.1)  # SMIC brut à temps plein de 2025 : 21 621,60 € par an


def test_au_salaire_median_le_net_gagne_500_euros_par_an_sans_changer_le_cout_du_travail():
    median = Persona(adultes=(Adulte(salaire_brut_mensuel=2671.81),))  # 2 115 € nets par mois
    avant, apres = calculer(LOI_ACTUELLE, median), calculer(MESURE, median)
    assert apres["salaire_net"] - avant["salaire_net"] == pytest.approx(500, abs=1)
    assert apres["cout_du_travail"] == avant["cout_du_travail"] and apres["csg"] == avant["csg"]
