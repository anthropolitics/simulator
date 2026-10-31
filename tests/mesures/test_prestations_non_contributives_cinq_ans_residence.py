from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("prestations_non_contributives_cinq_ans_residence",))


def parent_seul(nationalite="FR", annees=0):
    """Sans revenu, deux enfants, locataire : RSA, prestations familiales et aide au logement."""
    return Persona(adultes=(Adulte(nationalite=nationalite, annees_titre_sejour=annees),), enfants=(3, 7), loyer_mensuel=600, code_commune="69123")


def test_un_menage_francais_ou_resident_depuis_cinq_ans_garde_ses_prestations():
    mixte = Persona(adultes=(Adulte(salaire_brut_mensuel=1800), Adulte(nationalite="US", annees_titre_sejour=1)), enfants=(4, 8))
    for persona in (parent_seul(), parent_seul("US", 5), parent_seul("DE", 5), mixte):
        assert calculer(loi(SCENARIO), persona) == calculer(LOI_ACTUELLE, persona)


def test_avant_cinq_ans_un_menage_etranger_perd_toutes_ses_prestations():
    # Aujourd'hui, le RSA s'ouvre après trois mois de résidence pour un Européen, après cinq ans de titre de séjour pour les autres.
    for nationalite, rsa_actuel in (("DE", True), ("US", False)):
        persona = parent_seul(nationalite, 4)
        avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(SCENARIO), persona)
        assert avant["prestations_familiales"] > 0 and avant["aides_logement"] > 0 and (avant["minima_sociaux"] > 0) == rsa_actuel
        assert apres["prestations_familiales"] == apres["minima_sociaux"] == apres["aides_logement"] == apres["prestations_sociales"] == 0
        assert avant["revenu_disponible"] - apres["revenu_disponible"] == avant["prestations_sociales"]
