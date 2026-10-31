import dataclasses
from pathlib import Path

from solution import LogEntry, parse_line, summarise

FIXTURE = Path(__file__).parent / "fixtures" / "app.log"


def entry(ts, level, module, message):
    return LogEntry(timestamp=ts, level=level, module=module, message=message)


# ---------- Part 1: parse_line ----------

def test_logentry_is_dataclass():
    assert dataclasses.is_dataclass(LogEntry), "LogEntry should be a @dataclass."
    names = [f.name for f in dataclasses.fields(LogEntry)]
    assert names == ["timestamp", "level", "module", "message"], f"LogEntry fields must be timestamp, level, module, message in that order; got {names}."


def test_format_a_basic():
    got = parse_line("2025-03-01 09:01:16,001 ERROR [payments] Card declined for order 17")
    assert got == entry("2025-03-01 09:01:16", "ERROR", "payments", "Card declined for order 17"), "Format A: date, time (drop ',mmm'), level, [module], message. Use named groups and build a LogEntry."


def test_format_a_without_millis():
    got = parse_line("2025-03-01 09:02:00 ERROR [db.pool] Connection lost: timeout after 30s")
    assert got == entry("2025-03-01 09:02:00", "ERROR", "db.pool", "Connection lost: timeout after 30s"), "The milliseconds ',mmm' are optional: (?:,\\d{3})?. Module names may contain dots: [\\w.]+."


def test_format_b_basic():
    got = parse_line("[2025-03-01T09:01:17] ERROR payments: Retry failed for order 17")
    assert got == entry("2025-03-01 09:01:17", "ERROR", "payments", "Retry failed for order 17"), "Format B: [dateTtime] level module: message. The timestamp is normalised with a SPACE instead of T."


def test_level_case_and_warn():
    assert parse_line("[2025-03-01T09:02:01] WARN db.pool: Reconnecting").level == "WARNING", "WARN is stored as WARNING."
    assert parse_line("2025-03-01 09:02:03,120 error [auth] Invalid token").level == "ERROR", "Levels are case-insensitive (re.IGNORECASE) and stored upper-case."
    assert parse_line("[2025-03-01T09:00:02] info auth: ok").level == "INFO", "Lower-case levels in format B too."
    assert parse_line("2025-03-01 09:00:00 Warning [x] w").level == "WARNING", "'Warning' in mixed case is WARNING."


def test_unknown_level_rejected():
    assert parse_line("2025-03-01 09:02:04,500 VERBOSE [app] nope") is None, "Only DEBUG, INFO, WARNING, WARN, ERROR, CRITICAL are levels. Use an alternation, not \\w+."
    assert parse_line("2025-03-01 09:02:04 INFORMATION [app] nope") is None, "'INFORMATION' is not 'INFO': the level must be followed by whitespace, not more letters."


def test_strip_and_message_spaces():
    got = parse_line("2025-03-01 09:01:16,001 error [payments]  Card declined  \n")
    assert got == entry("2025-03-01 09:01:16", "ERROR", "payments", "Card declined"), "Strip the line (newline, trailing spaces) and strip the message."


def test_empty_message():
    assert parse_line("2025-03-01 09:03:15,001 INFO [app]") == entry("2025-03-01 09:03:15", "INFO", "app", ""), "The message is optional: no message gives ''. Make ' message' an optional group and use '' for None."
    assert parse_line("[2025-03-01T09:03:15] INFO app:") == entry("2025-03-01 09:03:15", "INFO", "app", ""), "Format B with no message gives '' too."


def test_message_may_contain_brackets_and_colons():
    got = parse_line("2025-03-01 09:03:16,002 INFO [notifications.email] Sent 12 emails: [ok] done")
    assert got == entry("2025-03-01 09:03:16", "INFO", "notifications.email", "Sent 12 emails: [ok] done"), "The module is the FIRST [ ... ]; the message is everything after it, brackets and colons included."


def test_garbage_lines():
    bad = [
        "Traceback (most recent call last):",
        '  File "app/payments.py", line 88, in charge',
        "-- end of log --",
        "2025-3-01 09:03:13,000 INFO [app] one-digit month",
        "[2025-03-01 09:03:14] INFO app: format B needs the T",
        "2025-03-01T09:00:00 INFO [app] format A needs a space, not T",
        "2025-03-01 09:00:00,12 INFO [app] milliseconds need 3 digits",
        "2025-03-01 09:00:00 INFO app no brackets",
        "[2025-03-01T09:00:00] INFO app no colon",
        "2025-03-01 09:00:00 INFO [] empty module",
        "",
    ]
    for line in bad:
        assert parse_line(line) is None, f"This line is not valid in either format and must give None: {line!r}. Use fullmatch so no part can be skipped."


def test_millis_not_in_format_b():
    assert parse_line("[2025-03-01T09:00:00,123] INFO app: x") is None, "Format B has no milliseconds."


# ---------- Part 2: summarise ----------

def write(tmp_path, text):
    p = tmp_path / "test.log"
    p.write_text(text, encoding="utf-8")
    return p


def test_summarise_small_example(tmp_path):
    p = write(tmp_path, "2025-03-01 09:00:01 INFO [app] start\n[2025-03-01T09:00:02] ERROR db: down\n\noops\n")
    assert summarise(p) == {"total": 2, "levels": {"INFO": 1, "ERROR": 1}, "top_error_modules": [("db", 1)], "unparsed": [4]}, "Count parsed lines and levels, ERROR modules, and the 1-based numbers of non-blank unparsed lines (line 3 is blank and is skipped)."


def test_summarise_accepts_str_path(tmp_path):
    p = write(tmp_path, "2025-03-01 09:00:01 INFO [app] start\n")
    assert summarise(str(p))["total"] == 1, "summarise must accept a str path as well as a Path: wrap it with Path(path)."


def test_summarise_empty_file(tmp_path):
    p = write(tmp_path, "")
    assert summarise(p) == {"total": 0, "levels": {}, "top_error_modules": [], "unparsed": []}, "An empty file gives zero counts and empty lists, with all four keys present."


def test_summarise_blank_lines_not_unparsed(tmp_path):
    p = write(tmp_path, "\n   \n\t\nbad\n")
    assert summarise(p)["unparsed"] == [4], "Blank and whitespace-only lines are skipped, not reported. Line numbers start at 1 (enumerate(..., start=1))."


def test_top_errors_ties_and_cut(tmp_path):
    lines = []
    for module, n in [("zeta", 2), ("alpha", 2), ("mid", 3), ("low", 1), ("crit", 5)]:
        level = "CRITICAL" if module == "crit" else "ERROR"
        lines += [f"2025-03-01 09:00:00 {level} [{module}] boom"] * n
    p = write(tmp_path, "\n".join(lines) + "\n")
    got = summarise(p)["top_error_modules"]
    assert got == [("mid", 3), ("alpha", 2), ("zeta", 2)], (
        f"Got {got}. Count ONLY ERROR (CRITICAL is not counted), sort by count high to low, break ties by module name A-Z "
        "(key=lambda kv: (-kv[1], kv[0])), and keep at most 3. Counter.most_common keeps first-seen order for ties, not A-Z."
    )


def test_top_errors_are_tuples(tmp_path):
    p = write(tmp_path, "2025-03-01 09:00:00 ERROR [a] x\n")
    got = summarise(p)["top_error_modules"]
    assert got == [("a", 1)] and isinstance(got[0], tuple), "top_error_modules is a list of (module, count) TUPLES."


def test_levels_is_plain_dict(tmp_path):
    p = write(tmp_path, "2025-03-01 09:00:00 ERROR [a] x\n")
    levels = summarise(p)["levels"]
    assert type(levels) is dict, "Return levels as a plain dict (dict(counter)), so a missing level raises KeyError instead of quietly giving 0."


def test_fixture_file():
    assert FIXTURE.exists(), "fixtures/app.log is missing next to the tests."
    got = summarise(FIXTURE)
    assert got["total"] == 16, f"fixtures/app.log has 16 valid lines in the two formats; you parsed {got['total']}. Check lower-case levels, WARN, optional milliseconds and empty messages."
    assert got["levels"] == {"INFO": 4, "DEBUG": 1, "WARNING": 2, "ERROR": 8, "CRITICAL": 1}, f"Level counts are wrong: {got['levels']}. WARN must be counted as WARNING, 'error'/'Error' as ERROR."
    assert got["top_error_modules"] == [("payments", 3), ("auth", 2), ("db.pool", 2)], f"Top ERROR modules are wrong: {got['top_error_modules']}. 'auth' and 'db.pool' tie at 2: sort ties A-Z."
    assert got["unparsed"] == [8, 9, 10, 14, 19, 20, 25], f"Unparsed line numbers are wrong: {got['unparsed']}. Lines 5 and 15 are blank (skip them); the traceback, VERBOSE, one-digit month, '[date time]' and the end marker are unparsed."
