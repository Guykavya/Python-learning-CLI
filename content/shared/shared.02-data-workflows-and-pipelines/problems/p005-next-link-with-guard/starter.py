import httpx


class TooManyPagesError(RuntimeError):
    """The API kept sending a next link after max_pages pages."""


def fetch_linked(client, path="/v2/orders", max_pages=100):
    """Follow rel="next" links from path; at most max_pages requests; return all orders."""
    raise NotImplementedError("request path, read response.links.get('next'), count the pages")
