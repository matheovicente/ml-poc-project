from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import MODELS, RANDOM_STATE, RESULTS_DIR, ensure_directories
from data import load_dataset_split
from metrics import compute_metrics
from plots import plot_feature_importance


def model_grids() -> dict[str, tuple[object, dict[str, list[object]]]]:
    return {
        "log_reg": (
            Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "model",
                        LogisticRegression(max_iter=3000, class_weight="balanced", random_state=RANDOM_STATE),
                    ),
                ]
            ),
            {"model__C": [0.1, 0.5, 1.0, 3.0]},
        ),
        "random_forest": (
            RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
            {
                "n_estimators": [250, 500],
                "max_depth": [4, 8, None],
                "min_samples_leaf": [2, 5],
                "max_features": ["sqrt"],
            },
        ),
        "gradient_boosting": (
            GradientBoostingClassifier(random_state=RANDOM_STATE),
            {
                "n_estimators": [100, 200],
                "learning_rate": [0.03, 0.06],
                "max_depth": [2, 3],
                "subsample": [0.85],
            },
        ),
    }


def feature_importance_rows(model_key: str, model: object, features: list[str]) -> list[dict[str, object]]:
    estimator = model.named_steps["model"] if hasattr(model, "named_steps") else model
    values = None
    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        values = abs(estimator.coef_).mean(axis=0)
    if values is None:
        return []
    return [
        {"model_key": model_key, "feature": feature, "importance": float(value)}
        for feature, value in sorted(zip(features, values), key=lambda item: item[1], reverse=True)
    ]


def main() -> None:
    ensure_directories()
    X_train, X_test, y_train, y_test = load_dataset_split()
    splitter = TimeSeriesSplit(n_splits=4)

    metrics_rows = []
    cv_rows = []
    importance_rows = []

    for model_key, (model, grid) in model_grids().items():
        print(f"\nTraining {MODELS[model_key]['name']}")
        search = GridSearchCV(
            model,
            grid,
            scoring="f1",
            cv=splitter,
            n_jobs=1,
            refit=True,
        )
        search.fit(X_train, y_train)
        best_model = search.best_estimator_
        joblib.dump(best_model, MODELS[model_key]["path"])

        y_pred = best_model.predict(X_test)
        y_score = best_model.predict_proba(X_test)[:, 1] if hasattr(best_model, "predict_proba") else None
        row = {
            "model_key": model_key,
            "model_name": MODELS[model_key]["name"],
            "cv_best_f1": float(search.best_score_),
            **compute_metrics(y_test, y_pred, y_score),
            "best_params": str(search.best_params_),
        }
        metrics_rows.append(row)

        cv_result = pd.DataFrame(search.cv_results_).sort_values("rank_test_score").head(8)
        for _, cv_row in cv_result.iterrows():
            cv_rows.append(
                {
                    "model_key": model_key,
                    "rank": int(cv_row["rank_test_score"]),
                    "mean_cv_f1": float(cv_row["mean_test_score"]),
                    "std_cv_f1": float(cv_row["std_test_score"]),
                    "params": str(cv_row["params"]),
                }
            )

        importance_rows.extend(feature_importance_rows(model_key, best_model, list(X_train.columns)))
        print(row)

    metrics = pd.DataFrame(metrics_rows)
    importances = pd.DataFrame(importance_rows)
    metrics.to_csv(RESULTS_DIR / "training_model_metrics.csv", index=False)
    pd.DataFrame(cv_rows).to_csv(RESULTS_DIR / "training_cv_results.csv", index=False)
    importances.to_csv(RESULTS_DIR / "feature_importance.csv", index=False)
    plot_feature_importance(importances, RESULTS_DIR.parent / "plots" / "feature_importance.png")


if __name__ == "__main__":
    main()
