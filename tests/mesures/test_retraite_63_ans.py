import pytest
from pytest import approx

from simulator.mesures.retraite_63_ans import MESURE, retraites
from simulator.retraites import PARAMETRES_ACTUELS, depart, selon_generation

A_63_ANS = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40


def test_age_legal_plafonne_a_63_ans():
    # 1964 garde 62 ans et 9 mois ; 1966 passe de 63 ans et 3 mois à 63 ans, 1985 de 64 à 63 ans. La durée requise ne change pas.
    ages = [selon_generation(A_63_ANS.age_legal, annee) for annee in (1961, 1964, 1965, 1966, 1968, 1985)]
    assert ages == [62 * 12, 62 * 12 + 9, 62 * 12 + 9, 63 * 12, 63 * 12, 63 * 12]
    assert A_63_ANS.duree_requise == PARAMETRES_ACTUELS.duree_requise


def test_le_taux_plein_ne_change_pas_pour_une_carriere_continue():
    # Début à 21 ans : les 172 trimestres arrivent à 64 ans, après 63 ans.
    assert depart(1985, 21, SMIC_ANNUEL, parametres=A_63_ANS) == depart(1985, 21, SMIC_ANNUEL)
    # Début à 20 ans : la carrière longue (borne de 21 ans) mène déjà à 63 ans, avec les 172 trimestres.
    d = depart(1985, 20, SMIC_ANNUEL, parametres=A_63_ANS)
    assert (d.age_annees, d.age_mois, d.trimestres) == (63, 0, 172)
    assert d == depart(1985, 20, SMIC_ANNUEL)


def test_depart_a_63_ans_avec_decote():
    with pytest.raises(ValueError, match="âge légal"):
        depart(1985, 21, SMIC_ANNUEL, age_depart=63 * 12)
    # Début à 21 ans, départ à 63 ans : 168 trimestres, 4 manquent, décote de 5 %.
    d = depart(1985, 21, SMIC_ANNUEL, parametres=A_63_ANS, age_depart=63 * 12)
    assert (d.trimestres, d.taux) == (168, approx(0.475))
    assert d.regime_general == approx(SMIC_ANNUEL * 0.475 * 168 / 172 / 12)  # 835,95 €
    assert d.agirc_arrco == approx(POINTS_SMIC * 42 * 1.4386 * 0.96 / 12)  # coefficient de 0,96 pour 4 trimestres manquants
