from simulator.mesures import Mesure
from simulator.mesures.smic_1600_net import smic_a

# brut_depuis_net(2200) sur la loi 2025 : salaire brut mensuel d'un salarié du privé non cadre, seul, à temps plein, qui touche 2 200 € net.
SMIC_BRUT_MENSUEL = 2779.18

MESURE = Mesure(
    id="smic_2200_net",
    titre="Salaire minimum à 2 200 € net par mois",
    candidats=("Nathalie Arthaud",),
    source="https://www.lutte-ouvriere.org/medias/document/fichiers/2026/06/brochure-ete-2026.pdf",
    citation=(
        "« Quand nous discutons entre nous de ce qu'il faut pour vivre, tout le monde convient qu'il faudrait 300, 400, 500 euros d'augmentation. "
        "Aujourd'hui il faut gagner au moins 2 200 euros net par mois pour s'en sortir. Eh bien voilà ce que nous devons exiger ! » (p. 9)"
    ),
    traduction=(
        "Source : brochure « Nathalie Arthaud, Présidentielle 2027 », discours de la fête annuelle de Lutte ouvrière de mai 2026, diffusée comme "
        "brochure de campagne depuis le 25 août 2026 (https://www.lutte-ouvriere.org/portail/breves/brochure-campagne-196541.html, consulté le "
        "31 octobre 2026) ; la candidate a repris le montant à Saint-Fons (« 2 200 euros net pour vivre, c'est le minimum décent », Lyon Bondy "
        "Blog, 30 septembre 2026, https://lyonbondyblog.fr/LBB/a-saint-fons-nathalie-arthaud-veut-remettre-le-monde-du-travail-en-ordre-de-bataille/). "
        "Le rapport « Présidentielle 2027 — Analyse des programmes » (p. 57) ne parle que d'une « hausse des salaires ». La revendication est lue "
        "comme un salaire minimum mensuel net pour un temps plein de 35 heures par semaine (151,67 heures par mois). Sur la loi 2025, un salarié du "
        "privé non cadre, seul, à temps plein, touche 2 200 € net pour 2 779,18 € brut. À partir du 1er janvier 2025, le paramètre "
        "marche_travail.salaire_minimum.smic.smic_b_horaire passe de 11,88 € à 2 779,18 / 151,67 = 18,32 € et smic_b_mensuel de 1 801,80 € à "
        "2 779,18 €. Les dispositifs de la loi actuelle qui se réfèrent au SMIC (allègements de cotisations patronales, prime d'activité, "
        "apprentissage, etc.) suivent le nouveau montant. Un salaire déclaré au SMIC suit le nouveau montant ; un salaire à temps plein qui passe "
        "sous le nouveau SMIC y est relevé ; les autres salaires restent fixes. L'« augmentation massive des salaires, des allocations et des "
        "pensions » et leur indexation sur les prix, que la brochure demande aussi sans montant, ne sont pas simulées."
    ),
    appliquer=smic_a(SMIC_BRUT_MENSUEL),
    hypotheses=(
        "Les salaires au-dessus du nouveau minimum sont tenus fixes ; la hausse générale des salaires que Lutte ouvrière réclame, et les effets "
        "sur l'emploi, les heures travaillées et les prix, ne sont pas calculés."
    ),
)
