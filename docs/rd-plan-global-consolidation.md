# R&D — plan global de consolidation, optimisation et maintenance du site M.R.S.C

**Revue initiale du dépôt local : 12 octobre 2026. Mise à jour de décision : 13 octobre 2026.** Ce document organise les pistes déjà présentes dans le dépôt et la demande d’allègement de la barre de parcours. C’est un plan de travail, pas une certification de qualité, d’accessibilité, de sécurité ni un audit de l’hébergement en production. Les choix de publication restent humains.

**Décision mise à jour le 13 octobre :** à la demande explicite du lecteur, les quatre commandes ne restent plus visibles pendant la lecture. Elles sont regroupées derrière une seule bascule native « Parcours » intégrée à la barre principale ; elles restent disponibles sur demande. Le simulateur autonome reçoit un contrôle équivalent dans sa barre de retour, tandis que l’iframe dans une page du site laisse la navigation au bandeau parent pour éviter un doublon. Cette décision remplace l’option initialement écartée ci-dessous ; la découvrabilité et le focus restent à tester avec des personnes.

## 1. Besoin, périmètre et décision de cette itération

**Signal reçu :** le site doit rester complet, stable et fonctionnel, mieux réunir ses améliorations et éviter les doublons ou versions obsolètes ; la barre « Précédent / Suivant / Accueil / Dernière vue » est jugée trop volumineuse et insuffisamment intégrée visuellement.

**Observation vérifiée dans le dépôt :** lors de la revue du 12 octobre, `assets/js/navigation-parcours.js` insérait une barre sticky permanente sur les pages du site et dans le simulateur autonome. Depuis la mise à jour du 13 octobre, le script place les mêmes quatre commandes dans un `<details>` « Parcours » fermé par défaut ; le simulateur généré a un habillage dédié, car il ne charge pas la feuille CSS commune.

**Hypothèse de la première passe (12 octobre) :** une barre secondaire alignée sur le contenu, compacte sur une seule ligne lorsque l’espace le permet et adaptée aux petits écrans, peut réduire l’emprise visuelle sans supprimer les quatre actions ni leurs noms accessibles.

**Décision initiale du 12 octobre, désormais supersédée :** appliquer un style plus discret sur le site et dans le simulateur : boutons visuellement à 38 px sur pointeur fin, cibles de 44 px sur tactile et mobile, symboles décoratifs masqués sur très petit écran pour garder les libellés visibles, compteur d’étape court et barre alignée au contenu. La mise à jour du 13 octobre conserve ces invariants dans un panneau fermé par défaut. Aucun stockage supplémentaire, requête réseau, dépendance ou fonction de suivi n’est ajouté. Aucun fichier « ancien » n’est supprimé sur la seule base de son âge ou de son nom.

## 2. Carte des sources de vérité et des sorties

L’inventaire ci-dessous provient des fichiers et des générateurs du dépôt. Il différencie une copie réellement redondante d’une sortie nécessaire à la publication.

| Surface | Source de vérité / sortie | Décision de consolidation |
| --- | --- | --- |
| Pages générales | 12 HTML à la racine (dont la 404), `assets/css/site.css`, `assets/js/site.js` et `assets/js/navigation-parcours.js` | Les styles et comportements communs restent centralisés. Les pages conservent un contenu lisible sans JavaScript. |
| Fiches d’apprentissage | `docs/apprentissage/catalogue.toml` et `referentiel.toml` → générateur `outils/construire-apprentissages.py` → `apprendre.html`, 70 fiches et données d’atlas | Les pages publiées sont des sorties, pas des versions concurrentes. Modifier les TOML puis régénérer et vérifier ; ne pas éditer les sorties à la main. |
| Les Mondes / Escales anglaises | Données et comportements locaux dans `assets/js/anglais-aventure-data.js`, `apprentissage-aventure-data.js`, `anglais-aventure.js` et `apprentissage.js` ; styles spécifiques dans `assets/css/anglais-aventure.css` | Le style de jeu reste séparé du style commun tant que la différence sert son interface ; vérifier les sources de génération avant toute édition des données produites. |
| Simulateur | Moteur embarqué, provenance et correctif ; `outils/construire-simulateur.py` → `simulateur/index.html` ; routes `api/` ; page d’intégration `simulateur.html` ; service distant Render distinct | La page statique générée, l’intégration, la copie locale et le service distant ont des rôles de publication/repli différents. Les supprimer ou les fusionner sans plan de disponibilité ferait perdre une voie de fonctionnement. Le service distant n’est pas couvert par l’audit local. |
| R&D, contrôles et publication | `AGENTS.md`, `docs/rd-innovation-continue.md`, portefeuille/journal, vérificateurs et workflows | Ces éléments décrivent la méthode, les contrôles et les décisions ; ils se complètent et ne remplacent pas une validation humaine. |

Le dépôt contient 12 pages HTML à la racine, 70 fiches autonomes et une page HTML générée du simulateur ; le vérificateur statique contrôle 83 pages. Il y a une feuille CSS commune et une feuille dédiée au jeu. Le dépôt n’expose pas de paquetage ou de bundler JavaScript à la racine : conserver le déploiement simple sans introduire une chaîne de build juste pour déplacer quelques règles.

## 3. Doublons, versions anciennes et éléments à préserver

### Ce qui est confirmé

- La recherche de noms de fichiers `old`, `backup`, `legacy`, `archive`, `copy`, `v1` ou `v2` n’a pas trouvé de copie de page ou de feuille de style explicitement archivée. Cette recherche par nom ne prouve pas qu’aucun code mort n’existe.
- Le CSS commun et le CSS du jeu ont des périmètres différents ; leur coexistence n’est pas un doublon à retirer.
- Les fiches HTML et les données d’atlas sont générées depuis le catalogue. Les supprimer ou les corriger directement casserait la synchronisation.
- La page du simulateur, son moteur, son correctif, l’API locale et le service Render correspondent à des étapes ou modes d’hébergement distincts, et non à des copies interchangeables.
- Les pages générales répètent une partie de la structure de navigation et de pied de page ; le générateur des fiches fournit déjà un point de centralisation pour celles-ci. Remplacer les pages statiques par un `fetch()` de fragments ferait dépendre la structure de JavaScript et dégraderait le repli sans script.
- La clé historique `mrsc-texte-agrandi` est encore lue pour la migration d’une préférence. La retirer sans période de migration et test de reprise effacerait un choix déjà conservé dans certains navigateurs.

### Ce qui n’est pas encore démontré

Aucun rapport de couverture CSS/JavaScript ou rendu navigateur n’établit ici qu’une règle est inutilisée, qu’un écran est visuellement conforme ou qu’un fichier public peut être retiré sans casser un lien externe. Ne pas nettoyer un bloc de cascade, une page ou une ancienne clé uniquement parce qu’il paraît ancien. Pour retirer un élément, exiger : propriétaire/source identifiés, références et liens examinés, alternative prête, sortie générée comparée, tests complets réussis et procédure de retour arrière.

## 4. Brainstorming — options examinées pour la barre

| Option | Valeur possible | Risque / coût | Décision |
| --- | --- | --- | --- |
| A. Réduire les boutons et l’espace du statut, puis aligner la barre au contenu | Moins de hauteur ; actions immédiatement visibles ; code réversible et sans dépendance | Les libellés longs ne tiennent pas sur tout écran étroit ; demander une revue clavier/tactile et lecteur d’écran | **Prototype choisi** : libellés visibles dans les deux formats, symboles décoratifs masqués à très petite largeur ; cibles tactiles de 44 px. |
| B. Replier les commandes dans un panneau `<details>` du bandeau principal | Libère la hauteur de lecture ; une seule bascule révèle ou replie les quatre actions au besoin | Ajoute une action et peut réduire leur découverte ; exige de tester focus, clavier, zoom et compréhension | **Adopté le 13 octobre à la demande du lecteur** : panneau fermé par défaut et commande visible « Parcours » ; garder les quatre actions, leurs noms et leur état. |
| C. Déplacer les quatre commandes directement dans la rangée des liens principaux | Une seule bande visuelle | Surcharge les liens de rubrique et confond la navigation du site avec l’historique de visite | Toujours écarté : seule la bascule Parcours rejoint le bandeau ; les quatre commandes s’ouvrent dans un panneau distinct. |
| D. Remplacer la barre par l’historique natif du navigateur | Moins de code et moins de stockage applicatif | Fait perdre « Accueil » et « Dernière vue », et ne répond pas au parcours personnalisé demandé par le site | Écarté tant que ces deux actions font partie de la fonction. |

## 5. Plan global par priorité

### P0 — préserver la fiabilité actuelle

1. Garder les générateurs comme sources de vérité ; vérifier chaque sortie après modification.
2. Conserver les contrôles statiques, de sécurité, d’intégration et de R&D dans la CI. La protection de branche GitHub doit toujours être configurée par un administrateur pour rendre la CI obligatoire.
3. Ne pas qualifier le site de « complet » au sens universel : préserver les statuts éditoriaux, lacunes, provenances et limites visibles.
4. Ne pas confondre l’audit du dépôt avec l’état du simulateur Render, de GitHub Pages, de Vercel ou des journaux des prestataires.

### P1 — interface, accessibilité et robustesse

1. Tester le panneau Parcours fermé/ouvert et le réglage Affichage sur l’accueil, une page d’information, une fiche et le simulateur : clavier seul, focus, Échap, clic extérieur, ouverture concurrente de Menu/Affichage, tailles de texte 50/75/100/125/150 %, zoom natif du navigateur, largeurs 320/375/768/1024/1440 px, paysage court, pointeur fin et tactile. Vérifier en particulier que la navigation de bureau passe en menu repliable à 125/150 % sans perte de libellés ni escalade en hauteur.
2. Rejouer Précédent/Suivant, retour à l’accueil, dernière vue, fragments d’ancre, retour du navigateur et session `sessionStorage` bloquée. Vérifier que les contrôles gardent un nom clair, que leur statut replié est annoncé et que le message de repli reste accessible dans le panneau.
3. Si un problème réel apparaît, privilégier une correction ciblée avec repli plutôt que l’ajout d’une couche de framework.
4. Maintenir un contrôle séparé du simulateur intégré et de sa version autonome ; les deux ne partagent pas toujours la même origine ni les mêmes styles.

### P2 — réduire les duplications sans perdre le rendu statique

1. Cartographier les fragments communs des pages générales et les points où ils divergent (liens actifs, chemins profonds, statut, navigation, pied de page).
2. Prototyper, hors production, un petit générateur statique de fragments si la maintenance des copies devient source d’erreurs. Il devra produire du HTML autonome avant publication, sans requête d’inclusion au runtime et sans nouvelle dépendance.
3. Comparer les HTML avant/après : titres, métadonnées, liens, ancres, attributs ARIA, versions sans JavaScript et publication. N’intégrer qu’après génération reproductible et contrôles qui couvrent toutes les pages.
4. Auditer la cascade CSS avec un outil conscient des media queries et états, puis compléter par des rendus. Supprimer uniquement les déclarations prouvées mortes ; les règles répétées dans différents breakpoints peuvent être intentionnelles.

### P2 — entretenir le contenu et le simulateur

1. Maintenir le catalogue, la carte des lacunes, les fiches publiées et les données de jeu alignés à partir des TOML ; les prototypes restent à relire.
2. À chaque mise à jour amont du simulateur, réexaminer provenance, patch M.R.S.C, générateur, page produite et routes. Vérifier séparément le service Render.
3. Avant de prioriser des optimisations de poids ou de performance, établir une mesure locale reproductible puis une mesure sur appareils réels ; ne pas ajouter de télémétrie individuelle implicite.
4. Retirer une sortie ou une clé de stockage seulement après un plan de migration, une vérification des liens et une période de retour arrière.

### P3 — idées à étudier, pas à livrer sans preuve

- recherche transversale locale et tolérante aux accents ; vérifier d’abord la qualité des titres, des synonymes et des thèmes indexés ;
- parcours de lecture imprimables ou à faible débit ; garder des pages autonomes et ne pas ajouter de progression obligatoire ;
- registre de changement éditorial (source, statut, date, raison de révision) avec une vue publique concise ;
- séparation progressive entre fonctions de contenu, composants d’interface et styles, uniquement si des défauts observés justifient le coût ;
- comparaison des hypothèses du simulateur avec affichage explicite de l’incertitude, sous réserve d’une revue méthodologique, de sources et de mesures adaptées.

À éviter sans besoin démontré : chatbot omniprésent, compte obligatoire, dépendances CDN, animation décorative lourde, score de personne, suivi d’audience par défaut, suppression des parcours alternatifs ou promesse de prédiction.

## 6. Critères de réussite et limites de preuve

La modification de la barre ne sera considérée comme validée qu’après :

- contrôles de code, syntaxe, générateurs et intégration réussis ;
- observation visuelle de l’accueil et des autres surfaces citées, dans les largeurs et états ci-dessus ;
- vérification clavier et technologie d’assistance pertinente, puis retours volontaires si les choix restent ambigus ;
- confirmation qu’aucune donnée, requête externe, dépendance ou étape obligatoire n’a été ajoutée.

### Vérification fonctionnelle intégrée — 12 octobre 2026

- Les contrôles de dépôt et d’intégration passent : générateurs, 83 pages, cohérence des données, syntaxe des scripts et 16 routes/API exercées par le vérificateur.
- Sur l’aperçu local, les **83 pages publiques** et **270 routes distinctes de pages ou ressources locales** répondent HTTP 200.
- Des essais DOM simulés ont exercé les commandes d’affichage, le menu et son retour clavier Échap, le repli de la barre lorsque `sessionStorage` est bloqué, le partage de repli, les filtres des 70 fiches, les 15 mondes et le parcours local, une mission d’anglais jusqu’à sa fin avec repli 3D, le chargement volontaire de la carte, ainsi que le choix de source et les réglages du simulateur intégré et autonome. Les scénarios/préréglages ont aussi été activés et leur état annoncé vérifié après le retour réel de l’API locale.
- La revue a révélé que les cartes de scénarios et préréglages du simulateur étaient des `<div>` cliquables, donc pas des commandes clavier natives. Elles ont été remplacées dans la source locale et le correctif versionné par des boutons avec `aria-pressed`, puis régénérées et retestées. La présentation annonçait aussi 9 scénarios alors que le moteur en expose 11 ; le chiffre est corrigé et le vérificateur empêche une nouvelle divergence. Aucun contenu ni parcours n’a été supprimé. L’initiative reste « à tester » pour les validations sur de vrais appareils.

**Limites de la vérification fonctionnelle :** les essais DOM simulés ne calculent pas la mise en page CSS. La passe Chromium ci-dessous mesure le reflow et lance axe, mais ne remplace pas une inspection visuelle humaine, un essai avec lecteur d’écran, un test de zoom du navigateur, des essais volontaires ou la validation des hébergements en production. L’aperçu local ne prouve pas la disponibilité du service Render.

### Contrôle responsive et axe en Chromium headless — 12 octobre 2026

- **Matrice automatisée :** 29 cas sur l’accueil, la transparence, une fiche autonome et le simulateur, à 320, 375, 768, 1024 et 1440 px, avec des variantes tactiles et paysage court. Après correction d’une largeur minimale de 340 px dans la grille de lecture et du repli des commandes longues de leviers, aucun débordement horizontal ni aucune cible tactile sous 44 px n’a été relevé. Les quatre commandes de parcours, leurs libellés, la navigation réelle, le focus visible et le message de repli avec `sessionStorage` bloqué ont été vérifiés.
- **Analyse automatisée :** axe ne relève aucune violation sur les quatre pages représentatives. Les sept onglets du simulateur ont aussi été parcourus à 320 px ; leurs tableaux portent une région nommée et focusable, et axe ne rapporte aucune violation. Avec les détails d’audit ouverts, les 36 régions de tableaux (sources, 20 domaines, familles de leviers, garde-fous) restent dans leur propre conteneur défilant, sans élargir la page ; axe ne rapporte aucune violation.
- **Corrections et génération :** contraste des textes secondaires et des titres de familles du simulateur, noms/focus des tableaux dynamiques et de l’audit, et focus du journal causal. Le patch local et l’empreinte de provenance ont été reconstruits, puis `simulateur/index.html` régénéré. L’API et l’intégration ont été contrôlées séparément par `outils/verifier-integration.py`.

**Limites du contrôle navigateur :** exécution automatisée dans Chromium headless ; les mesures de largeur et axe ne sont pas une inspection visuelle, un test de lecteur d’écran ou une validation humaine. Aucun test de zoom du navigateur, de volontaire ou d’hébergement en production n’est revendiqué.

**État de cette itération :** le prototype de style, les garde-fous, les passes DOM et Chromium headless sont présents dans le dépôt local. Les validations manuelles, la revue de lecteur d’écran et les hébergements restent à vérifier ; aucune page, version ou fonction n’a été retirée. Les documents de référence sont [`rd-innovation-continue.md`](rd-innovation-continue.md), [`rd-audit-securite-optimisation.md`](rd-audit-securite-optimisation.md), [`rd-affichage-adaptatif.md`](rd-affichage-adaptatif.md), [`rd-coherence-visuelle-editoriale.md`](rd-coherence-visuelle-editoriale.md) et le portefeuille [`rd/portefeuille.toml`](rd/portefeuille.toml).
