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
from plots import plot_model_comparison


def evaluate_models() -> pd.DataFrame:
    ensure_directories()
    _, X_test, _, y_test = load_dataset_split()

    rows = []
    for model_key, model_info in MODELS.items():
        model_path = model_info["path"]
        if not model_path.exists():
            raise FileNotFoundError(f"Modèle introuvable : {model_path}")
        model = joblib.load(model_path)
        if not hasattr(model, "predict"):
            raise TypeError(f"Le modèle {model_key} ne possède pas de méthode predict(X).")

        y_pred = model.predict(X_test)
        model_metrics = compute_metrics(y_test, y_pred)
        rows.append(
            {
                "model_key": model_key,
                "model_name": model_info["name"],
                **model_metrics,
            }
        )

    results = pd.DataFrame(rows)
    output_path = RESULTS_DIR / "model_metrics.csv"
    results.to_csv(output_path, index=False)
    print("\nMétriques des modèles")
    print(results.to_string(index=False))
    print(f"\nRésultats sauvegardés : {output_path}")
    plot_model_comparison(results, PLOTS_DIR / "model_comparison.png")
    return results


def launch_streamlit() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_DIR)
    app_path = SRC_DIR / "app.py"
    print("\nLancement de Streamlit : http://localhost:8501")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            "8501",
        ],
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
