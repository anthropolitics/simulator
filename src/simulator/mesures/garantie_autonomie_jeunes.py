from openfisca_core.model_api import YEAR, Variable, max_
from openfisca_france.entities import Famille

from simulator.mesures import Mesure, ajouter_prestation

SEUIL_PAUVRETE = 1337  # par mois, pour une personne seule
AGE_MINIMUM, AGE_MAXIMUM = 18, 24


class garantie_autonomie(Variable):
    value_type = float
    entity = Famille
    definition_period = YEAR
    label = "Garantie d'autonomie des jeunes : complément du revenu du ménage jusqu'au seuil de pauvreté"

    def formula(famille, period):
        individu = famille.members
        age = individu("age", period.first_month)
        jeune = famille.any((age >= AGE_MINIMUM) * (age <= AGE_MAXIMUM), role=Famille.PARENT)
        # Revenu disponible du ménage hors garantie, poste par poste comme OpenFisca le somme : le lire en entier ferait une boucle.
        revenus = famille.sum(individu("revenus_nets_du_travail", period) + individu("pensions_nettes", period) + individu("revenus_nets_du_capital", period))
        prestations = famille("prestations_familiales", period) + famille("minima_sociaux", period) + famille("aides_logement", period)
        menage = famille.demandeur.menage
        revenu = revenus + prestations + menage("impots_directs", period)  # impôts négatifs
        return jeune * max_(12 * SEUIL_PAUVRETE * menage("unites_consommation", period) - revenu, 0)


def appliquer(reforme):
    ajouter_prestation(reforme, garantie_autonomie)


MESURE = Mesure(
    id="garantie_autonomie_jeunes",
    titre="Garantie d'autonomie : aucun jeune de 18 à 24 ans sous le seuil de pauvreté (1 337 € par mois pour une personne seule)",
    candidats=("Jean-Luc Mélenchon",),
    source="https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf",
    citation=(
        "« Nous proposons d'avancer immédiatement vers la garantie d'autonomie pour les jeunes, qui financera leur réussite durant les études et "
        "la formation. [...] Son principe : plus aucun jeune ne doit vivre sous le seuil de pauvreté, fixé à 1 337 euros par mois, ce qui coûtera "
        "9,5 milliards d'euros. » (p. 8) ; « Créer une garantie d'autonomie pour tous les jeunes détaché·es du foyer fiscal de leurs parents afin "
        "qu'aucun·e ne vive en dessous du seuil de pauvreté (1 337 euros pour une personne seule) » (plan pour l'enseignement supérieur, p. 13)"
    ),
    traduction=(
        "Sources : « Comment nous allons remettre de l'ordre dans les comptes publics », La France insoumise, 14 octobre 2026, et « Comment nous "
        "allons refonder l'enseignement supérieur, la recherche et la formation continue », octobre 2026 "
        "(https://melenchon2027.fr/wp-content/uploads/2026/10/plan_ESR_lowres.pdf), consultés le 31 octobre 2026. Aucun des deux ne donne de "
        "limite d'âge : la garantie vise les 18 à 24 ans, la tranche que le RSA exclut avant 25 ans, comme la garantie d'autonomie « pour les "
        "18-25 ans » du programme de 2022, alors limitée à trois ans et réservée aux jeunes en formation qualifiante (Institut Montaigne, "
        "https://www.institutmontaigne.org/presidentielle-2022/jean-luc-melenchon/creer-une-garantie-dautonomie-de-trois-ans-sous-reserve-dune-formation-qualifiante-et-sous-conditions-de-ressources-pour-les-18-25-ans/), "
        "et celle du programme du Nouveau Front populaire de 2024, « accessible dès 18 ans pour les personnes indépendantes fiscalement ». Le plan "
        "de 2026 l'ouvre à « tous les jeunes » détachés du foyer fiscal de leurs parents, sans condition d'études ni de durée : aucune n'est "
        "exigée. Un adulte du persona déclare ses propres revenus, il est donc détaché ; un enfant à charge ne l'est pas et n'y a pas droit. Le "
        "seuil de pauvreté se mesure sur le niveau de vie, revenu disponible du ménage par unité de consommation, et le plan donne 1 337 € « pour "
        "une personne seule » : la garantie, versée à la famille dont un parent a de 18 à 24 ans, complète son revenu disponible annuel jusqu'à "
        "12 × 1 337 = 16 044 € par unité de consommation (échelle de l'Insee : 1 pour le premier adulte, 0,5 par autre personne de 14 ans ou "
        "plus, 0,3 par enfant plus jeune), soit 16 044 € pour une personne seule et 24 066 € pour un couple sans enfant. Le revenu complété est "
        "celui de la loi 2025, prestations comprises (prime d'activité, aides au logement, prestations familiales), impôts déduits. La garantie "
        "n'est pas imposable et ne compte pas dans les ressources des autres prestations, le document n'en disant rien. La somme se calcule sur "
        "l'année, à partir du 1er janvier 2025."
    ),
    appliquer=appliquer,
    hypotheses=(
        "Le recours est supposé complet. Les effets sur l'emploi des jeunes, la poursuite d'études et la décohabitation, qui change le nombre de "
        "jeunes détachés du foyer de leurs parents, ne sont pas calculés, pas plus que le financement."
    ),
)
