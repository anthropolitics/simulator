from simulator.mesures import Mesure

PARTS_DEUXIEME_ENFANT = 1  # une part au lieu d'une demi-part


def appliquer(reforme):
    def modifier(parametres):
        quotient = parametres.impot_revenu.calcul_impot_revenu.plaf_qf.quotient_familial
        quotient.cas_general.enf2.update(start="2025-01-01", value=PARTS_DEUXIEME_ENFANT)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="part_fiscale_deuxieme_enfant",
    titre="Part fiscale complète dès le deuxième enfant",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/22-mesures",
    citation="Instituer une part fiscale complète dès le deuxième enfant.",
    traduction=(
        "Mesure 8 des « 22 mesures » de la campagne de 2022 ; le livret « La famille » de 2022 précise « une part fiscale pleine, contre une "
        "demi-part actuellement, pour le deuxième enfant » (https://rassemblementnational.fr/documents/projet/projet-la-famille.pdf, p. 7). Le "
        "programme des législatives de 2024 la reprend mot pour mot (https://rassemblementnational.fr/documents/202406-programme.pdf#page=9) et le "
        "contre-budget 2026 du groupe RN, présenté le 23 octobre 2025, la chiffre à 2,86 Md€ (« Part fiscale pleine dès le deuxième enfant », "
        "https://rassemblementnational.fr/documents/GRN-CONTRE-BUDGET-2026.pdf#page=7). Pour 2027, elle figure dans la trajectoire budgétaire "
        "présentée par la candidate le 6 octobre 2026 : LCP rapporte la promesse « d'octroyer une part fiscale pleine dès le deuxième enfant » "
        "(https://lcp.fr/actualites/permis-de-conduire-gratuit-exoneration-d-impot-jusqu-a-30-ans-comment-le-rn-veut, 6 octobre 2026) et "
        "l'Institut de l'Entreprise la relève dans le dossier de presse du même jour, qui n'est pas en ligne "
        "(https://www.institut-entreprise.fr/wp-content/uploads/2026/10/Analyse-primaire-contre-budget-RN-Note-de-contexte-IDEP.pdf) ; sources "
        "consultées le 31 octobre 2026. À partir du 1er janvier 2025, le deuxième enfant à charge apporte une part de quotient familial au lieu "
        "d'une demi-part (paramètre enf2 de 0,5 à 1, article 194 du CGI) ; le troisième enfant et les suivants en apportent déjà une. Les sources "
        "ne parlent pas du plafonnement : chaque demi-part due aux enfants reste plafonnée par la loi actuelle (1 807 € d'avantage en impôt pour "
        "le plafond général), si bien que la demi-part nouvelle rapporte au plus 1 807 € par an. Un parent isolé suit la même règle : son "
        "deuxième enfant apporte une part."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # le dossier de presse du 6 octobre 2026 n'est connu que par la presse et une note de l'Institut de l'Entreprise
    hypotheses="Les effets sur la natalité et sur l'activité des parents ne sont pas calculés, pas plus que le financement de la mesure.",
)
