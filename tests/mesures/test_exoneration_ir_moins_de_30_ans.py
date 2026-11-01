import pytest
from openfisca_core.simulation_builder import SimulationBuilder

from simulator.engine import SMIC_ACTUEL, Scenario, calculer, loi
from simulator.persona import Adulte, Persona, situation

SCENARIO = Scenario(mesures=("exoneration_ir_moins_de_30_ans",))
PLAFOND = 4 * 11.88 * 1820  # quatre SMIC annuels bruts de 2025 : 86 486,40 €


def test_un_salarie_de_25_ans_sous_le_plafond_ne_paie_plus_d_impot():
    # 3 000 € brut par mois : environ 28 000 € de salaire imposable, imposé aujourd'hui ; tout est sous le plafond.
    assert calculer(loi(SCENARIO), Persona(adultes=(Adulte(age=25, salaire_brut_mensuel=3000),)))["impot_revenu"] == 0


def test_le_plafond_et_l_age_s_appliquent_a_chaque_conjoint():
    # Le conjoint de 25 ans n'est imposé qu'au-delà de quatre SMIC ; celui de 35 ans, sur tout son salaire.
    couple = Persona(adultes=(Adulte(age=25, salaire_brut_mensuel=10_000), Adulte(age=35, salaire_brut_mensuel=3000)))
    simulation = SimulationBuilder().build_from_entities(loi(SCENARIO), situation(couple, SMIC_ACTUEL, SMIC_ACTUEL))
    imposable = simulation.calculate_add("salaire_imposable", "2025")
    assert imposable[0] > PLAFOND
    assert list(simulation.calculate("revenu_assimile_salaire", "2025")) == pytest.approx([imposable[0] - PLAFOND, imposable[1]])
