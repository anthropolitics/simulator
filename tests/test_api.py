import json

from fastapi.testclient import TestClient

from simulator import api, engine
from simulator.api import LIMITE, app, appels, appels_programmes
from simulator.menages import MENAGES
from simulator.tableau import POSTES

client = TestClient(app)


def faux_resultat(scenario):
    postes = {poste: 0 for poste in POSTES}
    postes["revenu_disponible"] = 1000 + len(scenario.mesures)
    postes["tva"] = -100
    avant = postes | {"retraites": [None]}
    return {"ecart_pouvoir_achat": 10, "ecart_revenu_disponible": 7, "avant": avant, "apres": avant}


def test_simulation():
    r = client.post("/simulation", json={"persona": {"salaire_brut_mensuel": 3000, "enfants": 1}, "scenario": {"taux_troisieme_tranche_ir": 0.35}})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"annee", "mesures", "avant", "apres", "ecart_revenu_disponible", "ecart_pouvoir_achat", "versions"}
    assert body["versions"]["openfisca-france"]


def test_entree_invalide_refusee():
    r = client.post("/simulation", json={"persona": {"salaire_brut_mensuel": -1}, "scenario": {"taux_troisieme_tranche_ir": 0.3}})
    assert r.status_code == 422


def test_limite_de_calculs_par_adresse():
    appels.clear()
    demande = {"persona": {"salaire_brut_mensuel": 2500}, "scenario": {"taux_troisieme_tranche_ir": 0.3}}
    codes = [client.post("/simulation", json=demande).status_code for _ in range(LIMITE + 1)]
    assert codes == [200] * LIMITE + [429]


def test_mesure_inconnue_refusee():
    appels.clear()
    r = client.post("/simulation", json={"persona": {"salaire_brut_mensuel": 2500}, "scenario": {"mesures": ["n_existe_pas"]}})
    assert r.status_code == 422


def test_catalogue_des_mesures():
    r = client.get("/mesures")
    assert r.status_code == 200 and isinstance(r.json(), list)


def test_catalogue_des_menages():
    r = client.get("/menages")
    assert r.status_code == 200 and [m["id"] for m in r.json()] == list(MENAGES)


def test_les_programmes_pour_un_foyer_saisi(monkeypatch):
    appels_programmes.clear()
    monkeypatch.setattr(engine, "simuler", lambda persona, scenario: faux_resultat(scenario))
    r = client.post("/programmes", json={"persona": {"adultes": [{"salaire_brut_mensuel": 2000}], "enfants": [8]}})
    assert r.status_code == 200
    lignes = [json.loads(ligne) for ligne in r.iter_lines()]
    assert len(lignes) == len(api.programmes())
    assert {ligne["candidat"] for ligne in lignes} == set(api.programmes())
    assert all(ligne["menage"] == "vous" and set(ligne["avant"]) == set(POSTES) for ligne in lignes)
    assert all(ligne["ecart_pouvoir_achat"] == 10 for ligne in lignes)


def test_les_programmes_refusent_un_foyer_invalide():
    r = client.post("/programmes", json={"persona": {"adultes": [{"age": 12}]}})
    assert r.status_code == 422


def test_limite_des_calculs_de_programmes(monkeypatch):
    appels_programmes.clear()
    monkeypatch.setattr(engine, "simuler", lambda persona, scenario: faux_resultat(scenario))
    demande = {"persona": {"adultes": [{"salaire_brut_mensuel": 2000}]}}
    codes = [client.post("/programmes", json=demande).status_code for _ in range(api.PROGRAMMES_LIMITE + 1)]
    assert codes == [200] * api.PROGRAMMES_LIMITE + [429]
