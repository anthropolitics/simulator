from openfisca_france.entities import Famille

from simulator.mesures import Mesure
from simulator.mesures.allocations_familiales_reservees_aux_francais import reserver

DUREE = 5  # années de titre de séjour et années travaillées en France, en équivalent temps plein


def un_parent_francais_ou_resident_actif(famille, mois):
    individu = famille.members
    francais = individu("nationalite", mois) == b"FR"
    resident_actif = (individu("duree_possession_titre_sejour", mois) >= DUREE) * (individu("annees_travail_france", mois.this_year) >= DUREE)
    return famille.any(francais + resident_actif, role=Famille.PARENT)


MESURE = Mesure(
    id="prestations_sociales_cinq_ans_sejour_et_travail",
    titre="Prestations sociales des étrangers conditionnées à cinq ans de séjour régulier et de travail en France",
    candidats=("Bruno Retailleau",),
    source="https://avecretailleau.fr/projet/mesure/conditionner-les-prestations-sociales-a-cinq-ans-de-sejour",
    citation=(
        "Conditionner l'accès des étrangers aux prestations sociales à cinq ans de séjour régulier et de travail en France, et subordonner l'aide "
        "sociale à la régularité du séjour. Ce principe sera inscrit dans la Constitution, faute de quoi il sera censuré comme il l'a déjà été."
    ),
    traduction=(
        "Mesure n° 10 du site de campagne, mise à jour le 22 septembre 2026 (consultée le 31 octobre 2026). La source ne liste pas les prestations ; "
        "elle justifie la mesure par la réciprocité (« on contribue, puis on reçoit ») et renvoie aux dispositions censurées de la loi immigration de "
        "janvier 2024, qui visaient des prestations non contributives. Toutes les prestations non contributives que calcule OpenFisca le sont : "
        "prestations familiales, minima sociaux (RSA, prime d'activité, allocation aux adultes handicapés, minimum vieillesse, allocation de "
        "solidarité spécifique) et aides au logement ; retraites et chômage, contributifs, ne changent pas. Elles sont annulées lorsque aucun des "
        "parents n'est français, ni n'a à la fois cinq ans de titre de séjour et cinq années travaillées en France, en équivalent temps plein, sans "
        "qu'un emploi en cours soit exigé : la source joint les deux conditions par « et ». Pour un couple, il suffit qu'un parent remplisse la "
        "condition, comme pour le revenu familial du candidat. Les ressortissants de l'Union européenne, que la source ne distingue pas, sont "
        "traités comme les autres étrangers. La condition de séjour régulier pour l'aide sociale ne change rien au persona, toujours en séjour "
        "régulier. Les prestations créées par d'autres mesures (revenu familial, revenu d'incitation à l'activité) gardent leurs propres conditions."
    ),
    appliquer=lambda reforme: reserver(reforme, ("prestations_familiales", "minima_sociaux", "aides_logement"), un_parent_francais_ou_resident_actif),
    hypotheses=(
        "La source prévoit une révision de la Constitution par référendum. Les aides locales et les prestations que ne calcule pas OpenFisca ne sont "
        "pas simulées, pas plus que les effets sur les comportements, dont les départs du territoire et l'activité."
    ),
)
