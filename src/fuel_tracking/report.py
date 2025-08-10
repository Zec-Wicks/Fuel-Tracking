from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .viz import data_visualisations



def produce_report(data, report_title: str = "Fuel Consumption Report", outputs_dir: str | Path = "outputs") -> str:
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = outputs_dir / "fuel_consumption_report.pdf"
    c = canvas.Canvas(str(pdf_filename), pagesize=A4)
    width, height = A4
    y = height - 50
    line_spacing = 20

    def draw_line(text: str):
        nonlocal y
        if y < 100:
            c.showPage()
            y = height - 50
        c.drawString(50, y, text)
        y -= line_spacing

    c.setFont("Helvetica-Bold", 18)
    draw_line("Past 28 Days Fuel Consumption Report")

    from .stats import numeric_statistics

    past_end = dt.datetime.now()
    past_start = past_end - pd.to_timedelta("28day")

    current_totals = numeric_statistics(data, past_start, past_end, "sum", False)
    current_avg = numeric_statistics(data, past_start, past_end, "average", False)

    c.setFont("Helvetica", 12)
    draw_line(f"Total Cost: ${current_totals['TotalCost']:.2f}")
    draw_line(f"Total Distance: {current_totals['Distance']:.2f} KM")
    draw_line(f"Total Petrol Consumption: {current_totals['PetrolFilled(Litres)']:.2f} L")
    draw_line(f"Fuel Economy: {round(current_avg['Kilometrage(L/100km)'], 2)}L / 100 KM")
    draw_line(f"Cost Per Kilometre: ${round(current_avg['CostPerKilometre'], 2)}")
    draw_line("")

    c.setFont("Helvetica-Bold", 18)
    draw_line(f"{dt.datetime.now().year} Fuel Consumption Report")

    year_start = dt.datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0)
    year_end = dt.datetime.now().replace(month=12, day=31, hour=23, minute=59, second=59)

    year_totals = numeric_statistics(data, year_start, year_end, "sum", False)
    year_avg = numeric_statistics(data, year_start, year_end, "average", False)

    c.setFont("Helvetica", 12)
    draw_line(f"Total Cost: ${year_totals['TotalCost']:.2f}")
    draw_line(f"Total Distance: {year_totals['Distance']:.2f} KM")
    draw_line(f"Total Petrol Consumption: {year_totals['PetrolFilled(Litres)']:.2f} L")
    draw_line(f"Fuel Economy: {round(year_avg['Kilometrage(L/100km)'], 2)}L / 100 KM")
    draw_line(f"Cost Per Kilometre: ${round(year_avg['CostPerKilometre'], 2)}")
    draw_line("")

    from .io import load_data  # noqa: F401 (kept for future use/reference)

    # All-time
    all_time_totals = numeric_statistics(data, function="sum")
    all_time_avg = numeric_statistics(data, function="average")

    c.setFont("Helvetica-Bold", 18)
    draw_line("All-Time Fuel Consumption Report")

    c.setFont("Helvetica", 12)
    draw_line(f"Total Cost: ${all_time_totals['TotalCost']:.2f}")
    draw_line(f"Total Distance: {all_time_totals['Distance']:.2f} KM")
    draw_line(f"Total Petrol Consumption: {all_time_totals['PetrolFilled(Litres)']:.2f} L")
    draw_line(f"Fuel Economy: {round(all_time_avg['Kilometrage(L/100km)'], 2)}L / 100 KM")
    draw_line(f"Cost Per Kilometre: ${round(all_time_avg['CostPerKilometre'], 2)}")

    c.showPage()
    y = height - 100

    fig_paths = data_visualisations(data, outputs_dir=outputs_dir)

    for fig_path in fig_paths.values():
        if Path(fig_path).exists():
            if y < 200:
                c.showPage()
                y = height - 50
            c.drawImage(str(fig_path), 50, y - 150, width=400, height=200)
            y -= 230

    c.save()
    return str(pdf_filename)
