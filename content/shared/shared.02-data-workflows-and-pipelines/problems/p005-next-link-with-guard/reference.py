import httpx


class TooManyPagesError(RuntimeError):
    """The API kept sending a next link after max_pages pages."""


def fetch_linked(client, path="/v2/orders", max_pages=100):
    """Follow rel="next" links from path; at most max_pages requests; return all orders."""
    orders = []
    url = path
    for page_number in range(1, max_pages + 1):
        response = client.get(url)
        response.raise_for_status()
        orders.extend(response.json()["orders"])
        next_link = response.links.get("next")
        if next_link is None:
            return orders
        url = next_link["url"]
    raise TooManyPagesError(
        f"more than {max_pages} pages from {path}: the API still sent a next link "
        f"after page {max_pages} (last next URL: {url})"
    )
