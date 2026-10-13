---
name: motion-design
description: >
  Référence R&D pour concevoir ou relire une animation web ou micro-interaction utile au M.R.S.C.
  À utiliser avec le cadre local d’art direction et d’accessibilité ; les recettes amont restent
  des heuristiques facultatives, jamais des obligations.
---

# Motion design — entrée locale M.R.S.C.

Avant toute proposition, suis le cadre propre au site dans [`direction-artistique-motion`](../direction-artistique-motion/SKILL.md), sa [carte partagée](../../../.agents/skills/direction-artistique-motion/SKILL.md), `AGENTS.md` et les sources de vérité de la page touchée.

Le contenu amont non modifié est conservé dans [`UPSTREAM-SKILL.md`](UPSTREAM-SKILL.md), avec ses fiches `director/`, `patterns/` et `reference/`. Consulte uniquement les passages pertinents comme une boîte à idées ; les durées, budgets de performance, catégories et recettes ne sont ni des normes ni des validations d’accessibilité.

## Garde-fous M.R.S.C.

- Le mouvement doit expliquer un état, répondre à une action ou aider à suivre une relation. Il n’est pas obligatoire pour rendre une interface vivante.
- Choisis l’effet le plus simple qui remplit cet objectif. N’ajoute **pas** automatiquement les trois couches « primaire, secondaire, ambiante », de parallaxe, d’animation au chargement, de boucle, de particules ou de séquences décalées recommandées dans certaines recettes amont.
- Respecte `prefers-reduced-motion` avec un état statique équivalent ; préserve clavier, focus, texte, contrôle utilisateur et contenu. Évite les effets vestibulaires et tout mouvement qui masque, retarde ou déplace l’information.
- Reste dans la pile du site (HTML/CSS/JavaScript) et ses dépendances existantes. N’ajoute pas de bibliothèque, CDN, ressource distante, police, script ou média pour appliquer une recette de ce skill.
- Une même action doit rester cohérente et réversible. Vérifie le résultat aux tailles mobile et bureau ; distingue les tests automatisés de la revue visuelle humaine et des essais utilisateurs.

En cas de conflit, les règles M.R.S.C. priment sur le contenu amont. La [provenance, les licences et l’audit](SOURCE.md) décrivent exactement ce qui est conservé.
