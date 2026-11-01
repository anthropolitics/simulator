from simulator.mesures import Mesure

TAUX_DEDUCTIBLE = 0.042  # 6,6 % au total avec les 2,4 % non déductibles, comme le taux médian des pensions de retraite


def appliquer(reforme):
    def baisser(parametres):
        parametres.prelevements_sociaux.contributions_sociales.csg.activite.deductible.update(start="2025-01-01", value=TAUX_DEDUCTIBLE)
        return parametres

    reforme.modify_parameters(modifier_function=baisser)


MESURE = Mesure(
    id="csg_activite_6_6_pourcent",
    titre="CSG sur les revenus d'activité abaissée de 9,2 % à 6,6 %",
    candidats=("David Lisnard",),
    source="https://www.unenouvelleenergie.fr/david-lisnard-sur-cnews-et-europe-1-je-ne-suis-pas-candidat-pour-un-poste-je-viens-pour-redresser-le-pays/",
    citation=(
        "Pouvoir d'achat : baisser la CSG de 9,2 % à 6,6 % pour augmenter les salaires nets. Il propose d'abaisser la contribution sociale "
        "généralisée (CSG) sur les revenus d'activité de 9,2 % à 6,6 % afin d'augmenter directement le salaire net des travailleurs, sans alourdir "
        "le coût du travail pour les entreprises."
    ),
    traduction=(
        "Compte rendu de l'entretien du 27 octobre 2026 sur CNews et Europe 1, publié le 28 octobre 2026 sur le site de Nouvelle Énergie, le parti du "
        "candidat (consulté le 31 octobre 2026) ; le candidat y présente le taux de 6,6 % comme un alignement sur celui des revenus de remplacement. "
        "Sur un salaire, la CSG compte 6,8 % déductibles de l'impôt sur le revenu et 2,4 % non déductibles. Le calcul abaisse, à partir du 1er janvier "
        "2025, la part déductible de 6,8 % à 4,2 % et garde les 2,4 % non déductibles, soit la répartition du taux de 6,6 % des pensions de retraite "
        "(4,2 % et 2,4 %), auquel la mesure s'aligne. L'assiette (98,25 % du salaire brut jusqu'à 4 plafonds de la sécurité sociale) ne change pas : "
        "le salaire net gagne 2,55 % du brut, 46 € par mois au SMIC ; la part déductible baissant, le salaire imposable et l'impôt sur le revenu "
        "augmentent un peu. Les revenus d'activité des indépendants, qu'OpenFisca taxe au même taux, baissent aussi ; ceux du persona ne sont que des "
        "salaires. La CRDS et la CSG sur les revenus de remplacement et du capital ne changent pas. Le rapport « Présidentielle 2027 — Analyse des "
        "programmes » (28 octobre 2026, p. 35) chiffre « 45 € net par mois » au SMIC pour une « baisse de 3 points des cotisations salariales » : ce "
        "gain est celui de cette baisse de CSG."
    ),
    appliquer=appliquer,
    hypotheses=(
        "Le financement annoncé (réduction du nombre d'organismes publics, économies de 200 milliards d'euros) n'est pas calculé, pas plus que la "
        "compensation des recettes de la sécurité sociale et les effets sur l'emploi et les salaires négociés."
    ),
)
