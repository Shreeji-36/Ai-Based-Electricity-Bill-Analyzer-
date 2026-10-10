"""Turns raw OCR text of an electricity bill into structured fields.

Works line by line: find a label (e.g. "Units Consumed"), then read the first
number that follows it on the same line (or on the next line for table layouts).
"""
import re
from datetime import datetime, timedelta

NUM = r"(?:rs\.?|inr|₹)?\s*(\d[\d,]*(?:\.\d+)?)"
MON = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
DATE = rf"(\d{{1,2}}[/\-. ](?:\d{{1,2}}|{MON})[/\-. ]\d{{2,4}})"

UNIT_LABELS = [
    r"units?\s*consumed", r"billed\s*units?", r"total\s*units?", r"net\s*units?",
    r"energy\s*consumed", r"(?:total\s*)?(?:energy\s*)?consumption", r"kwh\s*consumed",
    r"net\s*consumption",
]
AMOUNT_LABELS = [  # best label first
    r"total\s*(?:current\s*)?bill(?:\s*amount)?", r"net\s*bill\s*amount", r"current\s*bill",
    r"total\s*amount", r"grand\s*total",
    r"net\s*(?:amount\s*)?payable", r"amount\s*payable", r"total\s*payable", r"amount\s*due",
]
CONSUMER_LABELS = [
    r"consumer\s*(?:no|number|num|#)", r"con(?:sumer)?\.?\s*no", r"service\s*(?:connection\s*)?(?:no|number)",
    r"connection\s*(?:no|number|id)", r"account\s*(?:no|number)", r"k\.?\s*no",
]
BILLDATE_LABELS = [r"bill\s*date", r"billing\s*date", r"date\s*of\s*(?:bill|issue)", r"(?:bill\s*)?issue\s*date"]

DATE_FORMATS = ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%d %m %Y", "%d/%m/%y", "%d-%m-%y", "%d.%m.%y",
                "%d-%b-%Y", "%d %b %Y", "%d/%b/%Y", "%d.%b.%Y", "%d-%B-%Y", "%d %B %Y",
                "%d-%b-%y", "%d %b %y")


def _date(s: str):
    s = re.sub(r"\s+", " ", s.strip().replace("Sept", "Sep").replace("sept", "sep"))
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s.title() if re.search(r"[a-z]", s, re.I) else s, fmt)
        except ValueError:
            continue
    return None


def _to_float(s: str):
    # OCR often reads the decimal point as a comma: "3,81,900,00" -> 381900.00
    # (in Indian grouping the last group before the decimals always has 3 digits)
    if re.fullmatch(r"\d[\d,]*,\d{2}", s) and s.count(",") >= 2:
        s = s[: s.rfind(",")] + "." + s[s.rfind(",") + 1:]
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return None


def _lines(text: str) -> list[str]:
    text = text.replace("₹", " Rs ").replace("|", " ")
    return [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.splitlines() if ln.strip()]


def _number_after(lines: list[str], i: int, m: re.Match):
    """First number after the label match on line i, else first number on the next line."""
    rest = lines[i][m.end():]
    n = re.search(NUM, rest, re.I)
    if n:
        return _to_float(n.group(1)), lines[i][m.start(): m.end() + n.end()]
    if i + 1 < len(lines):
        n = re.search(NUM, lines[i + 1], re.I)
        if n and re.match(r"^[^a-z]*$", lines[i + 1][:n.start()], re.I):
            return _to_float(n.group(1)), lines[i + 1]
    return None, ""


def _find_number(lines, labels, lo, hi):
    """Returns list of (priority, value, matched_segment, full_line)."""
    found = []
    for pr, lab in enumerate(labels):
        pat = re.compile(lab, re.I)
        for i, ln in enumerate(lines):
            for m in pat.finditer(ln):
                v, seg = _number_after(lines, i, m)
                if v is not None and lo <= v <= hi:
                    found.append((pr, v, seg, ln))
    return found


def _unit_type(seg: str, line: str) -> str:
    s = seg.lower()
    if "kvah" in s:
        return "kVAh"
    if "kwh" in s or "kw h" in s:
        return "kWh"
    l = line.lower()
    return "kVAh" if ("kvah" in l and "kwh" not in l) else "kWh"


def _pick_units(lines):
    cands = _find_number(lines, UNIT_LABELS, 10, 10_000_000)
    if not cands:
        # fallback: any "<number> kWh" in the text
        for ln in lines:
            m = re.search(rf"{NUM}\s*kwh", ln, re.I)
            if m and 10 <= (_to_float(m.group(1)) or 0) <= 10_000_000:
                cands.append((9, _to_float(m.group(1)), "kwh", ln))
    if not cands:
        return None, None
    cands = [(p, v, _unit_type(seg, ln)) for p, v, seg, ln in cands]
    kwh = [c for c in cands if c[2] == "kWh"]
    best = min(kwh or cands, key=lambda c: c[0])
    return best[1], best[2]


def _pick_amount(lines):
    cands = _find_number(lines, AMOUNT_LABELS, 100, 1_000_000_000)
    if not cands:
        return None
    # label priority first; among equal priority, the largest value (the grand figure)
    best_pr = min(c[0] for c in cands)
    return max(c[1] for c in cands if c[0] == best_pr)


def _pick_token(lines, labels, token, need_digit=True):
    for lab in labels:
        pat = re.compile(rf"{lab}[\s.:,;#\-]*{token}", re.I)
        for ln in lines:
            m = pat.search(ln)
            if m:
                val = m.group(m.lastindex).strip(" -/.:").upper()
                if not need_digit or any(c.isdigit() for c in val):
                    return val
    return None


def _pick_date(lines, labels):
    for lab in labels:
        pat = re.compile(rf"{lab}[\s.:,;\-]*{DATE}", re.I)
        for ln in lines:
            m = pat.search(ln)
            if m:
                return m.group(m.lastindex).strip()
    return None


def _pick_period(text: str):
    t = " ".join(_lines(text))
    patterns = [
        rf"previous\s*reading[^\d]{{0,20}}{DATE}.{{0,60}}?current\s*reading[^\d]{{0,20}}{DATE}",
        rf"previous\s*reading\s*date[\s.:\-]*{DATE}.{{0,60}}?current\s*reading\s*date[\s.:\-]*{DATE}",
        rf"(?:billing|bill)?\s*period[\s.:\-]*(?:from\s*)?{DATE}\s*(?:to|-|–|till)\s*{DATE}",
        rf"from\s*{DATE}\s*(?:to|-|–|till)\s*{DATE}",
        rf"{DATE}\s*(?:to|–|till)\s*{DATE}",
        rf"{DATE}\s+-\s+{DATE}",
    ]
    for p in patterns:
        for m in re.finditer(p, t, re.I):
            a, b = _date(m.group(1)), _date(m.group(2))
            if a and b and 0 < (b - a).days <= 62:
                d = (b - a).days
                if a.day == 1 and (b + timedelta(days=1)).day == 1:  # e.g. 01/08 - 31/08 = 31 days
                    d += 1
                return m.group(1), m.group(2), d
    return None, None, None


def _pick_tariff(lines):
    for ln in lines:
        m = re.search(r"tariff(?:\s*(?:category|code|type|name))?[\s:\-]*([A-Za-z0-9][A-Za-z0-9 \-/.]{1,40})", ln, re.I)
        if m:
            val = re.split(r"\s{2,}|\b(?:contract|demand|bill|due|date|consumer|units|kva|kw|load|period)\b",
                           m.group(1), flags=re.I)[0].strip(" -:.")
            if val:
                return val
    return None


FIELDS = ("consumer_number", "billing_date", "period_start", "period_end", "days",
          "units", "units_unit", "amount", "tariff")


def finalize(out: dict) -> dict:
    """Adds rate, warnings and confidence to a dict of raw fields."""
    out["rate"] = None
    warnings: list[str] = []
    units, amount = out.get("units"), out.get("amount")
    rate_bad = False
    if units and amount:
        out["rate"] = round(amount / units, 2)
        if not 2 <= out["rate"] <= 25:
            rate_bad = True
            warnings.append(f"The bill works out to Rs {out['rate']}/unit, which looks unusual. "
                            "Please double-check units and amount.")
    if out.get("units_unit") == "kVAh":
        warnings.append("Units were read in kVAh (not kWh). Check which one you want to use.")
    weights = {"units": .35, "amount": .35, "days": .10, "billing_date": .08,
               "consumer_number": .07, "tariff": .05}
    conf = sum(w for k, w in weights.items() if out.get(k) is not None) - (0.2 if rate_bad else 0)
    out["confidence"] = round(max(conf, 0), 2)
    out["warnings"] = warnings
    return out


def parse_fields(text: str) -> dict:
    lines = _lines(text)
    units, unit_type = _pick_units(lines)
    ps, pe, days = _pick_period(text)
    return {
        "consumer_number": _pick_token(lines, CONSUMER_LABELS, r"([A-Z0-9][A-Z0-9/\-]{4,19})"),
        "billing_date": _pick_date(lines, BILLDATE_LABELS),
        "period_start": ps, "period_end": pe, "days": days,
        "units": units, "units_unit": unit_type, "amount": _pick_amount(lines),
        "tariff": _pick_tariff(lines),
    }


def parse_bill(text: str) -> dict:
    return finalize(parse_fields(text))