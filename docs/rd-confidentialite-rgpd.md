# R&D — catégories de données et vie privée du site M.R.S.C

**État de l’inventaire : 8 octobre 2026.** La page publique [`confidentialite.html`](../confidentialite.html) décrit les traitements visibles dans le dépôt. C’est une notice de transparence en cours de validation, pas une attestation de conformité ni un avis juridique. L’association doit confirmer les rôles, bases juridiques, prestataires, règles de conservation et conditions de production avant de considérer l’information comme finalisée.

## Pourquoi une notice même sans compte ni base

L’absence de base de données propre au site n’exclut pas les traitements : l’hébergeur reçoit des requêtes et peut journaliser une adresse IP ; le navigateur garde les préférences et, dans l’onglet courant, une suite de chemins de pages visités ; la personne peut écrire à l’adresse de contact ; une carte externe peut être chargée ; les services tiers reçoivent leurs propres requêtes. La CNIL rappelle qu’une adresse IP peut constituer une donnée personnelle et que l’accès au stockage du navigateur entre dans les technologies de lecture/écriture sur le terminal.

## Inventaire technique observé

L’audit porte sur les fichiers du dépôt et les actions décrites par le code, pas sur une capture réseau complète du site public. La page GitHub Pages de projet confirmée est `https://thejmimiia-code.github.io/MRSC/`. Le dernier workflow de publication consulté a réussi sur `main`, SHA `625eed72e252da71e484589f58942d8dd0b85930`, le 7 octobre 2026. GitHub Pages ne lance pas les fonctions Python du simulateur.

| Catégorie | Ce qui est présent | But observé | Où / destinataire | Durée ou limite connue |
| --- | --- | --- | --- | --- |
| Réponses et progression d’apprentissage | Aucune réponse d’exercice, note, profil ou progression n’est envoyée par les fiches ; pas de compte | Consultation de ressources statiques | Aucune base M.R.S.C observée dans les fichiers étudiés | Non applicable au code actuel |
| Préférences d’affichage | Taille du texte, contraste, espacement ; anciens réglages de taille compatibles | Réappliquer un choix de lisibilité entre les pages | `localStorage` du navigateur, sous l’origine du site ; aucune transmission serveur codée | Jusqu’à l’effacement par la personne ; pas de date d’expiration réglée |
| Parcours de navigation dans l’onglet | Chemins internes et fragments de page, sans paramètres de requête ni texte saisi | Revenir/avancer dans les pages visitées, retourner à l’accueil ou reprendre la dernière vue | `sessionStorage` du navigateur, sous l’origine du site ; aucune transmission serveur codée | Session de l’onglet selon le navigateur, éventuellement restaurée ; l’effacement des données du site ou la fermeture de session la supprime |
| Partage volontaire de l’adresse publique | URL fixe du site, sans texte saisi, historique ni donnée de compte | Ouvrir le menu de partage de l’appareil, copier l’adresse ou préparer un courriel | API de partage du terminal si la personne l’utilise ; presse-papiers local ; aucun envoi vers le serveur M.R.S.C codé | À l’initiative de la personne ; l’application choisie applique ses propres règles ; la copie reste dans le presse-papiers jusqu’à son remplacement ou son effacement |
| Contact volontaire | Adresse de réponse et texte rédigé par la personne ; le contenu peut contenir des données personnelles non sollicitées | Lire et répondre à une demande ou un retour | Logiciel du visiteur, fournisseur d’envoi, boîte `assomrsc@gmail.com` gérée par l’association | Durée interne de la boîte non documentée ; règle de suppression à décider |
| Hébergement et requêtes | GitHub indique qu’il journalise et stocke l’adresse IP des visiteurs de GitHub Pages à des fins de sécurité. Les autres champs techniques et durées sont à confirmer auprès de GitHub | Servir les fichiers, sécurité et disponibilité | GitHub Pages / services GitHub | Aucun contrôle direct des journaux depuis ce dépôt ; période précise non confirmée ici |
| Carte Google | La carte n’est pas chargée automatiquement ; action volontaire par bouton ou lien externe | Afficher une carte de localisation | Google My Maps après activation ; le navigateur contacte Google | Données et durées régies par Google ; à confirmer selon la configuration et les traceurs déposés |
| Liens vers des ressources tierces | Ouverture volontaire de sources, PDF ou services externes | Consulter la ressource demandée | Fournisseur correspondant après clic | Hors contrôle du site ; consulter la notice du fournisseur |
| Simulateur sur GitHub Pages | Tentatives de requêtes à des chemins `/api/…` ; l’API Python locale n’est pas exécutée par GitHub Pages et l’interface propose un lien vers Render | Signaler que la copie embarquée ne peut pas calculer | GitHub Pages pour les requêtes statiques ; aucune progression nominative n’est codée | Journaux éventuels de l’hébergeur, selon ses règles |
| Simulateur hébergé sur Render (adresse active communiquée) | Adresse IP et éléments techniques de requête ; paramètres de simulation transmis à l’API ; éventuellement requêtes aux fournisseurs de données publiques | Servir l’application et calculer les scénarios demandés | Render ; selon l’action « Rafraîchir les données », Eurostat, BCE, Banque mondiale, Frankfurter, Opendatasoft ou fournisseurs de marché | Configuration, journaux, sous-traitants et durées non vérifiés dans ce dépôt ; à confirmer auprès de Render et par l’association |
| Fonctions locales du simulateur sur Vercel (option d’hébergement du site M.R.S.C) | Requêtes vers l’API locale, paramètres de simulation et éventuellement requêtes vers les sources publiques | Faire fonctionner la copie embarquée si le site est déployé sur cet hébergeur et que la source Render n’est pas retenue | Vercel et, selon les sources appelées, Eurostat, BCE, Banque mondiale, Frankfurter, Opendatasoft ou fournisseurs de marché | Cette option n’est pas l’adresse active du simulateur ; déploiement et journaux à confirmer avant usage |

Les données d’accessibilité ne sont pas envoyées au serveur par le code examiné et ne sont pas utilisées pour inférer un handicap. Cela n’exonère pas de qualifier le stockage local conformément aux règles applicables. Une préférence liée à l’affichage ne devient pas automatiquement une catégorie particulière au sens de l’article 9 ; il ne faut toutefois pas chercher à en déduire une information de santé.

## Traceurs et préférences de lecture

Clés de préférences observées dans les scripts : `mrsc-texte-niveau`, `mrsc-contraste-renforce`, `mrsc-espacement-renforce` et le réglage historique `mrsc-texte-agrandi`. Le simulateur embarqué a des clés équivalentes. Elles ne contiennent pas de nom, d’adresse courriel ou de réponse d’exercice. La navigation utilise la clé `mrsc-parcours-navigation-v1` dans `sessionStorage` : les valeurs conservées sont les chemins de pages internes et leurs fragments, sans paramètres de requête, titre de page, texte saisi, identifiant ou réponse d’exercice.

Les règles françaises sur les traceurs visent les API d’accès ou de stockage sur le terminal, notamment `localStorage` et `sessionStorage`. Le bouton de partage peut aussi écrire l’adresse publique dans le presse-papiers sur action explicite ; l’association doit confirmer la qualification juridique de cette écriture avant publication. La CNIL indique que certaines préférences de présentation intrinsèques et attendues du service peuvent relever d’une exemption de consentement ; cela ne vaut pas automatiquement pour tout stockage ni pour tout historique de navigation. Les traitements de données personnelles associés restent soumis aux principes du RGPD. La recommandation consolidée publiée en janvier 2026 rappelle l’importance d’une information transparente.

Choix de conception actuel : la personne active elle-même les préférences d’affichage, qui servent uniquement à conserver ces réglages sur le même site. L’historique de parcours est conservé uniquement pour les commandes demandées de navigation, dans l’onglet courant, sans mesure d’audience ou publicité. À faire valider séparément par l’association : qualification au regard de l’article 82, information sur le terminal, nécessité d’un mécanisme de consentement ou possibilité d’utiliser la fonction sans persistance. Ne pas affirmer une exemption certaine sans cette validation.

## Carte et services tiers

Sur `localisation.html`, l’iframe Google n’a plus de `src` avant l’action « Charger la carte Google dans cette page ». Le lien d’ouverture externe est aussi identifié comme Google et inclut `rel="noreferrer"`. Ce mécanisme évite l’appel automatique de la carte à l’arrivée sur la page ; il ne constitue pas, à lui seul, une analyse juridique du contenu de l’iframe. Vérifier si Google dépose ou lit des traceurs non exemptés après clic et si le choix demandé est suffisamment explicite au regard de la configuration réellement servie.

Aucune balise Analytics, pixel publicitaire, script de police distante ou script social n’a été repéré dans les pages auditées. Le résultat devra être rejoué après toute intégration externe. Une ressource ouverte sur un autre domaine reçoit la requête nécessaire à son affichage ; le site ne contrôle pas la réutilisation faite par ce domaine.

## Éléments à confirmer par l’association

1. Confirmer que l’association M.R.S.C est bien responsable de traitement pour le site, préciser son identité juridique complète et l’adresse de contact pour les demandes de droits.
2. Choisir et documenter la base juridique adaptée au traitement des messages entrants ; éviter de choisir une base uniquement par défaut.
3. Fixer une durée de conservation et une procédure d’effacement des courriels après clôture, avec exceptions justifiées (obligations légales ou litige).
4. Vérifier le fournisseur de la boîte, ses paramètres, les personnes autorisées, les sauvegardes et les éventuels transferts de données.
5. Consulter les conditions et paramètres de GitHub Pages applicables au dépôt public ; distinguer les journaux contrôlés par GitHub des journaux accessibles à l’association.
6. Valider le chargement de Google My Maps, la finalité, les données transmises et la nécessité éventuelle d’un consentement avant toute lecture/écriture de traceur tiers.
7. Pour l’application Render déjà indiquée comme adresse active, confirmer les journaux, leur durée, la région d’hébergement, les sous-traitants, le cache et les requêtes aux sources publiques ; pour les fonctions facultatives du site sur Vercel ou tout autre hébergeur, faire le même inventaire avant activation et actualiser la notice.
8. Refaire un audit réseau dans un vrai navigateur (profil vierge, refus des cookies tiers, première visite, activation de la carte, consultation du simulateur) et compléter avec les tests visuels, clavier et lecteur d’écran déjà prévus.

## Veille à maintenir

Le vérificateur pédagogique contrôle la présence de la page de confidentialité et des liens de navigation. Une revue des données est requise avant toute modification de `localStorage`, `sessionStorage`, formulaire, compte, courriel, contenu intégré, analytics, publication serveur ou traitement d’entrées de simulation. La documentation RGPD doit être révisée dès qu’un destinataire, une finalité ou une durée change ; contrôler que les parcours de navigation restent internes au site et qu’aucune donnée saisie ne s’y ajoute.

## Références consultées

- [CNIL — RGPD : les premières étapes](https://www.cnil.fr/fr/passer-laction/rgpd-les-premieres-etapes) : finalités, catégories, destinataires, durées et information des personnes.
- [CNIL — identifier les données personnelles](https://www.cnil.fr/fr/identifier-les-donnees-personnelles) : l’adresse IP et les identifiants de connexion peuvent être des données personnelles.
- [CNIL — cookies et autres traceurs](https://www.cnil.fr/fr/cookies-et-autres-traceurs/regles/cookies/comment-mettre-mon-site-web-en-conformite) : le stockage du navigateur fait partie des accès au terminal ; l’exemption de personnalisation ne doit pas être étendue sans examen à l’historique de navigation.
- [CNIL — recommandation consolidée sur les cookies et autres traceurs (janvier 2026)](https://www.cnil.fr/sites/default/files/2026-01/recommandation_cookies_consolidee.pdf) : information transparente sur les opérations de lecture/écriture, y compris certaines préférences exemptées.
- [GitHub Docs — What is GitHub Pages?](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) : l’hébergeur indique journaliser et stocker l’adresse IP des visiteurs des sites GitHub Pages pour la sécurité.
- [GitHub — déclaration de confidentialité](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement).
- [CNIL — journalisation](https://www.cnil.fr/fr/la-cnil-publie-une-recommandation-relative-aux-mesures-de-journalisation) : les journaux doivent être proportionnés à leur finalité et leur durée déterminée.
