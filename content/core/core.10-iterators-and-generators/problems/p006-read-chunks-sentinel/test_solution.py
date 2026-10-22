from solution import read_chunks


def make_reader(parts):
    parts = list(parts)
    calls = []

    def read():
        calls.append(1)
        return parts.pop(0) if parts else ""

    return read, calls


def test_collects_chunks():
    read, _ = make_reader(["ab", "cd", "e"])
    assert read_chunks(read) == ["ab", "cd", "e"], "Collect every chunk before the first empty string, without the empty string."


def test_empty_source():
    read, calls = make_reader([])
    assert read_chunks(read) == [], "A reader that is empty at once gives an empty list."
    assert len(calls) == 1, "read() should be called exactly once here."


def test_call_count():
    read, calls = make_reader(["x", "y"])
    read_chunks(read)
    assert len(calls) == 3, "One call per chunk plus one final call that returns the empty sentinel: you called read() the wrong number of times."


def test_stops_at_first_sentinel_only():
    items = ["a", "", "b", ""]
    state = {"i": 0}

    def read():
        v = items[state["i"]]
        state["i"] += 1
        return v

    assert read_chunks(read) == ["a"], "Stop at the FIRST empty string. Later chunks are not read."
