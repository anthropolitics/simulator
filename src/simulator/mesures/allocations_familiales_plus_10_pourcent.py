from openfisca_core.model_api import Variable

from simulator.mesures import Mesure
from simulator.mesures.pensions_plus_10_pourcent import CITATION, DOCUMENT, SOURCE

HAUSSE = 0.10


def appliquer(reforme):
    actuelle = reforme.variables["af"].get_formula("2025-01-01")

    class af(Variable):
        def formula_2025_01_01(famille, period, parameters):
            return (1 + HAUSSE) * actuelle(famille, period, parameters)

    reforme.update_variable(af)


MESURE = Mesure(
    id="allocations_familiales_plus_10_pourcent",
    titre="Allocations familiales revalorisées de 10 %",
    candidats=("Jean-Luc Mélenchon",),
    source=SOURCE,
    citation=CITATION,
    traduction=(
        DOCUMENT + "À partir du 1er janvier 2025, le montant mensuel des allocations familiales (variable af : montant de base selon le nombre d'enfants et "
        "les ressources, majorations pour âge, allocation forfaitaire et compléments dégressifs) est multiplié par 1,1. Le document nomme les "
        "« allocations familiales » : les autres prestations familiales (complément familial, allocation de rentrée scolaire, PAJE, allocation de "
        "soutien familial) ne changent pas. La hausse entre, comme les allocations elles-mêmes, dans les ressources du RSA et de la prime "
        "d'activité. Le chiffrage du document (8 milliards d'euros pour les pensions, les allocations familiales et les APL) est discuté dans la "
        "mesure pensions_plus_10_pourcent ; une hausse de 10 % des allocations familiales y tient dans tous les cas."
    ),
    appliquer=appliquer,
    hypotheses="Les effets sur la natalité, l'activité des parents et le financement de la branche famille ne sont pas calculés.",
)
