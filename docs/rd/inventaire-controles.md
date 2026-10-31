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
| `outils/auditer-affichages.mjs` | Audit navigateur des formats d'affichage | `test_auditer_affichages.mjs` (navigateur remplacé, périmètre réduit dans la copie ; 3 modes) | `faute-en-memoire` |
| `outils/auditer-criteres-22.mjs` | Comptage des critères WCAG 2.2 sur les pages | `test_auditer_criteres_22.mjs` (navigateur remplacé par deux faux ; 4 modes : nominal, échec total, échec partiel, défauts) | `faute-en-memoire` |
| `outils/auditer-prototypes.py` | 17 contrôles mécaniques par fiche | `test_audit_prototypes.py` (30 tests, données copiées puis cassées) | `faute-en-memoire` |
| `outils/banc_mutations.py` | Aides partagées des bancs de mutation | Aucune : module d'aide, sans sortie | `hors-portee` |
| `outils/compter-paliers.py` | Compte les paliers d'affichage et refuse ceux que personne n'a déclarés | `test_paliers_affichage.py` (20 cas : palier neuf, dette qui monte, dette qui descend, raison vide, courte ou en attente, décision inventée, deux écritures de la même condition, écriture non canonique, inscription orpheline, trois sources illisibles, écriture à travers un lien refusée, et la garde de copie) | `banc` |
| `outils/confronter-sources.py` | Prototype de confrontation d'affirmations aux sources | `test_confronter_sources.py` (9 tests) | `faute-en-memoire` |
| `outils/construire-apprentissages.py` | Génère les fiches et le catalogue | `--verifier` plus `test_reproductibilite_artefacts.py` | `hors-portee` |
| `outils/construire-avancees.py` | Génère `avancees.md` depuis le registre | `test_avancees.py` (15 tests) | `faute-en-memoire` |
| `outils/construire-carte-lacunes.py` | Génère la carte des lacunes | `--verifier` plus `test_reproductibilite_artefacts.py` | `hors-portee` |
| `outils/construire-paquets-relecture.py` | Prépare les paquets de relecture | `test_mutations_files_relecture.py` (même banc : les deux outils partagent le même tri) | `banc` |
| `outils/construire-simulateur.py` | Génère `simulateur/index.html` | `--verifier` plus `verifier-integration.py` | `hors-portee` |
| `outils/construire-sources-refusees.py` | Registre des sources tentées et refusées | `test_sources_refusees.py` (10 tests) | `faute-en-memoire` |
| `outils/etat-rd.py` | Imprime l'état daté de la R&D | `test_etat_rd.py` (7 cas : chaque source retirée ou cassée doit être nommée, code 1) | `banc` |
| `outils/file-relecture.py` | Construit la file de relecture | `test_mutations_files_relecture.py` (divergence, fichier supprimé, édition à la main, tri éprouvé sur une fiche ajoutée) | `banc` |
| `outils/generer-fonctions-api.py` | Génère les fonctions Vercel de `api/` | `verifier-integration.py` | `hors-portee` |
| `outils/modele-grilles.py` | Modèle des grilles : colonnes calculées largeur par largeur, et contrôle des grilles converties en `auto-fit` | `test_modele_grilles.py` (33 cas : grille revenue fixe, minimum de la feuille ou du registre qui ne suit plus la règle, palier ajouté après coup, sélecteur disparu, registre sans grille, deux sources illisibles en code 2, monotonicité de `auto-fit`, grille à pistes inégales déclarée non convertible, seuil de repli à deux colonnes, conversion annulée par une règle inégale, grille de quatre éléments qui interdit la troisième colonne, capacité qui borne le nombre de colonnes, `@media` vide qui ne décale pas la lecture, écart de grille à deux valeurs, capacité déclarée fausse, déclaration qui ne décide rien, colonnes égales écrites sans `minmax`, grille déclarée fixe devenue dynamique, grille fixe qui change de colonnes, lecture des pistes au premier niveau, piste `auto` non décidable, cascade qui compte les pistes inégales, écart en `clamp` évalué par largeur, rapport `flex` modifié, `flex-wrap` retiré, présentation qui réimpose une grille, écart de conversion recopié, déclaration de grille sur un conteneur flex, et la règle qui retrouve `k` colonnes pour cinq combinaisons) | `banc` |
| `outils/mettre-a-jour-simulateur.py` | Met à jour le moteur embarqué depuis l'amont | `verifier-maj-amont.py` | `hors-portee` |
| `outils/optimiser-images.py` | Variantes AVIF/WebP des grandes illustrations | `test_manifeste_sans_imagemagick.py` (6 tests) et `--verifier` | `test` |
| `outils/registre-relecture.py` | Registre des relectures humaines | `test_registre_relecture.py` (14 tests) | `faute-en-memoire` |
| `outils/serveur-local.py` | Serveur local qui imite Vercel et GitHub Pages | Aucune : outil de développement | `hors-portee` |
| `outils/statuts_editoriaux.py` | Définitions partagées des statuts | Aucune : module d'aide | `hors-portee` |
| `outils/test-cache-css-ia.cjs` | Simule un CSS périmé servi sous l'ancienne URL | `test_test_cache_css_ia.mjs` (5 cas : nominal, version périmée, attente inversée, interception retirée, ancien CSS identique) | `banc` |
| `outils/test-experience.cjs` | 10 essais navigateur du panneau, du menu, de la lecture vocale et de l'ancrage du panneau | `test_test_experience.mjs` (harnais seul : 10 échecs comptés et nommés, code de sortie, 3 mutations rejetées) · lancé par le job `graphismes` depuis le 29 octobre | `banc` |
| `outils/verifier-accessibilite.cjs` | Audit axe des pages, lancé dans le job navigateur | `test_verifier_accessibilite.mjs` (navigateur et axe remplacés ; 3 modes, chaque exécution doit avoir son verdict) | `faute-en-memoire` |
| `outils/verifier-affichages.py` | 16 garde-fous de format et d'impression | `test_mutations_affichages.py` (8 mutations, dont 4 sur le placement mesuré du panneau) · `test_placement_panneau.mjs` (3 600 positions, sans navigateur) | `banc` |
| `outils/verifier-budgets-visuels.py` | Budgets d'affichage des titres | `test_mutations_budgets_visuels.py` (3 fautes : titre long, page sans titre, H1 gonflé) | `banc` |
| `outils/verifier-decision-prospective.py` | Faits internes du brief prospectif | `test_verifier_decision_prospective.py` (20 tests) | `test` |
| `outils/verifier-fiches-statistiques.cjs` | Géométrie des deux fiches de statistiques | `test_verifier_fiches_statistiques.mjs` (navigateur remplacé ; 4 modes + relevé commité intact) | `faute-en-memoire` |
| `outils/annoncer-echec-graphismes.py` | Nomme en annotation ce que la mesure navigateur a refusé — les journaux et artefacts peuvent être hors d'atteinte | `test_annoncer_echec_graphismes.py` (5 cas : constats recopiés, relevé vide, dossier vide, JSON illisible, erreurs au-delà de six) | `banc` |
| `outils/verifier-fichiers-servis.py` | Relevé d'en-têtes confronté aux fichiers | `test_fichiers_servis.py` (28 tests) | `test` |
| `outils/verifier-fusions.py` | Fusion et suppression de branche sans perte | `test_mutations_fusions.py` (6 fautes dans de petits dépôts git neufs) | `banc` |
| `outils/verifier-graphismes.cjs` | Mesure navigateur de trois visuels | `test_mesure_graphismes.mjs` (3 pages de contrôle aux dimensions connues, nombres confrontés à l'arithmétique) · `verifier-mutation-graphismes.py` (les 3 mutations produisent l'erreur annoncée) | `banc` |
| `outils/verifier-integration.py` | Intégration du simulateur au site, sans navigateur | `test_mutations_integration.py` (3 fautes : ressource orpheline, chiffre annoncé, page absente) | `banc` |
| `outils/verifier-inventaire-controles.py` | Tient ce document : couverture, existence, vocabulaire des statuts | `test_verifier_inventaire_controles.py` (casse l'inventaire dans une copie) | `banc` |
| `outils/verifier-mutation-graphismes.py` | La mutation d'affichage a-t-elle fait dire au contrôle ce qu'elle devait ? | `test_verifier_mutation_graphismes.py` (6 cas, dont un qui relit les messages dans le script) | `banc` |
| `outils/verifier-maj-amont.py` | Retard du moteur embarqué sur l'amont | `test_verifier_maj_amont.py` (4 cas ; la provenance est lue dans une copie, la sonde réseau remplacée) | `faute-en-memoire` |
| `outils/verifier-planches-statuts.py` | Planches des statuts et leur archive | `test_mutations_planches_statuts.py` (6 fautes plantées, un dépôt illisible qui doit être dit, et 3 cas de vérification d'empreintes sur une archive restaurée) | `banc` |
| `outils/verifier-poids-pages.py` | Poids estimé des pages et budget de sobriété | `test_mutations_poids_pages.py` (4 fautes : image lourde, ressource absente, `<picture>` sans repli, budget à 1 Kio) | `banc` |
| `outils/verifier-publication-locale.py` | Le site publié ne manque d'aucun fichier | `test_mutations_publication_locale.py` (6 fautes : copie, lien, aperçu local, sitemap) | `banc` |
| `outils/verifier-publication.py` | Ce que l'hébergement sert réellement | `test_verifier_publication.py` (5 tests) | `test` |
| `outils/verifier-rd-continue.py` | Consignes, skills et portefeuille R&D | `test_mutations_rd_continue.py` (4 fautes : initiative, skill, ancre publique, veille) | `banc` |
| `outils/verifier-resilience-statutaire.py` | Structure documentaire du registre statutaire | `test_verifier_resilience_statutaire.py` (19 tests) | `faute-en-memoire` |
| `outils/verifier-securite.py` | Frontières de sécurité du simulateur | `test_mutations_securite.py` (6 mutations : en-tête, limite, action, runner, liste statique, plafond de source) | `banc` |
| `outils/verifier-separation-contenus.py` | Empêche le retour des contenus personnels | `test_separation_contenus.py` (11 tests) | `test` |
| `outils/verifier-site-statique.py` | 99 pages, liens, ancres, canoniques, sitemap | `test_mutations_site_statique.py` (5 mutations) | `banc` |
| `outils/verifier-source-distante.py` | Utilisabilité de la version en ligne du simulateur | `test_verifier_source_distante.py` (9 cas sur un serveur local réel : page, API, ordre des routes, hôte refusé, port fermé) | `banc` |
| `outils/verifier-taux-dates.py` | Une règle chiffrée porte sa date | `test_verifier_taux_dates.py` (14 tests, catalogue temporaire muté) | `banc` |
| `outils/verifier-vote-distanciel.py` | Garde-fous documentaires du vote distanciel | `test_verifier_vote_distanciel.py` (86 tests) | `faute-en-memoire` |
| `outils/versionner-css-ia.py` | Lie la page IA au contenu exact du CSS | `test_version_css_ia.py` (2 tests) | `test` |

## Ce que l'inventaire dit en clair

48 fichiers d'`outils/` (hors `test_*`), répartis ainsi :

- **Vingt-deux** contrôles sont éprouvés en cassant réellement quelque chose : les garde-fous d'affichage, la porte des pages statiques, la règle des taux datés, les frontières de sécurité, la règle « ne rien perdre en fusionnant », la porte de publication, la porte d'intégration, la continuité R&D, le budget de poids, les budgets d'affichage, les deux outils de la file de relecture, les planches des statuts, l'état daté de la R&D, la vérification de la source distante, le contrôle des mutations d'affichage, le test du cache CSS, le harnais des essais navigateur, la mesure des graphismes et ce contrôle-ci, qui casse l'inventaire dans une copie du dépôt.
- **Douze** le sont en cassant des données en mémoire ou en simulant ce qui ne peut pas être joint. C'est utile, mais la lecture du fichier sur disque, ou la sonde réseau, n'est pas éprouvée : un `registre-relecture.py` qui lirait le mauvais fichier resterait vert sur ces tests ; `verifier-maj-amont.py` n'interroge jamais réellement l'amont ; et les quatre scripts navigateur (`auditer-criteres-22.mjs`, `verifier-fiches-statistiques.cjs`, `verifier-accessibilite.cjs`, `auditer-affichages.mjs`) ne voient jamais un vrai Chromium — leurs bancs éprouvent ce qu'ils font de mesures qu'on leur donne, pas la justesse de ce qu'ils mesurent.
- **Six** ont un test qui n'injecte aucune faute.
- **Aucun** n'est réduit à son propre témoignage.
- **Aucun** n'est réduit à son seul vert quotidien.
- **Huit** ne sont pas des contrôles (générateurs, aides partagées, serveur local) : ils relèvent de `--verifier` et de `test_reproductibilite_artefacts.py`.

Autrement dit : **40 contrôles sur 40** s'appuient sur un test capable d'échouer. Aucun contrôle n'est plus cru sur parole, et l'inventaire ne compte plus aucun `test-en-soi`.

## Par où continuer, par ordre de rentabilité

1. Continuer la **conversion des grilles** : `outils/modele-grilles.py --regle` en compte 36 dont 4 converties ; les 32 autres fixent encore leur nombre de colonnes, dont 30 par un palier de largeur. Chacune se convertit avec la même règle — le plus large minimum de piste qui garde les colonnes de conception au conteneur maximal — et le modèle dit d'avance l'écart avec l'ancienne cascade.
2. Résorber la **dette des paliers** comptée par `outils/compter-paliers.py` : 15 conditions de format pour 45 blocs, dont aucune n'a été mesurée. Commencer par les grilles (trois paliers, 13 blocs) qui s'obtiendraient en `auto-fit`, puis par le seuil 1260/1261 px, tenu à la main en deux endroits.
3. Vérifier les **empreintes** de l'archive des statuts (`sha256sum -c`), que `verifier-planches-statuts.py` contrôle en nombre, en unicité de noms et en forme de ligne — jamais en contenu.
4. Étendre les **pages de contrôle** aux autres scripts navigateur : la mesure de `verifier-graphismes.cjs` est désormais éprouvée sur une image générée, pas sur les trois pages réelles ni sur la constellation.

## Limites de ce document

- Les statuts viennent de la lecture des tests les 28 et 29 octobre 2026, pas d'une exécution de chaque mutation possible. `test` et `faute-en-memoire` sont des jugements sur ce que fait le test, pas des mesures.
- Le classement `aucun-test` de `verifier-securite.py` a été levé le 28 octobre 2026 par `outils/test_mutations_securite.py` ; six fautes plantées y suffisent à prouver que la porte refuse, pas qu'elle voit toutes les régressions de sécurité possibles.
- L'inventaire ne juge pas l'utilité des contrôles, seulement l'existence d'une preuve qu'ils peuvent échouer.
