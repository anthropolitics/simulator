"""Le persona : un ménage type, traduit en situation OpenFisca."""

from pydantic import BaseModel, Field, model_validator

ANNEE = "2025"
# Les minima sociaux regardent les revenus des mois précédents : sans l'année d'avant, OpenFisca verse un RSA fantôme.
ANNEES = (str(int(ANNEE) - 1), ANNEE)
HEURES_TEMPS_PLEIN = 35 * 52 / 12


class Adulte(BaseModel, frozen=True):
    age: int = Field(default=40, ge=18, le=110)
    salaire_brut_mensuel: float = Field(default=0, ge=0, le=100_000)
    au_smic: bool = Field(default=False, description="Payé au SMIC à temps plein : le salaire suit les mesures sur le SMIC.")
    retraite_brute_mensuelle: float = Field(default=0, ge=0, le=50_000)
    nationalite: str = Field(default="FR", pattern="^[A-Z]{2}$", description="Code ISO du pays.")
    annees_titre_sejour: int = Field(default=0, ge=0, le=90, description="Pour un étranger : ancienneté de son titre de séjour.")
    apprenti: bool = Field(default=False, description="En contrat d'apprentissage depuis un an ; suppose un âge de 16 à 24 ans.")
    annees_travail_france: int = Field(default=0, ge=0, le=70, description="Années travaillées en France, en équivalent temps plein.")
    insertion_15h: bool = Field(default=False, description="Au moins 15 heures par semaine de formation ou de recherche active d'emploi.")


class Depenses(BaseModel, frozen=True):
    """Dépenses annuelles TTC du ménage ; un poste absent est imputé selon son niveau de vie (enquête Budget de famille de l'Insee)."""

    electricite: float | None = Field(default=None, ge=0, le=100_000)
    gaz: float | None = Field(default=None, ge=0, le=100_000)
    fioul: float | None = Field(default=None, ge=0, le=100_000)
    autres_energies_logement: float | None = Field(default=None, ge=0, le=100_000, description="Bois, charbon, chaleur des réseaux.")
    carburants: float | None = Field(default=None, ge=0, le=100_000)
    hors_energie_taux_normal: float | None = Field(default=None, ge=0, le=1_000_000, description="Reste de la consommation au taux normal de TVA (20 %).")
    hors_energie_taux_intermediaire: float | None = Field(
        default=None,
        ge=0,
        le=1_000_000,
        description="Reste de la consommation au taux intermédiaire (10 %) : restaurants, hôtels, transports, médicaments non remboursables.",
    )
    hors_energie_taux_reduit: float | None = Field(
        default=None, ge=0, le=1_000_000, description="Reste de la consommation au taux réduit (5,5 %) : alimentation, eau, livres."
    )
    hors_energie_taux_particulier: float | None = Field(
        default=None, ge=0, le=1_000_000, description="Reste de la consommation au taux particulier (2,1 %) : presse."
    )


class Persona(BaseModel, frozen=True):
    adultes: tuple[Adulte, ...] = Field(min_length=1, max_length=2, description="Deux adultes forment un couple marié.")
    enfants: tuple[int, ...] = Field(default=(), max_length=6, description="Âge de chaque enfant à charge.")
    loyer_mensuel: float = Field(default=0, ge=0, le=20_000)
    code_commune: str | None = Field(default=None, pattern="^[0-9AB]{5}$", description="Code INSEE ; il fixe la zone des aides au logement.")
    patrimoine_financier: float = Field(default=0, ge=0, description="Patrimoine financier net du foyer.")
    patrimoine_immobilier: float = Field(default=0, ge=0, description="Patrimoine immobilier net du foyer, résidence principale comprise.")
    residence_principale: float = Field(default=0, ge=0, description="Valeur nette de la résidence principale, comprise dans le patrimoine immobilier.")
    depenses: Depenses = Field(default_factory=Depenses)

    @model_validator(mode="before")
    @classmethod
    def depuis_ancien_format(cls, donnees):
        # Format de la première version de l'API : un salaire par adulte et un nombre d'enfants de 10 ans.
        if isinstance(donnees, dict) and "salaire_brut_mensuel" in donnees:
            salaires = [donnees["salaire_brut_mensuel"], donnees.get("salaire_brut_mensuel_conjoint")]
            return {"adultes": [{"salaire_brut_mensuel": s} for s in salaires if s is not None], "enfants": [10] * donnees.get("enfants", 0)}
        return donnees

    @model_validator(mode="after")
    def residence_dans_le_patrimoine(self):
        if self.residence_principale > self.patrimoine_immobilier:
            raise ValueError("La résidence principale fait partie du patrimoine immobilier : elle ne peut pas le dépasser.")
        return self

    @model_validator(mode="after")
    def commune_si_loyer(self):
        if self.loyer_mensuel and self.code_commune is None:
            raise ValueError("Un loyer demande le code de la commune, qui fixe la zone des aides au logement.")
        return self

    @model_validator(mode="after")
    def enfants_mineurs_ou_etudiants(self):
        if any(not 0 <= age <= 25 for age in self.enfants):
            raise ValueError("Un enfant à charge a entre 0 et 25 ans.")
        return self


def salaire_annuel(adulte: Adulte, annee: str, smic: dict[str, float], smic_actuel: dict[str, float]) -> float:
    if adulte.au_smic:
        return smic[annee]
    salaire = adulte.salaire_brut_mensuel * 12
    # Un salaire au moins égal au SMIC actuel est celui d'un temps plein : la loi le relève au SMIC simulé s'il passe dessous.
    # shortcut: un salaire plus bas est lu comme un temps partiel et reste fixe ; à revoir si le persona décrit ses heures.
    return max(salaire, smic[annee]) if salaire >= smic_actuel[annee] else salaire


def situation(persona: Persona, smic: dict[str, float], smic_actuel: dict[str, float]) -> dict:
    """Situation OpenFisca du persona ; smic et smic_actuel donnent, par année, le SMIC à temps plein de la législation simulée et de la loi actuelle."""
    adultes = [f"adulte{i + 1}" for i in range(len(persona.adultes))]
    petits = [f"enfant{i + 1}" for i in range(len(persona.enfants))]
    individus: dict[str, dict] = {}
    for nom, a in zip(adultes, persona.adultes):
        individu = {
            "date_naissance": {"ETERNITY": f"{int(ANNEE) - a.age}-01-01"},
            "statut_marital": {annee: "marie" if len(adultes) == 2 else "celibataire" for annee in ANNEES},
            "salaire_de_base": {annee: salaire_annuel(a, annee, smic, smic_actuel) for annee in ANNEES},
        }
        if a.retraite_brute_mensuelle:
            individu["retraite_brute"] = {annee: a.retraite_brute_mensuelle * 12 for annee in ANNEES}
        if a.nationalite != "FR":
            individu["nationalite"] = {annee: a.nationalite for annee in ANNEES}
            individu["duree_possession_titre_sejour"] = {annee: a.annees_titre_sejour for annee in ANNEES}
        if a.annees_travail_france:
            individu["annees_travail_france"] = {ANNEE: a.annees_travail_france}
        if a.insertion_15h:
            individu["insertion_15h"] = {ANNEE: True}
        if a.apprenti:
            individu["apprentissage_contrat_debut"] = {annee: f"{int(ANNEE) - 1}-01-01" for annee in ANNEES}
        individus[nom] = individu
    individus |= {nom: {"date_naissance": {"ETERNITY": f"{int(ANNEE) - age}-01-01"}} for nom, age in zip(petits, persona.enfants)}
    # Un enfant est français si un parent l'est ; sinon il suit le premier adulte. Sans cela, OpenFisca le croit français et la
    # condition de nationalité de la prime d'activité, qui regarde tous les membres de la famille, laisse passer des parents étrangers.
    if petits and all(a.nationalite != "FR" for a in persona.adultes):
        premier = persona.adultes[0]
        for nom in petits:
            individus[nom] |= {
                "nationalite": {annee: premier.nationalite for annee in ANNEES},
                "duree_possession_titre_sejour": {annee: premier.annees_titre_sejour for annee in ANNEES},
            }
    menage: dict = {"personne_de_reference": adultes[:1], "conjoint": adultes[1:], "enfants": petits}
    if persona.loyer_mensuel:
        menage |= {
            "loyer": {annee: persona.loyer_mensuel * 12 for annee in ANNEES},
            "depcom": {annee: persona.code_commune for annee in ANNEES},
            "statut_occupation_logement": {annee: "locataire_vide" for annee in ANNEES},
        }
    menage |= {f"depense_{poste}": {ANNEE: montant} for poste, montant in persona.depenses if montant is not None}
    foyer: dict = {"declarants": adultes, "personnes_a_charge": petits}
    if persona.patrimoine_financier or persona.patrimoine_immobilier:
        foyer |= {
            "patrimoine_financier": {ANNEE: persona.patrimoine_financier},
            "patrimoine_immobilier": {ANNEE: persona.patrimoine_immobilier},
            # Cases de la déclaration d'IFI : valeur de la résidence principale, avant son abattement de 30 %, et des autres immeubles.
            "b1ab": {ANNEE: persona.residence_principale},
            "b1ac": {ANNEE: persona.patrimoine_immobilier - persona.residence_principale},
        }
    return {
        "individus": individus,
        "foyers_fiscaux": {"foyer": foyer},
        "familles": {"famille": {"parents": adultes, "enfants": petits}},
        "menages": {"menage": menage},
    }
