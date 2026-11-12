# Carte des lacunes du catalogue d'apprentissage

**Nature :** carte de travail générée depuis `docs/apprentissage/referentiel.toml`, `docs/apprentissage/catalogue.toml` et `docs/rd/portefeuille.toml`. Elle ne recherche rien, ne relit rien et ne valide rien. Une case vide est une case à travailler, pas un défaut établi.

**Date de référence :** celle de la revue de portefeuille, `2026-10-20`.

## 1. Où en est la carte

| Mesure | Valeur |
| --- | ---: |
| Sujets du référentiel | 106 |
| dont `actif` | 8 |
| dont `partiel` | 92 |
| dont `a-creer` | 3 |
| dont `revue-experte` | 3 |
| Domaines | 15 |
| Fiches publiées | 108 |
| dont prototypes à relire | 82 |
| Sujets sans aucune fiche | 6 |
| Sujets ouverts par une carte de sujet | 8 |
| Lesquels | `ecoute-prononciation`, `revenus-salaire-impots`, `securite-electricite`, `securite-sciences`, `droits-travail`, `systemes-embarques`, `premiers-secours`, `activite-corps-securite` |

## 2. Répartition par domaine

| Domaine | Sujets | actif | partiel | à créer | revue experte | sans fiche |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Français, lecture, écriture et communication | 6 | 2 | 4 | 0 | 0 | 0 |
| Langues étrangères et interculturel | 4 | 0 | 4 | 0 | 0 | 0 |
| Mathématiques, mesures et données | 11 | 5 | 6 | 0 | 0 | 0 |
| Budget, économie, consommation et travail | 5 | 0 | 4 | 1 | 0 | 1 |
| Sciences, technologie et environnement | 10 | 1 | 7 | 1 | 1 | 2 |
| Géographie, territoire et espace | 5 | 0 | 5 | 0 | 0 | 0 |
| Histoire, chronologie et mémoire | 4 | 0 | 4 | 0 | 0 | 0 |
| Citoyenneté, médias et information | 6 | 0 | 6 | 0 | 0 | 0 |
| Démarches, droits, sécurité et vie professionnelle | 5 | 0 | 4 | 1 | 0 | 1 |
| Numérique, données, cybersécurité et intelligence artificielle | 10 | 0 | 10 | 0 | 0 | 0 |
| Informatique, algorithmique et langages de programmation | 10 | 0 | 10 | 0 | 0 | 0 |
| Arts, musique, création et culture | 4 | 0 | 4 | 0 | 0 | 0 |
| Santé, alimentation, corps et sécurité | 7 | 0 | 5 | 0 | 2 | 2 |
| Apprendre à apprendre, autonomie et relations | 4 | 0 | 4 | 0 | 0 | 0 |
| Études supérieures, spécialités et recherche — post-bac au doctorat | 15 | 0 | 15 | 0 | 0 | 0 |

## 3. Les 6 sujets sans aucune fiche

Ce sont les seuls sujets dont l'absence est déclarée dans le référentiel. Les 92 sujets `partiel` ont déjà au moins une fiche : leur manque est à qualifier sujet par sujet, il n'est pas listé ici.

| Domaine | Sujet | Statut | Exigence de preuve avant publication | Travail ouvert |
| --- | --- | --- | --- | --- |
| Budget, économie, consommation et travail | Revenus, fiche de paie, prélèvements et impôts | `a-creer` | Relecture par une personne compétente en argent, budget et finances, puis sources primaires datées | [carte de sujet](sujet-revenus-salaire-impots.md) |
| Sciences, technologie et environnement | Sécurité électrique, protections et limites des interventions | `revue-experte` | Relecture par une personne experte du sujet, puis sources primaires datées | [carte de sujet](sujet-securite-electricite.md) |
| Sciences, technologie et environnement | Risques, consignes et usages sûrs des outils et produits | `a-creer` | Sources primaires datées, relecture éditoriale, puis contrôle d'accessibilité | [carte de sujet](sujet-securite-sciences.md) |
| Démarches, droits, sécurité et vie professionnelle | Droits au travail, contrats, sécurité et interlocuteurs | `a-creer` | Relecture par une personne compétente en droit, démarches et travail, puis sources primaires datées | [carte de sujet](sujet-droits-travail.md) |
| Santé, alimentation, corps et sécurité | Premiers secours et conduites à tenir | `revue-experte` | Relecture par une personne experte du sujet, puis sources primaires datées | [carte de sujet](sujet-premiers-secours.md) |
| Santé, alimentation, corps et sécurité | Activité physique, repos, mobilité et sécurité | `revue-experte` | Relecture par une personne experte du sujet, puis sources primaires datées | [carte de sujet](sujet-activite-corps-securite.md) |

## 4. Ce que cette carte ne dit pas

- Elle ne dit pas qu'un sujet absent du référentiel n'existe pas : le référentiel est une carte de travail, pas un inventaire du savoir.
- Elle ne dit rien de la qualité des 108 fiches publiées ni de l'exactitude de leur contenu.
- Elle ne fournit aucune source : chaque sujet ouvert doit encore être documenté auprès de sources primaires, avec leur date, leur périmètre et leurs droits.
- Elle ne hiérarchise pas les domaines : un domaine à onze sujets à créer n'est pas « plus important » qu'un domaine à un sujet.
- Elle applique l'exigence de preuve du domaine déclaré : un sujet de santé rangé sous « études supérieures » (ISCED-F 09) reçoit l'exigence générale. Ce classement est à corriger au cas par cas, pas à lire comme une règle de risque.

## 5. Comment avancer

1. Choisir un sujet de la section 3 et écrire sa carte de sujet (identité, portée, relations, preuve, forme d'apprentissage, statut, entretien) selon `docs/rd-innovation-continue.md`.
2. Rechercher des sources primaires datées ; si aucune n'est accessible, laisser le sujet ouvert plutôt que de le remplir par une affirmation non traçable.
3. Fabriquer une fiche seulement après la relecture exigée dans la dernière colonne ; conserver le statut « Prototype à relire » tant que la preuve humaine manque.
4. Régénérer cette carte après toute modification du référentiel et vérifier qu'aucun sujet n'a disparu par accident.

Régénérer avec `python3 outils/construire-carte-lacunes.py` ; vérifier avec `--verifier`.
