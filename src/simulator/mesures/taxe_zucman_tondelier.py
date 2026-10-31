from simulator.mesures import Mesure
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
)
