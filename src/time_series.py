from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from statsmodels.tsa.statespace.sarimax import SARIMAX


def smape(y_true: pd.Series, y_pred: pd.Series) -> float:
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    values = np.where(denominator == 0, 0, np.abs(y_true - y_pred) / denominator)
    return float(np.mean(values) * 100)


def mape(y_true: pd.Series, y_pred: pd.Series) -> float:
    denominator = y_true.replace(0, np.nan)
    return float((np.abs((y_true - y_pred) / denominator).dropna()).mean() * 100)


def predict_by_recent_analog(
    series: pd.DataFrame,
    anchor_date: pd.Timestamp,
    horizon_days: int,
    variable: str,
) -> pd.DataFrame:
    """Forecast the next horizon by replaying the previous horizon."""
    history = series[series["date"] <= anchor_date].tail(horizon_days)
    actual = series[
        (series["date"] > anchor_date)
        & (series["date"] <= anchor_date + pd.Timedelta(days=horizon_days))
    ].head(horizon_days)

    if len(history) < horizon_days or len(actual) < horizon_days:
        return pd.DataFrame()

    return pd.DataFrame(
        {
            "date": actual["date"].to_numpy(),
            "y_true": actual[variable].to_numpy(dtype=float),
            "y_pred": history[variable].to_numpy(dtype=float),
        }
    )


def prepare_daily_series(series: pd.DataFrame, variable: str) -> pd.DataFrame:
    """Return one clean daily observation per date for time-series models."""
    daily = (
        series[["date", variable]]
        .dropna()
        .sort_values("date")
        .groupby("date", as_index=False)[variable]
        .mean()
        .set_index("date")
        .asfreq("D")
    )
    daily[variable] = (
        daily[variable]
        .interpolate(method="time", limit_direction="both")
        .ffill()
        .bfill()
        .clip(lower=0)
    )
    return daily.reset_index()


def predict_by_sarimax(
    series: pd.DataFrame,
    anchor_date: pd.Timestamp,
    horizon_days: int,
    variable: str,
    train_window_days: int = 730,
    min_train_days: int = 365,
) -> pd.DataFrame:
    """Forecast traffic with a weekly-seasonal SARIMAX model."""
    train_start = anchor_date - pd.Timedelta(days=train_window_days)
    train = series[(series["date"] >= train_start) & (series["date"] <= anchor_date)]
    actual = series[
        (series["date"] > anchor_date)
        & (series["date"] <= anchor_date + pd.Timedelta(days=horizon_days))
    ].head(horizon_days)

    if len(train) < min_train_days or len(actual) < horizon_days:
        return pd.DataFrame()

    y_train = train.set_index("date")[variable].astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        warnings.simplefilter("ignore", UserWarning)
        model = SARIMAX(
            y_train,
            order=(1, 0, 1),
            seasonal_order=(1, 0, 1, 7),
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fitted = model.fit(disp=False, maxiter=80)
        forecast = fitted.forecast(steps=horizon_days)

    return pd.DataFrame(
        {
            "date": actual["date"].to_numpy(),
            "y_true": actual[variable].to_numpy(dtype=float),
            "y_pred": np.clip(forecast.to_numpy(dtype=float), 0, None),
        }
    )


def backtest_chokepoint_series(
    raw: pd.DataFrame,
    portname: str,
    horizon_days: int = 30,
    variable: str = "n_total",
    model_name: str = "analog",
    n_splits: int = 8,
    min_train_days: int = 365,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    series = prepare_daily_series(raw[raw["portname"].eq(portname)], variable)
    if len(series) < min_train_days + horizon_days:
        return pd.DataFrame(), pd.DataFrame()

    first_anchor_idx = min_train_days
    last_anchor_idx = len(series) - horizon_days - 1
    if first_anchor_idx >= last_anchor_idx:
        return pd.DataFrame(), pd.DataFrame()

    anchor_indices = np.linspace(first_anchor_idx, last_anchor_idx, n_splits, dtype=int)
    prediction_frames = []
    metric_rows = []
    for split_id, idx in enumerate(anchor_indices, start=1):
        anchor_date = series.loc[idx, "date"]
        try:
            if model_name == "analog":
                predictions = predict_by_recent_analog(
                    series,
                    anchor_date=anchor_date,
                    horizon_days=horizon_days,
                    variable=variable,
                )
            elif model_name == "sarimax":
                predictions = predict_by_sarimax(
                    series,
                    anchor_date=anchor_date,
                    horizon_days=horizon_days,
                    variable=variable,
                    min_train_days=min_train_days,
                )
            else:
                raise ValueError(f"Modèle time series inconnu : {model_name}")
        except Exception:
            continue

        if predictions.empty:
            continue
        predictions["model"] = model_name
        predictions["portname"] = portname
        predictions["split_id"] = split_id
        predictions["anchor_date"] = anchor_date
        predictions["horizon_days"] = horizon_days
        predictions["variable"] = variable
        predictions["error"] = predictions["y_true"] - predictions["y_pred"]
        prediction_frames.append(predictions)

        y_true = predictions["y_true"]
        y_pred = predictions["y_pred"]
        metric_rows.append(
            {
                "model": model_name,
                "portname": portname,
                "split_id": split_id,
                "anchor_date": anchor_date.date().isoformat(),
                "horizon_days": horizon_days,
                "variable": variable,
                "mae": float(np.mean(np.abs(y_true - y_pred))),
                "rmse": float(np.sqrt(np.mean((y_true - y_pred) ** 2))),
                "mape": mape(y_true, y_pred),
                "smape": smape(y_true, y_pred),
                "mean_actual": float(y_true.mean()),
                "mean_predicted": float(y_pred.mean()),
            }
        )

    if not prediction_frames:
        return pd.DataFrame(), pd.DataFrame()
    return pd.concat(prediction_frames, ignore_index=True), pd.DataFrame(metric_rows)


def run_backtests(
    raw: pd.DataFrame,
    portnames: list[str],
    horizons: list[int] | None = None,
    variable: str = "n_total",
    models: list[str] | None = None,
    n_splits: int = 8,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    horizons = horizons or [14, 30, 90]
    models = models or ["analog", "sarimax"]
    all_predictions = []
    all_metrics = []
    for portname in portnames:
        for horizon in horizons:
            for model_name in models:
                predictions, metrics = backtest_chokepoint_series(
                    raw,
                    portname,
                    horizon_days=horizon,
                    variable=variable,
                    model_name=model_name,
                    n_splits=n_splits,
                )
                if not predictions.empty:
                    all_predictions.append(predictions)
                    all_metrics.append(metrics)

    if not all_predictions:
        return pd.DataFrame(), pd.DataFrame()
    return pd.concat(all_predictions, ignore_index=True), pd.concat(all_metrics, ignore_index=True)


def aggregate_backtest_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    if metrics.empty:
        return metrics
    return (
        metrics.groupby(["model", "portname", "horizon_days", "variable"], as_index=False)
        .agg(
            mae=("mae", "mean"),
            rmse=("rmse", "mean"),
            mape=("mape", "mean"),
            smape=("smape", "mean"),
            mean_actual=("mean_actual", "mean"),
            mean_predicted=("mean_predicted", "mean"),
        )
        .sort_values(["horizon_days", "portname", "mae"])
    )


def plot_backtest_example(
    predictions: pd.DataFrame,
    portname: str,
    horizon_days: int,
    output_path: Path,
) -> None:
    import matplotlib.pyplot as plt

    subset = predictions[
        predictions["portname"].eq(portname)
        & predictions["horizon_days"].eq(horizon_days)
    ].copy()
    if subset.empty:
        return
    split_id = subset["split_id"].max()
    subset = subset[subset["split_id"].eq(split_id)].sort_values("date")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(11, 6))
    actual = subset.drop_duplicates("date")
    ax.plot(actual["date"], actual["y_true"], label="Trafic réel", linewidth=2.8, color="#222222")
    labels = {"analog": "Baseline analogue", "sarimax": "SARIMAX hebdomadaire"}
    for model_name, model_subset in subset.groupby("model"):
        ax.plot(
            model_subset["date"],
            model_subset["y_pred"],
            label=labels.get(model_name, model_name),
            linewidth=2.1,
        )
    ax.set_title(f"Backtest trafic {portname} - horizon {horizon_days} jours")
    ax.set_ylabel("Navires par jour")
    ax.set_xlabel("Date")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
