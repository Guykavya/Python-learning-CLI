## Approach

Each step is a small function from DataFrame to DataFrame, so it can be tested alone, and one helper writes a log line
(rows and missing cells before and after, plus a note). The new idea of the project is the **reason column**
`pm25_flag`: the value becomes missing, but the story (`code`, `spike`, `stuck`, `missing`) stays. The report is
**generated from the same numbers** as the code, so it cannot disagree with it.

The two decisions worth defending (chapter 13.3): the spike rule is **relative to the neighbours**, not to the whole
table (150 is a spike on a quiet night and plausible on a polluted one); and the stuck rule counts **runs** (one repeated
value is fine, six in a row is a fault). The chapter's rule leaves one injected spike untouched, because it sits just
below the 3-times line: **a rule is a judgement**, and the test tolerates that one miss on purpose.

## Code

```python
import numpy as np
import pandas as pd
import pandera.pandas as pa

FLAGS = ["ok", "code", "spike", "stuck", "missing"]
LIMIT = 60.0


def _na(df):
    return int(df.isna().sum().sum())


def _formats(df):
    out = df.copy()
    out["station"] = out["station"].str.strip().str.replace("-", " ", regex=False).str.title()
    is_iso = out["ts"].str.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
    is_dmy = out["ts"].str.fullmatch(r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}")
    iso = pd.to_datetime(out["ts"].where(is_iso), format="%Y-%m-%d %H:%M", errors="coerce")
    dmy = pd.to_datetime(out["ts"].where(is_dmy), format="%d/%m/%Y %H:%M", errors="coerce")
    out["ts"] = iso.fillna(dmy)
    out["pm25_flag"] = np.where(out["pm25"] == -999, "code", np.where(out["pm25"].isna(), "missing", "ok"))
    out["pm25"] = out["pm25"].mask(out["pm25"] == -999)
    return out


def _duplicates(df):
    return df.drop_duplicates(subset=["station", "ts"], keep="first").sort_values(["station", "ts"]).reset_index(drop=True)


def _suspects(df, spike_ratio=3.0, stuck_hours=6, hi=500):
    out = df.copy()
    g = out.groupby("station")["pm25"]
    neighbours = g.transform(lambda s: s.rolling(7, center=True, min_periods=3).median())
    spike = ((out["pm25"] > spike_ratio * neighbours) | (out["pm25"] > hi)).fillna(False)
    same = out["pm25"].eq(g.shift())
    run_id = (~same).groupby(out["station"]).cumsum()
    run_len = out.groupby(["station", run_id])["pm25"].transform("size")
    stuck = out["pm25"].notna() & (run_len >= stuck_hours)
    out.loc[spike, "pm25_flag"] = "spike"
    out.loc[stuck, "pm25_flag"] = "stuck"
    out["pm25"] = out["pm25"].mask(out["pm25_flag"].isin(["spike", "stuck"]))
    return out


def _schema(stations):
    return pa.DataFrameSchema(
        {
            "station": pa.Column(str, pa.Check.isin(list(stations))),
            "ts": pa.Column("datetime64[ns]", coerce=True),
            "pm25": pa.Column(float, pa.Check.in_range(0, 500), nullable=True),
            "humidity": pa.Column(float, pa.Check.in_range(0, 100), nullable=True),
            "pm25_flag": pa.Column(str, pa.Check.isin(FLAGS)),
        },
        unique=["station", "ts"], strict=True,
        checks=[pa.Check(lambda d: d["pm25"].notna() == (d["pm25_flag"] == "ok"), error="pm25 present <=> flag is ok")],
    )


def _quarantine(df, schema):
    try:
        schema.validate(df, lazy=True)
    except pa.errors.SchemaErrors as e:
        fc = e.failure_cases
        if fc["index"].isna().any():
            raise
        bad = df.index.isin(fc["index"])
        return df[~bad].reset_index(drop=True), int(bad.sum())
    return df, 0


def _repair(clean):
    b = clean.copy()
    for st, g in b.groupby("station"):
        s = g.set_index("ts")["pm25"].interpolate(method="time", limit=3, limit_area="inside")
        b.loc[g.index, "pm25"] = s.to_numpy()
    rest = b["pm25"].isna() & b["humidity"].notna()
    fitted = {}
    for st, g in b[b["pm25"].notna()].groupby("station"):
        fitted[st] = np.polyfit(g["humidity"], g["pm25"], 1)
    b.loc[rest, "pm25"] = [fitted[s][0] * h + fitted[s][1] for s, h in zip(b.loc[rest, "station"], b.loc[rest, "humidity"])]
    return b


def clean_air(raw, stations=("Hill Road", "Riverside", "Airport")):
    log = []

    def step(name, before, after, note):
        log.append({"step": name, "rows_before": len(before), "rows_after": len(after),
                    "na_before": _na(before), "na_after": _na(after), "note": note})
        return after

    t1 = step("formats", raw, _formats(raw), "names, timestamps, -999 -> missing")
    t2 = step("duplicates", t1, _duplicates(t1), "same station + hour: first copy kept")
    t3 = step("suspects", t2, _suspects(t2), "spikes and stuck runs -> missing, reason kept")
    t4, n_bad = _quarantine(t3, _schema(stations))
    clean = step("validate", t3, t4, f"{n_bad} rows quarantined")
    flags = {k: int(v) for k, v in clean["pm25_flag"].value_counts().items()}

    way_a = clean.groupby("station")["pm25"].mean()
    way_b = _repair(clean).groupby("station")["pm25"].mean()

    lines = ["# Air quality: cleaning report", "", "### Steps"]
    for r in log:
        lines.append(f"- **{r['step']}**: {r['rows_before']} -> {r['rows_after']} rows; "
                     f"missing cells {r['na_before']} -> {r['na_after']}. {r['note']}.")
    lines += ["", "### Why pm25 is missing (after cleaning)"]
    lines += [f"- {k}: {v}" for k, v in flags.items()]
    lines += ["", "### Missing-data decision",
              "Missingness depends on humidity (above 85 percent about half of the readings fail): MAR.",
              "Way A drops the missing hours. Way B interpolates gaps up to 3 hours, then predicts from humidity.",
              "", "### Mean PM2.5 (ug/m3) by station"]
    for st in way_a.index:
        lines.append(f"{st} | A: {way_a[st]:.1f} | B: {way_b[st]:.1f}")
    return clean, flags, log, "\n".join(lines)
```

## Complexity

O(n log n) for the sorts, O(n) for the rolling medians, runs and fits (3,280 rows runs in well under a second).

## Another way

Make the thresholds parameters of `clean_air` (3 times, 6 hours, 3 hours of interpolation) so that the report prints
them: a threshold that is visible can be challenged. Replace the humidity line by a regression with more predictors,
or by several random fills (chapter 9.5) to show the spread of answer B. Keep answer A next to it either way: the
honest result of the project is the pair, and the gap.
