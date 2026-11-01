from simulator.mesures import Mesure


def appliquer(reforme):
    def modifier(parametres):
        # Abattement de 30 % porté à 100 % : la résidence principale sort de l'assiette.
        parametres.taxation_capital.impot_fortune_immobiliere_ifi_partir_2018.reduc_exo.abattement_residence_principale.update(start="2025-01-01", value=1)
        return parametres

    reforme.modify_parameters(modifier_function=modifier)


MESURE = Mesure(
    id="ifi_hors_residence_principale",
    titre="Résidence principale exclue de l'impôt sur la fortune immobilière",
    candidats=("Éric Zemmour",),
    source="https://www.institutmontaigne.org/presidentielle-2022/eric-zemmour/reformer-limpot-sur-la-fortune-immobiliere-ifi-en-excluant-la-residence-principale-de-son-calcul",
    citation="Réformer l'impôt sur la fortune immobilière (IFI) en excluant la résidence principale de son calcul",
    traduction=(
        "Mesure de la campagne de 2022 : le programme d'alors (programme.zemmour2022.fr, redirigé vers programme.ericzemmour.fr) refuse l'accès "
        "(erreur 403) et Reconquête n'a publié aucun programme pour 2027 ; la mesure est connue par la fiche de l'Institut Montaigne, qui en donne "
        "l'intitulé cité, et par la presse (https://www.toutsurmesfinances.com/argent/a/eric-zemmour-programme, mis à jour le 27 octobre 2026) ; "
        "sources consultées le 31 octobre 2026. À partir du 1er janvier 2025, l'abattement de 30 % sur la valeur de la résidence principale (article 973 du CGI) passe à 100 % : "
        "l'IFI ne porte plus que sur les autres biens immobiliers. Le seuil d'assujettissement de 1,3 M€, le barème, la décote et le plafonnement "
        "ne changent pas."
    ),
    appliquer=appliquer,
    a_confirmer=True,  # mesure de la campagne de 2022, connue par une source secondaire ; aucun programme 2027
    hypotheses="Le patrimoine est tenu fixe : ni réallocation vers la résidence principale, ni effet de la mesure sur les prix immobiliers.",
)
