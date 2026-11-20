from urllib.parse import urljoin


def fetch_all(client, url, max_pages=1000):
    items = []
    seen = set()
    while url is not None:
        if url in seen:
            raise RuntimeError(f"pagination loop: {url} was already fetched")
        if len(seen) >= max_pages:
            raise RuntimeError(f"too many pages (more than {max_pages})")
        seen.add(url)
        response = client.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code} for {url}")
        try:
            data = response.json()
            page_items = data["items"]
        except (ValueError, KeyError, TypeError):
            raise RuntimeError(f"unexpected response body from {url}") from None
        items.extend(page_items)
        nxt = data.get("next")
        url = urljoin(url, nxt) if nxt else None
    return items
