import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from gold.gold import rainCategory, riskScore, tempCategory, windSpeedCategory  # noqa: E402


def row(rain=0, gust=0, temp=20, prob=0, wind=0):
    return {
        "precipitation_sum": rain,
        "wind_gusts_10m_max": gust,
        "temperature_2m_max": temp,
        "precipitation_probability_max": prob,
        "wind_speed_10m_max": wind,
    }


@pytest.mark.parametrize("t,c", [(-1, "froid"), (0, "frais"), (14.9, "frais"), (15, "doux"),
                                 (30, "chaud"), (40, "extreme")])
def test_temp_category(t, c):
    assert tempCategory(t) == c


@pytest.mark.parametrize("r,c", [(0, "sec"), (0.1, "legere"), (5, "moderee"), (20, "forte")])
def test_rain_category(r, c):
    assert rainCategory(r) == c


@pytest.mark.parametrize("w,c", [(10, "calme"), (20, "modere"), (40, "fort"), (60, "violent")])
def test_wind_category(w, c):
    assert windSpeedCategory(w) == c


def test_calm_day_scores_zero():
    assert riskScore(row()) == 0


def test_each_factor_matches_readme_table():
    assert riskScore(row(rain=20)) == 30
    assert riskScore(row(rain=5)) == 10
    assert riskScore(row(rain=1)) == 5
    assert riskScore(row(gust=80)) == 20
    assert riskScore(row(temp=45)) == 15
    assert riskScore(row(temp=0)) == 8
    assert riskScore(row(prob=70)) == 10
    assert riskScore(row(wind=60)) == 25


def test_score_is_capped_at_100():
    assert riskScore(row(rain=50, gust=100, temp=46, prob=90, wind=80)) == 100


def test_works_on_dataframe_apply():
    df = pd.DataFrame([row(), row(rain=25)])
    assert df.apply(riskScore, axis=1).tolist() == [0, 30]
