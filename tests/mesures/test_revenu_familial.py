import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, DepensesEnergie, Persona

MESURE = loi(Scenario(mesures=("revenu_familial",)))


def test_240_euros_par_enfant_mineur_a_la_place_des_allocations_familiales_et_du_quotient_familial():
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=2500), Adulte(salaire_brut_mensuel=2000)), enfants=(5, 10))
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(MESURE, couple)
    assert apres["prestations_mesures"] == 2 * 240 * 12
    assert apres["prestations_familiales"] == 0 < avant["prestations_familiales"]
    assert apres["impot_revenu"] < avant["impot_revenu"]  # plus de parts de quotient familial pour les enfants


def test_la_paje_est_maintenue():
    parents = Persona(adultes=(Adulte(salaire_brut_mensuel=1500), Adulte()), enfants=(1,))
    avant, apres = calculer(LOI_ACTUELLE, parents), calculer(MESURE, parents)
    assert apres["prestations_mesures"] == 240 * 12
    assert apres["prestations_familiales"] == avant["prestations_familiales"] > 0


def test_un_enfant_de_18_ans_ou_plus_ne_le_recoit_pas():
    assert calculer(MESURE, Persona(adultes=(Adulte(salaire_brut_mensuel=3000),), enfants=(19,)))["prestations_mesures"] == 0


def test_sans_enfant_rien_ne_change():
    seul = Persona(adultes=(Adulte(salaire_brut_mensuel=3000),))
    assert calculer(MESURE, seul) == calculer(LOI_ACTUELLE, seul)


def etranger(annees_titre_sejour=10, annees_travail_france=5):
    return Adulte(salaire_brut_mensuel=2500, nationalite="US", annees_titre_sejour=annees_titre_sejour, annees_travail_france=annees_travail_france)


@pytest.mark.parametrize(
    "adultes, droit",
    [
        ((Adulte(salaire_brut_mensuel=2500),), True),  # un Français, sans années de travail renseignées
        ((etranger(annees_titre_sejour=4, annees_travail_france=10),), False),
        ((etranger(), etranger(annees_titre_sejour=1, annees_travail_france=0)), True),  # un parent qui remplit la condition suffit
    ],
)
def test_un_parent_francais_ou_etranger_avec_cinq_ans_de_titre_de_sejour_et_de_travail_ouvre_droit(adultes, droit):
    assert calculer(MESURE, Persona(adultes=adultes, enfants=(5, 10)))["prestations_mesures"] == droit * 2 * 240 * 12


def test_sous_cinq_ans_de_travail_un_etranger_perd_le_revenu_familial_et_seulement_lui():
    # Dépenses d'énergie fixées : imputées, elles suivraient le niveau de vie de chaque ménage.
    energie = DepensesEnergie(electricite=1000, gaz=0, fioul=0, autres_energies_logement=0, carburants=1000)
    sous, dessus = (calculer(MESURE, Persona(adultes=(etranger(annees_travail_france=n),), enfants=(5, 10), depenses_energie=energie)) for n in (4, 5))
    perdu = {"prestations_mesures", "prestations_sociales", "revenu_disponible"}
    assert {sortie: dessus[sortie] - sous[sortie] for sortie in dessus} == {sortie: 2 * 240 * 12 * (sortie in perdu) for sortie in dessus}
