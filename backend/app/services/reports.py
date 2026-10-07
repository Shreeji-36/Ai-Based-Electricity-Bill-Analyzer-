import csv
import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer


def to_csv(r: dict) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Machine", "Units (kWh)", "Cost (INR)", "Share (%)", "Efficiency (%)"])
    for x in r["rows"]:
        w.writerow([x["name"], x["units"], x["cost"], x["pct"], x["efficiency"]])
    return buf.getvalue().encode()


def to_xlsx(r: dict) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Machine Analysis"
    ws.append(["Machine", "Units (kWh)", "Cost (INR)", "Share (%)", "Efficiency (%)"])
    for x in r["rows"]:
        ws.append([x["name"], x["units"], x["cost"], x["pct"], x["efficiency"]])
    rec = wb.create_sheet("Recommendations")
    rec.append(["Recommendation", "Units Saved", "Cost Saved (INR)"])
    for t in r["tips"]:
        rec.append([t["text"], t["save_units"], t["save_cost"]])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def to_pdf(r: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    s = getSampleStyleSheet()
    b = r["bill"]
    items = [
        Paragraph(f"Energy Report - {r['industry']} Industry", s["Title"]),
        Paragraph(f"Units: {b['units']} | Amount: INR {b['amount']} | Rate: {r['rate']}/unit", s["Normal"]),
        Spacer(1, 12),
        Paragraph("Machine-wise Analysis", s["Heading2"]),
        Table([["Machine", "Units", "Cost", "Share %"]] +
              [[x["name"], x["units"], x["cost"], x["pct"]] for x in r["rows"]]),
        Spacer(1, 12),
        Paragraph(f"Forecast next month: {r['forecast']['units']} units / INR {r['forecast']['amount']}", s["Normal"]),
        Paragraph("Recommendations", s["Heading2"]),
    ]
    items += [Paragraph(f"- {t['text']} (save INR {t['save_cost']})", s["Normal"]) for t in r["tips"]]
    items.append(Paragraph(f"Total estimated savings: INR {r['total_savings']}", s["Heading3"]))
    doc.build(items)
    return buf.getvalue()