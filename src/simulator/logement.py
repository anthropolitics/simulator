"""Loyer d'un locataire qui ne le donne pas, estimé d'après sa commune, son logement et son foyer, avec les enquêtes Logement de l'Insee."""

# Loyer mensuel moyen au mètre carré, hors charges, en 2020, dans le parc privé et dans le parc social (enquête Logement 2020, SDES,
# « Les conditions de logement des ménages locataires », tableau 1, https://www.statistiques.developpement-durable.gouv.fr/media/6480/download).
LOYER_AU_M2_2020 = {False: 10.5, True: 6.5}
# L'enquête de 2020 ne le détaille pas par taille d'agglomération ; celle de 2013 le fait : ensemble, communes rurales, unités urbaines de
# moins de 100 000 habitants, de 100 000 habitants ou plus, unité urbaine de Paris, secteur libre puis secteur social, et le nombre de
# ménages locataires des deux premières (Insee, enquête Logement 2013, tableaux DEPLOC_6 et DEPLOC_2,
# https://www.insee.fr/fr/statistiques/2419862). Champ : France métropolitaine, logements loués vides.
LOYER_AU_M2_2013 = {False: (8.59, 5.63, 7.21, 8.79, 16.11), True: (5.51, 5.02, 4.98, 5.28, 6.66)}
MENAGES_2013 = {False: (817_741, 1_771_561), True: (239_786, 1_377_818)}
# Indice de référence des loyers, moyenne des quatre trimestres de 2020 et de 2025 (Insee, série 001515333,
# https://www.insee.fr/fr/statistiques/serie/001515333).
IRL = {"2020": 130.56, "2025": 145.93}
# Surface moyenne du logement des locataires, en mètres carrés, début 2024, parc privé puis parc social : personnes seules de moins de
# 65 ans, de 65 ans ou plus, familles monoparentales, couples sans enfant de moins de 65 ans, de 65 ans ou plus, couples avec un ou deux
# enfants, avec trois enfants ou plus (Insee Première n° 2090, enquête Logement 2023-2024, tableau complémentaire 3,
# https://www.insee.fr/fr/statistiques/fichier/8727513/ip2090.xlsx). Sources consultées le 19 novembre 2026.
SURFACES = {False: (46.7, 58.8, 75.5, 67.0, 83.0, 87.1, 99.8), True: (53.9, 59.1, 73.7, 70.5, 71.9, 77.2, 82.5)}


def surface_moyenne(social: bool, adultes: int, enfants: int, age: int) -> float:
    """Surface du logement des locataires du même type de ménage, selon l'âge de l'adulte le plus âgé."""
    if adultes == 1:
        return SURFACES[social][2 if enfants else age >= 65]
    return SURFACES[social][5 + (enfants >= 3) if enfants else 3 + (age >= 65)]


def loyer_au_m2(zone: int | None, social: bool) -> float:
    """Loyer mensuel au mètre carré de 2025, hors charges, selon la zone des aides au logement de la commune."""
    ensemble, rural, petites, grandes, paris = LOYER_AU_M2_2013[social]
    ruraux, petits = MENAGES_2013[social]
    # shortcut: la zone des aides au logement tient lieu de taille d'agglomération : zone 1, Paris ; zone 2, 100 000 habitants ou plus, et
    # les communes inconnues, comme le fait OpenFisca ; zone 3, la moyenne des communes rurales et des petites agglomérations. Le niveau de
    # 2020 suit ensuite l'indice de référence des loyers. Passer à un loyer par commune (carte des loyers du ministère) si l'écart compte.
    selon_la_zone = {1: paris, 2: grandes, 3: (ruraux * rural + petits * petites) / (ruraux + petits)}[zone or 2]
    return LOYER_AU_M2_2020[social] * selon_la_zone / ensemble * IRL["2025"] / IRL["2020"]
