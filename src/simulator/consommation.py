"""Dépenses d'énergie d'un ménage, imputées selon son niveau de vie à partir de l'enquête Budget de famille de l'Insee.

OpenFisca ne connaît pas la consommation : la TVA sur l'énergie se calcule sur ces dépenses, que le persona peut remplacer
par les siennes. Elles sont tenues fixes d'un scénario à l'autre (incidence statique).
"""

from bisect import bisect

# Dépense annuelle moyenne par ménage et par décile de niveau de vie, en euros de 2017 (déciles 1 à 10).
# Insee, enquête Budget de famille 2017, tableau TF106 « Dépenses annuelles moyennes selon le niveau de vie »,
# https://www.insee.fr/fr/statistiques/fichier/4648335/TF106.csv ; codes de la nomenclature de l'enquête entre parenthèses.
DEPENSES_2017 = {
    "electricite": (592, 635, 640, 683, 714, 759, 814, 808, 855, 957),  # 0451
    "gaz": (159, 209, 251, 237, 245, 250, 270, 259, 266, 386),  # 0452
    "fioul": (73, 110, 102, 157, 129, 132, 132, 133, 109, 129),  # 0453 combustibles liquides
    "energie_logement": (967, 1123, 1193, 1279, 1281, 1348, 1449, 1427, 1530, 1925),  # 045 électricité, gaz et autres combustibles
    "carburants": (622, 754, 868, 1006, 1174, 1196, 1333, 1288, 1462, 1375),  # 07221
}

# Indices des prix à la consommation, moyennes annuelles, base 100 en 2015 (Insee, Informations rapides n° 8 du 12 janvier 2018
# pour 2017, et « Prix à la consommation – Moyennes annuelles – Année 2025 » pour 2025).
IPC = {
    "ensemble": {"2017": 101.22, "2018": 101.22 * 1.018, "2025": 120.95},  # 2018 : +1,8 % en moyenne (Insee, TEF 2020, fiche 11.4)
    "energie": {"2017": 103.19, "2025": 150.29},
    "produits_petroliers": {"2017": 104.34, "2025": 139.16},
}
INDICE_DU_POSTE = {
    "electricite": "energie",
    "gaz": "energie",
    "autres_energies_logement": "energie",
    "fioul": "produits_petroliers",
    "carburants": "produits_petroliers",
}
POSTES = tuple(INDICE_DU_POSTE)
# Taux de TVA de la loi 2025 par poste, parmi les paramètres taxation_indirecte.tva d'OpenFisca-France. L'abonnement à l'électricité
# et au gaz, à 5,5 % jusqu'au 31 juillet 2025, est compté au taux normal comme la consommation ; le bois de chauffage est au taux
# intermédiaire, la chaleur des réseaux, minoritaire dans ce poste, aussi.
TAUX_DU_POSTE = {
    "electricite": "taux_normal",
    "gaz": "taux_normal",
    "fioul": "taux_normal",
    "carburants": "taux_normal",
    "autres_energies_logement": "taux_intermediaire",
}

# Limites supérieures des déciles 1 à 9 de niveau de vie en 2018, en euros de 2018 (Insee, Revenus et patrimoine des ménages,
# édition 2021, fiche 1.4, figure 1) : l'année la plus proche de l'enquête dont tous les déciles sont publiés.
DECILES_2018 = (11_210, 14_150, 16_680, 18_990, 21_250, 23_750, 26_680, 30_820, 39_130)


def decile(niveau_de_vie_2025: float) -> int:
    """Décile de niveau de vie, de 1 à 10, d'un niveau de vie annuel exprimé en euros de 2025."""
    return bisect(DECILES_2018, niveau_de_vie_2025 * IPC["ensemble"]["2018"] / IPC["ensemble"]["2025"]) + 1


def depenses_imputees(niveau_de_vie_2025: float) -> dict[str, float]:
    """Dépenses annuelles d'énergie, en euros de 2025, d'un ménage moyen du décile de ce niveau de vie."""
    i = decile(niveau_de_vie_2025) - 1
    en_2017 = {poste: valeurs[i] for poste, valeurs in DEPENSES_2017.items()}
    # Le reste de la dépense d'énergie du logement : bois, charbon, chaleur des réseaux.
    en_2017["autres_energies_logement"] = en_2017.pop("energie_logement") - en_2017["electricite"] - en_2017["gaz"] - en_2017["fioul"]
    # shortcut: l'électricité et le gaz suivent l'indice de l'énergie, qui mêle produits pétroliers ; passer aux indices par produit si l'écart compte.
    return {poste: round(montant * IPC[INDICE_DU_POSTE[poste]]["2025"] / IPC[INDICE_DU_POSTE[poste]]["2017"]) for poste, montant in en_2017.items()}
