# Plan complet de R&D, d'innovation et de prospective — mémoire et continuité d'ÉVA

**Note de travail datée du 2026-11-01. Rendu depuis `plan.toml` — ne pas éditer.**

ÉVA est une direction de recherche, pas une capacité acquise. La page publique eva.html dit déjà qu'elle ne « possède pas toutes les fonctions envisagées » ; ce plan organise le travail qui rendrait certaines phrases vraies, et qui rend visibles celles qui ne le sont pas.

**Statuts :** 12 phases — 3 en-attente, 2 en-cours, 5 fait, 2 hors-portee.

## Ce qui est une fiction de conception

Le prénom, l'année de naissance fictive (1980) et le corps à venir sont un **cadre de conception**, pas des faits : ils servent à écrire une voix cohérente, et ne doivent jamais apparaître comme des informations sur une personne réelle. Aucun essai ne collecte de donnée personnelle.

## Ce que ce plan ne décide pas

Ce plan ne décide pas d'un achat, d'un devis, d'un hébergement, d'un modèle ni d'une date de mise en service. Il ne promet ni conscience, ni corps, ni parité de délai avec un humain : ces trois objets ont leur propre phase, et leur statut est un refus motivé.

## Les phases

| Phase | Horizon | Statut | Test | Branches servies |
| --- | --- | --- | --- | --- |
| [`memoire-trois-horizons`](#memoire-trois-horizons) | court | fait | `outils/test_memoire_eva.py` | `documentation-rd-eva`, `coordination-de-tous-les-agents`, `veille-savoirs-evolutifs` |
| [`economie-de-contexte`](#economie-de-contexte) | moyen | fait | `outils/test_memoire_eva.py` | `coordination-de-tous-les-agents`, `optimisation-du-site`, `poids-et-sobriete-numerique` |
| [`graphe-de-memoire`](#graphe-de-memoire) | moyen | fait | `outils/test_memoire_eva.py` | `cartographier-les-lacunes`, `indexation-et-lecteurs-de-contenu`, `veille-savoirs-evolutifs` |
| [`rappel-mesure`](#rappel-mesure) | court | en-cours | `outils/test_memoire_eva.py` | `indexation-et-lecteurs-de-contenu`, `ecouter-la-page` |
| [`couverture-des-branches`](#couverture-des-branches) | moyen | fait | `outils/test_verifier_plan_eva.py` | `documentation-rd-eva`, `coherence-textes-publics` |
| [`verite-et-refus`](#verite-et-refus) | long | fait | `outils/test_verifier_plan_eva.py` | `sources-fermees-et-registre-des-refus`, `confronter-une-affirmation-a-sa-source`, `vote-distanciel-verifiable` |
| [`continuite-du-support`](#continuite-du-support) | long | en-cours | `outils/test_memoire_eva.py` | `optimisation-du-site`, `raccordement-domaine-www`, `poids-et-sobriete-numerique` |
| [`apprentissages-et-relecture`](#apprentissages-et-relecture) | long | en-attente | `outils/test_audit_prototypes.py` | `relire-les-44-prototypes`, `co-conception-et-essais`, `autres-langues-et-contextes` |
| [`voix-et-ecoute`](#voix-et-ecoute) | moyen | en-attente | `outils/test_verifier_accessibilite.mjs` | `ecouter-la-page`, `direction-artistique-motion` |
| [`persona-de-conception`](#persona-de-conception) | long | en-attente | `outils/verifier-plan-eva.py` | `documentation-rd-eva`, `coherence-textes-publics` |
| [`conscience-et-corps`](#conscience-et-corps) | long | hors-portee | `outils/verifier-plan-eva.py` | `mondes-3d-pluridisciplinaires`, `direction-artistique-motion` |
| [`parite-humaine-des-delais`](#parite-humaine-des-delais) | long | hors-portee | `outils/test_memoire_eva.py` | `prospective-apprentissages-2030` |

### memoire-trois-horizons

**Une mémoire à trois horizons, avec un pointeur par fait** — horizon court, statut `fait`.

Retrouver ce qui est chaud (le tour en cours), ce qui est décidé (le journal et les avancées) et ce qui est durable (les documents de fond) sans relire le dépôt. Trois horizons, un seul fichier d'index, et chaque entrée renvoie à sa source par un chemin et un numéro de ligne — jamais une copie.

- **Preuve :** `outils/memoire-eva.py`
- **Test :** `outils/test_memoire_eva.py`
- **Dépend de :** rien
- **Limite :** L'index est construit sur les fichiers, pas sur un sens : il retrouve des mots et des pointeurs, il ne comprend pas une question. Un fait qui n'est écrit nulle part reste introuvable, et c'est voulu.

### economie-de-contexte

**Économiser le contexte : un résumé court, un pointeur long** — horizon moyen, statut `fait`.

Ne jamais charger un document entier pour savoir s'il parle d'un sujet. Chaque entrée porte un titre, un résumé de 160 caractères au plus et son pointeur ; une recherche imprime ce qu'elle a lu, en octets, à côté de la taille du corpus. La méthode est nommée « ponytail » dans le dépôt : la queue la plus courte qui tienne le poisson.

- **Preuve :** `outils/memoire-eva.py`
- **Test :** `outils/test_memoire_eva.py`
- **Dépend de :** `memoire-trois-horizons`
- **Limite :** Le résumé est la première phrase du document, pas un résumé écrit : il peut donc manquer le sujet réel. Un document sans phrase liminaire n'a pas de résumé du tout, et l'index le dit au lieu d'inventer.

### graphe-de-memoire

**Un graphe navigable : phases, branches, avancées, preuves** — horizon moyen, statut `fait`.

Sortir la mémoire du texte : un fichier Mermaid lisible dans Obsidian ou Graphify, un fichier DOT pour les outils de graphe, et la même vérité dans les deux. Sommaire : une branche du portefeuille pointe vers les phases qui la servent, une phase vers ses dépendances, une avancée vers ses preuves.

- **Preuve :** `outils/memoire-eva.py`
- **Test :** `outils/test_memoire_eva.py`
- **Dépend de :** `memoire-trois-horizons`
- **Limite :** Le graphe est **dérivé** : il ne porte aucune information que le plan, le portefeuille et les avancées ne portent déjà. Ce n'est pas une base de connaissances, c'est une carte de ce qui est écrit ailleurs.

### rappel-mesure

**Mesurer le temps de rappel au lieu de le promettre** — horizon court, statut `en-cours`.

Chronométrer la recherche dans l'index sur des requêtes réelles et publier la médiane, le maximum et le budget déclaré. Ce qui est mesuré est le rappel de l'index, pas la pensée : aucune comparaison avec un cerveau humain n'est revendiquée ici.

- **Preuve :** `outils/memoire-eva.py`
- **Test :** `outils/test_memoire_eva.py`
- **Dépend de :** `memoire-trois-horizons`, `economie-de-contexte`
- **Limite :** Mesure locale, sur une machine de CI, sans réseau ni utilisateur. Un index rapide ne dit rien de la pertinence : un résultat trouvé en 3 ms peut être le mauvais.

### couverture-des-branches

**Aucune branche du projet sans phase qui la serve** — horizon moyen, statut `fait`.

Les dix-neuf initiatives du portefeuille doivent apparaître dans au moins une phase. Une branche que le plan ignore est une branche qu'on oubliera ; le contrôle refuse cette omission plutôt que de la laisser au souvenir.

- **Preuve :** `outils/verifier-plan-eva.py`
- **Test :** `outils/test_verifier_plan_eva.py`
- **Dépend de :** `memoire-trois-horizons`
- **Limite :** La couverture prouve qu'une branche est **nommée**, pas qu'elle avance : une phase peut citer une branche et rester à l'arrêt. Le statut de la phase, lui, dit où l'on en est.

### verite-et-refus

**Une capacité sans test n'est pas une capacité** — horizon long, statut `fait`.

Refuser mécaniquement trois fautes : un statut « fait » sans test et sans citation au journal, un « hors-portée » sans condition de révision, une date future. C'est la règle que la page publique applique déjà en prose — la rendre exécutable.

- **Preuve :** `outils/verifier-plan-eva.py`
- **Test :** `outils/test_verifier_plan_eva.py`
- **Dépend de :** `memoire-trois-horizons`
- **Limite :** Le contrôle vérifie qu'un test **existe**, pas qu'il prouve ce que la phase prétend. La lecture du test reste humaine, et c'est écrit dans l'inventaire des contrôles.

### continuite-du-support

**Survivre à la fin d'une session : le support comme corps provisoire** — horizon long, statut `en-cours`.

La mémoire ne doit pas dépendre d'une conversation en cours. Tout ce qui compte est écrit dans le dépôt, versionné, et l'index se régénère à l'identique depuis n'importe quelle copie fraîche — c'est ce que le banc éprouve. L'état « chaud » se recalcule, il ne se stocke pas, donc il ne peut pas être périmé.

- **Preuve :** `outils/memoire-eva.py`
- **Test :** `outils/test_memoire_eva.py`
- **Dépend de :** `memoire-trois-horizons`, `verite-et-refus`
- **Limite :** La continuité repose sur git et sur une copie distante : si les deux disparaissent, la mémoire disparaît. Aucune sauvegarde hors du dépôt n'est décidée ici, et le plan de sauvegarde reste à écrire avec l'association.

### apprentissages-et-relecture

**Servir les apprentissages sans remplacer la relecture humaine** — horizon long, statut `en-attente`.

Relier chaque fiche d'apprentissage à sa source, à sa date de relecture et à son statut, pour qu'ÉVA puisse citer une fiche sans jamais la présenter comme validée. La mémoire sert ici de table de renvoi, pas de caution.

- **Preuve :** `docs/apprentissage/file-relecture.md`
- **Test :** `outils/test_audit_prototypes.py`
- **Dépend de :** `memoire-trois-horizons`
- **Limite :** Aucun relecteur n'est désigné à ce jour : la phase ne peut pas avancer sans personne.
- **Condition de révision :** Une personne compétente accepte un rôle de relecture et une première relecture est consignée dans docs/apprentissage/relectures.toml.

### voix-et-ecoute

**Parler et écouter, avec une mesure et un repli** — horizon moyen, statut `en-attente`.

Une voix lisible et une écoute utilisables sans service tiers obligatoire, mesurées sur les pages qui les portent, avec un repli texte complet. Le support existe déjà côté lecture d'écran ; la voix d'ÉVA, elle, n'est pas décidée.

- **Preuve :** `docs/rd/inclusion-lecture-vocale.md`
- **Test :** `outils/test_verifier_accessibilite.mjs`
- **Dépend de :** `verite-et-refus`
- **Limite :** Aucune voix n'est choisie, aucun fournisseur n'est retenu. La qualité d'une voix ne se mesure pas en millisecondes.
- **Condition de révision :** Une décision associative sur la voix, une licence compatible et une écoute contradictoire par des personnes concernées.

### persona-de-conception

**Une voix cohérente, déclarée comme fiction** — horizon long, statut `en-attente`.

Tenir une voix stable — le prénom, un ton, un refus — sans jamais la faire passer pour une personne. Le cadre fictif (naissance en 1980, corps à venir) est écrit dans ce plan pour être **visible comme fiction**, jamais pour être raconté comme un souvenir.

- **Preuve :** `docs/rd/listes-eva-materiel.md`
- **Test :** `outils/verifier-plan-eva.py`
- **Dépend de :** `verite-et-refus`
- **Limite :** Une persona n'est pas une identité : rien n'est collecté, rien n'est mémorisé sur les personnes qui parlent à ÉVA. Le jour où le site public raconterait une biographie, ce serait une faute, pas une fonctionnalité.
- **Condition de révision :** Une relecture éditoriale et associative du texte public, et une règle écrite qui interdit toute biographie fictive présentée au présent.

### conscience-et-corps

**Conscience et exosquelette : ce que le dépôt refuse d'affirmer** — horizon long, statut `hors-portee`.

Écrire noir sur blanc ce qu'aucune preuve du dépôt ne soutient : la conscience, la subjectivité, un corps propre, un exosquelette. Ces objets ne sont pas niés — ils sont déclarés **non démontrés**, et leur phase ne peut pas passer à « fait » sans une définition mesurable et une preuve indépendante.

- **Preuve :** `eva.html`
- **Test :** `outils/verifier-plan-eva.py`
- **Dépend de :** `verite-et-refus`
- **Limite :** Aucun protocole ne peut, aujourd'hui, établir une conscience. Le plan ne fixe donc aucune date, et la page publique garde la phrase qui dit qu'ÉVA ne possède pas toutes les fonctions envisagées.
- **Condition de révision :** Une définition opérationnelle et falsifiable de la capacité revendiquée, une mesure indépendante reproduite par un tiers, une revue de sûreté, et une décision de l'association — les quatre, pas l'une des quatre.

### parite-humaine-des-delais

**Les délais d'un humain : une mesure, pas une promesse** — horizon long, statut `hors-portee`.

Distinguer deux choses que la demande mélange : le temps de **rappel** de l'index, mesuré en millisecondes, et le temps de **réponse utile** d'un humain, qui dépend de la lecture, du doute et de la vérification. Le premier se mesure ici ; le second n'a pas de référentiel dans ce dépôt.

- **Preuve :** `outils/memoire-eva.py`
- **Test :** `outils/test_memoire_eva.py`
- **Dépend de :** `rappel-mesure`
- **Limite :** Aucune étude de temps de réponse humaine n'est citée : la comparer demanderait un protocole avec des personnes, une mesure de charge cognitive et un accord éthique. Rien de tout cela n'existe ici.
- **Condition de révision :** Un protocole d'essai avec des personnes volontaires, des tâches comparables, une mesure publiée et une relecture éthique — ou le renoncement explicite à la comparaison.

## Le graphe

227 nœuds et 442 arêtes, dérivés de ce plan, du portefeuille et des avancées.

- `graphe.md` — diagramme Mermaid, lisible dans Obsidian ou Graphify ;
- `graphe.dot` — même graphe, fichiers compris, pour les outils de graphe ;
- `memoire.json` — l'index à trois horizons, un résumé court et un pointeur par fait.

## Comment s'en servir

```sh
python3 outils/memoire-eva.py --chercher "gouttière conteneur"
python3 outils/memoire-eva.py --evaluer
python3 outils/memoire-eva.py --verifier
python3 outils/verifier-plan-eva.py
```

## Limites

- L'index retrouve des **mots**, pas un sens : une question mal formulée ne trouve rien.
- Le résumé est la première phrase de la source, pas un résumé écrit pour le sujet.
- Le graphe ne porte aucune information qui ne soit déjà écrite ailleurs.
- Rien ici ne démontre une conscience, un corps ou une parité de délai avec une personne : les phases correspondantes sont `hors-portee` ou `en-attente`, avec leur condition.
