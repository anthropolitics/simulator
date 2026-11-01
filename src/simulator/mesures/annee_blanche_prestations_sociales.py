from datetime import date, timedelta
from functools import reduce

from openfisca_core.parameters import Parameter
from openfisca_core.periods import instant

from simulator.mesures import Mesure
from simulator.persona import ANNEE

# Montants revalorisés au 1er avril selon l'inflation (art. L161-25 du code de la sécurité sociale) : base mensuelle des allocations familiales,
# dont toutes les prestations familiales sont des pourcentages, RSA, prime d'activité, allocation aux adultes handicapés, ASS.
MONTANTS = (
    "prestations_sociales.prestations_familiales.bmaf.bmaf",
    "prestations_sociales.solidarite_insertion.minima_sociaux.rsa.rsa_m.montant_de_base_du_rsa",
    "prestations_sociales.solidarite_insertion.minima_sociaux.ppa.pa_m.montant_de_base",
    "prestations_sociales.prestations_etat_de_sante.invalidite.aah.montant",
    "chomage.allocations_assurance_chomage.ass.montant_plein",
)
# Barème des aides au logement des locataires, revalorisé au 1er octobre selon l'indice de référence des loyers (art. L823-4 du code de la
# construction et de l'habitation) : loyers plafonds, forfait de charges, participation minimale.
BAREME_LOGEMENT = "prestations_sociales.aides_logement.allocations_logement.locatif.formule"
REVALORISATION_LOGEMENT = f"{ANNEE}-10-01"


def geler(parametre: Parameter) -> None:
    """Retire du paramètre, toute l'année simulée, la revalorisation qu'il reçoit dans l'année : en euros constants, une année sans revalorisation."""
    revalorisation = parametre(f"{ANNEE}-12-31") / parametre(f"{int(ANNEE) - 1}-12-31")
    debuts = [f"{ANNEE}-01-01", *sorted(v.instant_str for v in parametre.values_list if f"{ANNEE}-01-01" < v.instant_str <= f"{ANNEE}-12-31")]
    fins = [(date.fromisoformat(d) - timedelta(days=1)).isoformat() for d in debuts[1:]] + [f"{ANNEE}-12-31"]
    for debut, fin, valeur in [(d, f, parametre(d)) for d, f in zip(debuts, fins)]:
        parametre.update(start=instant(debut), stop=instant(fin), value=valeur / revalorisation)


def feuilles(noeud):
    if isinstance(noeud, Parameter):
        yield noeud
    for enfant in getattr(noeud, "children", {}).values():
        yield from feuilles(enfant)


def appliquer(reforme):
    def modifier(parametres):
        for chemin in MONTANTS:
            geler(reduce(getattr, chemin.split("."), parametres))
        for parametre in feuilles(reduce(getattr, BAREME_LOGEMENT.split("."), parametres)):
            if any(v.instant_str == REVALORISATION_LOGEMENT for v in parametre.values_list):
                geler(parametre)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="annee_blanche_prestations_sociales",
    titre="Année blanche : les prestations sociales ne sont pas revalorisées pendant un an, sauf les petites retraites",
    candidats=("Gabriel Attal",),
    source="https://attalpresident.fr/actualites/dans-le-parisien-gabriel-attal-vise-le-zero-deficit-en-2037",
    citation="Dès le budget 2028, une « année blanche » gèlerait temporairement les prestations sociales, en protégeant les petites retraites.",
    traduction=(
        "Page du site de campagne du 3 juillet 2026, qui résume l'entretien du candidat au Parisien (consultée le 31 octobre 2026) ; la fiche « Équilibrer "
        "les comptes de la Sécurité sociale » (https://attalpresident.fr/programme/mesures/equilibre-securite-sociale) cite aussi l'année blanche, sans "
        "la détailler. Une année blanche ne baisse aucun montant en euros courants : elle supprime une revalorisation, que les années suivantes ne "
        "rattrapent pas. Dans ce simulateur en euros constants de 2025, elle devient une baisse de niveau, sur toute l'année simulée, égale à la "
        "revalorisation de 2025 de chaque montant. La base mensuelle des allocations familiales, le montant de base du RSA, celui de la prime "
        "d'activité, l'allocation aux adultes handicapés et l'allocation de solidarité spécifique, revalorisés de 1,7 % au 1er avril 2025, sont "
        "divisés par 1,017 du 1er janvier au 31 décembre 2025 : de janvier à mars ils valent leur montant de 2024 divisé par 1,017, d'avril à décembre "
        "leur montant de 2024. Toutes les prestations familiales, qui sont des pourcentages de cette base, baissent de 1,7 % ; le RSA et la prime "
        "d'activité, qui complètent les ressources jusqu'à un montant garanti, baissent davantage en proportion. Le barème des aides au logement des "
        "locataires revalorisé au 1er octobre 2025 (+1,04 %, indice de référence des loyers) est divisé de même par sa revalorisation : loyers "
        "plafonds, forfait de charges et participation minimale. Les plafonds de ressources, revalorisés au 1er janvier, ne changent pas : la source "
        "parle de geler les prestations, pas leurs conditions. Le candidat protège les « petites retraites » sans dire jusqu'à quel montant : le "
        "minimum vieillesse (ASPA) est revalorisé comme aujourd'hui, et les pensions de retraite, que le persona donne en montant et qu'une mesure "
        "ne peut pas changer dans ce simulateur, ne sont pas gelées, si bien que la perte des retraités au-dessus du seuil n'est pas simulée."
    ),
    appliquer=appliquer,
    hypotheses=(
        "La revalorisation perdue est celle de 2025 (1,7 % au 1er avril, 1,04 % au 1er octobre pour le logement) ; celle de 2028, qui dépendra de "
        "l'inflation de 2027, n'est pas connue. Les pensions de retraite au-dessus du seuil des « petites retraites » ne sont pas gelées, faute de "
        "seuil et de levier dans le simulateur. Les effets sur la consommation et le recours aux prestations ne sont pas calculés."
    ),
)
