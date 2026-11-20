# Information Gathering (Phase 1 – data layer)

`download_data.py` collects the data-layer resources for the purpose and saves them in `raw/` **exactly as the sources return them**.
Nothing is renamed, cleaned or filtered here: according to the iTelos lectures (L12 slides 27–28, L17 slides 18, 41, 42), that is done in **Language Definition (Phase 2)**, after the language terms are fixed.

```bash
python3 download_data.py            # downloads only the files missing in raw/
python3 download_data.py --summary  # prints what is in raw/
```

Delete a file in `raw/` to download it again. Weather and snow cover the window `WINDOW` in the script (1 Oct 2025 – 30 Sep 2026).

What each file contains, which CQs it serves, and what we noticed in the data are in [`information_gathering.md`](information_gathering.md).

## Files in `raw/`

| File | Source | What | License |
|---|---|---|---|
| `osm_hiking_routes.json` | OpenStreetMap (Overpass) | hiking route relations | ODbL |
| `osm_restaurants_huts.json` | OpenStreetMap | restaurants, mountain huts, bivouacs | ODbL |
| `osm_malghe_agriturismi.json` | OpenStreetMap | features named "Malga …", agriturismi | ODbL |
| `osm_peaks_passes.json` | OpenStreetMap | peaks, saddles, mountain passes | ODbL |
| `osm_via_ferrata.json` | OpenStreetMap | via ferrata ways and relations, with geometry | ODbL |
| `osm_lakes_viewpoints.json` | OpenStreetMap | lakes, viewpoints | ODbL |
| `osm_parking.json` | OpenStreetMap | parking areas | ODbL |
| `osm_transport.json` | OpenStreetMap | railway stations, aerialway stations and lines | ODbL |
| `osm_admin_areas.json` | OpenStreetMap | municipalities, Comunità di Valle, named valleys | ODbL |
| `osm_places.json` | OpenStreetMap | town and village centres | ODbL |
| `sat_sentieri.kml.zip` | SAT, https://sentieri.sat.tn.it/download/ | SAT trail catalogue with track geometry | ODbL / DbCL |
| `meteotrentino_stations.xml` | Meteotrentino `listaStazioni` | weather stations | CC-BY |
| `meteotrentino_snow_fields.xml` | Meteotrentino `listaCampiNeve` | snow observation fields | CC-BY |
| `meteotrentino_snow_history.csv` | Meteotrentino `rilieviNeveDiUnGiornoCsv` | daily snow observations in the window | CC-BY |
| `openmeteo_observations.json` | Open-Meteo Historical Weather API | daily observed weather at each active station | CC BY 4.0 |
| `openmeteo_forecasts.json` | Open-Meteo Historical Forecast API | daily forecast weather at each active station | CC BY 4.0 |
| `gtfs_extraurbano.zip`, `gtfs_urbano.zip` | Trentino Trasporti (dati.trentino.it) | bus/rail stops, lines and timetables (GTFS) | CC-BY |
