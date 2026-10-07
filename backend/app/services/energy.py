from app.data.industries import INDUSTRIES


def analyze(industry: str, bill: dict, hours: dict[str, float]) -> dict:
    ind = INDUSTRIES[industry]
    units_total, days = bill["units"], bill["days"]
    rate = bill["amount"] / units_total

    rows = []
    for m in ind["machines"]:
        h = hours.get(m["id"], 0)
        est = m["kw"] * h * days * (m["efficiency"] / 100 + 0.2)
        rows.append({"name": m["name"], "units": est, "efficiency": m["efficiency"]})

    estimated = sum(r["units"] for r in rows)
    if estimated > units_total:  # cap at 95% of the real bill
        scale = units_total * 0.95 / estimated
        for r in rows:
            r["units"] *= scale

    others = max(units_total - sum(r["units"] for r in rows), 0)
    rows.append({"name": "Others", "units": others, "efficiency": 90})

    for r in rows:
        r["cost"] = round(r["units"] * rate)
        r["pct"] = round(r["units"] / units_total * 100, 1)
        r["units"] = round(r["units"])

    machines = [r for r in rows if r["name"] != "Others"]
    by_units = sorted(machines, key=lambda r: r["units"], reverse=True)
    by_eff = sorted(machines, key=lambda r: r["efficiency"], reverse=True)

    next_units = round(units_total * 1.03)  # placeholder, ML forecast in Phase 3
    tips = []
    for r in machines:
        if r["efficiency"] < 78 or r["pct"] > 25:
            save_units = round(r["units"] * 0.12)
            tips.append({
                "text": f"Optimize {r['name']}: cut idle time and schedule preventive maintenance.",
                "save_units": save_units,
                "save_cost": round(save_units * rate),
            })

    return {
        "industry": ind["name"],
        "bill": bill,
        "rate": round(rate, 2),
        "rows": rows,
        "highest": by_units[0]["name"],
        "lowest": by_units[-1]["name"],
        "most_efficient": by_eff[0]["name"],
        "least_efficient": by_eff[-1]["name"],
        "forecast": {"units": next_units, "amount": round(next_units * rate)},
        "tips": tips,
        "total_savings": sum(t["save_cost"] for t in tips),
    }