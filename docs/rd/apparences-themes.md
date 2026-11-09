# Apparences du site — six thèmes dans « Personnalisation »

**Note de travail du 7 novembre 2026. État : proposition d'agent, contenu relu par agent le 7 novembre 2026 avec sources primaires confrontées.**
Ce document n'est ni une charte graphique adoptée, ni une validation visuelle, ni un essai avec des personnes. La relecture de contenu et des sources a été prise en charge par la nouvelle étape `outils/verifier-relecture-contenus.py` (rapport : [`relecture-apparences-2026-11-07.md`](relecture-apparences-2026-11-07.md)) ; la personne garde la validation du rendu à l'œil — placement, style, construction — sans avoir à lire les registres. Il sépare ce qui a été demandé, ce qui a été mesuré, ce qui a été corrigé et ce qui reste un choix humain.

## 1. Signal, fait, hypothèse, proposition

| Nature | Ce qui est écrit ici |
| --- | --- |
| **Signal observé** | La demande du 7 novembre 2026 : proposer dans le menu « Personnalisation » plusieurs configurations d'apparence sous forme de thèmes, en commençant par les plus utilisés sur le Web, puis en enrichissant avec des styles inspirés d'ambiances de série des années 80, de rétro-futurisme et d'univers d'arcade, **en les nommant différemment**. |
| **Fait mesuré** | Le dépôt disposait déjà de 108 jetons de couleur dans `:root`, d'un panneau « Personnalisation » construit par `assets/js/site.js` et partagé par les 13 pages et les fiches, d'un réglage de contraste renforcé et de règles `@media (forced-colors: active)`. |
| **Hypothèse de conception** | Un thème peut être porté par les seuls jetons, sans réécrire les pages : deux attributs sur `<html>` suffisent, l'un pour le choix nominal, l'autre pour le fond résolu. |
| **Proposition livrée** | Six thèmes, une seule feuille CSS et un seul script. Aucune page HTML ne fige d'apparence. |
| **Non fait** | Aucune étude de fréquentation, aucun sondage, aucun essai avec des personnes, aucune **relecture humaine** des libellés (la relecture de contenu par agent est faite, voir § 5), aucune comparaison visuelle validée par une personne, aucun lecteur d'écran. |

L'expression « les plus utilisés sur le net » vient de la demande et n'est citée ici que comme signal. La relecture par agent du 7 novembre 2026 a confronté cette formulation à MDN : `color-scheme` documente `light` et `dark` comme schémas **du système d'exploitation**, et `prefers-color-scheme` comme préférence exprimée par le système ou le navigateur — rien n'y mesure la fréquence des réglages proposés par les sites Web. **Aucune allégation de fréquence n'est donc retenue.** Les trois réglages documentés (**suivre l'appareil**, **clair**, **sombre**) sont placés en tête par décision de conception, sans statistique. Détail et source : `docs/rd/relecture-apparences-2026-11-07.md`, correction n° 3.

## 2. Les six choix

| Valeur | Nom affiché | Fond | Ce que change |
| --- | --- | --- | --- |
| `systeme` | Suivre l'appareil | résolu par `prefers-color-scheme` | Reprend le réglage clair/sombre de l'appareil, et le suit sans rechargement. |
| `clair` | Papier clair | clair | La palette habituelle du site, explicitement choisie. |
| `sombre` | Nuit sobre | sombre | Tous les jetons basculent, sans décor ajouté. |
| `bobine` | Bobine nocturne | sombre | Bleu nuit, néon rouge, fines lignes de bande magnétique. |
| `horizon` | Cap horizon | sombre | Cuivre et ambre, lignes obliques, rayons un peu plus doux. |
| `arcade` | Salle d'arcade | sombre | Grille cyan et magenta, accents lumineux, rayons plus carrés. |

Les trois derniers noms, couleurs, dégradés et libellés sont **originaux**. Les références citées dans la demande ont servi d'ambiance générale ; aucun nom d'œuvre, de marque, de personnage ni de logotype n'est repris dans le produit, et aucune affiliation n'est suggérée. `outils/verifier-apparences.py` refuse la réapparition de ces noms dans `site.css` et `site.js`. Le choix d'une des quatre chartes de `direction-artistique-motion` reste **une décision distincte, toujours ouverte** : ces thèmes sont des préférences d'affichage, pas la charte de l'association.

## 3. Comment c'est construit

- `assets/js/site.js` écrit `data-apparence` (choix nominal : accents et décor) et `data-apparence-fond` (`clair` ou `sombre`). « Suivre l'appareil » résout donc le même bloc de jetons que « Nuit sobre », sans dupliquer la palette.
- `assets/css/site.css` contient **un seul** bloc `html[data-apparence-fond="sombre"]`, généré depuis les 108 jetons de couleur de `:root`. La porte vérifie qu'aucun jeton n'est oublié : une carte restée claire avec du texte clair deviendrait illisible.
- Le bleu devient un accent lumineux en fond sombre ; `--on-accent` passe donc à une encre sombre. Trois règles qui écrivaient du blanc sur fond bleu sont reprises explicitement. Le premier relevé navigateur a d'ailleurs trouvé un contraste de **1,48:1 à 2,03:1** sur les boutons avant cette correction ; il est remonté à **9,20:1 – 12,64:1** après.
- Les trois palettes inspirées reprennent aussi `--navy`, `--navy-deep` et `--navy-deep-2` : la barre de navigation change donc de surface (prune, cuivre, indigo) au lieu de ne différer que par un liseré. Toutes restent sombres, `--on-navy` garde son contraste.
- Les décors sont des dégradés statiques posés sur le fond du corps, derrière les cartes qui gardent leur surface. **Aucune animation n'est ajoutée** : `prefers-reduced-motion` n'a rien à désactiver. Les couleurs forcées du système et le contraste renforcé neutralisent les décors.
- Préférence `mrsc-apparence` dans le stockage local, avec repli pour la visite si le stockage est bloqué ; synchronisation entre onglets et vers l'iframe locale de même origine ; bouton de retour à « Suivre l'appareil ». Aucune donnée n'est envoyée, aucun compte, aucun témoin de mesure.
- Une seule source : les 13 pages et les fiches d'apprentissage chargent les mêmes `site.css` et `site.js`. La porte refuse qu'une page fige `data-apparence` dans son HTML.

## 4. Ce qui reste ouvert

- **Validation visuelle à l'œil** du placement, du style et de la construction, ainsi qu'une comparaison côte à côte si la personne le souhaite. La relecture de contenu, des noms et des sources n'est plus à sa charge : elle a été faite par l'étape dédiée le 7 novembre 2026 (**22 concordant, 3 corrige**, zéro chaîne publique non couverte). Aucune validation humaine du fond n'a été consignée et aucune entrée n'a été ajoutée à `relectures.toml`.
- **Simulateur** : l'attribut est propagé à l'iframe locale, mais la page du simulateur est générée avec sa propre feuille ; elle ne suit pas encore les thèmes. À traiter dans un lot séparé, avec le générateur.
- **Éclair de thème clair au rechargement** : `site.js` est chargé en `defer`, comme les autres préférences du site. Un thème sombre mémorisé peut donc s'appliquer après un premier rendu clair. Corriger demanderait un script de démarrage dans l'en-tête des pages, soit un changement de gabarit à arbitrer.
- **Portée du contraste** : la porte mesure les paires de jetons déclarées, et le relevé navigateur mesure quelques styles calculés sur l'accueil. Les 13 pages, tous les états (survol, focus, ouvert) et les lecteurs d'écran ne sont pas couverts.
- `outils/auditer-affichages.mjs` compte déjà les glyphes décoratifs `font-size: 0` comme « texte sous 12 px » ; l'ajout d'un chevron de plus dans le panneau ajoute un faux positif du même type. La sonde reste à corriger, avec un banc qui exécute réellement le filtre.

## 5. Preuves

- `python3 outils/verifier-apparences.py` — ordre des six choix, 108 jetons, contrastes, décors statiques, source unique.
- `python3 outils/test_mutations_apparences.py` — 12 fautes plantées, toutes refusées ; copie intacte verte.
- `node outils/test-experience.cjs` — 13/13 essais navigateur avec le panneau à cinq réglages.
- [`releve-apparences-2026-11-07.md`](releve-apparences-2026-11-07.md) — mesures Chromium 153 des six thèmes.
- `python3 outils/verifier-relecture-contenus.py` — 8 sources primaires datées, 25 affirmations rattachées, 20 chaînes publiques couvertes, 0 promotion humaine.
- `python3 outils/test_mutations_relecture_contenus.py` — 19 fautes plantées, toutes refusées ; copie intacte verte.
- [`relecture-apparences-2026-11-07.md`](relecture-apparences-2026-11-07.md) — rapport de relecture par agent et trois corrections issues des sources (constante de luminance, tolérance de seuil, allégation de fréquence).
