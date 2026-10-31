"""Ménages types : des foyers calés sur les statistiques de l'Insee, pour publier ce que chaque programme leur fait.

Chaque ménage dit d'où vient chacune de ses valeurs. Un ménage par couleur de la charte : il la garde partout où il apparaît.

Les statistiques sont les dernières publiées au 31 octobre 2026, prises telles quelles, sans revalorisation : salaires de 2025,
pensions de décembre 2024, patrimoines du début de 2024. Les salaires nets sont convertis en brut par engine.brut_depuis_net
(salarié seul du privé, non cadre, à temps plein, loi 2025) ; le résultat est écrit en dur, le calcul prenant plusieurs secondes.
Un patrimoine est le patrimoine brut médian d'un groupe de l'enquête Patrimoine, réparti selon la composition et l'endettement
moyens de ce groupe, en parts du patrimoine brut ; la dette est déduite de la résidence principale, et un autre logement n'est
compté que si la majorité du groupe en détient un.
"""

from dataclasses import dataclass

from simulator.persona import Adulte, Persona


@dataclass(frozen=True)
class Menage:
    id: str
    prenom: str
    situation: str  # « Métier, ville, foyer », dans l'ordre de la charte
    couleur: str  # ocre, ardoise, sauge, prune, argile ou lin
    persona: Persona
    sources: str  # la source de chaque valeur du persona, et les choix faits quand elle manque


# Publications citées par plusieurs ménages.
SALAIRES = "Insee, « Les salaires dans le secteur privé en 2025 », Insee Première n° 2132, octobre 2026, https://www.insee.fr/fr/statistiques/9087193"
RETRAITES = (
    "Drees, « Les retraités et les retraites », édition 2026, octobre 2026, https://drees.solidarites-sante.gouv.fr (le site de la Drees ne "
    "répondait pas le 31 octobre 2026 : ouvrage lu sur la copie de l'UNSA Retraités, "
    "https://retraites.unsa.org/IMG/pdf/les_retraites_et_les_retraites_-_edition_2026-1.pdf)"
)
DEBUT_DE_CARRIERE = (
    f"âge moyen de première validation d'une année complète pour la retraite, 23,0 ans pour les femmes et 22,2 ans pour les hommes de la "
    f"génération 1976, la dernière publiée ({RETRAITES}, fiche 12) ; la Drees ne le publie ni par métier ni par diplôme"
)
NAISSANCES = (
    "âge moyen à la naissance des enfants en 2025, 31,2 ans pour les mères et 34,1 ans pour les pères (Insee, « Bilan démographique 2025 », "
    "Insee Première n° 2087, janvier 2026, https://www.insee.fr/fr/statistiques/8719824)"
)
ENFANTS = (
    "choix de 10 ans pour l'aîné, l'âge des enfants dans l'ancien format de l'API, aucune statistique ne donnant un âge type ; écart de 4 ans "
    "avec le cadet, la durée moyenne entre les deux premières naissances, « autour de 3,9 ans » depuis 1980 (Insee, « Un premier enfant à "
    "28 ans », Insee Première n° 1419, octobre 2012, https://www.insee.fr/fr/statistiques/1281068)"
)
LOGEMENT = (
    "Insee, « Conditions de logement début 2024 : les locataires sont moins bien lotis que les propriétaires », Insee Première n° 2090, "
    "janvier 2026, enquête Logement 2023-2024, https://www.insee.fr/fr/statistiques/8727513"
)
PATRIMOINE = (
    "Insee, enquête Histoire de vie et Patrimoine 2023-2024 : « Les montants de patrimoine détenus par les ménages en 2024 », Insee Focus "
    "n° 371, décembre 2025, https://www.insee.fr/fr/statistiques/8672665 ; « Patrimoine et endettement des ménages en 2024 », Insee "
    "Résultats, février 2026, https://www.insee.fr/fr/statistiques/8736842"
)
PATRIMOINE_DES_LOCATAIRES = (
    f"Patrimoine : 9 900 € de patrimoine financier, ni immobilier ni résidence principale. C'est le patrimoine brut médian des ménages "
    f"locataires, 20 800 € (Insee Focus n° 371, tableau complémentaire 4), multiplié par 47,4 %, la part du patrimoine financier des "
    f"ménages situés entre le 2e et le 3e décile de patrimoine brut (16 500 à 40 100 €), où l'immobilier ne pèse que 1,9 % (Insee Résultats, "
    f"« Montant de patrimoine brut moyen, décomposition par grandes composantes », onglet PATBRUT) ; leurs dettes, surtout des crédits "
    f"automobiles, vont avec le patrimoine résiduel (véhicules, équipement), que le persona ne décrit pas ({PATRIMOINE})."
)
PRENOMS = "Insee, Fichier des prénoms, édition juillet 2026, naissances de 1900 à 2025, fichier national, https://www.insee.fr/fr/statistiques/8595130"
PROFESSIONS = (
    "Insee, « Professions et secteurs d'activité », Emploi, chômage, revenus du travail, Insee Références, juin 2025, figure 1, "
    "https://www.insee.fr/fr/statistiques/8376826"
)
METIER = (
    "choix dans la catégorie socioprofessionnelle, les effectifs par métier de la Dares (« Portraits statistiques des métiers ») n'ayant pu "
    "être consultés, le site opposant une vérification anti-robot"
)
SANS_COMMUNE = "Pas de loyer, donc pas de code commune : la ville est un choix sans effet sur le calcul."

MENAGES: dict[str, Menage] = {
    m.id: m
    for m in (
        Menage(
            id="seul_au_smic",
            prenom="Julien",
            situation="Vendeur à Toulouse · vit seul",
            couleur="ocre",
            persona=Persona(
                adultes=(Adulte(age=42, salaire_brut_mensuel=1801.80, au_smic=True, age_debut_carriere=22),),
                loyer_mensuel=616,
                code_commune="31555",
                patrimoine_financier=9_900,
            ),
            sources=(
                "Salaire : SMIC à temps plein (au_smic), 1 801,80 € brut par mois en 2025 (11,88 € de l'heure pour 151,67 heures), 1 426 € net "
                f"selon l'Insee ({SALAIRES}). "
                "Âge : 42 ans, l'âge médian des ménages locataires du secteur libre en 2022 (Insee, « En 2022, la moitié des ménages locataires "
                "du parc social ont plus de 53 ans », Insee Première n° 2047, avril 2025, https://www.insee.fr/fr/statistiques/8392029) ; aucune "
                "source consultée ne donne l'âge des salariés au SMIC vivant seuls. "
                f"Début de carrière : 22 ans, {DEBUT_DE_CARRIERE}. "
                "Logement : locataire du parc privé, le statut le plus fréquent des personnes seules de moins de 65 ans (42,5 %, "
                f"{LOGEMENT}, figure 1). Loyer : 616 € hors charges par mois, soit 46,7 m², la surface moyenne des personnes seules de moins de "
                "65 ans locataires du parc privé (même publication, tableau complémentaire 3), à 13,2 € le m², le loyer médian hors charges des "
                "appartements de 2 pièces loués vides dans la ville de Toulouse en 2025 (Observatoires locaux des loyers, résultats 2025, "
                "https://www.observatoires-des-loyers.org/datagouv/2025/Base_OP_2025_Nationale.csv, jeu « Résultats nationaux des observatoires "
                "locaux des loyers » sur data.gouv.fr). Choix : Toulouse (code commune 31555), l'une des plus grandes agglomérations suivies "
                "par les observatoires, et le loyer des 2 pièces, 43 m² en moyenne dans l'agglomération, la taille la plus proche de 46,7 m². "
                f"{PATRIMOINE_DES_LOCATAIRES} "
                f"Prénom : Julien, le plus donné aux garçons nés en 1983 ({PRENOMS}). "
                f"Métier : vendeur, un métier d'employé, {METIER} ; les employés sont 24,8 % des personnes en emploi en 2024 ({PROFESSIONS})."
            ),
        ),
        Menage(
            id="couple_salaires_medians",
            prenom="Émilie",
            situation="Comptable à Nantes · 2 enfants",
            couleur="ardoise",
            persona=Persona(
                adultes=(
                    Adulte(age=39, salaire_brut_mensuel=2688.24, age_debut_carriere=23),
                    Adulte(age=42, salaire_brut_mensuel=2940.88, age_debut_carriere=22),
                ),
                enfants=(10, 6),
                patrimoine_financier=59_400,
                patrimoine_immobilier=135_100,
                residence_principale=135_100,
            ),
            sources=(
                "Salaires : 2 128 € et 2 328 € net par mois, les salaires médians en équivalent temps plein des femmes et des hommes du secteur "
                f"privé en 2025 ({SALAIRES}, figure 4), soit 2 688,24 € et 2 940,88 € brut. "
                f"Âges : enfants de 10 et 6 ans, {ENFANTS}. Parents de 39 et 42 ans : l'{NAISSANCES}, plus 8 ans, l'âge moyen des deux enfants. "
                f"Début de carrière : 23 ans pour elle, 22 ans pour lui, {DEBUT_DE_CARRIERE}. "
                "Logement : propriétaires accédants, le statut le plus fréquent des couples avec un ou deux enfants (46,9 %, "
                f"{LOGEMENT}, figure 1). {SANS_COMMUNE} "
                "Patrimoine : patrimoine brut médian des propriétaires accédants, 355 500 €, dont 70 % d'immobilier et un endettement égal à "
                "32 % du patrimoine brut (Insee Focus n° 371, tableau complémentaire 4) : 248 850 € d'immobilier moins 113 760 € de prêt, "
                "imputé à la résidence principale, soit 135 100 € de résidence principale nette, qui fait tout le patrimoine immobilier (choix : "
                "19,5 % seulement des ménages de 40 à 49 ans ont un autre logement, Insee Résultats, « Taux de détention par grand type "
                "d'actifs », onglet AGE). Patrimoine financier : 59 400 €, 16,7 % du patrimoine brut, la part du financier chez les ménages de "
                f"40 à 49 ans (Insee Résultats, « Montant de patrimoine brut moyen, décomposition par grandes composantes », onglet AGE) ({PATRIMOINE}). "
                "Prénom : Émilie, le deuxième prénom le plus donné aux filles nées en 1986, le premier, Aurélie, revenant au ménage sauge "
                f"({PRENOMS}) ; c'est le prénom du premier adulte. "
                "Métier : comptable, pour un salaire médian, entre le salaire moyen des employés (1 979 € net) et celui des professions "
                f"intermédiaires (2 681 €) ({SALAIRES}, figure 1), {METIER}."
            ),
        ),
        Menage(
            id="mere_seule",
            prenom="Aurélie",
            situation="Aide-soignante à Reims · 1 enfant",
            couleur="sauge",
            persona=Persona(
                adultes=(Adulte(age=41, salaire_brut_mensuel=2500.01, age_debut_carriere=23),),
                enfants=(10,),
                loyer_mensuel=463,
                code_commune="51454",
                patrimoine_financier=9_900,
            ),
            sources=(
                "Foyer : une mère et un enfant. 82 % des familles monoparentales sont des mères, dont 46 % vivent avec un seul enfant ; en tout, "
                "47,6 % des familles monoparentales ont un enfant, le cas le plus fréquent, 35,5 % deux (Insee, « Les familles en 2020 : 25 % de familles "
                "monoparentales, 21 % de familles nombreuses », Insee Focus n° 249, septembre 2021, https://www.insee.fr/fr/statistiques/5422681). "
                "Salaire : 1 979 € net par mois, le salaire moyen en équivalent temps plein des employés du privé en 2025, la catégorie la moins "
                f"payée ({SALAIRES}, figure 1), soit 2 500,01 € brut ; choix : les « revenus modestes » sont ceux de cette catégorie. "
                f"Âges : enfant de 10 ans, {ENFANTS}. Mère de 41 ans : l'{NAISSANCES}, plus 10 ans. "
                f"Début de carrière : 23 ans, {DEBUT_DE_CARRIERE}. "
                "Logement : locataire du parc social, le cas le plus fréquent des familles monoparentales locataires (35,9 %, contre 24,5 % "
                f"dans le parc privé ; 36,9 % sont propriétaires) ({LOGEMENT}, figure 1). Loyer : 463 € hors charges par mois, soit 73,7 m², la "
                "surface moyenne des familles monoparentales locataires du parc social (même publication, tableau complémentaire 3), à 6,28 € "
                "le m², le loyer moyen du parc social de Reims au 1er janvier 2025 (SDES, répertoire des logements locatifs des bailleurs "
                "sociaux, RPLS au 1er janvier 2025, fichier « Données nationales : régions, départements, EPCI et communes », onglet COMMUNE, "
                "https://www.statistiques.developpement-durable.gouv.fr/54-millions-de-logements-locatifs-sociaux-en-france-au-1er-janvier-2025). "
                "Choix : Reims (code commune 51454), une grande ville de province au loyer social proche de la moyenne de province, 6,37 € le m² "
                "(même source). Le persona ne distingue pas le parc social : le loyer est calculé comme celui d'un locataire du parc privé. "
                "Pour ce ménage, l'écart est de 17 € de revenu disponible par an, les aides au logement restant les mêmes (380 € par an). "
                f"{PATRIMOINE_DES_LOCATAIRES} "
                f"Prénom : Aurélie, le plus donné aux filles nées en 1984 ({PRENOMS}). "
                f"Métier : aide-soignante, un métier d'employée, {METIER} ; les employées sont 38,8 % des femmes en emploi en 2024 ({PROFESSIONS})."
            ),
        ),
        Menage(
            id="couple_retraites",
            prenom="Jean",
            situation="Retraité à Angers · en couple",
            couleur="prune",
            persona=Persona(
                adultes=(Adulte(age=73, retraite_brute_mensuelle=2186), Adulte(age=74, retraite_brute_mensuelle=1383)),
                patrimoine_financier=104_300,
                patrimoine_immobilier=234_600,
                residence_principale=234_600,
            ),
            sources=(
                "Pensions : 2 186 € et 1 383 € brut par mois, les pensions moyennes de droit direct, majoration pour trois enfants comprise, "
                f"des hommes et des femmes retraités résidant en France en décembre 2024 ({RETRAITES}, fiche 5, tableau 1) ; l'ouvrage ne publie "
                "pas de médiane. Montants de décembre 2024, sans revalorisation. "
                "Âges : 73 et 74 ans, les âges médians des retraités de droit direct fin 2024, 73 ans pour les hommes et 74 ans et 5 mois pour "
                "les femmes (même ouvrage, fiche 1). "
                f"Logement : propriétaires, comme 85 % des couples de 65 ans ou plus ({LOGEMENT}, figure 1). {SANS_COMMUNE} "
                "Patrimoine : patrimoine brut médian des propriétaires de 70 ans ou plus, 372 400 €, dont 64 % d'immobilier et un endettement "
                "égal à 1 % du patrimoine brut (Insee Focus n° 371, tableau complémentaire 4) : 234 600 € d'immobilier net, qui est la "
                "résidence principale (choix : 22,2 % seulement des ménages de 70 ans ou plus ont un autre logement, Insee Résultats, « Taux "
                "de détention par grand type d'actifs », onglet AGE). Patrimoine financier : 104 300 €, 28 % du patrimoine brut, la part du "
                "financier chez les ménages de 70 ans ou plus (Insee Résultats, « Montant de patrimoine brut moyen, décomposition par grandes "
                f"composantes », onglet AGE) ({PATRIMOINE}). "
                f"Prénom : Jean, le plus donné aux garçons nés en 1952 ({PRENOMS}) ; c'est le prénom du premier adulte, à la pension des hommes. "
                "Métier : retraité ; une pension moyenne ne désigne aucun métier."
            ),
        ),
        Menage(
            id="retraitee_seule",
            prenom="Marie",
            situation="Retraitée à Limoges · vit seule",
            couleur="argile",
            persona=Persona(
                adultes=(Adulte(age=74, retraite_brute_mensuelle=1383),),
                patrimoine_financier=34_500,
                patrimoine_immobilier=93_900,
                residence_principale=93_900,
            ),
            sources=(
                "Pension : 1 383 € brut par mois, la pension moyenne de droit direct des femmes retraitées résidant en France en décembre 2024, "
                f"21 % sous celle de l'ensemble des retraités, 1 752 € ({RETRAITES}, fiche 5, tableau 1). Choix : une femme, pour une pension "
                "modeste qui reste une moyenne publiée ; sans pension de réversion, le persona n'étant pas veuf. Montant de décembre 2024, sans "
                "revalorisation. "
                "Âge : 74 ans, l'âge médian des retraitées de droit direct fin 2024, 74 ans et 5 mois (même ouvrage, fiche 1). "
                "Logement : propriétaire sans emprunt, le cas le plus fréquent des personnes seules de 65 ans ou plus (62,5 % de propriétaires "
                f"non accédants, 64,3 % de propriétaires en tout, 33,7 % de locataires) ({LOGEMENT}, figure 1). {SANS_COMMUNE} "
                "Patrimoine : patrimoine brut médian des ménages de retraités anciens employés ou ouvriers, 144 300 €, dont 66,4 % d'immobilier, "
                "23,9 % de patrimoine financier et un endettement égal à 1,3 % du patrimoine brut (Insee Résultats, « Montants moyen et médian de "
                "patrimoine brut et net » et « Montant de patrimoine brut moyen, décomposition par grandes composantes », onglets PCS) : "
                "93 900 € de résidence principale nette, qui fait tout l'immobilier (12,6 % seulement de ces ménages ont un autre logement, "
                f"« Taux de détention par grand type d'actifs », onglet PCS), et 34 500 € de patrimoine financier ({PATRIMOINE}). Choix : les "
                "anciens employés et ouvriers, le groupe des pensions modestes. "
                f"Prénom : Marie, le plus donné aux filles nées en 1951 ({PRENOMS}). "
                "Métier : retraitée."
            ),
        ),
        Menage(
            id="couple_cadres",
            prenom="Nicolas",
            situation="Ingénieur à Lyon · 2 enfants",
            couleur="lin",
            persona=Persona(
                adultes=(
                    Adulte(age=42, salaire_brut_mensuel=5931.27, age_debut_carriere=22),
                    Adulte(age=39, salaire_brut_mensuel=5931.27, age_debut_carriere=23),
                ),
                enfants=(10, 6),
                patrimoine_financier=104_400,
                patrimoine_immobilier=245_200,
                residence_principale=245_200,
            ),
            sources=(
                "Salaires : 4 711 € net par mois chacun, le salaire moyen en équivalent temps plein des cadres du privé en 2025 "
                f"({SALAIRES}, figure 1), soit 5 931,27 € brut ; la conversion est celle d'un salarié non cadre, le persona ne décrivant pas "
                "le statut de cadre. Niveau de vie : le revenu disponible que le simulateur calcule pour le foyer, divisé par ses 2,1 unités de "
                "consommation, est d'environ 48 300 € par an, à 0,5 % sous le 9e décile de niveau de vie de 2024, 48 580 € (Insee, « Niveau de "
                "vie et pauvreté en 2024 », Insee Première n° 2117, juillet 2026, https://www.insee.fr/fr/statistiques/9019316) : le ménage est "
                "au 9e décile, en haut du neuvième dixième de la distribution ; le simulateur ne compte pas les revenus de son patrimoine, que "
                "le niveau de vie de l'Insee inclut. "
                "Âges : ceux du ménage ardoise, pour comparer à composition égale, parents de 42 et 39 ans et enfants de 10 et 6 ans. "
                f"Début de carrière : 22 ans pour lui, 23 ans pour elle, {DEBUT_DE_CARRIERE}. "
                f"Logement : propriétaires accédants, comme le ménage ardoise ({LOGEMENT}, figure 1). {SANS_COMMUNE} "
                "Patrimoine : patrimoine brut médian des ménages entre le 8e et le 9e décile de niveau de vie, 485 500 €, dont 65,4 % "
                "d'immobilier, 21,5 % de patrimoine financier et un endettement égal à 14,9 % du patrimoine brut (Insee Résultats, « Montants "
                "moyen et médian de patrimoine brut et net » et « Montant de patrimoine brut moyen, décomposition par grandes composantes », "
                "onglets NIVVIE) : 245 200 € de résidence principale nette, qui fait tout l'immobilier (36,5 % seulement de ces ménages ont un "
                "autre logement, « Taux de détention par grand type d'actifs », onglet NIVVIE), et 104 400 € de patrimoine financier "
                f"({PATRIMOINE}). "
                "Prénom : Nicolas, le deuxième prénom le plus donné aux garçons nés en 1983, le premier, Julien, revenant au ménage ocre "
                f"({PRENOMS}) ; c'est le prénom du premier adulte. "
                f"Métier : ingénieur, un métier de cadre, {METIER} ; les cadres sont 23,0 % des personnes en emploi en 2024 ({PROFESSIONS})."
            ),
        ),
    )
}
