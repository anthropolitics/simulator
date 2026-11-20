from simulator.mesures import Cout, Mesure
from simulator.mesures.taxe_zucman_melenchon import HYPOTHESES, TRADUCTION, appliquer

MESURE = Mesure(
    id="taxe_zucman_tondelier",
    titre="Taxe Zucman : impôt plancher de 2 % sur les patrimoines de plus de 100 millions d'euros",
    candidats=("Marine Tondelier",),
    source="https://lesecologistes.fr/pages/6ImK65GKUnvibm33WGkjkj/projet-2027",
    citation="Mettre en place une taxe Zucman de 2 % au-delà de 100 millions d'euros de patrimoine.",
    traduction=(
        "Citation du programme « Pour une prospérité écologique » (p. 66) telle que la reproduit MonVote2027 ; la page des Écologistes n'a pas "
        "pu être consultée. Le rapport « Présidentielle 2027 — Analyse des programmes » (p. 42) indique un seuil de 50 M€ ; la mesure retient "
        "les 100 M€ du programme. La traduction est la même que pour la taxe Zucman de Jean-Luc Mélenchon : " + TRADUCTION
    ),
    appliquer=appliquer,
    a_confirmer=True,
    hypotheses=HYPOTHESES,
    cout=Cout(
        -25,
        -5,
        "15 à 25 Md€ de recettes selon le contre-budget des Écologistes du 4 septembre 2025, repris par la note de France Positive citée plus loin "
        "; le programme de 2027 ne donne pas de rendement. 15 à 25 Md€ de recettes selon Gabriel Zucman, cité par le rapport n° 689 du Sénat du 4 "
        "juin 2025, p. 41 (https://www.senat.fr/rap/l24-689/l24-6891.pdf) ; 5 Md€ selon Philippe Aghion et Xavier Jaravel, cités par la note de "
        "France Positive « Présidentielle 2027 : les trajectoires budgétaires des candidats » du 28 septembre 2026 "
        "(https://france-positive-backend.vercel.app/api/media/file/1ba0bafa-bba6-4f6f-9d36-9178a08235a0-synthese-fp-trajectoires-budgetaires.pdf). "
        "Sources consultées le 20 novembre 2026.",
    ),
)
