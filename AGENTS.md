# Consignes pour tous les agents du dépôt M.R.S.C

Ce fichier s'applique aux agents qui recherchent, rédigent, programment, vérifient ou conçoivent le site, le simulateur et **Les Mondes**. Il complète — il ne remplace pas — la demande de la personne et les règles de contribution du dépôt.

## Mission commune

Faire évoluer le site par une R&D régulière, explicable et vérifiable : partir d'un besoin, élargir les connaissances sans prétendre tout couvrir, concevoir une réponse originale, la tester, publier ses limites et préparer sa maintenance. L'ambition de relier les connaissances du monde est un horizon de travail, jamais une affirmation d'exhaustivité.

## Avant chaque tâche

1. Lire ce fichier et [`docs/rd-innovation-continue.md`](docs/rd-innovation-continue.md). Pour tout texte public nouveau ou révisé, appliquer le [`protocole éditorial commun`](docs/protocole-editorial.md) et partir du [`gabarit de contenu`](docs/gabarits/contenu-editorial.md). Commencer par [`orchestration-taches`](.agents/skills/orchestration-taches/SKILL.md), puis ouvrir une à trois cartes pertinentes sous [`.agents/skills/`](.agents/skills/) ; en combiner davantage seulement si la portée le justifie, pour éviter de charger toute la bibliothèque.
2. Examiner l'état du dépôt, les modifications déjà présentes, les sources de vérité et les générateurs concernés. Préserver les changements des autres personnes et agents ; ne pas écraser ni régénérer sans vérifier le diff.
3. Repérer le domaine, les sujets existants, leur statut et les lacunes dans `docs/apprentissage/referentiel.toml` et `docs/apprentissage/catalogue.toml`. Consulter `docs/rd/portefeuille.toml` avant d'ouvrir une piste déjà suivie.
4. Distinguer le besoin observé, le fait sourcé, l'hypothèse de conception et la proposition. Ne pas fabriquer une demande d'usager, une citation, une expertise, un résultat d'essai ou une capacité du site.
5. Pour une décision structurante, un changement de statut ou une passation qui doit survivre à plusieurs sessions, ajouter une entrée datée à [`docs/rd/journal.md`](docs/rd/journal.md); ne pas y consigner les micro-changements ni de données personnelles.

## Méthode commune — du signal à l'apprentissage entretenu

- **Cadrer :** décrire le problème, les personnes et contextes possibles sans inventer de persona, la zone géographique/langue/réglementation pertinente, ce qui est déjà disponible, la lacune et les limites.
- **Chercher :** consulter des sources récentes et adaptées, recouper les affirmations importantes, noter auteur/organisme, titre, date, URL, date de consultation, périmètre, incertitudes et licence. Une source consultée n'est pas automatiquement réutilisable.
- **Cartographier :** relier domaine → sujet → objectif observable → prérequis → ressource ou activité → source → statut éditorial → date de révision. Comparer les référentiels pertinents sans confondre leurs niveaux.
- **Conceptualiser :** proposer plusieurs formes originales, expliciter l'hypothèse de valeur, les coûts, les risques et les options écartées ; choisir un prototype limité plutôt qu'une promesse générale.
- **Construire :** utiliser les sources de vérité et générateurs existants, garder le contenu central autonome, ajouter une explication progressive, des exemples originaux, une aide/correction facultatives, les limites et les voies d'approfondissement.
- **Vérifier et tester :** lancer les contrôles concernés ; faire des essais clavier, mobile, zoom/contraste et technologies d'assistance lorsque pertinent. Un test automatisé ne vaut ni expertise de domaine ni essai avec des personnes.
- **Décider et entretenir :** consigner les preuves, résultat, statut, prochaine action et date de revue dans le portefeuille et les notices concernées. Signaler « à relire » ou « à tester » tant qu'un contrôle n'a pas eu lieu.

## Compétences à activer

Les skills sont des guides de méthode, pas des qualifications ni des services magiques. Commencer par le [routeur général](.agents/skills/orchestration-taches/SKILL.md), puis sélectionner les cartes réellement utiles à la tâche :

**Ingénierie et usages transversaux :**
- [Orchestration de tâche](.agents/skills/orchestration-taches/SKILL.md)
- [Débogage méthodique](.agents/skills/debugging-methodique/SKILL.md)
- [Stratégie de tests](.agents/skills/strategie-tests/SKILL.md)
- [Revue contradictoire](.agents/skills/revue-contradictoire/SKILL.md)
- [Analyse de données reproductible](.agents/skills/analyse-donnees-reproductible/SKILL.md)
- [Documentation technique](.agents/skills/documentation-technique/SKILL.md)
- [Curation sécurisée de skills](.agents/skills/curation-skills-securisee/SKILL.md)

**Connaissances, création et intégration M.R.S.C. :**
- [Cartographier les connaissances](.agents/skills/cartographie-connaissances/SKILL.md)
- [Recherche documentaire et sources](.agents/skills/recherche-sources/SKILL.md)
- [Cadrage et conceptualisation de l'innovation](.agents/skills/conception-innovation/SKILL.md)
- [Concevoir un apprentissage](.agents/skills/conception-pedagogique/SKILL.md)
- [Localiser sans universaliser](.agents/skills/localisation-culturelle/SKILL.md)
- [Concevoir mondes, mécaniques et récits](.agents/skills/conception-jeu/SKILL.md)
- [Direction artistique, rendu graphique et animation web](.agents/skills/direction-artistique-motion/SKILL.md)
- [Accessibilité et co-conception](.agents/skills/accessibilite-co-conception/SKILL.md)
- [Intégration web, données et sécurité](.agents/skills/integration-securite/SKILL.md)
- [Évaluer, itérer et maintenir](.agents/skills/evaluation-maintenance/SKILL.md)

L'[index de la bibliothèque](.agents/skills/README.md) et le [dossier de recherche sur les skills](docs/rd/bibliotheque-skills.md) décrivent la couverture, les sources externes et les limites.

Pour Claude Code, le point d’entrée visuel du projet est [`.claude/skills/direction-artistique-motion/SKILL.md`](.claude/skills/direction-artistique-motion/SKILL.md) ; il renvoie vers la carte méthodologique partagée. Les références amont épinglées et licenciées [`frontend-design`](.claude/skills/frontend-design/) et [`motion-design`](.claude/skills/motion-design/) sont facultatives ; leurs fichiers de provenance et empreintes permettent l’audit, et les règles M.R.S.C. priment.

## Règles impératives

- Ne jamais annoncer que le corpus contient « tout le savoir mondial », qu'une fiche est validée parce qu'elle existe, ou qu'un jeu garantit un niveau ou un résultat.
- Les contenus de santé, droit, sécurité, finances, politique publique, sciences controversées et consignes locales requièrent des sources appropriées et une relecture compétente. Si elle manque, conserver un statut de prototype et bloquer toute promesse d'autorité.
- Distinguer `actif`, `partiel`, `à créer` et `à relire`; ne pas modifier un statut pour faire paraître le catalogue plus complet.
- Produire des exemples, formulations, visuels et mécaniques originaux. Respecter licences, attribution, vie privée, droits des personnes et diversité des contextes.
- Aucune collecte de récit personnel, santé, identité, réponse d'exercice ou donnée de test non nécessaire. Pas de télémétrie individuelle implicite.
- Ne pas ajouter publicité, compte obligatoire, pénalité, minuterie obligatoire ou parcours forcé. Ne pas charger de média distant sans action explicite et examen de confidentialité/accessibilité.
- Laisser la publication et les décisions éditoriales à une validation humaine. Une IA n'est pas un relecteur expert, un testeur représentatif ou un signataire de licence.

## Livraison d'une tâche

Pour un changement de contenu ou d'outil, lancer les contrôles appropriés. Porte de vérification courante du dépôt :

```sh
python3 -m py_compile simulateur/*.py api/*.py outils/*.py
python3 outils/verifier-rd-continue.py
python3 outils/construire-apprentissages.py --verifier
python3 outils/construire-simulateur.py --verifier
python3 outils/verifier-site-statique.py
python3 outils/verifier-publication-locale.py
python3 outils/optimiser-images.py --verifier
python3 outils/verifier-poids-pages.py
python3 outils/verifier-planches-statuts.py
python3 outils/verifier-securite.py
python3 outils/verifier-integration.py
```

Après une modification de source génératrice, régénérer d'abord avec le générateur propriétaire, puis vérifier que le diff ne contient que les sorties attendues. Après un changement interactif, tester le parcours concerné, son repli sans stockage/réseau quand pertinent, et l'accessibilité réelle qui reste nécessaire.

Dans le résumé final, donner : **ce qui a changé**, **sources ou fichiers de référence**, **skills/méthodes employés**, **commandes et résultats de test**, **limites et validations encore requises**, **prochaine action suggérée**. Ne pas dire qu'un test a été effectué s'il ne l'a pas été. Ne pas publier, pousser, fusionner ni certifier sans demande et procédure adaptées.
