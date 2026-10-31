import pytest
from pytest import approx

from simulator import engine
from simulator.mesures.retraite_60_ans_40_annuites import MESURE, retraites
from simulator.persona import Adulte, Persona
from simulator.retraites import PARAMETRES_ACTUELS, depart

PARAMETRES = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40
MINIMUM = 1835.85  # 1 700 € net / (1 - 6,6 % - 0,5 % - 0,3 %)


def test_parametres():
    assert (PARAMETRES.age_legal_cible, PARAMETRES.duree_requise_cible, PARAMETRES.minimum_pension) == (60 * 12, 160, MINIMUM)
    assert MINIMUM * (1 - 0.066 - 0.005 - 0.003) == approx(1700, abs=0.01)


def test_smic_debut_a_21_ans_ne_en_1985():
    avant, apres = depart(1985, 21, SMIC_ANNUEL), depart(1985, 21, SMIC_ANNUEL, parametres=PARAMETRES)
    assert (avant.age_annees, avant.trimestres, avant.pension_mensuelle) == (64, 172, approx(1243.21, abs=0.01))
    # 40 ans de cotisation mènent aux 160 trimestres à 61 ans, après l'âge légal de 60 ans.
    assert (apres.age_annees, apres.age_mois, apres.trimestres, apres.taux) == (61, 0, 160, 0.5)
    # 900,90 € au régime général et 40 × 66,40 points à 1,4386 € (318,43 €), soit 1 219,33 € : relevés au minimum de 1 835,85 €.
    assert apres.agirc_arrco == approx(POINTS_SMIC * 40 * 1.4386 / 12)
    assert apres.regime_general == approx(MINIMUM - apres.agirc_arrco)
    assert apres.pension_mensuelle == approx(MINIMUM)
    assert apres.cumul == approx(MINIMUM * 12 * 25.1)  # espérance de vie à 61 ans : (27,1 + 23,1) / 2


def test_ne_en_1964_debut_a_20_ans():
    # 62 ans et 9 mois avec 171 trimestres aujourd'hui ; les 160 trimestres sont là à 60 ans.
    assert (depart(1964, 20, SMIC_ANNUEL).age_annees, depart(1964, 20, SMIC_ANNUEL).age_mois) == (62, 9)
    d = depart(1964, 20, SMIC_ANNUEL, parametres=PARAMETRES)
    assert (d.age_annees, d.age_mois, d.trimestres, d.pension_mensuelle) == (60, 0, 160, approx(MINIMUM))


def test_depart_a_60_ans_avec_decote():
    # Début à 22 ans : le taux plein vient à 62 ans.
    assert depart(1985, 22, SMIC_ANNUEL, parametres=PARAMETRES).age_annees == 62
    with pytest.raises(ValueError, match="âge légal"):
        depart(1985, 22, SMIC_ANNUEL, age_depart=60 * 12)
    # À 60 ans : 152 trimestres, 8 manquent, décote de 10 % ; pas de minimum avec une décote.
    d = depart(1985, 22, SMIC_ANNUEL, parametres=PARAMETRES, age_depart=60 * 12)
    assert (d.trimestres, d.taux) == (152, approx(0.45))
    assert d.regime_general == approx(SMIC_ANNUEL * 0.45 * 152 / 160 / 12)  # 770,27 €
    assert d.agirc_arrco == approx(POINTS_SMIC * 38 * 1.4386 * 0.92 / 12)  # coefficient de 0,92 pour 8 trimestres manquants


def test_carriere_longue_avant_16_ans():
    # Début à 15 ans : 58 ans avant comme après, la borne des 16 ans demandant la durée requise cotisée, atteinte à 55 ans avec 160 trimestres.
    avant, apres = depart(1985, 15, SMIC_ANNUEL), depart(1985, 15, SMIC_ANNUEL, parametres=PARAMETRES)
    assert (avant.age_annees, apres.age_annees, apres.trimestres) == (58, 58, 172)
    assert (avant.pension_mensuelle, apres.pension_mensuelle) == (approx(1243.21, abs=0.01), approx(MINIMUM))


def test_carriere_incomplete_minimum_au_prorata():
    # Début à 22 ans et 8 ans sans emploi : taux plein à 67 ans avec 148 trimestres, avant comme après.
    avant = depart(1985, 22, SMIC_ANNUEL, 8)
    apres = depart(1985, 22, SMIC_ANNUEL, 8, PARAMETRES)
    assert (avant.age_annees, apres.age_annees, apres.trimestres) == (67, 67, 148)
    assert avant.pension_mensuelle == approx(900.90 * 148 / 172 + POINTS_SMIC * 37 * 1.4386 / 12)  # 1 069,74 €
    assert apres.pension_mensuelle == approx(MINIMUM * 148 / 160)  # 1 698,16 €


def test_cadre_au_dessus_du_plafond():
    # 80 000 € par an dès 23 ans : 63 ans au lieu de 66 ; même pension maximale au régime général, 3 ans de points en moins.
    avant, apres = depart(1985, 23, 80_000), depart(1985, 23, 80_000, parametres=PARAMETRES)
    assert (avant.age_annees, apres.age_annees, apres.trimestres) == (66, 63, 160)
    assert apres.regime_general == approx(1962.50)
    assert apres.agirc_arrco == approx(avant.agirc_arrco * 40 / 43)
    assert apres.pension_mensuelle == approx(3984.70, abs=0.01)  # au-dessus du minimum
    # Espérance de vie à 63 ans : (25,3 + 21,5) / 2 = 23,4 ans, contre (22,7 + 19,2) / 2 = 20,95 ans à 66 ans.
    assert apres.cumul == approx(apres.pension_mensuelle * 12 * 23.4)
    assert apres.cumul > avant.cumul


def test_persona_au_smic():
    # 40 ans en 2025, né en 1985, premier emploi à 22 ans : 65 ans et 1 243 € aujourd'hui, 62 ans et le minimum ensuite.
    persona = Persona(adultes=(Adulte(age=40, au_smic=True),))
    avant = engine.retraites(persona, engine.SMIC_ACTUEL, PARAMETRES_ACTUELS)
    apres = engine.retraites(persona, engine.SMIC_ACTUEL, PARAMETRES)
    assert avant == [{"age_annees": 65, "age_mois": 0, "pension_mensuelle": 1243, "cumul": 325224}]
    # Espérance de vie à 62 ans : (26,2 + 22,3) / 2 = 24,25 ans ; 1 835,85 × 12 × 24,25 = 534 232 €.
    assert apres == [{"age_annees": 62, "age_mois": 0, "pension_mensuelle": 1836, "cumul": 534232}]
