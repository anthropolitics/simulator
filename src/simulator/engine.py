"""Persona + scénario → ce que le scénario change pour le foyer, calculé avec OpenFisca-France."""

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from functools import lru_cache
from importlib.metadata import version
from multiprocessing import get_context
from threading import Lock

from openfisca_core.reforms import Reform
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem

# Dernière année dont la législation est entièrement votée : le barème des revenus 2025 date de la loi de finances 2026.
ANNEE = "2025"
VARIABLES = ("salaire_net", "impots_directs", "prestations_sociales", "revenu_disponible")
VERSIONS = {paquet: version(paquet) for paquet in ("simulator", "openfisca-france")}

LOI_ACTUELLE = FranceTaxBenefitSystem()
TRANCHE = 2  # troisième tranche du barème de l'impôt sur le revenu (30 % en 2025)


def bareme_ir(parametres):
    return parametres.impot_revenu.bareme_ir_depuis_1945.bareme


TAUX_ACTUEL = bareme_ir(LOI_ACTUELLE.parameters).brackets[TRANCHE].rate(f"{ANNEE}-01-01")


# shortcut: une réforme prend 0,7 s à construire, on garde les 8 dernières ; à revoir avec le catalogue de mesures.
@lru_cache(maxsize=8)
def loi(taux: float):
    if taux == TAUX_ACTUEL:
        return LOI_ACTUELLE

    class Scenario(Reform):
        name = f"Taux de la troisième tranche de l'impôt sur le revenu à {taux:.0%}"

        def apply(self):
            def modifier(parametres):
                bareme_ir(parametres).brackets[TRANCHE].rate.update(start=f"{ANNEE}-01-01", value=taux)
                return parametres

            self.modify_parameters(modifier_function=modifier)

    return Scenario(LOI_ACTUELLE)


def situation(salaires: tuple[float, ...], enfants: int) -> dict:
    """Foyer OpenFisca : un ou deux adultes mariés, leurs enfants de 10 ans."""
    adultes = [f"adulte{i + 1}" for i in range(len(salaires))]
    petits = [f"enfant{i + 1}" for i in range(enfants)]
    individus = {
        nom: {
            # Les minima sociaux regardent les revenus des mois précédents : sans l'année d'avant, OpenFisca verse un RSA fantôme.
            "salaire_de_base": {str(int(ANNEE) - 1): salaire * 12, ANNEE: salaire * 12},
            "date_naissance": {"ETERNITY": "1985-01-01"},
            "statut_marital": {ANNEE: "marie" if len(adultes) == 2 else "celibataire"},
        }
        for nom, salaire in zip(adultes, salaires)
    }
    individus |= {nom: {"date_naissance": {"ETERNITY": "2015-01-01"}} for nom in petits}
    return {
        "individus": individus,
        "foyers_fiscaux": {"foyer": {"declarants": adultes, "personnes_a_charge": petits}},
        "familles": {"famille": {"parents": adultes, "enfants": petits}},
        "menages": {"menage": {"personne_de_reference": adultes[:1], "conjoint": adultes[1:], "enfants": petits}},
    }


def calculer(legislation, foyer: dict) -> dict[str, int]:
    simulation = SimulationBuilder().build_from_entities(legislation, foyer)
    return {variable: round(float(simulation.calculate_add(variable, ANNEE).sum())) for variable in VARIABLES}


def calculer_selon(taux: float, foyer: dict) -> dict[str, int]:
    return calculer(loi(taux), foyer)


# OpenFisca garde les paramètres par date dans un cache de 128 entrées commun à toutes les législations, et une simulation
# en lit 112 : dans un même processus, la loi actuelle et le scénario se chassent du cache (3,5 s par calcul au lieu de 1,3).
# Chacun tourne donc dans son processus, qui garde son cache chaud, et les deux calculs se font en parallèle.
PROCESSUS: dict[str, ProcessPoolExecutor] = {}
VERROU = Lock()


def lancer(role: str, taux: float, foyer: dict):
    with VERROU:
        try:
            return PROCESSUS[role].submit(calculer_selon, taux, foyer)
        except (KeyError, BrokenProcessPool):  # premier calcul, ou processus tué (par exemple faute de mémoire) : on le relance
            PROCESSUS[role] = ProcessPoolExecutor(max_workers=1, mp_context=get_context("spawn"))
            return PROCESSUS[role].submit(calculer_selon, taux, foyer)


@lru_cache(maxsize=4096)  # mêmes entrées, même résultat : les valeurs par défaut du site ne se calculent qu'une fois
def simuler(salaires: tuple[float, ...], enfants: int, taux: float) -> dict:
    """Montants annuels du foyer selon la loi actuelle et selon le scénario."""
    foyer = situation(salaires, enfants)
    avant = lancer("loi actuelle", TAUX_ACTUEL, foyer)
    apres = avant if taux == TAUX_ACTUEL else lancer("scenario", taux, foyer)
    avant, apres = avant.result(), apres.result()
    return {
        "annee": int(ANNEE),
        "avant": avant,
        "apres": apres,
        "ecart_revenu_disponible": apres["revenu_disponible"] - avant["revenu_disponible"],
        "versions": VERSIONS,
    }
