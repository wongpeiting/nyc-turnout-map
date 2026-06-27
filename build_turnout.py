# build_turnout.py
# Join 2024 General Election ED-level turnout (NYC Open Data) onto the existing
# district geometry, by ElectDist. Writes turnout-2024.geojson. Read-only on inputs.
import csv
import json
import sys

CSV_PATH = "Historical_Voter_Turnout_20260626.csv"
GEOJSON_IN = "election-results.geojson"
GEOJSON_OUT = "turnout-2024.geojson"
ELECTION = "2024 General Election"

# syncing assembly district numbers
def parse_electdist(geo_unit):
    """ '23,001' -> 23001 ; return None if it doesn't look like AD,ED."""
    parts = geo_unit.split(",")
    if len(parts) != 2:
        return None
    try:
        ad, ed = int(parts[0]), int(parts[1])
    except ValueError:
        return None
    if ed == 0:  # 'NN,0' rows are placeholders, not real EDs
        return None
    return int(f"{ad}{parts[1].zfill(3)}")

# build lookup table: reads every CSV row but keep only ones relevant to the 2024 General Election
# records 3 things: turnout, voted, and registered (computed as voted + did_not)
def load_turnout(csv_path):
    """Return {ElectDist:int -> {turnout, voted, registered}} for the target election."""
    lookup = {}
    na = 0
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            if row["Geo_Level"] != "Election District" or row["Election"] != ELECTION:
                continue
            ed = parse_electdist(row["Geo_Unit"])
            if ed is None:
                continue
            try:
                turnout = float(row["Turnout"])
                voted = int(row["Voted"])
                did_not = int(row["Did_Not_Vote"])
            except ValueError:
                na += 1
                continue
            lookup[ed] = {
                "turnout": round(turnout, 4),
                "voted": voted,
                "registered": voted + did_not,
            }
    return lookup, na

# join the data -- walks every polygon in the geojson, looks up its ElectDist in the table to match
# then writes turnout-2024.geojson file
def main():
    lookup, na = load_turnout(CSV_PATH)
    if not lookup:
        sys.exit(f"ERROR: no '{ELECTION}' Election District rows found in {CSV_PATH}")

    with open(GEOJSON_IN) as f:
        gj = json.load(f)

    matched = 0
    for feat in gj["features"]:
        ed = int(feat["properties"]["ElectDist"])
        data = lookup.get(ed)
        props = {"ElectDist": ed}
        if data is not None:
            props.update(data)
            matched += 1
        feat["properties"] = props

    with open(GEOJSON_OUT, "w") as f:
        json.dump(gj, f)

    total = len(gj["features"])
    turnouts = [p["turnout"] for f in gj["features"] if (p := f["properties"]).get("turnout") is not None]
    turnouts.sort()
    print(f"features: {total}")
    print(f"matched:  {matched}")
    print(f"no data:  {total - matched} (incl. {na} NA rows dropped from CSV)")
    print(f"turnout min/median/max: "
          f"{turnouts[0]:.3f} / {turnouts[len(turnouts)//2]:.3f} / {turnouts[-1]:.3f}")
    print(f"wrote {GEOJSON_OUT}")


if __name__ == "__main__":
    main()
