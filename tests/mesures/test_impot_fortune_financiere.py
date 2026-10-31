from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("impot_fortune_financiere",))
CADRE = Adulte(salaire_brut_mensuel=10_000)


def test_le_foyer_ne_paie_plus_l_ifi_et_paie_l_iff_sur_son_patrimoine_hors_residence_principale():
    fortune = Persona(adultes=(CADRE,), patrimoine_financier=3e6, patrimoine_immobilier=2e6, residence_principale=1e6)
    avant, apres = calculer(LOI_ACTUELLE, fortune), calculer(loi(SCENARIO), fortune)
    # IFI : 70 % de 1 M€ + 1 M€ = 1,7 M€ ; 0,5 % de 0,8 à 1,3 M€ et 0,7 % au-delà.
    ifi = 0.005 * 500_000 + 0.007 * 400_000
    # IFF : 3 M€ + 1 M€ = 4 M€ ; puis 0,7 % jusqu'à 2,57 M€ et 1 % au-delà.
    iff = 0.005 * 500_000 + 0.007 * 1_270_000 + 0.01 * 1_430_000
    assert avant["impots_directs"] - avant["impot_revenu"] == -ifi
    assert apres["impots_mesures"] == iff == 25_690
    assert apres["impots_directs"] - apres["impot_revenu"] == -iff
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == ifi - iff


def test_le_plafonnement_a_75_pourcent_des_revenus_est_garde():
    sans_revenu = Persona(adultes=(Adulte(),), patrimoine_financier=3e6)
    assert calculer(loi(SCENARIO), sans_revenu)["impots_mesures"] == 0
    salarie = Persona(adultes=(CADRE,), patrimoine_financier=3e6)
    assert calculer(loi(SCENARIO), salarie)["impots_mesures"] == 0.005 * 500_000 + 0.007 * 1_270_000 + 0.01 * 430_000


def test_jusqu_a_1_3_million_hors_residence_principale_rien_ne_change():
    menage = Persona(adultes=(Adulte(salaire_brut_mensuel=3000),), patrimoine_financier=1.3e6, patrimoine_immobilier=400e3, residence_principale=400e3)
    assert calculer(loi(SCENARIO), menage) == calculer(LOI_ACTUELLE, menage)
