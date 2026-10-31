from pytest import approx

from simulator.mesures.abrogation_reforme_retraites_2023 import MESURE, retraites
from simulator.retraites import PARAMETRES_ACTUELS, depart, selon_generation

AVANT_2023 = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40


def test_age_et_duree_d_avant_2023():
    # 62 ans pour tous ; un trimestre de plus toutes les trois générations, de 168 (1961) à 172 (1973).
    assert [selon_generation(AVANT_2023.age_legal, annee) for annee in (1961, 1969, 1985)] == [62 * 12] * 3
    duree = [selon_generation(AVANT_2023.duree_requise, annee) for annee in (1961, 1963, 1964, 1966, 1967, 1970, 1972, 1973, 1985)]
    assert duree == [168, 168, 169, 169, 170, 171, 171, 172, 172]


def test_generations_1964_a_1972_partent_plus_tot():
    # Né en 1966, début à 20 ans : 63 ans (borne de 21 ans) aujourd'hui ; 169 trimestres requis, atteints à 62 ans et 3 mois, après 62 ans.
    avant, apres = depart(1966, 20, SMIC_ANNUEL), depart(1966, 20, SMIC_ANNUEL, parametres=AVANT_2023)
    assert (avant.age_annees, avant.age_mois) == (63, 0)
    assert (apres.age_annees, apres.age_mois, apres.trimestres, apres.regime_general) == (62, 3, 169, approx(900.90))
    assert apres.agirc_arrco == approx(POINTS_SMIC * 42.25 * 1.4386 / 12)  # 42 ans et 3 mois de points : 336,34 €
    # Espérance de vie à 62 ans et 3 mois : 24,25 + (23,4 - 24,25) × 3 / 12 = 24,0375 ans, soit 356 882 €.
    assert apres.cumul == approx(apres.pension_mensuelle * 12 * 24.0375)
    # Né en 1968, début à 22 ans : 170 trimestres à 64 ans et 6 mois au lieu de 172 à 65 ans.
    d = depart(1968, 22, SMIC_ANNUEL, parametres=AVANT_2023)
    assert (d.age_annees, d.age_mois, d.trimestres) == (64, 6, 170)


def test_generation_1985_meme_age_de_16_a_24_ans():
    # 172 trimestres dans les deux lois : 62 ans pour un début à 19 ans (borne de 20 ans aujourd'hui, durée atteinte à 62 ans avant 2023).
    for age_debut in (16, 19, 20, 22, 24):
        assert depart(1985, age_debut, SMIC_ANNUEL, parametres=AVANT_2023) == depart(1985, age_debut, SMIC_ANNUEL)


def test_debut_avant_16_ans_avec_8_trimestres_de_plus():
    # 58 ans aujourd'hui avec 172 trimestres ; avant 2023, 180 trimestres pour 58 ans : 59 ans pour un début à 14 ans, 60 ans à 15 ans.
    assert (depart(1985, 14, SMIC_ANNUEL).age_annees, depart(1985, 15, SMIC_ANNUEL).age_annees) == (58, 58)
    a_14, a_15 = depart(1985, 14, SMIC_ANNUEL, parametres=AVANT_2023), depart(1985, 15, SMIC_ANNUEL, parametres=AVANT_2023)
    assert (a_14.age_annees, a_14.trimestres, a_15.age_annees, a_15.trimestres) == (59, 180, 60, 180)
