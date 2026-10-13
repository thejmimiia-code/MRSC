---
name: direction-artistique-motion
description: Cadre une direction artistique distinctive, le rendu graphique et les animations web du M.R.S.C. À activer pour une exploration visuelle, une illustration, une micro-interaction ou une refonte d’interface du site.
---

# Direction artistique et mouvement web — M.R.S.C

Aider à rendre les pages du M.R.S.C. ludiques, attirantes et reconnaissables, au service de la découverte et de l’apprentissage. Rechercher une expression originale propre au projet, sans prétendre prouver qu’aucun équivalent n’existe. Cette carte est une méthode de conception et d’essai, pas une identité déjà approuvée.

## Quand l’activer

Avant de proposer ou modifier une palette, une composition, une illustration, le rythme d’une page, une animation, une transition ou une expérience destinée à donner envie d’explorer le site. La combiner avec `conception-innovation`, `conception-pedagogique`, `conception-jeu`, `accessibilite-co-conception`, `integration-securite` et `evaluation-maintenance` selon la portée.

## Entrées

- La demande exacte, la page pilote éventuelle et la tâche que la personne doit pouvoir accomplir.
- Les sources de vérité, contenus, marques et composants déjà présents ; l’état Git et les générateurs concernés.
- Les contraintes du public et des contextes connues, sans fabriquer de persona ni de témoignage.
- Les références visuelles et techniques, leur auteur, leur licence et ce qui peut ou non être repris. Dans Claude Code, `.claude/skills/frontend-design/` et `.claude/skills/motion-design/` conservent deux snapshots amont audités ; ce sont des références facultatives, la méthode M.R.S.C. et `AGENTS.md` restent prioritaires.
- Les objectifs de mouvement, les contextes mobile/clavier/tactile, le mouvement réduit, les performances visées et les limites de validation.

Si une entrée manque, distinguer les faits des hypothèses et proposer des options plutôt que de figer un choix visuel majeur.

## Méthode

1. **Auditer avant d’inventer.** Lire `AGENTS.md`, `docs/rd/visuel-motion.md`, `docs/rd-coherence-visuelle-editoriale.md` et `docs/rd-affichage-adaptatif.md`. Examiner la page réelle, les règles de `assets/css/site.css`, les scripts et leurs générateurs. `docs/pistes-visuelles-ia.html` est une planche propre au dossier IA, pas une direction validée pour tout le site. Préserver le contenu, les liens, les fonctions et les réglages existants.
2. **Clarifier le propos.** Relier le choix graphique à une idée réelle du M.R.S.C. — expériences, connaissances, transmission, société civile — et à un objectif de lecture ou d’apprentissage. Ne pas ajouter de décoration qui concurrence l’information.
3. **Diverger.** Produire trois directions qui diffèrent réellement par leur composition, leur rythme et leur langage graphique. Pour chacune, préciser une palette courte, les rôles typographiques, la mise en page, un motif ou élément de signature, la manière facultative de découvrir un contenu, les avantages, les risques et les limites. Écarter les rendus génériques choisis par défaut (cartes uniformes, gradients décoratifs, cerveau/robot générique, entrées animées systématiques). Une signature de mouvement peut être une seule action cohérente, pas un effet sur chaque bloc.
4. **Concevoir le mouvement par son intention.** Pour chaque animation envisagée, décrire : le changement rendu compréhensible, le déclencheur, l’élément principal, le retour visuel, la durée/easing à essayer, l’équivalent immobile, la réduction de mouvement et le coût technique. Privilégier une réponse au geste, une explication spatiale ou une révélation facultative. Si l’effet ne sert ni la compréhension, ni l’orientation, ni une émotion voulue sans gêner la lecture, ne pas l’ajouter.
5. **Explorer la nouveauté sans pression.** Une piste possible est une sélection éditoriale « À découvrir » et un bouton « Une autre piste », alimentés par un ensemble local de contenus et sans profil personnel. Garder les rubriques et les parcours entiers immédiatement accessibles. Traiter le mélange aléatoire, la variation par visite et l’effet sur l’apprentissage comme des hypothèses à comparer, pas comme des bénéfices prouvés.
6. **Prototyper petit et réversible.** Commencer par une planche locale/non publiée ou une seule page pilote. Conserver le HTML lisible et les voies sans JavaScript. Utiliser d’abord le HTML, le CSS et le JavaScript déjà présents ; ne pas introduire React, Framer Motion, p5.js, une police distante, un CDN ou un service externe sans besoin démontré et accord adapté.
7. **Critiquer et vérifier.** Comparer les options au brief et au système visuel existant. Vérifier clavier, focus, contraste, zoom/reflow, tactile, libellés, mouvement réduit, faible débit et pages sans script selon la surface. Examiner des captures dans plusieurs largeurs lorsque l’environnement le permet. Les tests automatisés n’attestent ni qualité esthétique humaine, ni conformité complète, ni effet pédagogique.
8. **Préparer une décision.** Consigner le concept, l’hypothèse, la preuve, la licence des références, les compromis, les fichiers touchés, les essais réels et la suite dans le document R&D et le portefeuille si la piste est structurante. Garder les directions concurrentes jusqu’à ce qu’une sélection soit réellement faite.

## Livrables

- Un bref audit de l’existant et des contraintes de la pile.
- Trois propositions visuellement distinctes, accompagnées de croquis/wireframes ou d’une planche de comparaison.
- Pour le mouvement : un inventaire d’effets justifiés et leurs états de repli, pas seulement une liste d’easings.
- Une hypothèse et un prototype isolé pour un parcours précis ; une proposition de tâches d’évaluation accessibles et respectueuses de la vie privée.
- Une liste claire des changements, tests exécutés, limites et validations encore attendues.

## Garde-fous

- Viser une personnalité originale du M.R.S.C. ; ne jamais promettre une nouveauté absolue ni copier une identité, une illustration, un personnage ou un motif reconnaissable.
- Ne pas importer un skill, une image, une police, du code d’exemple ou un média sans contrôler source, licence, attribution, pertinence et dépendances.
- Respecter `prefers-reduced-motion` en retirant les déplacements/effets non essentiels, sans faire disparaître l’information ; ne pas lancer de boucle décorative, de parallaxe, de défilement forcé ou de flash. Une animation prolongée doit être évitable et contrôlable.
- Garder tout contenu lisible sans animation ; rendre les mêmes actions accessibles au clavier et au toucher, sans dépendre du survol. Pour les commandes tactiles principales, viser au moins 44 px.
- Pas de compte obligatoire, de série quotidienne, de pénalité d’absence, de compte à rebours, de progression forcée, de score individuel, de télémétrie implicite ni de personnalisation fondée sur un profil.
- Ne pas optimiser le temps passé ou la fréquence des visites comme substitut à l’apprentissage. N’annoncer un bénéfice d’apprentissage, de mémorisation ou d’engagement qu’après un essai adapté et volontaire.
- Préserver chaque page, version, fonction et source générée tant que ses usages, sa provenance et les risques de régression n’ont pas été examinés.
