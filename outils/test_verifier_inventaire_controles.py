#!/usr/bin/env python3
"""Tests du contrôle de l'inventaire des contrôles.

`verifier-inventaire-controles.py` garde `docs/rd/inventaire-controles.md` : un
outil ajouté sans ligne, un fichier de test annoncé qui n'existe pas, un chemin
cité qui a bougé, un total écrit à la main qui a pris du retard. Ce contrôle-là
aussi doit prouver qu'il mord — sinon il protège l'inventaire exactement comme
un cadenas sans pêne.

Les fautes sont plantées dans une copie complète du dépôt, comme pour la porte
des pages statiques : l'outil lit des chemins réels.

Usage :
    python3 outils/test_verifier_inventaire_controles.py
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-inventaire-controles.py"
DOC = "docs/rd/inventaire-controles.md"


def ligne_de(copie: Path, outil: str) -> str:
    """Ligne du tableau décrivant `outil`, telle qu'elle est écrite dans la copie."""
    for ligne in (copie / DOC).read_text(encoding="utf-8").splitlines():
        if ligne.startswith(f"| `{outil}`"):
            return ligne
    raise AssertionError(f"{outil} n'a pas de ligne dans l'inventaire : le banc ne peut pas muter")


class TestInventaireControles(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Inventaire des contrôles", resultat.stdout)

    def test_outil_ajoute_sans_ligne_refuse(self) -> None:
        """Le cas qui compte : un nouvel outil ne peut pas entrer sans décision écrite."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            (copie / "outils" / "verifier-nouveaute.py").write_text(
                "#!/usr/bin/env python3\n", encoding="utf-8"
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("outils/verifier-nouveaute.py", resultat.stderr)
        self.assertIn("absents de l'inventaire", resultat.stderr)

    def test_ligne_retiree_refuse(self) -> None:
        """Retirer une ligne de l'inventaire doit être vu, pas silencieux.

        La ligne est lue dans la copie plutôt qu'écrite en dur : ce banc ne doit
        pas casser chaque fois qu'un statut change dans le document qu'il garde.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            ligne = ligne_de(copie, "outils/verifier-fusions.py")
            banc_mutations.muter(copie, DOC, ligne, "")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("outils/verifier-fusions.py", resultat.stderr)

    def test_test_annonce_absent_refuse(self) -> None:
        """Un statut qui prétend s'appuyer sur un test doit citer un test réel."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            banc_mutations.muter(
                copie,
                DOC,
                "`test_placement_panneau.mjs` (3 600 positions, sans navigateur)",
                "`test_qui_n_existe_pas.py` (3 600 positions, sans navigateur)",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("test_qui_n_existe_pas.py", resultat.stderr)

    def test_compte_du_tableau_faux_refuse(self) -> None:
        """Le 3 novembre 2026, la prose annonçait « Vingt-deux » bancs pour trente.

        Le total était recopié à la main, personne ne le relisait, et il avait
        pris six unités de retard. Le tableau « Combien » est désormais confronté
        aux lignes réelles : ce cas casse un seul chiffre — celui du banc, lu dans
        le document et non recopié ici, pour que le banc ne meure pas au prochain
        ajout d'outil (ce qui est arrivé le jour même).
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            nombre = self.nombre_du_banc(copie)
            banc_mutations.muter(copie, DOC, f"| `banc` | {nombre} |", f"| `banc` | {nombre + 1} |")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn(f"annonce {nombre + 1}", resultat.stderr)

    def test_phrase_de_synthese_fausse_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            phrase = self.phrase_de_synthese(copie)
            avec, total = phrase.groups()
            banc_mutations.muter(copie, DOC, phrase.group(0), f"**{int(avec) - 1} contrôles sur {total}**")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn(f"{int(avec) - 1} contrôles éprouvés", resultat.stderr)

    def test_phrase_de_synthese_effacee_refusee(self) -> None:
        """Effacer la phrase ne doit pas valoir zéro erreur : elle porte les totaux."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            phrase = self.phrase_de_synthese(copie)
            banc_mutations.muter(copie, DOC, phrase.group(0), "les contrôles éprouvés, en prose")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("a disparu", resultat.stderr)

    def test_statut_absent_du_tableau_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            ligne = self.ligne_de_combien(copie, "test-en-soi")
            trouve = re.match(r"\|\s*`(?P<statut>[a-z-]+)`", ligne)
            self.assertIsNotNone(trouve)
            banc_mutations.muter(copie, DOC, ligne, ligne.replace("`test-en-soi`", "`test_en_soi`"))
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("omet", resultat.stderr)

    @staticmethod
    def ligne_de_combien(copie: Path, statut: str) -> str:
        """Ligne du tableau « Combien » pour un statut, lue dans le document."""
        for ligne in (copie / DOC).read_text(encoding="utf-8").splitlines():
            if re.match(rf"\|\s*`{re.escape(statut)}`\s*\|\s*\d+\s*\|", ligne):
                return ligne
        raise AssertionError(f"aucune ligne « {statut} » dans le tableau : le banc ne peut pas muter")

    def nombre_du_banc(self, copie: Path) -> int:
        """Nombre annoncé pour les bancs, lu dans le document — jamais recopié."""
        ligne = self.ligne_de_combien(copie, "banc")
        return int(re.search(r"\|\s*(\d+)\s*\|", ligne.split("`banc`", 1)[1]).group(1))

    @staticmethod
    def phrase_de_synthese(copie: Path) -> re.Match[str]:
        trouve = re.search(r"\*\*(\d+) contrôles sur (\d+)\*\*", (copie / DOC).read_text(encoding="utf-8"))
        if not trouve:
            raise AssertionError("la phrase « N contrôles sur N » a disparu du document")
        return trouve

    def test_statut_inconnu_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            ligne = ligne_de(copie, "outils/verifier-maj-amont.py")
            statut = ligne.rsplit("`", 2)[1]
            banc_mutations.muter(copie, DOC, ligne, ligne.replace(f"`{statut}`", "`peut-etre`"))
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("statut inconnu", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
