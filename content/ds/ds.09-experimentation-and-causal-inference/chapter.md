# Chapter 9 (DS): Experimentation and causal inference

A model can tell you that customers who use a feature spend more. It cannot tell you that **launching** the feature will make them spend more, because the customers who choose the feature may simply be the keener ones. That gap, between *predicting* what happens and knowing what *causes* it, is the subject of this chapter. It is also where a data scientist's work meets money: whether to roll out a redesign, a price, a recommendation algorithm (the offline evaluation of ds.08 can only prepare for that decision).

The best tool for a causal question is a **randomised controlled experiment**, called an A/B test when it compares two versions. This chapter teaches it properly: how to design one (what to measure, how to split users, how many you need), how to analyse it (tests, intervals, variance reduction), and, above all, how it goes wrong in practice: looking at the results every day until they turn significant (**peeking**), testing twenty metrics and reporting the one that worked (**multiple testing**), a broken split that silently biases everything (**sample-ratio mismatch**). Then it turns to what to do when you cannot randomise: **causal inference** from observational data, with its assumptions, its tools (adjustment, propensity scores, difference-in-differences) and its limits.

By the end you reach the outcome of the syllabus: **size an experiment and analyse it without peeking errors.** The project analyses a simulated product experiment, with traps planted in it, and ends in a decision memo.

Prerequisites: ds.02 (hypothesis tests, confidence intervals, p-values), ds.01 (probability, the bootstrap), ds.04 (leakage, honest evaluation). Every formula in this chapter is implemented and checked against a library.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, pandas, SciPy and statsmodels. All data are **simulated with a known truth** (a true effect we planted), which is the only way to see whether a method works: with real data you never know the right answer. Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, json, hashlib, warnings, platform
import numpy as np
import pandas as pd
import scipy
import statsmodels
from scipy import stats
from statsmodels.stats.power import NormalIndPower, TTestIndPower
from statsmodels.stats.proportion import proportions_ztest, confint_proportions_2indep, proportion_effectsize
from statsmodels.stats.multitest import multipletests
import statsmodels.api as sm

np.set_printoptions(precision=4, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
warnings.filterwarnings("ignore")
print("python     ", sys.version.split()[0])
print("numpy      ", np.__version__)
print("scipy      ", scipy.__version__)
print("pandas     ", pd.__version__)
print("statsmodels", statsmodels.__version__)
```
```text
python      3.14.4
numpy       2.5.4
scipy       1.18.1
pandas      3.1.1
statsmodels 0.15.0
```

## Table of contents

1. [Why randomise: correlation, confounding and potential outcomes](#1-why-randomise-correlation-confounding-and-potential-outcomes)
2. [Anatomy of an A/B test](#2-anatomy-of-an-ab-test)
3. [Analysing a test: proportions and means](#3-analysing-a-test-proportions-and-means)
4. [Power, minimum detectable effect and sample size](#4-power-minimum-detectable-effect-and-sample-size)
5. [Variance reduction and awkward metrics](#5-variance-reduction-and-awkward-metrics)
6. [Is the experiment trustworthy? Sample ratio mismatch and A/A tests](#6-is-the-experiment-trustworthy-sample-ratio-mismatch-and-aa-tests)
7. [Multiple testing](#7-multiple-testing)
8. [Peeking and sequential testing](#8-peeking-and-sequential-testing)
9. [A Bayesian view, briefly](#9-a-bayesian-view-briefly)
10. [Analysing a completed experiment end to end](#10-analysing-a-completed-experiment-end-to-end)
11. [Causal inference without an experiment](#11-causal-inference-without-an-experiment)
12. [Project: analyse a simulated product experiment](#12-project-analyse-a-simulated-product-experiment)
13. [Common traps](#13-common-traps)
14. [Summary](#14-summary)

## 1. Why randomise: correlation, confounding and potential outcomes

### 1.1 The fundamental problem of causal inference

We want to know the **causal effect** of a treatment (a new checkout page) on an outcome (did the customer buy). For one customer, there are two **potential outcomes**: `Y(1)`, what happens if they see the new page, and `Y(0)`, what happens if they see the old one. The effect for that customer is `Y(1) − Y(0)`. But we only ever observe **one** of the two: the customer sees one page. The other outcome is the **counterfactual**, and it can never be observed for the same person at the same moment. That is the fundamental problem.

What we can estimate is the **average treatment effect (ATE)**, `E[Y(1)] − E[Y(0)]`, by comparing *different* people. That works only if the two groups are **comparable** apart from the treatment. If they are not, the difference in their outcomes mixes the effect with the pre-existing differences. That mixing is **confounding**.

### 1.2 A demonstration with a known answer

Users have a hidden "keenness". Keen users are more likely to use a new feature and also spend more anyway. The true effect of the feature is +2.0 in spend, for everyone.

```python run
rng = np.random.default_rng(0)
n = 100_000
keen = rng.normal(0, 1, n)                                    # hidden engagement
TRUE_EFFECT = 2.0
def spend(treated):
    return 20 + 8 * keen + TRUE_EFFECT * treated + rng.normal(0, 5, n)

# Observational world: keen users choose to adopt the feature
adopt = (rng.random(n) < 1 / (1 + np.exp(-1.5 * keen))).astype(int)
y_obs = spend(adopt)
naive = y_obs[adopt == 1].mean() - y_obs[adopt == 0].mean()

# Experimental world: a coin flip decides who gets the feature
assign = rng.integers(0, 2, n)
y_rct = spend(assign)
rct = y_rct[assign == 1].mean() - y_rct[assign == 0].mean()

print(f"true effect                              : {TRUE_EFFECT:.2f}")
print(f"observational comparison (adopters vs not): {naive:.2f}   <- inflated by keenness")
print(f"randomised comparison                    : {rct:.2f}")
print(f"mean keenness of adopters {keen[adopt == 1].mean():+.2f} vs non-adopters {keen[adopt == 0].mean():+.2f}; in the randomised arms {keen[assign == 1].mean():+.2f} vs {keen[assign == 0].mean():+.2f}")
```
```text
true effect                              : 2.00
observational comparison (adopters vs not): 10.52   <- inflated by keenness
randomised comparison                    : 1.96
mean keenness of adopters +0.53 vs non-adopters -0.53; in the randomised arms -0.00 vs +0.00
```

The observational difference is several times the truth, because adopters were keener to begin with. A coin flip cannot be correlated with keenness (or with anything else, seen or unseen), so randomised groups are **exchangeable** on average, and the difference in means estimates the ATE without bias. This is the entire logic of an experiment: **randomisation breaks every link between the treatment and the confounders**, including the ones you did not think of.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw two side-by-side scatter plots of 100,000 users, with hidden keenness on the x-axis and spend on the y-axis. Left plot, observational: users with high keenness adopt a feature more often, so adopters (orange) sit to the right of non-adopters (blue); the gap in mean spend is 10.52 while the true effect is 2.0. Right plot, randomised: a coin flip mixes colours evenly (mean gap 1.96). Mark the mean of each colour."

### 1.3 What an experiment does not give you

- It estimates the effect **for the population and period tested**, not forever and not for everyone.
- It tells you **whether** and **how much**, not **why**.
- It is only as good as its execution: a broken split, contamination between arms, or a metric defined after the fact can ruin it. Most of this chapter is about those failures.

## 2. Anatomy of an A/B test

### 2.1 The parts

| Part | Question | Example |
|---|---|---|
| **Hypothesis** | What do we change, and what do we expect? | a one-page checkout will raise purchase conversion |
| **Unit of randomisation** | Who or what is assigned? | the user (not the session, not the page view) |
| **Treatment / control** | What does each arm get? | new page / old page |
| **Primary metric** | The one number that decides | purchase conversion within 7 days |
| **Guardrail metrics** | What must not get worse? | page load time, refund rate, support tickets |
| **Secondary metrics** | Help to understand, never to decide | revenue per user, basket size |
| **Minimum detectable effect (MDE)** | The smallest effect worth detecting | +0.5 percentage points |
| **Sample size and duration** | How long, how many | computed in section 4 |
| **Decision rule** | What do we do under each outcome? | ship if the lower bound of the interval is above 0 and guardrails hold |

**Write these down before the experiment starts** (pre-registration). Everything you decide after seeing the data (which metric, which segment, which dates) is a way to fool yourself.

### 2.2 The unit of randomisation

The unit must match how the metric is measured and how interference can happen. If you randomise by *page view* but a user sees both versions, their behaviour is a blend. If users influence each other (a marketplace, a social network, shared inventory), randomising users leaks the treatment between arms (**interference**) and the measured effect is wrong; the fix is to randomise clusters (cities, groups).

### 2.3 Assigning users: a stable, independent hash

Assignment must be (1) **random-like**, (2) **stable**, the same user always sees the same arm, and (3) **independent between experiments**, otherwise two experiments are secretly one. The standard solution is to hash the user id together with an experiment-specific **salt**.

```python run
def bucket(user_id, salt, n_buckets=1000):
    h = hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest()
    return int(h[:12], 16) % n_buckets

def arm(user_id, salt, treatment_share=0.5):
    return "treatment" if bucket(user_id, salt) < treatment_share * 1000 else "control"

ids = np.arange(200_000)
a1 = np.array([arm(i, "checkout-v2") for i in ids])
print("share in treatment:", round(float((a1 == "treatment").mean()), 4), "| stable on a second call:", all(arm(i, "checkout-v2") == a1[i] for i in range(0, 5000)))
a2 = np.array([arm(i, "new-search") for i in ids])               # a different experiment, different salt
t1, t2 = (a1 == "treatment"), (a2 == "treatment")
print("another experiment's treatment share:", round(float(t2.mean()), 4), "| correlation between the two assignments:", round(float(np.corrcoef(t1, t2)[0, 1]), 4))
print("share of users in treatment of BOTH:", round(float((t1 & t2).mean()), 4), "(independence would give 0.25)")
a3 = np.array([arm(i, "checkout-v2") for i in ids])               # same salt = same split
print("reusing the salt gives the identical split:", bool((a1 == a3).all()), " <- two experiments with one salt would not be independent")
```
```text
share in treatment: 0.5002 | stable on a second call: True
another experiment's treatment share: 0.5013 | correlation between the two assignments: 0.0004
share of users in treatment of BOTH: 0.2508 (independence would give 0.25)
reusing the salt gives the identical split: True  <- two experiments with one salt would not be independent
```

Hashing beats `random.choice` at request time, because a random choice made at each visit gives a returning user a different page each time, and it needs no stored table.

## 3. Analysing a test: proportions and means

### 3.1 The test of two proportions, from scratch

Conversion is a yes/no per user, so each arm is a count of successes `x` out of `n`. With `p̂₁ = x₁/n₁` and `p̂₂ = x₂/n₂`, the null hypothesis "no difference" is tested with the **pooled z-test**:

```text
p̂ = (x₁ + x₂)/(n₁ + n₂)          z = (p̂₂ − p̂₁) / sqrt( p̂ (1 − p̂) (1/n₁ + 1/n₂) )          p-value = 2 · P(Z > |z|)
```

The **confidence interval** for the difference uses the unpooled standard error `sqrt(p̂₁(1−p̂₁)/n₁ + p̂₂(1−p̂₂)/n₂)` (we are no longer assuming the null).

```python run
def two_prop_test(x_c, n_c, x_t, n_t, alpha=0.05):
    p_c, p_t = x_c / n_c, x_t / n_t
    pooled = (x_c + x_t) / (n_c + n_t)
    z = (p_t - p_c) / math.sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t))
    p_value = 2 * stats.norm.sf(abs(z))
    se = math.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    zc = stats.norm.ppf(1 - alpha / 2)
    return {"p_control": p_c, "p_treatment": p_t, "diff": p_t - p_c, "relative lift": (p_t - p_c) / p_c, "z": z, "p_value": p_value,
            "ci_low": p_t - p_c - zc * se, "ci_high": p_t - p_c + zc * se}

res = two_prop_test(x_c=1000, n_c=10_000, x_t=1060, n_t=10_000)
print({k: round(v, 5) for k, v in res.items()})
z_sm, p_sm = proportions_ztest(count=[1060, 1000], nobs=[10_000, 10_000])
lo, hi = confint_proportions_2indep(1060, 10_000, 1000, 10_000, method="wald")
print("statsmodels  z %.5f  p-value %.5f  CI [%.5f, %.5f]" % (z_sm, p_sm, lo, hi))
print("max difference:", max(abs(res["z"] - z_sm), abs(res["p_value"] - p_sm), abs(res["ci_low"] - lo), abs(res["ci_high"] - hi)))
```
```text
{'p_control': 0.1, 'p_treatment': 0.106, 'diff': 0.006, 'relative lift': 0.06, 'z': 1.39579, 'p_value': np.float64(0.16278), 'ci_low': np.float64(-0.00242), 'ci_high': np.float64(0.01442)}
statsmodels  z 1.39579  p-value 0.16278  CI [-0.00242, 0.01442]
max difference: 1.734723475976807e-18
```

> **Predict the output.** Control converts at 10.0% and treatment at 10.4%, with 10,000 users in each arm. Is the difference significant at the 5% level? Roughly what is the p-value?

<details><summary>Answer</summary>

No. The difference is 0.4 percentage points (a 4% relative lift), but with 10,000 users per arm the standard error of the difference is about 0.43 points, so the observed gap is less than one standard error.

```python run
r = two_prop_test(1000, 10_000, 1040, 10_000)
print(f"z = {r['z']:.3f}, p-value = {r['p_value']:.3f}, 95% CI for the difference [{r['ci_low']:+.4f}, {r['ci_high']:+.4f}]")
```
```text
z = 0.935, p-value = 0.350, 95% CI for the difference [-0.0044, +0.0124]
```

The interval runs from a loss of about half a percentage point to a gain of more than one point: the data are compatible with a real improvement, with no effect and with a harm. "Not significant" means **inconclusive**, not "no effect".

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw ONE plot of the normal curve of the difference in conversion rate between two arms, 10,000 users each. Control converts at 10.0%, treatment at 10.6%, so the observed difference is 0.006. Centre the curve on zero (the null), mark z = 1.40 with a vertical line, shade both tails beyond plus and minus 1.40 (total p-value 0.163), and also draw the 95% confidence interval from -0.0024 to +0.0144 as a bar under the axis."

### 3.2 Means: the Welch t-test

For a continuous metric (revenue per user, time on page) compare the means. The **Welch** test does not assume equal variances:

```text
t = (ȳ_t − ȳ_c) / sqrt( s_t²/n_t + s_c²/n_c )          degrees of freedom by the Welch-Satterthwaite formula
```

```python run
def welch(y_c, y_t, alpha=0.05):
    n_c, n_t = len(y_c), len(y_t)
    v_c, v_t = y_c.var(ddof=1) / n_c, y_t.var(ddof=1) / n_t
    diff = y_t.mean() - y_c.mean()
    se = math.sqrt(v_c + v_t)
    df = (v_c + v_t) ** 2 / (v_c ** 2 / (n_c - 1) + v_t ** 2 / (n_t - 1))
    t = diff / se
    p = 2 * stats.t.sf(abs(t), df)
    h = stats.t.ppf(1 - alpha / 2, df) * se
    return {"diff": diff, "se": se, "t": t, "df": df, "p_value": p, "ci_low": diff - h, "ci_high": diff + h}

rng = np.random.default_rng(1)
yc = rng.normal(50, 20, 3000); yt = rng.normal(51.5, 25, 3200)                        # different variances and sizes
ours = welch(yc, yt)
ref = stats.ttest_ind(yt, yc, equal_var=False)
ci = ref.confidence_interval(0.95)
print({k: round(v, 5) for k, v in ours.items()})
print("scipy: t %.5f  p %.5f  df %.3f  CI [%.5f, %.5f]" % (ref.statistic, ref.pvalue, ref.df, ci.low, ci.high))
```
```text
{'diff': np.float64(1.37903), 'se': 0.57219, 't': np.float64(2.41009), 'df': np.float64(6042.99891), 'p_value': np.float64(0.01598), 'ci_low': np.float64(0.25733), 'ci_high': np.float64(2.50074)}
scipy: t 2.41009  p 0.01598  df 6042.999  CI [0.25733, 2.50074]
```

### 3.3 Statistical and practical significance

A **p-value** is the probability of seeing a difference at least this large *if there were no true difference*. It is not the probability that the treatment works, nor that the null is true. With a huge sample, a trivially small effect is "highly significant"; with a small sample, a large effect is "not significant". Always report three things together:

1. the **effect size** with its **confidence interval** (how big, and how sure),
2. the **p-value** (how surprising under no effect),
3. whether the effect is **practically worth** the change (the MDE you set in advance).

```python run
for n_arm in [2_000, 20_000, 200_000, 2_000_000]:
    x_c, x_t = int(0.1000 * n_arm), int(0.1020 * n_arm)                                # a +0.2 point (2% relative) lift in every case
    r = two_prop_test(x_c, n_arm, x_t, n_arm)
    print(f"n per arm {n_arm:>9,}: lift {r['diff']:+.4f}  p-value {r['p_value']:.4f}  95% CI [{r['ci_low']:+.4f}, {r['ci_high']:+.4f}]")
```
```text
n per arm     2,000: lift +0.0020  p-value 0.8338  95% CI [-0.0167, +0.0207]
n per arm    20,000: lift +0.0019  p-value 0.5175  95% CI [-0.0040, +0.0079]
n per arm   200,000: lift +0.0020  p-value 0.0358  95% CI [+0.0001, +0.0039]
n per arm 2,000,000: lift +0.0020  p-value 0.0000  95% CI [+0.0014, +0.0026]
```

The same small effect (0.2 points) moves from hopelessly inconclusive to "highly significant" only because the sample grows. Whether a +0.2 point lift is worth shipping is a business question that the p-value cannot answer, and a wide interval at small `n` is not evidence that the effect is zero.

### 3.4 One-sided versus two-sided

A two-sided test asks "is there a difference in either direction?". A one-sided test asks only "is the treatment better?" and has more power for that single direction, but it can never detect a harm. Experiments that can hurt users (nearly all of them) use **two-sided** tests, or one-sided tests with the harm checked by a guardrail. Decide *before* the data arrive; switching sides afterwards halves the p-value dishonestly.

### 3.5 Try it

1. Run `two_prop_test` with `alpha=0.01`. What happens to the interval and to the decision?
2. Compute the relative lift's confidence interval by dividing the absolute interval by the control rate. Why is that an approximation?

## 4. Power, minimum detectable effect and sample size

### 4.1 Two ways to be wrong

| | Truth: no effect | Truth: a real effect |
|---|---|---|
| **Test says significant** | false positive (type I error), probability **α** (usually 0.05) | correct; probability **1 − β** is the **power** |
| **Test says not significant** | correct | missed effect (type II error), probability **β** (usually 0.2) |

Significance level α is fixed by you. **Power** (1 − β, typically 80%) is the chance to detect an effect of a given size if it is really there. It grows with the sample size and with the size of the effect, and falls with the noise.

### 4.2 Sample size by formula

For two proportions, `p₁` (control) and `p₂ = p₁ + δ` (treatment), the sample size **per arm** for a two-sided test at level α and power 1 − β is approximately

```text
n = (z_{1−α/2} + z_{1−β})² · [ p₁(1−p₁) + p₂(1−p₂) ] / δ²
```

For a continuous metric with standard deviation σ and an absolute effect δ:

```text
n = 2 · (z_{1−α/2} + z_{1−β})² · σ² / δ²
```

The `1/δ²` is the most important part: **halving the effect you want to detect quadruples the sample**.

```python run
def n_per_arm_prop(p1, delta, alpha=0.05, power=0.8):
    p2 = p1 + delta
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / delta ** 2

def n_per_arm_mean(sigma, delta, alpha=0.05, power=0.8):
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return 2 * (za + zb) ** 2 * sigma ** 2 / delta ** 2

base = 0.10
rows = []
for rel in [0.20, 0.10, 0.05, 0.02, 0.01]:
    d = base * rel
    n_ = n_per_arm_prop(base, d)
    es = proportion_effectsize(base + d, base)
    n_sm = NormalIndPower().solve_power(effect_size=es, alpha=0.05, power=0.8, ratio=1.0)
    rows.append((f"{rel:.0%}", d, n_, n_sm))
print(pd.DataFrame(rows, columns=["relative lift to detect", "absolute (points)", "n per arm (formula)", "n per arm (statsmodels, arcsine)"]).round(4).to_string(index=False))
print("\nhalving the lift from 10% to 5% multiplies n by", round(n_per_arm_prop(base, base * .05) / n_per_arm_prop(base, base * .10), 2))
```
```text
relative lift to detect  absolute (points)  n per arm (formula)  n per arm (statsmodels, arcsine)
                    20%             0.0200           3,838.1022                        3,834.5957
                    10%             0.0100          14,748.0450                       14,744.1048
                     5%             0.0050          57,759.9060                       57,755.6390
                     2%             0.0020         356,331.2911                      356,326.1535
                     1%             0.0010       1,419,069.6071                    1,419,061.8189

halving the lift from 10% to 5% multiplies n by 3.92
```

The two columns differ slightly because statsmodels uses an arcsine-transformed effect size; for planning, either is fine. What matters is the size of the numbers: detecting a 1% relative lift on a 10% base needs more than a million users per arm.

### 4.3 Verify by simulation

A formula is a claim; a simulation checks it. Run many experiments with a real lift of exactly the planned size, and count how often the test rejects.

```python run
def simulate_power(p1, delta, n, sims=20_000, alpha=0.05, seed=0):
    r = np.random.default_rng(seed)
    x1, x2 = r.binomial(n, p1, sims), r.binomial(n, p1 + delta, sims)
    pooled = (x1 + x2) / (2 * n)
    z = (x2 - x1) / n / np.sqrt(pooled * (1 - pooled) * 2 / n)
    return float(np.mean(np.abs(z) > stats.norm.ppf(1 - alpha / 2)))

d = 0.005
n_plan = math.ceil(n_per_arm_prop(0.10, d))
print(f"planned n per arm for a +{d} lift on a 10% base: {n_plan:,}")
print("simulated power at the planned n      :", round(simulate_power(0.10, d, n_plan), 3), "(target 0.80)")
print("simulated power with half the sample   :", round(simulate_power(0.10, d, n_plan // 2), 3))
print("simulated power if the true lift is half the planned one (n unchanged):", round(simulate_power(0.10, d / 2, n_plan), 3))
print("simulated false-positive rate when there is NO effect, planned n:", round(simulate_power(0.10, 0.0, n_plan), 3), "(target 0.05)")
```
```text
planned n per arm for a +0.005 lift on a 10% base: 57,760
simulated power at the planned n      : 0.796 (target 0.80)
simulated power with half the sample   : 0.505
simulated power if the true lift is half the planned one (n unchanged): 0.287
simulated false-positive rate when there is NO effect, planned n: 0.049 (target 0.05)
```

The last two lines are the lessons. If the real effect is **half** what you planned for, power collapses to below 30%. Experiments are routinely under-powered because the planned effect was wishful. And with no effect the test rejects 5% of the time: that is what α means.

### 4.4 Duration, traffic and the weekly cycle

Sample size becomes a duration: `days = (2 · n per arm) / daily eligible traffic`. Two corrections:

- **Run full weeks.** Behaviour differs between weekdays and weekends; stopping on a Tuesday over-represents some days.
- **Do not sell the same user twice.** Count **unique users**, not visits, if the unit is the user.

```python run
daily_traffic = 40_000
n_needed = math.ceil(n_per_arm_prop(0.10, 0.005))
days = 2 * n_needed / daily_traffic
print(f"{n_needed:,} per arm -> {2 * n_needed:,} users in total -> {days:.1f} days at {daily_traffic:,} eligible users a day -> run {math.ceil(days / 7)} full weeks")
print("if only half the traffic is eligible:", math.ceil(2 * n_needed / (daily_traffic / 2) / 7), "weeks")
```
```text
57,760 per arm -> 115,520 users in total -> 2.9 days at 40,000 eligible users a day -> run 1 full weeks
if only half the traffic is eligible: 1 weeks
```

### 4.5 The minimum detectable effect, turned around

Often traffic is the constraint and you ask the reverse: "given 4 weeks, what is the smallest effect I can detect?".

```python run
def mde_prop(p1, n, alpha=0.05, power=0.8):
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    delta = 0.001
    for _ in range(60):                                                                   # solve n_per_arm_prop(p1, delta) = n by fixed-point
        delta = (za + zb) * math.sqrt((p1 * (1 - p1) + (p1 + delta) * (1 - p1 - delta)) / n)
    return delta
for weeks in [1, 2, 4, 8]:
    n_arm = int(weeks * 7 * daily_traffic / 2)
    d_ = mde_prop(0.10, n_arm)
    print(f"{weeks} week(s): {n_arm:>9,} users per arm -> MDE {d_:.4f} points absolute ({d_ / 0.10:.1%} relative)")
```
```text
1 week(s):   140,000 users per arm -> MDE 0.0032 points absolute (3.2% relative)
2 week(s):   280,000 users per arm -> MDE 0.0023 points absolute (2.3% relative)
4 week(s):   560,000 users per arm -> MDE 0.0016 points absolute (1.6% relative)
8 week(s): 1,120,000 users per arm -> MDE 0.0011 points absolute (1.1% relative)
```

If the MDE is bigger than any lift you could realistically expect, **do not run the test as designed**: it will most probably come back inconclusive. Change the design (a more sensitive metric, variance reduction, a bolder change) or accept that you cannot learn this with an experiment.

### 4.6 Try it

1. Change the power from 0.8 to 0.9 and the α from 0.05 to 0.01. How much does the sample size grow?
2. Use `TTestIndPower` to find the sample size for a continuous metric with σ = 25 and a 2-unit effect, and compare with `n_per_arm_mean`.

## 5. Variance reduction and awkward metrics

### 5.1 CUPED: use what you knew before the experiment

Users differ hugely before they ever see your change: heavy spenders spend a lot in both arms. That between-user variance is noise to the experiment. If we have a **pre-experiment** measurement `X` of each user (last month's spend), we can subtract the part of `Y` that `X` predicts. **CUPED** (Controlled-experiment Using Pre-Experiment Data) does this:

```text
θ = Cov(Y, X) / Var(X)          Y_adj = Y − θ (X − mean(X))
```

The adjusted metric has the same expected treatment effect (X was measured before randomisation, so it is independent of the arm), and a variance smaller by the factor `1 − ρ²`, where `ρ` is the correlation between `X` and `Y`. A correlation of 0.7 halves the variance and so halves the sample you need.

```python run
rng = np.random.default_rng(3)
n_arm = 2000
rho_target = 0.7
def make_experiment(effect):
    x = rng.normal(100, 30, 2 * n_arm)                                                   # pre-experiment spend
    y = 100 + rho_target * (x - 100) + rng.normal(0, 30 * math.sqrt(1 - rho_target ** 2), 2 * n_arm)   # in-experiment spend, correlated with x
    arm_ = np.r_[np.zeros(n_arm), np.ones(n_arm)]
    return x, y + effect * arm_, arm_

x, y, a = make_experiment(effect=3.0)
theta = np.cov(y, x)[0, 1] / np.var(x, ddof=1)
y_adj = y - theta * (x - x.mean())
raw = welch(y[a == 0], y[a == 1]); adj = welch(y_adj[a == 0], y_adj[a == 1])
print(f"corr(x, y) = {np.corrcoef(x, y)[0, 1]:.3f} | theta = {theta:.3f}")
print(f"raw     : effect {raw['diff']:.3f}, standard error {raw['se']:.3f}, p-value {raw['p_value']:.4f}")
print(f"CUPED   : effect {adj['diff']:.3f}, standard error {adj['se']:.3f}, p-value {adj['p_value']:.4f}")
print(f"variance ratio {(adj['se'] / raw['se']) ** 2:.3f} (theory: 1 - rho^2 = {1 - np.corrcoef(x, y)[0, 1] ** 2:.3f})")
```
```text
corr(x, y) = 0.698 | theta = 0.700
raw     : effect 2.584, standard error 0.952, p-value 0.0067
CUPED   : effect 3.220, standard error 0.680, p-value 0.0000
variance ratio 0.511 (theory: 1 - rho^2 = 0.513)
```

Check that CUPED does not introduce bias, and measure the power gain by simulation:

```python run
reps = 3000
eff = 3.0
est_raw, est_adj, rej_raw, rej_adj = [], [], 0, 0
for _ in range(reps):
    x, y, a = make_experiment(eff)
    th = np.cov(y, x)[0, 1] / np.var(x, ddof=1)
    ya = y - th * (x - x.mean())
    r1, r2 = welch(y[a == 0], y[a == 1]), welch(ya[a == 0], ya[a == 1])
    est_raw.append(r1["diff"]); est_adj.append(r2["diff"]); rej_raw += r1["p_value"] < 0.05; rej_adj += r2["p_value"] < 0.05
print(f"true effect {eff} | mean estimate raw {np.mean(est_raw):.3f}, CUPED {np.mean(est_adj):.3f} (both unbiased)")
print(f"spread of the estimate (std over {reps} experiments): raw {np.std(est_raw):.3f}, CUPED {np.std(est_adj):.3f}")
print(f"power: raw {rej_raw / reps:.3f} | CUPED {rej_adj / reps:.3f}")
```
```text
true effect 3.0 | mean estimate raw 3.025, CUPED 3.016 (both unbiased)
spread of the estimate (std over 3000 experiments): raw 0.972, CUPED 0.689
power: raw 0.882 | CUPED 0.993
```

Rules: the covariate must be measured **before** assignment (never something the treatment could change, or you bias the estimate), and `θ` can be computed on the pooled data of both arms. A regression of `Y` on the arm and `X` gives the same adjustment and a standard error with no extra work.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw two scatter plots side by side of 4,000 users: pre-experiment spend x (mean 100, sd 30) against in-experiment spend y, with correlation 0.7, coloured by arm (control, treatment +3). Left: raw y, where the two colour clouds overlap heavily. Right: CUPED-adjusted y = y - 0.7 (x - mean x), where the cloud is narrower and the arms separate. Annotate the standard errors 0.952 and 0.680."

### 5.2 Ratio metrics and the unit of analysis

"Click-through rate" is clicks divided by impressions. If users are randomised, the independent units are **users**, not impressions: a user with 500 impressions is one observation, not 500. Treating every impression as independent gives a standard error far too small. The proper variance of a ratio of means uses the **delta method**:

```text
R = mean(clicks)/mean(views)      Var(R) ≈ (1/(n·V̄²)) · [ Var(C) − 2R·Cov(C,V) + R²·Var(V) ]
```

```python run
rng = np.random.default_rng(4)
n_users = 4000
views = rng.poisson(rng.gamma(1.5, 20, n_users)) + 1                                    # very different activity per user
ctr_user = rng.beta(2, 38, n_users)                                      # each user has their own click propensity
clicks = rng.binomial(views, ctr_user)
R = clicks.sum() / views.sum()

naive_se = math.sqrt(R * (1 - R) / views.sum())                                          # treats each impression as independent
delta_se = math.sqrt((np.var(clicks, ddof=1) - 2 * R * np.cov(clicks, views)[0, 1] + R ** 2 * np.var(views, ddof=1)) / n_users) / views.mean()
idx = rng.integers(0, n_users, (2000, n_users))                                          # resample whole USERS with replacement
boot = clicks[idx].sum(1) / views[idx].sum(1)
print(f"CTR {R:.4f}")
print(f"standard error: impression-level (wrong) {naive_se:.5f} | delta method (users) {delta_se:.5f} | bootstrap over users {np.std(boot):.5f}")
print(f"the naive standard error is {delta_se / naive_se:.1f} times too small")
```
```text
CTR 0.0494
standard error: impression-level (wrong) 0.00061 | delta method (users) 0.00091 | bootstrap over users 0.00090
the naive standard error is 1.5 times too small
```

The two honest estimates (delta method and bootstrap over users) agree, and the naive one is about 1.5 times too small here, which means its z-statistics are inflated by the same factor and its false-positive rate is far above 5%. The more users differ in activity, the worse it gets. **Analyse at the level you randomised.**

### 5.3 Heavy-tailed metrics: revenue

Revenue per user is mostly zero with a few huge values. The mean is dominated by those whales, so the variance is enormous and power is low; a single large purchase in one arm can create a fake lift.

```python run
rng = np.random.default_rng(5)
def revenue(n, lift=0.0):
    buys = rng.random(n) < 0.08
    amount = np.exp(rng.normal(3.0, 1.1, n)) * (1 + lift)                                # lognormal order values: a heavy right tail
    return buys * amount

yc, yt = revenue(30_000), revenue(30_000, lift=0.05)                                       # a real 5% revenue lift
r_mean = welch(yc, yt)
cap = np.quantile(np.r_[yc, yt], 0.995)
r_cap = welch(np.minimum(yc, cap), np.minimum(yt, cap))
print("share of zeros:", round(float((yc == 0).mean()), 3), "| max order value", round(float(yc.max()), 1), "vs median positive order", round(float(np.median(yc[yc > 0])), 1))
print(f"plain means      : diff {r_mean['diff']:+.3f} (se {r_mean['se']:.3f}, p {r_mean['p_value']:.3f})")
print(f"capped at p99.5  : diff {r_cap['diff']:+.3f} (se {r_cap['se']:.3f}, p {r_cap['p_value']:.3f})")
```
```text
share of zeros: 0.919 | max order value 526.4 vs median positive order 21.6
plain means      : diff +0.082 (se 0.150, p 0.583)
capped at p99.5  : diff -0.092 (se 0.102, p 0.369)
```

Look at what the output says: with 60,000 users and a **real** 5% revenue lift, the plain comparison finds nothing (p = 0.58) and the capped one even has the wrong sign. Revenue per user is so noisy that this experiment cannot see a 5% change, which is exactly the power problem of section 4 in a harder form. (Capping also changes what is being estimated: it measures the effect on capped revenue.)

Options for heavy tails: **winsorise or cap** at a high percentile (decided in advance; it changes the estimand slightly), analyse **conversion and average order value separately**, use a **bootstrap** for the interval, or use a **log transform** for positive values. Never remove outliers after seeing which arm they fall in.

### 5.4 Time effects, novelty and interference

| Effect | What happens | Defence |
|---|---|---|
| **Novelty / primacy** | users click a new design because it is new, or avoid it because it is unfamiliar; the effect fades or grows | plot the effect by day; run long enough; look at new-versus-returning users |
| **Weekly cycles** | different behaviour on different days | run complete weeks |
| **Seasonality, campaigns** | an outside event hits one period | run arms concurrently, never "before versus after" |
| **Carry-over / contamination** | a user sees both versions or arms share a resource | stable assignment, cluster randomisation |
| **Network effects** | a treated user changes an untreated user's experience | randomise by cluster, geo, or time slices |

### 5.5 Try it

1. In the CUPED experiment, set the correlation to 0.3 instead of 0.7. How much variance do you save now?
2. Use `sm.OLS` with `y ~ arm + x` and check that the coefficient on `arm` and its standard error agree with the CUPED result.


## 6. Is the experiment trustworthy? Sample ratio mismatch and A/A tests

### 6.1 Check the experiment before reading the result

Before looking at any metric, ask whether the experiment itself ran correctly. Two checks catch most disasters.

### 6.2 Sample ratio mismatch (SRM)

If you planned a 50/50 split and 100,000 users arrived, you expect close to 50,000 in each arm. A **sample ratio mismatch** means the observed counts differ from the planned ratio by more than chance allows. It is the single most valuable diagnostic in experimentation, because it reveals that **assignment or logging is broken**, and then *every* metric is suspect: the two arms no longer contain comparable users.

The test is a chi-square goodness-of-fit test of the observed counts against the planned ratio. Because an SRM signals a bug, not a result, teams use a strict threshold (p < 0.001).

```python run
def srm_check(n_control, n_treatment, planned_treatment_share=0.5):
    total = n_control + n_treatment
    expected = [total * (1 - planned_treatment_share), total * planned_treatment_share]
    chi2, p = stats.chisquare([n_control, n_treatment], expected)
    return chi2, p

for label, nc, nt in [("healthy: 50,215 vs 49,785", 50_215, 49_785), ("small shortfall: 50,500 vs 49,500", 50_500, 49_500), ("broken: 51,000 vs 49,000", 51_000, 49_000)]:
    chi2, p = srm_check(nc, nt)
    print(f"{label:36s} chi2 {chi2:7.2f}  p-value {p:.2e}  -> {'SRM! do not trust this experiment' if p < 0.001 else 'ok'}")
```
```text
healthy: 50,215 vs 49,785            chi2    1.85  p-value 1.74e-01  -> ok
small shortfall: 50,500 vs 49,500    chi2   10.00  p-value 1.57e-03  -> ok
broken: 51,000 vs 49,000             chi2   40.00  p-value 2.54e-10  -> SRM! do not trust this experiment
```

A split of 51,000 to 49,000 looks harmless (2% off), and the test says it is wildly improbable for a fair coin. The middle row (50,500 to 49,500) is borderline: p = 0.0016 is above the 0.001 alarm line, yet a fair coin would produce a gap that large only about once in 600 experiments. A borderline SRM deserves a look at the logs, not a shrug. Common causes: a redirect in the treatment loses users; a bot filter applied to one arm only; the treatment crashes on some devices, so those users never get logged; assignment done after some exposure; a caching layer that serves one version to many.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a bar chart of three planned 50/50 experiments showing observed counts per arm: 50,215 vs 49,785 (p = 0.17, ok), 50,500 vs 49,500 (p = 0.0016, borderline), 51,000 vs 49,000 (p = 2.5e-10, SRM). Add a dashed line at the expected 50,000 and a coloured badge above each pair showing chi-square (1.85, 10.00, 40.00) and a green or red verdict."

### 6.3 What an SRM does to the result

Suppose the treatment crashes for 20% of users on slow phones, so those users are not logged in the treatment arm. Slow-phone users convert less than others. The treatment has **no real effect**, but the surviving users in the treatment arm are a healthier mix, and the metric looks better.

```python run
rng = np.random.default_rng(10)
n = 200_000
slow = rng.random(n) < 0.30                                                       # 30% of users are on slow phones
conv_p = np.where(slow, 0.06, 0.12)                                                # slow-phone users convert less
treated = rng.integers(0, 2, n).astype(bool)
converted = rng.random(n) < conv_p                                                 # the treatment has NO effect on anyone
lost = treated & slow & (rng.random(n) < 0.25)                                     # in the treatment arm, 25% of slow-phone users crash and are never logged
logged = ~lost
nc, nt = int(((~treated) & logged).sum()), int((treated & logged).sum())
xc, xt = int(converted[(~treated) & logged].sum()), int(converted[treated & logged].sum())
r = two_prop_test(xc, nc, xt, nt)
print(f"users logged: control {nc:,}, treatment {nt:,}  | SRM p-value {srm_check(nc, nt)[1]:.2e}")
print(f"conversion: control {r['p_control']:.4f}, treatment {r['p_treatment']:.4f} -> fake lift {r['diff']:+.4f} (p-value {r['p_value']:.2e}); the true effect is exactly 0")
```
```text
users logged: control 99,467, treatment 92,927  | SRM p-value 2.83e-50
conversion: control 0.1004, treatment 0.1052 -> fake lift +0.0048 (p-value 5.98e-04); the true effect is exactly 0
```

A highly significant "win" that is entirely an artefact. The SRM check, run first, would have stopped the analysis. **Treat an SRM as a bug to fix, not a result to adjust for.** Find the cause, repair it, rerun.

### 6.4 A/A tests: test the testing machinery

An **A/A test** assigns users to two arms that receive the *same* experience. Run it on your real platform and real metrics. If the tooling is sound, about 5% of metrics are "significant" at α = 0.05 and the p-values are spread evenly between 0 and 1. If more than 5% are significant, something is wrong: variance underestimated (the impression-level error of section 5.2), correlated users, a faulty hash.

```python run
pop = pd.DataFrame({"user": np.arange(100_000)})
pop["metric"] = rng.lognormal(3, 1, len(pop))                                       # a skewed per-user metric
pvals = []
for s in range(1500):
    t = np.array([bucket(u, f"aa-test-{s}") < 500 for u in pop["user"].iloc[:2000]])        # a fresh A/A split each time (2,000 users)
    y = pop["metric"].iloc[:2000].to_numpy()
    pvals.append(welch(y[~t], y[t])["p_value"])
pvals = np.array(pvals)
print(f"A/A tests: {len(pvals)} | share significant at 0.05: {np.mean(pvals < 0.05):.3f} (target 0.05)")
hist, _ = np.histogram(pvals, bins=10, range=(0, 1))
print("p-value histogram (10 equal bins; flat = healthy):", hist.tolist())
print("Kolmogorov-Smirnov test against Uniform(0,1): p-value", round(stats.kstest(pvals, "uniform").pvalue, 3))
```
```text
A/A tests: 1500 | share significant at 0.05: 0.055 (target 0.05)
p-value histogram (10 equal bins; flat = healthy): [163, 159, 147, 149, 135, 139, 154, 144, 164, 146]
Kolmogorov-Smirnov test against Uniform(0,1): p-value 0.608
```

### 6.5 Balance on pre-experiment covariates

Randomisation guarantees balance **on average**; any one experiment can be unlucky, and a bug can break it. Compare the arms on things measured *before* the experiment (previous spend, tenure, platform, country) with the **standardised mean difference** `(mean_t − mean_c) / pooled std`. Values within ±0.05 are fine; large values suggest a problem.

```python run
n = 20_000
pre_spend = rng.lognormal(3, 1, n); tenure = rng.gamma(2, 12, n); platform = rng.choice(["ios", "android", "web"], n, p=[.4, .4, .2])
good = rng.integers(0, 2, n).astype(bool)                                           # a fair split
bad = (pre_spend > np.quantile(pre_spend, 0.4)) & (rng.random(n) < 0.6)             # a broken split: treatment skewed to high spenders
def smd(x, t):
    return (x[t].mean() - x[~t].mean()) / math.sqrt((x[t].var(ddof=1) + x[~t].var(ddof=1)) / 2)
rows = []
for name, t in [("fair split", good), ("broken split", bad)]:
    rows.append((name, smd(np.log(pre_spend), t), smd(tenure, t), smd((platform == "ios").astype(float), t), ))
print(pd.DataFrame(rows, columns=["", "SMD log pre-spend", "SMD tenure", "SMD share on iOS"]).set_index("").round(3).to_string())
```
```text
              SMD log pre-spend  SMD tenure  SMD share on iOS
                                                             
fair split               0.0050     -0.0140            0.0070
broken split             1.2100     -0.0090            0.0240
```

### 6.6 A checklist before reading results

1. Planned versus observed sample ratio (SRM, p < 0.001 means stop).
2. Exposure: did the users in each arm actually experience what you intended (logging, feature flags, caching)?
3. Balance on pre-experiment covariates.
4. A/A history of the platform: is the false-positive rate 5%?
5. Data quality: duplicates, bots, test accounts, missing logs, metrics defined as planned.
6. Duration: whole weeks, the planned sample reached.

## 7. Multiple testing

### 7.1 The problem

Each test at level α has a 5% chance of a false positive when nothing is going on. Run many tests and the chance that **at least one** is a false positive grows quickly. With `m` independent tests, `P(at least one false positive) = 1 − (1 − α)^m`.

```python run
print(pd.DataFrame({"number of tests m": [1, 3, 5, 10, 20, 50, 100], "P(at least one false positive)": [1 - 0.95 ** m for m in [1, 3, 5, 10, 20, 50, 100]]}).round(3).to_string(index=False))
```
```text
 number of tests m  P(at least one false positive)
                 1                          0.0500
                 3                          0.1430
                 5                          0.2260
                10                          0.4010
                20                          0.6420
                50                          0.9230
               100                          0.9940
```

> **Predict the output.** An experiment tracks 20 metrics and the treatment has no effect on any of them. In what share of such experiments will at least one metric come out "significant" at 5%?

<details><summary>Answer</summary>

About **64%**: `1 − 0.95²⁰`. Simulate it:

```python run
rng7 = np.random.default_rng(7)
m_metrics, sims = 20, 20_000
z = rng7.normal(size=(sims, m_metrics))                                          # 20 independent null metrics per experiment
p = 2 * stats.norm.sf(np.abs(z))
print(f"experiments with at least one 'significant' metric (all effects are zero): {np.mean((p < 0.05).any(1)):.3f}   theory {1 - 0.95 ** 20:.3f}")
print(f"average number of 'significant' metrics per experiment: {np.mean((p < 0.05).sum(1)):.2f}   (= 20 x 0.05)")
```
```text
experiments with at least one 'significant' metric (all effects are zero): 0.642   theory 0.642
average number of 'significant' metrics per experiment: 1.00   (= 20 x 0.05)
```

More often than not, an experiment that does nothing will show a "win" on some metric. That is how teams ship noise.

</details>

The same applies to **segments** (country, platform, new versus returning), to **time slices**, to **several variants** (A/B/C/D) and to **many experiments** run by a team: every extra comparison is another draw.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw ONE line chart: x-axis is the number of independent tests m (1 to 100), y-axis is the probability of at least one false positive, 1 - 0.95^m. Plot the curve and label the points m=1 (0.05), m=10 (0.40), m=20 (0.64), m=50 (0.92), m=100 (0.99). Draw a horizontal dashed line at 0.05 and shade the gap between it and the curve to show inflated error."

### 7.2 Controlling the family-wise error rate (FWER)

The **family-wise error rate** is the probability of making *at least one* false claim in the family of tests. Controlling it at α means a false "win" is rare across the whole family.

- **Bonferroni**: reject test `i` if `p_i ≤ α/m`. Simple, valid under any dependence, conservative.
- **Holm** (step-down): sort the p-values `p_(1) ≤ ... ≤ p_(m)`; reject `p_(k)` while `p_(k) ≤ α/(m − k + 1)`, and stop at the first failure. Uniformly more powerful than Bonferroni, equally valid.

### 7.3 Controlling the false discovery rate (FDR)

When you run hundreds of tests and expect some real effects (feature screening, many segments), controlling the chance of *any* false claim is too strict. The **false discovery rate** is the expected *share* of claimed discoveries that are false. The **Benjamini-Hochberg (BH)** procedure: sort the p-values, find the largest `k` with `p_(k) ≤ (k/m)·q`, and reject the `k` smallest.

```python run
def bonferroni(p, alpha=0.05):
    return np.asarray(p) <= alpha / len(p)

def holm(p, alpha=0.05):
    p = np.asarray(p); order = np.argsort(p); m = len(p)
    reject = np.zeros(m, bool)
    for rank, idx in enumerate(order):
        if p[idx] <= alpha / (m - rank):
            reject[idx] = True
        else:
            break
    return reject

def benjamini_hochberg(p, q=0.05):
    p = np.asarray(p); m = len(p); order = np.argsort(p)
    thresh = (np.arange(1, m + 1) / m) * q
    below = np.flatnonzero(p[order] <= thresh)
    reject = np.zeros(m, bool)
    if len(below):
        reject[order[: below.max() + 1]] = True
    return reject

r = np.random.default_rng(2)
p_demo = np.r_[r.uniform(0, 0.001, 4), r.uniform(0.001, 0.04, 6), r.uniform(0, 1, 40)]            # a few strong effects, some weak, mostly nothing
for name, ours, method in [("Bonferroni", bonferroni(p_demo), "bonferroni"), ("Holm", holm(p_demo), "holm"), ("Benjamini-Hochberg", benjamini_hochberg(p_demo), "fdr_bh")]:
    ref = multipletests(p_demo, alpha=0.05, method=method)[0]
    print(f"{name:20s} rejects {int(ours.sum()):2d} of {len(p_demo)} | identical to statsmodels: {bool((ours == ref).all())}")
print(f"uncorrected p < 0.05 rejects {int((p_demo < 0.05).sum())}")
```
```text
Bonferroni           rejects  4 of 50 | identical to statsmodels: True
Holm                 rejects  4 of 50 | identical to statsmodels: True
Benjamini-Hochberg   rejects  5 of 50 | identical to statsmodels: True
uncorrected p < 0.05 rejects 11
```

### 7.4 What each procedure buys: a simulation

A hundred tests per experiment, of which 20 have a real effect (a shift of 3 standard errors) and 80 have none. We measure, over many experiments, how many true effects each rule finds (**power**), how often it makes at least one false claim (**FWER**) and what share of its claims are false (**FDR**).

```python run
rng8 = np.random.default_rng(8)
sims, m_true, m_null = 4000, 20, 80
rows = {"uncorrected": [], "Bonferroni": [], "Holm": [], "Benjamini-Hochberg": []}
for _ in range(sims):
    z = np.r_[rng8.normal(3, 1, m_true), rng8.normal(0, 1, m_null)]
    p = 2 * stats.norm.sf(np.abs(z))
    for name, rej in [("uncorrected", p < 0.05), ("Bonferroni", bonferroni(p)), ("Holm", holm(p)), ("Benjamini-Hochberg", benjamini_hochberg(p))]:
        tp, fp = int(rej[:m_true].sum()), int(rej[m_true:].sum())
        rows[name].append((tp / m_true, fp > 0, fp / max(tp + fp, 1)))
summary = pd.DataFrame({name: np.array(v).mean(0) for name, v in rows.items()}, index=["power (share of true effects found)", "FWER (any false claim)", "FDR (share of claims that are false)"]).T
print(summary.round(3).to_string())
```
```text
                    power (share of true effects found)  FWER (any false claim)  FDR (share of claims that are false)
uncorrected                                      0.8490                  0.9840                                0.1840
Bonferroni                                       0.3160                  0.0400                                0.0060
Holm                                             0.3220                  0.0420                                0.0070
Benjamini-Hochberg                               0.6060                  0.4020                                0.0390
```

Read the table row by row. Uncorrected testing finds the most true effects and also makes a false claim in almost every experiment. Bonferroni and Holm almost never make a false claim but find fewer effects. Benjamini-Hochberg finds more than the FWER methods while keeping the share of false claims near 5%. **Choose the error you can afford**: FWER when one false claim is costly (a launch decision), FDR when you screen many candidates and will follow up.

### 7.5 Segment fishing

You cut a null experiment into 20 segments and report the one with p < 0.05. That is exactly the 20-metric problem.

```python run
rng9 = np.random.default_rng(9)
n = 60_000
seg = rng9.integers(0, 20, n)
treated = rng9.integers(0, 2, n).astype(bool)
converted = rng9.random(n) < 0.10                                                  # no effect anywhere
rows = []
for s in range(20):
    m_ = seg == s
    r = two_prop_test(int(converted[m_ & ~treated].sum()), int((m_ & ~treated).sum()), int(converted[m_ & treated].sum()), int((m_ & treated).sum()))
    rows.append((s, r["diff"], r["p_value"]))
seg_tab = pd.DataFrame(rows, columns=["segment", "lift", "p_value"]).sort_values("p_value")
print(seg_tab.head(3).round(4).to_string(index=False))
print("smallest p-value:", round(seg_tab["p_value"].iloc[0], 4), "| Bonferroni threshold 0.05/20 =", 0.0025, "| BH rejects:", int(benjamini_hochberg(seg_tab["p_value"].to_numpy()).sum()), "segments")
```
```text
 segment    lift  p_value
       5  0.0252   0.0203
       7  0.0224   0.0355
      15 -0.0232   0.0376
smallest p-value: 0.0203 | Bonferroni threshold 0.05/20 = 0.0025 | BH rejects: 0 segments
```

The "best" segment shows p of about 0.02, an apparent win with a plausible story ("it works for segment 13!"). It is the largest of 20 draws. After correction, nothing survives.

### 7.6 Practical rules

1. **One primary metric** decides. Secondary and guardrail metrics are reported, not used to declare a win.
2. List the **segments** you will examine *before* the experiment. Everything else is **exploratory**, labelled as such, and follow-up experiments must confirm it.
3. For several variants against one control, use a correction (Holm, or Dunnett's test).
4. Guardrails need a different logic: to claim "no harm" you need power for the harm size (a non-inferiority margin), not merely "not significant".
5. Report the **number of things you looked at**, not only the one that worked.

## 8. Peeking and sequential testing

### 8.1 The temptation

The experiment has been running for a week. The dashboard shows p = 0.03. Do we stop and ship? Or p = 0.20 after three days: do we wait? Everyone peeks. The trouble is that a fixed-horizon test (section 3) is valid **only if you look once**, at the planned sample size. Looking repeatedly and stopping at the first "significant" result is a form of multiple testing, with a catch: the looks are on overlapping data, so the p-value wanders and, given enough looks, crosses 0.05 almost surely even when there is no effect.

### 8.2 Measuring the damage

An A/A experiment (no real effect). We observe a user pair at a time, compute the z-statistic at `K` evenly spaced looks, and stop with a "win" the first time `|z| > 1.96`.

```python run
rng10 = np.random.default_rng(10)
def peeking_false_positive_rate(K, per_look=200, sims=20_000, crit=1.96):
    d = rng10.normal(size=(sims, K, per_look)).sum(2)                    # sum of standardised pair differences in each batch
    S = d.cumsum(1)                                                       # running sum after each look
    n = per_look * np.arange(1, K + 1)
    Z = S / np.sqrt(n)                                                    # z-statistic at each look
    return float((np.abs(Z) > crit).any(1).mean()), Z

rows = []
for K in [1, 2, 3, 5, 10, 20, 50]:
    rate, _ = peeking_false_positive_rate(K)
    rows.append((K, rate))
print(pd.DataFrame(rows, columns=["number of looks K", "false-positive rate if you stop at the first |z| > 1.96"]).to_string(index=False))
```
```text
 number of looks K  false-positive rate if you stop at the first |z| > 1.96
                 1                                                   0.0517
                 2                                                   0.0850
                 3                                                   0.1069
                 5                                                   0.1394
                10                                                   0.1915
                20                                                   0.2484
                50                                                   0.3211
```

With one look the false-positive rate is the promised 5%. With ten looks it is roughly four times higher, and it keeps growing with every additional look. (Checking *daily* for a two-week test is 14 looks.) The nominal "5%" has become 20-30% without anyone noticing.

> **Predict the output.** Looking at the results after every one of 10 equal batches and stopping at the first p < 0.05, what is the real chance of declaring a winner when there is no effect?

<details><summary>Answer</summary>

Roughly **19%** (the table row for K = 10 above): almost four times the nominal 5%.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate or draw a random walk of the z-statistic of an A/A test (no real effect) over 10 equally spaced looks, showing several simulated paths. Draw horizontal lines at z = plus and minus 1.96. Highlight in red the paths that cross a line at any look and stop there. Add a note: with 1 look 5% of paths cross, with 10 looks about 19% do."

### 8.3 Three honest ways to monitor

**1. Fixed horizon.** Compute the sample size, run to it, look once. Simple, and what most teams should do. Peeking is allowed for *monitoring problems* (SRM, crashes, guardrails) but not for deciding the primary result.

**2. Group-sequential designs with spending.** Plan `K` looks in advance and use **stricter thresholds at each look** so that the overall false-positive rate stays at 5%. Two classic shapes:

- **Pocock**: the same critical value `c` at every look.
- **O'Brien-Fleming**: a very high threshold early (`c·sqrt(K/k)` at look `k`), falling to nearly the usual value at the end. It rarely stops early, but costs almost no power.

The constants have no neat formula for general `K`; we find them by simulating the null.

```python run
def sequential_boundaries(K, alpha=0.05, sims=400_000, seed=0):
    r = np.random.default_rng(seed)
    S = r.normal(size=(sims, K)).cumsum(1)
    Z = S / np.sqrt(np.arange(1, K + 1))
    # Pocock: constant c with P(max_k |Z_k| > c) = alpha
    c_pocock = np.quantile(np.abs(Z).max(1), 1 - alpha)
    # O'Brien-Fleming: boundaries c * sqrt(K/k): find c with P(any |Z_k| > c*sqrt(K/k)) = alpha
    scaled = (np.abs(Z) * np.sqrt(np.arange(1, K + 1) / K)).max(1)
    c_obf = np.quantile(scaled, 1 - alpha)
    return c_pocock, c_obf

K = 5
c_p, c_o = sequential_boundaries(K)
bounds = pd.DataFrame({"look": range(1, K + 1), "fixed-horizon (invalid if repeated)": 1.96, "Pocock": c_p, "O'Brien-Fleming": c_o * np.sqrt(K / np.arange(1, K + 1))})
print(bounds.round(3).to_string(index=False))
print("(published values for 5 looks: Pocock 2.413, O'Brien-Fleming 4.56 at look 1 falling to 2.04 at look 5)")
```
```text
 look  fixed-horizon (invalid if repeated)  Pocock  O'Brien-Fleming
    1                               1.9600  2.4140           4.5650
    2                               1.9600  2.4140           3.2280
    3                               1.9600  2.4140           2.6360
    4                               1.9600  2.4140           2.2830
    5                               1.9600  2.4140           2.0420
(published values for 5 looks: Pocock 2.413, O'Brien-Fleming 4.56 at look 1 falling to 2.04 at look 5)
```

Now check what these thresholds do: type I error under the null, and power and stopping time under a real effect.

```python run
def evaluate_design(K, thresholds, effect, per_look=280, sims=20_000, seed=3):
    r = np.random.default_rng(seed)
    d = (r.normal(size=(sims, K, per_look)) + effect).sum(2)             # standardised pair differences; effect in std units per pair
    n = per_look * np.arange(1, K + 1)
    Z = d.cumsum(1) / np.sqrt(n)
    crossed = np.abs(Z) > thresholds[None, :]
    stopped = crossed.any(1)
    first = np.where(stopped, crossed.argmax(1), K - 1)
    return float(stopped.mean()), float(((first + 1) / K).mean())            # P(declare a win), mean fraction of the planned sample used

designs = {"fixed horizon, one look at the end": np.r_[np.full(K - 1, np.inf), 1.96], "peeking at 1.96 (invalid)": np.full(K, 1.96),
           "Pocock": np.full(K, c_p), "O'Brien-Fleming": c_o * np.sqrt(K / np.arange(1, K + 1))}
effect = 0.075                                                           # with 5 x 280 = 1,400 pairs a fixed-horizon test has about 80% power
rows = []
for name, th in designs.items():
    t1, _ = evaluate_design(K, th, 0.0)
    pw, frac = evaluate_design(K, th, effect)
    rows.append((name, t1, pw, frac))
print(pd.DataFrame(rows, columns=["design (5 looks)", "false-positive rate (no effect)", "power (real effect)", "mean share of the sample used (real effect)"]).set_index("design (5 looks)").round(3).to_string())
```
```text
                                    false-positive rate (no effect)  power (real effect)  mean share of the sample used (real effect)
design (5 looks)                                                                                                                     
fixed horizon, one look at the end                           0.0490               0.8030                                       1.0000
peeking at 1.96 (invalid)                                    0.1420               0.8510                                       0.5760
Pocock                                                       0.0490               0.7120                                       0.7060
O'Brien-Fleming                                              0.0490               0.7910                                       0.8000
```

Read it carefully. Naive peeking has the highest "power", but only because it also has an inflated false-positive rate; it is not a fair comparison. Among the **valid** designs (false-positive rate 0.05), O'Brien-Fleming keeps almost all of the power of the fixed-horizon test (0.79 against 0.80) and uses about 80% of the planned sample on average when the effect is real; Pocock stops earlier (about 71% of the sample) but pays with less power (0.71). Naive peeking shows 0.85 power and a 14% false-positive rate: not a fair comparison. The price of being allowed to look is a slightly larger maximum sample, or a little power.

**3. Always-valid inference (mixture sequential tests).** The group-sequential test needs a fixed number of looks. An **always-valid p-value** stays valid under continuous monitoring at *any* time, so a dashboard can be watched all day. The mixture sequential probability ratio test (mSPRT) for a mean difference `θ` with known standard deviation `σ` of one pair difference mixes over a normal prior `θ ~ N(0, τ²)`:

```text
Λ_n = sqrt( σ² / (σ² + n τ²) ) · exp( n² τ² d̄² / ( 2 σ² (σ² + n τ²) ) )          reject H0 as soon as Λ_n ≥ 1/α
```

By a martingale argument (Ville's inequality) `P(Λ_n ≥ 1/α for some n) ≤ α` under the null, however often you look.

```python run
def msprt_lambda(dbar, n, sigma=1.0, tau=0.1):
    return np.sqrt(sigma ** 2 / (sigma ** 2 + n * tau ** 2)) * np.exp(n ** 2 * tau ** 2 * dbar ** 2 / (2 * sigma ** 2 * (sigma ** 2 + n * tau ** 2)))

def msprt_run(effect, n_max=5000, sims=3000, tau=0.1, alpha=0.05, seed=4):
    r = np.random.default_rng(seed)
    x = (r.normal(size=(sims, n_max)) + effect).cumsum(1)
    n = np.arange(1, n_max + 1)
    lam = msprt_lambda(x / n, n, tau=tau)
    hit = lam >= 1 / alpha
    stopped = hit.any(1)
    t = np.where(stopped, hit.argmax(1) + 1, n_max)
    return float(stopped.mean()), float(np.median(t[stopped])) if stopped.any() else float("nan"), float(hit[:, :1396].any(1).mean())

null_rate, _, _ = msprt_run(0.0)
pw, med_n, by_1396 = msprt_run(0.075)
print(f"mSPRT monitored after EVERY observation (5000 looks): false-positive rate {null_rate:.3f} (guarantee: <= 0.05)")
print(f"with a real effect of 0.075: detected in {pw:.2f} of runs within 5000 pairs; median stopping time {med_n:.0f} pairs")
print("a fixed-horizon test needs about", math.ceil((1.96 + 0.8416) ** 2 / 0.075 ** 2), "pairs for 80% power; the mSPRT has detected the effect in only", round(by_1396, 2), "of runs by that point")
```
```text
mSPRT monitored after EVERY observation (5000 looks): false-positive rate 0.028 (guarantee: <= 0.05)
with a real effect of 0.075: detected in 0.99 of runs within 5000 pairs; median stopping time 1262 pairs
a fixed-horizon test needs about 1396 pairs for 80% power; the mSPRT has detected the effect in only 0.56 of runs by that point
```

Continuous monitoring has a legitimate form, and its price is paid in power. At the sample size where the fixed-horizon test has 80% power, the always-valid test has detected the effect in only 56% of runs; it catches up later (99% by 5,000 pairs). That is the cost of staying valid against every possible stopping time. Choose it when decisions are time-critical or users will look regardless.

### 8.4 Practical rules about peeking

1. Decide the **stopping rule** before the experiment: a fixed horizon, a group-sequential plan with its thresholds, or an always-valid test.
2. Looking is not forbidden; **deciding** on a look is. Watch for SRM, errors, latency; do not stop for a promising primary metric.
3. Stopping early for **harm** is a separate and legitimate rule (a guardrail with its own sequential boundary).
4. Stopping early on a "win" **overestimates** the effect (you stop when noise happens to favour you). If an effect estimate matters, use a design that corrects for it or confirm it.
5. Never extend a disappointing test "to get more data" without having planned it: that is peeking with a second chance.

## 9. A Bayesian view, briefly

### 9.1 Posterior distributions for a conversion rate

Bayesian A/B testing treats each arm's conversion rate `p` as unknown with a **prior** distribution, updates it with the data, and reports statements such as "the probability that the treatment is better is 96%". For conversion data the Beta distribution is the natural prior: with a `Beta(a, b)` prior and `x` successes in `n` trials, the posterior is `Beta(a + x, b + n − x)`.

```python run
def bayes_ab(x_c, n_c, x_t, n_t, a=1, b=1, draws=400_000, seed=0):
    r = np.random.default_rng(seed)
    pc = r.beta(a + x_c, b + n_c - x_c, draws); pt = r.beta(a + x_t, b + n_t - x_t, draws)
    diff = pt - pc
    return {"P(treatment better)": float((diff > 0).mean()), "posterior mean lift": float(diff.mean()),
            "95% credible interval": (float(np.quantile(diff, 0.025)), float(np.quantile(diff, 0.975))),
            "expected loss if we ship": float(np.maximum(-diff, 0).mean()), "expected loss if we do not": float(np.maximum(diff, 0).mean())}

res = bayes_ab(1000, 10_000, 1060, 10_000)
for k, v in res.items():
    print(f"{k:28s}", v if isinstance(v, tuple) else round(v, 5))
freq = two_prop_test(1000, 10_000, 1060, 10_000)
print(f"\nfrequentist for the same data: two-sided p = {freq['p_value']:.4f} -> one-sided p = {freq['p_value'] / 2:.4f}; 1 - one-sided p = {1 - freq['p_value'] / 2:.4f}")
```
```text
P(treatment better)          0.91887
posterior mean lift          0.00601
95% credible interval        (-0.002422845312266058, 0.014434527153916849)
expected loss if we ship     0.00016
expected loss if we do not   0.00617

frequentist for the same data: two-sided p = 0.1628 -> one-sided p = 0.0814; 1 - one-sided p = 0.9186
```

With a flat prior, `P(treatment better)` is close to `1 − (one-sided p-value)`: the two views often agree numerically while differing in meaning. The Bayesian summary is easier to explain ("92% likely to be better") and supports a **decision-theoretic** rule: ship when the expected loss is smaller than a cost threshold you set.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw two Beta posterior density curves for conversion rate on one axis: control with 1,000 conversions out of 10,000 (Beta(1001, 9001)) and treatment with 1,060 out of 10,000 (Beta(1061, 8941)), from 0.09 to 0.12. Shade the overlap region, mark each mean, and add a second small plot of the difference distribution centred near 0.006 with the area above zero shaded (91.9%)."

### 9.2 The prior matters when data are few

```python run
for a_, b_, name in [(1, 1, "flat Beta(1,1)"), (10, 90, "informative Beta(10, 90): 'conversion is about 10%'")]:
    r = bayes_ab(7, 60, 12, 60, a_, b_)
    print(f"{name:55s} P(better) {r['P(treatment better)']:.3f}, posterior mean lift {r['posterior mean lift']:+.4f}")
```
```text
flat Beta(1,1)                                          P(better) 0.890, posterior mean lift +0.0807
informative Beta(10, 90): 'conversion is about 10%'     P(better) 0.807, posterior mean lift +0.0313
```

With 60 users per arm, the observed rates (11.7% and 20%) imply an 8-point lift. A flat prior believes it; an informative prior shrinks the estimate toward the believed rate. That shrinkage is a feature (small experiments overstate effects) as long as the prior is defensible and disclosed.

### 9.3 Bayes does not cure peeking

A common claim is that Bayesian methods "allow peeking". The truth is subtler: the posterior at each moment is a valid statement of belief given the data and the prior, and the optional stopping does not change it. But if you **stop when `P(better) > 95%`** and are judged by how often you launch a null change, the long-run false-launch rate is not 5%.

```python run
rng11 = np.random.default_rng(11)
def bayes_peek(K, per_look=500, sims=4000, thresh=0.95, base=0.10):
    xc = rng11.binomial(per_look, base, (sims, K)).cumsum(1); xt = rng11.binomial(per_look, base, (sims, K)).cumsum(1)
    n = per_look * np.arange(1, K + 1)
    pc, pt = (xc + 1) / (n + 2), (xt + 1) / (n + 2)
    sd = np.sqrt(pc * (1 - pc) / n + pt * (1 - pt) / n)
    prob_better = stats.norm.cdf((pt - pc) / sd)                                        # normal approximation to the posterior comparison
    return float((prob_better > thresh).any(1).mean())
print(pd.DataFrame({"looks K": [1, 5, 10, 20], "share of NULL experiments launched (stop when P(better) > 95%)": [bayes_peek(K) for K in [1, 5, 10, 20]]}).to_string(index=False))
```
```text
 looks K  share of NULL experiments launched (stop when P(better) > 95%)
       1                                                          0.0447
       5                                                          0.1440
      10                                                          0.1732
      20                                                          0.2238
```

Even with one look, "P(better) > 95%" launches about 5% of null experiments (it is a one-sided 5% test), and with more looks the rate climbs just like the p-value did. A Bayesian procedure that must have controlled error rates needs the same sequential design thinking. The difference between the schools is philosophical; the arithmetic of repeated looks applies to both.

### 9.4 Try it

1. In `bayes_ab`, use an informative prior centred on a 10% conversion with the weight of 1,000 users. How does the posterior for the 60-user experiment change?
2. Change `thresh` to 0.99 and 0.999 in `bayes_peek`. How strict must the threshold be for 20 looks to keep the false-launch rate near 5%?


## 10. Analysing a completed experiment end to end

### 10.1 The scenario and the order of work

A shop tested a redesigned checkout page. The pre-registered plan: **primary metric** = purchase conversion within 7 days; **guardrail** = page latency must not rise by more than 50 ms; **pre-registered segments** = platform (ios, android, web); planned 60,000 users in total, 50/50. Exploratory only: country.

The order of analysis matters. Each step gates the next:

```text
1 trust checks (SRM, balance)  ->  2 primary metric  ->  3 variance reduction  ->  4 guardrails  ->  5 pre-registered segments (corrected)
      ->  6 time pattern (novelty)  ->  7 exploratory analysis (labelled)  ->  8 decision
```

We simulate the data with a known truth: the redesign raises conversion by 1.5 points on iOS, 1.2 on Android, and has no effect on web; the effect is stronger in the first week (novelty, 1.5 times the average, falling to 0.8 times by week 3); latency rises by 30 ms.

```python run
def sim_experiment(n=60_000, seed=21):
    r = np.random.default_rng(seed)
    uid = np.arange(n)
    arm_ = np.array([bucket(u, "checkout-v2-final") < 500 for u in uid])                        # True = treatment
    platform = r.choice(["ios", "android", "web"], n, p=[.35, .35, .30])
    country = r.choice(["IN", "US", "UK", "DE", "FR", "BR", "JP", "AU"], n)
    pre_spend = r.lognormal(3.0, 1.0, n)                                                          # spend in the 30 days BEFORE the experiment
    week = r.integers(1, 5, n)                                                                    # week of first exposure (1..4)
    base = 0.05 + 0.06 * (np.log(pre_spend) - 3.0) / 3 + np.where(platform == "web", -0.01, 0.0)     # heavier spenders convert more
    effect = np.select([platform == "ios", platform == "android"], [0.015, 0.012], 0.0) * np.where(week == 1, 1.5, np.where(week == 2, 1.1, 0.8))
    p = np.clip(base + 0.05 + effect * arm_, 0.001, 0.99)
    converted = (r.random(n) < p).astype(int)
    latency = r.gamma(9, 22, n) + 30 * arm_                                                       # ms; the new page is 30 ms slower
    return pd.DataFrame({"user": uid, "arm": arm_.astype(int), "platform": platform, "country": country, "pre_spend": pre_spend,
                         "week": week, "converted": converted, "latency_ms": latency})

exp = sim_experiment()
print(exp.shape, "| overall conversion:", round(exp["converted"].mean(), 4))
print(exp.head(4).round(3).to_string(index=False))
```
```text
(60000, 8) | overall conversion: 0.1036
 user  arm platform country  pre_spend  week  converted  latency_ms
    0    0      web      DE    21.4450     3          0     91.1690
    1    1  android      BR    10.7420     1          0    151.2650
    2    1      web      JP     4.3530     4          0    199.1620
    3    1      ios      UK    48.9500     2          1    295.7850
```

### 10.2 Step 1: trust checks

```python run
n_c, n_t = int((exp.arm == 0).sum()), int((exp.arm == 1).sum())
chi2, p_srm = srm_check(n_c, n_t)
print(f"SRM: control {n_c:,}, treatment {n_t:,}, p-value {p_srm:.3f} -> {'FAIL' if p_srm < 0.001 else 'pass'}")
bal = []
for col in ["pre_spend", "week"]:
    x = np.log(exp[col]) if col == "pre_spend" else exp[col].astype(float)
    bal.append((col, smd(x.to_numpy(), exp.arm.to_numpy() == 1)))
for plat in ["ios", "android", "web"]:
    bal.append((f"share {plat}", smd((exp.platform == plat).to_numpy().astype(float), exp.arm.to_numpy() == 1)))
print(pd.DataFrame(bal, columns=["covariate", "standardised mean difference"]).round(3).to_string(index=False), "\n(all within +-0.05: balanced)")
```
```text
SRM: control 30,082, treatment 29,918, p-value 0.503 -> pass
    covariate  standardised mean difference
    pre_spend                       -0.0190
         week                       -0.0150
    share ios                        0.0100
share android                       -0.0000
    share web                       -0.0110 
(all within +-0.05: balanced)
```

### 10.3 Step 2: the primary metric

```python run
def arm_counts(df, col="converted"):
    c, t = df[df.arm == 0][col], df[df.arm == 1][col]
    return int(c.sum()), len(c), int(t.sum()), len(t)

r = two_prop_test(*arm_counts(exp))
print(f"control {r['p_control']:.4f} | treatment {r['p_treatment']:.4f} | lift {r['diff']:+.4f} points ({r['relative lift']:+.1%} relative)")
print(f"95% CI [{r['ci_low']:+.4f}, {r['ci_high']:+.4f}] | p-value {r['p_value']:.4f}")
mde = mde_prop(r["p_control"], len(exp) // 2)
print(f"with {len(exp) // 2:,} users per arm the minimum detectable effect was {mde:.4f} points -> the observed lift is {'above' if abs(r['diff']) > mde else 'below'} that")
```
```text
control 0.0994 | treatment 0.1078 | lift +0.0084 points (+8.5% relative)
95% CI [+0.0035, +0.0133] | p-value 0.0007
with 30,000 users per arm the minimum detectable effect was 0.0069 points -> the observed lift is above that
```

State it in words: the new page changes conversion by an estimated amount, with an interval that excludes zero (or not); and the interval, not just the p-value, is what the decision uses.

### 10.4 Step 3: variance reduction by regression adjustment

For a binary outcome the natural adjustment is a regression of the outcome on the arm and pre-experiment covariates. An OLS fit (a linear probability model) with robust standard errors gives the same kind of gain as CUPED.

```python run
exp["log_pre"] = np.log(exp["pre_spend"])
X0 = sm.add_constant(exp[["arm"]].astype(float))
X1 = sm.add_constant(pd.concat([exp[["arm", "log_pre"]].astype(float), pd.get_dummies(exp["platform"], drop_first=True, dtype=float)], axis=1))
m0 = sm.OLS(exp["converted"], X0).fit(cov_type="HC1")
m1 = sm.OLS(exp["converted"], X1).fit(cov_type="HC1")
print(f"unadjusted : effect {m0.params['arm']:+.4f}, se {m0.bse['arm']:.4f}, 95% CI [{m0.conf_int().loc['arm', 0]:+.4f}, {m0.conf_int().loc['arm', 1]:+.4f}]")
print(f"adjusted   : effect {m1.params['arm']:+.4f}, se {m1.bse['arm']:.4f}, 95% CI [{m1.conf_int().loc['arm', 0]:+.4f}, {m1.conf_int().loc['arm', 1]:+.4f}]")
print(f"the adjustment shrinks the standard error by {1 - m1.bse['arm'] / m0.bse['arm']:.1%}; the point estimate barely moves (as it must: the covariates are pre-treatment)")
print(f"R-squared of the pre-experiment covariates for the outcome: {sm.OLS(exp['converted'], X1.drop(columns='arm')).fit().rsquared:.4f}")
```
```text
unadjusted : effect +0.0084, se 0.0025, 95% CI [+0.0035, +0.0133]
adjusted   : effect +0.0087, se 0.0025, 95% CI [+0.0039, +0.0136]
the adjustment shrinks the standard error by 0.3%; the point estimate barely moves (as it must: the covariates are pre-treatment)
R-squared of the pre-experiment covariates for the outcome: 0.0055
```

The gain is small here, and that is typical for a yes/no outcome: past spend predicts conversion only weakly, and the Bernoulli noise of a single purchase decision dominates. Adjustment pays off when the outcome is continuous and strongly predicted by its own past, as in the spend example of section 5.1. Always report it as the same experiment, analysed more sharply.

(Adjust only for covariates measured **before** assignment. Adjusting for anything the treatment could change, such as post-exposure engagement, biases the estimate; section 11.8.)

### 10.5 Step 4: guardrails and non-inferiority

For a guardrail the question is not "is there a difference?" but "is the harm smaller than the margin we can tolerate?". That is a **non-inferiority** test: the harm is acceptable if the **upper** bound of the interval for the increase in latency is below the margin.

```python run
lat = welch(exp.loc[exp.arm == 0, "latency_ms"].to_numpy(), exp.loc[exp.arm == 1, "latency_ms"].to_numpy(), alpha=0.10)      # 90% two-sided = 95% one-sided
margin = 50.0
print(f"latency: control {exp.loc[exp.arm == 0, 'latency_ms'].mean():.1f} ms, treatment {exp.loc[exp.arm == 1, 'latency_ms'].mean():.1f} ms | increase {lat['diff']:+.1f} ms, one-sided 95% upper bound {lat['ci_high']:.1f} ms")
print(f"margin {margin:.0f} ms -> guardrail {'PASSES (harm is confidently below the margin)' if lat['ci_high'] < margin else 'FAILS or is inconclusive'}")
print(f"note: the increase IS significantly greater than zero (p {'< 1e-12' if lat['p_value'] < 1e-12 else '= %.1e' % lat['p_value']}); that does not matter if it is below the tolerance we agreed")
```
```text
latency: control 197.8 ms, treatment 227.9 ms | increase +30.2 ms, one-sided 95% upper bound 31.0 ms
margin 50 ms -> guardrail PASSES (harm is confidently below the margin)
note: the increase IS significantly greater than zero (p < 1e-12); that does not matter if it is below the tolerance we agreed
```

### 10.6 Step 5: pre-registered segments, corrected

```python run
rows = []
for plat in ["ios", "android", "web"]:
    sub = exp[exp.platform == plat]
    rr = two_prop_test(*arm_counts(sub))
    rows.append((plat, len(sub), rr["diff"], rr["ci_low"], rr["ci_high"], rr["p_value"]))
seg = pd.DataFrame(rows, columns=["platform", "users", "lift", "ci_low", "ci_high", "p_value"])
seg["p (Holm, 3 segments)"] = multipletests(seg["p_value"], method="holm")[1]
print(seg.round(4).to_string(index=False))
```
```text
platform  users    lift  ci_low  ci_high  p_value  p (Holm, 3 segments)
     ios  20916  0.0183  0.0098   0.0267   0.0000                0.0001
 android  20903  0.0115  0.0031   0.0199   0.0071                0.0141
     web  18181 -0.0068 -0.0153   0.0017   0.1153                0.1153
```

The interval for each segment is wide (about a third of the users each), and the web segment's interval includes zero, as it should since we planted no effect there. Do not read "significant on iOS, not significant on web" as "the effect differs between platforms" without testing the **difference**, that is, the interaction:

```python run
Xi = sm.add_constant(pd.DataFrame({"arm": exp.arm.astype(float), "ios": (exp.platform == "ios").astype(float), "web": (exp.platform == "web").astype(float)}))
Xi["arm_x_ios"], Xi["arm_x_web"] = Xi["arm"] * Xi["ios"], Xi["arm"] * Xi["web"]
mi = sm.OLS(exp["converted"], Xi).fit(cov_type="HC1")
print("treatment effect on the reference platform (android): %+.4f" % mi.params["arm"])
print("difference for web vs android: %+.4f (p = %.4f) | difference for ios vs android: %+.4f (p = %.4f)" % (mi.params["arm_x_web"], mi.pvalues["arm_x_web"], mi.params["arm_x_ios"], mi.pvalues["arm_x_ios"]))
```
```text
treatment effect on the reference platform (android): +0.0115
difference for web vs android: -0.0183 (p = 0.0026) | difference for ios vs android: +0.0068 (p = 0.2647)
```

### 10.7 Step 6: time pattern and novelty

```python run
rows = []
for w in [1, 2, 3, 4]:
    sub = exp[exp.week == w]
    rr = two_prop_test(*arm_counts(sub))
    rows.append((w, len(sub), rr["diff"], rr["ci_low"], rr["ci_high"]))
print(pd.DataFrame(rows, columns=["week of first exposure", "users", "lift", "ci_low", "ci_high"]).round(4).to_string(index=False))
```
```text
 week of first exposure  users   lift  ci_low  ci_high
                      1  15029 0.0115  0.0016   0.0214
                      2  14964 0.0088 -0.0009   0.0186
                      3  15009 0.0109  0.0012   0.0206
                      4  14998 0.0021 -0.0075   0.0118
```

The weekly estimates are similar for weeks 1 to 3 and lower in week 4, but every interval overlaps all the others. We planted a modest fade (a multiplier falling from 1.5 to 0.8 over the weeks), and a sample of 15,000 users per week is too small to show a change of that size clearly. That is a general lesson: **a novelty effect that matters can still be invisible in a test of this size**. The honest report says: "we see no strong sign of a fade, but we could not have seen a moderate one". A longer test, or a holdout kept after launch, answers it.

### 10.8 Step 7: exploratory analysis, clearly labelled

```python run
rows = []
for c in sorted(exp.country.unique()):
    sub = exp[exp.country == c]
    rr = two_prop_test(*arm_counts(sub))
    rows.append((c, len(sub), rr["diff"], rr["p_value"]))
ex = pd.DataFrame(rows, columns=["country", "users", "lift", "p_value"])
ex["p (Benjamini-Hochberg)"] = multipletests(ex["p_value"], method="fdr_bh")[1]
print(ex.sort_values("p_value").round(4).to_string(index=False))
print("EXPLORATORY: 8 unplanned comparisons; any apparent winner is a hypothesis for the next experiment, not a result.")
```
```text
country  users   lift  p_value  p (Benjamini-Hochberg)
     US   7513 0.0157   0.0260                  0.2078
     FR   7515 0.0119   0.0909                  0.3638
     BR   7512 0.0089   0.1958                  0.4107
     UK   7679 0.0089   0.2054                  0.4107
     AU   7513 0.0061   0.3743                  0.5049
     DE   7495 0.0062   0.3931                  0.5049
     JP   7503 0.0046   0.5044                  0.5049
     IN   7270 0.0048   0.5049                  0.5049
EXPLORATORY: 8 unplanned comparisons; any apparent winner is a hypothesis for the next experiment, not a result.
```

### 10.9 Step 8: the decision memo

```python run
wins = seg[(seg["lift"] > 0) & (seg["p (Holm, 3 segments)"] < 0.05)]["platform"].tolist()
rec = ("SHIP to " + " and ".join(wins) + "; no demonstrated benefit on the other platforms, so do not claim one.") if wins else "DO NOT SHIP: no platform shows a benefit after correction."
memo = f"""DECISION MEMO: checkout redesign
Trust checks   : SRM p = {p_srm:.2f} (pass); pre-experiment covariates balanced.
Primary metric : conversion {r['p_control']:.2%} -> {r['p_treatment']:.2%}; lift {r['diff']*100:+.2f} points, 95% CI [{r['ci_low']*100:+.2f}, {r['ci_high']*100:+.2f}] (adjusted CI [{m1.conf_int().loc['arm', 0]*100:+.2f}, {m1.conf_int().loc['arm', 1]*100:+.2f}]).
Guardrail      : latency +{lat['diff']:.0f} ms (one-sided 95% upper bound {lat['ci_high']:.0f} ms) vs a {margin:.0f} ms tolerance: pass.
Segments (planned, Holm-corrected): ios {seg.loc[0, 'lift']*100:+.2f} pts (p={seg.loc[0, 'p (Holm, 3 segments)']:.3f}), android {seg.loc[1, 'lift']*100:+.2f} pts (p={seg.loc[1, 'p (Holm, 3 segments)']:.3f}), web {seg.loc[2, 'lift']*100:+.2f} pts (p={seg.loc[2, 'p (Holm, 3 segments)']:.2f}).
Caveats        : the effect looks larger in week 1; keep a 5% holdout after launch to measure the long-run effect. Country analysis is exploratory only.
Recommendation : {rec}"""
print(memo)
```
```text
DECISION MEMO: checkout redesign
Trust checks   : SRM p = 0.50 (pass); pre-experiment covariates balanced.
Primary metric : conversion 9.94% -> 10.78%; lift +0.84 points, 95% CI [+0.35, +1.33] (adjusted CI [+0.39, +1.36]).
Guardrail      : latency +30 ms (one-sided 95% upper bound 31 ms) vs a 50 ms tolerance: pass.
Segments (planned, Holm-corrected): ios +1.83 pts (p=0.000), android +1.15 pts (p=0.014), web -0.68 pts (p=0.12).
Caveats        : the effect looks larger in week 1; keep a 5% holdout after launch to measure the long-run effect. Country analysis is exploratory only.
Recommendation : SHIP to ios and android; no demonstrated benefit on the other platforms, so do not claim one.
```

Notice what the memo contains: numbers with intervals, the checks that were run, what was planned versus exploratory, a caveat, and an action that follows from the evidence rather than from the headline p-value.

### 10.10 Try it

1. Repeat the primary analysis using only the first week's users. How does the interval and the conclusion change? Why is "stop after week 1" dangerous?
2. Change the guardrail margin to 20 ms. What does the memo now say?

## 11. Causal inference without an experiment

### 11.1 When you cannot randomise

Sometimes an experiment is impossible or unethical (does smoking cause cancer?), too slow, or the change already happened (a price rise last quarter). **Causal inference** tries to estimate effects from observational data by making **assumptions** explicit. Every method below is only as good as those assumptions, and none can be verified from the data alone. That is the central, uncomfortable fact of the field.

### 11.2 The assumptions

| Assumption | Meaning | Fails when |
|---|---|---|
| **Consistency / SUTVA** | one well-defined treatment; one unit's treatment does not change another's outcome | spillovers, network effects, "treatment" means different things |
| **Ignorability (no unmeasured confounding)** | given the measured covariates `X`, treatment is as good as random: `Y(0), Y(1) ⟂ T | X` | something unmeasured drives both treatment and outcome |
| **Positivity (overlap)** | every kind of unit has some chance of both treatments: `0 < P(T=1 | X) < 1` | a group is always or never treated |

### 11.3 An observational dataset with a known answer

Customers choose to subscribe to a premium plan. Higher-income and older customers subscribe more, and also spend more regardless. The true effect of the plan on monthly spend is +5.

```python run
rng = np.random.default_rng(31)
n = 40_000
age = rng.normal(40, 10, n); income = rng.lognormal(10.5, 0.4, n)
z_inc, z_age = (np.log(income) - 10.5) / 0.4, (age - 40) / 10
p_treat = 1 / (1 + np.exp(-(-0.4 + 1.2 * z_inc + 0.6 * z_age)))
T = (rng.random(n) < p_treat).astype(int)
TRUE = 5.0
Y = 50 + 9 * z_inc + 4 * z_age + TRUE * T + rng.normal(0, 8, n)
obs = pd.DataFrame({"T": T, "Y": Y, "age": age, "z_inc": z_inc, "z_age": z_age, "income": income})
print(f"treated share {T.mean():.2f} | true effect {TRUE}")
print(f"naive difference in means: {Y[T == 1].mean() - Y[T == 0].mean():.2f}   <- biased upward by the confounders")
print(f"mean income score: treated {z_inc[T == 1].mean():+.2f}, untreated {z_inc[T == 0].mean():+.2f} | mean age score: treated {z_age[T == 1].mean():+.2f}, untreated {z_age[T == 0].mean():+.2f}")
```
```text
treated share 0.42 | true effect 5.0
naive difference in means: 14.83   <- biased upward by the confounders
mean income score: treated +0.51, untreated -0.39 | mean age score: treated +0.26, untreated -0.18
```

### 11.4 Method 1: regression adjustment

If we have measured all confounders and the outcome model is right, include them in the regression. The coefficient on `T` estimates the effect.

```python run
fit = sm.OLS(obs["Y"], sm.add_constant(obs[["T", "z_inc", "z_age"]])).fit(cov_type="HC1")
print(f"regression adjustment: effect {fit.params['T']:.3f} (se {fit.bse['T']:.3f}), 95% CI [{fit.conf_int().loc['T', 0]:.2f}, {fit.conf_int().loc['T', 1]:.2f}]  (truth {TRUE})")
wrong = sm.OLS(obs["Y"], sm.add_constant(obs[["T"]])).fit(cov_type="HC1")
print(f"leaving the confounders out : effect {wrong.params['T']:.3f}")
```
```text
regression adjustment: effect 4.984 (se 0.093), 95% CI [4.80, 5.17]  (truth 5.0)
leaving the confounders out : effect 14.832
```

### 11.5 Method 2: propensity scores

The **propensity score** `e(x) = P(T = 1 | X = x)` is the probability of being treated given the covariates. The key result (Rosenbaum and Rubin): if ignorability holds given `X`, it also holds given `e(X)` alone, so a single number can summarise all the confounding. Estimate it with a model of treatment (logistic regression here), then use it in one of three ways.

```python run
from sklearn.linear_model import LogisticRegression
ps_model = LogisticRegression(C=1e6, max_iter=2000).fit(obs[["z_inc", "z_age"]], obs["T"])
obs["ps"] = ps_model.predict_proba(obs[["z_inc", "z_age"]])[:, 1]
print("propensity score quantiles, treated  :", np.quantile(obs.loc[obs["T"] == 1, "ps"], [.01, .25, .5, .75, .99]).round(3))
print("propensity score quantiles, untreated:", np.quantile(obs.loc[obs["T"] == 0, "ps"], [.01, .25, .5, .75, .99]).round(3))
print("overlap check: share of units with a propensity below 0.02 or above 0.98:", round(float(((obs.ps < .02) | (obs.ps > .98)).mean()), 4))
```
```text
propensity score quantiles, treated  : [0.09  0.399 0.587 0.756 0.955]
propensity score quantiles, untreated: [0.022 0.149 0.275 0.455 0.843]
overlap check: share of units with a propensity below 0.02 or above 0.98: 0.0056
```

**Overlap** is the first thing to check: if treated and untreated units have propensity scores in non-overlapping ranges, there are no comparable units for some region and no method can fix that.

**(a) Inverse probability weighting (IPW).** Weight each unit by the inverse of the probability of the treatment it received: `w = T/e + (1−T)/(1−e)`. This builds a pseudo-population in which treatment is independent of the covariates.

```python run
w = np.where(obs["T"] == 1, 1 / obs["ps"], 1 / (1 - obs["ps"]))
ate_ipw = np.average(obs.loc[obs["T"] == 1, "Y"], weights=w[obs["T"] == 1]) - np.average(obs.loc[obs["T"] == 0, "Y"], weights=w[obs["T"] == 0])
print(f"IPW estimate: {ate_ipw:.3f}  (truth {TRUE})")
print(f"largest weight {w.max():.1f}; effective sample size {w.sum() ** 2 / (w ** 2).sum():,.0f} of {len(w):,}")
wt = np.clip(w, None, np.quantile(w, 0.99))
ate_trim = np.average(obs.loc[obs["T"] == 1, "Y"], weights=wt[obs["T"] == 1]) - np.average(obs.loc[obs["T"] == 0, "Y"], weights=wt[obs["T"] == 0])
print(f"with weights capped at their 99th percentile: {ate_trim:.3f}   <- capping adds bias: it trades bias for variance")
# balance after weighting
def wsmd(x, t, w):
    m1, m0 = np.average(x[t == 1], weights=w[t == 1]), np.average(x[t == 0], weights=w[t == 0])
    v = (x[t == 1].var(ddof=1) + x[t == 0].var(ddof=1)) / 2
    return (m1 - m0) / math.sqrt(v)
rows = [(c, wsmd(obs[c].to_numpy(), obs["T"].to_numpy(), np.ones(n)), wsmd(obs[c].to_numpy(), obs["T"].to_numpy(), w)) for c in ["z_inc", "z_age"]]
print(pd.DataFrame(rows, columns=["covariate", "SMD before weighting", "SMD after weighting"]).round(3).to_string(index=False))
```
```text
IPW estimate: 5.059  (truth 5.0)
largest weight 44.0; effective sample size 22,728 of 40,000
with weights capped at their 99th percentile: 6.118   <- capping adds bias: it trades bias for variance
covariate  SMD before weighting  SMD after weighting
    z_inc                1.0020               0.0070
    z_age                0.4490              -0.0070
```

Always **check balance after** adjusting: the whole point is to make treated and untreated comparable, and the standardised differences tell you whether it worked. Extreme weights (units with a propensity near 0 or 1) make the estimate unstable: here the largest weight is 44 and the effective sample size is only 57% of the real one. Capping the weights reduces the variance but **adds bias** (the capped estimate above is further from the truth), so trimming is a trade, not a free fix; report the effective sample size and how sensitive the answer is to the cap.

**(b) Matching.** For each treated unit find an untreated unit with a similar propensity score and compare outcomes.

```python run
from sklearn.neighbors import NearestNeighbors
treated_idx = np.flatnonzero(obs["T"] == 1); control_idx = np.flatnonzero(obs["T"] == 0)
nn = NearestNeighbors(n_neighbors=1).fit(obs.loc[control_idx, ["ps"]])
dist, j = nn.kneighbors(obs.loc[treated_idx, ["ps"]])
matched = control_idx[j.ravel()]
att = (obs["Y"].to_numpy()[treated_idx] - obs["Y"].to_numpy()[matched]).mean()
print(f"1-to-1 nearest-neighbour matching on the propensity score (with replacement): effect on the treated {att:.3f} (truth {TRUE}); mean distance {dist.mean():.4f}")
print("balance on the matched sample, SMD:", {c: round(float((obs[c].to_numpy()[treated_idx].mean() - obs[c].to_numpy()[matched].mean()) / obs[c].std()), 3) for c in ["z_inc", "z_age"]})
```
```text
1-to-1 nearest-neighbour matching on the propensity score (with replacement): effect on the treated 5.067 (truth 5.0); mean distance 0.0001
balance on the matched sample, SMD: {'z_inc': 0.001, 'z_age': -0.002}
```

**(c) Stratification**: cut the propensity score into bins, compare within each bin, and average.

```python run
obs["stratum"] = pd.qcut(obs["ps"], 10, labels=False)
by = obs.groupby("stratum").apply(lambda g: pd.Series({"effect": g.loc[g["T"] == 1, "Y"].mean() - g.loc[g["T"] == 0, "Y"].mean(), "n": len(g)}))
print(f"stratification on propensity deciles: {np.average(by['effect'], weights=by['n']):.3f} (truth {TRUE})")
obs['stratum20'] = pd.qcut(obs['ps'], 40, labels=False)
by40 = obs.groupby('stratum20').apply(lambda g: pd.Series({'effect': g.loc[g['T'] == 1, 'Y'].mean() - g.loc[g['T'] == 0, 'Y'].mean(), 'n': len(g)}))
print(f"with 40 strata: {np.average(by40['effect'], weights=by40['n']):.3f}")
```
```text
stratification on propensity deciles: 5.449 (truth 5.0)
with 40 strata: 5.090
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a diagram of propensity-score weighting on 40,000 users. Top: two histograms of propensity score from 0 to 1, treated (median 0.587) and untreated (median 0.275), overlapping. Bottom: the same histograms after inverse probability weighting, where the two shapes match. Add a small table of standardised mean difference before and after: z_inc 1.002 to 0.007, z_age 0.449 to -0.007."

### 11.6 Doubly robust estimation

Regression needs the **outcome model** to be right; IPW needs the **propensity model** to be right. The **augmented IPW (AIPW)** estimator combines them and is consistent if *either* is right.

```python run
X_out = sm.add_constant(obs[["z_inc", "z_age"]])
m1_, m0_ = sm.OLS(obs.loc[obs["T"] == 1, "Y"], X_out[obs["T"] == 1]).fit(), sm.OLS(obs.loc[obs["T"] == 0, "Y"], X_out[obs["T"] == 0]).fit()
mu1, mu0 = m1_.predict(X_out), m0_.predict(X_out)
e = obs["ps"].to_numpy()
aipw = np.mean(mu1 - mu0 + obs["T"] * (obs["Y"] - mu1) / e - (1 - obs["T"]) * (obs["Y"] - mu0) / (1 - e))
print(f"AIPW (doubly robust): {aipw:.3f} (truth {TRUE})")
boots = []
for _ in range(200):
    i = rng.integers(0, n, n); d = obs.iloc[i]
    ps_ = LogisticRegression(C=1e6, max_iter=500).fit(d[["z_inc", "z_age"]], d["T"]).predict_proba(d[["z_inc", "z_age"]])[:, 1]
    Xd = sm.add_constant(d[["z_inc", "z_age"]])
    a1, a0 = sm.OLS(d.loc[d["T"] == 1, "Y"], Xd[d["T"] == 1]).fit(), sm.OLS(d.loc[d["T"] == 0, "Y"], Xd[d["T"] == 0]).fit()
    u1, u0 = a1.predict(Xd), a0.predict(Xd)
    boots.append(np.mean(u1 - u0 + d["T"] * (d["Y"] - u1) / ps_ - (1 - d["T"]) * (d["Y"] - u0) / (1 - ps_)))
print(f"bootstrap 95% interval: [{np.quantile(boots, .025):.2f}, {np.quantile(boots, .975):.2f}]")
```
```text
AIPW (doubly robust): 5.027 (truth 5.0)
bootstrap 95% interval: [4.80, 5.20]
```

### 11.7 The limit: unmeasured confounding

All of the above assume we measured every confounder. Add a hidden driver (say, "enthusiasm") that raises both subscription and spending, and delete it from the data.

```python run
rng = np.random.default_rng(32)
enth = rng.normal(0, 1, n)
p2 = 1 / (1 + np.exp(-(-0.4 + 1.2 * z_inc + 0.6 * z_age + 1.0 * enth)))
T2 = (rng.random(n) < p2).astype(int)
Y2 = 50 + 9 * z_inc + 4 * z_age + 6 * enth + TRUE * T2 + rng.normal(0, 8, n)
d2 = pd.DataFrame({"T": T2, "Y": Y2, "z_inc": z_inc, "z_age": z_age, "enth": enth})
known = sm.OLS(d2["Y"], sm.add_constant(d2[["T", "z_inc", "z_age"]])).fit().params["T"]
oracle = sm.OLS(d2["Y"], sm.add_constant(d2[["T", "z_inc", "z_age", "enth"]])).fit().params["T"]
print(f"adjusting for everything we can measure (income, age): {known:.2f}   <- still biased")
print(f"if enthusiasm had been measured (oracle)            : {oracle:.2f}   (truth {TRUE})")
```
```text
adjusting for everything we can measure (income, age): 10.00   <- still biased
if enthusiasm had been measured (oracle)            : 4.99   (truth 5.0)
```

No statistical method can see a confounder that is not in the data. That is why **observational causal estimates require a justification from domain knowledge** (a causal diagram), a **sensitivity analysis** ("how strong would an unmeasured confounder have to be to explain this effect away?"), and ideally a design (a natural experiment, section 11.9) that removes the confounder by construction.

### 11.8 What to adjust for: confounders, mediators and colliders

More covariates are **not** always better. Sketch the causal structure first:

| Variable type | Relation | Adjust? |
|---|---|---|
| **Confounder** | causes both treatment and outcome | **yes** (it opens a back-door path) |
| **Mediator** | on the path from treatment to outcome (treatment -> mediator -> outcome) | **no**, if you want the total effect (you remove the effect you are measuring) |
| **Collider** | caused by both treatment and outcome | **no** (adjusting creates a spurious association) |
| **Pre-treatment predictor of the outcome only** | affects the outcome, not the treatment | yes: harmless and reduces variance (CUPED) |

```python run
rng = np.random.default_rng(33)
T3 = rng.integers(0, 2, n)                                                       # randomised
M = 2.0 * T3 + rng.normal(0, 1, n)                                               # a mediator: the treatment raises engagement ...
Y3 = 3.0 * M + rng.normal(0, 1, n)                                               # ... and engagement raises revenue. Total effect = 2*3 = 6
C = 1.0 * T3 + 1.0 * Y3 + rng.normal(0, 1, n)                                    # a collider: caused by both
d3 = pd.DataFrame({"T": T3, "M": M, "Y": Y3, "C": C})
for name, cols in [("no adjustment (total effect, correct: 6)", ["T"]), ("adjust for the mediator M", ["T", "M"]), ("adjust for the collider C", ["T", "C"])]:
    print(f"{name:45s} effect on T: {sm.OLS(d3['Y'], sm.add_constant(d3[cols])).fit().params['T']:+.2f}")
```
```text
no adjustment (total effect, correct: 6)      effect on T: +5.98
adjust for the mediator M                     effect on T: +0.01
adjust for the collider C                     effect on T: -0.36
```

Adjusting for the mediator wipes out the effect (+6 becomes about 0); adjusting for the collider replaces a large positive effect by a small negative one, an association manufactured by the adjustment itself. This also explains the rule "adjust only for pre-treatment variables" in section 10.4.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw three small causal graphs with arrows between nodes T (treatment), M, C and Y (outcome). Graph 1: T -> M -> Y (M is a mediator, adjusting removes the effect: +6 becomes +0.01). Graph 2: T -> C <- Y (C is a collider, adjusting gives -0.36). Graph 3: T -> Y with no adjustment, correct total effect +5.98. Mark the adjusted variable with a box in each graph."

### 11.9 Designs that remove confounding: natural experiments

**Difference-in-differences (DiD).** A policy is introduced in some places (treated) but not others (control). Compare the *change* over time in the treated with the *change* in the control. The assumption: without the policy, both groups would have changed in parallel (**parallel trends**).

```python run
rng = np.random.default_rng(42)
stores = pd.DataFrame({"store": np.arange(80), "treated": np.repeat([1, 0], 40), "level": rng.normal(100, 15, 80)})
stores["level"] += 12 * stores["treated"]                                         # treated stores were already bigger (a level difference)
rows = []
for t in range(12):                                                               # 12 weeks; the policy starts in week 6 in treated stores
    for _, s in stores.iterrows():
        post = int(t >= 6)
        rows.append((int(s.store), t, int(s.treated), post, s.level + 1.5 * t + 6.0 * post * s.treated + rng.normal(0, 4)))      # common trend 1.5/week; true effect +6
panel = pd.DataFrame(rows, columns=["store", "week", "treated", "post", "sales"])
g = panel.groupby(["treated", "post"])["sales"].mean().unstack()
print(g.round(2).to_string())
before_after = g.loc[1, 1] - g.loc[1, 0]
cross = g.loc[1, 1] - g.loc[0, 1]
did = (g.loc[1, 1] - g.loc[1, 0]) - (g.loc[0, 1] - g.loc[0, 0])
print(f"treated before vs after   : {before_after:+.2f}   <- includes the common time trend")
print(f"treated vs control (after): {cross:+.2f}   <- includes the pre-existing level difference")
print(f"difference-in-differences : {did:+.2f}   (truth +6.0)")
fit = sm.OLS(panel["sales"], sm.add_constant(pd.DataFrame({"treated": panel.treated, "post": panel.post, "treated_x_post": panel.treated * panel.post}).astype(float))).fit(cov_type="cluster", cov_kwds={"groups": panel["store"]})
print(f"regression form: coefficient on treated x post {fit.params['treated_x_post']:+.2f}, clustered standard error {fit.bse['treated_x_post']:.2f}")
```
```text
post           0        1
treated                  
0       103.9000 112.8500
1       116.1700 131.0800
treated before vs after   : +14.90   <- includes the common time trend
treated vs control (after): +18.23   <- includes the pre-existing level difference
difference-in-differences : +5.96   (truth +6.0)
regression form: coefficient on treated x post +5.96, clustered standard error 0.53
```

Check the assumption you can check, **parallel pre-trends**: in the weeks before the policy the treated-minus-control gap should be flat.

```python run
gap = panel.groupby(["week", "treated"])["sales"].mean().unstack()
gap["treated - control"] = gap[1] - gap[0]
print(gap["treated - control"].round(2).to_frame().T.to_string())
print("pre-policy gap (weeks 0-5) std:", round(float(gap["treated - control"].iloc[:6].std()), 2), "| a clear trend before the policy would break the design")
```
```text
week                   0       1       2       3       4       5       6       7       8       9       10      11
treated - control 11.7000 13.2700 12.4900 12.5100 10.9300 12.7500 18.1800 18.9700 17.9200 17.7300 17.6200 18.9600
pre-policy gap (weeks 0-5) std: 0.83 | a clear trend before the policy would break the design
```

Use clustered standard errors (here by store): the repeated weekly measurements of one store are correlated.

**Regression discontinuity (RD).** If treatment is assigned by a threshold on a score (a loyalty tier at 1,000 points, a scholarship at a test score), units just below and just above the cutoff are nearly identical; the jump in the outcome at the cutoff estimates the effect locally.

```python run
rng = np.random.default_rng(35)
score = rng.uniform(0, 100, 20_000)
treated_rd = (score >= 60).astype(int)
y_rd = 20 + 0.30 * score + 4.0 * treated_rd + rng.normal(0, 3, len(score))        # smooth trend in the score + a jump of 4 at the cutoff
bw = 8
near = np.abs(score - 60) < bw
Xrd = sm.add_constant(pd.DataFrame({"t": treated_rd[near], "s": score[near] - 60, "ts": treated_rd[near] * (score[near] - 60)}).astype(float))
rd = sm.OLS(y_rd[near], Xrd).fit(cov_type="HC1")
print(f"local linear RD (bandwidth {bw}): jump at the cutoff {rd.params['t']:+.2f} (se {rd.bse['t']:.2f}); truth +4.0")
print(f"naive difference of all treated vs all untreated: {y_rd[treated_rd == 1].mean() - y_rd[treated_rd == 0].mean():+.2f}  (mixes the effect with the score trend)")
```
```text
local linear RD (bandwidth 8): jump at the cutoff +4.11 (se 0.21); truth +4.0
naive difference of all treated vs all untreated: +19.07  (mixes the effect with the score trend)
```

**Instrumental variables (IV).** If something (the instrument `Z`) shifts the treatment but affects the outcome *only* through the treatment, it isolates variation in treatment that is free of the hidden confounder. With a binary instrument the **Wald estimator** is `Cov(Z, Y) / Cov(Z, T)`: the effect of `Z` on the outcome divided by its effect on the treatment.

```python run
rng = np.random.default_rng(36)
hidden = rng.normal(0, 1, n)
Z = rng.integers(0, 2, n)                                                          # e.g. a randomly timed promotion email
T4 = (rng.random(n) < 1 / (1 + np.exp(-(-0.5 + 1.5 * Z + 1.0 * hidden)))).astype(int)
Y4 = 10 + 3.0 * T4 + 5.0 * hidden + rng.normal(0, 2, n)                            # true effect 3
naive_iv = Y4[T4 == 1].mean() - Y4[T4 == 0].mean()
wald = np.cov(Z, Y4)[0, 1] / np.cov(Z, T4)[0, 1]
print(f"naive difference: {naive_iv:.2f} (biased by the hidden driver) | IV (Wald) estimate: {wald:.2f} (truth 3.0)")
print(f"first stage: the instrument moves treatment by {T4[Z == 1].mean() - T4[Z == 0].mean():+.2f} (a weak instrument would make the estimate wildly unstable)")
```
```text
naive difference: 6.83 (biased by the hidden driver) | IV (Wald) estimate: 3.00 (truth 3.0)
first stage: the instrument moves treatment by +0.29 (a weak instrument would make the estimate wildly unstable)
```

### 11.10 Which method when

| Situation | Method | Key assumption | Check |
|---|---|---|---|
| You can randomise | A/B test | none beyond execution | SRM, A/A |
| Observed confounders, treatment is a choice | regression, IPW, matching, AIPW | no unmeasured confounding, overlap | balance after adjustment, overlap plots, sensitivity analysis |
| Policy rolled out in some places or times | difference-in-differences | parallel trends | pre-trend plot, placebo tests |
| Assignment by a threshold | regression discontinuity | no manipulation of the score at the cutoff | density of the score at the cutoff, bandwidth sensitivity |
| A random nudge shifts treatment | instrumental variable | the instrument affects the outcome only via treatment | first-stage strength |

### 11.11 Try it

1. In the propensity example, remove `z_age` from the propensity model but keep it in the outcome. Which estimator is hurt: IPW or regression? Which one does AIPW still get right?
2. Add a placebo test to the DiD: pretend the policy started in week 3 (using only weeks 0-5) and estimate the "effect". It should be near zero.


## 12. Project: analyse a simulated product experiment

### 12.1 The brief

A subscription app redesigned its **onboarding flow**. The team ran an A/B test for 21 days and a product manager has already said, in a meeting: *"We looked at day 9 and it was significant, so we shipped it to everyone."* You are asked to review the analysis. The data have been simulated with a truth we know, and with problems of the kind that real experiments have.

The pre-registered plan: **primary metric** = activation (finishing onboarding); planned 45,000 users per arm; two-sided α = 0.05; MDE 1.0 point on a 40% base; **guardrail** = support-ticket rate may not rise by more than 1 point; secondary metrics = day-7 retention, week-1 sessions, 30-day revenue, share-content, invite-friend, notification opt-in.

Your deliverables:

1. A small, tested library, **`abtest`**, with the tools of this chapter.
2. An **audit** of the experiment: every problem found, with evidence.
3. The **correct analysis** of the part of the data that can be trusted.
4. A **decision memo** that a product manager can act on, and a one-paragraph reply to "we looked at day 9 and shipped".

### 12.2 The library

```python run
import pathlib, tempfile, subprocess, os
proj = pathlib.Path(tempfile.mkdtemp()) / "abtest_project"
proj.mkdir()
(proj / "abtest.py").write_text('''"""abtest: sample sizes, trust checks, tests, corrections, sequential boundaries and a decision rule."""
import math
import numpy as np
import pandas as pd
from scipy import stats


# ---------- planning ----------
def n_per_arm_prop(p1, delta, alpha=0.05, power=0.8):
    p2 = p1 + delta
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / delta ** 2


def mde_prop(p1, n, alpha=0.05, power=0.8):
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    delta = 0.001
    for _ in range(60):
        delta = (za + zb) * math.sqrt((p1 * (1 - p1) + (p1 + delta) * (1 - p1 - delta)) / n)
    return delta


# ---------- trust checks ----------
def srm_check(n_control, n_treatment, planned_treatment_share=0.5):
    total = n_control + n_treatment
    expected = [total * (1 - planned_treatment_share), total * planned_treatment_share]
    return stats.chisquare([n_control, n_treatment], expected)[1]


def smd(x, treated):
    x, treated = np.asarray(x, float), np.asarray(treated, bool)
    return float((x[treated].mean() - x[~treated].mean()) / math.sqrt((x[treated].var(ddof=1) + x[~treated].var(ddof=1)) / 2))


def dedupe(df, key="user"):
    return df.drop_duplicates(key, keep="first")


# ---------- tests ----------
def two_prop_test(x_c, n_c, x_t, n_t, alpha=0.05):
    p_c, p_t = x_c / n_c, x_t / n_t
    pooled = (x_c + x_t) / (n_c + n_t)
    z = (p_t - p_c) / math.sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t))
    se = math.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
    zc = stats.norm.ppf(1 - alpha / 2)
    return {"p_control": p_c, "p_treatment": p_t, "diff": p_t - p_c, "z": z, "p_value": 2 * stats.norm.sf(abs(z)),
            "ci_low": p_t - p_c - zc * se, "ci_high": p_t - p_c + zc * se}


def welch(y_c, y_t, alpha=0.05):
    y_c, y_t = np.asarray(y_c, float), np.asarray(y_t, float)
    v_c, v_t = y_c.var(ddof=1) / len(y_c), y_t.var(ddof=1) / len(y_t)
    diff, se = y_t.mean() - y_c.mean(), math.sqrt(v_c + v_t)
    df = (v_c + v_t) ** 2 / (v_c ** 2 / (len(y_c) - 1) + v_t ** 2 / (len(y_t) - 1))
    h = stats.t.ppf(1 - alpha / 2, df) * se
    return {"diff": diff, "se": se, "p_value": 2 * stats.t.sf(abs(diff / se), df), "ci_low": diff - h, "ci_high": diff + h}


def cuped(y, x, treated, max_z=3.5):
    """Adjust y with a PRE-experiment covariate x. Refuse if x differs between the arms by more than chance allows
    (the treatment may have changed it). The test is on the standardised difference, scaled by its standard error."""
    treated = np.asarray(treated, bool)
    z = smd(x, treated) / math.sqrt(1 / treated.sum() + 1 / (~treated).sum())
    if abs(z) > max_z:
        raise ValueError(f"covariate differs between arms (z = {z:.1f}); it may not be a pre-treatment measurement")
    y, x = np.asarray(y, float), np.asarray(x, float)
    theta = np.cov(y, x)[0, 1] / np.var(x, ddof=1)
    return y - theta * (x - x.mean())


# ---------- multiple testing ----------
def holm(p, alpha=0.05):
    p = np.asarray(p); order = np.argsort(p); reject = np.zeros(len(p), bool)
    for rank, idx in enumerate(order):
        if p[idx] <= alpha / (len(p) - rank):
            reject[idx] = True
        else:
            break
    return reject


def benjamini_hochberg(p, q=0.05):
    p = np.asarray(p); m = len(p); order = np.argsort(p)
    below = np.flatnonzero(p[order] <= np.arange(1, m + 1) / m * q)
    reject = np.zeros(m, bool)
    if len(below):
        reject[order[: below.max() + 1]] = True
    return reject


# ---------- sequential monitoring ----------
def obf_boundaries(K, alpha=0.05, sims=300_000, seed=0):
    """O'Brien-Fleming critical |z| values for K equally spaced looks, found by simulating the null."""
    S = np.random.default_rng(seed).normal(size=(sims, K)).cumsum(1)
    Z = np.abs(S / np.sqrt(np.arange(1, K + 1)))
    c = np.quantile((Z * np.sqrt(np.arange(1, K + 1) / K)).max(1), 1 - alpha)
    return c * np.sqrt(K / np.arange(1, K + 1))


# ---------- decision ----------
def decide(srm_p, ci_low, ci_high, guardrail_upper=None, margin=None):
    if srm_p < 0.001:
        return "INVALID: sample ratio mismatch; fix the experiment before reading any metric"
    if guardrail_upper is not None and margin is not None and guardrail_upper >= margin:
        return "DO NOT SHIP: the guardrail may be violated"
    if ci_low > 0:
        return "SHIP: the primary metric improved with confidence"
    if ci_high <= 0:
        return "DO NOT SHIP: no benefit or a harm"
    return "INCONCLUSIVE: the interval includes zero; extend the test or accept the uncertainty"
''', encoding="utf-8")
print("abtest.py:", len((proj / "abtest.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
abtest.py: 110 lines
```

### 12.3 The tests

Each test guards a failure from this chapter.

```python run
(proj / "test_abtest.py").write_text('''import numpy as np, pandas as pd, pytest
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest
import abtest as ab

def test_sample_size_matches_statsmodels_to_within_one_percent():
    ours = ab.n_per_arm_prop(0.10, 0.01)
    theirs = NormalIndPower().solve_power(effect_size=proportion_effectsize(0.11, 0.10), alpha=0.05, power=0.8)
    assert abs(ours - theirs) / theirs < 0.01

def test_mde_is_the_inverse_of_the_sample_size():
    n = ab.n_per_arm_prop(0.10, 0.01)
    assert ab.mde_prop(0.10, n) == pytest.approx(0.01, rel=0.01), "mde_prop(n_per_arm_prop(delta)) must give back delta"

def test_two_prop_test_matches_statsmodels():
    r = ab.two_prop_test(1000, 10_000, 1060, 10_000)
    z, p = proportions_ztest([1060, 1000], [10_000, 10_000])
    assert r["z"] == pytest.approx(z) and r["p_value"] == pytest.approx(p)

def test_false_positive_rate_is_five_percent_without_an_effect():
    rng = np.random.default_rng(0)
    hits = 0
    for _ in range(3000):
        x_c, x_t = rng.binomial(5000, 0.1), rng.binomial(5000, 0.1)
        hits += ab.two_prop_test(x_c, 5000, x_t, 5000)["p_value"] < 0.05
    assert 0.035 < hits / 3000 < 0.065, "an A/A comparison should reject about 5% of the time"

def test_srm_flags_a_real_mismatch_and_not_normal_noise():
    assert ab.srm_check(51_000, 49_000) < 0.001
    assert ab.srm_check(50_100, 49_900) > 0.05

def test_corrections_match_statsmodels():
    p = np.random.default_rng(1).uniform(0, 0.08, 40)
    assert (ab.holm(p) == multipletests(p, method="holm")[0]).all()
    assert (ab.benjamini_hochberg(p) == multipletests(p, method="fdr_bh")[0]).all()

def test_peeking_inflates_errors_and_obrien_fleming_does_not():
    rng = np.random.default_rng(2)
    K, sims = 5, 20_000
    Z = rng.normal(size=(sims, K, 100)).sum(2).cumsum(1) / np.sqrt(100 * np.arange(1, K + 1))
    naive = (np.abs(Z) > 1.96).any(1).mean()
    corrected = (np.abs(Z) > ab.obf_boundaries(K, sims=100_000)[None, :]).any(1).mean()
    assert naive > 0.10, "stopping at the first |z| > 1.96 over five looks should inflate the error well above 5%"
    assert corrected < 0.065, "O'Brien-Fleming boundaries must hold the error near 5%"

def test_cuped_is_unbiased_and_reduces_variance():
    rng = np.random.default_rng(3)
    raw, adj = [], []
    for _ in range(600):
        x = rng.normal(100, 30, 800); t = np.r_[np.zeros(400, bool), np.ones(400, bool)]
        y = 0.7 * (x - 100) + rng.normal(0, 20, 800) + 2.0 * t
        raw.append(y[t].mean() - y[~t].mean()); ya = ab.cuped(y, x, t); adj.append(ya[t].mean() - ya[~t].mean())
    assert np.mean(adj) == pytest.approx(2.0, abs=0.15) and np.std(adj) < 0.8 * np.std(raw)

def test_cuped_refuses_a_covariate_the_treatment_could_have_changed():
    rng = np.random.default_rng(4)
    t = np.r_[np.zeros(500, bool), np.ones(500, bool)]
    x_after = rng.normal(0, 1, 1000) + 1.5 * t                         # measured AFTER the treatment: differs between arms
    with pytest.raises(ValueError, match="pre-treatment"):
        ab.cuped(rng.normal(size=1000), x_after, t)

def test_dedupe_keeps_one_row_per_user():
    df = pd.DataFrame({"user": [1, 2, 2, 3, 3, 3], "v": range(6)})
    assert list(ab.dedupe(df)["user"]) == [1, 2, 3]

def test_the_decision_rule():
    assert ab.decide(1e-6, 0.01, 0.02).startswith("INVALID"), "an SRM overrides any apparent win"
    assert ab.decide(0.5, 0.01, 0.02).startswith("SHIP")
    assert ab.decide(0.5, -0.01, 0.02).startswith("INCONCLUSIVE"), "an interval that includes zero is not a win"
    assert ab.decide(0.5, -0.03, -0.01).startswith("DO NOT SHIP")
    assert ab.decide(0.5, 0.01, 0.02, guardrail_upper=0.02, margin=0.01).startswith("DO NOT SHIP"), "a possible guardrail violation blocks the launch"
''', encoding="utf-8")
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "test_abtest.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-800:] or res.stderr.strip()[-800:])
```
```text
...........                                                              [100%]
11 passed in 1.23s
```

### 12.4 The experiment's data

The generator plants problems that the audit must find. It is shown here for transparency, but **in a real review you would not have it**, so try the audit first and read the generator afterwards.

<details><summary>Data generator (open after you try the audit)</summary>

```python run
def simulate_onboarding(seed=39, n=90_000):
    r = np.random.default_rng(seed)
    uid = np.arange(n)
    day = r.integers(0, 21, n)
    treat = np.array([bucket(u, "onboarding-v3") < 500 for u in uid])
    platform = r.choice(["android", "ios", "web"], n, p=[.45, .40, .15])
    pre = r.poisson(r.gamma(2.0, 2.5, n))                                           # sessions in the 30 days BEFORE the experiment
    bot = r.random(n) < 0.015                                                       # 1.5% of traffic is bots
    pre = np.where(bot, r.integers(150, 400, n), pre)
    z = np.log1p(pre) - 1.6
    eff = np.array([0.014, 0.006, 0.001])[day // 7]                                 # TRUE effect on activation: strong in week 1, fading to ~0 (novelty)
    activated = np.where(bot, r.random(n) < 0.9, r.random(n) < np.clip(0.40 + 0.05 * z + eff * treat, 0.01, 0.99)).astype(int)
    d7 = np.where(bot, 0, (r.random(n) < np.clip(0.25 + 0.04 * z, .01, .99))).astype(int)
    sessions = r.poisson(np.clip(2 + 0.8 * z + 1.0 * activated, .2, None))
    revenue = (r.random(n) < 0.06) * np.exp(r.normal(3.0, 1.0, n))
    ticket, invited, shared, optin = (r.random(n) < 0.04).astype(int), (r.random(n) < 0.08).astype(int), (r.random(n) < 0.12).astype(int), (r.random(n) < 0.55).astype(int)
    logged = np.ones(n, bool)
    logged &= ~(treat & (platform == "android") & (r.random(n) < 0.18))             # BUG 1: the new flow crashes for 18% of treated Android users: they are never logged
    logged &= ~(treat & bot & (r.random(n) < 0.9))                                  # BUG 2: the new flow's edge filter drops most bots, only in the treatment arm
    df = pd.DataFrame(dict(user=uid, day=day, arm=treat.astype(int), platform=platform, pre_sessions=pre, activated=activated, d7_retained=d7,
                           sessions_w1=sessions, revenue_30d=revenue, support_ticket=ticket, invited_friend=invited, shared_content=shared, notif_optin=optin))[logged]
    dup = df.sample(frac=0.02, random_state=seed)                                   # BUG 3: 2% of events were logged twice
    return pd.concat([df, dup], ignore_index=True).sort_values(["day", "user"], kind="stable").reset_index(drop=True)

raw = simulate_onboarding()
print(raw.shape, "| columns:", list(raw.columns))
```
```text
(87498, 13) | columns: ['user', 'day', 'arm', 'platform', 'pre_sessions', 'activated', 'd7_retained', 'sessions_w1', 'revenue_30d', 'support_ticket', 'invited_friend', 'shared_content', 'notif_optin']
```

</details>

### 12.5 The audit, step by step

**Step 1. Plan versus reality.**

```python run
sys.path.insert(0, str(proj))
import importlib, abtest as ab
importlib.reload(ab)

planned_n, planned_p, planned_mde = 45_000, 0.40, 0.01
print(f"planned: {planned_n:,} per arm; the sample-size formula for an MDE of {planned_mde} on a {planned_p:.0%} base gives {ab.n_per_arm_prop(planned_p, planned_mde):,.0f} per arm -> the plan was adequately powered")
n_c, n_t = int((raw.arm == 0).sum()), int((raw.arm == 1).sum())
print(f"rows received: control {n_c:,}, treatment {n_t:,}")
```
```text
planned: 45,000 per arm; the sample-size formula for an MDE of 0.01 on a 40% base gives 37,824 per arm -> the plan was adequately powered
rows received: control 45,973, treatment 41,525
```

**Step 2. Data quality: duplicates and bots.**

```python run
dups = int(raw.duplicated("user").sum())
print(f"duplicate user rows: {dups:,} ({dups / len(raw):.1%})")
nodup = ab.dedupe(raw)
print("users with an implausible pre-experiment activity (more than 100 sessions in 30 days):", int((nodup.pre_sessions > 100).sum()), "->",
      nodup.assign(bot=nodup.pre_sessions > 100).groupby("arm")["bot"].mean().round(4).to_dict(), "(share of each arm)")
print("activation rate of those users:", round(float(nodup[nodup.pre_sessions > 100].activated.mean()), 3), "vs", round(float(nodup[nodup.pre_sessions <= 100].activated.mean()), 3), "for the rest")
```
```text
duplicate user rows: 1,716 (2.0%)
users with an implausible pre-experiment activity (more than 100 sessions in 30 days): 728 -> {0: 0.0146, 1: 0.0017} (share of each arm)
activation rate of those users: 0.89 vs 0.398 for the rest
```

Two findings. A few percent of the rows are duplicates (users counted twice inflate the sample size and understate the variance). And there are bots, with absurd activity and near-perfect "activation", that appear **almost only in the control arm** (1.5% of control users against 0.2% of treatment users): a difference in how the arms filter traffic is itself a red flag, and it biases the comparison against the treatment.

**Step 3. Sample ratio mismatch.**

```python run
clean = nodup[nodup.pre_sessions <= 100]
for name, d in [("raw data", raw), ("deduplicated", nodup), ("deduplicated, bots removed", clean)]:
    nc, nt = int((d.arm == 0).sum()), int((d.arm == 1).sum())
    print(f"{name:28s} control {nc:6,}, treatment {nt:6,} | SRM p-value {ab.srm_check(nc, nt):.2e}")
print()
rows = []
for plat in ["android", "ios", "web"]:
    d = clean[clean.platform == plat]
    nc, nt = int((d.arm == 0).sum()), int((d.arm == 1).sum())
    rows.append((plat, nc, nt, nt / (nc + nt), ab.srm_check(nc, nt)))
print(pd.DataFrame(rows, columns=["platform", "control", "treatment", "treatment share (planned 0.5)", "SRM p-value"]).round(4).to_string(index=False))
```
```text
raw data                     control 45,973, treatment 41,525 | SRM p-value 4.19e-51
deduplicated                 control 45,076, treatment 40,706 | SRM p-value 2.42e-50
deduplicated, bots removed   control 44,416, treatment 40,638 | SRM p-value 2.22e-38

platform  control  treatment  treatment share (planned 0.5)  SRM p-value
 android    19991      16215                         0.4479       0.0000
     ios    17653      17685                         0.5005       0.8648
     web     6772       6738                         0.4987       0.7699
```

The SRM is **only on Android**, where the treatment arm has about 19% fewer users than the control arm, matching the 18% of treated Android users who crash. On iOS and web the split is healthy. This is the key diagnosis. Every Android comparison is biased: the treated Android users are a survivor group (those whose phones did not crash, probably newer, faster ones). **Android cannot be analysed until the crash is fixed**; iOS and web can.

**Step 4. The day-9 peek, reconstructed.**

```python run
def activation_test(d):
    return ab.two_prop_test(int(d[d.arm == 0].activated.sum()), int((d.arm == 0).sum()), int(d[d.arm == 1].activated.sum()), int((d.arm == 1).sum()))

rows = []
for last_day in [2, 4, 6, 9, 13, 17, 20]:
    d = raw[raw.day <= last_day]
    r_ = activation_test(d)
    rows.append((last_day + 1, len(d), r_["diff"], r_["p_value"], r_["z"]))
cum = pd.DataFrame(rows, columns=["day of the test", "users so far", "cumulative lift", "p-value", "z"])
print(cum.round(4).to_string(index=False))
```
```text
 day of the test  users so far  cumulative lift  p-value      z
               3         12546           0.0180   0.0401 2.0523
               5         20979           0.0133   0.0502 1.9585
               7         29121           0.0152   0.0083 2.6386
              10         41701           0.0125   0.0094 2.5989
              14         58258           0.0050   0.2191 1.2289
              18         74907           0.0038   0.2885 1.0614
              21         87498           0.0024   0.4657 0.7294
```

On the raw data the cumulative lift at day 10 is about +1.2 points with p of about 0.01: "significant". That is what the product manager saw. Three things were wrong with acting on it:

1. **It was a peek** in a fixed-horizon test: the p-value does not mean what it says (section 8).
2. **The effect was a first-week effect.** Early users carry the novelty boost; later users see much less.
3. **The data were broken** (SRM, duplicates, bots), so the early "win" was partly an artefact.

How much would a properly planned sequential test have demanded at day 10? With three equally spaced looks (days 7, 14, 21), O'Brien-Fleming boundaries:

```python run
bounds = ab.obf_boundaries(3)
print("O'Brien-Fleming critical |z| at looks on days 7, 14, 21:", bounds.round(3))
d7 = raw[raw.day <= 6]
print("z-statistic at the day-7 look on the raw data:", round(activation_test(d7)["z"], 3), "-> needs", round(bounds[0], 3), "to stop for a win:", "STOP" if abs(activation_test(d7)["z"]) > bounds[0] else "continue")
```
```text
O'Brien-Fleming critical |z| at looks on days 7, 14, 21: [3.468 2.453 2.003]
z-statistic at the day-7 look on the raw data: 2.639 -> needs 3.468 to stop for a win: continue
```

A properly designed sequential test would not have stopped at day 7 or 10.

**Step 5. The correct analysis on trustworthy data (iOS and web, deduplicated, bots removed, full 21 days).**

```python run
valid = clean[clean.platform != "android"]
nv_c, nv_t = int((valid.arm == 0).sum()), int((valid.arm == 1).sum())
print(f"valid subset: control {nv_c:,}, treatment {nv_t:,}, SRM p-value {ab.srm_check(nv_c, nv_t):.3f}")
primary = activation_test(valid)
print(f"activation: control {primary['p_control']:.4f}, treatment {primary['p_treatment']:.4f}, lift {primary['diff']*100:+.2f} points, 95% CI [{primary['ci_low']*100:+.2f}, {primary['ci_high']*100:+.2f}], p = {primary['p_value']:.3f}")
mde_valid = ab.mde_prop(primary["p_control"], nv_c)
print(f"on this smaller sample the MDE is {mde_valid*100:.2f} points (the plan assumed 1.0)")
# variance reduction with the pre-experiment covariate
y_adj = ab.cuped(valid.activated.to_numpy(), np.log1p(valid.pre_sessions.to_numpy()), valid.arm.to_numpy() == 1)
adj = welch(y_adj[valid.arm.to_numpy() == 0], y_adj[valid.arm.to_numpy() == 1])
print(f"with the pre-experiment covariate (regression adjustment): lift {adj['diff']*100:+.2f} points, 95% CI [{adj['ci_low']*100:+.2f}, {adj['ci_high']*100:+.2f}], p = {adj['p_value']:.3f}")
```
```text
valid subset: control 24,425, treatment 24,423, SRM p-value 0.993
activation: control 0.3936, treatment 0.4009, lift +0.73 points, 95% CI [-0.14, +1.60], p = 0.100
on this smaller sample the MDE is 1.24 points (the plan assumed 1.0)
with the pre-experiment covariate (regression adjustment): lift +0.71 points, 95% CI [-0.16, +1.57], p = 0.108
```

**Step 6. Novelty: the effect over time.**

```python run
rows = []
for wk, (a, b) in enumerate([(0, 6), (7, 13), (14, 20)], start=1):
    d = valid[(valid.day >= a) & (valid.day <= b)]
    r_ = activation_test(d)
    rows.append((f"week {wk} (days {a + 1}-{b + 1})", len(d), r_["diff"] * 100, r_["ci_low"] * 100, r_["ci_high"] * 100))
print(pd.DataFrame(rows, columns=["exposure period", "users", "lift (points)", "ci_low", "ci_high"]).round(2).to_string(index=False))
```
```text
    exposure period  users  lift (points)  ci_low  ci_high
  week 1 (days 1-7)  16368         2.2400  0.7400   3.7400
 week 2 (days 8-14)  16275        -0.5600 -2.0600   0.9500
week 3 (days 15-21)  16205         0.5000 -1.0100   2.0000
```

The lift is clearly positive for users first exposed in week 1 (about +2.2 points, interval excluding zero), while the later two weeks are indistinguishable from zero. That is the signature of a **novelty effect**, though with 16,000 users per period the later intervals are wide, so the honest statement is "the early lift is real, the later lift is unproven". The average over three weeks overstates what users will get once the page is no longer new.

**Step 7. Secondary metrics and multiple testing.**

```python run
rows = []
for m in ["d7_retained", "invited_friend", "shared_content", "notif_optin"]:
    c, t = valid[valid.arm == 0][m], valid[valid.arm == 1][m]
    r_ = ab.two_prop_test(int(c.sum()), len(c), int(t.sum()), len(t))
    rows.append((m, r_["diff"] * 100, r_["p_value"]))
for m in ["sessions_w1", "revenue_30d"]:
    r_ = welch(valid[valid.arm == 0][m], valid[valid.arm == 1][m])
    rows.append((m, r_["diff"], r_["p_value"]))
sec = pd.DataFrame(rows, columns=["secondary metric", "difference", "raw p-value"])
sec["Holm rejects"] = ab.holm(sec["raw p-value"].to_numpy())
sec["BH rejects"] = ab.benjamini_hochberg(sec["raw p-value"].to_numpy())
print(sec.round(4).to_string(index=False))
print("metrics with raw p < 0.05:", int((sec["raw p-value"] < 0.05).sum()), "| after Holm correction:", int(sec["Holm rejects"].sum()))
```
```text
secondary metric  difference  raw p-value  Holm rejects  BH rejects
     d7_retained     -0.0758       0.8453         False       False
  invited_friend     -0.2450       0.3192         False       False
  shared_content      0.6151       0.0367         False       False
     notif_optin      0.8356       0.0635         False       False
     sessions_w1      0.0243       0.1236         False       False
     revenue_30d     -0.0137       0.9040         False       False
metrics with raw p < 0.05: 1 | after Holm correction: 0
```

One secondary metric may look "significant" by itself (`shared_content`). With six metrics tested, that is the expected number of false alarms; after correction nothing survives. It must not appear in the memo as a win (and the data were generated with no effect on it).

**Step 8. The guardrail.**

```python run
gc, gt = valid[valid.arm == 0].support_ticket, valid[valid.arm == 1].support_ticket
g = ab.two_prop_test(int(gc.sum()), len(gc), int(gt.sum()), len(gt), alpha=0.10)                 # 90% two-sided = 95% one-sided
print(f"support tickets: control {g['p_control']:.4f}, treatment {g['p_treatment']:.4f}; increase {g['diff']*100:+.2f} points, one-sided 95% upper bound {g['ci_high']*100:+.2f} points (tolerance 1.00)")
```
```text
support tickets: control 0.0409, treatment 0.0394; increase -0.15 points, one-sided 95% upper bound +0.14 points (tolerance 1.00)
```

**Step 9. The decision and the memo.**

```python run
decision = ab.decide(ab.srm_check(nv_c, nv_t), primary["ci_low"], primary["ci_high"], guardrail_upper=g["ci_high"], margin=0.01)
late = activation_test(valid[valid.day >= 14])
android_c, android_t = int(((clean.platform == 'android') & (clean.arm == 0)).sum()), int(((clean.platform == 'android') & (clean.arm == 1)).sum())
memo = f"""REVIEW OF THE ONBOARDING EXPERIMENT
Verdict on the analysis that led to the launch: NOT SUPPORTED. It acted on a day-10 peek of a fixed-horizon test, on data with three defects.
Defects found   : (1) sample-ratio mismatch on Android (the treatment arm has {(1 - android_t / android_c) * 100:.0f}% fewer users than control; cause: crashes); (2) bots filtered in the treatment arm only; (3) {dups:,} duplicated rows.
Reliable subset : iOS + web, deduplicated, bots removed ({nv_c + nv_t:,} users). Android must not be analysed until the crash is fixed.
Primary metric  : activation {primary['p_control']:.2%} -> {primary['p_treatment']:.2%}; lift {primary['diff']*100:+.2f} points, 95% CI [{primary['ci_low']*100:+.2f}, {primary['ci_high']*100:+.2f}], p = {primary['p_value']:.2f}.
Time pattern    : a first-week lift that fades; the lift for users first exposed on days 15-21 is {late['diff']*100:+.2f} points (CI [{late['ci_low']*100:+.2f}, {late['ci_high']*100:+.2f}]).
Secondary       : no metric survives multiple-testing correction; do not cite the raw p-values.
Guardrail       : support tickets {g['diff']*100:+.2f} points, one-sided upper bound {g['ci_high']*100:+.2f} (limit +1.00): OK.
Decision rule   : {decision}
Recommendation  : do not claim a validated improvement. Fix the Android crash, keep a 10% holdout on the old flow for 4 more weeks to measure the long-run effect, then decide with a fixed-horizon analysis planned in advance."""
print(memo)
```
```text
REVIEW OF THE ONBOARDING EXPERIMENT
Verdict on the analysis that led to the launch: NOT SUPPORTED. It acted on a day-10 peek of a fixed-horizon test, on data with three defects.
Defects found   : (1) sample-ratio mismatch on Android (the treatment arm has 19% fewer users than control; cause: crashes); (2) bots filtered in the treatment arm only; (3) 1,716 duplicated rows.
Reliable subset : iOS + web, deduplicated, bots removed (48,848 users). Android must not be analysed until the crash is fixed.
Primary metric  : activation 39.36% -> 40.09%; lift +0.73 points, 95% CI [-0.14, +1.60], p = 0.10.
Time pattern    : a first-week lift that fades; the lift for users first exposed on days 15-21 is +0.50 points (CI [-1.01, +2.00]).
Secondary       : no metric survives multiple-testing correction; do not cite the raw p-values.
Guardrail       : support tickets -0.15 points, one-sided upper bound +0.14 (limit +1.00): OK.
Decision rule   : INCONCLUSIVE: the interval includes zero; extend the test or accept the uncertainty
Recommendation  : do not claim a validated improvement. Fix the Android crash, keep a 10% holdout on the old flow for 4 more weeks to measure the long-run effect, then decide with a fixed-horizon analysis planned in advance.
```

### 12.6 The reply to "we looked at day 9 and it was significant"

> Looking at the data every day is not wrong. Deciding on one look is. A fixed-horizon test promises a 5% false-positive rate only if you look once, at the planned sample size; stopping the first time p dips below 0.05 raises that rate several times over. Day 9 also fell in the part of the test where the novelty effect is strongest, so the early estimate overstated the long-run lift even if it was real. And the data had defects (a sample-ratio mismatch, filtered bots, duplicates) that we only found by checking. When the defects are removed and the full period is analysed, the interval for the lift includes zero. We should not ship on that evidence; we should fix the crash, keep a holdout, and use a planned sequential design if we want to stop early.

### 12.7 What to hand in

1. `abtest.py` and `test_abtest.py`, all tests passing.
2. The audit: each defect, the evidence (a number), the effect on the analysis if left unfixed, and the fix.
3. The corrected analysis on the reliable subset with intervals.
4. The memo, and a short paragraph for a non-technical reader.
5. A **pre-registration** for the follow-up experiment: hypothesis, metric, MDE, sample size, duration in whole weeks, stopping rule, segments, guardrails.

### 12.8 Extensions

1. Run the audit again with `seed=40` through `seed=45`. Which conclusions change from seed to seed, and which are stable? What does that say about the cost of making a decision from one experiment?
2. Plan the follow-up as a **group-sequential** test with O'Brien-Fleming boundaries at weeks 1, 2, 3 and 4 and compute the sample size inflation relative to a fixed-horizon test.
3. Add an `abtest.report(df, config)` function that runs steps 1 to 9 and returns the memo, with tests that a planted SRM makes it return INVALID.
4. Replace the Android exclusion by an **intention-to-treat** analysis that keeps the crashed users in the denominator (you would need the assignment log, not the event log). Why is this the right fix for a crash?
5. Estimate the long-run effect by regressing the lift on the weeks since first exposure, with a confidence interval, and discuss what a 5% holdout would add.

## 13. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Comparing groups that chose their treatment | confounding reported as an effect | randomise (1, 2) |
| One salt for two experiments | experiments are not independent | experiment-specific salt, hash-based stable assignment (2.3) |
| Deciding on the p-value alone | tiny effects or inconclusive tests misread | effect size, interval, practical threshold (3.3) |
| "Not significant" read as "no effect" | an under-powered test mistaken for a null | report the interval and the MDE (3.1, 4) |
| No power calculation | an inconclusive test by design | sample size and MDE before starting (4) |
| Planned effect too optimistic | power collapses | plan for a realistic or the smallest worthwhile effect (4.3) |
| Stopping on a weekday, not a full cycle | weekly pattern biases the result | run whole weeks (4.4) |
| Analysing impressions or sessions when users were randomised | standard errors far too small | analyse at the unit of randomisation; delta method or bootstrap over users (5.2) |
| Outliers in revenue | lost power or a fake effect | cap in advance, bootstrap, or split conversion and order value (5.3) |
| Skipping the SRM check | a broken experiment analysed as if fine | chi-square on the arm counts first; p < 0.001 stops the analysis (6.2) |
| A covariate affected by the treatment | adjustment biases the estimate | only pre-experiment covariates (5.1, 11.8) |
| Many metrics, one significant | a false win | one primary metric, correction for the rest (7) |
| Subgroup fishing | a segment "wins" by chance | pre-registered segments, interaction tests, correction (7.5, 10.6) |
| Peeking and stopping at p < 0.05 | the false-positive rate is 15-30% | fixed horizon, group-sequential boundaries, or always-valid tests (8) |
| Stopping early on a win | the effect is overestimated | confirm, or use a design that corrects the estimate (8.4) |
| Extending a failed test "to get more data" | peeking with a second chance | decide the horizon in advance (8.4) |
| Treating a Bayesian probability as exempt from peeking | the long-run false-launch rate is not controlled | plan the stopping rule for either school (9.3) |
| Reading the average effect only | novelty or a segment hidden | effect by week, by segment (10.6, 10.7) |
| Adjusting for a mediator or a collider | the effect is erased or invented | adjust for pre-treatment confounders only (11.8) |
| Assuming no unmeasured confounding without argument | a biased "causal" estimate | causal diagram, sensitivity analysis, a design that removes the confounder (11.7) |
| Extreme inverse-probability weights | unstable estimates | check overlap, effective sample size; trim with care (11.5) |
| Difference-in-differences with different pre-trends | the design is invalid | plot pre-trends, placebo tests (11.9) |
| Using a weak instrument | wild estimates | check the first-stage strength (11.9) |

## 14. Summary

- **Randomisation** makes the treated and control groups comparable on everything, measured or not, so a difference in means estimates the causal effect. An observational comparison confounded by keenness overstated a true effect of 2 as more than 10.
- An **A/B test** needs a hypothesis, a unit of randomisation, a primary metric, guardrails, an MDE, a sample size, a duration and a decision rule **written before it starts**. Assign with a **stable hash plus a per-experiment salt**.
- **Analysis**: two-proportion z-test and Welch's t-test (matching the libraries), intervals with p-values, and practical significance. "Not significant" means inconclusive. A **p-value is not** the probability that the treatment works.
- **Power**: `n = (z_{α/2} + z_β)² · variance / δ²`, so halving the detectable effect quadruples the sample. Simulation confirms it; an effect half as large as planned leaves power below 30%. Convert sample size to duration (whole weeks) and invert it into an MDE.
- **Variance reduction**: CUPED / regression adjustment with a **pre-experiment** covariate cuts variance by `1 − ρ²`. Analyse at the level you randomised (delta method or bootstrap over users for ratio metrics); tame heavy tails in advance; watch for novelty and interference.
- **Trust checks come first**: **sample-ratio mismatch** (chi-square, p < 0.001 stops everything), A/A tests, covariate balance, data quality. An SRM manufactured a significant lift from nothing.
- **Multiple testing**: the chance of some false positive is `1 − 0.95^m`. Bonferroni and Holm control the family-wise error; Benjamini-Hochberg controls the false discovery rate. One primary metric, pre-registered segments, exploratory results labelled as such.
- **Peeking** inflates the false-positive rate from 5% to about 19% with ten looks. Remedies: a fixed horizon; **group-sequential** boundaries (Pocock, **O'Brien-Fleming**) found by simulating the null; **always-valid** mSPRT, which pays in power. Bayesian stopping rules need the same planning.
- **Causal inference without an experiment** rests on assumptions (consistency, ignorability, positivity). Tools: regression adjustment, **propensity scores** (IPW, matching, stratification), **doubly robust** AIPW, with balance and overlap checks. Unmeasured confounding defeats them all. Adjust for confounders, not mediators or colliders. **Difference-in-differences** (parallel trends), **regression discontinuity** and **instrumental variables** use the structure of the situation to remove confounding.
- The **project** is a reviewer's job: find the SRM, the bots and the duplicates; reconstruct the peek; analyse the trustworthy subset with intervals; find the novelty fade; correct the secondary metrics; and write a memo that says what the evidence supports, with tested tools behind it.

You reached the outcome of this chapter: you can **size an experiment and analyse it without peeking errors**, and you can say exactly which claims a given dataset can and cannot support. Next, ds.10 covers the last topics of the data-science track: communicating results, ethics and fairness, and the lifecycle of a data-science project.
