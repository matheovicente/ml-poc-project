from __future__ import annotations

import sys
from pathlib import Path

import joblib
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import MODELS, RANDOM_STATE, RESULTS_DIR, ensure_directories
from data import load_dataset_split
from metrics import compute_metrics


def build_model_grids() -> dict[str, tuple[object, dict[str, list[object]]]]:
    return {
        "log_reg": (
            Pipeline(
                [
                    ("scaler", StandardScaler()),
                    (
                        "model",
                        LogisticRegression(
                            max_iter=3000,
                            class_weight="balanced",
                            random_state=RANDOM_STATE,
                        ),
                    ),
                ]
            ),
            {
                "model__C": [0.1, 1.0, 3.0],
                "model__solver": ["lbfgs"],
            },
        ),
        "random_forest": (
            RandomForestClassifier(
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            {
                "n_estimators": [250],
                "max_depth": [None, 12],
                "min_samples_leaf": [1, 3],
                "max_features": ["sqrt"],
            },
        ),
        "gradient_boosting": (
            GradientBoostingClassifier(random_state=RANDOM_STATE),
            {
                "n_estimators": [150, 250],
                "learning_rate": [0.05, 0.1],
                "max_depth": [2, 3],
                "subsample": [0.9],
                "min_samples_leaf": [1],
            },
        ),
    }


def _extract_feature_importance(model_key: str, model: object, feature_names: list[str]) -> list[dict[str, object]]:
    estimator = model
    if hasattr(model, "named_steps"):
        estimator = model.named_steps.get("model", model)

    values = None
    if hasattr(estimator, "feature_importances_"):
        values = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        values = abs(estimator.coef_).mean(axis=0)

    if values is None:
        return []

    return [
        {"model_key": model_key, "feature": feature, "importance": float(value)}
        for feature, value in sorted(zip(feature_names, values), key=lambda item: item[1], reverse=True)
    ]


def main() -> None:
    import pandas as pd

    ensure_directories()
    X_train, X_test, y_train, y_test = load_dataset_split()
    model_grids = build_model_grids()
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)

    cv_rows = []
    test_rows = []
    importance_rows = []

    for key, (model, param_grid) in model_grids.items():
        print(f"\nRecherche d'hyperparamètres : {MODELS[key]['name']}")
        search = GridSearchCV(
            model,
            param_grid=param_grid,
            scoring="f1_macro",
            cv=cv,
            n_jobs=1,
            refit=True,
        )
        search.fit(X_train, y_train)
        best_model = search.best_estimator_

        path = MODELS[key]["path"]
        joblib.dump(best_model, path)

        y_pred = best_model.predict(X_test)
        test_metrics = compute_metrics(y_test, y_pred)
        test_rows.append(
            {
                "model_key": key,
                "model_name": MODELS[key]["name"],
                "cv_best_f1_macro": float(search.best_score_),
                **test_metrics,
                "best_params": str(search.best_params_),
            }
        )

        cv_result = pd.DataFrame(search.cv_results_)
        cv_result = cv_result.sort_values("rank_test_score").head(10)
        for _, row in cv_result.iterrows():
            cv_rows.append(
                {
                    "model_key": key,
                    "rank": int(row["rank_test_score"]),
                    "mean_cv_f1_macro": float(row["mean_test_score"]),
                    "std_cv_f1_macro": float(row["std_test_score"]),
                    "params": str(row["params"]),
                }
            )

        importance_rows.extend(_extract_feature_importance(key, best_model, list(X_train.columns)))
        print(f"Meilleur CV F1 macro : {search.best_score_:.4f}")
        print(f"Métriques test : {test_metrics}")
        print(f"Modèle sauvegardé : {path}")

    pd.DataFrame(test_rows).to_csv(RESULTS_DIR / "training_model_metrics.csv", index=False)
    pd.DataFrame(cv_rows).to_csv(RESULTS_DIR / "training_cv_results.csv", index=False)
    pd.DataFrame(importance_rows).to_csv(RESULTS_DIR / "feature_importance.csv", index=False)
    print(f"\nRésultats d'entraînement sauvegardés dans : {RESULTS_DIR}")


if __name__ == "__main__":
    main()
