---
name: integration-securite
description: Use to integrate knowledge and interaction into the existing site, game, data pipeline, generator, API, storage or deployment while preserving security and privacy boundaries.
---
# Skill — Intégration web, données et sécurité

## Quand l’activer

Pour toute modification de code, schéma, navigation, sauvegarde locale, média, API, génération, workflow, publication ou intégration d'un service tiers.

## Entrées

- Architecture et source de vérité existantes; `AGENTS.md`, générateurs et contrôles.
- Flux de données entrée → traitement → affichage → stockage/transmission.
- Cible publiée, solution de repli et contraintes de sécurité/accessibilité.

## Méthode

1. Repérer si la ressource est générée. Modifier la source puis régénérer avec l'outil propriétaire; ne pas éditer une sortie à la main.
2. Définir les entrées contrôlées, les limites, les erreurs et les comportements sans réseau/stockage/API/WebGL.
3. Minimiser les données; utiliser textContent ou échappement sûr; aucune requête externe, télémétrie ou stockage de réponse non documentés.
4. Si un service tiers est proposé, le déclencher sur action claire, expliquer sa finalité et prévoir une alternative.
5. Mettre à jour ensemble routes locales, navigation, sitemap, allowlist de publication, notice et scripts si nécessaire.
6. Lancer compilation, linter/tests disponibles, vérificateurs de liens/contenus/sécurité, puis tester les interactions touchées sur petit/large écran ou simulateur DOM.
7. Relire `git diff`, garder les modifications préexistantes, supprimer les dépendances/artefacts temporaires et rapporter ce qui n'a pas été essayé.

## Livrables

- Changement traçable dans le bon fichier source.
- Tests automatisés ciblés et test manuel/DOM documenté avec limites.
- Notice, statut de données et solution de repli actualisés.

## Garde-fous

- Ne pas exposer sources/outils internes à travers l'hébergement statique.
- Pas de secrets, données personnelles ou réponses d'apprentissage en logs ou dépôt.
- Pas de nouvelle dépendance distante, CDN, police ou iframe autochargé sans revue.
- Ne pas déclarer « sécurisé », « accessible » ou « compatible partout » sur la seule base d'une compilation.
