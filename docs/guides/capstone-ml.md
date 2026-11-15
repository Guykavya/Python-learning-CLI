# ML capstone: a model of your own learning, tracked, optimised, served and monitored

You have finished (or nearly finished) the ML Engineer track, route 1 (ml.01 to ml.07). The
capstone proves you can combine it: take **your own study history** (the `attempts` and
`problem_state` tables of `data/progress.db`), train a model that predicts something useful
about it, measure it honestly, shrink it, serve it as an API, and watch it for drift. You
choose the question. Nobody gives you a solution. The checklist at the bottom is how you (or a
reviewer) decide it is done.

Syllabus line: *Train a model on your own learning history from this module and serve it as
an API.*

The sentence that matters is **an honest number, then a running service**. Anyone can fit a
network that scores well on a few hundred rows of their own data. The skill this capstone
tests is knowing whether the score is real (ds.04), whether a deep model earned its place
over a simple one (ml.01, ml.02), and whether the thing you serve is the thing you tested
(ml.06, ml.07).

## Rules

- **It is yours.** Your question, your modelling, your words. Use the course chapters and the
  official docs, not generated analysis. A reviewer (a friend, or Claude in tutor mode) reads
  and comments; they do not rewrite it.
- **Own folder, own repo.** Keep it outside `my-work/`, with its own git history on your
  personal GitHub. Never a company account or remote.
- **Your data is personal.** `progress.db` is private. **Never commit it**, a copy of it, or a
  CSV of it. The repo holds only (a) the extraction script, (b) a **synthetic generator** with
  the same columns that anybody can run, and (c) models trained on the synthetic data for the
  public demo. Your real model stays local. A test proves no real row is in git.
- **Read-only.** Open `progress.db` read-only (`file:...?mode=ro`) and copy what you need into
  `data/raw/` once. Never write to it from the capstone.
- **Work offline.** After the extraction, everything runs from local files. The course must
  keep working with no AI and no internet.
- **Time-box.** Plan 4-5 weeks of part-time work. Write the problem note first (below).
- **Small data is the point.** You may have only a few hundred attempts. That is realistic.
  The capstone is **not** about a high score; it is about reporting *how little you can
  conclude* from small data, and building the whole machinery correctly anyway.
- **Not a leaderboard.** An honest 0.62 that you can defend beats a 0.90 caused by a leak.

## Pick a question

A good question is **a decision for future you, a target you can compute from history, and
a column that is tempting but cheats**. Choose one:

1. **Will I pass this problem on the next attempt?** Target: `attempts.passed` of the next
   attempt. Decision: which problems to review or warm up before trying.
2. **Will I solve this problem within 3 attempts and 30 minutes?** A harder, more useful
   target built from several columns.
3. **When should I review this problem?** Predict whether a review at interval `d` will be
   remembered; compare with the engine's own spaced-repetition schedule. Decision: a better
   schedule.
4. **Which module will I struggle with next week?** Aggregate per module and week; a
   regression or ranking task on tiny data (a good lesson in how little you can predict).

If you cannot decide in a day, take the default: **question 1**. It has enough rows, a clear
target and an obvious planted trap: `hints_used`, `seconds` and `quality` of an attempt are
only known **after** it; using them to predict that same attempt is a leak.

If your history has fewer than about **300 attempts**, use the synthetic generator for the
development and say so in the report; use your real data only for the final check.

## Step 0: the problem note (1-2 pages, before any modelling)

Write `PROBLEM.md` and keep it in the repo:

1. The decision this model supports, who makes it (you), and what you do today without a model.
2. The target, defined precisely: which row, which column, measured when.
3. **The prediction moment**: the exact time at which the model is asked. Every feature must
   exist at that moment. Draw the timeline for one attempt (ds.04 section 4).
4. How the model will be used: the unit scored, how often, what you do with the score.
5. The metric, **why**, and the baselines you must beat (the "last result" rule, the problem's
   past pass rate, a logistic regression) with the cost of each kind of error.
6. The split, and why it matches deployment (**time-ordered**: the future is never in training).
7. The three biggest risks (leak, tiny data, a change in how you study over time) and what you
   try first.
8. What you are deliberately not doing.

Bring `PROBLEM.md` to the reviewer before you write much code.

## Requirements

Tick every **Must**. Aim for most **Should** items. **Stretch** is optional.

### A. Data, documentation and privacy

- **Must:** `DATA.md`: how the extraction works, the date, row counts, a SHA-256 of the raw
  extract, and a **data dictionary** (every column: meaning, unit, and *when it becomes known*).
- **Must:** an extraction script that reads `progress.db` read-only and writes `data/raw/`
  (gitignored). The raw extract is never edited; one script rebuilds everything downstream.
- **Must:** a **synthetic generator** with the same schema and a *known* data-generating
  process (for example pass probability rising with practice and falling with difficulty and
  gaps). With it you can check that your pipeline recovers a known truth.
- **Must:** a data-quality profile: missing values, duplicates, impossible values (negative
  seconds), the date range, class balance, and rows per problem and per day.
- **Must:** a privacy test: nothing from `progress.db` is tracked by git.
- **Should:** features are a function you can re-run on a refreshed extract.

### B. The leakage audit

- **Must:** `LEAKAGE_AUDIT.md` with, **for every feature**, an answer to "is it known at the
  prediction moment?", and a verdict: keep, drop, or rebuild as-of the prediction time.
- **Must:** run and record: the single-feature scan, the permutation view of what the model
  relies on, the **shuffled-label test** on the full pipeline (it must fall to chance), and a
  time check (every aggregate such as "pass rate so far" uses only rows **before** the
  attempt).
- **Must:** a **planted-leak drill**: add a column derived from the target (or from the
  after-the-fact `quality`), show your audit catches it, and show the score before and after.
- **Must:** the split is **time-ordered** with a sealed final period; a test proves every test
  row is later than every training row. The test set is opened **once**.
- **Should:** an "audit waterfall": the score after each fix, from the too-good number to the
  honest one.

### C. Baselines, evaluation and honest statistics

- **Must:** at least **three baselines**: a dummy, a one-line rule (for example "same as the
  last attempt"), and a regularised logistic regression.
- **Must:** metrics fitted to the problem (log loss, Brier score, ROC AUC and average
  precision for a skewed target), each with an **interval** (bootstrap over test rows, or
  over *problems* if attempts of one problem are correlated).
- **Must:** the final model is compared with the best baseline with a **paired** interval and
  the verdict is one of: beats, not distinguishable, loses to. With small data, "not
  distinguishable" is a legitimate and common answer.
- **Must:** a record of every model and setting tried, with its cross-validated score and
  spread, so the best is not just the luckiest.
- **Should:** a **learning curve** (score against number of training rows) that tells you
  whether more data or a better model would help.

### D. Models, including a neural network

- **Must:** a gradient-boosted or random-forest model, tuned with a budgeted search, on the
  tabular features (ds.06).
- **Must:** a **PyTorch** model trained with your own loop (ml.01, ml.02): either an MLP on the
  same features, or a small sequence model (GRU or 1-D conv) over the **last k attempts** of a
  problem (ml.04). Seeded, with early stopping on a validation period, loss curves saved, and
  a gradient/overfitting check (it must be able to overfit 20 rows before you trust it).
- **Must:** an honest **comparison** of all families on identical splits. If the network does
  not beat boosting or even the logistic baseline, **say so**; that is the expected result on
  hundreds of rows and not a failure.
- **Must:** a **calibration** check (reliability table, Brier score) and recalibration if
  needed, fitted on data the model did not train on.
- **Should:** one model implemented by hand and checked against a library (for example logistic
  regression by gradient descent against scikit-learn).
- **Stretch:** a **pretrained text embedding** of the problem statements as a feature (ml.05),
  compared with and without; or a LoRA/fine-tuning study if you have GPU time. It must earn its
  place with an interval, not by being fashionable.

### E. Tracking and reproducibility (ml.06)

- **Must:** every training run is **tracked** (MLflow, or your own JSON record): config, seed,
  data hash, git commit, library versions, metrics, and the model artefact.
- **Must:** **reproduce** a past run from its record, bit-for-bit or within a stated tolerance,
  and a test that fails if the data hash changed.
- **Must:** the whole thing rebuilds from the raw extract with one command (`make all` or
  `python run_all.py`); the README says how long it takes (machine-specific).
- **Must:** a pinned `requirements.txt` and a fixed seed for every random step.
- **Should:** the pipeline as stages (DVC or a Makefile) so only stale stages rerun.
- **Should:** a **promotion gate**: a challenger replaces the champion only if it beats it with
  an interval on the sealed period, and the rule is in code.

### F. Optimisation (ml.07)

- **Must:** an **optimisation report** for the final model: size, latency and accuracy before
  and after, with every latency measured in a **fresh process** (warm-up, median and p95, noise
  floor stated). Report ratios, not absolute milliseconds.
- **Must:** an **ONNX export** of the final model with a **parity test** (max difference, same
  predicted class), tested with a batch size different from the export size.
- **Must:** at least two further variants (int8 quantisation, a smaller architecture, or
  pruning with fine-tuning) in a **Pareto table**, with a stated requirement and the decision
  written as one sentence ("ship X: 3.9x smaller, 2x faster, accuracy -0.001").
- **Should:** the preprocessing is **inside** the exported graph or covered by a golden-example
  test.
- **Stretch:** a micro-batching wrapper with a measured effect at high load.

### G. Serving and monitoring

- **Must:** a **FastAPI** service (swe.05, ml.06) that loads the chosen artefact once, validates
  the input (Pydantic), returns the probability **and the model version**, and has `/health`,
  `/metadata` and a metrics endpoint. Bad requests give a clear 422, not a crash.
- **Must:** an **equivalence test**: batch scoring equals one-row scoring equals scoring through
  the HTTP API (use `TestClient`; no real network needed).
- **Must:** every prediction is **logged** (inputs, output, version, time) in SQLite so it can
  later be joined to the real outcome.
- **Must:** a **drift monitor**: PSI or KS on the input features between a reference window
  and a recent window, with a minimum window size and a threshold **calibrated on no-drift
  windows**; and a **drift drill**: inject a shift into the synthetic data, show the alert
  fires, and show a stable window does not alert.
- **Must:** a one-page **runbook**: what each alert means, what you check first, and how to
  roll back to the previous model.
- **Should:** a Dockerfile that builds offline from pre-downloaded wheels (see ml.06 section
  5.3) and a note on how to run it.
- **Stretch:** a **concept drift** check using realised outcomes: the model's calibration by
  risk band over time, on logged predictions joined to what actually happened.

### H. Communication and engineering

- **Must:** `REPORT.md` of **5-8 pages**: summary that starts with the answer, the question,
  the data (and its limits), the leakage audit, methods, results with intervals, the
  optimisation table, the serving design, the monitoring, and what you would do next.
- **Must:** a **model card**: intended use, data, performance overall and by slice (early and
  late period, easy and hard modules), limits, monitoring, contact.
- **Must:** every number in the report is produced by code and traceable (a table
  `number -> script -> function`).
- **Must:** a `pytest` suite covering: extraction and cleaning, the time-ordered split, the
  leakage guards, the shuffled-label test, determinism, the ONNX parity, the API contract and
  the drift monitor. Every assert has a message naming the likely mistake.
- **Must:** git history with many small commits and clear messages, no secrets, no personal
  data, no machine-specific paths.
- **Should:** `ruff` clean and type hints on the public functions; a CI workflow that runs the
  tests on the synthetic data only.
- **Stretch:** an offline demo page or CLI that reads your real model and prints, for each
  due review, "probability you pass" next to the engine's schedule.

## How the review works

1. **Problem review** (before modelling): the reviewer reads `PROBLEM.md` and asks questions.
   Typical outcomes: "what is known when you open the problem?", "what happens when you change
   how you study?", "how many rows do you really have?".
2. **Audit review** (after the first model): the reviewer picks two features, asks you to
   defend their place, then runs your planted-leak drill.
3. **Midpoint check:** clean data, a time-ordered split, three baselines and the first honest
   score exist, and every run is tracked. The reviewer re-runs the pipeline and tries to break
   the split.
4. **Optimisation and serving review:** the reviewer asks for a latency number, then asks how
   you know it is not noise. They send a malformed request, a batch of size 7, and a shifted
   input window, and watch the service and the monitor.
5. **Fresh-machine test:** clone the repo into a new folder, follow only the README with the
   **synthetic** data, and rebuild everything. If you get stuck, the README is the bug.
6. **Challenge drill:** the reviewer picks three numbers from the report and asks "show me".
   You trace each to a script and a row count within a few minutes.

### Scoring (for yourself)

| Score | Meaning |
|---|---|
| All Musts, most Shoulds | ML capstone passed |
| All Musts only | Passed, but go back and add the missing polish and tests |
| Any Must missing | Not done yet. Finish those first |
| Any Must in section B (leakage) or F (parity) missing | Not done, whatever else is complete |

Stretch items are for pride and for your portfolio, not for the pass mark.

## Suggested order (5 weeks)

| Week | Goal |
|---|---|
| 1 | Problem note, extraction, synthetic generator, quality profile, time-ordered split, baselines |
| 2 | Features, leakage audit with the planted-leak drill, boosting model, tracking and reproducing a run |
| 3 | PyTorch model, honest comparison with intervals, calibration, learning curve |
| 4 | ONNX export with parity, quantisation and one more variant, Pareto table, decision |
| 5 | FastAPI service with logging, drift monitor and drill, runbook, tests, report and model card |

## Why this capstone

The pieces of the track are easy to learn separately and easy to get wrong together. A network
that "works" on 400 rows is usually fitting noise; an ONNX file that was never compared with the
original may be wrong; a service without a monitor fails silently. By using your own history you
get a problem that is small, personal and honest: you will feel how little data supports, and you
will practise the habit that matters for life: **a number you cannot defend is not a result**.
And a model of how you learn is, at the end, something you can actually use.
