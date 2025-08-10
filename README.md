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

## Install (editable)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Usage

Run against the default `data.csv` and write to `outputs/`:

```bash
fueltrack
```

Specify a CSV and output directory:

```bash
fueltrack path/to/data.csv --out results
```

## Data format

Required columns (see `data.example.csv`):

- `Date` (parseable by pandas)
- `Distance` (km)
- `PetrolFilled(Litres)` (L)
- `TotalCost` ($)
- Optional: `PetrolType`

## Notes

- The CLI mirrors the notebook’s calculations and plots. If you add new analyses in the notebook, consider moving them into `src/fuel_tracking/` and invoking them from the CLI.
- Generated assets are written under `outputs/` by default.