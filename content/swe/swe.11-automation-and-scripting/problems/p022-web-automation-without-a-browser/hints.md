## Hint 1

Split it in two: `get_page` knows HTTP (headers, timeout, errors) and nothing about books; the loop in `fetch_books` knows pages and nothing about HTTP. For the parser: in `handle_starttag`, which attribute tells the "next" link apart from a book link? For the loop: what data structure answers "have I been here before?" quickly?

## Hint 2

```text
get_page: req = Request(url, headers={"User-Agent": USER_AGENT})
    try: with urlopen(req, timeout=timeout) as r: return r.read().decode("utf-8")
    except HTTPError as e: raise FetchError(f"{url}: HTTP {e.code}") from e
    except (URLError, TimeoutError, OSError) as e: raise FetchError(f"{url}: {e}") from e
BookParser.handle_starttag: ... elif tag == "a" and a.get("class") == "next": self.next_href = a.get("href")
fetch_books:
    url = urljoin(base_url, start); seen = set(); books = []
    while url and url not in seen and len(seen) < 50:
        seen.add(url); p = BookParser(); p.feed(get_page(url, timeout)); books += p.books
        url = urljoin(url, p.next_href) if p.next_href else None
    if not books: raise FetchError(...)
    return books
```
