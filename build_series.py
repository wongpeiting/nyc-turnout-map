# build_series.py
# Join ED-level turnout for the 8 post-redistricting elections (2022-2024) onto the
# current district geometry, by ElectDist. Each feature gets per-election turnout/
# voted/registered values. Also computes per-election quintile color breaks so the
# choropleth can rescale to each election (primaries run far lower than generals).
#
# Writes:
#   turnout-series.geojson  -- geometry + per-election properties (t/v/r + key)
#   series-meta.json        -- ordered election list with labels, dates, breaks
#
# 2017 is deliberately excluded: it predates the 2022 redistricting, so the ED codes
# line up but the boundaries don't -- joining it would be a false join.
import csv
import json
import sys

CSV_PATH = "Historical_Voter_Turnout_20260626.csv"
GEOJSON_IN = "election-results.geojson"
GEOJSON_OUT = "turnout-series.geojson"
META_OUT = "series-meta.json"

# The 8 elections that share the current district geometry, with short property keys.
TARGETS = {
    "2022 Federal Primary":       "22FP",
    "2022 State Primary":         "22SP",
    "2022 General":               "22G",
    "2023 City Primary":          "23CP",
    "2023 General":               "23G",
    "2024 Presidential Primary":  "24PP",
    "2024 State Primary":         "24SP",
    "2024 General Election":      "24G",
}


def parse_electdist(geo_unit):
    """'23,001' -> 23001 ; None if it doesn't look like AD,ED or is a placeholder."""
    parts = geo_unit.split(",")
    if len(parts) != 2:
        return None
    try:
        int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if int(parts[1]) == 0:
        return None
    return int(f"{int(parts[0])}{parts[1].zfill(3)}")


def quintile_breaks(vals):
    """4 interior breakpoints (20/40/60/80th pct) splitting vals into 5 bins."""
    vals = sorted(vals)
    n = len(vals)

    def pct(p):
        if n == 1:
            return vals[0]
        idx = p * (n - 1)
        lo = int(idx)
        hi = min(lo + 1, n - 1)
        return vals[lo] + (vals[hi] - vals[lo]) * (idx - lo)

    return [round(pct(q), 4) for q in (0.2, 0.4, 0.6, 0.8)]


def main():
    # Per-election {ed -> {t, v, r}} plus each election's date/year.
    lookups = {name: {} for name in TARGETS}
    dates = {}
    years = {}
    with open(CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            name = row["Election"]
            if name not in TARGETS:
                continue
            dates.setdefault(name, row["Election_Date"])
            years.setdefault(name, row["Year"])
            if row["Geo_Level"] != "Election District":
                continue
            ed = parse_electdist(row["Geo_Unit"])
            if ed is None:
                continue
            try:
                t = float(row["Turnout"])
                v = int(row["Voted"])
                dn = int(row["Did_Not_Vote"])
            except ValueError:
                continue
            lookups[name][ed] = {"t": round(t, 4), "v": v, "r": v + dn}

    missing = [n for n in TARGETS if not lookups[n]]
    if missing:
        sys.exit(f"ERROR: no ED rows for: {missing}")

    # Join onto geometry: each feature carries every election it has data for.
    gj = json.load(open(GEOJSON_IN))
    matched = {name: 0 for name in TARGETS}
    for feat in gj["features"]:
        ed = int(feat["properties"]["ElectDist"])
        props = {"ElectDist": ed}
        for name, key in TARGETS.items():
            d = lookups[name].get(ed)
            if d is not None:
                props[f"t{key}"] = d["t"]
                props[f"v{key}"] = d["v"]
                props[f"r{key}"] = d["r"]
                matched[name] += 1
        feat["properties"] = props

    # Per-election color breaks, computed from the values actually on the map.
    series_vals = {key: [] for key in TARGETS.values()}
    for feat in gj["features"]:
        for key in TARGETS.values():
            tv = feat["properties"].get(f"t{key}")
            if tv is not None:
                series_vals[key].append(tv)

    meta = []
    for name, key in TARGETS.items():
        vals = series_vals[key]
        meta.append({
            "key": key,
            "name": name,
            "date": dates[name],
            "year": years[name],
            "n": len(vals),
            "breaks": quintile_breaks(vals),
        })
    # chronological slider order (dates are MM/DD/YYYY -> sort by Y, M, D)
    def datekey(m):
        mm, dd, yy = m["date"].split("/")
        return (int(yy), int(mm), int(dd))
    meta.sort(key=datekey)

    with open(GEOJSON_OUT, "w") as f:
        json.dump(gj, f, separators=(",", ":"))
    with open(META_OUT, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"features: {len(gj['features'])}")
    print(f"wrote {GEOJSON_OUT} and {META_OUT}\n")
    print(f"{'election':28} {'date':12} {'matched':>7}  breaks (%)")
    for m in meta:
        b = " ".join(f"{x*100:4.1f}" for x in m["breaks"])
        print(f"{m['name']:28} {m['date']:12} {matched[m['name']]:>7}  {b}")


if __name__ == "__main__":
    main()
