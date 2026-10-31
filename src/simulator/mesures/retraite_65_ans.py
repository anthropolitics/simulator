from dataclasses import replace

from simulator.mesures import Mesure
from simulator.retraites import Parametres

# Âge légal en mois par génération : 3 mois de plus par génération à partir de 1964, jusqu'à 65 ans pour la génération 1972.
AGE_LEGAL = (
    (1961, 62 * 12),
    (1962, 62 * 12 + 6),
    (1963, 62 * 12 + 9),
    (1964, 63 * 12),
    (1965, 63 * 12 + 3),
    (1966, 63 * 12 + 6),
    (1967, 63 * 12 + 9),
    (1968, 64 * 12),
    (1969, 64 * 12 + 3),
    (1970, 64 * 12 + 6),
    (1971, 64 * 12 + 9),
    (1972, 65 * 12),
)


def retraites(parametres: Parametres) -> Parametres:
    return replace(parametres, age_legal=AGE_LEGAL)


MESURE = Mesure(
    id="retraite_65_ans",
    titre="Âge légal de départ à la retraite porté à 65 ans",
    candidats=("David Lisnard",),
    source="https://www.unenouvelleenergie.fr/notre-programme/reussir-une-nouvelle-ambition-francaise/",
    citation=(
        "« La réforme des retraites : la priorité de l'augmentation de l'âge de la retraite avant la réforme d'ensemble combinant la répartition et la "
        "capitalisation » ; « la norme de l'âge légal de 65 ans est un impératif national urgent pour des raisons d'équilibre financier. »"
    ),
    traduction=(
        "Le programme de Nouvelle Énergie, le parti de David Lisnard (page consultée le 31 octobre 2026), fixe la cible, 65 ans, sans calendrier ni "
        "changement de la durée de cotisation ; le rapport « Présidentielle 2027 — Analyse des programmes » (28 octobre 2026) résume « âge de départ à "
        "65 ans ». L'âge légal monte de 3 mois par génération, le rythme de la réforme de 2023, à partir de la génération 1964, la première qui n'avait "
        "pas atteint l'âge légal en 2025, l'année simulée : 63 ans pour la génération 1964, 64 ans pour 1968, 65 ans à partir de 1972 (au lieu de 62 ans et "
        "9 mois pour 1964 et 1965, puis 63 ans et 3 mois à 64 ans de 1966 à 1969). Ce choix suit l'« impératif urgent » : la hausse commence dès la "
        "prochaine génération, mais par paliers, comme toutes les réformes de l'âge depuis 2010, plutôt qu'en une fois. La durée requise reste celle de "
        "la loi actuelle (172 trimestres à partir de la génération 1966) : quand elle n'est atteinte qu'après 65 ans, l'âge de départ au taux plein ne "
        "change pas. Les carrières longues (départ de 58 à 63 ans selon l'âge de début et la génération, avec la durée requise cotisée) et l'âge du taux plein "
        "automatique, 67 ans, ne changent pas : le programme n'en parle pas."
    ),
    retraites=retraites,
    a_confirmer=True,  # page du parti non datée, déjà en ligne en août 2025 (Wayback Machine), avant la candidature du 31 mars 2026
    hypotheses=(
        "La réforme d'ensemble qui suivrait n'est pas simulée : socle de pension minimale par répartition versé à partir de 65 ans, minimum vieillesse "
        "de 1 000 € par mois, autres régimes convertis à la capitalisation en « environ 8 tranches », cotisations obligatoires placées dans un dispositif "
        "individuel, agence centrale de retraite. Le calcul tient la carrière et le salaire fixes : ni l'emploi des seniors, ni le chômage, l'invalidité "
        "ou les minima sociaux entre l'ancien et le nouvel âge de départ, ni les économies pour les comptes publics ne sont calculés."
    ),
)
