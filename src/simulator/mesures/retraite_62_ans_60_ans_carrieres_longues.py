from dataclasses import replace

from simulator.mesures import Mesure
from simulator.retraites import Parametres

DUREE_CARRIERE_LONGUE = 160  # 40 annuités
# (début avant cet âge, âge de départ en mois, trimestres cotisés en plus des 160) : un début à 20 ans au plus tard part à 60 ans avec
# 160 trimestres, puis 2 trimestres de plus par année de début jusqu'à 23 ans ; avant 16 ans, 58 ans avec la durée requise de 168 trimestres.
CARRIERES_LONGUES = ((16, 58 * 12, 8), (21, 60 * 12), (22, 62 * 12, 2), (23, 62 * 12, 4), (24, 62 * 12, 6))


def retraites(parametres: Parametres) -> Parametres:
    return replace(
        parametres,
        age_legal_cible=62 * 12,
        duree_requise_cible=168,
        duree_carriere_longue=DUREE_CARRIERE_LONGUE,
        carrieres_longues=CARRIERES_LONGUES,
    )


MESURE = Mesure(
    id="retraite_62_ans_60_ans_carrieres_longues",
    titre="Retraite à 62 ans avec 42 annuités au plus, à 60 ans avec 40 annuités pour un début avant 20 ans",
    candidats=("Marine Le Pen",),
    source="https://rassemblementnational.fr/22-mesures",
    citation=(
        "« Refuser tout allongement de l'âge de départ à la retraite. » ; « Permettre à ceux qui ont commencé à travailler avant 20 ans pendant "
        "40 annuités de prendre leur retraite à 60 ans. »"
    ),
    traduction=(
        "Sources, consultées le 31 octobre 2026. Les « 22 mesures » du site du Rassemblement national datent de la présidentielle 2022. Devant le "
        "Medef, le 27 août 2026, la candidate a repris « un âge de départ à 62 ans, voire 60 ans pour ceux qui ont travaillé « avant 20 ans » et "
        "auront cotisé 40 ans » (AFP, La Gazette France, 28 août 2026) ; Yahoo Finance (24 septembre 2026) ajoute, pour les autres, une « évolution "
        "progressive jusqu'à 42 années de cotisation ». Le détail vient des amendements du groupe RN au projet de réforme de 2023 (n° CF412 du 26 "
        "janvier 2023, https://www.assemblee-nationale.fr/dyn/16/amendements/0760/CION_FIN/CF412.pdf, et n° 18985 du 2 février 2023) : « aucun "
        "Français n'aurait à cotiser plus de 42 annuités » ; 60 ans avec 160 trimestres pour un début « entre 17 et 20 ans » ; « pour les personnes "
        "entrées dans la vie active après 20 ans, et cela jusqu'à 24 ans et demi, l'âge du taux plein évoluerait progressivement à raison de 1 "
        "trimestre pour 6 mois supplémentaires (par un système progressif de 160 à 168 trimestres de cotisation) » ; l'âge légal est « fixé entre 60 "
        "et 62 ans » pour un début entre 20 et 21 ans, 62 ans après. La proposition de loi n° 284 du 18 septembre 2024 du groupe RN fixait aussi "
        "62 ans et 168 trimestres. Le calcul : âge légal de 62 ans et durée requise de 168 trimestres pour toutes les générations (age_legal_cible, "
        "duree_requise_cible), au lieu de 62 ans et 9 mois à 64 ans et de 170 à 172 trimestres. Carrières longues : le moteur lit « commencer avant N "
        "ans » comme valider 5 trimestres avant la fin de l'année des N ans, soit, à 4 trimestres par an, un début à N - 1 ans au plus tard. La borne "
        "de 21 ans donne donc 60 ans avec 160 trimestres cotisés à un début avant 20 ans, comme le dit la source, et à un début à 20 ans, qui ouvre la "
        "tranche progressive sans trimestre de plus et dont l'âge légal part de 60 ans. Les âges entiers de début comptent ensuite 2 trimestres de "
        "plus par année (1 par 6 mois) : 162 trimestres pour un début à 21 ans (borne de 22 ans), 164 à 22 ans, 166 à 23 ans ; à 24 ans, les 168 "
        "trimestres du droit commun. Ces bornes gardent l'âge légal de 62 ans, l'âge « entre 60 et 62 ans » d'un début entre 20 et 21 ans valant "
        "62 ans à 21 ans ; avec la durée exigée, le départ vient de toute façon après 62 ans, sauf à 21 ans (61 ans et 6 mois, relevés à 62 ans). "
        "La source ne dit rien d'un début avant 16 ans : le départ à 58 ans de la loi actuelle est gardé, avec la durée requise (168 trimestres), "
        "pour ne pas reculer l'âge de départ, ce que la source refuse. Un départ au taux plein avec 160 à 166 trimestres reste proratisé sur les "
        "168 trimestres de la durée requise, la source ne parlant que du taux plein. L'âge du taux plein automatique (67 ans), la décote et la surcote "
        "ne changent pas. La mesure s'applique d'emblée."
    ),
    retraites=retraites,
    a_confirmer=True,  # « 22 mesures » de la campagne 2022 ; en 2026, seulement des propos rapportés par la presse
    hypotheses=(
        "La réindexation des retraites sur l'inflation ne change rien dans un calcul en euros constants de 2025 ; le minimum vieillesse à 1 000 € "
        "est la mesure minimum_vieillesse_1000. Les incitations à travailler au-delà de l'âge de la retraite pour les seniors qui ont leurs "
        "trimestres (suppression de leurs cotisations retraite et chômage) ne sont pas simulées. La carrière et le salaire sont tenus fixes ; ni "
        "l'emploi des seniors, ni le financement (9 milliards d'euros par an selon la candidate, 23 à 38 selon l'Institut Montaigne) ne sont calculés."
    ),
)
