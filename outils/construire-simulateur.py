#!/usr/bin/env python3
"""Génère `simulateur/index.html`, la page du simulateur, à partir du moteur.

Le moteur sert sa page depuis la constante `HTML_PAGE` de
`simulateur/interface.py`, en remplaçant le repère `===SCENARIOS_JSON===` par
le catalogue des scénarios (`simulateur/dashboard.py`). Ce script fait
exactement la même substitution, mais une fois pour toutes : la page devient
un fichier statique publiable (Vercel, GitHub Pages), sans build à chaque
requête.

Usage :
    python3 outils/construire-simulateur.py [--verifier]

`--verifier` ne réécrit rien : il signale si le fichier publié a divergé du
moteur (utilisable en CI, ou après une mise à jour du moteur).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from simulateur.dashboard import SCENARIOS  # noqa: E402
from simulateur.interface import HTML_PAGE  # noqa: E402

SORTIE = RACINE / "simulateur" / "index.html"
PROVENANCE = RACINE / "simulateur" / "PROVENANCE.json"
REPERE = "===SCENARIOS_JSON==="


def provenance() -> dict[str, str]:
    """Provenance du moteur embarqué (dépôt amont, révision, date)."""
    try:
        return json.loads(PROVENANCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def page_complete() -> str:
    scenarios_json = json.dumps(
        {
            cle: {k: v for k, v in valeur.items() if k != "fn"}
            for cle, valeur in SCENARIOS.items()
        },
        ensure_ascii=False,
    )
    contenu = HTML_PAGE.replace(REPERE, scenarios_json)
    if REPERE in contenu:
        raise SystemExit(
            f"Le repère {REPERE} n'a pas été remplacé : la page serait inutilisable."
        )
    origine = provenance()
    reference = origine.get("revision_courte", "révision inconnue")
    date = origine.get("date_revision", "")[:10]
    entete = (
        "<!DOCTYPE html>\n<!--\n"
        "  Page du simulateur macro-politique, générée pour le site M.R.S.C par\n"
        "  outils/construire-simulateur.py — ne pas modifier à la main.\n"
        f"  Moteur : {origine.get('depot_amont', 'dépôt du simulateur')}\n"
        f"  révision {reference}{f' ({date})' if date else ''}, "
        f"copiée le {origine.get('copie_le', 'date inconnue')}.\n"
        "  Source de la page : simulateur/interface.py, constante HTML_PAGE.\n-->"
    )
    return contenu.replace("<!DOCTYPE html>", entete, 1)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--verifier", action="store_true", help="ne rien écrire, signaler une divergence")
    options = analyseur.parse_args()

    page = page_complete()
    if options.verifier:
        if not SORTIE.is_file():
            print(f"{SORTIE.relative_to(RACINE)} est absent : lancez le script sans --verifier.")
            return 1
        if SORTIE.read_text(encoding="utf-8") != page:
            print(f"{SORTIE.relative_to(RACINE)} a divergé du moteur : régénérez-le.")
            return 1
        print("La page du simulateur est à jour.")
        return 0

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(page, encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} écrit : {len(page):,} caractères".replace(",", " "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
