"""Catalogue des mesures : chaque module de ce dossier traduit une mesure de programme en réforme OpenFisca.

Un module définit MESURE = Mesure(...). Sa fonction appliquer(reforme) reçoit la réforme OpenFisca en construction et
peut, comme dans toute réforme : changer des paramètres (reforme.modify_parameters), remplacer ou neutraliser une
variable (reforme.update_variable, reforme.neutralize_variable). Pour créer un impôt ou une prestation, elle passe par
ajouter_impot ou ajouter_prestation : le montant entre alors dans le revenu disponible, et plusieurs mesures se cumulent.
Une mesure sur les retraites donne en plus, ou seulement, retraites(parametres) : les paramètres du moteur de retraite
(simulator.retraites) qu'elle change, par dataclasses.replace.
Quand une source chiffre la mesure, cout dit ce qu'elle coûte ou rapporte aux finances publiques : le moteur en tire le budget du
scénario. Un financement sans effet calculable sur un foyer (économies de dépenses, impôt sur les entreprises) est une mesure comme une
autre, sans fonction appliquer et au coût négatif.
"""

import importlib
import pkgutil
from collections.abc import Callable
from dataclasses import dataclass

from openfisca_core.model_api import ADD, Variable
from openfisca_core.reforms import Reform
from openfisca_france.entities import Famille, FoyerFiscal

from simulator.retraites import Parametres


@dataclass(frozen=True)
class Cout:
    """Ce que la mesure coûte chaque année aux finances publiques, en milliards d'euros ; négatif quand elle rapporte."""

    bas: float  # le chiffrage le plus bas ; égal au plus haut quand une seule source chiffre
    haut: float
    source: str  # qui chiffre, et où
    # Une recette ou une économie que le candidat annonce ne compte qu'au rendement qu'une source fiable lui accorde au plus, et pour zéro sans
    # aucune évaluation fiable ; annonce garde alors ce que le candidat promet, en négatif comme le coût.
    annonce: float | None = None

    def __post_init__(self):
        assert self.bas <= self.haut and self.source, "un coût va du chiffrage le plus bas au plus haut et cite sa source"
        assert self.annonce is None or self.annonce <= self.bas <= self.haut <= 0, "une recette plafonnée ne rapporte pas plus que l'annonce"


@dataclass(frozen=True)
class Mesure:
    id: str
    titre: str
    candidats: tuple[str, ...]
    source: str  # URL du document du candidat qui porte la mesure
    citation: str  # la mesure telle que la source l'écrit
    traduction: str  # comment la mesure devient des paramètres OpenFisca, et les choix faits quand la source est muette
    appliquer: Callable[[Reform], None] = lambda reforme: None
    retraites: Callable[[Parametres], Parametres] | None = None
    a_confirmer: bool = False  # vrai tant que seule une source secondaire porte la mesure
    hypotheses: str = ""  # les effets que le calcul mécanique laisse de côté (comportements, répercussions)
    cout: Cout | None = None  # vide tant qu'aucune source ne chiffre la mesure


def ajouter_impot(reforme: Reform, variable: type[Variable]) -> None:
    """Crée un impôt : la variable donne le montant payé, positif, sur l'année ; il est retranché des impôts directs."""
    reforme.add_variable(variable)
    reforme.impots_ajoutes.append(variable)  # type: ignore[attr-defined]


def ajouter_prestation(reforme: Reform, variable: type[Variable]) -> None:
    """Crée une prestation (entité famille ou individu) : son montant annuel s'ajoute aux prestations sociales."""
    if variable.entity.key not in ("famille", "individu"):
        raise ValueError(f"{variable.__name__} : une prestation se verse à une famille ou à un individu.")
    reforme.add_variable(variable)
    reforme.prestations_ajoutees.append(variable)  # type: ignore[attr-defined]


def vers_menage(menage, variable: type[Variable], period):
    """Montant annuel de la variable, ramené au ménage."""
    entite, nom = variable.entity.key, variable.__name__
    if entite == "menage":
        return menage(nom, period, options=[ADD])
    if entite == "individu":
        return menage.sum(menage.members(nom, period, options=[ADD]))
    # Un foyer fiscal ou une famille compte une fois : par son déclarant principal ou son demandeur.
    if entite == "foyer_fiscal":
        return menage.sum(menage.members.foyer_fiscal(nom, period, options=[ADD]), role=FoyerFiscal.DECLARANT_PRINCIPAL)
    return menage.sum(menage.members.famille(nom, period, options=[ADD]), role=Famille.DEMANDEUR)


def vers_famille(famille, variable: type[Variable], period):
    """Montant annuel de la variable, ramené à la famille."""
    if variable.entity.key == "famille":
        return famille(variable.__name__, period, options=[ADD])
    return famille.sum(famille.members(variable.__name__, period, options=[ADD]))


def _decouvrir() -> dict[str, Mesure]:
    mesures = [importlib.import_module(f"{__name__}.{m.name}").MESURE for m in pkgutil.iter_modules(__path__)]
    catalogue = {m.id: m for m in mesures}
    assert len(catalogue) == len(mesures), "deux mesures portent le même id"
    return catalogue


CATALOGUE = _decouvrir()
