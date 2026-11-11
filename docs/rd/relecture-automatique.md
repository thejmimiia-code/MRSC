# Relecture de contenu automatique à chaque édition

**Note de méthode du 9 novembre 2026, complétée le 10 novembre 2026. État : mécanisme en place ; relecture de fond des 81 prototypes exécutée et consignée, le reste du corpus existant gardé en dette visible.**

## 1. La demande et la frontière

Le 7 novembre, la personne a confié à l’agent la relecture de contenu et la vérification des sources sûres : elle ne veut pas « se cogner la lecture de millier de lignes », elle garde le rendu à l’œil pour valider un placement, un style, une construction. Le 9 novembre, elle a demandé que ce soit fait **automatiquement lors de toutes éditions**, « afin d’assurer d’avoir toujours du contenu qui soit propre, pro et sourcé sans erreurs ».

La réponse n’est pas de transformer un programme en juge de vérité. Un script ne sait pas décider qu’une phrase est exacte, ni fabriquer une expertise de domaine, ni remplacer une relecture humaine consignée. La réponse est de rendre l’étape **obligatoire, immédiate et vérifiable** : aucune édition ne peut être publiée sans être passée par l’agent, et la personne n’a rien à lire pour que ce soit le cas.

Le 10 novembre 2026, la personne a rappelé : « la relecture c’est toi qui doit la faire ». La lecture du contenu et la vérification des sources ne sont donc **jamais** une porte à lui attribuer. `docs/rd/relecture-agent-prototypes.toml` et `docs/rd/relecture-agent-prototypes-2026-11-10.md` consignent la passe effectuée sur les 81 prototypes ; `docs/apprentissage/relectures.toml` reste le registre vide des seules relectures humaines, et la personne garde le jugement du rendu à l’œil.

| Qui | Fait quoi |
| --- | --- |
| L’agent | Relit le texte modifié, confronte chaque fait à une source primaire datée, corrige ou retire ce qui n’est pas étayé, consigne le constat et les limites. |
| La porte `outils/relire-contenus.py` | Refuse toute édition non signée, rejoue les contrôles mécaniques, vérifie les extraits de sources, les dates, le câblage et l’absence de promotion en relecture humaine. |
| La personne | Peut valider à l’œil un placement, un style, une construction. Aucune lecture de registre n’est demandée. |

## 2. Ce qui se déclenche tout seul

| Déclencheur | Portée | Commande |
| --- | --- | --- |
| `.github/workflows/relecture-contenus.yml` | Chaque `push` sur **toutes les branches**, chaque `pull_request`, chaque `workflow_dispatch` | `python3 outils/relire-contenus.py`, la porte du lot, puis le banc de mutations |
| `.github/workflows/verification.yml` | CI lourde existante, sur les PR et `main` | les deux mêmes commandes, ajoutées à l’étape de relecture |
| `.githooks/pre-commit` | Chaque `commit` local, après `git config core.hooksPath .githooks` | `python3 outils/relire-contenus.py` |

Le crochet local est une commodité : un `--no-verify` ne contourne pas la CI. La CI, elle, ne signe jamais rien : elle vérifie. C’est l’agent qui signe, après avoir lu.

## 3. Les quatre verrous

1. **Empreinte de chaque unité.** `docs/rd/empreintes-contenus.toml` consigne le SHA-256 de chaque fichier texte du dépôt (pages, fiches, scripts, feuilles, outils, documents, workflows, crochets) : **499 unités avant la passe du 10 novembre 2026, 503 après** l’ajout des quatre fichiers de méthode de cette passe, **507 après** les quatre fichiers de la passe de sources du 11 novembre 2026, **509 après** les deux fichiers du complément de la seconde passe du même jour, **511 après** les deux fichiers de la troisième passe consacrée à l’accueil IGN, **519 après** les huit fichiers du lot de plan complet du projet (4 cartes de cadrage, 2 outils et les 2 fichiers du plan). **523 après** les quatre fichiers du lot plan complet du site du 17 h 24 UTC (2 documents et 2 outils). À l’issue de ce lot : **523 unités sous empreinte, 136 relues par agent, 387 en dette initiale consignée**. Un fichier nouveau non déclaré, un fichier déclaré disparu ou une empreinte modifiée font échouer la porte avec le chemin exact.
2. **Signature d’agent.** `docs/rd/editions-relecture.toml` reçoit une `[[edition]]` par fichier modifié : date, auteur forcé à `agent`, empreintes avant/après, nature (`fait-source`, `mesure-interne`, `proposition`), sources primaires ou fichiers reproductibles, constat et limites. `--appliquer` refuse de signer si une URL externe nouvelle n’est pas couverte par une source enregistrée, si une apostrophe droite apparaît, ou si une autre porte du dépôt est en faute.
3. **Sources vérifiables hors ligne.** Les huit sources primaires du 7 novembre (MDN, W3C/WAI, dépôt `w3c/wcag`) ont un extrait bref mis en cache dans `docs/rd/sources-primaires/`, avec URL, date et empreinte du corps. La porte confronte l’ancre du registre au contenu réel de l’extrait, refuse un extrait modifié et exige une consultation de moins de 366 jours par rapport à la dernière relecture. Une URL seule dans un fichier ne suffit plus.
4. **Batterie mécanique rejouée à chaque fois.** Ancres internes et liens locaux des 122 pages HTML, lisibilité de tous les TOML, absence de marqueurs de brouillon ou de conflit, aucune apostrophe droite nouvelle, câblage CI + crochet + inventaire, registre des relectures humaines vide, et `outils/verifier-relecture-contenus.py` pour le lot des apparences.

## 4. Ce que cela ne fait pas

- La relecture de fond **des 81 prototypes est désormais faite par l’agent** : 11 champs lus par fiche, 17 pages de source ouvertes, 20 égalités simples recalculées sans écart, 40 constats à trancher. Les 89 adresses uniques encore non ouvertes le 10 novembre 2026 ont été tentées le 11 novembre 2026 : 83 contenus, 3 pages d’erreur servies et 3 erreurs de récupération. Une seconde passe du même jour a retenté les 3 erreurs et lu 16 pages officielles de remplacement ou de contexte pour 5 des 6 adresses ; l’accueil IGN reste en HTTP 403, sans page lue. Une troisième passe retente cet accueil (13 réponses HTTP 403) et lit 10 pages officielles de l’IGN sur `cartes.gouv.fr` et `data.geopf.fr`, sans déclarer la source-portail résolue ni modifier les deux fiches de géographie. Voir `docs/rd/relecture-agent-prototypes-2026-11-10.md`, `docs/rd/sources-ouvertes-2026-11-11.md`, `docs/rd/sources-complement-2026-11-11.md` et `docs/rd/sources-ign-2026-11-11.md`.
- Cela ne **relit pas le reste du corpus existant**. Les empreintes du 9 novembre restent une référence de départ ; `limite_reference` dans le manifeste dit noir sur blanc que la relecture éditoriale par agent des autres unités reste une dette visible. Les 26 fiches sans statut éditorial, le fond de `transparence.html`, la prospective, la citation signée et les 387 unités encore en `reference-initiale` après le lot site du 17 h 24 UTC ne sont pas déclarés validés.
- Cela ne **valide pas humainement** quoi que ce soit. `docs/apprentissage/relectures.toml` reste vide et reste le seul registre des relectures humaines ; aucune fiche n’est promue, aucun statut n’est embelli.
- Cela ne donne ni **expertise de domaine**, ni **avis juridique**, ni **essai avec des personnes**, ni **validation visuelle**. Trois recherches Web sur des noms ne remplacent pas une consultation INPI/EUIPO.
- Cela ne **juge pas la vérité** d’une page source : l’extrait est confronté à son ancre et à sa date, pas à la réalité du monde.
- Cela ne remplace pas les contrôles métier existants (générateurs, navigateur, accessibilité, publication) : cela les rend déclenchés par toute édition et empêche qu’on les contourne en oubliant la relecture.

## 5. Reproduire

```
python3 outils/relire-contenus.py
python3 outils/verifier-relecture-contenus.py
python3 outils/test_mutations_relire_contenus.py
python3 outils/relecture-agent-prototypes.py --verifier
python3 outils/test_mutations_relecture_agent_prototypes.py
```

Après une édition, l’agent consigne sa lecture :

```
python3 outils/relire-contenus.py --appliquer chemin/de/la/page.html \
  --nature fait-source --sources mdn-color-scheme,w3c-contrast-minimum \
  --constat "Ce qui a été relu et confronté." \
  --limite "Ce que cette relecture ne couvre pas."
```

`outils/test_mutations_relire_contenus.py` plante 17 fautes dans une copie jetable — édition non signée, unité absente ou orpheline, ancre morte, lien cassé, brouillon, TOML illisible, extrait modifié ou sans ancre, source périmée, crochet retiré, branche non couverte, apostrophe droite, édition falsifiée, écriture humaine usurpée, URL externe non sourcée — et exige que chacune soit refusée **en la nommant**. La copie intacte doit rester verte.
