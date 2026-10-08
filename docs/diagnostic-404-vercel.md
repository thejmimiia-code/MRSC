# Diagnostic — erreur Vercel « 404 NOT_FOUND »

**Signalement d'origine** (page d'erreur Vercel, bouton « Copy Debug Prompt ») :

```
404 NOT_FOUND
Request ID: cdg1:cdg1::knh8m-1791313676874-74172451324a
URL: https://d-mocratie-et-politique-du-peuple-pour-le-peup-git-ec5223-mrsc1.vercel.app/
```

**En une phrase :** cette adresse n'appartient pas au site M.R.S.C. C'est un aperçu
(« Preview ») du **dépôt du simulateur macro-politique**, et le 404 vient de ce que
**ce dépôt ne contient aucun `index.html`** : Vercel sert le dépôt tel quel, donc `/`
ne trouve aucun fichier à afficher. Le déploiement, lui, est bien « Ready ».

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

Le projet M.R.S.C (`assets/`, `index.html`, pages `.html`) n'a, lui, **aucun déploiement
Vercel** : son historique d'hébergement est GitHub Pages (`github-pages` dans la liste des
déploiements GitHub de `thejmimiia-code/MRSC`). Le 404 signalé ne peut donc pas venir
du présent dépôt.

## 2. Que sert réellement ce projet Vercel ?

Test sur le domaine public du même projet (production, sans protection) :

| Adresse testée | Réponse |
|---|---|
| `https://d-mocratie-et-politique-du-peuple-p.vercel.app/` | **404 NOT_FOUND** (page identique au signalement) |
| `https://d-mocratie-et-politique-du-peuple-p.vercel.app/outils/reglages_depot.html` | **200** — la page s'affiche normalement |

```sh
curl -sS -o /dev/null -w '%{http_code} /\n' https://d-mocratie-et-politique-du-peuple-p.vercel.app/
curl -sS -o /dev/null -w '%{http_code} /outils/reglages_depot.html\n' https://d-mocratie-et-politique-du-peuple-p.vercel.app/outils/reglages_depot.html
```

Ce que cela démontre :

1. le déploiement **fonctionne** : il sert bien des fichiers du dépôt ;
2. il n'y a **rien à afficher à la racine `/`**, faute d'`index.html` dans le dépôt ;
3. ce n'est donc ni une panne Vercel, ni un déploiement supprimé, ni une adresse
   mal recopiée : c'est un dépôt déployé sans page d'accueil.

Vérification complémentaire : `gh api repos/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple/git/trees/main?recursive=1`
ne renvoie qu'un seul fichier `.html` (`outils/reglages_depot.html`) et **aucun `index.html`**.

## 3. Deux causes distinctes, à ne pas confondre

| # | Cause | Effet observé | Correctif |
|---|---|---|---|
| 1 | **Aucun `index.html` à la racine du dépôt déployé** | `/` → `404 NOT_FOUND` (code générique : le chemin demandé n'existe pas dans le déploiement) | Fournir une page d'accueil (`index.html`) ou un dossier de sortie qui en contient une |
| 2 | **Protection des déploiements activée** (Vercel Authentication, active par défaut sur les nouveaux projets) | Un visiteur non connecté à l'équipe voit *« Log in to Vercel »* au lieu du site ; les liens d'aperçu ne sont pas partageables publiquement | Projet → **Security → Deployment Protection → Vercel Authentication : Disabled** (ou « Standard » avec une exception pour l'adresse publique) |

À noter pour lire les codes Vercel : `DEPLOYMENT_NOT_FOUND` signifie que l'adresse ne
correspond à aucun déploiement (déploiement supprimé ou URL erronée) ; `NOT_FOUND` (cas ici)
signifie que le déploiement existe mais que **le chemin demandé n'y existe pas**.

## 4. Correctifs

### A. Pour le projet du simulateur (dépôt `…-par-le-peuple`)

Trois options, de la plus rapide à la plus complète :

1. **Page d'accueil minimale (1 fichier, aucun build)** — déposer un `index.html` à la
   racine de ce dépôt ; le 404 disparaît au déploiement suivant.

   ```html
   <!doctype html>
   <html lang="fr">
   <head>
     <meta charset="utf-8">
     <meta name="viewport" content="width=device-width, initial-scale=1">
     <title>Simulateur macro-politique — Démocratie et politique du peuple</title>
   </head>
   <body>
     <h1>Simulateur macro-politique systémique</h1>
     <p>Modèle gigogne à 5 échelons : 93 leviers croisables, 20 domaines d'impact, données publiques en direct.</p>
     <ul>
       <li><a href="https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple">Code et documentation du projet</a></li>
       <li><a href="https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple/blob/main/docs/SIMULATEUR_PARAMETRABLE.md">Guide du simulateur paramétrable</a></li>
     </ul>
   </body>
   </html>
   ```

2. **Page du simulateur générée au build** — le simulateur produit son HTML dans
   `simulateur/interface.py` (constante `HTML_PAGE`). Un script d'export (à ajouter dans
   ce dépôt) peut écrire `public/index.html`, puis dans **Project Settings → Build & Development Settings** :
   *Build Command* = ce script, *Output Directory* = `public`, *Framework Preset* = `Other`.
   Attention : Vercel héberge des fichiers statiques ; le simulateur est un programme Python
   (serveur local `simulateur/dashboard.py`, route `POST /api/donnees`) qui ne s'exécute pas
   tel quel sur Vercel. La page s'afficherait, mais les fonctions serveur resteraient indisponibles.

3. **Ne pas héberger le simulateur sur Vercel** — c'est la conclusion déjà écrite dans ce
   dépôt (`NOTE_POUR_CLAUDE.md`, `outils/details_depot.html` : « laisser vide : l'ancienne
   adresse Vercel renvoie 404 »). Dans ce cas, supprimer le projet Vercel ou retirer le champ
   *Website* du dépôt évite de partager une adresse qui ne peut pas fonctionner.

### A bis. Depuis l'intégration du simulateur au site M.R.S.C

Le site M.R.S.C embarque désormais le moteur du simulateur (copie datée dans `simulateur/`), sa page publiée (`simulateur/index.html`) et les fonctions `api/*.py` qui exposent ses 16 routes — voir `docs/integration-simulateur.md`. Conséquence pratique pour l'ancien projet : au lieu de bricoler une page d'accueil dans le dépôt du simulateur, il suffit de publier **ce** dépôt sur Vercel (l'outil y est complet et interactif), et de retirer du dépôt du simulateur le champ *Website* qui pointe vers l'adresse 404 — ou de le faire pointer vers la page du simulateur du site.

### B. Pour publier le site M.R.S.C sur Vercel (dépôt MRSC, celui-ci)

Le présent dépôt est un site statique dont `index.html` est bien à la racine : il s'affiche
sans configuration. Marche à suivre :

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

L'accès au tableau de bord Vercel (projet et équipe `mrsc1`) requiert une authentification ;
les constats ci-dessus reposent donc sur des réponses HTTP publiques, sur les messages du bot
Vercel dans GitHub et sur le contenu des dépôts. Les réglages exacts du projet (Build Command,
Output Directory, Deployment Protection) sont à confirmer écran par écran :
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
