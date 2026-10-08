# R&D — cohérence visuelle et éditoriale du site M.R.S.C

**État au 8 octobre 2026 — revue de structure et harmonisation intégrées ; contrôle visuel en navigateur réel encore nécessaire.** Ce document fixe des règles de cohérence pour l’accueil, les pages d’information, l’apprentissage, l’IA & société, le simulateur et les fiches autonomes. Les pages et le catalogue passent les contrôles statiques ; aucune validation visuelle en navigateur réel ni validation par les membres de l’association n’est revendiquée.

## 1. Intention et identité à faire apparaître

Le site doit être d’abord reconnaissable comme celui du **Mouvement Représentatif de la Société Civile**, association loi 1901, et non comme une juxtaposition d’outils. Le fil de lecture retenu pour l’accueil est :

> Faire société à partir des expériences, des compétences et des savoir-faire de chacune et chacun ; créer du lien, rendre les ressources compréhensibles, ouvrir des espaces d’information et de participation.

La formulation de la mission est une synthèse des statuts disponibles dans le dépôt. Le texte statutaire reste la référence pour l’objet, les valeurs, le fonctionnement et l’adhésion.

Le site associe plusieurs portes d’entrée, sans imposer de parcours :

1. **Apprendre et transmettre** — fiches autonomes, exemples du quotidien, sources, repères indicatifs ; corpus à compléter et non certifiant.
2. **S’informer et débattre** — dossier IA & société, questions, sources et limites explicites.
3. **Examiner des hypothèses** — simulateur de politiques publiques, présenté comme un modèle exploratoire, jamais comme une prédiction certaine ou un verdict.
4. **Prendre part et partager** — documents, contact, contributions volontaires et partage des ressources.

Le site ne doit pas laisser entendre qu’une formation certifiante, une permanence, un compte ou une fonction d’EVA sont disponibles lorsqu’aucune description validée ne l’établit.

## 2. Statut des contenus et des affirmations

Pour éviter de confondre parole officielle, analyse et outil :

| Type de contenu | Présentation à conserver |
| --- | --- |
| Statuts, bulletins et documents adoptés | Les qualifier de documents officiels et relier au fichier source. Ne pas reformuler une règle d’adhésion au-delà du texte disponible. |
| Dossier de réflexion, questions et pistes éditoriales | Les sourcer et préciser lorsqu’elles n’ont pas été adoptées par l’association comme position officielle. |
| Fiches d’apprentissage | Expliquer simplement, partir d’une situation concrète, signaler limites et sources ; ne pas faire passer le corpus pour un programme complet, une formation certifiante ou un diagnostic de niveau. |
| Simulateur et résultats calculés | Indiquer hypothèses, provenance, date et limites ; un résultat dépend du modèle et ne constitue ni une prévision ni une décision politique. |
| Information externe | Nommer l’éditeur, la date quand elle est connue et le lien ; distinguer donnée, interprétation, exemple et opinion. |

Aucune phrase attribuée à l’association ne doit être présentée comme une décision collective sans document ou validation qui l’atteste. Les contributions par courriel sont des propositions ou questions jusqu’à leur examen ; elles ne deviennent pas automatiquement des positions du M.R.S.C.

## 3. Système visuel commun

### Repères de marque

Le logo local et les couleurs du site donnent les repères principaux :

- bleu nuit `#1d3268` pour l’identité, la navigation et les textes de titre ;
- bleu `#2958a2` pour les actions primaires, liens et états actifs ;
- vert assombri `#456d29` pour les repères de progrès et d’action ;
- or `#e7a126` pour l’accent et les focus sur surfaces sombres ;
- rouge `#e55058` réservé à l’alerte ou à un contraste sémantique ;
- fonds blancs et gris très clairs pour les pages, cartes et zones de lecture.

Les teintes pâles peuvent servir de fond, pas de petit texte sur blanc. Le vert de marque pour le texte atteint environ 6,05:1 sur blanc. Une couleur ne doit jamais être le seul moyen de transmettre un état.

### Boutons et commandes

Les appels à l’action utilisent les mêmes repères géométriques et typographiques, définis par `--button-radius` et `--button-height` dans `assets/css/site.css` :

- **principal** — fond bleu M.R.S.C, texte blanc, hauteur confortable, angle carré adouci ; action principale de la page ;
- **secondaire** — surface claire, texte bleu nuit, contour discret ; lien ou action complémentaire ;
- **navigation et réglages** — commandes compactes mais de même famille visuelle, avec états hover, focus, désactivé et couleurs forcées ;
- **simulateur autonome** — conserve le contraste nécessaire à son interface sombre, tout en reprenant les accents bleu, vert et or M.R.S.C. Les boutons de retour, de parcours et d’affichage n’utilisent plus un jeu de couleurs étranger au site.

Une vraie commande HTML `<button>` reçoit les mêmes règles de police, curseur, rayon, état de focus et taille tactile qu’un lien portant la classe `.button`. Ne pas créer de faux boutons en lien bleu souligné ni ajouter de nouvelles pilules décoratives pour une action principale.

### Cartes, rythme et responsive

- Les cartes ont une bordure fine, un rayon cohérent, un fond clair et une ombre discrète ; l’accent coloré sert à identifier la rubrique, pas à décorer chaque bloc différemment.
- Les pages utilisent une hiérarchie commune : bandeau ou hero, contenu centré, titres bleu nuit, texte lisible, sections espacées, sources et contact accessibles en fin de page.
- Les fiches donnent priorité à la lecture, aux exemples et aux sources ; les filtres et commandes ne doivent pas ressembler à des contrôles du simulateur.
- Les points de rupture se basent sur la largeur disponible, avec une colonne sur petit écran, un retour à la ligne pour les libellés longs et aucun zoom désactivé.
- Les réglages d’affichage, le mouvement réduit, le contraste renforcé, les couleurs forcées et les zones de focus sont pris en compte par les styles communs.

## 4. Accueil : nouvel ordre de lecture

L’accueil commence par la mission de l’association et la valeur des expériences personnelles. Il donne ensuite quatre portes d’entrée : apprentissages autonomes, IA & société, simulateur, informations et documents. La participation, la prise de parole, le partage et la traçabilité sont présentés avant le pied de page.

La page distingue :

- les textes statutaires ;
- les dossiers de réflexion, dont le dossier IA, qui peuvent ouvrir un débat sans être décrits comme des positions votées ;
- les outils et leurs limites ;
- les possibilités de contact et de partage.

Le partage s’effectue à la demande par le menu natif de l’appareil, la copie locale de l’adresse ou un courriel. Les métadonnées Open Graph de l’accueil fournissent un titre, un résumé et le logo pour l’aperçu du lien, sans pixel de suivi. Le site ne met pas en avant de compte social non confirmé et n’impose aucune plateforme. Aucune adresse de réseau social ne doit être ajoutée sans URL officielle validée par l’association.

## 5. Supervision de l’ensemble du site

| Surface | Vérification de cohérence à appliquer | État de cette itération |
| --- | --- | --- |
| Accueil | Mission avant les produits ; parcours variés ; liens vers apprendre, IA, simulateur, documents, sources, contact et partage ; distinction officiel/réflexion/modèle | Réorganisé ; partage natif avec repli courriel/copie ; mention sociale non souhaitée supprimée |
| Navigation, barre de parcours et réglages | Même bleu nuit, bleu, contours, rayon, taille minimale, focus visible et états désactivés | Boutons de parcours rapprochés du style d’action M.R.S.C ; menus et contrôles harmonisés |
| Apprendre | Recherche, filtres, cartes, étiquettes et liens de fiche ; source visible mais facultative ; repères non stigmatisants | 35 entrées au catalogue : 26 fiches du corpus initial et 9 prototypes explicitement à relire ; nouvelle première série informatique, programmation, électricité, électronique et littératie des sources ; objectif éditorial de 1 000 présenté comme cible, non comme offre actuelle ; couverture partielle |
| Fiches autonomes | Explication complète sur la page ; horizon séparé de la difficulté ; statut éditorial, analogie et sa limite, aide/correction, sources facultatives et retour vers le site | 35 pages générées, dont neuf prototypes à relire ; contenu autoportant ; relecture spécialisée et essais apprenants en attente ; commandes et métadonnées statiquement contrôlées |
| IA & société | Hero, cartes d’usages, risques et opportunités, alertes, sources, exercices et prise de contact | Palette commune maintenue ; statut des pistes et sources documenté |
| Simulateur intégré | Actions vers l’outil, données, provenance, avertissements et limites | Contrôles vérifiés dans la page d’intégration ; essai visuel à poursuivre |
| Simulateur autonome | Retour permanent, commandes, réglages, tableaux défilants, focus et états système | Générateur harmonisé avec les accents M.R.S.C ; page synchronisée et vérifiée par `--verifier` ; aucun essai visuel dans un navigateur réel documenté |
| Documents et liens utiles | Cartes et sources faciles à distinguer ; ne pas surcharger en boutons | Composants communs maintenus ; sources publiques, institutionnelles, éducatives et associatives distinguées, avec registre daté des portées et droits de réutilisation dans `docs/apprentissage/sources-utilite-publique.md` |
| Localisation et contact | Carte chargée sur action ; coordonnées lisibles ; actions explicites | Boutons et encarts relus ; chargement de carte conservé sur action seulement |
| Transparence et confidentialité | Tableaux, aides de lecture, catégories, sources et limites ; lisibilité au zoom | Entrée obsolète supprimée du registre ; liens et contenus mis en cohérence |
| Page 404 | Identité commune, retour d’accueil, navigation et contact sans impasse | Modèle commun conservé |

## 6. Liens sociaux, partage et voix de l’association

Les réseaux sociaux sont des destinations éditoriales : un logo ou un nom de plateforme sans URL vérifiée n’est pas un lien utile et peut laisser croire à tort que le compte est officiel. Les ressources doivent pouvoir circuler sans imposer un réseau : partage du système d’exploitation, courriel ou copie de l’adresse publique.

La prise de parole publique doit s’appuyer sur des contenus identifiables : documents officiels, dossier de réflexion sourcé, fiche pédagogique ou résultat du simulateur clairement limité. Un formulaire de témoignage ou de contribution ne sera ajouté qu’après définition de son traitement de données, de ses destinataires et de sa durée de conservation.

## 7. Vérifications et limites

### Contrôles à automatiser

- pages publiques et fiches reliées à la feuille de style et à la navigation communes ;
- absence d’éléments de compte social non désirés ou non confirmés ;
- classes d’action reliées à des règles CSS, présence de focus et états accessibles ;
- liens locaux, ancres, balises essentielles, syntaxe JavaScript et sorties des générateurs ;
- présence des sources, limites et déclarations de statut éditorial dans les pages correspondantes.

### Revue humaine requise

Les validateurs statiques ne mesurent ni le rendu des boutons, ni les espacements, ni la hiérarchie visuelle réelle. Une passe de captures et de tests dans Chromium, Firefox et Safari/WebKit reste nécessaire aux largeurs 320, 375, 768, 1024, 1440 px, au zoom 200–400 %, au clavier et avec lecteur d’écran. Il faut contrôler particulièrement l’accueil, le catalogue, une fiche, le dossier IA, le simulateur autonome, le tableau de transparence et la page 404.

Le CSS commun a fait l’objet d’une reconstruction après la perte d’une ancienne version de travail. La version actuelle est contrôlée techniquement mais ne peut pas être déclarée visuellement identique à toutes les personnalisations antérieures. Comparer les rendus avec l’identité de production et recueillir des retours de membres et de personnes apprenantes avant d’affirmer que la direction visuelle est définitive.

## 8. Sources internes et prochaines étapes

- Statuts de l’association : page `documents.html` et PDF officiel relié depuis l’accueil.
- Méthode et registre des contenus : `transparence.html`.
- Règles d’apprentissage : `docs/rd-parcours-apprentissage.md`.
- Adaptation et essais d’accessibilité : `docs/rd-affichage-adaptatif.md`.
- Suivi de la vie privée : `docs/rd-confidentialite-rgpd.md`.

Étapes suivantes : faire valider la formulation de la mission et des modalités d’adhésion par les responsables ; recueillir les URL de comptes sociaux que l’association souhaite réellement rendre publics, s’il y en a ; mener les essais visuels et accessibilité multi-navigateurs ; puis corriger l’ensemble des pages à partir des captures et des retours, sans confondre validation automatisée et validation de design.
