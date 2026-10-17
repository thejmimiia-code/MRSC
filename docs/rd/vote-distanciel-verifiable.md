# Vote distanciel vérifiable — cadrage de sécurité et conditions de non-déploiement

**Date : 17 octobre 2026. Statut : recherche à cadrer, aucun système de vote n’est disponible.** Ce document décrit une architecture candidate et ses conditions d’arrêt. Il ne constitue ni une certification, ni un audit cryptographique, ni un avis juridique, ni une autorisation d’organiser un scrutin.

## 1. Reformulation de l’objectif

L’objectif raisonnable n’est pas un système « infalsifiable en toutes circonstances » : aucun logiciel, terminal, réseau, administrateur ou procédé humain ne peut recevoir cette garantie absolue. La cible de recherche est un vote **vérifiable de bout en bout**, où :

- une personne autorisée peut voter au plus une fois selon les règles du scrutin ;
- le contenu du bulletin reste secret et n’est pas relié publiquement à l’identité ;
- chaque personne peut vérifier que son bulletin chiffré est inclus sans pouvoir prouver son choix à un tiers ;
- tout observateur peut vérifier les preuves du dépouillement sans accéder aux bulletins en clair ;
- aucune autorité seule ne peut déchiffrer ou modifier le résultat ;
- les erreurs, indisponibilités et contestations ont une procédure hors ligne documentée.

« Vérifiable comme Bitcoin » ne signifie pas mettre les votes sur une blockchain publique. Un registre append-only et répliqué peut aider à détecter une modification, mais il ne résout ni le secret du vote, ni l’authentification, ni l’achat de voix, ni la coercition, ni un terminal compromis. Une chaîne publique permanente peut au contraire aggraver les risques de corrélation et de réidentification.

## 2. Questions bloquantes avant toute conception détaillée

L’association doit préciser, avec une relecture juridique compétente :

1. **Type de scrutin :** décision interne associative, consultation non contraignante, assemblée générale, élection statutaire ou scrutin public. Les exigences et le droit applicable diffèrent.
2. **Corps électoral :** qui établit l’éligibilité, comment corriger une omission et comment séparer cette liste des bulletins ?
3. **Règle de vote :** un choix, plusieurs choix, jugement majoritaire, quorum, procuration, vote modifiable ou non.
4. **Canaux de secours :** papier, téléphone accompagné, lieu physique, assistance accessible ; aucun vote distant ne doit être l’unique recours avant validation.
5. **Menaces prioritaires :** fraude interne, serveur compromis, terminal infecté, déni de service, coercition au domicile, perte de clé, collusion des autorités, métadonnées réseau.
6. **Autorité de décision et contestation :** qui ouvre, clôt, dépouille, publie, annule ou recommence le scrutin ?

Tant que ces réponses et la base juridique ne sont pas consignées, le travail reste documentaire et aucun bulletin réel ne doit être recueilli.

## 3. Propriétés à ne pas confondre

| Propriété | Preuve attendue | Ce qu’elle ne garantit pas |
| --- | --- | --- |
| Intégrité du registre | Empreintes chaînées, signatures, copies indépendantes et journal public | Exactitude d’un bulletin saisi sur un appareil compromis |
| Secret du bulletin | Chiffrement à clé publique, séparation identité/bulletin, dépouillement à seuil | Absence de coercition ou de capture d’écran au domicile |
| Éligibilité et unicité | Jeton anonyme à usage unique émis après contrôle séparé | Anonymat si l’émission et le dépôt sont corrélés par horaires ou réseau |
| Vérifiabilité individuelle | Reçu ne révélant pas le choix et preuve d’inclusion | Possibilité de démontrer son choix à un acheteur — qui doit justement être empêchée |
| Vérifiabilité universelle | Preuves à divulgation nulle de connaissance et artefacts publics vérifiables | Disponibilité du service ou honnêteté du terminal de vote |
| Disponibilité | Réplication, files d’attente, fenêtre suffisante et procédure de reprise | Intégrité cryptographique ni accessibilité réelle |
| Transparence | Code, protocole, paramètres, cérémonies et résultats d’audit publiés | Sécurité par le seul fait que le code est ouvert |

## 4. Architecture candidate — à expertiser, pas à développer directement

### Séparation des rôles

1. **Registre des personnes habilitées** — connaît l’identité et l’éligibilité, jamais le choix.
2. **Émetteur de justificatifs anonymes** — transforme l’éligibilité en droit de vote non traçable, idéalement avec signatures aveugles ou mécanisme équivalent expertisé.
3. **Urne chiffrée** — accepte un justificatif valide une seule fois, publie le bulletin chiffré et sa preuve de validité.
4. **Tableau public append-only** — permet de vérifier inclusion, ordre et absence de retrait ; plusieurs miroirs indépendants comparent leurs empreintes.
5. **Autorités de dépouillement à seuil** — par exemple 3 parts sur 5 ; aucune clé complète n’existe sur une seule machine.
6. **Vérificateur indépendant** — logiciel distinct, reproductible et utilisable hors ligne à partir des artefacts publiés.
7. **Procédure de contestation et procédure d’annulation** — délais, preuves recevables, autorité humaine, annulation et nouveau scrutin.

### Parcours minimal

`contrôle d’éligibilité → justificatif anonyme → chiffrement local → preuve de bulletin valide → dépôt → reçu d’inclusion non révélateur → clôture signée → dépouillement à seuil → preuves publiques → vérification indépendante`

Les journaux techniques ne doivent contenir ni choix, ni justificatif brut, ni association identité–horaire–adresse réseau exploitable. La minimisation des métadonnées doit être vérifiée expérimentalement ; elle ne peut pas être déduite du seul chiffrement du bulletin.

## 5. Menaces et réponses minimales

| Menace | Réponse de conception | Risque résiduel / arrêt |
| --- | --- | --- |
| Serveur d’urne compromis | Bulletins chiffrés côté client, preuves publiques, miroirs et vérificateur indépendant | Arrêt si le serveur peut substituer un bulletin sans alerte vérifiable |
| Administrateur malveillant | Séparation des rôles, signatures multiples, clé à seuil, cérémonies observables | Arrêt si une seule personne peut ouvrir, clore et déchiffrer |
| Terminal de vote compromis | Vérification sur second appareil, bulletin papier ou canal physique de secours | Aucun mécanisme général ne garantit un terminal personnel infecté |
| Coercition ou achat de voix | Reçu non transférable, possibilité encadrée de revoter où seul le dernier vote compte, canal physique | Le vote au domicile reste exposé ; avis juridique et étude d’usage obligatoires |
| Corrélation identité/bulletin | Services séparés, délais/mélange, minimisation des logs, réseaux et horloges étudiés | Arrêt si les métadonnées permettent une corrélation réaliste |
| Déni de service | Fenêtre longue, réplication, reprise et prolongation décidée humainement | Aucun système connecté n’est disponible « en toutes circonstances » |
| Perte ou collusion des clés | Sauvegardes scellées, seuil multi-organisations, rotation et exercice de récupération | Arrêt si la cérémonie de clé n’est pas répétable et observée |
| Faiblesse cryptographique | Bibliothèques éprouvées, paramètres versionnés, audit externe, migration prévue | Ne jamais inventer de primitive cryptographique dans le dépôt |
| Réidentification future | Pas de bulletin en clair, rétention minimale, pas de chaîne publique contenant des identifiants | Le chiffrement permanent n’est pas une promesse de secret permanent |

## 6. Choix technologique proposé

Ne pas construire une cryptographie maison ni choisir une blockchain par analogie. Comparer d’abord des systèmes de vote vérifiable existants et maintenus :

- **Belenios** — système de vote en ligne vérifiable ; miroir GitHub consulté le 17 octobre 2026, licence AGPL-3.0, dépôt source annoncé sur GitLab : <https://github.com/glondu/belenios>.
- **Helios** — serveur de vote vérifiable de bout en bout ; dépôt GitHub consulté le 17 octobre 2026, licence Apache-2.0 : <https://github.com/benadida/helios-server>.
- **ElectionGuard** — composants pour élections vérifiables de bout en bout et artefacts d’audit ; dépôt désormais porté par Election Technology Initiative, consulté le 17 octobre 2026, licence MIT : <https://github.com/Election-Tech-Initiative/electionguard>.

Ces références prouvent seulement l’existence de projets et leurs métadonnées publiques observées. Elles ne prouvent pas qu’ils conviennent au droit, au type de scrutin, aux menaces ou aux moyens du M.R.S.C. Une comparaison doit examiner protocole, version, audits indépendants, modèle de menace, accessibilité, coercition, opérations de clés, maintenance et licence.

## 7. Phases et portes de décision

### Phase 0 — cadrage, aucune donnée réelle

- répondre aux six questions bloquantes ;
- produire une analyse juridique et statutaire ;
- définir le modèle de menace et les critères d’annulation ;
- comparer « ne pas numériser », système existant hébergé et intégration maîtrisée.

**Sortie :** décision humaine de poursuivre ou d’arrêter. Par défaut : arrêt.

### Phase 1 — banc d’essai fictif

- scrutin entièrement fictif, électeurs synthétiques, aucune identité réelle ;
- deux implémentations indépendantes du vérificateur ;
- tests de falsification, suppression, duplication, ordre, clôture, perte de clé et panne réseau ;
- revue d’accessibilité et parcours papier équivalent.

**Sortie :** défauts publiés, aucun usage décisionnel.

### Phase 2 — audit et exercice contradictoire

- audit cryptographique et applicatif externe ;
- exercice opérationnel avec autorités distinctes ;
- test de récupération, contestation et destruction des données ;
- revue juridique, protection des données et accessibilité.

**Sortie :** même avec des résultats favorables, une autorisation humaine séparée reste nécessaire.

### Phase 3 — pilote non contraignant

Uniquement si toutes les portes précédentes ont une preuve. Consultation réversible, canal alternatif, incidents visibles et aucune conséquence statutaire automatique.

## 8. Critères d’arrêt immédiat

- promesse publique « infalsifiable », « totalement sécurisé » ou « anonyme garanti » ;
- cryptographie conçue localement sans revue spécialisée ;
- identité et bulletin accessibles au même service ou dans les mêmes journaux ;
- une personne ou machine détient seule la clé de dépouillement ;
- absence de canal de secours, de contestation ou d’annulation ;
- impossibilité de vérifier sans faire confiance au serveur principal ;
- audit, droit applicable, accessibilité ou procédure de clés non établis ;
- utilisation pour une élection publique ou statutaire sans autorisation compétente.

## 9. Décision de cette passe

**Ne pas développer de système de vote réel.** Ouvrir une initiative de recherche prioritaire, préparer le modèle de menace et comparer des solutions existantes. Le premier prototype éventuel doit rester un banc d’essai fictif, hors navigation publique, sans identité ni bulletin réel.
