import itertools

import pytest

from solution import at_least, count_per_minute, first_messages, parse_line, parse_lines, summarize

LINES = [
    "2024-05-01 10:15:02 INFO web: started\n",
    "2024-05-01 10:15:09 DEBUG db: pool size 5\n",
    "garbage line\n",
    "2024-05-01 10:15:40 ERROR db: connection lost\n",
    "\n",
    "2024-05-01 10:16:01 WARNING web: slow request /home\n",
    "2024-05-01 10:16:30 ERROR web: timeout: upstream\n",
    "2024-05-01 10:16:31 CRITICAL db: unknown level\n",
    "2024-05-01 10:18:00 INFO db: recovered\n",
]


def limited(lines, limit):
    """Yield lines, but fail if more than `limit` lines are read: proves a stage is lazy."""
    for i, line in enumerate(lines):
        if i >= limit:
            raise AssertionError(
                f"The pipeline read line number {i + 1}, but only {limit} were needed. "
                "Some stage reads ahead or collects everything (list(), sorted(), len())."
            )
        yield line


# ---------- parse_line ----------

def test_parse_line_valid():
    assert parse_line("2024-05-01 10:15:40 ERROR db: connection lost\n") == {
        "date": "2024-05-01",
        "time": "10:15:40",
        "level": "ERROR",
        "source": "db",
        "message": "connection lost",
    }, "A valid line gives a dict with exactly the keys date, time, level, source, message. Strip the newline."


def test_parse_line_colon_in_message():
    record = parse_line("2024-05-01 10:16:30 ERROR web: timeout: upstream")
    assert record is not None, "A message may contain ': '. Split rest only at the FIRST ': '."
    assert (record["source"], record["message"]) == ("web", "timeout: upstream"), "Split rest at the first ': ' only."


def test_parse_line_extra_spaces():
    record = parse_line("  2024-05-01   10:15:02  INFO   web:   hi there  \n")
    assert record is not None, "Extra spaces between fields are allowed: use split(maxsplit=3), not split(' ')."
    assert record["message"] == "hi there", "Strip spaces at both ends of the message."


@pytest.mark.parametrize(
    "line, why",
    [
        ("", "an empty line"),
        ("\n", "a blank line"),
        ("garbage line", "too few parts"),
        ("2024-05-01 10:15:02 INFO web started", "no ': ' after the source"),
        ("2024-05-01 10:15:02 INFO web:x", "':' must be followed by a space"),
        ("2024-05-01 10:15:02 INFO web: ", "an empty message"),
        ("2024-05-01 10:15:02 INFO : hello", "an empty source"),
        ("2024-05-01 10:15:02 INFO my web: hello", "a source with a space"),
        ("2024-05-01 10:15:02 info web: hello", "a lower-case level"),
        ("2024-05-01 10:15:02 CRITICAL web: hello", "an unknown level"),
        ("2024-5-01 10:15:02 INFO web: hello", "a date with a one-digit month"),
        ("2024/05/01 10:15:02 INFO web: hello", "a date with / instead of -"),
        ("2024-0a-01 10:15:02 INFO web: hello", "a date with a letter"),
        ("2024-05-01 10:15 INFO web: hello", "a time without seconds"),
        ("2024-05-01 24:00:00 INFO web: hello", "hour 24"),
        ("2024-05-01 10:60:00 INFO web: hello", "minute 60"),
        ("2024-05-01 10:15:61 INFO web: hello", "second 61"),
        ("2024-05-01 1x:15:02 INFO web: hello", "a time with a letter"),
    ],
)
def test_parse_line_invalid(line, why):
    assert parse_line(line) is None, f"{line!r} is invalid ({why}): parse_line must return None, not raise and not a record."


# ---------- parse_lines ----------

def test_parse_lines_example():
    sources = [r["source"] for r in parse_lines(LINES)]
    assert sources == ["web", "db", "db", "web", "web", "db"], "Six valid lines, in order. Skip invalid lines; do not stop at the first one."


def test_parse_lines_creation_reads_nothing():
    parse_lines(limited(LINES, 0))  # must not raise: a generator reads nothing until next()


def test_parse_lines_is_lazy():
    records = parse_lines(limited(LINES, 4))
    got = [next(records)["message"] for _ in range(3)]
    assert got == ["started", "pool size 5", "connection lost"], "The first three records come from the first four lines."


def test_parse_lines_endless():
    got = list(itertools.islice(parse_lines(itertools.cycle(LINES)), 10))
    assert len(got) == 10, "parse_lines must work on an endless stream of lines."
    assert got[6]["message"] == "started", "After the 6 records of one round, the stream starts again."


# ---------- at_least ----------

def test_at_least_warning():
    got = [r["message"] for r in at_least(parse_lines(LINES), "WARNING")]
    assert got == ["connection lost", "slow request /home", "timeout: upstream"], (
        "WARNING and more serious: WARNING and ERROR. Compare positions in DEBUG < INFO < WARNING < ERROR, not strings."
    )


def test_at_least_bounds():
    assert len(list(at_least(parse_lines(LINES), "DEBUG"))) == 6, "DEBUG is the lowest level: every record passes."
    assert [r["level"] for r in at_least(parse_lines(LINES), "ERROR")] == ["ERROR", "ERROR"], "ERROR: only ERROR records."
    assert len(list(at_least(parse_lines(LINES), "INFO"))) == 5, "INFO and above: all but the DEBUG record."


def test_at_least_bad_level_raises_at_once():
    with pytest.raises(ValueError):
        at_least(parse_lines(limited(LINES, 0)), "LOUD")
    with pytest.raises(ValueError):
        at_least([], "error")


def test_at_least_bad_level_message():
    try:
        at_least([], "LOUD")
    except ValueError as e:
        assert "LOUD" in str(e), "The error message should name the bad level so the user can fix it."
    else:
        raise AssertionError(
            "at_least must raise ValueError when it is CALLED. If you put 'yield' in at_least, the check only runs at "
            "the first next(). Check first, then return a generator expression (or call a generator helper)."
        )


def test_at_least_is_lazy():
    errors = at_least(parse_lines(limited(LINES, 4)), "ERROR")
    assert next(errors)["message"] == "connection lost", "The first ERROR is on line 4: only four lines may be read."


# ---------- count_per_minute ----------

def test_count_per_minute_example():
    assert list(count_per_minute(parse_lines(LINES))) == [
        ("2024-05-01 10:15", 3),
        ("2024-05-01 10:16", 2),
        ("2024-05-01 10:18", 1),
    ], "Group neighbouring records by 'date HH:MM' with groupby and count each group. Minutes with no records are not listed."


def test_count_per_minute_empty():
    assert list(count_per_minute(iter([]))) == [], "No records: no minutes."


def test_count_per_minute_includes_date():
    lines = ["2024-05-01 23:59:10 INFO a: x", "2024-05-02 23:59:20 INFO a: y"]
    assert list(count_per_minute(parse_lines(lines))) == [
        ("2024-05-01 23:59", 1),
        ("2024-05-02 23:59", 1),
    ], "The same clock minute on two different days is two different minutes: put the date in the key."


def test_count_per_minute_after_filter():
    got = list(count_per_minute(at_least(parse_lines(LINES), "WARNING")))
    assert got == [("2024-05-01 10:15", 1), ("2024-05-01 10:16", 2)], "Stages combine: count only the filtered records."


def test_count_per_minute_is_lazy():
    minutes = count_per_minute(parse_lines(limited(itertools.cycle(LINES), 6)))
    assert next(minutes) == ("2024-05-01 10:15", 3), (
        "To finish the first minute, groupby needs the first record of the next minute (line 6), and no more."
    )


def test_count_per_minute_endless():
    got = list(itertools.islice(count_per_minute(parse_lines(itertools.cycle(LINES))), 4))
    assert [c for _, c in got] == [3, 2, 1, 3], "Works on an endless stream: never call list() or sorted() on the records."


# ---------- summarize ----------

def test_summarize_example():
    assert summarize(parse_lines(LINES)) == {
        "total": 6,
        "by_level": {"INFO": 2, "DEBUG": 1, "ERROR": 2, "WARNING": 1},
        "top_source": "db",
        "first": "2024-05-01 10:15:02",
        "last": "2024-05-01 10:18:00",
    }, "Check each key. top_source: db and web both have 3, so the alphabetically first, 'db', wins."


def test_summarize_empty():
    assert summarize(iter([])) == {
        "total": 0,
        "by_level": {},
        "top_source": None,
        "first": None,
        "last": None,
    }, "No records: total 0, empty by_level, and None for top_source, first and last. Do not crash on max() of nothing."


def test_summarize_filtered():
    assert summarize(at_least(parse_lines(LINES), "WARNING")) == {
        "total": 3,
        "by_level": {"ERROR": 2, "WARNING": 1},
        "top_source": "web",
        "first": "2024-05-01 10:15:40",
        "last": "2024-05-01 10:16:30",
    }, "summarize works on any stage. Here web has 2 records and db has 1."


def test_summarize_tie_break():
    lines = [
        "2024-05-01 10:00:00 INFO zeta: a",
        "2024-05-01 10:00:01 INFO alpha: b",
        "2024-05-01 10:00:02 INFO zeta: c",
        "2024-05-01 10:00:03 INFO alpha: d",
    ]
    assert summarize(parse_lines(lines))["top_source"] == "alpha", (
        "zeta and alpha both have 2 records: pick the alphabetically first, not the first one seen."
    )


def test_summarize_one_pass_on_generator():
    big = (f"2024-05-01 10:{i // 60 % 60:02d}:{i % 60:02d} INFO s{i % 3}: m" for i in range(30_000))
    result = summarize(parse_lines(big))
    assert result["total"] == 30_000, (
        "summarize got a generator: it can be read only once. Count everything in ONE loop."
    )
    assert result["by_level"] == {"INFO": 30_000}, "All 30,000 records are INFO."
    assert result["last"] == "2024-05-01 10:19:59", "last is the time of the final record in the stream."


# ---------- first_messages ----------

def test_first_messages_example():
    assert first_messages(LINES, "ERROR", 2) == ["db: connection lost", "web: timeout: upstream"], (
        "Format each as 'source: message'."
    )


def test_first_messages_fewer_than_n():
    assert first_messages(LINES, "WARNING", 10) == [
        "db: connection lost",
        "web: slow request /home",
        "web: timeout: upstream",
    ], "If there are fewer than n, return them all."


def test_first_messages_stops_reading():
    got = first_messages(limited(LINES, 7), "ERROR", 2)
    assert got == ["db: connection lost", "web: timeout: upstream"], "The two ERROR messages."


def test_first_messages_zero():
    assert first_messages(limited(LINES, 0), "INFO", 0) == [], "n = 0: an empty list, and no line may be read."


def test_first_messages_endless():
    got = first_messages(itertools.cycle(LINES), "ERROR", 5)
    assert len(got) == 5, "first_messages must work on an endless stream: use islice, not a list of all records."


def test_first_messages_bad_level():
    with pytest.raises(ValueError):
        first_messages(LINES, "FATAL", 1)
