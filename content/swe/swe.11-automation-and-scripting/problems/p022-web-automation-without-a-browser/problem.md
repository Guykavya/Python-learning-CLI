# Web automation without a browser

Chapter sections 10 (order of preference: API, hidden JSON, HTML, browser), 10.2 (parsing HTML with `BookParser`) and 10.3 (being a polite automator). Many pages put their content straight into the HTML, so a plain HTTP request and a small parser are enough: no browser, 100 times faster, far less fragile. The tests start a tiny local web server on `127.0.0.1` (like the chapter's `demo_server.py`), so nothing on the internet is touched.

A shop lists books over several pages:

```html
<ul>
<li class="book"><a href="/b/1">Python Basics</a> <span class="price">12.50</span></li>
<li class="book"><a href="/b/2">Automate It</a> <span class="price">20.00</span></li>
</ul>
<a class="next" href="/page/2">Next</a>          <!-- missing on the last page -->
```

## What to write

```python
def get_page(url, timeout) -> str: ...
def fetch_books(base_url, start="/", timeout=5) -> list[dict]: ...
```

Use only the standard library: `urllib.request`, `urllib.parse.urljoin` and `html.parser`. The starter gives `FetchError`, `USER_AGENT` and the chapter's `BookParser`; extend the parser so it also remembers the `href` of the `<a class="next">` link (`next_href`, `None` if there is none).

`get_page(url, timeout)`:
- sends a request with the header `User-Agent: USER_AGENT` (say who you are) and the given `timeout`, and returns the body decoded as UTF-8;
- an HTTP error status (such as 500 or 404) raises `FetchError` whose message contains the **URL** and the status code; a timeout or a connection problem raises `FetchError` with the URL too (`urllib.error.HTTPError` first, then `URLError`, `TimeoutError` and other `OSError`s).

`fetch_books(base_url, start="/", timeout=5)`:
- starts at `urljoin(base_url, start)`, parses the books on the page, then follows the "next" link (relative, so `urljoin` it with the current page's URL) until a page has none;
- never visits the same URL twice (a broken site whose "next" points back must not loop for ever), and stops after at most 50 pages;
- returns all books in page order as dicts `{"title": ..., "url": ..., "price": ...}` (`url` is the `href` as written, `price` a `float`);
- if no book at all was found, raises `FetchError("no books found at <url>")`: an empty result usually means the layout changed, and a silent empty list would look like "the shop sold out".

## Example

```python
fetch_books("http://127.0.0.1:8765")
# [{'title': 'Python Basics', 'url': '/b/1', 'price': 12.5},
#  {'title': 'Automate It', 'url': '/b/2', 'price': 20.0},
#  {'title': 'Tom & Jerry', 'url': '/b/3', 'price': 7.25}, ...]
fetch_books("http://127.0.0.1:8765", start="/broken")   # FetchError: http://127.0.0.1:8765/boom: HTTP 500
```
