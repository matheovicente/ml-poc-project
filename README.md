# Pump Price Prediction

This project predicts whether the US regular gasoline price will increase the following week.

The business idea is to test whether maritime tanker traffic around strategic chokepoints, especially the Strait of Hormuz, adds useful signal to oil-market variables such as Brent.

## Business Case

Gasoline prices are influenced by crude oil prices, refining constraints, demand cycles and geopolitical disruptions. Maritime chokepoints matter because a disruption in tanker flows can signal stress in energy supply chains.

The project asks:

> Can tanker traffic around strategic chokepoints help predict short-term movements in pump prices?

## Dataset

The final dataset combines:

- IMF PortWatch daily chokepoint data, aggregated weekly;
- FRED weekly US regular gasoline price (`GASREGW`);
- FRED Brent crude oil price (`DCOILBRENTEU`);
- optional FRED macro variables when available.

The main local files are:

- `data/raw/portwatch_daily_chokepoints.csv`
- `data/processed/pump_price_dataset.csv`

## Repository Structure

```text
deliverables/        Markdown deliverables
data/                raw and processed datasets
logs/                execution logs
models/              trained ML models
notebooks/           exploratory notebooks
plots/               generated visualizations
results/             model metrics and outputs
scripts/             executable project scripts
src/                 source code used by the professor template
tests/               optional tests
```

The required template contracts are preserved:

- `src/data.py` exposes `load_dataset_split()`;
- `src/metrics.py` exposes `compute_metrics(y_true, y_pred)`;
- `src/app.py` exposes `build_app()`;
- `scripts/main.py` evaluates registered models and launches Streamlit.

## Models

The model families are kept stable:

- Logistic Regression;
- Random Forest;
- Gradient Boosting.

The improvement comes from better feature engineering, chronological train/test splitting and compact hyperparameter tuning.

## Run

```bash
pip install -r requirements.txt
python scripts/prepare_data.py
python scripts/train_models.py
python scripts/main.py
```

Streamlit then runs at:

```text
http://localhost:8501
```

## Outputs

- `results/model_metrics.csv`
- `results/training_model_metrics.csv`
- `results/feature_importance.csv`
- `plots/model_comparison.png`
- `plots/feature_importance.png`
- `plots/pump_brent_timeseries.png`
- `plots/tanker_traffic_timeseries.png`
