#!/usr/bin/env python3
"""Banc de mutation de `verifier-planches-statuts.py`.

Ce contrôle garde les planches des statuts et leur archive : les planches citées
par le plan, les références `statuts-animation/…` éparpillées dans le dépôt, les
liens d'image des documents de R&D, l'absence de PNG suivi dans l'arbre, et les
343 empreintes du manifeste d'archive. Il n'avait aucun test.

Six fautes sont plantées dans une copie complète du dépôt, plus un cas qui n'est
pas une faute du dépôt mais une incapacité de l'environnement :

1. une planche citée par le plan est supprimée ;
2. une référence `statuts-animation/…` apparait dans un document vers une planche qui n'existe ni sur disque ni au manifeste ;
3. un lien d'image pointe vers un fichier inexistant ;
4. le manifeste perd une empreinte (342 au lieu de 343) ;
5. deux lignes du manifeste portent le même nom de fichier ;
6. un PNG est réellement suivi par git dans `docs/rd/statuts-animation/` ;
7. **la copie n'est pas un dépôt git** : le contrôle des PNG ne peut pas être
   fait, et l'outil doit le dire au lieu d'annoncer « aucun PNG suivi ».

Le septième cas vient d'un défaut réel trouvé en écrivant ce banc : avant le
28 octobre 2026, `git ls-files` en échec rendait une sortie vide, et le contrôle
affirmait l'absence de PNG qu'il n'avait jamais cherchés. Le banc a donc obligé
à corriger l'outil, pas seulement à l'éprouver.

Les cas 6 et 7 ont besoin d'un dépôt git : la copie en reçoit un (`git init`),
parce que `copie_complete()` exclut `.git` par construction.

Usage :
    python3 outils/test_mutations_planches_statuts.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-planches-statuts.py"
PLAN = "docs/rd/plan-statuts-animation.md"
MANIFESTE = "docs/rd/statuts-animation/ARCHIVE-film-associatif.sha256"
IDENTITE = {
    "GIT_AUTHOR_NAME": "banc",
    "GIT_AUTHOR_EMAIL": "banc@example.invalid",
    "GIT_COMMITTER_NAME": "banc",
    "GIT_COMMITTER_EMAIL": "banc@example.invalid",
}


def executer(mutation, depot: bool = True) -> subprocess.CompletedProcess[str]:  # noqa: ANN001
    """Copie complète, dépôt git optionnel, préparation, puis le contrôle réel."""
    with tempfile.TemporaryDirectory(prefix="mrsc-planches-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        if depot:
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=copie, check=True, capture_output=True, env={**os.environ, **IDENTITE},
            )
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


def premiere_planche_citee(copie: Path) -> str:
    """Premier lien `statuts-animation/…` du plan, pour ne pas recopier un nom."""
    plan = (copie / PLAN).read_text(encoding="utf-8")
    trouve = re.search(r"\]\((statuts-animation/[^)]+)\)", plan)
    if not trouve:
        raise AssertionError("aucune planche citée dans le plan : le banc ne peut pas muter")
    return trouve.group(1)


class TestPlanchesStatuts(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        # Le résumé ne prétend plus « conforme » : il dit ce qui est vérifié
        # (forme, nombre, unicité) et ce qui ne l'est pas (le contenu).
        self.assertIn("manifeste de 343 empreintes bien formées", resultat.stdout)
        self.assertIn("contenu non vérifié ici", resultat.stdout)

    def test_planche_supprimee_refusee(self) -> None:
        def supprimer(copie: Path) -> None:
            (copie / "docs" / "rd" / premiere_planche_citee(copie)).unlink()

        resultat = executer(supprimer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("planche citée absente", resultat.stdout)

    def test_reference_sans_fichier_refusee(self) -> None:
        # Le nom est assemblé, jamais écrit d'un trait : le contrôle balaie tous
        # les fichiers texte du dépôt, y compris ce banc, et une référence
        # littérale vers une planche absente ferait échouer la porte du dépôt
        # réel. C'est un piège rencontré en écrivant ce fichier.
        def ajouter(copie: Path) -> None:
            chemin = copie / PLAN
            chemin.write_text(
                chemin.read_text(encoding="utf-8")
                + "\nVoir " + "statuts-animation/" + "absente-totalement.webp\n",
                encoding="utf-8",
            )

        resultat = executer(ajouter)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("référence sans fichier ni archive", resultat.stdout)

    def test_lien_d_image_non_resolu_refuse(self) -> None:
        def casser(copie: Path) -> None:
            chemin = copie / "docs" / "rd" / "formats-affichage.md"
            chemin.write_text(
                chemin.read_text(encoding="utf-8") + "\n![absente](images/absente-banc.png)\n",
                encoding="utf-8",
            )

        resultat = executer(casser)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("lien d'image non résolu", resultat.stdout)

    def test_manifeste_tronque_refuse(self) -> None:
        def tronquer(copie: Path) -> None:
            chemin = copie / MANIFESTE
            lignes = chemin.read_text(encoding="utf-8").splitlines()
            chemin.write_text("\n".join(lignes[:-1]) + "\n", encoding="utf-8")

        resultat = executer(tronquer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("342 empreintes au lieu de 343", resultat.stdout)

    def test_manifeste_avec_nom_en_double_refuse(self) -> None:
        """Le compte reste bon : seule l'unicité des noms est cassée."""
        def dupliquer(copie: Path) -> None:
            chemin = copie / MANIFESTE
            lignes = chemin.read_text(encoding="utf-8").splitlines()
            empreinte, premier_nom = lignes[0].split("  ", 1)
            empreinte_suivante, _ = lignes[1].split("  ", 1)
            lignes[1] = f"{empreinte_suivante}  {premier_nom}"
            chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")

        resultat = executer(dupliquer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("noms de fichiers en double", resultat.stdout)

    def test_png_suivi_dans_l_arbre_refuse(self) -> None:
        def suivre(copie: Path) -> None:
            chemin = copie / "docs" / "rd" / "statuts-animation" / "planche-fautive.png"
            chemin.write_bytes(b"\x89PNG\r\n\x1a\n")
            subprocess.run(
                ["git", "add", "-f", str(chemin.relative_to(copie))],
                cwd=copie, check=True, capture_output=True, env={**os.environ, **IDENTITE},
            )

        resultat = executer(suivre)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("PNG suivi dans l'arbre", resultat.stdout)

    def test_archive_restauree_verifiee_en_contenu(self) -> None:
        """`--empreintes` vérifie une archive restaurée, hors de l'arbre."""
        with tempfile.TemporaryDirectory(prefix="mrsc-archive-") as dossier:
            archive = Path(dossier) / "archive"
            archive.mkdir()
            # Deux fichiers dont l'empreinte est lue dans le manifeste réel.
            manifeste = (RACINE / MANIFESTE).read_text(encoding="utf-8").splitlines()
            entrees = [ligne.split("  ", 1) for ligne in manifeste if "  " in ligne][:2]
            for _, nom in entrees:
                (archive / nom).write_bytes(b"contenu de test")
            # Une copie complète du dépôt pour que le reste du contrôle passe.
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=copie, check=True, capture_output=True, env={**os.environ, **IDENTITE},
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--empreintes", str(archive)))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        # Les deux fichiers existent mais ne correspondent pas : deux écarts nommés.
        self.assertEqual(resultat.stdout.count("empreinte différente"), 2, resultat.stdout)

    def test_archive_conforme_acceptee(self) -> None:
        """Un fichier réellement conforme est vu conforme, et compté."""
        with tempfile.TemporaryDirectory(prefix="mrsc-archive-") as dossier:
            archive = Path(dossier) / "archive"
            archive.mkdir()
            manifeste = (RACINE / MANIFESTE).read_text(encoding="utf-8").splitlines()
            empreinte, nom = [ligne.split("  ", 1) for ligne in manifeste if "  " in ligne][0]
            contenu = b"contenu conforme"
            (archive / nom).write_bytes(contenu)
            # Le manifeste de la copie est réécrit pour décrire ce fichier : le
            # banc ne recopie pas une empreinte, il la recalcule.
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            # Un dépôt git, sinon le contrôle des PNG échoue avant d'arriver au
            # manifeste — c'est le comportement voulu, il est testé plus bas.
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=copie, check=True, capture_output=True, env={**os.environ, **IDENTITE},
            )
            import hashlib

            calcule = hashlib.sha256(contenu).hexdigest()
            chemin = copie / MANIFESTE
            lignes = chemin.read_text(encoding="utf-8").splitlines()
            lignes[0] = f"{calcule}  {nom}"
            chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--empreintes", str(archive)))
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("1 empreinte(s) conforme(s)", resultat.stdout)
        self.assertIn("342 fichier(s) absent(s)", resultat.stdout)

    def test_archive_absente_est_un_manque(self) -> None:
        def rien(copie: Path) -> None:
            pass

        with tempfile.TemporaryDirectory(prefix="mrsc-archive-") as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            subprocess.run(
                ["git", "init", "-q", "-b", "main"],
                cwd=copie, check=True, capture_output=True, env={**os.environ, **IDENTITE},
            )
            resultat = banc_mutations.lancer(
                OUTIL, copie, arguments=("--empreintes", str(Path(dossier) / "inexistant"))
            )
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("archive introuvable", resultat.stdout)

    def test_depot_illisible_refuse_au_lieu_de_rassurer(self) -> None:
        """Le défaut trouvé en écrivant ce banc : une vérification impossible n'est pas un succès."""
        resultat = executer(lambda copie: None, depot=False)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("le contrôle des PNG suivis n'a pas pu être fait", resultat.stdout)
        self.assertNotIn("aucun PNG suivi", resultat.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
