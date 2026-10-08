# R&D — affichage adaptatif du site M.R.S.C et du simulateur

**État :** adaptations intégrées le 7 octobre 2026 ; `outils/verifier-site-statique.py` vérifie les pages, liens, ancres, repères essentiels et JavaScript, et `outils/verifier-integration.py` ajoute les contrôles du simulateur. Les essais visuels nécessitant un navigateur, un lecteur d’écran ou des personnes utilisatrices restent à effectuer. Il ne constitue pas une déclaration de conformité WCAG.

## 1. Objectif et principes

Conserver les mêmes contenus et fonctions, sans détecter la marque ou le modèle du terminal : les mises en page réagissent à l’espace réellement disponible, à l’orientation et au type de pointeur. L’utilisateur garde le contrôle du zoom natif du navigateur. Les préférences de contraste, d’espacement et de mouvement sont prises en compte lorsqu’elles sont disponibles.

L’adaptation couvre les pages publiques (dont l’accueil, le catalogue et les fiches « Apprendre », « IA & société », la notice vie privée, la présentation du simulateur et la page 404), la version autonome publiée dans `simulateur/`, et l’aperçu intégré dans une iframe. Le moteur amont n’est pas modifié : les compléments du simulateur restent dans `outils/construire-simulateur.py`.

## 2. Références de recherche et conséquences pratiques

- **Reflow — WCAG 2.2, critère 1.4.10 (AA)** : pour un contenu de lecture verticale, viser une largeur de **320 pixels CSS** sans perte de contenu/fonction ni défilement horizontal général. Les tableaux de données et cartes qui ont réellement besoin de deux dimensions peuvent garder un défilement **local**, au lieu de rendre toute la page bidimensionnelle. [W3C — Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)
- **Redimensionnement — WCAG 2.2, 1.4.4 (AA)** : le texte doit pouvoir atteindre **200 %** sans perte de contenu ou de fonction. Le site ne bloque pas le zoom natif ; son réglage maison est un complément, pas un substitut. [W3C — Resize Text](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html)
- **Espacement — WCAG 2.2, 1.4.12 (AA)** : aucune perte si l’utilisateur impose au minimum un interligne de 1,5×, un espacement après paragraphe de 2×, un interlettrage de 0,12× et un espacement des mots de 0,16×. Le critère exige que les surcharges utilisateur ne cassent pas l’interface ; il n’oblige pas à fournir un bouton maison. Le mode « Espacement du texte » apporte ici une option simple. [W3C — Text Spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html)
- **Zones d’interaction — WCAG 2.2, 2.5.8 (AA)** : cible minimale de 24 × 24 pixels CSS sous réserve des exceptions du critère ; 44 × 44 correspond à la cible renforcée du critère 2.5.5 (AAA). Pour le confort tactile, les réglages d’affichage et les principaux boutons du simulateur visent 44 pixels de hauteur. [W3C — WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- **Préférences du système** : les médias CSS `prefers-contrast`, `forced-colors`, `prefers-reduced-motion` et `prefers-reduced-transparency` permettent de suivre les options d’accessibilité de la plateforme plutôt que de leur imposer une palette ou des effets. Les requêtes `orientation` et `any-pointer: coarse` décrivent le contexte d’affichage et d’entrée, pas un modèle d’appareil. [MDN — `@media`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media), [prefers-contrast](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-contrast), [forced-colors](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/forced-colors), [prefers-reduced-motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion), [prefers-reduced-transparency](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-transparency).
- **Lisibilité cognitive et apprentissages** : le document W3C COGA complète les critères WCAG par des recommandations d’usage et recommande d’inclure les personnes concernées dans la recherche et les tests. C’est une note d’orientation, pas un critère de conformité. [W3C — Making Content Usable for People with Cognitive and Learning Disabilities](https://www.w3.org/TR/coga-usable/)

## 3. Audit du dépôt avant cette itération

### Site commun

- `assets/css/site.css` comportait déjà des mises en page fluides, plusieurs bascules de colonnes, une navigation repliée et un respect de `prefers-reduced-motion`.
- Un réglage de texte binaire A+/A− était présent. Il ne permettait pas de réduire/augmenter par étapes, et aucun contrôle simple ne proposait contraste ou espacement renforcés.
- Le registre de transparence utilise un tableau large. Il se trouve dans une zone locale défilante, nommée et focusable au clavier ; une consigne visuelle manquait.
- Les en-têtes restent collants sur les pages publiques ; sur un écran court en paysage, ils peuvent prendre une part importante de la hauteur disponible.

### Simulateur

- L’interface autonome contenait un breakpoint principal à 640 px, mais des colonnes `minmax(300px, …)` et `minmax(330px, …)` continuaient à imposer une largeur supérieure à celle d’un viewport de 320 pixels CSS (notamment après zoom). La vue compacte des leviers héritait de la même contrainte.
- Les tableaux de résultats et la matrice ont besoin d’une présentation bidimensionnelle. Leur défilement était local, mais les zones n’étaient pas accessibles au clavier et ne donnaient pas d’instruction visible.
- Plusieurs libellés et aides sont volontairement denses ; les tailles de texte et d’espacement n’étaient pas modulables depuis l’interface.

## 4. Changements intégrés

### Site M.R.S.C

- Le bouton unique est remplacé par un panneau natif `<details>` « Affichage », présent dans la navigation commune, y compris sur la page 404.
- Taille du texte en trois paliers (100 %, 125 %, 150 %), avec commandes séparées A−/A+, désactivation aux limites, annonce du niveau et mémorisation locale. L’ancien choix A+/A− est migré au premier chargement. Le zoom du navigateur reste indépendant.
- « Contraste renforcé » et « Espacement du texte » sont activables et mémorisés sur l’appareil. Les contrôles ont des noms accessibles et des états `aria-pressed` ; le panneau se ferme au clic extérieur et à Échap.
- Le contraste renforcé suit aussi `prefers-contrast: more`. `forced-colors: active` laisse la palette système dominer et remplace les ombres dépendant du contraste par des bordures visibles.
- La vérification initiale de la palette a repéré le vert de marque `#76b544` utilisé comme petit texte sur fond clair (environ 2,48:1 sur blanc). Le jeton est assombri en `#456d29` : environ 6,05:1 sur blanc et 5,3:1 sur le bleu pâle du hero. Ce calcul sur les jetons ne remplace pas un audit complet de chaque état et composant.
- Les réglages de plateforme pour mouvement réduit et transparence réduite sont suivis. Une règle paysage/hauteur courte libère de l’espace vertical. Les principaux contrôles gardent une cible de 44 px pour les pointeurs tactiles.
- Le tableau de transparence conserve son défilement local et reçoit une instruction visuelle.
- Une barre de parcours propose « Précédent », « Suivant », « Accueil » et « Dernière vue » sur les pages du site. Elle rejoue les liens internes de l’onglet ; sur les pages du site, son décalage sticky suit la hauteur réelle de l’en-tête lors d’un redimensionnement, y compris quand les réglages d’affichage font évoluer cette hauteur. Son emplacement, son ordre clavier, ses libellés et son repli vers la navigation native si `sessionStorage` est bloqué restent à tester avec zoom, clavier et lecteur d’écran. La portée des données est documentée dans `docs/rd-confidentialite-rgpd.md`.

### Simulateur

- `outils/construire-simulateur.py` ajoute, sans toucher à `simulateur/interface.py`, les réglages A−/A+, contraste et interligne ainsi que les commandes de navigation du parcours à côté du retour permanent au site.
- Les trois réglages partagent les préférences locales du site lorsque l’iframe est de même origine ; l’événement de stockage synchronise alors les deux documents. Si le simulateur distant est servi depuis une autre origine, l’isolation du navigateur empêche ce partage.
- Sous 640 px, les grilles des domaines, des leviers (y compris la vue compacte) et de la console passent en colonne unique. Les libellés sont autorisés à revenir à la ligne ; les rangées de chiffres se replient. Les contrôles tactile/curseurs gagnent de la hauteur. Les textes secondaires de l’interface sont plafonnés à un minimum de 0,75 rem (12 px à la base), puis suivent les paliers A−/A+.
- Les tableaux intrinsèquement larges restent défilables dans leurs propres cadres, portent un nom de région, sont focusables au clavier et sont précédés d’une consigne. Les infobulles sont bornées à la largeur de l’écran.
- Le générateur applique aussi les adaptations mouvement réduit, contraste renforcé, couleurs forcées et transparence réduite. La barre de retour reste collante, y compris en paysage.

Les préférences manuelles sont enregistrées localement sous `mrsc-texte-niveau`, `mrsc-contraste-renforce` et `mrsc-espacement-renforce`. Aucune n’est envoyée au serveur. Si le stockage local est bloqué, elles restent actives pendant la visite. L’interface reste utilisable avec le zoom du navigateur sans dépendre de ces contrôles.

## 5. Matrice d’essais à effectuer dans un navigateur réel

Les contrôles statiques ne remplacent pas le rendu. Pour chaque page publique, puis pour `simulateur/index.html` et `simulateur.html`, vérifier les cas suivants dans au moins Chromium, Firefox et Safari/WebKit lorsque disponibles :

| Situation | Vérification attendue |
| --- | --- |
| Largeurs CSS 320, 360, 390, 430, 768, 920, 1024, 1260, 1440 et 1920 px | Pas de débordement horizontal global ; ordre de lecture conservé ; navigation et réglages utilisables. |
| 1280 px à 400 % de zoom (viewport ramené à environ 320 px CSS), et texte à 200 % | Pas de contenu ni de commande masqués ; les cartes se replient ; seul un tableau/cadre bidimensionnel défile horizontalement. |
| Portrait et paysage, dont 667 × 375 et écran court en paysage | En-tête, barre de parcours et barre du simulateur ne masquent pas le contenu ; focus et commandes restent visibles. |
| Espacements WCAG 1.4.12, appliqués par une feuille de style ou un outil de test | Titres, cartes, formulaires, aides et commandes s’agrandissent sans chevauchement ni troncature. |
| Contraste renforcé manuel, `prefers-contrast: more` et Windows High Contrast/`forced-colors` | Liens, bordures, valeurs et focus restent visibles ; ne pas s’appuyer uniquement sur une couleur. |
| `prefers-reduced-motion`, transparence réduite | Pas de défilement animé/transitions persistantes ; l’information ne dépend pas d’un mouvement ou d’un flou. |
| Souris, clavier seul, tactile/pointeur grossier | Parcours Tab/Échap, focus non masqué, panneau de réglages opérable et cibles de taille confortable. |
| Zoom par étapes puis retour A− ; `localStorage` et `sessionStorage` autorisés puis bloqués | Le niveau annoncé correspond au rendu ; le parcours s’enregistre quand `sessionStorage` est disponible ; s’il est bloqué, la navigation native reste utilisable et aucune donnée saisie n’est perdue. |
| Lecteur d’écran et navigation des tableaux | Noms de toutes les commandes précédent/suivant/accueil/dernière vue et des régions annoncés ; les deux tableaux du simulateur restent atteignables au clavier. |

**Limite de validation de cette session :** aucun navigateur graphique ni moteur WebDriver n’est installé dans l’environnement de travail. Les dimensions, les reflows et les médias système ne peuvent donc pas être confirmés visuellement ici. La suite automatisée vérifie la présence des règles, contrôles et régions ; les essais ci-dessus et une revue avec des personnes utilisatrices restent nécessaires avant d’affirmer la conformité.

## 6. Choix restant à évaluer

- Le site conserve son identité claire et le simulateur son interface sombre. Un basculement automatique clair/sombre complet (`prefers-color-scheme`) n’est pas introduit dans cette itération : les deux surfaces utilisent encore plusieurs couleurs de composants spécifiques ; l’appliquer sans inventaire/rendu complet risquerait d’afficher du texte peu contrasté. À réévaluer avec une palette à jetons et des captures multi-navigateurs.
- `prefers-reduced-data` n’a pas de règle dédiée : pas de vidéo ou d’animation lourde à désactiver dans les nouvelles adaptations, et la carte de localisation est déjà chargée paresseusement. Réévaluer si des médias plus lourds sont ajoutés.
- La version distante du simulateur peut échapper aux réglages ajoutés au générateur tant que son origine ou son dépôt ne sont pas contrôlés par M.R.S.C.
- Prévoir ensuite une passe de tests manuels et utilisateurs : petits écrans, basse vision, difficulté de lecture, handicap moteur, retours sur l’utilité des réglages et possibilité de découvrir le panneau.
