from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd

from .io import NUMERIC_COLUMNS, add_ratio_columns, safe_divide


def _daily_metrics(data: pd.DataFrame, gap_days: pd.Series) -> pd.DataFrame:
    """Combine same-day entries, then derive ratios and per-day rates.

    Ratios are recomputed from the daily totals rather than summed, and
    `gap_days` (days since the previous fill-up day, from the full dataset)
    is used to turn each fill's distance and cost into per-day rates.
    """
    daily = data[list(NUMERIC_COLUMNS)].resample("D").sum(min_count=1).dropna(how="all")
    daily = add_ratio_columns(daily)
    gaps = gap_days.reindex(daily.index)
    daily["NormalisedDistance"] = safe_divide(daily["Distance"], gaps)
    daily["NormalisedCost"] = safe_divide(daily["TotalCost"], gaps)
    return daily


def data_visualisations(data: pd.DataFrame, outputs_dir: str | Path = "outputs") -> Dict[str, str]:
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    fig_paths: Dict[str, str] = {}
    data = data.sort_index()

    # Days between fill-up days across all fuel types (first entry has no previous fill)
    fill_days = data.index.normalize().unique()
    gap_days = pd.Series(fill_days, index=fill_days).diff().dt.days

    if "PetrolType" in data.columns:
        series_sets = {
            str(fuel_type): _daily_metrics(group, gap_days)
            for fuel_type, group in data.groupby("PetrolType")
        }
    else:
        series_sets = {None: _daily_metrics(data, gap_days)}

    # --- Helper to plot one line per fuel type ---
    def save_multi_plot(column_name, title, ylabel, filename, colour="blue", fill="bfill"):
        plt.figure(figsize=(8, 4))

        for label, daily in series_sets.items():
            # Each fill-up's value covers the days leading up to it (bfill);
            # point-in-time values like price carry forward instead (ffill).
            series = daily[column_name].asfreq("D")
            series = series.bfill() if fill == "bfill" else series.ffill()
            if label is None:
                series.plot(color=colour)
            else:
                series.plot(label=label)

        if None not in series_sets:
            plt.legend()

        plt.title(title)
        plt.xlabel("Date")
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        path = str(outputs_dir / filename)
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return path

    # Generate the 5 charts
    fig_paths["daily_distance"] = save_multi_plot("NormalisedDistance", "Daily Distance", "KM/day", "daily_distance.png", "red")
    fig_paths["daily_cost"] = save_multi_plot("NormalisedCost", "Daily Cost", "$/day", "daily_cost.png", "orange")
    fig_paths["fuel_economy"] = save_multi_plot("FuelEconomy(L/100km)", "Fuel Economy", "L/100KM", "fuel_economy.png", "green")
    fig_paths["cost_per_km"] = save_multi_plot("CostPerKilometre", "Cost Per KM", "$/KM", "cost_per_km.png", "blue")
    fig_paths["petrol_price"] = save_multi_plot("PetrolPrice(PerLitre)", "Petrol Price", "$/Litre", "petrol_price.png", "purple", fill="ffill")

    return fig_paths
