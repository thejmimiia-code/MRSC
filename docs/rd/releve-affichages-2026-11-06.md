# Relevé d'affichage du 6 novembre 2026 — retour d'un vrai navigateur

**Document daté.** Il ne remplace ni une relecture humaine, ni un essai avec des
personnes, ni un lecteur d'écran. Il dit ce qu'un Chromium sans interface a
mesuré, avec quels réglages, et ce que ces mesures ne prouvent pas. Les relevés
plus anciens (`docs/rd/formats-affichage.md`, `docs/rd/avancees.md`) gardent
leur date : ils ne sont pas corrigés ici.

## 1. Pourquoi ce relevé

Le lot #281 avait été publié sans mesure navigateur : Chromium n'était plus
disponible dans l'atelier. Deux points restaient donc écrits en attente :

- « remesurer les six configurations d'affichage » ;
- « débordement horizontal préexistant de 24 px à `320-130` », relevé le
  6 novembre lors d'un A/B sur la version d'avant #281 et attribué à
  `.section-heading` et `.licence-callout`.

Le navigateur a été rétabli **hors du dépôt** : `@sparticuz/chromium` 153.0.0
(binaire `HeadlessChrome/153.0.8010.0`), `puppeteer-core` 25.16.0, et les
bibliothèques `al2023.tar.br` du paquet extraites dans `/tmp` avec
`LD_LIBRARY_PATH`. Aucun fichier du site, aucune feuille CSS et aucun script n'a
été modifié pour ce relevé.

## 2. Ce qui a été mesuré

| Relevé | Outil | Combinaisons | Résultat |
| --- | --- | --- | --- |
| Matrice complète | `outils/auditer-affichages.mjs` | **2 470 mesures** : 10 modes × 13 pages × 19 formats (280 → 3 840 px, densités 1× à 3×) | défilement horizontal maximal **0 px**, 0 élément hors cadre, 0 texte rogné, 0 cible sous 24 px |
| Ciblage `320 px / 130 %` | sonde locale Puppeteer | **272 mesures** : 13 pages, crans 100/130 %, six présentations, contraste + espacement renforcés, mobile et non mobile, puis A/B avant/après #281 | `scrollWidth = clientWidth = 320` partout |
| A/B `#281` | même sonde, deux serveurs locaux | `transparence.html` d'avant #281 (45 759 o, récupérée depuis `76a945a` via l'API GitHub) et d'après (50 876 o), **mêmes CSS/JS** | 72 combinaisons par version, aucun débordement dans l'une ni dans l'autre |
| Comportements | `outils/test-experience.cjs` | 13 essais avec `outils/serveur-local.py` | **13/13** : menu, « Personnalisation », mode réduit persistant, 320 px à 130 %, focus, lecture vocale, iframe |

Résumé machine des compteurs : [`releve-affichages-2026-11-06.json`](releve-affichages-2026-11-06.json).

Reproduction :

```sh
npm install --prefix /tmp/navigateur @sparticuz/chromium puppeteer-core
# décompresser bin/al2023.tar.br (zlib.brotliDecompressSync) dans /tmp/al2023-libs
python3 -m http.server 4180 --bind 0.0.0.0            # racine du dépôt
BASE_URL=http://127.0.0.1:4180 RAPPORT=/tmp/audit.json \
  LD_LIBRARY_PATH=/tmp/al2023-libs/lib node outils/auditer-affichages.mjs
MRSC_BROWSER_NODE_MODULES=/tmp/navigateur/node_modules \
  LD_LIBRARY_PATH=/tmp/al2023-libs/lib node outils/test-experience.cjs
```

`auditer-affichages.mjs` demande ImageMagick (`convert`) pour la netteté des
images ; il était disponible. La suite navigateur doit tourner avec
`serveur-local.py` : avec un simple serveur de fichiers statiques, quatre essais
échouent sur `#overlay.visible` du simulateur faute de moteur `/api` — c'est un
artefact de montage, pas un défaut du site (9/13 puis 13/13 avec le bon serveur).

## 3. Le point `320-130` : non reproduit

Sur les 2 470 mesures de la matrice, les 272 mesures ciblées et les 144 mesures
d'A/B, **aucune** ne produit de défilement horizontal, y compris
`transparence.html` à 320 px avec le texte à 130 %, les six présentations,
le contraste et l'espacement renforcés, en mobile comme en non mobile.

Deux lectures sont possibles et le relevé ne tranche pas entre elles :

- le débordement de 24 px tenait à un réglage du harnais A/B du 6 novembre qui
  n'a pas été reconstitué ici ;
- ou il a disparu avec la restructuration de #281, sans qu'aucune règle CSS
  n'ait été changée.

**Aucune conclusion « corrigé » n'est tirée** : rien n'a été modifié dans le
site. L'entrée plus ancienne qui mentionne ce débordement reste dans les
avancées avec sa date ; ce relevé s'y ajoute, il ne l'efface pas. La suite à
donner est de conserver la mesure et de ne plus présenter ce point comme un
défaut constaté sur la version publiée, sans pour autant l'affirmer résorbé.

## 4. Deux limites que la mesure a fait apparaître

### 4.1 Un faux positif de la sonde, pas du site

Les 2 470 mesures comptent chacune **un** « texte sous 12 px » : toujours
`span.customize-settings-chevron`, `font-size: 0`. Ce chevron est déclaré
`aria-hidden="true"` et dessiné par un masque SVG ; `font-size: 0` annule le
caractère `⌄` d'origine pour qu'il ne s'affiche pas sous le masque. Le critère
« corps de texte inférieur à 12 px » ne doit pas s'appliquer à un décor sans
texte lisible — `outils/cadrages.py` l'avait déjà écarté pour la même raison
(`font-size: 0` jugé illisible). **L'auditeur `auditer-affichages.mjs` sort
donc en code 1 sur un site sans défaut de ce critère.** Correction à faire dans
l'outil, pas dans la feuille de style : écarter les éléments `aria-hidden` dont
le corps est nul, et nommer cet écart. Cette correction n'est pas faite dans ce
lot : elle demande un banc qui exécute réellement le filtre, alors que le banc
actuel remplace le navigateur par un faux qui renvoie directement les compteurs.

> **Suite, 12 novembre 2026.** La correction est faite dans l’outil : le filtre
> écarte un `aria-hidden` **dont le corps est nul**, compte les décors écartés
> (`nbDecorsEcartes`) et nomme chacun dans le rapport. Le banc
> `test_auditer_affichages.mjs` ne se contente plus du faux : il extrait du
> script la fonction de mesure réellement envoyée au navigateur et l’exécute sur
> trois DOM témoins — le décor à écarter, un vrai texte de 11 px à conserver, et
> un `aria-hidden` visible de 11 px qui doit rester compté. Trois mutations de
> `test_mutations_affichages.py` et une garde de `verifier-affichages.py`
> tiennent la décision. Le paragraphe ci-dessus reste tel qu’il a été écrit le
> 6 novembre ; ce qui l’a changé est daté ici. **Aucune mesure réelle n’a été
> rejouée** : le navigateur n’était pas disponible dans cet environnement.

### 4.2 Dix agrandissements d'image réellement mesurés

Dans les dix modes, `index.html` au format « tel paysage 844 » (844 × 390,
densité 3×) affiche `accueil-logo-mrsc-3d-1400.avif` à 698 px CSS, soit
**2 094 pixels d'appareil pour une source de 1 400 pixels** (facteur 1,50).
Le critère de netteté du dépôt demande l'inverse : la source doit fournir au
moins autant de pixels que l'écran en affiche.

La cause est lisible dans la feuille : le commentaire voisin des plafonds de
densité dit encore que l'emblème de l'accueil « est vectoriel » depuis le
24 octobre 2026 et que les quatre paliers (700, 560, 466, 400 px) « ne
protégeaient plus rien ». Or l'accueil sert désormais un bitmap 800/1 400 px
(`index.html`), les tracés vectoriels ayant été rejetés ce même 24 octobre.
**Le commentaire décrit un état qui n'est plus celui du HTML.**

Réintroduire un plafond de densité réduirait la taille affichée de l'emblème sur
les écrans 3× : c'est un arbitrage entre netteté et place occupée, donc une
décision de l'association, pas une correction mécanique. Ce lot la consigne
sans la prendre. Les dix occurrences exactes sont dans le relevé JSON.

## 5. Ce que ce relevé ne prouve pas

- Un seul navigateur (Chromium 153), un seul système, aucune personne, aucun
  lecteur d'écran, aucun zoom natif du navigateur, aucune mesure de contraste
  ni de préférence `prefers-reduced-motion`.
- Les compteurs mécaniques ne disent rien de la lisibilité réelle, de la
  fidélité visuelle des deux commandes de l'en-tête ni de la compréhension de
  la page Transparence : la validation humaine du 6 novembre porte sur la
  structure, pas sur le fond des textes.
- Le relevé JSON est un résumé des compteurs, pas la preuve que la mesure a eu
  lieu : la preuve est la commande ci-dessus et le rapport complet qu'elle écrit.
- Le faux positif de la sonde et les dix agrandissements restent ouverts ; ce
  document les nomme, il ne les résout pas.
