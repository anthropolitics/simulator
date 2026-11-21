from simulator.mesures import Cout, Mesure
from simulator.persona import ANNEE

# Seuil bas de chaque tranche, en euros par part et par an, et taux marginal.
BAREME = (
    (0, 0.03),
    (7_200, 0.04),
    (10_800, 0.065),
    (15_600, 0.085),
    (19_200, 0.105),
    (22_800, 0.125),
    (27_600, 0.23),
    (32_400, 0.25),
    (37_200, 0.29),
    (43_200, 0.32),
    (60_000, 0.40),
    (96_000, 0.53),
    (180_000, 0.60),
    (396_000, 0.70),
)


def appliquer(reforme):
    def modifier(parametres):
        tranches = parametres.impot_revenu.bareme_ir_depuis_1945.bareme.brackets
        assert len(tranches) == len(BAREME)
        for tranche, (seuil, taux) in zip(tranches, BAREME):
            tranche.threshold.update(start=f"{ANNEE}-01-01", value=seuil)
            tranche.rate.update(start=f"{ANNEE}-01-01", value=taux)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="ir_14_tranches",
    titre="Barème de l'impôt sur le revenu à 14 tranches",
    candidats=("Jean-Luc Mélenchon",),
    source="https://desintox.lafranceinsoumise.fr/vous-voulez-augmenter-les-impots/",
    citation=(
        "Notre révolution fiscale modifie d'abord le barème de l'impôt sur le revenu (IR) pour intégrer quatorze tranches, comme en 1983, "
        "contre cinq actuellement. […] Si vous voulez calculer combien vous paierez d'impôt avec la France insoumise, nous avons fait un "
        "simulateur : https://impots.lafranceinsoumise.fr/ ."
    ),
    traduction=(
        "Ni le programme ni le contre-budget du 14 octobre 2026 (« Nous réformerons l'impôt sur le revenu au cours du mandat pour le rendre "
        "plus progressif avec l'instauration de 14 tranches ») ne publient les seuils et les taux. Ils sont lus dans le code du simulateur "
        "impots.lafranceinsoumise.fr, vers lequel renvoie la page citée (mise à jour le 12 mars 2026) et qui porte encore le titre « Nouveau "
        "Front populaire » : seuils par part et par an de 0, 7 200, 10 800, 15 600, 19 200, 22 800, 27 600, 32 400, 37 200, 43 200, 60 000, "
        "96 000, 180 000 et 396 000 €, taux marginaux de 3 ; 4 ; 6,5 ; 8,5 ; 10,5 ; 12,5 ; 23 ; 25 ; 29 ; 32 ; 40 ; 53 ; 60 et 70 %. Ces 14 "
        "tranches remplacent les 5 tranches du barème OpenFisca (impot_revenu.bareme_ir_depuis_1945.bareme) appliqué aux revenus 2025, sans "
        "indexation des seuils. Comme dans ce simulateur, le quotient familial, son plafonnement, la décote et les autres règles de l'impôt "
        "restent ceux de la loi 2025. Le code de ce simulateur modifie ensuite le montant obtenu pour certains niveaux de revenu et certaines "
        "situations familiales ; ces ajustements ne font pas partie du barème et ne sont pas reproduits."
    ),
    appliquer=appliquer,
    a_confirmer=True,
    hypotheses=(
        "Le calcul ne tient pas compte des changements de comportement (offre de travail, optimisation, départs), ni du calendrier : le "
        "contre-budget prévoit la réforme « au cours du mandat ». La CSG à 14 tranches annoncée avec ce barème fait l'objet d'une mesure distincte."
    ),
    cout=Cout(
        -5.5,
        -2,
        "Avec la CSG progressive : 5,5 Md€ de recettes selon le contre-budget 2026 de La France insoumise "
        "(https://lafranceinsoumise.fr/wp-content/uploads/2025/10/Budget-2026_LFI_web_pages.pdf, p. 60) ; de 2 à 8 Md€ selon Lucas Chancel, "
        "Anne-Laure Delatte et Élise Huillery en juin 2024 "
        "(https://www.lagrandeconversation.com/app/uploads/2024/06/chiffrage-des-recettes-fiscales-du-programme-du-nouveau-front-populaire-la-grande-conversation.pdf). "
        "Pour le seul impôt sur le revenu, 4,7 Md€ selon l'Institut Montaigne en 2022 "
        "(https://www.institutmontaigne.org/presidentielle-2022/jean-luc-melenchon/rendre-limpot-sur-le-revenu-plus-progressif-avec-un-bareme-a-14-tranches). "
        "Sources consultées le 20 novembre 2026."
        " La recette retenue ne dépasse pas les 5,5 Md€ qu'annonce La France insoumise ; la fourchette des économistes va jusqu'à 8 Md€.",
        annonce=-5.5,
    ),
)
