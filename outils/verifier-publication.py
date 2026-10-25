#!/usr/bin/env python3
"""Vérifie ce qu’un hébergement sert réellement pour les fichiers sensibles.

Le script interroge une adresse publique (ou locale) et relève, pour chaque
fichier contrôlé : le code HTTP, le type MIME, l’encodage de transfert et la
politique de cache. Il ne juge ni le rendu, ni la qualité des images, ni la
performance réelle : il constate des en-têtes.

Il envoie un en-tête Accept-Encoding (gzip, deflate, br) : sans lui, un hébergeur
ne compresse pas et le contrôle conclurait à tort à l’absence de compression.
Les octets relevés sont ceux annoncés par Content-Length, c’est-à-dire la taille
transférée quand une compression est appliquée.

Il vérifie aussi le **périmètre** : les documents de travail, les outils et les
sources du moteur ne doivent jamais être servis. Le 25 octobre 2026, une
publication GitHub Pages configurée « depuis une branche » a servi la racine
entière du dépôt (`README.md`, `AGENTS.md`, `outils/`, `docs/`…) : tous les
fichiers attendus répondaient 200, donc ce contrôle passait au vert alors que le
site publiait ce qu’il devait cacher. Une réponse 200 sur un chemin de
`HORS_PERIMETRE` fait désormais échouer le contrôle.

Exemples :
    python3 outils/verifier-publication.py --base-url https://exemple.github.io/MRSC/
    python3 outils/verifier-publication.py --base-url http://127.0.0.1:8000/ --tentatives 1

Sortie : tableaux Markdown sur la sortie standard. Code 0 si tous les fichiers
du périmètre répondent 200 et si aucun fichier hors périmètre n’est servi,
1 sinon. Un type MIME inattendu est signalé sans faire échouer le contrôle,
car les navigateurs décodent d’après le contenu ; un type faux reste néanmoins
un défaut à corriger côté hébergement.
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# (chemin, préfixes de type MIME acceptés, description)
CIBLES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("", ("text/html",), "Accueil"),
    ("apprendre.html", ("text/html",), "Catalogue et Boussole"),
    ("anglais-aventure.html", ("text/html",), "Atlas Les Mondes"),
    ("transparence.html", ("text/html",), "Transparence et sobriété"),
    ("assets/css/site.css", ("text/css",), "Feuille de style principale"),
    ("assets/css/anglais-aventure.css", ("text/css",), "Styles de l’atlas"),
    ("assets/js/site.js", ("javascript", "text/javascript", "application/javascript"), "Script principal"),
    ("assets/js/anglais-aventure.js", ("javascript", "text/javascript", "application/javascript"), "Script de l’atlas"),
    ("assets/images/mondes-savoirs-hero-800.avif", ("image/avif",), "Atlas 800 px, AVIF"),
    ("assets/images/mondes-savoirs-hero-1200.avif", ("image/avif",), "Atlas 1 200 px, AVIF"),
    ("assets/images/mondes-savoirs-hero-1672.avif", ("image/avif",), "Atlas pleine largeur, AVIF"),
    ("assets/images/mondes-savoirs-hero-800.webp", ("image/webp",), "Atlas 800 px, WebP"),
    ("assets/images/escales-anglais-hero-800.avif", ("image/avif",), "Secours de scène 800 px, AVIF"),
    ("assets/images/escales-anglais-hero-800.webp", ("image/webp",), "Secours de scène 800 px, WebP"),
    ("favicon.ico", ("image/x-icon", "image/vnd.microsoft.icon", "application/octet-stream"), "Favicon"),
    ("assets/images/favicon-32.png", ("image/png",), "Icône 32 px"),
    ("assets/images/favicon-192.png", ("image/png",), "Icône 192 px"),
    ("assets/images/apple-touch-icon.png", ("image/png",), "Icône Apple Touch"),
    ("llms.txt", ("text/plain",), "Sommaire pour lecteurs automatiques"),
    ("sitemap.xml", ("application/xml", "text/xml"), "Sitemap"),
)

#: Chemins qui ne doivent **jamais** être servis par l’hébergement public.
#: Leur présence signifie que la racine du dépôt est publiée au lieu du seul
#: artefact préparé par `.github/workflows/deploy-pages.yml` — c’est le cas
#: d’une source Pages « Deploy from a branch », qui sert tout le dépôt.
#: (chemin, description)
HORS_PERIMETRE: tuple[tuple[str, str], ...] = (
    ("README.md", "Documentation de développement"),
    ("AGENTS.md", "Consignes internes des agents"),
    ("LICENCE", "Licence du dépôt"),
    ("docs/protocole-editorial.md", "Protocole éditorial interne"),
    ("docs/rd/journal.md", "Journal de R&D et de passation"),
    ("outils/serveur-local.py", "Outil de développement"),
    ("api/simuler.py", "Fonction serveur Python du moteur"),
)


ENTETES_REQUETE = {
    "User-Agent": "MRSC-verifier-publication/1",
    # Sans cet en-tête, un hébergeur ne compresse pas et le contrôle conclurait
    # à tort à l’absence de compression.
    "Accept-Encoding": "gzip, deflate, br",
}


class Resultat:
    def __init__(self, chemin: str, url: str, description: str) -> None:
        self.chemin = chemin
        self.url = url
        self.description = description
        self.statut: int | None = None
        self.type: str = ""
        self.encodage: str = ""
        self.cache: str = ""
        self.octets: int | None = None
        self.erreur: str = ""


def _releve(entetes, statut: int) -> tuple[int, str, str, str, str, int | None]:
    longueur = entetes.get("Content-Length", "")
    try:
        octets = int(longueur) if longueur.strip() else None
    except ValueError:
        octets = None
    return (
        statut,
        entetes.get_content_type(),
        entetes.get("Content-Encoding", ""),
        entetes.get("Cache-Control", ""),
        "",
        octets,
    )


def sonder(url: str, tentatives: int, attente: float) -> tuple[int | None, str, str, str, str, int | None]:
    derniere_erreur = ""
    for essai in range(1, max(1, tentatives) + 1):
        requete = urllib.request.Request(url, method="HEAD", headers=ENTETES_REQUETE)
        try:
            with urllib.request.urlopen(requete, timeout=20) as reponse:
                return _releve(reponse.headers, reponse.status)
        except urllib.error.HTTPError as erreur:
            # Certains hébergeurs refusent HEAD : on retente en GET sans lire le corps.
            if erreur.code in (405, 501):
                try:
                    requete_get = urllib.request.Request(url, method="GET", headers=ENTETES_REQUETE)
                    with urllib.request.urlopen(requete_get, timeout=20) as reponse:
                        reponse.read(1)
                        return _releve(reponse.headers, reponse.status)
                except (urllib.error.URLError, OSError) as nouvelle_erreur:
                    derniere_erreur = str(nouvelle_erreur)
            else:
                derniere_erreur = f"HTTP {erreur.code}"
                # Un 404 ne se corrige pas en attendant : inutile de réessayer.
                if erreur.code in (400, 401, 403, 404, 410):
                    return erreur.code, "", "", "", derniere_erreur, None
        except (urllib.error.URLError, OSError) as erreur:
            derniere_erreur = str(erreur)
        if essai < tentatives:
            time.sleep(attente)
    return None, "", "", "", derniere_erreur or "aucune réponse", None


def construire_url(base: str, chemin: str) -> str:
    if not base.endswith("/"):
        base += "/"
    return base + chemin


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--base-url", required=True, help="Racine publique du site, terminée par /")
    analyseur.add_argument("--tentatives", type=int, default=1, help="Nombre d’essais par fichier (défaut : 1)")
    analyseur.add_argument("--attente", type=float, default=10.0, help="Secondes entre deux essais (défaut : 10)")
    options = analyseur.parse_args()

    resultats: list[Resultat] = []
    anomalies: list[str] = []
    for chemin, types_acceptes, description in CIBLES:
        url = construire_url(options.base_url, chemin)
        resultat = Resultat(chemin or "/", url, description)
        statut, type_mime, encodage, cache, erreur, octets = sonder(url, options.tentatives, options.attente)
        resultat.statut = statut
        resultat.type = type_mime
        resultat.encodage = encodage
        resultat.cache = cache
        resultat.octets = octets
        resultat.erreur = erreur
        if statut != 200:
            motif = f"HTTP {statut}" if statut else "injoignable"
            detail = f" ({erreur})" if erreur and erreur not in motif else ""
            anomalies.append(f"{resultat.chemin} : {motif}{detail}")
        elif not any(type_mime.startswith(prefixe) for prefixe in types_acceptes):
            anomalies.append(f"{resultat.chemin} : type « {type_mime or 'absent'} » au lieu de {' / '.join(types_acceptes)}")
        resultats.append(resultat)

    print(f"# En-têtes servis pour {options.base_url}\n")
    print("| Fichier | Rôle | Statut | Type MIME | Encodage | Octets servis | Cache |")
    print("| --- | --- | ---: | --- | --- | ---: | --- |")
    for resultat in resultats:
        statut = str(resultat.statut) if resultat.statut else "—"
        type_mime = resultat.type or "—"
        octets = f"{resultat.octets:,}".replace(",", " ") if resultat.octets is not None else "—"
        print(
            f"| `{resultat.chemin}` | {resultat.description} | {statut} | "
            f"{type_mime} | {resultat.encodage or '—'} | {octets} | {resultat.cache or '—'} |"
        )

    manquants = [a for a in anomalies if "injoignable" in a or "HTTP" in a]
    types_inattendus = [a for a in anomalies if a not in manquants]

    # ── Périmètre : ce qui ne doit pas être servi ──────────────────────────
    fuites: list[str] = []
    indetermines: list[str] = []
    print("\n## Hors périmètre de publication (attendu : 404)\n")
    print("| Chemin | Rôle | Statut | Verdict |")
    print("| --- | --- | ---: | --- |")
    for chemin, description in HORS_PERIMETRE:
        url = construire_url(options.base_url, chemin)
        statut, _, _, _, erreur, _ = sonder(url, options.tentatives, options.attente)
        statut_affiche = str(statut) if statut else "—"
        if statut == 200:
            verdict = "**SERVI — fuite**"
            fuites.append(f"{chemin} : servi en 200, alors qu’il ne doit pas être publié")
        elif statut in (401, 403, 404, 410):
            verdict = "absent, conforme"
        else:
            # Réseau coupé ou statut imprévu : ce n’est pas une fuite prouvée,
            # mais le périmètre reste non vérifié — donc le contrôle échoue.
            detail = f" ({erreur})" if erreur else ""
            verdict = f"non vérifiable{detail}"
            indetermines.append(f"{chemin} : statut {statut_affiche}, périmètre non vérifiable{detail}")
        print(f"| `{chemin}` | {description} | {statut_affiche} | {verdict} |")
    if types_inattendus:
        print("\nTypes inattendus (à corriger côté hébergement, sans bloquer ici) :")
        for anomalie in types_inattendus:
            print(f"- {anomalie}")
    if manquants:
        print("\nFichiers manquants ou injoignables :", file=sys.stderr)
        for anomalie in manquants:
            print(f"- {anomalie}", file=sys.stderr)
    if fuites:
        print("\nPérimètre de publication violé :", file=sys.stderr)
        for fuite in fuites:
            print(f"- {fuite}", file=sys.stderr)
        print(
            "  Vérifier la source Pages : elle doit être « GitHub Actions » et publier l’artefact "
            "`_site` produit par `.github/workflows/deploy-pages.yml`, jamais la racine du dépôt. "
            "Détail dans la section « Publication sur GitHub Pages » du README.",
            file=sys.stderr,
        )
    if indetermines:
        print("\nPérimètre non vérifié (ni fuite prouvée, ni conformité) :", file=sys.stderr)
        for indetermine in indetermines:
            print(f"- {indetermine}", file=sys.stderr)
        print("  Relancer quand l’hébergement répond, ou vérifier l’adresse de base.", file=sys.stderr)
    if manquants or fuites or indetermines:
        return 1
    compressés = sum(1 for resultat in resultats if resultat.encodage)
    print(f"\n{len(resultats)} fichiers contrôlés : tous répondent 200.")
    print(
        f"{len(HORS_PERIMETRE)} chemins internes contrôlés : aucun n’est servi "
        "(documents de travail, outils et sources du moteur restent hors du site)."
    )
    if compressés:
        print(f"Compression de transfert annoncée par l’hébergeur pour {compressés} fichier(s).")
    else:
        print(
            "Aucune compression de transfert annoncée, malgré l’en-tête Accept-Encoding envoyé : "
            "le serveur a répondu sans Content-Encoding."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
