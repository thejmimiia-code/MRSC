#!/usr/bin/env python3
"""Banc de mutation de l'étape de relecture par agent.

Une nouvelle porte qui ne mord pas ne protège rien : chaque cas plante une faute
réelle dans une copie jetable du dépôt et exige que
`verifier-relecture-contenus.py` la refuse **en la nommant**. Le premier cas
vérifie que la copie intacte passe : sans lui, une porte toujours rouge
semblerait verte.

Fautes plantées : attribution humaine usurpée, statut de validation humaine,
source non primaire, source non datée, ancre trop longue, limites absentes,
fait-source sans source, source inconnue, proposition sourcée, chaîne publique
modifiée, chaîne publique non couverte, entrée humaine ajoutée, constante de
luminance périmée, tolérance de contraste revenue, nom d'œuvre réintroduit,
étape retirée de la CI ou de l'inventaire, et limite effacée du rapport.

Usage :
    python3 outils/test_mutations_relecture_contenus.py
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

OUTIL = "verifier-relecture-contenus.py"
REGISTRE = "docs/rd/relecture-contenus.toml"
RAPPORT = "docs/rd/relecture-apparences-2026-11-07.md"
CSS = "assets/css/site.css"
JS = "assets/js/site.js"
PORTE = "outils/verifier-apparences.py"
HUMAIN = "docs/apprentissage/relectures.toml"
WORKFLOW = ".github/workflows/verification.yml"
INVENTAIRE = "docs/rd/inventaire-controles.md"


def remplacer(dossier: Path, relatif: str, transformer) -> None:  # noqa: ANN001
    """Applique une fonction de transformation à un fichier de la copie."""
    chemin = banc_mutations.cible(dossier, relatif)
    texte = chemin.read_text(encoding="utf-8")
    modifie = transformer(texte)
    assert modifie != texte, f"mutation sans effet dans {relatif}"
    chemin.write_text(modifie, encoding="utf-8")


def retirer_affirmation(texte: str, identifiant: str) -> str:
    """Retire un bloc [[affirmation]] entier du registre."""
    motif = re.compile(r"\n\[\[affirmation\]\]\n(?:(?!\n\[\[).)*?id = \"" + re.escape(identifiant) + r"\"(?:(?!\n\[\[).)*", re.S)
    modifie, nombre = motif.subn("", texte, count=1)
    assert nombre == 1, f"bloc {identifiant} introuvable"
    return modifie


class MutationsRelectureContenus(unittest.TestCase):
    def refuser(self, preparer, attendu: str) -> None:  # noqa: ANN001
        with tempfile.TemporaryDirectory(prefix="mrsc-relecture-") as tmp:
            dossier = Path(tmp)
            banc_mutations.copie_jetable(dossier)
            preparer(dossier)
            resultat = banc_mutations.lancer(OUTIL, dossier)
            self.assertNotEqual(resultat.returncode, 0, f"la faute n'a pas été refusée : {resultat.stdout}")
            self.assertIn(attendu, resultat.stderr + resultat.stdout, resultat.stderr[-1200:])

    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-relecture-") as tmp:
            dossier = Path(tmp)
            banc_mutations.copie_jetable(dossier)
            resultat = banc_mutations.lancer(OUTIL, dossier)
            self.assertEqual(resultat.returncode, 0, resultat.stderr)

    def test_attribution_humaine_usurpee(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(d, REGISTRE, 'auteur = "agent"', 'auteur = "une personne"'),
                     "auteur doit être")

    def test_statut_de_validation_humaine(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, REGISTRE, 'statut = "relu-par-agent-sources-confrontees"',
            'statut = "valide-par-une-personne"'), "relu-par-agent")

    def test_source_non_primaire(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, REGISTRE,
            'url = "https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/color-scheme"',
            'url = "https://un-blog.test/couleurs"'), "domaine non retenu")

    def test_source_non_datee(self) -> None:
        self.refuser(lambda d: remplacer(
            d, REGISTRE, lambda t: t.replace("consulte_le = 2026-11-07", "consulte_le = 2025-11-07", 1)),
            "date de consultation")

    def test_ancre_trop_longue(self) -> None:
        self.refuser(lambda d: remplacer(
            d, REGISTRE,
            lambda t: t.replace('ancre = "\\"light\\" and \\"dark\\""',
                                'ancre = "une longue phrase recopiee mot pour mot depuis la page entiere"', 1)),
            "ancre trop longue")

    def test_limites_de_source_effacees(self) -> None:
        self.refuser(lambda d: remplacer(
            d, REGISTRE,
            lambda t: re.sub(r'(id = "w3c-luminance"[\s\S]*?limites = )"[^"]*"',
                             r'\1"courte"', t, count=1)),
            "limites")

    def test_fait_source_sans_source(self) -> None:
        self.refuser(lambda d: remplacer(
            d, REGISTRE,
            lambda t: t.replace('sources = ["mdn-prefers-color-scheme"]', 'sources = []', 1)),
            "un fait-source exige")

    def test_source_inconnue(self) -> None:
        self.refuser(lambda d: remplacer(
            d, REGISTRE,
            lambda t: t.replace('sources = ["mdn-color-scheme"]', 'sources = ["source-fantome"]', 1)),
            "source inconnue")

    def test_proposition_sourcee_a_une_source(self) -> None:
        self.refuser(lambda d: remplacer(
            d, REGISTRE,
            lambda t: re.sub(r'(id = "chaine-01"[\s\S]*?sources = )\[\]',
                             r'\1["mdn-color-scheme"]', t, count=1)),
            "ne doit pas s'appuyer")

    def test_chaine_publique_modifiee(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, JS, 'label: "Bobine nocturne"', 'label: "Bobine"'),
            "n'existe plus")

    def test_chaine_publique_non_couverte(self) -> None:
        self.refuser(lambda d: remplacer(d, REGISTRE, lambda t: retirer_affirmation(t, "chaine-06")),
                     "chaîne publique non relue")

    def test_entree_humaine_ajoutee(self) -> None:
        self.refuser(lambda d: remplacer(
            d, HUMAIN, lambda t: t + '\n[[relecture]]\nfiche = "fr-distinguer-fait-interpretation"\n'),
            "ne doit jamais y écrire")

    def test_constante_de_luminance_perimee(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, PORTE, "valeur <= 0.04045", "valeur <= 0.03928"),
            "seuil WCAG 2.2 actuel")

    def test_tolerance_de_contraste_revenue(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, PORTE, "if mesure + 1e-9 < seuil:", "if mesure < seuil - 0.01:"),
            "sans arrondi tolérant")

    def test_nom_d_oeuvre_reintroduit(self) -> None:
        self.refuser(lambda d: remplacer(d, CSS, lambda t: "/* Stranger Things */\n" + t),
                     "nom protégé réapparu")

    def test_etape_retiree_de_la_ci(self) -> None:
        self.refuser(lambda d: remplacer(
            d, WORKFLOW,
            lambda t: t.replace("          python3 outils/verifier-relecture-contenus.py", "          true", 1)),
            "n'est pas câblée")

    def test_etape_retiree_de_l_inventaire(self) -> None:
        self.refuser(lambda d: remplacer(
            d, INVENTAIRE,
            lambda t: t.replace("| `outils/verifier-relecture-contenus.py` |",
                                "| `outils/verifier-relecture-contenus-ancien.py` |", 1)),
            "n'est pas recensée")

    def test_limite_effacee_du_rapport(self) -> None:
        self.refuser(lambda d: remplacer(
            d, RAPPORT, lambda t: t.replace("avis juridique", "conseil")),
            "passage attendu absent")

    def test_validation_humaine_revendiquee(self) -> None:
        self.refuser(lambda d: remplacer(
            d, RAPPORT, lambda t: t + "\nTexte validé par une personne.\n"),
            "ne pas revendiquer")


if __name__ == "__main__":
    unittest.main(verbosity=2)
