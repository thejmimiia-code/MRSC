# Vote distanciel — document de convocation

**Pour la séance de délibération. Version du 20 octobre 2026. Ce document ne décide rien : il prépare une réunion de 60 à 90 minutes et se lit en une vingtaine de minutes.**

## 1. Ce qui est demandé avant la séance

Lire ce document, puis venir avec des objections plutôt qu’avec une préférence. Rien d’autre n’est demandé : ni préparation technique, ni connaissance des logiciels de vote, ni relecture des statuts page par page. Le dossier complet reste disponible pour qui veut l’ouvrir : [`vote-distanciel-dossier-deliberation.md`](vote-distanciel-dossier-deliberation.md).

Trois résultats sont attendus de la séance, et rien de plus :

1. confirmer quelle version des statuts est applicable, et si un règlement intérieur existe ;
2. choisir **un** profil de scrutin, ou `aucun` ;
3. choisir une voie : **A** (ne pas voter à distance), **B** (expertiser un service existant) ou **C** (auto-héberger un logiciel existant).

La décision se consigne ensuite dans les huit champs du §6 de [`vote-distanciel-decision.md`](vote-distanciel-decision.md). Tant qu’ils sont vides, la recherche reste documentaire et aucun système n’est construit.

## 2. Les huit profils, en une ligne chacun

Ces chiffres sont des **relevés de lecture** de la copie locale des statuts (25 pages, version « modification du 30 septembre 2020 », non confirmée applicable). Aucun n’est un paramètre réglable : ce sont des questions à poser au texte.

| Profil | Corps électoral | Quorum | Majorité | Procuration | Secret | Statut |
| --- | --- | --- | --- | --- | --- | --- |
| `bureau-executif` | Membres du Bureau présents ou représentés | Non relevé | Absolue, départage président | 1 | Non imposé | `a-faire-relire` |
| `conseil-ethique` | Conseil constitué, présents ou représentés | Non relevé | Absolue, départage propre | 1 | Non imposé | `a-faire-relire` |
| `territoriale-constitutive` | Membres présents | Non relevé | Blanc majoritaire → reprise | Non établie | **Imposé** | `a-faire-relire` |
| `ago-premiere` | Membres à jour de cotisation | 25 % | Absolue, départage président | 2 | Sur demande | `a-faire-relire` |
| `ago-seconde` | Membres à jour, même ordre du jour | Aucun minimum | Absolue, départage président | 2 | Sur demande | `a-faire-relire` |
| `age-premiere` | Membres | 51 % | Absolue | 1 | Non précisé | `a-faire-relire` |
| `age-seconde` | Membres, même ordre du jour | Aucun minimum | **Unanimité** | 1 | Non précisé | `a-faire-relire` |
| `dissolution` | À confirmer (art. 15 et 19) | 60 % puis 30 % | Deux tiers | À confirmer | À confirmer | `bloque-interpretation` |

Deux points à retenir, indépendants de tout logiciel :

- **`dissolution` ne peut pas être retenu** aujourd’hui : l’articulation des articles 15 et 19 n’est pas tranchée, et le contrôle automatique refuse ce profil dans la trace.
- **`ago-premiere` est le seul profil dont les statuts décrivent une session numérique** d’au moins sept jours. Cela ne suffit pas à le choisir : quatre questions du §3 restent ouvertes, dont ce qu’est une « réponse transmise » pour le quorum.

Le tableau ne classe rien. Un profil simple n’est pas meilleur qu’un profil complexe : il est seulement plus facile à éprouver avant de s’y engager.

## 3. Les huit ambiguïtés à trancher

Aucune ne relève de l’informatique. Aucune ne peut être tranchée par un outil, ni par un agent. Tant qu’elles sont ouvertes, aucun profil ne peut être configuré.

| # | Question | Ce qui reste bloqué | Qui peut trancher |
| --- | --- | --- | --- |
| 1 | Une connexion, une réponse vide, un bulletin blanc ou une délégation comptent-ils pareillement dans chaque quorum ? | Le calcul du quorum de tous les profils | Association et relecture juridique |
| 2 | Comment appliquer une voix prépondérante identifiable dans un scrutin secret ? | AGO et Bureau | Relecture juridique |
| 3 | Comment un mandataire vote-t-il pour un mandant sans que leurs choix soient révélés ? | Le régime des procurations | Relecture juridique et cryptographique |
| 4 | Comment qualifier les membres « concernés ou impactés », et comment contester cette qualification ? | L’éligibilité par question | Association |
| 5 | Comment articuler l’article 15 et les seuils de l’article 19 pour la dissolution ? | Le profil dissolution | Relecture juridique |
| 6 | Le bulletin blanc est-il décompté partout, ou seulement à la constitution territoriale ? | Le dépouillement de chaque profil | Association |
| 7 | Le passage « tout moyen reconnu valable par l’ensemble des membres » vaut-il approbation d’un protocole précis ? | La base juridique d’un protocole | Relecture juridique |
| 8 | La copie locale des statuts est-elle la version opposable, et existe-t-il un règlement intérieur ? | **Tout le reste** | Association |

L’ambiguïté 8 commande les sept autres. Si elle n’est pas tranchée en séance, les décisions 2 et 3 ci-dessus ne peuvent pas être prises le même jour : il faudra d’abord vérifier la version en vigueur.

## 4. Les trois voies, en trois phrases

- **A — Ne pas voter à distance.** On garde le présentiel et on étudie seulement les moyens de participation qui ne sont pas un scrutin électronique : procuration, consultation écrite, débat à distance, séance décalée. A n’est pas « ne rien faire » : c’est un choix qui exige ses propres preuves sur l’égalité d’accès.
- **B — Expertiser un service existant.** On choisit **un** candidat et une version précise, puis on examine droit, contrat, métadonnées, preuves exportables, audits et réversibilité. Rien n’est installé à ce stade.
- **C — Auto-héberger un logiciel existant.** On exploite un logiciel libre sur une infrastructure maîtrisée, sans écrire de cryptographie. Cela exige des personnes nommées pour l’exploitation, les clés et les incidents, ainsi qu’une permanence pendant toute la fenêtre de vote.

**La voie D — construire un système — est bloquée** : elle supposerait d’inventer des primitives cryptographiques locales, ce que le cadrage interdit. `aucun` reste une réponse valide pour le profil, et il n’est compatible qu’avec la voie A.

## 5. Ce qui ne sera pas demandé ce jour-là

- Aucune identité, aucun bulletin, aucune clé, aucune donnée personnelle : rien de tel n’est recueilli, ni en séance, ni après.
- Aucun choix de logiciel, de version ou d’hébergeur.
- Aucune décision technique présentée comme acquise : le dossier ne sélectionne aucun candidat et n’ordonne aucun profil.
- Aucune promesse publique de sécurité : « sécurisé » n’est pas une propriété démontrable, et dix menaces restent à expertiser.

## 6. Comment se termine la séance

Deux issues seulement, toutes deux acceptables :

- **une décision** : le profil (ou `aucun`), la voie, les dates, l’instance décideuse, et les objections non résolues consignées au §10 du dossier ;
- **une décision de reporter** : la même trace reste vide, avec la raison du report écrite dans le journal de R&D.

Une objection consignée n’est pas un échec. Une objection effacée pour faire apparaître un consensus en est un.
