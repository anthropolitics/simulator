"""Ce que le programme de chaque candidat change pour chaque ménage type, tel que le catalogue le traduit.

    uv run python -m simulator.tableau > tableau.json

Le programme d'un candidat, ce sont toutes les mesures du catalogue qui le citent : rien de ce que le catalogue n'a pas encore traduit.
"""

import json
import subprocess
import sys
import unicodedata

from simulator.engine import VERSIONS, Scenario, simuler
from simulator.menages import MENAGES, Menage
from simulator.mesures import CATALOGUE
from simulator.persona import ANNEE


def programmes() -> dict[str, tuple[str, ...]]:
    """Mesures du catalogue de chaque candidat, dans l'ordre alphabétique du nom de famille, comme le veut la charte."""
    # Le nom suit le premier prénom, composé ou non : « Marine Le Pen » se range à Le Pen, « Édouard Philippe » à Philippe.
    candidats = sorted({c for m in CATALOGUE.values() for c in m.candidats}, key=lambda c: unicodedata.normalize("NFD", c.split(" ", 1)[1]))
    return {c: tuple(i for i, m in CATALOGUE.items() if c in m.candidats) for c in candidats}


# Les postes du revenu que le site décompose, avant et après : l'écart de pouvoir d'achat est celui du revenu disponible et de la TVA.
POSTES = ("salaire_net", "retraite_nette", "impots_directs", "prestations_sociales", "revenu_disponible", "tva")


def ligne(candidat: str, menage: str, r: dict) -> dict:
    """Une ligne du tableau : ce que le programme d'un candidat change pour un ménage, poste par poste."""
    return {
        "candidat": candidat,
        "menage": menage,
        "ecart_pouvoir_achat": r["ecart_pouvoir_achat"],
        "ecart_revenu_disponible": r["ecart_revenu_disponible"],
        "avant": {poste: r["avant"][poste] for poste in POSTES},
        "apres": {poste: r["apres"][poste] for poste in POSTES},
        "retraites": [avant and {"avant": avant, "apres": apres} for avant, apres in zip(r["avant"]["retraites"], r["apres"]["retraites"])],
    }


def persona_publie(menage: Menage) -> dict:
    """Le foyer tel que la page le pré-remplit : la commune compte, puisqu'un loyer la rend obligatoire.

    Sans elle, le formulaire pré-rempli est invalide et le calcul ne part pas ; et la commune fixe la zone des aides au logement,
    donc le foyer saisi ne reproduirait pas le ménage type.
    """
    return menage.persona.model_dump(mode="json", include={"adultes", "enfants", "loyer_mensuel", "code_commune"})


def tableau() -> dict:
    resultats = []
    for candidat, mesures in programmes().items():  # le candidat d'abord : la réforme de son programme ne se construit qu'une fois
        for menage in MENAGES.values():
            resultats.append(ligne(candidat, menage.id, simuler(menage.persona, Scenario(mesures=mesures))))
    # Le commit qui a produit le tableau, pour le rejouer ; « -dirty » si le code avait des modifications non commitées.
    commit = subprocess.run(["git", "describe", "--always", "--dirty"], check=True, capture_output=True, text=True).stdout.strip()
    return {
        "annee": int(ANNEE),
        "commit": commit,
        "versions": VERSIONS,
        "programmes": [
            {"candidat": c, "mesures": [{"id": i, "titre": CATALOGUE[i].titre, "a_confirmer": CATALOGUE[i].a_confirmer} for i in m]}
            for c, m in programmes().items()
        ],
        "menages": [
            {
                "id": m.id,
                "prenom": m.prenom,
                "situation": m.situation,
                "couleur": m.couleur,
                "sources": m.sources,
                "persona": persona_publie(m),
            }
            for m in MENAGES.values()
        ],
        "resultats": resultats,
    }


if __name__ == "__main__":
    json.dump(tableau(), sys.stdout, ensure_ascii=False, indent=1)
