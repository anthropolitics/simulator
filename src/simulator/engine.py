"""Persona + scénario → ce que le scénario change pour le foyer, calculé avec OpenFisca-France."""

from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from functools import lru_cache
from importlib.metadata import version
from multiprocessing import get_context
from threading import Lock

from openfisca_core.model_api import YEAR, Variable
from openfisca_core.reforms import Reform
from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_france import FranceTaxBenefitSystem
from openfisca_france.entities import Famille, FoyerFiscal, Individu, Menage
from pydantic import BaseModel, Field, field_validator

from simulator.mesures import CATALOGUE, vers_famille, vers_menage
from simulator.persona import ANNEE, ANNEES, HEURES_TEMPS_PLEIN, Adulte, Persona, situation

# Montants annuels du ménage rendus pour chaque législation. Les impôts sont négatifs : ce que le foyer paie.
SORTIES = (
    "salaire_net",
    "retraite_nette",
    "csg",
    "impot_revenu",
    "impots_mesures",
    "impots_directs",
    "prestations_familiales",
    "minima_sociaux",
    "aides_logement",
    "prestations_mesures",
    "prestations_sociales",
    "revenu_disponible",
    "cout_du_travail",
)
VARIABLES_SORTIES = {"impot_revenu": "irpp_economique"}
VERSIONS = {paquet: version(paquet) for paquet in ("simulator", "openfisca-france")}


def _appeler(formule, entite, period, parameters):
    # OpenFisca accepte des formules à deux ou trois arguments.
    return formule(entite, period, parameters) if formule.__code__.co_argcount == 3 else formule(entite, period)


def _avec_crochets(loi):
    """La loi, plus les entrées propres au simulateur et deux crochets, nuls ici, où les mesures branchent impôts et prestations."""
    impots_directs_actuels = loi.variables["impots_directs"].get_formula(ANNEE)
    prestations_sociales_actuelles = loi.variables["prestations_sociales"].get_formula(ANNEE)

    class impots_mesures(Variable):
        value_type = float
        entity = Menage
        definition_period = YEAR
        label = "Impôts créés par les mesures simulées, montant payé"

    class prestations_mesures(Variable):
        value_type = float
        entity = Famille
        definition_period = YEAR
        label = "Prestations créées par les mesures simulées"

    class patrimoine_financier(Variable):
        value_type = float
        entity = FoyerFiscal
        definition_period = YEAR
        label = "Patrimoine financier net du foyer"

    class patrimoine_immobilier(Variable):
        value_type = float
        entity = FoyerFiscal
        definition_period = YEAR
        label = "Patrimoine immobilier net du foyer"

    class annees_travail_france(Variable):
        value_type = int
        entity = Individu
        definition_period = YEAR
        label = "Années travaillées en France, en équivalent temps plein"

    class insertion_15h(Variable):
        value_type = bool
        entity = Individu
        definition_period = YEAR
        label = "Au moins 15 heures par semaine de formation ou de recherche active d'emploi"

    # OpenFisca-France applique le barème de l'IFI dès 800 000 € ; l'IFI n'est dû qu'au-delà de 1,3 M€ (CGI, art. 964), borne basse de la décote.
    class isf_ifi_iai(Variable):
        def formula_2018_01_01(foyer_fiscal, period, parameters):
            assiette = foyer_fiscal("assiette_isf_ifi", period)
            ifi = parameters(period).taxation_capital.impot_fortune_immobiliere_ifi_partir_2018
            return (assiette > ifi.decote.borne_inferieure_decote) * ifi.bareme.calc(assiette)

    class impots_directs(Variable):
        value_type = float
        entity = Menage
        definition_period = YEAR
        label = "Impôts directs, y compris ceux des mesures simulées"

        def formula(menage, period, parameters):
            return _appeler(impots_directs_actuels, menage, period, parameters) - menage("impots_mesures", period)

    class prestations_sociales(Variable):
        value_type = float
        entity = Famille
        definition_period = YEAR
        label = "Prestations sociales, y compris celles des mesures simulées"

        def formula(famille, period, parameters):
            return _appeler(prestations_sociales_actuelles, famille, period, parameters) + famille("prestations_mesures", period)

    class Crochets(Reform):
        name = "Loi actuelle"

        def apply(self):
            for variable in (impots_mesures, prestations_mesures, patrimoine_financier, patrimoine_immobilier, annees_travail_france, insertion_15h):
                self.add_variable(variable)
            self.update_variable(impots_directs)
            self.update_variable(prestations_sociales)

            # OpenFisca-France reprend pour l'IFI le forfait mobilier de 5 % de l'ancien ISF ; l'IFI ne taxe que l'immobilier (CGI, art. 965).
            def sans_forfait_mobilier(parametres):
                parametres.taxation_capital.impot_fortune_immobiliere_ifi_partir_2018.forfait_mobilier.majoration_forfaitaire.update(
                    start="2018-01-01", value=0
                )
                return parametres

            self.modify_parameters(modifier_function=sans_forfait_mobilier)
            self.update_variable(isf_ifi_iai)

    return Crochets(loi)


LOI_ACTUELLE = _avec_crochets(FranceTaxBenefitSystem())
TRANCHE = 2  # troisième tranche du barème de l'impôt sur le revenu (30 % en 2025)


def bareme_ir(parametres):
    return parametres.impot_revenu.bareme_ir_depuis_1945.bareme


TAUX_ACTUEL = bareme_ir(LOI_ACTUELLE.parameters).brackets[TRANCHE].rate(f"{ANNEE}-01-01")


class Scenario(BaseModel, frozen=True):
    mesures: tuple[str, ...] = Field(default=(), description="Identifiants des mesures du catalogue, voir GET /mesures.")
    taux_troisieme_tranche_ir: float | None = Field(
        default=None, ge=0, le=0.6, description="Taux de la tranche à 30 % du barème de l'impôt sur le revenu, entre 0 et 0,6."
    )

    @field_validator("mesures")
    @classmethod
    def mesures_connues(cls, mesures):
        if inconnues := set(mesures) - CATALOGUE.keys():
            raise ValueError(f"Mesures inconnues : {', '.join(sorted(inconnues))}.")
        return tuple(sorted(set(mesures)))  # même scénario, même clé de cache

    @property
    def neutre(self) -> bool:
        return not self.mesures and self.taux_troisieme_tranche_ir in (None, TAUX_ACTUEL)


def _sommer(reforme, nom: str, entite, variables, ramener) -> None:
    def formula(population, period):
        return sum(ramener(population, variable, period) for variable in variables)

    reforme.update_variable(type(nom, (Variable,), {"value_type": float, "entity": entite, "definition_period": YEAR, "formula": formula}))


# shortcut: une réforme prend 0,7 s à construire, on garde les 8 dernières ; à revoir quand le site combinera les mesures librement.
@lru_cache(maxsize=8)
def loi(scenario: Scenario):
    if scenario.neutre:
        return LOI_ACTUELLE

    class Simulee(Reform):
        name = ", ".join(CATALOGUE[m].titre for m in scenario.mesures) or "Taux de la troisième tranche de l'impôt sur le revenu"

        def apply(self):
            self.impots_ajoutes, self.prestations_ajoutees = [], []
            if (taux := scenario.taux_troisieme_tranche_ir) is not None:

                def modifier(parametres):
                    bareme_ir(parametres).brackets[TRANCHE].rate.update(start=f"{ANNEE}-01-01", value=taux)
                    return parametres

                self.modify_parameters(modifier_function=modifier)
            for mesure in scenario.mesures:
                CATALOGUE[mesure].appliquer(self)
            if self.impots_ajoutes:
                _sommer(self, "impots_mesures", Menage, self.impots_ajoutes, vers_menage)
            if self.prestations_ajoutees:
                _sommer(self, "prestations_mesures", Famille, self.prestations_ajoutees, vers_famille)

    return Simulee(LOI_ACTUELLE)


def smic_annuel(legislation) -> dict[str, float]:
    """SMIC brut à temps plein de chaque année, mois par mois, selon la législation."""
    return {
        annee: sum(
            legislation.parameters(f"{annee}-{mois:02d}-01").marche_travail.salaire_minimum.smic.smic_b_horaire * HEURES_TEMPS_PLEIN for mois in range(1, 13)
        )
        for annee in ANNEES
    }


SMIC_ACTUEL = smic_annuel(LOI_ACTUELLE)


def calculer(legislation, persona: Persona) -> dict[str, int]:
    foyer = situation(persona, smic_annuel(legislation), SMIC_ACTUEL)
    if any(a.retraite_brute_mensuelle for a in persona.adultes):
        # Le taux de CSG sur une pension dépend du revenu fiscal de N-2 ; le calculer dans la même simulation crée une spirale
        # qu'OpenFisca coupe en annulant la CSG. On le fournit donc en entrée, estimé par une première simulation sur N-1.
        # shortcut: ce revenu de N-1 ignore la CSG déductible de N-1, il est surestimé de 4 à 6 % de la pension ; itérer si un cas limite en dépend.
        premiere = SimulationBuilder().build_from_entities(legislation, situation(persona, smic_annuel(legislation), SMIC_ACTUEL))
        foyer["foyers_fiscaux"]["foyer"]["rfr"] = {str(int(ANNEE) - 2): float(premiere.calculate("rfr", ANNEES[0])[0])}
    simulation = SimulationBuilder().build_from_entities(legislation, foyer)
    return {sortie: round(float(simulation.calculate_add(VARIABLES_SORTIES.get(sortie, sortie), ANNEE).sum())) for sortie in SORTIES}


def calculer_selon(scenario: Scenario, persona: Persona) -> dict[str, int]:
    return calculer(loi(scenario), persona)


def brut_depuis_net(net_mensuel: float, legislation=LOI_ACTUELLE) -> float:
    """Salaire brut mensuel d'un salarié seul, à temps plein, qui touche ce salaire net ; OpenFisca ne calcule que dans l'autre sens."""
    bas, haut = net_mensuel, net_mensuel * 2
    while haut - bas > 0.01:
        milieu = (bas + haut) / 2
        persona = Persona(adultes=(Adulte(salaire_brut_mensuel=milieu),))
        simulation = SimulationBuilder().build_from_entities(legislation, situation(persona, smic_annuel(legislation), SMIC_ACTUEL))
        bas, haut = (milieu, haut) if simulation.calculate_add("salaire_net", ANNEE).sum() / 12 < net_mensuel else (bas, milieu)
    return round((bas + haut) / 2, 2)


# OpenFisca garde les paramètres par date dans un cache de 128 entrées commun à toutes les législations, et une simulation
# en lit 112 : dans un même processus, la loi actuelle et le scénario se chassent du cache (3,5 s par calcul au lieu de 1,3).
# Chacun tourne donc dans son processus, qui garde son cache chaud, et les deux calculs se font en parallèle.
PROCESSUS: dict[str, ProcessPoolExecutor] = {}
VERROU = Lock()


def lancer(role: str, scenario: Scenario, persona: Persona):
    with VERROU:
        try:
            return PROCESSUS[role].submit(calculer_selon, scenario, persona)
        except (KeyError, BrokenProcessPool):  # premier calcul, ou processus tué (par exemple faute de mémoire) : on le relance
            PROCESSUS[role] = ProcessPoolExecutor(max_workers=1, mp_context=get_context("spawn"))
            return PROCESSUS[role].submit(calculer_selon, scenario, persona)


@lru_cache(maxsize=4096)  # mêmes entrées, même résultat : les valeurs par défaut du site ne se calculent qu'une fois
def simuler(persona: Persona, scenario: Scenario) -> dict:
    """Montants annuels du foyer selon la loi actuelle et selon le scénario."""
    avant = lancer("loi actuelle", Scenario(), persona)
    apres = avant if scenario.neutre else lancer("scenario", scenario, persona)
    avant, apres = avant.result(), apres.result()
    return {
        "annee": int(ANNEE),
        "mesures": list(scenario.mesures),
        "avant": avant,
        "apres": apres,
        "ecart_revenu_disponible": apres["revenu_disponible"] - avant["revenu_disponible"],
        "versions": VERSIONS,
    }
