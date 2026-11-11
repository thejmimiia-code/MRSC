# Plan complet du site M.R.S.C. et refonte de l’accueil — 11 novembre 2026

**Lot du 11 novembre 2026, 17 h 24 UTC. Demande : « faire le plan complet du site, vérifier toutes les redondances surtout sur la page d’accueil, faire le brainstorming nécessaire afin d’avoir une page entièrement revue, où les choses sont placées correctement avec logique et intelligence et en une seule fois ; les visiteurs doivent tout de suite trouver les choses et savoir où cliquer, ce doit être simple et ludique ».** Ce document est une carte de travail attribuée à l’agent, gardée par `outils/verifier-plan-site.py` et `outils/test_mutations_plan_site.py`. Il n’est ni une validation éditoriale, ni un jugement de rendu, ni une publication.

## 1. Demande et méthode

**Besoin observé par la personne :** l’accueil répétait plusieurs fois les mêmes informations avec des formulations différentes — « les choses étaient rabâchées différemment à plusieurs reprises ». **Fait mesuré :** avant ce lot, le `<main>` de `index.html` contenait 8 sections, 21310 caractères et jusqu’à cinq descriptions distinctes des trois mêmes ressources. **Hypothèse de conception :** un visiteur trouve plus vite quand chaque information occupe **une seule place** et quand chaque porte d’entrée est formulée comme **sa question**, pas comme une énième présentation de la ressource. **Proposition :** une refonte en une passe, décrite section par section ci-dessous.

Méthode : `orchestration-taches` pour cadrer, `conception-innovation` pour produire trois options dont « ne rien construire », `revue-contradictoire` pour l’audit des reprises, `documentation-technique` pour la carte vérifiable. Les sources de vérité restent `AGENTS.md`, `docs/apprentissage/catalogue.toml`, `docs/rd/portefeuille.toml`, `assets/css/site.css`, `outils/verifier-integration.py` et `outils/verifier-site-statique.py`. La refonte ne modifie ni le `<head>`, ni l’en-tête, ni le pied de page, ni la feuille de style : **110 classes CSS de l’ancienne page sont toutes conservées**, pour ne laisser aucun sélecteur orphelin.

**Ce que « en une seule fois » veut dire ici :** livrer ensemble l’inventaire, l’audit, le brainstorming, le plan, la page refondue, la garde, le banc, le câblage CI et les signatures — sans demander à la personne de trancher une étape intermédiaire. Cela ne veut pas dire franchir une porte humaine : la publication, le choix éditorial final et le jugement du rendu à l’œil restent à une personne.

## 2. Plan complet du site

Le site compte 19 surfaces : 13 pages racine servies, 107 fiches générées, l’interface du simulateur, l’API locale, les ressources partagées et deux fichiers d’indexation. La navigation principale compte 9 entrées, répétées à l’identique dans l’en-tête et le pied de page ; l’accueil n’ajoute pas de dixième menu, il ajoute des **portes d’intention**.

| Surface | Rôle unique | Pour qui | On y arrive depuis | Statut |
| --- | --- | --- | --- | --- |
| `index.html` | Accueil : présenter l’association une fois et orienter vers les quatre portes | Tous les visiteurs | navigation, footer, llms.txt, sitemap.xml | page refondue |
| `apprendre.html` | Catalogue des 107 fiches, boussole et parcours | Visiteur qui veut comprendre une notion | accueil, navigation, footer, fiches | page servie |
| `apprendre/fiches/` | 107 fiches autonomes générées depuis le catalogue | Visiteur en situation d’apprentissage | apprendre.html, atlas, sitemap.xml | pages générées |
| `anglais-aventure.html` | Les Mondes : atlas et aventure d’apprentissage libre | Visiteur qui veut explorer par le jeu | apprendre.html, navigation, footer | prototype |
| `ia-societe.html` | Dossier sur les usages de l’IA et les questions à débattre | Visiteur qui veut démêler une affirmation | accueil, navigation, footer | dossier |
| `simulateur.html` | Présentation du simulateur et de ses limites | Visiteur qui veut comparer des choix publics | accueil, navigation, footer | page servie |
| `simulateur/index.html` | Interface du moteur embarqué | Visiteur qui veut régler des leviers | simulateur.html | page générée |
| `eva.html` | Proposition de présentation du projet ÉVA, à relire | Visiteur qui suit la recherche | accueil #rd-eva, footer, llms.txt | proposition à relire |
| `documents.html` | Documents officiels de l’association | Visiteur qui veut vérifier un texte | accueil, navigation, footer | documents locaux |
| `liens-utiles.html` | Ressources externes sélectionnées | Visiteur qui veut aller plus loin | navigation, footer | page servie |
| `localisation.html` | Informations de localisation | Visiteur qui cherche le territoire | navigation, footer | page servie |
| `nous-contacter.html` | Moyens de contacter l’association | Visiteur qui veut écrire | accueil, navigation, footer | page servie |
| `transparence.html` | Méthode, registre des sources et licence | Visiteur qui vérifie une information | accueil, navigation, footer | page servie |
| `confidentialite.html` | Vie privée et données | Visiteur qui veut savoir ce qui est collecté | footer, accueil (repère chiffré) | page servie |
| `404.html` | Page d’erreur avec retour à l’accueil | Visiteur arrivé sur une adresse absente | serveur | page servie |
| `api/` | Fonctions serveur du simulateur | Interface du simulateur | simulateur/index.html | hors accueil |
| `assets/` | Feuilles, scripts, images et documents locaux | Toutes les pages | toutes les pages | ressources |
| `sitemap.xml` | Liste des URL publiques | Moteurs et outils | llms.txt | fichier servi |
| `llms.txt` | Sommaire facultatif pour les lecteurs de contenu | Assistants et lecteurs | index.html (rel="describedby") | fichier servi |

Règle de placement : une information n’a qu’une seule maison. Les statuts sont dans `documents.html` ; la méthode et le registre des sources sont dans `transparence.html` ; le catalogue est dans `apprendre.html` ; le modèle et ses limites sont dans `simulateur.html` ; l’état du chantier ÉVA est dans `eva.html`. L’accueil **ne décrit aucune de ces pages une deuxième fois** : il dit une fois ce qu’elles sont dans l’ouverture, puis il oriente.

Ce que ce plan ne dit pas : qu’une page est exacte, claire, accessible ou utile ; qu’un lien vivant garantit une information à jour ; que la navigation convient à un lecteur d’écran ou à un téléphone. Ces contrôles existent ailleurs et leurs limites restent écrites.

## 3. Audit des redondances de l’accueil

L’audit est **recalculé** sur le `<main>` de `index.html` à chaque lancement de la garde, à partir des expressions régulières consignées dans `docs/rd/plan-site-complet-2026-11-11.toml`. Un seuil écrit ne suffit pas : c’est la page qui fait foi.

| Repère | Ce qui était répété | Avant | Après | Décision de placement |
| --- | --- | --- | --- | --- |
| `compte` | Absence de compte, d’abonnement et de mesure d’audience | 5 | 2 | Une seule promesse dans l’ouverture et un seul repère chiffré ; les trois autres reprises sont retirées. |
| `sources` | Mention des sources, limites et statut | 26 | 16 | Une seule promesse dans l’ouverture et une seule liste de sources en fin de parcours ; les cartes ne répètent plus la promesse. |
| `invitation` | Invitation à écrire ou à poser une question | 7 | 5 | Une phrase dans l’ouverture et une section « Participer » ; les invitations de la section association et de l’ancienne section « Participer » sont retirées. |
| `predit` | Le simulateur ne prédit pas | 3 | 1 | Une seule mise au point dans l’ouverture ; les deux reformulations du simulateur sont retirées. |
| `position` | Le dossier / ÉVA ne sont pas une position votée | 4 | 1 | Une seule réserve, dans la section ÉVA ; les trois reformulations du dossier IA sont retirées. |
| `dossier` | Le dossier sur l’intelligence artificielle | 9 | 4 | Présenté une fois dans l’ouverture, puis uniquement par des libellés de destination. |
| `fiches` | Les fiches d’apprentissage | 14 | 8 | Présentées une fois dans l’ouverture, puis uniquement par des gestes et des destinations. |
| `simulateur` | Le simulateur | 17 | 9 | Présenté une fois dans l’ouverture, puis uniquement par des gestes et des destinations. |
| `association1901` | Le régime associatif loi 1901 | 3 | 2 | Une mention dans le bandeau d’ouverture et une dans la présentation de l’association ; la lede ne la répète plus. |
| `description_ressource` | Description de ce qu’est une ressource | 8 | 3 | Une seule description, dans l’ouverture ; les trois autres blocs deviennent des questions de visiteur, des principes ou des gestes. |

Avant la refonte, les trois ressources étaient présentées dans **cinq endroits** : la liste `home-hero-resources`, l’encadré « Par où commencer ? », les « Trois portes d’entrée » de la section association, les quatre cartes « Les ressources en détail » et les trois cartes « Des documents, des idées et leurs sources ». Chaque endroit redisait « fiches / dossier IA / simulateur » avec des adjectifs différents. Le « sans compte » apparaissait cinq fois, la promesse de sources vingt-six fois, la mise au point « le simulateur ne prédit pas » trois fois, et la réserve « ce n’est pas une position votée » quatre fois.

Deux autres défauts de logique ont été relevés : la section **ÉVA arrivait avant les ressources** (`mission → rd-eva → actions → rejoindre`), alors qu’un chantier interne intéresse le visiteur après ce qu’il est venu chercher ; et **deux sections distinctes** (« Participez selon vos disponibilités » et « Une question ou l’envie de participer ? ») invitaient toutes deux à écrire à l’association.

Après la refonte : 6 sections, 18112 caractères, une seule description des ressources, une seule liste de sources, une seule section de contact, et l’ordre `mission → actions → rd-eva → rejoindre`. Aucun contrôle n’a été assoupli pour y parvenir.

## 4. Brainstorming : trois options

| Option | Titre | Contenu | Coût | Risque principal | Décision |
| --- | --- | --- | --- | --- | --- |
| **A** | Réordonner sans réécrire | Déplacer ÉVA après les ressources et fusionner les deux sections de contact. | Très faible : quelques blocs déplacés. | Les cinq descriptions des ressources restent ; le rabâchage signalé persiste. | écartée |
| **B** | Une seule porte par intention | L’ouverture décrit une fois les trois ressources ; l’orienteur pose quatre questions ; les cartes deviennent des gestes ; les principes ne renvoient plus aux ressources ; ÉVA est déplacé ; contact et partage fusionnent ; sources une seule fois. | Moyen : réécriture du seul <main>, head, header, footer et toutes les classes CSS conservés. | Le ton des nouvelles questions reste à juger à l’œil ; aucun essai avec des personnes. | retenue |
| **C** | Page-portail minimale | Ne garder que le H1 et quatre gros boutons, supprimer les autres sections. | Élevé : une vingtaine de contrôles d’intégration et une partie de la feuille CSS seraient à réécrire. | Perdre les repères chiffrés, les statuts, les sources et les replis de partage contredirait les gardes existantes. | écartée |

**Théorie du changement de l’option retenue :** besoin → mécanisme → activité observable → effet attendu → preuve nécessaire.

| Étape | Ce qui est écrit |
| --- | --- |
| Besoin | Le visiteur ne doit pas relire trois fois la même promesse avant de trouver un lien. |
| Mécanisme | Une seule description, puis des questions de visiteur, puis des gestes, puis une seule section par thème. |
| Activité observable | Depuis le premier écran, choisir une des quatre questions et cliquer ; ou descendre jusqu’aux quatre cartes d’action. |
| Effet attendu | Moins de texte à parcourir, une destination par intention, aucun doublon de destination. |
| Preuve nécessaire | Les compteurs de la section 3, les quatre destinations distinctes de la section 6, les gardes du dépôt et la batterie complète. Un essai avec des personnes et un regard sur le rendu restent nécessaires pour juger l’effet réel. |

**Critères d’arrêt définis avant la refonte :** aucune information clé ne doit dépasser son seuil ; chaque information doit avoir une seule section ; les quatre portes doivent avoir quatre destinations distinctes ; toutes les classes CSS de l’ancienne page doivent rester employées ; toutes les gardes existantes doivent rester vertes ; le poids de la page ne doit pas augmenter. L’option C a été écartée parce qu’elle aurait demandé de réécrire une vingtaine de contrôles d’intégration et une partie de `assets/css/site.css` : ce n’est plus « une seule fois », c’est un autre chantier.

## 5. Structure retenue, section par section

| Section | Rôle | Information qui n’est écrite que là | Destinations |
| --- | --- | --- | --- |
| accueil | Ouverture | La seule présentation des trois ressources, les repères chiffrés et la promesse de traçabilité | #mission, apprendre.html#catalogue-fiches |
| mission | L’association | Qui nous sommes, les statuts, trois principes et la hiérarchie de preuve | documents.html, #actions |
| actions | Les quatre gestes | Une tâche, une destination : aucune redescription des ressources | apprendre.html, ia-societe.html, simulateur.html, transparence.html |
| rd-eva | Le chantier | ÉVA, son état et ses limites, après les ressources et non avant | eva.html, transparence.html#rd-innovation |
| rejoindre | Participer et faire circuler | Une seule section de contact, d’adhésion et de partage | nous-contacter.html, bulletin, courriel, partage |
| sources | Sources et méthode | Une seule liste de provenance, en fin de parcours | transparence.html |

L’ordre est celui d’une visite : **qui parle** (ouverture + association) → **ce qu’on peut faire** (quatre gestes) → **ce qui se prépare** (ÉVA) → **comment s’y joindre** (participer, adhérer, partager) → **d’où viennent les informations** (sources). Le bandeau « Vous cherchez… ? » apporte la part ludique sans JavaScript : quatre questions numérotées, quatre verbes, une seule ligne d’indice chacune. Aucun compte, aucun parcours obligatoire, aucun nouveau bouton, aucun média distant : la simplicité est structurelle, pas décorative.

Trois remplacements de fond, pas trois reformulations :

1. L’encadré « Par où commencer ? » qui **décrivait** les ressources devient un **orienteur par question** : « Comprendre une notion », « Démêler une info sur l’IA », « Comparer des choix publics », « Suivre le chantier ÉVA ».
2. Les « Trois portes d’entrée » de l’association, qui renvoyaient encore vers les mêmes trois ressources, deviennent **trois principes** (« Partir de ce que nous vivons », « Mettre les savoirs en commun », « Rendre les propositions compréhensibles ») avec des liens vers les documents, la méthode et le contact — jamais vers une quatrième description des fiches.
3. Les cartes « Ressources en détail » deviennent **quatre gestes** (« Comprendre », « Démêler », « Comparer », « Vérifier ») ; la section « Des documents, des idées et leurs sources », qui répétait une cinquième fois le même trio, est supprimée.

## 6. Où cliquer : la carte des destinations

| N | Question du visiteur | Destination | Indice lu |
| --- | --- | --- | --- |
| 01 | Comprendre une notion | `apprendre.html` | Une fiche courte, un exemple, un exercice si vous voulez. |
| 02 | Démêler une info sur l’IA | `ia-societe.html` | Ce qui est documenté, ce qui se discute, ce qui reste ouvert. |
| 03 | Comparer des choix publics | `simulateur.html` | Régler un levier et lire les effets, échelon par échelon. |
| 04 | Suivre le chantier ÉVA | `#rd-eva` | Ce qui est documenté, ce qui reste à tester. |

Les quatre portes mènent à quatre endroits distincts. Les quatre cartes d’action mènent à `apprendre.html`, `ia-societe.html`, `simulateur.html` et `transparence.html`. La section association mène à `documents.html` et à l’ancre `#actions` ; la section ÉVA mène à `eva.html` et à la méthode R&D ; la section participer mène à `nous-contacter.html`, au bulletin d’adhésion et au partage ; la section sources mène à `transparence.html`. Le pied de page reste la navigation exhaustive, l’en-tête reste le menu, et l’accueil n’invente aucune dixième entrée.

Un visiteur qui arrive avec une question n’a donc qu’un choix à faire au premier écran. S’il descend, il trouve une seule section par sujet, dans un ordre qui va du plus concret au plus général.

## 7. Ce qui a réellement changé

1. `index.html` : réécriture du seul `<main>`, de 8 à 6 sections, de 21310 à 18112 caractères, sans toucher au `<head>`, à l’en-tête, au pied de page ni à `assets/css/site.css`.
2. `docs/rd/plan-site-complet-2026-11-11.md` et `docs/rd/plan-site-complet-2026-11-11.toml` : plan complet du site, audit chiffré, brainstorming, structure, carte des destinations.
3. `outils/verifier-plan-site.py` : recalcule les 10 reprises, l’ordre des sections, les quatre portes, la couverture des 19 surfaces, les 110 classes CSS conservées et l’absence de validation inventée ; `outils/test_mutations_plan_site.py` plante ses fautes dans une copie complète.
4. Câblage de ces deux commandes dans `.github/workflows/verification.yml`, mise à jour de `docs/rd/inventaire-controles.md`, du journal, des avancées et de la mémoire ÉVA, puis signature de chaque unité par `outils/relire-contenus.py --appliquer`.
5. Régénération du rapport de poids des pages après la réduction du HTML, puis gardes du site, gardes R&D et batterie complète.
6. `outils/test_mutations_integration.py` et `outils/test_mutations_affichages.py` : deux bancs existants réalignés sur les repères de l’accueil refondu. Leurs fragments plantés désignaient `<dt>Accès au site</dt>` — devenu `<dt>Réutilisation</dt>` — et la porte d’entrée retirée vers le catalogue des fiches ; sans cet alignement les bancs refusaient de mordre et la batterie sortait à 94/96. Les fautes plantées restent les mêmes : retour de la carte du siège, réintroduction de l’appel aux dons, porte sans lien, renvoi aux statuts perdu.

**Ce qui n’a pas changé :** les 107 fiches, les 81 prototypes à relire, les statuts, le catalogue, le référentiel, le portefeuille, l’API, le moteur du simulateur, les autres pages HTML, les scripts, les images, `docs/apprentissage/relectures.toml` (0 relecture humaine), la décision prospective A/B/C et l’état de `www.ign.fr/`. **Publication :** à la demande explicite de la personne le 11 novembre 2026 — « pousses et fusionnes que je vois directement sur le site » —, ce lot est commité sur la branche de session, poussé et proposé en fusion vers `main` dans la même passe. La fusion déclenche `deploy-pages.yml`, qui sert `index.html` et les pages publiées sur l’adresse publique du dépôt ; `source` Pages reste « GitHub Actions », donc `docs/`, `outils/`, `api/` et `README.md` ne sont pas publiés. Les 27 commandes de ce workflow plus ses 7 commandes éclatées ont été jouées en local avant la poussée : 34 sur 34 vertes. Publier ne valide rien : aucune relecture humaine, aucune expertise, aucun avis juridique, aucun essai avec des personnes, aucun rendu vérifié à l’œil.

## 8. Limites, contrôles et prochaine action

Une page plus courte et mieux ordonnée **ne prouve pas** qu’un visiteur trouve plus vite, ni que le ton des quatre questions est le bon, ni que le rendu plaît : ce sont des jugements de personnes, pas des résultats de cette passe. Les quatre nouvelles questions, l’ordre des cartes et la place du panneau de partage demandent un regard à l’œil sur téléphone, au clavier, au zoom et avec un lecteur d’écran. Aucun essai volontaire n’a eu lieu, aucune expertise de domaine, aucun avis juridique, aucune validation humaine, aucune promotion de statut.

Les contrôles réellement exécutés sont consignés dans `docs/rd/journal.md` : `verifier-site-statique.py`, `verifier-integration.py`, `verifier-publication-locale.py`, `verifier-securite.py`, `verifier-poids-pages.py`, `auditer-selecteurs-morts.py --verifier`, `verifier-budgets-visuels.py`, `verifier-affichages.py --verifier`, `verifier-apparences.py --verifier`, `verifier-plan-site.py`, son banc de 13 cas, `verifier-plan-projet.py` (579 fichiers), `verifier-inventaire-controles.py` (73 outils), `verifier-workflows.py`, `relire-contenus.py`, la batterie complète reconstruite depuis le workflow (96 commandes, 96 OK, dont les 5 commandes exclusives à la CI écartées) et `git diff --check`.

Pour tenir la carte à jour :

```sh
python3 outils/verifier-plan-site.py
python3 outils/test_mutations_plan_site.py
python3 outils/verifier-site-statique.py
python3 outils/verifier-integration.py
python3 outils/auditer-selecteurs-morts.py --verifier
python3 outils/relire-contenus.py
python3 outils/construire-avancees.py --verifier
python3 outils/memoire-eva.py --verifier
git diff --check
```

**Prochaine action prise par l’agent :** présenter la page refondue pour le regard à l’œil, sans demander à la personne de relire le texte à sa place ; si le rendu appelle un ajustement, le consigner comme une nouvelle édition datée, avec son constat et sa limite. Retenter `www.ign.fr/` à une date ultérieure reste ouvert, l’horloge du 11 novembre 2026 n’ayant pas changé.
