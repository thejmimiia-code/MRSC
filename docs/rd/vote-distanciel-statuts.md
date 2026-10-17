# Vote distanciel — exigences relevées dans les statuts du M.R.S.C.

**Relevé du 17 octobre 2026. Statut : extraction interne à faire relire juridiquement et par l’association.** Cette note applique la demande « suivre les directives des statuts » au cadrage du vote distanciel. Elle ne reformule pas les statuts officiels, ne tranche pas leurs ambiguïtés et ne vaut ni interprétation juridique ni décision associative.

## Source et méthode

- **Source :** copie locale [`assets/documents/statuts-2020.pdf`](../../assets/documents/statuts-2020.pdf), 25 pages, version indiquée « modification du 30 septembre 2020 », validée en AGE le 2 octobre 2020.
- **Empreinte SHA-256 de la copie consultée :** `938bd5b72d70ab4e3737f61b91818a6813b29cc5453da44c81d5b7f33ca143c3`.
- **Méthode :** extraction locale du texte avec pypdf 6.1.1 ; lecture ciblée des pages 7 à 24. Le PDF est chiffré et son encodage a produit des avertissements d’objets ; toute citation ou règle doit être confrontée visuellement au PDF avant usage réel.
- **Périmètre :** exigences susceptibles d’influencer un vote numérique interne. Les autres dispositions restent applicables même si elles ne sont pas reproduites ici.

Le registre structuré [`vote-distanciel-regles.toml`](vote-distanciel-regles.toml) conserve chaque règle avec son article, sa page, sa portée et son statut de relecture.

## Règles relevées

### Principes communs

| Repère | Relevé du document | Conséquence de conception candidate |
| --- | --- | --- |
| Articles 3 et 5, pages 7 et 9 | Seuls les membres concernés ou impactés votent ; un conflit d’intérêt personnel retire la participation au vote. | L’éligibilité dépend de la question, pas seulement d’une liste générale. Sa détermination et son recours doivent être arrêtés avant l’émission des droits anonymes. |
| Article 4, page 8 | « 1 personne physique = 1 cotisation = 1 voix » pour l’adhésion d’une personne morale. | Le registre d’éligibilité doit empêcher plusieurs droits issus d’une même cotisation, sans inscrire l’identité dans l’urne. |
| Article 11.9, page 20 | Le vote arrive après information, compréhension, débat, analyse, proposition, contrôle d’éthique et synthèse. | Une urne ne doit pas court-circuiter les phases préparatoires ni ouvrir avant publication de l’ordre du jour et des éléments compréhensibles. |

### Bureau exécutif et conseil d’éthique

| Repère | Relevé du document | Conséquence candidate |
| --- | --- | --- |
| Article 10.1, page 11 | Réunions et consultations électroniques admises ; une procuration au maximum par membre ; pouvoirs en blanc non pris en compte ; majorité absolue des présents et représentés ; voix du président prépondérante en cas d’égalité ; procès-verbal signé. | Le type d’organe doit paramétrer plafond des procurations, majorité, départage et production du procès-verbal. Ces paramètres ne peuvent pas être un réglage libre après ouverture. |
| Article 10.2.1, page 13 | Le conseil d’éthique peut délibérer à distance ; une procuration par membre ; majorité absolue ; règle de départage particulière. | Ne pas réutiliser automatiquement la règle de départage du Bureau exécutif pour le conseil d’éthique. |

### Assemblée territoriale

| Repère | Relevé du document | Conséquence candidate |
| --- | --- | --- |
| Article 11.6, page 18 | Lors de la constitution, les membres présents votent à bulletin secret pour les postes territoriaux. | Le secret est une exigence statutaire pour ce cas ; l’éligibilité paraît limitée aux présents, ce qui doit être confirmé avant d’assimiler présence et connexion distante. |
| Article 11.6, page 18 | Les votes blancs sont comptés ; s’ils sont majoritaires, candidature irrecevable et procédure reprise avec de nouveaux candidats. | Le bulletin blanc doit être une option distincte, décomptée et reliée à une règle d’annulation/reprise vérifiable. |

### Assemblée générale ordinaire

| Repère | Relevé du document | Conséquence candidate |
| --- | --- | --- |
| Article 14, pages 22–23 | Tous les membres à jour de cotisation composent l’AGO ; convocation et ordre du jour ; seules les questions à l’ordre du jour sont traitées. | Le corps électoral et le bulletin doivent être figés et engagés cryptographiquement avant ouverture ; une question ne peut pas être ajoutée silencieusement. |
| Article 14, page 22 | Première assemblée : présence de 25 % nécessaire ; seconde avec même ordre du jour sept jours plus tard, sans minimum de présents. | Le système doit distinguer première et seconde convocation, calculer le quorum selon la règle applicable et empêcher la clôture sous le seuil. |
| Article 14, pages 22–23 | Majorité absolue des présents et représentés ; voix du président prépondérante en cas d’égalité. | Le décompte doit séparer les catégories nécessaires et publier la règle de départage avant le vote. L’effet d’un scrutin secret sur la voix prépondérante doit être expertisé. |
| Article 14, page 23 | Procuration admise, au plus deux pouvoirs par membre ; pouvoirs en blanc non pris en compte. | La procuration exige un registre séparé, révocable et auditable, sans révéler le bulletin ; le cumul doit être plafonné avant émission des droits. |
| Article 14, page 23 | Scrutin secret sur demande du président ou de la majorité des présents ou représentés. | Le mode secret ne doit pas être décidé après réception de bulletins. La procédure de demande et le moment de bascule doivent être définis avant le scrutin. |
| Article 14, page 23 | Session numérique ouverte au moins sept jours ; consultations écrites admises ; réponses transmises prises en compte dans le quorum. | La fenêtre d’ouverture minimale et la définition d’une « réponse transmise » doivent être fixées. Il faut éviter de publier qui a répondu avec quoi. |
| Article 14, page 23 | Procès-verbal signé par le président ou le vice-président. | Les preuves cryptographiques complètent le procès-verbal mais ne le remplacent pas ; l’autorité et la signature du PV restent humaines. |

### Assemblée générale extraordinaire et dissolution

| Repère | Relevé du document | Conséquence candidate |
| --- | --- | --- |
| Article 15, pages 23–24 | AGE demandée par le fondateur ou 51 % des membres ; quorum de 51 % ; une procuration par membre ; majorité absolue des présents et représentés. | Un profil AGE distinct est requis, avec preuve de convocation, plafond de procuration et quorum propres. |
| Article 15, page 24 | Seconde AGE avec même ordre du jour quinze jours plus tard ; sans minimum de présents ; décision à l’unanimité. | La seconde convocation ne peut pas réutiliser le profil AGO ; l’unanimité et le délai doivent être contrôlés séparément. |
| Article 19, page 25 | La dissolution mentionne une majorité des deux tiers et des quorums de 60 % en première instance et 30 % en seconde. | La dissolution exige un profil séparé. Son articulation avec l’article 15 doit être interprétée par une personne compétente avant tout vote. |

## Ambiguïtés et conflits à faire trancher

1. **Présence, représentation et réponse numérique :** les statuts emploient plusieurs notions sans définir si une connexion, une réponse vide, un bulletin blanc ou une délégation comptent de la même manière pour chaque quorum.
2. **Secret et voix prépondérante :** appliquer une voix de départage identifiable dans un scrutin secret peut créer une tension entre secret et règle de décision.
3. **Procuration et secret :** le mandataire doit disposer d’un droit supplémentaire sans que le système révèle les choix du mandant ou du mandataire ; la révocation et un éventuel vote direct ultérieur ne sont pas détaillés.
4. **Membres « concernés ou impactés » :** aucun mécanisme de qualification, contestation ou date de gel n’est décrit dans les pages relevées.
5. **AGE et dissolution :** les règles de l’article 15 et les seuils spécifiques de l’article 19 doivent être articulés ; l’outil ne doit pas choisir une interprétation.
6. **Bulletins blancs :** une règle explicite existe pour la constitution d’une assemblée territoriale, pas nécessairement pour tous les autres scrutins.
7. **« Tout moyen reconnu valable par l’ensemble des membres » :** ce passage de l’article 14 ne suffit pas, à lui seul, à établir qu’un protocole précis a été approuvé ou qu’il respecte toutes les autres règles.
8. **Version et règlement intérieur :** il faut confirmer que la copie locale est la version opposable actuelle et vérifier l’existence d’un règlement intérieur ou de décisions ultérieures.

## Profils candidats — pas encore des règles exécutables

| Profil | Corps électoral | Quorum / majorité | Procuration | Secret | Statut |
| --- | --- | --- | --- | --- | --- |
| Bureau exécutif | Membres du Bureau présents ou représentés | Majorité absolue ; départage président | 1 maximum | Non imposé dans le relevé | À relire |
| Conseil d’éthique | Membres constitués présents ou représentés | Majorité absolue ; départage propre | 1 maximum | Non imposé dans le relevé | À relire |
| Territoriale constitutive | Membres présents de l’assemblée | Blanc majoritaire → reprise | Non établie ici | Imposé | À relire |
| AGO, première convocation | Membres à jour ; présents et représentés | Quorum 25 %, majorité absolue | 2 maximum | Sur demande prévue | À relire |
| AGO, seconde convocation | Même ordre du jour | Pas de minimum relevé, majorité absolue | 2 maximum | Sur demande prévue | À relire |
| AGE, première convocation | Membres ; présents et représentés | Quorum 51 %, majorité absolue | 1 maximum | Non précisé ici | À relire |
| AGE, seconde convocation | Même ordre du jour | Pas de minimum relevé, unanimité | 1 maximum | Non précisé ici | À relire |
| Dissolution | À confirmer avec articles 15 et 19 | 2/3 ; quorums 60 % puis 30 % | À confirmer | À confirmer | Bloqué par interprétation |

## Décision de cette passe

Les statuts permettent des consultations électroniques dans plusieurs organes et une session numérique d’AGO d’au moins sept jours, mais ils n’autorisent pas à traiter tous les votes avec une règle unique. **Aucun moteur de scrutin ne doit être développé avant validation de ces profils, des ambiguïtés et de la version statutaire applicable.**
