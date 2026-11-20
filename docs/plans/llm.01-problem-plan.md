# Problem plan: llm.01 LLM fundamentals for builders (20 problems)

Rules: [README.md](README.md) (shared, read R1–R5 first) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `llm.01.p001` … `p020`, folder `pNNN-slug`. Requires swe.02, core.09: no pydantic yet, dataclasses are fine.

**Mix:** 8 drill, 7 applied, 3 deep, 2 challenge. **Kinds:** 13 code, 4 trace, 3 explain.
**assessment:** explain = p006, trace = p002, fix = p016, build = p020.
**★ core set (write first):** p001, p002, p004, p006, p008, p011, p014, p016, p020.

**Testing notes**
- **No real provider, no key, no invented model output.** Every reply is scripted. `tiktoken` is not installed (checked); token counts use the chapter's `estimate_tokens` (`ceil(len/4)`) or the learner's own BPE.
- **FakeLLM** (chapter §1.3) goes in each problem's `conftest.py` as a fixture factory, copied verbatim with `ContextTooLong`, `RateLimited`, `estimate_tokens`, `input_tokens`, `FRAMING = 4`, `Usage(input_tokens, output_tokens)`, `Reply(text, usage, stop_reason, latency_s)`.
  Interface: `FakeLLM(replies=("OK.",), *, context_window=8000, ttft_s=0.4, tokens_per_s=60.0, counter=estimate_tokens, fail_first=())`;
  `.complete(messages, *, system=None, max_tokens=256, temperature=1.0) -> Reply`; `replies` is a cycling list or a function `messages -> str`;
  `stop_reason` is `"end_turn"` or `"max_tokens"` (truncates text to `max_tokens*4` chars); `.calls` records every Reply; `fail_first` raises the listed exceptions first.
  The solution receives the fake as an argument (`def f(llm, ...)`) and never imports it. `problem.md` shows the interface and points to chapter §1.3 for the code.
- Prices and speeds are **illustrative** values passed in (a small `Price(input_per_mtok, output_per_mtok, cached_per_mtok)` dataclass defined in the test), never real provider prices. Say so in each `problem.md`.
- Money: compare with `pytest.approx(..., rel=1e-9)`; hand-check every expected cost in `solution.md`.
- Everything is the standard library; each test file runs in well under a second.

## A. A call, its bill and its stop reason (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Never trust a cut-off reply | drill | code | `complete_or_raise(llm, messages, max_tokens)` returns the text or raises `Truncated` (defined in solution) when `stop_reason == "max_tokens"`; message names the cap; FakeLLM scripted long and short replies; checks exactly one call was made |
| 2 | Trace three FakeLLM calls | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` the printed `usage`, `stop_reason` and latency (`%.2f`) of three calls (one normal, one cut by `max_tokens=5`, one with a system prompt); the code in `problem.md` prints ints and formatted floats only |
| 3 | Count the input tokens of a conversation | drill | code | `count_input(messages, system=None, counter=...)` with `FRAMING = 4` per message and for the system prompt; empty content = 0 + framing; hand-checked totals; counter is injected (test passes a counter that counts words) |

## B. Tokens (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 4 | Train byte-pair encoding | applied | code | `train_bpe(text, n_merges)` + `bpe_encode`; **the chapter's tie rule** (most frequent, ties by `max` of the pair tuple) and end-of-word marker stated in `problem.md`; hand-checked merges on `"low lower lowest"`; `n_merges` larger than possible stops early; encode→join round-trips |
| 5 | Trace the BPE merges | applied | trace | `⚠ HAND-TRACE` the first 4 merges and the token list of one word for a 6-word corpus; includes one tie so the tie rule matters |
| 6 | Why can't the model count the r's? | drill | explain | `assessment = "explain"` (Ch. 2, 7.2): tokens, not letters; digits split oddly; what to do instead (code). Checklist: "token", "sub-word", "does not see characters", "use code / a tool", "verify" |

## C. Context windows and conversations (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 7 | What a long chat really costs | applied | code | `billed_input(turns, user_tokens, reply_tokens)` closed form; test compares with a brute-force loop for 1..30 turns and checks the quadratic growth (doubling turns ≈ 4× tokens) |
| 8 | Keep the history inside the window | applied | code | `fit_history(messages, window, max_tokens, counter)` keeps the newest messages that fit `window - max_tokens`, never drops the newest user message, keeps user/assistant alternation (starts with a user message), raises `ContextTooLong` if the newest alone does not fit; run with FakeLLM to show no `ContextTooLong` across 30 turns |
| 9 | Trace a sliding window | drill | trace | `⚠ HAND-TRACE` the chapter's `"window"` strategy (`history[-keep:]`, keep=3): which message numbers are sent at turns 1–5 and the billed input per turn with fixed message sizes |

## D. Sampling settings (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Softmax with a temperature | drill | code | `softmax(scores, temperature)` returns dict token→prob; sums to 1 (`approx`); scores of 1000 do not overflow (subtract max); temperature → 0 equals argmax (the statement defines `temperature == 0` as greedy); higher T raises entropy |
| 11 | Top-k and top-p filters | applied | code | `top_k(dist, k)`, `top_p(dist, p)`: renormalised; keeps at least one token; `p=1.0` keeps all; tie at the cut-off kept by the stated rule (stable order by prob desc then token); compared with a slow obvious version on seeded random distributions |
| 12 | Trace a nucleus cut | drill | trace | `⚠ HAND-TRACE` for a 6-token distribution, which tokens survive `p = 0.8` and their renormalised probabilities printed with `:.2f` |
| 13 | Which setting for which job? | deep | explain | Ch. 4.5: choose temperature/top-p for 6 jobs (extraction, code, brainstorming, classification, story, eval-judge) and justify two. Checklist: "deterministic for checking", "temperature 0 is still not a guarantee", "diversity costs consistency" |

## E. Cost, latency and choosing a model (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 14 | Cost of one call | drill | code | `call_cost(in_tok, out_tok, price, cached_tok=0)` per million tokens; cached tokens billed at the cached price and not again at full price; `cached_tok > in_tok` → `ValueError`; no cached price → cached tokens cost full price; hand-checked |
| 15 | From one call to a monthly bill and a peak | applied | code | `estimate(calls_per_day, in_tok, out_tok, price, speed, cached_share, retry_overhead, peak_factor, days)` returns monthly cost, p50 latency and peak concurrency (Little's law: rate × latency); hand-checked numbers; `cached_share` outside 0..1 → `ValueError` |
| 16 | Fix the cost estimator | deep | code | `assessment = "fix"`. Given an estimator with three bugs (prices read per thousand instead of per million; cached tokens billed twice; latency forgets time-to-first-token). Tests hand-checked; each failing message names one bug |
| 17 | Ask the small model first | challenge | code | Ch. 6.2: `route(question, small, large, validate)` calls `small` (a FakeLLM) and escalates to `large` only when `validate` fails or the reply is cut off; returns text, model used, total cost. Tests: escalation count on 10 scripted questions, cost equals the sum of both calls when escalated, never calls `large` when `small` passes |

## F. What models are bad at, and the project (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Retry with validation | applied | code | `checked_call(llm, messages, validate, tries=3)` (Ch. 7.4): returns `(reply or None, attempts, billed_input)`; feedback message appended after each failure; billed input grows with each retry (hand-checked); a truncated reply counts as invalid; FakeLLM with scripted bad, bad, good replies |
| 19 | Review a cost estimate | deep | explain | a one-page estimate (given) with 5 hidden problems: history re-sent but costed once, no retries, average instead of peak, prices hard-coded as facts, output tokens guessed from the input. Checklist names the 5 problems and one fix each |
| 20 | Token and cost calculator | challenge | code | `assessment = "build"`: the project library in slices: `estimate_tokens(text, method)`, `token_range`, `load_models(path)` (JSON written by the test in `tmp_path`, validated with clear errors), `compare(spec, models)` sorted by monthly cost, `verdict` with reasons, `main(argv)` exit codes 0/1. Tests mirror chapter §8.3 but with new numbers; models marked illustrative |

## Counts check

Tiers: drill 1, 2, 3, 6, 9, 10, 12, 14 = 8; applied 4, 5, 7, 8, 11, 15, 18 = 7; deep 13, 16, 19 = 3; challenge 17, 20 = 2. Total 20.
Kinds: trace 2, 5, 9, 12 = 4; explain 6, 13, 19 = 3; code = 13. One assessment of each kind (p006, p002, p016, p020).

## Risks and open questions

- p004/p005: the chapter breaks ties with `max(pairs, key=lambda p: (pairs[p], p))`, i.e. the alphabetically **largest** pair wins. State that exactly; a learner using `most_common` gets a different order. Hand-trace p005 with that rule.
- p008: "fit" has several reasonable definitions. The statement must fix one (newest-first greedy, whole messages only, first sent message must be `user`) and the tests check only that definition.
- p010: the chapter's `softmax` may not define `temperature == 0`; the statement defines it. Do not test float equality of probabilities; use `approx`.
- p017: costs are illustrative; the test passes the prices.
