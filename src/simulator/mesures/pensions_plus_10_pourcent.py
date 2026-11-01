from openfisca_core.model_api import Variable, set_input_divide_by_period

from simulator.mesures import Mesure

HAUSSE = 0.10
SOURCE = "https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf"
CITATION = (
    "« La loi de finances peut inverser la tendance en augmentant les revenus pour lesquels l'État est décisionnaire : [...] en protégeant les "
    "milieux populaires et les familles de l'inflation, sur laquelle nous indexerons toutes les pensions, allocations familiales et APL, qui seront "
    "rehaussées de 10 % (8 milliards d'euros). » (p. 8)"
)
DOCUMENT = (
    "Source : « Comment nous allons remettre de l'ordre dans les comptes publics », La France insoumise, document de la campagne présidentielle 2027 "
    "daté du 14 octobre 2026 (consulté le 31 octobre 2026). La phrase est lue comme une hausse de 10 % de chacune des trois prestations qu'elle "
    "énumère ; chacune fait l'objet d'une mesure : pensions_plus_10_pourcent, allocations_familiales_plus_10_pourcent et apl_plus_10_pourcent. "
)


def _saisie_majoree(holder, period, array):
    set_input_divide_by_period(holder, period, (1 + HAUSSE) * array)


class retraite_brute(Variable):
    # La retraite du persona est une donnée d'entrée, sans formule : la hausse s'applique quand la simulation la reçoit, par année.
    set_input = _saisie_majoree


def appliquer(reforme):
    reforme.update_variable(retraite_brute)


MESURE = Mesure(
    id="pensions_plus_10_pourcent",
    titre="Retraites déjà versées revalorisées de 10 %",
    candidats=("Jean-Luc Mélenchon",),
    source=SOURCE,
    citation=CITATION,
    traduction=(
        DOCUMENT + "La retraite brute saisie dans le persona, pension en cours de paiement, est multipliée par 1,1 pour 2025 et pour l'année précédente que "
        "la simulation lit aussi (ressources des minima sociaux, revenu fiscal qui fixe le taux de CSG de la pension) : la hausse est simulée comme "
        "si elle s'appliquait déjà. La CSG, la CRDS, la CASA, l'impôt sur le revenu et le minimum vieillesse suivent la pension relevée. Le "
        "document ne dit pas quelles pensions sont visées : la mesure porte sur les retraites, seule pension que décrit le persona ; les pensions "
        "d'invalidité ou de réversion ne sont pas distinguées. Elle ne change pas le calcul des retraites des salariés qui partiront (moteur de "
        "retraite) : une revalorisation porte sur les pensions déjà liquidées. Le coût annoncé, 8 milliards d'euros pour les trois prestations, est "
        "très inférieur à celui d'une hausse de 10 % des seules retraites, de l'ordre de 40 milliards d'euros pour 422 milliards d'euros de "
        "pensions versées en 2025 (Conseil d'orientation des retraites, synthèse du rapport annuel de juin 2026, "
        "https://www.cor-retraites.fr/sites/default/files/2026-06/Synth%C3%A8se%20RA.pdf, consulté le 31 octobre 2026) : il s'accorderait mieux "
        "avec une simple indexation des pensions sur l'inflation, la hausse de 10 % ne visant que les allocations familiales et les APL. La mesure "
        "suit la lettre du texte ; l'indexation sur l'inflation, déjà prévue par la loi 2025, ne change rien dans la simulation."
    ),
    appliquer=appliquer,
    hypotheses=(
        "Le financement et ses effets sur les comptes de l'assurance vieillesse ne sont pas calculés, pas plus que l'effet de la hausse des "
        "pensions sur la consommation et les prix."
    ),
)
