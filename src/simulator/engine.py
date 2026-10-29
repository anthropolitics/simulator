"""Persona + scénario → ce que le scénario change pour le foyer, calculé avec OpenFisca-France."""

from functools import lru_cache
from importlib.metadata import version

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
# shortcut: alterner loi actuelle et réforme vide le cache de paramètres d'OpenFisca (128 dates partagées, 112 lues
# par simulation) : une requête prend environ 7 s au lieu de 3. À traiter avant d'ouvrir le simulateur au public.
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


def situation(salaires: list[float], enfants: int) -> dict:
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


def simuler(salaires: list[float], enfants: int, taux: float) -> dict:
    """Montants annuels du foyer selon la loi actuelle et selon le scénario."""
    foyer = situation(salaires, enfants)
    avant, apres = calculer(LOI_ACTUELLE, foyer), calculer(loi(taux), foyer)
    return {
        "annee": int(ANNEE),
        "avant": avant,
        "apres": apres,
        "ecart_revenu_disponible": apres["revenu_disponible"] - avant["revenu_disponible"],
        "versions": VERSIONS,
    }
