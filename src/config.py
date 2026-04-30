from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
RESULTS_DIR = PROJECT_ROOT / "results"
PLOTS_DIR = PROJECT_ROOT / "plots"
LOGS_DIR = PROJECT_ROOT / "logs"

RAW_DATA_PATH = RAW_DATA_DIR / "portwatch_daily_chokepoints.csv"
MONTHLY_FEATURES_PATH = PROCESSED_DATA_DIR / "chokepoint_monthly_features.csv"
SUMMARY_FEATURES_PATH = PROCESSED_DATA_DIR / "chokepoint_summary_features.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.25

NUMERIC_FEATURES = [
    "mean_n_total",
    "std_n_total",
    "cv_n_total",
    "mean_n_tanker",
    "tanker_share",
    "mean_capacity",
    "mean_capacity_tanker",
    "tanker_capacity_share",
    "mean_n_container",
    "mean_n_dry_bulk",
    "mean_n_general_cargo",
    "mean_n_cargo",
    "disruption_frequency_total",
    "disruption_frequency_tanker",
    "max_drop_n_total",
    "max_drop_n_tanker",
    "observed_days",
]

MODELS = {
    "log_reg": {
        "name": "Régression logistique",
        "description": "Baseline linéaire avec standardisation des variables.",
        "path": MODELS_DIR / "log_reg.joblib",
    },
    "random_forest": {
        "name": "Random Forest",
        "description": "Ensemble d'arbres pour capturer les relations non linéaires.",
        "path": MODELS_DIR / "random_forest.joblib",
    },
    "gradient_boosting": {
        "name": "Gradient Boosting",
        "description": "Modèle boosting pour classifier le niveau de criticité.",
        "path": MODELS_DIR / "gradient_boosting.joblib",
    },
}


def ensure_directories() -> None:
    for directory in [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        MODELS_DIR,
        RESULTS_DIR,
        PLOTS_DIR,
        LOGS_DIR,
    ]:
        directory.mkdir(parents=True, exist_ok=True)

