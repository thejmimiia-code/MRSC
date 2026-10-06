"""Adaptateur GED 26.1 CSV : présence mensuelle, dates ambiguës et provenance.

Pas de téléchargement implicite, pas d'antidatage, pas de somme de victimes imputée.
"""

import argparse
import csv
import hashlib
import io
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

from simulateur.fichiers import verifier_chemins_distincts
from simulateur.validation_temporelle import (
    CIBLE_UCDP,
    Observation,
    Registre,
    _objet_unique,
    date_iso,
    mois_iso,
    mois_suivant,
)

CHAMPS = {'id', 'country', 'country_id', 'type_of_violence', 'date_start', 'date_end',
          'date_prec', 'low', 'best', 'high'}


@dataclass(frozen=True)
class ContratImport:
    version_source: str
    nature: str
    source: str
    licence: str
    publication: str
    disponibilite: str
    ingestion: str
    preuve_disponibilite: str
    debut: str
    fin: str
    pays_ids: list[int]
    couverture_exhaustive: bool = False
    preuve_exhaustivite: str = ''

    def __post_init__(self) -> None:
        if self.version_source != '26.1':
            raise ValueError('Seul le schéma GED annuel 26.1 est pris en charge')
        if self.nature not in ('synthetique', 'observee'):
            raise ValueError('Nature explicite requise')
        if self.nature == 'observee' and self.licence != 'CC-BY-4.0':
            raise ValueError('Attribution CC-BY-4.0 requise pour les données UCDP observées')
        for nom in ('source', 'licence', 'preuve_disponibilite'):
            if not isinstance(getattr(self, nom), str) or not getattr(self, nom).strip():
                raise ValueError(f'{nom} doit être renseigné')
        if self.nature == 'observee' and not self.source.startswith('https://'):
            raise ValueError('Source HTTPS requise pour un import déclaré observé')
        debut, fin = mois_iso(self.debut), mois_iso(self.fin)
        if not date(1989, 1, 1) <= debut <= fin <= date(2025, 12, 1):
            raise ValueError('Période mensuelle incompatible avec GED 26.1')
        if not (mois_suivant(fin) <= date_iso(self.publication)
                <= date_iso(self.disponibilite) <= date_iso(self.ingestion)):
            raise ValueError('Clôture de période <= publication <= disponibilité <= ingestion requise')
        if (not isinstance(self.pays_ids, list) or not self.pays_ids
                or any(type(i) is not int or i <= 0 for i in self.pays_ids)
                or len(set(self.pays_ids)) != len(self.pays_ids)):
            raise ValueError('Identifiants pays positifs, explicites et uniques requis')
        if type(self.couverture_exhaustive) is not bool:
            raise ValueError('couverture_exhaustive doit être booléen')
        if self.couverture_exhaustive and (
                not isinstance(self.preuve_exhaustivite, str) or not self.preuve_exhaustivite.strip()):
            raise ValueError('Une déclaration d’exhaustivité nécessite une preuve référencée')


def date_ged(texte: str) -> date:
    # CSV date ou timestamp de minuit ; aucune troncature arbitraire d'un texte.
    match = re.fullmatch(r'(\d{4}-\d{2}-\d{2})(?:[ T]00:00:00(?:\.0{1,6})?)?', texte)
    if not match:
        raise ValueError(f'Date GED invalide : {texte!r}')
    return date_iso(match[1])


def entier_csv(texte: str, nom: str, minimum: int = 0) -> int:
    if not re.fullmatch(r'\d+', texte) or int(texte) < minimum:
        raise ValueError(f'{nom} doit être un entier >= {minimum}')
    return int(texte)


class LecteurEmpreinte(io.RawIOBase):
    """Calcule le SHA-256 des octets transmis au parseur, sans seconde lecture."""

    def __init__(self, source, empreinte):
        self.source = source
        self.empreinte = empreinte

    def readable(self):
        return True

    def readinto(self, tampon):
        n = self.source.readinto(tampon)
        if n:
            self.empreinte.update(memoryview(tampon)[:n])
        return n


def convertir(csv_path: Path, contrat: ContratImport) -> dict:
    """Valide toutes les lignes ; ne remplace jamais un fichier partiel par une absence réelle."""
    cellules = {}
    for pays in sorted(contrat.pays_ids):
        mois = mois_iso(contrat.debut)
        while mois <= mois_iso(contrat.fin):
            cellules[(pays, mois.strftime('%Y-%m'))] = {'certains': [], 'ambigus': []}
            mois = mois_suivant(mois)
    empreinte = hashlib.sha256()
    ids = {}
    comptes = {'lignes_lues': 0, 'evenements_uniques': 0, 'doublons_identiques': 0,
               'evenements_retenus': 0, 'hors_perimetre': 0}
    with csv_path.open('rb') as source, io.TextIOWrapper(
        io.BufferedReader(LecteurEmpreinte(source, empreinte)),
        encoding='utf-8-sig', newline='',
    ) as fichier:
        lecteur = csv.DictReader(fichier, strict=True)
        colonnes = lecteur.fieldnames
        if not colonnes or len(set(colonnes)) != len(colonnes) or not CHAMPS <= set(colonnes):
            raise ValueError('En-tête CSV incomplet ou colonnes dupliquées')
        for ligne in lecteur:
            numero = lecteur.line_num
            comptes['lignes_lues'] += 1
            try:
                if None in ligne or any(v is None for v in ligne.values()):
                    raise ValueError('Nombre de colonnes incohérent')
                identifiant = entier_csv(ligne['id'], 'id', 1)
                canonique = hashlib.sha256(json.dumps(ligne, sort_keys=True).encode()).hexdigest()
                if identifiant in ids:
                    if ids[identifiant] != canonique:
                        raise ValueError('Même id avec contenus contradictoires')
                    comptes['doublons_identiques'] += 1
                    continue
                ids[identifiant] = canonique
                pays = entier_csv(ligne['country_id'], 'country_id', 1)
                if not ligne['country'].strip():
                    raise ValueError('Nom de pays absent')
                type_violence = entier_csv(ligne['type_of_violence'], 'type_of_violence', 1)
                precision = entier_csv(ligne['date_prec'], 'date_prec', 1)
                if type_violence not in (1, 2, 3) or precision not in (1, 2, 3, 4, 5):
                    raise ValueError('Type de violence ou précision inconnu')
                debut, fin = date_ged(ligne['date_start']), date_ged(ligne['date_end'])
                if not date(1989, 1, 1) <= debut <= fin <= date(2025, 12, 31):
                    raise ValueError('Intervalle temporel invalide pour GED 26.1')
                if precision == 1 and debut != fin:
                    raise ValueError('Une date exacte ne peut couvrir plusieurs jours')
                low, best, high = (entier_csv(ligne[n], n) for n in ('low', 'best', 'high'))
                if not 0 <= low <= best <= high or high < 1:
                    raise ValueError('Bornes de décès incohérentes ou événement non létal')
                comptes['evenements_uniques'] += 1
                touches = []
                mois = debut.replace(day=1)
                while mois <= fin:
                    cle = (pays, mois.strftime('%Y-%m'))
                    if cle in cellules:
                        touches.append(cle)
                    mois = mois_suivant(mois)
                if not touches:
                    comptes['hors_perimetre'] += 1
                    continue
                comptes['evenements_retenus'] += 1
                # Comparer l'intervalle ORIGINAL, pas le nombre de mois restant après filtre.
                classe = 'certains' if (debut.year, debut.month) == (fin.year, fin.month) else 'ambigus'
                for cle in touches:
                    cellules[cle][classe].append(identifiant)
            except (ValueError, TypeError) as erreur:
                raise ValueError(f'Ligne CSV {numero} : {erreur}') from erreur
    observations, audit = [], []
    for (pays, mois), preuves in sorted(cellules.items()):
        if preuves['certains']:
            valeur, motif = 1, 'presence_dans_un_mois_non_ambigu'
        elif preuves['ambigus']:
            valeur, motif = None, 'intervalle_chevauchant_plusieurs_mois'
        elif contrat.couverture_exhaustive:
            valeur, motif = 0, 'absence_d_enregistrement_dans_snapshot_declare_exhaustif'
        else:
            valeur, motif = None, 'exhaustivite_non_attestee'
        o = Observation(
            identifiant=f'ucdp-letal:{pays}:{mois}', unite=f'UCDP_COUNTRY_{pays}', mois=mois,
            revision=1, cible=CIBLE_UCDP, valeur=valeur,
            couverture='complete' if valeur is not None else 'incomplete',
            nature=contrat.nature, source=contrat.source, version_source=contrat.version_source,
            licence=contrat.licence, preuve_disponibilite=contrat.preuve_disponibilite,
            publication=contrat.publication, disponibilite=contrat.disponibilite,
            ingestion=contrat.ingestion,
        )
        observations.append(o)
        audit.append({'identifiant': o.identifiant, 'valeur': valeur, 'motif': motif,
                      'ids_certains': sorted(preuves['certains']),
                      'ids_ambigus': sorted(preuves['ambigus'])})
    registre = Registre(tuple(observations))
    return {
        'protocole': 'import-ged-26.1-v1', 'nature': contrat.nature,
        'avertissement': 'Un snapshot actuel ne prouve pas la disponibilité historique des étiquettes.',
        'contrat': asdict(contrat), 'empreinte_csv_sha256': empreinte.hexdigest(),
        'empreinte_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'empreinte_registre_sha256': registre.empreinte(), 'comptes': comptes,
        'synthese': {'cellules': len(audit), 'positives': sum(a['valeur'] == 1 for a in audit),
                    'negatives': sum(a['valeur'] == 0 for a in audit),
                    'inconnues': sum(a['valeur'] is None for a in audit)},
        'audit_cellules': audit, 'observations': [asdict(o) for o in registre.observations],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, required=True)
    parser.add_argument('--contrat', type=Path, required=True)
    parser.add_argument('--sortie', type=Path, default=Path('rd-resultats-observations-ucdp.jsonl'))
    parser.add_argument('--rapport', type=Path, default=Path('rd-resultats-import-ucdp.json'))
    args = parser.parse_args()
    try:
        verifier_chemins_distincts(args.csv, args.contrat, args.sortie, args.rapport)
        donnees = json.loads(args.contrat.read_text(encoding='utf-8'), object_pairs_hook=_objet_unique)
        contrat = ContratImport(**donnees)
        resultat = convertir(args.csv, contrat)
    except (OSError, ValueError, TypeError, csv.Error) as erreur:
        parser.error(str(erreur))
    args.sortie.write_text(''.join(json.dumps(o, ensure_ascii=False, allow_nan=False) + '\n'
                                 for o in resultat['observations']), encoding='utf-8')
    args.rapport.write_text(json.dumps(resultat, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps({'nature': resultat['nature'], 'comptes': resultat['comptes'],
                      'synthese': resultat['synthese']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
