#!/usr/bin/env python3
"""Décide ce que vaut l'arbre d'accessibilité d'une page, et refuse ce qui manque.

`mesurer-arbre-accessibilite.cjs` relève, dans un vrai Chromium, ce que la page
**expose** aux technologies d'assistance : rôles, noms accessibles, niveaux de
titres, repères, listes, zones vivantes, cadres. Ce script ne mesure rien : il
pose les règles et il refuse.

**Pourquoi ce contrôle existe.** Le dépôt mesurait déjà les contrastes, le
focus, la taille des cibles et l'espacement du texte. Aucune de ces mesures ne
dit ce qu'un lecteur d'écran reçoit : une cible peut être nommée dans le HTML et
annoncée sans nom, un `ul` peut porter des puces et perdre sa sémantique dans un
autre moteur, une image `alt=""` peut rester exposée. Le 13 novembre 2026, ces
trois cas n'étaient mesurés nulle part.

**Ce que le refus signifie, et ce qu'il ne signifie pas.** Un refus nomme la
page et l'élément : il ne dit pas que la page est inaccessible, il dit qu'une
information manque là où une technologie d'assistance la cherche. L'inverse
n'est pas vrai non plus — un arbre propre ne rend pas une page compréhensible.

**Les règles, et d'où elles viennent.** WCAG 2.2 AA : 1.3.1 (information et
relations), 2.4.1 (contournement de blocs), 2.4.6 (titres et étiquettes), 3.1.1
(langue de la page), 4.1.2 (nom, rôle, valeur). Deux règles sont **préventives**
et le disent : la sémantique de liste sous `list-style: none` (WebKit la retire,
ce relevé mesure Chromium) et la langue des passages en langue étrangère (le
détecter demanderait une analyse linguistique, hors de portée ici).

Usage :
    python3 outils/arbre-accessibilite.py --plan /tmp/arbre-plan.json
    node outils/mesurer-arbre-accessibilite.cjs /tmp/arbre-plan.json /tmp/arbre-rapport.json
    python3 outils/arbre-accessibilite.py --controler /tmp/arbre-rapport.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def refuser(message: str, code: int = 1) -> int:
    print(message, file=sys.stderr)
    return code


#: Dossiers qui ne contiennent pas de page publiée : outils, documentation,
#: ressources, et la sortie des générateurs d'API.
DOSSIERS_HORS_SITE = ("docs", "outils", "assets", "api", "node_modules", ".git")


def pages_publiees(racine: Path = RACINE) -> tuple[str, ...]:
    """Toutes les pages du site, lues sur le disque — jamais recopiées ici.

    Plus large que `cadrages.pages_publiees`, qui ne prend que la racine : les
    108 fiches de `apprendre/` et le simulateur bâti sont publiés eux aussi, et
    une fiche sans titre exposé est aussi gênante qu'une page d'accueil sans
    repère. Le 13 novembre 2026, aucune mesure d'arbre ne les visitait.
    """
    pages = []
    for chemin in racine.rglob("*.html"):
        relatif = chemin.relative_to(racine)
        if relatif.parts[0] in DOSSIERS_HORS_SITE:
            continue
        pages.append(relatif.as_posix())
    return tuple(sorted(pages))


def construire_plan(pages: tuple[str, ...], largeur: int) -> dict:
    return {
        "pages": list(pages),
        "largeur": largeur,
        "note": (
            "Arbre d'accessibilité de Chromium, une largeur. Ce que le navigateur "
            "expose aux technologies d'assistance ; ni compréhension, ni ordre de "
            "lecture, ni autre moteur."
        ),
    }


def controler(rapport: dict) -> tuple[list[str], list[str]]:
    """Les refus, et les constats qui n'en sont pas.

    Un refus est une information manquante là où une technologie d'assistance la
    cherche. Un constat est un fait relevé qu'aucune règle ne tranche ici — une
    zone vivante vide, une langue étrangère déclarée : les compter comme fautes
    reviendrait à inventer un défaut.
    """
    refus: list[str] = []
    constats: list[str] = []
    pages = rapport.get("pages", [])
    if not pages:
        return (["aucune page mesurée : un contrôle vide ne vaut pas un contrôle"], constats)
    for erreur in rapport.get("erreurs", []):
        refus.append(f"{erreur.get('page')} : mesure impossible — {erreur.get('raison')}")

    for page in pages:
        nom = page.get("page")
        if not (page.get("langue") or "").strip():
            refus.append(f"{nom} : `lang` absent de `<html>` — la langue de la page n'est pas annoncée")

        titres = page.get("titres") or []
        if not titres:
            refus.append(f"{nom} : aucun titre exposé — la page ne se parcourt pas par titres")
        niveaux = [titre.get("niveau") for titre in titres if titre.get("niveau")]
        if niveaux.count(1) > 1:
            refus.append(f"{nom} : {niveaux.count(1)} titres de niveau 1 — un seul h1 par page")
        if niveaux and 1 not in niveaux:
            refus.append(f"{nom} : aucun titre de niveau 1 parmi {len(niveaux)} titres")
        for avant, apres, titre in zip(niveaux, niveaux[1:], titres[1:]):
            if apres - avant > 1:
                refus.append(
                    f"{nom} : titre de niveau {apres} après un niveau {avant} "
                    f"(« {titre.get('texte') or 'sans texte'} ») — niveau sauté"
                )

        reperes = page.get("reperes") or []
        principaux = [repere for repere in reperes if repere.get("role") == "main"]
        if len(principaux) != 1:
            refus.append(f"{nom} : {len(principaux)} repère(s) `main` — il en faut exactement un")
        for role in ("banner", "contentinfo"):
            compte = len([repere for repere in reperes if repere.get("role") == role])
            if compte > 1:
                refus.append(f"{nom} : {compte} repères `{role}` — un seul est identifiable")

        vus: dict[tuple[str, str], int] = {}
        for repere in reperes:
            cle = (str(repere.get("role")), (repere.get("nom") or "").strip())
            vus[cle] = vus.get(cle, 0) + 1
        for (role, nom_repere), compte in vus.items():
            if compte > 1 and role in ("navigation", "complementary", "region", "form", "search"):
                etiquette = f"« {nom_repere} »" if nom_repere else "sans nom"
                refus.append(
                    f"{nom} : {compte} repères `{role}` {etiquette} — "
                    "des repères de même rôle doivent se distinguer par leur nom"
                )

        for element in page.get("noms_vides") or []:
            if isinstance(element, dict):
                refus.append(
                    f"{nom} : {element.get('role')} sans nom accessible "
                    f"({element.get('element') or 'élément inconnu'}) — annoncé sans étiquette"
                )
            else:
                refus.append(f"{nom} : {element} sans nom accessible — annoncé sans étiquette")

        images = page.get("images") or {}
        if images.get("sans_alt"):
            refus.append(
                f"{nom} : {images['sans_alt']} image(s) sans attribut `alt` — "
                "ni informative, ni déclarée décorative"
            )
        exposees_vides = [nom_image for nom_image in (images.get("exposees") or []) if not nom_image]
        if exposees_vides:
            refus.append(
                f"{nom} : {len(exposees_vides)} image(s) exposée(s) sans nom — "
                "une image décorative doit sortir de l'arbre, une informative doit être nommée"
            )

        for cadre in page.get("cadres") or []:
            if not cadre:
                refus.append(f"{nom} : cadre sans nom accessible — le lecteur annonce « cadre »")

        for zone in page.get("zones_vivantes") or []:
            if zone.get("masquee"):
                refus.append(
                    f"{nom} : zone vivante masquée (`{zone.get('element')}`) — "
                    "une annonce dans un sous-arbre caché n'arrive pas"
                )
            elif zone.get("vide"):
                constats.append(
                    f"{nom} : zone vivante vide (`{zone.get('element')}`, {zone.get('politesse')}) — "
                    "légitime si elle se remplit, à relire si elle reste vide"
                )

        listes = page.get("listes") or {}
        sans_role = listes.get("sans_role") or 0
        if sans_role:
            # Refus, et non constat, depuis que le site est à zéro : 397 listes
            # portaient encore ce défaut le 13 novembre 2026 au matin. La règle
            # est **préventive** dans Chromium — il garde la sémantique de liste
            # même sans puces — et réelle dans WebKit, qui la retire. Refuser
            # ici n'est donc pas mesurer un défaut : c'est refuser de le
            # réintroduire dans le seul moteur que ce relevé ne visite pas.
            refus.append(
                f"{nom} : {sans_role} liste(s) sans puces et sans `role=\"list\"` — "
                "WebKit retire alors la sémantique de liste (préventif, non mesuré ici)"
            )
        if listes.get("document") and not listes.get("exposees"):
            refus.append(
                f"{nom} : {listes['document']} liste(s) dans le document, aucune exposée — "
                "l'arbre ne rend pas la structure des listes"
            )

        for langue in page.get("langues_declarees") or []:
            constats.append(
                f"{nom} : passage déclaré en `{langue.get('langue')}` (`{langue.get('element')}`) — "
                "non vérifié : ce relevé ne juge pas la langue du texte"
            )

    return refus, constats


def resumer(rapport: dict) -> str:
    pages = rapport.get("pages", [])
    titres = sum(len(page.get("titres") or []) for page in pages)
    interactifs = sum(int(page.get("interactifs") or 0) for page in pages)
    reperes = sum(len(page.get("reperes") or []) for page in pages)
    sans_nom = sum(len(page.get("noms_vides") or []) for page in pages)
    return (
        f"Arbre d'accessibilité : {len(pages)} page(s), {titres} titre(s) exposé(s), "
        f"{reperes} repère(s), {interactifs} cible(s) interactive(s) dont {sans_nom} sans nom, "
        f"{rapport.get('navigateur') or 'navigateur inconnu'} — mesure, pas audit."
    )


def main() -> int:
    parseur = argparse.ArgumentParser(description="Plan, contrôle et résumé de l'arbre d'accessibilité.")
    parseur.add_argument("--plan", type=Path, help="écrit le plan de mesure")
    parseur.add_argument("--pages", nargs="*", help="pages à mesurer (défaut : toutes)")
    parseur.add_argument("--largeur", type=int, default=1280)
    parseur.add_argument("--controler", type=Path, metavar="RAPPORT")
    parseur.add_argument("--resume", type=Path)
    arguments = parseur.parse_args()

    if arguments.plan:
        pages = tuple(arguments.pages) if arguments.pages else pages_publiees()
        if not pages:
            return refuser("Aucune page publiée trouvée : le plan serait vide.", 2)
        plan = construire_plan(pages, arguments.largeur)
        arguments.plan.parent.mkdir(parents=True, exist_ok=True)
        arguments.plan.write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Plan de l'arbre d'accessibilité : {len(pages)} page(s) à {arguments.largeur} px → {arguments.plan}")
        return 0

    if arguments.controler:
        try:
            rapport = json.loads(arguments.controler.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            return refuser(f"Lecture impossible ({arguments.controler}) : {erreur} — aucune conclusion.", 2)
        refus, constats = controler(rapport)
        print(resumer(rapport))
        for constat in constats:
            print(f"  · {constat}")
        if refus:
            for ligne in refus:
                print(f"  ! {ligne}", file=sys.stderr)
            print(f"Refusé : {len(refus)} constat(s).", file=sys.stderr)
            return 1
        print(f"Accord : 0 refus, {len(constats)} constat(s) non tranché(s).")
        return 0

    if arguments.resume:
        try:
            rapport = json.loads(arguments.resume.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            return refuser(f"Lecture impossible ({arguments.resume}) : {erreur}", 2)
        print(resumer(rapport))
        for page in rapport.get("pages", []):
            print(
                f"  {page.get('page')} : {len(page.get('titres') or [])} titre(s), "
                f"{len(page.get('reperes') or [])} repère(s), "
                f"{len(page.get('noms_vides') or [])} cible(s) sans nom"
            )
        return 0

    parseur.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
