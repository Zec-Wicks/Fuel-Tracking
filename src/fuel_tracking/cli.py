from __future__ import annotations

import argparse
from pathlib import Path

from .io import load_data
from .report import produce_report
from .viz import data_visualisations


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fueltrack",
        description="Analyse fuel CSV data, generate charts and a PDF report.",
    )
    p.add_argument("csv", nargs="?", default="data.csv", help="Path to CSV file")
    p.add_argument("--out", default="outputs", help="Output directory for assets and report")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    df = load_data(args.csv)

    outputs_dir = Path(args.out)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Charts
    data_visualisations(df, outputs_dir)

    pdf = produce_report(df, outputs_dir=outputs_dir)
    print(f"Report saved to {pdf}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
