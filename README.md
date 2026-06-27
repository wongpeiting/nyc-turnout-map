# The Turnout Divide — NYC 2024 voter turnout map

An interactive choropleth of voter turnout in New York City's roughly 4,000 election
districts in the 2024 General Election. Each district is shaded by the share of its
registered voters who cast a ballot, from under 45% (deep red) to 75%+ (pale yellow).
Hover any district for its turnout rate and raw counts.

Built with [Mapbox GL JS](https://docs.mapbox.com/mapbox-gl-js/).

## Files

- `index.html` — the map (Mapbox GL JS, geocoder search, hover tooltip, mobile drawer).
- `turnout-2024.geojson` — district polygons joined to turnout numbers; what the map loads.
- `build_turnout.py` — builds `turnout-2024.geojson` by joining the turnout CSV to the
  district geometry on `ElectDist`.
- `election-results.geojson` — the source district geometry (originally a 2025 mayoral
  primary file; only its shapes and `ElectDist` ids are reused here).
- `Historical_Voter_Turnout_20260626.csv` — raw turnout export (see Data source).

## Data source

NYC Open Data — [Historical Voter Turnout](https://data.cityofnewyork.us/City-Government/Historical-Voter-Turnout/rixx-fc37/about_data)
(dataset `rixx-fc37`), filtered to `Geo_Level = "Election District"` and
`Election = "2024 General Election"`. Turnout is reported by the source; registered
voters are derived as `Voted + Did_Not_Vote`. Districts with no matching data (parks and
other non-residential areas) render blank.

## Rebuild

```bash
python3 build_turnout.py
```

## Run locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000/index.html
```

The Mapbox access token in `index.html` is a public client-side token restricted to this
project's URLs in the Mapbox account.
