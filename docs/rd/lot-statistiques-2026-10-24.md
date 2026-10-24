# R&D — Résumer des chiffres sans effacer leurs différences

**24 octobre 2026 · Prototype à relire, aucun essai humain réalisé.**

## Besoin et périmètre

Le sujet `tableaux-graphiques` reste partiel. Le catalogue explique déjà la moyenne, les graduations et la lecture d'un tableau ; il ne propose pas de fiche dédiée à la médiane. Cette absence est un constat du catalogue, pas une difficulté observée chez des visiteurs.

Question : comment comparer deux résumés numériques sans présenter l'un comme « le vrai chiffre » ? Objectif observable : calculer moyenne et médiane sur une petite série puis dire quelle information chaque résultat conserve. Prérequis : addition, division, classement numérique. Langue française ; aucune règle juridique locale n'est enseignée.

### Lot livré

- Nouvelle fiche `maths-moyenne-mediane` : tri, répétitions conservées, effectifs impair/pair, exemple commenté, trois exercices facultatifs, corrections et contre-exemples. Les valeurs sont des durées fictives, pas des données recueillies.
- Fiche `maths-moyenne` enrichie : un zéro observé compte dans l'effectif ; une valeur absente ne devient pas automatiquement un zéro. La moyenne de deux valeurs renseignées n'est pas annoncée comme celle des trois valeurs attendues.
- Le sujet reste **partiel** et les deux fiches **Prototype à relire**. Aucune validation humaine n'est ajoutée au registre.

La nouvelle fiche ne double pas celle sur la moyenne : elle introduit un classement et une position centrale, puis compare leurs effets à ceux d'un partage égal. L'exercice sur l'absence enrichit l'existant plutôt que de créer une deuxième fiche sur le même calcul.

## Recherche et preuves

Source réellement ouverte via l'API GitHub le 24 octobre 2026 : **Python Software Foundation, documentation Python 3.14.0, `statistics`, sections `mean` et `median`** :
https://github.com/python/cpython/blob/v3.14.0/Doc/library/statistics.rst

| Affirmation | Appui lu | Portée et limite |
| --- | --- | --- |
| Moyenne = somme / effectif | `mean` | Définition arithmétique, pas une règle de décision personnelle. |
| La moyenne peut être déplacée par une valeur éloignée | Note de `mean` | Illustré par deux séries originales ; pas d'inférence sur une population réelle. |
| Médiane impaire : valeur du milieu après classement | `median` | Séries numériques finies ; répétitions conservées. |
| Médiane paire : moyenne des deux centrales | `median` | Convention explicitée ; les autres conventions ne sont pas enseignées ici. |
| Zéro et donnée absente produisent des calculs différents | Application de somme/effectif aux exemples originaux | On n'impute aucune valeur ; ce lot n'enseigne pas les méthodes statistiques de traitement des données manquantes. |

La documentation est une référence technique précise, **pas une étude pédagogique**. Le calcul direct avec des fractions et la bibliothèque `statistics` recoupe les exemples, mais ne constitue pas une seconde source documentaire indépendante. Une référence pédagogique francophone et une relecture mathématique restent à apporter. Droits de reprise non vérifiés ; aucun texte, exercice ni visuel de la documentation n'est reproduit.

## Choix de conception

Trois options considérées :

1. Un graphique interactif : rejeté pour ce lot, car l'interaction ajouterait une difficulté sans être nécessaire au calcul.
2. Un long cours regroupant tous les indicateurs : rejeté, car moyenne pondérée, dispersion et échantillonnage exigent d'autres objectifs.
3. Une fiche autonome avec une seule valeur modifiée entre deux séries : retenue, pour rendre visible ce qui change dans le total et ce qui reste au milieu.

Hypothèse à éprouver : comparer les séries A et B aide à distinguer somme et position. Aucune amélioration de compréhension n'est revendiquée. Les aides et corrections restent facultatives et accessibles sans compte ni script tiers. Pas de photographie décorative ni de nouveau graphique à interpréter.

## Contrôle des exemples

`python3 outils/test_exemples_statistiques.py` lit le catalogue et contrôle des passages chiffrés précis : exemple initial (7 et 4), exercice A (4 et 3), B (8 et 3), C (médiane 5), série paire expliquée (médiane 6), et distinction zéro/absence (4 sur trois valeurs, 6 sur deux valeurs renseignées). Il vérifie aussi la conservation des doublons, l'invariance au réordonnement, la translation et le refus d'une série vide dans la fonction de référence.

Deux mutations en mémoire (moyenne 4 remplacée par 5, médiane 5 par 8) sont également détectées.

Ces tests ne comprennent pas tout le texte : modifier un autre passage peut leur échapper. Ils ne prouvent ni la bonne analogie ni la compréhension. La CI exécute ce contrôle en complément des contrôles de génération, sources déclarées et statut.

## Relecture et essai à préparer

Avant toute séance, faire approuver la tâche et le consentement selon le protocole d'essais du dépôt. Ne pas collecter de notes scolaires, de revenus ni de récits personnels.

- Relecture mathématique : conventions de médiane, cas pair, doublons, limite « au moins la moitié » et interprétation d'une donnée absente.
- Relecture pédagogique : vérifier que la distinction partage/position est compréhensible et que les exemples ne supposent pas de pratique de Python.
- Tâche candidate : demander de commenter les deux séries A/B, puis une série différente. Autoriser papier, oral, aide et arrêt sans justification.
- Observer les erreurs de procédure (tri absent, doublon retiré, extrêmes pris au lieu du centre, zéro inventé), sans attribuer un déficit à la personne.
- Décision : si les aides ne permettent pas d'expliquer la distinction, raccourcir ou découper la fiche avant d'étendre le lot. Une réponse exacte isolée ne vaut pas maîtrise.

## Suite

Priorité suivante : faire relire ce lot et les prototypes déjà en attente, puis travailler la comparaison de groupes de tailles différentes (moyenne pondérée), sans dupliquer la présente fiche. Ne pas ouvrir de contenu de santé, de droit ou de finances pour remplir une case sans source adaptée et personne compétente. Revue éditoriale de ce prototype prévue sous 180 jours, ou plus tôt en cas de retour signalant une erreur.

## Limite des relevés historiques

L'ajout d'une page ne crée pas une mesure d'accessibilité. Les anciens relevés axe (99 pages / 198 exécutions, au 20 octobre) et l'inventaire de couleurs restent datés ; leurs contrôles ne sont plus recalculés comme s'ils couvraient automatiquement la nouvelle fiche. Les compteurs du catalogue et les résultats des nouvelles passes sont distingués de ces archives.

## Vérification de rendu du lot

`verifier-fiches-statistiques.cjs` : **288 relevés, 0 échec**, sur deux fiches,
320/390/768/1280 px, texte 100/115/130 %, six présentations, avec ou sans contraste
et espacement renforcés. Aides/corrections ouvertes, densité 2. Périmètre : sortie
horizontale des éléments du contenu, rognage horizontal des boîtes et présence
du statut. Capture de la nouvelle fiche relue à 390 px / 130 %.
Le [relevé](audit-fiches-statistiques-2026-10-24.json) ne mesure ni lecture réelle,
ni ordre au lecteur d'écran, ni conformité WCAG. Le script est intégré à la CI.

Une seconde garde a été rectifiée : le test de reproductibilité refusait une date
éditoriale égale au jour courant, même quand une fiche venait réellement d'être
révisée. Il compare maintenant la date à la source TOML ; les passes sous horloge
à +37/+400 jours et la mutation d'un générateur dépendant du jour sont conservées.
