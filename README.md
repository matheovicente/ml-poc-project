# Détroits maritimes - criticité des chokepoints

Ce projet construit un modèle de classification pour estimer la criticité des
grands chokepoints maritimes mondiaux à partir des données journalières
PortWatch.

## Problématique

Quels chokepoints maritimes sont les plus critiques en cas de fermeture, et
peut-on prédire automatiquement leur niveau de criticité à partir de données de
trafic maritime ?

## Dataset

Source : IMF PortWatch / ArcGIS API

```text
https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query
```

Dataset brut local :

```text
data/raw/portwatch_daily_chokepoints.csv
```

Contenu actuel :

- 74 844 lignes
- 28 chokepoints
- données journalières
- trafic par type de navire
- capacité par type de navire
- Ormuz est présent sous `Strait of Hormuz`, `portid = chokepoint6`

## Objectif ML

Le projet transforme les données journalières en observations mensuelles par
chokepoint. Pour chaque ligne, on calcule des variables de trafic, de capacité,
d'exposition tanker et de perturbation.

La cible `criticality_class` est construite à partir d'un score métier :

```text
0 = criticité faible
1 = criticité moyenne
2 = criticité élevée
3 = criticité extrême
```

## Structure

```text
deliverables/
data/
logs/
models/
notebooks/
plots/
results/
scripts/
src/
tests/
```

Les signatures imposées par le template du professeur sont respectées :

- `src/data.py` : `load_dataset_split()`
- `src/metrics.py` : `compute_metrics(y_true, y_pred)`
- `src/app.py` : `build_app()`

## Exécution

Préparer les features :

```bash
python scripts/prepare_data.py
```

Entraîner les modèles :

```bash
python scripts/train_models.py
```

Simuler les fermetures des 5 chokepoints les plus critiques sur 14, 30 et 90 jours :

```bash
python scripts/simulate_closures.py --top-n 5 --durations 14 30 90
```

Backtester les modèles de trafic normal, dont SARIMAX :

```bash
python scripts/backtest_timeseries.py --top-n 5 --horizons 14 30 90 --models analog sarimax
```

Évaluer les modèles et lancer Streamlit :

```bash
python scripts/main.py
```

Application :

```text
http://localhost:8501
```

## Modèles

- Régression logistique
- Random Forest
- Gradient Boosting
- Baseline temporelle par analogue récent
- SARIMAX hebdomadaire pour prévoir le trafic journalier normal

## Sorties

- `data/processed/chokepoint_monthly_features.csv`
- `data/processed/chokepoint_summary_features.csv`
- `models/*.joblib`
- `results/model_metrics.csv`
- `results/closure_simulation_summary.csv`
- `results/closure_simulation_timeseries.csv`
- `results/time_series_backtest_metrics_aggregated.csv`
- `plots/*.png`
- `plots/closure_simulations/*.png`
- `plots/closure_simulations/*_focus.png` pour les graphiques adaptés aux slides
- `plots/backtests/*.png`

## Simulation de fermeture

La simulation répond à la question suivante :

> Que se passe-t-il si l'un des principaux chokepoints ferme pendant 2 semaines,
> 1 mois ou 3 mois ?

Méthode V1 :

- on construit une baseline de trafic attendu à partir de l'historique récent ;
- le chokepoint fermé passe à zéro trafic pendant la durée simulée ;
- une partie du trafic perdu est redistribuée vers des routes alternatives
  plausibles, quand elles existent ;
- le taux de redistribution dépend du chokepoint fermé. Par exemple, Ormuz a un
  taux faible car les alternatives maritimes sont limitées.

Cette simulation ne prétend pas prédire parfaitement les décisions réelles des
navires. Elle sert à comparer les ordres de grandeur et à visualiser les effets
potentiels d'une fermeture.

Deux types de graphiques sont générés :

- version complète : toutes les routes du scénario ;
- version `focus` : le détroit fermé et les routes qui changent le plus, plus
  lisible pour une présentation.

## Fiabilité des séries temporelles

La fermeture est un scénario contrefactuel, donc elle ne peut pas être validée
directement sans fermeture réelle comparable. En revanche, la baseline de trafic
normal peut être testée.

Le script `scripts/backtest_timeseries.py` prédit des fenêtres passées et compare
les prévisions aux observations réelles avec deux approches :

- `analog` : baseline simple qui rejoue une période récente comparable ;
- `sarimax` : modèle statistique de série temporelle avec saisonnalité hebdomadaire.

Les erreurs sont mesurées avec :

- MAE ;
- RMSE ;
- MAPE ;
- sMAPE.

## Limites

PortWatch repose sur les signaux AIS. Le score de criticité est construit à
partir de pondérations métiers simples : il doit donc être interprété comme un
indice transparent, pas comme une vérité absolue.
