import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("compte_social_unique_70_pourcent_smic",)))
PLAFOND_COUPLE = 2 * 0.7 * 1426.30 * 12  # 70 % du SMIC net par adulte : 998,41 € par mois chacun, 23 961,84 € par an


def test_au_dela_de_70_pourcent_du_smic_net_par_adulte_les_aides_sont_retenues():
    # Couple sans emploi, trois enfants, locataire : RSA, allocations familiales, complément familial et aide au logement dépassent le plafond.
    couple = Persona(adultes=(Adulte(), Adulte()), enfants=(3, 6, 9), loyer_mensuel=800, code_commune="69123")
    avant, apres = calculer(LOI_ACTUELLE, couple), calculer(MESURE, couple)
    aides = avant["prestations_familiales"] + avant["minima_sociaux"] + avant["aides_logement"]
    assert aides > PLAFOND_COUPLE
    assert apres["prestations_mesures"] == pytest.approx(PLAFOND_COUPLE - aides, abs=1)
    assert apres["prestations_sociales"] == pytest.approx(PLAFOND_COUPLE, abs=1)
    # Chaque aide garde son montant : seul le total est ramené au plafond.
    assert {s: apres[s] for s in apres if s not in ("prestations_mesures", "prestations_sociales", "revenu_disponible")} == {
        s: avant[s] for s in avant if s not in ("prestations_mesures", "prestations_sociales", "revenu_disponible")
    }
