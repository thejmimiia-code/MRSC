# Prompt à coller dans la session du dépôt du simulateur

Session à ouvrir sur `thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple`.

**Le principe, en trois lignes.** Le simulateur est chez lui dans son dépôt : c'est là qu'il
évolue. Son déploiement Vercel doit donc servir **le simulateur lui-même** (sa page *et* son
API de calcul), et le site M.R.S.C s'y branche. Une seule source de vérité, aucune
synchronisation à faire.

---

```text
Objectif : rendre le site Vercel de ce dépôt réellement fonctionnel, c'est-à-dire servir
le simulateur (sa page ET son API de calcul), pour qu'il soit utilisable seul et affichable
par le site du M.R.S.C.

## Contrat attendu (3 points, c'est tout)

1. `/` sert la page du simulateur — la vraie page interactive (constante `HTML_PAGE` de
   `simulateur/interface.py`), pas une page de présentation.
2. `/api/<route>` sert le moteur : les mêmes routes que `simulateur/dashboard.py`
   (`/api/catalogue`, `/api/contexte`, `/api/simuler`, `/api/bulles`, `/api/run`,
   `/api/scenarios`, `/api/export`, `/api/presets`, `/api/comparer`, `/api/bulle`,
   `/api/donnees`, `/api/proxy`).
3. La page reste affichable dans un cadre (`<iframe>`) : ne pas ajouter d'en-tête
   `X-Frame-Options`, ni de `Content-Security-Policy: frame-ancestors`.

La page appelle `/api/...` en chemin absolu : page et API doivent donc être sur la même
adresse, à la racine du domaine. C'est le point à respecter avant tout le reste.

## Situation actuelle (vérifiée, à ne pas refaire)

    curl -sS -o /dev/null -w '%{http_code} /\n' https://d-mocratie-et-politique-du-peuple-p.vercel.app/
    # 404 DEPLOYMENT_NOT_FOUND : aucun index.html sur la branche main
    curl -sS -w '\n%{http_code}\n' https://d-mocratie-et-politique-du-peuple-p.vercel.app/api/scenarios
    # 404 : aucune API exposée

Le déploiement existe et réussit, mais la branche `main` ne contient ni page d'accueil ni
fonctions : Vercel sert le dépôt tel quel, donc `/` ne trouve rien. Une branche non fusionnée
(`arena/98dbb2a2-…`) ajoute des pages vitrines statiques (`index.html`, `docs/index.html`,
`simulateur/index.html`…) : elles décrivent le projet mais ne contiennent aucun appel `/api/`,
donc elles ne font pas fonctionner le simulateur. Ne pas partir de ces vitrines.

## Recette éprouvée (à reprendre telle quelle)

Le dépôt du site M.R.S.C contient une implémentation **déjà écrite et testée** de ce contrat :
`thejmimiia-code/MRSC`, dossier `simulateur/` et dossier `api/`. Elle ne modifie pas le moteur.

- `api/*.py` — un fichier par route, chacun exposant une classe `handler` dérivant de
  `BaseHTTPRequestHandler` (le format reconnu par Vercel pour les fonctions Python fichier
  par fichier) ;
- `simulateur/pont_api.py` — réécrit le chemin reçu (Vercel transmet l'URL complète) sur la
  route déclarée, puis délègue à `simulateur.dashboard.DashboardHandler` : aucune logique
  n'est dupliquée ;
- `outils/generer-fonctions-api.py` — régénère les fonctions en lisant les routes réellement
  servies par `dashboard.py` (si une route est ajoutée au moteur, il le signale).

Le plus simple ici : copier ces trois éléments dans ce dépôt, générer les fonctions, et
écrire un `index.html` à la racine qui sert la page du moteur (même substitution que
`dashboard.py` pour le repère `===SCENARIOS_JSON===`). Sinon, une variante à un seul fichier
avec une réécriture `vercel.json` (`/api/:path*` → `api/index.py`) est possible, mais elle
n'est pas testée : préférer la recette éprouvée.

## Réglages Vercel

- Framework Preset : **Other** · Build Command : **vide** · Output Directory : **`.`**
- Install Command : vide — le moteur n'utilise que la bibliothèque standard Python, aucune
  dépendance à installer, aucun `requirements.txt` à créer.
- Security → Deployment Protection → Vercel Authentication : **Disabled**, sinon un visiteur
  non connecté voit la page de connexion Vercel au lieu du simulateur.
- Ne pas ajouter de `rewrites` attrape-tout : on veut de vrais fichiers, pas des 200 trompeurs.

## Vérification attendue (avant de conclure)

    curl -sS -o /dev/null -w '%{http_code} /\n' https://d-mocratie-et-politique-du-peuple-p.vercel.app/
    # 200, et la page contient #console-pilotage
    curl -sS https://d-mocratie-et-politique-du-peuple-p.vercel.app/api/scenarios
    # {"scenarios": {...}}
    curl -sS -X POST -H 'Content-Type: application/json' \
      -d '{"parametres":{"tva_taux_normal":1.5},"horizon":5}' \
      https://d-mocratie-et-politique-du-peuple-p.vercel.app/api/simuler
    # une simulation complète en JSON

## Côté site M.R.S.C : rien à faire

Le site connaît déjà cette adresse (attribut `data-source-distante` de `simulateur.html`) et
la vérifie à chaque visite : dès que la page et l'API répondent, il affiche cette version et
laisse la copie embarquée de côté. Tant que ce n'est pas le cas, la copie embarquée continue
de faire le calcul — le site reste utilisable. Aucune synchronisation, aucun échange de
fichiers : c'est tout l'intérêt de servir le simulateur depuis son propre dépôt.
```
