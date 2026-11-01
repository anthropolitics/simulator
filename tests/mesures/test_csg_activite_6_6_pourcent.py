import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("csg_activite_6_6_pourcent",)))


def test_au_smic_le_net_gagne_2_6_points_de_csg_sur_98_25_pourcent_du_brut():
    smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, smic), calculer(MESURE, smic)
    gain = 0.026 * 0.9825 * 11.88 * 35 * 52  # 552,33 € par an, 46,03 € par mois
    assert apres["salaire_net"] - avant["salaire_net"] == pytest.approx(gain, abs=1)
    assert apres["csg"] - avant["csg"] == pytest.approx(gain, abs=1)  # la CSG est négative : elle baisse d'autant
    assert apres["cout_du_travail"] == avant["cout_du_travail"]
    assert apres["impot_revenu"] <= avant["impot_revenu"]  # plus de salaire imposable : l'impôt, négatif, ne baisse pas
