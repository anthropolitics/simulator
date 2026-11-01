from simulator.mesures import Mesure
from simulator.mesures.allocations_familiales_reservees_aux_francais import reserver, un_parent_francais

MESURE = Mesure(
    id="prestations_non_contributives_reservees_aux_francais",
    titre="Prestations sociales non contributives réservées aux Français",
    candidats=("Éric Zemmour", "Nicolas Dupont-Aignan"),
    source=(
        "https://www.debout-la-france.fr/projet/immigration-et-assimilation/ ; https://www.debout-la-france.fr/actualite/communique-nicolas-dupont-aignan-a-limoges/ ; "
        "https://www.institutmontaigne.org/presidentielle-2022/eric-zemmour/retirer-les-aides-sociales-non-contributives-aux-etrangers-extra-europeens"
    ),
    citation=(
        "Nicolas Dupont-Aignan (Debout la France) : « Supprimer les aides sociales non contributives pour les étrangers (RSA, allocations "
        "familiales, aides au logement…) » ; Éric Zemmour (BFMTV, 7 décembre 2021) : « La solidarité qui n’est pas contributive, c’est-à-dire le "
        "RSA, les allocations familiales, le minimum vieillesse [...] tout cela doit être réservé aux Français »."
    ),
    traduction=(
        "Sources consultées le 31 octobre 2026. Nicolas Dupont-Aignan : la page « Immigration et assimilation » du projet de Debout la France "
        "(© 2026) et le communiqué de Limoges du 20 octobre 2026, dont les « 20 mesures chocs » comptent la « Suppression des aides sociales non "
        "contributives aux étranger[s] ». La page « Économie et travail » du même projet écrit au contraire, dans ses économies, « conditionner les "
        "aides sociales non contributives à 5 ans de résidence pour tout étranger », comme le projet de 2022 (décision 81) : le calcul suit la "
        "mesure du communiqué daté et de la page consacrée à l'immigration. Éric Zemmour : la mesure de 2022 est connue par l'Institut Montaigne, "
        "qui cite l'entretien de BFMTV et note que l'équipe de campagne parlait d'« étrangers extra-communautaires » ; le programme de 2022 "
        "(programme.zemmour2022.fr) refuse l'accès (erreur 403) et Reconquête n'a publié aucun programme pour 2027. Le plan d'économies de Sarah "
        "Knafo, que le site de Reconquête relaie (2026), garde la « Limitation des prestations sociales non contributives (RSA, APL, "
        "allocations familiales…) aux citoyens français » (https://www.budget2027.fr/, mesure 3) : le calcul réserve donc les prestations aux "
        "Français, sans exception pour les Européens. Toutes les prestations non contributives que calcule OpenFisca le sont : prestations "
        "familiales, minima sociaux (RSA, prime d'activité, allocation aux adultes handicapés, minimum vieillesse, allocation de solidarité "
        "spécifique) et aides au logement. Elles sont annulées lorsque aucun des parents n'est de nationalité française, quelle que soit "
        "l'ancienneté du titre de séjour ; il suffit qu'un parent soit français, comme pour les prestations familiales du programme du RN."
    ),
    appliquer=lambda reforme: reserver(reforme, ("prestations_familiales", "minima_sociaux", "aides_logement"), un_parent_francais),
    a_confirmer=True,  # Éric Zemmour : déclaration de 2021 et plan d'une dirigeante de son parti ; aucun programme 2027
    hypotheses=(
        "Selon l'Institut Montaigne, la mesure suppose une révision constitutionnelle et la dénonciation de traités ; le calcul la tient pour "
        "acquise. Les aides locales et "
        "les prestations que ne calcule pas OpenFisca ne sont pas simulées, pas plus que les effets sur les comportements, dont les départs du "
        "territoire et les naturalisations."
    ),
)
