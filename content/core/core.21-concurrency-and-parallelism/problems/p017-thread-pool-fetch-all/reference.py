from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_all(urls, fetch, workers):
    """Return {url: fetch(url) or the exception it raised}, using a pool of `workers` threads."""
    results = {}
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_url = {executor.submit(fetch, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as exc:
                results[url] = exc
    return results
