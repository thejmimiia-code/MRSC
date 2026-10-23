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
