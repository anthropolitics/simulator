import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("part_fiscale_deuxieme_enfant",))


def test_le_deuxieme_enfant_apporte_une_part():
    parts = loi(SCENARIO).parameters("2025-01-01").impot_revenu.calcul_impot_revenu.plaf_qf.quotient_familial.cas_general
    assert (parts.enf1, parts.enf2, parts.enf3_et_sup) == (0.5, 1, 1)


def test_un_couple_aise_gagne_le_plafond_d_une_demi_part():
    # 3 parts puis 3,5 : l'avantage dû aux enfants, plafonné à 1 807 € par demi-part, passe de 2 à 3 demi-parts.
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=12_000), Adulte(salaire_brut_mensuel=12_000)), enfants=(5, 10))
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(loi(SCENARIO), couple)
    assert apres["impot_revenu"] - avant["impot_revenu"] == pytest.approx(1807, abs=1)
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == pytest.approx(1807, abs=1)
