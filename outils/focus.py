#!/usr/bin/env python3
"""Décide ce que vaut l'indicateur de focus, et refuse ce qui n'est pas mesuré.

`mesurer-focus.cjs` relève, dans un vrai navigateur, ce qui change quand une
personne parcourt la page à la touche Tab : le contour, l'ombre, le fond, la
bordure ou le texte qui apparaît, sa couleur, le fond adjacent et le rapport
WCAG calculé. Ce script ne mesure rien : il pose le seuil et il refuse.

**Le seuil, et d'où il vient.** WCAG 2.2 AA, critère 1.4.11 (contraste des
éléments non textuels) : l'indicateur de focus doit atteindre **3:1** contre les
couleurs adjacentes. 3,0:1 passe, 2,99:1 est refusé — la même exigence de
précision que les 0,5 px du cadrage : un seuil qu'on arrondit ne prouve rien.

**Ce que le refus signifie, et ce qu'il ne signifie pas.** Un élément dont
l'indicateur tombe sous 3:1 n'est pas « illisible » : il est plus difficile à
suivre au clavier pour qui voit mal. Un élément dont *rien* ne change au focus
est plus grave : c'est le critère 2.4.7 qui tombe. Le rapport ne tranche pas le
dessin — il nomme l'élément, l'indicateur, le rapport et le fond, et laisse la
décision de le changer à une personne.

**Les angles morts, nommés plutôt que tus.** Un élément posé sur une image n'a
pas de fond calculable : il est compté à part, jamais jugé. Un élément dont
l'apparence de focus n'est pas retrouvée après défocalisation n'est pas mesuré :
le script le dit, et ce script refuse — une sonde qui ne sait pas ce qu'elle
regarde doit le dire au lieu de rendre un chiffre.

Usage :
    python3 outils/focus.py --plan /tmp/focus-plan.json
    node outils/mesurer-focus.cjs /tmp/focus-plan.json /tmp/focus-rapport.json
    python3 outils/focus.py --controler /tmp/focus-plan.json /tmp/focus-rapport.json
    python3 outils/focus.py --resume /tmp/focus-rapport.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

#: Largeurs mesurées : téléphone courant et bureau. Deux suffisent ici parce que
#: ce qui change avec la largeur, c'est la place — et un indicateur de focus ne
#: dépend pas de la place. Le dire est plus honnête que de le laisser croire.
LARGEURS = (390, 1440)

#: Plafond d'éléments portés au focus par page et par largeur. Le plus long
#: parcours observé (`anglais-aventure.html`) compte 448 cibles ; en mesurer
#: soixante est un échantillon déclaré, pas une couverture — le rapport dit
#: quand la traversée s'est arrêtée au plafond.
LIMITE = 60

#: Seuil WCAG 2.2 AA, 1.4.11 (contraste des éléments non textuels).
SEUIL = 3.0


def charger_cadrages():
    """Importe `cadrages.py`, dont le nom porte un tiret."""
    spec = importlib.util.spec_from_file_location("cadrages", RACINE / "outils" / "cadrages.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cadrages"] = module
    spec.loader.exec_module(module)
    return module


def pages_publiees() -> tuple[str, ...]:
    """Les pages du site, lues sur le disque — jamais recopiées ici."""
    return charger_cadrages().pages_publiees()


def construire_plan(pages: tuple[str, ...], largeurs: tuple[int, ...], limite: int) -> dict:
    return {
        "pages": list(pages),
        "largeurs": list(largeurs),
        "limite": limite,
        "seuil": SEUIL,
        "note": (
            "Focus au clavier : deux largeurs, soixante éléments par page et par "
            "largeur par défaut. Un relevé arrêté au plafond le dit ; ce n'est "
            "pas une couverture exhaustive."
        ),
    }


def refuser(message: str, code: int = 1) -> int:
    print(message, file=sys.stderr)
    return code


def controler(plan: dict, rapport: dict) -> list[str]:
    """Les refus. Chacun nomme la page, la largeur, l'élément et le rapport."""
    refus: list[str] = []
    vues = {(page.get("page"), page.get("largeur")) for page in rapport.get("pages", [])}
    for nom_page in plan.get("pages", []):
        for largeur in plan.get("largeurs", []):
            if (nom_page, largeur) not in vues:
                refus.append(
                    f"{nom_page} · {largeur} px : aucun relevé — un cadrage non mesuré est une "
                    "erreur, pas un silence"
                )

    for page in rapport.get("pages", []):
        nom, largeur = page.get("page"), page.get("largeur")
        elements = page.get("elements")
        if not isinstance(elements, list) or not elements:
            refus.append(f"{nom} · {largeur} px : relevé vide — rien n'a été porté au focus")
            continue
        for element in elements:
            etiquette = f"{nom} · {largeur} px · {element.get('selecteur', '?')}"
            if element.get("retabli") is False:
                # Le focus rendu par `element.focus()` ne redonne pas l'apparence
                # que la touche Tab avait produite : l'apparence « au repos » n'est
                # alors pas comparable, et tout chiffre qui en sortirait serait faux.
                refus.append(
                    f"{etiquette} : apparence de focus non retrouvée après défocalisation — "
                    "la comparaison au repos n'est pas fiable, aucun rapport n'est rendu"
                )
                continue
            if element.get("fond_image"):
                continue  # compté par `resumer`, jamais jugé
            if element.get("indicateur") in (None, "aucun"):
                refus.append(
                    f"{etiquette} : aucun indicateur de focus — rien ne change à l'écran "
                    "(WCAG 2.4.7)"
                )
                continue
            contraste = element.get("contraste")
            if contraste is None:
                refus.append(
                    f"{etiquette} : indicateur « {element.get('indicateur')} » sans rapport "
                    "calculable — couleur ou fond illisible"
                )
                continue
            if contraste < SEUIL:
                refus.append(
                    f"{etiquette} : {element.get('indicateur')} à {contraste}:1 pour un seuil de "
                    f"{SEUIL}:1 (WCAG 2.2 AA, 1.4.11) — fond adjacent "
                    f"{couleur(element.get('fond'))}"
                )
    return refus


def couleur(valeur) -> str:
    if isinstance(valeur, dict):
        return f"rgb({valeur.get('r')}, {valeur.get('g')}, {valeur.get('b')})"
    return "inconnu"


def resumer(rapport: dict) -> str:
    elements = [element for page in rapport.get("pages", []) for element in page.get("elements", [])]
    mesures = [element for element in elements if not element.get("hors_liste")]
    sur_image = [element for element in mesures if element.get("fond_image")]
    sans_indicateur = [
        element for element in mesures if not element.get("fond_image") and element.get("indicateur") in (None, "aucun")
    ]
    jugeables = [
        element
        for element in mesures
        if not element.get("fond_image") and element.get("indicateur") not in (None, "aucun")
    ]
    sous_seuil = [element for element in jugeables if (element.get("contraste") or 0) < SEUIL]
    bornees = [page for page in rapport.get("pages", []) if page.get("borne")]
    return (
        f"Focus : {len(rapport.get('pages', []))} page(s) et largeur(s), {len(elements)} élément(s) "
        f"porté(s) au focus, {len(jugeables)} indicateur(s) jugé(s), {len(sous_seuil)} sous le seuil "
        f"de {SEUIL}:1, {len(sans_indicateur)} sans indicateur, {len(sur_image)} sur fond d'image "
        f"(non mesurables), {len(bornees)} relevé(s) arrêté(s) au plafond"
    )


def main() -> int:
    parseur = argparse.ArgumentParser(description="Plan, contrôle et résumé du focus au clavier.")
    parseur.add_argument("--plan", type=Path, help="écrit le plan de mesure")
    parseur.add_argument("--pages", nargs="*", help="pages à mesurer (défaut : toutes)")
    parseur.add_argument("--largeurs", default=",".join(str(v) for v in LARGEURS))
    parseur.add_argument("--limite", type=int, default=LIMITE)
    parseur.add_argument("--controler", nargs=2, metavar=("PLAN", "RAPPORT"))
    parseur.add_argument("--resume", type=Path)
    arguments = parseur.parse_args()

    if arguments.plan:
        pages = tuple(arguments.pages) if arguments.pages else pages_publiees()
        if not pages:
            return refuser("Aucune page publiée trouvée : le plan serait vide.", 2)
        largeurs = tuple(int(valeur) for valeur in arguments.largeurs.split(",") if valeur.strip())
        if not largeurs:
            return refuser("Aucune largeur : le plan ne dirait pas dans quel cadrage mesurer.", 2)
        plan = construire_plan(pages, largeurs, arguments.limite)
        arguments.plan.parent.mkdir(parents=True, exist_ok=True)
        arguments.plan.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(
            f"Plan du focus : {len(pages)} page(s) × {len(largeurs)} largeur(s), "
            f"{arguments.limite} élément(s) par relevé au plus → {arguments.plan}"
        )
        return 0

    if arguments.controler:
        chemin_plan, chemin_rapport = (Path(chemin) for chemin in arguments.controler)
        try:
            plan = json.loads(chemin_plan.read_text(encoding="utf-8"))
            rapport = json.loads(chemin_rapport.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            return refuser(f"Lecture impossible : {erreur} — aucune conclusion.", 2)
        refus = controler(plan, rapport)
        print(resumer(rapport))
        if refus:
            for ligne in refus:
                print(f"  - {ligne}", file=sys.stderr)
            print(f"Refusé : {len(refus)} constat(s).", file=sys.stderr)
            return 1
        return 0

    if arguments.resume:
        try:
            rapport = json.loads(arguments.resume.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            return refuser(f"Lecture impossible : {erreur}", 2)
        print(resumer(rapport))
        for page in rapport.get("pages", []):
            for element in page.get("elements", []):
                if element.get("fond_image"):
                    continue
                contraste = element.get("contraste")
                if element.get("indicateur") in (None, "aucun") or (contraste or 0) < SEUIL:
                    print(
                        f"  - {page['page']} · {page['largeur']} px · {element.get('selecteur')} : "
                        f"{element.get('indicateur')} {contraste} contre {SEUIL}:1"
                    )
        return 0

    parseur.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
