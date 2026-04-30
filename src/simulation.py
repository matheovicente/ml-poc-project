from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_DURATIONS = [14, 30, 90]

ROUTE_ALTERNATIVES = {
    "Strait of Hormuz": {
        "redistribution_rate": 0.08,
        "alternatives": {
            "Bab el-Mandeb Strait": 0.35,
            "Suez Canal": 0.25,
            "Cape of Good Hope": 0.25,
            "Malacca Strait": 0.15,
        },
    },
    "Malacca Strait": {
        "redistribution_rate": 0.45,
        "alternatives": {
            "Lombok Strait": 0.40,
            "Sunda Strait": 0.25,
            "Makassar Strait": 0.20,
            "Ombai Strait": 0.10,
            "Cape of Good Hope": 0.05,
        },
    },
    "Taiwan Strait": {
        "redistribution_rate": 0.35,
        "alternatives": {
            "Luzon Strait": 0.45,
            "Korea Strait": 0.25,
            "Tsugaru Strait": 0.15,
            "Malacca Strait": 0.15,
        },
    },
    "Bohai Strait": {
        "redistribution_rate": 0.30,
        "alternatives": {
            "Korea Strait": 0.45,
            "Tsugaru Strait": 0.25,
            "Taiwan Strait": 0.20,
            "Malacca Strait": 0.10,
        },
    },
    "Korea Strait": {
        "redistribution_rate": 0.35,
        "alternatives": {
            "Tsugaru Strait": 0.40,
            "Taiwan Strait": 0.25,
            "Bohai Strait": 0.20,
            "Luzon Strait": 0.15,
        },
    },
    "Suez Canal": {
        "redistribution_rate": 0.65,
        "alternatives": {
            "Cape of Good Hope": 0.85,
            "Gibraltar Strait": 0.15,
        },
    },
    "Bab el-Mandeb Strait": {
        "redistribution_rate": 0.60,
        "alternatives": {
            "Cape of Good Hope": 0.75,
            "Suez Canal": 0.15,
            "Gibraltar Strait": 0.10,
        },
    },
    "Panama Canal": {
        "redistribution_rate": 0.45,
        "alternatives": {
            "Cape of Good Hope": 0.30,
            "Magellan Strait": 0.25,
            "Suez Canal": 0.20,
            "Malacca Strait": 0.15,
            "Gibraltar Strait": 0.10,
        },
    },
}


def select_top_chokepoints(summary: pd.DataFrame, top_n: int = 5) -> list[str]:
    return (
        summary.sort_values("criticality_score", ascending=False)
        .head(top_n)["portname"]
        .tolist()
    )


def build_baseline_forecast(
    raw: pd.DataFrame,
    chokepoints: list[str],
    duration_days: int,
    lookback_days: int = 365,
    pre_event_days: int = 60,
    anchor_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Build a recent-history analog baseline plus a pre-closure window."""
    frame = raw.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame = frame.sort_values(["portname", "date"]).reset_index(drop=True)
    latest_date = pd.to_datetime(anchor_date) if anchor_date is not None else frame["date"].max()
    frame = frame[frame["date"] <= latest_date].copy()

    closure_date = latest_date + pd.Timedelta(days=1)
    future_dates = pd.date_range(
        closure_date,
        periods=duration_days,
        freq="D",
    )

    future_frames = []
    for portname in chokepoints:
        history = frame[frame["portname"].eq(portname)].tail(duration_days).copy()
        if history.empty:
            continue
        if len(history) < duration_days:
            reps = int(np.ceil(duration_days / len(history)))
            history = pd.concat([history] * reps, ignore_index=True).tail(duration_days)
        history = history.tail(duration_days).reset_index(drop=True)
        future = pd.DataFrame(
            {
                "portname": portname,
                "date": future_dates,
                "baseline_n_total": history["n_total"].to_numpy(),
                "baseline_n_tanker": history["n_tanker"].to_numpy(),
                "baseline_capacity": history["capacity"].to_numpy(),
                "baseline_capacity_tanker": history["capacity_tanker"].to_numpy(),
            }
        )
        future_frames.append(future)

    future = pd.concat(future_frames, ignore_index=True)
    future["period"] = "simulation"
    future["days_from_closure"] = (future["date"] - closure_date).dt.days

    pre_start = latest_date - pd.Timedelta(days=pre_event_days - 1)
    pre = frame[
        (frame["date"] >= pre_start)
        & (frame["date"] <= latest_date)
        & (frame["portname"].isin(chokepoints))
    ].copy()
    pre = pre.rename(
        columns={
            "n_total": "baseline_n_total",
            "n_tanker": "baseline_n_tanker",
            "capacity": "baseline_capacity",
            "capacity_tanker": "baseline_capacity_tanker",
        }
    )
    pre = pre[
        [
            "portname",
            "date",
            "baseline_n_total",
            "baseline_n_tanker",
            "baseline_capacity",
            "baseline_capacity_tanker",
        ]
    ]
    pre["period"] = "historique"
    pre["days_from_closure"] = (pre["date"] - closure_date).dt.days
    return (
        pd.concat([pre, future], ignore_index=True)
        .sort_values(["portname", "date"])
        .reset_index(drop=True)
    )


def choose_normal_anchor_date(
    raw: pd.DataFrame,
    closed_chokepoint: str,
    pre_event_days: int = 60,
    min_ratio_to_median: float = 0.75,
) -> pd.Timestamp:
    frame = raw.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    series = (
        frame[frame["portname"].eq(closed_chokepoint)]
        .sort_values("date")[["date", "n_total"]]
        .dropna()
        .reset_index(drop=True)
    )
    if series.empty:
        return frame["date"].max()

    historical_median = series["n_total"].median()
    rolling_median = series["n_total"].rolling(pre_event_days, min_periods=pre_event_days).median()
    candidates = series.loc[
        rolling_median.ge(historical_median * min_ratio_to_median)
        & series["n_total"].ge(historical_median * min_ratio_to_median),
        "date",
    ]
    if candidates.empty:
        return series["date"].max()
    return candidates.max()


def simulate_single_closure(
    baseline: pd.DataFrame,
    closed_chokepoint: str,
    redistribution_rate: float = 0.35,
    ramp_days: int = 7,
    use_route_alternatives: bool = True,
) -> pd.DataFrame:
    """Simulate closure and partial redistribution to the other chokepoints.

    The redistribution is intentionally simple and auditable:
    - the closed chokepoint's simulated flow is set to zero;
    - a share of its lost flow is redistributed to open chokepoints;
    - open chokepoints receive that extra flow according to their baseline
      capacity share on each simulated day;
    - the redistribution ramps linearly during the first days.
    """
    result = baseline.copy()
    route_info = ROUTE_ALTERNATIVES.get(closed_chokepoint, {})
    if use_route_alternatives and route_info:
        redistribution_rate = float(route_info.get("redistribution_rate", redistribution_rate))
        alternative_weights = route_info.get("alternatives", {})
    else:
        alternative_weights = {}
    result["closed_chokepoint"] = closed_chokepoint
    result["is_post_closure"] = result["days_from_closure"] >= 0
    result["days_since_closure"] = np.where(
        result["is_post_closure"],
        result["days_from_closure"] + 1,
        0,
    )
    result["ramp_factor"] = np.where(
        result["is_post_closure"],
        np.minimum(1.0, result["days_since_closure"] / ramp_days),
        0.0,
    )

    result["sim_n_total"] = result["baseline_n_total"]
    result["sim_n_tanker"] = result["baseline_n_tanker"]
    result["sim_capacity"] = result["baseline_capacity"]
    result["sim_capacity_tanker"] = result["baseline_capacity_tanker"]
    for column in [
        "sim_n_total",
        "sim_n_tanker",
        "sim_capacity",
        "sim_capacity_tanker",
        "baseline_n_total",
        "baseline_n_tanker",
        "baseline_capacity",
        "baseline_capacity_tanker",
    ]:
        result[column] = result[column].astype(float)

    closed_rows = result["portname"].eq(closed_chokepoint) & result["is_post_closure"]
    lost_by_day = result.loc[
        closed_rows,
        [
            "date",
            "baseline_n_total",
            "baseline_n_tanker",
            "baseline_capacity",
            "baseline_capacity_tanker",
        ],
    ].rename(
        columns={
            "baseline_n_total": "lost_n_total",
            "baseline_n_tanker": "lost_n_tanker",
            "baseline_capacity": "lost_capacity",
            "baseline_capacity_tanker": "lost_capacity_tanker",
        }
    )

    result = result.merge(lost_by_day, on="date", how="left")
    open_rows = ~result["portname"].eq(closed_chokepoint) & result["is_post_closure"]
    capacity_pool = (
        result.loc[open_rows]
        .groupby("date")["baseline_capacity"]
        .sum()
        .rename("open_capacity_pool")
    )
    result = result.merge(capacity_pool, on="date", how="left")
    if alternative_weights:
        result["route_weight"] = result["portname"].map(alternative_weights).fillna(0.0)
        route_weight_sum = result.groupby("date")["route_weight"].transform("sum")
        result["redistribution_weight"] = np.where(
            open_rows & (route_weight_sum > 0),
            result["route_weight"] / route_weight_sum,
            0.0,
        )
    else:
        result["redistribution_weight"] = np.where(
            open_rows,
            result["baseline_capacity"] / result["open_capacity_pool"].replace(0, np.nan),
            0.0,
        )
    result["redistribution_weight"] = result["redistribution_weight"].fillna(0)
    result["redistribution_rate"] = redistribution_rate

    for variable in ["n_total", "n_tanker", "capacity", "capacity_tanker"]:
        lost_col = f"lost_{variable}"
        sim_col = f"sim_{variable}"
        extra = (
            result[lost_col]
            * redistribution_rate
            * result["ramp_factor"]
            * result["redistribution_weight"]
        )
        result.loc[open_rows, sim_col] = result.loc[open_rows, sim_col] + extra[open_rows]
        result.loc[closed_rows, sim_col] = 0.0
        result[f"delta_{variable}"] = result[sim_col] - result[f"baseline_{variable}"]

    return result


def run_closure_scenarios(
    raw: pd.DataFrame,
    summary: pd.DataFrame,
    top_n: int = 5,
    durations: list[int] | None = None,
    redistribution_rate: float = 0.35,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    durations = durations or DEFAULT_DURATIONS
    closed_chokepoints = select_top_chokepoints(summary, top_n=top_n)
    chokepoints = set(closed_chokepoints)
    for closed in closed_chokepoints:
        chokepoints.update(ROUTE_ALTERNATIVES.get(closed, {}).get("alternatives", {}).keys())
    available = set(raw["portname"].unique())
    chokepoints = [name for name in sorted(chokepoints) if name in available]

    scenario_frames = []
    summary_rows = []
    for duration in durations:
        for closed in closed_chokepoints:
            anchor_date = choose_normal_anchor_date(raw, closed)
            baseline = build_baseline_forecast(
                raw,
                chokepoints,
                duration_days=duration,
                anchor_date=anchor_date,
            )
            scenario = simulate_single_closure(
                baseline,
                closed_chokepoint=closed,
                redistribution_rate=redistribution_rate,
            )
            scenario["duration_days"] = duration
            scenario["scenario_name"] = f"{closed} fermé {duration} jours"
            scenario["anchor_date"] = anchor_date.date().isoformat()
            scenario_frames.append(scenario)

            closed_rows = scenario["portname"].eq(closed) & scenario["is_post_closure"]
            open_rows = ~scenario["portname"].eq(closed) & scenario["is_post_closure"]
            summary_rows.append(
                {
                    "closed_chokepoint": closed,
                    "duration_days": duration,
                    "anchor_date": anchor_date.date().isoformat(),
                    "redistribution_rate": scenario["redistribution_rate"].max(),
                    "lost_vessels_closed": -scenario.loc[closed_rows, "delta_n_total"].sum(),
                    "lost_tankers_closed": -scenario.loc[closed_rows, "delta_n_tanker"].sum(),
                    "lost_capacity_closed": -scenario.loc[closed_rows, "delta_capacity"].sum(),
                    "lost_tanker_capacity_closed": -scenario.loc[
                        closed_rows, "delta_capacity_tanker"
                    ].sum(),
                    "redistributed_vessels_to_others": scenario.loc[
                        open_rows, "delta_n_total"
                    ].sum(),
                    "redistributed_tankers_to_others": scenario.loc[
                        open_rows, "delta_n_tanker"
                    ].sum(),
                    "net_vessels_loss": -scenario["delta_n_total"].sum(),
                    "net_tankers_loss": -scenario["delta_n_tanker"].sum(),
                }
            )

    return pd.concat(scenario_frames, ignore_index=True), pd.DataFrame(summary_rows)


def plot_closure_scenario(
    scenario: pd.DataFrame,
    closed_chokepoint: str,
    duration_days: int,
    output_path: Path,
    variable: str = "n_total",
    smooth_window: int = 7,
) -> None:
    import matplotlib.pyplot as plt

    subset = scenario[
        (scenario["closed_chokepoint"] == closed_chokepoint)
        & (scenario["duration_days"] == duration_days)
    ].copy()
    sim_col = f"sim_{variable}"
    baseline_col = f"baseline_{variable}"
    if smooth_window > 1:
        subset = subset.sort_values(["portname", "date"]).copy()
        subset[f"{sim_col}_smooth"] = (
            subset.groupby("portname")[sim_col]
            .transform(lambda series: series.rolling(smooth_window, min_periods=1).mean())
        )
        subset[f"{baseline_col}_smooth"] = (
            subset.groupby("portname")[baseline_col]
            .transform(lambda series: series.rolling(smooth_window, min_periods=1).mean())
        )
        sim_plot_col = f"{sim_col}_smooth"
        baseline_plot_col = f"{baseline_col}_smooth"
        y_label_suffix = f"moyenne mobile {smooth_window}j"
    else:
        sim_plot_col = sim_col
        baseline_plot_col = baseline_col
        y_label_suffix = "journalier"

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(13, 7))
    for portname, group in subset.groupby("portname"):
        group = group.sort_values("date")
        linewidth = 3 if portname == closed_chokepoint else 1.8
        alpha = 1.0 if portname == closed_chokepoint else 0.8
        if group[sim_plot_col].max() <= 2 and portname != closed_chokepoint:
            continue
        ax.plot(group["date"], group[sim_plot_col], label=portname, linewidth=linewidth, alpha=alpha)

    closure_date = subset.loc[subset["days_from_closure"].eq(0), "date"].min()
    if pd.notna(closure_date):
        ax.axvline(closure_date, color="black", linestyle="--", linewidth=1.3, label="Début fermeture")
    ax.set_title(
        f"Avant / fermeture / après : fermeture de {closed_chokepoint} pendant {duration_days} jours"
    )
    ax.set_ylabel(f"Navires simulés ({y_label_suffix})" if variable == "n_total" else variable)
    ax.set_xlabel("Date simulée")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def plot_focus_closure_scenario(
    scenario: pd.DataFrame,
    closed_chokepoint: str,
    duration_days: int,
    output_path: Path,
    variable: str = "n_total",
    smooth_window: int = 7,
    top_changed: int = 5,
) -> None:
    import matplotlib.pyplot as plt

    subset = scenario[
        (scenario["closed_chokepoint"] == closed_chokepoint)
        & (scenario["duration_days"] == duration_days)
    ].copy()
    sim_col = f"sim_{variable}"
    baseline_col = f"baseline_{variable}"
    subset = subset.sort_values(["portname", "date"]).copy()
    subset[f"{sim_col}_smooth"] = (
        subset.groupby("portname")[sim_col]
        .transform(lambda series: series.rolling(smooth_window, min_periods=1).mean())
    )
    subset[f"{baseline_col}_smooth"] = (
        subset.groupby("portname")[baseline_col]
        .transform(lambda series: series.rolling(smooth_window, min_periods=1).mean())
    )
    subset["abs_delta_post"] = np.where(
        subset["days_from_closure"] >= 0,
        (subset[f"{sim_col}_smooth"] - subset[f"{baseline_col}_smooth"]).abs(),
        0.0,
    )

    changed = (
        subset[~subset["portname"].eq(closed_chokepoint)]
        .groupby("portname")["abs_delta_post"]
        .sum()
        .sort_values(ascending=False)
        .head(top_changed)
        .index.tolist()
    )
    focus_ports = [closed_chokepoint] + changed
    focus = subset[subset["portname"].isin(focus_ports)].copy()

    colors = {
        closed_chokepoint: "#d62728",
    }
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12.5, 6.5))
    for portname, group in focus.groupby("portname"):
        group = group.sort_values("date")
        linewidth = 3.4 if portname == closed_chokepoint else 2.3
        alpha = 1.0 if portname == closed_chokepoint else 0.92
        ax.plot(
            group["date"],
            group[f"{sim_col}_smooth"],
            label=portname,
            linewidth=linewidth,
            alpha=alpha,
            color=colors.get(portname),
        )

    closure_date = focus.loc[focus["days_from_closure"].eq(0), "date"].min()
    if pd.notna(closure_date):
        ax.axvline(closure_date, color="black", linestyle="--", linewidth=1.4)
        ax.text(
            closure_date,
            ax.get_ylim()[1] * 0.96,
            " fermeture",
            fontsize=10,
            va="top",
            ha="left",
        )

    ax.set_title(
        f"Routes les plus impactées - fermeture de {closed_chokepoint} ({duration_days} jours)",
        fontsize=15,
    )
    ax.set_ylabel(f"Navires par jour, moyenne mobile {smooth_window}j")
    ax.set_xlabel("Date")
    ax.legend(fontsize=9, ncol=2, loc="best")
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)
