from simulator import tableau
from simulator.menages import Menage
from simulator.persona import Adulte, Persona


def test_le_programme_d_un_candidat_reunit_ses_mesures():
    p = tableau.programmes()
    assert "smic_1700_net" in p["Jean-Luc Mélenchon"] and "smic_1600_net" not in p["Jean-Luc Mélenchon"]
    noms = list(p)
    # Par nom de famille : Le Pen à L, Mélenchon (é) avant Philippe.
    assert noms.index("Marine Le Pen") < noms.index("David Lisnard") < noms.index("Jean-Luc Mélenchon") < noms.index("Édouard Philippe")


def test_une_ligne_par_candidat_et_par_menage(monkeypatch):
    seul = Menage(id="seul", prenom="", situation="", couleur="ocre", persona=Persona(adultes=(Adulte(age=40, au_smic=True),)), sources="")
    monkeypatch.setattr(tableau, "MENAGES", {"seul": seul})
    monkeypatch.setattr(tableau, "programmes", lambda: {"Marine Le Pen": ("retraite_62_ans_60_ans_carrieres_longues",)})
    t = tableau.tableau()
    (ligne,) = t["resultats"]
    assert (ligne["candidat"], ligne["menage"], ligne["ecart_pouvoir_achat"]) == ("Marine Le Pen", "seul", 0)
    # Début à 22 ans au SMIC : 65 ans aujourd'hui, 63 ans avec la mesure (164 trimestres pour un début à 22 ans).
    assert (ligne["retraites"][0]["avant"]["age_annees"], ligne["retraites"][0]["apres"]["age_annees"]) == (65, 63)
    assert t["programmes"][0]["mesures"][0] | {"titre": ""} == {"id": "retraite_62_ans_60_ans_carrieres_longues", "titre": "", "a_confirmer": True}
