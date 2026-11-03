import httpx


def fetch_all_cursor(client, limit=3):
    """First call without cursor; then send back next_cursor until it is None or missing."""
    return []
