from dataclasses import replace

from simulator.mesures import Mesure
from simulator.retraites import Parametres

SMIC_NET_MENSUEL = 1700  # SMIC du programme, même document, p. 9
# Pension brute qui donne ce montant net à un retraité seul sans autre revenu : CSG au taux médian (6,6 %), CRDS (0,5 %) et CASA (0,3 %).
MINIMUM_PENSION_BRUT = round(SMIC_NET_MENSUEL / (1 - 0.066 - 0.005 - 0.003), 2)  # 1 835,85 €


def retraites(parametres: Parametres) -> Parametres:
    return replace(parametres, age_legal_cible=60 * 12, duree_requise_cible=160, minimum_pension=MINIMUM_PENSION_BRUT)


MESURE = Mesure(
    id="retraite_60_ans_40_annuites",
    titre="Retraite à 60 ans avec 40 annuités, pension minimum au niveau du SMIC (1 700 € net) pour une carrière complète",
    candidats=("Jean-Luc Mélenchon",),
    source="https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf",
    citation=(
        "« Nous abrogerons la réforme Borne qui a porté la retraite à 64 ans, ce qui occasionnera une dépense de 9 milliards d'euros. Cette abrogation "
        "immédiate sera un premier pas vers le retour à la retraite à 60 ans avec 40 annuités, objectif sur un mandat. [...] il faudra protéger le pouvoir "
        "d'achat en refusant la désindexation des pensions et porter la pension minimum au niveau du SMIC pour une carrière complète. » (p. 11 et 12)"
    ),
    traduction=(
        "Source : « Comment nous allons remettre de l'ordre dans les comptes publics », La France insoumise, document de la campagne présidentielle 2027 "
        "daté du 14 octobre 2026 (consulté le 31 octobre 2026) ; le rapport « Présidentielle 2027 — Analyse des programmes » (28 octobre 2026, p. 20) "
        "le résume en « retraite à 60 ans après 40 annuités ; prise en compte de la pénibilité ; minimum de pension au niveau du SMIC ». La cible est "
        "simulée d'emblée, pour toutes les générations : l'étape intermédiaire (abrogation de la réforme de 2023) et le calendrier « sur un mandat » ne "
        "le sont pas. L'âge légal passe à 60 ans (age_legal_cible) et la durée requise pour le taux plein à 160 trimestres (duree_requise_cible), au lieu "
        "de 62 ans et 9 mois à 64 ans et de 170 à 172 trimestres selon la génération. Le document ne dit rien des carrières longues, de l'âge du taux "
        "plein automatique, de la décote ni de la surcote : ils restent ceux de la loi actuelle. Les carrières longues gardent leurs bornes et "
        "exigent, comme aujourd'hui, la durée requise cotisée, soit 160 trimestres ; seul le départ à 58 ans pour un début avant 16 ans reste plus tôt "
        "que 60 ans, les autres bornes (60 à 63 ans) n'avancent plus aucun départ. Partir à 60 ans sans les 160 trimestres reste possible, avec la "
        "décote ; le taux plein vient au plus tard à 67 ans. Pension minimum : le même document porte le SMIC à 1 700 € net par mois (p. 9) ; le minimum "
        "est pris à ce montant, net, pension totale (régime de base et complémentaire) comprise, et proratisé pour une carrière incomplète, comme LFI "
        "l'avait précisé pour le minimum à 1 600 € net du programme du Nouveau Front populaire (« tout retraité avec une carrière complète touche "
        "1 600 euros net de retraites, MiCo et retraite complémentaire compris », Moneyvox, 25 juin 2024, "
        "https://www.moneyvox.fr/retraite/actualites/98415/petites-retraites-des-precisions-sur-le-minimum-a-1-600-euros-au-nouveau-front-populaire). "
        "Le moteur raisonne en pension brute : 1 700 € net valent 1 835,85 € brut pour un retraité seul sans autre revenu, qui paie la CSG au taux "
        "médian (6,6 %), la CRDS (0,5 %) et la CASA (0,3 %) ; un retraité au taux normal de CSG (8,3 %) toucherait 1 668,79 € net. Le montant, en "
        "euros de 2025 comme toute la simulation, est pris tel quel. Le minimum (minimum_pension) relève la pension totale au taux plein à "
        "1 835,85 € brut par mois, multipliés par les trimestres validés sur 160 quand il en manque ; une pension avec décote n'y a pas droit, comme "
        "pour le minimum contributif. Chaque adulte salarié part à l'âge où il atteint le taux plein, au plus tôt. La hausse de 10 % et "
        "l'indexation sur l'inflation des pensions déjà versées (p. 8) ne font pas partie de cette mesure."
    ),
    retraites=retraites,
    hypotheses=(
        "La prise en compte de la pénibilité n'est pas simulée : le document ne la détaille pas et le persona ne dit pas à quels risques il est "
        "exposé. Le financement, par les recettes nouvelles du document (dont la réduction des exonérations de cotisations sociales, p. 14), et "
        "ses effets sur les salaires et l'emploi ne sont pas calculés. La carrière et le salaire sont tenus fixes : ni l'emploi des seniors, ni "
        "l'effet du départ plus précoce sur les embauches, ni le coût pour les comptes publics ne sont calculés."
    ),
)
