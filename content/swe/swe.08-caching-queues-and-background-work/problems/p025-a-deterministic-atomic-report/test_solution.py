import os

import pytest

from solution import build_report, write_atomic

ROWS = [(3, "cy", 990), (1, "ada", 2500), (2, "bo", 4200)]
EXPECTED = b"month,order_id,customer,total_cents\n2026-10,1,ada,2500\n2026-10,2,bo,4200\n2026-10,3,cy,990\n"


def test_report_content():
    assert build_report(ROWS, "2026-10") == EXPECTED, \
        "Header 'month,order_id,customer,total_cents', then rows sorted by order_id, '\\n' line endings, as bytes."


def test_report_is_deterministic():
    shuffled = [ROWS[2], ROWS[0], ROWS[1]]
    assert build_report(shuffled, "2026-10") == build_report(ROWS, "2026-10"), "The same rows in any order must give the same bytes: sort them."
    assert build_report(ROWS, "2026-10") == build_report(ROWS, "2026-10"), "No time or random value may appear in the report."


def test_report_quotes_and_unicode():
    data = build_report([(1, "Smith, Jo", 100), (2, "Zoë", 5)], "2026-11")
    assert data.decode("utf-8").splitlines() == ["month,order_id,customer,total_cents", '2026-11,1,"Smith, Jo",100', "2026-11,2,Zoë,5"], \
        "Use csv.writer so a comma inside a name is quoted, and encode the text as UTF-8."


def test_empty_report():
    assert build_report([], "2026-10") == b"month,order_id,customer,total_cents\n", "No rows: just the header."


def test_atomic_write(tmp_path):
    path = str(tmp_path / "report.csv")
    write_atomic(path, EXPECTED)
    assert open(path, "rb").read() == EXPECTED
    assert [f for f in os.listdir(tmp_path) if f.endswith(".tmp")] == [], "After a successful write no .tmp file may remain (os.replace moves it)."


@pytest.mark.parametrize("point", ["mid-write", "before-replace"])
def test_crash_keeps_the_old_file(tmp_path, crash_at, crash_type, point):
    path = str(tmp_path / "report.csv")
    old = b"month,order_id,customer,total_cents\n2026-10,1,ada,1\n"
    with open(path, "wb") as f:
        f.write(old)
    with pytest.raises(crash_type):
        write_atomic(path, EXPECTED, crash_at(point))
    assert open(path, "rb").read() == old, \
        f"A crash at {point!r} must leave the OLD complete file. Write to a temporary file, then os.replace it onto the final name."
    leftovers = [f for f in os.listdir(tmp_path) if f.endswith(".tmp")]
    assert leftovers, "The temporary file must be in the SAME folder as the report and end in '.tmp'."


@pytest.mark.parametrize("point", ["mid-write", "before-replace"])
def test_crash_with_no_old_file(tmp_path, crash_at, crash_type, point):
    path = str(tmp_path / "report.csv")
    with pytest.raises(crash_type):
        write_atomic(path, EXPECTED, crash_at(point))
    assert not os.path.exists(path), f"A crash at {point!r} must not leave a half-written report under the final name."


def test_retry_after_crash_and_duplicate_run(tmp_path, crash_at, crash_type):
    path = str(tmp_path / "report.csv")
    with pytest.raises(crash_type):
        write_atomic(path, EXPECTED, crash_at("mid-write"))
    write_atomic(path, EXPECTED)                     # the retry
    first = open(path, "rb").read()
    write_atomic(path, build_report(list(reversed(ROWS)), "2026-10"))      # a duplicate run
    assert open(path, "rb").read() == first == EXPECTED, "A retry and a duplicate run produce identical bytes."


def test_crash_points_are_used(tmp_path):
    seen = []

    class Recorder:
        def hit(self, name):
            seen.append(name)

    write_atomic(str(tmp_path / "r.csv"), EXPECTED, Recorder())
    assert seen == ["mid-write", "before-replace"], f"Call crash.hit('mid-write') between the halves and crash.hit('before-replace') before os.replace; got {seen}"
