# Journal de R&D et de passation entre agents

Ce journal conserve les décisions structurantes et les relais utiles, pas le détail de chaque commit. Utiliser le [gabarit d'initiative](gabarit-initiative.md) pour une décision nouvelle et le [portefeuille vivant](portefeuille.toml) pour son état courant. Une entrée doit rester datée, reliée à un identifiant d'initiative, préciser les preuves, la décision, les contrôles réellement exécutés et la suite. Ne pas y mettre de données personnelles ni recopier les réponses de personnes apprenantes.

## 2026-10-12 — Mise en place du dispositif de R&D multi-agent

- **Initiative :** `coordination-de-tous-les-agents`.
- **Décision :** utiliser `AGENTS.md` comme consigne commune, des cartes de skills sous `.agents/skills/`, le manuel [`rd-innovation-continue.md`](../rd-innovation-continue.md), le portefeuille TOML et ce journal comme sources de passation.
- **Surface publique :** ajouter une présentation du processus dans `transparence.html#rd-innovation`, accessible depuis `anglais-aventure.html` et `apprendre.html`; les consignes et skills détaillés restent lisibles dans le dépôt GitHub.
- **Automatisation :** ajouter un vérificateur hors ligne, l'appeler dans la CI, le déploiement et la veille hebdomadaire. La veille peut afficher les échéances et mettre à jour l'issue de suivi; elle ne consulte pas les sources externes et ne modifie ni n'approuve un contenu.
- **Essais d’usage :** préparer [`protocole-essais-usage.md`](protocole-essais-usage.md) avec tâches, consentement à adapter, notes minimales, arrêt et méthode d'analyse. C'est un protocole à faire relire, pas un test humain déjà exécuté.
- **Contrôles réellement exécutés localement :** compilation Python; vérificateur R&D et du protocole; génération-vérification du catalogue; vérificateur statique; vérificateur d'intégration; vérificateur de sécurité; parsing YAML des workflows et du formulaire; vérification HTTP des pages publiques modifiées; `git diff --check`.
- **Limites :** aucun test de l'exécution réelle des workflows GitHub n'a été effectué sur cette branche; aucune recherche automatique externe, relecture experte des contenus, validation exhaustive des droits ou essai d'usage avec des personnes n'est revendiqué.
- **Prochaine action :** faire relire le protocole de consentement et les tâches par les rôles compétents avant tout recrutement; après intégration dans `main`, examiner la première exécution planifiée et vérifier que le résumé et l'issue sont lisibles.
