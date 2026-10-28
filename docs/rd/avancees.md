# Avancées réutilisables de la R&D

**Document de travail généré.** Il ne certifie rien et ne remplace ni une relecture, ni un audit, ni une décision éditoriale. Il retient ce qu'un lot a appris de durable, avec la preuve locale qui le soutient, le contrôle qui le maintient et la limite qui l'accompagne.

**À quoi cela sert :** un autre agent reprend le projet sans avoir à reconstituer l'histoire. Chaque entrée dit aussi ce qu'elle ne prouve pas, pour qu'une avancée ne se transforme pas en argument d'autorité.

**Date du registre :** 2026-10-28 — dernière revue consignée dans `avancees.toml`. Cette sortie ne dépend pas du jour où elle est régénérée.

## 1. Vue d'ensemble

| Mesure | Valeur |
| --- | ---: |
| Avancées consignées | 20 |
| Période couverte | du 2026-10-20 au 2026-10-28 |
| Contrôles exécutables cités | 26 |
| Initiatives du portefeuille concernées | 12 |

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

### `sortie-commitee-sans-horloge` — Une sortie commitée ne se date pas avec l'horloge

*Consignée le 2026-10-22.*

**Constat.** Deux fichiers générés et commités portaient la date du jour de leur génération. Comparés octet par octet par une porte CI, ils divergeaient dès le lendemain sans qu'aucun contenu ait changé : la porte « qualite » et la publication du site échouaient, et régénérer réparait le jour même en re-cassant le suivant.

**Ce que cela change.** L'horodatage des sorties vient désormais des registres — `meta.derniere_revue` pour les avancées, la plus récente `revue_le` du catalogue pour l'audit — et non de `date.today()`. La validation, elle, continue de juger les dates au jour réel. Un contrôle rejoue toutes les portes CI qui comparent un fichier généré avec une horloge déplacée de +37 et +400 jours, et prouve par mutation qu'il détecte bien un générateur fautif.

**Preuves dans le dépôt :**

- `outils/construire-avancees.py`
- `outils/auditer-prototypes.py`
- `outils/test_reproductibilite_artefacts.py`
- `docs/rd/avancees.md`
- `docs/apprentissage/audit-automatique.md`

**Contrôle qui la maintient :** `python3 outils/test_reproductibilite_artefacts.py && python3 outils/verifier-rd-continue.py`

**Limite — ce que cela ne prouve pas.** Le contrôle prouve qu'une sortie est stable, jamais qu'une date est juste : la véracité d'une date de revue reste une relecture humaine. Il ne couvre pas non plus les scripts d'un futur lot, ni les rapports non commités de la veille, qui restent hors du périmètre comparé.

**Suite.** Étendre la règle au prochain générateur ajouté : si sa sortie est commitée puis comparée, son horodatage doit venir d'une donnée du dépôt et une entrée doit être ajoutée aux portes rejouées.

Initiatives liées : `optimisation-du-site`, `coordination-de-tous-les-agents`.

### `boite-non-nulle-nest-pas-affichee` — Une boîte non nulle ne prouve pas qu'un élément est affiché

*Consignée le 2026-10-23.*

**Constat.** Un balayage de la taille des cibles a signalé 50 liens de 15 px sur `apprendre.html`. Ils étaient dans des `<details>` refermés : Chromium leur donne une boîte non nulle, un texte vide et une position, alors que personne ne les voit et qu'aucun clavier ne les atteint. Le même angle mort menaçait la lecture à voix haute livrée la veille, dont le filtre reposait sur `getClientRects` seul.

**Ce que cela change.** Quatre cas ont été mesurés et séparés : `display:none` donne un texte mais pas de boîte, `visibility:hidden` et un `<details>` refermé donnent une boîte mais pas de texte, `aria-hidden` est visible pour l'œil et doit être écarté à part. Toute liste d'éléments « affichés » du dépôt — lecture à voix haute, audit des cibles, échantillon de focus — vérifie désormais `checkVisibility({ checkVisibilityCSS: true, contentVisibilityAuto: true })`, garde `getClientRects` et `innerText` en secours, et écarte `details:not([open])` explicitement.

**Preuves dans le dépôt :**

- `assets/js/site.js`
- `outils/auditer-criteres-22.mjs`
- `outils/verifier-affichages.py`
- `outils/test-experience.cjs`
- `docs/rd/inclusion-criteres-wcag-22.md`

**Contrôle qui la maintient :** `python3 outils/verifier-affichages.py && node outils/test-experience.cjs`

**Limite — ce que cela ne prouve pas.** Ces trois signaux décrivent un rendu dans Chromium, pas la perception : un contenu à contraste insuffisant, hors cadre après défilement ou recouvert par un bandeau reste « affiché » pour la mesure. Le cas d'un contenu animé, d'un iframe ou d'un canvas n'est pas couvert, et aucun de ces tests ne remplace une passe au clavier avec un lecteur d'écran.

**Suite.** Reprendre ce filtre pour tout futur balayage d'éléments interactifs, et vérifier qu'aucun script du dépôt ne conclut « visible » à partir d'une seule mesure de boîte.

Initiatives liées : `optimisation-du-site`, `ecouter-la-page`.

### `ecouter-sans-promettre-une-conformite` — Une aide d'inclusion se mesure sur ce qu'elle n'envoie pas, pas sur ce qu'elle déclare

*Consignée le 2026-10-23.*

**Constat.** Une lecture à voix haute pouvait sembler une simple fonctionnalité de confort. Trois vérifications en ont fait une décision de conception : le texte lu ne doit jamais quitter l'appareil, la commande ne doit pas exister sur un appareil sans voix, et le résultat ne doit jamais être présenté comme une conformité. Un service public a d'ailleurs été mis en demeure en juin 2026 pour avoir déclaré « totalement conforme » un espace mesuré à 42,11 %.

**Ce que cela change.** Toute aide d'accessibilité ajoutée au site est désormais instruite comme une option comparée de la note prospective, avec sa source externe, son coût, son repli et ses limites publiées à côté de la commande. Trois garanties sont vérifiables dans le code plutôt que dans une intention : aucune création de la commande sans moteur de synthèse, aucun envoi réseau dans le module, et langue de chaque bloc respectée. Le contrôle statique refuse un `fetch`, un appel à un service de synthèse et une commande construite mais jamais ajoutée au panneau.

**Preuves dans le dépôt :**

- `docs/rd/inclusion-lecture-vocale.md`
- `assets/js/site.js`
- `outils/verifier-affichages.py`
- `outils/test-experience.cjs`
- `outils/verifier-accessibilite.cjs`

**Contrôle qui la maintient :** `python3 outils/verifier-affichages.py && node outils/test-experience.cjs && node outils/verifier-accessibilite.cjs`

**Limite — ce que cela ne prouve pas.** Aucune voix réelle n'a été écoutée, aucun lecteur d'écran n'a été utilisé et aucune personne n'a essayé la commande : le banc remplace `speechSynthesis` par un double qui enregistre les énoncés. La limite affichée sous le bouton dit seulement ce que le dispositif ne peut pas garantir ; elle ne prouve aucune amélioration de compréhension, et les chiffres d'effet cités viennent d'études scolaires anglophones.

**Suite.** Faire écouter la fonction à une personne qui lit difficilement et à une personne utilisant un lecteur d'écran, puis consigner les mots mal prononcés et le cran de vitesse qui lui convient ; retirer le lot si la voix perd le fil ou si un bloc est lu deux fois.

Initiatives liées : `ecouter-la-page`.

### `reponse-chiffree-reliee-au-test` — Vérifier le résultat écrit dans la fiche, pas seulement un calcul parallèle

*Consignée le 2026-10-24.*

**Constat.** Un test peut recalculer une moyenne exacte sans repérer une réponse fausse écrite dans le catalogue. L'ajout d'une fiche faisait aussi croître les totaux attendus d'anciens relevés axe, comme si une nouvelle page avait été mesurée automatiquement.

**Ce que cela change.** Les exemples du lot moyenne/médiane sont reliés à leurs passages de correction dans le catalogue. Deux mutations des réponses doivent échouer. Les compteurs courants sont distingués des anciens relevés d'accessibilité, conservés à leur périmètre daté.

**Preuves dans le dépôt :**

- `outils/test_exemples_statistiques.py`
- `docs/apprentissage/catalogue.toml`
- `docs/rd/lot-statistiques-2026-10-24.md`
- `outils/verifier-site-statique.py`

**Contrôle qui la maintient :** `python3 outils/test_exemples_statistiques.py && python3 outils/verifier-site-statique.py`

**Limite — ce que cela ne prouve pas.** Les contrôles portent sur des passages identifiés et des calculs finis : ils ne comprennent pas la totalité du texte, ne prouvent pas l'efficacité d'une analogie et ne remplacent aucune relecture mathématique ou pédagogique indépendante.

**Suite.** Faire relire les deux fiches et leurs tâches candidates, puis étendre les assertions aux prochains exemples sans transformer une correction automatique en promesse de compréhension.

Initiatives liées : `relire-les-44-prototypes`, `co-conception-et-essais`.

### `un-espacement-impose-casse-la-page` — Un espacement imposé casse la page avant de la rendre lisible

*Consignée le 2026-10-24.*

**Constat.** Le critère WCAG 1.4.12 ne demande pas d'afficher un texte espacé, mais de supporter qu'une personne impose interligne 1,5, interlettrage 0,12 em, espacement des mots 0,16 em et 2 em après chaque paragraphe. Appliqué aux 98 pages, il a sorti la barre de navigation du cadre de 47 à 56 px entre 1 261 et 1 366 px — « Nous contacter » finissait hors de la fenêtre — et fait déborder les 84 fiches de 22 px à 1 280 px. Aucun des deux défauts ne se voyait sans imposer cet espacement.

**Ce que cela change.** `outils/auditer-criteres-22.mjs` applique les quatre valeurs du critère en `!important`, puis cherche deux pertes : une page qui se met à défiler horizontalement et un texte rogné par un ancêtre en `overflow: hidden` ou `clip`, nœud de texte par nœud de texte. Deux corrections sont livrées : `flex-wrap: wrap` sur `.nav-links`, qui laisse la ligne unique tant qu'elle tient, et `white-space: normal` sur le seul bouton de la colonne latérale d'une fiche. Un seizième contrôle de `verifier-affichages.py` refuse le retour en arrière.

**Preuves dans le dépôt :**

- `outils/auditer-criteres-22.mjs`
- `outils/verifier-affichages.py`
- `assets/css/site.css`
- `docs/rd/formats-affichage.md`
- `docs/rd/inclusion-criteres-wcag-22.md`
- `docs/rd/audit-criteres-22-2026-10-24.json`
- `transparence.html`

**Contrôle qui la maintient :** `python3 outils/verifier-affichages.py && node outils/auditer-criteres-22.mjs`

**Limite — ce que cela ne prouve pas.** La mesure voit un débordement et un rognage, pas une perte de sens : un chevauchement partiel, une coupure de mot, un texte masqué par un `clip-path` sans `overflow` ou déplacé hors du champ visible sans déborder lui échappent. Aucune personne n'a relu ce critère, et rien ne prouve qu'une personne qui a besoin de cet espacement lit mieux la page : c'est une géométrie, pas un usage.

**Suite.** Faire lire la page à une personne qui agrandit l'interlettrage, puis étendre la mesure au zoom 200 % et au critère 1.4.10 (redistribution du contenu), qui n'ont jamais été éprouvés ici.

Initiatives liées : `optimisation-du-site`.

### `un-total-sans-son-manque` — Un total de mesure doit dire ce qu'il n'a pas mesuré

*Consignée le 2026-10-24.*

**Constat.** Le relevé WCAG 2.2 publiait « 825 éléments testés, 0 entièrement masqué » alors que le site compte 8 856 cibles atteignables : le plafond de 60 par page et les huit pages de l'échantillon coupaient la passe sans que le chiffre le dise. `anglais-aventure.html` en compte 448, dont 60 seulement étaient portées au focus. Le même outil, lancé sans serveur local, rendait « 0 cible, 0 masquée » — indiscernable d'une page parfaite.

**Ce que cela change.** Le plafond passe à 500, au-delà du maximum observé, le focus est mesuré sur les 98 pages aux deux largeurs, le bilan publie les pages coupées et les cibles non testées, et un chargement en échec est compté comme un échec — avec sortie en erreur si toutes les pages échouent. Résultat du 24 octobre 2026 : 8 856 éléments testés sur 8 856 atteignables, 0 masqué, 0 page coupée ; relevé conservé dans `docs/rd/audit-criteres-22-2026-10-24.json`.

**Preuves dans le dépôt :**

- `outils/auditer-criteres-22.mjs`
- `docs/rd/audit-criteres-22-2026-10-24.json`
- `docs/rd/inclusion-criteres-wcag-22.md`

**Contrôle qui la maintient :** `node outils/auditer-criteres-22.mjs --sans-focus && python3 outils/verifier-rd-continue.py`

**Limite — ce que cela ne prouve pas.** Le chiffre est plus honnête, pas plus concluant : cinq points par élément ne disent rien de la lisibilité du contour de focus, le recouvrement n'est testé qu'après un défilement que la mesure provoque elle-même, et un bandeau qui apparaît au clavier réel n'est pas reproduit. Aucun lecteur d'écran ni appareil réel n'a servi à cette passe.

**Suite.** Appliquer la même règle aux autres mesures du dépôt : tout script qui publie un total doit publier aussi ce qu'il a écarté, et refuser de rendre « zéro » quand il n'a rien pu charger.

Initiatives liées : `optimisation-du-site`, `ecouter-la-page`.

### `un-trace-remplace-une-photo-de-logo` — Restaurer une identité refusée plutôt que défendre son remplacement

*Consignée le 2026-10-24.*

**Constat.** Les tracés SVG introduits le 24 octobre ont été rejetés : leur netteté ne justifiait pas une réinterprétation de l'identité. Sur la page IA, des règles mobiles déplaçaient les pastilles mais pas les extrémités des rayons.

**Ce que cela change.** Les images antérieures de l'accueil et d'Apprendre sont restaurées avec leurs variantes et proportions. L'accueil est plafonné à 700 CSS px pour sa source de 1400 px à densité 2. La constellation utilise des ancres identiques sur téléphone et bureau, vérifiées dans un navigateur.

**Preuves dans le dépôt :**

- `assets/images/accueil-logo-mrsc-3d.jpg`
- `assets/images/mondes-savoirs-hero.jpg`
- `outils/verifier-graphismes.cjs`
- `docs/rd/ligne-graphique.md`
- `docs/rd/audit-graphismes-2026-10-24.json`

**Contrôle qui la maintient :** `python3 outils/verifier-affichages.py && node outils/verifier-graphismes.cjs`

**Limite — ce que cela ne prouve pas.** Trois visuels seulement, Chromium, densités 1 et 2 : ni validation de tout le site, ni contraste mesuré sur les pixels des images, ni avis humain sur téléphone. Les illustrations restaurées ne sont pas des photographies documentaires.

**Suite.** Étendre le contrôle aux autres visuels et aux densités supérieures, mesurer le contraste et faire relire la direction photographique.

Initiatives liées : `optimisation-du-site`.

### `controle-preventif-qui-prouve-qu-il-mord` — Un contrôle préventif qui ne trouve rien doit prouver qu'il mord

*Consignée le 2026-10-28.*

**Constat.** Le contrôle `outils/verifier-taux-dates.py`, écrit le 28 octobre 2026 pour empêcher qu'une fiche recopie un taux de cotisation sans sa date, rend « 85 fiches contrôlées, 0 défaut » : le catalogue est propre, et un contrôle qui ne signale jamais rien est indiscernable d'un contrôle cassé. C'est le même piège que le relevé WCAG publiant « 0 élément masqué » quand il n'avait rien pu charger.

**Ce que cela change.** Le contrôle est livré avec `outils/test_verifier_taux_dates.py`, qui plante dans une copie du catalogue les quatre fautes qu'il doit voir — taux sans année, montant légal sans année, règle datée sans source datée, phrase dans une liste — et qui rejoue l'outil par sous-processus pour vérifier que la sortie en erreur est bien celle du programme, pas seulement d'une fonction. Chaque ligne verte du dépôt vaut donc pour ce qu'elle prouve : une phrase acceptée est une phrase dont la forme est datée, pas une phrase exacte.

**Preuves dans le dépôt :**

- `outils/verifier-taux-dates.py`
- `outils/test_verifier_taux_dates.py`
- `docs/rd/sujet-revenus-salaire-impots.md`

**Contrôle qui la maintient :** `python3 outils/test_verifier_taux_dates.py && python3 outils/verifier-taux-dates.py && python3 outils/verifier-rd-continue.py`

**Limite — ce que cela ne prouve pas.** Le contrôle ne lit que des chiffres écrits en pourcentage ou en euros et qu'un vocabulaire fermé de droit, de fiscalité et de protection sociale : une règle écrite en toutes lettres (« le dixième du brut ») ou un taux cité sans le mot attendu lui échappent, et il ne compare aucun barème à sa date. Ses quatorze tests disent qu'il détecte les cas plantés, pas qu'il couvre les cas réels. Il ne remplace ni la relecture compétente du domaine ni l'ouverture de la source officielle.

**Suite.** Deux portes sont désormais éprouvées par mutation (`verifier-affichages.py`, `verifier-site-statique.py`, dix fautes plantées au total, aides partagées dans `outils/banc_mutations.py`). L'inventaire écrit des outils a depuis été livré et tenu par un garde : `docs/rd/inventaire-controles.md` et `outils/verifier-inventaire-controles.py` (45 fichiers, 37 contrôles, 17 appuyés sur un test capable d'échouer). La suite est de combler les écarts par ordre de rentabilité, en commençant par `verifier-securite.py`.

Initiatives liées : `cartographier-les-lacunes`, `relire-les-44-prototypes`.

### `inventaire-des-controles-tenu-par-un-garde` — Un inventaire des contrôles ne vaut que s'il échoue quand on l'oublie

*Consignée le 2026-10-28.*

**Constat.** Le 28 octobre 2026, l'inventaire écrit des outils du dépôt a rendu un chiffre désagréable : sur 37 contrôles, 17 seulement s'appuient sur un test capable d'échouer. Mais un inventaire tenu à la main devient faux au premier outil ajouté, et rien dans la CI ne l'aurait signalé : le document aurait décrit un dépôt qui n'existe plus, en donnant l'impression que le sujet était traité.

**Ce que cela change.** `outils/verifier-inventaire-controles.py` lit le tableau de `docs/rd/inventaire-controles.md` et échoue si un fichier d'`outils/` n'y figure pas, si une ligne désigne un outil absent, si un statut sort des six admis ou si le fichier de test annoncé n'existe pas. Il ne juge pas les statuts — il empêche seulement l'inventaire de mentir par omission. Son propre banc, `outils/test_verifier_inventaire_controles.py`, plante cinq fautes dans une copie complète du dépôt, dont celle qui compte : un outil ajouté sans ligne. Les deux tournent dans `verification.yml` et dans `deploy-pages.yml`, et `AGENTS.md` exige la ligne dans le même commit que l'outil.

**Preuves dans le dépôt :**

- `outils/verifier-inventaire-controles.py`
- `outils/test_verifier_inventaire_controles.py`
- `docs/rd/inventaire-controles.md`
- `AGENTS.md`
- `outils/banc_mutations.py`

**Contrôle qui la maintient :** `python3 outils/test_verifier_inventaire_controles.py && python3 outils/verifier-inventaire-controles.py`

**Limite — ce que cela ne prouve pas.** Le garde vérifie la forme de l'inventaire, jamais la justesse d'un statut : une ligne qui déclare `banc` en citant un test existant mais sans rapport passerait. La couverture repose sur une convention de nommage (`test_*`, `__*` exclus) : un outil rangé ailleurs, ou un fichier d'aide nommé comme un contrôle, fausse le compte sans être vu. Enfin l'inventaire lui-même n'a été rempli qu'en lisant les tests, sans exécuter chaque mutation possible — c'est un jugement daté, pas une mesure.

**Suite.** Prendre les contrôles par ordre de rentabilité écrite dans l'inventaire : `verifier-securite.py` n'a aucun test, puis `verifier-fusions.py`, puis les deux portes de publication, puis `auditer-criteres-22.mjs` et son « 0 élément masqué » publié sans avoir rien pu charger. Chaque nouveau banc met à jour la ligne correspondante dans le même commit.

Initiatives liées : `optimisation-du-site`, `cartographier-les-lacunes`.

### `taux-date-hors-de-la-fiche` — Un taux daté n'entre pas dans une fiche : on enseigne la vérification, pas le chiffre

*Consignée le 2026-10-28.*

**Constat.** La fiche F2302 de Service-Public, vérifiée le 1er janvier 2026, publie des taux et des plafonds de cotisations salariales (assurance vieillesse, CSG dont une part non déductible, CRDS, retraites complémentaires) qui changent en tout ou partie à chaque exercice. Une fiche qui écrirait « la CSG est de 9,2 % » deviendrait fausse sans qu'aucun contrôle du dépôt ne le voie : ni `auditer-prototypes.py`, qui juge la forme et les sources, ni le prototype de confrontation, qui cherche des ancres lexicales, ne comparent un barème à sa date.

**Ce que cela change.** La carte `docs/rd/sujet-revenus-salaire-impots.md` borne le sujet à ce qui ne vieillit pas : l'ordre de lecture d'un bulletin fictif, les deux soustractions à refaire, et la distinction des trois montants appelés « net » (à payer, imposable, social). Les taux et plafonds sont cités une fois, avec la date de vérification de l'éditeur, puis renvoyés à la source officielle ; la fiche à venir ne doit en recopier aucun.

**Preuves dans le dépôt :**

- `docs/rd/sujet-revenus-salaire-impots.md`
- `docs/rd/carte-lacunes.md`
- `docs/rd/portefeuille.toml`

**Contrôle qui la maintient :** `python3 outils/construire-carte-lacunes.py --verifier && python3 outils/construire-avancees.py --verifier && python3 outils/verifier-rd-continue.py`

**Limite — ce que cela ne prouve pas.** Cette règle n'est pas automatisée : rien ne détecte aujourd'hui un pourcentage ou un plafond en euros écrit dans une fiche sans date, et la carte n'est pas une fiche. Aucune relecture par une personne compétente en paie ou en droit du travail n'a eu lieu, aucun essai avec des personnes non plus, et les quatre pages ont été lues une seule fois, le 28 octobre 2026 : une réforme peut les changer avant la première fiche.

**Suite.** Lors de la rédaction du prototype, vérifier qu'aucun taux ni plafond ne figure hors d'un encadré daté, puis examiner un contrôle qui signalerait dans une fiche d'économie un pourcentage présenté comme une connaissance stable.

Initiatives liées : `cartographier-les-lacunes`, `relire-les-44-prototypes`.

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
