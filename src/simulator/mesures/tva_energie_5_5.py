from openfisca_core.model_api import Variable

from simulator.consommation import ENERGIE
from simulator.mesures import Cout, Mesure

TAUX = 0.055


def taux_reduit(poste: str) -> type[Variable]:
    def formula_2025_01_01(menage, period):
        return menage.empty_array() + TAUX

    return type(f"taux_tva_{poste}", (Variable,), {"formula_2025_01_01": formula_2025_01_01})


def appliquer(reforme):
    for poste in ENERGIE:
        reforme.update_variable(taux_reduit(poste))


MESURE = Mesure(
    id="tva_energie_5_5",
    titre="TVA à 5,5 % sur l'électricité, le gaz, les carburants, le fioul et le bois",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/22-mesures",
    citation=("Baisser la TVA de 20% à 5.5% sur les produits énergétiques (carburants, fioul, gaz et électricité) en tant que biens de première nécessité."),
    traduction=(
        "Mesure 4 des « 22 mesures pour 2022 ». Le rapport « Présidentielle 2027 — Analyse des programmes » (28 octobre 2026, p. 16) la décrit "
        "pour 2027 comme une « TVA de 20 % à 5,5 % sur l'électricité, le gaz, les carburants, le fioul et le bois » : le calcul suit cette "
        "description, la plus récente, et inclut donc le bois. À partir du 1er janvier 2025, le taux de TVA de chaque poste d'énergie du "
        "ménage (électricité, gaz, fioul, carburants, et autres énergies du logement : bois, charbon, chaleur des réseaux) passe à 5,5 %. "
        "Les dépenses d'énergie sont celles du persona, ou, à défaut, celles d'un ménage moyen de son décile de niveau de vie dans l'enquête "
        "Budget de famille 2017 de l'Insee, portées aux prix de 2025. Le gain est la baisse de la TVA payée sur ces dépenses ; il compte dans "
        "l'écart de pouvoir d'achat, pas dans le revenu disponible, qui ne comprend pas les impôts sur la consommation."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # document de la campagne 2022, que seule une source de 2026 rattache au programme 2027
    hypotheses=(
        "La baisse de taux est supposée passer entièrement dans le prix payé, convention de l'incidence statique ; une répercussion partielle "
        "réduirait le gain. Les quantités consommées sont tenues fixes : la hausse de la consommation que la baisse de prix pourrait entraîner "
        "n'est pas calculée, pas plus que l'effet sur les émissions et le financement de la mesure."
    ),
    cout=Cout(
        9,
        13.6,
        "10,96 Md€ selon le contre-budget 2026 du groupe RN, « Baisse TVA énergies », bois compris "
        "(https://rassemblementnational.fr/documents/GRN-CONTRE-BUDGET-2026.pdf#page=7) ; 11,3 Md€, de 9 à 13,6, selon l'Institut Montaigne en "
        "2024, sans le bois "
        "(https://www.institutmontaigne.org/legislatives-2024/rassemblement-national/baisser-la-tva-de-20-a-55-pour-les-carburants-lelectricite-le-gaz-et-le-fioul-domestique). "
        "Sources consultées le 20 novembre 2026.",
    ),
)
