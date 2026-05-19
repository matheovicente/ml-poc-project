from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import PORTWATCH_RAW_PATH, PLOTS_DIR, PROCESSED_DATA_PATH, ensure_directories
from plots import plot_pump_brent_timeseries, plot_tanker_traffic


CHOKEPOINTS = [
    "Strait of Hormuz",
    "Bab el-Mandeb Strait",
    "Suez Canal",
    "Malacca Strait",
]


def slugify(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_").replace("'", "")


def fetch_fred(series_id: str, start: pd.Timestamp, end: pd.Timestamp, column: str) -> pd.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    df = pd.read_csv(url)
    df.columns = ["date", column]
    df["date"] = pd.to_datetime(df["date"])
    df[column] = pd.to_numeric(df[column].replace(".", np.nan), errors="coerce")
    df = df[(df["date"] >= start) & (df["date"] <= end)].dropna()
    return df


def build_weekly_portwatch(raw_path: Path) -> pd.DataFrame:
    raw = pd.read_csv(raw_path, parse_dates=["date"])
    frames = []
    for chokepoint in CHOKEPOINTS:
        sub = raw[raw["portname"].eq(chokepoint)][["date", "n_tanker", "capacity_tanker"]].copy()
        if sub.empty:
            continue
        weekly = (
            sub.set_index("date")
            .resample("W-MON")
            .mean()
            .rename(
                columns={
                    "n_tanker": f"{slugify(chokepoint)}_n_tanker",
                    "capacity_tanker": f"{slugify(chokepoint)}_capacity_tanker",
                }
            )
        )
        frames.append(weekly)
    if not frames:
        raise ValueError("No chokepoint data found in PortWatch file.")
    return pd.concat(frames, axis=1).reset_index()


def add_rolling_features(df: pd.DataFrame, column: str) -> None:
    df[f"{column}_ma4"] = df[column].rolling(4, min_periods=2).mean()
    df[f"{column}_ma12"] = df[column].rolling(12, min_periods=4).mean()
    df[f"{column}_std4"] = df[column].rolling(4, min_periods=2).std()
    df[f"{column}_ratio12"] = df[column] / df[f"{column}_ma12"].replace(0, np.nan)
    for lag in [1, 2, 4]:
        df[f"{column}_lag{lag}"] = df[column].shift(lag)


def build_dataset() -> pd.DataFrame:
    weekly = build_weekly_portwatch(PORTWATCH_RAW_PATH)
    start = weekly["date"].min()
    end = weekly["date"].max()

    pump = fetch_fred("GASREGW", start, end, "pump_price")
    brent = fetch_fred("DCOILBRENTEU", start, end, "brent_price")

    pump_weekly = pump.set_index("date").resample("W-MON").mean().reset_index()
    brent_weekly = brent.set_index("date").resample("W-MON").last().reset_index()

    df = weekly.merge(pump_weekly, on="date", how="inner")
    df = df.merge(brent_weekly, on="date", how="left")
    df["brent_price"] = df["brent_price"].ffill()

    for optional_id, column in [("WTESTUS", "us_oil_stocks"), ("DTWEXBGS", "usd_index")]:
        try:
            optional = fetch_fred(optional_id, start, end, column)
            optional = optional.set_index("date").resample("W-MON").last().reset_index()
            df = df.merge(optional, on="date", how="left")
            df[column] = df[column].ffill()
        except Exception:
            pass

    tanker_columns = [f"{slugify(name)}_n_tanker" for name in CHOKEPOINTS]
    for column in tanker_columns:
        if column in df.columns:
            add_rolling_features(df, column)

    ratio_columns = [f"{column}_ratio12" for column in tanker_columns if f"{column}_ratio12" in df.columns]
    stress_components = [(1 - df[column].clip(0, 2)) for column in ratio_columns]
    df["maritime_stress"] = pd.concat(stress_components, axis=1).mean(axis=1)

    df["brent_return_1w"] = df["brent_price"].pct_change(1)
    df["brent_return_4w"] = df["brent_price"].pct_change(4)
    df["brent_vol_4w"] = df["brent_return_1w"].rolling(4).std()
    df["brent_return_1w_lag1"] = df["brent_return_1w"].shift(1)
    df["brent_return_1w_lag2"] = df["brent_return_1w"].shift(2)

    df["pump_return_1w"] = df["pump_price"].pct_change(1)
    df["pump_return_4w"] = df["pump_price"].pct_change(4)
    df["pump_return_1w_lag1"] = df["pump_return_1w"].shift(1)
    df["pump_return_1w_lag2"] = df["pump_return_1w"].shift(2)

    if "us_oil_stocks" in df.columns:
        df["stocks_return_4w"] = df["us_oil_stocks"].pct_change(4)
    if "usd_index" in df.columns:
        df["usd_return_4w"] = df["usd_index"].pct_change(4)

    df["month"] = df["date"].dt.month
    df["week_of_year"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_driving_season"] = df["month"].isin([5, 6, 7, 8]).astype(int)
    df["is_winter"] = df["month"].isin([12, 1, 2]).astype(int)

    df["target_return_1w"] = df["pump_price"].pct_change(1).shift(-1)
    df["target_price_up_1w"] = (df["target_return_1w"] > 0).astype(int)
    return df.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)


def main() -> None:
    ensure_directories()
    dataset = build_dataset()
    dataset.to_csv(PROCESSED_DATA_PATH, index=False)
    plot_pump_brent_timeseries(dataset, PLOTS_DIR / "pump_brent_timeseries.png")
    plot_tanker_traffic(dataset, PLOTS_DIR / "tanker_traffic_timeseries.png")
    print(f"Dataset saved to {PROCESSED_DATA_PATH}")
    print(f"Shape: {dataset.shape}")
    print(f"Period: {dataset['date'].min().date()} to {dataset['date'].max().date()}")
    print(f"Target positive rate: {dataset['target_price_up_1w'].mean():.2%}")


if __name__ == "__main__":
    main()
