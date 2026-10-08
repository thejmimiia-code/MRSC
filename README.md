# M.R.S.C — site public

> **Adresse publique durable du projet : [https://thejmimiia-code.github.io/MRSC/](https://thejmimiia-code.github.io/MRSC/)** — GitHub Pages est activé et HTTPS est imposé. L’adresse reste stable tant que le compte et le dépôt gardent ce nom. Les changements de cette branche seront visibles après intégration à `main` et publication.

Reproduction statique des pages publiques de [www.mrsc.fr](https://www.mrsc.fr/) pour servir de base aux travaux de R&D, complétée par un outil citoyen : le simulateur macro-politique.

## Pages

- `index.html` — accueil recentré sur la mission du M.R.S.C, les expériences de chacun, les apprentissages, le débat, les outils citoyens, les documents et le partage
- `apprendre.html` — parcours d’apprentissage accessibles, repères par matière et difficulté, fiches autonomes et sources sans compte
- `ia-societe.html` — réflexion sur les usages, effets sociaux et fraudes ; réflexes de vérification et liens vers les fiches pratiques
- `simulateur.html` — présentation du simulateur macro-politique, accès à la version interactive hébergée sur Render et aperçu intégré lorsqu’il est disponible
- `documents.html` — statuts, parution au Journal officiel, bulletins d’adhésion et de don
- `liens-utiles.html` — ressources externes référencées sur le site d’origine
- `localisation.html` — carte Google My Maps et repères affichés
- `nous-contacter.html` — coordonnées de contact
- `transparence.html` — projet, méthode, registre des sources page par page et licence d’utilisation
- `confidentialite.html` — information publique sur les préférences locales, les contacts, l’hébergement et les services tiers
- `404.html` — page d’erreur servie par les hébergeurs pour toute adresse inconnue

Le dépôt fournit également un [plan de site XML](sitemap.xml) pour les moteurs d’indexation et une veille éditoriale automatisée sur les fiches, les sources, les dates de revue et les lacunes de couverture. Le détail des traitements de données et les points juridiques à confirmer sont documentés dans [`docs/rd-confidentialite-rgpd.md`](docs/rd-confidentialite-rgpd.md).

La mise en page est responsive, le menu s’adapte aux écrans étroits et des commandes précédent/suivant, accueil et dernière vue rejouent le parcours interne dans l’onglet, avec repli sur la navigation du navigateur si le stockage est bloqué. La suite des pages est conservée dans `sessionStorage` sans paramètres de requête ni données saisies ; la notice publique en détaille la portée. Le panneau « Affichage » propose trois tailles de texte, un contraste renforcé et l’espacement du texte ; ces préférences restent locales et ne remplacent pas le zoom du navigateur. Les règles communes de boutons, cartes, palette et de statut des contenus sont décrites dans [`docs/rd-coherence-visuelle-editoriale.md`](docs/rd-coherence-visuelle-editoriale.md) ; la R&D et la matrice d’essais multi-écrans figurent dans [`docs/rd-affichage-adaptatif.md`](docs/rd-affichage-adaptatif.md). La recherche sur les apprentissages figure dans `docs/rd-parcours-apprentissage.md` ; la veille sur l’IA et les fraudes, dans [`docs/rd-ia-usages-fraudes.md`](docs/rd-ia-usages-fraudes.md) ; `docs/pistes-visuelles-ia.html` présente trois directions graphiques exploratoires, hors navigation publique.

## Le simulateur macro-politique

Le site intègre le **simulateur macro-politique systémique** du projet *Démocratie et politique, du peuple, pour le peuple, par le peuple* : 5 échelons (local → européen → mondial → géopolitique), 93 leviers de politique publique, 20 domaines d’impact notés de 0 à 100, une console de veille des seuils tolérables, des données publiques (Eurostat, BCE, Banque mondiale, Frankfurter) et des exports JSON/CSV.

| Élément | Rôle |
|---|---|
| `simulateur/` | Moteur embarqué (Python), copié depuis son dépôt d’origine — voir `simulateur/PROVENANCE.json` |
| `simulateur/index.html` | Page publiée du simulateur, **générée** depuis le moteur ; le générateur ajoute le retour permanent vers le site, les commandes de parcours et les réglages d’affichage |
| `api/*.py` | Fonctions serveur exposant les 12 routes du moteur (`/api/catalogue`, `/api/simuler`, `/api/bulles`…) |
| `simulateur/pont_api.py` | Pont entre les routes déclarées et le gestionnaire HTTP du moteur (ajout propre au site) |
| `simulateur.html` | Page du site : présentation, limites assumées, aperçu embarqué |
| `outils/verifier-integration.py` | Vérifie la page, les fonctions et chaque route, sans navigateur |

**Le moteur n’est pas modifié** : le site en embarque une copie datée, et deux scripts s’occupent du reste.

```sh
python3 outils/mettre-a-jour-simulateur.py  # rapatrie le moteur amont et régénère la page
python3 outils/construire-simulateur.py     # régénère simulateur/index.html depuis le moteur
python3 outils/generer-fonctions-api.py     # (re)génère les fonctions api/*.py
python3 outils/verifier-integration.py      # contrôle l’ensemble
```

**Deux sources, une seule page.** L’application interactive évolue dans son dépôt et est hébergée à l’adresse publique [https://simulateur-macro-politique.onrender.com/](https://simulateur-macro-politique.onrender.com/). La page `simulateur.html` privilégie cette version si la sonde confirme que la page et son API répondent ; si le site est hébergé sur un service compatible, la copie embarquée peut prendre le relais. Sur GitHub Pages, qui n’exécute pas Python, la page affiche un lien direct vers Render plutôt qu’un faux aperçu fonctionnel. L’adresse Render, et non l’ancienne adresse Vercel du simulateur, est la référence à utiliser.

```sh
python3 outils/verifier-source-distante.py  # contrôle la page Render et son API (0 = oui)
python3 outils/verifier-maj-amont.py        # le moteur embarqué a-t-il pris du retard ? (1 = oui)
```

Une veille hebdomadaire (`.github/workflows/maj-simulateur.yml`) échoue — et prévient par courriel — quand le moteur amont a bougé ; elle ne publie jamais rien à votre place. Les consignes de maintenance et de vérification du service Render sont dans [`docs/prompt-session-simulateur.md`](docs/prompt-session-simulateur.md).

Le site et sa copie embarquée peuvent être testés avec les fonctions Python sur Vercel ou en local. Sur l’adresse GitHub Pages, utilisez le lien Render affiché dans la page du simulateur. Le détail de l’architecture, de la mise à jour et du dépannage est dans [`docs/integration-simulateur.md`](docs/integration-simulateur.md).

## Lancer en local

Depuis la racine du dépôt :

```sh
python3 outils/serveur-local.py --port 4173 --bind 0.0.0.0
```

Puis ouvrir `http://localhost:4173`. Ce serveur reproduit le comportement des hébergeurs : toute adresse inconnue renvoie `404.html`, les dossiers ne sont jamais listés, et `/api/…` est relayé au moteur du simulateur (lancé dans le même processus) — l’aperçu local est donc complet, page et données comprises. L’option `--sans-moteur` se contente des fichiers statiques.

Sans script, un simple serveur de fichiers fonctionne aussi (`python3 -m http.server 4173 --bind 0.0.0.0`), mais il affiche un listing de dossier, un message d’erreur génériques, et l’API du simulateur n’est pas servie.

## Publication sur GitHub Pages

Le workflow `.github/workflows/deploy-pages.yml` valide le HTML, les liens locaux et la syntaxe JavaScript, puis publie les pages HTML (dont `404.html` et `confidentialite.html`), `assets/`, `sitemap.xml`, le catalogue et ses fiches autonomes ainsi que la page du simulateur (`simulateur/index.html` et sa provenance). Les documents de travail dans `docs/`, les outils de `outils/`, les sources Python du moteur et les fonctions `api/` ne sont pas copiés sur le site. Le déploiement est automatique à chaque push sur `main` (un lancement manuel reste possible depuis l’onglet **Actions** avec « Publish M.R.S.C site »). GitHub Pages est actuellement configuré en mode public avec HTTPS ; toute mise à jour de cette branche attend son intégration à `main` et une publication réussie.

GitHub Pages ne sait pas exécuter Python : la copie embarquée ne calcule pas à cette adresse. Pour utiliser l’outil interactif, ouvrez la version publique hébergée sur [Render](https://simulateur-macro-politique.onrender.com/).

## Publication du site M.R.S.C sur Vercel (optionnelle)

Cette configuration concerne l’hébergement du **site M.R.S.C**, pas l’adresse publique active du simulateur, hébergé sur Render. Les fonctions Python de `api/` peuvent aussi faire fonctionner la copie embarquée du site si la source Render ne répond pas. Marche à suivre :

1. Vercel → **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages : *Framework Preset* **Other**, *Build Command* **vide**, *Output Directory* **`.`**, *Install Command* **vide**.
3. Déployer, puis vérifier `/` (accueil), `/simulateur/` (outil) et `/api/scenarios` (JSON).
4. **Security → Deployment Protection → Vercel Authentication : Disabled**, sinon les visiteurs non connectés voient la page de connexion Vercel à la place du site.

Fichiers prévus pour cet hébergement : `vercel.json` (mode statique explicite, en-têtes de sécurité, durée et mémoire des fonctions) et `.vercelignore` (même périmètre de publication que GitHub Pages, `api/` et `simulateur/` compris). Aucune dépendance Python n’est requise : le moteur n’utilise que la bibliothèque standard, et la version Python par défaut de Vercel (3.12) convient.

Un déploiement peut être « Ready » tout en renvoyant `404 NOT_FOUND` sur `/` : cela arrive quand le dépôt déployé ne contient pas d’`index.html` à sa racine. Le diagnostic complet de ce cas, tel qu’il s’est présenté sur un autre projet de l’équipe `mrsc1`, est conservé dans [`docs/diagnostic-404-vercel.md`](docs/diagnostic-404-vercel.md).

## Contenu et ressources externes

Le logo du site a été repris localement dans `assets/images/logo-mrsc.jpg`. Les pages existantes et leurs éléments visibles ont été reconstitués à partir du site public ; `ia-societe.html` réunit désormais une première réflexion sur l’IA et un parcours de prévention des fraudes, complété par des fiches d’apprentissage autonomes. Ces contenus sont une première version à relire, non une liste exhaustive. Les documents PDF (statuts, bulletins et parution officielle) pointent vers leurs fichiers d’origine ; la carte de localisation est intégrée depuis Google My Maps. Ces ressources nécessitent donc encore une connexion à leurs services hébergeurs.

Le moteur du simulateur vient du dépôt [thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple) et reste sous licence **MIT** ; sa révision copiée est enregistrée dans `simulateur/PROVENANCE.json`.

## Transparence et licence

Chaque page publique comporte un encadré « Sources & traçabilité » distinguant les sources externes des apports « Original M.R.S.C ». La page `transparence.html` présente le projet, la méthode, le registre des sources page par page et la licence d'utilisation.

L'outil est open-source et gratuit, selon les conditions du fichier [LICENCE](LICENCE). Toute réutilisation impose l'attribution « Source : M.R.S.C — https://thejmimiia-code.github.io/MRSC/ ». Il est interdit de s'en attribuer le mérite ou la paternité ; l'outil reste la propriété intellectuelle exclusive de son créateur, unique auteur.
