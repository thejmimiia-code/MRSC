# Intégration du simulateur macro-politique au site M.R.S.C

Ce document explique **comment l’outil fonctionne sur le site**, **comment le mettre à jour** et **quoi vérifier** avant de publier. Il s’adresse à toute personne qui reprend le dépôt, sans supposer qu’elle connaisse le projet d’origine.

---

## 1. Ce qui a été intégré

Le simulateur est un moteur Python autonome (bibliothèque standard uniquement) publié dans un autre dépôt, sous licence MIT :

> [`thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple`](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple)

Il expose une page interactive et 12 routes HTTP (`/api/catalogue`, `/api/contexte`, `/api/simuler`, `/api/bulles`, `/api/export`…). Deux contraintes ont guidé l’intégration :

| Contrainte | Conséquence |
|---|---|
| Le moteur vit dans son dépôt, il ne faut pas le modifier | Le site en embarque une **copie datée** dans `simulateur/`, avec sa provenance et un script de mise à jour |
| Le site est un site statique, sans build | La page du moteur est **générée une fois** en fichier HTML ; les routes deviennent des **fonctions** (`api/*.py`) |

## 2. Architecture

```
site M.R.S.C
├── simulateur.html              ← page du site : présentation, limites, aperçu embarqué
├── simulateur/
│   ├── *.py                     ← moteur copié (dépôt d’origine, MIT)
│   ├── index.html               ← page de l’outil, GÉNÉRÉE (ne pas modifier à la main)
│   ├── PROVENANCE.json          ← dépôt amont, révision, date de copie
│   └── pont_api.py              ← AJOUT M.R.S.C : pont vers les fonctions serverless
├── api/*.py                     ← 12 fonctions Vercel, une par route du moteur
├── outils/
│   ├── mettre-a-jour-simulateur.py   ← rapatrie le moteur amont + régénère la page
│   ├── construire-simulateur.py      ← génère simulateur/index.html depuis le moteur
│   ├── generer-fonctions-api.py      ← génère api/*.py depuis les routes du moteur
│   ├── verifier-integration.py       ← contrôle tout, sans navigateur
│   └── serveur-local.py              ← aperçu local complet (site + API)
└── vercel.json / .vercelignore       ← réglages et périmètre de publication
```

### Pourquoi `simulateur/index.html` est-il généré ?

Le moteur sert sa page depuis la constante `HTML_PAGE` en y remplaçant le repère `===SCENARIOS_JSON===` par le catalogue des scénarios (`simulateur/dashboard.py`). `outils/construire-simulateur.py` fait la même substitution, une fois pour toutes : la page devient un fichier statique publiable, servi aussi bien par Vercel que par GitHub Pages, sans exécuter Python pour l’afficher.

### À quoi sert `simulateur/pont_api.py` ?

Le moteur route sur son propre `self.path` (`/api/catalogue`, `/api/simuler`…). Sur Vercel, chaque fichier de `api/` devient une route distincte : `FonctionAPI` réécrit le chemin reçu sur la route déclarée par la sous-classe, puis délègue au gestionnaire du moteur. Le comportement des routes est donc **exactement** celui du moteur, sans en modifier une ligne.

C’est aussi ce fichier qui place le cache des données publiques dans `/tmp` : sur un hébergeur à fonctions, le dossier du projet est en lecture seule.

### Les trois modes d’exécution

| Où | Page de l’outil | Routes `/api/…` | Résultat |
|---|---|---|---|
| Vercel | `simulateur/index.html` (statique) | fonctions Python de `api/` | outil complet |
| Local (`outils/serveur-local.py`) | idem | moteur lancé en interne (port + 1), relais par proxy | outil complet |
| GitHub Pages | idem | absentes (pas d’exécution Python) | présentation seule ; `assets/js/site.js` remplace l’aperçu par un avis explicite |

## 3. Mettre à jour le moteur

Quand le dépôt d’origine évolue :

```sh
python3 outils/mettre-a-jour-simulateur.py          # branche main du dépôt amont
python3 outils/mettre-a-jour-simulateur.py --revision <branche|étiquette|commit>
python3 outils/mettre-a-jour-simulateur.py --depuis /chemin/vers/un/clone   # sans réseau
```

Le script copie les fichiers du paquet, **conserve** ceux listés dans `fichiers_ajoutes_par_le_site` (dont `pont_api.py`), met à jour `PROVENANCE.json`, puis régénère la page.

Après toute mise à jour, et en cas de doute :

```sh
python3 outils/generer-fonctions-api.py --verifier   # les routes exposées couvrent-elles le moteur ?
python3 outils/construire-simulateur.py --verifier   # la page publiée est-elle à jour ?
python3 outils/verifier-integration.py               # page, fonctions, et chaque route interrogée
```

Si le moteur ajoute une route (`/api/nouvelle`), `generer-fonctions-api.py` s’arrête en la signalant : ajoutez son nom à la liste `ROUTES` du script, relancez-le, puis committez la fonction créée. C’est volontairement explicite plutôt qu’automatique : une route exposée est une décision.

## 4. Publier

### Vercel (outil complet)

1. **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages : *Framework Preset* **Other**, *Build Command* **vide**, *Output Directory* **`.`**, *Install Command* **vide**.
3. Vérifier après déploiement : `/` (accueil), `/simulateur.html` (présentation), `/simulateur/` (outil), `/api/scenarios` (JSON).
4. **Security → Deployment Protection → Vercel Authentication : Disabled** — sinon un visiteur non connecté voit la page de connexion Vercel à la place du site.

`vercel.json` fixe la durée maximale (60 s) et la mémoire (1 024 Mo) des fonctions : les routes les plus lourdes (`/api/bulles`, `/api/simuler`) ont besoin de quelques secondes à froid. Si l’offre refuse ces valeurs, retirez la clé `functions` : les valeurs par défaut suffisent en général. Aucune dépendance Python n’est à installer, et la version par défaut (3.12) convient au moteur (qui demande ≥ 3.11).

### GitHub Pages (présentation seule)

Le workflow publie `simulateur.html`, `simulateur/index.html` et `simulateur/PROVENANCE.json`. Les sources du moteur et les fonctions `api/` ne sont pas publiées : les Pages n’exécutent pas de Python, et l’avis « aperçu interactif indisponible » prend la place de l’outil.

### Local

```sh
python3 outils/serveur-local.py --port 4173 --bind 0.0.0.0
```

Ouvrir `http://localhost:4173/simulateur.html`. Le moteur démarre en interne sur le port suivant ; `--sans-moteur` sert uniquement les fichiers statiques.

## 5. Dépannage

| Symptôme | Cause probable | Que faire |
|---|---|---|
| `404 NOT_FOUND` sur `/` | Le dépôt n’a pas d’`index.html` à sa racine, ou le projet déployé n’est pas ce dépôt | Voir `docs/diagnostic-404-vercel.md` |
| La page s’affiche, mais « Aperçu interactif indisponible » | L’hébergeur n’exécute pas Python (GitHub Pages) ou les fonctions ne sont pas déployées | Vérifier `/api/scenarios` ; publier sur Vercel |
| `/api/...` renvoie une erreur JSON `error` | La route a reçu des paramètres invalides (levier inconnu, corps vide) | Le message du moteur indique le paramètre attendu |
| Réponse lente au premier appel | Démarrage à froid d’une fonction | Normal ; `maxDuration` est réglé à 60 s |
| Les chiffres restent « référence datée » | Aucune connexion aux API publiques, repli assumé | Utiliser « Rafraîchir les données » dans l’outil (les valeurs sont alors collectées par le navigateur) |
| La sonde `HEAD /api/scenarios` échoue | Le moteur n’est pas joignable : c’est elle qui décide d’afficher l’aperçu | Vérifier les journaux de la fonction, puis relancer `outils/verifier-integration.py` |

## 6. Ce qui n’est pas fait, volontairement

- **Aucune modification du moteur** : il est copié tel quel ; les ajouts du site vivent dans `pont_api.py` et les outils.
- **Aucun build JavaScript, aucune dépendance** : une page HTML générée, des fonctions Python en bibliothèque standard.
- **Aucun suivi analytique** : le site ne dépose aucun cookie de mesure et le simulateur ne demande aucune donnée personnelle.
- **Aucune publication des sources du moteur sur GitHub Pages** : seuls la page générée et le fichier de provenance sont copiés.

## 7. Sources

- Vercel — *Python Functions in the /api Directory* : <https://vercel.com/docs/functions/runtimes/python/api-directory>
- Vercel — *Using the Python Runtime with Vercel Functions* (version Python, bundling) : <https://vercel.com/docs/functions/runtimes/python>
- Vercel — *Custom 404 page* (un `404.html` du dossier de sortie est servi automatiquement) : <https://vercel.com/guides/custom-404-page>
- Dépôt du moteur : <https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple> (licence MIT)
