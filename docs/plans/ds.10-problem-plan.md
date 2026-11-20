# Problem plan: ds.10 Interpretation and communication (20 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.10.p001` … `p020`, folder `pNNN-slug`. Requires ds.06. Libraries: NumPy, pandas,
SciPy, scikit-learn. **SHAP and LIME are not installed** (as in the chapter): Shapley values are computed by exact enumeration,
by sampling and by the linear closed form, and checked against each other.

**Mix:** 7 drill, 6 applied, 5 deep, 2 challenge. **Kinds:** 12 code, 5 trace, 3 explain.
**assessment:** explain = p016, trace = p007, fix = p012, build = p020.
**★ core set (write first, 8):** 1, 4, 7, 8, 10, 12, 16, 20. Outcome (explain a prediction to a non-technical reader): p13–p17.

**Testing notes**
- Names follow the chapter's §11 toolkit: `shapley_exact(f, x, background)`, `shapley_sampling(f, x, background, m, seed)`,
  `reason_codes(phi, names, texts, forbidden, k)`, `counterfactual(predict_proba, x, names, actionable, cutoff, scale, ...)`,
  `natural_frequency(p, n, lo, hi)`, `wilson_interval(k, n)`, `auc_pairs(y, score)`, `partial_dependence_manual`, `ice`, `ale_1d`.
- **Shapley tests are axioms, not numbers** (the chapter's §11.3 tests): efficiency (contributions sum to `f(x) − mean f(background)`),
  dummy (an unused feature gets 0), symmetry (interchangeable features get equal credit), linear closed form
  (`φ_j = w_j (x_j − mean_j)`), and sampling → exact as m grows. Exact enumeration only for ≤ 6 features (2⁶ coalitions × background
  ≤ 50 rows), so each call is fast; brute force over all permutations for ≤ 4 features as the slow oracle.
- Data: `make_credit(n, seed)` (§2.1, a credit dataset with a **known rule**) in `conftest.py` with n ≤ 3,000; models are
  `LogisticRegression` and `HistGradientBoostingClassifier(max_iter=50)`.
- Communication problems are explain problems (self-rated against `answer.md`) or code that produces **wording** checked by rules
  (e.g. natural frequencies "about 12 out of 100", no unsupported causal verbs) — never free text judged by a test.

## A. Readable models and importance (Ch. 3–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Odds ratios per standard deviation | drill | code | `odds_ratio_table(model, X, names)` → per-feature odds ratio for a one-SD increase; a feature with zero coefficient → 1.0 |
| 2 | Monotonic constraints | applied | code | `constrained_model(X, y, increasing, decreasing)` with `HistGradientBoostingClassifier(monotonic_cst=...)`; `violations(model, feature, grid, X, direction)` is 0 for constrained features |
| 3 | Permutation importance on held-out data | drill | explain | impurity importance against permutation importance on held-out data: why impurity importance favours high-cardinality and noisy features (§4.1–4.2, numbers printed in `problem.md`) and which one to show a risk committee; checklist: "computed on training data", "many split points", "held-out", "model reliance, not truth"
| 4 | Correlated features split the credit | deep | code | `grouped_permutation_importance(model, X, y, groups, n_repeats, seed)`; two copies of one feature each look weak alone, their group is strong |
| 5 | Which importance answers which question? | drill | trace | `⚠ HAND-TRACE` given four questions ("what does the model use?", "what helps on new data?" …) and the chapter's table as code, print the method chosen for each |

## B. Effect plots (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Partial dependence and ICE | applied | code | `partial_dependence_manual(model, X, feature, grid)` and `ice(...)`; the PD curve is the mean of the ICE curves; equals `sklearn.inspection.partial_dependence(kind="average")` |
| 7 | Trace a partial-dependence point | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` a hand-made model `f(age, income) = 0.1·age − 0.02·income + 0.5` on 3 rows: print PD at age = 30, 40 (exact) |
| 8 | ALE when features are correlated | deep | code | `ale_1d(model, X, feature, n_bins)` (centred to mean 0); on correlated data with a model that depends only on the other feature, ALE is ≈ flat while PD is not |

## C. Shapley values (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Shapley values by hand | drill | trace | `⚠ HAND-TRACE` the §6.2 three-player toy game `f_toy` with values for all 8 coalitions (inline): print each player's Shapley value as a fraction |
| 10 | Exact Shapley by enumeration | applied | code | `shapley_exact(f, x, background)` over all coalitions with the interventional value function; passes efficiency, dummy and symmetry tests; equals the all-permutations brute force for 4 features |
| 11 | The linear closed form | drill | code | `linear_shap(w, x, background_mean)`; equals `shapley_exact` on a logistic model's **log-odds** output within 1e-10 |
| 12 | Fix the Shapley sampler | applied | code | `assessment = "fix"`; given `shapley_sampling` with two bugs (it uses the same permutation for every feature and forgets to average over background rows); tests: error vs exact falls like `1/sqrt(m)` and is < 0.02 at m = 2,000 |
| 13 | Global importance from local values | deep | code | `shap_importance(PHI, names)` = mean |φ| per feature, sorted; on the known rule the top feature is the one the rule weights most |
| 14 | What Shapley values cannot tell you | deep | explain | the §6.8 experiments: correlated features, background choice, model not reality, no causal claim; checklist |

## D. Local explanations and reason codes (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | Reason codes | applied | code | `reason_codes(phi, names, texts, forbidden, k)`: top k **risk-increasing** features only, forbidden (sensitive) features never listed, plain-language texts returned |
| 16 | Explain one decision to a borrower | deep | explain | `assessment = "explain"`; the outcome: from one applicant's Shapley table, reason codes and counterfactual (printed in `problem.md`), write the letter-style explanation for a non-technical reader and say what the explanation does **not** promise; checklist in `answer.md` (answer first, three reasons, one actionable change, no jargon, no causal overclaim) |
| 17 | Counterfactual: what would change the decision? | challenge | code | `counterfactual(predict_proba, x, names, actionable, cutoff, scale, steps, max_features)` finds the smallest change over actionable features that crosses the cutoff; touches only actionable features; returns `None` for an already-approved applicant (the chapter's tests) |

## E. Communication and fairness (Ch. 9–10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Natural frequencies | drill | trace | `⚠ HAND-TRACE` given `natural_frequency(p, n, lo, hi)`, print the sentence for p = 0.123 (n = 100) and with an interval 0.10–0.15 |
| 19 | Performance by group | applied | trace | `⚠ HAND-TRACE` given `group_table` and 12 inline rows from two groups, print each group's approval rate, TPR and FPR at the cut; the solution names the gap |

## F. Project (Ch. 11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | Explainable credit-risk report | challenge | code | `assessment = "build"`; `credit_report(model, X_train, X_test, y_test, applicant_ids)` returns a dict with AUC (`auc_pairs` = sklearn), global SHAP importance, group table, and per-applicant reason codes + counterfactual; tests are the §11.3 toolkit tests plus: report keys present, reason codes never contain the sensitive feature, every counterfactual crosses the cutoff |

## Counts check

Tiers: drill 7 (1, 3, 5, 7, 9, 11, 18), applied 6 (2, 6, 10, 12, 15, 19), deep 5 (4, 8, 13, 14, 16), challenge 2 (17, 20).
Kinds: trace 5 (5, 7, 9, 18, 19), explain 3 (3, 14, 16), code 12.
Assessment: explain p016, trace p007, fix p012, build p020 — exactly one each.

## Risks and open questions

- Interventional vs conditional Shapley: p010's `problem.md` must define the value function exactly (background rows replace the
  absent features), or the brute-force oracle and the learner will disagree.
- `HistGradientBoostingClassifier(monotonic_cst=...)` needs the constraint list in column order; give it explicitly.
- `make_credit(n=14000)` in the chapter: tests use n ≤ 3,000 so exact Shapley over a 50-row background stays fast.
