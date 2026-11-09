# Relecture de contenu automatique à chaque édition

**Note de méthode du 9 novembre 2026. État : mécanisme en place, relecture de fond du corpus existant encore en dette consignée.**

## 1. La demande et la frontière

Le 7 novembre, la personne a confié à l’agent la relecture de contenu et la vérification des sources sûres : elle ne veut pas « se cogner la lecture de millier de lignes », elle garde le rendu à l’œil pour valider un placement, un style, une construction. Le 9 novembre, elle a demandé que ce soit fait **automatiquement lors de toutes éditions**, « afin d’assurer d’avoir toujours du contenu qui soit propre, pro et sourcé sans erreurs ».

La réponse n’est pas de transformer un programme en juge de vérité. Un script ne sait pas décider qu’une phrase est exacte, ni fabriquer une expertise de domaine, ni remplacer une relecture humaine consignée. La réponse est de rendre l’étape **obligatoire, immédiate et vérifiable** : aucune édition ne peut être publiée sans être passée par l’agent, et la personne n’a rien à lire pour que ce soit le cas.

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

1. **Empreinte de chaque unité.** `docs/rd/empreintes-contenus.toml` consigne le SHA-256 des **494 fichiers texte** du dépôt (pages, fiches, scripts, feuilles, outils, documents, workflows, crochets). Un fichier nouveau non déclaré, un fichier déclaré disparu ou une empreinte modifiée font échouer la porte avec le chemin exact.
2. **Signature d’agent.** `docs/rd/editions-relecture.toml` reçoit une `[[edition]]` par fichier modifié : date, auteur forcé à `agent`, empreintes avant/après, nature (`fait-source`, `mesure-interne`, `proposition`), sources primaires ou fichiers reproductibles, constat et limites. `--appliquer` refuse de signer si une URL externe nouvelle n’est pas couverte par une source enregistrée, si une apostrophe droite apparaît, ou si une autre porte du dépôt est en faute.
3. **Sources vérifiables hors ligne.** Les huit sources primaires du 7 novembre (MDN, W3C/WAI, dépôt `w3c/wcag`) ont un extrait bref mis en cache dans `docs/rd/sources-primaires/`, avec URL, date et empreinte du corps. La porte confronte l’ancre du registre au contenu réel de l’extrait, refuse un extrait modifié et exige une consultation de moins de 366 jours par rapport à la dernière relecture. Une URL seule dans un fichier ne suffit plus.
4. **Batterie mécanique rejouée à chaque fois.** Ancres internes et liens locaux des 122 pages HTML, lisibilité de tous les TOML, absence de marqueurs de brouillon ou de conflit, aucune apostrophe droite nouvelle, câblage CI + crochet + inventaire, registre des relectures humaines vide, et `outils/verifier-relecture-contenus.py` pour le lot des apparences.

## 4. Ce que cela ne fait pas

- Cela ne **relit pas le fond du corpus existant**. Les 494 empreintes du 9 novembre sont une référence de départ ; `limite_reference` dans le manifeste dit noir sur blanc que la relecture éditoriale par agent de l’existant reste une dette visible. Les 107 fiches, 81 prototypes, le fond de `transparence.html`, la prospective et la citation signée ne sont pas déclarés validés.
- Cela ne **valide pas humainement** quoi que ce soit. `docs/apprentissage/relectures.toml` reste vide et reste le seul registre des relectures humaines ; aucune fiche n’est promue, aucun statut n’est embelli.
- Cela ne donne ni **expertise de domaine**, ni **avis juridique**, ni **essai avec des personnes**, ni **validation visuelle**. Trois recherches Web sur des noms ne remplacent pas une consultation INPI/EUIPO.
- Cela ne **juge pas la vérité** d’une page source : l’extrait est confronté à son ancre et à sa date, pas à la réalité du monde.
- Cela ne remplace pas les contrôles métier existants (générateurs, navigateur, accessibilité, publication) : cela les rend déclenchés par toute édition et empêche qu’on les contourne en oubliant la relecture.

## 5. Reproduire

```
python3 outils/relire-contenus.py
python3 outils/verifier-relecture-contenus.py
python3 outils/test_mutations_relire_contenus.py
```

Après une édition, l’agent consigne sa lecture :

```
python3 outils/relire-contenus.py --appliquer chemin/de/la/page.html \
  --nature fait-source --sources mdn-color-scheme,w3c-contrast-minimum \
  --constat "Ce qui a été relu et confronté." \
  --limite "Ce que cette relecture ne couvre pas."
```

`outils/test_mutations_relire_contenus.py` plante 17 fautes dans une copie jetable — édition non signée, unité absente ou orpheline, ancre morte, lien cassé, brouillon, TOML illisible, extrait modifié ou sans ancre, source périmée, crochet retiré, branche non couverte, apostrophe droite, édition falsifiée, écriture humaine usurpée, URL externe non sourcée — et exige que chacune soit refusée **en la nommant**. La copie intacte doit rester verte.
