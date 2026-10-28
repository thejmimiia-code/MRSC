# Inventaire des contrôles du dépôt

**Document de travail, daté du 28 octobre 2026.** Il répond à une seule question, outil par outil : *qu'est-ce qui prouve que ce contrôle peut échouer ?* Un contrôle dont personne n'a jamais vu l'échec est une affirmation, pas une vérification — c'est la leçon tirée ce jour en écrivant `outils/test_mutations_affichages.py` puis `outils/test_mutations_site_statique.py`.

Ce document ne dit pas que les contrôles « sans test » sont faux. Il dit qu'on ne le sait pas encore, et il nomme le travail restant. Il est tenu par `outils/verifier-inventaire-controles.py`, qui échoue si un outil du dépôt n'y figure pas, si un test annoncé n'existe pas ou si un chemin cité a bougé — et dont le propre pouvoir de mordre est éprouvé par `outils/test_verifier_inventaire_controles.py`, cinq fautes plantées dans une copie du dépôt. Un inventaire qu'on peut oublier de mettre à jour ne vaut rien ; un garde d'inventaire qu'on croit sur parole ne vaut pas mieux.

## Comment lire la colonne « Statut »

| Statut | Ce qu'il veut dire | Ce qu'il ne veut pas dire |
| --- | --- | --- |
| `banc` | Un test casse réellement un fichier (dans une copie jetable ou un fichier temporaire) et exige l'échec **avec le message attendu**. | Que le contrôle couvre toutes les fautes possibles. |
| `faute-en-memoire` | Un test copie des données structurées, casse un champ ou une entrée, et exige le refus. | Que le fichier réel sur disque serait refusé : la lecture du fichier n'est pas éprouvée. |
| `test` | Un test existe, mais il n'injecte pas de faute : il vérifie un calcul, une structure ou un cas nominal. | Qu'il protège contre une régression de la règle gardée. |
| `test-en-soi` | Le fichier **est** le test : un script navigateur ou une simulation d'erreur, lancé par la CI. | Qu'un second test le protège : s'il cesse de mordre, seule sa lecture le dit. |
| `aucun-test` | Rien ne prouve que ce contrôle sait échouer. Il tourne en CI et il est vert. | Qu'il est inutile — seulement qu'il est cru sur parole. |
| `hors-portee` | Ce n'est pas un contrôle : générateur, aide partagée ou outil de développement. | Qu'il est dispensé de preuve : ses sorties sont vérifiées par `--verifier` et par `test_reproductibilite_artefacts.py`. |

## Inventaire

| Outil | Rôle | Garde actuelle | Statut |
| --- | --- | --- | --- |
| `outils/auditer-affichages.mjs` | Audit navigateur des formats d'affichage | Vert du job `graphismes` | `aucun-test` |
| `outils/auditer-criteres-22.mjs` | Comptage des critères WCAG 2.2 sur les pages | Vert du job `graphismes` et relevé JSON commité | `aucun-test` |
| `outils/auditer-prototypes.py` | 17 contrôles mécaniques par fiche | `test_audit_prototypes.py` (30 tests, données copiées puis cassées) | `faute-en-memoire` |
| `outils/banc_mutations.py` | Aides partagées des bancs de mutation | Aucune : module d'aide, sans sortie | `hors-portee` |
| `outils/confronter-sources.py` | Prototype de confrontation d'affirmations aux sources | `test_confronter_sources.py` (9 tests) | `faute-en-memoire` |
| `outils/construire-apprentissages.py` | Génère les fiches et le catalogue | `--verifier` plus `test_reproductibilite_artefacts.py` | `hors-portee` |
| `outils/construire-avancees.py` | Génère `avancees.md` depuis le registre | `test_avancees.py` (15 tests) | `faute-en-memoire` |
| `outils/construire-carte-lacunes.py` | Génère la carte des lacunes | `--verifier` plus `test_reproductibilite_artefacts.py` | `hors-portee` |
| `outils/construire-paquets-relecture.py` | Prépare les paquets de relecture | `--verifier` seul | `aucun-test` |
| `outils/construire-simulateur.py` | Génère `simulateur/index.html` | `--verifier` plus `verifier-integration.py` | `hors-portee` |
| `outils/construire-sources-refusees.py` | Registre des sources tentées et refusées | `test_sources_refusees.py` (10 tests) | `faute-en-memoire` |
| `outils/etat-rd.py` | Imprime l'état daté de la R&D | Aucune : sortie lue à la main | `aucun-test` |
| `outils/file-relecture.py` | Construit la file de relecture | `--verifier` seul | `aucun-test` |
| `outils/generer-fonctions-api.py` | Génère les fonctions Vercel de `api/` | `verifier-integration.py` | `hors-portee` |
| `outils/mettre-a-jour-simulateur.py` | Met à jour le moteur embarqué depuis l'amont | `verifier-maj-amont.py` | `hors-portee` |
| `outils/optimiser-images.py` | Variantes AVIF/WebP des grandes illustrations | `test_manifeste_sans_imagemagick.py` (6 tests) et `--verifier` | `test` |
| `outils/registre-relecture.py` | Registre des relectures humaines | `test_registre_relecture.py` (14 tests) | `faute-en-memoire` |
| `outils/serveur-local.py` | Serveur local qui imite Vercel et GitHub Pages | Aucune : outil de développement | `hors-portee` |
| `outils/statuts_editoriaux.py` | Définitions partagées des statuts | Aucune : module d'aide | `hors-portee` |
| `outils/test-cache-css-ia.cjs` | Simule un CSS périmé servi sous l'ancienne URL | Il est lui-même le test ; mutation intégrée | `test-en-soi` |
| `outils/test-experience.cjs` | 8 essais navigateur du panneau et du menu | Il est lui-même le test | `test-en-soi` |
| `outils/verifier-accessibilite.cjs` | Audit axe des pages, lancé dans le job navigateur | Vert du job `graphismes` | `aucun-test` |
| `outils/verifier-affichages.py` | 16 garde-fous de format et d'impression | `test_mutations_affichages.py` (5 mutations) | `banc` |
| `outils/verifier-budgets-visuels.py` | Budgets d'affichage des titres | Vert de CI seulement | `aucun-test` |
| `outils/verifier-decision-prospective.py` | Faits internes du brief prospectif | `test_verifier_decision_prospective.py` (20 tests) | `test` |
| `outils/verifier-fiches-statistiques.cjs` | Géométrie des deux fiches de statistiques | Vert du job `graphismes` | `aucun-test` |
| `outils/verifier-fichiers-servis.py` | Relevé d'en-têtes confronté aux fichiers | `test_fichiers_servis.py` (28 tests) | `test` |
| `outils/verifier-fusions.py` | Fusion et suppression de branche sans perte | Vert de CI seulement | `aucun-test` |
| `outils/verifier-graphismes.cjs` | Mesure navigateur de trois visuels | Trois mutations internes (`distorsion`, `densite`, `ancre`) rejouées en CI | `test-en-soi` |
| `outils/verifier-integration.py` | Intégration du simulateur au site, sans navigateur | Vert de CI seulement | `aucun-test` |
| `outils/verifier-inventaire-controles.py` | Tient ce document : couverture, existence, vocabulaire des statuts | `test_verifier_inventaire_controles.py` (casse l'inventaire dans une copie) | `banc` |
| `outils/verifier-maj-amont.py` | Retard du moteur embarqué sur l'amont | Vert de CI seulement | `aucun-test` |
| `outils/verifier-planches-statuts.py` | Planches des statuts et leur archive | Vert de CI seulement | `aucun-test` |
| `outils/verifier-poids-pages.py` | Poids estimé des pages et budget de sobriété | Vert de CI seulement | `aucun-test` |
| `outils/verifier-publication-locale.py` | Le site publié ne manque d'aucun fichier | Vert de CI seulement | `aucun-test` |
| `outils/verifier-publication.py` | Ce que l'hébergement sert réellement | `test_verifier_publication.py` (5 tests) | `test` |
| `outils/verifier-rd-continue.py` | Consignes, skills et portefeuille R&D | Vert de CI seulement | `aucun-test` |
| `outils/verifier-resilience-statutaire.py` | Structure documentaire du registre statutaire | `test_verifier_resilience_statutaire.py` (19 tests) | `faute-en-memoire` |
| `outils/verifier-securite.py` | Frontières de sécurité du simulateur | Vert de CI seulement — **le plus surprenant de la liste** | `aucun-test` |
| `outils/verifier-separation-contenus.py` | Empêche le retour des contenus personnels | `test_separation_contenus.py` (11 tests) | `test` |
| `outils/verifier-site-statique.py` | 99 pages, liens, ancres, canoniques, sitemap | `test_mutations_site_statique.py` (5 mutations) | `banc` |
| `outils/verifier-source-distante.py` | Utilisabilité de la version en ligne du simulateur | Aucune : demande le réseau | `aucun-test` |
| `outils/verifier-taux-dates.py` | Une règle chiffrée porte sa date | `test_verifier_taux_dates.py` (14 tests, catalogue temporaire muté) | `banc` |
| `outils/verifier-vote-distanciel.py` | Garde-fous documentaires du vote distanciel | `test_verifier_vote_distanciel.py` (86 tests) | `faute-en-memoire` |
| `outils/versionner-css-ia.py` | Lie la page IA au contenu exact du CSS | `test_version_css_ia.py` (2 tests) | `test` |

## Ce que l'inventaire dit en clair

45 fichiers d'`outils/` (hors `test_*`), répartis ainsi :

- **Quatre** contrôles sont éprouvés en cassant réellement un fichier : les garde-fous d'affichage, la porte des pages statiques, la règle des taux datés, et ce contrôle-ci, qui casse l'inventaire dans une copie du dépôt.
- **Sept** le sont en cassant des données en mémoire. C'est utile, mais la lecture du fichier sur disque n'est pas éprouvée : un `registre-relecture.py` qui lirait le mauvais fichier resterait vert sur ces tests.
- **Six** ont un test qui n'injecte aucune faute.
- **Trois** sont eux-mêmes des tests (scripts navigateur, simulation de cache) : leur échec est visible, mais rien ne vérifie qu'ils continuent de mordre.
- **Dix-sept** ne sont prouvés par rien d'autre que leur vert quotidien.
- **Huit** ne sont pas des contrôles (générateurs, aides partagées, serveur local) : ils relèvent de `--verifier` et de `test_reproductibilite_artefacts.py`.

Autrement dit : **17 contrôles sur 37** s'appuient sur un test capable d'échouer. Les 20 autres n'ont aucune preuve de ce genre : trois *sont* des tests, et dix-sept ne sont prouvés par rien d'autre que leur vert quotidien.

## Par où continuer, par ordre de rentabilité

1. `verifier-securite.py` — il garde les frontières HTTP, WSGI, la provenance navigateur et la liste statique du simulateur, et il n'a aucun test. C'est le décalage le plus fort entre l'enjeu et la preuve.
2. `verifier-fusions.py` — il garde la règle « ne rien perdre en fusionnant », et il tourne sur un journal de 137 entrées où une inversion d'ordre s'est déjà produite.
3. `verifier-publication-locale.py` et `verifier-integration.py` — deux portes à forte conséquence, vérifiées seulement par elles-mêmes.
4. `auditer-criteres-22.mjs` — il a déjà publié « 0 élément masqué » sans avoir rien pu charger ; ce défaut-là mérite un test qui le reproduit.

## Limites de ce document

- Les statuts viennent de la lecture des tests le 28 octobre 2026, pas d'une exécution de chaque mutation possible. `test` et `faute-en-memoire` sont des jugements sur ce que fait le test, pas des mesures.
- `verifier-securite.py` pourrait déjà contenir des assertions qui échouent si on retire une protection ; il n'a simplement pas de fichier de test dédié. Le classer `aucun-test` dit cela, pas qu'il est décoratif.
- L'inventaire ne juge pas l'utilité des contrôles, seulement l'existence d'une preuve qu'ils peuvent échouer.
