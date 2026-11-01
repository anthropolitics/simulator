from openfisca_core.model_api import Variable

from simulator.mesures import Mesure

TAUX = 0.025
SEUIL_NET_MENSUEL = 2000


def appliquer(reforme):
    deductible = reforme.variables["csg_deductible_salaire"].get_formula("2025-01-01")
    imposable = reforme.variables["csg_imposable_salaire"].get_formula("2025-01-01")

    def concerne(individu, period, parameters):
        # Salaire net du mois avec la CSG de la loi actuelle : la baisse ne doit pas faire sortir de la mesure ceux qu'elle fait passer au-dessus.
        net = individu("salaire_de_base", period) + individu("cotisations_salariales", period) + individu("crds_salaire", period)
        return (net + deductible(individu, period, parameters) + imposable(individu, period, parameters)) < SEUIL_NET_MENSUEL

    class csg_deductible_salaire(Variable):
        def formula_2025_01_01(individu, period, parameters):
            return deductible(individu, period, parameters) * (1 - concerne(individu, period, parameters))

    class csg_imposable_salaire(Variable):
        def formula_2025_01_01(individu, period, parameters):
            taux_actuel = parameters(period).prelevements_sociaux.contributions_sociales.csg.activite.imposable
            return imposable(individu, period, parameters) * (1 + concerne(individu, period, parameters) * (TAUX / taux_actuel - 1))

    reforme.update_variable(csg_deductible_salaire)
    reforme.update_variable(csg_imposable_salaire)


MESURE = Mesure(
    id="csg_2_5_pourcent_salaires_moins_2000_net",
    titre="CSG ramenée de 9,2 % à 2,5 % sur les salaires de moins de 2 000 € net par mois",
    candidats=("Éric Zemmour",),
    source="https://www.institutmontaigne.org/presidentielle-2022/eric-zemmour/baisser-le-taux-de-la-csg-sur-les-revenus-dactivite-de-92-a-25",
    citation="« Je propose donc une baisse de la CSG pour les salaires de moins de 2000€. Cette baisse représenterait un 13e mois. »",
    traduction=(
        "Mesure de la campagne de 2022 : le programme d'alors (programme.zemmour2022.fr, redirigé vers programme.ericzemmour.fr) refuse l'accès "
        "(erreur 403) et Reconquête n'a publié aucun programme pour 2027 ; la mesure est connue par la fiche de l'Institut Montaigne, qui cite "
        "le candidat sur RTL (https://twitter.com/ZemmourEric/status/1471010643486683137) et retient, d'après l'équipe de campagne, une baisse "
        "du taux de CSG sur les revenus d'activité de 9,2 % à 2,5 % sous 2 000 € net par mois ; sources consultées le 31 octobre 2026. Le "
        "rapport « Présidentielle 2027 — Analyse des programmes » (28 octobre 2026, p. 51) ne cite qu'une « baisse des impôts ». À partir du 1er "
        "janvier 2025, un salarié dont le salaire net du mois, calculé avec la CSG de la loi actuelle, est inférieur à 2 000 € paie la CSG à "
        "2,5 % au lieu de 9,2 % sur la même assiette (98,25 % du salaire brut). L'Institut Montaigne rapporte que l'équipe de campagne envisage "
        "une hausse du taux par tranches sous le seuil, qu'elle n'a pas publiée : le calcul applique la mesure telle qu'annoncée, avec un effet "
        "de seuil à 2 000 € net, au-delà duquel rien ne change. Comme l'Institut Montaigne, il supprime la part déductible (6,8 points) et "
        "porte la part non déductible de 2,4 % à 2,5 %. Le salaire imposable monte donc de la CSG déductible supprimée, et l'impôt sur le "
        "revenu avec lui. La CRDS ne change pas. Les revenus d'activité des indépendants, que vise aussi la mesure, ne sont pas simulés, le "
        "persona n'ayant que des salaires ; les revenus de remplacement (chômage, retraites) ne sont pas concernés."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # mesure de la campagne de 2022, connue par une source secondaire ; aucun programme 2027
    hypotheses=(
        "L'effet de seuil pourrait conduire des salariés juste au-dessus de 2 000 € net à négocier un salaire plus bas : ce comportement n'est "
        "pas simulé, pas plus que le financement annoncé (suppression des prestations non contributives aux étrangers hors Union européenne) "
        "ni les effets sur l'emploi et les salaires négociés."
    ),
)
