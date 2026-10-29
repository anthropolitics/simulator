import pytest

from simulator import engine


@pytest.fixture(autouse=True, scope="session")
def arreter_les_processus_de_calcul():
    yield
    # Arrêtés avant la fin de la session, ils écrivent leur couverture à temps pour le rapport.
    for processus in engine.PROCESSUS.values():
        processus.shutdown()
