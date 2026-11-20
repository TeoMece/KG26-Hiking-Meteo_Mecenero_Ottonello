# Information Gathering – resources, fields and CQ coverage

This document describes the resources in `raw/`. For each one it gives what it contains, which **original** fields matter for the CQs in `Context Questions and Scenarios Definitions.xlsx`, and what we noticed in the data.
Field names are kept as the sources give them. Renaming them to the language terms, fixing datatypes and filtering are Phase 2.

Downloaded on 20 Nov 2026 with `download_data.py`. Weather and snow cover 1 Oct 2025 – 30 Sep 2026.

**In short**
- 18 raw files from 5 sources: SAT, OpenStreetMap, Meteotrentino, Open-Meteo, Trentino Trasporti.
- Of the 40 CQs, 25 can be answered with these data, 12 only in part, and 3 not as they are written (CQ9, CQ27, CQ39). See section 2.
- Section 3 lists the data problems to fix in Phase 2. Section 4 lists the decisions we still have to take together.

**Contents:** 1. Resources · 2. CQ coverage · 3. Things to handle in Phase 2 · 4. Open decisions for the team

## 1. Resources

### SAT trail catalogue – `sat_sentieri.kml.zip`

- **Content:** 1082 trail segments (KML `Placemark`) with 1080 distinct codes. Each segment is a `LineString` in WGS84 (lon, lat), without altitude.
- **Fields:**
  - `numero`: code; prefix E (554) or O (528)
  - `denominaz`: name; empty for 690
  - `difficolta`: T 35, E 784, EE 191, EEA-F 19, EEA-PD 23, EEA-D 26, EEA-MD 4
  - `loc_inizio`, `loc_fine`: start and end place, as text
  - `quota_iniz`, `quota_fine`, `quota_min`, `quota_max`: altitude in metres
  - `lun_planim`, `lun_inclin`: length in metres, planimetric and inclined
  - `t_andata`, `t_ritorno`: walking time out and back, as `hh:mm`
  - `gr_mont`: mountain group (95 groups)
  - `comuni_toc`: the municipalities the trail crosses, comma-separated
  - `competenza`: the SAT section in charge
- **Via ferratas:** the 72 segments with `difficolta` EEA-*. 71 of them have a name, and 66 of the names start with "VIA FERRATA".
- **Elevation gain:** there is no field for it.

### OpenStreetMap (Overpass API, area = Provincia di Trento, `ref:ISTAT=022`)

Every element has its OSM id, its tags and a point (`center`, or the node itself). The via ferrata and aerialway files also have the full geometry.

| File | Elements | Relevant tags (how many elements have them) |
|---|---|---|
| `osm_hiking_routes.json` | 1650 `route=hiking` relations | `ref` 1477, `name` 763, `ascent` 1142, `distance` (km) 1186, `duration` 12; `network`: lwn 1475, rwn 85, nwn 51, iwn 9 |
| `osm_restaurants_huts.json` | 1511 restaurants, 189 `alpine_hut`, 160 `wilderness_hut` (bivouacs) | `opening_hours`: restaurants 345, huts 36, bivouacs 2; `ele`: huts 140, bivouacs 73 |
| `osm_malghe_agriturismi.json` | 1104 features named "Malga …", 41 tagged as agritourism | malghe: `amenity=restaurant` 71, `alpine_hut` 35, `wilderness_hut` 33, but also `building=yes` 417, `place=locality` 203, `tourism=information` 80; `opening_hours` 8 |
| `osm_peaks_passes.json` | 1981 peaks, 731 saddles and passes | peaks: `name` 1772, `ele` 1877; passes: `name` 639, `ele` 662 |
| `osm_via_ferrata.json` | 157 `highway=via_ferrata` ways, 11 relations | ways: `name` 77, `via_ferrata_scale` 105 |
| `osm_lakes_viewpoints.json` | 254 lakes, 939 viewpoints | lakes: `name` 160 |
| `osm_parking.json` | 10857 parking areas | `access`: not set 4167, yes 2768, private 1927, customers 1757 |
| `osm_transport.json` | 54 railway stations, 17 halts, 582 aerialway stations, 208 aerialway lines (137 chair lifts, 56 gondolas, 15 cable cars) | `name`, `aerialway` |
| `osm_admin_areas.json` | 166 municipalities (`admin_level=8`), 16 Comunità di Valle (`admin_level=7`), 846 `natural=valley` (820 named) | `name`; centre of the bounding box only, no boundaries |
| `osm_places.json` | 405 settlements (1 city, 7 towns, 397 villages) | `name`; the node is the centre of the settlement |

### Meteotrentino

- `meteotrentino_stations.xml`: 208 weather stations, of which 113 are active (no `fine` date). Fields: `codice`, `nome`, `quota`, `latitudine`, `longitudine`, `inizio`, `fine`.
- `meteotrentino_snow_fields.xml`: 55 snow observation fields. Fields: `codice`, `nome`, `quota`, `utmlat`, `utmlon` (UTM, metres).
- `meteotrentino_snow_history.csv`: 3709 daily observations from 37 fields.
  - **By month:** Oct 33, Nov 175, Dec 731, Jan 829, Feb 761, Mar 767, Apr 260, May 33, Jun–Sep about 30 each. From June to August only Malga Bissina (1780 m) reports, apart from one row from Canazei in June.
  - **Fields for the CQs:** `codice_campo`, `DataRilievo`, `Altitudine`, `HS` (snow depth, cm), `HN` (fresh snow, cm), `HSnum`, `HNnum`, `LatUTM`, `LongUTM`. The other columns use the AINEVA observation code.

### Open-Meteo (daily values at the 113 active Meteotrentino stations)

The script adds `station_code` to each record, so every series stays linked to its station. Both files have 113 stations × 365 days and no null values.

- `openmeteo_observations.json`, from the Historical Weather API (model reanalysis, not station measurements):
  - `precipitation_sum`, `rain_sum` (mm), `snowfall_sum` (cm), `snow_depth_max` (m)
  - `weather_code` (WMO), `cloud_cover_mean` (%)
  - `wind_speed_10m_max`, `wind_gusts_10m_max` (km/h)
  - `temperature_2m_max`, `temperature_2m_min` (°C)
- `openmeteo_forecasts.json`, from the Historical Forecast API: the first hours of each weather-model run, joined together. It is a short-range forecast for the day, not a forecast made several days before.
  - `weather_code`, `precipitation_sum`, `precipitation_probability_max`, `snowfall_sum`, `cloud_cover_mean`
  - wind and temperature, as above

### Trentino Trasporti GTFS

| File | Stops | Routes | Calendar |
|---|---|---|---|
| `gtfs_extraurbano.zip` | 2857 | 121: 120 bus, 1 rail (R35 Trento – Malè – Mezzana) | 10 Sep 2026 – 25 Jun 2027 |
| `gtfs_urbano.zip` | 1116 | 44: 43 bus, 1 cable car (Funivia Trento – Sardagna, `route_type` 5) | 10 Sep 2026 – 8 Jun 2027 |

Both feeds contain `stops`, `routes`, `trips`, `stop_times`, `calendar`, `calendar_dates`, `shapes` and `transfers`.

## 2. CQ coverage

Legend:
- ✅ answerable with the data in `raw/`, sometimes with a spatial join (distance, intersection) in a later phase;
- ⚠️ answerable only in part, or only after a decision of the team;
- ❌ not answerable as the CQ is written.

| CQ | Data | Status | Note |
|---|---|---|---|
| CQ1 | SAT geometry, `gr_mont`; OSM restaurants, `alpine_hut` | ✅ | "Mountain Y" can be a SAT `gr_mont` or an OSM peak: to decide |
| CQ2 | SAT `comuni_toc`, `t_andata` + `t_ritorno` | ✅ | |
| CQ3 | SAT `quota_max` | ✅ | "Area Y" to define |
| CQ4 | SAT `difficolta`; OSM `ascent` | ⚠️ | SAT has no elevation gain; "family-friendly" to define |
| CQ5 | SAT geometry; valleys (OSM); observations `precipitation_sum` | ✅ | needs a rule linking trails to stations |
| CQ6 | valleys; observations `cloud_cover_mean`, `weather_code` | ✅ | threshold for "clear skies" to decide |
| CQ7 | SAT `difficolta` EEA-*, `gr_mont` | ✅ | |
| CQ8 | SAT `quota_max`; forecasts `weather_code` (95–99 = thunderstorm), `wind_gusts_10m_max` | ⚠️ | daily values: "afternoon" is not available |
| CQ9 | – | ❌ | no driving times in the data; needs a routing service, or straight-line distance as a proxy |
| CQ10 | SAT `lun_inclin`, EEA-* | ✅ | "Region Y" to define (Trentino is one province) |
| CQ11 | SAT `quota_max`, `denominaz` | ✅ | |
| CQ12 | SAT geometry (EEA-* segments and the other segments) | ✅ | spatial: start of the via ferrata touching another segment |
| CQ13 | SAT `comuni_toc`, `difficolta` (F < PD < D < MD); OSM `via_ferrata_scale` | ✅ | |
| CQ14 | SAT EEA-*, `gr_mont`; snow `HS`; observations `snow_depth_max` | ⚠️ | snow is measured at points: needs a rule linking a via ferrata to a field or station |
| CQ15 | OSM peaks `ele`; `snow_depth_max`, `HS` | ⚠️ | "today": the KG is a snapshot, so "on day X"; snow at the peak is estimated from stations |
| CQ16 | observations `snowfall_sum`; snow `HN` | ✅ | needs a rule linking routes to stations |
| CQ17 | stations `quota` + `snowfall_sum`; snow fields `Altitudine` + `HN` | ✅ | "Locality" = station or snow field? |
| CQ18 | SAT `t_andata`, `t_ritorno` | ✅ | |
| CQ19 | SAT `gr_mont`; OSM `ascent` | ⚠️ | as CQ4 |
| CQ20 | OSM lakes, viewpoints; forecasts `cloud_cover_mean`, `weather_code` | ✅ | spatial |
| CQ21 | SAT `quota_max`, `loc_fine`; OSM peaks | ✅ | link trail and peak by geometry, or by the name in `loc_fine` |
| CQ22 | OSM parking, `alpine_hut`; SAT geometry, `loc_fine` | ✅ | 3684 parkings are private or for customers |
| CQ23 | SAT `difficolta` = EE (191), `gr_mont` | ✅ | |
| CQ24 | OSM peaks, `alpine_hut`, `wilderness_hut` (point, `ele`) | ✅ | distance or altitude rule for "on the summit" |
| CQ25 | SAT `quota_min`, `quota_max` | ✅ | |
| CQ26 | SAT geometry, `loc_fine`; OSM peaks | ✅ | spatial |
| CQ27 | – | ❌ | snow is known at 37 fields and 113 stations, not along a trail |
| CQ28 | OSM passes, huts, `opening_hours` | ⚠️ | "open" is missing for almost all huts and bivouacs; "snow-covered" has the same problem as CQ27 |
| CQ29 | SAT, OSM huts; snow | ⚠️ | "today" and point snow, as CQ15 |
| CQ30 | GTFS `stops`, `trips`, `stop_times`; SAT start point | ⚠️ | needs timetable routing; the GTFS calendar does not overlap the weather window |
| CQ31 | SAT start point; `osm_places.json` | ✅ | |
| CQ32 | SAT end point; `osm_places.json`; OSM railway stations; GTFS R35 | ✅ | |
| CQ33 | GTFS, OSM transport | ⚠️ | meaning of "only" unclear |
| CQ34 | GTFS `stops`, `stop_times`; SAT; OSM restaurants | ✅ | spatial, plus "the line stops in Y" from `stop_times` |
| CQ35 | SAT geometry; OSM `wilderness_hut` | ✅ | spatial |
| CQ36 | OSM routes with `network` rwn/nwn/iwn (145); huts | ⚠️ | "multi-day" is not tagged (`duration` on 12 routes): define it by distance or by number of huts |
| CQ37 | OSM "Malga …" | ⚠️ | selection by name also catches place names and signposts: filter in Phase 2 |
| CQ38 | OSM agritourism (41) | ⚠️ | low coverage |
| CQ39 | OSM malghe, `opening_hours` (8); forecasts | ❌ | "open and serving lunch" is not in the data; "this week" does not fit a snapshot; the forecasts are short-range |
| CQ40 | SAT `comuni_toc`, `loc_inizio`, `loc_fine`; OSM `alpine_hut` | ✅ | |

**Total:** 25 ✅, 12 ⚠️, 3 ❌.

## 3. Things to handle in Phase 2

These are data problems only. Nothing has been changed in `raw/`.

### SAT
- Codes E396 and E731 appear twice each.
- 690 trails have an empty `denominaz`.
- Text is in upper case and contains HTML entities (`&quot;`).
- Times are `hh:mm` strings, and `t_ritorno` is `00:00` for 5 trails.
- `comuni_toc` is a comma-separated list.
- SAT codes carry an E/O prefix, while OSM `ref` has only the number. The 1080 SAT codes use 795 different numbers, and 285 of those numbers exist with both prefixes (for example E244 and O244). Of the 1148 OSM routes whose `ref` matches a SAT number, 601 could be either one. So a link to OSM (for example to use `ascent`) has to be checked on the geometry.

### OSM
- `distance` is a string in km, `ascent` a string in m.
- Malghe are selected by name, so the file also contains place names (`place=locality`) and signposts (`tourism=information`).
- `opening_hours` is rare everywhere.
- Via ferratas appear both in SAT (72 segments) and in OSM (157 ways), and the two overlap.
- Many aerialways are ski lifts (137 chair lifts), and OSM does not say whether they run in summer.
- Admin areas have only a bounding-box centre.

### Meteotrentino snow
- Values are in the AINEVA code (for example `Ta` = 54 means −4 °C, decoded in `TaG`), with `/`, `//` and `///` for missing values, leading zeros (`015`) and trailing spaces.
- UTM coordinates use a decimal comma, and `LatUTM` holds the easting and `LongUTM` the northing (the labels are swapped).
- Field 10AG (Pampeago AG) is not in `meteotrentino_snow_fields.xml` and has no coordinates (95 rows).
- 19 field-days have more than one observation.
- In `meteotrentino_snow_fields.xml`, `utmlat` holds the easting and `utmlon` the northing: the labels are swapped.

### Open-Meteo
- These are model values on a grid, adjusted to the station altitude, not measurements.
- `snow_depth_max` is in metres, while Meteotrentino `HS` is in centimetres.

### GTFS
- The timetable starts on 10 Sep 2026, so it does not overlap the weather window.

## 4. Open decisions for the team

1. **Spatial concepts:** which of Area, Valley, Region, Mountain, Mountain Group and Locality to keep, and from which file each comes. The candidates are Comunità di Valle (16), `natural=valley` (846), SAT `gr_mont` (95) and municipalities (166).
2. **Trail, Route and Via Ferrata:** SAT segments, OSM route relations, SAT EEA-* or OSM `highway=via_ferrata`.
3. **Linking weather and snow to trails:** for example the nearest active station, possibly with a limit on the difference in altitude.
4. **Time:** rewrite "today" and "this week" as "on day X" inside the window.
5. **Forecasts:** the Historical Forecast API is short-range. A forecast made a week before is not available.
6. **Elevation gain:** use OSM `ascent` through the SAT–OSM link, or compute it from a terrain model, which we have not collected.
7. **Travel times by car and by bus (CQ9, CQ30):** leave them out, or compute them.
8. **Opening of huts and malghe:** drop "open", or accept low coverage.
