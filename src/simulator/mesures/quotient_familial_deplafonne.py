from simulator.mesures import Mesure

SANS_PLAFOND = 1e9  # un plafond qu'aucun avantage n'atteint ; l'infini donnerait 0 × ∞ pour un foyer sans demi-part
# Demi-part d'enfant à charge, première part d'un parent isolé (case T), demi-part d'une personne seule ayant eu des enfants à charge (case L).
PLAFONDS = ("general", "celib_enf", "celib")


def appliquer(reforme):
    def deplafonner(parametres):
        plafonds = parametres.impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part
        for nom in PLAFONDS:
            getattr(plafonds, nom).update(start="2025-01-01", value=SANS_PLAFOND)
        return parametres

    reforme.modify_parameters(modifier_function=deplafonner)


MESURE = Mesure(
    id="quotient_familial_deplafonne",
    titre="Déplafonnement du quotient familial",
    candidats=("David Lisnard",),
    source="https://www.unenouvelleenergie.fr/notre-programme/reussir-une-nouvelle-ambition-francaise/",
    citation=(
        "A l'instar d'autres pays européens, la France doit relancer sa politique familiale dans ses trois dimensions : des allocations "
        "financières, notamment par le déplafonnement du quotient familial, des investissements pour les structures d'accueil et une politique "
        "du logement familial."
    ),
    traduction=(
        "Programme de Nouvelle Énergie, le parti du candidat (page consultée le 31 octobre 2026), qui date le démantèlement de la politique familiale "
        "de 2013, année où le plafond de l'avantage d'une demi-part est passé de 2 336 € à 2 000 €, puis à 1 500 € en 2014. La tribune du candidat "
        "« Changer de logiciel fiscal » (Atlantico, 13 avril 2026, https://atlantico.fr/article/decryptage/changer-de-logiciel-fiscal-david-lisnard) "
        "reprend le « déplafonnement du quotient familial », selon le résumé qu'en fait Le Cahier d'Uniquien "
        "(https://lecahierdauniquien.substack.com/p/changer-de-logiciel-fiscal-que-valent, 19 avril 2026), la tribune n'étant pas lisible sans "
        "abonnement. Déplafonner, c'est supprimer le plafond, pas revenir à celui de 2012 : à partir du 1er janvier 2025, les plafonds de "
        "l'avantage procuré par les parts de quotient familial (1 807 € par demi-part d'enfant à charge, 4 262 € pour la première part d'un parent "
        "isolé, 1 079 € pour la demi-part d'une personne seule ayant eu des enfants à charge) sont portés à un milliard d'euros, que nul avantage "
        "n'atteint. Le nombre de parts, la décote et les réductions d'impôt ne changent pas. Seuls les foyers dont l'avantage dépasse aujourd'hui le "
        "plafond y gagnent : pour un couple avec deux enfants dont le revenu par part est dans la tranche à 30 %, le gain est de 3 282 € par an."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # page du parti non datée ; la tribune de la campagne n'est connue que par un résumé
    hypotheses="Les effets sur la natalité et l'activité des parents ne sont pas simulés, pas plus que le financement.",
)
