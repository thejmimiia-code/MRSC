#!/usr/bin/env python3
"""Aucune sortie commitée ne doit dépendre du jour où on la régénère.

Panne réelle à l'origine de ces tests : le 2026-10-22, les portes « qualite » et
« Publish M.R.S.C site » sont passées au rouge uniquement parce que
`docs/rd/avancees.md` et `docs/apprentissage/audit-automatique.md` portaient la
date du jour de leur génération. Comparées octet par octet au fichier commité,
elles divergeaient dès le lendemain sans qu'aucun contenu ait changé, et la
publication du site était bloquée. Régénérer les fichiers réparait le jour même
et re-cassait le suivant : la cause était structurelle, pas éditoriale.

Ces tests rejouent chaque porte CI qui compare un fichier généré avec une
horloge déplacée de +37 puis +400 jours. +400 franchit à la fois la prochaine
échéance de revue de contenu d'une fiche (2027-01-09) et l'échéance de revue du
portefeuille : si une sortie dépend encore du calendrier, elle échoue ici,
aujourd'hui, au lieu d'échouer en production dans plusieurs mois.

Ce que ces tests ne font pas :
  - ils ne vérifient pas qu'une date est *juste*, seulement qu'elle est *stable*
    — la justesse d'une date de revue reste une relecture humaine ;
  - ils ne remplacent pas les portes elles-mêmes, ils les rejouent ailleurs dans
    le temps ;
  - une alerte d'échéance dépassée (`verifier-rd-continue.py`) est un
    avertissement par conception et ne fait pas échouer une porte : ces tests
    vérifient le code de retour, pas l'absence d'alerte.
"""

from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import importlib.util
import io
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE / "outils") not in sys.path:
    sys.path.insert(0, str(RACINE / "outils"))

# Fichiers écrits par les générateurs et comparés au dépôt par une porte CI.
ARTEFACTS = (
    "apprendre.html",
    "docs/apprentissage/audit-automatique.md",
    "docs/apprentissage/file-relecture.md",
    "docs/apprentissage/objectif-1000.md",
    "docs/apprentissage/paquets-relecture.md",
    "docs/apprentissage/sources-refusees.md",
    "docs/couverture-savoirs-base.md",
    "docs/rd/avancees.md",
    "docs/rd/carte-lacunes.md",
    "docs/rd/confrontations-sources.md",
    "simulateur/index.html",
)

# Mêmes commandes que `.github/workflows/verification.yml`.
PORTES = (
    ("construire-apprentissages.py", ("--verifier", "--rapport")),
    ("construire-simulateur.py", ("--verifier",)),
    ("file-relecture.py", ("--verifier",)),
    ("auditer-prototypes.py", ("--verifier",)),
    ("construire-paquets-relecture.py", ("--verifier",)),
    ("construire-sources-refusees.py", ("--verifier",)),
    ("confronter-sources.py", ("--verifier",)),
    ("construire-avancees.py", ("--verifier",)),
    ("registre-relecture.py", ()),
    ("verifier-rd-continue.py", ()),
)

DECALAGES_JOURS = (0, 37, 400)


class _MetaHorloge(type):
    """Métatype qui laisse les vraies `date` passer les `isinstance`.

    Sans lui, remplacer `date` par une sous-classe ferait échouer tous les
    `isinstance(valeur, date)` du dépôt sur les dates produites par `tomllib` :
    l'horloge de test signalerait alors des pannes qui n'existent pas.
    """

    def __instancecheck__(cls, objet):
        return type.__instancecheck__(dt.date, objet)

    def __subclasscheck__(cls, sous_classe):
        return type.__subclasscheck__(dt.date, sous_classe)


def horloge(decalage_jours: int) -> type:
    """Classe `date` dont `today()` renvoie une date déplacée."""
    cible = dt.date.today() + dt.timedelta(days=decalage_jours)

    class Horloge(dt.date, metaclass=_MetaHorloge):
        @classmethod
        def today(cls):
            return cible

    return Horloge


class _ModuleDatetime:
    """Substitut de `import datetime as dt` qui ne remplace que `date`.

    Remplacer l'attribut `date` du vrai module `datetime` modifierait
    l'interpréteur entier, `tomllib` compris ; ce mandataire reste local au
    module testé et transmet tout le reste au module réel.
    """

    def __init__(self, reel, horloge_injectee):
        self._reel = reel
        self._horloge = horloge_injectee

    def __getattr__(self, nom):
        if nom == "date":
            return self._horloge
        return getattr(self._reel, nom)


def lancer_porte(script: str, arguments: tuple[str, ...], decalage_jours: int) -> tuple[int, str]:
    """Exécute `main()` d'un outil du dépôt avec une horloge déplacée."""
    horloge_injectee = horloge(decalage_jours)
    specification = importlib.util.spec_from_file_location(
        f"porte_{script[:-3].replace('-', '_')}_{decalage_jours}", RACINE / "outils" / script
    )
    module = importlib.util.module_from_spec(specification)
    tampon = io.StringIO()
    argv_reel = sys.argv
    with tempfile.TemporaryDirectory() as dossier:
        argv_test = [script, *arguments]
        if "--rapport" in arguments:
            argv_test.append(str(Path(dossier) / "rapport.md"))
        try:
            with contextlib.redirect_stdout(tampon), contextlib.redirect_stderr(tampon):
                specification.loader.exec_module(module)
                if hasattr(module, "date"):
                    module.date = horloge_injectee
                module_datetime = getattr(module, "dt", None)
                if getattr(module_datetime, "__name__", "") == "datetime":
                    module.dt = _ModuleDatetime(dt, horloge_injectee)
                sys.argv = argv_test
                try:
                    code = module.main()
                except SystemExit as sortie:  # un outil qui sort au lieu de retourner
                    code = sortie.code if isinstance(sortie.code, int) else 1
        finally:
            sys.argv = argv_reel
    return int(code), tampon.getvalue()


def empreintes() -> dict[str, str]:
    def empreinte(chemin: Path) -> str:
        return hashlib.sha256(chemin.read_bytes()).hexdigest() if chemin.is_file() else "absent"

    return {relatif: empreinte(RACINE / relatif) for relatif in ARTEFACTS}


class AucuneSortieNeDependDuCalendrier(unittest.TestCase):
    def test_les_portes_ci_passent_a_une_date_decalee(self):
        """La panne de 2026-10-22 ne doit plus pouvoir se reproduire.

        Chaque porte est rejouée au jour réel puis dans le futur. Un échec ici
        signifie qu'un fichier commité changerait tout seul avec le calendrier.
        """
        for decalage in DECALAGES_JOURS:
            for script, arguments in PORTES:
                with self.subTest(porte=script, horloge=f"+{decalage} jours"):
                    code, sortie = lancer_porte(script, arguments, decalage)
                    detail = "\n".join(
                        ligne for ligne in sortie.splitlines() if "ÉCHEC" in ligne or "erreur" in ligne.casefold()
                    )
                    self.assertEqual(
                        code,
                        0,
                        f"{script} --verifier échoue avec une horloge à +{decalage} jours : "
                        f"une sortie commitée dépend du jour d'exécution.\n{detail or sortie[-800:]}",
                    )

    def test_le_mode_verifier_n_ecrit_dans_aucun_artefact(self):
        """Vérifier ne doit pas régénérer : sinon la comparaison est circulaire."""
        avant = empreintes()
        for script, arguments in PORTES:
            lancer_porte(script, arguments, 400)
        self.assertEqual(avant, empreintes(), "un mode --verifier a modifié un artefact du dépôt")

    def test_les_deux_horodatages_viennent_des_sources_editoriales(self):
        """Contrôle direct sur les deux fichiers qui ont cassé la publication."""
        registre = tomllib.loads((RACINE / "docs/rd/avancees.toml").read_text(encoding="utf-8"))
        catalogue = tomllib.loads((RACINE / "docs/apprentissage/catalogue.toml").read_text(encoding="utf-8"))
        attendus = {
            "docs/rd/avancees.md": ("**Date du registre :**", str(registre["meta"]["derniere_revue"])),
            "docs/apprentissage/audit-automatique.md": ("**Date de référence :**", max(str(f["revue_le"]) for f in catalogue["fiche"])),
        }
        for relatif, (etiquette, date_source) in attendus.items():
            lignes = (RACINE / relatif).read_text(encoding="utf-8").splitlines()
            horodatees = [ligne for ligne in lignes if ligne.startswith(etiquette)]
            with self.subTest(fichier=relatif):
                self.assertEqual(len(horodatees), 1, f"étiquette « {etiquette} » absente ou dupliquée")
                # Une revue réellement faite aujourd'hui peut légitimement
                # porter la date du jour. C'est sa provenance qui compte ; la
                # stabilité sous horloge décalée est testée séparément.
                self.assertEqual(
                    horodatees[0][len(etiquette):].strip()[:10],
                    date_source,
                    "l'horodatage ne correspond pas à la source éditoriale",
                )


class LeGardeFouADesDents(unittest.TestCase):
    def test_un_generateur_horodate_sur_le_jour_est_bien_detecte(self):
        """Preuve que le test précédent n'est pas décoratif.

        On rejoue le même harnais sur un générateur volontairement fautif, qui
        horodate sa sortie sur `date.today()`. Il doit échouer sous horloge
        déplacée — sinon la porte ci-dessus pourrait passer à tort.
        """
        modele = '''
import sys
from datetime import date
from pathlib import Path

SORTIE = Path({cible!r})


def main() -> int:
    attendu = f"**Date de génération :** {{date.today().isoformat()}}.\\n"
    if "--verifier" in sys.argv:
        return 0 if SORTIE.read_text(encoding="utf-8") == attendu else 1
    SORTIE.write_text(attendu, encoding="utf-8")
    return 0
'''
        with tempfile.TemporaryDirectory() as dossier:
            artefact = Path(dossier) / "artefact.md"
            generateur = Path(dossier) / "generateur-fautif.py"
            generateur.write_text(modele.format(cible=str(artefact)), encoding="utf-8")
            artefact.write_text(
                f"**Date de génération :** {dt.date.today().isoformat()}.\n", encoding="utf-8"
            )

            def lancer(decalage: int) -> int:
                injectee = horloge(decalage)
                specification = importlib.util.spec_from_file_location("fautif", generateur)
                module = importlib.util.module_from_spec(specification)
                argv_reel = sys.argv
                try:
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        specification.loader.exec_module(module)
                        module.date = injectee
                        sys.argv = ["generateur-fautif.py", "--verifier"]
                        return int(module.main())
                finally:
                    sys.argv = argv_reel

            self.assertEqual(lancer(0), 0, "le générateur fautif passe au jour réel, comme attendu")
            self.assertNotEqual(
                lancer(400),
                0,
                "le harnais ne détecte pas une sortie horodatée sur le jour : il est sans effet",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
