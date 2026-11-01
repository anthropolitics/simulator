import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona


def test_seul_le_salaire_de_moins_de_2000_euros_net_paie_la_csg_a_2_5_pourcent():
    # 2 000 € brut, environ 1 560 € net : concerné ; 3 000 € brut, environ 2 340 € net : non.
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=2000), Adulte(salaire_brut_mensuel=3000)))
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(loi(Scenario(mesures=("csg_2_5_pourcent_salaires_moins_2000_net",))), couple)
    baisse = (0.092 - 0.025) * 0.9825 * 2000 * 12  # 6,7 points sur 98,25 % du salaire brut : 1 579,86 € par an
    assert apres["csg"] - avant["csg"] == pytest.approx(baisse, abs=1)
    assert apres["salaire_net"] - avant["salaire_net"] == pytest.approx(baisse, abs=1)
    # La CSG déductible disparue s'ajoute au revenu imposable : l'impôt monte, sans reprendre le gain.
    assert 0 < avant["impot_revenu"] - apres["impot_revenu"] < baisse
