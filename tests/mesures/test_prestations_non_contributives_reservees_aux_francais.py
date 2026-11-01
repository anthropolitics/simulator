from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona


def test_une_famille_etrangere_meme_europeenne_perd_toutes_ses_prestations_non_contributives():
    # Allemande sans revenu, vingt ans de titre de séjour, deux enfants, locataire : prestations familiales, RSA et aide au logement aujourd'hui.
    persona = Persona(adultes=(Adulte(nationalite="DE", annees_titre_sejour=20),), enfants=(3, 7), loyer_mensuel=600, code_commune="69123")
    avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(Scenario(mesures=("prestations_non_contributives_reservees_aux_francais",))), persona)
    assert min(avant["prestations_familiales"], avant["minima_sociaux"], avant["aides_logement"]) > 0
    assert apres["prestations_familiales"] == apres["minima_sociaux"] == apres["aides_logement"] == apres["prestations_sociales"] == 0
    assert avant["revenu_disponible"] - apres["revenu_disponible"] == avant["prestations_sociales"]
