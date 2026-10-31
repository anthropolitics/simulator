from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("smic_2000_brut",))


def seul(salaire):
    return Persona(adultes=(Adulte(salaire_brut_mensuel=salaire),))


def test_un_salarie_au_smic_touche_le_net_de_2000_brut():
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, au_smic), calculer(loi(SCENARIO), au_smic)
    assert apres["salaire_net"] == calculer(LOI_ACTUELLE, seul(2000))["salaire_net"] > avant["salaire_net"]


def test_un_haut_salaire_ne_change_pas():
    assert calculer(loi(SCENARIO), seul(8000)) == calculer(LOI_ACTUELLE, seul(8000))
