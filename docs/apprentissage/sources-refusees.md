# Registre des sources tentées et refusées

**Document de travail généré.** Il recense les pages qui ont été tentées pour étayer une fiche du catalogue mais qui ont été écartées après vérification : accès refusé (HTTP 403), accès payant, page introuvable ou contenu hors du périmètre cherché après lecture.

**Ce que ce registre empêche :** qu'un autre agent ne retente puis ne cite une page illisible ou hors sujet pour faire baisser le nombre de constats sans preuve réelle. **Ce qu'il ne prouve pas :** qu'une fiche est relue, ni que toutes les sources possibles d'un sujet ont été explorées.

**Date de révision du registre :** 2026-10-20.

## 1. Vue d'ensemble

| Mesure | Valeur |
| --- | ---: |
| Sources refusées consignées | 6 |
| Fiches du catalogue concernées | 5 |
| Refus suivis d'une page de remplacement ouverte et lue | 5 |
| Motif : Accès refusé (HTTP 403) | 3 |
| Motif : Contenu hors du périmètre cherché après lecture | 3 |

Un refus consigné ne valide jamais la fiche associée : le statut éditorial dépend uniquement du registre des relectures humaines (`docs/apprentissage/relectures.toml`).

## 2. Détail des refus consignés

### `eduscol-lexique-arts-plastiques-hors-perimetre` — Éduscol — « Lexique pour les arts plastiques : Les éléments du langage plastique » (PDF)

- **Fiche concernée :** `arts-composer-formes`
- **Adresse écartée :** `https://eduscol.education.fr/document/14122/download`
- **Date de la tentative :** 2026-10-20
- **Catégorie de refus :** Contenu hors du périmètre cherché après lecture (`hors-perimetre`)
- **Motif constaté :** Ouverte et lue intégralement (4 parties) le 20 octobre 2026 : la ressource définit les notions de forme, d'espace et de support aux cycles 2 et 3, mais n'énonce ni la hiérarchie visuelle par taille, distance et isolement autour d'un titre, ni la règle d'accessibilité sur le contraste ne reposant pas sur la seule couleur.
- **Décision retenue :** Portail conservé par écrit en l'attente d'une page précise (`portail-conserve`)
- **Limite — ce que ce refus ne dit pas :** Refuser cette page maintient volontairement la fiche arts-composer-formes en constat (portail seul assumé par écrit) plutôt que d'y attacher une citation de façade qui ne couvre pas son affirmation principale.

### `eduscol-se-reperer-temps-hors-perimetre` — Éduscol — « Se repérer dans le temps : construire des repères historiques » (PDF)

- **Fiche concernée :** `histoire-situer-siecle`
- **Adresse écartée :** `https://eduscol.education.fr/document/16789/download`
- **Date de la tentative :** 2026-10-20
- **Catégorie de refus :** Contenu hors du périmètre cherché après lecture (`hors-perimetre`)
- **Motif constaté :** Ouverte et lue intégralement (3 parties) le 20 octobre 2026 : la ressource mentionne le lexique « année, décennie, siècle » mais n'énonce ni l'absence d'année zéro ni les bornes arithmétiques d'un siècle (an 1 à an 100, 1901 à 2000).
- **Décision retenue :** Remplacée par une autre page ouverte et lue (`remplacee`)
- **Source de remplacement dans le catalogue :** `https://promenade.imcce.fr/fr/pages2/277.html`
- **Limite — ce que ce refus ne dit pas :** La fiche Éduscol 16789 reste pertinente pour la didactique du temps historique aux cycles 3 et 4 ; elle est refusée ici uniquement parce qu'elle n'étaye pas la règle de bornage arithmétique des siècles enseignée par la fiche.

### `hal-citations-fonctionnalite-non-active` — HAL — « Les citations dans HAL »

- **Fiche concernée :** `recherche-distinguer-resume-citation`
- **Adresse écartée :** `https://doc.hal.science/citations/`
- **Date de la tentative :** 2026-10-20
- **Catégorie de refus :** Contenu hors du périmètre cherché après lecture (`hors-perimetre`)
- **Motif constaté :** Ouverte le 20 octobre 2026 : la page annonce d'emblée qu'elle décrit une fonctionnalité d'export de citations (APA, MLA, IEEE, Chicago) non encore mise en place, au lieu d'expliquer les champs Résumé et Citer d'une notice déposée.
- **Décision retenue :** Remplacée par une autre page ouverte et lue (`remplacee`)
- **Source de remplacement dans le catalogue :** `https://doc.hal.science/visualisation-dun-depot/`
- **Limite — ce que ce refus ne dit pas :** Ce refus porte uniquement sur l'adéquation de cette page à l'objectif de la fiche au 20 octobre 2026 ; il ne juge ni la qualité de la documentation HAL, ni le fonctionnement réel de l'archive ouverte.

### `ign-livret-decouvrez-monde-cartes-403` — IGN — « Découvrez le monde des cartes » (livret pédagogique PDF)

- **Fiche concernée :** `geo-lire-legende-carte`
- **Adresse écartée :** `https://www.ign.fr/publications-de-l-ign/institut/Ressources_pedagogiques/livret_decouvrez_LMDC.pdf`
- **Date de la tentative :** 2026-10-20
- **Catégorie de refus :** Accès refusé (HTTP 403) (`acces-refuse-403`)
- **Motif constaté :** Tentée le 20 octobre 2026 : le téléchargement direct du livret PDF renvoie une erreur HTTP 403. Faute d'ouverture directe du document, il est écarté au profit d'une ressource pédagogique Éduscol ouverte et lue.
- **Décision retenue :** Remplacée par une autre page ouverte et lue (`remplacee`)
- **Source de remplacement dans le catalogue :** `https://eduscol.education.fr/document/16807/download`
- **Limite — ce que ce refus ne dit pas :** Ce refus constate seulement l'impossibilité d'ouvrir le PDF à la date du relevé ; il ne dit rien de l'exactitude ni de la licence du livret de l'IGN, dont le portail reste cité comme point d'entrée.

### `ign-livret-decouvrez-monde-cartes-paysage-403` — IGN — « Découvrez le monde des cartes » (livret pédagogique PDF)

- **Fiche concernée :** `geo-decrire-paysage`
- **Adresse écartée :** `https://www.ign.fr/publications-de-l-ign/institut/Ressources_pedagogiques/livret_decouvrez_LMDC.pdf`
- **Date de la tentative :** 2026-10-20
- **Catégorie de refus :** Accès refusé (HTTP 403) (`acces-refuse-403`)
- **Motif constaté :** Tentée le 20 octobre 2026 pour la lecture de paysage : le téléchargement direct du livret PDF renvoie une erreur HTTP 403. Conformément à la règle interdisant de citer une page non ouverte, cette adresse est écartée.
- **Décision retenue :** Remplacée par une autre page ouverte et lue (`remplacee`)
- **Source de remplacement dans le catalogue :** `https://eduscol.education.fr/document/16804/download`
- **Limite — ce que ce refus ne dit pas :** Ce refus constate uniquement le blocage HTTP 403 lors de la consultation ; la ressource Éduscol de remplacement (document 16804) couvre la démarche de description géographique mais pas la vallée fictive de la fiche.

### `ign-mag-lire-carte-cinq-etapes-403` — IGN — « Apprendre à lire une carte en cinq étapes »

- **Fiche concernée :** `geo-lire-legende-carte`
- **Adresse écartée :** `https://www.ign.fr/mag/apprendre-lire-une-carte-en-cinq-etapes`
- **Date de la tentative :** 2026-10-20
- **Catégorie de refus :** Accès refusé (HTTP 403) (`acces-refuse-403`)
- **Motif constaté :** Tentée le 20 octobre 2026 : l'ouverture directe de la page renvoie une erreur HTTP 403. Seuls des extraits d'indexation étaient visibles, ce qui ne permet ni de lire la page en entier, ni d'en vérifier le périmètre et les droits.
- **Décision retenue :** Remplacée par une autre page ouverte et lue (`remplacee`)
- **Source de remplacement dans le catalogue :** `https://eduscol.education.fr/document/16807/download`
- **Limite — ce que ce refus ne dit pas :** Un refus HTTP 403 depuis l'environnement de travail ne prouve pas que la page est indisponible pour un navigateur ordinaire, mais interdit de la citer comme une source ouverte et lue.

## 3. Garde-fous vérifiés par la porte

- Une adresse inscrite dans ce registre ne peut pas figurer simultanément parmi les sources actives de `docs/apprentissage/catalogue.toml`.
- Lorsqu'un refus est marqué `remplacee`, l'adresse `url_remplacement` doit être présente sur la fiche concernée dans le catalogue.
- Aucun extrait long sous droits n'est stocké dans le champ `motif` : seule la raison factuelle du refus est consignée.
- Toute entrée sans date réelle, sans motif explicite ou sans limite écrite fait échouer le contrôle.

Généré depuis `docs/apprentissage/sources-refusees.toml` ; vérifier avec `python3 outils/construire-sources-refusees.py --verifier`.
