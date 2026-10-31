from numpy import floor
from openfisca_core.model_api import Variable

from simulator.mesures import Mesure

HAUSSE = 0.10


def appliquer(reforme):
    actuelle = reforme.variables["aide_logement"].get_formula("2025-01-01")

    class aide_logement(Variable):
        def formula_2025_01_01(famille, period):
            return floor((1 + HAUSSE) * actuelle(famille, period))  # versée à l'euro inférieur, comme l'aide actuelle

    reforme.update_variable(aide_logement)


MESURE = Mesure(
    id="apl_plus_10_pourcent",
    titre="Aides au logement revalorisées de 10 %",
    candidats=("Marine Tondelier",),
    source="https://lesecologistes.fr/pages/6ImK65GKUnvibm33WGkjkj/projet-2027",
    citation="Revaloriser les APL de 10 % avec un mécanisme empêchant la répercussion sur les montants des loyers.",
    traduction=(
        "Le texte de la mesure est celui que votons-2027.fr cite en renvoyant à la page du projet des Écologistes, qui n'a pas pu être lue "
        "directement. À partir du 1er janvier 2025, le montant mensuel des aides au logement (variable aide_logement, somme de l'APL, de l'ALF et de "
        "l'ALS) est multiplié par 1,1 puis arrondi à l'euro inférieur. La source porte sur le montant des aides (« revaloriser les APL de 10 % ») "
        "sans détailler le barème : chaque allocataire reçoit 10 % de plus. Relever de 10 % les paramètres du barème (loyers plafonds, forfait de "
        "charges) aurait donné une hausse variable selon le loyer et la composition du foyer, que la source ne décrit pas. La hausse s'applique aux "
        "trois aides, que la source ne distingue pas et qu'OpenFisca calcule avec le même barème (aide_logement_montant) : le persona, locataire d'un "
        "logement vide non conventionné, touche l'ALF ou l'ALS et non l'APL. Le mécanisme contre la répercussion sur les loyers n'est pas décrit ; il "
        "n'a pas d'effet ici, le loyer du persona étant une donnée."
    ),
    appliquer=appliquer,
    a_confirmer=True,
    hypotheses=(
        "Le loyer est tenu fixe : une hausse des loyers, que la mesure entend empêcher, n'est pas simulée. Le financement, les effets sur le recours "
        "aux aides et sur le marché du logement ne sont pas calculés."
    ),
)
