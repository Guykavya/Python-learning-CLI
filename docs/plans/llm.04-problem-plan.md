# Problem plan: llm.04 Evaluating LLM applications (25 problems)

Rules: [README.md](README.md) (shared, read R1–R5 first) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style. Ids `llm.04.p001` … `p025`, folder `pNNN-slug`. Requires llm.03.

**Mix:** 9 drill, 9 applied, 4 deep, 3 challenge. **Kinds:** 18 code, 4 trace, 3 explain.
**assessment:** explain = p008, trace = p003, fix = p021, build = p025.
**★ core set (write first):** p002, p003, p004, p008, p009, p012, p016, p019, p021, p023, p025.

**Testing notes**
- **System under test:** the chapter's compact `RagSystem(docs, cfg=Config())` with `.retrieve(question, pool)` and `.answer(question) -> Result` (Ch. 1.2; BM25 + LSA + RRF + rerank + extractive answerer, no model at all). Copy it verbatim into `conftest.py` when a problem needs a live system; most problems need only **run records** (dicts) written in the test.
- **The judge is simulated:** the chapter's `SimulatedJudge(accuracy, leniency, verbosity_bias, position_bias, seed)` with `.grade(answer, truth) -> str` and `.pairwise(quality_a, quality_b) -> str` goes in `conftest.py`. It is a model of a judge with known biases, not a real model; `problem.md` says so. No real model output anywhere.
- **Statistics:** the solution may use `math` and `random` only (as the chapter). Bootstrap uses an injected `random.Random(seed)`; tests check properties (interval contains the point estimate, narrows with n, paired is narrower than unpaired on correlated data) or recompute with the same seeded `Random`. Sign test and Wilson interval are hand-checked to 4 decimals; `scipy.stats.binomtest` / `proportion_confint`-style values may be used **in the test** as a second opinion (scipy installed).
- Eval cases: `EvalCase(id, question, gold_doc, gold_phrase, kind, tags)` like the chapter; small hand-written sets of 6–12 cases on 3–4 short synthetic documents.

## A. Datasets (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Normalise, exact match, contains | drill | code | `normalise(text)` (lower, strip punctuation and articles as the chapter), `exact_match(pred, gold)`, `contains_phrase(pred, phrase)`; table of 10 pairs including punctuation, case, numbers `1,000` vs `1000` (statement says: not equal) |
| 2 | Token F1 | drill | code | `token_f1(pred, gold)` with multiset overlap; both empty → 1.0, one empty → 0.0; repeated words counted once per occurrence; hand-checked |
| 3 | Trace five metrics on five answers | drill | trace | `assessment = "trace"`. `⚠ HAND-TRACE` exact match, contains, token F1 (`:.2f`) for 5 answers to one question (the chapter's blind-spot set style: correct but long, wrong but overlapping, negated, number changed, refusal) |
| 4 | Validate the eval cases | applied | code | `validate_cases(cases, docs)` → list of problems: duplicate ids, unknown gold doc, gold phrase not in its doc (normalised), unanswerable case with a gold phrase, empty question; each problem names the case id |
| 5 | Near-duplicate questions | applied | code | `near_duplicates(cases, threshold=0.8)` by token Jaccard; returns pairs `(id_a, id_b, score)` sorted; `drop_duplicates_of(hand, synthetic)` keeps hand-written cases; hand-checked scores |
| 6 | A stable dev/test split and a fingerprint | drill | code | `split_dev_test(cases, test_fraction, salt)` by `sha256(salt + id)` so adding cases never moves old ones; `dataset_hash(cases)` independent of list order, changes when any field changes; tests add cases and check no old case moved |
| 7 | Do two labellers agree? | drill | code | `cohens_kappa(a, b)`; hand-checked on a 10-label example; perfect agreement → 1.0; the degenerate case where both use one label (expected agreement 1) returns 1.0 if identical (statement rule); unequal lengths → ValueError |
| 8 | Why evaluate retrieval separately? | drill | explain | `assessment = "explain"` (Ch. 3.1): a wrong answer can come from retrieval or generation; fixing the wrong stage wastes work; recall@k is cheap and needs no judge. Checklist: "two stages", "diagnose which failed", "retrieval metrics need only ids", "generation can only use what was retrieved" |

## B. Retrieval and answer metrics (Ch. 3–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Which stage failed? | applied | code | `diagnose(case, retrieved_doc_ids, answer_ok, refused)` → `"ok"`, `"retrieval"` (gold doc not retrieved), `"generation"` (retrieved, still wrong), `"false_refusal"`, `"correct_refusal"`, `"false_answer"` (answered an unanswerable case); 8 cases |
| 10 | Trace a diagnosis table | applied | trace | `⚠ HAND-TRACE` the stage counts the chapter's runner prints for 6 given run records, and the slice by `kind` |
| 11 | Synthetic cases: cheap and dangerous | drill | explain | Ch. 2.4: why generated questions inflate scores (they copy the document's words), when they are still useful. Checklist: "lexical overlap favours keyword retrieval", "no real user phrasing", "use for coverage, not for the headline number", "dedupe against hand-written" |
| 12 | Measure both sides of refusing | applied | code | `refusal_rates(records)` → false-answer rate (on unanswerable) and false-refusal rate (on answerable) with their denominators; empty denominators → `None` not 0; hand-checked |
| 13 | Support score | applied | code | `support_score(answer, sources)` = share of answer sentences whose content tokens are ≥ 60 % covered by one source (the chapter's rule, stated); a refusal returns 1.0 by statement rule; hand-checked on 4 answers |
| 14 | The blind spots of cheap metrics | deep | explain | Ch. 4.2: for the five answers of p003, say what each metric gets wrong and what catches it instead. Checklist: "negation keeps overlap", "length lowers F1 for correct answers", "numbers need exact checks", "refusal needs its own metric" |

## C. Model-graded evaluation (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Parse the judge's verdict | drill | code | `parse_verdict(text)` → `True`, `False` or `None`: accepts `PASS`/`FAIL`, `Verdict: pass`, JSON `{"verdict": "fail"}`; both words present or neither → `None`; never guesses; 12 inputs |
| 16 | Compare the judge with human labels | applied | code | `agreement_report(human, judge)` → agreement, kappa (reuse p7 logic), abstain rate (judge `None`), false-pass and false-fail counts; abstentions excluded from agreement but reported; hand-checked |
| 17 | Test the judge for position bias | challenge | code | `position_flip_rate(judge, pairs)` asks `pairwise` in both orders for each pair and counts verdicts that do not swap; `debiased_preference` counts a win only when both orders agree; tests with `SimulatedJudge(position_bias=0.0)` (≈ 0 flips) and `0.3` (clearly more), using fixed seeds and wide margins |

## D. Statistics for small test sets (Ch. 6–7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Wilson interval | drill | code | `wilson_interval(successes, n, z=1.96)`; hand-checked to 4 decimals (and against a second formula in the test); `n = 0` → ValueError; 0/10 and 10/10 stay inside [0, 1] |
| 19 | Paired difference: bootstrap and sign test | deep | code | `paired_difference(new, base, n_boot, seed)` on per-case 0/1 scores keyed by case id (mean diff + bootstrap CI), `sign_test_p(improved, worsened)` exact two-sided binomial with ties dropped; hand-checked p-values (e.g. 8 vs 1 → 0.0391) |
| 20 | Is the change real? | deep | trace | `⚠ HAND-TRACE` for 4 comparisons (improved/worsened/ties counts given) print the sign-test p (`:.3f`) and the decision at α = 0.05 |
| 21 | Fix the comparison | deep | code | `assessment = "fix"`. Given `compare_runs` with three bugs: compares averages over **different** case sets (must pair by id and report unmatched ids), counts ties as improvements, and uses a one-sided p-value. Each test names one bug |
| 22 | How many questions do you need? | applied | trace | `⚠ HAND-TRACE` the chapter's `sample_size_paired(sd, smallest_effect)` for 3 settings (round up), and why halving the effect needs 4× the questions |

## E. Gates, CI and the project (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | A regression gate | challenge | code | `gate(base, new, rules)`: per-metric maximum allowed drop, minimum absolute levels, cost/latency ceilings, an `accepted` list of trade-offs that turns a named failure into a warning; returns `{"passed", "failures", "warnings"}` with readable reasons; refuses to compare runs whose dataset hashes differ |
| 24 | Run, slice, save and load | applied | code | `run_eval(system, cases)` → run dict with per-case records, dataset hash, config and label; `summarize(run, tag=None)` slices by tag; `save_run`/`load_run` JSON round-trip in `tmp_path`; uses the conftest `RagSystem` on 8 cases |
| 25 | An evaluation suite with a CI gate | challenge | code | `assessment = "build"`: `main(argv)` with `baseline` (writes a run) and `check` (runs, compares with the saved baseline, prints a report, exit 0/1). Tests: unchanged system passes; a config change that breaks retrieval (pool=1) fails with a reason naming recall; an accepted trade-off passes with a warning |

## Counts check

Tiers: drill 1, 2, 3, 6, 7, 8, 11, 15, 18 (9); applied 4, 5, 9, 10, 12, 13, 16, 22, 24 (9); deep 14, 19, 20, 21 (4); challenge 17, 23, 25 (3). Total 25.
Kinds: trace 3, 10, 20, 22 (4); explain 8, 11, 14 (3); code 18.
One assessment of each kind: explain p008, trace p003, fix p021, build p025.

## Risks and open questions

- The metrics' exact rules (article removal, punctuation, sentence split, support threshold) must be copied from the chapter into `problem.md`; hand-checked numbers depend on them.
- p017: the simulated judge is random; choose seeds and pair counts so the reference passes on 3 seeds with a wide margin (README R3).
- p019: bootstrap intervals are random; test properties or recompute with the same seeded `Random` in the test. Do not hard-code bootstrap bounds.
- p024/p025 run the conftest `RagSystem` (BM25 + LSA in NumPy): keep the corpus to ≤ 4 documents so the test stays under a few seconds.
