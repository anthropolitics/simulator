import pytest
from pytest import approx

from simulator.mesures.retraite_63_ans_taux_plein_65_ans import MESURE, retraites
from simulator.retraites import PARAMETRES_ACTUELS, depart, selon_generation

RETAILLEAU = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40


def test_parametres():
    # 1963 garde 62 ans et 9 mois ; 63 ans à partir de 1964. Taux plein automatique à 65 ans, décote de 1,75 % par trimestre.
    ages = [selon_generation(RETAILLEAU.age_legal, annee) for annee in (1961, 1963, 1964, 1966, 1985)]
    assert ages == [62 * 12, 62 * 12 + 9, 63 * 12, 63 * 12, 63 * 12]
    assert (RETAILLEAU.age_taux_plein, RETAILLEAU.decote, RETAILLEAU.duree_requise) == (65 * 12, approx(0.0175), PARAMETRES_ACTUELS.duree_requise)


def test_la_duree_reste_le_verrou_d_une_carriere_complete():
    # Début à 21 ou 22 ans : les 172 trimestres arrivent à 64 ou 65 ans, comme aujourd'hui.
    assert depart(1985, 21, SMIC_ANNUEL, parametres=RETAILLEAU) == depart(1985, 21, SMIC_ANNUEL)
    assert depart(1985, 22, SMIC_ANNUEL, parametres=RETAILLEAU) == depart(1985, 22, SMIC_ANNUEL)


def test_taux_plein_automatique_a_65_ans():
    # Début à 24 ans : 67 ans et 172 trimestres aujourd'hui, 65 ans et 164 trimestres ensuite, sans décote.
    avant, apres = depart(1985, 24, SMIC_ANNUEL), depart(1985, 24, SMIC_ANNUEL, parametres=RETAILLEAU)
    assert (avant.age_annees, avant.pension_mensuelle) == (67, approx(1243.21, abs=0.01))
    assert (apres.age_annees, apres.trimestres, apres.taux) == (65, 164, 0.5)
    assert apres.regime_general == approx(900.90 * 164 / 172)  # 859,00 €, au-dessus du minimum contributif au prorata (852,08 €)
    assert apres.agirc_arrco == approx(POINTS_SMIC * 41 * 1.4386 / 12)  # 326,39 €
    # Espérance de vie à 65 ans : (23,6 + 20,0) / 2 = 21,8 ans, contre 20,2 ans à 67 ans : 310 097 € au lieu de 301 354 €.
    assert apres.cumul == approx(apres.pension_mensuelle * 12 * 21.8)
    assert apres.cumul > avant.cumul


def test_depart_a_63_ans_avec_decote_de_7_pourcent_par_an():
    with pytest.raises(ValueError, match="âge légal"):
        depart(1985, 24, SMIC_ANNUEL, age_depart=63 * 12)
    # Début à 24 ans, départ à 63 ans : 156 trimestres ; 16 manquent pour la durée, 8 avant 65 ans : décote de 8 × 1,75 % = 14 %.
    d = depart(1985, 24, SMIC_ANNUEL, parametres=RETAILLEAU, age_depart=63 * 12)
    assert (d.trimestres, d.taux) == (156, approx(0.43))
    assert d.regime_general == approx(SMIC_ANNUEL * 0.43 * 156 / 172 / 12)  # 702,70 €
    assert d.agirc_arrco == approx(POINTS_SMIC * 39 * 1.4386 * 0.92 / 12)  # coefficient de 0,92 pour 8 trimestres manquants


def test_generation_1964_relevee_a_63_ans():
    # Début à 20 ans : 170 trimestres requis atteints à 62 ans et 6 mois ; 62 ans et 9 mois aujourd'hui, 63 ans ensuite.
    avant, apres = depart(1964, 20, SMIC_ANNUEL), depart(1964, 20, SMIC_ANNUEL, parametres=RETAILLEAU)
    assert (avant.age_annees, avant.age_mois, apres.age_annees, apres.age_mois, apres.trimestres) == (62, 9, 63, 0, 172)
