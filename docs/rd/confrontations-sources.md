# Prototype de confrontation d'affirmations aux sources déclarées

**Document de travail R&D généré — hors porte de publication.** Il éprouve l'initiative `confronter-une-affirmation-a-sa-source` sur un échantillon de fiches déjà pourvues d'une page précise ouverte et datée. Il ne valide aucune fiche, ne remplace aucune relecture humaine et ne stocke aucun extrait sous droits.

**Question testée :** peut-on vérifier mécaniquement qu'une page citée contient encore les repères clés d'une affirmation de fiche, sans lire à la place d'une personne ? **Réponse observée sur l'échantillon :** les ancres courtes produisent un **indice de maintenance** utile, mais souffrent de faux positifs (négation non détectée, chiffre présent dans une autre colonne) et de faux négatifs (formules coupées dans un PDF, périmètre réparti entre deux sources, synonymes).

**Date du relevé :** 2026-10-20.

## 1. Synthèse de l'échantillon

| Mesure | Valeur |
| --- | ---: |
| Confrontations documentées | 9 |
| Fiches distinctes couvertes | 9 |
| Indice concordant (`indice-concordant`) | 8 |
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

### `comparer-sources-auteur-contexte-point-de-vue` (`histoire-comparer-sources`)

- **Source confrontée :** `https://cache.media.eduscol.education.fr/file/HG_Competences/11/4/RA16_C3C4_HIGE_Analyser_comprendre_document_819114.pdf`
- **Affirmation de la fiche (texte M.R.S.C.) :** Analyser deux documents demande d'identifier l'auteur, le contexte et les destinataires, puis de confronter des points de vue toujours partiels pour repérer informations complémentaires ou contradictoires.
- **Ancres cherchées (6) :** `auteur`, `contexte`, `destinataires`, `point de vue`, `partiel`, `contradictoires`
- **Ancres repérées :** `auteur`, `contexte`, `destinataires`, `point de vue`, `partiel`, `contradictoires`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** Ces termes méthodologiques généraux figurent dans la plupart des guides d'analyse documentaire ; leur présence ne prouve pas que la source couvre le cas précis d'une affiche et d'un carnet de notes fictifs.
- **Faux négatif documenté :** La fiche emploie le verbe « corroborer » dans ses notions, tandis que la ressource Éduscol parle de « croiser » et « confronter » les supports : chercher « corroborer » produirait un constat d'ancre absente.
- **Limite :** Cet indice ne remplace pas une relecture par une personne compétente en histoire et en éducation aux médias pour vérifier la formulation de l'exercice et de ses limites.

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

### `decrire-paysage-observation-ensembles-hypotheses` (`geo-decrire-paysage`)

- **Source confrontée :** `https://eduscol.education.fr/document/16804/download`
- **Affirmation de la fiche (texte M.R.S.C.) :** Décrire un paysage complète l'observation en identifiant les objets et les ensembles visibles avant de formuler des hypothèses ou de confronter d'autres documents pour interpréter.
- **Ancres cherchées (6) :** `observation`, `objets`, `ensembles`, `hypothèses`, `visible`, `interprétation`
- **Ancres repérées :** `observation`, `objets`, `ensembles`, `hypothèses`, `visible`, `interprétation`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** Les mots « observation », « hypothèses » et « interprétation » apparaissent dans des contextes historiques comme géographiques au sein du même document : leur seule présence ne prouve pas que le passage porte sur un paysage.
- **Faux négatif documenté :** La fiche distingue « élément naturel » et « aménagement », tandis que le document Éduscol 16804 emploie « objets », « ensembles » et « formes d'organisation » : chercher « aménagement » produirait un faux négatif lexical.
- **Limite :** Cet indice ne valide ni la description fictive de vallée ni la réserve sur l'accessibilité du pont, qui relèvent du choix éditorial de la fiche.

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

### `objet-connecte-local-distant-snt-23494` (`info-objet-connecte-local-distant`)

- **Source confrontée :** `https://eduscol.education.fr/document/23494/download`
- **Affirmation de la fiche (texte M.R.S.C.) :** Un système informatique embarqué exécute des algorithmes de contrôle reliant capteurs, interface homme-machine (IHM) sur l'objet ou déportée et actionneurs, tandis que la connexion réseau expose aussi aux enjeux de sûreté et de sécurité.
- **Ancres cherchées (7) :** `informatique embarquée`, `objets connectés`, `capteurs`, `actionneurs`, `interface homme-machine`, `sûreté`, `sécurité`
- **Ancres repérées :** `informatique embarquée`, `objets connectés`, `capteurs`, `actionneurs`, `interface homme-machine`, `sûreté`, `sécurité`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** Le programme de SNT regroupe sept thématiques dans un même PDF : les mots « réseau », « données » ou « sécurité » apparaissent aussi dans les chapitres sur Internet ou les réseaux sociaux sans concerner le programme embarqué d'un objet.
- **Faux négatif documenté :** La fiche oppose « fonctionnement local » et « liaison réseau » en cas de coupure d'Internet, tandis que le programme officiel parle de « système informatique embarqué », de « réseau local » et d'IHM « sur l'objet ou déportée ».
- **Limite :** Cet indice vérifie l'alignement terminologique avec le programme de SNT de seconde au 20 octobre 2026 ; il ne prouve pas que l'exercice de la prise programmable fictive a été relu par une personne compétente en systèmes embarqués.

### `situer-siecle-bornes-sans-an-zero` (`histoire-situer-siecle`)

- **Source confrontée :** `https://promenade.imcce.fr/fr/pages2/277.html`
- **Affirmation de la fiche (texte M.R.S.C.) :** Dans l'ère commune sans année zéro pour les historiens, le Ier siècle va de l'an 1 à l'an 100, le XXe de 1901 à 2000 et le XXIe commence en 2001.
- **Ancres cherchées (6) :** `1 avant J.-C.`, `an 1`, `an 100`, `1901`, `2000`, `2001`
- **Ancres repérées :** `1 avant J.-C.`, `an 1`, `an 100`, `1901`, `2000`, `2001`
- **Ancres absentes :** aucune
- **État du relevé (2026-10-20) :** `indice-concordant` — Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)
- **Faux positif documenté :** La même page de l'IMCCE présente aussi la notation algébrique des astronomes (Cassini, 1740) où l'an 1 avant J.-C. est appelé « année 0 » : la présence simultanée de « an 1 » et « année 0 » ne permet pas à un automate de savoir laquelle des deux conventions la fiche retient.
- **Faux négatif documenté :** La source de l'IMCCE écrit « XXème siècle » et « XXIème siècle » alors que la fiche M.R.S.C. typographie « XXe siècle » et « XXIe siècle » : une ancre portant sur « XXe siècle » échouerait sur cette variante orthographique.
- **Limite :** Cet indice vérifie la présence des bornes chronologiques de référence sur la page de l'IMCCE au 20 octobre 2026 ; il ne valide ni l'astuce mentale d'ajout de 1 au nombre de centaines ni l'exercice de la fiche.

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
