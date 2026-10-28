# Journal de R&D et de passation entre agents

Ce journal conserve les décisions structurantes et les relais utiles, pas le détail de chaque commit. Utiliser le [gabarit d'initiative](gabarit-initiative.md) pour une décision nouvelle et le [portefeuille vivant](portefeuille.toml) pour son état courant. Une entrée doit rester datée, reliée à un identifiant d'initiative, préciser les preuves, la décision, les contrôles réellement exécutés et la suite. Ne pas y mettre de données personnelles ni recopier les réponses de personnes apprenantes.

## 2026-10-28 — Les budgets d'affichage des titres sont vus en échec

- **Initiative :** `coherence-textes-publics`.
- **Sixième contrôle éprouvé de la journée :** `outils/verifier-budgets-visuels.py`. Il existe parce qu'aucun test ne voyait un `<title>` tronqué dans les résultats de recherche ni un H1 qui s'allonge à 320 px ; il lit les valeurs de `site.css` plutôt que de recopier des constantes — et rien ne prouvait qu'il savait refuser.
- **Trois fautes :** un `<title>` porté à 79 caractères pour un plafond de 60 ; une page privée de sa balise `<title>` ; le plancher du `clamp()` de `h1` gonflé, qui fait passer l'estimation du titre d'accueil de **6 à 63 lignes**. Quatre tests, **0,3 s**.
- **Une mutation qui n'a rien cassé, et c'est écrit :** retirer la variante `1672w` du `srcset` du héros des mondes laisse le contrôle vert. Plutôt que de forcer un test qui passerait pour une preuve, la limite est inscrite dans le banc et dans l'avancée : la géométrie du héros et les modes d'affichage ne sont pas éprouvés.
- **Câblage :** `MRSC_RACINE` ajouté à `verifier-budgets-visuels.py`, banc lancé après la porte dans `verification.yml` (la publication ne lance pas ce contrôle), `AGENTS.md` mentionne le dixième banc.
- **L'inventaire suit :** `verifier-budgets-visuels.py` passe de `aucun-test` à `banc` → **11 bancs**, **24 contrôles sur 37** avec une preuve d'échec.
- **Contrôles exécutés :** `test_mutations_budgets_visuels.py` (4 tests), `verifier-budgets-visuels.py`, `verifier-inventaire-controles.py`, `test_verifier_inventaire_controles.py`, `test_mutations_poids_pages.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier` (27 avancées), `test_protocole_editorial.py`, chargement YAML du workflow, `git diff --check`.
- **Limites :** trois fautes pour quatre familles de contrôles — les modes d'affichage et le héros des mondes restent hors d'atteinte du banc. Les nombres de lignes sont des estimations hors ligne qu'aucun rendu ne confirme : un budget respecté dit qu'une chaîne est courte, pas qu'elle est bien écrite.
- **Prochaine action :** `file-relecture.py` et `construire-paquets-relecture.py`, la file de relecture des 59 prototypes, puis `auditer-criteres-22.mjs` depuis le job `graphismes`.

## 2026-10-28 — Le budget de poids se prouve aussi en l'abaissant

- **Initiative :** `poids-et-sobriete-numerique`.
- **Cinquième contrôle éprouvé de la journée :** `outils/verifier-poids-pages.py`. Le site annonce 300 Kio mobile et 450 Kio grand écran ; ce contrôle est le seul à faire tenir la promesse, et rien ne prouvait qu'il savait refuser.
- **Quatre fautes :** une image incompressible de 400 Kio référencée par l'accueil — le budget mobile cède, mesuré à 555,6 Kio ; une ressource locale absente ; un `<picture>` sans repli exploitable ; et, **sans toucher au dépôt**, la copie intacte relancée avec `--budget-mobile 1`, où aucune page ne doit passer. Cinq tests, **22 s**.
- **Le cas qui a demandé deux essais :** ma première `<picture>` contenait un `<img src>` valide, donc elle avait un repli et le contrôle avait raison de se taire. Il a fallu un `<img>` sans source exploitable pour que la faute existe vraiment. Une mutation qui ne casse rien est un test qui ne prouve rien — c'est déjà écrit dans `banc_mutations.muter()`, et l'écrire ne dispense pas de le vérifier à la main.
- **Câblage :** `MRSC_RACINE` ajouté à `verifier-poids-pages.py` (la liste des pages est calculée à l'import, donc avant), banc lancé dans `verification.yml` et `deploy-pages.yml`, `AGENTS.md` mentionne le neuvième banc et son coût.
- **L'inventaire suit :** `verifier-poids-pages.py` passe de `aucun-test` à `banc` → **10 bancs**, **23 contrôles sur 37** avec une preuve d'échec.
- **Contrôles exécutés :** `test_mutations_poids_pages.py` (5 tests, 22,4 s), `verifier-poids-pages.py` (99 pages sous les budgets), `verifier-inventaire-controles.py`, `test_verifier_inventaire_controles.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier` (26 avancées), `test_protocole_editorial.py`, chargement YAML des deux workflows, `git diff --check`.
- **Limites :** le banc éprouve le calcul et les seuils, pas la promesse. Les budgets restent des seuils de travail qu'aucune mesure réseau ni appareil réel ne valide ; l'image de 400 Kio simule une illustration mal compressée, pas un usage. Et le contrôle ne pèse que ce qu'il sait lire — une police distante ou un média chargé après action lui échappent, comme son en-tête le dit déjà.
- **Prochaine action :** `auditer-criteres-22.mjs`, dont le banc devra tourner dans le job `graphismes` puisqu'il demande Chromium, puis `verifier-budgets-visuels.py`.

## 2026-10-28 — La mémoire du projet a son banc

- **Initiative :** `coordination-de-tous-les-agents`.
- **Le dernier contrôle de la première liste :** `outils/verifier-rd-continue.py` garde ce qui rend la R&D reprenable — skills, portefeuille, avancées, sources refusées, paquets de relecture, registre, page de transparence, veille hebdomadaire. Sa seule preuve était son propre vert.
- **Quatre fautes, quatre familles :** une initiative privée de son champ `question` ; une section `## Garde-fous` retirée d'un skill ; l'ancre `rd-innovation` renommée dans `transparence.html` ; la veille décalée du lundi au mardi. Cinq tests, **5 s**.
- **Un effet en cascade instructif :** retirer `## Garde-fous` d'un skill le rend inexploitable, et le portefeuille signale ensuite les huit initiatives qui s'appuient dessus. Le message exact est long — le banc vérifie le premier, pas la liste entière, et le dit dans sa limite.
- **Câblage :** `MRSC_RACINE` ajouté à `verifier-rd-continue.py`, banc lancé dans `verification.yml` et `deploy-pages.yml` (5 s, donc les deux), `AGENTS.md` mentionne le huitième banc.
- **L'inventaire suit :** `verifier-rd-continue.py` passe de `aucun-test` à `banc` → **9 bancs**, **22 contrôles sur 37** avec une preuve d'échec. La liste « par où continuer » est réécrite avec une contrainte nouvelle : `auditer-criteres-22.mjs` demande Chromium, donc son banc devra tourner dans le job `graphismes`.
- **Contrôles exécutés :** `test_mutations_rd_continue.py` (5 tests), `verifier-rd-continue.py` (36 OK), `verifier-inventaire-controles.py`, `test_verifier_inventaire_controles.py`, les bancs d'affichage, de pages statiques, de sécurité, de fusions, de publication, d'intégration, `verifier-site-statique.py`, `verifier-integration.py`, `construire-avancees.py --verifier` (25 avancées), `test_protocole_editorial.py`, chargement YAML des deux workflows, `git diff --check`.
- **Limites :** quatre fautes pour trente-six contrôles. La carte des lacunes, les paquets de relecture, l'audit automatique et le registre des relectures restent éprouvés par leur seule lecture. Et un portefeuille bien formé n'est pas un portefeuille juste.
- **Prochaine action :** `auditer-criteres-22.mjs` — le script qui a déjà publié « 0 élément masqué » sans avoir rien pu charger — puis `verifier-poids-pages.py`.

## 2026-10-28 — La porte d'intégration est éprouvée, et son banc a un prix

- **Initiative :** `optimisation-du-site`.
- **Quatrième et dernier point de l'ordre de rentabilité initial :** `outils/verifier-integration.py`. 1 599 lignes, seize routes montées comme le fait Vercel, les nombres écrits en prose recalculés depuis `catalogue.toml`, les ressources de `assets/` traquées quand plus rien ne les cite. Rien ne l'éprouvait ailleurs que par son propre vert.
- **Trois fautes, trois familles :** une ressource ajoutée à `assets/` que rien ne cite ; un total annoncé dans `apprendre.html` qui ne correspond plus au catalogue ; une page publique supprimée. Elles couvrent ce que la porte vérifie **elle-même**, pas ce qu'elle délègue.
- **Une limite trouvée en écrivant le banc :** deux des outils que la porte lance en sous-processus — `construire-simulateur.py` et `generer-fonctions-api.py` — ne lisent pas `MRSC_RACINE`. Ils auraient donc vérifié le **vrai** dépôt pendant qu'on croyait éprouver la copie. Le choix assumé est de ne pas les muter et de l'écrire, plutôt que d'ajouter la variable à deux outils de plus dans le même lot.
- **Le prix, et la décision qu'il impose :** `verifier-integration.py` lance quatre outils et un serveur à chaque exécution, soit 21 s. Le banc complet prend **67 s** — de loin le plus cher du dépôt (les autres vont de 0,5 à 15 s). Il tourne donc **sur les pull requests seulement** : rejouer trois fois les mêmes fautes à chaque publication n'apprend rien et doublerait la durée du travail de mise en ligne. Ce choix est écrit dans `verification.yml`, à l'endroit où il s'applique.
- **Câblage :** `MRSC_RACINE` ajouté à `verifier-integration.py` (import des modules de `simulateur/` compris), banc lancé après la porte dans `qualite`, `AGENTS.md` mentionne le septième banc et son coût.
- **L'inventaire suit :** `verifier-integration.py` passe de `aucun-test` à `banc` → **8 bancs**, **21 contrôles sur 37** avec une preuve d'échec. La liste « par où continuer » est réécrite : elle pointe désormais `auditer-criteres-22.mjs` puis `verifier-rd-continue.py`.
- **Contrôles exécutés :** `test_mutations_integration.py` (4 tests, 66,6 s), `verifier-integration.py` (tous les contrôles passent), `verifier-inventaire-controles.py`, `test_verifier_inventaire_controles.py`, `test_mutations_publication_locale.py`, `test_mutations_fusions.py`, `test_mutations_securite.py`, `test_mutations_affichages.py`, `test_mutations_site_statique.py`, `verifier-site-statique.py`, `verifier-publication-locale.py`, `verifier-securite.py`, `verifier-fusions.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier` (24 avancées), `test_protocole_editorial.py`, chargement YAML du workflow, `git diff --check`.
- **Limites :** les routes HTTP de la porte ne sont pas éprouvées ici — `verifier-securite.py` les couvre et a son propre banc ; les contrôles délégués non plus, ce qui laisse deux outils hors d'atteinte du banc tant qu'ils ne lisent pas `MRSC_RACINE`. Le banc coûte 67 s à chaque pull request : c'est une dépense assumée, pas une optimisation oubliée.
- **Prochaine action :** `auditer-criteres-22.mjs`, qui a publié « 0 élément masqué » alors qu'il n'avait rien pu charger, puis `verifier-rd-continue.py`.

## 2026-10-28 — La porte de publication se prouve en retirant un fichier de sa liste

- **Initiative :** `optimisation-du-site`.
- **Troisième point de l'ordre de rentabilité :** `outils/verifier-publication-locale.py`. Il est né d'un vrai défaut — le favicon existait dans le dépôt, les pages le demandaient, la liste de copie de `deploy-pages.yml` l'oubliait — et rien n'éprouvait ce contrôle depuis.
- **Six fautes, dans une copie complète :** une page ajoutée à la racine et oubliée à la copie ; `favicon.ico` retiré de la liste, c'est-à-dire le défaut d'origine rejoué ; un lien des pages vers un fichier non publié ; une entrée en trop dans la liste blanche de l'aperçu local ; **l'inverse** — une page publiée que l'aperçu local ne sert pas ; une adresse du `sitemap.xml` qui ne correspond à aucun fichier publié.
- **Les deux sens de l'aperçu local :** le contrôle compare deux listes qui doivent être identiques. Éprouver un seul sens aurait laissé la moitié de la promesse en l'air : un aperçu trop large fabrique un faux site, un aperçu trop étroit cache une page publiée.
- **Coût :** sept tests, **0,9 s**. Le banc tourne après la porte dans `verification.yml` **et** dans `deploy-pages.yml` — ici la porte ne vérifie pas seulement, elle autorise la publication.
- **Deuxième ancre typographique :** la première tentative a échoué sans rien écrire, parce que `verification.yml` écrit `d’aucun` avec une apostrophe courbe. Le remplacement exigeait l'ancre exacte. Leçon déjà notée le 27 octobre, reformulée ici : dans ces fichiers, copier l'ancre depuis le fichier, pas depuis le souvenir.
- **L'inventaire suit :** `verifier-publication-locale.py` passe de `aucun-test` à `banc` → **7 bancs**, **20 contrôles sur 37** avec une preuve d'échec.
- **Contrôles exécutés :** `test_mutations_publication_locale.py` (7 tests), `verifier-publication-locale.py` (136 fichiers, 99 pages, 4 802 références), `verifier-inventaire-controles.py`, `test_verifier_inventaire_controles.py`, `test_mutations_fusions.py`, `test_mutations_securite.py`, `test_mutations_affichages.py`, `test_mutations_site_statique.py`, `verifier-site-statique.py`, `verifier-integration.py`, `verifier-securite.py`, `verifier-fusions.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier` (23 avancées), `test_protocole_editorial.py`, chargement YAML des deux workflows, `git diff --check`.
- **Limites :** les mutations portent sur ce que la liste de copie **déclare**, jamais sur ce que GitHub Pages sert réellement ; un hébergement qui omettrait un fichier correctement copié laisserait la porte verte. Les en-têtes HTTP et les redirections ne sont pas de son ressort (le workflow « en-têtes » les couvre). L'aperçu local n'est comparé que pour les fichiers racine : un dossier servi en trop lui échapperait.
- **Prochaine action :** `verifier-integration.py`, dernière porte à forte conséquence vérifiée seulement par elle-même — 1 599 lignes, 16 routes exercées, et le contrôle qui compare la présentation du site au moteur du simulateur.

## 2026-10-28 — La règle « ne rien perdre en fusionnant » est éprouvée sur des dépôts neufs

- **Initiative :** `optimisation-du-site`.
- **Deuxième point de l'ordre de rentabilité :** `outils/verifier-fusions.py`. Il garde l'état de fusion, les marqueurs de conflit, les `.orig` suivis, l'ordre antichronologique et l'unicité des titres du journal, et — avec `--branches` — l'atteignabilité des blobs de chaque branche distante. Aucun test.
- **Ce qu'il ne fallait pas faire :** muter le dépôt réel. Fabriquer une branche perdue, un `MERGE_HEAD` ou un `.orig` suivi dans l'historique du projet serait une faute commise pour prouver qu'une faute serait vue.
- **La solution :** `outils/test_mutations_fusions.py` crée un **petit dépôt git neuf** par cas (deux entrées de journal, deux pages, un commit) et casse une propriété à la fois — marqueur de conflit commité, `.orig` suivi, entrées de journal inversées, titres en double, branche distante au fichier unique. Huit tests, **0,5 s**: les dépôts d'essai sont plus rapides à fabriquer qu'à copier.
- **Deux cas honnêtes, qui comptent autant que les fautes :** une branche déjà contenue dans `main` est dite « contenue dans main » **avant** toute comparaison d'objets ; une branche **recopiée** — même contenu, commits distincts, donc pas un ancêtre — est comparée blob par blob et doit rester « supprimable sans perte ». Sans ce second cas, le contrôle pourrait crier au vol à chaque fusion par recopie et personne ne l'aurait su.
- **Un premier essai faux, corrigé :** la branche d'essai « absorbée » était un ancêtre de `main`, donc le raccourci s'appliquait et la comparaison de blobs n'était jamais atteinte. Le cas a été scindé en deux : l'ancêtre, et la recopie. Le second est le seul qui éprouve vraiment `blobs_atteignables()`.
- **Câblage :** le banc tourne après la porte dans `verification.yml` (pas dans `deploy-pages.yml`, qui ne lance pas ce contrôle), `MRSC_RACINE` ajouté à `verifier-fusions.py`, `AGENTS.md` mentionne le cinquième banc.
- **L'inventaire suit :** `verifier-fusions.py` passe de `aucun-test` à `banc` → **6 bancs**, **19 contrôles sur 37** avec une preuve d'échec.
- **Un banc cassé par ce qu'il garde :** `test_verifier_inventaire_controles.py` a échoué dès que la ligne de `verifier-fusions.py` a changé de statut, parce qu'il recopiait la ligne entière en dur. La faute est instructive : un banc qui cite le document doit lire le document, sinon il interdit de le corriger. Les deux mutations concernées lisent maintenant la ligne dans la copie et n'en changent que le nécessaire.
- **Contrôles exécutés :** `test_mutations_fusions.py` (8 tests), `verifier-fusions.py --branches` (436 fichiers suivis, branche de travail supprimable sans perte), `verifier-inventaire-controles.py`, `test_verifier_inventaire_controles.py`, `test_mutations_securite.py`, `test_mutations_affichages.py`, `test_mutations_site_statique.py`, `verifier-securite.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier` (22 avancées), `verifier-site-statique.py`, `verifier-publication-locale.py`, `verifier-integration.py`, `test_protocole_editorial.py`, chargement YAML des workflows, `git diff --check`.
- **Limites :** les dépôts d'essai comptent trois fichiers ; le banc ne dit rien du comportement sur 436 fichiers suivis ni sur un vrai historique de 137 entrées. Ni `MERGE_HEAD` ni l'index non fusionné ne sont couverts — les créer proprement demanderait de manipuler un dépôt réel. Et le contrôle ne supprime rien : il autorise, une personne décide.
- **Prochaine action :** `verifier-publication-locale.py` et `verifier-integration.py`, les deux portes de publication, puis `auditer-criteres-22.mjs`.

## 2026-10-28 — La porte de sécurité est vue en échec, six fois

- **Initiative :** `optimisation-du-site`.
- **Premier point de l'ordre de rentabilité de l'inventaire :** `outils/verifier-securite.py`. Il garde les en-têtes Vercel, l'épinglage des actions, le pont WSGI, les limites HTTP, la provenance navigateur, les redirections et la liste statique du serveur local — onze fonctions internes — et **aucun test** ne prouvait qu'une seule d'entre elles savait échouer.
- **La distinction qui compte :** cet outil *contient* des assertions, ce qui le faisait passer pour testé. Mais un `verifier(condition, message)` que personne n'a jamais vu refuser est un commentaire qui s'imprime « OK ». C'est exactement le piège que l'inventaire du matin avait nommé.
- **Six fautes plantées, toutes vues avec leur message :** un en-tête `X-Frame-Options` retiré de `vercel.json` ; `"maxDuration": 60` ramené à 30, la CSP restant intacte pour que seul le second contrôle morde ; `actions/checkout@<sha>` remplacé par `@v4`, un tag mouvant ; `runs-on: ubuntu-24.04` repassé à `ubuntu-latest` ; la liste statique élargie à **tout** fichier de la racine — l'état qui a publié le dépôt entier le 25 octobre 2026 ; le plafond de lecture d'une source distante (`MAX_SOURCE_RESPONSE_BYTES`) supprimé de `simulateur/donnees_live.py`.
- **Une mutation dans le moteur, pas seulement dans la configuration :** la sixième casse du code Python réellement exécuté par le site. Elle n'était possible que parce que la porte importe `simulateur/` depuis sa racine : `MRSC_RACINE` s'applique donc aussi à l'import, et c'est bien la copie mutée qu'on éprouve. Troisième outil à recevoir cette variable.
- **Coût :** sept tests, **3,3 s** — copies complètes comprises, la copie du dépôt prenant 0,06 s. Les deux workflows le lancent après la porte, `qualite` comme `publish`.
- **L'inventaire suit :** `verifier-securite.py` passe de `aucun-test` à `banc`. Il reste **18 contrôles sur 37** appuyés sur un test capable d'échouer, dont **5** par mutation réelle. Le garde de l'inventaire a refusé la première version de cette mise à jour — il exige que le fichier de test cité existe, ce qui l'a fait échouer avant que je ne l'écrive.
- **Contrôles exécutés :** `test_mutations_securite.py` (7 tests), `verifier-securite.py` (64 lignes de sortie, 11 contrôles), `verifier-inventaire-controles.py` (45 outils, 0 écart), `test_verifier_inventaire_controles.py`, `test_mutations_affichages.py`, `test_mutations_site_statique.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier` (21 avancées), `verifier-site-statique.py`, `verifier-integration.py`, `verifier-publication-locale.py`, `verifier-fusions.py`, `test_protocole_editorial.py`, chargement YAML des deux workflows, `git diff --check`.
- **Limites :** six mutations disent ce que le banc sait voir, pas ce que la porte devrait couvrir. La provenance navigateur, le cache partagé, les redirections et la limite WSGI restent non éprouvés ; deux de ces contrôles utilisent des objets simulés à l'intérieur de l'outil, et un faux `opener` peut mentir sur le comportement réel d'`urllib`. Toujours aucun navigateur, et aucune vérification que ces portes voient des régressions qu'on n'a pas pensé à planter.
- **Prochaine action :** `verifier-fusions.py`, deuxième de la liste — il garde « ne rien perdre en fusionnant » sur un journal de 137 entrées où une inversion d'ordre s'est déjà produite.

## 2026-10-28 — L'inventaire des contrôles existe, et il est gardé

- **Initiative :** `optimisation-du-site`.
- **Suite de la même journée :** le 28 octobre 2026, deux bancs de mutation ont été écrits au cas par cas. Le journal s'était donné une autre suite : arrêter de traiter les outils un par un et écrire l'inventaire. C'est fait — `docs/rd/inventaire-controles.md` classe chaque fichier d'`outils/` par ce qui prouve qu'il peut échouer.
- **Le chiffre, sans arrondi favorable :** 45 fichiers d'`outils/` hors `test_*`, dont **8** ne sont pas des contrôles (générateurs, aides, serveur local). Sur les **37** restants : **4** `banc`, **7** `faute-en-memoire`, **6** `test`, **3** `test-en-soi`, **17** `aucun-test`. Autrement dit, **17 contrôles sur 37** s'appuient sur un test capable d'échouer ; les 20 autres n'ont aucune preuve de ce genre.
- **Un sixième statut a été nécessaire :** `test-en-soi`, pour les fichiers qui *sont* le test (`test-experience.cjs`, `test-cache-css-ia.cjs`, `verifier-graphismes.cjs` avec ses trois mutations internes). Les ranger dans `test` promettait une protection qui n'existe pas : rien ne vérifie qu'ils continuent de mordre.
- **Le garde, et pourquoi il fallait en écrire un :** un inventaire tenu à la main est faux dès le premier outil ajouté, et le document aurait alors décrit un dépôt imaginaire. `outils/verifier-inventaire-controles.py` échoue si un outil d'`outils/` n'a pas de ligne, si une ligne désigne un outil absent, si un statut sort du vocabulaire admis ou si le fichier de test annoncé n'existe pas. Il ne juge pas les statuts, et le dit dans son en-tête.
- **Ce garde-là aussi devait prouver qu'il mord :** `outils/test_verifier_inventaire_controles.py` plante cinq fautes dans une copie complète du dépôt (un outil ajouté sans ligne, une ligne retirée, un test annoncé inexistant, un statut inconnu, plus la copie intacte verte). La mutation « outil ajouté » est le cas qui compte : c'est l'oubli ordinaire, celui qui aurait rendu tout le document décoratif. Coût : 0,4 s, parce que la copie complète pèse 0,06 s.
- **Un bug du banc, corrigé et instructif :** `verifier-inventaire-controles.py` calculait sa racine depuis `__file__`, donc muter une copie ne changeait rien : deux des cinq tests ont d'abord échoué en silence, en lisant le vrai dépôt. La racine passe par `MRSC_RACINE`, comme les deux autres bancs — troisième outil à recevoir cette variable, et la raison d'être commune mérite d'être dite : un contrôle doit pouvoir lire une copie sans qu'on lui mente.
- **Câblage :** le banc et le contrôle tournent dans `verification.yml` et dans `deploy-pages.yml` (ce qui publie rend des comptes), et `AGENTS.md` exige la ligne d'inventaire dans le même commit que l'outil.
- **Contrôles exécutés :** `test_verifier_inventaire_controles.py` (5 tests), `verifier-inventaire-controles.py` (45 outils, 0 écart), `test_mutations_affichages.py`, `test_mutations_site_statique.py`, `test_verifier_taux_dates.py` + `verifier-taux-dates.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier` (20 avancées), `verifier-site-statique.py`, `verifier-integration.py`, `verifier-publication-locale.py`, `verifier-securite.py`, `verifier-fusions.py`, `test_protocole_editorial.py`, chargement YAML des deux workflows, `git diff --check`.
- **Limites :** les statuts viennent de la lecture des tests, pas de l'exécution de chaque mutation possible ; une ligne qui déclarerait `banc` en citant un test réel mais sans rapport passerait le garde. La couverture repose sur une convention de nommage (`test_*` et `__*` exclus d'`outils/`), donc un fichier d'aide nommé comme un contrôle fausserait le compte. Aucun des 17 contrôles `aucun-test` n'a été examiné en profondeur : le classement dit « non prouvé », pas « cassé ». Toujours aucun navigateur dans cet environnement.
- **Prochaine action :** `verifier-securite.py`, qui garde les frontières HTTP, WSGI, la provenance navigateur et la liste statique du simulateur sans aucun test — puis `verifier-fusions.py`, les deux portes de publication, et `auditer-criteres-22.mjs`.

## 2026-10-28 — La porte des pages statiques est éprouvée par mutation

- **Initiative :** `optimisation-du-site`.
- **Suite de l'inventaire du même jour :** sur 42 outils de vérification, une dizaine seulement avait un test capable d'échouer quand on casse la propriété contrôlée. `verifier-site-statique.py` — la porte qui voit le plus de choses, 99 pages, liens, ancres, canoniques, sitemap, `llms.txt`, syntaxe JS — n'en avait aucun.
- **Ce qui a été ajouté :** `outils/test_mutations_site_statique.py` plante cinq fautes réelles et exige un échec **avec le message attendu** : un lien qui suit un fichier renommé (`apprendre-absente.html`), une canonique recopiée d'une autre adresse, un `alt` perdu sur le logo, une ancre qui ne correspond plus à aucun identifiant (`#licence-absente`), une page publique oubliée au sitemap (`eva.html`).
- **Une copie complète, et pourquoi :** le banc des affichages travaille sur des liens symboliques ; ici c'est impossible. La porte refuse toute cible qui sort du dépôt, et un lien symbolique vers l'original en sort par construction — la première tentative a produit 4 718 faux échecs. `banc_mutations.copie_complete()` copie donc réellement l'arbre (28 Mio, 0,06 s). Le cas est documenté dans le module, parce que la prochaine personne qui écrira un banc se posera la même question.
- **Mutualisation :** les aides (`copie_jetable`, `copie_complete`, `ouvrir`, `muter`, `lancer`) sortent dans `outils/banc_mutations.py`. `test_mutations_affichages.py` a été réécrit pour l'utiliser, sans changer ses mutations — les trois tests restent verts, ce qui est la preuve du refactor.
- **Câblage :** le banc tourne après `verifier-site-statique.py` dans `verification.yml` et `deploy-pages.yml` (15 s, dont cinq exécutions complètes de la porte), et `AGENTS.md` mentionne les deux bancs et la commande.
- **Contrôles exécutés :** `test_mutations_site_statique.py` (3 tests, 5 mutations vues, copie intacte verte, dépôt inchangé), `test_mutations_affichages.py` (3 tests), `verifier-site-statique.py`, `verifier-affichages.py`, `verifier-rd-continue.py`, `verifier-integration.py`, `verifier-publication-locale.py`, `construire-avancees.py --verifier`, `test_protocole_editorial.py`, chargement YAML des deux workflows, `git diff --check`.
- **Limites :** cinq fautes ne couvrent pas les 99 pages ni les contrôles de `llms.txt`, des relations ARIA ou des dépendances d'apprentissage ; le banc prouve que ces cinq cas sont vus, pas que la porte est complète. Les 15 s s'ajoutent au temps de CI. Toujours aucun navigateur.
- **Prochaine action :** inventaire écrit des 42 outils — pour chacun, « banc de mutation », « test sans mutation » ou « écarté, et pourquoi » — plutôt que de traiter les outils un par un au hasard.

## 2026-10-28 — Les garde-fous d'affichage sont vus en échec, pas seulement verts

- **Initiative :** `optimisation-du-site`.
- **Constat de départ :** depuis le 23 octobre 2026, le journal répète « mutation rejouée : détectée » à propos de `verifier-affichages.py`. C'était vrai et c'était fait **à la main** : aucun test du dépôt n'échouait si l'on retirait la règle qu'un garde-fou prétend protéger. Un inventaire des outils le confirme : sur vingt outils de vérification, huit avaient un test, cinq d'entre eux un test qui mute réellement quelque chose.
- **Ce qui a été ajouté :** `outils/test_mutations_affichages.py` rejoue cinq mutations datées du journal sur les seize garde-fous — panneau de personnalisation ancré à droite, mention d'impression sur sa propre ligne, note de version non bornée dans le bas de page, adresse d'impression et mention d'impression retirées de l'accueil. Chacune doit produire un échec **et** le message attendu, pas seulement un code de sortie.
- **Comment, sans risque :** le banc construit une copie jetable du dépôt en **liens symboliques** ; seuls les fichiers mutés sont de vraies copies, et les dossiers parents sont matérialisés au besoin. `verifier-affichages.py` accepte désormais `MRSC_RACINE`, prévue pour cet usage. Un test vérifie que `assets/css/site.css` du dépôt est identique octet pour octet avant et après une mutation détectée : une porte qui laisse l'arbre modifié après un échec serait pire que pas de porte.
- **Le contrôle qui compte :** la copie **intacte** doit être verte. Sans ce cas, un banc de mutation prouverait seulement que le contrôle échoue toujours.
- **Défauts de mon propre banc, trouvés en l'écrivant :** `ouvrir()` utilisait `parts.index(morceau)`, qui renvoie la première occurrence et sautait le mauvais enfant dès qu'un nom se répétait ; et un fichier absent de la copie n'était jamais créé. Les deux cas donnaient un `FileNotFoundError` au lieu d'un test. Corrigés avant livraison, avec une fonction idempotente.
- **Câblage :** le banc rejoint `verifier-affichages.py` dans `verification.yml` et `deploy-pages.yml` (environ 0,6 s), et `AGENTS.md` reçoit la règle et la commande.
- **Contrôles exécutés :** `test_mutations_affichages.py` (3 tests, 5 mutations détectées), `verifier-affichages.py`, `verifier-rd-continue.py`, `construire-avancees.py --verifier`, `verifier-site-statique.py`, `verifier-integration.py`, `verifier-publication-locale.py`, `verifier-securite.py`, `test_reproductibilite_artefacts.py`, `test_protocole_editorial.py`, chargement YAML des deux workflows, `git diff --check`.
- **Limites :** cinq mutations ne couvrent pas seize garde-fous — les autres restent prouvés par la lecture et par la mesure au navigateur, pas par un échec rejoué. Le banc prouve qu'une règle retirée est vue, pas qu'elle suffit à bien afficher. Toujours aucun navigateur ici.
- **Prochaine action :** traiter ou écarter par écrit les outils de vérification qui n'ont encore aucun test de mutation, en commençant par `verifier-securite.py` et `verifier-site-statique.py`.

## 2026-10-28 — Une règle chiffrée porte sa date, et le contrôle prouve qu'il mord

- **Initiative :** `cartographier-les-lacunes` et `relire-les-44-prototypes`.
- **Suite d'une décision du même jour :** la carte `docs/rd/sujet-revenus-salaire-impots.md` fixait qu'un taux daté n'entre pas dans une fiche. Une règle écrite dans un document ne tient pas longtemps ; ce lot la rend exécutable.
- **Ce que fait le contrôle :** `outils/verifier-taux-dates.py` lit les champs de contenu du catalogue et refuse une phrase qui réunit **un chiffre en pourcentage ou en euros** et **un terme de droit, de fiscalité ou de protection sociale** (cotisation, CSG, CRDS, prélèvement, impôt, taxe, TVA, taux, plafond, barème, retenue, contribution, amende, majoration, pénalité, abattement, exonération, SMIC, revenu fiscal) sans l'année de la règle. Une phrase qui se dit « fictive » ou « inventée » passe : elle illustre, elle n'affirme pas. Et une fiche qui énonce une règle datée doit citer une source dont `droits_controles_le` est renseigné.
- **Pourquoi si étroit :** une règle large condamnerait les fiches de mathématiques. `maths-pourcentage.html` écrit « 20 % » et « 10 % » dans des exercices inventés ; ces phrases ne portent aucun terme de règle et ne sont pas touchées. Le corpus entier rend **85 fiches contrôlées, 0 défaut** — le vocabulaire fermé est ce qui rend ce zéro lisible.
- **Le piège évité :** un contrôle préventif qui ne trouve rien est indiscernable d'un contrôle cassé. `outils/test_verifier_taux_dates.py` livre donc quatorze tests, dont quatre fautes plantées dans une copie du catalogue, et une exécution par **sous-processus** qui vérifie que la sortie en erreur est bien celle du programme. Écrire le test a d'ailleurs révélé deux défauts de mon propre banc : un `TypeError` sur les entiers puis un paramètre qui masquait sa propre fonction de sérialisation — corrigés avant livraison.
- **Câblage :** nouveau pas dans `.github/workflows/verification.yml` et dans `.github/workflows/deploy-pages.yml` — la fiche est publiée, donc ses chiffres le sont aussi, et la publication contrôle ses règles depuis le 25 octobre 2026. Les deux fichiers se chargent sans erreur (`yaml.safe_load`). `AGENTS.md` reçoit la règle et les deux commandes dans la liste de livraison.
- **Traçabilité :** avancée `controle-preventif-qui-prouve-qu-il-mord` (19 avancées) et sa sortie régénérée ; carte de sujet mise à jour avec la mention du garde-fou.
- **Contrôles exécutés :** tests du contrôle, contrôle lui-même, `test_avancees.py`, `construire-avancees.py --verifier`, `verifier-rd-continue.py`, `verifier-affichages.py`, `verifier-site-statique.py`, `verifier-integration.py`, `verifier-publication-locale.py`, `test_protocole_editorial.py`, `verifier-securite.py`, `git diff --check`.
- **Limites :** le contrôle lit des chiffres écrits en pourcentage ou en euros et un vocabulaire fermé ; une règle écrite en toutes lettres lui échappe, et il ne compare aucun barème à sa date. Ses tests prouvent qu'il détecte les cas plantés, pas qu'il couvre les cas réels. Aucune relecture compétente n'a eu lieu, aucune fiche n'a été écrite.
- **Prochaine action :** passer en revue les autres contrôles préventifs du dépôt — ceux qui rendent zéro défaut sur le corpus courant — et vérifier que chacun a un test qui échoue quand on plante la faute qu'il prétend voir.

## 2026-10-28 — Une carte de sujet pour « Revenus, fiche de paie, prélèvements et impôts »

- **Initiative :** `cartographier-les-lacunes` (P1, en-cours), avec `relire-les-44-prototypes`.
- **Signal de départ :** la carte des lacunes déclarait dix-sept sujets sans aucune fiche. Deux d'entre eux touchent la vie quotidienne et restaient vides : « Droits au travail, contrats, sécurité et interlocuteurs » et « Revenus, fiche de paie, prélèvements et impôts ». Le second est ouvert ici ; le premier reste ouvert, sans carte.
- **Décision de périmètre :** la carte `docs/rd/sujet-revenus-salaire-impots.md` ne traite **pas** la paie en général. Elle borne le sujet à trois gestes : trouver sur un bulletin **fictif** le brut, le total des cotisations salariales, le net à payer avant impôt, le taux et le montant de l'impôt prélevé à la source et le net à payer ; refaire les deux soustractions et signaler un écart ; associer chaque montant appelé « net » à son usage. Tout le reste — contester un bulletin, déclarer ses revenus, arbitrer un taux, droit du travail, crédit — est explicitement dehors, avec le sujet voisin qui le porte.
- **Ce que les sources ont imposé :** les quatre pages ouvertes le 28 octobre 2026 ne disent pas la même chose au même niveau. La fiche F559 (vérifiée le 1er juin 2026) donne les sept zones du bulletin et le délai de contestation de trois ans ; la fiche F34009 (15 avril 2026) dit qui prélève l'impôt et où il figure ; la fiche F2302 (1er janvier 2026) publie des **taux et plafonds datés** ; la page Urssaf (10 avril 2026) définit les cinq montants mais pour un **salarié du particulier employeur** seulement. En croisant ces quatre niveaux, la carte retient une règle : ce qui s'apprend, c'est la structure et la vérification arithmétique, pas les taux. Un taux recopié dans une fiche deviendrait faux sans qu'aucun contrôle du dépôt ne le voie.
- **Deux pages tentées, aucune retenue :** `impots.gouv.fr/particulier/le-prelevement-la-source` a répondu « Erreur 404 », et une page d'article de Légifrance a affiché « Pas de contenu disponible à cette date ». Aucune n'est citée. Conséquence écrite dans la carte : elle rapporte ce que dit la vulgarisation officielle (Dila), pas le texte normatif ; une fiche publiée devra ouvrir l'article du code du travail à sa date.
- **Registres mis à jour :** `docs/rd/carte-lacunes.md` régénéré (quatre sujets ouverts par une carte, dont le nouveau, et dix-sept sujets toujours sans fiche) ; `docs/rd/portefeuille.toml` (`cartographier-les-lacunes` : quatre cartes, prochaine action reformulée) ; `docs/rd/avancees.toml` reçoit une avancée `taux-date-hors-de-la-fiche` et sa sortie `docs/rd/avancees.md` est régénérée (18 avancées).
- **Contrôles exécutés :** `construire-carte-lacunes.py --verifier`, `construire-avancees.py --verifier`, `verifier-rd-continue.py`, `verifier-site-statique.py` et `git diff --check`.
- **Limites :** aucune relecture par une personne compétente en argent, budget et finances — le domaine l'exige avant toute fiche ; aucune observation d'usage ; les quatre pages ont été lues une seule fois, ce jour ; la carte ne contient aucun chiffre de salaire et n'a été confrontée à aucun bulletin réel. Rien n'automatise encore la règle « pas de taux recopié ».
- **Prochaine action :** faire relire cette carte et celle de `securite-sciences`, puis choisir laquelle donne lieu à une première fiche prototype : vérification des montants d'un bulletin fictif, ou lecture complète d'une étiquette CLP.

## 2026-10-28 — Le panneau « Personnalisation » ne sort plus par la gauche sur ordinateur

- **Signalement :** « le menu part à gauche sur le mode ordinateur », avec une capture où « Agrandir » se lit « randir », « Écouter la page » « ter la page », et où la note de la lecture vocale perd son début — alors que le texte se replie correctement à droite.
- **Cause, mesurée sur la capture :** le défaut n'est pas dans le contenu du panneau mais dans son ancrage. La capture est à 2× ; le bord gauche de la fenêtre tombe à x = 202, le bord droit du panneau à x = 811. Le panneau visible fait donc 305 px CSS pour les 352 px que lui donne `min(clamp(300px, 22rem, 380px), calc(100vw - 1rem))` : **47 px passent hors de l'écran**, à gauche. Deux indices confirment un rognage et non un décalage du texte — le bord gauche du cadre n'apparaît pas, et un fragment d'icône subsiste devant chaque libellé.
- **Pourquoi seulement là :** `right: 0` ancre le panneau à son bouton. Dans l'en-tête **compact**, les deux commandes se rangent au début de la barre, juste après le logo : le bouton finit à ~305 px du bord gauche, moins que la largeur du panneau. Dans l'en-tête agrandi, la rangée est centrée et le bouton est assez à droite (le tableau du 23 octobre relève x = 912 à 1 280 px, x = 1 072 à 1 440 px). Le cas « en-tête compact sur ordinateur » n'avait jamais été mesuré : les lignes « ordinateur » de la table de référence étaient prises en-tête agrandi.
- **Correctif, une règle :** sous `@media (min-width: 761px) and (min-height: 561px)`, `html.entete-compacte .customize-settings-panel { right: auto; left: 0 }` : le panneau s'ouvre vers la droite, sous son bouton. La requête écarte explicitement les deux formats qui gardent leur ancrage propre (`position: fixed; left: .5rem; right: .5rem` sous 760 px et en paysage court) — sans ce double garde, la spécificité de `html.entete-compacte` l'aurait emporté sur leurs règles et ramené le défaut sur téléphone.
- **Ce qui ne change pas :** l'en-tête agrandi garde `right: 0`, le téléphone et le paysage court leur ancrage plein écran, ainsi que le plafond de hauteur et le défilement interne. Aucune page statique n'est modifiée : le panneau reste construit par `site.js`.
- **Contrôles exécutés :** `verifier-affichages.py` (16 garde-fous) — le contrôle « panneau du menu » vérifie désormais la bascule et sa requête ; **mutation rejouée** (`right: auto; left: 0` → `right: 0`), détectée, fichier restauré à l'identique ; `versionner-css-ia.py` → `8afb38b59bc892e8` ; `verifier-site-statique.py`, `verifier-integration.py` et `verifier-publication-locale.py` (136 fichiers, 99 pages, 4 802 références) réussis.
- **Limite :** aucun navigateur dans cet environnement ; la position est déduite de la capture et de la feuille de style, pas re-mesurée. Le rendu réel reste à constater en en-tête compact sur ordinateur, en-tête agrandi, téléphone et paysage court.
- **Suite :** vérifier à l'écran en en-tête compact à 1 024, 1 280 et 1 440 px, puis ajouter au tableau de `formats-affichage.md` une ligne « 1 280 × 900, en-tête compact ».

## 2026-10-25 — La publication vérifie aussi l'attribution imprimée

- **Constat :** `outils/verifier-affichages.py` porte depuis ce jour le contrôle de l'attribution sur copie imprimée — source, adresse, licence, statut. Il ne tournait que dans `verification.yml`, donc sur les pull requests. Une poussée directe sur `main`, ou une fusion dont la porte a été contournée, pouvait publier une page qui ne porte plus cette attribution, sans qu'aucun contrôle ne s'y oppose.
- **Pourquoi c'est une incohérence :** la règle du dépôt est que la publication contrôle ses règles, pas seulement les pull requests. Une exigence de licence vérifiée à l'entrée et pas à la sortie n'est vérifiée qu'à moitié.
- **Correctif :** `deploy-pages.yml` exécute `verifier-affichages.py` avant de préparer `_site`, sur le même commit que celui qui sera publié. Le coût est d'environ une seconde.
- **Contrôles :** les six workflows se chargent sans erreur (`yaml.safe_load`), l'étape est la 12e sur 23 et le contrôle passe localement.
- **Limite :** ce contrôle lit le dépôt, pas ce que l'hébergeur sert ensuite ; le relevé réseau reste le rôle de `verifier-publication.py`.
- **Suite :** constater au prochain déploiement que l'étape apparaît verte, et qu'un échec de format bloque bien la publication avant l'envoi de l'artefact.

## 2026-10-25 — Un dépôt sans issues ne rend plus rouge une vérification réussie

- **Constat :** sur `main`, deux workflows échouaient alors que leurs contrôles passaient — « Vérifier les en-têtes servis par l’hébergement » (relevé réussi, échec à la publication de l’issue) et « Veille éditoriale des apprentissages » (contrôles réussis, échec à la création de l’issue). Cause unique : `has_issues` vaut `false` sur le dépôt, donc `gh issue create` échoue et `set -euo pipefail` fait tomber l’étape.
- **Pourquoi c’est un défaut de notre côté :** un rapport périodique impossible à publier n’est pas une mesure en échec. Confondre les deux transforme un réglage du dépôt en alerte permanente — et une alerte toujours rouge cesse d’être lue.
- **Correctif :** les deux étapes interrogent `has_issues` avant d’écrire. Si les issues sont désactivées, elles consignent le rapport dans le résumé de l’exécution, ajoutent une note renvoyant vers **Settings → General → Features**, et sortent en 0. Rien n’est perdu : le relevé et les rapports restent lisibles, ils ne sont simplement plus dupliqués dans une issue.
- **Contrôles :** les six fichiers de workflow se chargent sans erreur (`yaml.safe_load`) ; le bloc shell ajouté est relu après analyse pour vérifier l’échappement des accents graves.
- **Limite :** le comportement réel ne sera constaté qu’au prochain run (relevé à chaque publication et chaque nuit, veille chaque semaine). Ce correctif ne dit rien de la qualité des rapports eux-mêmes.
- **Suite :** soit laisser les issues désactivées et lire les résumés d’exécution, soit les réactiver et retrouver les deux issues de suivi uniques.

## 2026-10-25 — La copie imprimée porte enfin son adresse, exigée par la licence

- **Initiative :** présentation et licence. En vérifiant le signalement précédent sur le pied de page, un défaut plus grave est apparu : la feuille d'impression lit `attr(data-print-url)` depuis le 16 octobre, et **aucune page n'écrivait cet attribut**. Toute copie imprimée sortait avec « Copie du site M.R.S.C. — — à relire, pas une version certifiée », donc sans l'adresse que la licence rend obligatoire.
- **Pourquoi c'est grave et non cosmétique :** la licence publiée dans `transparence.html#licence` impose une attribution citant explicitement l'adresse. Une page imprimée circule sans lien vers la page en ligne : elle doit porter cette adresse elle-même, sinon la réutilisation n'est pas attribuée.
- **Correctif, une source unique :** `data-print-url` est écrit dans la balise `<html>` à partir de la canonique de chaque page — pages racine, 85 fiches et `apprendre.html` par le générateur, page du simulateur par la couche d'intégration de `construire-simulateur.py` (moteur amont intact). `404.html`, sans canonique, reçoit son adresse publiée. La ligne d'impression reprend source, licence et statut ; elle ne dépend pas de JavaScript.
- **Un piège évité :** `simulateur/index.html` a d'abord été modifié à la main, ce que `verifier-integration.py` a refusé (« a divergé du moteur »). L'attribut est donc produit par le générateur, et la page régénérée — c'est le contrôle qui a empêché de figer une modification non reproductible.
- **Contrôles exécutés :** 13ᵉ contrôle renommé « pied de page et copie imprimée » — présence et contenu de `html::after`, attribut sur les 98 pages, égalité avec la canonique, accord de domaine entre la feuille et les canoniques. **Quatre mutations rejouées, quatre détectées.** Portes : affichages, site statique, publication locale, apprentissages synchronisés, intégration.
- **Limite :** le contrôle lit le CSS et le HTML, il n'imprime rien. Le rendu papier reste à constater sur une impression réelle. Les mentions « Tous droits réservés » du pied de page restent hors de la copie : la ligne renvoie à la licence.
- **Suite :** imprimer une page de chaque type (accueil, fiche, simulateur) et vérifier la ligne ; si les droits doivent figurer sur papier, ce sera une seconde ligne, pas un retour du pied de page complet.

## 2026-10-25 — La mention d'impression du pied de page prend sa propre ligne

- **Initiative :** présentation du pied de page. Signalement avec capture : « la phrase commence juste derrière le point et se retrouve coupée, visuellement c'est moche ».
- **Cause :** la phrase « Une copie imprimée n'est pas une version certifiée » suivait « Boussole des savoirs » dans le même paragraphe centré. Le retour à la ligne tombait donc au milieu d'elle, et le point précédent semblait l'introduire.
- **Petite décision, conséquence de lecture :** la mention devient un `<span class="footer-rd-print">` en `display: block` et `text-align: start`, et le paragraphe n'est plus borné à 72 ch dans le bas de page : la ligne démarre au bord gauche du conteneur, à l'aplomb du reste du site. La note de version au-dessus garde le centrage demandé le 23 octobre. Sans CSS, le `<span>` redevient en ligne : aucune page ne dépend de la feuille de style pour rester lisible.
- **Deux endroits à la fois :** les 13 pages racine et le générateur de fiches (`outils/construire-apprentissages.py`) portent le même pied de page ; les 85 fiches sont régénérées, et la porte vérifie que les deux restent d'accord.
- **Contrôles exécutés :** `verifier-affichages.py` étendu (règle CSS, `max-width: none`, présence du `<span>` sur 98 pages), avec deux mutations rejouées et détectées — `<span>` retiré d'`index.html`, puis `display: block` et `text-align: start` retirés de la règle. `construire-apprentissages.py --verifier` : sorties synchronisées.
- **Constat voisin, corrigé dans la même journée :** la règle `@media print` masque `.site-footer` en entier. Le pied de page reste masqué (ses liens relatifs seraient morts sur papier), mais la ligne d'impression porte désormais source, adresse, licence et statut — voir l'entrée « La copie imprimée porte enfin son adresse ». Les mentions « Tous droits réservés » restent, elles, hors de la copie.
- **Limite :** aucune mesure au navigateur dans cet environnement (Chromium indisponible) ; le rendu réel reste à constater, notamment le voisinage d'une ligne centrée et d'une ligne calée à gauche.
- **Suite :** regarder le pied de page sur écran large et sur téléphone ; si le mélange centré/à gauche ne convient pas, la variante tient en une règle (centrer `.footer-rd-print` ou aligner toute la note à gauche).

## 2026-10-25 — Le site est revenu, mais il publiait la racine du dépôt

- **Initiative :** publication GitHub Pages. Après le 404 du matin (site Pages absent, Actions arrêté par la facturation), le site répond de nouveau ; la source Pages a été réglée sur « Deploy from a branch ».
- **Défaut constaté :** ce mode publie la **racine du dépôt**, pas l’artefact `_site` préparé par `deploy-pages.yml`. Vérifié en interrogeant le site publié : `https://…/MRSC/README.md`, `/AGENTS.md` et `/outils/serveur-local.py` répondent 200 et servent leur contenu ; les dossiers commençant par un point (`.agents/`, `.claude/`) restent en 404, signature du traitement Jekyll d’une source de branche. Le site, pourtant vert, exposait donc `docs/`, `outils/`, `api/`, les consignes internes des agents et la licence — hors du périmètre documenté.
- **Pourquoi aucun contrôle ne l’a vu :** `outils/verifier-publication.py` ne sondait que la liste des fichiers attendus. Tous répondaient 200 ; l’excès de publication était invisible. Un contrôle qui ne vérifie que la présence ne dit rien de l’excès.
- **Correctif :** le contrôleur sonde désormais sept chemins de `HORS_PERIMETRE` (README, AGENTS, LICENCE, protocole éditorial, journal de R&D, outil de développement, source du moteur) et **échoue** si l’un répond 200 ; le rapport porte un second tableau « Hors périmètre de publication ». `configure-pages` reçoit `enablement: true` pour recréer le site s’il a disparu. `outils/test_verifier_publication.py` vérifie que le contrôle mord, contre deux serveurs locaux : une racine de dépôt servie (échec attendu) et un périmètre correct (succès attendu). Le test est branché sur les deux workflows.
- **Preuves exécutées :** sur la racine réelle du dépôt servie en local, le contrôleur sort en 1 et nomme les sept fuites ; sur `outils/serveur-local.py`, il sort en 0 (20 fichiers en 200, 7 chemins internes en 404). Quatre tests unitaires verts.
- **Ce qui reste hors dépôt :** rebasculer la source Pages sur « GitHub Actions » relève du compte ; tant que ce n’est pas fait, le site continue de publier la racine et le contrôle nocturne restera rouge — c’est l’alarme voulue, pas une régression du contrôle.
- **Limite :** le contrôle constate ce que l’hébergement sert à l’instant de la mesure ; il ne prouve ni ce qui a été publié avant, ni ce qui reste en cache. Il ne remplace pas une vérification des réglages Pages, qu’aucun jeton du dépôt ne peut lire avec les droits actuels.
- **Complément, hors sujet mais bloquant :** la porte de vérification de `main` échouait déjà depuis la fusion précédente sur `verifier-decision-prospective.py` — le brief prospectif annonçait 203/391 Kio pour la page Apprendre, la mesure régénérée dans `poids-pages.md` donne 217,5/405,8 Kio. La ligne du brief est resynchronisée à 218/406 Kio depuis cette source ; aucun autre repère du tableau ne bouge, et les 20 tests du contrôle restent verts.
- **Suite :** après rebascule, relancer la publication, constater le run vert puis le contrôle d’en-têtes du lendemain ; si un 200 réapparaît sur un chemin interne, la source a changé de mode.

## 2026-10-25 — Séparer les contenus de personnage du site associatif

- **Décision :** les portraits, références physiques et travaux personnels du personnage ne relèvent pas de ce dépôt. Ils sont retirés de l’arbre courant, avec sauvegarde hors dépôt avant suppression.
- **Périmètre :** retrait du prototype visuel et de ses dépendances, de son lien dans Personnalisation, de sa route de publication et des descriptions de personnage dans la bible du film. Les planches du film associatif et la présentation générale de la recherche en IA sont conservées.
- **Limite :** ce nettoyage ne purge ni l’historique Git, ni les anciennes PR, ni les versions étiquetées. Ne pas republier le dépôt sans traiter ces emplacements ; le passage en privé ne garantit pas le retrait des copies antérieures.
- **Prévention :** règles d’exclusion et contrôle dédié dans la CI et avant publication ; elles empêchent le retour des chemins connus, pas la reconnaissance universelle de données sensibles dans tout fichier.
- **Complément :** retrait des deux décisions historiques de création du personnage et de 164 entrées de son inventaire ; 343 empreintes de travaux associatifs conservées sans modification. Les originaux restent sauvegardés hors dépôt et dans le dossier Drive de passation. Quatre tests supplémentaires portent le garde-fou à onze tests.
- **Contrôles exécutés :** sept tests du garde-fou, vérifications statique, publication locale, intégration, sécurité, archive des planches et poids des pages ; quatre tests de reproductibilité. Aucun essai navigateur ni retrait des copies historiques revendiqué.

## 2026-10-24 — Réunir des groupes sans donner le même poids à leurs moyennes

- **Initiative :** `relire-les-44-prototypes`. Enrichissement de `maths-moyenne`, sans nouvelle fiche ni changement de statut : 85 fiches, 59 prototypes.
- **Besoin éditorial :** la suite du lot précédent identifiait le piège des effectifs différents. Ce n'est pas un retour d'usager ni une difficulté mesurée auprès de personnes.
- **Choix :** exercice supplémentaire dans la fiche existante, plutôt qu'une nouvelle fiche redondante ou une formule isolée. Reconstituer les totaux avant de nommer la pondération ; durée indicative portée de 10 à 14 minutes, non mesurée en séance.
- **Source consultée :** documentation Python 3.14.0, section `fmean` et poids. Exemple original, calcul contrôlé ; référence technique et non pédagogique. Aucune reprise de texte ni exercice.
- **Preuves :** huit tests ciblés, dont une mutation de la moyenne globale. [Dossier du complément](groupes-statistiques-2026-10-24.md). Le statut reste « Prototype à relire » ; aucune relecture indépendante réalisée.
- **Suite :** faire relire la charge de la fiche et l'explication du poids ; si l'enchaînement zéro/absence/groupes est trop dense lors d'un essai approuvé, découper l'activité sans multiplier des fiches quasi identiques.

## 2026-10-24 — Comparer les résumés sans inventer les données absentes

- **Initiatives :** `relire-les-44-prototypes` et `co-conception-et-essais`. Lot de contenu délimité : une nouvelle fiche `maths-moyenne-mediane`, une fiche `maths-moyenne` enrichie par la différence entre zéro et absence. Catalogue : 85 fiches, dont 59 prototypes à relire ; aucun nouveau sujet déclaré complet.
- **Recherche :** documentation Python 3.14.0, sections mean et median réellement lues. Formules et conventions explicites ; aucune efficacité pédagogique déduite de cette référence technique. Exercices fictifs originaux et droits de reprise non vérifiés, sans extrait repris.
- **Conception :** une valeur change entre deux séries pour comparer le partage et la position. Pas d'animation ni de tableau de bord qui remplacerait l'explication. [Dossier du lot](lot-statistiques-2026-10-24.md) : hypothèse, options écartées, registre des affirmations et tâche d'essai à faire approuver.
- **Contrôles :** six tests numériques et éditoriaux ciblés, dont deux mutations de réponses détectées ; audit des 59 prototypes sans échec mécanique (un constat documentaire préexistant reste ouvert). Passe de rendu ciblée : 288 relevés, 0 échec. Publication locale, génération, poids, statuts et sources déclarées contrôlés.
- **Angle mort corrigé :** les garde-fous demandaient que les anciens relevés axe augmentent automatiquement avec le nombre de fiches. Les chiffres historiques sont désormais séparés du compte courant : ajouter une page ne signifie pas l'avoir auditée.
- **Limites :** aucune relecture humaine ajoutée, une seule source documentaire pour la nouvelle fiche, aucun essai de compréhension, aucun taux RGAA/WCAG. La passe navigateur porte sur la géométrie du contenu et non une validation d'accessibilité complète.
- **Suite :** obtenir une relecture mathématique et pédagogique, puis éprouver les confusions tri/doublons/zéro avec un protocole approuvé. Aborder ensuite les groupes de tailles différentes, sans gonfler le catalogue par des doublons.

## 2026-10-24 — Le cache peut désynchroniser le dessin et ses pastilles

- **Initiative :** `optimisation-du-site`. La capture smartphone fournie après la fusion #188 montre les nouveaux points SVG et la nouvelle légende, mais les anciennes positions CSS des pastilles et du cœur. Les mesures précédentes utilisaient un contexte navigateur neuf et ne couvraient pas ce mélange.
- **Reproduction :** servir le HTML courant avec le CSS du commit `f3c4ddf` reproduit les décalages ; un test pérenne rejoue les seules anciennes règles géométriques. Cela étaye l'explication sans prétendre lire le cache du téléphone.
- **Correction :** l'URL du CSS de `ia-societe.html` porte désormais une empreinte SHA-256 de son contenu. Une nouvelle réponse HTML demande donc une autre URL que celle du CSS antérieur. `versionner-css-ia.py --verifier` refuse une empreinte absente ou périmée ; son mode sans option la synchronise après modification de la feuille.
- **Contrôles :** 12 cas navigateur (320/390/768 px, présentations équilibrée/compacte, texte 130 %, densité 2), anciens décalages détectés et nouvelles ancres alignées. Relevé : [audit-cache-css-ia-2026-10-24.json](audit-cache-css-ia-2026-10-24.json). Test exécuté avec le CSS historique entier puis avec la fixture ciblée. Passe complète IA rejouée avec la nouvelle URL : 1 260 relevés, 0 échec. Tests Python de l'empreinte, site statique et périmètre publié également vérifiés ; contrôle et simulation ajoutés à la CI.
- **Limite :** cette correction cible la page IA. Elle ne force pas le renouvellement d'un document HTML lui-même conservé en cache et ne prouve pas l'état du cache de l'appareil de l'utilisateur. Les autres pages n'ont pas encore d'URL CSS versionnée.
- **Suite :** vérifier après publication le rendu sur le téléphone concerné, puis étudier le versionnement des ressources sur l'ensemble des pages générées.

## 2026-10-24 — Restaurer l'identité, puis mesurer les alignements

- **Initiative :** `optimisation-du-site`. Les héros vectoriels ont été rejetés : la netteté n'autorise pas à réinterpréter l'identité. Les cinq fichiers d'accueil antérieurs sont récupérés depuis le parent de leur suppression, sans réencodage ; Apprendre retrouve son illustration antérieure et son générateur est synchronisé.
- **Décision :** direction photographique et documentaire, illustration minimale, aucun redessin du logo officiel. [Ligne graphique](ligne-graphique.md) : les images restaurées restent des synthèses existantes, pas des photographies documentaires ; la migration de tout le site n'est pas achevée.
- **Cause rectifiée :** les pastilles IA avaient déjà `translate(-50%, -50%)`. Le décalage venait des dérogations mobiles à leurs positions, sans changement des points SVG. Coordonnées unifiées, cœur proportionné et question déplacée dans la légende pour ne pas sortir du disque au cran 130 %.
- **Mesure :** 3 780 relevés finaux, 0 échec sur les trois visuels ; sept largeurs, cinq crans, six présentations, trois modes et densités 1/2. Les deux images ont été validées puis les 1 260 relevés IA rejoués après la dernière correction. 420 relevés enregistrent le masquage volontaire de l'illustration Apprendre en couleurs forcées. Voir [le relevé](audit-graphismes-2026-10-24.json).
- **Contrôles :** proportions et pixels réellement décodés, densité, cadre horizontal, ancres à 2 pixels, chevauchements et débordement du texte des pastilles. Trois mutations exécutées et détectées (distorsion, densité, ancre). Captures 320/390/1280 au cran 130 %, densité 2 ; revue des captures accueil et IA sur smartphone simulé.
- **Porte continue :** job `graphismes` ajouté au workflow de vérification, avec relevés et captures conservés même en échec. Les contrôles locaux d'affichage, d'intégration, de publication locale, de variantes, de génération et du site statique passent.
- **Limites :** contrôle ciblé, Chromium seulement, pas de contraste sur les pixels, pas de vérification humaine sur téléphone ni de validation de tous les visuels. Source d'accueil limitée à 1400 px : plafond 700 CSS px pour la densité 2, sans agrandissement artificiel.
- **Suite :** inventorier les autres visuels, étendre la passe aux densités supérieures et mesurer le contraste ; faire relire la direction graphique, sans annoncer une conformité RGAA/WCAG.

## 2026-10-24 — L'espacement du texte casse la mise en page avant de la rendre lisible

- **Initiative :** `optimisation-du-site`. Après la taille des cibles et le focus, un troisième critère se mesure : **espacement du texte** (`1.4.12`, niveau AA depuis WCAG 2.1). Il ne demande pas d'afficher un texte espacé, mais de supporter qu'une personne impose elle-même interligne 1,5, interlettrage 0,12 em, espacement des mots 0,16 em et 2 em après chaque paragraphe — sans perte de contenu ni de fonction.
- **Pourquoi lui :** la taille des cibles et le focus mesurent des éléments ; ce critère mesure une **mise en page**. C'est le seul des trois qui pouvait révéler une largeur figée, un libellé en `nowrap` ou une barre de navigation trop juste.
- **Mesure :** `outils/auditer-criteres-22.mjs` applique ces quatre valeurs en `!important` après chargement, puis cherche deux pertes : une page qui se met à défiler horizontalement, et un texte rogné par un ancêtre en `overflow: hidden`. Le texte est cherché par nœud, pas par conteneur : un `overflow` sur un bloc décoratif ne rogne rien.
- **Deux défauts réels, sur 196 relevés (98 pages × 390 et 1 280 px) :**
  1. À 1 261–1 366 px, la barre de navigation sortait du cadre de **47 à 56 px** : les sept entrées espacées ne tenaient plus sur une ligne, et « Nous contacter » finissait hors de la fenêtre. `flex-wrap: wrap` sur `.nav-links` suffit ; la ligne reste unique tant qu'elle tient.
  2. Les **84 fiches** débordaient de **22 px** à 1 280 px : le bouton « Retour aux mondes et parcours » de la colonne latérale mesure 361 px avec l'interlettrage du critère, dans une colonne de 300 px. Son `white-space: nowrap` — voulu partout ailleurs pour des boutons nets — lui interdisait de passer à la ligne. Seule cette règle est rendue sécable.
- **Piège de mesure, encore :** la page ne signalait aucun défilement horizontal quand la barre sortait du cadre, parce que le débordement partait à gauche et à droite du conteneur centré. Un contrôle de débordement seul concluait « rien à signaler » : c'est en mesurant la position réelle de chaque élément, puis en regardant quels nœuds de texte sortaient de leur cadre, que les deux défauts sont apparus.
- **Ce que la correction change à l'œil :** entre 1 261 et 1 366 px, la barre passe sur deux lignes centrées — les dix entrées, puis « Nous contacter » — plutôt que de sortir de l'écran. Aucune entrée n'est retirée ni raccourcie, et la ligne reste unique partout ailleurs. Le panneau mobile ouvert garde ses dix entrées sur une seule colonne à 390 px, avec et sans l'espacement (mesuré).
- **Après correction :** **0 débordement sur 196 relevés**, **0 texte rogné**, la taille des cibles et le focus inchangés (5 655 conformes / 8 856 éléments testés). Les 84 fiches ont été repassées une à une aux deux largeurs avec l'espacement du critère : 0 débordement.
- **Garde-fou :** `verifier-affichages.py` compte un **16ᵉ** contrôle — `flex-wrap` sur `.nav-links`, `white-space: normal` sur le bouton de la colonne latérale, et les trois valeurs d'espacement du réglage « espacement renforcé » (interligne ≥ 1,5, interlettrage ≥ 0,12 em, espacement des mots ≥ 0,16 em). Trois mutations jouées, trois détectées.
- **Protocole :** § 6 decies de [`formats-affichage.md`](formats-affichage.md) ; note [`inclusion-criteres-wcag-22.md`](inclusion-criteres-wcag-22.md).
- **Limite :** la mesure voit un rognage et un débordement, pas une perte de sens : un chevauchement partiel, une coupure de mot moche, un texte masqué par un `clip-path` sans `overflow` restent invisibles pour elle. Une ellipse avec moyen de révéler le texte est admise par le critère ; le dépôt n'en utilise aucune. Aucune personne n'a relu ce critère non plus.
- **Prochaine action :** faire relire les trois critères par un rôle accessibilité, et rejouer la passe — une vingtaine de minutes — à chaque changement de mise en page.

## 2026-10-24 — Ce que la lecture laissait entendre, et ce que la mesure cachait

- **Initiative :** `ecouter-la-page` et `optimisation-du-site`. Deux passations différées du lot « écouter la page » : un défaut d'écoute et un angle mort de mesure.
- **Défaut mesuré, plus large que noté :** trois segments d'`anglais-avenventure.html` avaient été signalés sans ponctuation finale. La mesure, refaite sur les 98 pages en attendant la fin réelle de chaque lecture, en trouve **46 sur 6 462**. Un bloc long est découpé en morceaux de 220 caractères ; la coupe tombait sur une espace, donc au milieu d'une phrase, et le morceau finissait sur un mot nu que le moteur enchaîne au suivant comme un mot de plus.
- **Correction :** chaque morceau coupé reçoit une virgule — elle dit la continuation, là où un point inventerait une phrase — et cette virgule compte dans la limite : à 220 caractères, le dernier mot repasse au morceau suivant. Après : **0 segment sur 6 462** sans ponctuation finale, aucun au-delà de 220 caractères. Trois mutations statiques rejouées, trois détectées ; la première, « virgule mise en commentaire », a échappé au contrôle, qui cherchait une sous-chaîne : il compare désormais la ligne réelle.
- **Angle mort de mesure :** le relevé WCAG 2.2 annonçait « 825 éléments testés » alors que le site compte 8 856 cibles ; le plafond de 60 par page et l'échantillon de huit pages coupaient la passe en silence. Pire, lancé sans serveur local, le même outil rendait « 0 cible, 0 masquée » — indiscernable d'une page parfaite.
- **Correction :** plafond porté à 500 (le maximum observé est 448), focus mesuré sur les 98 pages aux deux largeurs, pages coupées et cibles non testées déclarées, chargement en échec compté comme un échec. Résultat : **8 856 éléments testés sur 8 856 atteignables, 0 entièrement masqué, 0 page coupée**. Cibles : 5 655 conformes, 901 en ligne, 2 304 espacées, 0 à corriger. Relevé conservé dans [`audit-criteres-22-2026-10-24.json`](audit-criteres-22-2026-10-24.json).
- **Écart assumé :** +2 cibles par rapport au relevé du 23 octobre (5 654 / 900), sans effet sur la conclusion ; l'origine n'a pas été isolée et n'est pas attribuée.
- **Limite :** aucun son réel n'a été écouté — la virgule est vérifiée comme chaîne, pas à l'oreille ; et la passe de focus reste une géométrie de cinq points, sans lecteur d'écran ni appareil réel.
- **Prochaine action :** faire écouter une page longue par une personne qui lit difficilement, en notant si les reprises après une virgule s'entendent naturellement ; rejouer la passe de focus à chaque changement de mise en page.

## 2026-10-24 — Les deux derniers héros cessent d'être des images

- **Initiative :** `optimisation-du-site`. L'emblème de l'accueil et l'atlas de la page d'apprentissage étaient les deux dernières illustrations bitmap du site ; le héros des Mondes et le décor des missions sont déjà des rendus.
- **Constat mesuré :** à 390 px et 3×, la boîte de l'emblème mesure 366 × 202 px, donc l'écran demande 1 098 pixels de large quand la source en fournit 1 400 — net à 1,3×, interpolé au-delà. Agrandir la source repousse la limite sans la supprimer, chaque écran plus dense la ramenant.
- **Décision :** remplacer les deux photos par des tracés SVG, dans le langage graphique déjà employé par le site. `accueil-embleme-mrsc.svg` (4 518 octets) reprend les quatre arcs, le joyau de verre et le sigle ; `atlas-savoirs.svg` (8 700 octets) reprend les trois îles reliées au-dessus d'un livre ouvert. Aucune image agrégée, aucun HTML étranger dans les tracés.
- **Effet mesuré :** accueil 153,5 → **75,9 Kio** (mobile et grand écran), `apprendre.html` 216,0 → **113,1 Kio** mobile et 404,2 → 113,1 Kio grand écran, laquelle était signalée proche du budget de 450 Kio. Cinq fichiers retirés (813 782 octets) ; manifeste, générateur de variantes, relevé d'en-têtes et sonde de publication mis à jour.
- **Contrôle :** le 7ᵉ contrôle de `verifier-affichages.py` est réécrit — un seul tracé par figure, dimensions intrinsèques exactes, `viewBox`, `title`, pas de `<image>` ni de `data:image/`, poids borné, et ratio de la feuille lu **dans la règle de la figure** puis comparé à celui du tracé. **Neuf mutations rejouées, neuf détectées.** La version initiale validait un ratio trouvé ailleurs dans la feuille ; c'est la mutation « 16/9 » qui l'a révélé.
- **Protocole :** § 6 undecies de [`formats-affichage.md`](formats-affichage.md) ; § 4.2 septies de [`poids-et-sobriete-numerique.md`](poids-et-sobriete-numerique.md).
- **Limite :** le rendu est net, pas nécessairement plus beau — les tracés sont plats, sans grain ni profondeur de champ, et une personne peut préférer l'ancienne image. Mesure dans un Chromium sans interface seulement ; aucun appareil réel, et la composition n'a été relue qu'en capture à 390, 768 et 1 440 px.
- **Prochaine action :** faire regarder les deux tracés par une personne extérieure au lot, consigner son verdict, et retirer le dernier repli bitmap de l'accueil si la réponse est positive.

## 2026-10-23 — « Écouter la page » : reculer et choisir sa vitesse

- **Initiative :** `ecouter-la-page`. Deux gestes manquaient pour écouter vraiment : reprendre le passage qu'on vient de perdre, et choisir un débit qui convient.
- **Décision instruite :** les travaux sur le débit de parole ne montrent pas d'effet uniforme d'une vitesse donnée ; l'étude sur l'aphasie (25 adultes, 113/154/200 mots par minute) ne trouve pas d'écart significatif de compréhension **entre vitesses** mais conclut à la nécessité de respecter les préférences individuelles, et une étude de 1997 où l'auditeur contrôle le débit trouve un gain. Conclusion retenue : donner le choix, sans promettre un gain.
- **Ce qui est livré :** bouton « Reculer » (rejoue le passage précédent), sélecteur à quatre crans (0,75 / 1 / 1,25 / 1,5), application immédiate en reprenant le passage courant, clé `mrsc-lecture-vitesse` pour la mémoire locale. La note sous les commandes dit désormais que la vitesse reste sur l'appareil ; la page Vie privée nomme la clé.
- **Piège évité, mesuré :** `cancel()` peut rappeler `onend` d'une énonciation annulée. Sans jeton de génération, « Reculer » ou un changement de vitesse rejouait **deux** passages au lieu d'un (constaté : 7 énonciations au lieu de 6). Le jeton est vérifié dans les deux rappels ; l'essai navigateur simule ce rappel tardif et échoue si le jeton manque.
- **Mesures :** à 320 px et 130 %, les quatre commandes tiennent dans le panneau (283, 127, 145 et 153 px de large ; 53, 53, 53 et 44 px de haut), débordement 0 px ; même résultat à 390 et 1 440 px, à 100 % comme à 130 %. **14 mutations rejouées, 14 détectées** sur le contrôle statique ; **9/9 essais navigateur** ; axe 49 exécutions, 0 violation.
- **Protocole :** § 6 decies de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** le banc remplace la synthèse par un double ; aucun débit réel n'a été écouté, et personne n'a encore essayé ces deux gestes.
- **Prochaine action :** faire écouter la fonction par une personne qui lit difficilement et par une personne sous lecteur d'écran, en notant le cran de vitesse qui lui convient.

## 2026-10-23 — Les critères WCAG 2.2 mesurés avant le RGAA 5

- **Initiative :** `optimisation-du-site` et `ecouter-la-page`. Le RGAA 5, aligné sur WCAG 2.2, est annoncé pour la fin 2026 : deux critères AA n'existaient pas dans la version travaillée jusqu'ici — taille des cibles (`2.5.8`) et focus non masqué (`2.4.11`).
- **Outil :** `outils/auditer-criteres-22.mjs`, hors CI (il demande Chromium). Trois états : conforme, exception prévue par le critère, à corriger. Il relève toutes les cibles d'une page, écarte celles qui sont dans une phrase et celles qui sont assez espacées, puis porte le focus sur un échantillon pour vérifier qu'aucun bandeau collant ne le recouvre entièrement.
- **Résultat, site entier :** 98 pages × 390 et 1 280 px — **5 654 cibles conformes, 900 en ligne (exception), 2 304 espacées (exception), 0 à corriger**. Focus : **825 éléments testés sur huit pages, 0 entièrement masqué**.
- **Avant correction, 12 défauts réels**, tous dans le pied de page à 390 px : « Contact » 49 × 19, « Haut de page » 86 × 19, « Licence » 48 × 19. Les liens légaux passent à 24 px de haut (`inline-flex` + `min-height`), l'écart vertical du bloc reprenant la hauteur gagnée : pied de page à **430 px** à 1 440 px (425 avant), écart de centrage **0 px** sur chaque ligne, aucun débordement. `.footer-legal a` entre dans les `CIBLES` du contrôle statique ; `min-height` retiré ⇒ contrôle en échec.
- **Défaut trouvé dans le lot de la veille :** le premier balayage signalait 50 cibles de 15 px sur `apprendre.html`. C'étaient des liens dans des `<details>` **fermés** : Chromium leur donne une boîte non nulle. La lecture à voix haute livrée le 23 octobre s'appuyait sur `getClientRects`, insuffisant pour ce cas ; elle aurait pu lire un contenu que personne ne voit. Quatre cas mesurés : `display:none` (texte présent, boîte vide), `visibility:hidden` (texte vide, boîte non vide), `<details>` fermé (texte vide, boîte non vide), `aria-hidden` (visible pour l'œil). Aucune mesure seule ne suffit : le filtre vérifie désormais `checkVisibility`, garde `getClientRects` et `innerText` en secours et écarte `aria-hidden` à part.
- **Essai navigateur ajouté :** sur `apprendre.html`, la liste de couverture n'est pas lue quand elle est fermée (449 segments, 0 « Fiche(s) ») et l'est quand elle est ouverte (564 segments, 82). **9/9 essais**.
- **Protocole :** § 6 nonies de [`formats-affichage.md`](formats-affichage.md) ; note [`inclusion-criteres-wcag-22.md`](inclusion-criteres-wcag-22.md).
- **Limite :** deux critères mesurés ne font pas un audit ; une géométrie ne dit rien de la difficulté réelle à viser une cible ; l'échantillon de focus s'arrête à 60 cibles par page et à huit pages ; aucune personne n'a relu ces critères.
- **Prochaine action :** rejouer la mesure à la publication du RGAA 5, puis faire relire les deux critères par un rôle accessibilité.

## 2026-10-23 — « Écouter la page » : l’inclusion comme recherche, pas comme conformité

- **Initiative :** `ecouter-la-page` (nouvelle, `prototype` / `a-valider`). Demande : « continue la R et D, l’innovation et la prospective pour que le site soit inclusif ».
- **Recadrage d’abord :** aucun taux de conformité RGAA ou WCAG n’est publié. La décision n° 2026-358 de l’Arcom (24 juin 2026) sanctionne précisément un espace déclaré « totalement conforme » alors qu’un audit mesurait 42,11 % : une déclaration n’est pas une mesure. Le lot est donc instruit comme une **option de conception** de la note prospective, avec ses preuves et ses limites.
- **Options comparées** dans [`inclusion-lecture-vocale.md`](inclusion-lecture-vocale.md) : lecture locale à voix haute (retenue), fichiers audio enregistrés (coût de maintenance et dérive de version), service de synthèse distant (le texte quitterait l’appareil, contraire à la décision 4), lecteurs d’écran seuls (ne sert pas qui voit mais lit lentement), ne rien construire (repli).
- **Décision instruite par deux méta-analyses :** effet modéré de la lecture à voix haute sur la compréhension en lecture (`d = 0,35`, IC 95 % 0,14–0,56 ; Wood & al., *Journal of Learning Disabilities*, 2018, 22 études, 2 942 participants) ; effet négligeable des polices « pour dyslexiques » (`g = -0,04` ; *Annals of Dyslexia*, 2026, 15 études, 688 participants). Conclusion retenue : construire l’écoute, s’abstenir d’une police miracle.
- **Ce qui est livré :** une commande « Écouter la page », en dernier dans le panneau *Personnalisation*, créée **seulement** si le moteur existe ; lecture du seul `main`, blocs découpés à 220 caractères, langue de chaque bloc respectée (une réplique anglaise des Escales est prononcée en `en`), arrêt net, pause, état annoncé en `aria-live`, bloc en cours marqué par un contour, voix coupée au `pagehide`. Aucun stockage, aucune requête, aucun tiers.
- **Trois défauts trouvés en écoutant le code, pas à l’œil :**
  1. `textContent` collait les phrases séparées par un élément mis en bloc — « librement.Les Escales ». Passage à `innerText`, plus un point ajouté aux blocs qui n’en ont pas.
  2. Un bloc situé dans un `<details>` refermé, ou masqué, était lu quand même : `getClientRects()` vide les écarte désormais tous d’un coup.
  3. « Arrêter la lecture » et « Reprendre » débordaient du panneau sous 360 px à 130 %. Libellés raccourcis (« Arrêter », nom accessible complet conservé), puis `flex-basis: 0` pour que la pause cesse d’être renvoyée à la ligne suivante. Mesuré à 320 px et 130 % : 125 × 53 px et 148 × 53 px, contenus dans le panneau, 0 px de débordement.
- **Ordre dans le panneau corrigé après capture :** intercalée entre « Affichage » et « Présentation », la commande coupait le groupe de réglages en deux. Elle passe en fin de panneau ; l’en-tête compact garde exactement deux boutons.
- **Trois pièges de moteur corrigés avant publication :** Chromium remonte une annulation volontaire comme une erreur `interrupted` — filtrée, sinon « Arrêter » annonçait une panne ; `cancel()` suivi d'un `speak()` dans le même tour est parfois perdu, la première énonciation part au tour suivant ; « Reprendre » ne relance plus le segment suivant, sous peine de le lire deux fois. L'essai navigateur étendu à ces cas échoue bien quand le filtre est retiré.
- **Mesures :** 49 segments sans doublon sur une fiche type ; 534 sur une Escale ouverte, dont 1 en `lang="en"` ; 0 requête réseau pendant la lecture ; aucun texte agrandi deux fois.
- **Garde-fou :** 15ᵉ contrôle `controler_lecture_a_voix_haute` (présence, appel dans le panneau, langue, arrêt, `aria-live`, écarte les contenus masqués, aucun `fetch`). **Sept mutations rejouées, sept détectées** — après quatre premières versions trop permissives (sous-chaîne au lieu de l’appel réel, CSS présent mais déclaration disparue).
- **Un nom accessible refusé par axe :** le premier jet donnait au bouton `aria-label="Lire la page à voix haute"` alors que son texte visible était « Lire à voix haute » — deux règles sérieuses `label-content-name-mismatch`, une par largeur. Le nom redondant est retiré au repos ; à l'arrêt, « Arrêter la lecture à voix haute » contient bien « Arrêter ». Mesure refaite : 0 violation.
- **Accessibilité :** `verifier-accessibilite.cjs` passe de 47 à **49 exécutions, 0 violation**, avec deux états ajoutés pour le panneau muni de l’écoute. **Essais navigateur : 9/9**, dont un essai dédié qui remplace `speechSynthesis` par un double.
- **Limite déclarée à côté de la commande et dans la note :** la voix est celle de l’appareil, elle peut manquer ou mal prononcer ; ce n’est pas un lecteur d’écran ; aucune voix réelle n’a été écoutée par une personne, aucun essai d’usage n’a eu lieu, et le chiffre `d = 0,35` vient d’études scolaires anglophones. Ce lot ne vaut ni conformité ni preuve d’efficacité.
- **Prochaine action :** faire écouter la fonction par une personne qui lit difficilement et par une personne utilisant un lecteur d’écran ; consigner les mots mal prononcés. Rôle : accessibilité, sans échéance promise.

## 2026-10-23 — L’illustration d’« Apprendre » n’est plus agrandie

- **Initiative :** `optimisation-du-site`. Signalement avec capture : « l’image dans le menu apprendre est moche, on voit les pixels ».
- **Cause trouvée, mécanique :** l’attribut `height="941"` du HTML servait de hauteur. `aspect-ratio` ne calcule une dimension que si l’autre est automatique : la boîte mesurait **497 × 941 px** au lieu de 497 × 311, et l’image 16/9 était étirée **2,1 fois** pour la couvrir. Le défaut ne venait donc pas de l’encodage.
- **Décision :** `height: auto` sur `.english-promo-art img` ; `aspect-ratio` reprend la main et `object-fit: cover` recadre au lieu d’étirer.
- **Résultat mesuré :** boîte 328 × 205 à 390 px, 497 × 311 au-delà de 760 px ; la variante servie couvre toujours au moins le pixel de l’écran (marge de 1,19× à 1,97× selon le profil, 1,44× avant correction tombait à 0,47× sur écran 2×), aucun débordement horizontal.
- **Garde-fou :** nouveau 14ᵉ contrôle `controler_illustrations` (`height: auto`, `aspect-ratio`, `object-fit`, les deux `sizes`, dimensions intrinsèques, plafond de 520 px). **Six mutations rejouées, six détectées** — dont une d’abord passée inaperçue (`sizes` faussé sur une seule des deux sources), corrigée en comparant le nombre d’occurrences.
- **Protocole :** § 6 ter bis de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** mesure d’un Chromium sans interface sur `apprendre.html` ; les autres illustrations n’utilisent pas `aspect-ratio` et ne portent pas ce défaut.
- **Prochaine action :** décor vectoriel du héros pour `apprendre.html` et l’accueil.

## 2026-10-23 — Le texte du bas de page vraiment centré

- **Initiative :** `optimisation-du-site`. Troisième retour, capture à l’appui : « l’affichage est pas top là en bas de page, c’est pas vraiment équilibré ».
- **Cause trouvée :** le centrage publié ne portait que sur les boîtes. Une règle globale alignant tous les paragraphes sur `start` s’applique directement aux paragraphes du pied de page et gagne sur le `text-align: center` hérité ; les droits et les liens, tenant sur une ligne, paraissaient centrés, mais la note de version restait collée à gauche.
- **Décision :** centrage explicite des paragraphes du bas de page (`.footer-bottom p { text-align: center }`), et non plus confiance dans l’héritage.
- **Mesure refaite :** l’écart est désormais calculé sur le milieu de chaque *ligne de texte*, pas sur celui de la boîte. Résultat : **0 px** sur toutes les lignes, à 320, 390, 576, 720 et 1 440 px, sur quatre pages, à 100 % et à 130 % de texte, sans débordement.
- **Piège de garde-fou :** le premier jet du contrôle a échoué alors que la règle était juste — le commentaire CSS citait une accolade et l’expression régulière `[^}]*` s’arrêtait dessus. Commentaire réécrit sans accolades.
- **Garde-fou :** `controler_pied_de_page` vérifie maintenant le centrage explicite des paragraphes ; **sept mutations rejouées, sept détectées** ; les 13 contrôles d’affichage passent.
- **Protocole :** § 6 septies de [`formats-affichage.md`](formats-affichage.md), « Troisième passage : le texte lui-même ».
- **Limite :** mesure d’un Chromium sans interface ; reste à constater sur un écran réel, à fort grossissement.
- **Prochaine action :** revue visuelle sur téléphone réel, puis décor vectoriel du héros pour `apprendre.html` et l’accueil.

## 2026-10-23 — Le bas du pied de page centré

- **Initiative :** `optimisation-du-site`. Deuxième capture, avec un point encore visible sous la note de version et une demande : « l’affichage devrait être centré ! Ce serait plus joli ! ».
- **Vérification d’abord :** la capture précédait la publication (feuille de style mise en cache 600 s) : sur le code publié, ni puce, ni point orphelin, ni filet. Rien n’a été « recorrigé » à l’aveugle.
- **Vrai cas limite trouvé :** un texte qui *commence* par la ponctuation d’un lien précédent — `Voir <a>la page</a>. Une phrase` — n’avait pas de phrase précédente dans son nœud. La règle n’accroche plus le point à la phrase suivante (« .Une phrase ») : ce nœud n’est plus découpé du tout. Trois cas rejoués dans Chromium.
- **Décision :** le bloc du bas devient une seule colonne centrée (droits, liens légaux, note de version derrière son filet), à toutes les largeurs ; plus aucun filet vertical dans la liste légale ; le repli de la liste sur téléphone est borné à 320 px pour donner toujours trois entrées puis deux.
- **Piège évité :** une première tentative avait supprimé avec le bloc média du pied de page un `@media (max-width: 920px)` entier et laissé 3 px de débordement à 320 px ; bissection CSS / JS, puis retrait du seul bloc devenu inutile. Un `}` orphelin après `forced-colors` a aussi été retiré.
- **Résultat mesuré :** écart de centrage nul sur les trois blocs à 320, 390, 768, 1 024, 1 160, 1 440 et 1 920 px ; aucun débordement à aucune largeur, ni à 130 % de texte, ni sur six autres pages ; aucune puce ni bloc de ponctuation. Le pied de page passe de 377 à **425 px** à 1 440 px (bloc du bas sur trois lignes au lieu de deux) et de 1 035 à 1 038 px à 320 px.
- **Garde-fou :** `controler_pied_de_page` est étendu au centrage, à l’absence de filet vertical et à la borne de repli. **Cinq mutations rejouées, cinq détectées** ; les 13 contrôles d’affichage passent.
- **Essais navigateur :** `test-experience.cjs` à **8/8**.
- **Protocole :** § 6 septies de [`formats-affichage.md`](formats-affichage.md) réécrit ; poids du pire cas ramené à 276,2 Kio mobile et 543,4 Kio grand écran.
- **Limite :** mesure d’un Chromium sans interface ; le rendu des filets reste à constater sur un écran très dense.
- **Prochaine action :** revue visuelle sur téléphone réel, puis décor vectoriel du héros pour `apprendre.html` et l’accueil.

## 2026-10-23 — Le pied de page remis d’aplomb

- **Initiative :** `optimisation-du-site`. Signalement avec capture : « le bas de page est mal présenté, c’est anarchique ».
- **Cause trouvée, mécanique :** ce n’était pas une règle de style mais le script de `site.js` qui met chaque phrase en début de ligne. Il s’appliquait aussi au pied de page et ne savait pas qu’un point peut suivre un lien : « Boussole des savoirs. Une copie… » produisait un fragment « . » seul, affiché en bloc sur sa propre ligne (mesuré à y = 9 852).
- **Décision :** le pied de page sort du périmètre du découpage, et la règle apprend qu’un morceau sans lettre ni chiffre rejoint la phrase précédente — la correction vaut donc aussi pour le contenu principal.
- **Liste légale :** les liens passent en `<ul>` avec séparateur vertical porté par l’élément, qui ne peut pas rester seul en fin de ligne ; sous 520 px la règle s’efface. 97 pages et le générateur `construire-apprentissages.py` sont alignés. Le séparateur de la note de version devient insécable : à 130 % avec espacement renforcé, il commençait la ligne.
- **Composition :** le bloc du bas était un flux (droits à gauche, liens à droite, note se cassant au hasard). Il devient une grille de deux rangées, une colonne sous 1 120 px — seuil mesuré, la mention ne tient sur une ligne qu’à partir de 1 130 px. La colonne « Naviguer », deux fois plus haute que les autres, passe en deux colonnes au-delà de 1 040 px.
- **Résultat mesuré :** une ligne par bloc à partir de 768 px, aucun chevauchement ni débordement de 320 à 1 920 px, y compris à 130 % avec contraste et espacement renforcés. Le pied de page passe de 549 à **377 px** à 1 440 px.
- **Garde-fou :** 13ᵉ contrôle `controler_pied_de_page` (périmètre du découpage, ponctuation rattachée, grille, liste sur les 97 pages). **Quatre mutations rejouées, quatre détectées.**
- **Essais navigateur :** `ouvrirPanneau` devient robuste au clic recouvert par la barre collante du simulateur (bascule au clavier) ; trois passes consécutives à **8/8**.
- **Protocole :** § 6 septies de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** mesure d’un Chromium sans interface ; les filets et séparateurs restent à constater sur un écran très dense.
- **Prochaine action :** revue visuelle sur téléphone réel, puis décor vectoriel du héros pour `apprendre.html` et l’accueil.

## 2026-10-23 — Le panneau « Personnalisation » repris pour la qualité d’affichage

- **Initiative :** `optimisation-du-site`. Retour d’usage après la fusion : « c’est un affichage de haute qualité qu’il faut, pas un truc de basse qualité ».
- **Quatre défauts vus à la capture, aucun à la lecture :** quatre lignes grises interchangeables sans repère et un « Agrandir » centré au milieu de lignes alignées à gauche ; un compteur « 100 % » hérité du blanc de la barre marine, donc **invisible à 1:1** sur le fond blanc ; le texte des cartes de présentation à **4,36:1** sur le fond d’une carte sélectionnée, sous le seuil AA ; un chevron de police (« ⌄ ») dont le dessin variait selon la machine, à côté d’un hamburger SVG.
- **Décision :** les icônes et les chevrons sont des **masques SVG** (`mask:` + `font-size: 0`), une épaisseur de trait unique (2) et une grille de 24 px partagée avec le hamburger. Une icône par ligne, l’habillage des lignes étendu au bouton d’en-tête, filet de séparation, ombre à trois couches et apparition de 160 ms supprimée sous `prefers-reduced-motion`. Le texte des cartes passe à `--text-soft` (**5,58:1**), et le compteur devient un contrôle segmenté `A− · 100 % · A+` de 44 px.
- **Panneaux ouverts remis en page pour 350 px :** parcours en deux colonnes avec l’étape sur sa propre ligne (le « Étape 1/1 » ne se colle plus au bord derrière un filet) ; cartes de présentation à 40 px d’aperçu et rembourrage réduit ; contenu aligné sous le libellé (retrait de 28,6 px).
- **Une piste essayée puis retirée :** replier les descriptions des présentations non choisies sur téléphone. Cela ramenait le panneau de 1 114 à 724 px, mais retirait l’information qui permet de choisir (« Mosaïque », « Panorama composite » ne se devinent pas à leur nom). La liste complète est conservée ; c’est le panneau qui défile, dans son plafond en `dvh`.
- **Garde-fou :** 12ᵉ contrôle `controler_habillage_du_panneau` — masque du chevron avec `font-size: 0`, au moins trois icônes de réglage, couleur propre du compteur, `--text-soft` sur les cartes. **Quatre mutations rejouées, quatre détectées**, fichier restauré à l’identique. L’essai navigateur vérifie que chaque réglage porte un masque non vide ; **8/8**.
- **Résultat mesuré :** les trois panneaux ouverts sur neuf profils de 320 px à 1 440 px — bas toujours dans l’écran (528 ≤ 568 à 320 px, 772 ≤ 780 à 390 px), **0 px de débordement** partout, aucun texte sous son seuil de contraste à 130 % avec contraste renforcé.
- **Coût :** `anglais-aventure.html` passe de 272,1 à **275,1 Kio mobile** en pire cas (542,3 Kio grand écran), toujours au-dessus du budget de 450 assumé pour un appareil sans WebGL.
- **Protocole :** § 6 sexies de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** captures de Chromium sans interface ; le rendu sur téléphone réel, ombres comprises, reste à constater.
- **Prochaine action :** revue visuelle sur téléphone réel, puis décor vectoriel du héros pour `apprendre.html` et l’accueil.

## 2026-10-23 — Deux commandes au lieu de cinq : le panneau « Personnalisation »

- **Initiative :** `optimisation-du-site`. Demande : un second menu regroupe les commandes liées pour ne laisser que deux boutons dans l’en-tête.
- **Décision :** les quatre commandes de réglage (« Agrandir/Réduire », « Parcours », « Affichage », « Présentation ») sont réunies dans un panneau `details` nommé **« Personnalisation »**, créé par `assets/js/site.js` et peuplé par déplacement des blocs existants. L’en-tête compact ne montre plus que « Menu » et « Personnalisation » ; **aucune des 98 pages statiques n’est modifiée**.
- **Défaut de spécificité, trouvé à la mesure :** les règles du panneau, écrites avec deux classes, perdaient contre `html.has-js .site-header.is-compact …` qui en porte cinq : les réglages revenaient côte à côte et un panneau ouvert se posait à **x = 370 px pour une ligne de 350 px**. Les règles sont réécrites `html.has-js .site-header .customize-settings-panel …`, après les règles compactes.
- **Impasse corrigée :** « Agrandir » fermait son propre panneau ; une fois l’en-tête agrandi, « Réduire » devenait inatteignable. Le clic ne ferme plus le panneau, et la bascule est mesurée réversible à 320, 390, 720 et 1 440 px.
- **Échap par étages :** un premier Échap referme le réglage ouvert, un second le panneau, avec retour du focus sur « Personnalisation ». Le drapeau est posé en phase de capture, sinon les réglages se referment avant qu’on puisse savoir qu’ils étaient ouverts.
- **Deuxième impasse corrigée :** une fois les réglages dans un panneau qui défile, leurs panneaux ouverts ne peuvent plus être bornés à l’écran ; le test navigateur exige désormais soit la contenance, soit un conteneur qui défile réellement, au lieu d’exiger les deux.
- **Résultat mesuré (Chromium sans interface, panneau ouvert) :** en-tête **90 px** à 320, 390, 430 et 520 px (contre 110 px avant regroupement), commandes 145/145 à 320 et 180/180 à 390, **32 px** de haut ; panneau de 304 à 504 px de large, bas à 287 px, aucun débordement horizontal ; paysage 844 × 390 : en-tête 49 px, 80 / 151 px ; 768 × 1 024 : 194 px, 92 / 161 px ; 1 280 et 1 440 px : 198 px, 161 px, panneau ancré de 352 px. Quatre lignes de 36 px dans le panneau, à 130 % de texte aussi (379 px de haut à 320 × 568, bas à 499 ≤ 568).
- **Garde-fous :** `controler_panneau_du_menu` exige le panneau créé en JavaScript, le déplacement des **trois** blocs, les lignes préfixées `html.has-js .site-header`, les panneaux imbriqués `position: static`, le panneau ancré et défilant, la grille à deux colonnes et son repli. Cinq mutations rejouées — préfixe de spécificité retiré, `position: static` retiré, `layoutSettings` laissé dans l’en-tête, `overflow: auto` retiré, grille à une colonne — **toutes détectées**, fichiers restaurés.
- **Essais navigateur :** le test de l’en-tête compact est réécrit (il décrivait cinq commandes) ; les autres ouvrent le panneau comme le ferait une personne. **8/8.**
- **Protocole :** § 6 quinquies de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** mesure d’un Chromium sans interface ; le panneau suit `--hauteur-entete`, dont dépend son ancrage.
- **Prochaine action :** revue visuelle sur téléphone réel, puis décor vectoriel du héros pour `apprendre.html` et l’accueil.

## 2026-10-23 — Sur téléphone, les commandes du menu passent à 32 px

- **Initiative :** `optimisation-du-site`. Troisième passage du même jour, sur demande : « modifie la taille des boutons du menu smartphone », précisée « smartphones en mode comprimé ».
- **Périmètre retenu :** les cinq commandes de l’en-tête compact **sur téléphone** (≤ 520 px). Les autres formats compacts — paysage court et tablette compacte — gardent 36 px, et la tablette non compacte ses 44 px.
- **Décision :** `PLANCHER_COMMANDES_ENTETE_PX` passe de 36 à **32 px**, valeur plancher du contrôle : 32 px laisse 10 px au-dessus et au-dessous d’un libellé de 12 px et reste **8 px au-dessus du minimum WCAG** (24 px, 2.5.8). Le plancher de contrôle empêche un retour discret aux 24 px d’origine.
- **Défaut trouvé en route :** la grille `auto-fit` ouvrait trois colonnes à 430 px et quatre à 520 px ; la cinquième commande laissait alors un trou à côté d’« Affichage ». La grille est fixée à **deux colonnes** (`repeat(2, minmax(0, 1fr))`), avec un repli explicite à une colonne sous 300 px — sans lui, deux colonnes de 19 px à 70 px de fenêtre.
- **Résultat mesuré (Chromium sans interface, panneau ouvert) :** en-tête **149 → 122 → 110 px** à 320, 360, 390, 430 et 520 px ; commandes à 32 px ; panneau bas à 537 px pour 568, et toujours sous la ligne de flottaison ; aucun libellé coupé, aucun débordement horizontal, à 100 % comme à 130 % de texte (l’en-tête y mesure 114 à 178 px selon la largeur).
- **Garde-fous :** le contrôle de la grille exige désormais deux colonnes, la dernière commande en pleine largeur (`grid-column: 1 / -1`) **et** le repli à une colonne du palier 300 px. Mutations rejouées : commande à 24 px, commande à 20 px, grille sans repli, dernière commande non pleine largeur — toutes détectées, fichiers restaurés à l’identique. Les essais navigateur passent leurs planchers à 32 px et restent **8/8**.
- **Protocole :** § 6 quater de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** mesure d’un Chromium sans interface ; 32 px reste au-dessus du minimum, mais le rendu n’a pas été revu sur un téléphone réel.
- **Prochaine action :** faire confirmer le rendu sur téléphone réel ; si 32 px est encore trop massif, le palier suivant est 28 px — toujours au-dessus de 24 px.

## 2026-10-23 — Les commandes du menu redescendent à 36 px

- **Initiative :** `optimisation-du-site`. Retour d’usage sur la PR #173 : « il faut réduire pour avoir un entre-deux, là les boutons sont trop gros », capture à l’appui.
- **Mesure du reproche :** à 44 px, la grille de trois rangées portait l’en-tête à **149 px** sur les trois profils de téléphone (320, 390, 430 px), soit près d’un quart de l’écran de 640 px. Les commandes faisaient 141 px de large à 390 px.
- **Décision :** `PLANCHER_COMMANDES_ENTETE_PX` passe de 44 à **36 px**, plus les écarts resserrés (`.3rem` → `.22rem`) et le rembourrage réduit (`.25rem .2rem` → `.18rem .2rem`). À 36 px, le bouton garde 12 px au-dessus et au-dessous d’un libellé de 12 px, et reste **12 px au-dessus du minimum WCAG** (24 px, 2.5.8) : ce n’est pas un retour au plancher qui posait problème.
- **Résultat mesuré (Chromium sans interface, panneau ouvert) :** en-tête de **149 → 122 px** à 320, 390 et 430 px ; commandes à 36 px sur les trois profils et en paysage 844 × 390 (en-tête 51 → 49 px) ; la tablette de 768 px garde ses 44 px, son en-tête n’étant pas compact. Panneau ouvert : bas à 560 px pour 568, 621 px pour 780, 380 px pour 390 — aucun dépassement, aucun libellé coupé, aucun débordement horizontal, à 100 % et 130 % de texte.
- **Garde-fous :** le plancher du contrôle `controler_en_tete_compact` suit (`PLANCHER_COMMANDES_ENTETE_PX = 36`), les trois déclarations de la feuille sont ajustées à la source, et les planchers des essais navigateur (36 px de hauteur, 36 px de largeur) suivent. Un contrôle reste capable de refuser un retour discret aux 24 px d’origine.
- **Contrôles réellement exécutés :** `verifier-affichages.py` (11/11), `test-experience.cjs` (**8/8**), `verifier-integration.py`, plus la matrice de mesure à 320, 390, 430, 844 × 390 et 768 px.
- **Protocole :** § 6 quater de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** mesure d’un Chromium sans interface ; le choix de 36 px est un compromis validé par la mesure, pas par une revue sur appareil réel.
- **Prochaine action :** faire confirmer le rendu sur téléphone réel, puis étendre le décor vectoriel du héros à `apprendre.html` et à l’accueil.

## 2026-10-23 — Le menu du téléphone : quatre défauts mesurés, dont un bloquant

- **Initiative :** `optimisation-du-site`. Demande de revoir « l'affichage des boutons dans le menu en mode smartphone ».
- **Mesure avant :** cinq commandes de **24 px** de haut, empilées en deux ou trois rangées irrégulières (390 px : `Menu` 75×24, `Agrandir` 100×24, `Parcours` 95×24 / `Affichage` 99×24, `Présentation` 123×24) ; en paysage 844 × 390, le panneau descendant à **522 px** sur un écran de 390 px, les derniers liens étaient inatteignables.
- **Défaut bloquant, paysage :** le panneau part de `top: 100%` sous un en-tête collant, sans plafond ni défilement. Il est borné à `calc(100dvh - var(--hauteur-entete))` et rendu défilable. `site.js` publie cette hauteur au chargement puis par `ResizeObserver` : une constante en `rem` laissait encore 47 px de débordement au cran de texte 130 %.
- **Deuxième défaut trouvé au rendu, pas à la lecture :** le panneau défilable gardait `justify-content: center` ; le contenu débordait par le haut et « Accueil » se retrouvait à `y = 10` pour un panneau à 51. Corrigé par `justify-content: safe center` (repli `flex-start`).
- **Troisième défaut :** trois colonnes sous 520 px laissaient 92 px par commande et cassaient les libellés en plein mot (« Parcour / s », « Présent / ation »). Deux colonnes pleines et `overflow-wrap: normal` ; « Présentation » occupe la dernière rangée. À 70 px de fenêtre, la grille `auto-fit` repasse à une colonne et l'en-tête prend toute la largeur, sinon « Agrandir » (43,6 px de texte) débordait d'une colonne de 42,8 px.
- **Quatrième défaut :** le panneau s'arrêtait 16 px avant le bord droit — sa largeur explicite annulait l'étirement par `left`/`right` — et sa gouttière variait de 8 à 24 px selon le palier. La largeur est libérée et la gouttière calculée.
- **Décision de plancher :** `PLANCHER_CIBLE_PX` reste à **24 px** (WCAG 2.2, 2.5.8) pour les liens et les autres cibles ; les cinq commandes de l'en-tête compact reçoivent leur propre plancher, **44 px**, parce qu'elles se touchent au pouce sans visée. Les trois déclarations à 24 px de la feuille sont relevées à la source, pas contournées par une surcharge.
- **Garde-fou :** 11ᵉ contrôle `controler_panneau_du_menu` — défilement interne, plafond `dvh`, centrage `safe`, publication de `--hauteur-entete` (mesure initiale et `ResizeObserver`), grille `auto-fit`, le tout dans une même règle. **Sept mutations rejouées, sept détectées** ; fichiers restaurés à l'identique.
- **Essais navigateur ajustés, pas supprimés :** trois assertions comparaient la largeur d'un bouton entre l'état compact et l'état déployé, ou fixaient la largeur « réservée » à 100 px et `overflow-wrap: anywhere`. Elles décrivaient l'ancienne disposition. Remplacées par des équivalents plus stricts : égalité des deux commandes d'une même rangée, aller-retour compact → déployé → compact qui redonne le même cadre, libellé contenu dans son cadre sur une ligne quand la place suffit. **8/8 essais réussis.**
- **Mesure après, panneau ouvert :** 320, 390, 430 px et paysage 844 × 390 — panneau de 0 à la largeur de l'écran, bas toujours au-dessus de la ligne de flottaison, commandes à 44 px, aucun libellé coupé, aucun débordement horizontal, à 100 % et à 130 %.
- **Protocole :** § 6 quater de [`formats-affichage.md`](formats-affichage.md).
- **Limite :** Chromium sans interface ; aucune revue sur téléphone réel.
- **Prochaine action :** étendre le décor vectoriel du héros à `apprendre.html` et à l'accueil.

## 2026-10-23 — Le héros des Mondes passe de l'image au décor vectoriel

- **Initiative :** `poids-et-sobriete-numerique`. Suite directe du signalement sur la netteté, puis d'une rectification : les trois illustrations ont été créées par l'agent, et le générateur disponible plafonne à **1,06 Mpx** (1 376×768 en 16:9, 1 264×848 en 3:2, mesuré deux fois) — sous le master actuel de 1,57 Mpx, qui contient pourtant plus de détail réel qu'un agrandissement depuis 1 376 px (34,6 dB en aller-retour contre 40,1 dB pour le témoin agrandi).
- **Décision :** la personne responsable du site a écarté « garder l'image » et « régénérer à 1 376 px » au profit d'un **décor 3D vectoriel**, dans le langage des cinq scènes de mission. Vérifié auparavant que la résolution du générateur ne peut pas être poussée : 3:2 comme 16:9 rendent ~1,06 Mpx.
- **Ce qui a été construit :** `assets/js/decor-atlas.js` (15 Kio) — archipel de savoirs : bibliothèque à colonnes et livres-monuments, pont de pierre, observatoire, serre, phare, îlots, récifs. Dessiné une fois par taille, à la densité de l'écran, sans boucle d'animation.
- **Trois défauts trouvés au rendu, pas à la lecture :** (1) un panneau de ciel posé dans le monde laissait voir son arête comme une diagonale et disputait la profondeur aux triangles — le fond est désormais construit pour la caméra et dessiné avant tout, sans test de profondeur ; (2) un champ vertical fixe recadrait les îles latérales en 4:3 et en bandeau — le champ horizontal est figé, le vertical s'en déduit ; (3) le cadrage automatique incluait la mer de 400 unités et les nuages, ce qui reculait la caméra jusqu'à rendre les îles minuscules — le cadrage ne porte plus que sur le décor, et se calcule point par point dans le repère de la caméra.
- **Résultat mesuré (Chromium sans interface, 8 profils) :** tampon **égal au besoin** partout — 1 170×658 pour 1 170×658 à 390 px @3×, 1 672×941 à 1 280 px @2×, 1 024×755 à 1 024 px @1×. Aucun débordement. Le 1:1 n'est plus une limite atteinte, c'est la définition du rendu.
- **Repli :** le `<picture>` reste, mais différé (`data-src`, `data-srcset`). WebGL désactivé → l'image est chargée et correctement choisie sur les 8 profils ; WebGL actif → **aucune requête** vers `mondes-savoirs-hero-*`. Le préchargement de l'image a été retiré.
- **Poids :** `anglais-aventure.html` de 227,6 à **132,9 Kio mobile**. Pire cas, repli compris : 268,3 Kio mobile et **535,5 Kio grand écran**, au-dessus du budget de 450 — assumé et affiché, puisque ce cas ne se produit que sur un appareil sans WebGL. Le compteur ignorait `data-srcset` : il sous-comptait déjà le repli de la scène des missions. Il distingue maintenant transfert typique et pire cas.
- **Garde-fous :** `verifier-affichages.py` passe de 9 à **10** contrôles ; la règle de densité couvre les deux fichiers de rendu. Quatre mutations détectées (plafond à 2 dans `decor-atlas.js`, canvas retiré, `role`/`aria-label` retirés, chargement du repli déplacé). **Deux mutations ne le sont pas** — une sortie après `if (!image) return;`, une condition rendue fausse : le contrôle lit la structure, il n'exécute pas le code. Limite écrite dans le fichier et ici, pas passée sous silence.
- **Limites :** le décor n'a pas le grain d'une illustration peinte ; c'est un changement de style assumé. Aucune revue humaine sur appareil réel. Aucun test Safari ou Firefox : la perte de contexte WebGL est câblée mais n'a pas été provoquée artificiellement.
- **Prochaine action :** faire regarder le héros sur un téléphone et un portable Retina réels, et décider si le même traitement doit s'appliquer à l'illustration de `apprendre.html` et à l'accueil.

## 2026-10-23 — « La version smartphone est pixelisée » : deux causes réelles, une fausse piste

- **Initiative :** `poids-et-sobriete-numerique`. Signalement de la personne responsable du site : « la version smartphone est pixelisée, la qualité des images et du rendu de 3D doit être irréprochable ».
- **Fausse piste écartée par la mesure, pas par le raisonnement.** Une première sonde lisait `naturalWidth` et concluait qu’à 390 px et 3× le navigateur ne servait que 390 px de source pour 1 170 nécessaires. C’est le même artefact que le 22 octobre : pour un `srcset` en `w`, `naturalWidth` est rapporté après correction de densité. En rechargeant le fichier choisi hors `srcset`, **42 profils** (3 pages, 320 px à 2× jusqu’à 2 560 px à 1×) montrent **zéro déficit** : 1 200 px servis pour 1 170 nécessaires à 390 px @3×, 1 672 pour 1 672 à 1 920 px @2×. La géométrie hybride faisait donc ce qu’elle annonçait.
- **Cause réelle n° 1, le décor 3D :** le plafond `min(devicePixelRatio, 2)` survivait et bridait les téléphones à 3×. Tampon mesuré après ouverture d’une mission : **642 × 402 pour 964 × 602 nécessaires** à 390 px @3×, 722 × 452 pour 1 084 × 677 à 430 px @3×, soit 322 et 362 px étirés. `DENSITE_MAX` passe à **4**, `BUDGET_PIXELS` de 4 à **6 Mpx**. Après : **964 × 602 (3,00)**, 1 084 × 677 (3,00), 582 × 364 (2,00), 1 435 × 897 (2,00), zéro déficit. Capturé à 3×, le décor montre des arêtes franches, sans escalier sur les diagonales.
- **Cause réelle n° 2, l’encodage :** l’AVIF était en **qualité 60**. À 800 px, 31,9 dB ; q72 32,8 ; **q78 33,2** ; q82 33,5 (gain imperceptible). À 200 %, q60 fond les rambardes du pont et les feuillages, q78 les tient. Le déficit se voyait **parce que l’image est servie au pixel de l’écran** : un bloc de compression de 8 px se lit alors comme du pixel. Qualités portées à **AVIF 78 / WebP 88**. Le WebP ne monte pas à 90 : en 1 672 px la variante dépasserait son JPEG source (370 Kio), et l’outil refuse — à raison — un dérivé plus lourd que sa source.
- **Poids après la passe :** `anglais-aventure.html` **227,6 Kio** mobile / 415,9 Kio grand écran, `apprendre.html` 202,8 / 391,1, `index.html` 140,4 / 238,7. Les 98 pages restent sous 300 et 450 Kio. Variantes du dépôt : 1 553 → **2 199 Kio**.
- **Garde-fous :** `outils/verifier-affichages.py` passe de 7 à 9 contrôles — `DENSITE_MAX >= 3`, `BUDGET_PIXELS >= 6 Mpx`, aucun `Math.min(devicePixelRatio, N)`, et qualité AVIF ≥ 78 / WebP ≥ 88. Trois mutations rejouées (`DENSITE_MAX = 2`, plafond en dur réintroduit, qualités 60/80) : les trois sont détectées avec la ligne fautive, fichiers restaurés à l’identique (`diff` vide).
- **Effet de bord traité, pas contourné :** neuf variantes changent d’octets, donc le relevé d’en-têtes du 20 octobre ne peut plus être confronté aux fichiers avant publication. Les neuf entrées portent `perime_le = 2026-10-23` et `verifier-fichiers-servis.py` les annonce « relevé périmé, mesure à refaire » : aucun octet n’a été inventé. Sept tests bornent le mécanisme — marqueur manquant sur un binaire modifié, antérieur à la mesure, dans le futur, mal daté, posé sur un texte, ou oublié sur un fichier revenu concordant : tous échouent. Au passage, deux portes que je n’avais pas rejouées échouaient réellement : `verifier-decision-prospective.py` (poids d’Apprendre, 164/314 → 203/391 Kio) et `test_fichiers_servis.py`.
- **Protocole :** § 4.2 quinquies de `poids-et-sobriete-numerique.md`, § 6 bis de `formats-affichage.md`.
- **Limite, énoncée telle quelle :** le master reste 1 672 × 941, donc le mieux atteignable est le 1:1 ; au-delà il n’y a pas de détail à servir, et aucun agrandissement logiciel n’a été fait. Aucune revue humaine sur appareil réel : la mesure est celle d’un Chromium sans interface.
- **Prochaine action :** faire constater la netteté sur un téléphone réel, et déposer le master ≥ 2 880 px (procédure du § 4.2 quater) pour lever le dernier plafond.

## 2026-10-22 — L’échelle de texte relevée, et les petites tailles accrochées à 12 px

- **Initiative :** `poids-et-sobriete-numerique`. Suite directe de la mesure d’affichage : le réglage « texte 50 % » donnait 8 px de corps.
- **Décision :** la personne responsable du site a écarté le statu quo et le simple plancher — qui aurait rendu deux crans identiques — et retenu de **relever l’échelle** : 50/75/100/125/150 % devient **75/85/100/115/130 %**.
- **Migration.** La clé passe de `mrsc-texte-niveau` à `mrsc-texte-cran`, parce que les anciennes valeurs sont ambiguës avec les nouvelles (75 y signifiait « réduit », c’est désormais le minimum). Une table reprend le choix une seule fois : 50 → 75, 75 → 85, 125 → 115, 150 → 130, 100 inchangé, crans indexés 0/1/2 → 100/115/130, ancien réglage binaire → 115 %. Les cinq cas ont été vérifiés dans le navigateur, y compris la réécriture de la nouvelle clé.
- **Simulateur.** Il lit la même clé : sans changement, il serait retombé à 100 % devant une valeur inconnue. Son échelle et sa migration ont été modifiées à l’identique dans `outils/construire-simulateur.py`, et `simulateur/index.html` régénéré.
- **Effet de bord trouvé par la mesure, pas par la lecture :** à 75 %, un `.82rem` vaut 9,84 px. J’ai d’abord cru qu’il suffisait d’accrocher les tailles sous `.8rem` ; la mesure a montré 563 éléments encore sous 12 px. **166 déclarations en `rem`, 3 en `em` et la balise `<small>`** sont donc écrites `max(12px, …)`, sans effet à 100 % ni au-delà. Un dernier `clamp(11px, …)` traînait : relevé.
- **Résultat mesuré :** plus aucun texte sous 12 px sur les 13 pages au cran 75 % ; **1 157 mesures, 0 défaut**, crans 75 et 130 % et six présentations comprises.
- **Garde-fou corrigé deux fois par l’expérience :** le contrôle ignorait `max()` et `clamp()`, puis jugeait un `clamp(2.7rem, …)` comme un plancher à 43 px alors qu’il s’agissait de rem. Il évalue maintenant chaque plancher au cran de texte le plus réduit. Trois mutations — plancher `max()` à 10 px, `clamp` à 10 px, taille en `rem` sans plancher — sont détectées.
- **Prochaine action :** constater les nouveaux crans sur un appareil réel, et vérifier qu’aucun texte ne reste illisible en contraste renforcé au cran 75 %.

## 2026-10-22 — Les formats d’affichage, mesurés dans un navigateur

- **Initiative :** `poids-et-sobriete-numerique`. Demande de la personne utilisatrice : « il faut optimiser les affichages pour tous les formats d’affichage ».
- **Décision de méthode :** ne pas relire le CSS, mais **mesurer**. Un Chromium sans interface a été obtenu dans l’environnement de travail (`@sparticuz/chromium` + `puppeteer-core`, bibliothèques NSS extraites du paquet). C’est la première fois que le rendu de ce site est mesuré, après plusieurs lots où la limite « aucun navigateur n’a été lancé » était explicite.
- **Matrice :** 13 pages × 19 formats d’écran (280 px de pliable à 3 840 px de 4K, densités 1× à 3×, téléphones en paysage) = **247 mesures** ; puis les 6 présentations du site et les 4 réglages (texte 50 à 150 %, contraste, espacement) sur 7 formats = **910 mesures** supplémentaires.
- **Douze défauts réels trouvés, tous corrigés :** défilement latéral jusqu’à **72 px** à 280 px ; titre « Transparence, » de 301 px dans 258 px ; **40 déclarations de texte sous 12 px**, dont l’en-tête compact à 10,9 px avec des commandes de **20 px de haut** ; cibles tactiles à 23,6 px et 17 px ; illustration d’accueil étirée de **1,7×** en paysage, 1,65× sur portable 2×, 1,39× sur tablette 2× ; logo étiré à 3× sur les 13 pages ; héros des mondes à 1,5× en paysage (2 508 px demandés pour 1 672) ; illustration de promotion anglais à 1,46× dans quatre présentations ; défilements de 35 à 117 px au texte 150 % ; mesure de lecture jusqu’à **150 caractères par ligne** ; bouton rogné de 8 px dans une carte.
- **Deux causes structurelles :** les pistes de grille écrites `1fr` (soit `minmax(auto, 1fr)`) laissent la largeur minimale du contenu élargir la colonne — dix occurrences corrigées en `minmax(0, 1fr)` ; et `overflow-wrap: break-word`, posé sur les titres, ne réduit pas cette largeur minimale, contrairement à `anywhere`, ce qui laissait la césure sans effet sur la mise en page.
- **Reproche à moi-même :** ma première détection d’image agrandie était fausse — `naturalWidth` est corrigé par la densité dès qu’un `srcset` en `w` est présent. La comparaison juste se fait avec la largeur réelle du fichier, lue sur le disque. Sept faux positifs ont été éliminés avant de conclure quoi que ce soit.
- **Résultat mesuré :** **0 défaut sur les 247 mesures** écran, **0 sur les six présentations × sept formats**, **0 au texte 150 % × sept formats**. Seul le réglage « texte 50 % » laisse du texte à 8 px : c’est la définition du réglage, pas un défaut de mise en page ; les commandes y gardent 24 px.
- **Garde-fou :** `outils/verifier-affichages.py` (7 contrôles) dans la CI, puisqu’un navigateur n’y est pas disponible. Sept mutations volontaires — texte à `.72rem`, contact à 23 px, en-tête compact ramené à zéro sous deux formes, palier de densité supprimé, piste `1fr` rétablie, plafond du héros supprimé — toutes détectées. Deux failles du contrôle ont été trouvées par ces mutations : il ignorait `!important` et `min-height: 0` écrit sans unité. Corrigées, puis remutées.
- **Protocole et limites :** `docs/rd/formats-affichage.md`. Les formats sont émulés ; aucun appareil physique, aucune police réelle de l’appareil, et le zoom est approché par une fenêtre plus étroite.
- **Prochaine action :** constater sur un téléphone et un portable Retina réels la bascule en panneau de l’illustration d’accueil, demander si le réglage « texte 50 % » doit être relevé (8 px de corps), et rejouer `outils/auditer-affichages.mjs` après tout changement de feuille de style.

## 2026-10-22 — Une porte de CI dépendait d’un binaire absent

- **Initiative :** `optimisation-du-site`. La CI a rejeté le lot sur l’étape « Vérifier le manifeste des variantes d’images », alors que la même commande passait en local sur le même commit.
- **Cause, établie par expérience :** la vérification du manifeste lisait les dimensions des sources avec ImageMagick, que le runner n’installe pas. L’ancien script, relancé sans cet outil, lève `RuntimeError: ImageMagick est requis pour mesurer les variantes générées`. La génération a besoin d’ImageMagick ; la **vérification**, non : elle ne fait que confronter des fichiers à un manifeste.
- **Correctif :** les dimensions se lisent désormais dans l’en-tête du fichier pour JPEG, PNG et WebP ; ImageMagick ne sert plus que de repli, pour un format non reconnu et pour l’encodage. La lecture produit les mêmes valeurs que l’outil externe sur les 14 fichiers non AVIF du dossier d’images ; les 7 AVIF ne sont pas décodés à la main et passent par le repli.
- **Garde-fou :** `outils/test_manifeste_sans_imagemagick.py`, six tests, exécuté dans la même étape de CI. Il vérifie aussi le plafonnement des variantes à la largeur native et que les paliers 2 560 et 2 880 px apparaissent quand la source les permet. Mutation de contrôle — rétablir la dépendance à ImageMagick — détectée, trois erreurs, puis restauration vérifiée.
- **Défaut de diagnostic corrigé au passage :** l’échec ne remontait que « exit code 1 », sans le message du script. L’étape relaie maintenant les lignes fautives en annotations `::error`, comme le fait déjà l’étape des fiches d’apprentissage. C’est ce qui manquait pour identifier le problème sans rejouer la CI à l’aveugle.
- **Contrôles réellement exécutés :** les 21 étapes de `verification.yml` — 32 commandes `python3` — rejouées en local, 0 échec ; `optimiser-images.py --verifier` avec et sans ImageMagick ; les six nouveaux tests avec et sans ImageMagick ; une mutation ; `git diff --check`.
- **Rectification de décompte :** les entrées précédentes annonçaient « 33 étapes de `verification.yml` ». Le workflow compte **21 étapes**, dont 31 commandes `python3` avant ce lot et 32 après. Le chiffre de 33 venait du découpage du script de rejeu local, pas du workflow. Le décompte utile est celui des commandes.
- **Limite :** la cause a été reproduite localement en retirant ImageMagick du `PATH`, pas observée sur le runner lui-même, dont les journaux ne sont pas téléchargeables depuis cet environnement. La correction est donc validée par équivalence d’environnement, pas par lecture du journal de la CI.

## 2026-10-22 — Géométrie hybride du héros et pipeline prêt pour un master plus large

- **Initiatives :** `poids-et-sobriete-numerique` et `optimisation-du-site`. Suite du signalement sur la netteté des illustrations ; la géométrie hybride est retenue. **[Rectifié le 23 octobre 2026]** Cette entrée disait que « la personne utilisatrice fournira un master d’au moins 2 880 px » : c’est faux — les trois illustrations ont été créées par l’agent, de A à Z, et aucun master externe n’existe ni n’est attendu. La géométrie hybride reste juste, pour la raison correcte : ne jamais agrandir le fichier de 1 672 px existant.
- **Mesure qui a orienté la décision :** le générateur d’images disponible ici plafonne à environ **1,05 million de pixels** quel que soit le format demandé — 1 376×768 en 16:9, 1 024×1 024 en carré. Le master actuel (1 672×941, 1 573 000 px) est donc **33 % plus grand** qu’une régénération possible : refaire les images aurait dégradé le site. La régénération est écartée, sur preuve et non par préférence.
- **Décision de conception :** géométrie **hybride**. Le plein cadre est conservé là où il n’étire rien — sous 1 680 px en 1×, et sous 700 px en bandeau. Il devient **panneau contenu** sur les écrans denses (2× et plus, plafond 836 px = la moitié du master) et au-delà de 1 680 px en 1× (plafond 1 672 px). Le texte passe alors dessous, sur le fond bleu nuit.
- **Résultat vérifié :** **aucun agrandissement** sur les **17 combinaisons écran × densité** testées, de 320 px à 3× à 2 560 px à 1× ; la plus grande source requise est de 1 672 px pour 1 672 px servis. L’agrandissement de 1,72× qui subsistait sur Retina est supprimé.
- **Pipeline préparé pour un master plus large, si un jour il existe :** `outils/optimiser-images.py` ne produit plus jamais de variante plus large que sa source — une telle variante n’ajoute aucun détail. Il produit désormais automatiquement la largeur native et les paliers utiles (2 560 et 2 880 px) quand la source les permet. Déposer un master de 2 880 px puis lancer `python3 outils/optimiser-images.py` suffira à créer les variantes manquantes, sans toucher au code.
- **Trois garde-fous ajoutés dans `verifier-budgets-visuels.py` :** les valeurs de panneau (`--hero-art-max`) doivent exister **et** être appliquées par une règle `.adventure-hero-art` portant `max-width` et `position: static` ; aucun palier de la matrice ne peut réclamer plus que la variante la plus large servie ; et une variante présente sur le disque mais absente des `srcset` fait échouer la porte, pour que l’arrivée du master ne passe pas inaperçue.
- **Défaut trouvé pendant ce lot :** la première version du contrôle vérifiait les valeurs `--hero-art-max` sans vérifier que la règle les applique. La mutation « retirer `max-width` » passait donc au vert alors que l’image redevenait pleine largeur. Corrigé, puis rejoué : la mutation échoue désormais avec le bon message.
- **Contrôles réellement exécutés :** les 33 étapes de `verification.yml` en local ; `optimiser-images.py --verifier` (3 sources, 1 553,4 Kio dérivés, manifeste cohérent, inchangé) ; quatre mutations volontaires — panneau dense supprimé, panneau élargi à 900 px, `max-width` retirée, variante 2 560 px simulée sur le disque — toutes détectées, chacune suivie d’une restauration vérifiée.
- **Limites :** aucun navigateur n’a été lancé. La géométrie hybride est vérifiée par calcul et lecture du CSS, jamais par rendu : le passage du plein cadre au panneau à 2× et la répartition texte/image n’ont été vus par personne. Le seuil de 1 680 px en 1× est un choix, pas une mesure d’écran réelle.
- **Prochaine action :** constater la géométrie hybride sur un portable Retina réel et sur téléphone. **[Rectifié le 23 octobre 2026]** Il n’y a pas de master à recevoir : le générateur plafonne à 1,06 Mpx, sous le fichier existant de 1,57 Mpx. Voir § 4.2 quater de `poids-et-sobriete-numerique.md`.

## 2026-10-22 — Le héros des mondes était étiré, pas compressé

- **Initiatives :** `poids-et-sobriete-numerique` et `optimisation-du-site`. Troisième signalement du même jour sur les illustrations : « revois les images qui ne sont au bon ratio, il ne faut pas voir les pixels ».
- **Contrôle préalable :** tous les `width`/`height` déclarés correspondent aux fichiers réels — aucun ratio déclaré n’était faux. Le défaut n’était donc pas dans le HTML mais dans la géométrie CSS.
- **Le calcul qui tranche :** le héros imposait `object-fit: cover` dans une boîte de 150 à 180vw de haut. Remplir cette boîte demande **3 742 px** de source à 390 px en 3× et **4 126 px** à 430 px en 3×. Aucune variante ne pouvait suivre : l’agrandissement atteignait **3,1×**. Le lot précédent avait corrigé la déclaration `sizes` ; c’était nécessaire mais insuffisant, puisque même la variante 1 672 px restait trop petite pour cette géométrie.
- **Décision de conception :** sous 700 px, le héros devient un **bandeau au ratio naturel** de l’illustration (16/9), texte dessous sur le fond bleu nuit, voile supprimé. La source nécessaire retombe à la largeur de l’écran : 960 à 1 290 px selon les paliers, tous couverts par les variantes existantes. **Aucun agrandissement** ne subsiste sur les cinq largeurs de téléphone testées.
- **Déclaration `sizes` ramenée à la vérité :** `100vw` partout, l’ancienne valeur `150vw` n’ayant plus d’objet. Aucune sous-déclaration ne peut donc plus faire choisir une variante trop petite.
- **Coût mesuré :** inchangé sur les téléphones courants (variante 1 200 px, page ≈ 240 Kio) ; les très grands téléphones à 3× (430 px) passent à 1 672 px, soit ≈ 322 Kio, au-dessus du budget de 300 Kio — conséquence assumée et chiffrée, pas subie.
- **Garde-fou ajouté dans `verifier-budgets-visuels.py` :** quatre vérifications — bandeau mobile effectif (`position: static`, `height: auto`, voile masqué, `min-height: 0` aux deux paliers), `sizes` exact, aucun palier de téléphone ne réclamant plus que la plus grande variante servie, et facteurs de grand écran plafonnés aux valeurs constatées. Trois mutations volontaires (retour au `cover`, boîte à 180vw rétablie, variante 1 672 px retirée) ont été détectées avec un message nommant la cause.
- **Ce qui reste et ne se règle pas ici :** sur grand écran le héros reste plein cadre, donc la source nécessaire vaut la largeur de l’écran en pixels d’appareil. Agrandissement résiduel **1,15× à 1 920 px (1×)**, **1,53× à 1 024 px (2×)**, **1,72× à 1 440 px (2×)**. Il faudrait une illustration d’au moins **2 880 px** de large. Un agrandissement Lanczos a été écarté : fichier plus lourd, aucun détail créé.
- **Contrôles réellement exécutés :** les 33 étapes de `verification.yml` en local, 0 échec ; `verifier-budgets-visuels.py` (4 contrôles) ; trois mutations suivies d’une restauration vérifiée par `git diff --stat` ; `git diff --check`.
- **Limites :** aucun navigateur n’a été lancé. La géométrie est vérifiée par calcul et lecture du CSS, jamais par rendu. Le bandeau mobile change la composition et n’a été vu par personne : c’est le premier point à regarder sur téléphone réel, avec le haut du bandeau et le passage du voile au fond uni.
- **Prochaine action :** faire constater le bandeau sur un téléphone réel. **[Rectifié le 23 octobre 2026]** « Obtenir de l’association une illustration d’au moins 2 880 px » était une fausse piste : l’illustration est un travail de l’agent, et le générateur disponible ne dépasse pas 1,06 Mpx. L’agrandissement sur grand écran a depuis été supprimé par la géométrie hybride, sans nouvelle illustration.

## 2026-10-22 — La netteté des mondes tenait au choix de variante, pas à la compression

- **Initiatives :** `poids-et-sobriete-numerique` (P1) et `optimisation-du-site`. Signalement de la personne utilisatrice : « les images sur les mondes sont de très mauvaises qualités il faut revoir cela ».
- **Deux fausses pistes écartées par la mesure, avant d’agir.** La compression n’était pas en cause : l’AVIF q60 du héros mesure 36,4 dB de PSNR en sRGB, conformément à ce que la note de sobriété documentait déjà (le calcul direct à 12,7 dB est l’artefact YCbCr déjà connu). La régénération ne pouvait pas aider non plus : le générateur d’images disponible ici rend du 1 376 × 768, soit moins que le master de 1 672 × 941 — régénérer aurait dégradé la résolution.
- **Défaut 1, dans la déclaration `sizes`.** Le héros des mondes imposait `object-fit: cover` dans une boîte de 180vw de haut, donc une image mise en page sur ≈ 1 247 px de large pour un téléphone de 390 px, pendant que `sizes="100vw"` annonçait 390 px. Le navigateur choisissait la variante 800 px, agrandie ≈ 3,1× en pixels d’appareil. La déclaration devient `(max-width: 430px) 150vw, (max-width: 700px) 105vw, 100vw` : la variante 1 200 px est choisie, l’agrandissement tombe à ≈ 2,1×.
- **Défaut 2, dans le rendu 3D.** Le canvas des cinq missions plafonnait `devicePixelRatio` à 1,5, puis le CSS l’agrandissait sur tout écran à 2× ou 3× : arêtes floues sur les appareils les plus denses. Le plafond passe à 2, borné par un budget de 4 Mpx ; le rendu n’a lieu qu’une fois par monde, le coût reste ponctuel.
- **Compromis de poids explicite.** La déclaration honnête serait ≈ 320vw ; elle aurait fait choisir la variante 1 672 px et porté la page à ≈ 322 Kio de mobile, au-dessus du budget de 300 Kio. 150vw garde ≈ 240 Kio mesurés par gzip sur les fichiers réellement choisis, en abandonnant une part du gain.
- **Ce que cela ne règle pas.** Le master reste 1 672 × 941 : sur un écran à 2× il est affiché sur jusqu’à 2 880 px d’appareil, soit 1,7× d’agrandissement résiduel. Il faudrait une source de 2 560 à 2 880 px. Un agrandissement Lanczos produit un fichier plus gros, pas une image plus nette : il n’a pas été retenu et ne doit pas être présenté comme un progrès.
- **Défaut annexe relevé :** `verifier-poids-pages.py` annonce retenir le candidat « selon `sizes` » mais ne lit pas cet attribut ; ses chiffres sont des majorants, pas le choix réel du navigateur. Le calcul de poids de ce lot a donc été refait à la main, mêmes fichiers, gzip niveau 9.
- **Contrôles réellement exécutés :** `node` sur `assets/js/anglais-aventure.js` (syntaxe) ; `python3 outils/verifier-poids-pages.py` ; reprise intégrale des 33 étapes de `verification.yml` en local, 0 échec ; calcul gzip manuel des trois scénarios de variante.
- **Limites :** aucun navigateur n’a été lancé : ni confirmation que la variante 1 200 px est bien celle retenue à l’exécution, ni rendu du canvas à 2×, ni comparaison avant/après à l’œil. Les facteurs d’agrandissement sont des calculs de mise en page, pas des mesures d’écran. La netteté sur Retina reste insuffisante par construction.
- **Prochaine action :** faire confirmer sur un téléphone réel et sur un portable Retina que le gain est perceptible. **[Rectifié le 23 octobre 2026]** « Demander à l’association une illustration d’au moins 2 560 px » était une fausse piste : l’illustration est un travail de l’agent, et le générateur disponible ne dépasse pas 1,06 Mpx. Décider ensuite si `verifier-poids-pages.py` doit lire `sizes` ou cesser de l’annoncer.

## 2026-10-22 — Les sorties commitées ne dépendent plus du calendrier

- **Initiatives :** `optimisation-du-site` (P1) et `coordination-de-tous-les-agents`. Demande de la personne utilisatrice : « règle ces points de manière à ne pas avoir de problème par la suite », après deux points laissés ouverts — une dérive horodatée qui cassait la publication, et l'absence de toute validation visuelle.
- **Panne corrigée à la racine :** `docs/rd/avancees.md` et `docs/apprentissage/audit-automatique.md` portaient la date du jour de leur génération. Comparées octet par octet par les portes CI, elles divergeaient dès le lendemain alors qu'aucun contenu n'avait changé ; régénérer réparait le jour même et re-cassait le suivant. La PR #166 avait traité le symptôme (régénération), pas la cause.
- **Décision de conception :** l'horodatage d'une sortie commitée vient désormais d'une donnée du dépôt — `meta.derniere_revue` pour les avancées, la plus récente `revue_le` du catalogue pour l'audit — et non de `date.today()`. La validation, elle, continue de juger les dates au jour réel : une date de revue ou de droits dans le futur reste une erreur. Deux fonctions `date_de_reference()` portent cette règle et sont reprises par `verifier-rd-continue.py`, qui régénère les mêmes sorties pour les comparer.
- **Défaut latent trouvé en chemin :** `outils/construire-simulateur.py` finissait par une ligne morte `it(main())` après `raise SystemExit(main())`. Invisible en CI, puisque jamais atteinte au lancement direct ; elle faisait échouer toute importation du module, donc tout contrôle qui l'aurait rejoué en processus. Supprimée.
- **Second défaut latent :** trois contrôles d'identité de type exacte (`type(date_plan) is date`) rendaient `construire-apprentissages.py` impossible à éprouver sous une horloge déplacée, et signalaient de faux défauts. Remplacés par `isinstance`, seul cas du dépôt.
- **Garde-fou ajouté :** `outils/test_reproductibilite_artefacts.py` rejoue les dix portes CI qui comparent un fichier généré, avec une horloge déplacée de +37 puis +400 jours. +400 franchit la prochaine échéance de revue d'une fiche (2027-01-09) et l'échéance du portefeuille. Un test de mutation sur un générateur volontairement fautif prouve que ce harnais détecte bien une horodatage sur le jour ; il ne peut donc pas passer à tort.
- **Second garde-fou :** `outils/verifier-budgets-visuels.py` mesure ce qu'aucune porte ne voyait — longueur des `<title>` (60 caractères, avec l'exception nommée de l'accueil à 73 et la raison de l'accord), plafonds de non-régression du H1 de l'accueil, estimation des lignes à 320 px et en grand écran à partir des valeurs réellement lues dans `site.css`, et couverture de `.home-hero-facts` en contraste renforcé, couleurs forcées et lecture.
- **Mesure corrigée :** le H1 de l'accueil mesure **63** caractères, et non 62 comme l'indiquait l'entrée précédente — le point final compte. Le titre de page reste à 73 caractères.
- **Contrôles réellement exécutés :** `py_compile` sur tout `outils/` ; trois mutations du vérificateur visuel (titre de page allongé, H1 allongé, `.home-hero-facts` retiré du contraste renforcé), chacune détectée et nommée, suivie d'une restauration vérifiée ; sonde complète des dix portes à +0, +37 et +400 jours, toutes vertes ; `test_avancees.py` (15 tests), `test_audit_prototypes.py` (30 tests), `test_reproductibilite_artefacts.py` (4 tests) ; `verifier-rd-continue.py` (36 OK, 0 échec) ; reprise intégrale des étapes de `verification.yml` en local.
- **Limites :** l'estimation du H1 donne **6 lignes à 320 px pour un plafond de 6** — le titre est au ras de son budget sur écran étroit, là où le précédent en occupait environ 4. Ce chiffre est une estimation (avance moyenne de 0,5 em, police système supposée), jamais un rendu. Aucun navigateur n'a été lancé : ni crénage, ni césure, ni zoom texte, ni lecteur d'écran. Le budget de 60 caractères pour un titre est un repère de travail, pas une règle de moteur de recherche.
- **Prochaine action :** observer le H1 et les repères chiffrés à 320 px dans un navigateur réel et dans les six présentations, puis décider soit de raccourcir le H1 sur écran étroit (variante mobile plus courte, jamais une réduction de la police sous le plancher d'accessibilité), soit d'assumer six lignes en le consignant. Étendre la règle d'horodatage au prochain générateur ajouté.

## 2026-10-22 — Le titre de l’accueil nomme trois verbes au lieu d’une intention

- **Initiative :** `coherence-textes-publics` (P1). Second lot du même jour, après la réécriture de l’ouverture (PR #166, fusionnée dans `main` en `3725288`).
- **Décision de la personne utilisatrice :** entre quatre variantes qui lui ont été proposées, elle retient « Apprendre, vérifier et débattre des sujets qui nous concernent. », demande de la propager au titre de page, au partage et aux données structurées, puis de chasser les doublons. Le titre précédent était le repère éditorial approuvé et son remplacement figurait dans les options écartées du lot précédent : il est levé ici par une demande explicite, pas par une préférence d’agent.
- **Pourquoi ces trois verbes tiennent :** chacun correspond à une ressource réellement présente — apprendre (les 84 fiches du catalogue), vérifier (les sources affichées page à page, les documents officiels, la page Transparence), débattre (le dossier IA & société et le simulateur, qui compare des arbitrages sans prédire). Aucun des trois n’annonce un service rendu à la place de la personne, ni une position votée de l’association.
- **Propagation :** `<title>`, `og:title`, `WebSite.name` et `WebPage.name` du JSON-LD portent la même chaîne, préfixée de « M.R.S.C. — » (73 caractères). Le H1 conserve l’accent coloré sur sa seconde moitié (`<span>des sujets qui nous concernent.</span>`).
- **Doublons retirés :** la phrase d’ouverture répétait « les sujets de société » juste après le H1 (elle dit désormais « rendre ces sujets compréhensibles ») ; le titre de la section « Ressources et outils » reprenait les trois verbes (« Apprendre, s’informer ou tester une idée. » devient « Les ressources en détail. »).
- **Contrôle ajouté :** `verifier-integration.py` exige la nouvelle formule à la place du terme verrouillé « Comprendre les sujets », et vérifie que le titre, `og:title` et les deux `name` du JSON-LD sont exactement égaux et contiennent le texte du H1 (balises retirées, point final ôté). Son détail d’échec nomme la pièce désalignée : la première version annonçait « alignés » tout en échouant, défaut trouvé en éprouvant le contrôle.
- **Mise en page :** aucune règle CSS modifiée. La largeur utile vient de la colonne du hero, pas de `max-width: 20ch` ; le titre passe de 42 à 62 caractères, soit environ une ligne de plus en grand écran. Le mot le plus long (« concernent. ») était déjà présent dans le titre précédent, ce qui ne change pas le risque de débordement à 320 px documenté dans la feuille de cohérence.
- **Contrôles réellement exécutés :** deux mutations volontaires (`og:title`, puis `WebPage.name` du JSON-LD) pour vérifier que le contrôle échoue et nomme la pièce en cause, chaque fois suivies d’une restauration vérifiée par `git diff --stat` ; `python3 -m py_compile outils/verifier-integration.py` ; reprise intégrale des 31 étapes de `.github/workflows/verification.yml` en local ; `git diff --check`.
- **Limites :** aucun rendu dans un navigateur réel, aucun essai à 320, 375, 768, 1024 et 1440 px, en contraste renforcé, couleurs forcées, dans les six présentations ni au lecteur d’écran ; aucune mesure de compréhension par une personne. Le titre de page fait 73 caractères, au-delà de ce que les moteurs de recherche affichent en général sans troncature : l’arbitrage entre cohérence H1/titre et longueur affichée n’est pas tranché par une personne. Le contrôle ajouté vérifie une égalité de chaînes, jamais la pertinence de la formule.
- **Prochaine action :** faire relire la formule par une personne de l’association ; observer le H1 sur quatre lignes en grand écran et à 320 px dans les six présentations ; décider si le titre de page doit être raccourci pour l’affichage en résultats de recherche, auquel cas le contrôle d’alignement devra accepter une formule raccourcie cohérente plutôt qu’une égalité stricte.

## 2026-10-22 — L’ouverture de l’accueil nomme ce qu’elle contient

- **Initiative :** `coherence-textes-publics` (P1).
- **Signal reçu :** la personne utilisatrice juge la présentation du site « évasive » et « pas claire » : « Le M.R.S.C. est une association. Sur ce site, vous trouverez des fiches, un dossier sur l’intelligence artificielle et un simulateur. », puis « Choisissez ce qui vous intéresse. Aucun parcours n’est imposé. » Un inventaire sans objet, sans échelle ni règle de preuve, et une formule de liberté dite trois fois sur la même page (ouverture, encadré « Par où commencer ? », section « Ressources et outils »).
- **Décision de conception :** l’ouverture répond à quatre questions vérifiables — qui publie (une association qui met en commun les expériences, les compétences et les savoir-faire de ses membres, selon ses statuts), ce que chaque ressource permet de faire (apprendre une notion ; séparer les usages documentés de l’IA des questions à débattre ; comparer les effets de décisions de politique publique), quelle est l’échelle réelle (repères chiffrés `home-hero-facts`) et quelle est la règle de preuve (chaque page indique ses sources, ses limites et son statut ; le simulateur ne prédit rien). Le détail de chaque ressource reste dans l’encadré « Par où commencer ? », pour ne pas dire deux fois la même chose ; l’absence de parcours imposé n’y est plus dite qu’une fois, avec l’absence de compte.
- **Repères chiffrés, jamais recopiés :** 84 fiches dans 15 domaines, dont 26 du corpus initial et 58 prototypes « à relire » au 22 octobre 2026 (`docs/apprentissage/catalogue.toml`, `referentiel.toml`) ; plus de 100 leviers, 5 échelons et 20 domaines d’impact (moteur : 101 leviers, `LIBELLES_STRATES`, `DOMAINES`) ; 0 compte, abonnement ou mesure d’audience (notice `confidentialite.html`).
- **Options écartées :** remplacer le titre « Comprendre les sujets qui nous concernent. », repère éditorial approuvé ; détailler en ouverture les 11 scénarios ou les 52 indicateurs du simulateur, qui appartiennent à `simulateur.html` ; écrire « 26 fiches relues », la relecture indépendante du corpus initial n’étant pas garantie ; annoncer une couverture exhaustive des sujets.
- **Changements :** `index.html` (ouverture, encadré d’entrée, phrase de la section « Ressources et outils », description meta et JSON-LD, ligne de traçabilité sur l’origine des nombres), `assets/css/site.css` (composant `home-hero-facts` avec ses variantes contraste renforcé, couleurs forcées et présentation « Lecture »), `outils/verifier-integration.py` (contrôle des formulations concrètes et de l’absence des formules évasives, nouvelle fonction `chiffres_accueil_coherents`).
- **Contrôles réellement exécutés :** `python3 -m py_compile outils/verifier-integration.py`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-integration.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-poids-pages.py` (accueil : 110,4 Kio mobile, 172,3 Kio grand écran, sous les budgets de travail) ; serveur local lancé et `index.html` servi en HTTP 200 ; puis, après rebasage sur `main` et régénération des deux sorties horodatées, reprise intégrale des 31 étapes de la porte `verification.yml` en local (0 échec). Les quatre contrôles d’ouverture, dont les trois nouveaux, passent. Le rebasage sur `main` après la fusion de la PR #165 a fait échouer le contrôle des fiches (catalogue passé de 83 à 84 entrées, 57 à 58 prototypes) : les repères de l’ouverture ont été recalés sur le catalogue, ce qui est exactement l’effet recherché par ce contrôle.
- **Dérive préexistante traitée à part :** `verifier-rd-continue.py` échouait déjà sur `origin/main` (2b5848d) pour deux sorties à régénérer (`docs/rd/avancees.md` via `construire-avancees.py`, `docs/apprentissage/audit-automatique.md` via `auditer-prototypes.py`), et cet échec bloquait aussi le workflow de publication. Le `diff` de ces deux fichiers ne portait que sur leur ligne de date : les générateurs horodatent leur sortie au jour courant et les contrôles `--verifier` la comparent octet par octet, donc toute sortie générée un jour donné échoue dès le lendemain. Les deux fichiers ont été régénérés dans un commit distinct de ce lot éditorial, sans aucun changement de contenu. La cause structurelle reste ouverte : rendre la comparaison indifférente à la ligne de date, ou horodater la sortie depuis la date du registre, appartient aux initiatives propriétaires de ces outils.
- **Limites :** aucun rendu dans un navigateur réel, aucun essai clavier, zoom, contraste renforcé, couleurs forcées, lecteur d’écran ni présentation alternative sur la nouvelle ouverture, et aucune mesure de compréhension par une personne. Les contrôles ajoutés vérifient la présence des formulations et l’accord des nombres avec les registres, pas leur clarté réelle. L’affirmation « aucune mesure d’audience » dépend de la notice vie privée et de sa réserve : le constat doit être refait si un service, un script ou une intégration externe est ajouté.
- **Prochaine action :** faire relire l’ouverture par une personne de l’association et la faire lire à une personne qui découvre le site ; vérifier le rendu de `home-hero-facts` à 320, 375, 768, 1024 et 1440 px, en contraste renforcé, couleurs forcées et dans les six présentations ; traiter les deux sorties à régénérer dans leur propre initiative.

## 2026-10-20 — Premier prototype pour les systèmes embarqués, carte du sujet sécurité des produits et septième refus

- **Initiatives :** `cartographier-les-lacunes` (P1), `relire-les-44-prototypes` (P0), `confronter-une-affirmation-a-sa-source` (P0), `sources-fermees-et-registre-des-refus` (P1) et `prospective-apprentissages-2030` (P1), après fusion des PR #163 et #164 sur `main`.
- **Le sujet `systemes-embarques` passe de `a-creer` à `partiel` avec un premier prototype (`83 → 84 fiches`, `57 → 58 prototypes`, `18 → 17 sujets sans fiche`) :**
  - création de la fiche `info-objet-connecte-local-distant` (*Distinguer programme embarqué local et liaison réseau d'un objet connecté*) dans `docs/apprentissage/catalogue.toml`, rattachée à `informatique-programmation` → `systemes-embarques` dans `docs/apprentissage/referentiel.toml` ;
  - adossée aux trois sources primaires ouvertes et lues le 20 octobre 2026 dans `docs/rd/sujet-systemes-embarques.md` : programme de SNT de seconde (`eduscol.education.fr/document/23494/download`), activité pédagogique Éduscol (`eduscol.education.fr/document/23560/download`) et guide `ANSSI-PA-087` (*Recommandations relatives à la sécurité des (systèmes d')objets connectés*, Licence Ouverte v2.0) ;
  - vérification phrase par phrase de non-duplication avec `tech-electronique-capteur` : la fiche porte sur le partage entre exécution locale du programme embarqué, interface homme-machine (sur l'objet ou déportée) et liaison réseau, ainsi que sur ce qui continue ou s'arrête lors d'une coupure d'Internet ;
  - 17/17 contrôles mécaniques `ok` dans `auditer-prototypes.py` et **0 violation axe-core 4.14.0** sur les **99 pages HTML × 2 largeurs** (`198` exécutions de `verifier-accessibilite.cjs --etendu`).
- **Ouverture d'une troisième carte de sujet (`docs/rd/sujet-securite-sciences.md`) :** ouverture de `sciences-techniques-environnement` → `securite-sciences` (*Risques, consignes et usages sûrs des outils et produits*, maintenu à `statut = a-creer`) à partir de trois sources institutionnelles ouvertes et lues le 20 octobre 2026 : le dossier INRS sur le système d'étiquetage CLP (`règlement (CE) n° 1272/2008` : 9 pictogrammes `SGH01`–`SGH09`, mentions `DANGER`/`ATTENTION`, mentions `H`/`EUH`, conseils `P`, identifiant `UFI`), l'actualité INRS sur le règlement délégué `(UE) 2023/707` (nouvelles classes de danger pour perturbateurs endocriniens, `PBT`/`vPvB` et `PMT`/`vPvM`, obligatoires au plus tard le 1er mai 2025 pour les substances et le 1er mai 2026 pour les mélanges, **sans pictogramme associé à ce jour**), et le programme de sciences et technologie du cycle 3 (BO n° 25 du 22 juin 2023). La carte fixe la frontière stricte avec `premiers-secours` et `securite-electricite` (`revue-experte`).
- **Septième refus consigné (`extraction-incomplete`) et neuvième sonde de confrontation :**
  - ajout de la catégorie `extraction-incomplete` dans `outils/construire-sources-refusees.py` (10 tests unitaires dans `outils/test_sources_refusees.py`) et enregistrement dans `docs/apprentissage/sources-refusees.toml` du référentiel professionnel Éduscol `h092c.pdf` pour `arts-composer-formes` : le PDF de 70 pages est tronqué à la page 30 avant d'atteindre le tableau `S 2.4 – Composition texte/image, mise en page(s)`. Refuser de citer un tableau non lu directement maintient volontairement `arts-composer-formes` comme unique constat (`1 constat`) ;
  - ajout d'une 9e sonde dans `docs/rd/confrontations-sources.toml` (`objet-connecte-local-distant-snt-23494`) et d'une 10e avancée réutilisable dans `docs/rd/avancees.toml` (`carte-de-sujet-avant-premiere-fiche`).
- **Prochaine action :** faire relire `info-objet-connecte-local-distant` par une personne compétente en informatique ou systèmes embarqués, décider s'il faut rédiger une première fiche prototype sur la lecture complète d'une étiquette CLP (`securite-sciences`), et trancher le constat restant sur `arts-composer-formes`.

## 2026-10-20 — Une convocation courte, sans le dossier entier

- **Initiative :** `vote-distanciel-verifiable` (P0). Suite directe du dossier de délibération fusionné par la PR #162.
- **Besoin de départ, non inventé :** le dossier fait douze sections ; le faire lire intégralement avant une séance décourage, et une convocation qui demande une heure de lecture la veille ne fait venir personne. Il fallait donc un document de préparation séparé, court, sans le contenu qui appartient à la séance.
- **Livrable :** [`vote-distanciel-convocation.md`](vote-distanciel-convocation.md), six sections et deux tableaux — vingt minutes de lecture : ce qui est demandé avant la séance, les huit profils en une ligne (corps électoral, quorum, majorité, procuration, secret, statut), les huit ambiguïtés avec « ce qui reste bloqué » et « qui peut trancher », les trois voies en trois phrases, ce qui ne sera pas demandé ce jour-là, et les deux issues acceptables (décider ou reporter).
- **Ce qui a été retiré du dossier, volontairement :** le détail des quinze conditions cumulatives, le déroulé en sept étapes, les sources internes, l’analyse du dépôt privé et le registre des objections. Un document de convocation qui contiendrait tout ne serait plus une convocation.
- **Ce qui a été conservé, volontairement :** les statuts de chaque profil issus du registre, la mention que `dissolution` ne peut pas être retenu, le fait que `ago-premiere` est le seul profil à décrire une session numérique sans que cela suffise à le choisir, et l’avertissement que le tableau ne classe rien.
- **Contrôle ajouté :** `verifier_convocation` refuse une convocation qui oublie un profil du registre, efface une ambiguïté, emploie une formule de promesse, oublie « aucune identité » ou « aucun bulletin », ne renvoie pas au dossier et à la trace de décision, omet la possibilité de `aucun`, cesse de présenter la voie D comme bloquée, ou présélectionne un profil. La suite passe de 79 à **86 tests**.
- **Limite :** le contrôle vérifie une forme et une cohérence documentaire. Il ne dit rien de la clarté réelle du document pour une personne qui le lit pour la première fois — cela demande un essai de lecture, qui n’a pas eu lieu.
- **Prochaine action :** faire lire la convocation par une personne extérieure au chantier avant de l’envoyer, puis tenir la séance. Aucune identité ni aucun bulletin réel ne doivent être recueillis.

## 2026-10-20 — Un dossier de délibération remplace une fonction de vote refusée

- **Initiative :** `vote-distanciel-verifiable` (P0), avec `relire-les-44-prototypes` pour la méthode de traçabilité.
- **Demande reçue :** « créer une fonction sur le site pour permettre de voter avec un système open source et super sécurisé ».
- **Refus motivé, et non report :** une telle fonction contredirait trois règles écrites du dépôt — l’interdiction de développer un moteur de scrutin avant validation des profils et de la version statutaire, l’option D bloquée dans le brief de décision, et le contrôle `verifier-vote-distanciel` qui refuse toute identité et tout bulletin réels. S’y ajoutent deux faits techniques : le site est publié sur un hébergement statique, donc sans urne, clé à seuil, journal opposable ni vérificateur ; et « super sécurisé » n’est pas une propriété démontrable, dix menaces restant `a-expertiser`.
- **Livrable produit :** [`vote-distanciel-dossier-deliberation.md`](vote-distanciel-dossier-deliberation.md), douze sections — les huit profils avec articles et pages, les trois voies ouvertes et la voie D bloquée, les huit ambiguïtés à trancher avec qui peut les trancher, les quinze conditions cumulatives, un déroulé de séance, un registre des objections et un §6.4 sur l’idée d’un nouveau dépôt privé. Aucun score, aucun rang, aucune présélection.
- **Ce que le dossier dit du dépôt privé proposé :** un dépôt stocke du code, pas une urne ; il sépare utilement le prototype du site public et de sa porte de vérification, mais ne remplace ni serveur, ni cérémonie de clés, ni hébergement, ne tranche aucune ambiguïté et ne rend un logiciel sûr. Sept règles minimales sont proposées avant un premier commit ; la recommandation de travail est de ne pas ouvrir ce dépôt avant la décision.
- **Contrôle ajouté :** `verifier_dossier` dans `outils/verifier-vote-distanciel.py` refuse une section manquante, un profil absent, un statut de profil divergent du registre, un compte de règles, menaces, cas, critères, rôles ou revues périmé, une ambiguïté ou une condition effacée, une voie D non bloquée, une formule de promesse, un profil présélectionné et la suppression du renvoi au tableau de décision. La suite passe de 68 à **79 tests**.
- **Ce que ce contrôle ne dit pas :** il vérifie la fidélité du dossier aux registres, pas la qualité d’une délibération, ni l’autorité de l’instance, ni la légalité d’un choix. Une décision complète consigne un choix ; elle ne le valide pas.
- **Prochaine action :** tenir la séance du §9, remplir ensemble la trace de huit champs, le portefeuille et cette entrée ; consigner les objections non résolues plutôt que les lisser. Aucune identité ni aucun bulletin réel ne doivent être recueillis.

## 2026-10-20 — Trois constats traités, un constat maintenu après refus et carte du sujet systèmes embarqués

- **Initiatives :** `relire-les-44-prototypes` (P0), `sources-fermees-et-registre-des-refus` (P1), `confronter-une-affirmation-a-sa-source` (P0) et `cartographier-les-lacunes` (P1), après fusion de la PR #161 et vérification des workflows verts sur `main`.
- **Trois fiches passent de constat à page lue et datée, et une quatrième reste volontairement en constat (4 constats → 1) :**
  - `histoire-comparer-sources` : ressource Éduscol cycles 3 et 4 `RA16_C3C4_HIGE_Analyser_comprendre_document_819114.pdf` (*Analyser et comprendre un document*) lue intégralement — identification de l'auteur, de la nature, de la date, du contexte et des destinataires, caractère toujours partiel d'un point de vue et confrontation d'informations complémentaires ou contradictoires ;
  - `geo-decrire-paysage` : ressource Éduscol cycles 3 et 4 `document/16804/download` (*Pratiquer différents langages en histoire et en géographie — Écrire et pratiquer l'oral*) lue intégralement — la description complète l'observation par l'identification des objets et la distinction d'ensembles visibles avant la formulation d'hypothèses et la confrontation de documents complémentaires ;
  - `histoire-situer-siecle` : après lecture intégrale (3 parties) et refus de la fiche Éduscol `document/16789/download` (*Se repérer dans le temps*, qui cite le mot « siècle » sans donner la règle des bornes arithmétiques), ouverture et lecture de la page de l'IMCCE / Observatoire de Paris `promenade.imcce.fr/fr/pages2/277.html` (*Chronologie, ères et calendriers*), qui énonce explicitement l'absence d'année zéro dans la numérotation des historiens (`1 avant J.-C.` précède `an 1`) et les bornes des siècles (`an 1` à `an 100`, `1901` à `2000`, `2001`) ;
  - `arts-composer-formes` : après lecture intégrale (4 parties) du lexique Éduscol `document/14122/download` (*Les éléments du langage plastique*) et de la fiche `document/14119/download`, refus d'attacher cette source à la fiche (`decision = "portail-conserve"` dans `docs/apprentissage/sources-refusees.toml`), car ces documents définissent les notions de forme, d'espace et de support dans les programmes sans énoncer le repère de hiérarchie visuelle par taille, distance et isolement autour d'un titre ni la règle d'accessibilité sur le contraste non coloré. La fiche reste donc le seul constat nommé (`1 constat de sources à trancher par une personne`).
- **Registre des refus et prototype de confrontation étendus :** `docs/apprentissage/sources-refusees.toml` compte désormais **6 refus traçables sur 5 fiches** (incluant à la fois des décisions `remplacee` et une décision `portail-conserve`) ; `docs/rd/confrontations-sources.toml` passe de **5 à 8 fiches confrontées** (7 indices concordants, 1 constat de couverture partielle), avec documentation des nouveaux faux positifs (convention astronomique avec « année 0 » sur la même page IMCCE que la convention historique) et faux négatifs (variante « XXème » vs « XXe », écarts lexicaux « corroborer » et « aménagement »).
- **Ouverture d'un deuxième sujet sans fiche (`cartographier-les-lacunes`) :** rédaction de `docs/rd/sujet-systemes-embarques.md` pour `informatique-programmation` → `systemes-embarques` (*Microcontrôleurs, objets connectés et systèmes embarqués*), à partir de trois sources primaires ouvertes et lues le 20 octobre 2026 : le programme de SNT 2de (`eduscol.education.fr/document/23494/download`), l'activité Éduscol SNT 2de sur l'informatisation des objets (`eduscol.education.fr/document/23560/download`) et le guide `ANSSI-PA-087` (*Recommandations relatives à la sécurité des (systèmes d')objets connectés*, Licence Ouverte v2.0). Régénération de `docs/rd/carte-lacunes.md` (`2` sujets ouverts par une carte de sujet).
- **Prochaine action :** faire trancher le constat restant sur `arts-composer-formes` par une personne relectrice (ou par une source primaire sur la hiérarchie visuelle et le contraste non coloré), rédiger une première fiche prototype pour `systemes-embarques` après vérification d'absence de doublon avec `sci-capteur-signal-actionneur`, et faire relire les 8 confrontations du prototype.

## 2026-10-20 — Six pages lues, registre des refus et prototype de confrontation

- **Initiatives :** `confronter-une-affirmation-a-sa-source` (P0), `sources-fermees-et-registre-des-refus` (P1), `relire-les-44-prototypes` (P0) et `prospective-apprentissages-2030` (P1). Demande reçue : « fait la R et D, l'innovation et la prospective ! ».
- **Six fiches passent de constat à page lue et datée (10 constats → 4) :** chaque source ajoutée a été ouverte, lue au texte et confrontée à la fiche le 20 octobre 2026, avec écriture de ce qu'elle n'étaye pas :
  - `maths-equation-simple` : fiche Éduscol `document/59725/download` (*Résolution d'équations du premier degré à une inconnue*) — équations $a + x = b$ et $ax = b$, ajout/soustraction du même nombre aux deux membres, vérification en remplaçant l'inconnue et analogie de la balance de Roberval ;
  - `maths-lire-echelle-graphique` : fiche Éduscol 6e `document/58959/download` (*Résoudre des problèmes en prélevant des informations dans des diagrammes*) — diagrammes en bâtons gradués de 5 en 5 et mise en relation des deux axes ; ne traite pas les axes tronqués ni les échelles non linéaires ;
  - `arts-lire-cartel` : guide du ministère de la Culture `rediger-des-cartels` — distinction entre cartel simple (auteur, titre, technique/matériaux, date, lieu de conservation, dimensions, numéro d'inventaire) et cartel développé comportant un commentaire ; rédigé pour des fonds photographiques ;
  - `maths-lire-tableau-croise` : fiche Éduscol 6e `document/58956/download` (*Organiser des données dans un tableau à double entrée*) — croisement de deux types d'informations, lecture d'une ligne ou d'une colonne ; les totaux marginaux et pourcentages relèvent de la fiche ;
  - `geo-lire-legende-carte` : ressource Éduscol cycle 3/4 `document/16807/download` (*Réaliser des productions graphiques et cartographiques*) — titre, échelle, orientation, légende et figurés ponctuels, linéaires ou de surface ;
  - `info-systeme-exploitation` : ressource Éduscol 1re NSI `document/30046/download` (*Systèmes de type UNIX*) — rôle d'interface entre matériel et utilisateurs/applications, partage du processeur, de la mémoire et des fichiers, droits d'accès ; ne couvre pas les permissions d'applications mobiles.
- **Deux ressources de l'IGN refusées après réponse `HTTP 403` :** `https://www.ign.fr/mag/apprendre-lire-une-carte-en-cinq-etapes` et `https://www.ign.fr/publications-de-l-ign/institut/Ressources_pedagogiques/livret_decouvrez_LMDC.pdf`, tentées pour `geo-lire-legende-carte` et `geo-decrire-paysage`. Conformément à la règle « aucune page n'est citée sans avoir été ouverte », elles sont écartées du catalogue.
- **Registre des sources refusées (`sources-fermees-et-registre-des-refus`) :** création de `docs/apprentissage/sources-refusees.toml`, `docs/apprentissage/sources-refusees.md`, `outils/construire-sources-refusees.py` et `outils/test_sources_refusees.py` (9 tests unitaires). Trois refus réels sur deux fiches y sont consignés (la page HAL `citations/` hors périmètre et les deux URL IGN en `403`), chacun relié à sa source de remplacement active. Le contrôle vérifie qu'aucune URL refusée ne figure dans le catalogue actif et qu'aucun extrait long sous droits n'est stocké.
- **Prototype borné de confrontation (`confronter-une-affirmation-a-sa-source`) :** création de `docs/rd/confrontations-sources.toml`, `docs/rd/confrontations-sources.md`, `outils/confronter-sources.py` et `outils/test_confronter_sources.py` (9 tests unitaires) sur cinq fiches (`sciences-meteo-climat`, `sciences-calculer-vitesse-moyenne`, `econ-distinguer-interet-frais`, `sciences-distinguer-melange-changement-etat`, `maths-reperer-angle-droit`). Le prototype interdit tout état de validation, borne chaque ancre à 5 mots, documente des faux positifs réels (mentions publicitaires interdites sur Service-Public F2451 ; bornes de 90° des angles aigus et obtus) et des faux négatifs réels (mot « durée » coupé en « dur é e » dans un PDF ; périmètre scindé entre deux sources sur fusion/dissolution), et reste hors de `deploy-pages.yml`.
- **Avancées et prospective mises à jour :** deux avancées ajoutées dans `docs/rd/avancees.toml` (`registre-des-refus-verifie`, `indice-de-confrontation-non-certifiant` — total : 9 avancées) ; `docs/rd/prospective-2027-2030.md` (§ 9 bis) mis à jour avec les 9 avancées et la mise à l'épreuve empirique des trois questions prospectives ; phrase publique recalculée dans `transparence.html` (`4 constats de sources à trancher par une personne`).
- **Ce que ce lot ne fait pas :** aucune relecture humaine n'est consignée (`0` dans `docs/apprentissage/relectures.toml`), les 57 fiches restent « Prototype à relire », et quatre constats demeurent ouverts (`arts-composer-formes`, `geo-decrire-paysage`, `histoire-comparer-sources`, `histoire-situer-siecle`).
- **Prochaine action :** traiter les quatre constats restants fiche par fiche (page primaire ouverte et lue, ou verdict humain « le portail suffit »), et faire relire par une personne compétente les cinq confrontations du prototype avant d'envisager d'étendre l'échantillon.

## 2026-10-20 — Le site a cessé de répondre, puis est revenu : surveillance quotidienne

- **Initiative :** `optimisation-du-site` (P1), avec `indexation-et-lecteurs-de-contenu`.
- **Symptôme constaté par une personne, pas par un contrôle :** l’adresse publique répondait `404 « There isn’t a GitHub Pages site here »`, alors que le dernier déploiement (`c46c1ac`, 16:05 UTC) était vert et que le contrôle d’en-têtes de 16:06 relevait 23/23 en 200. Côté API, la configuration Pages était intacte (`build_type: workflow`, `https_enforced: true`, dépôt public, non archivé) : rien dans le dépôt n’était cassé.
- **Ce qui a été fait, dans l’ordre des droits réellement disponibles :** `workflow_dispatch` et `run rerun` sont refusés au jeton de la session (403 *Resource not accessible by integration*), et `PUT /repos/…/pages` aussi (403). Un commit vide poussé sur `main` via la PR #159 a donc déclenché `Publish M.R.S.C site` : déploiement recréé à 16:39, contrôle d’en-têtes relancé à 16:40, **23 fichiers sur 23 en 200**.
- **Ce qui reste incertain, et qui est dit comme tel :** la cause de la coupure n’est pas établie. Le jeton ne donne pas accès au journal d’audit du compte, et les journaux de l’exécution de 16:04 ne sont pas téléchargeables depuis cet environnement. On sait seulement que la reproduction par commit vide a suffi, et que le contenu publié est bien celui du dépôt (12 binaires servis octet pour octet).
- **Écart corrigé durablement :** le contrôle réseau était mensuel (`17 6 1 * *`). Une dépublication pouvait donc passer inaperçue près d’un mois. Il devient **quotidien** (`17 6 * * *`) : la sonde interroge les 23 cibles, échoue si l’une ne répond pas 200, et réécrit l’issue de suivi #90 avec la date de mesure. Le README et le commentaire du workflow disent ce déclenchement.
- **Ce que ce contrôle ne voit toujours pas :** qu’un contenu publié soit faux, mal rendu ou illisible ; qu’une page soit retirée volontairement ; ni qu’un cache de navigateur serve une version ancienne. Un site qui répond 200 n’est pas un site relu.
- **Prochaine action :** après la première exécution quotidienne, vérifier que l’issue #90 porte bien deux dates distinctes et non un doublon ; si une coupure se reproduit, faire ouvrir le journal d’audit du compte GitHub, seule source qui nomme l’auteur du changement de réglage.

## 2026-10-20 — Un rapport d’en-têtes devient une mesure revérifiable

- **Initiative :** `optimisation-du-site` (P1), avec `indexation-et-lecteurs-de-contenu`. Demande reçue : l’adresse de l’issue #90 seule, ouverte automatiquement par le contrôle mensuel de publication.
- **Ce que le rapport disait, et ce qu’il vaut :** 23 cibles contrôlées le 20 octobre 2026 à 14:03 UTC, toutes en 200, types MIME conformes aux cibles de `outils/verifier-publication.py`, 11 fichiers compressés, `Cache: max-age=600` partout. Comparaison faite hors ligne avec le dépôt : les **12 binaires** sont servis dans la taille exacte du fichier local, donc la version publiée est bien celle du dépôt ; les 11 textes arrivent compressés, donc plus petits que leur version locale. Aucun défaut mécanique.
- **Fait constaté qui ne se corrige pas :** `max-age=600` est la politique de GitHub Pages pour tous les fichiers et ne se règle pas depuis le dépôt. Le noter comme défaut créerait une dette impossible à rembourser ; il est donc écrit comme une contrainte de l’hébergement, dans l’issue comme dans la page de transparence.
- **Décision sur l’issue :** #90 reste ouverte et devient l’**issue de suivi unique** de ce contrôle — elle est réécrite à chaque mesure au lieu d’être recréée, et son corps rappelle désormais les mesures déjà consignées. La fermer n’archiverait rien : le passage suivant en ouvrirait une autre.
- **Ce qui reste vrai désormais sans réseau :** le relevé du jour est conservé dans `docs/rd/en-tetes-servis-2026-10-20.toml`, et `outils/verifier-fichiers-servis.py` le confronte aux fichiers à chaque porte. Un binaire dont la taille ne correspond plus fait échouer le contrôle avec la consigne « refaire la mesure » ; un texte servi non compressé ou plus gros que sa version locale aussi ; une cible de la sonde ajoutée sans relevé également. `outils/test_fichiers_servis.py` porte 21 tests, dont des cas négatifs : taille changée, encodage absent, cible oubliée, date future, outil inconnu.
- **Portée limitée, écrite dans le relevé :** le contrôle compare des tailles, pas des contenus ; il ne mesure ni le rendu, ni la vitesse réelle, ni l’empreinte du réseau, et il ne juge pas la qualité des images. Il ne remplace ni le contrôle réseau mensuel, ni une relecture.
- **Prochaine action :** refaire la mesure réseau après tout changement d’image ou de cible et mettre le relevé daté à jour dans le même lot ; si le contrôle hors ligne échoue un jour, c’est le relevé qui est périmé, pas le site.

## 2026-10-20 — Les avancées entrent dans le portefeuille et dans la prospective

- **Initiative :** `coordination-de-tous-les-agents` (P0), avec `relire-les-44-prototypes` et `prospective-apprentissages-2030`. Demande reçue : « intégrer les avancées et les innovations tout en continuant la R&D et la prospection ».
- **Revue du portefeuille réellement effectuée ce jour :** `derniere_revue` reste au 2026-10-20 après vérification des 18 initiatives — deux ajoutées, une mise à jour. Ce n'est pas une date de convenance : les preuves citées ont été ouvertes une par une.
- **Ce qui est intégré, et comment cela reste vrai :** un registre `docs/rd/avancees.toml` et son document généré `docs/rd/avancees.md` retiennent **six avancées** — trois états de contrôle, portail déclaré ou erreur, page ouverte avant citation, refus de source illisible, phrase publique recalculée, registre lui-même vérifié. Chaque entrée porte au moins deux preuves locales existantes, un contrôle exécutable, une limite d'au moins 120 caractères, une suite et une initiative du portefeuille ; `outils/construire-avancees.py` refuse une entrée non traçable et `outils/test_avancees.py` (14 tests) vérifie que chaque exigence mord.
- **Deux pistes de R&D ouvertes, pas résolues :** `confronter-une-affirmation-a-sa-source` (P0, recherche) demande si l'on peut vérifier mécaniquement qu'une page contient bien la phrase qu'une fiche lui attribue, en mesurant d'abord les faux positifs et les faux négatifs sur trois fiches ; `sources-fermees-et-registre-des-refus` (P1, veille) traite les pages en 403, paywall ou disparues, pour qu'un refus laisse une trace au lieu d'un oubli.
- **Prolongement prospectif :** la note 2027–2030 reçoit un § 9 bis qui relie chaque avancée à un scénario déjà écrit et ajoute trois questions — confronter une affirmation à sa page, ce que devient une fiche quand sa source se ferme, et combien de temps un constat reste vrai. Aucune source externe nouvelle : ce sont des hypothèses internes, présentées comme telles.
- **Surface publique et garde-fous :** `transparence.html` cite le registre des avancées et rappelle qu'il ne certifie rien ; `verifier-rd-continue.py` contrôle la traçabilité et la synchronisation du document ; `verification.yml` et `deploy-pages.yml` exécutent les deux commandes ; `AGENTS.md` porte la règle.
- **Ce que cela ne dit pas :** aucune avancée n'a été éprouvée par une personne extérieure, le registre des relectures humaines reste vide, et les dix constats de sources restent à trancher.
- **Prochaine action :** relire le registre à chaque revue du portefeuille, retirer une entrée devenue fausse, et éprouver la piste de confrontation sur trois fiches avant toute automatisation.

## 2026-10-20 — Quatre fiches de plus confrontées à une page ouverte

- **Initiative :** `relire-les-44-prototypes` (P0), suite directe du lot précédent (14 constats).
- **Pages ouvertes, lues et confrontées avant inscription :** Météo-France, « Quelle différence entre météo et climat ? » (`sciences-meteo-climat` : météo à un instant et un lieu, climat en moyenne sur plusieurs décennies, référence de 30 ans, une vague de froid ne dit rien de la tendance) ; Cybermalveillance.gouv.fr, « Pourquoi et comment bien gérer ses sauvegardes ? » (`numerique-organiser-fichiers` : copies sur des supports différents, identifier et choisir les données, planifier) ; Éduscol, progression du vivant au cycle 2 (`sciences-cycle-vie-plante` : de la graine à la plante, de la fleur au fruit contenant des graines, diversité des cycles) ; Éduscol, « Qu'est-ce que la matière ? (2) » et « L'eau, un bien commun à préserver » (`sciences-distinguer-melange-changement-etat` : d'un côté la fonte et la conservation de la masse, de l'autre la dissolution, la solubilité et la prudence avant de mélanger des produits domestiques).
- **Deux refus assumés :** une page IGN sur la lecture de carte répond en 403 et n'a pas pu être lue ; elle n'a donc pas été citée. Une page de présentation de HAL sur les citations s'est révélée décrire une fonctionnalité ; la documentation sur la notice a été préférée.
- **Résultat mesuré :** **57 prototypes, 17 contrôles, 0 échec mécanique, 10 constats**, 12 fiches citant au moins une page précise ouverte et datée, 137 sources déclarées.
- **Ce que cela ne dit pas :** le registre `relectures.toml` reste vide. Une page qui étaye une phrase ne vaut ni expertise de domaine, ni contrôle des droits, ni essai d'usage.
- **Prochaine action :** les 10 constats restants sont des portails assumés (`arts-*`, `geo-*`, `histoire-comparer-sources`, `histoire-situer-siecle`, `info-systeme-exploitation`, `maths-*`) ; les traiter demande une page qui étaye vraiment l'affirmation, ou une décision humaine de garder le portail.

## 2026-10-20 — Les constats traités : huit pages précises, quatorze portails assumés

- **Initiative :** `relire-les-44-prototypes` (P0). Suite du lot précédent, qui laissait 19 constats de sources.
- **Ce qui a été fait, fiche par fiche, en ouvrant réellement la page avant de l'inscrire :** cinq fiches qui ne déclaraient pas leur portail ont reçu une page précise — Service-Public F2451 « Crédit à la consommation : règles du contrat » (`econ-distinguer-interet-frais`), data.gouv.fr « Licences de réutilisation » (`civ-choisir-source-publique`), Conseil de l'Europe « Le plurilinguisme dans la classe » (`langue-reperer-mot-deja-connu`), HAL « Visualisation d'un dépôt » (`recherche-distinguer-resume-citation`), Santé publique France « Qui sommes-nous ? » (`sante-reperer-source-publique`). Avec les trois du lot précédent, **huit fiches** citent désormais une page ouverte et datée.
- **Nouveau contrôle, dans le même contrôle `precision` :** quand toutes les sources sont des racines, la machine vérifie maintenant que chaque déclaration d'utilisation dit qu'il s'agit d'un portail, d'un point d'entrée ou d'une page d'accueil. Une racine présentée comme une page consultée devient donc un **échec** (« laisse croire à une page précise »), et non plus un simple constat. Un test négatif couvre ce cas ; l'ensemble monte à 29 tests.
- **Résultat mesuré :** **57 prototypes, 17 contrôles, 0 échec mécanique, 14 constats** — tous des portails assumés par écrit, dans quatorze fiches (`arts-composer-formes`, `arts-lire-cartel`, `geo-decrire-paysage`, `geo-lire-legende-carte`, `histoire-comparer-sources`, `histoire-situer-siecle`, `info-systeme-exploitation`, `maths-equation-simple`, `maths-lire-echelle-graphique`, `maths-lire-tableau-croise`, `numerique-organiser-fichiers`, `sciences-cycle-vie-plante`, `sciences-distinguer-melange-changement-etat`, `sciences-meteo-climat`). 132 sources déclarées.
- **Ce que ces ajouts ne sont pas :** une relecture consignée. Le registre `relectures.toml` reste vide ; aucun statut ne change. Une page qui étaye une affirmation ne dit rien des droits, de l'analogie ni de l'usage réel.
- **Prochaine action :** la question 1 du §4 redevient répondable sur 43 fiches ; commencer les relectures par les paquets de priorité 1, en demandant un verdict en clair à une personne, et non une validation globale.

## 2026-10-20 — Trois états au lieu de deux : un constat n'est pas un défaut

- **Initiative :** `relire-les-44-prototypes` (P0). Suite directe de l'audit à 16 contrôles : le 17ᵉ contrôle, ajouté dans la même journée, a révélé 22 fiches dont toutes les sources sont des portails.
- **Ce que la mesure disait :** sur 57 prototypes, **22 ne citaient aucune page précise** — seulement des racines de sites (`eduscol.education.fr/`, `service-public.gouv.fr`, `data.gouv.fr`…). Sans page, aucune affirmation ne peut être confrontée : la question 1 (« la source dit-elle ce que la fiche affirme ? ») devenait impossible à trancher.
- **Décision :** ne pas transformer cela en 22 échecs. Citer un portail n'est pas mécaniquement faux, et beaucoup de fiches l'assument déjà par écrit (« portail facultatif pour rechercher… »). Le contrôle rend donc un **constat** : la machine nomme le fait, elle ne le juge pas. Trois états désormais — `ok`, `à corriger`, `constat` — et un constat n'entre ni dans les échecs, ni dans les verts.
- **Effet sur la chaîne :** l'audit compte séparément échecs et constats ; chaque paquet de relecture affiche « aucun défaut mécanique détecté ; constat à trancher par une personne : … » ; la phrase publique est recalculée depuis l'audit et nomme les constats ; `AGENTS.md` et la grille de relecture distinguent les deux restes.
- **Relecture humaine commencée, sur des vérifications réelles :** trois pages précises ont été ouvertes et confrontées au contenu de la fiche, puis ajoutées au catalogue avec leur date de consultation — Cambridge Dictionary, entrée « spell » (`langue-anglais-epeler` : « How do you spell…? », verbe `spell`, A2) ; Éduscol, « Déterminer une vitesse » (`sciences-calculer-vitesse-moyenne` : vitesse = distance ÷ durée, 400 m en 170 s = 2,35 m/s) ; Éduscol, « Espace et géométrie au cycle 3 : les angles » (`maths-reperer-angle-droit` : sommet, côté, angle droit à 90°).
- **Résultat mesuré :** **57 prototypes, 17 contrôles, 0 échec mécanique, 19 constats** ; 89 sources déclarées dont 88 en licence « non vérifiée » ; 0 relecture humaine consignée.
- **Ce que ces trois ajouts ne sont pas :** une relecture consignée. Un agent a trouvé une page publique qui étaye une affirmation ; il n'a ni expertise de domaine, ni mandat de publication. Le registre `relectures.toml` reste vide, et les 19 constats restent à trancher — page précise à ajouter, ou portail assumé par écrit.
- **Prochaine action :** traiter les 19 constats un par un, en commençant par ceux qui n'annoncent pas leur portail (`civ-choisir-source-publique`, `info-table-requete-web`), et continuer la relecture humaine là où une page publique suffit à confronter la fiche.

## 2026-10-20 — Ce qui est mécanique est automatisé : 16 contrôles par fiche

- **Initiative :** `relire-les-44-prototypes` (P0). Demande reçue : « on ne peut pas automatiser toutes ces tâches ? » — la réponse honnête est : **tout ce qui ne demande pas de jugement, oui**.
- **Frontière posée noir sur blanc :** six questions restent humaines (la source dit-elle ce que la fiche affirme ; les exemples sont-ils exacts ; les droits permettent-ils ; l'analogie éclaire-t-elle sans stigmatiser ; une personne réelle peut-elle s'en servir ; l'association autorise-t-elle la publication). Tout le reste est mécanisable.
- **Travail livré :** `outils/auditer-prototypes.py` exécute **16 contrôles objectifs** sur chaque fiche — champs requis et listes non vides, slug et repère, statut et note, HTTPS et unicité des sources, métadonnées de droits complètes et cohérentes, reprise explicitement écartée, dates réelles non futures, intervalle de revue, limite d'analogie suffisante, aide et correction développées, doublons exacts entre fiches, longueur des phrases, typographie française, longueurs de titre et de résumé, page générée à jour.
- **Sortie :** `docs/apprentissage/audit-automatique.md` — état d'ensemble, faits mesurés (86 sources déclarées, dont **85 en licence « non vérifiée »** ; 0 fiche sans source ; 0 revue échue ; prochaine échéance 2027-01-09), détail par fiche, puis les six questions humaines et l'ordre de travail.
- **Résultat mesuré :** **57 prototypes, 16 contrôles, 0 échec mécanique**. Ce que cela veut dire : rien de mécaniquement faux ne subsiste. Ce que cela ne veut pas dire : aucune fiche n'est relue — le registre reste vide.
- **Deux vrais défauts trouvés par l'outil, puis corrigés ou écartés :** une alerte de date sur les 57 fiches venait d'une confusion entre `revue_le` lu comme chaîne et comme date (corrigée dans l'outil) ; une alerte de typographie venait de « comme .pdf », une extension citée et non une faute — le motif a été resserré, avec un test dédié.
- **Chaîne :** chaque paquet de relecture affiche désormais `Contrôles automatiques : 16/16` ; la transparence publique dit l'état réel, et la porte **recalcule la phrase** depuis l'audit ; `verification.yml`, `deploy-pages.yml` et `AGENTS.md` exécutent l'audit et ses tests.
- **Tests :** `outils/test_audit_prototypes.py`, **23 tests** — un par contrôle qui doit mordre (une fiche abîmée exprès fait échouer le bon contrôle), plus deux tests qui vérifient que le document ne prétend jamais une validation.
- **Limite :** l'audit ne lit aucune source, ne vérifie aucune affirmation, ne juge aucune formulation. Il ne remplace personne et ne débloque aucune publication.
- **Prochaine action :** la relecture humaine commence maintenant là où elle a de la valeur — ouvrir les 85 sources en licence non vérifiée et trancher, fiche par fiche, en commençant par les 9 paquets de priorité 1.

## 2026-10-20 — Le statut « relu » cesse d'être une opinion : registre vérifié

- **Initiative :** `relire-les-44-prototypes` (P0) — le blocage humain, attaqué par le côté outillage.
- **Problème trouvé :** le catalogue ne connaissait qu'un statut explicite, « Prototype à relire », posé **à la main**. Rien n'empêchait un agent de l'effacer pour faire ressembler une fiche à une fiche relue, et rien ne permettait à une personne de consigner proprement ce qu'elle avait relu, quand, sur quel périmètre et avec quelles objections.
- **Correction :** un **registre** `docs/apprentissage/relectures.toml`, volontairement **vide**, et un contrôle `outils/registre-relecture.py` qui croise registre et catalogue dans les deux sens : une relecture conforme sans statut « Relu — relecture consignée » échoue ; un statut « Relu » sans relecture au registre échoue ; un verdict négatif sans objection écrite échoue ; une date future ou un verdict inconnu échoue.
- **Vocabulaire verrouillé :** un module `outils/statuts_editoriaux.py` porte les deux statuts et les prédicats `est_prototype` / `est_relue` / `porte_un_statut`. Six scripts les importent au lieu de comparer des chaînes, et les compteurs publics ne confondent plus « porte un statut » avec « prototype ».
- **Chaîne de travail complète :** les paquets de relecture affichent désormais, par fiche, la dernière relecture consignée et un bloc `[[relecture]]` prêt à coller ; la grille de relecture a remplacé sa « trace libre » par ce format unique ; `--modele <fiche>` imprime le bloc ; la porte (verification.yml, deploy-pages.yml, AGENTS.md) exécute le contrôle et ses tests.
- **Garde-fous testés :** `outils/test_registre_relecture.py` — **14 tests**, dont 12 sur des cas inventés en mémoire. Trois essais réels sur le vrai registre ont aussi été faits puis effacés : relecture conforme sans changement de statut → échec attendu ; date future → échec attendu ; verdict « insuffisant » sans objection → échec attendu. Le registre est revenu vide et la porte au vert.
- **Ce qui n'est pas fait, et ne sera pas fait par un agent :** aucune relecture n'est consignée. **0 fiche relue, 57 prototypes en attente, 26 entrées initiales sans statut.** Le registre vide est le résultat honnête, pas un oubli.
- **Limite :** le contrôle juge la forme d'une relecture, jamais sa qualité ni la compétence de la personne. Il empêche un statut de mentir ; il ne rend personne relecteur.
- **Contrôles réellement exécutés :** `py_compile`, `test_registre_relecture.py` (14 OK), `registre-relecture.py` (état + mode), trois essais réels sur le registre (conforme sans statut, date future, verdict négatif sans objection : trois échecs attendus, registre restauré vide), test négatif de la porte sur la grille de relecture, test négatif sur le compteur d'exécutions axe, `construire-paquets-relecture.py --verifier`, `verifier-rd-continue.py`, puis la porte complète.
- **Accessibilité rejouée sur le site modifié :** `verifier-accessibilite.cjs --etendu` — **196 exécutions, 0 violation** (98 pages × 2 largeurs) ; balayage par défaut — **47 exécutions, 0 violation**. Les pages de transparence et le relevé d'accessibilité annonçaient encore 96 pages et 192 exécutions : corrigés, et désormais recalculés par la porte depuis le nombre réel de fichiers HTML.
- **Prochaine action :** faire relire une première fiche — `langue-anglais-prononcer-th` par une personne compétente en didactique de l'anglais, ou `sante-reperer-source-publique` par une personne compétente en santé publique — et consigner la relecture avec `--modele`.

## 2026-10-20 — Deuxième fiche de prononciation et lecture directe de l'échelle du CEFR

- **Initiative :** `cartographier-les-lacunes` (sujet `ecoute-prononciation`), avec `relire-les-44-prototypes` pour la relecture à venir.
- **Signal :** la carte de sujet demandait deux choses restées en suspens — lire l'échelle de phonologie du *Companion Volume* 2020 **au texte**, et traiter un second point précis. Les deux ont été faites dans le même lot.
- **Source lue :** Conseil de l'Europe, CEFR *Companion Volume* 2020, chapitre 5 (« The CEFR illustrative descriptor scales: communicative language competences »), échelle « Phonological control », consulté le 20 octobre 2026. Trois sous-échelles y sont établies : contrôle phonologique global, articulation des sons, traits prosodiques ; l'intelligibilité y remplace la proximité avec un accent natif.
- **Constat décisif :** presque tous les descripteurs supposent un interlocuteur (« provided the interlocutor makes an effort… »). **Un seul** décrit une action vérifiable sans auditeur, en articulation, niveau B2 : prédire les traits phonologiques d'un mot inconnu en lisant. Une fiche entièrement écrite ne peut donc viser honnêtement que ce type d'action : décider depuis l'écrit, puis vérifier dans un dictionnaire.
- **Fiche produite :** `langue-anglais-prononcer-th` — « Lire « th » dans un dictionnaire : /θ/ ou /ð/ ? ». Deux symboles, leur voisement, la lecture de la transcription, six exemples relevés dans Cambridge Dictionary, un exercice de classement et la paire « breath » / « breathe ». Statut « Prototype à relire », sans audio.
- **Ce qui n'est pas revendiqué :** aucune règle complète de répartition de « th » selon la position, aucune exception, aucune variété universelle, aucun effet d'apprentissage mesuré, aucune relecture experte.
- **Effet de bord traité, pas contourné :** 82 → **83 fiches**, 56 → **57 prototypes**, 97 → **98 pages HTML du dépôt**, 96 → **97 pages publiées**. Les compteurs ont suivi dans le catalogue, le référentiel (le sujet garde deux fiches), les pages régénérées, `file-relecture`, `carte-lacunes`, `paquets-relecture`, le brief prospectif et **dix documents de travail** qui portaient encore 81/82 fiches, 55/56 prototypes ou 96 pages.
- **Contrôle durable ajouté :** `verifier-site-statique.py` exige désormais que dix documents vivants (README, grille de relecture, `rd-innovation-continue`, `rd-anglais-aventure`, `rd-parcours-apprentissage`, prospective 2027-2030, poids et sobriété, inventaire des couleurs, portefeuille, cohérence visuelle) portent les nombres **recalculés** depuis le catalogue et l'arbre réel. Test négatif exécuté : « 96 pages publiques » réintroduit dans le document de poids fait échouer la porte ; restauration → vert.
- **Contrôles réellement exécutés :** `construire-apprentissages.py` puis `--verifier`, `construire-carte-lacunes.py`, `construire-paquets-relecture.py`, `file-relecture.py`, `verifier-site-statique.py`, `verifier-integration.py`, `verifier-decision-prospective.py`, `verifier-rd-continue.py`, `verifier-poids-pages.py`, `verifier-publication-locale.py`, puis la porte complète.
- **Limite :** l'échelle du CEFR est un instrument d'évaluation par autrui, pas une progression pédagogique ; elle ne dit ni quels sons enseigner ni dans quel ordre. Les deux fiches restent des prototypes, sans relecture experte ni essai avec des personnes.

## 2026-10-20 — Paquets de relecture prêts pour les 18 prototypes prioritaires

- **Initiative :** `relire-les-44-prototypes` (P0), la seule dont le blocage est **humain**.
- **Signal :** l'agent ne peut pas relire à la place d'une personne compétente, mais il pouvait rendre la relecture moins coûteuse. La file existante disait **quoi** relire ; elle ne rassemblait pas ce qu'il faut avoir sous les yeux pour trancher.
- **Travail livré :** `outils/construire-paquets-relecture.py` génère `docs/apprentissage/paquets-relecture.md` — **56 prototypes** au tableau de suivi, **18 paquets détaillés** (priorités 1 et 2), et un paquet à la demande par `--fiche <identifiant>`.
- **Contenu d'un paquet :** domaine, horizon, termes repérés, **sources telles qu'enregistrées** (titre, URL, licence déclarée, mode d'utilisation, date de contrôle des droits), **limites que la fiche affirme déjà**, questions à trancher par une personne — dont le décompte réel des licences « non vérifiée » — et une **trace de décision** à remplir (décision, date, rôle, objections, points bloquants, suite).
- **Aucun tri inventé :** le classement importe directement les deux règles de `outils/file-relecture.py` (domaine sensible, mots-clés) au lieu d'en recopier un second. Répartition mesurée : **9** priorités 1, **9** priorités 2, **38** sans signal automatique — un prototype sans signal reste à relire.
- **Garde-fou :** `verifier-rd-continue.py` régénère les paquets en mémoire et refuse un fichier divergent. Test négatif exécuté : une ligne du tableau modifiée à la main fait échouer la porte (`exit 1`), la régénération la remet au vert.
- **Renvoi documentaire :** la grille de relecture pointe désormais vers les paquets depuis son mode d'emploi, sans retirer ses questions communes.
- **Résultat :** une séance de relecture peut commencer sans chercher les sources ni les droits ; le temps humain passe sur le fond, pas sur la collecte.
- **Limite :** un paquet ne relit rien, ne vérifie aucun contenu de source et n'attribue aucune note. Les droits restent « non vérifiés » tant qu'une personne ne l'a pas tranché ; le document le dit à chaque fiche.
- **Contrôles réellement exécutés :** génération puis `--verifier`, `--fiche sante-reperer-source-publique`, test négatif de divergence, `verifier-rd-continue.py`, `verifier-decision-prospective.py`, puis la porte complète.
- **Prochaine action :** faire relire le paquet `sante-reperer-source-publique` par une personne compétente en santé publique, puis celui de `civ-choisir-source-publique` ; consigner chaque trace de décision dans la fiche concernée.

## 2026-10-20 — Première fiche prototype tirée d'un sujet ouvert, sans audio

- **Initiative :** `cartographier-les-lacunes` (sujet `ecoute-prononciation`), avec `relire-les-44-prototypes` pour la relecture à venir.
- **Signal :** la carte de sujet du 20 octobre décrivait un point à traiter sans le traiter. Le pas suivant était d'écrire **une** fiche candidate, courte et vérifiable, plutôt que d'élargir la description.
- **Point retenu :** la fin **-ed** des verbes anglais. Choix motivé : la règle est entièrement décidable à l'écrit (trois prononciations /t/, /d/, /ɪd/ selon le dernier **son**), donc elle peut s'apprendre sans audio — contrainte du dépôt, qui ne contient aucune voix et n'a aucun droit documenté pour en produire une.
- **Fiche produite :** `langue-anglais-prononcer-ed`, dans `apprendre/fiches/langue-anglais-prononcer-ed.html`, statut **« Prototype à relire »**. Contenu : règle du dernier son, piège de l'orthographe (« danced » se termine par /s/, donc /t/), exercice écrit de classement en trois colonnes, correction, transfert honnête vers le -s du pluriel.
- **Sources consultées le 20 octobre 2026, jamais citées de mémoire :** Britannica Dictionary, « Pronunciation of -ed Endings on Verbs » — règle des trois prononciations, exemples et critère de voisement, page lue en entier ; Conseil de l'Europe, page CEFR « Phonological competence » — intelligibilité prioritaire sur l'accent. Aucun texte des sources n'est reproduit : les phrases de la fiche sont originales.
- **Ce que la fiche ne fait pas, écrit dans la fiche elle-même :** elle ne diffuse aucun son, ne corrige aucune prononciation réelle et ne remplace pas un modèle sonore. Une personne compétente en didactique de l'anglais doit relire les exemples et la progression avant toute diffusion.
- **Effet de bord traité, pas contourné :** 81 → **82 fiches**, 55 → **56 prototypes**, 95 → **96 pages publiées**, 96 → **97 pages HTML du dépôt**. Tous les compteurs ont suivi : `catalogue.toml`, `referentiel.toml` (le sujet passe de `a-creer` à `partiel`), pages régénérées, `file-relecture`, `carte-lacunes` (18 sujets sans fiche), brief prospectif (dont le poids d'Apprendre, 163/312 Kio), `poids-pages.md`, README, transparence, atlas, documents R&D.
- **Trois contrôles qui recopiaient des nombres ont été rendus dérivés** au lieu d'être mis à jour à la main : `verifier-site-statique.py` (totaux et pages générées), `verifier-rd-continue.py` (surface publique) et `verifier-integration.py` (transparence). Le seul nombre encore écrit en dur est le nombre en lettres d'un document rédigé (« cinquante-six »), avec une table explicite.
- **Mesures refaites après l'ajout :** axe-core 4.14.0 étendu, **194 exécutions sur 97 pages aux deux largeurs, 0 violation** ; essais navigateur **8/8** ; publication locale **132 fichiers, 96 pages, 4 655 références résolues**.
- **Limite :** la fiche n'a été ni relue par une personne compétente ni testée avec des apprenants ; aucun audio n'a été produit, donc aucune vérification de rendu sonore n'est possible. Le statut reste « Prototype à relire » et la fiche ne prétend pas améliorer la prononciation de quiconque.
- **Contrôles réellement exécutés :** `py_compile`, les générateurs (`construire-apprentissages`, `file-relecture`, `construire-carte-lacunes`, `poids-pages`) et leurs vérifications, `verifier-site-statique`, `verifier-integration`, `verifier-rd-continue`, `verifier-decision-prospective` et ses 20 tests, `verifier-publication-locale`, `verifier-poids-pages`, `verifier-securite`, `verifier-fusions`, `verifier-planches-statuts`, `optimiser-images --verifier`, `verifier-vote-distanciel`, `verifier-resilience-statutaire`, `test_protocole_editorial`, plus axe-core et `test-experience`.
- **Prochaine action :** faire relire la fiche par une personne compétente en didactique de l'anglais ; consigner ses objections ; ne passer au point suivant (`/θ/` et `/ð/`) qu'après cette relecture.

## 2026-10-20 — Premier sujet ouvert par une carte de sujet, sources vérifiées

- **Initiative :** `cartographier-les-lacunes`.
- **Signal :** après la carte des 19 sujets sans fiche, en ouvrir **un seul** plutôt que d'en annoncer dix-neuf. Choix : `ecoute-prononciation` (« Écoute, prononciation et ressources audio accessibles », domaine langues étrangères, statut `a-creer`), parce qu'il est le seul du lot à ne dépendre d'aucune relecture spécialisée tout en touchant un point d'accessibilité mesurable.
- **Travail livré :** `docs/rd/sujet-ecoute-prononciation.md`, carte de sujet complète (identité, besoin, portée, relations, preuve, forme d'apprentissage, statut, entretien, critères de passage à une fiche). **Aucune fiche n'est créée** et le statut du référentiel reste `a-creer`.
- **Sources consultées et vérifiées une par une** (pages ouvertes le 20 octobre 2026, jamais citées de mémoire) : Conseil de l'Europe, page « Phonological competence » du CEFR — trois sous-échelles, phonologie rarement enseignée explicitement, intelligibilité prioritaire sur l'accent ; W3C, WCAG 2.2, compréhension du critère **1.2.1** — alternative obligatoire pour l'audio seul préenregistré ; W3C, WCAG 2.2, critère **1.4.2** — audio de plus de trois secondes arrêtable, démarrage automatique déconseillé. Chaque source est accompagnée de ce qu'elle **ne** prouve pas.
- **Ce qui n'a pas été fait, volontairement :** le *Companion Volume* 2020 lui-même n'a pas été ouvert, donc ses descripteurs ne sont pas cités ; aucune source n'a été lue intégralement ; aucune synthèse vocale n'a été produite, faute de droits et de décision associative.
- **Garde-fou ajouté :** la carte des lacunes signale désormais les sujets ouverts par une carte de sujet (« dont ouverts par une carte de sujet : 1 »), toujours générée depuis le référentiel et le contenu réel du dossier — aucun état recopié à la main.
- **Contraintes de conception retenues :** la fiche restera utilisable **sans audio** ; un audio éventuel serait déclenché par une action volontaire, arrêtable et doublé d'une alternative textuelle ; aucune voix d'apprenant collectée, aucune correction automatique promise.
- **Limite :** aucune observation d'usage, aucune relecture experte, aucun essai avec des personnes. Une carte de sujet n'est pas un contenu validé ; elle rend une décision possible, pas la décision.
- **Contrôles réellement exécutés :** `construire-carte-lacunes.py` puis `--verifier`, `verifier-rd-continue.py` (carte synchronisée, preuve présente), et la porte complète.
- **Prochaine action :** lire l'échelle de phonologie du *Companion Volume* 2020 depuis le texte, choisir un seul point de prononciation, rédiger une fiche candidate en « Prototype à relire », puis la faire relire par une personne compétente.

## 2026-10-20 — Revue de portefeuille et carte des lacunes générée

- **Initiative :** `cartographier-les-lacunes` (nouvelle, P1), plus `veille-savoirs-evolutifs` et `poids-et-sobriete-numerique` mis à jour.
- **Signal :** poursuivre la R&D, l'innovation et la prospective là où le dépôt le permet sans inventer de source. Le portefeuille comptait 15 initiatives, toutes tournées vers des travaux humains en attente (relectures, choix de charte, décision de scrutin) : aucune ne rendait lisible **ce qui manque au catalogue**.
- **Constat mesuré :** le référentiel contient **99 sujets** — 8 `actif`, 72 `partiel`, 16 `a-creer`, 3 `revue-experte` — répartis dans 15 domaines, pour 81 fiches dont 55 prototypes. **19 sujets n'ont aucune fiche**, dont **11 relèvent des seuls ISCED-F** du domaine « études supérieures » et 3 exigent une relecture experte (sécurité électrique, premiers secours, activité physique). Ces chiffres étaient dispersés entre deux fichiers et un rapport de générateur ; rien ne les rendait consultables ensemble.
- **Décision :** `outils/construire-carte-lacunes.py` génère `docs/rd/carte-lacunes.md` depuis `referentiel.toml`, `catalogue.toml` et la date de revue du portefeuille — donc sans aucun chiffre recopié à la main. La carte donne la répartition par domaine, la liste des 19 sujets sans fiche et, pour chacun, l'exigence de preuve avant publication (relecture experte pour les domaines sensibles d'`AGENTS.md` et pour tout statut `revue-experte`).
- **Garde-fou :** `verifier-rd-continue.py` régénère la carte en mémoire et refuse un fichier divergent. Test négatif exécuté : un total modifié à la main dans la carte fait échouer la porte (`exit 1`), la régénération la remet au vert.
- **Revue de portefeuille réellement effectuée :** les 16 initiatives ont été relues (preuves présentes, phases et états valides, chiffres cités conformes) ; deux actions périmées corrigées ; `derniere_revue` passe de `2026-10-13` à `2026-10-20`, prochaine revue avant le 2026-11-19.
- **Résultat :** 16 initiatives dont une nouvelle, une carte de 19 sujets ouverts avec leur exigence de preuve, et deux points de divergence fermés (sonde de production à 23 cibles, chiffres publics recalculés).
- **Limite :** la carte ne recherche aucune source et ne dit rien de la qualité des fiches existantes. Un sujet absent du référentiel reste invisible : elle décrit une carte de travail, pas un inventaire du savoir. L'exigence de preuve suit le domaine déclaré, donc un sujet de santé rangé sous « études supérieures » (ISCED-F 09) reçoit l'exigence générale.
- **Contrôles réellement exécutés :** `construire-carte-lacunes.py` (génération puis `--verifier`), test négatif de divergence, `verifier-rd-continue.py` (16 initiatives, carte synchronisée, revue au 2026-10-20), plus la porte complète.
- **Prochaine action :** ouvrir **un seul** sujet sans fiche du domaine « langues étrangères » (`Écoute, prononciation et ressources audio accessibles`), écrire sa carte de sujet, puis chercher des sources primaires datées ; laisser le sujet ouvert si aucune source accessible ne le documente.

## 2026-10-20 — La sonde de production couvre enfin les ressources que les pages demandent

- **Initiative :** `coherence-textes-publics`.
- **Signal :** la revue de cohérence cherchait une divergence entre ce que le site demande et ce qui est contrôlé. Elle en a trouvé une : la sonde d'en-têtes vérifiait 19 fichiers, mais aucune des trois icônes PNG ni `llms.txt`, pourtant demandés par les 94 pages depuis l'ajout de l'icône 192 px.
- **Constat :** `outils/verifier-publication.py` liste ses cibles à la main (`CIBLES`). Une ressource ajoutée aux pages n'y entre pas d'elle-même : une icône publiée avec un mauvais type MIME ou un 404 serait passée inaperçue jusqu'à ce qu'un navigateur la réclame.
- **Décision :** ajouter les quatre cibles manquantes — `favicon-32.png`, `favicon-192.png`, `apple-touch-icon.png` (`image/png`) et `llms.txt` (`text/plain`). La sonde passe de 19 à 23 fichiers.
- **Preuve exécutée localement :** `python3 outils/verifier-publication.py --base-url http://127.0.0.1:4180/` → **23 fichiers contrôlés, tous 200**, types MIME conformes (dont `image/png` pour les deux icônes et `text/plain` pour `llms.txt`). L'absence de `Content-Encoding` signalée sur ce passage est normale : le serveur local n'est pas un replica de production.
- **Limite :** la confirmation en production viendra du prochain passage du workflow de vérification de publication, qui met à jour l'issue #90 ; elle n'a pas pu être forcée depuis la session.
- **Contrôles réellement exécutés :** sonde locale sur 23 cibles, plus la porte complète (seize contrôles et `py_compile`).

## 2026-10-20 — Les chiffres publics sont recalculés, plus recopiés

- **Initiative :** `coherence-textes-publics`.
- **Signal :** ranger les points en attente et les divergences. La revue en lecture seule du 20 octobre n'a trouvé **aucun écart de chiffre** : 81 fiches, 26 initiales et 55 prototypes dans `catalogue.toml`, 15 domaines dans `referentiel.toml`, 95 pages publiées, 96 fichiers HTML dans le dépôt (dont `docs/pistes-visuelles-ia.html`, non publié), 94 URL de sitemap (95 pages moins la 404 `noindex`), 131 fichiers publiés, 4 606 références résolues. Le risque n'était donc pas un écart existant, mais l'absence de garde-fou : les totaux étaient écrits en dur dans trois pages et vérifiés par comparaison de texte avec eux-mêmes.
- **Constat :** `verifier-integration.py` exigeait la présence littérale de « 81 fiches dans 15 domaines » et « 55 prototypes explicitement à relire » dans la page de transparence. Ajouter une fiche au catalogue aurait laissé la page mentir et le contrôle passer au vert.
- **Décision :** recalculer les nombres depuis les fichiers de référence, puis les chercher dans les pages. `chiffres_publics_coherents()` lit `catalogue.toml` et `referentiel.toml`, compte les statuts éditoriaux, compte les fichiers HTML réels du dépôt, et confronte `apprendre.html`, `transparence.html` et `anglais-aventure.html`. Deux tests négatifs ont prouvé que le contrôle mord : une page HTML témoin ajoutée dans `docs/` fait échouer l'attente « 96 pages HTML du dépôt », et « 82 fiches dans 15 domaines » écrit dans la transparence fait échouer la comparaison au catalogue. Les témoins n'ont pas été conservés.
- **Points en attente soldés dans la même passe :** l'étiquette `planches-statuts-animation-2026-10` a été récupérée dans le clone local (elle y manquait, divergence local/distant) et **les 507 empreintes ont été revérifiées depuis cette étiquette** ; la branche distante absorbée `arena/a1507d48-mrsc` a été supprimée après vérification d'ascendance ; la phrase d'audit du 13 octobre sur `robots.txt`/`llms.txt` a été datée (« à l'audit ») pour ne plus se lire comme une affirmation actuelle alors que `llms.txt` existe.
- **Ce qui reste ouvert, par conception :** la réécriture d'historique (décision argumentée dans `archives-et-poids-du-depot.md`, coût : l'archive, gain côté GitHub : nul sans le support) ; les issues #8 et #90, rapports automatiques recréés à chaque exécution ; les choix éditoriaux listés dans `portefeuille.toml`, qui appartiennent à l'association.
- **Limite :** le contrôle compare des totaux, pas le sens des phrases ; il n'empêche pas une formulation fausse qui réutiliserait un nombre juste.
- **Prochaine action :** étendre la même méthode aux chiffres du simulateur (101 leviers, 52 indicateurs, 11 scénarios) s'ils sont un jour écrits en prose ailleurs que dans des notes datées.

## 2026-10-20 — Réécriture d'historique mesurée : elle coûterait l'archive, et ne ferait pas maigrir GitHub

- **Initiative :** `optimisation-du-site`.
- **Signal :** la demande « `--force` sur `main` » pour supprimer les 1,3 Go de l'historique. Avant d'exécuter, l'opération a été mesurée sur un clone miroir complet plutôt que sur la foi de la procédure ancienne.
- **Constat :** trois essais reproductibles, `git-filter-repo` 2.47.0. (A) purger `main` seule en gardant l'étiquette : **1,27 Gio → 1,27 Gio**, gain nul, l'étiquette référençant les mêmes objets. (B) purger toutes les références : **1,27 Gio → 22 Mio**, mais l'étiquette ne garde plus que trois icônes : les **505 planches sont effacées**, c'est-à-dire exactement la perte que l'archive existait pour empêcher. (C) sur GitHub, chaque proposition de fusion depuis la #85 conserve une référence `refs/pull/<n>/head` qui atteint encore les 506 objets PNG ; ces références ne se réécrivent pas par un `push --force`, donc la taille annoncée ne baisserait pas sans un passage du support. Dans les deux premiers cas, l'arbre de `main` ressort **identique bit à bit** (`8283543`) : la réécriture ne fait perdre aucun fichier de `main`, seulement l'archive.
- **Décision :** ne pas réécrire. La procédure du dossier d'archive est corrigée : l'export vérifié de l'étiquette passe **avant** toute réécriture, et la conservation de l'étiquette est posée comme condition, pas comme formalité. La suppression de l'étiquette qui figurait dans l'ancienne procédure est explicitement signalée comme la perte.
- **Résultat :** `docs/rd/archives-et-poids-du-depot.md` porte les trois scénarios chiffrés, la décision et la procédure conditionnelle ; l'archive reste intacte et **507 empreintes ont été revérifiées depuis l'étiquette seule** avant et après la mesure.
- **Limite :** l'archive ne peut pas être déposée en ressource de version depuis la session : `uploads.github.com` est injoignable (`SSL_ERROR_SYSCALL`), et l'espace de travail est plafonné à ~128 Mo pour un fichier de 1,3 Go. Une copie hors GitHub reste donc à faire par la personne qui administre le dépôt si la réécriture est un jour décidée.
- **Contrôles réellement exécutés :** clone miroir complet (394 commits), `git archive` de l'étiquette + `sha256sum -c` sur 507 fichiers, deux exécutions de `git filter-repo` sur des copies, tailles avant/après `git gc --prune=now`, comparaison des arbres, audit des références `refs/pull/*`, puis la porte habituelle.
- **Prochaine action :** aucune tant que le coût réel (perte de l'archive contre un gain nul côté GitHub) n'est pas accepté explicitement.

## 2026-10-19 — Une ressource livrée sans être citée fait désormais échouer la porte

- **Initiative :** `optimisation-du-site`.
- **Signal :** `favicon-192.png` n'avait été trouvée orpheline qu'à la main, après coup. Rien n'empêchait la même dérive de revenir au prochain ajout d'image.
- **Constat :** `verifier-integration.py` contrôlait qu'une liste fixe de ressources était **présente**, jamais qu'un fichier publié de `assets/` était **cité**.
- **Décision :** ajouter le contrôle inverse, dans l'outil existant plutôt que dans un nouveau script. Le périmètre publié est emprunté à `verifier-publication-locale.py` (l'étape de préparation du site), donc un fichier jamais livré n'est pas jugé. Une ressource est citée si son chemin publié ou son nom apparaît dans un autre fichier publié.
- **Preuve que le contrôle mord :** un fichier témoin ajouté dans `assets/images/` fait échouer le contrôle avec son chemin exact, puis la suppression du témoin le fait repasser au vert. Le témoin n'est pas resté dans le dépôt.
- **Résultat :** 32 ressources publiées, aucune orpheline ; 131 fichiers publiés lus. La règle est inscrite dans `AGENTS.md`, section « Fusionner et importer sans perte ».
- **Limite :** le contrôle compare des noms et des chemins dans du texte, pas des URL résolues ; une ressource citée uniquement via un chemin construit dynamiquement passerait pour citée par chance, et une ressource citée par un fichier non publié serait signalée à tort (cas inexistant aujourd'hui).
- **Contrôles réellement exécutés :** `verifier-integration.py` complet (tous les contrôles passent), plus la démonstration d'échec ci-dessus.
- **Prochaine action :** étendre le contrôle aux fichiers de `docs/` servis par le site si un jour ce périmètre s'ouvre.

## 2026-10-19 — L'icône 192 px branchée sur les 94 pages, plus aucune ressource orpheline

- **Initiative :** `optimisation-du-site`.
- **Signal :** finir le ménage sans rien perdre et sans laisser de ressource livrée pour rien. `assets/images/favicon-192.png` était la seule ressource encore servie sans être citée par aucune page.
- **Constat :** l'icône 192 px a une empreinte et des dimensions distinctes de `favicon-32.png` et d'`apple-touch-icon.png` : ce n'était pas un doublon, donc la supprimer aurait été une perte. Elle restait pourtant inutilisée, téléchargée sans jamais servir.
- **Décision :** la brancher plutôt que la supprimer — une balise `icon` 192×192 déclarée après celle de 32 px, sur les treize pages racine et dans le gabarit des fiches, puis génération des 81 fiches par leur générateur (aucune retouche à la main). L'icône entre aussi dans la liste des ressources contrôlées par `verifier-integration.py`.
- **Résultat :** plus aucune ressource orpheline ; les navigateurs à forte densité et Android disposent d'une icône de bonne taille ; 4 606 références internes vérifiées, toutes résolues.
- **Limite :** aucun manifeste d'application web n'est ajouté : l'icône sert d'icône d'onglet et de raccourci, pas d'installation PWA. Les effets visuels n'ont pas été comparés à l'œil sur un écran haute densité.
- **Contrôles réellement exécutés :** `construire-apprentissages --verifier` (81 fiches synchronisées), `verifier-publication-locale` (131 fichiers, 95 pages, 4 606 références, 16 fichiers racine), `verifier-site-statique`, `verifier-poids-pages`, `verifier-integration` (icône servie), `verifier-securite`, `optimiser-images --verifier`, `verifier-planches-statuts`, `verifier-fusions`, `verifier-rd-continue`, `py_compile`.
- **Prochaine action :** si une installation PWA devient utile, ajouter alors un manifeste et des icônes 512 px, avec la même règle : aucune ressource livrée sans être citée.

## 2026-10-19 — Doublons inutiles retirés du dépôt, rien d'autre en attente

- **Initiative :** `optimisation-du-site`.
- **Signal :** demande de ne plus rien laisser en attente, de fusionner ce qui reste et de supprimer les doublons inutiles.
- **Constat :** aucune proposition de fusion n'était ouverte et aucune branche distante ne subsistait hors `main`. Deux fichiers sans usage subsistaient en revanche dans l'arbre : `assets/images/favicon.ico`, **octet pour octet identique** à `favicon.ico` et cité par aucune page, et `assets/documents/.gitkeep`, marqueur de dossier vide alors que trois PDF y sont versionnés.
- **Décision :** retirer ces deux fichiers, sans toucher à `assets/images/favicon-192.png`, qui n'est pas un doublon (empreinte et dimensions distinctes) mais une ressource encore non branchée : la supprimer serait une perte, pas un ménage.
- **Résultat :** deux fichiers en moins, 15 Ko et un marqueur ; périmètre publié ramené à 132 fichiers, 95 pages, 4 512 références internes toujours résolues.
- **Limite :** `favicon-192.png` reste livré sans être cité ; le brancher demanderait de modifier les 94 pages pour un manifeste d'icônes, décision éditoriale non prise ici.
- **Contrôles réellement exécutés :** recherche d'occurrences du doublon dans toutes les pages, scripts, feuilles de style et documents (aucune) ; `verifier-site-statique`, `verifier-publication-locale`, `verifier-poids-pages`, `verifier-planches-statuts`, `verifier-fusions`, `verifier-integration`, `verifier-securite`, `optimiser-images --verifier`, `verifier-rd-continue`, `py_compile` — tous réussis.
- **Prochaine action :** décider, avec la personne responsable, si `favicon-192.png` sert à un manifeste d'icônes ou retourne dans l'archive.

## 2026-10-19 — L'aperçu local avait sa propre liste de fichiers et divergeait du site

- **Initiatives :** `optimisation-du-site`, `coherence-textes-publics`.
- **Signal :** vérification générale de l'état du dépôt et de l'aperçu local avant de conclure que tout est en ordre.
- **Constat :** `outils/serveur-local.py` portait sa **propre liste blanche** de fichiers racine (`FICHIERS_RACINE_PUBLICS`). Elle avait la même lacune que le workflow de publication : le favicon en était absent. L'aperçu local renvoyait donc 404 sur `favicon.ico` alors que le dépôt et le site publié le servent. Deux listes écrites à la main pour la même chose finissent toujours par diverger.
- **Décision :** ne pas se contenter de corriger la liste ; rendre la divergence impossible à ignorer. Le vérificateur de publication lit désormais la liste blanche de l'aperçu dans le code du serveur et la compare à l'ensemble des fichiers racine réellement publiés.
- **Résultat :** `favicon.ico` servi par l'aperçu ; 136 URL du site servies en local contrôlées, toutes en 200, favicon et routes `/api/…` comprises ; l'alignement des deux listes est vérifié à chaque proposition.
- **Limite :** l'aperçu local reproduit les listes de publication, pas les en-têtes d'un hébergeur ; il ne remplace ni le contrôle réseau de `verifier-publication.py` ni un essai sur le site publié.
- **Contrôles réellement exécutés :** `verifier-publication-locale` (133 fichiers, 95 pages, 4 512 références, 16 fichiers racine alignés) et son cas d'échec simulé ; balayage d'accessibilité axe-core **192 exécutions, 0 violation** sur toutes les pages aux deux largeurs ; **8/8 essais navigateur** ; 136 URL locales en 200 ; porte de vérification complète.
- **Prochaine action :** conserver la règle — toute liste qui décrit le site publié doit être comparée à celle du workflow de publication, jamais maintenue à la main en parallèle.

## 2026-10-19 — Fusionner et importer sans perte : contrôle ajouté et branches absorbées supprimées

- **Initiative :** `coordination-de-tous-les-agents`.
- **Signal :** exigence que toute fusion ou import se fasse sans perte de contenu et sans laisser d'erreur ouverte.
- **Constat :** après la vague de fusions, cinq branches distantes subsistaient sans proposition ouverte. Leur contenu était absorbé par `main`, mais rien ne le prouvait, et rien n'empêchait qu'une branche portant un travail unique soit supprimée par inadvertance.
- **Décision :** écrire le critère de non-perte au lieu de l'estimer. Une branche est supprimable si **tous ses blobs restent atteignables depuis les autres références** ; l'outil `outils/verifier-fusions.py` le calcule et refuse de déclarer supprimable une branche qui porte un contenu unique. Il contrôle aussi, hors ligne, l'absence de fusion inachevée, de fichier non fusionné, de marqueur de conflit, de sauvegarde `.orig`/`.rej`, et l'ordre antichronologique du journal.
- **Résultat :** les cinq branches (`arena/1630fc34`, `arena/5570078e`, `arena/7d6aa1e7`, `arena/a708368f`, `arena/cd07d282`) ont été vérifiées « supprimable sans perte » puis supprimées ; il ne reste que `main`. Les 505 planches de `arena/cd07d282` restent récupérables : l'archive de l'étiquette a été re-vérifiée après suppression, 507 fichiers conformes.
- **Outillage :** `verifier-fusions.py` entre dans la porte de vérification et dans `AGENTS.md`, qui gagne une section « Fusionner et importer sans perte » ; un workflow `audit-branches.yml` relit les branches une fois par mois et à la demande.
- **Limite :** le contrôle de suppression porte sur l'accessibilité des objets, pas sur leur intérêt ; une branche peut être « supprimable sans perte » et contenir un travail que personne n'a relu. La décision éditoriale reste humaine.
- **Contrôles réellement exécutés :** audit des cinq branches avant suppression ; cas d'échec simulés (contenu unique sur une branche, marqueur de conflit, fichier `.orig` suivi) tous refusés ; après suppression, audit sans branche hors `main` et `sha256sum -c` sur l'archive (507 conformes) ; porte de vérification complète.
- **Prochaine action :** lancer `audit-branches.yml` à la demande avant toute nouvelle suppression, et ne jamais résoudre un conflit en écartant un côté sans avoir comparé les deux.

## 2026-10-19 — La lecture des en-têtes suit la publication au lieu de la précéder

- **Initiative :** `optimisation-du-site`.
- **Signal :** après la fusion du correctif du favicon, `Vérifier les en-têtes servis par l'hébergement` a échoué sur `main` alors que le fichier était correct.
- **Constat :** ce contrôle était déclenché sur `push` vers `main`, en même temps que la publication. Il interrogeait donc l'ancienne version du site — celle qui n'avait pas encore le favicon — pendant que la nouvelle se déployait. L'échec était un artefact de course, pas un défaut du site.
- **Décision :** déclencher la lecture des en-têtes à la fin de la publication (`workflow_run` sur « Publish M.R.S.C site »), pour interroger la version réellement servie. Le déclenchement manuel et la revue mensuelle restent en place.
- **Résultat :** plus de faux échec ; le contrôle porte sur l'état publié, et il intègre désormais le favicon.
- **Limite :** la lecture dépend du bon déroulement de la publication ; si celle-ci échoue, les en-têtes ne sont pas relus — ce qui est le comportement attendu, mais laisse le dernier relevé en place.
- **Contrôles réellement exécutés :** fusion du correctif, publication Pages réussie, puis lecture des en-têtes déclenchée par la publication.
- **Prochaine action :** consulter le rapport d'en-têtes dans l'issue de suivi pour confirmer que `favicon.ico` répond bien en 200 avec un type d'image.

## 2026-10-19 — Le site publié manquait d'un fichier : le favicon

- **Initiatives :** `optimisation-du-site`, `coherence-textes-publics`.
- **Signal :** exigence que le contenu complet du dépôt se retrouve sur le site publié. Le dépôt contient 95 pages et leurs ressources ; encore faut-il que la copie de publication les emporte toutes.
- **Constat :** le workflow `deploy-pages.yml` ne publie qu'une liste explicite. Arrêté le 15 octobre 2026 avec le favicon (proposition #57), celui-ci n'a jamais été ajouté à cette liste. Les 94 pages du site demandaient donc `/MRSC/favicon.ico` et recevaient une erreur : onglet sans icône, et un fichier du dépôt absent du site. Aucun contrôle ne pouvait le voir, car `verifier-site-statique.py` valide les liens dans le dépôt, où le favicon existe.
- **Décision :** reconstruire localement le périmètre publié à partir du workflow lui-même, puis vérifier que tout ce que les pages demandent y figure ; publier `favicon.ico` ; rendre le contrôle permanent.
- **Outil :** `outils/verifier-publication-locale.py` relit la liste de copie, reconstitue les 133 fichiers publiés et contrôle 4 512 références internes, les `url()` des feuilles de style et les 94 adresses du sitemap. Il refuse aussi toute page publique du dépôt absente de la liste de copie.
- **Résultat :** le périmètre publié est complet ; les 95 pages du site ont leurs ressources, favicon compris. Le contrôle tourne à chaque proposition et avant chaque publication.
- **Limite :** le contrôle porte sur la liste de copie, pas sur ce que GitHub sert réellement : un hébergeur peut encore modifier en-têtes, types MIME ou compression. `verifier-publication.py` reste le contrôle réseau, et il inclut désormais le favicon.
- **Contrôles réellement exécutés :** cas d'échec simulés (favicon retiré de la liste, page ajoutée sans publication) puis `verifier-publication-locale`, `verifier-site-statique`, `verifier-poids-pages`, `verifier-securite`, `verifier-integration`, `verifier-planches-statuts` et la porte complète.
- **Prochaine action :** vérifier le favicon servi sur le site après la publication, via `outils/verifier-publication.py --base-url https://thejmimiia-code.github.io/MRSC/`.

## 2026-10-19 — Planches conservées sans perte et archive scellée

- **Initiative :** `direction-artistique-motion`.
- **Signal :** exigence explicite de ne rien perdre, ni en qualité ni en fonction, après la sortie des planches de l'arbre.
- **Décision :** mesurer l'écart de chaque conversion au lieu de le supposer ; remplacer les douze WebP qualité 82, qui modifiaient plus d'un million de pixels par planche, par des **WebP sans perte** (écart pixel nul) ; sceller l'archive d'un manifeste SHA-256 des 507 fichiers d'origine, vérifiable en une commande ; ajouter `outils/verifier-planches-statuts.py` à la porte de vérification, y compris le contrôle des liens d'image de `docs/rd/`, qui ne l'étaient pas jusque-là.
- **Résultat :** les douze planches de l'arbre sont identiques aux PNG d'origine (AE = 0) pour 14,7 Mo au lieu de 31,4 Mo ; l'archive est vérifiée conforme sur ses 507 fichiers ; le vérificateur refuse une planche citée absente, un PNG réintroduit ou un manifeste incomplet.
- **Contrôle des liens :** 205 liens d'image des documents de `docs/rd/` recensés, dont 193 vers l'archive ; un lien non résolu et non archivé fait désormais échouer la porte.
- **Limite :** la conversion préserve les pixels, pas les octets : les `.webp` conservés ne sont pas identiques fichier par fichier aux `.png` archivés, et les planches restent « à relire ».
- **Contrôles réellement exécutés :** `compare -metric AE` sur les douze planches (0 après conversion), `sha256sum -c` sur l'archive extraite (507 conformes), `verifier-planches-statuts` et ses trois cas d'échec simulés, puis la porte de vérification complète.
- **Prochaine action :** conserver cette règle pour toute nouvelle planche — archive étiquetée, manifeste d'empreintes, et WebP sans perte dans l'arbre.

## 2026-10-19 — Planches des statuts sorties de l'arbre, originales archivées

- **Initiative :** `direction-artistique-motion`.
- **Signal :** les 505 planches entrées avec la PR #85 pesaient 1 290,9 Mo et n'étaient ni publiées ni validées ; le dépôt dépassait le seuil d'alerte de GitHub et chaque clone téléchargeait 1,3 Go.
- **Décision :** conserver dans l'arbre les douze planches réellement citées par le plan, converties en WebP qualité 82 (1,4 Mo) ; archiver les 493 autres et les originaux PNG dans l'étiquette `planches-statuts-animation-2026-10`, qui fige l'état du dépôt avant retrait ; documenter la procédure dans `docs/rd/archives-et-poids-du-depot.md` ; ignorer les futurs `*.png` de ce dossier.
- **Résultat :** arbre de `main` ramené de 1 299,7 Mo à 10,3 Mo et de 853 à 361 fichiers ; `docs/rd/statuts-animation/` de 1 290,9 Mo à 1,6 Mo. Le site publié n'est pas concerné, `docs/` restant exclu de Pages et de Vercel.
- **Limite :** l'historique Git conserve les 1,29 Go, donc le clonage reste à 1,3 Go tant que `main` n'est pas réécrit ; la fidélité visuelle des douze WebP n'a pas été contrôlée à l'œil, et les planches restent « à relire ».
- **Contrôles réellement exécutés :** mesure des arbres avant et après (`git ls-tree -rl`), conversion et vérification des dimensions (`identify`), `verifier-site-statique`, `verifier-rd-continue`, `verifier-securite`, `verifier-poids-pages`, `optimiser-images --verifier`.
- **Prochaine action :** télécharger l'archive de l'étiquette, puis réécrire l'historique (`git filter-repo`) avec l'accord explicite de la personne qui administre le dépôt ; ne plus committer de PNG hors des étiquettes d'archive.

## 2026-10-19 — Fusions du 19 octobre : point, contrôle d'intégrité et liens de la bible

- **Initiatives :** `direction-artistique-motion`, `relire-les-44-prototypes`, `optimisation-du-site`, `prospective-apprentissages-2030`, `vote-distanciel-verifiable`.
- **Signal :** six propositions de fusion étaient ouvertes sur `main` et toutes en conflit. Le clone local était tronqué à `c67a941`, ce qui masquait la divergence réelle et faisait passer `main` pour un ancêtre direct des six branches : sans remise en profondeur, aucune mesure de conflit n'est fiable.
- **Décision :** faire le point avant toute fusion, puis distinguer apport nouveau et travail déjà intégré. Une seule proposition apportait encore quelque chose, la #85, plan d’animation des statuts, 60 commits et 583 lignes de fond. Les cinq autres avaient été écrites sur une version antérieure des mêmes fichiers, et `main` avait depuis intégré un travail équivalent ou plus abouti. Preuve directe : résoudre leurs conflits avec le contenu de `main` redonne un arbre strictement identique à celui de `main`.
- **Résultat :** les six propositions ont été fusionnées par la personne responsable du dépôt, puis l’ordre du journal rétabli dans la proposition #129 et le poids des planches traité dans les propositions #130 et #132. L’arbre ne garde plus que les douze planches citées par le plan, en WebP sans perte (écart pixel nul, 14,7 Mo au lieu de 31,4 Mo), les 493 autres sont archivées dans l’étiquette `planches-statuts-animation-2026-10` avec un manifeste SHA-256 des 507 fichiers d’origine, et `verifier-planches-statuts.py` contrôle citations, archive et manifeste. L’arbre tombe à 23,6 Mo et 363 fichiers. Le point d’analyse est dans [`docs/rd/fusions-du-19-octobre-2026.md`](fusions-du-19-octobre-2026.md) ; le poids, dans [`docs/rd/archives-et-poids-du-depot.md`](archives-et-poids-du-depot.md).
- **Contrôle d’intégrité :** aucune perte de contenu. Les entrées du journal correspondent, corps compris, à l’ensemble des entrées des six propositions ; `verifier_registre`, `verifier_sources`, `verifier_chaine_logicielle`, `verifier_resultats` et `verifier_revues` sont présents ; `etat_trace_decision` garde sa signature étendue ; `vote-distanciel-sources.toml` a conservé `points_a_resoudre` et `preuves_a_chercher`.
- **Une coquille corrigée :** la ligne « **Contrôles réellement exécutés :** » de l’entrée « Plan films d’animation des statuts » avait perdu une lettre, « **Contr ôles réellement exécutés :** » ; la ligne est rétablie. C’est la seule ligne du journal modifiée par cette passe.
- **Liens de la bible :** le retrait des planches de l’arbre a rendu non résolus les 193 liens d’image de `docs/rd/statuts-animation/bible-fil-et-video-01.md`, que la porte du dépôt ne contrôlait pas. Le plan avait reçu une mention d’archive, la bible non : une mention identique y a été ajoutée, qui indique où sont les planches et que les liens désignent les versions archivées. Le manque a été comblé ensuite en amont, dans la proposition #133 : `verifier-planches-statuts.py` contrôle désormais les 205 liens d’image de `docs/rd/`, et un lien vers un fichier ni présent ni archivé fait échouer la porte.
- **Contrôles réellement exécutés :** `py_compile` ; `verifier-rd-continue.py` ; `construire-apprentissages.py --verifier` ; `construire-simulateur.py --verifier` ; `verifier-site-statique.py` ; `optimiser-images.py --verifier` ; `verifier-poids-pages.py` ; `verifier-securite.py` ; `verifier-integration.py` ; `verifier-decision-prospective.py` ; `verifier-vote-distanciel.py` ; `test_verifier_vote_distanciel.py` ; `test_verifier_decision_prospective.py` ; `file-relecture.py --verifier` ; `verifier-resilience-statutaire.py` et son test. Les quinze commandes réussissent.
- **Limite :** ce relevé ne juge pas le fond des propositions, dont les planches restent « à relire ». Le contrôle des liens tolère les 193 liens de la bible parce qu’ils sont au manifeste, mais il vérifie qu’un fichier de ce nom existe, pas qu’il s’agit bien de la planche voulue. La réécriture d’historique qui retirerait les 1,29 Go du référentiel reste à décider par la personne qui administre le dépôt.
- **Prochaine action :** décider du sort de l’historique, qui conserve les 1,29 Go des planches.

## 2026-10-19 — Ménage des propositions de fusion et des branches résiduelles

- **Initiative :** `coordination-de-tous-les-agents`.
- **Signal :** aucune proposition de fusion n'était plus ouverte, mais deux branches distantes restaient en attente et le dépôt s'était alourdi de 1,29 Go de planches apportées par la PR #85.
- **Décision :** reprendre le travail R&D resté sur `arena/1f836c07-mrsc` (fiches de rédaction, angles morts, variantes, mouture globale) après remise du journal en ordre antichronologique ; supprimer `arena/7d6aa1e7-mrsc`, qui ne portait qu'un doublon de la fusion #85, une note d'état devenue fausse et le retrait de treize lignes de contrôles du vérificateur de vote distanciel.
- **Résultat :** `main` réunit les quatre documents statutaires et leurs contrôles (19 fiches, 16 angles morts, 15 arbitrages, 9 modifications candidates) ; il ne reste plus qu'une branche de travail, celle de la session en cours.
- **Limite :** les planches restent « à relire » et le fond statutaire n'est ni adopté ni validé ; le sort des 506 PNG sous `docs/rd/statuts-animation/` (1,29 Go, non publiés) n'est pas tranché ici et pèse sur le clonage du dépôt.
- **Contrôles réellement exécutés :** `py_compile`, `verifier-rd-continue`, `construire-apprentissages --verifier`, `construire-simulateur --verifier`, `verifier-site-statique`, `optimiser-images --verifier`, `verifier-poids-pages`, `verifier-securite`, `verifier-integration`, `verifier-decision-prospective`, `verifier-vote-distanciel`, `test_verifier_vote_distanciel`, `test_verifier_decision_prospective`, `file-relecture --verifier`, `verifier-resilience-statutaire`, `test_verifier_resilience_statutaire` — tous réussis.
- **Prochaine action :** décider du sort des planches (retrait de l'arbre avec hébergement externe, ou purge d'historique) avant d'ajouter de nouvelles images au dépôt.

## 2026-10-18 — Mouture globale candidate à trois niveaux

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** consolider les arbitrages en une architecture où les statuts gardent le pouvoir et les droits, le règlement précise les modalités durables et les procédures portent l’exécution révisable.
- **Résultat :** neuf modifications statutaires minimales candidates, vingt-cinq domaines réglementaires, une couche procédurale et un chemin d’adoption séparé.
- **Équilibre :** le fondateur reste gardien de l’intention sans devenir souverain ; l’assemblée décide dans ses compétences ; le Bureau exécute ; éthique, contrôle et recours restent bornés.
- **Limite :** la mouture n’est pas adoptée et ne garantit pas toutes les circonstances ; chaque modification reste soumise aux sources officielles, à l’avis juridique et à la décision compétente.
- **Prochaine action :** confronter les neuf modifications à un test de nécessité, puis préparer un tableau statuts actuels / rédaction candidate / justification / effet / risque.

## 2026-10-18 — Variantes pour préserver la vision sans captation

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** comparer plusieurs solutions pour chaque point sensible au lieu d’imposer immédiatement une rédaction unique.
- **Résultat :** quinze arbitrages documentent variantes, avantages, risques et niveau normatif ; une candidate de travail est indiquée sans sélection.
- **Prospective :** chaque variante est examinée contre deux dérives opposées : captation par une minorité et concentration au profit des organes en place.
- **Optimisation :** le contrôle refuse une variante déclarée sélectionnée, la suppression d’un arbitrage ou une candidate inexistante.
- **Limite :** les candidates expriment une hypothèse de consolidation, pas l’intention juridiquement opposable de l’auteur ni une décision de l’association.
- **Prochaine action :** soumettre les quinze arbitrages au fondateur, à la revue juridique et à l’organe compétent avant toute intégration dans les statuts ou le règlement.

## 2026-10-18 — Couverture croisée et angles morts maintenus ouverts

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** rechercher les trous entre risques, invariants, articles du règlement, preuves et rôles plutôt que déclarer la couverture complète.
- **Résultat :** les seize familles de risques sont reliées aux clauses candidates et invariants ; seize angles morts bloquants ou importants possèdent une condition de sortie et un rôle requis.
- **Optimisation :** le contrôle refuse une famille non couverte, un angle mort fermé sans preuve, un rôle inconnu et toute prétention de couverture validée ou exhaustive.
- **Limite :** une liaison documentaire n’établit pas l’efficacité ; de nouveaux angles morts peuvent apparaître lors des revues et exercices.
- **Prochaine action :** fermer uniquement les angles pour lesquels la preuve attendue est produite et relue, en commençant par les sources officielles et décisions juridiques préalables.

## 2026-10-18 — Fiches de rédaction bornées pour les dix-neuf titres

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** préparer la rédaction titre par titre sans transformer le squelette en règlement adopté.
- **Résultat :** dix-neuf fiches relient sources statutaires, objectif, contenu à rédiger, interdit, preuve attendue et rôles humains requis.
- **Optimisation :** le contrôle refuse une fiche supprimée, un statut prématuré, un rôle inconnu et toute adoption ou effet juridique déclaré.
- **Limite :** ces fiches autorisent seulement une future rédaction candidate ; elles ne résolvent aucune décision préalable et ne prouvent pas l’efficacité des contrôles.
- **Prochaine action :** faire examiner les fiches par les rôles requis, puis rédiger par lots réversibles en conservant chaque blocage.

## 2026-10-18 — Squelette non adopté du règlement intérieur

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** organiser les modalités candidates sans transformer les cinq décisions préalables en règles ni présenter le projet comme adopté.
- **Résultat :** dix-neuf titres et quatre-vingt-deux articles de travail couvrent adhésion, organes, votes, finances, données, discipline, sécurité et continuité.
- **Optimisation :** le vérificateur refuse un projet présenté comme adopté, une lacune de numérotation et la disparition des garde-fous essentiels.
- **Limite :** aucun article ne produit d’effet ; compétence d’adoption, renouvellement des dirigeants, articles 17–18, dissolution et charte restent à trancher.
- **Prochaine action :** faire relire le squelette, puis rédiger des clauses candidates uniquement lorsque source, compétence, preuve et recours sont confirmés.

## 2026-10-18 — Classement normatif proposé pour chaque groupe d’articles

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** distinguer ce qui relève des statuts, du règlement, d’une procédure, d’un niveau mixte ou d’une décision préalable.
- **Résultat :** les vingt groupes possèdent un classement justifié ; l’article 9, le renouvellement des dirigeants, les articles 17–18 et la dissolution restent en décision préalable.
- **Optimisation :** deux tests refusent un article non classé et le déclassement de la dissolution en simple procédure.
- **Limite :** ce classement est une proposition documentaire ; seul un examen juridique et la décision associative peuvent arrêter le niveau normatif.
- **Prochaine action :** rédiger le squelette du règlement uniquement pour les éléments classés `reglement` ou `mixte`, sans convertir les décisions préalables en règles.

## 2026-10-18 — Matrice de traçabilité des vingt groupes d’articles

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** relier chaque partie des statuts à son objet, sa compétence, sa preuve, son recours, sa règle d’urgence et son point restant à trancher.
- **Résultat :** vingt groupes couvrent les pages 3 à 25 ; les articles 17–18 restent sans page inventée et la dissolution reste bloquée pour interprétation juridique.
- **Optimisation :** le vérificateur contrôle désormais la présence des vingt groupes, les champs de traçabilité et les deux blocages de source/interprétation.
- **Limite :** la matrice est une lecture de travail, pas une norme adoptée ni une interprétation juridique opposable.
- **Prochaine action :** faire relire chaque ligne, puis distinguer les clauses relevant des statuts, du règlement intérieur ou d’une procédure opérationnelle.

## 2026-10-18 — Registre contrôlable des risques statutaires

- **Initiative :** `resilience-statutaire-globale`.
- **Décision :** transformer le brainstorming global en registre structuré sans score, probabilité ni prétention d’exhaustivité.
- **Résultat :** huit invariants, seize familles de risques et trois portes bloquantes relient scénarios, actifs, contrôles et conditions d’arrêt.
- **Optimisation :** un vérificateur et cinq tests empêchent suppression silencieuse, validation prématurée, porte indicative et promesse d’exhaustivité.
- **Limite :** la structure améliore la couverture documentaire mais ne prouve ni efficacité des contrôles, ni légalité, ni absence de scénario inconnu.
- **Prochaine action :** attribuer les revues, réunir les documents absents et convertir chaque contrôle retenu en clause ou procédure reliée à sa source statutaire.

## 2026-10-18 — Plan global de résilience et prévention des détournements

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** cartographier les dynamiques croisées des statuts, les captations internes ou externes, les crises et les erreurs avant de rédiger le règlement intérieur.
- **Résultat :** seize familles de scénarios, cinq niveaux de continuité, vingt-et-un chapitres de règlement, cinq portes de décision et une feuille de route consolidée.
- **Revue contradictoire :** le plan traite également les abus possibles des mécanismes de protection eux-mêmes : urgence prolongée, conseil d’éthique capturé, contrôle centralisé et recours supprimé.
- **Limite :** aucun texte ne peut être exhaustif ou étanche ; le plan ne modifie pas les statuts, ne crée aucun pouvoir public et reste à relire juridiquement et démocratiquement.
- **Prochaine action :** réunir les documents absents, produire la matrice article–compétence–preuve–recours et faire distinguer ce qui relève des statuts, du règlement ou d’une procédure.

## 2026-10-18 — Pré-vérification juridique complète des statuts

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** relire les 25 pages article par article avant de poursuivre le QCM et la rédaction du règlement intérieur.
- **Résultat :** une note de cohérence interne recense les questions de gouvernance, corps électoral, finances, sanctions, assemblées et dissolution ; les orientations déjà données par le fondateur sont séparées des règles actuellement écrites.
- **Revue contradictoire :** une seconde passe a recherché conflits de compétence, définitions absentes, règles spéciales et procédures sans recours ; aucun sous-agent indépendant n’était disponible.
- **Limite :** cette pré-vérification n’est ni un avis juridique ni une validation ; le droit positif actuel et la version déposée restent à confronter à des sources officielles et à une personne compétente.
- **Prochaine action :** obtenir les documents absents, faire répondre un relecteur juridique aux douze questions bornées, puis reprendre le QCM sur la majorité d’adoption du règlement.

## 2026-10-18 — Six présentations par intention derrière « Présentation »

- **Initiative :** `optimisation-du-site` (avec la carte `direction-artistique-motion`).
- **Signal et demande :** produire d’autres personnalisations de présentation via le bouton prévu, avec des compositions pertinentes qui donnent envie de profiter des contenus.
- **Décision :** ajouter trois rythmes CSS aux trois choix existants — « Vitrine » (aéré, grands titres, grandes tuiles), « Mosaïque » (tuiles variées sans flux dense ni réordonnancement) et « Compacte » (dense, pour balayer et comparer) — plus un mini-aperçu schématique et une ligne « Idéal pour : … » par choix, sur le site et dans le simulateur autonome généré. « Équilibrée » reste le défaut ; contenu, ordre de lecture et fonctions inchangés. Étude, motifs retenus ou écartés et arbitrages dans [`presentations-personnalisees.md`](presentations-personnalisees.md).
- **Options écartées ou différées :** mode sombre complet (197 couleurs hexadécimales sans inventaire de jetons), rangées horizontales de découverte personnalisée (reflow et profil), surfaces translucides décoratives (contraste), palette recalculée automatiquement selon l’environnement de la personne (palette vérifiée), colonnes magazine pour le texte courant et animations au défilement.
- **Défauts observés et corrections pendant l’intégration :** titres Vitrine trop grands à 320 px (17 puis 15 px de débordement mesurés, planchers abaissés) ; bouton long d’aside de fiche (élargissement des boutons retiré) ; nom de domaine incassable en pistes étroites (coupe autorisée) ; bouton « interactions » et sources sans espace du simulateur en pistes de 200 px (repli du moteur appliqué) ; débordement préexistant de Panorama sur les étapes « IA & société » à 320 px (listes d’étapes exclues des collections). Un débordement d’en-tête de 59 px à 1 440 px dans le navigateur sans interface des essais est identique dans les six modes et sur le commit de départ : préexistant, à requalifier dans un navigateur graphique.
- **Requalification et correctif d’en-tête (même jour) :** la rangée de navigation (neuf ou dix liens + Parcours/Affichage/Présentation) mesure ~1 350 à ~1 565 px sans repli possible dans un conteneur limité à la colonne de contenu (1 160 px) : débordement mesuré de 1 280 px à ~1 600 px de fenêtre (3 à 139 px selon page et largeur), susceptible de tronquer les extrémités selon les polices réelles ou de nouvelles entrées de menu. Correctif CSS : au-delà du seuil de repli (1 261 px), la rangée utilise toute la fenêtre (plafond 104 rem) et peut passer sur deux lignes plutôt que de tronquer ; en-tête compact et modes 125/150 % inchangés par spécificité supérieure. Preuves dans l’environnement d’essai : débordement nul de 1 280 à 1 920 px sur l’accueil (neuf liens) et le catalogue (dix liens), captures d’en-tête à 1 440 et 1 920 px sans élément tronqué, essais navigateur 8/8, assertion ajoutée au vérificateur d’intégration. Relecture visuelle humaine toujours due ; statut inchangé `a-tester`.
- **Contrôles réellement exécutés :** porte complète du dépôt (`py_compile`, vérificateurs R&D, apprentissages, simulateur régénéré, site statique, images, poids, sécurité, intégration étendue aux six choix, `node --check`, `git diff --check`) ; `outils/test-experience.cjs` dans un navigateur sans interface : 8/8, y compris la boucle Vitrine/Mosaïque/Compacte sur le catalogue ; matrice ponctuelle hors dépôt de 144 cas (8 pages × 3 largeurs × 6 modes) sans débordement imputable aux modes après corrections. Détail et limites dans la note R&D.
- **Limites :** aucun essai avec des personnes, aucun lecteur d’écran, aucun autre moteur de navigateur, aucune relecture visuelle humaine ni vérification après publication ; l’utilité et la compréhension des libellés/aperçus restent des hypothèses (tâche candidate B7 à relire).
- **Prochaine action :** revue visuelle humaine des six présentations (accueil, catalogue, fiche, dossier IA, simulateur) et de l’en-tête corrigé dans un navigateur graphique, puis essais volontaires seulement après relecture du protocole ; garder l’initiative à l’état `a-tester`.

## 2026-10-18 — Inventaire des couleurs et plan de jetons (aucune valeur modifiée)

- **Initiative :** `optimisation-du-site`.
- **Signal et demande :** suite des présentations et du correctif d’en-tête du même jour — réaliser l’inventaire de couleurs que le § 6 de [`rd-affichage-adaptatif.md`](../rd-affichage-adaptatif.md) pose comme préalable à toute variante sombre.
- **Résultat :** [`inventaire-couleurs-jetons.md`](inventaire-couleurs-jetons.md). Feuille principale : 188 occurrences hexadécimales hors définitions initiales (91 valeurs distinctes) et 103 fonctions couleur ; feuille de l’aventure : 231 occurrences (131 distinctes), sans `:root` propre ; habillage du simulateur : 66 occurrences ; pages et 81 fiches sans couleur propre hors métadonnée `theme-color`. Hors périmètre « thème » : palette sombre propre du moteur du simulateur (déjà en variables dans la page générée) et palettes des scènes illustrées de l’aventure (190 littéraux de dessin). Lecture par rôles : grappe de textes secondaires « ardoise » (8 valeurs voisines, 28 occurrences) parallèle à `--muted`, fonds teintés par famille (20 valeurs, 36 occurrences), bordures, accents texte foncés ; contrastes de référence du thème clair tous au-dessus de 4,5:1 sur blanc (plus faible : `--muted` à 5,00:1). Deux blocs de contraste renforcé redéfinissent déjà les onze jetons : le mécanisme de variante par jetons existe.
- **Décision :** aucune valeur de couleur ni aucun fichier de style ou de code modifié dans cette passe. Plan en trois phases proposé dans la note : tokenisation par rôle à valeurs strictement identiques dans la feuille principale, puis aventure et habillage du simulateur via son générateur, variante sombre seulement après prototype borné, captures et relecture humaine — décision séparée, non prise.
- **Points relevés pour la phase 1 :** `--white` à double rôle (fond clair et premier plan sur fond marine) à scinder ; quatre libellés de cartes d’accueil en littéraux qui ne suivent pas le contraste renforcé ; une valeur verrouillée par le vérificateur d’intégration (`#bae6fd`) ; base d’ombre `rgba(26,48,91)` distincte de `--navy`.
- **Contrôles réellement exécutés :** comptages et grappes produits par script éphémère (méthode décrite dans la note), calculs de contraste selon la formule de luminance relative, puis vérificateurs documentaires et d’intégration du dépôt. Aucun rendu modifié, donc aucun essai navigateur à refaire pour cette passe.
- **Limites :** inventaire statique (ni couleurs d’images, ni contextes d’empilement réels) ; aucun essai avec des personnes ; le thème sombre reste différé et non promis.
- **Prochaine action :** phase 1 de tokenisation par rôle dans `assets/css/site.css`, à valeurs identiques en thème clair et avec captures avant/après ; garder l’initiative à l’état `a-tester`, la relecture visuelle humaine des présentations et de l’en-tête restant prioritaire.

## 2026-10-18 — Jetons de rôle, phase 1 : 84 littéraux remplacés à valeurs identiques

- **Initiative :** `optimisation-du-site`.
- **Signal et demande :** exécuter la phase 1 du plan de l’inventaire des couleurs du même jour, sans changer le rendu.
- **Résultat :** dix-huit jetons de rôle ajoutés au `:root` de `assets/css/site.css` (textes secondaires, surfaces, fonds teintés, bordures, textes sur fond marine) et 84 littéraux remplacés sur 72 lignes, plan à blanc relu ligne par ligne avant application. Le blanc littéral est réparti selon son rôle vérifié (`--surface` pour les fonds clairs, `--on-navy` pour le chiffre blanc sur pastille marine) ; un anneau décoratif au rôle ambigu reste littéral. Détail, résidu et points ouverts au § 9 de [`inventaire-couleurs-jetons.md`](inventaire-couleurs-jetons.md).
- **Preuve d’identité :** styles calculés porteurs de couleur photographiés avant/après dans un navigateur sans interface sur 8 pages types × 2 largeurs, plus l’accueil en contraste renforcé — 16 582 éléments, 0 différence. Essais navigateur 8/8 et porte complète du dépôt réussis ; assertion verrouillée `#bae6fd` mise à jour et nouveau contrôle d’intégration sur les jetons.
- **Décisions et restes :** les quatre libellés de cartes d’accueil restent des littéraux (arbitrage ouvert, car les aligner changerait le rendu du contraste renforcé) ; les usages existants de `var(--white)` ne sont pas encore scindés ; 104 occurrences hexadécimales ponctuelles et les 103 `rgba()` restent littéraux. Aucune valeur sombre créée.
- **Limites :** identité prouvée au niveau des styles calculés dans l’environnement d’essai (police de repli), pas une relecture visuelle humaine ; états de survol garantis par l’égalité des valeurs des jetons, non photographiés.
- **Prochaine action :** relecture visuelle humaine toujours prioritaire ; ensuite phase 2 (feuille de l’aventure, habillage du simulateur via son générateur), la variante sombre restant subordonnée à un prototype borné et à une décision séparée. État inchangé : `a-tester`.

## 2026-10-18 — Jetons de rôle, phase 2 : aventure et habillage du simulateur

- **Initiative :** `optimisation-du-site`.
- **Signal et demande :** exécuter la phase 2 du plan de l’inventaire des couleurs, toujours sans changer le rendu.
- **Résultat :** feuille de l’aventure — 77 littéraux remplacés sur 69 lignes : 54 par des jetons communs du site non redéfinis en contraste renforcé (`--text-soft`, `--surface`, `--on-navy`…), 23 par quatre jetons locaux `--mondes-*` définis en tête de feuille. Habillage du simulateur — 31 littéraux remplacés dans le seul générateur `outils/construire-simulateur.py`, quatre jetons préfixés `--mrsc-*` sans collision avec le moteur, page autonome régénérée et vérifiée. Verrous du vérificateur d’intégration mis à jour (dégradé du bouton principal) et contrôle de phase 2 ajouté. Détail au § 10 de [`inventaire-couleurs-jetons.md`](inventaire-couleurs-jetons.md).
- **Décision d’ensemble gelé :** vingt-trois littéraux de l’aventure égaux aux jetons d’origine du site (bleu marine, encre, gris, bleu, vert) restent écrits en dur : ces jetons sont redéfinis en contraste renforcé, donc les brancher changerait le rendu de ce seul mode. Même arbitrage ouvert que les libellés de cartes d’accueil de la phase 1 — choix de conception à décider explicitement, avec captures.
- **Preuve d’identité :** styles calculés photographiés avant/après sur 9 pages types × 2 largeurs, contraste renforcé compris pour l’accueil, l’aventure et le simulateur — 41 940 éléments, 0 différence. Essais navigateur 8/8, porte complète du dépôt réussie.
- **Limites :** identité prouvée au niveau des styles calculés dans l’environnement d’essai (police de repli), pas une relecture visuelle humaine ; les thématiques couleur par monde de l’aventure et les valeurs ponctuelles restent littérales, à dessein.
- **Prochaine action :** relecture visuelle humaine toujours prioritaire. La phase 3 (variante sombre) reste subordonnée à un prototype borné, à ses mesures de contraste et à une décision séparée ; l’arbitrage « ensemble gelé » peut être tranché à cette occasion. État inchangé : `a-tester`.

## 2026-10-18 — Arbitrage de l’ensemble gelé : les couleurs de marque suivent le contraste renforcé

- **Initiative :** `optimisation-du-site`.
- **Décision :** brancher sur leurs jetons les littéraux laissés en suspens aux phases 1–2 : les quatre libellés de cartes d’accueil (vert et bleu sur leurs jetons d’origine ; or et rouge sur deux nouveaux jetons d’accent-texte `--gold-ink`/`--red-ink`, les accents de base étant trop clairs pour du texte) et les vingt-trois littéraux de l’aventure égaux aux jetons d’origine du site. Tous les usages ont été relus avant remplacement : éléments foncés sur fonds clairs uniquement.
- **Preuve :** photographie des styles calculés avant/après (24 contextes, 41 940 éléments) — thème par défaut strictement inchangé (0 différence) ; en contraste renforcé, 106 éléments prennent la valeur renforcée de leur jeton, avec des contrastes tous en hausse (gris secondaire 5,00 → 8,97:1 ; bleu 6,97 → 8,88:1 ; marine 12,29 → 15,20:1 ; avatar 9,75 → 12,05:1). Essais navigateur 8/8, porte complète réussie, contrôle d’intégration dédié. Détail au § 11 de [`inventaire-couleurs-jetons.md`](inventaire-couleurs-jetons.md).
- **Limites :** mesures dans l’environnement d’essai (police de repli) ; relecture visuelle humaine toujours due. État inchangé : `a-tester`.

## 2026-10-18 — Prototype sombre borné et non activé : faisabilité partielle

- **Initiative :** `optimisation-du-site`.
- **Démarche :** valeurs sombres candidates pour les seuls jetons de rôle, calculées puis injectées uniquement dans la session du navigateur d’essai — aucun fichier du dépôt ne les contient, rien n’est activé ni publié. Quatre captures (accueil, catalogue, aventure) conservées hors dépôt.
- **Résultat :** les contrastes calculés sont satisfaisants (textes entre 7,56:1 et 15,64:1 sur les fonds de référence), et les zones peintes par les jetons rendent correctement. Mais la variante n’est **pas activable en l’état** : surfaces claires littérales hors jetons (en-tête `rgba(255,255,255,.97)`, dégradés et voiles des sections, panneaux) rendant illisibles les textes éclaircis ; jetons à double rôle (`--navy` en titres quasi illisibles, `--white`) ; composants mixtes texte-en-jeton sur fond littéral.
- **Décision :** ne rien activer. Si la variante sombre est poursuivie, prérequis « phase 2.5 » : résorber les surfaces littérales et scinder les jetons à double rôle — toujours à valeurs identiques en thème clair — puis re-prototyper et décider séparément du déclenchement. Détail et valeurs candidates au § 12 de [`inventaire-couleurs-jetons.md`](inventaire-couleurs-jetons.md).
- **Prochaine action :** relecture visuelle humaine des présentations, de l’en-tête et des captures du prototype ; aucune promesse de thème sombre. État inchangé : `a-tester`.

## 2026-10-18 — Jetons de rôle, phase 2.5 : scission des doubles rôles et surfaces littérales résorbées

- **Initiative :** `optimisation-du-site`.
- **Signal et demande :** exécuter le prérequis « phase 2.5 » issu du prototype sombre borné du même jour, sans changer le rendu ni activer quoi que ce soit.
- **Résultat :** dans `assets/css/site.css`, 234 remplacements à valeurs identiques, plan à blanc relu ligne par ligne : les 78 usages de `var(--white)` répartis par rôle réel (`--surface` ×49, `--on-navy` ×27, `--on-accent` ×2 pour le bouton plein), les 46 premiers plans `var(--navy)` vers le nouveau `--navy-ink` (13 fonds marine conservés), et 110 littéraux — en-tête translucide `--surface-header`, arrêts des dégradés de héros et de sections, voiles, pied et héros sombres, bloc de code, bannière d’état, bordures et encres ponctuelles — vers 77 jetons de rôle. `--navy-ink` est redéfini comme `--navy` en contraste renforcé (classe et préférence système) et en couleurs forcées ; `--surface`, `--on-navy` et `--on-accent` y reçoivent le miroir `Canvas` que `--white` portait. Aventure : 11 premiers plans vers `--navy-ink` (fond d’avatar conservé) ; page 404 et page de pistes alignées. `--white` demeure défini comme alias hérité, sans aucun usage. Détail au § 13 de [`inventaire-couleurs-jetons.md`](inventaire-couleurs-jetons.md).
- **Preuve d’identité :** styles calculés photographiés avant/après sur 26 contextes (9 pages types × 2 largeurs ; contraste renforcé sur l’accueil, l’aventure et le simulateur ; couleurs forcées émulées sur l’accueil et l’aventure) — 26 734 éléments, 0 différence. Un premier passage relevait 120 valeurs transitoires pendant les transitions déclenchées par l’ajout de la classe de contraste ; banc corrigé (transitions neutralisées des deux côtés) et captures rejouées. Essais navigateur 8/8, porte complète du dépôt réussie, contrôle d’intégration « phase 2.5 » ajouté et deux verrous mis à jour.
- **Limites :** identité prouvée au niveau des styles calculés dans l’environnement d’essai (police de repli), pas une relecture visuelle humaine ; résidu littéral motivé (ombres, halos et anneaux d’illustration, alphas ponctuels sur marine, impression). Aucune valeur sombre créée, rien d’activé.
- **Prochaine action :** relecture visuelle humaine toujours prioritaire ; le re-prototype sombre borné peut désormais être tenté sur les seuls jetons, sans décision d’activation. État inchangé : `a-tester`.

## 2026-10-18 — Re-prototype sombre borné après phase 2.5 : feuille principale débloquée, deux résidus à traiter

- **Initiative :** `optimisation-du-site`.
- **Signal et demande :** le prérequis « phase 2.5 » étant rempli, re-prototyper la variante sombre sur les seuls jetons — toujours sans rien activer ni publier de valeur sombre.
- **Résultat :** valeurs candidates du § 12 étendues mécaniquement aux 117 jetons et injectées uniquement dans la session du navigateur d’essai ; contraste mesuré élément par élément (fond effectif, pire cas des dégradés) avec témoin clair par le même banc. Feuille principale : en jetons seuls, 12 textes sous les repères sur 2 368 — uniquement les boutons pleins (2,13:1) ; avec la simulation libellée d’une scission de `--blue`, **0/2 368**. Les trois familles bloquantes du § 12 ont disparu sur ce périmètre ; neuf captures hors dépôt le montrent (accueil, catalogue, transparence, 320 px, simulateur témoin inchangé). Aventure : 439/1 338 textes sous les repères — littéraux des thématiques par monde, périmètre exclu de la phase 2.5. Détail au § 14 de [`inventaire-couleurs-jetons.md`](inventaire-couleurs-jetons.md).
- **Décision :** ne rien activer. Deux bloqueurs résiduels avant toute phase 3 : scinder `--blue` (lien/focus contre surface du bouton plein — insoluble par une seule valeur, remède du même gabarit que la phase 2.5) et résorber les littéraux de l’aventure ou décider son exclusion explicitement. Déclenchement toujours entièrement ouvert.
- **Limites :** mesures et captures d’un navigateur sans interface, police de repli ; dérivation des candidates mécanique (teintes vertes lisant olive, échelle des surfaces douces resserrée) ; survols non mesurés ; combinaison avec le contraste renforcé non prototypée ; aucune relecture visuelle humaine ni essai avec des personnes — requis avant toute décision d’activation.
- **Prochaine action :** relecture visuelle humaine des captures ; si la variante est poursuivie, scission de `--blue` à valeurs claires identiques puis périmètre aventure, avant essais avec personnes concernées et décision séparée. État inchangé : `a-tester`.

## 2026-10-18 — Calcul, contestation et proclamation séparés

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** interdire qu’un total calculé devienne automatiquement un résultat associatif.
- **Résultat :** six étapes cumulatives couvrent gel, vérifications cryptographique et statutaire, incidents, contestation et décision ; le paquet public minimal exclut identités, secrets et journaux.
- **Prospective :** divergence de miroirs, disparition d’un vérificateur et recours exigeant une preuve du choix deviennent des arrêts distincts, sans probabilité.
- **Optimisation :** le contrôle refuse un résultat préautorisé, la suppression de la contestation et une porte de proclamation partielle.
- **Limite :** aucun résultat, recours, procès-verbal ou scrutin réel n’est produit.
- **Prochaine action :** faire relire la chaîne complète par les six rôles après décision associative sur un profil et une option.

## 2026-10-18 — Chaîne logicielle reliée à une porte humaine avant banc

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** exiger sept preuves cumulatives entre source épinglée, dépendances, construction, provenance, écarts, gel des mises à jour et vérification future.
- **Résultat :** une porte bloquante couvre tous les contrôles ; aucun logiciel n’est sélectionné, construit ou exécuté.
- **Prospective :** disparition du fournisseur, mise à jour silencieuse et audit d’une autre version sont traités comme des ruptures de preuve, sans probabilité.
- **Optimisation :** le contrôle refuse une sélection prématurée, la suppression du gel des mises à jour et une porte partielle.
- **Limite :** métadonnées et plans de preuves ne valent ni audit, ni reproductibilité constatée, ni sécurité.
- **Prochaine action :** appliquer cette porte à une seule version candidate uniquement après choix associatif et attribution des revues.

## 2026-10-18 — Cycle projeté des clés borné de la désignation à la destruction

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** formaliser six phases de cérémonie sans primitive locale, secret réel ni autorisation d’exécution.
- **Résultat :** désignation, génération distribuée, vérification, conservation, dépouillement à seuil et destruction comportent preuves, interdits et arrêts ; cinq incompatibilités empêchent la recentralisation.
- **Prospective :** les sauvegardes communes, remplacements silencieux et clés de secours uniques sont traités comme des annulations du seuil, sans probabilité.
- **Optimisation :** le contrôle refuse la cryptographie maison, la suppression de la destruction et l’absence d’interdiction des sauvegardes multi-parts.
- **Limite :** aucune clé, cérémonie, autorité ou solution réelle n’est créée ni déclarée sûre.
- **Prochaine action :** faire confronter ce cycle au protocole précis d’une solution existante après décision associative et attribution des revues.

## 2026-10-17 — Assistance distinguée de la procuration et du choix

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** séparer assistance, support, procuration, recours et protection contre la coercition avant toute définition opérationnelle.
- **Résultat :** six situations synthétiques et quatre séparations fonctionnelles bornent les actes permis, interdits, preuves et conditions d’arrêt.
- **Prospective :** un canal d’aide peut devenir un canal de coercition, de délégation implicite ou de corrélation ; son existence n’est pas une garantie.
- **Optimisation :** le contrôle refuse une assistance exécutable, l’absence de condition d’arrêt et la disparition de la frontière assistance–procuration.
- **Limite :** aucune personne, assistance, procuration, contestation ou suspicion réelle n’est traitée.
- **Prochaine action :** confronter ces frontières au profil statutaire choisi et aux revues juridique, accessibilité, données et cryptographie.

## 2026-10-17 — Accessibilité et repli examinés sans donnée de santé

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** structurer huit barrières et le risque propre à chaque repli sans déclarer de conformité ni autoriser d’essai avec des personnes.
- **Résultat :** clavier, lecteur d’écran, zoom, compréhension, temps, équipement, assistance et vérification indépendante sont reliés à une preuve projetée et à un repli à expertiser.
- **Prospective :** un canal alternatif peut affaiblir secret, égalité ou vérifiabilité ; il n’est donc jamais présumé accessible par sa seule existence.
- **Optimisation :** le contrôle refuse une conformité prématurée, une barrière supprimée et un repli dont le risque n’est pas documenté.
- **Limite :** aucun diagnostic, justificatif de handicap, personne réelle ou résultat d’utilisabilité n’est collecté.
- **Prochaine action :** faire examiner une version candidate précise par le rôle accessibilité avec les autres rôles avant tout essai autorisé.

## 2026-10-17 — Continuité bornée par des arrêts sûrs

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** traiter sept incidents sans automatiser une décision associative ni dégrader les garanties sous prétexte de disponibilité.
- **Résultat :** non-ouverture, gel, suspension ou non-proclamation sont les défauts projetés ; chaque incident exige l’association et les rôles compétents.
- **Prospective :** l’indisponibilité d’une part de clé, du registre d’éligibilité ou des preuves est distinguée d’une fuite ou corrélation, sans probabilité.
- **Optimisation :** le contrôle refuse la suppression d’un incident, un statut opérationnel prématuré et toute réponse sans autorité associative.
- **Limite :** aucune procédure n’est approuvée ou utilisable pour un scrutin réel ; délais, canaux et compétences restent à faire relire.
- **Prochaine action :** confronter ces arrêts aux statuts, à l’accessibilité, aux recours et aux capacités opérationnelles avant tout exercice synthétique.

## 2026-10-17 — Épreuve de corrélation rendue non exécutable

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** formaliser les vues et signaux d’une future épreuve synthétique sans produire de jeu, de code d’attaque ni de seuil numérique.
- **Résultat :** quatre vues d’attaque, cinq signaux et cinq prérequis sont structurés ; `execution_autorisee = false`.
- **Prospective :** la collusion émetteur–urne et la persistance dans les sauvegardes sont traitées comme des scénarios distincts, sans probabilité.
- **Optimisation :** le contrôle refuse un seuil inventé, une autorisation prématurée et toute catégorie étrangère au modèle de données.
- **Limite :** aucune épreuve n’a été exécutée et aucun niveau de corrélation n’est déclaré acceptable.
- **Prochaine action :** faire préenregistrer métrique, référence, seuil et plan de destruction par les revues humaines compétentes.

## 2026-10-17 — Données du vote séparées avant toute collecte

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** modéliser identité, justificatif, bulletin, reçu, preuves, journaux et procurations avant tout essai ; le chiffrement seul ne suffit pas à empêcher une corrélation.
- **Résultat :** huit catégories projetées avec finalité, détenteur, rétention et contenus interdits ; six liaisons interdites, dont identité–bulletin et journal d’émission–journal d’urne. Aucun flux n’est autorisé.
- **Prospective :** les preuves publiques durables et les journaux transitoires sont traités séparément pour éviter qu’un registre append-only conserve des métadonnées réidentifiantes.
- **Optimisation :** trois tests supplémentaires refusent catégorie absente, suppression de l’interdiction identité–bulletin et statut prématurément expertisé.
- **Limite :** ce modèle n’est ni une analyse d’impact, ni une base juridique, ni une garantie d’anonymat ; tous les détenteurs et durées sont des propositions.
- **Prochaine action :** faire examiner les flux et le test de corrélation par les rôles protection des données, cryptographie et opérations avant tout banc synthétique.

## 2026-10-17 — Revues du vote séparées par rôle

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** ne pas laisser une même personne, un agent ou la CI tenir lieu de validation globale ; séparer association décisionnaire, droit/statuts, cryptographie, protection des données, accessibilité/usages et opérations/sécurité.
- **Résultat :** six rôles et cinq revues relient artefacts, question, preuve et condition de sortie. Tous restent `a-attribuer` et aucune personne n’est nommée ou supposée disponible.
- **Optimisation :** quatre tests refusent rôle manquant, attribution non prouvée et décision de phase privée d’un rôle.
- **Limite :** le plan ne trouve pas les personnes compétentes et ne prouve aucune indépendance ; l’association doit organiser ces revues.
- **Prochaine action :** attribuer les rôles par mandat, commencer par source statutaire et modèle de menace, puis consigner objections et inconnues sans les transformer en validation.

## 2026-10-17 — Trois directives statutaires manquantes structurées

- **Initiative :** `vote-distanciel-verifiable`.
- **Constat :** le conseil d’éthique, les phases participatives préalables et le procès-verbal d’AGO figuraient dans la note humaine mais pas dans le registre structuré.
- **Décision :** ajouter `conseil-ethique-electronique`, `phases-participatives` et `ago-proces-verbal`, puis les relier aux profils concernés sans créer de paramètre exécutable.
- **Résultat :** 18 règles couvrent désormais les huit profils ; le conseil d’éthique n’utilise plus une référence libre hors registre.
- **Limite :** les trois relevés restent `a-faire-relire`, comme les autres ; structurer un texte ne tranche pas sa portée juridique.
- **Prochaine action :** faire relire le profil retenu article par article et vérifier le règlement intérieur avant toute spécification de test.

## 2026-10-17 — Profils statutaires reliés sans devenir exécutables

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** relier les 15 relevés à 8 profils distincts sans encoder de quorum, majorité, délai, procuration ou secret directement utilisable par une urne.
- **Résultat :** Bureau, conseil d’éthique, territoriale, deux AGO, deux AGE et dissolution disposent de règles sources et questions bloquantes ; dissolution reste `bloque-interpretation`.
- **Optimisation :** quatre tests refusent profil absent, paramètre exécutable prématuré et déblocage de la dissolution.
- **Limite :** cette cartographie n’est pas une interprétation des statuts ; le conseil d’éthique comporte encore une référence libre à structurer si ce profil est choisi.
- **Prochaine action :** faire relire un seul profil choisi par l’association, puis seulement convertir ses règles confirmées en spécification de test, jamais directement en production.

## 2026-10-17 — Premiers écarts documentaires des candidats

- **Initiative :** `vote-distanciel-verifiable`.
- **Recherche :** lecture à commit épinglé de la spécification et du guide outil Belenios, du modèle de confidentialité Helios et du fichier SECURITY ElectionGuard.
- **Constats :** Belenios documente vérification et rôles mais nécessite d’expertiser publication d’identité/alias et récupération des justificatifs ; Helios annonce des métadonnées de vote et données d’identité incompatibles avec la minimisation tant qu’une configuration contraire n’est pas démontrée ; ElectionGuard est un SDK dont l’intégration complète et les versions restent à définir, son fichier SECURITY n’étant pas un audit.
- **Décision :** aucun candidat ne franchit encore un critère bloquant, faute de preuves réunies ; cela n’est pas un verdict d’insécurité.
- **Optimisation :** chaque source possède maintenant plusieurs points à résoudre et preuves à chercher ; un test refuse une liste de preuves vide.
- **Limite :** auto-descriptions des projets, lecture partielle, aucun code exécuté, aucun audit indépendant recensé dans cette passe.
- **Prochaine action :** attendre le profil et la voie B/C, puis rechercher spécifications, audits et configuration exacte seulement pour les candidats encore pertinents.

## 2026-10-17 — Sources candidates épinglées sans sélection

- **Initiative :** `vote-distanciel-verifiable`.
- **Recherche :** API GitHub et README consultés le 17 octobre 2026 pour les dépôts de Belenios, Helios et ElectionGuard. Les commits par défaut sont épinglés, avec branche, date, licence API, archivage et dernière release GitHub observable.
- **Constats limités :** Belenios se décrit comme système vérifiable avec rôles séparables et le dépôt GitHub comme miroir ; Helios se décrit comme système vérifiable de bout en bout dans un README bref ; ElectionGuard se décrit comme SDK/composants avec artefacts vérifiables, pas comme service complet M.R.S.C.
- **Décision :** ne déduire aucune aptitude de ces auto-descriptions ; conserver les trois statuts `a-evaluer` et l’option A comme référence.
- **Optimisation :** quatre tests refusent commit abrégé, source déclarée évaluée ou champ de sélection.
- **Limite :** aucun protocole, audit indépendant, version déployable, dépendance, accessibilité ou adéquation statutaire n’a été évalué.
- **Prochaine action :** après choix humain du profil et de la voie, réouvrir les spécifications et audits exacts du ou des candidats encore pertinents.

## 2026-10-17 — Comparaison du vote sans score ni classement

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** comparer l’option A et trois projets existants sans score compensatoire, rang ou probabilité ; une inconnue sur un critère bloquant empêche la sélection.
- **Résultat :** grille TOML de 4 options et 15 critères couvrant statuts/droit, secret, vérifiabilité, coercition, clés, métadonnées, procurations, quorum, résilience, chaîne logicielle, accessibilité, réversibilité, maintenance, licence et audits. Toutes les options restent `a-evaluer`.
- **Optimisation :** quatre tests refusent option absente, score ajouté et critère rendu non bloquant.
- **Limite :** les licences sont des métadonnées observées ; aucune version, fonctionnalité, audit ou aptitude n’est évaluée dans cette passe.
- **Prochaine action :** attendre le choix d’un profil et d’une voie A/B/C, puis faire remplir la grille par des rôles compétents avec des preuves exactes, sans total global.

## 2026-10-17 — Décision suivante du vote bornée et traçable

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision de méthode :** demander à l’association un profil statutaire et une voie A/B/C, sans autoriser de scrutin ni présélectionner un outil. D reste bloquée ; dissolution reste bloquée avant interprétation des articles 15 et 19.
- **Résultat :** brief de décision avec conditions cumulatives, motifs d’arrêt et trace atomique de huit champs. Une trace vide signifie attente ; une trace partielle est refusée.
- **Optimisation :** cinq tests couvrent attente, trace partielle, option D, dissolution non interprétée et décision complète bornée.
- **Limite :** le contrôle vérifie une consignation, pas l’autorité de l’instance, la qualité de la relecture ou la légalité du choix.
- **Prochaine action :** l’association confirme ou remplace la version statutaire, indique le règlement intérieur, puis choisit `aucun`/A ou un seul profil avec A, B ou C.

## 2026-10-17 — Banc synthétique du vote défini sans l’exécuter

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** préparer un protocole capable d’invalider une solution candidate, sans développer d’urne ni utiliser de données réelles.
- **Résultat :** 12 cas projetés couvrent les 10 menaces : altérations de bulletin, terminal, coercition, corrélation, seuil, clés, panne, émission, build, rétention et profil statutaire. Chaque cas précise altération, attendu et condition d’arrêt ; tous restent `a-concevoir`.
- **Optimisation :** quatre tests supplémentaires refusent un cas dit réussi, une menace non couverte ou inconnue ; le contrôle exige des données synthétiques uniquement.
- **Limite :** aucun cas n’a été exécuté ; ce protocole ne prouve aucune propriété cryptographique, juridique, opérationnelle ou d’accessibilité.
- **Prochaine action :** faire expertiser le protocole et choisir un seul profil statutaire avant de sélectionner une solution candidate et sa version.

## 2026-10-17 — Directives statutaires relevées pour le vote distanciel

- **Initiative :** `vote-distanciel-verifiable`.
- **Source :** copie locale `assets/documents/statuts-2020.pdf`, 25 pages, empreinte SHA-256 `938bd5b72d70ab4e3737f61b91818a6813b29cc5453da44c81d5b7f33ca143c3`. Extraction locale pypdf 6.1.1 ; le PDF chiffré a produit des avertissements d’objets, donc confrontation visuelle et relecture compétente encore requises.
- **Constat :** les statuts admettent plusieurs consultations électroniques, dont une AGO numérique ouverte au moins sept jours, mais distinguent Bureau, conseil d’éthique, territoriale, AGO, AGE et dissolution. Quorum, majorité, procuration, secret, blanc, délai et départage ne sont pas uniformes.
- **Décision :** ne pas créer une règle générique. Consigner 15 relevés `a-faire-relire`, leurs pages, portées et ambiguïtés ; lier leur empreinte au PDF source.
- **Ambiguïtés bloquantes :** présence/réponse numérique, secret et voix prépondérante, procuration secrète, qualification des membres concernés, article 15 face à la dissolution, portée du blanc et version du règlement intérieur.
- **Optimisation :** quatre tests supplémentaires refusent empreinte obsolète, règle absente ou statut prématurément validé.
- **Prochaine action :** faire confirmer la version applicable et les profils par l’association et une personne compétente avant de choisir un seul type de scrutin pour un éventuel banc synthétique.

## 2026-10-17 — Options de vote et tests négatifs du registre

- **Initiative :** `vote-distanciel-verifiable`.
- **Prospective :** quatre options sans probabilité sont comparées : ne pas voter à distance, service existant expertisé, logiciel existant auto-hébergé, nouveau système. L’option A reste le comparateur ; D est écartée à ce stade.
- **Optimisation :** le validateur du registre est isolé et couvert par six tests, dont suppression d’une menace, preuve vide, faux statut maîtrisé, invariant dupliqué et registre détaché de l’initiative.
- **Résultat :** le contrôle ne vérifie plus seulement le fichier nominal ; il démontre qu’il refuse plusieurs dégradations structurantes.
- **Limite :** les tests vérifient un schéma documentaire, pas une propriété cryptographique, une résistance réelle ou la pertinence des options.
- **Prochaine action :** définir avec l’association le type de scrutin et éliminer les options incompatibles avant toute comparaison technique approfondie.

## 2026-10-17 — Modèle de menace du vote rendu reproductible

- **Initiative :** `vote-distanciel-verifiable`.
- **Décision :** transformer la revue contradictoire en registre TOML maintenable plutôt qu’en liste implicite dans une architecture.
- **Résultat :** 7 invariants et 10 menaces couvrent serveur, terminal, coercition, métadonnées, collusion, clés, disponibilité, émission, chaîne logicielle et réidentification. Chaque menace distingue contrôle proposé, preuve attendue, risque résiduel et condition d’arrêt ; toutes restent `a-expertiser`.
- **Optimisation :** la CI refuse une menace absente, dupliquée, incomplète ou présentée prématurément comme maîtrisée.
- **Limite :** ce registre est une auto-analyse de conception ; il n’est ni exhaustif, ni audité, ni validé par une personne spécialiste du vote ou de la cryptographie.
- **Prochaine action :** faire critiquer le registre par les rôles juridique, cryptographique, protection des données, opérations et accessibilité avant tout choix d’outil.

## 2026-10-17 — Vote distanciel vérifiable cadré sans promesse absolue

- **Initiative :** `vote-distanciel-verifiable`.
- **Besoin exprimé :** permettre un vote à distance secret, vérifiable et résistant au détournement, avec une analogie à la vérification publique de Bitcoin.
- **Décision :** ne pas promettre « infalsifiable » ou « sécurisé en toutes circonstances », ne pas développer de cryptographie maison et ne pas recueillir de bulletin réel. Cadrer un vote vérifiable de bout en bout, séparant identité, justificatif anonyme, urne chiffrée, registre append-only, autorités de dépouillement à seuil et vérificateur indépendant.
- **Recherche :** métadonnées GitHub consultées le 17 octobre 2026 pour Belenios (miroir AGPL-3.0), Helios (Apache-2.0) et ElectionGuard porté par Election Technology Initiative (MIT). Cette vérification ne vaut ni audit, ni sélection.
- **Risques bloquants :** terminal compromis, coercition au domicile, corrélation par métadonnées, collusion, perte de clés, déni de service, droit applicable et accessibilité. Une blockchain publique ne résout pas ces risques et peut aggraver la réidentification.
- **Résultat :** note de cadrage en neuf sections, initiative P0 à cadrer et contrôle CI des garde-fous.
- **Prochaine action :** faire préciser le type de scrutin et les six décisions de gouvernance, puis obtenir des revues juridique, cryptographique, protection des données et accessibilité avant un éventuel banc d’essai entièrement synthétique.

## 2026-10-17 — Chronologie de décision prospective contrôlée

- **Initiative :** `prospective-apprentissages-2030`.
- **Décision :** empêcher une trace où la décision précède le brief ou où le réexamen n’est pas postérieur à la décision.
- **Résultat :** trois tests supplémentaires couvrent les deux chronologies impossibles et un cas valide ; la suite atteint 20 tests.
- **Limite :** l’ordre des dates ne démontre ni qu’une réunion a eu lieu, ni que l’instance indiquée avait mandat, ni que le réexamen se tiendra.
- **Prochaine action :** conserver la trace vide jusqu’à une décision humaine, puis renseigner une date de réexamen réellement convenue.

## 2026-10-17 — Décision et portefeuille rendus cohérents

- **Initiative :** `prospective-apprentissages-2030`.
- **Décision :** relier l’état de la trace au statut du portefeuille : une décision vide exige `a-cadrer`, tandis qu’une décision consignée exige une évolution d’état dans le même changement.
- **Résultat :** quatre tests supplémentaires couvrent l’attente cohérente, les deux divergences et l’initiative absente ; le rapport affiche ensemble décision et état.
- **Limite :** cette cohérence de gouvernance ne prouve ni l’autorité de la décision, ni l’utilité d’un pilote, ni un consensus.
- **Prochaine action :** faire décider A/B/C par l’association puis modifier ensemble la trace, le portefeuille et le journal, ou conserver explicitement l’attente.

## 2026-10-17 — Trace de décision prospective protégée

- **Initiative :** `prospective-apprentissages-2030`.
- **Décision :** distinguer automatiquement une décision en attente d’une trace complète et refuser les traces partielles, sans choisir d’option à la place de l’association.
- **Résultat :** le vérificateur accepte cinq champs vides ou cinq champs renseignés, limite l’option à A/B/C, contrôle les deux dates ISO et produit une erreur concise plutôt qu’une trace Python.
- **Limite :** une trace complète atteste une consignation, pas la qualité de la délibération ni l’autorité de la personne indiquée.
- **Prochaine action :** l’association peut conserver la décision en attente ou remplir les cinq champs après délibération ; aucune option n’est présélectionnée.

## 2026-10-17 — Date du brief rendue explicite et testable

- **Initiative :** `prospective-apprentissages-2030`.
- **Décision :** lire la date de référence dans l’en-tête du brief plutôt que la coder dans l’outil, et exiger que l’en-tête du tableau porte la même date.
- **Résultat :** neuf tests couvrent maintenant aussi une date française valide, une divergence entre dates et un mois invalide.
- **Limite :** une date cohérente ne rend pas les hypothèses prospectives vraies ; toute actualisation du brief doit rester une décision éditoriale consciente.
- **Prochaine action :** soumettre le pré-mortem et les options A/B/C à l’association, sans modifier automatiquement la date de l’instantané.

## 2026-10-17 — Échéances et poids ajoutés au garde-fou prospectif

- **Initiatives :** `prospective-apprentissages-2030`, `poids-et-sobriete-numerique`.
- **Décision :** étendre le contrôle du brief aux revues échues, à la prochaine revue du portefeuille et au poids local de `apprendre.html`, en conservant le 17 octobre 2026 comme date de référence explicite de l’instantané.
- **Résultat :** sept lignes factuelles sont maintenant reliées à leurs sources ; six tests couvrent le comptage, les absences, l’arrondi et le calcul d’échéance.
- **Limite :** les poids sont des estimations gzip locales et l’échéance ne prouve pas qu’une revue de fond a eu lieu.
- **Prochaine action :** faire relire les risques et décider si le pilote Boussole mérite du temps face aux relectures sensibles.

## 2026-10-17 — Vérificateur prospectif durci après fusion

- **Initiative :** `prospective-apprentissages-2030`.
- **Décision :** supprimer le nombre de domaines codé en dur et le recalculer depuis le catalogue ; couvrir le comptage de la Boussole par trois tests unitaires.
- **Résultat :** le contrôle suit désormais cinq valeurs internes et refuse explicitement une section ou une liste absente.
- **Limite :** les tests portent sur la synchronisation structurelle, pas sur la qualité des questions ni sur le choix prospectif.
- **Prochaine action :** faire relire les six risques du pré-mortem et attribuer les rôles de décision.

## 2026-10-17 — Brief prospectif rendu vérifiable

- **Initiative :** `prospective-apprentissages-2030`.
- **Décision :** contrôler automatiquement quatre faits internes du brief (fiches, prototypes, initiatives/P0, questions de la Boussole) au lieu de laisser vieillir un instantané silencieusement.
- **Résultat :** `outils/verifier-decision-prospective.py` recalcule ces valeurs depuis le catalogue, le portefeuille et la page générée ; la CI échoue si le brief diverge.
- **Limite :** ce contrôle ne valide ni les scénarios, ni la recommandation, ni le choix A/B/C, qui reste une décision de l’association.
- **Prochaine action :** faire relire le pré-mortem et attribuer les rôles nécessaires avant tout pilote.

## 2026-10-17 — Reprise R&D, optimisation et pré-mortem prospectif

- **Initiatives :** `relire-les-44-prototypes`, `optimisation-du-site`, `prospective-apprentissages-2030`.
- **Décision :** intégrer sur la branche active la file de relecture générée et l’extension du balayage d’accessibilité ; ajouter au brief prospectif un pré-mortem sans choisir à la place de l’association.
- **Résultat technique :** 55 prototypes ordonnés pour relecture ; 23 états interactifs couverts ; contraste du héros corrigé. Les contrôles automatiques ne valent ni relecture experte ni essai humain.
- **Prospective :** six échecs possibles ont désormais un signal sans suivi individuel, un repli réversible et une porte humaine ; aucune probabilité n’est attribuée aux scénarios.
- **Prochaine action :** attribuer les relectures des 9 domaines sensibles, puis faire trancher les options A/B/C par l’association.

## 2026-10-17 — PR #94 ouverte

- **Initiatives :** `relire-les-44-prototypes`, `optimisation-du-site`.
- **Décision :** ouvrir la PR #94 depuis `arena/26d57815-mrsc` sans la fusionner ; la demande portait sur une fusion de la PR #93, pas sur une autorisation permanente.
- **Contrôles exécutés :** CI `qualite` réussie sur la PR (31 s) ; porte locale 11/11 ; axe 47/0 et 192/0 ; `test-experience.cjs` 8/8.
- **Limites :** la CI ne lance pas les balayages navigateur (dépendances hors dépôt) ; la relecture des prototypes reste entièrement humaine.
- **Prochaine action :** attendre une décision explicite de fusion, ou poursuivre sur les signalements par excès de la file de relecture.

## 2026-10-17 — File de relecture des 55 prototypes

- **Initiative :** `relire-les-44-prototypes` (P0, `a-valider`).
- **Signal :** la prochaine action de l'initiative P0 — organiser les relectures — restait une consigne sans support. Les 55 prototypes étaient listés dans le catalogue mais aucune vue ne les ordonnait pour une personne, et les domaines à relecture spécialisée (santé, droit, argent, politique publique) n'étaient pas distingués.
- **Décision :** générer `docs/apprentissage/file-relecture.md` depuis le catalogue avec deux règles explicites — domaine déclaré, puis mots-clés dans les champs éditoriaux — sans jamais produire de note ni de validation. La sortie affiche les termes trouvés pour que le triage soit corrigeable, et rappelle qu'un prototype sans signal reste à relire.
- **Résultat mesuré :** 55 prototypes, dont **9** dans des domaines à relecture spécialisée et **9** signalés par mots-clés hors de ces domaines ; 37 sans signal automatique ; 15 domaines. Les 55 liens vers les fiches résolvent.
- **Outil :** `outils/file-relecture.py`, avec `--verifier` (échoue si le fichier diverge du catalogue) et `--sortie`. Aucun réseau, aucune donnée personnelle. Étape ajoutée au workflow de vérification.
- **Contrôles réellement exécutés :** génération, `--verifier` (succès, puis échec provoqué et retour au vert après restauration), résolution des 55 liens, `verifier-rd-continue.py`, `verifier-site-statique.py`, `verifier-integration.py`, porte locale complète.
- **Limites :** aucune relecture n'a eu lieu ; les motifs par mots-clés sont imparfaits (par exemple « service public » dans une fiche de mathématiques) ; le classement ne préjuge ni de la qualité ni de la difficulté ; aucun relecteur n'est identifié.
- **Prochaine action :** répartir les 9 fiches des domaines sensibles, puis les 9 signalées par mots-clés, et corriger les signalements par excès au fil des relectures.

## 2026-10-17 — PR #93 fusionnée et publication vérifiée

- **Initiatives :** `prospective-apprentissages-2030`, `veille-savoirs-evolutifs`, `optimisation-du-site`.
- **Décision :** fusion de la PR #93 (`16edfbf`) sur demande explicite de la personne utilisatrice, pour voir le résultat publié. Fusion par merge commit, sans écrasement d'historique.
- **Contrôles exécutés :** workflow « Vérification du site M.R.S.C » réussi sur `main` (35 s) ; « Publish M.R.S.C site » réussi (40 s) ; « Veille éditoriale des apprentissages » réussie (22 s). Le contenu de la PR était déjà passé par la porte locale 10/10 et `test-experience.cjs` 8/8.
- **Limites :** la réussite des workflows prouve que la publication a été acceptée, pas que le site publié soit conforme ni accessible ; aucun contrôle de la version en ligne (en-têtes, rendu, lecteur d'écran) n'est refait dans cette entrée.
- **Prochaine action :** poursuivre les états interactifs non couverts (formulaires en erreur, mission terminée), puis faire relire l'accessibilité par une personne compétente.

## 2026-10-17 — Accessibilité : recherche vide, aides et contraste du héros

- **Initiative :** `optimisation-du-site` (P1, `a-tester`).
- **Signal :** après fusion de la PR #93, les états restants étaient la recherche sans résultat, les aides dépliées des fiches, une réponse de mission choisie et les modes de contraste. Ils n'avaient jamais été balayés.
- **Mesures :** le script passe à 23 états et 47 exécutions par défaut (24 pages + 23 états) ; le mode `--etendu` reste à 192 exécutions sur 96 pages. Les deux sont sans violation après correction.
- **Défaut trouvé :** à 1 280 px seulement, le bouton secondaire du héros des Mondes affichait du blanc sur `rgba(11,33,51,.45)`, soit un fond effectif `#919ba3` et 2,82:1. À 360 px, le recadrage de l'image masquait le problème.
- **Décision :** porter le fond du bouton à `rgba(11,33,51,.72)` (6,5:1 dans le pire cas sur fond blanc), le survol à `.9`, et les pastilles voisines à `.7`. Ne pas se fier à l'image derrière : la borne de calcul est le fond clair.
- **Preuve :** `docs/rd/accessibilite-2026-10-17.md`, troisième passe mise à jour.
- **Contrôles réellement exécutés :** `outils/verifier-accessibilite.cjs` 47/0 et `--etendu` 192/0 ; porte locale 10/10 ; `test-experience.cjs` 8/8.
- **Limites :** les états de survol ne sont pas mesurés ; les images de fond ne sont pas analysées ; toujours aucun lecteur d'écran ni revue experte.
- **Prochaine action :** faire relire ces corrections, puis couvrir les formulaires en erreur et une mission menée jusqu'au bout.

## 2026-10-17 — Accessibilité : toutes les pages et les panneaux ouverts

- **Initiative :** `optimisation-du-site` (P1, `a-tester`).
- **Signal :** le premier balayage ne couvrait que huit pages au repos. Deux angles manquaient : les 81 fiches et pages secondaires, et les panneaux fermés par défaut, invisibles à axe tant qu'ils ne sont pas ouverts.
- **Mesures :** `outils/verifier-accessibilite.cjs` rend le protocole reproductible. Mode `--etendu` : 96 pages × 360/1 280 px, **192 exécutions sans violation**. Mode par défaut : 12 pages × 2 largeurs et 13 états interactifs, **37 exécutions**. La page `simulateur.html` est chargée sans `networkidle0` (iframe et appels asynchrones), avec cinq secondes d'attente.
- **Défaut trouvé par les états :** panneau « Affichage » déplié, les libellés de `A−`, `A+` et « Espacement du texte » ne reprenaient pas leur texte visible ; ce défaut était invisible tant que le panneau restait fermé.
- **Décisions :** préfixer les libellés `A−`/`A+` dans les 94 pages et dans `outils/construire-apprentissages.py` ; laisser aux quatre boutons à bascule un nom stable et confier l'état à `aria-pressed` au lieu d'un libellé « activer/désactiver » qui doublait l'information ; régénérer le simulateur et revérifier les fiches générées.
- **Preuve :** `docs/rd/accessibilite-2026-10-17.md`, mis à jour avec les trois passes.
- **Contrôles réellement exécutés :** `outils/verifier-accessibilite.cjs` (37 exécutions), `--etendu` (192 exécutions), `verifier-integration.py`, `verifier-site-statique.py`, `verifier-rd-continue.py`, fiches et simulateur `--verifier`, `py_compile`, `test-experience.cjs` 8/8.
- **Limites :** Chromium seulement ; pas de lecteur d'écran, pas de navigation clavier exhaustive, pas de revue experte ; seuls les états listés sont visités ; la version publiée n'est pas contrôlée.
- **Prochaine action :** faire relire ces corrections par une personne compétente, si possible avec un utilisateur de lecteur d'écran, puis étendre le balayage aux formulaires en erreur et aux contenus repliés.

## 2026-10-17 — Noms accessibles et contrastes : balayage axe-core

- **Initiative :** `optimisation-du-site` (P1, `a-tester`).
- **Signal :** les essais navigateur du dépôt couvraient le réflow, le zoom et les réglages, mais aucun contrôle automatique ne portait sur les noms accessibles ni les contrastes. Un balayage axe-core 4.14.0 sur 8 pages × 360/1 280 px a relevé deux règles seulement : `color-contrast` (42 nœuds, pied de page à 3,22:1 pour `.footer-rd` et 2,31:1 pour ses liens) et `label-content-name-mismatch` (12 nœuds : commandes d'affichage du site et du simulateur, boutons de monde de l'atlas).
- **Décisions :** corriger sans retirer de contenu ni de fonction. `.footer-rd` passe à `rgba(255,255,255,.74)` (9,3:1 calculé sur `#121f43`), ses liens à `#cfe0ff` (12,1:1), avec exception `forced-colors`. Les libellés accessibles des commandes d'affichage commencent par leur texte visible. Les boutons de mission de l'atlas ne surchargent plus leur nom accessible : leur contenu visible fait foi. Les boutons de monde gardent un glyphe `aria-hidden` et une mention masquée « Filtrer les fiches de ce monde. ». Utilitaire `.visually-hidden` ajouté.
- **Preuve :** `docs/rd/accessibilite-2026-10-17.md` (méthode, résultat avant/après, limites).
- **Contrôles réellement exécutés :** axe-core 4.14.0 sur 16 exécutions, **aucune violation après correction** ; `outils/test-experience.cjs` **8/8** ; sonde Puppeteer locale sur Les Mondes (ouverture d'escale, focus rendu, filtre par monde, nom accessible du bouton de mission) ; `outils/construire-simulateur.py --verifier` ; `verifier-rd-continue.py` ; `verifier-site-statique.py` ; `verifier-integration.py`.
- **Limites :** axe ne teste qu'une partie des critères ; aucun lecteur d'écran, aucune navigation clavier exhaustive, aucune revue par une personne experte ; Chromium seulement ; états interactifs non balayés en continu. Ce relevé n'est ni un audit ni une conformité RGAA/WCAG.
- **Prochaine action :** faire relire les corrections par une personne compétente en accessibilité, si possible avec un utilisateur de lecteur d'écran, puis étendre le balayage aux états ouverts et aux missions en cours. Ne pas modifier l'état de l'initiative avant cette relecture.

## 2026-10-17 — Veille externe, brief de décision et état vérifiable

- **Initiatives :** `prospective-apprentissages-2030` (P1, `a-cadrer`) et `veille-savoirs-evolutifs` (P0, `en-cours`).
- **Signal :** la note de prospective indiquait explicitement n'avoir fait aucun balayage externe, et sa prochaine action — faire relire la Boussole puis décider d'un pilote — ne pouvait pas être exécutée par un agent. Les 55 prototypes restaient à relire. Il manquait donc deux pièces : des sources datées, et une décision formulée pour l'association.
- **Recherche (17 octobre 2026) :** quatre sources publiées en 2026, consignées avec chiffres, périmètre et limites dans `docs/rd/veille-2026-10-17.md`. Reuters Institute, 16 juin : usage hebdomadaire d'un chatbot pour s'informer 10 % (7 % en 2025), 1 % en source principale, aucune hausse mesurée en France, confiance 20 % contre 37 % ; 33 % des utilisateurs demandent d'évaluer une source. Défenseur des droits, 9 avril : 165 011 réclamations (+17 %), 61 % de personnes en difficulté administrative en 2024 contre 39 % en 2016, 49 % seulement faisant seules leurs démarches en ligne. Arcep, 21 mai : consommation électrique des centres de données +12 % en 2024, émissions +23 %, 46 % des émissions du numérique en France en 2022 selon le périmètre ADEME-Arcep élargi. Commission européenne, page du 12 octobre : article 50 applicable depuis le 2 août 2026 (marquage, étiquetage), code de bonne conduite signé par environ 190 organisations.
- **Décisions :** ne pas trancher à la place de l'association. Ajouter au brief trois options bornées (`docs/rd/decision-prospective.md`), des critères d'arrêt datés et une trace de décision à remplir ; recommander l'option B (relire puis pilote papier) ou A si aucun relecteur n'est disponible avant le 31 janvier 2027 ; ajouter une dixième décision « sans regret » (ne jamais faire dépendre l'essentiel d'un seul canal). Aucun chiffre externe n'est transposé au site ; aucune conversion en bénéfice d'usage.
- **Outil :** `outils/etat-rd.py` imprime un état daté et recalculé (initiatives, P0, revue du portefeuille, fiches, prototypes, revues échues, prochaine revue, poids maximal) pour que le brief repose sur des faits vérifiables. Aucun réseau, aucune donnée personnelle.
- **Contrôles exécutés :** `py_compile` ; `python3 outils/etat-rd.py --date 2026-10-17` (14 initiatives, 4 P0, 81 fiches, 55 prototypes, 0 revue échue, revue du portefeuille dans 26 jours, 95 pages sous budget) ; `verifier-rd-continue.py` ; `verifier-site-statique.py` ; `verifier-integration.py` (mis à jour pour le nouveau paragraphe de transparence) ; `test-experience.cjs`.
- **Limites :** pas d'atelier, pas d'essai avec des personnes, pas de revue experte ni juridique, pas de recherche systématique ; les incertitudes « langues » et « capacité de relecture » restent sans signal externe vérifié dans cette passe ; le brief n'est pas une décision.
- **Prochaine action :** faire trancher les trois options et consigner la décision ; refaire la veille en janvier 2027 ; ne pas promouvoir le prototype avant relecture.

## 2026-10-17 — Poids des pages, sobriété et réflow à 320 px

- **Initiative :** `poids-et-sobriete-numerique` (lien `optimisation-du-site` et `prospective-apprentissages-2030`).
- **Signal et périmètre :** trois illustrations portaient l’essentiel du poids des pages principales; les essais navigateur du dépôt échouaient déjà sur trois cas (largeur instable du bouton compact, débordement de `index.html` à 320 px, débordement à 320 px et 150 % avec contraste et espacement renforcés). La passe devait réduire les octets transférés sans retirer de contenu, de repli JPEG, de texte alternatif ni de fonctionnement sans JavaScript.
- **Recherche et sources :** mise à jour ADEME 2024 sur l’empreinte du numérique (4,4 %, environ 29,5 Mt CO₂e en 2022) et INSEE 2025 (21 Mt, 3,2 % en 2023) lues comme des périmètres différents, non comparables directement; répartition ADEME–Arcep 2023 (79 % équipements, 16 % centres de données, 5 % réseaux); Web Almanac 2025 (2 559 Kio médians sur mobile, images 911 Kio); RGESN 2024 (78 critères, 9 familles); W3C WSG en Draft Note (2 octobre 2025). Aucune conformité à ces cadres n’est revendiquée.
- **Mesure :** `outils/verifier-poids-pages.py` reconstruit hors ligne le poids des 95 pages avec gzip niveau 9, en deux scénarios d’image. Avant : accueil 289,7 Kio, apprentissage 459,3 Kio, atlas 662,7 Kio (mobile comme grand écran). Après : 106,2 / 168,1 ; 158,8 / 308,6 ; 183,0 / 332,7 Kio. Le détail est dans `docs/rd/poids-pages.md`; la méthode et les limites, dans `docs/rd/poids-et-sobriete-numerique.md`.
- **Optimisations :** variantes AVIF qualité 60 et WebP qualité 80 en 800 px et à la largeur d’origine (1 400 ou 1 672 px), plus 1 200 px pour l’atlas; `<picture>` avec `srcset`, `sizes`, repli JPEG; préchargement AVIF typé; image de secours de la scène chargée seulement si WebGL échoue; hauteur réelle de l’illustration d’accueil corrigée de 788 à 933 px; types MIME locaux `.avif`/`.webp`; boutons longs autorisés à revenir à la ligne sous 520 px; largeur du bouton compact réservée; sous 240 px, le logo laisse la place aux commandes.
- **Qualité d’image :** PSNR après normalisation sRGB (le calcul direct AVIF↔JPEG donnait 12–14 dB à cause de l’espace YCbCr). AVIF q60 pleine largeur : 38,8 / 36,4 / 38,7 dB; WebP q80 : 38,5 / 36,0 / 38,9 dB. Contrôles par l’agent seulement : rendu côte à côte dans Chromium à 400 px (moyennes de luminance à 0,0005 près), écart mesuré sur la source ramenée à 800 px (erreur absolue moyenne de 1,0 à 1,6 % de la dynamique, PSNR 31,9–36,7 dB) et recadrage à l’échelle 1; aucune revue humaine ni mesure perceptuelle (SSIM, VMAF, Butteraugli).
- **Contrôles réellement exécutés :** `python3 outils/optimiser-images.py --verifier` ; `python3 outils/verifier-poids-pages.py --rapport docs/rd/poids-pages.md` ; `MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules node outils/test-experience.cjs` — **8/8** essais (les 3 mêmes cas échouaient sur le commit de base, vérifié dans un worktree séparé) ; sondes Puppeteer locales de sélection AVIF et de repli WebGL ; `py_compile` ; vérificateurs R&D, fiches, simulateur, site statique, protocole éditorial, sécurité et intégration — réussis.
- **Décisions :** conserver les JPEG comme référence et repli; ne jamais supprimer une source au profit d’un format unique; ne pas ajouter de CDN, police distante, média automatique ou mesure d’audience; traiter la sobriété comme un moyen de réduire une dépendance, pas comme un indicateur de qualité éditoriale. Le dépôt gagne environ 1,5 Mio de variantes, alors que les transferts par visite baissent.
- **Limites :** aucune mesure réseau, aucun test sur appareil réel, Safari, Firefox ou lecteur d’écran; aucun Lighthouse/CrUX; types MIME, compression et cache de GitHub Pages et Vercel non vérifiés; aucune estimation carbone; aucune revue visuelle humaine des images. La passe n’est ni un audit RGESN ni une preuve d’impact évité.
- **Suite donnée le même jour :** `outils/verifier-publication.py` et le workflow « Vérifier les en-têtes servis par l’hébergement » relèvent désormais code, type MIME, encodage, octets et cache sur la version publiée. Relevé réel du 17 octobre 2026 (issue #90) : 18/18 fichiers en 200, `image/avif` et `image/webp` correctement typés, gzip sur les 9 fichiers texte et aucun sur les images (attendu), `Cache-Control: max-age=600`. L’estimation hors ligne reste à +0,7–4,2 % sous les octets servis pour les fichiers texte (gzip 9 estimé contre gzip de Pages), et identique à l’octet pour les images déjà compressées. Le relevé reste hors de la porte hors ligne et ne vaut ni pour Vercel, qui héberge le simulateur du dépôt amont, ni comme mesure de performance.
- **Prochaine action :** faire relire les illustrations par une personne, mesurer sur appareil et réseau réels, puis seulement réviser l’état de `poids-et-sobriete-numerique` et la date de revue du portefeuille.

## 2026-10-16 — Personnages-matériaux pour l’identité pédagogique

- **Initiative :** `direction-artistique-motion`.
- **Signal :** reprendre les matériaux du visuel d’accueil (verre, métal, arcs, cristal) pour des personnages uniques, vidéos de présentation et animations pédagogiques intuitives. Accueil 3D inchangé.
- **Décision :** quatre guides proposés (Vertige, Ambre, Lame, Facette), distincts du logo et de Léna / Marc / Karim. Dix planches identite-01 à 10. Noms à valider.
- **Contrôles :** planches identité.

## 2026-10-16 — Pistes nouvelles 11–20

- **Initiative :** `direction-artistique-motion`.
- **Signal :** encore des pistes totalement nouvelles.
- **Décision :** timbres, bakélite, flaque, buvard, chambre à air, sucre, gare, pétanque, acétate, phalènes.
- **Contrôles :** planches nouveau-11 à 20.

## 2026-10-16 — Dix pistes totalement nouvelles

- **Initiative :** `direction-artistique-motion`.
- **Signal :** des essais totalement nouveaux, hors fusions grille/gouache/pixels.
- **Décision :** tram-vitrail, cyanotype, laine, savon, Super 8, craie, émail, radar, ombres, péniche. France, Léna / Marc / Karim.
- **Contrôles :** planches nouveau-01 à 10.

## 2026-10-16 — Fusions 11–20

- **Initiative :** `direction-artistique-motion`.
- **Signal :** encore des fusions (grille, gouache, pixels, mains).
- **Décision :** F-11 à F-20. France, Léna / Marc / Karim.
- **Contrôles :** planches fusion-11 à 20.

## 2026-10-16 — Fusions de styles (quatre planches choisies)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** mélanger mots croisés, gouache fraîche, pixels visages, mains ; innover.
- **Décision :** dix fusions F-01 à F-10. Trio Léna / Marc / Karim, France 1985. F-10 = tentative de look unique de film.
- **Contrôles :** planches fusion-01 à 10.

## 2026-10-16 — Compilation Drive + X17

- **Initiative :** `direction-artistique-motion`.
- **Signal :** zipper toutes les planches sur Drive ; dix autres ; l’association sélectionnera pour des fusions.
- **Décision :** zip JPG dans le dossier Drive « M.R.S.C. planches animation statuts ». Série X17 (80s + humanité). PNG originaux restent dans le dépôt ; le zip n’est pas versionné.
- **Contrôles :** archive créée ; envoi Drive.

## 2026-10-16 — Expériences 80s, humanité et sensualité (X16)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** ajouter une part de sensualité et d’humanité.
- **Décision :** chaleur des mains, veste partagée, bal maladroit, regards, bus, parapluie. Pas d’érotisme. Neuf planches (gouttes non livrées).
- **Contrôles :** planches X16.

## 2026-10-16 — Dix expériences 80s (X15)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** des choses intéressantes, encore ; codes 80s.
- **Décision :** CRT-stores, plastique K7, aérobic, polaroid ciel, pixels visages, égaliseur, bâtons fluo, catadioptres, Antiope, chrome pluie. France.
- **Contrôles :** planches X15.

## 2026-10-16 — Dix expériences 80s (X14)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** innover absolument et tenir les codes 80s.
- **Décision :** Memphis-zinc, VHS-Walkman, lasers-damier, LCD fluo, Minitel-aérographe, enceinte-K7, aérographe BD, cubes fluo, onde-mobylette, disquette-vitrail. France, fluo teal/magenta, pas de logos de marques.
- **Contrôles :** planches X14.

## 2026-10-16 — Dix expériences de style (X13)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** dix autres.
- **Décision :** fonds de bouteille, bitume-bonbon, carte de bal, bic rouge, rouille-chrome, libellule, empreintes, caramel, tableau départs, néon asphalte. France.
- **Contrôles :** planches X13.

## 2026-10-16 — Dix expériences de style (X12)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** dix autres innovants.
- **Décision :** gouache fraîche, patron, gravier-cel, boule à facettes, cartes percées, rayons, courant, tableau vert, roue, papillons. France.
- **Contrôles :** planches X12.

## 2026-10-16 — Dix expériences de style (X11)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** continuer la R&D jusqu’au style unique ; dix autres.
- **Décision :** trichromie, mie de pain, aiguillage, serpentins, fiches, graisse, sable pétanque, cahier Seyes, verre, buée. France.
- **Contrôles :** planches X11.

## 2026-10-16 — Dix expériences de style (X10)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** innover ; un style déjà repéré dans la série précédente (non nommé) ; dix autres.
- **Décision :** expériences tickets, mire TV, parquet, limonade, chambre à air, tampon, écorce, pluie zinc, équerre, barbe à papa. France.
- **Contrôles :** planches X10.

## 2026-10-16 — Vingt mixtes, lot 2/2

- **Initiative :** `direction-artistique-motion`.
- **Signal :** dix autres.
- **Décision :** M20-11 à 20 livrés.
- **Contrôles :** planches ajoutées.

## 2026-10-16 — Vingt mixtes, premier lot de dix

- **Initiative :** `direction-artistique-motion`.
- **Signal :** vingt autres mixtes.
- **Décision :** dix livrés (ticket, ardoise, zinc-coloriage, isobares, soudure, timbre, formica, flaque, cire, dynamo). Dix suivants au tour d’après (plafond d’images).
- **Contrôles :** planches M20-01 à 10.

## 2026-10-16 — Dix mixtes inédits pour trouver la touche

- **Initiative :** `direction-artistique-motion`.
- **Signal :** dix autres, mixtes jamais faits, France.
- **Décision :** dix hybrides (émail-Minitel, pétanque-buvard, horaires-vitrail, camembert-VHS, chaîne-guirlande, acétate-anaglyphe, pomme d’amour, papier bible, gravier-aérographe, pastis-encre-argile).
- **Contrôles :** planches ajoutées.

## 2026-10-16 — Dix planches France, plus de diner US

- **Initiative :** `direction-artistique-motion`.
- **Signal :** dix autres styles ; tout en français ; décors en France.
- **Décision :** zinc, brasserie, salle des fêtes, quai, tabac, bibliothèque, atelier vélo, fête foraine, lycée, berge. Diner américain écarté. Textes français.
- **Contrôles :** bible mise à jour.

## 2026-10-16 — Dix styles d’animation supplémentaires

- **Initiative :** `direction-artistique-motion`.
- **Signal :** dix autres, variés.
- **Décision :** fusain, broderie, UPA magenta, blacklight, comics dimanche, origami dur, synth UI, pare-brise, affiche Est, crayon test. Toujours le booth, à choisir.
- **Contrôles :** bible mise à jour.

## 2026-10-16 — Mix VHS+volume et cinq styles inédits

- **Initiative :** `direction-artistique-motion`.
- **Signal :** mixer la piste 3 et la 6, plus cinq inédits.
- **Décision :** planche mix VHS volume ; inédits litho néon, verre soda, mosaïque cassette, rétroprojecteur, radar diner. Toujours le même booth, à choisir.
- **Contrôles :** bible mise à jour.

## 2026-10-16 — Six pistes d’animation (sortie du réalisme)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** même ambiance 80s, passer au dessin animé pour suivre les personnages ; style neuf, inspiré de plusieurs recettes qui tiennent ; 6 présentations.
- **Décision :** réalisme écarté pour le casting. Six hybrides : encre chrome, argile lanterne, VHS aurore, vitrail nuit, riso boulevard, volume pinceau. À choisir ou fusionner (max deux) puis model sheets.
- **Contrôles :** bible mise à jour ; six planches.

## 2026-10-16 — Bible Léna / Marc / Karim et vidéo 01

- **Initiative :** `direction-artistique-motion`.
- **Signal :** mêmes personnages principaux de A à Z ; figurants et périodes seuls changent ; vieillir sans excès ; première vidéo ; histoire concrète sur toutes les périodes.
- **Décision :** bible `docs/rd/statuts-animation/bible-fil-et-video-01.md`. Pacte du vendredi. Vidéos 01–06 puis statuts avec le même trio. Storyboard 01 : arrivée, booth, pacte, la seconde où Marc regarde l’arcade. Visages IA non figés.
- **Contrôles :** note + bible.

## 2026-10-16 — Fil narratif entre les décennies

- **Initiative :** `direction-artistique-motion`.
- **Signal :** relier intelligemment les décennies par des histoires qui mènent à la conclusion M.R.S.C.
- **Décision :** constantes = la bande de trois, le booth du diner, le carnet savoir-faire. Arc 1985 → 1994 → 2004 → 2014 → 2020 → la table revient. Les statuts = ce qui empêche la table de se vider. Quatre planches de liaison, scènes 2004 et 2020 encore à produire.
- **Contrôles :** note mise à jour.

## 2026-10-16 — Style Amblin / 80s cinéma (BTTF, Stranger Things)

- **Initiative :** `direction-artistique-motion`.
- **Signal :** revoir le style vers Retour vers le futur, Stranger Things, etc.
- **Décision :** piste lumière 80s cinéma (néon, grain, brume, diner, vélos), personnages originaux, pas de copies de films. Quatre planches amblin 80/90/2010/2020. À adapter à mesure.
- **Contrôles :** note mise à jour.

## 2026-10-16 — Prologue en décennies, style 80s coloré

- **Initiative :** `direction-artistique-motion`.
- **Signal :** partir des années 80 (tout était possible), faire défiler les décennies, montrer la dégradation des relations et le nombrilisme ; ambiance 80s colorée, réaliste et animée ; adapter à mesure.
- **Décision :** premières scènes = montage 80 / 90 / 2010 / 2020. Quatre planches d’essai. Le seuil M.R.S.C. vient après ce défilement. Pas de logos de marques.
- **Contrôles :** note mise à jour.

## 2026-10-16 — Accroche humaniste du film des statuts

- **Initiative :** `direction-artistique-motion`.
- **Signal :** partir du repli (écrans, distance) pour faire revivre convivialité, savoir-être, partage des savoir-faire et des expériences ; découvrir le M.R.S.C. et ce qui s’ouvre quand on comprend son fonctionnement.
- **Décision :** le film est un récit humaniste 3D, pas un explainer. Arc : seul avec les écrans → le seuil → la table du partage → les portes. Les statuts = carte du « comment on fait ensemble ». Quatre planches d’accroche, non validées. COVID/médias = climat du personnage, pas un pamphlet public.
- **Contrôles :** note mise à jour.

## 2026-10-16 — Seconds angles de présentation des statuts

- **Initiative :** `direction-artistique-motion`.
- **Signal :** les premières chartes mascottes n’étaient pas à la hauteur ; il faut l’angle, pas seulement le dessin.
- **Décision :** quatre nouveaux angles (maison ouverte, table de fondation, assemblée en cercle, voyage dans le livre). Fil proposé : une personne arrive, chaque article est une pièce ou un geste, dans l’ordre. Anciennes planches archivées.
- **Contrôles :** note mise à jour ; pas de page publique.

## 2026-10-16 — Plan films d’animation des statuts

- **Initiative :** `direction-artistique-motion`.
- **Signal :** expliquer le fonctionnement associatif par des films 3D, depuis le début des statuts, tous les articles, VO française, sous-titres anglais optionnels, quatre styles et personnages originaux.
- **Décision :** note `docs/rd/plan-statuts-animation.md` et quatre planches de style (non validées). Le PDF des statuts fait foi. Aucune vidéo produite. Extraction automatique du PDF impossible ici ; transcription humaine requise avant tournage. Accueil 3D inchangé.
- **Contrôles réellement exécutés :** rédaction documentaire ; pas de page publique nouvelle.
## 2026-10-16 — Achats indexés sur les dons, puis complément

- **Initiative :** `documentation-rd-eva`.
- **Signal :** adapter vraiment les achats à la capacité des dons ; si le total ne permet pas le matériel, conserver / placer les fonds et lancer un appel complémentaire.
- **Décision :** cycle public sur `eva.html#cagnotte-dons` : collecter → faire le point → n’acheter qu’un palier couvert → sinon conservation et, le cas échéant, placement selon les règles de l’association (sans promesse de rendement) → nouvelle cagnotte → recommencer. Transparence des totaux et des reports, sans données personnelles non consenties.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` ; `verifier-rd-continue.py`.

## 2026-10-16 — Spark, serveur dédié, cagnotte et conscience comme question

- **Initiative :** `documentation-rd-eva`.
- **Signal :** cadrer une première capacité de calcul (type Spark, peu énergivore), un palier serveur, des recherches sur la conscience autonome, et une cagnotte transparente indexée sur le total collecté.
- **Décision :** pages publiques et note `docs/rd/materiel-spark-serveur-dons.md`. Conscience = question ouverte, pas un résultat. Spark / serveur = pistes à devis, pas une commande. Cagnotte = mécanisme proposé ; tant qu’elle n’est pas ouverte, bulletin de don et courriel existants. Achats par paliers selon le total, avec transparence sans données personnelles non consenties. Aucun montant fixé.
- **Sources consultées :** fiche constructeur NVIDIA DGX Spark (16 oct. 2026). Les watts constructeur ne sont pas une mesure M.R.S.C.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` ; `verifier-rd-continue.py`.

## 2026-10-16 — Listes R&D Éva et matériel idéal

- **Initiative :** `documentation-rd-eva`.
- **Signal :** il faut une liste de travail pour la R&D d’Éva et pour le matériel idéal.
- **Décision :** deux listes publiques de cadrage sur `eva.html#listes-rd-eva` (et `docs/rd/listes-eva-materiel.md`) : chantiers de recherche, puis catégories de matériel à spécifier. Aucun modèle, prix, puissance ni appel aux dons. Statut : à relire.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` ; `verifier-rd-continue.py`.

## 2026-10-16 — Logo compact : plus de coupe en haut

- **Initiative :** `coherence-textes-publics`.
- **Signal :** en mode réduit, le haut du logo (barres de couleur) était coupé.
- **Décision :** `object-fit: contain` et cadrage haut, sans recadrage `cover`.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py`.

## 2026-10-16 — Cycle R&D : voisines, passeport simulateur, pied de page

- **Initiative :** `prospective-apprentissages-2030` (lien `optimisation-du-site`).
- **Signal :** second cycle R&D / prospective / innovation sur l’ensemble du site, sans inventer de validation.
- **Décision :**
  1. Sur chaque fiche, jusqu’à trois **voisines du même domaine** (catalogue), sans cursus.
  2. **Passeport de lecture** du simulateur : séparer paramètres, moteur, résultat calculé et contexte sourcé.
  3. Mention R&D en **pied de page** de toutes les pages publiques ; copie imprimée datée par l’URL, non certifiée.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-rd-continue.py` ; `verifier-site-statique.py` ; `verifier-integration.py`.

## 2026-10-16 — Cycle R&D : boussole, impression, prospective

- **Initiative :** `prospective-apprentissages-2030` (lien `optimisation-du-site`).
- **Signal :** poursuivre R&D, prospective et innovation sur l’ensemble du site, sans inventer de validation.
- **Décision :**
  1. Prototype HTML de la **Boussole des savoirs** (dix questions du catalogue, statuts visibles) sur `apprendre.html`, entrée depuis l’accueil.
  2. Feuille **d’impression** du site (en-tête et commandes masqués) comme premier pas du kit autonome.
  3. Mise à jour de la note 2027–2030 : ces objets sont des prototypes à relire, pas des essais d’usage.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-rd-continue.py` ; `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-16 — Plan global : une phrase par ligne

- **Initiative :** `coherence-textes-publics`.
- **Signal :** après un point, la phrase suivante restait sur la même ligne ; ce n’est ni joli ni confortable à lire.
- **Plan :**
  1. Découper tout le contenu principal **et** le pied de page (`p`, listes, tableaux, légendes, citations, `small`).
  2. Après `. ? ! …`, la phrase suivante commence **toujours en dessous**, alignée à gauche.
  3. Ne pas casser les libellés de navigation, boutons, code, formulaires.
  4. Protéger les abréviations (M.R.S.C., ÉVA, Mme, M., Dr, etc.).
- **Décision :** le script et le CSS couvrent désormais ces blocs, pas seulement `p` / `li` / `dd`.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py`.

## 2026-10-16 — Cadre du logo compact, même fichier

- **Initiative :** `coherence-textes-publics`.
- **Signal :** trop de blanc autour du logo en mode réduit.
- **Décision :** même image ; cadre aux coins des boutons, recadrage CSS (cover) pour réduire le blanc.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-16 — Bandeau compact identique Chrome et Firefox

- **Initiative :** `coherence-textes-publics`.
- **Signal :** le mode réduit était correct dans Firefox, pas dans Chrome (float / flex).
- **Décision :** groupe `header-compact-tools` à droite du logo (flex) : même rendu dans les deux moteurs.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-16 — Bandeau compact smartphone : boutons à droite du logo

- **Initiative :** `coherence-textes-publics`.
- **Signal :** sur téléphone, Affichage et Présentation passaient sous le logo.
- **Décision :** sous 760 px, logo à gauche à la hauteur des deux rangées ; les commandes s’enroulent uniquement à droite.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-16 — Une ligne compacte sur ordinateur

- **Initiative :** `coherence-textes-publics`.
- **Signal :** sur PC, Présentation tombait seul sous un logo trop haut.
- **Décision :** logo à la hauteur des boutons ; une seule rangée (nowrap) sur grand écran, retour à la ligne seulement sous 760 px.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-16 — Boutons à droite du logo, sans passage dessous

- **Initiative :** `coherence-textes-publics`.
- **Signal :** Présentation passait encore sous le logo.
- **Décision :** logo flottant à gauche ; les commandes s’enroulent dans l’espace à droite (plus de superposition).
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-16 — Logo et boutons sans superposition

- **Initiative :** `coherence-textes-publics`.
- **Signal :** le logo étiré recouvrait Menu et Agrandir.
- **Décision :** taille fixe du logo ; marge gauche réservée plus large que le logo, pour que les boutons restent à droite.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-16 — Logo compact à la hauteur des deux rangées

- **Initiative :** `coherence-textes-publics`.
- **Signal :** sur smartphone le logo restait petit (plafond 40 px) à côté des deux rangées de boutons.
- **Décision :** le logo s’étire de haut en bas du bandeau compact, sans réduction sur petit écran.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-15 — Agrandir le logo à côté des boutons réduits

- **Initiative :** `coherence-textes-publics`.
- **Signal :** le logo compact restait trop petit à côté du groupe de boutons (deux rangées).
- **Décision :** logo calé sur la hauteur du bandeau (≈ 48 px, 40 px sur petit écran), pas sur un seul bouton.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-15 — Logo compact à l’échelle des boutons

- **Initiative :** `coherence-textes-publics`.
- **Signal :** après le resserrement des boutons, le logo compact restait trop grand.
- **Décision :** hauteur du logo alignée sur les commandes (≈ 22 px, 18 px sur petit écran), marge gauche réduite.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-15 — Boutons encore plus serrés en mode réduit

- **Initiative :** `coherence-textes-publics`.
- **Signal :** les boutons du mode réduit restaient gros (min-height 44 px imposée après coup par les media queries).
- **Décision :** surcharge plus spécifique : hauteur auto, padding collé au texte, y compris sous 760 px et au toucher.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-15 — Réduire le padding des boutons en mode compact

- **Initiative :** `coherence-textes-publics`.
- **Signal :** en mode réduit, surtout sur smartphone, les boutons étaient trop grands autour du texte.
- **Décision :** les commandes d’en-tête compactes épousent le libellé (plus de stretching à 33 %), padding et taille de caractère diminués.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-15 — Ranger les boutons du mode réduit

- **Initiative :** `coherence-textes-publics`.
- **Signal :** en en-tête réduit, Menu, Agrandir, Parcours, Affichage et Présentation s’empilaient sans alignement.
- **Décision :** logo à gauche ; les cinq commandes se rangent en rangées égales (trois puis deux), même hauteur, hors du flux du menu déroulant.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-15 — Logo compact hors du groupe de boutons

- **Initiative :** `coherence-textes-publics`.
- **Signal :** en en-tête réduit, le logo s’insérait entre Agrandir et Parcours.
- **Décision :** le logo compact est calé en haut à gauche de la barre, hors du flux des boutons.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.

## 2026-10-15 — Chaque phrase commence en début de ligne

- **Initiative :** `coherence-textes-publics`.
- **Signal :** les débuts de phrase se retrouvaient au milieu d’une ligne, avec la suite en dessous.
- **Décision :** dans le contenu principal, chaque phrase est affichée comme un bloc (`span.phrase`), en protégeant les abréviations (M.R.S.C., ÉVA, etc.).
- **Contrôles réellement exécutés :** `node --check assets/js/site.js` ; `verifier-site-statique.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** sans JavaScript, les paragraphes restent continus.

## 2026-10-15 — Visuel d’accueil validé

- **Initiative :** `coherence-textes-publics`.
- **Signal :** la légende présentait encore le bandeau 3D comme une proposition à relire, alors qu’il a été validé.
- **Décision :** retirer la mention « à relire / pas encore l’identité officielle ». Le visuel d’accueil `accueil-logo-mrsc-3d.jpg` est l’image retenue.
- **Contrôles réellement exécutés :** `verifier-rd-continue.py` ; `verifier-site-statique.py` — réussis.
- **Limites et suite :** l’en-tête compact conserve le logo plat, plus lisible en petit format.

## 2026-10-15 — Navigation sans retour à la ligne et prénom Éva

- **Initiative :** `coherence-textes-publics`.
- **Signal :** les libellés du menu (IA & société, Liens utiles, Nous contacter) se cassaient ; les phrases partaient en milieu de ligne ; préciser qu’ÉVA donne le prénom Éva.
- **Décision :** `white-space: nowrap` sur les liens de navigation. Typographie : `text-wrap: pretty`, pas de césure au milieu des mots. Accueil et page ÉVA : l’acronyme Entité Virtuelle Autonome donne le prénom **Éva** à l’entité du projet.
- **Contrôles réellement exécutés :** `verifier-site-statique.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** le visuel 3D d’accueil est validé ; ne pas le modifier.

## 2026-10-15 — Visuel 3D à l’accueil et logo en en-tête réduit

- **Initiative :** `coherence-textes-publics`.
- **Signal :** en mode réduit, l’identité disparaît ; intégrer le visuel 3D choisi à l’accueil.
- **Décision :** bandeau d’accueil avec `accueil-logo-mrsc-3d.jpg` (proposition R&D, légende explicite). En en-tête compact, garder un petit logo plat pour identifier l’onglet de navigation.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-site-statique.py` ; `verifier-rd-continue.py` ; `verifier-integration.py` ; `verifier-securite.py` — réussis.
- **Limites et suite :** le visuel 3D n’est pas l’identité officielle ; relecture humaine du cadrage.

## 2026-10-15 — R&D, innovation et prospective : source de santé publique

- **Initiative :** `prospective-apprentissages-2030` et `relire-les-44-prototypes` (titre porté à 55 prototypes).
- **Signal :** continuer la R&D, l’innovation et la prospective, puis fusionner.
- **Décision :** prototype `sante-reperer-source-publique` (Message-exemple, sirop miracle fictif). Aucun conseil médical. Sujet `sources-sante` passé à `partiel`. Note prospective : compteurs 81/55 ; identification visuelle locale (favicon) comme capacité sans regret ; piste Boussole vers cette fiche.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-site-statique.py` ; `verifier-rd-continue.py` ; `verifier-integration.py` ; `verifier-securite.py` — réussis.
- **Limites et suite :** relecture santé/médias ; l’initiative prospective reste `a-cadrer`.

## 2026-10-15 — Favicon au logo M.R.S.C.

- **Initiative :** `coherence-textes-publics`.
- **Signal :** pas d’icône dans la barre d’onglets / favoris ; le logo identifie mieux le site.
- **Décision :** publier `favicon.ico` (dérivé de `logo-mrsc.jpg`) et des PNG 32 / 180, liés depuis toutes les pages publiques, sans ressource distante.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-site-statique.py` ; `verifier-rd-continue.py` ; `verifier-integration.py` ; `verifier-securite.py` — réussis.
- **Limites et suite :** à 16 px le texte du logo reste peu lisible ; l’identification repose sur la forme et les couleurs.

## 2026-10-15 — Échelle France / monde sur une frise fictive

- **Initiative :** `relire-les-44-prototypes` (titre porté à 54 prototypes).
- **Signal :** continuer et fusionner.
- **Décision :** prototype `histoire-reperer-echelle-france-monde` (Frise-exemple, Val-exemple). Sujet `histoire-monde-france` passé à `partiel`. Aucune chronologie officielle.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-site-statique.py` ; `verifier-rd-continue.py` ; `verifier-integration.py` ; `verifier-securite.py` — réussis.
- **Limites et suite :** relecture historique humaine.

## 2026-10-15 — R&D, innovation et prospective : citation / résumé

- **Initiative :** `prospective-apprentissages-2030` et `relire-les-44-prototypes` (titre porté à 53 prototypes).
- **Signal :** demander de faire la R&D, l’innovation et la prospective, puis fusionner.
- **Décision :** prototype `recherche-distinguer-resume-citation` (Carte-exemple, jeu de billes fictif). Sujet `methodes-universitaires` passé à `partiel`. Actualiser les compteurs de la note prospective (79/53) et ajouter une capacité « sans regret » : partir de ce que la personne sait déjà. La Boussole reste un concept, non une fonction du site.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-site-statique.py` ; `verifier-rd-continue.py` ; `verifier-integration.py` ; `verifier-securite.py` — réussis.
- **Limites et suite :** relecture méthodologique ; aucun style de citation imposé. L’initiative prospective reste `a-cadrer` jusqu’à examen par l’association.

## 2026-10-15 — Valoriser les langues déjà connues

- **Initiative :** `coherence-textes-publics` et `relire-les-44-prototypes` (titre porté à 52 prototypes).
- **Signal :** poursuivre le cycle et produire du contenu qui valorise l’apprentissage.
- **Décision :** prototype `langue-reperer-mot-deja-connu` (Affiche-exemple Entrée/Entrada). S’appuyer sur un mot déjà familier. Sujet `autres-langues` passé à `partiel`.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-site-statique.py` ; `verifier-rd-continue.py` ; `verifier-integration.py` ; `verifier-securite.py` — réussis.
- **Limites et suite :** relecture langues/FLE ; pas d’audio. Écoute/prononciation reste `a-creer`.

## 2026-10-15 — Prototype intérêt / frais sur un crédit fictif

- **Initiative :** `relire-les-44-prototypes` (titre porté à 51 prototypes).
- **Signal :** poursuivre le cycle R&D après fusion de la PR #52 ; sujet `banque-credit-interets` encore à créer.
- **Décision :** prototype `econ-distinguer-interet-frais` (tableau inventé « Prêt-exemple », 100 €, 5 € d’intérêt, 3 € de frais). Aucun conseil d’emprunt. Sujet passé à `partiel`.
- **Contrôles réellement exécutés :** `construire-apprentissages.py --verifier` ; `verifier-site-statique.py` ; `verifier-rd-continue.py` ; `verifier-integration.py` ; `verifier-securite.py` — réussis.
- **Limites et suite :** relecture financière humaine ; ne pas copier de barème. Autres sujets `a-creer` inchangés.

## 2026-10-15 — Valoriser l’apprentissage et prototype d’information électorale

- **Initiative :** `coherence-textes-publics` et `relire-les-44-prototypes` (titre porté à 50 prototypes).
- **Signal :** la personne demande de valoriser l’apprentissage (après le retrait du CP) et de poursuivre la R&D.
- **Décision :** l’accueil Apprendre part de ce que la personne vit déjà ; le repère 1 s’appelle « Premiers pas » et non « Reprendre les bases ». Ajouter le prototype `civ-reperer-info-electorale` (sujet élections, statut partiel), sans consigne de vote.
- **Contrôles réellement exécutés :** à compléter après vérification.
- **Limites et suite :** relecture humaine du ton et du prototype. Les droits du travail restent `a-creer`.

## 2026-10-15 — Retirer le repère « CP » des textes d’accueil de l’apprentissage

- **Initiative :** `coherence-textes-publics`, maintenue à l’état `a-valider`.
- **Signal :** la personne a vu sur le site la mention « des bases du CP jusqu’aux spécialités », jugée trop péjorative pour qui vient apprendre, et un compteur encore affiché à 73/47 (déploiement antérieur).
- **Décision :** ne plus renvoyer le public vers un niveau scolaire (CP) dans le cap visé, la carte de couverture et l’horizon de planification. Formuler des « premiers pas utiles », et rappeler que chacun peut commencer où il en a besoin. Les compteurs publics restent ceux du catalogue généré (75 entrées, 49 prototypes).
- **Changements :** générateur d’apprentissages, `plan-1000.toml`, carte générée, notice de parcours. Aucune fiche n’est présentée comme validée.
- **Contrôles réellement exécutés :** `verifier-rd-continue.py` ; `construire-apprentissages.py --verifier` ; `test_protocole_editorial.py` ; `verifier-site-statique.py` ; `verifier-securite.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** la page publique ne se met à jour qu’après fusion et publication Pages. Faire relire humainement le ton.

## 2026-10-15 — Prototype lecture d’une mention de garantie

- **Initiative :** `relire-les-44-prototypes` (titre porté à 49 prototypes).
- **Question :** comment lire un ticket d’achat fictif (vendeur, objet, prix, date, mention) sans enseigner le droit de la garantie ?
- **Base vérifiée :** le sujet `consommation-contrats` était `a-creer`. Pages consultées le 15 octobre 2026 : accueil DGCCRF et SignalConso. Aucune durée légale, enquête ni étape de formulaire n’est reprise.
- **Décision :** prototype `econ-lire-mention-garantie`. Sujet passé à `partiel`.
- **Contrôles réellement exécutés :** compilation Python ; `verifier-rd-continue.py` ; `construire-apprentissages.py` puis `--verifier` (75 fiches, 15 domaines) ; `construire-simulateur.py --verifier` ; `test_protocole_editorial.py` (7 tests) ; `verifier-site-statique.py` ; `verifier-securite.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** à relire (consommation, accessibilité). Banque/crédit et impôts restent `a-creer`.

## 2026-10-15 — Prototype d’échelle d’institution

- **Initiative :** `relire-les-44-prototypes` (titre porté à 48 prototypes).
- **Question :** comment commencer une recherche d’information publique par l’échelle (proximité, nationale, européenne) sans enseigner un organigramme ?
- **Base vérifiée :** le sujet `institutions-droits` était `a-creer`. Portails consultés le 15 octobre 2026 : Vie publique (rubrique fiches) et Service-Public (accueil). Aucune fiche institutionnelle n’est recopiée.
- **Décision :** prototype `civ-reperer-echelle-institution` avec trois questions fictives. Sujet passé à `partiel`.
- **Contrôles réellement exécutés :** compilation Python ; `verifier-rd-continue.py` ; `construire-apprentissages.py` puis `--verifier` (74 fiches, 15 domaines) ; `construire-simulateur.py --verifier` ; `test_protocole_editorial.py` (7 tests) ; `verifier-site-statique.py` ; `verifier-securite.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** à relire (institutions, accessibilité). Les élections et le droit du travail restent `a-creer`.

## 2026-10-15 — Prototype lecture d’une licence logicielle

- **Initiative :** `relire-les-44-prototypes` (titre porté à 47 prototypes).
- **Question :** comment aider à lire une notice de licence avant de réutiliser un programme, sans donner d’avis juridique ?
- **Base vérifiée :** le sujet `genie-logiciel-droits` était `a-creer`. Pages consultées le 15 octobre 2026 : Open Source Definition (OSI) et SPDX License List. Aucun critère OSD ni identifiant SPDX n’est recopié.
- **Décision :** prototype `prog-lire-licence-logiciel` avec notice fictive « horloge-exemple ». Sujet passé à `partiel`.
- **Contrôles réellement exécutés :** compilation Python ; `verifier-rd-continue.py` ; `construire-apprentissages.py` puis `--verifier` (73 fiches, 15 domaines) ; `construire-simulateur.py --verifier` ; `test_protocole_editorial.py` (7 tests) ; `verifier-site-statique.py` ; `verifier-securite.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** à relire (PI du logiciel, accessibilité). Le travail collectif et les licences copyleft ne sont pas couverts.

## 2026-10-15 — Prototype table / requête / page Web

- **Initiative :** `relire-les-44-prototypes` (titre porté à 46 prototypes).
- **Question :** comment distinguer un stockage structuré, une question posée aux données et un affichage Web, sans enseigner un langage de requête ?
- **Base vérifiée :** le sujet `bases-donnees-web` était `a-creer`. Pages consultées le 15 octobre 2026 : MDN « relation client-serveur » (requête/réponse du navigateur) et l’accueil de data.gouv.fr (catalogue distinct des pages de présentation). Aucun extrait ni chiffre de bandeau n’est repris.
- **Décision :** prototype `info-table-requete-web` avec club fictif « Atelier des cartes ». Sujet passé à `partiel`. Pas de SQL, pas d’API, pas de configuration.
- **Contrôles réellement exécutés :** compilation Python ; `verifier-rd-continue.py` ; `construire-apprentissages.py` puis `--verifier` (72 fiches, 15 domaines) ; `construire-simulateur.py --verifier` ; `test_protocole_editorial.py` (7 tests) ; `verifier-site-statique.py` ; `verifier-securite.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** à relire (bases de données, Web, accessibilité). Les sujets `genie-logiciel-droits` et `systemes-embarques` restent `a-creer`.

## 2026-10-15 — Prototype d’orientation vers un service public

- **Initiative :** `relire-les-44-prototypes` (titre porté à 45 prototypes), en lien avec `veille-savoirs-evolutifs`.
- **Question :** comment aider à trouver un point d’entrée public et à préparer un formulaire, sans enseigner une procédure en vigueur ni un conseil juridique ?
- **Base vérifiée :** le sujet `services-publics` du référentiel était `a-creer`. Les pages d’accueil de Service-Public (15 octobre 2026) et de France services (même jour) se présentent comme orientation / accompagnement ; la fiche hameçonnage de Cybermalveillance.gouv.fr a été lue pour le risque des liens reçus. Le site de la CNIL était en maintenance : aucune affirmation n’en est tirée.
- **Décision :** publier un prototype autonome `civ-trouver-service-public` (exercice fictif, analogie du guichet, limites explicites). Passer le sujet à `partiel`. Ne pas recopier de démarche, délai, slogan ni statistique des sites consultés.
- **Changements :** source TOML, référentiel, page générée, atlas, grille de relecture, compteurs 71/45, portefeuille.
- **Contrôles réellement exécutés :** compilation Python ; `verifier-rd-continue.py` ; `construire-apprentissages.py` puis `--verifier` (71 fiches, 15 domaines) ; `construire-simulateur.py --verifier` ; `test_protocole_editorial.py` (7 tests) ; `verifier-site-statique.py` ; `verifier-securite.py` ; `verifier-integration.py` — réussis.
- **Limites et suite :** prototype à relire ; pas d’essai avec des personnes ; les sources évoluent. Faire relire démarches et accessibilité. Le sujet `droits-travail` reste `a-creer`.

## 2026-10-15 — Proposition de présentation publique prudente pour ÉVA

- **Initiative :** `documentation-rd-eva`, conservée à l’état `a-cadrer`.
- **Constat :** la PR #44 (`c3c9ce2`) a ajouté `eva.html` et relié la page depuis l’accueil, le sitemap et `llms.txt`, mais le workflow Pages ne la publiait pas. Le document source est identifié comme rédigé par une IA et non relu. La demande actuelle est d’introduire ÉVA dans sa section dédiée, sans détails personnels, procédés internes ni secrets, et d’expliquer le besoin général de matériel et de financements.
- **Décision :** formuler une présentation générale qui distingue objectifs de recherche et capacités disponibles, ne revendique aucune conscience et ne publie ni détail de production, ni donnée personnelle, ni montant. Présenter le matériel et les moyens financiers comme un besoin à confirmer, pas comme un budget ou appel aux dons approuvé. Garder clairement le statut de proposition préparée avec l’aide d’une IA, à relire, et la séparation d’avec toute position officielle de l’association.
- **Changements :** le bloc `index.html#rd-eva` et `eva.html` présentent cette version générale; `llms.txt` et le registre de `transparence.html` sont alignés. La copie Pages, l’aperçu local et leurs vérifications incluent la page assainie. Le portefeuille reste `a-cadrer` et demande la confirmation des besoins matériels/financiers et de leur publication.
- **Contrôles réellement exécutés :** `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`; `python3 outils/construire-apprentissages.py --verifier` (70 fiches, 15 domaines); `python3 outils/construire-simulateur.py --verifier`; `python3 outils/verifier-rd-continue.py` (13 initiatives); `python3 outils/test_protocole_editorial.py` (7 tests); `python3 outils/verifier-site-statique.py` (84 pages, 83 URL publiques dans le sitemap); `python3 outils/verifier-securite.py`; `python3 outils/verifier-integration.py` (84 pages d’interface et 16 routes API locales); `git diff --check` — réussis.
- **Limites et suite :** aucune relecture par les personnes responsables du projet, vérification indépendante de capacité technique ou confirmation d’un budget n’est revendiquée. La page reste une proposition à relire. Le texte détaillé de la PR #44 est déjà présent dans l’historique public du dépôt; remplacer le fichier courant ne retire pas les anciens commits. Aucune réécriture d’historique n’est faite. Faire relire cette proposition et confirmer les besoins, le budget et toute éventuelle collecte avant communication officielle; si des informations anciennes doivent réellement être retirées de toutes les révisions, il faudra une procédure distincte de purge d’historique et une autorisation explicite.

## 2026-10-15 — Migration de la cible déclarée du simulateur vers Vercel

- **Initiative :** `coherence-textes-publics`, maintenue à l’état `a-valider`.
- **Signal :** le lien de `simulateur.html`, la sonde et plusieurs consignes indiquaient encore Render alors que la personne a fourni l’alias Vercel du simulateur.
- **Éléments GitHub consultés :** le dépôt amont déclare cet alias comme `homepageUrl`; sa branche `main` contient `index.html` et `api/[...path].py`. La PR amont #53 est fusionnée et GitHub signale un déploiement *Production — success* pour le commit `b7a2d7242f6d8f32efc4b86839baf969208d3a57`. L’observation 404 de `docs/diagnostic-404-vercel.md` correspond à un état précédent.
- **Décision :** utiliser l’alias Vercel déclaré comme cible par défaut du site M.R.S.C ; conserver l’hôte Render dans la liste autorisée uniquement pour compatibilité, sans le présenter comme source actuellement vérifiée.
- **Changements :** liens, aperçu, libellés, sonde et allowlist mis à jour ; README, guide d’intégration, prompt de maintenance, notice publique et inventaire de confidentialité actualisés. Le diagnostic 404 est conservé comme historique, avec un avertissement explicite sur son statut. La prochaine vérification humaine et le besoin de confirmer les informations de l’hébergeur sont ajoutés au portefeuille.
- **Contrôles réellement exécutés :** compilation Python ; `node --check assets/js/site.js` ; `verifier-rd-continue.py` ; `construire-apprentissages.py --verifier` ; `construire-simulateur.py --verifier` ; `verifier-site-statique.py` (83 pages) ; `verifier-securite.py` (hôtes Vercel/Render exacts, domaines voisins, localhost et autres contrôles ciblés) ; `verifier-integration.py` (page, 16 routes API, cible déclarée et source simulée) — réussis. `git diff --check` — réussi après l’ajout de cette entrée.
- **Limites et suite :** aucun accès HTTP direct à Vercel ou Render, aucun test des API, calculs, iframe ou navigateur public n’a été effectué. Le statut GitHub de déploiement ne prouve pas leur fonctionnement. Après publication, ouvrir l’alias puis `/api/scenarios` et `/api/catalogue`, effectuer un calcul et vérifier l’iframe depuis `simulateur.html`; si l’alias tourne encore en chargement, relever les erreurs console/réseau. L’association doit confirmer les informations de confidentialité propres au fournisseur. Aucune validation complète n’est revendiquée.

## 2026-10-15 — Tâches candidates pour les contrôles d’affichage et de navigation

- **Initiative :** `co-conception-et-essais`, maintenue à l’état `a-cadrer`.
- **Signal observé dans le dépôt :** le protocole existant proposait huit tâches centrées sur le catalogue, les fiches et les Escales; depuis sa rédaction, le site comporte également des panneaux « Affichage », « Présentation », « Parcours » et un contrôle « Réduire/Agrandir ». Le protocole ne séparait pas leurs usages ni leurs conditions mobile/clavier.
- **Options examinées :** élargir les tâches A7/A8 aurait mélangé l’accès au contenu et la découverte des commandes; attendre toute revue humaine avant même de rédiger des tâches aurait laissé les nouveaux contrôles sans scénario candidat. Le choix réversible est de séparer B1–B6 en brouillon, sans les utiliser avant les revues requises.
- **Décision :** ajouter six propositions B1–B6 pour explorer le réglage du texte, les mises en page, l’en-tête, l’usage clavier/Échap, le reflow à petite largeur et, sur choix volontaire, une technologie d’assistance. Elles complètent les tâches A1–A8 sans changer les fonctions du site. Ces consignes restent des brouillons; aucune séance, revue experte, approbation du consentement ou autorisation de recrutement n’est revendiquée.
- **Changements :** `docs/rd/protocole-essais-usage.md` précise les tâches candidates et une préparation technique qui évite d’effacer les données ou préférences d’un appareil personnel et n’ajoute ni enregistrement d’écran/voix ni chronométrage par défaut. `docs/rd/portefeuille.toml` conserve `a-cadrer` et exige une relecture des rôles d’accessibilité, d’édition et de confidentialité/droit ainsi que la confirmation du consentement et de la conservation des notes avant toute séance.
- **Contrôles :** `python3 outils/verifier-rd-continue.py` et `git diff --check` — exécutés après ces modifications et réussis.
- **Limites et suite :** les tâches sont des hypothèses de conception, pas des preuves d’utilisabilité, d’accessibilité ou de compréhension. Aucune personne n’a été recrutée ni testée. Faire relire le protocole et définir le cadre de données avant de préparer des essais volontaires; garder l’initiative `a-cadrer` jusque-là.

## 2026-10-15 — Prospective et innovation pour l’apprentissage à l’horizon 2030

- **Initiative :** `prospective-apprentissages-2030`, ajoutée au portefeuille à l’état `a-cadrer` et priorité `P1`.
- **Question :** quelles capacités d’apprentissage et de délibération restent utiles sous plusieurs futurs plausibles de médiation numérique, continuité des services, langues et capacité de relecture ? L’horizon 2027–2030 sert à organiser une réflexion, pas à annoncer une prédiction.
- **Base vérifiée dans le dépôt :** 70 fiches suivies dans 15 domaines, dont 44 prototypes à relire; cinq Escales d’anglais; réglages de présentation locaux; simulateur distant déclaré Vercel mais non vérifié directement. Un contrôle TOML ciblé confirme que les six fiches du parcours pilote existent et que leurs sujets sont tous au statut `partiel`. Les sources sont les registres et notes de R&D locales; aucune veille externe actuelle, enquête de besoin, atelier de l’association ou session de test n’a été menée dans cette passe.
- **Options comparées :** Boussole des savoirs à partir des fiches existantes; passeport de traçabilité d’un résultat du simulateur; kit autonome/à imprimer; ne rien construire. La note propose une Boussole comme candidat au prototype papier uniquement, parce qu’elle peut réutiliser les identifiants et statuts déjà présents sans API, profil, IA ni nouvelle saisie. Le concept est rejetable si les filtres de l’atlas suffisent ou si les relations augmentent la confusion et la maintenance.
- **Changements :** création de `docs/rd/prospective-2027-2030.md` avec quatre scénarios de stress sans probabilité, les incertitudes, les choix robustes, une route illustrative de vérification d’information et les portes d’approbation; ajout de l’initiative et de ses critères au `portefeuille.toml`. Une synthèse destinée au public est préparée dans `transparence.html#prospective-2030`, avec renvoi vers la note de travail et son statut non validé; le registre de traçabilité et les tests d’intégration couvrent le contenu et le style de l’encadré. Les titres et le repère de statut de cet encadré ont un contraste explicite. Le portefeuille référence maintenant aussi la page publique. Le statut de l’initiative reste `a-cadrer`.
- **Contrôles réellement exécutés après la synthèse :** compilation Python; vérifications des sorties apprentissages et simulateur; `python3 outils/verifier-rd-continue.py` (13 initiatives); `python3 outils/test_protocole_editorial.py` (7 tests); vérificateurs statique, sécurité et intégration (16 routes API locales, dont l’assertion prospective); contrôle TOML des six fiches/statuts du parcours; vérification des 14 liens locaux de la note; `git diff --check` — réussis.
- **Limites et suite :** les scénarios sont des hypothèses de conception, pas des prévisions ni des faits externes; aucun balayage externe récent, atelier avec l’association ou test avec des personnes n’a été réalisé. Le concept n’est ni construit, ni approuvé, ni testé. La synthèse publique reprend ces limites, mais n’a pas fait l’objet d’une revue visuelle humaine. Faire examiner l’angle par l’association, sélectionner ou écarter le pilote, puis consulter et recouper des sources externes primaires sur les axes retenus avant d’annoncer une tendance ou de passer au prototype.

## 2026-10-14 — Largeur stable du bouton Agrandir/Réduire

- **Initiative :** `optimisation-du-site`, maintenue à l’état `a-tester`.
- **Signal et reproduction :** après la correction du retour compact, le bouton changeait encore visiblement de largeur quand son texte basculait. Le test Chromium ciblé a reproduit le cas à 720 px et échoué à 7/8 : cadre de 83,859 px avec « Agrandir », puis 77,266 px avec « Réduire ».
- **Cause établie :** le bouton avait `flex: 0 1 auto`; sa largeur suivait le texte, et son cadre n’était pas réservé au libellé le plus large. Le code de redimensionnement réassignait également le même texte tant que la fenêtre continuait de rétrécir sous 520 px.
- **Correction :** réserver une base fixe de 100 px CSS pour les deux libellés, borner cette base à la largeur du viewport moins 16 px aux tailles extrêmes, permettre le retour à la ligne dans le cadre et garder une hauteur minimale de 44 px. Le bouton Menu ne rétrécit plus; les autres contrôles de la barre gardent aussi leur largeur et passent à la ligne comme un groupe. `setHeaderCompact` devient idempotent et l’écouteur de réduction ne réapplique pas l’état si l’en-tête est déjà compact.
- **Contrôles réellement exécutés :** `MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules node outils/test-experience.cjs` — **8/8 essais réussis** après correction, avec stabilité du cadre aux libellés Agrandir/Réduire à 720 et 500 px, aucune mutation du libellé à 480 → 460 px quand il est déjà compact, flex-shrink nul sur les contrôles visibles à 320 px et cadre/texte contenus à 240 et 70 px. Une relance avec un serveur HTTP statique simple occupant le port 4173 a échoué sur les cas simulateur (`/api/catalogue` renvoyait 404) ; après remplacement par `outils/serveur-local.py --bind 0.0.0.0 --port 4173`, les 8/8 essais ont réussi. `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`, vérificateur R&D, générateurs apprentissages/simulateur en mode vérification, vérificateurs statique, sécurité et intégration, `node --check assets/js/site.js`, `node --check outils/test-experience.cjs` et `git diff --check` — réussis. Le contrôle `qualite` de la PR #40 a aussi réussi.
- **Publication vérifiée :** la PR #40 a été fusionnée dans `main` (merge commit `01bbed52e32aa5e9c28dd926fadf8c27050c81f7`). Le workflow `Publish M.R.S.C site`, run `38643494034`, s’est terminé avec succès ; ses étapes de préparation, téléversement et déploiement GitHub Pages sont toutes réussies. L’API Pages confirme l’URL publique `https://thejmimiia-code.github.io/MRSC/`. L’URL publique n’a pas été récupérée indépendamment depuis cet environnement.
- **Limites et suite :** les mesures sont automatisées en Chromium headless. Aucune revue visuelle humaine après correction, aucun essai avec lecteur d’écran ni personne utilisatrice n’est revendiqué. Conserver `a-tester`; l’aperçu local complet est disponible sur le port 4173. Vérifier visuellement la barre à 320/375/720 px, puis reprendre la matrice clavier, tactile, zoom natif et technologies d’assistance.

## 2026-10-14 — Essais Chromium des panneaux et du reflow mobile

- **Initiative :** `optimisation-du-site`.
- **Périmètre :** création du harnais navigateur `outils/test-experience.cjs`, dans la continuité de la matrice d’essais. Chromium headless et Puppeteer ont été installés temporairement sous `/tmp`, sans dépendance ajoutée au site ni au dépôt.
- **Défauts observés et corrections :** des panneaux positionnés en absolu restaient disposés lorsque leur `<details>` était fermé ; les styles communs et le générateur du simulateur masquent désormais explicitement le panneau jusqu’à l’ouverture. À 320 px en « Panorama composite », une piste de 300 px imposait quelques pixels de débordement ; le générateur borne maintenant la piste à `min(300px,100%)`, et les sources/étiquettes longues du simulateur peuvent revenir à la ligne. À 150 % de texte et avec contraste/espacement renforcés, le panneau « Présentation » du site pouvait dépasser en bas ; sa hauteur réserve l’espace de la barre d’ancrage. Dans le simulateur, « Parcours » et « Présentation » sont fixés au coin supérieur sur petit écran pour ne pas rester sous la barre haute avec `backdrop-filter` ; le navigateur vérifie leurs limites et leur premier plan.
- **Contrôles navigateur réellement exécutés :** `MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules node outils/test-experience.cjs` — **7/7 essais réussis** : sélection immédiate et contenu inchangé, réglages existants préservés, navigation/persistance/réinitialisation, clavier/Échap/focus et chevrons, panneaux fermés réellement masqués, six pages représentatives à 320/1440 px, paysage court, taille 150 % + contraste/espacement, stockage autorisé puis bloqué sur le site et le simulateur, guide du simulateur, panneau local à 320 × 375 et synchronisation avec l’iframe locale de même origine.
- **Contrôles complets exécutés après les changements :** compilation Python ; `verifier-rd-continue.py` ; générateur d’apprentissages en mode vérification ; générateur du simulateur puis `--verifier` ; site statique (83 pages) ; sécurité ; intégration (incluant les 16 routes API locales) ; 7 tests du protocole éditorial ; `node --check` des deux scripts du site et du nouveau harnais ; `git diff --check` — réussis. Le vérificateur statique et les tests de sécurité ont aussi été relancés séparément, avec succès.
- **Limites et suite :** les sept essais couvrent des pages types et des interactions déterminées, pas les 83 pages à tous les breakpoints. Aucun Firefox/Safari, essai visuel humain, lecteur d’écran, appareil physique ou utilisation par des personnes n’est revendiqué ; la conformité WCAG reste à évaluer. Garder l’initiative `a-tester` et réaliser les vérifications humaines/technologies d’assistance décrites dans la matrice avant de réviser son statut.

## 2026-10-14 — Recompactage de l’en-tête en fenêtre très étroite

- **Initiative :** `optimisation-du-site`, maintenue à l’état `a-tester`.
- **Signal rapporté en Chrome :** en réduisant fortement la largeur de la fenêtre, le bouton « Agrandir » présentait un défaut visuel et la personne souhaitait que le site revienne à sa forme compacte pour l’afficher à côté d’une autre fenêtre, sans le fermer.
- **Diagnostic vérifié :** le mode compact initial se déclenche déjà sous 760 px. Mais après l’action volontaire « Agrandir », une réduction de 720 à 500 px conservait l’en-tête ouvert : le seuil 760 px était déjà franchi, donc son événement de changement ne se déclenchait pas une seconde fois. Le nouveau cas navigateur a échoué avant le correctif à l’attente du retour compact.
- **Correction :** une écoute du redimensionnement active à 520 px ou moins replie de nouveau l’en-tête à chaque réduction de largeur ; le bouton reste utilisable après ce redimensionnement. Son cadre est borné à la largeur disponible et, si nécessaire, le libellé se replie à l’intérieur au lieu de sortir de la bordure.
- **Contrôle navigateur :** le harnais Chromium headless exécute maintenant le parcours 720 → agrandissement manuel → 500 → 320 → 240 px, avec de nouveaux agrandissements entre les étapes ; il contrôle le repli des informations de marque, l’absence de débordement de document à 320 px, le libellé sur une ligne à 240 px et son maintien dans le cadre à 70 px. Résultat après correction : **8/8 essais**.
- **Suite et limites :** code et affichage testés en Chromium headless ; le défaut visuel n’a pas encore été revérifié manuellement dans Chrome après le correctif. Conserver `a-tester` et demander une nouvelle vérification visuelle au même niveau de compression, puis poursuivre la revue clavier, tactile et lecteur d’écran. Aucun suivi d’usage n’est ajouté.

## 2026-10-14 — Protocole éditorial et contexte des échanges repris depuis Drive

- **Initiative :** `coherence-textes-publics` ; articulation avec `optimisation-du-site`.
- **Signal et décision :** les échanges transmis confirment une ligne éditoriale positive et concrète fondée sur les expériences, le partage des savoirs et des propositions compréhensibles. Ils demandent une méthode permanente, des contenus ludiques utiles, des sources visibles et une cohérence à l’échelle du site. La proposition antérieure centrée sur ÉVA dans le document Drive n’annule pas le choix explicite retenu pour l’accueil : présentation de l’association et trois rubriques, sans la présenter comme une décision officielle.
- **Contexte de sauvegarde :** la notice Drive décrit un ancien instantané de 261 fichiers sur la branche `arena/9f768afc-mrsc`, base `a1049e8`, non publié et non fusionné à la date de l’archive. Son état de travail signale notamment des essais navigateur/accessibilité inachevés. Il n’a pas été restauré par-dessus le dépôt plus récent ; les fonctions de personnalisation et les contrôles structurels déjà présents dans ce dépôt ont été conservés.
- **Changements :** création de `docs/protocole-editorial.md` et `docs/gabarits/contenu-editorial.md`, références ajoutées à `AGENTS.md`, au README et au dossier de cohérence, initiative du portefeuille mise à jour, et sept tests structurels dans `outils/test_protocole_editorial.py`, appelés par la CI et le workflow de publication.
- **Contrôles réellement exécutés à cette étape :** `python3 outils/test_protocole_editorial.py` — sept tests réussis.
- **Limites et suite :** ce cadre guide les prochains lots mais ne certifie pas les pages existantes ; la revue des pages, des sources et des droits demeure progressive et humaine. La matrice de rendu mobile/clavier/stockage de l’initiative `optimisation-du-site` reste distincte et à rejouer ; le script navigateur décrit dans l’ancienne sauvegarde n’est pas présent dans le checkout courant.

## 2026-10-14 — Délai de déploiement GitHub Pages après la nouvelle présentation

- **Initiative :** `coherence-textes-publics`.
- **Signal :** après la fusion de la PR #35, le contrôle qualité et la veille ont réussi, mais la publication Pages a expiré pendant `Deploy to GitHub Pages` (run `38593400963`). Une nouvelle tentative après la PR #36 a échoué de la même façon après 10 min 55 s (run `38595622343`) ; les vérifications et le téléversement de l’artefact ont réussi.
- **Diagnostic et correction :** le code de `actions/deploy-pages@v5.0.1` fixe `MAX_TIMEOUT` à 600 000 ms. La tentative de demander 20 minutes a été ramenée à ce maximum par l’action, avec un avertissement ; cette configuration sans effet a donc été retirée. La cause du déploiement qui reste en attente n’est pas établie.
- **Contrôles exécutés :** vérificateurs locaux d’intégration, sécurité, pages statiques et continuité R&D réussis ; CI de la PR #36 réussie. Les deux exécutions de publication, elles, ont échoué au déploiement. La récupération des journaux d’exécution n’a pas abouti (EOF du serveur de résultats Actions).
- **Limites et suite :** le rejeu manuel et `workflow_dispatch` sont refusés par les permissions GitHub de cette intégration (`actions:write`). La cause précise reste inconnue et la mise en ligne n’est pas confirmée ; vérifier le statut/service Pages et réessayer lorsqu’un rejeu ou une nouvelle publication est possible.

## 2026-10-14 — Présentation de l’association et trois repères de réflexion sur l’accueil

- **Initiative :** `coherence-textes-publics`.
- **Signal et décision :** l’utilisateur a retrouvé et fourni une proposition de rédaction issue d’Arena, absente du dépôt. Il a choisi d’intégrer la présentation complète de l’association et les trois rubriques courtes, plutôt qu’une seule phrase de remplacement.
- **Vérification de source :** extraction du PDF local `assets/documents/statuts-2020.pdf` : l’article 2 expose l’objet, le lien social et la mise en avant des compétences, expériences et savoir-faire ; l’article 3 demande le partage des savoirs et précise les réalités territoriales ; les articles 11.8 et 11.9 parlent de synthèses en mots courants, de compréhension et des étapes du travail participatif. Le lien PDF reste visible.
- **Changements :** `index.html` remplace le résumé de la mission et la carte latérale par une présentation à mots simples, deux accès aux ressources, puis trois cartes « Partir de ce que nous vivons », « Mettre les savoirs en commun » et « Rendre les propositions compréhensibles ». `assets/css/site.css` borne la largeur du texte et réutilise les cartes existantes, qui se replient aux seuils mobiles. `outils/verifier-integration.py` contrôle la présence de la présentation, des trois rubriques et des liens.
- **Contrôles exécutés :** `python3 outils/verifier-site-statique.py` (83 pages), `python3 outils/verifier-integration.py` (nouveau contrôle du texte d’accueil et 16 routes API), `python3 outils/verifier-rd-continue.py` et `git diff --check` — réussis.
- **Limites :** c’est une rédaction du site fondée sur les statuts, pas la preuve d’une nouvelle décision collective de l’association. L’utilisateur a choisi la proposition ; aucune relecture indépendante par l’association, inspection navigateur ou validation par lecteur d’écran n’est revendiquée.
- **Prochaine action :** faire relire les formulations par l’association avant de les présenter comme une position collective ; vérifier le rendu de la page d’accueil sur téléphone et au clavier.

## 2026-10-14 — Orientation des flèches des panneaux Affichage et Présentation

- **Initiative :** `optimisation-du-site`.
- **Signal :** retour indiquant que les flèches décoratives restent fixes quand « Affichage » ou « Présentation » s’ouvre.
- **Diagnostic et correction :** les règles communes ne reliaient pas ces icônes à l’état natif `details[open]` ; de plus, les `span` en ligne doivent devenir transformables pour pivoter. Les chevrons sont maintenant `inline-block`, pivotent de 180° quand le panneau est ouvert et utilisent une transition courte. Le CSS généré du simulateur a été aligné, et la flèche « Parcours » reçoit également le comportement transformable déjà prévu.
- **Contrôles exécutés :** `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py` (83 pages), `python3 outils/verifier-integration.py` (dont les nouveaux contrôles CSS et les 16 routes API), `node --check assets/js/site.js` et `git diff --check` — tous réussis.
- **Limites :** aucun navigateur graphique n’est disponible ; ces assertions statiques ne confirment pas le rendu visuel sur smartphone. Une ouverture/fermeture réelle des panneaux reste à vérifier dans un navigateur.

## 2026-10-14 — Correction du panneau Affichage sur smartphone

- **Initiative :** `optimisation-du-site`.
- **Signal :** retour signalant que le panneau « Affichage » peut se décaler à gauche et devenir partiellement invisible sur smartphone, en particulier lorsque le zoom modifie la largeur CSS. L’inspection des règles confirme le risque : le panneau presque aussi large que le viewport était aligné à droite d’un bouton qui peut se trouver près du bord gauche.
- **Correction :** sous 760 px CSS, le bouton `details` cesse d’être le bloc de positionnement ; le panneau s’ancre au conteneur relatif de la barre, à gauche, garde une largeur bornée par le viewport et défile à l’intérieur si sa hauteur dépasse l’espace disponible. Le vérificateur d’intégration couvre explicitement cet ancrage et ces limites responsive.
- **Contrôles exécutés :** compilation Python ; vérificateurs R&D, apprentissages (70 fiches), simulateur, site statique (83 pages), sécurité et intégration (82 pages/fiches) ; `node --check` des scripts du site ; `git diff --check` — tous réussis. Le contrôle d’intégration confirme en particulier l’ancrage et la largeur du panneau mobile.
- **Limites :** le correctif est fondé sur les règles CSS et contrôles statiques ; il ne constitue pas une inspection dans un navigateur mobile. Après publication, vérifier l’ouverture du panneau sur un appareil réel, aux largeurs 320–430 px, en orientation paysage et avec zoom élevé.

## 2026-10-14 — Présentations personnalisables et Panorama composite

- **Initiative :** `optimisation-du-site`.
- **Signal et périmètre :** demande d’ajouter dans la barre supérieure une commande repliable permettant de choisir une présentation CSS sur tout le site et dans le simulateur. La précision « Panorama composite » a été retenue pour le troisième choix ; les contenus, fonctions et ordre de lecture restent inchangés. En l’absence de préférence enregistrée, « Équilibrée » reste la base afin de préserver la présentation existante ; le choix est réversible.
- **Décisions et changements :** `assets/js/site.js` ajoute le panneau natif « Présentation », ses choix radio nommés, une annonce d’état, la remise à zéro, l’application immédiate, la fermeture à Échap/au clic extérieur et la coordination avec les autres panneaux. `assets/css/site.css` applique les compositions « Lecture » et « Panorama composite » aux pages publiques et aux fiches. `outils/construire-simulateur.py` étend le même choix au simulateur autonome, régénéré dans `simulateur/index.html`. La préférence `mrsc-mise-en-page` reste locale ; elle se partage avec le simulateur intégré seulement à même origine. Le parent répercute directement dans cette iframe les classes de texte, contraste, espacement et mise en page, même si le stockage est bloqué ; la copie détecte le bandeau parent et masque ses réglages redondants. Aucun envoi serveur ni dépendance n’est ajouté.
- **Documentation et garde-fous :** notice de confidentialité, dossier `docs/rd-affichage-adaptatif.md`, portefeuille et `outils/verifier-integration.py` actualisés. Le vérificateur couvre l’inclusion des scripts/styles communs sur 82 pages/fiches et les contrôles déclarés des trois présentations. Le statut de l’initiative reste `a-tester` jusqu’à une revue du rendu et des interactions par une personne.
- **Contrôles locaux réellement exécutés :** générateur du simulateur puis `--verifier`; `py_compile` de `simulateur/*.py`, `api/*.py`, `outils/*.py`; `verifier-rd-continue.py`; générateur d’apprentissages en mode vérification; `verifier-site-statique.py`; `verifier-securite.py`; `verifier-integration.py`; `node --check` des scripts du site; `git diff --check` — réussis. Des harnais DOM ponctuels sous Node ont exercé sur le site la sélection en direct, la mémorisation/réinitialisation, Échap et le repli si `localStorage` est bloqué ; sur le simulateur, la sélection, la mémorisation/réinitialisation et le masquage des contrôles redondants lorsque l’iframe de même origine détecte le bandeau parent. Un harnais complémentaire a vérifié que la page parente répercute les classes de texte, contraste, espacement et le mode de présentation dans l’iframe de même origine même lorsque `localStorage` est bloqué, et n’intervient pas dans une iframe inter-origines.
- **Limites et suite :** pas de moteur de navigateur disponible, donc aucun rendu visuel, essai clavier réel, zoom, appareil tactile, lecteur d’écran ou usage par des personnes n’est revendiqué. Après publication, examiner à 320 px, en zoom élevé, en paysage, avec stockage bloqué et sur les principales familles de pages ; conserver l’état `a-tester` jusqu’à ces contrôles.

## 2026-10-14 — Remédiation CI et diagnostic du domaine

- **Signal et périmètre :** demande de régler les problèmes restés ouverts après le tour R&D : avertissements des workflows GitHub Actions, raccordement de `www.mrsc.fr` et validations humaines. Aucun accès à la zone DNS ni relecteur humain n’a été fourni; ne pas modifier le domaine ou présenter une validation inexistante.
- **CI :** les manifestes officiels des actions épinglées indiquent Node.js 24 : `actions/checkout` v7.0.1 (`3d3c42e5aac5ba805825da76410c181273ba90b1`), `actions/setup-python` v7.0.0 (`5fda3b95a4ea91299a34e894583c3862153e4b97`), `actions/configure-pages` v6.0.0 (`45bfe0192ca1faeb007ade9deae92b16b8254a0d`) et `actions/deploy-pages` v5.0.1 (`368f82528645a54fb793d4d04e342629a3f51346`). `upload-pages-artifact` v5.0.0 est composite et appelle `upload-artifact` v7.0.0, dont le manifeste indique également Node.js 24. Les quatre workflows sont fixés à Ubuntu 24.04 afin d’éviter la bascule automatique du label `ubuntu-latest`; le test de sécurité vérifie ce choix.
- **Autre échec réel décelé pendant les contrôles :** `construire-apprentissages.py --verifier` comparait une sortie suivie qui contenait `date.today()`. Elle devenait donc périmée dès le lendemain. La source TOML déclare maintenant `date_plan`; le générateur valide cette date et l’emploie pour produire une sortie stable. `docs/apprentissage/objectif-1000.md` suit maintenant `date_plan = 2026-10-14`, en accord avec son rafraîchissement de publication par le PR #29; les vérifications réussissent et la date ne dépend plus du jour d’exécution.
- **Domaine :** le résolveur système renvoie actuellement l’IPv4 `213.186.33.50` pour `www.mrsc.fr` et `mrsc.fr`. L’API Pages indique `cname: null`, l’adresse publiée reste `https://thejmimiia-code.github.io/MRSC/` et HTTPS est activé pour cette adresse GitHub Pages. Ne pas encore déclarer le domaine personnalisé ni changer canoniques/sitemap : l’initiative `raccordement-domaine-www` est `bloquee` jusqu’au CNAME `www → thejmimiia-code.github.io` posé par l’administrateur DNS et vérifié après propagation.
- **Contrôles locaux exécutés :** compilation Python; `verifier-rd-continue.py` (12 initiatives); générateurs d’apprentissage et du simulateur en mode vérification; vérificateur statique (83 pages, 70 fiches et 82 URL de sitemap); tests de sécurité ciblés, y compris l’épingle Ubuntu 24.04; intégration (16 routes API); `node --check` sur les deux scripts JavaScript; `git diff --check` — réussis. Les premiers contrôles GitHub de la PR #30 ont échoué sur le fichier généré `docs/apprentissage/objectif-1000.md`. La cause a été identifiée : pendant le travail, `main` a avancé avec le PR #29, qui a rafraîchi ce fichier à la date du 14 octobre; la branche de travail contenait encore la date source du 13. Ce n’était pas une différence de Python 3.11/3.12. La branche courante a ensuite intégré le nouveau `main` (`a1049e8`), la date de source `date_plan` a été alignée sur le 14 octobre et reste stable entre deux révisions explicites. Le vérificateur affiche maintenant les différences dans les annotations GitHub. Après fusion du PR #30 (`ca994bc`), le contrôle qualité (`38553659447`), la veille (`38553659684`) et Pages (`38553659541`) ont tous réussi. Les trois jobs utilisaient `ubuntu-24.04` et aucun n’a produit d’annotation. Les PR Dependabot redondants #11, #13, #14 et #15 ont été fermés; le #12 était déjà fermé. Le workflow Pages confirme la publication, mais aucune vérification manuelle du rendu dans un navigateur externe n’a été faite.
- **Limites et suite :** aucune relecture humaine des textes ou sources externes n’a eu lieu; une personne de l’association et les rôles compétents doivent encore relire. Les contrôles CI et Pages du PR #30 ont réussi le 14 octobre; maintenir les SHA complets et tester Ubuntu 26 séparément avant de changer le runner. L’administrateur DNS doit ensuite effectuer le CNAME; seulement après, configurer Pages/HTTPS, harmoniser les URL et vérifier dans un navigateur que `www.mrsc.fr` reste dans la barre d’adresse.

## 2026-10-13 — Tour R&D de cohérence des textes publics

- **Initiative :** `coherence-textes-publics`, liée à `optimisation-du-site`, `veille-savoirs-evolutifs` et `indexation-et-lecteurs-de-contenu`.
- **Signal et périmètre :** demande de conduire un cycle R&D complet avec brainstorming, vérifier la cohérence des textes du site et optimiser sans inventer de faits ni de validations. Revue des affirmations transversales des pages, des générateurs, de 70 fiches, du simulateur, du README, des documents et des règles R&D. Ce n’est pas une relecture scientifique ligne par ligne.
- **Constats confirmés :** `apprendre.html` disait « 26 fiches et 44 prototypes » sans préciser que la relecture indépendante des 26 fiches initiales n’est pas garantie ; le générateur clarifie maintenant les 70 entrées et les statuts. Le README présentait encore tous les PDF comme dépendants de leurs hébergeurs, alors que les statuts et bulletins sont copiés localement et que seul le document du Journal officiel est un lien externe. Le README appelait `github.io` une adresse durable alors que l’objectif déclaré est `www.mrsc.fr`.
- **Simulateur et hébergement :** les deux registres contrôlés comptent 101 leviers, 52 indicateurs et 11 scénarios. La copie du site est à `99491d8`, copiée le 8 octobre ; la tête GitHub amont consultée le 13 octobre est `4b15284892114235bc1e16a0e8cb2c801de9a115`, avec les mêmes comptes. Le patch local ne passe ni `git apply --check` ni la vérification inverse sur cette tête ; aucun moteur n’a été remplacé. La configuration GitHub Pages renvoie `cname: null` et 82 canoniques pointent vers `github.io`. Le DNS, le certificat, Render et les réponses de production n’ont pas été testés.
- **Décisions :** conserver « plus de 100 » pour le résumé, montrer révision/date de copie et avertir que les versions peuvent différer ; ne pas synchroniser le moteur avant revue du patch ; garder les notes d’audit datées sans les réécrire ; ne pas changer CNAME/canonicals avant confirmation DNS/HTTPS par l’administrateur ; conserver `www.mrsc.fr` dans la barre d’adresse, sans redirection.
- **Brainstorming et plan :** comparaison de la réécriture générale, d’un registre central des affirmations, de comptes exacts versus fourchettes, d’une distinction local/externe, d’une mise à jour amont immédiate et d’un changement immédiat des canoniques. Décisions détaillées, bénéfices/risques et priorités consignés dans le [plan global](../rd-plan-global-consolidation.md) et le [rapport de cohérence](rapport-coherence-editoriale-2026-10-13.md).
- **Changements :** `outils/construire-apprentissages.py` et sorties régénérées ; `anglais-aventure.html`, `transparence.html`, `simulateur.html`, `README.md` ; garde-fous dans `outils/verifier-site-statique.py` et `outils/verifier-integration.py` ; règle éditoriale dans `docs/rd-coherence-visuelle-editoriale.md` ; nouvelle initiative et revue datée dans `docs/rd/portefeuille.toml`.
- **Contrôles réellement exécutés :** compilation Python ; `verifier-rd-continue.py` ; vérificateurs des générateurs d’apprentissage et du simulateur ; `verifier-site-statique.py` (83 pages, 70 fiches, 82 URL de sitemap) ; `verifier-securite.py` (60 contrôles ciblés) ; `verifier-integration.py` (tous les contrôles, dont les 16 routes locales) ; `node --check` pour `site.js` et `navigation-parcours.js` ; `git diff --check` — tous réussis après les corrections. Le premier contrôle du générateur avait seulement détecté la sortie attendue à régénérer ; un premier contrôle statique puis d’intégration a aussi permis d’ajuster les assertions au nouveau texte. Les séries finales ont toutes réussi.
- **Intégration et publication :** le PR #27 a été fusionné (`4bd6cba`). Les workflows de vérification (run `38461428394`), de veille éditoriale (`38461428457`) et de publication Pages (`38461428409`) ont réussi ; le job de déploiement GitHub Pages s’est terminé avec succès. Le workflow a émis des avertissements non bloquants : certaines actions ciblent Node.js 20, forcé sous Node.js 24, et `ubuntu-latest` doit migrer vers Ubuntu 26 le 19 octobre 2026.
- **Limites :** aucune relecture par une personne de l’association, experte de domaine ou apprenante ; aucun audit individuel de toutes les sources externes, visite du site publié dans un navigateur réel ou essai d’accessibilité. Le DNS et le certificat `www.mrsc.fr`, ainsi que le service Render, n’ont pas été testés. Le succès du workflow confirme la publication GitHub Pages, pas les réponses visibles dans tous les navigateurs. Les tests vérifient la cohérence technique des éléments déclarés, pas leur exactitude scientifique ou leur compréhension par les visiteurs.
- **Prochaine action :** faire relire les nouvelles formulations par l’association ; traiter les avertissements de la chaîne CI avant la migration du 19 octobre ; confirmer séparément CNAME/DNS/HTTPS du domaine ; puis examiner le patch du simulateur et ses tests avant toute mise à jour amont.

## 2026-10-13 — Indexabilité et repères pour les lecteurs automatiques

- **Initiative :** `indexation-et-lecteurs-de-contenu`.
- **Signal et audit :** demande d’améliorer la découverte des pages par les moteurs et les outils de lecture, sans promettre leur indexation ou leur classement. Le sitemap généré comprend 82 URL publiques et le vérificateur en confirme la couverture ; il n’a pas de `lastmod`, car aucune date fiable n’est générée. L’inventaire initial de 81 pages HTML (sans l’interface autonome du simulateur) trouvait titres et descriptions uniques, mais sept canoniques manquantes ; `simulateur/index.html` n’avait ni description ni canonique. La page 404 est `noindex` et hors sitemap. **À l’audit**, le dépôt n’avait ni `robots.txt` ni `llms.txt` : le second est créé par la décision ci-dessous, le premier reste volontairement absent (voir « Hébergement et robots »).
- **Recherche externe :** [AnswerDotAI, « The /llms.txt file, v2 », Jeremy Howard](https://github.com/AnswerDotAI/llms-txt), publié le 2024-09-03, modifié le 2026-08-10 et consulté le 2026-10-13. Le dépôt présente ce format Markdown comme une proposition ouverte aux commentaires, permet un fichier sous un chemin de projet et décrit les URL de ce chemin. Cette source n’établit ni norme officielle d’indexation, ni effet sur le classement, ni taux d’utilisation ; aucun texte de la source n’a été repris.
- **Décision :** compléter les huit URL canoniques manquantes et décrire l’interface autonome dans sa source, puis vérifier que les canoniques correspondent au sitemap. Ajouter sur l’accueil un JSON-LD minimal `Organization` / `WebSite` / `WebPage`, limité aux noms, URL, langue, courriel et description déjà publics. Publier un `llms.txt` français concis, relié depuis l’accueil avec `rel="describedby"`, en signalant qu’il est facultatif et expérimental. Ne pas ajouter de directives `index,follow` redondantes, de dates `lastmod` inventées, de miroirs Markdown complets à maintenir en doublon, ni de mots-clés artificiels. Les 79 pages sans `og:title` relevées à l’audit n’ont pas été modifiées : les métadonnées Open Graph servent surtout aux aperçus de partage et ne résolvent pas le besoin principal.
- **Hébergement et robots :** ne pas ajouter de `robots.txt` dans ce dépôt pour GitHub Pages : le site canonique est un site-projet sous `/MRSC/`, tandis qu’un fichier placé dans le dépôt serait servi sous ce chemin et ne configurerait pas la racine de l’hôte. L’absence de directive `noindex` sur les pages publiques les laisse sans blocage HTML identifié ; la 404 conserve son `noindex`. Le domaine et le chemin éventuels de Vercel n’étant pas confirmés, une politique à la racine devra attendre cette vérification.
- **Changements et sources de vérité :** canoniques ajoutées à `ia-societe.html`, `simulateur.html`, `documents.html`, `liens-utiles.html`, `localisation.html`, `nous-contacter.html` et `transparence.html`; description et canonique du simulateur dans `simulateur/interface.py`, puis sortie régénérée dans `simulateur/index.html`. Graphe JSON-LD, relation `describedby` et contrôle de l’accueil dans `index.html`. Nouveau `llms.txt`, ajouté à la liste de publication GitHub Pages et à l’allowlist du serveur local ; contrôle hors ligne des titres, descriptions, canoniques, JSON-LD, sitemap et liens Markdown dans `outils/verifier-site-statique.py`, ainsi que contrôles de publication et de réponse texte dans `outils/verifier-integration.py` et `outils/verifier-securite.py`. Initiative suivie dans `docs/rd/portefeuille.toml`.
- **Contrôles réellement exécutés :** `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`, `python3 outils/verifier-rd-continue.py`, `python3 outils/construire-apprentissages.py --verifier`, `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-integration.py`, `node --check assets/js/site.js`, `node --check assets/js/navigation-parcours.js` et `git diff --check` — réussis. Le contrôle statique confirme 82 pages avec titres, descriptions et canoniques uniques, 82 URL dans le sitemap et 14 liens internes valides dans `llms.txt`. Le serveur local répond aussi en `text/plain` pour ce fichier.
- **Limites :** aucun moteur de recherche ni outil webmaster, site publié, crawler, navigateur graphique ou personne volontaire n’a été consulté pour cette tâche. Les contrôles prouvent la cohérence des fichiers et la réponse du serveur local, pas une indexation, un classement, une reprise par un assistant, une validation visuelle ou une validation humaine du contenu. Aucun service tiers ni suivi n’a été ajouté.
- **Prochaine action :** après publication, faire vérifier par la personne qui administre le domaine le sitemap, quelques canoniques et les erreurs d’exploration dans les outils pour webmasters choisis ; confirmer d’abord le domaine d’hébergement avant d’envisager un `robots.txt` à la racine.

## 2026-10-13 — Accueil simplifié et espace de suivi pour ÉVA

- **Initiative :** `documentation-rd-eva`, liée à `optimisation-du-site`.
- **Signal :** le texte « Faire société à partir de ce que chacune et chacun apporte » a été jugé peu compréhensible. Demande d’employer des mots directs et de rendre visible le suivi continu du projet ÉVA. Le document Drive « Pour l’accueil du site du M.R.S.C » propose une piste de rédaction plus longue.
- **Décision :** remplacer l’accroche abstraite et plusieurs textes de présentation par des phrases concrètes sur les ressources et les actions disponibles. Ajouter après la mission une section identifiée « Recherche et développement · ÉVA », avec un statut de recherche en cours et un engagement à distinguer objectifs, essais, résultats et limites. Le brouillon Drive est traité comme une proposition éditoriale, pas comme une preuve des capacités techniques d’ÉVA ; aucune fonction, mesure ni performance n’est annoncée.
- **Changements et sources :** introduction, textes d’accueil et métadonnées dans `index.html` ; ligne de traçabilité renvoyant à `index.html#rd-eva` dans `transparence.html` ; règles de clarté et de statut dans `docs/rd-coherence-visuelle-editoriale.md` ; nouvelle initiative `documentation-rd-eva` dans `docs/rd/portefeuille.toml` ; assertions de l’accueil et du registre dans `outils/verifier-integration.py`.
- **Contrôles réellement exécutés :** `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`, `python3 outils/verifier-rd-continue.py`, `python3 outils/construire-apprentissages.py --verifier`, `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-integration.py`, `node --check assets/js/site.js`, `node --check assets/js/navigation-parcours.js` et `git diff --check` — tous réussis. Le registre compte désormais 9 initiatives ; l’intégration confirme la présence et le statut prudent de la rubrique ÉVA.
- **Limites :** aucun rapport d’essai, dépôt technique ou mesure de performance d’ÉVA n’a été consulté ici ; seuls le signal de la personne et le brouillon Drive ont servi à formuler la présentation générale. La page et le vocabulaire n’ont pas été relus par des visiteurs ; aucun contrôle dans un navigateur graphique, au clavier réel ou avec un lecteur d’écran n’a été fait.
- **Prochaine action :** recueillir auprès de l’équipe ÉVA les éléments techniques publiables (objectifs validés, essais datés, versions, résultats, échecs, limites, sources et droits), puis compléter la rubrique sans annoncer de fonction non démontrée.

## 2026-10-13 — Harmonisation visuelle des commandes du bandeau

- **Initiative :** `optimisation-du-site`.
- **Signal :** la barre « Menu / Réduire / Parcours / Affichage » a été signalée comme visuellement dispersée et peu cohérente avec l’identité générale du site.
- **Décision :** préserver l’ordre, les libellés, les commandes et le repli existants ; lorsque les liens principaux sont repliés, réunir les commandes visibles en un groupe centré. Uniformiser leur hauteur minimale (44 px), bord, rayon, fond discret, typographie, espacements et accent d’état doré. Ne pas confondre ce réglage avec une refonte globale de la navigation ni masquer de libellé.
- **Changements et sources :** `assets/css/site.css` uniformise Menu, Réduire/Agrandir, Parcours et Affichage aux différents breakpoints ; `outils/verifier-integration.py` verrouille cette cohérence statique. `docs/rd-affichage-adaptatif.md`, `docs/rd-coherence-visuelle-editoriale.md` et le portefeuille décrivent le résultat et gardent la revue humaine à faire.
- **Contrôles réellement exécutés :** `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`, `python3 outils/verifier-rd-continue.py`, `python3 outils/construire-apprentissages.py --verifier`, `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-integration.py`, `node --check assets/js/site.js` et `git diff --check` — tous réussis. L’intégration contrôle 83 pages, 16 routes et les styles de la barre. Un premier lancement a échoué parce qu’une assertion CSS attendait l’ancien padding ; l’attendu a été aligné sur les nouvelles valeurs, puis l’intégration complète a réussi.
- **Limites :** aucune capture ou inspection par navigateur graphique n’a été faite dans l’environnement ; aucun essai clavier, tactile, lecteur d’écran ou zoom sur appareil réel ne confirme la hiérarchie visuelle effective. Les assertions d’intégration vérifient les règles présentes, pas leur rendu humain.
- **Prochaine action :** contrôler la barre sur un navigateur réel aux largeurs étroites et larges, puis à 50/100/125/150 %, et vérifier l’alignement, l’ordre de focus, le contraste des états et les retours à la ligne avant de modifier le statut `a-tester`.

## 2026-10-13 — Paliers de texte 50–150 % et navigation stable à fort agrandissement

- **Initiative :** `optimisation-du-site`.
- **Signal :** demande d’abaisser le réglage « Affichage » à 50 % pour montrer davantage de contenu et observation d’une barre de navigation qui s’empile et prend plus de place à 150 %.
- **Décision :** garder le réglage comme échelle CSS du texte, distincte du zoom natif du navigateur ; proposer cinq niveaux 50/75/100/125/150 %, enregistrés en pourcentage. Interpréter les anciennes valeurs indexées 0/1/2 comme 100/125/150 % et conserver la préférence binaire précédente à 125 %. À 125/150 %, replier la navigation de bureau dans la bascule Menu existante, conserver tous les libellés et plafonner la croissance des commandes ; les cibles tactiles restent au moins 44 px.
- **Changements et sources :** `assets/js/site.js` gère les niveaux, limites et migrations ; `assets/css/site.css` applique les échelles, stabilise le bandeau et le panneau Affichage et active le reflow du menu ; `outils/construire-simulateur.py` applique la même logique à la version autonome, régénérée dans `simulateur/index.html`. Les contrôles d’intégration et les matrices de `docs/rd-affichage-adaptatif.md` et `docs/rd-plan-global-consolidation.md` couvrent désormais ces états ; le portefeuille garde l’initiative `a-tester`.
- **Contrôles réellement exécutés :** `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`, `python3 outils/verifier-rd-continue.py`, `python3 outils/construire-apprentissages.py --verifier`, `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-integration.py`, `node --check assets/js/site.js` et `git diff --check` — réussis. La génération `python3 outils/construire-simulateur.py` a aussi été exécutée. Un harnais ponctuel Node/VM sans bibliothèque DOM a vérifié, pour le site et le simulateur, les niveaux par défaut, les paliers 50/75/100/125/150, les anciennes valeurs, les limites A−/A+, la mémorisation et le repli quand le stockage est bloqué ; un premier oracle du harnais avait une attente erronée sur A− à 150 %, corrigée avant la réussite.
- **Limites :** aucun navigateur graphique n’est disponible ici ; pas de rendu/mesure responsive, inspection visuelle, essai tactile/clavier réel, lecteur d’écran, utilisateur volontaire ni zoom natif du navigateur n’a été contrôlé. Les tests statiques et le harnais DOM simulé ne valident pas la mise en page effective ni la conformité WCAG.
- **Prochaine action :** vérifier visuellement et au clavier sur un navigateur réel les pages représentatives à 320/375/768/1024/1260/1440 px, à chaque niveau de texte et avec le zoom natif indépendant ; inspecter la bascule Menu à 125/150 %, les panneaux concurrents, les cibles tactiles et le simulateur autonome avant de changer l’état de l’initiative.

## 2026-10-13 — Commandes du parcours regroupées dans une bascule

- **Initiative :** `optimisation-du-site`.
- **Demande et hypothèse :** regrouper Précédent, Suivant, Accueil et Dernière vue derrière une seule commande dans la barre commune, afin que les quatre actions restent disponibles à la demande sans occuper constamment la zone de lecture.
- **Décision :** employer un `<details>` natif nommé « Parcours », fermé par défaut, et laisser les quatre boutons existants et leur logique d’historique dans son panneau. À Échap, le panneau se ferme et le focus revient à la bascule ; clic extérieur, Menu, Affichage ou réduction de l’en-tête le ferment aussi. La sortie du simulateur autonome reçoit le même contrôle ; une iframe dans une page ayant l’en-tête commun ne duplique pas ces commandes. Cette décision remplace la barre sticky persistante et l’objection antérieure contre le repli ; la découvrabilité reste à éprouver.
- **Changements et sources :** construction DOM et coordination dans `assets/js/navigation-parcours.js` ; styles communs, tactiles, contrastes et flèche d’état dans `assets/css/site.css` ; habillage autonome dans `outils/construire-simulateur.py`, puis régénération de `simulateur/index.html`. L’événement de recalcul sticky devenu inutile a été retiré de `assets/js/site.js`. Assertions d’intégration actualisées dans `outils/verifier-integration.py` ; `docs/rd-affichage-adaptatif.md`, `docs/rd-coherence-visuelle-editoriale.md`, le plan global et le portefeuille décrivent la décision actuelle.
- **Contrôles réellement exécutés :** `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`, `python3 outils/verifier-rd-continue.py`, `python3 outils/construire-apprentissages.py --verifier`, `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-integration.py`, `node --check assets/js/site.js`, `node --check assets/js/navigation-parcours.js` et `git diff --check` — réussis. Deux harnais ponctuels Node avec DOM simulé ont aussi vérifié la bascule unique fermée par défaut, les quatre boutons, la coordination avec Menu/Affichage, la fermeture extérieure, Échap et le retour du focus, puis l’insertion autonome et l’absence de doublon dans l’iframe du site. L’aperçu local existant sur le port 4173 a répondu HTTP 200 pour l’accueil, le simulateur autonome et le script de navigation.
- **Limites :** aucun rendu ou calcul de mise en page dans un navigateur n’a été inspecté, aucune matrice responsive/axe n’a été relancée pour cette nouvelle présentation, et aucun essai visuel, lecteur d’écran ou utilisateur n’a eu lieu. Les harnais DOM et les réponses HTTP confirment des aspects techniques, pas l’utilisabilité ni la conformité WCAG. L’aperçu 4173 était déjà en cours d’exécution ; il n’a pas été redémarré.
- **Prochaine action :** faire vérifier visuellement et au clavier le bandeau, le panneau Parcours et sa position sur accueil, page d’information, fiche et simulateur, aux largeurs étroites et avec zoom/tactile ; tester la découvrabilité et le lecteur d’écran avant de changer l’état `a-tester`.

## 2026-10-13 — Contrôle Réduire/Agrandir de l’en-tête adaptatif

- **Initiative :** `optimisation-du-site`.
- **Demande et hypothèse :** ajouter entre Menu et Affichage un moyen de libérer de la hauteur sur téléphone, tout en gardant disponibles navigation, réglages et choix d’agrandissement.
- **Décision :** compacter automatiquement l’en-tête à 760 px CSS ou moins, ainsi qu’en paysage court (hauteur ≤ 560 px et largeur ≤ 920 px). Le bouton, visible quand le menu principal est replié, permet de basculer manuellement l’avis R&D et l’identité. Il annonce son état via `aria-expanded`, déplace le focus avant de masquer une zone qui le contient, ferme le menu si besoin et ne persiste pas de préférence. Sans JavaScript, le bouton reste caché et l’en-tête complet visible. Le parcours sticky recalcule son décalage lors du changement de hauteur.
- **Changements et sources :** règles communes dans `assets/css/site.css` ; interaction et breakpoint dans `assets/js/site.js` ; événement de recalcul dans `assets/js/navigation-parcours.js`. Le générateur `outils/construire-apprentissages.py` et ses 70 fiches générées, ainsi que les pages statiques concernées, portent les identifiants et le bouton. Les contrôles d’intégration/static couvrent ordre, présence, styles et comportement déclaré ; `docs/rd-affichage-adaptatif.md` et le portefeuille décrivent la portée et la suite.
- **Contrôles réellement exécutés :** compilation Python (`simulateur/*.py`, `api/*.py`, `outils/*.py`), `python3 outils/verifier-rd-continue.py`, `python3 outils/construire-apprentissages.py --verifier`, `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-integration.py`, `node --check` des deux scripts JavaScript et `git diff --check` — réussis. Un harnais DOM simulé ponctuel sous Node a vérifié l’état mobile initial, les libellés/états ARIA, la bascule manuelle et au breakpoint, la fermeture du menu, le transfert du focus et l’absence de persistance ; il ne constitue pas un test navigateur. Le premier contrôle d’intégration a signalé que sa liste de composants de marque ne reconnaissait pas le nouveau bouton ; l’allowlist et le contrôle du style ont été étendus, puis toute l’intégration a passé.
- **Limites :** aucun rendu navigateur, inspection visuelle, essai sur appareil réel, parcours clavier complet, technologie d’assistance ou essai avec des personnes n’a été fait pour cette modification. Les vérifications automatisées n’établissent pas la conformité WCAG ni l’utilisabilité réelle.
- **Prochaine action :** garder l’initiative `a-tester` et vérifier l’en-tête compactable à petit écran, en paysage court, avec zoom élevé, tactile et clavier/lecteur d’écran ; contrôler visuellement le positionnement sticky avant de changer son état.

## 2026-10-13 — Bibliothèque polyvalente de skills et curation contrôlée

- **Initiative :** `coordination-de-tous-les-agents`.
- **Demande :** conserver les méthodes réutilisables dans le dépôt et repérer de nouvelles compétences pour des tâches variées, sans import indiscriminé.
- **Décision :** la bibliothèque durable est `.agents/skills/` ; `orchestration-taches` est désormais le routeur à consulter en premier, puis l’agent n’active qu’un petit ensemble pertinent. Cette organisation est persistante dans le dépôt, pas une installation globale de l’assistant ni une promesse de couvrir chaque tâche.
- **Recherche externe :** les dépôts MIT [Matt Pocock `skills`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336) (commit `49dd158d1076134a641b33efb035946536778336`, 9 octobre 2026) et [Addy Osmani `agent-skills`](https://github.com/addyosmani/agent-skills/tree/1be8e34187e34647bb83adc3a1323b26ae6f6abe) (commit `1be8e34187e34647bb83adc3a1323b26ae6f6abe`, 10 octobre 2026) ont été examinés directement. Deux références choisies — TDD (skill et deux fichiers Markdown) et débogage (un fichier Markdown) — sont conservées sous leurs licences, commits, sources et empreintes. Leurs adaptateurs spécifiques, scripts et lots complets n’ont pas été importés ; les recommandations génériques qui ajoutent des dépendances ou bloquent tout test sans validation utilisateur sont encadrées par les cartes locales.
- **Compétences ajoutées :** `orchestration-taches`, `debugging-methodique`, `strategie-tests`, `revue-contradictoire`, `analyse-donnees-reproductible`, `documentation-technique` et `curation-skills-securisee`. Elles couvrent cadrage/routage, diagnostic, tests, contre-revue, données, documentation et chaîne de provenance des skills. Les dix cartes M.R.S.C. préexistantes et les références visuelles Claude Code restent en place.
- **Documentation :** mise à jour d’`AGENTS.md`, de l’index `.agents/skills/README.md`, du manuel R&D, du portefeuille et ajout de [`bibliotheque-skills.md`](bibliotheque-skills.md), avec sources, exclusions, périmètre et règle de maintenance.
- **Contrôles réellement exécutés :** `python3 outils/verifier-rd-continue.py` — réussi (17 skills partagés, 8 initiatives cohérentes) ; validation scriptée des frontmatters/sections des 17 cartes — réussie ; `sha256sum -c` sur les quatre dossiers importés — tous les fichiers OK ; comparaison binaire des six fichiers Addy/Matt aux commits épinglés — réussie ; inventaire des imports — aucun fichier exécutable ou binaire ; `git diff --check` — réussi. Le contenu amont comprend des exemples de commandes ; ils n’ont pas été exécutés. Aucun paquet ni dépendance n’a été installé.
- **Limites :** ces contrôles valident la structure et l’identité des fichiers, pas l’innocuité absolue d’instructions Markdown, la qualité pour chaque agent ou une couverture exhaustive de toutes les tâches. Aucun essai de relais par un second agent n’a été réalisé ; l’activation réelle d’outils spécifiques dépend de leur présence dans l’environnement.
- **Prochaine action :** lors de prochaines tâches, utiliser le routeur et noter les lacunes réelles ; ne créer une autre carte qu’après vérification du besoin et comparaison à l’index. Après intégration, demander à un autre agent d’essayer la passation et corriger les manques observés.

## 2026-10-13 — Skills Claude pour la direction artistique et le mouvement web

- **Initiative :** `direction-artistique-motion`.
- **Signal :** demande d'une identité visuelle plus ludique et distinctive, d'animations web et d'une impression de découverte lors des visites répétées, pour soutenir l'apprentissage. Ce souhait n'est pas traité comme une preuve de besoin général ni comme un effet pédagogique déjà observé.
- **Audit interne :** le site est principalement en HTML/CSS/JavaScript ; les règles de cohérence et d'adaptation existent déjà. `docs/pistes-visuelles-ia.html` compare trois pistes propres à la page IA, sans constituer une direction globale choisie.
- **Sources primaires consultées :** Anthropic `frontend-design` (Apache 2.0) pour la direction artistique et LottieFiles `motion-design` (MIT) pour les idées de mouvement ; en complément, Anthropic `algorithmic-art` et `webapp-testing`, Vercel `web-design-guidelines` et plusieurs candidats communautaires. Les licences, formats, commits épinglés, limites et motifs d’exclusion sont consignés dans [`visuel-motion.md`](visuel-motion.md).
- **Décision :** importer uniquement les deux skills les plus pertinents et auditables depuis des commits fixes. `frontend-design` est conservé tel quel comme méthode visuelle. Pour LottieFiles `motion-design`, conserver le fichier amont sans modification sous `UPSTREAM-SKILL.md`, mais faire de `SKILL.md` une entrée locale qui rappelle que les règles M.R.S.C. priment et que les recettes (notamment les couches ambiantes) sont facultatives. Vercel reste un lien d'audit possible, non copié. Les autres candidats sont écartés ou différés tant qu'ils sont hors pile, trop larges, réclament du code distant ou n'ont pas pu être audités.
- **Changements :** les deux snapshots, leurs licences, provenances et manifestes SHA-256 se trouvent sous `.claude/skills/frontend-design/` et `.claude/skills/motion-design/`. Ajout/mise à jour des cartes de méthode Claude Code et partagée, de la note de R&D, des preuves du portefeuille et de cette entrée. Aucun code public, style de production, média, paquet ou dépendance du site n'a changé ; aucun code de skill n'a été exécuté.
- **Contrôles réellement exécutés :** `python3 outils/verifier-rd-continue.py` — réussi (10 skills partagés, 8 initiatives cohérentes) ; `python3 outils/verifier-securite.py` — tous les tests ciblés passent ; `git diff --check` — réussi ; `sha256sum -c` sur les deux manifests — tous les fichiers OK ; comparaison binaire des fichiers amont avec les commits épinglés — réussie ; inventaire des fichiers et recherche statique de commandes/appels distants dans le contenu amont — aucun exécutable, binaire ni motif trouvé ; validation scriptée de `name`/`description` pour les trois entrées Claude Code — réussie. Le CLI Claude Code n'est pas disponible : `claude plugin validate` n'a pas été exécuté.
- **Limites :** deux références textuelles externes sont copiées sous licence, mais aucun installateur, script ni dépendance n'a été exécuté ou ajouté ; aucune maquette, capture ou animation créée ; pas d'inspection visuelle humaine, d'essai d'accessibilité avec des personnes, de test utilisateur ni de mesure d'apprentissage. Le gain de découverte et d'apprentissage reste une hypothèse. Les trois directions restent à concevoir et choisir.
- **Prochaine action :** préparer trois maquettes non publiées pour une surface pilote, les comparer avec le système actuel, puis demander au M.R.S.C. de sélectionner ou combiner une direction avant toute intégration. Prévoir une évaluation volontaire et sans télémétrie individuelle.

## 2026-10-12 — Mise en place du dispositif de R&D multi-agent

- **Initiative :** `coordination-de-tous-les-agents`.
- **Décision :** utiliser `AGENTS.md` comme consigne commune, des cartes de skills sous `.agents/skills/`, le manuel [`rd-innovation-continue.md`](../rd-innovation-continue.md), le portefeuille TOML et ce journal comme sources de passation.
- **Surface publique :** ajouter une présentation du processus dans `transparence.html#rd-innovation`, accessible depuis `anglais-aventure.html` et `apprendre.html`; les consignes et skills détaillés restent lisibles dans le dépôt GitHub.
- **Automatisation :** ajouter un vérificateur hors ligne, l'appeler dans la CI, le déploiement et la veille hebdomadaire. La veille peut afficher les échéances et mettre à jour l'issue de suivi; elle ne consulte pas les sources externes et ne modifie ni n'approuve un contenu.
- **Essais d’usage :** préparer [`protocole-essais-usage.md`](protocole-essais-usage.md) avec tâches, consentement à adapter, notes minimales, arrêt et méthode d'analyse. C'est un protocole à faire relire, pas un test humain déjà exécuté.
- **Contrôles réellement exécutés localement :** compilation Python; vérificateur R&D et du protocole; génération-vérification du catalogue; vérificateur statique; vérificateur d'intégration; vérificateur de sécurité; parsing YAML des workflows et du formulaire; vérification HTTP des pages publiques modifiées; `git diff --check`.
- **Limites :** aucun test de l'exécution réelle des workflows GitHub n'a été effectué sur cette branche; aucune recherche automatique externe, relecture experte des contenus, validation exhaustive des droits ou essai d'usage avec des personnes n'est revendiqué.
- **Prochaine action :** faire relire le protocole de consentement et les tâches par les rôles compétents avant tout recrutement; après intégration dans `main`, examiner la première exécution planifiée et vérifier que le résumé et l'issue sont lisibles.

## 2026-10-12 — Barre de parcours compacte et plan global de consolidation

- **Initiative :** `optimisation-du-site`.
- **Signal et périmètre :** demande d’alléger les commandes de pages visitées et de mieux intégrer leur barre à l’accueil et aux pages du site ; revue de structure du dépôt local pour distinguer améliorations partageables, sorties générées, copies d’hébergement et anciennes versions potentielles.
- **Décision de conception :** garder les quatre actions (Précédent, Suivant, Accueil, Dernière vue), aligner la barre secondaire sur la largeur de lecture, réduire les boutons à 38 px sur pointeur fin, conserver 44 px sur tactile/petit écran et raccourcir le statut. Sous 520 px, les symboles décoratifs sont masqués pour garder les libellés d’action visibles ; `aria-label` reste également explicite. Placer la barre après l’en-tête sticky afin que son décalage suive la hauteur de l’en-tête sans gonfler celle-ci. Le simulateur généré garde son thème sombre et reçoit les mêmes invariants d’usage.
- **Options écartées :** replier la barre dans un menu ajouterait une étape et diminuerait la découverte ; intégrer toutes les commandes au menu principal le surchargerait ; supprimer la navigation personnalisée ferait perdre Accueil et Dernière vue. Pas de nouveau stockage, de requête réseau, de télémétrie ou de dépendance.
- **Audit de doublons :** le plan [`rd-plan-global-consolidation.md`](../rd-plan-global-consolidation.md) cartographie les 12 pages racine, 70 fiches générées et la page générée du simulateur, ainsi que leurs sources et tests. La recherche de fichiers explicitement `old`/`backup`/`legacy` n’a pas trouvé de copie à retirer. Les sorties de fiches, le simulateur embarqué et le service distant ont des rôles distincts ; aucune suppression de ces voies n’a été faite. La centralisation future des fragments des pages statiques et le nettoyage CSS restent conditionnés à un générateur autonome, une preuve de code mort et des essais.
- **Changements :** styles du site et du simulateur ; libellés/status du composant partagé ; vérifications d’intégration ajoutées ; feuille d’adaptation visuelle, portefeuille et README mis à jour.
- **Contrôles exécutés :** `python3 -m py_compile simulateur/*.py api/*.py outils/*.py`, `python3 outils/verifier-rd-continue.py`, `python3 outils/construire-apprentissages.py --verifier`, `python3 outils/construire-simulateur.py --verifier`, `python3 outils/verifier-site-statique.py`, `python3 outils/verifier-securite.py`, `python3 outils/verifier-integration.py`, `node --check assets/js/navigation-parcours.js` et `git diff --check` — réussis.
- **Limites :** aucune observation dans un navigateur réel, aucun essai clavier/lecteur d’écran avec des personnes, aucune validation de l’hébergement Render/Vercel/GitHub Pages et aucune suppression d’ancienne version n’ont été revendiqués. Aucun navigateur graphique ou Playwright/Puppeteer n’est disponible dans l’environnement local.
- **Prochaine action :** tester l’accueil, une page d’information, une fiche et le simulateur à 320/375/768/1024/1440 px, zoom élevé, clavier, tactile, lecteur d’écran et stockage de session bloqué ; n’enregistrer que les problèmes utiles et ajuster avant de qualifier le rendu.

## 2026-10-12 — Vérification fonctionnelle transversale

- **Initiative :** `optimisation-du-site`.
- **Demande reprise :** s’assurer que les principales surfaces et interactions déjà présentes sont reliées et utilisables sans retirer de contenu.
- **Contrôles de dépôt relancés :** compilation Python, registre R&D, vérification des sorties apprentissages et simulateur, liens/ancres et syntaxe statique, sécurité, intégration et `git diff --check` — tous réussis. Le vérificateur d’intégration a exercé les 16 routes/API locales.
- **Essai HTTP local :** parcours des 83 pages publiques, puis des liens et ressources locales ; 270 routes distinctes ont répondu HTTP 200 sur l’aperçu local.
- **Essai DOM simulé, sans navigateur graphique :** réglages d’affichage, menu avec Échap, message de repli de navigation quand `sessionStorage` est bloqué, partage avec solution de copie, filtres des 70 fiches, ajout/retrait et filtre des fiches dans Les Mondes, fin d’une mission avec repli du rendu 3D, carte chargée seulement après action, choix de source du simulateur intégré et moteur/réglages du simulateur autonome. Les presets et scénarios ont été activés et vérifiés avec leur retour API et leur état `aria-pressed`.
- **Défaut corrigé :** la revue a trouvé deux groupes de cartes cliquables du simulateur (`scénarios` et `préréglages`) implémentés en `<div>`, non activables au clavier natif. La source locale et le patch versionné les produisent maintenant comme boutons avec état sélectionné annoncé ; `simulateur/index.html` a été régénéré et le contrôle d’intégration verrouille ce comportement.
- **Cohérence de l’offre :** la page de présentation annonçait 9 scénarios alors que `simulateur/dashboard.py` en expose 11. Le chiffre est corrigé et le vérificateur d’intégration compare maintenant la présentation à la source du moteur.
- **Décision :** conserver l’initiative `a-tester` et les voies de repli ; ne supprimer ni page, ni donnée, ni fonction. La vérification DOM ne mesure pas les styles, le rendu, l’accessibilité réelle ou l’usage.
- **Limites :** essais sur un environnement DOM simulé et le serveur local uniquement. Aucune validation visuelle, essai complet au clavier, lecteur d’écran, mesure de contraste, session avec volontaires, ni vérification de Render/Vercel/GitHub Pages en production.
- **Prochaine action :** revue humaine sur de vrais appareils selon la matrice déjà inscrite au plan ; traiter tout défaut reproductible puis seulement réviser l’état du portefeuille.

## 2026-10-12 — Contraste, défilement et clavier dans le simulateur

- **Initiative :** `optimisation-du-site`.
- **Signal :** un contrôle axe initial avait relevé 178 cibles de contraste et deux régions défilantes non accessibles au clavier dans la page du simulateur. La revue du rendu mobile a également trouvé un débordement à 320 px.
- **Corrections :** les couleurs secondaires ont été basculées vers les variables de texte du thème ; les titres de familles affichent le texte lisible avec un accent de bordure validé. Les sept vues dynamiques nomment leurs conteneurs de tableaux et les rendent focusables ; le journal causal devient une région annoncée. Les tableaux d’audit (sources, indicateurs, leviers et garde-fous) reçoivent chacun leur conteneur défilant, son nom accessible et son focus clavier. À 320 px, la grille de lecture passe en une colonne et les commandes longues des leviers se replient sans élargir la page.
- **Génération et provenance :** le patch local a été reconstruit à partir du commit amont `99491d872f1fb2716041aeb4733f5921359ec7c6`. `git apply --check` a réussi sur cette base ; après application, les modules Python concernés correspondaient aux sources locales. `simulateur/PROVENANCE.json` a reçu l’empreinte SHA-256 mise à jour et `simulateur/index.html` a été régénéré.
- **Contrôles réellement exécutés :** compilation des sources Python modifiées ; `python3 outils/construire-simulateur.py --verifier` ; `python3 outils/verifier-integration.py` (dont les 16 routes locales interrogées) ; navigateur Chromium sans interface via Puppeteer : 29 cas responsive, navigation précédente/suivante/accueil/dernière vue, focus visible, repli quand `sessionStorage` est bloqué, et 4 analyses axe (accueil, transparence, fiche et simulateur). Les 29 cas n’ont signalé aucun débordement ; les 4 pages n’ont signalé aucune violation axe. Sur le simulateur à 320 px, les sept onglets ont ensuite été parcourus : chaque région de tableau était nommée, focusable et sans débordement de page ; une séquence Tab / Maj+Tab a confirmé le focus clavier visible sur une région de résultats et une région d’audit. Les 36 régions de tableaux d’audit l’étaient aussi. Les analyses axe répétées pour chaque onglet et avec tous les détails d’audit ouverts n’ont rapporté aucune violation. Un parcours interactif distinct a sélectionné un scénario puis un préréglage, vérifié le rendu des résultats et le contenu du journal, puis confirmé la création des exports JSON et CSV sans erreur navigateur.
- **Limites :** ces résultats sont ceux de tests automatisés en Chromium sans interface ; ils ne constituent ni une inspection visuelle humaine ni un essai avec lecteur d’écran, ni une validation de Render, Vercel ou GitHub Pages. Aucun essai utilisateur n’a été fait.
- **Prochaine action :** faire relire le rendu à fort zoom et au lecteur d’écran sur appareils réels ; conserver les voies de repli et ne supprimer aucune ancienne version sans nouvel audit des usages.
