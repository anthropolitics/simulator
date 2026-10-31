"""Retraite d'un salarié du privé : âge de départ au taux plein, pension brute du régime général et de l'Agirc-Arrco, cumul sur l'espérance de vie.

OpenFisca ne calcule aucune pension : ce moteur simplifié applique la législation en vigueur, figée, avec les paramètres monétaires de
2025 et des montants en euros 2025. Un salaire constant en euros 2025 reproduit un cas type du COR (salaire en proportion constante du
salaire moyen) avec une croissance réelle nulle : le salaire annuel moyen des 25 meilleures années est alors ce salaire, plafonné.

Simplifications : naissance au 1er janvier ; carrière au même salaire depuis l'âge de début, sauf des années sans emploi qui ne valident
aucun trimestre et viennent après les débuts de carrière ; un trimestre validé tous les 12 / n mois pour n trimestres validés par an ;
tous les trimestres sont cotisés, au régime général ; ni enfants (majorations de durée, 23 ou 24 meilleures années des mères), ni rachats,
ni service national, ni réversion ; le minimum contributif se compare à la pension surcote comprise.
"""

from dataclasses import dataclass
from math import ceil, inf


@dataclass(frozen=True)
class Parametres:
    # Âge légal en mois et durée requise en trimestres, par génération : (première génération, valeur). Les générations 1961 et 1965,
    # coupées en cours d'année, prennent la valeur d'une naissance en janvier. Code de la sécurité sociale (CSS), art. L161-17-2 et
    # L161-17-3 modifiés par l'art. 105 de la LFSS pour 2026 (loi n° 2025-1403 du 30 décembre 2025), qui décale d'une génération le
    # calendrier de 2023 pour les retraites prenant effet à partir du 1er septembre 2026 ; circulaire Cnav n° 2026-07 du 5 mars 2026,
    # https://legislation.lassuranceretraite.fr/Pdf/circulaire_cnav_2026_07_05032026.pdf
    age_legal: tuple[tuple[int, int], ...] = (
        (1961, 62 * 12),
        (1962, 62 * 12 + 6),
        (1963, 62 * 12 + 9),
        (1966, 63 * 12 + 3),
        (1967, 63 * 12 + 6),
        (1968, 63 * 12 + 9),
        (1969, 64 * 12),
    )
    duree_requise: tuple[tuple[int, int], ...] = ((1961, 168), (1962, 169), (1963, 170), (1966, 172))
    # Renseignés, ils valent pour toutes les générations : le module ne calcule que des actifs, pas encore partis.
    age_legal_cible: int | None = None
    duree_requise_cible: int | None = None
    age_taux_plein: int = 67 * 12  # L351-8 1° CSS, inchangé (circulaire Cnav n° 2026-07, point 3)

    # Régime général. Décote et surcote : 1,25 % par trimestre, la décote dans la limite de 20 trimestres (R351-27, L351-1-2 CSS).
    taux_plein: float = 0.5
    decote: float = 0.0125
    decote_max: int = 20
    surcote: float = 0.0125
    plafond_securite_sociale: float = 47_100  # 2025, arrêté du 19 décembre 2024
    # 150 heures au SMIC horaire de 2025 (11,88 €), soit 1 782 € par trimestre, 4 au plus par an ; circulaire Cnav n° 2024-40 du 23 décembre 2024,
    # https://legislation.lassuranceretraite.fr/Pdf/circulaire_cnav_2024_40_23122024.pdf
    salaire_trimestre: float = 150 * 11.88
    # Minimum contributif mensuel 2025, entier puis majoré (au moins 120 trimestres cotisés), proratisé par la durée et réduit pour que
    # l'ensemble des retraites ne dépasse pas le plafond (L351-10 CSS) ; circulaire Cnav n° 2025-04 du 20 janvier 2025,
    # https://legislation.lassuranceretraite.fr/Pdf/circulaire_cnav_2025_04_20012025.pdf
    minimum_contributif: float = 747.69
    minimum_contributif_majore: float = 893.65
    trimestres_cotises_majoration: int = 120
    plafond_minimum_contributif: float = 1_394.86
    minimum_pension: float = 0  # minimum mensuel de la pension totale au taux plein, proratisé par la durée comme le minimum contributif ; aucun en 2025

    # Agirc-Arrco : taux de calcul des points sur les tranches 1 (jusqu'au plafond) et 2 (de 1 à 8 plafonds), appelés à 127 % (7,87 % et
    # 21,59 %) ; prix d'achat 2025 et valeur de service depuis le 1er novembre 2024, inchangée au 1er novembre 2025. Agirc-Arrco, Chiffres clés,
    # https://www.agirc-arrco.fr/storage/2025/04/chiffrAA_2025.pdf et https://www.agirc-arrco.fr/storage/2025/04/Chiffres-cles_2025.pdf
    taux_points_tranche_1: float = 0.062
    taux_points_tranche_2: float = 0.17
    prix_achat_point: float = 20.1877
    valeur_point: float = 1.4386

    # Carrières longues (L351-1-1 et D351-1-1 CSS) : (début d'activité avant cet âge, âge de départ en mois[, trimestres cotisés exigés en plus])
    # à partir de la génération 1971, avec la durée requise cotisée. Débuter avant un âge, c'est valider 5 trimestres à la fin de l'année de cet anniversaire.
    # Circulaire Cnav n° 2026-29 du 4 septembre 2026, https://legislation.lassuranceretraite.fr/Documents/Circulaires/Pdf/circulaire_cnav_2026_29_04092026.pdf
    carrieres_longues: tuple[tuple[int, ...], ...] = ((16, 58 * 12), (18, 60 * 12), (20, 62 * 12), (21, 63 * 12))
    duree_carriere_longue: int | None = None  # durée cotisée exigée ; par défaut, la durée requise de la génération
    # Début avant 20 ans, générations antérieures : âge abaissé par le décret n° 2026-345 du 7 mai 2026 (même circulaire). Le plus bas des
    # deux âges s'applique : une mesure qui relève l'âge de la borne de 20 ans remplace aussi ce calendrier.
    carriere_longue_20_ans: tuple[tuple[int, int], ...] = (
        (1961, 60 * 12),
        (1964, 60 * 12 + 6),
        (1965, 60 * 12 + 9),
        (1967, 61 * 12),
        (1968, 61 * 12 + 3),
        (1969, 61 * 12 + 6),
        (1970, 61 * 12 + 9),
        (1971, 62 * 12),
    )


PARAMETRES_ACTUELS = Parametres()

# Espérance de vie du moment en 2025, de 55 à 75 ans, femmes puis hommes. Insee, Bilan démographique 2025, tableau DEC5 « Espérance de vie
# par sexe et âge », résultats provisoires à fin 2025, https://www.insee.fr/fr/statistiques/fichier/8721189/5_Esperance_vie.xlsx
FEMMES = (32.5, 31.5, 30.6, 29.7, 28.8, 27.9, 27.1, 26.2, 25.3, 24.4, 23.6, 22.7, 21.9, 21.0, 20.2, 19.4, 18.6, 17.7, 16.9, 16.1, 15.3)
HOMMES = (28.1, 27.3, 26.4, 25.6, 24.8, 23.9, 23.1, 22.3, 21.5, 20.7, 20.0, 19.2, 18.5, 17.7, 17.0, 16.3, 15.5, 14.9, 14.2, 13.5, 12.8)
# Le persona n'a pas de sexe : moyenne simple des femmes et des hommes.
ESPERANCE_DE_VIE = {age: (f + h) / 2 for age, f, h in zip(range(55, 76), FEMMES, HOMMES)}


@dataclass(frozen=True)
class Depart:
    age_annees: int
    age_mois: int
    pension_mensuelle: float  # brute, régime général et Agirc-Arrco
    regime_general: float  # mensuelle brute, minimum contributif et minimum de pension compris
    agirc_arrco: float  # mensuelle brute
    trimestres: int
    taux: float  # du régime général, décote comprise
    salaire_annuel_moyen: float
    cumul: float  # pension brute sur l'espérance de vie à l'âge de départ, sans actualisation


def selon_generation(table: tuple[tuple[int, int], ...], annee: int) -> int:
    for premiere, valeur in reversed(table):
        if annee >= premiere:
            return valeur
    raise ValueError(f"Les paramètres commencent à la génération {table[0][0]}.")


def esperance_de_vie(age: int) -> float:
    """Espérance de vie à cet âge en mois, interpolée entre deux âges entiers."""
    annees, mois = divmod(age, 12)
    e = ESPERANCE_DE_VIE
    return e[annees] + (e[annees + 1] - e[annees]) * mois / 12 if mois else e[annees]


def coefficient_agirc_arrco(trimestres: int) -> float:
    """Coefficient d'anticipation pour ces trimestres manquants : 1 % par trimestre jusqu'à 12, 1,25 % jusqu'à 20, 1,75 % au-delà.

    Agirc-Arrco, « Les coefficients de minoration », septembre 2026, https://www.agirc-arrco.fr/storage/2024/10/Coefficients-de-minorations-AA.pdf ;
    le coefficient de solidarité est supprimé pour les retraites prenant effet à partir du 1er décembre 2023 (accord du 5 octobre 2023).
    """
    return 1 - 0.01 * min(trimestres, 12) - 0.0125 * min(max(trimestres - 12, 0), 8) - 0.0175 * max(trimestres - 20, 0)


def depart(
    annee_naissance: int,
    age_debut: int,
    salaire_annuel_brut: float,
    annees_sans_emploi: int = 0,
    parametres: Parametres = PARAMETRES_ACTUELS,
    age_depart: int | None = None,
) -> Depart:
    """Départ à la retraite d'un salarié du privé.

    La personne part au plus tôt à l'âge où elle a le taux plein : âge légal et durée requise atteints, carrière longue, ou âge du taux
    plein automatique. age_depart, en mois, impose un autre âge, à partir de l'âge légal, avec décote ou surcote.
    """
    p = parametres
    age_legal = p.age_legal_cible or selon_generation(p.age_legal, annee_naissance)
    duree = p.duree_requise_cible or selon_generation(p.duree_requise, annee_naissance)
    par_an = min(4, int(salaire_annuel_brut // p.salaire_trimestre))
    debut = 12 * (age_debut + annees_sans_emploi)

    def trimestres(age: int) -> int:
        return max(age - debut, 0) * par_an // 12

    def age_pour(n: int) -> float:
        return debut + ceil(12 * n / par_an) if par_an else inf

    ages = [max(age_legal, age_pour(duree)), p.age_taux_plein]
    for avant, age_anticipe, *en_plus in p.carrieres_longues:
        if (avant - age_debut + 1) * par_an >= 5:
            if avant == 20:
                age_anticipe = min(age_anticipe, selon_generation(p.carriere_longue_20_ans, annee_naissance))
            ages.append(max(age_anticipe, age_pour((p.duree_carriere_longue or duree) + sum(en_plus))))
    taux_plein_a = int(min(ages))
    age = taux_plein_a if age_depart is None else age_depart
    if age < min(age_legal, taux_plein_a):
        raise ValueError("Départ avant l'âge légal sans carrière longue.")

    t = trimestres(age)
    avant_taux_plein = ceil((p.age_taux_plein - age) / 3)
    manquants = 0 if age >= taux_plein_a else min(duree - t, avant_taux_plein)
    taux = p.taux_plein * (1 - p.decote * min(manquants, p.decote_max))
    surcote = max(t - max(duree, trimestres(age_legal)), 0)
    salaire_moyen = min(salaire_annuel_brut, p.plafond_securite_sociale)
    prorata = min(t / duree, 1)
    regime_general = salaire_moyen * taux * prorata * (1 + p.surcote * surcote) / 12

    tranche_2 = min(max(salaire_annuel_brut - p.plafond_securite_sociale, 0), 7 * p.plafond_securite_sociale)
    points = (salaire_moyen * p.taux_points_tranche_1 + tranche_2 * p.taux_points_tranche_2) / p.prix_achat_point
    # Au-delà de 20 trimestres manquants pour la durée, seul l'âge compte.
    coefficient = coefficient_agirc_arrco(avant_taux_plein if duree - t >= 20 else manquants) if manquants else 1
    agirc_arrco = points * max(age - debut, 0) / 12 * p.valeur_point * coefficient / 12

    if not manquants:
        minimum = p.minimum_contributif_majore if t >= p.trimestres_cotises_majoration else p.minimum_contributif
        regime_general += max(min(minimum * prorata - regime_general, p.plafond_minimum_contributif - regime_general - agirc_arrco), 0)
        regime_general += max(p.minimum_pension * prorata - regime_general - agirc_arrco, 0)
    pension = regime_general + agirc_arrco
    return Depart(
        age_annees=age // 12,
        age_mois=age % 12,
        pension_mensuelle=pension,
        regime_general=regime_general,
        agirc_arrco=agirc_arrco,
        trimestres=t,
        taux=taux,
        salaire_annuel_moyen=salaire_moyen,
        cumul=pension * 12 * esperance_de_vie(age),
    )
