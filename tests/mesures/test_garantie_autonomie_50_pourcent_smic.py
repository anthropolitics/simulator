import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.mesures.garantie_autonomie_50_pourcent_smic import montant
from simulator.persona import Adulte, Persona


def test_la_moitie_du_smic_net_de_2025():
    assert 2 * montant(11.88) == pytest.approx(1_426.30, abs=0.01)  # SMIC net mensuel publié pour 2025


def test_une_personne_seule_sans_revenu_touche_713_euros_par_mois():
    seul = Persona(adultes=(Adulte(),))
    avant, apres = calculer(LOI_ACTUELLE, seul), calculer(loi(Scenario(mesures=("garantie_autonomie_50_pourcent_smic",))), seul)
    prime_de_noel = 152.45  # versée aux allocataires du RSA, inchangée
    assert avant["minima_sociaux"] == round(3 * 635.71 + 9 * 646.52 + prime_de_noel)  # RSA revalorisé en avril 2025
    assert apres["minima_sociaux"] == round(12 * 713.15 + prime_de_noel)
    assert apres["revenu_disponible"] - avant["revenu_disponible"] == apres["minima_sociaux"] - avant["minima_sociaux"]
