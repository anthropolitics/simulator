import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

MESURE = loi(Scenario(mesures=("annee_blanche_prestations_sociales",)))
REVALORISATION = 474.37 / 466.44  # base mensuelle des allocations familiales au 1er avril 2025, puis 2024 : +1,7 %


def parametres(date):
    return MESURE.parameters(date).prestations_sociales


def test_les_montants_perdent_leur_revalorisation_de_2025_toute_l_annee():
    assert parametres("2025-06-01").prestations_familiales.bmaf.bmaf == pytest.approx(466.44)  # montant d'avril 2024
    assert parametres("2025-02-01").prestations_familiales.bmaf.bmaf == pytest.approx(466.44 / REVALORISATION)
    assert parametres("2025-06-01").solidarite_insertion.minima_sociaux.rsa.rsa_m.montant_de_base_du_rsa == pytest.approx(635.71)
    loyer = parametres("2025-11-01").aides_logement.allocations_logement.locatif.formule.l_plafonds_loyers.par_zone.zone_2.personnes_seules
    assert loyer == pytest.approx(287.35)  # barème d'octobre 2024 au lieu de 290,34 €
    # Les petites retraites (minimum vieillesse) et les plafonds de ressources gardent leur revalorisation.
    assert parametres("2025-06-01").solidarite_insertion.minimum_vieillesse.aspa.montant_maximum_annuel.personnes_seules == 12_411.44
    assert parametres("2025-06-01").prestations_familiales.prestations_generales.af.af_cond_ress.plafond_tranche_1 == 78_565
    assert MESURE.parameters("2026-06-01").prestations_sociales.prestations_familiales.bmaf.bmaf == 478.16  # au-delà de 2025, rien ne change


def test_un_parent_seul_locataire_perd_une_revalorisation_sur_toutes_ses_prestations():
    parent = Persona(adultes=(Adulte(salaire_brut_mensuel=1000),), enfants=(4, 8), loyer_mensuel=650, code_commune="69123")
    avant, apres = calculer(LOI_ACTUELLE, parent), calculer(MESURE, parent)
    # Les prestations familiales sont des pourcentages de la base : elles baissent de 1,7 %.
    assert apres["prestations_familiales"] == pytest.approx(avant["prestations_familiales"] / REVALORISATION, abs=2)
    # RSA et prime d'activité complètent les ressources jusqu'à un montant garanti, qui baisse de 1,7 % : la prestation baisse davantage.
    assert 0 < apres["minima_sociaux"] < avant["minima_sociaux"] / REVALORISATION
    assert 0 < apres["aides_logement"] < avant["aides_logement"]
    perte = sum(avant[s] - apres[s] for s in ("prestations_familiales", "minima_sociaux", "aides_logement"))
    assert avant["revenu_disponible"] - apres["revenu_disponible"] == pytest.approx(perte, abs=2)
