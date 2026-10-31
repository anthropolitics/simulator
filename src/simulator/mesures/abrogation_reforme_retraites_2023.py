from dataclasses import replace

from simulator.mesures import Mesure
from simulator.retraites import Parametres

# La loi d'avant la réforme de 2023. Âge légal de 62 ans à partir de la génération 1955 (L161-17-2 CSS, loi n° 2010-1330 du 9 novembre 2010).
AGE_LEGAL = ((1961, 62 * 12),)
# Durée requise de la loi n° 2014-40 du 20 janvier 2014, art. 2 (L161-17-3 CSS) : un trimestre de plus toutes les trois générations.
DUREE_REQUISE = ((1961, 168), (1964, 169), (1967, 170), (1970, 171), (1973, 172))
# Carrières longues (D351-1-1 CSS jusqu'au 31 août 2023) : 58 ans pour un début avant 16 ans, avec 8 trimestres cotisés de plus que la durée
# requise ; 60 ans pour un début avant 20 ans, avec la durée requise.
CARRIERES_LONGUES = ((16, 58 * 12, 8), (20, 60 * 12))


def retraites(parametres: Parametres) -> Parametres:
    return replace(parametres, age_legal=AGE_LEGAL, duree_requise=DUREE_REQUISE, carrieres_longues=CARRIERES_LONGUES)


MESURE = Mesure(
    id="abrogation_reforme_retraites_2023",
    titre="Abrogation de la réforme des retraites de 2023 : retour à 62 ans et au calendrier de durée de 2014",
    candidats=("Marine Tondelier", "Raphaël Glucksmann", "Nicolas Dupont-Aignan"),
    source=(
        "Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 42 ; "
        "https://place-publique.eu/document/6J8wjk3EW8dBCLwKxa7J96/projet-placepublique-acte1.pdf ; https://www.debout-la-france.fr/projet/retraites/"
    ),
    citation=(
        "Marine Tondelier (rapport, p. 42) : « Abrogation de la réforme de 2023 ; retour à 62 ans ; prise en compte de la pénibilité ; minimum de "
        "pension à 1 200 € » ; Raphaël Glucksmann (Place publique, « Acte un », chantier 19) : « Abroger la réforme Macron de 2023 » ; Nicolas "
        "Dupont-Aignan (Debout la France) : « Maintenir l'âge minimum de départ à la retraite et la durée de cotisations aux niveaux actuels »."
    ),
    traduction=(
        "Sources, consultées le 31 octobre 2026. Marine Tondelier : le rapport « Présidentielle 2027 — Analyse des programmes » et franceinfo (30 "
        "septembre 2026), où elle veut abroger la dernière réforme : « On revient mécaniquement à 62 ans en un trait de plume » ; le projet 2027 des "
        "Écologistes (https://lesecologistes.fr/pages/6ImK65GKUnvibm33WGkjkj/projet-2027) n'a pas pu être lu, le site refusant l'accès (erreur 403). "
        "Raphaël Glucksmann : le projet de Place publique « Acte un », présenté le 23 juin 2025 (Public Sénat, 23 juin 2025), avant sa candidature du "
        "23 août 2026, et que franceinfo (30 septembre 2026) cite comme son projet ; il veut ensuite « cesser la focalisation sur le seul âge légal » "
        "(« certains doivent pouvoir partir à la retraite à 60 ans, d'autres devront travailler davantage »), sans paramètre, ce qui n'est pas simulé. "
        "La « convergence vers un âge de départ à 63 ans » que le rapport lui prête (p. 27) ne figure dans aucun de ses documents, ni dans la presse "
        "(franceinfo, 30 septembre 2026 ; Public Sénat, 24 août 2026 ; Yahoo Finance, 24 septembre 2026 : il « ne fixe pas, pour l'instant, de nouvel "
        "âge légal unique ») : elle n'est pas retenue. Nicolas Dupont-Aignan : la page « Retraites » de Debout la France, non datée, écrite vers "
        "2021-2022 (données jusqu'à 2021) ; aucun document de la campagne 2027 n'a été trouvé. Garder les niveaux de 2022, c'est la loi d'avant "
        "2023, comme l'abroger. Le calcul revient à cette loi pour l'âge, la durée et les carrières longues. L'âge légal est de 62 ans pour toutes "
        "les générations simulées, au lieu de 62 ans à 64 ans (à partir de 1969). La durée requise suit la loi du 20 janvier 2014 : 168 trimestres "
        "pour les générations 1961 à 1963, 169 de 1964 à 1966, 170 de 1967 à 1969, 171 de 1970 à 1972, 172 à partir de 1973, au lieu de 172 dès "
        "1966. Les carrières longues reprennent leurs deux bornes d'avant le 1er septembre 2023 : 58 ans pour un début avant 16 ans, avec 8 "
        "trimestres cotisés de plus que la durée requise, et 60 ans pour un début avant 20 ans, avec la durée requise (Conseil d'orientation des "
        "retraites, séance du 14 mars 2024, document n° 7, https://www.cor-retraites.fr/sites/default/files/2024-03/Doc_07_point_actualite_RACL_RP.pdf ; "
        "Legisocial, 16 février 2023) ; les bornes de 18 et 21 ans disparaissent. L'âge du taux plein automatique, 67 ans, n'avait pas changé en "
        "2023. Les autres dispositions de la réforme de 2023, dont la revalorisation du minimum contributif, sont gardées : les sources ne parlent "
        "que de l'âge et de la durée. La mesure s'applique d'emblée. Dans le moteur, un salarié né en 1985 qui cotise sans interruption part au "
        "même âge pour un début de 16 à 24 ans, la durée de 172 trimestres étant la même ; un début à 14 ou 15 ans le fait partir à 59 ou 60 ans au "
        "lieu de 58, à cause des 8 trimestres de plus. Les générations 1964 à 1972 partent plus tôt (né en 1966 avec un début à 20 ans : 62 ans et "
        "3 mois au lieu de 63 ans). Le minimum de pension à 1 200 € de Marine Tondelier et de Raphaël Glucksmann est la mesure minimum_pension_1200."
    ),
    retraites=retraites,
    a_confirmer=True,  # « Acte un » date de juin 2025, avant la campagne ; la page de Debout la France de 2021-2022 ; le projet des Écologistes illisible
    hypotheses=(
        "La prise en compte de la pénibilité, l'objectif d'un départ à 60 ans (Marine Tondelier) et la réforme qui suivrait l'abrogation (Raphaël "
        "Glucksmann) ne sont pas simulés : les sources ne les chiffrent pas. L'indexation des retraites sur l'inflation (Nicolas Dupont-Aignan) "
        "ne change rien dans un calcul en euros constants de 2025. La carrière et le salaire sont tenus fixes ; ni l'emploi des seniors, ni le "
        "financement, ni le coût pour les comptes publics ne sont calculés."
    ),
)
