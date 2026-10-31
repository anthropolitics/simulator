from dataclasses import replace

from pytest import approx

from simulator.mesures.minimum_pension_1200 import MESURE, retraites
from simulator.retraites import PARAMETRES_ACTUELS, depart

MINIMUM = retraites(PARAMETRES_ACTUELS)
assert MESURE.retraites is retraites
SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_15_000 = 15_000 * 0.062 / 20.1877  # points Agirc-Arrco d'une année à 15 000 € : 46,07


def test_carriere_complete_relevee_a_1200():
    # 15 000 € par an dès 21 ans, 172 trimestres à 64 ans : 893,65 € (minimum contributif majoré) et 43 ans de points (237,48 €), soit 1 131,13 €.
    avant, apres = depart(1985, 21, 15_000), depart(1985, 21, 15_000, parametres=MINIMUM)
    assert avant.pension_mensuelle == approx(893.65 + POINTS_15_000 * 43 * 1.4386 / 12)
    assert (apres.age_annees, apres.agirc_arrco, apres.pension_mensuelle) == (64, approx(avant.agirc_arrco), approx(1200))
    assert apres.regime_general == approx(1200 - avant.agirc_arrco)  # le régime général verse le complément : 962,52 €


def test_carriere_incomplete_au_prorata():
    # Début à 40 ans : 108 trimestres à 67 ans ; 1 200 × 108 / 172 = 753,49 € au lieu de 469,48 € + 149,11 €.
    avant, apres = depart(1985, 40, 15_000), depart(1985, 40, 15_000, parametres=MINIMUM)
    assert avant.pension_mensuelle == approx(747.69 * 108 / 172 + POINTS_15_000 * 27 * 1.4386 / 12)
    assert (apres.trimestres, apres.pension_mensuelle) == (108, approx(1200 * 108 / 172))


def test_sans_effet_avec_decote_ou_au_dessus():
    # Départ à 64 ans avec 12 trimestres de décote : pas de minimum.
    assert depart(1985, 40, 15_000, parametres=MINIMUM, age_depart=64 * 12) == depart(1985, 40, 15_000, age_depart=64 * 12)
    # Au SMIC, carrière complète : 1 243,21 €, déjà au-dessus.
    assert depart(1985, 21, SMIC_ANNUEL, parametres=MINIMUM) == depart(1985, 21, SMIC_ANNUEL)


def test_un_minimum_plus_haut_est_garde():
    assert retraites(replace(PARAMETRES_ACTUELS, minimum_pension=1500)).minimum_pension == 1500
