from openfisca_core.model_api import YEAR, Variable
from openfisca_france.entities import FoyerFiscal

from simulator.mesures import Mesure, ajouter_impot


class assiette_isf_ifi(Variable):
    def formula_2025_01_01(foyer_fiscal, period):
        # b1ab : valeur de la résidence principale, exclue de l'assiette.
        return foyer_fiscal("patrimoine_financier", period) + foyer_fiscal("patrimoine_immobilier", period) - foyer_fiscal("b1ab", period)


class isf_ifi(Variable):
    def formula_2025_01_01(foyer_fiscal, period):
        return foyer_fiscal.empty_array()


class impot_fortune_financiere(Variable):
    value_type = float
    entity = FoyerFiscal
    definition_period = YEAR
    label = "Impôt sur la fortune financière, montant payé"

    def formula_2025_01_01(foyer_fiscal, period):
        return foyer_fiscal("isf_ifi_apres_plaf", period)  # barème, décote, réductions et plafonnement de l'IFI, sur la nouvelle assiette


def appliquer(reforme):
    for variable in (assiette_isf_ifi, isf_ifi):
        reforme.update_variable(variable)
    ajouter_impot(reforme, impot_fortune_financiere)


MESURE = Mesure(
    id="impot_fortune_financiere",
    titre="Impôt sur la fortune financière à la place de l'IFI",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/22-mesures",
    citation="Supprimer l’IFI qui taxe l’enracinement et créer un IFF, impôt sur la fortune financière, pour taxer la spéculation.",
    traduction=(
        "La mesure 16 des « 22 mesures » de la campagne de 2022 ne donne ni assiette ni barème. Le rapport « Présidentielle 2027 — Analyse des "
        "programmes » (p. 16) range l'« IFF sur le patrimoine financier » parmi les mesures présentées à la conférence du 6 octobre 2026. Le "
        "texte précis est l'amendement I-CF361 au projet de loi de finances pour 2026, daté du 17 octobre 2025, présenté par Jean-Philippe "
        "Tanguy et le groupe Rassemblement national et rejeté en commission "
        "(https://www.assemblee-nationale.fr/dyn/17/amendements/1906A/CION_FIN/CF361.pdf). Il transforme l'IFI en impôt sur la fortune "
        "financière dont l'assiette est « l'ensemble du patrimoine » net, et en exclut « la résidence principale ou unique », les actifs "
        "nécessaires à une activité professionnelle, les trois quarts de la valeur des parts de TPE, PME et ETI et « les œuvres d'art détenues "
        "depuis plus de 10 ans ». Il ne modifie ni le seuil d'assujettissement de 1,3 M€ (article 964 du CGI), ni le barème et la décote "
        "(article 977), ni le plafonnement de l'impôt et des impôts sur le revenu à 75 % des revenus (article 979) : le calcul les garde. Le "
        "contre-budget 2026 du groupe RN chiffre « IFF à la place de la taxe sur les holdings et de l'IFI » à 4 Md€ "
        "(https://rassemblementnational.fr/documents/GRN-CONTRE-BUDGET-2026.pdf#page=7). À partir du 1er janvier 2025, l'IFI (variable "
        "isf_ifi) est annulé et l'impôt sur la fortune financière est calculé par la chaîne de l'IFI d'OpenFisca, dont l'assiette change "
        "(assiette_isf_ifi) : patrimoine financier plus patrimoine immobilier, moins la résidence principale, sans l'abattement de 30 % que "
        "l'amendement supprime. Le texte inclut dans l'assiette le patrimoine immobilier autre que la résidence principale ; le calcul le taxe "
        "avec le patrimoine financier. Le persona ne décrit ni biens professionnels, ni parts de société, ni œuvres d'art : ces exclusions sont "
        "comptées nulles. Le seuil de 1,3 M€ est apprécié sur l'assiette, résidence principale "
        "exclue. L'impôt s'ajoute aux impôts directs de l'année 2025."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # document de la campagne 2022 et amendement de 2025, que seule une source de 2026 rattache au programme 2027
    hypotheses=(
        "Le calcul suppose un patrimoine déclaré et évalué sans changement de comportement : ni réallocation entre immobilier et placements "
        "financiers, ni départ, ni effet de l'impôt sur la valeur des actifs."
    ),
)
