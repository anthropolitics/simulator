from dataclasses import replace

from simulator.mesures import Mesure
from simulator.retraites import Parametres

# Âge légal en mois par génération : 63 ans à partir de 1964, la première qui n'avait pas atteint son âge légal en 2025.
AGE_LEGAL = ((1961, 62 * 12), (1962, 62 * 12 + 6), (1963, 62 * 12 + 9), (1964, 63 * 12))


def retraites(parametres: Parametres) -> Parametres:
    # 7 % par an : 1,75 % par trimestre manquant, au lieu de 1,25 %.
    return replace(parametres, age_legal=AGE_LEGAL, age_taux_plein=65 * 12, decote=0.07 / 4)


MESURE = Mesure(
    id="retraite_63_ans_taux_plein_65_ans",
    titre="Âge minimal de départ à 63 ans, taux plein automatique à 65 ans, décote de 7 % par an",
    candidats=("Bruno Retailleau",),
    source="https://lcp.fr/actualites/retraites-bruno-retailleau-veut-un-age-minimal-de-depart-a-63-ans-et-un-taux-plein-a-65",
    citation=(
        "« L'âge minimal de départ, c'est 63 ans » ; ce départ à 63 ans aura « une décote de 7 % par an » ; le taux plein automatique à 65 ans, "
        "« même si vous n'avez pas toutes vos annuités, tous vos trimestres » (LCI, 22 septembre 2026)."
    ),
    traduction=(
        "Le candidat a présenté sa réforme sur LCI le 22 septembre 2026 ; la dépêche AFP reprise par LCP le 23 septembre 2026 (consultée le 31 octobre "
        "2026) cite ses mots. Les documents des Républicains lus ne donnent pas ces paramètres : la brochure de janvier 2026 "
        "(https://republicains.fr/wp-content/uploads/2026/01/51705_LesRepublicains_Brochures_A5-40P_DEF.pdf) exonère de cotisations retraite et "
        "chômage les salariés qui ont tous leurs trimestres avant l'âge légal, et le livret « Produire plus » de février 2026 annonce un étage de "
        "retraite par capitalisation. Le rapport « Présidentielle 2027 — Analyse des programmes » (28 octobre 2026) le range à 65 ans : c'est l'âge "
        "du taux plein automatique, pas l'âge légal. L'âge légal passe à 63 ans (age_legal) pour les générations à partir de 1964, la première qui "
        "n'avait pas atteint son âge légal en 2025, l'année simulée : 62 ans et 9 mois pour 1964 et 1965, 63 ans et 3 mois à 64 ans pour les "
        "générations suivantes, aujourd'hui ; les générations 1961 à 1963 gardent le leur. La cible s'applique d'emblée, la source ne donnant pas de "
        "calendrier. La durée requise ne change pas (172 trimestres, soit 43 ans, à partir de la génération 1966) : avec elle, le départ à 63 ans se "
        "fait au taux plein, ce que la dépêche confirme pour « les personnes ayant commencé à travailler jeunes et ayant une carrière complète ». "
        "L'âge du taux plein automatique passe de 67 à 65 ans (age_taux_plein). La décote de « 7 % par an » est lue comme 1,75 % du taux par "
        "trimestre manquant au lieu de 1,25 % (5 % par an) : elle compte, comme aujourd'hui, le plus petit des deux nombres de trimestres "
        "manquants, pour la durée requise ou jusqu'à 65 ans, si bien qu'un départ à 63 ans coûte au plus 2 × 7 % = 14 %. Les coefficients de "
        "l'Agirc-Arrco restent ceux d'aujourd'hui, comptés jusqu'au nouvel âge du taux plein. Les carrières longues (départ à 58, 60 ou 62 ans pour "
        "un début avant 16, 18 ou 20 ans) et la surcote ne changent pas, la source n'en parlant pas."
    ),
    retraites=retraites,
    a_confirmer=True,  # mesure annoncée à la télévision, qu'aucun document du candidat ou des Républicains ne porte encore
    hypotheses=(
        "L'âge du taux plein serait lié à l'espérance de vie : il est tenu à 65 ans, l'espérance de vie étant celle de 2025. La part de "
        "capitalisation (25 à 30 % des retraites des jeunes qui entrent sur le marché du travail, avec pour piste de financement une cotisation de 1 % du salaire brut) "
        "n'est pas simulée : ni son rendement, ni la baisse des droits par répartition qu'elle remplacerait ne sont donnés. Les exceptions pour la "
        "pénibilité, à définir avec les partenaires sociaux, et l'exonération de cotisations des salariés qui ont leurs trimestres ne sont pas "
        "simulées. Chaque salarié part au taux plein, au plus tôt : le départ à 63 ans avec décote n'est pas choisi. La carrière et le salaire sont "
        "tenus fixes ; ni l'emploi des seniors, ni les 40 milliards d'euros d'économies annoncés sur cinq ans ne sont calculés."
    ),
)
