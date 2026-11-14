# Relecture par agent — lot « coût de la vie et carte », 14 novembre 2026

**Ce que ce document est :** la trace de la relecture faite par l’agent sur les
contenus du lot `cout-de-la-vie-et-carte`. **Ce qu’il n’est pas :** une
validation humaine, une expertise statistique, un audit ni une conformité. La
personne garde le rendu à l’œil ; personne n’a relu ce lot.

## Ce qui a été ouvert, et ce qui en a été retenu

Quatre sources publiques ont été lues le 14 novembre 2026, puis recopiées à la
main dans `docs/rd/sources-primaires/`, chacune avec son empreinte SHA-256, son
URL et sa date de consultation.

### `data-gouv-dvf`

`https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres` — fiche du jeu
de données « Demandes de valeurs foncières », lue par son API publique.

Ce qu’elle permet d’affirmer : le fichier est **produit par la DGFiP**, publié
sous licence `lov2` (Licence Ouverte 2.0), mis à jour **semestriellement en avril
et en octobre**, il couvre la métropole et les DOM **à l’exception de l’Alsace,
de la Moselle et de Mayotte**, la dernière mise à jour date du **12 octobre
2026**, et sa réutilisation **interdit la ré-identification** des personnes
comme **l’indexation** par les moteurs de recherche.

Ce qu’elle ne dit pas : la qualité des prix, les ventes non enregistrées, les
écarts entre communes. Et comme chaque mise à jour remplace la totalité des
fichiers, un chiffre publié n’est reproductible qu’avec l’archive du jour.

### `geo-api-decoupage`

`https://geo.api.gouv.fr/decoupage-administratif` — page d’accueil de l’API
Découpage administratif.

Ce qu’elle permet d’affirmer : l’API sert les communes (et les arrondissements),
les communes associées et déléguées, les EPCI, les départements et les régions.
Un appel vérifié le même jour, `communes?code=75056`, rend pour Paris
`2103778` habitants et un centre à `[2.347, 48.8589]`.

Ce qu’elle ne dit pas : ni la licence, ni le millésime de population, ni les
limites d’usage. La page ne présente donc pas la population comme millésimée :
elle l’annonce comme un ordre de grandeur daté.

### `data-gouv-decoupage-administratif`

`https://www.data.gouv.fr/datasets/decoupage-administratif-1` — fiche du jeu de
données « Découpage administratif », source de l’API précédente.

Ce qu’elle permet d’affirmer : la licence est `lov2`, la provenance est le Code
officiel géographique de l’INSEE, la population légale de l’INSEE et les codes
postaux de La Poste, la périodicité est annuelle, et le jeu **ne contient aucune
géométrie** — les contours sont explicitement renvoyés à un autre jeu de
données. C’est ce qui interdit de dessiner une commune à partir de ces données.

### `data-gouv-admin-express`

`https://www.data.gouv.fr/datasets/admin-express-admin-express-cog-admin-express-cog-carto-admin-express-cog-carto-pe-admin-express-cog-carto-plus-pe`
— fiche du jeu de données ADMIN EXPRESS.

Ce qu’elle permet d’affirmer : les contours viennent de l’**IGN**, sous
**Licence Ouverte** (`lov2`), et suivent le **Code officiel géographique** de
l’INSEE. Le site ne dessine donc aucun contour de mémoire.

Ce qu’elle ne dit pas : la fiche décrit l’**édition courante**, pas l’**édition
2018** utilisée par le fond de carte. La fiche produit de l’IGN
(`geoservices.ign.fr/adminexpress`), citée comme ressource du jeu de données, a
répondu **403** — elle n’a pas été lue, et la page le dit au lieu de la citer
comme ouverte.

### Les deux adresses d’API que le collecteur interroge

Le site ne lit pas la licence dans une phrase écrite à la main : il la demande.
Deux adresses distinctes des fiches publiques sont donc enregistrées comme
sources, parce que ce sont elles que le code appelle.

- `data-gouv-dvf-api` —
  `https://www.data.gouv.fr/api/1/datasets/demandes-de-valeurs-foncieres/` :
  la réponse porte « license » : « lov2 », « frequency » : « semiannual »,
  « last_update » : « 2026-10-12… » et l’empreinte SHA-1 de la ressource à
  télécharger. C’est cette lecture qui fait échouer la collecte si la licence
  change, et c’est ce qui rend le refus vérifiable.
- `geo-api-communes-champs` —
  `https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux,population,centre,departement`
  : l’adresse appelée par le collecteur. Un appel de contrôle sur Paris
  (`code=75056`) rend le nom, le code, la population et le point central.

Ce que ces deux extraits ne disent pas : qu’un fichier téléchargé est intact
(l’empreinte le dira), que la réponse est complète pour toutes les communes, ni
quel millésime porte la population. Une réponse d’API n’est pas une page.

### L’export intermédiaire et la source des revenus

- `france-geojson-export` —
  `https://api.github.com/repos/gregoiredavid/france-geojson` : l’API du dépôt
  d’où vient le fichier de contours ne déclare **aucune licence** (champ
  « license » à null). C’est écrit, plutôt que de laisser croire que la Licence
  Ouverte viendrait de l’export : elle vient de l’IGN, à la source.
- `data-gouv-filosofi` —
  `https://www.data.gouv.fr/datasets/revenus-et-pauvrete-des-menages-aux-niveaux-national-et-local-revenus-localises-sociaux-et-fiscaux`
  : le revenu médian communal existe, il est libre (`fr-lo`, badge « hdv ») et
  produit par l’INSEE ; ses ressources passent par des pages insee.fr en
  xls/xlsx, sans URL de fichier stable. La page n’affiche donc aucun revenu :
  c’est une collecte non faite, pas une donnée inexistante.

## Ce que la relecture a vérifié dans les contenus

- **Aucun total de coût de la vie n’est calculé.** La page affiche la population,
  les prix médians au m² des appartements et des maisons, et le nombre de ventes.
  Le seul calcul est une division présentée comme une hypothèse de la personne :
  mensualité saisie ÷ prix médian.
- **Une médiane sous cinq ventes n’est pas publiée**, et la page dit pourquoi.
- **Trois causes d’absence, trois phrases** : aucune vente enregistrée, commune
  d’Alsace-Moselle hors du champ de DVF, données non encore collectées. Ce sont
  trois faits de nature différente ; les confondre serait déjà une affirmation.
- **Les mention de licence et de producteur** de la page correspondent aux fiches
  lues, y compris l’exclusion de l’Alsace, de la Moselle et de Mayotte.
- **La limite de contour** est écrite : métropole seulement, communes en points,
  découpage 2018.

## Ce que cette relecture ne couvre pas

- Aucun fichier DVF n’a été téléchargé depuis cette machine : les prix, leur
  couverture réelle et leur vraisemblance **ne sont pas vérifiés**. Le banc du
  collecteur (15 cas) prouve qu’il refuse une source muette ou une licence
  fermée, pas que les chiffres produits seront justes.
- Aucun chiffre n’a été recoupé contre une source secondaire (notaires, INSEE,
  observatoires locaux).
- Aucune lecture par une personne compétente en statistique publique ; aucun
  essai avec une personne utilisatrice ; aucun lecteur d’écran ; aucun essai
  dans Firefox ou Safari.
- Les extraits ont été recopiés à la main depuis les réponses d’API : la mise en
  forme, les liens et les info-bulles ne sont pas reproduits, et une réponse
  d’API n’est pas une page mise en page.
