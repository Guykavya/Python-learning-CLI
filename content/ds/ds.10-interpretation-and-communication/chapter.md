# Chapter 10 (DS): Interpretation and communication

A model that nobody understands is a model that nobody can safely use. The credit analyst asks "why was this application declined?". The regulator asks "can you show the model is not using something it should not?". The product manager asks "what should I tell customers?". The data scientist herself asks "is this model right for the right reasons, or has it found a shortcut?" (ds.04 and ds.08 gave you shortcuts that scored 0.98 and failed in deployment). None of them is helped by an AUC. They need **explanations**, and they need the explanations **told in words they can use**.

This chapter has two halves that belong together. The first is **interpretation**: the tools for looking inside a model (coefficients, importance, partial dependence, **Shapley values**, local surrogates, counterfactuals), including their **limits**, because every explanation method answers a narrower question than people think and several famous misreadings follow from forgetting that. The second is **communication**: turning a model, its numbers and its uncertainty into a message for someone who does not know what a log-odds is, and who will make a decision with it.

By the end you reach the syllabus outcome: **explain a model's prediction to a non-technical reader.** The project builds a small, tested explanation toolkit and uses it to write the one-page report on a credit-risk model that a lender could act on.

Prerequisites: ds.06 (models, boosting), ds.05 (pipelines, permutation importance), ds.04 (leakage, thresholds, calibration, error analysis), ds.03 (metrics). Everything here is implemented from scratch where it fits and checked against a known answer.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, pandas, SciPy and scikit-learn. **SHAP and LIME are not installed**, so we implement Shapley values ourselves (exact enumeration, a sampling approximation and a closed form for linear models, checked against each other) and a LIME-style local surrogate; the library calls are shown as *Try it on your machine* with no invented output. The data are **synthetic, generated from a known rule**, so we can check whether an explanation is faithful to what the model should have learned. Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, json, itertools, warnings, platform
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy import stats
from sklearn import (ensemble, inspection, linear_model, metrics, model_selection, pipeline, preprocessing, tree)

np.set_printoptions(precision=4, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 100)
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
warnings.filterwarnings("ignore")
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__)
print("pandas ", pd.__version__)
print("sklearn", sklearn.__version__)
```
```text
python  3.14.4
numpy   2.5.4
pandas  3.1.1
sklearn 1.9.1
```

## Table of contents

1. [Why explain, and to whom](#1-why-explain-and-to-whom)
2. [The running example: credit risk with a known rule](#2-the-running-example-credit-risk-with-a-known-rule)
3. [Models you can read](#3-models-you-can-read)
4. [Global importance: which features matter](#4-global-importance-which-features-matter)
5. [Effect plots: partial dependence, ICE and ALE](#5-effect-plots-partial-dependence-ice-and-ale)
6. [Shapley values and SHAP](#6-shapley-values-and-shap)
7. [Local explanations: LIME-style surrogates, reason codes and counterfactuals](#7-local-explanations-lime-style-surrogates-reason-codes-and-counterfactuals)
8. [Global surrogates and what explanations cannot tell you](#8-global-surrogates-and-what-explanations-cannot-tell-you)
9. [Communicating results to non-technical people](#9-communicating-results-to-non-technical-people)
10. [Fairness and responsible use, briefly](#10-fairness-and-responsible-use-briefly)
11. [Project: an explainable credit-risk model report](#11-project-an-explainable-credit-risk-model-report)
12. [Common traps](#12-common-traps)
13. [Summary](#13-summary)

## 1. Why explain, and to whom

### 1.1 Six reasons

| Reason | The question | Who asks |
|---|---|---|
| **Debugging** | Is the model right for the right reasons? Has it found a leak or a shortcut? | the data scientist |
| **Trust and adoption** | Does this match what experts know? | the domain expert, the user |
| **Recourse** | What could this person change to get a different outcome? | the affected person |
| **Compliance** | Can you justify an automated decision? Which factors drove it? | regulators, auditors, lawyers |
| **Fairness** | Does it lean on a proxy for something it must not use? | ethics and risk teams |
| **Science and insight** | What did the model learn about the world? | researchers (with care: section 8) |

The same model needs different explanations for different audiences. A regulator wants the whole decision logic; an applicant wants three reasons and a path to approval; the CEO wants one sentence about risk.

### 1.2 Kinds of explanation

| Axis | Choices |
|---|---|
| **Scope** | **global** (how does the model behave overall?) versus **local** (why this prediction?) |
| **Access** | **model-agnostic** (works from inputs and outputs alone) versus **model-specific** (uses the internals: coefficients, tree structure) |
| **Nature** | **inherently interpretable** models (a short tree, a linear model with sensible features) versus **post-hoc** explanations of a black box |

### 1.3 The honest trade-off

Interpretable models are easy to explain and sometimes nearly as accurate (on tabular data, often within a point or two of AUC). Complex models can be more accurate and then need post-hoc tools. The tools are **approximations of the model's behaviour, not windows into its mind**, and they can mislead. So the order of work is:

1. Try an interpretable model first, as the baseline you must beat (the course's rule about baselines, once more).
2. If a complex model earns its accuracy, **constrain** it where domain knowledge allows (monotonic constraints, section 3.3).
3. Explain it with several methods, and treat disagreement as information.
4. State what the explanation does **not** show.

## 2. The running example: credit risk with a known rule

### 2.1 The data

A lender predicts whether a borrower will **default within a year**. The generator below uses a rule we know, including a non-linearity (utilisation matters more as it rises), an **interaction** (high utilisation *and* a high debt ratio together are much worse than either alone), a pair of correlated features (loan amount follows income), a duplicate feature, and a meaningless high-cardinality code that should receive no credit from any honest method.

```python run
def make_credit(n=14000, seed=0):
    r = np.random.default_rng(seed)
    age = np.clip(r.normal(42, 12, n), 21, 75)
    income = np.exp(r.normal(10.9, 0.45, n)) * (1 + 0.004 * (age - 42))               # annual income
    region = r.choice([0, 1, 2, 3], n, p=[.35, .30, .20, .15])                       # four regions; income differs by region (a proxy-risk, section 10)
    income = income * np.array([1.12, 1.0, 0.88, 0.78])[region]
    employment_years = np.clip(r.gamma(2.2, 3.0, n) * (age / 42), 0, 45)
    debt_ratio = np.clip(r.beta(2.2, 4.5, n), 0.01, 0.95)
    utilisation = np.clip(r.beta(2.0, 3.2, n), 0.0, 1.0)
    delinquencies = r.poisson(0.15 + 1.4 * utilisation ** 2)
    history = np.clip(r.gamma(3.0, 3.0, n) + 0.12 * (age - 21), 0.5, 40)
    inquiries = r.poisson(1.0 + 1.3 * utilisation)
    loan_amount = income * r.uniform(0.15, 1.1, n)                                   # correlated with income
    logit = (-3.9 + 4.2 * utilisation ** 2 + 1.1 * np.log1p(delinquencies) + 2.2 * debt_ratio
             - 0.9 * np.log(income / 55_000) - 0.045 * history - 0.02 * employment_years
             + 0.45 * (inquiries > 3) + 1.8 * ((utilisation > 0.7) & (debt_ratio > 0.4)) + 0.6 * (loan_amount / income))
    default = (r.random(n) < 1 / (1 + np.exp(-logit))).astype(int)
    df = pd.DataFrame(dict(age=age, income=income, employment_years=employment_years, debt_ratio=debt_ratio, utilisation=utilisation,
                           delinquencies=delinquencies, credit_history_years=history, inquiries=inquiries, loan_amount=loan_amount, region=region))
    df["income_k"] = (df["income"] / 1000 + r.normal(0, 0.3, n)).round(1)            # a noisy near-copy of income, in thousands
    df["branch_code"] = r.integers(0, 200, n)                                        # an ID-like code with NO relationship to default
    return df, default

credit, y = make_credit()
print(credit.shape, "| default rate:", round(float(y.mean()), 3))
print(credit.head(4).round(2).to_string(index=False))
print("correlation of income with loan_amount: %.2f | with income_k: %.3f" % (credit.income.corr(credit.loan_amount), credit.income.corr(credit.income_k)))
```
```text
(14000, 12) | default rate: 0.139
    age      income  employment_years  debt_ratio  utilisation  delinquencies  credit_history_years  inquiries  loan_amount  region  income_k  branch_code
43.5100 53,800.3500           15.9900      0.2300       0.7100              1               10.2900          3  28,432.9100       1   54.1000          172
40.4100 38,282.3300            2.4400      0.3600       0.6000              0                9.3000          1  20,681.5300       2   37.9000           48
49.6900 99,455.2000            3.8300      0.2200       0.5500              1               22.1500          1  27,243.7400       0   99.9000          179
43.2600 30,877.8100            1.2900      0.2600       0.6200              1                5.5100          1   6,554.3800       2   31.5000          146
correlation of income with loan_amount: 0.70 | with income_k: 1.000
```

### 2.2 Split, and two models to explain

```python run
CORE = ["age", "income", "employment_years", "debt_ratio", "utilisation", "delinquencies", "credit_history_years", "inquiries", "loan_amount", "region"]
X_dev, X_test, y_dev, y_test = model_selection.train_test_split(credit, y, test_size=0.25, random_state=0, stratify=y)
X_tr, X_val, y_tr, y_val = model_selection.train_test_split(X_dev, y_dev, test_size=0.25, random_state=1, stratify=y_dev)

logit_model = pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression(max_iter=3000)).fit(X_dev[CORE], y_dev)
gbm = ensemble.HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_depth=4, min_samples_leaf=40, random_state=0).fit(X_dev[CORE], y_dev)
base_rate = y_dev.mean()
rows = []
for name, m in [("base rate (predict the average)", None), ("logistic regression", logit_model), ("gradient boosting", gbm)]:
    p = np.full(len(y_test), base_rate) if m is None else m.predict_proba(X_test[CORE])[:, 1]
    rows.append((name, metrics.roc_auc_score(y_test, p), metrics.average_precision_score(y_test, p), metrics.brier_score_loss(y_test, p)))
print(pd.DataFrame(rows, columns=["model", "test AUC", "average precision", "Brier"]).set_index("model").round(4).to_string())
```
```text
                                 test AUC  average precision  Brier
model                                                              
base rate (predict the average)    0.5000             0.1386 0.1194
logistic regression                0.7900             0.4898 0.0943
gradient boosting                  0.7914             0.4990 0.0933
```

Notice what the table does *not* show: the boosted model is **no better** than the plain logistic regression. The interaction (high utilisation *and* high debt together) affects only about 5% of the borrowers, and a straight line already captures the broad pattern, so the extra flexibility buys almost nothing in AUC. That is a common and valuable finding (ds.06 told you to try the simple model first), and it makes the point of section 1.3 concrete: here an interpretable model would be a perfectly good choice. We explain the boosted model anyway, because it learned the interaction and the non-linearity that the straight line cannot express, and because most real systems need the tools of this chapter.

### 2.3 Try it

1. Compute the AUC of each model on the rows with `utilisation > 0.7 and debt_ratio > 0.4`. Where does the gap between the models come from?
2. Fit a logistic regression that also contains `utilisation**2` and the interaction term. How close does it get to the boosted model?

## 3. Models you can read

### 3.1 Logistic regression: coefficients, odds and standardised effects

A logistic regression says `log-odds = b + Σ w_j x_j`. Each coefficient is the change in the **log-odds** of default for one unit of the feature, which is a multiplicative change in the odds by `exp(w_j)`. Standardise the features first to compare them: then `w_j` is the effect of a one-standard-deviation change.

```python run
lr = logit_model[-1]
coef = pd.DataFrame({"standardised coefficient": lr.coef_[0], "odds ratio per 1 std": np.exp(lr.coef_[0]), "std of the feature": X_dev[CORE].std().to_numpy()}, index=CORE)
print(coef.reindex(coef["standardised coefficient"].abs().sort_values(ascending=False).index).round(3).to_string())
print("\nreading one row: a one-std higher utilisation multiplies the odds of default by %.2f, holding the other features fixed" % np.exp(lr.coef_[0][CORE.index("utilisation")]))
```
```text
                      standardised coefficient  odds ratio per 1 std  std of the feature
utilisation                             0.8990                2.4570              0.1950
income                                 -0.6160                0.5400         29,475.9550
debt_ratio                              0.4260                1.5310              0.1690
delinquencies                           0.3640                1.4390              0.6840
loan_amount                             0.2360                1.2660         26,063.6670
credit_history_years                   -0.2320                0.7930              5.3700
region                                  0.0840                1.0880              1.0630
inquiries                               0.0820                1.0860              1.2450
employment_years                       -0.0620                0.9400              4.9910
age                                    -0.0140                0.9870             11.4870

reading one row: a one-std higher utilisation multiplies the odds of default by 2.46, holding the other features fixed
```

Three cautions that apply to every coefficient table. A coefficient is "holding the other features fixed", which is a strange thing to ask when features move together (income and loan amount). It describes **association in the model**, not a causal effect (ds.09). And coefficients of correlated features are unstable: the model can split credit between them arbitrarily.

### 3.2 A short decision tree: rules a person can follow

```python run
from sklearn.tree import DecisionTreeClassifier, export_text
shallow = DecisionTreeClassifier(max_depth=3, min_samples_leaf=150, random_state=0).fit(X_dev[CORE], y_dev)
print(export_text(shallow, feature_names=CORE, decimals=2, show_weights=True))
print('(weights = [number who repay, number who default] in each leaf)')
print("shallow tree test AUC: %.4f (logistic %.4f, boosting %.4f)" % (metrics.roc_auc_score(y_test, shallow.predict_proba(X_test[CORE])[:, 1]),
      metrics.roc_auc_score(y_test, logit_model.predict_proba(X_test[CORE])[:, 1]), metrics.roc_auc_score(y_test, gbm.predict_proba(X_test[CORE])[:, 1])))
```
```text
|--- utilisation <= 0.69
|   |--- utilisation <= 0.52
|   |   |--- delinquencies <= 0.50
|   |   |   |--- weights: [5560.00, 356.00] class: 0
|   |   |--- delinquencies >  0.50
|   |   |   |--- weights: [1709.00, 266.00] class: 0
|   |--- utilisation >  0.52
|   |   |--- delinquencies <= 0.50
|   |   |   |--- weights: [804.00, 138.00] class: 0
|   |   |--- delinquencies >  0.50
|   |   |   |--- weights: [635.00, 278.00] class: 0
|--- utilisation >  0.69
|   |--- debt_ratio <= 0.41
|   |   |--- income <= 49332.38
|   |   |   |--- weights: [103.00, 113.00] class: 1
|   |   |--- income >  49332.38
|   |   |   |--- weights: [194.00, 105.00] class: 0
|   |--- debt_ratio >  0.41
|   |   |--- weights: [38.00, 201.00] class: 1

(weights = [number who repay, number who default] in each leaf)
shallow tree test AUC: 0.7407 (logistic 0.7900, boosting 0.7914)
```

A depth-3 tree is something a person can read aloud and apply by hand, and it pays for that in accuracy. Whether the price is acceptable depends on the use.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a decision tree diagram of depth 3 for credit default. Root: utilisation <= 0.69. Left child splits on utilisation <= 0.52, then each side splits on delinquencies <= 0.50. Right child splits on debt_ratio <= 0.41; the low-debt side splits on income <= 49332, the high-debt side is a leaf. Show [repay, default] counts in each leaf, e.g. [5560, 356] and [38, 201], and colour leaves by class."

### 3.3 Constraints: put domain knowledge into the black box

Domain experts know directions: more delinquencies should never make a borrower *safer*; higher income should never raise risk. A free-form boosted model can violate that on noisy regions of the data, which both hurts trust and often hurts accuracy. `HistGradientBoosting` accepts **monotonic constraints**: `+1` (non-decreasing), `-1` (non-increasing), `0` (free) for each feature.

```python run
mono = {"utilisation": 1, "delinquencies": 1, "debt_ratio": 1, "inquiries": 1, "income": -1, "credit_history_years": -1, "employment_years": -1}
cst = [mono.get(c, 0) for c in CORE]
gbm_mono = ensemble.HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_depth=4, min_samples_leaf=40, monotonic_cst=cst, random_state=0).fit(X_dev[CORE], y_dev)
print("constraints:", dict(zip(CORE, cst)))
print("test AUC  free: %.4f | monotonic: %.4f" % (metrics.roc_auc_score(y_test, gbm.predict_proba(X_test[CORE])[:, 1]), metrics.roc_auc_score(y_test, gbm_mono.predict_proba(X_test[CORE])[:, 1])))

def violations(model, feature, grid, X, direction=+1, n=300, seed=0):
    """Share of sampled borrowers for whom the prediction moves the WRONG way when only `feature` increases along `grid`.
    direction=+1: risk should not fall as the feature rises; direction=-1: risk should not rise."""
    r = np.random.default_rng(seed); idx = r.choice(len(X), n, replace=False)
    bad = 0
    for i in idx:
        rows = np.repeat(X.iloc[[i]].to_numpy(), len(grid), axis=0); rows[:, CORE.index(feature)] = grid
        p = model.predict_proba(pd.DataFrame(rows, columns=CORE))[:, 1]
        bad += np.any(direction * np.diff(p) < -1e-9)
    return bad / n
g = np.linspace(X_dev["delinquencies"].min(), X_dev["delinquencies"].max(), 12)
gi = np.linspace(X_dev["income"].quantile(.02), X_dev["income"].quantile(.98), 12)
print(f"borrowers for whom MORE delinquencies lowers the predicted risk: free {violations(gbm, 'delinquencies', g, X_test[CORE]):.1%}, monotonic {violations(gbm_mono, 'delinquencies', g, X_test[CORE]):.1%}")
print(f"borrowers for whom HIGHER income raises the predicted risk     : free {violations(gbm, 'income', gi, X_test[CORE], direction=-1):.1%}, monotonic {violations(gbm_mono, 'income', gi, X_test[CORE], direction=-1):.1%}")
```
```text
constraints: {'age': 0, 'income': -1, 'employment_years': -1, 'debt_ratio': 1, 'utilisation': 1, 'delinquencies': 1, 'credit_history_years': -1, 'inquiries': 1, 'loan_amount': 0, 'region': 0}
test AUC  free: 0.7914 | monotonic: 0.7927
borrowers for whom MORE delinquencies lowers the predicted risk: free 14.0%, monotonic 0.0%
borrowers for whom HIGHER income raises the predicted risk     : free 37.7%, monotonic 0.0%
```

Constraints cost little or nothing in accuracy when the knowledge is right, and they remove the embarrassing local contradictions that make a model hard to defend.

### 3.4 Try it

1. Add the constraint `loan_amount: +1` and compare the AUC. Is the constraint justified by the data-generating rule?
2. Fit a depth-5 tree and measure how its test AUC and its readability change.

## 4. Global importance: which features matter

### 4.1 Impurity importance (built into tree ensembles): fast and biased

A random forest's `feature_importances_` sums how much each feature reduced impurity across all splits. It is free after training, and it has a well-known flaw: it is computed on the **training** data and favours features with many distinct values, which offer more chances to split on noise. The `branch_code` column is pure noise.

> **Predict the output.** `branch_code` is a random number with no relationship to default. A deep random forest is trained, and we ask it for its built-in (impurity) importances. Will the noise column come out near zero?

<details><summary>Answer</summary>

No. It receives an importance of about 0.075, ranked 9th of 12 features, comparable to `age` and `employment_years`. A forest that memorises its training data (training AUC 1.000, validation 0.777) splits on noise, and the impurity measure counts those splits as useful. Permutation importance on held-out data, next, gives the same column essentially zero.

</details>

```python run
rf = ensemble.RandomForestClassifier(n_estimators=250, min_samples_leaf=1, max_features="sqrt", random_state=0, n_jobs=1)
FEATS_ALL = CORE + ["income_k", "branch_code"]
rf.fit(X_tr[FEATS_ALL], y_tr)
imp_imp = pd.Series(rf.feature_importances_, index=FEATS_ALL)
print("train AUC %.3f vs validation AUC %.3f (a deep forest memorises its training data)" % (metrics.roc_auc_score(y_tr, rf.predict_proba(X_tr[FEATS_ALL])[:, 1]), metrics.roc_auc_score(y_val, rf.predict_proba(X_val[FEATS_ALL])[:, 1])))
print("impurity importance, largest first:")
print(imp_imp.sort_values(ascending=False).round(3).head(8).to_string())
print(f"\nthe meaningless branch_code gets importance {imp_imp['branch_code']:.3f}, ranked {int((imp_imp > imp_imp['branch_code']).sum()) + 1} of {len(FEATS_ALL)}")
```
```text
train AUC 1.000 vs validation AUC 0.777 (a deep forest memorises its training data)
impurity importance, largest first:
utilisation            0.2170
debt_ratio             0.1080
credit_history_years   0.0890
income                 0.0840
loan_amount            0.0840
employment_years       0.0800
income_k               0.0790
age                    0.0760

the meaningless branch_code gets importance 0.075, ranked 9 of 12
```

### 4.2 Permutation importance: measured where it counts

**Permutation importance** (ds.05 section 11.2) shuffles one column on **held-out** data and measures the drop in the score. A feature the model genuinely uses causes a drop; a useless feature does not. It is model-agnostic and honest about generalisation.

```python run
pi = inspection.permutation_importance(rf, X_val[FEATS_ALL], y_val, scoring="roc_auc", n_repeats=10, random_state=0, n_jobs=1)
perm = pd.DataFrame({"mean AUC drop": pi.importances_mean, "std": pi.importances_std}, index=FEATS_ALL).sort_values("mean AUC drop", ascending=False)
print(perm.round(4).to_string())
print(f"\nbranch_code: impurity importance {imp_imp['branch_code']:.3f} (not small) versus permutation importance {perm.loc['branch_code', 'mean AUC drop']:.4f} (about zero)")
```
```text
                      mean AUC drop    std
utilisation                  0.1173 0.0121
income                       0.0322 0.0060
delinquencies                0.0316 0.0040
income_k                     0.0247 0.0052
debt_ratio                   0.0237 0.0041
loan_amount                  0.0090 0.0044
credit_history_years         0.0070 0.0045
inquiries                    0.0038 0.0032
region                       0.0021 0.0018
age                          0.0018 0.0017
branch_code                  0.0008 0.0020
employment_years            -0.0027 0.0014

branch_code: impurity importance 0.075 (not small) versus permutation importance 0.0008 (about zero)
```

Permutation importance puts the noise code at zero, where it belongs. Compute it on data the model did not train on.

### 4.3 The correlated-features problem

`income` and `income_k` carry the same information. Shuffle one, and the model can fall back on the other, so **each looks unimportant even though the pair is crucial**. The fix is to permute the correlated features **together** as a group.

```python run
def grouped_permutation_importance(model, X, y, groups, n_repeats=10, seed=0):
    rng = np.random.default_rng(seed)
    base = metrics.roc_auc_score(y, model.predict_proba(X)[:, 1])
    out = {}
    for name, cols in groups.items():
        drops = []
        for _ in range(n_repeats):
            Xp = X.copy()
            perm_idx = rng.permutation(len(X))
            Xp[cols] = X[cols].to_numpy()[perm_idx]                                   # shuffle the group's rows TOGETHER (keeps their mutual relationship)
            drops.append(base - metrics.roc_auc_score(y, model.predict_proba(Xp)[:, 1]))
        out[name] = (float(np.mean(drops)), float(np.std(drops)))
    return pd.DataFrame(out, index=["mean AUC drop", "std"]).T

rf2 = ensemble.RandomForestClassifier(n_estimators=250, min_samples_leaf=5, random_state=0, n_jobs=1).fit(X_tr[FEATS_ALL], y_tr)
single = {c: [c] for c in ["income", "income_k"]}
group = {"income + income_k (as a group)": ["income", "income_k"]}
print(pd.concat([grouped_permutation_importance(rf2, X_val[FEATS_ALL], y_val, single), grouped_permutation_importance(rf2, X_val[FEATS_ALL], y_val, group)]).round(4).to_string())
```
```text
                                mean AUC drop    std
income                                 0.0152 0.0036
income_k                               0.0163 0.0039
income + income_k (as a group)         0.0507 0.0058
```

Read the three rows: shuffled alone, each copy of income has a modest effect (the other covers for it); shuffled together, the drop is far larger. A report that says "income_k is unimportant" would be false; the right statement is that *income* matters, whichever column carries it. Group correlated features, or drop the duplicates before computing importance.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Make one bar chart of mean AUC drop from permutation importance with a random forest. Three bars: income alone 0.0152, income_k alone 0.0163 (income_k is a noisy copy of income), and income + income_k shuffled together as a group 0.0507. Add a small diagram showing that when one copy is shuffled the model falls back on the other copy, so single bars look small."

### 4.4 Drop-column importance and its cost

**Drop-column importance** retrains the model without each feature and measures the loss in validation score. It answers a different and often better question ("is this feature needed?") and accounts for substitutes, but it needs one retraining per feature. For a quick model it is affordable:

```python run
rows = []
base_auc = metrics.roc_auc_score(y_val, ensemble.HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_depth=4, random_state=0).fit(X_tr[CORE], y_tr).predict_proba(X_val[CORE])[:, 1])
for c in CORE:
    cols = [k for k in CORE if k != c]
    m = ensemble.HistGradientBoostingClassifier(max_iter=150, learning_rate=0.08, max_depth=4, random_state=0).fit(X_tr[cols], y_tr)
    rows.append((c, base_auc - metrics.roc_auc_score(y_val, m.predict_proba(X_val[cols])[:, 1])))
drop = pd.Series(dict(rows)).sort_values(ascending=False)
print(f"validation AUC with all features: {base_auc:.4f}")
print("AUC lost when the feature is removed and the model retrained:"); print(drop.round(4).to_string())
```
```text
validation AUC with all features: 0.7842
AUC lost when the feature is removed and the model retrained:
utilisation             0.0710
debt_ratio              0.0139
income                  0.0128
delinquencies           0.0077
inquiries               0.0021
region                  0.0011
loan_amount             0.0008
credit_history_years   -0.0000
age                    -0.0015
employment_years       -0.0023
```

Read it as "how much information is lost if this feature is not available": utilisation is clearly the most valuable, and several features whose information is partly carried by others (income and loan amount; age, credit history and employment years) lose little individually. Different importance methods answer different questions; do not expect them to agree and do not report one as "the" importance.

### 4.5 Which question does each answer

| Method | Question it answers | Weakness |
|---|---|---|
| Impurity importance | Where did the trees find splits (on training data)? | biased to high-cardinality and noisy features; train-set only |
| Permutation importance (held-out) | How much does the model's accuracy depend on this feature? | splits credit among correlated features; creates unrealistic rows |
| Grouped permutation | How much does it depend on this group? | you must choose the groups |
| Drop-column | Is this information needed at all? | expensive; substitutes hide importance |
| Coefficients (linear) | The model's weight on the feature, holding others fixed | scale-dependent; unstable under correlation |
| SHAP (section 6) | How much did each feature push the prediction away from the average? | depends on the background; model-not-world |

### 4.6 Try it

1. Compute the permutation importance on the **training** set for the forest. Does `branch_code` now look important? What does that tell you?
2. Put `loan_amount` and `income` in one group and compute the grouped permutation importance for the boosted model.

## 5. Effect plots: partial dependence, ICE and ALE

### 5.1 Partial dependence: the average effect of one feature

The **partial dependence** of the prediction on feature `j` at value `v` is the average prediction when `x_j` is set to `v` for *every* row, leaving the other columns as they are: `PD_j(v) = (1/n) Σ_i f(x_{i,-j}, v)`. It shows the **shape** of the dependence (rising, flat, saturating) averaged over the population. We implement it and check it against scikit-learn.

```python run
def partial_dependence_manual(model, X, feature, grid, predict=lambda m, d: m.predict_proba(d)[:, 1]):
    out = []
    for v in grid:
        Xv = X.copy(); Xv[feature] = v
        out.append(predict(model, Xv).mean())
    return np.array(out)

Xs = X_val[CORE].sample(1500, random_state=0)
pd_sk = inspection.partial_dependence(gbm, Xs, ["utilisation"], kind="average", grid_resolution=8, percentiles=(0.02, 0.98), method="brute", response_method="predict_proba")
grid = pd_sk["grid_values"][0]                                                    # use scikit-learn's own grid so the two are directly comparable
pd_ours = partial_dependence_manual(gbm, Xs, "utilisation", grid)
print("max |ours - scikit-learn| on the same grid:", float(np.max(np.abs(pd_ours - pd_sk["average"][0]))))
print(pd.DataFrame({"utilisation": grid, "average predicted default probability": pd_ours}).round(4).to_string(index=False))
```
```text
max |ours - scikit-learn| on the same grid: 0.0
 utilisation  average predicted default probability
      0.0555                                 0.0689
      0.1618                                 0.0689
      0.2680                                 0.0696
      0.3743                                 0.0772
      0.4805                                 0.1221
      0.5868                                 0.1792
      0.6930                                 0.2908
      0.7992                                 0.4972
```

### 5.2 ICE: one curve per borrower, and what the average hides

**Individual conditional expectation (ICE)** curves draw the same thing for each row separately. When the curves are parallel the average is a good summary. When they differ (an **interaction**), the average is misleading. Our rule has an interaction: utilisation hurts more when the debt ratio is high. Split the ICE curves by debt ratio:

```python run
def ice(model, X, feature, grid, predict=lambda m, d: m.predict_proba(d)[:, 1]):
    return np.array([predict(model, X.assign(**{feature: v})) for v in grid]).T                  # rows = borrowers, columns = grid points

curves = ice(gbm, Xs, "utilisation", grid)
high = (Xs["debt_ratio"] > 0.4).to_numpy()
tab = pd.DataFrame({"utilisation": grid, "PDP (everyone)": curves.mean(0), "debt ratio <= 0.4": curves[~high].mean(0), "debt ratio > 0.4": curves[high].mean(0)})
tab["rise vs lowest utilisation, low debt"] = tab["debt ratio <= 0.4"] - tab["debt ratio <= 0.4"].iloc[0]
tab["rise vs lowest utilisation, high debt"] = tab["debt ratio > 0.4"] - tab["debt ratio > 0.4"].iloc[0]
print(tab.round(4).to_string(index=False))
```
```text
 utilisation  PDP (everyone)  debt ratio <= 0.4  debt ratio > 0.4  rise vs lowest utilisation, low debt  rise vs lowest utilisation, high debt
      0.0555          0.0689             0.0579            0.0926                                0.0000                                 0.0000
      0.1618          0.0689             0.0579            0.0925                               -0.0001                                -0.0001
      0.2680          0.0696             0.0584            0.0938                                0.0005                                 0.0012
      0.3743          0.0772             0.0646            0.1043                                0.0067                                 0.0118
      0.4805          0.1221             0.0985            0.1728                                0.0406                                 0.0802
      0.5868          0.1792             0.1549            0.2314                                0.0970                                 0.1389
      0.6930          0.2908             0.2471            0.3845                                0.1892                                 0.2919
      0.7992          0.4972             0.3813            0.7457                                0.3234                                 0.6531
```

The average curve (PDP) is a blend. For borrowers with a high debt ratio the effect of utilisation is much steeper than for those with a low one. A single curve would tell the lender "utilisation matters moderately" when the truth is "utilisation matters a lot *for the heavily indebted*". Always look at the ICE spread or a split before accepting a PDP.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot partial dependence curves of predicted default probability against utilisation. X values: 0.0555, 0.1618, 0.2680, 0.3743, 0.4805, 0.5868, 0.6930, 0.7992. Draw three lines: everyone (0.069 to 0.497), debt ratio <= 0.4 (0.058 to 0.381), debt ratio > 0.4 (0.093 to 0.746). Label the axes and highlight that the average line hides how much steeper the high-debt curve is."

### 5.3 ALE: a safer average when features are correlated

PDP sets a feature to values that may be **impossible for that borrower** (a loan of 10 times the income for someone with low income), and the model's behaviour there is extrapolation. **Accumulated local effects (ALE)** fix this: cut the feature into bins from its quantiles, and within each bin compute the average change in prediction when the feature moves from the bin's lower edge to its upper edge **using only the rows that are actually in that bin** (so the other features take realistic values), then accumulate and centre.

```python run
def ale_1d(model, X, feature, n_bins=10, predict=lambda m, d: m.predict_proba(d)[:, 1]):
    x = X[feature].to_numpy()
    edges = np.unique(np.quantile(x, np.linspace(0, 1, n_bins + 1)))
    idx = np.clip(np.searchsorted(edges, x, side="right") - 1, 0, len(edges) - 2)
    effects = np.zeros(len(edges) - 1); counts = np.bincount(idx, minlength=len(edges) - 1)
    for k in range(len(edges) - 1):
        rows = X[idx == k]
        if len(rows) == 0: continue
        lo, hi = rows.assign(**{feature: edges[k]}), rows.assign(**{feature: edges[k + 1]})
        effects[k] = (predict(model, hi) - predict(model, lo)).mean()
    ale = np.r_[0, np.cumsum(effects)]
    centre = np.sum((ale[:-1] + ale[1:]) / 2 * counts) / counts.sum()                  # centre so the average over the data is zero
    return edges, ale - centre

edges, ale = ale_1d(gbm, Xs, "loan_amount")
pdp_loan = partial_dependence_manual(gbm, Xs, "loan_amount", edges)
print(pd.DataFrame({"loan_amount": edges, "ALE (centred)": ale, "PDP (centred)": pdp_loan - pdp_loan.mean()}).round(4).to_string(index=False))
print("correlation of loan_amount with income in this data: %.2f" % Xs["loan_amount"].corr(Xs["income"]))
```
```text
 loan_amount  ALE (centred)  PDP (centred)
  3,744.6367        -0.0070        -0.0050
 11,239.9559        -0.0065        -0.0049
 15,678.5472        -0.0066        -0.0052
 20,397.3601        -0.0033        -0.0036
 24,868.7965         0.0015         0.0006
 30,036.6992         0.0015         0.0006
 36,366.9712         0.0033         0.0025
 42,700.3871         0.0041         0.0036
 54,762.4768         0.0043         0.0039
 69,289.6107         0.0034         0.0037
241,573.8231         0.0038         0.0038
correlation of loan_amount with income in this data: 0.72
```

In this data the two curves for `loan_amount` are close: the model uses the loan amount only weakly, so there is little extrapolation for the PDP to get wrong. The difference between the two grows when the model depends strongly on correlated features and the data are thin in the region where a PDP forces unrealistic combinations. The safe habit is to say which one you show, and to look at both when features are correlated.

A different and common situation: two features that are near-copies of each other. A model has no reason to use both.

```python run
rng = np.random.default_rng(1); n_ = 6000
a_ = rng.normal(size=n_); b_ = a_ + rng.normal(0, 0.15, n_); c_ = rng.normal(size=n_)
y_syn = 2.0 * a_ + 1.0 * c_ + rng.normal(0, 0.5, n_)                              # the truth: y depends on a (weight 2) and c; b is just a noisy copy of a
D = pd.DataFrame({"a": a_, "b": b_, "c": c_})
m_syn = ensemble.HistGradientBoostingRegressor(max_iter=200, random_state=0).fit(D, y_syn)
Dv = D.sample(1500, random_state=0)
gg = np.linspace(-1.5, 1.5, 7)
for f in ["a", "b"]:
    curve = np.array([m_syn.predict(Dv.assign(**{f: v})).mean() for v in gg])
    print(f"partial dependence of {f}: slope per unit {np.polyfit(gg, curve, 1)[0]:+.2f}")
print("shifting a and b TOGETHER by one unit changes the prediction by", round(float((m_syn.predict(Dv.assign(a=Dv.a + 1, b=Dv.b + 1)) - m_syn.predict(Dv)).mean()), 2))
```
```text
partial dependence of a: slope per unit +1.97
partial dependence of b: slope per unit -0.02
shifting a and b TOGETHER by one unit changes the prediction by 2.0
```

The model found that `a` explains `y` and gives `b` no weight, so `b` looks irrelevant in every plot, although it carries exactly the same information. "The model does not use b" is true; "b is unrelated to y" is false. Explanations describe **the model**, and with correlated inputs the model's choice among near-duplicates is close to arbitrary (it can differ between two training runs), a point that matters again for Shapley values.

### 5.4 Try it

1. Draw (as a table) the ICE curves of five borrowers for `delinquencies`. Do the curves cross?
2. Compute the ALE of `income` and compare with its PDP.


## 6. Shapley values and SHAP

### 6.1 The idea: fair credit for a team result

A prediction is the joint result of many features. How much of the difference between *this* borrower's predicted risk and the *average* predicted risk is due to each feature? Game theory has a classic answer. Treat the features as **players** in a cooperative game whose payoff is the model's output. The **Shapley value** of a feature is its average marginal contribution over all the orders in which the features could join the team:

```text
φ_i = Σ over subsets S not containing i  of   [ |S|! (d − |S| − 1)! / d! ] · ( v(S ∪ {i}) − v(S) )
```

where `d` is the number of features and `v(S)` is the payoff when only the features in `S` are "present". The weight is the chance that exactly the features in `S` come before `i` in a random ordering.

The payoff `v(S)` must say what the model predicts when some features are **unknown**. A model cannot simply ignore an input, so the standard (interventional) choice fills the absent features with values drawn from a **background dataset** and averages:

```text
v(S) = average over background rows b of   f( x_S , b_{not S} )
```

Features in `S` keep the borrower's values; the others are replaced by those of a background row. So `v(∅)` is the average prediction over the background (the **base value**) and `v(all features)` is the model's prediction for this borrower.

Shapley values are the only attribution that satisfies these four properties:

| Property | Meaning |
|---|---|
| **Efficiency** | the attributions add up: `Σ φ_i = f(x) − base value` |
| **Symmetry** | two features that always contribute the same get the same value |
| **Dummy** | a feature that never changes the output gets 0 |
| **Additivity** | for a sum of models, the attributions add |

SHAP (SHapley Additive exPlanations) is this idea packaged, with fast algorithms for specific model types (TreeSHAP for trees). We build the exact version from scratch so that nothing is hidden.

### 6.2 A worked example small enough to check by hand

Take `f(x) = 2·x₀ + x₁·x₂`: feature 0 is linear, features 1 and 2 form an **interaction** (their product). The explained point is `x = (1, 2, 3)`; the background has four rows. We list `v(S)` for every one of the 8 subsets.

```python run
def f_toy(A):
    A = np.atleast_2d(A)
    return 2 * A[:, 0] + A[:, 1] * A[:, 2]

bg_toy = np.array([[0.0, 0.0, 0.0], [2.0, 1.0, 0.0], [0.0, 2.0, 1.0], [2.0, 1.0, 3.0]])
x_toy = np.array([1.0, 2.0, 3.0])
rows = []
for s in range(8):
    S = [i for i in range(3) if (s >> i) & 1]
    Z = np.where(np.isin(np.arange(3), S)[None, :], x_toy[None, :], bg_toy)
    rows.append((str(set(S)) if S else "{}", f_toy(Z).mean()))
print(pd.DataFrame(rows, columns=["present features S", "v(S) = average prediction"]).to_string(index=False))
print("base value v({}) =", f_toy(bg_toy).mean(), "| prediction f(x) =", float(f_toy(x_toy)[0]))
```
```text
present features S  v(S) = average prediction
                {}                     3.2500
               {0}                     3.2500
               {1}                     4.0000
            {0, 1}                     4.0000
               {2}                     5.0000
            {0, 2}                     5.0000
            {1, 2}                     8.0000
         {0, 1, 2}                     8.0000
base value v({}) = 3.25 | prediction f(x) = 8.0
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a lattice (cube) diagram of the 8 subsets of features {0,1,2} for f(x)=2*x0 + x1*x2 at x=(1,2,3), with a background of 4 rows. Label each node with v(S): {} 3.25, {0} 3.25, {1} 4.0, {0,1} 4.0, {2} 5.0, {0,2} 5.0, {1,2} 8.0, {0,1,2} 8.0. Colour the edges where feature 1 or 2 is added, and show the final Shapley values 0, 1.875, 2.875."

### 6.3 The exact algorithm

The code follows the formula. It builds all `2^d` coalitions as bit patterns, evaluates the model once on every (coalition, background row) combination, then applies the weights.

```python run
def shapley_exact(f, x, background):
    """Exact interventional Shapley values of f at x. Returns (phi, base_value, f_at_x)."""
    x, B = np.asarray(x, float), np.asarray(background, float)
    d = len(x); M = 1 << d
    subsets = np.arange(M)
    mask = ((subsets[:, None] >> np.arange(d)) & 1).astype(bool)                  # (M, d): True = the feature keeps x's value
    Z = np.where(mask[:, None, :], x[None, None, :], B[None, :, :])                # (M, background rows, d)
    v = np.asarray(f(Z.reshape(-1, d))).reshape(M, len(B)).mean(1)                 # v(S) for every coalition
    size = mask.sum(1)
    w = np.array([math.factorial(s) * math.factorial(d - s - 1) / math.factorial(d) for s in range(d)])
    phi = np.zeros(d)
    for i in range(d):
        without = subsets[~mask[:, i]]
        phi[i] = np.sum(w[size[without]] * (v[without | (1 << i)] - v[without]))
    return phi, float(v[0]), float(v[M - 1])

phi, base, fx = shapley_exact(f_toy, x_toy, bg_toy)
print("Shapley values:", phi.round(4), "| base", base, "| f(x)", fx)
print("efficiency: sum of phi + base =", round(float(phi.sum() + base), 6), "= f(x) =", fx)
print("feature 0 (linear, weight 2):  2 * (x0 - mean of background x0) =", 2 * (x_toy[0] - bg_toy[:, 0].mean()))
```
```text
Shapley values: [0.    1.875 2.875] | base 3.25 | f(x) 8.0
efficiency: sum of phi + base = 8.0 = f(x) = 8.0
feature 0 (linear, weight 2):  2 * (x0 - mean of background x0) = 0.0
```

Read the results. Feature 0 is linear, and `x₀ = 1` happens to sit exactly at the background average of `x₀` (which is 1), so it gets exactly 0. Features 1 and 2 form a product; together they account for the whole rise from 3.25 to 8 (4.75), and the Shapley values share that between them (1.875 and 2.875), not equally, because `x₂ = 3` is further from its background average than `x₁ = 2` is from its own. Efficiency holds exactly.

### 6.4 Linear models have a closed form

For a linear model `f(x) = b + Σ w_j x_j` the marginal contribution of feature `j` never depends on the others, so `φ_j = w_j (x_j − mean of x_j over the background)`. This gives a ready-made test of the code:

```python run
rng_b = np.random.default_rng(0)
bg = X_dev[CORE].sample(100, random_state=0).to_numpy()
lin_f = lambda A: logit_model.decision_function(pd.DataFrame(A, columns=CORE))
x0 = X_test[CORE].iloc[0].to_numpy()
phi_lin, base_lin, fx_lin = shapley_exact(lin_f, x0, bg)
w = logit_model[-1].coef_[0] / logit_model[0].scale_                                  # coefficient per ORIGINAL unit of each feature
closed = w * (x0 - bg.mean(0))
print("max |exact enumeration - closed form w_j (x_j - mean_j)| =", float(np.max(np.abs(phi_lin - closed))))
print("efficiency check: sum(phi) + base - prediction =", float(phi_lin.sum() + base_lin - fx_lin))
```
```text
max |exact enumeration - closed form w_j (x_j - mean_j)| = 1.6653345369377348e-16
efficiency check: sum(phi) + base - prediction = -2.220446049250313e-16
```

Agreement to rounding error means the enumeration is right. (The log-odds of the logistic regression is the function `f` here, because attributions are additive on the log-odds scale.)

### 6.5 Explaining one borrower with the boosted model

Pick the test borrower with the highest predicted risk. We explain the model's **log-odds** and then translate.

```python run
gb_logodds = lambda A: gbm.decision_function(A)
bg = X_dev[CORE].sample(100, random_state=1).to_numpy()
p_test = gbm.predict_proba(X_test[CORE])[:, 1]
i_hi = int(np.argmax(p_test)); x_hi = X_test[CORE].iloc[i_hi].to_numpy()
t0 = time.perf_counter()
phi_hi, base_hi, fx_hi = shapley_exact(gb_logodds, x_hi, bg)
print(f"exact Shapley values for 10 features (1,024 coalitions x 100 background rows = 102,400 predictions): {time.perf_counter() - t0:.2f} s")
expl = pd.DataFrame({"value": x_hi, "average value": bg.mean(0), "contribution to log-odds": phi_hi}, index=CORE).sort_values("contribution to log-odds", ascending=False)
print(expl.round(3).to_string())
sig = lambda z: 1 / (1 + np.exp(-z))
print(f"\nbase value (average borrower): log-odds {base_hi:+.3f} = probability {sig(base_hi):.3f}")
print(f"this borrower: log-odds {fx_hi:+.3f} = probability {sig(fx_hi):.3f}; sum of contributions {phi_hi.sum():+.3f}; check {base_hi + phi_hi.sum() - fx_hi:+.1e}")
```
```text
exact Shapley values for 10 features (1,024 coalitions x 100 background rows = 102,400 predictions): 0.12 s
                           value  average value  contribution to log-odds
utilisation               0.8820         0.3770                    2.5790
debt_ratio                0.6800         0.2840                    0.9690
delinquencies             1.0000         0.3100                    0.5110
income               34,222.0640    58,833.5860                    0.3460
inquiries                 7.0000         1.5900                    0.2160
credit_history_years      6.3750        11.4680                    0.2120
region                    2.0000         1.1400                    0.1170
employment_years          1.5080         6.2960                    0.0840
loan_amount          32,186.2360    34,413.9740                    0.0230
age                      41.5800        41.2820                   -0.0040

base value (average borrower): log-odds -2.349 = probability 0.087
this borrower: log-odds +2.704 = probability 0.937; sum of contributions +5.053; check +8.9e-16
```

Read the table as a bridge from the average borrower to this one: start at the base value and add each feature's contribution. Positive contributions push the risk up, negative ones push it down.

> **Predict the output.** The contributions are measured in log-odds. Suppose a borrower's total contribution from utilisation is +1.0 and from income is +1.0 (both in log-odds). Do they raise the *probability* of default by the same number of percentage points?

<details><summary>Answer</summary>

Not in general. The log-odds scale is additive, the probability scale is not: the same +1.0 in log-odds moves a probability of 2% to about 5% (+3 points) but a probability of 40% to about 64% (+24 points).

```python run
for p0 in [0.02, 0.10, 0.40, 0.80]:
    lo = math.log(p0 / (1 - p0)); p1 = 1 / (1 + math.exp(-(lo + 1.0)))
    print(f"start at probability {p0:.2f}: adding +1.0 log-odds gives {p1:.3f} ({(p1 - p0) * 100:+.1f} percentage points)")
```
```text
start at probability 0.02: adding +1.0 log-odds gives 0.053 (+3.3 percentage points)
start at probability 0.10: adding +1.0 log-odds gives 0.232 (+13.2 percentage points)
start at probability 0.40: adding +1.0 log-odds gives 0.644 (+24.4 percentage points)
start at probability 0.80: adding +1.0 log-odds gives 0.916 (+11.6 percentage points)
```

So attributions in log-odds can be added and compared with each other, but a statement like "utilisation adds 12 points of risk" is only valid for one specific ordering and starting point. Say "raises the odds by a factor of e^φ", or report the order of the drivers, not points.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a waterfall chart explaining one borrower's default risk in log-odds. Start at the base value -2.349 (average borrower, probability 0.087). Add contributions: utilisation +2.579, debt_ratio +0.969, delinquencies +0.511, income +0.346, inquiries +0.216, credit_history_years +0.212, region +0.117, employment_years +0.084, loan_amount +0.023, age -0.004. End at +2.704 (probability 0.937)."

### 6.6 The cost, and a sampling approximation

Exact enumeration costs `2^d` coalitions: fine for 10 features, impossible for 40. The **permutation-sampling** estimator draws a random ordering of the features and one random background row `z`, then walks from `z` towards `x` one feature at a time, recording each feature's marginal change. Averaging over many orderings is an unbiased estimate of the same Shapley value, with cost `m · (d + 1)` evaluations.

```python run
def shapley_sampling(f, x, background, m=2000, seed=0):
    r = np.random.default_rng(seed)
    x, B = np.asarray(x, float), np.asarray(background, float)
    d = len(x)
    z = B[r.integers(len(B), size=m)]                                               # one background row per ordering
    perms = np.argsort(r.random((m, d)), axis=1)                                    # a random order of the d features for each sample
    pts = np.repeat(z[:, None, :], d + 1, axis=1)                                   # (m, d+1, d): point k has the first k features (in order) set to x's values
    for k in range(1, d + 1):
        for j in range(k):
            pts[np.arange(m), k, perms[:, j]] = x[perms[:, j]]
    vals = np.asarray(f(pts.reshape(-1, d))).reshape(m, d + 1)
    contrib = vals[:, 1:] - vals[:, :-1]                                            # marginal contribution of the feature added at step k
    phi = np.zeros(d)
    np.add.at(phi, perms.ravel(), contrib.ravel())
    return phi / m

rows = []
for m in [50, 200, 1000, 5000]:
    errs = [np.max(np.abs(shapley_sampling(gb_logodds, x_hi, bg, m=m, seed=s) - phi_hi)) for s in range(5)]
    t0 = time.perf_counter(); shapley_sampling(gb_logodds, x_hi, bg, m=m, seed=0); el = time.perf_counter() - t0
    rows.append((m, m * 11, np.mean(errs), el))
print(pd.DataFrame(rows, columns=["orderings m", "model evaluations", "mean max error vs exact (log-odds)", "seconds"]).round(4).to_string(index=False))
print("exact enumeration for comparison: 102,400 evaluations")
```
```text
 orderings m  model evaluations  mean max error vs exact (log-odds)  seconds
          50                550                              0.1521   0.0015
         200               2200                              0.0564   0.0023
        1000              11000                              0.0238   0.0063
        5000              55000                              0.0092   0.0326
exact enumeration for comparison: 102,400 evaluations
```

The error falls like `1/sqrt(m)`. This is the trade used in practice for models with many features: accept a small, controllable sampling error. (TreeSHAP computes exact values for tree ensembles in polynomial time by exploiting the tree structure; it is what `shap.TreeExplainer` uses, but it explains a slightly different value function, the tree's own conditional expectation.)

### 6.7 From local to global: SHAP importance and dependence

Averaging the absolute attributions over many borrowers gives a global importance with a direct meaning: *how many log-odds units this feature moves a typical prediction*. Computing exact values for 120 test borrowers:

```python run
t0 = time.perf_counter()
sample_idx = np.random.default_rng(2).choice(len(X_test), 120, replace=False)
Xs_ = X_test[CORE].iloc[sample_idx].to_numpy()
PHI = np.array([shapley_exact(gb_logodds, x, bg)[0] for x in Xs_])
print(f"{len(Xs_)} exact explanations in {time.perf_counter() - t0:.0f} s | efficiency holds for all: {bool(np.allclose(PHI.sum(1) + base_hi, gbm.decision_function(pd.DataFrame(Xs_, columns=CORE)), atol=1e-6))}")
shap_imp = pd.Series(np.abs(PHI).mean(0), index=CORE).sort_values(ascending=False)
pi_gbm = inspection.permutation_importance(gbm, X_test[CORE], y_test, scoring="roc_auc", n_repeats=8, random_state=0, n_jobs=1)
pi_gbm = pd.Series(pi_gbm.importances_mean, index=CORE)
cmp_ = pd.DataFrame({"mean |SHAP| (log-odds)": shap_imp, "permutation importance (AUC drop)": pi_gbm.reindex(shap_imp.index)})
print(cmp_.round(4).to_string())
print("rank correlation between the two importance measures: %.2f" % stats.spearmanr(cmp_.iloc[:, 0], cmp_.iloc[:, 1]).statistic)
```
```text
120 exact explanations in 8 s | efficiency holds for all: True
                      mean |SHAP| (log-odds)  permutation importance (AUC drop)
utilisation                           0.6339                             0.1369
income                                0.3271                             0.0371
debt_ratio                            0.3217                             0.0202
delinquencies                         0.2793                             0.0292
credit_history_years                  0.1367                             0.0057
employment_years                      0.0910                            -0.0014
inquiries                             0.0336                             0.0014
loan_amount                           0.0274                            -0.0000
region                                0.0250                             0.0010
age                                   0.0128                            -0.0003
rank correlation between the two importance measures: 0.85
```

The two measures agree on the top features and may disagree about the rest, because they ask different questions (how much does this feature move predictions versus how much does accuracy depend on it).

A **dependence** view shows *how* a feature's contribution changes with its value, and colouring by a second feature reveals interactions. With a table instead of a plot:

```python run
d = pd.DataFrame({"utilisation": Xs_[:, CORE.index("utilisation")], "phi_utilisation": PHI[:, CORE.index("utilisation")], "debt_ratio": Xs_[:, CORE.index("debt_ratio")]})
d["utilisation band"] = pd.cut(d["utilisation"], [0, 0.3, 0.5, 0.7, 1.01], labels=["<=0.3", "0.3-0.5", "0.5-0.7", ">0.7"])
d["debt ratio"] = np.where(d["debt_ratio"] > 0.4, "high (>0.4)", "low (<=0.4)")
print(d.pivot_table(index="utilisation band", columns="debt ratio", values="phi_utilisation", aggfunc=["mean", "count"], observed=True).round(3).to_string())
```
```text
                        mean                   count            
debt ratio       high (>0.4) low (<=0.4) high (>0.4) low (<=0.4)
utilisation band                                                
<=0.3                -0.5420     -0.5200          17          29
0.3-0.5              -0.3310     -0.1270          11          24
0.5-0.7               0.7990      0.6510           8          21
>0.7                  2.5810      1.8940           4           6
```

The contribution of utilisation rises with utilisation (the non-linearity) and is larger for the highly indebted at high utilisation (the interaction). Exactly what the data-generating rule says.

### 6.8 The limits of SHAP: five experiments

Shapley values are mathematically neat and widely over-trusted. Each of the following is a way they get misread.

**(a) The answer depends on the background: "compared with whom?"**

```python run
bg_all = X_dev[CORE].sample(100, random_state=3).to_numpy()
low_risk = X_dev[CORE][gbm.predict_proba(X_dev[CORE])[:, 1] < 0.05].sample(100, random_state=3).to_numpy()
phi_all, base_all, _ = shapley_exact(gb_logodds, x_hi, bg_all)
phi_low, base_low, _ = shapley_exact(gb_logodds, x_hi, low_risk)
cmp_bg = pd.DataFrame({"vs all borrowers": phi_all, "vs low-risk borrowers only": phi_low}, index=CORE)
print(cmp_bg.round(3).to_string())
print(f"base value (log-odds): {base_all:+.2f} vs {base_low:+.2f}; the borrower's prediction is {fx_hi:+.2f} in both cases")
```
```text
                      vs all borrowers  vs low-risk borrowers only
age                            -0.0060                     -0.0100
income                          0.3220                      0.6010
employment_years                0.0870                      0.1220
debt_ratio                      0.7640                      1.0460
utilisation                     2.6860                      2.9950
delinquencies                   0.5110                      0.7320
credit_history_years            0.1940                      0.2540
inquiries                       0.2140                      0.1930
loan_amount                     0.0260                     -0.0030
region                          0.1230                      0.0980
base value (log-odds): -2.22 vs -3.32; the borrower's prediction is +2.70 in both cases
```

Same borrower, same model, same prediction, different explanations, because the question changed from "why is this borrower riskier than average?" to "why is this borrower riskier than a low-risk one?". Always state the background in the explanation, and choose it to match the question (typically the population the decision is made on).

**(b) Correlated or duplicated features: the credit is split arbitrarily.** `income` and `income_k` are the same quantity. Four forests, differing only in their random seed, explain the same borrower:

```python run
FE = CORE + ["income_k"]
bg_e = X_dev[FE].sample(60, random_state=4).to_numpy()
xe = X_test[FE].iloc[i_hi].to_numpy()
rows = []
for seed in range(4):
    rf_s = ensemble.RandomForestClassifier(n_estimators=60, min_samples_leaf=25, max_features=0.5, random_state=seed, n_jobs=1).fit(X_dev[FE], y_dev)
    f_rf = lambda A, m=rf_s: m.predict_proba(A)[:, 1]
    ph, _, _ = shapley_exact(f_rf, xe, bg_e)
    rows.append((seed, ph[FE.index("income")], ph[FE.index("income_k")], ph[FE.index("income")] + ph[FE.index("income_k")]))
print(pd.DataFrame(rows, columns=["forest seed", "phi(income)", "phi(income_k)", "phi(income) + phi(income_k)"]).round(4).to_string(index=False))
```
```text
 forest seed  phi(income)  phi(income_k)  phi(income) + phi(income_k)
           0       0.0356         0.0178                       0.0535
           1       0.0350         0.0209                       0.0559
           2       0.0374         0.0269                       0.0643
           3       0.0323         0.0246                       0.0569
```

(Here the attributions are in probability units because the forest outputs probabilities.) The **sum** of the two attributions is similar from model to model (0.054 to 0.064), while the **split** between the two copies moves: `income_k` receives between a third and over 40% of the total depending only on the random seed. Reporting "income_k contributes X" is reporting an accident of training. Merge duplicate features or sum their attributions before explaining.

**(c) It explains the model, not the world.** Attributions say what the model *did*. They do not say what would happen if a feature were changed in reality (causal effect, ds.09), nor that the feature is the real cause. The model may use `inquiries` because it correlates with utilisation; the borrower cannot reduce risk by deleting an inquiry. Treat "feature X pushes this prediction up" as a statement about the model, and add "and in the real world X is / is not something the borrower can act on" only from domain knowledge.

**(d) Additive explanation of a non-additive model.** The Shapley split of an interaction between two features is equal by construction (section 6.3), a convention rather than a measurement. If the model's behaviour is dominated by an interaction, a single bar per feature hides it. Look at SHAP interaction values or dependence plots coloured by the partner feature.

**(e) Explanations can be fooled and can be unfaithful when approximated.** Sampling error (6.6), a small or unrepresentative background (a), and deliberately built models that behave differently on the synthetic points used by perturbation methods can all produce attributions that look reasonable and are wrong. Check the explanations (section 8.3).

The library version, for reference (not installed here, so no output is shown):

```python
# Try it on your machine:  pip install shap
import shap
explainer = shap.TreeExplainer(gbm, data=X_dev[CORE].sample(100, random_state=0), feature_perturbation="interventional", model_output="raw")
sv = explainer(X_test[CORE].iloc[:200])              # sv.values: (200, 10) log-odds contributions, sv.base_values: the base value
shap.plots.waterfall(sv[0])                           # one borrower, as a chart
shap.plots.beeswarm(sv)                               # global importance and dependence in one picture
```

### 6.9 Try it

1. Run `shapley_exact` for the logistic regression with the borrower from 6.5 and compare its attributions with the boosted model's. Where do they differ, and does it match the interaction we planted?
2. Explain the same borrower with background sizes 10, 30, 100 and 300 and measure how much the attributions change.

## 7. Local explanations: LIME-style surrogates, reason codes and counterfactuals

### 7.1 LIME: a local straight-line approximation

**LIME** (Local Interpretable Model-agnostic Explanations) explains one prediction by fitting a simple model to the black box's behaviour **near** that point: generate perturbed copies of the borrower, ask the model for their predictions, weight them by closeness, and fit a weighted linear regression. The coefficients are the local slopes: "around this borrower, one more standard deviation of utilisation adds this many log-odds".

```python run
def lime_like(f, x, X_ref, n=3000, kernel_width=None, seed=0, alpha=1.0):
    r = np.random.default_rng(seed)
    sd = X_ref.std(0).to_numpy() if hasattr(X_ref, "std") else np.std(X_ref, axis=0)
    d = len(x)
    Z = x + r.normal(size=(n, d)) * sd                                              # perturb every feature by about one standard deviation
    dist = np.linalg.norm((Z - x) / sd, axis=1)
    kw = kernel_width or 0.75 * math.sqrt(d)
    wts = np.exp(-dist ** 2 / kw ** 2)                                               # closer points count more
    reg = linear_model.Ridge(alpha=alpha).fit((Z - x) / sd, f(Z), sample_weight=wts)
    return reg.coef_                                                                 # log-odds per standard deviation, around x

coef_lime = lime_like(gb_logodds, x_hi, X_dev[CORE])
comp = pd.DataFrame({"LIME slope (log-odds per std)": coef_lime, "Shapley value (log-odds)": phi_hi}, index=CORE)
print(comp.round(3).to_string())
```
```text
                      LIME slope (log-odds per std)  Shapley value (log-odds)
age                                          0.0160                   -0.0040
income                                      -0.1920                    0.3460
employment_years                            -0.0520                    0.0840
debt_ratio                                   0.1980                    0.9690
utilisation                                  0.5450                    2.5790
delinquencies                                0.3480                    0.5110
credit_history_years                        -0.1170                    0.2120
inquiries                                    0.0180                    0.2160
loan_amount                                  0.0550                    0.0230
region                                       0.1020                    0.1170
```

LIME's numbers are **slopes at the point**, SHAP's are **contributions relative to the background**, so they are not the same quantity. The income row shows it: the local slope is negative (more income would lower this borrower's risk), while the Shapley value is positive (this borrower's income is *below* the background average, which raises the risk relative to an average borrower). Both are true; they answer different questions. Compare the rankings, and read each number for what it is. More important is stability.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 1D picture of LIME. Plot a wiggly black-box curve of log-odds against utilisation. Mark the explained borrower's point (utilisation 0.882). Scatter perturbed points around it, with size showing closeness weight (large near the point, small far away). Draw the weighted straight line fitted to them, and label its slope as the local effect: about 0.545 log-odds per standard deviation of utilisation."

### 7.2 LIME's weakness: randomness and kernel choice

```python run
def top3(c, names=CORE):
    return [names[i] for i in np.argsort(-np.abs(c))[:3]]
rows = []
for seed in range(5):
    rows.append((f"seed {seed}", ", ".join(top3(lime_like(gb_logodds, x_hi, X_dev[CORE], seed=seed)))))
for kw in [0.5, 1.5, 3.0]:
    rows.append((f"kernel width {kw}", ", ".join(top3(lime_like(gb_logodds, x_hi, X_dev[CORE], kernel_width=kw)))))
print(pd.DataFrame(rows, columns=["setting", "top three features by |slope|"]).to_string(index=False))
print("Shapley top three:", ", ".join(top3(phi_hi)), "(deterministic: exact enumeration gives the same answer every time)")
```
```text
         setting          top three features by |slope|
          seed 0 utilisation, delinquencies, debt_ratio
          seed 1 utilisation, delinquencies, debt_ratio
          seed 2 utilisation, delinquencies, debt_ratio
          seed 3     utilisation, delinquencies, income
          seed 4     utilisation, delinquencies, income
kernel width 0.5       delinquencies, region, inquiries
kernel width 1.5     utilisation, delinquencies, income
kernel width 3.0 utilisation, delinquencies, debt_ratio
Shapley top three: utilisation, debt_ratio, delinquencies (deterministic: exact enumeration gives the same answer every time)
```

Different random seeds and different kernel widths can reorder the features. A "local" model depends on what you call local. This does not make LIME useless, but it means a LIME explanation needs to be repeated and checked, which is not necessary for exact Shapley values.

### 7.3 Reason codes: telling the borrower why

In lending, a declined applicant must be told the **principal reasons**. A standard recipe: take the features that most **increased** the predicted risk (the largest positive attributions), skip any that are not permitted as reasons or that the applicant cannot understand, and translate them into plain language.

```python run
REASON_TEXT = {
    "utilisation": "you are using a high share of your available credit",
    "delinquencies": "you have a history of missed payments",
    "debt_ratio": "your debts are high compared with your income",
    "income": "your income is low for the amount you want to borrow",
    "credit_history_years": "your credit history is short",
    "inquiries": "there have been many recent credit enquiries on your file",
    "loan_amount": "the loan amount requested is large relative to your income",
    "employment_years": "you have been in your current employment for a short time",
}
NOT_A_REASON = {"age", "region"}                                                     # features we never present as a reason for a decision

def reason_codes(phi, k=3, names=CORE):
    order = np.argsort(-phi)
    out = []
    for i in order:
        if phi[i] <= 0: break
        if names[i] in NOT_A_REASON or names[i] not in REASON_TEXT: continue
        out.append((names[i], REASON_TEXT[names[i]], float(phi[i])))
        if len(out) == k: break
    return out

print(f"borrower {i_hi}: predicted probability of default {sig(fx_hi):.1%}")
for rank, (name, text, ph) in enumerate(reason_codes(phi_hi), start=1):
    print(f"  reason {rank}: {text}   [{name}, contribution {ph:+.2f} log-odds]")
```
```text
borrower 403: predicted probability of default 93.7%
  reason 1: you are using a high share of your available credit   [utilisation, contribution +2.58 log-odds]
  reason 2: your debts are high compared with your income   [debt_ratio, contribution +0.97 log-odds]
  reason 3: you have a history of missed payments   [delinquencies, contribution +0.51 log-odds]
```

The notice a lender sends contains only the plain-language reasons. The numbers in brackets are for the audit file.

### 7.4 Counterfactual explanations: what would change the decision

A counterfactual answers the question that matters most to the affected person: **"what would I have to change to be approved?"** We search for the **smallest change in actionable features** that brings the predicted risk below the approval cutoff. Not all features are fair game: age and region cannot be changed, past delinquencies cannot be undone, and changes should be plausible.

```python run
CUTOFF = 0.20                                                                        # approve if predicted default probability is below 20%
ACTIONABLE = {"utilisation": ("absolute floor", 0.05), "debt_ratio": ("absolute floor", 0.05), "loan_amount": ("share of the current value", 0.30)}     # features that can be LOWERED, and how far
stds = X_dev[CORE].std()

def counterfactual(model, x, cutoff=CUTOFF, steps=11, max_features=3):
    x = np.asarray(x, float)
    base_p = model.predict_proba(pd.DataFrame([x], columns=CORE))[:, 1][0]
    if base_p < cutoff:
        return base_p, None
    names = list(ACTIONABLE)
    grids = {}
    for nme in names:
        kind, bound = ACTIONABLE[nme]
        cur = x[CORE.index(nme)]
        floor = bound if kind == "absolute floor" else cur * bound
        grids[nme] = np.linspace(cur, min(cur, floor), steps)                       # from today's value down to the lowest value we allow
    best = None
    for k in range(1, max_features + 1):
        for combo in itertools.combinations(names, k):
            for vals in itertools.product(*[grids[c][1:] for c in combo]):
                cand = x.copy()
                for c, v in zip(combo, vals): cand[CORE.index(c)] = v
                p = model.predict_proba(pd.DataFrame([cand], columns=CORE))[:, 1][0]
                if p < cutoff:
                    cost = sum(abs(cand[CORE.index(c)] - x[CORE.index(c)]) / stds[c] for c in combo)
                    if best is None or cost < best[0]:
                        best = (cost, combo, {c: (x[CORE.index(c)], cand[CORE.index(c)]) for c in combo}, p)
        if best is not None:
            break
    return base_p, best

declined = [i for i in range(len(X_test)) if gbm.predict_proba(X_test[CORE].iloc[[i]])[:, 1][0] > 0.30][:3]
for i in declined:
    p0, best = counterfactual(gbm, X_test[CORE].iloc[i].to_numpy())
    print(f"borrower {i}: predicted default probability {p0:.1%} -> declined (cutoff {CUTOFF:.0%})")
    if best is None:
        print("   no combination of the actionable changes reaches the cutoff")
    else:
        cost, combo, changes, p1 = best
        print("   smallest change found:", "; ".join(f"{c}: {a:,.2f} -> {b:,.2f}" for c, (a, b) in changes.items()), f"| new probability {p1:.1%}")
```
```text
borrower 18: predicted default probability 85.3% -> declined (cutoff 20%)
   smallest change found: utilisation: 0.79 -> 0.34 | new probability 13.0%
borrower 29: predicted default probability 49.9% -> declined (cutoff 20%)
   smallest change found: utilisation: 0.75 -> 0.68 | new probability 12.4%
borrower 35: predicted default probability 48.9% -> declined (cutoff 20%)
   smallest change found: utilisation: 0.74 -> 0.54 | new probability 19.1%
```

Counterfactual advice has traps worth stating on the page:

| Trap | What can go wrong |
|---|---|
| **Not causal** | the model says lower utilisation lowers the score; that does not guarantee that lowering it will make the borrower repay |
| **Not actionable** | "increase your income by 40%" is advice nobody can follow quickly; restrict to features that can change, and cap the size of the change |
| **Not plausible** | a combination that never occurs in real borrowers is an extrapolation of the model |
| **Not stable** | a retrained model gives different advice; people who followed advice may still be declined |
| **Gaming** | published recourse lets people move features without changing the underlying risk |

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a before and after picture of a counterfactual explanation. Plot predicted default probability against utilisation, with a horizontal line at the 20% approval cutoff. Mark borrower 18 at utilisation 0.79 (probability 85.3%, declined) and an arrow moving left to utilisation 0.34 (probability 13.0%, approved). Shade the approved region below the cutoff and label the change needed."

### 7.5 Try it

1. Change `CUTOFF` to 0.10 and 0.30 and see how the recourse changes for the same borrowers.
2. Add `inquiries` to the actionable set (with a direction "down") and explain why that change takes time and may not be a fair instruction.

## 8. Global surrogates and what explanations cannot tell you

### 8.1 A global surrogate: a readable copy

Train a small, readable model (a shallow tree) to **imitate the black box's predictions**, not the true outcomes. Its rules summarise how the complex model behaves overall. The key number is its **fidelity**: how well the copy reproduces the black box.

```python run
surrogate_target = gbm.predict_proba(X_dev[CORE])[:, 1]
rows = []
for depth in [2, 3, 4, 5]:
    sur = tree.DecisionTreeRegressor(max_depth=depth, min_samples_leaf=100, random_state=0).fit(X_dev[CORE], surrogate_target)
    fid_test = metrics.r2_score(gbm.predict_proba(X_test[CORE])[:, 1], sur.predict(X_test[CORE]))
    rows.append((depth, 2 ** depth, fid_test))
print(pd.DataFrame(rows, columns=["surrogate depth", "leaves (at most)", "fidelity: R-squared to the black box on test data"]).round(3).to_string(index=False))
sur = tree.DecisionTreeRegressor(max_depth=3, min_samples_leaf=100, random_state=0).fit(X_dev[CORE], surrogate_target)
print(export_text(sur, feature_names=CORE, decimals=2))
```
```text
 surrogate depth  leaves (at most)  fidelity: R-squared to the black box on test data
               2                 4                                             0.6870
               3                 8                                             0.7660
               4                16                                             0.8260
               5                32                                             0.8610
|--- utilisation <= 0.68
|   |--- utilisation <= 0.52
|   |   |--- delinquencies <= 0.50
|   |   |   |--- value: [0.07]
|   |   |--- delinquencies >  0.50
|   |   |   |--- value: [0.13]
|   |--- utilisation >  0.52
|   |   |--- delinquencies <= 0.50
|   |   |   |--- value: [0.15]
|   |   |--- delinquencies >  0.50
|   |   |   |--- value: [0.28]
|--- utilisation >  0.68
|   |--- debt_ratio <= 0.40
|   |   |--- delinquencies <= 1.50
|   |   |   |--- value: [0.34]
|   |   |--- delinquencies >  1.50
|   |   |   |--- value: [0.53]
|   |--- debt_ratio >  0.40
|   |   |--- utilisation <= 0.74
|   |   |   |--- value: [0.62]
|   |   |--- utilisation >  0.74
|   |   |   |--- value: [0.80]
```

A surrogate with a fidelity of 0.7 is a useful sketch; one with 0.3 is misleading, and the risk is that the reader sees tidy rules and forgets that the copy is wrong for a third of the behaviour. Always report the fidelity next to the rules.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a diagram of a global surrogate. On the left a black box (gradient boosting) produces predicted default probabilities for borrowers; on the right a depth-3 decision tree is trained to copy those predictions, not the true outcomes. Show the tree: utilisation <= 0.68 first, leaf values from 0.07 to 0.80. Add a small bar chart of fidelity R-squared for depths 2 to 5: 0.687, 0.766, 0.826, 0.861."

### 8.2 What explanations cannot tell you

| An explanation cannot tell you | Why |
|---|---|
| That the model is **right** | it describes the model's behaviour, including its mistakes |
| What **causes** the outcome | attributions follow the model's use of correlations (ds.09) |
| What would happen if a feature changed **in the world** | the model was fitted on observational data; intervening is a different question |
| That the explanation is **stable** | depends on background, random seeds, correlated features, model retraining |
| That **protected information** is not used | a model can use proxies; an explanation shows features, not meanings |
| That the model is **fair** | needs separate group-level tests (section 10) |

### 8.3 Sanity-check your explanations

Three checks that catch bad explanations before they reach a report.

**(1) Deletion (faithfulness) test.** If the top-attributed features really drive the prediction, then replacing them by typical values should change the prediction a lot, much more than replacing the *least* important features.

> **Predict the output.** For each of 120 borrowers we replace the features with the largest attributions by their average value and measure how much the prediction changes (in log-odds). We do the same with the *least* attributed features. After replacing just **one** feature, how do the two compare?

<details><summary>Answer</summary>

Replacing the single most-attributed feature changes the prediction by about 0.74 log-odds on average; replacing the single least-attributed feature changes it by about 0.01. The attributions pass the faithfulness test: the features the explanation calls important are the ones the model actually depends on.

</details>

```python run
def deletion_curve(f, X, PHI, bg_mean, order="top", k_max=5):
    out = []
    for kdel in range(0, k_max + 1):
        Xm = X.copy()
        for n_ in range(len(X)):
            ranking = np.argsort(-np.abs(PHI[n_])) if order == "top" else np.argsort(np.abs(PHI[n_]))
            Xm[n_, ranking[:kdel]] = bg_mean[ranking[:kdel]]
        out.append(np.mean(np.abs(f(Xm) - f(X))))
    return out
bg_mean = bg.mean(0)
top_ = deletion_curve(gb_logodds, Xs_, PHI, bg_mean, "top"); bottom_ = deletion_curve(gb_logodds, Xs_, PHI, bg_mean, "bottom")
print(pd.DataFrame({"features replaced by the average": range(6), "mean |change| in log-odds: top-attributed first": top_, "least-attributed first": bottom_}).round(3).to_string(index=False))
```
```text
 features replaced by the average  mean |change| in log-odds: top-attributed first  least-attributed first
                                0                                           0.0000                  0.0000
                                1                                           0.7350                  0.0090
                                2                                           0.9610                  0.0140
                                3                                           1.0140                  0.0300
                                4                                           1.0800                  0.0600
                                5                                           1.1420                  0.1290
```

If removing the "important" features changes the prediction no more than removing the "unimportant" ones, the explanation is not faithful.

**(2) Model-randomisation test.** An explanation method should respond to the model. Train the same model on **shuffled labels** (a model that has learned nothing) and explain it: the attributions should collapse. If they still look convincing, the method explains the data or the code, not the model.

```python run
y_shuf = np.random.default_rng(0).permutation(y_dev)
gbm_junk = ensemble.HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_depth=4, min_samples_leaf=40, random_state=0).fit(X_dev[CORE], y_shuf)
f_junk = lambda A: gbm_junk.decision_function(A)
PHI_junk = np.array([shapley_exact(f_junk, x, bg)[0] for x in Xs_[:40]])
print("test AUC of the junk model: %.3f (chance)" % metrics.roc_auc_score(y_test, gbm_junk.predict_proba(X_test[CORE])[:, 1]))
print("mean |SHAP| (log-odds), real model vs junk model:")
print(pd.DataFrame({"real model": np.abs(PHI[:40]).mean(0), "model trained on shuffled labels": np.abs(PHI_junk).mean(0)}, index=CORE).round(3).to_string())
print("total attribution mass: real %.2f vs junk %.2f" % (np.abs(PHI[:40]).sum(1).mean(), np.abs(PHI_junk).sum(1).mean()))
```
```text
test AUC of the junk model: 0.507 (chance)
mean |SHAP| (log-odds), real model vs junk model:
                      real model  model trained on shuffled labels
age                       0.0110                            0.0280
income                    0.3530                            0.0090
employment_years          0.0930                            0.0020
debt_ratio                0.2970                            0.0330
utilisation               0.5660                            0.0080
delinquencies             0.2590                            0.0000
credit_history_years      0.1350                            0.0160
inquiries                 0.0200                            0.0010
loan_amount               0.0300                            0.0040
region                    0.0250                            0.0140
total attribution mass: real 1.79 vs junk 0.12
```

**(3) Agreement across methods.** Compute two or three importance measures. Features that rank high in all of them can be reported with confidence; those where they disagree need a closer look (and a caveat in the report).

```python run
agree = pd.DataFrame({"SHAP": shap_imp.rank(ascending=False), "permutation": pi_gbm.rank(ascending=False), "|standardised logistic coefficient|": pd.Series(np.abs(logit_model[-1].coef_[0]), index=CORE).rank(ascending=False)}).loc[shap_imp.index]
print(agree.astype(int).to_string())
print("rank correlation SHAP vs logistic coefficients: %.2f; SHAP vs permutation: %.2f" % (stats.spearmanr(agree["SHAP"], agree.iloc[:, 2]).statistic, stats.spearmanr(agree["SHAP"], agree["permutation"]).statistic))
```
```text
                      SHAP  permutation  |standardised logistic coefficient|
utilisation              1            1                                    1
income                   2            2                                    2
debt_ratio               3            4                                    3
delinquencies            4            3                                    4
credit_history_years     5            5                                    6
employment_years         6           10                                    9
inquiries                7            6                                    8
loan_amount              8            8                                    5
region                   9            7                                    7
age                     10            9                                   10
rank correlation SHAP vs logistic coefficients: 0.85; SHAP vs permutation: 0.85
```

### 8.4 Try it

1. Repeat the deletion test with SHAP values from the *logistic regression*. Which model's top features matter more when removed?
2. Make the junk model stronger by using only 5% shuffled labels. At what level of shuffling do the attributions start to look like the real model's?


## 9. Communicating results to non-technical people

### 9.1 The best analysis is worth nothing if it is not understood

A model's value is realised only when someone **decides** differently because of it. That someone is usually not a data scientist, has five minutes, and cares about money, risk, people and deadlines, not about log-odds. Communication is therefore a core skill of the job and a technical one: it needs the same care about correctness as the code, because a wrong simplification misleads just as a bug does.

### 9.2 Know the reader

| Reader | What they need | What to leave out | Length |
|---|---|---|---|
| **Executive / sponsor** | the decision, its size in money or customers, the main risk, what you need from them | method, metrics names | one paragraph, one page at most |
| **Domain expert / analyst** | how it behaves, where it is strong and weak, how to use and monitor it | derivations | a few pages with tables |
| **Regulator / auditor** | data, method, validation, fairness, governance, documentation | marketing language | complete and traceable |
| **Affected person (customer)** | the decision, the main reasons, what they can do, how to appeal | any jargon | a short letter |
| **Engineer / peer** | reproducible detail: data versions, code, tests, limitations | persuasion | the repository and its README |

Before writing, answer in one sentence each: *Who is reading? What decision will they make? What do they already know? What is the one thing they must remember?*

### 9.3 Structure: answer first

Put the **conclusion and the request first**, then the evidence, then the caveats. Readers stop reading at any point, so whatever they have read so far should be the most important part.

```text
1. The answer       "We recommend approving applicants whose predicted risk is below 20%. This approves 81 of every 100 applicants, and about 7 in 100 of those approved default."
2. Why you can rely on it   the evidence, in numbers the reader can picture, with the uncertainty
3. How it decides   the top drivers, one example
4. Where it fails   limits, groups it serves worse, what could change
5. What we need     the decision, the owner, the next review date
```

A test for every sentence and every chart: **"so what?"** If it does not support the decision, it goes in an appendix.

### 9.4 Translating the numbers

Technical quantities mean nothing to most readers, and some are easily misread. Translate each into a statement about **people**, using **natural frequencies** ("out of 100").

**Probabilities become counts.** "A 20% probability of default" is abstract; "out of 100 borrowers like this one, about 20 are expected to default" is not. And the number should come with honest uncertainty, taken from how reliable the model's probabilities turned out to be (calibration, ds.04 section 11).

```python run
def wilson_interval(k, n, z=1.96):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half

def natural_frequency(p, n=100, lo=None, hi=None):
    if not 0 <= p <= 1: raise ValueError("p must be a probability")
    s = f"Out of {n} people like this, about {round(p * n)} are expected to default"
    if lo is not None and hi is not None:
        s += f" (somewhere between {round(lo * n)} and {round(hi * n)})"
    return s + "."

p_mono = gbm_mono.predict_proba(X_test[CORE])[:, 1]
band = (p_mono >= 0.15) & (p_mono < 0.25)
k_, n_ = int(y_test[band].sum()), int(band.sum())
lo, hi = wilson_interval(k_, n_)
print(f"test borrowers the model scored between 15% and 25%: {n_}; {k_} actually defaulted ({k_ / n_:.1%}; 95% interval {lo:.1%} to {hi:.1%})")
print(natural_frequency(float(p_mono[band].mean()), 100, lo, hi))
```
```text
test borrowers the model scored between 15% and 25%: 452; 82 actually defaulted (18.1%; 95% interval 14.9% to 22.0%)
Out of 100 people like this, about 19 are expected to default (somewhere between 15 and 22).
```

**AUC becomes a pairing game.** The AUC is the probability that a randomly chosen defaulter receives a higher risk score than a randomly chosen non-defaulter. You can say exactly that, and show it is true:

```python run
def auc_pairs(y_true, score):
    pos, neg = score[y_true == 1], score[y_true == 0]
    ranks = stats.rankdata(np.r_[pos, neg])
    return (ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))
rng = np.random.default_rng(0)
pos, neg = p_mono[y_test == 1], p_mono[y_test == 0]
sim = np.mean(rng.choice(pos, 200_000) > rng.choice(neg, 200_000))
print(f"AUC (scikit-learn) {metrics.roc_auc_score(y_test, p_mono):.4f} | pairwise formula {auc_pairs(y_test, p_mono):.4f} | simulated 200,000 random pairs {sim:.4f}")
print(f"In words: if we pick one borrower who defaulted and one who repaid at random, the model gives the defaulter the higher risk score about {round(auc_pairs(y_test, p_mono) * 100)} times out of 100 (a coin flip would be 50).")
```
```text
AUC (scikit-learn) 0.7927 | pairwise formula 0.7927 | simulated 200,000 random pairs 0.7949
In words: if we pick one borrower who defaulted and one who repaid at random, the model gives the defaulter the higher risk score about 79 times out of 100 (a coin flip would be 50).
```

**Relative versus absolute risk.** "Doubles your risk" and "raises your risk by 2 points" can describe the same facts and feel completely different. Give the absolute numbers, and the relative one only beside them.

```python run
def risk_statement(p0, p1, n=1000):
    return (f"risk goes from {p0:.1%} to {p1:.1%}: {round(p0 * n)} to {round(p1 * n)} people in {n}; that is {p1 / p0:.1f} times as high, "
            f"but {(p1 - p0) * 100:.1f} percentage points more")
print("rare event   :", risk_statement(0.004, 0.008))
print("common event:", risk_statement(0.20, 0.40))
```
```text
rare event   : risk goes from 0.4% to 0.8%: 4 to 8 people in 1000; that is 2.0 times as high, but 0.4 percentage points more
common event: risk goes from 20.0% to 40.0%: 200 to 400 people in 1000; that is 2.0 times as high, but 20.0 percentage points more
```

Both "double". Only one of them is a big deal in absolute terms. A reader told only "doubles" cannot tell.

**Classification results become a table of 1,000 people.** At a cutoff of 20% (approve when the predicted risk is below it), what happens to 1,000 applicants?

```python run
CUT = 0.20
approve = p_mono < CUT
n_t = len(y_test)
scale = 1000 / n_t
tbl = pd.DataFrame({
    "applicants": [1000, (approve.sum()) * scale, (~approve).sum() * scale],
    "of whom would default": [y_test.sum() * scale, y_test[approve].sum() * scale, y_test[~approve].sum() * scale],
}, index=["all applicants", "approved by the model", "declined by the model"]).round(0).astype(int)
print(tbl.to_string())
print(f"\napproved: {approve.mean():.0%} of applicants, and {y_test[approve].mean():.1%} of the approved default")
print(f"declined: {(~approve).mean():.0%} of applicants; {y_test[~approve].mean():.1%} of them would have defaulted, so {(1 - y_test[~approve].mean()):.0%} of declines turn away someone who would have repaid")
print(f"the model catches {(y_test[~approve].sum() / y_test.sum()):.0%} of all defaulters by declining them; the other {(y_test[approve].sum() / y_test.sum()):.0%} are approved")
```
```text
                       applicants  of whom would default
all applicants               1000                    139
approved by the model         808                     61
declined by the model         192                     78

approved: 81% of applicants, and 7.5% of the approved default
declined: 19% of applicants; 40.6% of them would have defaulted, so 59% of declines turn away someone who would have repaid
the model catches 56% of all defaulters by declining them; the other 44% are approved
```

Counts per 1,000 are the clearest form for non-specialists, and they show a trade the executive can price: how many good customers are turned away for each default avoided.

**Uncertainty is part of the message.** "The model's default rate among approved is 8.5%" is misleading precision. Give the interval, and say what it implies for the decision.

```python run
boot = []
rb = np.random.default_rng(1)
for _ in range(1000):
    i = rb.integers(0, n_t, n_t)
    a, yy = approve[i], y_test[i]
    boot.append(yy[a].mean())
print(f"default rate among approved: {y_test[approve].mean():.1%}, 95% bootstrap interval {np.quantile(boot, .025):.1%} to {np.quantile(boot, .975):.1%}")
print("say: 'about", round(y_test[approve].mean() * 100), "in 100 approved borrowers default (could be", round(np.quantile(boot, .025) * 100), "to", round(np.quantile(boot, .975) * 100), ")', not '8.5%'")
```
```text
default rate among approved: 7.5%, 95% bootstrap interval 6.6% to 8.5%
say: 'about 7 in 100 approved borrowers default (could be 7 to 8 )', not '8.5%'
```

### 9.5 Honest displays

A chart is an argument. These rules prevent the common ways of misleading, usually unintentionally. There is no screen here, so the habit is practised with tables and text charts.

| Rule | Why |
|---|---|
| **Bars start at zero** | a truncated bar exaggerates differences |
| **Same scale across panels you compare** | different axes make small things look big |
| **Show uncertainty** (intervals, ranges) | a difference inside the noise is not a difference |
| **Label units and the population** | "% of what?" is the commonest question |
| **Sort sensibly and label directly** | the reader should not need a legend lookup |
| **No dual axes, 3-D effects, or decorative colour** | they invite wrong readings |
| **Show the window you chose and why** | cherry-picked dates mislead |
| **One message per chart, stated in the title** | "Utilisation is the strongest driver of risk" beats "Feature importance" |
| **Never show a number you cannot defend** | a spurious third decimal damages credibility |

```python run
def text_bar(label_values, width=40, unit=""):
    top = max(abs(v) for _, v in label_values)
    for label, v in label_values:
        n = int(round(abs(v) / top * width))
        print(f"{label:24s} {'#' * n:<{width}s} {v:6.2f}{unit}")
print("What pushes a typical prediction (mean |SHAP|, log-odds), bars start at zero:")
text_bar([(k, v) for k, v in shap_imp.head(6).items()])
```
```text
What pushes a typical prediction (mean |SHAP|, log-odds), bars start at zero:
utilisation              ########################################   0.63
income                   #####################                      0.33
debt_ratio               ####################                       0.32
delinquencies            ##################                         0.28
credit_history_years     #########                                  0.14
employment_years         ######                                     0.09
```

### 9.6 One decision, three audiences

The same facts, told three ways. All come from the explanation of borrower `i_hi`.

```python run
phi_m, base_m, fx_m = shapley_exact(lambda A: gbm_mono.decision_function(A), x_hi, bg)
reasons = reason_codes(phi_m, 3)
p_applicant = sig(fx_m)
print("EXECUTIVE (two sentences):")
print(f"  The model rates this application very high-risk: its estimate is about {round(p_applicant * 100)} in 100, against {round(y_dev.mean() * 100)} in 100 overall (estimates this extreme are the least certain, but any reasonable error still means declining under the 20% policy).\n")
print("ANALYST (a paragraph with the numbers):")
print(f"  Predicted default probability {p_applicant:.1%} (base rate {sig(base_m):.1%}). The log-odds exceed the average by {fx_m - base_m:.2f}; the largest contributions are "
      + ", ".join(f"{n} ({ph:+.2f})" for n, _, ph in reasons) + ". The model is monotonic in these features; see the validation by risk band for calibration in this range.\n")
print("APPLICANT (a plain letter):")
print("  We are sorry that we cannot offer you this loan. The main reasons are: " + "; ".join(t for _, t, _ in reasons) + ".")
p0, best = counterfactual(gbm_mono, x_hi)
if best is not None:
    cost, combo, changes, p1 = best
    print("  What could change our decision: " + " and ".join(f"{('reducing your ' + c.replace('_', ' ')) } from {a:,.2f} to about {b:,.2f}" for c, (a, b) in changes.items()) + ".")
print("  You can ask us to review this decision or to explain it to you in person.")
```
```text
EXECUTIVE (two sentences):
  The model rates this application very high-risk: its estimate is about 97 in 100, against 14 in 100 overall (estimates this extreme are the least certain, but any reasonable error still means declining under the 20% policy).

ANALYST (a paragraph with the numbers):
  Predicted default probability 97.4% (base rate 8.3%). The log-odds exceed the average by 6.04; the largest contributions are utilisation (+2.87), debt_ratio (+1.07), delinquencies (+0.63). The model is monotonic in these features; see the validation by risk band for calibration in this range.

APPLICANT (a plain letter):
  We are sorry that we cannot offer you this loan. The main reasons are: you are using a high share of your available credit; your debts are high compared with your income; you have a history of missed payments.
  You can ask us to review this decision or to explain it to you in person.
```

Notice that nothing in the letter mentions a score, a model, a probability or a log-odds. And that every statement in it is backed by a number in the analyst's paragraph.

### 9.7 Limitations, and the model card

Say what the model **cannot** do and when it should **not** be used. A **model card** is a short, standard document that travels with the model:

| Section | Contents |
|---|---|
| **Intended use** | decision supported, population, who uses it, what it must not be used for |
| **Data** | source, period, size, known gaps, how the target is defined |
| **Method** | model type, constraints, features used and excluded |
| **Performance** | metrics at the operating point, with intervals, overall and by group |
| **Explanations** | how decisions are explained, with the caveats of section 8 |
| **Limits and risks** | known failure modes, drift, groups with worse performance |
| **Monitoring** | what is watched, thresholds that trigger review, owner, review date |
| **Contact and governance** | who approves changes, how to appeal |

```python run
model_card = {
    "name": "credit-default-risk v1 (boosted trees, monotonic constraints)",
    "intended_use": "rank applicants by 12-month default risk to support (not replace) a human underwriter; not for pricing, collections or employment decisions",
    "training_data": f"{len(X_dev):,} synthetic borrowers; default rate {y_dev.mean():.1%}; no data about people outside the lender's applicants",
    "features": CORE,
    "never_given_as_reasons": sorted(NOT_A_REASON),
    "performance": {"test_AUC": round(float(metrics.roc_auc_score(y_test, p_mono)), 3), "approval_rate_at_20pct": round(float(approve.mean()), 3), "default_rate_among_approved": round(float(y_test[approve].mean()), 3)},
    "known_limits": ["calibrated only inside the range of the training data", "performance by region differs (see the fairness table)", "assumes the economy resembles the training period"],
    "monitoring": "monthly: default rate by predicted-risk band; quarterly: PSI of the inputs; retrain trigger: calibration gap above 3 points",
}
print(json.dumps(model_card, indent=2))
```
```text
{
  "name": "credit-default-risk v1 (boosted trees, monotonic constraints)",
  "intended_use": "rank applicants by 12-month default risk to support (not replace) a human underwriter; not for pricing, collections or employment decisions",
  "training_data": "10,500 synthetic borrowers; default rate 13.9%; no data about people outside the lender's applicants",
  "features": [
    "age",
    "income",
    "employment_years",
    "debt_ratio",
    "utilisation",
    "delinquencies",
    "credit_history_years",
    "inquiries",
    "loan_amount",
    "region"
  ],
  "never_given_as_reasons": [
    "age",
    "region"
  ],
  "performance": {
    "test_AUC": 0.793,
    "approval_rate_at_20pct": 0.808,
    "default_rate_among_approved": 0.075
  },
  "known_limits": [
    "calibrated only inside the range of the training data",
    "performance by region differs (see the fairness table)",
    "assumes the economy resembles the training period"
  ],
  "monitoring": "monthly: default rate by predicted-risk band; quarterly: PSI of the inputs; retrain trigger: calibration gap above 3 points"
}
```

### 9.8 A checklist before sending anything

1. Does the **first sentence** state the conclusion or the request?
2. Could someone who did not attend the analysis follow it?
3. Is every number accompanied by its **unit, population and uncertainty**?
4. Are **absolute** numbers given next to every relative one?
5. Is each chart's title its **message**, and does it start at zero where it should?
6. Have you said what the model **cannot** do?
7. Does each statement survive the question **"how do you know?"**
8. Is there exactly one **recommended action**, with an owner and a date?

### 9.9 Try it

1. Rewrite the executive paragraph for a borrower who was **approved** with a 3% predicted risk, in two sentences.
2. Take any metric from a model you built earlier in this course and write its natural-frequency translation for a non-specialist.

## 10. Fairness and responsible use, briefly

### 10.1 Why this belongs in an explanation chapter

Explaining a model includes asking **who it works for**. A model can score well overall and fail systematically for a group, and it can use a stand-in (a **proxy**) for something it is not allowed to use. Here `region` is an input and is correlated with income, which is a legitimate feature, so even a model without `region` would treat regions differently.

### 10.2 Check performance by group

```python run
REGION = {0: "Region A", 1: "Region B", 2: "Region C", 3: "Region D"}
def group_table(model_p, groups, y, cut=CUT):
    rows = []
    for g in sorted(np.unique(groups)):
        m = groups == g
        ap = model_p[m] < cut
        rows.append((REGION[g], int(m.sum()), ap.mean(), y[m][ap].mean(), (~ap)[y[m] == 0].mean(), (ap)[y[m] == 1].mean(), model_p[m].mean(), y[m].mean()))
    return pd.DataFrame(rows, columns=["group", "applicants", "approval rate", "default rate among approved", "good applicants wrongly declined", "defaulters approved", "mean predicted risk", "actual default rate"]).set_index("group")
print(group_table(p_mono, X_test["region"].to_numpy(), y_test).round(3).to_string())
```
```text
          applicants  approval rate  default rate among approved  good applicants wrongly declined  defaulters approved  mean predicted risk  actual default rate
group                                                                                                                                                            
Region A        1206         0.8510                       0.0700                            0.1010               0.4970               0.1200               0.1200
Region B        1085         0.8100                       0.0800                            0.1330               0.4610               0.1360               0.1400
Region C         710         0.7920                       0.0870                            0.1520               0.4670               0.1480               0.1480
Region D         499         0.7210                       0.0580                            0.1850               0.2530               0.1790               0.1660
```

Read each column as a different kind of fairness:

| Column | Criterion it speaks to |
|---|---|
| approval rate | **demographic parity**: do groups get approved at similar rates? |
| good applicants wrongly declined | **equal opportunity**: do equally creditworthy people get declined equally often? |
| defaulters approved | the matching error on the other side |
| mean predicted vs actual risk | **calibration within groups**: do predictions mean the same thing for each group? |

When base rates differ between groups, these criteria cannot all be satisfied at once (a mathematical fact, not a technical shortcoming). Choosing among them is a **policy decision** for the organisation and its regulator, to be made openly and recorded; the data scientist's job is to measure, show the trade-off and flag it.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Make a grouped bar chart comparing four regions for a credit model. Groups: Region A, B, C, D. Bars per group: approval rate (0.851, 0.810, 0.792, 0.721) and good applicants wrongly declined (0.101, 0.133, 0.152, 0.185). Label axes and add a note that approval rate relates to demographic parity and wrongly declined good applicants relates to equal opportunity."

### 10.3 Dropping the sensitive column is not enough

```python run
CORE_NR = [c for c in CORE if c != "region"]
cst_nr = [mono.get(c, 0) for c in CORE_NR]
gbm_nr = ensemble.HistGradientBoostingClassifier(max_iter=250, learning_rate=0.06, max_depth=4, min_samples_leaf=40, monotonic_cst=cst_nr, random_state=0).fit(X_dev[CORE_NR], y_dev)
p_nr = gbm_nr.predict_proba(X_test[CORE_NR])[:, 1]
cmp = pd.DataFrame({"approval rate (with region)": group_table(p_mono, X_test["region"].to_numpy(), y_test)["approval rate"],
                    "approval rate (region removed)": group_table(p_nr, X_test["region"].to_numpy(), y_test)["approval rate"]})
print(cmp.round(3).to_string())
print("test AUC with region %.4f, without %.4f" % (metrics.roc_auc_score(y_test, p_mono), metrics.roc_auc_score(y_test, p_nr)))
```
```text
          approval rate (with region)  approval rate (region removed)
group                                                                
Region A                       0.8510                          0.8420
Region B                       0.8100                          0.8060
Region C                       0.7920                          0.8100
Region D                       0.7210                          0.7330
test AUC with region 0.7927, without 0.7924
```

Removing `region` hardly moves the approval gaps, because income, debt and loan size carry the regional pattern. Fairness has to be measured on **outcomes by group**, not assumed from the list of inputs.

### 10.4 Responsible-use habits

1. State the intended use, and refuse out-of-scope uses.
2. Measure by group, with intervals; keep a record of what you chose and why.
3. Keep a human in the loop for consequential decisions, with a way to contest them.
4. Monitor after launch; retrain with attention to feedback loops (declined applicants never produce outcome data).
5. Treat explanations as aids to scrutiny, not as proof of fairness.

## 11. Project: an explainable credit-risk model report

### 11.1 The brief

The head of credit risk wants to adopt the boosted default model, on three conditions: she must be able to **explain every decision** to the applicant, the model must **respect obvious credit logic**, and she needs a **one-page report** she can show the board. You will:

1. Build a small, **tested explanation toolkit**, `explain_toolkit`: exact and sampled Shapley values, reason codes, counterfactual recourse, and plain-language translators.
2. Use it to produce, **from code**, the report for the board: no number in the report is typed by hand.
3. Include the checks of section 8 so the report states what the explanations can and cannot support.

### 11.2 The toolkit

```python run
import pathlib, tempfile, subprocess, os
proj = pathlib.Path(tempfile.mkdtemp()) / "explain_project"
proj.mkdir()
(proj / "explain_toolkit.py").write_text('''"""explain_toolkit: Shapley values, reason codes, counterfactuals and plain-language helpers."""
import itertools
import math
import numpy as np
from scipy import stats


# ---------- Shapley values (interventional, on whatever scale f returns) ----------
def shapley_exact(f, x, background):
    """Exact Shapley values by enumerating all 2^d coalitions. Returns (phi, base_value, f_at_x)."""
    x, B = np.asarray(x, float), np.asarray(background, float)
    d = len(x); M = 1 << d
    subsets = np.arange(M)
    mask = ((subsets[:, None] >> np.arange(d)) & 1).astype(bool)
    Z = np.where(mask[:, None, :], x[None, None, :], B[None, :, :])
    v = np.asarray(f(Z.reshape(-1, d))).reshape(M, len(B)).mean(1)
    size = mask.sum(1)
    w = np.array([math.factorial(s) * math.factorial(d - s - 1) / math.factorial(d) for s in range(d)])
    phi = np.zeros(d)
    for i in range(d):
        without = subsets[~mask[:, i]]
        phi[i] = np.sum(w[size[without]] * (v[without | (1 << i)] - v[without]))
    return phi, float(v[0]), float(v[M - 1])


def shapley_sampling(f, x, background, m=2000, seed=0):
    """Unbiased permutation-sampling estimate of the same values; cost m*(d+1) evaluations."""
    r = np.random.default_rng(seed)
    x, B = np.asarray(x, float), np.asarray(background, float)
    d = len(x)
    z = B[r.integers(len(B), size=m)]
    perms = np.argsort(r.random((m, d)), axis=1)
    pts = np.repeat(z[:, None, :], d + 1, axis=1)
    for k in range(1, d + 1):
        for j in range(k):
            pts[np.arange(m), k, perms[:, j]] = x[perms[:, j]]
    vals = np.asarray(f(pts.reshape(-1, d))).reshape(m, d + 1)
    phi = np.zeros(d)
    np.add.at(phi, perms.ravel(), (vals[:, 1:] - vals[:, :-1]).ravel())
    return phi / m


# ---------- reason codes ----------
def reason_codes(phi, names, texts, forbidden=(), k=3):
    """The k largest risk-INCREASING contributions among permitted features, as (name, plain text, contribution)."""
    out = []
    for i in np.argsort(-np.asarray(phi)):
        if phi[i] <= 0:
            break
        if names[i] in forbidden or names[i] not in texts:
            continue
        out.append((names[i], texts[names[i]], float(phi[i])))
        if len(out) == k:
            break
    return out


# ---------- counterfactual recourse ----------
def counterfactual(predict_proba, x, names, actionable, cutoff, scale, steps=11, max_features=3):
    """Smallest change (in standard deviations) to ACTIONABLE features, lowering them only, that brings the probability below the cutoff.
    actionable: {name: lowest allowed value}. Returns (current probability, best) where best = (cost, {name: (old, new)}, new probability) or None."""
    x = np.asarray(x, float)
    p0 = float(predict_proba(x[None, :])[0])
    if p0 < cutoff:
        return p0, None
    cands = [n for n in actionable if n in names]
    grids = {n: np.linspace(x[names.index(n)], min(x[names.index(n)], actionable[n]), steps)[1:] for n in cands}
    for k in range(1, max_features + 1):
        best = None
        for combo in itertools.combinations(cands, k):
            for vals in itertools.product(*[grids[c] for c in combo]):
                z = x.copy()
                for c, v in zip(combo, vals):
                    z[names.index(c)] = v
                p = float(predict_proba(z[None, :])[0])
                if p < cutoff:
                    cost = sum(abs(z[names.index(c)] - x[names.index(c)]) / scale[names.index(c)] for c in combo)
                    if best is None or cost < best[0]:
                        best = (cost, {c: (x[names.index(c)], z[names.index(c)]) for c in combo}, p)
        if best is not None:
            return p0, best
    return p0, None


# ---------- plain-language helpers ----------
def wilson_interval(k, n, z=1.96):
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def natural_frequency(p, n=100, lo=None, hi=None):
    if not 0 <= p <= 1:
        raise ValueError("p must be a probability between 0 and 1")
    s = f"Out of {n} people like this, about {round(p * n)} are expected to default"
    if lo is not None and hi is not None:
        s += f" (somewhere between {round(lo * n)} and {round(hi * n)})"
    return s + "."


def auc_pairs(y_true, score):
    """Share of (defaulter, non-defaulter) pairs in which the defaulter has the higher score: the AUC, exactly."""
    y_true, score = np.asarray(y_true), np.asarray(score)
    pos, neg = score[y_true == 1], score[y_true == 0]
    ranks = stats.rankdata(np.r_[pos, neg])
    return float((ranks[: len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))
''', encoding="utf-8")
print("explain_toolkit.py:", len((proj / "explain_toolkit.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
explain_toolkit.py: 107 lines
```

### 11.3 The tests

Each test guards a property that makes an explanation trustworthy.

```python run
(proj / "test_explain_toolkit.py").write_text('''import math
import numpy as np, pytest
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
import explain_toolkit as ex

rng = np.random.default_rng(0)
B = rng.normal(size=(60, 4))
X0 = rng.normal(size=4)

def nonlinear(A):
    A = np.atleast_2d(A)
    return np.sin(A[:, 0]) + A[:, 1] * A[:, 2] + 0.5 * A[:, 0] ** 2          # feature 3 is never used

def test_efficiency_the_contributions_add_up_to_prediction_minus_base():
    phi, base, fx = ex.shapley_exact(nonlinear, X0, B)
    assert phi.sum() + base == pytest.approx(fx, abs=1e-9), "Shapley values must add up to f(x) minus the base value"

def test_a_feature_the_model_never_uses_gets_zero():
    phi, _, _ = ex.shapley_exact(nonlinear, X0, B)
    assert phi[3] == pytest.approx(0, abs=1e-12), "the dummy property: an unused feature must receive no credit"

def test_linear_models_match_the_closed_form():
    w = np.array([2.0, -1.0, 0.5, 3.0])
    f = lambda A: np.atleast_2d(A) @ w + 1.0
    phi, _, _ = ex.shapley_exact(f, X0, B)
    assert np.allclose(phi, w * (X0 - B.mean(0)), atol=1e-10), "for a linear model phi_j = w_j (x_j - mean of the background)"

def test_symmetric_features_receive_equal_credit():
    f = lambda A: np.atleast_2d(A)[:, 0] * np.atleast_2d(A)[:, 1]
    x = np.array([2.0, 2.0, 0.0, 0.0])
    B_sym = B.copy(); B_sym[:, 1] = B_sym[:, 0]                              # symmetry is a property of the whole game: the background must treat the two features alike too
    phi, _, _ = ex.shapley_exact(f, x, B_sym)
    assert phi[0] == pytest.approx(phi[1]), "an interaction between two interchangeable features is shared equally"

def test_sampling_converges_to_exact():
    phi, _, _ = ex.shapley_exact(nonlinear, X0, B)
    approx = ex.shapley_sampling(nonlinear, X0, B, m=20000, seed=1)
    assert np.max(np.abs(approx - phi)) < 0.05

def test_reason_codes_only_use_permitted_risk_increasing_features():
    names = ["utilisation", "age", "income", "debt_ratio"]
    texts = {"utilisation": "high use of credit", "income": "low income", "debt_ratio": "high debt", "age": "age"}
    out = ex.reason_codes(np.array([0.9, 1.5, -0.4, 0.3]), names, texts, forbidden=("age",), k=3)
    assert [n for n, _, _ in out] == ["utilisation", "debt_ratio"], "age is forbidden and income lowers the risk, so neither may appear"

def test_counterfactual_crosses_the_cutoff_and_touches_only_actionable_features():
    X = rng.normal(size=(400, 3)); y = (X[:, 0] + 0.5 * X[:, 1] + rng.normal(0, 0.5, 400) > 0.5).astype(int)
    clf = LogisticRegression().fit(X, y)
    pp = lambda A: clf.predict_proba(A)[:, 1]
    x = np.array([2.0, 1.0, 0.7]); names = ["a", "b", "c"]
    p0, best = ex.counterfactual(pp, x, names, {"a": -1.0, "b": -1.0}, cutoff=0.5, scale=np.ones(3))
    assert p0 > 0.5 and best is not None
    cost, changes, p1 = best
    assert p1 < 0.5, "the proposed change must really bring the probability below the cutoff"
    assert set(changes) <= {"a", "b"}, "feature c is not actionable and must not be changed"
    assert all(new < old for old, new in changes.values()), "actionable features are only lowered"

def test_counterfactual_returns_nothing_for_an_already_approved_applicant():
    clf = LogisticRegression().fit(rng.normal(size=(100, 2)), rng.integers(0, 2, 100))
    p0, best = ex.counterfactual(lambda A: np.full(len(A), 0.05), np.array([0.0, 0.0]), ["a", "b"], {"a": -1.0}, cutoff=0.2, scale=np.ones(2))
    assert best is None

def test_natural_frequency_wording_and_validation():
    assert ex.natural_frequency(0.2, 100, 0.17, 0.24) == "Out of 100 people like this, about 20 are expected to default (somewhere between 17 and 24)."
    with pytest.raises(ValueError):
        ex.natural_frequency(1.2)

def test_the_pairwise_auc_equals_scikit_learn():
    y = rng.integers(0, 2, 500); s = rng.normal(size=500) + y
    assert ex.auc_pairs(y, s) == pytest.approx(roc_auc_score(y, s))
''', encoding="utf-8")
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "test_explain_toolkit.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-800:] or res.stderr.strip()[-800:])
```
```text
..........                                                               [100%]
10 passed in 0.97s
```

### 11.4 The report, generated from code

Every sentence below is assembled from computed numbers, so rerunning the project on a retrained model rewrites the report. The model is the **monotonic boosted model**; the explanations come from the toolkit.

```python run
sys.path.insert(0, str(proj))
import importlib, explain_toolkit as xt
importlib.reload(xt)

f_final = lambda A: gbm_mono.decision_function(A)
proba_final = lambda A: gbm_mono.predict_proba(pd.DataFrame(A, columns=CORE))[:, 1]
bg_final = X_dev[CORE].sample(100, random_state=5).to_numpy()
rep_idx = np.random.default_rng(7).choice(len(X_test), 100, replace=False)
PHI_final = np.array([xt.shapley_exact(f_final, x, bg_final)[0] for x in X_test[CORE].iloc[rep_idx].to_numpy()])
drivers = pd.Series(np.abs(PHI_final).mean(0), index=CORE).sort_values(ascending=False)

# example applicants: one clearly approved, one near the cutoff, one clearly declined
p_all = p_mono
i_ok = int(np.argmin(np.abs(p_all - 0.04))); i_edge = int(np.argmin(np.abs(p_all - CUT))); i_no = int(np.argmin(np.abs(p_all - 0.55)))
scale_vec = X_dev[CORE].std().to_numpy()
floors = {"utilisation": 0.05, "debt_ratio": 0.05, "loan_amount": None}

def example(i):
    x = X_test[CORE].iloc[i].to_numpy()
    phi, base, fx = xt.shapley_exact(f_final, x, bg_final)
    fl = {"utilisation": 0.05, "debt_ratio": 0.05, "loan_amount": 0.3 * x[CORE.index("loan_amount")]}
    p0, best = xt.counterfactual(proba_final, x, CORE, fl, CUT, scale_vec)
    return {"p": sig(fx), "reasons": xt.reason_codes(phi, CORE, REASON_TEXT, forbidden=NOT_A_REASON, k=3), "recourse": best}

ex_rows = {"approved": example(i_ok), "borderline": example(i_edge), "declined": example(i_no)}
auc_text = round(xt.auc_pairs(y_test, p_mono) * 100)
grp = group_table(p_mono, X_test["region"].to_numpy(), y_test)
worst_decl = grp["good applicants wrongly declined"].idxmax(); best_decl = grp["good applicants wrongly declined"].idxmin()
lo_b, hi_b = np.quantile(boot, [.025, .975])

lines = []
A = lines.append
A("CREDIT-RISK MODEL: REPORT FOR THE CREDIT COMMITTEE")
A("=" * 56)
A(f"1. Recommendation\n   Use the model to approve applicants whose predicted risk of default is below {CUT:.0%}, with a human underwriter reviewing the borderline cases.")
A(f"   On last period's applicants this approves {approve.mean():.0%} of them. About {round(y_test[approve].mean() * 100)} in 100 of those approved would default (plausibly {round(lo_b * 100)} to {round(hi_b * 100)}), against {round(y_test.mean() * 100)} in 100 of all applicants.")
A("2. What it achieves, per 1,000 applicants")
A(f"   Approved {int(round(approve.sum() * scale))}; declined {int(round((~approve).sum() * scale))}. Of the declined, {int(round(y_test[~approve].sum() * scale))} would have defaulted and {int(round((1 - y_test[~approve]).sum() * scale))} would have repaid.")
A(f"   The model catches {y_test[~approve].sum() / y_test.sum():.0%} of defaulters by declining them. Each avoided default costs about {(1 - y_test[~approve].mean()) / y_test[~approve].mean():.1f} good customers turned away.")
A(f"   Ranking quality: if we pick one defaulter and one repayer at random, the model scores the defaulter as riskier about {auc_text} times in 100.")
A("3. What drives the decisions (largest average effect first)")
for k_name, v in drivers.head(5).items():
    A(f"   - {REASON_TEXT.get(k_name, k_name)}  [{k_name}]   typical push on the odds of default: x{math.exp(v):.2f}")
A("   The model follows credit logic: more missed payments, more debt or higher credit use never lower a score; higher income or a longer history never raise it (verified; see appendix).")
A("4. Three applicants")
for name, e in ex_rows.items():
    why = "; ".join(t for _, t, _ in e["reasons"]) or "no factor stands out as raising the risk"
    A(f"   {name.upper():10s}: predicted default risk {e['p']:.0%} ({'approve' if e['p'] < CUT else 'decline'}). Main risk factors: {why}.")
    if e["recourse"] is not None:
        cost, changes, p1 = e["recourse"]
        A("      Smallest change that would flip the decision: " + " and ".join(f"{c.replace('_', ' ')} {a:,.2f} -> {b:,.2f}" for c, (a, b) in changes.items()) + f" (new risk {p1:.0%}).")
A("5. Fairness check by region")
A(f"   Good applicants wrongly declined range from {grp['good applicants wrongly declined'].min():.1%} ({best_decl}) to {grp['good applicants wrongly declined'].max():.1%} ({worst_decl}); approval rates range from {grp['approval rate'].min():.0%} to {grp['approval rate'].max():.0%}.")
A("   Removing the region input does not close the gap, because income and debt carry the regional pattern. Recommendation: review the cutoff by region with the compliance team before launch.")
A("6. What this model cannot do")
A("   It describes how risk relates to the borrower's data, not what would cause a borrower to default. Reasons given to applicants are the model's main risk factors, not proof of cause. It has not been tested on people who were never applicants. It must be re-checked if the economy changes.")
A("7. Needed from the committee")
A("   (a) approve the 20% cutoff or choose another from the table in the appendix; (b) decide the fairness question in section 5; (c) appoint an owner for the monthly monitoring described in the model card.")
print("\n".join(lines))
```
```text
CREDIT-RISK MODEL: REPORT FOR THE CREDIT COMMITTEE
========================================================
1. Recommendation
   Use the model to approve applicants whose predicted risk of default is below 20%, with a human underwriter reviewing the borderline cases.
   On last period's applicants this approves 81% of them. About 7 in 100 of those approved would default (plausibly 7 to 8), against 14 in 100 of all applicants.
2. What it achieves, per 1,000 applicants
   Approved 808; declined 192. Of the declined, 78 would have defaulted and 114 would have repaid.
   The model catches 56% of defaulters by declining them. Each avoided default costs about 1.5 good customers turned away.
   Ranking quality: if we pick one defaulter and one repayer at random, the model scores the defaulter as riskier about 79 times in 100.
3. What drives the decisions (largest average effect first)
   - you are using a high share of your available credit  [utilisation]   typical push on the odds of default: x1.92
   - your income is low for the amount you want to borrow  [income]   typical push on the odds of default: x1.50
   - your debts are high compared with your income  [debt_ratio]   typical push on the odds of default: x1.39
   - you have a history of missed payments  [delinquencies]   typical push on the odds of default: x1.36
   - your credit history is short  [credit_history_years]   typical push on the odds of default: x1.16
   The model follows credit logic: more missed payments, more debt or higher credit use never lower a score; higher income or a longer history never raise it (verified; see appendix).
4. Three applicants
   APPROVED  : predicted default risk 4% (approve). Main risk factors: your income is low for the amount you want to borrow.
   BORDERLINE: predicted default risk 20% (decline). Main risk factors: you are using a high share of your available credit; you have a history of missed payments; your income is low for the amount you want to borrow.
      Smallest change that would flip the decision: utilisation 0.54 -> 0.50 (new risk 13%).
   DECLINED  : predicted default risk 55% (decline). Main risk factors: you are using a high share of your available credit; your income is low for the amount you want to borrow; your debts are high compared with your income.
      Smallest change that would flip the decision: utilisation 0.69 -> 0.37 (new risk 14%).
5. Fairness check by region
   Good applicants wrongly declined range from 10.1% (Region A) to 18.5% (Region D); approval rates range from 72% to 85%.
   Removing the region input does not close the gap, because income and debt carry the regional pattern. Recommendation: review the cutoff by region with the compliance team before launch.
6. What this model cannot do
   It describes how risk relates to the borrower's data, not what would cause a borrower to default. Reasons given to applicants are the model's main risk factors, not proof of cause. It has not been tested on people who were never applicants. It must be re-checked if the economy changes.
7. Needed from the committee
   (a) approve the 20% cutoff or choose another from the table in the appendix; (b) decide the fairness question in section 5; (c) appoint an owner for the monthly monitoring described in the model card.
```

### 11.5 Appendix checks that stand behind the report

```python run
viol_delq = violations(gbm_mono, 'delinquencies', g, X_test[CORE]); viol_inc = violations(gbm_mono, 'income', gi, X_test[CORE], direction=-1)
print(f"monotonicity: borrowers with a wrong-direction response  delinquencies {viol_delq:.1%}, income {viol_inc:.1%}")
sample_phi = PHI_final[:40]
print(f"explanations add up to the prediction (efficiency): {bool(np.allclose(sample_phi.sum(1) + xt.shapley_exact(f_final, X_test[CORE].iloc[rep_idx[0]].to_numpy(), bg_final)[1], f_final(X_test[CORE].iloc[rep_idx[:40]].to_numpy()), atol=1e-6))}")
top_ = deletion_curve(f_final, X_test[CORE].iloc[rep_idx[:40]].to_numpy(), PHI_final[:40], bg_final.mean(0), "top", 3)
bot_ = deletion_curve(f_final, X_test[CORE].iloc[rep_idx[:40]].to_numpy(), PHI_final[:40], bg_final.mean(0), "bottom", 3)
print("faithfulness (mean |change| in log-odds after replacing k features by the average): top-attributed", np.round(top_, 2), "vs least-attributed", np.round(bot_, 2))
cut_table = pd.DataFrame({"cutoff": [0.10, 0.15, 0.20, 0.30]})
cut_table["approval rate"] = [float((p_mono < c).mean()) for c in cut_table["cutoff"]]
cut_table["default rate among approved"] = [float(y_test[p_mono < c].mean()) for c in cut_table["cutoff"]]
cut_table["good applicants declined (per 1,000)"] = [float(((p_mono >= c) & (y_test == 0)).sum() / len(y_test) * 1000) for c in cut_table["cutoff"]]
print(cut_table.round(3).to_string(index=False))
```
```text
monotonicity: borrowers with a wrong-direction response  delinquencies 0.0%, income 0.0%
explanations add up to the prediction (efficiency): True
faithfulness (mean |change| in log-odds after replacing k features by the average): top-attributed [0.   0.75 0.8  0.92] vs least-attributed [0.   0.01 0.03 0.06]
 cutoff  approval rate  default rate among approved  good applicants declined (per 1,000)
 0.1000         0.5820                       0.0540                              311.1430
 0.1500         0.7260                       0.0650                              182.5710
 0.2000         0.8080                       0.0750                              114.2860
 0.3000         0.8900                       0.0910                               51.7140
```

### 11.6 What to hand in

1. `explain_toolkit.py` and `test_explain_toolkit.py`, all tests passing.
2. The report, generated by code, for **two different cutoffs**; compare how the message changes.
3. A one-page **model card** for the model, from the template in 9.7.
4. A paragraph for the applicant who was declined, and one for the board, from the same facts.
5. A list of the three ways your explanations could be wrong, with the check you ran for each.

### 11.7 Extensions

1. Add `shap`-based explanations (on your machine) and compare with the toolkit's exact values on the same borrowers.
2. Add a **stability test**: retrain with different seeds and report how often the top-3 reasons for a declined applicant change.
3. Extend `counterfactual` with costs per feature (a missed payment cannot be undone, utilisation can be lowered in a month) and with plausibility (only suggest values observed in real borrowers).
4. Write the monitoring plan: which statistics, which thresholds, who is alerted, when the model is retrained or withdrawn.
5. Present the report to a friend who has never studied statistics. Note which sentences they ask you to repeat, and rewrite them.

## 12. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Treating impurity importance as truth | noise and high-cardinality columns look important | permutation importance on held-out data (4) |
| Permuting one of two correlated features | both look unimportant | group them (4.3) |
| Reading one importance number as "the" importance | methods answer different questions | compare several; explain the question each answers (4.5) |
| A PDP as the whole story | interactions hidden by the average | ICE and splits by the interacting feature (5.2) |
| PDP with correlated features | impossible feature combinations | ALE, and say which you show (5.3) |
| Calling a feature "unimportant" because the model ignores it | a near-copy takes the credit | merge or sum duplicates (5.3, 6.8b) |
| SHAP without a background | the baseline is undefined | state the background and choose it for the question (6.8a) |
| Adding SHAP values on the probability scale | they add on the log-odds scale | report on log-odds, or say "multiplies the odds by" (6.5) |
| SHAP read as causal | advice that does not work in the world | attributions describe the model (6.8c, 8.2) |
| Trusting an approximate explainer without a check | unfaithful attributions | deletion test, shuffled-label test (8.3) |
| One LIME run | unstable explanation | repeat, vary the kernel, or use exact values (7.2) |
| Reasons that cite protected or incomprehensible features | legal and trust problems | permitted list with plain-language text (7.3) |
| Recourse that is impossible, implausible or unstable | advice that cannot be followed | actionable, bounded, plausible changes only (7.4) |
| A surrogate without its fidelity | tidy rules that are wrong a third of the time | always report R-squared (8.1) |
| Leading with method | the reader stops before the answer | answer first (9.3) |
| Jargon and bare probabilities | the message is lost | natural frequencies, pairs, plain words (9.4) |
| Relative risk alone | small risks look huge | give absolute numbers beside it (9.4) |
| False precision | credibility lost when it fails | intervals and rounded numbers (9.4) |
| Misleading charts | wrong conclusions | zero baselines, uncertainty, one message (9.5) |
| Assuming fairness from the list of inputs | proxies carry the effect | measure outcomes by group (10) |
| An explanation that is a story | persuasive and untested | state what it cannot show; run the sanity checks (8) |

## 13. Summary

- **Why explain**: debugging, trust, recourse, compliance, fairness, insight. Different readers need different explanations. Scope is global or local; methods are model-specific or model-agnostic; models are interpretable by design or explained after the fact. **Try the interpretable model first**; here the logistic regression matched the boosted model's AUC.
- **Readable models**: logistic coefficients and odds ratios (association, not cause; unstable under correlation), shallow trees, and **monotonic constraints** that remove contradictions of credit logic (14% and 38% of borrowers moved the wrong way before; 0% after) at no cost in accuracy.
- **Global importance**: impurity importance is biased (noise got the credit of real features); **permutation importance on held-out data** is honest but splits credit among correlated features (group them); drop-column importance asks whether information is needed. They answer different questions.
- **Effect plots**: partial dependence (average), **ICE** (individual curves, reveals interactions), **ALE** (safer with correlated features). Explanations describe the **model**: of two near-identical features, the model used one and the plots gave the other nothing.
- **Shapley values**: fair credit by averaging marginal contributions over all feature orderings, defined against a **background**. Efficiency, symmetry, dummy and additivity hold; we implemented exact enumeration (checked against a hand example and the linear closed form) and unbiased sampling (error ~ 1/sqrt(m)). Importance by mean |SHAP|; dependence tables show non-linearity and interactions.
- **SHAP's limits**: depends on the background; the split between correlated features is arbitrary (the sum is stable); not causal; additive summaries hide interactions; approximations need checking; log-odds do not add on the probability scale.
- **Local explanations**: LIME-style surrogates are unstable across seeds and kernels; **reason codes** turn the largest risk-raising attributions into permitted plain-language reasons; **counterfactuals** find the smallest actionable change that flips the decision, with five caveats (causal, actionable, plausible, stable, gaming).
- **Sanity checks**: a global surrogate with its fidelity, the deletion (faithfulness) test, the shuffled-label (model randomisation) test, and agreement across methods.
- **Communication**: know the reader; **answer first**; translate probabilities to natural frequencies with uncertainty, AUC to a pairing game, relative to absolute risk, classification results to counts per 1,000; honest displays; one decision told three ways; limits and a **model card**; a checklist.
- **Fairness in brief**: measure by group (approval, wrongly declined, calibration), accept that criteria conflict when base rates differ, and remember that dropping a sensitive column does not remove its proxies.
- **The project** produced a toolkit with ten tests that encode the properties explanations must have, and a board report generated entirely from code, with the checks that stand behind it.

You reached the outcome of this chapter: you can **explain a model's prediction to a non-technical reader**, as a two-sentence verdict, as an analyst's paragraph, and as a plain letter to the person affected, each backed by the same exact numbers. This completes the data-science track; ml.01 begins the deep-learning track.
