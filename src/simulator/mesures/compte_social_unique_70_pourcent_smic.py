from openfisca_core.model_api import ADD, YEAR, Variable, max_
from openfisca_france.entities import Famille

from simulator.mesures import Mesure, ajouter_prestation, vers_famille
from simulator.mesures.revenu_familial import revenu_familial
from simulator.mesures.revenu_incitation_activite import revenu_incitation_activite

PLAFOND = 0.7
SMIC_NET_MENSUEL = 1426.30  # SMIC net à temps plein en 2025, pour 1 801,80 € brut


class plafonnement_compte_social_unique(Variable):
    value_type = float
    entity = Famille
    definition_period = YEAR
    label = "Compte social unique : aides non contributives au-delà de 70 % du SMIC net par adulte, retenues (montant négatif)"

    def formula(famille, period):
        # Hors handicap (AEEH, AAH), vieillesse (minimum vieillesse) et chômage (ASS).
        familiales = famille("prestations_familiales", period) - famille("aeeh", period, options=[ADD]) - famille("aes", period, options=[ADD])
        minima = famille("minima_sociaux", period) - famille("minimum_vieillesse", period, options=[ADD])
        minima -= famille.sum(sum(famille.members(v, period, options=[ADD]) for v in ("aah", "caah", "ass")))
        aides = familiales + minima + famille("aides_logement", period)
        # Les aides que créent les autres mesures du candidat entrent dans le compte quand elles sont simulées avec celle-ci.
        simulees = famille.simulation.tax_benefit_system.variables
        aides += sum(vers_famille(famille, v, period) for v in (revenu_familial, revenu_incitation_activite) if v.__name__ in simulees)
        plafond = PLAFOND * SMIC_NET_MENSUEL * 12 * famille.nb_persons(Famille.PARENT)
        return -max_(aides - plafond, 0)


MESURE = Mesure(
    id="compte_social_unique_70_pourcent_smic",
    titre="Compte social unique : aides sociales plafonnées à 70 % du SMIC net par adulte",
    candidats=("Bruno Retailleau",),
    source="https://avecretailleau.fr/projet/mesure/plafonner-les-aides-sociales-a-70-du-smic",
    citation=(
        "Créer un Compte social unique, sur le modèle du compte fiscal : chaque adulte disposera d'un compte retraçant toutes les aides non "
        "contributives qu'il perçoit, quelle qu'en soit l'origine. Un plafond national s'appliquera ensuite : le total ne pourra pas dépasser 70 % "
        "du SMIC net par adulte, hors handicap, dépendance et vieillesse. Ni la retraite ni le chômage n'entrent dans ce calcul."
    ),
    traduction=(
        "Mesure n° 28 du site de campagne, mise à jour le 11 septembre 2026 (consultée le 31 octobre 2026). Le compte réunit les aides non "
        "contributives que calcule OpenFisca : prestations familiales, sauf l'allocation d'éducation de l'enfant handicapé, minima sociaux, sauf "
        "l'allocation aux adultes handicapés et son complément, le minimum vieillesse et l'allocation de solidarité spécifique, rangée avec le "
        "chômage, et aides au logement ; le revenu familial et le revenu d'incitation à l'activité du candidat s'y ajoutent quand ils sont simulés "
        "avec cette mesure. Le plafond vaut 70 % du SMIC net à temps plein de 2025 (1 426,30 € par mois, soit 998,41 €) par adulte de la famille, "
        "enfants exclus, comme dans l'exemple de la source qui raisonne « par adulte du foyer ». Il s'apprécie sur l'année : le dépassement est "
        "retenu sur le total, comme une prestation négative, sans dire quelle aide baisse. Les gratuités, tarifs sociaux et aides facultatives "
        "des collectivités, que la source compte aussi, ne sont pas dans OpenFisca : seules les aides légales sont plafonnées. L'exemple de la "
        "source (couple sans emploi, deux enfants, 1 706 € d'aides légales et 2 375 € avec les aides locales, ramenés à 1 865 €) ne se reproduit "
        "pas avec un plafond de 70 % par adulte, qui donne 1 997 € : le calcul suit la règle écrite, pas l'exemple."
    ),
    appliquer=lambda reforme: ajouter_prestation(reforme, plafonnement_compte_social_unique),
    hypotheses=(
        "Le recensement des aides, dont la source attend l'essentiel des 10 milliards d'euros d'économies avec la lutte contre la fraude, n'a pas "
        "d'effet sur un ménage qui déclare ses revenus exactement. Les aides des collectivités et les tarifs sociaux ne sont pas simulés. Les "
        "effets sur l'emploi et le recours aux aides ne sont pas calculés."
    ),
)
