# Chapter 3 (DS): Machine learning fundamentals

Machine learning is the practice of letting a computer find a rule from examples instead of writing the rule by hand. Show it thousands of past flats with their prices and it learns a price rule; show it past emails marked spam or not and it learns a spam rule. The hard part is not fitting the rule. Any flexible method can fit the examples it was shown, even perfectly. The hard part is the question that decides whether the work is worth anything: **will the rule still work on examples it has never seen?**

This chapter is about that question. You will learn the vocabulary (supervised and unsupervised learning, features and targets), the one danger that haunts every model (**overfitting**), the trade-off behind it (**bias and variance**), the main cure (**regularisation**), and the discipline that keeps you honest (**train, validation and test splits, and cross-validation**). Then you learn to measure a model with the right numbers: the **metrics** for regression and for classification, and why a model that is "95% accurate" can be useless. By the end you reach the outcome of the syllabus: **you can explain overfitting using a learning curve**, with your own experiment as evidence. The project builds a small **model evaluation framework** that you will reuse for the rest of the data-science track.

Prerequisites: ds.02 (regression, train/test idea, coefficients) and ds.01 (gradients, the bootstrap, probability). If a formula looks unfamiliar, the code beside it computes it from scratch before using a library.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, pandas, scikit-learn and matplotlib-free text output. Data are either **synthetic** (seeded random numbers from a known rule, so we can check what the model recovers) or **ship inside scikit-learn** (`load_diabetes`, `load_breast_cancer`); nothing is downloaded. Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, warnings
import numpy as np
import pandas as pd
import sklearn
from sklearn import datasets, linear_model, metrics, model_selection, preprocessing, pipeline, dummy, neighbors, tree, ensemble, cluster, decomposition

np.set_printoptions(precision=4, suppress=True, linewidth=110)
pd.set_option("display.width", 120)
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
warnings.filterwarnings("ignore", category=UserWarning)
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

1. [What machine learning is, and the two families](#1-what-machine-learning-is-and-the-two-families)
2. [The shape of a supervised problem](#2-the-shape-of-a-supervised-problem)
3. [Baselines: the model you must beat](#3-baselines-the-model-you-must-beat)
4. [Train, validation and test](#4-train-validation-and-test)
5. [Overfitting and underfitting](#5-overfitting-and-underfitting)
6. [The bias-variance trade-off](#6-the-bias-variance-trade-off)
7. [Learning curves](#7-learning-curves)
8. [Regularisation](#8-regularisation)
9. [Cross-validation](#9-cross-validation)
10. [Choosing hyperparameters without cheating](#10-choosing-hyperparameters-without-cheating)
11. [Metrics for regression](#11-metrics-for-regression)
12. [Metrics for classification](#12-metrics-for-classification)
13. [Unsupervised learning: finding structure without labels](#13-unsupervised-learning-finding-structure-without-labels)
14. [Project: a model evaluation framework](#14-project-a-model-evaluation-framework)
15. [Common traps](#15-common-traps)
16. [Summary](#16-summary)

## 1. What machine learning is, and the two families

### 1.1 Learning a rule from examples

Ordinary programming takes **rules and data** and produces **answers**. Machine learning takes **data and answers** and produces **rules** (a *model*), which we then apply to new data.

| | Input | Output |
|---|---|---|
| Programming | rules + data | answers |
| Machine learning (training) | data + answers | a model (the rules) |
| Machine learning (prediction) | model + new data | predicted answers |

### 1.2 Supervised and unsupervised learning

- **Supervised learning**: every training example comes with the right answer (a **label** or **target**). The model learns to predict the answer from the other columns (the **features**). When the target is a number (price, temperature) the task is **regression**; when it is a category (spam or not, which of five species) it is **classification**.
- **Unsupervised learning**: there is no target. The model looks for **structure** in the features alone: groups of similar rows (**clustering**), a few directions that carry most of the variation (**dimensionality reduction**, such as the PCA of ds.01), or rows that do not fit (anomalies).

A third family, **reinforcement learning** (learning from reward by trial and error), is outside this course. Most business machine learning is supervised, and most of this chapter is too.

```python run
tasks = pd.DataFrame([
    ("Predict the price of a flat", "supervised", "regression", "flat price in rupees"),
    ("Will this customer cancel next month?", "supervised", "classification", "cancelled yes/no"),
    ("Which of 3 species is this flower?", "supervised", "classification (3 classes)", "species"),
    ("Group customers into segments", "unsupervised", "clustering", "none"),
    ("Compress 50 columns to 3", "unsupervised", "dimensionality reduction", "none"),
    ("Spot unusual card transactions", "unsupervised (or supervised)", "anomaly detection", "none, or fraud yes/no if known"),
], columns=["task", "family", "type", "target"])
print(tasks.to_string(index=False))
```
```text
                                 task                       family                       type                         target
          Predict the price of a flat                   supervised                 regression           flat price in rupees
Will this customer cancel next month?                   supervised             classification               cancelled yes/no
   Which of 3 species is this flower?                   supervised classification (3 classes)                        species
        Group customers into segments                 unsupervised                 clustering                           none
             Compress 50 columns to 3                 unsupervised   dimensionality reduction                           none
       Spot unusual card transactions unsupervised (or supervised)          anomaly detection none, or fraud yes/no if known
```

## 2. The shape of a supervised problem

### 2.1 Features, target, and the matrix

A supervised dataset is a table. One column is the **target** `y` (what we want to predict); the other columns are the **features** and form the matrix `X` of ds.01 (one row per example, one column per feature). The model is a function `ŷ = f(X)`. Training means choosing `f`, from a family of possible functions, so that `ŷ` is close to `y` on the data we have. A well-chosen name for the goal: **generalisation**, being right on data we have *not* seen.

We use a real dataset that ships with scikit-learn: 442 diabetes patients, ten baseline measurements (age, sex, body-mass index, blood pressure and six blood-serum values, already standardised) and a measure of disease progression one year later.

```python run
data = datasets.load_diabetes(as_frame=True)
X_all, y_all = data.data, data.target
print("X shape:", X_all.shape, "| y shape:", y_all.shape)
print("features:", list(X_all.columns))
print(X_all.head(3).round(3).to_string())
print("\ntarget (disease progression after a year): mean", round(float(y_all.mean()), 1), "| SD", round(float(y_all.std()), 1), "| range", y_all.min(), "to", y_all.max())
print("correlation of each feature with the target:")
print(X_all.corrwith(y_all).sort_values(ascending=False).round(3).to_string())
```
```text
X shape: (442, 10) | y shape: (442,)
features: ['age', 'sex', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
      age     sex     bmi      bp      s1      s2      s3      s4      s5      s6
0  0.0380  0.0510  0.0620  0.0220 -0.0440 -0.0350 -0.0430 -0.0030  0.0200 -0.0180
1 -0.0020 -0.0450 -0.0510 -0.0260 -0.0080 -0.0190  0.0740 -0.0390 -0.0680 -0.0920
2  0.0850  0.0510  0.0440 -0.0060 -0.0460 -0.0340 -0.0320 -0.0030  0.0030 -0.0260

target (disease progression after a year): mean 152.1 | SD 77.1 | range 25.0 to 346.0
correlation of each feature with the target:
bmi    0.5860
s5     0.5660
bp     0.4410
s4     0.4300
s6     0.3820
s1     0.2120
age    0.1880
s2     0.1740
sex    0.0430
s3    -0.3950
```

### 2.2 A model is a family plus a fitting rule

Two choices define every model in this chapter. The **model family** (a straight line, a decision tree, nearest neighbours) fixes the shapes the model can take. The **fitting rule** (least squares, a split criterion) picks one shape from the family using the training data. Parameters the fitting rule finds (the coefficients of a line) are **parameters**. Settings that *you* choose before fitting (the depth of a tree, the strength of a penalty, the number of neighbours) are **hyperparameters**, and choosing them well is half of practical machine learning (section 10).

scikit-learn gives every model the same interface: `fit(X, y)` to learn, `predict(X)` to apply, and `score` for a default metric. Learn this interface once and every model follows.

```python run
model = linear_model.LinearRegression()
model.fit(X_all, y_all)
pred = model.predict(X_all.iloc[:5])
print("first 5 predictions:", pred.round(1))
print("first 5 true values:", y_all.iloc[:5].values)
print("intercept", round(float(model.intercept_), 2), "| coefficients:", model.coef_.round(1))
```
```text
first 5 predictions: [206.1  68.1 176.9 166.9 128.5]
first 5 true values: [151.  75. 141. 206. 135.]
intercept 152.13 | coefficients: [ -10.  -239.8  519.8  324.4 -792.2  476.7  101.   177.1  751.3   67.6]
```

These predictions were made on the **same rows** the model was fitted on. That is the trap this whole chapter is about: how good a model looks on its own training data tells you little about how good it will be on new data.

## 3. Baselines: the model you must beat

### 3.1 The dumbest sensible model

Before judging any model ask: *compared with what?* A **baseline** is a trivial model whose score any real model must beat. For regression the simplest baseline predicts the training mean for everyone; for classification, the most common class. If your clever model does not beat it, the clever model has learned nothing.

```python run
X_tr, X_te, y_tr, y_te = model_selection.train_test_split(X_all, y_all, test_size=0.25, random_state=0)
print("train rows:", len(X_tr), "| test rows:", len(X_te))

base = dummy.DummyRegressor(strategy="mean").fit(X_tr, y_tr)
lin = linear_model.LinearRegression().fit(X_tr, y_tr)
for name, m in (("baseline: always the training mean", base), ("linear regression", lin)):
    err = metrics.mean_absolute_error(y_te, m.predict(X_te))
    print(f"{name:36} test MAE = {err:6.2f} | test R2 = {metrics.r2_score(y_te, m.predict(X_te)):7.3f}")
```
```text
train rows: 331 | test rows: 111
baseline: always the training mean   test MAE =  58.31 | test R2 =  -0.000
linear regression                    test MAE =  45.12 | test R2 =   0.359
```

The baseline has an R² close to zero by construction: predicting the mean explains none of the variation. The linear model beats it clearly, which is the minimum evidence that features carry information. In real projects the right baseline is often a business rule ("last month's value", "the customer's segment average"), and a model must beat that too (ds.04).

### 3.2 Why we keep baselines honest

A classification baseline shows why accuracy alone misleads. Take the breast-cancer data that ships with scikit-learn (569 tumours, 30 measurements, malignant or benign).

```python run
cancer = datasets.load_breast_cancer(as_frame=True)
Xc, yc = cancer.data, cancer.target                       # 1 = benign, 0 = malignant
print("classes:", {str(k): int(v) for k, v in zip(cancer.target_names, np.bincount(yc))}, "| benign share:", round(float(yc.mean()), 3))
Xc_tr, Xc_te, yc_tr, yc_te = model_selection.train_test_split(Xc, yc, test_size=0.25, random_state=0, stratify=yc)
major = dummy.DummyClassifier(strategy="most_frequent").fit(Xc_tr, yc_tr)
print("most-frequent baseline accuracy on test:", round(float(major.score(Xc_te, yc_te)), 3), "(a model must clearly beat this)")
```
```text
classes: {'malignant': 212, 'benign': 357} | benign share: 0.627
most-frequent baseline accuracy on test: 0.629 (a model must clearly beat this)
```

## 4. Train, validation and test

### 4.1 Why one set is not enough

If you fit a model and score it on the same data, the score is flattered: the model has seen those answers. So we **split** the data. The model is fitted on the **training set** and judged on data it did not see. But there is a second, quieter trap. If you try ten models, or twenty settings, and keep the one with the best score on the same held-out set, you have used that set to *choose*, and the winning score is optimistic: you picked the luckiest. So we need three sets:

| Set | Used for | Touched |
|---|---|---|
| **Training** | fitting parameters | many times |
| **Validation** | choosing the model and hyperparameters | many times |
| **Test** | one final, honest estimate of performance | **once**, at the very end |

The test set is a sealed envelope. Open it once. If you look at the test score, change something, and look again, it has become a second validation set and the honest estimate is gone.

```python run
def three_way_split(X, y, val=0.2, test=0.2, seed=0):
    X_tmp, X_test, y_tmp, y_test = model_selection.train_test_split(X, y, test_size=test, random_state=seed)
    X_train, X_val, y_train, y_val = model_selection.train_test_split(X_tmp, y_tmp, test_size=val / (1 - test), random_state=seed)
    return X_train, X_val, X_test, y_train, y_val, y_test


Xa, Xb, Xt, ya, yb, yt = three_way_split(X_all, y_all)
print("train / validation / test:", len(Xa), len(Xb), len(Xt), "| total:", len(Xa) + len(Xb) + len(Xt))
```
```text
train / validation / test: 264 89 89 | total: 442
```

### 4.2 A split is one random draw

Whatever score you get from a split depends partly on *which rows landed where*. Repeat the split with different seeds and watch the score move. This is not a bug; it is **variance in the evaluation**, and it is the reason a single test score deserves an error bar and why cross-validation (section 9) exists.

```python run
scores = []
for seed in range(200):
    a, b, ya_, yb_ = model_selection.train_test_split(X_all, y_all, test_size=0.25, random_state=seed)
    scores.append(metrics.r2_score(yb_, linear_model.LinearRegression().fit(a, ya_).predict(b)))
scores = np.array(scores)
print(f"test R2 over 200 different random splits: mean {scores.mean():.3f} | SD {scores.std():.3f} | min {scores.min():.3f} | max {scores.max():.3f}")
print("so a single split could have told you anything from", round(float(np.quantile(scores, 0.05)), 2), "to", round(float(np.quantile(scores, 0.95)), 2), "(5th to 95th percentile)")
```
```text
test R2 over 200 different random splits: mean 0.482 | SD 0.060 | min 0.287 | max 0.650
so a single split could have told you anything from 0.39 to 0.58 (5th to 95th percentile)
```

### 4.3 Reproducibility and the random state

`random_state=0` fixes the shuffle so that you (and the reader of your report) get the same split. Always set it. Do not treat a lucky seed as a result: choosing the seed with the best score is the same sin as peeking at the test set.

### 4.4 Stratified splits for classes

With imbalanced classes a random split can by bad luck put almost all the rare cases on one side. A **stratified** split keeps the class proportions equal in both parts.

```python run
rare = np.r_[np.ones(20), np.zeros(980)]                      # 2% positives
X_dummy = np.arange(1000).reshape(-1, 1)
for strat in (None, rare):
    shares = []
    for seed in range(300):
        _, _, _, yt_ = model_selection.train_test_split(X_dummy, rare, test_size=0.2, random_state=seed, stratify=strat)
        shares.append(yt_.mean())
    print(f"{'stratified' if strat is not None else 'plain random':13}: test positive share min {min(shares):.3f}, max {max(shares):.3f} (the whole data: {rare.mean():.3f})")
```
```text
plain random : test positive share min 0.000, max 0.055 (the whole data: 0.020)
stratified   : test positive share min 0.020, max 0.020 (the whole data: 0.020)
```

## 5. Overfitting and underfitting

### 5.1 A model that is too flexible memorises

Consider fitting a curve to noisy data. A straight line is rigid: it cannot bend to follow the data and misses real structure (**underfitting**). A very wiggly curve can pass through every training point and learns the noise as if it were signal (**overfitting**). Neither generalises. We make a world where the truth is known: `y = sin(2πx)` plus noise, and fit polynomials of increasing degree.

```python run
rng = np.random.default_rng(1)
def make_curve(n, noise=0.3, seed=0):
    r = np.random.default_rng(seed)
    x = np.sort(r.uniform(0, 1, n))
    return x.reshape(-1, 1), np.sin(2 * np.pi * x) + r.normal(0, noise, n)


Xs_tr, ys_tr = make_curve(30, seed=1)
Xs_te, ys_te = make_curve(2000, seed=2)
truth = lambda x: np.sin(2 * np.pi * x)
print("noise SD 0.3 -> the best any model can do is an RMSE of about 0.30 on new data (the noise cannot be predicted)")


def poly_model(degree):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree), preprocessing.StandardScaler(), linear_model.LinearRegression())


print("\ndegree | train RMSE | test RMSE | verdict")
rows = []
for d in (0, 1, 2, 3, 4, 6, 9, 12, 15):
    m = poly_model(d).fit(Xs_tr, ys_tr)
    tr = math.sqrt(metrics.mean_squared_error(ys_tr, m.predict(Xs_tr)))
    te = math.sqrt(metrics.mean_squared_error(ys_te, m.predict(Xs_te)))
    rows.append((d, tr, te))
best = min(rows, key=lambda r: r[2])[0]
for d, tr, te in rows:
    low = min(r[2] for r in rows)
    verdict = "underfits" if d < best else ("overfits (test error rising)" if te > 1.1 * low else "about right")
    print(f"{d:6d} | {tr:10.3f} | {te:9.3f} | {verdict}")
```
```text
noise SD 0.3 -> the best any model can do is an RMSE of about 0.30 on new data (the noise cannot be predicted)

degree | train RMSE | test RMSE | verdict
     0 |      0.727 |     0.773 | underfits
     1 |      0.479 |     0.545 | underfits
     2 |      0.464 |     0.563 | underfits
     3 |      0.258 |     0.314 | about right
     4 |      0.250 |     0.319 | about right
     6 |      0.250 |     0.321 | about right
     9 |      0.236 |     0.341 | about right
    12 |      0.233 |     0.370 | overfits (test error rising)
    15 |      0.231 |     0.388 | overfits (test error rising)
```

Read the two columns together. The **training error** only ever falls as the model becomes more flexible: with enough freedom the model can fit anything. The **test error** falls, reaches a minimum, and then **rises**: the extra flexibility is spent on the noise. The best model is neither the simplest nor the most complex. This U-shaped test curve is the single most important picture in the chapter. It has the same shape for polynomial degree, tree depth, number of neighbours (reversed), or any other "complexity" dial.

### 5.2 Seeing the fit

We cannot draw here, but we can print what the models predict at a few points and compare with the truth.

```python run
grid = np.array([[0.05], [0.25], [0.5], [0.75], [0.95]])
print("x          :", grid.ravel())
print("truth      :", truth(grid.ravel()).round(2))
for d in (1, 3, 15):
    print(f"degree {d:2d}  :", poly_model(d).fit(Xs_tr, ys_tr).predict(grid).round(2))
```
```text
x          : [0.05 0.25 0.5  0.75 0.95]
truth      : [ 0.31  1.    0.   -1.   -0.31]
degree  1  : [ 1.03  0.64  0.16 -0.32 -0.71]
degree  3  : [ 0.46  0.99 -0.02 -0.98 -0.37]
degree 15  : [ 0.03  1.17 -0.03 -0.9  -0.25]
```

Degree 1 is far off at the ends of the wave (underfit). Degree 3 follows the truth. Degree 15 is erratic, especially near the edges, where it has few points to hold it down.

### 5.3 Why more data cures overfitting, and why it cannot cure underfitting

With more training data there is less room to chase noise. Repeat the degree-15 fit with more and more rows.

```python run
print("n train | degree-1 test RMSE | degree-3 test RMSE | degree-15 test RMSE")
for n in (20, 30, 60, 120, 500, 2000):
    Xn, yn = make_curve(n, seed=3)
    r = [math.sqrt(metrics.mean_squared_error(ys_te, poly_model(d).fit(Xn, yn).predict(Xs_te))) for d in (1, 3, 15)]
    print(f"{n:7d} | {r[0]:18.3f} | {r[1]:18.3f} | {r[2]:19.3f}")
```
```text
n train | degree-1 test RMSE | degree-3 test RMSE | degree-15 test RMSE
     20 |              0.614 |              0.380 |               8.755
     30 |              0.529 |              0.312 |               0.394
     60 |              0.529 |              0.319 |               0.397
    120 |              0.540 |              0.315 |               0.338
    500 |              0.526 |              0.316 |               0.306
   2000 |              0.524 |              0.311 |               0.303
```

The degree-1 line stays bad however much data it gets: it is limited by its own rigidity, not by the sample. The degree-15 curve is a disaster with 20 rows (a test RMSE of several units: the curve shoots off between the points), improves dramatically with data, and approaches the others by 500 rows. This is the practical rule: **overfitting is a problem of too little data for the model's flexibility; underfitting is a problem of a model that is too simple, and more data will not help.**

## 6. The bias-variance trade-off

### 6.1 Two ways to be wrong

The error of a model on new data splits into three parts:

`expected error = bias² + variance + irreducible noise`

- **Bias** is the error from the model being *too simple* to represent the truth, even with unlimited data (the straight line through a sine wave).
- **Variance** is the error from the model being *too sensitive to the particular sample*: train it on a different sample and it changes a lot (the wiggly degree-15 curve).
- **Irreducible noise** is the randomness in the target itself; no model can remove it.

Simple models have high bias and low variance; flexible models have low bias and high variance. The total is smallest in between. We can **measure** the pieces because we know the truth: fit the same model on hundreds of freshly drawn training sets and look at the predictions at fixed points.

```python run
def bias_variance(degree, n_train=30, reps=400, noise=0.3, points=np.linspace(0.05, 0.95, 19)):
    P = np.empty((reps, len(points)))
    for r in range(reps):
        X_, y_ = make_curve(n_train, noise, seed=1000 + r)
        P[r] = poly_model(degree).fit(X_, y_).predict(points.reshape(-1, 1))
    mean_pred = P.mean(axis=0)
    bias2 = float(np.mean((mean_pred - truth(points)) ** 2))
    var = float(np.mean(P.var(axis=0)))
    return bias2, var


print("degree | bias^2 | variance | noise^2 | sum   (measured at 19 interior points; the edges, where high degrees explode, are left out)")
for d in (1, 2, 3, 5, 9, 12):
    b2, v = bias_variance(d)
    print(f"{d:6d} | {b2:6.3f} | {v:8.3f} | {0.3 ** 2:7.3f} | {b2 + v + 0.09:5.3f}")
```
```text
degree | bias^2 | variance | noise^2 | sum   (measured at 19 interior points; the edges, where high degrees explode, are left out)
     1 |  0.164 |    0.022 |   0.090 | 0.276
     2 |  0.161 |    0.043 |   0.090 | 0.294
     3 |  0.003 |    0.013 |   0.090 | 0.107
     5 |  0.000 |    0.032 |   0.090 | 0.122
     9 |  0.004 |    0.863 |   0.090 | 0.957
    12 |  0.021 |    4.114 |   0.090 | 4.225
```

Bias falls as the degree grows; variance rises. At degree 1 almost all the error is bias; at degree 12 it is variance. The sum is smallest around degree 3 to 5. Check that the decomposition is not just arithmetic: the sum should match the mean squared error measured directly against *fresh noisy observations* at the same points.

```python run
pts = np.linspace(0.05, 0.95, 19)
for d in (1, 3, 12):
    mse = []
    for r in range(400):
        X_, y_ = make_curve(30, seed=1000 + r)                                   # the same 400 training sets as bias_variance
        y_new = truth(pts) + np.random.default_rng(9000 + r).normal(0, 0.3, len(pts))
        mse.append(np.mean((poly_model(d).fit(X_, y_).predict(pts.reshape(-1, 1)) - y_new) ** 2))
    b2, v = bias_variance(d)
    print(f"degree {d:2d}: measured MSE at the points, averaged over training sets {np.mean(mse):6.3f} | bias^2 + variance + noise^2 = {b2 + v + 0.09:6.3f}")
```
```text
degree  1: measured MSE at the points, averaged over training sets  0.282 | bias^2 + variance + noise^2 =  0.276
degree  3: measured MSE at the points, averaged over training sets  0.109 | bias^2 + variance + noise^2 =  0.107
degree 12: measured MSE at the points, averaged over training sets  4.231 | bias^2 + variance + noise^2 =  4.225
```

The two agree up to the finite number of fresh-noise draws. (The test RMSE of section 5.1 at high degrees is worse than this variance suggests because it includes the edges of the interval, where a high-degree polynomial swings wildly.) This is the mathematical reason behind the U-shaped curve of section 5.

### 6.2 What moves the dial

| To lower **bias** | To lower **variance** |
|---|---|
| a more flexible model (higher degree, deeper tree) | more training data |
| add informative features | a simpler model, fewer features |
| less regularisation | **more regularisation** (section 8) |
| | averaging many models (ensembles, ds.05) |

The dial for most of this track is complexity. You do not need to hit zero bias or zero variance; you need the sweet spot, and you find it with data (validation and cross-validation), not with intuition.

> **Predict the output.** A decision tree grown to its full depth reaches 100% accuracy on its training data. Is it more likely to have high bias or high variance? What would you expect of its score on new data?

<details><summary>Answer</summary>

```python run
Xtr_, Xte_, ytr_, yte_ = model_selection.train_test_split(Xc, yc, test_size=0.3, random_state=3, stratify=yc)
deep = tree.DecisionTreeClassifier(random_state=0).fit(Xtr_, ytr_)
print("full-depth tree: train accuracy", round(deep.score(Xtr_, ytr_), 3), "| test accuracy", round(deep.score(Xte_, yte_), 3), "| depth", deep.get_depth(), "| leaves", deep.get_n_leaves())
```
```text
full-depth tree: train accuracy 1.0 | test accuracy 0.906 | depth 6 | leaves 16
```

Perfect training accuracy means the tree has memorised the training rows (many leaves, one per few examples): **high variance**, low bias. Its test accuracy is clearly lower than its training accuracy. The gap between training and test performance is the signature of overfitting.

</details>

## 7. Learning curves

### 7.1 What a learning curve shows

A **learning curve** plots the model's training score and its validation score as the **number of training examples** grows. It is the most useful diagnostic in this chapter because one picture separates the two problems:

- **High bias (underfitting)**: training and validation errors are both high and converge to each other at a poor level. More data will not help; a richer model will.
- **High variance (overfitting)**: training error is low, validation error is much higher, and there is a **gap** that narrows as data grows. More data (or a simpler model or regularisation) will help.
- **Good fit**: both errors are low and close.

We compute it by hand: for each training size, fit on that many rows, then score on the training rows used and on a fixed validation set. Averaging over several random draws smooths the noise.

```python run
def learning_curve_table(make_model, X, y, sizes, val_X, val_y, repeats=30, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for n in sizes:
        tr, va = [], []
        for _ in range(repeats):
            idx = rng.choice(len(X), n, replace=False)
            m = make_model().fit(X[idx], y[idx])
            tr.append(math.sqrt(metrics.mean_squared_error(y[idx], m.predict(X[idx]))))
            va.append(math.sqrt(metrics.mean_squared_error(val_y, m.predict(val_X))))
        out.append((n, np.mean(tr), np.mean(va)))
    return pd.DataFrame(out, columns=["n_train", "train_rmse", "val_rmse"]).assign(gap=lambda d: d.val_rmse - d.train_rmse)


pool_X, pool_y = make_curve(600, seed=7)
sizes = [12, 20, 40, 80, 160, 320]
for d, label in ((1, "degree 1 (too simple: high bias)"), (3, "degree 3 (about right)"), (12, "degree 12 (too flexible: high variance)")):
    lc = learning_curve_table(lambda d=d: poly_model(d), pool_X, pool_y, sizes, Xs_te, ys_te)
    print(label)
    print(lc.round(3).to_string(index=False))
    print()
```
```text
degree 1 (too simple: high bias)
 n_train  train_rmse  val_rmse    gap
      12      0.4590    0.5820 0.1230
      20      0.4900    0.5660 0.0750
      40      0.4950    0.5340 0.0390
      80      0.4980    0.5330 0.0350
     160      0.5100    0.5290 0.0190
     320      0.5110    0.5260 0.0160

degree 3 (about right)
 n_train  train_rmse  val_rmse    gap
      12      0.2570    0.4060 0.1490
      20      0.2630    0.3550 0.0920
      40      0.2820    0.3260 0.0450
      80      0.2890    0.3190 0.0300
     160      0.2920    0.3140 0.0220
     320      0.2980    0.3110 0.0130

degree 12 (too flexible: high variance)
 n_train  train_rmse  val_rmse     gap
      12      0.1450   78.9080 78.7630
      20      0.1910    7.4090  7.2180
      40      0.2550    0.4290  0.1730
      80      0.2720    0.3300  0.0590
     160      0.2800    0.3140  0.0340
     320      0.2890    0.3080  0.0190
```

Compare the three tables. For degree 1, training and validation RMSE are close to each other but both stay high (about 0.5, against the noise floor of 0.3) however many rows we add: a **high-bias** curve. For degree 12 the training RMSE is tiny with few rows and the validation RMSE is enormous (78.9 with 12 rows, 7.4 with 20); the gap closes only as rows pass 40 and is still wider than for degree 3 at 80 rows: a **high-variance** curve. For degree 3 both end near the noise floor of 0.3. If you can reduce the gap with more data, collecting data is worth it; if both curves have already flattened at a bad value, collecting data is wasted money.

### 7.2 Explaining overfitting with a learning curve: the outcome

Here is the explanation the syllabus asks for, as a sentence you can defend with the table above: *"A model overfits when it has more flexibility than the data can pin down. On a learning curve this shows as a low training error, a much higher validation error and a large gap between them. The gap shrinks as the number of examples grows (the validation curve falls towards the training curve), so overfitting is cured by more data, a simpler model, or regularisation; whereas if both curves are high and flat, the model underfits and needs more capacity or better features."*

scikit-learn does the same computation with cross-validation inside (`learning_curve`); we use it on a real dataset so the pattern is not only synthetic.

```python run
def real_curve(est, X, y, scoring="neg_root_mean_squared_error"):
    sizes_, tr, va = model_selection.learning_curve(est, X, y, train_sizes=[0.1, 0.2, 0.4, 0.7, 1.0], cv=model_selection.KFold(5, shuffle=True, random_state=0), scoring=scoring)
    return pd.DataFrame({"n_train": sizes_, "train_rmse": -tr.mean(axis=1), "val_rmse": -va.mean(axis=1)}).assign(gap=lambda d: d.val_rmse - d.train_rmse)


Xp = pipeline.make_pipeline(preprocessing.PolynomialFeatures(2), preprocessing.StandardScaler(), linear_model.LinearRegression())
print("diabetes data, linear regression (10 features):")
print(real_curve(linear_model.LinearRegression(), X_all.values, y_all.values).round(2).to_string(index=False))
print("\ndiabetes data, all degree-2 interaction features (65 features): more flexible")
print(real_curve(Xp, X_all.values, y_all.values).round(2).to_string(index=False))
print("\nbaseline RMSE (SD of the target):", round(float(y_all.std()), 2))
```
```text
diabetes data, linear regression (10 features):
 n_train  train_rmse  val_rmse     gap
      35     39.8300   69.7800 29.9500
      70     47.2500   61.9200 14.6700
     141     51.5700   56.6100  5.0400
     247     53.9500   55.2300  1.2800
     353     53.4000   54.5300  1.1300

diabetes data, all degree-2 interaction features (65 features): more flexible
 n_train  train_rmse   val_rmse        gap
      35      0.0000   161.7100   161.7100
      70     19.3800 1,403.9400 1,384.5600
     141     39.2100   103.6500    64.4400
     247     47.0000    63.6200    16.6300
     353     48.3500    58.3200     9.9800

baseline RMSE (SD of the target): 77.09
```

The plain linear model has a small gap and its curves flatten early: it has little variance, and most of the remaining error is noise plus whatever a straight line cannot capture. The degree-2 model with 65 features has a much lower training error and a much larger gap: more flexible, more overfit, and on this small dataset (442 rows) it does *no better* on validation data. A richer model is not an improvement unless the validation score says so.

## 8. Regularisation

### 8.1 Penalising complexity

The cure for variance that keeps the flexible model is **regularisation**: add a penalty for large coefficients to the quantity the fit minimises. Big coefficients are how a flexible model wiggles through noise; shrinking them calms it down.

- **Ridge (L2)** minimises `Σ (yᵢ − ŷᵢ)² + α Σ βⱼ²`
- **Lasso (L1)** minimises `Σ (yᵢ − ŷᵢ)² + α Σ |βⱼ|`

`α` (alpha) is a hyperparameter: 0 gives ordinary least squares; larger values shrink the coefficients more. Ridge has a closed-form solution that follows from the calculus of ds.01: set the gradient of the penalised loss to zero.

`β = (XᵀX + αI)⁻¹ Xᵀy`

Adding `αI` to `XᵀX` also repairs a near-singular matrix (ds.01, section 3.3). The intercept is not penalised. We implement it and compare with scikit-learn.

```python run
def ridge_fit(X, y, alpha):
    """Closed-form ridge on centred data; the intercept is left unpenalised."""
    xm, ym = X.mean(axis=0), y.mean()
    Xc_, yc_ = X - xm, y - ym
    beta = np.linalg.solve(Xc_.T @ Xc_ + alpha * np.eye(X.shape[1]), Xc_.T @ yc_)
    return ym - xm @ beta, beta


Xv, yv = X_all.values, y_all.values
b0, b = ridge_fit(Xv, yv, alpha=1.0)
sk = linear_model.Ridge(alpha=1.0).fit(Xv, yv)
print("our intercept", round(float(b0), 4), "| sklearn", round(float(sk.intercept_), 4))
print("our coefs    ", b.round(2))
print("sklearn coefs", sk.coef_.round(2))
print("identical    :", np.allclose(b, sk.coef_))
```
```text
our intercept 152.1335 | sklearn 152.1335
our coefs     [  29.47  -83.15  306.35  201.63    5.91  -29.52 -152.04  117.31  262.94  111.88]
sklearn coefs [  29.47  -83.15  306.35  201.63    5.91  -29.52 -152.04  117.31  262.94  111.88]
identical    : True
```

### 8.2 Features must be on one scale

The penalty adds up squared coefficients. If one feature is measured in thousands and another in fractions, their coefficients are in wildly different units and the penalty treats them unfairly. **Standardise the features before regularising** (the diabetes columns happen to be pre-scaled; most data are not). The same applies to the penalty-based methods of ds.01's gradient descent.

### 8.3 What the penalty does to the coefficients

Fix a deliberately flexible setting (a degree-9 polynomial, 30 noisy points) and increase `α`. Large `α` flattens the curve; tiny `α` lets it wiggle.

```python run
def poly_ridge(degree, alpha):
    return pipeline.make_pipeline(preprocessing.PolynomialFeatures(degree, include_bias=False), preprocessing.StandardScaler(), linear_model.Ridge(alpha=alpha))


print("alpha     | train RMSE | test RMSE | largest |coefficient| | verdict")
rows = []
for alpha in (1e-8, 1e-5, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0):
    m = poly_ridge(9, alpha).fit(Xs_tr, ys_tr)
    tr = math.sqrt(metrics.mean_squared_error(ys_tr, m.predict(Xs_tr)))
    te = math.sqrt(metrics.mean_squared_error(ys_te, m.predict(Xs_te)))
    rows.append((alpha, tr, te, float(np.abs(m[-1].coef_).max())))
best_te = min(r[2] for r in rows)
for alpha, tr, te, cmax in rows:
    tag = "best" if te == best_te else ("little penalty: wiggly" if cmax > 10 else ("too much penalty: underfits" if te > 1.3 * best_te else ""))
    print(f"{alpha:9.0e} | {tr:10.3f} | {te:9.3f} | {cmax:21.2f} | {tag}")
```
```text
alpha     | train RMSE | test RMSE | largest |coefficient| | verdict
    1e-08 |      0.236 |     0.340 |                421.16 | little penalty: wiggly
    1e-05 |      0.246 |     0.323 |                 22.75 | little penalty: wiggly
    1e-03 |      0.253 |     0.313 |                  7.77 | best
    1e-02 |      0.264 |     0.320 |                  4.39 | 
    1e-01 |      0.314 |     0.384 |                  1.51 | 
    1e+00 |      0.348 |     0.432 |                  0.53 | too much penalty: underfits
    1e+01 |      0.425 |     0.487 |                  0.29 | too much penalty: underfits
    1e+02 |      0.584 |     0.639 |                  0.08 | too much penalty: underfits
```

As `α` grows, the largest coefficient shrinks steadily, the training error rises (the fit is restrained) and the test error first falls and then rises: another U-shaped curve, this time over the **regularisation strength** instead of the degree. The same model family, with a dial that moves it from overfit to underfit.

### 8.4 Lasso and sparsity

The L1 penalty has a special effect: it drives some coefficients to **exactly zero**, so the model selects features. Useful when many features are junk. We build data where only 3 of 30 features matter.

```python run
rng = np.random.default_rng(11)
n, p = 120, 30
Xl = rng.normal(size=(n, p))
true_beta = np.zeros(p); true_beta[[0, 1, 2]] = [3.0, -2.0, 1.5]
yl = Xl @ true_beta + rng.normal(0, 1.0, n)
Xl_te = rng.normal(size=(2000, p)); yl_te = Xl_te @ true_beta + rng.normal(0, 1.0, 2000)

models = {"least squares": linear_model.LinearRegression(), "ridge (alpha=30)": linear_model.Ridge(alpha=30), "lasso (alpha=0.15)": linear_model.Lasso(alpha=0.15)}
print(f"{'model':20} | test RMSE | coefficients that are exactly zero | the 3 true coefficients (3, -2, 1.5) estimated as")
for name, m in models.items():
    m.fit(Xl, yl)
    rm = math.sqrt(metrics.mean_squared_error(yl_te, m.predict(Xl_te)))
    print(f"{name:20} | {rm:9.3f} | {int(np.sum(m.coef_ == 0)):>2d} of {p} {'':22} | {m.coef_[:3].round(2)}")
print("noise SD is 1.0, so the best possible test RMSE is about 1.0")
```
```text
model                | test RMSE | coefficients that are exactly zero | the 3 true coefficients (3, -2, 1.5) estimated as
least squares        |     1.172 |  0 of 30                        | [ 2.88 -2.14  1.51]
ridge (alpha=30)     |     1.452 |  0 of 30                        | [ 2.32 -1.64  1.19]
lasso (alpha=0.15)   |     1.035 | 23 of 30                        | [ 2.83 -2.01  1.39]
noise SD is 1.0, so the best possible test RMSE is about 1.0
```

Least squares uses all 30 features and pays for the 27 useless ones with a higher test error. Ridge shrinks every coefficient but removes none; at `α = 30` it is too strong for this problem (the true coefficient 3 is estimated as 2.3) and does *worse* than least squares: a penalty must be tuned, not assumed. Lasso zeroes most of the junk and gets closest to the truth, at the cost of shrinking the true coefficients a little. A caution: the surviving features and their order are fragile when features are correlated with each other; treat lasso's selection as a hint, not a verdict.

### 8.5 The regularisation path

Watching how the coefficients change as `α` grows tells you which features are the last to be shrunk, and therefore the strongest.

```python run
alphas = [0.01, 0.05, 0.1, 0.2, 0.4, 0.8]
path = pd.DataFrame({a: linear_model.Lasso(alpha=a).fit(Xl, yl).coef_[:6] for a in alphas}, index=[f"x{i}" for i in range(6)])
print("lasso coefficients of the first 6 features (x0, x1, x2 are the real ones) as alpha grows:")
print(path.round(2).to_string())
print("number of non-zero coefficients out of 30:", [int(np.sum(linear_model.Lasso(alpha=a).fit(Xl, yl).coef_ != 0)) for a in alphas])
```
```text
lasso coefficients of the first 6 features (x0, x1, x2 are the real ones) as alpha grows:
    0.0100  0.0500  0.1000  0.2000  0.4000  0.8000
x0  2.8800  2.8800  2.8600  2.8000  2.6600  2.3600
x1 -2.1200 -2.0700 -2.0300 -1.9800 -1.8000 -1.3900
x2  1.5100  1.4800  1.4300  1.3400  1.1600  0.8000
x3  0.1300  0.0600  0.0000  0.0000  0.0000  0.0000
x4 -0.0000  0.0000  0.0000  0.0000  0.0000  0.0000
x5 -0.0000 -0.0000 -0.0000 -0.0000  0.0000  0.0000
number of non-zero coefficients out of 30: [22, 14, 10, 6, 3, 3]
```

The three real features survive until `α` is large; the junk features drop out first.


## 9. Cross-validation

### 9.1 Using all the data to judge, without peeking

A single validation split wastes data and is noisy (section 4.2). **K-fold cross-validation** uses every row for validation exactly once: split the data into `k` equal **folds**; for each fold, train on the other `k − 1` and score on that fold; average the `k` scores. The spread of the `k` scores is a free error bar.

We write it by hand first.

```python run
def kfold_indices(n, k, seed=0):
    idx = np.random.default_rng(seed).permutation(n)
    return np.array_split(idx, k)


def cross_val_manual(make_model, X, y, k=5, seed=0, scorer=metrics.r2_score):
    folds = kfold_indices(len(y), k, seed)
    scores = []
    for i in range(k):
        val = folds[i]
        train = np.concatenate([folds[j] for j in range(k) if j != i])
        m = make_model().fit(X[train], y[train])
        scores.append(scorer(y[val], m.predict(X[val])))
    return np.array(scores)


s = cross_val_manual(linear_model.LinearRegression, Xv, yv, k=5)
print("5 fold scores (R2):", s.round(3))
print(f"mean {s.mean():.3f} | SD across folds {s.std(ddof=1):.3f}")

auto = model_selection.cross_val_score(linear_model.LinearRegression(), Xv, yv, cv=model_selection.KFold(5, shuffle=True, random_state=0), scoring="r2")
print("scikit-learn cross_val_score:", auto.round(3), "| mean", round(float(auto.mean()), 3), "(folds differ because the shuffle differs; the mean agrees closely)")
```
```text
5 fold scores (R2): [0.501 0.503 0.533 0.557 0.343]
mean 0.487 | SD across folds 0.084
scikit-learn cross_val_score: [0.332 0.46  0.537 0.522 0.595] | mean 0.489 (folds differ because the shuffle differs; the mean agrees closely)
```

### 9.2 Choosing k, and repeating

`k = 5` or `k = 10` are the usual choices. A larger `k` trains on more data per fold (in principle less pessimistic) but costs more fits and makes the folds more alike. On this dataset the table shows little systematic gain from a larger `k` (the means differ by about 0.03 at most, similar to the shuffle-to-shuffle noise), so `k = 5` is a sound default. **Leave-one-out** (`k = n`) is the extreme and is expensive. Repeating k-fold with different shuffles smooths the dependence on any one partition.

```python run
print("   k | mean R2 | SD of the mean-over-repeats (10 repeats of different shuffles) | fits")
for k in (2, 3, 5, 10, 20):
    means = [model_selection.cross_val_score(linear_model.LinearRegression(), Xv, yv, cv=model_selection.KFold(k, shuffle=True, random_state=r), scoring="r2").mean() for r in range(10)]
    print(f"{k:4d} | {np.mean(means):7.4f} | {np.std(means):63.4f} | {k * 10:4d}")
```
```text
   k | mean R2 | SD of the mean-over-repeats (10 repeats of different shuffles) | fits
   2 |  0.4833 |                                                          0.0106 |   20
   3 |  0.4856 |                                                          0.0055 |   30
   5 |  0.4818 |                                                          0.0059 |   50
  10 |  0.4756 |                                                          0.0093 |  100
  20 |  0.4548 |                                                          0.0090 |  200
```

### 9.3 Stratified, grouped and time-ordered folds

- **Stratified k-fold** keeps the class proportions in every fold: the default for classification.
- **Group k-fold** keeps all rows of one group (a patient, a customer, a store) in the same fold. When rows from the same patient sit in both training and validation sets, the model recognises the patient and the score is inflated.
- **Time-series split** always validates on the future of the training window; shuffling a time series lets the model see tomorrow while predicting today.

The last two are the heart of ds.04. Here is the first effect in miniature: 40 "patients" with 10 rows each, where each patient has a personal offset that the model can memorise.

```python run
rng = np.random.default_rng(21)
n_pat, per = 40, 10
pid = np.repeat(np.arange(n_pat), per)
offset = rng.normal(0, 3, n_pat)[pid]                                    # a personal level that is NOT related to the features
Xg = rng.normal(size=(n_pat * per, 3))
yg = Xg @ [1.0, -1.0, 0.5] + offset + rng.normal(0, 0.5, n_pat * per)
Xg_id = np.column_stack([Xg, np.eye(n_pat)[pid]])                        # the patient identity is visible to the model

rf = lambda: ensemble.RandomForestRegressor(n_estimators=100, random_state=0, min_samples_leaf=1)
plain = model_selection.cross_val_score(rf(), Xg_id, yg, cv=model_selection.KFold(5, shuffle=True, random_state=0), scoring="r2").mean()
grouped = model_selection.cross_val_score(rf(), Xg_id, yg, cv=model_selection.GroupKFold(5), groups=pid, scoring="r2").mean()
print(f"ordinary 5-fold CV (a patient appears on both sides): R2 = {plain:.3f}")
print(f"group 5-fold CV (a patient is on one side only)     : R2 = {grouped:.3f}")
print("the honest question is 'how well will it do on a NEW patient?', and only the grouped score answers it")
```
```text
ordinary 5-fold CV (a patient appears on both sides): R2 = 0.684
group 5-fold CV (a patient is on one side only)     : R2 = -0.129
the honest question is 'how well will it do on a NEW patient?', and only the grouped score answers it
```

### 9.4 What cross-validation estimates

Cross-validation estimates the performance of a **procedure** (fit with these settings on this much data), not of one particular fitted model. After choosing settings with it you refit on all the training data and then report the sealed test set once.

## 10. Choosing hyperparameters without cheating

### 10.1 A search with cross-validation

Pick a grid of hyperparameter values, cross-validate each, choose the best, refit. `GridSearchCV` does exactly this. We tune the ridge `α` on the diabetes training data and open the test set once.

```python run
Xtr_d, Xte_d, ytr_d, yte_d = model_selection.train_test_split(Xv, yv, test_size=0.25, random_state=0)
grid = model_selection.GridSearchCV(linear_model.Ridge(), {"alpha": np.logspace(-3, 2, 11)}, cv=model_selection.KFold(5, shuffle=True, random_state=0), scoring="neg_root_mean_squared_error")
grid.fit(Xtr_d, ytr_d)
res = pd.DataFrame({"alpha": grid.cv_results_["param_alpha"].astype(float), "cv_rmse": -grid.cv_results_["mean_test_score"], "cv_sd": grid.cv_results_["std_test_score"]})
print(res.round(3).to_string(index=False))
print("\nbest alpha:", round(float(grid.best_params_["alpha"]), 4), "| cv RMSE", round(float(-grid.best_score_), 2))
print("test RMSE of the refit best model (opened once):", round(math.sqrt(metrics.mean_squared_error(yte_d, grid.predict(Xte_d))), 2))
print("test RMSE of plain least squares                :", round(math.sqrt(metrics.mean_squared_error(yte_d, linear_model.LinearRegression().fit(Xtr_d, ytr_d).predict(Xte_d))), 2))
```
```text
   alpha  cv_rmse  cv_sd
  0.0010  54.0870 3.8660
  0.0030  54.0820 3.8700
  0.0100  54.0640 3.8790
  0.0320  54.0110 3.8970
  0.1000  54.0960 3.9410
  0.3160  55.3330 3.9340
  1.0000  59.5720 3.7110
  3.1620  66.6140 3.6000
 10.0000  73.2510 3.6450
 31.6230  76.9640 3.6710
100.0000  78.4420 3.6780

best alpha: 0.0316 | cv RMSE 54.01
test RMSE of the refit best model (opened once): 56.4
test RMSE of plain least squares                : 56.39
```

Note how flat the curve is near the best value, and look at `cv_sd`: several neighbouring values are within one standard deviation of each other, so the "best" `α` is not sharply defined. A common rule is to choose the **simplest model within one standard error of the best**. And on this small dataset the gain over plain least squares is nil (56.40 against 56.39): ten well-behaved features and 331 rows leave little variance to remove. Regularisation helps when there are many features or little data (section 8.4).

### 10.2 The optimism of the best of many

If you try many settings and report the best cross-validated score, that score is biased upwards: you took the maximum of several noisy estimates. The remedy is the sealed test set, or, when data are scarce, **nested cross-validation**: an inner loop chooses the hyperparameters and an outer loop scores the whole choosing procedure. Demonstration on pure noise, where every honest score should be at or below chance.

```python run
rng = np.random.default_rng(31)
Xn = rng.normal(size=(80, 60))
yn = rng.integers(0, 2, 80)                                              # labels unrelated to the features
params = {"C": np.logspace(-4, 2, 13)}
inner = model_selection.GridSearchCV(linear_model.LogisticRegression(max_iter=2000), params, cv=model_selection.StratifiedKFold(5, shuffle=True, random_state=1), scoring="accuracy")
inner.fit(Xn, yn)
print("pure noise, labels random (chance accuracy = 0.5)")
print("best cross-validated accuracy found by the search:", round(float(inner.best_score_), 3), "<- optimistic: the maximum of 13 noisy scores")
nested = model_selection.cross_val_score(inner, Xn, yn, cv=model_selection.StratifiedKFold(5, shuffle=True, random_state=2), scoring="accuracy")
print("nested cross-validation of the same procedure    :", round(float(nested.mean()), 3), "(an honest estimate: about chance)")
```
```text
pure noise, labels random (chance accuracy = 0.5)
best cross-validated accuracy found by the search: 0.588 <- optimistic: the maximum of 13 noisy scores
nested cross-validation of the same procedure    : 0.525 (an honest estimate: about chance)
```

The inner search reports a score above chance for data that contain no signal at all. Nested cross-validation sees through it. Never report the score you used to choose.

## 11. Metrics for regression

### 11.1 The common ones

A **metric** turns predictions and truth into one number. For regression, with errors `eᵢ = yᵢ − ŷᵢ`:

| Metric | Formula | Meaning | Note |
|---|---|---|---|
| **MAE** mean absolute error | `mean(abs(e))` | average miss, in target units | robust to outliers |
| **MSE** mean squared error | `mean(e²)` | squared units | punishes big misses |
| **RMSE** | `sqrt(MSE)` | typical miss, in target units | sensitive to outliers |
| **R²** | `1 − Σe² / Σ(y − ȳ)²` | share of variance explained | 0 = same as predicting the mean; negative = worse |
| **MAPE** | `mean(abs(e / y))` | average percentage miss | breaks when `y` is near 0 |

```python run
def reg_metrics(y, p):
    e = y - p
    return {"MAE": np.mean(np.abs(e)), "MSE": np.mean(e ** 2), "RMSE": math.sqrt(np.mean(e ** 2)),
            "R2": 1 - np.sum(e ** 2) / np.sum((y - y.mean()) ** 2), "MAPE": np.mean(np.abs(e / y))}


m = linear_model.LinearRegression().fit(Xtr_d, ytr_d)
p = m.predict(Xte_d)
ours = reg_metrics(yte_d, p)
print({k: round(float(v), 4) for k, v in ours.items()})
print("sklearn  MAE", round(metrics.mean_absolute_error(yte_d, p), 4), "| RMSE", round(math.sqrt(metrics.mean_squared_error(yte_d, p)), 4), "| R2", round(metrics.r2_score(yte_d, p), 4), "| MAPE", round(metrics.mean_absolute_percentage_error(yte_d, p), 4))
```
```text
{'MAE': 45.1206, 'MSE': 3180.1596, 'RMSE': 56.3929, 'R2': 0.3594, 'MAPE': 0.3796}
sklearn  MAE 45.1206 | RMSE 56.3929 | R2 0.3594 | MAPE 0.3796
```

### 11.2 Which metric? It depends on the cost of an error

Metrics are not interchangeable. A single huge miss moves the RMSE far more than the MAE. If the business is hurt by large errors (a stock-out), use RMSE; if every unit of error costs the same, use MAE. Here is the effect of one outlier.

```python run
y_true = np.array([100.0, 110, 95, 105, 98, 102, 107, 99])
p_good = y_true + np.array([2, -3, 1, 2, -2, 3, -1, 2])
p_bad = p_good.copy(); p_bad[0] = 160                                       # one wild miss
for name, pp in (("small errors everywhere", p_good), ("same, but one prediction off by 60", p_bad)):
    r = reg_metrics(y_true, pp)
    print(f"{name:36} MAE {r['MAE']:6.2f} | RMSE {r['RMSE']:6.2f} | RMSE/MAE {r['RMSE'] / r['MAE']:5.2f}")
```
```text
small errors everywhere              MAE   2.00 | RMSE   2.12 | RMSE/MAE  1.06
same, but one prediction off by 60   MAE   9.25 | RMSE  21.31 | RMSE/MAE  2.30
```

One wild prediction raises the MAE about 4.6 times but the RMSE about 10 times. A ratio of RMSE to MAE well above 1.25 or so warns of a few large errors.

### 11.3 R² has traps

R² compares your model with predicting the mean **of the data being scored**. It is 0 for the mean predictor and *can be negative on a test set*: a model worse than the mean. R² computed on training data only rises as features are added, even useless ones.

```python run
rng = np.random.default_rng(41)
n = 60
x1 = rng.normal(size=(n, 1)); y1 = 2 * x1[:, 0] + rng.normal(0, 1, n)
x1_te = rng.normal(size=(2000, 1)); y1_te = 2 * x1_te[:, 0] + rng.normal(0, 1, 2000)
print("added junk columns | train R2 | test R2")
for junk in (0, 5, 20, 40, 55):
    A = np.hstack([x1, rng.normal(size=(n, junk))]); A_te = np.hstack([x1_te, rng.normal(size=(2000, junk))])
    mm = linear_model.LinearRegression().fit(A, y1)
    print(f"{junk:18d} | {mm.score(A, y1):8.3f} | {mm.score(A_te, y1_te):8.3f}")
```
```text
added junk columns | train R2 | test R2
                 0 |    0.818 |    0.807
                 5 |    0.835 |    0.790
                20 |    0.863 |    0.768
                40 |    0.950 |    0.441
                55 |    0.991 |   -0.205
```

Training R² climbs towards 1 as junk columns are added; test R² falls, eventually below zero. Report test or cross-validated R², never training R².

### 11.4 Look at the residuals

A single number hides patterns. Residuals should have no structure: if they grow with the prediction, the error is not constant; if they are mostly one sign in one region, the model is biased there.

```python run
resid = yte_d - p
order = np.argsort(p)
chunks = np.array_split(order, 4)
print("predictions split into 4 groups (low to high): mean residual | mean absolute residual")
for i, c in enumerate(chunks):
    print(f"  group {i + 1}: mean prediction {p[c].mean():6.1f} | mean residual {resid[c].mean():7.2f} | mean |residual| {np.abs(resid[c]).mean():6.2f}")
```
```text
predictions split into 4 groups (low to high): mean residual | mean absolute residual
  group 1: mean prediction   90.4 | mean residual    6.66 | mean |residual|  30.24
  group 2: mean prediction  139.0 | mean residual   -7.24 | mean |residual|  51.84
  group 3: mean prediction  175.4 | mean residual    9.63 | mean |residual|  42.66
  group 4: mean prediction  223.6 | mean residual  -24.68 | mean |residual|  56.13
```

The residuals are not pure noise: the highest predictions are too high on average (mean residual about −25 in the top group) while the middle groups are close to zero. The model over-predicts the sickest patients; a single R² would never tell you.

## 12. Metrics for classification

### 12.1 The confusion matrix

A classifier that predicts positive or negative makes four kinds of outcome, collected in the **confusion matrix**: true positives (TP), false positives (FP), false negatives (FN), true negatives (TN). Every classification metric is built from these four counts.

```python run
Xc_tr, Xc_te, yc_tr, yc_te = model_selection.train_test_split(Xc, yc, test_size=0.3, random_state=0, stratify=yc)
clf = pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression(max_iter=1000)).fit(Xc_tr, yc_tr)
pred = clf.predict(Xc_te)
# positive class = 0 (malignant), the one we must not miss
pos = 0
TP = int(np.sum((pred == pos) & (yc_te == pos))); FP = int(np.sum((pred == pos) & (yc_te != pos)))
FN = int(np.sum((pred != pos) & (yc_te == pos))); TN = int(np.sum((pred != pos) & (yc_te != pos)))
print(pd.DataFrame([[TP, FN], [FP, TN]], index=["actually malignant", "actually benign"], columns=["predicted malignant", "predicted benign"]).to_string())
print("sklearn confusion_matrix (rows true 0/1, cols predicted 0/1):\n", metrics.confusion_matrix(yc_te, pred))
```
```text
                    predicted malignant  predicted benign
actually malignant                   61                 3
actually benign                       4               103
sklearn confusion_matrix (rows true 0/1, cols predicted 0/1):
 [[ 61   3]
 [  4 103]]
```

### 12.2 Accuracy, precision, recall, F1

- **Accuracy** `= (TP + TN) / all`: the share right. Misleading when classes are unequal.
- **Precision** `= TP / (TP + FP)`: of those predicted positive, how many are. "When it raises an alarm, is it real?"
- **Recall** (sensitivity) `= TP / (TP + FN)`: of the real positives, how many did we find. "How many did it miss?"
- **Specificity** `= TN / (TN + FP)`: of the real negatives, how many did we clear.
- **F1** `= 2PR / (P + R)`: the harmonic mean of precision and recall; low if either is low.

```python run
def cls_metrics(TP, FP, FN, TN):
    acc = (TP + TN) / (TP + FP + FN + TN)
    prec = TP / (TP + FP) if TP + FP else float("nan")
    rec = TP / (TP + FN) if TP + FN else float("nan")
    spec = TN / (TN + FP) if TN + FP else float("nan")
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else float("nan")
    return {"accuracy": acc, "precision": prec, "recall": rec, "specificity": spec, "F1": f1}


ours = cls_metrics(TP, FP, FN, TN)
print({k: round(v, 4) for k, v in ours.items()})
print("sklearn precision", round(metrics.precision_score(yc_te, pred, pos_label=0), 4), "| recall", round(metrics.recall_score(yc_te, pred, pos_label=0), 4), "| F1", round(metrics.f1_score(yc_te, pred, pos_label=0), 4), "| accuracy", round(metrics.accuracy_score(yc_te, pred), 4))
```
```text
{'accuracy': 0.9591, 'precision': 0.9385, 'recall': 0.9531, 'specificity': 0.9626, 'F1': 0.9457}
sklearn precision 0.9385 | recall 0.9531 | F1 0.9457 | accuracy 0.9591
```

### 12.3 The accuracy trap

Take a fraud problem: 1 transaction in 200 is fraudulent. A model that says "never fraud" is right 99.5% of the time and catches nothing.

```python run
rng = np.random.default_rng(51)
y_f = (rng.uniform(size=20_000) < 0.005).astype(int)
never = np.zeros_like(y_f)
print("fraud share:", round(float(y_f.mean()), 4))
print("'never fraud' model: accuracy", round(metrics.accuracy_score(y_f, never), 4), "| recall", metrics.recall_score(y_f, never, zero_division=0), "| precision", metrics.precision_score(y_f, never, zero_division=0))
```
```text
fraud share: 0.0049
'never fraud' model: accuracy 0.9951 | recall 0.0 | precision 0.0
```

The headline number looks superb and the model is worthless. For imbalanced problems report **precision, recall and the confusion matrix**, never accuracy alone. Which of the two to favour depends on costs: missing a cancer (FN) is far worse than a false alarm (FP), so favour recall; flagging an innocent customer as a fraudster is costly in a different way.

### 12.4 Probabilities and thresholds

Most classifiers output a **probability** (or a score) and the label comes from a **threshold**, 0.5 by default. Moving the threshold trades precision against recall: a lower threshold flags more cases (higher recall, more false alarms); a higher threshold flags fewer (higher precision, more misses).

```python run
proba_malignant = clf.predict_proba(Xc_te)[:, 0]
print("threshold | flagged | precision | recall | F1")
for th in (0.1, 0.3, 0.5, 0.7, 0.9, 0.99):
    flag = proba_malignant >= th
    tp = int(np.sum(flag & (yc_te == 0))); fp = int(np.sum(flag & (yc_te == 1))); fn = int(np.sum(~flag & (yc_te == 0)))
    pr = tp / (tp + fp) if tp + fp else float("nan"); rc = tp / (tp + fn)
    print(f"{th:9.2f} | {int(flag.sum()):7d} | {pr:9.3f} | {rc:6.3f} | {2 * pr * rc / (pr + rc) if pr + rc else float('nan'):5.3f}")
```
```text
threshold | flagged | precision | recall | F1
     0.10 |      74 |     0.851 |  0.984 | 0.913
     0.30 |      68 |     0.912 |  0.969 | 0.939
     0.50 |      65 |     0.938 |  0.953 | 0.946
     0.70 |      61 |     0.967 |  0.922 | 0.944
     0.90 |      54 |     1.000 |  0.844 | 0.915
     0.99 |      51 |     1.000 |  0.797 | 0.887
```

### 12.5 ROC curve and AUC

The **ROC curve** plots the true-positive rate (recall) against the false-positive rate as the threshold sweeps from high to low. The **AUC** (area under it) summarises ranking quality in one number: it equals the probability that a randomly chosen positive gets a higher score than a randomly chosen negative. 0.5 is a coin; 1.0 is perfect. We compute it from that definition and check it.

```python run
def auc_by_pairs(y, score):
    pos_s, neg_s = score[y == 1], score[y == 0]
    greater = (pos_s[:, None] > neg_s[None, :]).mean()
    ties = (pos_s[:, None] == neg_s[None, :]).mean()
    return float(greater + 0.5 * ties)


score_malignant = proba_malignant
y_mal = (yc_te == 0).astype(int)
print("AUC by counting pairs :", round(auc_by_pairs(y_mal, score_malignant), 4))
print("sklearn roc_auc_score :", round(metrics.roc_auc_score(y_mal, score_malignant), 4))
fpr, tpr, thr = metrics.roc_curve(y_mal, score_malignant)
print("a few ROC points (fpr, tpr):", [(round(float(a), 3), round(float(b), 3)) for a, b in list(zip(fpr, tpr))[::max(1, len(fpr) // 6)]])
rng = np.random.default_rng(52)
print("random scores:", round(auc_by_pairs(y_mal, rng.uniform(size=len(y_mal))), 3), "(about 0.5)")
```
```text
AUC by counting pairs : 0.9956
sklearn roc_auc_score : 0.9956
a few ROC points (fpr, tpr): [(0.0, 0.0), (0.0, 0.922), (0.019, 0.938), (0.028, 0.953), (0.047, 0.969), (0.084, 0.984), (0.103, 1.0)]
random scores: 0.493 (about 0.5)
```

AUC is threshold-free, which is useful for comparing models, but it can look excellent on heavily imbalanced data where a precision-recall view is more informative (ds.04). **Log loss** (cross-entropy, the loss of ds.01) judges the quality of the probabilities themselves, not just their ranking.

```python run
def log_loss(y, p, eps=1e-15):
    p = np.clip(p, eps, 1 - eps)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


p_pos = clf.predict_proba(Xc_te)[:, 1]
print("our log loss:", round(log_loss(yc_te, p_pos), 4), "| sklearn:", round(metrics.log_loss(yc_te, p_pos), 4))
print("overconfident predictions are punished: the same hard labels with probabilities pushed to 0.999/0.001 ->", round(log_loss(yc_te, np.where(p_pos > 0.5, 0.999, 0.001)), 4))
```
```text
our log loss: 0.0846 | sklearn: 0.0846
overconfident predictions are punished: the same hard labels with probabilities pushed to 0.999/0.001 -> 0.2837
```

### 12.6 More than two classes

For several classes, compute precision and recall per class and average them: **macro** averaging treats every class equally, **weighted** averaging weights by class size. Use macro when the rare classes matter.

(The iris flowers are an easy problem; a perfect score on a 45-row test set is typical and should not be over-read.)

```python run
iris = datasets.load_iris()
Xi_tr, Xi_te, yi_tr, yi_te = model_selection.train_test_split(iris.data, iris.target, test_size=0.3, random_state=0, stratify=iris.target)
ic = neighbors.KNeighborsClassifier(5).fit(Xi_tr, yi_tr)
print(metrics.classification_report(yi_te, ic.predict(Xi_te), target_names=iris.target_names, digits=3))
```
```text
              precision    recall  f1-score   support

      setosa      1.000     1.000     1.000        15
  versicolor      1.000     1.000     1.000        15
   virginica      1.000     1.000     1.000        15

    accuracy                          1.000        45
   macro avg      1.000     1.000     1.000        45
weighted avg      1.000     1.000     1.000        45
```

## 13. Unsupervised learning: finding structure without labels

### 13.1 Clustering with k-means

K-means groups points into `k` clusters by repeating two steps: assign each point to the nearest centre, then move each centre to the mean of its points. It minimises the total squared distance from points to their centres (the **inertia**). We write it from scratch, using the distance and mean ideas of ds.01.

```python run
def kmeans(X, k, iters=100, seed=0):
    rng = np.random.default_rng(seed)
    centres = X[rng.choice(len(X), k, replace=False)]
    for _ in range(iters):
        d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
        labels = d.argmin(axis=1)
        new = np.array([X[labels == j].mean(axis=0) if np.any(labels == j) else centres[j] for j in range(k)])
        if np.allclose(new, centres):
            break
        centres = new
    d = ((X[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)
    return centres, d.argmin(axis=1), float(d.min(axis=1).sum())


Xb, true_lab = datasets.make_blobs(n_samples=600, centers=[[0, 0], [6, 0], [3, 5]], cluster_std=1.0, random_state=0)
centres, labels, inertia = kmeans(Xb, 3)
print("centres found:\n", centres[np.argsort(centres[:, 0])].round(2))
print("cluster sizes:", np.bincount(labels), "| inertia:", round(inertia, 1))
skm = cluster.KMeans(3, n_init=10, random_state=0).fit(Xb)
print("sklearn inertia:", round(float(skm.inertia_), 1))
```
```text
centres found:
 [[-0.07  0.01]
 [ 3.14  5.02]
 [ 5.89 -0.13]]
cluster sizes: [200 200 200] | inertia: 1137.5
sklearn inertia: 1137.5
```

### 13.2 Choosing k, and the problem of the start

K-means finds a *local* minimum, which depends on the starting centres; real implementations restart several times (`n_init`) and keep the best. The right `k` is not given by the algorithm. Inertia always falls as `k` grows, so we look for an "elbow", or use the **silhouette score** (how much closer a point is to its own cluster than to the next one; from −1 to 1).

```python run
print("k | inertia | silhouette")
for k in range(2, 8):
    km = cluster.KMeans(k, n_init=10, random_state=0).fit(Xb)
    print(f"{k} | {km.inertia_:7.1f} | {metrics.silhouette_score(Xb, km.labels_):.3f}")
print("the data were generated from 3 blobs: the silhouette peaks at k = 3 while inertia keeps falling")

starts = [kmeans(Xb, 3, seed=s)[2] for s in range(8)]
print("inertia from 8 single random starts:", np.round(starts, 0), "-> some starts get stuck in a worse solution")
```
```text
k | inertia | silhouette
2 |  4540.3 | 0.474
3 |  1137.5 | 0.685
4 |   992.0 | 0.562
5 |   860.8 | 0.445
6 |   756.0 | 0.312
7 |   663.9 | 0.335
the data were generated from 3 blobs: the silhouette peaks at k = 3 while inertia keeps falling
inertia from 8 single random starts: [1138. 1138. 1138. 1138. 1138. 1138. 1138. 4489.] -> some starts get stuck in a worse solution
```

### 13.3 Dimensionality reduction with PCA

PCA (ds.01, sections 4 and 5) projects the data onto the few directions of greatest variance. As a pre-processing step it reduces noise and the number of columns; as a visual aid it gives a 2-D picture of high-dimensional data. The **explained variance ratio** says how much each component keeps.

```python run
Xs_c = preprocessing.StandardScaler().fit_transform(Xc)
pca = decomposition.PCA().fit(Xs_c)
cum = np.cumsum(pca.explained_variance_ratio_)
print("breast-cancer data: 30 features")
print("variance kept by the first 1, 2, 3, 5, 10 components:", [round(float(cum[i - 1]), 3) for i in (1, 2, 3, 5, 10)])
print("components needed to keep 95% of the variance:", int(np.argmax(cum >= 0.95)) + 1)

for ncomp in (2, 10, 30):
    pip = pipeline.make_pipeline(preprocessing.StandardScaler(), decomposition.PCA(ncomp), linear_model.LogisticRegression(max_iter=1000))
    sc = model_selection.cross_val_score(pip, Xc, yc, cv=model_selection.StratifiedKFold(5, shuffle=True, random_state=0), scoring="accuracy")
    print(f"logistic regression on {ncomp:2d} components: cross-validated accuracy {sc.mean():.3f}")
```
```text
breast-cancer data: 30 features
variance kept by the first 1, 2, 3, 5, 10 components: [0.443, 0.632, 0.726, 0.847, 0.952]
components needed to keep 95% of the variance: 10
logistic regression on  2 components: cross-validated accuracy 0.958
logistic regression on 10 components: cross-validated accuracy 0.981
logistic regression on 30 components: cross-validated accuracy 0.979
```

Unsupervised results are harder to judge, because there is no right answer to score against. Check clusters for **stability** (do they survive a re-run or a resample?) and for **meaning** (can you describe each in business terms?). A cluster you cannot name is probably not a segment.

## 14. Project: a model evaluation framework

### 14.1 The brief

Build one small module, `evalkit.py`, that you can point at any scikit-learn-style model and dataset to produce an **honest evaluation report**. It must:

1. split the data once into a development set and a sealed test set (stratified for classification);
2. compare models against a **baseline** with cross-validation and report mean ± SD;
3. draw a **learning curve** and say whether the model is high-bias, high-variance or fine;
4. tune a hyperparameter with a search on the development set only;
5. open the test set **once**, for the single finalist, and report the metrics that suit the task;
6. refuse to open the test set twice.

### 14.2 The module

```python run
import pathlib, tempfile
tmp = pathlib.Path(tempfile.mkdtemp(prefix="evalkit_"))
EVALKIT = r'''"""evalkit: an honest model evaluation workflow."""
import math
import numpy as np
import pandas as pd
from sklearn import dummy, metrics, model_selection


class TestSetAlreadyOpened(RuntimeError):
    pass


class Evaluation:
    def __init__(self, X, y, task="regression", test_size=0.2, seed=0):
        assert task in ("regression", "classification")
        self.task, self.seed = task, seed
        strat = y if task == "classification" else None
        self.X_dev, self._X_test, self.y_dev, self._y_test = model_selection.train_test_split(
            X, y, test_size=test_size, random_state=seed, stratify=strat)
        self._opened = False
        self.cv = (model_selection.StratifiedKFold(5, shuffle=True, random_state=seed) if task == "classification"
                   else model_selection.KFold(5, shuffle=True, random_state=seed))
        self.scoring = "accuracy" if task == "classification" else "neg_root_mean_squared_error"

    def baseline(self):
        base = dummy.DummyClassifier(strategy="most_frequent") if self.task == "classification" else dummy.DummyRegressor()
        return self.compare({"baseline": base}).iloc[0]

    def compare(self, models):
        rows = []
        for name, m in models.items():
            s = model_selection.cross_val_score(m, self.X_dev, self.y_dev, cv=self.cv, scoring=self.scoring)
            s = s if self.task == "classification" else -s
            rows.append({"model": name, "cv_mean": s.mean(), "cv_sd": s.std(ddof=1)})
        return pd.DataFrame(rows).sort_values("cv_mean", ascending=(self.task == "regression")).reset_index(drop=True)

    def learning_curve(self, model, sizes=(0.1, 0.25, 0.5, 0.75, 1.0)):
        n, tr, va = model_selection.learning_curve(model, self.X_dev, self.y_dev, train_sizes=list(sizes), cv=self.cv, scoring=self.scoring)
        sign = 1 if self.task == "classification" else -1
        lc = pd.DataFrame({"n_train": n, "train": sign * tr.mean(axis=1), "validation": sign * va.mean(axis=1)})
        lc["gap"] = (lc.train - lc.validation) if self.task == "classification" else (lc.validation - lc.train)
        return lc

    @staticmethod
    def diagnose(lc, task="regression"):
        last = lc.iloc[-1]
        err = (1 - last.validation) if task == "classification" else last.validation          # validation error, in the same units as the gap
        rel_gap = last.gap / max(abs(err), 1e-12)
        if rel_gap > 0.15:
            return "high variance (large gap between training and validation): more data, simpler model or regularisation"
        return "high bias or near the noise floor (small gap): more capacity or better features, not more data"

    def tune(self, model, grid):
        gs = model_selection.GridSearchCV(model, grid, cv=self.cv, scoring=self.scoring).fit(self.X_dev, self.y_dev)
        return gs.best_estimator_, gs.best_params_, abs(gs.best_score_)

    def final_test(self, model):
        if self._opened:
            raise TestSetAlreadyOpened("the test set was already used once; collect new data instead of tuning on it")
        self._opened = True
        model.fit(self.X_dev, self.y_dev)
        p = model.predict(self._X_test)
        if self.task == "regression":
            return {"RMSE": math.sqrt(metrics.mean_squared_error(self._y_test, p)), "MAE": metrics.mean_absolute_error(self._y_test, p), "R2": metrics.r2_score(self._y_test, p)}
        return {"accuracy": metrics.accuracy_score(self._y_test, p), "precision": metrics.precision_score(self._y_test, p, average="macro"),
                "recall": metrics.recall_score(self._y_test, p, average="macro"), "F1": metrics.f1_score(self._y_test, p, average="macro")}
'''
(tmp / "evalkit.py").write_text(EVALKIT)
sys.path.insert(0, str(tmp))
import evalkit
print("written:", len(EVALKIT.splitlines()), "lines")
```
```text
written: 65 lines
```

### 14.3 Using it on a regression problem

```python run
ev = evalkit.Evaluation(X_all.values, y_all.values, task="regression", seed=0)
print("development rows:", len(ev.y_dev), "| sealed test rows:", len(ev._y_test))
print("baseline RMSE:", round(float(ev.baseline().cv_mean), 2))
candidates = {
    "linear": linear_model.LinearRegression(),
    "ridge": pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.Ridge(alpha=1.0)),
    "tree (full depth)": tree.DecisionTreeRegressor(random_state=0),
    "forest": ensemble.RandomForestRegressor(n_estimators=100, random_state=0),
    "kNN (k=10)": pipeline.make_pipeline(preprocessing.StandardScaler(), neighbors.KNeighborsRegressor(10)),
}
print(ev.compare(candidates).round(2).to_string(index=False))
```
```text
development rows: 353 | sealed test rows: 89
baseline RMSE: 78.57
            model  cv_mean  cv_sd
            ridge  53.8100 2.1800
           linear  53.8500 2.1200
       kNN (k=10)  58.2600 3.9100
           forest  58.5500 3.3100
tree (full depth)  83.0100 4.6400
```

The full-depth tree (cross-validated RMSE 83) is even **worse than the baseline** (78.6): it memorises its training rows. Ridge and plain linear regression are statistically tied (the difference is far smaller than the fold-to-fold SD), and the forest and the neighbours sit in between. Now the diagnosis, the tuning and the single opening of the test set.

```python run
lc = ev.learning_curve(candidates["tree (full depth)"])
print(lc.round(2).to_string(index=False))
print("diagnosis (full tree):", evalkit.Evaluation.diagnose(lc))
lc2 = ev.learning_curve(candidates["ridge"])
print("\nridge:", evalkit.Evaluation.diagnose(lc2))

best, params, cv_rmse = ev.tune(pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.Ridge()), {"ridge__alpha": np.logspace(-2, 3, 11)})
print("\nbest ridge parameters:", {k: round(float(v), 3) for k, v in params.items()}, "| cv RMSE", round(cv_rmse, 2))
print("final test (opened once):", {k: round(v, 3) for k, v in ev.final_test(best).items()})
try:
    ev.final_test(best)
except evalkit.TestSetAlreadyOpened as e:
    print("second attempt refused:", e)
```
```text
 n_train   train  validation     gap
      28 -0.0000     89.0400 89.0400
      70 -0.0000     80.0500 80.0500
     141 -0.0000     71.6000 71.6000
     211 -0.0000     82.9200 82.9200
     282 -0.0000     83.0900 83.0900
diagnosis (full tree): high variance (large gap between training and validation): more data, simpler model or regularisation

ridge: high bias or near the noise floor (small gap): more capacity or better features, not more data

best ridge parameters: {'ridge__alpha': 10.0} | cv RMSE 53.74
final test (opened once): {'RMSE': 58.56, 'MAE': 46.123, 'R2': 0.331}
second attempt refused: the test set was already used once; collect new data instead of tuning on it
```

### 14.4 And on a classification problem

```python run
evc = evalkit.Evaluation(Xc.values, yc.values, task="classification", seed=0)
print("baseline accuracy:", round(float(evc.baseline().cv_mean), 3))
cands = {
    "logistic": pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression(max_iter=2000)),
    "tree (depth 3)": tree.DecisionTreeClassifier(max_depth=3, random_state=0),
    "tree (full)": tree.DecisionTreeClassifier(random_state=0),
    "forest": ensemble.RandomForestClassifier(n_estimators=200, random_state=0),
}
print(evc.compare(cands).round(3).to_string(index=False))
lcc = evc.learning_curve(cands["tree (full)"])
print(lcc.round(3).to_string(index=False))
print("diagnosis (full tree):", evalkit.Evaluation.diagnose(lcc, "classification"))
print("final test of the logistic model:", {k: round(v, 3) for k, v in evc.final_test(cands["logistic"]).items()})
```
```text
baseline accuracy: 0.626
         model  cv_mean  cv_sd
      logistic   0.9780 0.0110
        forest   0.9650 0.0240
   tree (full)   0.9430 0.0260
tree (depth 3)   0.9300 0.0400
 n_train  train  validation    gap
      36 1.0000      0.8970 0.1030
      91 1.0000      0.9140 0.0860
     182 1.0000      0.9230 0.0770
     273 1.0000      0.9430 0.0570
     364 1.0000      0.9430 0.0570
diagnosis (full tree): high variance (large gap between training and validation): more data, simpler model or regularisation
final test of the logistic model: {'accuracy': 0.982, 'precision': 0.986, 'recall': 0.976, 'F1': 0.981}
```

### 14.5 What to hand in, for your own version

1. `evalkit.py` plus a test file: a fake dataset where the right answer is known (a perfectly noisy target must give R² near 0; a deterministic target must give R² near 1), and a test that the second `final_test` raises.
2. A report on one dataset that is not in this chapter: baseline, at least four models, a learning curve for two of them with the diagnosis in words, the tuned finalist, the one test score, and a paragraph on what could still be wrong.
3. Extensions: a `GroupKFold` option, repeated cross-validation, a permutation test that shows the best model beats the baseline by more than chance, and a confidence interval for the test score by bootstrap (ds.01, section 15).

## 15. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Scoring on the training data | a flattering number that says nothing about new data | always score held-out data (4) |
| Choosing the model with the test set | the test score becomes optimistic | validation or CV for choosing; the test set once (4, 10) |
| One lucky split | a score that moves by several points between seeds | cross-validation and an error bar (4.2, 9) |
| Believing training R² | rises with every added column | report cross-validated or test R² (11.3) |
| Accuracy on imbalanced classes | a useless model that looks excellent | confusion matrix, precision, recall, baseline (12.3) |
| Default 0.5 threshold | the wrong trade of misses against false alarms | choose the threshold from costs (12.4) |
| No baseline | no idea whether the model learned anything | always compare with a trivial model (3) |
| Fitting the scaler on all data, then splitting | information from the test rows leaks in | fit preprocessing inside the pipeline (ds.04) |
| Random folds for grouped or time-ordered data | inflated scores | `GroupKFold`, time-based splits (9.3, ds.04) |
| Reporting the best of many cross-validated scores | optimism from the maximum | nested CV or a sealed test set (10.2) |
| Unscaled features with a penalty or distances | the large-scale column dominates | standardise inside a pipeline (8.2) |
| Using a deeper model because it fits better | overfitting | read the learning curve before adding capacity (7) |
| Collecting more data for an underfit model | no improvement | add capacity or features instead (5.3, 7) |
| Trusting lasso's selected features | unstable under correlation | stability checks; treat as a hint (8.4) |
| Judging clusters by inertia alone | always "more clusters is better" | silhouette, stability and meaning (13.2) |

## 16. Summary

- **Machine learning** finds a rule from examples. **Supervised** learning has a target (regression for numbers, classification for categories); **unsupervised** learning looks for structure without one (clustering, dimensionality reduction). **Parameters** are fitted; **hyperparameters** are chosen by you.
- The goal is **generalisation**: being right on unseen data. Always compare with a **baseline** (the mean, the majority class, a business rule).
- Use **three sets**: training to fit, validation to choose, **test** to report once. A single split is noisy; **k-fold cross-validation** uses all rows and gives an error bar. Stratify for classes, group for repeated entities, keep the time order for time series. Choose hyperparameters with a search, and use **nested cross-validation** or the sealed test set to avoid reporting the optimism of the best of many.
- **Overfitting** is learning the noise: training error keeps falling while validation error turns upward. **Underfitting** is a model too simple for the signal. The error splits into **bias², variance and noise**; flexibility lowers bias and raises variance, and the best model sits in between.
- A **learning curve** (training and validation error against the number of training rows) diagnoses which problem you have: a large gap that narrows with data is variance (more data, simpler model, regularisation); two high, flat, close curves are bias (more capacity or better features, not more data). That is how you **explain overfitting using a learning curve**.
- **Regularisation** adds a penalty on coefficient size: **ridge** shrinks all coefficients (closed form `(XᵀX + αI)⁻¹Xᵀy`), **lasso** sets some to exactly zero. Scale features first and choose `α` by cross-validation.
- **Regression metrics**: MAE (robust), RMSE (punishes big misses), R² (share of variance explained; negative if worse than the mean; training R² is meaningless) and MAPE (trouble near zero). Look at residuals.
- **Classification metrics** come from the confusion matrix: accuracy (misleading when classes are unequal), precision, recall, F1, with a threshold that trades them off; the ROC curve and **AUC** measure ranking; **log loss** judges the probabilities. Pick by the cost of each kind of error.
- **Unsupervised** methods have no answer key: k-means (restarts, silhouette), PCA (explained variance). Judge them by stability and meaning.
- The **evaluation framework** of the project turns all of this into a workflow that refuses to open the test set twice.

You reached the outcome of this chapter: you can **explain overfitting using a learning curve**, with the polynomial, tree and 65-feature experiments as evidence, the bias-variance decomposition measured by simulation, and a framework that diagnoses the curve for you. Next (ds.04) turns the same discipline on its hardest enemy: data leakage.
