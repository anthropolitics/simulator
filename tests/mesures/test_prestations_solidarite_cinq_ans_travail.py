import pytest

from simulator.consommation import POSTES
from simulator.engine import Scenario, calculer, loi
from simulator.persona import Adulte, Depenses, Persona

SCENARIO = Scenario(mesures=("prestations_solidarite_cinq_ans_travail",))


def parent_seul(annees_travail_france):
    """Étrangère sans revenu, dix ans de titre de séjour, deux enfants, locataire. Dépenses fixées : imputées, elles suivraient le niveau de vie."""
    adulte = Adulte(nationalite="US", annees_titre_sejour=10, annees_travail_france=annees_travail_france)
    return Persona(adultes=(adulte,), enfants=(3, 7), loyer_mensuel=600, code_commune="69123", depenses=Depenses(**dict.fromkeys(POSTES, 1000)))


def test_sous_cinq_ans_de_travail_les_minima_sociaux_et_l_aide_au_logement_sont_perdus_et_seulement_eux():
    sous, dessus = (calculer(loi(SCENARIO), parent_seul(n)) for n in (4, 5))
    assert sous["minima_sociaux"] == sous["aides_logement"] == 0 < dessus["aides_logement"] < dessus["minima_sociaux"]
    perdu = dessus["minima_sociaux"] + dessus["aides_logement"]
    attendu = {
        "minima_sociaux": dessus["minima_sociaux"],
        "aides_logement": dessus["aides_logement"],
        "prestations_sociales": perdu,
        "revenu_disponible": perdu,
    }
    # Les prestations familiales restent : elles relèvent de la condition de nationalité de l'autre mesure du programme.
    assert {sortie: dessus[sortie] - sous[sortie] for sortie in dessus} == pytest.approx({sortie: attendu.get(sortie, 0) for sortie in dessus}, abs=1)
