import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import ANNEE, Adulte, Persona


def test_les_allocations_familiales_augmentent_de_10_pourcent():
    # Deux enfants de moins de 14 ans : allocations familiales de 32 % de la base mensuelle (BMAF), sans majoration pour âge.
    famille = Persona(adultes=(Adulte(salaire_brut_mensuel=3000), Adulte(salaire_brut_mensuel=3000)), enfants=(5, 8))
    avant, apres = calculer(LOI_ACTUELLE, famille), calculer(loi(Scenario(mesures=("allocations_familiales_plus_10_pourcent",))), famille)
    bmaf = [LOI_ACTUELLE.parameters(f"{ANNEE}-{mois:02d}-01").prestations_sociales.prestations_familiales.bmaf.bmaf for mois in range(1, 13)]
    hausse = 0.1 * 0.32 * sum(bmaf)
    assert apres["prestations_familiales"] - avant["prestations_familiales"] == pytest.approx(hausse, abs=1)
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == pytest.approx(hausse, abs=1)  # ni imposables, ni dans d'autres ressources ici
