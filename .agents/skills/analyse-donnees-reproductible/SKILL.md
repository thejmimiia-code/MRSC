---
name: analyse-donnees-reproductible
description: Inspecte, transforme et représente des données en préservant provenance, unités, incertitudes, confidentialité et reproductibilité.
---
# Analyse de données reproductible

## Quand l’activer

Pour un CSV, JSON, tableur, dataset, export, graphique, indicateur, simulation ou calcul quantitatif ; également avant de connecter une nouvelle source de données à une interface.

## Entrées

- Question à laquelle les données doivent répondre et public du résultat.
- Source, date, licence, définition de chaque champ, unités, période et granularité.
- Volume, qualité, données personnelles/sensibles, schéma et changements connus.
- Scripts, bibliothèques et sorties attendues déjà présents dans le dépôt.

## Méthode

1. **Qualifier la source.** Repérer auteur/propriétaire, méthode de collecte, population, dates, licence et limites. Conserver les données d’origine en lecture seule ; travailler sur une copie identifiée.
2. **Examiner le schéma avant calcul.** Vérifier colonnes, types, encodage, séparateurs, unités, fuseau horaire, clés, doublons, valeurs manquantes et plages plausibles. Signaler les anomalies avant de les corriger.
3. **Définir les transformations.** Documenter filtre, normalisation, jointure, agrégation et traitement des valeurs manquantes. Rendre l’opération déterministe, relançable et séparée de l’original ; ne jamais imputer ou supprimer silencieusement.
4. **Choisir un calcul proportionné à la question.** Vérifier dénominateur, période, population, biais de sélection, échantillon, unités et incertitude. Distinguer corrélation, description, estimation et causalité ; ne pas conclure au-delà du plan de données.
5. **Construire une représentation honnête.** Afficher titre, unités, source, période, filtres et échelles ; garder axes, légende et points manquants lisibles. Ne pas tronquer ou sélectionner une échelle pour fabriquer un effet.
6. **Contrôler les sorties.** Utiliser des invariants, totaux, bornes, exemples manuels et/ou comparaison à une référence indépendante. Contrôler un échantillon après export et noter les arrondis.
7. **Rendre la reprise possible.** Enregistrer la provenance, version/date, script ou étapes de transformation, paramètres, checksums utiles et consignes de mise à jour. Fournir une variante agrégée/anonymisée si les données sources ne peuvent être partagées.

## Livrables

- Dictionnaire des champs et note de provenance/limites.
- Transformation rejouable, contrôles de qualité et sortie versionnée si pertinent.
- Graphique/tableau lisible avec unités, base de calcul, incertitudes et interprétation limitée.

## Garde-fous

- Ne pas envoyer de données privées à un service externe ni les déposer dans les logs, prompts publics ou fichiers versionnés sans autorisation.
- Ne pas confondre anonymisation, pseudonymisation et agrégation ; réduire la granularité et les champs personnels au strict nécessaire.
- Ne pas inventer de valeur manquante, de définition, de date ou de source. Marquer « inconnu » quand l’information manque.
- N’ajouter aucun paquet ni télécharger de dataset juste parce qu’un exemple le suggère ; vérifier licence, sécurité, version et taille avant tout ajout.
- Aucun résultat statistique n’est une preuve de causalité ou une recommandation experte sans méthode appropriée et relecture compétente.
