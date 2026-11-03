import logging

import pytest

from solution import process_batch


def fake_clock(*values):
    values = list(values)
    calls = []

    def clock():
        calls.append(1)
        return values[min(len(calls), len(values)) - 1]

    clock.calls = calls
    return clock


def order(id_, amount, email="asha@example.com"):
    return {"id": id_, "customer": {"email": email, "city": "Pune"}, "status": "shipped",
            "amount": amount, "currency": "INR", "updated_at": "2024-06-01T12:00:00Z"}


def pipeline_lines(caplog, level=None):
    return [(r.levelname, r.getMessage()) for r in caplog.records
            if r.name == "pipeline" and (level is None or r.levelname == level)]


@pytest.fixture
def logs(caplog):
    caplog.set_level(logging.DEBUG, logger="pipeline")
    return caplog


def test_example_from_the_statement(logs):
    records = [order(101, "19.99"), order(102, "-5", "ravi@example.com"),
               order("103", "7.00", "meera@example.com")]
    loaded = []
    result = process_batch(records, loaded.append, run_id="a1b2c3d4", clock=fake_clock(100.0, 100.25))
    assert result == {"run_id": "a1b2c3d4", "read": 3, "loaded": 1, "skipped": 2, "duration": 0.25}, (
        f"Returned {result}. read = all records, loaded = passed to sink, skipped = invalid, "
        "duration = second clock() minus first."
    )
    assert loaded == [records[0]], "Only the valid record (101) goes to the sink, unchanged."
    info = pipeline_lines(logs, "INFO")
    assert info == [("INFO", "run a1b2c3d4 started: 3 records"),
                    ("INFO", "run a1b2c3d4 finished: read=3 loaded=1 skipped=2 duration=0.250s")], (
        f"INFO lines were {info}. Expected exactly the start line and the summary line, in the "
        "given format (duration with 3 decimals and an 's')."
    )
    warnings = pipeline_lines(logs, "WARNING")
    assert warnings == [("WARNING", "run a1b2c3d4 skipped record id=102: bad amount"),
                        ("WARNING", "run a1b2c3d4 skipped record id='103': bad id")], (
        f"WARNING lines were {warnings}. One per skipped record: the id (with %r, so the string "
        "'103' shows its quotes) and the reason."
    )


def test_no_customer_data_in_the_logs(logs):
    records = [order(1, "x", "secret.person@example.com"), order(-1, "1.00", "other@example.com"),
               order(2, "1.00", "fine@example.com")]
    process_batch(records, lambda r: None, run_id="r1", clock=fake_clock(0.0, 1.0))
    text = "\n".join(msg for _, msg in pipeline_lines(logs))
    assert "@" not in text and "secret.person" not in text, (
        "An email address appeared in the logs. Log only the id and the reason, never the "
        "record or the customer."
    )
    assert "Pune" not in text, "Do not log the record (or any customer field) at all."


def test_never_prints(logs, capsys):
    process_batch([order(1, "2.00"), order(0, "2.00")], lambda r: None, run_id="r1", clock=fake_clock(0.0, 0.0))
    out = capsys.readouterr()
    assert out.out == "" and out.err == "", "Use the logger, never print()."


def test_uses_the_pipeline_logger(caplog):
    caplog.set_level(logging.INFO)
    process_batch([order(1, "2.00")], lambda r: None, run_id="r9", clock=fake_clock(0.0, 0.0))
    names = {r.name for r in caplog.records}
    assert names == {"pipeline"}, (
        f"Log records came from {names}. Use logging.getLogger('pipeline'), not the root logger "
        "(logging.info(...)) and not __name__."
    )


def test_generated_run_ids_differ_and_tag_every_line(logs):
    a = process_batch([order(1, "1.00")], lambda r: None, clock=fake_clock(0.0, 0.0))
    b = process_batch([order(1, "1.00")], lambda r: None, clock=fake_clock(0.0, 0.0))
    assert isinstance(a["run_id"], str) and len(a["run_id"]) == 8, (
        f"run_id {a['run_id']!r}: when none is given, generate uuid.uuid4().hex[:8]."
    )
    assert a["run_id"] != b["run_id"], "Two runs got the same run_id; generate a new one per call."
    lines = pipeline_lines(logs)
    assert len(lines) == 4 and all(a["run_id"] in m for _, m in lines[:2]) and all(
        b["run_id"] in m for _, m in lines[2:]), (
        "Every line of a run must contain that run's id, so you can grep one run out of the logs."
    )


def test_clock_is_called_twice_and_duration_formatted(logs):
    clock = fake_clock(12.0, 13.23456)
    result = process_batch([order(i, "1.00") for i in range(1, 6)], lambda r: None, run_id="z", clock=clock)
    assert len(clock.calls) == 2, f"clock() was called {len(clock.calls)} times; call it once at start, once at end."
    assert result["duration"] == pytest.approx(1.23456), "duration is end - start, unrounded in the dict."
    summary = pipeline_lines(logs, "INFO")[-1][1]
    assert summary == "run z finished: read=5 loaded=5 skipped=0 duration=1.235s", (
        f"Summary was {summary!r}. Round only in the message, with %.3f."
    )


def test_one_summary_line_for_a_big_batch(logs):
    records = [order(i, f"{i}.50") for i in range(1, 1001)]
    count = []
    process_batch(records, count.append, run_id="big", clock=fake_clock(0.0, 2.0))
    assert len(count) == 1000
    info = pipeline_lines(logs, "INFO")
    assert len(info) == 2, (
        f"{len(info)} INFO lines for 1000 records. Only start + summary are INFO; per-record "
        "lines (if any) belong at DEBUG."
    )


def test_validation_rules(logs):
    records = [
        order(True, "1.00"),        # bool is not an id
        order(0, "1.00"),           # not > 0
        order(None, "1.00"),
        order(5, 3.5),              # amount must be a string
        order(6, "abc"),
        order(7, None),
        order(8, "-0.01"),
        order(9, "0"),              # zero is allowed
        order(10, "1e3"),           # Decimal understands this
    ]
    loaded = []
    result = process_batch(records, loaded.append, run_id="v", clock=fake_clock(0.0, 0.0))
    assert [r["id"] for r in loaded] == [9, 10], (
        f"Loaded ids {[r['id'] for r in loaded]}; only 9 ('0') and 10 ('1e3') are valid. "
        "True is a bool (isinstance(True, int) is True!), 0 is not > 0, 3.5 is not a string."
    )
    reasons = [m.split(": ")[-1] for _, m in pipeline_lines(logs, "WARNING")]
    assert reasons == ["bad id"] * 3 + ["bad amount"] * 4, f"Reasons were {reasons}."
    assert result["skipped"] == 7 and result["loaded"] == 2


def test_sink_failure_logs_an_error_and_reraises(logs):
    def sink(record):
        if record["id"] == 3:
            raise RuntimeError("disk full")
    with pytest.raises(RuntimeError):
        process_batch([order(i, "1.00") for i in range(1, 6)], sink, run_id="f1", clock=fake_clock(0.0, 1.0))
    errors = pipeline_lines(logs, "ERROR")
    assert errors == [("ERROR", "run f1 failed after 2 loaded: RuntimeError")], (
        f"ERROR lines were {errors}. Log 'run <id> failed after <loaded> loaded: <class name>' "
        "and then re-raise."
    )
    assert not [m for _, m in pipeline_lines(logs, "INFO") if "finished" in m], (
        "A failed run must not log 'finished'; the summary would lie."
    )


def test_empty_batch(logs):
    result = process_batch([], lambda r: None, run_id="e", clock=fake_clock(5.0, 5.0))
    assert result == {"run_id": "e", "read": 0, "loaded": 0, "skipped": 0, "duration": 0.0}
    assert pipeline_lines(logs, "INFO")[-1][1] == "run e finished: read=0 loaded=0 skipped=0 duration=0.000s"
