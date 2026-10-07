import numpy as np
from sklearn.ensemble import IsolationForest

# Typical share of total bill (%). Placeholder values: calibrate with real client data.
BENCHMARK_SHARE = {
    "HVAC System": 25, "Air Compressor": 15, "Chiller Plant": 25, "Fluid Bed Dryer": 10,
    "Tablet Compression Machine": 8, "Milk Chilling Plant": 25, "Pasteurizer": 12,
    "Homogenizer": 10, "Refrigeration Compressor": 35, "Boiler": 15,
    "Electric Arc Furnace": 45, "Rolling Mill": 20, "Induction Furnace": 25,
    "Cooling Water Pump": 6, "Evaporator Fan": 10, "Condenser Unit": 12,
    "Cooling Tower Pump": 6,
}


def check_bill(history: list[float], current: float) -> dict:
    if len(history) < 4:
        return {"is_anomaly": False, "score": 0.0, "method": "insufficient-history",
                "message": "Add more monthly bills to enable anomaly detection."}
    h = np.array(history, dtype=float)
    med = float(np.median(h))
    mad = float(np.median(np.abs(h - med))) or max(med * 0.05, 1.0)
    z = 0.6745 * (current - med) / mad
    flagged, method = abs(z) > 3.5, "robust-zscore"
    if len(h) >= 8:
        iso = IsolationForest(contamination=0.1, random_state=42).fit(h.reshape(-1, 1))
        flagged = flagged or bool(iso.predict([[current]])[0] == -1)
        method = "isolation-forest+zscore"
    direction = "higher" if current > med else "lower"
    msg = (f"Consumption is unusually {direction} than your typical {med:,.0f} units."
           if flagged else "Consumption is within the normal range.")
    return {"is_anomaly": flagged, "score": round(z, 2), "method": method, "message": msg}


def machine_anomalies(rows: list[dict]) -> list[dict]:
    flags = []
    for r in rows:
        expected = BENCHMARK_SHARE.get(r["name"])
        if expected and r["pct"] > expected * 1.5 and r["pct"] - expected > 8:
            flags.append({"machine": r["name"], "share": r["pct"], "expected": expected,
                          "message": f"{r['name']} uses {r['pct']}% of the bill vs ~{expected}% typical."})
    return flags