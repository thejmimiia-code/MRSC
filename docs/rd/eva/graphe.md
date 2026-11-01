# Graphe de la mémoire d'ÉVA

Dérivé de `plan.toml`, `portefeuille.toml` et `avancees.toml` par
`python3 outils/memoire-eva.py --regenerer`. Ne rien éditer ici.

```mermaid
flowchart LR
  n_branche_autres_langues_et_contextes["branche:autres-langues-et-contextes"]
  n_branche_cartographier_les_lacunes["branche:cartographier-les-lacunes"]
  n_branche_co_conception_et_essais["branche:co-conception-et-essais"]
  n_branche_coherence_textes_publics["branche:coherence-textes-publics"]
  n_branche_confronter_une_affirmation_a_sa_source["branche:confronter-une-affirmation-a-sa-source"]
  n_branche_coordination_de_tous_les_agents["branche:coordination-de-tous-les-agents"]
  n_branche_direction_artistique_motion["branche:direction-artistique-motion"]
  n_branche_documentation_rd_eva["branche:documentation-rd-eva"]
  n_branche_ecouter_la_page["branche:ecouter-la-page"]
  n_branche_indexation_et_lecteurs_de_contenu["branche:indexation-et-lecteurs-de-contenu"]
  n_branche_mondes_3d_pluridisciplinaires["branche:mondes-3d-pluridisciplinaires"]
  n_branche_optimisation_du_site["branche:optimisation-du-site"]
  n_branche_poids_et_sobriete_numerique["branche:poids-et-sobriete-numerique"]
  n_branche_prospective_apprentissages_2030["branche:prospective-apprentissages-2030"]
  n_branche_raccordement_domaine_www["branche:raccordement-domaine-www"]
  n_branche_relire_les_44_prototypes["branche:relire-les-44-prototypes"]
  n_branche_sources_fermees_et_registre_des_refus["branche:sources-fermees-et-registre-des-refus"]
  n_branche_veille_savoirs_evolutifs["branche:veille-savoirs-evolutifs"]
  n_branche_vote_distanciel_verifiable["branche:vote-distanciel-verifiable"]
  n_phase_apprentissages_et_relecture["phase:apprentissages-et-relecture"]
  n_phase_conscience_et_corps["phase:conscience-et-corps"]
  n_phase_continuite_du_support["phase:continuite-du-support"]
  n_phase_couverture_des_branches["phase:couverture-des-branches"]
  n_phase_economie_de_contexte["phase:economie-de-contexte"]
  n_phase_graphe_de_memoire["phase:graphe-de-memoire"]
  n_phase_memoire_trois_horizons["phase:memoire-trois-horizons"]
  n_phase_parite_humaine_des_delais["phase:parite-humaine-des-delais"]
  n_phase_persona_de_conception["phase:persona-de-conception"]
  n_phase_rappel_mesure["phase:rappel-mesure"]
  n_phase_verite_et_refus["phase:verite-et-refus"]
  n_phase_voix_et_ecoute["phase:voix-et-ecoute"]
  n_branche_autres_langues_et_contextes -->|servie par| n_phase_apprentissages_et_relecture
  n_branche_cartographier_les_lacunes -->|servie par| n_phase_graphe_de_memoire
  n_branche_co_conception_et_essais -->|servie par| n_phase_apprentissages_et_relecture
  n_branche_coherence_textes_publics -->|servie par| n_phase_couverture_des_branches
  n_branche_coherence_textes_publics -->|servie par| n_phase_persona_de_conception
  n_branche_confronter_une_affirmation_a_sa_source -->|servie par| n_phase_verite_et_refus
  n_branche_coordination_de_tous_les_agents -->|servie par| n_phase_economie_de_contexte
  n_branche_coordination_de_tous_les_agents -->|servie par| n_phase_memoire_trois_horizons
  n_branche_direction_artistique_motion -->|servie par| n_phase_conscience_et_corps
  n_branche_direction_artistique_motion -->|servie par| n_phase_voix_et_ecoute
  n_branche_documentation_rd_eva -->|servie par| n_phase_couverture_des_branches
  n_branche_documentation_rd_eva -->|servie par| n_phase_memoire_trois_horizons
  n_branche_documentation_rd_eva -->|servie par| n_phase_persona_de_conception
  n_branche_ecouter_la_page -->|servie par| n_phase_rappel_mesure
  n_branche_ecouter_la_page -->|servie par| n_phase_voix_et_ecoute
  n_branche_indexation_et_lecteurs_de_contenu -->|servie par| n_phase_graphe_de_memoire
  n_branche_indexation_et_lecteurs_de_contenu -->|servie par| n_phase_rappel_mesure
  n_branche_mondes_3d_pluridisciplinaires -->|servie par| n_phase_conscience_et_corps
  n_branche_optimisation_du_site -->|servie par| n_phase_continuite_du_support
  n_branche_optimisation_du_site -->|servie par| n_phase_economie_de_contexte
  n_branche_poids_et_sobriete_numerique -->|servie par| n_phase_continuite_du_support
  n_branche_poids_et_sobriete_numerique -->|servie par| n_phase_economie_de_contexte
  n_branche_prospective_apprentissages_2030 -->|servie par| n_phase_parite_humaine_des_delais
  n_branche_raccordement_domaine_www -->|servie par| n_phase_continuite_du_support
  n_branche_relire_les_44_prototypes -->|servie par| n_phase_apprentissages_et_relecture
  n_branche_sources_fermees_et_registre_des_refus -->|servie par| n_phase_verite_et_refus
  n_branche_veille_savoirs_evolutifs -->|servie par| n_phase_graphe_de_memoire
  n_branche_veille_savoirs_evolutifs -->|servie par| n_phase_memoire_trois_horizons
  n_branche_vote_distanciel_verifiable -->|servie par| n_phase_verite_et_refus
  n_phase_economie_de_contexte -->|prépare| n_phase_rappel_mesure
  n_phase_memoire_trois_horizons -->|prépare| n_phase_apprentissages_et_relecture
  n_phase_memoire_trois_horizons -->|prépare| n_phase_continuite_du_support
  n_phase_memoire_trois_horizons -->|prépare| n_phase_couverture_des_branches
  n_phase_memoire_trois_horizons -->|prépare| n_phase_economie_de_contexte
  n_phase_memoire_trois_horizons -->|prépare| n_phase_graphe_de_memoire
  n_phase_memoire_trois_horizons -->|prépare| n_phase_rappel_mesure
  n_phase_memoire_trois_horizons -->|prépare| n_phase_verite_et_refus
  n_phase_rappel_mesure -->|prépare| n_phase_parite_humaine_des_delais
  n_phase_verite_et_refus -->|prépare| n_phase_conscience_et_corps
  n_phase_verite_et_refus -->|prépare| n_phase_continuite_du_support
  n_phase_verite_et_refus -->|prépare| n_phase_persona_de_conception
  n_phase_verite_et_refus -->|prépare| n_phase_voix_et_ecoute
```

Le détail fichier par fichier est dans `graphe.dot`.
