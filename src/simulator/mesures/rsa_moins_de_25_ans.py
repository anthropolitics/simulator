from openfisca_core.model_api import Variable, not_
from openfisca_france.entities import Famille

from simulator.mesures import Cout, Mesure

AGE_MINIMUM = 18


def appliquer(reforme):
    actuelle = reforme.variables["rsa_eligibilite"].get_formula("2025-01-01")

    class rsa_eligibilite(Variable):
        def formula_2025_01_01(famille, period, parameters):
            # La loi 2025 exige 25 ans d'un parent sans enfant ; les autres conditions (nationalité, non-étudiant) restent celles d'aujourd'hui.
            individu = famille.members
            majeur = famille.any((individu("age", period) >= AGE_MINIMUM) * not_(individu("etudiant", period)), role=Famille.PARENT)
            nationalite = famille.any(individu("rsa_condition_nationalite", period), role=Famille.PARENT)
            return actuelle(famille, period, parameters) + majeur * nationalite * famille("rsa_eligibilite_tns", period)

    reforme.update_variable(rsa_eligibilite)


MESURE = Mesure(
    id="rsa_moins_de_25_ans",
    titre="RSA ouvert aux moins de 25 ans, dès 18 ans",
    candidats=("Fabien Roussel",),
    source="https://d3n8a8pro7vhmx.cloudfront.net/fabienroussel2022/pages/217/attachments/original/1643038967/exe_la_france_des_jours_heureux_LIVRE_stc.pdf",
    citation=(
        "« 42 Le revenu de solidarité active (RSA) sera ouvert aux moins de 25 ans. En prenant immédiatement cette mesure, la nouvelle majorité "
        "politique manifestera qu'elle entend réparer une injustice criante. » (La France des Jours heureux, 2022)"
    ),
    traduction=(
        "Proposition 42 du programme de Fabien Roussel pour 2022, « La France des Jours heureux » (consulté le 31 octobre 2026) ; votons-2027.fr "
        "(https://votons-2027.fr/candidats/roussel/programme) le présente comme son programme de 2027, et le discours de l'université d'été du "
        "PCF d'août 2026 (https://www.pcf74.fr/2026/08/universite-d-ete-2026-discours-de-fabien-roussel.html) n'en parle pas. Aujourd'hui, un "
        "allocataire du RSA sans enfant doit avoir 25 ans (paramètre rsa_cond.age_pac). À partir du 1er janvier 2025, la famille est aussi éligible "
        "si un parent a au moins 18 ans, âge que la source ne donne pas mais qui est celui de la majorité et de la prime d'activité, et n'est pas "
        "étudiant, avec les mêmes conditions de nationalité ou de séjour qu'aujourd'hui (variable rsa_eligibilite). Le montant, les ressources "
        "prises en compte et le forfait logement sont ceux de la loi 2025. Un enfant de 18 à 24 ans à la charge du foyer reste compté comme "
        "enfant et n'ouvre pas de droit à part, le persona ne le décrivant pas comme un foyer distinct."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # programme de 2022 ; aucun document de la campagne 2027 lu ne porte la mesure
    hypotheses=(
        "Le recours au RSA est supposé complet. Les effets sur l'emploi et la poursuite d'études des jeunes, et le coût pour les départements, ne "
        "sont pas calculés."
    ),
    cout=Cout(
        1.2,
        6.6,
        "De 1,2 à 3,8 Md€ selon le recours, pour les 18-25 ans non étudiants, d'après la DREES en 2012, et 6,6 Md€ au plus selon la direction "
        "générale du Trésor, cités par le rapport Sirugue de 2016 (https://www.vie-publique.fr/files/rapport/pdf/164000239.pdf) ; 5,8 Md€ nets pour "
        "1,4 million de jeunes selon la DREES en 2016, citée par le rapport n° 267 du Sénat de 2021 "
        "(https://www.senat.fr/rap/l20-267/l20-2671.pdf). Montants de 2012 à 2016 ; le candidat ne chiffre pas la mesure. Sources consultées le 20 "
        "novembre 2026.",
    ),
)
