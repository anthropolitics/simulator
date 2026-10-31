"""Ménages types : des foyers calés sur les statistiques de l'Insee, pour publier ce que chaque programme leur fait.

Chaque ménage dit d'où vient chacune de ses valeurs. Un ménage par couleur de la charte : il la garde partout où il apparaît.
"""

from dataclasses import dataclass

from simulator.persona import Persona


@dataclass(frozen=True)
class Menage:
    id: str
    prenom: str
    situation: str  # « Métier, ville, foyer », dans l'ordre de la charte
    couleur: str  # ocre, ardoise, sauge, prune, argile ou lin
    persona: Persona
    sources: str  # la source de chaque valeur du persona, et les choix faits quand elle manque


MENAGES: dict[str, Menage] = {}
