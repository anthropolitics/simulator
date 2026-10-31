from openfisca_core.model_api import MONTH, Variable, where
from openfisca_france.entities import Individu

from simulator.mesures import Mesure, ajouter_prestation

# Montants du livret : par mois pour le jeune, par an pour l'employeur, avant 18 ans puis de 18 à 25 ans.
JEUNE = (230, 330)
EMPLOYEUR = (2750, 4000)


def selon_age(individu, period, montants):
    return individu("apprenti", period) * where(individu("age", period) < 18, *montants)


class cheque_formation_apprenti(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = "Chèque formation versé par l'État à l'apprenti"

    def formula(individu, period):
        return selon_age(individu, period, JEUNE)


def appliquer(reforme):
    ajouter_prestation(reforme, cheque_formation_apprenti)
    actuel = reforme.variables["cout_differe"].get_formula("2025-01-01")

    class cout_differe(Variable):
        def formula_2025_01_01(individu, period, parameters):
            return actuel(individu, period, parameters) + selon_age(individu, period, EMPLOYEUR) / 12

    reforme.update_variable(cout_differe)


MESURE = Mesure(
    id="cheque_formation_apprentis",
    titre="Chèque formation de 230 à 330 € par mois pour les apprentis et leurs employeurs",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/documents/projet/projet-la-jeunesse.pdf",
    citation=(
        "Je mettrai en place un chèque formation accessible à tous les 18-25 ans versé par l'État. Il correspondra à 50 % de ce que coûterait la "
        "formation d'un jeune s'il était scolarisé dans une filière générale. Pour un apprenti de 16 ans, cela représente 5 500 €, équitablement "
        "partagés entre la rémunération qu'il touchera chaque mois et son entreprise d'accueil. Pour un jeune au-dessus de 18 ans, 8 000€. "
        "Concrètement, cela signifie une hausse de 230 € de la rémunération mensuelle de tous les moins de 18 ans (et de 330 € pour les 18-25) qui "
        "feront le choix de l'apprentissage, de l'alternance ou de la formation professionnelle. Pour l'entreprise formatrice, ce sont 2 750 € ou 4 "
        "000 € qui viendront récompenser chaque année son effort en faveur de l'insertion professionnelle de nos jeunes."
    ),
    traduction=(
        "Le livret « Les jeunes » de la présidentielle 2022, publié sur le site du Rassemblement national, détaille la mesure que la page des 22 "
        "mesures résume ainsi : « Créer un chèque-formation mensuel de 200 à 300€ pour les apprentis, les alternants et leurs employeurs » "
        "(https://rassemblementnational.fr/22-mesures). À partir du 1er janvier 2025, un apprenti (variable OpenFisca apprenti : contrat "
        "d'apprentissage de moins de trois ans, 16 à 24 ans) reçoit de l'État 230 € par mois avant 18 ans et 330 € de 18 à 25 ans, montants mensuels "
        "que donne le livret. Ce chèque est une prestation individuelle : la source ne dit rien de son régime fiscal et social, il n'est donc ni "
        "imposé, ni soumis à cotisations, ni compté dans les ressources des autres prestations. La part de l'employeur, 2 750 € ou 4 000 € par an, "
        "s'ajoute aux aides différées (variable cout_differe) et réduit d'autant le coût du travail. Les alternants en contrat de "
        "professionnalisation et les jeunes en formation professionnelle, que le persona ne décrit pas, ne sont pas simulés."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # document d'une campagne antérieure, que seule une source de 2026 rattache au programme 2027
    hypotheses="Le nombre d'apprentis, les embauches et les salaires versés par les employeurs sont tenus fixes. Le financement n'est pas calculé.",
)
