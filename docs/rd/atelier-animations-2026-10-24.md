# Atelier animations 2,5D — 24 octobre 2026

## Demande et périmètre

L'utilisateur demande une page de tests accessible depuis Personnalisation, avec des animations 2D simulant la 3D et une palette issue de sa planche EVA. La page `animations.html` est un prototype public isolé : aucune nouvelle identité graphique n'est appliquée au reste du site. Les logos officiels existants sont conservés.

## Direction proposée, non encore validée

Brun nuit #211713 pour le fond ; crème #F4E6CE pour le texte ; cuivre #B77750 pour la matière ; rose #ED97AC pour un accent lumineux. Ce sont des teintes proposées à partir de la référence, pas une mesure colorimétrique exhaustive.

Trois études complémentaires :
1. Portrait : plans de décor, portrait, avant-plan ; caméra oscillante douce, réglage manuel au curseur ou à la souris. Équivalent tactile/clavier via le curseur.
2. Dossier : rotation de surface en perspective, tranche et ombre, cycle alterné de sept secondes.
3. Lettrage : passage lumineux de six secondes sans clignotement ni son.

La parallaxe et la perspective CSS ont été retenues plutôt qu'un modèle WebGL (modélisation et rig non disponibles) ou une vidéo (réglages et pause plus difficiles à adapter à chaque élément). Hypothèse : ces trois études suffisent pour choisir une intensité de relief et une direction de palette ; cela reste à éprouver avec l'utilisateur.

## Provenance et limite de qualité

`assets/images/animation/eva-reference.webp` est un recadrage 246 × 482 de `Gemini_Generated_Image.jpeg` fourni par l'utilisateur. Aucun suréchantillonnage, aucun modèle 3D, aucune génération de poses ou de visage. Le recadrage contient une partie du décor d'origine : ce n'est pas un personnage détouré ou articulé. La provenance exacte et les droits de production de la planche ne sont pas vérifiés ; pas d'inférence de permission générale de réutilisation.

Largeur maximale du portrait : 246 CSS px. Il n'offre donc pas une densité native 2× à cette largeur. La limite est explicitement annoncée sur la page : ce n'est pas un gain de qualité ni un master haute définition. Les lettrages et objets CSS sont indépendants du raster. Pour la suite : créer des calques et poses originaux haute définition après validation du style, sans réinterpréter les logos.

## Commandes et précautions

Arrêt au chargement ; lecture/pause ; intensité ; zéro désactive les effets ; mode immobile ; curseur manuel de point de vue ; arrêt de la boucle lorsque l'onglet est masqué ; préférence système `prefers-reduced-motion` prioritaire et réévaluée à chaud. Aucun stockage, collecte, compte, son ou service externe. Pas de geste tactile obligatoire. Les trois études restent visibles sans JavaScript.

## Contrôles exécutés

- `outils/test-atelier-animations.cjs` avec Puppeteer/Chromium : 240 configurations, 320/390/768/1280 px × 75/85/100/115/130 % × six présentations × deux contrastes, densité 2. Pas de débordement horizontal global détecté. Ce test ne mesure pas toutes les boîtes de texte ni toutes les occlusions.
- Commandes lecture/pause, changement effectif de matrice de transformation du dossier pendant lecture, mode immobile et préférence système : réussis. Lien Personnalisation depuis une fiche imbriquée : bonne URL.
- Capture grand écran relue ; taille des petits libellés bornée à 12 px minimum dans le CSS. Pas de mesure de compréhension, d'essai sur téléphone réel, de lecteur d'écran, de performance GPU ou d'audit complet de contraste.
- Vérification statique, intégration, publication locale et poids des pages : réussis après ajout de la page au sitemap et au périmètre de publication. Inventaire courant : 101 HTML dans le dépôt, 100 pages publiques ; audits historiques inchangés.

## Suite / décision attendue

Faire juger les trois études par l'utilisateur, notamment le relief, le rose et le rythme. Ne pas assimiler une approbation du mouvement des plans à celle d'un personnage qui parlerait ou marcherait. Faire ensuite un essai de poses/calques haute définition si cette direction est retenue. Prochaine revue avant extension à d'autres pages. Aucun statut de conformité RGAA/WCAG revendiqué.
