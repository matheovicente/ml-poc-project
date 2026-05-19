# Maritime Chokepoint Risk

This project studies the criticality of global maritime chokepoints using IMF
PortWatch daily traffic data. It combines feature engineering, supervised
classification, time-series backtesting and closure simulations.

## Business Question

Which maritime chokepoints are the most critical in case of a temporary closure,
and how could a closure affect traffic on other strategic routes?

The project focuses on operational maritime risk rather than financial markets:

- ranking chokepoints by criticality;
- classifying their risk level;
- comparing model performance;
- testing normal-traffic forecasts;
- simulating 14, 30 and 90 day closure scenarios.

## Repository Structure

```text
deliverables/        Markdown deliverables
data/                raw and processed datasets
logs/                execution logs
models/              trained ML models
notebooks/           exploratory notebooks
plots/               generated visualizations
results/             metrics and simulation outputs
scripts/             executable project scripts
src/                 project source code
tests/               optional tests
```

The repository follows the professor template:

- `src/data.py` exposes `load_dataset_split()`;
- `src/metrics.py` exposes `compute_metrics(y_true, y_pred)`;
- `src/app.py` exposes `build_app()`;
- `scripts/main.py` evaluates the registered models and launches Streamlit.

## Dataset

Source: IMF PortWatch / ArcGIS API  
Local file: `data/raw/portwatch_daily_chokepoints.csv`

Current dataset:

- 74,844 daily observations;
- 28 maritime chokepoints;
- total vessel traffic, tanker traffic, cargo traffic and capacities;
- Strait of Hormuz included as `Strait of Hormuz`.

## Models

The model families are intentionally kept stable:

- Logistic Regression;
- Random Forest;
- Gradient Boosting.

The training script improves their efficiency through cross-validated
hyperparameter search, without adding new model families.

## Run the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Prepare datasets and plots:

```bash
python scripts/prepare_data.py
```

Train the models:

```bash
python scripts/train_models.py
```

Generate closure scenarios:

```bash
python scripts/simulate_closures.py --top-n 5 --durations 14 30 90
```

Backtest normal-traffic forecasts:

```bash
python scripts/backtest_timeseries.py --top-n 5 --horizons 14 30 90 --models analog sarimax
```

Evaluate models and launch Streamlit:

```bash
python scripts/main.py
```

Application URL:

```text
http://localhost:8501
```

## Main Outputs

- `results/model_metrics.csv`
- `results/training_model_metrics.csv`
- `results/training_cv_results.csv`
- `results/feature_importance.csv`
- `results/closure_simulation_summary.csv`
- `results/time_series_backtest_metrics_aggregated.csv`
- `plots/model_comparison.png`
- `plots/feature_importance.png`
- `plots/closure_simulations/*_focus.png`
- `plots/backtests/*.png`

## Interpretation

The classification target is based on a transparent business criticality score.
The model metrics therefore measure how well each model reproduces this scoring
logic. The closure scenarios are counterfactual simulations and should be read
as decision-support stress tests, not as exact vessel-by-vessel forecasts.
