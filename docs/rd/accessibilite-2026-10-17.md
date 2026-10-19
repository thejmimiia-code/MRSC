# Accessibilité : balayages automatiques du 17 octobre 2026

Statut : **relevé technique par l'agent**, pas un audit d'accessibilité, pas une conformité RGAA ou WCAG, pas une validation par une personne experte ni par des personnes utilisatrices.

## Pourquoi

L'initiative `optimisation-du-site` (P1, état `a-tester`) demandait de vérifier les pages types au clavier, au zoom et avec des technologies d'assistance. Les essais navigateur du dépôt couvrent le réflow, le zoom et les réglages d'affichage, mais aucun contrôle automatique ne portait sur les noms accessibles et les contrastes. Ces passes comblent ce manque mesurable, sans prétendre remplacer une revue humaine.

## Méthode

- Outil : `axe-core` 4.14.0, exécuté dans Chromium via Puppeteer, sur le site servi localement par `outils/serveur-local.py` (moteur désactivé).
- Script reproductible : `outils/verifier-accessibilite.cjs`. Par défaut, il balaie 12 pages représentatives aux deux largeurs et 13 états interactifs ; avec `--etendu`, il balaie toutes les pages HTML du dépôt aux deux largeurs.
- Dépendances installées hors dépôt : `puppeteer-core`, `@sparticuz/chromium` et `axe-core` (commandes en tête du script). Aucun paquet n'est ajouté au dépôt.
- Largeurs : 360 px et 1 280 px.
- Le balayage intervient après chargement des scripts, donc sur les composants construits par JavaScript (cartes de mission, fiches d'apprentissage, commandes d'affichage).
- Aucune donnée personnelle, aucun réseau : tout est servi depuis le dépôt local.

## Premier balayage : pages types

Huit pages × deux largeurs, soit 16 exécutions. Deux règles seulement échouaient :

| Règle | Nœuds | Cause mesurée |
| --- | --- | --- |
| `color-contrast` | 42 | `.footer-rd` à 3,22:1 et liens de pied de page `#2958a2` à 2,31:1 sur fond `#121f43` |
| `label-content-name-mismatch` | 12 | libellés de boutons d'affichage (`Contraste +`, `Interligne +`, `A−`, `A+`) et boutons de monde des Mondes dont le nom accessible ne reprenait pas le texte visible |

Aucune autre règle axe n'a échoué sur ces pages ; cela ne signifie pas que les autres critères sont satisfaits, seulement qu'axe n'a rien détecté parmi ceux qu'il sait tester.

### Corrections

- `assets/css/site.css` : `.footer-rd` passe à `rgba(255, 255, 255, .74)` (contraste calculé 9,3:1 sur `#121f43`) ; les liens de ce paragraphe passent à `#cfe0ff` (12,1:1) ; exception `forced-colors` pour que le texte redevienne `CanvasText` en mode contraste système ; utilitaire `.visually-hidden` ajouté.
- `assets/js/site.js` et `outils/construire-simulateur.py` : les libellés accessibles des boutons `A−` et `A+` commencent par leur texte visible.
- `assets/js/anglais-aventure.js` :
  - les boutons de mission ne posent plus d'`aria-label` : leur nom accessible est directement leur contenu visible (numéro, repère, titre, consigne, action) ;
  - les boutons de monde portent un glyphe `aria-hidden` et une mention masquée « Filtrer les fiches de ce monde. » ;
  - les boutons de parcours gardent un libellé explicite qui commence par leur texte visible.

Après correction, ces 16 exécutions ne remontent plus aucune violation.

## Deuxième passe : toutes les pages

`outils/verifier-accessibilite.cjs --etendu` : 96 pages HTML × deux largeurs, soit **192 exécutions, aucune violation axe**.

La page `simulateur.html` ne se stabilise pas sur `networkidle0` (iframe et appels asynchrones) ; le script y charge la page puis attend cinq secondes avant le balayage.

## Troisième passe : états interactifs

Le balayage au repos ne voit pas les panneaux fermés ni les composants qui apparaissent au clic. Vingt-trois états ont donc été ouverts puis analysés sur les deux largeurs :

- menu mobile ouvert ;
- panneau « Affichage » déplié sur l'accueil, puis contraste renforcé activé ;
- filtre actif sur Apprendre, puis recherche sans résultat ;
- aides dépliées dans une fiche ;
- mission ouverte dans Les Mondes, réponse choisie, puis filtre par monde ;
- commandes d'affichage rendues visibles dans le simulateur, texte agrandi, puis contraste renforcé.

Deux défauts que les passes précédentes ne pouvaient pas voir ont été trouvés.

1. **Panneau « Affichage » (fermé par défaut)** : les libellés de `A−`, `A+` et « Espacement du texte » ne contenaient pas leur texte visible.
   - `A−` et `A+` reçoivent un libellé qui commence par le glyphe visible, dans les 94 pages qui portent l'en-tête et dans le générateur `outils/construire-apprentissages.py`.
   - Les quatre boutons à bascule (« Contraste renforcé », « Espacement du texte » sur le site ; « Contraste + », « Interligne + » dans le simulateur) ne modifient plus leur libellé à l'activation : leur nom reste celui affiché et `aria-pressed` porte l'état. Un libellé qui bascule entre « activer » et « désactiver » doublait cette information et créait le décalage.
   - `simulateur/index.html` a été régénéré ; les 81 fiches ont été vérifiées après modification du générateur.
2. **Bouton secondaire du héros des Mondes, à 1 280 px** : texte blanc sur `rgba(11, 33, 51, .45)`, soit un fond effectif `#919ba3` et un contraste de 2,82:1 une fois la couche translucide composée sur du clair. À 360 px, le recadrage de l'image donnait un fond plus sombre : le défaut n'apparaissait qu'à une largeur.
   - Le fond passe à `rgba(11, 33, 51, .72)` (6,5:1 dans le pire cas sur fond blanc) et le survol à `.9` ; les pastilles de la même zone passent à `.7`.
   - Ce calcul reste une borne : l'image de fond n'est pas analysée, et le survol n'est pas mesuré par axe.

Après correction, les **47 exécutions** du script par défaut (24 pages + 23 états) ne remontent aucune violation.

## Ce que ces mesures ne disent pas

- axe ne couvre qu'une partie des critères WCAG ; l'absence de violation n'est ni une conformité ni une preuve d'utilisabilité.
- Aucun essai avec lecteur d'écran, aucune navigation clavier exhaustive, aucune revue par une personne experte en accessibilité.
- Chromium seulement ; Firefox et Safari ne sont pas testés.
- Seuls les états listés sont balayés, une fois ; une session complète, les formulaires en erreur, les contenus repliés des fiches et les missions jusqu'au bout ne le sont pas.
- Les contrastes recalculés à la main portent sur le fond connu du pied de page ou sur une borne « fond blanc » ; les images de fond ne sont pas analysées, et les états de survol ne sont pas mesurés par axe.
- La version publiée sur GitHub Pages n'est pas contrôlée dans cette passe.

## Suite

- Faire relire les corrections par une personne compétente en accessibilité et, si possible, par un utilisateur de lecteur d'écran.
- Élargir les états balayés (formulaires en erreur, mission terminée) et refaire la mesure après toute modification des composants interactifs.
- Ne pas modifier l'état de `optimisation-du-site` avant cette relecture : les preuves restent des mesures locales par l'agent.
