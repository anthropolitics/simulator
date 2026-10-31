import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, brut_depuis_net, calculer, loi
from simulator.mesures.smic_1700_net import SMIC_BRUT_MENSUEL
from simulator.persona import Adulte, Persona


def test_le_smic_brut_correspond_a_1700_net_sur_la_loi_2025():
    assert brut_depuis_net(1700) == pytest.approx(SMIC_BRUT_MENSUEL, abs=0.01)


def test_un_salarie_au_smic_touche_1700_net():
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    assert calculer(loi(Scenario(mesures=("smic_1700_net",))), au_smic)["salaire_net"] == pytest.approx(1700 * 12, abs=1)
    assert calculer(LOI_ACTUELLE, au_smic)["salaire_net"] == pytest.approx(1426.30 * 12, abs=1)
