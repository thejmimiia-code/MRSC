#!/usr/bin/env python3
"""Confronte le dessin au pixel près dans **tous** les cadrages personnalisés.

La promesse du site est que la mise en page suit l'espace disponible, jamais une
largeur d'écran supposée. Cette promesse n'était vérifiée que dans un seul
cadrage : présentation par défaut, trois tailles de texte, aucune densité. Or le
panneau de personnalisation en propose six présentations (`Lecture`,
`Panorama`, `Vitrine`, `Compacte`, `Mosaïque`) et cinq crans de texte de 75 à
130 %, et `--content` comme les gouttières changent avec eux.

Deux fautes y sont mesurées, et une seule suffit à refuser :

- **le débordement horizontal** — le document doit tenir exactement dans la
  fenêtre, au pixel déclaré près (`tolerance_px`, 0,5 px par défaut : un demi-
  pixel est le plus petit écart qu'un navigateur puisse produire en arrondissant
  une longueur) ;
- **le nombre de colonnes** — chaque grille déclarée dans
  `docs/rd/grilles-dynamiques.toml` doit montrer exactement ce que la feuille
  promet dans ce cadrage-là, pas ce qu'elle montre par défaut.

Le plan est écrit par `--releve-json`, mesuré par `outils/mesurer-cadrages.cjs`,
puis confronté par `--controler`. Un cadrage non mesuré est une **erreur**, pas
un silence : un contrôle incomplet ne vaut pas un contrôle vide.

Usage :
    python3 outils/cadrages.py --releve-json /tmp/plan.json
    node outils/mesurer-cadrages.cjs /tmp/plan.json /tmp/rapport.json
    python3 outils/cadrages.py --controler /tmp/plan.json /tmp/rapport.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
REGISTRE = "docs/rd/grilles-dynamiques.toml"
# Le registre écrit : dimensions balayées, tolérance, coût. Aucun outil ne
# l'applique — il documente — mais `test_cadrages.py` le confronte au plan,
# sinon il annoncerait éternellement le coût du lot précédent.
REGISTRE_CADRAGES = "docs/rd/cadrages.toml"
FEUILLE = "assets/css/site.css"

#: Les présentations du panneau de personnalisation, avec le nom que le
#: document porte (`data-layout`) et celui que le registre emploie. `None` est la
#: présentation par défaut, celle qui n'écrit aucun `data-layout`.
PRESENTATIONS = (None, "vitrine", "panorama", "compacte", "mosaique", "lecture")

#: Les crans de texte réellement proposés par `site.js` (`textLevels`), ramenés à
#: une échelle. Le cran 100 % vaut 1 : c'est la référence des feuilles.
ECHELLES = {75: 0.75, 85: 0.85, 100: 1.0, 115: 1.15, 130: 1.3}

def pages_publiees(racine: Path = RACINE) -> tuple[str, ...]:
    """Toutes les pages du site, lues sur le disque et non recopiées ici.

    Le 2 novembre 2026, le contrôle ne visitait que quatre pages — une par
    famille de dessin. Neuf pages publiées n'étaient donc confrontées à aucun
    cadrage : un débordement qui n'aurait touché que `documents.html` serait
    passé inaperçu, et la limite était écrite noir sur blanc dans le registre.
    Une liste écrite à la main aurait vieilli de la même façon ; elle est donc
    dérivée, et le registre est confronté à elle par `test_cadrages.py`.
    """
    return tuple(sorted(chemin.name for chemin in racine.glob("*.html")))


#: Toutes les pages publiées, une par fichier à la racine du site.
PAGES = pages_publiees()

#: Quatre largeurs qui encadrent les seuils de la feuille : téléphone étroit,
#: téléphone courant, tablette (le seuil de 760 px et sa gouttière) et bureau.
LARGEURS = (320, 390, 768, 1440)


def charger_modele():
    """Importe `modele-grilles.py`, dont le nom porte un tiret."""
    spec = importlib.util.spec_from_file_location("modele_grilles", RACINE / "outils" / "modele-grilles.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["modele_grilles"] = module
    spec.loader.exec_module(module)
    return module


def lire_registre(chemin: Path) -> dict:
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        raise SystemExit(f"Registre illisible ({chemin}) : {erreur}")


def construire_plan(modele, registre: dict, feuille: str) -> dict:
    """Ce que la feuille promet, cadrage par cadrage, grille par grille."""
    grilles = modele.lire_grilles(feuille)
    capacites = modele.lire_capacites(
        modele.RACINE, [e.get("selecteur") or "" for e in registre.get("grille", [])]
    )
    modele.appliquer_capacites(grilles, capacites)
    trouvees = modele.presentations_lues(grilles, feuille)
    contenus = modele.contenu_des_presentations(feuille)
    pages = modele.pages_des_grilles(modele.RACINE, list(grilles))
    entrees = {e.get("selecteur"): e for e in registre.get("grille", [])}

    defaut = contenus["defaut"]
    combinaisons: list[dict] = []
    # Une présentation réécrit des colonnes de grille et la largeur du conteneur.
    # Sur une page sans grille déclarée, elle n'a pas de cible nommée : la
    # mesurer six fois coûterait cinq chargements de plus par cran et par
    # largeur sans rien confronter. Ces pages sont donc mesurées dans la
    # présentation par défaut seulement — c'est écrit dans `cadrages.toml`.
    pages_avec_grilles = {
        page for page in PAGES if any(pages.get(selecteur) == page for selecteur in entrees)
    }
    for page in PAGES:
        presentations = PRESENTATIONS if page in pages_avec_grilles else (None,)
        for presentation in presentations:
            for cran, echelle in ECHELLES.items():
                modele.definir_contenu(contenus.get(presentation or "defaut", defaut))
                for largeur in LARGEURS:
                    attendu: dict[str, dict] = {}
                    for selecteur, entree in entrees.items():
                        if pages.get(selecteur) != page:
                            continue
                        grille = grilles.get(selecteur)
                        if grille is None or grille.asymetrique:
                            continue
                        ancienne = grille.chaine
                        if pages.get(selecteur):
                            grille.chaine = modele.chaine_d_ancetres(
                                modele.RACINE, pages[selecteur], selecteur
                            )
                        try:
                            regle = (
                                None
                                if presentation is None
                                else modele.regle_applicable(
                                    trouvees, presentation, largeur, selecteur
                                )
                            )
                            # Le plan annonce la **capacité** : combien de colonnes
                            # la place permet. Le nombre de cartes borne ce que le
                            # visiteur voit, et c'est au contrôle de l'appliquer —
                            # exemplaire par exemplaire, avec le compte réellement
                            # lu. Le registre, lui, ne connaît que des listes
                            # possibles (`items = [1, …, 7]`) : s'en servir ici
                            # supposerait un exemplaire unique par sélecteur, ce
                            # qui est faux sur `liens-utiles.html` et
                            # `transparence.html`.
                            cartes_declarees = grille.items
                            grille.items = 0
                            try:
                                nombre = modele.colonnes_attendues(
                                    grille, entree, regle, largeur, echelle
                                )
                            finally:
                                grille.items = cartes_declarees
                            # Une grille `auto-fit` **replie** ses pistes vides :
                            # trois cartes dans une place de six n'en occupent
                            # que trois. Un `repeat(4, …)` ne replie rien :
                            # quatre colonnes restent quatre, même avec une seule
                            # carte. Le contrôle a besoin de le savoir, sinon il
                            # applique la borne des cartes à un dessin fixe.
                            repliable = regle is None or (
                                regle.get("regime") != "fixe"
                                and not str(regle.get("valeur", "")).lstrip().startswith("minmax(0")
                                and str(regle.get("valeur", "")).strip() != "1fr"
                            )
                        finally:
                            grille.chaine = ancienne
                        if nombre:
                            attendu[selecteur] = {"colonnes": nombre, "repliable": bool(repliable)}
                    combinaisons.append(
                        {
                            "page": page,
                            "layout": presentation,
                            "cran": cran,
                            "echelle": echelle,
                            "largeur": largeur,
                            "attendu": attendu,
                        }
                    )
    modele.definir_contenu(defaut)
    grilles_par_page: dict[str, list[str]] = {}
    for combinaison in combinaisons:
        for selecteur in combinaison["attendu"]:
            liste = grilles_par_page.setdefault(combinaison["page"], [])
            if selecteur not in liste:
                liste.append(selecteur)
    return {
        "tolerance_px": 0.5,
        "pages": list(PAGES),
        "grilles": grilles_par_page,
        "combinaisons": combinaisons,
    }


def controler(plan: dict, rapport: dict) -> list[str]:
    """Compare le promis au mesuré. Rend la liste des fautes, jamais un silence."""
    tolerance = float(plan.get("tolerance_px", 0.5))
    mesures = rapport.get("mesures") or []
    if not mesures:
        return [
            "le rapport ne contient aucune mesure — un contrôle incomplet ne vaut pas "
            "un contrôle vide"
        ]
    index = {
        (m.get("page"), m.get("layout"), m.get("cran"), m.get("largeur")): m for m in mesures
    }
    erreurs: list[str] = []
    for combinaison in plan.get("combinaisons", []):
        cle = (
            combinaison["page"],
            combinaison.get("layout"),
            combinaison.get("cran"),
            combinaison["largeur"],
        )
        mesure = index.get(cle)
        libelle = (
            f"{combinaison['page']} · {combinaison.get('layout') or 'défaut'} · "
            f"{combinaison.get('cran')} % · {combinaison['largeur']} px"
        )
        if mesure is None:
            erreurs.append(f"{libelle} : aucune mesure — le cadrage n'a pas été confronté")
            continue
        debordement = mesure.get("debordement")
        if debordement is None:
            erreurs.append(f"{libelle} : débordement non mesuré")
        elif debordement > tolerance:
            coupable = mesure.get("coupable") or {}
            detail = (
                f" — {coupable.get('tag', '?')}"
                + (f".{coupable.get('classe')}" if coupable.get("classe") else "")
                + f" dépasse de {coupable.get('depasse')} px"
                if coupable
                else ""
            )
            erreurs.append(
                f"{libelle} : débordement horizontal de {debordement} px "
                f"(tolérance {tolerance} px){detail}"
            )
        # Un mot coupé est un mot perdu : la zone de découpe d'un ancêtre le
        # rogne, et le visiteur ne le lit jamais. On le nomme avec son extrait.
        coupes = mesure.get("coupes")
        if coupes is None:
            erreurs.append(f"{libelle} : texte coupé non mesuré")
        else:
            for coupe in coupes:
                nom = coupe.get("tag", "?") + (
                    f".{coupe['classe']}" if coupe.get("classe") else ""
                )
                extrait = (coupe.get("texte") or "").strip()
                erreurs.append(
                    f"{libelle} : {nom} coupe un mot de {coupe.get('depasse')} px"
                    + (f" (« {extrait} »)" if extrait else "")
                )
        # Deux cartes qui se recouvrent : l'une cache l'autre.
        chevauchements = mesure.get("chevauchements")
        if chevauchements is None:
            erreurs.append(f"{libelle} : chevauchement non mesuré")
        else:
            for chevauchement in chevauchements:
                erreurs.append(
                    f"{libelle} : {chevauchement.get('premiere')} et "
                    f"{chevauchement.get('seconde')} se chevauchent de "
                    f"{chevauchement.get('largeur')} × {chevauchement.get('hauteur')} px "
                    f"dans {chevauchement.get('selecteur')}"
                )
        # Le contraste : ce qui est écrit doit rester lisible, et pas seulement
        # tenir dans la page. Le seuil dépend de la taille et de la graisse, donc
        # il se calcule ici et non dans le navigateur.
        contraste = mesure.get("contraste")
        if contraste is None:
            erreurs.append(f"{libelle} : contraste non mesuré")
        else:
            if not contraste.get("mesures"):
                erreurs.append(f"{libelle} : aucun texte mesuré pour le contraste")
            for candidat in contraste.get("candidats") or []:
                seuil = seuil_de_contraste(float(candidat.get("taille") or 0), bool(candidat.get("gras")))
                rapport_mesure = float(candidat.get("ratio") or 0)
                if rapport_mesure >= seuil:
                    continue
                nom = candidat.get("tag", "?") + (
                    f".{candidat['classe']}" if candidat.get("classe") else ""
                )
                texte = (candidat.get("texte") or "").strip()
                erreurs.append(
                    f"{libelle} : {nom} contraste {rapport_mesure}:1, seuil {seuil}:1 "
                    f"pour {candidat.get('taille')} px"
                    + (" gras" if candidat.get("gras") else "")
                    + (f" (« {texte} »)" if texte else "")
                )
            for candidat in contraste.get("candidats_degrade") or []:
                seuil = seuil_de_contraste(float(candidat.get("taille") or 0), bool(candidat.get("gras")))
                pire, fond = pire_contraste_degrade(candidat)
                if pire >= seuil:
                    continue
                nom = candidat.get("tag", "?") + (
                    f".{candidat['classe']}" if candidat.get("classe") else ""
                )
                texte = (candidat.get("texte") or "").strip()
                erreurs.append(
                    f"{libelle} : {nom} contraste {pire}:1 sur un dégradé, seuil {seuil}:1 "
                    f"pour {candidat.get('taille')} px"
                    + (" gras" if candidat.get("gras") else "")
                    + f" — pire point rgb({fond['r']:.0f}, {fond['g']:.0f}, {fond['b']:.0f})"
                    + (f" (« {texte} »)" if texte else "")
                )
        # Le plan annonce une **capacité** ; ce que le visiteur voit en dépend
        # aussi du nombre de cartes. Chaque exemplaire est donc confronté avec
        # son propre compte : cinq cartes dans une grille qui permet six colonnes
        # en occupent cinq, et c'est conforme. Ne mesurer qu'un exemplaire par
        # sélecteur — le premier trouvé — faisait accuser la feuille de 14 écarts
        # qui n'existaient pas, le 3 novembre 2026.
        detail_grilles = mesure.get("grilles")
        if detail_grilles is None:
            # Sans ce relevé, aucune colonne ne peut être confrontée : le dire une
            # fois vaut mieux que d'ajouter une erreur par grille pour la même cause.
            erreurs.append(f"{libelle} : grilles non mesurées (colonnes absentes du relevé)")
            detail_grilles = None
        for selecteur, capacite in (combinaison.get("attendu") or {}).items():
            if detail_grilles is None:
                break
            detail = detail_grilles.get(selecteur)
            if detail is None:
                erreurs.append(f"{libelle} : {selecteur} n'a pas été mesurée")
                continue
            if isinstance(capacite, dict):
                colonnes_max = int(capacite.get("colonnes") or 0)
                repliable = bool(capacite.get("repliable"))
            else:
                erreurs.append(f"{libelle} : {selecteur} sans capacité déclarée dans le plan")
                continue
            instances = detail.get("instances") or []
            total = int(detail.get("total") or 0)
            if not instances:
                erreurs.append(f"{libelle} : {selecteur} ne porte aucune carte à mesurer")
                continue
            if total > len(instances):
                # Le relevé plafonne le nombre d'exemplaires inspectés : le taire
                # laisserait croire que tous l'ont été.
                erreurs.append(
                    f"{libelle} : {selecteur} compte {total} exemplaire(s), "
                    f"{len(instances)} seul(s) inspecté(s)"
                )
            for rang, instance in enumerate(instances, start=1):
                cartes = int(instance.get("cartes") or 0)
                attendu_ici = min(colonnes_max, cartes) if repliable and cartes else colonnes_max
                observe = int(instance.get("colonnes") or 0)
                if observe == attendu_ici:
                    continue
                pistes = int(instance.get("pistes") or observe)
                repliees = pistes - observe
                detail_pistes = (
                    f" ({pistes} piste(s) déclarée(s), {repliees} repliée(s))" if repliees > 0 else ""
                )
                exemplaire = f" · exemplaire {rang}/{total}" if total > 1 else ""
                erreurs.append(
                    f"{libelle}{exemplaire} : {selecteur} annonce {attendu_ici} colonne(s) "
                    f"occupée(s) pour {cartes} carte(s), le navigateur en compte {observe}"
                    f"{detail_pistes}"
                )
    return erreurs


#: « Grand texte » au sens WCAG 2.2 (1.4.3) : 24 px, ou 18,66 px en gras —
#: c'est-à-dire 18 pt. Les deux seuils sont écrits ici, en un seul endroit, pour
#: que le calcul de la mesure et le contrôle ne puissent pas diverger.
SEUIL_GRAND_TEXTE_PX = 24.0
SEUIL_GRAND_TEXTE_GRAS_PX = 18.66
CONTRASTE_PETIT_TEXTE = 4.5
CONTRASTE_GRAND_TEXTE = 3.0


def seuil_de_contraste(taille: float, gras: bool) -> float:
    """Le rapport minimal exigé pour un texte, selon sa taille et sa graisse."""
    if taille >= SEUIL_GRAND_TEXTE_PX:
        return CONTRASTE_GRAND_TEXTE
    if gras and taille >= SEUIL_GRAND_TEXTE_GRAS_PX:
        return CONTRASTE_GRAND_TEXTE
    return CONTRASTE_PETIT_TEXTE


def luminance_wcag(couleur: dict) -> float:
    """Luminance relative WCAG d'une couleur `{r, g, b}` en 0–255."""

    def canal(valeur: float) -> float:
        v = float(valeur) / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * canal(couleur["r"]) + 0.7152 * canal(couleur["g"]) + 0.0722 * canal(couleur["b"])


def rapport_wcag(une: dict, autre: dict) -> float:
    l1, l2 = luminance_wcag(une), luminance_wcag(autre)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


def poser(dessus: dict, dessous: dict) -> dict:
    """Compose une couleur sur une autre, comme le fait un navigateur."""
    alpha = float(dessus.get("a", 1))
    return {
        "r": dessus["r"] * alpha + dessous["r"] * (1 - alpha),
        "g": dessus["g"] * alpha + dessous["g"] * (1 - alpha),
        "b": dessus["b"] * alpha + dessous["b"] * (1 - alpha),
        "a": 1,
    }


#: Points échantillonnés entre deux arrêts d'un dégradé. Neuf suffisent à suivre
#: une interpolation en sRGB sans prétendre la prouver : entre deux couleurs, la
#: luminance varie de façon monotone par canal, et le pire cas d'un texte est
#: toujours à l'un des extrêmes ou près d'eux. C'est une borne **pratique**,
#: écrite comme telle dans la limite du registre.
ECHANTILLONS_DEGRADE = 9


def _arrets_et_zone(couche) -> tuple[list[dict], tuple[float, float]]:
    """Rend les arrêts d'une couche et la portion de l'axe couverte par le texte.

    Le relevé donne des arrêts `{r, g, b, a, t}` et une zone `[début, fin]` sur
    l'axe du dégradé — la projection de la boîte du texte. Une couche d'ancienne
    forme (simple liste de couleurs) reste lue : zone entière, positions
    implicites. Une zone illisible vaut la plage entière : c'est un majorant,
    jamais un silence.
    """
    if isinstance(couche, dict):
        arrets = list(couche.get("arrets") or [])
        zone = couche.get("zone") or [0.0, 1.0]
    else:
        arrets, zone = list(couche or []), [0.0, 1.0]
    if len(arrets) < 2:
        return arrets, (0.0, 1.0)
    positions = [a.get("t") if isinstance(a, dict) else None for a in arrets]
    if any(p is None for p in positions):
        # Positions partiellement écrites : on revient à l'hypothèse uniforme,
        # qui couvre le même chemin de couleurs — elle ne le situe simplement
        # pas au pixel près. Le relevé dit lesquelles il n'a pas pu lire.
        positions = [i / (len(arrets) - 1) for i in range(len(arrets))]
    try:
        debut, fin = float(zone[0]), float(zone[1])
    except (TypeError, ValueError, IndexError):
        debut, fin = 0.0, 1.0
    debut, fin = max(0.0, min(1.0, debut)), max(0.0, min(1.0, fin))
    if fin < debut:
        debut, fin = fin, debut
    return arrets, (debut, fin)


def _couleur_a(arrets: list[dict], positions: list[float], t: float) -> dict:
    if t <= positions[0]:
        return dict(arrets[0])
    if t >= positions[-1]:
        return dict(arrets[-1])
    for i in range(1, len(positions)):
        if t <= positions[i]:
            largeur = positions[i] - positions[i - 1] or 1e-9
            part = (t - positions[i - 1]) / largeur
            a, b = arrets[i - 1], arrets[i]
            return {
                "r": a["r"] + (b["r"] - a["r"]) * part,
                "g": a["g"] + (b["g"] - a["g"]) * part,
                "b": a["b"] + (b["b"] - a["b"]) * part,
                "a": a.get("a", 1) + (b.get("a", 1) - a.get("a", 1)) * part,
            }
    return dict(arrets[-1])


def plage_degrade(base: dict, couches: list, seuil_points: int = 64) -> list[dict]:
    """Rend les couleurs que le fond peut prendre, du plus sombre au plus clair.

    Chaque couche est un dégradé posé au-dessus du précédent, réduit à la
    **portion réellement sous le texte**. Une couche peut contenir des arrêts
    transparents : ils laissent voir ce qui est dessous, et c'est justement le
    cas des halos radiaux du site.
    """
    couleurs = [base]
    for couche in couches:
        arrets, (debut, fin) = _arrets_et_zone(couche)
        if not arrets:
            continue
        positions = [a.get("t") if isinstance(a, dict) else None for a in arrets]
        if len(arrets) == 1:
            positions = [0.0]
        elif any(p is None for p in positions):
            positions = [i / (len(arrets) - 1) for i in range(len(arrets))]
        positions = [float(p) for p in positions]
        if fin <= debut:
            fin = min(1.0, debut + 0.001)
        points = {debut, fin}
        points.update(p for p in positions if debut <= p <= fin)
        for rang in range(ECHANTILLONS_DEGRADE):
            points.add(debut + (fin - debut) * rang / (ECHANTILLONS_DEGRADE - 1))
        echantillons = [_couleur_a(arrets, positions, p) for p in sorted(points)]
        composees = [poser(echantillon, fond) for fond in couleurs for echantillon in echantillons]
        # Les compositions sont ramenées aux deux extrêmes de luminance plus la
        # médiane : garder les 81 compositions de trois couches rendrait le
        # contrôle lent sans rien prouver de plus.
        composees.sort(key=luminance_wcag)
        if len(composees) > 3:
            composees = [composees[0], composees[len(composees) // 2], composees[-1]]
        couleurs = composees
        if len(couleurs) > seuil_points:  # garde-fou : jamais atteint avec 3 couleurs
            couleurs = couleurs[:seuil_points]
    return couleurs


def pire_contraste_degrade(candidat: dict) -> tuple[float, dict]:
    """Le pire rapport de contraste d'un texte sur une plage de dégradé."""
    texte = dict(candidat.get("couleur") or {})
    base = dict(candidat.get("base") or {"r": 255, "g": 255, "b": 255, "a": 1})
    couches = candidat.get("couches") or []
    plage = plage_degrade(base, couches)
    pire, pire_fond = None, base
    for fond in plage:
        couleur = poser(texte, fond) if float(texte.get("a", 1)) < 1 else texte
        ratio = rapport_wcag(couleur, fond)
        if pire is None or ratio < pire:
            pire, pire_fond = ratio, fond
    return round(pire or 0, 3), pire_fond


def lire_motifs(chemin: Path | None = None) -> dict[str, str]:
    """Rend les motifs écrits pour les rangées incomplètes assumées.

    Le 4 novembre 2026, une personne a tranché : une rangée incomplète reste un
    fait de dessin, mais un vide **assumé** doit porter son motif, écrit dans
    `docs/rd/cadrages.toml` à côté de son chiffre. Un motif qui n'existe que
    dans une conversation ne survit pas à la conversation.

    Un registre illisible n'est pas un registre vide : le diagnostic le dit
    plutôt que de déclarer tous les vides « sans motif ».
    """
    chemin = chemin or (RACINE / REGISTRE_CADRAGES)
    registre = lire_registre(chemin)
    rangees = registre.get("rangees") or {}
    motifs = rangees.get("motifs") or {}
    return {str(cle): str(valeur) for cle, valeur in motifs.items()}


def orphelins(plan: dict, rapport: dict) -> tuple[list[dict], list[str]]:
    """Nomme les grilles dont la dernière rangée laisse un vide visible.

    Une rangée incomplète n'est pas une faute : cinq cartes en deux colonnes
    laissent une carte seule, et c'est parfois le dessin voulu. Ce diagnostic ne
    refuse rien — il chiffre, cadrage par cadrage, ce qu'un œil verrait, et
    laisse la décision à une personne. Il rend aussi les grilles dont la rangée
    n'a pas été relevée : un diagnostic incomplet se dit, il ne se tait pas.
    """
    motifs = lire_motifs()
    mesures = rapport.get("mesures") or []
    index = {(m.get("page"), m.get("layout"), m.get("cran"), m.get("largeur")): m for m in mesures}
    trouvees: dict[tuple[str, str], dict] = {}
    sans_releve: set[str] = set()
    for combinaison in plan.get("combinaisons", []):
        cle = (combinaison["page"], combinaison.get("layout"), combinaison.get("cran"), combinaison["largeur"])
        mesure = index.get(cle)
        if mesure is None:
            continue
        detail_grilles = mesure.get("grilles") or {}
        for selecteur, capacite in (combinaison.get("attendu") or {}).items():
            detail = detail_grilles.get(selecteur)
            if detail is None or not detail.get("instances"):
                sans_releve.add(selecteur)
                continue
            fait = detail["instances"][0]
            colonnes_max = int(capacite.get("colonnes") or 0) if isinstance(capacite, dict) else 0
            # `manque` est déjà net des gouttières : un vide plus fin qu'un
            # demi-pixel n'est pas un vide, c'est un arrondi de navigateur.
            if colonnes_max <= 1 or float(fait.get("manque") or 0) <= 0.5:
                continue
            entree = trouvees.setdefault(
                (combinaison["page"], selecteur),
                {
                    "page": combinaison["page"],
                    "selecteur": selecteur,
                    "cadrages": 0,
                    "pire_manque": 0.0,
                    "exemple": None,
                },
            )
            entree["motif"] = motifs.get(f"{combinaison['page']} · {selecteur}")
            entree["cadrages"] += 1
            if float(fait.get("manque") or 0) > entree["pire_manque"]:
                entree["pire_manque"] = float(fait.get("manque") or 0)
                entree["exemple"] = (
                    f"{combinaison.get('layout') or 'défaut'} · {combinaison.get('cran')} % · "
                    f"{combinaison['largeur']} px · {fait.get('derniere')} carte(s) sur la "
                    f"dernière rangée, {colonnes_max} colonne(s) au plus"
                )
    return sorted(trouvees.values(), key=lambda e: (-e["pire_manque"], e["selecteur"])), sorted(sans_releve)


def ecartes(rapport: dict) -> dict:
    """Nomme ce que le contrôle écarte, avec son compte.

    Un contrôle qui exclut sans le dire finit par exclure tout. Deux familles
    sont écartées du contraste : le texte **décoratif déclaré** (`aria-hidden`,
    `role="presentation"`) et le texte posé sur un **fond en image**, que la
    méthode ne sait pas calculer. Ce diagnostic les rend relisibles, sélecteur
    par sélecteur ; il ne juge rien et ne refuse rien.
    """
    decoratifs: dict[str, int] = {}
    fond_image: dict[str, int] = {}
    for mesure in rapport.get("mesures") or []:
        contraste = mesure.get("contraste") or {}
        for selecteur in contraste.get("decoratifs_selecteurs") or []:
            decoratifs[selecteur] = decoratifs.get(selecteur, 0) + 1
        for selecteur in contraste.get("fond_image_selecteurs") or []:
            fond_image[selecteur] = fond_image.get(selecteur, 0) + 1
    return {
        "decoratifs": sorted(decoratifs.items(), key=lambda couple: (-couple[1], couple[0])),
        "fond_image": sorted(fond_image.items(), key=lambda couple: (-couple[1], couple[0])),
    }


def nommer_candidat(candidat: dict) -> str:
    """Un nom lisible pour un texte mesuré : la balise et sa première classe."""
    classe = str(candidat.get("classe") or "").split(" ")[0]
    nom = str(candidat.get("tag") or "?")
    return f"{nom}.{classe}" if classe else nom


#: Motifs pour lesquels une zone radiale n'a pas pu être située. Le relevé les
#: écrit ; un motif inconnu n'est pas ignoré, il est nommé tel quel.
MOTIFS_RADIAUX = (
    "centre-absent",
    "rayon-absent-ou-en-pourcentage",
)


def majorant_radial(rapport: dict) -> dict:
    """Chiffre ce que coûte un dégradé radial dont la zone n'a pas pu être située.

    Un dégradé **linéaire** est projeté sur son axe : le texte ne voit que la
    portion de plage qui est vraiment sous lui. Un dégradé **radial** l'est
    aussi — mais seulement si son centre est écrit en pourcentage et son rayon
    en pixels. Sinon la mesure retombe sur la plage **entière** : c'est un
    majorant assumé, écrit comme tel dans les limites du registre depuis le
    3 novembre 2026, et jamais chiffré. Un majorant qu'on ne chiffre pas se lit
    comme une mesure.

    Ce diagnostic ne juge rien et ne corrige rien : il compte. Combien de textes
    sont jugés contre une plage qu'ils ne voient pas, pour quel motif, et — sur
    l'échantillon joint au rapport, qui est plafonné — combien de **verdicts**
    tiennent à ce majorant seul : des textes refusés avec la plage entière qui
    passeraient si la couche ambiguë ne comptait pas. Ce second chiffre est une
    borne, pas une vérité : la vraie zone est quelque part entre les deux.
    """
    mesures = rapport.get("mesures") or []
    if not mesures:
        return {"lisible": False, "raison": "le rapport ne contient aucun relevé"}

    sans_compteur = [
        mesure.get("nom") or mesure.get("page") or "?"
        for mesure in mesures
        if "degrades_radiaux_non_situes" not in (mesure.get("contraste") or {})
    ]
    if sans_compteur:
        return {
            "lisible": False,
            "raison": (
                "le relevé ne porte pas les compteurs radiaux : il a été produit par une "
                "version antérieure du relevé, qui ne distinguait pas une zone non située "
                "d'une zone entière. Relever à nouveau, plutôt que compter zéro."
            ),
            "exemples": sans_compteur[:3],
        }

    bilan = {
        "lisible": True,
        "releves": len(mesures),
        "textes_degrades": 0,
        "textes_radiaux": 0,
        "textes_non_situes": 0,
        "couches_par_motif": {},
        "echantillon": 0,
        "deplaces": 0,
        "deplaces_forts": 0,
        "verdicts_en_jeu": 0,
        "pire_ecart": None,
    }
    for mesure in mesures:
        contraste = mesure.get("contraste") or {}
        bilan["textes_degrades"] += int(contraste.get("degrades") or 0)
        bilan["textes_radiaux"] += int(contraste.get("degrades_radiaux") or 0)
        bilan["textes_non_situes"] += int(contraste.get("degrades_radiaux_non_situes") or 0)
        for motif, compte in (contraste.get("couches_radiales_non_situees") or {}).items():
            bilan["couches_par_motif"][motif] = bilan["couches_par_motif"].get(motif, 0) + int(compte)
        for candidat in contraste.get("candidats_degrade") or []:
            couches = candidat.get("couches") or []
            ambigues = [c for c in couches if isinstance(c, dict) and c.get("situe") is False]
            if not ambigues:
                continue
            bilan["echantillon"] += 1
            avec, _ = pire_contraste_degrade(candidat)
            sans_candidat = dict(candidat)
            sans_candidat["couches"] = [
                c for c in couches if not (isinstance(c, dict) and c.get("situe") is False)
            ]
            sans, _ = pire_contraste_degrade(sans_candidat)
            ecart = round(sans - avec, 3)
            if ecart <= 0:
                continue
            bilan["deplaces"] += 1
            if ecart >= 1.0:
                bilan["deplaces_forts"] += 1
            seuil = seuil_de_contraste(float(candidat.get("taille") or 0), bool(candidat.get("gras")))
            if avec < seuil <= sans:
                bilan["verdicts_en_jeu"] += 1
            if bilan["pire_ecart"] is None or ecart > bilan["pire_ecart"]["ecart"]:
                bilan["pire_ecart"] = {
                    "ecart": ecart,
                    "avec": avec,
                    "sans": sans,
                    "selecteur": nommer_candidat(candidat),
                    "texte": (candidat.get("texte") or "")[:40],
                }
    return bilan


def principal(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description="Confronte le dessin dans tous les cadrages personnalisés.")
    analyseur.add_argument("--releve-json", metavar="CHEMIN", help="écrire le plan à mesurer")
    analyseur.add_argument(
        "--controler",
        nargs=2,
        metavar=("PLAN", "RAPPORT"),
        help="confronter un rapport de mesure au plan",
    )
    analyseur.add_argument(
        "--ecartes",
        nargs=1,
        metavar="RAPPORT",
        help="nommer les textes écartés du contraste (décoratifs, fonds en image)",
    )
    analyseur.add_argument(
        "--orphelins",
        nargs=2,
        metavar=("PLAN", "RAPPORT"),
        help="nommer les grilles dont la dernière rangée laisse un vide visible",
    )
    analyseur.add_argument(
        "--radiaux",
        nargs=1,
        metavar="RAPPORT",
        help="chiffrer ce que coûte un dégradé radial dont la zone n'a pas été située",
    )
    options = analyseur.parse_args(arguments)

    modele = charger_modele()
    chemin_feuille = RACINE / FEUILLE
    if not chemin_feuille.is_file():
        print(f"Feuille de style introuvable : {FEUILLE}", file=sys.stderr)
        return 2
    feuille = chemin_feuille.read_text(encoding="utf-8")
    modele.definir_gouttiere(feuille)
    modele.definir_feuille(feuille)

    if options.releve_json:
        registre = lire_registre(RACINE / REGISTRE)
        plan = construire_plan(modele, registre, feuille)
        destination = Path(options.releve_json)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        attendus = sum(len(c["attendu"]) for c in plan["combinaisons"])
        print(
            f"Plan de cadrage écrit : {destination} — {len(plan['combinaisons'])} combinaison(s), "
            f"{attendus} grille(s) à confronter, tolérance {plan['tolerance_px']} px."
        )
        return 0

    if options.radiaux:
        try:
            rapport = json.loads(Path(options.radiaux[0]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            print(f"Lecture impossible ({erreur}) — aucun chiffre.", file=sys.stderr)
            return 2
        bilan = majorant_radial(rapport)
        if not bilan.get("lisible"):
            print(f"Majorant radial : illisible — {bilan['raison']}", file=sys.stderr)
            for exemple in bilan.get("exemples") or []:
                print(f"  - relevé sans compteurs : {exemple}", file=sys.stderr)
            return 2
        part = (
            f"{bilan['textes_non_situes']} texte(s) sur {bilan['textes_degrades']} posés sur un "
            f"dégradé"
        )
        if bilan["textes_radiaux"]:
            part += f", dont {bilan['textes_radiaux']} sur un dégradé radial"
        print(f"Majorant radial : {part}.")
        if not bilan["textes_non_situes"]:
            print(
                "Aucun texte n'est jugé contre une plage qu'il ne voit pas : "
                "toutes les zones radiales ont été situées."
            )
            return 0
        motifs = ", ".join(
            f"{motif} ({compte})" for motif, compte in sorted(bilan["couches_par_motif"].items())
        )
        print(f"  - motifs des couches non situées : {motifs or 'aucun motif écrit'}")
        print(
            f"  - sur l'échantillon joint, {bilan['echantillon']} texte(s) portent une couche "
            f"non située ; {bilan['deplaces']} voient leur pire rapport changer si on la retire, "
            f"dont {bilan['deplaces_forts']} de plus d'un point."
        )
        if bilan["verdicts_en_jeu"]:
            print(
                f"  - {bilan['verdicts_en_jeu']} verdict(s) tiennent au majorant seul : refusés "
                "avec la plage entière, conformes si la couche ambiguë ne comptait pas."
            )
        if bilan["pire_ecart"]:
            pire = bilan["pire_ecart"]
            print(
                f"  - pire écart : {pire['selecteur']} — {pire['avec']}:1 avec la couche, "
                f"{pire['sans']}:1 sans elle ({pire['ecart']} point(s))."
            )
        print(
            "Ce chiffre est une borne, pas une mesure : la vraie zone d'un halo ambigu est "
            "quelque part entre les deux. Il ne refuse rien."
        )
        return 0

    if options.ecartes:
        try:
            rapport = json.loads(Path(options.ecartes[0]).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            print(f"Lecture impossible ({erreur}) — aucun diagnostic.", file=sys.stderr)
            return 2
        bilan = ecartes(rapport)
        if not bilan["decoratifs"] and not bilan["fond_image"]:
            print("Écartés du contraste : aucun — tout texte visible a été mesuré.")
            return 0
        print("Écartés du contraste, décoratif déclaré (aria-hidden, role=presentation) :")
        for selecteur, compte in bilan["decoratifs"]:
            print(f"  - {selecteur} : présent dans {compte} cadrage(s)")
        print("Écartés du contraste, texte posé sur un fond en image (non calculable) :")
        for selecteur, compte in bilan["fond_image"]:
            print(f"  - {selecteur} : présent dans {compte} cadrage(s)")
        print("Ces textes ne sont ni jugés ni corrigés : ce diagnostic les rend relisibles.")
        return 0

    if options.orphelins:
        plan_lu, rapport_lu = options.orphelins
        try:
            plan = json.loads(Path(plan_lu).read_text(encoding="utf-8"))
            rapport = json.loads(Path(rapport_lu).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            print(f"Lecture impossible ({erreur}) — aucun diagnostic.", file=sys.stderr)
            return 2
        liste, sans_releve = orphelins(plan, rapport)
        if not liste:
            print(
                "Rangées : aucune grille ne laisse de vide visible dans les cadrages mesurés "
                f"— {len(rapport.get('mesures') or [])} relevé(s) lu(s)."
            )
        sans_motif = []
        for entree in liste:
            motif = entree.get("motif")
            if not motif:
                sans_motif.append(f"{entree['page']} · {entree['selecteur']}")
            print(
                f"  - {entree['page']} · {entree['selecteur']} : {entree['cadrages']} cadrage(s) "
                f"avec une dernière rangée incomplète, vide maximal {entree['pire_manque']:.2f} px "
                f"({entree['exemple']})"
                + (f" — assumée : {motif}" if motif else " — SANS MOTIF ÉCRIT")
            )
        if sans_motif:
            # Chaque vide sans motif sort avec son chiffre : un manque nommé sans
            # son nombre oblige à rouvrir le rapport pour écrire le motif, et
            # c'est ainsi qu'un motif s'écrit de mémoire — donc faux.
            for entree in liste:
                if entree.get("motif"):
                    continue
                print(
                    f"  ! sans motif : {entree['page']} · {entree['selecteur']} : "
                    f"{entree['cadrages']} cadrage(s), vide maximal {entree['pire_manque']:.2f} px "
                    f"({entree['exemple']}) — décision A2 du 4 novembre 2026 : le motif s'écrit "
                    "dans [rangees.motifs].",
                    file=sys.stderr,
                )
        if sans_releve:
            print(
                f"  ! {len(sans_releve)} grille(s) sans relevé de rangée : "
                + ", ".join(sans_releve[:8])
                + ("…" if len(sans_releve) > 8 else ""),
                file=sys.stderr,
            )
        return 0

    if options.controler:
        plan_lu, rapport_lu = options.controler
        try:
            plan = json.loads(Path(plan_lu).read_text(encoding="utf-8"))
            rapport = json.loads(Path(rapport_lu).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            print(f"Lecture impossible ({erreur}) — aucune confrontation.", file=sys.stderr)
            return 2
        erreurs = controler(plan, rapport)
        if erreurs:
            for erreur in erreurs[:40]:
                print(f"  - {erreur}", file=sys.stderr)
            if len(erreurs) > 40:
                print(f"  … {len(erreurs) - 40} autre(s) écart(s).", file=sys.stderr)
            print(
                f"Refusé : {len(erreurs)} écart(s) entre la feuille et ce que le navigateur "
                f"affiche ({rapport.get('navigateur') or 'navigateur inconnu'}).",
                file=sys.stderr,
            )
            return 1
        combinaisons = len(plan.get("combinaisons", []))
        mesures = len(rapport.get("mesures", []))
        print(
            f"Cadrages : {combinaisons} combinaison(s) mesurée(s) sur {mesures} relevé(s), "
            f"aucun débordement au-delà de {plan.get('tolerance_px')} px, aucun écart de colonnes, "
            f"aucun mot coupé, aucun chevauchement de cartes, contraste tenu "
            f"— navigateur {rapport.get('navigateur') or 'inconnu'}."
        )
        return 0

    analyseur.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(principal())
