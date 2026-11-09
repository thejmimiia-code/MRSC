#!/usr/bin/env python3
"""Vérifie les six apparences proposées dans « Personnalisation ».

Le 7 novembre 2026, six thèmes sont ajoutés : les trois réglages les plus
courants sur le Web, puis trois palettes originales. Une apparence n'est pas
une couleur d'accent : c'est la promesse que **toutes** les surfaces, tous les
textes et toutes les bordures suivent. Ce contrôle vérifie mécaniquement :

1. les six choix, leur ordre et l'absence de nom d'œuvre ou de marque ;
2. que le bloc de fond sombre redéclare **chaque** jeton de couleur de `:root`
   (un jeton oublié laisserait du texte clair sur une carte restée claire) ;
3. le contraste WCAG des paires texte/fond pour chaque thème, accents compris ;
4. l'absence d'animation dans les décors — `prefers-reduced-motion` n'a donc
   rien à désactiver — et la reprise par les couleurs forcées du système ;
5. que la préférence est lue, écrite et synchronisée, et qu'aucune page HTML
   ne fige une apparence : la source reste `site.css` et `site.js`.

Il ne juge ni le goût des palettes, ni leur ressemblance avec une ambiance, ni
leur utilité : ces trois questions restent à une personne. Il ne mesure pas non
plus le rendu dans un navigateur ; `test-experience.cjs` et le relevé daté
`docs/rd/releve-apparences-2026-11-07.md` portent cette preuve-là.

Usage :
    python3 outils/verifier-apparences.py
    MRSC_RACINE=/tmp/copie python3 outils/verifier-apparences.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
CSS = RACINE / "assets" / "css" / "site.css"
JS = RACINE / "assets" / "js" / "site.js"

ORDRE_ATTENDU = ("systeme", "clair", "sombre", "bobine", "horizon", "arcade")
PALETTES_ORIGINALES = ("bobine", "horizon", "arcade")
#: Jetons qui gardent leur valeur sur fond sombre : ils sont déjà des surfaces
#: marines ou des premiers plans clairs prévus pour elles. La liste est fermée :
#: un jeton ajouté à `:root` et oublié ici fait échouer la porte, au lieu d'être
#: déclaré inchangé par complaisance. Ces 17 jetons ne sont pas recopiés dans le
#: bloc sombre, pour ne pas dupliquer un littéral que les contrôles d'intégration
#: comptent comme une seule occurrence.
INCHANGES = frozenset({
    "--navy", "--navy-alpha", "--navy-deep", "--navy-deep-2",
    "--on-navy", "--on-navy-border", "--on-navy-fill", "--on-navy-fill-2",
    "--on-navy-fill-strong", "--on-navy-green", "--on-navy-link",
    "--on-navy-pale", "--on-navy-sky", "--on-navy-text",
    "--on-navy-text-faint", "--on-navy-text-soft", "--white",
})
NOMS_PROTEGES = (
    "stranger things", "retour vers le futur", "back to the future",
    "ready player one", "player one", "oasis", "eleven", "marty mcfly",
)
#: Paires (texte, fond, seuil) : 4,5:1 pour du texte, 3:1 pour un repère d'UI.
PAIRES = (
    ("--ink", "--surface", 4.5),
    ("--muted", "--surface", 4.5),
    ("--blue", "--surface", 4.5),
    ("--on-accent", "--blue", 4.5),
    ("--on-navy", "--navy", 4.5),
    ("--code-text", "--code-surface", 4.5),
    ("--text-soft", "--blue-soft", 4.5),
    ("--gold-ink", "--tint-gold", 4.5),
    ("--gold", "--navy", 3.0),
)


def declarations(bloc: str) -> dict[str, str]:
    return {k: v.strip() for k, v in re.findall(r"^\s*(--[a-z0-9-]+):\s*([^;]+);", bloc, re.M)}


def bloc_css(texte: str, selecteur: str) -> str:
    """Corps de la première règle dont le sélecteur est exactement `selecteur`."""
    motif = re.compile(r"(?m)^" + re.escape(selecteur) + r"\s*\{(.*?)^\}", re.S)
    trouve = motif.search(texte)
    return trouve.group(1) if trouve else ""


def rgb(hexa: str) -> tuple[float, float, float]:
    valeur = hexa.lstrip("#")
    if len(valeur) == 3:
        valeur = "".join(c * 2 for c in valeur)
    return tuple(int(valeur[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def contraste(clair: str, fond: str) -> float:
    def luminance(couleur: str) -> float:
        canaux = []
        for valeur in rgb(couleur):
            # Seuil normatif 0.04045, pas 0.03928 : la définition W3C de la
            # luminance relative a été corrigée en mai 2021. Vérifié le
            # 7 novembre 2026 sur w3c/wcag (guidelines/terms/20/relative-luminance.html)
            # et consigné dans docs/rd/relecture-contenus.toml (source w3c-luminance).
            canaux.append(valeur / 12.92 if valeur <= 0.04045 else ((valeur + 0.055) / 1.055) ** 2.4)
        return 0.2126 * canaux[0] + 0.7152 * canaux[1] + 0.0722 * canaux[2]

    l1, l2 = luminance(clair), luminance(fond)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def resoudre(jetons: dict[str, str], valeur: str, profondeur: int = 0) -> str:
    if profondeur > 6:
        return valeur
    reference = re.fullmatch(r"var\((--[a-z0-9-]+)\)", valeur.strip())
    if reference and reference.group(1) in jetons:
        return resoudre(jetons, jetons[reference.group(1)], profondeur + 1)
    return valeur.strip()


def verifier() -> list[str]:
    erreurs: list[str] = []
    if not CSS.is_file() or not JS.is_file():
        return ["assets/css/site.css ou assets/js/site.js absent"]

    css = CSS.read_text(encoding="utf-8")
    js = JS.read_text(encoding="utf-8")

    # 1. Les six choix, dans l'ordre annoncé, avec un libellé et une description.
    tableau = re.search(r"(?s)const APPARENCES = \[(.*?)\n  \];", js)
    if not tableau:
        return ["site.js — le tableau APPARENCES a disparu"]
    entrees = re.findall(r'value: "([a-z-]+)", label: "([^"]+)",.*?description: "([^"]+)"', tableau.group(1), re.S)
    valeurs = tuple(e[0] for e in entrees)
    if valeurs != ORDRE_ATTENDU:
        erreurs.append(f"site.js — six apparences attendues dans cet ordre {ORDRE_ATTENDU}, lu {valeurs}")
    if any(not libelle.strip() or not description.strip() for _, libelle, description in entrees):
        erreurs.append("site.js — une apparence n'a plus de libellé ou de description lisible")
    for theme in PALETTES_ORIGINALES:
        if f'html[data-apparence="{theme}"]' not in css:
            erreurs.append(f"site.css — la palette « {theme} » n'a plus de règle d'accents")

    # 2. Aucun nom d'œuvre, de marque ou de personnage repris.
    for nom in NOMS_PROTEGES:
        if nom in css.casefold() or nom in js.casefold():
            erreurs.append(f"un nom protégé est réapparu (« {nom} ») : les palettes doivent rester originales")

    # 3. Le fond sombre reprend tous les jetons de couleur de :root.
    racine = declarations(bloc_css(css, ":root"))
    couleurs = {k: v for k, v in racine.items() if v.startswith("#") or v.startswith("rgba(")}
    sombre = declarations(bloc_css(css, 'html[data-apparence-fond="sombre"]'))
    if not sombre:
        erreurs.append("site.css — le bloc de fond sombre a disparu")
    non_declares = set(couleurs) - set(sombre)
    if non_declares != INCHANGES:
        oublies = sorted(non_declares - INCHANGES)
        en_trop = sorted(INCHANGES - non_declares)
        erreurs.append(
            "site.css — les jetons laissés inchangés ne sont plus exactement la liste fermée : "
            f"oublié(s) {', '.join(oublies[:8]) or 'aucun'} ; "
            f"déclaré(s) en trop {', '.join(en_trop[:8]) or 'aucun'}"
        )
    if re.search(r"color-scheme:\s*dark", bloc_css(css, 'html[data-apparence-fond="sombre"]')) is None:
        erreurs.append("site.css — le fond sombre n'annonce plus `color-scheme: dark`")
    if sombre.get("--on-accent", "").casefold() != "#0b1220":
        erreurs.append("site.css — `--on-accent` doit rester une encre sombre : le texte des boutons sur accent clair sinon")

    # 4. Contraste de chaque thème, après application des accents.
    for theme in ORDRE_ATTENDU:
        jetons = dict(racine)
        if theme not in ("systeme", "clair"):
            jetons.update(sombre)
        if theme in PALETTES_ORIGINALES:
            jetons.update(declarations(bloc_css(css, f'html[data-apparence="{theme}"]')))
        for texte, fond, seuil in PAIRES:
            if texte not in jetons or fond not in jetons:
                erreurs.append(f"{theme} — paire {texte}/{fond} absente des jetons")
                continue
            a, b = resoudre(jetons, jetons[texte]), resoudre(jetons, jetons[fond])
            if not (a.startswith("#") and b.startswith("#")):
                erreurs.append(f"{theme} — paire {texte}/{fond} non mesurable ({a} sur {b})")
                continue
            mesure = contraste(a, b)
            # W3C, Understanding 1.4.3 et 1.4.11 : les seuils 4,5:1 et 3:1 ne
            # doivent pas être arrondis (4,499:1 échoue). La tolérance de 0,01
            # d'origine laissait passer un contraste insuffisant ; seule une
            # marge de calcul à virgule flottante reste tolérée.
            if mesure + 1e-9 < seuil:
                erreurs.append(f"{theme} — {texte} sur {fond} : {mesure:.2f}:1 sous le seuil {seuil}:1")

    # 5. Décors statiques, couleurs forcées, contraste renforcé.
    for theme in PALETTES_ORIGINALES:
        decors = re.findall(
            r'(?ms)^html\[data-apparence="' + theme + r'"\] body \{(.*?)^\}', css
        )
        if not decors or "background-image" not in decors[0]:
            erreurs.append(f"site.css — le décor statique de « {theme} » a disparu")
        elif re.search(r"\banimation\b", decors[0]):
            erreurs.append(f"site.css — le décor de « {theme} » ajoute une animation : `prefers-reduced-motion` serait contourné")
    if "html[data-apparence] body { background-image: none !important; }" not in css:
        erreurs.append("site.css — les couleurs forcées ne neutralisent plus les décors")
    if "html.contraste-renforce[data-apparence] body" not in css:
        erreurs.append("site.css — le contraste renforcé ne neutralise plus les décors")

    # 6. Préférence : lecture, écriture, synchronisation et source partagée.
    for fragment, raison in (
        ('const CLE_APPARENCE = "mrsc-apparence";', "la clé de préférence"),
        ("savePreference(CLE_APPARENCE, choix)", "l'enregistrement du choix"),
        ("event.key === CLE_APPARENCE", "la synchronisation entre onglets"),
        ("(prefers-color-scheme: dark)", "le suivi du réglage système"),
        ("root.dataset.apparenceFond", "l'attribut de fond résolu"),
    ):
        if fragment not in js:
            erreurs.append(f"site.js — {raison} a disparu")
    pages = sorted(RACINE.glob("*.html")) + sorted((RACINE / "apprendre" / "fiches").glob("*.html"))
    figees = [p.name for p in pages if "data-apparence=" in p.read_text(encoding="utf-8")]
    if figees:
        erreurs.append(f"{len(figees)} page(s) figent une apparence dans leur HTML : {', '.join(figees[:5])}")

    return erreurs


if __name__ == "__main__":
    fautes = verifier()
    if fautes:
        for faute in fautes:
            print("ÉCHEC — " + faute, file=sys.stderr)
        print(f"{len(fautes)} faute(s) dans les apparences.", file=sys.stderr)
        sys.exit(1)
    print("OK — 6 apparences, tous les jetons de couleur suivis, contrastes mesurés, décors statiques, source unique.")
