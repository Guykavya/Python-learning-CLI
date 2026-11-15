import httpx


def fetch_all_pages(client, per_page=3):
    """Follow next_page from page 1 until it is None; return all orders in order."""
    orders = []
    page = 1
    while page is not None:
        response = client.get("/v1/orders", params={"page": page, "per_page": per_page})
        response.raise_for_status()
        body = response.json()
        orders.extend(body["data"])
        page = body["next_page"]          # the API decides; None ends the loop
    return orders
