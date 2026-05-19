from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import PLOTS_DIR, RAW_DATA_PATH, RESULTS_DIR, SUMMARY_FEATURES_PATH, ensure_directories
from time_series import aggregate_backtest_metrics, plot_backtest_example, run_backtests


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest des prévisions de trafic par chokepoint.")
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--horizons", type=int, nargs="+", default=[14, 30, 90])
    parser.add_argument("--variable", default="n_total")
    parser.add_argument("--models", nargs="+", default=["analog", "sarimax"])
    parser.add_argument("--splits", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_directories()
    raw = pd.read_csv(RAW_DATA_PATH, parse_dates=["date"])
    summary = pd.read_csv(SUMMARY_FEATURES_PATH)
    portnames = (
        summary.sort_values("criticality_score", ascending=False)
        .head(args.top_n)["portname"]
        .tolist()
    )

    predictions, metrics = run_backtests(
        raw,
        portnames=portnames,
        horizons=args.horizons,
        variable=args.variable,
        models=args.models,
        n_splits=args.splits,
    )
    aggregated = aggregate_backtest_metrics(metrics)

    predictions_path = RESULTS_DIR / "time_series_backtest_predictions.csv"
    metrics_path = RESULTS_DIR / "time_series_backtest_metrics.csv"
    aggregated_path = RESULTS_DIR / "time_series_backtest_metrics_aggregated.csv"
    predictions.to_csv(predictions_path, index=False)
    metrics.to_csv(metrics_path, index=False)
    aggregated.to_csv(aggregated_path, index=False)

    backtest_plot_dir = PLOTS_DIR / "backtests"
    backtest_plot_dir.mkdir(parents=True, exist_ok=True)
    for portname in portnames:
        safe_name = portname.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        for horizon in args.horizons:
            plot_backtest_example(
                predictions,
                portname=portname,
                horizon_days=horizon,
                output_path=backtest_plot_dir / f"{safe_name}_{horizon}d_backtest.png",
            )

    print(f"Prédictions backtest : {predictions_path}")
    print(f"Métriques détaillées : {metrics_path}")
    print(f"Métriques agrégées : {aggregated_path}")
    print(f"Graphiques : {backtest_plot_dir}")
    print(aggregated.to_string(index=False))


if __name__ == "__main__":
    main()
