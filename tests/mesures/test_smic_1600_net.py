import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, brut_depuis_net, calculer, loi
from simulator.mesures.smic_1600_net import SMIC_BRUT_MENSUEL
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("smic_1600_net",))


def test_le_smic_brut_correspond_a_1600_net_sur_la_loi_2025():
    assert brut_depuis_net(1600) == pytest.approx(SMIC_BRUT_MENSUEL, abs=0.01)


def test_un_salarie_au_smic_touche_1600_net():
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, au_smic), calculer(loi(SCENARIO), au_smic)
    assert avant["salaire_net"] == pytest.approx(1426.30 * 12, abs=1)
    assert apres["salaire_net"] == pytest.approx(1600 * 12, abs=1)


def test_un_haut_salaire_ne_change_pas():
    cadre = Persona(adultes=(Adulte(salaire_brut_mensuel=8000),))
    assert calculer(loi(SCENARIO), cadre) == calculer(LOI_ACTUELLE, cadre)
