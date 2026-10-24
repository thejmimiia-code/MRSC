# Formats d'affichage : ce qui est vérifié, et comment

Cette page consigne la mesure qui a servi de référence pour l'affichage du site
sur tous les formats d'écran, les défauts qu'elle a révélés, les corrections
apportées et ce qui reste hors de portée d'un contrôle automatique.

Dernière mesure : **22 octobre 2026**, sur les 13 pages du site.

## 1. Pourquoi une mesure plutôt qu'une relecture

Les feuilles de style se lisent, mais une règle juste peut produire un défaut :
un `min-height: 0` posé pour gagner de la place annule une cible tactile, une
piste `1fr` s'élargit à la largeur d'un mot insécable, une image plafonnée à
l'écran reste plus dense que sa source. Aucune de ces trois situations ne se
voit en lisant la règle isolée.

La mesure a donc été faite **dans un navigateur réel** (Chromium sans
interface), page par page, format par format.

## 2. La matrice mesurée

| Famille | Formats |
| --- | --- |
| Téléphones | 280 (pliable), 320, 360, 390, 414, 430 |
| Téléphones en paysage | 568 × 320, 844 × 390 |
| Tablettes | 768, 820, 1024 en paysage |
| Ordinateurs | 1280, 1366, 1440 (2×), 1680 |
| Grands écrans | 1920, 2 560, 3 440 (ultra-large), 3 840 (4K) |
| Densités | 1×, 2×, 3× |
| Présentations du site | Équilibrée, Lecture, Vitrine, Mosaïque, Panorama composite, Compacte |
| Tailles de texte | 75 %, 85 %, 100 %, 115 %, 130 % |
| Réglages | contraste renforcé, espacement renforcé |

Soit **247 mesures** pour la matrice écran seule et **910 mesures** pour les
mêmes pages croisées avec les six présentations et les quatre réglages — portées
à **1 157 mesures** après le changement d'échelle de texte du § 6.

## 3. Ce que la mesure a trouvé

Chaque ligne a été constatée, corrigée, puis remesurée.

| Défaut | Constat | Correction |
| --- | --- | --- |
| Défilement latéral aux formats étroits | jusqu'à 72 px à 280 px sur l'accueil, 37 px sur la page 404, 18 px sur les liens utiles | césure des tokens insécables, `min-width: 0` sur les pistes, `minmax(0, 1fr)` partout où une piste nue `1fr` laissait la largeur minimale du contenu élargir la colonne |
| Titre qui déborde | « Transparence, » mesure 301 px à 40 px de corps pour 258 px disponibles | corps réduit sous 340 px, césure en dernier recours |
| Texte sous 12 px | 40 déclarations, dont l'en-tête compact à **10,9 px** et ses commandes à 20 px de haut | plancher à `.75rem` (12 px) et cible de 24 px |
| Cibles tactiles trop petites | commandes de l'en-tête compact à **20 px**, contact de pied de page à 23,6 px, liens de source à 17 px | plancher de 24 px (WCAG 2.2, 2.5.8) |
| Illustration d'accueil étirée | 1,7× sur téléphone en paysage, 1,65× sur portable 2×, 1,39× sur tablette 2× | plafond d'affichage par densité : 700 px à 2×, 560 à 2,5×, 466 à 3×, 400 à 3,5× |
| Logo étiré à 3× | 258 px d'appareil pour 234 px de source, sur les 13 pages | plafond à 78 px de 3× à 3,49×, 66 px au-delà |
| Héros des mondes étiré en paysage | 1,5× sur un téléphone de 844 px à 3× : 2 508 px demandés pour 1 672 disponibles | paliers de densité du panneau : 836, 668, 557, 477 px |
| Illustration de la promotion anglais étirée | 1,46× dans les présentations Lecture, Mosaïque, Panorama et Compacte, où la colonne s'élargit | plafond à 520 px, la largeur déjà annoncée par `sizes` |
| Texte à 150 % | débordement de 35 à 117 px sur 10 pages, surtout à 280 px | en-tête qui passe à la ligne, césure `anywhere` (seule valeur qui réduit la largeur minimale) |
| Mesure de lecture | jusqu'à 150 caractères par ligne sur écran large | `main .container p { max-width: 72ch }` |
| Bouton rogné | « Voir notre méthode de R&D » faisait 268 px dans une carte de 260 px | intitulé sécable |

## 4. Résultat de la mesure finale

- **247 mesures écran : aucun défaut** — pas de défilement latéral, aucun
  élément hors cadre, aucun texte sous 12 px, aucune cible sous 24 px, aucune
  image agrandie, aucun texte rogné.
- **Six présentations × sept formats : aucun défaut.**
- **Texte à 150 % × sept formats : aucun défaut.**
- **Tous les crans de texte (75 à 130 %) et les six présentations : aucun
  défaut** sur les 1 157 mesures de la passe finale.

Le critère de netteté reste celui du § 4.2 quater de
[poids-et-sobriete-numerique.md](poids-et-sobriete-numerique.md) : la source
doit fournir au moins autant de pixels que l'écran en affiche.

## 5. Le garde-fou exécutable

`outils/verifier-affichages.py` vérifie que les règles sur lesquelles repose
cette mesure sont toujours présentes : plancher de texte, plancher de cible,
mesure de lecture, plafonds d'image par densité, pistes de grille sans `1fr`
nue, césure des mots longs, en-tête compact non rapetissé, densité du rendu 3D,
qualité d'encodage des images (voir § 6 bis) et décor du héros avec son repli
(voir § 6 ter).

Il ne remplace pas la mesure : il constate que ses appuis n'ont pas été
retirés. **Sept mutations** — texte à `.72rem`, contact ramené à 23 px,
en-tête compact ramené à zéro (deux formes), palier de densité supprimé, piste
`1fr` rétablie, plafond du héros des mondes supprimé — ont été appliquées
volontairement : toutes sont détectées.

Deux failles du contrôle lui-même ont été trouvées ainsi : il ignorait les
valeurs suivies de `!important`, et il ne reconnaissait pas `min-height: 0`
écrit sans unité, c'est-à-dire précisément la forme qui annule une cible.
Corrigées, puis remutées.

## 6. L'échelle de texte a changé le 22 octobre 2026

L'ancienne échelle offrait 50, 75, 100, 125 et 150 %. Le cran 50 % donnait
**8 px de corps** et 14 px pour les liens du texte : illisible, même choisi
volontairement. La personne responsable du site a retenu de **relever les
crans** plutôt que de poser un plancher qui aurait rendu deux crans identiques.

| Avant | Après | Corps |
| --- | --- | ---: |
| 50 % | **75 %** | 12 px |
| 75 % | **85 %** | 13,6 px |
| 100 % | 100 % | 16 px |
| 125 % | **115 %** | 18,4 px |
| 150 % | **130 %** | 20,8 px |

Deux conséquences traitées :

1. **Migration.** La clé de stockage passe de `mrsc-texte-niveau` à
   `mrsc-texte-cran` : les anciennes valeurs sont ambiguës avec les nouvelles
   (75 y signifiait « réduit », c'est maintenant le minimum). Une table de
   correspondance reprend le choix une seule fois — 50 → 75, 75 → 85, 125 → 115,
   150 → 130, crans indexés 0/1/2 → 100/115/130, ancien réglage binaire → 115 %.
   Vérifié dans le navigateur sur les cinq cas, y compris la réécriture de la
   nouvelle clé.
2. **Plancher des petites tailles.** `166` déclarations en `rem`, `3` en `em` et
   la balise `<small>` sont désormais écrites `max(12px, …)` : au cran 75 %, un
   `.82rem` vaudrait 9,84 px. Le plancher ne change rien à 100 % ni au-delà, et
   garantit 12 px minimum partout. Mesure : plus aucun texte sous 12 px sur les
   13 pages au cran 75 %.

Le simulateur embarque la même échelle et la même clé, sinon il serait retombé à
100 % en lisant une valeur qu'il ne connaît pas ; sa page a été régénérée.

## 6 bis. Netteté : le rendu 3D et l'encodage (23 octobre 2026)

Deux garde-fous nés du signalement « la version smartphone est pixelisée ». La
mesure complète est au § 4.2 quinquies de
[`poids-et-sobriete-numerique.md`](poids-et-sobriete-numerique.md) ; ici, seule
la règle vérifiée est rappelée.

- **Densité du rendu 3D.** `assets/js/anglais-aventure.js` doit garder
  `DENSITE_MAX >= 3` et `BUDGET_PIXELS >= 6_000_000`, et ne doit contenir
  **aucun** `Math.min(devicePixelRatio, N)`. Ce plafond était la cause du flou
  du décor : tampon de 642 px étiré sur 964 px de dalle à 3×.
- **Qualité d'encodage.** `outils/optimiser-images.py` doit garder AVIF ≥ 78 et
  WebP ≥ 88. Les images étant servies au pixel de l'écran, une qualité basse se
  lit directement comme du pixel : la q60 mesurait 31,9 dB à 800 px, contre
  33,2 dB en q78.

Trois mutations — `DENSITE_MAX = 2`, plafond `Math.min(window.devicePixelRatio
|| 1, 2)` réintroduit, qualités 60/80 rétablies — sont détectées avec la ligne
fautive nommée.

## 6 ter. Le héros des Mondes est devenu un décor vectoriel (23 octobre 2026)

Le héros de `anglais-aventure.html` n'est plus une image mais un `<canvas>` WebGL
(`assets/js/decor-atlas.js`). Une image a une résolution finie ; un rendu n'en a
pas. Mesure sur huit profils : **tampon égal au besoin en pixels d'appareil**, de
360 px à 2× à 1 920 px à 1×, donc aucun agrandissement possible.

Deux conséquences pour cette porte :

- la règle de densité (`DENSITE_MAX >= 3`, `BUDGET_PIXELS >= 6 Mpx`, aucun
  `Math.min(devicePixelRatio, N)`) s'applique désormais aux **deux** fichiers de
  rendu, `anglais-aventure.js` et `decor-atlas.js` ;
- un contrôle vérifie que le canvas est présent et décrit pour les aides
  techniques (`role="img"`, `aria-label`), que le repli image existe et reste
  différé, et que la fonction d'échec le charge.

Détail des mesures, des quatre mutations détectées et des deux qui ne le sont pas :
§ 4.2 sexies de [`poids-et-sobriete-numerique.md`](poids-et-sobriete-numerique.md).

## 6 ter bis. L'illustration d'« Apprendre » n'est plus agrandie (23 octobre 2026)

Signalement, capture en main : « l'image dans le menu apprendre est moche, on voit
les pixels ». La mesure a confirmé un défaut net, pas une question de goût.

- **La cause : l'attribut `height` du HTML servait de hauteur.** L'illustration
  porte `width="1672" height="941"` pour réserver sa place, et la feuille
  déclarait `aspect-ratio: 16 / 10` avec `object-fit: cover`. Or `aspect-ratio`
  ne calcule une dimension que si l'autre est **automatique** : avec une hauteur
  imposée de 941 px, la boîte mesurait **497 × 941 px** au lieu de 497 × 311, et
  l'image — un 16/9 — était étirée **2,1 fois** pour la couvrir. Les pixels
  venaient de là, pas de l'encodage.
- **La correction tient en une déclaration** : `height: auto` sur
  `.english-promo-art img`. `aspect-ratio` reprend la main, la boîte retrouve
  497 × 311 px, et `object-fit: cover` recadre au lieu d'étirer.
- **Ce que la densité garantit ensuite.** Mesure après correction, source
  réellement servie comparée aux pixels d'appareil nécessaires :

| Profil | Boîte | Variante servie | Besoin en pixels | Marge |
| --- | --- | --- | --- | --- |
| 390 px à 3× | 328 × 205 | 1 200 px | 984 px | 1,22× |
| 390 px à 2× | 328 × 205 | 800 px | 656 px | 1,22× |
| 576 px à 2× | 504 × 315 | 1 200 px | 1 008 px | 1,19× |
| 768 px à 2× | 305 × 190 | 1 200 px | 610 px | 1,97× |
| 1 024 px à 2× | 414 × 259 | 1 200 px | 828 px | 1,45× |
| 1 280 px à 2× | 497 × 311 | 1 200 px | 994 px | 1,21× |
| 1 440 px à 2× | 497 × 311 | 1 200 px | 994 px | 1,21× |
| 1 440 px à 1× | 497 × 311 | 800 px | 497 px | 1,61× |

Aucun profil ne descend sous 1× : l'image est toujours servie au moins au pixel
de l'écran, et aucun débordement horizontal n'apparaît à aucune largeur.

- **Garde-fou : 14ᵉ contrôle `controler_illustrations`.** Il exige `height: auto`,
  `aspect-ratio` et `object-fit: cover` sur la règle, les deux déclarations
  `sizes` à `520 px` au-delà de 760 px (une seule occurrence laisserait l'autre
  format annoncer une autre largeur), les dimensions intrinsèques `1672 × 941`
  dans la page, et le plafond de 520 px qui rend la déclaration `sizes` vraie
  dans toutes les présentations. **Six mutations rejouées, six détectées** :
  `height: auto` retiré, `aspect-ratio` retiré, `object-fit` retiré, plafond
  retiré, `sizes` faussé sur une seule source, dimensions intrinsèques retirées.
- **Une mutation qui a d'abord échappé au contrôle** : `sizes` faussé sur une
  seule des deux sources passait, parce que le contrôle cherchait la bonne
  déclaration *quelque part* dans la figure. Il compare désormais le nombre
  d'occurrences (deux) et l'ensemble des valeurs.

Limite : la mesure est celle d'un Chromium sans interface, sur `apprendre.html`
seulement ; les autres illustrations n'ont pas de `aspect-ratio` et ne sont pas
concernées par ce défaut précis.

## 6 quater. Le menu du téléphone : cinq commandes, deux rangées, un panneau borné (23 octobre 2026)

Le menu ouvert en mode smartphone a été mesuré page par page, panneau ouvert, à
320, 360, 390 et 430 px, puis en paysage (844 × 390) et sur tablette (768 × 1024).
Quatre défauts sont sortis de la mesure, dont un bloquant.

| Défaut | Mesure avant | Correction |
| --- | --- | --- |
| Liens inatteignables en paysage | panneau de **472 px** commençant à 49 px, donc bas à **522 px** pour un écran de 390 px ; `overflow: visible` | plafond `calc(100dvh - var(--hauteur-entete))` + `overflow-y: auto` |
| Contenu sorti par le haut | `justify-content: center` sur un conteneur défilable : « Accueil » à **y = 10** pour un panneau à 51 | `justify-content: safe center` (repli `flex-start`) |
| Commandes de 24 px | cinq boutons de 24 px de haut, empilés en deux ou trois rangées irrégulières | **32 px** sur téléphone, **36 px** sur les autres formats compacts, deux colonnes pleines |
| Libellés coupés | « Parcour / s », « Affichag / e », « Présent / ation » (`overflow-wrap: anywhere`) | deux colonnes pleines, `overflow-wrap: normal`, « Présentation » sur toute la largeur |

- **Le plancher tactile du site ne change pas** : `PLANCHER_CIBLE_PX` reste à
  24 px (WCAG 2.2, 2.5.8) pour les liens et les autres cibles. Les cinq commandes
  de l'en-tête compact ont leur propre plancher, `PLANCHER_COMMANDES_ENTETE_PX = 32`,
  parce qu'elles se touchent au pouce sans visée. Trois passages le même jour :
  44 px d'abord, jugés trop lourds (149 px d'en-tête sur un écran de 640), puis
  36 px, puis **32 px sur téléphone** sur nouvelle demande — les autres formats
  compacts (paysage court, tablette compacte) restent à 36 px. À 32 px, le bouton
  garde 10 px au-dessus et au-dessous d'un libellé de 12 px, et **8 px au-dessus
  du minimum WCAG** : le plancher du contrôle est 32 px, donc un retour aux 24 px
  d'origine échoue.
- **La hauteur de l'en-tête est mesurée, pas supposée.** Elle varie avec le logo,
  le cran de texte (217 px à 320 px et 130 %) et le mode compact. `site.js`
  publie `--hauteur-entete` au chargement puis sur chaque `ResizeObserver` :
  une constante en `rem` laissait le panneau déborder de 47 px au cran 130 %.
- **Deux colonnes, pas davantage.** `auto-fit` en ouvrait trois à 430 px et
  quatre à 520 px : la cinquième commande laissait alors un trou à côté
  d'« Affichage ». La grille est fixée à `repeat(2, minmax(0, 1fr))`, avec un
  repli explicite à une colonne sous 300 px, et l'en-tête y prend toute la largeur
  (sans quoi « Agrandir », 43,6 px de texte, ne tenait pas dans une colonne de
  42,8 px).
- **Le panneau rejoint les bords** : sa largeur explicite annulait l'étirement
  par `left`/`right`, et il s'arrêtait 16 px avant le bord droit ; il s'arrêtait
  aussi à 8 ou 24 px des côtés à cause de la gouttière de `.nav-inner`, désormais
  calculée (`calc((100vw - 100%) / -2)`) au lieu d'être devinée.

Mesure après correction (Chromium sans interface, panneau ouvert) :

| Profil | Panneau (x, y, l, h) | Bas ≤ écran | Commandes |
| --- | --- | --- | --- |
| 320 × 568 @2 | 0, 110, 320, 427 | 537 ≤ 568 | 2 + 2 + 1 pleine largeur, 32 px |
| 390 × 780 @3 | 0, 110, 390, 427 | 537 ≤ 780 | 32 px, libellés entiers |
| 430 × 900 @3 | 0, 110, 430, 427 | 537 ≤ 900 | 32 px |
| 844 × 390 @3 (paysage) | 0, 49, 844, 331 | 380 ≤ 390 | une rangée, 36 px |
| 768 × 1024 @2 | 8, 192, 752, 472 | 664 ≤ 1024 | cinq boutons de 44 px (en-tête non compact) |

Aucun débordement horizontal, aucun lien hors du cadre, aucune commande sous
32 px sur téléphone ni sous 36 px ailleurs en compact, à tous les crans de texte
(100 % et 130 %). L'en-tête passe de 149 px (44 px) à 122 px (36 px) puis
**110 px** (32 px) sur les trois profils de téléphone.

Le garde-fou `controler_panneau_du_menu` (11ᵉ contrôle de
[`verifier-affichages.py`](../../outils/verifier-affichages.py)) exige, dans une
même règle, le défilement interne, le plafond en `dvh` et le centrage `safe`, la
publication de `--hauteur-entete` (avec mesure initiale et `ResizeObserver`) et
la grille à deux colonnes, la dernière commande en pleine largeur et le repli à
une colonne sous 300 px. Mutations rejouées : défilement retiré, plafond remplacé
par une constante, `safe center` retiré, grille sans repli, dernière commande non
pleine largeur, publication renommée, `ResizeObserver` retiré, mesure initiale
retirée, commande ramenée à 24 px puis à 20 px — **toutes détectées**, fichiers
restaurés à l'identique.

Limite : la mesure est celle d'un Chromium sans interface, pas d'un téléphone
réel ; les captures ont été relues à 320, 390 et 844 px.

## 6 quinquies. Deux commandes au lieu de cinq : « Personnalisation » (23 octobre 2026)

Demande : « un second menu regroupe les commandes liées pour ne laisser que deux
boutons ». L'en-tête compact portait cinq commandes (« Menu », « Agrandir »,
« Parcours », « Affichage », « Présentation ») réparties en deux ou trois
rangées. Les quatre commandes de réglage sont désormais réunies dans un panneau
« Personnalisation » ; l'en-tête n'en montre plus que deux.

- **Aucune des 98 pages n'est modifiée.** `assets/js/site.js` crée le panneau et
  y déplace les trois blocs de réglage au chargement ; `navigation-parcours.js`
  insère « Parcours » devant « Affichage », donc dans le panneau. Le HTML statique
  reste inchangé, et `has-js` empêche le panneau de clignoter sans JavaScript.
- **Le panneau est une liste de lignes**, pas un vol de commandes : chaque
  réglage fait 36 px de haut sur toute la largeur utile, avec un chevron à
  droite ; les panneaux ouverts restent dans le flux (`position: static`), bordés
  à gauche au lieu de flotter au-dessus.
- **La spécificité est le piège.** Les règles de l'en-tête compact
  (`html.has-js .site-header.is-compact …`) portent plus de classes que les
  règles du panneau : écrites sans préfixe, elles restaient sans effet et les
  réglages revenaient côte à côte, un panneau ouvert se posant à **x = 370 px
  pour une ligne de 350 px**. Les règles du panneau sont donc écrites
  `html.has-js .site-header .customize-settings-panel …` et déclarées après.
- **Échap ferme par étages.** Un premier Échap referme le réglage ouvert
  (« Présentation », « Affichage »…) et laisse le panneau ouvert ; un second
  referme le panneau et rend le focus à sa commande. Sans cela, Échap aurait fait
  disparaître le panneau sous les doigts de qui ferme un seul réglage.
- **« Agrandir » ne referme pas son propre panneau.** Le bouton vit dans le
  panneau : le refermer au clic rendait « Réduire » inatteignable. Mesuré comme
  réversible à 320, 390, 720 et 1 440 px.
- **Le panneau ne déborde plus de l'écran.** Sous 760 px et en paysage court, il
  se cale sous l'en-tête à la largeur de l'écran ; au-delà, il reste ancré sous
  son bouton. Sur tablette et sur ordinateur, « Agrandir/Réduire » figure en
  première ligne du panneau et fonctionne dans les deux sens.

Mesure après correction (Chromium sans interface, panneau ouvert, puis réglages
ouverts) :

| Profil | En-tête | Commandes | Panneau (x, y, l, h) | Débordement |
| --- | --- | --- | --- | --- |
| 320 × 568 | **90 px** | 145 / 145 px, 32 px | 8, 99, 304, 188 | 0 |
| 390 × 780 | 90 px | 180 / 180 px, 32 px | 8, 99, 374, 188 | 0 |
| 430 × 900 | 90 px | 200 / 200 px, 32 px | 8, 99, 414, 188 | 0 |
| 520 × 900 | 90 px | 245 / 245 px, 32 px | 8, 99, 504, 188 | 0 |
| 844 × 390 (paysage) | 49 px | 80 / 151 px, 36 px | 8, 58, 828, 188 | 0 |
| 768 × 1024 | 194 px | 92 / 161 px, 44 px | 162, 200, 352, 147 | 0 |
| 1 280 × 900 | 198 px | 161 px, 44 px | 912, 202, 352, 147 | 0 |
| 1 440 × 900 | 198 px | 161 px, 44 px | 1 072, 202, 352, 147 | 0 |

Quatre lignes de réglage de 36 px, aucune sous 32 px, aucun élément hors du
panneau, aucun débordement horizontal ; à 130 % de texte, le panneau atteint
379 px de haut à 320 × 568 et reste sous le bas de l'écran (499 ≤ 568).

Les garde-fous de `controler_panneau_du_menu` exigent désormais : le panneau
créé en JavaScript avec son identifiant `#site-customize-panel`, le déplacement
des **trois** blocs de réglage (sinon une commande reste dans l'en-tête), les
lignes `display: flex; width: 100%` préfixées `html.has-js .site-header`, les
panneaux imbriqués `position: static`, le panneau ancré et défilant, et la grille
à deux colonnes avec son repli à une colonne. Mutations rejouées : préfixe de
spécificité retiré, `position: static` retiré, `layoutSettings` laissé dans
l'en-tête, `overflow: auto` retiré, grille ramenée à une colonne —
**toutes détectées**, fichier restauré à l'identique. Les 8 essais navigateur de
`test-experience.cjs` couvrent la bascule réversible, la fermeture par étages et
les deux commandes à 32 px à 320, 500 et 720 px.

Limite : la mesure est celle d'un Chromium sans interface ; le panneau est
positionné par rapport à l'en-tête, dont il suit la hauteur mesurée.

## 6 sexies. Finitions du panneau : la qualité se mesure aussi à l'écran (23 octobre 2026)

Retour d'usage après la fusion : « c'est un affichage de haute qualité qu'il faut,
pas un truc de basse qualité ». Le panneau fonctionnait, mais quatre défauts se
voyaient à la capture, aucun à la lecture du code.

| Défaut | Mesure avant | Correction |
| --- | --- | --- |
| Quatre lignes grises identiques | aucun repère visuel ; « Agrandir » centré au milieu de lignes alignées à gauche | une icône par ligne (masque SVG, 19 px) et l'habillage des lignes appliqué au bouton d'en-tête |
| Compteur de taille invisible | « 100 % » hérité du blanc de la barre marine : **1:1** sur le fond blanc du panneau | couleur propre au panneau, contrôle segmenté `A− · 100 % · A+` |
| Texte des cartes sous le seuil AA | 12,16 px de `--muted` sur le fond bleu clair d'une carte sélectionnée : **4,36:1** | `--text-soft` : **5,58:1** |
| Chevron dépendant de la machine | glyphe « ⌄ » en police ; sa forme variait et il jurait avec le hamburger SVG | masque SVG partagé par les quatre panneaux du site, même épaisseur de trait (2) que le hamburger |

- **Les icônes sont des masques, pas des glyphes** : `background-color:
  currentColor` et `mask:` sur le `::before` du résumé. Le dessin est identique
  sur toutes les machines et net à 4×, là où un caractère dépend de la police de
  substitution. Les quatre tracés (agrandir/réduire, parcours, affichage,
  présentation) partagent la même grille de 24 px et la même épaisseur.
- **Le panneau est redessiné, pas seulement recoloré** : rayon de 16 px, ombre à
  trois couches, apparition de 160 ms (supprimée sous `prefers-reduced-motion`),
  lignes de 44 px sur fond transparent qui se teintent au survol et à
  l'ouverture, filet entre le réglage d'en-tête et les trois préférences.
- **Chaque panneau ouvert a été remis en page pour 350 px** : le compteur
  devient un contrôle segmenté de 44 px de haut ; le parcours passe en deux
  colonnes (« Précédent / Suivant », « Accueil / Dernière vue ») avec l'étape sur
  sa propre ligne, au lieu d'un « Étape 1/1 » collé au bord droit derrière un
  filet ; les cartes de présentation passent de 20 px à 40 px d'aperçu et de
  0,65 rem à 0,45 rem de rembourrage ; le contenu ouvert s'aligne sous le
  libellé (retrait de 28,6 px), plus sous l'icône.
- **Un garde-fou plutôt qu'une promesse** : `controler_habillage_du_panneau`
  (12ᵉ contrôle de `verifier-affichages.py`) exige le masque du chevron avec
  `font-size: 0`, au moins trois icônes de réglage, la couleur propre du compteur
  et `--text-soft` sur le texte des cartes. **Quatre mutations rejouées, quatre
  détectées** : glyphe rendu au chevron, icône retirée, couleur du compteur
  retirée, contraste des cartes ramené à `--muted`.
- **Un essai de plus, réellement mesuré** : `test-experience.cjs` vérifie que
  chaque réglage porte bien un masque non vide (`maskImage !== 'none'`) ; **8/8**.

Mesure après finitions (Chromium sans interface, chaque réglage ouvert tour à
tour, panneau borné et défilant) :

| Profil | Affichage | Parcours | Présentation | Débordement |
| --- | --- | --- | --- | --- |
| 320 × 568 | panneau 434 px, bas 528 ≤ 568 | 312 px, bas 408 | 462 px, bas 560 | 0 |
| 360 × 740 | 416 px, bas 510 | 312 px, bas 408 | 634 px, bas 732 | 0 |
| 390 × 780 | 416 px, bas 476 | 312 px, bas 371 | 712 px, bas 772 | 0 |
| 430 × 900 | 416 px, bas 472 | 312 px, bas 370 | 832 px, bas 892 | 0 |
| 520 × 900 | 416 px, bas 476 | 312 px, bas 371 | 832 px, bas 892 | 0 |
| 844 × 390 (paysage) | 325 px, bas 379 | 325 px, bas 381 | 325 px, bas 382 | 0 |
| 768 × 1 024 | 436 px, bas 630 | 331 px, bas 528 | 814 px, bas 1 012 | 0 |
| 1 280 × 900 | 436 px, bas 632 | 331 px, bas 530 | 686 px, bas 887 | 0 |
| 1 440 × 900 | 436 px, bas 634 | 331 px, bas 531 | 686 px, bas 887 | 0 |

Le panneau ne sort jamais du cadre et aucun élément ne déborde de sa boîte
(`0 px` partout) ; quand la présentation ouverte dépasse la hauteur restante,
c'est le panneau qui défile, comme prévu par son plafond en `dvh`. À 130 % de
texte avec contraste renforcé, le balayage ne relève plus aucun texte sous son
seuil de contraste.

Limite : ces mesures sont des captures de Chromium sans interface ; le rendu sur
un téléphone réel reste à constater, en particulier les ombres du panneau.


## 6 septies. Le pied de page, remis d'aplomb puis centré (23 octobre 2026)

Deux signalements, deux passages. Le premier, avec capture : « le bas de page
est mal présenté, c'est anarchique ». Le second, après publication : « l'affichage
devrait être centré ! Ce serait plus joli ! ».

### Premier passage : le point orphelin

- **La cause n'était pas une règle de style mais un script.** Le module de
  `site.js` qui met chaque phrase de contenu en début de ligne s'appliquait aussi
  au pied de page. Il ne savait pas qu'un point peut suivre un lien : à
  « Boussole des savoirs. Une copie imprimée… », le découpage produisait un
  fragment « . » seul, que `display: block` posait sur sa propre ligne. Mesure
  avant : trois lignes pour la note de version, la deuxième ne contenant qu'un
  point (y = 9 852).
- **Deux corrections, aux deux endroits.** Le pied de page sort du périmètre du
  découpage — des mentions légales se lisent d'un tenant — et la règle de
  découpage elle-même apprend qu'un morceau sans lettre ni chiffre n'est pas une
  phrase : il rejoint celle qui le précède.
- **Cas limite, trouvé après la publication.** Un texte qui *commence* par la
  ponctuation du lien qui le précède — `Voir <a>la page</a>. Une seconde phrase` —
  n'a pas de phrase précédente à l'intérieur du nœud : la règle y accrochait
  d'abord le point devant la phrase suivante (« .Une seconde phrase »). Ce nœud
  n'est donc plus découpé du tout ; trois cas rejoués dans le navigateur : lien
  suivi d'un point (un seul bloc, intact), sigle `M.R.S.C.` (deux blocs justes),
  deux phrases ordinaires (trois blocs justes).
- **Les séparateurs « · » de la liste légale pouvaient finir une ligne.** La
  liste est passée en `<ul>`, 97 pages et le générateur de fiches alignés, et le
  séparateur de la note de version est devenu insécable.
- **La colonne « Naviguer »** (dix liens) faisait le double des autres, avec un
  grand vide sous le logo. Au-delà de 1 040 px, elle passe en deux colonnes de
  libellés insécables.

### Deuxième passage : une seule colonne, centrée

- **Le bloc du bas devient une colonne centrée.** `grid-template-columns:
  minmax(0, 1fr)`, `justify-items: center`, `text-align: center`, `gap: .55rem` :
  les droits, puis les liens légaux, puis la note de version derrière son filet.
  C'est le centrage demandé, et il ne dépend plus de la largeur : la composition
  ne change pas d'allure d'un écran à l'autre.
- **Plus aucun filet vertical dans la liste légale.** Le séparateur `border-left`
  ne se détachait pas de son lien, mais il ouvrait la rangée quand elle se
  repliait, et le bloc se lisait en barres. Seuls les écarts séparent désormais
  les entrées ; la liste reste une `<ul>` sans puce.
- **Le repli de la liste est décidé, pas subi.** À 390 px, quatre entrées
  tenaient sur la première ligne et « Haut de page » retombait seule en dessous.
  Trois entrées mesurent 252 px, quatre 331 px : la liste est bornée à 320 px
  (`max-width: 20rem`) sous 520 px, ce qui donne partout le même repli, trois
  entrées puis deux. À 130 % de texte, la même borne produit deux puis deux puis
  une, sans débordement.
- **Ce que le centrage coûte.** Le bloc du bas passe de deux rangées à trois :
  130 px au lieu de 82 px à partir de 768 px, soit 425 px de pied de page à
  1 440 px contre 377 px. C'est le prix du centrage — l'alternative, garder
  droits et liens côte à côte, laissait un grand vide au milieu.
- **Un piège de maintenance.** Une première tentative avait supprimé, avec le
  bloc média du pied de page, un `@media (max-width: 920px)` entier et ses règles
  sans rapport : il en restait un débordement horizontal de 3 px à 320 px
  (`article.scope-card` finissait à x = 323). La bissection par échange de
  fichiers — CSS seul, JS seul, les deux — a désigné la feuille de style. Le bloc
  final ne contient plus que des règles de pied de page, et un `}` orphelin qui
  traînait après le bloc `forced-colors` a été retiré (accolades équilibrées,
  1 161 / 1 161).

Mesure après correction (Chromium sans interface, `index.html`) :

| Profil | Droits | Liens légaux | Note de version | Écart de centrage | Débordement |
| --- | --- | --- | --- | --- | --- |
| 320 × 640 | 2 lignes | 2 rangées (3 + 2) | 3 lignes | 0 px | 0 |
| 390 × 800 | 2 lignes | 2 rangées (3 + 2) | 3 lignes | 0 px | 0 |
| 768 × 900 | 1 ligne | 1 rangée | 2 lignes | 0 px | 0 |
| 1 024 × 800 | 1 ligne | 1 rangée | 2 lignes | 0 px | 0 |
| 1 160 × 900 | 1 ligne | 1 rangée | 2 lignes | 0 px | 0 |
| 1 440 × 900 | 1 ligne | 1 rangée | 2 lignes | 0 px | 0 |
| 1 920 × 1 080 | 1 ligne | 1 rangée | 2 lignes | 0 px | 0 |

L'écart de centrage est la distance entre le milieu de chaque bloc et le milieu du
bloc du bas : nul partout. Aucune puce, aucun filet vertical, aucun bloc de
ponctuation seule ; aucun débordement horizontal, y compris à 130 % de texte avec
contraste et espacement renforcés, et sur six autres pages (accueil, apprendre,
documents, transparence, 404, deux fiches) aux largeurs 320 à 1 920 px. Hauteur du
pied de page : 1 038 px à 320, 994 px à 390, 759 px à 768, 425 px au-delà de
1 160 px.

### Troisième passage : le texte lui-même, pas seulement sa boîte

Le centrage publié ne tenait pas : sur une capture suivante, les droits et les
liens légaux se lisaient bien au centre, mais la note de version restait collée
au bord gauche.

- **La cause est une règle globale.** Le paragraphe est aligné par une règle
  `p` générale sur `text-align: start`. Elle s'applique directement à l'élément
  et gagne sur le `text-align: center` hérité du bloc : les deux premiers blocs
  paraissaient centrés parce qu'ils tiennent sur une ligne et que leur boîte est
  réduite à cette ligne, tandis que la note, elle, s'étend sur la largeur
  maximale et laissait voir son alignement à gauche. Un `text-align: center`
  explicite sur les paragraphes du bas de page suffit.
- **Ce que la mesure avait manqué.** Elle comparait les milieux des *boîtes* :
  zéro partout, et pourtant le texte n'était pas centré. La mesure compare
  maintenant le milieu de chaque *ligne de texte* à celui du bloc — c'est la
  seule mesure qui décrit ce que l'œil voit.
- **Après correction :** écart de 0 px sur chaque ligne des droits et de la note,
  à 320, 390, 576, 720, 1 440, sur quatre pages, à 100 % et à 130 % de texte ;
  aucun débordement.
- **Un piège de garde-fou.** La première version du contrôle a échoué alors que
  la règle était bonne : le commentaire CSS citait lui-même une accolade, et
  l'expression régulière `[^}]*` s'arrêtait sur elle. Le commentaire a été
  réécrit sans accolades — les contrôles de ce fichier découpent les règles à
  l'accolade fermante.

Garde-fou : 13ᵉ contrôle `controler_pied_de_page`, étendu au centrage — découpage
absent du pied de page, ponctuation seule rattachée (et nœud non découpé quand
elle ouvre le texte), colonne centrée, **paragraphes du bas de page explicitement
centrés**, liste légale sans puce ni filet, borne de repli sur téléphone, liste
présente sur toutes les pages. **Sept mutations rejouées, sept détectées** :
`justify-items` retiré, liste réalignée à gauche, borne de téléphone supprimée,
filet vertical rétabli, retour à l'ancienne règle de ponctuation, centrage des
paragraphes retiré, puis remplacé par un alignement à gauche.

Limite : la mesure est celle d'un Chromium sans interface ; le rendu des filets
sur un écran à très forte densité reste à constater.

## 6 octies. « Écouter la page » : une commande qui tient dans le panneau (23 octobre 2026)

Le lot d'inclusion ajoute une commande de lecture à voix haute, en dernier dans
le panneau « Personnalisation ». Ce qui suit ne juge pas la voix — aucun banc
sans interface ne peut l'écouter — mais vérifie que la commande s'affiche sans
casser la mise en page, aux largeurs et aux crans de texte les plus serrés.

- **Ce qui était faux au premier jet.** « Arrêter la lecture » et « Reprendre »
  ne tenaient pas côte à côte dans 328 px : le second sortait du cadre. Un
  `flex-wrap` ne suffisait pas, car le bouton principal réclamait toute la ligne
  par sa base `auto` et repoussait la pause en dessous, seule sur sa ligne.
- **Correction mesurée.** Libellés courts (« Arrêter »), nom accessible complet
  conservé (`aria-label`), puis `flex: 1 1 0` sur le bouton principal et
  `flex: 0 0 auto` sur la pause. À 320 px et 130 % : bouton principal
  125 × 53 px, pause 148 × 53 px, les deux dans le panneau, débordement 0 px.
- **Ordre dans le panneau.** Intercalée entre « Affichage » et « Présentation »,
  la commande coupait le groupe des réglages en deux ; une capture l'a montré.
  Elle passe après « Présentation ». L'en-tête compact garde deux boutons.
- **Matrice relevée** (Chromium sans interface, 100 % et 130 %) : 320 × 568,
  390 × 780, 430 × 900, 667 × 375, 844 × 390, 768 × 1 024, 1 440 × 900 —
  panneau entièrement dans l'écran, contenu dans le panneau, `overflow-y: auto`,
  aucun débordement horizontal, aucune capture de texte hors cadre.
- **Contraste du bloc marqué.** Le bloc en cours de lecture reçoit un contour de
  3 px (`outline`, jamais `box-shadow` seul) et `Highlight` en mode contraste
  forcé : l'information reste perceptible quand les couleurs sont imposées.

Garde-fou : 15ᵉ contrôle `controler_lecture_a_voix_haute`. **Sept mutations
rejouées, sept détectées** : langue du bloc ignorée, arrêt sans annulation,
contenus masqués lus, `fetch` ajouté, marque visuelle supprimée, commande
construite mais jamais ajoutée au panneau. Les quatre premières versions du
contrôle étaient trop permissives — elles cherchaient une sous-chaîne au lieu de
l'appel réel, ou acceptaient un `outline` présent ailleurs dans la feuille.

Limite : la mesure porte sur la géométrie de la commande, pas sur le son. Une
voix absente, une prononciation fautive ou une pause qui ne reprend pas restent
possibles et ne se voient qu'à l'oreille.

## 6 nonies. Cibles de 24 px et focus non masqué (23 octobre 2026)

Deux critères WCAG 2.2 de niveau AA entreront dans le RGAA 5 ; ils se mesurent,
eux, dans un navigateur. `outils/auditer-criteres-22.mjs` les relève hors CI.

- **Taille des cibles (2.5.8).** Le relevé couvre **5 655 cibles conformes** sur
  98 pages aux deux largeurs, plus **901 en ligne** (liens dans une phrase) et
  **2 304 espacées** (exception de proximité), donc **0 à corriger**. Avant
  correction, 12 défauts réels subsistaient, tous dans le pied de page à 390 px :
  les liens légaux mesuraient 19 px de haut et se touchaient.
- **Correction.** `.footer-legal a` passe en `inline-flex` avec
  `min-height: 24px`; l'écart vertical du bloc tombe de 0,3 rem à zéro pour que
  la hauteur gagnée ne se voie pas. Mesuré : liens à 24 px (25 px à 130 %),
  centrage inchangé à 0 px, pied de page 430 px à 1 440 px contre 425 avant.
- **Focus non masqué (2.4.11).** Pour chaque cible atteignable, le script fait
  défiler en `instant`, porte le focus, puis teste cinq points du rectangle
  contre `elementFromPoint`. **8 856 éléments testés sur 98 pages, 0 entièrement
  masqué, 0 page coupée** (24 octobre 2026). Le plafond de 60 cibles et les huit
  pages du premier essai coupaient la passe en silence : `anglais-aventure.html`
  en compte 448, dont 60 seulement étaient portées au focus. Le plafond passe à
  500 — au-delà du maximum observé — et le bilan déclare désormais les pages
  coupées. Une page qui ne se charge pas est comptée comme un échec, et non
  comme « zéro défaut » : c'était un second piège du même outil.
- **Deux pièges de mesure, mesurés et corrigés dans l'outil.** Un défilement
  animé n'a pas fini au moment de la mesure et produit de faux « hors écran » :
  le défilement est forcé en `instant` et la feuille reçoit
  `scroll-behavior: auto`. Et le contenu d'un `<details>` refermé garde une
  boîte non nulle dans Chromium : il a produit 50 fausses alertes avant filtrage
  par `checkVisibility` et par `details:not([open])`.

Garde-fou : `.footer-legal a` entre dans les `CIBLES` vérifiées par
`verifier-affichages.py` (plancher de 24 px) ; retirer `min-height` fait échouer
le contrôle. Le contrôle de lecture à voix haute exige désormais
`checkVisibility` et `innerText` : les deux sont nécessaires, aucun ne suffit.

Limite : la mesure porte sur une géométrie, pas sur la difficulté réelle à viser
ni sur un audit complet ; la passe du focus couvre désormais toutes les cibles
des 98 pages (8 856 éléments), mais cinq points par élément ne disent rien de la
lisibilité du contour, et le recouvrement n'est testé qu'après un défilement que
la mesure provoque elle-même.

## 6 decies. Reculer et choisir son débit : deux gestes de plus dans le panneau (23 octobre 2026)

Un seul bouton « Lire à voix haute » ne laissait que deux issues : tout écouter
ou tout arrêter. Deux gestes manquaient, et ils se mesurent comme le premier :
dans le panneau, aux largeurs et aux crans de texte les plus serrés.

- **Ce que la page savait déjà faire, et pas encore montrer.** La lecture
  découpait la page en passages et savait où elle en était ; elle ne permettait
  ni de revenir en arrière ni de changer de rythme. Le lot ajoute un bouton
  « Reculer » et un sélecteur à quatre crans (0,75 / 1 / 1,25 / 1,5), le
  changement s'appliquant au passage suivant sans repartir du début.
- **Mise en page retenue.** Le groupe des commandes passe à quatre éléments :
  « Arrêter » 283 × 53 px, « Pause » 127 × 53, « Reculer » 145 × 53 et le
  sélecteur 153 × 44. Mesuré à 320 px et 130 % : les quatre tiennent dans le
  panneau, **débordement 0 px** ; contrôle répété à 390 px et 1 440 px, à 100 %
  comme à 130 %. « Arrêter » occupe la ligne pleine, les deux autres commandes
  se partagent la suivante, le sélecteur prend la troisième avec sa légende
  (« Vitesse de lecture »), hors de la cible tactile.
- **Le sélecteur garde une cible de 44 px** (`min-height`) : le gain de place ne
  se paie pas en précision. À 320 px et 130 %, aucune ligne de texte n'est
  tronquée ; la dernière ligne du panneau s'arrête sur une ligne pleine, sans
  coupure de mot.
- **Mémoire locale, une clé de plus.** `mrsc-lecture-vitesse` retient le cran
  choisi ; rien d'autre n'est écrit, aucun texte lu ni position de lecture. La
  page Vie privée nomme la clé, la note sous les commandes le dit en une phrase.
- **Le défaut qui a failli passer.** `speechSynthesis.cancel()` peut rappeler le
  rappel de fin d'une énonciation annulée. Sans jeton de génération, « Reculer »
  ou un changement de vitesse rejouait **deux** passages : 7 énonciations au
  lieu de 6, mesuré. Un compteur incrémenté à chaque démarrage et à chaque arrêt
  est comparé dans la fin **et** dans l'erreur ; l'essai navigateur simule
  exprès ce rappel fantôme.

- **Une coupe ne doit pas s'entendre finie (24 octobre 2026).** Les blocs longs
  sont découpés en morceaux de 220 caractères ; la coupe tombait sur une espace,
  donc au milieu d'une phrase, et le morceau se terminait sur un mot nu. Mesuré
  sur les **98 pages** du site, en attendant la fin réelle de chaque lecture :
  **46 segments sur 6 462** dans ce cas. Un moteur de synthèse enchaîne alors le
  morceau suivant comme un mot de plus, sans respiration. Chaque morceau coupé
  reçoit désormais une **virgule** — elle dit la continuation, là où un point
  inventerait une phrase qui n'existe pas — et cette virgule compte dans la
  limite : si le morceau fait déjà 220 caractères, son dernier mot repasse au
  morceau suivant. Après correction, **0 segment sur 6 462** finit sur un mot nu,
  et aucun ne dépasse 220 caractères.

Garde-fou : 15ᵉ contrôle `controler_lecture_a_voix_haute`, désormais **dix-sept
mutations rejouées, dix-sept détectées**. Sept concernent le premier lot (langue
du bloc ignorée, arrêt sans annulation, contenus masqués lus, `fetch` ajouté,
marque visuelle supprimée, commande construite mais jamais ajoutée au panneau,
nom accessible sans le texte visible) ; sept visent le second : vitesses
supprimées, débit ignoré, jeton de génération retiré des deux rappels puis d'un
seul, retour arrière retiré, vitesse non conservée, cible du sélecteur abaissée
de 44 à 24 px. Trois faiblesses du contrôle ont été trouvées en le mutant : il
cherchait `"data.readAloudBack"` là où le code lit `dataset.readAloudBack`,
bornait le module par un nombre de caractères — un ajout de fonction faisait
croire à une disparition — et se contentait de constater une `min-height` sans
comparer sa valeur.

Limite : la mesure porte sur la géométrie et sur un double de la synthèse, pas
sur le son. Aucun débit réel n'a été écouté, et personne n'a encore essayé ces
deux gestes ; le cran qui convient à une personne ne se déduit d'aucune mesure.

## 6 undecies. Les deux derniers héros passent en géométrie (24 octobre 2026)

Il restait deux illustrations bitmap dans le site : l'emblème de l'accueil et
l'atlas de `apprendre.html`. Le héros des Mondes était déjà un rendu 3D (§ 6 ter),
l'illustration d'« Apprendre » avait été désétirée (§ 6 ter bis) ; ces deux-là
n'avaient reçu qu'un correctif de variante. Elles deviennent des tracés SVG.

- **Ce que la mesure disait.** À 390 px et 3×, la boîte de l'emblème mesure
  366 × 202 px : l'écran demande 1 098 pixels de large, la source en fournissait
  1 400, donc le rendu était net à 1,3× et interpolé au-delà. Fournir une source
  plus large repousse la limite sans la supprimer — chaque écran plus dense la
  ramène. Un tracé, lui, se rastérise à la densité de l'écran.
- **Ce qui est livré.** `assets/images/accueil-embleme-mrsc.svg` (4 518 octets,
  1 292 compressés) reprend le langage de l'ancienne image — quatre arcs vert,
  or, ardoise et encre, joyau de verre facetté, sigle et mention — en dégradés,
  facettes et une ombre douce. `assets/images/atlas-savoirs.svg` (8 700 octets,
  2 203 compressés) remplace l'atlas : trois îles — bibliothèque, observatoire,
  phare — reliées par des chemins pointillés au-dessus d'un livre ouvert.
- **Ce que la mesure navigateur donne.** Quatre profils, deux pages :

| Page | Profil | Boîte | `viewBox` | Écart de ratio | Débordement |
| --- | --- | --- | --- | ---: | ---: |
| Accueil | 320 px @3× | 296 × 163 | 1 200 × 660 | 0,0022 | 0 px |
| Accueil | 390 px @3× | 366 × 202 | 1 200 × 660 | 0,0063 | 0 px |
| Accueil | 768 px @2× | 718 × 395 | 1 200 × 660 | 0,0005 | 0 px |
| Accueil | 1 440 px @1×, 2× et 3× | 1 158 × 637 | 1 200 × 660 | 0,0003 | 0 px |
| Apprendre | 320 px @3× | 258 × 161 | 1 600 × 1 000 | 0,0025 | 0 px |
| Apprendre | 390 px @3× | 328 × 205 | 1 600 × 1 000 | 0,0000 | 0 px |
| Apprendre | 768 px @2× | 305 × 190 | 1 600 × 1 000 | 0,0053 | 0 px |
| Apprendre | 1 440 px @1×, 2× et 3× | 497 × 311 | 1 600 × 1 000 | 0,0019 | 0 px |

L'écart de ratio reste sous 0,007 : `object-fit` ne recadre donc pas un dessin
dont la composition est centrée, et la place est réservée avant chargement par
les dimensions intrinsèques.

- **Un plafond de densité n'a plus de sens sur un tracé.** Les quatre paliers
  `min-resolution` (2, 2,5, 3 et 3,5 dppx) réduisaient l'emblème à 700, 560, 466
  puis 400 px : ils existaient uniquement pour ne pas étirer un bitmap de
  1 400 px. Depuis le passage au tracé, ils rapetissaient le dessin de moitié sur
  un écran 2× — mesuré : 698 px de large à 768 px @2× contre 1 158 px à
  1 440 px @2×. Ils sont retirés ; l'emblème occupe désormais toute la largeur de
  sa colonne à toutes les densités (1 158 px @1×, @2× et @3×, soit 1 158 unités
  de tracé pour 2 316 pixels d'appareil à 2×, sans interpolation). Les logos
  d'en-tête et de pied de page, qui restent des images, gardent leurs paliers de
  78 et 66 px.

- **Poids.** L'accueil passe de 153,5 à **75,9 Kio** en mobile comme en grand
  écran (251,8 Kio avant, sur grand écran) ; `apprendre.html` de 216,0 à
  **113,1 Kio** mobile et de 404,2 à 113,1 Kio grand écran, alors qu'elle était
  signalée « proche du budget ». Les cinq fichiers de l'ancienne image de
  l'accueil (813 782 octets) sont retirés du dépôt ; le manifeste de variantes,
  le générateur, le relevé d'en-têtes et la sonde de publication sont mis à jour
  en conséquence.

Garde-fou : le 7ᵉ contrôle `controler_illustrations` a été réécrit et renommé
« illustrations non agrandies, héros vectoriels ». Il exige, pour chacune des
deux figures, un seul `<img>`, pointant sur le bon SVG, avec un texte alternatif,
des dimensions intrinsèques égales à celles du fichier ; et, pour chaque SVG, un
`viewBox`, un `<title>`, l'absence de `<image>`, de `data:image/` et de
`<foreignObject>`, un poids sous 40 000 octets, et des attributs `width`/`height`
cohérents avec le HTML. Le ratio de la feuille est lu **dans la règle de la
figure** et comparé à celui du tracé. **Neuf mutations rejouées, neuf détectées** :
retour à un `<picture>` avec `srcset`, `src` faux, `alt` retiré, dimensions HTML
faussées, image base64 agrégée dans le SVG, ratio de la feuille passé à 16/9,
dimensions du SVG faussées, `title` retiré, `height: auto` retiré.

Le contrôle des plafonds de densité (6ᵉ) change de règle en même temps : il
refusait qu'un palier manque, il refuse désormais qu'un palier **s'applique à un
héros vectoriel**, et vérifie que les logos gardent les leurs. Deux mutations
rejouées, deux détectées : `max-width: 466px` réintroduit sur `.home-hero-visual`
dans le bloc `3dppx`, et bloc `3dppx` des logos supprimé.

La première version du contrôle lisait le ratio **n'importe où** dans la feuille :
elle validait donc un ratio appartenant à une autre règle. C'est la mutation
« ratio passé à 16/9 » qui l'a montré.

Limite : le rendu est net, pas nécessairement plus beau. Les deux tracés ont un
langage plat, sans grain ni profondeur de champ ; une personne peut préférer
l'ancienne image, et ce choix ne se tranche pas par une mesure. Aucun appareil
réel n'a été utilisé : les profils sont émulés dans un Chromium sans interface.

## 7. Ce qui n'est pas couvert

- **Police réelle.** La mesure utilise les polices installées dans
  l'environnement de mesure ; une police de substitution peut changer les
  retours à la ligne de quelques pixels.
- **Zoom du navigateur.** Le zoom est approché par une fenêtre plus étroite.
  C'est équivalent pour la mise en page, pas pour la netteté des images.
- **Recouvrement avec le réglage de texte.** Le plancher de 12 px ne s'applique
  qu'aux tailles déclarées par la feuille ; un agrandissement du texte par le
  navigateur reste hors de son contrôle.
- **Appareils physiques.** Aucun téléphone ni portable Retina réel n'a été
  utilisé : les formats sont émulés. Les captures produites pendant la mesure
  ont été relues, mais elles ne remplacent pas un contrôle à l'œil sur
  l'appareil.

## 8. Refaire la mesure

Le protocole complet est dans `outils/auditer-affichages.mjs` (facultatif, hors
CI : il demande Chromium). Il rend un tableau par page et par format, avec les
mêmes seuils que ceux décrits ici.

Les deux critères WCAG 2.2 se rejouent avec `outils/auditer-criteres-22.mjs`,
qui a besoin d'un serveur local sur son port (`python3 -m http.server 4187`).
Une passe complète — 98 pages × 390 et 1 280 px, focus compris — dure une
vingtaine de minutes ; `--sans-focus` ne mesure que la taille des cibles et
`--pages` limite le périmètre. Le script écrit son relevé en JSON, comme
[`audit-criteres-22-2026-10-24.json`](audit-criteres-22-2026-10-24.json).
