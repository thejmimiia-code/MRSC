# Brief de décision — prochaine étape du vote distanciel

**Date : 17 octobre 2026. Statut : à décider par l’association. Aucun système de vote n’est disponible.** Ce brief ne demande pas d’autoriser un scrutin réel. Il demande seulement de décider si la recherche peut passer du cadrage documentaire à l’expertise d’un profil et d’un banc synthétique.

## 1. Ce qui est établi dans le dépôt

- La copie locale des statuts comporte plusieurs profils de scrutin et non une règle unique.
- Dix-huit relevés statutaires sont structurés, tous `a-faire-relire`.
- Dix menaces et sept invariants sont documentés, tous `a-expertiser`.
- Douze cas de banc synthétique sont décrits, tous `a-concevoir` et jamais exécutés.
- Aucun bulletin réel, aucune identité réelle, aucune clé de production et aucun service de vote ne sont présents.
- Les métadonnées publiques de Belenios, Helios et ElectionGuard ont été consultées ; aucun projet n’est sélectionné ni audité par le M.R.S.C.

Ces constats sont techniques et documentaires. Ils ne prouvent ni conformité juridique, ni sécurité, ni accessibilité, ni aptitude à un scrutin statutaire.

## 2. Décision bornée à prendre

L’association doit choisir **un seul profil** pour la prochaine étude, ou arrêter la piste :

- `bureau-executif` ;
- `conseil-ethique` ;
- `territoriale-constitutive` ;
- `ago-premiere` ;
- `ago-seconde` ;
- `age-premiere` ;
- `age-seconde` ;
- `dissolution` — bloqué tant que l’articulation des articles 15 et 19 n’est pas relue ;
- `aucun` — arrêt ou report de la recherche.

Les huit profils sont reliés à leurs règles et questions bloquantes dans [`vote-distanciel-profils.toml`](vote-distanciel-profils.toml). Ils sont volontairement non exécutables : aucun quorum, seuil, délai ou plafond ne peut être injecté automatiquement avant relecture.

Puis choisir une voie :

- **A — Ne pas voter à distance.** Étudier seulement les alternatives accessibles et la participation à distance sans vote électronique.
- **B — Expertiser un service existant.** Examiner droit, contrat, métadonnées, preuves exportables, audits et réversibilité.
- **C — Expertiser l’auto-hébergement d’un logiciel existant.** Examiner compétences, clés, builds, mises à jour, reprise et exploitation.
- **D — Construire un système.** Option bloquée à ce stade ; elle ne peut pas être choisie dans la trace.

A ou `aucun` sont des décisions valides. La recherche n’a pas à aboutir à un outil. La grille [`vote-distanciel-comparaison.toml`](vote-distanciel-comparaison.toml) prépare quinze critères bloquants sans score, rang ni probabilité ; toutes les options restent `a-evaluer`. Le relevé [`vote-distanciel-sources.toml`](vote-distanciel-sources.toml) épingle les trois dépôts à des commits observés le 17 octobre 2026 ; les [`premiers écarts et inconnues`](vote-distanciel-premiers-ecarts.md) orientent les preuves à chercher sans constituer une évaluation.

## 3. Conditions cumulatives avant un banc synthétique

1. La version applicable des statuts et l’existence d’un règlement intérieur sont confirmées.
2. Le profil choisi et ses règles sont relus par une personne compétente et par l’association.
3. Les ambiguïtés de quorum, procuration, secret, blanc et départage propres au profil sont levées.
4. Une solution existante et une version précise sont désignées pour expertise ; aucune cryptographie locale n’est ajoutée.
5. Le protocole du banc est relu en cryptographie, droit, protection des données, opérations et accessibilité.
6. L’environnement est isolé, les données sont synthétiques et le plan de destruction est fixé avant l’exercice.
7. Pour l’épreuve de corrélation, métrique, référence et seuil d’arrêt sont définis et datés par la revue humaine avant génération des données ; aucun seuil du dépôt ne vaut décision.
8. Une condition d’arrêt entraîne réellement l’arrêt, sans compensation par un score global.
9. Les six rôles du [`plan de revues`](vote-distanciel-revues.toml) ont examiné les artefacts relevant de leur responsabilité ; aucune disponibilité n’est supposée.

Si une condition manque, la phase reste documentaire.

## 4. Ce qui ferait arrêter ou revenir en arrière

- version statutaire incertaine ou règle contradictoire non tranchée ;
- profil nécessitant une présence ou un secret que le dispositif ne peut établir ;
- impossibilité de séparer identité, droit de vote et bulletin ;
- absence de vérificateur indépendant ou d’export complet des preuves ;
- dépendance à une personne, une clé, un fournisseur ou un serveur unique ;
- canal alternatif inaccessible ou procédure d’annulation absente ;
- métadonnées permettant une corrélation réaliste ;
- impossibilité de détruire les secrets et journaux transitoires ;
- avis juridique, cryptographique ou protection des données défavorable.

## 5. Recommandation de travail

**Ne pas autoriser de scrutin ni construire de système.** Faire d’abord relire la source statutaire et choisir, si l’association souhaite continuer, un seul profil simple pour comparer A, B et C. L’AGO numérique est explicitement mentionnée dans la copie locale, mais cela ne suffit pas à la choisir : quorum, procuration, secret éventuel et définition d’une réponse doivent encore être interprétés.

## 6. Trace de décision associative

Remplir les huit champs ensemble après délibération. Laisser tout vide signifie « décision en attente ». Une trace partielle est volontairement refusée par le contrôle automatique.

| Champ | Valeur |
| --- | --- |
| Version des statuts confirmée | |
| Règlement intérieur vérifié | |
| Profil retenu | |
| Option retenue | |
| Instance ou rôle décideur | |
| Date de décision | |
| Date de réexamen | |
| Conditions ou objections | |

**Valeurs attendues :** profil parmi la liste du §2 ; option A, B ou C ; dates au format `AAAA-MM-JJ`. L’option D est bloquée. Une trace complète consigne une décision, elle ne la valide pas.
