#!/usr/bin/env python3
"""Garde la passe de sources du 11 novembre 2026 honnête et vérifiable.

L’agent a tenté les 89 adresses uniques encore non ouvertes après la passe du
10 novembre 2026. Cette porte ne rejoue pas le réseau : elle confronte le
registre des ouvertures au catalogue, au registre des 81 relectures, au rapport
daté et au registre des seules relectures humaines, resté vide. Elle refuse
qu’une page d’erreur soit racontée comme une page de contenu, qu’une source
ouverte soit inventée, qu’un compte soit embelli ou qu’une URL externe soit
recopiée.

Les références sont des adresses sans schéma : les adresses exactes restent
dans `docs/apprentissage/catalogue.toml`, source de vérité. La racine peut être
surchargée par `MRSC_RACINE` pour le banc de mutation.

Usage :
    python3 outils/verifier-sources-ouvertes.py
"""

from __future__ import annotations

import os
import sys
import tomllib
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
REGISTRE_AGENT = RACINE / "docs" / "rd" / "relecture-agent-prototypes.toml"
REGISTRE_HUMAIN = RACINE / "docs" / "apprentissage" / "relectures.toml"
LEDGER = RACINE / "docs" / "rd" / "sources-ouvertes-2026-11-11.toml"
RAPPORT = RACINE / "docs" / "rd" / "sources-ouvertes-2026-11-11.md"
COMPLEMENT = RACINE / "docs" / "rd" / "sources-complement-2026-11-11.toml"
RAPPORT_COMPLEMENT = RACINE / "docs" / "rd" / "sources-complement-2026-11-11.md"
TROISIEME = RACINE / "docs" / "rd" / "sources-ign-2026-11-11.toml"
RAPPORT_TROISIEME = RACINE / "docs" / "rd" / "sources-ign-2026-11-11.md"

STATUTS = {"contenu", "page-erreur-servie", "echec-recuperation"}
DEJA_OUVERTES = frozenset({
    "docs.python.org/3/library/statistics.html",
    "guides.data.gouv.fr/ecologie.data.gouv.fr/ecologie.data.gouv.fr/indicateurs-phares/utiliser-un-indicateur/comprendre-un-indicateur",
    "meteofrance.com/meteo-a-z/quelle-difference-entre-meteo-et-climat",
    "www.ameli.fr/assure/remboursements/rembourse/consultations-telemedecine/metropole",
    "www.ameli.fr/assure/sante/bons-gestes/seniors/prevenir-chutes-personnes-agees",
    "www.cnil.fr/fr",
    "www.cybermalveillance.gouv.fr/tous-nos-contenus/bonnes-pratiques/sauvegardes",
    "www.economie.gouv.fr/dgccrf",
    "www.education.gouv.fr/le-socle-commun-de-connaissances-de-competences-et-de-culture-12512",
    "www.francecompetences.fr/app/uploads/2026/01/Vademecum-VF_2026.pdf",
    "www.inrs.fr/publications/essentiels/CLP.html",
    "www.inrs.fr/risques/electriques/prevention-risque-electrique.html",
    "www.legifrance.gouv.fr/",
    "www.santepubliquefrance.fr/maladies-et-traumatismes/cancers/cancer-du-sein/articles/taux-de-participation-au-programme-de-depistage-organise-du-cancer-du-sein-en-2022-2023-et-evolution-depuis-2005",
    "www.service-public.gouv.fr/",
    "www.service-public.gouv.fr/particuliers/vosdroits/F1427",
})
ERREURS_SERVIES = frozenset({
    "developer.mozilla.org/fr/docs/Glossary/Byte",
    "www.assurance-maladie.ameli.fr/index.php/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant",
    "www.hceres.fr/fr/ofis",
})
ECHECS = frozenset({
    "extranet.inao.gouv.fr/fichier/Plaquette-SIQO-francais.pdf",
    "www.education.gouv.fr/media/199172/download",
    "www.ign.fr/",
})
TRANCHE_SUPPLEMENTAIRE = "eduscol.education.gouv.fr/5745/ressources-d-accompagnement-du-programme-de-technologie-au-cycle-4"
INTERDITES = (
    "https://", "http://", "validation humaine obtenue", "conforme",
    "tout est relu", "R&D terminée", "projet achevé", "statut promu",
    "essai avec des personnes réalisé", "avis juridique rendu", "expertise acquise",
)
REPERES = (
    "11 novembre 2026", "89 adresses", "105 / 105", "83 pages de contenu",
    "3 pages d’erreur servies", "3 erreurs de récupération",
    "6 adresses sans contenu", "relu-par-agent", "Prototype à relire",
    "Aucune URL externe nouvelle",
)

# Complément du 11 novembre 2026, seconde passe : les six adresses restées sans
# contenu confrontable sont reprises une à une. Un résultat de recherche ne vaut
# pas une page lue ; une page d'accueil ne vaut pas la résolution d'une source.
INDISPONIBLES = ERREURS_SERVIES | ECHECS
ETATS_COMPLEMENT = {
    "extranet.inao.gouv.fr/fichier/Plaquette-SIQO-francais.pdf": "remplacement-partiel",
    "www.education.gouv.fr/media/199172/download": "remplacement-partiel",
    "www.ign.fr/": "aucune-page-lue",
    "developer.mozilla.org/fr/docs/Glossary/Byte": "contexte-officiel",
    "www.assurance-maladie.ameli.fr/index.php/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant": "remplacement-exact",
    "www.hceres.fr/fr/ofis": "remplacement-exact",
}
ANCIENS_STATUTS = {ref: ("page-erreur-servie" if ref in ERREURS_SERVIES else "echec-recuperation")
                   for ref in INDISPONIBLES}
LECTURES_ATTENDUES = frozenset({
    "www.inao.gouv.fr/",
    "www.inao.gouv.fr/aop-appellation-origine-protegee",
    "www.inao.gouv.fr/label-rouge",
    "www.inao.gouv.fr/igp-indication-geographique-protegee",
    "eduscol.education.gouv.fr/5712/ressources-d-accompagnement-du-programme-de-mathematiques-au-cycle-3",
    "www.education.gouv.fr/sites/default/files/programme-de-math-matiques-pour-le-cycle-3-439827.pdf",
    "www.ameli.fr/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant",
    "www.ameli.fr/assure/remboursements/etre-bien-rembourse/medecin-traitant-parcours-soins-coordonnes",
    "www.hceres.fr/fr/office-francais-de-lintegrite-scientifique",
    "www.hceres.fr/fr/integrite-scientifique",
    "www.hceres.fr/fr/dossiers-et-communiques/le-college-du-hceres-valide-la-creation-de-loffice-francais-dintegrite",
    "www.hceres.fr/fr/sitemap",
    "www.ofis-france.fr/",
    "developer.mozilla.org/en-US/docs/Glossary/Endianness",
    "developer.mozilla.org/en-US/docs/Glossary/Base64",
    "developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Global_Objects/TypedArray",
})
POUR_ATTENDUS = {"retentative", "remplacement", "contexte"}
FICHES_COMPLEMENT = frozenset({
    "sante-reperer-signes-qualite-origine", "maths-convertir-unites",
    "geo-decrire-paysage", "geo-lire-legende-carte", "info-bits-octets",
    "sante-comprendre-parcours-soins", "recherche-conserver-reference",
})
REPERES_COMPLEMENT = (
    "11 novembre 2026", "16 pages officielles lues", "1 adresse sans page lue",
    "aucune fiche modifiée", "aucun statut promu", "Aucune URL externe nouvelle",
    "HTTP 403", "HTTP 500", "Page non trouvée",
    "docs/rd/sources-ouvertes-2026-11-11.md", "9 situations",
)
FICHES_IGN = ("geo-decrire-paysage", "geo-lire-legende-carte")
TITRE_IGN = "Institut national de l’information géographique et forestière — IGN"
STATUTS_TROISIEME = {"http-403", "redirection", "page-erreur-servie", "contenu-generique"}
LECTURES_IGN = frozenset({
    "cartes.gouv.fr/explorer-les-cartes/",
    "cartes.gouv.fr/actualites/clap-de-fin-pour-le-geoportail-bienvenue-sur-cartesgouvfr",
    "cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2026-01-scan-25/",
    "cartes.gouv.fr/aide/fr/guides-utilisateur/visualiseur-cartographique/generalites-visualiseur/",
    "cartes.gouv.fr/decouvrir/explorer-les-cartes/",
    "cartes.gouv.fr/decouvrir/",
    "cartes.gouv.fr/aide/fr/partenaires/ign/referentiels-description-territoire/occupation-sol-topographie/ocs-ge-nouvelle-generation/",
    "cartes.gouv.fr/aide/fr/partenaires/ign/generalites-ign/actualites/2026-07-plan-ign-hd-et-sentiers/",
    "data.geopf.fr/annexes/ressources/documentation/Legende2026.pdf",
    "data.geopf.fr/annexes/ressources/fiches/cartesIGN/composition_donnee_cartes_ign_classiques.pdf",
})
REPERES_TROISIEME = (
    "11 novembre 2026", "troisième passe", "16 h 14 UTC", "13 réponses HTTP 403",
    "10 pages officielles réellement lues", "Aucune fiche modifiée",
    "aucun statut promu", "Aucune URL externe nouvelle", "www.ign.fr/",
    "11 situations", "date ultérieure", "docs/rd/sources-complement-2026-11-11.md",
)
#: « aucun statut promu » est la formulation honnête du complément ; seule la
#: promotion elle-même est interdite, pas sa négation écrite noir sur blanc.
INTERDITES_COMPLEMENT = tuple(x for x in INTERDITES if x != "statut promu")


def reference(url: str) -> str:
    """Retire le schéma d’une adresse pour ne pas la recopier."""
    return url.split("://", 1)[-1]


def statut_attendu(ref: str) -> str:
    if ref in ERREURS_SERVIES:
        return "page-erreur-servie"
    if ref in ECHECS:
        return "echec-recuperation"
    return "contenu"


def charger(chemin: Path, erreurs: list[str]) -> dict:
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        erreurs.append(f"{chemin.relative_to(RACINE)} illisible : {erreur}")
        return {}


def controler_complement(refs_catalogue: set[str], prototypes: set[str],
                         erreurs: list[str]) -> None:
    """Confronte le complément de la seconde passe du 11 novembre 2026.

    Aucune lecture n'est rejouée ici : la porte vérifie que les 16 pages dites
    lues sont consignées, datées et rattachées, que les 6 adresses sans contenu
    restent nommées, qu'aucune adresse de remplacement n'a été glissée dans le
    catalogue, et qu'un accueil ne suffit pas à déclarer une source résolue.
    """
    complement = charger(COMPLEMENT, erreurs)
    if erreurs:
        return
    meta = complement.get("meta", {})
    comptes = {
        "dossiers": 6, "lectures": 16, "remplacements_exacts": 2,
        "remplacements_partiels": 2, "contextes_officiels": 1,
        "sans_page_lue": 1, "pages_officielles_lues": 16,
        "fiches_modifiees": 0, "statuts_promus": 0,
        "urls_externes_recopiees": 0, "anciennes_adresses_sans_contenu": 6,
        "retentatives_effectuees": 3, "erreurs_servies_traitees": 3,
    }
    for champ, valeur in comptes.items():
        if meta.get(champ) != valeur:
            erreurs.append(f"complément : meta « {champ} » annoncée à tort : {meta.get(champ)} au lieu de {valeur}")
    if meta.get("auteur") != "agent" or str(meta.get("date")) != "2026-11-11":
        erreurs.append("complément : auteur ou date du complément absent")
    if meta.get("registre_principal") != "docs/rd/sources-ouvertes-2026-11-11.toml":
        erreurs.append("complément : registre principal non nommé")
    if complement.get("relecture"):
        erreurs.append("complément : un registre de relectures humaines n'a pas à y être copié")

    lectures = complement.get("lecture", [])
    refs_lectures: set[str] = set()
    if len(lectures) != 16:
        erreurs.append(f"complément : {len(lectures)} lecture(s) consignée(s) au lieu de 16")
    for lecture in lectures:
        ref = str(lecture.get("reference", ""))
        if ref in refs_lectures:
            erreurs.append(f"complément : lecture consignée deux fois : {ref}")
        refs_lectures.add(ref)
        if "://" in ref or not ref or ref.startswith("/"):
            erreurs.append(f"complément : référence de lecture avec schéma ou vide : {ref}")
        if lecture.get("ancienne_reference") not in INDISPONIBLES:
            erreurs.append(f"complément : lecture sans ancienne adresse indisponible : {ref}")
        if lecture.get("pour") not in POUR_ATTENDUS:
            erreurs.append(f"complément : motif de lecture inconnu : {ref}")
        fiches = lecture.get("fiches", [])
        if not fiches or not set(fiches) <= prototypes:
            erreurs.append(f"complément : fiches inconnues ou absentes pour la lecture {ref}")
        for champ in ("organisme", "titre", "date_page", "repere"):
            if len(str(lecture.get(champ, ""))) < 2:
                erreurs.append(f"complément : champ « {champ} » absent pour la lecture {ref}")
        if not str(lecture.get("tranche", "")):
            erreurs.append(f"complément : tranche de lecture absente pour {ref}")
    if refs_lectures != LECTURES_ATTENDUES:
        manquantes = sorted(LECTURES_ATTENDUES - refs_lectures)
        inventees = sorted(refs_lectures - LECTURES_ATTENDUES)
        erreurs.append(
            "complément : lecture de remplacement absente ou inventée : "
            + ", ".join(manquantes + inventees)
        )
    intruses = refs_lectures & refs_catalogue
    if intruses:
        erreurs.append("complément : adresse de remplacement ajoutée au catalogue : " + ", ".join(sorted(intruses)))
    if "www.ign.fr/" in refs_lectures:
        erreurs.append("complément : accueil IGN raconté comme une page de remplacement lue")
    par_ref = {str(l.get("reference", "")): l for l in lectures}
    if par_ref.get("www.inao.gouv.fr/", {}).get("pour") != "retentative":
        erreurs.append("complément : l'accueil INAO n'est pas nommé comme simple retentative")

    dossiers = complement.get("dossier", [])
    vus: set[str] = set()
    etats: dict[str, int] = {}
    toutes_fiches: set[str] = set()
    if len(dossiers) != 6:
        erreurs.append(f"complément : {len(dossiers)} dossier(s) au lieu de 6")
    for dossier in dossiers:
        ref = str(dossier.get("reference", ""))
        if ref in vus:
            erreurs.append(f"complément : dossier consigné deux fois : {ref}")
        vus.add(ref)
        if ref not in INDISPONIBLES:
            erreurs.append(f"complément : dossier pour une adresse inattendue : {ref}")
            continue
        if dossier.get("ancien_statut") != ANCIENS_STATUTS[ref]:
            erreurs.append(f"complément : ancien statut embelli ou inversé pour {ref}")
        etat = str(dossier.get("nouveau_statut", ""))
        etats[etat] = etats.get(etat, 0) + 1
        if etat != ETATS_COMPLEMENT[ref]:
            erreurs.append(f"complément : résultat de seconde passe inexact pour {ref} : {etat}")
        pages = dossier.get("pages_lues", [])
        if not set(pages) <= refs_lectures:
            erreurs.append(f"complément : page non lue citée comme lue pour {ref}")
        if etat == "aucune-page-lue" and pages:
            erreurs.append(f"complément : {ref} déclarée sans page lue mais en cite {len(pages)}")
        if etat == "remplacement-exact" and not any("/" in p.split("/")[-1] or p.count("/") > 1 for p in pages):
            erreurs.append(f"complément : remplacement exact réduit à une page d'accueil pour {ref}")
        fiches = dossier.get("fiches", [])
        if not fiches or not set(fiches) <= prototypes:
            erreurs.append(f"complément : fiches inconnues ou absentes pour le dossier {ref}")
        toutes_fiches.update(fiches)
        for champ in ("repere", "limite"):
            if len(str(dossier.get(champ, ""))) < 20:
                erreurs.append(f"complément : champ « {champ} » trop court pour {ref}")
    if vus != INDISPONIBLES:
        erreurs.append("complément : adresse sans contenu non reprise : " + ", ".join(sorted(INDISPONIBLES - vus)))
    for etat, nombre in (("remplacement-exact", 2), ("remplacement-partiel", 2),
                         ("contexte-officiel", 1), ("aucune-page-lue", 1)):
        if etats.get(etat, 0) != nombre:
            erreurs.append(f"complément : {etats.get(etat, 0)} dossier(s) « {etat} » au lieu de {nombre}")
    if toutes_fiches != FICHES_COMPLEMENT:
        erreurs.append("complément : fiches de la seconde passe incohérentes avec le catalogue")

    textes = ((COMPLEMENT, COMPLEMENT.read_text(encoding="utf-8")),
              (RAPPORT_COMPLEMENT, RAPPORT_COMPLEMENT.read_text(encoding="utf-8")))
    for chemin, texte in textes:
        if "https://" in texte or "http://" in texte:
            erreurs.append(f"{chemin.relative_to(RACINE)} : URL externe recopiée")
        for interdite in INTERDITES_COMPLEMENT:
            if interdite.lower() in texte.lower():
                erreurs.append(f"{chemin.relative_to(RACINE)} : formulation interdite « {interdite} »")
    rapport_texte = textes[1][1]
    for repere in REPERES_COMPLEMENT:
        if repere not in rapport_texte:
            erreurs.append(f"rapport du complément : repère absent « {repere} »")
    for ref in sorted(LECTURES_ATTENDUES):
        if ref not in rapport_texte:
            erreurs.append(f"rapport du complément : lecture absente du relevé : {ref}")



def controler_troisieme(refs_catalogue: set[str], prototypes: set[str],
                        agent: dict, erreurs: list[str]) -> None:
    """Confronte la troisième passe : l'accueil IGN n'est pas déclaré résolu.

    Un domaine officiel de remplacement ne vaut pas l'ouverture de l'adresse
    déclarée. La porte vérifie le décompte des 403, les 10 pages datées,
    l'absence de toute modification de fiche ou de catalogue, et le maintien
    de la source IGN dans `sources_indisponibles` des deux fiches.
    """
    troisieme = charger(TROISIEME, erreurs)
    if erreurs:
        return
    meta = troisieme.get("meta", {})
    comptes = {
        "tentatives": 17, "http_403": 13, "redirections": 1,
        "pages_erreur_servies": 1, "contenus_generiques": 2,
        "pages_lues": 10, "confrontations": 2, "fiches_modifiees": 0,
        "adresses_ajoutees_catalogue": 0, "rattachements_agent_modifies": 0,
        "statuts_promus": 0, "urls_externes_recopiees": 0,
    }
    for champ, valeur in comptes.items():
        if meta.get(champ) != valeur:
            erreurs.append(f"troisième passe : meta « {champ} » annoncée à tort : {meta.get(champ)} au lieu de {valeur}")
    if meta.get("auteur") != "agent" or str(meta.get("date")) != "2026-11-11":
        erreurs.append("troisième passe : auteur ou date absent")
    if meta.get("adresse_declaree") != "www.ign.fr/":
        erreurs.append("troisième passe : adresse déclarée IGN absente ou remplacée")
    if sorted(meta.get("fiches", [])) != sorted(FICHES_IGN):
        erreurs.append("troisième passe : fiches de géographie absentes ou inventées")
    if troisieme.get("relecture"):
        erreurs.append("troisième passe : un registre de relectures humaines n'a pas à y être copié")

    tentatives = troisieme.get("tentative", [])
    vues: set[str] = set()
    statuts: dict[str, int] = {}
    if len(tentatives) != 17:
        erreurs.append(f"troisième passe : {len(tentatives)} tentative(s) au lieu de 17")
    for tentative in tentatives:
        ref = str(tentative.get("reference", ""))
        if ref in vues:
            erreurs.append(f"troisième passe : tentative consignée deux fois : {ref}")
        vues.add(ref)
        if "://" in ref or not ref:
            erreurs.append(f"troisième passe : référence de tentative avec schéma ou vide : {ref}")
        statut = str(tentative.get("statut", ""))
        statuts[statut] = statuts.get(statut, 0) + 1
        if statut not in STATUTS_TROISIEME:
            erreurs.append(f"troisième passe : statut de tentative embelli ou inconnu : {ref} : {statut}")
        if len(str(tentative.get("repere", ""))) < 20:
            erreurs.append(f"troisième passe : repère de tentative trop court : {ref}")
    for statut, nombre in (("http-403", 13), ("redirection", 1),
                           ("page-erreur-servie", 1), ("contenu-generique", 2)):
        if statuts.get(statut, 0) != nombre:
            erreurs.append(f"troisième passe : {statuts.get(statut, 0)} tentative(s) « {statut} » au lieu de {nombre}")
    if "www.ign.fr/" not in vues:
        erreurs.append("troisième passe : l'accueil déclaré n'a pas été retenté")
    elif next(x for x in tentatives if x.get("reference") == "www.ign.fr/").get("statut") != "http-403":
        erreurs.append("troisième passe : accueil IGN raconté comme lisible")

    lectures = troisieme.get("lecture", [])
    refs_lues: set[str] = set()
    if len(lectures) != 10:
        erreurs.append(f"troisième passe : {len(lectures)} lecture(s) au lieu de 10")
    for lecture in lectures:
        ref = str(lecture.get("reference", ""))
        if ref in refs_lues:
            erreurs.append(f"troisième passe : lecture consignée deux fois : {ref}")
        refs_lues.add(ref)
        if "://" in ref:
            erreurs.append(f"troisième passe : référence de lecture avec schéma : {ref}")
        if lecture.get("pour") != "contexte-officiel":
            erreurs.append(f"troisième passe : motif de lecture inattendu : {ref}")
        if not set(lecture.get("fiches", [])) <= set(FICHES_IGN) & prototypes:
            erreurs.append(f"troisième passe : fiches inconnues ou absentes pour {ref}")
        for champ in ("organisme", "titre", "date_page", "repere", "limite"):
            if len(str(lecture.get(champ, ""))) < 2:
                erreurs.append(f"troisième passe : champ « {champ} » absent pour {ref}")
        if not str(lecture.get("tranche", "")):
            erreurs.append(f"troisième passe : tranche de lecture absente pour {ref}")
    if refs_lues != LECTURES_IGN:
        erreurs.append("troisième passe : lecture officielle absente ou inventée : "
                       + ", ".join(sorted(LECTURES_IGN ^ refs_lues)))
    if "www.ign.fr/" in refs_lues:
        erreurs.append("troisième passe : accueil IGN raconté comme une page lue")
    if refs_lues & refs_catalogue:
        erreurs.append("troisième passe : adresse de remplacement ajoutée au catalogue")

    confrontations = troisieme.get("confrontation", [])
    if len(confrontations) != 2 or sorted(str(c.get("fiche")) for c in confrontations) != sorted(FICHES_IGN):
        erreurs.append("troisième passe : confrontation des deux fiches absente ou inventée")
    for c in confrontations:
        if c.get("verdict") != "contexte-officiel-consigne":
            erreurs.append(f"troisième passe : verdict de confrontation inexact pour {c.get('fiche')}")
        if len(str(c.get("suite", ""))) < 20 or len(str(c.get("confrontation", ""))) < 20:
            erreurs.append(f"troisième passe : confrontation trop courte pour {c.get('fiche')}")
    limites = troisieme.get("limite", [])
    if len(limites) != 6:
        erreurs.append(f"troisième passe : {len(limites)} limite(s) au lieu de 6")
    texte_limites = " ".join(str(l.get("texte", "")) for l in limites)
    for repere in ("HTTP 403", "date ultérieure", "aucune fiche"):
        if repere not in texte_limites:
            erreurs.append(f"troisième passe : limite absente « {repere} »")

    # La source-portail reste indisponible dans le registre des 81 fiches.
    par_fiche = {str(e.get("fiche")): e for e in agent.get("relecture", [])}
    for identifiant in FICHES_IGN:
        entree = par_fiche.get(identifiant, {})
        if TITRE_IGN not in entree.get("sources_indisponibles", []):
            erreurs.append(f"troisième passe : {identifiant} : source-portail IGN déclarée résolue")
        if any("cartes.gouv.fr" in str(s) or "geopf.fr" in str(s)
               for s in entree.get("sources_ouvertes", [])):
            erreurs.append(f"troisième passe : {identifiant} : rattachement de remplacement inventé")
        if entree.get("verdict") != "a-trancher" or entree.get("sources_non_ouvertes") != 1:
            erreurs.append(f"troisième passe : {identifiant} : verdict ou compte modifié sans registre humain")

    textes = ((TROISIEME, TROISIEME.read_text(encoding="utf-8")),
              (RAPPORT_TROISIEME, RAPPORT_TROISIEME.read_text(encoding="utf-8")))
    for chemin, texte in textes:
        if "https://" in texte or "http://" in texte:
            erreurs.append(f"{chemin.relative_to(RACINE)} : URL externe recopiée")
        for interdite in INTERDITES_COMPLEMENT:
            if interdite.lower() in texte.lower():
                erreurs.append(f"{chemin.relative_to(RACINE)} : formulation interdite « {interdite} »")
    rapport = textes[1][1]
    for repere in REPERES_TROISIEME:
        if repere not in rapport:
            erreurs.append(f"rapport de la troisième passe : repère absent « {repere} »")
    for ref in sorted(LECTURES_IGN):
        if ref not in rapport:
            erreurs.append(f"rapport de la troisième passe : lecture absente du relevé : {ref}")

def controler() -> list[str]:
    erreurs: list[str] = []
    for chemin in (CATALOGUE, REGISTRE_AGENT, REGISTRE_HUMAIN, LEDGER, RAPPORT,
                   COMPLEMENT, RAPPORT_COMPLEMENT, TROISIEME, RAPPORT_TROISIEME):
        if not chemin.is_file():
            erreurs.append(f"fichier absent : {chemin.relative_to(RACINE)}")
    if erreurs:
        return erreurs

    catalogue = charger(CATALOGUE, erreurs)
    agent = charger(REGISTRE_AGENT, erreurs)
    humain = charger(REGISTRE_HUMAIN, erreurs)
    ledger = charger(LEDGER, erreurs)
    charger(COMPLEMENT, erreurs)
    charger(TROISIEME, erreurs)
    if erreurs:
        return erreurs
    if humain.get("relecture"):
        erreurs.append("registre humain écrit : un agent n’y inscrit aucune relecture")

    prototypes = [f for f in catalogue.get("fiche", []) if f.get("statut_editorial") == "Prototype à relire"]
    if len(prototypes) != 81:
        erreurs.append(f"catalogue : {len(prototypes)} prototypes au lieu de 81")
    par_url: dict[str, dict] = {}
    urls = set()
    for fiche in prototypes:
        for source in fiche.get("sources", []):
            url = str(source.get("url", ""))
            urls.add(url)
            entree = par_url.setdefault(url, {"titres": set(), "fiches": set()})
            entree["titres"].add(str(source.get("titre", "")))
            entree["fiches"].add(str(fiche.get("id", "")))
    if len(urls) != 105:
        erreurs.append(f"catalogue : {len(urls)} adresses uniques au lieu de 105")
    refs_catalogue = {reference(u) for u in urls}
    inconnues = DEJA_OUVERTES - refs_catalogue
    if inconnues:
        erreurs.append("adresses déjà ouvertes absentes du catalogue : " + ", ".join(sorted(inconnues)))
    attendus = refs_catalogue - DEJA_OUVERTES
    if len(attendus) != 89:
        erreurs.append(f"passe du 11 novembre : {len(attendus)} adresses attendues au lieu de 89")

    meta = ledger.get("meta", {})
    comptes = {
        "adresses_deja_ouvertes": len(DEJA_OUVERTES),
        "adresses_tentees": 89,
        "pages_contenu": 83,
        "pages_erreur_servies": 3,
        "echecs_recuperation": 3,
        "adresses_sans_contenu": 6,
        "adresses_uniques_catalogue": 105,
    }
    for champ, valeur in comptes.items():
        if meta.get(champ) != valeur:
            erreurs.append(f"meta : {champ} annoncé à tort : {meta.get(champ)} au lieu de {valeur}")
    if meta.get("auteur") != "agent" or str(meta.get("date")) != "2026-11-11":
        erreurs.append("meta : auteur ou date de la passe de sources absent")
    if meta.get("registre_agent") != "docs/rd/relecture-agent-prototypes.toml":
        erreurs.append("meta : registre d’agent de la passe précédente non nommé")

    entrees = ledger.get("ouverture", [])
    vues: set[str] = set()
    compte_statuts = {statut: 0 for statut in STATUTS}
    for entree in entrees:
        ref = str(entree.get("reference", ""))
        if ref in vues:
            erreurs.append(f"adresse de source consignée deux fois : {ref}")
        vues.add(ref)
        if ref not in attendus:
            erreurs.append(f"adresse de source inattendue dans le registre : {ref}")
            continue
        url = next(u for u in urls if reference(u) == ref)
        attendu = par_url[url]
        statut = entree.get("statut")
        if statut not in STATUTS:
            erreurs.append(f"{ref} : statut inconnu « {statut} »")
            continue
        compte_statuts[statut] += 1
        if statut != statut_attendu(ref):
            erreurs.append(f"{ref} : statut de source embelli ou inversé : {statut}")
        if sorted(entree.get("titres", [])) != sorted(attendu["titres"]):
            erreurs.append(f"{ref} : titres déclarés incohérents avec le catalogue")
        if sorted(entree.get("fiches", [])) != sorted(attendu["fiches"]):
            erreurs.append(f"{ref} : fiches rattachees incohérentes avec le catalogue")
        tranche = entree.get("tranche")
        if ref == TRANCHE_SUPPLEMENTAIRE:
            if tranche != "0,1":
                erreurs.append(f"{ref} : la deuxième tranche lue n’est pas consignée")
        elif tranche != 0:
            erreurs.append(f"{ref} : tranche de lecture inattendue : {tranche}")
        if len(str(entree.get("repere", ""))) < 20:
            erreurs.append(f"{ref} : repère de lecture trop court")
    manquantes = attendus - vues
    if manquantes:
        erreurs.append("adresse de source absente du registre : " + ", ".join(sorted(manquantes)))
    for statut, nombre in compte_statuts.items():
        if nombre != comptes[{"contenu": "pages_contenu", "page-erreur-servie": "pages_erreur_servies", "echec-recuperation": "echecs_recuperation"}[statut]]:
            erreurs.append(f"registre : {nombre} entrées « {statut} » au lieu du compte annoncé")

    # Le registre des 81 fiches doit porter exactement les rattachements de la passe.
    entrees_agent = agent.get("relecture", [])
    if len(entrees_agent) != 81:
        erreurs.append(f"registre d’agent : {len(entrees_agent)} relectures au lieu de 81")
    verdicts = {"a-trancher": 0, "relue-sans-ecart": 0}
    par_fiche: dict[str, dict] = {}
    for fiche in prototypes:
        identifiant = str(fiche.get("id", ""))
        ouvertes, indisponibles = [], []
        for source in fiche.get("sources", []):
            ref = reference(str(source.get("url", "")))
            if ref in DEJA_OUVERTES or (ref in attendus and statut_attendu(ref) == "contenu"):
                ouvertes.append(str(source.get("titre", "")))
            elif ref in attendus:
                indisponibles.append(str(source.get("titre", "")))
            else:
                erreurs.append(f"{identifiant} : adresse du catalogue absente des deux passes : {ref}")
        par_fiche[identifiant] = {
            "ouvertes": sorted(ouvertes),
            "indisponibles": sorted(indisponibles),
            "non_ouvertes": len(fiche.get("sources", [])) - len(ouvertes),
        }
    for entree in entrees_agent:
        identifiant = str(entree.get("fiche", "?"))
        if identifiant not in par_fiche:
            erreurs.append(f"relecture d’agent pour une fiche inconnue : {identifiant}")
            continue
        verdicts[entree.get("verdict")] = verdicts.get(entree.get("verdict"), 0) + 1
        attendu = par_fiche[identifiant]
        if sorted(entree.get("sources_ouvertes", [])) != attendu["ouvertes"]:
            erreurs.append(f"{identifiant} : source ouverte inventée ou manquante")
        if sorted(entree.get("sources_indisponibles", [])) != attendu["indisponibles"]:
            erreurs.append(f"{identifiant} : adresse sans contenu non consignée ou inventée")
        if entree.get("sources_non_ouvertes") != attendu["non_ouvertes"]:
            erreurs.append(f"{identifiant} : sources_non_ouvertes incohérent")
        if str(entree.get("passe_sources")) != "2026-11-11":
            erreurs.append(f"{identifiant} : passe_sources absente ou datée à tort")
        constat = str(entree.get("constat", ""))
        limite = str(entree.get("limite", ""))
        suite = str(entree.get("suite", ""))
        if "Le 11 novembre 2026" not in constat or "83 pages de contenu" not in constat:
            erreurs.append(f"{identifiant} : constat sans trace de la passe de sources")
        if "sans contenu confrontable après la passe du 11 novembre 2026" not in limite:
            erreurs.append(f"{identifiant} : limite sans trace de la passe de sources")
        if "docs/rd/sources-ouvertes-2026-11-11.md" not in suite:
            erreurs.append(f"{identifiant} : suite sans renvoi au rapport de la passe")
        for champ in (constat, limite, suite):
            if "https://" in champ or "http://" in champ:
                erreurs.append(f"{identifiant} : URL externe recopiée dans la relecture")
    if verdicts.get("a-trancher") != 40 or verdicts.get("relue-sans-ecart") != 41:
        erreurs.append("verdicts du 10 novembre modifiés sans registre humain")

    rapport = RAPPORT.read_text(encoding="utf-8")
    for repere in REPERES:
        if repere not in rapport:
            erreurs.append(f"rapport : repère absent « {repere} »")
    for ref in sorted(attendus):
        if ref not in rapport:
            erreurs.append(f"rapport : référence de la passe absente : {ref}")
    for interdite in INTERDITES:
        if interdite.lower() in rapport.lower():
            if interdite in ("https://", "http://"):
                erreurs.append("rapport : URL externe recopiée")
            else:
                erreurs.append(f"rapport : formulation interdite « {interdite} »")
    ledger_texte = LEDGER.read_text(encoding="utf-8")
    for interdite in INTERDITES:
        if interdite.lower() in ledger_texte.lower():
            if interdite in ("https://", "http://"):
                erreurs.append("registre des ouvertures : URL externe recopiée")
            else:
                erreurs.append(f"registre des ouvertures : formulation interdite « {interdite} »")

    meta_agent = agent.get("meta", {})
    if str(meta_agent.get("passe_sources")) != "2026-11-11":
        erreurs.append("meta du registre d’agent : passe_sources absente")
    if meta_agent.get("registre_sources") != "docs/rd/sources-ouvertes-2026-11-11.toml":
        erreurs.append("meta du registre d’agent : registre des sources non nommé")
    if meta_agent.get("rapport_sources") != "docs/rd/sources-ouvertes-2026-11-11.md":
        erreurs.append("meta du registre d’agent : rapport des sources non nommé")

    ids_prototypes = {str(f.get("id", "")) for f in prototypes}
    controler_complement(refs_catalogue, ids_prototypes, erreurs)
    controler_troisieme(refs_catalogue, ids_prototypes, agent, erreurs)
    return erreurs


def main() -> int:
    erreurs = controler()
    if erreurs:
        print("ÉCHEC — passe de sources du 11 novembre 2026", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    print("Sources ouvertes vérifiées : 89 adresses tentées, 83 contenus, 3 pages d’erreur servies, "
          "3 erreurs de récupération, 105 / 105 adresses du catalogue tentées ; "
          "complément : 6 dossiers, 16 pages officielles lues, 1 adresse sans page lue, "
          "aucune adresse de remplacement au catalogue ; troisième passe : 17 tentatives, "
          "13 HTTP 403, 10 pages officielles lues, accueil IGN toujours fermé, "
          "aucun registre humain écrit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
