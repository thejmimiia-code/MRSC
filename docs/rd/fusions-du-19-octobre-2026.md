# Fusions du 19 octobre 2026 : point et contrôle d'intégrité

**Date :** 19 octobre 2026.  
**Statut :** relevé technique par l'agent, pas une revue éditoriale, pas une validation humaine. Les chiffres viennent de commandes reproductibles, reproduites plus bas. Aucun jugement sur le fond des propositions n'est porté ici.

## Pourquoi

Six propositions de fusion étaient ouvertes sur `main`, toutes signalées « en conflit », et aucune n'était fusionnable en l'état. La passe visait à faire le point sur chacune, à distinguer un apport réellement nouveau d'un travail déjà intégré, puis à contrôler l'intégrité du résultat après la fusion. Ce document est le **point d'analyse** ; le poids des planches est traité dans [`archives-et-poids-du-depot.md`](archives-et-poids-du-depot.md).

## Méthode

- Dépôt remis en profondeur (`git fetch --unshallow`) avant toute mesure. Le clone initial était tronqué à `c67a941`, ce qui faisait passer `main` pour un ancêtre direct des six branches et masquait la divergence réelle : sans cette remise en profondeur, aucune mesure de conflit n'est fiable.
- Pour chaque proposition : base de fusion réelle (`git merge-base`), fichiers en conflit (`git merge-tree`), et confrontation de chaque ligne ajoutée par la proposition avec la version de `main` du même fichier.
- Pour les propositions dont l'apport paraissait déjà repris : fusion complète dans un worktree détaché, résolution de tous les conflits par le contenu de `main`, puis comparaison de l'arbre obtenu avec l'arbre de `main` (`git rev-parse <commit>^{tree}`).
- Après les fusions : contrôle d'intégrité du texte de `main` contre la version d'origine de chaque proposition, recherche d'anomalies de caractères, et exécution de la porte de vérification du dépôt.

## Ce que contenait chaque proposition

| PR | Branche | Commits | Retard sur `main` au moment de l'analyse | Fichiers en conflit | Apport encore absent de `main` |
|---|---|---|---|---|---|
| [#85](https://github.com/thejmimiia-code/MRSC/pull/85) | `arena/1dfe1c18-mrsc` | 60 | 91 | 1 | **oui** — 583 lignes de fond et 505 planches |
| [#94](https://github.com/thejmimiia-code/MRSC/pull/94) | `arena/26d57815-mrsc` | 2 | 76 | 3 | non |
| [#98](https://github.com/thejmimiia-code/MRSC/pull/98) | `arena/13f92351-mrsc` | 1 | 66 | 4 | non |
| [#100](https://github.com/thejmimiia-code/MRSC/pull/100) | `arena/6f04b42c-mrsc` | 1 | 61 | 3 | non |
| [#104](https://github.com/thejmimiia-code/MRSC/pull/104) | `arena/f24fb15f-mrsc` | 1 | 52 | 6 | non |
| [#112](https://github.com/thejmimiia-code/MRSC/pull/112) | `arena/d2a9e068-mrsc` | 1 | 34 | 5 | non |

Les cinq dernières propositions n'étaient pas en conflit « par hasard » : elles avaient été écrites sur une version antérieure des mêmes fichiers, et `main` avait depuis intégré un travail équivalent ou plus abouti. La preuve est directe — **résoudre leurs conflits en conservant le contenu de `main` redonne un arbre strictement identique à celui de `main`**, comparaison d'arbres à l'appui, sans aucun écart. Il ne restait donc rien à y fusionner.

- **#94 — file de relecture des 55 prototypes.** `outils/file-relecture.py` est identique à l'octet près à celui de `main` ; `docs/apprentissage/file-relecture.md` y est présent. Le correctif de contraste du héros existe aussi : `main` utilise `var(--on-navy)` là où la proposition écrivait `#fff`, c'est-à-dire la même correction passée par les jetons de rôle.
- **#98 — protéger la trace de décision.** La fonction `etat_trace_decision` de `main` porte la signature étendue `(markdown, date_brief)` et ajoute le contrôle de l'ancrage sur la date du brief, l'ordre décision / réexamen et la cohérence avec l'état `a-cadrer` de l'initiative. La proposition apportait la version simple, déjà dépassée.
- **#100 — modèle de menace du vote.** `docs/rd/vote-distanciel-menaces.toml` est identique à celui de `main`. La vérification proposée en ligne dans `principal()` a été reprise dans `main` sous la forme de `verifier_registre()`, avec les mêmes messages et des contrôles supplémentaires.
- **#104 — sources candidates épinglées.** `main` contient le même `docs/rd/vote-distanciel-sources.toml` **plus** deux champs par projet (`points_a_resoudre`, `preuves_a_chercher`), et `verifier_sources()` exige ces champs. Reprendre la version de la proposition aurait fait échouer `verifier-vote-distanciel.py` : c'eût été une régression, pas une fusion.
- **#112 — chaîne de preuves logicielles.** `docs/rd/vote-distanciel-chaine-logicielle.toml` est identique à celui de `main`, et `verifier_chaine_logicielle()` y est déjà présente.

## Contrôle d'intégrité après les fusions

Aucune perte de contenu n'a été constatée :

- **Entrées de journal** : les entrées de `main` correspondent, corps compris, à l'ensemble des entrées des six propositions. Aucune entrée manquante, aucun doublon de titre.
- **Fichiers de code et de données** : `verifier_registre`, `verifier_sources`, `verifier_chaine_logicielle`, `verifier_resultats` et `verifier_revues` sont présents dans `outils/verifier-vote-distanciel.py` ; `etat_trace_decision` garde la signature étendue ; `docs/rd/vote-distanciel-sources.toml` a conservé `points_a_resoudre` et `preuves_a_chercher` ; la feuille de style utilise toujours `var(--on-navy)`.
- **Caractères** : la comparaison de tous les fichiers texte de `main` avec la version d'origine de chaque proposition ne fait apparaître qu'une seule anomalie, décrite ci-dessous.

### Une coquille corrigée

La ligne « **Contrôles réellement exécutés :** rédaction documentaire… » de l'entrée « Plan films d'animation des statuts » avait perdu une lettre : « **Contr ôles réellement exécutés :** ». La ligne est rétablie. C'était la seule anomalie de ce type dans tout l'arbre, et la seule ligne du journal modifiée par cette passe.

### L'ordre du journal

La résolution du conflit de la proposition #85 avait placé les 29 entrées du 2026-10-16 en tête du journal, au-dessus des entrées du 2026-10-18 et du 2026-10-17, rompant l'ordre antichronologique. **Cet ordre a été rétabli en amont**, dans la fusion de la proposition #129, par la personne responsable du dépôt. La présente passe s'est limitée à le vérifier sur l'ensemble des entrées et à conserver les entrées du 2026-10-19 — celles du ménage des propositions, du retrait des planches, du contrôle des liens et du présent relevé.

### Les liens de la bible du film

Le retrait des planches de l'arbre a rendu **non résolus les 193 liens d'image** de [`statuts-animation/bible-fil-et-video-01.md`](statuts-animation/bible-fil-et-video-01.md), qui n'étaient vérifiés par aucun contrôle. Le plan [`plan-statuts-animation.md`](plan-statuts-animation.md) avait reçu une mention d'archive ; la bible, non. Une mention d'archive identique y a été ajoutée, qui indique où sont les planches et que les liens ci-dessous désignent les versions archivées.

Le manque a ensuite été comblé en amont, dans la proposition #133 : `outils/verifier-planches-statuts.py` contrôle désormais **les 205 liens d'image des documents de `docs/rd/`**, et un lien vers un fichier ni présent dans l'arbre ni inscrit au manifeste fait échouer la porte. Les 193 liens de la bible sont acceptés explicitement, parce qu'ils désignent des planches archivées. Un lien cassé ne peut plus passer sans bruit.

Commande de contrôle, avant l'automatisation de la proposition #133 :

```sh
python3 - <<'PY'
import re, subprocess, os
for d in ("docs/rd/statuts-animation/bible-fil-et-video-01.md", "docs/rd/plan-statuts-animation.md"):
    txt = subprocess.run(["git", "cat-file", "blob", f"HEAD:{d}"], capture_output=True).stdout.decode()
    liens = re.findall(r"\]\(([^)]*\.(?:png|webp|jpg))\)", txt)
    casses = [l for l in liens if subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:docs/rd/statuts-animation/{os.path.basename(l)}"],
        capture_output=True).returncode != 0]
    print(d, len(liens), "liens,", len(casses), "non résolus")
PY
```

Les « non résolus » de la bible sont les liens vers les planches archivées : ils ne le sont plus au sens du contrôle, qui les reconnaît maintenant grâce au manifeste.

## Le poids des planches

La proposition #85 a fait entrer **505 PNG (1 291 Mo)** sous `docs/rd/statuts-animation/`, faisant passer l'arbre de `main` de 8,8 Mo à 1 299,7 Mo. La question a été reprise et tranchée en amont, en deux temps :

- **proposition #130** — seules les douze planches citées par le plan restent dans l'arbre, les 493 autres sont archivées dans l'étiquette `planches-statuts-animation-2026-10`, et `.gitignore` empêche le retour de PNG dans le dossier ;
- **proposition #132** — l'encodage WebP qualité 82 s'est révélé **avec perte** (1 058 000 à 1 077 000 pixels modifiés par planche, sur 1 081 344). La conversion a été refaite en **WebP sans perte**, écart pixel mesuré **0** sur les douze planches, pour 14,7 Mo au lieu de 31,4 Mo de PNG. Un manifeste SHA-256 des **507 fichiers d'origine** a été produit (`ARCHIVE-planches-2026-10.sha256`), et `outils/verifier-planches-statuts.py` refuse désormais une planche citée absente, une référence sans fichier ni archive, un PNG réintroduit dans l'arbre ou un manifeste incomplet.

Résultat : l'arbre tombe à **23,6 Mo et 363 fichiers**, sans perte de contenu, les originaux restant accessibles octet pour octet dans l'étiquette. Voir [`archives-et-poids-du-depot.md`](archives-et-poids-du-depot.md) pour les chiffres, la procédure de récupération et la réécriture d'historique qui reste à décider par la personne qui administre le dépôt.

## Contrôles exécutés

```
py_compile simulateur/*.py api/*.py outils/*.py
python3 outils/verifier-rd-continue.py
python3 outils/construire-apprentissages.py --verifier
python3 outils/construire-simulateur.py --verifier
python3 outils/verifier-site-statique.py
python3 outils/optimiser-images.py --verifier
python3 outils/verifier-poids-pages.py
python3 outils/verifier-planches-statuts.py
python3 outils/verifier-securite.py
python3 outils/verifier-integration.py
python3 outils/verifier-decision-prospective.py
python3 outils/verifier-vote-distanciel.py
python3 outils/test_verifier_vote_distanciel.py
python3 outils/test_verifier_decision_prospective.py
python3 outils/file-relecture.py --verifier
python3 outils/verifier-resilience-statutaire.py
python3 outils/test_verifier_resilience_statutaire.py
```

Les seize commandes réussissent. Le poids des pages reste sous budget : 95 pages, dont `simulateur/index.html` à 72,7 Kio. `verifier-publication.py` n'a pas été exécuté : il exige une URL publiée et mesure l'hébergement, pas le dépôt.

## Limites

- Ce relevé ne dit pas si le fond des propositions est juste : les planches restent « à relire » et le plan d'animation une proposition, pas une décision.
- La relecture humaine, la validation des sources et l'arbitrage éditorial ne sont pas faits ici.
- Le contrôle des liens d'image, longtemps absent, existe désormais (proposition #133) : `outils/verifier-planches-statuts.py` couvre les 205 liens d'image de `docs/rd/` et tolère les 193 liens de la bible parce qu'ils sont au manifeste. Ce qu'il ne vérifie pas : qu'un lien autorisé pointe encore vers le bon fichier, seulement qu'un fichier de ce nom existe. Une renumérotation des planches archivées passerait le contrôle.
- Aucun mesurage réseau, aucune mesure de temps de clonage, aucun contrôle du temps de déploiement n'a été réalisé.
- Les 507 empreintes du manifeste ont été produites à partir de l'étiquette ; l'absence d'écart constatée vaut pour les fichiers présents dans l'étiquette au moment de la mesure, pas pour l'intégrité de l'étiquette elle-même, qui n'a pas été vérifiée comme objet signé.
