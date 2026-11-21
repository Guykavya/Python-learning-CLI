import http.server
import threading
import time

import pytest

import solution
from solution import FetchError, fetch_books, get_page


def page(books, next_href=None):
    items = "".join(f'<li class="book"><a href="{href}">{title}</a> <span class="price">{price}</span></li>\n'
                    for href, title, price in books)
    nxt = f'<a class="next" href="{next_href}">Next</a>' if next_href else ""
    return f"<html><body><h1>Books</h1><ul>\n{items}</ul>{nxt}</body></html>"


PAGES = {
    "/": page([("/b/1", "Python Basics", "12.50"), ("/b/2", "Automate It", "20.00")], "/page/2"),
    "/page/2": page([("/b/3", "Tom &amp; Jerry", "7.25")], "3"),                 # relative link: /page/3
    "/page/3": page([("/b/4", "Last One", "1.00")]),
    "/broken": page([("/b/9", "Before The Crash", "5.00")], "/boom"),
    "/loop": page([("/b/5", "Round And Round", "3.00")], "/loop"),
    "/empty": "<html><body><div class='new-layout'>Books moved!</div></body></html>",
}


class Handler(http.server.BaseHTTPRequestHandler):
    agents = []

    def do_GET(self):
        Handler.agents.append(self.headers.get("User-Agent", ""))
        if self.path == "/slow":
            time.sleep(2)
        if self.path == "/boom":
            body, status = b"internal error", 500
        elif self.path in PAGES or self.path == "/slow":
            body, status = PAGES.get(self.path, PAGES["/page/3"]).encode("utf-8"), 200
        else:
            body, status = b"not found", 404
        try:
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except OSError:
            pass                                    # the client gave up (timeout test)

    def log_message(self, *args):
        pass


class QuietServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass


@pytest.fixture
def base():
    Handler.agents = []
    server = QuietServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_get_page_returns_text(base):
    assert "Python Basics" in get_page(base + "/", timeout=5), "Return the decoded body of the page."


def test_get_page_says_who_you_are(base):
    get_page(base + "/", timeout=5)
    assert Handler.agents[-1] == solution.USER_AGENT, f"Send the header User-Agent: USER_AGENT; the server saw {Handler.agents[-1]!r}"


def test_get_page_http_error_names_the_url(base):
    with pytest.raises(FetchError) as info:
        get_page(base + "/missing", timeout=5)
    assert "/missing" in str(info.value) and "404" in str(info.value), f"Name the URL and the status; got {str(info.value)!r}"


def test_follows_next_links_in_order(base):
    books = fetch_books(base)
    assert [b["title"] for b in books] == ["Python Basics", "Automate It", "Tom & Jerry", "Last One"], \
        "Follow every 'next' link (the one on page 2 is relative: urljoin it with the current URL). &amp; becomes &."
    assert books[0] == {"title": "Python Basics", "url": "/b/1", "price": 12.5}, f"Each book is a dict with a float price; got {books[0]}"


def test_a_500_raises_with_the_url(base):
    with pytest.raises(FetchError) as info:
        fetch_books(base, start="/broken")
    assert "/boom" in str(info.value) and "500" in str(info.value), \
        f"A failing page must raise FetchError naming the failing URL; got {str(info.value)!r}"


def test_never_loops(base):
    books = fetch_books(base, start="/loop")
    assert [b["title"] for b in books] == ["Round And Round"], "A 'next' link back to the same page must not be followed again."


def test_nothing_found_is_an_error(base):
    with pytest.raises(FetchError, match="no books"):
        fetch_books(base, start="/empty")


def test_timeout_becomes_fetch_error(base):
    start = time.monotonic()
    with pytest.raises(FetchError):
        fetch_books(base, start="/slow", timeout=0.5)
    assert time.monotonic() - start < 1.8, "Pass the timeout to urlopen: the slow page takes 2 s, the limit is 0.5 s."


def test_connection_refused_becomes_fetch_error():
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()                                       # nobody listens on this port now
    with pytest.raises(FetchError):
        get_page(f"http://127.0.0.1:{port}/", timeout=2)
