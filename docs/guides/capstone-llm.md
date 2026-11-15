# LLM capstone: a production LLM application with retrieval, tools, evaluation and a security review

You have finished (or nearly finished) the LLM Engineer track (llm.01 to llm.07). The capstone
proves you can combine it: build one LLM application that **answers from documents with
citations**, **uses tools safely**, is **measured by an evaluation suite**, has been
**red-teamed and hardened**, and is **served and monitored like a real service**. You choose the
application. Nobody gives you a solution. The checklist at the bottom is how you (or a reviewer)
decide it is done.

Syllabus line: *Production LLM application with retrieval, tools, evaluation suite and security
review.*

The phrase that matters is **with numbers**. Anyone can wire a model to a vector store and get a
demo that looks good. The skill this capstone tests is knowing, and showing, how often it is
right, how often it must refuse, what an attacker can make it do, what each request costs, and
whether last week's change helped or hurt.

## Rules

- **It is yours.** Your problem, your design, your words. Use the course chapters and the
  official docs, not generated analysis. A reviewer (a friend, or Claude in tutor mode) reads and
  comments; they do not rewrite it.
- **Own folder, own repo.** Keep it outside `my-work/`, with its own git history on your
  personal GitHub. Never a company account, company remote or company data.
- **Data you may use.** Public documents whose licence allows your use, documents you wrote, or
  a synthetic library you generate. Never personal data about real, identifiable people. Record
  every source, its licence and the download date in `DATA.md`, keep raw files read-only, and
  work **offline from the local copy**.
- **No key needed.** The course keeps working with no AI and no subscription, so your tests and
  your evaluation must run against **fake model backends** with scripted behaviour (llm.01 to
  llm.07 did this). A real provider is an **optional adapter** behind the same interface; if you
  add one, the key comes from an environment variable, never from the repo, and no test depends
  on it.
- **No invented results.** Every number in your report comes from code you ran. If a result
  comes from a simulated model, the report says so. Statements about how real models behave are
  labelled as general knowledge, not measurements.
- **Test only what you own.** Red-team your own application. Never attack a system you are not
  authorised to test.
- **Time-box.** Plan 5-6 weeks of part-time work. Write the problem note and the threat model
  first (below).
- **Small is fine.** A library of 20-60 documents and an evaluation set of 60-120 questions is
  enough, if the evaluation is honest about how little that set can prove.

## Pick a problem

A good problem has **documents worth asking questions about**, **one or two actions a model
could take** (so tools and permissions matter), and **something to protect** (so the security
review is real). Choose one:

1. **A help desk for a fictional or public product.** Policy and product documents, an order or
   account lookup, an email or ticket tool. (The llm.06 help desk is this, in miniature; yours
   must be built from scratch with your own documents and tools.)
2. **A study assistant over your own notes and PDFs.** Question answering with page citations,
   plus tools to create flashcards or move files, with approval before anything destructive.
3. **A personal knowledge base over a public document set** (a standard, a manual, a legal or
   technical text with an open licence): answers with exact citations, "not found" when the text
   is silent, and a tool that exports a cited summary.
4. **An operations assistant over runbooks.** Retrieval over runbooks and incident notes, a
   read-only tool that fetches service status (simulated), and a gated tool that opens a ticket.

If you cannot decide in a day, take the default: **option 1**. It already has all three
conditions of an LLM security problem (private data, untrusted content, a way out), so the
review has something to find.

## Step 0: the problem note and the threat model (2-3 pages, before any code)

Write `PROBLEM.md` and `THREAT_MODEL.md` and keep them in the repo:

1. The **user and the decision or task** the application supports, and what happens today
   without it.
2. The **documents**: sources, licences, size, how they change, who can add to them (this is
   your untrusted-content boundary).
3. The **tools**: each one, its risk class (read, write, destructive, outbound), and who can use
   it.
4. **What a good answer is**: cited, correct, and refused when the documents are silent. What a
   wrong answer costs, and what a wrong refusal costs.
5. The **requirements in numbers**: p95 latency, cost per 1,000 requests, the monthly budget,
   the minimum acceptable evaluation results.
6. The **assets** to protect (secrets, private data, the ability to act, the budget), the
   **attackers** (a curious user, a malicious user, a third party who can plant text), the
   **trust boundaries**, and the **three conditions** (private data, untrusted content, a way
   out) and which of them you will remove.
7. The three biggest **risks** and what you will try first.
8. What you are deliberately not doing.

Bring both notes to the reviewer before you write much code.

## Requirements

Tick every **Must**. Aim for most **Should** items. **Stretch** is optional.

### A. Data, ingestion and retrieval (llm.03)

- **Must:** `DATA.md` with every source, licence, date and a SHA-256 of each raw file.
- **Must:** an **ingestion pipeline** that is **re-runnable safely**: unchanged files are
  skipped (content hash), changed files replaced, deleted files removed, empty or unreadable
  files reported, and a second run changes nothing. Cleaning (headers, hyphenation, wraps) is
  code, with tests.
- **Must:** chunks with **metadata** (document, page, type, date), and **context in the indexed
  text** (title and heading), with the original text shown to the user.
- **Must:** **hybrid retrieval** (keyword plus vector, fused) with **metadata filters applied
  before ranking**, built so the embedder is swappable. It must run offline.
- **Must:** a **retrieval evaluation** on its own: recall@k and MRR on questions with a known
  gold passage, including **paraphrased** questions that share few words with the answer.
- **Must:** a quarantine check at ingestion for suspicious documents (instruction-like text,
  hidden characters, encoded blobs, outside links), with a test on a poisoned document.
- **Should:** a reranking stage, measured against no reranking.
- **Stretch:** a trained embedding model compared with your offline one, using the same
  evaluation.

### B. Generation, citations and refusal (llm.02, llm.03)

- **Must:** a **provider-neutral model interface** (`complete(system, user, max_tokens,
  timeout)` returning text, token usage and the exact model id), with **fake backends** for
  tests and a pinned-version registry in configuration that refuses aliases such as `latest`.
- **Must:** a prompt that numbers its sources, wraps untrusted text in tags with the closing tag
  defused, defines how to refuse, and carries a **version string** that is logged.
- **Must:** answers with **citations** that are **verified in code**: the cited source exists,
  quoted text really appears in it, numbers in the answer appear in the sources. An answer that
  fails verification is retried a bounded number of times and then becomes a refusal.
- **Must:** **structured output** (Pydantic) wherever code consumes the model's reply, with the
  repair loop bounded and every token counted.
- **Must:** the full **failure path**: timeouts and a deadline, retries with jittered backoff,
  `Retry-After` honoured, a circuit breaker and a fallback model, each tested with scripted
  failures.
- **Should:** streaming with time to first token recorded as its own metric.

### C. Tools, agency and approval (llm.05)

- **Must:** each tool has a **typed parameter model** (Pydantic), a **risk class**, and a
  **preview computed from the real arguments and state** by your own code.
- **Must:** a **policy per task** (allowed tools, readable and writable scopes, per-run call
  limits), enforced in code on every call; the model is never asked what it may do.
- **Must:** **approval** for destructive or outbound actions: bound to the exact action, re-checked
  before running, only an explicit yes counts, and a refusal is information for the model. Prefer
  reversible actions (soft delete, undo).
- **Must:** the agent loop has **every guard**: step limit, token budget, deadline, repeat
  detection, consecutive-error limit, user abort, and a **named stop reason** for every run.
- **Should:** checkpoints and resume after a crash, with tools that are safe to repeat.
- **Stretch:** a dry-run mode that shows the whole plan as previews before anything changes.

### D. The evaluation suite (llm.04)

- **Must:** an **evaluation dataset** in JSON Lines with checkable gold answers, **tags**,
  deliberate **unanswerable** questions (at least a quarter of the set), a **validator** that
  runs on every load, deduplication of any synthetic cases, a **dev and test split**, and a
  **fingerprint** stored in every result.
- **Must:** metrics that **separate retrieval from generation** (retrieval hit versus correct
  answer), score unanswerable cases as refusals, and track **false answers and wrong refusals
  together**, plus cost and latency per query.
- **Must:** every comparison between two versions is **paired**, with an interval and an exact
  sign test for yes/no metrics, and the report states how many questions would be needed to
  detect the effect you care about.
- **Must:** a **regression gate** with hard limits, tracked metrics and warnings, that **exits
  non-zero** when a change must not merge, refuses to compare runs on different datasets, and
  is wired into CI.
- **Must:** a **golden-set check on a schedule** that would catch a silent change of the model
  behind a pinned name (simulate one in a test).
- **Should:** if you use a model as judge, validate it against **human labels** (agreement,
  kappa, the **false accept rate**) and run the **padding and swap tests**; keep deterministic
  checks beside it.
- **Stretch:** an evaluation of the agent: scenarios with safety invariants as hard gates.

### E. Security review (llm.06)

- **Must:** `SECURITY_REVIEW.md`: the threat model from step 0 updated with what you found, the
  controls, and the residual risks you accept and why.
- **Must:** a **red-team corpus** covering all three channels (typed by the user, planted in a
  document, hidden in a tool result), each attack with a **goal measured by its effect** on the
  world, plus a list of **benign tasks**.
- **Must:** the **baseline** (attack success rate and utility with no defenses) and the result
  with the **full stack**, each **control alone**, and the stack **minus one control**
  (leave-one-out), so the report names which controls are essential and which are redundant.
- **Must:** controls that **do not depend on the model**: server-side authorization and data
  minimisation, an outbound recipient allow-list, budgets, taint and argument provenance,
  output sanitising (foreign images and links), and **no secrets in prompts**.
- **Must:** **personal data redacted before logging**, with the redactor measured on a labelled
  set and its gaps (names, addresses) stated; a retention rule.
- **Must:** the red-team run is a **CI gate**: the hardened stack must have attack success zero,
  and every attack you discover becomes a permanent test.
- **Should:** canary tokens that detect a leak of planted text.
- **Stretch:** repeat the red team against a real model, with intervals over repeated runs.

### F. Serving, observability and releases (llm.07)

- **Must:** a **FastAPI service** with request validation (422 before any model call), a
  request id (safe values only), a per-user rate limit (`429` with `Retry-After`), clean `503`
  and `504` mappings with no provider details, `/health` and a separate `/ready` that reports
  not-ready while a circuit breaker is open.
- **Must:** a **response cache** whose key contains the question, model version, prompt version,
  index version and scope, with TTL, a size limit and single-flight; personalised and fallback
  answers are never shared across keys. A test proves there are no stale answers after a model
  or index change.
- **Must:** **per-request tracking** of model version, tokens, cost, total and per-step latency,
  cache hit, fallback and citation/refusal flags, as one redacted JSON log line, Prometheus-style
  metrics with latency histograms, and a trace per request.
- **Must:** **alert rules** on p95 latency, error rate, cost per 1,000 requests, **citation rate**
  and **refusal rate**, with minimum request counts chosen with the worst case in mind, and an
  HTML-escaped dashboard.
- **Must:** a **release process**: candidates compared with the current model on the golden set
  and gated on correctness, citations, refusals, latency and cost; a **sticky canary** judged
  **by cohort**; promote and rollback in one step; a token-protected admin rollback.
- **Must:** an **incident drill** in a test: a slow provider, an outage and a recovery, with the
  alerts, the fallback and the breaker behaving as the runbook says.
- **Should:** a capacity estimate with Little's law and a concurrency limit on model calls.
- **Stretch:** a shared cache (for several workers) and standard trace export.

### G. Engineering and reproducibility

- **Must:** one command (`make all`, or `python run_all.py`) rebuilds the index, runs the
  evaluation, the red team and the tests from the raw files, and the README says how long it
  takes (machine-specific).
- **Must:** a pinned `requirements.txt`, fixed seeds, and **virtual time** in tests so a day of
  traffic runs in seconds and every latency is reproducible.
- **Must:** a `pytest` suite covering ingestion, chunking, retrieval, citation verification,
  every guard of the agent loop, the evaluation statistics (with hand-checked values), the gate,
  every defense and every attack of the corpus, the cache, the metrics, the service contract and
  the release gate. Every assert has a message naming the likely mistake.
- **Must:** git history with many small commits and clear messages, no secrets, no personal
  data, no machine-specific paths.
- **Should:** `ruff` clean, type hints on public functions, and a CI workflow that runs
  everything offline.
- **Stretch:** a Dockerfile that builds offline from pre-downloaded wheels.

### H. Communication

- **Must:** `REPORT.md` of **6-9 pages**: the answer first (what the application does, how well,
  at what cost), the problem and data, the retrieval and generation design, the tools and their
  controls, the evaluation with intervals and slices, the security review, the operating model
  (metrics, alerts, release process), and what you would do next.
- **Must:** a **model card** and a **runbook** (alert, first look, likely cause, action).
- **Must:** every number in the report is produced by code and **traceable**
  (`number -> script -> function`), and every claim about real models is labelled as general
  knowledge.
- **Must:** a 10-minute walkthrough script in which one slide is the **security review** and one
  is the **release gate catching a regression**.
- **Should:** every figure's title states its finding, and uncertainty is shown.
- **Stretch:** a recorded walkthrough.

## How the review works

1. **Problem and threat-model review** (before building): the reviewer reads `PROBLEM.md` and
   `THREAT_MODEL.md` and asks questions. Typical outcomes: "who can write into the documents?",
   "what is the worst thing the email tool can do?", "what does a wrong refusal cost?".
2. **Retrieval review** (after the first index): the reviewer asks for the retrieval numbers
   on the paraphrased questions before hearing about the model, then tries to break ingestion
   (change a file, delete one, add a poisoned one).
3. **Midpoint check:** ingestion is re-runnable, retrieval and the evaluation dataset exist with
   a baseline, the model interface and fakes work, and the first honest numbers are recorded.
4. **Agent and security review:** the reviewer plays attacker for 30 minutes (a poisoned
   document, a hostile tool result, an obfuscated message) and checks that your corpus already
   contained the attack, or adds it to the corpus as a failing test.
5. **Release and operations review:** the reviewer hands you a "new model version" that is
   cheaper and worse, and you show the gate blocking it; then breaks the provider and you show
   the alert, the fallback, the breaker and the runbook.
6. **Fresh-machine test:** clone the repo into a new folder, follow only the README, and
   rebuild everything offline. If you get stuck, the README is the bug.
7. **Challenge drill:** the reviewer picks three numbers from the report and asks "show me". You
   trace each to a script and a row count within a few minutes.

### Scoring (for yourself)

| Score | Meaning |
|---|---|
| All Musts, most Shoulds | LLM capstone passed |
| All Musts only | Passed, but go back and add the missing polish and tests |
| Any Must missing | Not done yet. Finish those first |
| Any Must in section E (security) or D (evaluation gate) missing | Not done, whatever else is complete |

Stretch items are for pride and for your portfolio, not for the pass mark.

## Suggested order (6 weeks)

| Week | Goal |
|---|---|
| 1 | Problem note, threat model, data and ingestion (re-runnable), chunking, the evaluation dataset and its validator |
| 2 | Hybrid retrieval and its evaluation, quarantine, the model interface with fakes, citations verified in code |
| 3 | Tools, policies, approvals and the agent loop with every guard |
| 4 | The evaluation suite end to end: slices, paired comparisons, the CI gate, the golden-set check |
| 5 | The red team: corpus, baseline, controls, leave-one-out, the CI gate; privacy and logging |
| 6 | The service: cache, metrics, alerts, release gate and canary, incident drill; report, model card, runbook |

## Why this capstone

Each piece of the track is easy to build alone and easy to get wrong in combination. A retriever
that looks good on questions copied from the documents fails on paraphrases; a citation that
nobody verifies is decoration; a tool that works is a liability until its permissions, approvals
and previews exist; a cheaper model can quietly make answers worse while every dashboard stays
green; and a defense nobody measured against an attacker is a hope. By building the whole
application with an evaluation suite, a security review and an operating model, you practise the
habit that matters for life: **a claim you cannot measure and defend is not a result**, and a
system you cannot watch is not finished.
