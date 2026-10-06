"""Contrôles de chemins pour éviter de remplacer une source par son résultat."""

from itertools import combinations
from pathlib import Path


def verifier_chemins_distincts(*chemins: Path) -> None:
    """Détecte alias relatifs, liens symboliques et liens physiques existants."""
    for a, b in combinations(chemins, 2):
        if a.resolve() == b.resolve() or (a.exists() and b.exists() and a.samefile(b)):
            raise ValueError('Entrées et sorties doivent être des fichiers distincts')
