#!/usr/bin/env python3
"""Estime le poids des pages publiques et vérifie un budget de sobriété.

Le calcul est hors ligne : il additionne le HTML, les feuilles de style, les
scripts et les images locales que le navigateur demanderait, puis compresse
chaque fichier avec gzip pour approcher le transfert. Il ne mesure ni le réseau,
ni le cache, ni le rendu, ni la consommation énergétique, et ne remplace pas un
audit RGESN, Lighthouse ou une mesure sur appareil réel.

    python3 outils/verifier-poids-pages.py
    python3 outils/verifier-poids-pages.py --rapport docs/rd/poids-pages.md
    python3 outils/verifier-poids-pages.py --budget-mobile 300 --budget-desktop 450

Deux scénarios sont estimés pour chaque page : le plus petit candidat d’image
(téléphone en 1× ou 2× selon `sizes`) et le plus grand (grand écran en 2×). Les
icônes d’installation, les polices distantes et les médias chargés après une
action volontaire ne sont pas comptés.
"""

from __future__ import annotations

import argparse
import gzip
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob("*.html"))
PAGES.extend(sorted((ROOT / "apprendre" / "fiches").glob("*.html")))
PAGES.append(ROOT / "simulateur" / "index.html")
PAGES = [page for page in PAGES if page.is_file()]

# Seuils de travail, pas une norme : ils doivent rester discutés et révisés
# avec les mesures et les retours d’usage.
BUDGET_MOBILE_KIO = 300
BUDGET_DESKTOP_KIO = 450
ALERTE_RATIO = 0.8


@dataclass
class SlotImage:
    """Une image affichée une fois, avec ses candidats srcset locaux."""

    candidats: list[tuple[int | None, Path]] = field(default_factory=list)
    externe: bool = False
    repli_differe: bool = False


class ExtracteurRessources(HTMLParser):
    def __init__(self, page: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.page = page
        self.styles: set[Path] = set()
        self.scripts: set[Path] = set()
        self.images: list[SlotImage] = []
        self.pictures: list[SlotImage] = []
        self.courante: SlotImage | None = None
        self.manquantes: set[str] = set()
        self.externes: set[str] = set()
        self.picture_sans_source: list[str] = []

    def resoudre(self, url: str) -> Path | None:
        url = url.strip()
        if not url or url.startswith(("http://", "https://", "//", "data:", "mailto:", "tel:", "#")):
            return None
        cible = (self.page.parent / url.split("?", 1)[0].split("#", 1)[0]).resolve()
        if not cible.is_file():
            self.manquantes.add(url)
            return None
        return cible

    def ajouter_candidats(self, slot: SlotImage, valeur: str) -> None:
        for candidat in valeur.split(","):
            morceaux = candidat.strip().split()
            if not morceaux:
                continue
            url = morceaux[0]
            largeur: int | None = None
            if len(morceaux) > 1 and morceaux[1].endswith("w") and morceaux[1][:-1].isdigit():
                largeur = int(morceaux[1][:-1])
            cible = self.resoudre(url)
            if cible:
                slot.candidats.append((largeur, cible))
            elif url.startswith(("http://", "https://", "//")):
                slot.externe = True
                self.externes.add(url)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributs = dict(attrs)
        if tag == "link":
            relations = set((attributs.get("rel") or "").lower().split())
            if "stylesheet" in relations:
                cible = self.resoudre(attributs.get("href") or "")
                if cible:
                    self.styles.add(cible)
        elif tag == "script":
            if attributs.get("src"):
                cible = self.resoudre(attributs["src"])
                if cible:
                    self.scripts.add(cible)
        elif tag == "picture":
            self.courante = SlotImage()
            self.pictures.append(self.courante)
        elif tag == "source":
            if self.courante is not None and attributs.get("srcset"):
                self.ajouter_candidats(self.courante, attributs["srcset"])
        elif tag == "img":
            slot = self.courante if self.courante is not None else SlotImage()
            if attributs.get("srcset"):
                self.ajouter_candidats(slot, attributs["srcset"])
            if attributs.get("src"):
                cible = self.resoudre(attributs["src"])
                if cible:
                    slot.candidats.append((None, cible))
            if attributs.get("data-src") or attributs.get("data-srcset"):
                slot.repli_differe = True
            self.images.append(slot)
            if self.courante is not None:
                if not slot.candidats and not slot.repli_differe:
                    self.picture_sans_source.append(attributs.get("alt", ""))
                self.courante = None

    def close(self) -> None:
        super().close()
        if self.courante is not None and self.courante.candidats:
            # Une image reste prioritaire sur un <picture> incomplet.
            self.images.append(self.courante)
            self.courante = None


def compresser(chemin: Path) -> int:
    return len(gzip.compress(chemin.read_bytes(), 9))


def choisir(slot: SlotImage, plus_petit: bool) -> Path | None:
    if not slot.candidats:
        return None
    with_width = [(largeur, chemin) for largeur, chemin in slot.candidats if largeur is not None]
    pool = with_width or slot.candidats
    if plus_petit:
        return min(pool, key=lambda item: item[0] if item[0] is not None else 0)[1]
    return max(pool, key=lambda item: item[0] if item[0] is not None else 0)[1]


def mesurer(page: Path) -> dict:
    extracteur = ExtracteurRessources(page)
    extracteur.feed(page.read_text(encoding="utf-8"))
    extracteur.close()
    mobile: set[Path] = set(extracteur.styles) | set(extracteur.scripts)
    bureau: set[Path] = set(extracteur.styles) | set(extracteur.scripts)
    for slot in extracteur.images:
        petit = choisir(slot, plus_petit=True)
        grand = choisir(slot, plus_petit=False)
        if petit:
            mobile.add(petit)
        if grand:
            bureau.add(grand)
    html = page.stat().st_size
    gzip_html = compresser(page)
    poids = {}
    for nom, fichiers in (("mobile", mobile), ("bureau", bureau)):
        brut = html + sum(chemin.stat().st_size for chemin in fichiers)
        compresse = gzip_html + sum(compresser(chemin) for chemin in fichiers)
        poids[nom] = {"brut": brut, "gzip": compresse, "fichiers": fichiers}
    return {
        "page": page.relative_to(ROOT).as_posix(),
        "poids": poids,
        "manquantes": extracteur.manquantes,
        "externes": extracteur.externes,
        "picture_sans_source": extracteur.picture_sans_source,
    }


def controler_pictures(pages: list[dict]) -> list[str]:
    erreurs: list[str] = []
    for mesure in pages:
        if mesure["manquantes"]:
            erreurs.append(
                f"{mesure['page']} : ressource locale absente — " + ", ".join(sorted(mesure["manquantes"]))
            )
        if mesure["picture_sans_source"]:
            erreurs.append(
                f"{mesure['page']} : <picture> sans image de repli — l’alternative JPEG est requise"
            )
    return erreurs


def rapport_markdown(pages: list[dict], budget_mobile: int, budget_desktop: int) -> str:
    lignes = [
        "# Poids estimé des pages publiques",
        "",
        "Estimation hors ligne : HTML, CSS, JavaScript et image retenue pour chaque page, "
        "compressés avec gzip. Elle ne mesure ni le réseau, ni le cache, ni le rendu.",
        "",
        f"Budget de travail : {budget_mobile} Kio (mobile) et {budget_desktop} Kio (grand écran) compressés.",
        "",
        "| Page | Mobile (Kio gzip) | Grand écran (Kio gzip) | Brut maximal (Kio) |",
        "| --- | ---: | ---: | ---: |",
    ]
    for mesure in sorted(pages, key=lambda item: item["poids"]["bureau"]["gzip"], reverse=True):
        lignes.append(
            f"| `{mesure['page']}` | {mesure['poids']['mobile']['gzip'] / 1024:.1f} "
            f"| {mesure['poids']['bureau']['gzip'] / 1024:.1f} "
            f"| {max(item['brut'] for item in mesure['poids'].values()) / 1024:.1f} |"
        )
    return "\n".join(lignes) + "\n"


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--rapport", type=Path, help="écrire un rapport Markdown à ce chemin")
    analyseur.add_argument("--budget-mobile", type=int, default=BUDGET_MOBILE_KIO, help="Kio gzip, scénario mobile")
    analyseur.add_argument("--budget-desktop", type=int, default=BUDGET_DESKTOP_KIO, help="Kio gzip, grand écran")
    options = analyseur.parse_args()

    if not PAGES:
        print("ÉCHEC — aucune page publique trouvée.", file=sys.stderr)
        return 1
    pages = [mesurer(page) for page in PAGES]
    erreurs = controler_pictures(pages)
    depassements = []
    for mesure in pages:
        mobile = mesure["poids"]["mobile"]["gzip"] / 1024
        bureau = mesure["poids"]["bureau"]["gzip"] / 1024
        if mobile > options.budget_mobile:
            depassements.append(f"{mesure['page']} : {mobile:.1f} Kio mobile > {options.budget_mobile} Kio")
        if bureau > options.budget_desktop:
            depassements.append(f"{mesure['page']} : {bureau:.1f} Kio grand écran > {options.budget_desktop} Kio")
    erreurs.extend(depassements)

    if options.rapport:
        destination = options.rapport if options.rapport.is_absolute() else ROOT / options.rapport
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            rapport_markdown(pages, options.budget_mobile, options.budget_desktop), encoding="utf-8"
        )

    for mesure in sorted(pages, key=lambda item: item["poids"]["bureau"]["gzip"], reverse=True)[:8]:
        mobile = mesure["poids"]["mobile"]["gzip"] / 1024
        bureau = mesure["poids"]["bureau"]["gzip"] / 1024
        alerte = ""
        if mobile > options.budget_mobile * ALERTE_RATIO or bureau > options.budget_desktop * ALERTE_RATIO:
            alerte = "  ← proche du budget"
        print(f"{mesure['page']:<40} {mobile:7.1f} Kio mobile  {bureau:7.1f} Kio grand écran{alerte}")

    if erreurs:
        for erreur in erreurs:
            print(f"ÉCHEC — {erreur}", file=sys.stderr)
        return 1
    print(
        f"Poids des pages : {len(pages)} pages sous les budgets de travail "
        f"({options.budget_mobile} Kio mobile, {options.budget_desktop} Kio grand écran, gzip estimé)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
