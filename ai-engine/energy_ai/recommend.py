RULES = [
    ("air compressor", "Fix air leaks and reduce unloaded running hours.", 0.15),
    ("hvac", "Shift HVAC to off-peak hours and widen temperature setpoints.", 0.12),
    ("chiller", "Raise chilled-water setpoint and clean condenser coils.", 0.10),
    ("refrigeration", "Defrost on demand and keep condensers clean.", 0.10),
    ("chilling", "Improve insulation and use night-time pre-cooling.", 0.10),
    ("furnace", "Optimize charging schedule to cut idle holding time.", 0.08),
    ("boiler", "Tune combustion and insulate steam lines.", 0.09),
    ("pump", "Fit a VFD and replace old motors with IE3/IE4 models.", 0.12),
    ("fan", "Fit a VFD and replace old motors with IE3/IE4 models.", 0.12),
    ("mill", "Optimize production scheduling to reduce idle running.", 0.08),
]


def recommendations(rows: list[dict], rate: float, machine_flags: list[dict]) -> list[dict]:
    flagged = {f["machine"] for f in machine_flags}
    out = []
    for r in rows:
        if r["name"] == "Others":
            if r["pct"] > 20:
                s = round(r["units"] * 0.20)
                out.append({"machine": "Others", "text": "Switch lighting to LED and cut standby loads.",
                            "save_units": s, "save_cost": round(s * rate)})
            continue
        if not (r["pct"] >= 15 or r["efficiency"] < 78 or r["name"] in flagged):
            continue
        name = r["name"].lower()
        text, frac = next(((t, f) for k, t, f in RULES if k in name),
                          ("Schedule preventive maintenance and reduce idle time.", 0.05))
        if r["efficiency"] < 80:
            frac *= 1 + (80 - r["efficiency"]) / 100
        s = round(r["units"] * frac)
        out.append({"machine": r["name"], "text": text, "save_units": s,
                    "save_cost": round(s * rate)})
    return sorted(out, key=lambda x: x["save_cost"], reverse=True)