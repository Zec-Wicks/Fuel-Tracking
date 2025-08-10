from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

REQUIRED_COLUMNS: Iterable[str] = (
    "Date",
    "Distance",
    "PetrolFilled(Litres)",
    "TotalCost",
)


def load_data(csv_path: str | Path, dayfirst: bool = True, date_format: str | None = None) -> pd.DataFrame:
    """Load the CSV file, parse dates, set index, sort, and add derived columns.

    Expected columns:
      - Date
      - Distance
      - PetrolFilled(Litres)
      - TotalCost
      - PetrolType (optional, used for mode stats)
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV missing required columns: {missing}. "
            "See data.example.csv for the expected format."
        )

    # Parse and index by Date
    if date_format:
        df["Date"] = pd.to_datetime(df["Date"], format=date_format, errors="coerce")
    else:
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=dayfirst, errors="coerce")
    df = df.set_index("Date").sort_index().copy()

    # Coerce numeric columns
    for col in ("Distance", "PetrolFilled(Litres)", "TotalCost"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived columns
    df["PetrolPrice(PerLitre)"] = df["TotalCost"] / df["PetrolFilled(Litres)"]
    df["Kilometrage(L/100km)"] = (df["PetrolFilled(Litres)"] / df["Distance"]) * 100
    df["CostPerKilometre"] = df["TotalCost"] / df["Distance"]

    return df
