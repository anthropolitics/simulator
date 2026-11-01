from simulator.mesures import Mesure

MESURE = Mesure(
    id="suppression_ifi",
    titre="Suppression de l'impôt sur la fortune immobilière (IFI)",
    candidats=("David Lisnard",),
    source="https://atlantico.fr/article/decryptage/changer-de-logiciel-fiscal-david-lisnard",
    citation="Suppression de l'IFI ; refonte de la fiscalité foncière sur la base de valeurs vénales actualisées.",
    traduction=(
        "Tribune du candidat « Changer de logiciel fiscal », Atlantico, 13 avril 2026. Elle n'est pas lisible sans abonnement : la citation est celle "
        "du résumé qu'en fait Le Cahier d'Uniquien (https://lecahierdauniquien.substack.com/p/changer-de-logiciel-fiscal-que-valent, 19 avril 2026, "
        "consulté le 31 octobre 2026). À partir du 1er janvier 2025, l'IFI (variable isf_ifi) est annulé. La refonte de la fiscalité foncière sur "
        "des valeurs vénales, que le candidat a reprise sur CNews le 27 octobre 2026 en parlant seulement d'une « possibilité » de prendre en compte "
        "la valeur vénale des biens pour la taxe foncière "
        "(https://www.unenouvelleenergie.fr/david-lisnard-sur-cnews-et-europe-1-je-ne-suis-pas-candidat-pour-un-poste-je-viens-pour-redresser-le-pays/), "
        "n'a ni assiette ni taux : elle n'est pas simulée, et la taxe foncière n'est pas dans le simulateur."
    ),
    appliquer=lambda reforme: reforme.neutralize_variable("isf_ifi"),
    a_confirmer=True,  # la tribune n'est connue que par un résumé
    hypotheses=(
        "Le calcul suppose un patrimoine déclaré et évalué sans changement de comportement. Une taxe foncière refondue sur les valeurs vénales, qui "
        "pourrait reprendre une part de l'IFI supprimé, n'est pas simulée."
    ),
)
