import pytest

from solution import items, pages


def make_api(data, failures=None, other_error_on=None):
    """A fake service. failures = {page: how many times it fails first}. Records every call."""
    calls = []
    left = dict(failures or {})

    def fetch_page(n):
        calls.append(n)
        if n == other_error_on:
            raise ValueError("bad page")
        if left.get(n, 0) > 0:
            left[n] -= 1
            raise ConnectionError(f"page {n} timed out")
        return list(data[n]) if n < len(data) else []

    return fetch_page, calls


DATA = [["a", "b", "c"], ["d", "e"], ["f"]]


def test_pages_basic():
    fetch, calls = make_api(DATA)
    assert list(pages(fetch)) == DATA, "pages yields every non-empty page in order."
    assert calls == [0, 1, 2, 3], "Fetch pages 0, 1, 2, then 3 which is empty: stop there. Do not fetch further."


def test_pages_empty_service():
    fetch, calls = make_api([])
    assert list(pages(fetch)) == [], "Page 0 is empty: no pages."
    assert calls == [0], "Only page 0 is fetched."


def test_pages_is_lazy():
    fetch, calls = make_api(DATA)
    p = pages(fetch)
    assert calls == [], "Creating the iterator must not fetch anything yet."
    assert next(p) == ["a", "b", "c"], "The first page."
    assert calls == [0], "One next() means one fetch."


def test_items_lazy():
    fetch, calls = make_api(DATA)
    it = items(fetch)
    assert (next(it), next(it)) == ("a", "b"), "The first two items."
    assert calls == [0], "Only page 0 is needed for the first two items. Do not fetch all pages first."
    assert list(it) == ["c", "d", "e", "f"], "The rest, across pages."
    assert calls == [0, 1, 2, 3], "Stop after the first empty page."


def test_items_across_page_boundary():
    fetch, calls = make_api(DATA)
    it = items(fetch)
    got = [next(it) for _ in range(4)]
    assert got == ["a", "b", "c", "d"], "Item 4 is the first item of page 1."
    assert calls == [0, 1], "Page 1 is fetched only when its first item is needed."


def test_retry_then_success():
    fetch, calls = make_api(DATA, failures={1: 2})
    assert list(items(fetch, retries=2)) == list("abcdef"), "Two failures with retries=2: the third try works."
    assert calls == [0, 1, 1, 1, 2, 3], "Retry the SAME page number. Do not move on to the next page after a failure."


def test_too_many_failures():
    fetch, calls = make_api(DATA, failures={1: 3})
    got = []
    with pytest.raises(ConnectionError):
        for x in items(fetch, retries=2):
            got.append(x)
    assert got == ["a", "b", "c"], "Items of page 0 arrive before page 1 fails."
    assert calls == [0, 1, 1, 1], "1 try + 2 retries = 3 calls for page 1, then give up and raise."


def test_zero_retries():
    fetch, calls = make_api(DATA, failures={0: 1})
    with pytest.raises(ConnectionError):
        list(pages(fetch, retries=0))
    assert calls == [0], "retries=0 means try once only."


def test_other_errors_not_retried():
    fetch, calls = make_api(DATA, other_error_on=1)
    with pytest.raises(ValueError):
        list(items(fetch))
    assert calls == [0, 1], "Only ConnectionError is retried. Catch exactly that exception, not Exception."


def test_page_numbers_not_shared():
    fetch, calls = make_api(DATA)
    first = pages(fetch)
    second = pages(fetch)
    assert next(first) == ["a", "b", "c"], "first starts at page 0."
    assert next(second) == ["a", "b", "c"], "Each pages() call has its own page counter: keep it inside pages, not global."
