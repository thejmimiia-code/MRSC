# Bibliothèque de skills R&D M.R.S.C.

Ces cartes sont des méthodes réutilisables, conservées dans le dépôt et partageables entre agents. Elles ne sont ni des certifications ni des garanties de capacité ou d'expertise. Chaque agent doit signaler les relectures humaines encore nécessaires.

**Pour chaque nouvelle tâche :** commencer par [`orchestration-taches`](orchestration-taches/SKILL.md), puis ouvrir uniquement une à trois cartes de domaine adaptées. Ne pas charger toute la bibliothèque par défaut ; la sélection fait partie de la méthode.

## Routage général et ingénierie

| Besoin | Skill |
|---|---|
| Cadrer la demande, choisir les compétences et ordonner les étapes | [`orchestration-taches`](orchestration-taches/SKILL.md) |
| Trouver la cause d'une erreur ou d'une régression | [`debugging-methodique`](debugging-methodique/SKILL.md) |
| Choisir des tests utiles, reproductibles et proportionnés au risque | [`strategie-tests`](strategie-tests/SKILL.md) |
| Rechercher les écarts d'un diff, y compris les contre-exemples | [`revue-contradictoire`](revue-contradictoire/SKILL.md) |
| Analyser ou transformer des données sans perdre leur provenance | [`analyse-donnees-reproductible`](analyse-donnees-reproductible/SKILL.md) |
| Rédiger/mettre à jour documentation et procédures depuis les sources réelles | [`documentation-technique`](documentation-technique/SKILL.md) |
| Découvrir, importer ou actualiser un skill en contrôlant ses risques | [`curation-skills-securisee`](curation-skills-securisee/SKILL.md) |

## Connaissances, apprentissage et création

| Besoin | Skill |
|---|---|
| Repérer domaines, lacunes, prérequis et liens interdisciplinaires | [`cartographie-connaissances`](cartographie-connaissances/SKILL.md) |
| Vérifier faits, études, règles, sources, licences et incertitudes | [`recherche-sources`](recherche-sources/SKILL.md) |
| Transformer une demande en concept original testable | [`conception-innovation`](conception-innovation/SKILL.md) |
| Concevoir objectif, leçon, aides, pratique et correction | [`conception-pedagogique`](conception-pedagogique/SKILL.md) |
| Adapter langues, régions, unités, cultures et règles locales sans les universaliser | [`localisation-culturelle`](localisation-culturelle/SKILL.md) |
| Concevoir monde, mission, dialogue, mécanique et narration | [`conception-jeu`](conception-jeu/SKILL.md) |
| Concevoir une direction artistique distinctive et des animations web accessibles | [`direction-artistique-motion`](direction-artistique-motion/SKILL.md) |
| Évaluer navigation et contenus avec l'accessibilité en tête | [`accessibilite-co-conception`](accessibilite-co-conception/SKILL.md) |
| Interpréter les essais, itérer et entretenir les sources | [`evaluation-maintenance`](evaluation-maintenance/SKILL.md) |
| Intégrer au dépôt en protégeant sécurité, vie privée et solutions de repli | [`integration-securite`](integration-securite/SKILL.md) |

## Références Claude Code

- Le point d’entrée de méthode visuelle du projet est [`direction-artistique-motion`](../../.claude/skills/direction-artistique-motion/SKILL.md), qui renvoie vers la carte partagée.
- Les références amont [`frontend-design`](../../.claude/skills/frontend-design/) et [`motion-design`](../../.claude/skills/motion-design/) sont optionnelles et auditées. Les règles M.R.S.C. priment ; voir les sources, licences et sommes dans chaque dossier.

Les inspirations externes, commits retenus, exclusions et règles de mise à jour sont consignés dans [`docs/rd/bibliotheque-skills.md`](../../docs/rd/bibliotheque-skills.md).

**Séquence minimale d'une nouvelle piste :** cadrer → cartographier/rechercher → conceptualiser → concevoir le format → intégrer → rendre accessible → évaluer/entretenir. Toutes les étapes ne demandent pas forcément une carte séparée, mais chaque étape applicable doit laisser un résultat ou une limite explicite.

Lire aussi [`AGENTS.md`](../../AGENTS.md), le [manuel de R&D continue](../../docs/rd-innovation-continue.md), le [portefeuille](../../docs/rd/portefeuille.toml) et le [journal des passations](../../docs/rd/journal.md). L'index est un routeur, pas une promesse de couverture de tous les métiers ou de tous les skills publics.
