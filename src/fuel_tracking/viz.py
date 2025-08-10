from __future__ import annotations

from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd


def data_visualisations(data: pd.DataFrame, outputs_dir: str | Path = "outputs") -> Dict[str, str]:
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    fig_paths: Dict[str, str] = {}

    data = data.sort_index().copy()
    data["DaysSinceLastEntry"] = data.index.to_series().diff().dt.days.fillna(7)

    data["NormalisedCost"] = data["TotalCost"] / data["DaysSinceLastEntry"]
    data["NormalisedDistance"] = data["Distance"] / data["DaysSinceLastEntry"]

    daily = data.resample("D").sum()

    # Replace zeros with NaN for smoother plots, then backfill
    for col in ("NormalisedCost", "NormalisedDistance", "Kilometrage(L/100km)"):
        daily[col] = daily[col].replace(0, float("nan")).bfill()

    # 1. Daily Distance
    plt.figure(figsize=(8, 4))
    daily["NormalisedDistance"].plot(title="Daily Distance (Normalised)", color="blue")
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.ylabel("Distance (KM/day)")
    fig_paths["daily_distance"] = str(outputs_dir / "daily_distance.png")
    plt.savefig(fig_paths["daily_distance"], bbox_inches="tight")
    plt.close()

    # 2. Daily Fuel Cost
    plt.figure(figsize=(8, 4))
    daily["NormalisedCost"].plot(title="Daily Fuel Cost (Normalised)", color="green")
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.ylabel("Cost per Day ($)")
    fig_paths["rolling_money_spent"] = str(outputs_dir / "rolling_money_spent.png")
    plt.savefig(fig_paths["rolling_money_spent"], bbox_inches="tight")
    plt.close()

    # 3. Fuel Economy Over Time
    plt.figure(figsize=(8, 4))
    daily["Kilometrage(L/100km)"].plot(title="Daily Kilometerage (L/100) (Normalised)", color="red")
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.ylabel("Fuel Economy (L/100KM)")
    fig_paths["fuel_economy"] = str(outputs_dir / "fuel_economy.png")
    plt.savefig(fig_paths["fuel_economy"], bbox_inches="tight")
    plt.close()

    return fig_paths
