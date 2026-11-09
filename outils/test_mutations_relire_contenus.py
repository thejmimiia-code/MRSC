#!/usr/bin/env python3
"""Banc de mutations de la sentinelle de toutes les éditions.

Une porte qui ne sait pas échouer ne protège aucune édition. Chaque cas plante
une faute réelle dans une copie jetable du dépôt et exige que
`relire-contenus.py` la refuse **en la nommant**. Le premier cas vérifie que la
copie intacte passe : une porte toujours rouge n'est pas une preuve.

Fautes plantées : édition non signée, unité nouvelle non enregistrée, unité
déclarée disparue, ancre morte, lien local cassé, marqueur de brouillon, TOML
illisible, extrait de source modifié, extrait sans ancre, source sans extrait,
source périmée, crochet supprimé, déclencheur de branche retiré, apostrophe
droite nouvelle, édition falsifiée, écriture dans le registre humain, et URL
externe nouvelle non sourcée au moment de signer.

Usage :
    python3 outils/test_mutations_relire_contenus.py
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "relire-contenus.py"
MANIFESTE = "docs/rd/empreintes-contenus.toml"
EDITIONS = "docs/rd/editions-relecture.toml"
REGISTRE = "docs/rd/relecture-contenus.toml"
HUMAIN = "docs/apprentissage/relectures.toml"
CROCHET = ".githooks/pre-commit"
WORKFLOW = ".github/workflows/relecture-contenus.yml"
CACHE = "docs/rd/sources-primaires/mdn-theme-color.txt"
PAGE = "index.html"


def muter(dossier: Path, relatif: str, ancien: str, nouveau: str) -> None:
    banc_mutations.muter(dossier, relatif, ancien, nouveau)


def ajouter(dossier: Path, relatif: str, texte: str) -> None:
    chemin = banc_mutations.ouvrir(dossier, relatif)
    if chemin.is_symlink():
        chemin.unlink()
    chemin.write_text(texte, encoding="utf-8")


class MutationsRelireContenus(unittest.TestCase):
    def refuser(self, preparer, attendu: str, arguments: tuple[str, ...] = ()) -> None:  # noqa: ANN001
        with tempfile.TemporaryDirectory(prefix="mrsc-relire-") as tmp:
            dossier = Path(tmp)
            banc_mutations.copie_jetable(dossier)
            preparer(dossier)
            resultat = banc_mutations.lancer(OUTIL, dossier, arguments=arguments)
            self.assertNotEqual(resultat.returncode, 0, f"la faute n'a pas été refusée : {resultat.stdout}")
            self.assertIn(attendu, resultat.stderr + resultat.stdout, resultat.stderr[-1200:])

    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-relire-") as tmp:
            dossier = Path(tmp)
            banc_mutations.copie_jetable(dossier)
            resultat = banc_mutations.lancer(OUTIL, dossier)
            self.assertEqual(resultat.returncode, 0, resultat.stderr)

    def test_edition_non_signee(self) -> None:
        self.refuser(
            lambda d: muter(d, PAGE, "<!doctype html>", "<!doctype html>\n<!-- retouche -->"),
            "édition non relue",
        )

    def test_unite_nouvelle_non_enregistree(self) -> None:
        self.refuser(
            lambda d: ajouter(d, "docs/rd/edition-fantome.md", "# Un nouveau document\n"),
            "unité non enregistrée",
        )

    def test_unite_declaree_disparue(self) -> None:
        def preparer(dossier: Path) -> None:
            banc_mutations.cible(dossier, "llms.txt").unlink()
        self.refuser(preparer, "unité déclarée mais absente")

    def test_ancre_morte(self) -> None:
        self.refuser(
            lambda d: muter(d, PAGE, "<!doctype html>", "<!doctype html>\n<a href=\"#ancre-fantome\">x</a>"),
            "ancre interne morte",
        )

    def test_lien_local_casse(self) -> None:
        self.refuser(
            lambda d: muter(d, PAGE, "<!doctype html>", "<!doctype html>\n<img src=\"assets/images/inexistante.png\" alt=\"\">"),
            "local introuvable",
        )

    def test_marqueur_de_brouillon(self) -> None:
        self.refuser(
            lambda d: muter(d, PAGE, "<!doctype html>", "<!doctype html>\n<!-- TODO à compléter -->"),
            "marqueur de brouillon",
        )

    def test_toml_illisible(self) -> None:
        self.refuser(
            lambda d: muter(d, HUMAIN, "#", "// commentaire non TOML\n#"),
            "TOML illisible",
        )

    def test_extrait_de_source_modifie(self) -> None:
        self.refuser(
            lambda d: muter(d, CACHE, "a suggested color", "a suggested colour"),
            "l'extrait a été modifié",
        )

    def test_extrait_sans_ancre(self) -> None:
        def preparer(dossier: Path) -> None:
            chemin = banc_mutations.cible(dossier, CACHE)
            contenu = chemin.read_text(encoding="utf-8")
            entete, _, corps = contenu.partition("---\n")
            import hashlib
            nouveau = corps.replace("a suggested color", "une couleur proposee")
            empreinte = hashlib.sha256(nouveau.strip().encode("utf-8")).hexdigest()
            lignes = [l for l in entete.splitlines() if not l.startswith("empreinte = ")]
            chemin.write_text("\n".join(lignes) + f"\nempreinte = {empreinte}\n---\n" + nouveau, encoding="utf-8")
        self.refuser(preparer, "ancre absente de l'extrait")

    def test_source_sans_extrait(self) -> None:
        self.refuser(
            lambda d: muter(d, REGISTRE, 'extrait = "docs/rd/sources-primaires/mdn-color-scheme.txt"\n', ""),
            "aucun extrait mis en cache",
        )

    def test_source_perimee(self) -> None:
        self.refuser(
            lambda d: muter(d, REGISTRE, "consulte_le = 2026-11-07", "consulte_le = 2024-01-01"),
            "trop ancienne",
        )

    def test_crochet_supprime(self) -> None:
        def preparer(dossier: Path) -> None:
            banc_mutations.cible(dossier, CROCHET).unlink()
        self.refuser(preparer, "crochet pre-commit absent")

    def test_declencheur_de_branche_retire(self) -> None:
        self.refuser(
            lambda d: muter(d, WORKFLOW, "    branches: ['**']", "    branches: [main]"),
            "toutes les branches doivent être couvertes",
        )

    def test_apostrophe_droite_nouvelle(self) -> None:
        self.refuser(
            lambda d: muter(d, PAGE, "<!doctype html>", "<!doctype html>\n<p>d'essai</p>"),
            "apostrophes droites",
        )

    def test_edition_falsifiee(self) -> None:
        self.refuser(
            lambda d: ajouter(d, EDITIONS, '[[edition]]\nchemin = "index.html"\n'),
            "champ « date » absent",
        )

    def test_registre_humain_ecrit(self) -> None:
        self.refuser(
            lambda d: ajouter(d, HUMAIN, '[[relecture]]\nfiche = "fr-distinguer-fait-interpretation"\n'),
            "ne doit jamais y écrire",
        )

    def test_url_externe_nouvelle_non_sourcee(self) -> None:
        def preparer(dossier: Path) -> None:
            muter(dossier, PAGE, "<!doctype html>", "<!doctype html>\n<p>Voir https://source-inconnue.test/fait-non-source.</p>")
        self.refuser(
            preparer,
            "URL externe nouvelle sans source primaire",
            arguments=(
                "--appliquer", PAGE,
                "--nature", "fait-source",
                "--sources", "mdn-theme-color",
                "--constat", "Lecture du lot et confrontation à une source primaire datée.",
                "--limite", "Cette relecture ne couvre ni le rendu visuel ni une expertise humaine.",
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
