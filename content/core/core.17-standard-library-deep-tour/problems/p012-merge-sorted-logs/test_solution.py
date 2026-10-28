from collections.abc import Iterator
from itertools import islice

from solution import merge_files, merge_logs


def line(sec, msg):
    return f"2025-03-01T10:00:{sec:02d} {msg}"


def test_example():
    a = [line(0, "a1"), line(5, "a2")]
    b = [line(1, "b1"), line(5, "b2")]
    assert list(merge_logs(a, b)) == [line(0, "a1"), line(1, "b1"), line(5, "a2"), line(5, "b2")], (
        "Merge by time; on equal times the earlier source comes first."
    )


def test_returns_iterator():
    got = merge_logs([line(0, "x")], [line(1, "y")])
    assert isinstance(got, Iterator), "Return a lazy iterator (heapq.merge gives one), not a list."


def test_tie_uses_timestamp_only():
    a = [line(3, "zzz from source 1")]
    b = [line(3, "aaa from source 2")]
    got = list(merge_logs(a, b))
    assert got == [a[0], b[0]], (
        "Same timestamp: source 1 first. Comparing whole lines would put 'aaa' first; use key=lambda l: l[:19]."
    )


def test_three_sources_and_empty():
    a = [line(1, "a"), line(4, "a")]
    b = []
    c = [line(0, "c"), line(2, "c"), line(9, "c")]
    got = list(merge_logs(a, b, c))
    assert got == [line(0, "c"), line(1, "a"), line(2, "c"), line(4, "a"), line(9, "c")], "Any number of sources; an empty one is fine."
    assert list(merge_logs()) == [], "No sources: nothing."


def test_same_source_order_kept():
    a = [line(5, "first"), line(5, "second"), line(5, "third")]
    assert list(merge_logs(a)) == a, "Equal timestamps inside one source keep their order."


class Counting:
    """A sorted source that records how many lines were taken from it."""

    def __init__(self, start, n):
        self.taken = 0
        self.start = start
        self.n = n

    def __iter__(self):
        for i in range(self.n):
            self.taken += 1
            yield line(self.start + i, f"s{self.start}-{i}")


def test_lazy():
    a = Counting(0, 50)
    b = Counting(1, 50)
    first_three = list(islice(merge_logs(a, b), 3))
    # a gives seconds 0, 1, 2, ...; b gives seconds 1, 2, 3, ...  At second 1 there is a tie: a (the first source) wins.
    assert first_three == [line(0, "s0-0"), line(1, "s0-1"), line(1, "s1-0")], "The three earliest lines across both sources, ties to the first source."
    assert a.taken <= 3 and b.taken <= 3, (
        f"merge_logs read {a.taken} and {b.taken} lines to give 3: it must be lazy. "
        "Do not use sorted() or list() on the sources; heapq.merge reads one line ahead per source."
    )


def test_merge_files(tmp_path):
    p1 = tmp_path / "web1.log"
    p2 = tmp_path / "web2.log"
    p1.write_text(f"{line(0, 'web1 start')}\n{line(7, 'web1 GET /')}\n", encoding="utf-8")
    p2.write_text(f"{line(2, 'web2 start')}\n\n{line(7, 'web2 GET /a')}", encoding="utf-8")
    out = tmp_path / "all.log"
    n = merge_files([p1, p2], out)
    text = out.read_text(encoding="utf-8")
    expected = [line(0, "web1 start"), line(2, "web2 start"), line(7, "web1 GET /"), line(7, "web2 GET /a")]
    assert text.splitlines() == expected, (
        "Merged lines in time order, blank lines skipped, ties from the first file first. "
        "Strip each line's '\\n' before merging so a file without a final newline does not glue two lines together."
    )
    assert text.endswith("\n") and not text.endswith("\n\n"), "Every written line ends with exactly one '\\n'."
    assert n == 4, "Return the number of lines written (blank lines are not counted)."


def test_merge_files_utf8_and_empty(tmp_path):
    p1 = tmp_path / "a.log"
    p2 = tmp_path / "b.log"
    p1.write_text(f"{line(1, 'café ✓')}\n", encoding="utf-8")
    p2.write_text("", encoding="utf-8")
    out = tmp_path / "o.log"
    assert merge_files([p1, p2], out) == 1, "An empty file adds nothing."
    assert out.read_text(encoding="utf-8") == line(1, "café ✓") + "\n", "Read and write with encoding='utf-8'."
