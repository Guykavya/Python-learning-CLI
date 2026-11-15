# Chapter 7 (DS): Time-series forecasting

Most of machine learning assumes the rows of a table are **independent draws** from the same world. A time series breaks that assumption in the most basic way: the rows come in an **order**, today depends on yesterday, and there is only **one history**, which you can never repeat. You cannot reshuffle it, you cannot run the experiment again, and the thing you want to know (the future) is exactly the thing you do not have. In ds.04 you met the consequences: random splits that interpolate instead of forecasting, features that look ahead, baselines like "same as last week" that beat flexible models. This chapter turns those warnings into a complete method.

You will learn to read a series (**trend, seasonality, noise**), to forecast it with **naive and seasonal-naive baselines** that are surprisingly hard to beat, to measure forecasts with metrics that make sense across series (**MASE, sMAPE**), and to **backtest with rolling origins** so that your estimate of future accuracy is honest. You will then build **classical models** (exponential smoothing, ARIMA with seasonality and regressors), use **gradient boosting** on lag features with a proper multi-step strategy, produce **prediction intervals**, and combine forecasts. The thread through all of it is the outcome of the syllabus: **backtest a forecast and show whether it beats seasonal naive.** The project builds a sales-forecasting harness whose report refuses to claim a win that is not in the data.

Prerequisites: ds.04 (leakage, time splits, baselines, thresholds), ds.05 (pipelines), ds.03 (metrics). The statistics used (autocorrelation, stationarity) are explained when they appear.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, pandas, SciPy, scikit-learn and **statsmodels** (which is installed). **Prophet, pmdarima, sktime and LightGBM are not installed**, so their code is shown as *Try it on your machine* with no invented output. The data are **synthetic and seeded**: a daily-sales series with a known trend, weekly and yearly seasonality, promotions and holidays, so we always know what a good forecast looks like. Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, json, warnings, platform
import numpy as np
import pandas as pd
import scipy
import sklearn
import statsmodels
from scipy import stats
from sklearn import ensemble, linear_model, metrics, model_selection, preprocessing, pipeline, dummy
from statsmodels.tsa import stattools, seasonal
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox

np.set_printoptions(precision=4, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
warnings.filterwarnings("ignore")
print("python     ", sys.version.split()[0])
print("numpy      ", np.__version__)
print("pandas     ", pd.__version__)
print("scikit-learn", sklearn.__version__)
print("statsmodels", statsmodels.__version__)
```
```text
python      3.14.4
numpy       2.5.4
pandas      3.1.1
scikit-learn 1.9.1
statsmodels 0.15.0
```

## Table of contents

1. [What is different about time series](#1-what-is-different-about-time-series)
2. [The running series and its components](#2-the-running-series-and-its-components)
3. [Autocorrelation and stationarity](#3-autocorrelation-and-stationarity)
4. [Baselines and error metrics](#4-baselines-and-error-metrics)
5. [Backtesting with rolling origins](#5-backtesting-with-rolling-origins)
6. [Avoiding future-data leakage](#6-avoiding-future-data-leakage)
7. [Exponential smoothing](#7-exponential-smoothing)
8. [ARIMA, seasonal ARIMA and regressors](#8-arima-seasonal-arima-and-regressors)
9. [Gradient boosting for forecasting](#9-gradient-boosting-for-forecasting)
10. [Prediction intervals and probabilistic forecasts](#10-prediction-intervals-and-probabilistic-forecasts)
11. [Combining forecasts, drift and retraining](#11-combining-forecasts-drift-and-retraining)
12. [Project: sales forecasting with an honest backtest](#12-project-sales-forecasting-with-an-honest-backtest)
13. [Common traps](#13-common-traps)
14. [Summary](#14-summary)

## 1. What is different about time series

### 1.1 Four differences that change everything

| In ordinary tabular ML | In a time series |
|---|---|
| Rows are independent | **Neighbouring rows are correlated** (today looks like yesterday) |
| Shuffle freely, split at random | **Order is sacred**: the test set must be later than the training set |
| Features describe the row | The most useful features are **the series' own past** (lags), which exist only if you are careful about *when* you read them |
| One prediction per row | Often a **horizon** of many future steps (tomorrow, next week, next quarter), and error grows with the horizon |

### 1.2 The forecasting task, stated precisely

We stand at an **origin** (a point in time, "now"), with history up to and including the origin. We want predictions for the next `h` steps, the **horizon**. A forecast is only honest if it uses information that existed **at the origin**. Everything in this chapter (the baselines, the backtest, the features) is a way to respect that sentence.

```text
 history ---------------------------------|  origin  |---- horizon h = 7 ----> unknown future
 t0 ................................... t-1   t                t+1 ... t+7
 usable for forecasting                        "now"           what we must predict
```

### 1.3 Point forecasts, intervals, and what a forecast is for

A **point forecast** is one number per future step. A **prediction interval** says "with 90% probability the value will fall between a and b" (section 10). Decisions use both: a point forecast for the plan, an interval for the safety stock. And a forecast is always *for a decision* (how many units to order, how many staff to roster), so its quality is judged by the cost of its errors, not by an abstract score.

## 2. The running series and its components

### 2.1 Daily sales of one product, with a known recipe

We generate four years of daily sales. The recipe is the usual decomposition:

```text
sales = level(t) x weekly(day of week) x yearly(day of year) x promotion x holiday x noise(t)
```

with a growing trend that slows down in the last year (a **structural change**), a weekend peak, a summer-winter cycle, promotions we know about in advance, and a few fixed holidays.

```python run
def make_demand(start="2021-01-01", n_days=1461, seed=0):
    r = np.random.default_rng(seed)
    idx = pd.date_range(start, periods=n_days, freq="D")
    t = np.arange(n_days)
    level = 200 + 0.09 * t - 0.06 * np.maximum(t - 1100, 0)               # growth slows after day 1100
    weekly = np.array([0.85, 0.88, 0.92, 0.97, 1.12, 1.25, 1.01])         # Monday .. Sunday
    weekly = weekly / weekly.mean()
    yearly = 1 + 0.15 * np.sin(2 * np.pi * (idx.dayofyear - 100) / 365.25)
    promo = (r.random(n_days) < 0.07).astype(int)
    holiday = np.isin(idx.strftime("%m-%d"), ["01-01", "08-15", "10-02", "12-25"]).astype(int)
    noise = np.zeros(n_days)
    for i in range(1, n_days):                                             # a little autocorrelation in the noise
        noise[i] = 0.3 * noise[i - 1] + r.normal(0, 0.06)
    mean = level * weekly[idx.dayofweek] * yearly * np.where(promo == 1, 1.25, 1.0) * np.where(holiday == 1, 0.8, 1.0)
    sales = np.round(mean * np.exp(noise), 1)
    return pd.DataFrame({"sales": sales, "promo": promo, "holiday": holiday}, index=idx)

demand = make_demand()
y = demand["sales"]
print(demand.shape, "| from", y.index[0].date(), "to", y.index[-1].date(), "| frequency:", y.index.freqstr)
print(demand.head(8).to_string())
print("\nmean sales by year:")
print(y.groupby(y.index.year).mean().round(1).to_string())
```
```text
(1461, 3) | from 2021-01-01 to 2024-12-31 | frequency: D
              sales  promo  holiday
2021-01-01 152.6000      0        1
2021-01-02 207.1000      0        0
2021-01-03 234.7000      1        0
2021-01-04 209.5000      1        0
2021-01-05 151.4000      0        0
2021-01-06 166.0000      0        0
2021-01-07 169.6000      0        0
2021-01-08 195.8000      0        0

mean sales by year:
2021   218.7000
2022   251.2000
2023   285.0000
2024   309.9000
```

The first thing to do with any series is to **plot it**. We have no screen here, so we describe it with tables, which is also a useful habit: numbers cannot be misread by eye.

```python run
print("average by day of week (Mon..Sun):")
print(y.groupby(y.index.dayofweek).mean().round(1).rename(index=dict(enumerate("Mon Tue Wed Thu Fri Sat Sun".split()))).to_string())
print("\naverage by month (all years):")
print(y.groupby(y.index.month).mean().round(1).to_string())
print("\nmean on promo days vs normal days:", round(y[demand.promo == 1].mean(), 1), "vs", round(y[demand.promo == 0].mean(), 1))
```
```text
average by day of week (Mon..Sun):
Mon   227.8000
Tue   235.5000
Wed   243.0000
Thu   257.8000
Fri   298.7000
Sat   330.3000
Sun   270.4000

average by month (all years):
1    216.6000
2    230.5000
3    241.3000
4    267.8000
5    284.4000
6    300.4000
7    305.7000
8    300.8000
9    289.4000
10   268.6000
11   249.4000
12   238.1000

mean on promo days vs normal days: 334.4 vs 261.4
```

### 2.2 The components

| Component | Meaning | Here |
|---|---|---|
| **Level / trend** | the slowly moving average | grows, then slows |
| **Seasonality** | a pattern that repeats with a **fixed period** known in advance | period 7 (week) and about 365 (year) |
| **Cycle** | rises and falls with **no fixed period** (business cycles) | none here |
| **Calendar / events** | holidays, promotions | known ahead |
| **Noise** | what is left | proportional to the level |

**Additive** structure (`y = trend + seasonal + noise`) fits when the seasonal swing has a constant size. **Multiplicative** (`y = trend x seasonal x noise`) fits when the swing grows with the level, as with our weekend peak that is 25% above average whether the level is 200 or 300. Taking the **logarithm** turns a multiplicative series into an additive one, which is why log transforms are so common.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one figure with four stacked line plots of 4 years of daily sales (2021-2024). Panel 1: a rising trend that grows from about 200 and slows in the last year. Panel 2: a repeating 7-day weekly pattern with a weekend peak (Saturday highest, about 25% above average). Panel 3: a yearly sine wave peaking in summer. Panel 4: small noise. Add a fifth panel multiplying all four together, and label every panel."


### 2.3 Decomposing

`seasonal_decompose` estimates the trend with a centred moving average, averages what is left by position in the period to get the seasonal pattern, and calls the remainder noise. **STL** (Seasonal-Trend decomposition using Loess) does the same more robustly: it lets the seasonal pattern change slowly and can ignore outliers.

```python run
dec = seasonal.seasonal_decompose(y, model="multiplicative", period=7)
print("weekly seasonal factors found (Mon..Sun):", dec.seasonal.groupby(y.index.dayofweek).first().round(3).to_numpy())
print("true factors                          :", (np.array([0.85, 0.88, 0.92, 0.97, 1.12, 1.25, 1.01]) / np.mean([0.85, 0.88, 0.92, 0.97, 1.12, 1.25, 1.01])).round(3))

stl = seasonal.STL(np.log(y), period=7, robust=True).fit()
comp = pd.DataFrame({"log sales": np.log(y), "trend": stl.trend, "seasonal": stl.seasonal, "remainder": stl.resid})
print()
print(comp.iloc[[0, 365, 730, 1095, 1460]].round(3).to_string())
print("\nshare of variance of log sales explained by: trend %.2f, weekly seasonal %.2f, remainder %.3f" % (
    np.var(stl.trend) / np.var(np.log(y)), np.var(stl.seasonal) / np.var(np.log(y)), np.var(stl.resid) / np.var(np.log(y))))
```
```text
weekly seasonal factors found (Mon..Sun): [0.856 0.883 0.912 0.969 1.123 1.242 1.014]
true factors                          : [0.85 0.88 0.92 0.97 1.12 1.25 1.01]

            log sales  trend  seasonal  remainder
2021-01-01     5.0280 5.0470   -0.0040    -0.0150
2022-01-01     5.5620 5.2550    0.2640     0.0420
2023-01-01     5.1900 5.4460   -0.0160    -0.2400
2024-01-01     5.1380 5.5190   -0.1230    -0.2590
2024-12-31     5.5790 5.4690    0.1260    -0.0170

share of variance of log sales explained by: trend 0.56, weekly seasonal 0.32, remainder 0.114
```

> **Predict the output.** The remainder of a weekly STL decomposition holds what the trend and the weekly pattern do not explain. Which of these will leave a visible trace in the remainder: the yearly cycle, the promotions, the holidays?

<details><summary>Answer</summary>

**Promotions and holidays**, but not the yearly cycle. A weekly STL has no way to represent a promotion or a holiday, so they land in the remainder. The yearly cycle is slow, and STL's flexible trend smoother simply *absorbs* it: the "trend" wiggles with the seasons. Check both:

```python run
rem = pd.Series(stl.resid, index=y.index)
print("mean remainder (log scale): promo days %.3f | holiday days %.3f | other days %.3f" % (
    rem[demand.promo == 1].mean(), rem[demand.holiday == 1].mean(), rem[(demand.promo == 0) & (demand.holiday == 0)].mean()))
print("expected from the recipe  : promo %.3f | holiday %.3f" % (np.log(1.25), np.log(0.8)))
yearly_wave = np.sin(2 * np.pi * (y.index.dayofyear - 100) / 365.25)
tr_s = pd.Series(stl.trend, index=y.index)
smooth = np.polyval(np.polyfit(np.arange(len(y)), tr_s.to_numpy(), 2), np.arange(len(y)))
print("correlation of the yearly wave with: remainder %.2f | trend after removing its smooth curve %.2f" % (np.corrcoef(stl.resid, yearly_wave)[0, 1], np.corrcoef(tr_s.to_numpy() - smooth, yearly_wave)[0, 1]))
```
```text
mean remainder (log scale): promo days 0.209 | holiday days -0.187 | other days -0.001
expected from the recipe  : promo 0.223 | holiday -0.223
correlation of the yearly wave with: remainder 0.01 | trend after removing its smooth curve 0.96
```

A decomposition is a diagnostic: structure left in the remainder tells you what a model still has to learn (here: promotions and holidays, known in advance, make good **regressors**). And a flexible trend can swallow a slow seasonal cycle, so check what the trend is doing before calling it "the trend".

</details>

### 2.4 Trend and seasonality strength

Two numbers summarise a decomposition: the **strength of trend** and the **strength of seasonality**, both between 0 and 1 (Hyndman's definitions): `1 - Var(remainder) / Var(trend + remainder)` and `1 - Var(remainder) / Var(seasonal + remainder)`.

```python run
def strength(component, remainder):
    return max(0.0, 1 - np.var(remainder) / np.var(component + remainder))
print(f"trend strength {strength(stl.trend, stl.resid):.3f} | weekly seasonal strength {strength(stl.seasonal, stl.resid):.3f}")
```
```text
trend strength 0.836 | weekly seasonal strength 0.729
```

Strong seasonality tells you a **seasonal** baseline will be hard to beat; strong trend tells you a pure seasonal baseline needs a trend correction (section 4).

### 2.5 Try it

1. Run `seasonal_decompose(y, model="additive", period=7)` and look at the seasonal pattern. Why are its numbers in units of sales and not factors around 1?
2. Decompose with `period=365` (STL with a long period needs `seasonal` set to an odd number). What does the yearly pattern look like by month?

## 3. Autocorrelation and stationarity

### 3.1 Autocorrelation: how much does the past say about the present

The **autocorrelation at lag k** is the correlation between the series and itself shifted by `k` steps. A series with strong autocorrelation can be forecast from its past. A plot of autocorrelation against lag is the **ACF**. The **partial autocorrelation (PACF)** at lag `k` removes the effect of the shorter lags, isolating what lag `k` adds.

```python run
acf_vals = stattools.acf(np.log(y), nlags=28, fft=True)
print("ACF of log sales at lags 1..14, 21, 28:")
print(pd.Series(acf_vals[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,21,28]], index=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,21,28]).round(3).to_string())
```
```text
ACF of log sales at lags 1..14, 21, 28:
1    0.7300
2    0.4770
3    0.3660
4    0.3600
5    0.4730
6    0.7050
7    0.8540
8    0.7040
9    0.4560
10   0.3560
11   0.3480
12   0.4590
13   0.6840
14   0.8260
21   0.8150
28   0.7930
```

The raw series has autocorrelation near 1 for many lags because of the **trend** (everything is high together). The weekly rhythm shows as small bumps at lags 7, 14, 21, 28. Remove the trend by **differencing** (subtracting the previous value) and the picture clears:

```python run
dlog = np.log(y).diff().dropna()                     # day-to-day change in log sales (a growth rate)
d7 = np.log(y).diff(7).dropna()                      # change versus the same weekday last week
for name, s in [("log sales", np.log(y)), ("difference at lag 1", dlog), ("difference at lag 7", d7)]:
    a = stattools.acf(s, nlags=14, fft=True)
    print(f"{name:20s} ACF lags 1,2,7,14: {a[1]:+.2f} {a[2]:+.2f} {a[7]:+.2f} {a[14]:+.2f}")
```
```text
log sales            ACF lags 1,2,7,14: +0.73 +0.48 +0.85 +0.83
difference at lag 1  ACF lags 1,2,7,14: -0.03 -0.26 +0.56 +0.53
difference at lag 7  ACF lags 1,2,7,14: +0.16 +0.08 -0.42 -0.06
```

The lag-7 difference removes both the trend and the weekly pattern. What remains is short-memory noise (the small autocorrelation we built into the noise).

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Make one bar chart (an ACF plot) with lag 1 to 28 on the x-axis and autocorrelation on the y-axis. Use these values for log daily sales: lag 1 = 0.73, 2 = 0.48, 3 = 0.37, 4 = 0.36, 5 = 0.47, 6 = 0.71, 7 = 0.85, 8 = 0.70, 14 = 0.83, 21 = 0.82, 28 = 0.79. Highlight lags 7, 14, 21, 28 in a different colour and label them 'weekly rhythm'. Add a note that a high baseline comes from the trend."

### 3.2 White noise, random walk, and why it matters

A **white-noise** series has no autocorrelation: nothing in its past helps, so the best forecast is its mean. A **random walk** (each value is the previous value plus noise) has a unit root: the best forecast of every future step is simply the last value, and uncertainty grows like the square root of the horizon. Many financial series behave this way, and for them "naive" is very hard to beat. The check is the same for any series: do the *model's residuals* look like white noise? If not, there is structure left to exploit.

```python run
r = np.random.default_rng(1)
white = r.normal(size=1000)
walk = np.cumsum(white)
for name, s in [("white noise", white), ("random walk", walk), ("random walk, differenced", np.diff(walk))]:
    a = stattools.acf(s, nlags=10, fft=True)
    print(f"{name:26s} ACF lags 1,2,5,10: {a[1]:+.2f} {a[2]:+.2f} {a[5]:+.2f} {a[10]:+.2f}")
```
```text
white noise                ACF lags 1,2,5,10: -0.02 -0.03 -0.00 -0.01
random walk                ACF lags 1,2,5,10: +1.00 +0.99 +0.98 +0.96
random walk, differenced   ACF lags 1,2,5,10: -0.02 -0.03 -0.00 -0.01
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one figure with two line plots of 1000 steps. Top: white noise (random normal numbers, seed 1). Bottom: its running sum, a random walk. Under each plot add a small ACF bar chart for lags 1 to 10. The white noise ACF bars should be near 0; the random walk ACF should be near 1.0 (0.96 to 1.00). Add a third small line plot of the differenced random walk, which looks like white noise again."

### 3.3 Stationarity

A series is **(weakly) stationary** if its mean, variance and autocorrelation do not change over time. Trend and seasonality break it. Many classical models (ARIMA) assume stationarity *after transformation*, so we difference and take logs until the series looks stationary. The **augmented Dickey-Fuller (ADF)** test checks for a unit root: a small p-value says "stationary" (reject the unit root). Remember what it tests: it can be fooled by seasonality and by a short sample, so use it with the ACF, not instead of it.

```python run
def adf(name, s):
    stat, p, *_ = stattools.adfuller(s, autolag="AIC")
    print(f"{name:28s} ADF statistic {stat:7.2f}, p-value {p:.4f}  -> {'stationary' if p < 0.05 else 'NOT stationary'}")
adf("log sales", np.log(y))
adf("lag-1 difference of log", dlog)
adf("lag-7 difference of log", d7)
adf("random walk", pd.Series(walk))
adf("random walk, differenced", pd.Series(np.diff(walk)))
```
```text
log sales                    ADF statistic   -2.21, p-value 0.2016  -> NOT stationary
lag-1 difference of log      ADF statistic  -11.02, p-value 0.0000  -> stationary
lag-7 difference of log      ADF statistic   -8.45, p-value 0.0000  -> stationary
random walk                  ADF statistic   -1.17, p-value 0.6874  -> NOT stationary
random walk, differenced     ADF statistic  -32.15, p-value 0.0000  -> stationary
```

### 3.4 Why autocorrelation breaks ordinary cross-validation

In a series, a test day is correlated with the days around it. If those neighbours are in the training set, the model has been handed the answer (ds.04 section 7). The same correlation also means the **effective sample size is small**: 1,000 days of a highly autocorrelated series carry less information than 1,000 independent rows, so error estimates from a single backtest window are noisy. Both facts shape section 5.

### 3.5 Try it

1. Compute the ACF of the **residual** `d7` at lag 7 only, and explain why the lag-7 difference of a series with a weekly pattern produces a negative autocorrelation at lag 7 when the pattern is noisy.
2. Apply `stattools.pacf(dlog, nlags=10)`. Is there a cut-off? A PACF that cuts off after lag p suggests an AR(p) model (section 8).

## 4. Baselines and error metrics

### 4.1 The baselines

ds.04 said: a model must beat the best simple alternative, and on seasonal series the simple alternative is **seasonal naive**. Here are the standard baselines as functions of the training history `y_train` and the horizon `h`, each returning a Series on the future dates.

| Baseline | Forecast for step `k` | Best when |
|---|---|---|
| **Mean** | average of the history | no trend, no seasonality |
| **Naive** | the last observed value | random-walk-like series |
| **Seasonal naive** | the value one season ago (`y[t+k-m]`) | strong seasonality |
| **Drift** | last value plus the average historical change per step | a steady trend |
| **Seasonal naive + drift** | seasonal naive plus the drift of the seasonal pattern | seasonal and trending |
| **Seasonal average** | mean of the same weekday over the last `w` weeks | seasonal, noisy |

```python run
M = 7                                                    # the season: one week

def future_index(y_train, h):
    return pd.date_range(y_train.index[-1] + pd.Timedelta(days=1), periods=h, freq="D")

def f_mean(y_train, h, **kw):
    return pd.Series(y_train.mean(), index=future_index(y_train, h))

def f_naive(y_train, h, **kw):
    return pd.Series(y_train.iloc[-1], index=future_index(y_train, h))

def f_snaive(y_train, h, m=M, **kw):
    last_season = y_train.iloc[-m:].to_numpy()
    return pd.Series([last_season[k % m] for k in range(h)], index=future_index(y_train, h))

def f_drift(y_train, h, **kw):
    slope = (y_train.iloc[-1] - y_train.iloc[0]) / (len(y_train) - 1)
    return pd.Series(y_train.iloc[-1] + slope * np.arange(1, h + 1), index=future_index(y_train, h))

def f_savg(y_train, h, m=M, weeks=4, **kw):
    hist = y_train.iloc[-m * weeks:].to_numpy().reshape(weeks, m).mean(0)
    return pd.Series([hist[k % m] for k in range(h)], index=future_index(y_train, h))

def f_snaive_drift(y_train, h, m=M, **kw):
    base = f_snaive(y_train, h, m)
    season_change = (y_train.iloc[m:].to_numpy() - y_train.iloc[:-m].to_numpy()).mean()     # average change over one season
    steps = np.arange(1, h + 1)
    return base + season_change * (np.floor((steps - 1) / m) + 1)                          # one more season ahead = one more change

train, test = y.iloc[:-28], y.iloc[-28:]                 # one simple split for now: forecast the last 4 weeks
for name, fn in [("mean", f_mean), ("naive", f_naive), ("seasonal naive", f_snaive), ("drift", f_drift),
                 ("seasonal average (4 weeks)", f_savg), ("seasonal naive + drift", f_snaive_drift)]:
    fc = fn(train, 28)
    print(f"{name:28s} MAE on the last 28 days: {np.mean(np.abs(test.to_numpy() - fc.to_numpy())):7.2f}")
```
```text
mean                         MAE on the last 28 days:   33.43
naive                        MAE on the last 28 days:   43.96
seasonal naive               MAE on the last 28 days:   44.91
drift                        MAE on the last 28 days:   43.49
seasonal average (4 weeks)   MAE on the last 28 days:   31.05
seasonal naive + drift       MAE on the last 28 days:   45.79
```

Read the table with the date in mind: the last four weeks of the series end on 31 December, with promotions scattered through them and a holiday on 25 December. Plain **seasonal naive copies last week exactly, promotion spikes included**, so it is *worse* than just using the mean, and the drift correction does not help. The **seasonal average** over four weeks smooths those one-off events and wins by a wide margin. The lesson of the baseline family: the "obvious" baseline is not always the best simple baseline, and you should try the whole family before claiming a win.

### 4.2 Metrics

A forecast error is `e_t = y_t - ŷ_t`. Turning errors into one number:

| Metric | Formula | Property |
|---|---|---|
| **MAE** | mean `|e|` | in the units of the series; easy to read |
| **RMSE** | root of mean `e²` | punishes big misses |
| **MAPE** | mean `|e| / |y|` | a percentage; **explodes or is undefined when `y` is near 0**; favours under-forecasts |
| **sMAPE** | mean `2|e| / (|y| + |ŷ|)` | symmetric-ish percentage; still unstable near 0 |
| **MASE** | MAE divided by the in-sample MAE of the seasonal-naive forecast | **scale-free**; below 1 means "better than seasonal naive on training data" |
| **Bias (mean error)** | mean `e` | are we systematically too high or low? |

**MASE** is the standard for comparing across series with different scales, because the denominator is computed from the training history only (the average absolute change from one season to the next) and never from the test set.

```python run
def mae(y_true, y_pred):    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))
def rmse(y_true, y_pred):   return float(np.sqrt(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2)))
def mape(y_true, y_pred):   return float(np.mean(np.abs((np.asarray(y_true) - np.asarray(y_pred)) / np.asarray(y_true))))
def smape(y_true, y_pred):
    a, b = np.asarray(y_true), np.asarray(y_pred)
    return float(np.mean(2 * np.abs(a - b) / (np.abs(a) + np.abs(b))))
def bias(y_true, y_pred):   return float(np.mean(np.asarray(y_pred) - np.asarray(y_true)))
def mase(y_true, y_pred, y_train, m=M):
    scale = np.mean(np.abs(y_train.to_numpy()[m:] - y_train.to_numpy()[:-m]))          # in-sample seasonal-naive MAE
    return mae(y_true, y_pred) / scale

rows = []
for name, fn in [("naive", f_naive), ("seasonal naive", f_snaive), ("seasonal average", f_savg), ("seasonal naive + drift", f_snaive_drift)]:
    fc = fn(train, 28)
    rows.append((name, mae(test, fc), rmse(test, fc), mape(test, fc), smape(test, fc), mase(test, fc, train), bias(test, fc)))
print(pd.DataFrame(rows, columns=["forecast", "MAE", "RMSE", "MAPE", "sMAPE", "MASE", "bias"]).set_index("forecast").round(3).to_string())
```
```text
                           MAE    RMSE   MAPE  sMAPE   MASE     bias
forecast                                                            
naive                  43.9640 55.3390 0.1510 0.1670 1.7900 -36.8500
seasonal naive         44.9070 56.1270 0.1820 0.1610 1.8280  30.1930
seasonal average       31.0520 36.2720 0.1190 0.1150 1.2640  11.5210
seasonal naive + drift 45.7880 57.0340 0.1860 0.1640 1.8640  31.5950
```

### 4.3 When percentage errors lie

MAPE divides by the actual value. It has two defects. A series that touches zero (intermittent demand) makes it infinite. And it is **asymmetric**: an under-forecast can cost at most 100%, while an over-forecast has no ceiling, so minimising MAPE pushes forecasts *low*.

```python run
actual = np.array([50.0, 150.0])
for name, f in [("forecast 100 (the middle)", np.array([100.0, 100.0])), ("forecast 75 (biased low)", np.array([75.0, 75.0]))]:
    print(f"{name:26s} MAE {mae(actual, f):6.1f} | MAPE {mape(actual, f):.3f}")
with np.errstate(divide="ignore", invalid="ignore"):
    print("MAPE when an actual value is 0:", mape(np.array([10.0, 0.0, 12.0]), np.array([9.0, 1.0, 11.0])))
```
```text
forecast 100 (the middle)  MAE   50.0 | MAPE 0.667
forecast 75 (biased low)   MAE   50.0 | MAPE 0.500
MAPE when an actual value is 0: inf
```

Both forecasts have the same absolute error, but MAPE prefers the one that is systematically too low. That is a real incentive problem when a model is tuned on MAPE.

Rule: use **MAE or RMSE for decisions in the series' own units**, **MASE to compare across series or against the seasonal-naive baseline**, and report **bias** next to them. Avoid MAPE unless the series is large and strictly positive.

### 4.4 The skill score against the baseline

The honest summary of a forecaster is its **skill relative to seasonal naive**: `1 - MAE_model / MAE_snaive`. Positive means it beat the baseline; zero means a tie; negative means it is worse than doing nothing clever. This single number is the answer to the outcome of this chapter, once it is measured properly (next section).

```python run
def skill(err_model, err_baseline):
    return 1 - err_model / err_baseline
best_simple = f_snaive_drift(train, 28)
print(f"skill of 'seasonal naive + drift' over 'seasonal naive' on this one window: {skill(mae(test, best_simple), mae(test, f_snaive(train, 28))):+.3f}")
```
```text
skill of 'seasonal naive + drift' over 'seasonal naive' on this one window: -0.020
```

One window is one draw from a noisy process. The next section replaces it by many.

### 4.5 Try it

1. Make the seasonal average use 8 weeks instead of 4. Does MAE improve? What is the trade-off between a longer averaging window and a trend that keeps moving?
2. Implement `f_snaive` with `m=365` (a yearly seasonal naive) and compare on the last 28 days. Why does it need at least a year of history, and what does it ignore?


## 5. Backtesting with rolling origins

### 5.1 Why one test window is not enough

In section 4 we scored the baselines on a single window, the last four weeks. That window happened to contain promotions and a holiday, so the "winner" was partly an accident of the calendar. A single split gives one error number from one stretch of time, and with autocorrelated data that number is noisy. We need many forecasts, each made honestly from its own origin.

### 5.2 The rolling-origin backtest

A **rolling-origin backtest** (also called time-series cross-validation, or walk-forward validation) repeats the real forecasting situation many times:

1. Pick an origin. Train on history **up to** the origin.
2. Forecast the next `h` steps.
3. Compare with what actually happened.
4. Move the origin forward and repeat, so every forecast is an out-of-sample forecast from its own "now".

```text
origin 1:  [=============== train ===============] [ h ]
origin 2:  [================= train ================] [ h ]
origin 3:  [=================== train ===================] [ h ]      (expanding window)
origin 3:        [============ train ============] [ h ]               (sliding window)
```

Choices to make, and to **write down** with the result:

| Choice | Meaning | Guidance |
|---|---|---|
| `h` | horizon | the horizon the business needs (here 14 days) |
| `initial` | smallest training size | enough for the model to be fitted sensibly (here 1,000 days) |
| `step` | distance between origins | `step >= h` makes the test windows not overlap |
| window | **expanding** (all history) or **sliding** (last N days) | sliding if old data is no longer relevant |
| refit | fit a new model at every origin, or reuse | refit at every origin is the honest default |

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate a rolling-origin backtest on a timeline of 1461 daily points. The first origin is at day 1000 with horizon h = 14. Each step shows a blue 'train' bar from day 0 up to the origin and an orange 'forecast' bar of 14 days after it, then the origin moves forward by 14 days. Add a toggle between expanding window (blue bar starts at 0) and sliding window (fixed length). Show the step number."


### 5.3 A general backtest function

Every forecaster has the same signature `f(y_train, h, X_tr=None, X_future=None)` and returns `h` numbers. Optional `X_tr`, `X_future` carry **known-in-advance** covariates (promotions, holidays), cut at the origin like the history.

```python run
def backtest(y, forecaster, h=14, initial=1000, step=14, window=None, X=None):
    """Rolling-origin backtest. Returns one row per (origin, horizon step)."""
    rows = []
    for o in range(initial, len(y) - h + 1, step):                 # o = number of observations available at the origin
        lo = 0 if window is None else max(0, o - window)
        y_tr = y.iloc[lo:o]
        X_tr = None if X is None else X.iloc[lo:o]
        X_fu = None if X is None else X.iloc[o:o + h]
        fc = np.asarray(forecaster(y_tr, h, X_tr=X_tr, X_future=X_fu), dtype=float)
        assert len(fc) == h, "forecaster must return exactly h values"
        for k in range(h):
            rows.append((y.index[o - 1], y.index[o + k], k + 1, float(y.iloc[o + k]), fc[k]))
    return pd.DataFrame(rows, columns=["origin", "date", "horizon", "actual", "forecast"])

PROTOCOL = dict(h=14, initial=1000, step=14)
SCALE = float(np.mean(np.abs(y.to_numpy()[M:1000] - y.to_numpy()[:1000 - M])))     # MASE scale from the first 1,000 days only

baselines = {"mean": f_mean, "naive": f_naive, "seasonal naive": f_snaive, "drift": f_drift,
             "seasonal average (4w)": f_savg, "seasonal naive + drift": f_snaive_drift}
results = {name: backtest(y, fn, **PROTOCOL) for name, fn in baselines.items()}
n_origins = results["naive"]["origin"].nunique()
first, last = results["naive"]["date"].min().date(), results["naive"]["date"].max().date()
print(f"{n_origins} origins, horizon {PROTOCOL['h']}, forecasts for {first} to {last}, {len(results['naive'])} forecast values per model")
```
```text
32 origins, horizon 14, forecasts for 2023-09-28 to 2024-12-18, 448 forecast values per model
```

### 5.4 Summarising a backtest

```python run
def summarise(results, base="seasonal naive"):
    rows = []
    for name, bt in results.items():
        e = bt["actual"] - bt["forecast"]
        rows.append((name, e.abs().mean(), np.sqrt((e ** 2).mean()), e.abs().mean() / SCALE, smape(bt["actual"], bt["forecast"]), -e.mean()))
    out = pd.DataFrame(rows, columns=["model", "MAE", "RMSE", "MASE", "sMAPE", "bias"]).set_index("model")
    out["skill vs " + base] = 1 - out["MAE"] / out.loc[base, "MAE"]
    return out

print(summarise(results).round(3).sort_values("MAE").to_string())
```
```text
                           MAE    RMSE   MASE  sMAPE     bias  skill vs seasonal naive
model                                                                                 
seasonal average (4w)  26.4100 36.1220 1.1670 0.0860   1.2180                   0.1550
seasonal naive         31.2500 43.8450 1.3810 0.1000   2.3020                   0.0000
seasonal naive + drift 31.3220 43.9340 1.3840 0.1000   3.3520                  -0.0020
drift                  46.8420 62.4850 2.0700 0.1540 -27.6140                  -0.4990
naive                  47.0190 62.6910 2.0780 0.1540 -28.3700                  -0.5050
mean                   57.1510 75.0590 2.5260 0.1910 -46.8390                  -0.8290
```

> **Predict the output.** Before reading the table: which of "naive", "seasonal naive" and the 4-week "seasonal average" will have the lowest backtest error? And will the plain mean be better or worse than the naive forecast?

<details><summary>Answer</summary>

The **seasonal average** has the lowest error of the simple forecasters (MAE 26.4 against 31.3 for seasonal naive), because it smooths the one-off promotion spikes that plain seasonal naive copies. The **mean is the worst** of all (57.2), even worse than naive (47.0): with a rising series and strong weekly swings, the overall average is wrong almost every day.

</details>

Now the table is based on 32 independent four-week-ish stretches instead of one. Read three things: which baseline is best, how far the **mean** is from the seasonal ones (it shows how strong the seasonality is), and the sign of the **bias** (the naive forecast is too low in a rising series).

### 5.5 Error by horizon and by origin

Forecasts get worse further out; a model that wins at one step may lose at fourteen. And individual origins differ a lot.

```python run
def by_horizon(results, names):
    d = {n: results[n].assign(ae=lambda x: (x.actual - x.forecast).abs()).groupby("horizon")["ae"].mean() for n in names}
    return pd.DataFrame(d)
print("MAE by horizon step (days ahead):")
print(by_horizon(results, ["naive", "seasonal naive", "seasonal average (4w)"]).iloc[[0, 1, 2, 6, 7, 13]].round(2).to_string())

bt = results["seasonal average (4w)"].assign(ae=lambda x: (x.actual - x.forecast).abs())
per_origin = bt.groupby("origin")["ae"].mean()
print("\nMAE per origin of the seasonal average: min %.1f, median %.1f, max %.1f, std %.1f" % (per_origin.min(), per_origin.median(), per_origin.max(), per_origin.std()))
print("the three worst origins (forecast made on):", [d.date().isoformat() for d in per_origin.sort_values(ascending=False).index[:3]])
```
```text
MAE by horizon step (days ahead):
          naive  seasonal naive  seasonal average (4w)
horizon                                               
1       30.4200         26.6400                29.1100
2       68.7200         34.8700                30.8600
3       93.1100         23.8200                19.7600
7       25.4900         25.4900                21.1000
8       30.6900         27.6900                26.9500
14      26.0300         26.0300                20.5400

MAE per origin of the seasonal average: min 12.0, median 27.4, max 40.2, std 6.9
the three worst origins (forecast made on): ['2024-05-22', '2023-09-27', '2024-02-14']
```

Two things to notice in the horizon table. At steps 7 and 14 the **naive and seasonal-naive forecasts are identical**: the target is the same weekday as the origin day, so "last value" and "same weekday last week" are the same number. And errors do not simply grow with the horizon here, because a weekly pattern is predictable at any distance; what changes with the horizon is how much recent information (a promotion, a level shift) the forecast can use. The worst origins are the ones followed by holidays and promotions the baseline did not know about. A backtest that reports only the average hides this; always look at the **spread** and at the worst cases.

### 5.6 Does it beat seasonal naive? Skill with an error bar

This is the outcome of the chapter. A model beats the baseline if its **skill** is positive and the positive value is not luck. The tool is the same as in ds.04: a **paired** comparison on the same origins, with a bootstrap. Resample whole origins (the unit of independence, since forecasts within one origin are correlated) with replacement, and recompute the skill each time.

```python run
def origin_errors(bt):
    return (bt["actual"] - bt["forecast"]).abs().groupby(bt["origin"]).mean()

def skill_ci(bt_model, bt_base, n_boot=4000, seed=0):
    em, eb = origin_errors(bt_model), origin_errors(bt_base)
    assert (em.index == eb.index).all(), "compare models on identical origins"
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(em), (n_boot, len(em)))
    sk = 1 - em.to_numpy()[idx].mean(1) / eb.to_numpy()[idx].mean(1)
    point = 1 - em.mean() / eb.mean()
    lo, hi = np.percentile(sk, [2.5, 97.5])
    return point, lo, hi

def verdict(name, bt_model, bt_base, base_name="seasonal naive"):
    point, lo, hi = skill_ci(bt_model, bt_base)
    word = "BEATS" if lo > 0 else ("LOSES TO" if hi < 0 else "is not distinguishable from")
    print(f"{name:26s} skill vs {base_name}: {point:+.3f}  95% interval [{lo:+.3f}, {hi:+.3f}]  -> {word} {base_name}")

for name in ["seasonal average (4w)", "seasonal naive + drift", "naive", "mean"]:
    verdict(name, results[name], results["seasonal naive"])
```
```text
seasonal average (4w)      skill vs seasonal naive: +0.155  95% interval [+0.064, +0.233]  -> BEATS seasonal naive
seasonal naive + drift     skill vs seasonal naive: -0.002  95% interval [-0.007, +0.002]  -> is not distinguishable from seasonal naive
naive                      skill vs seasonal naive: -0.505  95% interval [-0.653, -0.366]  -> LOSES TO seasonal naive
mean                       skill vs seasonal naive: -0.829  95% interval [-1.075, -0.609]  -> LOSES TO seasonal naive
```

Notice the language: the verdict is one of three, not two. "Not distinguishable from" is a legitimate and common result, and it means: keep the simpler forecaster.

### 5.7 Expanding or sliding window

If the world changes (our growth slows after day 1,100), old data can mislead, and a sliding window forgets it. The window only matters for models that **learn from the whole training set**. The baselines above look at the last few weeks, so a window cannot change them. Section 11.4 tests windows on a fitted model (Holt-Winters), where the choice does matter, and finds an instructive answer.

### 5.8 A checklist for a trustworthy backtest

1. Every training set ends **before** its test window. Assert it in code.
2. The same origins for every model being compared.
3. Report horizon, number of origins, period covered, window type, refit policy.
4. Report the baseline's error next to the model's, plus skill with an interval.
5. Look at error by horizon and the worst origins.
6. Choose hyperparameters inside the training part of each origin (or on earlier origins), never on the test windows. If you tuned on the backtest, hold out a final, untouched period (the sealed test of ds.03 and ds.04).

### 5.9 Try it

1. Change the protocol to `step=7` (overlapping windows). Does the skill interval get narrower? Why is that narrowing not real?
2. Add a backtest at `h=1` and `h=28`. How does the gap between `naive` and `seasonal naive` change with the horizon?

## 6. Avoiding future-data leakage

### 6.1 Where the future sneaks in

In ds.04 section 7 you saw a centred rolling window leak. Time series offer many more ways, and each makes a backtest look better than reality:

| Leak | How it happens | Detect |
|---|---|---|
| **Centred or forward windows** | `rolling(center=True)`, `shift(-1)` | truncation test |
| **Statistics over the whole series** | scaling, mean encoding or seasonal profile computed on all dates | fit inside each origin |
| **Random CV on a series** | neighbours of a test day sit in the training set | use rolling origins only |
| **Features not yet known at the origin** | tomorrow's temperature *actual* instead of its forecast; today's total when the day is not over | write the "available when?" time for every column |
| **Target-derived features without a shift** | `y.rolling(7).mean()` includes today's `y` | always `shift(1)` first |
| **Revised data** | the value in your table is the final, corrected one; at the origin the first estimate was different | keep "as of" snapshots |
| **Tuning on the backtest** | choose the model or parameters by test error | sealed final period |

### 6.2 An automatic truncation test

The test: compute the features on the full series, then on the series cut at time `t`, and compare the feature values at `t`. If they differ, the feature at `t` used something after `t`. Run it at many cut points and fail loudly.

```python run
def assert_no_lookahead(make_features, series, cuts=(300, 500, 700, 900, 1100), tol=1e-9):
    full = make_features(series)
    bad = []
    for t in cuts:
        part = make_features(series.iloc[: t + 1])
        a, b = full.iloc[t].to_numpy(dtype=float), part.iloc[t].to_numpy(dtype=float)
        diff = ~np.isclose(a, b, atol=tol, equal_nan=True)
        bad += [part.columns[i] for i in np.flatnonzero(diff)]
    return sorted(set(bad))

def good_features(s):
    return pd.DataFrame({"lag1": s.shift(1), "lag7": s.shift(7), "roll7_past": s.shift(1).rolling(7).mean(),
                         "ewm_past": s.shift(1).ewm(span=7).mean()})

def leaky_features(s):
    f = good_features(s)
    f["roll7_centred"] = s.rolling(7, center=True).mean()                  # uses 3 future days
    f["roll7_now"] = s.rolling(7).mean()                                    # uses today's value: a leak for forecasting today
    f["next_day"] = s.shift(-1)                                             # the plainest leak
    f["global_scaled"] = (s - s.mean()) / s.std()                           # statistics from the whole series
    return f

print("good features, columns that look ahead :", assert_no_lookahead(good_features, y) or "none")
print("leaky features, columns that look ahead:", assert_no_lookahead(leaky_features, y))
```
```text
good features, columns that look ahead : none
leaky features, columns that look ahead: ['global_scaled', 'next_day', 'roll7_centred']
```

### 6.3 What a leak does to a score

We forecast **one day ahead** with a gradient-boosting model on the series' past plus calendar columns, and evaluate on the last year with the model fitted on the first three years. The only thing that changes is the feature set or the evaluation scheme.

```python run
def calendar(idx):
    return pd.DataFrame({"dow": idx.dayofweek, "doy_sin": np.sin(2 * np.pi * idx.dayofyear / 365.25),
                         "doy_cos": np.cos(2 * np.pi * idx.dayofyear / 365.25)}, index=idx)

ly = np.log(y)
base_X = pd.concat([calendar(y.index), demand[["promo", "holiday"]], good_features(ly)], axis=1)
split = 1096
def hgb():
    return ensemble.HistGradientBoostingRegressor(max_iter=150, learning_rate=0.08, max_depth=4, random_state=0)

def holdout_mae(X, name):
    Xv = X.iloc[7:]; yv = ly.iloc[7:]; cut_ = split - 7
    m = hgb().fit(Xv.iloc[:cut_], yv.iloc[:cut_])
    p = m.predict(Xv.iloc[cut_:])
    return mae(y.iloc[split:], np.exp(p))

rows = [("correct: past-only features, time split", holdout_mae(base_X, ""))]
leak_c = base_X.assign(roll7_centred=ly.rolling(7, center=True).mean())
rows.append(("leak: + centred 7-day mean", holdout_mae(leak_c, "")))
leak_now = base_X.assign(roll7_now=ly.rolling(7).mean())
rows.append(("leak: + rolling mean including today", holdout_mae(leak_now, "")))
Xv, yv = base_X.iloc[7:], ly.iloc[7:]
kf = model_selection.KFold(5, shuffle=True, random_state=0)
oof = model_selection.cross_val_predict(hgb(), Xv, yv, cv=kf)
rows.append(("wrong scheme: random 5-fold on past-only features", mae(y.iloc[7:], np.exp(oof))))
rows.append(("reference: seasonal naive on the same last year", mae(y.iloc[split:], y.shift(7).iloc[split:])))
print(pd.DataFrame(rows, columns=["setup", "one-day-ahead MAE"]).set_index("setup").round(2).to_string())
```
```text
                                                   one-day-ahead MAE
setup                                                               
correct: past-only features, time split                      20.4300
leak: + centred 7-day mean                                   17.4400
leak: + rolling mean including today                         18.0300
wrong scheme: random 5-fold on past-only features            16.1000
reference: seasonal naive on the same last year              30.7500
```

Same model, same data. The honest setup gives the honest error. The leaky features make it look about 15% better, and the *random* scheme about 21% better while using only legitimate features: that is interpolation (ds.04 section 7), a leak in the split, not in the features. None of these inflated numbers is dramatic, and that is the danger: a 15% "improvement" looks like a plausible result of a good model, and nobody investigates it. Leakage in time series is usually subtle, and the tests of section 6.2 are the defence, not suspicion alone.

### 6.4 Known-future versus unknown-future covariates

Not every column that exists in the future table is usable. Sort every extra column into one of three kinds:

| Kind | Example | Use at forecast time |
|---|---|---|
| **Known in advance** | calendar, holidays, planned promotions, prices already set | the true future values are available: use them |
| **Unknown but forecastable** | temperature, competitor price | you only have a *forecast* of it at the origin: train with forecast-quality values, not actuals |
| **Unknown** | tomorrow's footfall, today's web traffic | cannot be used as a future feature at all; only its lags |

The classic trap is training with the **actual** temperature and deploying with the **forecast** temperature, which is noisier. The model learned to trust a better signal than it will ever get. The cure is to backtest with the data exactly as it was available at each origin.

### 6.5 Try it

1. Add `ly.rolling(7).std()` (not shifted) to the feature set and check it with `assert_no_lookahead`. Is it caught? Does it improve the one-day-ahead MAE?
2. Add a "promo in the next 7 days" feature (a count of `promo` in the following week). Is that a leak? Think about when promotions are planned.

## 7. Exponential smoothing

### 7.1 The idea: a weighted average that forgets

Exponential smoothing forecasts with a weighted average of the past in which **recent observations count more** and the weights fall off geometrically. The simplest version, **simple exponential smoothing (SES)**, keeps one number, the **level** `l`, and updates it with each new observation:

```text
l_t = α · y_t + (1 − α) · l_{t−1}          forecast for every future step:  ŷ_{t+k} = l_t
```

`α` (alpha, between 0 and 1) is the smoothing parameter. Large `α` reacts quickly (and chases noise); small `α` averages over a long past (and reacts slowly). Two special cases: `α = 1` is the naive forecast, `α → 0` approaches the overall mean. We implement it and match statsmodels exactly.

```python run
def ses_fit(y_values, alpha, level0=None):
    level = y_values[0] if level0 is None else level0
    one_step = []                                      # forecast for time t made at t-1
    for v in y_values:
        one_step.append(level)
        level = alpha * v + (1 - alpha) * level
    return np.array(one_step), level

ys = y.iloc[:200].to_numpy()
ours_fit, ours_level = ses_fit(ys, alpha=0.3)
sm_fit = ExponentialSmoothing(y.iloc[:200], initialization_method="known", initial_level=ys[0]).fit(smoothing_level=0.3, optimized=False)
print("max |our one-step forecasts - statsmodels fittedvalues| =", float(np.max(np.abs(ours_fit - sm_fit.fittedvalues.to_numpy()))))
print("our final level", round(ours_level, 6), "| statsmodels forecast", round(float(sm_fit.forecast(1).iloc[0]), 6))
```
```text
max |our one-step forecasts - statsmodels fittedvalues| = 0.0
our final level 249.661227 | statsmodels forecast 249.661227
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate simple exponential smoothing step by step. Use a short noisy series of about 15 daily sales values around 250 (invent them). The update rule is level = alpha * y + (1 - alpha) * previous level, starting with level = first value. Draw the data as dots and the level as a line, with a slider for alpha from 0.05 to 1. Show the table of y, old level and new level for each step."


### 7.2 Adding trend and seasonality: Holt and Holt-Winters

- **Holt's linear method** adds a **trend** state `b` (the current slope): forecast `ŷ_{t+k} = l_t + k·b_t`. A **damped** trend multiplies the slope by `φ < 1` each step so the forecast flattens out instead of rising forever, which is usually more accurate at long horizons.
- **Holt-Winters** adds **seasonal** states (one per position in the season): additive (`+ s`) or multiplicative (`× s`). Each state has its own smoothing parameter (`α`, `β`, `γ`) and all are estimated by maximising the fit.

Our series is multiplicative, so we model **log sales** with additive components (the log trick of section 2.2).

```python run
y_fit = y.iloc[:1000]
t0 = time.perf_counter()
hw = ExponentialSmoothing(np.log(y_fit), trend="add", damped_trend=True, seasonal="add", seasonal_periods=7, initialization_method="estimated").fit()
print(f"fit in {time.perf_counter() - t0:.2f} s")
print("smoothing parameters: alpha(level) %.3f, beta(trend) %.4f, gamma(seasonal) %.3f, phi(damping) %.3f" % (
    hw.params["smoothing_level"], hw.params["smoothing_trend"], hw.params["smoothing_seasonal"], hw.params["damping_trend"]))
fc = np.exp(hw.forecast(14))
actual = y.iloc[1000:1014]
print("14-day forecast vs actual (first 7 days):")
print(pd.DataFrame({"forecast": fc.iloc[:7].round(1), "actual": actual.iloc[:7]}).to_string())
print(f"MAE over the 14 days: Holt-Winters {mae(actual, fc):.2f} | seasonal naive {mae(actual, f_snaive(y_fit, 14)):.2f} | seasonal average {mae(actual, f_savg(y_fit, 14)):.2f}")
```
```text
fit in 0.17 s
smoothing parameters: alpha(level) 0.112, beta(trend) 0.0166, gamma(seasonal) 0.000, phi(damping) 0.986
14-day forecast vs actual (first 7 days):
            forecast   actual
2023-09-28  297.5000 368.8000
2023-09-29  339.3000 337.3000
2023-09-30  379.9000 360.8000
2023-10-01  306.9000 285.0000
2023-10-02  259.4000 223.2000
2023-10-03  267.8000 248.7000
2023-10-04  279.0000 265.0000
MAE over the 14 days: Holt-Winters 32.35 | seasonal naive 39.00 | seasonal average 36.46
```

### 7.3 `alpha` is a memory length

```python run
rows = []
for alpha in [0.05, 0.2, 0.5, 0.9]:
    fit_, _ = ses_fit(np.log(y.iloc[:1000].to_numpy()), alpha)
    rows.append((alpha, "average age of the data used ~ %.1f days" % (1 / alpha), float(np.mean(np.abs(np.log(y.iloc[:1000].to_numpy()) - fit_)))))
print(pd.DataFrame(rows, columns=["alpha", "memory", "one-step MAE of SES on log sales"]).to_string(index=False))
```
```text
 alpha                                   memory  one-step MAE of SES on log sales
0.0500 average age of the data used ~ 20.0 days                            0.1308
0.2000  average age of the data used ~ 5.0 days                            0.1336
0.5000  average age of the data used ~ 2.0 days                            0.1408
0.9000  average age of the data used ~ 1.1 days                            0.1363
```

SES alone (no seasonality) is poor on a weekly series for any `α`: the weekly swing is far larger than the trend it is trying to track. That is why we add the seasonal states.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one bar chart of the weights that simple exponential smoothing gives to past observations: the weight at k days back is alpha * (1 - alpha)^k. Plot four panels for alpha = 0.05, 0.2, 0.5 and 0.9 for k = 0 to 30, on the same y-axis. Label each panel with its average age of data, 1/alpha: 20, 5, 2 and 1.1 days."


### 7.4 Backtesting it against the baselines

A forecaster for the backtest: refit at every origin, on the log scale, return to the original scale.

```python run
def f_hw(y_train, h, X_tr=None, X_future=None):
    m = ExponentialSmoothing(np.log(y_train), trend="add", damped_trend=True, seasonal="add", seasonal_periods=7, initialization_method="estimated").fit()
    return np.exp(m.forecast(h)).to_numpy()

t0 = time.perf_counter()
results["Holt-Winters (log, damped)"] = backtest(y, f_hw, **PROTOCOL)
print(f"backtest of Holt-Winters: {n_origins} refits in {time.perf_counter() - t0:.1f} s")
print(summarise(results).round(3).sort_values("MAE").to_string())
verdict("Holt-Winters (log, damped)", results["Holt-Winters (log, damped)"], results["seasonal naive"])
verdict("Holt-Winters (log, damped)", results["Holt-Winters (log, damped)"], results["seasonal average (4w)"], "seasonal average")
```
```text
backtest of Holt-Winters: 32 refits in 5.8 s
                               MAE    RMSE   MASE  sMAPE     bias  skill vs seasonal naive
model                                                                                     
Holt-Winters (log, damped) 22.7280 31.5320 1.0040 0.0740   0.0380                   0.2730
seasonal average (4w)      26.4100 36.1220 1.1670 0.0860   1.2180                   0.1550
seasonal naive             31.2500 43.8450 1.3810 0.1000   2.3020                   0.0000
seasonal naive + drift     31.3220 43.9340 1.3840 0.1000   3.3520                  -0.0020
drift                      46.8420 62.4850 2.0700 0.1540 -27.6140                  -0.4990
naive                      47.0190 62.6910 2.0780 0.1540 -28.3700                  -0.5050
mean                       57.1510 75.0590 2.5260 0.1910 -46.8390                  -0.8290
Holt-Winters (log, damped) skill vs seasonal naive: +0.273  95% interval [+0.201, +0.342]  -> BEATS seasonal naive
Holt-Winters (log, damped) skill vs seasonal average: +0.139  95% interval [+0.089, +0.190]  -> BEATS seasonal average
```

Two verdicts, deliberately: first against the textbook baseline, then against the **best** simple one. A model that only beats a weak baseline has not shown much.

### 7.5 What exponential smoothing cannot do

It has no way to use **external information**: it does not know a promotion is coming or that 25 December is a holiday. Those effects are in the residuals. Section 8's regression-with-ARMA-errors and section 9's gradient boosting can use them.

### 7.6 Try it

1. Fit `ExponentialSmoothing` with `trend=None` (no trend) and compare the backtest MAE. On a series with a trend, how does missing the trend show up in the bias?
2. Set `seasonal="mul"` on the original (not log) series and compare with the log-additive version. Which is easier to optimise, and why?

## 8. ARIMA, seasonal ARIMA and regressors

### 8.1 The idea: regress on your own past and your own errors

An **ARIMA(p, d, q)** model combines three pieces:

- **AR(p)**, autoregression: the series depends linearly on its last `p` values. AR(1): `y_t = c + φ·y_{t−1} + ε_t`.
- **I(d)**, integration: difference the series `d` times first to make it stationary (section 3).
- **MA(q)**, moving average of errors: the series depends on the last `q` forecast errors.

**Seasonal ARIMA** adds the same pieces at the seasonal lag: `(P, D, Q)_m`, for example a seasonal difference at lag 7 and a seasonal moving-average term. **SARIMAX** adds **eXogenous regressors**: the model for the part of the series the regressors do not explain is an ARMA process. That is how promotions and holidays enter.

### 8.2 An AR(1) you can see

Simulate `y_t = 0.7·y_{t−1} + ε_t` and let the model recover `φ`. A stationary AR(1) forecast decays toward the mean: each step multiplies the deviation by `φ`.

```python run
r = np.random.default_rng(2)
eps = r.normal(size=2000)
ar = np.zeros(2000)
for i in range(1, 2000):
    ar[i] = 0.7 * ar[i - 1] + eps[i]
m_ar = SARIMAX(ar, order=(1, 0, 0), trend="n").fit(disp=False)
print("true phi 0.700 | estimated phi %.3f (standard error %.3f)" % (m_ar.params[0], m_ar.bse[0]))
last = ar[-1]
print("last value %.2f -> forecasts for 1..6 steps:" % last, np.round(m_ar.forecast(6), 2), "| by hand last*phi^k:", np.round([last * m_ar.params[0] ** k for k in range(1, 7)], 2))
```
```text
true phi 0.700 | estimated phi 0.669 (standard error 0.017)
last value 2.51 -> forecasts for 1..6 steps: [1.68 1.12 0.75 0.5  0.34 0.23] | by hand last*phi^k: [1.68 1.12 0.75 0.5  0.34 0.23]
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot an AR(1) forecast decaying to the mean. The last observed value is 2.51 and phi is about 0.669. Draw a noisy simulated AR(1) series (y_t = 0.7 * y_(t-1) + noise) ending at 2.51, then the forecast points for steps 1 to 6: 1.68, 1.12, 0.75, 0.50, 0.34, 0.23, joined by a line that falls toward the mean 0. Label each point 'last * phi^k'."


### 8.3 The "airline model" for seasonal series

A durable workhorse for seasonal data with trend is `ARIMA(0,1,1)(0,1,1)_m` on the log scale: difference once at lag 1 and once at lag `m`, then model what remains with one moving-average term at each lag. We use a small AR/MA term at lag 1 (`order=(1,1,1)`) and the seasonal MA at lag 7, with promotions and holidays as regressors.

```python run
X_all = demand[["promo", "holiday"]].astype(float)
t0 = time.perf_counter()
sx = SARIMAX(np.log(y.iloc[:1000]), exog=X_all.iloc[:1000], order=(1, 1, 1), seasonal_order=(0, 1, 1, 7)).fit(disp=False, maxiter=100)
print(f"fit in {time.perf_counter() - t0:.1f} s | AIC {sx.aic:.1f}")
print(sx.summary().tables[1])
print("\nexpected effect of a promo on the log scale: ln(1.25) = %.3f ; of a holiday: ln(0.8) = %.3f" % (np.log(1.25), np.log(0.8)))
```
```text
fit in 3.0 s | AIC -2603.3
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
promo          0.2389      0.008     29.855      0.000       0.223       0.255
holiday       -0.2491      0.019    -13.162      0.000      -0.286      -0.212
ar.L1          0.2434      0.039      6.252      0.000       0.167       0.320
ma.L1         -0.8786      0.020    -43.079      0.000      -0.919      -0.839
ma.S.L7       -0.9691      0.011    -84.850      0.000      -0.992      -0.947
sigma2         0.0041      0.000     21.186      0.000       0.004       0.004
==============================================================================

expected effect of a promo on the log scale: ln(1.25) = 0.223 ; of a holiday: ln(0.8) = -0.223
```

The regressor coefficients recover the multipliers we built in (read them on the log scale: `exp(coef)` is the multiplier). The `sigma2` row is the variance of the one-step error.

### 8.4 Choosing orders: AIC and diagnostics

The **AIC** trades fit against complexity (lower is better) and can compare models **fitted to the same data with the same differencing**. It does not tell you whether the model is *adequate*. For that, test the residuals: if the model has captured the structure, residuals look like white noise. The **Ljung-Box** test checks the first several autocorrelations together; a small p-value means leftover structure.

```python run
rows = []
for order, sorder in [((0, 1, 1), (0, 1, 1, 7)), ((1, 1, 1), (0, 1, 1, 7)), ((1, 1, 1), (1, 1, 1, 7)), ((2, 1, 1), (0, 1, 1, 7))]:
    m = SARIMAX(np.log(y.iloc[:1000]), exog=X_all.iloc[:1000], order=order, seasonal_order=sorder).fit(disp=False, maxiter=100)
    resid = m.resid.iloc[8:]
    lb = acorr_ljungbox(resid, lags=[14], return_df=True)["lb_pvalue"].iloc[0]
    rows.append((str(order) + str(sorder), m.aic, m.bic, lb))
print(pd.DataFrame(rows, columns=["model (p,d,q)(P,D,Q,m)", "AIC", "BIC", "Ljung-Box p (lag 14)"]).set_index("model (p,d,q)(P,D,Q,m)").round(3).to_string())
```
```text
                               AIC         BIC  Ljung-Box p (lag 14)
model (p,d,q)(P,D,Q,m)                                              
(0, 1, 1)(0, 1, 1, 7)  -2,562.7150 -2,538.2160                0.0000
(1, 1, 1)(0, 1, 1, 7)  -2,603.2920 -2,573.8930                0.3890
(1, 1, 1)(1, 1, 1, 7)  -2,601.4860 -2,567.1880                0.4050
(2, 1, 1)(0, 1, 1, 7)  -2,602.0860 -2,567.7880                0.4320
```

Do not chase a p-value above 0.05 at any price. AIC differences smaller than about 2 are noise; a model with a slightly lower AIC but a worse backtest is the worse model. **The backtest decides**, as for every other model.

### 8.5 Backtest it

```python run
INTERVALS = {}                                           # origin date -> (lower, upper) of the 80% interval, kept for section 10

def f_sarimax(y_train, h, X_tr=None, X_future=None):
    m = SARIMAX(np.log(y_train), exog=X_tr, order=(1, 1, 1), seasonal_order=(0, 1, 1, 7)).fit(disp=False, maxiter=100)
    pred = m.get_forecast(h, exog=X_future)
    ci = pred.conf_int(alpha=0.2)                        # the 80% interval, on the log scale
    INTERVALS[y_train.index[-1]] = (np.exp(ci.iloc[:, 0].to_numpy()), np.exp(ci.iloc[:, 1].to_numpy()))
    return np.exp(pred.predicted_mean).to_numpy()

t0 = time.perf_counter()
results["SARIMAX + promo/holiday"] = backtest(y, f_sarimax, X=X_all, **PROTOCOL)
print(f"backtest of SARIMAX: {n_origins} refits in {time.perf_counter() - t0:.0f} s")
print(summarise(results).round(3).sort_values("MAE").to_string())
for rival in ["seasonal naive", "seasonal average (4w)", "Holt-Winters (log, damped)"]:
    verdict("SARIMAX + promo/holiday", results["SARIMAX + promo/holiday"], results[rival], rival)
```
```text
backtest of SARIMAX: 32 refits in 127 s
                               MAE    RMSE   MASE  sMAPE     bias  skill vs seasonal naive
model                                                                                     
SARIMAX + promo/holiday    16.2990 20.4590 0.7200 0.0550   1.3870                   0.4780
Holt-Winters (log, damped) 22.7280 31.5320 1.0040 0.0740   0.0380                   0.2730
seasonal average (4w)      26.4100 36.1220 1.1670 0.0860   1.2180                   0.1550
seasonal naive             31.2500 43.8450 1.3810 0.1000   2.3020                   0.0000
seasonal naive + drift     31.3220 43.9340 1.3840 0.1000   3.3520                  -0.0020
drift                      46.8420 62.4850 2.0700 0.1540 -27.6140                  -0.4990
naive                      47.0190 62.6910 2.0780 0.1540 -28.3700                  -0.5050
mean                       57.1510 75.0590 2.5260 0.1910 -46.8390                  -0.8290
SARIMAX + promo/holiday    skill vs seasonal naive: +0.478  95% interval [+0.410, +0.535]  -> BEATS seasonal naive
SARIMAX + promo/holiday    skill vs seasonal average (4w): +0.383  95% interval [+0.329, +0.434]  -> BEATS seasonal average (4w)
SARIMAX + promo/holiday    skill vs Holt-Winters (log, damped): +0.283  95% interval [+0.209, +0.349]  -> BEATS Holt-Winters (log, damped)
```

The regressors let SARIMAX forecast the promotion spikes and holiday dips that every earlier model had to treat as noise.

### 8.6 What the future values of the regressors mean

`forecast(h, exog=X_future)` needs the **future** promotion and holiday columns. They are legitimate here because they are known in advance (section 6.4). If a regressor is not known in advance you must forecast it first, and the forecast error of the regressor becomes part of the forecast error of the sales.

### 8.7 Where the statistical models stop

- Fitting a seasonal ARIMA with a long season (365 for daily data) is slow and fragile; use Fourier terms as regressors instead (`sin`/`cos` of the yearly cycle).
- They forecast **one series at a time**. With thousands of products you want a single model that learns across series (section 9).
- Prophet (an additive model with trend changepoints, Fourier seasonality and holidays) and the `pmdarima` auto-search are popular wrappers around the same ideas.

```python
# Try it on your machine:  pip install prophet pmdarima   (neither is installed here, so no output is shown)
from prophet import Prophet
df = demand.reset_index().rename(columns={"index": "ds", "sales": "y"})
m = Prophet(weekly_seasonality=True, yearly_seasonality=True)
m.add_regressor("promo"); m.add_regressor("holiday")
m.fit(df.iloc[:1000])
future = df.iloc[1000:1014][["ds", "promo", "holiday"]]
print(m.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]].head())
# Evaluate it with the SAME backtest() function above, by wrapping it as a forecaster f(y_train, h, X_tr, X_future).
```

### 8.8 Try it

1. Add Fourier terms for the yearly cycle (`sin` and `cos` of `2π·dayofyear/365.25`) as extra regressors in SARIMAX. Does the backtest improve?
2. Fit `SARIMAX` without the `promo` regressor and compare backtest MAE. How much of the error is the unmodelled promotions?


## 9. Gradient boosting for forecasting

### 9.1 Turning forecasting into a table

Machine-learning models want rows of features and a target. For forecasting we **build** that table from the series:

- **Lag features**: the value `j` steps back, `y[t−j]`.
- **Window features**: rolling mean, standard deviation, minimum or maximum over the last `w` steps.
- **Calendar features**: day of week, month, day of year (cyclical), holiday flags.
- **Known-future covariates**: promotion, price, planned events for the day being predicted.

The ds.04 rule applies to every column: it must be computable **at the origin**. And a new rule appears for multi-step forecasts: **a lag is only usable if it is old enough**. To forecast the day 10 steps ahead you cannot use `y[t−1]` of the target day, because that day is in the future too.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a table-building diagram. On the left, a daily sales series y with a marked 'origin' day. On the right, a feature table with one row per target day and columns: lag 1, lag 7, lag 14, rolling mean of the last 7 days, day of week, promo, holiday, target. Use arrows from the series cells to the row cells. Show for a forecast 10 days ahead that lag 1 of the target day is greyed out because it lies in the future."


### 9.2 Two strategies for multi-step forecasts

| Strategy | How | Strengths | Weakness |
|---|---|---|---|
| **Recursive** | train a one-step model; predict step 1, feed it back as a lag, predict step 2, and so on | one model; uses fresh lags | **errors compound**; later steps are built on earlier guesses |
| **Direct** | train a model that predicts step `k` straight from information at the origin (one model per `k`, or one model with `k` as a feature) | no compounding | needs a training table per horizon; ignores the intermediate path |

### 9.3 The direct strategy, written out

Stand at origin `o`. For each target `o + k` (`k = 1..14`) build features from information at `o`: the **level** (mean log sales of the last 28 days), the short-term movement (last 7 days versus 28), the values of the **same weekday** in the most recent weeks that are already known, and the calendar and covariates *of the target date*. One model learns all `k` at once, with `k` as a feature. The target is **log sales relative to the level**, which removes the trend (a tree cannot extrapolate a trend, ds.04 section 7.5).

```python run
H = 14
def direct_table(ly, dates, promo, holiday, origins, ks):
    """Rows for every (origin, step). ly: log series with NaN where unknown. Returns features, target (relative to the level), level."""
    ly = np.asarray(ly, float)
    cs = np.r_[0.0, np.cumsum(np.nan_to_num(ly))]
    o = np.asarray(origins)
    lvl28 = (cs[o + 1] - cs[o - 27]) / 28
    lvl7 = (cs[o + 1] - cs[o - 6]) / 7
    K = np.asarray(ks)[None, :]
    T = o[:, None] + K
    J = np.ceil(K / 7).astype(int)                                    # weeks back to reach a date that is already known at the origin
    rel = lambda back: ly[T - 7 * (J + back)] - lvl28[:, None]
    dow = dates.dayofweek.to_numpy()[T]
    doy = dates.dayofyear.to_numpy()[T]
    feats = [rel(0), rel(1), rel(2), np.broadcast_to((lvl7 - lvl28)[:, None], T.shape), np.broadcast_to(K, T.shape), dow,
             np.sin(2 * np.pi * doy / 365.25), np.cos(2 * np.pi * doy / 365.25), promo[T], holiday[T]]
    X = np.stack([np.asarray(f, float) for f in feats], axis=-1).reshape(-1, len(feats))
    target = (ly[T] - lvl28[:, None]).reshape(-1)
    return X, target, np.repeat(lvl28, T.shape[1])

DIRECT_COLS = ["same weekday, 1st known week", "same weekday, 2nd", "same weekday, 3rd", "momentum (7d - 28d level)", "horizon k", "day of week", "doy sin", "doy cos", "promo", "holiday"]

def f_gbm(y_train, h, X_tr=None, X_future=None, seed=0, **hgb_kw):
    n = len(y_train)
    dates = y_train.index.append(future_index(y_train, h))
    cov = pd.concat([X_tr, X_future])
    promo, holiday = cov["promo"].to_numpy(float), cov["holiday"].to_numpy(float)
    ly = np.r_[np.log(y_train.to_numpy()), np.full(h, np.nan)]
    ks = np.arange(1, h + 1)
    origins = np.arange(28, n - 1)                                    # every possible origin inside the training history
    Xr, tg, _ = direct_table(ly, dates, promo, holiday, origins, ks)
    ok = np.isfinite(tg)                                              # drops targets that would lie beyond the training data
    model = ensemble.HistGradientBoostingRegressor(max_iter=200, learning_rate=0.06, max_depth=4, min_samples_leaf=30, random_state=seed, **hgb_kw).fit(Xr[ok], tg[ok])
    Xo, _, lvl = direct_table(ly, dates, promo, holiday, np.array([n - 1]), ks)
    return np.exp(lvl + model.predict(Xo))

t0 = time.perf_counter()
one = f_gbm(y.iloc[:1000], H, X_tr=X_all.iloc[:1000], X_future=X_all.iloc[1000:1000 + H])
print(f"one fit + forecast in {time.perf_counter() - t0:.1f} s")
print("14-day forecast vs actual, first 7 days:", np.round(one[:7], 1), "|", y.iloc[1000:1007].to_numpy())
print("MAE over 14 days: GBM %.2f | seasonal naive %.2f | seasonal average %.2f" % (mae(y.iloc[1000:1014], one), mae(y.iloc[1000:1014], f_snaive(y.iloc[:1000], 14)), mae(y.iloc[1000:1014], f_savg(y.iloc[:1000], 14))))
```
```text
one fit + forecast in 0.2 s
14-day forecast vs actual, first 7 days: [365.1 323.3 355.4 297.  215.6 264.6 277.6] | [368.8 337.3 360.8 285.  223.2 248.7 265. ]
MAE over 14 days: GBM 13.38 | seasonal naive 39.00 | seasonal average 36.46
```

Look at the feature construction once more, because it is where leaks live: `rel(0)` is the value of the same weekday as the target, `J` weeks back, where `J = ceil(k / 7)` is the smallest number of weeks that lands on or before the origin. For `k = 1..7` that is the previous week, for `k = 8..14` two weeks back. Nothing in the row refers to a date after the origin. The truncation test of section 6.2 can check this mechanically.

```python run
def gbm_features_as_frame(s):
    """Wrap the direct features of the LAST origin of s in a one-row frame so assert_no_lookahead can inspect them."""
    n = len(s)
    dates = s.index.append(future_index(s, H)); promo = np.r_[demand["promo"].to_numpy(float)[:n], np.zeros(H)]; hol = np.r_[demand["holiday"].to_numpy(float)[:n], np.zeros(H)]
    ly_ = np.r_[np.log(s.to_numpy()), np.full(H, np.nan)]
    rows = []
    for t in range(n):
        if t < 40:
            rows.append([np.nan] * 3)
        else:
            X1, _, lvl = direct_table(ly_, dates, promo, hol, np.array([t]), np.array([1, 7, 14]))
            rows.append([X1[0, 0], X1[1, 0], X1[2, 3]])
    return pd.DataFrame(rows, index=s.index, columns=["rel(0) at k=1", "rel(0) at k=7", "momentum at k=14"])
print("direct features that look ahead:", assert_no_lookahead(gbm_features_as_frame, y.iloc[:800], cuts=(300, 500, 700)) or "none")
```
```text
direct features that look ahead: none
```

### 9.4 Backtest it

```python run
t0 = time.perf_counter()
results["GBM direct"] = backtest(y, f_gbm, X=X_all, **PROTOCOL)
print(f"backtest of the direct GBM: {n_origins} refits in {time.perf_counter() - t0:.0f} s")
print(summarise(results).round(3).sort_values("MAE").to_string())
for rival in ["seasonal naive", "seasonal average (4w)", "SARIMAX + promo/holiday"]:
    verdict("GBM direct", results["GBM direct"], results[rival], rival)
```
```text
backtest of the direct GBM: 32 refits in 9 s
                               MAE    RMSE   MASE  sMAPE     bias  skill vs seasonal naive
model                                                                                     
SARIMAX + promo/holiday    16.2990 20.4590 0.7200 0.0550   1.3870                   0.4780
GBM direct                 16.6480 21.3720 0.7360 0.0550   3.6200                   0.4670
Holt-Winters (log, damped) 22.7280 31.5320 1.0040 0.0740   0.0380                   0.2730
seasonal average (4w)      26.4100 36.1220 1.1670 0.0860   1.2180                   0.1550
seasonal naive             31.2500 43.8450 1.3810 0.1000   2.3020                   0.0000
seasonal naive + drift     31.3220 43.9340 1.3840 0.1000   3.3520                  -0.0020
drift                      46.8420 62.4850 2.0700 0.1540 -27.6140                  -0.4990
naive                      47.0190 62.6910 2.0780 0.1540 -28.3700                  -0.5050
mean                       57.1510 75.0590 2.5260 0.1910 -46.8390                  -0.8290
GBM direct                 skill vs seasonal naive: +0.467  95% interval [+0.395, +0.528]  -> BEATS seasonal naive
GBM direct                 skill vs seasonal average (4w): +0.370  95% interval [+0.305, +0.428]  -> BEATS seasonal average (4w)
GBM direct                 skill vs SARIMAX + promo/holiday: -0.021  95% interval [-0.104, +0.061]  -> is not distinguishable from SARIMAX + promo/holiday
```

### 9.5 The recursive strategy, and its compounding

```python run
def f_gbm_recursive(y_train, h, X_tr=None, X_future=None, seed=0):
    ly = np.log(y_train.to_numpy())
    idx = y_train.index
    cov = pd.concat([X_tr, X_future])
    promo, hol = cov["promo"].to_numpy(float), cov["holiday"].to_numpy(float)
    dates = idx.append(future_index(y_train, h))
    n = len(ly)

    def row(series, t):                                           # features for predicting position t from positions < t only
        return [series[t - 1], series[t - 2], series[t - 7], series[t - 14], series[t - 7:t].mean(), series[t - 28:t].mean(),
                dates.dayofweek[t], np.sin(2 * np.pi * dates.dayofyear[t] / 365.25), np.cos(2 * np.pi * dates.dayofyear[t] / 365.25), promo[t], hol[t]]
    Xt = np.array([row(ly, t) for t in range(28, n)])
    m = ensemble.HistGradientBoostingRegressor(max_iter=200, learning_rate=0.06, max_depth=4, min_samples_leaf=30, random_state=seed).fit(Xt, ly[28:] - Xt[:, 5])
    ext = np.r_[ly, np.zeros(h)]
    for k in range(h):                                            # feed each prediction back as the next lag
        t = n + k
        r_ = np.array(row(ext, t), float)[None, :]
        ext[t] = r_[0, 5] + m.predict(r_)[0]
    return np.exp(ext[n:])

t0 = time.perf_counter()
results["GBM recursive"] = backtest(y, f_gbm_recursive, X=X_all, **PROTOCOL)
print(f"backtest of the recursive GBM: {time.perf_counter() - t0:.0f} s")
hz = by_horizon(results, ["GBM direct", "GBM recursive", "seasonal average (4w)"])
print("MAE by horizon step:")
print(hz.iloc[[0, 1, 2, 6, 7, 13]].round(2).to_string())
```
```text
backtest of the recursive GBM: 9 s
MAE by horizon step:
         GBM direct  GBM recursive  seasonal average (4w)
horizon                                                  
1           15.8100        16.1200                29.1100
2           19.6600        19.2200                30.8600
3           17.8800        17.0500                19.7600
7           15.5400        15.3800                21.1000
8           18.7800        19.0700                26.9500
14          11.7000        10.6700                20.5400
```

Read the table honestly: **there is no visible compounding here**. The two strategies are within a few percent of each other at every horizon, and the recursive model is even slightly better at the longest steps. The reason is that this series is simple and the one-step model is accurate and unbiased; the weekly pattern and the calendar features anchor the later steps. Compounding becomes a problem when the one-step model has a small **bias** or a noisy series (each fed-back prediction carries the bias forward and grows it), which is common on real data. So the advice is not "direct is better"; it is: **try both and compare them by horizon on your backtest**. The direct form has two practical advantages that matter here too: it can use known-future covariates of the *target* date directly, and its training table treats all horizons in one model.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate a 14-day recursive forecast as a loop diagram. At step k, a model reads features (lag 1, lag 2, lag 7, lag 14, weekly and monthly means, calendar, promo) and predicts the next day's log sales. That prediction is appended to the series and becomes lag 1 for step k+1. Show steps 1 to 4, with the fed-back values in orange and real history in blue, and a note that errors can pile up."


### 9.6 Why the target is relative to the level

If we instead predict the raw log sales from raw lags, the tree sees values it has never seen when the series has grown, and flattens at the largest value in the training data (ds.04 section 7.5).

```python run
def f_gbm_raw(y_train, h, X_tr=None, X_future=None, seed=0):
    ly = np.log(y_train.to_numpy()); n = len(ly); idx = y_train.index
    dates = idx.append(future_index(y_train, h))
    cov = pd.concat([X_tr, X_future]); promo, hol = cov["promo"].to_numpy(float), cov["holiday"].to_numpy(float)
    ks = np.arange(1, h + 1)
    ext = np.r_[ly, np.full(h, np.nan)]
    def table(origins):
        O = np.asarray(origins)[:, None]; K = ks[None, :]; T = O + K; Jw = np.ceil(K / 7).astype(int)
        feats = [ext[T - 7 * Jw], ext[T - 7 * (Jw + 1)], np.broadcast_to(K, T.shape), dates.dayofweek.to_numpy()[T], promo[T], hol[T]]
        return np.stack([np.asarray(f, float) for f in feats], -1).reshape(-1, 6), ext[T].reshape(-1)
    Xr, tg = table(np.arange(28, n - 1)); ok = np.isfinite(tg)
    m = ensemble.HistGradientBoostingRegressor(max_iter=200, learning_rate=0.06, max_depth=4, min_samples_leaf=30, random_state=seed).fit(Xr[ok], tg[ok])
    return np.exp(m.predict(table([n - 1])[0]))

results["GBM direct, raw target"] = backtest(y, f_gbm_raw, X=X_all, **PROTOCOL)
rows = []
for name in ["GBM direct", "GBM direct, raw target"]:
    bt_ = results[name]
    rows.append((name, mae(bt_["actual"], bt_["forecast"]), bias(bt_["actual"], bt_["forecast"])))
print(pd.DataFrame(rows, columns=["model", "backtest MAE", "bias (forecast - actual)"]).set_index("model").round(2).to_string())
```
```text
                        backtest MAE  bias (forecast - actual)
model                                                         
GBM direct                   16.6500                    3.6200
GBM direct, raw target       20.4200                   -4.3500
```

The raw-target model has about 23% higher error and a **negative bias** (it under-forecasts, bias -4.4 against +3.6 for the relative model) because it cannot extrapolate growth. Predicting a *relative* quantity (and often a ratio to a seasonal baseline) is the standard fix, and it is the same idea as differencing in ARIMA.

### 9.7 Many series, one model

With thousands of products, fitting one ARIMA per product is slow and each model sees little data. A **global model** is trained on all products at once, with the product's identifier, price or category as features, so short series borrow strength from long ones. This is how most large retailers forecast. The direct table above extends naturally: add the product features and stack the tables. The backtest is unchanged except that origins and splits are by **time**, shared across products.

```python
# Try it on your machine:  pip install lightgbm   (not installed here, so no output is shown)
import lightgbm as lgb
model = lgb.LGBMRegressor(n_estimators=600, learning_rate=0.03, num_leaves=31, min_child_samples=40,
                          subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=0)
# Xr, tg are the direct-table arrays built exactly as in f_gbm above (for ONE series, or stacked over many series)
# model.fit(Xr[ok], tg[ok])      # same leak-free table, a faster boosting library
```

### 9.8 Try it

1. Add a feature `rel(3)` (a fourth same-weekday value) to `direct_table`. Does the backtest improve? Re-run the truncation test.
2. Train the direct model with `loss="absolute_error"` instead of squared error. The metric of the backtest is MAE: does matching the loss to the metric help?

## 10. Prediction intervals and probabilistic forecasts

### 10.1 A point is not enough

A point forecast of 300 units means little without its uncertainty. If demand could be anywhere between 250 and 350 you hold different stock than if it is between 295 and 305. A **prediction interval** at 80% is a range intended to contain the true value 80% of the time. It is **calibrated** when it does (ds.04 section 11 again, for intervals).

Two scores for an interval forecast, both computed on the backtest:

- **Coverage**: the share of actual values inside the interval. For a nominal 80% interval, aim for about 0.80. Too low = overconfident; too high = wastefully wide.
- **Width**: how wide the interval is. Among calibrated intervals, narrower is better.

For a quantile forecast `q` of level `τ`, the **pinball loss** is `τ·(y − q)` if `y ≥ q` and `(1 − τ)·(q − y)` otherwise. Its average is minimised by the true `τ`-quantile.

```python run
def pinball(y_true, q, tau):
    d = np.asarray(y_true) - np.asarray(q)
    return float(np.mean(np.maximum(tau * d, (tau - 1) * d)))
def coverage(y_true, lo, hi):
    y_true = np.asarray(y_true)
    return float(np.mean((y_true >= np.asarray(lo)) & (y_true <= np.asarray(hi))))
print("pinball loss of forecasting 100 when the truth is 120, at tau=0.9:", pinball([120], [100], 0.9), "and at tau=0.1:", pinball([120], [100], 0.1))
print("(under-forecasting costs 9 times more than over-forecasting at tau=0.9: the quantile leans high)")
```
```text
pinball loss of forecasting 100 when the truth is 120, at tau=0.9: 18.0 and at tau=0.1: 2.0
(under-forecasting costs 9 times more than over-forecasting at tau=0.9: the quantile leans high)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the pinball loss as a V-shaped line chart. The x-axis is the forecast q from 60 to 140 when the true value is y = 120. The loss is tau*(y-q) if y >= q, else (1-tau)*(q-y). Plot two lines, tau = 0.9 and tau = 0.1, and mark the point q = 100, where the losses are 18.0 and 2.0. Explain with a label which side is steeper."


### 10.2 Model-based intervals: SARIMAX

SARIMAX gives an interval from its error model (normal errors, correct structure). We kept the 80% interval of every backtest forecast of section 8 and can now check how honest it is.

> **Predict the output.** SARIMAX gives an 80% prediction interval for each forecast. Over the whole backtest, will about 80% of the actual values fall inside? Will the coverage be the same at step 1 and at step 14?

<details><summary>Answer</summary>

Overall the coverage is close to the target (0.81), but it differs a lot by horizon: only **0.66 at step 1** (intervals too narrow) and **0.94 at step 14** (too wide). The overall figure is an average of two opposite errors, which is why intervals must be checked by horizon.

</details>

```python run
sx_int = INTERVALS                                                         # filled by f_sarimax during the backtest of section 8
rows = []
for h_ in [1, 7, 14]:
    sub = results["SARIMAX + promo/holiday"].query("horizon == @h_")
    lo = np.array([sx_int[o][0][h_ - 1] for o in sub["origin"]]); hi = np.array([sx_int[o][1][h_ - 1] for o in sub["origin"]])
    rows.append((h_, coverage(sub["actual"], lo, hi), float(np.mean(hi - lo))))
sx_all_lo = np.array([sx_int[o][0][k - 1] for o, k in zip(results["SARIMAX + promo/holiday"]["origin"], results["SARIMAX + promo/holiday"]["horizon"])])
sx_all_hi = np.array([sx_int[o][1][k - 1] for o, k in zip(results["SARIMAX + promo/holiday"]["origin"], results["SARIMAX + promo/holiday"]["horizon"])])
rows.append(("all", coverage(results["SARIMAX + promo/holiday"]["actual"], sx_all_lo, sx_all_hi), float(np.mean(sx_all_hi - sx_all_lo))))
print(pd.DataFrame(rows, columns=["horizon step", "coverage of the nominal 80% interval", "mean width"]).set_index("horizon step").round(3).to_string())
```
```text
              coverage of the nominal 80% interval  mean width
horizon step                                                  
1                                           0.6560     47.5320
7                                           0.8440     50.8110
14                                          0.9380     55.6360
all                                         0.8060     56.4270
```

Overall coverage (0.81) looks perfect, but the rows above show it is an average of two failures: at step 1 the 80% interval covers only 66% (too narrow), at step 14 it covers 94% (too wide). The error model of the SARIMAX assumes the shape of the uncertainty grows in a certain way with the horizon, and the real series does not follow it. An interval has to be checked **by horizon**, not only on average.

### 10.3 Empirical intervals from past backtest errors

A model-free alternative that works for any point forecaster: collect the **relative errors** `log(actual / forecast)` from earlier backtest origins, by horizon, and use their quantiles to put an interval around a new point forecast. Calibrate on the earlier half of the origins, test on the later half. (This is the idea behind *conformal prediction*.)

```python run
def empirical_interval(bt_cal, bt_new, level=0.8):
    a = (1 - level) / 2
    err = np.log(bt_cal["actual"] / bt_cal["forecast"])
    q = err.groupby(bt_cal["horizon"]).quantile([a, 1 - a]).unstack()
    lo = bt_new["forecast"] * np.exp(q.loc[bt_new["horizon"], a].to_numpy())
    hi = bt_new["forecast"] * np.exp(q.loc[bt_new["horizon"], 1 - a].to_numpy())
    return lo.to_numpy(), hi.to_numpy()

origins_sorted = sorted(results["GBM direct"]["origin"].unique())
half = origins_sorted[len(origins_sorted) // 2]
rows = []
for name in ["GBM direct", "SARIMAX + promo/holiday", "seasonal average (4w)"]:
    bt_ = results[name]
    cal, new = bt_[bt_["origin"] < half], bt_[bt_["origin"] >= half]
    for level in [0.8, 0.95]:
        lo, hi = empirical_interval(cal, new, level)
        rows.append((name, level, coverage(new["actual"], lo, hi), float(np.mean(hi - lo))))
print(pd.DataFrame(rows, columns=["point forecaster", "nominal", "coverage on later origins", "mean width"]).round(3).to_string(index=False))
```
```text
       point forecaster  nominal  coverage on later origins  mean width
             GBM direct   0.8000                     0.7720     52.0820
             GBM direct   0.9500                     0.8790     70.8700
SARIMAX + promo/holiday   0.8000                     0.7410     55.0430
SARIMAX + promo/holiday   0.9500                     0.8300     73.0430
  seasonal average (4w)   0.8000                     0.6830     80.8180
  seasonal average (4w)   0.9500                     0.8620    125.3820
```

A shortfall of coverage on the later origins is the signature of **drift** (section 11): errors in the later period are larger than in the calibration period, so intervals calibrated on the past are too narrow.

### 10.4 Quantile gradient boosting

Boosting can fit a quantile directly: `loss="quantile"` with the target level. We fit the 10% and 90% quantiles of the direct model (an 80% interval) once on the first 1,000 days and test it on the later origins, comparing with SARIMAX on the same origins.

```python run
def direct_quantile_forecast(y_train, h, X_tr, X_future, taus=(0.1, 0.9)):
    n = len(y_train)
    dates = y_train.index.append(future_index(y_train, h))
    cov = pd.concat([X_tr, X_future]); promo, hol = cov["promo"].to_numpy(float), cov["holiday"].to_numpy(float)
    ly = np.r_[np.log(y_train.to_numpy()), np.full(h, np.nan)]; ks = np.arange(1, h + 1)
    Xr, tg, _ = direct_table(ly, dates, promo, hol, np.arange(28, n - 1), ks); ok = np.isfinite(tg)
    models = {t: ensemble.HistGradientBoostingRegressor(loss="quantile", quantile=t, max_iter=200, learning_rate=0.06, max_depth=4, min_samples_leaf=30, random_state=0).fit(Xr[ok], tg[ok]) for t in taus}
    return {t: m for t, m in models.items()}, ly, dates, promo, hol

models_q, ly_all, dates_all, promo_all, hol_all = direct_quantile_forecast(y.iloc[:1000], H, X_all.iloc[:1000], X_all.iloc[1000:1000 + H])
rows_lo, rows_hi, acts, hz_ = [], [], [], []
ly_full = np.log(y.to_numpy()); dates_full = y.index.append(future_index(y, H)); promo_full = np.r_[X_all["promo"].to_numpy(float), np.zeros(H)]; hol_full = np.r_[X_all["holiday"].to_numpy(float), np.zeros(H)]
for o in range(1000, len(y) - H + 1, 14):
    ly_o = np.r_[ly_full[:o], np.full(len(ly_full) + H - o, np.nan)]                 # nothing after the origin is visible
    Xo, _, lvl = direct_table(ly_o, dates_full, promo_full, hol_full, np.array([o - 1]), np.arange(1, H + 1))
    rows_lo.append(np.exp(lvl + models_q[0.1].predict(Xo))); rows_hi.append(np.exp(lvl + models_q[0.9].predict(Xo)))
    acts.append(y.to_numpy()[o:o + H]); hz_.append(np.arange(1, H + 1))
lo_q, hi_q, act_q = np.concatenate(rows_lo), np.concatenate(rows_hi), np.concatenate(acts)
sx_lo_aligned = sx_all_lo; sx_hi_aligned = sx_all_hi
print("same origins, same actual values (a quantile GBM trained once on the first 1,000 days; SARIMAX refit each origin):")
print(pd.DataFrame([("quantile GBM (10%, 90%)", coverage(act_q, lo_q, hi_q), float(np.mean(hi_q - lo_q)), pinball(act_q, lo_q, 0.1) + pinball(act_q, hi_q, 0.9)),
                    ("SARIMAX 80% interval", coverage(act_q, sx_lo_aligned, sx_hi_aligned), float(np.mean(sx_hi_aligned - sx_lo_aligned)), pinball(act_q, sx_lo_aligned, 0.1) + pinball(act_q, sx_hi_aligned, 0.9))],
                   columns=["method", "coverage (aim 0.80)", "mean width", "sum of the two pinball losses"]).set_index("method").round(3).to_string())
```
```text
same origins, same actual values (a quantile GBM trained once on the first 1,000 days; SARIMAX refit each origin):
                         coverage (aim 0.80)  mean width  sum of the two pinball losses
method                                                                                 
quantile GBM (10%, 90%)               0.7230     47.2120                         7.7880
SARIMAX 80% interval                  0.8060     56.4270                         7.3770
```

The SARIMAX interval is closer to nominal coverage and has the lower pinball total; the quantile GBM interval is narrower but too narrow (coverage 0.72 instead of 0.80), partly because it was trained once and never refit. Narrower is only better at equal coverage.

### 10.5 Reading interval results

- **Coverage far below nominal**: the intervals are overconfident. Typical causes: model misspecified, errors not normal, drift, calibrated on a quiet period. Widen them using backtest errors (10.3).
- **Coverage near nominal but very wide**: calibrated and useless. Compare widths among methods that have similar coverage.
- **Coverage depends on the situation**: check coverage separately on promotion days, holidays and weekdays (ds.04 section 12). Averages hide it.

```python run
bt_sx = results["SARIMAX + promo/holiday"].assign(lo=sx_all_lo, hi=sx_all_hi, promo=lambda d: X_all["promo"].reindex(d["date"]).to_numpy(), holiday=lambda d: X_all["holiday"].reindex(d["date"]).to_numpy())
rows = []
for name, mask in [("ordinary days", (bt_sx.promo == 0) & (bt_sx.holiday == 0)), ("promotion days", bt_sx.promo == 1), ("holidays", bt_sx.holiday == 1)]:
    s_ = bt_sx[mask]
    rows.append((name, len(s_), coverage(s_["actual"], s_["lo"], s_["hi"])))
print(pd.DataFrame(rows, columns=["slice", "forecast values", "coverage of the SARIMAX 80% interval"]).set_index("slice").round(3).to_string())
```
```text
                forecast values  coverage of the SARIMAX 80% interval
slice                                                                
ordinary days               402                                0.8110
promotion days               41                                0.7800
holidays                      5                                0.6000
```

Treat the holiday row with caution: it rests on only 5 forecast values, far too few to conclude anything. Always print the **count** next to a sliced score (ds.04 section 12.8).

### 10.6 Try it

1. Compute the empirical 95% interval for the best model and report its coverage on the later half. Which level of interval is hardest to calibrate, and why?
2. Add `promo` to the empirical interval calibration (separate quantiles for promotion and non-promotion days). Does coverage improve on promotion days?

## 11. Combining forecasts, drift and retraining

### 11.1 Combining forecasts

Averaging the forecasts of several models is one of the most reliable ideas in forecasting, **when the members are comparably good** and make partly independent errors. Then the average beats most of its members. A simple average is hard to beat; weights fitted on the backtest tend to chase noise.

```python run
members = ["SARIMAX + promo/holiday", "Holt-Winters (log, damped)", "GBM direct", "seasonal average (4w)"]
key = ["origin", "date", "horizon"]
base_frame = results[members[0]][key + ["actual"]].copy()
for mname in members:
    assert (results[mname][key].to_numpy() == base_frame[key].to_numpy()).all()
    base_frame[mname] = results[mname]["forecast"].to_numpy()
combo = {}
combo["average of 3 models"] = base_frame[members[:3]].mean(1)
combo["average of SARIMAX + GBM"] = base_frame[[members[0], members[2]]].mean(1)
combo["average of all 4"] = base_frame[members].mean(1)
for name, f in combo.items():
    results[name] = base_frame[key + ["actual"]].assign(forecast=f.to_numpy())
print(summarise(results).round(3).sort_values("MAE").head(8).to_string())
verdict("average of 3 models", results["average of 3 models"], results["seasonal naive"])
verdict("average of 3 models", results["average of 3 models"], results["SARIMAX + promo/holiday"], "best single model")
```
```text
                               MAE    RMSE   MASE  sMAPE    bias  skill vs seasonal naive
model                                                                                    
average of SARIMAX + GBM   15.7990 19.9300 0.6980 0.0530  2.5030                   0.4940
SARIMAX + promo/holiday    16.2990 20.4590 0.7200 0.0550  1.3870                   0.4780
GBM direct                 16.6480 21.3720 0.7360 0.0550  3.6200                   0.4670
average of 3 models        16.9040 21.3790 0.7470 0.0560  1.6820                   0.4590
GBM recursive              17.2860 21.5580 0.7640 0.0580 -0.3820                   0.4470
average of all 4           18.5320 23.8180 0.8190 0.0610  1.5660                   0.4070
GBM direct, raw target     20.4240 26.6470 0.9030 0.0680 -4.3520                   0.3460
Holt-Winters (log, damped) 22.7280 31.5320 1.0040 0.0740  0.0380                   0.2730
average of 3 models        skill vs seasonal naive: +0.459  95% interval [+0.395, +0.518]  -> BEATS seasonal naive
average of 3 models        skill vs best single model: -0.037  95% interval [-0.099, +0.022]  -> is not distinguishable from best single model
```

The table says two things. The average of the **two strong models** (SARIMAX and GBM) is the best forecast of all, with lower error than either alone. But adding weaker members makes it **worse**: the average of three or four is no better than the best single model, and the average of all four is clearly worse. Combination is not magic: averaging in a poor forecaster averages in its errors. Combine models that are each competitive on the backtest.

### 11.2 Drift: when the world changes under the model

Our series slows its growth after day 1,100. A model that assumed the old growth will be biased from then on. A backtest reveals this if you look at **error over time**, not just the average.

```python run
def mae_by_period(bt, edges):
    d = bt.assign(period=pd.cut(bt["date"], edges, labels=False), ae=(bt["actual"] - bt["forecast"]).abs(), e=bt["forecast"] - bt["actual"])
    return d.groupby("period").agg(MAE=("ae", "mean"), bias=("e", "mean"))
edges = [y.index[999], y.index[1099], y.index[1279], y.index[1460]]
print("period 0 = days 1000-1099 (before the slowdown), 1 = 1100-1279, 2 = 1280-1460")
tab = {n: mae_by_period(results[n], edges) for n in ["seasonal average (4w)", "Holt-Winters (log, damped)", "SARIMAX + promo/holiday", "GBM direct"]}
print(pd.concat(tab, axis=1).round(2).to_string())
```
```text
period 0 = days 1000-1099 (before the slowdown), 1 = 1100-1279, 2 = 1280-1460
       seasonal average (4w)          Holt-Winters (log, damped)         SARIMAX + promo/holiday         GBM direct       
                         MAE     bias                        MAE    bias                     MAE    bias        MAE   bias
period                                                                                                                    
0                    23.7600  12.0100                    20.1800  5.9000                 14.9200  7.4600    14.9900 3.8700
1                    26.0000 -12.4300                    22.6800 -6.2500                 16.1900 -6.8300    17.4500 3.4600
2                    28.4300   9.4200                    24.3000  3.2800                 17.2400  6.5700    16.7800 3.6400
```

Read the bias columns. The seasonal average and SARIMAX are **too high in period 0, too low in period 1 and too high again in period 2**: the bias swings with the time of year. That is not the slowdown; it is the **yearly cycle**, which these models (built on a weekly pattern) do not represent, so they under-forecast when the year is climbing and over-forecast when it is falling. The GBM has day-of-year features and its bias stays steady (about +3.5 in every period). Error by period is a diagnostic for missing structure of every kind, not only for drift. (The slowdown itself, which makes trend-extrapolating models over-forecast, is mixed in with this effect; separating them is the second Try-it of this section.)

### 11.3 A tracking signal: monitoring a live forecast

In production, watch the forecast like a patient. The **tracking signal** is the cumulative forecast error divided by the mean absolute error so far. It stays near zero for an unbiased forecast and drifts away (beyond roughly ±4) when the forecast is persistently too high or too low.

```python run
def tracking_signal(actual, forecast):
    e = np.asarray(actual) - np.asarray(forecast)
    return np.cumsum(e) / (np.cumsum(np.abs(e)) / np.arange(1, len(e) + 1))

bt1 = results["Holt-Winters (log, damped)"].query("horizon == 1").reset_index(drop=True)
ts_ = tracking_signal(bt1["actual"], bt1["forecast"])
print("tracking signal of the 1-step Holt-Winters forecast, every 4th origin:")
print(pd.Series(ts_[::4], index=bt1["date"].iloc[::4].dt.date).round(2).to_string())
```
```text
tracking signal of the 1-step Holt-Winters forecast, every 4th origin:
date
2023-09-28    1.0000
2023-11-23   -0.9800
2024-01-18   -1.8400
2024-03-14   -1.2800
2024-05-09   -1.5400
2024-07-04   -4.9900
2024-08-29   -2.9300
2024-10-24   -5.0800
```

Here the signal is within normal limits for most of the history and then falls below −4 from July 2024 and stays there. The sign convention is `actual − forecast`, so a large negative value means the forecast is persistently **too high**: the damped trend keeps assuming growth after the slowdown. That is exactly the alarm a production monitor should raise, long before anyone studies the backtest.

### 11.4 Retraining policy

How often should a model be refit? Our backtest refits at every origin (every two weeks). Production choices:

| Policy | When |
|---|---|
| **On a schedule** (daily, weekly) | cheap models, steady data pipelines |
| **On a trigger** (tracking signal beyond a limit, coverage collapse, PSI alert from ds.04) | expensive models |
| **Sliding window** | the old data is actively misleading after a regime change |

Check the effect of the window on the backtest with the fast model:

```python run
rows = []
for window in [None, 540, 365, 240]:
    bt_w = backtest(y, f_hw, window=window, **PROTOCOL)
    rows.append(("expanding" if window is None else f"sliding {window} days", mae(bt_w["actual"], bt_w["forecast"]), bias(bt_w["actual"], bt_w["forecast"])))
print(pd.DataFrame(rows, columns=["Holt-Winters training window", "backtest MAE", "bias"]).set_index("Holt-Winters training window").round(2).to_string())
```
```text
                              backtest MAE    bias
Holt-Winters training window                      
expanding                          22.7300  0.0400
sliding 540 days                   22.8200  0.1000
sliding 365 days                   22.8400 -0.1600
sliding 240 days                   23.8700  1.2900
```

There is no gain from a sliding window here, and the shortest window (240 days) is clearly worse. A damped trend and an exponentially discounted level already forget the distant past on their own, and a short window only throws away data that the seasonal states need. A window helps models that cannot forget by themselves (global regressions, tree models, ARIMA with constant coefficients); the experiment tells you which kind of model you have.

### 11.5 Special cases worth knowing

- **Intermittent demand** (many zeros: spare parts, slow sellers): MAPE is undefined and ordinary smoothing over-forecasts; use **Croston's method** or its variants, and judge with MASE or a pinball loss.
- **Hierarchies** (product, store, region, total): forecasts at different levels should add up; reconcile them (bottom-up, top-down, or optimal reconciliation).
- **Hourly data** with several seasons (day and week): add Fourier terms or multiple-seasonal models (TBATS, MSTL).
- **Long horizons** beyond one or two seasons: the trend and the seasonal pattern dominate; damped trends and simple models usually win.

### 11.6 Try it

1. Combine only the two statistical models. Is the average better than the best of the two?
2. Compute the tracking signal for the GBM direct forecast. Does it alarm after the slowdown at day 1,100? Then add Fourier terms for the yearly cycle to SARIMAX (section 8.8) and redo the error-by-period table: does the seasonal swing in the bias disappear?


## 12. Project: sales forecasting with an honest backtest

### 12.1 The brief

A retailer wants a two-week-ahead sales forecast for each store and asks one question: **"Is your model better than just repeating last week?"** Your job is to build a small harness, `forecast_lab`, that answers that question honestly, for any store, and refuses to claim a win that the data do not support. The deliverables:

1. A **backtest harness** with rolling origins, expanding or sliding windows, known-future covariates, and a fixed protocol written into every report.
2. A set of **forecasters**: the baseline family (naive, seasonal naive, seasonal average, mean, drift) and at least two real models (Holt-Winters, SARIMAX; the GBM of section 9 is the first extension).
3. A **report** with MAE, MASE, bias, skill versus seasonal naive **with a 95% interval**, and a verdict that is one of *BEATS*, *not distinguishable from*, *LOSES TO*.
4. **Tests** that guard the failures of this chapter: look-ahead in the harness or in a forecaster, an unfair baseline, a verdict that over-claims, a non-reproducible result.
5. A **second store** (a different seed and length) to prove the harness is not tuned to one series.

### 12.2 The library

```python run
import pathlib, tempfile, subprocess, os
proj = pathlib.Path(tempfile.mkdtemp()) / "forecast_lab_project"
proj.mkdir()
(proj / "forecast_lab.py").write_text('''"""forecast_lab: a rolling-origin backtest harness that reports skill against seasonal naive with an error bar."""
import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

M = 7                                                    # season length (days)


# ---------- forecasters: f(y_train, h, X_tr=None, X_future=None) -> array of h numbers ----------
def mean_fc(y_train, h, X_tr=None, X_future=None):
    return np.full(h, y_train.mean())

def naive_fc(y_train, h, X_tr=None, X_future=None):
    return np.full(h, y_train.iloc[-1])

def snaive_fc(y_train, h, X_tr=None, X_future=None, m=M):
    last = y_train.to_numpy()[-m:]
    return np.array([last[k % m] for k in range(h)])

def savg_fc(y_train, h, X_tr=None, X_future=None, m=M, weeks=4):
    prof = y_train.to_numpy()[-m * weeks:].reshape(weeks, m).mean(0)
    return np.array([prof[k % m] for k in range(h)])

def drift_fc(y_train, h, X_tr=None, X_future=None):
    slope = (y_train.iloc[-1] - y_train.iloc[0]) / (len(y_train) - 1)
    return y_train.iloc[-1] + slope * np.arange(1, h + 1)

def hw_fc(y_train, h, X_tr=None, X_future=None):
    fit = ExponentialSmoothing(np.log(y_train), trend="add", damped_trend=True, seasonal="add", seasonal_periods=M,
                               initialization_method="estimated").fit()
    return np.exp(fit.forecast(h)).to_numpy()

def sarimax_fc(y_train, h, X_tr=None, X_future=None):
    fit = SARIMAX(np.log(y_train), exog=X_tr, order=(1, 1, 1), seasonal_order=(0, 1, 1, M)).fit(disp=False, maxiter=100)
    return np.exp(fit.forecast(h, exog=X_future)).to_numpy()

BASELINES = {"mean": mean_fc, "naive": naive_fc, "seasonal naive": snaive_fc, "drift": drift_fc, "seasonal average": savg_fc}


# ---------- the harness ----------
def backtest(y, forecaster, h=14, initial=500, step=14, window=None, X=None):
    """One row per (origin, step). Training data always end at the origin; X_future holds only the h target days."""
    rows = []
    for o in range(initial, len(y) - h + 1, step):
        lo = 0 if window is None else max(0, o - window)
        y_tr = y.iloc[lo:o]
        X_tr = None if X is None else X.iloc[lo:o]
        X_fu = None if X is None else X.iloc[o:o + h]
        fc = np.asarray(forecaster(y_tr, h, X_tr=X_tr, X_future=X_fu), dtype=float)
        if len(fc) != h:
            raise ValueError(f"forecaster returned {len(fc)} values, expected {h}")
        for k in range(h):
            rows.append((y.index[o - 1], y.index[o + k], k + 1, float(y.iloc[o + k]), fc[k]))
    return pd.DataFrame(rows, columns=["origin", "date", "horizon", "actual", "forecast"])


def mase_scale(y, initial, m=M):
    """In-sample seasonal-naive MAE, from the data BEFORE the first origin only."""
    v = y.to_numpy()[:initial]
    return float(np.mean(np.abs(v[m:] - v[:-m])))


def origin_errors(bt):
    return (bt["actual"] - bt["forecast"]).abs().groupby(bt["origin"]).mean()


def skill_ci(bt_model, bt_base, n_boot=2000, seed=0):
    em, eb = origin_errors(bt_model), origin_errors(bt_base)
    if not (em.index == eb.index).all():
        raise ValueError("models must be compared on identical origins")
    idx = np.random.default_rng(seed).integers(0, len(em), (n_boot, len(em)))
    boots = 1 - em.to_numpy()[idx].mean(1) / eb.to_numpy()[idx].mean(1)
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return float(1 - em.mean() / eb.mean()), float(lo), float(hi)


def verdict(bt_model, bt_base, base_name="seasonal naive"):
    point, lo, hi = skill_ci(bt_model, bt_base)
    word = "BEATS" if lo > 0 else ("LOSES TO" if hi < 0 else "not distinguishable from")
    return f"skill {point:+.3f} [{lo:+.3f}, {hi:+.3f}] -> {word} {base_name}"


def report(y, forecasters, base="seasonal naive", X=None, **protocol):
    """Run every forecaster on the same origins; return (table, verdicts, backtests)."""
    bts = {name: backtest(y, fn, X=X, **protocol) for name, fn in forecasters.items()}
    scale = mase_scale(y, protocol.get("initial", 500))
    rows = []
    for name, bt in bts.items():
        e = bt["actual"] - bt["forecast"]
        rows.append((name, e.abs().mean(), e.abs().mean() / scale, (bt["forecast"] - bt["actual"]).mean(), 1 - e.abs().mean() / (bts[base]["actual"] - bts[base]["forecast"]).abs().mean()))
    table = pd.DataFrame(rows, columns=["model", "MAE", "MASE", "bias", f"skill vs {base}"]).set_index("model")
    verdicts = {name: verdict(bt, bts[base], base) for name, bt in bts.items() if name != base}
    return table, verdicts, bts
''', encoding="utf-8")
print("forecast_lab.py:", len((proj / "forecast_lab.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
forecast_lab.py: 94 lines
```

### 12.3 The tests

Each test guards one failure. The most important is the **corruption test**: replace the data after some date with garbage and check that forecasts made *before* that date do not change. A forecaster that peeks at the future (through a scaler fitted on the whole series, say) changes its answer and the test catches it.

```python run
(proj / "test_forecast_lab.py").write_text('''import numpy as np, pandas as pd, pytest
import forecast_lab as fl

def make_series(n=420, seed=0):
    r = np.random.default_rng(seed)
    idx = pd.date_range("2022-01-01", periods=n, freq="D")
    weekly = np.array([0.85, 0.88, 0.92, 0.97, 1.12, 1.25, 1.01])
    y = (100 + 0.2 * np.arange(n)) * weekly[idx.dayofweek] * np.exp(r.normal(0, 0.05, n))
    return pd.Series(y, index=idx)

PROTOCOL = dict(h=14, initial=300, step=14)

def test_training_data_always_end_before_the_targets():
    y = make_series()
    seen = []
    def spy(y_train, h, X_tr=None, X_future=None):
        seen.append((y_train.index[-1], len(y_train)))
        return np.full(h, y_train.iloc[-1])
    bt = fl.backtest(y, spy, **PROTOCOL)
    for origin, first_target in zip(bt["origin"].unique(), bt.groupby("origin")["date"].min()):
        assert origin < first_target, "an origin must come strictly before its first target date"
    assert all(last == origin for (last, _), origin in zip(seen, bt["origin"].unique())), "the forecaster must see data only up to the origin"

def test_covariates_are_cut_at_the_origin():
    y = make_series()
    X = pd.DataFrame({"promo": np.arange(len(y)) % 5 == 0}, index=y.index).astype(float)
    def spy(y_train, h, X_tr=None, X_future=None):
        assert X_tr.index[-1] == y_train.index[-1], "training covariates must end at the origin"
        assert X_future.index[0] == y_train.index[-1] + pd.Timedelta(days=1) and len(X_future) == h, "future covariates must be exactly the h target days"
        return np.full(h, y_train.iloc[-1])
    fl.backtest(y, spy, X=X, **PROTOCOL)

def forecasts_at_origins(factory, y, upto):
    """Backtest origins that need only data before `upto`; the forecaster is BUILT from the series it is tested on."""
    bt = fl.backtest(y, factory(y), h=14, initial=300, step=14)
    return bt[bt["date"] < y.index[upto]]

def honest_factory(y):
    return fl.hw_fc

def leaky_factory(y):
    global_level = y.mean()                       # computed from the WHOLE series, including the future
    def fc(y_train, h, X_tr=None, X_future=None):
        return fl.snaive_fc(y_train, h) * (global_level / y_train.mean())
    return fc

def test_corruption_test_passes_for_honest_and_catches_the_leaky_forecaster():
    y = make_series()
    y_bad = y.copy()
    y_bad.iloc[360:] = 1e6                       # garbage after day 360
    for factory, should_leak in [(honest_factory, False), (leaky_factory, True)]:
        a = forecasts_at_origins(factory, y, 360)
        b = forecasts_at_origins(factory, y_bad, 360)
        changed = not np.allclose(a["forecast"], b["forecast"])
        assert changed == should_leak, f"{factory.__name__}: corrupting the future {'changed' if changed else 'did not change'} earlier forecasts"

def test_snaive_matches_a_hand_calculation():
    y = pd.Series(np.arange(1.0, 15.0), index=pd.date_range("2022-01-01", periods=14))
    assert list(fl.snaive_fc(y, 3)) == [8.0, 9.0, 10.0], "seasonal naive repeats the last 7 days: day 8, 9, 10 of the history"

def test_a_forecaster_has_zero_skill_against_itself():
    bt = fl.backtest(make_series(), fl.snaive_fc, **PROTOCOL)
    point, lo, hi = fl.skill_ci(bt, bt)
    assert point == 0 and lo == 0 and hi == 0

def test_noise_is_never_declared_a_winner():
    y = make_series()
    rng = np.random.default_rng(0)
    def noise(y_train, h, X_tr=None, X_future=None):
        return fl.snaive_fc(y_train, h) * np.exp(rng.normal(0, 0.3, h))
    v = fl.verdict(fl.backtest(y, noise, **PROTOCOL), fl.backtest(y, fl.snaive_fc, **PROTOCOL))
    assert "BEATS" not in v, "random perturbations of the baseline must not be reported as an improvement"

def test_a_real_model_beats_a_bad_baseline():
    y = make_series()
    v = fl.verdict(fl.backtest(y, fl.hw_fc, **PROTOCOL), fl.backtest(y, fl.mean_fc, **PROTOCOL), "mean")
    assert "BEATS" in v, "Holt-Winters should clearly beat the overall mean on a seasonal, trending series"

def test_mase_scale_uses_only_the_training_period():
    y = make_series()
    y_bad = y.copy(); y_bad.iloc[300:] = 1e6
    assert fl.mase_scale(y, 300) == fl.mase_scale(y_bad, 300), "the MASE scale must not depend on data after the first origin"

def test_the_report_is_reproducible():
    y = make_series()
    a = fl.report(y, {"seasonal naive": fl.snaive_fc, "seasonal average": fl.savg_fc}, **PROTOCOL)
    b = fl.report(y, {"seasonal naive": fl.snaive_fc, "seasonal average": fl.savg_fc}, **PROTOCOL)
    assert a[0].equals(b[0]) and a[1] == b[1]
''', encoding="utf-8")
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "test_forecast_lab.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-700:] or res.stderr.strip()[-700:])
```
```text
.........                                                                [100%]
9 passed in 4.58s
```

### 12.4 Use it on a store the chapter never saw

A second store: different seed, shorter history, different start date. Nothing in the harness was tuned to the first series.

```python run
sys.path.insert(0, str(proj))
import importlib, forecast_lab as fl
importlib.reload(fl)

store2 = make_demand(start="2022-03-01", n_days=900, seed=5)
y2, X2 = store2["sales"], store2[["promo", "holiday"]].astype(float)
protocol = dict(h=14, initial=550, step=14)
forecasters = {**fl.BASELINES, "Holt-Winters": fl.hw_fc, "SARIMAX + promo/holiday": fl.sarimax_fc}
t0 = time.perf_counter()
table, verdicts, bts = fl.report(y2, forecasters, X=X2, **protocol)
print(f"{bts['naive']['origin'].nunique()} origins, h={protocol['h']}, {bts['naive']['date'].min().date()} to {bts['naive']['date'].max().date()}, run in {time.perf_counter() - t0:.0f} s")
print(table.round(3).sort_values("MAE").to_string())
print()
for name, v in verdicts.items():
    print(f"{name:26s} {v}")
```
```text
25 origins, h=14, 2023-09-02 to 2024-08-16, run in 63 s
                            MAE   MASE     bias  skill vs seasonal naive
model                                                                   
SARIMAX + promo/holiday 15.6440 0.6500   0.1540                   0.4430
Holt-Winters            20.3310 0.8440  -0.0520                   0.2760
seasonal average        23.7640 0.9870  -1.8440                   0.1540
seasonal naive          28.0900 1.1660   0.1360                   0.0000
mean                    47.6240 1.9770 -30.6460                  -0.6950
naive                   50.0760 2.0790  29.6500                  -0.7830
drift                   50.9020 2.1130  31.1440                  -0.8120

mean                       skill -0.695 [-0.963, -0.446] -> LOSES TO seasonal naive
naive                      skill -0.783 [-1.123, -0.477] -> LOSES TO seasonal naive
drift                      skill -0.812 [-1.162, -0.500] -> LOSES TO seasonal naive
seasonal average           skill +0.154 [+0.065, +0.236] -> BEATS seasonal naive
Holt-Winters               skill +0.276 [+0.199, +0.347] -> BEATS seasonal naive
SARIMAX + promo/holiday    skill +0.443 [+0.373, +0.508] -> BEATS seasonal naive
```

### 12.5 The best simple baseline, not only the textbook one

The honest question is "does it beat the *best* simple forecaster?". The report above compared with seasonal naive; now compare the real models with the best baseline found.

```python run
best_baseline = table.loc[list(fl.BASELINES)].sort_values("MAE").index[0]
print("best baseline on this store:", best_baseline)
for name in ["Holt-Winters", "SARIMAX + promo/holiday"]:
    print(f"{name:26s} {fl.verdict(bts[name], bts[best_baseline], best_baseline)}")
```
```text
best baseline on this store: seasonal average
Holt-Winters               skill +0.144 [+0.067, +0.216] -> BEATS seasonal average
SARIMAX + promo/holiday    skill +0.342 [+0.260, +0.415] -> BEATS seasonal average
```

### 12.6 The audit trail

A result is only as good as its recorded protocol. The report writes everything someone needs to repeat it or to challenge it.

```python run
record = {
    "series": {"name": "store 2", "start": str(y2.index[0].date()), "end": str(y2.index[-1].date()), "n_days": len(y2)},
    "protocol": {**protocol, "window": "expanding", "refit": "every origin", "metric_scale": "seasonal-naive MAE on the first %d days" % protocol["initial"],
                 "origins": int(bts["naive"]["origin"].nunique()), "covariates": ["promo", "holiday"] },
    "results": {n: {"MAE": round(float(table.loc[n, "MAE"]), 2), "MASE": round(float(table.loc[n, "MASE"]), 3)} for n in table.index},
    "verdicts_vs_seasonal_naive": verdicts,
    "environment": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "statsmodels": statsmodels.__version__},
}
print(json.dumps(record, indent=1)[:1800], "...")
```
```text
{
 "series": {
  "name": "store 2",
  "start": "2022-03-01",
  "end": "2024-08-16",
  "n_days": 900
 },
 "protocol": {
  "h": 14,
  "initial": 550,
  "step": 14,
  "window": "expanding",
  "refit": "every origin",
  "metric_scale": "seasonal-naive MAE on the first 550 days",
  "origins": 25,
  "covariates": [
   "promo",
   "holiday"
  ]
 },
 "results": {
  "mean": {
   "MAE": 47.62,
   "MASE": 1.977
  },
  "naive": {
   "MAE": 50.08,
   "MASE": 2.079
  },
  "seasonal naive": {
   "MAE": 28.09,
   "MASE": 1.166
  },
  "drift": {
   "MAE": 50.9,
   "MASE": 2.113
  },
  "seasonal average": {
   "MAE": 23.76,
   "MASE": 0.987
  },
  "Holt-Winters": {
   "MAE": 20.33,
   "MASE": 0.844
  },
  "SARIMAX + promo/holiday": {
   "MAE": 15.64,
   "MASE": 0.65
  }
 },
 "verdicts_vs_seasonal_naive": {
  "mean": "skill -0.695 [-0.963, -0.446] -> LOSES TO seasonal naive",
  "naive": "skill -0.783 [-1.123, -0.477] -> LOSES TO seasonal naive",
  "drift": "skill -0.812 [-1.162, -0.500] -> LOSES TO seasonal naive",
  "seasonal average": "skill +0.154 [+0.065, +0.236] -> BEATS seasonal naive",
  "Holt-Winters": "skill +0.276 [+0.199, +0.347] -> BEATS seasonal naive",
  "SARIMAX + promo/holiday": "skill +0.443 [+0.373, +0.508] -> BEATS seasonal naive"
 },
 "environment": {
  "python": "3.14.4",
  "numpy": "2.5.4",
  "pandas": "3.1.1",
  "statsmodels": "0.15.0"
 }
} ...
```

### 12.7 What to hand in

1. `forecast_lab.py` and `test_forecast_lab.py`, all tests passing.
2. The report for **two or more** series, with the full protocol.
3. A paragraph per model: where it wins, where it loses (by horizon, by origin, by promotion/holiday), and whether it beats the *best* baseline.
4. One deliberately **leaky forecaster** of your own, the corruption test failing for it, and the fix.
5. A recommendation for the retailer in plain words: use the model, or use the baseline, and why. A "not distinguishable" verdict means "use the simple one".

### 12.8 Extensions

1. Port the **direct GBM** of section 9 into `forecast_lab` and extend `report` with the horizon table of section 5.5.
2. Add prediction intervals to the report (empirical or quantile, section 10) and a coverage column.
3. Add a **forecast-combination** forecaster (the average of two others) and a test that its backtest rows align with its members.
4. Add a **sliding window** option to the report and a regime-change test series (growth that stops half-way). Which models cope?
5. Run the report over twenty generated stores and summarise how often each model beats the best baseline. What would you tell a retailer with a thousand stores?

## 13. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Random train/test split or random CV | interpolation; far too optimistic | rolling-origin backtest only (5, ds.04) |
| One test window | a noisy, calendar-dependent number | many origins; report the spread and the worst cases (5.4, 5.5) |
| Comparing with a weak baseline | "beats the mean" proves little | compare with the best simple forecaster, not only seasonal naive (4.1, 7.4, 12.5) |
| Copying last week's promotion spike (plain seasonal naive) | baseline looks worse than it should | also try the seasonal average and mean (4.1) |
| MAPE on small or zero values | infinite or misleading errors; rewards low forecasts | MAE, MASE, bias (4.2, 4.3) |
| Reporting skill without an interval | luck mistaken for improvement | paired bootstrap over whole origins (5.6) |
| Overlapping test windows treated as independent | an interval that is too narrow | `step >= h`, resample origins (5.6, 5.9) |
| Centred rolling windows, `shift(-1)`, un-shifted rolling stats | the future leaks into the features | `shift(1)` first; truncation test (6.2) |
| Statistics computed on the whole series | a quiet look-ahead | fit scalers and profiles inside each origin (6.1) |
| Training with actual covariates, deploying with forecasts of them | the model trusts a signal it will not get | backtest with the covariates as known at each origin (6.4) |
| Using a lag that is too new for the horizon | the feature does not exist at forecast time | lags at least `ceil(k)` old; direct tables (9.1, 9.3) |
| Recursive forecasts over long horizons | compounding errors | direct strategy, or measure error by horizon (9.5) |
| Tree models on a trending target | flat forecasts, strong negative bias | predict relative to the level; difference (9.6) |
| Choosing ARIMA orders by AIC alone | an adequate-looking model that forecasts badly | residual tests, then the backtest decides (8.4) |
| Ignoring known-in-advance information | promotions and holidays left as noise | regressors (SARIMAX) or features (GBM) (8, 9) |
| Intervals taken at face value | overconfident ranges | measure coverage on the backtest; recalibrate (10) |
| Judging only the average error | a failing period or segment hidden | error by horizon, period and slice (5.5, 10.5, 11.2) |
| Never retraining, or retraining on a fixed habit | drift unnoticed | tracking signal, scheduled refits, window tests (11.3, 11.4) |
| Tuning on the backtest and reporting it | optimism from selection | a final period untouched by any choice (5.8) |

## 14. Summary

- A time series has **one history in a fixed order**. Neighbouring values are correlated, so random splits interpolate, and every honest procedure respects "at the origin, only the past is known".
- **Components**: trend, seasonality (fixed period), cycles, calendar effects and noise. Additive when the swing is constant, multiplicative when it scales with the level; take logs to make it additive. Decompose (classical or STL) to *see* the structure; a flexible trend can swallow a slow seasonal cycle.
- **Autocorrelation and stationarity**: the ACF/PACF show memory; differencing and logs remove trend and seasonality; the ADF test helps decide, together with the plots.
- **Baselines first**: mean, naive, seasonal naive, drift, seasonal average. The obvious baseline is not always the best simple one. **Metrics**: MAE and RMSE in the series' units, **MASE** (scaled by the in-sample seasonal-naive error) across series, bias always; avoid MAPE on small values. The summary number is **skill** against the baseline.
- **Backtest with rolling origins**: many origins, a stated horizon, expanding or sliding windows, refit at each origin, identical origins for all models, `step >= h`. Report error by horizon and the worst origins. **Show whether a forecast beats seasonal naive** with skill and a bootstrap interval over whole origins: one of *beats*, *not distinguishable*, *loses to*.
- **Leakage**: centred windows, un-shifted rolling statistics, whole-series statistics, random CV, actual-versus-forecast covariates, revised data, tuning on the backtest. Guard with the **truncation test** and the **corrupt-the-future test**.
- **Exponential smoothing** (level, trend, seasonal states; `alpha` is a memory length) and **SARIMAX** (differencing, AR and MA terms, seasonal terms, regressors) are the classical workhorses; AIC and Ljung-Box guide, the backtest decides.
- **Gradient boosting** needs a leak-free table: lags old enough for the horizon, calendar and known-future features, a **target relative to the level** (trees cannot extrapolate trends), and a **direct** or **recursive** multi-step strategy. Global models serve many series.
- **Intervals**: coverage and width (and the pinball loss for quantiles); model-based, empirical-from-backtest and quantile-boosting intervals; calibrate and slice them like probabilities (ds.04).
- **Combine forecasts** by simple averaging; **monitor drift** with error over time and a tracking signal; choose a **retraining** policy; know the special cases (intermittent demand, hierarchies, multiple seasons).

You reached the outcome of this chapter: you can **backtest a forecast and show whether it beats seasonal naive**, with an interval, on the horizon the business needs, and the project turned that into a harness with tests that refuses to over-claim. Next, ds.08 covers other kinds of special data: text features (bag of words, TF-IDF) and the basics of recommender systems.
