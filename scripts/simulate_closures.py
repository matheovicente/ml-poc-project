from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import PLOTS_DIR, RAW_DATA_PATH, RESULTS_DIR, SUMMARY_FEATURES_PATH, ensure_directories
from simulation import plot_closure_scenario, plot_focus_closure_scenario, run_closure_scenarios


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simule la fermeture des chokepoints les plus critiques."
    )
    parser.add_argument("--top-n", type=int, default=5, help="Nombre de chokepoints à simuler.")
    parser.add_argument(
        "--durations",
        type=int,
        nargs="+",
        default=[14, 30, 90],
        help="Durées de fermeture à simuler, en jours.",
    )
    parser.add_argument(
        "--redistribution-rate",
        type=float,
        default=0.35,
        help="Part du trafic perdu redistribuée vers les autres chokepoints.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_directories()
    simulation_dir = PLOTS_DIR / "closure_simulations"
    simulation_dir.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(RAW_DATA_PATH, parse_dates=["date"])
    summary = pd.read_csv(SUMMARY_FEATURES_PATH)

    scenarios, simulation_summary = run_closure_scenarios(
        raw,
        summary,
        top_n=args.top_n,
        durations=args.durations,
        redistribution_rate=args.redistribution_rate,
    )

    scenarios_path = RESULTS_DIR / "closure_simulation_timeseries.csv"
    summary_path = RESULTS_DIR / "closure_simulation_summary.csv"
    scenarios.to_csv(scenarios_path, index=False)
    simulation_summary.to_csv(summary_path, index=False)

    for closed in simulation_summary["closed_chokepoint"].unique():
        safe_name = (
            closed.lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )
        for duration in args.durations:
            output = simulation_dir / f"{safe_name}_{duration}d_n_total.png"
            plot_closure_scenario(
                scenarios,
                closed_chokepoint=closed,
                duration_days=duration,
                output_path=output,
                variable="n_total",
            )
            focus_output = simulation_dir / f"{safe_name}_{duration}d_n_total_focus.png"
            plot_focus_closure_scenario(
                scenarios,
                closed_chokepoint=closed,
                duration_days=duration,
                output_path=focus_output,
                variable="n_total",
                top_changed=5,
            )

    print(f"Séries simulées : {scenarios_path}")
    print(f"Résumé simulation : {summary_path}")
    print(f"Graphiques : {simulation_dir}")
    print(
        simulation_summary.sort_values(
            ["duration_days", "lost_vessels_closed"],
            ascending=[True, False],
        ).to_string(index=False)
    )


if __name__ == "__main__":
    main()
