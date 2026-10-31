from dataclasses import replace

from simulator.mesures import Mesure
from simulator.retraites import Parametres

AGE_LEGAL = 63 * 12


def retraites(parametres: Parametres) -> Parametres:
    # Plafonné et non fixé : les générations 1961 à 1965, déjà sous 63 ans, gardent leur âge légal.
    return replace(parametres, age_legal=tuple((generation, min(age, AGE_LEGAL)) for generation, age in parametres.age_legal))


MESURE = Mesure(
    id="retraite_63_ans",
    titre="Âge légal de départ à la retraite ramené à 63 ans",
    candidats=("Raphaël Glucksmann",),
    source="Présidentielle 2027 — Analyse des programmes, 28 octobre 2026, p. 27",
    citation="Convergence vers un âge de départ à 63 ans ; prise en compte de la pénibilité ; minimum de pension à 1 200 € ; retraite progressive.",
    traduction=(
        "Seul le rapport « Présidentielle 2027 — Analyse des programmes » donne l'âge de 63 ans. Le projet de Place publique, « Acte un » "
        "(https://place-publique.eu/document/6J8wjk3EW8dBCLwKxa7J96/projet-placepublique-acte1.pdf, chantier 19, consulté le 31 octobre 2026), dit "
        "autre chose : « Abroger la réforme Macron de 2023 », puis « cesser la focalisation sur le seul âge légal qui produit l'injustice et fonder "
        "notre philosophie sur les inégalités de conditions et d'espérance de vie : certains doivent pouvoir partir à la retraite à 60 ans, d'autres "
        "devront travailler davantage ». Ni franceinfo (30 septembre 2026), ni Public Sénat (24 août 2026), ni Yahoo Finance (24 septembre 2026) ne "
        "lui prêtent un âge : il « ne fixe pas, pour l'instant, de nouvel âge légal unique ». Le calcul suit le rapport. L'âge légal de chaque "
        "génération est plafonné à 63 ans : les générations 1966 à 1968 (63 ans et 3 à 9 mois) et à partir de 1969 (64 ans) passent à 63 ans ; les "
        "générations 1961 à 1965 (62 ans à 62 ans et 9 mois) gardent le leur, une « convergence » vers 63 ans ne les faisant pas reculer. Le "
        "calendrier de la convergence n'étant pas donné, la cible s'applique d'emblée. La durée requise (172 trimestres à partir de la génération "
        "1966), l'âge du taux plein automatique (67 ans), la décote, la surcote et les carrières longues ne changent pas : la source n'en parle pas. "
        "Dans le moteur, l'âge du taux plein ne change donc pour aucun salarié qui a cotisé sans interruption : commencer à 21 ans ou plus mène aux "
        "172 trimestres à 64 ans ou plus, et commencer avant amène déjà, par les carrières longues, à un départ à 63 ans au plus (borne de 21 ans). "
        "La mesure ouvre un départ dès 63 ans avec une décote. Le minimum de pension à 1 200 € est la mesure minimum_pension_1200."
    ),
    retraites=retraites,
    a_confirmer=True,  # aucun document de Place publique ou de la campagne ne porte l'âge de 63 ans ; le projet « Acte un » parle d'abroger la réforme de 2023
    hypotheses=(
        "La prise en compte de la pénibilité et la retraite progressive ne sont pas simulées : la source ne les détaille pas, et le persona ne dit ni "
        "à quels risques il est exposé ni s'il veut réduire son temps de travail avant de partir. Chaque salarié part au taux plein : le départ à "
        "63 ans avec décote, que la mesure permet, n'est pas choisi. La carrière et le salaire sont tenus fixes ; ni l'emploi des seniors, ni le "
        "financement, que le rapport juge non bouclé, ne sont calculés."
    ),
)
