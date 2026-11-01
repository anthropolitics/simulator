from openfisca_core.model_api import ADD, Variable, min_

from simulator.mesures import Mesure

AGE_LIMITE = 30
PLAFOND_EN_SMIC = 4
HEURES_PAR_AN = 35 * 52  # 1 820 heures : le montant annuel du SMIC brut à temps plein


def appliquer(reforme):
    actuelle = reforme.variables["revenu_assimile_salaire"].get_formula("2025-01-01")

    class revenu_assimile_salaire(Variable):
        def formula_2025_01_01(individu, period, parameters):
            plafond = PLAFOND_EN_SMIC * parameters(period).marche_travail.salaire_minimum.smic.smic_b_horaire * HEURES_PAR_AN
            exonere = min_(individu("salaire_imposable", period, options=[ADD]), plafond)
            return actuelle(individu, period, parameters) - (individu("age", period.first_month) < AGE_LIMITE) * exonere

    reforme.update_variable(revenu_assimile_salaire)


MESURE = Mesure(
    id="exoneration_ir_moins_de_30_ans",
    titre="Exonération d'impôt sur le revenu des salaires des moins de 30 ans, jusqu'à 4 SMIC",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/22-mesures",
    citation="Exonérer d’impôt sur le revenu tous les jeunes actifs jusqu’à 30 ans pour qu’ils restent en France et fondent leur famille chez nous.",
    traduction=(
        "Mesure 7 des « 22 mesures » de la campagne de 2022, reprise par le programme des législatives de 2024 (« Supprimer l’impôt sur le revenu "
        "des jeunes de moins de 30 ans », https://rassemblementnational.fr/documents/202406-programme.pdf#page=10). Le 6 octobre 2026, en "
        "présentant sa trajectoire budgétaire, la candidate a proposé « d'exonérer les jeunes de moins de 30 ans d'impôt sur le revenu, jusqu'à "
        "quatre fois le Smic », pour 2 Md€ par an (LCP, 6 octobre 2026, "
        "https://lcp.fr/actualites/permis-de-conduire-gratuit-exoneration-d-impot-jusqu-a-30-ans-comment-le-rn-veut) ; l'Institut de l'Entreprise "
        "relève dans le dossier de presse, qui n'est pas en ligne, « l'exonération d'impôt sur le revenu des actifs de moins de trente ans jusqu'à "
        "quatre SMIC (2,0 Mds€) » "
        "(https://www.institut-entreprise.fr/wp-content/uploads/2026/10/Analyse-primaire-contre-budget-RN-Note-de-contexte-IDEP.pdf) ; sources "
        "consultées le 31 octobre 2026. Aucune source ne dit comment joue la limite de quatre SMIC. Le calcul suit le précédent des apprentis, "
        "dont le salaire est exonéré « dans la limite du montant annuel du salaire minimum de croissance » (article 81 bis du CGI) : à partir de "
        "2025, le salaire imposable d'une personne de moins de 30 ans au 1er janvier est retiré de son revenu imposable dans la limite de quatre "
        "SMIC annuels bruts (4 × 11,88 € × 1 820 heures = 86 486,40 €), et le surplus reste imposé ; il n'y a donc pas d'effet de seuil. La "
        "mesure vise les « actifs » : seuls les salaires sont exonérés, les allocations de chômage, revenus de remplacement, restent imposables. "
        "Chaque personne compte pour elle-même : dans un couple, seul le salaire du conjoint de moins de 30 ans est exonéré, et l'impôt du foyer "
        "est calculé sur le reste avec toutes ses parts. Les sources ne disent pas si le salaire exonéré reste dans le revenu fiscal de référence : le calcul l'en retire, avec "
        "le revenu imposable, ce qui joue sur les droits qui en dépendent."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # le dossier de presse du 6 octobre 2026 n'est connu que par la presse et une note de l'Institut de l'Entreprise
    hypotheses=(
        "Les effets sur l'expatriation, l'installation et l'activité des jeunes, que la mesure cherche à obtenir, ne sont pas calculés, pas plus "
        "que son financement."
    ),
)
