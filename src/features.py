from __future__ import annotations

import numpy as np
import pandas as pd

from config import NUMERIC_FEATURES


VESSEL_COLUMNS = [
    "n_container",
    "n_dry_bulk",
    "n_general_cargo",
    "n_roro",
    "n_tanker",
    "n_cargo",
    "n_total",
]

CAPACITY_COLUMNS = [
    "capacity_container",
    "capacity_dry_bulk",
    "capacity_general_cargo",
    "capacity_roro",
    "capacity_tanker",
    "capacity_cargo",
    "capacity",
]


def load_raw_portwatch(path: str | "PathLike[str]") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    for column in VESSEL_COLUMNS + CAPACITY_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.sort_values(["portid", "date"]).reset_index(drop=True)


def add_disruption_features(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    frame = df.copy()
    grouped = frame.groupby("portid", group_keys=False)

    for column in ["n_total", "n_tanker"]:
        rolling_mean = grouped[column].rolling(window, min_periods=15).mean().reset_index(level=0, drop=True)
        rolling_std = grouped[column].rolling(window, min_periods=15).std().reset_index(level=0, drop=True)
        frame[f"{column}_rolling_mean_30"] = rolling_mean
        frame[f"{column}_rolling_std_30"] = rolling_std
        frame[f"{column}_zscore"] = (frame[column] - rolling_mean) / rolling_std.replace(0, np.nan)
        frame[f"{column}_drop_vs_ma"] = (rolling_mean - frame[column]) / rolling_mean.replace(0, np.nan)

    frame["is_disruption_total"] = frame["n_total_zscore"] < -2
    frame["is_strong_disruption_total"] = frame["n_total_zscore"] < -3
    frame["is_disruption_tanker"] = frame["n_tanker_zscore"] < -2
    frame["is_strong_disruption_tanker"] = frame["n_tanker_zscore"] < -3
    return frame


def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator / denominator.replace(0, np.nan)


def _aggregate_features(group: pd.DataFrame) -> pd.Series:
    observed_days = int(group["date"].nunique())
    mean_n_total = group["n_total"].mean()
    std_n_total = group["n_total"].std()
    mean_n_tanker = group["n_tanker"].mean()
    mean_capacity = group["capacity"].mean()
    mean_capacity_tanker = group["capacity_tanker"].mean()

    return pd.Series(
        {
            "portname": group["portname"].iloc[0],
            "mean_n_total": mean_n_total,
            "median_n_total": group["n_total"].median(),
            "std_n_total": std_n_total,
            "cv_n_total": std_n_total / mean_n_total if mean_n_total else np.nan,
            "mean_n_tanker": mean_n_tanker,
            "tanker_share": mean_n_tanker / mean_n_total if mean_n_total else np.nan,
            "mean_capacity": mean_capacity,
            "mean_capacity_tanker": mean_capacity_tanker,
            "tanker_capacity_share": mean_capacity_tanker / mean_capacity if mean_capacity else np.nan,
            "mean_n_container": group["n_container"].mean(),
            "mean_n_dry_bulk": group["n_dry_bulk"].mean(),
            "mean_n_general_cargo": group["n_general_cargo"].mean(),
            "mean_n_cargo": group["n_cargo"].mean(),
            "disruption_frequency_total": group["is_disruption_total"].mean(),
            "disruption_frequency_tanker": group["is_disruption_tanker"].mean(),
            "strong_disruption_frequency_total": group["is_strong_disruption_total"].mean(),
            "strong_disruption_frequency_tanker": group["is_strong_disruption_tanker"].mean(),
            "max_drop_n_total": group["n_total_drop_vs_ma"].max(),
            "max_drop_n_tanker": group["n_tanker_drop_vs_ma"].max(),
            "observed_days": observed_days,
            "estimated_7d_lost_vessels": mean_n_total * 7,
            "estimated_14d_lost_vessels": mean_n_total * 14,
            "estimated_30d_lost_vessels": mean_n_total * 30,
            "estimated_7d_lost_tankers": mean_n_tanker * 7,
            "estimated_14d_lost_tankers": mean_n_tanker * 14,
            "estimated_30d_lost_tankers": mean_n_tanker * 30,
            "estimated_7d_lost_capacity": mean_capacity * 7,
            "estimated_14d_lost_capacity": mean_capacity * 14,
            "estimated_30d_lost_capacity": mean_capacity * 30,
            "estimated_7d_lost_tanker_capacity": mean_capacity_tanker * 7,
            "estimated_14d_lost_tanker_capacity": mean_capacity_tanker * 14,
            "estimated_30d_lost_tanker_capacity": mean_capacity_tanker * 30,
        }
    )


def build_monthly_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = add_disruption_features(df)
    frame["year"] = frame["date"].dt.year
    frame["month"] = frame["date"].dt.month

    monthly = (
        frame.groupby(["portid", "year", "month"], as_index=False)
        .apply(_aggregate_features, include_groups=False)
        .reset_index(drop=True)
    )
    return add_criticality_target(monthly)


def build_summary_features(df: pd.DataFrame) -> pd.DataFrame:
    frame = add_disruption_features(df)
    summary = (
        frame.groupby("portid", as_index=False)
        .apply(_aggregate_features, include_groups=False)
        .reset_index(drop=True)
    )
    return add_criticality_target(summary)


def _minmax(series: pd.Series) -> pd.Series:
    series = series.astype(float)
    minimum = series.min()
    maximum = series.max()
    if pd.isna(minimum) or pd.isna(maximum) or maximum == minimum:
        return pd.Series(0.0, index=series.index)
    return (series - minimum) / (maximum - minimum)


def add_criticality_target(df: pd.DataFrame) -> pd.DataFrame:
    frame = df.copy()
    weights = {
        "mean_n_total": 0.30,
        "mean_capacity": 0.25,
        "mean_capacity_tanker": 0.20,
        "tanker_share": 0.15,
        "disruption_frequency_total": 0.10,
    }

    raw_score = pd.Series(0.0, index=frame.index)
    for column, weight in weights.items():
        raw_score = raw_score + weight * _minmax(frame[column].fillna(0))

    frame["criticality_score"] = (raw_score * 100).round(3)
    frame["criticality_class"] = pd.qcut(
        frame["criticality_score"].rank(method="first"),
        q=4,
        labels=[0, 1, 2, 3],
    ).astype(int)

    for column in NUMERIC_FEATURES:
        if column in frame.columns:
            frame[column] = frame[column].replace([np.inf, -np.inf], np.nan).fillna(0)
    return frame

