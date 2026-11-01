from openfisca_core.model_api import Variable, min_

from simulator.mesures import Mesure

SALAIRE_BRUT_MEDIAN = 2671.81  # salaire brut mensuel qui donne le salaire net médian de la source, 2 115 €, selon engine.brut_depuis_net
BAISSE = 500 / (12 * SALAIRE_BRUT_MEDIAN)  # 1,56 % du salaire brut : 500 € nets par an au salaire médian


def appliquer(reforme):
    actuelle = reforme.variables["cotisations_salariales"].get_formula("2025-01-01")

    class cotisations_salariales(Variable):
        def formula_2025_01_01(individu, period, parameters):
            cotisations = actuelle(individu, period, parameters)  # montant négatif
            return cotisations + min_(BAISSE * individu("assiette_cotisations_sociales", period), -cotisations)

    reforme.update_variable(cotisations_salariales)


MESURE = Mesure(
    id="cotisations_salariales_500_euros_salaire_median",
    titre="Baisse des cotisations salariales : 500 € nets de plus par an au salaire médian",
    candidats=("Bruno Retailleau",),
    source="https://avecretailleau.fr/projet/mesure/rendre-30-milliards-d-euros-aux-salaries-et-aux-entreprises",
    citation=(
        "« 500 euros nets de plus par an pour tous les salariés, tout de suite. » Baisser les cotisations de 30 milliards d'euros par an. La moitié "
        "revient directement aux salariés, soit environ 500 euros nets par an au salaire médian, sans qu'ils aient rien à changer à leur "
        "organisation. L'autre moitié revient aux entreprises, en baisse durable du coût du travail dès la première heure travaillée."
    ),
    traduction=(
        "Mesure n° 24 du site de campagne, mise à jour le 24 septembre 2026 (consultée le 31 octobre 2026). La source ne dit pas quelles cotisations "
        "baissent ni comment le gain varie avec le salaire ; elle donne 500 € au salaire médian, et la mesure n° 25 du même site fixe ce salaire à "
        "2 115 € nets par mois. Le calcul lit une baisse proportionnelle, comme celle d'un taux de cotisation : la variable OpenFisca "
        "cotisations_salariales est réduite, à partir du 1er janvier 2025, de 1,56 % de l'assiette des cotisations (le salaire brut), sur tout le "
        "salaire, ce qui donne 500 € nets par an à 2 671,81 € brut par mois, le brut de 2 115 € nets. Un salarié au SMIC gagne 337 € par an, un "
        "salarié à 5 000 € brut 936 €. Le titre « pour tous les salariés » permettrait aussi de lire 500 € pour chacun, mais ce ne serait plus une "
        "baisse de cotisation proportionnelle au salaire, et la source chiffre le gain au salaire médian. La baisse ne dépasse pas les cotisations salariales dues. La "
        "CSG et la CRDS ne changent pas ; le salaire net et le salaire imposable augmentent. La moitié qui va aux entreprises n'est pas simulée."
    ),
    appliquer=appliquer,
    hypotheses=(
        "La baisse des cotisations patronales, l'autre moitié des 30 milliards d'euros, réduit le coût du travail sans changer mécaniquement le "
        "salaire brut ni le salaire net. Les droits à retraite attachés aux cotisations ne sont pas simulés. Le financement (réforme de l'assurance "
        "chômage, compte social unique, lutte contre la fraude) et les effets sur l'emploi ne sont pas calculés."
    ),
)
