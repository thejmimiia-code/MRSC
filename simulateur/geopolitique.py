"""Laboratoire géopolitique déterministe, non calibré et sans probabilités de guerre.

Les événements sont imposés, les conséquences sont calculées. Acteurs fictifs.
Voir docs/RD_GEOPOLITIQUE.md pour les équations et limites.
"""

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

from simulateur.model import DecisionPolitique
from simulateur.moteur import MoteurSimulationSystemique


# Compatibilité avec les imports publics de la strate annuelle de la PR #10.
# Le chargement différé évite une dépendance circulaire avec le moteur macro.
def __getattr__(nom: str):
    from simulateur import geopolitique_annuelle

    publics = {
        'BRENT_REFERENCE_USD', 'PART_PETROLE_HORMUZ_PCT', 'PRIME_PETROLE_HORMUZ_TOTALE',
        'PART_SEMICONDUCTEURS_TAIWAN', 'PERTE_PIB_BLOCUS_TOTAL_PCT',
        'PERTE_PIB_NUCLEAIRE_TACTIQUE', 'EFFORT_DEFENSE_INSTANT_T_PCT',
        'CIBLE_OTAN_DEFENSE_PCT', 'CIBLE_OTAN_SECURITE_ELARGIE_PCT',
        'PLAFOND_CLAUSE_SAUVEGARDE_PCT', 'PointDePassageStrategique',
        'chokepoints_par_defaut', 'EchelonGeopolitique', 'EffetsGeopolitiques',
        'propager_geopolitique',
    }
    if nom in publics:
        return getattr(geopolitique_annuelle, nom)
    raise AttributeError(f'{__name__} ne définit pas {nom}')


def borne(nom: str, valeur: float, minimum: float, maximum: float) -> None:
    if (not isinstance(valeur, (int, float)) or isinstance(valeur, bool)
            or not math.isfinite(valeur) or not minimum <= valeur <= maximum):
        raise ValueError(f'{nom} doit être fini et dans [{minimum}, {maximum}]')


def entier(nom: str, valeur: int, minimum: int, maximum: int) -> None:
    if type(valeur) is not int or not minimum <= valeur <= maximum:
        raise ValueError(f'{nom} doit être un entier dans [{minimum}, {maximum}]')


@dataclass(frozen=True)
class Acteur:
    nom: str
    nucleaire: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.nom, str) or not self.nom.strip() or type(self.nucleaire) is not bool:
            raise ValueError('Acteur : nom non vide et statut nucléaire booléen requis')


@dataclass(frozen=True)
class Alliance:
    protecteur: str
    protege: str
    # Aucune automaticité : une autorisation explicite est aussi nécessaire.
    delai_mois: int = 1


@dataclass(frozen=True)
class Secteur:
    nom: str
    demande: float = 100.0  # unités physiques normalisées par mois, pas euros
    part_importee: float = 0.6
    exposition_route: float = 0.8
    stock_mois: float = 1.0  # stock initial en mois de demande
    substitution: float = 0.25  # fraction des flux bloqués récupérable
    delai_substitution: int = 3  # mois de blocus consécutifs avant récupération
    poids_pib: float = 1.0
    capacite_stock_mois: float | None = None  # None conserve la capacité historique
    reconstitution_mensuelle: float = 0.0  # offre supplémentaire / demande, hors blocus

    def __post_init__(self) -> None:
        if not isinstance(self.nom, str) or not self.nom.strip():
            raise ValueError('Un secteur doit avoir un nom')
        borne('demande', self.demande, 0.001, 1e9)
        for nom in ('part_importee', 'exposition_route', 'substitution', 'poids_pib'):
            borne(nom, getattr(self, nom), 0, 1)
        borne('stock_mois', self.stock_mois, 0, 24)
        if self.capacite_stock_mois is not None:
            borne('capacite_stock_mois', self.capacite_stock_mois, self.stock_mois, 24)
        borne('reconstitution_mensuelle', self.reconstitution_mensuelle, 0, 1)
        entier('delai_substitution', self.delai_substitution, 0, 120)


@dataclass(frozen=True)
class Evenement:
    mois: int
    combats: tuple[tuple[str, str], ...] = ()  # (agresseur, cible), imposés ce mois
    autorisations: tuple[str, ...] = ()  # autorisation politique d'intervenir ce mois
    blocus: float = 0.0  # fraction fermée de la route exposée
    rupture_dialogue: bool = False
    mediation: bool = False
    emploi_nucleaire: bool = False  # branche imposée, JAMAIS déclenchée par le score

    def __post_init__(self) -> None:
        entier('mois', self.mois, 1, 120)
        borne('blocus', self.blocus, 0, 1)
        for nom in ('rupture_dialogue', 'mediation', 'emploi_nucleaire'):
            if type(getattr(self, nom)) is not bool:
                raise ValueError(f'{nom} doit être booléen')


@dataclass(frozen=True)
class Parametres:
    memoire_tension: float = 0.75
    poids_confrontation: float = 25.0
    poids_rupture: float = 15.0
    poids_mediation: float = 20.0
    seuil_signal: float = 25.0
    seuil_alerte: float = 60.0
    # Décote annuelle maximale d’activité, cumulée sans rattrapage automatique.
    elasticite_penurie: float = 0.04
    recuperation_annuelle: float = 0.0  # fraction du déficit d’activité résorbée en année sans pénurie

    def __post_init__(self) -> None:
        borne('memoire_tension', self.memoire_tension, 0, 1)
        for nom in ('poids_confrontation', 'poids_rupture', 'poids_mediation'):
            borne(nom, getattr(self, nom), 0, 100)
        borne('seuil_signal', self.seuil_signal, 0.001, 100)
        borne('seuil_alerte', self.seuil_alerte, self.seuil_signal, 100)
        if self.seuil_signal == self.seuil_alerte:
            raise ValueError('Les seuils doivent être distincts')
        borne('elasticite_penurie', self.elasticite_penurie, 0, 0.2)
        borne('recuperation_annuelle', self.recuperation_annuelle, 0, 1)


def simuler(acteurs: tuple[Acteur, ...], alliances: tuple[Alliance, ...],
            secteurs: tuple[Secteur, ...], evenements: tuple[Evenement, ...],
            horizon: int = 36, parametres: Parametres | None = None,
            *, calendrier_complet: bool = False) -> dict:
    """Simulation mensuelle pure ; pas de mutation ni de propagation d'alliance récursive."""
    entier('horizon', horizon, 1, 120)
    if type(calendrier_complet) is not bool:
        raise ValueError('calendrier_complet doit être booléen')
    p = parametres or Parametres()
    noms = {a.nom for a in acteurs}
    if not noms or len(noms) != len(acteurs) or any(not n for n in noms):
        raise ValueError('Acteurs non vides et uniques requis')
    if not secteurs or len({s.nom for s in secteurs}) != len(secteurs):
        raise ValueError('Secteurs non vides et uniques requis')
    if not math.isclose(sum(s.poids_pib for s in secteurs), 1, abs_tol=1e-9):
        raise ValueError('La somme des poids sectoriels doit être 1')
    for a in alliances:
        if a.protecteur not in noms or a.protege not in noms or a.protecteur == a.protege:
            raise ValueError('Alliance invalide')
        entier('delai_mois', a.delai_mois, 0, 120)
    calendrier = {e.mois: e for e in evenements}
    if len(calendrier) != len(evenements) or any(e.mois > horizon for e in evenements):
        raise ValueError('Un événement au maximum par mois, dans l’horizon')
    if calendrier_complet and set(calendrier) != set(range(1, horizon + 1)):
        raise ValueError('Calendrier incomplet : un mois absent ne prouve pas une accalmie')
    for e in evenements:
        if not set(e.autorisations) <= noms:
            raise ValueError('Autorisation pour un acteur inconnu')
        for agresseur, cible in e.combats:
            if agresseur not in noms or cible not in noms or agresseur == cible:
                raise ValueError('Combat invalide')
    nucleaires = {a.nom for a in acteurs if a.nucleaire}
    stocks = {s.nom: s.stock_mois * s.demande for s in secteurs}
    attaques_consecutives = dict.fromkeys(noms, 0)
    duree_blocus = 0
    tension = 0.0
    historique = []
    arret = None
    for mois in range(1, horizon + 1):
        e = calendrier.get(mois, Evenement(mois))
        if e.emploi_nucleaire:
            # Pas de fausse estimation des victimes ou de l'économie post-emploi.
            arret = {'mois': mois, 'motif': 'emploi_nucleaire_impose_hors_validite'}
            break
        cibles = {cible for _, cible in e.combats}
        for nom in noms:
            attaques_consecutives[nom] = attaques_consecutives[nom] + 1 if nom in cibles else 0
        interventions = set()
        for a in alliances:
            if (a.protege in cibles and a.protecteur in e.autorisations
                    and attaques_consecutives[a.protege] > a.delai_mois):
                for agresseur, cible in e.combats:
                    if cible == a.protege and agresseur != a.protecteur:
                        interventions.add((a.protecteur, agresseur))
        combats = set(e.combats) | interventions
        confrontation = any(a in nucleaires and b in nucleaires for a, b in combats)
        tension = max(0.0, min(100.0,
            p.memoire_tension * tension + p.poids_confrontation * confrontation
            + p.poids_rupture * e.rupture_dialogue - p.poids_mediation * e.mediation))
        posture = ('alerte' if tension >= p.seuil_alerte else
                   'signal' if tension >= p.seuil_signal else 'veille')
        duree_blocus = duree_blocus + 1 if e.blocus > 0 else 0
        flux = {}
        for s in secteurs:
            initial = stocks[s.nom]
            capacite = s.demande * (s.stock_mois if s.capacite_stock_mois is None
                                    else s.capacite_stock_mois)
            bloque = s.demande * s.part_importee * s.exposition_route * e.blocus
            substitution = bloque * s.substitution if duree_blocus > s.delai_substitution else 0.0
            # Offre supplémentaire explicite, livrée uniquement hors blocus global.
            # Jamais un crédit de stock sans entrée de matière.
            reconstitution = (min(capacite - initial, s.demande * s.reconstitution_mensuelle)
                              if e.blocus == 0 else 0.0)
            approvisionnement = s.demande - bloque + substitution + reconstitution
            disponible = initial + approvisionnement
            servi = min(s.demande, disponible)
            final = min(capacite, max(0.0, disponible - servi))
            excedent = max(0.0, disponible - servi - final)
            stocks[s.nom] = final
            flux[s.nom] = {
                'stock_initial': initial, 'approvisionnement': approvisionnement,
                'flux_bloque': bloque, 'substitution': substitution,
                'reconstitution': reconstitution, 'capacite_stock': capacite,
                'demande': s.demande, 'servi': servi, 'penurie': s.demande - servi,
                'stock_final': final, 'excedent': excedent,
            }
        penurie = sum(s.poids_pib * flux[s.nom]['penurie'] / s.demande for s in secteurs)
        historique.append({
            'mois': mois, 'evenement_impose': asdict(e),
            'interventions_calculees': [list(c) for c in sorted(interventions)],
            'confrontation_nucleaire_directe': confrontation,
            'indice_tension_conventionnel': tension,
            'posture_heuristique': posture, 'flux': flux, 'penurie_ponderee': penurie,
        })
    return {
        'version': 'geo-rd-v2',
        'statut': 'exploratoire_non_calibre_non_predictif',
        'hypotheses': {'acteurs': [asdict(a) for a in acteurs],
                       'alliances': [asdict(a) for a in alliances],
                       'secteurs': [asdict(s) for s in secteurs],
                       'parametres': asdict(p), 'horizon': horizon,
                       'calendrier_complet': calendrier_complet,
                       'evenements': [asdict(e) for e in sorted(evenements, key=lambda e: e.mois)]},
        'mois_supposes_calmes': [m for m in range(1, len(historique) + 1) if m not in calendrier],
        'arret': arret, 'mois': historique,
    }


def coupler_macro(rapport: dict) -> dict:
    """Deux moteurs neufs, décisions identiques ; seules les pénuries modifient le niveau d’activité.

    Ne projette que les années entièrement simulées avant une éventuelle rupture.
    """
    horizon = rapport['hypotheses']['horizon']
    entier('horizon', horizon, 1, 120)
    arret = rapport['arret']
    if arret is None:
        attendu = horizon
    else:
        entier('mois_arret', arret['mois'], 1, horizon)
        if arret.get('motif') != 'emploi_nucleaire_impose_hors_validite':
            raise ValueError('Motif d’arrêt géopolitique inconnu')
        attendu = arret['mois'] - 1
    if len(rapport['mois']) != attendu:
        raise ValueError('Trajectoire incompatible avec l’horizon ou l’arrêt déclaré')
    expose, temoin = MoteurSimulationSystemique(), MoteurSimulationSystemique()
    facteur = 1.0
    elasticite = rapport['hypotheses']['parametres']['elasticite_penurie']
    recuperation = rapport['hypotheses']['parametres'].get('recuperation_annuelle', 0.0)
    borne('elasticite_penurie', elasticite, 0, 0.2)
    borne('recuperation_annuelle', recuperation, 0, 1)
    for attendu, mois in enumerate(rapport['mois'], start=1):
        if type(mois['mois']) is not int or mois['mois'] != attendu:
            raise ValueError('Trajectoire macro : mois consécutifs depuis 1 requis')
        borne('penurie_ponderee', mois['penurie_ponderee'], 0, 1)
    annees = []
    for debut in range(0, len(rapport['mois']) - 11, 12):
        penurie = mean(m['penurie_ponderee'] for m in rapport['mois'][debut:debut + 12])
        gain_recuperation = recuperation * (1 - facteur) if penurie <= 1e-12 else 0.0
        facteur = min(1.0, facteur + gain_recuperation) * (1 - elasticite * penurie)
        decision = DecisionPolitique(annee=debut // 12 + 1, description='Témoin politique constant R&D')
        a = expose.appliquer_etape(decision, facteur_activite=facteur)
        b = temoin.appliquer_etape(decision)
        annees.append({'annee_relative': decision.annee, 'penurie_moyenne': penurie,
                       'decote_activite_annuelle_pct': 100 * elasticite * penurie,
                       'facteur_activite_cumule': facteur,
                       'recuperation_activite_points': 100 * gain_recuperation,
                       'expose': asdict(a), 'temoin': asdict(b),
                       'ecart_pib_mde': round(a.pib_nominal_mde - b.pib_nominal_mde, 2)})
    return {'methode': 'activite_cumulee_sans_double_choc_prix', 'annees': annees,
            'mois_non_projetes': len(rapport['mois']) % 12,
            'arret_geopolitique': rapport['arret']}


def cas_experimental(duree: int = 18, stock: float = 1.0, substitution: float = 0.25,
                     mediation: bool = False, autorisation: bool = True,
                     emploi_mois: int | None = None,
                     parametres: Parametres | None = None,
                     rupture_dialogue: bool | None = None) -> dict:
    """Cas fictif transparent ; aucun acteur réel ni calendrier de guerre prédit."""
    entier('duree', duree, 0, 36)
    for nom, valeur in (('mediation', mediation), ('autorisation', autorisation)):
        if type(valeur) is not bool:
            raise ValueError(f'{nom} doit être booléen')
    if rupture_dialogue is not None and type(rupture_dialogue) is not bool:
        raise ValueError('rupture_dialogue doit être booléen ou None')
    rupture = not mediation if rupture_dialogue is None else rupture_dialogue
    if emploi_mois is not None:
        entier('emploi_mois', emploi_mois, 1, 36)
    acteurs = (Acteur('A', True), Acteur('B'), Acteur('C', True))
    secteurs = (
        Secteur('energie', stock_mois=stock, substitution=substitution, poids_pib=0.6),
        Secteur('composants', part_importee=0.8, exposition_route=0.9,
                stock_mois=stock, substitution=substitution, poids_pib=0.4),
    )
    evenements = tuple(Evenement(
        mois=m, combats=(('A', 'B'),) if m <= duree else (),
        autorisations=('C',) if autorisation and m <= duree else (),
        blocus=0.8 if m <= duree else 0,
        rupture_dialogue=m <= duree and rupture,
        mediation=mediation,
        emploi_nucleaire=m == emploi_mois,
    ) for m in range(1, 37))
    rapport = simuler(acteurs, (Alliance('C', 'B'),), secteurs, evenements, 36, parametres)
    rapport['macro'] = coupler_macro(rapport)
    return rapport


def resumer(rapport: dict) -> dict:
    mois = rapport['mois']
    return {
        'mois_en_penurie': sum(m['penurie_ponderee'] > 1e-10 for m in mois),
        'penurie_cumulee_mois_demande': sum(m['penurie_ponderee'] for m in mois),
        'mois_intervention': next((m['mois'] for m in mois if m['interventions_calculees']), None),
        'premier_mois_alerte_heuristique': next((m['mois'] for m in mois if m['posture_heuristique'] == 'alerte'), None),
        'tension_max': max((m['indice_tension_conventionnel'] for m in mois), default=0),
        'dernier_ecart_pib_mde': rapport['macro']['annees'][-1]['ecart_pib_mde'] if rapport['macro']['annees'] else None,
        'arret': rapport['arret'],
    }


def campagne() -> dict:
    cas = {
        'temoin': cas_experimental(duree=0),
        'crise': cas_experimental(),
        'mediation': cas_experimental(mediation=True),
        'sans_autorisation': cas_experimental(autorisation=False),
        'emploi_impose_mois_8': cas_experimental(emploi_mois=8),
    }
    sensibilite = []
    for duree in (6, 18, 30):
        for stock in (0.0, 1.0, 3.0):
            for substitution in (0.0, 0.25, 0.75):
                for elasticite in (0.02, 0.04, 0.08):
                    p = Parametres(elasticite_penurie=elasticite)
                    r = cas_experimental(duree, stock, substitution, parametres=p)
                    sensibilite.append({'duree': duree, 'stock': stock, 'substitution': substitution,
                                        'elasticite': elasticite, **resumer(r)})
    sensibilite_escalade = []
    for memoire in (0.5, 0.75, 0.9):
        for poids in (10.0, 25.0, 40.0):
            for seuil in (40.0, 60.0, 80.0):
                p = Parametres(memoire_tension=memoire, poids_confrontation=poids,
                               seuil_alerte=seuil)
                r = cas_experimental(parametres=p)
                sensibilite_escalade.append({'memoire': memoire, 'poids_confrontation': poids,
                                             'seuil_alerte': seuil, **resumer(r)})
    return {'version': 'geo-campagne-v1',
            'avertissement': '108 combinaisons arbitraires, pas des futurs équiprobables. Aucun pronostic de guerre.',
            'synthese': {nom: resumer(r) for nom, r in cas.items()},
            'cas': cas, 'sensibilite': sensibilite, 'sensibilite_escalade': sensibilite_escalade}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie', type=Path, default=Path('rd-resultats-geopolitique.json'))
    args = parser.parse_args()
    rapport = campagne()
    args.sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(rapport['synthese'], ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
