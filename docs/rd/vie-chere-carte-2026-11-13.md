# Coût de la vie et carte de France : ce que les données libres permettent, et ce qu’elles interdisent

Statut : **dossier de R et D écrit par l’agent**, pas une validation. Aucune
relecture humaine, aucun essai avec des personnes, aucune expertise économique
ou statistique. Les chiffres cités ici sont ceux des sources consultées le
13 novembre 2026 ; ils ne sont pas des résultats de calcul du site.

## 1. La demande, reformulée sans la trahir

« Un simulateur qui affiche les vrais coûts de la vie avec une vraie carte de la
France sur laquelle on peut zoomer et arriver jusqu’à la ville. »

Trois exigences se cachent dans cette phrase, et elles ne se résolvent pas de la
même façon :

1. **Une carte réelle**, qu’on agrandit du pays au département, puis à la ville.
2. **Des coûts réels**, c’est-à-dire mesurés par un organisme public, datés,
   sourcés, et affichés seulement là où la mesure existe.
3. **Des données libres et vérifiées** : licence qui autorise la réutilisation,
   provenance traçable, fichier comparé à son empreinte.

Le piège est dans le mot « coût de la vie ». Il n’existe **aucune donnée
officielle par commune** qui le mesure comme un tout. Ce qui existe, ce sont des
morceaux : les prix des logements réellement vendus, les revenus déclarés, les
loyers là où un observatoire les publie, la population. Un simulateur honnête
n’additionne donc pas « un coût de la vie » qu’il aurait inventé : il montre les
morceaux mesurés, nomme ce qui manque, et laisse la personne faire ses propres
hypothèses à partir de son revenu.

## 2. Ce qui est réellement disponible, vérifié le 13 novembre 2026

### 2.1 Les contours : IGN, Admin Express, Licence Ouverte

La couche `ADMINEXPRESS-COG-CARTO.LATEST:departement` du géoservice de l’État
(`data.geopf.fr`, WFS) expose les propriétés `code_insee`, `nom_officiel`,
`code_insee_de_la_region`, `code_siren` et la géométrie. Vérifié en interrogeant
le service : la couche existe, répond en GeoJSON, et refuse un nom de propriété
qui n’existe pas — donc elle se contrôle elle-même.

Les contours utilisés pour le fond de carte viennent d’un export **IGN Admin
Express COG, édition 2018**, converti en GeoJSON et simplifié à 25 % par le
projet `gregoiredavid/france-geojson`, qui documente sa méthode (conversion
`mapshaper`, précision 5 décimales, simplification pondérée). Les limites
départementales n’ont pas bougé depuis 2018 en métropole : ce fond est stable,
et il est daté. Il est simplifié une seconde fois par le dépôt (voir § 5) pour
tenir dans le budget de poids d’une page.

Conséquence à écrire en façade : la carte couvre **la métropole** (96
départements). Les départements d’outre-mer ne sont pas affichés à cette
échelle, et le dire vaut mieux que d’écraser la Corse pour faire entrer Mayotte.

### 2.2 Les prix : DVF, la seule mesure des transactions réelles

Le jeu « Demandes de valeurs foncières » (DGFiP, publié sur data.gouv.fr) donne
les transactions immobilières des cinq dernières années, **licence Lov2**
(Licence Ouverte 2.0), mise à jour semestrielle — la dernière datait du
12 octobre 2026 au moment de la consultation. Points vérifiés dans la fiche du
jeu de données :

- fichiers par semestre, `valeursfoncieres-<année>-s<1|2>.txt.zip`, environ
  32 à 47 Mo chacun, avec une empreinte SHA-1 publiée ;
- **couverture incomplète** : « à l’exception de l’Alsace, de la Moselle et de
  Mayotte ». Le Bas-Rhin, le Haut-Rhin et la Moselle n’ont donc **aucun** prix
  DVF ; ce n’est pas une lacune du site, c’est le droit local du livre foncier ;
- **données à caractère personnel** : la réutilisation ne doit pas permettre de
  réidentifier les personnes, et l’indexation par les moteurs de recherche est
  interdite. Le site n’agrège que par commune (médianes et nombre de ventes),
  ne publie aucune parcelle ni adresse, et n’expose pas ces fichiers à
  l’indexation.

Ce que DVF permet de dire : le **prix médian au m² des ventes** d’appartements
et de maisons dans une commune, sur un semestre ou une année, avec le **nombre
de ventes** qui rend la médiane interprétable. Ce qu’il ne permet pas de dire :
un « prix du logement » pour les locataires, ni le coût pour un ménage donné.

### 2.3 La population et les coordonnées : `geo.api.gouv.fr`

L’API de l’État expose pour chaque commune `nom`, `code`, `codesPostaux`,
`population`, `centre` (lon/lat) et son département. Vérifié sur Paris :
`{"nom":"Paris","code":"75056","population":2103778,"centre":{"coordinates":[2.347,48.8589]}}`.
Le Code officiel géographique y est à jour, contrairement au fond de carte de
2018 : c’est pourquoi **les communes sont des points**, pas des contours.

### 2.4 Les revenus : identifiés, pas encore automatisés

Le dispositif FiLoSoFi de l’INSEE (revenus déclarés et disponibles, médianes,
taux de pauvreté, à l’échelle communale) est présent sur data.gouv.fr sous
licence Licence Ouverte, mais **ses fichiers pointent vers des pages HTML de
l’INSEE** (xls/xlsx), pas vers des URL stables et directement lisibles par une
machine. Une collecte automatique y serait fragile : elle casserait au premier
changement de page. C’est une dette nommée, pas une fonctionnalité cachée.

### 2.5 Les loyers : il n’existe pas de source libre couvrante

Les loyers encadrés ne concernent que quelques agglomérations, et les
observatoires locaux publient des loyers par agglomération, pas par commune.
Aucune donnée libre ne permet aujourd’hui d’afficher un loyer médian pour les
34 000 communes. Le simulateur ne l’inventera pas : il l’écrira.

## 3. Le modèle retenu, et pourquoi il ne calcule pas un « coût de la vie »

Le simulateur affiche, pour une commune :

| Ce qui est affiché | D’où cela vient | Ce que cela vaut |
| --- | --- | --- |
| Population | `geo.api.gouv.fr`, recensement INSEE | un ordre de grandeur daté, arrondi à la centaine |
| Prix médian au m², appartements | DVF, semestre collecté | une médiane de ventes réelles, avec le nombre de ventes |
| Prix médian au m², maisons | DVF, semestre collecté | idem |
| Nombre de ventes | DVF | la condition pour lire la médiane : sous 5 ventes, elle n’est pas affichée |
| Surface accessible avec un budget | **calcul**, à partir des chiffres ci-dessus et de la saisie de la personne | une division, pas une donnée |

Et **pas** de « coût de la vie total » : aucune source ne le mesure par commune.
Le calcul de surface est transparent : budget mensuel saisi, taux et durée
affichés comme des **hypothèses de la personne**, mensualité calculée, surface =
mensualité ÷ prix au m². Le site ne prétend ni connaître le taux réel d’un
emprunt, ni les frais, ni la fiscalité locale, ni le coût du transport.

Deux règles de lecture sont affichées avec les chiffres :

- une médiane sous **cinq ventes** n’est pas publiée (elle dirait le prix d’une
  maison, pas celui d’une commune) ;
- quand une commune n’a pas de données, la page dit **pourquoi** : « aucune vente
  enregistrée dans le fichier », « commune d’Alsace-Moselle : hors du champ de
  DVF », ou « données non encore collectées ».

## 4. Architecture : statique, précalculée, sans service tiers

- Le site est statique et publié sur GitHub Pages : **aucune requête vers un
  serveur de cartes** au chargement. C’est une exigence du dépôt (pas de média
  distant sans action explicite) et une exigence de sobriété : une carte
  vectorielle de 100 Ko remplace des centaines de tuiles.
- Les données sont **collectées hors de la page**, figées dans le dépôt avec
  leur provenance (URL, date, licence, empreinte SHA-256 du fichier source), puis
  lues par la page. Un fichier sans provenance est refusé.
- Découpage par département : la page ne charge que le département ouvert. Le
  fond national est le seul fichier systématiquement chargé.
- Une collecte qui échoue **n’efface rien** : elle n’écrit que si toutes les
  sources répondent, si les contrôles de vraisemblance passent et si les
  empreintes correspondent. Sinon elle sort en erreur et laisse les données
  précédentes en place, avec leur date.

## 5. Le fond de carte, fabriqué et contrôlable

`outils/preparer-fond-de-carte.py` transforme un GeoJSON départemental en un
fichier compact (tableaux de coordonnées arrondies à trois décimales, environ
1 km, simplification de Douglas-Peucker à 0,012°) et écrit sa provenance à côté.
Le fichier d’entrée faisait 556 Ko ; la sortie en fait **118 Kio** : 96 départements de
métropole (Corse-du-Sud et Haute-Corse compris), découpage 2018. Il est vérifié par `--verifier`, qui
recalcule l’empreinte et refuse un fichier modifié à la main.

## 6. Ce qui a été construit, et par quoi c’est tenu

| Pièce | Ce qu’elle fait | Ce qui la contrôle |
| --- | --- | --- |
| `outils/preparer-fond-de-carte.py` | fabrique le fond départemental | `--verifier` + 3 cas du banc |
| `outils/collecter-vie-chere.py` | télécharge DVF et `geo.api`, agrège par commune, refuse une source muette, une licence fermée, une colonne absente, une médiane aberrante | `--verifier` + 10 cas du banc (serveur HTTP local) |
| `.github/workflows/collecte-vie-chere.yml` | lance les tests puis la collecte le 1er de chaque mois, écrit la provenance, ouvre une PR — jamais un commit direct sur `main` | `verifier-workflows.py` |
| `couts-vie-chere/contenu.txt` | le texte de la page, en fragment | sentinelle de relecture |
| `outils/construire-page-couts.py` | assemble la page avec la coque du site | `--verifier` + 2 cas du banc (page retouchée à la main refusée) |
| `assets/js/carte-vie-chere.js` | carte SVG, zoom, recherche, fiche, calcul de surface | `node --check` ; rendu constaté en Chromium |
| `assets/css/site.css` (bloc `.couts-*`) | grille deux colonnes, cibles de 44 px, `forced-colors` | `verifier-budgets-visuels.py`, empreinte CSS |

Le banc commun est `outils/test_collecte_vie_chere.py` : **15 cas**, dont cinq qui
visent les deux fabricants (fond amputé d’un département, licence fermée, page
dérivée du fragment). Aucun cas ne touche le réseau public : le collecteur est
éprouvé contre un serveur local qui joue la panne, la licence fermée et le
fichier tronqué.

La page a été regardée dans un Chromium sans interface : 97 options de
département, 96 tracés, message « Carte de la métropole prête », état « Aucune
collecte n’a encore été faite », sélection du Rhône → zoom et message « aucune
donnée collectée pour ce département ». Aucun prix inventé n’y apparaît.

**Le point de navigation, tranché :** la page n’est **pas** dans le menu
principal. Ce menu est recopié dans chaque page du site, dont 108 fiches
produites par `outils/construire-apprentissages.py` ; l’y ajouter demande de
modifier le générateur, de régénérer puis de resigner l’ensemble des pages, ce
qui n’a pas été fait ici. La page s’atteint depuis `documents.html`, elle est
dans le `sitemap.xml`, et elle le dit elle-même à la fin de la section des
sources. C’est une dette nommée, pas un oubli.

## 7. Ce que cette R et D ne prouve pas

- Aucune donnée n’a encore été collectée par la machine au moment d’écrire ces
  lignes : l’atelier de l’agent n’a pas d’accès réseau vers data.gouv.fr, IGN ou
  `geo.api.gouv.fr`. Les sources ont été **lues** (API interrogée, fiche du jeu
  de données consultée), pas **téléchargées**. La page affiche donc ses états
  « données non collectées » tant que la collecte n’a pas tourné là où le réseau
  existe.
- Le prix médian au m² n’est pas un indice de prix : il mélange des biens de
  qualités différentes et ne suit pas l’évolution d’un même bien.
- DVF ne couvre pas l’Alsace-Moselle ni Mayotte ; les loyers ne sont pas couverts
  du tout ; les revenus ne sont pas encore collectés.
- Les contours sont ceux de 2018 : justes pour les départements, impropres aux
  communes, qui sont donc des points.
- Aucun essai avec des personnes, aucune validation par un statisticien, aucune
  vérification du rendu de la carte sur un appareil réel : la page a été
  regardée dans un Chromium sans interface, à une largeur, sans lecteur d’écran.
- Aucun essai dans Firefox ni Safari. La carte est du SVG lu par le navigateur ;
  rien ne dit qu’elle se comporte pareil ailleurs, et le zoom n’a été éprouvé
  qu’à la souris simulée et par le code, pas au clavier par une personne.
- Le zoom va jusqu’à la commune **comme point** : il n’y a pas de contour
  communal. « Jusqu’à la ville » est donc tenu pour la sélection et la fiche,
  pas pour le dessin du bâti.

## 8. Suite, par ordre de valeur

1. Lancer `collecte-vie-chere.yml` à la main (`workflow_dispatch`) : c’est la
   seule machine qui a le réseau. Puis relire les chiffres de trois communes
   connues (Paris, Lyon, un village) avant de dire que la carte affiche des
   prix réels.
2. Ajouter la page au menu principal, en modifiant le générateur des fiches et
   en resignant l’ensemble — ou décider que `documents.html` suffit, et retirer
   la phrase qui l’annonce.
3. Automatiser les revenus FiLoSoFi depuis une URL stable, ou renoncer
   explicitement à cet indicateur.
4. Ajouter les contours communaux actuels (IGN Admin Express, 34 000 polygones)
   sous forme de tuiles vectorielles préparées, si le budget de poids le permet.
5. Faire relire le modèle par une personne compétente en statistique publique
   avant toute présentation comme un outil d’aide à la décision.
