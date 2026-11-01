"""Ce que le programme de chaque candidat change pour chaque ménage type, tel que le catalogue le traduit.

    uv run python -m simulator.tableau > tableau.json

Le programme d'un candidat, ce sont toutes les mesures du catalogue qui le citent : rien de ce que le catalogue n'a pas encore traduit.
"""

import json
import subprocess
import sys
import unicodedata

from simulator.engine import VERSIONS, Scenario, simuler
from simulator.menages import MENAGES
from simulator.mesures import CATALOGUE
from simulator.persona import ANNEE


def programmes() -> dict[str, tuple[str, ...]]:
    """Mesures du catalogue de chaque candidat, dans l'ordre alphabétique du nom de famille, comme le veut la charte."""
    # Le nom suit le premier prénom, composé ou non : « Marine Le Pen » se range à Le Pen, « Édouard Philippe » à Philippe.
    candidats = sorted({c for m in CATALOGUE.values() for c in m.candidats}, key=lambda c: unicodedata.normalize("NFD", c.split(" ", 1)[1]))
    return {c: tuple(i for i, m in CATALOGUE.items() if c in m.candidats) for c in candidats}


# Les postes du revenu que le site décompose, avant et après : l'écart de pouvoir d'achat est celui du revenu disponible et de la TVA.
POSTES = ("salaire_net", "retraite_nette", "impots_directs", "prestations_sociales", "revenu_disponible", "tva")


def tableau() -> dict:
    resultats = []
    for candidat, mesures in programmes().items():  # le candidat d'abord : la réforme de son programme ne se construit qu'une fois
        for menage in MENAGES.values():
            r = simuler(menage.persona, Scenario(mesures=mesures))
            resultats.append(
                {
                    "candidat": candidat,
                    "menage": menage.id,
                    "ecart_pouvoir_achat": r["ecart_pouvoir_achat"],
                    "ecart_revenu_disponible": r["ecart_revenu_disponible"],
                    "avant": {poste: r["avant"][poste] for poste in POSTES},
                    "apres": {poste: r["apres"][poste] for poste in POSTES},
                    "retraites": [avant and {"avant": avant, "apres": apres} for avant, apres in zip(r["avant"]["retraites"], r["apres"]["retraites"])],
                }
            )
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
                "persona": m.persona.model_dump(mode="json", include={"adultes", "enfants", "loyer_mensuel"}),
            }
            for m in MENAGES.values()
        ],
        "resultats": resultats,
    }


if __name__ == "__main__":
    json.dump(tableau(), sys.stdout, ensure_ascii=False, indent=1)
