from simulator.engine import LOI_ACTUELLE, Scenario, calculer, loi
from simulator.persona import Adulte, Persona

SCENARIO = Scenario(mesures=("ir_14_tranches",))


def test_un_cadre_paie_le_bareme_a_14_tranches():
    cadre = Persona(adultes=(Adulte(salaire_brut_mensuel=8000),))
    avant, apres = calculer(LOI_ACTUELLE, cadre), calculer(loi(SCENARIO), cadre)
    rni = 71_261.12  # revenu net imposable, une part : le barème 2025 retrouve l'impôt actuel
    assert avant["impot_revenu"] == -round(0.11 * (29_579 - 11_600) + 0.30 * (rni - 29_579))
    tranches_pleines = 0.03 * 7_200 + 0.04 * 3_600 + 0.065 * 4_800 + 0.085 * 3_600 + 0.105 * 3_600 + 0.125 * 4_800 + 0.23 * 4_800 + 0.25 * 4_800
    assert apres["impot_revenu"] == -round(tranches_pleines + 0.29 * 6_000 + 0.32 * 16_800 + 0.40 * (rni - 60_000))
    assert apres["csg"] == avant["csg"]


def test_au_smic_la_decote_de_2025_s_applique_au_nouveau_bareme():
    au_smic = Persona(adultes=(Adulte(au_smic=True),))
    avant, apres = calculer(LOI_ACTUELLE, au_smic), calculer(loi(SCENARIO), au_smic)
    impot_brut = 0.03 * 7_200 + 0.04 * 3_600 + 0.065 * 4_800 + 0.085 * (15_958.58 - 15_600)  # revenu net imposable de 15 958,58 €
    assert avant["impot_revenu"] == 0
    assert apres["impot_revenu"] == -round(impot_brut - (897 - 0.4525 * impot_brut))  # décote d'une personne seule


def test_sous_la_decote_rien_ne_change():
    retraite = Persona(adultes=(Adulte(age=70, retraite_brute_mensuelle=1000),))
    assert calculer(loi(SCENARIO), retraite) == calculer(LOI_ACTUELLE, retraite)
