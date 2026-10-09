"""Machine-specific energy-saving recommendations.

Every machine gets advice that fits what it is (chiller, boiler, pump ...)
and how it is used (how many units, how many hours per day, its share of the bill).
"""

# machine id -> kind -> (advice text, fraction of that machine's energy that can be saved)
# {n} = number of machines, {h} = hours per day, {eff} = efficiency %
CATALOG = {
    "hvac": {
        "clean": ("Clean AHU filters and cooling coils every month. Clogged filters make fans and compressors work harder.", 0.05),
        "control": ("Fit VFDs on AHU fans and widen temperature/humidity set-points in non-critical areas.", 0.12),
        "multi": ("You run {n} HVAC units. Stage them so only the number needed for the current load runs, and rotate the duty units weekly.", 0.08),
    },
    "compressor": {
        "clean": ("Replace intake and oil-separator filters on schedule and hunt for air leaks with an ultrasonic detector.", 0.06),
        "control": ("Lower the discharge pressure to the minimum the process needs (roughly 7% saving per bar) and cut unloaded running.", 0.10),
        "multi": ("You run {n} compressors. Use a sequencer so only one trims the load while the others run fully loaded or stay off.", 0.10),
    },
    "chiller": {
        "clean": ("Clean condenser tubes and cooling-tower fill. Dirty tubes raise condensing temperature and power draw.", 0.05),
        "control": ("Raise the chilled-water set-point where the process allows (often 2-3% saving per degree C) and fit VFDs on pumps and fans.", 0.10),
        "multi": ("You run {n} chillers. Sequence them by load: fewer chillers at higher load is more efficient than all at part load.", 0.10),
    },
    "fbd": {
        "clean": ("Clean or replace inlet/exhaust filters and finger bags so air-flow resistance stays low.", 0.05),
        "control": ("Insulate heaters and ducts and use end-point detection to avoid over-drying batches.", 0.10),
        "multi": ("You run {n} dryers. Batch production so dryers run full loads back to back instead of several half-empty at once.", 0.08),
    },
    "tablet": {
        "clean": ("Clean and lubricate the presses and the dust-extraction filters. Worn tooling and clogged collectors raise motor load.", 0.04),
        "control": ("Put presses in standby during changeovers and cleaning, and fit a VFD on the dust collector.", 0.08),
        "multi": ("You run {n} presses. Plan batches so presses run back to back and idle ones are fully switched off.", 0.08),
    },
    "chilling": {
        "clean": ("Clean evaporator and condenser surfaces and de-scale heat exchangers regularly.", 0.05),
        "control": ("Pre-cool milk with a plate heat exchanger, improve tank insulation and shift chilling to night-time off-peak hours.", 0.10),
        "multi": ("You run {n} chilling units. Run only the capacity the milk intake needs and rotate duty units.", 0.08),
    },
    "pasteurizer": {
        "clean": ("Do CIP cleaning on schedule. Fouled plates cut heat transfer and waste energy.", 0.04),
        "control": ("Keep the regeneration section efficient and avoid running on recirculation when no milk is flowing.", 0.08),
        "multi": ("You run {n} pasteurizers. Run them at full capacity in fewer batches instead of several at part load.", 0.08),
    },
    "homogenizer": {
        "clean": ("Check valves, seals and lubrication. Worn parts raise motor load.", 0.04),
        "control": ("Set homogenizing pressure to the product minimum and switch off during idle periods.", 0.08),
        "multi": ("You run {n} homogenizers. Match the number running to the milk volume and shut the rest down.", 0.07),
    },
    "refcomp": {
        "clean": ("Keep condensers and evaporators clean and defrost on demand. Ice and scale raise compressor load.", 0.05),
        "control": ("Use floating head-pressure control to lower condensing pressure and fit VFD/slide-valve control on screw compressors.", 0.10),
        "multi": ("You run {n} refrigeration compressors. Sequence them so one trims the load and the others run fully loaded.", 0.09),
    },
    "boiler": {
        "clean": ("Clean heat-transfer surfaces, de-scale and tune blowdown. Soot and scale waste fuel and power.", 0.04),
        "control": ("Tune the air-fuel ratio, insulate steam lines and return condensate to the boiler.", 0.09),
        "multi": ("You run {n} boilers. Fire only the boilers the load needs and avoid several at low fire.", 0.08),
    },
    "eaf": {
        "clean": ("Maintain electrodes and water-cooled panels and seal door gaps to cut heat losses.", 0.03),
        "control": ("Optimise the charge mix, slag practice and power-on time, and cut tap-to-tap delays.", 0.08),
        "multi": ("You run {n} arc furnaces. Schedule heats so no furnace is held hot while waiting for the ladle or crane.", 0.07),
    },
    "rolling": {
        "clean": ("Check bearing lubrication and roll alignment to cut friction losses.", 0.03),
        "control": ("Reduce idle running between billets and use VFD drives on mill motors.", 0.08),
        "multi": ("You run {n} mills. Sequence production so mills are not left running empty between orders.", 0.07),
    },
    "induction": {
        "clean": ("Check coil insulation and cooling-water quality and keep the crucible lining in good condition.", 0.03),
        "control": ("Charge clean, dense scrap, avoid long hot holding of molten metal and keep power factor high.", 0.08),
        "multi": ("You run {n} induction furnaces. Melt in fewer, fuller heats instead of many part-filled ones.", 0.07),
    },
    "pump": {
        "clean": ("Clean strainers and check impeller wear and clearances.", 0.04),
        "control": ("Fit a VFD and trim flow to demand instead of throttling valves.", 0.15),
        "multi": ("You run {n} pumps. Run only the number needed for the flow and rotate duty/standby.", 0.10),
    },
    "evap": {
        "clean": ("Clean evaporator coils and fan blades and keep defrost on demand.", 0.04),
        "control": ("Fit EC fans or VFDs and slow the fans once the room is at temperature.", 0.15),
        "multi": ("You run {n} evaporator fans. Stage them by room load instead of running all at full speed.", 0.10),
    },
    "condenser": {
        "clean": ("Wash condenser coils and clear the fins and air path. Dirty condensers raise compressor power.", 0.05),
        "control": ("Use variable-speed condenser fans with floating head-pressure control.", 0.10),
        "multi": ("You run {n} condenser units. Stage the fans by heat load rather than running them all.", 0.08),
    },
    "towerpump": {
        "clean": ("Clean the tower basin and strainers so the pump does not fight blockages.", 0.04),
        "control": ("Fit a VFD and trim flow to the load, and match tower fans to the wet-bulb temperature.", 0.12),
        "multi": ("You run {n} tower pumps. Run only the number needed and rotate duty/standby.", 0.09),
    },
}

GENERIC = {
    "clean": ("Clean and service this machine on a fixed schedule. Dirt and wear raise power draw.", 0.04),
    "control": ("Fit a VFD or better controls and avoid running it unloaded.", 0.08),
    "multi": ("You run {n} units. Run only as many as the load needs and rotate duty.", 0.07),
}
HIGH = ("This runs about {h:g} h/day, almost non-stop. Add automatic shut-off or load-based control so it does not run idle between loads.", 0.07)
UPGRADE = ("Efficiency is only {eff}%. Plan a retrofit or replacement (IE3/IE4 motors, newer unit) and compare the payback.", 0.10)


def build_recommendations(rows: list[dict], rate: float, machine_flags: list[dict] | None = None,
                          limit: int = 12) -> list[dict]:
    flagged = {f["machine"] for f in (machine_flags or [])}
    out: list[dict] = []

    for r in rows:
        if r["name"] == "Others":
            if r["pct"] > 20:
                s = round(r["units"] * 0.20)
                out.append({"machine": "Others", "kind": "lighting",
                            "text": "Switch lighting to LED, switch off standby loads and consider sub-metering the 'Others' load to find what it is.",
                            "save_units": s, "save_cost": round(s * rate)})
            continue
        if r["units"] <= 0:
            continue

        h = r.get("hours") or 0
        n = r.get("qty") or 1
        eff = r["efficiency"]
        relevant = r["pct"] >= 3 or eff < 78 or r["name"] in flagged
        if not relevant:
            continue

        cat = CATALOG.get(r.get("id"), GENERIC)
        picks = [("cleaning", cat["clean"])]
        if n >= 3:
            picks.append(("multiple units", cat["multi"]))
        elif h >= 16:
            picks.append(("long running hours", HIGH))
        if r["pct"] >= 10 or eff < 78 or r["name"] in flagged:
            picks.append(("controls", cat["control"]))
        if eff < 75:
            picks.append(("upgrade", UPGRADE))

        for kind, (text, frac) in picks[:3]:
            if eff < 80:
                frac *= 1 + (80 - eff) / 100
            s = round(r["units"] * frac)
            out.append({"machine": r["name"], "kind": kind,
                        "text": text.format(n=n, h=h, eff=eff),
                        "save_units": s, "save_cost": round(s * rate)})

    out.sort(key=lambda x: x["save_cost"], reverse=True)
    return out[:limit]