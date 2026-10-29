from fastapi.testclient import TestClient

from simulator.api import LIMITE, app, appels

client = TestClient(app)


def test_simulation():
    r = client.post("/simulation", json={"persona": {"salaire_brut_mensuel": 3000, "enfants": 1}, "scenario": {"taux_troisieme_tranche_ir": 0.35}})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"annee", "avant", "apres", "ecart_revenu_disponible", "versions"}
    assert body["versions"]["openfisca-france"]


def test_entree_invalide_refusee():
    r = client.post("/simulation", json={"persona": {"salaire_brut_mensuel": -1}, "scenario": {"taux_troisieme_tranche_ir": 0.3}})
    assert r.status_code == 422


def test_limite_de_calculs_par_adresse():
    appels.clear()
    demande = {"persona": {"salaire_brut_mensuel": 2500}, "scenario": {"taux_troisieme_tranche_ir": 0.3}}
    codes = [client.post("/simulation", json=demande).status_code for _ in range(LIMITE + 1)]
    assert codes == [200] * LIMITE + [429]
