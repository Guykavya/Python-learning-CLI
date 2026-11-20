# Problem plan: ds.07 Time-series forecasting (35 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.07.p001` … `p035`, folder `pNNN-slug`. Requires ds.04. Libraries: NumPy, pandas,
SciPy, scikit-learn, statsmodels. **Prophet, pmdarima, sktime, LightGBM are not installed.**

**Mix:** 12 drill, 12 applied, 8 deep, 3 challenge. **Kinds:** 24 code, 7 trace, 4 explain.
**assessment:** explain = p015, trace = p010, fix = p019, build = p035.
**★ core set (write first, 14):** 1, 4, 7, 9, 10, 12, 13, 15, 16, 19, 22, 26, 30, 35. The outcome (backtest and show whether it
beats seasonal naive) is p12–p17 and p35.

**Testing notes**
- Forecaster signature from the chapter: `f(y_train, h, X_tr=None, X_future=None) -> np.ndarray of length h`; `backtest(y, forecaster,
  h, initial, step, window, X)` returns a long DataFrame (origin, horizon, date, actual, forecast). Problems reuse these names.
- Data: `make_demand(start, n_days, seed)` (§2.1: daily sales, weekly + yearly seasonality, promos, holidays) in `conftest.py`, usually
  with `n_days=730`; tiny inline series (≤ 14 values) for hand-checked answers.
- **Spike results (2026-11-18, under the 1 GiB cap):** statsmodels tsa import 1.1 s; Holt-Winters (m = 7, n = 1,000) 0.23 s per fit;
  `SARIMAX((1,0,1),(0,1,1,7))` on 1,000 days ≈ 1.0 s per fit; ARIMA(1,1,1) 0.05 s. **`SARIMAX` with a seasonal period of 52 failed with
  a MemoryError** (state dimension 105). Rules: seasonal periods ≤ 12 in tests; SARIMAX backtests ≤ 5 origins, Holt-Winters ≤ 15,
  from-scratch models as many as needed.
- Most model problems are **from scratch** (SES, Holt, seasonal naive, drift, direct GBM features) and are compared with statsmodels
  at a fixed `alpha` (`ExponentialSmoothing(...).fit(smoothing_level=a, optimized=False)`), which is deterministic (R3).
- Leakage is checked with the chapter's `assert_no_lookahead(make_features, series, cuts)`: features at time t must not change when the
  series after t is altered. The tests apply it to the learner's feature function.
- `HistGradientBoostingRegressor(max_iter=100)` stands in for LightGBM.

## A. What is different, and the components (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Future index for a horizon | drill | code | `future_index(y_train, h)` returns the next h daily dates after the last training date; works across a month/year boundary |
| 2 | Additive decomposition by moving averages | applied | code | `decompose(y, m)` (centred MA trend, seasonal means of the detrended series centred to sum 0, remainder); matches `seasonal_decompose(model="additive", period=m)` where both are defined |
| 3 | Trend and seasonality strength | deep | code | `strength(component, remainder)` = `max(0, 1 − var(R)/var(C+R))`; strong weekly season in `make_demand` > 0.6; white noise ≈ 0 |
| 4 | Autocorrelation by hand | drill | code | `acf(y, nlags)`; equals `statsmodels.tsa.stattools.acf(y, nlags, fft=False)`; lag 7 peak on weekly data |
| 5 | Read the ACF | drill | trace | `⚠ HAND-TRACE` ACF values of 4 inline series printed by given code (rounded): label each white noise / trend / weekly / random walk using the given rule |
| 6 | Why shuffled CV fails on time series | deep | explain | autocorrelation lets a random fold "see" its neighbours; why rolling origins are needed; checklist: "neighbours leak", "future in training", "rolling origin" |

## B. Baselines and metrics (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 7 | The six baselines | drill | code | `f_mean`, `f_naive`, `f_snaive`, `f_drift`, `f_savg`, `f_snaive_drift` on a 14-value inline series; exact hand values |
| 8 | Forecast errors | drill | code | `mae`, `rmse`, `mape` (raises on zero actuals), `smape`, `bias`; inline exact values |
| 9 | MASE | applied | code | `mase(y_true, y_pred, y_train, m)` scaled by in-sample seasonal-naive MAE; seasonal naive on its own train has MASE 1 in-sample |
| 10 | Trace the baselines | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` a 10-day series and h = 3: print the naive, seasonal-naive (m = 7) and drift forecasts |
| 11 | When percentage errors lie | deep | trace | `⚠ HAND-TRACE` two forecasts on a series with a day of 1 sale: print MAPE and sMAPE for each; MAPE prefers the worse forecast |

## C. Backtesting (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 12 | Rolling origins | drill | code | `origins(n, initial, step, h)` returns the cut points; the last forecast ends within the series; no origin before `initial` |
| 13 | A general backtest | applied | code | `backtest(y, forecaster, h, initial, step, window)`; long-format result; each forecast only saw data before its origin (the test passes a spy forecaster that records `y_train.index[-1]`) |
| 14 | Error by horizon | applied | code | `by_horizon(results, names)`; for naive, error grows with horizon on a random walk |
| 15 | Explain a backtest result | deep | explain | `assessment = "explain"`; from a printed `summarise` table and `skill_ci` (in `problem.md`), explain whether the model beats seasonal naive, how sure we are, and what the expanding vs sliding window choice changes; checklist |
| 16 | Skill score with an error bar | applied | code | `skill_ci(bt_model, bt_base, n_boot, seed)` resamples **origins** (not days); returns skill and 95% CI; a copy of the baseline has skill 0 with a CI around 0 |
| 17 | The verdict | applied | code | `verdict(name, bt_model, bt_base)` returns `"beats"`, `"no better"` or `"worse"` from the CI; three constructed cases |

## D. Future-data leakage (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | The truncation test | applied | code | `assert_no_lookahead(make_features, series, cuts)` raises `AssertionError` naming the column and cut when a feature changes after truncation; passes `good_features`, catches `leaky_features` |
| 19 | Fix the leaky feature table | applied | code | `assessment = "fix"`; given `make_features` with a centred rolling mean, `shift(-1)` and a full-series standardisation; tests: truncation test passes, holdout MAE becomes honest (worse than the leaky one, within a band) |
| 20 | Known-future or unknown-future? | drill | trace | `⚠ HAND-TRACE` given 8 covariates (promo calendar, holiday, temperature, yesterday's sales …), print which ones a given rule allows at forecast time |

## E. Exponential smoothing and ARIMA (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 21 | Simple exponential smoothing | drill | code | `ses_fit(y, alpha, level0)` returns levels and the flat forecast; equals statsmodels `SimpleExpSmoothing(...).fit(smoothing_level=alpha, optimized=False)` with the same initial level |
| 22 | Alpha is a memory length | drill | trace | `⚠ HAND-TRACE` SES on 5 values with alpha 0.5, level0 = first value: print each level |
| 23 | Holt-Winters by hand | deep | code | `holt_winters_additive(y, alpha, beta, gamma, m, init)` recursions; matches statsmodels `ExponentialSmoothing(..., initialization_method="known")` with the same initial states within 1e-8 |
| 24 | Backtest Holt-Winters | applied | code | `f_hw` (§7.4, log scale, damped) in `backtest` with ≤ 10 origins on 730 days; beats naive; result compared with seasonal naive |
| 25 | AR(1) from scratch | applied | code | `fit_ar1(y)` by least squares (`y_t = c + φ y_{t−1}`); φ within 0.05 of the true 0.7; forecast decays towards the mean |
| 26 | Choose an ARIMA order by AIC | deep | code | `best_order(y, candidates)` fits each `ARIMA` and returns the lowest AIC; on a simulated AR(2) the answer has p = 2 (≤ 6 candidates, monthly-size series) |

## F. Machine learning for forecasting (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Turning a series into a table | applied | code | `lag_table(y, lags, rolls)` with only past values (truncation test passes); rows with incomplete lags dropped |
| 28 | Direct strategy | deep | code | `direct_forecast(y, h, make_model)` fits one model per horizon k on target `y[t+k]`; length h; each model trained only on data before the origin |
| 29 | Recursive compounding | deep | trace | `⚠ HAND-TRACE` a recursive AR rule `ŷ_{t+1} = 0.5·y_t + 10` from y = 40: print 4 forecasts, showing how errors would compound |
| 30 | Predict the change, not the level | challenge | code | `f_gbm_relative(y_train, h, ...)` predicts `y / rolling level`; on a trending series it beats the raw-level GBM in a ≤ 6-origin backtest (trees cannot extrapolate) |

## G. Intervals, combining, drift (Ch. 10–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 31 | Pinball loss and coverage | drill | trace | `⚠ HAND-TRACE` given `pinball(y, q, tau)` and `coverage(y, lo, hi)`, print the pinball loss of a 0.1- and a 0.9-quantile forecast on 4 inline values, and the coverage of an inline interval
| 32 | Empirical intervals from past errors | challenge | code | `empirical_interval(bt_cal, bt_new, level)` adds per-horizon error quantiles; coverage on new origins within 0.07 of the level |
| 33 | Combining forecasts | applied | explain | why the simple average of seasonal naive and Holt-Winters often beats both (errors partly cancel), when it does not (one forecast much worse, errors correlated), and why fitted weights overfit with few origins; uses a printed backtest table; checklist
| 34 | Tracking signal | drill | explain | what a tracking signal beyond ±4 means and how the retraining policy reacts (§11.3–11.4); uses printed values; checklist |

## H. Project (Ch. 12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Sales forecasting with an honest backtest | challenge | code | `assessment = "build"`; `forecast_study(y, X)` returns the backtest summary (baselines + one model of the learner's choice), skill vs seasonal naive with CI, and the verdict; tests: no look-ahead (spy forecaster), origins correct, seasonal naive included, verdict consistent with the CI; on `make_demand(n_days=730, seed=…)` for 2 seeds |

## Counts check

Tiers: drill 12 (1, 4, 5, 7, 8, 10, 12, 20, 21, 22, 31, 34), applied 12 (2, 9, 13, 14, 16, 17, 18, 19, 24, 25, 27, 33),
deep 8 (3, 6, 11, 15, 23, 26, 28, 29), challenge 3 (30, 32, 35).
Kinds: trace 7 (5, 10, 11, 20, 22, 29, 31), explain 4 (6, 15, 33, 34), code 24.
Assessment: explain p015, trace p010, fix p019, build p035 — exactly one each.

## Risks and open questions

- Holt-Winters initial states: statsmodels' `initialization_method="known"` needs `initial_level`, `initial_trend`, `initial_seasonal`;
  p023's `problem.md` must give them and the exact recursion convention (the chapter's §7.2).
- Never use `seasonal_periods=365` or `SARIMAX` with m > 12 in tests (MemoryError under the cap; see spike).
- `make_demand(n_days=1461)` makes slower tests; use 730 unless yearly seasonality is the point.
