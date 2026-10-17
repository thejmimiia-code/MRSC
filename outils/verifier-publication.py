#!/usr/bin/env python3
"""Vérifie ce qu’un hébergement sert réellement pour les fichiers sensibles.

Le script interroge une adresse publique (ou locale) et relève, pour chaque
fichier contrôlé : le code HTTP, le type MIME, l’encodage de transfert et la
politique de cache. Il ne juge ni le rendu, ni la qualité des images, ni la
performance réelle : il constate des en-têtes.

Exemples :
    python3 outils/verifier-publication.py --base-url https://exemple.github.io/MRSC/
    python3 outils/verifier-publication.py --base-url http://127.0.0.1:8000/ --tentatives 1

Sortie : tableau Markdown sur la sortie standard. Code 0 si tous les fichiers
répondent 200, 1 sinon. Un type MIME inattendu est signalé sans faire échouer
le contrôle, car les navigateurs décodent d’après le contenu ; un type faux
reste néanmoins un défaut à corriger côté hébergement.
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
    ("assets/images/accueil-logo-mrsc-3d-800.avif", ("image/avif",), "Logo 800 px, AVIF"),
    ("assets/images/accueil-logo-mrsc-3d-1400.avif", ("image/avif",), "Logo pleine largeur, AVIF"),
    ("assets/images/accueil-logo-mrsc-3d-800.webp", ("image/webp",), "Logo 800 px, WebP"),
    ("assets/images/mondes-savoirs-hero-800.avif", ("image/avif",), "Atlas 800 px, AVIF"),
    ("assets/images/mondes-savoirs-hero-1200.avif", ("image/avif",), "Atlas 1 200 px, AVIF"),
    ("assets/images/mondes-savoirs-hero-1672.avif", ("image/avif",), "Atlas pleine largeur, AVIF"),
    ("assets/images/mondes-savoirs-hero-800.webp", ("image/webp",), "Atlas 800 px, WebP"),
    ("assets/images/escales-anglais-hero-800.avif", ("image/avif",), "Secours de scène 800 px, AVIF"),
    ("assets/images/escales-anglais-hero-800.webp", ("image/webp",), "Secours de scène 800 px, WebP"),
    ("sitemap.xml", ("application/xml", "text/xml"), "Sitemap"),
)


class Resultat:
    def __init__(self, chemin: str, url: str, description: str) -> None:
        self.chemin = chemin
        self.url = url
        self.description = description
        self.statut: int | None = None
        self.type: str = ""
        self.encodage: str = ""
        self.cache: str = ""
        self.erreur: str = ""


def sonder(url: str, tentatives: int, attente: float) -> tuple[int | None, str, str, str, str]:
    derniere_erreur = ""
    for essai in range(1, max(1, tentatives) + 1):
        requete = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "MRSC-verifier-publication/1"})
        try:
            with urllib.request.urlopen(requete, timeout=20) as reponse:
                entetes = reponse.headers
                return (
                    reponse.status,
                    entetes.get_content_type(),
                    entetes.get("Content-Encoding", ""),
                    entetes.get("Cache-Control", ""),
                    "",
                )
        except urllib.error.HTTPError as erreur:
            # Certains hébergeurs refusent HEAD : on retente en GET sans lire le corps.
            if erreur.code in (405, 501):
                try:
                    requete_get = urllib.request.Request(
                        url, method="GET", headers={"User-Agent": "MRSC-verifier-publication/1"}
                    )
                    with urllib.request.urlopen(requete_get, timeout=20) as reponse:
                        reponse.read(1)
                        entetes = reponse.headers
                        return (
                            reponse.status,
                            entetes.get_content_type(),
                            entetes.get("Content-Encoding", ""),
                            entetes.get("Cache-Control", ""),
                            "",
                        )
                except (urllib.error.URLError, OSError) as nouvelle_erreur:
                    derniere_erreur = str(nouvelle_erreur)
            else:
                derniere_erreur = f"HTTP {erreur.code}"
                # Un 404 ne se corrige pas en attendant : inutile de réessayer.
                if erreur.code in (400, 401, 403, 404, 410):
                    return erreur.code, "", "", "", derniere_erreur
        except (urllib.error.URLError, OSError) as erreur:
            derniere_erreur = str(erreur)
        if essai < tentatives:
            time.sleep(attente)
    return None, "", "", "", derniere_erreur or "aucune réponse"


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
        statut, type_mime, encodage, cache, erreur = sonder(url, options.tentatives, options.attente)
        resultat.statut = statut
        resultat.type = type_mime
        resultat.encodage = encodage
        resultat.cache = cache
        resultat.erreur = erreur
        if statut != 200:
            motif = f"HTTP {statut}" if statut else "injoignable"
            detail = f" ({erreur})" if erreur and erreur not in motif else ""
            anomalies.append(f"{resultat.chemin} : {motif}{detail}")
        elif not any(type_mime.startswith(prefixe) for prefixe in types_acceptes):
            anomalies.append(f"{resultat.chemin} : type « {type_mime or 'absent'} » au lieu de {' / '.join(types_acceptes)}")
        resultats.append(resultat)

    print(f"# En-têtes servis pour {options.base_url}\n")
    print("| Fichier | Rôle | Statut | Type MIME | Encodage | Cache |")
    print("| --- | --- | ---: | --- | --- | --- |")
    for resultat in resultats:
        statut = str(resultat.statut) if resultat.statut else "—"
        type_mime = resultat.type or "—"
        print(
            f"| `{resultat.chemin}` | {resultat.description} | {statut} | "
            f"{type_mime} | {resultat.encodage or '—'} | {resultat.cache or '—'} |"
        )

    manquants = [a for a in anomalies if "injoignable" in a or "HTTP" in a]
    types_inattendus = [a for a in anomalies if a not in manquants]
    if types_inattendus:
        print("\nTypes inattendus (à corriger côté hébergement, sans bloquer ici) :")
        for anomalie in types_inattendus:
            print(f"- {anomalie}")
    if manquants:
        print("\nFichiers manquants ou injoignables :", file=sys.stderr)
        for anomalie in manquants:
            print(f"- {anomalie}", file=sys.stderr)
        return 1
    print(f"\n{len(resultats)} fichiers contrôlés : tous répondent 200.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
