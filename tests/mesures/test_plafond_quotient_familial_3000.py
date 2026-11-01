import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("plafond_quotient_familial_3000",))


def test_seul_le_plafond_general_par_demi_part_change():
    demi_part = loi(SCENARIO).parameters("2025-01-01").impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part
    assert (demi_part.general, demi_part.celib_enf, demi_part.celib) == (3000, 4262, 1079)


def test_un_couple_aise_avec_deux_enfants_gagne_deux_fois_la_hausse_du_plafond():
    # Deux demi-parts plafonnées à 1 807 € puis à 3 000 € ; sans plafond, leur avantage dépasserait 6 000 €.
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=12_000), Adulte(salaire_brut_mensuel=12_000)), enfants=(5, 10))
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(loi(SCENARIO), couple)
    assert apres["impot_revenu"] - avant["impot_revenu"] == pytest.approx(2 * (3000 - 1807), abs=1)  # 2 386 €
