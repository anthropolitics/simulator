import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona


def test_la_retraite_nette_augmente_de_10_pourcent_et_ses_prelevements_avec():
    # 3 500 € brut par mois : CSG au taux plein (8,3 %) avant comme après la hausse, avec la CRDS (0,5 %) et la CASA (0,3 %).
    retraite = Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=3500),))
    avant, apres = calculer(LOI_ACTUELLE, retraite), calculer(loi(Scenario(mesures=("pensions_plus_10_pourcent",))), retraite)
    assert avant["retraite_nette"] == round(12 * 3500 * (1 - 0.083 - 0.005 - 0.003))
    assert apres["retraite_nette"] == pytest.approx(1.1 * avant["retraite_nette"], abs=1)
    assert apres["csg"] == pytest.approx(1.1 * avant["csg"], abs=1)
    assert apres["impot_revenu"] < avant["impot_revenu"]  # l'impôt, négatif, suit la pension imposable
