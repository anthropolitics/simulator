from openfisca_core.model_api import Variable
from openfisca_france.entities import Famille

from simulator.mesures import Mesure

# Les montants bruts : les annuler annule aussi les montants nets de CRDS et leur prise en compte dans les ressources du RSA et de la prime d'activité.
PRESTATIONS_FAMILIALES = ("af", "cf", "ars", "asf", "aeeh", "paje_base", "paje_naissance", "paje_adoption", "paje_cmg")


def reserver(reforme, variables, condition):
    """Annule les montants des variables de la famille quand condition(famille, mois) est fausse."""
    for nom in variables:

        def formula(famille, period, parameters, actuelle=reforme.variables[nom]):
            calcul = actuelle.get_formula(period)
            montant = calcul(famille, period, parameters) if calcul.__code__.co_argcount == 3 else calcul(famille, period)
            return montant * condition(famille, period.first_month)

        reforme.update_variable(type(nom, (Variable,), {"formula": formula}))


def un_parent_francais(famille, mois):
    return famille.any(famille.members("nationalite", mois) == b"FR", role=Famille.PARENT)


MESURE = Mesure(
    id="allocations_familiales_reservees_aux_francais",
    titre="Réserver les allocations familiales aux Français",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/documents/202406-programme.pdf#page=6",
    citation=(
        "Réserver les allocations familiales aux Français et conditionner à 5 années de travail en France l’accès aux prestations sociales "
        "non-contributives comme le RSA (si nécessaire par référendum constitutionnel)"
    ),
    traduction=(
        "Seule la première partie de la mesure est simulée. Les prestations familiales (allocations familiales, complément familial, allocation de "
        "rentrée scolaire, allocation de soutien familial, allocation d'éducation de l'enfant handicapé, prestation d'accueil du jeune enfant) sont "
        "annulées lorsque aucun des parents n'est de nationalité française. Le livret « La famille » de la campagne de 2022 précise le périmètre "
        "et le critère : « toutes les allocations et primes de politique familiale seront réservées, exclusivement, aux familles dont au moins l’un "
        "des deux parents est Français » (https://rassemblementnational.fr/documents/projet/projet-la-famille.pdf, p. 7). Les ressortissants de "
        "l'Union européenne, que la source ne distingue pas, sont traités comme les autres étrangers. Le RSA et la prime d'activité, qui comptent "
        "ces prestations dans leurs ressources, sont recalculés sans elles."
    ),
    appliquer=lambda reforme: reserver(reforme, PRESTATIONS_FAMILIALES, un_parent_francais),
    a_confirmer=True,  # document d'une campagne antérieure, que seule une source de 2026 rattache au programme 2027
    hypotheses=(
        "La seconde partie, la condition de cinq années de travail en France pour les prestations non contributives comme le RSA, n'est pas "
        "simulée : le ménage type ne renseigne pas les années travaillées en France. Le RSA et les autres prestations non contributives des "
        "ménages étrangers restent soumis aux seules conditions de la loi actuelle. La source prévoit, si nécessaire, un référendum "
        "constitutionnel. L'usage des économies, que le livret destine notamment à « la revalorisation des aides dont bénéficient les "
        "nationaux », n'est pas simulé, pas plus que les effets sur les comportements."
    ),
)
