from simulator.mesures import Cout, Mesure
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
    candidats=("Fabien Roussel", "François Ruffin"),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 45 et 48",
    citation=("Fabien Roussel (p. 45) : « SMIC à 1 600 € net » ; François Ruffin (p. 48) : « SMIC à 1 600 € »."),
    traduction=(
        "Le montant visé est un SMIC mensuel net pour 35 heures par semaine (151,67 heures par mois). Sur la loi 2025, un salarié du privé non cadre, "
        "seul, à temps plein, touche 1 600 € net pour 2 021,22 € brut. À partir du 1er janvier 2025, le paramètre "
        "marche_travail.salaire_minimum.smic.smic_b_horaire passe de 11,88 € à 2 021,22 / 151,67 = 13,33 € et smic_b_mensuel de 1 801,80 € à "
        "2 021,22 €. Pour François Ruffin, le "
        "rapport n'indique pas net ou brut ; 1 600 € brut étant inférieur au SMIC brut de 2025, le montant est lu comme net. Les dispositifs de la "
        "loi actuelle qui se réfèrent au SMIC (allègements de cotisations patronales, prime d'activité, apprentissage, etc.) suivent le nouveau "
        "montant. Le rapport prête aussi ce montant à Jean-Luc Mélenchon et à Raphaël Glucksmann (« en deux ans »), dont les documents de campagne de 2027 portent 1 700 € net : voir smic_1700_net. Un salaire déclaré au SMIC suit le nouveau montant ; un salaire à temps plein qui passe sous le nouveau SMIC y est relevé, comme la loi l'impose ; les autres salaires restent fixes."
    ),
    appliquer=smic_a(SMIC_BRUT_MENSUEL),
    a_confirmer=True,
    hypotheses=(
        "Les salaires au-dessus du SMIC sont tenus fixes : leur éventuelle revalorisation par diffusion de la hausse (grilles de branche) n'est pas "
        "calculée, pas plus que les effets sur l'emploi, les heures travaillées et les prix."
    ),
    cout=Cout(
        1.6,
        21,
        "1,6 Md€ pour un SMIC à 1 600 € net selon le contre-budget 2026 de La France insoumise, qui ne dit pas ce qu'il compte "
        "(https://lafranceinsoumise.fr/wp-content/uploads/2025/10/Budget-2026_LFI_web_pages.pdf, p. 40) ; de l'ordre de 3,8 Md€ selon la Fondation "
        "Jean-Jaurès "
        "(https://www.jean-jaures.org/publication/pour-une-hausse-progressive-du-smic-jusqua-1600-euros-accompagnee-dune-reduction-des-exonerations-sociales/) "
        "; 19 Md€, de 17 à 21, selon l'Institut Montaigne en 2024 : allègements de cotisations sur les bas salaires et salaires publics, moins les "
        "prélèvements en plus (https://www.institutmontaigne.org/legislatives-2024/nouveau-front-populaire/augmenter-le-smic-a-1600-e-net). "
        "Chiffrages de 2024, pour une hausse de 14,4 % du SMIC d'alors ; elle serait moindre depuis celui de 2025. Ni Fabien Roussel ni François "
        "Ruffin ne chiffrent la mesure. Sources consultées le 20 novembre 2026.",
    ),
)
