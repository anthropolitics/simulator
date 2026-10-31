from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("baisse_cotisations_salariales_3_points",))


def test_le_net_gagne_3_pourcent_de_tout_le_brut_sans_changer_le_cout_du_travail():
    cadre = Persona(adultes=(Adulte(salaire_brut_mensuel=5000),))  # au-dessus du plafond de la sécurité sociale
    avant, apres = calculer(LOI_ACTUELLE, cadre), calculer(loi(SCENARIO), cadre)
    assert apres["salaire_net"] - avant["salaire_net"] == 150 * 12
    assert apres["cout_du_travail"] == avant["cout_du_travail"]


def test_sans_cotisations_salariales_rien_ne_change():
    for persona in (
        Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=1500),)),
        Persona(adultes=(Adulte(age=20, apprenti=True, salaire_brut_mensuel=900),)),  # exonéré de cotisations salariales sous 50 % du SMIC
    ):
        assert calculer(loi(SCENARIO), persona) == calculer(LOI_ACTUELLE, persona)
