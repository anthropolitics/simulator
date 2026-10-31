from simulator.mesures import Mesure
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
)
