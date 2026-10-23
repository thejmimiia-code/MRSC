# Poids, sobriété et accès — mesure et prototype (octobre 2026)

**Note de travail datée du 17 octobre 2026. État : mesure locale, prototype d’optimisation et garde-fou automatisé, non audités par un tiers.** Ce document ne constitue ni un audit RGESN, ni une déclaration de conformité, ni un bilan carbone, ni une mesure de performance sur appareil réel. Il décrit une méthode reproductible, des chiffres obtenus dans l’environnement de développement et les limites qui subsistent.

## 1. Question et périmètre

**Question :** comment réduire le poids transféré des pages publiques et la dépendance à un réseau rapide, sans retirer de contenu, sans casser le repli sans JavaScript et sans ajouter de service tiers ?

Le périmètre couvre les pages publiques du dépôt : accueil, apprentissage, atlas **Les Mondes**, pages d’information, fiches autonomes et page générée du simulateur. Les fonctions Python, l’API et les documents de travail ne sont pas concernés par cette passe.

**Ce que cette note ne traite pas :** la consommation énergétique réelle des visiteurs, le remplacement des terminaux, l’hébergement, la compression HTTP du serveur, les budgets de performance par pays ou par appareil, et la mesure de l’impact carbone. Le poids transféré est un **proxy** technique, pas une empreinte environnementale.

## 2. Pourquoi ce sujet compte — sources et précautions

Les chiffres disponibles ne sont pas interchangeables. Deux publications françaises récentes donnent des ordres de grandeur différents selon leur périmètre et leur méthode ; il serait faux de les moyenner ou de les présenter comme une seule vérité.

| Repère | Valeur publiée | Périmètre et précaution | Source consultée |
| --- | --- | --- | --- |
| Part du numérique dans l’empreinte carbone française | **4,4 %** en 2022, environ **29,5 Mt CO₂e** | Mise à jour 2024 de l’étude ADEME ; périmètre plus large que les seuls produits et services numériques | [ADEME — dossier de presse « Numérique et environnement », 9 janvier 2025](https://www.ademe.fr/wp-content/uploads/2025/01/dossier-de-presse-numerique-et-environnement-090125.pdf) |
| Même indicateur, autre méthode | **21 Mt CO₂e**, soit **3,2 %** de l’empreinte française en 2023 | Comptabilité des « produits et services du numérique » ; ne pas confondre avec le chiffre ADEME ni conclure à une baisse | [INSEE — Empreinte carbone et consommation énergétique du numérique, 14 octobre 2025](https://www.insee.fr/fr/statistiques/8616811) |
| Répartition de l’empreinte | **79 %** équipements, **16 %** centres de données, **5 %** réseaux ; la fabrication domine l’empreinte des équipements (environ **80 %**) | Étude ADEME–Arcep ; ordres de grandeur nationaux, pas une mesure du site M.R.S.C. | [Arcep — dossier de presse du lot 3, mars 2023](https://www.arcep.fr/uploads/tx_gspublication/dossier-presse-Etude-Ademe-Arcep-lot3_mars2023.pdf) |
| Poids médian d’une page | **2 559 Kio** sur mobile et **2 862 Kio** sur ordinateur en juillet 2025 ; images : 911 Kio et 1 058 Kio | HTTP Archive, millions de sites ; médianes, fortement tirées par les sites les plus lourds | [HTTP Archive — Web Almanac 2025, Page Weight](https://almanac.httparchive.org/en/2025/page-weight) |
| Cadre méthodologique français | **78 critères** répartis en 9 familles (stratégie, spécifications, architecture, UX/UI, contenus, frontend, backend, hébergement, algorithmie) | Référentiel général d’écoconception des services numériques, version 2024 publiée le 17 mai 2024 par l’Arcep et l’Arcom avec l’ADEME, la DINUM, la CNIL et l’Inria ; cadre volontaire, pas une certification automatique | [RGESN 2024](https://ecoresponsable.numerique.gouv.fr/publications/referentiel-general-ecoconception/) |
| Cadre international émergent | Premier **Draft Note** public le 2 octobre 2025 : 92 lignes directrices et 254 critères de réussite annoncés | Web Sustainability Guidelines du W3C Sustainable Web Interest Group ; documents de travail, non Recommendation, aucune conformité revendiquée | [W3C — WSG, première Draft Note](https://www.w3.org/news/2025/web-sustainability-guidelines-wsg-becomes-a-first-public-draft-note/) |

**Lecture pour le projet :** dans un service éditorial léger, le levier le plus accessible n’est pas de changer d’hébergeur mais de **réduire les octets réellement demandés** : images surdimensionnées, variantes inutiles, chargement de médias avant leur affichage, scripts et données non nécessaires au premier écran. L’accessibilité reste une contrainte simultanée : alléger ne doit pas supprimer le zoom, le clavier, le contraste, le repli sans JavaScript ou le texte alternatif.

## 3. Méthode de mesure

La mesure est **hors ligne et reproductible** :

```sh
python3 outils/verifier-poids-pages.py --rapport docs/rd/poids-pages.md
```

Le script :

1. parcourt les 98 pages publiques (13 pages d’information à la racine, dont l’accueil et la page 404, 84 fiches et la page du simulateur) ;
2. additionne le HTML, les feuilles de style locales, les scripts locaux et l’image retenue pour chaque emplacement ;
3. compresse chaque fichier avec gzip niveau 9 pour approcher le transfert ;
4. estime deux scénarios : le plus petit candidat `srcset` (mobile ou petit écran) et le plus grand (grand écran à forte densité) ;
5. applique des budgets de travail : **300 Kio** compressés en scénario mobile, **450 Kio** en grand écran.

**Ce que la méthode ne mesure pas :** latence, débit réel, cache, TLS, compression Brotli ou configuration de l’hébergeur, coût énergétique, rendu, Core Web Vitals, mémoire du navigateur. Les icônes d’installation, les polices (le site n’en charge pas de distantes) et les médias chargés après une action volontaire sont exclus. Les chiffres sont donc des **comparaisons internes**, pas des mesures absolues.

## 4. Résultats mesurés

### 4.1 Poids estimé des pages principales

Mesure du 17 octobre 2026, avant et après la conversion des trois grandes illustrations. Les valeurs sont en Kio compressés (gzip simulé) ; « mobile » retient le plus petit candidat d’image, « grand écran » le plus grand.

| Page | Avant, mobile | Après, mobile | Écart | Avant, grand écran | Après, grand écran | Écart |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `index.html` | 289,7 | 106,2 | −63,3 % | 289,7 | 168,1 | −42,0 % |
| `apprendre.html` | 459,3 | 158,8 | −65,4 % | 459,3 | 308,6 | −32,8 % |
| `anglais-aventure.html` | 662,7 | 183,0 | −72,4 % | 662,7 | 332,7 | −49,8 % |
| `ia-societe.html`, `transparence.html`, fiches types | 52–59 | 52–59 | inchangé | 52–59 | 52–59 | inchangé |
| `simulateur/index.html` | 71,4 | 71,4 | inchangé | 71,4 | 71,4 | inchangé |

Le détail page par page est régénéré dans [`poids-pages.md`](poids-pages.md). Les 98 pages restent sous les budgets de travail après la passe.

### 4.2 Images : formats et qualité

Trois images représentaient l’essentiel du poids : `accueil-logo-mrsc-3d.jpg` (236,0 Kio), `mondes-savoirs-hero.jpg` (370,7 Kio) et `escales-anglais-hero.jpg` (180,5 Kio). Chacune a reçu des variantes AVIF (qualité 60) et WebP (qualité 80) — **portées à 78 et 88 le 23 octobre 2026, voir le § 4.2 quinquies** —, en 800 px et à sa largeur d’origine (1 400 px ou 1 672 px) ; une variante 1 200 px a été ajoutée pour l’atlas, affiché dans une colonne plus étroite.

| Image | JPEG source | AVIF 800 px | WebP 800 px | AVIF pleine largeur | WebP pleine largeur |
| --- | ---: | ---: | ---: | ---: | ---: |
| `accueil-logo-mrsc-3d` | 236,0 Kio | 52,0 Kio | 67,4 Kio | 113,9 Kio (1 400) | 155,0 Kio (1 400) |
| `mondes-savoirs-hero` | 370,7 Kio | 69,9 Kio | 76,0 Kio | 219,6 Kio (1 672) | 252,4 Kio (1 672) |
| `escales-anglais-hero` | 180,5 Kio | 30,0 Kio | 35,0 Kio | 86,6 Kio (1 672) | 107,0 Kio (1 672) |

**Contrôle de qualité :** les images ont été comparées à leur source avec ImageMagick par PSNR après normalisation en sRGB. Un premier calcul direct donnait des valeurs absurdes (12–14 dB) parce que le décodeur AVIF renvoyait un espace YCbCr ; après conversion des deux images en PNG sRGB, les valeurs sont cohérentes :

- AVIF q60, pleine largeur : 38,8 / 36,4 / 38,7 dB ;
- WebP q80, pleine largeur : 38,5 / 36,0 / 38,9 dB ;
- AVIF q60, 800 px : 36,5 / 31,9 / 34,9 dB ;
- WebP q80, 800 px : 36,7 / 32,8 / 35,8 dB.

Le PSNR n’est ni une mesure perceptuelle ni une preuve d’absence d’artefacts. Deux contrôles complémentaires ont été faits sur `mondes-savoirs-hero` :

- **Rendu navigateur** : les trois versions (AVIF 800, WebP 800, JPEG source) ont été affichées côte à côte dans Chromium sans interface, à 400 px de large. Les moyennes de luminance coïncident à 0,0005 près (0,3026 / 0,3031 / 0,3029) ; à l’œil, à cette taille, aucune différence de teinte ou de contraste n’a été relevée.
- **Écart mesuré sur la source redimensionnée** : comparées à la source ramenée à 800 px, les variantes présentent une erreur absolue moyenne de **1,0 à 1,6 %** de la dynamique (soit environ 2,5 à 4 niveaux sur 255) et un PSNR de 31,9 à 36,7 dB. Une partie de cet écart vient du rééchantillonnage, pas de la compression.
- **Recadrage à l’échelle 1** : les détails de tuiles, de ponts et de végétation restent lisibles dans les trois formats ; aucune dégradation évidente n’a été relevée à cette taille.

Ces contrôles ont été faits par l’agent, pas par un panel humain ni avec un outil perceptuel (SSIM, VMAF, Butteraugli). Ils ne remplacent pas une revue visuelle humaine sur écran réel, en particulier pour les dégradés de ciel et les zones sombres.

### 4.2 bis — Le vrai plafond de netteté était le choix de variante, pas la compression (22 octobre 2026)

**Mise à jour du même jour :** la déclaration `150vw` décrite ci-dessous a été abandonnée quelques heures plus tard. Le héros est devenu un bandeau au ratio naturel sous 700 px (§ 4.2 ter), ce qui supprime l’agrandissement sur téléphone *sans* dépasser le budget : le compromis de poids raconté plus bas n’a donc plus lieu d’être.

La revue visuelle humaine demandée au § 6 a eu lieu : la qualité des illustrations des mondes a été jugée insuffisante. La mesure a écarté deux fausses pistes avant d’en trouver deux vraies.

**Écartées.** La compression n’est pas en cause : en sRGB, l’AVIF q60 pleine largeur de `mondes-savoirs-hero` mesure **36,4 dB** de PSNR, comme l’indiquait déjà ce document ; un calcul direct redevient absurde (12,7 dB) pour la raison déjà connue — le décodeur renvoie du YCbCr. Régénérer l’illustration ne pouvait pas aider non plus : le générateur d’images disponible ici plafonne à **1 376 × 768 px**, soit moins que le master actuel de 1 672 × 941 — une régénération aurait donc *dégradé* la résolution.

**Trouvées.** Deux défauts réels, mesurables, tous deux dans la façon de servir l’image :

1. **Le héros des mondes déclarait `sizes="100vw"` alors qu’il est posé plus large que l’écran.** Le CSS lui impose `object-fit: cover` dans une boîte de 180vw de haut : sur un téléphone de 390 px, l’image est mise en page sur ≈ 1 247 px de large, puis rognée. En déclarant 100vw, le navigateur croyait n’avoir que 390 px à couvrir et choisissait la variante **800 px**. Résultat : un agrandissement d’environ **3,1×** en pixels d’appareil à 2×. La déclaration devient `(max-width: 430px) 150vw, (max-width: 700px) 105vw, 100vw`, ce qui fait choisir la variante **1 200 px** et ramène l’agrandissement à ≈ **2,1×**, soit un tiers de netteté gagné.

2. **Le décor 3D des cinq missions plafonnait la densité à 1,5.** Le tampon du canvas était rendu à `min(devicePixelRatio, 1.5)` puis agrandi par le CSS sur tout écran à 2× ou 3× : arêtes floues, précisément sur les appareils où l’on regarde le plus ces décors. Le plafond passe à 2, borné par un budget de 4 Mpx pour les appareils modestes. Ce rendu n’a lieu qu’une fois par monde, pas à chaque image : le coût reste ponctuel.

**Le compromis de poids est explicite.** La déclaration honnête serait ≈ 320vw (la largeur réellement mise en page). Elle aurait fait choisir la variante 1 672 px et porté la page à ≈ **322 Kio** de mobile, au-dessus du budget de travail de 300 Kio. La valeur retenue, 150vw, garde la page à ≈ **240 Kio** (mesuré par gzip sur les fichiers réellement choisis) en abandonnant une partie du gain possible.

**Ce que cela ne règle pas.** Le master reste 1 672 × 941. Sur un écran à 2× (portable Retina), il est affiché sur jusqu’à 2 880 px d’appareil : l’agrandissement résiduel est de **1,7×**, et il faudrait une source de 2 560 à 2 880 px pour le supprimer. Aucun traitement local ne crée ce détail — un agrandissement Lanczos produit un fichier plus gros, pas une image plus nette, et n’a donc pas été retenu. **La netteté complète dépend d’une illustration source plus grande**, que ce dépôt ne contient pas.

Un troisième point, relevé en passant : `outils/verifier-poids-pages.py` annonce dans sa docstring retenir le candidat « selon `sizes` » mais ne lit pas cet attribut — il prend le plus petit et le plus grand candidat du `srcset`. Ses chiffres restent des majorants prudents, mais ils ne reflètent pas le choix réel du navigateur ; le calcul ci-dessus a donc été fait à la main, avec les mêmes fichiers.

### 4.2 ter — La bonne réponse était la géométrie, pas la déclaration `sizes` (22 octobre 2026)

Le signalement a été reformulé : « les images qui ne sont pas au bon ratio, il ne faut pas voir les pixels ». La mesure a montré que le défaut n’était pas la déclaration `sizes` (corrigée au § 4.2 bis) mais la **géométrie du héros sur téléphone**.

**Le calcul qui tranche.** Le héros imposait `object-fit: cover` dans une boîte de 150 à 180vw de haut. Sur un téléphone de 390 px élargi à 3×, remplir cette boîte demande **3 742 px** de source ; à 430 px, **4 126 px**. Il aurait donc fallu une illustration de plus de 4 000 px de large pour un simple téléphone — aucune variante réaliste ne l’aurait fournie, et le master lui-même (1 672 px) en était très loin.

**La décision.** Sous 700 px, le héros n’est plus une image de fond recadrée : c’est un **bandeau au ratio naturel de l’illustration** (16/9), et le texte passe dessous sur le fond bleu nuit. La source nécessaire devient la largeur de l’écran :

| Écran | Source nécessaire avant (cover) | Après (bandeau) | Variante choisie |
| --- | ---: | ---: | --- |
| 320 px @3× | 3 072 px | **960 px** | 1 200 px |
| 360 px @3× | 3 456 px | **1 080 px** | 1 200 px |
| 390 px @3× | 3 742 px | **1 170 px** | 1 200 px |
| 430 px @3× | 4 126 px | **1 290 px** | 1 672 px |

Autrement dit : plus **aucun agrandissement** sur les cinq largeurs de téléphone testées, alors que le facteur atteignait 3,1×. Le poids ne bouge pas sur les téléphones courants (1 200 px, ≈ 240 Kio de page) ; seuls les très grands téléphones à 3× (430 px) passent à la variante 1 672 px, soit ≈ 322 Kio, au-dessus du budget de travail de 300 Kio — conséquence assumée et mesurée, pas subie.

**Mise à jour du même jour :** la géométrie décrite ci-dessous a été remplacée quelques heures plus tard par la géométrie hybride du § 4.2 quater, qui supprime l’agrandissement résiduel sur grand écran au lieu de l’assumer. Les chiffres restent exacts pour la version alors livrée.

**Ce qui reste, et qui ne se règle pas ici.** Sur grand écran, le héros reste une image plein cadre : la source nécessaire vaut la largeur de l’écran en pixels d’appareil. Avec un master de 1 672 px, l’agrandissement résiduel est de **1,15× à 1 920 px (1×)**, **1,53× à 1 024 px (2×)**, **1,72× à 1 440 px (2×)** et **1,53× à 2 560 px (1×)**. Pour l’annuler il faudrait une illustration d’au moins **2 880 px** de large. Aucun fichier du dépôt ne le permet, et un agrandissement logiciel (Lanczos) produirait un fichier plus lourd sans créer un seul détail : il n’a pas été fait.

**Garde-fou ajouté.** `outils/verifier-budgets-visuels.py` vérifie désormais quatre choses : que le bandeau mobile est bien en place (règle `.adventure-hero-art` en `position: static` et `height: auto`, voile masqué, `min-height: 0` aux deux paliers), que `sizes` reste exact, qu’aucun palier de téléphone testé ne réclame plus que la plus grande variante servie, et que les facteurs de grand écran ne dépassent pas les valeurs constatées. Trois mutations volontaires — retour au `cover`, rétablissement de la boîte à 180vw, retrait de la variante 1 672 px — ont été détectées avec un message nommant la cause.

**Limites.** Aucun navigateur n’a été lancé : la géométrie est vérifiée par calcul et par lecture du CSS, pas par rendu. Le bandeau mobile change la composition (texte sous l’image, voile supprimé) et n’a pas été vu par une personne ; c’est le premier point à regarder sur téléphone.

### 4.2 quater — Géométrie hybride et procédure d’arrivée d’un master plus large (22 octobre 2026)

La régénération des illustrations a été **écartée sur mesure** : le générateur disponible ici plafonne à environ 1,05 million de pixels, soit 1 376×768 en 16:9, contre 1 573 000 px pour le master actuel de 1 672×941. Refaire les images les aurait **réduites de 33 %**. La personne responsable du site fournira donc un master d’au moins 2 880 px, et a retenu une géométrie hybride en attendant.

**La géométrie hybride.** Le plein cadre — celui qui donne sa composition au héros — n’est conservé que là où il n’étire rien :

| Contexte | Traitement | Source nécessaire |
| --- | --- | --- |
| ≤ 700 px (téléphone, tablette étroite) | bandeau au ratio naturel, texte dessous | largeur de l’écran × densité |
| 701 à 1 679 px en 1× | plein cadre `cover` | ≤ 1 672 px |
| 701 px et plus en 2× ou 3× | panneau contenu, plafond **836 px** | 1 672 px au plus |
| 1 680 px et plus en 1× | panneau contenu, plafond **1 672 px** | 1 672 px au plus |

Résultat vérifié : **aucun agrandissement** sur les 17 combinaisons écran × densité testées, de 320 px à 3× à 2 560 px à 1×. Le 1,72× qui subsistait sur un portable Retina a disparu — au prix d’un panneau centré plutôt que d’un fond pleine largeur sur ces écrans.

**Procédure quand le master arrive** (aucune modification de code n’est nécessaire avant l’étape 4) :

1. déposer le fichier en remplacement de `assets/images/mondes-savoirs-hero.jpg`, largeur ≥ 2 880 px, ratio 16:9, sans texte incrusté ;
2. lancer `python3 outils/optimiser-images.py` : le script ne produit jamais de variante plus large que la source, et ajoute désormais automatiquement la largeur native et les paliers 2 560 et 2 880 px ;
3. vérifier le manifeste avec `python3 outils/optimiser-images.py --verifier` ;
4. compléter les `srcset` et `imagesrcset` de `anglais-aventure.html` et `apprendre.html` avec les nouvelles largeurs — la porte échoue tant que ce n’est pas fait, avec un message explicite ;
5. relever `--hero-art-max: 836px` (2×) et `--hero-art-max: 1672px` (1× très large) dans `anglais-aventure.css` et dans `outils/verifier-budgets-visuels.py` : avec un master de 2 880 px, le panneau peut passer à 1 440 px, ce qui rend le plein cadre inutile ;
6. refaire la mesure complète et consigner le nouveau poids.

**Ce qui reste vrai en attendant.** Le master de 1 672 px suffit désormais à tous les cas, mais un panneau de 836 px est plus petit qu’un fond pleine largeur : la composition change sur Retina. Aucun navigateur n’a été lancé ici, donc ce basculement n’a pas été vu.

### 4.2 quinquies — « La version smartphone est pixélisée » : la mesure a démenti l'agrandissement (23 octobre 2026)

Le signalement ne portait plus sur un cadrage mais sur la netteté perçue sur téléphone. Trois hypothèses ont été mesurées ; **deux étaient fausses**, et la vraie cause n'était pas celle qu'on croyait.

**Première fausse piste : le `srcset` ne tiendrait pas compte de la densité.** Une première sonde lisait `naturalWidth` et en concluait qu'à 390 px de large et 3× le navigateur ne servait que 390 pixels de source pour 1 170 nécessaires. C'était un **artefact de mesure** : pour une image choisie par descripteurs `w`, `naturalWidth` est rapporté *après* correction de densité (`1200 / 3,08 ≈ 390`). La mesure correcte recharge le fichier choisi hors `srcset` et lit sa largeur réelle. Refaites sur **42 combinaisons** page × écran × densité (320 px à 2× jusqu'à 2 560 px à 1×, `anglais-aventure.html`, `index.html`, `apprendre.html`) :

| Page | Exemple de profil | Fichier servi | Besoin réel | Verdict |
| --- | --- | ---: | ---: | --- |
| `anglais-aventure.html` | 390 px @3× | 1 200 px | 1 170 px | 1:1, aucun agrandissement |
| `anglais-aventure.html` | 430 px @3× | 1 672 px | 1 290 px | marge |
| `anglais-aventure.html` | 1 920 px @2× | 1 672 px | 1 672 px | exact |
| `anglais-aventure.html` | 1 920 px @3× | 1 672 px | 1 671 px | exact (panneau réduit à 557 px) |
| `index.html` | 390 px @3× | 1 400 px | 1 099 px | marge |
| `apprendre.html` | 1 920 px @3× | 1 672 px | 1 491 px | marge |

**Aucun déficit sur les 42 profils.** La géométrie hybride du § 4.2 quater fait donc ce qu'elle annonce : le navigateur ne reçoit jamais moins de pixels qu'il n'en affiche. L'agrandissement n'était pas la cause du flou.

**Deuxième fausse piste, partiellement vraie : le tampon du décor 3D.** Le plafond `min(devicePixelRatio, 2)` du § 4.2 bis bridait encore les téléphones à 3×. Mesuré après ouverture d'une mission, tampon contre dalle :

| Écran | Avant | Après | Écart |
| --- | --- | --- | --- |
| 390 px @3× | 642 × 402 | 964 × 602 | 322 px de flou en moins |
| 430 px @3× | 722 × 452 | 1 084 × 677 | 362 px |
| 820 px @2× | 1 435 × 897 | 1 435 × 897 | déjà exact |

Le plafond passe à **4×** et le budget de tampon de 4 à **6 Mpx** (`DENSITE_MAX = 4`, `BUDGET_PIXELS = 6_000_000`). Le rendu est un rendu vectoriel WebGL : capturé à 3× après clic sur une mission, il montre des arêtes franches et des diagonales sans escalier.

**Cause réelle et corrigée : la qualité d'encodage.** L'AVIF était encodé en **qualité 60**. Comparé à la source ramenée à 800 px, après normalisation sRGB :

| Qualité AVIF | PSNR | Poids (800 px) | Lecture à 200 % |
| --- | ---: | ---: | --- |
| 60 | 31,9 dB | 69,9 Kio | rambardes du pont et feuillages fondus, aplatissement des pages de livres |
| 72 | 32,8 dB | 90,4 Kio | détails revenus, feuillages encore mous |
| **78** | **33,2 dB** | **104,9 Kio** | **retenu : rambardes, tuiles et feuillage distincts** |
| 82 | 33,5 dB | 119,3 Kio | gain non perceptible au-delà |

Le déficit était donc visible **parce que l'image est servie en 1:1** : à l'échelle exacte du pixel, un bloc de compression de 8 × 8 px se lit directement comme du pixel. Qualités portées à **AVIF 78 et WebP 88** (le WebP reste un repli ; au-delà de 88, la variante 1 672 px dépasserait son JPEG source, ce que l'outil refuse — et il a raison : un dérivé plus lourd que sa source n'a pas de sens).

**Poids après la passe** (gzip estimé, `outils/verifier-poids-pages.py`) : `anglais-aventure.html` 227,6 Kio mobile / 415,9 Kio grand écran, `apprendre.html` 202,8 / 391,1, `index.html` 140,4 / 238,7. Les 98 pages restent sous 300 Kio et 450 Kio. Le total des variantes passe de 1 553 à **2 199 Kio** dans le dépôt, pour des fichiers servis plus lourds de 20 à 35 % sur les images — le prix explicite de la netteté.

**Garde-fous ajoutés** (`outils/verifier-affichages.py`, joués en CI) :

- `DENSITE_MAX ≥ 3`, `BUDGET_PIXELS ≥ 6 Mpx`, et **aucun `Math.min(devicePixelRatio, N)`** dans `anglais-aventure.js` — le plafond exact qui avait produit le flou ;
- qualité d'encodage **AVIF ≥ 78 et WebP ≥ 88** dans `outils/optimiser-images.py`, avec la ligne fautive nommée.

Trois mutations volontaires ont été rejouées : `DENSITE_MAX = 2`, retour du plafond `Math.min(window.devicePixelRatio || 1, 2)`, et retour aux qualités 60/80. Les trois sont détectées avec un message qui nomme la cause ; les fichiers ont été restaurés à l'identique (`diff` vide).

**Limite qui subsiste, énoncée telle quelle.** Le master reste 1 672 × 941. Tout ce qui précède est au mieux du 1:1 ; au-delà (un master de 2 880 px, voir la procédure du § 4.2 quater), il n'y a pas de détail supplémentaire à servir. Aucune revue humaine n'a eu lieu sur ce correctif : la mesure est celle d'un Chromium sans interface, pas d'un téléphone réel.

### 4.3 Stockage du dépôt

Les variantes ajoutent **1 553 Kio** au dépôt pour **787 Kio** d’images sources. Le dépôt grossit donc, alors que chaque visite transfère moins. C’est un compromis assumé : les sources restent la référence et le repli JPEG ; les variantes sont générées et vérifiées par [`outils/optimiser-images.py`](../../outils/optimiser-images.py), avec un manifeste d’empreintes [`derives-images.json`](derives-images.json).

## 5. Optimisations réellement intégrées

1. **Images responsives** : `<picture>` avec sources AVIF et WebP, `srcset` et `sizes`, repli `<img>` JPEG conservé.
2. **Dimensions correctes** : la hauteur déclarée de l’illustration d’accueil est passée de 788 à 933 px, conformément au fichier réel, pour réduire le décalage de mise en page.
3. **Priorité de chargement** : `fetchpriority="high"` sur l’image principale, `decoding="async"` sur les images concernées ; le préchargement de l’atlas déclare désormais le type AVIF et `imagesrcset`.
4. **Repli 3D différé** : l’image de secours de la scène n’est demandée que si le rendu WebGL échoue, au lieu d’être téléchargée à chaque visite puis masquée.
5. **Serveur local** : types MIME `image/avif` et `image/webp` ajoutés pour que l’aperçu local serve les variantes correctement.
6. **Réflow à 320 px** : les libellés de boutons longs peuvent passer à la ligne sur écran étroit ; la largeur du bouton compact de l’en-tête est réservée pour les deux libellés ; sous 240 px, le logo laisse la place aux commandes. Ces corrections ont été trouvées par les essais navigateur, pas supposées.
7. **Garde-fou** : `outils/verifier-poids-pages.py` échoue si une page dépasse les budgets ou si une ressource locale manque ; `outils/optimiser-images.py --verifier` contrôle le manifeste et les empreintes.

## 6. Tests exécutés et résultats

| Contrôle | Commande | Résultat |
| --- | --- | --- |
| Génération et manifeste d’images | `python3 outils/optimiser-images.py --verifier` | 3 sources, 14 variantes, manifeste et empreintes cohérents |
| Poids des pages | `python3 outils/verifier-poids-pages.py` | 98 pages sous 300 Kio mobile et 450 Kio grand écran (gzip estimé) |
| Essais navigateur | `MRSC_BROWSER_NODE_MODULES=… node outils/test-experience.cjs` | **8/8** essais réussis (Chromium sans interface, 320 → 240 px, 150 %, contraste et espacement) |
| Sélection des formats | sonde Puppeteer locale | AVIF sélectionné ; à 390 px, variante 800 ; à 768 px et 2×, variante 1 400 ; à 1 440 px, variante pleine largeur |
| Repli de la scène | sonde avec WebGL désactivé et clic sur une mission | image de secours chargée seulement à ce moment, AVIF 800 px, canvas masqué, aucun débordement |
| Porte du dépôt | vérificateurs R&D, fiches, simulateur, site statique, sécurité, intégration | réussis après régénération des fiches |

**Limites des essais :** Chromium sans interface fourni par `@sparticuz/chromium`, pas de Safari, Firefox, lecteur d’écran, appareil réel, réseau bridé ni mesure Lighthouse/CrUX. Les essais DOM et navigateur ne valent pas essai d’usage avec des personnes. Aucun test n’a été mené sur la production GitHub Pages ou Vercel.

### 4.4 Ce que l’hébergement sert réellement (GitHub Pages, 17 octobre 2026)

Une lecture des en-têtes a été faite depuis un runner GitHub, sur la version publiée (`https://thejmimiia-code.github.io/MRSC/`), avec `outils/verifier-publication.py` et un en-tête `Accept-Encoding: gzip, deflate, br`. Résultat daté, repris dans l’issue de suivi **#90** :

| Constat | Valeur relevée | Conséquence |
| --- | --- | --- |
| Disponibilité | 18/18 fichiers en **200** | Aucune variante oubliée dans la publication `_site` |
| Types d’images | `image/avif` et `image/webp` | GitHub Pages reconnaît les deux formats ; aucun `application/octet-stream` |
| Types de texte | `text/html`, `text/css`, `application/javascript`, `application/xml` | Rien à corriger côté hébergement |
| Compression | `Content-Encoding: gzip` sur les 9 fichiers texte ; aucune sur les images | Attendu : les images AVIF/WebP sont déjà compressées ; gzip sur 9 fichiers confirme que la négociation fonctionne |
| Cache | `Cache-Control: max-age=600` sur tous les fichiers | Dix minutes : une revisite proche est peu coûteuse, une mise à jour se propage vite |
| Octets servis | identiques aux tailles des variantes (ex. logo 800 AVIF : 53 242 octets) | Aucune transformation supplémentaire côté serveur |

**Confrontation avec l’estimation hors ligne** : sur les fichiers texte contrôlés, la compression gzip niveau 9 du script et celle réellement servie par Pages diffèrent de **+0,7 % à +4,2 %** (accueil 7 169 octets estimés pour 7 247 servis ; feuille de style 20 494 pour 21 355 ; script principal 7 285 pour 7 339 ; catalogue 41 939 pour 43 426 ; atlas 9 649 pour 9 770). L’estimation est donc **légèrement sous** les octets servis, jamais au-dessus ; les images AVIF/WebP, déjà compressées, sont servies à l’octet près. Les budgets de 300 et 450 Kio gardent une marge suffisante pour ce biais, puisque la page la plus lourde est estimée à 333 Kio. Cette confrontation porte sur le **transfert** de fichiers contrôlés, pas sur le rendu ni sur le temps de chargement.

**Ce que ces en-têtes ne prouvent pas :** ni la performance perçue, ni le comportement sur un appareil lent, ni la conformité RGESN, ni une empreinte carbone. Ils ne concernent pas Vercel : cette adresse héberge le simulateur du dépôt amont, pas les fichiers de ce dépôt. Le relevé est refait chaque mois, et à chaque modification du contrôleur ; il peut donc changer sans que cette note soit mise à jour.

## 7. Décisions et prochaines étapes

**Décisions prises dans cette passe :**

- conserver les JPEG sources comme référence et repli, ne jamais les supprimer au profit d’un format unique ;
- ne pas charger l’image de secours de la scène avant nécessité ;
- refuser un budget qui ne serait atteint qu’en supprimant du contenu, du texte alternatif ou le repli sans JavaScript ;
- ne pas ajouter de CDN, de police distante, de lecteur automatique ou de mesure d’audience pour « compenser » le poids.

**Prochaines actions, non exécutées ici :**

1. ~~Vérifier sur GitHub Pages les en-têtes réellement servis pour `.avif` et `.webp`, la compression et le cache.~~ **Fait le 17 octobre 2026** (§4.4, issue #90) : types corrects, gzip sur les fichiers texte, cache de 600 secondes. Le relevé reste à refaire chaque mois via le workflow ; une régression de type MIME serait signalée dans l’issue de suivi.
2. Faire une revue visuelle humaine des trois illustrations sur écran réel, à 100 % et à fort zoom.
3. Mesurer sur appareil et réseau réels (LCP, CLS, octets transférés) avec un outil accepté par l’association ; ne pas convertir ces mesures en bilan carbone.
4. Si un lecteur ancien ou un contexte à faible bande passante l’exige, tester une variante 1 000 px de l’image de secours et un chemin sans image décorative ; ne pas l’annoncer avant essai.
5. Intégrer progressivement les critères RGESN pertinents dans une auto-évaluation datée, avec un responsable par critère ; aucune conformité n’est revendiquée aujourd’hui.
6. Réexaminer annuellement, ou à chaque nouvelle illustration, les qualités, largeurs et budgets ; mettre à jour le manifeste et la note après mesure réelle.

## 8. Lien avec la prospective 2027–2030

Cette passe renforce une décision « sans regret » de la [note de prospective](prospective-2027-2030.md) : un socle léger, autonome et lisible reste utile dans les quatre futurs décrits (services stables, traçabilité fragile, réseau intermittent, archipel opaque). Elle ne prouve pas que ces futurs se réaliseront et ne remplace pas les arbitrages de l’association.
