---
name: strategie-tests
description: Définit des vérifications proportionnées au risque et teste des comportements observables sans ajouter de dépendances par réflexe.
---
# Stratégie de tests

## Quand l’activer

Avant ou pendant un changement qui modifie un comportement, pour un bug, une migration, une intégration, une génération, une interaction ou une fonctionnalité de sécurité. Pour un changement documentaire, choisir plutôt les contrôles de liens, de structure et de cohérence réellement nécessaires.

## Entrées

- Critères d’acceptation, contrat observable et source de vérité.
- Risques de régression, types d’entrées, limites et comportements de repli.
- Suite, outils, commandes et conventions déjà présents dans le dépôt.
- Environnements ou personnes qui doivent encore valider le résultat.

## Méthode

1. **Tester d’abord ce qui coûte le plus en cas d’erreur.** Identifier chemins critiques, données non fiables, états limites, sorties générées, intégrations, clavier/tactile et mouvement réduit selon la surface.
2. **Choisir la couche minimale efficace.** Test unitaire pour une règle isolée ; intégration pour les frontières ; navigateur ou essai manuel pour les interactions et le rendu. Ajouter un niveau supérieur seulement s’il couvre un risque que le niveau inférieur ne voit pas.
3. **Tester le contrat.** Préférer ce que la personne ou l’appelant observe à une fonction privée, un nombre d’appels internes ou un instantané fragile. Pour un bug, écrire un test qui reproduit précisément le symptôme lorsqu’un point d’entrée pertinent existe.
4. **Rendre l’oracle indépendant.** Calculer le résultat attendu à partir du besoin, d’une référence ou d’un cas travaillé fiable. Vérifier qu’un test peut réellement échouer si le comportement visé se casse.
5. **Limiter doublons et mocks.** Réutiliser la suite existante ; mocker seulement les frontières externes ou les nondéterminismes nécessaires. Ne pas simuler des composants internes que le test cherche précisément à vérifier.
6. **Exécuter par étapes.** Lancer le test ciblé, puis les tests voisins et la suite prescrite si le temps et l’environnement le permettent. Surveiller les sorties réelles ; ne pas continuer comme si un échec préexistant était vert.
7. **Déclarer la portée.** Distinguer compilation, tests unitaires, intégration, navigateur, inspection visuelle, accessibilité réelle et essai utilisateur. Noter ce qui n’a pas été exécuté et pourquoi.

## Livrables

- Matrice courte `risque → preuve → commande/observation → limite`.
- Test maintenable lié à un comportement pertinent, si le dépôt fournit un point de contrôle adapté.
- Résultat réel, erreurs résiduelles et validations encore humaines.

## Garde-fous

- Ne pas forcer TDD pour une modification sans comportement exécutable ni prétendre qu’un test de compilation prouve l’usage.
- Ne pas demander une approbation pour chaque cas de test ordinaire ; demander un arbitrage lorsque le contrat public, les données d’essai ou la stratégie changent substantiellement.
- Pas de nouvelle bibliothèque, navigateur, mock server ou service payant/réseau sans nécessité, accord et vérification de compatibilité.
- Ne pas modifier l’attendu uniquement pour faire passer le test ; justifier le changement depuis la source de vérité.
- Les recettes de `upstream/` sont des références, non des règles absolues ; la procédure du dépôt et la sécurité des données priment.
