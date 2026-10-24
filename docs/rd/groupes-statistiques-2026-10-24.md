# Réunir deux groupes : retrouver les totaux avant de partager

## Besoin et choix

Complément du [lot moyenne/médiane](lot-statistiques-2026-10-24.md), identifié dans sa suite éditoriale, pas par une enquête d'usage. La fiche moyenne avertissait sur la taille des groupes sans expliquer comment réunir leurs résultats.

Trois formes considérées : une nouvelle fiche (risque de doublon), une formule seule (masque la raison du poids), un exercice de reconstruction des totaux dans la fiche existante (retenu). Hypothèse non éprouvée : refaire le partage à partir des totaux permet de comprendre pourquoi chaque moyenne doit compter selon son effectif. La durée indicative passe de 10 à 14 minutes, sans mesure humaine.

## Affirmations et source

- Pour des groupes disjoints, de moyennes exactes et portant sur la même mesure, la somme de chaque groupe est sa moyenne multipliée par son effectif ; les sommes et les effectifs s'additionnent. C'est une application de la définition de moyenne, vérifiée par calcul dans l'exemple original.
- Source technique consultée le 24 octobre 2026 : Python Software Foundation, documentation Python 3.14.0, [statistics, section fmean](https://github.com/python/cpython/blob/v3.14.0/Doc/library/statistics.rst). La section décrit l'association de poids aux valeurs ; elle ne démontre pas la qualité pédagogique de notre explication. Licence de reprise non vérifiée ; aucun texte ni exercice reproduit.
- Exemple fictif : 2 manches de moyenne exacte 3, 6 manches de moyenne exacte 7. Total 6 + 42 = 48 ; effectif 8 ; moyenne 6. La moyenne non pondérée des deux moyennes serait 5 et ne convient pas ici.
- Limites écrites dans la correction : moyennes arrondies → reconstruction approximative ; effectifs absents → moyenne globale indéterminable en général ; même effectif non nul → la moyenne des deux moyennes convient. Le calcul ne démontre aucune différence causale entre les groupes.

## Vérifications exécutées

- `python3 outils/test_exemples_statistiques.py` : **8 tests réussis**, incluant le cas pondéré, trois cas d'effectifs égaux et une mutation 6 → 5 dans la réponse écrite, détectée.
- `verifier-fiches-statistiques.cjs` : **288 configurations, aucun échec**, mêmes deux fiches, largeurs 320/390/768/1280, tailles 100/115/130 %, six présentations, contraste/espacement standard et renforcés, densité 2, aides et corrections ouvertes. [Rapport de cette passe](audit-groupes-statistiques-2026-10-24.json). Géométrie du contenu et présence du statut seulement, pas un audit d'accessibilité ou une mesure de compréhension.
- Génération, audit des prototypes, site statique, intégration, continuité R&D, brief prospectif, publication locale et reproductibilité : contrôles réussis. Les compteurs restent à 85 fiches et 59 prototypes. Le rapport historique du premier lot n'est pas écrasé.

## Relecture et décision encore à faire

Aucune relecture indépendante ni séance avec des personnes n'a été menée. Les nouvelles explications n'ont qu'une référence technique ; un recoupement pédagogique francophone reste nécessaire. Vérifier notamment si l'allongement de la fiche débutante crée une surcharge. Une tâche candidate, à faire approuver avant tout essai : expliquer pourquoi 5 ne représente pas les huit manches, puis comparer deux groupes d'effectifs égaux. Autoriser papier, oral, aides et arrêt ; ne pas collecter de données personnelles de performance.

Décision actuelle : conserver le statut prototype et ne pas créer une fiche supplémentaire. Si l'explication reste trop dense malgré les aides lors d'un essai approuvé, séparer l'activité d'approfondissement. La date et l'intervalle de revue de la fiche restent inchangés ; aucun statut humain n'est ajouté.
