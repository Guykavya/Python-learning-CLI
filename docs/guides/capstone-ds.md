# DS capstone: raw data to a presented model, with a leakage audit

You have finished (or nearly finished) the Data Scientist track (ds.01 to ds.10). The
capstone proves you can combine it: take a real, messy, public tabular dataset, turn it into
a model with an **honest** score, find out where it fails, explain it to people who do not
know statistics, and defend every number against a sceptical reviewer. You choose the
problem. Nobody gives you a solution. The checklist at the bottom is how you (or a reviewer)
decide it is done.

Syllabus line: *Kaggle-style end-to-end project from raw data to presented model, with
leakage audit.*

The word that matters is **audit**. Anyone can fit a model that scores 0.97. The skill this
capstone tests is knowing, and showing, whether 0.97 is real (ds.04), and then saying in
plain words what the model does and does not do (ds.10).

## Rules

- **It is yours.** Your problem, your modelling, your words. Use the course chapters and the
  official docs, not generated analysis. A reviewer (a friend, or Claude in tutor mode)
  reads and comments; they do not rewrite it.
- **Own folder, own repo.** Keep it outside `my-work/`, with its own git history on your
  personal GitHub. Never a company account, company remote or company data. Never data with
  personal information about real, identifiable people unless it is a published open dataset
  whose licence allows your use.
- **Public data, downloaded once.** The dataset must be public and legally reusable.
  Download it once, record the URL, the date and the licence in `DATA.md`, and from then on
  work **offline from the local copy**. Keep the raw file untouched (read-only) in
  `data/raw/`; every cleaning step is code that produces `data/clean/`.
- **Not a competition.** The leaderboard rank does not matter. A model that scores 0.80
  honestly beats one that scores 0.90 through a leak, and you will be marked on the
  reasoning, not the metric.
- **Big enough to be honest.** At least **10,000 rows**, at least **15 columns**, a clear
  target, and a mix of numeric and categorical features with some missing values. Small
  enough for a laptop. Tiny textbook datasets (iris, a few hundred rows) are not allowed:
  they cannot show a leak or a failing segment.
- **Time-box.** Plan 4-5 weeks of part-time work. Write the problem note first (below).
- **No deep learning needed.** Gradient boosting and linear models are the expected tools.
  A neural network is allowed only as a stretch item, and only after the strong baselines.

## Pick a problem

A good problem is **a decision, a target that is known later, and a dataset in which some
column is tempting**. Suggestions (all public, with licences you must check yourself):

- **Bank marketing** (UCI): predict whether a client subscribes to a term deposit. It has a
  famous trap: the call-duration column is only known after the call.
- **Default of credit-card clients** (UCI, Taiwan): predict default next month from payment
  history. Good for time-based splits and cost-based thresholds.
- **Ames housing** (regression): predict sale price. Good for log targets, skew, many
  categorical features and error analysis by neighbourhood.
- **Online shoppers purchase intention** (UCI): predict purchases from sessions. Good for
  class imbalance and a user-level grouping question.
- **Adult income** (UCI): predict income class. Good for the fairness section, because the
  data contain sensitive attributes and proxies.

If you cannot decide in a day, take the default: **bank marketing**. It is small enough to
run in seconds and contains a planted leak you must find and explain.

## Step 0: the problem note (1-2 pages, before any modelling)

Write `PROBLEM.md` and keep it in the repo:

1. The decision this model supports, who makes it, and what happens today without a model.
2. The target, defined precisely: when it is measured, over what window, and for whom.
3. **The prediction moment**: the exact point in time at which the model will be used.
   Every feature must be known at that moment. Draw the timeline (ds.04 section 4).
4. How the model will be used in production: the unit scored, how often, what is done with
   the score (a threshold, a ranking, a probability shown to a human).
5. The metric you will optimise and **why**; the **baseline** you must beat (naive, business
   rule, simple model) and the cost of each kind of error (ds.04 section 10).
6. The split you will use and why it matches deployment (random, grouped, time-ordered).
7. The risks: three biggest unknowns (a leaky column? a changed definition? duplicates of the
   same customer?) and what you will try first.
8. What you are deliberately not doing.

Bring `PROBLEM.md` to the reviewer before you write much code.

## Requirements

Tick every **Must**. Aim for most **Should** items. **Stretch** is optional.

### A. Data, documentation and quality

- **Must:** `DATA.md`: source URL, download date, licence, file sizes, a SHA-256 checksum of
  every raw file, and a **data dictionary** (every column: meaning, type, unit, allowed
  values, and *when it becomes known*).
- **Must:** raw files are never edited; one script rebuilds everything downstream.
- **Must:** a **data-quality profile**: missing values per column and their pattern,
  duplicates (exact and near), impossible values, inconsistent categories, date range, and
  class balance, with counts.
- **Must:** the clean data written to Parquet or another typed format, with a cleaning log:
  every rule, how many rows it touched, why it is safe. Rows are flagged, not silently
  dropped.
- **Should:** the profile is a function you can re-run on a refreshed extract.
- **Stretch:** a second, external source joined in, with the key, grain and fan-out checked.

### B. The leakage audit (the core of this capstone)

- **Must:** `LEAKAGE_AUDIT.md` with, **for every feature**, an answer to "is this known at the
  prediction moment?" (the timeline question), who creates it, and a verdict: keep, drop, or
  rebuild as-of the prediction date.
- **Must:** run and record **all** of these detectives (ds.04 sections 4 to 6):
  1. the single-feature scan (one cross-validated score per column),
  2. the permutation or SHAP view of what the model relies on,
  3. the **shuffled-label test** on the full pipeline (it must fall to chance),
  4. a duplicate and near-duplicate check across the split,
  5. a group check: are the same customers/devices/entities on both sides of the split?
  6. the time check: for time-ordered data, a truncation test of every engineered feature.
- **Must:** a **planted-leak drill**: add a leaky column of your own design to a copy of the
  data (for instance a feature derived from the target), show your audit catches it, and show
  the score before and after. A detector you have never seen fire is not a detector.
- **Must:** every learned preprocessing step (scaling, imputing, encoding, selection,
  resampling) lives **inside the pipeline**, fitted on training folds only. A test proves the
  test rows never influence the fitted preprocessing.
- **Should:** an "audit waterfall" like ds.04 section 15: the score after each fix, from the
  too-good number to the honest one.
- **Stretch:** a regression test in your suite that fails if a column flagged "drop" ever
  appears in the feature list.

### C. Splits, baselines and evaluation

- **Must:** the split design in code and in words: sealed test set, validation by
  cross-validation of the correct kind (grouped, time-ordered or stratified), a gap if labels
  arrive late. The test set is opened **once**, and the README says when.
- **Must:** at least **three baselines**: a dummy, a business-rule or one-line heuristic, and
  a simple model (logistic or linear regression). The final model is compared with the best of
  them with a **paired interval** (a bootstrap over the test rows or folds), and the verdict
  is one of: beats, not distinguishable, loses to.
- **Must:** metrics suited to the problem (ds.03, ds.04): for a rare class, precision-recall
  and average precision, not accuracy; for regression, MAE and a scale-free error; each with
  an interval.
- **Must:** the model-selection record: every model and setting tried, with its
  cross-validated score and spread, so the best is not just the luckiest.
- **Should:** nested cross-validation or a final untouched period to estimate the optimism of
  the search (ds.05 section 9).
- **Stretch:** a learning curve showing whether more data or a better model would help.

### D. Modelling

- **Must:** a single scikit-learn `Pipeline` (ds.05) from raw columns to predictions, with a
  `ColumnTransformer`, handling missing values and unseen categories, usable on a raw row.
- **Must:** at least **three model families** compared fairly on identical folds: a linear
  model, a tree ensemble and gradient boosting (ds.06), tuned with a budgeted search.
- **Must:** one model implemented or re-derived by hand (for example logistic regression by
  Newton's method, or a small tree) and checked against scikit-learn, as in ds.06.
- **Should:** monotonic constraints or other domain knowledge in the final model, with a
  check that the constrained model respects them.
- **Stretch:** a neural network baseline (ml.01/ml.02) that is compared honestly with the
  boosted trees and, most likely, loses.

### E. Probabilities, thresholds and costs

- **Must:** a **calibration** check (reliability table, Brier score, log loss) and a
  recalibration if needed, fitted on data the model did not train on (ds.04 section 11).
- **Must:** the decision threshold chosen from a **stated cost matrix** on validation data,
  with its sensitivity to the costs, and the cost evaluated once on the test set.
- **Should:** a capacity-based alternative (top-k) if the real constraint is a number of
  actions.
- **Stretch:** a profit or loss curve over thresholds with an interval.

### F. Error analysis, interpretation and fairness

- **Must:** an **error analysis** (ds.04 section 12, ds.10 section 6): the confusion matrix
  or residuals, the list of the worst mistakes read by a human, and **slice tables** by at
  least three segments with row counts and intervals. Every hypothesis you test is reported,
  including those that failed.
- **Must:** an **interpretation section** (ds.10): global importance by two different
  methods, partial dependence or ICE for the top features, and the explanation of at least
  **five individual predictions**, each with the sanity checks of ds.10 section 8 (a
  faithfulness test, and agreement across methods).
- **Must:** a **group-fairness check**: performance and error rates by any sensitive or
  proxy attribute in the data, with the measures chosen and justified, and a note on what
  was done or not done about gaps.
- **Should:** reason codes and a counterfactual for a declined or flagged case, restricted to
  actionable features.
- **Stretch:** a stability analysis: how much do the top features and explanations change
  across seeds and resamples?

### G. Communication

- **Must:** `REPORT.md` of **5-8 pages**: an executive summary that starts with the answer
  and the recommended action, the problem, the data in one page, the leakage audit in one
  page, the methods, results with intervals, the errors and the limits, and the next steps.
- **Must:** a **one-page version for a non-technical reader** with no jargon (ds.10 section
  9): numbers as "out of 100", absolute alongside relative risks, uncertainty stated, one
  recommended action with an owner.
- **Must:** every number in the report is produced by code and **traceable** (a table
  `number -> script -> function`, or the numbers inserted automatically).
- **Must:** a **model card**: intended use, data, performance overall and by group, limits,
  monitoring plan, contact.
- **Must:** a 10-minute presentation script (five slides at most) in which the second slide
  is the leakage audit, not the architecture.
- **Should:** every figure's title states its finding; axes start at zero where they should;
  uncertainty is shown.
- **Stretch:** a recorded walkthrough, or an interactive offline demo (Streamlit).

### H. Reproducibility, serving and engineering

- **Must:** one command (`make all`, or `python run_all.py`) rebuilds clean data, the audit,
  the models, the tables, the figures and the report numbers from the raw files, and the
  README says how long it takes (machine-specific).
- **Must:** a pinned `requirements.txt`, a fixed seed for every random step, the Python and
  library versions recorded in an **experiment record** (config, data fingerprint,
  environment, commit, metrics) written for every training run (ds.04 section 13).
- **Must:** the final model saved as **one pipeline artefact**, with a small `predict`
  function or command-line tool that validates its input columns, handles an unseen category,
  and rejects bad requests with a clear message (ds.05 section 12, ds.04 section 14).
- **Must:** an **equivalence test**: batch scoring equals one-row-at-a-time scoring equals
  scoring from the reloaded file (ds.04 section 14.6).
- **Must:** a `pytest` suite covering: cleaning rules, the split (no row overlap, no group
  overlap, test later than train for time data), the leakage guards, the shuffled-label test,
  a determinism test (same seed, same metrics), and the serving checks.
- **Must:** git history with many small commits and clear messages, no secrets, no
  machine-specific paths, large data files ignored but described.
- **Should:** a monitoring sketch: which statistics (PSI of the inputs, calibration by risk
  band), thresholds, owner, and retraining trigger.
- **Should:** `ruff` clean and type hints on the public functions.
- **Stretch:** a Dockerfile or a `pyproject.toml` that installs the project and a CI workflow
  that runs the tests.

## How the review works

1. **Problem review** (before modelling): the reviewer reads `PROBLEM.md` and asks questions.
   Typical outcomes: "what is known on the day you score?", "who else could appear in both
   the training and test sets?", or "what does a false alarm cost?".
2. **Audit review** (after the first model): the reviewer reads `LEAKAGE_AUDIT.md`, picks two
   features, and asks you to defend their place in the model, then runs your planted-leak
   drill. If your first score is above what the reviewer expects, the audit is where you
   explain why.
3. **Midpoint check:** the data are clean and documented, the split and the baselines are
   fixed, the first honest score exists. The reviewer re-runs the pipeline and tries to break
   the split.
4. **Final review:** run through the checklist. For every unticked **Must** the reviewer gives
   a pointer, not a patch ("what happens to this score if you shuffle the labels?").
5. **Fresh-machine test:** clone the repo into a new folder, follow only the README, and
   rebuild everything from the raw files. If you get stuck, the README is the bug.
6. **Challenge drill:** the reviewer picks three numbers from the report and asks "show me".
   You trace each to a script and a row count within a few minutes.
7. **Explain-it drill:** the reviewer plays a non-technical customer who was declined and
   asks "why?", then plays a sceptical executive and asks "how do you know it works?". You
   answer in the plain words of your one-page report, not in statistics.

### Scoring (for yourself)

| Score | Meaning |
|---|---|
| All Musts, most Shoulds | DS capstone passed |
| All Musts only | Passed, but go back and add the missing polish and tests |
| Any Must missing | Not done yet. Finish those first |
| Any Must in section B missing | Not done, whatever else is complete: the audit is the point |

Stretch items are for pride and for your portfolio, not for the pass mark.

## Why this capstone

A model is easy; trust is hard. In practice the number one reason a data-science project
fails is not a weak algorithm. It is an evaluation that quietly flattered the model: a
column from the future, a customer on both sides of the split, a preprocessing step fitted on
everything. The audit, the planted-leak drill and the shuffled-label test are habits to keep
for life, because they are what makes a score believable. And the one-page version for a
non-technical reader is the other half of the job: a model that nobody can explain to the
person it affects does not get used, and should not be.
