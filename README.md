# M.R.S.C — site public

Reproduction statique des pages publiques de [www.mrsc.fr](https://www.mrsc.fr/) pour servir de base aux travaux de R&D.

## Pages

- `index.html` — accueil et présentation de l’association, avec l’IA & société mise en avant
- `ia-societe.html` — première page de réflexion sur les usages, opportunités, risques et effets sociaux de l’intelligence artificielle
- `documents.html` — statuts, parution au Journal officiel, bulletins d’adhésion et de don
- `liens-utiles.html` — ressources externes référencées sur le site d’origine
- `localisation.html` — carte Google My Maps et repères affichés
- `nous-contacter.html` — coordonnées de contact
- `transparence.html` — projet, méthode, registre des sources page par page et licence d’utilisation

La mise en page est responsive, les liens de navigation fonctionnent sans framework et le menu mobile est piloté par `assets/js/site.js`. La veille éditoriale se trouve dans `docs/veille-rd-mrsc.md` ; `docs/pistes-visuelles-ia.html` présente trois directions graphiques exploratoires, hors navigation publique.

## Lancer en local

Depuis la racine du dépôt :

```sh
python3 outils/serveur-local.py --port 4173 --bind 0.0.0.0
```

Puis ouvrir `http://localhost:4173`. Ce serveur reproduit le comportement des hébergeurs (Vercel et GitHub Pages) : toute adresse inconnue renvoie la page `404.html`, et les dossiers ne sont jamais listés — ce qui permet de vérifier une erreur 404 avant publication.

Sans script, un simple serveur de fichiers fonctionne aussi (`python3 -m http.server 4173 --bind 0.0.0.0`), mais il affiche un listing de dossier et un message d'erreur génériques.

## Publication sur GitHub Pages

Le workflow `.github/workflows/deploy-pages.yml` publie les pages HTML (dont `404.html`, la page d'erreur personnalisée), `assets/` et rien d'autre ; les documents de travail dans `docs/` et les outils de `outils/` ne sont pas copiés sur le site. Le déploiement est automatique à chaque push sur `main` (un lancement manuel reste possible depuis l’onglet **Actions** avec « Publish M.R.S.C site »). Prérequis : activer GitHub Pages dans **Settings → Pages → Build and deployment → Source → GitHub Actions**. L’adresse de projet attendue est `https://thejmimiia-code.github.io/MRSC/`.

## Publication sur Vercel

Le site est statique et son `index.html` est à la racine : il s’affiche sur Vercel sans build. Pour le brancher :

1. Vercel → **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages : *Framework Preset* **Other**, *Build Command* **vide**, *Output Directory* **`.`**, *Install Command* **vide**.
3. Déployer, puis vérifier que `/` répond bien (voir la liste de contrôle dans `docs/diagnostic-404-vercel.md`).
4. **Security → Deployment Protection → Vercel Authentication : Disabled**, sinon les visiteurs non connectés voient la page de connexion Vercel à la place du site.

Fichiers prévus pour cet hébergement : `vercel.json` (mode statique explicite et en-têtes de sécurité), `.vercelignore` (même périmètre de publication que GitHub Pages : `docs/`, `outils/` et `.github/` exclus) et `404.html` (page d’erreur maison, servie automatiquement par les deux hébergeurs).

Un déploiement peut être « Ready » tout en renvoyant `404 NOT_FOUND` sur `/` : cela arrive quand le dépôt déployé ne contient pas d’`index.html` à sa racine. Le diagnostic complet de ce cas, tel qu’il s’est présenté sur un autre projet de l’équipe `mrsc1`, est conservé dans `docs/diagnostic-404-vercel.md`.

## Contenu et ressources externes

Le logo du site a été repris localement dans `assets/images/logo-mrsc.jpg`. Les pages existantes et leurs éléments visibles ont été reconstitués à partir du site public ; `ia-societe.html` est un premier contenu de R&D ajouté au site. Les documents PDF (statuts, bulletins et parution officielle) pointent vers leurs fichiers d’origine ; la carte de localisation est intégrée depuis Google My Maps. Ces ressources nécessitent donc encore une connexion à leurs services hébergeurs.

## Transparence et licence

Chaque page publique comporte un encadré « Sources & traçabilité » distinguant les sources externes des apports « Original M.R.S.C ». La page `transparence.html` présente le projet, la méthode, le registre des sources page par page et la licence d'utilisation.

L'outil est open-source et gratuit, selon les conditions du fichier [LICENCE](LICENCE). Toute réutilisation impose l'attribution « Source : M.R.S.C — https://thejmimiia-code.github.io/MRSC/ ». Il est interdit de s'en attribuer le mérite ou la paternité ; l'outil reste la propriété intellectuelle exclusive de son créateur, unique auteur.
