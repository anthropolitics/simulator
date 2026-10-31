import pytest

from simulator.engine import LOI_ACTUELLE, SMIC_ACTUEL, calculer, retraites
from simulator.menages import MENAGES
from simulator.retraites import PARAMETRES_ACTUELS

# Salaire net mensuel du foyer que donne la source (Insee Première n° 2132) : le calcul de la loi actuelle doit le retrouver, à 1 € près.
SALAIRE_NET = {"seul_au_smic": 1426, "couple_salaires_medians": 2128 + 2328, "mere_seule": 1979, "couple_cadres": 2 * 4711}
# Pensions brutes moyennes de droit direct des hommes et des femmes fin 2024 (Drees, édition 2026, fiche 5, tableau 1).
RETRAITE_BRUTE = {"couple_retraites": (2186, 1383), "retraitee_seule": (1383,)}
NEUVIEME_DECILE = 48_580  # niveau de vie annuel 2024 (Insee Première n° 2117)


def test_six_menages_une_couleur_chacun():
    assert len(MENAGES) == 6 and all(id == m.id for id, m in MENAGES.items())
    assert sorted(m.couleur for m in MENAGES.values()) == sorted(("ocre", "ardoise", "sauge", "prune", "argile", "lin"))


@pytest.mark.parametrize("id", MENAGES)
def test_menage_type(id):
    persona = MENAGES[id].persona
    resultat = calculer(LOI_ACTUELLE, persona)  # un seul calcul par ménage : la suite est lente
    assert resultat["revenu_disponible"] > 0
    departs = retraites(persona, SMIC_ACTUEL, PARAMETRES_ACTUELS)
    assert [depart is not None for depart in departs] == [a.au_smic or a.salaire_brut_mensuel > 0 for a in persona.adultes]
    if id in SALAIRE_NET:
        assert abs(resultat["salaire_net"] / 12 - SALAIRE_NET[id]) <= 1
    else:
        assert tuple(a.retraite_brute_mensuelle for a in persona.adultes) == RETRAITE_BRUTE[id]
    if id == "couple_cadres":  # au 9e décile de niveau de vie : 2,1 unités de consommation, à 2 % près
        assert abs(resultat["revenu_disponible"] / 2.1 / NEUVIEME_DECILE - 1) < 0.02
