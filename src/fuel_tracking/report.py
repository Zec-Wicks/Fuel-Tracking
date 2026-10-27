from __future__ import annotations

import datetime as dt
from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .viz import data_visualisations
from .stats import numeric_statistics

CHART_WIDTH = 450
CHART_HEIGHT = 225  # matches the 2:1 aspect ratio of the generated figures
CHART_GAP = 25
MARGIN = 50


def produce_report(
    data: pd.DataFrame,
    report_title: str = "Fuel Consumption Report",
    outputs_dir: str | Path = "outputs",
    currency: str = "$",
) -> str:
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = outputs_dir / "fuel_consumption_report.pdf"
    c = canvas.Canvas(str(pdf_filename), pagesize=A4)
    c.setTitle(report_title)
    width, height = A4
    y = height - MARGIN
    line_spacing = 20

    def safe_round(value, decimals=2) -> str:
        """Helper to handle NaT/NaN values without crashing the report."""
        try:
            if pd.isna(value):
                return "N/A"
            return f"{float(value):.{decimals}f}"
        except (TypeError, ValueError):
            return "N/A"

    def draw_line(text: str, font="Helvetica", size=12):
        nonlocal y
        if y < 100:
            c.showPage()
            y = height - MARGIN
        c.setFont(font, size)
        c.drawString(MARGIN, y, text)
        y -= line_spacing

    def draw_section(title: str, start=None, end=None):
        totals = numeric_statistics(data, start, end, "sum", False)
        avg = numeric_statistics(data, start, end, "average", False)

        draw_line(title, "Helvetica-Bold", 18)
        draw_line(f"Total Cost: {currency}{safe_round(totals.get('TotalCost'))}")
        draw_line(f"Total Distance: {safe_round(totals.get('Distance'))} KM")
        draw_line(f"Total Petrol Consumption: {safe_round(totals.get('PetrolFilled(Litres)'))} L")
        draw_line(f"Fuel Economy: {safe_round(avg.get('FuelEconomy(L/100km)'))} L/100 KM")
        draw_line(f"Cost Per Kilometre: {currency}{safe_round(avg.get('CostPerKilometre'))}")
        draw_line("")

    now = dt.datetime.now()
    draw_section("Past 28 Days Fuel Consumption Report", now - pd.to_timedelta("28day"), now)
    draw_section(
        f"{now.year} Fuel Consumption Report",
        dt.datetime(now.year, 1, 1),
        dt.datetime(now.year, 12, 31, 23, 59, 59),
    )
    draw_section("All-Time Fuel Consumption Report")

    # --- Section: Visualizations ---
    c.showPage()  # Move to a new page for charts
    y = height - MARGIN

    fig_paths = data_visualisations(data, outputs_dir=outputs_dir)

    for fig_path in fig_paths.values():
        path_obj = Path(fig_path)
        if path_obj.exists() and path_obj.is_file():
            # Start a new page if the chart would run into the bottom margin
            if y - CHART_HEIGHT < MARGIN:
                c.showPage()
                y = height - MARGIN

            c.drawImage(
                str(path_obj), MARGIN, y - CHART_HEIGHT,
                width=CHART_WIDTH, height=CHART_HEIGHT, preserveAspectRatio=True,
            )
            y -= CHART_HEIGHT + CHART_GAP

    c.save()
    return str(pdf_filename)
