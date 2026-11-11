# Relecture de contenu des 81 prototypes par l’agent — 10 novembre 2026

> **Suite du 11 novembre 2026.** Les 89 adresses uniques encore non ouvertes lors de cette passe ont été tentées : 83 premières tranches avec contenu, 3 pages d’erreur servies et 3 erreurs de récupération. Voir `docs/rd/sources-ouvertes-2026-11-11.md` et `docs/rd/sources-ouvertes-2026-11-11.toml`. Une seconde passe du même jour reprend les 6 adresses restées sans contenu : 3 retentatives, 16 pages officielles lues pour 5 d’entre elles, 1 toujours sans page lue, aucun changement de fiche. Voir `docs/rd/sources-complement-2026-11-11.md`. Une troisième passe retente l’accueil IGN (13 réponses HTTP 403) et lit 10 pages officielles de l’IGN sur `cartes.gouv.fr` et `data.geopf.fr`, confrontées aux deux fiches de géographie sans les modifier. Voir `docs/rd/sources-ign-2026-11-11.md`. Les chiffres ci-dessous restent l’instantané du 10 novembre 2026, pas un état courant.

**Auteur :** agent. **État :** relecture de contenu exécutée et consignée, aucune validation humaine, aucune promotion de statut.
**Registre :** `docs/rd/relecture-agent-prototypes.toml` (81 entrées datées). **Porte :** `outils/relecture-agent-prototypes.py --verifier`. **Banc :** `outils/test_mutations_relecture_agent_prototypes.py`.

## 1. Le cadrage corrigé

La consigne du 10 novembre 2026 est « la relecture c’est toi qui doit la faire ». Elle rejoint la règle déjà écrite dans `docs/protocole-editorial.md` (§ « Relecture par agent », 7 novembre) et dans `docs/rd/relecture-automatique.md` : **la lecture du contenu et la vérification des sources appartiennent à l’agent**, la personne garde le contrôle du rendu à l’œil — placement, style, construction — et n’a aucun registre à lire pour valider. La réponse précédente et `docs/rd/plan-complet-rd-innovation-prospective.md` présentaient à tort cette lecture comme une porte humaine à ouvrir ; le plan est corrigé dans ce lot.

Ne pas confondre avec les portes distinctes qui restent ouvertes : expertise compétente du domaine, avis juridique, essai avec des personnes, décision associative, validation visuelle. Ce ne sont pas des lectures de milliers de lignes confiées à la personne, ce sont des actes que le dépôt ne peut pas fabriquer. Aucune n’est franchie ici.

La lecture est **systématique**, pas un coup d’œil : les 81 entrées de `docs/apprentissage/catalogue.toml` ont été parcourues champ par champ, et `outils/relecture-agent-prototypes.py` refuse qu’un des onze champs soit absent, vide, de type inattendu ou encore marqué « à compléter ». Son banc de 10 mutations plante cette faute-là aussi et exige qu’elle soit nommée.

## 2. Ce qui a été réellement relu

| Élément | Mesure | Comment |
| --- | ---: | --- |
| Prototypes lus | 81 / 81 | `docs/apprentissage/catalogue.toml`, source de vérité des fiches ; pages HTML générées confrontées par `outils/construire-apprentissages.py --verifier`. |
| Champs lus par fiche | 11 | objectif, situation, analogie, limite de l’analogie, notions, démarche, exercice, aide, correction, points à retenir, transfert ; présence, type et non-vacuité contrôlés pour les 81 fiches par `outils/relecture-agent-prototypes.py`. |
| Contrôles mécaniques | 17 × 81 | `outils/auditer-prototypes.py --verifier` : 81 fiches sans échec mécanique, 0 échec, 1 constat nommé (`arts-composer-formes`, portail assumé par écrit). |
| Expressions arithmétiques simples recalculées | 20 | Dans les énoncés, aides et corrections ; **0 écart**. 32 égalités exclues du calcul parce qu’elles sont des chaînes de réécriture, des expressions entre parenthèses ou des égalités algébriques avec inconnue. |
| Sources déclarées | 138 déclarations, 105 adresses uniques | Aucune URL nouvelle, aucune source inventée. |
| Pages de source ouvertes le 10 novembre 2026 | 17 | 16 adresses déclarées par 27 prototypes, plus 1 source primaire du registre d’apparences (W3C / WAI, contraste minimum). **89 adresses uniques non ouvertes** lors de cette passe. |
| Liens morts dans l’échantillon | 0 | Les 17 pages ont répondu ; une redirection a été constatée. |
| Erreurs factuelles corrigées dans les fiches | 0 | Aucune contradiction repérée entre les extraits consultés et les affirmations des fiches. **Le catalogue et les 107 pages générées sont inchangés.** |
| Fiches marquées « à trancher » | 40 | Constats de source, de version ou de domaine sensible, détaillés au §4. |
| Fiches sans écart détecté dans le périmètre relu | 41 | Le verdict `relue-sans-ecart` ne veut pas dire « conforme » : ce vocabulaire appartient au registre humain. |

## 3. Sources ouvertes et confrontées

Les adresses exactes restent dans `docs/apprentissage/catalogue.toml` ; ce tableau les nomme sans les recopier pour ne pas figer une URL de plus.

| Organisme et page | Repère observé | Ce que la page confirme |
| --- | --- | --- |
| CNIL, accueil | Actualités du 10 novembre 2026 | Portail général ; aucun passage précis sur « données personnelles et bons réflexes numériques ». |
| Guides de data.gouv.fr, « Comprendre un indicateur » | Page servie | Libellé, périmètre, unité, maille, date de mise à jour, licence, sources d’un indicateur. L’adresse déclarée, avec son segment répété, répond aujourd’hui. |
| Python, documentation `statistics` | « Python 3.15.2 documentation » | Sections *Averages and measures of central location* et *Measures of spread* ; les titres des fiches qui citent 3.15.2 sont exacts à cette date. |
| ameli, « Prévenir les chutes des personnes âgées » | 24 décembre 2024 | « Une personne sur trois » parmi les plus de 65 ans ; dégager les passages, éclairer, fixer les appuis. |
| Service Public, fiche F1427 | Vérifiée le 14 août 2026 | Gratuité, mairie du lieu de naissance pour une naissance en France, trois formes d’acte, service en ligne dédié pour une naissance à l’étranger. |
| Cybermalveillance.gouv.fr, sauvegardes | Page servie | Déconnexion du support après usage et test des sauvegardes au sommaire. |
| Météo-France, « Quelle différence entre météo et climat ? » | 22 mars 2026 | Météo à court terme, climat en moyenne sur plusieurs décennies, période de référence de 30 ans. |
| Éducation nationale, socle commun | 19 février 2026 | Cinq domaines et quatre cycles ; la page citée par sept fiches existe et porte ce titre. |
| DGCCRF, accueil de la direction | Actualités 2026 | Portail de direction ; aucune page précise sur un prix unitaire ou une mention de garantie. |
| INRS, prévention du risque électrique | Page servie | Champ du Code du travail et des installations professionnelles. |
| Santé publique France, taux de participation au dépistage | 30 avril 2024 | 50 à 74 ans, invitation tous les deux ans, examen clinique, mammographie, deuxième lecture des clichés normaux. L’adresse déclarée **redirige** vers un chemin plus court. |
| France Compétences, Vademecum | Janvier 2026 | Sommaire sur RNCP, certificateur, niveau de qualification et blocs de compétences. |
| Service Public, accueil | JORF et fiches du jour | Portail d’information officielle ; aucun passage précis. |
| ameli, « Consultations en métropole : vos remboursements » | 2 octobre 2026 | 70 % du tarif conventionnel dans le parcours, remboursement moins favorable hors parcours. |
| INRS, dossier d’étiquetage CLP | Page servie | Neuf pictogrammes, mentions d’avertissement, mentions de danger, conseils de prudence. |
| Légifrance, accueil | JORF du 10 novembre 2026 | Service public de diffusion du droit, recherche par fonds. |
| W3C / WAI, *Understanding SC 1.4.3* | WCAG 2.2 | Seuils 4,5:1 et 3:1, absence d’arrondi ; l’extrait mis en cache dans `docs/rd/sources-primaires/` concorde. |

Aucune des 17 pages ne contredit une affirmation des fiches qui la cite. Une ouverture de page ne prouve pas la vérité du monde : elle confronte un texte à un autre texte, à une date écrite.

## 4. Constats nommés, pas des erreurs

Le registre consigne **40 fiches `a-trancher`** et **41 `relue-sans-ecart`**. Les objections sont des faits exacts qu’un programme ne peut pas juger :

- **28 fiches** déclarent au moins une source qui est une page d’accueil (38 déclarations, 19 adresses racines). Aucun passage précis n’est confrontable. Les fiches le disent déjà dans leur champ `utilisation` ; la question reste de savoir si ce renvoi suffit.
- **3 fiches** (`maths-comparer-deux-releves`, `prog-comparer-langages`, `prog-lire-trace-erreur`) citent l’alias mouvant `docs.python.org/3/` : son contenu suit la version courante sans que l’URL change. Une seule de ces trois pages a été ouverte lors de cette passe ; les titres qui figent « 3.15.2 » sont exacts le 10 novembre 2026, pas garantis ensuite.
- **1 fiche** (`sante-comprendre-depistage-organise`) cite une adresse de Santé publique France qui redirige ; la page est servie, l’URL mériterait d’être mise à jour.
- **1 fiche** (`tech-circuit-ouvert-ferme`) s’appuie sur une page INRS de prévention en milieu professionnel pour un circuit simple d’apprentissage : l’adéquation reste à apprécier, le lien n’est pas faux.
- **14 fiches** des domaines santé, droit et démarches, argent, politique publique exigent une expertise compétente avant toute promotion. Leur relecture de contenu par agent ne la remplace pas.
- **1 constat mécanique** déjà nommé par `outils/auditer-prototypes.py` : `arts-composer-formes` ne cite qu’un portail et l’assume par écrit.

Aucun de ces constats n’a été transformé en correction silencieuse. Aucune note, aucun score, aucun ordre de valeur entre fiches.

## 5. Ce que ce lot corrige

- **Une erreur de cadrage**, pas une erreur de contenu : `docs/rd/plan-complet-rd-innovation-prospective.md`, `docs/rd/relecture-automatique.md`, `docs/apprentissage/grille-relecture.md` et `docs/rd/journal.md` disent désormais que la relecture de contenu et la vérification des sources sont exécutées par l’agent. La réponse précédente les présentait à tort comme une porte à attribuer.
- **La dette de relecture de fond** : les 81 pages de fiches passent de `reference-initiale` à `relu-par-agent` dans `docs/rd/empreintes-contenus.toml`, avec une `[[edition]]` datée par fichier dans `docs/rd/editions-relecture.toml`, un constat et une limite propres. La dette initiale consignée passe de 473 à **391 unités**.
- **Aucune fiche, aucun catalogue, aucun statut éditorial, aucune page HTML, CSS ou JavaScript n’est modifié.** `docs/apprentissage/relectures.toml` reste vide : c’est le registre des seules relectures humaines, un agent n’y écrit pas.

## 6. Limites

Cette relecture ne couvre pas : l’expertise du domaine, un avis juridique, un essai avec des personnes, la validation du rendu à l’œil, la performance réseau, l’usage réel, l’effet d’apprentissage, la vérité des pages sources, ni les **89 adresses uniques non ouvertes**. Elle ne juge pas de la licence ou de la titularité des droits, ne vérifie pas qu’un texte a été repris sans autorisation, et ne transforme pas un prototype en contenu validé. Les 20 calculs recalculés portent sur des égalités simples ; les expressions entre parenthèses, les chaînes de réécriture et les égalités algébriques ont été écartées, pas vérifiées par ce calcul. Les chiffres de ce rapport sont un instantané du 10 novembre 2026.

## 7. Portes qui restent ouvertes

Expertise compétente sur les 14 fiches de domaines sensibles ; avis juridique sur les questions de droit et de vote ; essais volontaires ; validation visuelle du rendu ; décision de l’association sur la publication et les priorités ; revue du portefeuille du 2026-11-19 ; décision prospective avant le 31 janvier 2027 ; DNS `www.mrsc.fr` ; mise à jour du moteur du simulateur. Aucune n’est franchie par ce lot, et aucune ne consiste à demander à la personne de lire ce registre à la place de l’agent.

## 8. Reproduire

```
python3 outils/relecture-agent-prototypes.py --verifier
python3 outils/test_mutations_relecture_agent_prototypes.py
python3 outils/auditer-prototypes.py --verifier
python3 outils/construire-apprentissages.py --verifier
python3 outils/relire-contenus.py
python3 outils/verifier-plan-complet.py
```

`outils/relecture-agent-prototypes.py --consigner` écrit les 81 `[[edition]]` et met à jour le manifeste ; il refuse d’agir si la porte `--verifier` échoue ou si `MRSC_RACINE` désigne une copie de banc.
