from simulator.mesures import Cout, Mesure
from simulator.persona import HEURES_TEMPS_PLEIN

SMIC_BRUT_MENSUEL = 2000


def appliquer(reforme):
    def modifier(parametres):
        smic = parametres.marche_travail.salaire_minimum.smic
        smic.smic_b_horaire.update(start="2025-01-01", value=SMIC_BRUT_MENSUEL / HEURES_TEMPS_PLEIN)
        smic.smic_b_mensuel.update(start="2025-01-01", value=SMIC_BRUT_MENSUEL)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="smic_2000_brut",
    titre="SMIC à 2 000 € brut par mois",
    candidats=("Marine Tondelier",),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 42",
    citation="SMIC à 2 000 € brut dès 2027",
    traduction=(
        "Le montant visé est un SMIC mensuel brut pour 35 heures par semaine (151,67 heures par mois). À partir du 1er janvier 2025, le paramètre "
        "marche_travail.salaire_minimum.smic.smic_b_horaire passe de 11,88 € à 2 000 / 151,67 = 13,19 € et smic_b_mensuel de 1 801,80 € à 2 000 €. "
        "La date annoncée (2027) n'est pas simulée : le montant s'applique à la loi 2025. Les dispositifs de la loi actuelle qui se réfèrent au SMIC "
        "(allègements de cotisations patronales, prime d'activité, apprentissage, etc.) suivent le nouveau montant. Un salaire déclaré au SMIC suit le nouveau montant ; un salaire à temps plein qui passe sous le nouveau SMIC y est relevé, comme la loi l'impose ; les autres salaires restent fixes."
    ),
    appliquer=appliquer,
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
        "Chiffrages de 2024, pour une hausse de 14,4 % du SMIC d'alors ; elle serait moindre depuis celui de 2025. La candidate ne chiffre pas la "
        "mesure ; 2 000 € brut valaient 1 600 € net en 2024. Sources consultées le 20 novembre 2026.",
    ),
)
