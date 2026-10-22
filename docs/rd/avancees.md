# Avancées réutilisables de la R&D

**Document de travail généré.** Il ne certifie rien et ne remplace ni une relecture, ni un audit, ni une décision éditoriale. Il retient ce qu'un lot a appris de durable, avec la preuve locale qui le soutient, le contrôle qui le maintient et la limite qui l'accompagne.

**À quoi cela sert :** un autre agent reprend le projet sans avoir à reconstituer l'histoire. Chaque entrée dit aussi ce qu'elle ne prouve pas, pour qu'une avancée ne se transforme pas en argument d'autorité.

**Date de génération :** 2026-10-22.

## 1. Vue d'ensemble

| Mesure | Valeur |
| --- | ---: |
| Avancées consignées | 10 |
| Période couverte | du 2026-10-20 au 2026-10-20 |
| Contrôles exécutables cités | 13 |
| Initiatives du portefeuille concernées | 10 |

Ces nombres mesurent la traçabilité du registre, pas la valeur des avancées. Une entrée peut être parfaitement traçable et se révéler fausse plus tard : c'est le contrôle qui la contredira.

## 2. Les avancées

### `carte-de-sujet-avant-premiere-fiche` — Ouvrir une carte de sujet avant la première fiche évite le doublon et le hors-périmètre

*Consignée le 2026-10-20.*

**Constat.** Créer directement une fiche sur un sujet vide (`a-creer`) expose à répéter une fiche voisine déjà présente dans un autre domaine (`tech-electronique-capteur` pour les systèmes embarqués) ou à déborder sur un sujet exigeant une relecture experte préalable (`premiers-secours` ou `securite-electricite`).

**Ce que cela change.** Chaque sujet sans fiche travaillé passe d'abord par une carte `docs/rd/sujet-<id>.md` reliée à `docs/rd/carte-lacunes.md`, qui fixe les sources primaires lues, ce qu'elles ne prouvent pas et la frontière phrase par phrase avec les fiches voisines avant toute rédaction dans `catalogue.toml`.

**Preuves dans le dépôt :**

- `docs/rd/carte-lacunes.md`
- `docs/rd/sujet-ecoute-prononciation.md`
- `docs/rd/sujet-systemes-embarques.md`
- `docs/rd/sujet-securite-sciences.md`
- `outils/construire-carte-lacunes.py`

**Contrôle qui la maintient :** `python3 outils/construire-carte-lacunes.py --verifier && python3 outils/auditer-prototypes.py --verifier`

**Limite — ce que cela ne prouve pas.** Une carte de sujet et une fiche prototype conforme aux contrôles mécaniques ne remplacent ni la relecture par une personne compétente du domaine, ni l'essai avec des personnes apprenantes.

**Suite.** Faire relire `info-objet-connecte-local-distant` et décider, à partir de `docs/rd/sujet-securite-sciences.md`, s'il faut rédiger un premier prototype sur la lecture complète d'une étiquette CLP.

Initiatives liées : `cartographier-les-lacunes`, `relire-les-44-prototypes`.

### `indice-de-confrontation-non-certifiant` — Confronter une affirmation par ancres donne un indice et ses angles morts, jamais une validation

*Consignée le 2026-10-20.*

**Constat.** Chercher des mots-clés d'une fiche dans sa page source détecte utilement la présence des termes attendus, mais échoue dès qu'une négation inverse le sens (mentions interdites sur Service-Public F2451) ou qu'un PDF coupe un mot dans une formule (« dur é e »).

**Ce que cela change.** Le prototype `docs/rd/confrontations-sources.toml` borne chaque ancre à cinq mots sans recopier d'extrait sous droits, interdit tout état de validation, exige l'écriture explicite d'un faux positif et d'un faux négatif par fiche, et reste hors de la porte de publication.

**Preuves dans le dépôt :**

- `docs/rd/confrontations-sources.toml`
- `docs/rd/confrontations-sources.md`
- `outils/confronter-sources.py`
- `outils/test_confronter_sources.py`

**Contrôle qui la maintient :** `python3 outils/test_confronter_sources.py && python3 outils/confronter-sources.py --verifier`

**Limite — ce que cela ne prouve pas.** Un indice concordant ne prouve jamais que la fiche dit vrai ni qu'elle respecte la portée de la source ; un constat d'ancre absente ou de page inaccessible ne prouve jamais que la fiche est fausse.

**Suite.** Mesurer les faux positifs et faux négatifs avec une personne relectrice avant d'envisager d'étendre l'échantillon au-delà des neuf fiches du prototype.

Initiatives liées : `confronter-une-affirmation-a-sa-source`, `relire-les-44-prototypes`, `prospective-apprentissages-2030`.

### `mesure-servie-reverifiee` — Ce que l'hébergement sert est mesuré, puis revérifié hors ligne

*Consignée le 2026-10-20.*

**Constat.** Un rapport d'en-têtes arrivait chaque mois dans une issue, était lu une fois, puis ne prouvait plus rien : rien ne signalait qu'une image avait changé depuis la mesure, ni qu'une cible de la sonde avait disparu du relevé.

**Ce que cela change.** Le relevé est désormais un fichier daté du dépôt, confronté aux fichiers à chaque porte sans réseau : une image ou une icône doit faire exactement la taille du fichier du dépôt, une page ou une feuille de style doit arriver compressée et plus petite, et le relevé doit couvrir exactement les cibles de la sonde — ni plus, ni moins.

**Preuves dans le dépôt :**

- `docs/rd/en-tetes-servis-2026-10-20.toml`
- `outils/verifier-fichiers-servis.py`
- `outils/test_fichiers_servis.py`

**Contrôle qui la maintient :** `python3 outils/test_fichiers_servis.py && python3 outils/verifier-fichiers-servis.py`

**Limite — ce que cela ne prouve pas.** Le contrôle compare des tailles, pas du contenu : une image servie à l'identique peut être inadaptée, et une page compressée peut être fausse. Il ne mesure ni le rendu, ni la vitesse réelle, ni l'empreinte du réseau ; la durée de cache de dix minutes vient de GitHub Pages et ne se règle pas depuis le dépôt.

**Suite.** Refaire la mesure réseau après tout changement d'image ou de cible, mettre à jour le relevé daté dans le même lot, et laisser l'issue de suivi ouverte comme journal de mesures.

Initiatives liées : `optimisation-du-site`, `indexation-et-lecteurs-de-contenu`.

### `page-ouverte-avant-citation` — Aucune page n'est citée sans avoir été ouverte

*Consignée le 2026-10-20.*

**Constat.** Chercher une page qui « a l'air » de répondre ne suffit pas : il faut l'ouvrir, y lire la phrase qui étaye l'affirmation, et noter ce qu'elle n'étaye pas. Vingt-deux fiches ont été traitées ainsi ; sept pages ont été refusées après tentative ou lecture.

**Ce que cela change.** Le catalogue porte, pour chaque page ajoutée, la date de consultation et une phrase qui sépare ce que la page étaye de ce qu'elle n'étaye pas — par exemple un document sur les changements d'état qui ne parle pas de dissolution.

**Preuves dans le dépôt :**

- `docs/apprentissage/catalogue.toml`
- `docs/apprentissage/audit-automatique.md`
- `docs/apprentissage/paquets-relecture.md`

**Contrôle qui la maintient :** `python3 outils/auditer-prototypes.py --verifier && python3 outils/construire-paquets-relecture.py --verifier`

**Limite — ce que cela ne prouve pas.** Une page qui étaye une phrase ne vaut ni expertise de domaine, ni contrôle des droits, ni essai d'usage réel ; le registre des relectures humaines reste vide.

**Suite.** Poursuivre fiche par fiche sur le constat restant (`arts-composer-formes`), en préférant une page réellement lue à un portail de plus.

Initiatives liées : `relire-les-44-prototypes`.

### `phrase-publique-recalculee` — La phrase publique se recalcule, elle ne se recopie pas

*Consignée le 2026-10-20.*

**Constat.** Une phrase écrite à la main dans une page publique vieillit au premier changement de mesure. Les nombres de l'audit ont changé trois fois en une journée.

**Ce que cela change.** La porte de vérification recalcule l'état depuis le catalogue et exige que la page de transparence contienne exactement la phrase dérivée : échecs, constats, nombre de contrôles et nombre de relectures consignées.

**Preuves dans le dépôt :**

- `outils/verifier-rd-continue.py`
- `transparence.html`
- `docs/apprentissage/audit-automatique.md`

**Contrôle qui la maintient :** `python3 outils/verifier-rd-continue.py`

**Limite — ce que cela ne prouve pas.** La phrase reste vraie sur ce que la machine mesure ; elle ne dit rien de la qualité des fiches et ne remplace aucune relecture.

**Suite.** Étendre le même principe à toute affirmation publique qui reprend un chiffre du dépôt.

Initiatives liées : `coherence-textes-publics`, `coordination-de-tous-les-agents`.

### `portail-declare-ou-erreur` — Une source-racine doit s'annoncer comme portail

*Consignée le 2026-10-20.*

**Constat.** Une fiche qui ne cite que la racine d'un site n'offre aucune page à confronter. Ce n'est pas mécaniquement faux, mais une racine présentée comme une page consultée laisse croire à une vérification qui n'a pas eu lieu.

**Ce que cela change.** Le contrôle de précision des sources distingue deux cas : racine annoncée par écrit comme portail, point d'entrée ou page d'accueil — constat ; racine présentée comme une page lue — échec. La discipline est vérifiable, pas déclarative.

**Preuves dans le dépôt :**

- `outils/auditer-prototypes.py`
- `outils/test_audit_prototypes.py`
- `docs/apprentissage/catalogue.toml`

**Contrôle qui la maintient :** `python3 outils/auditer-prototypes.py --verifier`

**Limite — ce que cela ne prouve pas.** La machine vérifie la présence de la phrase, pas sa sincérité ni la pertinence du portail. Elle ne dit pas si le portail suffit à étayer l'affirmation de la fiche.

**Suite.** Quand une page précise remplace un portail, consigner ce qu'elle étaye et ce qu'elle n'étaye pas, comme pour les douze fiches déjà traitées.

Initiatives liées : `relire-les-44-prototypes`, `veille-savoirs-evolutifs`.

### `refus-de-source-illisible` — Une source illisible se refuse et se consigne

*Consignée le 2026-10-20.*

**Constat.** Certaines pages utiles en apparence ne peuvent pas être lues : une page de l'IGN sur la lecture de carte répond 403, une page de présentation de HAL décrivait une fonctionnalité au lieu du mécanisme cherché. Les citer aurait fait baisser un compteur sans rien prouver.

**Ce que cela change.** Le refus devient une information du projet : la page écartée et sa raison sont écrites, et une autre page est cherchée quand elle existe. Un chiffre qui baisse sans explication est désormais un signal d'alerte, pas un progrès.

**Preuves dans le dépôt :**

- `docs/rd/journal.md`
- `docs/apprentissage/audit-automatique.md`

**Contrôle qui la maintient :** `python3 outils/verifier-rd-continue.py`

**Limite — ce que cela ne prouve pas.** Un refus consigné ne vaut pas preuve d'exhaustivité : d'autres pages accessibles peuvent exister et n'ont pas été cherchées.

**Suite.** Tenir une liste des sources refusées et de leur motif, pour éviter de les rechercher deux fois et pour documenter les angles morts.

Initiatives liées : `veille-savoirs-evolutifs`, `relire-les-44-prototypes`.

### `registre-des-avancees-verifie` — Une avancée sans preuve, contrôle et limite n'est pas une avancée

*Consignée le 2026-10-20.*

**Constat.** Les leçons d'un lot se perdent entre deux agents : elles restent dans un journal daté, mêlées à la chronologie, sans contrôle qui empêche de les déformer plus tard.

**Ce que cela change.** Ce registre est généré et vérifié : chaque entrée exige une preuve locale qui existe, un contrôle exécutable, une limite écrite, une suite et une initiative du portefeuille. Le fichier publié est comparé à la source par la porte de vérification.

**Preuves dans le dépôt :**

- `docs/rd/avancees.toml`
- `outils/construire-avancees.py`
- `outils/test_avancees.py`

**Contrôle qui la maintient :** `python3 outils/test_avancees.py && python3 outils/construire-avancees.py --verifier`

**Limite — ce que cela ne prouve pas.** Le registre vérifie la forme et la traçabilité, pas la vérité de l'avancée : une limite mal choisie passe le contrôle. C'est une mémoire disciplinée, pas une expertise.

**Suite.** Relire ce registre à chaque revue du portefeuille et y verser les avancées du lot suivant, en supprimant celles qui seraient devenues fausses.

Initiatives liées : `coordination-de-tous-les-agents`.

### `registre-des-refus-verifie` — Une source refusée entre dans un registre relié au catalogue, pas seulement dans le journal

*Consignée le 2026-10-20.*

**Constat.** Noter un refus de source dans le seul journal chronologique n'empêche pas un lot suivant de retenter la même page en 403 ou hors périmètre, ni de l'inscrire par inadvertance dans le catalogue.

**Ce que cela change.** Le registre `docs/apprentissage/sources-refusees.toml` et son générateur vérifient que chaque refus porte sa date, son motif et sa limite, qu'aucune URL refusée n'est citée comme source active du catalogue, et qu'un refus dit remplacé pointe une URL réellement présente sur la fiche.

**Preuves dans le dépôt :**

- `docs/apprentissage/sources-refusees.toml`
- `docs/apprentissage/sources-refusees.md`
- `outils/construire-sources-refusees.py`
- `outils/test_sources_refusees.py`

**Contrôle qui la maintient :** `python3 outils/test_sources_refusees.py && python3 outils/construire-sources-refusees.py --verifier`

**Limite — ce que cela ne prouve pas.** Ce registre ne recense que les pages effectivement tentées puis écartées par un agent ou une personne : il ne prouve ni l'exhaustivité des recherches documentaires, ni la validité de la source de remplacement.

**Suite.** Consigner chaque nouveau refus (403, accès payant, page retirée ou hors sujet après lecture) dans ce registre au moment où il survient.

Initiatives liées : `sources-fermees-et-registre-des-refus`, `relire-les-44-prototypes`, `veille-savoirs-evolutifs`.

### `trois-etats-de-controle` — Un contrôle automatique a trois états, pas deux

*Consignée le 2026-10-20.*

**Constat.** Un même contrôle peut rencontrer trois situations distinctes : le fait est conforme, le fait est faux et réparable sans jugement, ou le fait est exact mais la machine ne sait pas s'il est acceptable. Traiter la troisième comme un échec fabrique de faux défauts ; la traiter comme un vert efface un reste réel.

**Ce que cela change.** L'audit automatique des prototypes ne compte plus seulement échecs et réussites : il nomme des constats, hors échecs et hors verts, et chaque interface qui reprend l'audit (paquets de relecture, phrase publique) reprend les trois états.

**Preuves dans le dépôt :**

- `outils/auditer-prototypes.py`
- `outils/test_audit_prototypes.py`
- `docs/apprentissage/audit-automatique.md`

**Contrôle qui la maintient :** `python3 outils/test_audit_prototypes.py && python3 outils/auditer-prototypes.py --verifier`

**Limite — ce que cela ne prouve pas.** Ce partage ne dit rien de la valeur d'une fiche : il déplace seulement la frontière entre ce qu'un script tranche et ce qu'une personne doit trancher. Un constat nommé n'est ni une relecture ni une validation.

**Suite.** Éprouver le même partage sur d'autres contrôles à venir : avant d'ajouter un contrôle, se demander s'il peut produire un constat plutôt qu'un échec.

Initiatives liées : `relire-les-44-prototypes`.

## 3. Ce que ce registre ne dit pas

- Il ne dit pas qu'une fiche est relue, juste ou publiable : la relecture humaine reste dans `docs/apprentissage/relectures.toml`.
- Il ne remplace pas le journal : le journal garde l'ordre des décisions, ce registre garde ce qui reste vrai après elles.
- Il ne détecte pas une avancée devenue fausse : seule une personne qui relit le registre peut retirer une entrée.
- Il ne mesure ni usage, ni qualité, ni apprentissage : aucun chiffre d'audience n'y entre.

## 4. Ajouter une avancée

1. Vérifier que l'apprentissage reste vrai au-delà du lot : sinon, c'est une note de journal.
2. Écrire l'entrée dans `docs/rd/avancees.toml` : constat, changement, deux preuves locales au moins, contrôle exécutable, limite d'au moins 120 caractères, suite, initiative du portefeuille.
3. Régénérer avec `python3 outils/construire-avancees.py`, puis lancer `python3 outils/test_avancees.py`.
4. Retirer sans regret une entrée devenue fausse : la mémoire du projet n'est pas un palmarès.

Généré depuis `docs/rd/avancees.toml` ; vérifier avec `--verifier`.
