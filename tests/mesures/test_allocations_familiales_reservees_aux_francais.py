from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("allocations_familiales_reservees_aux_francais",))
ENFANTS = (1, 8, 12)  # un enfant de moins de 3 ans ouvre aussi la PAJE


def couple(premier="FR", second="FR"):
    return Persona(
        adultes=tuple(Adulte(salaire_brut_mensuel=4000, nationalite=n, annees_titre_sejour=20) for n in (premier, second)),
        enfants=ENFANTS,
    )


def test_une_famille_dont_un_parent_est_francais_garde_ses_prestations():
    for persona in (couple(), couple(second="DE"), couple(premier="US")):
        assert calculer(loi(SCENARIO), persona) == calculer(LOI_ACTUELLE, persona)


def test_une_famille_de_parents_etrangers_perd_ses_prestations_familiales_et_seulement_elles():
    for nationalite in ("DE", "US"):  # Union européenne ou non, quelle que soit l'ancienneté du titre de séjour
        persona = couple(nationalite, nationalite)
        avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(SCENARIO), persona)
        assert avant["prestations_familiales"] > 0 and avant["minima_sociaux"] == avant["aides_logement"] == 0
        assert apres["prestations_familiales"] == 0
        assert avant["revenu_disponible"] - apres["revenu_disponible"] == avant["prestations_familiales"]


def test_le_rsa_compte_la_perte_des_prestations_familiales():
    persona = Persona(adultes=(Adulte(nationalite="US", annees_titre_sejour=6),), enfants=(3, 7), loyer_mensuel=600, code_commune="69123")
    avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(SCENARIO), persona)
    assert apres["prestations_familiales"] == 0 < avant["prestations_familiales"]
    assert avant["minima_sociaux"] < apres["minima_sociaux"]
    assert 0 < avant["revenu_disponible"] - apres["revenu_disponible"] < avant["prestations_familiales"]
