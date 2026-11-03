import json

import httpx
import pytest

from solution import NotJSONError, get_json

BASE = "https://api.pagebound.test"
ORDER = {"id": 101, "customer": {"email": "asha@example.com", "city": "Pune"}, "status": "shipped",
         "amount": "19.99", "currency": "INR", "created_at": "2024-06-01T10:00:00Z",
         "updated_at": "2024-06-01T12:00:00Z", "items": [{"sku": "B1", "qty": 2}]}


def make_client(status=200, body=None, text=None, content_type="application/json"):
    """A client whose server always gives the same answer. Records every request."""
    seen = []

    def handler(request):
        seen.append(request)
        if body is not None:
            return httpx.Response(status, json=body)
        return httpx.Response(status, text=text or "", headers={"content-type": content_type})

    return httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE), seen


def test_returns_parsed_dict_and_sends_params():
    page = {"data": [ORDER], "page": 2, "next_page": 3}
    client, seen = make_client(body=page)
    result = get_json(client, "/v1/orders", {"page": 2, "per_page": 3})
    assert result == page, "Return response.json(): the parsed dict, not the Response or its text."
    assert len(seen) == 1, f"get_json sent {len(seen)} requests; one call needs one request."
    assert str(seen[0].url) == f"{BASE}/v1/orders?page=2&per_page=3", (
        f"The request went to {seen[0].url}. Pass the dict as params=... so httpx builds the query string."
    )
    assert seen[0].method == "GET", "Use client.get, not post."


def test_no_params_means_no_query_string():
    client, seen = make_client(body={"ok": True})
    assert get_json(client, "/v1/health") == {"ok": True}
    assert seen[0].url.query == b"", (
        f"Query was {seen[0].url.query!r}. With params=None the URL must have no query string."
    )


def test_list_json_is_returned_as_is():
    client, _ = make_client(body=[1, 2, 3])
    assert get_json(client, "/v1/ids") == [1, 2, 3], (
        "JSON can be a list too. Return whatever response.json() gives; do not assume a dict."
    )


def test_404_raises_http_status_error_even_with_html_body():
    client, _ = make_client(status=404, text="<html>Not Found</html>", content_type="text/html")
    with pytest.raises(httpx.HTTPStatusError) as info:
        get_json(client, "/v1/nope")
    assert info.value.response.status_code == 404, "The error must carry the 404 response."
    # If you got NotJSONError here: you parsed the body before calling raise_for_status().


def test_500_with_json_body_still_raises():
    client, _ = make_client(status=500, body={"error": "database down"})
    with pytest.raises(httpx.HTTPStatusError):
        get_json(client, "/v1/orders")
    # A 500 with a JSON error body is still a failure. Returning {"error": ...} as if it were
    # data would load an error message into your pipeline.


def test_200_html_raises_not_json_error_with_path_and_snippet():
    client, _ = make_client(text="<html><body>Maintenance</body></html>", content_type="text/html")
    with pytest.raises(NotJSONError) as info:
        get_json(client, "/v1/orders")
    message = str(info.value)
    assert "/v1/orders" in message, f"Message {message!r} must name the path so you know which call failed."
    assert "Maintenance" in message, f"Message {message!r} must show the start of the body."


def test_not_json_error_is_a_value_error_and_keeps_the_cause():
    client, _ = make_client(text="not json at all", content_type="text/plain")
    with pytest.raises(NotJSONError) as info:
        get_json(client, "/v1/orders")
    assert isinstance(info.value, ValueError)
    assert isinstance(info.value.__cause__, json.JSONDecodeError), (
        "Use 'raise NotJSONError(...) from error' inside the except block, so the original "
        "JSONDecodeError (with its line and column) is kept as __cause__."
    )


def test_snippet_is_cut_to_80_characters():
    body = "<html>" + "x" * 74 + "TAIL-THAT-MUST-NOT-APPEAR" + "y" * 2000
    client, _ = make_client(text=body, content_type="text/html")
    with pytest.raises(NotJSONError) as info:
        get_json(client, "/v1/orders")
    message = str(info.value)
    assert "<html>" in message, "The message must contain the start of the body."
    assert "TAIL-THAT-MUST-NOT-APPEAR" not in message and len(message) < 300, (
        f"The message is {len(message)} characters long. Put only body[:80] in it, not the whole page."
    )


def test_empty_200_body_is_not_json():
    client, _ = make_client(text="", content_type="application/json")
    with pytest.raises(NotJSONError):
        get_json(client, "/v1/orders")
    # An empty body with status 200 is a broken answer, not "no data".


def test_204_returns_none():
    client, seen = make_client(status=204, text="")
    assert get_json(client, "/v1/orders/101/cancel") is None, (
        "204 No Content has no body. Return None instead of trying to parse it."
    )
    assert len(seen) == 1
