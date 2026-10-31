from simulator.mesures import Mesure
from simulator.persona import HEURES_TEMPS_PLEIN

# brut_depuis_net(1600) sur la loi 2025 : salaire brut mensuel d'un salarié du privé non cadre, seul, à temps plein, qui touche 1 600 € net.
SMIC_BRUT_MENSUEL = 2021.22


def smic_a(brut_mensuel: float):
    """Réforme qui porte le SMIC brut à temps plein à ce montant mensuel à partir du 1er janvier 2025."""

    def appliquer(reforme):
        def modifier(parametres):
            smic = parametres.marche_travail.salaire_minimum.smic
            smic.smic_b_horaire.update(start="2025-01-01", value=brut_mensuel / HEURES_TEMPS_PLEIN)
            smic.smic_b_mensuel.update(start="2025-01-01", value=brut_mensuel)
            return parametres

        reforme.modify_parameters(modifier_function=modifier)

    return appliquer


MESURE = Mesure(
    id="smic_1600_net",
    titre="SMIC à 1 600 € net par mois",
    candidats=("Raphaël Glucksmann", "Fabien Roussel", "François Ruffin"),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 27, 45 et 48",
    citation=(
        "Raphaël Glucksmann (p. 27) : « SMIC à 1 600 € net en deux ans » ; "
        "Fabien Roussel (p. 45) : « SMIC à 1 600 € net » ; François Ruffin (p. 48) : « SMIC à 1 600 € »."
    ),
    traduction=(
        "Le montant visé est un SMIC mensuel net pour 35 heures par semaine (151,67 heures par mois). Sur la loi 2025, un salarié du privé non cadre, "
        "seul, à temps plein, touche 1 600 € net pour 2 021,22 € brut. À partir du 1er janvier 2025, le paramètre "
        "marche_travail.salaire_minimum.smic.smic_b_horaire passe de 11,88 € à 2 021,22 / 151,67 = 13,33 € et smic_b_mensuel de 1 801,80 € à "
        "2 021,22 €. Le calendrier (en deux ans pour Raphaël Glucksmann) n'est pas simulé : la cible s'applique d'emblée. Pour François Ruffin, le "
        "rapport n'indique pas net ou brut ; 1 600 € brut étant inférieur au SMIC brut de 2025, le montant est lu comme net. Les dispositifs de la "
        "loi actuelle qui se réfèrent au SMIC (allègements de cotisations patronales, prime d'activité, apprentissage, etc.) suivent le nouveau "
        "montant. Le rapport prête aussi ce montant à Jean-Luc Mélenchon, dont le programme de 2027 porte 1 700 € net : voir smic_1700_net. Un salaire déclaré au SMIC suit le nouveau montant ; un salaire à temps plein qui passe sous le nouveau SMIC y est relevé, comme la loi l'impose ; les autres salaires restent fixes."
    ),
    appliquer=smic_a(SMIC_BRUT_MENSUEL),
    a_confirmer=True,
    hypotheses=(
        "Les salaires au-dessus du SMIC sont tenus fixes : leur éventuelle revalorisation par diffusion de la hausse (grilles de branche) n'est pas "
        "calculée, pas plus que les effets sur l'emploi, les heures travaillées et les prix."
    ),
)
