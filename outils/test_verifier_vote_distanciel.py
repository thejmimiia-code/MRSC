#!/usr/bin/env python3
"""Tests du registre documentaire de menaces — aucune cryptographie testée."""

import copy
import hashlib
import importlib.util
import tomllib
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("verifier-vote-distanciel.py")
SPEC = importlib.util.spec_from_file_location("verifier_vote_distanciel", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RACINE = Path(__file__).parents[1]
REGISTRE_PATH = RACINE / "docs" / "rd" / "vote-distanciel-menaces.toml"
REGLES_PATH = RACINE / "docs" / "rd" / "vote-distanciel-regles.toml"
CAS_PATH = RACINE / "docs" / "rd" / "vote-distanciel-cas-essai.toml"
STATUTS_PATH = RACINE / "assets" / "documents" / "statuts-2020.pdf"
DECISION_PATH = RACINE / "docs" / "rd" / "vote-distanciel-decision.md"
COMPARAISON_PATH = RACINE / "docs" / "rd" / "vote-distanciel-comparaison.toml"
SOURCES_PATH = RACINE / "docs" / "rd" / "vote-distanciel-sources.toml"
PROFILS_PATH = RACINE / "docs" / "rd" / "vote-distanciel-profils.toml"
REVUES_PATH = RACINE / "docs" / "rd" / "vote-distanciel-revues.toml"
DONNEES_PATH = RACINE / "docs" / "rd" / "vote-distanciel-donnees.toml"
CORRELATION_PATH = RACINE / "docs" / "rd" / "vote-distanciel-correlation.toml"
CONTINUITE_PATH = RACINE / "docs" / "rd" / "vote-distanciel-continuite.toml"
ACCESSIBILITE_PATH = RACINE / "docs" / "rd" / "vote-distanciel-accessibilite.toml"
ASSISTANCE_PATH = RACINE / "docs" / "rd" / "vote-distanciel-assistance.toml"
CLES_PATH = RACINE / "docs" / "rd" / "vote-distanciel-cles.toml"
CHAINE_LOGICIELLE_PATH = RACINE / "docs" / "rd" / "vote-distanciel-chaine-logicielle.toml"
RESULTATS_PATH = RACINE / "docs" / "rd" / "vote-distanciel-resultats.toml"
DOSSIER_PATH = RACINE / "docs" / "rd" / "vote-distanciel-dossier-deliberation.md"


def table_decision(valeurs: list[str]) -> str:
    champs = [
        "Version des statuts confirmée", "Règlement intérieur vérifié",
        "Profil retenu", "Option retenue", "Instance ou rôle décideur",
        "Date de décision", "Date de réexamen", "Conditions ou objections",
    ]
    return "\n".join(f"| {champ} | {valeur} |" for champ, valeur in zip(champs, valeurs))


class RegistreMenacesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRE_PATH.open("rb") as fichier:
            cls.registre = tomllib.load(fichier)
        with REGLES_PATH.open("rb") as fichier:
            cls.regles = tomllib.load(fichier)
        with CAS_PATH.open("rb") as fichier:
            cls.cas = tomllib.load(fichier)
        cls.decision = DECISION_PATH.read_text(encoding="utf-8")
        with COMPARAISON_PATH.open("rb") as fichier:
            cls.comparaison = tomllib.load(fichier)
        with SOURCES_PATH.open("rb") as fichier:
            cls.sources = tomllib.load(fichier)
        with PROFILS_PATH.open("rb") as fichier:
            cls.profils = tomllib.load(fichier)
        with REVUES_PATH.open("rb") as fichier:
            cls.revues = tomllib.load(fichier)
        with DONNEES_PATH.open("rb") as fichier:
            cls.donnees = tomllib.load(fichier)
        with CORRELATION_PATH.open("rb") as fichier:
            cls.correlation = tomllib.load(fichier)
        with CONTINUITE_PATH.open("rb") as fichier:
            cls.continuite = tomllib.load(fichier)
        with ACCESSIBILITE_PATH.open("rb") as fichier:
            cls.accessibilite = tomllib.load(fichier)
        with ASSISTANCE_PATH.open("rb") as fichier:
            cls.assistance = tomllib.load(fichier)
        with CLES_PATH.open("rb") as fichier:
            cls.cles = tomllib.load(fichier)
        with CHAINE_LOGICIELLE_PATH.open("rb") as fichier:
            cls.chaine_logicielle = tomllib.load(fichier)
        with RESULTATS_PATH.open("rb") as fichier:
            cls.resultats = tomllib.load(fichier)
        cls.dossier = DOSSIER_PATH.read_text(encoding="utf-8")
        cls.empreinte_statuts = hashlib.sha256(STATUTS_PATH.read_bytes()).hexdigest()

    def test_registre_courant_est_coherent(self):
        self.assertEqual(MODULE.verifier_registre(self.registre), [])

    def test_refuse_une_menace_supprimee(self):
        registre = copy.deepcopy(self.registre)
        registre["menace"].pop()
        self.assertTrue(any("10 menaces" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_un_champ_de_preuve_vide(self):
        registre = copy.deepcopy(self.registre)
        registre["menace"][0]["preuve_attendue"] = ""
        self.assertTrue(any("preuve_attendue" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_une_menace_dite_maitrisee(self):
        registre = copy.deepcopy(self.registre)
        registre["menace"][0]["statut"] = "maitrisee"
        self.assertTrue(any("a-expertiser" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_un_invariant_duplique(self):
        registre = copy.deepcopy(self.registre)
        registre["invariant"].append(copy.deepcopy(registre["invariant"][0]))
        self.assertTrue(any("sans doublon" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_un_registre_detache_de_l_initiative(self):
        registre = copy.deepcopy(self.registre)
        registre["meta"]["initiative"] = "autre"
        self.assertTrue(any("initiative" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_regles_statutaires_courantes_sont_coherentes(self):
        self.assertEqual(MODULE.verifier_regles(self.regles, self.empreinte_statuts), [])

    def test_refuse_une_empreinte_statutaire_obsolete(self):
        self.assertTrue(any(
            "empreinte" in erreur
            for erreur in MODULE.verifier_regles(self.regles, "0" * 64)
        ))

    def test_refuse_une_regle_statutaire_supprimee(self):
        registre = copy.deepcopy(self.regles)
        registre["regle"].pop()
        self.assertTrue(any(
            "18 règles" in erreur
            for erreur in MODULE.verifier_regles(registre, self.empreinte_statuts)
        ))

    def test_refuse_une_regle_statutaire_dite_validee(self):
        registre = copy.deepcopy(self.regles)
        registre["regle"][0]["statut"] = "validee"
        self.assertTrue(any(
            "à faire relire" in erreur
            for erreur in MODULE.verifier_regles(registre, self.empreinte_statuts)
        ))

    def test_profils_statutaires_courants_sont_non_executables(self):
        self.assertEqual(MODULE.verifier_profils(self.profils), [])

    def test_refuse_un_profil_manquant(self):
        registre = copy.deepcopy(self.profils)
        registre["profil"].pop()
        self.assertTrue(any("8 profils" in erreur for erreur in MODULE.verifier_profils(registre)))

    def test_refuse_un_parametre_executable_avant_relecture(self):
        registre = copy.deepcopy(self.profils)
        registre["profil"][0]["quorum"] = 25
        self.assertTrue(any("non exécutable" in erreur for erreur in MODULE.verifier_profils(registre)))

    def test_maintient_la_dissolution_bloquee(self):
        registre = copy.deepcopy(self.profils)
        dissolution = next(item for item in registre["profil"] if item["id"] == "dissolution")
        dissolution["statut"] = "a-faire-relire"
        self.assertTrue(any("bloque-interpretation" in erreur for erreur in MODULE.verifier_profils(registre)))

    def test_cas_synthetiques_couvrent_les_menaces(self):
        self.assertEqual(MODULE.verifier_cas_essai(self.cas), [])

    def test_refuse_un_cas_execute_sans_expertise(self):
        registre = copy.deepcopy(self.cas)
        registre["cas"][0]["statut"] = "reussi"
        self.assertTrue(any("à concevoir" in erreur for erreur in MODULE.verifier_cas_essai(registre)))

    def test_refuse_une_menace_non_couverte(self):
        registre = copy.deepcopy(self.cas)
        for item in registre["cas"]:
            item["menaces"] = [m for m in item["menaces"] if m != "terminal-compromis"]
        self.assertTrue(any("10 menaces" in erreur for erreur in MODULE.verifier_cas_essai(registre)))

    def test_refuse_une_menace_inconnue(self):
        registre = copy.deepcopy(self.cas)
        registre["cas"][0]["menaces"].append("menace-inventee")
        self.assertTrue(any("inconnues" in erreur for erreur in MODULE.verifier_cas_essai(registre)))

    def test_comparaison_courante_est_sans_classement(self):
        self.assertEqual(MODULE.verifier_comparaison(self.comparaison), [])

    def test_refuse_une_option_absente(self):
        registre = copy.deepcopy(self.comparaison)
        registre["option"].pop()
        self.assertTrue(any("ElectionGuard" in erreur for erreur in MODULE.verifier_comparaison(registre)))

    def test_refuse_un_score(self):
        registre = copy.deepcopy(self.comparaison)
        registre["option"][0]["score"] = 100
        self.assertTrue(any("sans score" in erreur for erreur in MODULE.verifier_comparaison(registre)))

    def test_refuse_un_critere_non_bloquant(self):
        registre = copy.deepcopy(self.comparaison)
        registre["critere"][0]["bloquant"] = False
        self.assertTrue(any("maintenu bloquant" in erreur for erreur in MODULE.verifier_comparaison(registre)))

    def test_cycle_des_resultats_courant_ne_proclame_rien(self):
        self.assertEqual(MODULE.verifier_resultats(self.resultats), [])

    def test_refuse_un_resultat_autorise_automatiquement(self):
        registre = copy.deepcopy(self.resultats)
        registre["meta"]["resultat_autorise"] = True
        self.assertTrue(any("sans résultat autorisé" in erreur for erreur in MODULE.verifier_resultats(registre)))

    def test_refuse_la_suppression_de_la_contestation(self):
        registre = copy.deepcopy(self.resultats)
        registre["etape"] = [item for item in registre["etape"] if item["id"] != "fenetre-de-contestation"]
        self.assertTrue(any("6 étapes" in erreur for erreur in MODULE.verifier_resultats(registre)))

    def test_refuse_une_proclamation_sans_toutes_les_etapes(self):
        registre = copy.deepcopy(self.resultats)
        registre["porte"][0]["etapes"].pop()
        self.assertTrue(any("porte avant proclamation" in erreur for erreur in MODULE.verifier_resultats(registre)))

    def test_chaine_logicielle_courante_reste_non_executee(self):
        self.assertEqual(MODULE.verifier_chaine_logicielle(self.chaine_logicielle), [])

    def test_refuse_une_selection_logicielle_prematuree(self):
        registre = copy.deepcopy(self.chaine_logicielle)
        registre["meta"]["selection_effectuee"] = True
        self.assertTrue(any("non sélectionnée" in erreur for erreur in MODULE.verifier_chaine_logicielle(registre)))

    def test_refuse_la_suppression_du_controle_des_mises_a_jour(self):
        registre = copy.deepcopy(self.chaine_logicielle)
        registre["controle"] = [item for item in registre["controle"] if item["id"] != "mise-a-jour-gelee"]
        self.assertTrue(any("7 contrôles" in erreur for erreur in MODULE.verifier_chaine_logicielle(registre)))

    def test_refuse_une_porte_logicielle_partielle(self):
        registre = copy.deepcopy(self.chaine_logicielle)
        registre["porte"][0]["exigences"].pop()
        self.assertTrue(any("porte avant banc" in erreur for erreur in MODULE.verifier_chaine_logicielle(registre)))

    def test_cycle_des_cles_courant_reste_synthetique(self):
        self.assertEqual(MODULE.verifier_cles(self.cles), [])

    def test_refuse_la_cryptographie_maison(self):
        registre = copy.deepcopy(self.cles)
        registre["meta"]["cryptographie_maison"] = True
        self.assertTrue(any("sans cryptographie maison" in erreur for erreur in MODULE.verifier_cles(registre)))

    def test_refuse_la_suppression_de_la_destruction_des_cles(self):
        registre = copy.deepcopy(self.cles)
        registre["phase"] = [item for item in registre["phase"] if item["id"] != "destruction-et-contestation"]
        self.assertTrue(any("6 phases" in erreur for erreur in MODULE.verifier_cles(registre)))

    def test_refuse_la_sauvegarde_de_plusieurs_parts(self):
        registre = copy.deepcopy(self.cles)
        registre["incompatibilite"] = registre["incompatibilite"][:-2] + registre["incompatibilite"][-1:]
        self.assertTrue(any("centralisation" in erreur for erreur in MODULE.verifier_cles(registre)))

    def test_assistance_courante_reste_separee_de_la_procuration(self):
        self.assertEqual(MODULE.verifier_assistance(self.assistance), [])

    def test_refuse_la_confusion_assistance_procuration(self):
        registre = copy.deepcopy(self.assistance)
        registre["separation"] = registre["separation"][1:]
        self.assertTrue(any("assistance explicitement" in erreur for erreur in MODULE.verifier_assistance(registre)))

    def test_refuse_une_situation_sans_condition_arret(self):
        registre = copy.deepcopy(self.assistance)
        registre["situation"][0]["condition_arret"] = ""
        self.assertTrue(any("limite, preuve et arrêt" in erreur for erreur in MODULE.verifier_assistance(registre)))

    def test_refuse_une_assistance_dite_operationnelle(self):
        registre = copy.deepcopy(self.assistance)
        registre["meta"]["execution_autorisee"] = True
        self.assertTrue(any("non exécutable" in erreur for erreur in MODULE.verifier_assistance(registre)))

    def test_accessibilite_courante_ne_declare_aucune_conformite(self):
        self.assertEqual(MODULE.verifier_accessibilite(self.accessibilite), [])

    def test_refuse_une_conformite_accessibilite_prematuree(self):
        registre = copy.deepcopy(self.accessibilite)
        registre["meta"]["conformite_declaree"] = True
        self.assertTrue(any("sans conformité" in erreur for erreur in MODULE.verifier_accessibilite(registre)))

    def test_refuse_la_suppression_d_une_barriere(self):
        registre = copy.deepcopy(self.accessibilite)
        registre["barriere"].pop()
        self.assertTrue(any("8 barrières" in erreur for erreur in MODULE.verifier_accessibilite(registre)))

    def test_refuse_un_repli_sans_risque_documente(self):
        registre = copy.deepcopy(self.accessibilite)
        registre["barriere"][0]["risque_repli"] = ""
        self.assertTrue(any("repli et risque" in erreur for erreur in MODULE.verifier_accessibilite(registre)))

    def test_continuite_courante_reste_non_executable(self):
        self.assertEqual(MODULE.verifier_continuite(self.continuite), [])

    def test_refuse_un_incident_sans_decision_associative(self):
        registre = copy.deepcopy(self.continuite)
        registre["incident"][0]["autorite_humaine_requise"] = ["operations-securite"]
        self.assertTrue(any("autorité humaine" in erreur for erreur in MODULE.verifier_continuite(registre)))

    def test_refuse_un_abaissement_premature_des_garde_fous(self):
        registre = copy.deepcopy(self.continuite)
        registre["incident"][0]["statut"] = "operationnel"
        self.assertTrue(any("maintenu à faire relire" in erreur for erreur in MODULE.verifier_continuite(registre)))

    def test_refuse_un_incident_de_continuite_supprime(self):
        registre = copy.deepcopy(self.continuite)
        registre["incident"].pop()
        self.assertTrue(any("7 incidents" in erreur for erreur in MODULE.verifier_continuite(registre)))

    def test_epreuve_correlation_courante_reste_non_executable(self):
        self.assertEqual(MODULE.verifier_correlation(self.correlation), [])

    def test_refuse_un_seuil_de_correlation_invente(self):
        registre = copy.deepcopy(self.correlation)
        registre["meta"]["seuil_accepte"] = "0.42"
        self.assertTrue(any("aucun seuil" in erreur for erreur in MODULE.verifier_correlation(registre)))

    def test_refuse_l_autorisation_prematuree_de_l_epreuve(self):
        registre = copy.deepcopy(self.correlation)
        registre["meta"]["execution_autorisee"] = True
        self.assertTrue(any("non exécutable" in erreur for erreur in MODULE.verifier_correlation(registre)))

    def test_refuse_une_vue_qui_emploie_une_categorie_inconnue(self):
        registre = copy.deepcopy(self.correlation)
        registre["vue"][0]["categories"].append("adresse-ip-reelle")
        self.assertTrue(any("catégorie inconnue" in erreur for erreur in MODULE.verifier_correlation(registre)))

    def test_modele_de_donnees_courant_separe_identite_et_bulletin(self):
        self.assertEqual(MODULE.verifier_donnees(self.donnees), [])

    def test_refuse_une_categorie_de_donnees_absente(self):
        registre = copy.deepcopy(self.donnees)
        registre["categorie"].pop()
        self.assertTrue(any("8 catégories" in erreur for erreur in MODULE.verifier_donnees(registre)))

    def test_refuse_la_suppression_de_l_interdiction_identite_bulletin(self):
        registre = copy.deepcopy(self.donnees)
        registre["liaison_interdite"] = [
            liaison for liaison in registre["liaison_interdite"]
            if set((liaison["gauche"], liaison["droite"])) != {"identite-eligibilite", "bulletin-chiffre"}
        ]
        self.assertTrue(any("identité–bulletin" in erreur for erreur in MODULE.verifier_donnees(registre)))

    def test_refuse_une_categorie_dite_expertisee(self):
        registre = copy.deepcopy(self.donnees)
        registre["categorie"][0]["statut"] = "expertisee"
        self.assertTrue(any("maintenue à expertiser" in erreur for erreur in MODULE.verifier_donnees(registre)))

    def test_plan_de_revues_courant_est_a_attribuer(self):
        self.assertEqual(MODULE.verifier_revues(self.revues), [])

    def test_refuse_un_role_manquant(self):
        registre = copy.deepcopy(self.revues)
        registre["role"].pop()
        self.assertTrue(any("6 rôles" in erreur for erreur in MODULE.verifier_revues(registre)))

    def test_refuse_une_attribution_non_prouvee(self):
        registre = copy.deepcopy(self.revues)
        registre["role"][0]["statut"] = "attribue"
        self.assertTrue(any("non attribué" in erreur for erreur in MODULE.verifier_revues(registre)))

    def test_refuse_une_decision_sans_tous_les_roles(self):
        registre = copy.deepcopy(self.revues)
        decision = next(item for item in registre["revue"] if item["id"] == "decision-de-phase")
        decision["roles_requis"].pop()
        self.assertTrue(any("6 rôles" in erreur for erreur in MODULE.verifier_revues(registre)))

    def test_sources_courantes_sont_epinglees_sans_selection(self):
        self.assertEqual(MODULE.verifier_sources(self.sources), [])

    def test_refuse_un_commit_abrege(self):
        registre = copy.deepcopy(self.sources)
        registre["projet"][0]["commit"] = "8888045"
        self.assertTrue(any("commit Git complet" in erreur for erreur in MODULE.verifier_sources(registre)))

    def test_refuse_une_source_dite_evaluee(self):
        registre = copy.deepcopy(self.sources)
        registre["projet"][0]["statut"] = "selectionnee"
        self.assertTrue(any("à évaluer" in erreur for erreur in MODULE.verifier_sources(registre)))

    def test_refuse_une_selection_dans_le_releve(self):
        registre = copy.deepcopy(self.sources)
        registre["projet"][0]["selection"] = True
        self.assertTrue(any("sans score ni sélection" in erreur for erreur in MODULE.verifier_sources(registre)))

    def test_refuse_une_source_sans_preuves_a_chercher(self):
        registre = copy.deepcopy(self.sources)
        registre["projet"][0]["preuves_a_chercher"] = []
        self.assertTrue(any("preuves_a_chercher" in erreur for erreur in MODULE.verifier_sources(registre)))

    def test_decision_courante_est_en_attente(self):
        self.assertEqual(MODULE.verifier_decision(self.decision), ("en attente", []))

    def test_refuse_une_decision_partielle(self):
        etat, erreurs = MODULE.verifier_decision(table_decision(["oui", "", "", "", "", "", "", ""]))
        self.assertEqual(etat, "invalide")
        self.assertTrue(any("partielle" in erreur for erreur in erreurs))

    def test_refuse_option_d(self):
        valeurs = ["oui", "oui", "ago-premiere", "D", "Conseil", "2026-10-18", "2027-01-31", "Aucune"]
        etat, erreurs = MODULE.verifier_decision(table_decision(valeurs))
        self.assertEqual(etat, "invalide")
        self.assertTrue(any("A, B ou C" in erreur for erreur in erreurs))

    def test_refuse_dissolution_non_interpretee(self):
        valeurs = ["oui", "oui", "dissolution", "B", "Conseil", "2026-10-18", "2027-01-31", "Aucune"]
        etat, erreurs = MODULE.verifier_decision(table_decision(valeurs))
        self.assertEqual(etat, "invalide")
        self.assertTrue(any("dissolution" in erreur for erreur in erreurs))

    def test_accepte_une_decision_complete_bornee(self):
        valeurs = ["oui", "non applicable", "ago-premiere", "B", "Conseil", "2026-10-18", "2027-01-31", "Sous conditions"]
        self.assertEqual(MODULE.verifier_decision(table_decision(valeurs)), ("décision consignée", []))


class DossierDeliberationTests(unittest.TestCase):
    """Le dossier de délibération ne doit ni dériver des registres ni décider à leur place."""

    @classmethod
    def setUpClass(cls):
        for nom, chemin in (
            ("registre", REGISTRE_PATH),
            ("regles", REGLES_PATH),
            ("cas", CAS_PATH),
            ("profils", PROFILS_PATH),
            ("revues", REVUES_PATH),
            ("comparaison", COMPARAISON_PATH),
        ):
            with chemin.open("rb") as fichier:
                setattr(cls, nom, tomllib.load(fichier))
        cls.dossier = DOSSIER_PATH.read_text(encoding="utf-8")

    def verifier(self, markdown, profils=None, regles=None, revues=None, comparaison=None):
        return MODULE.verifier_dossier(
            markdown,
            profils if profils is not None else self.profils,
            regles if regles is not None else self.regles,
            self.registre,
            self.cas,
            revues if revues is not None else self.revues,
            comparaison if comparaison is not None else self.comparaison,
        )

    def test_dossier_courant_est_coherent(self):
        self.assertEqual(self.verifier(self.dossier), [])

    def test_refuse_un_profil_absent(self):
        erreurs = self.verifier(self.dossier.replace("`ago-seconde`", "`ago-bis`"))
        self.assertTrue(any("profil de dossier absent" in erreur for erreur in erreurs))

    def test_refuse_un_statut_de_profil_divergent(self):
        profils = copy.deepcopy(self.profils)
        profils["profil"][0]["statut"] = "valide"
        erreurs = self.verifier(self.dossier, profils=profils)
        self.assertTrue(any("statut du profil bureau-executif" in erreur for erreur in erreurs))

    def test_refuse_un_compte_des_menaces_perime(self):
        erreurs = self.verifier(self.dossier.replace("10 menaces", "9 menaces"))
        self.assertTrue(any("nombre de menaces" in erreur for erreur in erreurs))

    def test_refuse_une_ambiguite_effacee(self):
        dossier = self.dossier.replace("| 8 | La copie locale des statuts", "| 8 bis | La copie locale des statuts")
        erreurs = self.verifier(dossier)
        self.assertTrue(any("huit ambiguïtés" in erreur for erreur in erreurs))

    def test_refuse_une_condition_effacee(self):
        dossier = self.dossier.replace("| 15 | Six rôles ont examiné", "| 15 bis | Six rôles ont examiné")
        erreurs = self.verifier(dossier)
        self.assertTrue(any("quinze conditions" in erreur for erreur in erreurs))

    def test_refuse_une_voie_d_non_bloquee(self):
        dossier = self.dossier.replace("### Voie D — Construire un système\n\n- **Statut : bloquée.**", "### Voie D — Construire un système\n\n- **Statut : envisageable.**")
        erreurs = self.verifier(dossier)
        self.assertTrue(any("voie D" in erreur for erreur in erreurs))

    def test_refuse_une_formule_de_promesse(self):
        erreurs = self.verifier(self.dossier + "\nUn système super sécurisé.\n")
        self.assertTrue(any("formule de promesse interdite" in erreur for erreur in erreurs))

    def test_refuse_un_profil_presélectionne(self):
        dossier = self.dossier.replace("| Profil retenu | | Un identifiant", "| Profil retenu | `ago-premiere` | Un identifiant")
        erreurs = self.verifier(dossier)
        self.assertTrue(any("présélectionner un profil" in erreur for erreur in erreurs))

    def test_refuse_une_section_manquante(self):
        erreurs = self.verifier(self.dossier.replace("## 12. Sources internes", "## 12. Annexe"))
        self.assertTrue(any("section de dossier absente" in erreur for erreur in erreurs))

    def test_refuse_une_decision_inscrite_par_le_dossier(self):
        dossier = self.dossier.replace("**Seul le tableau du §6", "Le tableau du §6")
        erreurs = self.verifier(dossier)
        self.assertTrue(any("tableau de décision" in erreur for erreur in erreurs))


if __name__ == "__main__":
    unittest.main(verbosity=2)
