from itertools import islice

from solution import grep

LOGS = [
    "08:00 INFO start\n",
    "08:01 ERROR disk full\n",
    "08:02 INFO retry\n",
    "08:03 error: network\n",
]


def counted(items, log):
    for item in items:
        log.append(item)
        yield item


def endless_logs():
    n = 0
    while True:
        if n >= 10_000:
            raise RuntimeError("Read 10,000 lines from an endless stream: your code is not lazy.")
        yield "ok" if n % 3 else "error here"
        n += 1


def test_basic():
    assert list(grep(LOGS, "error")) == [
        (2, "08:01 ERROR disk full"),
        (4, "08:03 error: network"),
    ], "Number ALL lines from 1, ignore case when matching, and rstrip the line."


def test_word_case_ignored_both_sides():
    assert [n for n, _ in grep(LOGS, "Info")] == [1, 3], "Lower-case the word too, not only the line."


def test_no_match():
    assert list(grep(LOGS, "warning")) == [], "No matching line gives nothing."


def test_is_generator():
    result = grep(LOGS, "info")
    assert iter(result) is result, "grep must be a generator function (use yield or yield from)."


def test_max_count_result():
    assert list(grep(LOGS, "ERROR", max_count=1)) == [(2, "08:01 ERROR disk full")], "max_count=1 gives only the first match."


def test_max_count_stops_reading():
    log = []
    list(grep(counted(LOGS, log), "info", max_count=2))
    assert len(log) == 3, "After the last match you need (line 3), stop. Do not read line 4. Check the count right after yield, or use islice."


def test_max_count_zero():
    log = []
    assert list(grep(counted(LOGS, log), "info", max_count=0)) == [], "max_count=0 gives no matches."
    assert log == [], "max_count=0 must not read any line."


def test_endless_input():
    assert list(grep(endless_logs(), "error", max_count=3)) == [
        (1, "error here"), (4, "error here"), (7, "error here")
    ], "Must work on an endless stream when max_count is given."


def test_endless_without_limit_is_lazy():
    assert list(islice(grep(endless_logs(), "error"), 2)) == [(1, "error here"), (4, "error here")], "Without max_count, it must still be lazy."
