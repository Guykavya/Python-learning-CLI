from solution import first_valid

def endless(start=0):
    # Acts like an infinite stream. It stops the test after 10,000 items,
    # so a solution that is not lazy cannot freeze your computer.
    n = start
    while True:
        if n - start >= 10_000:
            raise RuntimeError("Read 10,000 items from an endless stream: your code is not lazy. Did you call list() on the input?")
        yield n
        n += 1


def must_not_be_read():
    raise AssertionError("This source was read too early. You already had n readings, so stop before the next source.")
    yield  # this line makes the function a generator


def test_basic():
    batches = [[12, None, 55, 20], [-3, 18], [25, 30]]
    assert first_valid(batches, 3) == [12, 20, 18], "Join the sources in order and skip None and values outside 0..50."


def test_fewer_than_n():
    batches = [[12, None, 55, 20], [-3, 18], [25, 30]]
    assert first_valid(batches, 10) == [12, 20, 18, 25, 30], "If there are fewer than n valid readings, return them all."


def test_zero():
    assert first_valid([[1, 2]], 0) == [], "n = 0 gives an empty list."


def test_bounds_and_zero_value():
    assert first_valid([[0, 50, 51, -1, 25.5]], 5) == [0, 50, 25.5], "0 and 50 are valid. Test 'r is not None', not 'if r', or 0 is lost."


def test_no_sources():
    assert first_valid([], 3) == [], "No sources give an empty list."


def test_returns_list():
    assert isinstance(first_valid([[1]], 1), list), "Return a list."


def test_does_not_open_next_source():
    assert first_valid([[5, None, 7], must_not_be_read()], 2) == [5, 7], "Stop as soon as you have n readings."


def test_does_not_read_past_last_needed():
    assert first_valid([[5, 6], [7], must_not_be_read()], 3) == [5, 6, 7], "Exactly n found at the end of a source: do not peek into the next source."


def test_endless_source():
    assert first_valid([[None, 99], endless()], 4) == [0, 1, 2, 3], "Must work when a source is endless: never call list() on a source."
