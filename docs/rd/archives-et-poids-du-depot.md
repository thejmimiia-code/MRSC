# Archives des planches et poids du dépôt

**Date :** 19 octobre 2026.  
**Statut :** relevé technique par l’agent, pas une revue éditoriale des planches. Les chiffres viennent de commandes reproductibles, reproduites plus bas. Aucun jugement sur la qualité visuelle n’est porté ici.

**Principe : rien n’est perdu.** Les 507 fichiers d’origine sont conservés octet pour octet dans l’étiquette [`planches-statuts-animation-2026-10`](https://github.com/thejmimiia-code/MRSC/releases/tag/planches-statuts-animation-2026-10), avec un manifeste d’empreintes vérifiable, et les douze planches conservées dans l’arbre sont **sans perte** (écart pixel nul).

## Pourquoi

La fusion de la PR #85, le 19 octobre 2026, a fait entrer **505 PNG (1 290,9 Mo)** sous `docs/rd/statuts-animation/`. L’arbre de `main` est passé de **8,8 Mo hors PNG** à **1 299,7 Mo**, et le dépôt entier à **1 276 Mo** côté GitHub. Ces planches ne sont **pas publiées** : `docs/` est exclu de GitHub Pages et de Vercel. Le coût portait donc uniquement sur le clonage, la place disque et le temps de chaque session de travail.

## Ce qui a changé

- **Douze planches citées** dans [`plan-statuts-animation.md`](plan-statuts-animation.md) restent dans l’arbre, **converties en WebP sans perte** : **14,7 Mo** au total au lieu de **31,4 Mo**, pour une image **strictement identique** (écart pixel mesuré : `0`).
- **Les 493 autres planches** et les douze originaux PNG sont **archivés hors de l’arbre**, dans la version étiquetée [`planches-statuts-animation-2026-10`](https://github.com/thejmimiia-code/MRSC/releases/tag/planches-statuts-animation-2026-10), qui pointe sur l’état du dépôt **avant** ce retrait.
- `docs/rd/statuts-animation/` contient la [bible du film](statuts-animation/bible-fil-et-video-01.md), la référence `eva-reference.jpg`, les douze WebP sans perte et le manifeste `ARCHIVE-planches-2026-10.sha256`.
- `.gitignore` ignore les `*.png` de ce dossier, pour qu’une planche ne revienne pas par inadvertance.

## Fidélité des douze planches conservées

Deux encodages ont été essayés, mesurés, et un seul retenu.

| Encodage | Écart pixel (`compare -metric AE`) | Poids des 12 fichiers | Décision |
|---|---|---|---|
| WebP qualité 82 (avec perte) | 1 058 000 à 1 077 000 pixels modifiés par planche, sur 1 081 344 | 1,4 Mo | **écarté** : perte réelle |
| **WebP sans perte** (`webp:lossless=true`) | **0** | 14,7 Mo | **retenu** |
| PNG d’origine | référence | 31,4 Mo | archivé |

Vérification reproductible, pour chaque planche :

```sh
git show planches-statuts-animation-2026-10:docs/rd/statuts-animation/amblin-01-annees-80.png > /tmp/orig.png
compare -metric AE /tmp/orig.png docs/rd/statuts-animation/amblin-01-annees-80.webp null:   # affiche 0
```

## Chiffres mesurés

| Mesure | Avant | Après |
|---|---|---|
| Arbre de `main` | 1 299,7 Mo | **23,6 Mo** |
| dont `docs/rd/statuts-animation/` | 1 290,9 Mo (505 PNG) | 15,6 Mo (12 WebP sans perte, la bible, une référence, le manifeste) |
| Fichiers suivis | 853 | 363 |
| Taille du dépôt GitHub | 1 323 547 Ko | **inchangée** tant que l’historique n’est pas réécrit |

Commandes utilisées :

```sh
git ls-tree -rl HEAD | awk '/\.png$/{s+=$4} END{printf "%.1f Mo\n", s/1048576}'
du -sh docs/rd/statuts-animation
gh api repos/thejmimiia-code/MRSC --jq '.size'   # en kilo-octets
```

## Contrôle d’intégrité de l’archive

Le manifeste [`statuts-animation/ARCHIVE-planches-2026-10.sha256`](statuts-animation/ARCHIVE-planches-2026-10.sha256) contient l’empreinte SHA-256 des **507** fichiers d’origine (505 PNG, la bible, la référence). Il a été produit à partir des objets de l’étiquette et vérifié une fois de bout en bout.

```sh
mkdir -p /tmp/verif-archive
git archive planches-statuts-animation-2026-10 docs/rd/statuts-animation | tar -x -C /tmp/verif-archive
cd /tmp/verif-archive/docs/rd/statuts-animation
cp /chemin/vers/le/depot/docs/rd/statuts-animation/ARCHIVE-planches-2026-10.sha256 .
sha256sum -c ARCHIVE-planches-2026-10.sha256 --quiet   # aucun message = tout est conforme
```

Résultat obtenu le 19 octobre 2026 : **507 fichiers conformes, aucun écart**.

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

Procédure pour la personne qui administre le dépôt, **après avoir téléchargé l’archive ci-dessus et vérifié son manifeste** :

```sh
git clone --mirror https://github.com/thejmimiia-code/MRSC.git mrsc-mirror.git
cd mrsc-mirror.git
git filter-repo --force --invert-paths --path-glob 'docs/rd/statuts-animation/*.png'
git push --force origin main
git push origin --delete planches-statuts-animation-2026-10
```

Points d’attention :

- `git filter-repo` réécrit tous les commits concernés ; les anciens identifiants de commit disparaissent, les propositions de fusion déjà fusionnées gardent leur trace mais leurs diffs ne se rejouent plus ;
- l’étiquette d’archive est le dernier endroit où les planches sont accessibles : **la télécharger et vérifier le manifeste avant** toute réécriture ;
- prévenir les personnes qui auraient un clone, puisqu’elles devront le refaire ;
- vérifier ensuite `gh api repos/thejmimiia-code/MRSC --jq '.size'` et contacter le support GitHub seulement si la taille ne baisse pas après quelques jours.

## Règle pour la suite

Ne pas committer de nouvelles planches PNG dans le dépôt. Les déposer dans une version étiquetée (`archives/…`), publier leur manifeste d’empreintes, et ne garder dans l’arbre que les planches réellement citées, en WebP **sans perte**.

## Limites

- La conversion sans perte préserve les pixels, pas la compression d’origine : les fichiers `.webp` conservés ne sont pas octet pour octet les `.png` archivés, même si l’image est identique.
- Le compte de fichiers et le poids « après » sont ceux de l’arbre fusionné le 19 octobre 2026 ; ils sont à recalculer avec les commandes ci-dessus si l’arbre évolue.
- Les planches restent « à relire » : aucune n’est validée, et ce document ne dit rien de leur intérêt artistique.
