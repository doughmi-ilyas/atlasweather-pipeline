import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from transformation.transform_weather import bronzedata, buildrows  # noqa: E402

DAILY = {
    "time": ["2026-09-14", "2026-09-15"],
    "temperature_2m_max": [22.6, 24.0],
    "temperature_2m_min": [20.1, 20.9],
    "precipitation_sum": [0.0, 1.2],
    "precipitation_probability_max": [0, 40],
    "wind_speed_10m_max": [21.1, 31.6],
    "wind_gusts_10m_max": [26.3, 38.2],
    "weather_code": [1, 3],
}


def write_city(folder, name, city="Ad Dakhla"):
    payload = {"city": city, "lat": 23.7, "lon": -15.9,
               "fetched_at": "2026-09-14 18:58:28", "response": {"daily": DAILY}}
    (folder / name).write_text(json.dumps(payload), encoding="utf-8")


def test_bronzedata_skips_failed_and_non_json(tmp_path):
    write_city(tmp_path, "a.json")
    (tmp_path / "b-failed.json").write_text("{}")
    (tmp_path / "notes.txt").write_text("x")
    assert bronzedata(str(tmp_path)) == ["a.json"]


def test_buildrows_explodes_days_and_dedupes(tmp_path, monkeypatch):
    bronze = tmp_path / "bronze"
    bronze.mkdir()
    write_city(bronze, "a.json")
    write_city(bronze, "b.json")  # same city+dates: duplicates must be dropped
    data = tmp_path / "data"
    data.mkdir()
    (data / "ma-cities.csv").write_text("city,admin_name,population\nAd Dakhla,Dakhla-Oued Ed-Dahab,165463\n")
    monkeypatch.chdir(tmp_path)
    df = buildrows("bronze", ["a.json", "b.json"])
    assert len(df) == 2
    assert df["population"].iloc[0] == 165463
    assert df["temperature_2m_max"].dtype.kind == "f"
    assert (tmp_path / "silver" / "data.csv").exists()
