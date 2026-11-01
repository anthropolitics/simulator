from openfisca_core.model_api import ADD, Variable

from simulator.mesures import Mesure

# Revenu catégoriel de l'impôt sur le revenu, et revenus dont il retire la CSG non déductible et la CRDS.
CATEGORIES = {"revenu_assimile_salaire": ("salaire", "chomage"), "revenu_assimile_pension": ("retraite",)}


def deductible(categorie, revenus, actuelle):
    def formula_2025_01_01(individu, period, parameters, actuelle=actuelle):
        imposable = actuelle(individu, period) if actuelle.__code__.co_argcount == 2 else actuelle(individu, period, parameters)
        # Montants négatifs : les ajouter les retire du revenu imposable, sans changer le revenu net.
        return imposable + sum(individu(f"{prelevement}_{revenu}", period, options=[ADD]) for revenu in revenus for prelevement in ("csg_imposable", "crds"))

    return type(categorie, (Variable,), {"formula_2025_01_01": formula_2025_01_01})


def appliquer(reforme):
    for categorie, revenus in CATEGORIES.items():
        reforme.update_variable(deductible(categorie, revenus, reforme.variables[categorie].get_formula("2025-01-01")))


MESURE = Mesure(
    id="csg_crds_deductibles",
    titre="CSG et CRDS entièrement déductibles de l'impôt sur le revenu",
    candidats=("David Lisnard",),
    source="https://atlantico.fr/article/decryptage/changer-de-logiciel-fiscal-david-lisnard",
    citation="Déductibilité complète de la CSG et de la CRDS de l'impôt sur le revenu.",
    traduction=(
        "Tribune du candidat « Changer de logiciel fiscal », Atlantico, 13 avril 2026. Elle n'est pas lisible sans abonnement : la citation est celle "
        "du résumé qu'en fait Le Cahier d'Uniquien (https://lecahierdauniquien.substack.com/p/changer-de-logiciel-fiscal-que-valent, 19 avril 2026, "
        "consulté le 31 octobre 2026), qui range la mesure dans une refonte de l'impôt sur le revenu à progressivité « modérée » sans en donner le "
        "barème. Aujourd'hui, sur un salaire, 6,8 points des 9,2 % de CSG sont déductibles du revenu imposable ; les 2,4 points restants et la CRDS "
        "(0,5 %) ne le sont pas. Sur une pension, 5,9 points des 8,3 % le sont, sur une allocation chômage 3,8 points des 6,2 %. À partir du 1er "
        "janvier 2025, la CSG non déductible et la CRDS sont retirées des salaires, allocations chômage et pensions que retient l'impôt sur le "
        "revenu (variables revenu_assimile_salaire et revenu_assimile_pension), comme la CSG déductible, avant l'abattement de 10 % ; le salaire "
        "net ne change pas. Sur un salaire, le revenu imposable baisse de 2,85 % du brut (2,9 % de 98,25 % du brut) avant cet abattement. Les "
        "revenus du capital, que le persona ne déclare pas, ne changent pas. Le reste de la refonte de l'impôt sur le revenu (« ajustement de la "
        "tranche à 30 % ») n'est pas chiffré par la source et n'est pas simulé."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # la tribune n'est connue que par un résumé
    hypotheses="Le financement de la baisse d'impôt n'est pas calculé, pas plus que ses effets sur l'activité.",
)
