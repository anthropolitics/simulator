import pytest

from simulator.consommation import POSTES
from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, DepensesEnergie, Persona

SCENARIO = Scenario(mesures=("tva_energie_5_5",))


def test_la_tva_payee_sur_l_energie_baisse_a_5_5_pourcent():
    depenses = DepensesEnergie(electricite=1200, gaz=600, fioul=0, autres_energies_logement=110, carburants=1500)
    persona = Persona(adultes=(Adulte(au_smic=True),), depenses_energie=depenses)
    avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(SCENARIO), persona)
    attendu = (1200 + 600 + 1500) / 1.2 * (0.2 - 0.055) + 110 / 1.1 * (0.1 - 0.055)
    assert apres["tva"] - avant["tva"] == pytest.approx(attendu, abs=1)
    assert apres["revenu_disponible"] == avant["revenu_disponible"]


def test_sans_depense_d_energie_rien_ne_change():
    persona = Persona(adultes=(Adulte(au_smic=True),), depenses_energie=DepensesEnergie(**{poste: 0 for poste in POSTES}))
    assert calculer(loi(SCENARIO), persona) == calculer(LOI_ACTUELLE, persona)
