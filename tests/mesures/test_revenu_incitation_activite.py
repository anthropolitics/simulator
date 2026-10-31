import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("revenu_incitation_activite",)))


def complement(salaire_net_annuel):
    return max(12 * 550 - 0.3 * salaire_net_annuel, 0)


def test_ria_socle_de_300_euros_sans_activite_ni_revenu_a_la_place_du_rsa():
    sans_revenu = Persona(adultes=(Adulte(),))
    avant, apres = calculer(LOI_ACTUELLE, sans_revenu), calculer(MESURE, sans_revenu)
    assert apres["prestations_mesures"] == 300 * 12
    assert apres["minima_sociaux"] == 0 < avant["minima_sociaux"]


def test_au_travail_le_ria_vaut_550_euros_moins_30_pourcent_du_salaire_et_remplace_la_prime_d_activite():
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, au_smic), calculer(MESURE, au_smic)
    assert apres["prestations_mesures"] == pytest.approx(complement(apres["salaire_net"]), abs=1)
    assert apres["minima_sociaux"] == 0 < avant["minima_sociaux"]


def test_chaque_adulte_le_recoit_sans_regard_pour_son_conjoint():
    couple = Persona(adultes=(Adulte(salaire_brut_mensuel=2000), Adulte()))
    apres = calculer(MESURE, couple)
    assert apres["prestations_mesures"] == pytest.approx(300 * 12 + complement(apres["salaire_net"]), abs=1)


@pytest.mark.parametrize(
    "persona",
    [
        Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=1500),)),
        Persona(adultes=(Adulte(salaire_brut_mensuel=5000),), enfants=(20,)),  # haut salaire, enfant majeur à charge sans revenu
    ],
)
def test_retraite_et_haut_salaire_ne_sont_pas_concernes(persona):
    assert calculer(MESURE, persona) == calculer(LOI_ACTUELLE, persona)


def test_ria_insertion_de_250_euros_sans_salaire_avec_15_heures_de_formation_ou_de_recherche_d_emploi():
    assert calculer(MESURE, Persona(adultes=(Adulte(insertion_15h=True),)))["prestations_mesures"] == 550 * 12
    # Avec un salaire, le complément compte déjà le RIA Insertion.
    assert calculer(MESURE, Persona(adultes=(Adulte(au_smic=True, insertion_15h=True),))) == calculer(MESURE, Persona(adultes=(Adulte(au_smic=True),)))
