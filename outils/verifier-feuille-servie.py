#!/usr/bin/env python3
"""Compare la feuille de style réellement servie à celle du dépôt.

Le 5 novembre 2026, le panneau du menu avait reçu l'habillage de
« Personnalisation » dans `assets/css/site.css`, et la porte de vérification
était verte. Le site publié, lui, servait encore l'ancienne feuille : quatre
déploiements GitHub Pages consécutifs avaient échoué à l'étape `deploy-pages`.
Tous les fichiers répondaient 200, tous les contrôles hors ligne passaient, et
le rendu vu par la personne restait celui d'avant la correction. Un contrôle
qui ne lit que des en-têtes ne peut pas voir une feuille périmée : il faut lire
les octets.

Ce contrôle **télécharge** la feuille servie et la compare, octet par octet, à
celle du dépôt. Il ne juge ni le rendu ni la qualité du CSS : il dit seulement
si ce que le navigateur peut charger est bien ce que la source contient. Une
divergence signifie une publication en retard (déploiement échoué) ou un cache
qui n'a pas encore été renouvelé — pas un défaut de la feuille elle-même.

L'adresse porte l'empreinte de la feuille locale en paramètre, pour ne pas
recevoir une réponse mise en cache par un intermédiaire, et la requête demande
un encodage `identity`. Les essais sont espacés : juste après un déploiement,
un CDN peut servir l'ancienne copie pendant quelques secondes.

Usage :
    python3 outils/verifier-feuille-servie.py --base-url https://exemple.github.io/MRSC/
    python3 outils/verifier-feuille-servie.py --base-url http://127.0.0.1:8000/ --tentatives 1

Codes de sortie :
    0  la feuille servie est identique à celle du dépôt ;
    1  elle diverge : les corrections de la source ne sont pas publiées ;
    2  relevé impossible (source absente, réseau ou encodage illisible) :
       aucun verdict n'est avancé, en particulier pas « identique ».

    `MRSC_RACINE` permet au banc de travailler sur une copie jetable.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
FEUILLE_LOCALE = RACINE / "assets" / "css" / "site.css"
CHEMIN_PUBLIE = "assets/css/site.css"

ENTETES_REQUETE = {
    "User-Agent": "MRSC-verifier-feuille-servie/1",
    # Sans `identity`, un hébergeur compresse la réponse et les octets lus ne
    # sont plus ceux du fichier : la comparaison accuserait une divergence qui
    # n'existe pas.
    "Accept-Encoding": "identity",
    "Cache-Control": "no-cache",
}


def empreinte(octets: bytes) -> str:
    """Empreinte courte, la même convention que `versionner-css-ia.py`."""
    return hashlib.sha256(octets).hexdigest()[:16]


def construire_url(base: str, chemin: str, version: str) -> str:
    if not base.endswith("/"):
        base += "/"
    return f"{base}{chemin}?v={urllib.parse.quote(version)}"


def decoder(octets: bytes, encodage: str) -> tuple[bytes | None, str]:
    """Décompresse au besoin ; un encodage inconnu n'est pas deviné."""
    encodage = (encodage or "").strip().lower()
    if encodage in ("", "identity"):
        return octets, ""
    try:
        if encodage == "gzip":
            return gzip.decompress(octets), ""
        if encodage == "deflate":
            return zlib.decompress(octets), ""
    except (OSError, zlib.error) as erreur:
        return None, f"encodage « {encodage} » illisible ({erreur})"
    return None, f"encodage « {encodage} » non géré : la réponse n'est pas lue"


def relever(url: str) -> tuple[str, bytes | None, str]:
    """Un essai : (verdict, octets servis, détail). Verdict : ok / absent / erreur."""
    requete = urllib.request.Request(url, method="GET", headers=ENTETES_REQUETE)
    try:
        with urllib.request.urlopen(requete, timeout=20) as reponse:
            octets, erreur = decoder(
                reponse.read(), reponse.headers.get("Content-Encoding", "")
            )
            if octets is None:
                return "erreur", None, erreur
            return "ok", octets, f"HTTP {reponse.status}"
    except urllib.error.HTTPError as erreur:
        # Un 404 ne se corrige pas en attendant : `comparer` ne réessaie pas.
        return ("absent" if 400 <= erreur.code < 500 else "erreur"), None, f"HTTP {erreur.code}"
    except (urllib.error.URLError, OSError) as erreur:
        return "erreur", None, str(erreur) or "aucune réponse"


def comparer(base: str, tentatives: int, attente: float) -> int:
    if not FEUILLE_LOCALE.is_file():
        print(
            f"Relevé impossible : {FEUILLE_LOCALE.relative_to(RACINE)} est absente — "
            "on ne peut pas comparer une feuille servie à une source qu'on n'a pas lue.",
            file=sys.stderr,
        )
        return 2
    source = FEUILLE_LOCALE.read_bytes()
    local = empreinte(source)
    url = construire_url(base, CHEMIN_PUBLIE, local)

    verdict = "erreur"
    servie: bytes | None = None
    detail = ""
    for essai in range(1, max(1, tentatives) + 1):
        verdict, servie, detail = relever(url)
        if verdict == "ok" and servie == source:
            break
        if verdict == "absent":
            break
        if essai < tentatives:
            time.sleep(attente)

    print(f"# Feuille de style servie — {base}\n")
    print("| | Empreinte | Octets |")
    print("| --- | --- | ---: |")
    print(f"| Source (`{CHEMIN_PUBLIE}`) | `{local}` | {len(source):,} |".replace(",", " "))
    if servie is None:
        print("| Servie | — | — |")
    else:
        print(f"| Servie | `{empreinte(servie)}` | {len(servie):,} |".replace(",", " "))

    if verdict != "ok" or servie is None:
        print(
            f"\nRelevé impossible ({detail}) : aucune comparaison n'a pu être faite. "
            "Ce n'est ni une conformité ni une divergence ; relancer quand le site répond.",
            file=sys.stderr,
        )
        return 2
    if servie != source:
        premiere_difference = next(
            (i for i, (a, b) in enumerate(zip(servie, source)) if a != b),
            min(len(servie), len(source)),
        )
        print(
            f"\nLa feuille servie **diverge** de la source : `{empreinte(servie)}` "
            f"au lieu de `{local}`, premier octet différent à {premiere_difference}. "
            "Les corrections de `site.css` (par exemple l'habillage commun du menu et "
            "de « Personnalisation ») ne sont pas dans ce que le navigateur charge : "
            "vérifier le déploiement GitHub Pages, puis le renouvellement du cache.",
            file=sys.stderr,
        )
        return 1
    print("\nFeuille servie identique à la source : le rendu publié peut être lu comme le code.")
    return 0


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--base-url", required=True, help="Racine publique du site, terminée par /")
    analyseur.add_argument("--tentatives", type=int, default=1, help="Nombre d’essais si la feuille diverge (défaut : 1)")
    analyseur.add_argument("--attente", type=float, default=10.0, help="Secondes entre deux essais (défaut : 10)")
    options = analyseur.parse_args()
    return comparer(options.base_url, options.tentatives, options.attente)


if __name__ == "__main__":
    sys.exit(main())
