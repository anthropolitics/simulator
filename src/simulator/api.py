"""API publique du simulateur : https://api.anthropolitics.fr/docs"""

from collections import defaultdict, deque
from contextlib import asynccontextmanager
from time import monotonic

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from simulator import engine
from simulator.engine import Scenario
from simulator.mesures import CATALOGUE
from simulator.persona import Adulte, Persona


@asynccontextmanager
async def demarrage(app: FastAPI):
    # Lance les deux processus de calcul sans attendre : le premier visiteur ne paie pas leur démarrage (environ 4 s).
    for role in ("loi actuelle", "scenario"):
        engine.lancer(role, Scenario(), Persona(adultes=(Adulte(salaire_brut_mensuel=2500),)))
    yield


app = FastAPI(
    lifespan=demarrage,
    title="anthropolitics simulator",
    summary="Ce qu'une réforme change pour un foyer, calculé avec OpenFisca-France.",
    license_info={"name": "AGPL-3.0", "identifier": "AGPL-3.0-only"},
)
# API ouverte : n'importe quel site peut l'appeler depuis un navigateur.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


# shortcut: compteur en mémoire, par processus, jamais purgé des adresses passées ; passer au proxy ou à Redis si le trafic grossit.
LIMITE, FENETRE = 10, 60  # calculs par adresse IP et par minute : un calcul occupe un cœur pendant plusieurs secondes
appels: dict[str, deque] = defaultdict(deque)


def limiter(request: Request):
    # Sans adresse (socket Unix), les appels partagent un même compteur.
    maintenant, recents = monotonic(), appels[request.client.host if request.client else ""]
    while recents and maintenant - recents[0] > FENETRE:
        recents.popleft()
    if len(recents) >= LIMITE:
        raise HTTPException(429, "Trop de calculs : réessayez dans une minute.", headers={"Retry-After": str(FENETRE)})
    recents.append(maintenant)


class Montants(BaseModel):
    salaire_net: int
    retraite_nette: int
    csg: int = Field(description="Négatif : ce que le foyer paie, déjà retranché des revenus nets.")
    impot_revenu: int = Field(description="Négatif : ce que le foyer paie.")
    impots_mesures: int = Field(description="Impôts créés par les mesures du scénario, comptés dans les impôts directs.")
    impots_directs: int = Field(description="Négatif : ce que le foyer paie.")
    prestations_familiales: int
    minima_sociaux: int
    aides_logement: int
    prestations_mesures: int = Field(description="Prestations créées par les mesures du scénario, comptées dans les prestations sociales.")
    prestations_sociales: int
    revenu_disponible: int
    cout_du_travail: int = Field(description="Ce que l'emploi des adultes coûte à leurs employeurs.")


class Simulation(BaseModel):
    persona: Persona
    scenario: Scenario


class Resultat(BaseModel):
    annee: int
    mesures: list[str]
    avant: Montants = Field(description="Loi actuelle, en euros par an.")
    apres: Montants = Field(description="Avec le scénario, en euros par an.")
    ecart_revenu_disponible: int
    versions: dict[str, str] = Field(description="Versions du code qui a produit le résultat, pour le rejouer.")


class MesureDecrite(BaseModel):
    id: str
    titre: str
    candidats: list[str]
    source: str
    citation: str
    traduction: str
    a_confirmer: bool = Field(description="Vrai tant que seule une source secondaire porte la mesure.")
    hypotheses: str = Field(description="Les effets que le calcul mécanique laisse de côté.")


@app.get("/mesures", response_model=list[MesureDecrite])
def mesures() -> list[dict]:
    return [{k: v for k, v in vars(m).items() if k != "appliquer"} for m in CATALOGUE.values()]


@app.post("/simulation", response_model=Resultat, dependencies=[Depends(limiter)])
def simulation(demande: Simulation) -> dict:  # FastAPI valide le dict du moteur contre Resultat
    return engine.simuler(demande.persona, demande.scenario)
