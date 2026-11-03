import httpx
import pytest

from solution import TooManyPagesError, fetch_linked

BASE = "https://api.pagebound.test"
SAFETY = 60


def order(i):
    return {"id": i, "customer": {"email": f"user{i}@example.com", "city": "Pune"}, "status": "shipped",
            "amount": "9.50", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
            "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 1}]}


def linked_server(pages, absolute=True, extra_rels=True):
    """pages: list of id lists. Page k (0-based) links to ?after=tok{k+1} until the last page."""
    seen = []

    def handler(request):
        seen.append(str(request.url))
        if len(seen) > SAFETY:
            raise AssertionError(f"More than {SAFETY} requests: your loop does not stop.")
        after = request.url.params.get("after")
        k = 0 if after is None else int(after.removeprefix("tok"))
        if k >= len(pages):
            return httpx.Response(404, json={"error": "no such page"})
        links = []
        if extra_rels:
            links.append(f'<{BASE}/v2/orders>; rel="first"')
        if k < len(pages) - 1:
            prefix = BASE if absolute else ""
            links.append(f'<{prefix}/v2/orders?after=tok{k + 1}>; rel="next"')
        if extra_rels and k > 0:
            links.append(f'<{BASE}/v2/orders?after=tok{k - 1}>; rel="prev"')
        headers = {"Link": ", ".join(links)} if links else {}
        return httpx.Response(200, json={"orders": [order(i) for i in pages[k]]}, headers=headers)

    return httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE), seen


def endless_server():
    seen = []

    def handler(request):
        seen.append(str(request.url))
        if len(seen) > SAFETY:
            raise AssertionError(
                f"More than {SAFETY} requests to an endless API: your max_pages guard does not work."
            )
        n = len(seen)
        return httpx.Response(200, json={"orders": [order(n)]},
                              headers={"Link": f'</v2/orders?after=x{n}>; rel="next"'})

    return httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE), seen


def ids(orders):
    return [o["id"] for o in orders]


def test_follows_next_links_to_the_end():
    client, seen = linked_server([[101, 102], [103, 104], [105]])
    result = fetch_linked(client)
    assert ids(result) == [101, 102, 103, 104, 105], f"Got {ids(result)}; collect 'orders' from every page."
    assert seen == [f"{BASE}/v2/orders", f"{BASE}/v2/orders?after=tok1", f"{BASE}/v2/orders?after=tok2"], (
        f"Requested {seen}. Start at path, then request exactly the rel=\"next\" URL of each answer."
    )


def test_picks_next_among_several_rels():
    client, seen = linked_server([[1], [2], [3], [4]], extra_rels=True)
    assert ids(fetch_linked(client)) == [1, 2, 3, 4], (
        "The Link header also has rel=\"first\" and rel=\"prev\" entries. Use the one with "
        "rel=\"next\" (response.links.get('next')), not the first URL in the header."
    )
    assert len(seen) == 4


def test_relative_next_urls_work():
    client, seen = linked_server([[1, 2], [3]], absolute=False, extra_rels=False)
    assert ids(fetch_linked(client)) == [1, 2, 3], (
        "The next URL can be a path like /v2/orders?after=tok1. client.get(url) with the base_url "
        "client handles both forms; do not glue BASE in front yourself."
    )
    assert seen[1] == f"{BASE}/v2/orders?after=tok1"


def test_no_link_header_means_one_page():
    client, seen = linked_server([[7, 8, 9]], extra_rels=False)
    assert ids(fetch_linked(client)) == [7, 8, 9]
    assert len(seen) == 1, "An answer without any Link header is the last page: no more requests."


def test_custom_start_path():
    seen = []

    def handler(request):
        seen.append(request.url.path)
        return httpx.Response(200, json={"orders": [order(1)]})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE)
    fetch_linked(client, path="/v2/orders/archive")
    assert seen == ["/v2/orders/archive"], f"Requested {seen}; the first request must go to the path argument."


def test_endless_api_raises_after_exactly_max_pages():
    client, seen = endless_server()
    with pytest.raises(TooManyPagesError) as info:
        fetch_linked(client, max_pages=5)
    assert len(seen) == 5, (
        f"The endless API got {len(seen)} requests with max_pages=5. Make at most max_pages requests, "
        "and raise when page max_pages still has a next link (do not request page 6)."
    )
    assert "5" in str(info.value), f"Message {str(info.value)!r} must mention max_pages (5)."


def test_endless_api_with_default_limit():
    client, seen = endless_server()
    with pytest.raises(TooManyPagesError):
        fetch_linked(client, max_pages=40)
    assert len(seen) == 40, f"{len(seen)} requests with max_pages=40."


def test_too_many_pages_is_a_runtime_error():
    assert issubclass(TooManyPagesError, RuntimeError), "Keep TooManyPagesError a RuntimeError subclass."
    client, seen = endless_server()
    with pytest.raises(TooManyPagesError):
        fetch_linked(client, max_pages=2)
    assert len(seen) == 2


def test_exactly_max_pages_is_fine():
    client, seen = linked_server([[1], [2], [3]])
    assert ids(fetch_linked(client, max_pages=3)) == [1, 2, 3], (
        "3 pages with max_pages=3 is allowed: the third page has no next link, so the data is complete. "
        "Raise only when page max_pages STILL has a next link."
    )
    assert len(seen) == 3


def test_one_page_too_many_raises():
    client, seen = linked_server([[1], [2], [3], [4]])
    with pytest.raises(TooManyPagesError):
        fetch_linked(client, max_pages=3)
    assert len(seen) == 3, f"{len(seen)} requests; stop at max_pages=3 and raise."


def test_max_pages_one():
    client, seen = linked_server([[1], [2]])
    with pytest.raises(TooManyPagesError):
        fetch_linked(client, max_pages=1)
    assert len(seen) == 1


def test_http_error_on_a_later_page_raises():
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) > SAFETY:
            raise AssertionError("Too many requests.")
        if len(calls) == 1:
            return httpx.Response(200, json={"orders": [order(1)]},
                                  headers={"Link": '</v2/orders?after=a>; rel="next"'})
        return httpx.Response(502, text="bad gateway")

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_linked(client)
    assert len(calls) == 2
