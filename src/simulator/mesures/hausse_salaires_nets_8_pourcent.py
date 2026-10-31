from openfisca_core.model_api import Variable, min_

from simulator.mesures import Mesure

HAUSSE_DU_NET = 0.08
PLAFOND_EN_SMIC = 3


def appliquer(reforme):
    actuelle = reforme.variables["cotisations_salariales"].get_formula("2025-01-01")

    class cotisations_salariales(Variable):
        def formula_2025_01_01(individu, period, parameters):
            cotisations = actuelle(individu, period, parameters)  # montant négatif, comme la CSG et la CRDS
            assiette = individu("assiette_cotisations_sociales", period)
            contributions = individu("csg_deductible_salaire", period) + individu("csg_imposable_salaire", period) + individu("crds_salaire", period)
            concerne = assiette <= PLAFOND_EN_SMIC * individu("smic_proratise", period)
            return cotisations + concerne * min_(HAUSSE_DU_NET * (assiette + cotisations + contributions), -cotisations)

    reforme.update_variable(cotisations_salariales)


MESURE = Mesure(
    id="hausse_salaires_nets_8_pourcent",
    titre="Hausse de 8 % des salaires nets jusqu'à 3 SMIC, par une baisse des cotisations salariales",
    candidats=("Nicolas Dupont-Aignan",),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 54",
    citation="Hausse des salaires de 8 % jusqu'à 3 SMIC sans coût pour l'employeur",
    traduction=(
        "Le projet de Debout la France pour 2022 précise le mécanisme : « Hausse de salaire de 8% (équivalent d’un 13e mois) pour tous les "
        "salariés jusqu’à 3 SMIC et pour les indépendants par une baisse des charges salariales » (100 décisions pour la France, décision 18, "
        "https://www.debout-la-france.fr/wp-content/uploads/2022/07/100-Decisions-pour-la-France_VFIN.pdf) et « Baisser les charges sociales "
        "salariales pour augmenter les salaires nets de 8% » (https://www.debout-la-france.fr/wp-content/uploads/2022/07/Le-chiffrage-du-projet_VFIN.pdf). "
        "Le salaire brut, et donc le coût du travail, ne change pas : à partir du 1er janvier 2025, la variable OpenFisca cotisations_salariales est "
        "réduite de 8 % du salaire net (brut moins cotisations salariales, CSG et CRDS) pour un salarié dont l'assiette des cotisations ne dépasse "
        "pas 3 SMIC proratisés (smic_proratise). La source ne prévoit pas de sortie progressive : au-delà de 3 SMIC, rien ne change. La baisse ne "
        "dépasse pas les cotisations salariales dues. Le volet indépendants n'est pas simulé, le persona n'ayant que des salaires."
    ),
    appliquer=appliquer,
    a_confirmer=True,
    hypotheses=(
        "Les droits à retraite attachés aux cotisations ne sont pas simulés. Le financement annoncé (lutte contre les gaspillages et les fraudes) "
        "n'est pas calculé, pas plus que les effets sur l'emploi et les salaires négociés."
    ),
)
