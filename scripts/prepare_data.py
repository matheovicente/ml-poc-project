from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from config import RAW_DATA_PATH, MONTHLY_FEATURES_PATH, PLOTS_DIR, SUMMARY_FEATURES_PATH, ensure_directories
from features import build_monthly_features, build_summary_features, load_raw_portwatch
from plots import (
    plot_criticality_ranking,
    plot_disruption_frequency,
    plot_tanker_capacity,
    plot_traffic_by_chokepoint,
)


def main() -> None:
    ensure_directories()
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset brut introuvable : {RAW_DATA_PATH}")

    raw = load_raw_portwatch(RAW_DATA_PATH)
    monthly = build_monthly_features(raw)
    summary = build_summary_features(raw)

    monthly.to_csv(MONTHLY_FEATURES_PATH, index=False)
    summary.to_csv(SUMMARY_FEATURES_PATH, index=False)

    plot_criticality_ranking(summary, PLOTS_DIR / "criticality_ranking.png")
    plot_traffic_by_chokepoint(summary, PLOTS_DIR / "traffic_by_chokepoint.png")
    plot_tanker_capacity(summary, PLOTS_DIR / "tanker_capacity_by_chokepoint.png")
    plot_disruption_frequency(summary, PLOTS_DIR / "disruption_frequency.png")

    print(f"Dataset mensuel sauvegardé : {MONTHLY_FEATURES_PATH}")
    print(f"Shape mensuelle : {monthly.shape}")
    print(f"Résumé chokepoints sauvegardé : {SUMMARY_FEATURES_PATH}")
    print(f"Shape résumé : {summary.shape}")


if __name__ == "__main__":
    main()
