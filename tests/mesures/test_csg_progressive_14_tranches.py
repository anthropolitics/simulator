import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("csg_progressive_14_tranches",))


def test_au_smic_la_csg_baisse_et_le_net_augmente_d_autant():
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, au_smic), calculer(loi(SCENARIO), au_smic)
    assiette = 1801.80 * 0.9825  # salaire brut mensuel au SMIC, abattement de 1,75 %
    assert avant["csg"] == -round(12 * 0.092 * assiette)
    assert apres["csg"] == -round(12 * (0.06 * 500 + 0.065 * 500 + 0.0675 * 400 + 0.075 * (assiette - 1400)))
    assert apres["salaire_net"] - avant["salaire_net"] == pytest.approx(apres["csg"] - avant["csg"], abs=1)


def test_un_cadre_paie_plus_de_csg_sans_changer_son_impot_sur_le_revenu():
    cadre = Persona(adultes=(Adulte(salaire_brut_mensuel=8000),))
    avant, apres = calculer(LOI_ACTUELLE, cadre), calculer(loi(SCENARIO), cadre)
    assiette = 8000 * 0.9825
    tranches_pleines = 0.06 * 500 + 0.065 * 500 + 0.0675 * 400 + 0.075 * 400 + 0.08 * 400 + 0.085 * 500 + 0.092 * 700 + 0.125 * 800 + 0.1364 * 790
    assert apres["csg"] == -round(12 * (tranches_pleines + 0.15 * 1010 + 0.16 * (assiette - 6000)))
    assert apres["impot_revenu"] == avant["impot_revenu"]  # la part déductible reste de 6,8 % de l'assiette


def test_la_csg_sur_les_retraites_ne_change_pas():
    retraite = Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=1500),))
    assert calculer(loi(SCENARIO), retraite) == calculer(LOI_ACTUELLE, retraite)
