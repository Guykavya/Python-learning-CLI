import httpx


def fetch_all_cursor(client, limit=3):
    """First call without cursor; then send back next_cursor until it is None or missing."""
    orders = []
    params = {"limit": limit}                 # first call: no cursor key at all
    while True:
        response = client.get("/v1/orders", params=params)
        response.raise_for_status()
        body = response.json()
        orders.extend(body["items"])
        cursor = body.get("next_cursor")
        if cursor is None:
            return orders
        params = {"limit": limit, "cursor": cursor}
