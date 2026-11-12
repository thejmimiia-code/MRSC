# Prospective des lacunes de contenu — combler sans faire semblant (horizon 2027)

**Note de travail du 6 novembre 2026. État : scénarios non tranchés, aucune décision prise au nom de l'association.** Cette note n'est ni une prévision, ni une étude de marché, ni une promesse de produit, ni une validation de contenu. Elle part d'une mesure du dépôt, de quatre pages externes ouvertes et lues ce jour, et de manques déjà consignés. Elle ne fabrique aucune demande d'usager, aucun profil de public et aucun avis d'expert.

Elle complète trois documents sans les remplacer : [`carte-lacunes.md`](carte-lacunes.md) pose l'exigence de preuve des sujets sans fiche, [`couverture-sujets.md`](couverture-sujets.md) qualifie les manques sujet par sujet, et [`decision-prospective.md`](decision-prospective.md) présente le brief d'atelier du 5 novembre 2026 dont la trace de décision reste vide. La note ancienne [`prospective-2027-2030.md`](prospective-2027-2030.md) reste une photographie datée d'octobre 2026.

## 1. Ce qui a été observé, et ce qui ne l'a pas été

Le 6 novembre 2026, la carte des lacunes comptait **6 sujets sans aucune fiche**, dont **3** portant le statut `revue-experte` : santé/sécurité du corps, droit et travail, premiers secours, activité physique et sécurité. Quatre cartes de sujet existaient déjà (`ecoute-prononciation`, `revenus-salaire-impots`, `securite-sciences`, `systemes-embarques`). Le portefeuille R&D affichait pourtant encore la phrase « Dix-sept sujets restent sans aucune fiche », héritée d'une revue du 20 octobre 2026 : **un décalage entre une prose de suivi et une mesure générée**, pas une couverture réelle. Ce décalage est corrigé dans [`portefeuille.toml`](portefeuille.toml) à l'occasion de ce lot, en gardant la date de la revue précédente visible.

Trois autres manques sont mesurables dans le catalogue : le repère 4 « Approfondir » ne comptait qu'une fiche avant ce lot ; aucun sujet ne porte la mention « Relu — relecture consignée » ; le registre [`relectures.toml`](../apprentissage/relectures.toml) ne contient aucune entrée. Le cap de 1 000 fiches de [`plan-1000.toml`](../apprentissage/plan-1000.toml) est une hypothèse de planification : il n'a jamais été une preuve de couverture, ni une autorisation de publier en masse.

**Ce lot n'a pas comblé les six sujets sans fiche.** Trois fiches ont été ajoutées sur trois sujets qui n'en avaient qu'une (`argumentation`, `probabilites-incertitude`, `tests-debogage`), au repère 3 ou 4, avec des exemples fictifs et vérifiables à la main. Elles portent toutes le statut « Prototype à relire ». C'est un essai de comblement *mesurable*, pas un comblement des manques sensibles : écrire une fiche de premiers secours ou de droit du travail sans relecture compétente serait précisément le geste que [`AGENTS.md`](../../AGENTS.md) interdit.

Un dernier décalage documentaire a été relevé sans être tranché : une fiche du corpus cite le fichier source de `statistics` épinglé à la version **v3.14.0** sur GitHub, tandis que la documentation vivante `docs.python.org/3/` affichait **3.15.2** lors de la consultation du 6 novembre 2026. Les deux adresses peuvent être légitimes ; elles ne documentent pas le même instant. **Arbitrage laissé à une personne compétente** : aucune des deux n'a été modifiée au passage, et aucune fiche nouvelle ne prétend les concilier.

## 2. Relevé mesuré, maintenu par une porte

Le bloc ci-dessous est **généré** depuis le catalogue, le référentiel, le registre des relectures, le plan et le portefeuille. Il est vérifié par `python3 outils/construire-couverture-sujets.py --verifier`. Un chiffre qui dérive fait échouer la porte au lieu de vieillir en silence dans une prose datée.

<!-- DEBUT RELEVE COUVERTURE -->

Relevé généré depuis le catalogue, le référentiel, le registre des relectures et le plan indicatif. Date de référence : revue de portefeuille du `2026-10-20`. Aucune donnée d'usage, aucune source externe, aucune projection de fréquentation.

| Mesure | Valeur | D'où vient le nombre |
| --- | ---: | --- |
| Fiches du catalogue | 108 | `catalogue.toml` |
| Prototypes à relire | 82 | statut éditorial partagé |
| Relectures humaines consignées | 0 | `relectures.toml` |
| Sujets du référentiel | 106 | `referentiel.toml` |
| Sujets sans aucune fiche | 6 | référentiel |
| Sujets à une seule fiche | 85 | référentiel × catalogue |
| Sujets sans repère 3 ou 4 | 87 | référentiel × catalogue |
| Sujets à créer sans carte de sujet | 0 | fichiers `sujet-*.md` |
| Fiches de repère 4 | 2 | `catalogue.toml` |
| Cap indicatif de fiches | 1000 | `plan-1000.toml` |
| Écart arithmétique au cap | 892 | cap moins fiches |

### Trois conséquences arithmétiques, pas trois prévisions

| Scénario de calcul | Ce que donne le relevé | Ce que le calcul ne dit pas |
| --- | --- | --- |
| A — Tenir le cap du nombre | 892 fiches manquantes ; à 3 fiches par lot, 298 lots ; si chaque nouvelle fiche reste un prototype, 974 prototypes à relire. | Ni le rythme réel, ni la disponibilité des relecteurs, ni l'utilité des fiches. |
| B — Relire d'abord | 82 prototypes en attente pour 0 relecture(s) consignée(s) ; le cap reste inchangé et aucune fiche nouvelle n'est nécessaire au calcul. | Le temps nécessaire, la compétence requise par domaine ni l'ordre des fiches. |
| C — Combler les manques mesurés | 6 sujets sans fiche, 85 sujets à une seule fiche, 87 sujets sans repère 3 ou 4, 0 carte(s) de sujet manquante(s). | Qu'un sujet est plus important qu'un autre, ni qu'une fiche comble son manque. |

Ces trois lignes sont des conséquences des seuls nombres du dépôt. Aucune probabilité, aucune échéance et aucune recommandation ne s'en déduit ; l'arbitrage reste à l'association.

<!-- FIN RELEVE COUVERTURE -->

## 3. Trois scénarios de travail, aucun recommandé

| Scénario | Ce qu'il fait travailler | Condition pour l'envisager | Signal mesurable, sans données d'usage | Ce qui resterait non résolu |
| --- | --- | --- | --- | --- |
| **S1 — Consolider d'abord** | Les prototypes déjà publiés et les quatre cartes de sujet existantes ; faire relire par domaine, puis ouvrir seulement les sujets dont la carte est prête. | Des personnes compétentes par domaine sont disponibles et acceptent de consigner leur revue. | Nombre d'entrées dans `relectures.toml` ; nombre de cartes de sujet ayant abouti à une fiche ; échéances de revue tenues. | Le cap de 1 000 recule ; les six sujets sans fiche restent sans fiche ; aucun effet d'apprentissage n'est mesuré. |
| **S2 — Étendre par couches successives** | Les sujets à une seule fiche et les repères 3 et 4 absents, en suivant le tri de [`couverture-sujets.md`](couverture-sujets.md) **sans** le traiter comme une priorité de personnes. | Une porte de non-régression existe, et chaque lot garde ses sources datées, ses droits et son statut « Prototype à relire ». | Manques mesurés avant/après chaque lot ; nombre de fiches par repère ; nombre de prototypes en attente. | La dette de relecture augmente plus vite que la couverture ; le risque de confondre « plus de fiches » et « mieux expliqué ». |
| **S3 — Tenir le cap du nombre** | La production de fiches jusqu'à 1 000, par lots réguliers. | Une décision explicite de l'association, une capacité de relecture connue et un arrêt possible. | Écart arithmétique au cap ; nombre de prototypes ; nombre de relectures consignées. | Rien ne dit que le nombre réponde à un besoin observé ; la qualité, l'accessibilité et la fraîcheur des sources restent entières. |

Ces scénarios ne sont pas mutuellement exclusifs et ne portent aucune probabilité. Le scénario S3 est écrit ici pour être **discutable**, pas pour être proposé : il est le plus exposé au risque de prendre un compte pour une couverture. Aucune échéance, aucun budget, aucun effectif et aucune attribution de rôle ne sont avancés.

## 4. Ce qu'il faudrait avant de combler les six sujets sans fiche

Pour chacun des six, la chaîne reste la même et n'a pas été franchie ici :

1. une **carte de sujet** datée, distincte de la fiche, avec le périmètre et les sujets voisins ;
2. des **sources primaires datées**, ouvertes et confrontées, avec leur licence et leur mode d'utilisation déclarés ;
3. une **relecture par une personne compétente** pour les domaines sensibles, consignée dans `relectures.toml` avec le rôle, le périmètre et les objections ;
4. une **décision de publication** de l'association, distincte de la relecture ;
5. une **date de revue** et un intervalle, pour que la fiche ne devienne pas une vérité sans date.

Aucune de ces cinq étapes n'est automatisable dans son jugement. Seules l'existence de la carte, la présence des métadonnées, la cohérence des statuts et la synchronisation des documents générés le sont — et c'est précisément le rôle du nouveau générateur.

## 5. Sources consultées le 6 novembre 2026

Ces pages ont été **ouvertes et lues** ce jour. Elles sont citées comme repères, sans reproduction de texte, de tableau, d'exemple ni d'illustration. Aucune d'elles ne valide la démarche pédagogique du M.R.S.C., ni l'utilité des fiches, ni une décision prospective.

| Page | Ce qui a été relevé | Limite explicite |
| --- | --- | --- |
| [`statistics` — documentation Python](https://docs.python.org/3/library/statistics.html) | Séparation entre résumés de position centrale et mesures de dispersion, et avertissement sur les valeurs manquantes qui perturbent tri et médiane. | Documentation technique vivante (`/3/`, version affichée 3.15.2) : ni version épinglée, ni preuve pédagogique, ni validation des exercices. |
| [`8. Errors and Exceptions` — tutorial Python](https://docs.python.org/3/tutorial/errors.html) | Distinction entre erreur de syntaxe et exception, rôle du contexte et de la dernière ligne d'un message d'erreur. | Spécifique à Python ; la trace et le programme de la fiche sont entièrement fictifs et originaux. |
| [`4. More Control Flow Tools` — tutorial Python](https://docs.python.org/3/tutorial/controlflow.html) | `if`/`elif`/`else`, `for`, `range()` à borne fin exclue, prudence sur la modification d'une collection pendant l'itération. | Page lue, **non retenue** pour une fiche dans ce lot : le catalogue possède déjà une entrée sur le sujet et aucune lacune nouvelle n'a été démontrée. |
| [« Le socle commun de connaissances, de compétences et de culture » — Éducation nationale](https://www.education.gouv.fr/le-socle-commun-de-connaissances-de-competences-et-de-culture-12512) | Repère institutionnel français, page datée du 19 février 2026, cycles 1 à 4, domaine 1 « langages pour penser et communiquer ». | Cadre scolaire français pour les 3–16 ans : ni validation universelle, ni preuve d'efficacité, ni avis sur une méthode. Le panneau de consentement aux cookies gêne l'extraction automatisée. |

**Droits :** aucune licence de reprise n'a été vérifiée ni demandée pour ces pages. Elles sont déclarées en `reference-factuelle` dans le catalogue : aucun extrait n'est reproduit, et les contenus des fiches nouvelles sont originaux et fictifs. La note elle-même ne contient aucune citation de ces pages.

## 6. Ce qui n'a pas été fait

- Aucun atelier avec l'association, aucun test avec des personnes, aucun échange avec un professionnel de santé, du droit ou de la sécurité.
- Aucune relecture humaine consignée ; les trois fiches nouvelles restent des prototypes.
- Aucune modification des statuts `a-creer` ou `revue-experte`, aucune fiche créée sur les six sujets sans fiche, aucune note de prospective présentée comme validée.
- Aucune collecte de données d'usage, aucune mesure d'audience, aucune prédiction de fréquentation.
- Aucune extension aux pages du simulateur, à la citation juridique ni au texte de `transparence.html`, qui relèvent d'un autre lot et restent en attente de relecture humaine.
- Aucune source externe nouvelle pour les domaines sensibles : leur comblement exigerait une recherche documentaire dédiée.

## 7. Trace de décision

**Décision : non tranchée.** Le brief du 5 novembre 2026 ([`decision-prospective.md`](decision-prospective.md)) reste « à décider par l'association ». La présente note ajoute un relevé mesuré, un instrument et trois scénarios ; elle ne choisit ni une option, ni un calendrier, ni un volume de fiches. Une décision ne sera consignée ici que si l'association l'a effectivement prise, avec sa date, son périmètre, son auteur par rôle et ses réserves.

Une fois qu'une personne aura tranché, cette section et le portefeuille R&D devront être mis à jour ensemble ; la porte `verifier-decision-prospective.py` refuse une trace vide présentée comme complète, comme une trace complète laissée en attente.
