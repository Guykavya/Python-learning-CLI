import httpx

from solution import CachingClient


class Server:
    """A scripted server: body/etag/headers can change; counts requests; records If-None-Match."""

    def __init__(self):
        self.requests = []
        self.etag = '"v1"'
        self.body = b"data-v1"
        self.cache_control = "max-age=60"
        self.status = 200
        self.send_etag = True

    def __call__(self, request):
        sent = request.headers.get("if-none-match")
        self.requests.append((str(request.url), sent))
        headers = {}
        if self.cache_control:
            headers["Cache-Control"] = self.cache_control
        if self.status == 200 and self.send_etag:
            headers["ETag"] = self.etag
            if sent == self.etag:
                return httpx.Response(304, headers=headers)
        return httpx.Response(self.status, content=self.body, headers=headers)


def make():
    server = Server()
    now = [0.0]
    client = CachingClient(httpx.Client(transport=httpx.MockTransport(server)), lambda: now[0])
    return client, server, now


A = "http://example.test/a"


def test_first_call_goes_to_the_network():
    c, s, now = make()
    assert c.get(A) == (b"data-v1", "network")
    assert len(s.requests) == 1


def test_fresh_copy_makes_no_request():
    c, s, now = make()
    c.get(A)
    now[0] = 30
    assert c.get(A) == (b"data-v1", "cache"), "At t=30 the copy (max-age=60) is still fresh."
    assert len(s.requests) == 1, "A fresh copy must not cause a request."
    now[0] = 59.9
    assert c.get(A)[1] == "cache"


def test_stale_copy_is_revalidated_with_the_etag():
    c, s, now = make()
    c.get(A)
    now[0] = 60
    assert c.get(A) == (b"data-v1", "revalidated"), "At t=60 the copy is stale (freshness ends at 60): send If-None-Match."
    assert s.requests[-1][1] == '"v1"', "The revalidation request must carry If-None-Match: the stored ETag."
    assert len(s.requests) == 2


def test_after_a_304_the_copy_is_fresh_again():
    c, s, now = make()
    c.get(A)
    now[0] = 61
    c.get(A)
    now[0] = 100
    assert c.get(A)[1] == "cache", "The 304 carried max-age=60: fresh until t=121."
    assert len(s.requests) == 2
    now[0] = 121
    assert c.get(A)[1] == "revalidated"


def test_a_changed_resource_replaces_the_copy():
    c, s, now = make()
    c.get(A)
    s.etag, s.body = '"v2"', b"data-v2"
    now[0] = 100
    assert c.get(A) == (b"data-v2", "network"), "The ETag no longer matches: the server sends the new body (200)."
    assert c.get(A) == (b"data-v2", "cache")
    now[0] = 200
    c.get(A)
    assert s.requests[-1][1] == '"v2"', "Revalidate with the NEW etag."


def test_no_store_is_never_kept():
    c, s, now = make()
    s.cache_control = "no-store"
    assert c.get(A)[1] == "network"
    assert c.get(A)[1] == "network"
    assert [sent for _, sent in s.requests] == [None, None], "A no-store response must not be stored or revalidated."


def test_no_store_removes_an_older_copy():
    c, s, now = make()
    c.get(A)
    s.cache_control = "no-store"
    s.etag = '"v2"'
    now[0] = 100
    c.get(A)
    s.cache_control = "max-age=60"
    now[0] = 101
    c.get(A)
    assert s.requests[-1][1] is None, "After a no-store answer the old copy must be gone (no If-None-Match)."


def test_etag_without_max_age_is_always_revalidated():
    c, s, now = make()
    s.cache_control = ""
    c.get(A)
    assert c.get(A)[1] == "revalidated", "No max-age: fresh for 0 seconds, but the ETag allows a cheap revalidation."
    assert len(s.requests) == 2


def test_no_cache_stores_but_revalidates():
    c, s, now = make()
    s.cache_control = "no-cache"
    c.get(A)
    assert c.get(A)[1] == "revalidated"


def test_max_age_without_etag():
    c, s, now = make()
    s.send_etag = False
    c.get(A)
    now[0] = 10
    assert c.get(A)[1] == "cache"
    now[0] = 70
    assert c.get(A)[1] == "network", "Stale and no ETag to revalidate with: fetch again."
    assert s.requests[-1][1] is None


def test_errors_are_not_stored():
    c, s, now = make()
    s.status = 500
    s.body = b"oops"
    assert c.get(A) == (b"oops", "network")
    s.status = 200
    s.body = b"fine"
    assert c.get(A) == (b"fine", "network"), "A 500 must not be cached."
    s.status = 404
    now[0] = 100          # the copy 'fine' is stale now
    assert c.get(A)[1] == "network"
    s.status = 200
    s.body = b"back"
    assert c.get(A) == (b"back", "network"), "A 404 removes the old copy."


def test_each_url_has_its_own_entry():
    c, s, now = make()
    c.get(A)
    c.get("http://example.test/b")
    assert len(s.requests) == 2
    c.get(A)
    c.get("http://example.test/b")
    assert len(s.requests) == 2, "Both URLs are cached separately."
