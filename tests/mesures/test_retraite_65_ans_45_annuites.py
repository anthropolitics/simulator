from pytest import approx

from simulator.mesures.retraite_65_ans_45_annuites import MESURE, retraites
from simulator.retraites import PARAMETRES_ACTUELS, depart, selon_generation

PHILIPPE = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40


def test_calendrier():
    # Réforme de 2023 jusqu'à 1968 (63 ans et 171 trimestres pour 1964, 64 ans et 172 pour 1968), puis 65 ans et 180 trimestres pour 1972.
    annees = (1963, 1964, 1965, 1968, 1969, 1971, 1972, 1990)
    assert [selon_generation(PHILIPPE.age_legal, a) for a in annees] == [62 * 12 + 9, 63 * 12, 63 * 12 + 3, 64 * 12, 64 * 12 + 3, 64 * 12 + 9, 65 * 12, 65 * 12]
    assert [selon_generation(PHILIPPE.duree_requise, a) for a in annees] == [170, 171, 172, 172, 174, 178, 180, 180]


def test_smic_debut_21_ans_ne_en_1985():
    # 180 trimestres à 21 + 45 = 66 ans, au lieu de 172 à 64 ans : deux ans de plus.
    d = depart(1985, 21, SMIC_ANNUEL, parametres=PHILIPPE)
    assert (d.age_annees, d.age_mois, d.trimestres, d.regime_general) == (66, 0, 180, approx(900.90))
    assert d.agirc_arrco == approx(POINTS_SMIC * 45 * 1.4386 / 12)  # 358,23 € pour 45 ans de points
    assert d.cumul == approx(1259.13 * 12 * 20.95, abs=2)  # espérance de vie à 66 ans : (22,7 + 19,2) / 2 = 20,95 ans


def test_retour_de_la_reforme_de_2023_ne_en_1964():
    # Né en 1964 : 171 trimestres au lieu de 170, atteints à 63 ans et 9 mois au lieu de 63 ans et 6 mois.
    assert (depart(1964, 21, SMIC_ANNUEL).age_annees, depart(1964, 21, SMIC_ANNUEL).age_mois) == (63, 6)
    d = depart(1964, 21, SMIC_ANNUEL, parametres=PHILIPPE)
    assert (d.age_annees, d.age_mois, d.trimestres) == (63, 9, 171)


def test_carriere_longue_avec_45_ans_cotises():
    # Début à 17 ans : la borne de 18 ans permet 60 ans, mais il faut 180 trimestres cotisés, atteints à 62 ans.
    d = depart(1985, 17, SMIC_ANNUEL, parametres=PHILIPPE)
    assert (d.age_annees, d.trimestres, d.taux) == (62, 180, 0.5)


def test_taux_plein_a_67_ans_au_prorata():
    # Cadre débutant à 23 ans : 180 trimestres à 68 ans, le taux plein vient à 67 ans avec 176 trimestres, au prorata de 176 / 180.
    d = depart(1985, 23, 80_000, parametres=PHILIPPE)
    assert (d.age_annees, d.trimestres, d.taux) == (67, 176, 0.5)
    assert d.regime_general == approx(47_100 * 0.5 * 176 / 180 / 12)  # 1 918,89 € au lieu de 1 962,50 €
    assert d.agirc_arrco == approx(421.70 * 44 * 1.4386 / 12, abs=0.1)  # 44 ans de points au lieu de 43
