"""
data.py - hourly London weather from the Open-Meteo historical archive
(ERA5 reanalysis, CC BY 4.0), 2010 to 2024. Downloaded once into data/.

One record per day is kept: the reading at noon, so "sunny" means sunny in
daylight. Each record's weather code (the WMO standard) is grouped into
sunny, cloudy or rainy. Fog and snow are rare in London and fit none of
the three, so those records are dropped.

Open-Meteo works the weather code out from cloud cover and rain, so those
two are not used as inputs; the model has to infer the weather from the
air itself.
"""

import json
import os

import pandas as pd

from pxlab.common import DATA_FOLDER, download_once

WEATHER_URL = (
    "https://archive-api.open-meteo.com/v1/archive?latitude=51.51&longitude=-0.13"
    "&start_date=2010-01-01&end_date=2024-12-31&timezone=Europe%2FLondon"
    "&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m,pressure_msl,weather_code"
)

# WMO weather codes grouped into the three classes of the brief.
CONDITIONS = {
    0: "sunny",  # clear sky
    1: "sunny",  # mainly clear
    2: "cloudy",  # partly cloudy
    3: "cloudy",  # overcast
    51: "rainy",  # drizzle: light, moderate, dense
    53: "rainy",
    55: "rainy",
    61: "rainy",  # rain: slight, moderate, heavy
    63: "rainy",
    65: "rainy",
    80: "rainy",  # rain showers
    81: "rainy",
    82: "rainy",
    95: "rainy",  # thunderstorm
}


def load_weather():
    """
    Noon weather records in date order, with the condition to predict.

    Returns:
        A DataFrame with "date", the inputs, "month" and "condition".
    """
    path = download_once(WEATHER_URL, os.path.join(DATA_FOLDER, "weather_london_hourly.json"))
    with open(path, encoding="utf-8") as file:
        hourly = json.load(file)["hourly"]
    frame = pd.DataFrame(hourly).rename(
        columns={
            "time": "time",
            "temperature_2m": "temperature",
            "relative_humidity_2m": "humidity",
            "wind_speed_10m": "wind_speed",
            "pressure_msl": "pressure",
        }
    )
    frame["time"] = pd.to_datetime(frame["time"])
    # Pressure falling over the morning is a classic sign of rain coming.
    frame["pressure_change"] = (frame["pressure"] - frame["pressure"].shift(6)).round(1)
    frame = frame[frame["time"].dt.hour == 12].copy()
    frame["date"] = frame["time"].dt.date
    frame["month"] = frame["time"].dt.month
    frame["condition"] = frame["weather_code"].map(CONDITIONS)
    frame = frame.dropna(subset=["condition"])
    columns = ["date", "temperature", "humidity", "wind_speed", "pressure", "pressure_change", "month", "condition"]
    return frame[columns].reset_index(drop=True)
