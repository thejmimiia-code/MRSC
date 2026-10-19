#!/usr/bin/env python3
"""Imprime un état daté et vérifiable de la R&D, à partir des fichiers du dépôt.

Aucun réseau, aucune donnée personnelle. Le résultat sert de pièce jointe à un
brief de décision : il rappelle ce qui est réellement mesuré dans le dépôt, pas
ce qui est supposé.

    python3 outils/etat-rd.py
    python3 outils/etat-rd.py --date 2026-10-17

Les valeurs sont recalculées à chaque exécution ; le fichier n'est pas
versionné pour éviter qu'un instantané périmé soit pris pour l'état courant.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORTEFEUILLE = ROOT / "docs" / "rd" / "portefeuille.toml"
CATALOGUE = ROOT / "docs" / "apprentissage" / "catalogue.toml"
JOURNAL = ROOT / "docs" / "rd" / "journal.md"
POIDS = ROOT / "docs" / "rd" / "poids-pages.md"


def lire_toml(chemin: Path) -> dict:
    with chemin.open("rb") as fichier:
        return tomllib.load(fichier)


def etat_portefeuille() -> dict:
    donnees = lire_toml(PORTEFEUILLE)
    initiatives = donnees.get("initiative", [])
    meta = donnees.get("meta", {})
    par_etat: dict[str, int] = {}
    for initiative in initiatives:
        etat = initiative.get("etat", "?")
        par_etat[etat] = par_etat.get(etat, 0) + 1
    p0 = [initiative["id"] for initiative in initiatives if initiative.get("priorite") == "P0"]
    revue = meta.get("derniere_revue")
    cadence = meta.get("cadence_revue_jours")
    echeance = None
    if isinstance(revue, dt.date) and isinstance(cadence, int):
        echeance = revue + dt.timedelta(days=cadence)
    return {
        "total": len(initiatives),
        "par_etat": par_etat,
        "p0": p0,
        "echeance": echeance,
    }


def etat_catalogue(date_reference: dt.date) -> dict:
    fiches = lire_toml(CATALOGUE).get("fiche", [])
    prototypes = sum(1 for fiche in fiches if fiche.get("statut_editorial") == "Prototype à relire")
    echeances: list[tuple[dt.date, str]] = []
    for fiche in fiches:
        revue = fiche.get("revue_le")
        intervalle = fiche.get("intervalle_revue_jours")
        if not revue or not isinstance(intervalle, int):
            continue
        try:
            prochaine = dt.date.fromisoformat(revue) + dt.timedelta(days=intervalle)
        except ValueError:
            continue
        echeances.append((prochaine, fiche.get("id", "?")))
    echues = [item for item in echeances if item[0] < date_reference]
    prochaines = sorted(item for item in echeances if item[0] >= date_reference)
    return {
        "total": len(fiches),
        "prototypes": prototypes,
        "initiales": len(fiches) - prototypes,
        "echues": len(echues),
        "prochaine": prochaines[0] if prochaines else None,
    }


def etat_journal() -> dt.date | None:
    if not JOURNAL.is_file():
        return None
    for ligne in JOURNAL.read_text(encoding="utf-8").splitlines():
        correspondance = re.match(r"^## (\d{4}-\d{2}-\d{2})", ligne)
        if correspondance:
            return dt.date.fromisoformat(correspondance.group(1))
    return None


def etat_poids() -> dict | None:
    if not POIDS.is_file():
        return None
    lignes = POIDS.read_text(encoding="utf-8").splitlines()
    pages = 0
    pire_mobile = (0.0, "")
    pire_ecran = (0.0, "")
    for ligne in lignes:
        colonnes = [colonne.strip() for colonne in ligne.strip().strip("|").split("|")]
        if len(colonnes) != 4 or not colonnes[0].startswith("`"):
            continue
        try:
            mobile = float(colonnes[1])
            ecran = float(colonnes[2])
        except ValueError:
            continue
        pages += 1
        nom = colonnes[0].strip("`")
        if mobile > pire_mobile[0]:
            pire_mobile = (mobile, nom)
        if ecran > pire_ecran[0]:
            pire_ecran = (ecran, nom)
    if not pages:
        return None
    return {"pages": pages, "mobile": pire_mobile, "ecran": pire_ecran}


def commit_court() -> str:
    try:
        resultat = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return "inconnu"
    return resultat.stdout.strip() or "inconnu"


def principal() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument(
        "--date",
        type=dt.date.fromisoformat,
        default=dt.date.today(),
        help="Date de référence (AAAA-MM-JJ), par défaut aujourd'hui",
    )
    options = analyseur.parse_args()

    portefeuille = etat_portefeuille()
    catalogue = etat_catalogue(options.date)
    journal = etat_journal()
    poids = etat_poids()

    print(f"# État R&D au {options.date.isoformat()}\n")
    print(f"Commit de référence : `{commit_court()}`. Valeurs recalculées depuis les fichiers du dépôt.\n")
    print("| Indicateur | Valeur | Source |")
    print("| --- | --- | --- |")
    etats = ", ".join(f"{etat} : {nombre}" for etat, nombre in sorted(portefeuille["par_etat"].items()))
    print(f"| Initiatives R&D | {portefeuille['total']} ({etats}) | `docs/rd/portefeuille.toml` |")
    print(f"| Priorité P0 | {len(portefeuille['p0'])} : {', '.join(portefeuille['p0'])} | Portefeuille |")
    if portefeuille["echeance"]:
        reste = (portefeuille["echeance"] - options.date).days
        mention = "échue" if reste < 0 else f"dans {reste} jour(s)"
        print(f"| Revue du portefeuille | {portefeuille['echeance'].isoformat()} ({mention}) | Portefeuille |")
    print(f"| Fiches publiées | {catalogue['total']} | `docs/apprentissage/catalogue.toml` |")
    print(f"| Dont prototypes à relire | {catalogue['prototypes']} | Statuts du catalogue |")
    print(f"| Fiches dont la revue est échue | {catalogue['echues']} | Dates `revue_le` + intervalle |")
    if catalogue["prochaine"]:
        prochaine_date, prochaine_id = catalogue["prochaine"]
        print(f"| Prochaine revue de fiche | {prochaine_date.isoformat()} (`{prochaine_id}`) | Catalogue |")
    if journal:
        anciennete = (options.date - journal).days
        print(f"| Dernière entrée de journal | {journal.isoformat()} ({anciennete} jour(s)) | `docs/rd/journal.md` |")
    if poids:
        print(
            f"| Pages mesurées | {poids['pages']} | `docs/rd/poids-pages.md` |"
        )
        print(
            f"| Page la plus lourde, mobile | {poids['mobile'][0]:.1f} Kio (`{poids['mobile'][1]}`) | Estimation gzip |"
        )
        print(
            f"| Page la plus lourde, grand écran | {poids['ecran'][0]:.1f} Kio (`{poids['ecran'][1]}`) | Estimation gzip |"
        )

    print("\n**Ce que ces chiffres ne mesurent pas :** la qualité éditoriale, l’effet d’apprentissage, l’usage réel, la performance réseau ou une empreinte carbone. Un compte de fiches n’est pas un indicateur de couverture suffisante.")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
