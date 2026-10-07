import re
from datetime import datetime

D = r"(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})"
NUM = r"([\d,]+(?:\.\d+)?)"
PATTERNS = {
    "consumer_number": r"(?:consumer|account|connection)\s*(?:no|number|#)?[\s.:\-]*([A-Z0-9\-]{6,18})",
    "units": rf"(?:units?\s*consumed|total\s*units?|kwh\s*consumed|net\s*consumption)[^\d]{{0,20}}{NUM}",
    "amount": rf"(?:total\s*(?:bill\s*)?amount|net\s*payable|amount\s*payable|total\s*payable)[^\d]{{0,20}}{NUM}",
    "tariff": r"tariff(?:\s*category)?[\s:\-]*([A-Za-z0-9 \-/]{2,30})",
    "rate": r"(?:energy\s*charge|rate)[^\d]{0,15}(\d+\.\d{1,2})",
    "billing_date": rf"(?:bill\s*date|billing\s*date|date\s*of\s*bill)[\s:\-]*{D}",
    "period": rf"{D}\s*(?:to|-|–)\s*{D}",
}


def _date(s: str):
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _find(key: str, text: str):
    m = re.search(PATTERNS[key], text, re.IGNORECASE)
    return m


def parse_bill(text: str) -> dict:
    out: dict = {k: None for k in
                 ("consumer_number", "billing_date", "period_start", "period_end",
                  "days", "units", "amount", "tariff", "rate")}
    for key in ("consumer_number", "billing_date", "tariff"):
        m = _find(key, text)
        out[key] = m.group(1).strip() if m else None
    for key in ("units", "amount", "rate"):
        m = _find(key, text)
        out[key] = float(m.group(1).replace(",", "")) if m else None
    m = _find("period", text)
    if m:
        a, b = _date(m.group(1)), _date(m.group(2))
        out["period_start"], out["period_end"] = m.group(1), m.group(2)
        if a and b and b > a:
            out["days"] = (b - a).days
    if out["rate"] is None and out["units"] and out["amount"]:
        out["rate"] = round(out["amount"] / out["units"], 2)
    found = sum(out[k] is not None for k in ("units", "amount", "consumer_number", "billing_date"))
    out["confidence"] = round(found / 4, 2)
    return out