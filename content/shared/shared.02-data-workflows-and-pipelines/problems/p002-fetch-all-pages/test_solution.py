import httpx
import pytest

from solution import fetch_all_pages

BASE = "https://api.pagebound.test"
SAFETY = 30   # the test server refuses to answer more than this many requests


def order(i):
    return {"id": i, "customer": {"email": f"user{i}@example.com", "city": "Pune"}, "status": "shipped",
            "amount": "19.99", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
            "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 2}]}


def paged_server(pages):
    """pages: list of lists of ids. Page n (1-based) is pages[n-1]; next_page is n+1 until the last."""
    seen = []

    def handler(request):
        seen.append(dict(request.url.params))
        if len(seen) > SAFETY:
            raise AssertionError(f"More than {SAFETY} requests: your loop does not stop when next_page is None.")
        assert request.url.path == "/v1/orders", f"Wrong path {request.url.path}; use /v1/orders."
        page = int(request.url.params.get("page", "0"))
        if not 1 <= page <= len(pages):
            return httpx.Response(404, json={"error": f"no page {page}"})
        next_page = page + 1 if page < len(pages) else None
        return httpx.Response(200, json={"data": [order(i) for i in pages[page - 1]],
                                         "page": page, "next_page": next_page})

    return httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE), seen


def ids(orders):
    return [o["id"] for o in orders]


def test_seven_orders_three_pages():
    client, seen = paged_server([[101, 102, 103], [104, 105, 106], [107]])
    result = fetch_all_pages(client)
    assert ids(result) == list(range(101, 108)), (
        f"Got ids {ids(result)}. Collect every page's 'data', in order, until next_page is None."
    )
    assert [p.get("page") for p in seen] == ["1", "2", "3"], (
        f"Pages requested: {[p.get('page') for p in seen]}. Start at page=1 and follow next_page."
    )
    assert all(p.get("per_page") == "3" for p in seen), "Send per_page on every request."


def test_returns_full_order_dicts():
    client, _ = paged_server([[101], [102]])
    result = fetch_all_pages(client)
    assert result == [order(101), order(102)], "Return the order dicts themselves, unchanged."


def test_last_page_full_is_not_followed_by_an_extra_request():
    client, seen = paged_server([[1, 2, 3], [4, 5, 6]])
    result = fetch_all_pages(client)
    assert ids(result) == [1, 2, 3, 4, 5, 6]
    assert len(seen) == 2, (
        f"{len(seen)} requests for 2 pages. The second page said next_page=None, so stop. "
        "Stopping on 'an empty page' or 'a short page' costs an extra request (or a 404)."
    )


def test_short_page_in_the_middle_is_not_the_end():
    client, seen = paged_server([[1, 2, 3], [4, 5], [6, 7, 8], [9]])
    result = fetch_all_pages(client)
    assert ids(result) == [1, 2, 3, 4, 5, 6, 7, 8, 9], (
        f"Got {ids(result)}. Page 2 had only 2 orders but next_page was 3. "
        "Never use 'len(data) < per_page' as the stopping rule; only next_page is None ends it."
    )
    assert len(seen) == 4


def test_empty_page_in_the_middle_is_not_the_end():
    client, seen = paged_server([[1, 2], [], [3]])
    assert ids(fetch_all_pages(client)) == [1, 2, 3], (
        "Page 2 was empty but next_page was 3. An empty page is not the end; next_page is None is."
    )


def test_no_orders_at_all():
    client, seen = paged_server([[]])
    assert fetch_all_pages(client) == [], "One empty page with next_page None means no orders."
    assert len(seen) == 1, f"{len(seen)} requests; one is enough when the first page says next_page None."


def test_single_page():
    client, seen = paged_server([[42]])
    assert ids(fetch_all_pages(client)) == [42]
    assert len(seen) == 1


def test_per_page_is_passed_through():
    client, seen = paged_server([[1, 2, 3, 4, 5], [6]])
    assert ids(fetch_all_pages(client, per_page=5)) == [1, 2, 3, 4, 5, 6]
    assert all(p.get("per_page") == "5" for p in seen), (
        f"Params sent: {seen}. Use the per_page argument, not a hard-coded 3."
    )


def test_follows_next_page_value_not_page_plus_one():
    seen = []
    script = {1: ([1, 2], 3), 3: ([3, 4], 7), 7: ([5], None)}   # the API skips page numbers

    def handler(request):
        seen.append(request.url.params.get("page"))
        if len(seen) > SAFETY:
            raise AssertionError("Too many requests: your loop does not stop.")
        page = int(request.url.params["page"])
        if page not in script:
            return httpx.Response(404, json={"error": f"no page {page}"})
        data, nxt = script[page]
        return httpx.Response(200, json={"data": [order(i) for i in data], "page": page, "next_page": nxt})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE)
    result = fetch_all_pages(client)
    assert seen == ["1", "3", "7"], (
        f"Pages requested: {seen}. Ask for exactly the page that next_page names; do not compute page + 1."
    )
    assert ids(result) == [1, 2, 3, 4, 5]


def test_server_error_on_page_two_raises():
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) > SAFETY:
            raise AssertionError("Too many requests.")
        if request.url.params["page"] == "1":
            return httpx.Response(200, json={"data": [order(1)], "page": 1, "next_page": 2})
        return httpx.Response(503, json={"error": "busy"})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_all_pages(client)
    # Returning only page 1 would look like success and silently lose data.
