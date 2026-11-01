from simulator.engine import Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("prestations_sociales_cinq_ans_sejour_et_travail",)))


def parent_seul(annees_travail_france):
    """Étrangère avec dix ans de titre de séjour, à mi-temps, deux enfants, locataire : prestations familiales, RSA ou prime d'activité, aide au logement."""
    adulte = Adulte(salaire_brut_mensuel=900, nationalite="US", annees_titre_sejour=10, annees_travail_france=annees_travail_france)
    return Persona(adultes=(adulte,), enfants=(4, 8), loyer_mensuel=600, code_commune="69123")


def test_sans_cinq_annees_de_travail_un_menage_etranger_perd_ses_prestations_non_contributives():
    # Dix ans de titre de séjour suffisent aujourd'hui, et pour la condition de résidence de David Lisnard ; il faut en plus cinq années travaillées.
    sous, dessus = calculer(MESURE, parent_seul(4)), calculer(MESURE, parent_seul(5))
    assert dessus["prestations_familiales"] > 0 and dessus["minima_sociaux"] > 0 and dessus["aides_logement"] > 0
    assert sous["prestations_familiales"] == sous["minima_sociaux"] == sous["aides_logement"] == sous["prestations_sociales"] == 0
    assert dessus["revenu_disponible"] - sous["revenu_disponible"] == dessus["prestations_sociales"]
