from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("apl_plus_10_pourcent",)))


def test_les_aides_au_logement_augmentent_de_10_pourcent():
    locataire = Persona(adultes=(Adulte(salaire_brut_mensuel=1800),), enfants=(5,), loyer_mensuel=700, code_commune="69123")
    avant, apres = calculer(LOI_ACTUELLE, locataire), calculer(MESURE, locataire)
    assert avant["aides_logement"] > 0
    assert 0 <= 1.1 * avant["aides_logement"] - apres["aides_logement"] < 12  # chaque mois est arrondi à l'euro inférieur
    assert abs(apres["revenu_disponible"] - avant["revenu_disponible"] - (apres["aides_logement"] - avant["aides_logement"])) <= 1


def test_sans_aide_au_logement_rien_ne_change():
    persona = Persona(adultes=(Adulte(salaire_brut_mensuel=1800),))
    assert calculer(MESURE, persona) == calculer(LOI_ACTUELLE, persona)
