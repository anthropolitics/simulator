from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("suppression_ifi",)))


def test_le_foyer_ne_paie_plus_l_ifi():
    fortune = Persona(adultes=(Adulte(salaire_brut_mensuel=10_000),), patrimoine_immobilier=2e6, residence_principale=1e6)
    avant, apres = calculer(LOI_ACTUELLE, fortune), calculer(MESURE, fortune)
    # IFI : 70 % de la résidence principale de 1 M€ plus 1 M€ d'autres immeubles, 1,7 M€ ; 0,5 % de 0,8 à 1,3 M€ et 0,7 % au-delà.
    ifi = 0.005 * 500_000 + 0.007 * 400_000  # 5 300 €
    assert avant["impots_directs"] - avant["impot_revenu"] == -ifi
    assert apres["impots_directs"] == apres["impot_revenu"] == avant["impot_revenu"]
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == ifi
