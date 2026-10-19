#!/usr/bin/env python3
"""Tests unitaires du comptage de la Boussole prospective."""

import datetime as dt
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("verifier-decision-prospective.py")
SPEC = importlib.util.spec_from_file_location("verifier_decision_prospective", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def trace_decision(valeurs: list[str]) -> str:
    champs = [
        "Option retenue", "Date", "Personne ou instance qui décide",
        "Conditions ajoutées", "Date de réexamen",
    ]
    lignes = "\n".join(f"| {champ} | {valeur} |" for champ, valeur in zip(champs, valeurs))
    return f"## 10. Trace de décision\n\n{lignes}\n"


class CompterQuestionsBoussoleTests(unittest.TestCase):
    def test_compte_uniquement_les_elements_de_la_liste(self):
        html = '''
        <section id="boussole-savoirs">
          <ol class="knowledge-compass"><li>Une</li><li>Deux</li></ol>
          <ul><li>Hors boussole</li></ul>
        </section>
        '''
        self.assertEqual(MODULE.compter_questions_boussole(html), 2)

    def test_refuse_une_section_absente(self):
        with self.assertRaisesRegex(ValueError, "section"):
            MODULE.compter_questions_boussole("<main></main>")

    def test_refuse_une_liste_absente(self):
        with self.assertRaisesRegex(ValueError, "knowledge-compass"):
            MODULE.compter_questions_boussole('<section id="boussole-savoirs"></section>')

    def test_lit_la_date_du_brief_et_du_tableau(self):
        texte = "**Date : 17 octobre 2026. Statut : brouillon.**\n| Fait | Valeur au 17 octobre 2026 |"
        self.assertEqual(MODULE.date_du_brief(texte), dt.date(2026, 10, 17))

    def test_refuse_deux_dates_differentes(self):
        texte = "**Date : 17 octobre 2026. Statut : brouillon.**\n| Fait | Valeur au 18 octobre 2026 |"
        with self.assertRaisesRegex(ValueError, "différente"):
            MODULE.date_du_brief(texte)

    def test_refuse_un_mois_inconnu(self):
        texte = "**Date : 17 octembre 2026.**\n| Valeur au 17 octembre 2026 |"
        with self.assertRaisesRegex(ValueError, "date française"):
            MODULE.date_du_brief(texte)

    def test_reconnait_une_decision_en_attente(self):
        self.assertEqual(MODULE.etat_trace_decision(trace_decision(["", "", "", "", ""])), "en attente")

    def test_refuse_une_decision_partielle(self):
        with self.assertRaisesRegex(ValueError, "partielle"):
            MODULE.etat_trace_decision(trace_decision(["B", "2026-10-17", "", "", ""]))

    def test_reconnait_une_decision_complete(self):
        texte = trace_decision(["B", "2026-10-17", "Conseil", "Aucune", "2027-01-31"])
        self.assertEqual(MODULE.etat_trace_decision(texte), "option B consignée")

    def test_refuse_une_option_invalide(self):
        texte = trace_decision(["D", "2026-10-17", "Conseil", "Aucune", "2027-01-31"])
        with self.assertRaisesRegex(ValueError, "A, B ou C"):
            MODULE.etat_trace_decision(texte)

    def test_refuse_decision_anterieure_au_brief(self):
        texte = trace_decision(["B", "2026-10-16", "Conseil", "Aucune", "2027-01-31"])
        with self.assertRaisesRegex(ValueError, "antérieure"):
            MODULE.etat_trace_decision(texte, dt.date(2026, 10, 17))

    def test_refuse_reexamen_le_jour_de_la_decision(self):
        texte = trace_decision(["B", "2026-10-17", "Conseil", "Aucune", "2026-10-17"])
        with self.assertRaisesRegex(ValueError, "après"):
            MODULE.etat_trace_decision(texte, dt.date(2026, 10, 17))

    def test_accepte_une_chronologie_coherente(self):
        texte = trace_decision(["B", "2026-10-18", "Conseil", "Aucune", "2027-01-31"])
        self.assertEqual(
            MODULE.etat_trace_decision(texte, dt.date(2026, 10, 17)),
            "option B consignée",
        )

    def test_aligne_attente_et_initiative_a_cadrer(self):
        initiatives = [{"id": "prospective-apprentissages-2030", "etat": "a-cadrer"}]
        self.assertEqual(MODULE.verifier_etat_initiative("en attente", initiatives), "a-cadrer")

    def test_refuse_attente_avec_initiative_avancee(self):
        initiatives = [{"id": "prospective-apprentissages-2030", "etat": "en-cours"}]
        with self.assertRaisesRegex(ValueError, "décision en attente"):
            MODULE.verifier_etat_initiative("en attente", initiatives)

    def test_refuse_decision_avec_initiative_a_cadrer(self):
        initiatives = [{"id": "prospective-apprentissages-2030", "etat": "a-cadrer"}]
        with self.assertRaisesRegex(ValueError, "encore"):
            MODULE.verifier_etat_initiative("option B consignée", initiatives)

    def test_refuse_initiative_absente(self):
        with self.assertRaisesRegex(ValueError, "absente"):
            MODULE.verifier_etat_initiative("en attente", [])

    def test_arrondit_les_poids_affiches(self):
        tableau = "| `apprendre.html` | 158.8 | 308.6 | 619.5 |"
        self.assertEqual(MODULE.poids_page(tableau, "apprendre.html"), (159, 309))

    def test_calcule_la_revue_depuis_les_metadonnees(self):
        meta = {"derniere_revue": dt.date(2026, 10, 13), "cadence_revue_jours": 30}
        self.assertEqual(MODULE.date_prochaine_revue(meta), dt.date(2026, 11, 12))

    def test_refuse_des_metadonnees_de_revue_incompletes(self):
        with self.assertRaisesRegex(ValueError, "métadonnées"):
            MODULE.date_prochaine_revue({"derniere_revue": dt.date(2026, 10, 13)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
