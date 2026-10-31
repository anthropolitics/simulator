"""Consommation d'un ménage, imputée selon son niveau de vie à partir de l'enquête Budget de famille de l'Insee.

OpenFisca ne connaît pas la consommation : la TVA se calcule sur ces dépenses, l'énergie poste par poste, le reste regroupé par
taux de TVA. Le persona peut les remplacer par les siennes. Elles sont tenues fixes d'un scénario à l'autre (incidence statique).
"""

from bisect import bisect

# Dépense annuelle moyenne par ménage et par décile de niveau de vie, en euros de 2017 (déciles 1 à 10).
# Insee, enquête Budget de famille 2017, tableau TF106 « Dépenses annuelles moyennes selon le niveau de vie »,
# https://www.insee.fr/fr/statistiques/fichier/4648335/TF106.csv ; codes de la nomenclature de l'enquête entre parenthèses.
DEPENSES_2017 = {
    "electricite": (592, 635, 640, 683, 714, 759, 814, 808, 855, 957),  # 0451
    "electricite_ou_gaz": (111, 127, 146, 146, 135, 143, 171, 168, 240, 394),  # 0450 électricité et gaz non séparables
    "gaz": (159, 209, 251, 237, 245, 250, 270, 259, 266, 386),  # 0452
    "fioul": (73, 110, 102, 157, 129, 132, 132, 133, 109, 129),  # 0453 combustibles liquides
    "energie_logement": (967, 1123, 1193, 1279, 1281, 1348, 1449, 1427, 1530, 1925),  # 045 électricité, gaz et autres combustibles
    "carburants": (622, 754, 868, 1006, 1174, 1196, 1333, 1288, 1462, 1375),  # 07221
}

HORS_ENERGIE = tuple(f"hors_energie_taux_{taux}" for taux in ("normal", "intermediaire", "reduit", "particulier"))
NORMAL, INTERMEDIAIRE, REDUIT, PARTICULIER = HORS_ENERGIE
# Le reste de la consommation, même source et même unité : chaque code le plus fin du TF106, hors énergie (045 et 07221, ci-dessus) et
# hors division 13, que l'Insee exclut de la consommation (impôts, remboursements de prêts, gros travaux, dons), avec le poste de son taux
# de TVA de la loi 2025, ou None si la dépense n'en porte pas (exonérée ou hors champ). Un code qui mêle plusieurs taux prend celui de la
# plus grande part de sa dépense ; un code sans détail (0331Z, 0571Z, 0741Z, 0971Z, 1271Z, 12331, 12911), le plus fréquent de sa division, 20 %.
CODES_2017: dict[str, tuple[str | None, tuple[int, ...]]] = {
    # Alimentation et boissons non alcooliques : 5,5 % (CGI, art. 278-0 bis, A, 1°), sauf la margarine et les graisses végétales (même 1°, c).
    "01111": (REDUIT, (31, 30, 26, 28, 29, 32, 30, 34, 33, 35)),  # riz sous toutes ses formes et produits à base de riz
    "01112": (REDUIT, (341, 407, 431, 461, 483, 511, 510, 578, 567, 665)),  # pain et autres produits de boulangerie et de viennoiserie yc biscuits et gâteaux
    "01113": (REDUIT, (45, 50, 51, 56, 58, 56, 66, 76, 74, 84)),  # pâtes alimentaires sous toutes leurs formes et plats à base de pâtes
    "01114": (REDUIT, (105, 120, 122, 144, 151, 147, 159, 163, 163, 172)),  # préparations telles que pâte à pâtisser, gâteau industriel, tarte, tourte
    "01115": (REDUIT, (41, 47, 48, 43, 50, 48, 63, 59, 65, 69)),  # autres céréales et produits à base de céréales yc farine, semoule, céréales petit déjeuner
    "01121": (REDUIT, (160, 194, 201, 266, 219, 264, 274, 277, 320, 372)),  # viande bovine fraîche ou surgelée
    "01122": (REDUIT, (51, 53, 71, 83, 72, 80, 78, 96, 83, 82)),  # viande porcine fraîche ou surgelée
    "01123": (REDUIT, (22, 49, 22, 29, 23, 28, 31, 34, 43, 41)),  # viande ovine ou caprine fraîche ou surgelée
    "01124": (REDUIT, (109, 141, 123, 147, 154, 169, 175, 174, 175, 222)),  # viande de volaille fraîche ou surgelée
    "01125": (REDUIT, (183, 237, 277, 328, 308, 329, 327, 358, 372, 422)),  # viande séchée salée ou fumée, charcuterie et abats, frais ou surgelé (jambon
    "01126": (REDUIT, (72, 88, 84, 106, 115, 116, 113, 130, 132, 149)),  # conserve de viande, produit de transformation des viandes, plat préparé de viande
    "01127": (REDUIT, (8, 10, 6, 11, 9, 15, 11, 20, 14, 15)),  # autres viandes comestibles fraîches ou surgelées (cheval, lapin, gibier) yc animaux sur pied
    "01130": (REDUIT, (59, 68, 74, 105, 85, 102, 96, 119, 164, 236)),  # poissons frais
    "01131": (REDUIT, (13, 13, 11, 15, 18, 21, 19, 30, 21, 28)),  # poissons surgelés ou congelés (hors poissons panés ou cuisinés)
    "01132": (REDUIT, (25, 29, 35, 46, 48, 68, 57, 70, 93, 119)),  # fruits de mer frais ou surgelés (yc cuits, nc cuisinés )
    "01133": (REDUIT, (12, 9, 15, 17, 17, 24, 22, 39, 36, 49)),  # poissons et fruits de mer salés, fumés, séchés yc surgelé
    "01134": (REDUIT, (53, 65, 63, 69, 72, 81, 89, 99, 106, 150)),  # conserves de poisson et de fruits de mer et plats préparés à base de poissons ou de
    "01145": (REDUIT, (170, 205, 209, 254, 263, 267, 300, 333, 333, 442)),  # fromage et lait caillé
    "01147": (REDUIT, (32, 35, 37, 39, 41, 42, 43, 61, 54, 66)),  # œufs
    "0114A": (REDUIT, (60, 70, 77, 80, 71, 72, 70, 73, 70, 82)),  # lait frais, condensé, en poudre
    "0114B": (REDUIT, (115, 135, 150, 169, 171, 177, 186, 210, 221, 231)),  # yaourts et produits laitiers
    "01151": (REDUIT, (28, 33, 39, 45, 39, 43, 43, 47, 48, 48)),  # beurre
    "0115A": (REDUIT, (31, 33, 27, 32, 35, 37, 30, 31, 47, 53)),  # huiles alimentaires
    "0115B": (NORMAL, (7, 14, 13, 14, 14, 15, 12, 13, 14, 10)),  # margarine et autres graisses alimentaires
    "01161": (REDUIT, (36, 41, 42, 54, 51, 59, 65, 73, 87, 113)),  # agrumes frais
    "01162": (REDUIT, (24, 25, 25, 31, 23, 24, 27, 32, 30, 33)),  # bananes fraîches
    "01168": (REDUIT, (32, 38, 34, 36, 39, 37, 44, 57, 68, 87)),  # fruits séchés
    "01169": (REDUIT, (3, 3, 4, 8, 8, 9, 10, 9, 11, 10)),  # fruits au sirop et fruits surgelés
    "0116A": (REDUIT, (112, 134, 142, 161, 142, 169, 214, 227, 259, 353)),  # autres fruits frais
    "01175": (REDUIT, (7, 8, 6, 4, 6, 6, 6, 8, 9, 13)),  # légumes secs
    "01176": (REDUIT, (6, 7, 11, 15, 12, 13, 11, 13, 16, 20)),  # légumes surgelés non cuisinés
    "01177": (REDUIT, (38, 47, 44, 46, 49, 48, 54, 61, 67, 69)),  # légumes et plats à base de légume,  en conserve (sans pommes de terre)
    "01178": (REDUIT, (18, 27, 26, 34, 37, 44, 41, 52, 59, 69)),  # légumes préparés et plats à base de légumes,  frais et surgelés (sauf les plats à base de
    "01179": (REDUIT, (64, 78, 74, 79, 77, 84, 75, 95, 93, 102)),  # pomme de terre, autres tubercules, produits à base de pommes de terre (chips) et tubercules
    "0117A": (REDUIT, (177, 197, 202, 208, 206, 241, 238, 295, 338, 443)),  # legumes frais
    "01181": (REDUIT, (14, 14, 16, 18, 15, 14, 14, 13, 16, 17)),  # sucre yc édulcorants
    # Confitures, miel, chocolat, glaces, confiserie : la confiserie et les produits composés de chocolat, à 20 % (même 1°, a et b), sont minoritaires.
    "0118A": (REDUIT, (136, 190, 190, 237, 235, 251, 252, 311, 304, 340)),  # produits à base de sucre et cacao
    "0119Z": (REDUIT, (91, 118, 121, 152, 146, 146, 136, 202, 181, 222)),  # autres produits alimentaires
    "01213": (REDUIT, (4, 8, 5, 5, 6, 6, 8, 5, 6, 5)),  # cacao et chocolat en poudre
    "0121A": (REDUIT, (64, 73, 92, 106, 107, 125, 117, 138, 154, 222)),  # café, thé, plantes à infusion
    "01221": (REDUIT, (36, 50, 58, 58, 65, 67, 76, 83, 84, 91)),  # eaux minérales
    "01222": (REDUIT, (52, 56, 49, 47, 47, 49, 43, 45, 50, 44)),  # boissons gazeuses
    "0122A": (REDUIT, (84, 87, 88, 97, 86, 102, 112, 115, 122, 133)),  # jus de fruits et de légumes
    "0131Z": (REDUIT, (92, 100, 99, 113, 141, 166, 192, 217, 236, 329)),  # autres dépenses d alimentation
    # Alcools et tabac : taux normal.
    "02111": (NORMAL, (55, 67, 104, 104, 97, 112, 123, 107, 110, 116)),  # spiritueux et liqueurs
    "0212A": (NORMAL, (73, 94, 138, 162, 180, 265, 235, 292, 297, 513)),  # vins, apéritifs à base de vin, champagne
    "02131": (NORMAL, (57, 43, 51, 67, 79, 62, 66, 59, 64, 74)),  # bière et boissons à base de bière
    "022ZZ": (NORMAL, (367, 416, 414, 421, 448, 443, 391, 348, 350, 371)),  # tabac et produits connexes
    "02411": (NORMAL, (0, 0, 2, 6, 5, 3, 2, 6, 6, 11)),  # dépenses de boissons alcoolisées, tabac et stupéfiants : cadeau offert à un autre ménage
    "03111": (NORMAL, (1, 2, 1, 2, 6, 5, 4, 15, 3, 5)),  # tissus pour vêtements
    "0312Z": (NORMAL, (618, 668, 680, 688, 720, 845, 908, 1054, 1313, 1441)),  # vêtements homme, femme, enfant
    "03131": (NORMAL, (16, 24, 26, 41, 35, 29, 49, 52, 60, 84)),  # accessoires du vêtement et mercerie
    "03141": (NORMAL, (11, 9, 3, 4, 5, 15, 15, 17, 17, 67)),  # nettoyage, réparation et location de vêtements
    "032ZZ": (NORMAL, (192, 223, 222, 225, 233, 273, 287, 340, 414, 473)),  # chaussures, yc location et réparation
    "0331Z": (NORMAL, (64, 67, 85, 83, 88, 112, 159, 146, 213, 275)),  # autres dépenses d habillement
    # Loyers : exonérés.
    "04111": (None, (1840, 1917, 2114, 2168, 2183, 2118, 1795, 1902, 1724, 1987)),  # loyers nets des aides au logement (hors charges ou avec charges non
    "04121": (None, (30, 18, 14, 42, 44, 43, 79, 47, 68, 87)),  # loyers (hors charges ou avec charges non isolables) des locataires autres résidences
    # Produits achetés par le ménage pour entretenir son logement : 20 % ; le taux de 10 % ne vaut que pour les travaux d'une entreprise.
    "0431Z": (NORMAL, (65, 53, 78, 81, 150, 314, 296, 246, 166, 306)),  # produits destinés aux travaux courants d’entretien et de réparation du logement (hors
    # Eau : 5,5 % (CGI, art. 278-0 bis, A, 1°) ; l'assainissement, à 10 %, que seuls les ménages raccordés au réseau paient, en fait moins de la moitié.
    "04431": (REDUIT, (191, 207, 230, 237, 244, 269, 266, 280, 288, 344)),  # factures d’eau résidence principale, autre logement, dépendance, terrain
    # Charges collectives : chauffage, entretien et syndic, à 20 %, en sont la plus grande part ; gardiens, assurance et taxe d'ordures n'ont pas de TVA.
    "04441": (NORMAL, (537, 627, 545, 519, 445, 502, 527, 565, 643, 872)),  # charges collectives relatives au logement (payées isolément du loyer ou crédit)
    # Cadeau d'habitation à un autre ménage : sans TVA, comme les loyers, plus grande part de la division hors énergie (choix discutable).
    "04611": (None, (11, 29, 20, 48, 22, 48, 77, 91, 83, 267)),  # autres dépenses d’habitation : cadeau offert (à destination d’un autre ménage)
    "0511Z": (NORMAL, (164, 204, 268, 221, 282, 368, 417, 573, 686, 912)),  # meubles, articles d’ameublement et de décoration
    "051AZ": (NORMAL, (2, 2, 8, 15, 10, 3, 27, 33, 18, 23)),  # tapis et autres revêtements, pose et réparation
    "0521Z": (NORMAL, (23, 44, 52, 51, 75, 76, 92, 104, 121, 215)),  # articles de literie et autres articles de ménage en textile
    "0531Z": (NORMAL, (81, 102, 175, 158, 144, 214, 157, 202, 217, 260)),  # gros appareils ménagers électriques
    "05321": (NORMAL, (12, 12, 12, 14, 23, 23, 40, 29, 41, 47)),  # petit électroménager
    "0541Z": (NORMAL, (35, 38, 54, 70, 65, 66, 93, 137, 107, 129)),  # verrerie, vaisselle, ustensiles de cuisine et article de ménage ou toilette yc réparation
    "0551Z": (NORMAL, (16, 41, 48, 49, 65, 56, 113, 89, 77, 191)),  # gros outillage de bricolage, de jardinage et leur réparation
    "0552Z": (NORMAL, (32, 65, 81, 89, 79, 109, 136, 265, 161, 318)),  # petit outillage et accessoires de bricolage et jardinage, matériaux extérieurs
    "0561Z": (NORMAL, (152, 205, 196, 225, 235, 222, 249, 274, 280, 318)),  # articles de ménage non durables
    # Services domestiques : surtout l'emploi direct d'un salarié à domicile, sans TVA ; les entreprises de services à la personne facturent 10 ou 5,5 %.
    "0562Z": (None, (63, 42, 91, 83, 100, 133, 233, 249, 470, 1344)),  # services domestiques et autres services pour le logement
    "0571Z": (NORMAL, (14, 18, 28, 22, 25, 60, 42, 59, 76, 133)),  # autres dépenses en équipement
    # Pharmacie : ce que paie le ménage va surtout aux médicaments non remboursables, à 10 % (CGI, art. 278 quater) ; les médicaments remboursables,
    # à 2,1 %, sont surtout payés par l'assurance maladie, et les lunettes et appareils, à 20 % ou 5,5 %, sont minoritaires (choix discutable).
    "0611Z": (INTERMEDIAIRE, (139, 180, 187, 209, 246, 234, 255, 283, 400, 410)),  # produits pharmaceutiques, appareils et matériels thérapeutiques
    # Soins : exonérés.
    "06211": (None, (42, 53, 77, 99, 100, 124, 107, 184, 101, 122)),  # consultations des médecins généralistes ou spécialistes hors hospitalisation
    "06221": (None, (27, 39, 54, 46, 49, 67, 84, 61, 99, 86)),  # dentiste, orthodontie
    "0623Z": (None, (29, 32, 47, 41, 45, 40, 82, 60, 79, 92)),  # services paramédicaux (labo, radio, soins des auxiliaires médicaux et paramédicaux…)
    "06311": (None, (10, 16, 24, 17, 28, 22, 35, 37, 25, 37)),  # services et soins hospitaliers
    "0641Z": (None, (7, 3, 4, 2, 2, 4, 16, 5, 21, 21)),  # autres dépenses de santé
    "0711Z": (NORMAL, (617, 771, 960, 1363, 1441, 1815, 2202, 2527, 2317, 4055)),  # achats d automobiles
    "07121": (NORMAL, (30, 27, 46, 59, 46, 115, 83, 77, 117, 134)),  # achats de motocycles neufs et occasion
    "07131": (NORMAL, (13, 14, 15, 31, 25, 46, 36, 45, 66, 62)),  # achats de cycles neufs et occasion
    "07211": (NORMAL, (56, 97, 95, 128, 136, 161, 114, 190, 197, 185)),  # pièces détachées, pneus et accessoires pour les véhicules personnels (hors ceux
    "07231": (NORMAL, (151, 214, 235, 266, 279, 329, 307, 360, 381, 412)),  # réparations, dépannages, révisions, lavage, entretien et contrôle technique
    "0724Z": (NORMAL, (70, 90, 71, 92, 127, 99, 140, 175, 170, 302)),  # autres services liés à l’utilisation de véhicules personnels
    # Déménagement : 20 %.
    "07361": (NORMAL, (7, 5, 6, 12, 13, 17, 13, 13, 20, 46)),  # autres services de transport (yc déménagement)
    # Transport de voyageurs : 10 % (CGI, art. 279, b quater) ; les vols internationaux, exonérés, sont minoritaires.
    "073ZZ": (INTERMEDIAIRE, (457, 351, 251, 315, 334, 410, 546, 499, 740, 1232)),  # services de transport
    "0741Z": (NORMAL, (166, 180, 178, 211, 220, 331, 344, 438, 565, 1010)),  # autres dépenses de transport
    # Service universel postal : exonéré.
    "08111": (None, (12, 15, 18, 17, 17, 25, 31, 21, 35, 34)),  # services postaux (yc timbres, enveloppes)
    "08121": (NORMAL, (68, 70, 63, 72, 76, 69, 103, 113, 106, 119)),  # achats et réparation téléphones fixes ou portables, télécopieurs et accessoires
    "08131": (NORMAL, (567, 573, 573, 614, 611, 652, 643, 666, 710, 741)),  # services de téléphone et fax, internet, recharges téléphoniques
    "0911Z": (NORMAL, (51, 65, 58, 54, 86, 68, 153, 116, 108, 168)),  # appareils de réception, d’enregistrement et de reproduction, du son et de l’image
    "09131": (NORMAL, (67, 56, 66, 63, 68, 75, 88, 104, 138, 178)),  # micro-ordinateurs, tablettes, matériels et accessoires informatiques (yc pièces
    "09141": (NORMAL, (25, 26, 30, 47, 44, 50, 51, 56, 68, 85)),  # supports vierges ou enregistrés pour l’image et le son (yc téléchargement)
    "091AZ": (NORMAL, (25, 6, 10, 14, 12, 36, 27, 22, 55, 51)),  # equipement photo, cinéma, optique
    "092ZZ": (NORMAL, (5, 15, 58, 11, 10, 83, 50, 324, 266, 119)),  # autres biens durables importants du domaine des loisirs et de la culture
    "0931Z": (NORMAL, (126, 101, 138, 117, 172, 214, 187, 208, 199, 211)),  # jeux, jouets et passe temps, articles de sport, de camping et de loisirs en plein
    # Fleurs et plantes : 10 % (CGI, art. 278 bis, 3° bis, d ; BOI-TVA-LIQ-30-10-35), plus que les accessoires et la livraison, à 20 %.
    "09321": (INTERMEDIAIRE, (71, 61, 75, 96, 108, 167, 151, 177, 265, 261)),  # horticulture, accessoires et frais de livraison
    "093AZ": (NORMAL, (123, 113, 116, 143, 125, 170, 227, 173, 236, 188)),  # animaux d’agrément
    # Sport et loisirs : salles, cours et locations à 20 %, plus que cotisations d'associations, exonérées, et parcs de loisirs, à 10 % (choix discutable).
    "09411": (NORMAL, (118, 131, 184, 164, 213, 276, 328, 317, 710, 800)),  # services sportifs et récréatifs (spectacles sportifs, participation loisirs
    # Services culturels : abonnements de télévision, à 10 % (CGI, art. 279, b octies), plus que la redevance audiovisuelle, sans TVA, ou le cinéma et
    # les spectacles, à 5,5 % ; l'Insee (France, portrait social, 2022) y compte 267 € de télévision, redevance comprise, et 98 € de cinéma et spectacles.
    "0942Z": (INTERMEDIAIRE, (290, 282, 312, 410, 435, 443, 528, 549, 611, 799)),  # services culturels
    # Jeux de hasard : exonérés.
    "09431": (None, (22, 23, 26, 45, 40, 57, 47, 39, 44, 38)),  # jeux de hasard (loto, tiercé …)
    # Livres : 5,5 % (CGI, art. 278-0 bis, A, 3°).
    "09511": (REDUIT, (82, 53, 68, 91, 83, 90, 118, 130, 162, 291)),  # livres yc e-books
    # Presse : 2,1 % (CGI, art. 298 septies).
    "09521": (PARTICULIER, (32, 76, 76, 116, 116, 122, 124, 133, 141, 206)),  # journaux et périodiques yc par abonnement
    "09531": (NORMAL, (3, 7, 6, 9, 13, 15, 14, 14, 18, 25)),  # imprimés divers (carte postale, de visite, poster, calendrier, carte routière, autocollant…)
    "09541": (NORMAL, (38, 38, 48, 72, 53, 72, 87, 92, 88, 129)),  # articles de papeterie et de dessin (yc toner pour imprimante)
    # Voyages à forfait : la TVA française ne porte que sur la marge de l'agence (CGI, art. 266, 1, e), le reste est souvent à l'étranger : sans TVA.
    "09611": (None, (89, 93, 107, 174, 227, 276, 340, 474, 677, 1171)),  # voyages à forfait, week-end, excursions… yc voyage scolaire
    "0971Z": (NORMAL, (90, 87, 101, 155, 160, 215, 269, 306, 366, 604)),  # autres dépenses de loisirs
    # Enseignement : exonéré.
    "10111": (None, (11, 36, 11, 10, 21, 11, 23, 18, 23, 55)),  # enseignement maternel et primaire (scolarité et cours d’alphabétisation)
    "10121": (None, (24, 25, 19, 18, 23, 22, 24, 20, 40, 35)),  # enseignement secondaire (scolarité et inscription aux concours de niveau secondaire)
    "10131": (None, (208, 121, 36, 102, 73, 58, 83, 135, 147, 184)),  # enseignement supérieur et frais d’inscription aux concours des grandes écoles
    "10141": (None, (42, 9, 16, 11, 11, 23, 18, 22, 24, 70)),  # enseignement ne correspondant à aucun niveau particulier (cours particuliers, enseignement
    "1015Z": (None, (11, 39, 11, 29, 3, 20, 12, 8, 15, 129)),  # autres dépenses d’enseignement
    # Restauration : 10 % (CGI, art. 279, m) ; les alcools, à 20 %, sont minoritaires.
    "11111": (INTERMEDIAIRE, (150, 184, 250, 342, 401, 523, 545, 690, 971, 1691)),  # repas pris dans un restaurant
    "11112": (INTERMEDIAIRE, (274, 249, 286, 344, 414, 468, 484, 523, 628, 808)),  # repas pris dans un café, bars ou assimilé
    # Cantines : 5,5 % pour les repas servis par un prestataire dans les écoles (CGI, art. 278-0 bis, E), retenu comme la plus grande part ;
    # restaurants d'entreprise à 10 % et cantines en régie publique, sans TVA, pour le reste (choix discutable).
    "11121": (REDUIT, (258, 277, 247, 299, 339, 346, 379, 380, 437, 615)),  # cantines scolaire et professionnelle
    # Restauration : 10 % (CGI, art. 279, m).
    "1113Z": (INTERMEDIAIRE, (81, 82, 92, 154, 166, 204, 242, 335, 432, 744)),  # autres dépenses de restauration
    # Hébergement : 10 % (CGI, art. 279, a) ; les nuits à l'étranger, sans TVA française, sont minoritaires.
    "11211": (INTERMEDIAIRE, (88, 147, 125, 234, 205, 225, 317, 410, 543, 1071)),  # services d hébergement
    # Coiffure (les cures thermales sont minoritaires), soins personnels, bijoux, effets personnels : 20 %.
    "12111": (NORMAL, (173, 180, 224, 252, 306, 339, 389, 415, 479, 612)),  # salons de coiffure et esthétique corporelle (yc cures thermales, tatouages
    "1212Z": (NORMAL, (219, 282, 296, 356, 360, 433, 447, 541, 591, 638)),  # appareils, articles et produits pour les soins personnels
    "12311": (NORMAL, (40, 14, 22, 28, 27, 46, 49, 79, 70, 175)),  # articles de bijouterie, de joaillerie et d’horlogerie (yc leur réparation)
    "1232Z": (NORMAL, (29, 39, 42, 44, 39, 55, 81, 109, 135, 140)),  # autres effets personnels : maroquinerie, accessoires (briquet, parapluie, lunettes de
    "12331": (NORMAL, (21, 21, 35, 32, 31, 45, 39, 52, 64, 104)),  # autres biens et services offerts  (à des personnes extérieures au ménage)
    # Assistantes maternelles salariées, crèches et maisons de retraite publiques ou associatives : sans TVA pour l'essentiel.
    "12411": (None, (41, 94, 169, 130, 234, 307, 376, 638, 506, 591)),  # services de protection sociale (assistante maternelle, crèche, maison de retraite
    # Assurances et services financiers : exonérés.
    "12511": (None, (21, 30, 35, 43, 40, 37, 44, 47, 43, 52)),  # assurances vie, décès
    "12521": (None, (258, 305, 320, 346, 347, 371, 391, 398, 425, 546)),  # assurances liées au logement
    "12531": (None, (493, 784, 942, 1096, 1101, 1193, 1208, 1271, 1333, 1499)),  # assurances liées à la santé
    "12541": (None, (374, 457, 538, 598, 676, 727, 779, 837, 828, 937)),  # assurances liées aux transports (yc assurance voyage)
    "12551": (None, (74, 89, 87, 110, 101, 159, 145, 158, 220, 322)),  # autres assurances (pack assurance, scolaire, dépendance, prévoyance, animaux, obsèques)
    "12611": (None, (108, 124, 127, 139, 138, 152, 153, 163, 181, 196)),  # services financiers
    "1271Z": (NORMAL, (212, 201, 392, 242, 346, 557, 633, 844, 867, 1591)),  # autres services
    "12811": (NORMAL, (7, 10, 8, 13, 24, 25, 48, 45, 42, 42)),  # autres dépenses occasionnées par une cérémonie
    "12911": (NORMAL, (11, 11, 16, 15, 14, 9, 24, 50, 23, 40)),  # dépenses SAI des personnes vivant hors du domicile au moins un jour par semaine
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
ENERGIE = tuple(INDICE_DU_POSTE)
INDICE_DU_POSTE |= dict.fromkeys(HORS_ENERGIE, "ensemble")
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
    NORMAL: "taux_normal",
    INTERMEDIAIRE: "taux_intermediaire",
    REDUIT: "taux_reduit",
    PARTICULIER: "taux_particulier_super_reduit",
}

# Limites supérieures des déciles 1 à 9 de niveau de vie en 2018, en euros de 2018 (Insee, Revenus et patrimoine des ménages,
# édition 2021, fiche 1.4, figure 1) : l'année la plus proche de l'enquête dont tous les déciles sont publiés.
DECILES_2018 = (11_210, 14_150, 16_680, 18_990, 21_250, 23_750, 26_680, 30_820, 39_130)


def decile(niveau_de_vie_2025: float) -> int:
    """Décile de niveau de vie, de 1 à 10, d'un niveau de vie annuel exprimé en euros de 2025."""
    return bisect(DECILES_2018, niveau_de_vie_2025 * IPC["ensemble"]["2018"] / IPC["ensemble"]["2025"]) + 1


def depenses_imputees(niveau_de_vie_2025: float) -> dict[str, float]:
    """Dépenses annuelles de consommation par poste, en euros de 2025, d'un ménage moyen du décile de ce niveau de vie."""
    i = decile(niveau_de_vie_2025) - 1
    en_2017 = {poste: valeurs[i] for poste, valeurs in DEPENSES_2017.items()}
    # Électricité et gaz non séparables vont avec l'électricité, au même taux de TVA. Le reste de la dépense d'énergie du logement :
    # bois, charbon, chaleur des réseaux.
    en_2017["electricite"] += en_2017.pop("electricite_ou_gaz")
    en_2017["autres_energies_logement"] = en_2017.pop("energie_logement") - en_2017["electricite"] - en_2017["gaz"] - en_2017["fioul"]
    en_2017 |= {poste: sum(valeurs[i] for taux, valeurs in CODES_2017.values() if taux == poste) for poste in HORS_ENERGIE}
    # shortcut: l'électricité et le gaz suivent l'indice de l'énergie, qui mêle produits pétroliers ; passer aux indices par produit si l'écart compte.
    return {poste: round(montant * IPC[INDICE_DU_POSTE[poste]]["2025"] / IPC[INDICE_DU_POSTE[poste]]["2017"]) for poste, montant in en_2017.items()}
