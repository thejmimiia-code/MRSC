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

1. parcourt les 96 pages publiques (13 pages d’information à la racine, dont l’accueil et la page 404, 82 fiches et la page du simulateur) ;
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

Le détail page par page est régénéré dans [`poids-pages.md`](poids-pages.md). Les 96 pages restent sous les budgets de travail après la passe.

### 4.2 Images : formats et qualité

Trois images représentaient l’essentiel du poids : `accueil-logo-mrsc-3d.jpg` (236,0 Kio), `mondes-savoirs-hero.jpg` (370,7 Kio) et `escales-anglais-hero.jpg` (180,5 Kio). Chacune a reçu des variantes AVIF (qualité 60) et WebP (qualité 80), en 800 px et à sa largeur d’origine (1 400 px ou 1 672 px) ; une variante 1 200 px a été ajoutée pour l’atlas, affiché dans une colonne plus étroite.

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
| Poids des pages | `python3 outils/verifier-poids-pages.py` | 96 pages sous 300 Kio mobile et 450 Kio grand écran (gzip estimé) |
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
