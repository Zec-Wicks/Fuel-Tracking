# Fuel-Tracking

A small Python tool to analyze fuel usage from a CSV, generate charts, and export a PDF report.

## Repository layout

- `data.csv` — your data input (see `data.example.csv` for schema)
- `fuelAnalysis.ipynb` — original exploratory notebook
- `src/fuel_tracking/` — reusable Python package
  - `io.py` — load and prepare data
  - `stats.py` — compute aggregations and stats
  - `viz.py` — create charts into `outputs/`
  - `report.py` — assemble a PDF report with charts and stats
  - `cli.py` — command-line interface
- `outputs/` — generated charts and reports
- `pyproject.toml` — project metadata and dependencies

## Install

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
```

To run the tests:

```bash
pip install -e ".[test]"
pytest
```

## Usage

Run against the default `data.csv` and write to `outputs/`:

```bash
fueltrack
```

Specify a CSV and output directory:

```bash
fueltrack path/to/data.csv --out results --currency "$"
```

## Data format

Required columns (see `data.example.csv`):

- `Date` (day-first, e.g. `21/12/2024`)
- `Distance` (km driven since the previous fill-up)
- `PetrolFilled(Litres)` (L)
- `TotalCost` ($)
- Optional: `PetrolType` (charts get one line per fuel type)

Rows with an unparseable date or number are skipped with a warning. Fuel economy,
price per litre and cost per km are calculated from totals, so a small top-up counts
for less than a full tank.

## Notes

- The CLI mirrors the notebook’s calculations and plots. If you add new analyses in the notebook, consider moving them into `src/fuel_tracking/` and invoking them from the CLI.
- Generated assets are written under `outputs/` by default.