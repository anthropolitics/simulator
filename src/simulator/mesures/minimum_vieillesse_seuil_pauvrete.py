from simulator.mesures import Mesure

SEUIL_PAUVRETE = 1337  # par mois, pour une personne seule, selon le contre-budget de LFI du 14 octobre 2026 (p. 8)
UC_COUPLE = 1.5  # unités de consommation d'un couple sans enfant, échelle de l'Insee


def appliquer(reforme):
    def modifier(parametres):
        aspa = parametres.prestations_sociales.solidarite_insertion.minimum_vieillesse.aspa
        for parametre in (aspa.montant_maximum_annuel, aspa.plafond_ressources):
            parametre.personnes_seules.update(start="2025-01-01", value=12 * SEUIL_PAUVRETE)
            parametre.couples.update(start="2025-01-01", value=12 * SEUIL_PAUVRETE * UC_COUPLE)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="minimum_vieillesse_seuil_pauvrete",
    titre="Minimum vieillesse au niveau du seuil de pauvreté (1 337 € par mois pour une personne seule)",
    candidats=("Jean-Luc Mélenchon",),
    source="https://melenchon2027.fr/wp-content/uploads/2026/04/PROGRAMME-FRONT-POPULAIRE.pdf",
    citation=(
        "« Augmenter le minimum contributif (pension de retraite pour une carrière complète) au niveau du SMIC et le minimum vieillesse au niveau du "
        "seuil de pauvreté » (programme du Nouveau Front populaire, juin 2024, p. 4)"
    ),
    traduction=(
        "Le programme du Nouveau Front populaire de 2024 est publié sur le site de campagne melenchon2027.fr (consulté le 31 octobre 2026). Le "
        "contre-budget de LFI du 14 octobre 2026 (« Comment nous allons remettre de l'ordre dans les comptes publics », "
        "https://melenchon2027.fr/wp-content/uploads/2026/10/Comment-nous-allons-remettre-de-l-ordre-dans-les-comptes-publics.pdf) reprend le "
        "minimum de pension au niveau du SMIC (voir retraite_60_ans_40_annuites) mais ne parle pas du minimum vieillesse ; il fixe le seuil de "
        "pauvreté « à 1 337 euros par mois » (p. 8), montant retenu ici. Le minimum vieillesse est l'allocation de solidarité aux personnes âgées "
        "(ASPA), allocation différentielle. À partir du 1er janvier 2025, son montant maximal et son plafond de ressources passent, pour une "
        "personne seule, de 12 411,44 € à 12 × 1 337 = 16 044 € par an, et, pour un couple, de 19 268,80 € à 1,5 × 16 044 = 24 066 € par an : la "
        "source ne dit rien des couples, et le seuil de pauvreté d'un couple sans enfant vaut 1,5 fois celui d'une personne seule (échelle de "
        "l'Insee). Les autres règles de l'ASPA (âge de 65 ans, ressources prises en compte, abattement sur les revenus d'activité) ne changent pas."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # programme de 2024 ; aucun document de la campagne 2027 lu ne porte le minimum vieillesse
    hypotheses=(
        "Le recours à l'ASPA est supposé complet ; la récupération de l'allocation sur la succession, le financement et les effets sur la décision "
        "de liquider sa retraite ne sont pas calculés."
    ),
)
