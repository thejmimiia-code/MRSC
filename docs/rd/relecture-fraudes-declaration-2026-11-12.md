# Relecture par agent — déclarer une fraude, 12 novembre 2026

**Date : 2026-11-12. Auteur : agent. Statut : relu par agent, sources confrontées.**

Ce document n’est ni une validation humaine, ni une expertise, ni un avis juridique,
ni un essai avec des personnes. Il est la trace d’une étape de vérification
exécutable : `outils/verifier-relecture-contenus.py`, câblée dans la CI et éprouvée
par `outils/test_mutations_relecture_contenus.py`. Le registre
`docs/apprentissage/relectures.toml` reste le seul endroit des relectures humaines :
il contient toujours zéro entrée et l’agent n’y a rien écrit.

## 1. Demande et décision d’ordre

La demande du 12 novembre 2026 portait sur quatre points à la fois : l’optimisation
de la lecture, l’information, le sourçage, la prévention — et **surtout la
déclaration** (« et surtout les déclarer »). L’inventaire a montré que la base
existait déjà : la section `#fraudes-ia` de `ia-societe.html` et cinq fiches du
domaine Numérique traitaient de la prévention et du signalement, avec une seule
phrase sur la déclaration (`p.ai-fraud-reporting`, ligne 309 du fichier d’alors).

Le lot ne réécrit donc pas la prévention : il **ajoute la partie manquante** et
nomme les quatre démarches que le public confond le plus souvent — signaler à une
plateforme, déclarer à sa banque, prévenir l’organisme imité, porter plainte.

## 2. Ce qui a changé

| Fichier | Changement |
| --- | --- |
| `ia-societe.html` | Nouveau bloc `.ai-fraud-declare` : six étapes ordonnées, un tableau de canaux par support, une mise en garde sur ce qu’aucune démarche ne garantit. La phrase de renvoi de `.ai-fraud-reporting` annonce ce bloc au lieu de le remplacer. Six sources officielles ajoutées à la liste des sources de la section. |
| `assets/css/site.css` | Styles du bloc « déclarer », sans nouveau palier de largeur : colonnes en `auto-fit` sur largeur de piste, tailles en `clamp()`. Règles de contraste renforcé et de couleurs forcées étendues au nouveau bloc. |
| `docs/apprentissage/catalogue.toml` | Fiche `numerique-declarer-fraude`, `revue_le = 2026-11-12`, intervalle de 90 jours, 8 sources documentaires. Statut inchangé pour les autres fiches. |
| `docs/apprentissage/referentiel.toml` | La fiche rejoint le sujet `reagir-fraude-numerique`, qui portait déjà la réaction après incident. |
| `liens-utiles.html` | Deux entrées de démarche officielle : page Service-Public sur l’hameçonnage, page Cybermalveillance sur le dépôt de plainte. |
| `docs/rd-ia-usages-fraudes.md` | Section § 4 bis « Déclarer : quatre démarches, quatre interlocuteurs », cinq sources de déclaration dans le tableau du § 5, § 7 mis à jour. |
| Compteurs publics | 107 → 108 fiches, 81 → 82 prototypes, 122 → 123 pages HTML, dans les pages et les documents qui les annoncent. |

## 3. Sources lues et confrontées

Toutes ont été ouvertes le 12 novembre 2026. L’extrait mis en cache dans
`docs/rd/sources-primaires/` est une recopie manuelle des passages utiles, faite
depuis la page telle qu’elle a été lue ; il porte l’empreinte du corps et une ancre
de cinq mots au plus. Aucun accès réseau n’est disponible depuis l’outil de
vérification, d’où la recopie.

| Source | Ce qu’elle a permis d’écrire | Ce qu’elle ne dit pas |
| --- | --- | --- |
| [Service-Public.gouv.fr — hameçonnage (phishing ou vishing)](https://www.service-public.gouv.fr/particuliers/vosdroits/F34800) | « le hameçonnage est considéré comme un délit » ; « le signalement n’est pas une plainte » ; la plainte reste ouverte à la victime. | Rien sur les délais de traitement ni sur un remboursement. |
| [Service-Public.gouv.fr — arnaques sur internet (THESEE, Pharos)](https://www.service-public.gouv.fr/particuliers/vosdroits/N31138) | Les familles de situations que l’administration distingue et le renvoi vers Perceval. | Aucune procédure complète, aucun chiffre. |
| [Service-Public.gouv.fr — fraude à la carte bancaire](https://www.service-public.gouv.fr/particuliers/vosdroits/F31324) | Opposition d’abord, puis déclaration en ligne avec FranceConnect, récépissé délivré, traitement par la gendarmerie nationale. | Ne garantit ni disponibilité du service ni remboursement. |
| [Service-Public.gouv.fr — Pharos](https://www.service-public.gouv.fr/particuliers/vosdroits/R17674) | Le contenu signalé « est visualisé et sauvegardé » et peut être orienté vers un service d’enquête. | Ne dit rien des signalements non retenus ni des délais. |
| [Cybermalveillance.gouv.fr — déposer plainte](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/page/deposer-plainte-cybermalveillance) | Les trois voies de plainte et l’accompagnement gratuit par France Victimes au 116 006. | N’est pas une autorité judiciaire et ne qualifie pas les faits. |
| [Cybermalveillance.gouv.fr — hameçonnage, que faire](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing) | Opposition immédiate, conservation des preuves, renvois vers Signal Spam, 33700, Phishing Initiative et Info Escroqueries. | Ne mesure ni l’efficacité des signalements ni les remboursements. |
| [Signal Spam](https://www.signal-spam.fr/) | Signalement par compte puis module de messagerie ; signalements partagés avec les acteurs compétents. | Aucune statistique de résultat ; pas de délai annoncé. |
| [33700](https://www.33700.fr/) | Signalement par formulaire ou capture d’écran ; envoi quotidien aux opérateurs. | Ne publie ni suites ni délais ; ne traite pas les courriels. |

## 4. Ce que la relecture ne couvre pas

- **Aucune expertise juridique.** Le registre ne dit pas si une situation relève
  d’une escroquerie, d’une usurpation d’identité ou d’une collecte frauduleuse de
  données : ces qualifications dépendent des faits et changent la procédure.
- **Aucun essai avec des personnes.** La lisibilité du bloc, la compréhension de
  l’ordre des démarches et l’accessibilité réelle (clavier, lecteur d’écran, fort
  zoom) restent à éprouver avec des personnes concernées, dont des victimes.
- **Aucune vérification de disponibilité future.** Les numéros, horaires et
  formulaires ont été lus le 12 novembre 2026 ; ils peuvent changer sans préavis.
  La fiche porte un intervalle de revue de 90 jours pour cette raison.
- **Aucune promotion de statut.** La fiche reste « Prototype à relire » avec sa
  note : les huit sources sont documentaires, les droits ne sont pas vérifiés, et
  aucune relecture humaine n’est consignée.
- **Le rendu à l’œil reste à la personne** : placement, style, densité du nouveau
  bloc sous 360 px, ordre de lecture. La vérification automatique ne lit pas de
  pixels.

## 5. Prochaine action suggérée

Faire relire la fiche `numerique-declarer-fraude` par une personne compétente en
droit pénal ou en accompagnement des victimes, en particulier la phrase sur la
pré-plainte THESEE et celle sur le courrier au procureur. Compte tenu de ce que
cette relecture est la condition d’une promotion de statut, elle doit rester
distincte de la lecture d’agent consignée ici.

## 6. Sources du lot du 12 novembre 2026, par identifiant

Chaque identifiant du registre `docs/rd/relecture-contenus.toml` et son URL, pour que la porte de relecture puisse confronter le rapport au registre.

| Identifiant | Source | URL |
| --- | --- | --- |
| `service-public-hameconnage` | Hameçonnage (phishing ou vishing) | https://www.service-public.gouv.fr/particuliers/vosdroits/F34800 |
| `service-public-arnaques-internet` | Arnaques sur internet (THESEE, Pharos ...) | https://www.service-public.gouv.fr/particuliers/vosdroits/N31138 |
| `service-public-perceval` | Fraude à la carte bancaire | https://www.service-public.gouv.fr/particuliers/vosdroits/F31324 |
| `service-public-pharos` | Signaler un contenu internet illégal (internet-signalement : Pharos) | https://www.service-public.gouv.fr/particuliers/vosdroits/R17674 |
| `cybermalveillance-deposer-plainte` | Déposer plainte après une cybermalveillance | https://www.cybermalveillance.gouv.fr/tous-nos-contenus/page/deposer-plainte-cybermalveillance |
| `cybermalveillance-hameconnage-victime` | Que faire en cas de phishing ou hameçonnage ? | https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing |
| `signal-spam-accueil` | Signal Spam — plateforme nationale de signalement de courriels indésirables | https://www.signal-spam.fr/ |
| `33700-accueil` | 33700 — plateforme de lutte contre les SMS et appels indésirables | https://www.33700.fr/ |
