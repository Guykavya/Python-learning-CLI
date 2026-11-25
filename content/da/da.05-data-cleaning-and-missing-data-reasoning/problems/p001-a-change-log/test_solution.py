import pandas as pd

from solution import log_step, show_log

HEADER = "step | rows_before | rows_after | dropped | note"


def frame(n):
    return pd.DataFrame({"id": list(range(n))})


def test_entry_has_exactly_the_five_keys():
    log = []
    log_step(log, "drop repeats", frame(4), frame(3), "whole row repeated")
    assert len(log) == 1, "log_step must append exactly one entry per call."
    assert sorted(log[0]) == ["dropped", "note", "rows_after", "rows_before", "step"], (
        "the entry must have exactly the keys step, rows_before, rows_after, dropped, note. Got %s." % sorted(log[0]))
    assert log[0] == {"step": "drop repeats", "rows_before": 4, "rows_after": 3, "dropped": 1,
                      "note": "whole row repeated"}, "wrong values in the entry: %s" % log[0]


def test_note_defaults_to_empty_text():
    log = []
    log_step(log, "x", frame(2), frame(2))
    assert log[0]["note"] == "", "when no note is given, the note must be an empty string."


def test_returns_after_so_steps_chain():
    log = []
    before, after = frame(5), frame(2)
    out = log_step(log, "filter", before, after)
    assert out is after, "return the `after` frame itself (not a copy, not None) so steps can be chained."


def test_dropped_is_never_negative():
    log = []
    log_step(log, "merge adds rows", frame(3), frame(7))
    assert log[0]["rows_before"] == 3 and log[0]["rows_after"] == 7
    assert log[0]["dropped"] == 0, (
        "a step that ADDS rows dropped nothing: dropped must be 0, not %s. Use max(0, ...)." % log[0]["dropped"])


def test_frames_are_not_changed():
    before, after = frame(4), frame(3)
    log_step([], "s", before, after)
    assert len(before) == 4 and len(after) == 3, "log_step must only read the frames, never change them."


def test_several_steps_keep_their_order():
    log = []
    df = frame(10)
    df = log_step(log, "load", df, df, "start")
    df = log_step(log, "filter", df, df.iloc[:7], "age rule")
    df = log_step(log, "dedupe", df, df.iloc[:6])
    assert [e["step"] for e in log] == ["load", "filter", "dedupe"], "entries must stay in the order the steps ran."
    assert [e["dropped"] for e in log] == [0, 3, 1]


def test_show_log_text_format():
    log = []
    df = frame(4)
    df = log_step(log, "load raw", df, df, "start")
    df = log_step(log, "drop repeats", df, df.iloc[:3], "whole row repeated")
    want = "\n".join([HEADER, "load raw | 4 | 4 | 0 | start", "drop repeats | 4 | 3 | 1 | whole row repeated"])
    got = show_log(log)
    assert isinstance(got, str), "show_log must RETURN a string, not print it or return a frame."
    assert got == want, "text differs.\nexpected:\n%s\ngot:\n%s" % (want, got)


def test_show_log_empty_log_is_only_the_header():
    assert show_log([]) == HEADER, "an empty log gives just the header line, with no newline at the end."


def test_show_log_empty_note_keeps_the_last_separator():
    log = []
    log_step(log, "x", frame(2), frame(1))
    assert show_log(log).split("\n")[1] == "x | 2 | 1 | 1 | ", (
        "an empty note still gives 'x | 2 | 1 | 1 | ' (the separator and an empty last field).")
