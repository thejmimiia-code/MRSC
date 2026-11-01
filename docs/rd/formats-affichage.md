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
qualité d'encodage des images (voir § 6 bis), décor du héros avec son repli
(voir § 6 ter) et espacement du texte (voir § 6 decies).

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

## 6 quinquies bis. Le panneau ne sort plus par la gauche en en-tête compact (28 octobre 2026)

Le tableau ci-dessus ne mesurait, sur ordinateur, que l'**en-tête agrandi**
(1 280 px : panneau à x = 912 ; 1 440 px : x = 1 072). Le cas « en-tête compact
sur ordinateur » n'avait jamais été relevé — c'est celui du signalement « le menu
part à gauche sur le mode ordinateur », où « Agrandir » se lit « randir » et
« Écouter la page » « ter la page ».

**Mesure de la capture** (capture système à 2×, panneau ouvert) : bord gauche de
la fenêtre à x = 202, bord droit du panneau à x = 811. Le panneau visible fait
donc 305 px CSS pour les 352 px que lui donne
`min(clamp(300px, 22rem, 380px), calc(100vw - 1rem))` : **47 px sortent de
l'écran par la gauche**. Deux indices confirment un rognage et non un décalage
du texte — le bord gauche du cadre ne se voit pas, et un fragment d'icône
subsiste devant chaque libellé.

**Cause :** `right: 0` ancre le panneau à son bouton. Dans l'en-tête compact, les
deux commandes se rangent au début de la barre, juste après le logo : le bouton
« Personnalisation » finit à ~305 px du bord gauche, moins que la largeur du
panneau. Dans l'en-tête agrandi, la rangée est centrée et le bouton se trouve
assez à droite pour que le panneau tienne.

**Correctif :** sous `@media (min-width: 761px) and (min-height: 561px)`,
`html.entete-compacte .customize-settings-panel { right: auto; left: 0 }` — le
panneau s'ouvre vers la droite, sous son bouton. La requête écarte elle-même les
deux formats qui gardent leur ancrage propre (`position: fixed; left: .5rem;
right: .5rem` sous 760 px et en paysage court) : sans ce double garde, la
spécificité de `html.entete-compacte` l'aurait emporté sur leurs règles et aurait
ramené le défaut sur téléphone. L'en-tête agrandi garde `right: 0`.

`controler_panneau_du_menu` vérifie désormais la bascule **et sa requête**.
Mutation rejouée : `right: auto; left: 0` remplacé par `right: 0` — détectée,
fichier restauré à l'identique.

Limite : aucun navigateur dans l'environnement de la correction ; la position est
déduite de la capture et de la feuille de style, pas re-mesurée. Reste à relever
une ligne « 1 280 × 900, en-tête compact » dans le tableau ci-dessus.

**Correctif du 30 octobre 2026 — la hauteur n'aurait jamais dû entrer dans la
requête.** Retour d'usage : « en mode réduit sur aperçu ordinateur depuis un
smartphone le menu est logé à gauche à moitié visible », capture à l'appui. Le
panneau ressortait de nouveau par la gauche, libellés rognés (« grandir »,
« arcours », « ffichage »).

La cause est la seconde moitié du garde écrit le 28 : `min-height: 561px`. Un
téléphone en « aperçu ordinateur » n'annonce pas une petite fenêtre, il annonce
une fenêtre **large et basse** — 980 × 4xx sur la capture. Elle dépasse donc
761 px de large sans atteindre 561 px de haut : la règle ne s'appliquait pas, le
panneau retombait sur `right: 0`, ancré à droite d'un bouton placé au début de
la barre, et sortait par la gauche. Le défaut du 28 octobre revenait par un mode
que la mesure du 28 n'avait pas visité.

La question n'est pas la hauteur, c'est la largeur : au-delà de 920 px, le format
« paysage court » n'existe plus (sa limite), donc le panneau a la place de
s'ouvrir à droite. La requête devient
`@media (min-width: 921px), (min-width: 761px) and (min-height: 561px)` — les
deux cas en ou, aucun autre format touché.

`test-experience.cjs` porte désormais un essai mesuré, « Aperçu ordinateur depuis
un téléphone : 980 × 440 », qui visite plusieurs formats, réduit l'en-tête comme
le fait l'utilisateur, puis exige que le panneau et ses lignes restent dans la
fenêtre. C'est la première fois que ce défaut est **re-mesuré** au lieu d'être
déduit d'une capture.

**Puis la troisième règle a été jetée (30 octobre 2026).** Retour d'usage, dans
la même heure : « il faut que ce soit adapté à chaque variable d'affichage, car
personne ne fait plus de plein écran constant ! Les gens règlent leurs fenêtres
en fonction de leurs usages et modulent constamment. Donc il faut que la gestion
soit dynamique et non sur des valeurs fixes. » C'était juste, et cela nommait le
défaut de méthode : depuis le 28 octobre, on empilait des points de rupture —
`right: 0`, puis `min-width: 761px and min-height: 561px`, puis `min-width:
921px` — et chacun laissait passer le format qu'on n'avait pas imaginé.

Les trois règles d'ancrage ont donc été **supprimées** de `site.css`. Le panneau
est placé par `placerPanneauPersonnalisation()` dans `site.js` :

| Ce qui est mesuré | Ce qui en est fait |
| --- | --- |
| largeur de la fenêtre (`visualViewport` s'il existe) | largeur bornée à la fenêtre moins deux marges de 8 px |
| bord droit du bouton | panneau aligné à droite dessus ; s'il sort à gauche, aligné à gauche du bouton ; puis borné aux marges |
| bas de l'en-tête | panneau posé dessous, hauteur bornée pour laisser au moins 160 px visibles, défilement interne au-delà |

Le calcul est refait à **chaque ouverture** et à chaque changement : `resize`,
`orientationchange`, `visualViewport` (`resize` et `scroll`, donc la barre
d'adresse du téléphone et le clavier virtuel), et `ResizeObserver` sur l'en-tête
(texte agrandi, en-tête réduit). Aucune de ces causes n'est un format nommé.

Ce qui reste dans la feuille de style est un **repli**, pas une décision :
position absolue sous le bouton, largeur souhaitée, défilement interne. Si le
script ne s'exécute pas, le panneau reste lisible.

Deux contrôles, à deux niveaux :

- `outils/test_placement_panneau.mjs` extrait la vraie fonction de `site.js` et
  l'exécute dans un contexte simulé (`node:vm`), **sans navigateur** : 3 600
  positions — toutes les largeurs de 240 à 2 560 px par pas de 40, cinq
  hauteurs, trois positions de bouton, avec et sans `visualViewport`. Il exige
  que le panneau reste dans la fenêtre, que sa hauteur visible ne descende pas
  sous 160 px, et que son bord droit suive le bouton quand la place le permet.
  Il a trouvé un défaut que personne n'avait vu : fenêtre de 320 px, en-tête de
  180 px, le panneau dépassait de 8 px par le bas — la borne de hauteur ne
  réservait pas la marge.
- `test_mutations_affichages.py` (8 mutations) vérifie que `verifier-affichages.py`
  refuse un placement qui perd sa borne en largeur, son écoute de la fenêtre
  visuelle, son rebranchement à l'ouverture, ou qu'une règle de format
  réintroduit un ancrage fixe.
- `test-experience.cjs` mesure, lui, un vrai Chromium : huit formats à
  l'ouverture, puis **quatre redimensionnements panneau ouvert** (élargi,
  écrasé en hauteur, rétréci en largeur, plein écran) — c'est la promesse
  dynamique, mesurée.

**Ce que ces contrôles ont trouvé, et qui ne se voyait pas à la lecture :**

| Trouvé par | Défaut |
| --- | --- |
| `test_placement_panneau.mjs` (sans navigateur) | la borne de hauteur ne réservait pas la marge du bas : fenêtre 320 px, en-tête 180 px → dépassement de 8 px |
| CI, essai à 980 × 440 | le panneau gardait les coordonnées de l'en-tête **agrandi** (left = −203 px) : réduire l'en-tête déplace le bouton, et le `ResizeObserver` de l'en-tête ne suffisait pas |
| CI, essai à 800 × 500 | panneau ouvert **sans aucun style en ligne** : Chromium restaure `<details open>` après `load`, sans émettre `toggle` |

Les deux derniers sont traités à la source : `setHeaderCompact` replace
explicitement après avoir rangé les commandes, et un `MutationObserver` sur
l'attribut `open` attrape la restauration du navigateur comme un clic.

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

### Quatrième passage : la mention d'impression sur sa propre ligne (25 octobre 2026)

Signalement, capture à l'appui : « la phrase commence juste derrière le point et
se retrouve coupée » — la mention « Une copie imprimée n'est pas une version
certifiée » s'affichait au milieu d'une ligne centrée, coupée après « Une copie
imprimée ».

- **La cause est la phrase elle-même, pas son alignement.** Elle était écrite à
  la suite de « Boussole des savoirs », dans le même paragraphe : le retour à la
  ligne du centrage tombait donc au milieu d'elle, et le point de la phrase
  précédente semblait l'introduire.
- **Deux corrections liées.** La mention devient un `<span class="footer-rd-print">`
  en `display: block` avec `text-align: start`, et le paragraphe cesse d'être
  borné à 72 ch dans le bas de page (`.footer-bottom .footer-rd { max-width: none }`) :
  la ligne démarre au bord gauche du conteneur, à l'aplomb du reste du site,
  tandis que la note de version au-dessus garde son centrage.
- **Le balisage se dégrade proprement.** Sans la feuille de style, le `<span>`
  reste en ligne et la phrase redevient celle d'avant, avec une espace devant
  elle : aucune page ne dépend du CSS pour rester lisible.
- **Le filet du bloc s'élargit.** Il suivait les 72 ch du paragraphe ; il couvre
  maintenant la largeur du conteneur, comme celui du bloc du bas au-dessus de
  lui. C'est un effet de bord assumé du `max-width: none`.
- **Ce que cette mention ne fait pas.** Elle ne s'imprime pas : la règle
  `@media print` masque `.site-footer` en entier. Une copie papier ne porte donc
  ni les droits, ni la licence, ni cette phrase. Le constat est consigné ici ; il
  n'est pas corrigé dans ce passage.

Garde-fou : le 13ᵉ contrôle est étendu — la règle `.footer-rd-print` doit porter
`display: block` et `text-align: start`, le paragraphe du bas de page doit
conserver `max-width: none`, et **les 13 pages racine comme les 85 fiches**
doivent porter le `<span>`. Le générateur de fiches et les pages racine sont donc
tenus ensemble : un seul des deux mis à jour fait échouer la porte. **Deux
mutations rejouées, deux détectées** : `<span>` retiré d'`index.html`, puis
`display: block` et `text-align: start` retirés de la règle CSS.

Limite : aucune mesure au navigateur cette fois — Chromium n'était pas
disponible dans l'environnement de travail. Le raisonnement porte sur la cascade
(`.footer-bottom .footer-rd` l'emporte par spécificité sur `.footer-rd`) ; le
rendu réel reste à constater sur écran, notamment le voisinage d'une ligne
centrée et d'une ligne calée à gauche.

### Cinquième passage : la copie papier porte enfin son adresse (25 octobre 2026)

Même signalement, suite. La feuille d'impression promettait depuis le 16 octobre
« Copie du site M.R.S.C. — *adresse* — à relire, pas une version certifiée »,
lue dans `attr(data-print-url)`. **Aucune page n'écrivait cet attribut.** La
ligne s'imprimait donc avec un tiret vide, et la licence du site — usage libre,
**attribution obligatoire avec citation de l'adresse** — n'était pas respectée
sur papier. Aucun contrôle ne portait sur la feuille d'impression.

- **Une source unique.** `data-print-url` est écrit dans la balise `<html>` de
  chaque page **à partir de sa canonique**, pas recopié : sur les pages racine,
  par un passage unique vérifiable ; sur les 85 fiches et `apprendre.html`, par
  `outils/construire-apprentissages.py` ; sur la page du simulateur, par
  `outils/construire-simulateur.py` dans sa couche d'intégration, le moteur
  amont restant intact. `404.html` n'a pas de canonique et reçoit son adresse
  publiée.
- **Ce que la ligne dit maintenant.** Source et adresse de la page, rappel de la
  licence avec son adresse complète, et le statut : « cette copie n'est pas une
  version certifiée : le statut à jour est celui de la page en ligne ». Le pied
  de page reste masqué en impression, parce que ses liens relatifs y seraient
  morts ; la ligne le remplace.
- **Pas de JavaScript dans la chaîne.** L'adresse est dans le HTML servi : une
  impression sans script, un lecteur qui exporte en PDF ou une impression vers
  une imprimante réseau donnent le même texte.
- **Un domaine figé, mais surveillé.** L'adresse de licence est écrite en clair
  dans la feuille. Le contrôle compare sa base à celle des canoniques : changer
  de domaine sans toucher la feuille fait échouer la porte au lieu de laisser
  une attribution pointer vers l'ancien site.
- **Ce qui n'est toujours pas dit sur papier.** Les mentions de droits du pied
  de page (« © … Tous droits réservés ») et la liste des liens légaux restent
  hors de la copie : la ligne renvoie à la licence en ligne. Cette omission est
  assumée ici, pas corrigée.

Garde-fou : le 13ᵉ contrôle, renommé « pied de page et copie imprimée », vérifie
la présence de `html::after` dans `@media print`, son contenu (`attr(data-print-url)`,
l'adresse de licence, la mention de non-certification), l'attribut sur **les 98
pages publiées**, l'égalité entre cet attribut et la canonique de chaque page, et
l'accord entre la base des canoniques et celle citée dans la feuille.
**Quatre mutations rejouées, quatre détectées** : attribut retiré d'une page
racine, attribut retiré d'une fiche, adresse d'impression remplacée par un autre
domaine, `attr(data-print-url)` retiré de la feuille.

Limite : le contrôle lit le CSS et le HTML, il n'imprime rien. Le rendu papier —
saut de page, position de la ligne sous un contenu long — reste à constater sur
une impression réelle, ce que cet environnement ne permet pas.

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
> **Décision retirée le 24 octobre 2026 après rejet des visuels.** Les chiffres de cette section décrivent la version abandonnée. Voir [la ligne graphique et le protocole de restauration](ligne-graphique.md).

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

## 6 decies. Espacement du texte : ce que le critère 1.4.12 casse (24 octobre 2026)

Le critère `1.4.12` (AA depuis WCAG 2.1) ne demande pas d'afficher un texte
espacé : il demande de supporter qu'une personne impose elle-même **interligne
1,5**, **interlettrage 0,12 em**, **espacement des mots 0,16 em** et **2 em après
chaque paragraphe**, sans perte de contenu ni de fonction. C'est le seul des
critères mesurés ici qui éprouve la mise en page plutôt que des éléments.

`outils/auditer-criteres-22.mjs` applique ces quatre valeurs en `!important`
après chargement, puis cherche deux pertes : une page qui se met à défiler
horizontalement, et un texte rogné par un ancêtre en `overflow: hidden` ou
`clip`. Le texte est cherché **par nœud** : un `overflow` sur un bloc décoratif ne
roge aucun texte, alors qu'un titre coupé en deux est une perte de contenu. Un
conteneur qui défile volontairement (`auto`, `scroll`) n'est pas compté.

Mesure du 24 octobre 2026, 98 pages × 390 et 1 280 px, soit 196 relevés :

| Défaut | Où | Amplitude | Correction |
| --- | --- | --- | --- |
| Barre de navigation hors cadre | toutes les pages, 1 261 à 1 366 px | **47 à 56 px**, « Nous contacter » hors de la fenêtre | `flex-wrap: wrap` sur `.nav-links` (la ligne reste unique tant qu'elle tient) |
| Bouton de la colonne latérale hors page | **84 fiches**, 1 280 px | **22 px** | `white-space: normal` sur `.learning-lesson-aside .button`, `nowrap` conservé partout ailleurs |

Ce que la correction change à l'œil : entre 1 261 et 1 366 px, sous l'espacement
du critère, la barre de navigation occupe **deux lignes centrées** — les dix
entrées, puis « Nous contacter » — au lieu de déborder. Aucune entrée n'est
supprimée, raccourcie ni masquée, et le repli n'apparaît que dans cette bande de
largeur, sous cet espacement : ailleurs, la ligne reste unique. Sur téléphone, le
panneau ouvert garde ses dix entrées sur une seule colonne (`flex-wrap: nowrap`
en colonne), mesuré à 390 px avec et sans l'espacement du critère.

**Piège de mesure.** La page ne signalait aucun défilement horizontal quand la
barre sortait du cadre : le débordement partait des deux côtés d'un conteneur
centré, et `scrollWidth − clientWidth` restait nul. Un contrôle de débordement
seul aurait conclu « rien à signaler ». C'est la position réelle de chaque
élément, puis le cadre de chaque nœud de texte, qui ont montré les deux défauts.

Après correction : **0 débordement sur 196 relevés, 0 texte rogné** ; les 84
fiches ont été repassées une à une aux deux largeurs, 0 débordement. La taille
des cibles (5 655 conformes) et le focus (8 856 éléments testés) sont inchangés.

Garde-fou : le **16ᵉ** contrôle de `verifier-affichages.py` exige `flex-wrap` sur
`.nav-links`, `white-space: normal` sur le bouton de la colonne latérale et les
trois valeurs d'espacement du réglage « espacement renforcé » (interligne ≥ 1,5 ;
interlettrage ≥ 0,12 em ; espacement des mots ≥ 0,16 em). Trois mutations jouées,
trois détectées : retrait de `flex-wrap`, interlettrage ramené à 0,06 em,
interligne ramené à 1,3.

Limite : la mesure voit un rognage et un débordement, pas une perte de sens. Un
chevauchement partiel, une coupure de mot, un texte masqué par un `clip-path`
sans `overflow`, un contenu déplacé hors du champ visible sans déborder restent
hors de portée. Une ellipse assortie d'un moyen de révéler le texte est admise
par le critère : le dépôt n'en utilise aucune. Et rien ici ne remplace une
lecture par une personne qui a réellement besoin de cet espacement.

## 8. Refaire la mesure

Le protocole complet est dans `outils/auditer-affichages.mjs` (facultatif, hors
CI : il demande Chromium). Il rend un tableau par page et par format, avec les
mêmes seuils que ceux décrits ici.

Les trois critères WCAG se rejouent avec `outils/auditer-criteres-22.mjs`, qui a
besoin d'un serveur local sur son port (`python3 -m http.server 4187`). Une passe
complète — 98 pages × 390 et 1 280 px, taille des cibles, focus et espacement
compris — dure une vingtaine de minutes ; `--sans-focus` ne mesure que la taille
des cibles et l'espacement, `--sans-espacement` retire l'espacement, et
`--pages` limite le périmètre. Le script écrit son relevé en JSON, comme
[`audit-criteres-22-2026-10-24.json`](audit-criteres-22-2026-10-24.json).

## Contrôle graphique après restauration — 24 octobre 2026

Les deux images antérieures sont restaurées, sans redessin ni agrandissement.
La méthode, les seuils, la matrice de 3 780 relevés et les limites sont décrits
 dans [ligne-graphique.md](ligne-graphique.md). Le résultat reproductible est
conservé dans [audit-graphismes-2026-10-24.json](audit-graphismes-2026-10-24.json).
Ce contrôle ciblé ne remplace pas une vérification de tous les visuels du site.

## 9. La dette des valeurs fixes, comptée (31 octobre 2026)

Le lot du 30 octobre a retiré **un** panneau des points de rupture. Une règle
locale n'est pas une règle : la feuille contenait 66 blocs `@media` et personne
ne savait combien supposaient une taille d'écran. `outils/compter-paliers.py` les
compte, et `docs/rd/paliers-affichage.toml` porte la raison de chacun.

| Classe | Conditions | Blocs | Ce qu'elle présume |
| --- | --- | --- | --- |
| `format` | 17 | 35 | une largeur, une hauteur ou une orientation — donc un écran |
| `preference` | 8 | 21 | un réglage de la personne, la densité ou l'impression — aucune taille |

Sur les 17 conditions de format, **15 sont en dette** et 2 sont assumées : les
planchers de survie à 240 et 300 px, en dessous desquels il n'existe plus
d'appareil, seulement un cadre d'aperçu. La dette la plus lourde est
`(max-width: 760px)`, **onze blocs** : c'est ce seuil qui décide que le site est
sur téléphone, et il n'a jamais été mesuré.

Ce tableau a été recopié à la main une fois de trop : il annonçait encore 45
blocs de format et quinze blocs à 760 px quand le relevé du 1er novembre 2026 en
comptait 35 et onze. Le chiffre qui fait foi est la sortie de
`compter-paliers.py --releve`, pas cette ligne.

Deux conditions vivaient écrites de deux façons — `(max-width:760px)` à côté de
`(max-width: 760px)`, `(forced-colors:active)` à côté de
`(forced-colors: active)`. Elles sont réécrites ; le contrôle refuse désormais
deux écritures d'une même condition, parce qu'elles compteraient double.

Ce que ce compte ne fait pas : il ne juge pas les raisons, et il ne dit pas
combien de personnes voient quel palier. Il rend seulement l'ajout coûteux —
« un palier de plus est un écran de plus que le site présume » — et la baisse
visible, avec l'obligation de la dater. La résorption passe par les grilles
(`auto-fit`, `minmax`), qui n'ont besoin d'aucune condition, puis par le seuil
1260/1261 px tenu à la main en deux endroits.

## 10. Sortir des paliers par le calcul (31 octobre 2026)

Compter la dette ne dit pas comment la résorber. `outils/modele-grilles.py`
reconstitue la cascade réelle d'une grille — règle de base, puis chaque `@media`
qui la reprend, dans l'ordre du fichier — et calcule le nombre de colonnes à
chaque largeur de fenêtre :

    colonnes(W) = max(1, floor((C(W) + g) / (N + g)))     avec C(W) = min(1160, W − 48)

La règle de conversion est unique : on prend le **plus large** minimum de piste
qui laisse encore `k` colonnes au conteneur maximal. Des cartes larges se lisent
mieux, et le repli se produit exactement quand la largeur ne suffit plus — pas à
une largeur ronde choisie d'avance.

| Grille | Avant | Après |
| --- | --- | --- |
| `.principle-grid` | 4 col., puis 2 sous 1 000 px, 1 sous 520 | `minmax(min(270px, 100%), 1fr)` |
| `.ai-fraud-grid` | 3 col., puis 2 sous 1 000 px, 1 sous 760 | `minmax(min(370px, 100%), 1fr)` |
| `.ai-fraud-steps` | 4 col., puis 2 sous 1 000 px, 1 sous 760 | `minmax(min(270px, 100%), 1fr)` |
| `.home-voice-grid` | 3 col., puis 2 sous 1 000 px, 1 sous 760 | `minmax(min(370px, 100%), 1fr)` |

Quatre blocs `@media` disparaissent — trois `(max-width: 1000px)`, un
`(max-width: 520px)` — et le compteur de paliers passe de 45 à 41 blocs de
format. La conversion ne « reproduit » pas l'ancienne cascade : elle insère
l'étape que la cascade sautait. Sous 1 000 px, `.principle-grid` montrait deux
cartes de 468 px là où trois de 306 tenaient ; elle en montre trois.

`docs/rd/grilles-dynamiques.toml` engage chaque grille sur trois points que
`--verifier` contrôle : `auto-fit` dans la règle de base, minimum égal à celui
que la règle donne, et **aucun `@media` qui réimpose un nombre de colonnes** —
celui-là annulerait la conversion sans changer un caractère de la règle de base.

Limites : le modèle ne lit que la présentation par défaut (`--content: 1160px`),
réduit un bloc `(orientation: landscape) and (max-height: 560px)` à sa largeur
maximale, suppose le conteneur `min(1160, W − 48)` et ignore toute grille hors de
`.container`. Il calcule des largeurs de piste, pas la lisibilité d'une carte.

## 11. Douze grilles, et deux compteurs corrigés (31 octobre 2026)

Après la première conversion de quatre grilles, le modèle comptait « 32 grilles
restantes ». **C'était faux par excès** : il cherchait un `repeat(...)` n'importe
où dans la valeur, si bien qu'un panneau texte + bouton (`minmax(0, 1fr) auto`)
ou un formulaire à bouton (`minmax(180px, 1.5fr) repeat(2, minmax(160px, 1fr)) auto`)
s'annonçaient convertibles. **34 grilles sont à pistes inégales** : `auto-fit`
ne sait pas les produire, elles gardent leurs paliers, et le rapport le dit
maintenant.

### Deux règles, parce qu'il y a deux questions

| Colonnes de conception | Règle | Pourquoi |
| --- | --- | --- |
| 3 et plus | plus large minimum qui garde `k` colonnes au conteneur maximal | il y a des étapes intermédiaires : on garde la forme au plus large et les cartes les plus larges possible |
| 2 | minimum qui replace le repli **là où la cascade le plaçait** | il n'y a aucune étape : la seule information de conception est le moment où l'on renonce à la paire |

Appliquer la première règle aux grilles à deux colonnes aurait replié
`.document-grid` dès 1 027 px de fenêtre au lieu de 760 — une régression
visible sur un ordinateur portable.

### Converties le 31 octobre 2026

`.ai-metric-grid` et `.ai-forms-grid` (4 col., 270 px), `.ai-lives-grid` (3, 370),
`.learning-catalogue-grid` (3, 370), `.learning-level-grid` et
`.learning-ecosystem-grid` (4, 270), `.link-grid` (3, 370),
`.learning-code-grid` (2, 470, seuil 1 000 px recopié). Avec les quatre du lot
précédent : **douze grilles**, onze restantes.

### Ce que les compteurs ne voyaient pas

`compter-paliers.py` comptait des **blocs** `@media`, pas les règles qu'ils
décident : douze conversions, et le relevé annonçait toujours « 41 blocs, dette
inchangée ». Il compte désormais les règles — **214 → 205** — et refuse leur
hausse comme leur baisse non datée.

`modele-grilles.py` portait deux minima pour la même grille, sous le même mot
(« recommandé ») : l'ajustement à l'ancienne cascade et la règle de conception.
Huit grilles ont d'abord été écrites avec le premier. C'est le contrôle
(`--verifier`), qui recalcule la règle, qui l'a arrêté.

## 12. Neuf grilles à deux colonnes, et ce que le modèle ne comptait pas (31 octobre 2026)

Les neuf grilles restantes de la famille « deux colonnes » avaient un palier à
760 px. La règle des deux colonnes donnait un minimum unique de 350 px. Il
aurait produit, sur `.document-grid`, **trois colonnes dès 1 130 px de conteneur
et une carte orpheline** : le modèle calculait des largeurs de piste sans savoir
combien d'éléments les pages mettent dans la grille.

### Trois branches, pas deux

| Cas | Règle |
| --- | --- |
| `k ≥ 3` colonnes | plus large minimum qui garde `k` colonnes au conteneur maximal |
| 2 colonnes, **plus de deux éléments** | repli là où la cascade renonçait, puis minimum relevé juste assez pour que trois colonnes ne tiennent pas |
| 2 colonnes, **deux éléments** | repli seulement : `auto-fit` replie la piste vide, aucune troisième colonne ne peut apparaître |

La capacité (`items`) est **mesurée** dans les pages et revérifiée à chaque
contrôle ; une balise `dl` est reconnue comme liste de paires, qu'une troisième
colonne couperait.

| Grille | éléments | minimum | écart mesuré avec la cascade |
| --- | --- | --- | --- |
| `.eva-listes-grid`, `.simulateur-duo`, `.ai-balance-grid` | 2 | 350 px | nul |
| `.document-grid`, `.home-action-grid` | 4 | 380 px | 6 largeurs sur 233 |
| `.knowledge-compass` | 10 | 380 px | 6 largeurs sur 233 |
| `.simulateur-chiffres`, `.simulateur-passeport`, `.ai-fraud-lesson-list` | 6, 4, 5 | 380 px | 6 largeurs sur 233 |

### Deux lectures muettes corrigées

- `gap: .75rem 1.1rem` = 12 px entre les lignes, **17,6 px entre les colonnes**.
  Le modèle prenait le premier nombre ; deux grilles déclaraient un écart faux.
- Un `@media` **vide** — trois blocs laissés sans règle après conversion —
  faisait attribuer les règles suivantes à cette condition. Le rapport est passé
  de 33 grilles à 16, huit conversions comprises, sans un mot. L'analyseur tient
  désormais une pile de blocs refermée sur les accolades.

## 13. La dernière grille égale quitte son palier (31 octobre 2026)

`.ai-path-steps` — les cinq étapes du parcours de la page IA — était la dernière
grille à pistes égales dont le nombre de colonnes dépendait encore d'une largeur
d'écran : cinq colonnes, puis `repeat(3, …)` sous 520 px, avec
`li:last-child { grid-column: 2 }` pour recentrer la cinquième étape.

La règle donne **220 px** : le plus large minimum qui laisse encore cinq
colonnes à 1 160 px de conteneur. Les deux règles du palier de 520 px
disparaissent ensemble — le recentrage n'a plus de sens quand le nombre de
colonnes suit la largeur de piste. Mesure avant conversion : **94 largeurs sur
233** changeaient de nombre de colonnes, écart maximal **3 colonnes** — c'est le
prix, et il est dit : sous 520 px l'ancienne cascade montrait trois étapes par
ligne, la nouvelle en montre une quand la place ne suffit plus (cartes de 59 px
de large à 240 px de fenêtre auparavant).

**État : 22 grilles dynamiques, aucune grille à pistes égales sous palier de
largeur.** 34 grilles restent à pistes inégales, assumées et déclarées non
convertibles, et **195 règles** restent sous condition de largeur (214 avant ces
trois lots).

## 14. La déclaration qui ne décide rien (31 octobre 2026)

Deux journées de suite, le journal a porté la même limite : le compteur de
règles ne voit pas un sélecteur mort **à l'intérieur** d'une règle vivante.
`.contact-grid` a vécu dans un bloc de 760 px pour y réimposer une colonne à une
grille déjà à une colonne, et le compte n'a pas bougé quand la déclaration a été
retirée.

`modele-grilles.py` recalcule maintenant, pour chaque déclaration de colonnes
sous condition de largeur, la valeur **en vigueur à cette largeur en l'excluant
elle-même**, et compare les écritures normalisées. Si les deux sont identiques,
la déclaration ne décide rien et `--verifier` échoue. Mesure du jour : **zéro**
sur les 67 grilles de la feuille — c'est donc une garde, et le banc en éprouve le
déclenchement.

Ce qu'elle ne voit pas : une déclaration neutralisée par une règle postérieure
de même spécificité hors condition de largeur, et une déclaration dont la valeur
diffère mais dont l'effet est nul.

## 15. Ce qui doit rester fixe se déclare (31 octobre 2026)

Le registre `docs/rd/grilles-dynamiques.toml` disait quoi convertir ; il ne disait
pas ce qui doit **rester fixe**. La distinction ne pouvait pas venir du code :
`.layout-choice-preview` dessine, dans le panneau Personnalisation, une vignette
par présentation — trois colonnes sur deux rangées pour « Mosaïque ». Cette forme
**est** l'information ; une largeur de piste la détruirait.

La section `[[grille_fixe]]` déclare donc sélecteur, nombre de colonnes et
raison. `--verifier` refuse trois choses : une grille déclarée fixe qui
disparaît, une qui passe en largeur de piste, une qui change de nombre de
colonnes. `--regle` ne leur propose plus de conversion et les nomme à part.

Au passage, une erreur de classement corrigée : `repeat(3, 1fr)` et `1fr 1fr`
étaient lues comme des pistes **inégales**, faute d'être écrites avec `minmax`.
Le compte passe de 34 à **30** grilles inégales, et de 33 à **36** grilles à
pistes égales.

## 16. Mesurer avant d'écrire : `flex-wrap` sur les pistes inégales (31 octobre 2026)

Les 30 grilles à pistes inégales gardent leurs paliers — mais est-ce un
raccommodage ou la seule façon de tenir deux colonnes de largeurs différentes ?
`modele-grilles.py --pistes` répond en trois familles, **sans toucher à la
feuille** :

| Famille | Nombre | Ce que cela veut dire |
| --- | --- | --- |
| `contenu` | 14 | une piste `auto` / `max-content` : le repli dépend du **texte**, aucun modèle ne le tranche sans navigateur |
| `proportion` | 15 | un `flex: <g> 1 <plancher>px` reproduirait le rapport ; l'écart avec la cascade est calculable |
| `motif` | 1 | `repeat(…)` imbriquée : rien à rendre dynamique |

Écarts mesurés sur 233 largeurs : **4** pour `.ai-hero-grid`, 13 à 18 pour
`.hero-grid`, `.participation-grid`, `.learning-work-panel`, `.english-promo-panel`,
24 à 32 pour `.learning-article-layout`, `.ai-questions-layout`, `.map-layout`,
et **179 à 221** pour `.ai-feature-panel`, `.simulateur-promo-panel`,
`.learning-coverage-topic`. **11 grilles** changent de colonnes sur moins d'un
huitième du balayage : ce sont les seules qu'un `flex-wrap` remplacerait sans
redessiner.

Deux erreurs de calcul ont été corrigées avant d'écrire quoi que ce soit :
comparer à `colonnes_anciennes` (qui répond toujours « 1 » pour une grille
inégale) et oublier la borne par la capacité mesurée. Ce sont les deux erreurs
qui avaient coûté deux journées sur les grilles égales.

## 17. Première grille à pistes inégales convertie en `flex-wrap` (31 octobre 2026)

`.ai-hero-grid` — texte et constellation de la page IA — portait un palier à
760 px qui la repliait d'un coup. Elle se replie désormais quand ses deux
panneaux de 330 px ne tiennent plus :

```css
.ai-hero-grid { display: flex; flex-wrap: wrap; gap: clamp(2rem, 5vw, 4.5rem); }
.ai-hero-grid > :first-child { flex: 1.05 1 330px; min-width: 0; }
.ai-hero-grid > :last-child  { flex: 0.95 1 330px; min-width: 0; }
```

**Coût mesuré :** 2 largeurs sur 233 changent de nombre de colonnes ; une colonne
peut varier de 16,5 px (4,9 %) au plus, parce que `flex` ne partage que le
surplus au-dessus du plancher là où la grille partageait tout par `fr`.

### Le piège : une présentation qui ne replie plus rien

La présentation « Lecture » repliait cette grille par
`grid-template-columns: minmax(0,1fr)`. Sur un conteneur **flex**, cette
déclaration est sans effet — la présentation aurait annoncé une colonne sans en
produire. Elle passe par `flex-basis: 100%`, et `--verifier` refuse désormais
qu'une présentation impose `grid-template-columns` à une grille convertie.

### Deux lectures corrigées au passage

- `gap: clamp(2rem, 5vw, 4.5rem)` était lu comme 16 px (ou tronqué en
  `clamp(2rem,`). L'écart dépend de la fenêtre : il est désormais évalué largeur
  par largeur, et une expression illisible rend `None` au lieu de 16.
- `minmax(230px, 300px)` a un **plafond** en pixels, que `flex` ne sait pas
  reproduire : six grilles passent de « proportion » à « borne ».

État : 22 grilles dynamiques, 5 fixes déclarées, 1 en `flex-wrap`,
**194 règles** sous condition de largeur (214 en début de journée).

## 18. Deuxième grille inégale, et les déclarations mortes d'un conteneur flex (31 octobre 2026)

`.english-promo-panel` passe en `flex-wrap` (280 px de base par panneau) :
**13 largeurs sur 233** changent de nombre de colonnes, une colonne peut varier
de **14 px (5 %)** au plus.

Le palier `@media (min-width: 761px)` portait deux déclarations : le plafond de
l'illustration, indispensable à sa déclaration `sizes`, et `justify-items: start`
sur la grille. La seconde ne décide plus rien en flex — mais elle restait une
règle, donc du travail compté. `--verifier` refuse désormais, sur une grille
déclarée en `flex-wrap`, toute règle qui lui applique `grid-template-columns`,
`grid-template-rows`, `grid-auto-flow` ou `justify-items`.

`.participation-grid` mesure **28 px (9,9 %)** d'écart : retenue, pas convertie,
et le chiffre est écrit pour que la décision ne se prenne pas au jugé.

État : 22 grilles dynamiques, 5 fixes, **2 en `flex-wrap`**, 12 « proportion » et
6 « borne » restantes, **192 règles** sous condition de largeur (214 en début de
journée).

## 19. Un plafond n'est pas une largeur : `max-width` sur une boîte flexible (31 octobre 2026)

Le plafond de `.english-promo-art` était écrit `width: min(100%, 520px)`, et il
tenait : dans une **grille**, un élément garde la largeur qu'on lui donne, la
piste se contentant de le contenir. Dès que ses présentations passent les
panneaux à `flex-basis: 100%`, la largeur de la boîte **vient du `flex-basis`** :
le plafond en `width` cesse d'agir sans disparaître, et rien dans la feuille ne
le signale.

Conséquence mesurée, pas supposée : en présentation Lecture à 1024 px, l'image
remontait à **879 px**, le navigateur — qui croyait encore la déclaration
`sizes` à 520 px — servait la variante de 800 px, et la densité tombait à
**0,91**. Le contrôle navigateur l'a vu (`densité insuffisante`) ; le modèle
statique, non.

D'où deux règles, désormais contrôlées :

1. un plafond destiné à rendre vraie une déclaration `sizes` s'écrit
   **`max-width`** — cette propriété s'applique à la taille principale d'une
   boîte flexible (CSS Flexbox, § 9.2), contrairement à `width` ;
2. `modele-grilles.py --verifier` refuse un `width: min(100%, Npx)` posé sur un
   **enfant direct** d'une grille déclarée en `flex-wrap`, en le nommant : la
   ligne, la classe et la propriété à écrire. Les enfants sont lus dans les
   pages HTML, pas devinés : une grille absente des pages est dite non mesurée.

Limite : le contrôle ne voit que la forme `min(100%, Npx)`. Un plafond écrit
`width: 520px`, `width: 65ch` ou `inline-size` lui échappe encore, et une
présentation qui plafonnerait autrement qu'en `flex-basis` aussi.

## 20. Troisième grille inégale : lire la plage, pas le compte (31 octobre 2026)

`.ai-path-panel` (page IA) passe en `flex-wrap` : `0.9fr` / `1.1fr`, 320 px de
base commune. Son palier `@media (max-width: 1000px)` ne portait que cette
grille et disparaît en entier — 37 blocs, 191 règles.

**La leçon de méthode est plus importante que la conversion.** Le relevé disait
« 29 largeurs sur 233 diffèrent de la cascade » : un compte, sans lieu. Deux
grilles au compte voisin pouvaient donc cacher des conséquences opposées, et
c'est exactement ce qui s'était produit.

`modele-grilles.py --pistes` imprime désormais la **bande** :

```
.ai-path-panel     plancher 320px · 29 largeur(s) sur 233 diffèrent de la cascade · colonnes jusqu'à 32px (7.6%) d'écart
    720–1000 px : 1 colonne(s) deviennent 2
.participation-grid plancher 280px · 13 largeur(s) sur 233 diffèrent de la cascade · colonnes jusqu'à 28px (9.0%) d'écart
    640–760 px : 1 colonne(s) deviennent 2
```

Une bande qui tombe **dans un palier existant** n'est pas la même décision qu'une
bande qui tombe là où la grille n'avait plus de règle : la première déplace une
décision déjà prise avec d'autres, la seconde ne fait que prolonger un repli.

Décisions de la journée, écrites pour ne pas être reprises au jugé :

- `.ai-path-panel` — **converti** (bande 720–1 000 px, repli à 672 px de
  conteneur).
- `.participation-grid` — **retenu** : sa bande (640–760 px) traverse le palier
  de 760 px, qui porte d'autres décisions, et aucune mesure navigateur n'a montré
  ce que deux cartes côte à côte y donnent.

Limites : la bande est calculée sur la présentation par défaut (`--content`
1 160 px). En Lecture (940 px) et en Panorama (1 480 px) elle se décale, et le
modèle ne les mesure pas.

## 21. Quatrième grille inégale : accepter une plage au lieu de la supprimer (31 octobre 2026)

`.home-share-panel` (accueil, « Partager le site ») passe en `flex-wrap` :
rapport 1 / 0,8 porté par le `fr`, 260 px de base par colonne. Sa règle de repli
vivait dans le bloc `@media (max-width: 760px)` parmi cinq autres : le bloc reste,
il perd une règle (191 → 190).

**C'est la première conversion qui crée une plage au lieu d'en supprimer une.**
Entre 600 et 760 px de fenêtre, le panneau montre deux colonnes de 264 px là où
le palier imposait une colonne. Ce n'est pas un compromis subi : `minmax(260px,
.8fr)` demande 260 px par colonne, et deux telles colonnes tiennent dès 592 px de
fenêtre. Le palier refusait ce que la grille elle-même autorisait — une valeur
fixe contre l'arithmétique du contenu.

Ce qui a été vérifié avant d'accepter :

- **pas de débordement possible** : `flex-wrap` replie au lieu de déborder ;
- **les boutons tiennent** : `.home-share-actions` est déjà en `flex-wrap`, et le
  plus long libellé (« Envoyer par courriel ») mesure ~190 px avec son
  remplissage, pour 264 px de colonne ;
- **le texte ne s'étire pas** : `max-width: 60ch` sur le paragraphe, donc il se
  replie au lieu d'étirer la colonne.

Ce qui reste non prouvé : personne n'a vu ce panneau à 600 px dans un navigateur.
L'arithmétique dit « pas de débordement », pas « cela se lit bien ». C'est la
limite qui avait fait **retenir** `.participation-grid`, et la différence tient au
contenu : une carte de citation à 25,6 px de corps dans 229 px de large, contre
deux paragraphes de 0,9 rem et deux boutons.

## 22. Une base en `em` : le repli suit la taille du texte (31 octobre 2026)

Les quatre conversions précédentes acceptaient une plage où deux colonnes
apparaissent, faute de mieux. Il y avait une troisième issue, et elle est
meilleure : **choisir la base** au lieu de garder le minimum déclaré.

`plancher_de_compromis()` cherche la plus petite base qui reproduit le nombre de
colonnes de la cascade à **toutes** les largeurs mesurées. Pour `.hero-grid` :
325,64 px. Avec elle, aucune largeur ne change de nombre de colonnes, et les
deux règles de palier qui forçaient une colonne peuvent partir.

Et cette base est écrite en `em` — `20.4em`, soit 326,4 px à taille normale :

| Taille de texte | Base écoulée | Effet |
|---|---:|---|
| 100 % | 326,4 px | repli identique à l'ancien palier |
| 115 % | 375,4 px | le repli avance |
| 130 % | 424,3 px | le repli avance davantage |

Une base en pixels ignore le réglage de taille de texte ; une base en `em` le
suit. C'est la première fois dans ce fil qu'un repli dépend d'une **variable
d'affichage choisie par la personne**, et non de la largeur de sa fenêtre.

Deux garde-fous :

1. **l'arrondi est fait au centième supérieur** — arrondir vers le bas rendrait
   une base plus petite que celle qui vient d'être vérifiée, et ferait
   réapparaître la plage ;
2. le registre déclare **l'écriture et sa valeur en pixels**
   (`plancher_expr = "20.4em"`, `plancher_px = 326.4`), et `--verifier` refuse
   qu'elles se contredisent de plus de 0,5 px, ou que la feuille écrive des
   pixels là où le registre annonce des `em`.

Ce que cela coûte, chiffré : une colonne peut varier de 68,7 px (24,3 %) au lieu
de 58,9 px (20,9 %). La reproduction est arithmétique — même *nombre* de
colonnes — pas un même dessin.

Limite : le compromis est calculé sur la présentation par défaut (contenu
1 160 px) ; en Lecture (940 px) le repli avance, et le modèle ne mesure pas
cette présentation.

## 23. La promesse « le repli ne bouge pas » devient un contrôle (31 octobre 2026)

Le lot précédent annonçait que la base de `.hero-grid` reproduisait exactement
l'ancien repli. C'était vrai, mais **affirmé** : la règle de palier avait disparu
avec la conversion, donc plus rien dans la feuille ne permettait de refaire le
calcul. Un registre qui garde `ecart_max_px` mais pas la largeur de repli d'avant
laisse la promesse invérifiable.

Le registre garde désormais :

```toml
plancher_expr = "20.4em"
plancher_px   = 326.4
repli_avant_px = 760
```

`--verifier` reconstruit la cascade d'avant (`grille_avant` + une règle qui force
une colonne sous `repli_avant_px`), applique la base déclarée, et refuse si le
nombre de colonnes diffère à **une seule** des 233 largeurs mesurées. Le message
nomme la plage :

```
.hero-grid : `repli_avant_px = 760` annoncé comme reproduit, mais de 670 à
760 px la grille d'avant montrait 1 colonne(s) et le flex en donne 2
```

Deux grilles converties avec cette garantie :

| Grille | Base | Mesurée | Coût (écart de colonne) |
|---|---:|---:|---:|
| `.mission-grid` | 20.85em (333,6 px) | 333,48 px | **116,8 px — 44,7 %** |
| `.learning-work-panel` | 21.29em (340,6 px) | 340,5 px | 68,1 px — 24,3 % |

`.mission-grid` porte le coût le plus élevé de tout le fil, et il s'explique : son
rapport 1,35 / 0,65 est très dissymétrique, et `flex` ne partage que le **surplus**
là où `fr` partage **tout** l'espace. Même nombre de colonnes partout, proportions
plus éloignées.

**Ce que le compteur de paliers ne voit pas :** les deux blocs `@media` concernés
portent plusieurs sélecteurs ; retirer un sélecteur d'une règle ne change ni le
nombre de blocs ni celui des règles. Le compteur reste à 189 alors que deux
grilles quittent leurs paliers. C'est la même limite que pour `.contact-grid` —
et la réponse est la même : seule la comparaison des cascades, largeur par
largeur, dit la vérité.

Limite du nouveau contrôle : il suppose **une seule** condition de repli sous
`repli_avant_px`. Une grille dont le palier changeait deux fois demanderait un
champ par condition, que le modèle ne gère pas encore.

## 24. Trois grilles de plus, et le compteur de paliers qui avoue (31 octobre 2026)

| Grille | Base de compromis | Repli reproduit | Coût (écart de colonne) |
|---|---:|---|---:|
| `.ai-questions-layout` | 20.85em (333,6 px) | 333,48 px | 100 px — 38,3 % |
| `.learning-hero-grid` | 21.09em (337,4 px) | 337,4 px | 50,6 px — 17,4 % |
| `.participation-grid` | 21.29em (340,5 px) | 340,5 px | 34,1 px — 11 % |

Aucune largeur ne change de nombre de colonnes — vérifié par `repli_avant_px`,
pas affirmé.

**Le revirement de `.participation-grid`, écrit avec ses deux chiffres.** Le
matin, elle avait été retenue : sa conversion créait une plage 640–760 px avec
28 px (9 %) d'écart. Ce n'était pas un jugement définitif mais l'absence d'une
méthode — on ne savait choisir que la base déclarée. La base de compromis
supprime la plage ; le coût monte à 34,1 px (11 %). Un demi-point de proportion
payé pour un nombre de colonnes constant, et une base qui suit la taille du texte.

**Le compteur de paliers avoue, et c'est le fait marquant.** Trois grilles
quittent leur palier, le compteur ne baisse que de **189 à 188** :
`.ai-questions-layout` et `.learning-hero-grid` occupaient des règles à
plusieurs sélecteurs, et retirer un sélecteur d'une règle ne change ni le nombre
de blocs ni celui des règles. Seule `.participation-grid`, seule sur sa règle,
coûte une unité.

Conséquence pour la suite : **la dette de 188 règles n'est plus un indicateur
d'avancement.** Trois conversions peuvent n'en retirer qu'une. Les seuls chiffres
honnêtes sont le nombre de grilles en `flex-wrap` (11) et le nombre de
« proportion » restantes (4).

Limites : bases calculées sur la présentation par défaut (contenu 1 160 px) ; en
Lecture (940 px) et Panorama (1 480 px) le repli se décale, et le modèle ne les
mesure pas.

## 25. Deux des quatre grilles « proportion » n'existent pas (1er novembre 2026)

Le relevé de la veille laissait quatre grilles « proportion » à traiter, en
disant que trois n'avaient **aucune base** qui reproduise leur repli. La suite
du travail a trouvé autre chose, et c'est plus utile que la conversion
attendue : **deux de ces grilles ne sont ouvertes par aucune page.**

### Ce que le nouveau relevé mesure

`outils/auditer-selecteurs-morts.py` lit chaque sélecteur de `assets/css` et
cherche le nom de classe dans les sources qui peuvent en produire une instance :
pages HTML servies, scripts, générateurs, données. Trois verdicts, jamais deux —
**lue** (le nom existe en toutes lettres), **dynamique** (le nom est construit à
l'exécution, donc indécidable d'ici : `adventure-learning-world-${n}`) et
**morte**.

Sur la feuille du 1er novembre 2026 : **25 classes mortes**, soit 6,7 % des
374 classes de `site.css`.

| Famille | Classes mortes | Ce qu'elles portaient |
| --- | ---: | --- |
| `ai-feature-*` | 13 | toute une section « constellation d'usages » de la page IA |
| `simulateur-promo-*` | 2 | le panneau de promotion du simulateur |
| `learning-home-*` | 2 | un panneau d'accueil des apprentissages |
| `hero-logo*`, `hero-aside-*` | 4 | un visuel de héros et deux notes d'aside |
| autres | 4 | `.enthusiasm`, `.statute-line`, `.home-statut-card`, `.site-journey-title` |

Deux d'entre elles étaient les grilles « proportion » `.ai-feature-panel` et
`.simulateur-promo-panel`.

### Ce que le modèle faisait de ces grilles

Pour `.simulateur-promo-panel`, `--pistes` calculait un compromis à
**28,54em (456,5 px)** « qui reproduirait le repli actuel ». Le calcul était
juste : la cascade de la feuille, largeur par largeur, était fidèlement
reproduite. Il portait seulement sur une grille à laquelle aucune page ne confie
d'enfants. **Un modèle arithmétique ne sait pas distinguer une grille d'un nom
dans une feuille** ; il faut une autre mesure pour cela.

Pour `.ai-feature-panel` et `.learning-coverage-topic`, le même relevé disait
« aucune base ne reproduit le repli actuel ». Le verdict était juste pour
`.learning-coverage-topic`, et **faux par accident** pour `.ai-feature-panel` :
le nombre d'éléments y était inconnu (`items = 0`, faute de page), et `flex` sans
plafond d'éléments peut aligner trois panneaux là où la grille n'a que deux
pistes. Aucune base ne reproduisait alors une cascade inventée. Le dire reste la
bonne réponse ; la raison, elle, était la mauvaise.

### Ce qui a changé dans la feuille

Les 25 familles de règles sont retirées — pas seulement les deux grilles : une
règle qu'aucune page n'ouvre ne mesure rien, et la laisser reviendrait à
entretenir un compteur qui compte des fantômes. Le retrait est chirurgical :
dans une liste de sélecteurs, seules les branches mortes partent (`.map-privacy-notice,.learning-home-panel`
garde la première) ; dans un `:is(...)`, seules les branches mortes partent
aussi ; un composé entièrement mort suffit à condamner le sélecteur, puisque
`.learning-home-panel .button` vise un bouton sous un panneau qui n'existe pas.

| Compteur | Avant | Après |
| --- | ---: | ---: |
| classes de `site.css` | 374 | 349 |
| grilles à pistes inégales relevées | 20 | **17** |
| dont « proportion » | 4 | **2** |
| blocs `@media` de format | 37 | **36** |
| règles sous un palier de largeur | 188 | **176** |

La baisse de 12 règles est réelle et répartie : 6 de moins sous 760 px, 5 sous
520 px, 1 sous 1000 px. Elle ne doit rien à une conversion — c'est la première
fois dans ce fil que le compteur de paliers baisse sans qu'une grille change de
forme.

### Les deux « proportion » qui restent, et ce qu'elles deviennent

| Grille | Verdict | Preuve |
| --- | --- | --- |
| `.learning-coverage-topic` | **non convertie** | trois enfants pour deux pistes : les liens sont placés par `grid-column:2` puis déplacés par `grid-column:auto` sous 760 px. Ce n'est pas un partage de panneaux mais une composition avec un enfant placé ; en `flex-wrap`, les liens occuperaient toute la rangée |
| `.map-layout` | **non convertie** | compromis 26,62em reproduisant le repli (aucune bande de changement), mais coût mesuré **212,9 px — 78,8 %** d'écart de largeur de colonne, pour un rapport 1,5 / 0,5. Son repli vit à 920 px, avec deux autres décisions de la page contact (`display:none` sur `.identity-contact`, `.map-info` en deux colonnes) |

Autrement dit : sur les quatre « proportion » annoncées, **zéro conversion**,
deux suppressions et deux refus motivés. C'est un lot qui ne ressemble pas aux
précédents, et c'est le résultat honnête.

### Limites

Le relevé ne voit pas une classe construite par une source qu'il ne lit pas, et
il ne dit rien de l'utilité d'une classe qu'il trouve : une règle peut viser une
classe présente et n'avoir aucun effet. Il ne lit ni `.md` ni `.toml` — un nom
cité dans un registre est une trace, pas un usage — et il se retire lui-même de
son corpus, ainsi que ses bancs, parce qu'un banc cite les noms qu'il cherche.
Les six classes d'`anglais-aventure.css` construites à l'exécution restent
**indécidables** : elles sont comptées, pas jugées.

## 26. « Borne » recouvrait deux choses — et une colonne d'icône en `px` ne suit pas le texte (1er novembre 2026)

Le lot précédent laissait six grilles classées « borne », avec ce commentaire
dans le code : *une colonne a un plafond en pixels, un `flex` n'en a pas*. La
mesure a montré que **cinq d'entre elles n'avaient aucun plafond** :

| Grille | Valeur | Paliers | Verdict |
| --- | --- | ---: | --- |
| `.layout-choice` | `1.25rem 3.375rem minmax(0,1fr)` | 0 | badge |
| `.home-entry-list li` | `2.375rem minmax(0,1fr)` | 0 | badge |
| `.learning-work-steps li` | `2.4rem 1fr` | 0 | badge |
| `.ai-question-list li` | `2.75rem 1fr` | 0 | badge |
| `html.has-js .site-header .customize-settings` | `1.125rem 2.5rem minmax(0,1fr)` | 0 | badge |
| `.learning-article-layout` | `minmax(0,1fr) minmax(230px,300px)` | 1 | **plafond** |

Aucune des cinq premières n'a de palier, aucune ne se replie : **il n'y avait
rien à rendre dynamique**, et le rapport envoyait convertir des colonnes de
numéro. Le mot « borne » mélangeait une décision de largeur (un plafond) et une
taille d'icône.

### Le défaut réel des badges : l'unité

Quatre de ces colonnes étaient écrites en **pixels nus** — `44px`, `38px`,
`20px` et `54px`, `18px` et `40px`. Le site sait agrandir le texte
(`html.texte-agrandi` porte la taille racine à 115 %, `texte-tres-agrandi` à
130 %). Une colonne en `px` ne bouge pas ; le numéro qu'elle porte, si. À 130 %,
on garde 44 px pour un texte 30 % plus large.

`rem` suit la taille racine. À 100 %, les deux écritures sont **identiques** :

| Avant | Après | À 100 % | À 130 % |
| --- | --- | ---: | ---: |
| `44px` | `2.75rem` | 44 px | 57,2 px |
| `38px` | `2.375rem` | 38 px | 49,4 px |
| `20px` | `1.25rem` | 20 px | 26 px |
| `54px` | `3.375rem` | 54 px | 70,2 px |
| `18px` | `1.125rem` | 18 px | 23,4 px |
| `40px` | `2.5rem` | 40 px | 52 px |
| `42px` | `2.625rem` | 42 px | 54,6 px |
| `36px` | `2.25rem` | 36 px | 46,8 px |

Huit pistes réécrites dans sept règles, aucune capture par défaut qui change : c'est le seul
changement de ce fil dont le rendu à 100 % est **rigoureusement identique** à
l'ancien, et qui ne se voit qu'au rythme où la personne lit.

### Le contrôle

`modele-grilles.py --verifier` refuse désormais toute piste en `Npx` nu, dans
les trois sources qui sont de nous : `assets/css/site.css`,
`assets/css/anglais-aventure.css` (`.adventure-character-line`, `42px` puis
`36px` sous 520 px) et `outils/construire-simulateur.py` (le panneau
`.site-layout-choice`, `20px 54px`). Une piste écrite dans un `minmax(...)`
n'est pas concernée : elle porte une décision de largeur, pas une taille
d'icône.

### Le plafond refusé, et la mesure qui change le refus

`.learning-article-layout` est la seule grille à plafond. Le relevé dit
maintenant, largeur par largeur :

> la piste vaut 300 à 300 px sur 180 largeurs à deux colonnes — la borne basse
> (230 px) n'est jamais atteinte

Autrement dit, `minmax(230px, 300px)` **se comporte comme `300px`** partout où
la grille a deux colonnes : la borne basse est un garde-fou que la cascade
n'atteint jamais. Le refus ne porte donc pas sur le plafond lui-même. Il porte
sur l'autre moitié du comportement : sous 760 px, la grille met ce panneau sur
une piste `minmax(0,1fr)` et il prend **toute la largeur**. Un `flex` de base
300 px resterait à 300 px : `flex-grow` ne peut pas dépendre du repli. Convertir
demanderait un second comportement, pas une base.

Ce refus est écrit dans `docs/rd/grilles-dynamiques.toml` (`[[grille_plafond]]`),
et le contrôle vérifie qu'il a toujours un objet : si la feuille perd le
plafond, la décision est refusée comme fausse.

### Limites

La feuille du moteur embarqué du simulateur vient de l'amont
(`simulateur/PROVENANCE.json`) et n'a pas été touchée : ses pistes
(`1fr 96px 74px auto` dans `.levier.compact`) restent en pixels, et ce contrôle
ne les lit pas — il lit `construire-simulateur.py`, qui ne porte que nos règles.
Aucun de ces changements n'a été regardé à 130 % dans un navigateur : la preuve
est arithmétique (44 px = 2,75 × 16), pas visuelle.

## 27. Une bande d'un pixel, et la fin d'un modèle qui se validait lui-même (1er novembre 2026)

Les six grilles converties en `flex-wrap` le 31 octobre portaient, au registre,
la phrase « aucune largeur ne change de nombre de colonnes ». Elle avait été
vérifiée à chaque largeur multiple de 10 px. En repassant le **même balayage au
pixel** — 2 321 largeurs de 240 à 2 560 —, trois des six changeaient de colonnes
à **761 px**.

La cause n'est pas un chiffre faux, c'est une géométrie :

> une base de `flex` ne replie qu'à un seuil, et les bases qui tombent pile entre
> 760 et 761 px forment une fenêtre de **0,46 px** de large.

| grille | base écrite la veille | px | fenêtre mesurée | corrigée en |
| --- | --- | --- | --- | --- |
| `.hero-grid` | `20.4em` | 326,40 | ]325,60 ; 326,06] | `20.37em` (325,92) |
| `.learning-work-panel` | `21.29em` | 340,64 | ]340,00 ; 340,50] | `21.28em` (340,48) |
| `.participation-grid` | `21.29em` | 340,64 | ]340,00 ; 340,50] | `21.28em` (340,48) |

Deux fautes de méthode ont été corrigées dans le calcul, pas seulement trois
valeurs : la base en `em` est désormais arrondie **vers le bas** puis vérifiée au
pixel (arrondir au-dessus de la base trouvée sort de la fenêtre et rouvre la
bande qu'on voulait fermer), et la tolérance du registre est passée de **0,5 px**
à **0,01 px** — plus large que la fenêtre, elle ne contrôlait rien.

### Ce que cet épisode a vraiment appris

Le balayage au pixel a trouvé trois erreurs que le balayage au pas de 10 px
avait validées. Mais le défaut est plus profond que le pas : **le modèle était le
seul juge du modèle**. Rien, dans ce dépôt, ne confrontait ce qu'il annonce à ce
qu'un navigateur affiche. Un contrôle qui ne se compare qu'à sa propre
arithmétique ne prouve que sa cohérence.

D'où la chaîne ajoutée ce jour, en trois pièces séparées à dessein :

1. **la prédiction** — `outils/modele-grilles.py --releve-json` écrit, pour
   **34 grilles**, ce que la feuille *devrait* produire : les largeurs qui
   encadrent chaque rupture annoncée, plus treize largeurs de repère. Une base en
   `em` est annoncée à 100 %, 115 % et 130 % — la promesse « le repli suit la
   taille du texte » n'avait jamais été mesurée nulle part. Une base en pixels
   n'est annoncée qu'à 100 %, et le relevé le dit (`suit_le_texte = false`)
   plutôt que de mesurer trois fois la même chose ;
2. **la mesure** — `outils/mesurer-grilles.cjs` compte, dans un vrai Chromium,
   les colonnes de chaque grille : rangées d'un `flex-wrap`, repérées par la
   position horizontale et non par le haut (plusieurs grilles converties sont en
   `align-items: center`, où deux panneaux n'ont jamais le même bord haut) ;
   pistes **non nulles** d'une grille (`auto-fit` replie les pistes vides à 0 px,
   et une grille de deux cartes sur quatre pistes n'a pas quatre colonnes). Il
   élargit la fenêtre de la largeur de l'ascenseur jusqu'à ce que la largeur
   cliente vaille exactement la largeur demandée : sans cela, chaque mesure
   serait décalée de 15 px et le modèle accuserait la feuille d'un artefact de
   navigateur ;
3. **la comparaison** — `outils/rapporter-mesure-grilles.py` lit les deux
   fichiers et nomme les divergences : largeur, échelle de texte, valeur
   annoncée, valeur vue, et **largeur réelle de l'élément** à côté du conteneur
   que le modèle présume. Cette dernière colonne est la première cause à écarter
   avant d'accuser la feuille : une grille qui porte son propre remplissage
   n'occupe pas la largeur que `conteneur()` lui prête.

### Le contrat de sortie, écrit avant la première mesure

- `mesurer-grilles.cjs` sort en **code 2** sans navigateur ou sans modules, et
  le dit — jamais vert, jamais un rapport vide présenté comme un succès ;
- il sort en **code 1** si une page ou un sélecteur n'a pas pu être mesuré ;
- `rapporter-mesure-grilles.py` sort en **code 2** sur un rapport sans
  navigateur, vide ou illisible, et compte un point annoncé sans mesure comme
  **non mesuré**, jamais comme conforme ;
- en mode `--controler`, la moindre divergence le fait sortir en **code 1**. Ce
  mode n'est pas encore celui de la CI : le premier passage est un **relevé**.
  Il publie les nombres, et l'étape le dit en première ligne de sa sortie. Passer
  au contrôle demande de lire ces nombres d'abord — l'inverse serait décider
  avant de mesurer.

### Limites

Le relevé mesure la présentation par défaut (celle que la feuille applique sans
`data-layout`) : les cinq autres présentations replient plusieurs de ces grilles
par d'autres règles, et ne sont pas couvertes. Il ne mesure qu'un point par
(page, grille) : la même grille peut se comporter autrement dans une page où
elle reçoit plus d'éléments — le relevé choisit la page où elle en reçoit le
plus, et le dit dans la prédiction. Enfin la comparaison reste celle d'un
navigateur sans personne devant : elle compte des colonnes, elle ne dit pas si la
page est lisible.
