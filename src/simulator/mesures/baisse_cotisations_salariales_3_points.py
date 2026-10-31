from openfisca_core.model_api import Variable, min_

from simulator.mesures import Mesure

BAISSE = 0.03


def appliquer(reforme):
    actuelle = reforme.variables["cotisations_salariales"].get_formula("2025-01-01")

    class cotisations_salariales(Variable):
        def formula_2025_01_01(individu, period, parameters):
            cotisations = actuelle(individu, period, parameters)  # montant négatif
            # La baisse ne dépasse pas les cotisations dues, par exemple pour un apprenti qui en est exonéré.
            return cotisations + min_(BAISSE * individu("assiette_cotisations_sociales", period), -cotisations)

    reforme.update_variable(cotisations_salariales)


MESURE = Mesure(
    id="baisse_cotisations_salariales_3_points",
    titre="Baisse de 3 points des cotisations salariales",
    candidats=("David Lisnard",),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 35",
    citation="Baisse de 3 points des cotisations salariales",
    traduction=(
        "La source ne dit pas quelles cotisations salariales baissent. Plutôt que de choisir une caisse (retraite de base, retraite complémentaire), "
        "la variable OpenFisca cotisations_salariales est réduite, à partir du 1er janvier 2025, de 3 % de l'assiette des cotisations "
        "(assiette_cotisations_sociales, le salaire brut), sur la totalité du salaire, sans plafond. Le rapport chiffre le gain à 45 € net par mois "
        "au SMIC et à 150 € pour un cadre à 5 000 € ; cette traduction donne 54 € de salaire net en plus au SMIC (3 % de 1 801,80 €) et 150 € à "
        "5 000 € brut. La baisse ne dépasse pas les cotisations salariales dues. La CSG et la CRDS, qui sont des contributions et non des cotisations, ne changent pas. Le salaire brut et le coût du "
        "travail restent inchangés ; le salaire net et le salaire imposable augmentent."
    ),
    appliquer=appliquer,
    a_confirmer=True,
    hypotheses=(
        "Les droits à retraite ou à indemnisation attachés aux cotisations ne sont pas simulés. La façon dont la baisse de recettes des caisses "
        "serait compensée n'est pas calculée, pas plus que les effets sur l'emploi et les salaires négociés."
    ),
)
