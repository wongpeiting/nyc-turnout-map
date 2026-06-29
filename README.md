# The Turnout Divide — NYC voter turnout, 2022–2024

An interactive choropleth of voter turnout across New York City's roughly 4,000 election districts. A time slider steps through **eight elections from 2022 to 2024** (primaries and general elections), crossfading between them. Each district is shaded by the share of its registered voters who cast a ballot, using **even color bands scaled to each election type** (generals 40/60/80%, primaries 5/10/15%) so primaries stay legible alongside generals. Hover or click any district for its turnout rate and raw counts.

Built with [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/).

## Features

- **Time slider** through eight elections, with a 450ms crossfade between them.
- **Even color bands** scaled per election type (generals 40/60/80%, primaries 5/10/15%).
- **Click a legend band** to isolate those districts; **click a district** to pin its numbers.
- **Locate me** (GPS), shareable **URL view state** (`#zoom/lat/lng`), and a swoop-in on load.

## Files

- `index.html` — the map (Mapbox GL JS, geocoder search, time slider, hover/click readouts).
- `turnout-series.geojson` — district polygons joined to per-election turnout numbers; what the map loads. Built from the CSV + geometry.
- `series-meta.json` — the ordered election list with per-election color breaks (reference output of the build; the page keeps its own inline copy in the `ELECTIONS` array).
- `build_series.py` — builds `turnout-series.geojson` and `series-meta.json` by joining the turnout CSV to the district geometry on `ElectDist`.
- `election-results.geojson` — the source district geometry (originally a 2025 mayoral primary file; only its shapes and `ElectDist` ids are reused here).
- `Historical_Voter_Turnout_20260626.csv` — raw turnout export (see Data source).

## Data source

NYC Open Data — [Historical Voter Turnout](https://data.cityofnewyork.us/City-Government/Historical-Voter-Turnout/rixx-fc37/about_data) (dataset `rixx-fc37`), filtered to `Geo_Level = "Election District"`. Turnout is reported by the source; registered voters are derived as `Voted + Did_Not_Vote`.

### Two things to know about the data

- **Only 2022–2024 elections are included.** They share the current district map. Pre-2022 elections are excluded because the 2022 redistricting changed ED boundaries: the codes line up but the geography doesn't, so joining them would be a false join.
- **Blank districts in primaries mean "no contest," not "no turnout."** New York runs closed party primaries, and a race only appears where it was contested. Districts with no primary on the ballot are reported as `NA` (often with every voter marked "Not Eligible to Vote") and render blank. Generals fill the whole city; primaries light up only ~70% of districts, but is not to be read as low participation.

## Rebuild

```bash
python3 build_series.py
```

If the election set or breaks change, update the inline `ELECTIONS` array near the top of the `<script>` in `index.html` to match `series-meta.json`.

## Run locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000/index.html
```