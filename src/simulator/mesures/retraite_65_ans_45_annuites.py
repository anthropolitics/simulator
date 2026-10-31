from dataclasses import replace

from simulator.mesures import Mesure
from simulator.mesures.retraite_65_ans import AGE_LEGAL
from simulator.retraites import Parametres

# Durée requise en trimestres par génération : celle de la réforme de 2023 jusqu'à 1968, puis 2 trimestres de plus par génération, 180 à partir de 1972.
DUREE_REQUISE = ((1961, 168), (1962, 169), (1963, 170), (1964, 171), (1965, 172), (1969, 174), (1970, 176), (1971, 178), (1972, 180))


def retraites(parametres: Parametres) -> Parametres:
    return replace(parametres, age_legal=AGE_LEGAL, duree_requise=DUREE_REQUISE)


MESURE = Mesure(
    id="retraite_65_ans_45_annuites",
    titre="Âge légal porté à 65 ans et durée de cotisation à 45 ans",
    candidats=("Édouard Philippe",),
    source="https://www.youtube.com/watch?v=tZuZwWpT4ak",
    citation=(
        "« Je propose de porter progressivement la durée de cotisation à 45 ans et l'âge de départ à 65 ans » : d'abord reprendre la réforme de 2023 "
        "(64 ans et 43 ans de cotisation), puis « en moins de dix ans, on passe » à 65 ans et 45 ans."
    ),
    traduction=(
        "Édouard Philippe a présenté sa réforme dans la vidéo « Retraites : la réforme que je propose aux Français », publiée sur sa chaîne YouTube le "
        "29 septembre 2026 ; la citation est celle de LCP (https://lcp.fr/actualites/retraites-edouard-philippe-veut-porter-l-age-de-depart-a-65-ans-et-la-duree-de, "
        "29 septembre 2026, consulté le 31 octobre 2026), recoupée par Public Sénat et l'AFP (Moneyvox) le même jour. Le rapport « Présidentielle 2027 — "
        "Analyse des programmes » (28 octobre 2026) écrit encore « maintien de l'âge légal à 64 ans ; allongement de la durée de cotisation » : la vidéo, "
        "plus récente que le programme qu'il analyse, chiffre les deux. Le candidat ne donne pas de calendrier par génération. Première étape, la réforme "
        "de 2023 revient, la suspension de la LFSS pour 2026 étant annulée : 63 ans et 171 trimestres pour la génération 1964, 63 ans et 3 mois et 172 "
        "trimestres pour 1965, puis 3 mois de plus par génération jusqu'à 64 ans pour 1968. Seconde étape, l'âge légal continue au même rythme, 64 ans et "
        "3 mois pour 1969 jusqu'à 65 ans pour 1972, et la durée requise monte de 2 trimestres par génération, de 174 pour 1969 à 180 pour 1972 : les deux "
        "cibles sont atteintes par la même génération, qui a 65 ans en 2037, une dizaine d'années après l'élection ; au rythme d'un trimestre par "
        "génération de la loi Touraine, les 45 ans ne seraient atteints qu'en 2041. Les carrières longues continuent, comme le candidat l'annonce, aux "
        "âges actuels (de 58 à 63 ans selon l'âge de début et la génération), mais avec la durée requise de la génération, comme aujourd'hui : avec 45 ans cotisés, "
        "commencer entre 15 et 19 ans fait partir entre 60 et 64 ans, ce que le candidat promet à « un Français sur trois ». L'âge du taux plein "
        "automatique reste 67 ans : la vidéo n'en parle pas."
    ),
    retraites=retraites,
    hypotheses=(
        "Le volet par capitalisation (fonds collectif obligatoire, plan d'épargne retraite pour tous, premier versement de l'État au premier emploi) n'est "
        "pas simulé, ni la prise en compte de la pénibilité, que le candidat annonce sans la détailler, ni les départs anticipés pour handicap, incapacité "
        "ou invalidité, que le moteur ne calcule pas et que le candidat garde à 55, 60 et 62 ans. Le calcul tient la carrière et le salaire fixes : ni "
        "l'emploi des seniors, ni le chômage, l'invalidité ou les minima sociaux avant le départ, ni les économies pour les comptes publics ne sont calculés."
    ),
)
