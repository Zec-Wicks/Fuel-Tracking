from __future__ import annotations

import datetime as dt
from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .viz import data_visualisations
from .stats import numeric_statistics

def produce_report(data: pd.DataFrame, report_title: str = "Fuel Consumption Report", outputs_dir: str | Path = "outputs") -> str:
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = outputs_dir / "fuel_consumption_report.pdf"
    c = canvas.Canvas(str(pdf_filename), pagesize=A4)
    width, height = A4
    y = height - 50
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
            y = height - 50
        c.setFont(font, size)
        c.drawString(50, y, text)
        y -= line_spacing

    # --- Section: Past 28 Days ---
    past_end = dt.datetime.now()
    past_start = past_end - pd.to_timedelta("28day")
    
    current_totals = numeric_statistics(data, past_start, past_end, "sum", False)
    current_avg = numeric_statistics(data, past_start, past_end, "average", False)

    draw_line("Past 28 Days Fuel Consumption Report", "Helvetica-Bold", 18)
    draw_line(f"Total Cost: ${safe_round(current_totals.get('TotalCost', 0))}")
    draw_line(f"Total Distance: {safe_round(current_totals.get('Distance', 0))} KM")
    draw_line(f"Total Petrol Consumption: {safe_round(current_totals.get('PetrolFilled(Litres)', 0))} L")
    draw_line(f"Fuel Economy: {safe_round(current_avg.get('Kilometrage(L/100km)', 0))} L/100 KM")
    draw_line(f"Cost Per Kilometre: ${safe_round(current_avg.get('CostPerKilometre', 0))}")
    draw_line("")

    # --- Section: Current Year ---
    year_now = dt.datetime.now().year
    year_start = dt.datetime(year_now, 1, 1)
    year_end = dt.datetime(year_now, 12, 31, 23, 59, 59)

    year_totals = numeric_statistics(data, year_start, year_end, "sum", False)
    year_avg = numeric_statistics(data, year_start, year_end, "average", False)

    draw_line(f"{year_now} Fuel Consumption Report", "Helvetica-Bold", 18)
    draw_line(f"Total Cost: ${safe_round(year_totals.get('TotalCost', 0))}")
    draw_line(f"Total Distance: {safe_round(year_totals.get('Distance', 0))} KM")
    draw_line(f"Total Petrol Consumption: {safe_round(year_totals.get('PetrolFilled(Litres)', 0))} L")
    draw_line(f"Fuel Economy: {safe_round(year_avg.get('Kilometrage(L/100km)', 0))} L/100 KM")
    draw_line(f"Cost Per Kilometre: ${safe_round(year_avg.get('CostPerKilometre', 0))}")
    draw_line("")

    # --- Section: All-Time ---
    all_time_totals = numeric_statistics(data, function="sum")
    all_time_avg = numeric_statistics(data, function="average")

    draw_line("All-Time Fuel Consumption Report", "Helvetica-Bold", 18)
    draw_line(f"Total Cost: ${safe_round(all_time_totals.get('TotalCost', 0))}")
    draw_line(f"Total Distance: {safe_round(all_time_totals.get('Distance', 0))} KM")
    draw_line(f"Total Petrol Consumption: {safe_round(all_time_totals.get('PetrolFilled(Litres)', 0))} L")
    draw_line(f"Fuel Economy: {safe_round(all_time_avg.get('Kilometrage(L/100km)', 0))} L/100 KM")
    draw_line(f"Cost Per Kilometre: ${safe_round(all_time_avg.get('CostPerKilometre', 0))}")

    # --- Section: Visualizations ---
    c.showPage()  # Move to a new page for charts
    y = height - 50
    
    fig_paths = data_visualisations(data, outputs_dir=outputs_dir)

    for fig_path in fig_paths.values():
        path_obj = Path(fig_path)
        if path_obj.exists() and path_obj.is_file():
            # Check if there is enough room for the image (200px height + 50px margin)
            if y < 250:
                c.showPage()
                y = height - 50
            
            # Draw image (width 450 to fill page better, height 200)
            c.drawImage(str(path_obj), 50, y - 200, width=450, height=200)
            y -= 250 # Move down for the next chart

    c.save()
    return str(pdf_filename)