from simulator.mesures import Mesure
from simulator.mesures.tva_energie_5_5 import taux_reduit

POSTES = ("electricite", "gaz")


def appliquer(reforme):
    for poste in POSTES:
        reforme.update_variable(taux_reduit(poste))


MESURE = Mesure(
    id="tva_electricite_gaz_5_5",
    titre="TVA à 5,5 % sur l'électricité et le gaz",
    candidats=("Fabien Roussel",),
    source="https://d3n8a8pro7vhmx.cloudfront.net/fabienroussel2022/pages/217/attachments/original/1643038967/exe_la_france_des_jours_heureux_LIVRE_stc.pdf",
    citation=(
        "« 58 Les taxes pesant sur les tarifs de l'électricité et du gaz seront abaissées immédiatement. [...] À titre d'exemple, les taxes qui "
        "constituent aujourd'hui le tiers de nos factures énergétiques seront réduites, la TVA sur les consommations sera fixée à 5,5 %, les taxes "
        "assises sur des taxes seront supprimées. » (La France des Jours heureux, 2022)"
    ),
    traduction=(
        "Proposition 58 du programme de Fabien Roussel pour 2022, « La France des Jours heureux » (consulté le 31 octobre 2026), que votons-2027.fr "
        "(https://votons-2027.fr/candidats/roussel/programme) présente comme son programme de 2027. En 2022, l'abonnement à l'électricité et au gaz était déjà à 5,5 % et la consommation à 20 % ; la "
        "loi 2025 porte aussi l'abonnement à 20 % à partir du 1er août 2025, et le simulateur compte toute la dépense d'électricité et de gaz au "
        "taux normal. À partir du 1er janvier 2025, le taux de TVA des postes électricité et gaz du ménage passe à 5,5 %, abonnement compris, ce qui "
        "rétablit pour l'abonnement le taux de 2022 et applique à la consommation le taux de la source. Les autres énergies (fioul, carburants, "
        "bois, réseaux de chaleur) ne changent pas : la source ne parle que de l'électricité et du gaz. Les dépenses sont celles du persona, ou, à "
        "défaut, celles d'un ménage moyen de son décile de niveau de vie (enquête Budget de famille 2017 de l'Insee, aux prix de 2025). Le gain "
        "compte dans l'écart de pouvoir d'achat, pas dans le revenu disponible. La baisse des accises sur l'électricité et le gaz, que la source "
        "annonce sans la chiffrer, n'est pas simulée, et la suppression des « taxes assises sur des taxes » se résume ici à la TVA plus basse."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # programme de 2022 ; aucun document de la campagne 2027 lu ne porte la mesure
    hypotheses=(
        "La baisse de taux est supposée passer entièrement dans le prix payé et les quantités consommées sont tenues fixes ; le financement et "
        "l'effet sur la consommation d'énergie ne sont pas calculés."
    ),
)
