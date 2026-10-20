# Vote distanciel — dossier de délibération de l’association

**Version du 20 octobre 2026. Statut : `a-deliberer`. Aucun système de vote n’existe dans le projet, aucun scrutin n’est autorisé, et ce dossier ne recommande ni profil ni voie.** Il rassemble les éléments nécessaires pour que l’association prenne une décision tracée ; il ne la prend pas à sa place.

## 1. À quoi sert ce dossier

Le brief [`vote-distanciel-decision.md`](vote-distanciel-decision.md) demande deux choix et une trace. Ce dossier les rend délibérables en une séance, sans expertise technique préalable, en rassemblant les huit profils, les trois voies ouvertes, les ambiguïtés à trancher et la question de l’emplacement d’un éventuel système.

Trois résultats sont attendus, à consigner ensemble :

1. confirmer la version applicable des statuts et l’existence d’un règlement intérieur ;
2. choisir un profil de scrutin — `aucun` est une réponse valide — et une voie A, B ou C ;
3. remplir la trace de huit champs du §6 de [`vote-distanciel-decision.md`](vote-distanciel-decision.md) et désigner les rôles du [`plan de revues`](vote-distanciel-revues.toml).

Durée indicative : 60 à 90 minutes, hors vérification documentaire préalable. Aucune donnée personnelle n’est nécessaire pour délibérer, seulement des règles et des rôles.

Ce que ce dossier n’est pas : un avis juridique, une comparaison de logiciels, une autorisation technique, ni une promesse de sécurité. Il ne modifie aucun statut et ne crée aucune compétence.

## 2. Ce qui est établi, ce qui ne l’est pas

| Élément | État réel | Preuve ou registre |
| --- | --- | --- |
| Copie des statuts | 25 pages, version « modification du 30 septembre 2020 », empreinte SHA-256 relevée | `assets/documents/statuts-2020.pdf` |
| Règles statutaires relevées | 18 relevés, tous `a-faire-relire` | [`vote-distanciel-regles.toml`](vote-distanciel-regles.toml) |
| Profils de scrutin | 8 profils, 7 `a-faire-relire`, dissolution `bloque-interpretation` | [`vote-distanciel-profils.toml`](vote-distanciel-profils.toml) |
| Menaces | 10 menaces documentées, toutes `a-expertiser` | [`vote-distanciel-menaces.toml`](vote-distanciel-menaces.toml) |
| Banc d’essai | 12 cas décrits, **aucun exécuté** | [`vote-distanciel-cas-essai.toml`](vote-distanciel-cas-essai.toml) |
| Candidats logiciels | 3 dépôts épinglés, **aucun audité ni sélectionné** | [`vote-distanciel-sources.toml`](vote-distanciel-sources.toml) |
| Grille de comparaison | 4 options, 15 critères bloquants, aucun score | [`vote-distanciel-comparaison.toml`](vote-distanciel-comparaison.toml) |
| Revues | 6 rôles et 5 revues, tous `a-attribuer` | [`vote-distanciel-revues.toml`](vote-distanciel-revues.toml) |
| Trace de décision | **vide : décision en attente** | [`vote-distanciel-decision.md`](vote-distanciel-decision.md) §6 |

Deux affirmations sont fausses et ne doivent pas entrer dans la délibération : « les statuts imposent un vote électronique » et « un logiciel libre suffit à garantir la sécurité ». La première contredit le relevé ; la seconde contredit le registre des menaces.

## 3. Les huit profils, un par un

Les nombres ci-dessous sont des **relevés de lecture**, pas des paramètres injectables. Un profil n’est ni une configuration, ni une interprétation juridique. Les identifiants renvoient à [`vote-distanciel-profils.toml`](vote-distanciel-profils.toml).

### 3.1 `bureau-executif` — Bureau exécutif

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | Membres du Bureau présents ou représentés | 10.1, p. 11 |
| Quorum et majorité | Majorité absolue ; voix du président prépondérante en cas d’égalité | 10.1, p. 11 |
| Procuration | Une au maximum par membre ; pouvoirs en blanc non pris en compte | 10.1, p. 11 |
| Secret | Non imposé par le relevé | 10.1, p. 11 |
| Procès-verbal | Signé | 10.1, p. 11 |
| Questions bloquantes | Qualifier présents et représentés dans une consultation différée ; décider si le scrutin doit être secret ; appliquer le départage sans contredire un secret éventuel | — |

Ce que voter à distance ajouterait ici : peu de gain de participation, beaucoup de questions de preuve. Le corps électoral est petit et la réunion peut déjà être électronique selon le relevé.

### 3.2 `conseil-ethique` — Conseil d’éthique

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | Membres constitués, présents ou représentés | 10.2.1, p. 13 |
| Quorum et majorité | Majorité absolue ; règle de départage propre, distincte du Bureau | 10.2.1, p. 13 |
| Procuration | Une au maximum par membre | 10.2.1, p. 13 |
| Secret | Non imposé par le relevé | 10.2.1, p. 13 |
| Questions bloquantes | Constituer et geler la liste des membres ; représenter la règle de départage propre ; décider si le litige traité exige le secret | — |

Point de vigilance : un scrutin sur un litige peut concerner des personnes nommées. Le secret et la minimisation des données y sont plus sensibles que dans un vote d’orientation générale.

### 3.3 `territoriale-constitutive` — Assemblée territoriale constitutive

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | Membres présents de l’assemblée | 11.6, p. 18 |
| Quorum et majorité | Non relevé dans cette passe ; blanc majoritaire entraînant une reprise avec de nouveaux candidats | 11.6, p. 18 |
| Procuration | Non établie dans le relevé | 11.6, p. 18 |
| Secret | **Imposé** : vote à bulletin secret | 11.6, p. 18 |
| Questions bloquantes | Une présence à distance satisfait-elle la notion de membre présent ; comment figer les candidatures et organiser la reprise ; les procurations sont-elles exclues ou seulement non décrites | — |

C’est le profil où le secret est explicitement écrit. Il est aussi celui où la notion de « présent » est la plus difficile à transposer à distance.

### 3.4 `ago-premiere` — Assemblée générale ordinaire, première convocation

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | Membres à jour de cotisation ; seules les questions à l’ordre du jour sont traitées | 14, p. 22 |
| Quorum | 25 % de présence nécessaire | 14, p. 22 |
| Majorité | Majorité absolue des présents et représentés ; départage par le président | 14, p. 22–23 |
| Procuration | Deux au maximum par membre ; pouvoirs en blanc non pris en compte | 14, p. 23 |
| Secret | Sur demande du président ou de la majorité des présents et représentés | 14, p. 23 |
| Session numérique | Ouverte au moins sept jours ; consultations écrites admises ; réponses transmises comptées dans le quorum | 14, p. 23 |
| Procès-verbal | Signé par le président ou le vice-président | 14, p. 23 |
| Questions bloquantes | Définir une « réponse transmise » ; arrêter le moment de la demande de scrutin secret ; articuler voix prépondérante et secret ; révoquer une procuration sans lier mandant et bulletin | — |

C’est le seul profil pour lequel les statuts décrivent explicitement une session numérique d’au moins sept jours. Cela ne suffit pas à le retenir : quatre questions restent ouvertes, et le quorum dépend d’une définition absente.

### 3.5 `ago-seconde` — Assemblée générale ordinaire, seconde convocation

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | Même ordre du jour, sept jours plus tard | 14, p. 22 |
| Quorum | Aucun minimum relevé | 14, p. 22 |
| Majorité | Majorité absolue des présents et représentés | 14, p. 22–23 |
| Procuration | Deux au maximum par membre | 14, p. 23 |
| Secret | Sur demande, comme en première convocation | 14, p. 23 |
| Questions bloquantes | Prouver le même ordre du jour ; dire si la durée numérique minimale s’applique ; articuler départage, secret et faible participation | — |

L’absence de quorum rend la participation faible plus lourde de conséquences : peu de votants peuvent décider beaucoup.

### 3.6 `age-premiere` — Assemblée générale extraordinaire, première convocation

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | Membres ; convocation demandée par le fondateur ou 51 % des membres | 15, p. 23–24 |
| Quorum | 51 % | 15, p. 24 |
| Majorité | Majorité absolue des présents et représentés | 15, p. 24 |
| Procuration | Une au maximum par membre | 15, p. 24 |
| Secret | Non précisé dans le relevé | 15, p. 24 |
| Questions bloquantes | Prouver la demande de convocation sans publier les identités ; déterminer la règle de secret ; définir le dénominateur du quorum | — |

Le seuil de 51 % rend ce profil particulièrement vulnérable à une panne, à une exclusion ou à une émission frauduleuse de droits.

### 3.7 `age-seconde` — Assemblée générale extraordinaire, seconde convocation

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | Même ordre du jour, quinze jours plus tard | 15, p. 24 |
| Quorum | Aucun minimum relevé | 15, p. 24 |
| Majorité | **Unanimité** des présents et représentés | 15, p. 24 |
| Procuration | Une au maximum par membre | 15, p. 24 |
| Secret | Non précisé dans le relevé | 15, p. 24 |
| Questions bloquantes | Prouver le même ordre du jour et le délai ; interpréter et vérifier l’unanimité ; déterminer la règle de secret | — |

L’unanimité est la règle la plus difficile à établir techniquement : elle exige de prouver l’absence d’opposition sans révéler les abstentions.

### 3.8 `dissolution` — Dissolution

| Élément | Relevé | Article et page |
| --- | --- | --- |
| Corps électoral | À confirmer avec les articles 15 et 19 | 15 et 19, p. 24–25 |
| Majorité | Deux tiers | 19, p. 25 |
| Quorum | 60 % en première instance, 30 % en seconde | 19, p. 25 |
| Statut | `bloque-interpretation` : l’articulation des articles 15 et 19 doit être relue par une personne compétente | — |

Ce profil ne peut pas être choisi dans la trace : le contrôle automatique le refuse. Il figure ici pour que la délibération sache pourquoi.

### 3.9 Tableau de synthèse — sans classement

| Profil | Corps électoral | Quorum | Majorité | Procuration | Secret | Statut |
| --- | --- | --- | --- | --- | --- | --- |
| `bureau-executif` | Bureau, présents et représentés | Non relevé | Absolue, départage président | 1 | Non imposé | `a-faire-relire` |
| `conseil-ethique` | Conseil constitué | Non relevé | Absolue, départage propre | 1 | Non imposé | `a-faire-relire` |
| `territoriale-constitutive` | Présents | Non relevé | Blanc majoritaire → reprise | Non établie | **Imposé** | `a-faire-relire` |
| `ago-premiere` | Membres à jour | 25 % | Absolue, départage président | 2 | Sur demande | `a-faire-relire` |
| `ago-seconde` | Membres à jour | Aucun minimum | Absolue, départage président | 2 | Sur demande | `a-faire-relire` |
| `age-premiere` | Membres | 51 % | Absolue | 1 | Non précisé | `a-faire-relire` |
| `age-seconde` | Membres | Aucun minimum | **Unanimité** | 1 | Non précisé | `a-faire-relire` |
| `dissolution` | À confirmer | 60 % puis 30 % | Deux tiers | À confirmer | À confirmer | `bloque-interpretation` |

Ce tableau ne hiérarchise rien. Un profil simple n’est pas meilleur qu’un profil complexe : il est seulement plus facile à éprouver.

## 4. Trois voies ouvertes, une voie bloquée

Les quatre options sont décrites dans [`vote-distanciel-comparaison.toml`](vote-distanciel-comparaison.toml). Aucune n’est évaluée à ce jour ; chacune reste `a-evaluer`.

### Voie A — Ne pas voter à distance

- **Ce que cela signifie :** maintenir le vote en présentiel et étudier seulement les moyens de participation à distance qui ne sont pas un scrutin électronique : procuration, consultation écrite, débat en visioconférence, séance décalée, aide au déplacement.
- **Ce qu’il faut réunir :** un inventaire des obstacles réels constatés, une revue d’accessibilité des solutions retenues, et une décision sur la procuration.
- **Ce que cela coûte :** rien en hébergement ni en cryptographie ; possiblement des déplacements et des exclusions de fait.
- **Limite à écrire :** l’option A n’est pas « ne rien faire ». C’est un choix qui exige ses propres preuves, notamment sur l’égalité d’accès.

### Voie B — Expertiser un service existant

- **Ce que cela signifie :** choisir **un** candidat et une version précise, puis examiner droit, contrat, métadonnées, preuves exportables, audits, réversibilité et juridiction du fournisseur.
- **Ce qu’il faut réunir :** l’accord écrit du fournisseur sur les données et les journaux, les rapports d’audit de la version exacte, un export complet vérifiable hors ligne, et une procédure de sortie.
- **Ce que cela coûte :** du temps d’expertise, une relecture juridique et parfois un abonnement.
- **Limite à écrire :** un service qui annonce « vérifiable de bout en bout » ne prouve ni la séparation identité–bulletin dans sa configuration réelle, ni la conformité au droit applicable.

### Voie C — Auto-héberger un logiciel existant

- **Ce que cela signifie :** héberger et exploiter un logiciel libre existant, sans écrire de cryptographie, sur une infrastructure maîtrisée.
- **Ce qu’il faut réunir :** des personnes nommées pour l’exploitation, les clés, la sécurité et les incidents ; une cérémonie de clés à plusieurs autorités ; des builds reproductibles et épinglés ; des sauvegardes testées ; une supervision ; un plan de mise à jour, de retrait et de destruction.
- **Ce que cela coûte :** un hébergement avec serveur, du temps d’exploitation continu, et une astreinte pendant la fenêtre de vote.
- **Limite à écrire :** auto-héberger ne supprime aucun risque du registre ; cela déplace la responsabilité vers l’association et ses bénévoles.

### Voie D — Construire un système

- **Statut : bloquée.** Elle supposerait d’inventer des primitives cryptographiques locales, ce que le cadrage interdit, et de traiter seul des problèmes que des projets spécialisés n’ont pas résolus.
- **Condition de réexamen :** aucune date n’est fixée. Elle ne peut être discutée qu’après évaluation des voies A, B et C, et jamais comme raccourci.

### Combinaisons à éviter

- Choisir B sans avoir lu un seul audit de la version visée.
- Choisir C sans personne nommée pour les clés et l’exploitation.
- Présenter A comme une absence de décision.
- Annoncer publiquement un « vote sécurisé » avant que les quinze conditions du §7 soient réunies.

## 5. Les huit ambiguïtés à trancher

Ces points ne relèvent pas de l’informatique. Ils relèvent des statuts, du droit et de l’association. Tant qu’ils sont ouverts, aucun profil ne peut être configuré.

| # | Question à trancher | Ce qui reste bloqué | Qui peut trancher | Preuve attendue |
| --- | --- | --- | --- | --- |
| 1 | Une connexion, une réponse vide, un bulletin blanc ou une délégation comptent-ils de la même manière dans chaque quorum ? | Le calcul du quorum de tous les profils | Association et relecture juridique | Règle écrite et exemples chiffrés |
| 2 | Comment appliquer une voix prépondérante identifiable dans un scrutin secret ? | AGO et Bureau | Relecture juridique | Décision motivée, ou renoncement explicite au départage |
| 3 | Comment un mandataire vote-t-il pour un mandant sans que leurs choix soient révélés ? | Le régime des procurations | Relecture juridique et cryptographique | Procédure de révocation et test de non-lien |
| 4 | Comment qualifier les membres « concernés ou impactés », et comment contester cette qualification ? | L’éligibilité par question | Association | Liste gelée, recours et date de gel |
| 5 | Comment articuler l’article 15 et les seuils de l’article 19 pour la dissolution ? | Le profil dissolution | Relecture juridique | Note d’interprétation datée |
| 6 | Le bulletin blanc est-il décompté dans tous les scrutins, ou seulement à la constitution territoriale ? | Le dépouillement de chaque profil | Association | Règle par profil |
| 7 | Le passage « tout moyen reconnu valable par l’ensemble des membres » vaut-il approbation d’un protocole précis ? | La base juridique d’un protocole | Relecture juridique | Avis écrit, ou nouvelle délibération explicite |
| 8 | La copie locale des statuts est-elle la version opposable, et existe-t-il un règlement intérieur ? | **Tout le reste** | Association | Version datée et règlement produit |

L’ambiguïté 8 commande les sept autres. Sans elle, une délibération sur un profil porterait sur un texte peut-être périmé.

## 6. La question de l’emplacement d’un éventuel système

Une idée a été proposée en séance : ouvrir un **nouveau dépôt privé** pour y mettre le système. Elle mérite une réponse précise, car elle mélange trois choses distinctes.

### 6.1 Un dépôt n’est pas un serveur

Un dépôt Git stocke du code et son historique. Il n’exécute pas d’urne, ne détient pas de clé de déchiffrement à seuil, ne tient pas de journal append-only opposable et ne fournit ni authentification des membres, ni supervision, ni reprise. Le site actuel est publié sur un hébergement statique : rien n’y peut recevoir un bulletin de façon confidentielle. Un dépôt privé ne change pas cette limite ; il faut un serveur, où qu’il soit.

### 6.2 Ce qu’un dépôt privé apporte réellement

- il sépare le prototype du site public et de sa porte de vérification ;
- il restreint l’accès aux personnes autorisées ;
- il permet d’épingler des versions et de conserver la trace des revues ;
- il évite qu’un fichier de vote soit publié par accident sur le site.

### 6.3 Ce qu’un dépôt privé ne change pas

- il ne tranche ni le profil statutaire, ni les ambiguïtés du §5 ;
- il ne remplace ni la cérémonie de clés, ni l’hébergement, ni le vérificateur indépendant ;
- il ne protège pas des erreurs de commit : un secret poussé reste dans l’historique ;
- il ne garantit pas le secret entre les personnes qui y ont accès ;
- il n’exonère d’aucune obligation de licence : un logiciel sous AGPL modifié et servi à distance peut devoir être publié ;
- il ne rend pas un logiciel « sûr » : une licence libre ne prouve aucun audit.

### 6.4 Conditions minimales avant le premier commit

Si l’association décide malgré tout d’ouvrir ce dépôt, ces règles devraient figurer dans son README avant tout code :

1. données strictement synthétiques, aucune identité réelle, aucun bulletin réel ;
2. aucune clé de production, aucun secret durable ;
3. plan de destruction des données d’essai, avec date ;
4. interdiction de toute promesse publique de sécurité ;
5. revue humaine avant tout déploiement, même interne ;
6. rattachement explicite à la trace de décision et à la version statutaire confirmée ;
7. sortie du dépôt documentée : export, licence, reprise ou abandon.

### 6.5 Recommandation de travail

Ne pas créer le dépôt avant la décision. Le choix du profil et de la voie détermine ce qu’on y mettrait : un dossier d’expertise pour la voie B, un environnement d’exploitation pour la voie C, des notes pour la voie A. Ouvrir un dépôt vide maintenant n’avancerait que sur un emplacement, pas sur une décision.

## 7. Les quinze conditions cumulatives

Elles sont énumérées intégralement au §3 de [`vote-distanciel-decision.md`](vote-distanciel-decision.md). Résumé opérationnel, dans l’ordre où elles se présentent :

| # | Condition | Où elle se prouve |
| --- | --- | --- |
| 1 | Version des statuts et règlement intérieur confirmés | Ambiguïté 8 |
| 2 | Profil et règles relus par une personne compétente et par l’association | §3 et trace |
| 3 | Ambiguïtés propres au profil levées | §5 |
| 4 | Une solution existante et une version désignée | Voie B ou C |
| 5 | Protocole du banc relu (cryptographie, droit, données, opérations, accessibilité) | Plan de revues |
| 6 | Environnement isolé, données synthétiques, plan de destruction | §6.4 |
| 7 | Métrique, référence et seuil d’arrêt de l’épreuve de corrélation fixés avant génération | Registre de corrélation |
| 8 | Une condition d’arrêt entraîne réellement l’arrêt | Protocole de banc |
| 9 | Sept incidents de continuité relus | Registre de continuité |
| 10 | Huit barrières d’accessibilité et risques des replis examinés | Registre d’accessibilité |
| 11 | Assistance, support, procuration et recours séparés | Registre d’assistance |
| 12 | Cycle des clés relu, aucune clé complète ni cryptographie maison | Registre des clés |
| 13 | Sept contrôles de chaîne logicielle documentés | Registre de chaîne logicielle |
| 14 | Gel, vérifications, incidents, contestations et décision clos avant proclamation | Registre des résultats |
| 15 | Six rôles ont examiné les artefacts relevant d’eux | Plan de revues |

Si une seule manque, la phase reste documentaire. Aucun total ne compense un manque.

## 8. Trace de décision à remplir

**Seul le tableau du §6 de [`vote-distanciel-decision.md`](vote-distanciel-decision.md) fait foi.** Il est reproduit ici pour la séance, avec les valeurs attendues.

| Champ | Valeur | Valeurs acceptées |
| --- | --- | --- |
| Version des statuts confirmée | | Référence datée du document confirmé |
| Règlement intérieur vérifié | | Existant, absent, ou référence |
| Profil retenu | | Un identifiant du §3, ou `aucun` |
| Option retenue | | `A`, `B` ou `C` — `D` refusée |
| Instance ou rôle décideur | | Instance réellement compétente |
| Date de décision | | `AAAA-MM-JJ` |
| Date de réexamen | | `AAAA-MM-JJ`, après la décision |
| Conditions ou objections | | Réserves, dissidences, suites |

Règles de contrôle déjà actives : une trace partielle est refusée ; `dissolution` est refusée ; `aucun` n’est compatible qu’avec `A` ; une date de réexamen antérieure ou égale à la décision est refusée. Une trace complète consigne une décision, elle ne la valide pas.

## 9. Déroulé proposé d’une séance

| Étape | Question posée | Sortie attendue |
| --- | --- | --- |
| 1 | La copie des statuts est-elle la version opposable ? | Référence datée, ou action de vérification |
| 2 | Un règlement intérieur existe-t-il ? | Référence, ou constat d’absence |
| 3 | Quelles ambiguïtés du §5 sont tranchées aujourd’hui ? | Décisions motivées et renvois |
| 4 | Quel profil, ou `aucun` ? | Identifiant retenu, sans classement préalable |
| 5 | Quelle voie, A, B ou C ? | Voie retenue et conditions |
| 6 | Qui tient les six rôles et les cinq revues ? | Noms ou fonctions, jamais supposés disponibles |
| 7 | Quelles dates de décision et de réexamen ? | Deux dates ISO cohérentes |

Deux règles de séance : aucune option n’est présélectionnée, et une objection non résolue est consignée au §10 plutôt que lissée dans un consensus apparent.

## 10. Registre des objections

À remplir pendant la séance. Une objection consignée n’est pas un échec ; une objection effacée en est un.

| Objection | Portée | Réponse ou suite | Date |
| --- | --- | --- | --- |
| | | | |

## 11. Ce que ce dossier ne fait pas

- Il n’interprète aucun article et ne remplace ni avis juridique, ni relecture compétente.
- Il ne sélectionne aucun logiciel, aucune version, aucun hébergeur.
- Il ne contient ni identité, ni bulletin, ni clé, ni donnée personnelle.
- Il ne crée aucun dépôt, aucun serveur et aucune promesse publique.
- Il ne classe pas les profils ni les voies : aucun score, aucun rang, aucune probabilité.
- Le vert de `outils/verifier-vote-distanciel.py` dit seulement que ce dossier reste cohérent avec les registres ; il ne valide aucune décision.

## 12. Sources internes

- [`vote-distanciel-decision.md`](vote-distanciel-decision.md) — brief et trace de décision.
- [`vote-distanciel-statuts.md`](vote-distanciel-statuts.md) — relevé des règles et ambiguïtés.
- [`vote-distanciel-regles.toml`](vote-distanciel-regles.toml) — 18 règles structurées.
- [`vote-distanciel-profils.toml`](vote-distanciel-profils.toml) — 8 profils non exécutables.
- [`vote-distanciel-comparaison.toml`](vote-distanciel-comparaison.toml) — options et critères bloquants.
- [`vote-distanciel-menaces.toml`](vote-distanciel-menaces.toml) — 10 menaces et conditions d’arrêt.
- [`vote-distanciel-revues.toml`](vote-distanciel-revues.toml) — rôles et revues à attribuer.
- [`vote-distanciel-protocole-banc.md`](vote-distanciel-protocole-banc.md) — protocole du banc synthétique.
- `assets/documents/statuts-2020.pdf` — copie de travail, non confirmée opposable.
