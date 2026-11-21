## Approach

```python
def get_page(url, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise FetchError(f"{url}: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"{url}: {e}") from e


def fetch_books(base_url, start="/", timeout=5):
    first = url = urljoin(base_url, start)
    seen, books = set(), []
    while url and url not in seen and len(seen) < MAX_PAGES:
        seen.add(url)
        parser = BookParser()
        parser.feed(get_page(url, timeout))
        books += parser.books
        url = urljoin(url, parser.next_href) if parser.next_href else None
    if not books:
        raise FetchError(f"no books found at {first}: has the layout changed?")
    return books
```

and in the parser, `elif tag == "a" and a.get("class") == "next": self.next_href = a.get("href")`.

Each defensive line answers a way scraping goes wrong: a **timeout** so a hanging server cannot freeze a scheduled job; an error with the **URL** so the log says which page failed; a **visited set** and a page cap so a broken "next" link cannot loop for ever; and **"no books" is an error**, because scrapers fail silently when a site changes its layout (section 10.2). `html.parser` converts `&amp;` to `&` for you (`convert_charrefs=True` by default).

## Complexity

O(total size of the pages) for parsing, one request per page.

## Another way

Prefer an API when there is one (section 10, level 1): `GET /api/books?page=2` returning JSON needs no parser and breaks far less. With `httpx` (installed, swe.02) the code is the same shape: `httpx.Client(timeout=5, headers=...)`, `r.raise_for_status()`. For messy real-world HTML, `beautifulsoup4` with CSS selectors (`soup.select("li.book")`) is more forgiving than a hand-written `HTMLParser`. And before scraping a real site, read its terms of service and `robots.txt` (section 10.3).
