from dataclasses import replace

from simulator.mesures import Mesure
from simulator.retraites import Parametres

MINIMUM = 1200  # brut, par mois


def retraites(parametres: Parametres) -> Parametres:
    return replace(parametres, minimum_pension=max(parametres.minimum_pension, MINIMUM))


MESURE = Mesure(
    id="minimum_pension_1200",
    titre="Minimum de pension à 1 200 € brut par mois pour une carrière complète",
    candidats=("Marine Tondelier", "Raphaël Glucksmann"),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 27 et 42",
    citation=(
        "Marine Tondelier (p. 42) : « Abrogation de la réforme de 2023 ; retour à 62 ans ; prise en compte de la pénibilité ; minimum de pension à "
        "1 200 € » ; Raphaël Glucksmann (p. 27) : « Convergence vers un âge de départ à 63 ans ; prise en compte de la pénibilité ; minimum de "
        "pension à 1 200 € ; retraite progressive »."
    ),
    traduction=(
        "Seul le rapport « Présidentielle 2027 — Analyse des programmes » donne le montant. Le projet 2027 des Écologistes "
        "(https://lesecologistes.fr/pages/6ImK65GKUnvibm33WGkjkj/projet-2027) n'a pas pu être lu le 31 octobre 2026, le site refusant l'accès (erreur "
        "403) ; une page plus ancienne du parti, « II- Pour la justice sociale et une économie au service du climat », vise « une retraite minimum au "
        "niveau du Smic ». Le projet de Place publique, « Acte un » "
        "(https://place-publique.eu/document/6J8wjk3EW8dBCLwKxa7J96/projet-placepublique-acte1.pdf, consulté le 31 octobre 2026), veut « garantir des "
        "pensions décentes », sans montant. Les 1 200 € sont lus en brut : la source ne le dit pas, mais c'est le montant de la promesse de la réforme "
        "de 2023, une pension « d'environ 1 200 € » brut pour une carrière complète, 85 % du SMIC net (« ce plancher minimal [...] s'entend bien en "
        "pension brute », Moneyvox, 11 janvier 2023, "
        "https://www.moneyvox.fr/retraite/actualites/91361/petite-retraite-surprise-la-pension-minimale-sera-de-1200-euros-en-brut) ; lu en net, il "
        "vaudrait environ 1 300 € brut selon le taux de CSG. Le paramètre minimum_pension du moteur passe de 0 à 1 200 € : la pension totale "
        "(régime général et Agirc-Arrco) d'un salarié qui part au taux plein est relevée à 1 200 € brut par mois s'il a la durée requise, et au "
        "prorata des trimestres validés sur la durée requise sinon, comme le minimum contributif (un salarié né en 1985 avec 108 trimestres sur 172 a "
        "droit à 1 200 × 108 / 172 = 753,49 €). Le complément est versé par le régime général. Une pension avec décote n'y a pas droit ; aucune "
        "condition de trimestres cotisés ni de plafond de l'ensemble des retraites n'est ajoutée, la source n'en disant rien. Le montant, en euros de "
        "2025 comme toute la simulation, est pris tel quel. La mesure vaut pour les salariés qui partiront ; les retraites déjà versées, saisies "
        "dans le persona, ne changent pas."
    ),
    retraites=retraites,
    a_confirmer=True,  # aucun document des Écologistes ou de Place publique lu ne porte le montant de 1 200 €
    hypotheses=(
        "Le financement n'est pas calculé, ni l'effet du minimum sur les pensions déjà versées, sur le minimum vieillesse ou sur la décision de "
        "partir plus tôt ou plus tard."
    ),
)
