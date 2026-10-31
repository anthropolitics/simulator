from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("cheque_formation_apprentis",)))


def test_l_apprenti_recoit_330_euros_par_mois_et_son_employeur_4000_euros_par_an():
    apprenti = Persona(adultes=(Adulte(age=20, apprenti=True, salaire_brut_mensuel=1000),))
    avant, apres = calculer(LOI_ACTUELLE, apprenti), calculer(MESURE, apprenti)
    assert apres["prestations_mesures"] == apres["revenu_disponible"] - avant["revenu_disponible"] == 330 * 12
    assert avant["cout_du_travail"] - apres["cout_du_travail"] == 4000


def test_un_salarie_qui_n_est_pas_apprenti_ne_recoit_rien():
    salarie = Persona(adultes=(Adulte(age=20, salaire_brut_mensuel=1000),))
    assert calculer(MESURE, salarie) == calculer(LOI_ACTUELLE, salarie)
