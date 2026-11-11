# Sources IGN : troisième passe du 11 novembre 2026

**Troisième passe du 11 novembre 2026, à 16 h 14 UTC.** La seconde passe avait laissé `www.ign.fr/` sans aucune page lue : toutes les variantes tentées répondaient HTTP 403. Sans renvoyer cette tâche à la personne, l’agent a **retenté l’accueil déclaré** et **ouvert les services officiels de l’IGN sous d’autres domaines**. Résultat : **13 réponses HTTP 403**, **1 redirection**, **1 page d’erreur servie**, **2 contenus génériques** et **10 pages officielles réellement lues**, datées et confrontées aux deux fiches de géographie. **Aucune fiche modifiée, aucune adresse ajoutée au catalogue, aucun rattachement changé, aucun statut promu, aucune URL externe recopiée.**

Les références sont écrites sans schéma, comme dans `docs/rd/sources-ouvertes-2026-11-11.toml` et `docs/rd/sources-complement-2026-11-11.toml` ; les adresses exactes restent dans `docs/apprentissage/catalogue.toml`.

## 1. L’accueil déclaré reste fermé

L’adresse déclarée par les deux fiches est `www.ign.fr/`, avec le titre « Institut national de l’information géographique et forestière — IGN ». Elle reste **en HTTP 403** après trois passes le même jour. Ouvrir un autre domaine officiel de l’IGN **ne résout pas cette source-portail** : elle reste écrite dans `sources_indisponibles` des deux fiches de `docs/rd/relecture-agent-prototypes.toml`, et aucun rattachement n’est ajouté.

| Référence sans schéma | Statut | Repère |
| --- | --- | --- |
| `www.ign.fr/` | http-403 | Accueil déclaré dans le catalogue : HTTP 403, sans contenu ni bandeau de maintenance. Retenté sans paramètre puis avec un paramètre de relecture daté. |
| `www.ign.fr/?relecture-2026-11-11-3=1` | http-403 | Troisième retentative datée de l’accueil déclaré : HTTP 403, aucune page servie. |
| `www.ign.fr/institut/institut/statut-et-missions` | http-403 | Page de statut et de missions signalée par la recherche : HTTP 403. |
| `geoservices.ign.fr/` | http-403 | Ancien portail des géoservices : HTTP 403. |
| `macarte.ign.fr/cgu` | http-403 | Conditions générales de Ma carte IGN : HTTP 403. |
| `inventaire-forestier.ign.fr/spip.php?rubrique4=` | http-403 | Sous-domaine de l’inventaire forestier national : HTTP 403. |
| `education.ign.fr/dossiers/lire-une-carte-et-sorienter` | http-403 | Ressources pédagogiques IGN : HTTP 403. |
| `www.ign.fr/mag/` | http-403 | Rubrique magazine du portail : HTTP 403. |
| `www.ign.fr/mag/apprendre-lire-une-carte-en-cinq-etapes` | http-403 | Dossier « Apprendre à lire une carte en cinq étapes » signalé par la recherche : HTTP 403 ; l’extrait de recherche n’est pas une page lue. |
| `www.ign.fr/mag/apprendre-lire-une-carte-en-cinq-etapes?relecture-2026-11-11=3` | http-403 | Même dossier avec paramètre de relecture : HTTP 403. |
| `ign.fr/mag/apprendre-lire-une-carte-en-cinq-etapes` | http-403 | Même dossier sans www : HTTP 403. |
| `ign.fr/reperes/comment-fabrique-t-les-cartes` | http-403 | Page « Comment fabrique-t-on les cartes ? » : HTTP 403. |
| `www.ign.fr/publications-de-l-ign/institut/Ressources_pedagogiques/livret_decouvrez_LMDC.pdf` | http-403 | Livret pédagogique « Découvrez le monde des cartes » : HTTP 403 ; le PDF n’a pas été lu. |
| `www.geoportail.gouv.fr/` | redirection | L’ancienne adresse du Géoportail répond et renvoie sur l’explorateur de cartes de cartes.gouv.fr ; ce n’est pas une page indépendante et elle n’est pas comptée deux fois. |
| `data.geopf.fr/` | page-erreur-servie | La racine du domaine de données répond « no Route matched with those values » : page d’erreur servie, aucun contenu de catalogue. |
| `cartes.gouv.fr/rechercher-une-donnee/dataset/IGNF_SCAN-25` | contenu-generique | La fiche de donnée attendue n’est pas servie : seulement le bandeau « Bienvenue sur cartes.gouv.fr » et « Géoservices converge vers cartes.gouv.fr ». Aucune description du SCAN 25 lue à cette adresse. |
| `cartes.gouv.fr/catalogue/dataset/IGNF_PLAN-IGN` | contenu-generique | Même bandeau générique, titre « entityTitle | Rechercher une donnée ». Aucune fiche de donnée lisible. |

Les dossiers du magazine IGN (« Apprendre à lire une carte en cinq étapes », « Le paysage est toujours un objet politique… »), le livret pédagogique « Découvrez le monde des cartes » et la page « Statut et missions » apparaissent dans les résultats de recherche mais **pas dans les pages lues** : chaque tentative de lecture a répondu HTTP 403. Un extrait de recherche n’est pas une page lue et n’est pas consigné comme tel.

## 2. Les 10 pages officielles lues

| N | Référence sans schéma | Date relevée | Fiches | Tranche | Repère lu |
| ---: | --- | --- | --- | --- | --- |
| 1 | `cartes.gouv.fr/explorer-les-cartes/` | éditions 2026-10-15 et 2026-06-01 visibles dans le catalogue de couches | geo-decrire-paysage, geo-lire-legende-carte | 0 | Catalogue de couches : Plan IGN, photographies aériennes, Carte TOP 25 (SCAN 25), parcelles cadastrales. La fiche SCAN 25 dit que la carte topographique représente le relief par des courbes de niveaux et les détails du terrain : routes, sentiers, constructions, bois, arbre isolé, rivière, source. Un panneau « Légendes » permet d’ouvrir la légende d’une couche. |
| 2 | `cartes.gouv.fr/actualites/clap-de-fin-pour-le-geoportail-bienvenue-sur-cartesgouvfr` | publié le 30 septembre 2026 | geo-decrire-paysage, geo-lire-legende-carte | 0 | Le Géoportail a fermé le 30 septembre après vingt ans ; la quasi-totalité des services, données et fonctionnalités sont accessibles sur cartes.gouv.fr. Un convertisseur de liens est actif jusqu’au 31 décembre 2026. Le message est signé « L’équipe de l’IGN ». |
| 3 | `cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2026-01-scan-25/` | modifié le 26 janvier 2026 | geo-lire-legende-carte | 0 | Le SCAN 25® est publié chaque année à partir du fond cartographique au 1:25 000 ; c’est la version numérique de la carte papier. « Même si le contenu est identique entre la carte papier et le SCAN 25, la légende utilisée n’est pas identique. » L’IGN prévoit de rapprocher les deux légendes et de retravailler couleurs et police. |
| 4 | `cartes.gouv.fr/aide/fr/guides-utilisateur/visualiseur-cartographique/generalites-visualiseur/` | modifié le 7 octobre 2026 | geo-lire-legende-carte | 0 | Le service « Explorer les cartes » succède au Géoportail ; parmi les outils cités figure « afficher la légende des couches », à côté de la mesure de distances, du profil altimétrique et de la recherche de lieux. |
| 5 | `cartes.gouv.fr/decouvrir/explorer-les-cartes/` | page sans date affichée | geo-decrire-paysage, geo-lire-legende-carte | 0 | Les cartes de l’IGN sont dites « référence du territoire français » ; la page invite à « Consulter leur légende, leurs métadonnées ou encore interroger directement les données sur la carte ». Elle cite les fonds IGN, les prises de vues aériennes, le SCAN 25, le cadastre et les données d’occupation du sol. |
| 6 | `cartes.gouv.fr/decouvrir/` | page sans date affichée | geo-decrire-paysage, geo-lire-legende-carte | 0 | Quatre entrées : Explorer les cartes, Rechercher une donnée, Publier une donnée, Collaborer. La page nomme les jeux de données de référence (BD ORTHO, SCAN 25, OCS GE, forêts publiques ONF) et leurs producteurs. |
| 7 | `cartes.gouv.fr/aide/fr/partenaires/ign/referentiels-description-territoire/occupation-sol-topographie/ocs-ge-nouvelle-generation/` | modifié le 16 décembre 2025 | geo-decrire-paysage | 0 | « 2 dimensions pour décrire le sol : couverture (c’est quoi ?) / usage (à quoi ça sert ?) » ; la page renvoie à la nomenclature du CNIG et aux seuils appliqués. |
| 8 | `cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2026-07-plan-ign-hd-et-sentiers/` | modifié le 9 juillet 2026 | geo-decrire-paysage | 0 | Le Plan IGN HD est présenté comme une « cartographie des paysages » qui met en avant les éléments au-dessus du sol : végétation, bâtiments, ombres portées. Le rendu distingue la structure du relief, les silhouettes du bâti et de la végétation, l’occupation du sol, puis les données vectorielles BD TOPO « représentées selon la symbolisation utilisée sur Plan IGN ». |
| 9 | `data.geopf.fr/annexes/ressources/documentation/Legende2026.pdf` | prochaine édition annoncée pour le printemps 2027 ; lignes d’égale déclinaison au 1er janvier 2025 | geo-lire-legende-carte | 0 | Le document est une table de correspondance explicite entre des signes et ce qu’ils représentent : aérodromes, espaces aériens, obstacles, et un « FONDS CARTOGRAPHIQUE » où autoroute, route principale, route secondaire, végétation, point coté et monuments ont chacun un figuré. Il précise que l’IGN transcrit des renseignements collectés sans être habilité à vérifier sur le terrain leur nature, position et hauteur. |
| 10 | `data.geopf.fr/annexes/ressources/fiches/cartesIGN/composition_donnee_cartes_ign_classiques.pdf` | date de mise à jour : 20/10/2026 | geo-lire-legende-carte | 0 | Tableau des territoires, échelles, produits et dates d’édition : PLAN IGN au 1:1 066 à 1:4 265, SCAN 25 Touristique au 1:8 531 à 1:17 061, SCAN 100, SCAN régional, SCAN 1000 ; éditions 2026 pour la métropole et plusieurs territoires ultramarins. |

Le point de bascule est `cartes.gouv.fr` : l’article du 30 septembre 2026, signé « L’équipe de l’IGN », annonce la fermeture définitive du Géoportail et la migration des services, données et fonctionnalités vers ce site. L’ancienne adresse `www.geoportail.gouv.fr/` y renvoie effectivement. Les pages d’aide de `cartes.gouv.fr` sont publiées sous une rubrique « partenaires/ign » et datées ; les documents de `data.geopf.fr` sont les annexes de la Géoplateforme.

## 3. Confrontation avec les deux fiches, sans les modifier

| Fiche | Objectif déclaré | Ce que les pages lues apportent | Ce qui reste décidé |
| --- | --- | --- | --- |
| `geo-decrire-paysage` | Décrire un paysage à partir d’indices visibles et nommer une information qui demanderait une autre source. | Le catalogue de couches de cartes.gouv.fr cite routes, sentiers, constructions, bois, arbre isolé, rivière et source comme détails représentés sur une carte topographique ; la page OCS GE distingue couverture (« c’est quoi ? ») et usage (« à quoi ça sert ? »). Le second terme demande une autre source que la seule observation. | Ne pas transformer ce rapprochement en correction de la fiche : le statut reste « Prototype à relire » et l’adresse IGN reste dans sources_indisponibles. |
| `geo-lire-legende-carte` | Retrouver deux éléments sur une carte fictive en lisant d’abord la légende et les symboles correspondants. | La page « Évolution de la légende du SCAN 25® en 2026 » dit qu’une légende est une convention qui peut différer entre version papier et version numérique ; la légende OACI 2026 montre une table explicite signe / signification ; le visualiseur permet d’« afficher la légende des couches ». | Ne pas importer les couleurs de la légende OACI dans la fiche : le domaine aéronautique n’est pas celui de la carte fictive. |

Les deux fiches gardent le verdict `a-trancher`, leur source Éduscol déjà ouverte, leur source IGN indisponible et `sources_non_ouvertes = 1`. La troisième passe **consigne des extraits confrontés avant toute modification**, elle ne touche à aucun champ éditorial.

## 4. Ce qui ne change pas

Aucune des 81 fiches du catalogue, aucune des 107 pages générées, aucun statut éditorial, aucune page HTML, CSS ou JavaScript, aucun PDF local, aucune URL du Journal officiel, aucun droit déclaré, aucune date de revue du portefeuille, aucune décision A/B/C. `docs/apprentissage/relectures.toml` reste vide. Les 81 relectures d’agent gardent 40 `a-trancher`, 41 `relue-sans-ecart`, 131 rattachements de sources ouvertes et 20 égalités simples sans écart. La dette initiale des 391 autres unités reste consignée. Le jugement du rendu à l’œil reste à la personne, sans texte à relire de sa part. Aucune publication, aucun poussage, aucune fusion, aucun déploiement, aucune certification.

## 5. Limites

1. L’adresse déclarée www.ign.fr/ reste en HTTP 403 sur les trois passes du 11 novembre 2026. Les pages lues sur cartes.gouv.fr et data.geopf.fr sont des pages officielles de l’IGN, pas l’ouverture de l’accueil déclaré : aucune source-portail n’est déclarée résolue.
2. La date de cette troisième passe est encore le 11 novembre 2026 (16 h 14 UTC dans l’environnement de travail). La retentative « à une date ultérieure » annoncée dans le complément reste donc à faire ; ce registre ne la remplace pas.
3. Les extraits de recherche concernant les dossiers du magazine IGN, le livret pédagogique et la page « Statut et missions » n’ont pas été lus : fetch_page a répondu HTTP 403 pour chacun. Ils ne sont pas consignés comme lectures.
4. Deux fiches de données de cartes.gouv.fr ne servent qu’un bandeau générique « Bienvenue sur cartes.gouv.fr » : elles sont consignées en contenu générique, sans description de donnée inventée.
5. La racine data.geopf.fr/ sert une page d’erreur « no Route matched with those values » : elle est consignée comme page d’erreur servie, pas comme contenu.
6. Aucune adresse de remplacement n’est ajoutée au catalogue, aucune fiche n’est modifiée, aucun rattachement du registre d’agent n’est changé, aucun statut promu. Ces pages donnent un contexte officiel, elles ne valident pas le contenu pédagogique des deux fiches.

## 6. Prochaine action prise par l’agent

La retentative **à une date ultérieure** annoncée dans `docs/rd/sources-complement-2026-11-11.md` reste ouverte : l’environnement de travail date encore du 11 novembre 2026. À cette date ultérieure, retenter `www.ign.fr/`, puis consigner toute page de l’Institut réellement lue **avant** de modifier l’une des deux fiches. Les 10 pages officielles déjà lues restent un contexte daté, pas un rattachement. Pour la plaquette INAO, le fichier `media/199172` et l’entrée MDN « Byte », ne rien inventer. Les 14 fiches de domaines sensibles gardent leur porte d’expertise compétente.

## 7. Reproduire

```
python3 outils/verifier-sources-ouvertes.py
python3 outils/test_mutations_sources_ouvertes.py
python3 outils/relecture-agent-prototypes.py --verifier
python3 outils/relire-contenus.py
python3 outils/construire-avancees.py --verifier
python3 outils/memoire-eva.py --verifier
git diff --check
```

`outils/verifier-sources-ouvertes.py` garde désormais les trois passes ; son banc `outils/test_mutations_sources_ouvertes.py` plante 11 situations dans une copie jetable, dont un accueil IGN déclaré lu et une réponse HTTP 403 embellie en contenu.

*Aucune URL externe nouvelle n’est recopiée ici. Les références sans schéma et les titres déclarés suffisent à retrouver les passages ; les adresses exactes restent dans le catalogue.*
