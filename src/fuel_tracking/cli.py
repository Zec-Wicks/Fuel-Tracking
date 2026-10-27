from __future__ import annotations

import argparse
from pathlib import Path

from .io import load_data
from .report import produce_report


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fueltrack",
        description="Analyse fuel CSV data, generate charts and a PDF report.",
    )
    p.add_argument("csv", nargs="?", default="data.csv", help="Path to CSV file")
    p.add_argument("--out", default="outputs", help="Output directory for assets and report")
    p.add_argument("--currency", default="$", help="Currency symbol used in the report")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        df = load_data(args.csv)
    except (FileNotFoundError, ValueError) as e:
        parser.error(str(e))

    outputs_dir = Path(args.out)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    # Also generates the charts into outputs_dir
    pdf = produce_report(df, outputs_dir=outputs_dir, currency=args.currency)
    print(f"Report saved to {pdf}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
