#!/usr/bin/env python3
"""Banc de mutation de `verifier-fusions.py`, deuxième de l'ordre de rentabilité.

Ce contrôle garde une règle de dépôt, pas une page : « ne rien perdre en
fusionnant ». Il dispose de deux régimes très différents — des contrôles hors
ligne sur l'index et le journal, et un audit `--branches` qui compare des objets
git — et aucun test ne l'éprouvait.

Le banc ne mute pas le dépôt réel : son historique n'a pas à servir de cobaye,
et fabriquer une branche perdue dedans serait une faute, pas un test. Chaque cas
part donc d'un **petit dépôt git neuf**, créé à la volée, dont on casse une
propriété à la fois. La porte est ensuite lancée par sous-processus, avec
`MRSC_RACINE` pointant sur ce dépôt.

Six fautes, plus deux cas honnêtes qui doivent rester verts :

1. un marqueur de conflit commité dans un fichier suivi ;
2. un `.orig` oublié et suivi ;
3. deux entrées de journal dans le mauvais ordre ;
4. deux entrées de journal au même titre ;
5. une branche distante qui porte un fichier présent nulle part ailleurs ;
6. une branche distante entièrement absorbée, qui doit rester *supprimable sans
   perte* — sans quoi le contrôle crierait au vol à chaque branche fusionnée.

Usage :
    python3 outils/test_mutations_fusions.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-fusions.py"
IDENTITE = {
    "GIT_AUTHOR_NAME": "banc",
    "GIT_AUTHOR_EMAIL": "banc@example.invalid",
    "GIT_COMMITTER_NAME": "banc",
    "GIT_COMMITTER_EMAIL": "banc@example.invalid",
}
JOURNAL = """# Journal

## 2026-10-28 — Seconde entrée

- texte.

## 2026-10-27 — Première entrée

- texte.
"""


def git(dossier: Path, *arguments: str) -> str:
    """Commande git dans le dépôt d'essai, avec une identité qui ne dépend de rien."""
    resultat = subprocess.run(
        ["git", *arguments],
        cwd=dossier,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, **IDENTITE},
    )
    if resultat.returncode != 0:
        raise AssertionError(f"git {' '.join(arguments)} a échoué : {resultat.stderr}")
    return resultat.stdout


def depot_neuf(dossier: Path) -> Path:
    """Dépôt minimal sain : deux pages, un journal en ordre, rien à signaler."""
    (dossier / "docs" / "rd").mkdir(parents=True)
    (dossier / "docs" / "rd" / "journal.md").write_text(JOURNAL, encoding="utf-8")
    (dossier / "apprendre.html").write_text("<!doctype html><title>Essai</title>\n", encoding="utf-8")
    (dossier / "README.md").write_text("# Essai\n", encoding="utf-8")
    git(dossier, "init", "-q", "-b", "main")
    git(dossier, "add", "-A")
    git(dossier, "commit", "-q", "-m", "état initial")
    return dossier


def lancer(dossier: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return banc_mutations.lancer(OUTIL, dossier, arguments=arguments)


class TestFusions(unittest.TestCase):
    def test_depot_neuf_passe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            resultat = lancer(dossier)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("ordre antichronologique et sans doublon", resultat.stdout)

    def test_marqueur_de_conflit_refuse(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            (dossier / "README.md").write_text(
                "# Essai\n<<<<<<< HEAD\nmain\n=======\nbranche\n>>>>>>> arena/essai\n",
                encoding="utf-8",
            )
            git(dossier, "commit", "-q", "-a", "-m", "conflit commité")
            resultat = lancer(dossier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("marqueur de conflit dans README.md", resultat.stdout)

    def test_sauvegarde_suivie_refusee(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            (dossier / "README.md.orig").write_text("# vestige\n", encoding="utf-8")
            git(dossier, "add", "README.md.orig")
            git(dossier, "commit", "-q", "-m", "vestige de fusion")
            resultat = lancer(dossier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("fichier de sauvegarde de fusion suivi : README.md.orig", resultat.stdout)

    def test_journal_hors_ordre_refuse(self) -> None:
        """L'inversion s'est déjà produite dans le vrai journal : elle doit être vue."""
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            (dossier / "docs" / "rd" / "journal.md").write_text(
                JOURNAL.replace(
                    "## 2026-10-28 — Seconde entrée\n\n- texte.\n\n"
                    "## 2026-10-27 — Première entrée\n\n- texte.\n",
                    "## 2026-10-27 — Première entrée\n\n- texte.\n\n"
                    "## 2026-10-28 — Seconde entrée\n\n- texte.\n",
                ),
                encoding="utf-8",
            )
            resultat = lancer(dossier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("ordre antichronologique attendu", resultat.stdout)

    def test_journal_titres_en_double_refuses(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            (dossier / "docs" / "rd" / "journal.md").write_text(
                JOURNAL + "\n## 2026-10-26 — Seconde entrée\n\n- texte.\n", encoding="utf-8"
            )
            resultat = lancer(dossier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("titres en double", resultat.stdout)

    def test_branche_portant_un_contenu_unique_refusee(self) -> None:
        """La suppression d'une telle branche perdrait le fichier : c'est le cas à voir."""
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            base = git(dossier, "rev-parse", "HEAD").strip()
            git(dossier, "checkout", "-q", "-b", "experience")
            (dossier / "experience.md").write_text("# Travail unique\n", encoding="utf-8")
            git(dossier, "add", "-A")
            git(dossier, "commit", "-q", "-m", "travail unique")
            unique = git(dossier, "rev-parse", "HEAD").strip()
            git(dossier, "checkout", "-q", "main")
            git(dossier, "branch", "-q", "-D", "experience")
            git(dossier, "update-ref", "refs/remotes/origin/main", base)
            git(dossier, "update-ref", "refs/remotes/origin/experience", unique)
            resultat = lancer(dossier, "--branches")
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("présents nulle part ailleurs", resultat.stdout)
        self.assertIn("experience.md", resultat.stdout)

    def test_branche_absorbee_est_dite_contenue(self) -> None:
        """Une branche déjà dans main est traitée avant toute comparaison d'objets."""
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            git(dossier, "checkout", "-q", "-b", "absorbee")
            (dossier / "apprendre.html").write_text(
                "<!doctype html><title>Essai</title><p>fusionnée</p>\n", encoding="utf-8"
            )
            git(dossier, "commit", "-q", "-a", "-m", "travail fusionné")
            pointe = git(dossier, "rev-parse", "HEAD").strip()
            git(dossier, "checkout", "-q", "main")
            git(dossier, "merge", "-q", "--ff-only", "absorbee")
            git(dossier, "branch", "-q", "-d", "absorbee")
            git(dossier, "update-ref", "refs/remotes/origin/main", pointe)
            git(dossier, "update-ref", "refs/remotes/origin/absorbee", pointe)
            resultat = lancer(dossier, "--branches")
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("absorbee : contenue dans main", resultat.stdout)

    def test_branche_recopiee_reste_supprimable(self) -> None:
        """Cas d'une fusion par recopie : contenu identique, objets de commit distincts.

        La branche n'est pas un ancêtre de `main`, donc le raccourci ne s'applique
        pas : c'est la comparaison de blobs qui décide. Elle doit conclure « sans
        perte » — sinon le contrôle crierait au vol à chaque fusion recopiée.
        """
        with tempfile.TemporaryDirectory(prefix="mrsc-fusions-") as temporaire:
            dossier = depot_neuf(Path(temporaire) / "depot")
            git(dossier, "checkout", "-q", "-b", "recopiee")
            (dossier / "note.md").write_text("# Même texte\n", encoding="utf-8")
            git(dossier, "add", "-A")
            git(dossier, "commit", "-q", "-m", "côté branche")
            cote_branche = git(dossier, "rev-parse", "HEAD").strip()
            git(dossier, "checkout", "-q", "main")
            (dossier / "note.md").write_text("# Même texte\n", encoding="utf-8")
            git(dossier, "add", "-A")
            git(dossier, "commit", "-q", "-m", "côté main, même contenu")
            cote_main = git(dossier, "rev-parse", "HEAD").strip()
            git(dossier, "branch", "-q", "-D", "recopiee")
            git(dossier, "update-ref", "refs/remotes/origin/main", cote_main)
            git(dossier, "update-ref", "refs/remotes/origin/recopiee", cote_branche)
            resultat = lancer(dossier, "--branches")
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("recopiee : contenu entièrement atteignable ailleurs", resultat.stdout)
        self.assertIn("supprimable sans perte", resultat.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
