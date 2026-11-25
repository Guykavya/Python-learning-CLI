"""A trimmed copy of the chapter's make_air (3 stations, 45 days), plus the truth and a table of the injected problems."""
import numpy as np
import pandas as pd
import pytest

STATIONS = ["Hill Road", "Riverside", "Airport"]


def make_air(seed=21, days=45):
    rng = np.random.default_rng(seed)
    hours = pd.date_range("2025-03-01", periods=days * 24, freq="h")
    frames = []
    for st, base in zip(STATIONS, [70, 40, 35]):
        h = hours.hour.values
        hum = np.clip(60 + 25 * np.sin((h - 4) / 24 * 2 * np.pi) + rng.normal(0, 8, len(hours)), 20, 100).round(0)
        pm = base + 0.6 * (hum - 60) + 12 * np.sin((h - 8) / 24 * 2 * np.pi) + rng.normal(0, 6, len(hours))
        frames.append(pd.DataFrame({"station": st, "ts": hours, "pm25": np.clip(pm, 2, None).round(1), "humidity": hum}))
    truth = pd.concat(frames, ignore_index=True)

    raw = truth.copy()
    pm = raw["pm25"].copy()
    pm[(raw["humidity"] > 85) & (rng.random(len(raw)) < .5)] = np.nan                                       # fog: MAR
    pm[(raw["station"] == "Riverside") & (raw["ts"] >= "2025-03-21") & (raw["ts"] < "2025-03-24")] = np.nan  # outage
    pm[(raw["station"] == "Hill Road") & (raw["ts"] >= "2025-03-10 06:00") & (raw["ts"] < "2025-03-11 18:00")] = 41.0  # stuck
    spikes = rng.choice(len(raw), 10, replace=False)
    pm.iloc[spikes] = pm.iloc[spikes] * 8
    pm[rng.random(len(raw)) < .03] = -999
    raw["pm25"] = pm
    injected = truth.assign(raw_pm25=pm.to_numpy())          # what the logger really wrote, by true station and hour

    ts = raw["ts"].dt.strftime("%Y-%m-%d %H:%M")
    raw["ts"] = np.where(raw["station"] == "Airport", raw["ts"].dt.strftime("%d/%m/%Y %H:%M"), ts)
    spell = {"Riverside": ["Riverside", "RIVERSIDE", "riverside "],
             "Hill Road": ["Hill Road", "hill-road", "HILL ROAD "], "Airport": ["Airport", "airport", "AIRPORT "]}
    pick = rng.choice(3, len(raw), p=[.7, .15, .15])
    raw["station"] = [spell[s][i] for s, i in zip(raw["station"], pick)]
    raw = pd.concat([raw, raw.sample(40, random_state=4)], ignore_index=True)
    return truth, raw, injected


@pytest.fixture(scope="module")
def air():
    return make_air()
