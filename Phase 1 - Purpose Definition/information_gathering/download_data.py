"""Phase 1 – Information Gathering: download the data-layer resources, unchanged.

Every file is saved in raw/ exactly as the source returns it (no renaming, no cleaning,
no filtering: that is Language Definition, Phase 2). A file that already exists is
skipped, so delete it to download it again. The window for weather and snow is WINDOW.

Run:  python3 download_data.py        (Python >= 3.9, standard library only)
      python3 download_data.py --summary   (only print what is in raw/)
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path

RAW = Path(__file__).resolve().parent / "raw"
UA = {"User-Agent": "KG-2026-UniTn-student-project"}
WINDOW = ("2025-10-01", "2026-09-30")  # one year of weather and snow

OVERPASS_MIRRORS = ["https://overpass-api.de/api/interpreter",
                    "https://overpass.kumi.systems/api/interpreter",
                    "https://overpass.private.coffee/api/interpreter"]
T = '[out:json][timeout:300];area["ref:ISTAT"="022"]["admin_level"="6"]->.t;'  # Provincia di Trento
OVERPASS = {
    "osm_hiking_routes.json": T + 'rel(area.t)["route"="hiking"];out tags center;',
    "osm_restaurants_huts.json": T + '(nwr(area.t)["amenity"="restaurant"];'
                                     'nwr(area.t)["tourism"~"^(alpine_hut|wilderness_hut)$"];);out tags center;',
    "osm_malghe_agriturismi.json": T + '(nwr(area.t)["name"~"^Malga ",i];'
                                       'nwr(area.t)["tourism"="guest_house"]["guest_house"="agritourism"];'
                                       'nwr(area.t)["agritourism"];);out tags center;',
    "osm_peaks_passes.json": T + '(node(area.t)["natural"~"^(peak|saddle)$"];'
                                 'node(area.t)["mountain_pass"="yes"];);out tags;',
    "osm_via_ferrata.json": T + '(way(area.t)["highway"="via_ferrata"];'
                                'rel(area.t)["route"~"^(ferrata|via_ferrata)$"];);out geom;',
    "osm_lakes_viewpoints.json": T + '(nwr(area.t)["natural"="water"]["water"="lake"];'
                                     'nwr(area.t)["tourism"="viewpoint"];);out tags center;',
    "osm_parking.json": T + 'nwr(area.t)["amenity"="parking"];out tags center;',
    "osm_transport.json": T + '(nwr(area.t)["railway"~"^(station|halt)$"];'
                              'nwr(area.t)["aerialway"="station"];);out tags center;'
                              'way(area.t)["aerialway"~"^(cable_car|gondola|mixed_lift|chair_lift)$"];out geom;',
    "osm_admin_areas.json": T + '(rel(area.t)["boundary"="administrative"]["admin_level"~"^(7|8)$"];'
                                'nwr(area.t)["natural"="valley"];);out tags center;',
    "osm_places.json": T + 'node(area.t)["place"~"^(city|town|village)$"];out tags;',  # town centres
}
FILES = {
    "sat_sentieri.kml.zip": "https://sentieri.sat.tn.it/download/sentierisat.kml.zip",
    "meteotrentino_stations.xml": "https://dati.meteotrentino.it/service.asmx/listaStazioni",
    "meteotrentino_snow_fields.xml": "https://dati.meteotrentino.it/service.asmx/listaCampiNeve",
    "gtfs_extraurbano.zip": "https://www.trentinotrasporti.it/opendata/google_transit_extraurbano_tte.zip",
    "gtfs_urbano.zip": "https://www.trentinotrasporti.it/opendata/google_transit_urbano_tte.zip",
}
SNOW_DAY = "https://dati.meteotrentino.it/service.asmx/rilieviNeveDiUnGiornoCsv?anno={y}&mese={m}&giorno={d}"
OPEN_METEO = {  # one file per API, daily values at every active Meteotrentino station
    "openmeteo_observations.json": ("https://archive-api.open-meteo.com/v1/archive",
        "precipitation_sum,rain_sum,snowfall_sum,snow_depth_max,weather_code,cloud_cover_mean,"
        "wind_speed_10m_max,wind_gusts_10m_max,temperature_2m_max,temperature_2m_min"),
    "openmeteo_forecasts.json": ("https://historical-forecast-api.open-meteo.com/v1/forecast",
        "weather_code,precipitation_sum,precipitation_probability_max,snowfall_sum,cloud_cover_mean,"
        "wind_speed_10m_max,wind_gusts_10m_max,temperature_2m_max,temperature_2m_min"),
}


def get(url, data=None, timeout=300):
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=UA), timeout=timeout) as r:
        return r.read()


def save(name, content):
    (RAW / name).write_bytes(content)
    print(f"  saved {name} ({len(content) // 1024} KB)")


def overpass(name, query, rounds=3):
    """Public Overpass servers are often overloaded: try every mirror, up to 3 rounds."""
    data = urllib.parse.urlencode({"data": query}).encode()
    for n in range(rounds):
        for url in OVERPASS_MIRRORS:
            try:
                return save(name, get(url, data))
            except OSError as err:
                print(f"  {url} failed ({err})")
        if n + 1 < rounds:
            print("  all mirrors failed, retrying in 2 minutes")
            time.sleep(120)
    print(f"  SKIPPED {name}: run the script again later")


def snow_history(name):
    """One request per day; the daily CSVs are concatenated with the header kept once."""
    day, end, out = date.fromisoformat(WINDOW[0]), date.fromisoformat(WINDOW[1]), []
    while day <= end:
        lines = get(SNOW_DAY.format(y=day.year, m=day.month, d=day.day), timeout=60).splitlines(keepends=True)
        out += lines if not out else lines[1:]
        day += timedelta(days=1)
        time.sleep(0.2)
    save(name, b"".join(out))


def active_stations():
    """Weather stations without an end date in meteotrentino_stations.xml."""
    ns = {"m": "http://www.meteotrentino.it/"}
    root = ET.parse(RAW / "meteotrentino_stations.xml").getroot()
    return [{"code": a.findtext("m:codice", namespaces=ns), "lat": a.findtext("m:latitudine", namespaces=ns),
             "lon": a.findtext("m:longitudine", namespaces=ns), "ele": a.findtext("m:quota", namespaces=ns)}
            for a in root.findall("m:anagrafica", ns) if not (a.findtext("m:fine", namespaces=ns) or "").strip()]


def open_meteo(name, url, variables, batch=20):
    """Open-Meteo free tier: ~600 weighted calls/minute, 5000/hour; one year at one point costs ~26."""
    stations, out = active_stations(), []
    for i in range(0, len(stations), batch):
        b = stations[i:i + batch]
        q = urllib.parse.urlencode({"latitude": ",".join(s["lat"] for s in b),
                                    "longitude": ",".join(s["lon"] for s in b),
                                    "elevation": ",".join(s["ele"] for s in b),
                                    "start_date": WINDOW[0], "end_date": WINDOW[1],
                                    "daily": variables, "timezone": "Europe/Rome"})
        for attempt in range(8):
            try:
                resp = json.loads(get(f"{url}?{q}", timeout=120))
                break
            except urllib.error.HTTPError as err:
                if err.code != 429:
                    raise
                print(f"  rate limit reached, waiting 10 minutes ({err.read()[:120]!r})")
                time.sleep(600)
        else:
            raise SystemExit(f"could not download {name}")
        for s, r in zip(b, resp if isinstance(resp, list) else [resp]):
            out.append({"station_code": s["code"], **r})  # keeps the link to the station
        print(f"  {name}: {len(out)}/{len(stations)} stations")
        if i + batch < len(stations):
            time.sleep(61)
    save(name, json.dumps(out).encode())


def summary():
    """Count what is in raw/ (used for the numbers in information_gathering.md)."""
    for p in sorted(RAW.iterdir()):
        n = ""
        if p.name.startswith("osm_"):
            n = f"{len(json.loads(p.read_bytes())['elements'])} elements"
        elif p.name.startswith("openmeteo_"):
            d = json.loads(p.read_bytes())
            n = f"{len(d)} stations x {len(d[0]['daily']['time'])} days"
        elif p.suffix == ".csv":
            n = f"{len(p.read_bytes().splitlines()) - 1} rows"
        print(f"{p.name:34} {p.stat().st_size // 1024:>7} KB  {n}")


def todo(name):
    if (RAW / name).exists():
        return False
    print(f"downloading {name}")
    return True


def main():
    RAW.mkdir(exist_ok=True)
    for name, url in FILES.items():
        if todo(name):
            save(name, get(url))
    if todo("meteotrentino_snow_history.csv"):
        snow_history("meteotrentino_snow_history.csv")
    for name, (url, variables) in OPEN_METEO.items():
        if todo(name):
            open_meteo(name, url, variables)
    for name, query in OVERPASS.items():  # last: Overpass is the least reliable source
        if todo(name):
            overpass(name, query)
    summary()
    missing = [n for n in [*OVERPASS, *FILES, "meteotrentino_snow_history.csv", *OPEN_METEO]
               if not (RAW / n).exists()]
    if missing:
        raise SystemExit(f"missing: {missing}")


if __name__ == "__main__":
    summary() if "--summary" in sys.argv else main()
