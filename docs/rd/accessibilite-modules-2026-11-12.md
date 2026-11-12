# Accessibilité : trois modules pour les personnes handicapées — 12 novembre 2026

Statut : **proposition de l'agent, mesurée en navigateur**, pas un audit d'accessibilité, pas une conformité RGAA ou WCAG, pas une validation par des personnes handicapées ni par une personne experte.

## Pourquoi

La demande du 12 novembre 2026 était d'ajouter, dans le menu « Personnalisation », les modules d'accessibilité destinés aux personnes handicapées qui manquaient, en s'inspirant de « Lisio » et de l'exemple du site MDPH en ligne de la CNSA (`mdphenligne.cnsa.fr`).

Le site possédait déjà six réglages : taille du texte (75 à 130 %), contraste renforcé, espacement du texte (critère WCAG 1.4.12), six apparences, six présentations de page et une lecture à voix haute. Trois besoins documentés n'étaient couverts par aucun d'eux :

| Besoin | Ce qui manquait | Module ajouté |
| --- | --- | --- |
| Lire avec des lettres plus distinctes (dyslexie, difficultés de lecture) | la police et l'interlettrage étaient figés ; seul le corps changeait | **Lecture facilitée** |
| Supprimer les mouvements (troubles vestibulaires, photosensibilité) | le site suivait `prefers-reduced-motion`, mais une personne dont le système ne l'active pas n'avait aucune commande | **Réduire les mouvements** |
| Naviguer au clavier sans deviner les repères | le lien d'évitement n'apparaissait qu'au focus, et le contour était fin | **Repères clavier visibles** |

## Droits : ce qui a été vérifié, et ce qui n'a pas été repris

**Lisio** (`lisio.fr`, « Web4All ») est une solution logicielle **propriétaire et payante**, en surcouche (SaaS), éditée par une société. Sa documentation décrit les fonctions offertes (affichage sur mesure, synthèse vocale, traductions, zone bas débit, affichage éco). Rien n'indique une licence libre. Aucun de ses fichiers, textes, icônes, libellés ou mises en page n'a été copié. Ses fonctions ont seulement servi de **liste de besoins à couvrir**, comme une veille concurrentielle.

**MDPH en ligne** (`mdphenligne.cnsa.fr`) est un téléservice public de la CNSA. Il diffuse des documents en FALC (facile à lire et à comprendre) et s'appuie sur une bannière d'accessibilité Lisio. Là encore : aucun texte, aucun visuel, aucun composant n'a été repris. Le site ne copie ni son bandeau « Notre site s'adapte à vos besoins », ni sa liste de profils, ni ses pictogrammes.

Ce qui a été fait à la place :

1. **Trois modules écrits pour ce site**, avec son vocabulaire, ses couleurs et ses composants (`display-control`, lignes du panneau, `role="status"`).
2. **Une icône originale** : une silhouette aux bras ouverts dessinée en SVG pour ce site, en masque CSS, comme les cinq autres icônes du panneau. Aucun pictogramme existant n'est réutilisé.
3. **Des polices système** (Verdana, Trebuchet MS, DejaVu Sans, puis la police de l'appareil) plutôt qu'une police « spéciale dyslexie » commerciale : aucune licence à acheter, aucun fichier à télécharger, donc aucun poids ajouté à la page.
4. **Aucun service distant** : les réglages sont des classes CSS et des valeurs de stockage local. La lecture vocale existante continue d'utiliser la voix de l'appareil.

Les deux sites restent cités comme **sources d'inspiration** dans ce document, sans lien d'affiliation ni reprise de marque.

## Ce que chaque module fait, exactement

### Lecture facilitée (`html.aide-lecture`)

- Texte suivi en Verdana / Trebuchet MS / DejaVu Sans, puis police système ;
- interlettrage de 0,035 em, espacement des mots de 0,12 em, interligne 1,75 ;
- texte **désjustifié** (une justification ouvre des rivières blanches qui gênent la lecture dyslexique) et césure coupée ;
- titres avec la même police, pour ne pas juxtaposer deux formes.

### Réduire les mouvements (`html.mouvement-attenue`)

- `animation-duration`, `transition-duration` ramenés à 0,001 ms, une seule itération ;
- `scroll-behavior: auto` ;
- l'animation du panneau de personnalisation coupée nommément.

Le réglage de la personne **prime** sur les animations du site, y compris quand le système ne demande rien. Il ne remplace pas `prefers-reduced-motion` : les deux continuent de s'appliquer.

### Repères clavier visibles (`html.reperes-visibles`)

- le lien « Aller au contenu principal » reste affiché en haut à gauche, avec un contour ;
- le contour de focus passe de 2 à 4 px ;
- les liens soulignés gardent leur soulignement au focus.

Rien ne s'ouvre ni ne se ferme : c'est un repère, pas une navigation parallèle.

## Mesures faites le 12 novembre 2026

Chromium sans interface (`puppeteer-core` + `@sparticuz/chromium`), site servi par `outils/serveur-local.py`.

| Ce qui est mesuré | Résultat |
| --- | --- |
| Panneau présent dans « Personnalisation » | oui, ligne « Accessibilité » entre « Présentation » et « Écouter la page » |
| Effet de « Lecture facilitée » | police calculée `Verdana, "Trebuchet MS", …`, interlettrage 0,58 px sur un texte de 16,64 px |
| Effet de « Réduire les mouvements » | durée de transition calculée `1e-06s` |
| Effet de « Repères clavier visibles » | `transform: none` sur le lien d'évitement, hauteur mesurée 45 px |
| Mémorisation | trois clés `mrsc-lecture-aide`, `mrsc-mouvement-attenue`, `mrsc-reperes-visibles` |
| Persistance entre pages | classes présentes sur `apprendre.html` après passage par l'accueil |
| Clavier | Entrée ouvre, premier Échap referme la ligne seule, second Échap le panneau |
| Débordement, largeurs 320 / 360 / 768 / 1280 px | aucun débordement horizontal, panneau contenu dans la fenêtre |
| Cibles des trois boutons | 44 px de haut à toutes les largeurs |
| Contraste du texte d'aide (seuil 4,5:1) | 6,34:1 en clair, 10,67:1 en sombre |
| Contraste du libellé des boutons | 12,29:1 en clair, 10,17:1 en sombre |
| axe-core, 49 exécutions par défaut | 0 violation |
| axe-core avec les trois modules actifs, 4 pages | 0 violation |
| `outils/test-experience.cjs` | 14/14 essais |

## Garde-fous ajoutés

- `outils/verifier-affichages.py` — un vingt-deuxième garde-fou lit la feuille et le script : présence des trois modules, police sur le texte suivi, désjustification, valeur réelle des durées coupées, `scroll-behavior`, lien d'évitement ramené à l'écran, commande et clés de mémoire dans `site.js`.
- `outils/test_mutations_affichages.py` — sept mutations plantent les fautes correspondantes (police effacée, désjustification retirée, durée remise à 1 s, lien d'évitement non ramené, commande retirée, préférence non mémorisée) et le banc exige que chacune soit vue.
- `outils/test-experience.cjs` — un quatorzième essai mesure les effets, la mémoire entre pages, le bouton de retour et l'ordre des Échap.

## Limites

- **Aucun essai avec des personnes handicapées** n'a eu lieu ce jour. Les trois modules répondent à des besoins documentés, pas à des besoins observés sur ce site.
- Ce n'est **ni un audit RGAA**, ni une conformité WCAG, ni une validation par une personne experte. axe-core ne voit qu'une partie des critères.
- La police « lecture facilitée » n'est pas une police conçue pour la dyslexie : c'est un choix de formes distinctes et largement disponibles. Un avis orthophonique ou une relecture par des personnes concernées reste nécessaire.
- Le contenu n'est pas traduit en FALC. Un module d'affichage ne remplace pas une réécriture en facile à lire et à comprendre ; ce chantier toucherait les 108 fiches et n'est pas ouvert.
- Aucun module ne remplace un lecteur d'écran ni les réglages du système.
- Les fonctions de Lisio non reprises (traduction automatique, zone bas débit, lecture vocale en langue étrangère) restent hors périmètre : elles demanderaient des services distants ou des licences.
