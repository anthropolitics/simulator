from dataclasses import replace

import pytest
from pytest import approx

from simulator.retraites import PARAMETRES_ACTUELS, coefficient_agirc_arrco, depart, selon_generation

SMIC_ANNUEL = 11.88 * 35 * 52  # SMIC brut à temps plein en 2025 : 21 621,60 €
POINTS_SMIC = SMIC_ANNUEL * 0.062 / 20.1877  # points Agirc-Arrco d'une année au SMIC : 66,40


def test_calendrier_de_la_lfss_2026():
    # Né en 1964 : 62 ans et 9 mois et 170 trimestres, au lieu de 63 ans et 171 trimestres avec la réforme de 2023.
    assert selon_generation(PARAMETRES_ACTUELS.age_legal, 1964) == 62 * 12 + 9
    assert selon_generation(PARAMETRES_ACTUELS.duree_requise, 1964) == 170
    assert selon_generation(PARAMETRES_ACTUELS.age_legal, 1969) == 64 * 12
    assert (depart(1964, 20, SMIC_ANNUEL).age_annees, depart(1964, 20, SMIC_ANNUEL).age_mois) == (62, 9)
    with pytest.raises(ValueError, match="génération 1961"):
        depart(1955, 20, SMIC_ANNUEL)


def test_smic_carriere_complete_ne_en_1985():
    # Début à 21 ans : 43 ans de cotisation mènent aux 172 trimestres pile à l'âge légal, 64 ans.
    d = depart(1985, 21, SMIC_ANNUEL)
    assert (d.age_annees, d.age_mois, d.trimestres, d.taux, d.salaire_annuel_moyen) == (64, 0, 172, 0.5, approx(SMIC_ANNUEL))
    assert d.regime_general == approx(900.90)  # 50 % du SMIC annuel, sur 12 mois ; au-dessus du minimum contributif majoré (893,65 €)
    assert d.agirc_arrco == approx(342.31, abs=0.01)  # 43 × 66,40 points à 1,4386 €, sur 12 mois
    assert d.pension_mensuelle == approx(1243.21, abs=0.01)  # 69 % du salaire brut
    assert d.cumul == approx(1243.21 * 12 * 22.55, abs=1)  # espérance de vie à 64 ans : (24,4 + 20,7) / 2 = 22,55 ans


def test_cadre_au_dessus_du_plafond():
    # 80 000 € par an dès 23 ans : la durée est atteinte à 66 ans, après l'âge légal.
    d = depart(1985, 23, 80_000)
    assert (d.age_annees, d.trimestres, d.salaire_annuel_moyen) == (66, 172, 47_100)
    assert d.regime_general == approx(47_100 * 0.5 / 12)  # la pension maximale : 1 962,50 €
    # Points par an : (47 100 × 6,20 % + 32 900 × 17 %) / 20,1877 = 421,70, sur 43 ans.
    assert d.agirc_arrco == approx(421.70 * 43 * 1.4386 / 12, abs=0.1)


def test_annees_sans_emploi_puis_decote_avant_le_taux_plein():
    # Début à 22 ans et 5 ans sans emploi : 172 trimestres à 70 ans, le taux plein vient à 67 ans avec 160 trimestres.
    d = depart(1985, 22, SMIC_ANNUEL, annees_sans_emploi=5)
    assert (d.age_annees, d.trimestres, d.taux) == (67, 160, 0.5)
    assert d.regime_general == approx(SMIC_ANNUEL * 0.5 * 160 / 172 / 12)  # 838,05 € ; le minimum contributif, 893,65 × 160 / 172, est plus bas
    assert d.agirc_arrco == approx(POINTS_SMIC * 40 * 1.4386 / 12)
    # Départ à 64 ans : 148 trimestres, 24 manquent pour la durée et 12 pour 67 ans ; le plus petit nombre fait la décote.
    d = depart(1985, 22, SMIC_ANNUEL, annees_sans_emploi=5, age_depart=64 * 12)
    assert (d.trimestres, d.taux) == (148, approx(0.5 * (1 - 12 * 0.0125)))
    assert d.regime_general == approx(SMIC_ANNUEL * 0.425 * 148 / 172 / 12)
    # Plus de 20 trimestres manquent pour la durée : l'Agirc-Arrco ne regarde que l'âge, 12 trimestres avant 67 ans, soit 0,88.
    assert d.agirc_arrco == approx(POINTS_SMIC * 37 * 1.4386 * 0.88 / 12)


def test_surcote_apres_le_taux_plein():
    # Taux plein à 64 ans ; partir à 66 ans ajoute 8 trimestres de surcote, + 10 %.
    d = depart(1985, 21, SMIC_ANNUEL, age_depart=66 * 12)
    assert (d.trimestres, d.regime_general) == (180, approx(900.90 * 1.10))
    assert d.agirc_arrco == approx(POINTS_SMIC * 45 * 1.4386 / 12)


def test_carriere_longue():
    # Début à 17 ans : 8 trimestres à la fin de l'année des 18 ans, départ à 60 ans avec les 172 trimestres.
    d = depart(1985, 17, SMIC_ANNUEL)
    assert (d.age_annees, d.age_mois, d.trimestres, d.taux) == (60, 0, 172, 0.5)
    # Né en 1968, début à 18 ans : la borne de 20 ans le fait partir à 61 ans et 3 mois, la durée étant atteinte à 61 ans.
    d = depart(1968, 18, SMIC_ANNUEL)
    assert (d.age_annees, d.age_mois) == (61, 3)
    assert d.cumul == approx(d.pension_mensuelle * 12 * (25.1 + (24.25 - 25.1) * 3 / 12))  # espérance de vie entre 61 et 62 ans
    # Début à 18 ans : 4 trimestres à la fin de l'année des 18 ans, il en faut 5 ; la borne de 20 ans donne 62 ans.
    assert depart(1985, 18, SMIC_ANNUEL).age_annees == 62


def test_age_legal_cible_62_et_65_ans_ne_en_1985():
    a_62 = replace(PARAMETRES_ACTUELS, age_legal_cible=62 * 12)
    a_65 = replace(PARAMETRES_ACTUELS, age_legal_cible=65 * 12)
    actuel = depart(1985, 21, SMIC_ANNUEL)
    # À 62 ans, la durée requise manque encore : le départ au taux plein reste à 64 ans.
    assert depart(1985, 21, SMIC_ANNUEL, parametres=a_62) == actuel
    # Partir à 62 ans devient possible, avec 8 trimestres de décote.
    with pytest.raises(ValueError, match="âge légal"):
        depart(1985, 21, SMIC_ANNUEL, age_depart=62 * 12)
    tot = depart(1985, 21, SMIC_ANNUEL, parametres=a_62, age_depart=62 * 12)
    assert (tot.trimestres, tot.taux) == (164, approx(0.45))
    assert tot.agirc_arrco == approx(POINTS_SMIC * 41 * 1.4386 * 0.92 / 12)
    # À 65 ans : un an de plus, les mêmes 50 % au régime général, un an de points en plus, une année de retraite en moins.
    tard = depart(1985, 21, SMIC_ANNUEL, parametres=a_65)
    assert (tard.age_annees, tard.trimestres, tard.regime_general) == (65, 176, approx(actuel.regime_general))
    assert tard.agirc_arrco == approx(actuel.agirc_arrco * 44 / 43)
    assert tard.cumul == approx(tard.pension_mensuelle * 12 * 21.8)  # (23,6 + 20,0) / 2
    assert tard.cumul < actuel.cumul


def test_minimum_contributif():
    # 15 000 € par an : 625 € au régime général, relevés au minimum contributif majoré pour 172 trimestres cotisés.
    assert depart(1985, 21, 15_000).regime_general == approx(893.65)
    # Début à 40 ans : 108 trimestres à 67 ans, moins de 120, le minimum entier au prorata.
    assert depart(1985, 40, 15_000).regime_general == approx(747.69 * 108 / 172)
    # Un minimum relevé à 1 300 € s'arrête au plafond de l'ensemble des retraites, 1 394,86 €.
    assert depart(1985, 21, 15_000, parametres=replace(PARAMETRES_ACTUELS, minimum_contributif_majore=1300)).pension_mensuelle == approx(1394.86)


def test_minimum_de_pension():
    minimum = replace(PARAMETRES_ACTUELS, minimum_pension=1600)
    assert depart(1985, 21, SMIC_ANNUEL, parametres=minimum).pension_mensuelle == approx(1600)
    assert depart(1985, 22, SMIC_ANNUEL, 5, minimum).pension_mensuelle == approx(1600 * 160 / 172)
    # Pas de minimum avec une décote, ni au-dessus.
    assert depart(1985, 22, SMIC_ANNUEL, 5, minimum, age_depart=64 * 12) == depart(1985, 22, SMIC_ANNUEL, 5, age_depart=64 * 12)
    assert depart(1985, 23, 80_000, parametres=minimum) == depart(1985, 23, 80_000)


def test_coefficients_agirc_arrco_publies():
    # Agirc-Arrco, tableaux 2 et 3 : 13 trimestres 0,8675 ; 20 trimestres ou 62 ans 0,78 ; 57 ans 0,43.
    assert [coefficient_agirc_arrco(n) for n in (0, 1, 12, 13, 20, 24, 40)] == approx([1, 0.99, 0.88, 0.8675, 0.78, 0.71, 0.43])
