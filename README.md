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
python3 -m http.server 4173 --bind 0.0.0.0
```

Puis ouvrir `http://localhost:4173`.

## Publication sur GitHub Pages

Le workflow `.github/workflows/deploy-pages.yml` publie les pages HTML et `assets/` uniquement ; les documents de travail dans `docs/` ne sont pas copiés sur le site. Le déploiement est automatique à chaque push sur `main` (un lancement manuel reste possible depuis l’onglet **Actions** avec « Publish M.R.S.C site »). Prérequis : activer GitHub Pages dans **Settings → Pages → Build and deployment → Source → GitHub Actions**. L’adresse de projet attendue est `https://thejmimiia-code.github.io/MRSC/`.

## Contenu et ressources externes

Le logo du site a été repris localement dans `assets/images/logo-mrsc.jpg`. Les pages existantes et leurs éléments visibles ont été reconstitués à partir du site public ; `ia-societe.html` est un premier contenu de R&D ajouté au site. Les documents PDF (statuts, bulletins et parution officielle) pointent vers leurs fichiers d’origine ; la carte de localisation est intégrée depuis Google My Maps. Ces ressources nécessitent donc encore une connexion à leurs services hébergeurs.

## Transparence et licence

Chaque page publique comporte un encadré « Sources & traçabilité » distinguant les sources externes des apports « Original M.R.S.C ». La page `transparence.html` présente le projet, la méthode, le registre des sources page par page et la licence d'utilisation.

L'outil est open-source et gratuit, selon les conditions du fichier [LICENCE](LICENCE). Toute réutilisation impose l'attribution « Source : M.R.S.C — https://thejmimiia-code.github.io/MRSC/ ». Il est interdit de s'en attribuer le mérite ou la paternité ; l'outil reste la propriété intellectuelle exclusive de son créateur, unique auteur.
