from simulator.mesures import Mesure

PLAFOND = 3000


def plafond_a(montant: float):
    """Porte le plafond général de l'avantage en impôt par demi-part de quotient familial à ce montant, à partir de 2025."""

    def appliquer(reforme):
        def modifier(parametres):
            demi_part = parametres.impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part
            demi_part.general.update(start="2025-01-01", value=montant)
            return parametres

        reforme.modify_parameters(modifier_function=modifier)

    return appliquer


MESURE = Mesure(
    id="plafond_quotient_familial_3000",
    titre="Plafond du quotient familial porté à 3 000 € par demi-part",
    candidats=("Nicolas Dupont-Aignan",),
    source="https://www.debout-la-france.fr/projet/famille/",
    citation="Restaurer les avantages familiaux supprimés ou amoindris. [...] En revalorisant le quotient familial à 3 000 € par demi-part.",
    traduction=(
        "Page « Famille » du projet de Debout la France, non datée, de 2026 (© 2026 ; la page « Économie et travail » du même projet cite des "
        "chiffres de 2026), consultée le 31 octobre 2026. Revaloriser « le quotient familial à 3 000 € par demi-part » s'entend du plafond de "
        "l'avantage en impôt procuré par chaque demi-part : le nombre de parts n'a pas de montant. Le projet de 2022 voulait le « rétablissement au "
        "niveau de 2012 des allocations et quotients familiaux » (100 décisions pour la France, décision 64, "
        "https://www.debout-la-france.fr/wp-content/uploads/2022/07/100-Decisions-pour-la-France_VFIN.pdf), soit le plafond de 2 336 € d'avant la "
        "loi de finances pour 2013 ; la page de 2026, plus récente et chiffrée, prime. À partir du 1er janvier 2025, le plafond général par demi-part au-delà des parts des adultes "
        "(article 197 du CGI) passe de 1 807 € à 3 000 €. Les plafonds particuliers (première part d'un parent isolé, 4 262 €, demi-part des "
        "personnes seules ayant élevé un enfant) ne changent pas : la source ne parle que du quotient familial en général. Seuls les foyers dont "
        "l'avantage dû aux enfants dépasse le plafond actuel y gagnent, au plus 1 193 € par demi-part."
    ),
    appliquer=plafond_a(PLAFOND),
    a_confirmer=True,  # page du projet non datée
    hypotheses="Les effets sur la natalité et sur l'activité des parents ne sont pas calculés, pas plus que le financement de la mesure.",
)
