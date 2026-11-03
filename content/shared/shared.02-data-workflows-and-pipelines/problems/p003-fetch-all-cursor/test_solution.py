import httpx
import pytest

from solution import fetch_all_cursor

BASE = "https://api.pagebound.test"
SAFETY = 30


def order(i):
    return {"id": i, "customer": {"email": f"user{i}@example.com", "city": None}, "status": "pending",
            "amount": "5.00", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
            "updated_at": "2024-06-01T12:00:00Z", "items": []}


def cursor_server(chunks, tokens, missing_key_at_end=False):
    """chunks[k] is the k-th answer's ids. tokens[k] is the cursor that leads TO chunk k+1.
    The server only knows these exact tokens, so a cursor you build yourself gets a 400."""
    seen = []
    lookup = {tok: k + 1 for k, tok in enumerate(tokens)}

    def handler(request):
        params = dict(request.url.params)
        seen.append(params)
        if len(seen) > SAFETY:
            raise AssertionError(f"More than {SAFETY} requests: your loop does not stop at next_cursor None.")
        if "cursor" not in params:
            k = 0
        elif params["cursor"] in lookup:
            k = lookup[params["cursor"]]
        else:
            return httpx.Response(400, json={"error": f"invalid cursor {params['cursor']!r}"})
        body = {"items": [order(i) for i in chunks[k]]}
        if k < len(chunks) - 1:
            body["next_cursor"] = tokens[k]
        elif not missing_key_at_end:
            body["next_cursor"] = None
        return httpx.Response(200, json=body)

    return httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE), seen


def ids(orders):
    return [o["id"] for o in orders]


def test_three_answers_in_order():
    client, seen = cursor_server([[101, 102, 103], [104, 105, 106], [107]], ["tokA", "tokB"])
    result = fetch_all_cursor(client)
    assert ids(result) == list(range(101, 108)), f"Got {ids(result)}; collect 'items' from every answer."
    assert len(seen) == 3, f"{len(seen)} requests for 3 answers."
    assert [p.get("cursor") for p in seen] == [None, "tokA", "tokB"], (
        f"Cursors sent: {[p.get('cursor') for p in seen]}. Send back exactly the last next_cursor."
    )


def test_first_request_has_no_cursor_parameter():
    client, seen = cursor_server([[1], [2]], ["t1"])
    fetch_all_cursor(client)
    assert "cursor" not in seen[0], (
        f"First request params: {seen[0]}. Leave the cursor key out completely; "
        "params={'cursor': None} is sent as 'cursor=' (an empty cursor)."
    )
    assert seen[0].get("limit") == "3", "Send limit on the first request too."


def test_limit_on_every_request():
    client, seen = cursor_server([[1, 2, 3, 4], [5, 6, 7, 8], [9]], ["x", "y"])
    assert ids(fetch_all_cursor(client, limit=4)) == list(range(1, 10))
    assert [p.get("limit") for p in seen] == ["4", "4", "4"], (
        f"limit values sent: {[p.get('limit') for p in seen]}. Keep sending limit with the cursor."
    )


def test_cursor_with_plus_slash_equals_survives():
    tokens = ["b3JkOjEwMw+/=", "a+b c/d==", "&page=9"]
    client, seen = cursor_server([[1], [2], [3], [4]], tokens)
    result = fetch_all_cursor(client)
    assert [p.get("cursor") for p in seen[1:]] == tokens, (
        f"The server received cursors {[p.get('cursor') for p in seen[1:]]}. Pass the cursor with "
        "params={...}; gluing it into the URL turns '+' into a space and '&' into a new parameter."
    )
    assert ids(result) == [1, 2, 3, 4]


def test_missing_next_cursor_key_also_stops():
    client, seen = cursor_server([[1, 2], [3]], ["more"], missing_key_at_end=True)
    assert ids(fetch_all_cursor(client)) == [1, 2, 3], (
        "The last answer has no next_cursor key at all. Use body.get('next_cursor') so that "
        "a missing key means the same as None (no KeyError)."
    )
    assert len(seen) == 2


def test_single_answer():
    client, seen = cursor_server([[7, 8]], [])
    assert ids(fetch_all_cursor(client)) == [7, 8]
    assert len(seen) == 1, "next_cursor None on the first answer: one request is enough."


def test_empty_result():
    client, seen = cursor_server([[]], [])
    assert fetch_all_cursor(client) == []
    assert len(seen) == 1, (
        f"{len(seen)} requests. Even with no orders you must make the first request to find out."
    )


def test_empty_answer_with_a_cursor_continues():
    client, _ = cursor_server([[1], [], [2]], ["p", "q"])
    assert ids(fetch_all_cursor(client)) == [1, 2], (
        "An empty 'items' list with a next_cursor is not the end. Only a missing/None cursor is."
    )


def test_items_are_full_dicts():
    client, _ = cursor_server([[5]], [])
    assert fetch_all_cursor(client) == [order(5)]


def test_error_status_raises():
    calls = []

    def handler(request):
        calls.append(1)
        if len(calls) > SAFETY:
            raise AssertionError("Too many requests.")
        if "cursor" not in request.url.params:
            return httpx.Response(200, json={"items": [order(1)], "next_cursor": "c"})
        return httpx.Response(400, json={"error": "cursor expired"})

    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE)
    with pytest.raises(httpx.HTTPStatusError):
        fetch_all_cursor(client)
    assert len(calls) == 2, "A 400 must raise at once (call raise_for_status on every answer)."
