from __future__ import annotations

import sys
from pathlib import Path

import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import MODELS, RANDOM_STATE, ensure_directories
from data import load_dataset_split


def build_models() -> dict[str, object]:
    return {
        "log_reg": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=2000,
                        class_weight="balanced",
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def main() -> None:
    ensure_directories()
    X_train, _, y_train, _ = load_dataset_split()
    models = build_models()

    for key, model in models.items():
        model.fit(X_train, y_train)
        path = MODELS[key]["path"]
        joblib.dump(model, path)
        print(f"Modèle entraîné et sauvegardé : {path}")


if __name__ == "__main__":
    main()
