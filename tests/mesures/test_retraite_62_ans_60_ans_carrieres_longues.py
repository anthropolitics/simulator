from pytest import approx

from simulator.mesures.retraite_62_ans_60_ans_carrieres_longues import MESURE, retraites
from simulator.retraites import PARAMETRES_ACTUELS, depart

LE_PEN = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40


def test_parametres():
    assert (LE_PEN.age_legal_cible, LE_PEN.duree_requise_cible, LE_PEN.duree_carriere_longue) == (62 * 12, 168, 160)


def test_ages_de_depart_selon_l_age_de_debut():
    # Né en 1985, au SMIC sans interruption : (âge de départ en mois, trimestres) aujourd'hui puis avec la mesure.
    attendus = {
        15: (58 * 12, 172, 58 * 12, 172),  # borne de 16 ans gardée : 168 trimestres atteints à 57 ans, départ à 58 ans
        19: (62 * 12, 172, 60 * 12, 164),  # avant 20 ans : 160 trimestres à 59 ans, départ à 60 ans
        20: (63 * 12, 172, 60 * 12, 160),  # à 20 ans : la borne de 21 ans donne aussi 60 ans avec 160 trimestres
        21: (64 * 12, 172, 62 * 12, 164),  # 162 trimestres à 61 ans et 6 mois, relevés à l'âge légal de 62 ans
        22: (65 * 12, 172, 63 * 12, 164),  # 164 trimestres à 63 ans
        23: (66 * 12, 172, 64 * 12 + 6, 166),  # 166 trimestres à 64 ans et 6 mois
        24: (67 * 12, 172, 66 * 12, 168),  # droit commun : 168 trimestres à 66 ans
    }
    for age_debut, attendu in attendus.items():
        avant, apres = depart(1985, age_debut, SMIC_ANNUEL), depart(1985, age_debut, SMIC_ANNUEL, parametres=LE_PEN)
        assert (12 * avant.age_annees + avant.age_mois, avant.trimestres, 12 * apres.age_annees + apres.age_mois, apres.trimestres) == attendu


def test_pension_a_60_ans_proratisee_sur_168_trimestres():
    # Début à 20 ans : 60 ans au taux plein avec 160 trimestres ; 900,90 × 160 / 168 = 858,00 € au régime général, au-dessus du minimum
    # contributif au prorata (851,10 €), et 40 ans de points (318,43 €).
    d = depart(1985, 20, SMIC_ANNUEL, parametres=LE_PEN)
    assert (d.taux, d.regime_general) == (0.5, approx(900.90 * 160 / 168))
    assert d.agirc_arrco == approx(POINTS_SMIC * 40 * 1.4386 / 12)
    assert d.cumul == approx(d.pension_mensuelle * 12 * (27.9 + 23.9) / 2)  # espérance de vie à 60 ans : 25,9 ans, soit 365 634 €


def test_annees_sans_emploi_retardent_le_depart():
    # Début à 19 ans puis 3 ans sans emploi : les 160 trimestres arrivent à 62 ans (65 ans aujourd'hui, avec 172).
    assert depart(1985, 19, SMIC_ANNUEL, 3).age_annees == 65
    d = depart(1985, 19, SMIC_ANNUEL, 3, LE_PEN)
    assert (d.age_annees, d.trimestres) == (62, 160)
