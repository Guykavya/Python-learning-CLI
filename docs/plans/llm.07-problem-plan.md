# Problem plan: llm.07 Shipping LLM applications (20 problems)

Rules: [README.md](README.md) (shared, read R1–R5 first) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `llm.07.p001` … `p020`, folder `pNNN-slug`. Requires llm.04 and swe.09 (FastAPI, health checks, structured logs, Prometheus text format).

**Mix:** 7 drill, 7 applied, 4 deep, 2 challenge. **Kinds:** 13 code, 4 trace, 3 explain.
**assessment:** explain = p008, trace = p007, fix = p016, build = p020.
**★ core set (write first):** p001, p004, p005, p007, p008, p009, p013, p016, p020.

**Testing notes**
- **The provider is a fake backend.** The chapter's `ModelSpec` (id, version, illustrative prices, speed, quality), `FakeBackend(spec, clock)` with `.complete(system, user, max_tokens=300, timeout=None) -> Completion` (text, tokens, cost, latency), `BackendError(message, status, retryable)`, `BackendTimeout`, and `VirtualClock(start=0.0)` with `.time()` / `.sleep()` go in `conftest.py`. Outages, slowness and a "silently changed" model are switches on the fake. No real provider, no real output; prices are illustrative and passed in.
- The compact `RagSystem` (BM25 + LSA, extractive answers) from llm.04 is the pipeline's retriever; copy it into `conftest.py` only for p016 and p020, with ≤ 4 small documents.
- **FastAPI:** `TestClient(create_app(pipeline, router, clock, ...))`; never a real server, never real time. Measured import ≈ 0.6 s.
- p006 (single flight) uses real threads with a `threading.Barrier`; keep ≤ 20 threads (runner sets `MALLOC_ARENA_MAX=2`, so the 1 GiB cap allows ~110) and a join timeout so a deadlock fails fast instead of hitting the 60 s cap.
- Percentiles use the chapter's **nearest-rank** definition (state it; NumPy's default interpolation gives different numbers).

## A. The provider side (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Pin exact model versions | drill | code | `load_registry(path)` reads a JSON registry written by the test in `tmp_path` → `{id: ModelSpec}`; refuses aliases (`latest`, a missing version), duplicate ids and missing prices with a message naming the entry |
| 2 | Trace the bill for four calls | drill | trace | `⚠ HAND-TRACE` cost (`:.6f`) and latency (`:.2f`) of 4 calls with given token counts on two illustrative `ModelSpec`s (ttft + tokens / speed) |
| 3 | Retry once, then fall back | applied | code | `ReliableBackend(primary, fallback, clock, max_attempts=2, base_delay=0.2)`: retries a retryable error once (virtual wait), never retries a non-retryable one, falls back and marks the answer `served_by="fallback"`; a breaker stops calling a primary that keeps failing; no fallback → clean `BackendError` |

## B. Caching responses (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 4 | A cache key that changes when the answer would | drill | code | `normalise_question(q)` and `cache_key(question, *, scope, model_id, prompt_version, index_version)`: whitespace/case variants share a key; changing **any** of scope, model, prompt version or index version changes it; stable `sha256` hex |
| 5 | TTL and LRU | applied | code | `ResponseCache(clock, ttl_s, max_items)`: `get` returns `None` after expiry (virtual clock), `put`, least-recently-**used** eviction (a `get` refreshes), `hit_rate`, `clear`, `len` |
| 6 | One computation for many simultaneous misses | challenge | code | `get_or_compute(key, compute)` with single flight: 20 threads asking for the same missing key run `compute` once and all get its value; an exception in `compute` reaches every waiter and is **not** cached; different keys compute in parallel |
| 7 | Trace a cache over traffic | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` hit/miss/evict for 10 requests with `ttl_s=30`, `max_items=2` and given virtual times, then the hit rate |
| 8 | What must never be cached? | deep | explain | `assessment = "explain"` (Ch. 3.4): answers personal to one user served to another, fallback/degraded answers during an outage, answers after an index or model change, refusals caused by an error. Checklist: "scope in the key", "versions in the key", "do not cache degraded answers", "TTL is not correctness" |

## C. Observability (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Nearest-rank percentiles | drill | code | `percentile(values, p)` nearest rank; hand-checked p50/p95/p99 on 20 values; p = 0 and 100; empty → ValueError; input not mutated |
| 10 | Metrics with labels, in text format | applied | code | `Metrics` with `inc(name, labels)`, `observe(name, value, labels)` and `render()` in Prometheus text format: sorted, labels escaped (`"` and `\`), counters end in `_total`; hand-checked output lines |
| 11 | Spans and a waterfall | applied | code | `Trace(clock)` with nested `span(name)` context managers; durations from the virtual clock; `waterfall()` text with indentation and offsets; a span that raises is closed and marked `error` |
| 12 | Silent change: same name, different model | drill | explain | Ch. 6.4–6.5: why a provider changing the model behind a name breaks you, how pinning, a golden set and per-version metrics catch it. Checklist: "pin versions", "golden set nightly", "compare by version label", "rollback path" |
| 13 | Alert rules | applied | code | `window_stats(records)` and `evaluate_alerts(records, rules)`: an alert needs a minimum number of requests, respects direction (`above` for latency/cost, `below` for cited-answer rate), reports value and threshold; hand-checked |
| 14 | Trace the alerts | applied | trace | `⚠ HAND-TRACE` the window stats (p95 latency nearest-rank, error rate, cost per request) and the fired alerts for 8 given records and 3 rules |
| 15 | Percentiles, not averages | drill | explain | Ch. 4.2: why the mean hides the slow tail; who the p99 user is; why averages of percentiles are wrong. Checklist: "tail latency", "mean pulled by outliers / hides them", "do not average percentiles across windows", "alert on p95/p99" |

## D. Serving and model changes (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 16 | Fix the service | deep | code | `assessment = "fix"`. Given a FastAPI `create_app` with three bugs: the cache key ignores the model id (an old model's answer is served after a switch), the fallback answer during an outage is cached (poisoning), and the 503 body leaks the exception text and has no request id. Tests with `TestClient` name each bug |
| 17 | Rate limit with Retry-After | applied | code | per-user `TokenBucket(clock, capacity, rate)` inside the app: the (capacity+1)-th request in a burst gets 429 with a `Retry-After` header equal to the wait in whole seconds (rounded up); after advancing the virtual clock the user is served; another user is unaffected |
| 18 | Sticky canary routing | deep | code | `sticky_bucket(user_id, salt)` (sha256 → 0..99) and `ModelRouter`: `start_canary(model, percent)`, `promote`, `rollback`; a user never flips between versions while the percentage is unchanged; 10,000 synthetic users split within ±2 % of the target |
| 19 | Should the new model ship? | deep | trace | `⚠ HAND-TRACE` the decisions the chapter's `gate_release(old_rows, new_rows, max_cited_drop, max_latency...)` prints for 3 candidate models with given golden-set summaries (cheaper and equal; regressed; cheapest but worse), with the sign-test p (`:.3f`) |

## E. The project (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | The monitored RAG service | challenge | code | `assessment = "build"`: `create_app(pipeline, router, clock, rate_limiter=None, rules=...)` with `POST /ask` (answer, citations, cost and request-id headers; input validated before any model call), `GET /metrics`, `GET /health/live` and `/health/ready` (not ready while the breaker is open), `GET /dashboard` (HTML-escaped), `POST /admin/rollback`. Tests mirror Ch. 8.2 with new scenarios: cache hit costs nothing, outage falls back and is not cached, total outage is a clean 503 with a request id, timeout 504, slow provider fires the latency alert, logs contain no personal data |

## Counts check

Tiers: drill 1, 2, 4, 7, 9, 12, 15 (7); applied 3, 5, 10, 11, 13, 14, 17 (7); deep 8, 16, 18, 19 (4); challenge 6, 20 (2). Total 20.
Kinds: trace 2, 7, 14, 19 (4); explain 8, 12, 15 (3); code 13.
One assessment of each kind: explain p008, trace p007, fix p016, build p020.

## Risks and open questions

- p006 threads: use a join timeout of ~5 s and assert all threads finished, so a learner's deadlock fails with a clear message instead of the runner's 60 s stop.
- p010: the exact text format (ordering, `# TYPE` lines) must be stated in `problem.md`; the test compares lines, so the statement is the contract.
- p020 is the largest problem in the track; it may take two sessions to write. Its `conftest.py` holds `FakeBackend`, `RagSystem`, `VirtualClock` and a small golden set.
- Docker, a real server, real Prometheus and real dashboards are **not** part of any problem (swe.09 covers them as tutorials).
