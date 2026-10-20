# Prototype de confrontation d'affirmations aux sources déclarées

**Document de travail R&D généré — hors porte de publication.** Il éprouve l'initiative `confronter-une-affirmation-a-sa-source` sur un échantillon de fiches déjà pourvues d'une page précise ouverte et datée. Il ne valide aucune fiche, ne remplace aucune relecture humaine et ne stocke aucun extrait sous droits.

**Question testée :** peut-on vérifier mécaniquement qu'une page citée contient encore les repères clés d'une affirmation de fiche, sans lire à la place d'une personne ? **Réponse observée sur l'échantillon :** les ancres courtes produisent un **indice de maintenance** utile, mais souffrent de faux positifs (négation non détectée, chiffre présent dans une autre colonne) et de faux négatifs (formules coupées dans un PDF, périmètre réparti entre deux sources, synonymes).

**Date du relevé :** 2026-10-20.

## 1. Synthèse de l'échantillon

| Mesure | Valeur |
| --- | ---: |
| Confrontations documentées | 5 |
| Fiches distinctes couvertes | 5 |
| Indice concordant (`indice-concordant`) | 4 |
| Constat de couverture partielle (`constat-couverture-partielle`) | 1 |

Aucun des états ci-dessus n'est une validation éditoriale ni un verdict d'erreur contre la fiche.

## 2. Détail par confrontation

### `angle-droit-sommet-90-degres` (`maths-reperer-angle-droit`)

- **Source confrontée :** `https://eduscol.education.fr/document/36614/download`
- **Affirmation de la fiche (texte M.R.S.C.) :** Un angle se repère par son sommet et ses côtés ; l'angle droit mesure 90°.
- **Ancres cherchées (4) :** `sommet`, `côté`, `angle droit`, `90°`
- **Ancres repérées :** `sommet`, `côté`, `angle droit`, `90°`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** Dans le tableau de la ressource Éduscol, « 90° » apparaît trois fois : « de 0° à 90° » (angle aigu), « 90° » (angle droit) et « de 90° à 180° » (angle obtus). Une fiche qui écrirait par erreur qu'un angle obtus vaut 90° passerait quand même le test d'ancre.
- **Faux négatif documenté :** Selon l'outil d'extraction PDF, le symbole degré est parfois converti en formule LaTeX (« 90^{\circ} ») ou en lettre « o » en exposant, faisant échouer la recherche littérale de « 90° ».
- **Limite :** Cet indice vérifie uniquement la présence du vocabulaire de base dans le document Éduscol du 20 octobre 2026 ; il ne contrôle ni la clarté de l'exercice ni l'accessibilité sans figure géométrique.

### `credit-conso-taux-frais-taeg` (`econ-distinguer-interet-frais`)

- **Source confrontée :** `https://www.service-public.gouv.fr/particuliers/vosdroits/F2451`
- **Affirmation de la fiche (texte M.R.S.C.) :** Pour comparer le coût d'un crédit à la consommation, on distingue le taux débiteur, les frais compris dans le coût total du crédit et le taux annuel effectif global.
- **Ancres cherchées (4) :** `taux débiteur`, `frais`, `coût total du crédit`, `taux annuel effectif global`
- **Ancres repérées :** `taux débiteur`, `frais`, `coût total du crédit`, `taux annuel effectif global`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** Faux positif observé sur cette même page le 20 octobre 2026 : la fiche F2451 contient les mots « améliore la situation financière ou le budget de l'emprunteur » et « substitut d'épargne » dans la liste de ce qu'il est interdit d'écrire dans une publicité. Un contrôle par mots-clés qui ignorerait la négation « Il est interdit » validerait à tort une affirmation illégale.
- **Faux négatif documenté :** Une mise à jour éditoriale de Service-Public.fr qui emploierait l'abréviation « TAEG » au lieu de la forme développée « taux annuel effectif global » ferait disparaître l'ancre sans changement du droit applicable.
- **Limite :** Cet indice ne vaut ni validation juridique ni conseil financier : la présence des termes réglementaires dans la fiche F2451 ne prouve pas que l'exemple chiffré fictif de la fiche M.R.S.C. est exact.

### `melange-changement-etat-perimetre-scinde` (`sciences-distinguer-melange-changement-etat`)

- **Source confrontée :** `https://eduscol.education.fr/document/15199/download`
- **Affirmation de la fiche (texte M.R.S.C.) :** La fusion est un changement d'état d'une même substance avec conservation de la masse, tandis que la dissolution disperse un solide soluble dans l'eau.
- **Ancres cherchées (4) :** `glace`, `fonte`, `masse`, `dissolution`
- **Ancres repérées :** `glace`, `fonte`, `masse`
- **Ancres absentes :** `dissolution`
- **État du relevé (2026-10-20) :** `constat-couverture-partielle` — Constat de couverture partielle — certaines ancres sont absentes de cette source précise, à interpréter par une personne
- **Faux positif documenté :** Le mot « eau » figure dans les deux documents Éduscol de la fiche : l'utiliser comme seule ancre donnerait un indice concordant trompeur sur un document qui ne parle pourtant pas de dissolution.
- **Faux négatif documenté :** Cas réel de faux négatif de périmètre observé le 20 octobre 2026 : l'ancre « dissolution » est absente du document 15199 parce que la fiche répartit son étayage entre deux sources complémentaires (le document 15199 pour la fusion et le document 95295 pour la dissolution).
- **Limite :** Un constat de couverture partielle sur une source isolée ne signale pas une erreur de la fiche : il rappelle qu'une affirmation composée peut reposer sur plusieurs sources distinctes du catalogue.

### `meteo-climat-reference-30-ans` (`sciences-meteo-climat`)

- **Source confrontée :** `https://meteofrance.com/meteo-a-z/quelle-difference-entre-meteo-et-climat`
- **Affirmation de la fiche (texte M.R.S.C.) :** La météo décrit le temps à un instant et un endroit donnés ; le climat repose sur des moyennes sur plusieurs décennies, avec une période de référence de 30 ans, et une vague de froid isolée ne suffit pas à infirmer la tendance climatique.
- **Ancres cherchées (6) :** `instant`, `endroit`, `moyenne`, `décennies`, `30 ans`, `vague de froid`
- **Ancres repérées :** `instant`, `endroit`, `moyenne`, `décennies`, `30 ans`, `vague de froid`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** La présence simultanée de « 30 ans », « moyenne » et « vague de froid » dans la page ne prouve pas le sens de la relation : un texte qui contesterait la normale de 30 ans contiendrait exactement les mêmes ancres.
- **Faux négatif documenté :** Si Météo-France remplace « 30 ans » par « trente années » ou déplace ce repère dans un schéma illustré, l'ancre disparaît du texte brut alors que l'affirmation reste étayée.
- **Limite :** Cet indice confirme uniquement que les six repères lexicaux figuraient dans la page ouverte le 20 octobre 2026 ; il ne vérifie ni la justesse pédagogique de la fiche ni l'absence de contresens.

### `vitesse-moyenne-quotient-unites` (`sciences-calculer-vitesse-moyenne`)

- **Source confrontée :** `https://eduscol.education.fr/document/16837/download`
- **Affirmation de la fiche (texte M.R.S.C.) :** La vitesse moyenne relie la distance parcourue et la durée du parcours par une division, et s'exprime notamment en m/s ou en km/h.
- **Ancres cherchées (6) :** `vitesse`, `distance`, `durée`, `m/s`, `km/h`, `400`
- **Ancres repérées :** `vitesse`, `distance`, `durée`, `m/s`, `km/h`, `400`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** Le même document Éduscol cite aussi la formule d'énergie « E = P × t » (grandeur produit) pour la opposer à la vitesse : repérer « distance » et « durée » dans le corps du texte ne prouve pas que la fiche utilise la bonne opération.
- **Faux négatif documenté :** Faux négatif observé le 20 octobre 2026 lors de l'extraction du PDF : dans l'équation mise en forme, le mot « durée » est découpé en « dur é e » et « distance parcourue » est collé en « distanceparcourue ». Chercher la formule exacte échoue sur le PDF alors qu'elle y figure.
- **Limite :** L'indice porte sur des mots isolés présents dans le PDF du 20 octobre 2026 ; la coupure des formules mathématiques lors de l'extraction montre qu'une absence d'ancre dans un PDF ne permet jamais de conclure que la fiche est fausse.

## 3. Pourquoi ce dispositif reste hors de la porte de publication

1. **Faux positifs avérés :** sur `econ-distinguer-interet-frais` (Service-Public F2451), des mots comme « améliore » et « budget » apparaissent dans la liste des mentions publicitaires interdites ; sur `maths-reperer-angle-droit`, « 90° » apparaît aussi dans les bornes des angles aigus et obtus.
2. **Faux négatifs avérés :** sur `sciences-calculer-vitesse-moyenne`, l'extraction du PDF Éduscol découpe « durée » en « dur é e » dans la formule mathématique ; sur `sciences-distinguer-melange-changement-etat`, l'étayage est réparti entre deux documents complémentaires.
3. **Règle de décision :** une page inaccessible ou modifiée produit un constat pour orienter la veille humaine, jamais un échec automatique de publication ni une conclusion sur la vérité de la fiche.

Généré depuis `docs/rd/confrontations-sources.toml` ; vérifier avec `python3 outils/confronter-sources.py --verifier`.
