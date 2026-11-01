import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Depenses, Persona


def test_seules_l_electricite_et_le_gaz_passent_a_5_5_pourcent():
    depenses = Depenses(electricite=1200, gaz=600, fioul=300, autres_energies_logement=110, carburants=1500)
    persona = Persona(adultes=(Adulte(au_smic=True),), depenses=depenses)
    avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(Scenario(mesures=("tva_electricite_gaz_5_5",))), persona)
    # Prix hors taxe fixes : un euro TTC au taux normal porte 1 / 1,2 € hors taxe, qui paie 14,5 points de TVA de moins.
    assert apres["tva"] - avant["tva"] == pytest.approx((1200 + 600) / 1.2 * (0.2 - 0.055), abs=1)
    assert apres["revenu_disponible"] == avant["revenu_disponible"]
