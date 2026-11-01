import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, bareme_ir, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("quotient_familial_deplafonne",)))


def test_un_couple_avec_deux_enfants_dans_la_tranche_a_30_pourcent_gagne_l_avantage_au_dela_du_plafond():
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=6000), Adulte(salaire_brut_mensuel=6000)), enfants=(5, 10))
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(MESURE, couple)
    # Revenu R par part dans la tranche à 30 %, à 2 comme à 3 parts : n parts paient 0,3 R - n (0,3 s2 - 0,11 (s2 - s1)), si bien que
    # la troisième part rapporte 0,19 s2 + 0,11 s1, quel que soit R. Aujourd'hui, l'avantage de ses deux demi-parts est plafonné à 2 × 1 807 €.
    seuils = [tranche.threshold("2025-01-01") for tranche in bareme_ir(LOI_ACTUELLE.parameters).brackets[1:3]]  # 11 600 € et 29 579 €
    avantage = 0.19 * seuils[1] + 0.11 * seuils[0]  # 6 896,01 €
    assert apres["impot_revenu"] - avant["impot_revenu"] == pytest.approx(avantage - 2 * 1807, abs=1)  # 3 282 € d'impôt en moins
