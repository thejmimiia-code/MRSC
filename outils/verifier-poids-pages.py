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
import os
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

#: Racine lue par le contrôle. La surcharge sert au banc de mutation
#: (`outils/test_mutations_poids_pages.py`), qui ajoute une image lourde ou
#: casse un `<picture>` dans une copie du dépôt.
ROOT = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
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
    # Ressources seulement demandées si le repli est nécessaire : elles ne
    # comptent pas dans le transfert typique, mais dans le pire cas.
    differes: list[tuple[int | None, Path]] = field(default_factory=list)
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

    def ajouter_candidats(self, slot: SlotImage, valeur: str, differes: bool = False) -> None:
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
                (slot.differes if differes else slot.candidats).append((largeur, cible))
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
            # `data-srcset` est une source différée : le navigateur ne la demande
            # que si le repli est nécessaire (WebGL absent, par exemple). Elle
            # compte quand même dans le poids estimé, parce qu'elle peut être
            # téléchargée : sous-compter une ressource conditionnelle ferait
            # croire à une page plus légère qu'elle ne peut l'être.
            if self.courante is not None and attributs.get("srcset"):
                self.ajouter_candidats(self.courante, attributs["srcset"])
            if self.courante is not None and attributs.get("data-srcset"):
                self.ajouter_candidats(self.courante, attributs["data-srcset"], differes=True)
        elif tag == "img":
            slot = self.courante if self.courante is not None else SlotImage()
            if attributs.get("srcset"):
                self.ajouter_candidats(slot, attributs["srcset"])
            if attributs.get("data-srcset"):
                self.ajouter_candidats(slot, attributs["data-srcset"], differes=True)
            if attributs.get("src"):
                cible = self.resoudre(attributs["src"])
                if cible:
                    slot.candidats.append((None, cible))
            if attributs.get("data-src"):
                cible = self.resoudre(attributs["data-src"])
                if cible:
                    slot.differes.append((None, cible))
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
    mobile_pire: set[Path] = set(mobile)
    bureau_pire: set[Path] = set(bureau)
    for slot in extracteur.images:
        petit = choisir(slot, plus_petit=True)
        grand = choisir(slot, plus_petit=False)
        if petit:
            mobile.add(petit)
        if grand:
            bureau.add(grand)
        deferes = slot.differes
        if deferes:
            def choisir_dans(pool, plus_petit):
                with_width = [(largeur, chemin) for largeur, chemin in pool if largeur is not None]
                retenus = with_width or pool
                clef = lambda item: item[0] if item[0] is not None else 0
                return (min if plus_petit else max)(retenus, key=clef)[1]
            mobile_pire.add(choisir_dans(deferes, True))
            bureau_pire.add(choisir_dans(deferes, False))
    html = page.stat().st_size
    gzip_html = compresser(page)
    poids = {}
    for nom, fichiers in (("mobile", mobile), ("bureau", bureau), ("mobile_pire", mobile_pire), ("bureau_pire", bureau_pire)):
        brut = html + sum(chemin.stat().st_size for chemin in fichiers)
        compresse = gzip_html + sum(compresser(chemin) for chemin in fichiers)
        poids[nom] = {"brut": brut, "gzip": compresse, "fichiers": fichiers}
    return {
        "page": page.relative_to(ROOT).as_posix(),
        "poids": poids,
        "differes": sorted({chemin.relative_to(ROOT).as_posix() for slot in extracteur.images for _, chemin in slot.differes}),
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
        "Le budget porte sur le **transfert typique**. Les images de repli marquées "
        "`data-srcset` ou `data-src` ne sont demandées que si le rendu 3D du "
        "navigateur est indisponible ; elles sont comptées à part et signalées "
        "en fin de contrôle, au lieu d’être ignorées.",
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
    # Le budget porte sur le transfert typique. Les ressources différées — les
    # images de repli, demandées seulement si WebGL est absent — sont mesurées
    # à part et affichées : une page peut légitimement dépasser le budget dans ce
    # cas-là, puisque le repli remplace un rendu qui ne fonctionne pas. Les
    # ignorer aurait été plus flatteur et moins vrai.
    pire_cas: list[tuple[str, float, float]] = []
    for mesure in pages:
        mobile = mesure["poids"]["mobile"]["gzip"] / 1024
        bureau = mesure["poids"]["bureau"]["gzip"] / 1024
        if mobile > options.budget_mobile:
            depassements.append(f"{mesure['page']} : {mobile:.1f} Kio mobile > {options.budget_mobile} Kio")
        if bureau > options.budget_desktop:
            depassements.append(f"{mesure['page']} : {bureau:.1f} Kio grand écran > {options.budget_desktop} Kio")
        if mesure["differes"]:
            pire_cas.append((
                mesure["page"],
                mesure["poids"]["mobile_pire"]["gzip"] / 1024,
                mesure["poids"]["bureau_pire"]["gzip"] / 1024,
            ))
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
    for page, mobile, bureau in sorted(pire_cas, key=lambda item: item[2], reverse=True)[:3]:
        print(
            f"  · {page} : replis différés compris, le pire cas serait de "
            f"{mobile:.1f} Kio mobile et {bureau:.1f} Kio grand écran "
            "(images demandées seulement si le rendu 3D est indisponible)."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
