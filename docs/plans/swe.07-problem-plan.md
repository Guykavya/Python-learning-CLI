# Problem plan: swe.07 Auth, API design and security (35 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `swe.07.p001`…`p035`.

**Mix:** 12 drill, 13 applied, 7 deep, 3 challenge. **Kinds:** 26 code, 6 trace, 3 explain.
**assessment:** explain = p033, trace = p013, fix = p023, build = p035.
**★ core set:** p003, p006, p009, p011, p013, p019, p021, p023, p024, p026, p028, p032, p033, p035 (outcomes: stop a user reading another user's data **and test it**; a payment-style endpoint safe to call twice).

**Testing notes**
- Web problems use **FastAPI** like the chapter (`build_app(...)` returning an app; `TestClient`). The chapter's helpers (`b64u`, `b64u_decode`, the fixed-clock pattern of Ch. 3 "Try it: a fixed clock") go into `conftest.py` where the learner does not write them.
- **Time is always injected** (`now: float` or a `clock()` callable): token expiry, session timeouts, rate limits and TOTP are tested at exact boundaries without sleeping.
- **Password hashing cost:** tests pass small scrypt parameters (`n=2**10, r=8, p=1`, ~1 MB, < 5 ms) so 50 hashes stay fast; one test checks the module's *default* `N` is ≥ 2**14 without hashing with it.
- **Known-answer tests** where a standard exists: PKCE S256 from RFC 7636 appendix B (`dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk` → `E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM`), TOTP from RFC 6238 appendix B (SHA-1 key `b"12345678901234567890"`, T = 59 → `94287082` with 8 digits), HOTP from RFC 4226 appendix D. Re-check each vector by running the reference when writing.
- "Two-actor" problems create users Asha and Ravi in the test, each with their own client/token (Ch. 8.4).
- Never real outgoing requests: SSRF checks take an injected `resolve(host) -> list[str]`.

## A. Threats and words (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Name the threat ✅ | drill | trace | `⚠ HAND-TRACE` 8 short scenarios (Ch. "Try it: name the threat"); write the STRIDE letter for each, one per line |
| 2 | Authentication is not authorisation ✅ | drill | explain | define both, identification and accountability, with one endpoint example each; the six questions of Ch. 1.4; checklist |

## B. Passwords (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 3 | A password module ✅ | drill | code | `hash_password(pw, n=, r=, p=)` with `hashlib.scrypt`, random 16-byte salt, self-describing string `scrypt$n$r$p$salt$hash`; `verify_password` with `hmac.compare_digest`; wrong password, tampered string, unicode password |
| 4 | Upgrade the cost on login ✅ | applied | code | `needs_rehash(stored)` and `verify_and_upgrade(pw, stored) -> (ok, new_stored_or_None)` (Ch. 2.2, "Try it: the cost upgrade"); old cost upgraded only after a correct password |
| 5 | A modern password policy ✅ | drill | code | `check_password_policy(pw, username)` → list of problems: length < 12, in a given breached list, contains the username, all one character; **no** composition rules (Ch. 2.4); a long passphrase passes |
| 6 | A login that does not reveal accounts ✅ | applied | code | `login(users, username, password, verify)`: same error for unknown user and wrong password, and `verify` is still called once with a dummy hash for an unknown user (the test counts calls) so timing does not leak (Ch. 2.5) |
| 7 | Reset tokens ✅ | applied | code | `ResetTokens(clock)`: `issue(user) -> token` (random, `secrets`), stores only the SHA-256, expires after 15 min, single use, a new token cancels the old one (Ch. 2.6) |
| 8 | Why not just encrypt passwords? ✅ | drill | explain | key theft reveals every password; hashing is one-way; slow hash vs fast hash; salt vs pepper (Ch. "Try it: why not just encrypt passwords?"); checklist |

## C. Sessions (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | A server-side session store ✅ | applied | code | `SessionStore(clock, idle=30*60, absolute=8*3600)`: `create`, `get` (slides the idle timer), `rotate(old_sid)` at login (fixation, Ch. 3.3), `destroy`; ids from `secrets.token_urlsafe(32)`; boundaries tested exactly |
| 10 | Keep secrets out of the logs ✅ | drill | code | a `logging.Filter` that masks `password`, `token`, `authorization`, `api_key` values in dict args and `key=value` text; the message is still logged (Ch. 15.6, "Try it: the logged password"); tests with `caplog` |

## D. Tokens and JWT (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 11 | A JWT by hand ✅ | drill | code | `sign(payload, key)` and `verify(token, key)` for HS256 with base64url without padding (Ch. 4.1); a changed payload, a changed header, a wrong key and a token with two dots missing all raise `InvalidToken` |
| 12 | Claims that must be checked ✅ | applied | code | `check_claims(claims, now, issuer, audience, leeway=30)`: `exp`, `nbf`, `iss`, `aud` (string or list), required `sub`; each failure named in the exception |
| 13 | What is wrong with this token? ✅ | deep | trace | `assessment = "trace"`. `⚠ HAND-TRACE` 6 tokens shown decoded (alg `none`, `exp` in the past, `aud` of another service, HS256 signed with the public key, a `kid` path, a valid one) against the chapter's `verify` (Ch. 4.3, "Try it: what is wrong with this token?"); write which check rejects each, or `accepted` |
| 14 | Refresh tokens that detect theft ✅ | deep | code | `RefreshStore`: `issue(user)`, `rotate(token)` returns a new pair and retires the old token; reusing a retired token raises `TokenReuse` **and revokes the whole family** (Ch. 4.4) |

## E. OAuth2 and OpenID Connect (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | PKCE by hand ✅ | drill | code | `make_verifier()` (43–128 chars from the allowed set) and `challenge_for(verifier)` (S256, base64url, no padding); RFC 7636 test vector |
| 16 | Fix the sloppy redirect check ✅ | applied | code | the authorisation server accepts `redirect_uri.startswith(registered)`; `https://app.example.com.evil.net/cb` and `https://app.example.com/cb/../x` get through; exact match against the registered list (Ch. "Try it: the sloppy redirect check") |
| 17 | The authorisation code flow, in order ✅ | drill | trace | `⚠ HAND-TRACE` the chapter's in-process flow (Ch. 5.3); write the 8 messages in order: who sends what to whom (`state`, `code_challenge`, `code`, `code_verifier`, token) |

## F. API keys, one-time codes, webhooks (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | API keys done right ✅ | applied | code | `ApiKeys`: `create(owner) -> "pk_" + prefix + "_" + secret` shown once, store prefix + SHA-256 only, `check(key)` finds by prefix and compares in constant time, `revoke`; the stored data never contains the secret |
| 19 | TOTP with replay protection ✅ | applied | code | `hotp`, `totp(key, at, step=30, digits=6)`, `verify_totp(key, code, now, last_step)` accepting ±1 step and rejecting a step ≤ `last_step` (Ch. 6.3, "Try it: the TOTP replay"); RFC 4226/6238 vectors |
| 20 | Verify a signed webhook ✅ | applied | code | `receive(body: bytes, ts, signature, now, secret)`: HMAC-SHA256 over `f"{ts}.".encode() + body`, 5-minute tolerance, compare in constant time; re-serialising the JSON breaks the signature (test sends bytes with odd spacing) |

## G. Authorisation and IDOR (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 21 | One policy function, deny by default ✅ | applied | code | `can(user, action, order)` (Ch. 7.3): owners read/cancel their own pending orders, support reads all, admins refund; anonymous and unknown actions → `False`; a table of 20 cases |
| 22 | 401, 403 or 404? ✅ | drill | trace | `⚠ HAND-TRACE` 6 requests (no token, bad token, another user's order, admin route as a user, a missing order, own order); write the status each should get (Ch. 7.5, "Try it: the 403 that leaks") |
| 23 | Fix the IDOR ✅ | applied | code | `assessment = "fix"`. `GET/PATCH/DELETE /notes/{id}` load by id only, so Ravi can read and delete Asha's notes; fix by scoping the query to the owner and returning 404 (Ch. 8.3); tests act as both users |
| 24 | The two-actor test ✅ | challenge | code | Outcome 1, the test half. The learner writes `check_isolation(make_client) -> list[str]` (Ch. 8.4): problems found; the test runs it against the secure app (must return `[]`) and against 3 apps with one hole each (read, update, list) — each hole must be reported |

## H. API design and pagination (Ch. 9–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Status codes that mean something ✅ | drill | trace | `⚠ HAND-TRACE` 8 situations (created, accepted for later, validation error, conflict, gone, precondition failed, rate limited, unhandled bug); write the status code (Ch. "Try it: status codes") |
| 26 | Keyset pagination with an opaque cursor ✅ | deep | code | `page_after(rows, cursor, limit)` ordered by `(created, id)`; `encode_cursor`/`decode_cursor` (base64url JSON); a tampered cursor → `ValueError` (400); inserting a new row between pages does not repeat or skip any row (offset would) |
| 27 | Sort and filter by allow-list ✅ | drill | code | `parse_listing(params)`: `sort` from `{"created", "-created", "total"}`, `status` from an enum, `limit` 1..100; anything else → a 400 error listing what is allowed (Ch. 10.4, "Try it: the sort oracle") |

## I. Rate limiting (Ch. 11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 28 | A token bucket with `Retry-After` ✅ | applied | code | `TokenBucket(capacity, rate, clock)`: `take()` → `(allowed, retry_after_seconds)`; burst up to capacity, refill rate exact, `Retry-After` rounded **up**; a FastAPI dependency returns 429 with the header |
| 29 | The boundary burst ✅ | deep | trace | `⚠ HAND-TRACE` limit 5 per 10 s; requests at given times around a window edge; write allowed/denied for fixed window, sliding log and token bucket (Ch. 11.2, "Try it: the boundary burst") |
| 30 | Which IP is the client? ✅ | deep | code | `client_ip(remote_addr, x_forwarded_for, trusted_proxies=1)`: take the right entry counting from the right; a spoofed left-most value is ignored; no proxies trusted → `remote_addr` (Ch. 11.3, "Try it: the spoofed header") |

## J. Evolving an API and idempotency (Ch. 12–13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 31 | Stop lost updates with ETags ✅ | applied | code | `GET` returns an `ETag` (hash of the version); `PUT` without `If-Match` → 428, with a stale one → 412, with the current one → 200 and a new ETag (Ch. 12.6) |
| 32 | A payment endpoint that is safe to call twice ✅ | challenge | code | Outcome 2. `POST /payments` with `Idempotency-Key` (Ch. 13.3–13.6): the first call charges a fake provider once and stores the response; a repeat with the same key and body returns the **same** response and does not charge again; same key + different body → 422; a request still in progress → 409; keys are scoped per user; the test calls 2, 3 and 10 times and counts provider charges |
| 33 | Why "check, then insert" is not enough ✅ | deep | explain | `assessment = "explain"`. Explain why a client cannot tell "failed" from "succeeded but the reply was lost", why idempotency keys solve it, why a read-then-write check races, and why the key must be stored in the same transaction as the effect (Ch. 13.1–13.4, "Try it: what is wrong with this design?") |

## K. Input handling (Ch. 14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 34 | Path traversal and SSRF guards ✅ | deep | code | `safe_join(base, user_path)` (resolved path must stay inside `base`; `..`, absolute paths, symlinks in `tmp_path`) and `check_url(url, resolve)` (http/https only, resolve **first**, then reject loopback/private/link-local/metadata IPs, Ch. 14.6, "Try it: why resolve before checking?") |

## L. Project (Ch. 17)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Audit and harden an API ✅ | challenge | code | `assessment = "build"`. Given `build_app(insecure=True)` (the chapter's style of Ch. 17.1, shortened): the learner writes `build_hardened_app()`. The tests are the audit findings, red on the insecure app and green on the hardened one: login does not reveal accounts and is throttled, passwords hashed, tokens expire, no IDOR on orders, payments idempotent, redirects only to allowed hosts, no secrets in logs, one error format with no tracebacks |

## Counts check

Tiers: drill 1, 2, 3, 5, 8, 10, 11, 15, 17, 22, 25, 27 (12); applied 4, 6, 7, 9, 12, 16, 18, 19, 20, 21, 23, 28, 31 (13); deep 13, 14, 26, 29, 30, 33, 34 (7); challenge 24, 32, 35 (3). Total 35.
Kinds: trace 1, 13, 17, 22, 25, 29 (6); explain 2, 8, 33 (3); code 26.

## Risks and open questions

- p035 is large: keep the insecure app to ~120 lines and 8 findings; the full 10-finding audit of Ch. 17 stays in the chapter.
- p032's "in progress → 409" needs two overlapping requests; test it by calling the handler function directly with a provider that blocks on a `threading.Event`, not with real concurrency in `TestClient`.
- Security wording ages (password guidance, OWASP list order). `answer.md` files cite the chapter's sections, not outside documents, so they stay consistent with the course.
