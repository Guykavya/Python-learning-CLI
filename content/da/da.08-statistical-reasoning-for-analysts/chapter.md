# Chapter 8 (DA): Statistical reasoning for analysts

Every number you computed in da.01 to da.07 described the rows in front of you: "the mean spend of these 500 customers is 2,578". That is a fact about the table. But nobody wants a fact about a table. Your manager wants a fact about **all** the customers, including the ones not in your file, and about next month's customers too. As soon as you say "customers spend about 3,100 a month", you have stepped from description to **inference**: you use a part to say something about the whole. That step can be wrong in two very different ways, and this chapter teaches you to tell them apart.

- **Luck.** Another sample would have given another number. The estimate wobbles, and the wobble can be measured. This is the problem of *uncertainty*, and the tool is the **confidence interval**.
- **Bias.** The sample was not a fair picture of the whole, so the estimate is off in a *consistent direction*, however large the sample. More data does not cure it. The tool is careful thinking about **how the data got to you**.

And a third trap sits on top of both: when you find that two things move together, it is tempting to say that one *causes* the other. A **correlation** is a fact about the data; a **cause** is a claim about the world, and between the two stand **confounders**.

By the end of this chapter you reach two outcomes: **you can explain why a correlation in your data does not prove an effect**, and **you can report an estimate with its uncertainty**. The chapter ends with the most useful exercise in applied statistics: taking a flawed analysis, finding what is wrong with it, and redoing it honestly.

Prerequisites: da.01 (descriptive statistics: mean, median, standard deviation, quantiles). Everything else is built here, in plain words and with code, because every idea is demonstrated on **synthetic data whose truth we know**. That is the great advantage of simulation: in real life you never learn whether your estimate was right; here you will, every time.

> **Offline rule for this chapter.** NumPy, pandas, SciPy and statsmodels are installed in the course environment. No internet is needed. Every dataset is **synthetic**, built with seeded random numbers (`numpy.random.default_rng`), so you get the same numbers I did. The company, its customers and its prices are invented. Every output block below was produced by running the code above it, in one session from top to bottom. **Versions are machine-specific.** Some blocks use many repeated random experiments (thousands); they run in a second or two. These are the versions used:

```python run
import sys
import numpy as np
import pandas as pd
import scipy
import statsmodels
from scipy import stats

print("python     ", sys.version.split()[0])
print("numpy      ", np.__version__)
print("pandas     ", pd.__version__)
print("scipy      ", scipy.__version__)
print("statsmodels", statsmodels.__version__)
```
```text
python      3.14.4
numpy       2.5.4
pandas      3.1.1
scipy       1.18.1
statsmodels 0.15.0
```

Two setup lines make the printed tables compact.

```python run
pd.set_option("display.width", 110)
pd.set_option("display.max_columns", 12)
pd.set_option("display.float_format", "{:,.2f}".format)
print("display options set")
```
```text
display options set
```

## Table of contents

1. [Populations and samples](#1-populations-and-samples)
2. [Sampling variation](#2-sampling-variation)
3. [Sampling bias](#3-sampling-bias)
4. [Confidence intervals](#4-confidence-intervals)
5. [Comparing groups and the meaning of a p-value](#5-comparing-groups-and-the-meaning-of-a-p-value)
6. [Practical against statistical significance](#6-practical-against-statistical-significance)
7. [Correlation](#7-correlation)
8. [Causation and confounders](#8-causation-and-confounders)
9. [Reporting uncertainty](#9-reporting-uncertainty)
10. [Project: critique and redo a flawed analysis](#10-project-critique-and-redo-a-flawed-analysis)
11. [Common traps](#11-common-traps)
12. [Summary](#12-summary)

## 1. Populations and samples

### 1.1 The vocabulary

| Word | Meaning | Example |
|---|---|---|
| **Population** | everyone (or everything) you want to know about | all 200,000 customers of the delivery app QuickBite |
| **Sample** | the part you actually observe | 500 customers who answered a survey |
| **Parameter** | a true number about the population (usually unknown) | the real mean monthly spend of all customers |
| **Statistic** or **estimate** | the same number computed from the sample | the mean spend of the 500 |
| **Sampling frame** | the list from which the sample is drawn | the customer database |
| **Estimand** | the exact quantity you want to know | "the mean monthly spend of all customers active in June" |

The last word is the one beginners skip. Before you estimate anything, say *what* you are trying to estimate, for *whom*, and *when*. A sample of last year's customers estimates last year's customers.

### 1.2 A population we can see completely

In real work you never see the population. To learn how estimates behave, we build one in code and **keep all of it**. Our synthetic app QuickBite has 200,000 customers in three kinds of city. For each we know the monthly spend (in rupees) and whether the customer ordered again within a week (`reorders`).

```python run
def make_population(N=200_000, seed=42):
    rng = np.random.default_rng(seed)
    city = rng.choice(["Metro", "Large", "Small"], N, p=[.35, .40, .25])
    age = np.clip(rng.normal(35, 10, N), 18, 70).round().astype(int)
    base = pd.Series(city).map({"Metro": 3200, "Large": 2400, "Small": 1700}).to_numpy()
    spend = (base * np.exp(rng.normal(0, .45, N) - .45 ** 2 / 2) * (1 + .004 * (age - 35))).round(0)
    p_reorder = 1 / (1 + np.exp(-(-1.2 + .00045 * (spend - 2400))))        # big spenders reorder more often
    return pd.DataFrame({"customer_id": np.arange(N), "age": age, "city": city, "monthly_spend": spend,
                         "reorders": rng.random(N) < p_reorder})


pop = make_population()
TRUE_MEAN = pop["monthly_spend"].mean()
TRUE_SHARE = pop["reorders"].mean()
print(pop.head(4).to_string(index=False))
print()
print(f"TRUE mean monthly spend : {TRUE_MEAN:10,.2f}")
print(f"TRUE median             : {pop['monthly_spend'].median():10,.2f}")
print(f"TRUE standard deviation : {pop['monthly_spend'].std():10,.2f}")
print(f"TRUE share who reorder  : {TRUE_SHARE * 100:9.2f} %")
print(pop.groupby("city")["monthly_spend"].agg(["size", "mean"]).round(1).to_string())
```
```text
 customer_id  age  city  monthly_spend  reorders
           0   38 Small         552.00     False
           1   37 Large       2,781.00      True
           2   29 Small         833.00     False
           3   44 Large       1,305.00     False

TRUE mean monthly spend :   2,502.44
TRUE median             :   2,205.00
TRUE standard deviation :   1,347.72
TRUE share who reorder  :     25.31 %
        size     mean
city                 
Large  80073 2,394.40
Metro  69990 3,195.90
Small  49937 1,703.70
```

These are the **parameters**. The population is skewed: the mean (2,502) is above the median (2,205), because a few customers spend a lot. Metro customers spend almost twice what Small-city customers do. Hold on to those facts; each will matter.

From now on we play the analyst who does not see all of this and draws a **simple random sample**: every customer has the same chance of being picked.

```python run
rng = np.random.default_rng(1)
sample = pop.sample(n=500, random_state=7)
print("sample mean spend :", round(sample["monthly_spend"].mean(), 1), "  (truth", round(TRUE_MEAN, 1), ")")
print("sample reorder %  :", round(sample["reorders"].mean() * 100, 1), "  (truth", round(TRUE_SHARE * 100, 1), ")")
```
```text
sample mean spend : 2577.6   (truth 2502.4 )
sample reorder %  : 23.8   (truth 25.3 )
```

The sample mean is close to the truth, but not equal. The gap is the **sampling error**. Is it small or large? Would a second sample give a similar number? That is the question of the next section.

## 2. Sampling variation

### 2.1 Draw many samples

If one sample gives 2,578, a second would give a different number. To see how different, repeat the experiment many times: draw 5,000 samples of 500 customers, compute the mean of each, and look at those 5,000 means. This collection is called the **sampling distribution of the mean**. You can only do this with a simulated population; in real life you have one sample. But the simulation shows what that one sample is *like*.

```python run
def text_hist(x, bins=12, width=40, decimals=0):
    """A histogram drawn with # characters (da.09 teaches real plots)."""
    counts, edges = np.histogram(x, bins=bins)
    for c, lo, hi in zip(counts, edges[:-1], edges[1:]):
        print(f"{lo:>9,.{decimals}f} - {hi:>9,.{decimals}f} | {'#' * int(width * c / counts.max())} {c}")


spend = pop["monthly_spend"].to_numpy()
rng = np.random.default_rng(10)
means_500 = np.array([rng.choice(spend, 500, replace=False).mean() for _ in range(5000)])
print("5,000 sample means, n = 500")
text_hist(means_500, bins=10)
print(f"\naverage of the sample means : {means_500.mean():,.1f}   (truth {TRUE_MEAN:,.1f})")
print(f"spread of the sample means  : {means_500.std():,.1f}")
print(f"smallest / largest          : {means_500.min():,.0f} / {means_500.max():,.0f}")
```
```text
5,000 sample means, n = 500
    2,259 -     2,304 |  1
    2,304 -     2,348 |  25
    2,348 -     2,393 | #### 146
    2,393 -     2,438 | ############### 548
    2,438 -     2,483 | ################################# 1222
    2,483 -     2,528 | ######################################## 1442
    2,528 -     2,573 | ############################ 1020
    2,573 -     2,618 | ############ 445
    2,618 -     2,663 | ### 119
    2,663 -     2,707 |  32

average of the sample means : 2,501.4   (truth 2,502.4)
spread of the sample means  : 60.5
smallest / largest          : 2,259 / 2,707
```

Three observations, each important.

1. The sample means pile up around the truth. Their average is within a few rupees of 2,502.4: **a random sample does not lean to one side**. This property is called being *unbiased*.
2. They spread: from about 2,300 to 2,700. A single sample of 500 can miss by a few hundred rupees.
3. The shape is a **bell**, even though the spend itself is skewed. This is not an accident; it is the central limit theorem (2.3).

### 2.2 The standard error

The spread of the sampling distribution has a name: the **standard error** (SE) of the mean. It measures how far a sample mean typically lands from the truth. There is a formula, and it is one of the most useful in statistics:

```text
SE of the mean = (standard deviation of the individual values) / sqrt(n)
```

```python run
sigma = spend.std()
for n in (100, 500, 2000):
    est = np.array([rng.choice(spend, n, replace=False).mean() for _ in range(3000)])
    print(f"n = {n:5d} | simulated spread {est.std():8.1f} | formula sigma/sqrt(n) {sigma / np.sqrt(n):8.1f}")
```
```text
n =   100 | simulated spread    134.0 | formula sigma/sqrt(n)    134.8
n =   500 | simulated spread     60.1 | formula sigma/sqrt(n)     60.3
n =  2000 | simulated spread     29.9 | formula sigma/sqrt(n)     30.1
```

The simulation and the formula agree. Notice the **square root**: to halve the error you must take **four times** as many observations. Going from 500 to 2,000 halves the standard error; going from 500 to 1,000 reduces it by only 29 percent. This is why surveys of 1,000 people can describe a whole country: the precision depends on `n`, not on the size of the population (as long as the population is much bigger than the sample).

The formula needs `sigma`, the spread of individual values in the *population*, which you do not know. In practice you replace it with the standard deviation of your *sample* (`ddof=1`, the unbiased version):

```python run
s = sample["monthly_spend"].std(ddof=1)
se_hat = s / np.sqrt(len(sample))
print(f"sample std {s:,.1f} | estimated SE {se_hat:,.1f} | true SE {sigma / np.sqrt(500):,.1f}")
```
```text
sample std 1,417.0 | estimated SE 63.4 | true SE 60.3
```

The estimated standard error from **one** sample is close to the true one. That is the miracle that makes inference possible: from a single sample you can estimate how much that very sample would wobble.

> **Predict the output.** A colleague's sample has 5,000 customers. Roughly how big is the standard error of their mean, compared with ours (n = 500)? And would a sample of 5,000 from a population of 200,000 be "a lot" of the population?

<details><summary>Answer</summary>

```python run
print("SE for n = 500   :", round(sigma / np.sqrt(500), 1))
print("SE for n = 5,000 :", round(sigma / np.sqrt(5000), 1))
print("ratio            :", round(np.sqrt(5000 / 500), 2))
print("fraction of the population sampled:", 5000 / 200_000)
```
```text
SE for n = 500   : 60.3
SE for n = 5,000 : 19.1
ratio            : 3.16
fraction of the population sampled: 0.025
```

Ten times the data gives an error that is `sqrt(10) = 3.16` times smaller, not 10 times. And 5,000 customers are only 2.5 percent of the population, yet that is enough for a precise estimate. What matters is the absolute size of the sample, not the fraction of the population.

</details>

### 2.3 The bell shape: the central limit theorem

The spend of individual customers is skewed to the right (a few big spenders). But the **means** of samples are bell-shaped. The **central limit theorem** says: the mean of many independent values is approximately normally distributed (bell-shaped), whatever the shape of the original data, when `n` is large enough. How large? It depends on the skew. For mildly skewed data, 30 can be enough; for very skewed data, hundreds.

```python run
print("skewness of individual spends :", round(stats.skew(spend), 2))
for n in (2, 10, 50, 500):
    est = np.array([rng.choice(spend, n, replace=False).mean() for _ in range(4000)])
    print(f"skewness of sample means, n = {n:3d}: {stats.skew(est):5.2f}")
```
```text
skewness of individual spends : 1.63
skewness of sample means, n =   2:  0.99
skewness of sample means, n =  10:  0.45
skewness of sample means, n =  50:  0.17
skewness of sample means, n = 500:  0.07
```

The skewness (0 means symmetric) falls towards zero as `n` grows. Because the shape of the sampling distribution becomes known (a normal curve), we can say how often the sample mean lands within a given distance of the truth: **about 95 percent of the time within 1.96 standard errors**. This is the foundation of the confidence interval in section 4.

```python run
within = np.abs(means_500 - TRUE_MEAN) <= 1.96 * sigma / np.sqrt(500)
print("share of the 5,000 sample means within 1.96 SE of the truth:", round(within.mean() * 100, 1), "%")
```
```text
share of the 5,000 sample means within 1.96 SE of the truth: 94.8 %
```

### 2.4 The law of large numbers

As the sample grows, the sample mean settles near the truth. This is the **law of large numbers**. We watch one growing sample: the running mean after the first 10, 100, 1,000, 10,000, 100,000 customers.

```python run
shuffled = pop["monthly_spend"].sample(frac=1, random_state=3).to_numpy()
for n in (10, 100, 1000, 10_000, 100_000):
    print(f"n = {n:7d} | running mean {shuffled[:n].mean():9,.1f} | error {shuffled[:n].mean() - TRUE_MEAN:+9,.1f}")
```
```text
n =      10 | running mean   2,319.2 | error    -183.2
n =     100 | running mean   2,208.2 | error    -294.3
n =    1000 | running mean   2,474.6 | error     -27.9
n =   10000 | running mean   2,466.1 | error     -36.3
n =  100000 | running mean   2,504.8 | error      +2.4
```

The error does not fall steadily: it jumps around and shrinks in the long run, at the `1/sqrt(n)` rate. A small sample can be lucky or unlucky; a very large one hardly is. Remember this contrast with the next section, because it is the key to the whole chapter: **a large sample fixes luck. It does not fix bias.**

## 3. Sampling bias

### 3.1 Precision is not accuracy

Imagine an archer. If the arrows land in a tight cluster, far from the target's centre, the archer is *precise* but not *accurate*. A large biased sample is that archer: the arrows (estimates) cluster tightly around the wrong value. The standard error says nothing about this. It measures the size of the cluster, not its distance from the target.

Bias comes from how units get into the sample. The sampling method decides who can appear. Let us build four plausible, careless methods and compare them with the fair simple random sample, at three sizes of sample.

| Method | How the sample is taken | What is wrong |
|---|---|---|
| **Random** | every customer has equal chance | nothing |
| **Convenience** | survey shown in the app to people who open it daily; heavy spenders open it more | big spenders are over-represented |
| **Undercoverage** | the database used only covers Metro customers | whole groups cannot be sampled |
| **Self-selection** | a survey link is sent to all; satisfied, high-spending customers answer more | the respondents choose themselves |

```python run
rng = np.random.default_rng(5)
N = len(pop)
w_conv = pop["monthly_spend"].to_numpy() ** 1.5                      # chance to be reached grows with spend
w_resp = np.exp((pop["monthly_spend"].to_numpy() - 2500) / 4000)     # chance to answer grows with spend
metro = (pop["city"] == "Metro").to_numpy()


def draw(method, n):
    if method == "random":
        idx = rng.choice(N, n, replace=False)
    elif method == "convenience":
        idx = rng.choice(N, n, replace=False, p=w_conv / w_conv.sum())
    elif method == "undercoverage":
        idx = rng.choice(np.flatnonzero(metro), n, replace=False)
    else:  # self-selection
        idx = rng.choice(N, n, replace=False, p=w_resp / w_resp.sum())
    return pop["monthly_spend"].to_numpy()[idx].mean()


rows = []
for method in ["random", "convenience", "undercoverage", "self-selection"]:
    row = {"method": method}
    for n in (200, 2000, 20000):
        row[f"n={n}"] = np.mean([draw(method, n) for _ in range(20)])      # average of 20 repeats: the centre of the cluster
    rows.append(row)
res = pd.DataFrame(rows).set_index("method")
res.loc["TRUTH"] = TRUE_MEAN
print(res.round(0).to_string())
```
```text
                  n=200   n=2000  n=20000
method                                   
random         2,516.00 2,505.00 2,500.00
convenience    3,661.00 3,642.00 3,519.00
undercoverage  3,204.00 3,194.00 3,198.00
self-selection 3,130.00 3,132.00 3,054.00
TRUTH          2,502.00 2,502.00 2,502.00
```

Each cell is the average over 20 repeated samples, so it shows where the cluster of estimates is centred. Read down any column and across any row.

- **Random** sits at the truth at every size (2,502): the cluster narrows, but its centre is right.
- **Convenience**, **undercoverage** and **self-selection** are centred at 3,050 to 3,660, far above 2,502, **at every sample size**. Taking 20,000 instead of 200 did not bring them to the truth; it only made the cluster tighter around the wrong number. (At 20,000, a tenth of the whole population, the convenience sample starts to run out of heavy spenders to pick, so it drifts a little towards the truth, but it stays far away.) That is a precise, confident, wrong answer, and a narrow confidence interval around it would be actively misleading.

> **Bias is a property of the method, not of the size.** No amount of data repairs a sampling method that systematically leaves some people out or over-selects others. The only repairs are to fix the method, or to correct the bias with extra knowledge (3.4).

### 3.2 Kinds of bias to look for

Bias has many faces. Learn the names; they are the checklist you run on every dataset you did not collect yourself.

| Bias | What happens | Example |
|---|---|---|
| **Selection / convenience** | the easy-to-reach units are not typical | surveying only people who open the app daily |
| **Undercoverage** | part of the population is not in the frame | a database without small-city customers |
| **Self-selection** | units choose whether to be in | opt-in surveys, online reviews |
| **Non-response** | those who do not answer differ from those who do | missing data in da.05 (MNAR) |
| **Survivorship** | only the survivors are observed | analysing "successful companies" that still exist |
| **Selection on the outcome** | the sample is chosen using the very thing you measure | studying only customers who complained |
| **Measurement bias** | the instrument leans one way | a scale that reads 2 kg high, a leading question |
| **Time bias** | the sample is from a special period | data from the festival month only |

Non-response is the same problem as MNAR in da.05: when missingness depends on the value itself, the observed rows are not a fair sample. Dropping the missing rows *is* a biased sample.

### 3.3 Survivorship bias, with numbers

A classic: a company reviews the ratings of its apps, but only apps still on the store. Poor apps were removed, so the survivors look good.

```python run
rng = np.random.default_rng(21)
quality = rng.normal(3.4, 0.8, 5000)                         # the true quality of 5,000 apps released
rating = np.clip(quality + rng.normal(0, 0.3, 5000), 1, 5)   # the star rating users give
stays = rng.random(5000) < 1 / (1 + np.exp(-(rating - 3.5) * 3))      # poor apps are removed more often
print(f"all 5,000 apps released   : mean rating {rating.mean():.2f}")
print(f"the {stays.sum()} apps still listed : mean rating {rating[stays].mean():.2f}")
print(f"share of apps that survived: {stays.mean() * 100:.0f} %")
```
```text
all 5,000 apps released   : mean rating 3.39
the 2343 apps still listed : mean rating 3.97
share of apps that survived: 47 %
```

An analyst who sees only the surviving apps believes the average app is a good one (4.0 stars), whereas the average app released is 3.4. The missing apps are not in the table at all, so there is no `NaN` to warn you. **Ask what is not in your data and why.** The same logic explains "this strategy worked for every successful company I studied": the unsuccessful companies that followed it are not around to be studied.

### 3.4 Partial repairs: stratification and weights

If you know something about the population, you can repair *part* of a bias. Suppose the sample over-represents Metro customers (undercoverage in a milder form), and you know the true share of each city from the customer database. **Post-stratification** weights each stratum by its true share.

```python run
rng = np.random.default_rng(8)
# a sample with a skewed city mix: Metro customers are three times as likely to be reached
w_city = np.where(pop["city"] == "Metro", 3.0, 1.0)
idx = rng.choice(N, 3000, replace=False, p=w_city / w_city.sum())
sm = pop.iloc[idx]

true_mix = pop["city"].value_counts(normalize=True)
sample_mix = sm["city"].value_counts(normalize=True)
by_city = sm.groupby("city")["monthly_spend"].mean()
print(pd.DataFrame({"true share": true_mix, "sample share": sample_mix, "mean spend in sample": by_city}).round(3).to_string())
print()
print(f"raw sample mean                 : {sm['monthly_spend'].mean():8,.1f}")
print(f"post-stratified (true weights)  : {(by_city * true_mix).sum():8,.1f}")
print(f"truth                           : {TRUE_MEAN:8,.1f}")
```
```text
       true share  sample share  mean spend in sample
city                                                 
Large        0.40          0.24              2,434.28
Metro        0.35          0.61              3,176.88
Small        0.25          0.15              1,739.09

raw sample mean                 :  2,786.5
post-stratified (true weights)  :  2,520.6
truth                           :  2,502.4
```

The raw mean is too high because Metro, the high-spending city, is over-represented. Weighting each city's mean by its **true** share removes the problem. The weighted estimator is the same weighted average that you used in da.06 (never average averages; weight by size).

Post-stratification repairs only what the strata capture. Apply it to the *convenience* sample of 3.1, where the bias is "heavy spenders are more likely to be reached", *within every city*:

```python run
rng = np.random.default_rng(9)
idx = rng.choice(N, 3000, replace=False, p=w_conv / w_conv.sum())
sc = pop.iloc[idx]
by_city_c = sc.groupby("city")["monthly_spend"].mean()
true_by_city = pop.groupby("city")["monthly_spend"].mean()
print(f"convenience sample, raw mean            : {sc['monthly_spend'].mean():8,.1f}")
print(f"convenience sample, post-stratified     : {(by_city_c * true_mix).sum():8,.1f}")
print(f"truth                                   : {TRUE_MEAN:8,.1f}")
print()
print(pd.DataFrame({"sample mean in city": by_city_c, "true mean in city": true_by_city}).round(0).to_string())
```
```text
convenience sample, raw mean            :  3,637.1
convenience sample, post-stratified     :  3,400.5
truth                                   :  2,502.4

       sample mean in city  true mean in city
city                                         
Large             3,292.00           2,394.00
Metro             4,270.00           3,196.00
Small             2,357.00           1,704.00
```

Post-stratification helps only a little here (3,637 to 3,401), because *inside each city* the sample still contains too many big spenders: every row of the second table is too high. The bias runs through the variable you are trying to measure, and no other variable you hold contains that information. Weighting corrects only the bias that your weighting variables explain. It is a good tool, not a cure. The honest statement for a biased sample is often: "the estimate is probably too high; here is the likely direction and size", not a corrected number with an interval around it.

> **Try it.** The random sample of section 1.2 (500 customers) gave a share of customers who reorder. In the convenience sample of 3.1, would you expect the share who reorder to be too high or too low, and why? Check with a sample of 3,000.

<details><summary>Answer</summary>

```python run
rng = np.random.default_rng(12)
idx = rng.choice(N, 3000, replace=False, p=w_conv / w_conv.sum())
print("convenience sample, share who reorder:", round(pop["reorders"].to_numpy()[idx].mean() * 100, 1), "%")
print("truth                                :", round(TRUE_SHARE * 100, 1), "%")
```
```text
convenience sample, share who reorder: 34.3 %
truth                                : 25.3 %
```

Too high. In this population, big spenders reorder more often, and the convenience method over-selects big spenders, so it over-selects reorderers too. The bias in one variable leaks into every variable that is related to the one that drove the selection. This is why a biased sample is dangerous even for questions you did not have in mind when you collected it.

</details>


## 4. Confidence intervals

### 4.1 From an estimate to a range

A single number, "mean spend is 2,578", is a **point estimate**. It invites false confidence, because it hides how much a second sample would differ. A **confidence interval** (CI) gives a range of plausible values for the parameter, built from the sample so that the procedure is right most of the time.

For a mean, the recipe is short:

```text
estimate  +/-  critical value  x  standard error
```

where the standard error is `s / sqrt(n)` (section 2.2), and the critical value comes from a table: about 1.96 for a 95 percent interval when `n` is large; slightly more for small `n` (the t distribution).

```python run
x = sample["monthly_spend"].to_numpy()
n = len(x)
mean, se = x.mean(), x.std(ddof=1) / np.sqrt(n)
t_crit = stats.t.ppf(0.975, df=n - 1)                       # the 97.5th percentile of the t distribution
lo, hi = mean - t_crit * se, mean + t_crit * se
print(f"n = {n}, mean = {mean:,.1f}, SE = {se:,.1f}, critical value = {t_crit:.3f}")
print(f"95% confidence interval: {lo:,.1f} to {hi:,.1f}")
print("truth inside the interval:", lo <= TRUE_MEAN <= hi)
print("scipy gives the same interval:", np.round(stats.t.interval(0.95, df=n - 1, loc=mean, scale=se), 1))
```
```text
n = 500, mean = 2,577.6, SE = 63.4, critical value = 1.965
95% confidence interval: 2,453.1 to 2,702.1
truth inside the interval: True
scipy gives the same interval: [2453.1 2702.1]
```

We report: "mean monthly spend is about 2,578, 95 percent CI 2,453 to 2,702 (n = 500)". The truth, 2,502, is inside. Notice that you can read three things from the interval at once: the best guess (the middle), the precision (the width), and the plausible range for the truth.

### 4.2 What "95 percent" really means

Here is the most misunderstood sentence in statistics. The 95 percent is **not** the probability that the truth lies in *this* interval (the truth is a fixed number: it is either in or not). It is a statement about the **procedure**: if you repeated the sampling and the interval-building many times, about 95 percent of the intervals you build would contain the truth. We can check this claim, because we know the truth. Draw 10,000 samples, build the interval of each, and count how many contain 2,502.

```python run
rng = np.random.default_rng(31)


def ci_mean(x, level=0.95):
    n = len(x)
    se = x.std(ddof=1) / np.sqrt(n)
    h = stats.t.ppf((1 + level) / 2, df=n - 1) * se
    return x.mean() - h, x.mean() + h


covers, widths, first = [], [], []
for i in range(10_000):
    lo_, hi_ = ci_mean(rng.choice(spend, 500, replace=False))
    covers.append(lo_ <= TRUE_MEAN <= hi_)
    widths.append(hi_ - lo_)
    if i < 8:
        first.append((lo_, hi_))
print(f"intervals that contain the truth: {np.mean(covers) * 100:.1f} % of 10,000   (the procedure's coverage)")
print(f"average width: {np.mean(widths):,.0f}")
print("\nthe first eight intervals:")
for lo_, hi_ in first:
    mark = "ok  " if lo_ <= TRUE_MEAN <= hi_ else "MISS"
    bar = " " * int((lo_ - 2250) / 10) + "[" + "-" * max(int((hi_ - lo_) / 10) - 1, 0) + "]"
    print(f"{mark} {lo_:7,.0f} to {hi_:7,.0f} {bar}")
print(f"{'':25}truth = {TRUE_MEAN:,.0f}")
```
```text
intervals that contain the truth: 94.5 % of 10,000   (the procedure's coverage)
average width: 237

the first eight intervals:
ok     2,349 to   2,576          [---------------------]
ok     2,483 to   2,744                        [-------------------------]
ok     2,300 to   2,525      [---------------------]
ok     2,339 to   2,566         [---------------------]
ok     2,359 to   2,594           [----------------------]
ok     2,300 to   2,516      [--------------------]
ok     2,457 to   2,702                     [-----------------------]
ok     2,302 to   2,520      [--------------------]
                         truth = 2,502
```

About 95 percent of the intervals contain the truth, and the rest miss it by bad luck. In real work you build **one** interval and cannot know whether it is one of the lucky 95 or one of the unlucky 5. That is the honest meaning: *a method that is right 19 times in 20*.

> **Predict the output.** If you ask for a 99 percent interval instead of 95 percent, will it be wider or narrower? What does the extra confidence cost?

<details><summary>Answer</summary>

```python run
for level in (0.80, 0.95, 0.99):
    lo_, hi_ = ci_mean(x, level)
    print(f"{int(level * 100)}% interval: {lo_:,.0f} to {hi_:,.0f}   width {hi_ - lo_:,.0f}")
```
```text
80% interval: 2,496 to 2,659   width 163
95% interval: 2,453 to 2,702   width 249
99% interval: 2,414 to 2,741   width 328
```

Wider. Being more sure that the interval catches the truth requires a bigger net. The price of confidence is width; the price of narrowness is confidence. The only way to get **both** a narrow and a confident interval is more data (or less variable data). 95 percent is a convention, not a law; whatever level you use, say it.

</details>

### 4.3 What a confidence interval is not

Five misreadings, all common, all wrong.

1. "**There is a 95 percent chance the truth is in this interval.**" The statement is about the method (see above). For a given interval, the truth is in or out.
2. "**95 percent of customers spend between 2,453 and 2,702.**" No: the interval is for the *mean*, not for individuals. Individual spends range from a few hundred to many thousands.
3. "**If two intervals overlap, there is no difference.**" Not reliable. Two intervals can overlap and the difference between the groups still be clearly nonzero; use the interval *for the difference* (4.6).
4. "**A narrow interval means the estimate is right.**" It means it is precise. A biased sample has a narrow interval around the wrong value (4.7).
5. "**The interval is where the next sample's mean will fall.**" No. The next sample mean varies by about `SE x sqrt(2)` around the truth, a wider range.

Check misreading 2 in code:

```python run
print(f"CI for the MEAN spend        : {ci_mean(x)[0]:8,.0f} to {ci_mean(x)[1]:8,.0f}")
print(f"range holding 95% of CUSTOMERS: {np.percentile(x, 2.5):8,.0f} to {np.percentile(x, 97.5):8,.0f}")
```
```text
CI for the MEAN spend        :    2,453 to    2,702
range holding 95% of CUSTOMERS:      749 to    6,133
```

The first describes where the average is; the second describes where people are. Mixing them up is one of the most frequent mistakes in reports.

### 4.4 Proportions

For a share (the fraction who reorder), the standard error is `sqrt(p(1-p)/n)`. The simple "normal" interval `p +/- 1.96 SE` works for moderate `p` and big `n`. For small counts or `p` close to 0 or 1 it can go below 0 or misbehave; the **Wilson** interval is better there.

```python run
k = int(sample["reorders"].sum())
p_hat = k / n
se_p = np.sqrt(p_hat * (1 - p_hat) / n)
print(f"{k} of {n} reorder: p = {p_hat:.3f}")
print(f"normal interval : {p_hat - 1.96 * se_p:.3f} to {p_hat + 1.96 * se_p:.3f}")
ci = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method="wilson")
print(f"Wilson interval : {ci.low:.3f} to {ci.high:.3f}")
print(f"truth           : {TRUE_SHARE:.3f}")
print()
print("a rare event: 2 successes in 40")
k2, n2 = 2, 40
se2 = np.sqrt(k2 / n2 * (1 - k2 / n2) / n2)
print(f"  normal interval: {k2 / n2 - 1.96 * se2:.3f} to {k2 / n2 + 1.96 * se2:.3f}   <- a negative lower limit is impossible")
ci2 = stats.binomtest(k2, n2).proportion_ci(confidence_level=0.95, method="wilson")
print(f"  Wilson interval: {ci2.low:.3f} to {ci2.high:.3f}")
```
```text
119 of 500 reorder: p = 0.238
normal interval : 0.201 to 0.275
Wilson interval : 0.203 to 0.277
truth           : 0.253

a rare event: 2 successes in 40
  normal interval: -0.018 to 0.118   <- a negative lower limit is impossible
  Wilson interval: 0.014 to 0.165
```

For ordinary values the two agree. For 2 events in 40 the normal formula gives a negative lower limit, which is nonsense for a share; Wilson stays inside 0 to 1. A good habit: when counts are small, use Wilson and always show the counts (`k of n`) beside the percentage.

### 4.5 The bootstrap: an interval for almost anything

The formula for the mean is special. What is the standard error of the *median*? Of the 90th percentile? Of a ratio? There are formulas for some and none for others. The **bootstrap** gives a general answer with a simple idea: your sample is the best picture you have of the population, so *resample from your sample* (with replacement, same size) many times, compute the statistic each time, and see how it varies.

```python run
def bootstrap_ci(x, stat, B=5000, level=0.95, seed=0):
    rng = np.random.default_rng(seed)
    x = np.asarray(x)
    boots = np.array([stat(rng.choice(x, len(x), replace=True)) for _ in range(B)])
    a = (1 - level) / 2
    return np.quantile(boots, [a, 1 - a]), boots.std()


for name, f, true_val in [("mean", np.mean, TRUE_MEAN), ("median", np.median, pop["monthly_spend"].median()),
                          ("90th percentile", lambda v: np.quantile(v, .9), pop["monthly_spend"].quantile(.9))]:
    (lo_, hi_), sd = bootstrap_ci(x, f)
    print(f"{name:16} estimate {f(x):8,.0f} | 95% bootstrap CI {lo_:8,.0f} to {hi_:8,.0f} | SE {sd:6,.0f} | truth {true_val:8,.0f}")
(lo_, hi_), _ = bootstrap_ci(x, np.mean)
print(f"\nt-interval for the mean : {ci_mean(x)[0]:,.0f} to {ci_mean(x)[1]:,.0f}")
```
```text
mean             estimate    2,578 | 95% bootstrap CI    2,448 to    2,705 | SE     64 | truth    2,502
median           estimate    2,284 | 95% bootstrap CI    2,165 to    2,451 | SE     59 | truth    2,205
90th percentile  estimate    4,410 | 95% bootstrap CI    3,987 to    4,686 | SE    194 | truth    4,241

t-interval for the mean : 2,453 to 2,702
```

For the mean, the bootstrap and the t-interval agree. For the median and the 90th percentile, the bootstrap gives intervals where we had no formula. Notice that the interval for the 90th percentile is much wider than for the mean: the tail is where there are few data. Three warnings about the bootstrap: it cannot fix **bias** (it resamples what you have); it needs a decent sample (with 15 values it is unreliable); and for statistics driven by the extremes (the maximum) it fails.

### 4.6 A confidence interval for a difference

Most real questions compare two groups: "do Metro customers spend more than Large-city ones?" Compute the difference and the interval **of the difference**. The standard error of a difference of two independent means is `sqrt(SE1^2 + SE2^2)`.

```python run
rng = np.random.default_rng(14)
a = pop[pop["city"] == "Metro"]["monthly_spend"].sample(300, random_state=1).to_numpy()
b = pop[pop["city"] == "Large"]["monthly_spend"].sample(300, random_state=2).to_numpy()
diff = a.mean() - b.mean()
se_d = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
res = stats.ttest_ind(a, b, equal_var=False)                         # Welch's test
ci_d = res.confidence_interval(0.95)
print(f"Metro mean {a.mean():,.0f} | Large mean {b.mean():,.0f} | difference {diff:,.0f}")
print(f"by hand : {diff - 1.96 * se_d:,.0f} to {diff + 1.96 * se_d:,.0f}")
print(f"scipy   : {ci_d.low:,.0f} to {ci_d.high:,.0f}")
print(f"truth   : {pop[pop['city'] == 'Metro']['monthly_spend'].mean() - pop[pop['city'] == 'Large']['monthly_spend'].mean():,.0f}")
print("interval contains 0:", ci_d.low <= 0 <= ci_d.high)
```
```text
Metro mean 3,223 | Large mean 2,371 | difference 852
by hand : 644 to 1,060
scipy   : 644 to 1,061
truth   : 802
interval contains 0: False
```

The report reads: "Metro customers spend about 850 more per month (95 percent CI 640 to 1,060)". An interval that **excludes zero** says the direction of the difference is clear; the width says how large it plausibly is. This one sentence carries more information than "p < 0.05". The same idea holds for a difference of two shares (conversion rates):

```python run
def diff_prop_ci(k1, n1, k2, n2, z=1.96):
    p1, p2 = k1 / n1, k2 / n2
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return p1 - p2, (p1 - p2 - z * se, p1 - p2 + z * se)


d, (lo_, hi_) = diff_prop_ci(130, 1000, 100, 1000)
print(f"13.0% against 10.0%: difference {d * 100:.1f} points, 95% CI {lo_ * 100:.1f} to {hi_ * 100:.1f} points")
```
```text
13.0% against 10.0%: difference 3.0 points, 95% CI 0.2 to 5.8 points
```

### 4.7 A narrow interval around the wrong value

Section 3 warned that bias beats precision. Here is the proof in the language of intervals: build the 95 percent interval from the *convenience* sample and check how often it contains the truth.

```python run
rng = np.random.default_rng(55)
cover_bad = []
for _ in range(500):
    idx = rng.choice(N, 2000, replace=False, p=w_conv / w_conv.sum())
    lo_, hi_ = ci_mean(spend[idx])
    cover_bad.append(lo_ <= TRUE_MEAN <= hi_)
print(f"intervals from the convenience sample that contain the truth: {np.mean(cover_bad) * 100:.0f} % (nominal 95 %)")
lo_, hi_ = ci_mean(spend[idx])
print(f"the last one: {lo_:,.0f} to {hi_:,.0f}   | truth {TRUE_MEAN:,.0f}")
```
```text
intervals from the convenience sample that contain the truth: 0 % (nominal 95 %)
the last one: 3,518 to 3,682   | truth 2,502
```

The nominal "95 percent confidence" interval contains the truth **0 percent** of the time. The interval measures luck only; when the method is biased, the interval is a precise statement about the wrong thing. A confidence interval is always conditional on a **representative sample**, and no formula can check that for you.

### 4.8 How many observations do I need?

Because the margin of error is `1.96 x sigma / sqrt(n)`, you can solve for `n` before collecting data: to get a margin of `m`, you need `n = (1.96 x sigma / m)^2`.

```python run
for m in (200, 100, 50, 25):
    need = (1.96 * sigma / m) ** 2
    print(f"margin +/-{m:4d} rupees needs n = {need:9,.0f}")
```
```text
margin +/- 200 rupees needs n =       174
margin +/- 100 rupees needs n =       698
margin +/-  50 rupees needs n =     2,791
margin +/-  25 rupees needs n =    11,164
```

Halving the margin costs four times the sample: planning is cheap, and fixing a too-small study is not. To use this you need a guess for `sigma` (from a pilot, from old data), and it assumes a fair sample.

> **Try it.** For a share close to 25 percent, what sample size gives a margin of error of 2 percentage points (95 percent confidence)? Use `n = 1.96^2 x p(1-p) / m^2`. What if you do not know `p`?

<details><summary>Answer</summary>

```python run
for p in (0.25, 0.5):
    print(f"p = {p}: n = {1.96 ** 2 * p * (1 - p) / 0.02 ** 2:,.0f}")
```
```text
p = 0.25: n = 1,801
p = 0.5: n = 2,401
```

About 1,800 for `p = 0.25`. If you have no idea of `p`, use 0.5, which maximises `p(1-p)` and gives the worst case, 2,401. That is why opinion polls of about 1,000 people quote a margin near 3 points: `1.96 x 0.5 / sqrt(1000)` is 3.1 percent.

</details>

## 5. Comparing groups and the meaning of a p-value

### 5.1 The A/B setting

A company changes its checkout page. Half of the visitors see the old page (A), half the new one (B), assigned at random. After a week: A converts 10.0 percent of 4,000 visitors, B converts 11.5 percent of 4,000. Is B better, or is that luck? The tool is a **hypothesis test**.

```python run
kA, nA, kB, nB = 400, 4000, 460, 4000
pA, pB = kA / nA, kB / nB
d, (lo_, hi_) = diff_prop_ci(kB, nB, kA, nA)
print(f"A: {pA * 100:.1f}%   B: {pB * 100:.1f}%   difference {d * 100:.1f} points, 95% CI {lo_ * 100:.2f} to {hi_ * 100:.2f}")
# a two-proportion z-test
p_pool = (kA + kB) / (nA + nB)
z = (pB - pA) / np.sqrt(p_pool * (1 - p_pool) * (1 / nA + 1 / nB))
p_value = 2 * (1 - stats.norm.cdf(abs(z)))
print(f"z = {z:.2f}, two-sided p-value = {p_value:.4f}")
```
```text
A: 10.0%   B: 11.5%   difference 1.5 points, 95% CI 0.14 to 2.86
z = 2.17, two-sided p-value = 0.0303
```

### 5.2 What the p-value is

Start from a skeptic: "There is no real difference; the pages convert equally, and the gap is luck." This is the **null hypothesis**. The **p-value** answers one question:

> *If the null hypothesis were true, how often would luck alone produce a difference at least as large as the one we saw?*

A small p-value means "that would be rare under pure luck", which makes the skeptic's story hard to believe. The conventional line is 0.05. Be exact about what the number is **not**: it is not the probability that the null hypothesis is true, not the probability that B is better, and not the size of the effect.

We can build a p-value from nothing but shuffling, which makes its meaning concrete. Under the null, the labels A and B are meaningless: pool all 8,000 visitors, shuffle the labels, split again, and see how large a difference appears by chance. This is a **permutation test**.

```python run
rng = np.random.default_rng(2)
outcomes = np.concatenate([np.ones(kA), np.zeros(nA - kA), np.ones(kB), np.zeros(nB - kB)])
observed = pB - pA
perm = np.empty(10_000)
for i in range(10_000):
    rng.shuffle(outcomes)
    perm[i] = outcomes[nA:].mean() - outcomes[:nA].mean()
p_perm = np.mean(np.abs(perm) >= abs(observed))
print(f"observed difference : {observed * 100:.2f} points")
print(f"differences that luck alone produced (10,000 shuffles): typical size {perm.std() * 100:.2f} points")
print(f"share of shuffles at least as extreme: {p_perm:.4f}   (z-test gave {p_value:.4f})")
text_hist(perm * 100, bins=9, width=30, decimals=1)
```
```text
observed difference : 1.50 points
differences that luck alone produced (10,000 shuffles): typical size 0.70 points
share of shuffles at least as extreme: 0.0345   (z-test gave 0.0303)
     -2.5 -      -2.0 |  26
     -2.0 -      -1.4 | # 169
     -1.4 -      -0.9 | ######## 856
     -0.9 -      -0.3 | ##################### 2191
     -0.3 -       0.2 | ############################## 3015
      0.2 -       0.8 | ####################### 2359
      0.8 -       1.3 | ########## 1077
      1.3 -       1.9 | ## 269
      1.9 -       2.4 |  38
```

Only a small share of the shuffles produce a gap as large as 1.5 points. The permutation p-value and the z-test p-value agree. If you can shuffle, you understand the p-value.

### 5.3 When there is no effect

What does a p-value look like when the null is *true*? Simulate 10,000 A/B tests in which both pages have the same 10 percent conversion.

```python run
rng = np.random.default_rng(3)
ps = []
for _ in range(10_000):
    ka, kb = rng.binomial(4000, .10, 2)
    pp = (ka + kb) / 8000
    zz = (kb - ka) / 4000 / np.sqrt(pp * (1 - pp) * (2 / 4000))
    ps.append(2 * (1 - stats.norm.cdf(abs(zz))))
ps = np.array(ps)
print(f"tests with p < 0.05 when NOTHING is going on: {np.mean(ps < .05) * 100:.1f} %")
print(f"tests with p < 0.01 when NOTHING is going on: {np.mean(ps < .01) * 100:.1f} %")
text_hist(ps, bins=10, width=30, decimals=1)
```
```text
tests with p < 0.05 when NOTHING is going on: 5.1 %
tests with p < 0.01 when NOTHING is going on: 1.1 %
      0.0 -       0.1 | ########################## 1031
      0.1 -       0.2 | ########################## 1008
      0.2 -       0.3 | ########################## 996
      0.3 -       0.4 | ######################### 985
      0.4 -       0.5 | ######################## 949
      0.5 -       0.6 | ########################### 1035
      0.6 -       0.7 | ######################### 969
      0.7 -       0.8 | ############################## 1149
      0.8 -       0.9 | ###################### 880
      0.9 -       1.0 | ########################## 998
```

When there is no effect, p-values are spread **evenly** between 0 and 1, and 5 percent of tests fall below 0.05 anyway. That is what the 0.05 line *means*: you accept being fooled one time in twenty. This simple fact is the root of the next problem.

### 5.4 Many tests, many false alarms

An analyst compares 20 customer segments on 20 outcomes. Even if nothing is real, about one result in twenty will be "significant". Report only the winner and you have a publication-ready false discovery.

```python run
rng = np.random.default_rng(11)
n_each = 300
found = []
for trial in range(20):
    g1 = rng.normal(100, 20, n_each)                    # two groups from the SAME distribution
    g2 = rng.normal(100, 20, n_each)
    found.append(stats.ttest_ind(g1, g2, equal_var=False).pvalue)
found = np.array(found)
print("20 comparisons where nothing differs")
print("p-values below 0.05:", int((found < .05).sum()), "| smallest p:", round(found.min(), 4))
print("chance of at least one p < 0.05 in 20 null tests:", round((1 - .95 ** 20) * 100, 1), "%")
print("Bonferroni threshold (0.05 / 20):", 0.05 / 20, "-> p-values below it:", int((found < .05 / 20).sum()))
```
```text
20 comparisons where nothing differs
p-values below 0.05: 1 | smallest p: 0.0291
chance of at least one p < 0.05 in 20 null tests: 64.2 %
Bonferroni threshold (0.05 / 20): 0.0025 -> p-values below it: 0
```

The chance of at least one false alarm in 20 independent tests is 64 percent. Three defences: **decide the questions before looking** (pre-register what you will test); **correct** for the number of tests (the Bonferroni rule divides the threshold by the number of tests; stricter but simple); and **report all** the comparisons you ran, not only the interesting ones. Slicing the data until something is significant is called *p-hacking* (or "the garden of forking paths"), and it produces results that do not repeat.

### 5.5 Not significant is not "no effect"

A test with a small sample may fail to detect a real difference. The inability to reject the null is **absence of evidence, not evidence of absence**. The probability that a test detects a real effect of a given size is its **power**. Simulate: the true improvement is 1.5 points (10.0 to 11.5 percent), as in our A/B test. How often does a test with `n` per group call it significant?

```python run
def power(p0, p1, n, sims=3000, seed=5):
    rng = np.random.default_rng(seed)
    ka, kb = rng.binomial(n, p0, sims), rng.binomial(n, p1, sims)
    pp = (ka + kb) / (2 * n)
    z = (kb - ka) / n / np.sqrt(pp * (1 - pp) * (2 / n))
    return np.mean(2 * (1 - stats.norm.cdf(np.abs(z))) < .05)


for n_group in (200, 500, 1000, 2000, 4000, 8000):
    print(f"n per group = {n_group:5d} -> power {power(.10, .115, n_group) * 100:5.1f} %")
```
```text
n per group =   200 -> power   7.2 %
n per group =   500 -> power  11.9 %
n per group =  1000 -> power  19.6 %
n per group =  2000 -> power  34.0 %
n per group =  4000 -> power  57.4 %
n per group =  8000 -> power  85.8 %
```

With 500 per group, the test notices the real improvement less than one time in five. A team that runs such an experiment, sees "p = 0.4, no significant difference", and drops the idea has discarded a good change because the experiment was too small to see it. **Plan the sample size before the test** (the margin formula of 4.8 is the same idea), and when a result is not significant, look at the confidence interval: it will be wide, and it will show that the data are *compatible with* both "no effect" and "a useful effect".

```python run
d, (lo_, hi_) = diff_prop_ci(int(.115 * 500), 500, int(.10 * 500), 500)
print(f"n = 500 per group: difference {d * 100:.1f} points, 95% CI {lo_ * 100:.1f} to {hi_ * 100:.1f}  -> includes 0, and includes +5")
```
```text
n = 500 per group: difference 1.4 points, 95% CI -2.4 to 5.2  -> includes 0, and includes +5
```

## 6. Practical against statistical significance

### 6.1 Two different questions

"Is the effect **real**?" is the question a p-value or an interval answers (is it distinguishable from luck?). "Is the effect **big enough to matter**?" is a separate question about money, time and decisions. Mixing the two is the commonest misuse of statistics. The word *significant* in "statistically significant" does not mean *important*.

The sample size decides how small an effect can be called significant. With enough data, any difference, however tiny, becomes "significant".

```python run
def ab_summary(pA, pB, n):
    kA, kB = int(round(pA * n)), int(round(pB * n))
    d, (lo_, hi_) = diff_prop_ci(kB, n, kA, n)
    pp = (kA + kB) / (2 * n)
    z = d / np.sqrt(pp * (1 - pp) * 2 / n)
    return {"n per group": n, "A %": pA * 100, "B %": pB * 100, "diff (points)": d * 100,
            "CI low": lo_ * 100, "CI high": hi_ * 100, "p-value": 2 * (1 - stats.norm.cdf(abs(z)))}


tbl = pd.DataFrame([ab_summary(.1000, .1010, 4_000_000), ab_summary(.100, .115, 800), ab_summary(.100, .115, 4000)])
tbl.index = ["tiny effect, huge sample", "big effect, small sample", "big effect, big sample"]
print(tbl.assign(**{'p-value': tbl['p-value'].map('{:.2g}'.format)}).round(4).to_string())
```
```text
                          n per group   A %   B %  diff (points)  CI low  CI high  p-value
tiny effect, huge sample      4000000 10.00 10.10           0.10    0.06     0.14  2.6e-06
big effect, small sample          800 10.00 11.50           1.50   -1.53     4.53     0.33
big effect, big sample           4000 10.00 11.50           1.50    0.14     2.86     0.03
```

Read the three rows.

- **Huge sample, tiny effect.** B converts 10.10 percent against 10.00 percent: a difference of **0.1 points**. With four million visitors per group the p-value is about 0.000003: *highly significant*. But the confidence interval says the effect is between 0.06 and 0.14 points, a change that may be worth less than the cost of maintaining the new page.
- **Small sample, big effect.** A 1.5-point improvement with 800 visitors per group is **not** significant (p = 0.33), and the interval runs from about −1.5 to +4.5 points. The effect may be large; the experiment is too small to say.
- **Big effect, big sample.** The same 1.5 points with 4,000 per group: significant (p = 0.03), with an interval from 0.1 to 2.9 points that excludes zero but is still wide.

### 6.2 Effect size and the minimum effect of interest

An **effect size** expresses how big a difference is, in units people understand: rupees, percentage points, minutes, or a ratio. State it as an absolute difference (+0.05 points) *and* a relative one (+0.5 percent), because relative changes on small bases sound dramatic. Often a standardised effect size is also useful: **Cohen's d**, the difference of means in units of the standard deviation (about 0.2 small, 0.5 medium, 0.8 large, as rough guides only).

```python run
def cohens_d(a, b):
    sp = np.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return (a.mean() - b.mean()) / sp


print("Metro against Large, spend: d =", round(cohens_d(a, b), 2))
```
```text
Metro against Large, spend: d = 0.66
```

The key practical step is to decide **before the analysis** the *smallest effect that would change a decision*: the **minimum effect of interest** (MEI). For the checkout page, perhaps +0.5 points is the smallest gain that pays for the redesign. Then read the confidence interval against it. There are only three honest outcomes:

| Where the interval lies | Conclusion |
|---|---|
| entirely **above** the MEI | the effect is real and worth having |
| entirely **below** the MEI (including negative values) | the effect is real or absent, but too small to matter |
| **straddles** the MEI | inconclusive: the data cannot tell; collect more or decide under uncertainty |

```python run
MEI = 0.5                                              # points of conversion
def verdict(lo_, hi_, mei=MEI):
    if lo_ > mei: return "worth it: the whole interval is above the minimum effect"
    if hi_ < mei: return "not worth it: the whole interval is below the minimum effect"
    return "inconclusive: the interval contains the minimum effect"


for name, row in tbl.iterrows():
    print(f"{name:26} CI [{row['CI low']:5.2f}, {row['CI high']:5.2f}] -> {verdict(row['CI low'], row['CI high'])}")
```
```text
tiny effect, huge sample   CI [ 0.06,  0.14] -> not worth it: the whole interval is below the minimum effect
big effect, small sample   CI [-1.53,  4.53] -> inconclusive: the interval contains the minimum effect
big effect, big sample     CI [ 0.14,  2.86] -> inconclusive: the interval contains the minimum effect
```

The first row, the "highly significant" one, is classed **not worth it**; the second, the "not significant" one, is **inconclusive** (not "no effect"); the third is also **inconclusive** against a threshold of 0.5 points, although its p-value is below 0.05. A p-value alone would have said "yes, no, yes", and each of those answers would have hidden something. Only the interval shows what the data can and cannot support. With a much bigger test (20,000 per group, below) the third row becomes a clear "worth it".

### 6.3 How to speak about results

Prefer sentences that give the size and the uncertainty, and avoid the word "significant" without saying which kind.

| Instead of | Say |
|---|---|
| "The result is significant (p < 0.05)." | "B converts 1.5 points higher (95% CI 0.1 to 2.9); the lower end is below our 0.5-point threshold, so the gain is not yet established." |
| "There was no significant difference." | "We cannot rule out a difference of up to 5 points either way; the test was too small to tell." |
| "The effect is highly significant (p < 0.001)." | "The effect is small: +0.05 points (CI 0.02 to 0.08); it will not repay the cost." |
| "We proved that..." | "The data are consistent with..." |

> **Try it.** In the A/B test of 5.1 (A: 400 of 4,000; B: 460 of 4,000), where is the confidence interval relative to the minimum effect of 0.5 points, and what is the verdict? How would the verdict change with 20,000 visitors per group and the same observed rates?

<details><summary>Answer</summary>

```python run
for n_ in (4000, 20000):
    r = ab_summary(.100, .115, n_)
    print(f"n per group {n_:6d}: CI [{r['CI low']:.2f}, {r['CI high']:.2f}] -> {verdict(r['CI low'], r['CI high'])}")
```
```text
n per group   4000: CI [0.14, 2.86] -> inconclusive: the interval contains the minimum effect
n per group  20000: CI [0.89, 2.11] -> worth it: the whole interval is above the minimum effect
```

With 4,000 per group, the interval runs from about 0.14 to 2.86: it contains 0.5, so the verdict is **inconclusive** with respect to the threshold, although the p-value (0.03) says "significant". With 20,000 per group the interval narrows to about 0.9 to 2.1 and the verdict becomes "worth it". The observed rates are identical; only the amount of data differs. This is why "significant" must never be the end of the sentence.

</details>


## 7. Correlation

### 7.1 What a correlation measures

The **correlation coefficient** `r` (Pearson) measures how closely two numeric variables follow a **straight-line** pattern. It is between −1 (a perfect downward line) and +1 (a perfect upward line); 0 means no straight-line relation. It is the covariance divided by the two standard deviations, which is the same as the average product of the two variables once each is converted to z-scores (distance from its mean in units of its standard deviation).

```python run
age_s, spend_s = sample["age"].to_numpy(float), sample["monthly_spend"].to_numpy(float)
za, zs = (age_s - age_s.mean()) / age_s.std(), (spend_s - spend_s.mean()) / spend_s.std()
print("r by the z-score average :", round(float(np.mean(za * zs)), 4))
print("r from numpy             :", round(float(np.corrcoef(age_s, spend_s)[0, 1]), 4))
res = stats.pearsonr(age_s, spend_s)
print("r from scipy             :", round(float(res.statistic), 4), "| 95% CI", np.round(res.confidence_interval(0.95), 3))
print("r in the whole population:", round(float(np.corrcoef(pop['age'], pop['monthly_spend'])[0, 1]), 4))
```
```text
r by the z-score average : 0.0896
r from numpy             : 0.0896
r from scipy             : 0.0896 | 95% CI [0.002 0.176]
r in the whole population: 0.0691
```

Like any statistic from a sample, `r` has uncertainty: the sample gives a weak positive value, with an interval that comes close to zero. Report the interval, not only `r`.

How to read the size? There is no universal answer, but a rough guide for social and business data: `|r|` below 0.1 negligible, 0.1 to 0.3 weak, 0.3 to 0.5 moderate, above 0.5 strong. The square, `r^2`, is the share of the variation in one variable that a straight line on the other accounts for: `r = 0.3` explains 9 percent.

### 7.2 Always look: Anscombe's quartet

A single number can hide the shape of the data. In 1973 the statistician Francis Anscombe made four small datasets that have **nearly identical** means, variances and correlations, and look completely different.

```python run
x123 = np.array([10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5], float)
sets = {
    "I   (a line with noise)": (x123, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
    "II  (a curve)":           (x123, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
    "III (a line + 1 outlier)": (x123, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
    "IV  (one leverage point)": (np.array([8] * 7 + [19] + [8] * 3, float), [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
}
rows = []
for name, (xx, yy) in sets.items():
    yy = np.array(yy)
    slope, intercept = np.polyfit(xx, yy, 1)
    rows.append({"dataset": name, "mean y": yy.mean(), "std y": yy.std(ddof=1), "r": np.corrcoef(xx, yy)[0, 1], "slope": slope})
print(pd.DataFrame(rows).round(2).to_string(index=False))
```
```text
                 dataset  mean y  std y    r  slope
 I   (a line with noise)    7.50   2.03 0.82   0.50
           II  (a curve)    7.50   2.03 0.82   0.50
III (a line + 1 outlier)    7.50   2.03 0.82   0.50
IV  (one leverage point)    7.50   2.03 0.82   0.50
```

The four rows are the same to two decimals: r = 0.82, slope = 0.50. Yet dataset II is a perfect curve (a line is the wrong model), III is a perfect line spoiled by one outlier, and IV has all but one of its points at the same x, so the whole correlation rests on a single point. Without a look at the data, you could not tell. The lesson is a rule: **never report a correlation without having looked at the scatter** (da.09 teaches plots; for now, a table of binned averages works).

```python run
sample_b = sample.assign(age_band=pd.cut(sample["age"], [17, 25, 35, 45, 71]))
print(sample_b.groupby("age_band", observed=True)["monthly_spend"].agg(["size", "mean", "median"]).round(0).to_string())
```
```text
          size     mean   median
age_band                        
(17, 25]    90 2,476.00 2,284.00
(25, 35]   149 2,452.00 2,138.00
(35, 45]   183 2,626.00 2,378.00
(45, 71]    78 2,820.00 2,470.00
```

### 7.3 Where Pearson's `r` fails

**Outliers.** One extreme point can create or destroy a correlation (Anscombe III and IV).

**Non-linear relations.** `r` only sees straight lines. A perfect curve can have `r = 0`:

```python run
xx = np.linspace(-3, 3, 61)
yy = xx ** 2                                              # y is completely determined by x
print("Pearson r for y = x^2 on a symmetric range:", round(float(np.corrcoef(xx, yy)[0, 1]), 3))
print("Spearman (ranks):", round(float(stats.spearmanr(xx, yy).statistic), 3))
xm = np.linspace(0, 3, 31)
print("Pearson r for y = x^2 on x from 0 to 3   :", round(float(np.corrcoef(xm, xm ** 2)[0, 1]), 3))
print("Spearman r for the same data             :", round(float(stats.spearmanr(xm, xm ** 2).statistic), 3))
```
```text
Pearson r for y = x^2 on a symmetric range: 0.0
Spearman (ranks): 0.016
Pearson r for y = x^2 on x from 0 to 3   : 0.966
Spearman r for the same data             : 1.0
```

On a symmetric range the "perfectly determined" relation has correlation zero, because the left half goes down and the right half goes up. On the positive half `r` is high (0.97) but not 1, since the curve is not a line, while **Spearman's rank correlation** is exactly 1: it only asks whether higher x goes with higher y (monotonic), not whether the pattern is straight. Spearman is also less shaken by outliers and a good second look at skewed variables such as spend.

**Restricted range.** If you look only at a narrow slice of x, the correlation shrinks, even when the relation is strong. Example: height and basketball skill among professional players. Everybody is tall, so height seems to matter little.

```python run
rng = np.random.default_rng(9)
score = rng.normal(0, 1, 5000)                              # an admission test score
success = 0.6 * score + rng.normal(0, 0.8, 5000)           # later performance
print("r among all applicants        :", round(float(np.corrcoef(score, success)[0, 1]), 2))
top = score > 1                                             # only the top 16 percent are admitted
print("r among admitted students only:", round(float(np.corrcoef(score[top], success[top])[0, 1]), 2))
```
```text
r among all applicants        : 0.61
r among admitted students only: 0.32
```

A university that studies only the students it admitted finds that the test hardly predicts success, and may conclude that the test is useless. It is a selection effect (section 3) in disguise.

### 7.4 Spurious correlations

Two things that both trend over time are correlated by that fact alone. Take two **random walks**, series that are pure accumulated noise with no connection at all:

```python run
rng = np.random.default_rng(17)
rs = []
for _ in range(1000):
    a_ = np.cumsum(rng.normal(size=100))
    b_ = np.cumsum(rng.normal(size=100))
    rs.append(np.corrcoef(a_, b_)[0, 1])
rs = np.array(rs)
print(f"1,000 pairs of unrelated random walks of length 100:")
print(f"  share with |r| > 0.5 : {np.mean(np.abs(rs) > .5) * 100:.0f} %")
print(f"  share with |r| > 0.8 : {np.mean(np.abs(rs) > .8) * 100:.0f} %")
```
```text
1,000 pairs of unrelated random walks of length 100:
  share with |r| > 0.5 : 40 %
  share with |r| > 0.8 : 8 %
```

Four in ten pairs of unrelated trending series show a correlation above 0.5 in absolute value, and one in twelve above 0.8. This is why headlines like "ice cream sales track the stock market" or "cheese consumption tracks deaths by bedsheet tangling" exist. When you correlate two time series, first remove the trend (take differences or growth rates) or compare changes, not levels.

The second source is **data dredging**: the more pairs you test, the more impressive coincidences you find (section 5.4). With 100 unrelated variables and 50 rows there are 4,950 pairs:

```python run
rng = np.random.default_rng(23)
junk = rng.normal(size=(50, 100))
cm = np.corrcoef(junk, rowvar=False)
iu = np.triu_indices(100, k=1)
pairs = cm[iu]
print("pairs of unrelated variables:", len(pairs))
print("largest |r| found           :", round(float(np.abs(pairs).max()), 3))
print("pairs with |r| > 0.3        :", int((np.abs(pairs) > .3).sum()), "(each looks 'moderate', all are noise)")
```
```text
pairs of unrelated variables: 4950
largest |r| found           : 0.472
pairs with |r| > 0.3        : 170 (each looks 'moderate', all are noise)
```

A scatter plot of the winning pair would look convincing, and it means nothing. If a correlation came from a search, say so, and test it on **new data**.

## 8. Causation and confounders

### 8.1 Why correlation is not enough

When two variables, A and B, move together in your data, there are at least four explanations.

| Explanation | Picture | Example |
|---|---|---|
| A causes B | A → B | a discount raises sales |
| B causes A (**reverse causation**) | B → A | stores in busy areas run more promotions; busy areas also sell more |
| **A confounder** C causes both | A ← C → B | hot weather raises ice cream sales and swimming accidents |
| Coincidence or selection | -- | a trend, a search among many pairs, a biased sample |

Observational data cannot tell these stories apart by themselves. The correlation is a fact about the numbers; "A causes B" is a claim about what would happen if you **changed** A. To change A and watch B you need an experiment, or an argument that no confounder is left.

### 8.2 A confounder in action

Hot days increase ice cream sales, and hot days also increase the number of people who swim, and so the number of swimming accidents. Ice cream does not cause accidents.

```python run
rng = np.random.default_rng(30)
days = 365
temp = rng.normal(25, 7, days)                                        # the confounder
ice_cream = 40 + 6 * temp + rng.normal(0, 25, days)                   # depends on temperature only
accidents = 1 + 0.15 * temp + rng.normal(0, 1.2, days)                # depends on temperature only
d = pd.DataFrame({"temp": temp, "ice_cream": ice_cream, "accidents": accidents})
print("correlation ice cream - accidents:", round(float(d["ice_cream"].corr(d["accidents"])), 2))
```
```text
correlation ice cream - accidents: 0.58
```

A clear correlation (0.58), with no causal link at all. Now **hold the confounder fixed**: look within narrow bands of temperature, and the relation disappears.

```python run
d["band"] = pd.cut(d["temp"], [-10, 15, 20, 25, 30, 50])
within = d.groupby("band", observed=True).apply(lambda g: g["ice_cream"].corr(g["accidents"]), include_groups=False)
print(within.round(2).to_string())
# the same idea in one number: partial correlation = correlation of the parts temperature cannot explain
r_ice = d["ice_cream"] - np.polyval(np.polyfit(d["temp"], d["ice_cream"], 1), d["temp"])
r_acc = d["accidents"] - np.polyval(np.polyfit(d["temp"], d["accidents"], 1), d["temp"])
print("partial correlation, temperature removed:", round(float(np.corrcoef(r_ice, r_acc)[0, 1]), 2))
```
```text
band
(-10, 15]   -0.28
(15, 20]     0.12
(20, 25]     0.05
(25, 30]     0.11
(30, 50]     0.26
partial correlation, temperature removed: -0.01
```

Within the temperature bands the correlations are small and scatter around zero in both directions (−0.28 to +0.26; the extreme bands hold few days, so their values are noisy), and the **partial correlation** (the correlation of what is left after removing the effect of temperature from both variables, using all days) is −0.01. This is the logic of **controlling for a confounder**: compare like with like.

### 8.3 A business example: does the loyalty app raise spending?

QuickBite wants to know whether customers who use its loyalty app spend more *because of* the app. We simulate a world where we know the true answer. Each customer has an **engagement** level (how much they like and use food delivery) and an **income** level. Both raise spending, and both make a customer more likely to install the app. The app itself has a true causal effect of exactly **+150 rupees** a month.

```python run
def make_app_world(n=20_000, tau=150, seed=60):
    rng = np.random.default_rng(seed)
    engagement = rng.normal(0, 1, n)
    income = rng.normal(0, 1, n)
    p_app = 1 / (1 + np.exp(-(-0.3 + 1.2 * engagement + 0.6 * income)))      # keen, well-off customers install the app
    app = rng.random(n) < p_app
    spend = 2500 + 400 * engagement + 300 * income + tau * app + rng.normal(0, 500, n)
    return pd.DataFrame({"engagement": engagement, "income": income, "app": app, "spend": spend})


world = make_app_world()
TAU = 150
g = world.groupby("app")["spend"].agg(["size", "mean"])
print(g.round(0).to_string())
naive = g.loc[True, "mean"] - g.loc[False, "mean"]
print(f"\nnaive difference (app users - others): {naive:,.0f}   | TRUE causal effect: {TAU}")
```
```text
        size     mean
app                  
False  11192 2,280.00
True    8808 2,928.00

naive difference (app users - others): 648   | TRUE causal effect: 150
```

The naive comparison says the app users spend more than **four times** what the app actually adds. It mixes two things: the effect of the app (150) and the fact that app users are *different people*: more engaged and richer. App users would have spent more even without the app. This is **confounding**, and the naive difference answers a different question ("how do app users and non-users compare?") from the one asked ("what does the app do?").

```python run
print("average engagement  | app users:", round(world.loc[world["app"], "engagement"].mean(), 2),
      "| others:", round(world.loc[~world["app"], "engagement"].mean(), 2))
print("average income level| app users:", round(world.loc[world["app"], "income"].mean(), 2),
      "| others:", round(world.loc[~world["app"], "income"].mean(), 2))
```
```text
average engagement  | app users: 0.49 | others: -0.4
average income level| app users: 0.23 | others: -0.21
```

The groups differ on both confounders. How can we compare like with like? Two ways.

**Stratify** on the confounder: compare app users and non-users *within* groups of similar engagement, then average the differences.

```python run
world["eng_band"] = pd.qcut(world["engagement"], 10, labels=False)
within = world.groupby(["eng_band", "app"])["spend"].mean().unstack()
gap = within[True] - within[False]
print("difference within each engagement decile:", gap.round(0).astype(int).tolist())
print(f"average of the within-decile differences : {gap.mean():,.0f}   (naive {naive:,.0f}, truth {TAU})")
```
```text
difference within each engagement decile: [372, 314, 351, 316, 342, 330, 306, 358, 325, 328]
average of the within-decile differences : 334   (naive 648, truth 150)
```

The estimate falls from about 650 to about 330. Much closer, still above 150, because the *hidden* confounder (income) is still unbalanced. **Regression adjustment** does the same thing in a more flexible way: fit a model of spending on the app indicator *and* the confounders, and read the app coefficient as "the difference between app users and non-users who have the same engagement and income".

```python run
import statsmodels.formula.api as smf
world["app_i"] = world["app"].astype(int)
rows = []
for label, formula in [("no adjustment", "spend ~ app_i"),
                       ("adjust for engagement only", "spend ~ app_i + engagement"),
                       ("adjust for engagement and income", "spend ~ app_i + engagement + income")]:
    m = smf.ols(formula, data=world).fit()
    lo_, hi_ = m.conf_int().loc["app_i"]
    rows.append({"model": label, "app effect": m.params["app_i"], "CI low": lo_, "CI high": hi_})
res = pd.DataFrame(rows).set_index("model")
res.loc["TRUTH"] = [TAU, np.nan, np.nan]
print(res.round(0).to_string())
```
```text
                                  app effect  CI low  CI high
model                                                        
no adjustment                         648.00  629.00   666.00
adjust for engagement only            324.00  306.00   342.00
adjust for engagement and income      163.00  147.00   179.00
TRUTH                                 150.00     NaN      NaN
```

The estimates move toward the truth as more confounders are controlled: 648 with none, 324 with engagement, and 163 when both are included. The last interval contains the truth. The table teaches the central point of observational causal analysis: **the estimate is only as good as the list of confounders you control for.** And the list is a matter of knowledge, not of statistics. Which brings the uncomfortable question.

> **What if a confounder is not in the data?** Drop `income` from the data (as if nobody had asked) and the best you can do is the second row: 324, more than twice the truth, and *the output gives no warning*. The interval, built from the sampling variation, would look perfectly tight. Unmeasured confounding is the main reason why observational estimates of effects cannot be fully trusted, however large the data.

### 8.4 The experiment

The cure is **randomisation**. Suppose QuickBite instead picks 4,000 customers by coin flip and gives them an in-app prompt that makes them install the app. Because the coin does not know anything about engagement or income, the two groups are alike in everything, measured or not, on average. Any difference in spending afterwards is due to the app.

```python run
rng = np.random.default_rng(61)
n_exp = 4000
exp = make_app_world(n_exp, seed=62).drop(columns="app")                    # the same kind of customers...
exp["app_i"] = (rng.random(n_exp) < .5).astype(int)                         # ...but the app is assigned by a coin flip
exp["spend"] = 2500 + 400 * exp["engagement"] + 300 * exp["income"] + TAU * exp["app_i"] + rng.normal(0, 500, n_exp)
g1, g0 = exp.loc[exp["app_i"] == 1, "spend"], exp.loc[exp["app_i"] == 0, "spend"]
r = stats.ttest_ind(g1, g0, equal_var=False)
ci = r.confidence_interval(0.95)
print("engagement in the two arms:", round(exp.loc[exp["app_i"] == 1, "engagement"].mean(), 3), "vs", round(exp.loc[exp["app_i"] == 0, "engagement"].mean(), 3))
print(f"difference in mean spend : {g1.mean() - g0.mean():7,.0f}   95% CI {ci.low:,.0f} to {ci.high:,.0f}   (truth {TAU})")
```
```text
engagement in the two arms: -0.023 vs 0.011
difference in mean spend :     154   95% CI 111 to 198   (truth 150)
```

The two arms have almost equal engagement (and income), and a plain difference of means, with no adjustment at all, lands near 150 with an honest interval. That is the power of the **randomised experiment** (A/B test): it removes confounding, including from variables nobody measured. It costs time and sometimes is unethical or impossible (you cannot randomly assign smoking or a city). When it is impossible, the observational approaches of 8.3 are the fallback, used with humility.

| Method | Estimate | Verdict |
|---|---|---|
| Naive comparison of app users and non-users | about 650 | confounded by who chooses the app |
| Stratify / adjust for engagement | about 330 | better, still biased by income |
| Adjust for engagement and income | about 165 | good, because we knew every confounder |
| Randomised experiment | about 155 | unbiased by design |

### 8.5 Reverse causation, and other traps

**Reverse causation.** Customers who contact support churn more. Does support cause churn? Perhaps the customers who had a problem contacted support, and the problem (not the contact) made them leave. The arrow runs from the problem to both.

**Selection into the data.** Compare the salaries of people with and without a master's degree, among those who got a job at your company: if the company hires non-degree candidates only when they are exceptional, the comparison is distorted by the hiring rule. Conditioning on a variable that is influenced by both of the things you are studying creates a false relation (a **collider**).

**Aggregation.** A relation across groups (cities, schools) can differ from the relation inside them (the *ecological fallacy*), and Simpson's paradox (da.06) can reverse a trend when a confounder is lumped in.

### 8.6 A checklist before you say "causes"

1. **Order in time.** Did the supposed cause happen before the effect?
2. **A mechanism.** Is there a plausible story of how A changes B?
3. **A comparison group.** Is the comparison fair, or do the groups differ in other ways (who chose A)?
4. **Confounders.** Which variables could drive both? Were they measured and controlled? Which are missing?
5. **Dose and response.** Does more A go with more B?
6. **Replication.** Does it hold in other periods, places, samples?
7. **An experiment.** Can you randomise, even a small pilot?
8. **Language.** If you cannot randomise, write "is associated with" or "is consistent with an effect of", and give the size with its interval.

> **Try it.** In the app world, is the *engagement* itself related to the app? Compute the correlation between `engagement` and `app_i`, and then the correlation between `engagement` and `spend` among app users only. Which of the two arrows in "engagement → app" and "engagement → spend" does each number describe, and why do you need both for a confounder?

<details><summary>Answer</summary>

```python run
print("corr(engagement, app) :", round(float(world["engagement"].corr(world["app_i"])), 2))
print("corr(engagement, spend) among app users:", round(float(world.loc[world["app"], ["engagement", "spend"]].corr().iloc[0, 1]), 2))
print("corr(engagement, spend) among non-users:", round(float(world.loc[~world["app"], ["engagement", "spend"]].corr().iloc[0, 1]), 2))
```
```text
corr(engagement, app) : 0.44
corr(engagement, spend) among app users: 0.48
corr(engagement, spend) among non-users: 0.5
```

The first number (0.44) is the arrow into the treatment: more engaged customers are more likely to use the app. The second and third (about 0.5) are the arrows into the outcome: engagement raises spending, with or without the app. A variable is a confounder only if **both** arrows exist. A variable that affects only the outcome (like an unrelated random factor) does not bias the comparison, and a variable that affects only who gets the app (randomly assigned in an experiment) does not either.

</details>

## 9. Reporting uncertainty

### 9.1 What every estimate needs next to it

A number without its context is a rumour. For every estimate you report, attach:

1. **The estimand**: what, for whom, when.
2. **The estimate** and its **unit**.
3. **The uncertainty**: a confidence interval (and its level), not only a p-value.
4. **The sample size** (and for a rate, the counts).
5. **The method**: how the sample was drawn, how the interval was built.
6. **The caveats that could bias it**: missing data, who is in the sample, confounders not controlled.

A small helper that refuses to print an estimate without its interval and `n` turns the habit into code.

```python run
def sig_round(value, ref):
    """Round `value` to the precision of `ref` (the standard error): no digits beyond what the data support."""
    if ref == 0 or not np.isfinite(ref):
        return f"{value:,.0f}"
    decimals = max(0, 1 - int(np.floor(np.log10(abs(ref)))))
    return f"{round(value, decimals):,.{decimals}f}"


def report_mean(x, label, unit="", level=0.95):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    lo_, hi_ = ci_mean(x, level)
    se_ = x.std(ddof=1) / np.sqrt(len(x))
    return (f"{label}: {sig_round(x.mean(), se_)}{unit} ({int(level * 100)}% CI {sig_round(lo_, se_)} to {sig_round(hi_, se_)}; n = {len(x):,})")


print(report_mean(sample["monthly_spend"], "Mean monthly spend", " rupees"))
print(report_mean(pop["monthly_spend"].sample(50_000, random_state=1), "Mean monthly spend (n = 50,000)", " rupees"))
print(f"unrounded: {sample['monthly_spend'].mean():.6f}")
```
```text
Mean monthly spend: 2,578 rupees (95% CI 2,453 to 2,702; n = 500)
Mean monthly spend (n = 50,000): 2,498.1 rupees (95% CI 2,486.3 to 2,509.9; n = 50,000)
unrounded: 2577.616000
```

Look at the rounding. The first mean is printed as 2,578, not 2577.6 (the standard error is 63 rupees, so a decimal would mean nothing); with 50,000 rows the standard error is only about 6, so one decimal is justified. Printing `2577.612` would imply a precision of a thousandth of a rupee that the data do not have. This is **false precision**. A good rule: show about two significant digits of the uncertainty, no more.

### 9.2 Comparing groups in a table

When you compare groups, show every group's estimate and interval, the difference and its interval, and the counts.

```python run
rows = []
for city, seed_ in [("Metro", 1), ("Large", 2), ("Small", 3)]:
    v = pop[pop["city"] == city]["monthly_spend"].sample(400, random_state=seed_).to_numpy()
    lo_, hi_ = ci_mean(v)
    rows.append({"city": city, "n": len(v), "mean": v.mean(), "CI low": lo_, "CI high": hi_, "_v": v})
tab = pd.DataFrame(rows)
base_v = tab.loc[tab["city"] == "Small", "_v"].iloc[0]
tab["diff vs Small"] = [v.mean() - base_v.mean() for v in tab["_v"]]
tab["diff CI low"] = [stats.ttest_ind(v, base_v, equal_var=False).confidence_interval().low if len(v) else np.nan for v in tab["_v"]]
tab["diff CI high"] = [stats.ttest_ind(v, base_v, equal_var=False).confidence_interval().high for v in tab["_v"]]
tab.loc[tab["city"] == "Small", ["diff vs Small", "diff CI low", "diff CI high"]] = np.nan      # the baseline row
print(tab.drop(columns="_v").round(0).to_string(index=False))
```
```text
 city   n     mean   CI low  CI high  diff vs Small  diff CI low  diff CI high
Metro 400 3,152.00 3,012.00 3,291.00       1,481.00     1,323.00      1,640.00
Large 400 2,391.00 2,280.00 2,502.00         721.00       586.00        856.00
Small 400 1,670.00 1,594.00 1,747.00            NaN          NaN           NaN
```

The table lets a reader see both the levels and the gaps, and how sure each is. If you draw error bars on a chart (da.09), say what they are: a standard error, a 95 percent interval, or a standard deviation, which are three very different widths.

### 9.3 Words that fit the evidence

The wording should climb a ladder with the strength of the evidence.

| The evidence | Fitting wording |
|---|---|
| Randomised experiment, large, interval clear | "The change **increased** conversion by 1.5 points (CI 0.9 to 2.1)." |
| Observational, careful adjustment | "The app is **associated with** about 160 more rupees of spend, after adjusting for engagement and income; unmeasured differences could remain." |
| Observational, unadjusted | "App users spend more, but they differ from other customers in ways that probably explain much of the gap." |
| Small or noisy sample | "The data are **compatible with** anything from a small decrease to a large increase." |
| A search of many comparisons | "This pattern was found by exploring the data and needs confirmation on new data." |

And three habits for communicating with non-specialists: (1) give **ranges in words** ("somewhere between 3 and 6 more orders per hundred customers"), (2) use **natural frequencies** ("about 25 of every 100 customers reorder") instead of probabilities, (3) always state **what would change your mind**.

```python run
est, lo_, hi_ = 0.0150, 0.0014, 0.0286
print(f"Of every 1,000 visitors, {est * 1000:.0f} more convert on page B than on page A (plausibly {lo_ * 1000:.0f} to {hi_ * 1000:.0f} more).")
print("This is a randomised test with 4,000 visitors per page; it cannot rule out a gain as small as 1 or 2 extra sales per 1,000.")
```
```text
Of every 1,000 visitors, 15 more convert on page B than on page A (plausibly 1 to 29 more).
This is a randomised test with 4,000 visitors per page; it cannot rule out a gain as small as 1 or 2 extra sales per 1,000.
```


## 10. Project: critique and redo a flawed analysis

**The brief.** An analyst at QuickBite sent management a one-page report that claims the loyalty app lifts spending by a third and recommends a nationwide push. You are asked to (1) **critique** the report: list every statistical flaw and test each one with the data; (2) **redo** the analysis honestly; (3) write the **corrected report**. Because the data are synthetic, you will finally see which of the two analyses was closer to the truth, which real projects never get to see.

### 10.1 The data

The survey data, and, because we simulate the world, the whole customer base with the truth. In real life you would only have the survey and a customer table with a few columns.

```python run
CUISINES = ["north_indian", "south_indian", "chinese", "pizza", "burgers", "biryani", "desserts", "healthy", "street_food", "beverages", "breakfast", "other"]


def make_study(N=50_000, tau=120, seed=70, cuisine_seed=104):
    rng = np.random.default_rng(seed)
    city = rng.choice(["Metro", "Large", "Small"], N, p=[.35, .40, .25])
    age = np.clip(rng.normal(35, 10, N), 18, 70).round()
    eng = rng.normal(0, 1, N)                       # engagement: how much the customer orders (we measure this)
    inc = rng.normal(0, 1, N)                       # income level (we do NOT have this in the data)
    base = pd.Series(city).map({"Metro": 2700, "Large": 2200, "Small": 1700}).to_numpy()
    p_app = 1 / (1 + np.exp(-(-0.6 + 0.9 * eng + 0.5 * inc - 0.02 * (age - 35) + 0.3 * (city == "Metro"))))
    app = rng.random(N) < p_app                     # keen, richer, younger Metro customers install the app
    spend = base + 350 * eng + 250 * inc + tau * app + rng.normal(0, 450, N)        # the TRUE effect of the app is +120
    d = pd.DataFrame({"customer_id": np.arange(N), "city": city, "age": age, "engagement": eng.round(2),
                      "income_hidden": inc, "app": app, "spend": spend.round(0)})
    p_resp = 1 / (1 + np.exp(-(-5.3 + 0.8 * app + 0.5 * eng + 0.3 * (city == "Metro"))))   # who answers the pop-up
    d["responded"] = rng.random(N) < p_resp
    # the share of each customer's spend that goes to 12 cuisines: random noise, unrelated to everything else
    shares = np.random.default_rng(cuisine_seed).dirichlet(np.ones(12), N) * 100
    for k, name in enumerate(CUISINES):
        d["share_" + name] = shares[:, k].round(1)
    return d


base_world = make_study()
TAU2 = 120
survey = base_world[base_world["responded"]].drop(columns="income_hidden").reset_index(drop=True)
customer_db = base_world.drop(columns=["income_hidden", "spend", "responded"])          # what the company knows about everybody
print("survey respondents:", len(survey), "of", len(base_world), f"({len(survey) / len(base_world) * 100:.1f}%)")
print("survey columns    :", list(survey.columns))
print("customer table    :", list(customer_db.columns), "(no spend, no income)")
print(survey.head(3).to_string(index=False))
```
```text
survey respondents: 509 of 50000 (1.0%)
survey columns    : ['customer_id', 'city', 'age', 'engagement', 'app', 'spend', 'responded', 'share_north_indian', 'share_south_indian', 'share_chinese', 'share_pizza', 'share_burgers', 'share_biryani', 'share_desserts', 'share_healthy', 'share_street_food', 'share_beverages', 'share_breakfast', 'share_other']
customer table    : ['customer_id', 'city', 'age', 'engagement', 'app', 'share_north_indian', 'share_south_indian', 'share_chinese', 'share_pizza', 'share_burgers', 'share_biryani', 'share_desserts', 'share_healthy', 'share_street_food', 'share_beverages', 'share_breakfast', 'share_other'] (no spend, no income)
 customer_id  city   age  engagement   app    spend  responded  share_north_indian  share_south_indian  share_chinese  share_pizza  share_burgers  share_biryani  share_desserts  share_healthy  share_street_food  share_beverages  share_breakfast  share_other
          93 Small 26.00        0.15 False 1,898.00       True               23.20               27.70          14.00         0.40           6.70           0.40            6.40           6.20               2.20             2.60             7.70         2.40
         147 Large 41.00        0.08 False 2,615.00       True               17.00                5.70           2.40         0.80          12.30           2.80           20.30           1.20              22.00             5.00             4.20         6.40
         180 Large 26.00        0.63 False 1,747.00       True               12.40                5.30          25.80        13.70           0.50           6.50            2.80          18.30               2.20             9.70             0.40         2.40
```

The grain: one row per customer in both tables. The survey records `spend`, `app` (whether they use the app), the measured `engagement`, and the share of spend on 12 cuisines; the customer table lists city, age, engagement and app use for everybody, but not spend. `income_hidden` exists only in our simulation, to play the role of **the confounder nobody measured**.

### 10.2 The flawed report

The analyst's computations are reproduced in code (so that the report quotes real numbers), and then the report is printed as it was sent.

```python run
sv = survey.copy()
u1, u0 = sv.loc[sv["app"], "spend"], sv.loc[~sv["app"], "spend"]
naive_diff = u1.mean() - u0.mean()
p_naive = stats.ttest_ind(u1, u0, equal_var=False).pvalue
cuisine_hunt = []
for c in [col for col in sv.columns if col.startswith("share_")]:
    cuisine_hunt.append((c.replace("share_", ""), sv.loc[sv["app"], c].mean() - sv.loc[~sv["app"], c].mean(),
                         stats.ttest_ind(sv.loc[sv["app"], c], sv.loc[~sv["app"], c], equal_var=False).pvalue))
best = min(cuisine_hunt, key=lambda t: t[2])
r_eng = sv["engagement"].corr(sv["spend"])
FLAWED_REPORT = f"""
QUICKBITE LOYALTY APP: IMPACT ON SPENDING
We surveyed our customers through an in-app pop-up and received responses from the customers who chose to answer.
App users spend {u1.mean():,.0f} rupees per month on average against {u0.mean():,.0f} for non-users, a difference of {naive_diff:,.0f} rupees (+{naive_diff / u0.mean() * 100:.0f}%),
which is highly significant (p < 0.001). The app clearly boosts spending.
We also compared the share of spend on 12 cuisines and found that app users spend {best[1]:+.1f} points more of their budget on {best[0]} (p = {best[2]:.2f}),
so the app is especially powerful for the {best[0]} category.
Customers with a higher engagement score also spend more (r = {r_eng:.2f}), proving that engagement drives loyalty.
RECOMMENDATION: push the app to all 120,000 inactive customers; at +{naive_diff:,.0f} rupees each this adds about {naive_diff * 120_000 / 1e6:.0f} million rupees a month.
""".strip()
print(FLAWED_REPORT)
```
```text
QUICKBITE LOYALTY APP: IMPACT ON SPENDING
We surveyed our customers through an in-app pop-up and received responses from the customers who chose to answer.
App users spend 2,736 rupees per month on average against 2,342 for non-users, a difference of 394 rupees (+17%),
which is highly significant (p < 0.001). The app clearly boosts spending.
We also compared the share of spend on 12 cuisines and found that app users spend +1.7 points more of their budget on desserts (p = 0.01),
so the app is especially powerful for the desserts category.
Customers with a higher engagement score also spend more (r = 0.44), proving that engagement drives loyalty.
RECOMMENDATION: push the app to all 120,000 inactive customers; at +394 rupees each this adds about 47 million rupees a month.
```

Read it twice, as a skeptic. Try to list the flaws before you read on. There are at least six.

### 10.3 The critique, flaw by flaw

**Flaw 1: the sample is self-selected.** Who answers an in-app pop-up? We can check against the customer table, which describes everybody.

```python run
mix = pd.DataFrame({"all customers": customer_db["city"].value_counts(normalize=True),
                    "survey respondents": survey["city"].value_counts(normalize=True)}) * 100
print(mix.round(1).to_string())
print()
print("app users among all customers     :", round(customer_db["app"].mean() * 100, 1), "%")
print("app users among survey respondents:", round(survey["app"].mean() * 100, 1), "%")
print("mean engagement, all customers    :", round(customer_db["engagement"].mean(), 2))
print("mean engagement, respondents      :", round(survey["engagement"].mean(), 2))
true_mean_all = base_world["spend"].mean()
print(f"mean spend, whole base (truth)    : {true_mean_all:,.0f}")
print(f"mean spend, respondents           : {survey['spend'].mean():,.0f}")
```
```text
       all customers  survey respondents
city                                    
Large          40.20               35.80
Metro          35.00               44.20
Small          24.70               20.00

app users among all customers     : 40.6 %
app users among survey respondents: 70.7 %
mean engagement, all customers    : -0.0
mean engagement, respondents      : 0.64
mean spend, whole base (truth)    : 2,298
mean spend, respondents           : 2,620
```

Respondents are not typical: Metro is over-represented, app users are over-represented, and they are more engaged and spend more than the base. The report's own recommendation talks about the 120,000 customers who are *not* in the survey. A sample that over-selects people who like the app cannot say what the app does to others.

**Flaw 2: no sample size, no uncertainty.** The report gives no `n`, no interval. We compute them for the report's own comparison.

```python run
a1 = survey.loc[survey["app"], "spend"]
a0 = survey.loc[~survey["app"], "spend"]
r = stats.ttest_ind(a1, a0, equal_var=False)
ci = r.confidence_interval(0.95)
print(f"app users n = {len(a1)}, mean {a1.mean():,.0f} | non-users n = {len(a0)}, mean {a0.mean():,.0f}")
print(f"difference {a1.mean() - a0.mean():,.0f}, 95% CI {ci.low:,.0f} to {ci.high:,.0f}, p = {r.pvalue:.1e}")
print(f"relative to non-users: +{(a1.mean() / a0.mean() - 1) * 100:.0f}%")
```
```text
app users n = 360, mean 2,736 | non-users n = 149, mean 2,342
difference 394, 95% CI 260 to 528, p = 2.0e-08
relative to non-users: +17%
```

The comparison rests on a few hundred people, and the interval is wide: the plausible values for the difference are spread over more than 200 rupees. The report's single figure is one point in that range. The p-value is small, but it answers a narrow question (is the gap distinguishable from luck?), not the question the report asks (does the app raise spending?).

**Flaw 3: confounding.** App users are different people. We can see it in the variables we have.

```python run
cmp = survey.groupby("app").agg(n=("spend", "size"), spend=("spend", "mean"), engagement=("engagement", "mean"),
                                age=("age", "mean"), metro_share=("city", lambda s: (s == "Metro").mean() * 100))
print(cmp.round(2).to_string())
```
```text
         n    spend  engagement   age  metro_share
app                                               
False  149 2,341.67        0.07 35.29        48.99
True   360 2,735.82        0.87 34.20        42.22
```

App users are far more engaged (0.87 against 0.07 on the score) and a little younger; their city mix is similar. Engagement raises spending by itself, so the naive gap mixes the effect of the app with the effect of who uses it. (Income, which also drives app use and spending, is not in the data at all.)

**Flaw 4: the hunt among many comparisons.** The report highlights one cuisine out of twelve. How surprising is it to find one with p below 0.05 among twelve comparisons?

```python run
hunt = pd.DataFrame(cuisine_hunt, columns=["cuisine", "diff (points of spend share)", "p"]).sort_values("p")
print(hunt.round(3).head(5).to_string(index=False))
print("comparisons made:", len(hunt), "| expected false positives at p < 0.05:", round(len(hunt) * .05, 1),
      "| chance of at least one:", round((1 - .95 ** len(hunt)) * 100), "%",
      "| Bonferroni threshold:", round(0.05 / len(hunt), 4), "| smallest p:", round(hunt["p"].min(), 4))
```
```text
     cuisine  diff (points of spend share)    p
    desserts                          1.69 0.01
south_indian                         -1.33 0.10
north_indian                         -0.99 0.20
 street_food                          0.78 0.33
   breakfast                         -0.38 0.64
comparisons made: 12 | expected false positives at p < 0.05: 0.6 | chance of at least one: 46 % | Bonferroni threshold: 0.0042 | smallest p: 0.0143
```

We built these shares from pure noise, with no link to the app, so every difference is luck. With twelve comparisons the chance of at least one p below 0.05 is 46 percent, and the smallest p-value does not beat the corrected threshold of 0.05 / 12 = 0.004. The "finding" is a candidate for a *new* test, not a result.

**Flaw 5: a correlation called proof.** "Customers with a higher engagement score spend more (r as printed), proving that engagement drives loyalty." A correlation says nothing about direction: loyal customers may be engaged *because* they spend, and both may come from enjoying the food (a confounder). The strength of `r` is not evidence of cause (section 8).

**Flaw 6: extrapolating to a different population.** The figure in the report (even if correct) were measured among customers who *chose* the app. The plan is to push it to the **inactive** customers, who are probably less engaged and may respond differently, and a promotion is not the same as spontaneous use. The effect for people who adopt on their own is not the effect for people who are pushed. And "the same gain for each of 120,000 customers" multiplies a number of unknown uncertainty by a population that was not studied.

A summary of what the critique found:

| # | Flaw | Evidence in the data |
|---|---|---|
| 1 | Self-selected sample | Metro and app users over-represented; respondents spend more than the base |
| 2 | No `n`, no interval | the interval is hundreds of rupees wide |
| 3 | Confounding | app users are more engaged, younger, more often Metro |
| 4 | Hunting among comparisons | 12 cuisines compared, the best p does not survive correction |
| 5 | Correlation as proof | direction and confounders ignored |
| 6 | Extrapolation | effect on volunteers applied to a different group |

### 10.4 The redo

We repair what can be repaired, in steps, and compare each estimate with the truth (+120 rupees) at the end.

**Step 1: adjust for the measured confounders.** Regress spend on app use and the confounders we measured (engagement, age, city), with robust standard errors that do not assume equal variance.

```python run
fit_naive = smf.ols("spend ~ app_i", data=survey.assign(app_i=survey["app"].astype(int))).fit(cov_type="HC3")
fit_adj = smf.ols("spend ~ app_i + engagement + age + C(city)", data=survey.assign(app_i=survey["app"].astype(int))).fit(cov_type="HC3")
for name, f in [("naive", fit_naive), ("adjusted for engagement, age, city", fit_adj)]:
    lo_, hi_ = f.conf_int().loc["app_i"]
    print(f"{name:38} app effect {f.params['app_i']:6,.0f}   95% CI {lo_:6,.0f} to {hi_:6,.0f}")
```
```text
naive                                  app effect    394   95% CI    260 to    528
adjusted for engagement, age, city     app effect    231   95% CI    130 to    332
```

The adjustment removes a large part of the gap. But note two things. The interval is still wide (the survey is small). And there is one confounder we do not have: income.

**Step 2: weight for who answers.** The survey over-represents Metro and app users. Use the customer table (which covers everybody) to build post-stratification weights by city and app use, so that respondents stand in for the whole base.

```python run
cells = customer_db.assign(cell=customer_db["city"] + "|" + customer_db["app"].astype(str))["cell"].value_counts(normalize=True)
resp_cells = survey.assign(cell=survey["city"] + "|" + survey["app"].astype(str))["cell"].value_counts(normalize=True)
w_cell = (cells / resp_cells)
survey["w"] = (survey["city"] + "|" + survey["app"].astype(str)).map(w_cell)
print(pd.DataFrame({"share in base": cells, "share in survey": resp_cells, "weight": w_cell}).round(3).to_string())
fit_w = smf.wls("spend ~ app_i + engagement + age + C(city)", data=survey.assign(app_i=survey["app"].astype(int)), weights=survey["w"]).fit(cov_type="HC3")
lo_, hi_ = fit_w.conf_int().loc["app_i"]
print(f"\nweighted and adjusted: app effect {fit_w.params['app_i']:,.0f}   95% CI {lo_:,.0f} to {hi_:,.0f}")
print(f"weighted mean spend of respondents: {np.average(survey['spend'], weights=survey['w']):,.0f}   (truth for the whole base {true_mean_all:,.0f})")
```
```text
             share in base  share in survey  weight
cell                                               
Large|False           0.24             0.10    2.55
Large|True            0.16             0.26    0.60
Metro|False           0.20             0.14    1.37
Metro|True            0.15             0.30    0.52
Small|False           0.15             0.05    2.89
Small|True            0.09             0.15    0.64

weighted and adjusted: app effect 270   95% CI 160 to 380
weighted mean spend of respondents: 2,399   (truth for the whole base 2,298)
```

The weights make the respondents match the base on city and app use; they cannot make them match on *spending propensity within a cell* (that was the lesson of 3.4). Still, this is the more honest estimate of what the base looks like. The weighted mean spend moves toward the base value.

**Step 3: what does the unmeasured confounder do?** In this simulation we can include the hidden income, and so see how much it matters. In real life you cannot, but you can reason about it: *if there were a variable as strongly related to app use and to spending as engagement is, how far would the estimate move?*

```python run
full = base_world.assign(app_i=base_world["app"].astype(int))
full_resp = full[full["responded"]]
f_meas = smf.ols("spend ~ app_i + engagement + age + C(city)", data=full_resp).fit(cov_type="HC3")
f_all = smf.ols("spend ~ app_i + engagement + age + C(city) + income_hidden", data=full_resp).fit(cov_type="HC3")
print(f"adjusting for what we measured       : {f_meas.params['app_i']:6,.0f}")
print(f"adding the hidden income (impossible): {f_all.params['app_i']:6,.0f}   | truth {TAU2}")
drop = fit_naive.params["app_i"] - fit_adj.params["app_i"]
print(f"measured confounders already removed : {drop:6,.0f} rupees of the naive gap")
```
```text
adjusting for what we measured       :    231
adding the hidden income (impossible):    101   | truth 120
measured confounders already removed :    163 rupees of the naive gap
```

Adding the hidden income moves the estimate from 231 to 101, close to the truth of 120 (the remaining gap is sampling noise in 509 respondents), and the output of the "measured only" model gave no hint that this was missing. The honest statement is a **range**: with only the measured variables, the effect is at most about 230 and could be much lower, down to near zero. This is a sensitivity argument (da.05 used the same logic for missing data): you cannot get rid of the uncertainty, but you can say how far it plausibly reaches.

**Step 4: run the experiment.** The way out of confounding is randomisation. QuickBite runs a pilot: 3,000 customers are picked at random, and a coin flip decides who gets a prompt that installs the app. We simulate it in the same world (everyone assigned installs; the compliance is perfect for simplicity).

```python run
rng = np.random.default_rng(81)
pilot_ids = rng.choice(len(base_world), 4000, replace=False)
pilot = base_world.iloc[pilot_ids].copy()
treat = rng.random(4000) < .5
# the pilot customers' spend is re-drawn with the app switched on or off by the coin: spend = spend_without_app + tau * treated
spend_without = pilot["spend"].to_numpy() - TAU2 * pilot["app"].to_numpy()
pilot["spend_pilot"] = spend_without + TAU2 * treat
pilot["treated"] = treat
g1, g0 = pilot.loc[pilot["treated"], "spend_pilot"], pilot.loc[~pilot["treated"], "spend_pilot"]
rp = stats.ttest_ind(g1, g0, equal_var=False)
cip = rp.confidence_interval(0.95)
print("balance (should be alike): engagement", round(pilot.loc[pilot["treated"], "engagement"].mean(), 3), "vs", round(pilot.loc[~pilot["treated"], "engagement"].mean(), 3),
      "| income", round(pilot.loc[pilot["treated"], "income_hidden"].mean(), 3), "vs", round(pilot.loc[~pilot["treated"], "income_hidden"].mean(), 3))
print(f"pilot: n = {len(pilot)} ({int(treat.sum())} treated), difference {g1.mean() - g0.mean():,.0f}, 95% CI {cip.low:,.0f} to {cip.high:,.0f}")
```
```text
balance (should be alike): engagement -0.01 vs -0.005 | income -0.01 vs -0.015
pilot: n = 4000 (2052 treated), difference 134, 95% CI 88 to 179
```

The two arms are balanced on engagement and on the hidden income (which nobody measured), because the coin ignores everything. The difference of means is the effect of the app, with an honest interval.

### 10.5 The scorecard

All the estimates, against the truth.

```python run
score = pd.DataFrame([
    ("Report: naive, self-selected survey", fit_naive.params["app_i"], *fit_naive.conf_int().loc["app_i"]),
    ("Adjusted for measured confounders", fit_adj.params["app_i"], *fit_adj.conf_int().loc["app_i"]),
    ("Weighted and adjusted", fit_w.params["app_i"], *fit_w.conf_int().loc["app_i"]),
    (f"Randomised pilot (n = {len(pilot):,})", g1.mean() - g0.mean(), cip.low, cip.high),
], columns=["method", "estimate", "CI low", "CI high"]).set_index("method")
score["contains the truth (120)?"] = (score["CI low"] <= TAU2) & (score["CI high"] >= TAU2)
score["error vs truth"] = score["estimate"] - TAU2
print(score.round(0).to_string())
```
```text
                                     estimate  CI low  CI high  contains the truth (120)?  error vs truth
method                                                                                                   
Report: naive, self-selected survey    394.00  260.00   528.00                      False          274.00
Adjusted for measured confounders      231.00  130.00   332.00                      False          111.00
Weighted and adjusted                  270.00  160.00   380.00                      False          150.00
Randomised pilot (n = 4,000)           134.00   88.00   179.00                       True           14.00
```

The story in numbers: the report's estimate is **more than three times too large** and its interval does not contain the truth. Adjusting for measured confounders helps a lot (394 to 231), but the interval still sits above 120, because the hidden income is not accounted for. Weighting for who answered does not repair that (270). The randomised pilot is close to the truth and its interval contains it. Notice that the pilot answers the *causal* question directly and needs no model; the price is time and the need to run an experiment.

A single pilot can still be a little lucky or unlucky. How much? Run the same pilot 300 times:

```python run
rng = np.random.default_rng(90)
est, covered = [], []
for _ in range(300):
    ids = rng.choice(len(base_world), 4000, replace=False)
    pl = base_world.iloc[ids]
    t_ = rng.random(4000) < .5
    y = pl["spend"].to_numpy() - TAU2 * pl["app"].to_numpy() + TAU2 * t_
    r_ = stats.ttest_ind(y[t_], y[~t_], equal_var=False)
    c_ = r_.confidence_interval(0.95)
    est.append(y[t_].mean() - y[~t_].mean())
    covered.append(c_.low <= TAU2 <= c_.high)
est = np.array(est)
print(f"300 repeated pilots: estimates average {est.mean():,.0f} (truth {TAU2}), spread (SD) {est.std():,.0f}")
print(f"central 95% of the estimates: {np.quantile(est, .025):,.0f} to {np.quantile(est, .975):,.0f}")
print(f"intervals that contain the truth: {np.mean(covered) * 100:.0f}%")
```
```text
300 repeated pilots: estimates average 119 (truth 120), spread (SD) 23
central 95% of the estimates: 78 to 167
intervals that contain the truth: 95%
```

The pilot is unbiased (the repeated estimates centre on 120), its confidence interval covers the truth about 95 percent of the time, and a single pilot can be about 45 rupees off by luck. That is what the interval is for. The observational estimates have no such guarantee: their error is mostly bias, which no repetition can average away.

### 10.6 Decision against the minimum effect

The rollout costs money. Suppose the app must raise spending by at least **80 rupees per customer per month** to repay the promotion (the minimum effect of interest of section 6). Read the pilot's interval against it.

```python run
MEI2 = 80
print(f"pilot interval {cip.low:,.0f} to {cip.high:,.0f} against the threshold {MEI2}:",
      "the whole interval is above the threshold -> go" if cip.low > MEI2 else
      "the interval straddles the threshold -> inconclusive, or a smaller go with risk" if cip.high > MEI2 else "below the threshold -> do not roll out")
per_month_low, per_month_high = cip.low * 120_000, cip.high * 120_000
print(f"for 120,000 pushed customers: {per_month_low / 1e6:.1f} to {per_month_high / 1e6:.1f} million rupees a month (the report promised {naive_diff * 120_000 / 1e6:.0f})")
```
```text
pilot interval 88 to 179 against the threshold 80: the whole interval is above the threshold -> go
for 120,000 pushed customers: 10.6 to 21.5 million rupees a month (the report promised 47)
```

The report promised about 47 million rupees a month. The pilot supports about 11 to 22 million, and only if the effect among pushed customers equals the effect among the pilot's customers (which were a random sample of the whole base, so this is a fairer assumption than the report's). The threshold test is clear here: the whole interval lies above 80 rupees, so the rollout pays at the lower end too. The right sentence in the report is a range with its assumptions, not a point.

### 10.7 The corrected report

```python run
CORRECTED = f"""
QUICKBITE LOYALTY APP: IMPACT ON SPENDING (revised)
Question. Does installing the loyalty app raise a customer's monthly spend, and by how much?
Data. (a) An opt-in pop-up survey, {len(survey)} respondents of 50,000 customers; respondents over-represent Metro and app users. (b) A randomised pilot, {len(pilot):,} customers chosen at random, half given the app.
Findings.
 1. In the survey, app users spend {a1.mean() - a0.mean():,.0f} rupees more (95% CI {ci.low:,.0f} to {ci.high:,.0f}), but app users differ from others in engagement, age and city.
 2. After adjusting for these, the survey difference falls to {fit_adj.params['app_i']:,.0f} (CI {fit_adj.conf_int().loc['app_i'][0]:,.0f} to {fit_adj.conf_int().loc['app_i'][1]:,.0f}); income is not measured and could explain more of it.
 3. In the randomised pilot, the app raised spend by {g1.mean() - g0.mean():,.0f} rupees per month (95% CI {cip.low:,.0f} to {cip.high:,.0f}), about {(g1.mean() - g0.mean()) / g0.mean() * 100:.0f}% of mean spend.
 4. No cuisine shows a reliable difference; of 12 compared, the best p-value (about {hunt['p'].min():.2f}) does not survive correction for multiple tests.
Limits. The pilot measured a short period; long-run effects are unknown. The survey cannot show cause.
Recommendation. The effect is positive and moderate. At 120,000 customers it implies roughly {per_month_low / 1e6:.0f} to {per_month_high / 1e6:.0f} million rupees a month, if the pilot effect holds. Roll out in stages, measuring against a held-out group.
""".strip()
print(CORRECTED)
```
```text
QUICKBITE LOYALTY APP: IMPACT ON SPENDING (revised)
Question. Does installing the loyalty app raise a customer's monthly spend, and by how much?
Data. (a) An opt-in pop-up survey, 509 respondents of 50,000 customers; respondents over-represent Metro and app users. (b) A randomised pilot, 4,000 customers chosen at random, half given the app.
Findings.
 1. In the survey, app users spend 394 rupees more (95% CI 260 to 528), but app users differ from others in engagement, age and city.
 2. After adjusting for these, the survey difference falls to 231 (CI 130 to 332); income is not measured and could explain more of it.
 3. In the randomised pilot, the app raised spend by 134 rupees per month (95% CI 88 to 179), about 6% of mean spend.
 4. No cuisine shows a reliable difference; of 12 compared, the best p-value (about 0.01) does not survive correction for multiple tests.
Limits. The pilot measured a short period; long-run effects are unknown. The survey cannot show cause.
Recommendation. The effect is positive and moderate. At 120,000 customers it implies roughly 11 to 21 million rupees a month, if the pilot effect holds. Roll out in stages, measuring against a held-out group.
```

Compare the two reports. The corrected one is longer, hedged where hedging is due, and every number has a source, an interval or a count. It makes a smaller claim, and it is the one that will still be true next quarter.

### 10.8 What to hand in

For a flawed analysis of your own choosing (a blog post, a company deck, a news story with a dataset):

1. A **claim inventory**: every numeric or causal claim, and the evidence offered.
2. A **flaw list** matching the checklist: sampling, uncertainty, confounding, significance against size, multiple comparisons, correlation read as cause, extrapolation. For each, a **test** you ran on the data (not an opinion).
3. A **redo** with intervals, the best available adjustment and, if possible, an experiment or a natural comparison.
4. A **scorecard** comparing original and redone estimates (against a truth if you simulated one; against the best-available answer if not).
5. A **corrected report** in plain words, with the limits stated.

## 11. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Reporting the sample mean as "the" value | no sense of the wobble | report the estimate with a confidence interval and `n` (4.1, 9.1) |
| Treating more data as the cure for bias | a narrow interval around a wrong value | fix the sampling method, or correct with known weights (3.1, 4.7) |
| Confusing the SD with the SE | an interval for people read as an interval for the mean | SD describes individuals, SE the estimate (4.3) |
| Averaging rates or averages | wrong when sizes differ | weight by sizes (3.4) |
| Reading "95%" as "95% chance this interval holds the truth" | a misreading of the method | 95% of intervals built this way hold the truth (4.2) |
| The normal interval for small counts | negative or impossible limits | Wilson interval, show `k of n` (4.4) |
| Bootstrapping a biased or tiny sample | a tight interval around nothing | the bootstrap measures luck, not bias (4.5) |
| Reading a p-value as the probability the effect is real | a different probability altogether | it is how rare the data are if there were no effect (5.2) |
| Testing many things and reporting the winner | p-hacking | decide the tests beforehand, correct for their number (5.4) |
| "No significant difference, so no effect" | an underpowered test | look at the interval, plan the sample size (5.5) |
| "Highly significant" as "important" | a tiny effect with a huge `n` | compare the interval with the minimum effect (6) |
| Giving only relative changes | +50% of almost nothing | absolute and relative together (6.2) |
| A correlation without a look at the data | outliers, curves, restricted range | scatter or binned table first (7.2, 7.3) |
| Correlating two trending series | spurious strong correlation | compare changes, not levels (7.4) |
| Searching many pairs | impressive coincidences | confirm on new data (7.4) |
| Calling a gap between self-chosen groups "the effect" | confounding | compare like with like, adjust, or randomise (8) |
| Adjusting only for what is in the table | hidden confounders remain | argue about the unmeasured ones, give a range (8.3, 10.4) |
| Assuming the effect on volunteers holds for everybody | extrapolation | state the population the estimate is about (10.3) |
| Quoting more digits than the data support | false precision | round to the uncertainty (9.1) |

A habit for every claim you read or write: ask **"compared with what, who is missing, how sure, and could something else explain it?"** Those four questions catch most of what this chapter covers.

## 12. Summary

- **Inference** uses a sample to say something about a population. Two things can go wrong: **luck** (the estimate wobbles, measured by the standard error and shrinking as `1/sqrt(n)`) and **bias** (a consistent error caused by how the data arrived, not reduced by more data).
- The **sampling distribution** of the mean is centred on the truth for a random sample and bell-shaped (central limit theorem); the **standard error** is `s / sqrt(n)`. Four times the data halves the error. A sample's absolute size matters, not its share of the population.
- **Sampling bias** has many forms: convenience, undercoverage, self-selection, non-response, survivorship, selection on the outcome, measurement and time. Weighting by known strata repairs only the part of the bias that the strata explain. Ask what is **not** in your data and why.
- A **confidence interval** (estimate +/- critical value x SE; or bootstrap for medians and other statistics; Wilson for small counts) shows the plausible range. "95%" describes the **method**: 19 intervals in 20 hold the truth. It is not the range of individuals, not a probability for this interval, and it is conditional on a fair sample. Plan sample sizes with the margin formula.
- A **p-value** says how surprising the data are if there were no effect. It is not the probability the null is true, not the size of the effect. With no effect, 1 test in 20 is "significant"; many tests need correction. A non-significant result of a small test is **absence of evidence, not evidence of absence**; look at the interval and the power.
- **Practical significance** is a separate question from statistical significance: compare the confidence interval with the **minimum effect of interest**, and report effect sizes (absolute and relative) rather than "significant".
- **Correlation** measures straight-line association only. Look at the data (Anscombe), use Spearman for monotonic or skewed data, beware restricted range, trending series and searches over many pairs. Report its interval.
- **Causation** needs more than correlation: reverse causation, **confounders** and selection explain associations. Compare like with like (stratify, regress), know that unmeasured confounders remain, and prefer a **randomised experiment** when you can run one. Choose words that match the strength of the evidence.
- **Reporting**: every estimate comes with its estimand, unit, interval, `n`, method and caveats, rounded to what the data support, in language that climbs the ladder from "associated with" to "caused".
- The **critique-and-redo** method: inventory the claims, test each flaw against the data, redo with intervals and the best adjustment, check against an experiment if available, and write the report you would be proud to sign.

You reached both outcomes of this chapter: you can **explain why a correlation in your data does not prove an effect** (the naive app-user gap was four times the true effect, and the reasons are visible in the data), and you can **report an estimate with its uncertainty**, with an interval, a sample size and the limits of what the interval can mean. Next, da.09 turns these results into pictures: data visualisation, where the choice of chart, scale and error bar decides whether the reader sees the uncertainty or is misled.
