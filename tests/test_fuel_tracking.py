from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest

from fuel_tracking import data_visualisations, load_data, numeric_statistics, produce_report
from fuel_tracking.cli import main

EXAMPLE_CSV = Path(__file__).resolve().parent.parent / "data.example.csv"
HEADER = "Date,Distance,PetrolFilled(Litres),TotalCost,PetrolType\n"


def write_csv(tmp_path: Path, rows: str, header: str = HEADER) -> Path:
    path = tmp_path / "data.csv"
    path.write_text(header + rows)
    return path


def test_example_csv_runs_end_to_end(tmp_path):
    assert main([str(EXAMPLE_CSV), "--out", str(tmp_path)]) == 0
    assert (tmp_path / "fuel_consumption_report.pdf").stat().st_size > 0
    assert len(list(tmp_path.glob("*.png"))) == 5


def test_missing_file_is_a_clean_cli_error(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main([str(tmp_path / "nope.csv")])
    assert exc.value.code == 2
    assert "CSV not found" in capsys.readouterr().err


def test_bad_rows_are_dropped_with_warning(tmp_path):
    csv = write_csv(tmp_path, "01/01/2025,400,30,60,E10\nnot-a-date,400,30,60,E10\n05/01/2025,abc,30,60,E10\n")
    with pytest.warns(UserWarning, match="Dropping 2 row"):
        df = load_data(csv)
    assert len(df) == 1


def test_zero_distance_gives_nan_not_inf(tmp_path):
    csv = write_csv(tmp_path, "01/01/2025,0,0,0,E10\n08/01/2025,0,10,20,E10\n15/01/2025,400,30,60,E10\n")
    df = load_data(csv)
    assert not np.isinf(df.select_dtypes("number")).any().any()
    avg = numeric_statistics(df, function="average")
    assert math.isfinite(avg["FuelEconomy(L/100km)"])


def test_average_economy_is_weighted_by_distance(tmp_path):
    # 50 km top-up at 20 L/100km and 600 km tank at 5 L/100km
    csv = write_csv(tmp_path, "01/01/2025,50,10,20,E10\n15/01/2025,600,30,60,E10\n")
    avg = numeric_statistics(load_data(csv), function="average")
    assert avg["FuelEconomy(L/100km)"] == pytest.approx(40 / 650 * 100)
    assert avg["AverageDaysBetweenEntries"] == pytest.approx(14)


def test_same_day_entries_do_not_inflate_charts(tmp_path):
    csv = write_csv(tmp_path, "01/01/2025,400,30,60,E10\n08/01/2025,200,15,30,E10\n08/01/2025,200,15,30,E10\n")
    from fuel_tracking.viz import _daily_metrics

    df = load_data(csv)
    gaps = df.index.normalize().unique().to_series().diff().dt.days
    daily = _daily_metrics(df, gaps)
    assert daily.loc["2025-01-08", "FuelEconomy(L/100km)"] == pytest.approx(7.5)
    assert daily.loc["2025-01-08", "NormalisedDistance"] == pytest.approx(400 / 7)
    # Full chart + report generation must also survive same-day entries
    assert len(data_visualisations(df, tmp_path)) == 5
    produce_report(df, outputs_dir=tmp_path)


def test_mode_without_petrol_type_raises(tmp_path):
    csv = write_csv(
        tmp_path, "01/01/2025,400,30,60\n", header="Date,Distance,PetrolFilled(Litres),TotalCost\n"
    )
    df = load_data(csv)
    with pytest.raises(ValueError, match="PetrolType"):
        numeric_statistics(df, function="mode")
    # Charts still work without the optional column
    assert len(data_visualisations(df, tmp_path)) == 5


def test_monthly_mode_picks_single_value(tmp_path):
    csv = write_csv(tmp_path, "01/01/2025,400,30,60,E10\n10/01/2025,400,30,60,ULP98\n01/02/2025,400,30,60,E10\n")
    result = numeric_statistics(load_data(csv), function="mode", monthly=True)
    assert len(result) == 2
    assert result["PetrolType"].notna().all()
