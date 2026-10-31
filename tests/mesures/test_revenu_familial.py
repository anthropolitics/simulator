from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("revenu_familial",)))


def test_240_euros_par_enfant_mineur_a_la_place_des_allocations_familiales_et_du_quotient_familial():
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=2500), Adulte(salaire_brut_mensuel=2000)), enfants=(5, 10))
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(MESURE, couple)
    assert apres["prestations_mesures"] == 2 * 240 * 12
    assert apres["prestations_familiales"] == 0 < avant["prestations_familiales"]
    assert apres["impot_revenu"] < avant["impot_revenu"]  # plus de parts de quotient familial pour les enfants


def test_la_paje_est_maintenue():
    parents = Persona(adultes=(Adulte(salaire_brut_mensuel=1500), Adulte()), enfants=(1,))
    avant, apres = calculer(LOI_ACTUELLE, parents), calculer(MESURE, parents)
    assert apres["prestations_mesures"] == 240 * 12
    assert apres["prestations_familiales"] == avant["prestations_familiales"] > 0


def test_un_enfant_de_18_ans_ou_plus_ne_le_recoit_pas():
    assert calculer(MESURE, Persona(adultes=(Adulte(salaire_brut_mensuel=3000),), enfants=(19,)))["prestations_mesures"] == 0


def test_sans_enfant_rien_ne_change():
    seul = Persona(adultes=(Adulte(salaire_brut_mensuel=3000),))
    assert calculer(MESURE, seul) == calculer(LOI_ACTUELLE, seul)
