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
nue, césure des mots longs, en-tête compact non rapetissé.

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
