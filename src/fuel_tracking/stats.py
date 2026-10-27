from __future__ import annotations

import datetime as _dt
from typing import Literal, Tuple, Union

import pandas as pd

from .io import NUMERIC_COLUMNS, add_ratio_columns

AggFunc = Literal["sum", "average", "mode"]
DateLike = Union[_dt.datetime, pd.Timestamp, str, None]


def _coerce_dates(df: pd.DataFrame, start_date: DateLike, end_date: DateLike) -> Tuple[pd.Timestamp, pd.Timestamp]:
    start = df.index.min() if start_date is None else pd.to_datetime(start_date, dayfirst=True)
    end = df.index.max() if end_date is None else pd.to_datetime(end_date, dayfirst=True)
    return start, end


def _most_common(values: pd.Series):
    modes = values.mode()
    return modes.iloc[0] if not modes.empty else None


def numeric_statistics(
    data: pd.DataFrame,
    start_date: DateLike = None,
    end_date: DateLike = None,
    function: AggFunc = "sum",
    monthly: bool = False,
):
    """Compute aggregated statistics over [start_date, end_date].

    - "sum": totals of distance, litres and cost.
    - "average": mean distance, litres and cost per fill-up, plus price, fuel economy
      and cost-per-km computed from the totals (so long tanks weigh more than top-ups).
      Non-monthly results also include AverageDaysBetweenEntries.
    - "mode": most common PetrolType.
    """
    function = function.lower()

    start, end = _coerce_dates(data, start_date, end_date)
    tmp = data[(start <= data.index) & (data.index <= end)]
    grouped = tmp.groupby(tmp.index.to_period("M")) if monthly else None

    if function == "sum":
        source = grouped if monthly else tmp
        return source[list(NUMERIC_COLUMNS)].sum()

    if function == "average":
        if monthly:
            result = grouped[list(NUMERIC_COLUMNS)].mean()
            totals = grouped[list(NUMERIC_COLUMNS)].sum()
        else:
            result = tmp[list(NUMERIC_COLUMNS)].mean()
            totals = tmp[list(NUMERIC_COLUMNS)].sum()

        ratios = add_ratio_columns(totals.copy())
        for col in ("PetrolPrice(PerLitre)", "FuelEconomy(L/100km)", "CostPerKilometre"):
            result[col] = ratios[col]

        if not monthly:
            gaps = tmp.index.to_series().diff().dt.total_seconds() / 86400
            result["AverageDaysBetweenEntries"] = gaps.mean() if len(tmp.index) > 1 else float("nan")
        return result

    if function == "mode":
        if "PetrolType" not in tmp.columns:
            raise ValueError("Mode statistics require a 'PetrolType' column")
        if monthly:
            return grouped["PetrolType"].agg(_most_common).to_frame()
        return tmp[["PetrolType"]].mode()

    raise ValueError("Invalid function; expected one of: sum, average, mode")
