# Archives des planches et poids du dépôt

**Date :** 19 octobre 2026.  
**Statut :** relevé technique par l’agent, pas une revue éditoriale des planches. Les chiffres viennent de commandes reproductibles, reproduites plus bas. Aucun jugement sur la qualité visuelle n’est porté ici.

## Pourquoi

La fusion de la PR #85, le 19 octobre 2026, a fait entrer **505 PNG (1 290,9 Mo)** sous `docs/rd/statuts-animation/`. L’arbre de `main` est passé de **8,8 Mo hors PNG** à **1 299,7 Mo**, et le dépôt entier à **1 276 Mo** côté GitHub. Ces planches ne sont **pas publiées** : `docs/` est exclu de GitHub Pages et de Vercel. Le coût portait donc uniquement sur le clonage, la place disque et le temps de chaque session de travail.

## Ce qui a changé

- **Douze planches citées** dans [`plan-statuts-animation.md`](plan-statuts-animation.md) restent dans l’arbre, **converties en WebP qualité 82** : **1,42 Mo** au total au lieu de **31,4 Mo**.
- **Les 493 autres planches** et les douze originaux PNG sont **archivés hors de l’arbre**, dans la version étiquetée [`planches-statuts-animation-2026-10`](https://github.com/thejmimiia-code/MRSC/releases/tag/planches-statuts-animation-2026-10), qui pointe sur l’état du dépôt **avant** ce retrait.
- `docs/rd/statuts-animation/` ne contient plus que la [bible du film](statuts-animation/bible-fil-et-video-01.md), la référence `eva-reference.jpg` et les douze WebP.
- `.gitignore` ignore désormais les `*.png` de ce dossier, pour qu’une planche ne revienne pas par inadvertance.

## Chiffres mesurés

| Mesure | Avant | Après |
|---|---|---|
| Arbre de `main` | 1 299,7 Mo | **10,3 Mo** |
| dont `docs/rd/statuts-animation/` | 1 290,9 Mo (505 PNG) | 1,6 Mo (12 WebP, la bible et une référence) |
| Fichiers suivis | 853 | 361 |
| Taille du dépôt GitHub | 1 323 547 Ko | **1,26 Go inchangé** tant que l’historique n’est pas réécrit |

Commandes utilisées :

```sh
git ls-tree -rl HEAD | awk '/\.png$/{s+=$4} END{printf "%.1f Mo\n", s/1048576}'
du -sh docs/rd/statuts-animation
gh api repos/thejmimiia-code/MRSC --jq '.size'   # en kilo-octets
```

## Récupérer les originaux

Avec un clone du dépôt :

```sh
git archive --format=zip --output=planches-statuts-animation.zip \
  planches-statuts-animation-2026-10 docs/rd/statuts-animation
```

Sans clone, l’étiquette se parcourt dans l’interface :
`https://github.com/thejmimiia-code/MRSC/tree/planches-statuts-animation-2026-10/docs/rd/statuts-animation`
et se télécharge entière via « Download ZIP » de la version publiée (le fichier contient tout le dépôt de l’époque, planches comprises).

## Ce qui reste à faire : réécrire l’historique

Retirer les fichiers de l’arbre **ne réduit pas le clonage** : les 1,29 Go restent dans l’historique, accessibles par l’étiquette. Seule une réécriture d’historique les enlève. Elle n’a **pas** été faite ici : elle exige un `--force` sur `main`, opération hors du périmètre de la session d’agent et destructive pour les clones existants.

Procédure pour la personne qui administre le dépôt, **après avoir téléchargé l’archive ci-dessus** :

```sh
git clone --mirror https://github.com/thejmimiia-code/MRSC.git mrsc-mirror.git
cd mrsc-mirror.git
git filter-repo --force --invert-paths --path-glob 'docs/rd/statuts-animation/*.png'
git push --force origin main
git push origin --delete planches-statuts-animation-2026-10
```

Points d’attention :

- `git filter-repo` réécrit tous les commits concernés ; les anciens identifiants de commit disparaissent, les propositions de fusion déjà fusionnées gardent leur trace mais leurs diffs ne se rejouent plus ;
- l’étiquette d’archive est le dernier endroit où les planches sont accessibles : **la télécharger avant** toute réécriture ;
- prévenir les personnes qui auraient un clone, puisqu’elles devront le refaire ;
- vérifier ensuite `gh api repos/thejmimiia-code/MRSC --jq '.size'` et contacter le support GitHub seulement si la taille ne baisse pas après quelques jours.

## Règle pour la suite

Ne pas committer de nouvelles planches PNG dans le dépôt. Les déposer dans une version étiquetée (`archives/…`) et ne garder dans l’arbre que les planches réellement citées, en WebP compact.

## Limites

- La conversion WebP est automatique (qualité 82) : **la fidélité visuelle des douze WebP n’a pas été contrôlée à l’œil** ; les originaux restent dans l’archive.
- Le compte de fichiers et le poids « après » ne sont exacts qu’une fois la fusion effectuée ; ils sont à recalculer avec les commandes ci-dessus.
- Les planches restent « à relire » : aucune n’est validée, et ce document ne dit rien de leur intérêt artistique.
