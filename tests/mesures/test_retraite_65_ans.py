from pytest import approx

from simulator.mesures.retraite_65_ans import MESURE, retraites
from simulator.retraites import PARAMETRES_ACTUELS, depart, selon_generation

A_65_ANS = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40


def test_calendrier_trois_mois_par_generation():
    # La génération 1963 garde 62 ans et 9 mois ; 63 ans pour 1964, 64 ans pour 1968, 65 ans à partir de 1972. La durée requise ne change pas.
    ages = [selon_generation(A_65_ANS.age_legal, annee) for annee in (1963, 1964, 1968, 1970, 1972, 1990)]
    assert ages == [62 * 12 + 9, 63 * 12, 64 * 12, 64 * 12 + 6, 65 * 12, 65 * 12]
    assert A_65_ANS.duree_requise == PARAMETRES_ACTUELS.duree_requise


def test_smic_debut_21_ans_ne_en_1985():
    # Les 172 trimestres sont là à 64 ans ; il attend 65 ans, avec 176 trimestres.
    avant, apres = depart(1985, 21, SMIC_ANNUEL), depart(1985, 21, SMIC_ANNUEL, parametres=A_65_ANS)
    assert (avant.age_annees, apres.age_annees, apres.age_mois, apres.trimestres) == (64, 65, 0, 176)
    assert apres.regime_general == approx(900.90)  # 50 % du SMIC ; pas de surcote : les trimestres de plus sont avant l'âge légal
    assert apres.agirc_arrco == approx(POINTS_SMIC * 44 * 1.4386 / 12)  # 350,27 € pour 44 ans de points, au lieu de 342,31 €
    # 1 251,17 € par mois sur 21,8 ans d'espérance de vie à 65 ans, au lieu de 1 243,21 € sur 22,55 ans : 9 107 € de moins sur la retraite.
    assert apres.cumul == approx(1251.17 * 12 * 21.8, abs=2)
    assert avant.cumul - apres.cumul == approx(9107, abs=2)


def test_generation_1970_a_mi_parcours():
    # Né en 1970 : âge légal de 64 ans et 6 mois au lieu de 64 ans ; 174 trimestres à cet âge.
    d = depart(1970, 21, SMIC_ANNUEL, parametres=A_65_ANS)
    assert (d.age_annees, d.age_mois, d.trimestres) == (64, 6, 174)
    assert d.agirc_arrco == approx(POINTS_SMIC * 43.5 * 1.4386 / 12)


def test_duree_et_carrieres_longues_inchangees():
    # Début à 23 ans : les 172 trimestres n'arrivent qu'à 66 ans, après 65 ans ; le départ ne change pas.
    assert depart(1985, 23, 80_000, parametres=A_65_ANS) == depart(1985, 23, 80_000)
    # Début à 17 ans : la carrière longue fait toujours partir à 60 ans avec 172 trimestres.
    assert depart(1985, 17, SMIC_ANNUEL, parametres=A_65_ANS) == depart(1985, 17, SMIC_ANNUEL)
