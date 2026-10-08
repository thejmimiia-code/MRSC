# Intégration du simulateur macro-politique au site M.R.S.C

Ce document explique **comment l’outil fonctionne sur le site**, **comment le mettre à jour** et **quoi vérifier** avant de publier. Il s’adresse à toute personne qui reprend le dépôt, sans supposer qu’elle connaisse le projet d’origine.

## L’essentiel en quelques lignes

1. Le simulateur évolue dans **son dépôt** et sa version publique est hébergée sur Render à
   [`https://simulateur-macro-politique.onrender.com/`](https://simulateur-macro-politique.onrender.com/).
   Le site M.R.S.C conserve aussi une **copie datée** du moteur et de sa page.
2. `simulateur.html` connaît deux sources : la version Render, sélectionnée si la page et son
   API répondent, puis la copie embarquée si l’hébergement du site exécute ses fonctions Python.
   Sur un hébergement purement statique, la page donne un lien direct vers Render.
3. L’application en ligne doit servir **`/` (la page interactive) et `/api/…` (son API de calcul)**
   sur la même adresse. Les consignes de maintenance et de vérification figurent dans
   `docs/prompt-session-simulateur.md`.
4. Rien n’est automatique ailleurs : pas de synchronisation de fichiers entre les deux dépôts,
   pas de mise à jour publiée sans décision humaine.

---

## 1. Ce qui a été intégré

Le simulateur est un moteur Python autonome (bibliothèque standard uniquement) publié dans un autre dépôt, sous licence MIT :

> [`thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple`](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple)

Il expose une page interactive et 16 routes HTTP (`/api/catalogue`, `/api/contexte`, `/api/simuler`, `/api/bulles`, `/api/garde_fous`, `/api/export`…). Deux contraintes ont guidé l’intégration :

| Contrainte | Conséquence |
|---|---|
| Le moteur vit dans son dépôt, il ne faut pas le modifier | Le site en embarque une **copie datée** dans `simulateur/`, avec sa provenance et un script de mise à jour |
| Le site est publié sans étape de build ; certains hébergeurs peuvent exécuter Python | La page locale du moteur est **générée une fois** en fichier HTML ; les routes locales sont exposées par des **fonctions** (`api/*.py`) |

## 2. Architecture

```
site M.R.S.C
├── simulateur.html              ← page du site : présentation, limites, aperçu embarqué
├── simulateur/
│   ├── *.py                     ← moteur copié (dépôt d’origine, MIT)
│   ├── index.html               ← page de l’outil, GÉNÉRÉE (ne pas modifier à la main)
│   ├── PROVENANCE.json          ← dépôt amont, révision, date de copie
│   └── pont_api.py              ← AJOUT M.R.S.C : pont vers les fonctions serverless
├── api/
│   ├── *.py                     ← fonctions Python locales, une par route du moteur
│   └── verifier-source.py       ← AJOUT M.R.S.C : la source Render est-elle utilisable ?
├── outils/
│   ├── mettre-a-jour-simulateur.py   ← rapatrie le moteur amont + régénère la page
│   ├── construire-simulateur.py      ← génère simulateur/index.html depuis le moteur
│   ├── generer-fonctions-api.py      ← génère api/*.py depuis les routes du moteur
│   ├── verifier-integration.py       ← contrôle tout, sans navigateur
│   ├── verifier-source-distante.py   ← la version en ligne est-elle utilisable ?
│   ├── verifier-maj-amont.py         ← le moteur embarqué a-t-il pris du retard ?
│   └── serveur-local.py              ← aperçu local complet (site + API + bascule)
└── vercel.json / .vercelignore       ← réglages et périmètre de publication
```

### Pourquoi `simulateur/index.html` est-il généré ?

Le moteur sert sa page depuis la constante `HTML_PAGE` en y remplaçant le repère `===SCENARIOS_JSON===` par le catalogue des scénarios (`simulateur/dashboard.py`). `outils/construire-simulateur.py` fait la même substitution, une fois pour toutes, puis ajoute à la page publiée une barre de retour permanente vers `../index.html`, les réglages de texte/contraste/interligne et des adaptations responsives et clavier pour les tableaux larges. Le moteur amont reste inchangé ; la page devient un fichier statique publiable, servi aussi bien par Vercel que par GitHub Pages, sans exécuter Python pour l’afficher. Les préférences locales sont les mêmes que sur les pages M.R.S.C quand l’origine est la même ; le navigateur interdit leur partage automatique avec une source distante d’une autre origine.


### Réglages d’affichage du simulateur

Le générateur ajoute en plus des boutons A−/A+ (100, 125 et 150 %), contraste renforcé et espacement du texte ; la préférence se mémorise localement. Il ajoute des règles de reflow sous 640 px, élargit les cibles tactiles et rend les deux zones de tableaux focusables au clavier, nommées et annoncées. Ces ajouts et leur justification sont détaillés dans [`rd-affichage-adaptatif.md`](rd-affichage-adaptatif.md). Toute mise à jour du moteur doit être suivie d’une régénération et de `python3 outils/verifier-integration.py` pour garder la page publiée synchronisée.

### À quoi sert `simulateur/pont_api.py` ?

Le moteur route sur son propre `self.path` (`/api/catalogue`, `/api/simuler`…). Sur Vercel, chaque fichier de `api/` devient une route distincte : `FonctionAPI` réécrit le chemin reçu sur la route déclarée par la sous-classe, puis délègue au gestionnaire du moteur. Le comportement des routes est donc **exactement** celui du moteur, sans en modifier une ligne.

C’est aussi ce fichier qui place le cache des données publiques dans `/tmp` : sur un hébergeur à fonctions, le dossier du projet est en lecture seule.

### Les trois modes d’exécution

| Où | Page de l’outil | Routes `/api/…` | Résultat |
|---|---|---|---|
| Render (application du dépôt du simulateur) | application interactive servie à `/` | API Python de la même application | version publique active : `https://simulateur-macro-politique.onrender.com/` |
| Vercel (site M.R.S.C) | `simulateur/index.html` (copie générée) | fonctions Python de `api/` | le site privilégie Render si la sonde confirme la page et l’API ; sinon, la copie locale peut fonctionner |
| Local (`outils/serveur-local.py`) | idem | moteur en interne (port + 1) et fonctions du site montées depuis `api/` | outil complet |
| GitHub Pages (site M.R.S.C) | idem | absentes (pas d’exécution Python) | lien direct vers Render ; la copie locale ne peut pas calculer sur cet hébergement |

Quelle que soit l’adresse, `assets/js/site.js` applique le même ordre de préférence (voir § 5).

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

### Vercel (site M.R.S.C avec fonctions locales facultatives)

Vercel peut héberger **le site M.R.S.C** et les fonctions Python qui permettent à sa copie locale de calculer ; il ne s’agit pas de l’adresse publique active du simulateur, qui est sur Render.

1. **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages : *Framework Preset* **Other**, *Build Command* **vide**, *Output Directory* **`.`**, *Install Command* **vide**.
3. Vérifier après déploiement : `/` (accueil), `/simulateur.html` (présentation), `/simulateur/` (outil), `/api/scenarios` (JSON).
4. **Security → Deployment Protection → Vercel Authentication : Disabled** — sinon un visiteur non connecté voit la page de connexion Vercel à la place du site.

`vercel.json` fixe la durée maximale (60 s) et la mémoire (1 024 Mo) des fonctions : les routes les plus lourdes (`/api/bulles`, `/api/simuler`) ont besoin de quelques secondes à froid. Si l’offre refuse ces valeurs, retirez la clé `functions` : les valeurs par défaut suffisent en général. Aucune dépendance Python n’est à installer, et la version par défaut (3.12) convient au moteur (qui demande ≥ 3.11).

### GitHub Pages (présentation seule)

Le workflow `.github/workflows/deploy-pages.yml` publie les pages du site, la notice `confidentialite.html`, le catalogue et les fiches autonomes de `apprendre/`, `sitemap.xml`, `assets/` et `simulateur/index.html` avec sa provenance. Les sources Python du moteur, les fonctions `api/` et les documents de travail internes ne sont pas publiés. GitHub Pages n’exécute pas Python : le cadre local ne peut donc pas calculer ; la page de présentation propose un lien direct vers le simulateur hébergé sur Render. L’adresse publique du site M.R.S.C est [`https://thejmimiia-code.github.io/MRSC/`](https://thejmimiia-code.github.io/MRSC/) ; celle du simulateur est [`https://simulateur-macro-politique.onrender.com/`](https://simulateur-macro-politique.onrender.com/).

### Local

```sh
python3 outils/serveur-local.py --port 4173 --bind 0.0.0.0
```

Ouvrir `http://localhost:4173/simulateur.html`. Le moteur démarre en interne sur le port suivant ; `--sans-moteur` sert uniquement les fichiers statiques.

## 5. Rester à jour : source Render et copie embarquée

Le simulateur évolue dans son dépôt ; le site M.R.S.C sélectionne la version Render quand elle est vérifiée et garde une copie datée en repli.

### La sélection de la source

`simulateur.html` porte les deux adresses :

```html
<div class="simulateur-cadre" data-simulateur-apercu
     data-src="simulateur/"                                           <!-- copie embarquée -->
     data-source-distante="https://simulateur-macro-politique.onrender.com/"> <!-- source Render -->
```

À chaque visite, `assets/js/site.js` choisit dans cet ordre :

1. **la version Render**, si `api/verifier-source` confirme côté serveur que `/` sert la page
   interactive et qu’au moins une API de calcul répond ;
2. **la copie embarquée**, si l’API locale répond (`HEAD /api/scenarios`) ;
3. à défaut, notamment sur un hébergement purement statique comme GitHub Pages, un avis explicite
   avec un lien direct vers Render, plutôt qu’un cadre vide.

La vérification de la source distante est faite côté serveur : le navigateur ne peut pas lire la réponse
provenant d’une autre origine. Cela évite d’afficher une page de présentation comme si c’était le simulateur.
Sur un hébergement statique, qui n’exécute pas cette fonction ni l’API locale, le lien direct reste disponible.

Pour vérifier l’adresse Render depuis un environnement qui autorise les requêtes sortantes :

```sh
python3 outils/verifier-source-distante.py          # même contrôle que la fonction du site
python3 outils/verifier-source-distante.py --json
```

Le code de sortie vaut 0 si la page et l’API sont reconnues, 1 sinon (avec la raison). La fonction du site attend actuellement au plus 8 secondes par requête ; un démarrage à froid Render plus long, un réseau filtré ou une panne transitoire peut donc entraîner le repli. Ce résultat ne prouve pas à lui seul que l’adresse est définitivement indisponible. Le lien direct est maintenu sur la page.
Pour les consignes de maintenance de l’application amont, voir `docs/prompt-session-simulateur.md`.

Pour forcer la copie locale sur un hébergement avec fonctions Python, retirer l’attribut `data-source-distante`.
Ne pas vider `data-src` : il est nécessaire au chemin de repli.

### L’alerte de mise à jour du moteur embarqué

La copie embarquée est le repli versionné du site et ne calcule que sur un hébergement qui exécute ses fonctions Python. Pour éviter qu’elle prenne du retard, `.github/workflows/maj-simulateur.yml` compare chaque lundi la révision copiée (`simulateur/PROVENANCE.json`) à la branche `main` du dépôt amont. S’il y a du retard, le job échoue et GitHub prévient par courriel (notification par défaut des exécutions planifiées). La veille **ne modifie rien**, ne publie rien et n’écrit nulle part : la mise à jour reste une décision humaine.

```sh
python3 outils/verifier-maj-amont.py     # 0 : à jour · 1 : mise à jour disponible
python3 outils/mettre-a-jour-simulateur.py
```

## 6. Dépannage

| Symptôme | Cause probable | Que faire |
|---|---|---|
| `404 NOT_FOUND` sur `/` dans un ancien déploiement Vercel | Le projet historique ne servait pas l’application ; ce n’est pas l’adresse publique active | Voir le diagnostic historique `docs/diagnostic-404-vercel.md` ; l’adresse active est celle de Render indiquée plus haut |
| La page M.R.S.C affiche « aperçu intégré indisponible » | GitHub Pages n’exécute pas Python, ou les fonctions locales ne sont pas déployées | Ouvrir le lien Render affiché sur la page ; sur Vercel/local, vérifier `/api/scenarios` |
| `/api/...` renvoie une erreur JSON `error` | La route a reçu des paramètres invalides (levier inconnu, corps vide) | Le message du moteur indique le paramètre attendu |
| Réponse lente au premier appel | Démarrage à froid d’une fonction locale ou du service Render | Patienter puis réessayer ; un délai isolé ne suffit pas à conclure à une panne |
| Les chiffres restent « référence datée » | Aucune connexion aux API publiques, repli assumé | Utiliser « Rafraîchir les données » dans l’outil (les valeurs sont alors collectées par le navigateur) |
| La sonde `HEAD /api/scenarios` échoue | L’API locale du site n’est pas joignable | Vérifier les journaux de la fonction, puis relancer `outils/verifier-integration.py` |
| L’avis intégré apparaît sur le site M.R.S.C hébergé sur Vercel | Les fonctions Python du site ne sont pas déployées, ou le projet Vercel est mal configuré | Vérifier que `/api/scenarios` répond ; *Framework Preset* doit rester **Other** |
| Le site affiche la copie embarquée plutôt que Render | La sonde `api/verifier-source` ne reconnaît pas la page ou son API, ou le service Render est encore en démarrage | `python3 outils/verifier-source-distante.py` donne le détail ; ouvrir l’adresse Render directement pour vérifier le service |

## 7. Ce qui n’est pas fait, volontairement

- **Aucune modification du moteur** : il est copié tel quel ; les ajouts du site vivent dans `pont_api.py` et les outils.
- **Aucun build JavaScript, aucune dépendance** : une page HTML générée, des fonctions Python en bibliothèque standard.
- **Aucun suivi analytique observé** : le site ne dépose pas de cookie de mesure ; le simulateur ne demande ni compte ni identité. Les requêtes adressées à Render peuvent néanmoins inclure l’adresse IP et des données techniques ; voir `confidentialite.html`.
- **Aucune publication des sources du moteur sur GitHub Pages** : seuls la page générée et le fichier de provenance sont copiés.
- **Aucune mise à jour automatique** : la veille hebdomadaire alerte, elle ne publie pas ; le moteur copié ne bouge que sur décision humaine.

## 8. Sources

- Vercel — *Python Functions in the /api Directory* : <https://vercel.com/docs/functions/runtimes/python/api-directory>
- Vercel — *Using the Python Runtime with Vercel Functions* (version Python, bundling) : <https://vercel.com/docs/functions/runtimes/python>
- Vercel — *Custom 404 page* (un `404.html` du dossier de sortie est servi automatiquement) : <https://vercel.com/guides/custom-404-page>
- Dépôt du moteur : <https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple> (licence MIT)
