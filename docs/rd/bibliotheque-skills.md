# Bibliothèque permanente de skills — M.R.S.C.

**État au 13 octobre 2026.** Cette bibliothèque rend les méthodes utiles persistantes dans le dépôt, réutilisables par les agents compatibles et auditables dans l’historique Git. Elle ne constitue pas une installation globale de l’assistant et ne prétend pas couvrir toutes les tâches possibles.

## Où les trouver

- [`.agents/skills/`](../../.agents/skills/) : cartes partagées, portables entre agents. Chaque dossier possède un `SKILL.md` local en français ; certains contiennent aussi une référence amont licenciée, sa provenance et ses empreintes.
- [`.claude/skills/`](../../.claude/skills/) : points d’entrée ou références propres à Claude Code. Les références externes y sont épinglées et les règles M.R.S.C. priment.
- [`AGENTS.md`](../../AGENTS.md) : consigne permanente du dépôt. Il demande de commencer par le routeur, puis de ne charger que les cartes pertinentes.
- [Index des skills](../../.agents/skills/README.md) : besoins couverts, séquence de travail et navigation vers chaque carte.

Les skills sont des procédures de travail, pas des paquets exécutables, des capacités garanties, des qualifications ou des consignes supérieures à la demande de la personne, à `AGENTS.md` et aux règles de sécurité.

## Couverture

La bibliothèque combine les domaines M.R.S.C. déjà présents et des compétences générales pour les tâches qui leur manquaient :

| Type de tâche | Skills à combiner selon le besoin |
|---|---|
| Choisir une méthode, décomposer une demande | `orchestration-taches`, puis le plus petit ensemble métier utile |
| Recherche, vérification de faits et de sources | `recherche-sources`, `cartographie-connaissances` |
| Concept nouveau, pédagogie, jeu et récit | `conception-innovation`, `conception-pedagogique`, `conception-jeu` |
| Interface, image, mouvement et inclusion | `direction-artistique-motion`, `accessibilite-co-conception`, `localisation-culturelle` |
| Intégration, sécurité, génération et données applicatives | `integration-securite`, `analyse-donnees-reproductible` |
| Bug, tests et revue avant livraison | `debugging-methodique`, `strategie-tests`, `revue-contradictoire` |
| Documentation et continuité des décisions | `documentation-technique`, `evaluation-maintenance` |
| Ajout ou mise à jour d’une compétence d’agent | `curation-skills-securisee`, puis `documentation-technique` |

La liste détaillée est tenue dans l’index. Au démarrage, un agent ne doit pas ouvrir tous les skills : utiliser le routeur, puis en activer un à trois pertinents, davantage seulement si la portée le justifie.

## Références amont sélectionnées

Les contenus amont suivants sont conservés à une révision fixe, sous licence, à côté d’une entrée locale qui adapte les règles au dépôt :

- [`mattpocock/skills` — TDD](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336/skills/engineering/tdd), commit `49dd158d1076134a641b33efb035946536778336`, licence MIT. Seuls le skill et ses deux références Markdown utiles sont conservés sous [`strategie-tests/upstream/`](../../.agents/skills/strategie-tests/upstream/) ; l’adaptateur `agents/openai.yaml` n’est pas copié. L’entrée locale ne reprend pas l’exigence de demander confirmation pour chaque seam de test.
- [`addyosmani/agent-skills` — debugging and error recovery](https://github.com/addyosmani/agent-skills/tree/1be8e34187e34647bb83adc3a1323b26ae6f6abe/skills/debugging-and-error-recovery), commit `1be8e34187e34647bb83adc3a1323b26ae6f6abe`, licence MIT. Le seul skill Markdown est conservé sous [`debugging-methodique/upstream/`](../../.agents/skills/debugging-methodique/upstream/). L’entrée locale impose les commandes du dépôt et bloque l’exécution des exemples amont, dont certains présument npm.
- [`anthropics/skills` — `frontend-design`](../../.claude/skills/frontend-design/SOURCE.md), Apache-2.0, et [`LottieFiles/motion-design-skill`](../../.claude/skills/motion-design/SOURCE.md), MIT : imports visuel/mouvement précédemment audités. L’entrée locale de mouvement désactive l’application systématique de couches ambiantes et de recettes décoratives.

Chaque import dispose d’une provenance et d’un `SHA256SUMS`. Les sommes rendent détectable un changement des octets ; elles ne prouvent pas qu’un texte est sûr. Les skills sont des instructions que l’agent doit lire de manière critique.

## Découvertes utiles, sans import aveugle

La recherche a aussi examiné l’écosystème de skills d’ingénierie de [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills/tree/1be8e34187e34647bb83adc3a1323b26ae6f6abe) et [`mattpocock/skills`](https://github.com/mattpocock/skills/tree/49dd158d1076134a641b33efb035946536778336). Les techniques retenues dans les cartes locales sont : routage par intention plutôt que par outil, travail par petites tranches vérifiables, repro minimal et hypothèses falsifiables, tests sur contrats observables, relecture séparée contre la demande et les cas d’échec, contrôle de provenance et des transformations de données. Le pattern de revue contradictoire à contexte frais a été adapté seulement comme option pour les changements à fort risque : la méthode amont [`doubt-driven-development`](https://github.com/addyosmani/agent-skills/tree/1be8e34187e34647bb83adc3a1323b26ae6f6abe/skills/doubt-driven-development) exige des sous-agents et propose des CLIs inter-modèles, absents ou non autorisés dans de nombreux contextes ; ces appels obligatoires et répétés ne sont pas importés.

Les lots complets ne sont pas copiés. Certains candidats réclament des sous-agents ou outils CLI qui peuvent manquer, contiennent des commandes d’installation génériques inadaptées à la pile, imposent une confirmation à chaque étape ou ajoutent de nombreuses spécialisations et scripts hors besoin. En particulier, une revue contradictoire peut être faite par une seule session ; elle ne doit pas être présentée comme revue indépendante si aucun second contexte n’est disponible.

Les catalogues publics et le nombre de dépôts sont ouverts. Cette sélection est ciblée sur les tâches courantes du dépôt et sur les besoins exprimés, pas un recensement exhaustif d’Internet.

## Politique de maintenance

- Ajouter une carte lorsqu’un manque concret et récurrent est identifié, après comparaison à la bibliothèque existante.
- Préférer une courte méthode locale au téléchargement d’un bundle ; n’importer un amont que si son contenu complet, sa licence, ses scripts, ses dépendances et son utilité sont vérifiables.
- Épingler commit/version ; conserver la licence ; relire toutes les consignes ; ajouter provenance et empreintes ; ne lancer aucun script d’un skill externe sans demande et revue distinctes.
- Mettre à jour de manière contrôlée : comparer la nouvelle version à l’ancienne, revoir l’impact et les licences, puis valider les sommes. Pas de mise à jour automatique.
- Garder la bibliothèque accessible mais sélectionner seulement les skills appropriés à la demande. Retirer un skill uniquement après examen de ses usages et de sa provenance.
