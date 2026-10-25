# M.R.S.C — site public

> **Adresse actuellement publiée par GitHub Pages : [https://thejmimiia-code.github.io/MRSC/](https://thejmimiia-code.github.io/MRSC/).** Le domaine personnalisé souhaité, `www.mrsc.fr`, n’est pas encore configuré dans GitHub Pages. Lors de son raccordement, conserver `www.mrsc.fr` dans la barre d’adresse, sans redirection vers `github.io`, puis mettre à jour les canoniques et les consignes d’attribution après vérification du DNS et du HTTPS. Les changements de cette branche seront visibles après intégration à `main` et publication.

Reproduction statique des pages publiques de [www.mrsc.fr](https://www.mrsc.fr/) pour servir de base aux travaux de R&D, complétée par un outil citoyen : le simulateur macro-politique.

## Périmètre des contenus

Les références physiques, portraits, biographies et travaux personnels du personnage sont exclus de ce dépôt et de la publication du site associatif. Le prototype visuel correspondant a été retiré. La page `eva.html` conserve uniquement la présentation générale de la recherche en IA, sans portrait ni description physique.

Ce retrait de l’arbre courant **n’efface pas l’historique, les anciennes PR ou les versions étiquetées**. Le dépôt doit rester privé jusqu’à une purge distincte de ces emplacements. Le contrôle `python3 outils/verifier-separation-contenus.py` bloque le retour des chemins connus ; il ne constitue pas un détecteur universel de données sensibles.

## Pages

- `index.html` — accueil recentré sur la mission du M.R.S.C, les expériences de chacun, les apprentissages, le débat, les outils citoyens, les documents et le partage
- `apprendre.html` — parcours d’apprentissage accessibles, repères par matière et difficulté, fiches autonomes et sources sans compte
- `anglais-aventure.html` — « Les Mondes » : atlas des 85 fiches dans 15 domaines, parcours libres, plus cinq Escales d’anglais en 3D ; 59 prototypes restent à relire
- `ia-societe.html` — réflexion sur les usages, effets sociaux et fraudes ; réflexes de vérification et liens vers les fiches pratiques
- `simulateur.html` — présentation du simulateur macro-politique, accès à la version interactive publiée sur Vercel et aperçu intégré lorsqu’il est disponible
- `documents.html` — statuts, parution au Journal officiel, bulletins d’adhésion et de don
- `liens-utiles.html` — ressources externes référencées sur le site d’origine
- `localisation.html` — carte Google My Maps et repères affichés
- `nous-contacter.html` — coordonnées de contact
- `transparence.html` — projet, méthode, boucle de R&D continue, registre des sources page par page et licence d’utilisation
- `confidentialite.html` — information publique sur les préférences locales, les contacts, l’hébergement et les services tiers
- `404.html` — page d’erreur servie par les hébergeurs pour toute adresse inconnue

Le dépôt fournit également un [plan de site XML](sitemap.xml) et une veille éditoriale planifiée. Les consignes pour tous les agents sont dans [`AGENTS.md`](AGENTS.md), leurs cartes de compétences dans [`.agents/skills/`](.agents/skills/), le cycle complet dans [`docs/rd-innovation-continue.md`](docs/rd-innovation-continue.md), le [plan global de consolidation et d’optimisation](docs/rd-plan-global-consolidation.md) et les initiatives reprenables dans [`docs/rd/portefeuille.toml`](docs/rd/portefeuille.toml). `outils/verifier-rd-continue.py` vérifie hors ligne la structure de ce dispositif et signale les revues échues; la veille GitHub est planifiée chaque semaine. Ces automatisations ne parcourent pas le Web, ne certifient pas les sources et ne publient pas de savoir à la place de relectures humaines. Les recherches du jeu et ses limites sont dans [`docs/rd-anglais-aventure.md`](docs/rd-anglais-aventure.md); les données personnelles et réserves juridiques, dans [`docs/rd-confidentialite-rgpd.md`](docs/rd-confidentialite-rgpd.md).

La mise en page est responsive, le menu s’adapte aux écrans étroits et des commandes précédent/suivant, accueil et dernière vue rejouent le parcours interne dans l’onglet, avec repli sur la navigation du navigateur si le stockage est bloqué. La suite des pages est conservée dans `sessionStorage` sans paramètres de requête ni données saisies ; la notice publique en détaille la portée. Le panneau « Affichage » propose cinq tailles de texte, un contraste renforcé et l’espacement du texte ; le panneau « Présentation » propose six compositions par intention — Équilibrée, Lecture, Vitrine, Mosaïque, Panorama composite et Compacte — avec un mini-aperçu de chacune (voir [`docs/rd/presentations-personnalisees.md`](docs/rd/presentations-personnalisees.md)). Ces préférences restent locales et ne remplacent pas le zoom du navigateur. Les règles communes de boutons, cartes, palette et de statut des contenus sont décrites dans [`docs/rd-coherence-visuelle-editoriale.md`](docs/rd-coherence-visuelle-editoriale.md) ; la R&D et la matrice d’essais multi-écrans figurent dans [`docs/rd-affichage-adaptatif.md`](docs/rd-affichage-adaptatif.md). La recherche sur les apprentissages figure dans `docs/rd-parcours-apprentissage.md` ; la veille sur l’IA et les fraudes, dans [`docs/rd-ia-usages-fraudes.md`](docs/rd-ia-usages-fraudes.md) ; `docs/pistes-visuelles-ia.html` présente trois directions graphiques exploratoires, hors navigation publique.

## R&D continue et travail entre agents

Les consignes partagées de tout agent résident dans [`AGENTS.md`](AGENTS.md). Tout contenu public nouveau ou révisé suit le [`protocole éditorial commun`](docs/protocole-editorial.md) et son [gabarit réutilisable](docs/gabarits/contenu-editorial.md) ; ce cadre guide la méthode sans certifier les contenus existants. La bibliothèque de skills propose des méthodes de cadrage, analyse, débogage, tests, documentation, recherche des sources, pédagogie, game design, direction artistique, accessibilité, intégration sécurisée et maintenance ; son [index](.agents/skills/README.md) route chaque besoin vers les cartes pertinentes. Le [manuel de R&D continue](docs/rd-innovation-continue.md) explique le cycle complet; le [portefeuille](docs/rd/portefeuille.toml) permet de reprendre une initiative par sa question, son état, ses preuves, ses critères et sa prochaine action; le [journal de passation](docs/rd/journal.md) garde les décisions structurantes d'une session à l'autre. Le [protocole d'essais d'usage](docs/rd/protocole-essais-usage.md) prépare les tests sans prétendre qu'ils ont déjà eu lieu ; la [file de relecture](docs/apprentissage/file-relecture.md), générée par `python3 outils/file-relecture.py`, range les 55 prototypes pour organiser leurs relectures sans les valider. La [note de prospective](docs/rd/prospective-2027-2030.md) est complétée par une [veille externe datée](docs/rd/veille-2026-10-17.md) et par un [brief de décision](docs/rd/decision-prospective.md) soumis à l'association ; `python3 outils/etat-rd.py` imprime l'état vérifiable correspondant. Le [relevé d'accessibilité du 17 octobre 2026](docs/rd/accessibilite-2026-10-17.md) consigne des balayages axe-core locaux, leurs corrections et leurs limites : ce n'est ni un audit ni une conformité. `node outils/verifier-accessibilite.cjs` les rejoue (dépendances installées hors dépôt, commandes en tête du script). Une proposition peut être déposée via le formulaire GitHub dédié, sans données personnelles.

Les vérifications se lancent localement avec `python3 outils/verifier-rd-continue.py`. Le workflow GitHub de veille s’exécute chaque semaine, vérifie aussi les fiches et les liens internes, et signale les dates de revue. La CI contrôle le dispositif sur les pull requests; la publication contrôle ses règles. Ces automations ne font pas de recherche externe, n’authentifient pas le savoir et n’approuvent pas une fiche : l’expertise, les droits, les essais d’usage et l’accord de publication doivent rester des étapes humaines. La cible est d’élargir une carte plurielle et traçable, jamais de prétendre intégrer littéralement tout le savoir du monde.

## Le simulateur macro-politique

Le site intègre le **simulateur macro-politique systémique** du projet *Démocratie et politique, du peuple, pour le peuple, par le peuple* : 5 échelons (local → national → européen → mondial → géopolitique), plus de 100 leviers de politique publique, 20 domaines d’impact notés de 0 à 100, 52 indicateurs de contexte sourcés, une console de veille des seuils tolérables et des exports JSON/CSV.

| Élément | Rôle |
|---|---|
| `simulateur/` | Moteur embarqué (Python), copié depuis son dépôt d’origine — voir `simulateur/PROVENANCE.json` |
| `simulateur/index.html` | Page publiée du simulateur, **générée** depuis le moteur ; le générateur ajoute le retour permanent vers le site, les commandes de parcours et les réglages d’affichage |
| `api/*.py` | Fonctions serveur exposant les 16 routes du moteur (`/api/catalogue`, `/api/simuler`, `/api/bulles`, `/api/garde_fous`…) |
| `simulateur/pont_api.py` | Pont entre les routes déclarées et le gestionnaire HTTP du moteur (ajout propre au site) |
| `simulateur.html` | Page du site : présentation, limites assumées, aperçu embarqué |
| `outils/verifier-integration.py` | Vérifie la page, les fonctions et chaque route, sans navigateur |
| `outils/verifier-securite.py` | Tests HTTP/WSGI, bornes de requête et de sources, calculs concurrents, redirections, provenance/XSS, cache et whitelist statique |

Le site embarque une copie datée du moteur amont et applique un **correctif local de sécurité et d’intégration accessible**, conservé dans `outils/patchs/simulateur-securite-mrsc.patch`. Les scénarios et préréglages du simulateur local sont de vrais boutons utilisables au clavier, avec état annoncé. Le script de mise à jour réapplique le correctif avant de régénérer la page ; il doit être revu à chaque évolution amont. Il ne modifie pas le service publié dans l’autre dépôt.

```sh
python3 outils/mettre-a-jour-simulateur.py  # rapatrie le moteur amont et régénère la page
python3 outils/construire-simulateur.py     # régénère simulateur/index.html depuis le moteur
python3 outils/generer-fonctions-api.py     # (re)génère les fonctions api/*.py
python3 outils/verifier-securite.py         # tests ciblés HTTP/WSGI, cache, source et whitelist
python3 outils/verifier-integration.py      # contrôle l’ensemble
```

**Deux sources, une seule page.** Le dépôt amont identifie maintenant [Vercel](https://d-mocratie-et-politique-du-peuple-p.vercel.app/) comme adresse publique du simulateur ; sa branche `main` contient une page `index.html` et une fonction API, et GitHub a signalé un déploiement *Production* réussi le 14 octobre 2026 ([PR amont #53](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple/pull/53)). Ces éléments ne constituent pas un test HTTP de l’adresse, de ses API ou de l’intégration dans un cadre. La page `simulateur.html` pointe désormais vers cette adresse, et la sonde autorise cet hôte. L’ancien hôte Render reste accepté par la sonde pour compatibilité, mais n’est plus la cible par défaut. Sur GitHub Pages, qui n’exécute pas Python, la page propose un lien direct vers Vercel plutôt qu’un faux aperçu fonctionnel.

```sh
python3 outils/verifier-source-distante.py  # contrôle la source configurée et son API (0 = oui)
python3 outils/verifier-maj-amont.py        # le moteur embarqué a-t-il pris du retard ? (1 = oui)
```

Une veille hebdomadaire (`.github/workflows/maj-simulateur.yml`) échoue — et prévient par courriel — quand le moteur amont a bougé ; elle ne publie jamais rien à votre place. Les actions de workflow sont épinglées par SHA et `.github/workflows/verification.yml` exécute les contrôles sur les pull requests ; Dependabot surveille les mises à jour d’actions. Pour que le contrôle devienne réellement bloquant, les administrateurs doivent exiger le statut CI dans la protection de `main`. Les consignes de maintenance et de vérification du service amont sont dans [`docs/prompt-session-simulateur.md`](docs/prompt-session-simulateur.md).

Le site et sa copie embarquée peuvent être testés avec les fonctions Python sur Vercel ou en local. Sur l’adresse GitHub Pages, utilisez le lien Vercel affiché dans la page du simulateur. Le détail de l’architecture, de la mise à jour et du dépannage est dans [`docs/integration-simulateur.md`](docs/integration-simulateur.md) ; l’audit sécurité, ses limites et la feuille de route sont dans [`docs/rd-audit-securite-optimisation.md`](docs/rd-audit-securite-optimisation.md).

## Poids des pages, images et sobriété

Trois grandes illustrations disposent désormais de variantes AVIF et WebP en deux largeurs (et 1 200 px pour l’atlas), servies par `<picture>` avec un repli JPEG. L’image de secours de la scène 3D n’est chargée que si le rendu WebGL échoue. Une mesure locale reconstruit le poids des 96 pages publiques et applique des budgets de travail ; elle ne remplace ni une mesure réseau, ni un bilan carbone, ni un audit RGESN.

```sh
python3 outils/optimiser-images.py --verifier        # manifeste, empreintes et tailles des variantes
python3 outils/verifier-poids-pages.py              # poids estimé et budgets (99 pages)
python3 outils/verifier-poids-pages.py --rapport docs/rd/poids-pages.md
python3 outils/verifier-publication.py --base-url https://thejmimiia-code.github.io/MRSC/
python3 outils/test_fichiers_servis.py            # tests du relevé d’en-têtes conservé
python3 outils/verifier-fichiers-servis.py        # le relevé daté tient-il encore ? (sans réseau)
```

Le contrôle réseau demande un accès au site publié ; il relève les types MIME, l’encodage et le cache et ne juge ni le rendu ni la performance. Il tourne aussi depuis l’onglet Actions (`Vérifier les en-têtes servis par l’hébergement`), chaque jour et à chaque modification du contrôleur ou de ses cibles ; le tableau est repris dans une issue de suivi unique, réécrite à chaque mesure et laissée ouverte, sans constituer un audit.

Le relevé du 20 octobre 2026 est conservé dans [`docs/rd/en-tetes-servis-2026-10-20.toml`](docs/rd/en-tetes-servis-2026-10-20.toml) et revérifié sans réseau à chaque porte : chaque image et chaque icône doit arriver dans la taille exacte du fichier du dépôt — la version publiée est alors bien celle du dépôt —, et chaque page ou feuille de style doit arriver compressée, donc plus petite que sa version locale. Un binaire modifié depuis la mesure fait échouer le contrôle : c’est le relevé qui est périmé, pas le site, et il faut refaire la mesure. Cette comparaison porte sur des tailles, pas sur des contenus ; la durée de cache de dix minutes est imposée par GitHub Pages et ne se règle pas depuis le dépôt.

La méthode, les chiffres avant/après, les limites et les prochaines vérifications sont dans [`docs/rd/poids-et-sobriete-numerique.md`](docs/rd/poids-et-sobriete-numerique.md). Les essais navigateur du dépôt (`outils/test-experience.cjs`) couvrent aussi le réflow à 320 px et le zoom à 150 %.

## Lancer en local

Depuis la racine du dépôt :

```sh
python3 outils/serveur-local.py --port 4173
```

Puis ouvrir `http://localhost:4173`. Le serveur écoute uniquement sur `127.0.0.1` par défaut, n’expose que les fichiers destinés à la publication, renvoie `404.html` pour le reste et borne les corps `/api/…` à 1 Mio. `/api/…` est relayé au moteur du simulateur (lancé dans le même processus) — l’aperçu local est donc complet, page et données comprises. L’option `--sans-moteur` se contente des fichiers statiques. Pour un accès depuis un autre appareil, ajoutez `--bind 0.0.0.0` en comprenant que cela rend l’aperçu accessible depuis le réseau local.

Évitez de lancer un serveur de fichiers simple à la racine du dépôt : même sans listing, il pourrait rendre accessibles les sources et documents qui ne sont pas dans la publication. Pour un export déjà préparé, servez uniquement le dossier public construit ; pour travailler dans ce dépôt, utilisez `outils/serveur-local.py`.

## Publication sur GitHub Pages

Le workflow `.github/workflows/deploy-pages.yml` valide le HTML, les liens locaux et la syntaxe JavaScript, puis publie les pages HTML (dont `404.html`, `confidentialite.html` et `anglais-aventure.html`), `assets/`, `sitemap.xml`, le catalogue et ses fiches autonomes ainsi que la page du simulateur (`simulateur/index.html` et sa provenance). Les documents de travail dans `docs/`, les outils de `outils/`, les sources Python du moteur et les fonctions `api/` ne sont pas copiés sur le site. Le déploiement est automatique à chaque push sur `main` (un lancement manuel reste possible depuis l’onglet **Actions** avec « Publish M.R.S.C site »). Toute mise à jour de cette branche attend son intégration à `main` et une publication réussie.

**État de la publication au 25 octobre 2026 :** l’adresse `https://thejmimiia-code.github.io/MRSC/` répond `404 — There isn't a GitHub Pages site here`. Le contenu du dépôt n’est pas en cause : `python3 outils/verifier-publication-locale.py` et `python3 outils/verifier-site-statique.py` passent, et `outils/serveur-local.py` sert les 99 pages, `assets/`, les fiches et `/api/…` sans erreur. La chronologie est nette : le contrôle d’en-têtes de 11 h 33 UTC trouvait le site vert, et l’API répond désormais `404 Not Found` sur `/pages` avec `has_pages: false`. Le site Pages a donc été **dépublié dans la journée**, et la republication automatique n’a pas eu lieu. Deux causes côté compte se cumulent :

1. **Actions arrêté par la facturation.** Les quatre runs de `main` du 25 octobre à 18 h 14 n’ont démarré aucun pas, avec l’annotation « The job was not started because recent account payments have failed or your spending limit needs to be increased ». Aucun déploiement n’a donc eu lieu, ni pour rétablir le site, ni pour publier la fusion de la veille. À corriger dans **Settings → Billing & plans** (moyen de paiement ou limite de dépense), puis relancer « Publish M.R.S.C site » depuis l’onglet **Actions**.
2. **Site Pages à recréer.** `GET /repos/thejmimiia-code/MRSC/pages` répond `404 Not Found` et `has_pages` vaut `false`. L’étape `configure-pages` de ce dépôt porte désormais `enablement: true`, qui recrée le site s’il n’existe pas ; sinon, le créer dans **Settings → Pages** avec la source **GitHub Actions**.

Tant que ces deux points ne sont pas traités, l’adresse publique répond 404 : les corriger l’un sans l’autre ne suffit pas. Le contrôle quotidien `.github/workflows/verifier-publication.yml` le signalera chaque jour par un run rouge. Aucune de ces actions n’est exécutable depuis le dépôt : elles relèvent du compte titulaire.

GitHub Pages ne sait pas exécuter Python : la copie embarquée ne calcule pas à cette adresse. Pour utiliser l’outil interactif, ouvrez [la version publiée du simulateur sur Vercel](https://d-mocratie-et-politique-du-peuple-p.vercel.app/).

## Publication du site M.R.S.C sur Vercel (optionnelle)

Cette configuration concerne l’hébergement du **site M.R.S.C** et reste distincte du déploiement Vercel du simulateur amont. Les fonctions Python de `api/` peuvent aussi faire fonctionner la copie embarquée du site si la source distante ne répond pas. Marche à suivre :

1. Vercel → **Add New → Project** → importer `thejmimiia-code/MRSC`.
2. Réglages : *Framework Preset* **Other**, *Build Command* **vide**, *Output Directory* **`.`**, *Install Command* **vide**.
3. Déployer, puis vérifier `/` (accueil), `/simulateur/` (outil) et `/api/scenarios` (JSON).
4. **Security → Deployment Protection → Vercel Authentication : Disabled**, sinon les visiteurs non connectés voient la page de connexion Vercel à la place du site.

Fichiers prévus pour cet hébergement : `vercel.json` (mode statique explicite, en-têtes de sécurité, durée et mémoire des fonctions) et `.vercelignore` (même périmètre de publication que GitHub Pages, `api/` et `simulateur/` compris). Aucune dépendance Python n’est requise : le moteur n’utilise que la bibliothèque standard, et la version Python par défaut de Vercel (3.12) convient.

Un déploiement peut être « Ready » tout en renvoyant `404 NOT_FOUND` sur `/` si aucun `index.html` n’est publié à la racine. Le diagnostic [`docs/diagnostic-404-vercel.md`](docs/diagnostic-404-vercel.md) conserve l’observation initiale, mais le dépôt amont du simulateur contient désormais cette page et GitHub signale une publication *Production* réussie ; le domaine public n’a pas été contrôlé directement depuis ce dépôt.

## Contenu et ressources externes

Le logo du site a été repris localement dans `assets/images/logo-mrsc.jpg`. Les pages existantes et leurs éléments visibles ont été reconstitués à partir du site public ; `ia-societe.html` réunit désormais une première réflexion sur l’IA et un parcours de prévention des fraudes, complété par des fiches d’apprentissage autonomes. Ces contenus sont une première version à relire, non une liste exhaustive. Les statuts et les bulletins d’adhésion et de don sont publiés en copies locales dans `assets/documents/` ; le document de parution au Journal officiel reste un lien externe vers sa source officielle. L’intégration de Google My Maps n’est chargée qu’après une action volontaire ; le lien du Journal officiel ne contacte sa source que si une personne l’ouvre.

Le moteur du simulateur vient du dépôt [thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple) et reste sous licence **MIT** ; sa révision copiée est enregistrée dans `simulateur/PROVENANCE.json`.

## Transparence et licence

Chaque page publique comporte un encadré « Sources & traçabilité » distinguant les sources externes des apports « Original M.R.S.C ». La page `transparence.html` présente le projet, la méthode, le registre des sources page par page et la licence d'utilisation.

L'outil est open-source et gratuit, selon les conditions du fichier [LICENCE](LICENCE). Toute réutilisation impose l'attribution « Source : M.R.S.C — https://thejmimiia-code.github.io/MRSC/ ». Il est interdit de s'en attribuer le mérite ou la paternité ; l'outil reste la propriété intellectuelle exclusive de son créateur, unique auteur.
