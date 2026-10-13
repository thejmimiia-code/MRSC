# Tour R&D — cohérence des textes publics

**Date : 13 octobre 2026** · **Branche de travail : `arena/f585be03-mrsc`** · **État : corrections ciblées faites, revue humaine encore requise.**

Ce rapport consigne une revue transversale des affirmations répétées sur le site M.R.S.C. Elle cherche les écarts entre le texte, les générateurs, les sources de vérité, les documents disponibles et l’hébergement déclaré. Elle ne certifie ni l’exactitude scientifique de toutes les pages, ni la qualité de l’hébergement, ni la validation éditoriale par une personne.

## 1. Périmètre et méthode

### Éléments examinés

- Les 12 pages HTML à la racine, le catalogue et ses sorties (70 fiches), la page générée du simulateur, le README et les règles éditoriales/R&D associées.
- Les sources de vérité : `docs/apprentissage/catalogue.toml`, `docs/apprentissage/referentiel.toml`, `outils/construire-apprentissages.py`, `simulateur/PROVENANCE.json`, les registres du moteur, les fichiers PDF locaux et la configuration GitHub Pages.
- Les affirmations les plus susceptibles de se répéter : nombre d’entrées et statut des fiches, comptes du simulateur, provenance des documents, adresse publique, copie locale versus service distant.
- Les consignes R&D et de validation de `AGENTS.md`, du manuel R&D et des skills de revue contradictoire, de stratégie de tests et de documentation.

### Méthodes

1. Comparer les formulations aux fichiers qui font autorité et aux générateurs, sans éditer manuellement leurs sorties.
2. Rechercher les nombres, les liens de documents et les déclarations d’hébergement, puis contrôler leur contexte plutôt que de conclure à partir d’une occurrence isolée.
3. Interroger la configuration GitHub Pages et comparer les compteurs du moteur embarqué à la tête amont du dépôt source.
4. Ajouter des assertions d’intégration pour les confusions confirmées (copies PDF locales/externe, statut du corpus et adresse actuellement publiée).
5. Garder séparés contrôles automatisés, relecture humaine, vérification de sources et validation de production.

## 2. Constats, décisions et état

| ID | Constat vérifiable | Décision et état |
| --- | --- | --- |
| C-01 | Le catalogue comprend **70 entrées** : 26 fiches du corpus initial et 44 prototypes explicitement à relire. La page d’apprentissage présentait ces catégories sans préciser que la relecture indépendante de toutes les fiches initiales n’est pas garantie. | **Corrigé dans cette passe.** Le générateur expose les deux catégories, le total et la réserve de relecture ; le registre de transparence reprend la même limite. Un test statique protège le résumé généré. |
| C-02 | Les PDF des statuts et des bulletins d’adhésion et de don sont présents dans `assets/documents/`. La parution au Journal officiel, elle, reste un lien vers un hébergeur externe. Le registre de transparence distinguait déjà ces deux cas, mais le README disait encore que tous les PDF dépendaient de leurs hébergeurs d’origine. | **Corrigé dans cette passe.** Le README indique les copies locales et le lien externe. Un test contrôle les trois chemins locaux, l’étiquette « copies locales » et la source externe du Journal officiel. |
| C-03 | La configuration GitHub Pages renvoie `cname: null` ; les 82 canoniques trouvées pointent vers `thejmimiia-code.github.io`. Le domaine personnalisé `www.mrsc.fr` n’est pas configuré dans GitHub Pages. | **Statut clarifié, configuration à faire par l’administrateur du domaine.** Le README distingue l’adresse GitHub Pages actuelle de l’adresse souhaitée et rappelle de garder `www.mrsc.fr` visible, sans redirection. Les canoniques, le DNS, le CNAME et le HTTPS ne sont pas modifiés dans cette revue. |
| C-04 | La copie du simulateur dans le site est à la révision `99491d8`, copiée le 8 octobre 2026. La tête amont consultée le 13 octobre est [`4b15284892114235bc1e16a0e8cb2c801de9a115`](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple/commit/4b15284892114235bc1e16a0e8cb2c801de9a115). **Les deux exposent 101 leviers, 52 indicateurs et 11 scénarios** ; les chiffres « plus de 100 », 52 et 11 de la page sont cohérents avec la copie contrôlée. | **Pas de mise à jour du moteur.** La vérification de patch dans les deux sens ne permet ni application directe ni confirmation que le correctif local est entièrement intégré en amont. La page précise désormais que la copie embarquée peut différer de la version hébergée. Examiner le patch avant toute synchronisation. |
| C-05 | Une note d’audit datée du 12 octobre rapporte 81 URL de sitemap ; le contrôle courant du dépôt compte 82 URL. Les notes de travail sont datées et décrivent un état antérieur. | **Aucune correction rétroactive.** Conserver les résultats historiques avec leur date et utiliser les sorties actuelles des vérificateurs pour décrire le site présent. |
| C-06 | Les comptes publics du simulateur (101 leviers dans la copie locale, 52 indicateurs et 11 scénarios), les 70 entrées d’apprentissage et les 15 domaines ont une source de vérité ou un contrôle correspondant. La recherche de cohérence n’a pas établi d’autre contradiction chiffrée dans ce périmètre. | **Aucune extrapolation.** Cela ne prouve pas que tous les faits, références externes, raisonnements ou formulations de toutes les fiches sont exacts. |

## 3. Optimisations apportées

- **Fiches d’apprentissage :** le générateur affiche maintenant le total et distingue clairement les 26 fiches du corpus initial des 44 prototypes à relire. Il indique que la relecture indépendante de toutes les fiches initiales n’est pas garantie. Dans les textes d’« Apprendre » et des Mondes, « fiches complètes » est remplacé par « fiches autonomes » ou « page autonome », pour ne pas confondre une page disponible avec un contenu validé.
- **Transparence :** la page précise la répartition 26/44 et la réserve de relecture indépendante.
- **Documents :** le README différencie les copies locales et le lien externe du Journal officiel ; il n’attribue plus aux PDF locaux une dépendance à un hébergeur tiers.
- **Simulateur :** la page de présentation rappelle que la copie locale peut différer de la version hébergée et renvoie à la révision et à la date de copie déjà affichées.
- **Adresse :** le README parle de l’adresse GitHub Pages actuellement publiée, non d’une adresse durable ; le raccordement de `www.mrsc.fr` reste une tâche séparée qui nécessite une vérification technique et administrative.
- **Prévention des régressions :** les contrôles d’intégration couvrent les libellés local/externe, les formulations du README, le compte d’indicateurs du moteur et l’avertissement de version. Le générateur reste la seule source de la page d’apprentissage.

## 4. Brainstorming de conception

| Piste | Avantage | Limite ou risque | Décision |
| --- | --- | --- | --- |
| Réécriture générale des 83 pages contrôlées | Ton plus uniforme en une passe | Peut supprimer les distinctions utiles, introduire de nouveaux faits ou modifier un texte sans signal vérifiable | Écartée. Corriger les ambiguïtés confirmées et préparer des relectures humaines ciblées. |
| Registre unique, centralisé, de toutes les affirmations | Une seule source pour chaque chiffre | Nouveau format à maintenir, couplage des données et de l’éditorial, lourd pour peu de répétitions | Différé. Garde-fous ciblés dans les tests ; réexaminer si des écarts récurrents apparaissent. |
| Afficher un nombre exact de leviers sur la page de présentation | Précision immédiate | La copie locale, Render et l’amont peuvent être déployés à des dates différentes | Garder « plus de 100 » pour le résumé ; afficher la révision/date de la copie et faire correspondre les comptes exacts de la page générée au moteur local. |
| Synchroniser systématiquement le moteur amont | Éviter une copie obsolète | Un conflit peut retirer ou altérer le correctif local de sécurité et ses adaptations | Reporter. Rebaser et revoir le patch, tester les protections et comparer la provenance avant remplacement. |
| Étiqueter chaque document par son hébergeur | Catégorisation courte | Confond copies locales et sources originales | Distinguer « document officiel, copie locale » et « source externe », puis verrouiller ce vocabulaire par un test. |
| Modifier les canoniques vers `www.mrsc.fr` immédiatement | Aligner l’adresse affichée et l’objectif | Risque d’incohérence si CNAME, DNS ou certificat ne sont pas prêts | Reporter jusqu’à confirmation de l’administrateur et vérification du service ; ne pas substituer une redirection vers `github.io`. |

## 5. Plan global de suite

| Priorité | Action | Condition de sortie |
| --- | --- | --- |
| P0 — fait ici | Corriger les formulations et créer des tests ciblés pour les chiffres, catégories de PDF, état de l’adresse et révision du simulateur. | Les contrôles exécutés passent ; aucun statut ou chiffre non sourcé n’est ajouté. |
| P1 — relecture éditoriale | Faire relire les nouvelles formulations par une personne de l’association et vérifier la compréhension des distinctions 26/44, copie locale/source externe et version locale/en ligne. | Une revue humaine est datée et consignée ; les corrections conservent les réserves utiles. |
| P1 — domaine | Confirmer auprès de la personne responsable le DNS de `www.mrsc.fr`, le CNAME GitHub Pages et le HTTPS ; mettre ensuite à jour canonicals et attribution, sans rediriger l’adresse souhaitée vers `github.io`. | Tests de configuration et vérification des réponses publiques réussis après le changement. |
| P1 — moteur | Comparer l’amont à `outils/patchs/simulateur-securite-mrsc.patch`, porter ou remplacer les protections avec une revue ligne par ligne, puis vérifier la page générée et les routes. | Patch relu, tests de sécurité et d’intégration réussis, provenance mise à jour après seulement. |
| P2 — entretien éditorial | Examiner les pages d’information par thème, puis les fiches avec des personnes compétentes ; vérifier les sources externes directement selon le risque. | Décisions, sources consultées, limites et états de revue documentés ; aucune relecture de l’agent présentée comme validation indépendante. |
| P2 — architecture | Envisager un registre généré de faits communs uniquement si de nouvelles divergences montrent que les tests ciblés ne suffisent plus. | Comparaison coût/bénéfice documentée et possibilité de préserver les nuances contextuelles. |

## 6. Vérifications et limites

### Contrôles automatiques réellement exécutés

- `python3 -m py_compile simulateur/*.py api/*.py outils/*.py` — réussi.
- `python3 outils/verifier-rd-continue.py` — réussi ; 11 initiatives structurées, dont `coherence-textes-publics`.
- `python3 outils/construire-apprentissages.py --verifier` — réussi après régénération ; 70 fiches, 15 domaines, sorties synchronisées.
- `python3 outils/construire-simulateur.py --verifier` — réussi ; page intégrée synchronisée avec la copie du moteur.
- `python3 outils/verifier-site-statique.py` — réussi ; 83 pages, 70 fiches, 82 URL de sitemap, métadonnées, liens/ancres et assertions éditoriales contrôlés.
- `python3 outils/verifier-securite.py` — 60 contrôles ciblés réussis.
- `python3 outils/verifier-integration.py` — tous les contrôles passent, y compris les assertions ajoutées et l’exercice local des 16 routes API. Les services externes de test sont remplacés par des réponses simulées ; ce n’est pas un test de Render en production.
- `node --check assets/js/site.js`, `node --check assets/js/navigation-parcours.js` et `git diff --check` — réussis.

Pendant l’édition, les premiers contrôles ont signalé, à juste titre, une sortie d’apprentissage non encore régénérée, puis des attentes de test trop liées à l’ancienne formulation. Le générateur et les assertions ont été ajustés ; toute la suite finale ci-dessus a ensuite réussi. Ces contrôles sont automatisés. Aucun examen humain, navigateur réel ou déploiement n’est revendiqué.

La comparaison amont a été faite sur le dépôt GitHub source et une copie clonée temporaire ; le test du patch dans les deux sens était non destructif. Aucun fichier du moteur local n’a été remplacé.

Cette revue ne comprend pas :

- une expertise scientifique, juridique, pédagogique ou associative de chaque paragraphe ;
- la visite et la validation directe de chaque URL de source externe ;
- des essais volontaires, une relecture par lecteur d’écran ou une inspection visuelle humaine ;
- une vérification du fonctionnement réel de Render, de l’adresse `www.mrsc.fr`, du DNS, du certificat HTTPS ou du déploiement GitHub Pages après les changements ;
- une validation indépendante des 70 fiches, ni l’affirmation que le catalogue couvre tous les besoins.

Le plan détaillé et le brainstorming repris dans le [plan global de consolidation](../rd-plan-global-consolidation.md) sont le point de reprise. L’initiative `coherence-textes-publics` du portefeuille demeure **à valider humainement**.
