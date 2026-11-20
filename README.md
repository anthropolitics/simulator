# simulator

[![CI](https://github.com/anthropolitics/simulator/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/anthropolitics/simulator/actions/workflows/ci.yml?query=branch%3Amain)

Moteur de simulation open source qui calcule ce que chaque programme politique change, concrètement, pour des ménages français types.

> **Statut : en construction.** Un premier squelette calcule l'avant/après d'un foyer pour un scénario d'exemple ; la traduction des programmes arrive en phase 2.

## Pourquoi

Beaucoup d'électeurs votent sans savoir ce qu'une mesure changerait pour eux. Les chiffrages sérieux existent, mais ils restent illisibles pour le grand public et absents des réseaux sociaux, où se forme une bonne part des opinions.

Ce moteur rend ces chiffres calculables, vérifiables et rejouables, ménage par ménage, pour que chacun puisse voter en connaissance de cause, selon ses propres intérêts et critères. Il informe et chiffre ; il ne dit jamais pour qui voter.

## Ce que fait le moteur

Le moteur prend un **persona** et un **scénario**, et renvoie ce que le scénario change pour ce persona.

- **Persona** : un ménage type (composition, revenus, logement, territoire), calé sur les statistiques publiques de l'INSEE.
- **Scénario** : les mesures d'un programme, celles qui le financent comprises, traduites en paramètres documentés et sourcés.
- **Résultat** : un fichier JSON versionné, par exemple le revenu disponible annuel avant et après, détaillé en impôts, cotisations et prestations, et pour chaque salarié son âge de départ à la retraite au taux plein, sa pension et leur cumul sur l'espérance de vie. S'y ajoutent le bilan du foyer (entrées, sorties par usage, épargne), ce que le foyer verse aux administrations publiques, réparti par poste de dépense (charge de la dette comprise), ce qu'il en reçoit, et le budget du scénario : ce qu'il coûte ou rapporte aux finances publiques, et ce que le financer coûterait au foyer.

Exemple de lecture : « Sophie, infirmière à Lille, deux enfants. Programme A : + X €/an. Programme B : − Y €/an. Programme C : entre − Z et + W €/an, selon l'effet sur l'emploi. »

Le calcul sépare trois types d'effets :

| Effets | Exemples | Consensus | Présentation |
|---|---|---|---|
| Mécaniques | Barème de l'impôt, cotisations, prestations | Fort : c'est la loi appliquée | Une valeur |
| Budgétaires | Coût ou recette d'une mesure pour les finances publiques | Moyen : les chiffrages divergent | Une fourchette, du chiffrage le plus bas au plus haut, chacun avec sa source |
| Comportement et macro | Emploi, prix, croissance | Faible | Une fourchette sourcée, seulement quand elle change la conclusion |

## Financement et contreparties

Aucune mesure n'est gratuite, et aucune économie n'est sans effet. Chaque résultat porte donc, à côté de l'effet direct sur le foyer, le budget du scénario.

1. **Le coût.** Chaque mesure du catalogue porte ce qu'elle coûte ou rapporte par an aux finances publiques, en milliards d'euros, quand une source le chiffre : le candidat, un institut, une administration. Quand les chiffrages divergent, le coût est une fourchette. Le moteur ne recalcule pas ce coût : il faudrait les données fiscales de toute la population, qui ne sont pas publiques. Une mesure sans chiffrage est signalée « non chiffrée » et manque au total.
2. **Le financement du candidat.** Un impôt, une baisse de prestation ou une économie que le candidat annonce est une mesure du catalogue comme une autre : son effet sur le foyer entre dans le calcul, sa recette vient en déduction du coût. Un financement sans effet calculable sur un foyer (économies de fonctionnement, impôt sur les entreprises, lutte contre la fraude) compte pour sa recette seulement.
3. **Ce qui reste.** Le solde, coût moins recettes, est ce dont le déficit public se creuse ou se réduit. Pour dire ce qu'il pèse sur le foyer, le moteur le traduit en euros par an selon trois conventions, toujours données ensemble : s'il était financé par la seule TVA, par la seule CSG ou par le seul impôt sur le revenu, chaque taux relevé dans la même proportion. Un scénario qui rapporte plus qu'il ne coûte se lit dans l'autre sens : ce que le foyer gagnerait si l'excédent lui était rendu par cet impôt.

Exemple de lecture : « Julien, vendeur à Toulouse. Retraite à 62 ans : il part N mois plus tôt. La mesure coûte entre 9 Md€ par an, selon la candidate, et 38,5 Md€, selon l'Institut Montaigne. Financée par la TVA, elle lui coûterait entre A et B € par an ; par l'impôt sur le revenu, entre C et D €. Non financée, elle creuse le déficit d'autant. »

### Ce que le foyer verse et ce qu'il reçoit

Pour situer ces montants, chaque résultat donne aussi le compte du foyer avec les administrations publiques (État, Sécurité sociale, collectivités), avant et après le scénario.

- **Ce qu'il verse** : ses cotisations salariales, sa CSG, ses impôts directs et sa TVA. Ce total est réparti comme la dépense publique de 2024 (Insee) : sur 1 000 € versés, 415 € vont à la protection sociale (retraites, chômage, famille, solidarité), 156 € à la santé, 89 € à l'enseignement, 36 € aux intérêts de la dette, 32 € à la défense, et ainsi de suite.
- **Ce qu'il reçoit en argent** : ses pensions de retraite et ses prestations sociales.
- **Ce qu'il reçoit en nature** : l'école de ses enfants, à la dépense moyenne par élève du niveau de leur âge, de la maternelle à l'enseignement supérieur, pour la part que finance le public à ce niveau (DEPP : 94 % dans le premier degré, 89 % dans le second, 68 % dans le supérieur), et la santé de chacun, à la dépense publique moyenne par habitant (Insee) pondérée selon son âge comme les soins remboursés par l'assurance maladie (DREES) : un enfant compte pour 0,4 fois la moyenne, une personne de plus de 80 ans pour 3,1 fois.

C'est une convention de lecture : un euro versé finance chaque fonction selon son poids, quel que soit l'impôt. Les cotisations des employeurs et les taxes que le moteur ne calcule pas (carburants, tabac, taxe foncière) ne sont pas comptées dans ce qu'il verse.

### Le bilan du foyer

Chaque résultat donne enfin le bilan annuel du foyer, avant et après le scénario : ce qui entre, ce qui sort, et le solde, qui est son épargne.

- **Entrées** : salaires et retraites nets, prestations sociales.
- **Sorties** : impôts directs, logement et consommation par usage (alimentation, transports, santé, loisirs…).
  - **Combien le foyer dépense** vient de son propre revenu et du taux d'épargne que l'Insee mesure à son niveau de vie : 3 % du revenu chez les plus modestes, 28 % chez les plus aisés. C'est le principe du modèle Ines de l'Insee : la consommation suit le revenu du ménage, pas une dépense moyenne.
  - **Son logement** : un locataire paie son loyer, ou à défaut un loyer estimé d'après sa surface, sa zone (agglomération de Paris, grande agglomération, ailleurs) et son parc (privé ou social). Un propriétaire paie la taxe foncière et, s'il rembourse un emprunt, sa mensualité, ou à défaut la part de leurs revenus qu'y consacrent les accédants de son niveau de vie (enquêtes Logement de l'Insee). S'y ajoutent l'énergie et les charges.
  - **Comment le reste se répartit** vient de l'enquête Budget de famille de l'Insee : la répartition des ménages de son niveau de vie, déplacée selon son type de ménage (personne seule, famille monoparentale, couple avec ou sans enfants), l'âge de l'adulte le plus âgé, sa commune et son statut (locataire ou accédant, propriétaire sans emprunt).
- **Le scénario** garde les mêmes achats : seuls changent les revenus, les impôts et, quand une mesure touche la TVA, le prix de ces achats.

Ces dépenses sont celles de ménages comparables, pas celles du foyer : le solde donne un ordre de grandeur, qui vaut ce que valent les taux d'épargne de l'Insee, mesurés en 2017 par cinquième de niveau de vie. Pour la répartition entre postes, l'enquête ne publie chaque dimension que séparément ; le moteur les combine comme si elles jouaient indépendamment, ce qui force le trait pour les profils où elles vont ensemble (jeune, seul, locataire, en ville). Sans loyer saisi, un foyer est tenu pour propriétaire.

Ces trois conventions de financement ne sont le programme d'aucun candidat : elles donnent un ordre de grandeur, à assiettes fixes, et le moteur n'en choisit aucune. Les effets en retour sur l'emploi, les prix ou la croissance, qui changent le coût lui-même, restent des fourchettes sourcées.

## Projection dans le temps

Le moteur peut aussi répondre pour le même foyer dans un an, dans dix ans : le foyer est vieilli, puis simulé comme aujourd'hui. Tout reste en euros d'aujourd'hui.

- **Ce qui bouge** : chacun vieillit ; un enfant quitte le foyer à 21 ans ; les salaires montent plus vite que les prix, au rythme de la productivité du scénario de référence du Conseil d'orientation des retraites (0,7 % par an, 0,4 % et 1,0 % dans ses variantes) ; un salarié qui atteint l'âge de son départ au taux plein touche sa pension à la place de son salaire.
- **Ce qui ne bouge pas** : la législation, dont les barèmes suivent les prix ; le SMIC, les pensions et le loyer, qui suivent les prix aussi ; l'emploi, la composition du couple, le logement.
- **Ce que cela montre** : un impôt qui pèse plus quand le salaire monte plus vite que le barème, des allocations qui s'éteignent quand les enfants grandissent, et surtout l'effet d'une mesure sur les retraites, qui ne change rien aux revenus d'aujourd'hui mais décide de qui travaille encore à l'horizon.

Ce n'est pas une prévision : ni promotion, ni chômage, ni naissance, ni décès. La fourchette vient des variantes de productivité ; les effets d'une mesure sur l'emploi ou les prix n'y sont pas.

## Principes non négociables

Le moteur ne vaut que s'il reste crédible pour tous les bords.

1. **Tout est sourcé.** Chaque paramètre cite sa source : texte de loi, INSEE ou littérature économique. Un paramètre sans source n'est pas fusionné.
2. **Les incertitudes sont visibles.** Effets mécaniques et effets de comportement restent séparés ; les seconds sont donnés en fourchettes.
3. **La traduction des programmes est publique.** Chaque mesure devient des paramètres documentés dans ce dépôt, contestables par issue, y compris par les partis.
4. **Aucune consigne de vote.** Le moteur produit des effets, jamais un classement des programmes ni un « bon » choix.
5. **Tout est reproductible.** Chaque résultat publié renvoie à la version du code, des paramètres et du scénario qui l'a produit.
6. **Aucune mesure sans sa contrepartie.** Chaque résultat donne le coût ou la recette pour les finances publiques, avec sa source, ou dit qu'il n'est pas chiffré. Quand le candidat ne dit pas qui paie, le moteur ne le décide pas à sa place : il montre plusieurs financements possibles.

## Périmètre du MVP (présidentielle 2027)

Objectif : un moteur crédible sur un périmètre réduit, en ligne avant le premier tour (avril 2027).

Dans le MVP :

- effets mécaniques via OpenFisca-France : impôts, cotisations, prestations ;
- une dizaine de mesures phares par programme, pour les principaux candidats ;
- 5 à 8 personas ménages types ;
- le coût sourcé de chaque mesure et ses contreparties pour le foyer ;
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

Le moteur calcule l'avant/après d'un ménage type pour un scénario : une ou plusieurs mesures du catalogue, appliquées à la législation 2025 « comme si elles s'appliquaient aujourd'hui ». Le taux de la troisième tranche de l'impôt sur le revenu reste réglable à part, pour tester la chaîne ; ce n'est la mesure d'aucun programme.

| Fichier | Rôle |
|---|---|
| `src/simulator/engine.py` | Le moteur : un persona et un scénario donnent les montants annuels avant et après, détaillés par dispositif, calculés avec OpenFisca-France sur la législation 2025, et le budget du scénario : son coût, les mesures non chiffrées et ce que le financer coûterait au foyer par la TVA, la CSG ou l'impôt sur le revenu, d'après les recettes 2025 de chaque impôt (Insee) ; pour chaque législation, ce que le foyer verse aux administrations publiques, réparti par fonction de dépense (Insee, 2024), ce qu'il en reçoit en argent et en nature (école, santé), et son bilan : entrées, sorties par usage, épargne |
| `src/simulator/persona.py` | Le foyer dans quelques années, pour la projection : âges, départ des enfants, salaires, passage à la retraite. Le ménage type : adultes (âge, salaire, retraite, nationalité, début de carrière…), enfants, loyer et commune, ou pour un locataire sans loyer connu sa surface et son parc (privé ou social), emprunt d'un propriétaire accédant, patrimoine, dépenses de consommation |
| `src/simulator/logement.py` | Ce que le logement coûte à un foyer qui ne le dit pas. Le remboursement d'emprunt et la taxe foncière d'un propriétaire, en part de ses revenus selon son niveau de vie (enquête Logement 2023-2024). Le loyer d'un locataire, estimé d'après sa commune, sa surface et son foyer : loyer au mètre carré par zone et par parc, surface moyenne par type de ménage (enquêtes Logement 2013, 2020 et 2023-2024, indice de référence des loyers) |
| `src/simulator/consommation.py` | Les dépenses de consommation d'un ménage, imputées quand le persona ne les donne pas : leur total suit le revenu du foyer et le taux d'épargne des ménages de son niveau de vie (Insee, comptes par catégorie de ménages, déciles de 2024), leur répartition suit son profil (type de ménage, âge, commune, statut d'occupation) d'après l'enquête Budget de famille 2017 de l'Insee, portée aux prix de 2025 : l'énergie poste par poste, le reste regroupé par taux de TVA selon une table qui donne le taux de chaque code de l'enquête, et par usage pour le bilan du foyer. Elles servent aux mesures de TVA, avec une répercussion intégrale des taux sur les prix, et restent fixes d'un scénario à l'autre |
| `src/simulator/retraites.py` | La retraite de chaque adulte salarié, calculée hors d'OpenFisca par un moteur simplifié (régime général et Agirc-Arrco, carrière au salaire actuel) : âge de départ au taux plein, pension mensuelle brute et cumul sur l'espérance de vie, selon la loi actuelle et selon le scénario |
| `src/simulator/menages.py` | Les six ménages types, calés sur les statistiques de l'Insee, chaque valeur avec sa source |
| `src/simulator/tableau.py` | Le tableau publié sur le site : ce que le programme de chaque candidat (ses mesures du catalogue) change pour chaque ménage type |
| `src/simulator/mesures/` | Le catalogue : un fichier par mesure, avec sa source, la citation exacte, sa traduction en paramètres, les effets que le calcul laisse de côté et, quand une source le chiffre, son coût pour les finances publiques. Une mesure qui ne s'appuie encore que sur une source secondaire est marquée « à confirmer » |
| `src/simulator/api.py` | L'API FastAPI : `POST /simulation` (aujourd'hui ou à un horizon de 1 à 40 ans), `POST /programmes` (les treize programmes pour un foyer saisi, une ligne JSON par candidat), `GET /mesures` et `GET /menages`, ouverte à tous dans la limite de 10 calculs par minute et par adresse IP, documentée sur `/docs` |
| `tests/` | Tests du moteur, de l'API et de chaque mesure |
| `Dockerfile` | L'image déployée sur api.anthropolitics.fr |
| `.github/workflows/ci.yml` | Sur chaque PR et sur `main`, vérifie le lint et le formatage ruff, les types avec mypy, lance les tests avec au moins 90 % de couverture, construit l'image Docker et vérifie qu'elle calcule. `main` n'accepte que des PR à jour aux tests verts ; chaque push sur `main` déclenche le déploiement par le webhook GitHub de Coolify |

Chaque résultat indique les versions de simulator et d'OpenFisca-France qui l'ont produit.

### Lancer en local

Il faut [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

```bash
uv run pytest --cov
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

La documentation de l'API est alors sur http://localhost:8000/docs et le catalogue des mesures sur http://localhost:8000/mesures. Exemple d'appel :

```bash
curl -X POST http://localhost:8000/simulation -H 'Content-Type: application/json' \
  -d '{"persona": {"adultes": [{"au_smic": true}], "enfants": [4], "loyer_mensuel": 650, "code_commune": "69123"}, "scenario": {"mesures": ["smic_1600_net"]}}'
```

## Contribuer

On cherche quelques personnes motivées, à temps partiel, sur l'un de ces chantiers :

- **Moteur (Python)** : intégration OpenFisca, modèle de personas, catalogue de mesures.
- **Économie et data** : sourcer les paramètres et les fourchettes. Un profil économiste est un vrai plus.
- **Relecture** : traquer les biais et les erreurs de traduction des programmes.

Pour signaler une erreur ou contester la traduction d'une mesure, ouvrez une issue avec la source qui appuie votre lecture.

## Licence

[AGPL-3.0](LICENSE), comme OpenFisca-France. Toute version modifiée mise en ligne doit publier son code.
