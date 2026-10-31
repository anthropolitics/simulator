import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Depenses, Persona

SCENARIO = Scenario(mesures=("tva_sociale",))


def test_la_tva_monte_de_1_5_point_sur_les_seules_depenses_au_taux_normal():
    depenses = Depenses(
        electricite=1200,
        gaz=600,
        fioul=0,
        autres_energies_logement=110,
        carburants=1500,
        hors_energie_taux_normal=12_000,
        hors_energie_taux_intermediaire=3000,
        hors_energie_taux_reduit=4000,
        hors_energie_taux_particulier=100,
    )
    persona = Persona(adultes=(Adulte(au_smic=True),), depenses=depenses)
    avant, apres = calculer(LOI_ACTUELLE, persona), calculer(loi(SCENARIO), persona)
    au_taux_normal = 1200 + 600 + 1500 + 12_000
    assert avant["tva"] == pytest.approx(-(au_taux_normal / 1.2 * 0.2 + (110 + 3000) / 1.1 * 0.1 + 4000 / 1.055 * 0.055 + 100 / 1.021 * 0.021), abs=1)
    # Prix hors taxe fixes : un euro TTC au taux normal porte 1 / 1,2 € hors taxe, qui paie 1,5 point de plus.
    assert apres["tva"] - avant["tva"] == pytest.approx(-au_taux_normal / 1.2 * 0.015, abs=1)
    assert apres["revenu_disponible"] == avant["revenu_disponible"] and apres["cout_du_travail"] == avant["cout_du_travail"]
