"""simulateur/clarte.py — relire une simulation en français ordinaire.

Pourquoi ce module
------------------

Le moteur produit des nombres justes et illisibles : « solde_mesures_mde :
+18,4 », « spread_final_bps : 47,2 », « score_moyen_domaines : 52,1 ». Celui qui
n'a jamais lu un document budgétaire ne peut pas en tirer grand-chose — et c'est
normal : ces écritures sont un métier.

Ce module ne calcule rien de nouveau. Il **relit** une sortie de simulation et
en tire une dizaine de phrases complètes, dans l'ordre où une personne se pose
les questions :

    1. Combien l'État gagne-t-il ou perd-il ?
    2. Le déficit et la dette vont-ils mieux ou moins bien ?
    3. À quel prix l'État emprunte-t-il ?
    4. Qu'est-ce que ça change pour les ménages ?
    5. Quels secteurs en profitent, lesquels trinquent ?
    6. Où sont les signaux d'alerte ?

Chaque phrase est construite à partir des chiffres déjà calculés — jamais à
côté d'eux. Aucune n'ajoute d'information qui ne soit dans la sortie ; aucune ne
porte de jugement politique. Les grandeurs absentes sont simplement passées sous
silence, plutôt que remplacées par une approximation.

Non-portée
----------

Ce module ne dit pas ce qu'il faut faire. Il traduit. Une phrase peut donc
conclure « le déficit se creuse » sans jamais dire « c'est bien » ou « c'est
mal » : c'est au lecteur, ou au débat public, de trancher.

Aucune dépendance externe : bibliothèque standard uniquement.
"""

from __future__ import annotations

from typing import Any

#: Seuil en dessous duquel un écart est considéré comme non significatif, pour
#: ne pas annoncer « ça bouge » sur un arrondi. Exprimé dans l'unité de la
#: grandeur concernée.
SEUILS = {
    "mde": 0.05,        # 50 M€
    "pct_pib": 0.05,    # 0,05 point de PIB
    "pts": 0.05,
    "bps": 1.0,
    "indice": 0.1,
    "score": 0.15,
}


def nombre(valeur: Any, decimales: int = 1) -> str:
    """Formate un nombre à la française : virgule décimale, pas de point."""
    try:
        nombre_flottant = float(valeur)
    except (TypeError, ValueError):
        return "—"
    texte = f"{nombre_flottant:,.{decimales}f}"
    return texte.replace(",", " ").replace(".", ",").strip()


def signe(valeur: float) -> str:
    return "+" if valeur > 0 else ("−" if valeur < 0 else "")


def milliards(valeur: Any, decimales: int = 1) -> str:
    """Formate un montant en milliards d'euros avec son signe."""
    try:
        montant = float(valeur)
    except (TypeError, ValueError):
        return "—"
    return f"{signe(montant)}{nombre(abs(montant), decimales)} Md€"


def _lire(charge: dict, *cles: str, par_defaut: Any = None) -> Any:
    """Lecteur tolérant : remonte une valeur imbriquée sans jamais échouer."""
    courant: Any = charge
    for cle in cles:
        if not isinstance(courant, dict):
            return par_defaut
        courant = courant.get(cle)
        if courant is None:
            return par_defaut
    return courant


def _niveau(valeur: float | None, sens: int, seuil: float) -> str:
    """Qualifie un écart : favorable, défavorable ou neutre.

    ``sens`` vaut +1 quand une hausse est une bonne nouvelle (recettes, pouvoir
    d'achat) et −1 quand c'est une mauvaise (déficit, dette, tension sociale).
    """
    if valeur is None:
        return "inconnu"
    if abs(valeur) < seuil:
        return "neutre"
    return "favorable" if sens * valeur > 0 else "defavorable"


def _lire_solde_public(valeur: float | None) -> str:
    """Dit « déficit » ou « excédent » — un déficit négatif est un excédent."""
    if valeur is None:
        return "—"
    if valeur < 0:
        return f"un excédent de {nombre(abs(valeur), 1)} % du PIB"
    if valeur == 0:
        return "un solde à l'équilibre"
    return f"un déficit de {nombre(valeur, 1)} % du PIB"


def _phrase_budget(synthese: dict) -> dict[str, Any] | None:
    recettes = synthese.get("recettes_nouvelles_mde")
    depenses = synthese.get("depenses_nouvelles_mde")
    solde = synthese.get("solde_mesures_mde")
    if recettes is None and depenses is None:
        return None
    recettes = recettes or 0.0
    depenses = depenses or 0.0
    if solde is None:
        solde = recettes - depenses
    if abs(solde) < SEUILS["mde"] and abs(recettes) < SEUILS["mde"]:
        return None
    # Une dépense négative est une économie : le dire, plutôt que d'afficher
    # « −31,9 Md€ de dépenses en plus » qui se lit comme une contradiction.
    morceau_recettes = (f"apportent {milliards(recettes)} de recettes en plus"
                        if recettes >= 0
                        else f"retirent {milliards(abs(recettes))} de recettes")
    morceau_depenses = (f"ajoutent {milliards(depenses)} de dépenses"
                        if depenses >= 0
                        else f"font économiser {nombre(abs(depenses), 1)} Md€ de dépenses")
    if abs(solde) < SEUILS["mde"]:
        texte = (f"Au total, vos réglages {morceau_recettes} et {morceau_depenses} : "
                 f"le solde est à l'équilibre.")
    elif solde > 0:
        texte = (f"Au total, vos réglages {morceau_recettes} et {morceau_depenses} : "
                 f"le programme dégage {milliards(solde)} par an.")
    else:
        texte = (f"Au total, vos réglages {morceau_recettes} et {morceau_depenses} : "
                 f"le programme coûte {milliards(abs(solde))} par an.")
    return {
        "cle": "budget",
        "grandeur": "Solde du programme",
        "valeur": milliards(solde),
        "texte": texte,
        "niveau": _niveau(solde, 1, SEUILS["mde"]),
        "explication": "Recettes nouvelles moins dépenses nouvelles, à l'année terminale.",
    }


def _phrase_deficit(synthese: dict, horizon: int) -> dict[str, Any] | None:
    final = synthese.get("deficit_final_pct")
    if final is None:
        return None
    reference = synthese.get("deficit_reference_pct")
    ecart = synthese.get("deficit_ecart_pts")
    if ecart is None and reference is not None:
        ecart = final - reference
    if reference is None or ecart is None:
        texte = (f"Les comptes publics afficheraient {_lire_solde_public(final)} "
                 f"à l'année {horizon}.")
        return {
            "cle": "deficit", "grandeur": "Solde public",
            "valeur": _lire_solde_public(final).replace("un ", ""),
            "texte": texte, "niveau": _niveau(-final, 1, 0.0),
            "explication": "Part de la richesse nationale que l'État doit emprunter chaque année.",
        }
    # Un déficit négatif est un excédent : le dire, plutôt que d'afficher un
    # chiffre négatif que personne ne lit correctement.
    texte = (
        f"Les comptes publics afficheraient {_lire_solde_public(final)} "
        f"en année {horizon}, contre {_lire_solde_public(reference)} sans ces "
        f"mesures : soit {nombre(abs(ecart), 1)} point "
        f"{'de mieux' if ecart < 0 else 'de plus'}."
    )
    return {
        "cle": "deficit",
        "grandeur": "Solde public",
        "valeur": _lire_solde_public(final).replace("un ", ""),
        "texte": texte,
        "niveau": _niveau(ecart, -1, SEUILS["pct_pib"]),
        "explication": "Comparé à ce qui se passerait sans aucune politique nouvelle.",
    }


def _phrase_dette(synthese: dict, horizon: int) -> dict[str, Any] | None:
    ratio = synthese.get("dette_finale_pct")
    if ratio is None:
        return None
    reference = synthese.get("dette_reference_pct")
    montant = _lire(synthese, "bilan_intergenerationnel", "dette_publique_mde")
    ecart = synthese.get("dette_ecart_pts")
    if ecart is None and reference is not None:
        ecart = ratio - reference
    suite = ""
    if montant is not None:
        suite = f", soit environ {nombre(montant, 0)} milliards d'euros"
    if reference is None or ecart is None:
        texte = f"La dette publique atteindrait {nombre(ratio, 1)} % du PIB en année {horizon}{suite}."
        return {
            "cle": "dette", "grandeur": "Dette publique", "valeur": f"{nombre(ratio, 1)} % du PIB",
            "texte": texte, "niveau": "neutre",
            "explication": "Le stock accumulé, rapporté à la richesse produite en un an.",
        }
    texte = (
        f"La dette publique atteindrait {nombre(ratio, 1)} % du PIB en année {horizon}, "
        f"contre {nombre(reference, 1)} % sans réforme : "
        f"{nombre(abs(ecart), 1)} point {'de moins' if ecart < 0 else 'de plus'}{suite}."
    )
    return {
        "cle": "dette",
        "grandeur": "Dette publique",
        "valeur": f"{nombre(ratio, 1)} % du PIB",
        "texte": texte,
        "niveau": _niveau(ecart, -1, SEUILS["pct_pib"]),
        "explication": "Ce que l'État devra rembourser ou refinancer, mesuré en années de richesse nationale.",
    }


def _phrase_emprunt(synthese: dict, contexte: dict) -> dict[str, Any] | None:
    taux = synthese.get("taux_oat_final")
    if taux is None:
        return None
    spread = synthese.get("spread_final_bps")
    charge = synthese.get("charge_dette_finale_mde")
    comparaison = ""
    if spread is not None:
        comparaison = (
            f", soit {nombre(spread / 100.0, 2)} point de pourcentage de plus que "
            f"l'Allemagne ({nombre(spread, 0)} centièmes de point)"
        )
    cout = f" Cela représente {milliards(charge)} d'intérêts par an." if charge else ""
    # Le niveau d'un taux ne se juge pas seul : on le compare à celui d'aujourd'hui.
    depart = contexte.get("taux_oat_10ans") if isinstance(contexte, dict) else None
    ecart = (taux - float(depart)) if depart is not None else None
    if ecart is not None and abs(ecart) >= 0.25:
        comparaison += (
            f" — {nombre(abs(ecart), 2)} point {'de plus' if ecart > 0 else 'de moins'} "
            f"qu'aujourd'hui"
        )
    return {
        "cle": "emprunt",
        "grandeur": "Taux d'emprunt de l'État",
        "valeur": f"{nombre(taux, 2)} % sur 10 ans",
        "texte": (
            f"L'État emprunterait à {nombre(taux, 2)} % sur dix ans{comparaison}.{cout}"
        ),
        "niveau": _niveau(ecart, -1, 0.25) if ecart is not None else "neutre",
        "explication": "Le prix auquel la France emprunte : plus le taux est haut, plus la dette coûte cher à garder.",
    }


def _phrase_menages(etapes: list[dict], references: list[dict], synthese: dict) -> dict[str, Any] | None:
    if not etapes:
        return None
    dernier = etapes[-1]
    indice = dernier.get("pouvoir_achat_index")
    if indice is None:
        return None
    reference = (references[-1] if references else {}).get("pouvoir_achat_index")
    immobilier = synthese.get("taux_credit_immobilier_final")
    comparatif = ""
    if reference is not None and abs(indice - reference) >= SEUILS["indice"]:
        comparatif = (
            f", contre un indice {nombre(reference, 1)} sans réforme : "
            f"{nombre(abs(indice - reference), 1)} point {'de plus' if indice > reference else 'de moins'}"
        )
    credit = ""
    if immobilier is not None:
        credit = f" Le crédit immobilier reviendrait à {nombre(immobilier, 2)} %."
    return {
        "cle": "menages",
        "grandeur": "Pouvoir d'achat",
        "valeur": f"indice {nombre(indice, 1)} (départ 100)",
        "texte": (
            f"Le pouvoir d'achat se situerait à l'indice {nombre(indice, 1)} — 100 au "
            f"départ, ce qui veut dire qu'un même revenu permet d'acheter "
            f"{'davantage' if indice > 100 else 'moins'} qu'aujourd'hui"
            f"{comparatif}.{credit}"
        ),
        "niveau": _niveau(indice - (reference if reference is not None else 100.0), 1,
                          SEUILS["indice"]),
        "explication": "Indice construit par le modèle à partir des prix, des revenus et des prestations.",
    }


def _phrase_domaines(charge: dict) -> dict[str, Any] | None:
    domaines = charge.get("domaines") or []
    if not domaines:
        return None
    notes = [
        {"libelle": domaine.get("libelle", "domaine"), "score": float(domaine.get("score", 50.0))}
        for domaine in domaines
    ]
    if not notes:
        return None
    en_hausse = [note for note in notes if note["score"] > 50.0 + SEUILS["score"]]
    en_baisse = [note for note in notes if note["score"] < 50.0 - SEUILS["score"]]
    meilleur = max(notes, key=lambda note: note["score"])
    pire = min(notes, key=lambda note: note["score"])
    if not en_hausse and not en_baisse:
        texte = ("Aucun des vingt domaines d'action publique ne bouge de façon "
                 "mesurable par rapport à la trajectoire de référence.")
        niveau = "neutre"
    else:
        texte = (
            f"Sur {len(notes)} domaines d'action publique, {len(en_hausse)} "
            f"s'améliorent et {len(en_baisse)} se dégradent."
        )
        if en_hausse:
            texte += (
                f" Le plus aidé : {meilleur['libelle'].lower()} "
                f"({signe(meilleur['score'] - 50.0)}"
                f"{nombre(abs(meilleur['score'] - 50.0), 1)} point)."
            )
        # On ne désigne un « plus pénalisé » que s'il est réellement en baisse :
        # annoncer « le plus pénalisé : 0,0 point » ne voudrait rien dire.
        if en_baisse:
            texte += (
                f" Le plus pénalisé : {pire['libelle'].lower()} "
                f"({signe(pire['score'] - 50.0)}"
                f"{nombre(abs(pire['score'] - 50.0), 1)} point)."
            )
        niveau = "favorable" if len(en_hausse) > len(en_baisse) else (
            "defavorable" if len(en_baisse) > len(en_hausse) else "neutre"
        )
    return {
        "cle": "domaines",
        "grandeur": "Domaines d'action publique",
        "valeur": f"{len(en_hausse)} en hausse · {len(en_baisse)} en baisse",
        "texte": texte,
        "niveau": niveau,
        "explication": "Un score de 50 signifie « comme si de rien n'était » : c'est le zéro de l'écart, pas une appréciation.",
    }


def _phrase_social(synthese: dict) -> dict[str, Any] | None:
    tension = synthese.get("tension_finale")
    confiance = synthese.get("confiance_finale")
    if tension is None and confiance is None:
        return None
    morceaux = []
    if tension is not None:
        morceaux.append(f"la tension sociale se situerait à {nombre(tension, 0)} sur 100")
    if confiance is not None:
        morceaux.append(f"la confiance dans les institutions à {nombre(confiance, 0)} sur 100")
    texte = "Côté climat social, " + " et ".join(morceaux) + "."
    return {
        "cle": "social",
        "grandeur": "Climat social",
        "valeur": (f"tension {nombre(tension, 0)}/100" if tension is not None
                   else f"confiance {nombre(confiance, 0)}/100"),
        "texte": texte,
        "niveau": _niveau(50.0 - tension, 1, 5.0) if tension is not None else "neutre",
        "explication": "Grandeurs internes au modèle : elles traduisent des tensions mesurées ailleurs (fiscalité locale, services, censure), pas un sondage.",
    }


def _phrase_europe(synthese: dict) -> dict[str, Any] | None:
    statut = synthese.get("statut_pde")
    if statut is None or (isinstance(statut, str) and not statut.strip()):
        return None
    # Le moteur livre un booléen : vrai = sous procédure pour déficit excessif.
    sous_procedure = statut if isinstance(statut, bool) else (
        str(statut).strip().upper().startswith(("ALERTE", "EXCES", "DÉFICIT", "DEFICIT", "OUI", "VRAI"))
    )
    if sous_procedure:
        texte = ("La trajectoire resterait sous procédure européenne pour déficit "
                 "excessif : le déficit dépasse le plafond de 3 % du PIB retenu par "
                 "les règles communes.")
        niveau = "defavorable"
        libelle = "sous procédure"
    else:
        texte = ("La trajectoire resterait dans les limites des règles européennes "
                 "(déficit sous 3 % du PIB) : pas de procédure pour déficit excessif.")
        niveau = "favorable"
        libelle = "conforme"
    return {
        "cle": "europe",
        "grandeur": "Règles européennes",
        "valeur": libelle,
        "texte": texte,
        "niveau": niveau,
        "explication": "Le seuil de 3 % est une borne politique, pas une loi de la physique : plusieurs pays la dépassent durablement.",
    }


def _phrase_garde_fous(charge: dict) -> dict[str, Any] | None:
    diagnostic = charge.get("diagnostic") or {}
    strates = diagnostic.get("strates") or []
    niveau_global = diagnostic.get("niveau_global")
    alertes = diagnostic.get("alertes") or []
    if not strates and not niveau_global:
        return None
    libelles = {
        "favorable": "rien à signaler",
        "tolerable": "dans les limites suivies par le modèle",
        "vigilance": "à surveiller",
        "risque": "la trajectoire s'éloigne des repères",
        "hors_sol": "au-delà de ce que les sources permettent d'étayer",
    }
    seuils = len(alertes)
    pluriel = "s" if seuils > 1 else ""
    verbe = "appelle" if seuils == 1 else "appellent"
    texte = (
        f"Sur les garde-fous du simulateur, le niveau d'ensemble est « "
        f"{libelles.get(niveau_global, niveau_global)} » ; "
        f"{seuils} seuil{pluriel} {verbe} l'attention."
    )
    return {
        "cle": "garde_fous",
        "grandeur": "Signaux d'alerte",
        "valeur": f"{seuils} seuil{pluriel}",
        "texte": texte,
        "niveau": ("favorable" if niveau_global in ("favorable", "tolerable")
                   else ("defavorable" if niveau_global in ("risque", "hors_sol")
                         else "neutre")),
        "explication": "Les garde-fous sont des repères du modèle, gradués de « tolérable » à « hors-sol ». Ce ne sont pas des seuils officiels, sauf mention de la source.",
    }


def _resume(lignes: list[dict[str, Any]], synthese: dict) -> str:
    """Une phrase de synthèse, construite à partir des lignes disponibles."""
    favorables = [ligne for ligne in lignes if ligne["niveau"] == "favorable"]
    defavorables = [ligne for ligne in lignes if ligne["niveau"] == "defavorable"]
    solde = synthese.get("solde_mesures_mde")
    if not favorables and not defavorables:
        return ("Vos réglages ne changent presque rien par rapport à la "
                "trajectoire de référence : les écarts mesurés sont en dessous "
                "du seuil de lecture.")
    tete = ""
    if solde is not None and abs(solde) >= SEUILS["mde"]:
        tete = (f"Vos réglages {'dégagent' if solde > 0 else 'coûtent'} "
                f"{milliards(abs(solde))} par an. ")
    if favorables and not defavorables:
        return tete + "Toutes les grandeurs suivies évoluent dans le bon sens."
    if defavorables and not favorables:
        return tete + "Toutes les grandeurs suivies évoluent dans le sens inverse."
    # Les grandeurs sont citées telles quelles : leur ajouter un article
    # (« les règles européennes ») supposerait de connaître leur genre et leur
    # nombre. La forme nominale évite une faute de grammaire.
    # Le pluriel se construit à la main : « 1 grandeur(s) » se lit mal, et
    # une synthèse se lit plus qu'elle ne se parse.
    nom_hausse = "grandeur" + ("s" if len(favorables) > 1 else "")
    nom_baisse = "grandeur" + ("s" if len(defavorables) > 1 else "")
    hausse = ", ".join(ligne["grandeur"] for ligne in favorables[:3])
    baisse = ", ".join(ligne["grandeur"] for ligne in defavorables[:3])
    return (f"{tete}Le bilan est partagé : {len(favorables)} {nom_hausse} dans le bon "
            f"sens ({hausse}), {len(defavorables)} {nom_baisse} en sens inverse ({baisse}).")


def lecture_claire(charge: dict[str, Any]) -> dict[str, Any]:
    """Relit une sortie de simulation et la traduit en phrases ordinaires.

    Args:
        charge: une sortie de simulation sérialisée (``SortieSimulation.en_dict()``).

    Returns:
        Un dictionnaire ``{titre, horizon, resume, lignes, limites}``. Les
        grandeurs absentes de la charge sont simplement omises : une lecture
        courte vaut mieux qu'une lecture inventée.
    """
    if not isinstance(charge, dict):
        return {"titre": "Lecture indisponible", "horizon": None, "resume": "",
                "lignes": [], "limites": []}
    synthese = charge.get("synthese") or {}
    etapes = charge.get("etapes") or []
    references = charge.get("etapes_reference") or []
    horizon = charge.get("horizon") or len(etapes) or 5

    lignes: list[dict[str, Any]] = []
    for construire in (
        lambda: _phrase_budget(synthese),
        lambda: _phrase_deficit(synthese, horizon),
        lambda: _phrase_dette(synthese, horizon),
        lambda: _phrase_emprunt(synthese, charge.get("contexte") or {}),
        lambda: _phrase_menages(etapes, references, synthese),
        lambda: _phrase_domaines(charge),
        lambda: _phrase_social(synthese),
        lambda: _phrase_europe(synthese),
        lambda: _phrase_garde_fous(charge),
    ):
        try:
            ligne = construire()
        except Exception:  # pragma: no cover - la lecture ne doit jamais casser
            ligne = None
        if ligne:
            lignes.append(ligne)

    return {
        "titre": "Ce que disent les chiffres",
        "horizon": horizon,
        "resume": _resume(lignes, synthese),
        "lignes": lignes,
        "limites": [
            "Lecture automatique des résultats du modèle : chaque phrase reprend"
            " un chiffre déjà calculé, elle n'ajoute rien.",
            "Tout est mesuré par rapport à la trajectoire de référence (même"
            " moteur, leviers neutres) : les écarts ne sont pas des niveaux"
            " absolus.",
            "Un modèle n'est pas une prévision : deux hypothèses voisines"
            " peuvent donner des trajectoires éloignées.",
        ],
    }
