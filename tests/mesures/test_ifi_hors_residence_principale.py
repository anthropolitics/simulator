from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona


def test_seuls_les_autres_biens_immobiliers_restent_taxes():
    persona = Persona(adultes=(Adulte(salaire_brut_mensuel=10_000),), patrimoine_immobilier=3e6, residence_principale=1e6)
    avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(Scenario(mesures=("ifi_hors_residence_principale",))), persona)
    # Aujourd'hui : 70 % de 1 M€ + 2 M€ = 2,7 M€ ; 0,5 % de 0,8 à 1,3 M€, 0,7 % jusqu'à 2,57 M€, 1 % au-delà.
    ifi_avant = 0.005 * 500_000 + 0.007 * 1_270_000 + 0.01 * 130_000
    # Ensuite : 2 M€, sans la résidence principale.
    ifi_apres = 0.005 * 500_000 + 0.007 * 700_000
    assert (avant["impots_directs"] - avant["impot_revenu"], apres["impots_directs"] - apres["impot_revenu"]) == (-ifi_avant, -ifi_apres)
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == ifi_avant - ifi_apres  # 5 290 €
