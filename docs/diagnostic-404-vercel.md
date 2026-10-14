# Diagnostic historique — erreur Vercel « 404 NOT_FOUND »

> **Mise à jour du 15 octobre 2026 — le dépôt amont a changé depuis le diagnostic initial.**
> Sa branche `main` contient aujourd’hui un `index.html` racine et une route API Python,
> son champ `homepage` désigne `https://d-mocratie-et-politique-du-peuple-p.vercel.app/`,
> et GitHub indique un déploiement *Production — success* pour le commit
> `b7a2d7242f6d8f32efc4b86839baf969208d3a57` (PR amont [#53](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple/pull/53)).
> Ce statut n’est **pas** un test HTTP de l’alias, des API, des calculs ou de l’iframe ; aucun
> accès direct à Vercel n’a été effectué depuis ce dépôt. Les résultats et recommandations
> ci-dessous décrivent l’état constaté à l’époque et ne démontrent pas que l’adresse actuelle
> renvoie encore une 404. Le lien M.R.S.C a depuis été mis à jour vers l’alias Vercel.

**Signalement d'origine** (page d'erreur Vercel, bouton « Copy Debug Prompt ») :

```
404 NOT_FOUND
Request ID: cdg1:cdg1::knh8m-1791313676874-74172451324a
URL: https://d-mocratie-et-politique-du-peuple-pour-le-peup-git-ec5223-mrsc1.vercel.app/
```

**Constat historique en une phrase :** l’adresse signalée était un aperçu (« Preview ») du **dépôt du simulateur macro-politique**, distinct du site M.R.S.C. À la date du signalement, le dépôt déployé ne contenait pas de `index.html` racine ; la page Vercel était « Ready », mais `/` renvoyait 404. La présence ultérieure d’un `index.html` et d’un déploiement de production change ce diagnostic pour l’adresse publique actuelle.

---

## 1. À quel projet appartient cette adresse ?

Une adresse d'aperçu Vercel se lit ainsi :

```
<projet>-git-<branche>-<équipe>.vercel.app
```

L'adresse signalée est **exactement** le lien « Preview » publié par le bot Vercel
sur la PR n° 16 du dépôt `thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple` :

| Élément | Valeur constatée |
|---|---|
| Équipe Vercel | `mrsc1` (`team_5oEq0qjnchjcObNcAO1orMIM`) |
| Projet Vercel | `d-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple` (`prj_hOmat4tB2mJhcCpyu0rZBGh9miVY`) |
| Dépôt GitHub lié | `thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple` (**autre dépôt que MRSC**) |
| Branche déployée | `arena/43a71329-d-mocratie-et-politique-du-peu` (PR n° 16, ouverte) |
| État du déploiement | `Ready` (succès) — le 404 n'est **pas** un échec de build |

Preuves consultables :

```sh
gh pr view 16 -R thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple --json comments
gh api repos/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple/deployments --jq '.[] | [.id, .environment, .ref] | @tsv'
```

Lors de la vérification initiale, le présent dépôt M.R.S.C était publié sur GitHub Pages et aucun déploiement Vercel n’apparaissait dans la liste GitHub consultée. Ce constat historique sert seulement à identifier l’origine de l’erreur signalée ; le projet Vercel M.R.S.C éventuel est distinct du projet amont du simulateur.

## 2. Que servait ce projet Vercel au moment du diagnostic initial ?

Les résultats suivants sont ceux consignés lors du diagnostic initial ; ils ne sont pas des tests actuels :

| Adresse testée | Réponse |
|---|---|
| `https://d-mocratie-et-politique-du-peuple-p.vercel.app/` | **404 NOT_FOUND** (page identique au signalement) |
| `https://d-mocratie-et-politique-du-peuple-p.vercel.app/outils/reglages_depot.html` | **200** — la page s'affiche normalement |

```sh
curl -sS -o /dev/null -w '%{http_code} /\n' https://d-mocratie-et-politique-du-peuple-p.vercel.app/
curl -sS -o /dev/null -w '%{http_code} /outils/reglages_depot.html\n' https://d-mocratie-et-politique-du-peuple-p.vercel.app/outils/reglages_depot.html
```

Ce que ces tests démontraient à cette date (pas l’état présent) :

1. le déploiement **fonctionne** : il sert bien des fichiers du dépôt ;
2. il n'y a **rien à afficher à la racine `/`**, faute d'`index.html` dans le dépôt ;
3. ce n'est donc ni une panne Vercel, ni un déploiement supprimé, ni une adresse
   mal recopiée : c'est un dépôt déployé sans page d'accueil.

Vérification complémentaire consignée au moment du diagnostic : l’arbre `main` ne renvoyait qu'un fichier `.html` (`outils/reglages_depot.html`) et aucun `index.html`. Cette conclusion est dépassée : `main` contient maintenant un `index.html` racine et une route API Python. Aucun contrôle HTTP direct de l’alias actuel n’a été effectué depuis ce dépôt ; sa réponse doit encore être vérifiée dans un navigateur ou depuis un réseau autorisé.

## 3. Deux causes distinctes relevées dans le diagnostic initial

| # | Cause | Effet observé | Correctif |
|---|---|---|---|
| 1 | **Aucun `index.html` à la racine du dépôt déployé** | `/` → `404 NOT_FOUND` (code générique : le chemin demandé n'existe pas dans le déploiement) | Fournir une page d'accueil (`index.html`) ou un dossier de sortie qui en contient une |
| 2 | **Protection des déploiements activée** (Vercel Authentication, active par défaut sur les nouveaux projets) | Un visiteur non connecté à l'équipe voit *« Log in to Vercel »* au lieu du site ; les liens d'aperçu ne sont pas partageables publiquement | Projet → **Security → Deployment Protection → Vercel Authentication : Disabled** (ou « Standard » avec une exception pour l'adresse publique) |

À noter pour lire les codes Vercel : `DEPLOYMENT_NOT_FOUND` signifie que l'adresse ne
correspond à aucun déploiement (déploiement supprimé ou URL erronée) ; `NOT_FOUND` (cas ici)
signifie que le déploiement existe mais que **le chemin demandé n'y existe pas**.

## 4. Correctifs

### A. Pour le projet amont du simulateur — recommandations historiques, désormais dépassées

Le diagnostic initial proposait soit une page racine, soit de publier le site M.R.S.C sur Vercel, et concluait alors qu’il ne fallait pas utiliser Vercel pour le simulateur. Cette conclusion est désormais dépassée. Depuis, le dépôt amont a évolué : la branche `main` contient la page `index.html` et une fonction `api/[...path].py`, et GitHub a signalé un déploiement *Production* réussi. L’adresse Vercel est désormais la cible déclarée par le dépôt et le lien par défaut de M.R.S.C.

Ne pas appliquer la recommandation historique « ne pas héberger le simulateur sur Vercel » ni recopier la page minimale ci-dessus comme solution actuelle. Il reste nécessaire de vérifier en HTTP la racine, `/api/scenarios`, `/api/catalogue`, une simulation, puis l’intégration iframe : un état de déploiement réussi n’établit pas ces résultats.

Le lien Preview de PR #16 décrit dans la section 1 est une adresse d’aperçu d’une ancienne branche ; ne pas le confondre avec l’alias public déclaré `https://d-mocratie-et-politique-du-peuple-p.vercel.app/`.

### A bis. Relation avec le site M.R.S.C

Le site M.R.S.C embarque aussi une copie datée du moteur, une page publiée `simulateur/index.html` et des fonctions `api/*.py` — voir `docs/integration-simulateur.md`. Le projet Vercel éventuel de M.R.S.C est distinct de celui du dépôt amont : héberger le site M.R.S.C sur Vercel n’est pas nécessaire pour ouvrir le simulateur public, et GitHub Pages continue de proposer le lien externe direct.

### B. Pour publier le site M.R.S.C sur Vercel (dépôt MRSC, celui-ci)

Le présent dépôt est un site statique dont `index.html` est bien à la racine : il peut être déployé séparément du projet amont du simulateur. Cette option n’est pas nécessaire pour ouvrir le simulateur public. Marche à suivre :

1. Vercel → **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages (les valeurs par défaut conviennent, à confirmer) :
   * Framework Preset : **Other**
   * Build Command : *(vide)*
   * Output Directory : **`.`**
   * Install Command : *(vide)*
3. **Deploy** : `/` doit répondre `200` et afficher la page d'accueil.
4. **Security → Deployment Protection → Vercel Authentication : Disabled**, sinon un
   visiteur non connecté verra la page de connexion Vercel au lieu du site.
5. Éventuellement : **Settings → Domains** pour une adresse propre (par exemple `mrsc.fr`).

Le dépôt est déjà préparé pour cet hébergement :

| Fichier | Rôle |
|---|---|
| `index.html` (+ 6 pages) et `assets/` | Contenu public, à la racine → servi directement |
| `404.html` | Page d'erreur maison, servie automatiquement par Vercel **et** par GitHub Pages pour toute adresse inconnue (au lieu du message générique de l'hébergeur) |
| `vercel.json` | Mode statique explicite (`cleanUrls: false`, en-têtes de sécurité) |
| `.vercelignore` | Même périmètre que le workflow GitHub Pages : `docs/`, `outils/`, `.github/` ne sont pas publiés |
| `outils/serveur-local.py` | Aperçu local identique aux hébergeurs (404.html sur adresse inconnue, aucun listing) |
| `.github/workflows/deploy-pages.yml` | Publication GitHub Pages (copie désormais `404.html`) |

## 5. Ce que je n'ai pas pu vérifier

L'accès au tableau de bord Vercel (projet et équipe `mrsc1`) requiert une authentification. Les réponses HTTP citées dans les sections 2–3 sont celles du diagnostic initial, pas des contrôles de l’adresse actuelle. Les informations plus récentes proviennent des messages du bot Vercel, du statut de déploiement GitHub et du contenu du dépôt ; aucun test HTTP de l’alias actuel, de ses API ou de son iframe n’a été exécuté ici. Les réglages du projet (Build Command, Output Directory, Deployment Protection) sont à confirmer écran par écran :
**Project → Settings → Build and Development Settings** et **Settings → Deployment Protection**.

## 6. Vérification après correction (à refaire à chaque mise en ligne)

- [ ] Le déploiement est **Ready** (pas *Error*) dans l'onglet *Deployments*.
- [ ] `/` répond **200** et affiche la page d'accueil.
- [ ] Une adresse inconnue (`/test-introuvable`) affiche **notre** `404.html`.
- [ ] Une fenêtre de navigation privée affiche le site **sans** demander de connexion.
- [ ] Onglet *Source* du déploiement → bascule **Output** : `index.html` est bien présent à la racine.

## 7. Sources

- Vercel — *Debug this error code*, `404 NOT_FOUND` : <https://vercel.com/docs/errors/not_found>
- Vercel — *How to debug 404 errors* : <https://vercel.com/kb/guide/how-to-debug-404-errors>
- Vercel — *Custom 404 page* (un `404.html` dans le dossier de sortie est servi automatiquement) : <https://vercel.com/guides/custom-404-page>
- Vercel — *Deployment Protection is now enabled by default for new projects* : <https://vercel.com/changelog/deployment-protection-is-now-enabled-by-default-for-new-projects>
- Vercel Community — *404 NOT_FOUND for simple HTML & CSS site* (Framework `Other`, Build Command vide, Output Directory `.`) : <https://community.vercel.com/t/404-not-found-for-simple-html-css-site/1719>
