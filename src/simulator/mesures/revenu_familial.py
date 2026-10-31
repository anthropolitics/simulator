from openfisca_core.model_api import MONTH, Variable
from openfisca_france.entities import Famille

from simulator.mesures import Mesure, ajouter_prestation

MONTANT_PAR_ENFANT = 240
AGE_LIMITE = 18
DUREE = 5  # années de titre de séjour et de travail en France exigées d'un parent étranger
# Allocations familiales (majoration pour âge comprise), complément familial, allocation de rentrée scolaire, enfants du RSA et de la prime d'activité.
REMPLACEES = ("af", "cf", "ars", "rsa_nb_enfants")


class revenu_familial(Variable):
    value_type = float
    entity = Famille
    definition_period = MONTH
    label = "Revenu familial"

    def formula(famille, period):
        individu = famille.members
        francais = individu("nationalite", period) == b"FR"
        resident_actif = (individu("duree_possession_titre_sejour", period) >= DUREE) * (individu("annees_travail_france", period.this_year) >= DUREE)
        droit = famille.any(francais + resident_actif, role=Famille.PARENT)
        return droit * MONTANT_PAR_ENFANT * famille.sum(individu("age", period) < AGE_LIMITE, role=Famille.ENFANT)


def appliquer(reforme):
    ajouter_prestation(reforme, revenu_familial)
    for variable in REMPLACEES:
        reforme.neutralize_variable(variable)

    def modifier(parametres):
        qf = parametres.impot_revenu.calcul_impot_revenu.plaf_qf.quotient_familial
        for parts in (qf.cas_general.enf1, qf.cas_general.enf2, qf.cas_general.enf3_et_sup, qf.couple_ou_pers_a_charge.isol):
            parts.update(start="2025-01-01", value=0)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="revenu_familial",
    titre="Revenu familial de 240 € par mois et par enfant mineur, en remplacement de 12 dispositifs",
    candidats=("Bruno Retailleau",),
    source="https://republicains.fr/wp-content/uploads/2026/05/LR_Famille_vFinale.pdf",
    citation=(
        "Fusionner 12 dispositifs pour les remplacer par un Revenu familial (RF) de 240 euros versé chaque mois à tous, dès le premier enfant, de la "
        "naissance jusqu'à 18 ans ; Conditionner le Revenu familial à une résidence régulière en France et à l'exercice d'une activité "
        "professionnelle depuis au moins cinq ans et en permettre la suspension temporaire par décision de justice en cas de défaillance éducative ; "
        "Conserver les aides spécifiques pour les enfants de 0 à 3 ans (PAJE), les parents seuls (ASF), le logement (APL) ou le handicap (AEEH)."
    ),
    traduction=(
        "Le livret énumère les dispositifs existants (p. 10) : allocations familiales, supplément familial de traitement, quotient familial, "
        "majoration pour âge, complément familial, PAJE, allocation de rentrée scolaire, réduction d'impôt pour enfant scolarisé, bourses de collège "
        "et de lycée, prise en compte des enfants dans le RSA et la prime d'activité ; il cite parmi les dispositifs supprimés « notamment "
        "allocations familiales, majoration pour âge, complément familial, quotient familial » (p. 12) et maintient la PAJE, l'ASF, les aides au "
        "logement et l'AEEH (p. 11). Les dispositifs remplacés sont donc ceux de la page 10, PAJE exceptée. En 2025, chaque famille reçoit 240 € par "
        "mois et par enfant à charge de moins de 18 ans, prestation versée par l'impôt ou par virement selon le livret, donc ni imposable, ni comptée "
        "dans les ressources des autres prestations ; les variables af (majoration pour âge comprise), cf et ars sont neutralisées ; le nombre "
        "d'enfants retenu par le RSA et la prime d'activité (rsa_nb_enfants) est mis à zéro, si bien que majorations pour enfant, majoration pour "
        "parent isolé et forfait logement y sont calculés comme pour un foyer sans enfant, et qu'un parent de moins de 25 ans n'y a plus droit au "
        "titre de ses enfants ; les parts de quotient familial des enfants à charge et la demi-part de parent isolé (paramètres enf1, enf2, "
        "enf3_et_sup et isol) passent à zéro au 1er janvier 2025. Un enfant à charge de 18 ans ou plus perd ces dispositifs sans recevoir le Revenu "
        "familial. La réduction d'impôt pour frais de scolarité, les bourses et le supplément familial de traitement ne concernent pas le persona, "
        "qui ne déclare ni scolarité ni emploi public. Le doublement pour le troisième enfant mineur (proposition 2 du même livret) n'est pas inclus. "
        "Le livret réserve la condition de résidence et d'activité aux étrangers : « pour bénéficier pleinement des dispositifs familiaux, les "
        "ressortissants étrangers devront justifier de cinq années de résidence en France et d'exercice d'une activité professionnelle » (p. 4). "
        "Le Revenu familial est donc versé si un parent est français, ou si un parent étranger a au moins cinq ans de titre de séjour et au moins "
        "cinq années travaillées en France, en équivalent temps plein, sans exiger un emploi en cours. Le livret ne dit pas si, dans un couple, la "
        "condition vaut pour chaque parent ou pour l'un d'eux : il suffit ici qu'un parent la remplisse, comme il suffit qu'un parent soit "
        "français. Les ressortissants de l'Union européenne, que la source ne distingue pas, sont traités comme les autres étrangers. Une famille "
        "qui ne remplit pas la condition ne reçoit ni le Revenu familial ni les dispositifs qu'il remplace ; le livret, qui écrit « pleinement », "
        "ne dit pas ce qu'elle conserverait."
    ),
    appliquer=appliquer,
    hypotheses=(
        "La suspension temporaire par décision de justice en cas de défaillance éducative n'est pas simulée : le ménage type ne décrit aucune "
        "décision de justice. Les effets sur la natalité, l'activité des parents et le recours aux prestations ne sont pas simulés, pas plus que le "
        "financement et les économies de gestion annoncés."
    ),
)
