# R&D — usages de l’IA, fraudes et réflexes durables

**État de la revue : 7 octobre 2026.** Cette recherche étend la page publique [`ia-societe.html`](../ia-societe.html) et les fiches du domaine Numérique/IA. Elle s’appuie en priorité sur les ressources de Cybermalveillance.gouv.fr et les services publics français. C’est une première carte de travail, non une liste exhaustive des menaces, une certification de sécurité ou un conseil juridique, bancaire ou judiciaire.

## 1. Ligne éditoriale

- Partir d’un usage ou d’une demande précise, et non de l’idée qu’un outil ou une image « ressemble à de l’IA ».
- Décrire les usages, les personnes qui en tirent parti, les données, les conséquences possibles, la vérification humaine et les recours.
- Expliquer les fraudes par leurs mécanismes réutilisables : **qui est imité, quel contexte est invoqué, quelle action est demandée, par quel canal, avec quelle pression, et quelles données ou quels moyens sont visés**.
- Éviter les listes d’indices visuels comme méthode de détection. Les défauts de visage, de voix, de texte ou de logo ne sont pas des preuves fiables ; les détecteurs automatiques peuvent se tromper. La méthode centrale est de vérifier l’identité, le contexte et la demande par une voie indépendante.
- Ne pas attribuer à l’IA un incident qui n’a pas été documenté comme tel. De nombreuses escroqueries précèdent les modèles génératifs et se réalisent sans eux.
- Ne jamais promettre de répertorier toutes les fraudes présentes ou futures. Les catalogues illustrent des familles et doivent être complétés par des conduites à tenir qui restent utiles lorsque les prétextes changent.
- Parler de progrès rapides et observés, mais ne pas qualifier une évolution d’« exponentielle » comme fait mathématique sans indicateur défini, période, méthode et source. Capacité des modèles, coût d’accès et volume de fraudes sont des mesures distinctes.

## 2. Carte évolutive des usages de l’IA

Les familles se combinent et ne sont ni une définition juridique ni un inventaire exhaustif.

| Famille d’usage | Exemples de vie courante | Questions de contrôle |
| --- | --- | --- |
| Générer ou transformer | Brouillon, résumé, traduction, code, image, musique, voix ou vidéo | Quelles parties sont vérifiées ? Le résultat est-il marqué ou présenté comme authentique ? Quelles données ont été fournies ? |
| Percevoir ou extraire | Reconnaître une image, transcrire une voix, extraire des éléments d’un document | L’entrée est-elle exacte et complète ? Qui peut vérifier une erreur ou demander une correction ? |
| Recommander ou classer | Fil d’actualité, musique, recherche, offres, candidatures, courriers indésirables | Selon quels critères les éléments sont-ils mis en avant, cachés ou classés ? Peut-on contester le classement ? |
| Prédire ou aider à décider | Prévoir une demande, estimer un risque, attribuer un score, signaler une anomalie | Quelle population et quelles données ? À quel taux d’erreur ? Une personne reste-t-elle responsable ? |
| Automatiser ou agir | Réponse automatique, agent qui enchaîne des tâches, robot ou équipement connecté | Quelles permissions et limites ? Peut-on interrompre ou revenir en arrière ? Qui répond d’un dommage ? |
| Usages hybrides | Assistant de santé, outil éducatif, support client, traduction d’un appel, agent de vente | Quelles fonctions et quels tiers interviennent ? Quels sont les effets d’une erreur ou d’une fuite ? |

Les fiches publiques de première version couvrent : [usages et vérification des résultats](../apprendre/fiches/numerique-ia-usages.html), [voix, image et vidéo](../apprendre/fiches/numerique-verifier-media.html), [demande urgente ou inhabituelle](../apprendre/fiches/numerique-verifier-demande.html), [réaction après un incident](../apprendre/fiches/numerique-reagir-fraude.html), ainsi que le [hameçonnage](../apprendre/fiches/numerique-hameconnage.html) et la [protection des données](../apprendre/fiches/numerique-proteger-donnees.html). Elles constituent un début de couverture ; la carte source de vérité est `docs/apprentissage/referentiel.toml`.

## 3. Familles de scénarios de fraude à surveiller

| Canal / combinaison | Prétexte ou identité imitée | Action recherchée | Vérification robuste à enseigner |
| --- | --- | --- | --- |
| Courriel, SMS, messagerie instantanée ou message privé | Banque, administration, livraison, opérateur, réseau social, service de santé | Ouvrir un lien, scanner un QR code, saisir un identifiant, un mot de passe, un code ou des données bancaires | Ouvrir séparément l’application ou le site habituel ; saisir soi-même l’adresse ; utiliser un contact officiel déjà connu. |
| Appel, numéro usurpé, message vocal ou visioconférence | Faux conseiller, faux support, proche, collègue, dirigeant, fournisseur | Donner un code, installer un outil, partager un écran, payer ou transférer | Raccrocher ; rappeler un numéro enregistré auparavant ; confirmer auprès d’un autre responsable par une procédure connue. Un numéro affiché et une voix ne prouvent pas l’identité. |
| Texte, image, voix ou vidéo synthétiques ou montés | Proche, personnalité, service public, marque ou responsable | Croire une annonce, une urgence, une autorisation ou une demande de fonds | Vérifier la source d’origine, le contexte et la date ; confirmer par un autre canal ; ne pas s’appuyer sur un détecteur ou un défaut visuel isolé. |
| Faux support technique | Alerte de sécurité, virus, renouvellement de licence, remboursement | Accès à distance, contrôle de l’écran, installation ou paiement | Fermer l’échange ; contacter le support depuis le site ou le contrat déjà connu ; aucune prise de contrôle sous pression. |
| Urgence familiale ou professionnelle | « Nouveau téléphone », accident, paie, facture, changement de RIB, secret imposé | Virement, achat de cartes ou de crypto-actifs, divulgation d’informations ou contournement d’une procédure | Rappeler la personne sur son ancien numéro ; vérifier à deux personnes et via les coordonnées déjà enregistrées ; différer tout paiement inhabituel. |
| Fausse offre d’emploi ou arnaque à la tâche | Recruteur, entreprise connue, plateforme, mission rémunérée | Frais d’inscription, achat de matériel, dépôt, RIB, pièce d’identité, numéro de sécurité sociale ou encaissement d’un chèque | Vérifier l’entreprise et le poste via un canal professionnel indépendant ; ne pas payer un employeur potentiel ni acheter du matériel pour lui. |
| Faux placement, prêt ou investissement | Banque, conseiller, groupe d’investisseurs, célébrité, plateforme professionnelle | Dépôt initial, frais pour débloquer des gains, accès à un portefeuille ou recrutement d’autres personnes | Ne pas se fier à une vidéo, un témoignage ou une interface soignée ; vérifier séparément l’organisme et demander un avis indépendant ; ne pas investir sous pression. |
| Faux achat, location ou vente entre particuliers | Boutique, livreur, acheteur, vendeur, service de paiement | Paiement hors plateforme, acompte, faux remboursement ou réutilisation d’identifiants | Revenir à la plateforme par son application/site habituel ; examiner le paiement reçu dans son compte réel ; ne pas ouvrir de lien d’un prétendu acheteur ou livreur. |
| Fuite de données et usurpation | Organisme, assurance, école, employeur, association, membre de la famille | Exploiter des détails exacts pour gagner confiance, récupérer un compte, ouvrir un contrat ou détourner un paiement | Un détail vrai n’authentifie pas l’appel. Confirmer auprès de l’organisme, limiter les données transmises, protéger les comptes et prévenir l’entité concernée. |
| Images intimes fabriquées, chantage ou manipulation publique | Personne connue ou compte usurpé | Menace de diffusion, paiement, silence ou relais d’un contenu | Ne pas payer ni relayer le contenu ; conserver les preuves ; demander un accompagnement officiel et à une personne de confiance. Évaluer séparément les risques pour les mineurs ou la sécurité immédiate. |

Ce tableau sert à organiser l’apprentissage, pas à classifier une situation avec certitude. Une tentative peut combiner plusieurs canaux ou changer en cours d’échange ; un fraudeur peut utiliser un texte humain, un script, un service d’IA ou une équipe de faux opérateurs. Une même mesure n’est pas adaptée à tous les préjudices : banque, compte, identité, appareil compromis ou menace physique appellent des interlocuteurs différents.

## 4. Conduite à tenir transposable

1. **Faire une pause.** L’urgence, la peur, l’autorité affichée et le secret imposé sont des raisons de ralentir. Ne pas cliquer, scanner, transférer ou installer pendant l’échange.
2. **Vérifier l’identité, le contexte et la demande séparément.** Utiliser un numéro connu avant l’incident, l’application habituelle ou un site ouvert soi-même ; ne pas reprendre le lien, le QR code, le numéro ou le compte fournis par la sollicitation.
3. **Ne jamais communiquer sous pression** un mot de passe, un code à usage unique, des informations de carte, un accès à distance ou le contrôle d’un compte. Une banque ne demande pas de déplacer l’argent vers un « compte sécurisé ».
4. **Si quelque chose a déjà été transmis, agir selon le cas.** Pour un moyen de paiement ou un virement, contacter immédiatement la banque par une voie officielle ; pour un mot de passe, le changer depuis le service officiel et révoquer les sessions ; pour un appareil contrôlé à distance, cesser d’y saisir des identifiants et demander conseil.
5. **Garder les preuves** : messages, adresses, captures, reçus, dates, comptes et numéros. Ne pas détruire les éléments utiles et éviter de redistribuer un média douteux.
6. **Prévenir le service ou la personne dont l’identité a été utilisée et se faire orienter.** `17Cyber` fournit un diagnostic et des conseils ; les signalements à Signal Spam ou au 33700 ont des usages propres ; un signalement n’est pas automatiquement une plainte. Selon la situation, contacter la banque, le service concerné, la police ou la gendarmerie.
7. **Déclarer selon le canal adapté, sans confondre les quatre démarches.** Signalement à une plateforme, déclaration à la banque, information de l’organisme imité et plainte sont distincts et ne se remplacent pas (voir § 4 bis).
8. **Éviter les frais de récupération.** Des personnes peuvent recontacter une victime en prétendant récupérer son argent ; vérifier séparément toute nouvelle demande et ne pas verser de frais à un prétendu intermédiaire.

Ces actions doivent rester empathiques et non culpabilisantes. Les fraudeurs construisent des situations plausibles, souvent personnalisées ; une erreur de vigilance ne justifie ni honte ni retard à demander de l’aide.

## 4 bis. Déclarer : quatre démarches, quatre interlocuteurs

Vérifié le 12 novembre 2026 sur les pages officielles listées au § 5. Cette section est la raison d’être du lot : un catalogue de réflexes qui s’arrête au signalement manque la partie que la personne doit accomplir elle-même, souvent pendant que l’argent circule encore.

| Démarche | À quoi elle sert | Où elle se fait | Ce qu’elle ne fait pas |
| --- | --- | --- | --- |
| **Signalement** | Faire constater un fait par une plateforme ou un opérateur : courriel indésirable, SMS, site d’hameçonnage, contenu illégal | Signal Spam (courriels), 33700 (SMS et appels), Phishing Initiative (sites), Pharos (contenus illégaux), l’organisme imité | Elle n’ouvre pas de droit à indemnisation et ne vaut pas plainte |
| **Déclaration à la banque** | Bloquer un moyen de paiement et faire examiner les débits contestés | Banque, par un canal choisi par la victime ; déclaration Perceval sur Service-Public.fr pour la carte bancaire utilisée en ligne (FranceConnect, récépissé) | Elle ne qualifie pas l’infraction et ne se substitue pas à une plainte |
| **Information de l’organisme imité** | Lui permettre de prévenir ses clients, de fermer un site ou d’engager ses propres démarches | Canal officiel vérifié par la victime, jamais celui fourni par le message suspect | Elle ne remplace aucune démarche judiciaire |
| **Plainte** | Ouvrir une procédure pénale : le hameçonnage est un délit | Commissariat ou brigade de gendarmerie, courrier au procureur de la République, pré-plainte THESEE pour les escroqueries en ligne | Elle ne garantit ni remboursement ni condamnation ; elle n’est pas automatique |

**Ordre de travail retenu.** 1) Faire le point sur ce qui a circulé. 2) Pour de l’argent, la banque d’abord. 3) Déclaration Perceval si la carte est en possession de la victime. 4) Conserver les preuves tout du long. 5) Prévenir l’organisme imité. 6) Déposer plainte quand les faits sont stables. Les preuves — message d’origine complet, en-têtes, numéros, horaires, captures datées, relevés — conditionnent les étapes 2 à 6 : une démarche sans preuve est une démarche qu’on ne peut pas instruire.

**Canaux et repères vérifiés le 12 novembre 2026.** 17Cyber (diagnostic et orientation) ; Signal Spam (courriels, compte et module de messagerie) ; 33700 (SMS et appels, formulaire ou capture, transmission quotidienne aux opérateurs) ; Phishing Initiative (sites d’hameçonnage) ; Pharos (contenus illégaux, orientation possible vers un service d’enquête) ; Info Escroqueries au 0 805 805 817 (conseil, du lundi au vendredi) ; France Victimes au 116 006 (accompagnement des victimes, sept jours sur sept). Les horaires et formulaires changent : la page officielle reste la source.

**Limites tenues.** Aucun de ces canaux ne promet un remboursement ni une condamnation ; le délai de traitement dépend des services. La qualification pénale change selon les faits : la fiche publique ne remplace ni un avis juridique ni un accompagnement. Les procédures transfrontalières, les menaces immédiates et les situations impliquant une personne mineure sortent de ce tableau et demandent un interlocuteur compétent.

## 5. Sources françaises suivies

Sources consultées le 7 octobre 2026 ; ouvrir la page d’origine avant de reprendre une consigne, une date ou un chiffre. Les résultats d’assistance de Cybermalveillance reflètent les situations prises en charge, pas l’ensemble des fraudes et pas leur part attribuable à l’IA.

| Source | Ce qu’elle apporte | Revue conseillée |
| --- | --- | --- |
| [Cybermalveillance.gouv.fr — rapport d’activité et état de la menace 2025](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/actualites/rapport-activite-2025) | Fuites de données, hameçonnage personnalisé, faux conseillers, fraudes au virement, placements et escroqueries commerciales observés en 2025 | Trimestrielle et à chaque nouveau rapport |
| [Cybermalveillance.gouv.fr — baromètre de perception cyber 2026](https://www.cybermalveillance.gouv.fr/medias/2026/09/Deck-IPSOS-2026-1409-DEF.pdf) | Enquête Ipsos bva : dates, population, méthode et exposition déclarée aux menaces | Avant toute reprise de chiffre |
| [Cybermalveillance.gouv.fr — IA, menaces et opportunités](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/actualites/intelligence-artificielle-ia) | Usages malveillants possibles de contenus audio, vidéo ou photo ; prudence sur l’attribution | Trimestrielle |
| [Cybermalveillance.gouv.fr — hameçonnage : prévention et réaction](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing) | Contact direct, opposition, changement de mots de passe, preuves et signalements | Trimestrielle |
| [Cybermalveillance.gouv.fr — faux message de l’enfant](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/actualites/escroquerie-enfant-probleme-telephone-coucou-papa-maman) | Rappel par un numéro connu avant tout envoi d’argent | Trimestrielle |
| [Cybermalveillance.gouv.fr — faux conseiller bancaire](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/fraude-faux-conseiller-bancaire) | Usurpation téléphonique et conduite à tenir | Trimestrielle |
| [Cybermalveillance.gouv.fr — fausses offres d’emploi](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/fausses-offres-demploi-creees-par-des-fraudeurs) | Recruteurs usurpés, frais, matériel et données personnelles | Trimestrielle |
| [Cybermalveillance.gouv.fr — escroquerie au faux placement](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/escroquerie-placement-financier) | Vérification et réponse aux propositions de placement frauduleuses | Trimestrielle |
| [Cybermalveillance.gouv.fr — usurpation d’identité](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/usurpation-identite-que-faire) | Conservation des preuves et démarches selon le cas | Trimestrielle |
| [17Cyber](https://17cyber.gouv.fr/) | Diagnostic, conseils personnalisés et orientation vers les bons interlocuteurs | À vérifier à chaque revue de la notice ou des consignes |
| [Signal Spam](https://www.signal-spam.fr/) et [33700](https://www.33700.fr/) | Signalement de courriels/spams et de SMS, selon le service concerné | À vérifier avant publication de consignes de signalement |
| [Service-Public.gouv.fr — hameçonnage (phishing ou vishing)](https://www.service-public.gouv.fr/particuliers/vosdroits/F34800) | Qualification en délit, distinction signalement/plainte, voies de plainte ; page vérifiée le 10 avril 2026 | Trimestrielle |
| [Service-Public.gouv.fr — arnaques sur internet (THESEE, Pharos)](https://www.service-public.gouv.fr/particuliers/vosdroits/N31138) | Point d’entrée par situation : hameçonnage, compte piraté, achat, location, rançongiciel, sentiments | Trimestrielle |
| [Service-Public.gouv.fr — fraude à la carte bancaire](https://www.service-public.gouv.fr/particuliers/vosdroits/F31324) | Opposition immédiate, déclaration Perceval avec FranceConnect et récépissé ; page vérifiée le 13 février 2026 | Trimestrielle |
| [Service-Public.gouv.fr — signaler un contenu illégal (Pharos)](https://www.service-public.gouv.fr/particuliers/vosdroits/R17674) | Signalement d’un contenu illicite et orientation vers un service d’enquête | Trimestrielle |
| [Cybermalveillance.gouv.fr — déposer plainte](https://www.cybermalveillance.gouv.fr/tous-nos-contenus/page/deposer-plainte-cybermalveillance) | Commissariat ou brigade, courrier au procureur, pré-plainte THESEE, France Victimes | Trimestrielle |

Le baromètre 2026 consulté indique que 53 % des personnes interrogées de 18 à 75 ans ont déclaré avoir été confrontées à de l’hameçonnage au cours des douze mois précédents, et 15 % à un faux conseiller bancaire. L’enquête en ligne a été menée du 13 au 18 mai 2026 auprès de 2 000 personnes représentatives de cette population. Ces chiffres ne mesurent pas les fraudes utilisant l’IA.

Le rapport d’activité 2025 signale plusieurs hausses de recherches d’assistance pour des familles de fraude ; ces hausses ne mesurent ni une fréquence parmi toute la population, ni la part de fraude causée par l’IA. Toute donnée publique à afficher doit garder sa période, son dénominateur, la source primaire et cette limite.

## 6. Revue continue et seuils de mise à jour

- **Chaque semaine :** l’action GitHub `veille-apprentissages.yml` contrôle les dates de relecture déclarées des fiches et crée ou actualise une issue de suivi. Le script ne navigue pas automatiquement sur les pages des sources ; une relecture humaine reste indispensable.
- **Au moins tous les 90 jours :** vérifier manuellement les sources des quatre fiches IA/fraudes, leurs URL, les consignes de réponse, les coordonnées de signalement et l’adéquation des exemples. Les dates et liens sont enregistrés dans `docs/apprentissage/catalogue.toml`.
- **À réception d’une alerte officielle importante :** relire sans attendre les fiches concernées (par exemple évolution des fraudes bancaires, deepfakes audio/vidéo, faux emplois ou changement du service de signalement) et inscrire la date de consultation.
- **À chaque version :** faire relire les formulations par une personne maîtrisant le sujet ; tester compréhension, clavier, zoom, lecteur d’écran et pertinence des analogies avec des personnes aux parcours différents.
- **Contrôle automatique :** le générateur vérifie les liens HTTPS déclarés, les dates, la cohérence du catalogue et les lacunes du référentiel ; il ne valide ni la disponibilité future d’une page, ni la justesse d’une recommandation extérieure, ni la détection de toutes les fraudes.
- **Traçabilité :** conserver la date de revue, la version de la source, son champ, les limites d’un chiffre et la raison de toute modification. Une URL cassée ou un contenu modifié doit ouvrir une action de vérification.

## 7. Première mise en œuvre dans le dépôt

- Page publique : section « Fraude : vérifier la demande, pas seulement l’apparence » et rappel que la liste n’est ni exhaustive ni spécifique à l’IA. Le 12 novembre 2026 s’y ajoute un bloc « Et surtout : déclarer », qui ordonne les démarches et nomme le canal adapté à chaque support.
- Fiches ajoutées : quatre premières fiches autonomes sur les usages, les médias synthétiques, les sollicitations urgentes et la réaction après incident ; chaque fiche a un intervalle de relecture de 90 à 180 jours.
- Référentiel : les familles, les exemples et les besoins de suivi figurent dans `docs/apprentissage/referentiel.toml` ; toutes les entrées sont marquées comme partielles.
- Lacunes à traiter ensuite : fraudes aux faux investissements et cryptomonnaies ; faux achats, location et paiement ; faux support technique approfondi ; piratage de comptes et fuites de données ; arnaques romantiques ; usurpations visant enfants ou personnes vulnérables ; chantage aux images ; campagnes visant entreprises, associations et collectivités ; usages émergents d’agents autonomes. Chaque sujet devra être sourcé et relu, sans affirmer que cette liste prévoit tous les cas futurs.
