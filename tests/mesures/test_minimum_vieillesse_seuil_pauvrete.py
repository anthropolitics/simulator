import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona


def test_l_aspa_porte_le_revenu_d_un_retraite_seul_au_seuil_de_pauvrete():
    # ASPA différentielle : une petite retraite est complétée jusqu'au montant maximal, 12 411,44 € par an en 2025, 16 044 € avec la mesure.
    retraite = Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=600),))
    avant, apres = calculer(LOI_ACTUELLE, retraite), calculer(loi(Scenario(mesures=("minimum_vieillesse_seuil_pauvrete",))), retraite)
    assert apres["minima_sociaux"] - avant["minima_sociaux"] == pytest.approx(16_044 - 12_411.44, abs=1)
    assert apres["revenu_disponible"] == 16_044  # retraite de 600 € brut, sans CSG à ce niveau, et ASPA
