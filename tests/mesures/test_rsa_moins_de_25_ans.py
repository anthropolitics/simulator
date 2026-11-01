import pytest

from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import ANNEE, Adulte, Persona

JEUNE_SANS_REVENU = Persona(adultes=(Adulte(age=22),))


def test_un_jeune_de_22_ans_sans_revenu_touche_le_rsa_d_une_personne_seule():
    assert calculer(LOI_ACTUELLE, JEUNE_SANS_REVENU)["minima_sociaux"] == 0
    parametres = [LOI_ACTUELLE.parameters(f"{ANNEE}-{mois:02d}-01").prestations_sociales.solidarite_insertion.minima_sociaux for mois in range(1, 13)]
    forfaitaire = sum(p.rsa.rsa_m.montant_de_base_du_rsa for p in parametres)
    # Montant forfaitaire d'une personne seule sans ressources, sans forfait logement (ni loyer ni aide), et prime de Noël de 152,45 €.
    assert calculer(loi(Scenario(mesures=("rsa_moins_de_25_ans",))), JEUNE_SANS_REVENU)["minima_sociaux"] == pytest.approx(forfaitaire + 152.45, abs=1)
