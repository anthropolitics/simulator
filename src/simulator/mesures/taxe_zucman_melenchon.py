from openfisca_core.model_api import YEAR, Variable, max_
from openfisca_france.entities import FoyerFiscal

from simulator.mesures import Mesure, ajouter_impot

SEUIL = 100_000_000
TAUX = 0.02


class taxe_zucman(Variable):
    value_type = float
    entity = FoyerFiscal
    definition_period = YEAR
    label = "Impôt plancher de 2 % sur les patrimoines de plus de 100 millions d'euros, montant payé"

    def formula(foyer_fiscal, period):
        patrimoine = foyer_fiscal("patrimoine_financier", period) + foyer_fiscal("patrimoine_immobilier", period)
        prelevements_sociaux = foyer_fiscal.sum(foyer_fiscal.members("csg", period) + foyer_fiscal.members("crds", period))
        deja_paye = -(foyer_fiscal("irpp_economique", period) + foyer_fiscal("isf_ifi", period) + prelevements_sociaux)  # montants OpenFisca négatifs
        return (patrimoine > SEUIL) * max_(TAUX * patrimoine - deja_paye, 0)


def appliquer(reforme):
    if "taxe_zucman" not in reforme.variables:  # proposée par plusieurs candidats : un scénario qui les réunit la compte une fois
        ajouter_impot(reforme, taxe_zucman)


TRADUCTION = (
    "« Taxe Zucman » désigne l'impôt plancher de la proposition de loi adoptée par l'Assemblée nationale le 20 février 2025 (texte adopté "
    "n° 58) : un foyer dont le patrimoine net dépasse 100 millions d'euros paie la différence, si elle est positive, entre 2 % de la "
    "totalité de son patrimoine et ce qu'il acquitte déjà au titre de l'impôt sur le revenu (contribution exceptionnelle sur les hauts "
    "revenus comprise), de l'IFI, de la CSG et de la CRDS. Le taux de 2 % porte sur tout le patrimoine, pas seulement sur la part au-delà du "
    "seuil. Le patrimoine est la somme du patrimoine financier et du patrimoine immobilier nets du persona ; le persona ne dit pas quelle part "
    "est la résidence principale, l'abattement d'un million d'euros que le texte lui accorde n'est donc pas appliqué. Le simulateur ne "
    "calcule pas l'IFI sur le patrimoine du persona : la déduction de l'IFI est nulle, ce qui surestime l'impôt plancher d'un foyer qui paie "
    "l'IFI. La contribution différentielle sur les hauts revenus, créée après ce texte, n'est pas déduite. L'impôt s'ajoute aux impôts "
    "directs de l'année 2025."
)
HYPOTHESES = (
    "Le calcul suppose un patrimoine déclaré et évalué sans changement de comportement : ni départ, ni changement de résidence fiscale, ni "
    "réorganisation du patrimoine, ni effet de la taxe sur la valeur des actifs. Il ne dit rien de la façon dont un foyer dont le patrimoine "
    "est peu liquide acquitterait l'impôt (le texte prévoit un paiement étalé sur cinq ans en cas de gêne)."
)

MESURE = Mesure(
    id="taxe_zucman_melenchon",
    titre="Taxe Zucman : impôt plancher de 2 % sur les patrimoines de plus de 100 millions d'euros",
    candidats=("Jean-Luc Mélenchon",),
    source="https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf",
    citation=(
        "Il faudra donc aller plus loin en s'attaquant à cet enrichissement indécent. Cela passera par exemple par l'instauration de la taxe "
        "Zucman pour les personnes possédant plus de 100 millions d'euros de patrimoine (15 milliards d'euros de recettes)"
    ),
    traduction=TRADUCTION,
    appliquer=appliquer,
    hypotheses=HYPOTHESES,
)
