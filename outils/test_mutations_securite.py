#!/usr/bin/env python3
"""Banc de mutation de `verifier-securite.py` : la porte qui n'avait aucun test.

C'était le plus fort décalage de l'inventaire du 28 octobre 2026. La porte garde
les frontières HTTP et WSGI du simulateur, la provenance navigateur, la liste
statique servie en local et l'épinglage des actions de la CI — et rien ne
prouvait qu'elle savait refuser quoi que ce soit. Onze fonctions internes
s'exécutaient, toutes vertes, sans qu'aucune ne soit jamais vue en échec.

Six fautes sont plantées ici, chacune dans une copie complète du dépôt :

1. un en-tête de sécurité retiré de `vercel.json` ;
2. une limite de fonction Vercel abaissée, la CSP restant intacte ;
3. une action GitHub dé-épinglée sur un tag mouvant ;
4. un runner qui repasse à `ubuntu-latest` ;
5. la liste statique élargie à *tout* fichier de la racine ;
6. le plafond de lecture d'une source distante retiré du moteur.

La copie est complète parce que la porte lit des fichiers réels et importe les
modules de `simulateur/` : muter un lien symbolique ne suffirait pas, et muter
l'original est hors de question.

Usage :
    python3 outils/test_mutations_securite.py
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

OUTIL = "verifier-securite.py"
VERCEL = "vercel.json"
CI = ".github/workflows/verification.yml"
SERVEUR = "outils/serveur-local.py"
MOTEUR = "simulateur/donnees_live.py"


def executer(*mutations: tuple[str, str, str]) -> subprocess.CompletedProcess[str]:
    """Copie complète, mutations appliquées dans l'ordre, puis la porte réelle."""
    with tempfile.TemporaryDirectory(prefix="mrsc-securite-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        for relatif, ancien, nouveau in mutations:
            banc_mutations.muter(copie, relatif, ancien, nouveau)
        return banc_mutations.lancer(OUTIL, copie)


class TestSecurite(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-securite-") as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Tous les tests de sécurité ciblés passent", resultat.stdout)

    def test_entete_vercel_retire_refuse(self) -> None:
        """Le cas le plus grave : une iframe qui reclique le site si l'en-tête tombe."""
        resultat = executer((
            VERCEL,
            '        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },\n',
            "",
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("les en-têtes globaux Vercel correspondent", resultat.stderr)

    def test_limite_fonction_vercel_abaissee_refusee(self) -> None:
        """La CSP reste intacte : seul le second contrôle doit mordre."""
        resultat = executer((VERCEL, '"maxDuration": 60,', '"maxDuration": 30,'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("durée/mémoire Vercel", resultat.stderr)

    def test_action_github_deepinglee_refusee(self) -> None:
        """Un tag mouvant est une dépendance non épinglée, même sur une action connue."""
        resultat = executer((
            CI,
            "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
            "actions/checkout@v4",
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("épinglées sur des révisions immuables", resultat.stderr)

    def test_runner_non_epingle_refuse(self) -> None:
        resultat = executer((
            CI,
            "runs-on: ubuntu-24.04\n    timeout-minutes: 20",
            "runs-on: ubuntu-latest\n    timeout-minutes: 20",
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("pin un runner Ubuntu 24.04", resultat.stderr)

    def test_liste_statique_elargie_refusee(self) -> None:
        """État survenu le 25 octobre 2026 : un hébergement qui publie la racine du dépôt."""
        resultat = executer((
            SERVEUR,
            "        if len(parties) == 1 and parties[0] in FICHIERS_RACINE_PUBLICS:\n            return True",
            "        if len(parties) == 1:\n            return True",
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("le serveur local refuse le dépôt", resultat.stderr)

    def test_plafond_de_source_retire_refuse(self) -> None:
        """Une source peut annoncer 8 Mio et en envoyer 800 : le plafond doit tenir avant lecture."""
        resultat = executer((
            MOTEUR,
            '        if longueur > MAX_SOURCE_RESPONSE_BYTES:\n'
            '            raise ErreurSource("réponse source trop volumineuse")\n',
            "",
        ))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("refusée avant lecture", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
