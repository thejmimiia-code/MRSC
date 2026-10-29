#!/usr/bin/env python3
"""La mutation plantée a-t-elle fait dire au contrôle ce qu'elle devait lui faire dire ?

`outils/verifier-graphismes.cjs` sait rejouer trois fautes internes
(`distorsion`, `densite`, `ancre`) quand `MRSC_MUTATION` est défini. La CI exige
que le contrôle sorte en erreur pour chacune — mais un **code de sortie** ne dit
pas *pourquoi* il a échoué. Une mutation qui ferait céder le contrôle pour une
raison sans rapport avec ce qu'elle plante laisserait la CI verte : le banc
mesurerait une panne, pas la garde.

Ce contrôle lit le rapport JSON de la passe mutée et exige que l'erreur attendue
y figure :

- `distorsion` → « distorsion » (image étirée : ratio de boîte ≠ ratio source) ;
- `densite` → « densité insuffisante » (source retirée : l'image rendue est plus
  grande que son fichier) ;
- `ancre` → « ancre » (pastille déplacée loin de son point de constellation).

Usage :
    python3 outils/verifier-mutation-graphismes.py RAPPORT.json MUTATION

Code de sortie : 0 si l'erreur attendue est constatée, 1 sinon (le message dit ce
qui a été constaté à la place). Aucun réseau, aucun navigateur : le rapport est
un fichier déjà écrit par le contrôle.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

#: Ce que chaque mutation doit faire constater. Ces chaînes sont celles que
#: `verifier-graphismes.cjs` écrit dans `erreurs` ; si elles changent là-bas,
#: `test_verifier_mutation_graphismes.py` le verra, parce qu'il lit le script.
ATTENDU = {
    "distorsion": "distorsion",
    "densite": "densité insuffisante",
    "ancre": "ancre ",
}


def erreurs_constatees(rapport: dict) -> list[str]:
    """Toutes les erreurs du rapport, relevé par relevé."""
    constatees: list[str] = []
    for releve in rapport.get("erreurs", []):
        constatees.extend(str(erreur) for erreur in releve.get("erreurs", []))
    return constatees


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("rapport", type=Path, help="rapport JSON de la passe mutée")
    analyseur.add_argument("mutation", choices=sorted(ATTENDU), help="mutation plantée")
    options = analyseur.parse_args()

    if not options.rapport.is_file():
        print(
            f"ÉCHEC — rapport absent : {options.rapport}. La mutation n'a rien mesuré, "
            "donc son échec ne prouve rien."
        )
        return 1
    try:
        rapport = json.loads(options.rapport.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as erreur:
        print(f"ÉCHEC — rapport illisible : {options.rapport} ({erreur})")
        return 1

    constatees = erreurs_constatees(rapport)
    voulue = ATTENDU[options.mutation]
    if not any(voulue in erreur for erreur in constatees):
        print(
            f"ÉCHEC — la mutation « {options.mutation} » a fait échouer le contrôle "
            f"sans constater « {voulue.strip()} ». Constaté à la place : "
            f"{constatees[:5] if constatees else 'aucune erreur'}"
        )
        return 1

    # Une erreur constatée ne dit pas que *seule* celle-là l'a été : le compte
    # est publié pour que le journal puisse le citer.
    print(
        f"OK — mutation « {options.mutation} » : « {voulue.strip()} » constatée "
        f"({len(constatees)} erreur(s) au total sur {len(rapport.get('erreurs', []))} relevé(s))."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
