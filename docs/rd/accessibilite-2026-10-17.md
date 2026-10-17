# Accessibilité : balayage automatique du 17 octobre 2026

Statut : **relevé technique par l'agent**, pas un audit d'accessibilité, pas une conformité RGAA ou WCAG, pas une validation par une personne experte ni par des personnes utilisatrices.

## Pourquoi

L'initiative `optimisation-du-site` (P1, état `a-tester`) demandait de vérifier les pages types au clavier, au zoom et avec des technologies d'assistance. Les essais navigateur du dépôt couvrent le réflow, le zoom et les réglages d'affichage, mais aucun contrôle automatique ne portait sur les noms accessibles et les contrastes. Cette passe comble ce manque mesurable, sans prétendre remplacer une revue humaine.

## Méthode

- Outil : `axe-core` 4.14.0, exécuté dans Chromium via Puppeteer, sur le site servi localement par `outils/serveur-local.py` (moteur désactivé).
- Pages : accueil, apprendre, une fiche type (`apprendre/fiches/civ-verifier-information.html`), Les Mondes, transparence, simulateur (copie locale générée), ÉVA, documents.
- Largeurs : 360 px et 1 280 px, soit 16 exécutions.
- Le balayage intervient après chargement complet des scripts, donc sur les composants construits par JavaScript (cartes de mission, fiches d'apprentissage, commandes d'affichage).
- Aucune donnée personnelle, aucun réseau : tout est servi depuis le dépôt local.

## Résultat avant correction

Deux règles seulement échouaient sur les 16 exécutions :

| Règle | Nœuds | Cause mesurée |
| --- | --- | --- |
| `color-contrast` | 42 | `.footer-rd` à 3,22:1 et liens de pied de page `#2958a2` à 2,31:1 sur fond `#121f43` |
| `label-content-name-mismatch` | 12 | libellés de boutons d'affichage (`Contraste +`, `Interligne +`, `A−`, `A+`) et boutons de monde des Mondes dont le nom accessible ne reprenait pas le texte visible |

Aucune autre règle axe n'a échoué sur ces pages ; cela ne signifie pas que les autres critères sont satisfaits, seulement qu'axe n'a rien détecté parmi ceux qu'il sait tester.

## Corrections apportées

- `assets/css/site.css` : `.footer-rd` passe à `rgba(255, 255, 255, .74)` (contraste calculé 9,3:1 sur `#121f43`) ; les liens de ce paragraphe passent à `#cfe0ff` (12,1:1) ; exception `forced-colors` pour que le texte redevienne `CanvasText` en mode contraste système ; utilitaire `.visually-hidden` ajouté.
- `assets/js/site.js` et `outils/construire-simulateur.py` : les libellés accessibles des commandes d'affichage commencent désormais par leur texte visible (« Contraste + — … », « Interligne + — … », « A− — … », « A+ — … »).
- `assets/js/anglais-aventure.js` :
  - les boutons de mission ne posent plus d'`aria-label` : leur nom accessible est directement leur contenu visible (numéro, repère, titre, consigne, action) ;
  - les boutons de monde portent un glyphe `aria-hidden` et une mention masquée « Filtrer les fiches de ce monde. » ;
  - les boutons de parcours gardent un libellé explicite qui commence par leur texte visible.

## Résultat après correction

Les 16 exécutions (8 pages × 2 largeurs) ne remontent plus aucune violation axe, y compris pour les deux règles ci-dessus.

Contrôles fonctionnels complémentaires exécutés le même jour :

- `outils/test-experience.cjs` : 8/8 essais navigateur réussis ;
- sonde locale sur Les Mondes : ouverture d'une escale, focus sur le titre, retour à la carte avec focus rendu au bouton d'origine, filtre par monde appliqué, nom accessible du bouton de mission cohérent (« 01 Pré-A1 · A1 La gare des marées … Choisir cette escale »).

## Limites

- axe ne couvre qu'une partie des critères WCAG ; l'absence de violation n'est ni une conformité ni une preuve d'utilisabilité.
- Aucun essai avec lecteur d'écran, aucune navigation clavier exhaustive, aucune revue par une personne experte en accessibilité.
- Chromium seulement ; Firefox et Safari ne sont pas testés.
- Les états dynamiques ne sont balayés qu'au chargement et après les interactions de la sonde, pas pendant toute une session.
- Les contrastes recalculés à la main portent sur le fond connu du pied de page ; un changement de thème ou de fond invaliderait ces valeurs.
- Aucun contrôle de la version publiée sur GitHub Pages dans cette passe.

## Suite

- Faire relire les corrections par une personne compétente en accessibilité et, si possible, par un utilisateur de lecteur d'écran.
- Ajouter les états interactifs (menu ouvert, panneau de réglages, mission en cours) à un balayage ultérieur.
- Ne pas modifier l'état de `optimisation-du-site` avant cette relecture : les preuves restent des mesures locales par l'agent.
