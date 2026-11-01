from simulator.mesures import Mesure
from simulator.mesures.plafond_quotient_familial_3000 import plafond_a

PLAFOND = 2 * 1807  # le double du plafond général par demi-part de la loi 2025

MESURE = Mesure(
    id="plafond_quotient_familial_double",
    titre="Plafond du quotient familial doublé, de 1 807 € à 3 614 € par demi-part",
    candidats=("Éric Zemmour",),
    source="https://www.institutmontaigne.org/presidentielle-2022/eric-zemmour/doubler-le-quotient-familial",
    citation="« Je veux rétablir l'universalité de la politique familiale et doubler le quotient familial. »",
    traduction=(
        "Mesure de la campagne de 2022 : le programme d'alors (programme.zemmour2022.fr, redirigé vers programme.ericzemmour.fr) refuse l'accès "
        "(erreur 403) et Reconquête n'a publié aucun programme pour 2027. La fiche de l'Institut Montaigne cite le candidat "
        "(https://twitter.com/ZemmourEric/status/1471032671195353089) et lit la mesure comme le doublement du plafond de l'avantage en impôt par "
        "demi-part, alors de 1 570 €, à 3 140 € ; le rapport « Présidentielle 2027 — Analyse des programmes » (28 octobre 2026, p. 51) cite la "
        "« fiscalité familiale » parmi ses mesures, sans détail ; sources consultées le 31 octobre 2026. Un montant de 3 000 €, que donne la presse "
        "(« de 1.592 à 3.000 euros », https://www.toutsurmesfinances.com/argent/a/eric-zemmour-programme, mis à jour le 27 octobre 2026), ne se retrouve pas dans les paroles du candidat : le calcul double le plafond de la "
        "loi simulée. À partir du 1er janvier 2025, le plafond général par demi-part au-delà des parts des adultes (article 197 du CGI) passe "
        "de 1 807 € à 3 614 €. Les plafonds particuliers (première part d'un parent isolé, demi-part des personnes seules ayant élevé un enfant) "
        "ne changent pas. Seuls les foyers dont l'avantage dû aux enfants dépasse le plafond actuel y gagnent, au plus 1 807 € par demi-part. "
        "Le retour à l'universalité des allocations familiales, l'autre moitié de la phrase, n'est pas dans cette mesure."
    ),
    appliquer=plafond_a(PLAFOND),
    a_confirmer=True,  # mesure de la campagne de 2022, connue par une source secondaire ; aucun programme 2027
    hypotheses="Les effets sur la natalité et sur l'activité des parents ne sont pas calculés, pas plus que le financement de la mesure.",
)
