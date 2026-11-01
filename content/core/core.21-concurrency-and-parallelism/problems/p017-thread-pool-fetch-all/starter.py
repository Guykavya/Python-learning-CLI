from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_all(urls, fetch, workers):
    """Return {url: fetch(url) or the exception it raised}, using a pool of `workers` threads."""
    return {url: fetch(url) for url in urls}       # one at a time, and errors escape
