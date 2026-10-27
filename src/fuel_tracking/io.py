from __future__ import annotations

import warnings
from pathlib import Path
from typing import Iterable

import pandas as pd

REQUIRED_COLUMNS: Iterable[str] = (
    "Date",
    "Distance",
    "PetrolFilled(Litres)",
    "TotalCost",
)

NUMERIC_COLUMNS = ("Distance", "PetrolFilled(Litres)", "TotalCost")


def safe_divide(numerator, denominator):
    """Divide, returning NaN instead of inf/garbage where the denominator is not positive.

    Works on scalars and pandas Series alike.
    """
    if isinstance(denominator, pd.Series):
        return numerator / denominator.where(denominator > 0)
    if pd.isna(denominator) or denominator <= 0:
        return float("nan")
    return numerator / denominator


def add_ratio_columns(df: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    """Add price, fuel economy and cost-per-km derived from Distance, litres and cost."""
    litres = df["PetrolFilled(Litres)"]
    distance = df["Distance"]
    cost = df["TotalCost"]
    df["PetrolPrice(PerLitre)"] = safe_divide(cost, litres)
    df["FuelEconomy(L/100km)"] = safe_divide(litres, distance) * 100
    df["CostPerKilometre"] = safe_divide(cost, distance)
    return df


def load_data(csv_path: str | Path, dayfirst: bool = True, date_format: str | None = None) -> pd.DataFrame:
    """Load the CSV file, parse dates, set index, sort, and add derived columns.

    Expected columns:
      - Date
      - Distance
      - PetrolFilled(Litres)
      - TotalCost
      - PetrolType (optional, used for mode stats and per-fuel charts)

    Rows whose date or numeric values cannot be parsed are dropped with a warning.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV missing required columns: {missing}. "
            "See the 'Data format' section of the README for the expected format."
        )

    # Parse dates; "mixed" parses each value individually without the inference warning
    df["Date"] = pd.to_datetime(
        df["Date"], format=date_format or "mixed", dayfirst=dayfirst, errors="coerce"
    )

    # Coerce numeric columns
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    invalid = df["Date"].isna() | df[list(NUMERIC_COLUMNS)].isna().any(axis=1)
    if invalid.any():
        # +2: one for the header row, one because CSV line numbers start at 1
        lines = ", ".join(str(i + 2) for i in df.index[invalid])
        warnings.warn(
            f"Dropping {int(invalid.sum())} row(s) with unparseable date or numbers (CSV lines: {lines})",
            stacklevel=2,
        )
        df = df[~invalid]

    if df.empty:
        raise ValueError(f"No valid rows found in {csv_path}")

    df = df.set_index("Date").sort_index()

    return add_ratio_columns(df)
