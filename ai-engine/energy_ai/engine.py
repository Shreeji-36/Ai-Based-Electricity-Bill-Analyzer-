from energy_ai.anomaly import check_bill, machine_anomalies
from energy_ai.forecast import forecast_units
from energy_ai.recommend import recommendations


def enrich(result: dict, history_units: list[float], peak_kw: float) -> dict:
    units = result["bill"]["units"]
    rate = result["rate"]
    series = history_units + [units]
    fc = forecast_units(series, months=3)
    m_flags = machine_anomalies(result["rows"])
    recs = recommendations(result["rows"], rate, m_flags)
    return {
        "forecast": {**fc, "amount": [round(u * rate) for u in fc["units"]]},
        "peak_load_kw": round(peak_kw),
        "bill_anomaly": check_bill(history_units, units),
        "machine_anomalies": m_flags,
        "recommendations": recs,
        "total_savings": sum(r["save_cost"] for r in recs),
    }