# Problem plan: llm.02 Calling LLM APIs reliably (30 problems)

Rules: [README.md](README.md) (shared, read R1–R5 first) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `llm.02.p001` … `p030`, folder `pNNN-slug`. Requires llm.01 and swe.05 (FastAPI, Pydantic v2, TestClient are allowed).

**Mix:** 10 drill, 10 applied, 7 deep, 3 challenge. **Kinds:** 20 code, 7 trace, 3 explain.
**assessment:** explain = p005, trace = p010, fix = p016, build = p030.
**★ core set (write first):** p001, p003, p005, p007, p010, p012, p016, p019, p021, p024, p027, p030.

**Testing notes**
- This chapter does **not** use llm.01's `FakeLLM`. Its fake is an HTTP-level **`FakeProvider`** (Ch. 1.2) behind `httpx.MockTransport`, so the real client code (status codes, headers, JSON, SSE) is exercised with no network:
  `VirtualClock()` with `.time()` / `.sleep(s)` (moves `.now`, never really sleeps);
  steps `ok(text, stop_reason="end_turn", fail_after=None)`, `status(code, message="", retry_after=None)`, `slow(seconds, text)`, `hang()`, `garbage()`;
  `FakeProvider(steps, clock=None, api_key="test-key", repeat_last=True)` with `.transport()`, `.requests` (accepted bodies) and `.calls` (all HTTP calls); models `fake-small` / `fake-large`.
  Copy these (and, where a problem builds on it, the chapter's error classes, `RetryPolicy`, `LLMClient`) **verbatim into `conftest.py`**. The solution receives a `transport`, `client`, `clock` or `rng` as an argument.
- Never real sleeping and never real time: every retry/timeout test uses `VirtualClock` and asserts on `clock.now`. Jitter uses an injected `random.Random(seed)`; tests check bounds, not exact draws, unless the seed's values are recomputed in the test from the same `Random`.
- Pydantic error messages change between versions: tests check the **field name / location** in the error, not the full message text.
- Structured-output fixtures are invoices written by the test author (hand-checked totals). No real model output anywhere; scripted replies are labelled scripted.
- FastAPI tests (p027–p030): `TestClient(create_app(client, ...))`; import cost ≈ 0.6 s measured.

## A. The provider API and prompts (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Build the request body | drill | code | `make_body(messages, system, model, max_tokens, temperature, stream=False)` → dict in the chapter's wire format; system is a top-level field, not a message; `max_tokens` must be ≥ 1 (ValueError); messages must alternate starting with `user` (ValueError naming the index) |
| 2 | Which failures should you retry? | drill | trace | `⚠ HAND-TRACE` for 10 status codes (400, 401, 403, 404, 413, 429, 500, 503, 529, 200-with-garbage) print `retry` / `fail` and the exception class name, using the chapter's table (Ch. 1.3) |
| 3 | Classify a status into an exception | drill | code | `classify_status(status, message, retry_after)` → the chapter's hierarchy (`RateLimitError`, `ServerError`, `ContextLengthError` for 400 "prompt is too long", `AuthError`, `NotFoundError`, ...). The classes are **given in `starter.py`**; tests check `isinstance`, `.status` and `.retry_after` |
| 4 | Keep untrusted text inside the data block | applied | code | `build_messages_safe(document)` (Ch. 2.4): wraps the document in a random-tagged delimiter that the document cannot close (document containing the closing tag, or a fake `</document>`); the instructions stay in the system prompt; test tries 5 hostile documents |
| 5 | Why is the system prompt not a security boundary? | drill | explain | `assessment = "explain"`. Roles, what prompts can and cannot guarantee, why validation in code is still needed. Checklist: "the model can ignore instructions", "data vs instructions", "delimiter helps, does not guarantee", "validate the output in code" |
| 6 | Prompts are code: version and test them | applied | code | `render_prompt(template_version, **fields)` from a registry dict; unknown version → KeyError with the known versions listed; missing field → error naming it; the rendered prompt's hash is stable (tests compare to `hashlib.sha256` of the expected text) |

## B. Errors, timeouts, retries (Ch. 3.1–3.3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 7 | Exponential backoff with full jitter | drill | code | `backoff_delay(attempt, policy, rng, retry_after=None)`: in `[0, min(max_delay, base*2**(attempt-1))]`; `Retry-After` is a floor; 1,000 draws stay in bounds; the ceiling doubles then caps |
| 8 | Why jitter? | applied | trace | `⚠ HAND-TRACE` the chapter's `peak_load` idea on a tiny case: 4 clients, 3 attempts, base 1 s, no jitter → print how many requests arrive in each 1-second slot (all collide); jitter version is not traced (random) |
| 9 | Retry only what is worth retrying | applied | code | `call_with_retries(send, policy, clock, rng)` where `send()` raises the chapter's errors; retries 429/5xx/timeouts, never 400/401/404/413; stops at `max_attempts` with `RetriesExhausted(last_error, attempts)`; waits go through `clock.sleep` (test reads `clock.now`) |
| 10 | Trace a retry timeline | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` a run against `[status(429, retry_after=2), status(503), ok("hi")]` with a policy whose jitter is disabled (rng stub returning the ceiling): print each attempt number, outcome and `clock.now` |
| 11 | A deadline for the whole call | applied | code | extend p9 with `deadline_s`: never starts an attempt or a wait that would end past the deadline; raises `DeadlineExceeded`; test with `slow()` steps and `hang()`; `clock.now` never exceeds the deadline |
| 12 | The client: one call over HTTP | applied | code | `complete(transport, messages, ...)` using `httpx.Client(transport=...)`: sends key header, parses `text`, usage, `stop_reason`; maps error bodies through `classify_status`; a 200 with garbage → `MalformedResponse`; tests with `FakeProvider` |
| 13 | Retry-After as seconds and as a date | deep | trace | `⚠ HAND-TRACE` the wait in seconds that a given `parse_retry_after(value, now)` returns for 8 header values: integer, float, HTTP date 5 s after `now`, a date in the past (→ 0), negative, empty, garbage (→ None), huge (capped) |
| 14 | When do you give up? | deep | explain | three scenarios (user waiting in a chat; nightly batch of 10,000; payment-like action) → choose attempts/deadline/fallback and justify. Checklist: "user-facing deadline short", "batch can wait longer", "idempotency before retrying side effects", "budget" |

## C. Fallbacks and the circuit breaker (Ch. 3.4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Circuit breaker | applied | code | `CircuitBreaker(clock, failure_threshold, reset_after_s)` with states closed → open → half-open → closed/open; `allow()`, `record_success()`, `record_failure()`; full cycle checked with `VirtualClock` |
| 16 | Fix the fallback client | deep | code | `assessment = "fix"`. Given a `FallbackClient` with three bugs: it falls back on **our own** 400/401 errors (hiding a bug), it never skips a provider whose breaker is open, and it loses the list of errors in `AllProvidersFailed`. Tests name each bug |
| 17 | Trace a breaker | drill | trace | `⚠ HAND-TRACE` the state after each of 8 events (fail, fail, fail, call refused, time +31 s, success, fail, ...) with threshold 3 and reset 30 s |

## D. Structured output (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Lenient JSON parsing | drill | code | `parse_json_lenient(text)`: strips a Markdown code fence, takes the first complete `{...}` object (string-aware brace matching), raises `ParseError` with a short reason; tests: fenced, prose before/after, braces inside strings, two objects, truncated |
| 19 | An invoice schema in Pydantic | drill | code | `Invoice` / `InvoiceLine` with field constraints and a `model_validator` that the total equals the sum of lines (to the cent); tests check which field each bad input reports (location, not message text) |
| 20 | Grounding: every value must be in the document | applied | code | `check_grounded(invoice, document)` → list of problems: vendor and invoice number must appear in the document (normalised whitespace/case), numbers must appear as numbers (1,234.50 vs 1234.5); invented vendor is caught |
| 21 | The repair loop | applied | code | `extract(client, document, max_repairs=2)` (the chapter's flow): parse → validate → ground → on failure send the problems back; returns result with attempts and total tokens; truncated replies are **not** repaired; gives up with `ExtractionFailed` counting every token; client is the conftest `LLMClient` on a `FakeProvider` with scripted replies |
| 22 | Which layer catches it? | deep | trace | `⚠ HAND-TRACE` for 7 scripted replies (prose around JSON, wrong type, negative quantity, total mismatch, invented vendor, cut-off JSON, valid) print the layer that rejects each (`parse`, `schema`, `rule`, `grounding`, `truncated`, `ok`) |
| 23 | Valid JSON is not a correct answer | deep | explain | Ch. 4.1/4.3: why schema validation does not prove correctness; what grounding adds and still misses. Checklist: "schema checks shape", "grounding checks presence", "a value can be present but wrong", "human or eval for quality" |

## E. Streaming (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 24 | Parse server-sent events | drill | code | `parse_sse(lines)` generator of `(event, data)` with the SSE rules: blank line ends an event, `data:` lines join with `\n`, comments (`:`) ignored, missing `event` = `"message"`, trailing event without a blank line is dropped; works on an iterator (no `list()` of the input) |
| 25 | Join a stream and report totals | deep | code | `collect_stream(events)` → text, usage, stop_reason; an `error` event after some text raises `StreamInterrupted` with `partial_text`; tests use events produced by `FakeProvider` streaming (`ok(text, fail_after=3)`) |
| 26 | Trace a broken stream | deep | trace | `⚠ HAND-TRACE` the printed pieces, then the exception and partial text, for a scripted 5-piece stream that fails after 3, and whether the client retries (rule: retry only if nothing reached the user) |

## F. Budgets and the project (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | A per-user daily token budget | challenge | code | `TokenBudget(daily_limit)`: `check(user, day, estimated)` raises `BudgetExceeded` **before** the call; `record(user, day, actual)` after it (actual, not the estimate); `remaining`; days and users independent; a failed call still records the tokens the provider billed; hand-checked sequence |
| 28 | Token bucket rate limiter | applied | code | `TokenBucket(clock, capacity, rate)`: `try_acquire(n)`, `wait_time(n)`; refills by elapsed virtual time, never above capacity; hand-checked sequence with `VirtualClock` |
| 29 | A ledger of what each request cost | challenge | code | `Ledger` records request id, user, model, attempts, input/output tokens, cost (prices passed in, illustrative) including **failed attempts**; `by_user(day)` and `total()`; test: a request that needed 2 repairs costs 3 calls |
| 30 | The extraction API | challenge | code | `assessment = "build"`: `create_app(client, budget, today)` with `POST /extract` and `GET /health`. Status mapping like the chapter: invalid input 422 before any model call, budget 429, provider down 503, hang 504, context too long 413, invalid output after repairs 502, our misconfiguration 500 without leaking the key; responses carry a request id. Tests with `TestClient` and `FakeProvider` |

## Counts check

Tiers: drill 1, 2, 3, 5, 7, 10, 17, 18, 19, 24 (10); applied 4, 6, 8, 9, 11, 12, 15, 20, 21, 28 (10); deep 13, 14, 16, 22, 23, 25, 26 (7); challenge 27, 29, 30 (3). Total 30.
Kinds: trace 2, 8, 10, 13, 17, 22, 26 (7); explain 5, 14, 23 (3); code 20.
One assessment of each kind: explain p005, trace p010, fix p016, build p030.

## Risks and open questions

- p003: the error classes must exist before the solution can raise them. Put the class hierarchy in `starter.py` (given code) and test only `classify_status`.
- p021 and p030 depend on the chapter's `LLMClient`; copy it into `conftest.py` exactly (≈ 200 lines). Keep it identical across problems so a fix happens once (note the source line range of chapter §3.3 in each `conftest.py`).
- p024: the starter must not `list()` the input; one test feeds a generator that raises after the last needed line.
- Python 3.11 parse rule: the chapter uses `httpx.Response(..., json=...)` and f-strings with dict lookups; keep quotes outside `{}`.
