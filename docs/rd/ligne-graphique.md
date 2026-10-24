# Ligne graphique M.R.S.C. — décision du 24 octobre 2026

## Direction commune

Le registre retenu est photographique et documentaire, avec une illustration minimale. Une photographie doit montrer un sujet identifiable et être accompagnée de sa provenance et de ses droits ; une image de synthèse ne doit jamais être présentée comme une photographie réelle. Les schémas sont réservés à l'explication de relations : pas de géométrie décorative ajoutée, de joyau, de dégradé multicolore ou de mascotte.

Le logo officiel n'est ni redessiné ni réinterprété. Le fichier `logo-mrsc.jpg` n'a pas été modifié. Les images antérieures de l'accueil et d'Apprendre ont été restaurées ; ce sont des illustrations de synthèse existantes, **pas des photographies documentaires**. Cette restauration n'est donc pas présentée comme l'achèvement de la migration photographique de tout le site.

Pour les nouveaux visuels, les titres, légendes et sources restent en HTML, hors des images. L’image d’identité restaurée contient déjà son sigle et sa dénomination : elle est conservée telle quelle à la demande explicite de restauration. Pas de texte éditorial superposé à une photographie sans mesure du contraste au point le moins favorable. Palette : couleurs existantes du site, sans ajouter une palette décorative à chaque image. Conserver l'espace autour du sujet, sa proportion native et une légende précise plutôt qu'un cadrage qui coupe l'identité.

## Restauration et résolution

Les cinq fichiers `accueil-logo-mrsc-3d*` viennent du commit `be842fb17116d9a20e1246c5e15c9bb908340671`, parent de leur suppression. Ils ont été récupérés depuis GitHub, sans réencodage ni agrandissement. Le manifeste `derives-images.json` retrouve les empreintes et paramètres d'origine (AVIF 78, WebP 88). Le JPEG mesure 1400 × 933 pixels, 241 614 octets.

L'accueil est centré et plafonné à **700 pixels CSS**, afin de disposer de deux pixels source par pixel CSS avec la variante 1400. Ce choix réduit sa taille sur grand écran au lieu d'inventer des détails. Le ratio natif 1400/933 est conservé : imposer un bandeau 2:1 rognerait le visuel restauré. L'illustration d'Apprendre retrouve sa source 1672 × 941 et son ratio, sans recadrage.

Le schéma IA n'est pas un logo. Ses pastilles et les extrémités des rayons utilisent les mêmes coordonnées à toutes les largeurs. Les déplacements mobiles indépendants sont retirés. La question auparavant enfermée dans le petit cercle central rejoint la légende HTML : elle ne déborde plus du disque quand on agrandit le texte.

## Contrôle reproductible, périmètre exact

`outils/verifier-graphismes.cjs` mesure **trois visuels**, pas l'ensemble du site :

- accueil : `.home-hero-visual` ;
- Apprendre : `.english-promo-art` ;
- IA : `.ai-constellation`.

Matrice : 320, 360, 390, 768, 1024, 1280 et 1440 pixels ; texte 75, 85, 100, 115 et 130 % ; six présentations ; mode normal, contraste et espacement renforcés ensemble, couleurs forcées ; densités 1 et 2. Soit **3 780 relevés**. Bilan final : **0 échec**, écart maximal d’ancre 0,022 pixel ; 420 relevés consignent une image volontairement masquée en couleurs forcées.

Pour les images : décodage de la variante réellement chargée avec `createImageBitmap` (la valeur `naturalWidth` d'un `srcset` est corrigée de la densité et ne mesure pas ses pixels physiques), ratio à 0,01 près, densité disponible, sortie horizontale du cadre et de l'écran. En couleurs forcées, l'illustration d'Apprendre est masquée par la règle existante et ce cas est enregistré, pas compté comme une image mesurée.

Pour le schéma : écart entre centre de chaque pastille et centre du point SVG ≤ 2 pixels, absence de chevauchement des boîtes des pastilles entre elles ou avec le disque central, absence de sortie du cadre et de débordement horizontal du texte. Toute erreur fait sortir le programme avec le code 1 ; une panne du harnais donne le code 2.

```sh
npm install --prefix /tmp/mrsc-browser puppeteer-core@25.16.0 @sparticuz/chromium@153.0.0
# Servir le dépôt sur le port 4181 dans un autre terminal.
MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules \
  MRSC_CAPTURES=/tmp/mrsc-captures node outils/verifier-graphismes.cjs
```

`MRSC_TEST_URL` permet un autre serveur ; `MRSC_GRAPHISMES_JSON` change la sortie. `MRSC_MUTATION=distorsion`, `densite` ou `ancre` injecte un défaut dans le navigateur seulement, sur un relevé ciblé. Les trois mutations ont été exécutées et chacune a produit le code 1 : image écrasée, source trop petite, pastille désalignée. Les captures restent hors du dépôt ; le relevé JSON est conservé dans `audit-graphismes-2026-10-24.json`.

## Limites et suite obligatoire

Ce contrôle ne mesure **pas** le contraste pixel par pixel, les artefacts de compression, le sens d'un recadrage, l'ensemble des SVG/canvas/décors du site, ni les navigateurs autres que Chromium. Les crans de texte ne sont pas le zoom du navigateur. Les densités supérieures à 2, le téléphone réel, le lecteur d'écran et la lecture par une personne extérieure restent à vérifier. La netteté perçue n'est pas démontrée par la densité seule.

Avant de déclarer la ligne graphique appliquée partout : inventorier les autres visuels, distinguer documents/photographies/synthèses, vérifier provenance et droits, étendre les contrôles et faire relire les rendus réels. Aucun taux de conformité RGAA/WCAG n'est déduit de cette passe.

## Correctif de chargement après la capture smartphone

La capture reçue après la PR #188 révèle un angle mort : nouveau HTML et ancien
CSS peuvent coexister. Le mélange est reproduit avec le CSS de `f3c4ddf`, puis
avec les anciennes règles de positionnement dans `test-cache-css-ia.cjs`.
La page IA appelle désormais `site.css?v=<empreinte>` ; après tout changement
CSS, lancer `python3 outils/versionner-css-ia.py`. Le mode `--verifier` est
bloquant en CI si la référence ne correspond plus au contenu de la feuille.

Le test simule une ancienne réponse à l'URL non versionnée ; il vérifie que la
nouvelle URL charge les règles cohérentes avec le dessin. Ce n'est pas une
inspection du cache réel du téléphone. Il couvre 12 cas, dont la présentation
compacte à 320 px et texte 130 %. Voir le [relevé cache](audit-cache-css-ia-2026-10-24.json).
