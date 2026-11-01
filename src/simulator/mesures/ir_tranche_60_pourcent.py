from openfisca_core.parameters import ParameterScaleBracket

from simulator.mesures import Mesure
from simulator.persona import ANNEE

SEUIL = 250_000  # euros par part et par an
TAUX = 0.60


def appliquer(reforme):
    def modifier(parametres):
        debut = f"{ANNEE}-01-01"
        donnees = {"threshold": {debut: {"value": SEUIL}}, "rate": {debut: {"value": TAUX}}}  # sans valeur avant 2025 : la tranche n'existe pas
        parametres.impot_revenu.bareme_ir_depuis_1945.bareme.brackets.append(ParameterScaleBracket("tranche_60_pourcent", data=donnees))
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="ir_tranche_60_pourcent",
    titre="Tranche de l'impôt sur le revenu à 60 % au-delà de 250 000 € par part",
    candidats=("Marine Tondelier",),
    source="https://lesecologistes.fr/document/3N4JsAEmq6vsx42IITGNZa/vdef-programme-1.pdf",
    citation="Tranche d'impôt sur le revenu à 60 % au-delà de 250 000 euros.",
    traduction=(
        "Citation du programme « Pour une prospérité écologique » (juillet 2026), rubrique « Fiscalité du patrimoine et des entreprises », telle "
        "que la reproduit https://lacampagne2027.com/candidats/marine-tondelier (consulté le 31 octobre 2026) en renvoyant au PDF du programme "
        "daté du 15 juillet 2026 ; ce PDF et la page du projet des Écologistes n'ont pas pu être lus (accès refusé). Une sixième tranche est "
        "ajoutée au barème OpenFisca (impot_revenu.bareme_ir_depuis_1945.bareme) appliqué aux revenus 2025 : 60 % sur la fraction du revenu "
        "imposable par part qui dépasse 250 000 €. La source ne dit pas si le seuil s'entend par part ou par foyer ; il est lu par part, comme "
        "tous les seuils du barème, auquel s'applique le quotient familial. Les autres tranches (0, 11, 30, 41 et 45 %), le plafonnement du "
        "quotient familial, la décote et la contribution exceptionnelle sur les hauts revenus restent ceux de la loi 2025."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # citation lue chez un tiers, le programme lui-même n'a pas pu être consulté
    hypotheses=(
        "Les revenus déclarés sont tenus fixes : la baisse de l'offre de travail, l'optimisation (rémunération en dividendes ou en plus-values, "
        "soumises au prélèvement forfaitaire et non au barème) et les départs que le taux de 60 % pourrait entraîner ne sont pas calculés."
    ),
)
