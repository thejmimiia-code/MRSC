# M.R.S.C — site public

Reproduction statique des pages publiques de [www.mrsc.fr](https://www.mrsc.fr/) pour servir de base aux travaux de R&D, complétée par un outil citoyen : le simulateur macro-politique.

## Pages

- `index.html` — accueil et présentation de l’association, avec l’IA & société en avant
- `ia-societe.html` — première page de réflexion sur les usages, opportunités, risques et effets sociaux de l’intelligence artificielle
- `simulateur.html` — présentation du simulateur macro-politique et aperçu embarqué de l’outil
- `documents.html` — statuts, parution au Journal officiel, bulletins d’adhésion et de don
- `liens-utiles.html` — ressources externes référencées sur le site d’origine
- `localisation.html` — carte Google My Maps et repères affichés
- `nous-contacter.html` — coordonnées de contact
- `transparence.html` — projet, méthode, registre des sources page par page et licence d’utilisation
- `404.html` — page d’erreur servie par les hébergeurs pour toute adresse inconnue

La mise en page est responsive, les liens de navigation fonctionnent sans framework et le menu mobile est piloté par `assets/js/site.js`. La veille éditoriale se trouve dans `docs/veille-rd-mrsc.md` ; `docs/pistes-visuelles-ia.html` présente trois directions graphiques exploratoires, hors navigation publique.

## Le simulateur macro-politique

Le site intègre le **simulateur macro-politique systémique** du projet *Démocratie et politique, du peuple, pour le peuple, par le peuple* : 5 échelons (local → européen → mondial → géopolitique), 93 leviers de politique publique, 20 domaines d’impact notés de 0 à 100, une console de veille des seuils tolérables, des données publiques (Eurostat, BCE, Banque mondiale, Frankfurter) et des exports JSON/CSV.

| Élément | Rôle |
|---|---|
| `simulateur/` | Moteur embarqué (Python), copié depuis son dépôt d’origine — voir `simulateur/PROVENANCE.json` |
| `simulateur/index.html` | Page publiée du simulateur, **générée** depuis le moteur (`outils/construire-simulateur.py`) |
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

**Deux sources, une seule page.** Le simulateur se développe en continu dans son dépôt ; la page `simulateur.html` connaît donc les deux : la **version en développement** (le projet en ligne) et la **copie embarquée** du moteur. À chaque visite, le site interroge `api/verifier-source`, qui vérifie côté serveur que la version en ligne sert bien *la page du moteur et une API de calcul* : si oui, elle est affichée (toujours à jour) ; sinon, la copie embarquée prend le relais. Sans cette vérification, on afficherait comme simulateur une simple page de présentation. Deux commandes pour suivre le tout :

```sh
python3 outils/verifier-source-distante.py  # la version en ligne est-elle utilisable ? (0 = oui)
python3 outils/verifier-maj-amont.py        # le moteur embarqué a-t-il pris du retard ? (1 = oui)
```

Une veille hebdomadaire (`.github/workflows/maj-simulateur.yml`) échoue — et prévient par courriel — quand le moteur amont a bougé ; elle ne publie jamais rien à votre place. Pour rendre la version en ligne utilisable, le prompt à coller dans la session du dépôt du simulateur est dans [`docs/prompt-session-simulateur.md`](docs/prompt-session-simulateur.md).

L’outil interactif a besoin d’un hébergeur qui exécute du Python (Vercel, ou votre machine). Sur un hébergement purement statique (GitHub Pages), la page de présentation s’affiche et un avis remplace l’aperçu embarqué. Le détail de l’architecture, de la mise à jour et du dépannage est dans [`docs/integration-simulateur.md`](docs/integration-simulateur.md).

## Lancer en local

Depuis la racine du dépôt :

```sh
python3 outils/serveur-local.py --port 4173 --bind 0.0.0.0
```

Puis ouvrir `http://localhost:4173`. Ce serveur reproduit le comportement des hébergeurs : toute adresse inconnue renvoie `404.html`, les dossiers ne sont jamais listés, et `/api/…` est relayé au moteur du simulateur (lancé dans le même processus) — l’aperçu local est donc complet, page et données comprises. L’option `--sans-moteur` se contente des fichiers statiques.

Sans script, un simple serveur de fichiers fonctionne aussi (`python3 -m http.server 4173 --bind 0.0.0.0`), mais il affiche un listing de dossier, un message d’erreur génériques, et l’API du simulateur n’est pas servie.

## Publication sur GitHub Pages

Le workflow `.github/workflows/deploy-pages.yml` publie les pages HTML (dont `404.html`), `assets/` et la page du simulateur (`simulateur/index.html` et sa provenance) ; les documents de travail dans `docs/`, les outils de `outils/`, les sources Python du moteur et les fonctions `api/` ne sont pas copiés sur le site. Le déploiement est automatique à chaque push sur `main` (un lancement manuel reste possible depuis l’onglet **Actions** avec « Publish M.R.S.C site »). Prérequis : activer GitHub Pages dans **Settings → Pages → Build and deployment → Source → GitHub Actions**. L’adresse de projet attendue est `https://thejmimiia-code.github.io/MRSC/`.

Les Pages ne savent pas exécuter Python : sur cette adresse, le simulateur se présente mais ne calcule pas. Pour l’outil interactif, utilisez Vercel ou un lancement local.

## Publication sur Vercel

Le site est statique et son `index.html` est à la racine ; les fonctions Python de `api/` donnent vie au simulateur. Marche à suivre :

1. Vercel → **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages : *Framework Preset* **Other**, *Build Command* **vide**, *Output Directory* **`.`**, *Install Command* **vide**.
3. Déployer, puis vérifier `/` (accueil), `/simulateur/` (outil) et `/api/scenarios` (JSON).
4. **Security → Deployment Protection → Vercel Authentication : Disabled**, sinon les visiteurs non connectés voient la page de connexion Vercel à la place du site.

Fichiers prévus pour cet hébergement : `vercel.json` (mode statique explicite, en-têtes de sécurité, durée et mémoire des fonctions) et `.vercelignore` (même périmètre de publication que GitHub Pages, `api/` et `simulateur/` compris). Aucune dépendance Python n’est requise : le moteur n’utilise que la bibliothèque standard, et la version Python par défaut de Vercel (3.12) convient.

Un déploiement peut être « Ready » tout en renvoyant `404 NOT_FOUND` sur `/` : cela arrive quand le dépôt déployé ne contient pas d’`index.html` à sa racine. Le diagnostic complet de ce cas, tel qu’il s’est présenté sur un autre projet de l’équipe `mrsc1`, est conservé dans [`docs/diagnostic-404-vercel.md`](docs/diagnostic-404-vercel.md).

## Contenu et ressources externes

Le logo du site a été repris localement dans `assets/images/logo-mrsc.jpg`. Les pages existantes et leurs éléments visibles ont été reconstitués à partir du site public ; `ia-societe.html` est un premier contenu de R&D ajouté au site. Les documents PDF (statuts, bulletins et parution officielle) pointent vers leurs fichiers d’origine ; la carte de localisation est intégrée depuis Google My Maps. Ces ressources nécessitent donc encore une connexion à leurs services hébergeurs.

Le moteur du simulateur vient du dépôt [thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple) et reste sous licence **MIT** ; sa révision copiée est enregistrée dans `simulateur/PROVENANCE.json`.

## Transparence et licence

Chaque page publique comporte un encadré « Sources & traçabilité » distinguant les sources externes des apports « Original M.R.S.C ». La page `transparence.html` présente le projet, la méthode, le registre des sources page par page et la licence d'utilisation.

L'outil est open-source et gratuit, selon les conditions du fichier [LICENCE](LICENCE). Toute réutilisation impose l'attribution « Source : M.R.S.C — https://thejmimiia-code.github.io/MRSC/ ». Il est interdit de s'en attribuer le mérite ou la paternité ; l'outil reste la propriété intellectuelle exclusive de son créateur, unique auteur.
