from simulator.mesures import Mesure
from simulator.persona import ANNEE, HEURES_TEMPS_PLEIN

PART_DU_SMIC_NET = 0.5
# Cotisations et contributions salariales sur un SMIC : vieillesse 6,90 % et 0,40 %, Agirc-Arrco 3,15 %, CEG 0,86 %, CSG et CRDS 9,70 % sur 98,25 % du brut.
TAUX_SALARIAL_SMIC = 0.069 + 0.004 + 0.0315 + 0.0086 + 0.097 * 0.9825


def montant(smic_brut_horaire: float) -> float:
    return PART_DU_SMIC_NET * smic_brut_horaire * HEURES_TEMPS_PLEIN * (1 - TAUX_SALARIAL_SMIC)


def appliquer(reforme):
    def modifier(parametres):
        debut = f"{ANNEE}-01-01"
        # shortcut: le SMIC lu est celui des paramètres au moment où la mesure s'applique ; une mesure sur le SMIC appliquée après elle n'est pas suivie.
        smic = parametres.marche_travail.salaire_minimum.smic.smic_b_horaire(debut)
        parametres.prestations_sociales.solidarite_insertion.minima_sociaux.rsa.rsa_m.montant_de_base_du_rsa.update(start=debut, value=round(montant(smic), 2))
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="garantie_autonomie_50_pourcent_smic",
    titre="Garantie d'autonomie à la place du RSA, portée à 50 % du SMIC net",
    candidats=("Marine Tondelier",),
    source="https://lesecologistes.fr/pages/6ImK65GKUnvibm33WGkjkj/projet-2027",
    citation=(
        "Créer une garantie d'autonomie qui respecte la dignité et les droits des personnes allocataires […] en remplacement du Revenu de "
        "Solidarité Active (RSA) […] Augmenter son montant à 50 % du Smic net […] En finir avec la logique de stigmatisation en supprimant "
        "la contrepartie de 15 heures d'activités hebdomadaires."
    ),
    traduction=(
        "Programme « Pour une prospérité écologique » (13 juillet 2026, p. 119), cité par https://monvote2027.fr/candidat/tondelier (consulté le "
        "31 octobre 2026) ; la page des Écologistes n'a pas pu être lue (accès refusé). À partir du 1er janvier 2025, le montant forfaitaire du "
        "RSA pour une personne seule (paramètre prestations_sociales.solidarite_insertion.minima_sociaux.rsa.rsa_m.montant_de_base_du_rsa, "
        "635,71 € jusqu'en mars 2025 puis 646,52 €) devient 50 % du SMIC net mensuel à temps plein : 11,88 € brut de l'heure × 151,67 heures = "
        "1 801,80 € brut, moins 20,84 % de cotisations et contributions salariales (vieillesse 6,90 % et 0,40 %, Agirc-Arrco 3,15 %, CEG 0,86 %, "
        "CSG et CRDS 9,70 % sur 98,25 % du brut), soit 1 426,30 € net et une garantie de 713,15 €. La source ne décrit que le montant : le "
        "reste du RSA est gardé, dont les majorations selon la composition du foyer et pour parent isolé, le forfait logement, tous proportionnels "
        "au montant de base, la prise en compte des ressources et l'âge minimum de 25 ans. Le site tiers francebudget.fr écrit que la garantie "
        "s'ouvrirait « dès 18 ans » ; aucun passage cité du programme ne le dit, l'âge n'est donc pas changé. La prime d'activité, qui a son "
        "propre montant forfaitaire, ne change pas. La suppression de la contrepartie de 15 heures n'a pas d'effet calculé : le RSA de la loi "
        "2025 dans OpenFisca n'en dépend pas. Combinée à une mesure sur le SMIC, la garantie reste calculée sur le SMIC de 2025."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # citation lue chez un tiers, le programme lui-même n'a pas pu être consulté
    hypotheses=(
        "Le recours à la prestation est supposé complet, et l'offre de travail des allocataires est tenue fixe. Le financement de la mesure "
        "et l'accompagnement qui remplacerait la contrepartie d'activité ne sont pas calculés."
    ),
)
