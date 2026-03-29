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

    # Calculate global metrics
    data["DaysSinceLastEntry"] = data.index.to_series().diff().dt.days.fillna(7)
    data["NormalisedCost"] = data["TotalCost"] / data["DaysSinceLastEntry"]
    data["NormalisedDistance"] = data["Distance"] / data["DaysSinceLastEntry"]

    # --- Helper to plot multi-line graphs ---
    def save_multi_plot(column_name, title, ylabel, filename, colour = "blue", color_map=None):
        plt.figure(figsize=(8, 4))
        
        # Check if 'FuelType' exists, otherwise plot normally
        if "FuelType" in data.columns:
            for fuel_type, group in data.groupby("FuelType"):
                # Resample each fuel group individually
                group_daily = group.resample("D").sum()
                # Clean zeros and fill
                group_daily[column_name] = group_daily[column_name].replace(0, float("nan")).ffill().bfill()
                group_daily[column_name].plot(label=str(fuel_type))
            plt.legend()
        else:
            daily = data.resample("D").sum()
            daily[column_name] = daily[column_name].replace(0, float("nan")).bfill()
            daily[column_name].plot(color=colour)

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
    fig_paths["rolling_money_spent"] = save_multi_plot("NormalisedCost", "Daily Cost", "$/day", "daily_cost.png", "orange")
    fig_paths["fuel_economy"] = save_multi_plot("Kilometrage(L/100km)", "Fuel Economy", "L/100KM", "fuel_economy.png", "green")
    fig_paths["AvgCostPerKilometre"] = save_multi_plot("CostPerKilometre", "Cost Per KM", "$/KM", "cost_per_km.png", "blue")
    fig_paths["AvgPetrolCost"] = save_multi_plot("PetrolPrice(PerLitre)", "Petrol Price", "$/Litre", "petrol_price.png", "purple")

    return fig_paths