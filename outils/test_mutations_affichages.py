#!/usr/bin/env python3
"""Rejoue les mutations des garde-fous d'affichage sur une copie du dépôt.

Depuis le 23 octobre 2026, le journal dit à plusieurs reprises « mutation
rejouée : détectée ». C'était vrai, et c'était fait à la main : la porte
`verifier-affichages.py` n'avait aucun test qui échoue quand on retire la règle
qu'elle prétend protéger. Un garde-fou jamais vu en échec est une affirmation,
pas un contrôle — la leçon du 28 octobre sur `verifier-taux-dates.py` vaut ici
pour seize garde-fous d'un coup.

Ce banc construit une **copie jetable** du dépôt : chaque entrée de la racine est
un lien symbolique vers l'original, et seuls les fichiers mutés sont de vraies
copies. Rien n'est écrit dans l'arbre de travail, même quand un contrôle échoue.
La racine lue par `verifier-affichages.py` est surchargée par `MRSC_RACINE`,
prévue pour cet usage.

Ce que ce banc ne dit pas : il prouve que chaque garde-fou mord sur la mutation
qu'on lui présente, pas qu'il couvre toutes les façons de casser l'affichage. Un
garde-fou peut être puissant sur ce cas et aveugle sur un autre.

Usage :
    python3 outils/test_mutations_affichages.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONTROLE = RACINE / "outils" / "verifier-affichages.py"


def copie_jetable(dossier: Path) -> None:
    """Recopie l'arborescence en liens symboliques : rien n'est dupliqué."""
    for entree in RACINE.iterdir():
        if entree.name in {".git", "__pycache__"}:
            continue
        (dossier / entree.name).symlink_to(entree, target_is_directory=entree.is_dir())


def ouvrir(dossier: Path, relatif: str) -> Path:
    """Rend un chemin réel dans la copie, en défaisant les liens du chemin.

    Pour écrire `assets/css/site.css` sans toucher au dépôt, il faut que
    `assets` puis `assets/css` soient de vrais dossiers : ils sont recréés, et
    leurs autres enfants restent des liens vers l'original. La fonction est
    idempotente, parce que deux mutations successives empruntent le même chemin.
    """
    morceaux = Path(relatif).parts
    courant, original = dossier, RACINE
    for position, morceau in enumerate(morceaux[:-1]):
        suivant, cible = courant / morceau, original / morceau
        descendant = morceaux[position + 1]
        if suivant.is_symlink():
            suivant.unlink()
        suivant.mkdir(exist_ok=True)
        for enfant in cible.iterdir():
            if enfant.name == descendant or (suivant / enfant.name).exists():
                continue
            (suivant / enfant.name).symlink_to(enfant, target_is_directory=enfant.is_dir())
        courant, original = suivant, cible
    return courant / morceaux[-1]


def muter(dossier: Path, relatif: str, ancien: str, nouveau: str) -> None:
    """Remplace un fragment dans une copie réelle du fichier, jamais dans l'original."""
    chemin = ouvrir(dossier, relatif)
    if chemin.is_symlink():
        chemin.unlink()
    if not chemin.exists():
        shutil.copyfile(RACINE / relatif, chemin)
    texte = chemin.read_text(encoding="utf-8")
    if ancien not in texte:
        raise AssertionError(f"fragment absent de {relatif} : la mutation ne mordrait pas")
    chemin.write_text(texte.replace(ancien, nouveau, 1), encoding="utf-8")


def lancer(dossier: Path) -> subprocess.CompletedProcess[str]:
    environnement = dict(os.environ, MRSC_RACINE=str(dossier))
    return subprocess.run(
        [sys.executable, str(CONTROLE)],
        capture_output=True,
        text=True,
        check=False,
        env=environnement,
    )


#: Chaque entrée : nom, fichier, fragment retiré ou remplacé, message attendu.
#: Les mutations reprennent des décisions datées du journal, pour que le banc
#: garde le lien entre une règle écrite et le contrôle qui la tient.
MUTATIONS = (
    (
        "panneau de personnalisation ancré à droite",
        "assets/css/site.css",
        "    right: auto;\n    left: 0;\n",
        "",
        "ne bascule plus vers la droite",
    ),
    (
        "mention d'impression sur sa propre ligne",
        "assets/css/site.css",
        "  display: block;\n  margin-top: .3rem;\n  text-align: start;\n",
        "  margin-top: .3rem;\n  text-align: start;\n",
        "mention d'impression n'ouvre plus sa propre ligne",
    ),
    (
        "note de version non bornée dans le bas de page",
        "assets/css/site.css",
        ".footer-bottom .footer-rd {",
        ".footer-bottom .footer-rd-absent {",
        "note de version est de nouveau bornée",
    ),
    (
        "adresse d'impression sur la page d'accueil",
        "index.html",
        '<html lang="fr" data-print-url="https://thejmimiia-code.github.io/MRSC/">',
        '<html lang="fr">',
        "adresse d'impression",
    ),
    (
        "mention d'impression dans le pied de page de l'accueil",
        "index.html",
        '<span class="footer-rd-print">',
        '<span class="footer-rd-print-absent">',
        "collent la mention d'impression derrière le point",
    ),
)


class TestMutationsAffichages(unittest.TestCase):
    def setUp(self) -> None:
        self._dossier = tempfile.TemporaryDirectory()
        self.dossier = Path(self._dossier.name)
        copie_jetable(self.dossier)

    def tearDown(self) -> None:
        self._dossier.cleanup()

    def test_copie_intacte_passe(self) -> None:
        """Sans mutation, la copie doit être verte : sinon le banc ne prouve rien."""
        resultat = lancer(self.dossier)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("garde-fous des formats", resultat.stdout)

    def test_chaque_mutation_est_detectee(self) -> None:
        for nom, relatif, ancien, nouveau, message in MUTATIONS:
            with self.subTest(mutation=nom), tempfile.TemporaryDirectory() as dossier:
                copie_jetable(Path(dossier))
                muter(Path(dossier), relatif, ancien, nouveau)
                resultat = lancer(Path(dossier))
                self.assertEqual(
                    resultat.returncode,
                    1,
                    f"la mutation « {nom} » n'a pas été vue :\n{resultat.stdout}",
                )
                self.assertIn(message, resultat.stderr, resultat.stderr[:900])

    def test_le_depot_n_est_pas_modifie(self) -> None:
        """Le banc écrit dans une copie : un échec ne doit rien laisser derrière lui."""
        avant = (RACINE / "assets" / "css" / "site.css").read_bytes()
        muter(self.dossier, "assets/css/site.css", "    right: auto;\n    left: 0;\n", "")
        lancer(self.dossier)
        apres = (RACINE / "assets" / "css" / "site.css").read_bytes()
        self.assertEqual(avant, apres)


if __name__ == "__main__":
    unittest.main(verbosity=2)
