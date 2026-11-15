# Chapter 5 (DS): scikit-learn in depth

In ds.04 you learned that the evaluation can fail in quiet ways, and that the cure for the commonest one (preprocessing before splitting) is to put every fitted step inside a **pipeline**. This chapter teaches the tool properly. scikit-learn is the library that nearly every tabular machine-learning project in Python is built on, and its real strength is not any single algorithm. It is a **design**: one small set of rules (the *estimator API*) that every object follows, so that a scaler, an imputer, an encoder, a model and a whole chain of them can be fitted, cross-validated, tuned, saved and served in the same way.

Once you understand the design, scikit-learn stops being a list of classes to memorise and becomes a language. You will build **one object that goes from a raw table to predictions**, which is the outcome of this chapter. You will learn the estimator API and write your own transformer, use `Pipeline` and `ColumnTransformer` for mixed columns (numbers, categories, missing values, text), engineer features and *measure* whether each one helps, compare and tune models without fooling yourself (grid, random and successive-halving search, nested cross-validation), choose thresholds with the tools built for it, inspect a fitted model, and save and serve it. The project builds a small reusable library, `tabml`, that you can point at any tabular dataset.

Prerequisites: ds.04 (leakage, splits, thresholds, calibration, reproducibility) and ds.03 (cross-validation, metrics). The algorithms themselves (trees, forests, boosting, SVMs) are the subject of ds.06; here we treat them as interchangeable boxes that obey the API.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, pandas, SciPy and scikit-learn only. The data are **synthetic and seeded**: a used-car listings table with a known price rule, so we can check what a pipeline recovers. Every output block was produced by running the code above it, in one session from top to bottom. Timings and file sizes are machine-specific.

```python run
import sys, math, time, json, warnings, pathlib, tempfile, platform
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy import stats
from sklearn import (base, compose, dummy, ensemble, feature_extraction, feature_selection, impute, inspection,
                     linear_model, metrics, model_selection, pipeline, preprocessing, tree, utils)

np.set_printoptions(precision=4, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
warnings.filterwarnings("ignore")
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__)
print("pandas ", pd.__version__)
print("scipy  ", scipy.__version__)
print("sklearn", sklearn.__version__)
```
```text
python  3.14.4
numpy   2.5.4
pandas  3.1.1
scipy   1.18.1
sklearn 1.9.1
```

## Table of contents

1. [The estimator API: one design for everything](#1-the-estimator-api-one-design-for-everything)
2. [The running dataset: used-car listings](#2-the-running-dataset-used-car-listings)
3. [Transformers: scaling, imputing, encoding](#3-transformers-scaling-imputing-encoding)
4. [Pipeline: a chain that behaves like one model](#4-pipeline-a-chain-that-behaves-like-one-model)
5. [ColumnTransformer: different columns, different treatment](#5-columntransformer-different-columns-different-treatment)
6. [Writing your own estimator](#6-writing-your-own-estimator)
7. [Feature engineering, measured](#7-feature-engineering-measured)
8. [Model selection: comparing models fairly](#8-model-selection-comparing-models-fairly)
9. [Hyperparameter tuning](#9-hyperparameter-tuning)
10. [Targets, thresholds and calibration inside the API](#10-targets-thresholds-and-calibration-inside-the-api)
11. [Inspecting a fitted pipeline](#11-inspecting-a-fitted-pipeline)
12. [Saving, loading and serving](#12-saving-loading-and-serving)
13. [Debugging pipelines](#13-debugging-pipelines)
14. [Project: `tabml`, a reusable pipeline for tabular data](#14-project-tabml-a-reusable-pipeline-for-tabular-data)
15. [Common traps](#15-common-traps)
16. [Summary](#16-summary)

## 1. The estimator API: one design for everything

### 1.1 Why a design matters

Imagine every model had its own way of being used: `ridge.train(X, y)`, `forest.learn(data)`, `scaler.compute_statistics(X)`. Swapping one model for another would mean rewriting your code, and chaining steps would be a mess. scikit-learn avoids this with a handful of **conventions**. If you learn them once you can use any of the hundreds of classes in the library, and any library that copies the conventions (XGBoost, LightGBM and many others do).

### 1.2 The four kinds of object

| Kind | Key methods | Example | What it does |
|---|---|---|---|
| **Estimator** | `fit(X, y=None)` | anything below | learns something from data |
| **Transformer** | `fit`, `transform`, `fit_transform` | `StandardScaler`, `SimpleImputer` | turns X into a new X |
| **Predictor** | `fit`, `predict` (and `score`) | `LinearRegression`, `RandomForestClassifier` | turns X into predictions |
| **Meta-estimator** | wraps other estimators | `Pipeline`, `GridSearchCV`, `ColumnTransformer` | combines or tunes estimators |

Classifiers also have `predict_proba` (probabilities) and often `decision_function` (a raw score). Every estimator has `get_params()` and `set_params()`, and `sklearn.base.clone(est)` makes a fresh unfitted copy.

### 1.3 The rules

Here are the conventions, shown on a scaler. Watch each rule appear.

```python run
sc = preprocessing.StandardScaler()                       # Rule 1: hyperparameters are set in __init__, nothing is learned yet
print("before fit  has mean_ ?", hasattr(sc, "mean_"))
out = sc.fit(np.array([[1.0], [2.0], [3.0], [4.0]]))     # Rule 2: fit learns and RETURNS self
print("fit returns self:", out is sc)
print("after fit   mean_ =", sc.mean_, "| scale_ =", sc.scale_.round(4))   # Rule 3: learned values end in an underscore
print("transform   ->", sc.transform(np.array([[2.5], [10.0]])).ravel().round(4))   # Rule 4: transform APPLIES what was learned
print("get_params  ->", sc.get_params())
print("clone is unfitted:", not hasattr(base.clone(sc), "mean_"))
```
```text
before fit  has mean_ ? False
fit returns self: True
after fit   mean_ = [2.5] | scale_ = [1.118]
transform   -> [0.     6.7082]
get_params  -> {'copy': True, 'with_mean': True, 'with_std': True}
clone is unfitted: True
```

1. **Hyperparameters** (your choices) are constructor arguments, stored unchanged: `StandardScaler(with_std=True)`.
2. **`fit`** learns from data and returns `self`. That is why you can chain `Scaler().fit(X).transform(X)`.
3. **Learned values** end with an underscore: `mean_`, `coef_`, `classes_`. The trailing underscore is how you tell "I chose it" from "it was learned".
4. **`transform` and `predict` never learn.** They only apply what `fit` stored. This is the rule that makes pipelines leak-free: call `fit` on training data, then `transform` the rest.
5. **`X` is 2-D**: rows are samples, columns are features. `y` is 1-D. A single sample is a 1-row table, never a bare list.
6. **Input names**: when you fit on a DataFrame, the estimator remembers `feature_names_in_` and `n_features_in_` and checks them later (ds.04 section 14.2 showed why this matters).

### 1.4 `fit_transform` and why it exists

`fit_transform(X)` is `fit(X).transform(X)`, sometimes faster. Use it **only on training data**. For validation or test data call `transform`.

```python run
rng = np.random.default_rng(0)
Xtr = rng.normal(50, 10, (200, 1))
Xte = rng.normal(55, 10, (100, 1))                       # a slightly different group, as real test data often is
good = preprocessing.StandardScaler().fit(Xtr)
bad = preprocessing.StandardScaler().fit(Xte)             # WRONG: re-fitting on the test data
print("test mean after correct transform:", round(float(good.transform(Xte).mean()), 3), "(honestly not 0: the test group is shifted)")
print("test mean after re-fitted scaler :", round(float(bad.transform(Xte).mean()), 3), "(hides the shift)")
```
```text
test mean after correct transform: 0.361 (honestly not 0: the test group is shifted)
test mean after re-fitted scaler : -0.0 (hides the shift)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one picture of two bell curves on a shared x axis. Training data: 200 values, mean 50, spread 10. Test data: 100 values, mean 55, spread 10. Show a StandardScaler fitted on the training data: the test curve lands centred at about +0.36 after scaling, so the shift stays visible. Then show a scaler wrongly re-fitted on the test data: the test curve is forced to centre 0, hiding the shift. Label both outcomes."

### 1.5 `get_params`, `set_params` and the double underscore

Meta-estimators reach into their parts with a double underscore: `pipeline__step__param`. You will use this constantly when tuning (section 9).

```python run
est = pipeline.Pipeline([("scale", preprocessing.StandardScaler()), ("model", linear_model.Ridge(alpha=1.0))])
print(sorted(k for k in est.get_params() if "__" in k))
est.set_params(model__alpha=10.0)
print("alpha is now", est.get_params()["model__alpha"])
```
```text
['model__alpha', 'model__copy_X', 'model__fit_intercept', 'model__max_iter', 'model__positive', 'model__random_state', 'model__solver', 'model__tol', 'scale__copy', 'scale__with_mean', 'scale__with_std']
alpha is now 10.0
```

### 1.6 The three ways to feed data

| Input | Works? | Note |
|---|---|---|
| NumPy array | yes | no column names; you must track order yourself |
| pandas DataFrame | yes | names are remembered and checked; **preferred** |
| SciPy sparse matrix | yes (most estimators) | big one-hot or text matrices |

Many transformers return NumPy by default. `set_output(transform="pandas")` makes them return DataFrames with column names, which is far easier to inspect.

```python run
demo = pd.DataFrame({"a": [1.0, 2.0, 3.0], "b": [10.0, 20.0, 30.0]})
print(type(preprocessing.StandardScaler().fit_transform(demo)).__name__)
print(type(preprocessing.StandardScaler().set_output(transform="pandas").fit_transform(demo)).__name__)
print(preprocessing.StandardScaler().set_output(transform="pandas").fit_transform(demo).round(3).to_string())
```
```text
ndarray
DataFrame
        a       b
0 -1.2250 -1.2250
1  0.0000  0.0000
2  1.2250  1.2250
```

### 1.7 Try it

1. Write `sc2 = preprocessing.StandardScaler(); sc2.transform(np.array([[1.0]]))` and read the error. Which rule does it protect?
2. Fit a scaler on a DataFrame, then call `transform` with the columns in a different order. What happens, and which attribute made it possible to detect?

## 2. The running dataset: used-car listings

### 2.1 Why this dataset

Real tabular data are messy in a standard way: numbers on different scales, categories with few and many levels, missing values (some random, some meaningful), dates, and free text. We generate one table with all of these. The target `price_lakh` (price in lakh rupees) follows a hidden rule with an age penalty, a mileage penalty, brand and model effects, and a text effect (cars described as having an accident history sell for less). A second target, `sold_30d`, says whether the car sold within 30 days (more likely when the asking price is below the fair price).

```python run
def make_listings(n=4000, seed=0):
    r = np.random.default_rng(seed)
    brands = {"Maruti": 6.0, "Hyundai": 8.0, "Honda": 9.5, "Toyota": 14.0, "Tata": 7.0, "BMW": 38.0}
    model_effect = {(b, k): float(np.exp(r.normal(0, 0.22))) for b in brands for k in range(6)}   # 36 car models
    brand = r.choice(list(brands), n, p=[.28, .22, .14, .14, .14, .08])
    model_no = r.integers(0, 6, n)
    model = np.array([f"{b[:3].upper()}-{k}" for b, k in zip(brand, model_no)])
    year = r.integers(2008, 2024, n)
    age = 2024 - year
    mileage = np.clip(age * r.normal(11000, 3500, n) + r.normal(2000, 1500, n), 500, None).round(-2)
    fuel = r.choice(["petrol", "diesel", "hybrid", "electric"], n, p=[.50, .36, .08, .06])
    trans = r.choice(["manual", "automatic"], n, p=[.62, .38])
    engine = np.where(fuel == "electric", np.nan, r.choice([800, 1000, 1200, 1500, 2000, 2500], n)).astype(float)
    owners = np.clip(r.poisson(0.6 + 0.12 * age, n) + 1, 1, 5)
    city = r.choice(["Delhi", "Mumbai", "Pune", "Bengaluru", "Chennai", "Jaipur", "Lucknow", "Indore"], n)
    day = r.integers(0, 540, n)
    listed_on = (pd.Timestamp("2023-01-01") + pd.to_timedelta(day, unit="D")).strftime("%Y-%m-%d")
    accident = r.random(n) < 0.14
    service = r.random(n) < 0.45
    desc = np.array([" ".join(filter(None, [
        "accident history repaired" if a else "no accident", "full service record" if s else "", "single owner" if o == 1 else "",
        r.choice(["good condition", "minor scratches", "new tyres", "AC works well", "like new", ""])]))
        for a, s, o in zip(accident, service, owners)])
    base_price = np.array([brands[b] for b in brand]) * np.array([model_effect[(b, k)] for b, k in zip(brand, model_no)])
    fuel_f = pd.Series(fuel).map({"petrol": 1.0, "diesel": 1.07, "hybrid": 1.25, "electric": 1.45}).to_numpy()
    price = (base_price * np.exp(-0.085 * age - 0.0000022 * mileage) * fuel_f * np.where(trans == "automatic", 1.08, 1.0)
             * 0.96 ** (owners - 1) * np.where(accident, 0.88, 1.0) * np.where(service, 1.04, 1.0) * np.exp(r.normal(0, 0.09, n)))
    asking = price * np.exp(r.normal(0, 0.12, n))                     # sellers ask more or less than the fair price
    p_sold = 1 / (1 + np.exp(-(0.3 - 12.0 * np.log(asking / price) - 0.02 * age)))
    sold = (r.random(n) < p_sold).astype(int)
    df = pd.DataFrame(dict(brand=brand, model=model, year=year, mileage_km=mileage, fuel=fuel, transmission=trans,
                           engine_cc=engine, owners=owners, city=city, listed_on=listed_on, description=desc,
                           asking_lakh=asking.round(2), price_lakh=price.round(2), sold_30d=sold))
    # missing values: mileage is missing more often for old cars (informative), engine is missing for electric (structural) and randomly
    miss_m = r.random(n) < (0.03 + 0.012 * age)
    df.loc[miss_m, "mileage_km"] = np.nan
    df.loc[r.random(n) < 0.03, "engine_cc"] = np.nan
    df.loc[r.random(n) < 0.02, "transmission"] = None
    return df

cars = make_listings()
print(cars.shape)
print(cars.head(5).to_string())
```
```text
(4000, 14)
     brand  model  year   mileage_km    fuel transmission  engine_cc  owners     city   listed_on                                      description  asking_lakh  price_lakh  sold_30d
0  Hyundai  HYU-2  2019  46,100.0000  petrol       manual   800.0000       2   Mumbai  2024-02-05                            no accident new tyres       3.9400      3.4500         0
1     Tata  TAT-1  2023   7,400.0000  petrol       manual 1,000.0000       2  Chennai  2024-03-13        no accident full service record new tyres       6.0300      6.6400         1
2      BMW  BMW-4  2018 102,300.0000  petrol       manual 2,500.0000       4   Jaipur  2024-01-15  no accident full service record minor scratches      20.9700     16.5100         0
3  Hyundai  HYU-5  2008          NaN  diesel       manual 2,000.0000       3   Indore  2023-08-31                  no accident full service record       1.3500      1.4100         0
4    Honda  HON-5  2022  22,000.0000  diesel       manual 2,000.0000       1     Pune  2024-03-08           no accident single owner AC works well       7.5800      7.4900         0
```

### 2.2 First look: types, missing values, spread

Always profile before you build. These three lines catch most surprises.

```python run
print(cars.dtypes.to_string())
print()
print("missing share per column:")
print(cars.isna().mean().round(3)[lambda s: s > 0].to_string())
print()
print(cars[["price_lakh", "mileage_km", "year", "owners"]].describe().round(2).to_string())
```
```text
brand               str
model               str
year              int64
mileage_km      float64
fuel                str
transmission        str
engine_cc       float64
owners            int64
city                str
listed_on           str
description         str
asking_lakh     float64
price_lakh      float64
sold_30d          int64

missing share per column:
mileage_km     0.1320
transmission   0.0200
engine_cc      0.0780

       price_lakh   mileage_km       year     owners
count  4,000.0000   3,472.0000 4,000.0000 4,000.0000
mean       4.9800  94,274.8800 2,015.4400     2.5700
std        5.4900  62,305.1700     4.6000     1.2500
min        0.4800     500.0000 2,008.0000     1.0000
25%        2.0200  43,000.0000 2,011.0000     2.0000
50%        3.4000  83,600.0000 2,015.0000     2.0000
75%        5.5800 135,900.0000 2,019.0000     3.0000
max       54.8100 372,200.0000 2,023.0000     5.0000
```

Three things to notice for later. `mileage_km` is missing more often for old cars (the *fact* of being missing carries information). `engine_cc` is missing for all electric cars (a structural gap, not an error). `price_lakh` is skewed, so we will meet a log transform.

### 2.3 The split we will use throughout

Following ds.04: split once, keep a sealed test set, and do all choices with cross-validation on the development part.

```python run
target = "price_lakh"
features = [c for c in cars.columns if c not in ["price_lakh", "sold_30d", "asking_lakh"]]   # asking price is the seller's guess at the target: not a fair-price feature
dev, test = model_selection.train_test_split(cars, test_size=0.2, random_state=0)
dev, test = dev.reset_index(drop=True), test.reset_index(drop=True)
X_dev, y_dev = dev[features], dev[target]
X_test, y_test = test[features], test[target]
print("development:", dev.shape, "| sealed test:", test.shape)
print("baseline (predict the mean price) MAE on dev CV:",
      round(-model_selection.cross_val_score(dummy.DummyRegressor(), X_dev, y_dev, cv=5, scoring="neg_mean_absolute_error").mean(), 3), "lakh")
```
```text
development: (3200, 14) | sealed test: (800, 14)
baseline (predict the mean price) MAE on dev CV: 3.2 lakh
```

## 3. Transformers: scaling, imputing, encoding

A raw table cannot go straight into most models. Transformers prepare it. Each one learns something in `fit` (a mean, a category list, a median) and applies it in `transform`.

### 3.1 Scalers

Models that depend on distances or on coefficient size (linear models with penalties, k-NN, SVM, neural networks) are sensitive to the scale of each column. Trees are not.

| Scaler | Formula | When |
|---|---|---|
| `StandardScaler` | `(x - mean) / std` | default for roughly bell-shaped data |
| `MinMaxScaler` | `(x - min) / (max - min)` | bounded features, neural networks |
| `RobustScaler` | `(x - median) / IQR` | outliers present |
| `PowerTransformer` | Yeo-Johnson / Box-Cox | skewed data you want closer to normal |
| `QuantileTransformer` | maps to uniform or normal by rank | heavy-tailed data; non-linear |

```python run
col = cars[["mileage_km"]].dropna()
cmp_ = pd.DataFrame({"raw": col["mileage_km"]})
cmp_["standard"] = preprocessing.StandardScaler().fit_transform(col).ravel()
cmp_["robust"] = preprocessing.RobustScaler().fit_transform(col).ravel()
cmp_["power"] = preprocessing.PowerTransformer().fit_transform(col).ravel()
cmp_["quantile"] = preprocessing.QuantileTransformer(n_quantiles=200, output_distribution="normal", random_state=0).fit_transform(col).ravel()
print(pd.DataFrame({"skew": cmp_.apply(lambda s: stats.skew(s)), "min": cmp_.min(), "max": cmp_.max()}).round(3).to_string())
```
```text
            skew      min          max
raw       0.7030 500.0000 372,200.0000
standard  0.7030  -1.5050       4.4610
robust    0.7030  -0.8950       3.1070
power    -0.0930  -2.8040       2.8650
quantile -0.0750  -5.1990       5.1990
```

### 3.2 Imputers: filling the gaps

`SimpleImputer` fills with a mean, median, most-frequent value or a constant. The statistic is learned from training rows only. **`add_indicator=True` appends a 0/1 column marking which values were missing**, which keeps the information "this was missing" (our mileage gaps are informative).

```python run
demo = pd.DataFrame({"mileage_km": [20000.0, np.nan, 60000.0, 100000.0, np.nan]})
imp = impute.SimpleImputer(strategy="median", add_indicator=True).set_output(transform="pandas")
print(imp.fit_transform(demo).to_string())
print("learned median:", imp.statistics_)
```
```text
    mileage_km  missingindicator_mileage_km
0  20,000.0000                       0.0000
1  60,000.0000                       1.0000
2  60,000.0000                       0.0000
3 100,000.0000                       0.0000
4  60,000.0000                       1.0000
learned median: [60000.]
```

Other imputers: `KNNImputer` (fill from similar rows), `IterativeImputer` (model each column from the others; experimental). They cost more, and often a median plus an indicator is just as good.

### 3.3 Encoders: turning categories into numbers

| Encoder | Output | Use |
|---|---|---|
| `OneHotEncoder` | one 0/1 column per category | nominal categories with few levels |
| `OrdinalEncoder` | one integer column | ordered categories, or tree models |
| `TargetEncoder` | mean of the target per category (cross-fitted) | many levels (e.g. 36 car models, thousands of postcodes) |
| `LabelEncoder` | integer labels for **y** only | targets, never features |

Key options of `OneHotEncoder`: `handle_unknown="ignore"` (a category unseen in training becomes all zeros instead of an error), `min_frequency` (rare levels are grouped into "infrequent"), `drop="first"` (avoids the redundant column for linear models).

```python run
ohe = preprocessing.OneHotEncoder(handle_unknown="ignore", sparse_output=False, min_frequency=0.05).set_output(transform="pandas")
ohe.fit(cars[["fuel", "city"]])
print(ohe.get_feature_names_out().tolist())
unseen = pd.DataFrame({"fuel": ["petrol", "lpg"], "city": ["Delhi", "Goa"]})          # 'lpg' and 'Goa' never appeared
print(ohe.transform(unseen).round(0).T.to_string())
```
```text
['fuel_diesel', 'fuel_electric', 'fuel_hybrid', 'fuel_petrol', 'city_Bengaluru', 'city_Chennai', 'city_Delhi', 'city_Indore', 'city_Jaipur', 'city_Lucknow', 'city_Mumbai', 'city_Pune']
                    0      1
fuel_diesel    0.0000 0.0000
fuel_electric  0.0000 0.0000
fuel_hybrid    0.0000 0.0000
fuel_petrol    1.0000 0.0000
city_Bengaluru 0.0000 0.0000
city_Chennai   0.0000 0.0000
city_Delhi     1.0000 0.0000
city_Indore    0.0000 0.0000
city_Jaipur    0.0000 0.0000
city_Lucknow   0.0000 0.0000
city_Mumbai    0.0000 0.0000
city_Pune      0.0000 0.0000
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one table diagram of one-hot encoding. Input: two rows with columns fuel and city. Row 0 is fuel=petrol, city=Delhi. Row 1 is fuel=lpg, city=Goa, both never seen in training. Output: 12 0/1 columns, 4 for fuel (diesel, electric, hybrid, petrol) and 8 for city (Bengaluru to Pune). Highlight row 0 with a single 1 in fuel_petrol and one in city_Delhi, and row 1 as all zeros because handle_unknown is set to ignore."

`TargetEncoder` is the leak-safe way to use a high-cardinality column (ds.04 section 3.5). During `fit_transform` it uses internal cross-fitting so a row never sees its own label; during `transform` it uses the encodings learned from the full training set.

```python run
te = preprocessing.TargetEncoder(target_type="continuous", random_state=0).set_output(transform="pandas")
enc_train = te.fit_transform(X_dev[["model"]], y_dev)                 # cross-fitted
enc_test = te.transform(X_test[["model"]])
print("fit_transform vs transform on the SAME training rows differ (by design):")
same = te.transform(X_dev[["model"]])
print("  mean |cross-fitted - plain| =", round(float((enc_train["model"] - same["model"]).abs().mean()), 4))
print("learned encodings for 5 models:", {k: round(float(v), 2) for k, v in zip(te.categories_[0][:5], te.encodings_[0][:5])})
```
```text
fit_transform vs transform on the SAME training rows differ (by design):
  mean |cross-fitted - plain| = 0.1195
learned encodings for 5 models: {'BMW-0': 14.03, 'BMW-1': 17.22, 'BMW-2': 18.7, 'BMW-3': 17.53, 'BMW-4': 18.07}
```

### 3.4 Binning and function transforms

`KBinsDiscretizer` turns a number into ordered bins (useful for linear models that need a curve). `FunctionTransformer` wraps any function, such as `np.log1p`, so it can sit in a pipeline.

```python run
kb = preprocessing.KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="quantile").fit(cars[["year"]])
print("year bin edges:", kb.bin_edges_[0])
logt = preprocessing.FunctionTransformer(np.log1p, inverse_func=np.expm1, feature_names_out="one-to-one")
print("log1p of [0, 99999]:", logt.fit_transform(np.array([[0.0], [99999.0]])).ravel().round(3))
```
```text
year bin edges: [2008. 2011. 2015. 2019. 2023.]
log1p of [0, 99999]: [ 0.    11.513]
```

### 3.5 Try it

1. Fit a `OneHotEncoder` with `drop="first"` on `fuel`. How many columns, and which category vanished?
2. Fit `SimpleImputer(strategy="constant", fill_value=-1)` on `mileage_km`. Why might a tree model like this better than the median?

## 4. Pipeline: a chain that behaves like one model

### 4.1 The idea

A `Pipeline` is an ordered list of `(name, step)` pairs. All steps but the last are transformers; the last may be anything. `fit(X, y)` calls `fit_transform` on each transformer in turn, passing each output to the next, then `fit` on the final model. `predict(X)` calls `transform` through the chain and `predict` on the end. To the outside world the whole chain looks like **one estimator**.

```python run
num_only = ["year", "mileage_km", "owners", "engine_cc"]
pipe = pipeline.Pipeline([
    ("impute", impute.SimpleImputer(strategy="median")),
    ("scale", preprocessing.StandardScaler()),
    ("model", linear_model.Ridge(alpha=1.0)),
])
pipe.fit(X_dev[num_only], y_dev)
print(pipe)
print("predict 3 rows:", pipe.predict(X_test[num_only].head(3)).round(2))
print("steps by name :", list(pipe.named_steps))
print("learned medians:", pipe.named_steps["impute"].statistics_)
```
```text
Pipeline(steps=[('impute', SimpleImputer(strategy='median')),
                ('scale', StandardScaler()), ('model', Ridge())])
predict 3 rows: [3.78 1.52 3.78]
steps by name : ['impute', 'scale', 'model']
learned medians: [ 2015. 83700.     2.  1500.]
```

`make_pipeline(step1, step2, ...)` is a shortcut that names steps automatically from the class names (lower-cased).

### 4.2 Why it is the leak-free tool

When you pass the pipeline to `cross_val_score`, each fold calls `fit` on that fold's training rows only. The imputer's median, the scaler's mean, the selected columns: all are learned inside the fold. This is exactly the rule from ds.04. Compare the leaky and the pipeline way on our data.

```python run
cv = model_selection.KFold(5, shuffle=True, random_state=0)
Xnum = X_dev[num_only]

# leaky way: fit the imputer and scaler on ALL development rows first
Xleak = preprocessing.StandardScaler().fit_transform(impute.SimpleImputer(strategy="median").fit_transform(Xnum))
leaky = -model_selection.cross_val_score(linear_model.Ridge(alpha=1.0), Xleak, y_dev, cv=cv, scoring="neg_mean_absolute_error").mean()
honest = -model_selection.cross_val_score(pipe, Xnum, y_dev, cv=cv, scoring="neg_mean_absolute_error").mean()
print(f"MAE leaky preprocessing : {leaky:.4f}")
print(f"MAE inside the pipeline : {honest:.4f}   (the same to four decimals: for a plain scaler and imputer the leak is negligible)")
```
```text
MAE leaky preprocessing : 2.7077
MAE inside the pipeline : 2.7077   (the same to four decimals: for a plain scaler and imputer the leak is negligible)
```

The difference here is tiny, as ds.04 said it would be for plain scalers. The habit is what matters: the same code with `SelectKBest` or a target encoder would differ a lot.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate 5-fold cross-validation on a table of used-car rows, comparing two data flows. Leaky flow: an imputer and scaler are fitted once on all rows, then the folds are split. Pipeline flow: in each fold, the imputer and scaler are fitted on that fold's 4 training parts only, then applied to the held-out part. Colour data that the fitting step can see versus cannot see. Show the five folds side by side for each flow."

### 4.3 Inspecting and slicing a pipeline

```python run
print("first two steps only :", pipe[:2])
print("output of step 2 (first 2 rows):")
print(pipe[:2].transform(X_test[num_only].head(2)).round(3))
print("the final model's coefficients:", pipe[-1].coef_.round(3), "| intercept", round(float(pipe[-1].intercept_), 3))
print("feature names out of the preprocessing:", pipe[:-1].get_feature_names_out().tolist())
```
```text
first two steps only : Pipeline(steps=[('impute', SimpleImputer(strategy='median')),
                ('scale', StandardScaler())])
output of step 2 (first 2 rows):
[[-0.306  0.769  0.352 -0.893]
 [-1.609  0.613 -0.449 -0.54 ]]
the final model's coefficients: [ 2.031 -0.492 -0.375  0.028] | intercept 4.934
feature names out of the preprocessing: ['year', 'mileage_km', 'owners', 'engine_cc']
```

`pipe[:-1]` is "everything but the model": handy to look at the processed matrix, or to reuse the same preprocessing with a different model.

### 4.4 Caching and `passthrough`

A step can be `"passthrough"` (do nothing) or `"drop"`. Setting `memory=` caches fitted transformers on disk, which saves time when you tune only the final model. Grid search can also *swap steps* by setting a step to `"passthrough"` (section 9).

```python run
p2 = pipe.set_params(scale="passthrough")
print("without the scaler:", [name for name, _ in p2.steps], "->", p2.steps[1][1])
pipe.set_params(scale=preprocessing.StandardScaler())     # put it back
```
```text
without the scaler: ['impute', 'scale', 'model'] -> passthrough
```

### 4.5 Try it

1. Build `make_pipeline(impute.SimpleImputer(), linear_model.Ridge())` and print its steps' automatic names.
2. Ask `pipe.get_params()` for the keys that start with `impute__`. What can you tune on the imputer?

## 5. ColumnTransformer: different columns, different treatment

### 5.1 The problem

Our table has numbers, low-cardinality categories, a high-cardinality category, a date and text. Each needs its own preparation. A `ColumnTransformer` applies a different transformer to each group of columns, then glues the results side by side.

```python run
num_cols = ["year", "mileage_km", "engine_cc", "owners"]
low_cat = ["brand", "fuel", "transmission", "city"]
high_cat = ["model"]

prep = compose.ColumnTransformer([
    ("num", pipeline.make_pipeline(impute.SimpleImputer(strategy="median", add_indicator=True), preprocessing.StandardScaler()), num_cols),
    ("low", pipeline.make_pipeline(impute.SimpleImputer(strategy="most_frequent"), preprocessing.OneHotEncoder(handle_unknown="ignore")), low_cat),
    ("high", preprocessing.TargetEncoder(target_type="continuous", random_state=0), high_cat),
], remainder="drop", verbose_feature_names_out=False)

model = pipeline.Pipeline([("prep", prep), ("reg", linear_model.Ridge(alpha=1.0))])
model.fit(X_dev, y_dev)                                # RAW DataFrame in
print("preprocessing output columns:", len(model[:-1].get_feature_names_out()))
print(model[:-1].get_feature_names_out().tolist())
```
```text
preprocessing output columns: 27
['year', 'mileage_km', 'engine_cc', 'owners', 'missingindicator_mileage_km', 'missingindicator_engine_cc', 'brand_BMW', 'brand_Honda', 'brand_Hyundai', 'brand_Maruti', 'brand_Tata', 'brand_Toyota', 'fuel_diesel', 'fuel_electric', 'fuel_hybrid', 'fuel_petrol', 'transmission_automatic', 'transmission_manual', 'city_Bengaluru', 'city_Chennai', 'city_Delhi', 'city_Indore', 'city_Jaipur', 'city_Lucknow', 'city_Mumbai', 'city_Pune', 'model']
```

Each entry is `(name, transformer, columns)`. The `columns` can be a list of names, a boolean mask, or a selector function. `remainder="drop"` discards columns not listed (default), `"passthrough"` keeps them untouched, and a transformer applies to them.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one data-flow diagram of a scikit-learn ColumnTransformer on a used-car table. Input columns: four numeric (year, mileage_km, engine_cc, owners), four low-cardinality categories (brand, fuel, transmission, city) and one high-cardinality column (model). Three branches: impute + scale, impute + one-hot, target encoder. The outputs are glued side by side into 27 columns, then fed into a Ridge model. Label each branch and its column count."

### 5.2 Selecting columns by type: `make_column_selector`

When the column set changes, selecting by dtype is more robust than hard-coding names.

```python run
sel_num = compose.make_column_selector(dtype_include="number")
sel_obj = compose.make_column_selector(dtype_include=["object", "string"])
print("numeric columns :", sel_num(X_dev))
print("text-like columns:", sel_obj(X_dev))
```
```text
numeric columns : ['year', 'mileage_km', 'engine_cc', 'owners']
text-like columns: ['brand', 'model', 'fuel', 'transmission', 'city', 'listed_on', 'description']
```

(Note that `listed_on` and `description` are text-like columns here; we treat them separately in section 7. We left `asking_lakh` out of the features on purpose: it is the seller's own guess at the price, so using it to "predict" the price would be target leakage in the sense of ds.04. It returns in section 10, where the question is different. A real project keeps an explicit list per role in a config file, as the project does in section 14.)

### 5.3 Does the whole thing work? A first honest score

```python run
def cv_mae(est, X=X_dev, y=y_dev, cv=cv):
    s = model_selection.cross_val_score(est, X, y, cv=cv, scoring="neg_mean_absolute_error")
    return -s.mean(), s.std()

m, s = cv_mae(model)
print(f"ridge on raw table, prices as they are : MAE {m:.3f} +- {s:.3f} lakh   (mean-price baseline was 3.2)")
forest = pipeline.Pipeline([("prep", prep), ("reg", ensemble.RandomForestRegressor(n_estimators=100, min_samples_leaf=3, random_state=0, n_jobs=1))])
m, s = cv_mae(forest)
print(f"random forest, same preprocessing      : MAE {m:.3f} +- {s:.3f} lakh")
```
```text
ridge on raw table, prices as they are : MAE 1.369 +- 0.019 lakh   (mean-price baseline was 3.2)
random forest, same preprocessing      : MAE 0.615 +- 0.024 lakh
```

The model object accepts the **raw** `X_dev` with strings and missing values and returns lakh-rupee predictions. That is the chapter's outcome in its simplest form. Everything that follows makes this object better, safer and easier to tune.

### 5.4 Ordering, remainder and sparse output

- **Output column order** follows the order of the entries, not the order in the input table.
- `remainder="passthrough"` is risky in production: a new column that arrives in the data is silently passed to the model. Prefer an explicit list and `remainder="drop"`.
- Mixing one-hot (sparse) and dense outputs: `sparse_threshold` decides whether the combined result is sparse. Most models accept sparse input; some (`HistGradientBoosting`, in older versions) need dense, so check.
- `verbose_feature_names_out=False` keeps the original column names where unique. With `True` (default) names look like `low__fuel_diesel`, which stay unique.

### 5.5 Try it

1. Add an entry `("drop_id", "drop", ["city"])` and remove `city` from `low_cat`. Does the cross-validated MAE change?
2. Pass a test row with a brand never seen in training (`"Skoda"`). What happens, and which option made it safe?


## 6. Writing your own estimator

### 6.1 Why write one

The library cannot know that your `listed_on` is a date or that "accident history" in a description matters. Sooner or later you need a step of your own. If it obeys the API from section 1, it drops into a `Pipeline`, a `ColumnTransformer`, a grid search and a saved file like any built-in class. If it does not, it breaks the leak-free guarantee, because the pipeline cannot call `fit` and `transform` separately.

The recipe: inherit from `BaseEstimator` (gives `get_params`, `set_params`, `__repr__`, `clone` for free) and from `TransformerMixin` (gives `fit_transform`). Then follow four rules:

1. `__init__` only **stores** its arguments, with the same names. No computation, no validation.
2. `fit` learns things and stores them with a trailing underscore. It returns `self`.
3. `transform` uses only what `fit` stored. It never looks at the new data to learn.
4. `get_feature_names_out` tells downstream steps the output column names.

### 6.2 A stateless transformer: car features from raw columns

"Stateless" means there is nothing to learn: the output of each row depends only on that row. It still belongs in a class so it sits inside the pipeline.

```python run
from sklearn.utils.validation import check_is_fitted, validate_data

class CarAge(base.BaseEstimator, base.TransformerMixin):
    """From columns [year, listed_on, mileage_km] make age at listing and kilometres per year."""
    def fit(self, X, y=None):
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        check_is_fitted(self, "n_features_in_")
        listed_year = pd.to_datetime(X["listed_on"]).dt.year
        age = (listed_year - X["year"]).clip(lower=0)
        return pd.DataFrame({"age_at_listing": age, "km_per_year": X["mileage_km"] / age.clip(lower=1)}, index=X.index)

    def get_feature_names_out(self, input_features=None):
        return np.array(["age_at_listing", "km_per_year"], dtype=object)

ca = CarAge().fit(X_dev[["year", "listed_on", "mileage_km"]])
print(ca.transform(X_dev[["year", "listed_on", "mileage_km"]].head(4)).round(1).to_string())
print(ca)
```
```text
   age_at_listing  km_per_year
0              12  19,875.0000
1              13          NaN
2               0   5,600.0000
3               2  18,500.0000
CarAge()
```

### 6.3 A transformer that learns: group rare categories

Here `fit` has real work. It learns which categories are frequent in the **training** data. `transform` then relabels everything else as `"other"`, including categories that never appeared in training. Because the frequent list is learned in `fit`, it is leak-free inside cross-validation.

```python run
class RareGrouper(base.BaseEstimator, base.TransformerMixin):
    """Replace categories seen fewer than `min_count` times in training (or never seen) by `other`."""
    def __init__(self, min_count=50, other="other"):
        self.min_count = min_count
        self.other = other

    def fit(self, X, y=None):
        X = pd.DataFrame(X)
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        self.n_features_in_ = X.shape[1]
        self.frequent_ = {c: set(X[c].value_counts()[lambda s: s >= self.min_count].index) for c in X.columns}
        return self

    def transform(self, X):
        check_is_fitted(self, "frequent_")
        X = pd.DataFrame(X, columns=self.feature_names_in_) if not isinstance(X, pd.DataFrame) else X
        out = X.copy()
        for c in self.frequent_:
            out[c] = X[c].where(X[c].isin(self.frequent_[c]), self.other)
        return out

    def get_feature_names_out(self, input_features=None):
        return self.feature_names_in_

rg = RareGrouper(min_count=100).fit(X_dev[["model", "city"]])
print("models kept as frequent:", len(rg.frequent_["model"]), "of", X_dev["model"].nunique())
probe = pd.DataFrame({"model": ["BMW-3", "ZZZ-9"], "city": ["Delhi", "Goa"]})
print(rg.transform(probe).to_string())
print("get_params:", rg.get_params())
print("clone keeps the settings, drops the learning:", base.clone(rg).get_params() == rg.get_params(), "|", hasattr(base.clone(rg), "frequent_"))
```
```text
models kept as frequent: 12 of 36
   model   city
0  other  Delhi
1  other  other
get_params: {'min_count': 100, 'other': 'other'}
clone keeps the settings, drops the learning: True | False
```

### 6.4 Let scikit-learn audit your estimator

The library ships `check_estimator`, a battery of about 45 tests of the API rules (does `fit` return `self`? does it reject NaN or accept it as declared? does it work on one row? does `clone` work?). Run it on every estimator you write. It works on numeric transformers, so here is a small numeric one, written with `validate_data` so the input checks and `n_features_in_` come for free.

```python run
from sklearn.utils.estimator_checks import check_estimator
from collections import Counter

class QuantileClipper(base.TransformerMixin, base.BaseEstimator):
    """Learn the 1st and 99th percentile of every column in fit; clip to that range in transform."""
    def __init__(self, lower=0.01, upper=0.99):
        self.lower = lower
        self.upper = upper

    def fit(self, X, y=None):
        X = validate_data(self, X, dtype="numeric")
        self.low_ = np.quantile(X, self.lower, axis=0)
        self.high_ = np.quantile(X, self.upper, axis=0)
        return self

    def transform(self, X):
        check_is_fitted(self)
        X = validate_data(self, X, dtype="numeric", reset=False)
        return np.clip(X, self.low_, self.high_)

    def get_feature_names_out(self, input_features=None):
        return utils.validation._check_feature_names_in(self, input_features)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    results = check_estimator(QuantileClipper(), on_fail=None)
print(Counter(r["status"] for r in results))
print("failed checks:", [r["check_name"] for r in results if r["status"] == "failed"])
```
```text
Counter({'passed': 44, 'failed': 2, 'skipped': 1})
failed checks: ['check_estimators_pickle', 'check_estimators_pickle']
```

If the run above reports failures of `check_estimators_pickle`, they are not a bug in the transformer: the class is defined in this session rather than in an importable module, so pickle cannot find it by name. Section 12.2 explains and fixes exactly that; with the class moved into a module file the same check passes. In general, if a check fails, the message names the rule you broke. That is a cheap way to learn the API: break it on purpose and read the complaint.

### 6.5 Custom transformers in a real pipeline

```python run
qc = pipeline.make_pipeline(impute.SimpleImputer(strategy="median"), QuantileClipper(0.01, 0.99), preprocessing.StandardScaler())
qc.fit(X_dev[["mileage_km", "engine_cc"]])
print("clipper learned limits:", qc.named_steps["quantileclipper"].low_.round(0), qc.named_steps["quantileclipper"].high_.round(0))
print("tunable name           :", [k for k in qc.get_params() if k.startswith("quantileclipper__")])
```
```text
clipper learned limits: [7798.  800.] [252131.   2500.]
tunable name           : ['quantileclipper__lower', 'quantileclipper__upper']
```

### 6.6 Try it

1. Write a stateless `LogColumns(columns)` transformer that returns `np.log1p` of chosen columns. Which methods can you leave out?
2. Add `min_count` of `RareGrouper` to a grid search (section 9 shows how). Why does it work with no extra code?

## 7. Feature engineering, measured

### 7.1 The rule

Feature engineering means creating columns that make the pattern easier for the model to see. The temptation is to add many and trust your instinct. The discipline is: **add one idea at a time, and measure it with cross-validation on the development set.** Keep what helps beyond the noise (compare with the fold standard deviation), drop what does not. And **every learned feature step lives inside the pipeline**.

### 7.2 A configurable preprocessor

We build the `ColumnTransformer` from switches so each idea can be turned on separately. `sparse_threshold=0` makes the output dense, which every model accepts.

```python run
low_cat = ["brand", "fuel", "transmission", "city"]
num_cols = ["year", "mileage_km", "engine_cc", "owners"]

def make_prep(*, age=False, text=False, poly=False, target_encode=False):
    parts = [
        ("num", pipeline.make_pipeline(impute.SimpleImputer(strategy="median", add_indicator=True), preprocessing.StandardScaler()), num_cols),
        ("low", pipeline.make_pipeline(impute.SimpleImputer(strategy="most_frequent"), preprocessing.OneHotEncoder(handle_unknown="ignore")), low_cat),
    ]
    if target_encode:
        parts.append(("model_te", preprocessing.TargetEncoder(target_type="continuous", random_state=0), ["model"]))
    else:
        parts.append(("model_ohe", preprocessing.OneHotEncoder(handle_unknown="ignore", min_frequency=0.01), ["model"]))
    if age:
        parts.append(("age", pipeline.make_pipeline(CarAge(), impute.SimpleImputer(strategy="median"), preprocessing.StandardScaler()), ["year", "listed_on", "mileage_km"]))
    if text:
        parts.append(("text", feature_extraction.text.TfidfVectorizer(ngram_range=(1, 2), min_df=10), "description"))   # a single column NAME, not a list
    if poly:
        parts.append(("poly", pipeline.make_pipeline(impute.SimpleImputer(strategy="median"), preprocessing.StandardScaler(),
                                                      preprocessing.PolynomialFeatures(degree=2, include_bias=False)), ["year", "mileage_km", "owners"]))
    return compose.ColumnTransformer(parts, remainder="drop", sparse_threshold=0)

def ridge_model(prep, log_target=True, alpha=1.0):
    reg = linear_model.Ridge(alpha=alpha)
    if log_target:
        reg = compose.TransformedTargetRegressor(regressor=reg, func=np.log, inverse_func=np.exp)
    return pipeline.Pipeline([("prep", prep), ("reg", reg)])

print(make_prep(age=True, text=True))
```
```text
ColumnTransformer(sparse_threshold=0,
                  transformers=[('num',
                                 Pipeline(steps=[('simpleimputer',
                                                  SimpleImputer(add_indicator=True,
                                                                strategy='median')),
                                                 ('standardscaler',
                                                  StandardScaler())]),
                                 ['year', 'mileage_km', 'engine_cc', 'owners']),
                                ('low',
                                 Pipeline(steps=[('simpleimputer',
                                                  SimpleImputer(strategy='most_frequent')),
                                                 ('onehotencoder',
                                                  OneHotEncoder(handle_unkno...
                                 ['brand', 'fuel', 'transmission', 'city']),
                                ('model_ohe',
                                 OneHotEncoder(handle_unknown='ignore',
                                               min_frequency=0.01),
                                 ['model']),
                                ('age',
                                 Pipeline(steps=[('carage', CarAge()),
                                                 ('simpleimputer',
                                                  SimpleImputer(strategy='median')),
                                                 ('standardscaler',
                                                  StandardScaler())]),
                                 ['year', 'listed_on', 'mileage_km']),
                                ('text',
                                 TfidfVectorizer(min_df=10, ngram_range=(1, 2)),
                                 'description')])
```

Two scikit-learn features appear here worth naming. A **string** as the column spec (`"description"`) hands the transformer a 1-D column, which is what text vectorisers expect; a **list** (`["model"]`) hands a 2-D table. And `TransformedTargetRegressor` fits the model on `log(price)` and converts predictions back with `exp`, all inside the object, so callers still see lakh rupees.

### 7.3 One idea at a time

```python run
rows = []
def record(name, est):
    t0 = time.perf_counter()
    m, s = cv_mae(est)
    rows.append((name, m, s, time.perf_counter() - t0))

record("A. ridge, price as is, base columns", ridge_model(make_prep(), log_target=False))
record("B. + log target", ridge_model(make_prep()))
record("C. + age at listing, km per year", ridge_model(make_prep(age=True)))
record("D. + description text (tf-idf)", ridge_model(make_prep(age=True, text=True)))
record("E. + degree-2 interactions", ridge_model(make_prep(age=True, text=True, poly=True)))
record("F. D but `model` target-encoded instead of one-hot", ridge_model(make_prep(age=True, text=True, target_encode=True)))
table = pd.DataFrame(rows, columns=["step", "MAE (lakh)", "fold std", "seconds"]).set_index("step")
print(table.round(3).to_string())
```
```text
                                                    MAE (lakh)  fold std  seconds
step                                                                             
A. ridge, price as is, base columns                     1.3440    0.0270   0.5050
B. + log target                                         0.4270    0.0120   0.3760
C. + age at listing, km per year                        0.4240    0.0090   0.8160
D. + description text (tf-idf)                          0.3900    0.0120   1.3820
E. + degree-2 interactions                              0.3890    0.0100   1.4500
F. D but `model` target-encoded instead of one-hot      0.6730    0.0480   0.9830
```

> **Predict the output.** Row F replaces the one-hot columns of the 36 car `model` values by a target encoding, which is the more "advanced" tool. Will the error go down, stay the same, or go up?

<details><summary>Answer</summary>

It goes **up**, from 0.390 to 0.673 lakh. The advanced tool is not automatically better: 36 levels with about 90 rows each is a case where one-hot loses nothing, and the target encoder averages the raw price while the model works on the log price (see the explanation below the table).

</details>

How to read it: a change is real only if it beats the **fold standard deviation** by a margin, not just the third decimal. The log target (B) is a large step because prices multiply (each year of age takes about the same *percentage* off), and a straight-line model on the raw price cannot express that. Text (D) helps because "accident history" really moves the price. Interactions (E) add a bit or nothing; each extra feature must pay for itself.

Row F is the surprise, and the most useful row for your judgement. Replacing the one-hot columns of the 36 car `model` values by a **target encoding** makes the error much *worse*. Two reasons. First, 36 levels with about 90 rows each is not a high-cardinality column: one-hot gives every level its own coefficient and loses nothing. Second, the target encoder sees the target **as the pipeline gives it**. Here `TransformedTargetRegressor` wraps only the last step, so the encoder averages the *raw* price, while the model works on the *log* price; a mean of raw prices per car model is a poor, noisy linear feature, and during training it is cross-fitted (noisier still). Target encoding is a tool for columns with hundreds or thousands of levels, where one-hot is impractical. Reach for the simple tool first, and let the measurement overrule fashion.

### 7.4 Dates and cyclical features

A listing month, hour of day or weekday is cyclical: December is next to January. A raw number 1..12 breaks that. Encode a cycle with sine and cosine so the ends meet.

```python run
months = np.arange(1, 13)
cyc = pd.DataFrame({"month": months, "sin": np.sin(2 * np.pi * months / 12), "cos": np.cos(2 * np.pi * months / 12)})
print(cyc.round(3).iloc[[0, 5, 6, 11]].to_string(index=False))
d_jan_dec = np.hypot(cyc.loc[0, "sin"] - cyc.loc[11, "sin"], cyc.loc[0, "cos"] - cyc.loc[11, "cos"])
d_jan_jul = np.hypot(cyc.loc[0, "sin"] - cyc.loc[6, "sin"], cyc.loc[0, "cos"] - cyc.loc[6, "cos"])
print(f"distance January-December {d_jan_dec:.2f}  vs  January-July {d_jan_jul:.2f}")
```
```text
 month     sin     cos
     1  0.5000  0.8660
     6  0.0000 -1.0000
     7 -0.5000 -0.8660
    12 -0.0000  1.0000
distance January-December 0.52  vs  January-July 2.00
```

In this dataset the listing month has no effect on price (we built it that way), so adding it would only add noise. Real engineering is knowing what to try *and* testing it.

### 7.5 Interactions, bins and domain features

| Idea | Tool | Example here |
|---|---|---|
| Ratio of two columns | custom transformer or `FunctionTransformer` | km per year (done) |
| Product / square | `PolynomialFeatures` | age x mileage |
| Bins | `KBinsDiscretizer` | year bands for a linear model |
| Counts and flags from text | `CountVectorizer`, `TfidfVectorizer` | "accident" in the description |
| Group statistics (mean price of this model) | `TargetEncoder` | the 36 car models |
| Missing-value flag | `add_indicator=True` | mileage missing |
| Domain knowledge | a custom transformer | age at listing |

Trees find interactions and thresholds by themselves; linear models need them handed over. That is why engineering helps a ridge model a lot and a gradient-boosting model less (next section).

### 7.6 Feature selection, inside the pipeline

Two safe tools: `VarianceThreshold` (drop constant columns) and `SelectKBest`/`SelectFromModel` (keep the best columns). From ds.04 you know they must be **steps in the pipeline**, never applied before the split. A quick check that they are not needed here:

```python run
sel_pipe = pipeline.Pipeline([("prep", make_prep(age=True, text=True)),
                              ("select", feature_selection.SelectFromModel(linear_model.LassoCV(cv=3, random_state=0), threshold="median")),
                              ("reg", compose.TransformedTargetRegressor(regressor=linear_model.Ridge(alpha=1.0), func=np.log, inverse_func=np.exp))])
m, s = cv_mae(sel_pipe)
print(f"keep the best half of the columns (selected inside the folds): MAE {m:.3f} +- {s:.3f}   (table row D was {rows[3][1]:.3f})")
```
```text
keep the best half of the columns (selected inside the folds): MAE 0.392 +- 0.014   (table row D was 0.390)
```

### 7.7 Leakage in engineered features

Every feature you create must be computable **at prediction time from information available then**. Group statistics (average price per city, per model) computed over the whole table before splitting are a leak. Compute them with `TargetEncoder` or a custom transformer that learns them in `fit`. A good test is the one from ds.04: *would this feature have the same value if I deleted all rows after this one?*

### 7.8 Try it

1. Add `"city"` to the `TargetEncoder` and drop it from `low_cat`. Does the MAE move by more than the fold standard deviation?
2. Add a transformer that creates `is_automatic_diesel` (an interaction flag). Does ridge with log target improve?

## 8. Model selection: comparing models fairly

### 8.1 Same data, same splits, same preprocessing

Comparing models fairly means giving each the **same folds** and the **same preprocessing**, and measuring the same things. `cross_validate` runs a model through the folds and returns several metrics, fit times and (optionally) training scores in one go.

```python run
final_prep = lambda: make_prep(age=True, text=True)
def tt(est):
    return compose.TransformedTargetRegressor(regressor=est, func=np.log, inverse_func=np.exp)

candidates = {
    "dummy (median)": dummy.DummyRegressor(strategy="median"),
    "ridge": linear_model.Ridge(alpha=1.0),
    "random forest": ensemble.RandomForestRegressor(n_estimators=100, min_samples_leaf=3, random_state=0, n_jobs=1),
    "hist gradient boosting": ensemble.HistGradientBoostingRegressor(random_state=0),
}
scoring = {"mae": "neg_mean_absolute_error", "rmse": "neg_root_mean_squared_error", "r2": "r2", "mape": "neg_mean_absolute_percentage_error"}
cv5 = model_selection.KFold(5, shuffle=True, random_state=0)
rows = []
for name, est in candidates.items():
    r = model_selection.cross_validate(pipeline.Pipeline([("prep", final_prep()), ("reg", tt(est))]), X_dev, y_dev, cv=cv5,
                                       scoring=scoring, return_train_score=True)
    rows.append((name, -r["test_mae"].mean(), -r["train_mae"].mean(), -r["test_rmse"].mean(), r["test_r2"].mean(), -r["test_mape"].mean(), r["fit_time"].mean()))
cmp_models = pd.DataFrame(rows, columns=["model", "val MAE", "train MAE", "val RMSE", "val R2", "val MAPE", "fit s"]).set_index("model")
print(cmp_models.round(3).to_string())
```
```text
                        val MAE  train MAE  val RMSE  val R2  val MAPE  fit s
model                                                                        
dummy (median)           2.8750     2.8730    5.6710 -0.0830    0.6450 0.1140
ridge                    0.3900     0.3780    0.7200  0.9820    0.0800 0.1180
random forest            0.6600     0.3590    1.3080  0.9420    0.1330 5.1830
hist gradient boosting   0.4680     0.2890    0.9440  0.9700    0.0920 1.7790
```

> **Predict the output.** Before reading the table: which of the four models (dummy, ridge, random forest, hist gradient boosting) will have the lowest validation MAE? Which will have the largest gap between train and validation MAE?

<details><summary>Answer</summary>

The lowest validation MAE belongs to the plain **ridge** (0.390), ahead of boosting (0.468) and the forest (0.660). The largest train/validation gap belongs to the **random forest** (training MAE 0.359, validation 0.660): it fits the training rows far better than it generalises. The data follow a log-linear rule, which suits the simplest model best.

</details>

Read the **gap** between train MAE and validation MAE: a large gap is variance (ds.03 section 7). The random forest shows it clearly (training error far below validation error). Read `MAPE` as a percentage of the price, which is how a buyer thinks.

The winner is the **plain ridge regression**, ahead of the forest and the boosting model. That is not a fluke and not a failure of the fancy models. We built the price rule as a product of effects (age, mileage, brand...), which is a straight line on the log scale, and the ridge on a log target matches it exactly. Trees must approximate a straight line with steps and need many rows to do it. The lesson of ds.04 holds again: the right model is the one whose assumptions fit the structure, and you find out by measuring, not by choosing the most flexible one.

### 8.2 Custom scorers

A business metric is often not in the list. `make_scorer` turns any `f(y_true, y_pred)` into a scorer. Here: the share of predictions within 10% of the true price.

```python run
def within_10pct(y_true, y_pred):
    return float(np.mean(np.abs(y_pred - y_true) / y_true <= 0.10))

scorer = metrics.make_scorer(within_10pct)                     # greater is better
best = pipeline.Pipeline([("prep", final_prep()), ("reg", tt(ensemble.HistGradientBoostingRegressor(random_state=0)))])
s = model_selection.cross_val_score(best, X_dev, y_dev, cv=cv5, scoring=scorer)
print("share of predictions within 10% of the price (hist gradient boosting):", s.mean().round(3), "+-", s.std().round(3))
```
```text
share of predictions within 10% of the price (hist gradient boosting): 0.625 +- 0.017
```

If your metric is "smaller is better", pass `greater_is_better=False`; scikit-learn then negates it so all scorers follow "bigger is better".

### 8.3 Paired comparison of two models

As in ds.04, compare models on the **same folds** and look at the paired differences. Repeating the cross-validation with different shuffles gives more pairs.

```python run
rk = model_selection.RepeatedKFold(n_splits=5, n_repeats=3, random_state=1)
def fold_maes(est):
    return -model_selection.cross_val_score(pipeline.Pipeline([("prep", final_prep()), ("reg", tt(est))]), X_dev, y_dev, cv=rk, scoring="neg_mean_absolute_error")
a = fold_maes(candidates["ridge"]); b = fold_maes(candidates["hist gradient boosting"])
d = a - b
print(f"ridge MAE {a.mean():.3f}, boosting MAE {b.mean():.3f}; paired difference (ridge - boosting) per fold: mean {d.mean():.3f}, std {d.std(ddof=1):.3f}")
print(f"ridge better in {int((d < 0).sum())} of {len(d)} folds, boosting better in {int((d > 0).sum())}")
```
```text
ridge MAE 0.392, boosting MAE 0.466; paired difference (ridge - boosting) per fold: mean -0.074, std 0.022
ridge better in 15 of 15 folds, boosting better in 0
```

### 8.4 Validation curves: one hyperparameter at a time

`validation_curve` shows training and validation scores as one hyperparameter changes. It is the cheapest picture of over- and under-fitting for that parameter.

```python run
pipe_hgb = pipeline.Pipeline([("prep", final_prep()), ("reg", tt(ensemble.HistGradientBoostingRegressor(random_state=0)))])
depths = [2, 4, 8, 16, 32, 64]
tr_sc, va_sc = model_selection.validation_curve(pipe_hgb, X_dev, y_dev, param_name="reg__regressor__max_leaf_nodes", param_range=depths,
                                                 cv=cv5, scoring="neg_mean_absolute_error")
print(pd.DataFrame({"max_leaf_nodes": depths, "train MAE": -tr_sc.mean(1), "validation MAE": -va_sc.mean(1)}).round(3).to_string(index=False))
```
```text
 max_leaf_nodes  train MAE  validation MAE
              2     0.9290          0.9440
              4     0.6610          0.6990
              8     0.4390          0.5030
             16     0.3590          0.4640
             32     0.2850          0.4680
             64     0.2090          0.4900
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot one validation curve with max_leaf_nodes on the x axis (2, 4, 8, 16, 32, 64, log scale) and mean absolute error on the y axis. Train MAE: 0.929, 0.661, 0.439, 0.359, 0.285, 0.209. Validation MAE: 0.944, 0.699, 0.503, 0.464, 0.468, 0.490. Mark the validation minimum at 16 leaves, shade the left side as underfitting and the right side as overfitting, and show the growing gap between the two lines."

### 8.5 Residuals: where is the model wrong?

`cross_val_predict` gives an out-of-fold prediction for every row, so you can study errors without touching the test set (the ds.04 error analysis habit).

```python run
oof = model_selection.cross_val_predict(best, X_dev, y_dev, cv=cv5)
res = pd.DataFrame({"brand": X_dev["brand"], "fuel": X_dev["fuel"], "y": y_dev, "pred": oof})
res["abs_pct_error"] = (res["pred"] - res["y"]).abs() / res["y"]
print(res.groupby("brand")["abs_pct_error"].agg(["size", "mean"]).round(3).rename(columns={"mean": "mean abs % error"}).to_string())
print()
print(res.groupby("fuel")["abs_pct_error"].agg(["size", "mean"]).round(3).rename(columns={"mean": "mean abs % error"}).to_string())
```
```text
         size  mean abs % error
brand                          
BMW       236            0.1060
Honda     429            0.0930
Hyundai   752            0.0940
Maruti    887            0.0850
Tata      463            0.0890
Toyota    433            0.0990

          size  mean abs % error
fuel                            
diesel    1206            0.0920
electric   169            0.1130
hybrid     249            0.1040
petrol    1576            0.0880
```

### 8.6 Try it

1. Add `ensemble.ExtraTreesRegressor` and `linear_model.Lasso` to the comparison. Which wins? Is the winner's margin larger than the fold spread?
2. Change `within_10pct` to 5% and recompute. What does the answer tell you about how to describe the model to a buyer?

## 9. Hyperparameter tuning

### 9.1 What is being tuned

Hyperparameters are the settings you choose before `fit` (section 1.3, rule 1). Tuning means searching for a good combination by cross-validation. Three search classes cover almost every need:

| Class | Strategy | Use when |
|---|---|---|
| `GridSearchCV` | tries every combination | few parameters, few values each |
| `RandomizedSearchCV` | samples combinations at random from distributions | many parameters, continuous ranges |
| `HalvingRandomSearchCV` | tries many candidates on little data, keeps the best, gives them more data | expensive models, large grids |

All three behave like an estimator: `fit(X, y)` runs the search and (by default) **refits the best setting on all the data you gave it**; `predict` then uses that refitted model. After `fit`, look at `best_params_`, `best_score_`, `best_estimator_` and `cv_results_`.

### 9.2 Grid search: ridge strength and a preprocessing choice

The double-underscore names reach any step. Note how a setting of the *preprocessing* is tuned alongside the model: that is only safe because it is all one pipeline.

```python run
ridge_pipe = ridge_model(make_prep(age=True, text=True))
print([k for k in ridge_pipe.get_params() if "alpha" in k or "strategy" in k][:6])

grid = {
    "reg__regressor__alpha": [0.1, 0.3, 1.0, 3.0, 10.0],
    "prep__num__simpleimputer__strategy": ["median", "mean"],
}
gs = model_selection.GridSearchCV(ridge_pipe, grid, cv=cv5, scoring="neg_mean_absolute_error", n_jobs=1, refit=True)
t0 = time.perf_counter(); gs.fit(X_dev, y_dev); t_grid = time.perf_counter() - t0
print(f"grid search: {len(gs.cv_results_['params'])} candidates x 5 folds = {len(gs.cv_results_['params']) * 5} fits in {t_grid:.1f} s")
print("best params:", gs.best_params_, "| best CV MAE:", round(-gs.best_score_, 4))
cvr = pd.DataFrame(gs.cv_results_)
cols = ["param_reg__regressor__alpha", "param_prep__num__simpleimputer__strategy", "mean_test_score", "std_test_score", "rank_test_score"]
print(cvr[cols].sort_values("rank_test_score").head(5).round(4).to_string(index=False))
```
```text
['prep__num__simpleimputer__strategy', 'prep__low__simpleimputer__strategy', 'prep__age__simpleimputer__strategy', 'reg__regressor__alpha']
grid search: 10 candidates x 5 folds = 50 fits in 9.9 s
best params: {'prep__num__simpleimputer__strategy': 'median', 'reg__regressor__alpha': 1.0} | best CV MAE: 0.3899
 param_reg__regressor__alpha param_prep__num__simpleimputer__strategy  mean_test_score  std_test_score  rank_test_score
                      1.0000                                   median          -0.3899          0.0121                1
                      1.0000                                     mean          -0.3899          0.0121                2
                      3.0000                                   median          -0.3904          0.0142                3
                      3.0000                                     mean          -0.3904          0.0142                4
                      0.3000                                   median          -0.3905          0.0109                5
```

If the best `alpha` sits at the **edge** of the grid (the largest or smallest value tried), extend the grid in that direction; the true optimum may lie beyond. And if two settings tie exactly (as `mean` and `median` imputation may here), the setting did not matter, which is itself a finding.

`cv_results_` is a table of every candidate: read it, do not trust only the winner. When the top several candidates differ by less than their `std_test_score`, the choice among them is noise; choose the simplest or cheapest.

### 9.3 Randomized search: boosting with several hyperparameters

Random search samples from **distributions** (`scipy.stats`). It is usually better than a grid when only a few of the parameters really matter, because it tries many distinct values of each.

```python run
dist = {
    "reg__regressor__learning_rate": stats.loguniform(0.02, 0.3),
    "reg__regressor__max_leaf_nodes": stats.randint(8, 64),
    "reg__regressor__min_samples_leaf": stats.randint(5, 60),
    "reg__regressor__l2_regularization": stats.loguniform(1e-3, 10),
}
rs = model_selection.RandomizedSearchCV(pipe_hgb, dist, n_iter=12, cv=3, scoring="neg_mean_absolute_error", random_state=0, n_jobs=1)
t0 = time.perf_counter(); rs.fit(X_dev, y_dev); t_rand = time.perf_counter() - t0
print(f"random search: 12 candidates x 3 folds in {t_rand:.1f} s")
print("best params:", {k.split("__")[-1]: round(v, 4) if isinstance(v, float) else v for k, v in rs.best_params_.items()})
print("best CV MAE:", round(-rs.best_score_, 4), "| default-settings MAE (5-fold, section 8):", round(-model_selection.cross_val_score(pipe_hgb, X_dev, y_dev, cv=3, scoring="neg_mean_absolute_error").mean(), 4))
```
```text
random search: 12 candidates x 3 folds in 57.2 s
best params: {'l2_regularization': np.float64(0.1568), 'learning_rate': np.float64(0.1387), 'max_leaf_nodes': 11, 'min_samples_leaf': 8}
best CV MAE: 0.4879 | default-settings MAE (5-fold, section 8): 0.493
```

Read the last line honestly. If the tuned score is no better than the default-settings score, the defaults were already near a good region and tuning bought nothing. That is a common and useful outcome: it tells you to spend the effort on features and data instead.

### 9.4 Successive halving: spend effort on the promising candidates

Halving starts many candidates on a small slice of the data, keeps the best third, retrains them on more data, and repeats. On a table this small the saving can be swallowed by the overhead of the extra rounds (compare the two times printed below); halving pays when a single fit is slow or the data are large. It is still marked experimental, so you import `enable_halving_search_cv` first.

```python run
from sklearn.experimental import enable_halving_search_cv  # noqa: F401  (activates the experimental classes)
from sklearn.model_selection import HalvingRandomSearchCV

hs = HalvingRandomSearchCV(pipe_hgb, dist, n_candidates=24, factor=3, resource="n_samples", min_resources=400,
                           cv=3, scoring="neg_mean_absolute_error", random_state=0, n_jobs=1)
t0 = time.perf_counter(); hs.fit(X_dev, y_dev); t_half = time.perf_counter() - t0
print(f"halving: {hs.n_iterations_} rounds; candidates per round {hs.n_candidates_}; rows per candidate {hs.n_resources_}")
print(f"time {t_half:.1f} s (random search of 9.3 took {t_rand:.1f} s) | best CV MAE {-hs.best_score_:.4f} (scored on the final round's data)")
```
```text
halving: 2 rounds; candidates per round [24, 8]; rows per candidate [400, 1200]
time 81.1 s (random search of 9.3 took 57.2 s) | best CV MAE 0.5343 (scored on the final round's data)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate successive halving as a tournament funnel. Round 1: 24 candidate models, each trained on 400 rows. Keep the best third, which is 8 candidates. Round 2: those 8 are retrained on 1200 rows (3 times more). Show 24 dots shrinking to 8 and the data bar per candidate growing from 400 to 1200 rows, with a final winner highlighted. Label each round."

### 9.5 Searching over the pipeline's structure

A pipeline step can itself be a hyperparameter: pass a list of whole estimators. Here the search chooses between a ridge, a forest and a boosting model, each with its own setting, in one run. A list of dictionaries lets each model have its own parameter names.

```python run
swap_pipe = pipeline.Pipeline([("prep", final_prep()), ("reg", tt(linear_model.Ridge()))])
space = [
    {"reg__regressor": [linear_model.Ridge()], "reg__regressor__alpha": [0.3, 1.0, 3.0]},
    {"reg__regressor": [ensemble.HistGradientBoostingRegressor(random_state=0)], "reg__regressor__max_leaf_nodes": [8, 16, 31]},
]
sg = model_selection.GridSearchCV(swap_pipe, space, cv=3, scoring="neg_mean_absolute_error", n_jobs=1).fit(X_dev, y_dev)
out = pd.DataFrame(sg.cv_results_)[["param_reg__regressor", "mean_test_score", "rank_test_score"]]
out["param_reg__regressor"] = out["param_reg__regressor"].map(lambda e: type(e).__name__)
print(out.round(4).to_string(index=False))
```
```text
         param_reg__regressor  mean_test_score  rank_test_score
                        Ridge          -0.3953                2
                        Ridge          -0.3947                1
                        Ridge          -0.3961                3
HistGradientBoostingRegressor          -0.5162                6
HistGradientBoostingRegressor          -0.4777                4
HistGradientBoostingRegressor          -0.4930                5
```

### 9.6 The optimism of the search itself

The best score of a search is a **maximum over many noisy scores**, so it is biased upward (ds.03 section 10, ds.04 section 2). To measure the real performance of "the whole procedure including tuning" use **nested cross-validation**: an outer loop holds out data, and an inner loop (the search) runs only on the rest.

```python run
inner = model_selection.RandomizedSearchCV(pipe_hgb, dist, n_iter=8, cv=3, scoring="neg_mean_absolute_error", random_state=0, n_jobs=1)
outer = model_selection.KFold(4, shuffle=True, random_state=2)
inner_best, outer_score = [], []
for tr, te in outer.split(X_dev):
    inner.fit(X_dev.iloc[tr], y_dev.iloc[tr])
    inner_best.append(-inner.best_score_)
    outer_score.append(metrics.mean_absolute_error(y_dev.iloc[te], inner.predict(X_dev.iloc[te])))
print("inner best-candidate MAE per outer fold:", np.round(inner_best, 4))
print("outer (honest) MAE per outer fold      :", np.round(outer_score, 4))
print(f"mean inner {np.mean(inner_best):.4f} vs mean outer {np.mean(outer_score):.4f} -> optimism of the search: {np.mean(outer_score) - np.mean(inner_best):+.4f} lakh")
```
```text
inner best-candidate MAE per outer fold: [0.509  0.5173 0.5177 0.4897]
outer (honest) MAE per outer fold      : [0.4633 0.4745 0.4434 0.5258]
mean inner 0.5084 vs mean outer 0.4767 -> optimism of the search: -0.0317 lakh
```

Two opposite effects hide in this comparison. The inner score is a **maximum over candidates** (optimistic), but it is computed by 3-fold CV on part of the outer training data, so each inner model sees less data than the final model does (pessimistic). If the second effect wins, the outer error is *lower* than the inner one; with a bigger search or a smaller table the first effect wins. Neither number is wrong; they answer different questions, and only the outer one is an honest estimate for the final procedure. The cure is always the same: a final score from data the search never saw.

### 9.7 The one test-set evaluation

Tuning is finished. We pick the winner by its **cross-validation score**, take the search object (already refitted on all development data) and score the sealed test set **once**, next to the baseline.

```python run
# The choice between the two tuned searches is made from CV scores on the development set, never from the test set:
print(f"CV MAE: grid-searched ridge {-gs.best_score_:.3f} | randomly searched boosting {-rs.best_score_:.3f} -> choose the ridge")
final_search = gs                                           # refit on the whole development set by GridSearchCV(refit=True)
pred_test = final_search.predict(X_test)
mae_ = metrics.mean_absolute_error(y_test, pred_test)
print(f"sealed test MAE            : {mae_:.3f} lakh")
print(f"  mean-price baseline       : {metrics.mean_absolute_error(y_test, np.full(len(y_test), y_dev.mean())):.3f}")
print(f"  (for the record) boosting : {metrics.mean_absolute_error(y_test, rs.predict(X_test)):.3f}   <- not chosen, shown only to confirm the choice")
print(f"sealed test R2             : {metrics.r2_score(y_test, pred_test):.3f}")
print(f"within 10% of the price    : {within_10pct(y_test.to_numpy(), pred_test):.3f}")
```
```text
CV MAE: grid-searched ridge 0.390 | randomly searched boosting 0.488 -> choose the ridge
sealed test MAE            : 0.408 lakh
  mean-price baseline       : 3.296
  (for the record) boosting : 0.495   <- not chosen, shown only to confirm the choice
sealed test R2             : 0.976
within 10% of the price    : 0.714
```

### 9.8 A tuning checklist

1. Start with defaults and a baseline; tuning rarely rescues a bad feature set.
2. Tune the **pipeline**, not the model alone, when preprocessing has choices.
3. Use random or halving search when you have more than three parameters.
4. Use log scales (`loguniform`) for rates and penalties; integers for sizes.
5. Read `cv_results_`: if the top candidates tie within noise, pick the simplest.
6. Fix `random_state` everywhere (ds.04 section 13) and record the search settings.
7. Estimate the real performance with a sealed test set or nested CV.
8. Stop when the gain is smaller than the fold spread.

### 9.9 Try it

1. Change `n_iter` from 15 to 40 in the random search. Does the best CV MAE improve by more than the nested-CV optimism you measured?
2. Use `scoring="neg_root_mean_squared_error"` instead. Does the best parameter set change?


## 10. Targets, thresholds and calibration inside the API

### 10.1 A classification problem on the same table: will the car sell in 30 days?

The marketplace wants to know which listings will sell within 30 days. The signal that matters is the asking price **relative to the fair price**. We do not know the fair price at listing time, but we can estimate it with the regression model of section 9. That makes the classifier a **second stage** that uses the first model's output as a feature, and this is where a classic leak appears.

> **Cross-fit rule.** If stage 1 is fitted on the same rows that stage 2 trains on, stage 1's predictions on those rows are too good (it has seen their prices). The second model then learns to trust a feature that will be less accurate at prediction time. Give stage 2 **out-of-fold** stage-1 predictions for the training rows, and the ordinary predictions of the fully fitted stage 1 for new rows. `cross_val_predict` does exactly this.

```python run
cls_dev, cls_test = model_selection.train_test_split(cars, test_size=0.2, random_state=5, stratify=cars["sold_30d"])
cls_dev, cls_test = cls_dev.reset_index(drop=True), cls_test.reset_index(drop=True)
price_model = pipeline.Pipeline([("prep", final_prep()), ("reg", tt(ensemble.HistGradientBoostingRegressor(random_state=0)))])

# Stage 1: fair price. Out-of-fold for the development rows, fully fitted model for test rows.
fair_dev_oof = model_selection.cross_val_predict(price_model, cls_dev[features], cls_dev["price_lakh"], cv=5)
price_model.fit(cls_dev[features], cls_dev["price_lakh"])
fair_dev_leaky = price_model.predict(cls_dev[features])               # what a careless pipeline would use for training
fair_test = price_model.predict(cls_test[features])

def stage2(df, fair):
    out = df[["brand", "fuel", "transmission", "year", "owners", "city"]].copy()
    out["asking_vs_fair"] = np.log(df["asking_lakh"] / fair)
    return out

print("stage-1 MAE on the training rows, in-sample:", round(metrics.mean_absolute_error(cls_dev["price_lakh"], fair_dev_leaky), 3), "lakh")
print("stage-1 MAE on the training rows, out-of-fold:", round(metrics.mean_absolute_error(cls_dev["price_lakh"], fair_dev_oof), 3), "lakh   <- what new listings will see")
print("share of listings sold within 30 days (development):", round(cls_dev["sold_30d"].mean(), 3))
```
```text
stage-1 MAE on the training rows, in-sample: 0.305 lakh
stage-1 MAE on the training rows, out-of-fold: 0.48 lakh   <- what new listings will see
share of listings sold within 30 days (development): 0.531
```

```python run
cat_cols = ["brand", "fuel", "transmission", "city"]
clf_prep = compose.ColumnTransformer([
    ("cat", pipeline.make_pipeline(impute.SimpleImputer(strategy="most_frequent"), preprocessing.OneHotEncoder(handle_unknown="ignore")), cat_cols),
    ("num", preprocessing.StandardScaler(), ["year", "owners", "asking_vs_fair"]),
])
clf = pipeline.Pipeline([("prep", clf_prep), ("lr", linear_model.LogisticRegression(max_iter=2000))])

Xc_dev_ok, Xc_dev_leaky, Xc_test = stage2(cls_dev, fair_dev_oof), stage2(cls_dev, fair_dev_leaky), stage2(cls_test, fair_test)
for name, Xd in [("cross-fitted stage-1 feature", Xc_dev_ok), ("in-sample stage-1 feature (leaky)", Xc_dev_leaky)]:
    m = clf.fit(Xd, cls_dev["sold_30d"])
    print(f"trained on {name:36s}: test AUC {metrics.roc_auc_score(cls_test['sold_30d'], m.predict_proba(Xc_test)[:, 1]):.3f} | learned weight on asking_vs_fair {m['lr'].coef_[0][-1]:+.2f}")
```
```text
trained on cross-fitted stage-1 feature        : test AUC 0.709 | learned weight on asking_vs_fair -0.82
trained on in-sample stage-1 feature (leaky)   : test AUC 0.711 | learned weight on asking_vs_fair -1.05
```

The in-sample version looks cleaner to the second model, so it puts a different (here larger) weight on the feature than the honest version does. Look at what changed and what did not: the **weight** moved clearly, the **test AUC** hardly at all. A leak of this kind mostly distorts the *size* of the effect (and so the probabilities and thresholds built on it) more than the *ranking*. Our price model is strong and regularised, so the effect is mild; with an overfit first stage (a deep forest, a huge boosting model) it grows. scikit-learn automates the cross-fit rule in `StackingClassifier` / `StackingRegressor`.

From here we use the cross-fitted version.

```python run
clf.fit(Xc_dev_ok, cls_dev["sold_30d"])
p_dev_sold = model_selection.cross_val_predict(clf, Xc_dev_ok, cls_dev["sold_30d"], cv=5, method="predict_proba")[:, 1]
p_test_sold = clf.predict_proba(Xc_test)[:, 1]
y_cd, y_ct = cls_dev["sold_30d"].to_numpy(), cls_test["sold_30d"].to_numpy()
dm = dummy.DummyClassifier(strategy="prior").fit(Xc_dev_ok, y_cd)
print(f"sold rate: development {y_cd.mean():.3f}, test {y_ct.mean():.3f}")
print(f"test AUC: model {metrics.roc_auc_score(y_ct, p_test_sold):.3f} | dummy {metrics.roc_auc_score(y_ct, dm.predict_proba(Xc_test)[:, 1]):.3f}")
print(f"test average precision {metrics.average_precision_score(y_ct, p_test_sold):.3f} (random = {y_ct.mean():.3f})")
```
```text
sold rate: development 0.531, test 0.530
test AUC: model 0.709 | dummy 0.500
test average precision 0.730 (random = 0.530)
```

### 10.2 What `cv=5` means for classifiers and regressors

Passing an integer to `cross_val_score` or a search is **not** the same for every estimator: for a classifier it means `StratifiedKFold` (class proportions kept) and for a regressor `KFold`; neither shuffles. If your rows are ordered (by time, by customer) an unshuffled fold is a contiguous block, which can be good (time) or bad (sorted by label). Say what you want: pass a splitter object.

> **Predict the output.** A table is sorted by the label (all 0s first, then all 1s). What share of positives lands in the test part of the first fold under `KFold(5)` without shuffling, and under `StratifiedKFold(5)`?

<details><summary>Answer</summary>

`KFold(5)` takes a contiguous block, so the first test fold holds only 0s: the share of positives is **0.0**. `StratifiedKFold(5)` keeps the class mix in every fold: about **0.53**, the overall rate. This is why an integer `cv=5` is not harmless on ordered data.

</details>

```python run
y_sorted = np.sort(y_cd)                                        # a table sorted by the label: the worst case
print("first fold of KFold(5) without shuffle  : share positive in test fold =", round(float(y_sorted[: len(y_sorted) // 5].mean()), 3))
print("first fold of StratifiedKFold(5)        : share positive in test fold =",
      round(float(y_sorted[next(model_selection.StratifiedKFold(5).split(np.zeros((len(y_sorted), 1)), y_sorted))[1]].mean()), 3))
```
```text
first fold of KFold(5) without shuffle  : share positive in test fold = 0.0
first fold of StratifiedKFold(5)        : share positive in test fold = 0.53
```

### 10.3 Tuning the decision threshold with `TunedThresholdClassifierCV`

ds.04 chose the threshold by hand from a cost. scikit-learn has a meta-estimator for it: `TunedThresholdClassifierCV` wraps a classifier, finds the threshold that maximises a **scorer** using cross-validation, and then makes `predict` use that threshold. It does the "choose on out-of-fold predictions, never on the training fit" logic for you.

The business rule: if we predict "will sell" and it does not, we have promised a seller something false (cost 3). If we predict "will not sell" for a car that does sell, we wasted a promotion (cost 1).

```python run
def cost_per_listing(y_true, y_pred):
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))
    return -(3 * fp + 1 * fn) / len(y_true)                      # negative: scikit-learn maximises scores

cost_scorer = metrics.make_scorer(cost_per_listing)
tuned = model_selection.TunedThresholdClassifierCV(clf, scoring=cost_scorer, cv=5, refit=True, random_state=0).fit(Xc_dev_ok, y_cd)
print("tuned threshold:", round(float(tuned.best_threshold_), 3), "| best CV score (negative cost):", round(float(tuned.best_score_), 4))
for name, pred in [("threshold 0.5 (default predict)", clf.predict(Xc_test)), (f"tuned threshold {tuned.best_threshold_:.2f}", tuned.predict(Xc_test)),
                   ("always predict 'will sell'", np.ones(len(y_ct), int)), ("always predict 'will not sell'", np.zeros(len(y_ct), int))]:
    print(f"{name:34s} cost per listing on TEST: {-cost_per_listing(y_ct, pred):.3f}")
```
```text
tuned threshold: 0.73 | best CV score (negative cost): -0.4998
threshold 0.5 (default predict)    cost per listing on TEST: 0.746
tuned threshold 0.73               cost per listing on TEST: 0.494
always predict 'will sell'         cost per listing on TEST: 1.410
always predict 'will not sell'     cost per listing on TEST: 0.530
```

`FixedThresholdClassifier(clf, threshold=0.3)` is the sibling for a threshold you decided in advance. Both keep the threshold **inside the estimator**, so the saved model and the served model use the same rule (ds.04 section 14).

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot cost per listing against decision threshold from 0 to 1 for a classifier predicting whether a car sells in 30 days. A false positive costs 3 and a false negative costs 1. Mark threshold 0.5 (test cost 0.746) and the tuned threshold 0.73 (test cost 0.494). Add horizontal reference lines for always predicting sell (1.410) and never sell (0.530). Sketch a smooth U-shaped curve with its minimum near 0.73."

### 10.4 Calibration with `CalibratedClassifierCV`

The wrapper from ds.04 section 11 fits the calibration map on data the base model did not train on.

```python run
from sklearn import calibration
cal = calibration.CalibratedClassifierCV(clf, method="sigmoid", cv=5).fit(Xc_dev_ok, y_cd)
p_cal = cal.predict_proba(Xc_test)[:, 1]
print(f"Brier score  raw {metrics.brier_score_loss(y_ct, p_test_sold):.4f} | calibrated {metrics.brier_score_loss(y_ct, p_cal):.4f}")
frac_pos, mean_pred = calibration.calibration_curve(y_ct, p_cal, n_bins=5, strategy="quantile")
print(pd.DataFrame({"predicted": mean_pred, "observed": frac_pos}).round(3).to_string())
```
```text
Brier score  raw 0.2164 | calibrated 0.2167
   predicted  observed
0     0.2900    0.2750
1     0.4390    0.4500
2     0.5300    0.4940
3     0.6240    0.6190
4     0.7610    0.8120
```

Logistic regression is usually already well calibrated, so the gain here is small. The point is that the wrapper composes with the pipeline: `CalibratedClassifierCV(tuned_pipeline)` is again one estimator.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one calibration (reliability) plot. X axis: mean predicted probability, y axis: observed fraction positive. Plot five points: (0.29, 0.275), (0.439, 0.45), (0.53, 0.494), (0.624, 0.619), (0.761, 0.812). Add the dashed diagonal y = x as perfect calibration. Shade the gap between points and diagonal, and label points above the line as under-confident and points below as over-confident."

### 10.5 Weights through the pipeline

Sample weights (for example, newer rows count more) are passed to the final step by naming it: `pipe.fit(X, y, step__sample_weight=w)`.

```python run
w = np.where(cls_dev["year"] >= 2018, 2.0, 1.0)
weighted = base.clone(clf).fit(Xc_dev_ok, y_cd, lr__sample_weight=w)
print("coefficient on asking_vs_fair, unweighted vs weighted:", round(float(clf["lr"].coef_[0][-1]), 3), round(float(weighted["lr"].coef_[0][-1]), 3))
```
```text
coefficient on asking_vs_fair, unweighted vs weighted: -0.818 -0.829
```

### 10.6 Try it

1. Change the costs to `fp=1, fn=3` and refit `TunedThresholdClassifierCV`. Which way does the threshold move, and why?
2. Replace the cross-fitted feature by the in-sample one **inside the cost comparison**. Is the test cost worse, better or the same?

## 11. Inspecting a fitted pipeline

### 11.1 Coefficients with real names

Because the pipeline remembers the output names of every step, a linear model's coefficients can be read against meaningful columns.

```python run
ridge_final = ridge_model(make_prep(age=True, text=True)).fit(X_dev, y_dev)
names = ridge_final[:-1].get_feature_names_out()
coef = pd.Series(ridge_final["reg"].regressor_.coef_, index=names)
print("log-price coefficients, largest first (a coefficient of -0.2 means about -18% price):")
print(coef.reindex(coef.abs().sort_values(ascending=False).index).head(10).round(3).to_string())
```
```text
log-price coefficients, largest first (a coefficient of -0.2 means about -18% price):
low__brand_BMW            1.0690
low__brand_Maruti        -0.4770
num__year                 0.4020
low__brand_Tata          -0.3920
model_ohe__model_HON-0   -0.3560
model_ohe__model_BMW-3    0.3430
low__brand_Toyota         0.3130
model_ohe__model_HYU-3   -0.3000
model_ohe__model_BMW-5    0.2680
low__brand_Honda         -0.2600
```

(The target is `log(price)`, so a coefficient is roughly a **percentage change** per unit of the standardised feature. Remember that one-hot columns of the same variable and the rest are all relative to each other.)

### 11.2 Permutation importance: on the raw columns, on held-out data

**Permutation importance** shuffles one column and measures how much the score drops. Because the pipeline takes the **raw table**, we can shuffle raw columns such as `mileage_km` or `description`, no matter how many processed columns each became. Always compute it on **held-out** data; on training data an overfit model shows importance for noise.

```python run
inner_tr, inner_va = model_selection.train_test_split(dev, test_size=0.25, random_state=3)
fit_pipe = pipeline.Pipeline([("prep", final_prep()), ("reg", tt(ensemble.HistGradientBoostingRegressor(random_state=0)))]).fit(inner_tr[features], inner_tr[target])
pi = inspection.permutation_importance(fit_pipe, inner_va[features], inner_va[target], n_repeats=8, random_state=0,
                                       scoring="neg_mean_absolute_error")
imp = pd.DataFrame({"mean MAE increase": pi.importances_mean, "std": pi.importances_std}, index=features).sort_values("mean MAE increase", ascending=False)
print(imp.round(3).to_string())
```
```text
              mean MAE increase    std
brand                    2.2300 0.0700
year                     1.8500 0.0590
model                    0.3540 0.0080
mileage_km               0.2250 0.0170
fuel                     0.2090 0.0080
description              0.0720 0.0070
owners                   0.0460 0.0060
transmission             0.0380 0.0080
listed_on                0.0060 0.0030
engine_cc                0.0010 0.0030
city                     0.0000 0.0010
```

Reading it: the columns that raise the error most when shuffled are the ones the model leans on. In our price rule the biggest effects are brand and year, then model, mileage and fuel, and the description (accident history) is small but clearly above zero. Columns at zero are not used (`city`, `engine_cc`, and `listed_on`, which the generator ignores). Note that `brand` looks stronger than `model` partly because each car model belongs to one brand, so shuffling `brand` also scrambles that information. Caveat: when two columns carry the same information (year and age at listing), shuffling one is partly covered by the other, so each looks less important than together.

### 11.3 Partial dependence: the model's average response

A **partial dependence** curve shows the model's average prediction as one feature takes a range of values, with the others left as they are in the data.

```python run
va_filled = inner_va[features].assign(mileage_km=inner_va["mileage_km"].fillna(inner_tr["mileage_km"].median()))   # the grid is built from percentiles, so remove NaN first
pdp = inspection.partial_dependence(fit_pipe, va_filled, features=["mileage_km"], kind="average", grid_resolution=6)
print(pd.DataFrame({"mileage_km": pdp["grid_values"][0], "average predicted price (lakh)": pdp["average"][0]}).round(2).to_string(index=False))
```
```text
  mileage_km  average predicted price (lakh)
 14,300.0000                          5.2100
 52,705.2000                          4.8700
 91,110.4000                          4.5000
129,515.6000                          4.3100
167,920.8000                          4.1100
206,326.0000                          3.9800
```

The curve falls with mileage, as the generating rule says (about 0.0000022 per km in the exponent). Partial dependence averages over other columns and can mislead when features are strongly correlated; it describes the *model*, not the world.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one partial dependence plot for a used-car price model. X axis: mileage_km at six grid points (14,300; 52,705; 91,110; 129,516; 167,921; 206,326). Y axis: average predicted price in lakh (5.21, 4.87, 4.50, 4.31, 4.11, 3.98). Draw the falling line with markers, and add a small side panel showing how the model re-predicts every row with mileage forced to one grid value, then averages."

### 11.4 Seeing the whole pipeline

`print(pipe)` gives a text diagram. In a notebook, `sklearn.set_config(display="diagram")` draws a clickable one. `pipe.get_params(deep=True)` lists every tunable name; `pipe[:-1].transform(X)` shows the exact matrix the model sees.

```python run
processed = ridge_final[:-1].transform(X_dev.head(3))
print("matrix given to the model:", processed.shape, "(rows, columns) -> type", type(processed).__name__)
print("some text feature names:", [n for n in names if n.startswith("text")][:6])
```
```text
matrix given to the model: (3, 120) (rows, columns) -> type ndarray
some text feature names: ['text__ac', 'text__ac works', 'text__accident', 'text__accident ac', 'text__accident full', 'text__accident good']
```

### 11.5 Try it

1. Compute permutation importance on the **training** rows instead of held-out rows. Does any ignored column (like `city`) get a larger score?
2. Compute the partial dependence for `year`. Is the curve monotone?

## 12. Saving, loading and serving

### 12.1 What is saved

You save the **whole fitted pipeline**, from raw columns to prediction (ds.04 section 14). The standard tool is `joblib`, which stores NumPy arrays efficiently.

### 12.2 Custom classes must live in a module

Pickle stores a class only by **name** (`carlib.CarAge`), not by its code. A class defined in a notebook cell or in the script's `__main__` cannot be found by another program. So custom transformers belong in an importable module that both the training and the serving code import.

```python run
lib_dir = pathlib.Path(tempfile.mkdtemp())
(lib_dir / "carlib.py").write_text('''
import numpy as np
import pandas as pd
from sklearn import base
from sklearn.utils.validation import check_is_fitted

class CarAge(base.BaseEstimator, base.TransformerMixin):
    """From columns [year, listed_on, mileage_km] make age at listing and kilometres per year."""
    def fit(self, X, y=None):
        self.feature_names_in_ = np.asarray(X.columns, dtype=object)
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        check_is_fitted(self, "n_features_in_")
        listed_year = pd.to_datetime(X["listed_on"]).dt.year
        age = (listed_year - X["year"]).clip(lower=0)
        return pd.DataFrame({"age_at_listing": age, "km_per_year": X["mileage_km"] / age.clip(lower=1)}, index=X.index)

    def get_feature_names_out(self, input_features=None):
        return np.array(["age_at_listing", "km_per_year"], dtype=object)
''', encoding="utf-8")
sys.path.insert(0, str(lib_dir))
import carlib, joblib

def build_servable():
    prep = compose.ColumnTransformer([
        ("num", pipeline.make_pipeline(impute.SimpleImputer(strategy="median", add_indicator=True), preprocessing.StandardScaler()), num_cols),
        ("low", pipeline.make_pipeline(impute.SimpleImputer(strategy="most_frequent"), preprocessing.OneHotEncoder(handle_unknown="ignore")), low_cat),
        ("model_ohe", preprocessing.OneHotEncoder(handle_unknown="ignore", min_frequency=0.01), ["model"]),
        ("age", pipeline.make_pipeline(carlib.CarAge(), impute.SimpleImputer(strategy="median"), preprocessing.StandardScaler()), ["year", "listed_on", "mileage_km"]),
        ("text", feature_extraction.text.TfidfVectorizer(ngram_range=(1, 2), min_df=10), "description"),
    ], remainder="drop", sparse_threshold=0)
    return pipeline.Pipeline([("prep", prep), ("reg", tt(ensemble.HistGradientBoostingRegressor(random_state=0)))])

servable = build_servable().fit(X_dev, y_dev)
art = lib_dir / "car_price_model.joblib"
joblib.dump(servable, art)
print("saved:", art.name, f"({art.stat().st_size / 1024:.0f} KB)")
meta = {"sklearn": sklearn.__version__, "python": platform.python_version(), "n_features_in": int(servable.n_features_in_),
        "columns": list(servable.feature_names_in_), "trained_rows": int(len(X_dev))}
(lib_dir / "car_price_model.meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
print("sidecar metadata:", json.dumps(meta)[:200], "...")
```
```text
saved: car_price_model.joblib (381 KB)
sidecar metadata: {"sklearn": "1.9.1", "python": "3.14.4", "n_features_in": 11, "columns": ["brand", "model", "year", "mileage_km", "fuel", "transmission", "engine_cc", "owners", "city", "listed_on", "description"], "t ...
```

### 12.3 Loading in a fresh process, one request

The proof that saving works is a **different Python process** that has never seen the training code. The serving script below imports only `joblib`, `pandas` and the same `carlib` module.

```python run
import subprocess
serve_py = lib_dir / "serve.py"
serve_py.write_text('''
import sys, json
sys.path.insert(0, sys.argv[1])
import joblib, pandas as pd

model = joblib.load(sys.argv[1] + "/car_price_model.joblib")
meta = json.load(open(sys.argv[1] + "/car_price_model.meta.json", encoding="utf-8"))

def predict_one(record):
    missing = [c for c in meta["columns"] if c not in record]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    row = pd.DataFrame([{c: record[c] for c in meta["columns"]}])        # named columns, in the training order
    return float(model.predict(row)[0])

record = {"brand": "Hyundai", "model": "HYU-2", "year": 2019, "mileage_km": 46100.0, "fuel": "petrol", "transmission": "manual",
          "engine_cc": 800.0, "owners": 2, "city": "Mumbai", "listed_on": "2024-02-05", "description": "no accident new tyres"}
print("price estimate (lakh):", round(predict_one(record), 3))
try:
    predict_one({k: v for k, v in record.items() if k != "year"})
except ValueError as e:
    print("bad request rejected:", e)
''', encoding="utf-8")
res = subprocess.run([sys.executable, "-I", str(serve_py), str(lib_dir)], capture_output=True, text=True, timeout=120, encoding="utf-8")
print(res.stdout.strip() or res.stderr.strip()[-800:])
print("same row in this process:", round(float(servable.predict(X_dev.iloc[[0]].assign(**{"brand": "Hyundai", "model": "HYU-2", "year": 2019, "mileage_km": 46100.0, "fuel": "petrol", "transmission": "manual", "engine_cc": 800.0, "owners": 2, "city": "Mumbai", "listed_on": "2024-02-05", "description": "no accident new tyres"}))[0]), 3))
```
```text
price estimate (lakh): 3.751
bad request rejected: missing fields: ['year']
same row in this process: 3.751
```

### 12.4 The equivalence test

```python run
sample = X_test.head(100)
batch = servable.predict(sample)
one_by_one = np.array([servable.predict(sample.iloc[[i]])[0] for i in range(len(sample))])
reloaded = joblib.load(art).predict(sample)
print("max |batch - one-at-a-time| :", float(np.abs(batch - one_by_one).max()))
print("max |batch - reloaded file| :", float(np.abs(batch - reloaded).max()))
assert np.allclose(batch, one_by_one) and np.allclose(batch, reloaded)
print("equivalence test passed")
```
```text
max |batch - one-at-a-time| : 0.0
max |batch - reloaded file| : 0.0
equivalence test passed
```

### 12.5 Rules for artefacts

1. Save the pipeline, a **metadata** file (library versions, column list, training data fingerprint, metrics) and the code version.
2. Load only files you trust: **pickle and joblib can run arbitrary code when loaded.** Never load a model file from an unknown source. (The `skops` library offers a safer format for scikit-learn models; we do not use it here.)
3. A model saved with one scikit-learn version may not load, or may give different results, under another. Pin versions, and check them at load time.
4. Test the artefact from a fresh process before you ship it.

### 12.6 Try it

1. Make `serve.py` print the versions it runs with and compare them to `meta["sklearn"]`. Raise an error if they differ.
2. Send a request with `"fuel": "lpg"` (never seen). Does the model answer? Which component made that safe?

## 13. Debugging pipelines

Almost all pipeline errors fall into a few families. Here is each one, produced on purpose, so you recognise the message.

```python run
def show(label, fn):
    try:
        fn()
        print(f"{label}: no error")
    except Exception as e:
        print(f"{label}: {type(e).__name__}: {str(e).splitlines()[0][:150]}")

good_model = ridge_model(make_prep()).fit(X_dev, y_dev)
bad_missing_col = X_test.drop(columns=["owners"])
show("1. a column the model was trained on is missing", lambda: good_model.predict(bad_missing_col))
show("2. NaN given to a model that cannot take it   ", lambda: linear_model.Ridge().fit(X_dev[["mileage_km"]], y_dev))
show("3. unknown category, encoder not told to ignore", lambda: pipeline.make_pipeline(preprocessing.OneHotEncoder(), linear_model.Ridge()).fit(X_dev[["brand"]], y_dev).predict(pd.DataFrame({"brand": ["Skoda"]})))
show("4. a typo in a parameter name                  ", lambda: good_model.set_params(reg__regressor__alfa=1.0))
show("5. text where numbers are expected             ", lambda: preprocessing.StandardScaler().fit(X_dev[["brand"]]))
show("6. transform before fit                        ", lambda: preprocessing.StandardScaler().transform(np.array([[1.0]])))
show("7. predict with a different column order (named)", lambda: good_model.predict(X_test[X_test.columns[::-1]].head(2)))
show("8. fit with different row counts               ", lambda: linear_model.Ridge().fit(np.zeros((5, 2)), np.zeros(4)))
```
```text
1. a column the model was trained on is missing: ValueError: columns are missing: {'owners'}
2. NaN given to a model that cannot take it   : ValueError: Input X contains NaN.
3. unknown category, encoder not told to ignore: ValueError: Found unknown categories ['Skoda'] in column 0 during transform
4. a typo in a parameter name                  : ValueError: Invalid parameter 'alfa' for estimator Ridge(). Valid parameters are: ['alpha', 'copy_X', 'fit_intercept', 'max_iter', 'positive', 'random_state', 'so
5. text where numbers are expected             : ValueError: could not convert string to float: 'Maruti'
6. transform before fit                        : NotFittedError: This StandardScaler instance is not fitted yet. Call 'fit' with appropriate arguments before using this estimator.
7. predict with a different column order (named): no error
8. fit with different row counts               : ValueError: Found input variables with inconsistent numbers of samples: [5, 4]
```

Observations:

- **1** and **4**: scikit-learn names the thing that is missing or invalid. Read the full message; it lists valid choices.
- **7**: with named columns, a reordered table is **accepted** because the `ColumnTransformer` selects columns by name. With a bare NumPy array it would silently be wrong (ds.04 section 14.2). One more reason to feed DataFrames.
- **3**: the fix is `handle_unknown="ignore"` for one-hot, or an `"infrequent_if_exist"` setting.

### 13.1 Tools for finding the problem

| Tool | Use |
|---|---|
| `pipe[:k].transform(X)` | look at the data after the first `k` steps |
| `pipe[:-1].get_feature_names_out()` | see the column names the model receives |
| `Pipeline(..., verbose=True)` | print the time each step takes while fitting |
| `set_output(transform="pandas")` | get DataFrames with names between steps |
| `check_estimator(est)` | audit a custom class (section 6.4) |
| `model_selection.cross_val_score(..., error_score="raise")` | make a failing fold raise instead of becoming NaN |
| `sklearn.set_config(assume_finite=False)` | keep NaN/inf checks on (the default) |

```python run
import contextlib, io
buf = io.StringIO()
with contextlib.redirect_stderr(buf):
    pipeline.Pipeline([("impute", impute.SimpleImputer()), ("scale", preprocessing.StandardScaler()), ("m", linear_model.Ridge())], verbose=True).fit(X_dev[num_cols], y_dev)
print(buf.getvalue().strip().replace("\n", "\n"))
```
```text
[Pipeline] ............ (step 1 of 3) Processing impute, total=   0.0s
[Pipeline] ............. (step 2 of 3) Processing scale, total=   0.0s
[Pipeline] ................. (step 3 of 3) Processing m, total=   0.0s
```

### 13.2 Silent errors are worse than loud ones

The loud errors above are the easy case. The dangerous bugs run fine and give wrong numbers: preprocessing fitted outside the pipeline, `fit_transform` applied to test data, a `remainder="passthrough"` that lets an ID column in, a `random_state` missing. The defence is the ds.04 toolkit: the shuffled-label test, an equivalence test, and reading `get_feature_names_out()` once, with your eyes, for every new pipeline.

```python run
# a quick audit helper: which columns does the model actually receive?
def audit_inputs(model, raw_columns):
    seen = list(model[:-1].get_feature_names_out())
    dropped = [c for c in raw_columns if not any(c in n for n in seen)]
    return len(seen), dropped
n_seen, dropped = audit_inputs(good_model, features)
print(f"{n_seen} processed columns reach the model; raw columns that contribute nothing: {dropped}")
```
```text
62 processed columns reach the model; raw columns that contribute nothing: ['listed_on', 'description']
```

### 13.3 Try it

1. Add `remainder="passthrough"` to the `ColumnTransformer` and fit on a table that has a text column left over. What error do you get, and why is it a good one?
2. Break `QuantileClipper` on purpose (make `fit` return `None`) and rerun `check_estimator`. Which check names the problem?


## 14. Project: `tabml`, a reusable pipeline for tabular data

### 14.1 The brief

You have now met every piece. The project assembles them into a small library, **`tabml`**, that you can point at any tabular dataset by writing a short config. It must:

1. take a **raw table** (strings, missing values, text) and a **config** naming the role of each column,
2. build one `Pipeline` with leak-free preprocessing, with model choices for regression and classification,
3. train with a sealed test set, compare with a **baseline**, and write a **report** (config, data fingerprint, environment, metrics),
4. save the artefact and serve it through a `Predictor` that validates its input,
5. come with **tests** that guard the ds.04 failures: leaks, non-reproducibility, train/serve skew.

The code below is the whole library, in one file of about 150 lines. Read it once before running it: nothing in it is new, only assembled.

### 14.2 The library

```python run
proj = pathlib.Path(tempfile.mkdtemp()) / "tabml_project"
proj.mkdir()
(proj / "tabml.py").write_text('''"""tabml: a small, leak-free pipeline for tabular data (regression or classification)."""
import dataclasses, hashlib, json, platform
import numpy as np
import pandas as pd
import joblib
import sklearn
from sklearn import (compose, dummy, ensemble, feature_extraction, impute, linear_model, metrics,
                     model_selection, pipeline, preprocessing)


@dataclasses.dataclass
class Config:
    target: str
    numeric: list
    low_cat: list = dataclasses.field(default_factory=list)      # few levels: one-hot
    high_cat: list = dataclasses.field(default_factory=list)     # many levels: cross-fitted target encoding
    text: list = dataclasses.field(default_factory=list)         # free text: tf-idf
    task: str = "regression"                                     # "regression" | "classification"
    model: str = "hgb"                                           # "linear" | "forest" | "hgb"
    log_target: bool = False                                     # regression only
    seed: int = 0
    test_size: float = 0.2

    @property
    def features(self):
        return list(self.numeric) + list(self.low_cat) + list(self.high_cat) + list(self.text)


def make_estimator(cfg):
    reg = cfg.task == "regression"
    if cfg.model == "linear":
        est = linear_model.Ridge(alpha=1.0) if reg else linear_model.LogisticRegression(max_iter=3000)
    elif cfg.model == "forest":
        kw = dict(n_estimators=150, min_samples_leaf=3, random_state=cfg.seed, n_jobs=1)
        est = ensemble.RandomForestRegressor(**kw) if reg else ensemble.RandomForestClassifier(**kw)
    elif cfg.model == "hgb":
        est = (ensemble.HistGradientBoostingRegressor if reg else ensemble.HistGradientBoostingClassifier)(random_state=cfg.seed)
    else:
        raise ValueError(f"unknown model {cfg.model!r}; choose linear, forest or hgb")
    if reg and cfg.log_target:
        est = compose.TransformedTargetRegressor(regressor=est, func=np.log, inverse_func=np.exp)
    return est


def build_pipeline(cfg):
    parts = []
    if cfg.numeric:
        parts.append(("num", pipeline.make_pipeline(impute.SimpleImputer(strategy="median", add_indicator=True), preprocessing.StandardScaler()), list(cfg.numeric)))
    if cfg.low_cat:
        parts.append(("low", pipeline.make_pipeline(impute.SimpleImputer(strategy="most_frequent"), preprocessing.OneHotEncoder(handle_unknown="ignore")), list(cfg.low_cat)))
    if cfg.high_cat:
        te = preprocessing.TargetEncoder(target_type="continuous" if cfg.task == "regression" else "binary", random_state=cfg.seed)
        parts.append(("high", te, list(cfg.high_cat)))
    for col in cfg.text:                                          # one vectoriser per text column
        parts.append((f"text_{col}", feature_extraction.text.TfidfVectorizer(ngram_range=(1, 2), min_df=5), col))
    prep = compose.ColumnTransformer(parts, remainder="drop", sparse_threshold=0)
    return pipeline.Pipeline([("prep", prep), ("model", make_estimator(cfg))])


def fingerprint(df):
    h = hashlib.sha256(",".join(map(str, df.columns)).encode())
    h.update(pd.util.hash_pandas_object(df, index=False).to_numpy().tobytes())
    return h.hexdigest()[:16]


def _scores(cfg, y_true, pred):
    if cfg.task == "regression":
        return {"mae": float(metrics.mean_absolute_error(y_true, pred)), "r2": float(metrics.r2_score(y_true, pred))}
    return {"auc": float(metrics.roc_auc_score(y_true, pred)), "average_precision": float(metrics.average_precision_score(y_true, pred)),
            "brier": float(metrics.brier_score_loss(y_true, pred))}


def _predict(cfg, model, X):
    return model.predict(X) if cfg.task == "regression" else model.predict_proba(X)[:, 1]


def train(cfg, df):
    """Split, cross-validate on the development part, fit, score the sealed test part ONCE. Returns (model, report)."""
    missing = [c for c in cfg.features + [cfg.target] if c not in df.columns]
    if missing:
        raise ValueError(f"columns not in the data: {missing}")
    clf = cfg.task == "classification"
    dev, test = model_selection.train_test_split(df, test_size=cfg.test_size, random_state=cfg.seed, stratify=df[cfg.target] if clf else None)
    Xd, yd, Xt, yt = dev[cfg.features], dev[cfg.target], test[cfg.features], test[cfg.target]
    scoring = "roc_auc" if clf else "neg_mean_absolute_error"
    cv = (model_selection.StratifiedKFold if clf else model_selection.KFold)(5, shuffle=True, random_state=cfg.seed)
    cv_model = model_selection.cross_val_score(build_pipeline(cfg), Xd, yd, cv=cv, scoring=scoring)
    base_est = dummy.DummyClassifier(strategy="prior") if clf else dummy.DummyRegressor(strategy="mean")
    baseline = pipeline.Pipeline([("prep", build_pipeline(cfg)["prep"]), ("model", base_est)]).fit(Xd, yd)
    model = build_pipeline(cfg).fit(Xd, yd)
    report = {
        "config": dataclasses.asdict(cfg),
        "data": {"fingerprint": fingerprint(df), "rows": len(df), "train_rows": len(dev), "test_rows": len(test)},
        "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__, "pandas": pd.__version__},
        "cv_dev": {"metric": scoring, "mean": float(cv_model.mean()), "std": float(cv_model.std(ddof=1))},
        "test": _scores(cfg, yt, _predict(cfg, model, Xt)),
        "test_baseline": _scores(cfg, yt, _predict(cfg, baseline, Xt)),
    }
    return model, report


def save(model, report, folder):
    folder = __import__("pathlib").Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, folder / "model.joblib")
    (folder / "report.json").write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")


class Predictor:
    """Loads a saved model and serves it with validated, named inputs."""
    def __init__(self, folder):
        folder = __import__("pathlib").Path(folder)
        self.model = joblib.load(folder / "model.joblib")
        self.report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
        self.cfg = Config(**self.report["config"])
        if self.report["environment"]["sklearn"] != sklearn.__version__:
            raise RuntimeError(f"model trained with scikit-learn {self.report['environment']['sklearn']}, running {sklearn.__version__}")

    def predict(self, df):
        missing = [c for c in self.cfg.features if c not in df.columns]
        if missing:
            raise ValueError(f"missing input columns: {missing}")
        return _predict(self.cfg, self.model, df[self.cfg.features])

    def predict_one(self, record):
        return float(self.predict(pd.DataFrame([record]))[0])
''', encoding="utf-8")
print("wrote", (proj / "tabml.py").name, "-", len((proj / "tabml.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
wrote tabml.py - 126 lines
```

Design choices worth noticing:

- `high_cat` exists for columns with hundreds of levels; the 36 car models are few enough for `low_cat` (section 7.3, row F).
- **One config object** names every column's role. There is no `remainder="passthrough"`: a new column in the data cannot silently reach the model.
- The baseline is built with **the same preprocessing** and a dummy model, so "beats the baseline" compares like with like.
- `train` touches the test set once, at the end. Cross-validation uses only the development part.
- `Predictor` checks column names and the scikit-learn version, and exposes `predict_one` for a single record.
- Randomness is controlled by `cfg.seed` everywhere (split, folds, models, encoders).

### 14.3 Using it on two different problems

The same code handles both targets of our listings table.

```python run
sys.path.insert(0, str(proj))
import importlib, tabml
importlib.reload(tabml)

reg_cfg = tabml.Config(target="price_lakh", numeric=["year", "mileage_km", "engine_cc", "owners"], low_cat=["brand", "fuel", "transmission", "city", "model"],
                       text=["description"], task="regression", model="hgb", log_target=True)
reg_model, reg_report = tabml.train(reg_cfg, cars.drop(columns=["asking_lakh", "sold_30d", "listed_on"]))
print("REGRESSION report (rounded):")
print(json.dumps({k: reg_report[k] for k in ["data", "cv_dev", "test", "test_baseline"]}, indent=1, default=lambda v: round(v, 4)))
```
```text
REGRESSION report (rounded):
{
 "data": {
  "fingerprint": "ed5cd267fbd8050c",
  "rows": 4000,
  "train_rows": 3200,
  "test_rows": 800
 },
 "cv_dev": {
  "metric": "neg_mean_absolute_error",
  "mean": -0.4647810038031066,
  "std": 0.028185990301498907
 },
 "test": {
  "mae": 0.47798945667064857,
  "r2": 0.9685822615191467
 },
 "test_baseline": {
  "mae": 3.296430328125,
  "r2": -0.0016665849888188866
 }
}
```

```python run
clf_cfg = tabml.Config(target="sold_30d", numeric=["year", "mileage_km", "owners", "asking_lakh"], low_cat=["brand", "fuel", "transmission", "city", "model"],
                       text=["description"], task="classification", model="hgb")
clf_model, clf_report = tabml.train(clf_cfg, cars.drop(columns=["price_lakh", "listed_on"]))
print("CLASSIFICATION report (rounded):")
print(json.dumps({k: clf_report[k] for k in ["cv_dev", "test", "test_baseline"]}, indent=1, default=lambda v: round(v, 4)))
```
```text
CLASSIFICATION report (rounded):
{
 "cv_dev": {
  "metric": "roc_auc",
  "mean": 0.5776852484891878,
  "std": 0.021813515666179572
 },
 "test": {
  "auc": 0.5861413588920112,
  "average_precision": 0.6087565225372296,
  "brier": 0.2535099264404102
 },
 "test_baseline": {
  "auc": 0.5,
  "average_precision": 0.53,
  "brier": 0.24910039062499997
 }
}
```

(Look at the classifier honestly: its AUC is only modestly above the dummy's 0.5 (about 0.59). The signal for "will it sell" is the asking price **relative to the fair price** (section 10), and a config that lists only raw columns cannot express a ratio to another model's output. The pipeline did its job; the *features* limit the result, and the baseline in the report is what makes that visible. A lesser tool would have printed a bare AUC and let you believe it was fine.)

Compare model families by changing one word in the config:

```python run
rows = []
for m in ["linear", "forest", "hgb"]:
    cfg = tabml.Config(**{**reg_cfg.__dict__, "model": m})
    t0 = time.perf_counter()
    _, rep = tabml.train(cfg, cars.drop(columns=["asking_lakh", "sold_30d", "listed_on"]))
    rows.append((m, rep["cv_dev"]["mean"] * -1, rep["cv_dev"]["std"], rep["test"]["mae"], rep["test_baseline"]["mae"], time.perf_counter() - t0))
print(pd.DataFrame(rows, columns=["model", "dev CV MAE", "fold std", "test MAE", "baseline test MAE", "seconds"]).set_index("model").round(3).to_string())
print("(the linear model with a log target wins again: the price rule is log-linear, as section 8 found)")
```
```text
        dev CV MAE  fold std  test MAE  baseline test MAE  seconds
model                                                             
linear      0.3960    0.0140    0.4060             3.2960   0.2860
forest      0.6490    0.0320    0.6650             3.2960  13.3920
hgb         0.4650    0.0280    0.4780             3.2960   2.4020
(the linear model with a log target wins again: the price rule is log-linear, as section 8 found)
```

### 14.4 Save, load, serve

```python run
tabml.save(reg_model, reg_report, proj / "artefact")
pred = tabml.Predictor(proj / "artefact")
record = {"brand": "Toyota", "model": "TOY-1", "year": 2020, "mileage_km": 38000.0, "fuel": "hybrid", "transmission": "automatic",
          "engine_cc": 1500.0, "owners": 1, "city": "Pune", "description": "single owner full service record no accident"}
print("predicted price (lakh):", round(pred.predict_one(record), 2))
for label, bad in [("missing field", {k: v for k, v in record.items() if k != "year"}), ("unseen city and model", {**record, "city": "Goa", "model": "TOY-99"})]:
    try:
        print(f"{label}: ->", round(pred.predict_one(bad), 2))
    except ValueError as e:
        print(f"{label}: rejected ->", e)
print("artefact files:", sorted(p.name for p in (proj / "artefact").iterdir()))
```
```text
predicted price (lakh): 13.96
missing field: rejected -> missing input columns: ['year']
unseen city and model: -> 13.08
artefact files: ['model.joblib', 'report.json']
```

### 14.5 The tests

A reusable library is only reusable if you can change it without fear. These tests encode the failures of ds.04 and ds.05 as checks that run in seconds.

```python run
(proj / "test_tabml.py").write_text('''import numpy as np, pandas as pd, pytest
import tabml

def make_df(n=600, seed=0):
    r = np.random.default_rng(seed)
    year = r.integers(2008, 2024, n)
    brand = r.choice(["A", "B", "C"], n)
    model = r.choice([f"m{i}" for i in range(12)], n)
    km = np.where(r.random(n) < 0.1, np.nan, (2024 - year) * 11000 + r.normal(0, 3000, n))
    desc = np.where(r.random(n) < 0.2, "accident history", "no accident")
    price = (5 + 2 * (brand == "B")) * np.exp(-0.08 * (2024 - year)) * np.where(desc == "accident history", 0.85, 1.0) * np.exp(r.normal(0, 0.05, n))
    sold = (r.random(n) < 1 / (1 + np.exp(-(1 - 0.15 * (2024 - year))))).astype(int)
    return pd.DataFrame(dict(year=year, brand=brand, model=model, km=km, desc=desc, price=price, sold=sold))

CFG = tabml.Config(target="price", numeric=["year", "km"], low_cat=["brand"], high_cat=["model"], text=["desc"], model="forest", log_target=True)

def test_fits_a_raw_table_with_missing_values():
    model, report = tabml.train(CFG, make_df())
    assert report["test"]["r2"] > 0.8, "the model should learn this simple price rule"

def test_beats_the_baseline():
    _, report = tabml.train(CFG, make_df())
    assert report["test"]["mae"] < 0.5 * report["test_baseline"]["mae"], "a model that cannot halve the baseline error is not learning"

def test_reproducible():
    a = tabml.train(CFG, make_df())[1]
    b = tabml.train(CFG, make_df())[1]
    assert a["test"] == b["test"] and a["data"] == b["data"], "same config and data must give identical metrics"

def test_shuffled_labels_give_no_skill():
    df = make_df()
    df["price"] = np.random.default_rng(1).permutation(df["price"].to_numpy())
    _, report = tabml.train(CFG, df)
    assert report["test"]["r2"] < 0.1, "skill on shuffled labels means the pipeline leaks the target"

def test_test_rows_are_never_training_rows():
    df = make_df()
    from sklearn.model_selection import train_test_split
    dev, test = train_test_split(df, test_size=CFG.test_size, random_state=CFG.seed)
    assert not set(dev.index) & set(test.index)

def test_save_load_batch_equals_single(tmp_path):
    df = make_df()
    model, report = tabml.train(CFG, df)
    tabml.save(model, report, tmp_path)
    p = tabml.Predictor(tmp_path)
    batch = p.predict(df.head(25))
    single = np.array([p.predict_one(df.iloc[i][CFG.features].to_dict()) for i in range(25)])
    assert np.allclose(batch, single), "batch and one-at-a-time predictions differ: train/serve skew"

def test_missing_column_is_named(tmp_path):
    df = make_df()
    model, report = tabml.train(CFG, df)
    tabml.save(model, report, tmp_path)
    with pytest.raises(ValueError, match="year"):
        tabml.Predictor(tmp_path).predict(df.drop(columns=["year"]))

def test_unseen_category_does_not_crash(tmp_path):
    df = make_df()
    model, report = tabml.train(CFG, df)
    tabml.save(model, report, tmp_path)
    row = df.iloc[0][CFG.features].to_dict() | {"brand": "Z", "model": "never-seen"}
    assert np.isfinite(tabml.Predictor(tmp_path).predict_one(row))

def test_classification_runs():
    cfg = tabml.Config(target="sold", numeric=["year", "km"], low_cat=["brand"], task="classification", model="linear")
    _, report = tabml.train(cfg, make_df())
    assert report["test"]["auc"] > 0.6
''', encoding="utf-8")
import os
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore::FutureWarning", "test_tabml.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-700:] or res.stderr.strip()[-700:])
```
```text
.........                                                                [100%]
9 passed in 7.89s
```

Each test has a message-bearing assertion that names the failure it guards against. Break the library on purpose to see them work: change `random_state=cfg.seed` in `train_test_split` to `None` and `test_reproducible` fails; move the scaler outside the pipeline in your own variant and `test_shuffled_labels_give_no_skill` can catch the leak.

### 14.6 What to hand in

1. `tabml.py`, `test_tabml.py`, and an example config for **a dataset that is not ours** (choose any CSV you have; a Kaggle-style table works).
2. The report JSON of one regression run and one classification run, with the baseline.
3. A one-paragraph README: what the config roles mean, what is *not* handled (time and group splits, see below), how to run the tests.
4. The audit list from ds.04 section 15.9, answered for your dataset.

### 14.7 Extensions

1. Add a `split="time"` or `groups=` option to `Config` and `train`, using `TimeSeriesSplit`/`GroupKFold`, with the gap of ds.04 section 7.
2. Add `tune=True` which wraps the pipeline in a `RandomizedSearchCV` and reports the nested-CV estimate.
3. Add a threshold option for classifiers using `TunedThresholdClassifierCV` with a cost matrix from the config.
4. Add a `check_inputs` step in `Predictor` that compares each numeric input with the training range and warns (ds.04 section 14.4).
5. Package it with a `pyproject.toml` so `pip install -e .` makes `import tabml` work everywhere (core.13).

## 15. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Fitting preprocessing outside a pipeline | test information leaks into the model | every learned step inside one `Pipeline` (4) |
| `fit_transform` on validation or test data | statistics re-learned, shifts hidden | `fit` once on training rows, then only `transform` (1.4) |
| Putting heavy logic in `__init__` of a custom class | `clone` and grid search break | `__init__` stores arguments only; learn in `fit` (6.1) |
| Forgetting the trailing underscore on learned values | `check_estimator` fails; state leaks into `get_params` | learned attributes end with `_` (1.3) |
| Defining custom classes in the script or notebook | the saved file cannot be loaded elsewhere | put them in an importable module (12.2) |
| `remainder="passthrough"` | a new or ID column silently reaches the model | explicit column roles, `remainder="drop"` (5.4) |
| Using `OneHotEncoder` without `handle_unknown="ignore"` | crash on a new category in production | set it, or group rare levels (3.3) |
| One-hot for a column with hundreds of levels | huge sparse matrix, overfitting | `TargetEncoder` (cross-fitted) or `min_frequency` (3.3) |
| Mean/target encoding computed on all rows | the label leaks into the feature | `TargetEncoder` inside the pipeline (3.3, 7.7) |
| Stage-1 predictions in-sample as stage-2 features | the second model over-trusts a too-clean feature | out-of-fold predictions via `cross_val_predict` or `Stacking*` (10.1) |
| Judging a new feature by the test set | optimistic selection | measure one idea at a time with CV on development data (7.1) |
| Reporting the best score of a search | optimism of a maximum | nested CV or a sealed test set (9.6) |
| Tuning many parameters with a grid | exponential cost, few distinct values per parameter | random or halving search with distributions (9.3, 9.4) |
| Reading only `best_params_` | ties among candidates mistaken for a clear winner | read `cv_results_` and the fold spread (9.2) |
| Integer `cv=5` on ordered data | contiguous blocks or label-sorted folds | pass an explicit splitter (10.2, ds.04) |
| Default 0.5 threshold in a wrapped classifier | wrong trade-off | `TunedThresholdClassifierCV` with a cost scorer (10.3) |
| Permutation importance on training rows | importance for noise features | compute it on held-out data (11.2) |
| Treating partial dependence as causal | model behaviour taken for world behaviour | use it to describe the model only (11.3) |
| Loading a saved model from an untrusted source | pickle can run code | only load your own files; consider `skops` (12.5) |
| Loading under a different scikit-learn version | silent changes or errors | record and check versions at load time (12.5, 14.2) |
| Feeding bare NumPy arrays to a trained pipeline | wrong column order accepted silently | always pass DataFrames with names (13) |
| Not looking at `get_feature_names_out()` | an ID column or a duplicate sneaks in | print it once for every new pipeline (13.2) |

## 16. Summary

- scikit-learn is a **design**: estimators with `fit`; transformers with `transform`; predictors with `predict`. Hyperparameters live in `__init__`; learned values end with `_`; `fit` returns `self`; **`transform` and `predict` never learn**. `get_params`, `set_params` and `clone` make every object tunable and copyable.
- A **`Pipeline`** chains steps into one estimator and makes cross-validation leak-free. A **`ColumnTransformer`** gives each group of columns its own treatment (numeric: impute + scale; categorical: impute + one-hot; many levels: target encoding; text: tf-idf) and accepts the **raw table**. `TransformedTargetRegressor` transforms the target (log) and undoes it on prediction.
- **Your own steps** subclass `BaseEstimator` and `TransformerMixin`, learn in `fit`, apply in `transform`, name their outputs in `get_feature_names_out`, and are audited with `check_estimator`. Keep them in an importable module.
- **Feature engineering** is a measured activity: one idea at a time, compared with cross-validation and its fold spread, every learned step inside the pipeline. Linear models need engineered curves and interactions; trees find many themselves.
- **Compare models fairly** with the same folds and preprocessing (`cross_validate`, several metrics, train scores, custom scorers, paired differences, validation curves, out-of-fold residuals).
- **Tune** with `GridSearchCV` (few combinations), `RandomizedSearchCV` (many, with distributions) and `HalvingRandomSearchCV` (expensive); tune the whole pipeline by double-underscore names; read `cv_results_`; estimate real performance with nested CV or a sealed test set.
- **Wrappers compose**: `TunedThresholdClassifierCV` (cost-based threshold) and `CalibratedClassifierCV` turn a pipeline into a pipeline that decides and speaks in probabilities. Use **out-of-fold** predictions whenever one model's output feeds another.
- **Inspect** with named coefficients, permutation importance on held-out raw columns, and partial dependence, as descriptions of the model.
- **Ship** the whole pipeline with `joblib`, plus metadata and a fresh-process test; pickle is not safe for untrusted files; pin versions. Validate inputs by name and test batch = single = reloaded.
- **`tabml`** packages all of this behind one config, with a baseline in every report and tests for the leaks of ds.04.

You reached the outcome of this chapter: you can **build a single pipeline object that goes from raw data to predictions** (the `Pipeline` of section 5, grown into the artefact of sections 12 and 14), tune it without fooling yourself, and hand it to someone else with a test suite. Next (ds.06) opens the boxes you have been treating as black ones: linear and logistic regression by gradient descent, nearest neighbours, trees, forests, boosting, SVMs, clustering and PCA, each implemented from scratch and matched against scikit-learn.
