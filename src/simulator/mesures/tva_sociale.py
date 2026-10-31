from simulator.mesures import Mesure

HAUSSE = 0.015


def appliquer(reforme):
    def hausser(parametres):
        taux_normal = parametres.taxation_indirecte.tva.taux_normal
        taux_normal.update(start="2025-01-01", value=taux_normal("2025-01-01") + HAUSSE)
        return parametres

    reforme.modify_parameters(modifier_function=hausser)


MESURE = Mesure(
    id="tva_sociale",
    titre="TVA sociale : taux normal de TVA relevé de 1,5 point, de 20 % à 21,5 %",
    candidats=("Édouard Philippe",),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 24",
    citation="TVA sociale : +1,5 point de TVA (10 Md€) compensé par une baisse des cotisations patronales.",
    traduction=(
        "Le site du candidat propose de « rééquilibrer le financement du modèle social pour qu'il ne repose plus uniquement sur le travail et augmenter le "
        "salaire net des actifs » (https://www.edouardphilippe.fr/priorites/pour-une-france-plus-prospere, consulté le 31 octobre 2026), sans parler de TVA ; "
        "le 27 août 2026, devant le Medef, il a jugé indispensable de « faire en sorte que toute la population contribue au financement de la protection "
        "sociale » (Public Sénat, 2 septembre 2026). Le budget alternatif d'Horizons d'octobre 2026 n'en parle pas (Journal du Net, 13 octobre 2026). Seul le "
        "rapport « Présidentielle 2027 — Analyse des programmes » chiffre la mesure, sans dire quels taux montent. Le calcul relève le seul taux normal, de "
        "20 % à 21,5 % à partir du 1er janvier 2025 : c'est ce que donnent les 10 Md€ du rapport, un point du seul taux normal rapportant environ 7 Md€ et un "
        "point de tous les taux 11,4 Md€ (Terra Nova, cité par Moneyvox le 8 décembre 2025), et c'est ce qu'a fait la TVA sociale votée en 2012 (taux normal "
        "de 19,6 % à 21,2 %). Les taux intermédiaire, réduit et particulier ne changent pas. La hausse porte sur les dépenses du ménage au taux normal : "
        "électricité, gaz, fioul, carburants et reste de la consommation au taux normal, saisies ou imputées selon son décile de niveau de vie (enquête Budget "
        "de famille 2017 de l'Insee, aux prix de 2025). Elle compte dans l'écart de pouvoir d'achat, pas dans le revenu disponible, qui ne comprend pas les "
        "impôts sur la consommation. La baisse des cotisations patronales n'est pas simulée : ni le rapport ni le candidat ne disent quelles cotisations "
        "baissent, ni sur quels salaires."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # aucun document de la campagne 2027 ne porte la hausse de TVA
    hypotheses=(
        "La hausse de taux est supposée passer entièrement dans les prix, et les quantités consommées sont tenues fixes. Une baisse des cotisations "
        "patronales réduit le coût du travail sans changer, mécaniquement, le salaire brut ni le salaire net : le salaire net ne monterait que si "
        "les employeurs en reversaient une part en salaire, part qui dépend des négociations et n'est pas connue. Si les entreprises répercutaient "
        "au contraire la baisse du coût du travail sur leurs prix hors taxe, la hausse des prix payés serait moindre. Ces effets, comme ceux sur "
        "l'emploi et la compétitivité, ne sont pas calculés."
    ),
)
