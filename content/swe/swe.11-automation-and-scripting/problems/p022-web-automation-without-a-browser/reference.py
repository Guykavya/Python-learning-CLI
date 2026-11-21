import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

USER_AGENT = "book-fetcher/1.0 (learning project)"
MAX_PAGES = 50


class FetchError(Exception):
    pass


class BookParser(HTMLParser):
    """The chapter's parser (section 10.2), extended with the 'next' link."""

    def __init__(self):
        super().__init__()
        self.books, self._href, self._title, self._in_price = [], None, None, False
        self._last_href = None
        self.next_href = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href", "").startswith("/b/"):
            self._href = a["href"]
        elif tag == "a" and a.get("class") == "next":
            self.next_href = a.get("href")
        elif tag == "span" and a.get("class") == "price":
            self._in_price = True

    def handle_data(self, data):
        if self._href:
            self._title = data.strip()
        elif self._in_price:
            self.books.append({"title": self._title, "url": self._last_href, "price": float(data)})
            self._in_price = False

    def handle_endtag(self, tag):
        if tag == "a" and self._href:
            self._last_href, self._href = self._href, None


def get_page(url, timeout):
    """Body of url as text; any HTTP or network failure becomes FetchError naming the URL."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        raise FetchError(f"{url}: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"{url}: {e}") from e


def fetch_books(base_url, start="/", timeout=5):
    """All books, following 'next' links; never the same page twice; FetchError if none found."""
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
