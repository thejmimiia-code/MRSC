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

## Fusionner et importer sans perte

Une fusion ou une suppression de branche ne doit laisser ni contenu perdu, ni erreur ouverte.

- **Avant de fusionner :** lancer la porte de vérification sur la branche fusionnée, pas seulement sur la branche source. Un conflit se résout en comparant les deux versions, jamais en gardant un seul côté sans avoir lu l'autre.
- **Avant d'importer un travail venu d'ailleurs :** vérifier qu'il n'écrase pas un travail plus récent. Comparer avec `git diff <ref> main` et lire chaque ligne que le passage à `main` supprimerait.
- **Avant de supprimer une branche :** `python3 outils/verifier-fusions.py --branches` doit répondre « supprimable sans perte » pour cette branche. Critère : tous ses blobs restent atteignables depuis les autres références (main, étiquettes).
- **Après une fusion :** constater que les workflows de `main` sont verts (vérification, publication, en-têtes, veille) avant de passer à autre chose ; une publication qui échoue est une erreur laissée ouverte.
- **Après une résolution de conflit :** vérifier l'ordre du journal de R&D, l'absence de marqueurs de conflit et de fichiers `.orig`/`.rej` ; la porte les contrôle désormais.
- **Aucun chiffre en prose sans contrôle :** un total annoncé sur une page publique (« 82 fiches », « 97 pages du dépôt ») est recalculé depuis `docs/apprentissage/catalogue.toml`, `referentiel.toml` et l'arbre réel par `verifier-integration.py` ; on ne recopie jamais un compte à la main.
- **Aucune ressource orpheline :** un fichier de `assets/` publié mais cité par aucune page, aucun script ni aucun style est soit cité, soit retiré (et archivé s'il est distinct). `verifier-integration.py` le refuse désormais.

`outils/verifier-fusions.py` vérifie hors ligne : aucune fusion en cours, aucun fichier non fusionné dans l'index, aucun marqueur de conflit, aucune sauvegarde de fusion suivie, journal antichronologique et sans titre en double. Avec `--branches`, il audite les branches distantes et refuse de déclarer supprimable une branche qui porte un contenu unique.

## Règles impératives

- Ne jamais annoncer que le corpus contient « tout le savoir mondial », qu'une fiche est validée parce qu'elle existe, ou qu'un jeu garantit un niveau ou un résultat.
- Les contenus de santé, droit, sécurité, finances, politique publique, sciences controversées et consignes locales requièrent des sources appropriées et une relecture compétente. Si elle manque, conserver un statut de prototype et bloquer toute promesse d'autorité.
- Distinguer `actif`, `partiel`, `à créer` et `à relire`; ne pas modifier un statut pour faire paraître le catalogue plus complet.
- Produire des exemples, formulations, visuels et mécaniques originaux. Respecter licences, attribution, vie privée, droits des personnes et diversité des contextes.
- Aucune collecte de récit personnel, santé, identité, réponse d'exercice ou donnée de test non nécessaire. Pas de télémétrie individuelle implicite.
- Ne pas ajouter publicité, compte obligatoire, pénalité, minuterie obligatoire ou parcours forcé. Ne pas charger de média distant sans action explicite et examen de confidentialité/accessibilité.
- Laisser la publication et les décisions éditoriales à une validation humaine. Une IA n'est pas un relecteur expert, un testeur représentatif ou un signataire de licence.
- **Automatiser tout ce qui est mécanique, jamais ce qui demande un jugement.** `outils/auditer-prototypes.py` exécute 17 contrôles objectifs par fiche (champs, HTTPS et métadonnées de droits, dates, doublons, longueur des phrases, typographie, page générée, existence d'une page de source précise) et publie `docs/apprentissage/audit-automatique.md`. Un audit vert ne vaut **ni relecture ni validation** : il dit seulement qu'aucun défaut mécaniquement détectable ne subsiste. Ne jamais présenter ce vert comme une approbation.
- **Un constat n'est pas un défaut.** Trois états existent : `ok`, `à corriger` (le fait est faux et réparable sans jugement) et `constat` (la machine voit un fait exact qu'elle ne peut pas juger — par exemple une fiche qui ne cite qu'un portail, donc sans page à confronter). Un constat se nomme dans l'audit et dans la page publique ; il ne se présente jamais comme une faute, et il ne s'efface pas tout seul : une personne doit soit ajouter une page précise réellement consultée, soit assumer le portail par écrit dans la fiche.
- **Consigner une avancée, pas seulement une décision.** `docs/rd/avancees.toml` retient ce qu'un lot a appris de durable ; `outils/construire-avancees.py` produit `docs/rd/avancees.md`. Une entrée exige au moins deux preuves locales qui existent, un contrôle exécutable, une limite écrite d'au moins 120 caractères, une suite et une initiative du portefeuille — sinon c'est une note de journal. Le registre ne certifie rien : il rend l'apprentissage reprenable, limites comprises.
- **Ne jamais écrire une relecture à la place d'une personne.** `docs/apprentissage/relectures.toml` est le registre des relectures humaines ; il démarre vide et un agent ne doit ni le pré-remplir, ni changer un statut vers « Relu — relecture consignée » sans une entrée réelle. `outils/registre-relecture.py --modele <fiche>` imprime le bloc à faire remplir par la personne qui a relu.

## Livraison d'une tâche

Pour un changement de contenu ou d'outil, lancer les contrôles appropriés. Porte de vérification courante du dépôt :

```sh
python3 -m py_compile simulateur/*.py api/*.py outils/*.py
python3 outils/verifier-rd-continue.py
python3 outils/construire-carte-lacunes.py --verifier
python3 outils/auditer-prototypes.py --verifier
python3 outils/construire-paquets-relecture.py --verifier
python3 outils/test_registre_relecture.py
python3 outils/registre-relecture.py
python3 outils/construire-apprentissages.py --verifier
python3 outils/construire-simulateur.py --verifier
python3 outils/verifier-site-statique.py
python3 outils/verifier-publication-locale.py
python3 outils/test_fichiers_servis.py
python3 outils/verifier-fichiers-servis.py
python3 outils/verifier-fusions.py
python3 outils/optimiser-images.py --verifier
python3 outils/verifier-poids-pages.py
python3 outils/verifier-planches-statuts.py
python3 outils/verifier-securite.py
python3 outils/verifier-integration.py
```

Après une modification de source génératrice, régénérer d'abord avec le générateur propriétaire, puis vérifier que le diff ne contient que les sorties attendues. Après un changement interactif, tester le parcours concerné, son repli sans stockage/réseau quand pertinent, et l'accessibilité réelle qui reste nécessaire.

Dans le résumé final, donner : **ce qui a changé**, **sources ou fichiers de référence**, **skills/méthodes employés**, **commandes et résultats de test**, **limites et validations encore requises**, **prochaine action suggérée**. Ne pas dire qu'un test a été effectué s'il ne l'a pas été. Ne pas publier, pousser, fusionner ni certifier sans demande et procédure adaptées.
