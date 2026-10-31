from openfisca_core.model_api import MONTH, Variable, max_, not_, where
from openfisca_france.entities import Famille, Individu

from simulator.mesures import Mesure, ajouter_prestation

SOCLE, INSERTION = 300, 250
RETENUE_SUR_SALAIRE = 0.30
REMPLACES = ("rsa", "ppa", "ass")


class revenu_incitation_activite(Variable):
    value_type = float
    entity = Individu
    definition_period = MONTH
    label = "Revenu d'incitation à l'activité (RIA)"

    def formula(individu, period):
        age = individu("age", period)
        salaire = individu("salaire_net", period)
        complement = max_(SOCLE + INSERTION - RETENUE_SUR_SALAIRE * salaire, 0)
        sans_salaire = (SOCLE + INSERTION * individu("insertion_15h", period.this_year)) * (individu("retraite_nette", period) == 0)
        adulte = (age >= 18) * (age < 65) * not_(individu.has_role(Famille.ENFANT))
        return adulte * where(salaire > 0, complement, sans_salaire)


def appliquer(reforme):
    ajouter_prestation(reforme, revenu_incitation_activite)
    for variable in REMPLACES:
        reforme.neutralize_variable(variable)


MESURE = Mesure(
    id="revenu_incitation_activite",
    titre="Revenu d'incitation à l'activité (RIA) à la place du RSA, de la prime d'activité et de l'ASS",
    candidats=("Bruno Retailleau",),
    source="https://republicains.fr/wp-content/uploads/2026/01/51705_LesRepublicains_Brochures_A5-40P_DEF.pdf",
    citation=(
        "Pour lever ces freins, nous proposons la création d'un Revenu d'incitation à l'activité (RIA), en remplacement de trois dispositifs "
        "existants : le RSA, la prime d'activité et l'allocation de solidarité spécifique (ASS). [...] Une personne adulte de moins de 65 ans, sans "
        "activité et sans revenu, en situation régulière, perçoit un « RIA Socle » de 300 euros par mois. Si elle s'investit dans une formation ou "
        "une recherche active d'emploi, justifiant d'au moins quinze heures d'activité hebdomadaires, son RIA est complété par un « RIA Insertion » "
        "de 250 euros par mois. Si elle reprend une activité, son allocation devient un complément de rémunération, calculé en additionnant RIA Socle "
        "et RIA Insertion et en déduisant 30 % de son salaire. [...] Lorsque sa rémunération progresse et que ses revenus d'activité dépassent 1 833 "
        "euros par mois, le RIA s'annule [...] Contrairement au RSA et à la Prime d'activité, le RIA ne dépend pas de la situation familiale et "
        "n'interfère ni avec les allocations familiales ni avec les aides au logement."
    ),
    traduction=(
        "Livret « Travail gagnant », proposition 2 (p. 23-24). Les variables rsa, ppa et ass sont neutralisées et, en 2025, chaque adulte de 18 à 64 "
        "ans du persona reçoit, chaque mois, une prestation individuelle calculée sans regard pour son conjoint ni ses enfants : s'il a un salaire, "
        "550 € moins 30 % de son salaire net (montant nul au-delà de 1 833 € net, comme l'écrit la source) ; sans salaire ni pension de retraite, 300 "
        "€ (RIA Socle), plus 250 € (RIA Insertion) si l'adulte déclare au moins 15 heures par semaine de formation ou de recherche active d'emploi. "
        "Avec un salaire, le complément additionne RIA Socle et RIA Insertion, que l'adulte déclare ou non ces 15 heures, comme l'écrit la "
        "source. Les enfants à charge, même majeurs, n'y ouvrent pas droit, la source ne visant que les adultes du foyer. Le RIA n'est ni imposable "
        "ni compté dans les ressources des aides au logement. La condition de séjour régulier n'est pas simulée. La prime de Noël, réservée aux "
        "allocataires du RSA et de l'ASS, n'a plus d'allocataires : la source ne dit pas si elle est étendue au RIA."
    ),
    appliquer=appliquer,
    hypotheses=(
        "Les heures travaillées et les reprises d'emploi que le RIA vise à encourager ne sont pas simulées : le salaire du persona est tenu fixe. Le "
        "plafonnement des aides par le compte social unique, autre proposition du même livret, n'est pas inclus. Le financement n'est pas calculé."
    ),
)
