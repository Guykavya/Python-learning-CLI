# Problem plan: swe.02 Networking and HTTP (35 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.02.p001`…`p035`, folder `pNNN-slug`.

**Mix:** 11 drill, 14 applied, 7 deep, 3 challenge. **Kinds:** 27 code, 5 trace, 3 explain.
**assessment:** explain = p003, trace = p013, fix = p026, build = p035.
**★ core set:** p003, p005, p006, p010, p011, p013, p015, p021, p023, p026, p028, p030, p035 (outcomes: explain URL → page; call an API with timeouts and safe retries).

**Testing notes**
- **Never the internet.** Servers bind `("127.0.0.1", 0)` and read the port back (Ch. 3.3). Every socket gets `settimeout(5)` so a bug fails in 5 s, not at the 60 s cap.
- `conftest.py` carries the chapter's lab kit (Ch. 7.1): `LabHandler`, `QuietServer`, `serve(handler_class)` as a fixture that starts a `ThreadingHTTPServer` in a daemon thread and calls `shutdown()` + `server_close()` afterwards; `port_of(base)`. Problem tests define small handler subclasses (fails twice then succeeds, slow body, sets cookies…).
- Byte-level problems (framing, parsing, chunked) use **`socket.socketpair()`** or a list of byte chunks, not a server: fast, deterministic, works on Windows.
- Client problems take the HTTP client as a parameter (Ch. 19.2): tests pass `httpx.Client(transport=httpx.MockTransport(handler))`. Sleeping is injected (`sleep=recorder.append`), time is a fake clock; no test really sleeps more than 0.5 s.
- DNS (`getaddrinfo`) output is machine-specific: no test compares it; p004 only uses `localhost`/`127.0.0.1`.

## A. Layers, addresses and ports (Ch. 1–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Classify an IP address ✅ | drill | code | `classify(addr)` with `ipaddress` → `"loopback"`, `"private"`, `"link-local"`, `"global"`, `"invalid"`; v4 and v6 (`::1`, `fe80::1`, `10.0.0.1`, `8.8.8.8`, `"999.1.1.1"`) |
| 2 | Split host and port ✅ | drill | code | `split_hostport("example.com:8080")`, `"[::1]:443"`, `"localhost"` + default port from scheme (`http` 80, `https` 443); bad port → `ValueError` |
| 3 | From typing a URL to seeing a page ✅ | applied | explain | `assessment = "explain"`. Outcome 1. Walk through `https://shop.example/books?page=2#top` (Ch. 25): URL parse, DNS, TCP handshake, TLS, request, response, keep-alive, what the browser does with the fragment; checklist of 10 steps and 3 things that can fail at each layer |
| 4 | An echo server on port 0 ✅ | drill | code | `start_echo_server()` → `(server_socket, port)`, serves in a daemon thread, upper-cases each message (Ch. 5.3); test connects twice; port must be > 0 and not hard-coded (message: "use port 0 and getsockname()") |

## B. Sockets and framing (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Read exactly n bytes ✅ | drill | code | `recv_exactly(sock, n)` (Ch. 6.3) with `socketpair`; the writer sends in 1-byte pieces from a thread; closed early → `ConnectionError` naming how many bytes arrived; n = 0 → `b""` |
| 6 | Length-prefixed messages ✅ | applied | code | `send_message(sock, text)` / `recv_message(sock)` with a 4-byte big-endian length (`struct`), UTF-8; three messages back to back read correctly; an emoji message (bytes ≠ characters: message "length must count bytes") |
| 7 | A line reader that keeps the leftovers ✅ | applied | code | `LineReader` with `feed(chunk) -> list[str]`: chunks split lines anywhere, several lines per chunk, `\r\n` handled; the leftover waits for the next chunk; a line over 64 KiB raises `ValueError` (no endless buffer) |
| 8 | What does `recv` give you? ✅ | drill | trace | `⚠ HAND-TRACE` a sender's three `sendall` calls arrive as the given chunks; predict what a naive "one `recv` = one message" loop prints, then what the length-prefixed loop prints |
| 9 | Ask a UDP server, with a timeout ✅ | applied | code | `udp_ask(port, text, timeout, tries)`; the test's UDP server drops the first datagram; client resends after the timeout; all lost → returns `None`; replies from a different port are ignored |

## C. HTTP messages (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Parse an HTTP request ✅ | applied | code | `parse_request(data: bytes)` → method, target, version, headers (case-insensitive lookup, repeated headers kept), body read by `Content-Length`; bad request line or missing `Host` on HTTP/1.1 → `BadRequest` (the chapter's class, Ch. 15.1) |
| 11 | Build a response ✅ | drill | code | `build_response(status, body, content_type)` → bytes: status line with the reason phrase from `http.HTTPStatus`, `Content-Length` of the **encoded** body (message on the "é counts as 2 bytes" mistake), CRLF line ends, blank line |
| 12 | Decode a chunked body ✅ | applied | code | `decode_chunked(data)` (Ch. 8.4): hex sizes, chunk extensions `;x=1`, trailers, final `0`; a size line that is not hex or a short chunk → `ValueError` |
| 13 | Where does the body end? ✅ | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` four raw responses (Content-Length, chunked, `Connection: close` without length, `204` with a body that must be ignored); write each body exactly and whether the connection can be reused |
| 14 | A GET request by hand ✅ | applied | code | `http_get(host, port, path)` over a raw socket with `Host` and `Connection: close`; returns `(status, headers, body)`; tested against a `LabHandler` server that answers 200 and 404 |

## D. Methods, status codes, headers (Ch. 9–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Is it worth retrying? ✅ | drill | code | `worth_retrying(method, status, has_idempotency_key=False)` extending Ch. 10.4: 5xx/429/408 for safe and idempotent methods; POST only with a key; 4xx never (except 408/429); `None` status = connection error |
| 16 | Safe, idempotent, or neither? ✅ | drill | trace | for 8 calls (`GET /a`, `DELETE /a` twice, `POST /orders` twice, `PUT /a/1` twice, `PATCH` increment…) write the server state after each call; shows what "idempotent" means in data |
| 17 | What should the client do? ✅ | applied | code | `client_action(status, headers)` → `"use"`, `"follow:<url>"`, `"wait:<seconds>"`, `"fix-request"`, `"log-in"`, `"retry"`, `"give-up"`; `Retry-After` in seconds or as an HTTP date (`email.utils`, injected `now`) |
| 18 | Content negotiation with `Accept` ✅ | deep | code | `choose(accept_header, offered)` with q-values, `*/*`, `text/*`, q=0 meaning "not this"; ties keep the server's order; nothing acceptable → `None` (the server then sends 406) |
| 19 | A caching client with ETags ✅ | deep | code | `CachingClient(client, clock)`: stores body + ETag + `max-age`; fresh → no request; stale → sends `If-None-Match`, a `304` reuses the stored body; `no-store` never stored; the MockTransport handler counts requests |

## E. Cookies, URLs and JSON APIs (Ch. 12–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | A small cookie jar ✅ | challenge | code | `CookieJar` with `store(url, set_cookie_header, now)` and `header_for(url, now)`: `Path` prefix rule, `Secure` only on https, `Max-Age` expiry, `HttpOnly` kept, same-name replaced; host-only cookies (no `Domain`) |
| 21 | Build URLs without string glue ✅ | drill | code | `build_url(base, segments, query)` with `urllib.parse.quote` per segment and `urlencode(doseq=True)`; values containing `/`, `&`, `#`, spaces, Hindi text; `../` stays a harmless segment |
| 22 | PUT or POST to create? ✅ | applied | explain | explain who picks the id, what happens on a retry, and why `PUT /books/42` is idempotent and `POST /books` is not (Ch. 9.4, 21.5); checklist: client-chosen id, duplicate on retry, idempotency key as the fix |
| 23 | Read every page of an API ✅ | applied | code | `fetch_all(client, url)` follows `next` links in JSON (Ch. 14.3); stops on `null`; a repeated `next` link raises `RuntimeError` ("loop"); non-200 raises with the status; data across 3 pages in order |
| 24 | Turn API errors into exceptions ✅ | drill | code | `ApiError(status, code, message)`; `raise_for_api(response)` reads `{"error": {"code", "message"}}`; a body that is not JSON (an HTML 502 page) still raises with `code="bad-gateway"`-style fallback |

## F. A server from raw sockets (Ch. 15–16)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Route a request ✅ | applied | code | `route(routes, method, path)` with `{("GET", "/notes"): handler}` and one path parameter `/notes/{id}`; 404 for unknown paths, **405 with an `Allow` header** for a known path with the wrong method |
| 26 | Fix the server that hangs on keep-alive ✅ | deep | code | `assessment = "fix"`. Given a handler that reads the body with "read until the socket closes"; a keep-alive client never closes, so the server waits forever. Fix: read exactly `Content-Length` bytes (reuse p005). The test sends two requests on one connection with a 3 s socket timeout; message "the server waited for EOF" |

## G. HTTPS (Ch. 17)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | What TLS protects, and what it does not ✅ | deep | explain | the path, headers, body and cookies are hidden; the IP, the host name (SNI), sizes and timing are not; why `verify=False` is a trap; checklist from Ch. 17.1–17.3 |

## H. Timeouts and retries (Ch. 18–22)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 28 | Backoff with jitter and `Retry-After` ✅ | applied | code | `delays(attempts, base, cap, rng)` "full jitter" in `[0, min(cap, base·2^i)]`; checked with a seeded `random.Random` against the bounds, not exact values; `retry_after(header, now)` → seconds (int or HTTP date; past date → 0) |
| 29 | A timeout is per wait, not total ✅ | deep | trace | `⚠ HAND-TRACE` a server sends 1 byte every 0.8 s for 10 bytes; client read timeout 1 s; write whether it times out, after how long, and the same with a total deadline of 3 s (Ch. 20.3) |
| 30 | A resilient JSON client ✅ | challenge | code | `get_json(client, url, attempts=4, sleep=..., rng=...)`: retries `ConnectError`, `ReadTimeout`, 502/503/504/429 for GET only, honours `Retry-After`, gives up with the last error; **never** retries a POST without `Idempotency-Key`; tests count requests and recorded sleeps per scenario (Ch. 22) |
| 31 | A circuit breaker ✅ | deep | code | `CircuitBreaker(threshold, cooldown, clock)`: closed → open after N consecutive failures, open fails fast without calling, half-open lets one trial through, success closes (Ch. 21.6); every transition tested with the fake clock |

## I. Scraping, politely (Ch. 23–25)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 32 | Scrape a product table ✅ | applied | code | `parse_products(html)` with BeautifulSoup: name, price as `Decimal` from `"₹1,299.00"`, in-stock flag; a missing price → `None`, not a crash; extra whitespace and nested tags |
| 33 | `robots.txt` and a polite rate limiter ✅ | applied | code | `allowed(robots_text, agent, url)` with `urllib.robotparser.RobotFileParser.parse`; `RateLimiter(min_interval, clock, sleep)` waits only the remaining time (Ch. 24.3) |
| 34 | The mini browser, step by step ✅ | deep | trace | `⚠ HAND-TRACE` the chapter's mini browser (Ch. 25.1) fetching a URL that redirects once and sets a cookie: write the ordered list of steps (parse, resolve, connect, send, status, follow, cookie stored, final body length) |

## J. Project (Ch. 26)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Notes server and resilient client ✅ | challenge | code | `assessment = "build"`. `NotesServer` (raw sockets, keep-alive, `GET/POST /notes`, `GET /notes/{id}`, JSON, 400/404/405 with an error body) used as a context manager on port 0, and `NotesClient(base, client)` with timeouts and the p030 retry rule. Tests: create + list + get over one keep-alive connection; malformed JSON → 400; a flaky handler in front (fails twice) and the client still succeeds with 3 requests; POST is not retried |

## Counts check
Written 2026-11-19, all 35 validated (Sonnet, main session, no subagents). Deviations from the table: no shared `conftest.py` (each test file that needs a server carries a 30-line `serve()` helper, so a problem folder is self-contained); p004's accept loop uses a 0.1 s timeout because closing a listening socket does not wake a blocked `accept()` on Linux; p008, p016, p029, p034 expected answers come from running the code (p034 uses a dictionary instead of sockets, so it can be traced on paper); p013 expects `body=` and `reuse=` per response; p019 returns `(body, source)`; p030 follows chapter 21.2 (connect errors are retried even for POST; every other POST failure only with an idempotency key); p033 notes that `RobotFileParser` ignores a non-integer `Crawl-delay`; p035's client reuses the p030 policy inside `solution.py`.

Tiers: drill 1, 2, 4, 5, 8, 11, 13, 15, 16, 21, 24 (11); applied 3, 6, 7, 9, 10, 12, 14, 17, 22, 23, 25, 28, 32, 33 (14); deep 18, 19, 26, 27, 29, 31, 34 (7); challenge 20, 30, 35 (3). Total 35.
Kinds: trace 8, 13, 16, 29, 34 (5); explain 3, 22, 27 (3); code 27. Assessments: explain p003, trace p013, fix p026, build p035.

## Risks and open questions

- Threaded servers in tests: always `daemon=True`, always shut down in a fixture `finally`, or a failing test leaves a thread that blocks the next one.
- Windows firewall may pop up a dialog the first time Python listens; binding to `127.0.0.1` (not `0.0.0.0`) avoids it on most machines.
- p029 and p026 involve real waiting: keep total waiting under 4 s per test.
- TLS on loopback (Ch. 17.4) needs a certificate made with `openssl`/`cryptography`; no problem depends on it (explain only).
