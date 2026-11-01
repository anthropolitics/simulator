from openfisca_france.entities import Famille

from simulator.mesures import Mesure
from simulator.mesures.allocations_familiales_reservees_aux_francais import reserver

DUREE = 5  # années travaillées en France, en équivalent temps plein


def un_parent_francais_ou_ayant_travaille_cinq_ans(famille, mois):
    individu = famille.members
    francais = individu("nationalite", mois) == b"FR"
    return famille.any(francais + (individu("annees_travail_france", mois.this_year) >= DUREE), role=Famille.PARENT)


MESURE = Mesure(
    id="prestations_solidarite_cinq_ans_travail",
    titre="Prestations de solidarité réservées aux Français et aux étrangers ayant travaillé cinq ans en France",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/documents/202406-programme.pdf#page=6",
    citation=(
        "Réserver les allocations familiales aux Français et conditionner à 5 années de travail en France l’accès aux prestations sociales "
        "non-contributives comme le RSA (si nécessaire par référendum constitutionnel)"
    ),
    traduction=(
        "Seconde partie de la mesure du programme des législatives de 2024 ; la première, les prestations familiales réservées aux Français, est "
        "la mesure allocations_familiales_reservees_aux_francais. Le livret « Le contrôle de l'immigration » de la campagne de 2022 donne le "
        "périmètre : « Les prestations de solidarité qui ne relèvent pas d’un régime d’assurance seront soit réservées aux Français, soit soumises "
        "à des conditions fixées par loi, notamment en termes de durée de travail. Il faudra avoir travaillé durant cinq années en France pour "
        "pouvoir prétendre au bénéfice de ces prestations. Les allocations familiales [...] seront réservées aux Français » "
        "(https://rassemblementnational.fr/documents/projet/projet-controle-de-limmigration.pdf, p. 14). Le contre-budget 2026 du groupe RN "
        "(23 octobre 2025) chiffre à 6,1 Md€ « Réserver le bénéfice des prestations de solidarités aux étrangers ayant au moins 5 ans ETP "
        "travaillés en France » (https://rassemblementnational.fr/documents/GRN-CONTRE-BUDGET-2026.pdf#page=7) ; le dossier de presse du 6 "
        "octobre 2026, qui n'est pas en ligne, garde les « prestations de solidarité après 5 ans de travail », à côté des « prestations "
        "familiales : un parent français », selon l'Institut de l'Entreprise "
        "(https://www.institut-entreprise.fr/wp-content/uploads/2026/10/Analyse-primaire-contre-budget-RN-Note-de-contexte-IDEP.pdf, p. 6) ; "
        "sources consultées le 31 octobre 2026. Les prestations visées sont donc les prestations non contributives autres que familiales, que "
        "les deux chiffrages comptent à part : minima sociaux (RSA, prime d'activité, allocation aux adultes handicapés, minimum vieillesse, "
        "allocation de solidarité spécifique) et aides au logement. Elles sont annulées lorsque aucun des parents n'est français ni n'a "
        "travaillé au moins cinq ans en France, en équivalent temps plein, sans qu'un emploi en cours soit exigé ; pour un couple, il suffit que "
        "l'un des deux remplisse la condition, comme pour la nationalité dans le livret « La famille ». Les ressortissants de l'Union "
        "européenne, que les sources ne distinguent pas, sont traités comme les autres étrangers. Les conditions de la loi actuelle, dont cinq "
        "ans de titre de séjour pour le RSA et la prime d'activité, s'appliquent en plus."
    ),
    appliquer=lambda reforme: reserver(reforme, ("minima_sociaux", "aides_logement"), un_parent_francais_ou_ayant_travaille_cinq_ans),
    a_confirmer=True,  # le dossier de presse du 6 octobre 2026 n'est connu que par une note de l'Institut de l'Entreprise
    hypotheses=(
        "La source prévoit, si nécessaire, un référendum constitutionnel. Les aides locales et les prestations que ne calcule pas OpenFisca ne "
        "sont pas simulées, pas plus que les effets sur les comportements, dont les départs du territoire et l'activité."
    ),
)
