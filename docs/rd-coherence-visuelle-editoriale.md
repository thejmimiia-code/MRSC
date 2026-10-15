# R&D — cohérence visuelle et éditoriale du site M.R.S.C

**État initial au 12 octobre 2026 — revue de structure et harmonisation intégrées ; barre de parcours resserrée ; matrice automatisée Chromium headless passée.** Ce document fixe des règles de cohérence pour l’accueil, les pages d’information, l’apprentissage, l’IA & société, le simulateur et les fiches autonomes. Les pages et le catalogue passent les contrôles statiques et quatre surfaces représentatives ne présentent pas de violation axe dans les états testés ; aucune validation visuelle humaine, avec lecteur d’écran ou par les membres de l’association n’est revendiquée.

**Mise à jour du 13 octobre 2026 :** la barre secondaire persistante décrite dans la revue initiale est remplacée par une seule bascule native « Parcours » dans le bandeau commun ; les quatre commandes sont dans un panneau fermé par défaut. Les analyses Chromium/axe précédentes portaient sur l’ancienne présentation et ne valident pas le nouveau panneau. Sa revue visuelle, au clavier et avec technologies d’assistance reste à faire.

**Mise à jour du 13 octobre 2026 — accueil et ÉVA :** l’introduction a été reformulée avec des mots plus directs et une section présente les travaux de recherche sur ÉVA comme en cours. Le texte reçu dans le document Drive « Pour l’accueil du site du M.R.S.C » a servi de proposition éditoriale, pas de preuve technique ; les capacités, essais et résultats ne sont pas affirmés sans documentation. La rubrique devra être enrichie lorsque des éléments techniques validés pourront être publiés.

**Mise à jour du 14 octobre 2026 — présentation de l’association :** à la demande de l’utilisateur, la section d’accueil « Nos expériences ont quelque chose à apporter » et trois repères de réflexion ont été intégrés à `index.html`. La formulation de mission paraphrase les articles 2 et 3 des statuts locaux ; l’article 11.8 demande notamment une synthèse accessible en mots courants, et l’article 11.9 énumère les phases de travail participatif. Le lien vers le PDF des statuts est conservé. Cette rédaction reste une présentation du site fondée sur le document officiel, pas une déclaration d’une décision collective nouvelle ; aucune relecture humaine indépendante n’est revendiquée.

**Mise à jour du 13 octobre 2026 — cohérence des statuts :** la page d’apprentissage distingue désormais les 70 entrées (26 fiches du corpus initial et 44 prototypes explicitement à relire) et précise que la relecture indépendante de toutes les fiches initiales n’est pas garantie. Une absence de badge « prototype » ne doit jamais être interprétée comme une validation. Les copies PDF locales sont distinguées des liens vers une source externe ; l’adresse `github.io` est décrite comme l’adresse GitHub Pages actuellement configurée, en attendant le domaine personnalisé demandé.

## 1. Intention et identité à faire apparaître

Le site doit être d’abord reconnaissable comme celui du **Mouvement Représentatif de la Société Civile**, association loi 1901, et non comme une juxtaposition d’outils. Le fil de lecture retenu pour l’accueil est :

> Le M.R.S.C. propose des fiches, un dossier sur l’IA et un simulateur pour mieux comprendre des sujets de société. Le site explique aussi comment poser une question ou proposer une idée, et présente séparément la recherche sur ÉVA en distinguant les objectifs des résultats documentés.

La formulation de la mission est une synthèse des statuts disponibles dans le dépôt. Le texte statutaire reste la référence pour l’objet, les valeurs, le fonctionnement et l’adhésion.

Le site associe plusieurs portes d’entrée, sans imposer de parcours :

1. **Apprendre et transmettre** — fiches autonomes, exemples du quotidien, sources, repères indicatifs ; corpus à compléter et non certifiant.
2. **S’informer et débattre** — dossier IA & société, questions, sources et limites explicites.
3. **Examiner des hypothèses** — simulateur de politiques publiques, présenté comme un modèle exploratoire, jamais comme une prédiction certaine ou un verdict.
4. **Prendre part et partager** — documents, contact, contributions volontaires et partage des ressources.

Le site ne doit pas annoncer de fonction d’ÉVA comme disponible sans description et preuve validées. Les objectifs de recherche, les essais réalisés, les résultats et les fonctions réellement disponibles doivent être présentés séparément. Ne pas laisser entendre non plus qu’une formation certifiante, une permanence ou un compte existent si rien ne le confirme.

## 2. Statut des contenus et des affirmations

Pour éviter de confondre parole officielle, analyse et outil :

| Type de contenu | Présentation à conserver |
| --- | --- |
| Statuts, bulletins et documents adoptés | Distinguer le document officiel de son mode d’accès. Si un PDF est conservé dans `assets/documents/`, l’indiquer comme copie locale ; réserver « Source externe » aux liens vers un hébergeur externe. Ne pas reformuler une règle d’adhésion au-delà du texte disponible. |
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

L’accueil commence par une phrase simple sur ce que le visiteur peut trouver et faire : lire des fiches, s’informer sur l’IA, essayer le simulateur, poser une question ou proposer une idée. La mission de l’association est résumée avec des mots courants et reliée aux statuts officiels. Une section distincte présente la recherche en cours sur ÉVA : elle sépare les objectifs des essais, des résultats et des fonctions disponibles. Les documents, les sources, la participation et le contact restent accessibles depuis la page.

La page distingue :

- les textes statutaires ;
- les dossiers de réflexion, dont le dossier IA, qui peuvent ouvrir un débat sans être décrits comme des positions votées ;
- les outils et leurs limites ;
- les possibilités de contact et de partage.

Le partage s’effectue à la demande par le menu natif de l’appareil, la copie locale de l’adresse ou un courriel. Les métadonnées Open Graph de l’accueil fournissent un titre, un résumé et le logo pour l’aperçu du lien, sans pixel de suivi. Le site ne met pas en avant de compte social non confirmé et n’impose aucune plateforme. Aucune adresse de réseau social ne doit être ajoutée sans URL officielle validée par l’association.

## 5. Supervision de l’ensemble du site

| Surface | Vérification de cohérence à appliquer | État de cette itération |
| --- | --- | --- |
| Accueil | Phrases courtes et concrètes ; liens directs vers les ressources ; distinction entre documents officiels, réflexions, outils et recherche ÉVA ; objectifs séparés des essais et résultats | Présentation de l’association fondée sur les statuts, lien PDF conservé et trois repères pour poursuivre la réflexion ajoutés ; texte d’introduction simplifié et section ÉVA maintenue avec son statut en cours et ses limites ; relecture humaine indépendante encore utile |
| Navigation, panneau Parcours et réglages | Même bleu nuit, contour, rayon et focus visible ; une bascule visible « Parcours » regroupe les quatre commandes dans un panneau fermé par défaut. Menu, Réduire/Agrandir, Parcours et Affichage partagent une barre d’outils centrée, une hauteur minimale de 44 px et les mêmes états actifs/hover | Barre commune réharmonisée sans retirer de commande ni de libellé ; liens de rubrique restent dans le menu séparé quand la navigation se replie. Les actions du panneau Parcours gardent 38 px au pointeur fin et au moins 44 px sur tactile. La matrice headless antérieure ne valide pas la nouvelle présentation ; revue visuelle, clavier et lecteur d’écran encore requis |
| Apprendre | Recherche, filtres, cartes, étiquettes et liens de fiche ; source visible mais facultative ; repères non stigmatisants ; bien distinguer le corpus initial des prototypes | 72 entrées : 26 fiches du corpus initial et 46 prototypes explicitement à relire ; la relecture indépendante de toutes les fiches initiales n’est pas garantie. 33 fiches de développement réparties en quatre lots ouvrent des points d’entrée en français, langues, géographie, histoire, mathématiques, sciences, numérique, informatique, arts et recherche ; un prototype de démarches (`civ-trouver-service-public`) et un prototype informatique (`info-table-requete-web`) ouvrent les sujets des services publics et des tables/requêtes ; l’économie/consommation reste partielle ; objectif éditorial de 1 000 présenté comme cible, non comme offre actuelle ; couverture partielle |
| Fiches autonomes | Explication complète sur la page ; horizon séparé de la difficulté ; statut éditorial, analogie et sa limite, aide/correction, sources facultatives et retour vers le site | 72 pages générées, dont quarante-six prototypes à relire ; contenu autoportant ; relecture spécialisée et essais apprenants en attente ; commandes et métadonnées statiquement contrôlées |
| IA & société | Hero, cartes d’usages, risques et opportunités, alertes, sources, exercices et prise de contact | Palette commune maintenue ; statut des pistes et sources documenté |
| Simulateur intégré | Actions vers l’outil, données, provenance, avertissements et limites ; distinguer explicitement la copie embarquée de la version hébergée | Le résumé « plus de 100 » reste exact pour le moteur vérifié ; la page indique que la copie embarquée peut différer et affiche sa révision/date ; application Vercel amont et comportement HTTP non contrôlés par cette revue |
| Simulateur autonome | Retour permanent, commandes, réglages, tableaux défilants, focus et états système | Générateur et patch local harmonisés ; page synchronisée ; les sept vues dynamiques et 36 régions d’audit ont été testées à 320 px sous Chromium headless avec zéro violation axe ; revue visuelle humaine et lecteur d’écran encore requis |
| Documents et liens utiles | Cartes et sources faciles à distinguer ; indiquer si le PDF est une copie locale ou si le lien mène vers une source externe | Composants communs maintenus ; statuts et bulletins marqués comme copies locales dans le registre ; parution au Journal officiel maintenue comme source externe ; sources publiques, institutionnelles, éducatives et associatives distinguées avec registre daté des portées et droits de réutilisation dans `docs/apprentissage/sources-utilite-publique.md` |
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

La passe automatisée Chromium headless a couvert 29 vues responsives (accueil, transparence, fiche et simulateur) aux largeurs 320, 375, 768, 1024 et 1440 px avec des variantes tactiles et paysage court ; aucune largeur de page excédentaire ni violation axe n’a été signalée sur les quatre pages représentatives. La navigation réelle, le focus visible, `sessionStorage` bloqué et les sept vues du simulateur ont aussi été exercés. Cette mesure automatique ne valide pas la hiérarchie visuelle humaine, la perception des espacements ou la compréhensibilité des libellés. Une revue visuelle et un essai avec lecteur d’écran restent nécessaires, ainsi que des essais de zoom 200–400 % et une passe Firefox/Safari/WebKit. Contrôler particulièrement l’accueil, le catalogue, une fiche, le dossier IA, le simulateur autonome, le tableau de transparence et la page 404.

Le CSS commun a fait l’objet d’une reconstruction après la perte d’une ancienne version de travail. La version actuelle est contrôlée techniquement mais ne peut pas être déclarée visuellement identique à toutes les personnalisations antérieures. Comparer les rendus avec l’identité de production et recueillir des retours de membres et de personnes apprenantes avant d’affirmer que la direction visuelle est définitive.

## 8. Sources internes et prochaines étapes

- Statuts de l’association : page `documents.html` et PDF officiel relié depuis l’accueil.
- Méthode et registre des contenus : `transparence.html`.
- Règles d’apprentissage : `docs/rd-parcours-apprentissage.md`.
- Adaptation et essais d’accessibilité : `docs/rd-affichage-adaptatif.md`.
- Suivi de la vie privée : `docs/rd-confidentialite-rgpd.md`.
- Recherche en cours sur la direction artistique, le rendu visuel et le mouvement web : [`docs/rd/visuel-motion.md`](rd/visuel-motion.md). Elle complète le système visuel décrit ici ; les pistes ne sont pas encore sélectionnées ni intégrées.

Étapes suivantes : faire valider la formulation de la mission et des modalités d’adhésion par les responsables ; recueillir les URL de comptes sociaux que l’association souhaite réellement rendre publics, s’il y en a ; mener les essais visuels et accessibilité multi-navigateurs ; puis corriger l’ensemble des pages à partir des captures et des retours, sans confondre validation automatisée et validation de design.

## 9. Protocole éditorial permanent

Les échanges de rédaction ont établi une ligne durable : partir des expériences et de ce que les ressources apportent, mettre les savoirs en commun et expliquer les propositions en mots courants. Cette ligne est formalisée dans [`docs/protocole-editorial.md`](protocole-editorial.md), avec un [`gabarit réutilisable`](gabarits/contenu-editorial.md), une méthode de recherche et de vérification, l’affichage traçable des sources, des activités ludiques facultatives et une liste de contrôle adaptée aux types de page. `AGENTS.md` et le README renvoient à cette référence ; `outils/test_protocole_editorial.py` en contrôle les fichiers, rubriques et raccords documentaires.

Le protocole décrit une méthode commune, pas une mise en page unique imposée à chaque page. Il ne certifie pas les affirmations et ne transforme pas les pages existantes en contenus relus. L’harmonisation intégrale reste progressive : traiter les surfaces et lots du tableau ci-dessus, signaler les sources/relectures manquantes et ne modifier un statut qu’avec une preuve correspondante.
