---
name: documentation-technique
description: Rédige et entretient des documents, guides, exemples et décisions techniques alignés sur le fonctionnement vérifié du dépôt.
---
# Documentation technique

## Quand l’activer

Pour un README, guide utilisateur ou contributeur, procédure d’installation, documentation d’API, commentaire, ADR, journal de migration, texte d’interface ou mise à jour de documentation après un changement.

## Entrées

- Personne qui lit, tâche à réaliser et contexte d’usage.
- Comportement réel du produit, source de vérité, générateurs et versions.
- Terminologie du projet, langue, format existant, liens et droits de réutilisation.
- Commandes ou exemples que le document souhaite présenter comme opérationnels.

## Méthode

1. **Vérifier avant d’écrire.** Lire l’implémentation et les docs voisines ; déterminer si le fichier est généré, maintenu manuellement ou dupliqué. Trouver l’emplacement propriétaire avant l’édition.
2. **Concevoir pour la tâche du lecteur.** Donner le prérequis, l’action, le résultat attendu, les erreurs courantes et la solution de repli dans l’ordre d’usage. Expliquer les termes nécessaires sans reprendre l’architecture comme si elle était visible.
3. **Séparer fait et projection.** Présenter ce qui existe, ce qui a été testé, ce qui est proposé, ce qui reste inconnu et la date/version à laquelle cela a été vérifié.
4. **Garder les exemples fidèles.** Réutiliser la syntaxe, les noms et chemins réels ; vérifier les commandes et extraits sur l’environnement du dépôt avant d’annoncer qu’ils fonctionnent. Éviter les commandes destructrices ou les valeurs secrètes.
5. **Protéger la source de vérité.** Mettre à jour l’original, puis régénérer les sorties avec leur outil propriétaire. Synchroniser liens, ancres, tables de matière et index concernés sans dupliquer le document entier.
6. **Réviser.** Vérifier langue, accessibilité, liens, cohérence, version, licence et absence de données personnelles. Réduire l’ambiguïté et supprimer les affirmations qui n’ont pas de preuve.
7. **Entretenir.** Lors d’une modification d’API, de comportement ou de procédure, comparer changements et docs ; ajouter une note de migration quand une ancienne manière de faire devient incompatible.

## Livrables

- Document orienté lecteur, relié à la source de vérité.
- Exemples ou commandes testés, ou clairement marqués comme non vérifiés.
- Liens et références cohérents, limites et date de révision quand utiles.

## Garde-fous

- Ne jamais inventer un comportement, une commande, une option, un résultat, une garantie ou une licence.
- Ne pas modifier à la main une sortie générée ni supprimer une ancienne procédure avant l’audit de ses usages et voies de migration.
- Ne pas inclure secrets, identifiants, données privées ou captures contenant des informations non destinées au public.
- Ne pas surcharger avec de la prose marketing, des répétitions ou une taxonomie décorative ; privilégier la précision et la lecture rapide.
- Une doc à jour ne remplace pas un essai du produit ni une relecture experte.
