import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("plafond_quotient_familial_double",))


def test_le_plafond_general_par_demi_part_double():
    demi_part = loi(SCENARIO).parameters("2025-01-01").impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part
    assert (demi_part.general, demi_part.celib_enf) == (2 * 1807, 4262)


def test_un_couple_aise_avec_deux_enfants_gagne_deux_fois_le_plafond_actuel():
    # Deux demi-parts plafonnées à 1 807 € puis à 3 614 € ; sans plafond, leur avantage dépasserait 7 228 €.
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=12_000), Adulte(salaire_brut_mensuel=12_000)), enfants=(5, 10))
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(loi(SCENARIO), couple)
    assert apres["impot_revenu"] - avant["impot_revenu"] == pytest.approx(2 * 1807, abs=1)
