from openfisca_core.model_api import Variable, max_, min_
from openfisca_core.taxscales import MarginalRateTaxScale
from openfisca_france.model.prelevements_obligatoires.prelevements_sociaux.contributions_sociales.base import montant_csg_crds

from simulator.mesures import Mesure

# Barème marginal par personne : seuil mensuel de l'assiette de la CSG, taux.
BAREME = MarginalRateTaxScale(name="csg_14_tranches")
for seuil, taux in (
    (0, 0.06),
    (500, 0.065),
    (1_000, 0.0675),
    (1_400, 0.075),
    (1_800, 0.08),
    (2_200, 0.085),
    (2_700, 0.092),
    (3_400, 0.125),
    (4_200, 0.1364),
    (4_990, 0.15),
    (6_000, 0.16),
    (8_000, 0.17),
    (15_000, 0.18),
    (33_000, 0.19),
):
    BAREME.add_bracket(seuil, taux)


def csg_et_plafond_deductible(individu, period, parameters):
    """CSG du barème sur le salaire du mois, et part déductible d'aujourd'hui (6,8 % de l'assiette)."""
    csg = parameters(period).prelevements_sociaux.contributions_sociales.csg
    assiette = -montant_csg_crds(
        base_avec_abattement=individu("assiette_csg_abattue", period),
        base_sans_abattement=individu("assiette_csg_non_abattue", period),
        abattement_parameter=csg.activite.abattement,
        law_node=1,
        plafond_securite_sociale=individu("plafond_securite_sociale", period),
    )
    return BAREME.calc(assiette), csg.activite.deductible * assiette


def appliquer(reforme):
    class csg_deductible_salaire(Variable):
        def formula_2025_01_01(individu, period, parameters):
            csg, plafond = csg_et_plafond_deductible(individu, period, parameters)
            return -min_(csg, plafond)

    class csg_imposable_salaire(Variable):
        def formula_2025_01_01(individu, period, parameters):
            csg, plafond = csg_et_plafond_deductible(individu, period, parameters)
            return -max_(csg - plafond, 0)

    reforme.update_variable(csg_deductible_salaire)
    reforme.update_variable(csg_imposable_salaire)


MESURE = Mesure(
    id="csg_progressive_14_tranches",
    titre="CSG progressive à 14 tranches sur les salaires",
    candidats=("Jean-Luc Mélenchon",),
    source="https://desintox.lafranceinsoumise.fr/vous-voulez-augmenter-les-impots/",
    citation=(
        "La Contribution sociale généralisée (CSG) est rendue progressive avec 14 tranches également. Actuellement, chaque salarié paie la CSG "
        "au même taux (9,2 %), directement sur son salaire : un salarié au SMIC paie donc la même proportion qu'un millionnaire."
    ),
    traduction=(
        "Le programme (« Rendre la CSG progressive ») ne publie pas le barème. Il est lu dans le code du simulateur impots.lafranceinsoumise.fr, "
        "vers lequel renvoie la page citée (mise à jour le 12 mars 2026) et qui porte encore le titre « Nouveau Front populaire » : barème "
        "marginal par personne, appliqué à l'assiette actuelle de la CSG sur les salaires (98,25 % du brut jusqu'à quatre plafonds de la sécurité "
        "sociale), avec des seuils mensuels de 0, 500, 1 000, 1 400, 1 800, 2 200, 2 700, 3 400, 4 200, 4 990, 6 000, 8 000, 15 000 et 33 000 € "
        "et des taux de 6 ; 6,5 ; 6,75 ; 7,5 ; 8 ; 8,5 ; 9,2 ; 12,5 ; 13,64 ; 15 ; 16 ; 17 ; 18 et 19 %. Ce barème remplace, à partir du "
        "1er janvier 2025, le taux de 9,2 % de la CSG sur les salaires (variables csg_deductible_salaire et csg_imposable_salaire). La source ne "
        "dit pas quelle part reste déductible de l'impôt sur le revenu : la part déductible reste celle d'aujourd'hui, 6,8 % de l'assiette, sans "
        "dépasser la CSG due, et le reste est imposable. La source ne donne de barème que pour les salaires : la CSG sur les retraites, les "
        "allocations chômage et les revenus du capital, ainsi que la CRDS, ne changent pas."
    ),
    appliquer=appliquer,
    a_confirmer=True,
    hypotheses=(
        "Le calcul ne tient pas compte des effets sur les salaires négociés, l'offre de travail ou la répartition des rémunérations entre "
        "salaire et autres formes de revenu. L'effet sur les recettes de la sécurité sociale n'est pas calculé."
    ),
)
