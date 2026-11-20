from openfisca_france.entities import Famille

from simulator.mesures import Cout, Mesure
from simulator.mesures.allocations_familiales_reservees_aux_francais import reserver

DUREE = 5  # années de résidence régulière


def un_parent_francais_ou_resident(famille, mois):
    nationalite, titre = famille.members("nationalite", mois), famille.members("duree_possession_titre_sejour", mois)
    return famille.any((nationalite == b"FR") + (titre >= DUREE), role=Famille.PARENT)


MESURE = Mesure(
    id="prestations_non_contributives_cinq_ans_residence",
    titre="Conditionner les prestations sociales non contributives aux étrangers résidant régulièrement depuis au moins cinq ans",
    candidats=("David Lisnard",),
    source="https://www.unenouvelleenergie.fr/notre-programme/immigration/",
    citation=(
        "Conditionner les prestations sociales non contributives aux étrangers résidant régulièrement sur le territoire national depuis au moins cinq ans"
    ),
    traduction=(
        "La source ne détaille pas les prestations visées ; toutes les prestations non contributives que calcule OpenFisca le sont : prestations "
        "familiales, minima sociaux (RSA, prime d'activité, allocation aux adultes handicapés, minimum vieillesse, allocation de solidarité "
        "spécifique) et aides au logement. Elles sont annulées lorsque aucun des parents n'est français ni titulaire d'un titre de séjour depuis "
        "au moins cinq ans ; pour un couple, il suffit que l'un des deux remplisse la condition. L'ancienneté du titre de séjour du ménage type "
        "mesure la durée de résidence régulière. Les ressortissants de l'Union européenne, que la source ne distingue pas, sont traités comme les "
        "autres étrangers. La loi actuelle exige déjà des étrangers hors Espace économique européen cinq ans de titre de séjour pour le RSA et la "
        "prime d'activité, et dix ans pour le minimum vieillesse."
    ),
    appliquer=lambda reforme: reserver(reforme, ("prestations_familiales", "minima_sociaux", "aides_logement"), un_parent_francais_ou_resident),
    hypotheses="Les aides locales et les prestations que ne calcule pas OpenFisca ne sont pas simulées, pas plus que les effets sur les comportements.",
    cout=Cout(
        -8,
        -1.6,
        "Économie de 8 Md€ par an selon le candidat (https://www.unenouvelleenergie.fr/questions/le-programme-de-david-lisnard-est-il-chiffre/) ; "
        "2,1 Md€, de 1,6 à 2,7, selon l'Institut Montaigne, qui chiffrait en 2022 la même condition de cinq ans pour les seuls étrangers "
        "extra-européens "
        "(https://www.institutmontaigne.org/presidentielle-2022/valerie-pecresse/instaurer-un-minimum-de-5-ans-sur-le-territoire-pour-toucher-les-prestations-sociales-financees-en-dehors-des-cotisations-salariales). "
        "Sources consultées le 20 novembre 2026.",
    ),
)
