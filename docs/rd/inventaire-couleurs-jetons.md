# R&D — inventaire des couleurs et plan de jetons (avant toute variante sombre)

**Inventaire du 18 octobre 2026.** Le § 6 de [`rd-affichage-adaptatif.md`](../rd-affichage-adaptatif.md) et le § 6 de [`presentations-personnalisees.md`](presentations-personnalisees.md) diffèrent tout thème sombre tant que les couleurs codées en dur n’ont pas été inventoriées par rôles, avec mesures de contraste. Cette note réalise cet inventaire dans l’ensemble des fichiers sources du dépôt et propose un plan de jetons en trois phases. **Aucune valeur de couleur, aucun fichier de style ou de code n’est modifié dans cette passe** : le rendu actuel est strictement inchangé, et aucun thème sombre n’est livré ni promis. Initiative : `optimisation-du-site` (état `a-tester`, inchangé).

## 1. Méthode et limites du comptage

Comptage par script éphémère hors dépôt, rejouable à partir de cette description : recherche des littéraux hexadécimaux (3, 4, 6 ou 8 chiffres, normalisés en minuscules et en 6 chiffres) et des fonctions `rgb()`/`rgba()`/`hsl()`/`hsla()` dans les fichiers sources ; pour la feuille principale, rattachement de chaque valeur à la propriété CSS qui la porte et regroupement des valeurs en grappes de teintes proches (distance colorimétrique pondérée simple, seuil ≈ 28) ; contrastes calculés selon la formule de luminance relative des WCAG. Le chiffre de « 197 occurrences » cité jusqu’ici pour `assets/css/site.css` est remplacé par le décompte détaillé ci-dessous (199 occurrences hexadécimales au total dans le fichier, définitions comprises).

Limites : un inventaire statique ne voit ni les couleurs des images, ni celles calculées à l’exécution sans littéral, ni les contextes réels d’empilement (texte sur dégradé ou sur image) ; quatre valeurs de la feuille principale, portées par des déclarations multi-lignes (dégradés), sont comptées mais non rattachées à une propriété. Les paires de contraste du § 5 sont des calculs sur fonds unis de référence, pas un audit page par page.

## 2. Résultats par surface

| Surface | Hexadécimal (occurrences / valeurs distinctes) | Fonctions couleur |
|---|---|---|
| `assets/css/site.css` | 199 au total, dont 11 définitions initiales dans `:root` ; **188 hors définitions initiales / 91 distinctes** | 103 hors définitions initiales (68 distinctes) |
| `assets/css/anglais-aventure.css` | 231 / 131 | 35 (31 distinctes) |
| `outils/construire-simulateur.py` (habillage de la page autonome) | 66 / 33 | 11 (5 distinctes) |
| `outils/construire-apprentissages.py` | 1 / 1 | 0 |
| Pages HTML et 81 fiches | métadonnée `theme-color` `#1d3268` (= `--navy`) ; aucune couleur propre — les fiches chargent `site.css` | 0 |
| Scripts du site (`site.js`, `navigation-parcours.js`, `apprentissage.js`, fichiers de données) | 0 | 0 |

**Hors périmètre « thème d’interface »** (inventoriés pour ne pas les confondre avec les couleurs d’interface) :

- Moteur du simulateur (`simulateur/*.py`) : 139 occurrences / 54 distinctes et 61 fonctions. L’essentiel est la palette sombre propre du moteur (`interface.py`, 33 valeurs distinctes), déjà exprimée en variables dans la page générée (`--bg`, `--panel`, `--border`…) ; `domaines.py` (20 valeurs), `parametres.py` (28) et `dashboard.py` (11) portent des couleurs de données et de graphiques. Toute évolution y relève du moteur, puis d’une régénération — pas d’une tokenisation côté site.
- `assets/js/anglais-aventure.js` : 190 occurrences / 163 distinctes — palettes des scènes illustrées dessinées par le code (données de dessin), pas l’interface.
- `ia-societe.html` : 6 remplissages d’un graphique SVG en ligne (illustration).

## 3. Ce qui est déjà en jetons

La feuille principale définit onze jetons de couleur (`--ink`, `--navy`, `--blue`, `--blue-soft`, `--green`, `--gold`, `--red`, `--muted`, `--line`, `--paper`, `--white`) et une ombre (`--shadow`). Surtout, **le mécanisme de variante par jetons est déjà à l’œuvre** : deux blocs redéfinissent ces jetons avec des valeurs plus foncées — le réglage manuel `html.contraste-renforce` et la requête `@media (prefers-contrast: more)`. Une éventuelle variante sombre suivrait le même chemin, sans nouvelle machinerie.

La feuille de l’aventure n’a pas de `:root` propre : `anglais-aventure.html` charge `site.css` puis `anglais-aventure.css`, qui hérite donc des jetons du site ; 56 de ses occurrences (6 valeurs) sont déjà égales à ces jetons. Dans l’habillage du simulateur, 21 occurrences (4 valeurs) le sont aussi — mais cette page est autonome : ses valeurs devront rester recopiées ou redéfinies localement par son générateur.

## 4. Lecture par rôles dans la feuille principale

Sur 91 valeurs distinctes hors définitions initiales, 50 n’apparaissent qu’une fois ; les 87 valeurs rattachées à une propriété se rangent en 35 grappes de teintes proches. Les rôles dominants :

- **Textes secondaires.** Parallèlement au jeton `--muted` (`#647086`), une grappe « ardoise » de 8 valeurs voisines totalise 28 occurrences, presque toutes en `color` : `#536078` (×16), `#4f5d72` (×6), `#46536b` (×4)… C’est un second texte secondaire de fait, décliné en nuances quasi identiques au fil des composants.
- **Fonds et surfaces.** Grappe des blancs cassés (7 valeurs, 30 occurrences : `#f8f9fc`, `#f6f8fb`…) et grappe des fonds teintés par famille (20 valeurs, 36 occurrences : bleu très pâle `#edf1f6`, vert très pâle `#eff5e9`, crème `#f8f1df`…) — les fonds de cartes et d’encadrés.
- **Bordures.** Outre `--line` : `#aebbd0` (×5), `#dfe6ef` (×4), `#d7ddea` (×3), grappe de 10 valeurs / 19 occurrences.
- **Textes d’accent foncés.** `#835100` (or foncé) et `#a3232c` (rouge foncé) servent de versions lisibles des accents pour le texte — ce sont aussi les valeurs de `--gold`/`--red` en contraste renforcé.
- **Sur fond marine** (en-tête, pied, encadrés bleus) : blanc et blancs translucides `rgba(255,255,255,*)` (55 des 103 fonctions couleur), textes pâles `#bae6fd`, `#d9e5f7`, `#d6e9c3`.
- **Ombres.** Base `rgba(26,48,91,*)` (×13), légèrement distincte de `--navy` (`29,50,104`, ×2 seulement en fonction couleur) ; dérivées translucides des accents (bleu ×9, or ×4, rouge ×2) et vert vif d’illustration `rgba(118,181,68,*)` (×10).

## 5. Contrastes de référence du thème clair (calculés)

Textes fréquents sur blanc (`#ffffff`) et sur `--paper` (`#f5f7fa`) :

| Couleur de texte | Sur blanc | Sur `--paper` |
|---|---|---|
| `--ink` `#18243b` | 15,51:1 | 14,45:1 |
| `#46536b` | 7,75:1 | 7,22:1 |
| `#a3232c` | 7,41:1 | 6,90:1 |
| `--blue` `#2958a2` | 6,97:1 | 6,50:1 |
| `#4f5d72` | 6,69:1 | 6,23:1 |
| `#835100` | 6,68:1 | 6,23:1 |
| `#536078` | 6,34:1 | 5,91:1 |
| `--green` `#456d29` | 6,05:1 | 5,63:1 |
| `--muted` `#647086` | 5,00:1 | 4,65:1 |

Textes sur `--navy` (`#1d3268`) : blanc 12,29:1 ; `#d9e5f7` 9,66:1 ; `#d6e9c3` 9,54:1 ; `#bae6fd` 9,26:1 ; `--gold` `#e7a126` 5,57:1.

Lecture : toutes les couleurs de texte fréquentes dépassent le repère de 4,5:1 sur blanc ; la plus faible est `--muted` (5,00:1 sur blanc, 4,65:1 sur `--paper`), alors que la grappe ardoise littérale est plus contrastée — un point à arbitrer lors de la tokenisation, sans changer les valeurs dans un premier temps.

## 6. Points d’attention relevés (faits, à arbitrer en phase 1)

1. **`--white` joue deux rôles opposés** : fond de page et de cartes (dont 8 `background: #fff` littéraux) et premier plan clair sur fond marine (contours de focus, bordures). Avant toute variante sombre, il devra être scindé en rôles distincts (surface claire / élément sur fond sombre), sinon inverser l’un casserait l’autre.
2. **Quatre libellés de cartes d’accueil sont des littéraux** (`--home-card-kicker` : `#456d29`, `#2958a2`, `#835100`, `#a3232c`) alors que l’accent voisin suit les jetons (`--home-card-accent: var(--green)`…). En contraste renforcé, accents et libellés divergent donc légèrement (par exemple `--blue` passe à `#174a87`, le libellé reste `#2958a2`). Aligner ces libellés sur les jetons changerait le rendu du seul mode contraste renforcé : décision explicite et captures, pas un remplacement mécanique « à valeur égale ».
3. **Une valeur est verrouillée par un vérificateur** : `outils/verifier-integration.py` exige le littéral `.creator-note .eyebrow { color: #bae6fd; }`. La phase 1 devra mettre à jour cette assertion dans le même changement.
4. **Base d’ombre distincte de `--navy`** (`rgba(26,48,91,*)` contre `29,50,104`) : fusion ou jeton d’ombre dédié, à arbitrer (`--shadow` existe déjà pour l’ombre principale).
5. Les 15 occurrences de `site.css` exactement égales à un jeton existant ne sont **pas** toutes remplaçables telles quelles : trois sont des redéfinitions de jetons dans les blocs de contraste renforcé (les remplacer serait circulaire) et deux sont les libellés du point 2.

## 7. Plan proposé en trois phases (aucune exécutée ici au-delà de l’inventaire)

**Phase 1 — feuille principale, à valeurs strictement identiques.** Introduire des jetons de rôle (noms proposés, dans le style court déjà en place : `--text-soft`, `--surface`, `--surface-soft`, `--tint-blue`, `--tint-green`, `--tint-gold`, `--border-strong`, `--gold-ink`, `--red-ink`, `--on-navy`, `--on-navy-soft`) et remplacer les littéraux **par rôle** plutôt que par simple égalité de valeur, sans changer aucun rendu du thème clair. Preuve attendue : captures avant/après identiques sur les pages types, porte complète du dépôt et essais navigateur, assertion verrouillée du point 6.3 mise à jour dans le même changement.

**Phase 2 — surfaces voisines.** Même traitement pour `anglais-aventure.css` sur les jetons communs (ordre de chargement déjà favorable), puis pour l’habillage du simulateur **uniquement via son générateur** `outils/construire-simulateur.py`, page régénérée et `--verifier` à l’appui. Le moteur (`simulateur/*.py`) et les palettes d’illustration restent hors de cette tokenisation.

**Phase 3 — variante sombre : décision séparée, non prise ici.** Seulement après les phases 1–2 : prototype borné aux jetons de rôle, tableau de contrastes paire par paire (repères 4,5:1 pour le texte courant, 3:1 pour les grands textes et composants), captures sur l’ensemble des pages types, relecture visuelle humaine, puis décision sur le mode d’activation (préférence système `prefers-color-scheme`, choix manuel dans le panneau « Affichage », ou les deux). Les personnes concernées par la sensibilité à la lumière ou certaines basse visions doivent faire partie des essais avant toute publication.

## 8. Limites et statut

Inventaire statique et calculs de référence uniquement : aucun navigateur, aucune capture et aucun essai avec des personnes dans cette passe, et aucun fichier de style ou de code modifié. Le thème sombre reste **différé**, aux conditions des § 6 des deux notes citées en tête. La phase 1 a été réalisée le même jour (§ 9) ; l’état de l’initiative reste `a-tester`, la relecture visuelle humaine des présentations et de l’en-tête demeurant prioritaire.
## 9. Phase 1 réalisée le 18 octobre 2026 (feuille principale)

**Fait.** Dix-huit jetons de rôle ont été ajoutés au `:root` de `assets/css/site.css` et **84 littéraux, sur 72 lignes, ont été remplacés par ces jetons à valeurs strictement identiques** : textes secondaires (`--text-soft` `#536078`, `--text-soft-2`, `--text-soft-3`), surfaces claires (`--surface`, `--surface-soft`, `--surface-soft-2`), fonds teintés (`--tint-blue`, `--tint-green`, `--tint-gold` et variantes), bordures (`--border-strong`, `--border-soft`, `--border-soft-2`) et textes sur fond marine (`--on-navy`, `--on-navy-sky`, `--on-navy-pale`, `--on-navy-green`). Le blanc littéral a été réparti selon son rôle réel, vérifié ligne par ligne : fonds de cartes et d’impression vers `--surface` (8 occurrences), chiffre blanc sur pastille marine vers `--on-navy` (1) ; l’anneau blanc des pastilles décoratives `.ai-feature-orbit`, au rôle ambigu, reste un littéral. Chaque remplacement a d’abord été produit en plan à blanc et relu ligne par ligne ; aucune définition de jeton (blocs de contraste renforcé compris) n’a été touchée.

**Preuve d’identité du rendu.** Photographie des styles calculés porteurs de couleur (couleur, fonds, dégradés, bordures, contours, ombres) de tous les éléments, avant puis après le changement, dans un navigateur sans interface : 8 pages types (accueil, catalogue, dossier IA, aventure, une fiche, transparence, liens utiles, documents) × 2 largeurs (320 et 1 440 px), plus l’accueil en contraste renforcé — **16 582 éléments photographiés, 0 différence**. Essais navigateur `outils/test-experience.cjs` : 8/8 inchangés. Porte complète du dépôt réussie ; l’assertion verrouillée du § 6.3 a été mise à jour (`var(--on-navy-sky)`) et un nouveau contrôle d’intégration vérifie les principaux jetons et la disparition de leurs littéraux hors définition.

**Résidu assumé.** Hors définitions du `:root` initial, il reste 104 occurrences hexadécimales littérales (75 valeurs distinctes, pour l’essentiel des valeurs vues une ou deux fois : dégradés ponctuels, nuances isolées) et les 103 fonctions `rgba()` (blancs translucides sur fond marine, ombres, dérivées d’accents). Les quatre libellés de cartes d’accueil (§ 6.2) restent des littéraux en attente d’arbitrage, et les usages existants de `var(--white)` n’ont pas été scindés : seuls les littéraux l’ont été. Aucune valeur sombre n’existe toujours pas ; la phase 2 a été réalisée le même jour (§ 10), la phase 3 reste entière.
## 10. Phase 2 réalisée le 18 octobre 2026 (aventure et habillage du simulateur)

**« Les Mondes » (`assets/css/anglais-aventure.css`) : 77 littéraux remplacés sur 69 lignes.** Cinquante-quatre passent par des jetons communs du site **non redéfinis en contraste renforcé** — `--text-soft` (×17), `--text-soft-3` (×3), `--tint-blue` (×1), `--surface` pour les fonds blancs (×27), `--on-navy` pour les textes blancs du héros (×6) — et vingt-trois par quatre jetons locaux définis en tête de la feuille : `--mondes-bordure` (`#dce3ec`, ×10), `--mondes-vert` (`#3b5e2b`, ×5), `--mondes-ambre` (`#d99243`, ×4), `--mondes-progres` (`#3d776f`, ×4). **Ensemble gelé volontairement** : vingt-trois littéraux égaux aux jetons d’origine du site (`#1d3268` ×12, `#18243b` ×5, `#647086` ×3, `#2958a2` ×2, `#456d29` ×1) restent écrits en dur, car ces jetons sont redéfinis par les blocs de contraste renforcé : les brancher maintiendrait le thème clair par défaut mais changerait le rendu du seul contraste renforcé (dans le sens d’un contraste accru). C’est le même arbitrage que pour les libellés de cartes d’accueil (§ 6.2) : un choix de conception à décider explicitement, pas un renommage mécanique. Résidu : 154 occurrences littérales (123 valeurs distinctes — thématiques par monde et par scène, valeurs ponctuelles, ensemble gelé) et 35 fonctions couleur.

**Habillage du simulateur (`outils/construire-simulateur.py` uniquement) : 31 littéraux remplacés sur 30 lignes.** Quatre jetons préfixés, sans collision avec ceux du moteur, sont définis dans le `:root` de l’habillage : `--mrsc-marine` (`#1d3268`, ×8), `--mrsc-marine-2` (`#26375f`, ×6), `--mrsc-bordure` (`#526384`, ×7), `--mrsc-sur-marine` (`#fff`, ×10 en `color`). La page autonome a été régénérée par son générateur (`--verifier` à l’appui) ; l’assertion du vérificateur qui verrouillait le dégradé du bouton principal suit désormais la forme en jeton, et un contrôle de phase 2 verrouille les jetons des deux surfaces. Restent littéraux : les définitions propres du moteur et de l’habillage, des valeurs ponctuelles, et le bleu `#2958a2` / le vert `#456d29` vus une seule fois.

**Preuve d’identité du rendu.** Même méthode qu’au § 9, contextes élargis : 9 pages types (les 8 précédentes et la page autonome du simulateur) × 2 largeurs, avec contraste renforcé photographié en plus sur l’accueil, l’aventure et le simulateur — **41 940 éléments, 0 différence**. C’est ce contexte « contraste renforcé » qui valide l’ensemble gelé ci-dessus. Essais navigateur 8/8 inchangés, porte complète du dépôt réussie.

**État après phases 1–2.** Les couleurs répétées à rôle clair des trois feuilles passent par des jetons ; les résidus sont des valeurs ponctuelles, des thématiques par monde ou des arbitrages explicites (libellés d’accueil, ensemble gelé de l’aventure). La phase 3 — une variante sombre — reste **subordonnée à une relecture visuelle humaine et à une décision séparée** ; un prototype borné et non activé en documente désormais la faisabilité partielle et les prérequis (§ 12), sans qu’elle soit promise.
## 11. Arbitrage de l’« ensemble gelé » réalisé le 18 octobre 2026

**Décision.** Les littéraux laissés en suspens aux phases 1–2 sont désormais branchés sur leurs jetons : les quatre libellés de cartes d’accueil (vert et bleu sur `var(--green)`/`var(--blue)` ; or et rouge sur deux nouveaux jetons de rôle, `--gold-ink` `#835100` et `--red-ink` `#a3232c`, car les accents de base sont trop clairs pour du texte) et les vingt-trois littéraux de l’aventure égaux aux jetons d’origine (`--navy` ×12, `--ink` ×5, `--muted` ×3, `--blue` ×2, `--green` ×1). Chaque usage a été relu auparavant : tous sont des éléments foncés sur fonds clairs (titres, textes, bordures, contours de focus, fond d’avatar à initiales claires).

**Preuve.** Même photographie des styles calculés qu’aux § 9–10 (24 contextes, 41 940 éléments) : **thème par défaut strictement inchangé (0 différence)** ; seules différences dans les contextes « contraste renforcé » (106 éléments : les 2 libellés vert/bleu de l’accueil et 51 éléments de l’aventure, à chaque largeur), toutes dans le sens attendu — les éléments prennent la valeur renforcée de leur jeton. Contrastes avant → après, calculés sur blanc (les fonds réels du contraste renforcé sont clairs : `--paper` y vaut `#fff`) : encre 15,51 → 17,75:1 ; marine 12,29 → 15,20:1 ; gris secondaire 5,00 → 8,97:1 ; bleu 6,97 → 8,88:1 ; vert 6,05 → 6,24:1 ; initiales de l’avatar sur fond marine 9,75 → 12,05:1. **Aucune baisse.** Essais navigateur 8/8, porte complète réussie, contrôle d’intégration dédié ajouté.

## 12. Prototype sombre borné et non activé (18 octobre 2026) — faisabilité partielle, prérequis identifiés

**Méthode.** Des valeurs sombres candidates ont été définies pour les seuls jetons de rôle, calculées, puis **injectées uniquement dans la session du navigateur d’essai** (aucun fichier du dépôt ne les contient) afin de photographier quatre vues (accueil haut et cartes, catalogue, aventure). Rien n’est activé ni publié.

**Valeurs candidates (extraits).** Fonds : page `#0d1526`, section `#111c31`, carte `#162136`, marine conservé `#14264e`. Textes : `--ink` `#e9eef6`, `--muted` `#a7b3c6`, `--text-soft` `#b3c0d4` / `-2` `#bcc9dd` / `-3` `#c9d5e8`, liens `--blue` `#8ab4f0`, `--green` `#9ccb77`, `--gold-ink` `#f2c15f`, `--red-ink` `#ffb0b3`. Accents : `--gold` `#f0b64f`, `--red` `#ff9a9e`. Bordures : `--line` `#2b3a57`, `--border-strong` `#54688f`. Jetons « sur marine » inchangés. **Contrastes calculés : tous les textes entre 7,56:1 et 15,64:1 sur les trois fonds de référence** — le calcul par paires est donc satisfaisant.

**Constat des captures : la variante n’est pas activable en l’état.** Les zones peintes par les jetons (fond de page, textes, pied marine) rendent correctement, mais trois familles bloquantes, déjà chiffrées dans le résidu des § 9–10, cassent des pans entiers : (1) **surfaces claires littérales hors jetons** — l’en-tête est peint par `rgba(255,255,255,.97)`, les héros et sections par des dégradés/voiles clairs littéraux, certains panneaux par des blancs en dur : restées claires, elles rendent illisibles les textes passés en jetons clairs (adresse de contact et baseline de l’en-tête, appels de section, texte de panneaux de l’aventure) ; (2) **jetons à double rôle** — `--navy`, retenu comme surface, rend les titres qui l’utilisent comme couleur de texte quasi illisibles sur fond sombre (accueil et aventure), et `--white` pose le problème symétrique pour les premiers plans sur marine ; (3) **composants mixtes** texte-en-jeton sur fond littéral (boutons secondaires observés sombres à texte sombre).

**Conclusion et prérequis (« phase 2.5 »).** Avant toute décision sur une variante sombre, il faudrait — toujours à valeurs identiques dans le thème clair, avec la même preuve par photographie — résorber les surfaces littérales (le résidu de la feuille principale : 104 occurrences hexadécimales et 103 fonctions `rgba()`, dont l’en-tête translucide et les dégradés de sections) et scinder `--white` et `--navy` selon leurs rôles, puis re-prototyper. Le simulateur, sombre nativement avec la même identité marine/or/vert, montre au passage qu’une telle variante est graphiquement tenable. Décision d’activation et mode de déclenchement (préférence système, choix manuel, ou les deux) restent entièrement ouverts ; les captures du prototype sont conservées hors dépôt et décrites ci-dessus.
