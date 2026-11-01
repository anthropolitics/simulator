import numpy as np
import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("ir_tranche_60_pourcent",)))


def bareme(legislation, date):
    return legislation.parameters(date).impot_revenu.bareme_ir_depuis_1945.bareme


def test_la_tranche_ne_touche_que_la_part_au_dela_de_250_000_euros_en_2025():
    revenus_par_part = np.array([200_000, 250_000, 300_000])
    ecart = bareme(MESURE, "2025-01-01").calc(revenus_par_part) - bareme(LOI_ACTUELLE, "2025-01-01").calc(revenus_par_part)
    assert ecart == pytest.approx([0, 0, 0.15 * 50_000])  # 60 % au lieu de 45 % sur les 50 000 € au-delà du seuil
    assert bareme(MESURE, "2024-01-01").thresholds == bareme(LOI_ACTUELLE, "2024-01-01").thresholds


def test_un_tres_haut_salaire_paie_15_points_de_plus_au_dela_du_seuil():
    cadre = Persona(adultes=(Adulte(salaire_brut_mensuel=30_000),))
    avant, apres = calculer(LOI_ACTUELLE, cadre), calculer(MESURE, cadre)
    # Loi actuelle, une part : barème jusqu'à 45 % plus 3 % de contribution sur les hauts revenus au-delà de 250 000 €, d'où le revenu imposable.
    sous_45_pourcent = 0.11 * (29_579 - 11_600) + 0.30 * (84_577 - 29_579) + 0.41 * (181_917 - 84_577)
    revenu = (-avant["impot_revenu"] - sous_45_pourcent + 0.45 * 181_917 + 0.03 * 250_000) / 0.48
    assert revenu > 250_000
    assert avant["impot_revenu"] - apres["impot_revenu"] == pytest.approx(0.15 * (revenu - 250_000), abs=2)
    assert apres["csg"] == avant["csg"]
