# Archives des planches et poids du dépôt

**Date :** 19 octobre 2026.  
**Statut :** relevé technique par l’agent, pas une revue éditoriale des planches. Les chiffres viennent de commandes reproductibles, reproduites plus bas. Aucun jugement sur la qualité visuelle n’est porté ici.

**Principe : rien n’est perdu.** Les 507 fichiers d’origine sont conservés octet pour octet dans l’étiquette [`planches-statuts-animation-2026-10`](https://github.com/thejmimiia-code/MRSC/releases/tag/planches-statuts-animation-2026-10), avec une sauvegarde du manifeste historique hors dépôt, et les douze planches conservées dans l’arbre sont **sans perte** (écart pixel nul).

## Pourquoi

La fusion de la PR #85, le 19 octobre 2026, a fait entrer **505 PNG (1 290,9 Mo)** sous `docs/rd/statuts-animation/`. L’arbre de `main` est passé de **8,8 Mo hors PNG** à **1 299,7 Mo**, et le dépôt entier à **1 276 Mo** côté GitHub. Ces planches ne sont **pas publiées** : `docs/` est exclu de GitHub Pages et de Vercel. Le coût portait donc uniquement sur le clonage, la place disque et le temps de chaque session de travail.

## Ce qui a changé

- **Douze planches citées** dans [`plan-statuts-animation.md`](plan-statuts-animation.md) restent dans l’arbre, **converties en WebP sans perte** : **14,7 Mo** au total au lieu de **31,4 Mo**, pour une image **strictement identique** (écart pixel mesuré : `0`).
- **Les 493 autres planches** et les douze originaux PNG sont **archivés hors de l’arbre**, dans la version étiquetée [`planches-statuts-animation-2026-10`](https://github.com/thejmimiia-code/MRSC/releases/tag/planches-statuts-animation-2026-10), qui pointe sur l’état du dépôt **avant** ce retrait.
- `docs/rd/statuts-animation/` contient la [bible du film](statuts-animation/bible-fil-et-video-01.md), les douze WebP sans perte et le manifeste `ARCHIVE-film-associatif.sha256`.
- `.gitignore` ignore les `*.png` de ce dossier, pour qu’une planche ne revienne pas par inadvertance.
- [`outils/verifier-planches-statuts.py`](../outils/verifier-planches-statuts.py) contrôle les liens, l’absence de PNG suivi et le manifeste ; il tourne dans la CI à chaque proposition.

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
| Fichiers suivis | 853 | 365 (au 19 octobre 2026) |
| Taille du dépôt GitHub | 1 323 547 Ko | **inchangée** tant que l’historique n’est pas réécrit |

Commandes utilisées :

```sh
git ls-tree -rl HEAD | awk '/\.png$/{s+=$4} END{printf "%.1f Mo\n", s/1048576}'
du -sh docs/rd/statuts-animation
gh api repos/thejmimiia-code/MRSC --jq '.size'   # en kilo-octets
```

## Contrôle d’intégrité de l’archive

Le manifeste [`statuts-animation/ARCHIVE-film-associatif.sha256`](statuts-animation/ARCHIVE-film-associatif.sha256) ne contient désormais que **343 empreintes** du périmètre associatif. Les 164 entrées de création du personnage ont été retirées le 25 octobre 2026. Les empreintes restantes sont inchangées ; le manifeste intégral de 507 fichiers reste sauvegardé hors dépôt. La vérification complète réalisée le 19 octobre est une preuve historique, pas un contrôle du périmètre actuel.

```sh
mkdir -p /tmp/verif-archive
git archive planches-statuts-animation-2026-10 docs/rd/statuts-animation | tar -x -C /tmp/verif-archive
cd /tmp/verif-archive/docs/rd/statuts-animation
cp /chemin/vers/le/depot/docs/rd/statuts-animation/ARCHIVE-film-associatif.sha256 .
sha256sum -c ARCHIVE-film-associatif.sha256 --quiet   # vérifie les 343 entrées du sous-ensemble associatif
```

Résultat obtenu le 19 octobre 2026 : **507 fichiers conformes, aucun écart**.

Depuis le 29 octobre 2026, `outils/verifier-planches-statuts.py --empreintes DOSSIER` fait cette comparaison sans passer par `sha256sum`, et compte séparément ce qu'il a réellement vu :

```sh
python3 outils/verifier-planches-statuts.py --empreintes /tmp/verif-archive/docs/rd/statuts-animation
# OK — archive vérifiée : N empreinte(s) conforme(s), M fichier(s) absent(s), aucun écart.
```

Sans l'option, le contrôle ne vérifie **que la forme** du manifeste — 343 lignes bien formées, noms uniques, nombre attendu — et le dit désormais explicitement, au lieu d'annoncer « conforme ». La distinction compte : comparer les fichiers de l'arbre au manifeste produirait de faux écarts, parce que l'archive est figée et que les documents vivent. Mesuré le 29 octobre 2026 : la [bible du film](statuts-animation/bible-fil-et-video-01.md) présente dans l'arbre a pour empreinte `e6c9d68c…`, alors que le manifeste attend `6f3dcb4e…`. Cet écart est cohérent avec une archive figée et un document qui a évolué depuis ; il n'a **pas** été tranché ici (l'étiquette `planches-statuts-animation-2026-10` n'existe pas dans le clone de travail utilisé), et il ne doit pas être lu comme une corruption.

Le même outil contrôle les **liens d'image de tous les documents `docs/rd/*.md`** : 205 liens recensés au 19 octobre 2026, dont 193 vers des planches archivées (la [bible du film](statuts-animation/bible-fil-et-video-01.md)) et 12 vers les planches conservées. Un lien vers un fichier ni présent ni archivé fait échouer le contrôle, ce qui interdit qu'un retrait casse silencieusement une référence.

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

Retirer les fichiers de l’arbre **ne réduit pas le clonage** : les 1,29 Go restent dans l’historique, accessibles par l’étiquette. Seule une réécriture d’historique les enlève. Elle n’a **pas** été faite, et la mesure du 20 octobre 2026 explique pourquoi.

## Réécriture d’historique : mesurée, non faite

Mesures faites sur un clone miroir complet du dépôt (`git clone --mirror`, 1,27 Gio, 394 commits, **506 objets PNG dont 1 286 Mo**), avec `git-filter-repo` 2.47.0. Les trois essais ci-dessous sont reproductibles ; l’arbre de `main` en sort **identique bit à bit** (`82835438df49031c6003a465a339a486274ce380`) dans les deux premiers cas.

| Scénario | Taille après | Arbre de `main` | Archive |
|---|---|---|---|
| Référence | 1,27 Gio | intact | 505 planches + 2 fichiers |
| A — purger `main` seule, étiquette gardée | **1,27 Gio** | identique | intacte |
| B — purger toutes les références | **22 Mio** | identique | **505 planches effacées** |
| C — même chose côté GitHub | inchangée | identique | effacée |

- **A ne sert à rien** : l’étiquette référence les mêmes objets, donc les 1,29 Go restent dans le dépôt. Le gain est nul, la fragilité non.
- **B fait gagner 1,25 Gio**, mais la réécriture retire aussi les planches de l’étiquette, qui ne garde plus que les trois icônes du site. Autrement dit : le gain se paie exactement par la perte que tout ce dossier cherchait à éviter. `git filter-repo` peut se limiter à `main` (`--refs main`, c’est le scénario A), mais l’étiquette garde alors les mêmes objets et le gain est nul ; dès qu’on lève la limite, l’étiquette est réécrite comme le reste.
- **C explique le reste** : sur GitHub, chaque proposition de fusion fusionnée depuis la #85 garde une référence `refs/pull/<n>/head` qui atteint encore les 506 objets PNG, et ces références **ne se réécrivent pas par un `push --force`**. Tant qu’elles existent, la taille annoncée par GitHub ne baisse pas, même après une `main` purgée et une étiquette supprimée. Seul un passage du support GitHub (ramassage des objets inaccessibles) changerait le chiffre.

**Décision :** la réécriture n’est pas lancée. Elle ne rendrait pas le dépôt plus léger côté GitHub avant une intervention du support, et elle détruirait l’unique copie des 505 planches.

## Si la réécriture est décidée quand même

Elle reste possible, mais dans cet ordre, et **aucune étape ne se saute** :

```sh
# 1. Copier l’archive hors de GitHub et noter son empreinte (1,3 Go).
git archive --format=tar planches-statuts-animation-2026-10 -o planches-statuts-animation-2026-10.tar
sha256sum planches-statuts-animation-2026-10.tar > planches-statuts-animation-2026-10.tar.sha256
# 2. Stocker ce fichier ailleurs, puis le RELIRE et vérifier son empreinte :
sha256sum -c planches-statuts-animation-2026-10.tar.sha256
# 3. Seulement alors, réécrire et pousser :
git clone --mirror https://github.com/thejmimiia-code/MRSC.git mrsc-mirror.git
cd mrsc-mirror.git
git filter-repo --force --invert-paths --path-glob 'docs/rd/statuts-animation/*.png'
git push --force origin main
git push origin --delete planches-statuts-animation-2026-10
```

Points d’attention :

- `git filter-repo` réécrit tous les commits concernés ; les anciens identifiants de commit disparaissent, les propositions de fusion déjà fusionnées gardent leur trace mais leurs diffs ne se rejouent plus ;
- l’étiquette d’archive est **la seule copie** des planches : l’étape 2 est ce qui empêche la perte, pas une formalité ;
- la taille GitHub ne baissera probablement qu’après un ticket au support pour les références de propositions de fusion (voir C) ;
- prévenir les personnes qui auraient un clone, puisqu’elles devront le refaire ;
- vérifier ensuite `gh api repos/thejmimiia-code/MRSC --jq '.size'` et contacter le support GitHub seulement si la taille ne baisse pas après quelques jours.

## Règle pour la suite

Ne pas committer de nouvelles planches PNG dans le dépôt. Les déposer dans une version étiquetée (`archives/…`), publier leur manifeste d’empreintes, et ne garder dans l’arbre que les planches réellement citées, en WebP **sans perte**.

## Limites

- La conversion sans perte préserve les pixels, pas la compression d’origine : les fichiers `.webp` conservés ne sont pas octet pour octet les `.png` archivés, même si l’image est identique.
- Le compte de fichiers et le poids « après » sont ceux de l’arbre fusionné le 19 octobre 2026 ; ils sont à recalculer avec les commandes ci-dessus si l’arbre évolue.
- Les planches restent « à relire » : aucune n’est validée, et ce document ne dit rien de leur intérêt artistique.
- `assets/images/favicon-192.png`, un temps livré sans être cité, est désormais déclaré comme icône 192×192 sur les 94 pages : plus aucune ressource du dossier `assets/` n’est orpheline.

## Séparation du 25 octobre 2026

La référence de personnage a été retirée de l’arbre courant et sauvegardée hors dépôt. Le manifeste intégral historique a été sorti de l’arbre courant ; le sous-ensemble associatif de 343 empreintes permet encore de vérifier les références du film, sans réexposer les entrées du personnage. L’étiquette et l’historique contiennent encore les anciennes ressources et ne doivent pas être rendus publics sans une purge séparée. Les douze planches du film associatif sont conservées.
