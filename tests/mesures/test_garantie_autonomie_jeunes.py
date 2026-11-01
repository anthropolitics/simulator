from simulator.engine import Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("garantie_autonomie_jeunes",)))
TEMPS_PARTIEL = 900  # salaire brut mensuel


def test_un_jeune_seul_a_temps_partiel_est_porte_au_seuil_de_pauvrete():
    resultat = calculer(MESURE, Persona(adultes=(Adulte(age=22, salaire_brut_mensuel=TEMPS_PARTIEL),)))
    # Une unité de consommation : 12 × 1 337 = 16 044 € ; la garantie complète le salaire net et la prime d'activité.
    assert resultat["revenu_disponible"] == 16_044
    assert resultat["prestations_mesures"] == 16_044 - resultat["salaire_net"] - resultat["minima_sociaux"] > 0


def test_a_25_ans_la_garantie_ne_s_applique_plus():
    assert calculer(MESURE, Persona(adultes=(Adulte(age=25, salaire_brut_mensuel=TEMPS_PARTIEL),)))["prestations_mesures"] == 0
