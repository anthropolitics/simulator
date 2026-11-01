import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("csg_crds_deductibles",)))


def test_dans_la_tranche_a_30_pourcent_l_impot_baisse_de_30_pourcent_de_la_csg_et_de_la_crds_deduites():
    salarie = Persona(adultes=(Adulte(salaire_brut_mensuel=4000),))  # revenu imposable d'environ 35 000 €, dans la tranche à 30 %
    avant, apres = calculer(LOI_ACTUELLE, salarie), calculer(MESURE, salarie)
    deduites = (0.024 + 0.005) * 0.9825 * 4000 * 12  # CSG non déductible et CRDS : 1 367,64 € par an
    assert apres["impot_revenu"] - avant["impot_revenu"] == pytest.approx(0.30 * 0.9 * deduites, abs=2)  # après l'abattement de 10 % : 369,26 €
    assert {s: apres[s] for s in apres if s not in ("impot_revenu", "impots_directs", "revenu_disponible")} == {
        s: avant[s] for s in avant if s not in ("impot_revenu", "impots_directs", "revenu_disponible")
    }
