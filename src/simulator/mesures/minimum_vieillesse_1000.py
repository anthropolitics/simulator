from simulator.mesures import Mesure

MONTANT_ANNUEL = 12 * 1000


def appliquer(reforme):
    def modifier(parametres):
        aspa = parametres.prestations_sociales.solidarite_insertion.minimum_vieillesse.aspa
        for parametre in (aspa.montant_maximum_annuel.personnes_seules, aspa.plafond_ressources.personnes_seules):
            parametre.update(start="2025-01-01", value=max(parametre("2025-01-01"), MONTANT_ANNUEL))
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="minimum_vieillesse_1000",
    titre="Minimum vieillesse à 1 000 € par mois",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/22-mesures",
    citation="Revaloriser le minimum vieillesse à 1 000 € par mois et augmenter les petites retraites",
    traduction=(
        "Le minimum vieillesse désigne l'allocation de solidarité aux personnes âgées (ASPA) d'une personne seule, la source ne disant pas que le "
        "montant vise chaque membre d'un couple. À partir du 1er janvier 2025, le montant maximal et le plafond de ressources de l'ASPA d'une "
        "personne seule sont portés à 12 000 € par an s'ils sont inférieurs. La mesure date de la présidentielle 2022, quand l'ASPA valait "
        "916,78 € par mois ; en 2025 elle vaut 1 034,28 € : la mesure ne change rien. Le volet « augmenter les petites retraites » ne dit ni "
        "lesquelles ni de combien, il n'est pas simulé."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # document de la campagne 2022, que seule une source de 2026 rattache au programme 2027
    hypotheses="Aucun effet de comportement : la mesure ne change aucun montant de la loi 2025.",
)
