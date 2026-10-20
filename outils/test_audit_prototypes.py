#!/usr/bin/env python3
"""Tests de l'audit automatique des prototypes.

Un audit qui ne signale jamais rien est un audit décoratif. Ces tests vérifient
que chaque contrôle mord sur une fiche volontairement abîmée, et que les
constats restent des constats — jamais des validations.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import unittest
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from statuts_editoriaux import PROTOTYPE  # noqa: E402


def charger_module():
    specification = importlib.util.spec_from_file_location(
        "audit_prototypes", RACINE / "outils" / "auditer-prototypes.py"
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


MODULE = charger_module()
AUJOURDHUI = date(2026, 10, 20)


def fiche_valide() -> dict:
    return {
        "id": "demo-fiche",
        "titre": "Une fiche de démonstration courte",
        "matiere": "Démonstration",
        "matiere_id": "methodes",
        "domaine": "methodes-communication",
        "niveau": 2,
        "statut_editorial": PROTOTYPE,
        "note_statut_editorial": "Prototype de test, sans relecture.",
        "minutes": 10,
        "resume": "Un résumé court pour vérifier la longueur.",
        "objectif": "Vérifier un contrôle automatique.",
        "situation": "Une situation fictive de test.",
        "analogie_titre": "Comme un banc d'essai",
        "analogie": "On essaie une pièce avant de la monter.",
        "limite_analogie": (
            "L'image ne dit pas si la pièce tiendra : elle montre seulement qu'un essai précède le montage, "
            "et elle ne remplace ni une mesure ni l'avis de la personne qui utilisera l'objet."
        ),
        "notions": ["Notion une.", "Notion deux."],
        "demarche": ["Première étape.", "Deuxième étape."],
        "exercice": "Choisis la bonne réponse.",
        "aide": "Relis la première étape.",
        "correction": ["Réponse juste, avec la raison.", "Réponse fausse, avec la raison."],
        "a_retenir": ["Un repère.", "Une limite."],
        "transferer": "À réutiliser ailleurs.",
        "revue_le": "2026-10-20",
        "intervalle_revue_jours": 90,
        "sources": [
            {
                "titre": "Source de test",
                "url": "https://exemple.org/page",
                "licence_source": "Non vérifiée — lien documentaire ; aucune fiche n’est reprise",
                "droits_controles_le": "2026-10-20",
                "mode_utilisation": "reference-factuelle",
                "utilisation": "Règle consultée ; aucun texte n’est reproduit.",
            }
        ],
    }


def etats(fiche: dict, references: dict[str, list[str]] | None = None) -> dict[str, str]:
    if references is None:
        references = {"demo-fiche": ["methodes-communication"]}
    resultats = MODULE.controler(fiche, {fiche["id"]: fiche}, references, AUJOURDHUI)
    return {resultat["cle"]: resultat["etat"] for resultat in resultats}


class AuditMord(unittest.TestCase):
    def test_fiche_valide_passe_tous_les_controles_sauf_la_page(self):
        resultats = etats(fiche_valide())
        en_echec = [cle for cle, etat in resultats.items() if etat != "ok"]
        self.assertEqual(en_echec, ["page"], "seule la page générée manque dans ce test hors dépôt")

    def test_champ_manquant_signale(self):
        fiche = fiche_valide()
        fiche["analogie"] = ""
        self.assertEqual(etats(fiche)["champs"], "a-corriger")

    def test_liste_vide_signalee(self):
        fiche = fiche_valide()
        fiche["correction"] = ["", ""]
        self.assertEqual(etats(fiche)["champs_listes"], "a-corriger")

    def test_fiche_non_referencee_signalee(self):
        self.assertEqual(etats(fiche_valide(), {})["referencement"], "a-corriger")

    def test_statut_inconnu_signale(self):
        fiche = fiche_valide()
        fiche["statut_editorial"] = "Publiée"
        self.assertEqual(etats(fiche)["statut"], "a-corriger")

    def test_source_en_http_signalee(self):
        fiche = fiche_valide()
        fiche["sources"][0]["url"] = "http://exemple.org/page"
        self.assertEqual(etats(fiche)["sources"], "a-corriger")

    def test_sans_source_signalee(self):
        fiche = fiche_valide()
        fiche["sources"] = []
        self.assertEqual(etats(fiche)["sources"], "a-corriger")

    def test_droits_incomplets_signales(self):
        fiche = fiche_valide()
        del fiche["sources"][0]["licence_source"]
        self.assertEqual(etats(fiche)["droits"], "a-corriger")

    def test_reprise_non_ecartee_signalee(self):
        fiche = fiche_valide()
        fiche["sources"][0]["utilisation"] = "Règle et exemples repris."
        self.assertEqual(etats(fiche)["droits"], "a-corriger")

    def test_revue_future_signalee(self):
        fiche = fiche_valide()
        fiche["revue_le"] = "2027-01-01"
        self.assertEqual(etats(fiche)["dates"], "a-corriger")

    def test_intervalle_hors_bornes_signale(self):
        fiche = fiche_valide()
        fiche["intervalle_revue_jours"] = 10
        self.assertEqual(etats(fiche)["dates"], "a-corriger")

    def test_limite_d_analogie_trop_courte_signalee(self):
        fiche = fiche_valide()
        fiche["limite_analogie"] = "Ce n'est qu'une image."
        self.assertEqual(etats(fiche)["analogie"], "a-corriger")

    def test_correction_maigre_signalee(self):
        fiche = fiche_valide()
        fiche["correction"] = ["Une seule réponse."]
        self.assertEqual(etats(fiche)["exercice"], "a-corriger")

    def test_doublon_entre_fiches_signale(self):
        fiche = fiche_valide()
        autre = copy.deepcopy(fiche)
        autre["id"] = "autre-fiche"
        resultats = MODULE.controler(fiche, {fiche["id"]: fiche, "autre-fiche": autre}, {"demo-fiche": ["methodes-communication"]}, AUJOURDHUI)
        etats_cles = {resultat["cle"]: resultat["etat"] for resultat in resultats}
        self.assertEqual(etats_cles["doublons"], "a-corriger")

    def test_phrase_trop_longue_signalee(self):
        fiche = fiche_valide()
        fiche["transferer"] = "mot " * 60 + "."
        self.assertEqual(etats(fiche)["phrases"], "a-corriger")

    def test_typographie_signalee(self):
        fiche = fiche_valide()
        fiche["resume"] = "Un résumé avec une virgule mal espacée , comme ici."
        self.assertEqual(etats(fiche)["typographie"], "a-corriger")

    def test_extension_citee_n_est_pas_une_faute(self):
        fiche = fiche_valide()
        fiche["resume"] = "Le format comme .pdf s'affiche à la fin du nom."
        self.assertEqual(etats(fiche)["typographie"], "ok")

    def test_identifiant_non_slug_signale(self):
        fiche = fiche_valide()
        fiche["id"] = "Demo_Fiche!"
        self.assertEqual(etats(fiche)["identifiant"], "a-corriger")

    def test_titre_trop_long_signale(self):
        fiche = fiche_valide()
        fiche["titre"] = "Un titre absolument interminable " * 4
        self.assertEqual(etats(fiche)["longueurs"], "a-corriger")

    def test_source_dupliquee_signalee(self):
        fiche = fiche_valide()
        fiche["sources"].append(copy.deepcopy(fiche["sources"][0]))
        self.assertEqual(etats(fiche)["sources_dates"], "a-corriger")

    def test_date_de_droits_illisible_signalee(self):
        fiche = fiche_valide()
        fiche["sources"][0]["droits_controles_le"] = "hier"
        self.assertEqual(etats(fiche)["sources_dates"], "a-corriger")


class ConstatNEstPasUnEchec(unittest.TestCase):
    """Un portail seul n'est pas une faute : c'est un fait que la machine nomme."""

    def test_portail_assume_donne_un_constat(self):
        fiche = fiche_valide()
        fiche["sources"][0]["url"] = "https://exemple.org/"
        fiche["sources"][0]["utilisation"] = "Portail facultatif ; aucun texte n’est reproduit."
        self.assertEqual(etats(fiche)["precision"], MODULE.ETAT_A_VERIFIER)

    def test_portail_non_declare_est_une_erreur(self):
        fiche = fiche_valide()
        fiche["sources"][0]["url"] = "https://exemple.org/"
        # « Règle consultée » laisse croire à une page précise : c'est faux.
        self.assertEqual(etats(fiche)["precision"], "a-corriger")

    def test_racine_avec_parametre_reste_un_portail(self):
        fiche = fiche_valide()
        fiche["sources"][0]["url"] = "https://exemple.org/?q=1"
        fiche["sources"][0]["utilisation"] = "Point d’entrée consulté ; aucun contenu n’est copié."
        self.assertEqual(etats(fiche)["precision"], MODULE.ETAT_A_VERIFIER)

    def test_un_portail_plus_une_page_precise_passe(self):
        fiche = fiche_valide()
        second = copy.deepcopy(fiche["sources"][0])
        second["url"] = "https://exemple.org/"
        second["titre"] = "Portail de test"
        fiche["sources"].append(second)
        self.assertEqual(etats(fiche)["precision"], "ok")

    def test_le_constat_n_entre_pas_dans_les_echecs(self):
        fiche = fiche_valide()
        fiche["sources"][0]["url"] = "https://exemple.org/"
        fiche["sources"][0]["utilisation"] = "Portail facultatif ; aucun texte n’est reproduit."
        audits = MODULE.auditer([fiche], {"demo-fiche": ["methodes-communication"]}, AUJOURDHUI, seulement_prototypes=False)
        # Seule la page générée manque hors dépôt : le constat, lui, n'est pas un échec.
        self.assertEqual([echec["cle"] for echec in audits[0]["echecs"]], ["page"])
        self.assertEqual([constat["cle"] for constat in audits[0]["constats"]], ["precision"])
        chiffres = MODULE.resume(audits)
        self.assertEqual((chiffres["echecs"], chiffres["constats"], chiffres["fiches_a_verifier"]), (1, 1, 1))

    def test_le_document_nomme_les_constats_sans_les_appeler_defauts(self):
        fiche = fiche_valide()
        fiche["sources"][0]["url"] = "https://exemple.org/"
        fiche["sources"][0]["utilisation"] = "Portail facultatif ; aucun texte n’est reproduit."
        audits = MODULE.auditer([fiche], {"demo-fiche": ["methodes-communication"]}, AUJOURDHUI, seulement_prototypes=False)
        contenu = MODULE.construire(audits, {"methodes-communication": "Méthodes"}, AUJOURDHUI)
        self.assertIn("Constats nommés, à trancher par une personne", contenu)
        self.assertIn("Un constat n'est pas un défaut", contenu)
        self.assertIn("| Fiches avec au moins un échec | 1 |", contenu)  # seule la page manque ici
        self.assertIn("| Constats nommés (ni échecs, ni validations) | 1 |", contenu)


class DocumentGenere(unittest.TestCase):
    def test_audit_reel_du_depot_est_coherent(self):
        fiches, titres, references = MODULE.charger()
        audits = MODULE.auditer(fiches, references, date.today())
        self.assertTrue(audits, "aucun prototype audité")
        self.assertEqual(len({audit["fiche"]["id"] for audit in audits}), len(audits), "fiche auditée deux fois")
        contenu = MODULE.construire(audits, titres, date.today())
        self.assertIn("Ce qu'aucun script ne peut faire", contenu)
        self.assertIn("ni une relecture, ni une validation", contenu)

    def test_le_document_ne_pretend_jamais_une_validation(self):
        fiches, titres, references = MODULE.charger()
        audits = MODULE.auditer(fiches, references, date(AUJOURDHUI.year, AUJOURDHUI.month, AUJOURDHUI.day))
        contenu = MODULE.construire(audits, titres, AUJOURDHUI).casefold()
        for terme in ("validée", "approuvée", "relue par l'audit"):
            self.assertNotIn(terme, contenu)


if __name__ == "__main__":
    unittest.main()
