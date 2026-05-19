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

PORTWATCH_RAW_PATH = RAW_DATA_DIR / "portwatch_daily_chokepoints.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "pump_price_dataset.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.2

FEATURES = [
    "strait_of_hormuz_n_tanker",
    "strait_of_hormuz_n_tanker_ma4",
    "strait_of_hormuz_n_tanker_ma12",
    "strait_of_hormuz_n_tanker_ratio12",
    "strait_of_hormuz_n_tanker_lag1",
    "bab_el_mandeb_strait_n_tanker",
    "bab_el_mandeb_strait_n_tanker_ma4",
    "bab_el_mandeb_strait_n_tanker_ratio12",
    "suez_canal_n_tanker",
    "suez_canal_n_tanker_ma4",
    "suez_canal_n_tanker_ratio12",
    "malacca_strait_n_tanker",
    "malacca_strait_n_tanker_ma4",
    "malacca_strait_n_tanker_ratio12",
    "maritime_stress",
    "brent_price",
    "brent_return_1w",
    "brent_return_4w",
    "brent_vol_4w",
    "brent_return_1w_lag1",
    "brent_return_1w_lag2",
    "pump_price",
    "pump_return_1w",
    "pump_return_4w",
    "pump_return_1w_lag1",
    "pump_return_1w_lag2",
    "month",
    "week_of_year",
    "is_driving_season",
    "is_winter",
]

TARGET = "target_price_up_1w"

MODELS = {
    "log_reg": {
        "name": "Logistic Regression",
        "description": "Linear baseline with standardized features.",
        "path": MODELS_DIR / "log_reg.joblib",
    },
    "random_forest": {
        "name": "Random Forest",
        "description": "Tree ensemble capturing non-linear feature interactions.",
        "path": MODELS_DIR / "random_forest.joblib",
    },
    "gradient_boosting": {
        "name": "Gradient Boosting",
        "description": "Boosted trees optimized for short-term directional classification.",
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
