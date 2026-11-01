from simulator.mesures import Mesure
from simulator.mesures.smic_1600_net import smic_a

# brut_depuis_net(1700) sur la loi 2025 : salaire brut mensuel d'un salarié du privé non cadre, seul, à temps plein, qui touche 1 700 € net.
SMIC_BRUT_MENSUEL = 2147.56

MESURE = Mesure(
    id="smic_1700_net",
    titre="SMIC à 1 700 € net par mois",
    candidats=("Jean-Luc Mélenchon", "Raphaël Glucksmann"),
    source="https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf",
    citation=(
        "Jean-Luc Mélenchon : « Ces mesures d'urgence sociale doivent être complétées par une hausse du SMIC à 1 700 euros net. » (p. 9) ; "
        "Raphaël Glucksmann : « Porter le SMIC à 1 700 euros net par mois » (« Plan de sortie de crise », p. 2)."
    ),
    traduction=(
        "Source : « Comment nous allons remettre de l'ordre dans les comptes publics », La France insoumise, document de la campagne présidentielle "
        "2027 daté du 14 octobre 2026 (consulté le 31 octobre 2026). Le rapport « Présidentielle 2027 — Analyse des programmes » (28 octobre 2026, "
        "p. 19) écrit encore « SMIC à 1 600 € net » : le document du candidat prime. Pour Raphaël Glucksmann : « Plan de sortie de crise », document de "
        "sa campagne daté du 22 octobre 2026, publié sans programme sur glucks2027.fr et repris sur "
        "https://www.wikiglucksmann.fr/docs/glucks2027-plan-sortie-de-crise-2026-10-22.pdf (consulté le 1er novembre 2026), confirmé par Public Sénat "
        "le 30 octobre 2026 ; il remplace les 1 600 € net « en deux ans » de son projet « Acte un » de juin 2025, que reprend le rapport (p. 27). Le montant visé est un SMIC mensuel net pour 35 heures par "
        "semaine (151,67 heures par mois). Sur la loi 2025, un salarié du privé non cadre, seul, à temps plein, touche 1 700 € net pour 2 147,56 € "
        "brut. À partir du 1er janvier 2025, le paramètre marche_travail.salaire_minimum.smic.smic_b_horaire passe de 11,88 € à "
        "2 147,56 / 151,67 = 14,16 € et smic_b_mensuel de 1 801,80 € à 2 147,56 €. Les dispositifs de la loi actuelle qui se réfèrent au SMIC "
        "(allègements de cotisations patronales, prime d'activité, apprentissage, etc.) suivent le nouveau montant. Un salaire déclaré au SMIC suit "
        "le nouveau montant ; un salaire à temps plein qui passe sous le nouveau SMIC y est relevé, comme la loi l'impose ; les autres salaires "
        "restent fixes."
    ),
    appliquer=smic_a(SMIC_BRUT_MENSUEL),
    hypotheses=(
        "Les salaires au-dessus du SMIC sont tenus fixes : la conférence sur les salaires et l'indexation générale des salaires sur l'inflation, "
        "que le document annonce avec la hausse, ne sont pas calculées, pas plus que les effets sur l'emploi, les heures travaillées et les prix."
    ),
)
