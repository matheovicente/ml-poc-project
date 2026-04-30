# Assignment 5 - Conclusion et application

Le projet fournit :

- un classement des chokepoints par criticité ;
- une classification supervisée du niveau de criticité ;
- une comparaison de modèles ;
- une application Streamlit ;
- une simulation de fermeture sur 7, 14 ou 30 jours.
- une simulation détaillée des fermetures des principaux chokepoints sur 14, 30 et 90 jours, avec visualisation des courbes simulées des autres détroits.

La conclusion doit comparer les chokepoints à fort trafic global, comme Malacca
ou Suez, aux chokepoints énergétiques comme Ormuz.

## Simulation de fermeture

La V1 simule la fermeture des 5 chokepoints les plus critiques pendant :

- 14 jours ;
- 30 jours ;
- 90 jours.

Pour chaque scénario, le chokepoint fermé tombe à zéro trafic. Une part du trafic
perdu est redistribuée vers les autres chokepoints du groupe selon leur capacité
relative. Les résultats sont sauvegardés dans :

- `results/closure_simulation_summary.csv`
- `results/closure_simulation_timeseries.csv`
- `plots/closure_simulations/`
