# Intégration du simulateur macro-politique au site M.R.S.C

Ce document explique **comment l’outil fonctionne sur le site**, **comment le mettre à jour** et **quoi vérifier** avant de publier. Il s’adresse à toute personne qui reprend le dépôt, sans supposer qu’elle connaisse le projet d’origine.

## L’essentiel en quelques lignes

1. Le simulateur évolue dans **son dépôt**. Son adresse publique déclarée est
   [`https://d-mocratie-et-politique-du-peuple-p.vercel.app/`](https://d-mocratie-et-politique-du-peuple-p.vercel.app/).
   La branche amont `main` contient une page `index.html` et une route API ; GitHub a signalé un
   déploiement *Production* réussi le 14 octobre 2026. Ce statut n’est pas un contrôle HTTP ou
   fonctionnel de l’adresse. Le site M.R.S.C conserve aussi une **copie datée** du moteur et de
   sa page, avec un correctif local versionné de sécurité et d’intégration accessible.
2. `simulateur.html` privilégie la source Vercel si la page et son API répondent, puis la copie
   embarquée si l’hébergement M.R.S.C exécute ses fonctions Python. Sur un hébergement purement
   statique, la page donne un lien direct vers Vercel.
3. L’application distante doit servir **`/` (la page interactive) et `/api/…` (son API de calcul)**
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
| Le moteur amont doit rester identifiable et facile à mettre à jour | Le site en embarque une **copie datée** dans `simulateur/`, puis applique le correctif local versionné `outils/patchs/simulateur-securite-mrsc.patch` (sécurité et adaptations d’intégration/accessibilité) ; un échec d’application doit bloquer la mise à jour |
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
│   └── verifier-source.py       ← AJOUT M.R.S.C : la source Vercel est-elle utilisable ?
├── outils/
│   ├── mettre-a-jour-simulateur.py   ← rapatrie le moteur amont + régénère la page
│   ├── construire-simulateur.py      ← génère simulateur/index.html depuis le moteur
│   ├── generer-fonctions-api.py      ← génère api/*.py depuis les routes du moteur
│   ├── verifier-integration.py       ← contrôle tout, sans navigateur
│   ├── verifier-securite.py          ← tests HTTP/WSGI ciblés, sans réseau externe
│   ├── verifier-source-distante.py   ← la version en ligne est-elle utilisable ?
│   ├── verifier-maj-amont.py         ← le moteur embarqué a-t-il pris du retard ?
│   └── serveur-local.py              ← aperçu local complet (site + API + bascule)
└── vercel.json / .vercelignore       ← réglages et périmètre de publication
```

### Pourquoi `simulateur/index.html` est-il généré ?

Le moteur sert sa page depuis la constante `HTML_PAGE` en y remplaçant le repère `===SCENARIOS_JSON===` par le catalogue des scénarios (`simulateur/dashboard.py`). La copie locale de `simulateur/interface.py` reçoit aussi le correctif versionné du site : les choix de scénarios et de préréglages sont des boutons clavier natifs, avec un état `aria-pressed` synchronisé. `outils/construire-simulateur.py` effectue la substitution, puis ajoute à la page publiée une barre de retour permanente vers `../index.html`, les réglages de texte/contraste/interligne et des adaptations responsives et clavier pour les tableaux larges. La page devient ainsi un fichier statique publiable, servi par Vercel ou GitHub Pages, sans exécuter Python pour l’afficher ; les fonctions de calcul restent nécessaires à la copie locale. Le correctif ne modifie pas le dépôt amont ni son déploiement Vercel indépendant. Les préférences locales sont les mêmes que sur les pages M.R.S.C quand l’origine est la même ; le navigateur interdit leur partage automatique avec une source distante d’une autre origine.


### Réglages d’affichage du simulateur

Le générateur ajoute des boutons A−/A+ (100, 125 et 150 %), contraste renforcé et espacement du texte ; la préférence se mémorise localement. Il ajoute des règles de reflow sous 640 px et conserve des cibles tactiles d’au moins 44 px. Les tableaux de résultats, les tableaux créés à la demande dans les sept vues par strate et ceux de l’audit sont contenus dans des régions horizontalement défilables, nommées et accessibles au clavier ; le journal causal l’est également. Les textes secondaires et titres de familles utilisent des couleurs lisibles indépendamment des accents décoratifs. Les scénarios historiques et préréglages sont des boutons natifs : ils reçoivent le focus, s’activent au clavier et annoncent leur état sélectionné. Ces ajouts et leur justification sont détaillés dans [`rd-affichage-adaptatif.md`](rd-affichage-adaptatif.md). Toute mise à jour du moteur doit être suivie d’une régénération, de `python3 outils/verifier-integration.py`, puis d’un contrôle réel du rendu responsive, du clavier et de l’accessibilité automatisée ; le vérificateur statique ne remplace pas ces essais.

### À quoi sert `simulateur/pont_api.py` ?

Le moteur route sur son propre `self.path` (`/api/catalogue`, `/api/simuler`…). Sur Vercel, chaque fichier de `api/` devient une route distincte : `FonctionAPI` réécrit le chemin reçu sur la route déclarée par la sous-classe, puis délègue au gestionnaire. La copie locale conserve le comportement métier amont, mais le patch M.R.S.C borne les requêtes, retire les traces d’erreur des réponses, valide les provenances, rend les lectures navigateur propres à la requête et échappe les champs affichés. Ce patch local ne s’applique pas au déploiement Vercel indépendant hébergé dans l’autre dépôt.

C’est aussi ce fichier qui place le cache des données publiques dans `/tmp` : sur un hébergeur à fonctions, le dossier du projet est en lecture seule. Les lectures `/api/proxy` sont gardées en cache 60 secondes ; si une collecte externe, un rafraîchissement des marchés ou le calcul d’un catalogue complet de bulles est déjà en cours, un nouvel appel coûteux reçoit rapidement HTTP 503 au lieu d’empiler des threads. Les cibles de requête sont limitées à 16 Kio et 128 champs ; les sélections de leviers en double sont dédupliquées. Les réponses des séries macro sont plafonnées à 8 Mio, celles des cotations à 1 Mio ; les deux clients refusent les redirections HTTP. En cas d’échec, le moteur essaie une autre source déclarée ou une référence datée. Ces limites restent propres à chaque processus, pas globales entre instances.

### Les trois modes d’exécution

| Où | Page de l’outil | Routes `/api/…` | Résultat |
|---|---|---|---|
| Vercel (application du dépôt amont) | application interactive servie à `/` | API Python de la même application | adresse déclarée : `https://d-mocratie-et-politique-du-peuple-p.vercel.app/` ; statut de déploiement GitHub réussi, HTTP non contrôlé ici |
| Vercel (site M.R.S.C, projet distinct) | `simulateur/index.html` (copie générée) | fonctions Python de `api/` | le site peut sélectionner l’application amont si la sonde confirme la page et l’API ; sinon, la copie locale peut fonctionner |
| Local (`outils/serveur-local.py`) | idem | moteur en interne (port + 1) et fonctions du site montées depuis `api/` | outil complet |
| GitHub Pages (site M.R.S.C) | idem | absentes (pas d’exécution Python) | lien direct vers Vercel ; la copie locale ne peut pas calculer sur cet hébergement |

Quelle que soit l’adresse, `assets/js/site.js` applique le même ordre de préférence (voir § 5).

## 3. Mettre à jour le moteur

Quand le dépôt d’origine évolue :

```sh
python3 outils/mettre-a-jour-simulateur.py          # branche main du dépôt amont
python3 outils/mettre-a-jour-simulateur.py --revision <branche|étiquette|commit>
python3 outils/mettre-a-jour-simulateur.py --depuis /chemin/vers/un/clone   # sans réseau
```

Le script copie d’abord le paquet dans un dossier temporaire, **conserve** ceux listés dans `fichiers_ajoutes_par_le_site` (dont `pont_api.py`), vérifie que `outils/patchs/simulateur-securite-mrsc.patch` s’applique, puis seulement remplace la copie locale, met à jour `PROVENANCE.json` (y compris l’empreinte SHA-256 du patch) et régénère la page. En cas de conflit, il s’arrête avant de remplacer le moteur ; si l’amont contient déjà le patch complet, il le détecte. Vérifier le patch et l’intégration à chaque mise à jour amont ; le déploiement Vercel distant doit être vérifié séparément dans son dépôt et son projet.

Après toute mise à jour, et en cas de doute :

```sh
python3 outils/generer-fonctions-api.py --verifier   # les routes exposées couvrent-elles le moteur ?
python3 outils/construire-simulateur.py --verifier   # la page publiée est-elle à jour ?
python3 outils/verifier-securite.py                  # régressions ciblées, sans réseau externe
python3 outils/verifier-integration.py               # page, fonctions, et chaque route interrogée
```

Si le moteur ajoute une route (`/api/nouvelle`), `generer-fonctions-api.py` s’arrête en la signalant : ajoutez son nom à la liste `ROUTES` du script, relancez-le, puis committez la fonction créée. C’est volontairement explicite plutôt qu’automatique : une route exposée est une décision.

## 4. Publier

### Vercel (site M.R.S.C avec fonctions locales facultatives)

Vercel héberge l’application du simulateur dans le dépôt amont. Un **projet Vercel distinct** peut aussi héberger le site M.R.S.C et ses fonctions Python, qui permettent à la copie locale de calculer.

1. **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages : *Framework Preset* **Other**, *Build Command* **vide**, *Output Directory* **`.`**, *Install Command* **vide**.
3. Vérifier après déploiement : `/` (accueil), `/simulateur.html` (présentation), `/simulateur/` (outil), `/api/scenarios` (JSON).
4. **Security → Deployment Protection → Vercel Authentication : Disabled** — sinon un visiteur non connecté voit la page de connexion Vercel à la place du site.

`vercel.json` fixe la durée maximale (60 s) et la mémoire (1 024 Mo) des fonctions : les routes les plus lourdes (`/api/bulles`, `/api/simuler`) ont besoin de quelques secondes à froid. Il ajoute aussi des en-têtes de base (`nosniff`, HSTS, politique de référent, permissions, framing et CSP limitée). Cette CSP ne définit pas `script-src` : le moteur contient encore du JavaScript inline. Ne pas la présenter comme une protection XSS complète ni supposer qu’elle décrit les en-têtes du déploiement amont sans les vérifier. GitHub Pages n’applique pas cette configuration. Si l’offre refuse les paramètres `functions`, retirez-les : les valeurs par défaut suffisent en général. Aucune dépendance Python n’est à installer, et la version par défaut (3.12) convient au moteur (qui demande ≥ 3.11).

### GitHub Pages (présentation seule)

Le workflow `.github/workflows/deploy-pages.yml` publie les pages du site, la notice `confidentialite.html`, le catalogue et les fiches autonomes de `apprendre/`, `sitemap.xml`, `assets/` et `simulateur/index.html` avec sa provenance. Les sources Python du moteur, les fonctions `api/` et les documents de travail internes ne sont pas publiés. GitHub Pages n’exécute pas Python : le cadre local ne peut donc pas calculer ; la page de présentation propose un lien direct vers le simulateur amont sur Vercel. L’adresse publique du site M.R.S.C est [`https://thejmimiia-code.github.io/MRSC/`](https://thejmimiia-code.github.io/MRSC/) ; celle du simulateur est [`https://d-mocratie-et-politique-du-peuple-p.vercel.app/`](https://d-mocratie-et-politique-du-peuple-p.vercel.app/).

### Local

```sh
python3 outils/serveur-local.py --port 4173
```

Ouvrir `http://localhost:4173/simulateur.html`. Le serveur écoute sur `127.0.0.1` et ne sert que les fichiers destinés à la publication ; le moteur démarre en interne sur le port suivant. N’utilisez `--bind 0.0.0.0` que si un accès depuis le réseau est nécessaire et compris ; `--sans-moteur` sert uniquement les fichiers statiques.

## 5. Rester à jour : source Vercel et copie embarquée

Le simulateur évolue dans son dépôt ; le site M.R.S.C sélectionne la version Vercel quand elle est vérifiée et garde une copie datée en repli. L’ancienne adresse Render n’est plus la cible par défaut ; la sonde la conserve dans sa liste pour compatibilité, sans que sa disponibilité soit vérifiée.

### La sélection de la source

`simulateur.html` porte les deux adresses :

```html
<div class="simulateur-cadre" data-simulateur-apercu
     data-src="simulateur/"                                           <!-- copie embarquée -->
     data-source-distante="https://d-mocratie-et-politique-du-peuple-p.vercel.app/"> <!-- source distante -->
```

À chaque visite, `assets/js/site.js` choisit dans cet ordre :

1. **la version Vercel du dépôt amont**, si `api/verifier-source` confirme côté serveur que `/`
   sert la page interactive et qu’au moins une API de calcul répond ;
2. **la copie embarquée**, si l’API locale répond (`HEAD /api/scenarios`) ;
3. à défaut, notamment sur un hébergement purement statique comme GitHub Pages, un avis explicite
   avec un lien direct vers Vercel, plutôt qu’un cadre vide.

La vérification de la source distante est faite côté serveur : le navigateur ne peut pas lire la réponse
provenant d’une autre origine. Cela évite d’afficher une page de présentation comme si c’était le simulateur.
La fonction n’appelle que l’hôte Vercel déclaré ou l’ancien hôte Render conservé pour compatibilité, ainsi que les hôtes HTTPS exacts explicitement autorisés pour une préproduction ; elle refuse les identifiants, chemins arbitraires et redirections. L’exception localhost est réservée aux tests locaux par variable d’environnement. La query publique ne permet pas de contourner le cache de cinq minutes. Sur un hébergement statique, qui n’exécute pas cette fonction ni l’API locale, le lien direct reste disponible.

Pour vérifier l’adresse Vercel depuis un environnement qui autorise les requêtes sortantes :

```sh
python3 outils/verifier-source-distante.py          # même contrôle que la fonction du site
python3 outils/verifier-source-distante.py --json
```

Le code de sortie vaut 0 si la page et l’API sont reconnues, 1 sinon (avec la raison). La fonction du site attend actuellement au plus 8 secondes par requête ; un démarrage à froid, un réseau filtré ou une panne transitoire peut donc entraîner le repli. Un échec ponctuel ne prouve pas à lui seul que l’adresse est définitivement indisponible. Le lien direct est maintenu sur la page. Un statut *Production — success* dans GitHub ne remplace pas ce contrôle HTTP.
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
| `404 NOT_FOUND` sur `/` dans un ancien déploiement Vercel | État historique d’un déploiement sans page racine ; la branche amont contient désormais `index.html` | Le diagnostic `docs/diagnostic-404-vercel.md` conserve le contexte. Tester directement l’alias actuel et `/api/scenarios` ; le statut GitHub seul ne prouve pas la réponse HTTP. |
| La page M.R.S.C affiche « aperçu intégré indisponible » | GitHub Pages n’exécute pas Python, ou les fonctions locales ne sont pas déployées | Ouvrir le lien Vercel affiché sur la page ; sur un projet M.R.S.C Vercel/local, vérifier `/api/scenarios`. |
| `/api/...` renvoie une erreur JSON `error` | La route a reçu des paramètres invalides (levier inconnu, corps vide) | Le message du moteur indique le paramètre attendu |
| Réponse lente au premier appel | Démarrage à froid d’une fonction ou délai réseau | Patienter puis réessayer ; un délai isolé ne suffit pas à conclure à une panne |
| Les chiffres restent « référence datée » | Aucune connexion aux API publiques, repli assumé | Utiliser « Rafraîchir les données » dans l’outil (les valeurs sont alors collectées par le navigateur) |
| La sonde `HEAD /api/scenarios` échoue | L’API locale du site n’est pas joignable | Vérifier les journaux de la fonction, puis relancer `outils/verifier-integration.py` |
| L’avis intégré apparaît sur le site M.R.S.C hébergé sur Vercel | Les fonctions Python du site ne sont pas déployées, ou le projet Vercel M.R.S.C est mal configuré | Vérifier que `/api/scenarios` répond ; *Framework Preset* doit rester **Other** |
| L’adresse Vercel affiche une demande de connexion | Une protection de déploiement peut être active sur le projet amont | Tester en fenêtre privée et vérifier la protection d’accès du projet Vercel ; ce réglage n’a pas été contrôlé depuis ce dépôt |
| Le site affiche la copie embarquée plutôt que la version amont | La sonde `api/verifier-source` ne reconnaît pas la page ou son API, ou la source est temporairement lente | `python3 outils/verifier-source-distante.py` donne le détail ; ouvrir l’adresse publique directement pour contrôler le service. |
| L’adresse Vercel s’ouvre mais le simulateur reste en chargement | L’état de déploiement ne localise pas une erreur d’exécution côté navigateur/API | Tester `/api/scenarios`, puis examiner la console et les requêtes réseau du navigateur ; aucun diagnostic direct de production n’a été effectué depuis ce dépôt. |

## 7. Ce qui n’est pas fait, volontairement

- **Aucune modification du dépôt amont** : la copie locale `simulateur/` reçoit un correctif versionné propre au site (sécurité, accessibilité des cartes de scénario et intégration) ; ce correctif ne s’applique pas automatiquement au déploiement Vercel amont, à maintenir séparément.
- **Aucun build JavaScript, aucune dépendance** : une page HTML générée, des fonctions Python en bibliothèque standard.
- **Aucun suivi analytique observé** : le site ne dépose pas de cookie de mesure ; le simulateur ne demande ni compte ni identité dans le code examiné. Les requêtes adressées à l’application Vercel peuvent néanmoins contenir des données techniques comme l’adresse IP ; journaux et durées restent à confirmer, voir `confidentialite.html`.
- **Aucune publication des sources du moteur sur GitHub Pages** : seuls la page générée et le fichier de provenance sont copiés.
- **Aucune mise à jour automatique** : la veille hebdomadaire alerte, elle ne publie pas ; le moteur copié ne bouge que sur décision humaine.

## 8. Sources

- Vercel — *Python Functions in the /api Directory* : <https://vercel.com/docs/functions/runtimes/python/api-directory>
- Vercel — *Using the Python Runtime with Vercel Functions* (version Python, bundling) : <https://vercel.com/docs/functions/runtimes/python>
- Vercel — *Custom 404 page* (un `404.html` du dossier de sortie est servi automatiquement) : <https://vercel.com/guides/custom-404-page>
- Dépôt du moteur : <https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple> (licence MIT) ; `index.html` à la racine de `main` et route Python `api/[...path].py` consultés le 15 octobre 2026.
- PR amont #53, fusionnée le 14 octobre 2026 ; GitHub signale un déploiement *Production* réussi pour le commit `b7a2d7242f6d8f32efc4b86839baf969208d3a57` : <https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple/pull/53>. Ce statut n’est pas une requête HTTP directe à l’alias public.
