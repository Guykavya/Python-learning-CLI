# Problem plan: llm.06 Security for LLM applications (25 problems)

Rules: [README.md](README.md) (shared, read R1–R5 first) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `llm.06.p001` … `p025`, folder `pNNN-slug`. Requires llm.03 and llm.05.

**Mix:** 7 drill, 10 applied, 5 deep, 3 challenge. **Kinds:** 18 code, 4 trace, 3 explain.
**assessment:** explain = p008, trace = p004, fix = p014, build = p025.
**★ core set (write first):** p003, p004, p007, p008, p010, p012, p014, p017, p021, p023, p025.

**Testing notes**
- **The model is a deliberately obedient fake.** The chapter's `obedient_model(messages, tools, system="")` follows any instruction it finds in any text (user, document or tool result) — a worst-case model, not a real one. It, the `ScriptedModel` boundary from llm.05 (`ToolCall`, `ModelReply`, `say`, `call`, `calls`), the Kestrel help desk (`Customer`, orders, documents, `HelpDesk(docs, defenses, model)`, `Defenses.none() / filters_only() / capabilities_only() / full()`, `Outcome`) and the attack list (`Attack`, `ATTACKS`, `BENIGN`, `goal_reached`) go **verbatim into `conftest.py`** when a problem needs the live app. The learner's code receives them as arguments.
- **No real model output and no real attack transcripts.** Attacks are the chapter's scripted strings; anything about real systems is labelled *(general knowledge)*.
- **Path escapes** appear in p023 (attachment reader) with the full list from llm.05: `..`, absolute, `C:\`, UNC, null byte, symlink outside (skip that one test on Windows `OSError`), all in `tmp_path`.
- PII in tests is obviously fake (`asha@example.com`, `+91 98765 00000`, card `4111 1111 1111 1111`). HMAC keys are passed in, never read from the environment.
- The chapter's mini RAG (`RagSystem`, BM25 + LSA) is needed only in p021/p025; keep the document set tiny (≤ 6 docs).

## A. Threat model and injection (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Threat-model one feature | drill | explain | Ch. 1.1, 1.4: for "summarise my inbox and draft replies", answer the four questions and say which of the three conditions it has (private data, untrusted content, a way to send data out). Checklist: names all three, one concrete attack, one control that removes a condition |
| 2 | Trace the normaliser | drill | trace | `⚠ HAND-TRACE` the chapter's `normalise` and `instructions_in` on 6 strings (zero-width characters, full-width letters, mixed case, base64 payload, Markdown comment, a harmless sentence); printed as `repr` of plain strings |
| 3 | An injection scanner | drill | code | `scan_for_injection(text)` → list of matched pattern names after normalising (NFKC, zero-width removal, case) and decoding base64 runs; tests: 8 attacks found, obfuscated forms found, 6 benign texts not flagged |
| 4 | Which attacks get past the filter? | applied | trace | `assessment = "trace"`. `⚠ HAND-TRACE` for 8 messages print `blocked` or `passed` with the chapter's `scan_for_injection` (some paraphrased attacks pass, one benign message is blocked) |
| 5 | Measure a filter honestly | applied | code | `filter_report(scan, attacks, benign)` → catch rate, false-positive rate, the list of missed attacks and blocked benign messages; denominators reported; hand-checked on given lists |

## B. Documents and tool results are untrusted (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Provenance and taint | drill | code | `ContextItem(text, source)` with sources `system`, `user`, `document`, `tool`; `tainted(items)` true when any non-user, non-system item is present; `args_from_user(args, items)` true only if every argument value appears in a **user** item |
| 7 | Quarantine at the door | applied | code | `quarantine_reasons(text)` at ingestion: hidden instructions, invisible characters, long base64 blobs, links to non-allow-listed domains, text inside HTML comments; returns reasons; clean documents → `[]`; quarantined docs never reach the index (test with a 4-doc ingest) |
| 8 | Why are documents and tool results untrusted? | drill | explain | `assessment = "explain"` (Ch. 4): the model cannot tell data from instructions; anyone who can write a document or a web page can write to your prompt; filters miss paraphrases; make mistakes harmless instead. Checklist: "indirect injection", "same channel for data and instructions", "provenance", "capabilities over filters" |
| 9 | Tool arguments must come from the user | applied | code | `guard_send_email(call, items, customer)`: the recipient must be the customer's own address **or** appear in a user message; an address found only in a retrieved document is refused with a reason; case-insensitive compare |

## C. Limiting permissions and data exposure (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | The confused deputy | drill | code | `lookup_order(orders, customer_id, order_id)`: returns the order only if the customer owns it; "not yours" and "not found" give the **same** message (no enumeration); order ids compared exactly (not by prefix) |
| 11 | Recipients and budgets for outbound actions | applied | code | `OutboundGuard(allowed_domains, max_per_conversation)`: `allow(to)` checks the exact domain (not `endswith` on the raw string: `evil-kestrel.example` and `kestrel.example.evil.com` fail), counts sends per conversation |
| 12 | The answer is untrusted too | applied | code | `sanitize_output(text, allowed_hosts)`: removes Markdown images and links to non-allowed hosts (the exfiltration channel: `![x](https://evil.example/?d=SECRET)`), escapes HTML, keeps allowed links; `link_allowed(url)` parses with `urllib.parse` (userinfo `https://kestrel.example@evil.example` is evil) |
| 13 | Trace the help desk with capabilities only | deep | trace | `⚠ HAND-TRACE` the `Outcome` fields (`tool calls made`, `blocked`, `leaked`) for 4 attack messages against `HelpDesk(..., Defenses.capabilities_only())` with the obedient model |
| 14 | Fix the help desk | deep | code | `assessment = "fix"`. Given a `HelpDesk` with three bugs: taint is set for documents but not for **tool results**, the link allow-list uses `startswith("https://kestrel.example")`, and the order lookup reveals whether an order exists. Each test names one bug |

## D. Secrets, logging and privacy (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Mask and redact personal data | drill | code | `mask_email("asha@example.com") == "a***@example.com"`, `redact(text)` replaces emails, phone numbers and card numbers (Luhn-valid 13–19 digits with spaces/dashes) with tags; `pii_found(text)` lists kinds; 10-case table, no false hit on order ids |
| 16 | Canaries: notice a leak | applied | code | `make_canary(rng)` and `leaked(output, canary)`: detects the canary verbatim, with spaces/dashes between characters, reversed, and base64-encoded; does not fire on a different random canary |
| 17 | A privacy-safe log line | applied | code | `log_record(request, reply, key)` → dict with request id, `user = hmac_sha256(key, user_id)[:16]`, redacted text lengths, tool names, decision; test serialises the log and asserts no email, phone, card or raw user id appears |
| 18 | What never goes in a prompt | deep | explain | Ch. 6.1, 6.4: secrets, other customers' data, internal ids that grant access; why "the model is told not to reveal it" is not protection. Checklist: "anything in the prompt can leak", "secrets stay in code/tools", "minimise data", "logs are data too" |

## E. The red-team harness and the project (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Did the attack work? | applied | code | `goal_reached(goal, outcome)` for the chapter's goals (leak another customer's data, email an outsider, reveal the canary, emit an exfiltration link, change an order not owned); tests with hand-built `Outcome`s for each goal, success and failure |
| 20 | One control removed | deep | trace | `⚠ HAND-TRACE` the success table printed by a given `summarise(results)` for 4 stacks × 5 attacks (results given as data), including the totals and benign pass rate |
| 21 | A red-team harness | challenge | code | `run_redteam(make_app, defenses_list, attacks, benign)` → per stack: attacks that succeeded, benign pass rate; report sorted; uses the conftest help desk; tests: `none` loses most attacks, `full` loses none and keeps benign ≥ the chapter's level |
| 22 | Write attacks that beat the filter | deep | code | the learner writes `ATTACKS = [...]` (3 `Attack` objects) that **succeed against `filters_only`** and **fail against `full`**; the test runs each; message explains which condition was missing |
| 23 | Attachments: read only inside the folder | applied | code | `read_attachment(root, name)` for the help desk's attachment tool: every path escape refused (see testing notes), only allow-listed extensions, size cap; files made in `tmp_path` |
| 24 | A security gate in CI | challenge | code | `security_gate(report, baseline)` fails when any attack newly succeeds, when benign pass rate drops more than a stated tolerance, or when an attack disappeared from the suite (silent deletion); returns readable reasons |
| 25 | Red-team and harden the help desk | challenge | code | `assessment = "build"`: `harden(helpdesk_factory)` returns a help desk with the learner's controls (taint, argument provenance, ownership, outbound allow-list, output sanitising, redacted logs). Tests: every chapter attack plus 3 new hidden ones fail, all benign requests still succeed, logs contain no PII |

## Counts check

Tiers: drill 1, 2, 3, 6, 8, 10, 15 (7); applied 4, 5, 7, 9, 11, 12, 16, 17, 19, 23 (10); deep 13, 14, 18, 20, 22 (5); challenge 21, 24, 25 (3). Total 25.
Kinds: trace 2, 4, 13, 20 (4); explain 1, 8, 18 (3); code 18.
One assessment of each kind: explain p008, trace p004, fix p014, build p025.

## Risks and open questions

- The help desk + obedient model + attacks are ≈ 500 lines of chapter code. Copy them once into a shared `conftest.py` text and reuse it byte for byte in p013, p014, p019, p021, p022, p025; note the chapter line range at the top.
- p022 is open-ended: the test must only check behaviour (succeeds vs `filters_only`, fails vs `full`), never the wording of the attack.
- p025 hidden attacks must be variations of the chapter's families (encoded, indirect via document, via tool result, exfil link), not new families the chapter never taught.
- p015 regexes: card detection must use Luhn, or order numbers like `4111-2222` produce false hits; state the rule.
