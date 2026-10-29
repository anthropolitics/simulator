# simulator

Moteur de simulation open source qui calcule ce que chaque programme politique change, concrètement, pour des ménages français types.

> **Statut : en construction.** Un premier squelette calcule l'avant/après d'un foyer pour un scénario d'exemple ; la traduction des programmes arrive en phase 2.

## Pourquoi

Beaucoup d'électeurs votent sans savoir ce qu'une mesure changerait pour eux. Les chiffrages sérieux existent, mais ils restent illisibles pour le grand public et absents des réseaux sociaux, où se forme une bonne part des opinions.

Ce moteur rend ces chiffres calculables, vérifiables et rejouables, ménage par ménage, pour que chacun puisse voter en connaissance de cause, selon ses propres intérêts et critères. Il informe et chiffre ; il ne dit jamais pour qui voter.

## Ce que fait le moteur

Le moteur prend un **persona** et un **scénario**, et renvoie ce que le scénario change pour ce persona.

- **Persona** : un ménage type (composition, revenus, logement, territoire), calé sur les statistiques publiques de l'INSEE.
- **Scénario** : les mesures d'un programme, traduites en paramètres documentés et sourcés.
- **Résultat** : un fichier JSON versionné, par exemple le revenu disponible annuel avant et après, détaillé en impôts, cotisations et prestations.

Exemple de lecture : « Sophie, infirmière à Lille, deux enfants. Programme A : + X €/an. Programme B : − Y €/an. Programme C : entre − Z et + W €/an, selon l'effet sur l'emploi. »

Le calcul sépare deux types d'effets :

| Effets | Exemples | Consensus | Présentation |
|---|---|---|---|
| Mécaniques | Barème de l'impôt, cotisations, prestations | Fort : c'est la loi appliquée | Une valeur |
| Comportement et macro | Emploi, prix, croissance | Faible | Une fourchette sourcée, seulement quand elle change la conclusion |

## Principes non négociables

Le moteur ne vaut que s'il reste crédible pour tous les bords.

1. **Tout est sourcé.** Chaque paramètre cite sa source : texte de loi, INSEE ou littérature économique. Un paramètre sans source n'est pas fusionné.
2. **Les incertitudes sont visibles.** Effets mécaniques et effets de comportement restent séparés ; les seconds sont donnés en fourchettes.
3. **La traduction des programmes est publique.** Chaque mesure devient des paramètres documentés dans ce dépôt, contestables par issue, y compris par les partis.
4. **Aucune consigne de vote.** Le moteur produit des effets, jamais un classement des programmes ni un « bon » choix.
5. **Tout est reproductible.** Chaque résultat publié renvoie à la version du code, des paramètres et du scénario qui l'a produit.

## Périmètre du MVP (présidentielle 2027)

Objectif : un moteur crédible sur un périmètre réduit, en ligne avant le premier tour (avril 2027).

Dans le MVP :

- effets mécaniques via OpenFisca-France : impôts, cotisations, prestations ;
- une dizaine de mesures phares par programme, pour les principaux candidats ;
- 5 à 8 personas ménages types ;
- fourchettes macro uniquement quand elles changent la conclusion.

Hors MVP :

- agents IA qui « vivent » dans la simulation ;
- économie dynamique complète.

## Vision à terme

Une maquette simplifiée de la société française, avec des personas, une économie et un environnement, dont chaque règle, constante et paramètre est justifié par un consensus scientifique. On y simule l'effet des choix économiques des différents partis et l'évolution des personas d'un scénario à l'autre.

Le MVP en est la première brique : on commence par ce qui est solide, la législation déjà codée, et on ajoute la dynamique ensuite.

## Feuille de route

| Phase | Période | Contenu |
|---|---|---|
| 1 | Novembre 2026 | Socle moteur sur OpenFisca, format des personas et du catalogue de mesures |
| 2 | Décembre 2026 à janvier 2027 | Premiers programmes traduits, résultats publiés de bout en bout |
| 3 | Février à mars 2027 | Mises à jour au fil des programmes publiés |
| 4 | Avril 2027 | Rythme maximal jusqu'au second tour |

## Stack

| Brique | Choix | Pourquoi |
|---|---|---|
| Moteur | Python, [OpenFisca-France](https://github.com/openfisca/openfisca-france) | Législation française déjà codée et open source |
| Personas | Statistiques publiques INSEE | Ménages types calés sur la réalité |
| Résultats | FastAPI, JSON versionnés | Reproductibles, lisibles par d'autres outils |

## Ce qui existe déjà

On ne réécrit pas de moteur fiscal : on assemble des briques existantes et on les rend lisibles.

| Projet | Ce qu'il fait | Ce qui manque pour notre usage |
|---|---|---|
| OpenFisca-France, LexImpact | Code la législation socio-fiscale, chiffre des réformes sur des foyers types | Outils d'experts, pas de contenu grand public |
| PolicyEngine | Moteur open source ménage par ménage, proche de notre idée | États-Unis et Royaume-Uni seulement |
| Chiffrages IPP, iFRAP, Institut Montaigne | Coût et effets des programmes | Rapports longs, peu lus |
| Elyze, Boussole présidentielle | Rapprochent opinions et candidats | Ne chiffrent pas l'impact sur le ménage |
| AgentSociety, Aaru | Simulent des populations avec des agents IA | Ni centrés sur la France, ni sourcés mesure par mesure |

## Utilisation des résultats

Les résultats publiés ici servent de base à des vidéos courtes et pédagogiques : séries par persona, séries par mesure. Chaque vidéo renvoie au scénario correspondant dans ce dépôt, pour que n'importe qui puisse vérifier ou relancer le calcul. La production vidéo n'est pas open source ; les chiffres, si.

## Code

Le premier squelette calcule l'avant/après d'un foyer pour un scénario d'exemple : le taux de la troisième tranche de l'impôt sur le revenu (30 % aujourd'hui). Ce paramètre sert à tester la chaîne de bout en bout ; ce n'est la mesure d'aucun programme.

| Fichier | Rôle |
|---|---|
| `src/simulator/engine.py` | Le moteur : un foyer et un scénario donnent les montants annuels avant et après, calculés avec OpenFisca-France sur la législation 2025 |
| `src/simulator/api.py` | L'API FastAPI : `POST /simulation`, ouverte à tous dans la limite de 10 calculs par minute et par adresse IP, documentée sur `/docs` |
| `tests/` | Tests du moteur et de l'API |
| `Dockerfile` | L'image déployée sur api.anthropolitics.fr |
| `.github/workflows/ci.yml` | Sur chaque PR, vérifie le lint et le formatage ruff, les types avec mypy, lance les tests, construit l'image Docker et vérifie qu'elle calcule. `main` n'accepte que des PR à jour aux tests verts ; chaque push sur `main` déclenche le déploiement par le webhook GitHub de Coolify |

Chaque résultat indique les versions de simulator et d'OpenFisca-France qui l'ont produit.

### Lancer en local

Il faut [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

```bash
uv run pytest
```

```bash
uv run ruff check
```

```bash
uv run ruff format
```

```bash
uv run mypy
```

```bash
uv run uvicorn simulator.api:app --reload
```

La documentation de l'API est alors sur http://localhost:8000/docs. Exemple d'appel :

```bash
curl -X POST http://localhost:8000/simulation -H 'Content-Type: application/json' \
  -d '{"persona": {"salaire_brut_mensuel": 6000}, "scenario": {"taux_troisieme_tranche_ir": 0.35}}'
```

## Contribuer

On cherche quelques personnes motivées, à temps partiel, sur l'un de ces chantiers :

- **Moteur (Python)** : intégration OpenFisca, modèle de personas, catalogue de mesures.
- **Économie et data** : sourcer les paramètres et les fourchettes. Un profil économiste est un vrai plus.
- **Relecture** : traquer les biais et les erreurs de traduction des programmes.

Pour signaler une erreur ou contester la traduction d'une mesure, ouvrez une issue avec la source qui appuie votre lecture.

## Licence

[AGPL-3.0](LICENSE), comme OpenFisca-France. Toute version modifiée mise en ligne doit publier son code.
