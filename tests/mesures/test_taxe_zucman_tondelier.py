from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

FORTUNE = Persona(adultes=(Adulte(salaire_brut_mensuel=8000),), patrimoine_financier=150e6)


def test_meme_impot_que_chez_jean_luc_melenchon_compte_une_fois_si_les_deux_sont_choisis():
    tondelier = calculer(loi(Scenario(mesures=("taxe_zucman_tondelier",))), FORTUNE)
    assert tondelier["impots_mesures"] > 2_900_000
    assert calculer(loi(Scenario(mesures=("taxe_zucman_melenchon", "taxe_zucman_tondelier"))), FORTUNE) == tondelier


def test_sans_patrimoine_rien_ne_change():
    salarie = Persona(adultes=(Adulte(salaire_brut_mensuel=8000),))
    assert calculer(loi(Scenario(mesures=("taxe_zucman_tondelier",))), salarie) == calculer(LOI_ACTUELLE, salarie)
