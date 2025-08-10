from __future__ import annotations

import datetime as _dt
from typing import Literal, Optional

import pandas as pd

AggFunc = Literal["sum", "average", "mode"]


def _coerce_dates(df: pd.DataFrame, start_date, end_date):
    start = df.index.min() if start_date is None else pd.to_datetime(start_date, dayfirst=True)
    end = df.index.max() if end_date is None else pd.to_datetime(end_date, dayfirst=True)
    return start, end


def numeric_statistics(
    data: pd.DataFrame,
    start_date: Optional[_dt.datetime] | str | None = None,
    end_date: Optional[_dt.datetime] | str | None = None,
    function: AggFunc = "sum",
    monthly: bool = False,
):
    """Compute aggregated statistics.

    Mirrors notebook behavior but with safer handling.
    """
    function = function.lower()

    start, end = _coerce_dates(data, start_date, end_date)
    tmp = data[(start <= data.index) & (data.index <= end)]

    # Calculate time differences between entries
    tmp = tmp.copy()
    tmp["DaysSinceLast"] = tmp.index.to_series().diff().dt.days.fillna(1)

    if monthly:
        tmp = tmp.groupby(tmp.index.to_period("M"))

    if function == "sum":
        return tmp[["Distance", "PetrolFilled(Litres)", "TotalCost"]].sum()

    if function == "average":
        result = tmp[
            [
                "Distance",
                "PetrolFilled(Litres)",
                "TotalCost",
                "PetrolPrice(PerLitre)",
                "Kilometrage(L/100km)",
                "CostPerKilometre",
            ]
        ].mean()

        if not monthly:
            if len(tmp.index) > 1:
                avg_secs = tmp.index.to_series().diff().dt.total_seconds().mean()
                result["AverageTimeBetweenEntries(seconds)"] = pd.to_timedelta(avg_secs, unit="s")
            else:
                result["AverageTimeBetweenEntries(seconds)"] = pd.NaT
        return result

    if function == "mode":
        if monthly:
            return tmp[["PetrolType"]].agg(lambda group: group.mode())
        return tmp[["PetrolType"]].mode()

    raise ValueError("Invalid function; expected one of: sum, average, mode")
