# Vote distanciel — minimisation et séparation des données

**Date : 17 octobre 2026. Statut : modèle projeté à expertiser, aucun traitement réel.** Cette note répond à l’objectif de ne pas permettre de remonter d’un bulletin à une personne. Elle ne garantit pas l’anonymat et ne constitue ni analyse d’impact ni avis juridique.

## Principe

Le chiffrement du bulletin ne suffit pas. L’heure, l’adresse réseau, le justificatif, le reçu, la procuration et les journaux peuvent recréer un lien indirect. Le modèle doit empêcher qu’un service, une sauvegarde ou un opérateur puisse réunir les pièces nécessaires à cette corrélation.

Le registre [`vote-distanciel-donnees.toml`](vote-distanciel-donnees.toml) décrit huit catégories projetées et six liaisons interdites. Toutes restent `a-faire-expertiser`.

## Séparation minimale

- Le **registre d’éligibilité** connaît l’identité et le droit, jamais le bulletin, le reçu ou l’heure précise du dépôt.
- L’**urne** connaît un justificatif valable et un bulletin chiffré, jamais le nom, le courriel ou le numéro d’adhérent.
- Le **tableau public** ne reçoit que les artefacts indispensables à la vérification, sans identité ni métadonnée réseau.
- Le **registre de procurations** contrôle les délégations sans accéder aux choix ni aux reçus.
- Les **journaux d’émission et d’urne** restent séparés ; leurs horloges, identifiants et accès doivent faire l’objet d’un test de corrélation.
- Les **autorités de dépouillement** ne reçoivent aucune table d’identité et ne reconstituent jamais une clé complète sur une seule machine.

## Interdictions avant tout essai

- aucune liste réelle d’adhérents ;
- aucun courriel ou compte réel ;
- aucune adresse réseau d’une personne ;
- aucun bulletin réel ;
- aucun export de production ;
- aucune conservation « au cas où » ;
- aucune publication irréversible avant examen des risques de réidentification future.

## Questions obligatoires par catégorie

1. Quelle finalité précise justifie la donnée ?
2. Peut-elle être supprimée, agrégée ou produite localement ?
3. Qui la détient et qui peut techniquement la lire ?
4. À quelles autres données peut-elle être reliée par heure, identifiant, taille ou sauvegarde ?
5. Quelle durée minimale est fixée avant la collecte ?
6. Comment la suppression est-elle vérifiée dans journaux, sauvegardes et miroirs ?
7. Quel recours existe en cas d’erreur, fuite ou corrélation ?

Une réponse « chiffrée » ne répond à aucune de ces questions à elle seule.

## Épreuve de corrélation projetée

Le banc synthétique devra produire des événements d’émission et de dépôt simulés, puis demander à une équipe distincte de tenter de les relier avec les seules données réellement prévues. Le seuil acceptable doit être défini avant l’exercice. Une corrélation exploitable bloque la solution ; elle ne peut pas être compensée par un bon résultat sur un autre critère.

## Conservation et publication

Les preuves publiques peuvent devoir rester disponibles pour vérification, alors que les journaux transitoires doivent être supprimés. Cette tension doit être résolue artefact par artefact avant toute publication. Une chaîne append-only rend la suppression difficile ou impossible : elle ne doit donc jamais contenir une identité, un justificatif brut, une adresse réseau ou un choix individuel.

## Décision de cette passe

Aucun flux n’est autorisé. Le modèle sert à préparer la revue `protection-donnees`, l’analyse juridique et les tests synthétiques. Toute durée, tout détenteur et toute liaison restent des propositions jusqu’à expertise et décision associative.
