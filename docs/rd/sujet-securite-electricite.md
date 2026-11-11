# Carte de sujet — Sécurité électrique, protections et limites des interventions

**Statut : cadrage interne, sans fiche.** Cette carte ouvre le sujet `sciences-techniques-environnement` → `securite-electricite` (`statut = revue-experte`) du référentiel. Elle ne contient **aucune fiche d’apprentissage**, **aucune consigne de sécurité**, **aucun conseil médical**, **aucune règle de droit**, **aucune source externe nouvelle** et **aucune URL**. Elle est rédigée par un agent le 11 novembre 2026, sans relecture experte, sans essai avec des personnes et sans validation éditoriale.

**Porte inchangée :** relecture par une personne experte du sujet, puis sources primaires datées ; `revue-experte` reste affiché. Une carte de cadrage n’est pas une fiche : elle ne lève aucune exigence de relecture compétente et ne modifie ni le référentiel, ni le catalogue, ni `docs/apprentissage/relectures.toml`.

## 1. Identité

| Dimension | Contenu |
| --- | --- |
| Sujet du référentiel | `sciences-techniques-environnement` → « Sécurité électrique, protections et limites des interventions » (`statut = revue-experte`) |
| Ce dont il s’agit | Délimiter, avant toute rédaction, la question que le sujet devrait traiter, les frontières avec les sujets voisins et la forme d’une première activité observable. |
| Ce dont il ne s’agit pas | Ni une fiche publiée, ni un objectif d’apprentissage arrêté, ni une preuve de besoin chez les visiteurs, ni une source de vérité sur le domaine. |
| Fiches reliées | 0, mesuré par `docs/rd/couverture-sujets.md` et `docs/rd/carte-lacunes.md`. |

## 2. Besoin observé dans le dépôt uniquement

Le besoin est **interne et mesurable** : le référentiel déclare ce sujet sans aucune fiche, et `docs/rd/couverture-sujets.md` y relevait le manque `sans-carte-de-sujet`. Six sujets du référentiel sont sans fiche ; quatre d’entre eux n’avaient pas encore de carte de cadrage. Ce lot écrit ces quatre cartes, sans en déduire une priorité éditoriale.

Aucune observation d’usage, aucune donnée d’audience, aucun retour de volontaire et aucune mesure d’apprentissage n’existe dans le dépôt pour ce sujet. **Le besoin d’une fiche reste à démontrer**, pas à présupposer.

## 3. Portée proposée, à confirmer avant rédaction

**Dedans (hypothèse de cadrage) :** repérer, dans un texte de consigne fictif, qui est habilité, quel équipement est nommé et quelle action est explicitement interdite ; distinguer la lecture d’une consigne de l’exécution d’un geste.

**Dehors (frontières explicites) :** toute intervention sur un circuit, un appareil ou une installation sous tension ; toute habilitation, tout dépannage, tout diagnostic de matériel et toute conduite d’urgence. Les gestes de premiers secours relèvent d’un autre sujet, également en `revue-experte`.

**Limite de contexte :** le cadrage vaut pour le corpus M.R.S.C. en français, sans région, réglementation ou langue particulière arrêtée. Toute transposition demandera une relecture locale et compétente.

## 4. Relations avec les sujets voisins

| `securite-sciences` (`a-creer`, carte existante) | Y est déjà écrit que l’habilitation électrique ne doit pas figurer dans une fiche sur l’étiquetage des produits : la frontière reste valable. |
| `premiers-secours` (`revue-experte`, carte écrite dans ce lot) | Conduites d’urgence : strictement hors de ce sujet. |
| `systemes-embarques` (carte existante) | Un objet connecté peut être alimenté ; la carte de ce sujet parle du programme et de la mesure, pas de la sécurité de l’alimentation. |

Ces liens sont des **frontières de rédaction**, pas des équivalences de contenu : une carte ne dit pas ce que dira la fiche.

## 5. Preuve — sources internes uniquement

| Fichier interne | Ce qu’il établit | Ce qu’il n’établit pas |
| --- | --- | --- |
| `docs/apprentissage/referentiel.toml` | Le sujet existe, son statut et l’absence de fiche reliée. | Qu’une fiche est souhaitable, exacte ou prioritaire. |
| `docs/apprentissage/catalogue.toml` | 107 fiches déclarées, dont 81 prototypes à relire et 0 fiche marquée relue. | Que ce sujet doit rejoindre le catalogue sans porte de relecture. |
| `docs/rd/carte-lacunes.md` | Les six sujets sans fiche et l’exigence de preuve affichée pour chacun. | Une expertise de domaine ou une décision de publication. |
| `docs/rd/couverture-sujets.md` | Les manques mesurés, sujet par sujet, dont `sans-carte-de-sujet`. | Une qualité éditoriale ou un ordre d’importance. |
| `AGENTS.md` | La distinction besoin / fait / hypothèse / proposition, la porte de relecture compétente et l’interdiction de fabriquer un résultat d’essai. | Une autorisation de publier ou de promouvoir un statut. |

**Aucune source externe n’a été ouverte pour cette carte.** Aucun fait de droit, de santé, de sécurité ou de pratique professionnelle n’y est avancé. Les sources primaires datées devront être lues, confrontées et consignées avant toute fiche.

## 6. Hypothèse de forme, non construite

Une fiche entièrement textuelle pourrait demander de classer, dans une consigne fictive, les énoncés qui décrivent une interdiction, une condition d’habilitation et une limite de matériel, sans jamais demander d’agir. Le repli serait une lecture seule, sans manipulation, sans image imposée et sans simulation de courant.

Il s’agit d’une **proposition de conception**, pas d’un prototype livré. Trois options restent ouvertes, dont « ne pas construire » : garder le sujet ouvert et consacrer le temps disponible à la relecture des 81 prototypes existants. Le critère d’arrêt serait défini avant tout essai : si la porte de relecture compétente n’est pas réunie, aucune fiche n’est rédigée.

## 7. Statut et entretien

- **Statut du sujet :** reste `revue-experte` dans `docs/apprentissage/referentiel.toml`. Aucune fiche n’est ajoutée au catalogue, aucun statut promu, aucune relecture humaine consignée.
- **Porte avant publication :** relecture par une personne experte du sujet, puis sources primaires datées ; `revue-experte` reste affiché.
- **Prochaine action de l’agent :** consigner, avant toute rédaction, les sources primaires réellement lues avec leur date, leur repère et leur limite ; tenir cette carte à jour si le référentiel change.
- **Prochaine action qui n’est pas à l’agent :** réunir la relecture compétente, puis décider éditorialement de l’ouverture d’une fiche.

## 8. Limites

Cette carte ne juge pas la vérité du domaine, ne remplace pas une expertise, ne confirme aucun droit applicable, ne donne aucune conduite à tenir et ne prouve aucun bénéfice d’apprentissage. Elle ne vaut ni validation humaine, ni avis juridique, ni essai volontaire, ni rendu visuel validé. Elle n’est pas publiée sur le site : elle vit sous `docs/rd/`, comme document de travail daté. Un contrôle vert sur cette carte dirait seulement qu’un fichier existe et que les gardes internes sont cohérentes.
