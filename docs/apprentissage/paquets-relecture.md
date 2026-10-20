# Paquets de relecture des prototypes

**Document de travail généré.** Il rassemble ce qu’une personne doit avoir sous les yeux pour trancher un prototype : ses sources telles qu’elles sont enregistrées, les droits déclarés, les limites que la fiche affirme déjà, et une trace de décision à remplir. Il ne relit rien, ne note rien et ne valide rien : aucun champ n’est une évaluation.

Le tri reprend les deux règles de la [file de relecture](file-relecture.md) : domaine à relecture spécialisée, puis mots-clés repérés dans les champs éditoriaux. Ces signaux restent une heuristique, corrigeable par une personne.

## 0. Comment enregistrer une relecture, en trois gestes

1. Ouvrir le paquet de la fiche, lire ses sources et ses limites, puis trancher avec la [grille de relecture](grille-relecture.md).
2. Coller le bloc `[[relecture]]` du paquet à la fin de [`relectures.toml`](relectures.toml) et le compléter (date réelle, rôle, périmètre, verdict, objections).
3. Lancer `python3 outils/registre-relecture.py`. Le contrôle refuse une date future, un verdict inconnu, un verdict négatif sans objection, et tout statut du catalogue qui ne correspondrait pas au registre.

Un verdict « conforme » fait passer la fiche au statut « Relu — relecture consignée » — à condition de le faire dans `catalogue.toml`, sinon le contrôle échoue. Ni le script ni ce document ne relisent : ils enregistrent.

## 1. Ordre de passage proposé

| Priorité | Signification | Prototypes |
| ---: | --- | ---: |
| 1 | domaine exigeant une personne compétente du domaine | 9 |
| 2 | hors domaine sensible, mais mots-clés à vérifier | 9 |
| 3 | aucun signal automatique — reste à relire | 39 |
|  | **Total des prototypes** | **57** |

Les 18 paquets détaillés ci-dessous couvrent les priorités 1 et 2. Les autres prototypes apparaissent dans le tableau et se détaillent avec `--fiche <identifiant>`.

## 2. Tableau de suivi

| # | Fiche | Domaine | Priorité | Sources | Droits déclarés | Revue prévue le | Relecture consignée |
| ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 1 | [Choisir une source publique adaptée à sa question](fiches/civ-choisir-source-publique.html) | Citoyenneté, médias et information | 1 | 6 | 6 non vérifiée(s) | 2026-10-08 | aucune |
| 2 | [Repérer l’échelle d’une institution avant de chercher le bon service](fiches/civ-reperer-echelle-institution.html) | Citoyenneté, médias et information | 1 | 2 | 2 non vérifiée(s) | 2026-10-15 | aucune |
| 3 | [Repérer une information électorale officielle](fiches/civ-reperer-info-electorale.html) | Citoyenneté, médias et information | 1 | 2 | 2 non vérifiée(s) | 2026-10-15 | aucune |
| 4 | [Trouver un service public et préparer un formulaire](fiches/civ-trouver-service-public.html) | Démarches, droits, sécurité et vie professionnelle | 1 | 3 | 3 non vérifiée(s) | 2026-10-15 | aucune |
| 5 | [Comparer deux prix à quantité égale](fiches/econ-comparer-prix-unitaires.html) | Budget, économie, consommation et travail | 1 | 2 | 2 non vérifiée(s) | 2026-10-11 | aucune |
| 6 | [Distinguer un intérêt d’un frais sur un crédit fictif](fiches/econ-distinguer-interet-frais.html) | Budget, économie, consommation et travail | 1 | 3 | 3 non vérifiée(s) | 2026-10-15 | aucune |
| 7 | [Lire une facture et repérer une échéance](fiches/econ-lire-facture.html) | Budget, économie, consommation et travail | 1 | 2 | 2 non vérifiée(s) | 2026-10-11 | aucune |
| 8 | [Lire une mention de garantie sur un ticket fictif](fiches/econ-lire-mention-garantie.html) | Budget, économie, consommation et travail | 1 | 2 | 2 non vérifiée(s) | 2026-10-15 | aucune |
| 9 | [Repérer une source de santé publique avant d’agir](fiches/sante-reperer-source-publique.html) | Santé, alimentation, corps et sécurité | 1 | 3 | 3 non vérifiée(s) | 2026-10-15 | aucune |
| 10 | [Lire une étude sans confondre résultats et certitudes](fiches/recherche-lire-etude.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 2 | 1 | aucune à vérifier | 2026-10-08 | aucune |
| 11 | [Formuler une question et une hypothèse de recherche](fiches/recherche-question-hypothese.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 2 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 12 | [Lire une frise chronologique et ordonner des événements](fiches/histoire-lire-frise.html) | Histoire, chronologie et mémoire | 2 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 13 | [Repérer les parties d’une adresse Web](fiches/info-lire-adresse-web.html) | Informatique, algorithmique et langages de programmation | 2 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 14 | [Lire une licence avant de réutiliser un programme](fiches/prog-lire-licence-logiciel.html) | Informatique, algorithmique et langages de programmation | 2 | 2 | 2 non vérifiée(s) | 2026-10-15 | aucune |
| 15 | [Présenter une idée avec une raison et un exemple](fiches/fr-argumenter-avec-exemple.html) | Français, lecture, écriture et communication | 2 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 16 | [Repérer l’idée principale et les informations utiles](fiches/fr-reperer-idee-texte.html) | Français, lecture, écriture et communication | 2 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 17 | [Formuler une recherche sur le Web](fiches/numerique-formuler-recherche.html) | Numérique, données, cybersécurité et intelligence artificielle | 2 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 18 | [Nommer et retrouver ses fichiers sans exposer ses données](fiches/numerique-organiser-fichiers.html) | Numérique, données, cybersécurité et intelligence artificielle | 2 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 19 | [Composer une image avec quelques formes](fiches/arts-composer-formes.html) | Arts, musique, création et culture | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 20 | [Lire une notice d’œuvre en séparant faits et interprétations](fiches/arts-lire-cartel.html) | Arts, musique, création et culture | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 21 | [Garder la trace d’une source pour la retrouver](fiches/recherche-conserver-reference.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 22 | [Distinguer un résumé et une citation sur une fiche fictive](fiches/recherche-distinguer-resume-citation.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 3 | 3 | 3 non vérifiée(s) | 2026-10-15 | aucune |
| 23 | [Décrire un paysage sans lui faire dire trop](fiches/geo-decrire-paysage.html) | Géographie, territoire et espace | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 24 | [Lire une légende sur une carte](fiches/geo-lire-legende-carte.html) | Géographie, territoire et espace | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 25 | [S’orienter avec les points cardinaux](fiches/geo-points-cardinaux.html) | Géographie, territoire et espace | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 26 | [Comparer deux sources sur un même événement](fiches/histoire-comparer-sources.html) | Histoire, chronologie et mémoire | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 27 | [Repérer l’échelle d’un événement : un lieu de France ou plusieurs pays](fiches/histoire-reperer-echelle-france-monde.html) | Histoire, chronologie et mémoire | 3 | 2 | 2 non vérifiée(s) | 2026-10-15 | aucune |
| 28 | [Situer une année dans un siècle](fiches/histoire-situer-siecle.html) | Histoire, chronologie et mémoire | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 29 | [Comprendre les bits et les octets](fiches/info-bits-octets.html) | Informatique, algorithmique et langages de programmation | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 30 | [Comprendre les rôles d’un ordinateur](fiches/info-ordinateur-fonctions.html) | Informatique, algorithmique et langages de programmation | 3 | 1 | 1 non vérifiée(s) | 2026-10-08 | aucune |
| 31 | [Comprendre le rôle d’un système d’exploitation](fiches/info-systeme-exploitation.html) | Informatique, algorithmique et langages de programmation | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 32 | [Distinguer une table, une requête et une page Web](fiches/info-table-requete-web.html) | Informatique, algorithmique et langages de programmation | 3 | 2 | 2 non vérifiée(s) | 2026-10-15 | aucune |
| 33 | [Un même algorithme, plusieurs langages : Python et JavaScript](fiches/prog-comparer-langages.html) | Informatique, algorithmique et langages de programmation | 3 | 3 | 3 non vérifiée(s) | 2026-10-08 | aucune |
| 34 | [Tester un programme avec des cas simples](fiches/prog-tester-exemples.html) | Informatique, algorithmique et langages de programmation | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 35 | [Comprendre un mot grâce à son contexte](fiches/fr-comprendre-mot-contexte.html) | Français, lecture, écriture et communication | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 36 | [Lire la ponctuation pour comprendre une phrase](fiches/fr-lire-ponctuation.html) | Français, lecture, écriture et communication | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 37 | [Préparer une explication courte](fiches/fr-preparer-explication-orale.html) | Français, lecture, écriture et communication | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 38 | [Demander de l’aide ou une répétition en anglais](fiches/langue-anglais-demander-aide.html) | Langues étrangères et interculturel | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 39 | [Demander comment épeler un mot en anglais](fiches/langue-anglais-epeler.html) | Langues étrangères et interculturel | 3 | 2 | 2 non vérifiée(s) | 2026-10-11 | aucune |
| 40 | [Prononcer la fin -ed des verbes anglais](fiches/langue-anglais-prononcer-ed.html) | Langues étrangères et interculturel | 3 | 2 | 2 non vérifiée(s) | 2026-10-20 | aucune |
| 41 | [Lire « th » dans un dictionnaire : /θ/ ou /ð/ ?](fiches/langue-anglais-prononcer-th.html) | Langues étrangères et interculturel | 3 | 6 | 6 non vérifiée(s) | 2026-10-20 | aucune |
| 42 | [Reconnaître un mot que tu connais déjà sur une affiche bilingue](fiches/langue-reperer-mot-deja-connu.html) | Langues étrangères et interculturel | 3 | 3 | 3 non vérifiée(s) | 2026-10-15 | aucune |
| 43 | [Convertir des mesures sans changer leur quantité](fiches/maths-convertir-unites.html) | Mathématiques, mesures et données | 3 | 2 | 2 non vérifiée(s) | 2026-10-08 | aucune |
| 44 | [Résoudre une équation simple en gardant l’égalité](fiches/maths-equation-simple.html) | Mathématiques, mesures et données | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 45 | [Estimer un résultat pour vérifier un calcul](fiches/maths-estimer-calcul.html) | Mathématiques, mesures et données | 3 | 1 | 1 non vérifiée(s) | 2026-10-08 | aucune |
| 46 | [Lire les graduations d’un graphique](fiches/maths-lire-echelle-graphique.html) | Mathématiques, mesures et données | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 47 | [Lire une information à l’intersection d’un tableau](fiches/maths-lire-tableau-croise.html) | Mathématiques, mesures et données | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 48 | [Comprendre une moyenne comme un partage égal](fiches/maths-moyenne.html) | Mathématiques, mesures et données | 3 | 1 | 1 non vérifiée(s) | 2026-10-08 | aucune |
| 49 | [Comprendre une chance dans un tirage simple](fiches/maths-probabilite-tirage.html) | Mathématiques, mesures et données | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 50 | [Repérer un angle droit](fiches/maths-reperer-angle-droit.html) | Mathématiques, mesures et données | 3 | 2 | 2 non vérifiée(s) | 2026-10-11 | aucune |
| 51 | [Reformuler une demande avant de commencer](fiches/methodes-demander-clarification.html) | Apprendre à apprendre, autonomie et relations | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 52 | [Calculer une vitesse moyenne simple](fiches/sciences-calculer-vitesse-moyenne.html) | Sciences, technologie et environnement | 3 | 2 | 2 non vérifiée(s) | 2026-10-11 | aucune |
| 53 | [Repérer les grandes étapes de vie d’une plante à fleurs](fiches/sciences-cycle-vie-plante.html) | Sciences, technologie et environnement | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 54 | [Distinguer fusion et dissolution](fiches/sciences-distinguer-melange-changement-etat.html) | Sciences, technologie et environnement | 3 | 1 | 1 non vérifiée(s) | 2026-10-11 | aucune |
| 55 | [Distinguer météo et climat](fiches/sciences-meteo-climat.html) | Sciences, technologie et environnement | 3 | 2 | 2 non vérifiée(s) | 2026-10-11 | aucune |
| 56 | [Comprendre un circuit électrique ouvert ou fermé](fiches/tech-circuit-ouvert-ferme.html) | Sciences, technologie et environnement | 3 | 2 | 2 non vérifiée(s) | 2026-10-08 | aucune |
| 57 | [Distinguer capteur, commande et action dans un objet électronique](fiches/tech-electronique-capteur.html) | Sciences, technologie et environnement | 3 | 1 | 1 non vérifiée(s) | 2026-10-08 | aucune |

## 3. Paquets détaillés

### `civ-choisir-source-publique` — Choisir une source publique adaptée à sa question

| Élément | Valeur |
| --- | --- |
| Domaine | Citoyenneté, médias et information |
| Repère de difficulté | 2 |
| Horizon du contenu | Démarches, vie citoyenne et lecture critique ; références françaises modulables selon le sujet |
| Priorité de tri | 1 — domaine à relecture spécialisée — politique publique, médias et information |
| Termes repérés | droit et démarches : juridique |
| Fiche publiée | [lire la fiche](fiches/civ-choisir-source-publique.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Service-Public.fr — information officielle sur les droits et démarches](https://www.service-public.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |
| [Légifrance — diffusion du droit français](https://www.legifrance.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |
| [data.gouv.fr — plateforme de données publiques françaises](https://www.data.gouv.fr/) | Non vérifiée — les conditions varient selon les ressources ; aucune donnée réutilisée | reference-factuelle | 2026-10-08 |
| [INSEE — Institut national de la statistique et des études économiques](https://www.insee.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |
| [data.gouv.fr — « Licences de réutilisation »](https://www.data.gouv.fr/pages/legal/licences) | Non vérifiée — page consultée ; aucune réutilisation déclarée | reference-factuelle | 2026-10-20 |
| [Vie-publique.fr — repères sur les institutions et politiques publiques](https://www.vie-publique.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |

**Ce que la fiche dit déjà de ses limites**

> Un site officiel n’est pas un guichet qui garantit une réponse personnalisée : sa page peut être ancienne, limitée à un territoire ou simplifier une situation. Une statistique, un texte de loi et un commentaire éditorial demandent des vérifications différentes.

**Points à trancher par une personne**

- [ ] Ouvrir les 6 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 6 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "civ-choisir-source-publique"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `civ-reperer-echelle-institution` — Repérer l’échelle d’une institution avant de chercher le bon service

| Élément | Valeur |
| --- | --- |
| Domaine | Citoyenneté, médias et information |
| Repère de difficulté | 2 |
| Horizon du contenu | Repères généraux sur les échelles publique en France ; les compétences exactes varient selon le sujet, le territoire et la date |
| Priorité de tri | 1 — domaine à relecture spécialisée — politique publique, médias et information |
| Termes repérés | droit et démarches : juridique ; politique publique : collectivité |
| Fiche publiée | [lire la fiche](fiches/civ-reperer-echelle-institution.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Vie publique — les fiches sur les institutions](https://www.vie-publique.fr/fiches) | Non vérifiée — lien documentaire ; aucune fiche n’est reprise | reference-factuelle | 2026-10-15 |
| [Service-Public — accueil d’information officielle sur les droits et démarches](https://www.service-public.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-15 |

**Ce que la fiche dit déjà de ses limites**

> Un bâtiment a des étages stables ; les compétences publiques se chevauchent, changent et dépendent du territoire. L’Union européenne n’est pas « un étage au-dessus de la France » pour tout sujet. Cette analogie n’enseigne ni organigramme ni procédure.

**Points à trancher par une personne**

- [ ] Ouvrir les 2 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 2 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "civ-reperer-echelle-institution"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `civ-reperer-info-electorale` — Repérer une information électorale officielle

| Élément | Valeur |
| --- | --- |
| Domaine | Citoyenneté, médias et information |
| Repère de difficulté | 2 |
| Horizon du contenu | Lecture d’informations publiques en France ; les dates, listes et modalités d’une élection réelle se vérifient sur des pages officielles à jour |
| Priorité de tri | 1 — domaine à relecture spécialisée — politique publique, médias et information |
| Termes repérés | politique publique : scrutin, vote, élection |
| Fiche publiée | [lire la fiche](fiches/civ-reperer-info-electorale.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Vie publique — les fiches sur les institutions et la citoyenneté](https://www.vie-publique.fr/fiches) | Non vérifiée — lien documentaire ; aucune fiche n’est reprise | reference-factuelle | 2026-10-15 |
| [Service-Public — accueil d’information officielle sur les droits et démarches](https://www.service-public.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-15 |

**Ce que la fiche dit déjà de ses limites**

> Une élection n’est pas un horaire de train. Les règles, dates et listes changent. Un portail public oriente ; il ne dit pas pour qui voter et ne remplace pas le service compétent.

**Points à trancher par une personne**

- [ ] Ouvrir les 2 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 2 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "civ-reperer-info-electorale"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `civ-trouver-service-public` — Trouver un service public et préparer un formulaire

| Élément | Valeur |
| --- | --- |
| Domaine | Démarches, droits, sécurité et vie professionnelle |
| Repère de difficulté | 2 |
| Horizon du contenu | Orientation vers des services publics en France métropolitaine et outre-mer ; les organismes, sites et formulaires varient selon le territoire et la date |
| Priorité de tri | 1 — domaine à relecture spécialisée — droit, démarches et travail |
| Termes repérés | politique publique : service public |
| Fiche publiée | [lire la fiche](fiches/civ-trouver-service-public.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Service-Public — accueil d’information officielle sur les droits et démarches](https://www.service-public.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-15 |
| [France services — accueil du réseau d’accompagnement aux démarches](https://www.france-services.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-15 |
| [Cybermalveillance.gouv.fr — hameçonnage : prévention et conduite à tenir](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-15 |

**Ce que la fiche dit déjà de ses limites**

> Un site officiel n’est pas un guichet qui connaît ta situation. Les horaires, pièces, territoires et formulaires changent. Un accompagnement en personne, par exemple dans un point France services, n’est pas disponible partout de la même façon et ne remplace pas l’organisme compétent.

**Points à trancher par une personne**

- [ ] Ouvrir les 3 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 3 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "civ-trouver-service-public"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `econ-comparer-prix-unitaires` — Comparer deux prix à quantité égale

| Élément | Valeur |
| --- | --- |
| Domaine | Budget, économie, consommation et travail |
| Repère de difficulté | 2 |
| Horizon du contenu | Comparaison de prix et proportionnalité simple ; exemples fictifs de consommation |
| Priorité de tri | 1 — domaine à relecture spécialisée — argent, budget et finances |
| Termes repérés | — |
| Fiche publiée | [lire la fiche](fiches/econ-comparer-prix-unitaires.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [DGCCRF — information sur la consommation](https://www.economie.gouv.fr/dgccrf) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |
| [Éduscol — programmes et ressources de mathématiques au cycle 2](https://eduscol.education.gouv.fr/4746/ressources-d-accompagnement-du-programme-de-mathematiques-au-cycle-2) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |

**Ce que la fiche dit déjà de ses limites**

> Un produit n’est pas un simple ruban : sa composition, sa qualité, son utilité, sa conservation et la quantité réellement nécessaire comptent aussi. Le prix par unité compare un aspect chiffré, pas la valeur globale ni le meilleur choix pour une personne.

**Points à trancher par une personne**

- [ ] Ouvrir les 2 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 2 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "econ-comparer-prix-unitaires"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `econ-distinguer-interet-frais` — Distinguer un intérêt d’un frais sur un crédit fictif

| Élément | Valeur |
| --- | --- |
| Domaine | Budget, économie, consommation et travail |
| Repère de difficulté | 2 |
| Horizon du contenu | Lecture d’un tableau de montants fictifs ; les taux, contrats et droits réels se vérifient sur des pages officielles à jour et auprès d’un professionnel si besoin |
| Priorité de tri | 1 — domaine à relecture spécialisée — argent, budget et finances |
| Termes repérés | argent : crédit, prêt |
| Fiche publiée | [lire la fiche](fiches/econ-distinguer-interet-frais.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Banque de France — accueil de l’institution](https://www.banque-france.fr/) | Non vérifiée — lien documentaire ; aucune fiche ni barème n’est repris | reference-factuelle | 2026-10-15 |
| [Service-Public — accueil d’information officielle sur les droits et démarches](https://www.service-public.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-15 |
| [Service-Public.fr — « Crédit à la consommation : règles du contrat » (F2451)](https://www.service-public.gouv.fr/particuliers/vosdroits/F2451) | Non vérifiée — page consultée ; aucune réutilisation déclarée | reference-factuelle | 2026-10-20 |

**Ce que la fiche dit déjà de ses limites**

> Un crédit n’est pas un loyer. Les mots, les taux et les droits varient selon le contrat. Cette analogie n’explique ni un TAEG ni un choix d’emprunt.

**Points à trancher par une personne**

- [ ] Ouvrir les 3 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 3 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "econ-distinguer-interet-frais"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `econ-lire-facture` — Lire une facture et repérer une échéance

| Élément | Valeur |
| --- | --- |
| Domaine | Budget, économie, consommation et travail |
| Repère de difficulté | 2 |
| Horizon du contenu | Repères de vie courante et de consommation ; les exemples sont fictifs et les portails cités concernent la France |
| Priorité de tri | 1 — domaine à relecture spécialisée — argent, budget et finances |
| Termes repérés | — |
| Fiche publiée | [lire la fiche](fiches/econ-lire-facture.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Service-Public.fr — information officielle sur les droits et démarches](https://www.service-public.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |
| [DGCCRF — information sur la consommation](https://www.economie.gouv.fr/dgccrf) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |

**Ce que la fiche dit déjà de ses limites**

> Un ticket de caisse et une facture ne sont pas le même document. Leur présentation varie selon le service et le contexte ; toutes les factures n’affichent pas les mêmes rubriques. L’analogie aide à relier des lignes à un total, mais ne permet pas de vérifier seule la conformité juridique, la réalisation d’un service ou le paiement.

**Points à trancher par une personne**

- [ ] Ouvrir les 2 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 2 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "econ-lire-facture"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `econ-lire-mention-garantie` — Lire une mention de garantie sur un ticket fictif

| Élément | Valeur |
| --- | --- |
| Domaine | Budget, économie, consommation et travail |
| Repère de difficulté | 2 |
| Horizon du contenu | Lecture d’un document d’achat fictif en France ; les durées, droits et recours réels dépendent du contrat, du produit et des règles en vigueur |
| Priorité de tri | 1 — domaine à relecture spécialisée — argent, budget et finances |
| Termes repérés | droit et démarches : juridique, litige, recours |
| Fiche publiée | [lire la fiche](fiches/econ-lire-mention-garantie.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [DGCCRF — accueil de la direction de la concurrence, de la consommation et de la répression des fraudes](https://www.economie.gouv.fr/dgccrf) | Non vérifiée — lien documentaire ; aucune fiche pratique n’est reprise | reference-factuelle | 2026-10-15 |
| [SignalConso — service public d’information et de signalement pour les consommateurs](https://signal.conso.gouv.fr/fr) | Non vérifiée — lien documentaire ; aucun parcours de signalement n’est repris | reference-factuelle | 2026-10-15 |

**Ce que la fiche dit déjà de ses limites**

> Un colis et un contrat de consommation n’obéissent pas aux mêmes règles. Les durées, interlocuteurs et recours changent selon le produit, le vendeur, le territoire et la date. Cette analogie n’enseigne aucune garantie légale.

**Points à trancher par une personne**

- [ ] Ouvrir les 2 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 2 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "econ-lire-mention-garantie"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `sante-reperer-source-publique` — Repérer une source de santé publique avant d’agir

| Élément | Valeur |
| --- | --- |
| Domaine | Santé, alimentation, corps et sécurité |
| Repère de difficulté | 2 |
| Horizon du contenu | Lecture d’un message fictif ; aucun diagnostic, traitement ni consigne de soin n’est donné |
| Priorité de tri | 1 — domaine à relecture spécialisée — santé et sécurité |
| Termes repérés | santé : diagnostic, symptôme, traitement |
| Fiche publiée | [lire la fiche](fiches/sante-reperer-source-publique.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Ministère de la Santé — accueil](https://sante.gouv.fr/) | Non vérifiée — lien documentaire ; aucune fiche n’est reprise | reference-factuelle | 2026-10-15 |
| [Santé publique France — « Qui sommes-nous ? »](https://www.santepubliquefrance.fr/a-propos/sante-publique-france-qui-sommes-nous) | Non vérifiée — page consultée ; aucune réutilisation déclarée | reference-factuelle | 2026-10-20 |
| [Santé publique France — accueil](https://www.santepubliquefrance.fr/) | Non vérifiée — lien documentaire ; aucune consigne n’est reprise | reference-factuelle | 2026-10-15 |

**Ce que la fiche dit déjà de ses limites**

> Une pharmacie n’est pas un diagnostic. Un portail public oriente ; il ne te soigne pas et ne remplace pas un professionnel. Cette analogie n’indique aucun médicament.

**Points à trancher par une personne**

- [ ] Ouvrir les 3 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 3 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "sante-reperer-source-publique"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `recherche-lire-etude` — Lire une étude sans confondre résultats et certitudes

| Élément | Valeur |
| --- | --- |
| Domaine | Études supérieures, spécialités et recherche — post-bac au doctorat |
| Repère de difficulté | 4 |
| Horizon du contenu | Post-bac, licence, master et doctorat — selon la discipline |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | droit et démarches : juridique |
| Fiche publiée | [lire la fiche](fiches/recherche-lire-etude.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Carey, Steiner et Petri — Ten simple rules for reading a scientific paper, PLOS Computational Biology (2020)](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008032) | Creative Commons Attribution License (version non précisée sur la page consultée) | reference-factuelle | 2026-10-08 |

**Ce que la fiche dit déjà de ses limites**

> Une recherche peut porter sur des textes, des entretiens, une expérience en laboratoire, des archives, un modèle mathématique ou d’autres objets. Elle ne se réduit pas toujours à deux groupes comparables ; les disciplines ont plusieurs méthodes valables. L’image sert à poser des questions, pas à imposer une recette unique.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "recherche-lire-etude"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `recherche-question-hypothese` — Formuler une question et une hypothèse de recherche

| Élément | Valeur |
| --- | --- |
| Domaine | Études supérieures, spécialités et recherche — post-bac au doctorat |
| Repère de difficulté | 3 |
| Horizon du contenu | Premiers repères de conception d’une question de recherche ; l’exemple de la voiture-jouet est fictif |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | argent : prêt ; données personnelles : données personnelles |
| Fiche publiée | [lire la fiche](fiches/recherche-question-hypothese.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Centre national de la recherche scientifique — ressources et actualités scientifiques](https://www.cnrs.fr/fr) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-11 |

**Ce que la fiche dit déjà de ses limites**

> Toutes les recherches ne testent pas une hypothèse de cette manière. Une étude historique, qualitative, théorique ou exploratoire peut nécessiter d’autres questions et méthodes ; ce petit schéma ne constitue pas une recette universelle.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 1 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "recherche-question-hypothese"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `histoire-lire-frise` — Lire une frise chronologique et ordonner des événements

| Élément | Valeur |
| --- | --- |
| Domaine | Histoire, chronologie et mémoire |
| Repère de difficulté | 1 |
| Horizon du contenu | Premiers repères de chronologie ; exemple de dates entièrement fictif et dans un même mois |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | droit et démarches : succession |
| Fiche publiée | [lire la fiche](fiches/histoire-lire-frise.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Ministère de l’Éducation nationale — programmes et horaires de l’école élémentaire](https://www.education.gouv.fr/programmes-et-horaires-l-ecole-elementaire-9011) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |

**Ce que la fiche dit déjà de ses limites**

> Une frise peut choisir seulement certains événements, et son échelle n’est pas toujours régulière. La place d’un événement sur la ligne ne prouve pas qu’il a causé celui qui vient ensuite ; les exemples de cette fiche ne sont pas des faits historiques.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 1 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "histoire-lire-frise"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `info-lire-adresse-web` — Repérer les parties d’une adresse Web

| Élément | Valeur |
| --- | --- |
| Domaine | Informatique, algorithmique et langages de programmation |
| Repère de difficulté | 2 |
| Horizon du contenu | Premiers repères sur le protocole, l’hôte, le chemin et le paramètre d’une adresse Web fictive |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | données personnelles : donnée personnelle, données personnelles, mot de passe |
| Fiche publiée | [lire la fiche](fiches/info-lire-adresse-web.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [MDN — documentation Web et structure des URL](https://developer.mozilla.org/fr/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-11 |

**Ce que la fiche dit déjà de ses limites**

> Internet n’est pas un service postal centralisé. Les règles techniques, les redirections, les paramètres et les certificats ajoutent des détails que l’adresse visible ne montre pas toujours. Une URL lisible ne prouve pas que son contenu est sûr ou exact.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 1 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "info-lire-adresse-web"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `prog-lire-licence-logiciel` — Lire une licence avant de réutiliser un programme

| Élément | Valeur |
| --- | --- |
| Domaine | Informatique, algorithmique et langages de programmation |
| Repère de difficulté | 2 |
| Horizon du contenu | Premiers repères sur le code visible, la licence et l’attribution ; aucun conseil juridique personnalisé |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | droit et démarches : juridique |
| Fiche publiée | [lire la fiche](fiches/prog-lire-licence-logiciel.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Open Source Initiative — The Open Source Definition](https://opensource.org/osd) | Non vérifiée — lien documentaire ; aucun critère ni texte n’est repris | reference-factuelle | 2026-10-15 |
| [SPDX License List](https://spdx.org/licenses/) | Non vérifiée — lien documentaire ; aucune fiche de licence n’est reprise | reference-factuelle | 2026-10-15 |

**Ce que la fiche dit déjà de ses limites**

> Une recette n’est pas un logiciel : les règles de droit, les copies, les combinaisons de licences et les obligations de source sont spécifiques. Une étiquette de restaurant n’explique ni un contrat, ni un pays, ni une version de licence.

**Points à trancher par une personne**

- [ ] Ouvrir les 2 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 2 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "prog-lire-licence-logiciel"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `fr-argumenter-avec-exemple` — Présenter une idée avec une raison et un exemple

| Élément | Valeur |
| --- | --- |
| Domaine | Français, lecture, écriture et communication |
| Repère de difficulté | 2 |
| Horizon du contenu | Premiers repères d’argumentation et de communication ; les situations et opinions proposées sont fictives |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | droit et démarches : juridique |
| Fiche publiée | [lire la fiche](fiches/fr-argumenter-avec-exemple.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Ministère de l’Éducation nationale — socle commun de connaissances, de compétences et de culture](https://www.education.gouv.fr/le-socle-commun-de-connaissances-de-competences-et-de-culture-12512) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-11 |

**Ce que la fiche dit déjà de ses limites**

> Un argument n’est pas une adresse vérifiable d’un seul coup. Une raison peut être discutée, un exemple peut être particulier et plusieurs personnes peuvent tirer des conclusions différentes.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 1 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "fr-argumenter-avec-exemple"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `fr-reperer-idee-texte` — Repérer l’idée principale et les informations utiles

| Élément | Valeur |
| --- | --- |
| Domaine | Français, lecture, écriture et communication |
| Repère de difficulté | 2 |
| Horizon du contenu | Compréhension de textes courts et repérage d’informations ; exemples fictifs |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | droit et démarches : juridique |
| Fiche publiée | [lire la fiche](fiches/fr-reperer-idee-texte.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Ministère de l’Éducation nationale — socle commun et apprentissages](https://www.education.gouv.fr/le-socle-commun-de-connaissances-de-competences-et-de-culture-12512) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |

**Ce que la fiche dit déjà de ses limites**

> Un texte n’est pas toujours un dossier avec un seul titre. Il peut développer plusieurs idées importantes, et le détail utile dépend de la question que l’on se pose. Un résumé doit rester fidèle au texte, sans ajouter une interprétation comme si elle était écrite.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 1 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "fr-reperer-idee-texte"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `numerique-formuler-recherche` — Formuler une recherche sur le Web

| Élément | Valeur |
| --- | --- |
| Domaine | Numérique, données, cybersécurité et intelligence artificielle |
| Repère de difficulté | 1 |
| Horizon du contenu | Premiers repères pour choisir des mots de recherche et affiner une requête ; aucun moteur précis n’est privilégié |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | données personnelles : donnée personnelle |
| Fiche publiée | [lire la fiche](fiches/numerique-formuler-recherche.html) |
| Contrôles automatiques | 17/17 — aucun défaut mécanique détecté |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [CNIL — données personnelles et bons réflexes numériques](https://www.cnil.fr/fr) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-11 |

**Ce que la fiche dit déjà de ses limites**

> Un moteur de recherche ne pose pas de questions comme une personne et ses résultats dépendent de ses outils, de son index et parfois de réglages. La première page n’est pas forcément la meilleure réponse ni une liste complète.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 1 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "numerique-formuler-recherche"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

### `numerique-organiser-fichiers` — Nommer et retrouver ses fichiers sans exposer ses données

| Élément | Valeur |
| --- | --- |
| Domaine | Numérique, données, cybersécurité et intelligence artificielle |
| Repère de difficulté | 2 |
| Horizon du contenu | Organisation générale de fichiers, sans dépendre d’un appareil ou d’un logiciel précis |
| Priorité de tri | 2 — hors domaine sensible, signalé par mots-clés |
| Termes repérés | données personnelles : données personnelles |
| Fiche publiée | [lire la fiche](fiches/numerique-organiser-fichiers.html) |
| Contrôles automatiques | 16/17 — aucun défaut mécanique détecté ; constat à trancher par une personne : 1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne |
| Relecture consignée | aucune à ce jour |

**Sources enregistrées dans le catalogue**

| Source | Licence déclarée | Mode | Droits contrôlés le |
| --- | --- | --- | --- |
| [Cybermalveillance.gouv.fr — prévention et assistance face aux actes de cybermalveillance](https://www.cybermalveillance.gouv.fr/) | Non vérifiée — lien documentaire ; aucune réutilisation déclarée | reference-factuelle | 2026-10-08 |

**Ce que la fiche dit déjà de ses limites**

> Un ordinateur peut rechercher, trier, masquer ou partager des fichiers d’une manière qui dépend du logiciel et des réglages. Un nom clair ne remplace ni une sauvegarde, ni le contrôle des personnes qui ont accès au dossier.

**Points à trancher par une personne**

- [ ] Ouvrir les 1 source(s) et vérifier que chacune étaye réellement l’affirmation citée.
- [ ] Trancher les droits : 1 source(s) déclarent une licence « non vérifiée ». Référence factuelle ou reprise autorisée, la décision doit être écrite.
- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.
- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.
- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.

**Relecture à consigner dans `relectures.toml`**

```toml
[[relecture]]
fiche = "numerique-organiser-fichiers"
date = AAAA-MM-JJ
role = "expertise du domaine — préciser lequel"
perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]
verdict = "conforme"          # conforme | a-corriger | insuffisant
sources_ouvertes = []
droits_verifies_le = AAAA-MM-JJ
objections = []
points_bloquants = []
suite = "ce qui est décidé ensuite, et par qui"
```

Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association.

## 4. Ce que ces paquets ne font pas

- Ils ne remplacent ni la [grille de relecture](grille-relecture.md) ni l’expertise du domaine : les questions communes y restent.
- Ils ne vérifient aucun contenu de source et ne disent pas qu’une licence est valide ; ils montrent seulement ce qui est déclaré.
- Ils n’attribuent aucune note, aucun score et aucun ordre de valeur entre fiches.
- Ils n’autorisent aucune publication : la décision reste celle de l’association.
- Ils ne remplacent pas le registre : la seule trace opposable est l’entrée de `relectures.toml` vérifiée par `outils/registre-relecture.py`.

Régénérer avec `python3 outils/construire-paquets-relecture.py` ; vérifier avec `--verifier`.
