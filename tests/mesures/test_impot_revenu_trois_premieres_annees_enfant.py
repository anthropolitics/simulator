from simulator.engine import Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("impot_revenu_trois_premieres_annees_enfant",)))


def test_une_famille_aisee_qui_travaille_a_3_000_euros_de_reduction_tant_que_l_enfant_a_moins_de_3_ans():
    def couple(age_enfant):
        return Persona(adultes=(Adulte(salaire_brut_mensuel=4000), Adulte(salaire_brut_mensuel=4000)), enfants=(age_enfant,))

    # Même nombre de parts : seul l'âge de l'enfant change. À 3 ans, l'impôt est celui de la loi actuelle, plus de 3 000 €.
    trois_ans, un_an = calculer(MESURE, couple(3)), calculer(MESURE, couple(1))
    assert trois_ans["impot_revenu"] < -3000
    assert un_an["impot_revenu"] - trois_ans["impot_revenu"] == 3000
