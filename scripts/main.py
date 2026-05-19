from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import joblib
import pandas as pd

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*_args, **_kwargs):
        return False

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from config import MODELS, PLOTS_DIR, RESULTS_DIR, ensure_directories
from data import load_dataset_split
from metrics import compute_metrics
from plots import plot_feature_importance, plot_model_comparison


def evaluate_models() -> pd.DataFrame:
    ensure_directories()
    _, X_test, _, y_test = load_dataset_split()
    rows = []
    for model_key, model_info in MODELS.items():
        model = joblib.load(model_info["path"])
        y_pred = model.predict(X_test)
        y_score = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
        rows.append(
            {
                "model_key": model_key,
                "model_name": model_info["name"],
                **compute_metrics(y_test, y_pred, y_score),
            }
        )

    results = pd.DataFrame(rows)
    results.to_csv(RESULTS_DIR / "model_metrics.csv", index=False)
    plot_model_comparison(results, PLOTS_DIR / "model_comparison.png")

    importance_path = RESULTS_DIR / "feature_importance.csv"
    if importance_path.exists():
        plot_feature_importance(pd.read_csv(importance_path), PLOTS_DIR / "feature_importance.png")

    print(results.to_string(index=False))
    return results


def launch_streamlit() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(SRC_DIR / "app.py"), "--server.port", "8501"],
        cwd=PROJECT_ROOT,
        env=env,
        check=False,
    )


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    evaluate_models()
    launch_streamlit()


if __name__ == "__main__":
    main()
