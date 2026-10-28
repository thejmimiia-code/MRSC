#!/usr/bin/env python3
"""Banc de mutation de `verifier-publication-locale.py`, troisième de la liste.

Cette porte répond à une question qu'aucune autre ne pose : « ce qui est dans le
dépôt sera-t-il réellement servi par le site ? » Elle relit la liste de copie du
workflow de publication, reconstruit le périmètre servi, puis confronte les liens
des pages, les `url()` du CSS, le sitemap et la liste blanche de l'aperçu local.
Rien n'éprouvait ce contrôle : le favicon manquait déjà à la liste de copie sans
que personne ne le voie.

Six fautes sont plantées dans une copie complète du dépôt :

1. une page HTML ajoutée à la racine et oubliée dans la liste de copie ;
2. `favicon.ico` retiré de cette même liste, alors que les pages le demandent ;
3. un lien des pages vers un fichier qui n'est pas publié ;
4. une entrée en trop dans la liste blanche de l'aperçu local (servie, non publiée) ;
5. l'inverse : une page publiée que l'aperçu local ne sert pas ;
6. une adresse du `sitemap.xml` qui ne correspond à aucun fichier publié.

Usage :
    python3 outils/test_mutations_publication_locale.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-publication-locale.py"
WORKFLOW = ".github/workflows/deploy-pages.yml"
SERVEUR = "outils/serveur-local.py"
COPIE_RACINE = (
    " 404.html sitemap.xml llms.txt favicon.ico _site/"
)


def executer(*mutations: tuple[str, str, str] | None) -> subprocess.CompletedProcess[str]:
    """Copie complète, fichiers créés le cas échéant, mutations, puis la porte réelle."""
    with tempfile.TemporaryDirectory(prefix="mrsc-publication-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        for mutation in mutations:
            if mutation is None:
                continue
            relatif, ancien, nouveau = mutation
            banc_mutations.muter(copie, relatif, ancien, nouveau)
        return banc_mutations.lancer(OUTIL, copie)


class TestPublicationLocale(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-publication-") as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("périmètre publié complet", resultat.stdout)

    def test_page_oubliee_dans_la_liste_refusee(self) -> None:
        """Une page publiée sur le dépôt et oubliée à la copie n'est référencée par rien."""
        with tempfile.TemporaryDirectory(prefix="mrsc-publication-") as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            (copie / "nouvelle-page.html").write_text(
                "<!doctype html><title>Nouvelle page</title>\n", encoding="utf-8"
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("page publique absente du périmètre publié : nouvelle-page.html", resultat.stdout)

    def test_fichier_retire_de_la_copie_refuse(self) -> None:
        """Le cas réel : le favicon manquait à la liste, personne ne l'a vu."""
        resultat = executer((WORKFLOW, COPIE_RACINE, " 404.html sitemap.xml llms.txt _site/"))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("favicon.ico", resultat.stdout)

    def test_lien_vers_un_fichier_non_publie_refuse(self) -> None:
        resultat = executer((
            "index.html",
            'href="assets/css/site.css"',
            'href="assets/css/absente.css"',
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("absente.css", resultat.stdout)
        self.assertIn("n'est pas publié", resultat.stdout)

    def test_apercu_local_plus_large_que_le_site_refuse(self) -> None:
        """Servir en local un fichier que le site ne publie pas fabrique un faux aperçu."""
        resultat = executer((
            SERVEUR,
            '"404.html", "sitemap.xml", "llms.txt", "favicon.ico",',
            '"404.html", "sitemap.xml", "llms.txt", "favicon.ico", "notes-internes.md",',
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("fichiers servis mais non publiés — notes-internes.md", resultat.stdout)

    def test_page_publiee_non_servie_refusee(self) -> None:
        """L'autre sens : l'aperçu local ne doit pas être plus étroit que le site."""
        with tempfile.TemporaryDirectory(prefix="mrsc-publication-") as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            (copie / "merci.html").write_text("<!doctype html><title>Merci</title>\n", encoding="utf-8")
            banc_mutations.muter(
                copie,
                WORKFLOW,
                COPIE_RACINE,
                " 404.html sitemap.xml llms.txt favicon.ico merci.html _site/",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("fichiers publiés non servis — merci.html", resultat.stdout)

    def test_sitemap_hors_perimetre_refuse(self) -> None:
        resultat = executer((
            "sitemap.xml",
            "<loc>https://thejmimiia-code.github.io/MRSC/apprendre.html</loc>",
            "<loc>https://thejmimiia-code.github.io/MRSC/apprendre-disparu.html</loc>",
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("ne correspond à aucun fichier publié", resultat.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
