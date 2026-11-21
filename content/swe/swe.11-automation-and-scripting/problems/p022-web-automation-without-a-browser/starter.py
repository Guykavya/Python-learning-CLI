import urllib.error
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin

USER_AGENT = "book-fetcher/1.0 (learning project)"
MAX_PAGES = 50


class FetchError(Exception):
    pass


class BookParser(HTMLParser):
    """The chapter's parser (section 10.2). TODO: also remember the href of <a class="next"> in self.next_href."""

    def __init__(self):
        super().__init__()
        self.books, self._href, self._title, self._in_price = [], None, None, False
        self._last_href = None
        self.next_href = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href", "").startswith("/b/"):
            self._href = a["href"]
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
    # TODO
    raise FetchError("not written yet")


def fetch_books(base_url, start="/", timeout=5):
    """All books, following 'next' links; never the same page twice; FetchError if none found."""
    # TODO
    return []
