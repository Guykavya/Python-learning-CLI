import re

import numpy as np
import pandas as pd
import pytest

from conftest import STATIONS
from solution import clean_air

COLS = ["station", "ts", "pm25", "humidity", "pm25_flag"]


@pytest.fixture(scope="module")
def result(air):
    truth, raw, injected = air
    return clean_air(raw)


@pytest.fixture(scope="module")
def merged(air, result):
    truth, raw, injected = air
    clean = result[0]
    m = clean.merge(truth, on=["station", "ts"], suffixes=("", "_true"))
    return m.merge(injected[["station", "ts", "raw_pm25"]], on=["station", "ts"])


def test_shape_of_the_clean_table(air, result):
    clean = result[0]
    assert list(clean.columns) == COLS, "columns must be %s, got %s." % (COLS, list(clean.columns))
    assert len(clean) == 3 * 45 * 24, "one row per station and hour: 3 x 1080 = 3240 rows. Got %d (duplicates left, or rows lost?)." % len(clean)
    assert set(clean["station"]) == set(STATIONS), "station names must be canonical: %s." % sorted(set(clean["station"]))
    assert pd.api.types.is_datetime64_any_dtype(clean["ts"]), "ts must be a datetime column."
    assert clean.index.tolist() == list(range(len(clean))), "the index must be 0, 1, 2, ..."
    keys = list(zip(clean["station"], clean["ts"]))
    assert keys == sorted(keys), "sort by station, then ts."
    assert not clean.duplicated(["station", "ts"]).any(), "one row per station and hour."


def test_flag_and_value_agree(result):
    clean = result[0]
    assert set(clean["pm25_flag"]) <= {"ok", "code", "spike", "stuck", "missing"}, "unknown flag values: %s." % set(clean["pm25_flag"])
    assert (clean["pm25"].notna() == (clean["pm25_flag"] == "ok")).all(), "pm25 is present exactly when the flag is 'ok': a removed value keeps its reason."
    assert clean["pm25"].dropna().between(0, 500).all()


def test_known_truth_no_wrong_value_survives(merged):
    ok = merged[merged["pm25_flag"] == "ok"]
    wrong = ok[ok["pm25"] != ok["pm25_true"]]
    assert len(wrong) <= 1, (
        "%d readings marked 'ok' differ from the truth (at most one spike just under the 3-times line is tolerated). "
        "First: %s" % (len(wrong), wrong[["station", "ts", "pm25", "pm25_true"]].head(3).to_dict("records")))


def test_spikes_are_found_and_honest_values_are_kept(merged):
    sp = merged[merged["pm25_flag"] == "spike"]
    assert len(sp) >= 8, "10 spikes were injected (a few were hidden by -999 or a gap first): at least 8 'spike' flags expected, got %d." % len(sp)
    honest = sp[sp["raw_pm25"] == sp["pm25_true"]]
    assert len(honest) == 0, "honest readings were flagged as spikes: %s. Is the rule relative to the neighbours (3 x the rolling median)?" % (
        honest[["station", "ts", "pm25_true"]].head(3).to_dict("records"))


def test_the_stuck_run_is_flagged(merged):
    st = merged[merged["pm25_flag"] == "stuck"]
    assert len(st) >= 30, "the Hill Road sensor repeated 41.0 for 36 hours: at least 30 'stuck' flags expected, got %d." % len(st)
    assert set(st["station"]) == {"Hill Road"}, "only Hill Road was stuck, but 'stuck' was flagged at %s." % sorted(set(st["station"]))
    assert st["ts"].between(pd.Timestamp("2025-03-10 06:00"), pd.Timestamp("2025-03-11 17:00")).all(), "stuck flags outside the stuck window."


def test_codes_and_flag_counts(air, result):
    truth, raw, injected = air
    clean, flags = result[0], result[1]
    n_codes = int((raw.drop_duplicates()["pm25"] == -999).sum())
    assert flags.get("code") == n_codes, "the -999 codes of the unique rows must all be flagged 'code': expected %d, got %s." % (n_codes, flags.get("code"))
    assert flags == clean["pm25_flag"].value_counts().to_dict(), "flags is the dict of final flag counts."
    assert all(type(v) is int for v in flags.values()), "plain int counts."
    assert sum(flags.values()) == len(clean)


def test_log_is_a_trail_you_can_follow(air, result):
    truth, raw, injected = air
    clean, log = result[0], result[2]
    assert len(log) >= 4, "at least four steps: formats, duplicates, suspects, validate. Got %d log entries." % len(log)
    for r in log:
        assert {"step", "rows_before", "rows_after", "na_before", "na_after", "note"} <= set(r), "log entry keys missing: %s." % sorted(r)
    assert log[0]["rows_before"] == len(raw), "the first step starts from the raw table (%d rows)." % len(raw)
    for a, b in zip(log, log[1:]):
        assert b["rows_before"] == a["rows_after"], "each step starts where the previous one ended."
    assert log[-1]["rows_after"] == len(clean)
    assert len(raw) - len(clean) == 40, "exactly the 40 repeated rows disappear."
    dup = [r for r in log if r["rows_after"] < r["rows_before"]]
    assert len(dup) == 1 and dup[0]["rows_before"] - dup[0]["rows_after"] == 40, "one step removes the 40 duplicates and says so."


def test_bad_rows_are_quarantined_not_crashing(air):
    truth, raw, injected = air
    bad_humidity = raw.iloc[[0]].copy()
    bad_humidity[["station", "ts", "pm25", "humidity"]] = ["Airport", "20/04/2025 05:00", 30.0, 150.0]
    bad_format = raw.iloc[[1]].copy()
    bad_format[["station", "ts", "pm25", "humidity"]] = ["Riverside", "2025-04-20T05:00", 30.0, 50.0]
    clean, flags, log, report = clean_air(pd.concat([raw, bad_humidity, bad_format], ignore_index=True))
    assert len(clean) == 3240, "the two bad rows (humidity 150; a timestamp in a third format) must be quarantined, got %d rows." % len(clean)
    assert clean["humidity"].max() <= 100
    assert log[-1]["rows_before"] - log[-1]["rows_after"] == 2, "the validate step must show the 2 quarantined rows in its row counts."


def test_deterministic_and_input_not_changed(air, result):
    truth, raw, injected = air
    before = raw.copy()
    again = clean_air(raw)
    pd.testing.assert_frame_equal(raw, before, obj="the raw table (never change the raw data)")
    pd.testing.assert_frame_equal(again[0], result[0], obj="two runs on the same raw table")
    assert again[2] == result[2], "the log must be the same on every run (no global state)."


def test_report_names_both_answers_and_b_is_closer(air, result):
    truth, raw, injected = air
    clean, report = result[0], result[3]
    assert isinstance(report, str) and "humidity" in report and "MAR" in report, "the report must say that missingness depends on humidity (MAR)."
    lines = re.findall(r"^(.+?) \| A: (-?[\d.]+) \| B: (-?[\d.]+)\s*$", report, flags=re.M)
    got = {st: (float(a), float(b)) for st, a, b in lines}
    assert set(got) == set(STATIONS), "one line per station in the form '<station> | A: <x> | B: <y>'. Found %s." % sorted(got)
    way_a = clean.groupby("station")["pm25"].mean()
    true_mean = truth.groupby("station")["pm25"].mean()
    err_a, err_b = 0.0, 0.0
    for st, (a, b) in got.items():
        assert abs(a - way_a[st]) < 0.06, "A for %s must be the mean of the existing readings after dropping the missing ones (%.1f), got %.1f." % (st, way_a[st], a)
        assert b > a + 0.2, "B repairs the foggy (dusty) hours, so it must be clearly higher than A for %s: A %.1f, B %.1f." % (st, a, b)
        err_a += abs(a - true_mean[st])
        err_b += abs(b - true_mean[st])
    assert err_b < err_a, "B must be closer to the truth than A overall (errors A %.2f, B %.2f)." % (err_a, err_b)
    for r in result[2]:
        assert r["step"] in report, "the report lists the steps of the log (missing: %s)." % r["step"]
