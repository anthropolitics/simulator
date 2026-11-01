from openfisca_core.model_api import ADD, Variable, where
from openfisca_france.entities import FoyerFiscal

from simulator.mesures import Mesure

PLAFOND = 3000  # réduction d'impôt annuelle des familles plus aisées
AGE = 3  # pendant les trois premières années de l'enfant


def appliquer(reforme):
    actuelle = reforme.variables["reductions"].get_formula("2025-01-01")

    class reductions(Variable):
        def formula_2025_01_01(foyer_fiscal, period, parameters):
            actuelles = actuelle(foyer_fiscal, period, parameters)
            impot = foyer_fiscal("ip_net", period) - actuelles  # impôt après les réductions actuelles, positif
            jeune_enfant = foyer_fiscal.any(foyer_fiscal.members("age", period.first_month) < AGE, role=FoyerFiscal.PERSONNE_A_CHARGE)
            travaille = foyer_fiscal.any(foyer_fiscal.members("salaire_imposable", period, options=[ADD]) > 0, role=FoyerFiscal.DECLARANT)
            # Jusqu'à 3 000 €, l'impôt est supprimé ; au-delà, un foyer qui travaille a 3 000 € de réduction.
            return actuelles + jeune_enfant * where(impot <= PLAFOND, impot, PLAFOND * travaille)

    reforme.update_variable(reductions)


MESURE = Mesure(
    id="impot_revenu_trois_premieres_annees_enfant",
    titre="Pas d'impôt sur le revenu pendant les trois premières années de l'enfant pour les classes moyennes, 3 000 € de réduction au-delà",
    candidats=("Édouard Philippe",),
    source="https://www.edouardphilippe.fr/priorites/pour-une-france-plus-attentive-a-ses-enfants",
    citation=(
        "Supprimer l'impôt sur le revenu pendant les trois premières années de l'enfant pour les classes moyennes (4e à 6e déciles, début du 7e) ; "
        "accorder une réduction d'impôt de 3 000 € par an sur la même période aux familles plus aisées qui travaillent."
    ),
    traduction=(
        "Site de campagne du candidat (page consultée le 31 octobre 2026) ; il a repris la mesure sur France 2 le 8 octobre 2026 (« L'Heure de "
        "vérité », franceinfo et AFP, https://www.franceinfo.fr/elections/presidentielle/edouard-philippe-veut-aider-les-familles-des-le-premier-enfant-et-via-une-reduction-d-impot_8229028.html). "
        "Pour l'impôt sur les revenus de 2025, un foyer fiscal qui a à charge un enfant de moins de 3 ans au 1er janvier 2025 (0, 1 ou 2 ans dans le "
        "persona) voit son impôt, après les réductions actuelles, supprimé s'il ne dépasse pas 3 000 €, et réduit de 3 000 € au-delà si un "
        "déclarant a un salaire ; la réduction s'ajoute aux réductions d'impôt (variable reductions). La source situe la frontière entre les deux "
        "volets en déciles, sans montant : le calcul la place là où l'impôt atteint 3 000 €, le montant de la réduction des familles plus aisées, "
        "ce qui évite qu'une famille juste au-dessus de la frontière gagne moins qu'une famille juste en dessous. Pour un couple avec un enfant d'un "
        "an, l'impôt atteint 3 000 € à environ 3 220 € brut par mois chacun, soit un niveau de vie d'environ 33 600 € par an, 1,3 fois le niveau de "
        "vie médian de 2023 (25 760 €, Insee Première n° 2063, juillet 2025) : vers le début du 7e décile que vise la source. Pour un parent isolé, "
        "qui a moins d'unités de consommation par part fiscale, la frontière tombe plus haut dans la distribution. Les foyers des trois premiers "
        "déciles, que la source ne vise pas, paient très rarement l'impôt ; ils sont traités comme les classes moyennes. La réduction est due par "
        "foyer et par an, quel que soit le nombre d'enfants de moins de 3 ans ; elle ne crée pas de remboursement. La condition de travail des "
        "familles plus aisées est lue comme un salaire d'au moins un déclarant, seul revenu d'activité du persona."
    ),
    appliquer=appliquer,
    hypotheses="Les effets sur la natalité et l'activité des parents ne sont pas simulés, pas plus que le financement.",
)
