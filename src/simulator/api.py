"""API publique du simulateur : https://api.anthropolitics.fr/docs"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from simulator import engine

app = FastAPI(
    title="anthropolitics simulator",
    summary="Ce qu'une réforme change pour un foyer, calculé avec OpenFisca-France.",
    license_info={"name": "AGPL-3.0", "identifier": "AGPL-3.0-only"},
)
# API ouverte : n'importe quel site peut l'appeler depuis un navigateur.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["POST"], allow_headers=["Content-Type"])


class Persona(BaseModel):
    salaire_brut_mensuel: float = Field(ge=0, le=100_000)
    salaire_brut_mensuel_conjoint: float | None = Field(default=None, ge=0, le=100_000, description="Absent si la personne vit seule.")
    enfants: int = Field(default=0, ge=0, le=6)


class Scenario(BaseModel):
    taux_troisieme_tranche_ir: float = Field(ge=0, le=0.6, description="Taux de la tranche à 30 % du barème de l'impôt sur le revenu, entre 0 et 0,6.")


class Simulation(BaseModel):
    persona: Persona
    scenario: Scenario


class Montants(BaseModel):
    salaire_net: int
    impots_directs: int = Field(description="Négatif : ce que le foyer paie.")
    prestations_sociales: int
    revenu_disponible: int


class Resultat(BaseModel):
    annee: int
    avant: Montants = Field(description="Loi actuelle, en euros par an.")
    apres: Montants = Field(description="Avec le scénario, en euros par an.")
    ecart_revenu_disponible: int
    versions: dict[str, str] = Field(description="Versions du code qui a produit le résultat, pour le rejouer.")


@app.post("/simulation")
def simulation(demande: Simulation) -> Resultat:
    p = demande.persona
    salaires = [p.salaire_brut_mensuel] + ([] if p.salaire_brut_mensuel_conjoint is None else [p.salaire_brut_mensuel_conjoint])
    return engine.simuler(salaires, p.enfants, demande.scenario.taux_troisieme_tranche_ir)
