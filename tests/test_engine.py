from simulator.engine import TAUX_ACTUEL, simuler


def test_scenario_au_taux_actuel_ne_change_rien():
    r = simuler([3000], 0, TAUX_ACTUEL)
    assert r["avant"] == r["apres"] and r["ecart_revenu_disponible"] == 0


def test_hausse_du_taux_baisse_le_revenu_dans_la_tranche():
    r = simuler([6000], 0, 0.35)
    assert r["ecart_revenu_disponible"] < 0
    assert r["apres"]["impots_directs"] < r["avant"]["impots_directs"]


def test_revenu_disponible_additionne_ses_composantes():
    m = simuler([2500, 2000], 2, TAUX_ACTUEL)["avant"]
    # Chaque montant est arrondi à l'euro séparément.
    assert abs(m["revenu_disponible"] - (m["salaire_net"] + m["impots_directs"] + m["prestations_sociales"])) <= 1


def test_pas_de_rsa_fantome_pour_un_haut_salaire():
    assert simuler([6000], 0, TAUX_ACTUEL)["avant"]["prestations_sociales"] == 0


def test_deux_enfants_ouvrent_les_allocations_familiales():
    sans, avec = (simuler([2500, 2000], n, TAUX_ACTUEL)["avant"] for n in (0, 2))
    assert avec["prestations_sociales"] > sans["prestations_sociales"]
