# Chapter 6 (DS): ML algorithms, from scratch and with libraries

In ds.05 every model was a box with a `fit` and a `predict`. You learned to wire boxes together, feed them clean data, tune them and judge them honestly. This chapter opens the boxes. For each of the classic algorithms you will learn **the idea** (what the model believes about the world), **the fitting rule** (how it turns data into parameters), **an implementation in NumPy from scratch**, and then the most important step: a **check that your version gives the same answers as scikit-learn** on the same data. When two independent implementations agree to ten decimal places, you understand the algorithm. When they disagree, the difference teaches you a detail that no textbook mentions (a tie-breaking rule, a float32 conversion, a variance that divides by n instead of n−1).

You will build linear and logistic regression with gradient descent and Newton's method, k-nearest neighbours, two kinds of Naive Bayes, a decision tree, a random forest, gradient boosting, a linear support vector machine, k-means, DBSCAN, hierarchical clustering and PCA. Then you meet t-SNE (and UMAP) and learn the one thing everybody gets wrong about them: **the distances in the picture do not mean what they seem to mean**. By the end you reach the outcomes of the syllabus: **implement three algorithms from scratch and match scikit-learn's results**, and **explain why distances in a t-SNE plot are not meaningful**.

Prerequisites: ds.05 (the estimator API, pipelines), ds.03 (bias, variance, regularisation), ds.01 (gradients, eigenvectors, SVD, probability). When a formula appears, the code beside it computes it.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, pandas, SciPy and scikit-learn. **XGBoost, LightGBM and UMAP are not installed** in this environment, so their code is shown as *Try it on your machine* with no invented output; scikit-learn's `HistGradientBoosting` (the same histogram idea as LightGBM) runs in their place. Data are synthetic and seeded, or ship inside scikit-learn (`load_iris`, `load_digits`, `load_breast_cancer`). Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, warnings
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy import special, stats
from scipy.cluster import hierarchy
from sklearn import (cluster, datasets, decomposition, ensemble, feature_extraction, linear_model, manifold, metrics,
                     model_selection, naive_bayes, neighbors, pipeline, preprocessing, svm, tree)

np.set_printoptions(precision=5, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.float_format", lambda v: f"{v:,.5f}")
warnings.filterwarnings("ignore")
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__)
print("scipy  ", scipy.__version__)
print("sklearn", sklearn.__version__)
```
```text
python  3.14.4
numpy   2.5.4
scipy   1.18.1
sklearn 1.9.1
```

## Table of contents

1. [How to implement an algorithm and prove it is right](#1-how-to-implement-an-algorithm-and-prove-it-is-right)
2. [Linear regression: normal equation and gradient descent](#2-linear-regression-normal-equation-and-gradient-descent)
3. [Logistic regression: gradient descent and Newton's method](#3-logistic-regression-gradient-descent-and-newtons-method)
4. [k-nearest neighbours](#4-k-nearest-neighbours)
5. [Naive Bayes](#5-naive-bayes)
6. [Decision trees](#6-decision-trees)
7. [Random forests](#7-random-forests)
8. [Gradient boosting](#8-gradient-boosting)
9. [Support vector machines](#9-support-vector-machines)
10. [Clustering: k-means, DBSCAN, hierarchical](#10-clustering-k-means-dbscan-hierarchical)
11. [PCA for compression and feature reduction](#11-pca-for-compression-and-feature-reduction)
12. [t-SNE and UMAP: for looking, not for measuring](#12-t-sne-and-umap-for-looking-not-for-measuring)
13. [Project: a from-scratch library checked against scikit-learn](#13-project-a-from-scratch-library-checked-against-scikit-learn)
14. [Common traps](#14-common-traps)
15. [Summary](#15-summary)

## 1. How to implement an algorithm and prove it is right

### 1.1 Why implement what already exists?

scikit-learn's versions are faster, better tested and more complete than anything you will write in an afternoon. You implement them anyway, for three reasons:

1. **Understanding.** You cannot reason about why a model fails (why k-NN collapses with 200 features, why a tree overfits, why gradient descent diverges) until you have seen the moving parts.
2. **Reading the documentation.** Parameters such as `C`, `var_smoothing`, `min_samples_leaf` or `perplexity` stop being magic words once you have written the line of code they control.
3. **Interviews and research.** "Implement logistic regression" or "write k-means" are standard questions, and new methods are always variations on these.

### 1.2 The method: implement, then match

For every algorithm in this chapter we follow the same four steps.

1. **State the objective.** What quantity does the algorithm minimise or what rule does it follow? Write it as a formula.
2. **Implement it plainly** with NumPy. Clarity first; vectorise only where the loop would be painfully slow.
3. **Run both versions on the same data**, with the library configured to solve *the same problem* (same penalty, same initialisation, no randomness or the same seed).
4. **Compare at the right level.** Not every algorithm can match to the last digit:

| Level of agreement | When to expect it | Example |
|---|---|---|
| **Exact** (to about 1e-10) | deterministic algorithm, same objective, convex problem or same starting point | linear/logistic regression, Naive Bayes, k-NN, k-means with the same start, PCA, gradient boosting on the same trees |
| **Structural** | same procedure with tie-breaking freedom | decision trees (same splits unless two splits tie), DBSCAN (border points between two clusters) |
| **Statistical** | randomised algorithm | random forests: different random draws, similar accuracy |
| **Approximate** | iterative solver stopped early, non-smooth objective | SVM by sub-gradient descent: close weights, near-identical predictions |

A disagreement is never "fine, close enough" until you can say *which* row of this table explains it.

### 1.3 A comparison helper

```python run
def compare(name, ours, theirs, tol=1e-6):
    ours, theirs = np.asarray(ours, dtype=float), np.asarray(theirs, dtype=float)
    diff = float(np.max(np.abs(ours - theirs))) if ours.size else 0.0
    verdict = "MATCH" if diff <= tol else "DIFFERENT"
    print(f"{name:42s} max |ours - sklearn| = {diff:.2e}  -> {verdict}")
    return diff
```

## 2. Linear regression: normal equation and gradient descent

### 2.1 The model and the objective

Linear regression predicts `ŷ = Xw + b`. It chooses `w` and `b` to minimise the **mean squared error**

```text
L(w, b) = (1/n) Σ (y_i − x_i·w − b)²
```

A convenient trick: add a column of ones to `X` so the intercept `b` becomes just another weight. Call that matrix `X̃` and the weights `θ = (b, w)`.

### 2.2 Data with a known answer

```python run
rng = np.random.default_rng(0)
n, d = 500, 3
X_lin = rng.normal(0, 1, (n, d)) * [1.0, 10.0, 0.1] + [0, 50, 0]        # very different scales, on purpose
true_w, true_b = np.array([2.0, -0.3, 15.0]), 4.0
y_lin = X_lin @ true_w + true_b + rng.normal(0, 1.0, n)
print("column means:", X_lin.mean(0).round(2), "| column stds:", X_lin.std(0).round(3))
```
```text
column means: [-0.13 50.8   0.  ] | column stds: [0.979 9.566 0.102]
```

### 2.3 The closed form: normal equations

Setting the gradient of `L` to zero gives the **normal equations** `X̃ᵀX̃ θ = X̃ᵀy`. Solving them directly is the exact answer. In practice you never invert `X̃ᵀX̃`; you use a least-squares solver, which is numerically safer.

```python run
def add_ones(X):
    return np.column_stack([np.ones(len(X)), X])

theta_ne = np.linalg.solve(add_ones(X_lin).T @ add_ones(X_lin), add_ones(X_lin).T @ y_lin)   # normal equations
theta_ls = np.linalg.lstsq(add_ones(X_lin), y_lin, rcond=None)[0]                             # the safer way
sk_lin = linear_model.LinearRegression().fit(X_lin, y_lin)
print("ours (lstsq)  b, w:", theta_ls.round(5))
print("sklearn       b, w:", np.r_[sk_lin.intercept_, sk_lin.coef_].round(5))
compare("normal equations vs lstsq", theta_ne, theta_ls)
compare("linear regression, lstsq", theta_ls, np.r_[sk_lin.intercept_, sk_lin.coef_])
```
```text
ours (lstsq)  b, w: [ 3.87013  2.04111 -0.29866 15.62853]
sklearn       b, w: [ 3.87013  2.04111 -0.29866 15.62853]
normal equations vs lstsq                  max |ours - sklearn| = 6.62e-14  -> MATCH
linear regression, lstsq                   max |ours - sklearn| = 3.38e-14  -> MATCH
```

The closed form costs about `n·d² + d³` operations. That is cheap for 3 columns and impossible for a million columns or data that does not fit in memory. Hence gradient descent.

### 2.4 Gradient descent

The gradient of the mean squared error with respect to `θ` is

```text
∇L(θ) = (2/n) X̃ᵀ (X̃θ − y)
```

Gradient descent starts somewhere and repeatedly takes a step **downhill**: `θ ← θ − η ∇L(θ)`, where `η` (eta) is the **learning rate**.

```python run
def linreg_gd(X, y, lr=0.1, epochs=1000, tol=1e-10):
    Xt = add_ones(X)
    theta = np.zeros(Xt.shape[1])
    history = []
    for epoch in range(epochs):
        resid = Xt @ theta - y
        loss = float(np.mean(resid ** 2))
        history.append(loss)
        grad = 2 / len(y) * Xt.T @ resid
        theta -= lr * grad
        if np.max(np.abs(grad)) < tol:                  # stop when the slope is (almost) flat
            break
    return theta, history

theta_raw, hist_raw = linreg_gd(X_lin, y_lin, lr=0.0002, epochs=5000)
print(f"raw features, lr=0.0002: {len(hist_raw)} epochs, final loss {hist_raw[-1]:.4f}, theta {theta_raw.round(3)}")
```
```text
raw features, lr=0.0002: 5000 epochs, final loss 4.0201, theta [ 0.236  1.69  -0.23   0.318]
```

On the raw features gradient descent crawls: after 5,000 steps it is still far from the answer. The reason is **scale**. The second column varies by about 10, the third by about 0.1. The loss surface is a long, thin valley; a step size small enough not to explode along the steep direction is far too small along the flat one.

> **Predict the output.** 0.0002 looks tiny. What happens if we raise the learning rate to 0.001 on the raw features?

<details><summary>Answer</summary>

It **diverges**: the loss grows without limit, because along the steep direction (the column with a standard deviation of 10 and a mean of 50) every step overshoots the bottom by more than it started.

```python run
_, hist_big = linreg_gd(X_lin, y_lin, lr=0.001, epochs=8)
print("loss for the first 8 epochs:", [f"{v:.3g}" for v in hist_big])
```
```text
loss for the first 8 epochs: ['149', '2.67e+03', '5.03e+04', '9.5e+05', '1.79e+07', '3.39e+08', '6.4e+09', '1.21e+11']
```

</details>

### 2.5 Scaling fixes the valley

Standardise the features (ds.05 section 3.1), run gradient descent, then convert the weights back to the original units: if `z = (x − μ)/σ` then `w_original = w_z / σ` and `b_original = b_z − Σ w_z μ / σ`.

```python run
mu, sigma = X_lin.mean(0), X_lin.std(0)
theta_z, hist_z = linreg_gd((X_lin - mu) / sigma, y_lin, lr=0.1, epochs=5000)
w_back = theta_z[1:] / sigma
b_back = theta_z[0] - np.sum(theta_z[1:] * mu / sigma)
print(f"standardised, lr=0.1: {len(hist_z)} epochs, final loss {hist_z[-1]:.6f}")
compare("GD on standardised data, back-converted", np.r_[b_back, w_back], np.r_[sk_lin.intercept_, sk_lin.coef_])
```
```text
standardised, lr=0.1: 119 epochs, final loss 1.058742
GD on standardised data, back-converted    max |ours - sklearn| = 1.13e-10  -> MATCH
```

From thousands of crawling steps to a few dozen, with the exact answer. **Scale your features before any gradient-based method.**

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw two contour plots of a linear regression loss over two weights. Left: raw features (one column varies by about 10, another by about 0.1), so the contours are a long thin valley, and gradient descent zig-zags across it very slowly (5,000 steps, learning rate 0.0002, still not finished). Right: standardised features, round contours, and a short straight path reaching the minimum in 119 steps (learning rate 0.1). Label both paths and the minimum."

### 2.6 Stochastic and mini-batch gradient descent

Batch gradient descent reads every row for every step. **Stochastic gradient descent (SGD)** uses one row, **mini-batch** uses a small group (32, 256 rows). Each step is noisy but cheap, so on big data you get to a good region far sooner. The noise also means the iterates never settle exactly: you shrink the learning rate over time.

```python run
def linreg_minibatch(X, y, lr=0.05, epochs=50, batch=32, seed=0):
    r = np.random.default_rng(seed)
    Xt = add_ones(X)
    theta = np.zeros(Xt.shape[1])
    for epoch in range(epochs):
        order = r.permutation(len(y))
        step = lr / (1 + 0.1 * epoch)                      # decaying learning rate
        for start in range(0, len(y), batch):
            idx = order[start:start + batch]
            grad = 2 / len(idx) * Xt[idx].T @ (Xt[idx] @ theta - y[idx])
            theta -= step * grad
    return theta

theta_mb = linreg_minibatch((X_lin - mu) / sigma, y_lin)
mb_back = np.r_[theta_mb[0] - np.sum(theta_mb[1:] * mu / sigma), theta_mb[1:] / sigma]
compare("mini-batch GD (approximate by nature)", mb_back, np.r_[sk_lin.intercept_, sk_lin.coef_], tol=0.05)
sgd = pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.SGDRegressor(alpha=0.0, max_iter=200, tol=None, random_state=0)).fit(X_lin, y_lin)
print("sklearn SGDRegressor, training R²:", round(sgd.score(X_lin, y_lin), 5), "| exact solution R²:", round(sk_lin.score(X_lin, y_lin), 5))
```
```text
mini-batch GD (approximate by nature)      max |ours - sklearn| = 2.25e-03  -> MATCH
sklearn SGDRegressor, training R²: 0.93104 | exact solution R²: 0.93104
```

Mini-batch agrees to about two decimal places, which is the honest level for a noisy method (row 4 of the table in 1.2). scikit-learn's `SGDRegressor` is the library version of the same idea.

### 2.7 Ridge: adding the penalty

Ridge (ds.03 section 8) minimises `‖y − Xw − b‖² + α‖w‖²`. scikit-learn does **not** penalise the intercept, which it handles by centring `X` and `y` first. The closed form on centred data is `w = (XcᵀXc + αI)⁻¹ Xcᵀyc`, and `b = ȳ − x̄·w`.

```python run
def ridge_closed(X, y, alpha):
    xm, ym = X.mean(0), y.mean()
    Xc, yc = X - xm, y - ym
    w = np.linalg.solve(Xc.T @ Xc + alpha * np.eye(X.shape[1]), Xc.T @ yc)
    return ym - xm @ w, w

for alpha in [0.1, 10.0, 1000.0]:
    b, w = ridge_closed(X_lin, y_lin, alpha)
    skr = linear_model.Ridge(alpha=alpha).fit(X_lin, y_lin)
    compare(f"ridge alpha={alpha:g}", np.r_[b, w], np.r_[skr.intercept_, skr.coef_], tol=1e-8)
b_bad, w_bad = (lambda t: (t[0], t[1:]))(np.linalg.solve(add_ones(X_lin).T @ add_ones(X_lin) + 1000 * np.eye(4), add_ones(X_lin).T @ y_lin))
print("if we also penalised the intercept (alpha=1000):", round(b_bad, 3), "instead of", round(linear_model.Ridge(alpha=1000).fit(X_lin, y_lin).intercept_, 3))
```
```text
ridge alpha=0.1                            max |ours - sklearn| = 1.78e-15  -> MATCH
ridge alpha=10                             max |ours - sklearn| = 3.55e-15  -> MATCH
ridge alpha=1000                           max |ours - sklearn| = 3.55e-15  -> MATCH
if we also penalised the intercept (alpha=1000): 0.055 instead of 3.188
```

The last line shows the detail that makes a naive implementation disagree with the library: penalising the intercept drags it toward zero, which makes no sense (the intercept only says where the data are centred).

### 2.8 Try it

1. Implement gradient descent for ridge (add `2αw/n` to the gradient of the weights, not of the intercept) and match `Ridge(alpha=10)`. Remember that our loss is the *mean* and scikit-learn's is the *sum*: how must `α` be scaled?
2. Plot (or print every 10th value of) `hist_z` for learning rates 0.01, 0.1, 0.5 and 1.0. Which converges fastest, and which diverges?

## 3. Logistic regression: gradient descent and Newton's method

### 3.1 The model

Logistic regression models the probability of class 1 as `p = σ(x·w + b)` where `σ(z) = 1 / (1 + e^(−z))`, the **sigmoid**. It squashes any number into (0, 1). The fitting rule is **maximum likelihood**: choose `w, b` that make the observed labels most probable, which is the same as minimising the **log loss** (cross-entropy)

```text
L(w, b) = − Σ [ y_i log p_i + (1 − y_i) log(1 − p_i) ]
```

scikit-learn adds an L2 penalty by default, with the strength set by `C` (bigger `C` = weaker penalty), and does not penalise the intercept:

```text
objective(w, b) = ½ ‖w‖²  +  C · Σ logloss_i
```

### 3.2 The gradient is beautifully simple

The derivative of the log loss with respect to the linear score `z` is just `p − y`. So the gradient of the whole objective is

```text
∇_θ = C · X̃ᵀ (p − y)  +  (0, w)          (the penalty adds w to every weight except the intercept)
```

```python run
def sigmoid(z):
    return special.expit(z)                       # a numerically safe 1/(1+exp(-z))

rng = np.random.default_rng(1)
X_log = rng.normal(0, 1, (400, 3))
y_log = (rng.random(400) < sigmoid(X_log @ [1.5, -2.0, 0.5] + 0.3)).astype(int)
Xs_log = preprocessing.StandardScaler().fit_transform(X_log)

def logreg_objective(theta, X, y, C):
    z = add_ones(X) @ theta
    return 0.5 * theta[1:] @ theta[1:] + C * np.sum(np.logaddexp(0, z) - y * z)   # stable log loss

def logreg_gd(X, y, C=1.0, lr=None, epochs=20000, tol=1e-12):
    Xt = add_ones(X)
    theta = np.zeros(Xt.shape[1])
    lr = lr or 1.0 / (C * len(y))                 # a safe step for this objective (see Try it)
    for epoch in range(epochs):
        p = sigmoid(Xt @ theta)
        grad = C * Xt.T @ (p - y)
        grad[1:] += theta[1:]
        theta -= lr * grad
        if np.max(np.abs(grad)) < tol:
            break
    return theta, epoch + 1

theta_gd, steps = logreg_gd(Xs_log, y_log, C=0.5)
sk_log = linear_model.LogisticRegression(C=0.5, tol=1e-12, max_iter=10000).fit(Xs_log, y_log)
print("gradient descent steps:", steps)
compare("logistic regression, gradient descent", theta_gd, np.r_[sk_log.intercept_, sk_log.coef_[0]], tol=1e-6)
```
```text
gradient descent steps: 598
logistic regression, gradient descent      max |ours - sklearn| = 1.35e-09  -> MATCH
```

### 3.3 Newton's method: curvature makes it fast

Gradient descent uses the slope only. **Newton's method** also uses the curvature (the matrix of second derivatives, the *Hessian* `H`) and jumps to the bottom of the local quadratic approximation: `θ ← θ − H⁻¹∇`. For logistic regression

```text
H = C · X̃ᵀ diag(p(1 − p)) X̃  +  diag(0, 1, 1, …, 1)
```

Near the answer Newton's method doubles the number of correct digits at every step (**quadratic convergence**). Each step costs a `d × d` solve, so it suits problems with up to a few thousand columns. scikit-learn's `newton-cholesky` solver is exactly this; its default `lbfgs` approximates the Hessian cheaply.

```python run
def logreg_newton(X, y, C=1.0, steps=25, verbose=False):
    Xt = add_ones(X)
    theta = np.zeros(Xt.shape[1])
    for k in range(steps):
        p = sigmoid(Xt @ theta)
        grad = C * Xt.T @ (p - y)
        grad[1:] += theta[1:]
        H = C * (Xt.T * (p * (1 - p))) @ Xt
        H[1:, 1:] += np.eye(Xt.shape[1] - 1)
        theta = theta - np.linalg.solve(H, grad)
        if verbose:
            print(f"step {k + 1}: gradient size {np.max(np.abs(grad)):.2e}, objective {logreg_objective(theta, X, y, C):.10f}")
    return theta

theta_nt = logreg_newton(Xs_log, y_log, C=0.5, steps=7, verbose=True)
compare("logistic regression, Newton (7 steps)", theta_nt, np.r_[sk_log.intercept_, sk_log.coef_[0]], tol=1e-6)
compare("predict_proba, Newton", sigmoid(add_ones(Xs_log) @ theta_nt), sk_log.predict_proba(Xs_log)[:, 1], tol=1e-6)
```
```text
step 1: gradient size 5.14e+01, objective 86.5156274710
step 2: gradient size 1.25e+01, objective 79.3607378045
step 3: gradient size 3.18e+00, objective 78.6023719473
step 4: gradient size 3.84e-01, objective 78.5896924548
step 5: gradient size 7.17e-03, objective 78.5896881422
step 6: gradient size 2.53e-06, objective 78.5896881422
step 7: gradient size 3.10e-13, objective 78.5896881422
logistic regression, Newton (7 steps)      max |ours - sklearn| = 1.35e-09  -> MATCH
predict_proba, Newton                      max |ours - sklearn| = 7.74e-10  -> MATCH
```

Watch the gradient size column: it falls by a few times per step at first (51, 12.5, 3.2, 0.38) and then collapses (7e-3, 2.5e-6, 3e-13): near the answer the number of correct digits roughly doubles at each step. That is quadratic convergence, and it is why seven Newton steps beat thousands of gradient steps.

### 3.4 What `C` does

```python run
for C in [0.001, 0.01, 0.1, 1.0, 100.0]:
    th = logreg_newton(Xs_log, y_log, C=C)
    print(f"C={C:<7g} weights {th[1:].round(3)}  |weights| = {np.linalg.norm(th[1:]):.3f}")
```
```text
C=0.001   weights [ 0.078 -0.093  0.028]  |weights| = 0.125
C=0.01    weights [ 0.449 -0.535  0.144]  |weights| = 0.714
C=0.1     weights [ 1.142 -1.353  0.322]  |weights| = 1.799
C=1       weights [ 1.596 -1.894  0.43 ]  |weights| = 2.513
C=100     weights [ 1.702 -2.021  0.455]  |weights| = 2.681
```

Small `C` = strong penalty = weights near zero = a cautious, high-bias model. Large `C` approaches plain maximum likelihood. On perfectly separable data, plain maximum likelihood has no finite answer: the weights grow forever, which is one more reason the default has a penalty.

### 3.5 More than two classes: softmax

With `K` classes, multinomial logistic regression gives each class its own weight vector and turns the `K` scores into probabilities with the **softmax** `p_k = e^(z_k) / Σ_j e^(z_j)`. The gradient for class `k` is again `X̃ᵀ(p_k − y_k)` with one-hot `y`. scikit-learn's `LogisticRegression` uses softmax for more than two classes.

```python run
iris = datasets.load_iris()
Xi = preprocessing.StandardScaler().fit_transform(iris.data)
yi = iris.target
Y = np.eye(3)[yi]                                  # one-hot labels
C = 1.0
Wt = np.zeros((5, 3))                              # (intercept + 4 features) x 3 classes
Xit = add_ones(Xi)
for epoch in range(30000):
    P = special.softmax(Xit @ Wt, axis=1)
    G = C * Xit.T @ (P - Y)
    G[1:] += Wt[1:]
    Wt -= 0.004 * G
sk_soft = linear_model.LogisticRegression(C=C, tol=1e-12, max_iter=10000).fit(Xi, yi)
P_ours = special.softmax(Xit @ Wt, axis=1)
compare("softmax regression, predict_proba", P_ours, sk_soft.predict_proba(Xi), tol=1e-4)
print("note: weights are only defined up to adding the same vector to every class; probabilities are not")
```
```text
softmax regression, predict_proba          max |ours - sklearn| = 7.72e-08  -> MATCH
note: weights are only defined up to adding the same vector to every class; probabilities are not
```

The note matters: with softmax, adding the same number to every class's score leaves the probabilities unchanged, so weight vectors can differ between implementations while the predictions agree. Compare **predictions**, not raw parameters, when a model has this kind of symmetry. (Here the L2 penalty actually pins the weights down too, but the habit is worth keeping.)

### 3.6 Try it

1. The step size `1/(C·n)` in `logreg_gd` is safe because the log loss curvature is at most `¼` per row. Try `lr = 4/(C·n)` and `lr = 20/(C·n)`. Which converges, which oscillates?
2. Change `logreg_newton` so that it penalises the intercept too, and compare the intercept with scikit-learn's. Which line of the code did you change?


## 4. k-nearest neighbours

### 4.1 The idea: no training at all

k-NN keeps the whole training set. To predict a new point it finds the `k` training points **closest** to it and lets them vote (classification) or averages their targets (regression). There are no parameters to fit; all the work happens at prediction time. Its one belief about the world is: *similar inputs have similar outputs*, where "similar" means "close in Euclidean distance".

### 4.2 Implementation

The squared distance between every test row `a` and every training row `b` can be computed without loops: `‖a − b‖² = ‖a‖² − 2a·b + ‖b‖²`.

```python run
def pairwise_sq_dist(A, B):
    d2 = (A ** 2).sum(1)[:, None] - 2 * A @ B.T + (B ** 2).sum(1)[None, :]
    return np.maximum(d2, 0)                         # rounding can give tiny negatives

class KNN:
    def __init__(self, k=5, task="classification"):
        self.k, self.task = k, task
    def fit(self, X, y):
        self.X_, self.y_ = np.asarray(X, float), np.asarray(y)
        self.classes_ = np.unique(self.y_) if self.task == "classification" else None
        return self
    def _neighbours(self, X):
        d2 = pairwise_sq_dist(np.asarray(X, float), self.X_)
        return np.argsort(d2, axis=1, kind="stable")[:, : self.k]
    def predict_proba(self, X):
        nb = self.y_[self._neighbours(X)]
        return np.stack([(nb == c).mean(1) for c in self.classes_], axis=1)
    def predict(self, X):
        if self.task == "regression":
            return self.y_[self._neighbours(X)].mean(1)
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]      # a tie goes to the smallest label

cancer = datasets.load_breast_cancer()
Xc_tr, Xc_te, yc_tr, yc_te = model_selection.train_test_split(cancer.data, cancer.target, test_size=0.3, random_state=0, stratify=cancer.target)
sc_c = preprocessing.StandardScaler().fit(Xc_tr)
Zc_tr, Zc_te = sc_c.transform(Xc_tr), sc_c.transform(Xc_te)
for k in [1, 5, 15]:
    ours = KNN(k).fit(Zc_tr, yc_tr)
    sk = neighbors.KNeighborsClassifier(n_neighbors=k, algorithm="brute").fit(Zc_tr, yc_tr)
    compare(f"k-NN k={k}, predict_proba", ours.predict_proba(Zc_te), sk.predict_proba(Zc_te), tol=1e-12)
    print(f"   test accuracy ours {np.mean(ours.predict(Zc_te) == yc_te):.4f} | sklearn {sk.score(Zc_te, yc_te):.4f}")
```
```text
k-NN k=1, predict_proba                    max |ours - sklearn| = 0.00e+00  -> MATCH
   test accuracy ours 0.9474 | sklearn 0.9474
k-NN k=5, predict_proba                    max |ours - sklearn| = 0.00e+00  -> MATCH
   test accuracy ours 0.9474 | sklearn 0.9474
k-NN k=15, predict_proba                   max |ours - sklearn| = 0.00e+00  -> MATCH
   test accuracy ours 0.9415 | sklearn 0.9415
```

`algorithm="brute"` makes scikit-learn compute all distances like we do. Its other options (`kd_tree`, `ball_tree`) give the same neighbours faster, by organising the training points in a tree so most of them can be skipped.

### 4.3 Choosing k: bias and variance in one number

Small `k` follows every wiggle (low bias, high variance); `k = 1` scores 100% on its own training set. Large `k` smooths everything (high bias). Choose it by cross-validation, as always.

```python run
ks = [1, 3, 5, 9, 15, 25, 51, 101]
cv_acc = [model_selection.cross_val_score(pipeline.make_pipeline(preprocessing.StandardScaler(), neighbors.KNeighborsClassifier(k)), Xc_tr, yc_tr, cv=5).mean() for k in ks]
print(pd.DataFrame({"k": ks, "CV accuracy": cv_acc}).to_string(index=False))
```
```text
  k  CV accuracy
  1      0.94991
  3      0.96234
  5      0.96741
  9      0.96737
 15      0.96487
 25      0.95728
 51      0.93225
101      0.91472
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot k-nearest-neighbours cross-validated accuracy against k for k = 1, 3, 5, 9, 15, 25, 51, 101 with accuracies 0.950, 0.962, 0.967, 0.967, 0.965, 0.957, 0.932, 0.915. Mark the best region around k = 5 to 9. Annotate the left side as 'low bias, high variance, wiggly boundary' and the right side as 'high bias, over-smooth boundary'. Add two small sketches of a decision boundary for k = 1 and k = 101."

### 4.4 Scaling is not optional

Distances add up squared differences, so a column measured in thousands drowns a column measured in fractions. The cancer data mix areas (hundreds to thousands) with smoothness values (around 0.1).

```python run
raw = model_selection.cross_val_score(neighbors.KNeighborsClassifier(5), Xc_tr, yc_tr, cv=5).mean()
scaled = model_selection.cross_val_score(pipeline.make_pipeline(preprocessing.StandardScaler(), neighbors.KNeighborsClassifier(5)), Xc_tr, yc_tr, cv=5).mean()
print(f"k-NN on raw columns: {raw:.4f} | on standardised columns: {scaled:.4f}")
print("ranges of two columns:", cancer.feature_names[3], np.ptp(cancer.data[:, 3]).round(1), "vs", cancer.feature_names[4], np.ptp(cancer.data[:, 4]).round(3))
```
```text
k-NN on raw columns: 0.9372 | on standardised columns: 0.9674
ranges of two columns: mean area 2357.5 vs mean smoothness 0.111
```

### 4.5 The curse of dimensionality

In many dimensions, points drift apart and **all distances become alike**. If the nearest neighbour is almost as far as the farthest one, "nearest" stops meaning "similar".

```python run
rng = np.random.default_rng(0)
rows = []
for dim in [2, 10, 100, 1000]:
    P = rng.random((500, dim))
    d = np.sqrt(pairwise_sq_dist(P[:1], P[1:]))[0]
    rows.append((dim, d.min(), d.max(), d.min() / d.max()))
print(pd.DataFrame(rows, columns=["dimensions", "nearest", "farthest", "nearest / farthest"]).round(3).to_string(index=False))
```
```text
 dimensions  nearest  farthest  nearest / farthest
          2  0.01400   0.93700             0.01500
         10  0.57800   1.91800             0.30200
        100  3.63400   4.95300             0.73400
       1000 12.29500  13.61800             0.90300
```

In 2 dimensions the nearest point is much closer than the farthest; in 1,000 dimensions the ratio approaches 1. k-NN needs few, informative features, or a dimension reduction first (section 11).

### 4.6 Try it

1. Add `weights="distance"` behaviour to `KNN` (each neighbour votes with weight `1/distance`) and match `KNeighborsClassifier(weights="distance")`.
2. Use `KNN(task="regression")` on the `X_lin, y_lin` data of section 2 and compare with `KNeighborsRegressor`. Why is k-NN much worse than linear regression there?

## 5. Naive Bayes

### 5.1 The idea: Bayes' rule with a bold shortcut

Bayes' rule (ds.01) gives the probability of class `c` given features `x`:

```text
P(c | x)  ∝  P(c) · P(x | c)
```

`P(x | c)`, the joint distribution of all features within a class, is impossible to estimate with many features. The "naive" shortcut assumes the features are **independent within each class**, so `P(x | c) = Π_j P(x_j | c)`, a product of one-dimensional distributions that are easy to estimate. The assumption is almost always false, yet the classifier often ranks well, trains in one pass and works with tiny data. Its probabilities are usually over-confident (multiplying many "independent" pieces of evidence counts the same evidence several times).

We work with logarithms to turn the product into a sum and avoid numbers too small for a float: `log P(c | x) = log P(c) + Σ_j log P(x_j | c) − log Z`.

### 5.2 Gaussian Naive Bayes

For numeric features, assume each feature is normal within each class, with its own mean and variance. Fitting means computing those means and variances per class. One detail from scikit-learn's source: a small amount, `var_smoothing × (largest feature variance)`, is added to every variance so that no variance is zero. Variances use `n`, not `n − 1`.

```python run
class GaussianNBScratch:
    def __init__(self, var_smoothing=1e-9):
        self.var_smoothing = var_smoothing
    def fit(self, X, y):
        X = np.asarray(X, float)
        self.classes_ = np.unique(y)
        eps = self.var_smoothing * np.var(X, axis=0).max()
        self.theta_ = np.array([X[y == c].mean(0) for c in self.classes_])
        self.var_ = np.array([X[y == c].var(0) for c in self.classes_]) + eps
        self.log_prior_ = np.log(np.array([np.mean(y == c) for c in self.classes_]))
        return self
    def _joint_log_likelihood(self, X):
        X = np.asarray(X, float)
        ll = -0.5 * np.sum(np.log(2 * np.pi * self.var_), axis=1)[None, :] \
             - 0.5 * (((X[:, None, :] - self.theta_[None]) ** 2) / self.var_[None]).sum(2)
        return ll + self.log_prior_
    def predict_proba(self, X):
        jll = self._joint_log_likelihood(X)
        return np.exp(jll - special.logsumexp(jll, axis=1, keepdims=True))
    def predict(self, X):
        return self.classes_[np.argmax(self._joint_log_likelihood(X), axis=1)]

gnb_ours = GaussianNBScratch().fit(Xc_tr, yc_tr)
gnb_sk = naive_bayes.GaussianNB().fit(Xc_tr, yc_tr)
compare("Gaussian NB, class means", gnb_ours.theta_, gnb_sk.theta_, tol=1e-9)
compare("Gaussian NB, variances", gnb_ours.var_, gnb_sk.var_, tol=1e-9)
compare("Gaussian NB, predict_proba", gnb_ours.predict_proba(Xc_te), gnb_sk.predict_proba(Xc_te), tol=1e-9)
print("test accuracy:", round(np.mean(gnb_ours.predict(Xc_te) == yc_te), 4))
```
```text
Gaussian NB, class means                   max |ours - sklearn| = 0.00e+00  -> MATCH
Gaussian NB, variances                     max |ours - sklearn| = 0.00e+00  -> MATCH
Gaussian NB, predict_proba                 max |ours - sklearn| = 0.00e+00  -> MATCH
test accuracy: 0.924
```

### 5.3 How over-confident?

```python run
p = gnb_ours.predict_proba(Xc_te)[:, 1]
print("share of test predictions above 0.999 or below 0.001:", round(float(np.mean((p > 0.999) | (p < 0.001))), 3))
print("Brier score: Naive Bayes", round(metrics.brier_score_loss(yc_te, p), 4), "| logistic regression",
      round(metrics.brier_score_loss(yc_te, pipeline.make_pipeline(preprocessing.StandardScaler(), linear_model.LogisticRegression(max_iter=5000)).fit(Xc_tr, yc_tr).predict_proba(Xc_te)[:, 1]), 4))
```
```text
share of test predictions above 0.999 or below 0.001: 0.93
Brier score: Naive Bayes 0.076 | logistic regression 0.0265
```

The 30 cancer features are strongly correlated (radius, perimeter and area measure nearly the same thing), so Naive Bayes counts the same evidence many times and becomes extremely sure of itself. Use its ranking; calibrate its probabilities if you need them (ds.04 section 11).

### 5.4 Multinomial Naive Bayes for text

For word counts, each class has a probability for every word, `P(word | class)`, estimated from counts. A word never seen in a class would get probability 0 and veto the class entirely; **Laplace smoothing** adds `α` (usually 1) to every count:

```text
P(word j | class c) = (count_cj + α) / (Σ_j count_cj + α · vocabulary size)
```

```python run
rng = np.random.default_rng(3)
spam_words = "win free prize money click offer cash urgent winner claim".split()
ham_words = "meeting project report tomorrow lunch thanks schedule review notes call".split()
common = "the a you your we for this is today please".split()
def message(words):
    return " ".join(rng.choice(words + common, rng.integers(5, 12)))
texts = [message(spam_words) for _ in range(150)] + [message(ham_words) for _ in range(250)]
labels = np.array([1] * 150 + [0] * 250)
cv_vec = feature_extraction.text.CountVectorizer()
counts = cv_vec.fit_transform(texts).toarray()

class MultinomialNBScratch:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
    def fit(self, X, y):
        self.classes_ = np.unique(y)
        fc = np.array([X[y == c].sum(0) for c in self.classes_]) + self.alpha
        self.feature_log_prob_ = np.log(fc / fc.sum(1, keepdims=True))
        self.class_log_prior_ = np.log(np.array([np.mean(y == c) for c in self.classes_]))
        return self
    def predict_proba(self, X):
        jll = X @ self.feature_log_prob_.T + self.class_log_prior_
        return np.exp(jll - special.logsumexp(jll, axis=1, keepdims=True))

mnb_ours = MultinomialNBScratch().fit(counts, labels)
mnb_sk = naive_bayes.MultinomialNB().fit(counts, labels)
compare("Multinomial NB, word log-probabilities", mnb_ours.feature_log_prob_, mnb_sk.feature_log_prob_, tol=1e-12)
new = cv_vec.transform(["free prize for you today", "project meeting notes tomorrow", "please call me about the offer"]).toarray()
compare("Multinomial NB, predict_proba", mnb_ours.predict_proba(new), mnb_sk.predict_proba(new), tol=1e-12)
print("P(spam) for three new messages:", mnb_ours.predict_proba(new)[:, 1].round(4))
```
```text
Multinomial NB, word log-probabilities     max |ours - sklearn| = 8.88e-16  -> MATCH
Multinomial NB, predict_proba              max |ours - sklearn| = 0.00e+00  -> MATCH
P(spam) for three new messages: [0.9997 0.     0.4922]
```

### 5.5 Try it

1. Set `alpha=1e-10` (almost no smoothing) and score a message that contains one spam word and one ham word. What happens to the probabilities?
2. Add a duplicate of every cancer feature (60 columns) and refit Gaussian NB. How does the Brier score change, and why does logistic regression not suffer the same way?

## 6. Decision trees

### 6.1 The idea: twenty questions

A decision tree asks a yes/no question about one feature ("is `mean radius` ≤ 15.0?"), splits the data in two, and asks again in each half, until the groups are pure enough. A prediction follows the questions down to a **leaf** and returns the leaf's majority class (or class shares, or the mean for regression).

Building the best possible tree is computationally hopeless, so every library uses the same **greedy** rule: at each node, try every feature and every threshold, and take the split that most reduces **impurity**; then recurse.

### 6.2 Impurity

For classification with class shares `p_k` in a node:

- **Gini impurity** `1 − Σ p_k²`: the chance that two random rows from the node have different labels.
- **Entropy** `−Σ p_k log₂ p_k`: information in bits.

For regression the impurity is the **variance** (mean squared error around the node mean). The gain of a split is the parent impurity minus the size-weighted impurity of the two children.

```python run
def gini(counts):
    p = counts / counts.sum()
    return 1 - np.sum(p ** 2)
for c in [[50, 50], [90, 10], [100, 0]]:
    print(f"class counts {c}: gini {gini(np.array(c, float)):.3f}")
```
```text
class counts [50, 50]: gini 0.500
class counts [90, 10]: gini 0.180
class counts [100, 0]: gini 0.000
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw three boxes each holding 100 dots coloured by class: [50 vs 50], [90 vs 10], [100 vs 0]. Under each box show its Gini impurity (1 minus the sum of squared class shares): 0.500, 0.180, 0.000. Then draw one parent node of 100 mixed dots splitting into two child nodes with a threshold question, showing that gain equals parent impurity minus the size-weighted child impurities."

### 6.3 Implementation, faithful to scikit-learn's details

Four details decide whether a from-scratch tree reproduces scikit-learn's tree exactly. All four come from reading scikit-learn's source:

1. Inputs are converted to **float32** before anything else.
2. A threshold is the **midpoint** of two neighbouring sorted values: `v[i]/2 + v[i+1]/2`. A row goes left if `x ≤ threshold`.
3. Two values count as different only if they differ by more than `1e-7`.
4. Among equally good splits, scikit-learn keeps the first one it found, visiting features in a **random order** (seeded by `random_state`). We visit features in index order, so trees can differ only when two splits tie exactly.

The search for the best threshold of one feature is vectorised with cumulative sums: sort the node's rows by the feature once, and the class counts (or sums of `y`) on the left of every possible cut are a running total.

```python run
class TreeScratch:
    """CART tree. criterion 'gini' (classification) or 'mse' (regression)."""
    def __init__(self, criterion="gini", max_depth=None, min_samples_leaf=1, max_features=None, seed=None):
        self.criterion, self.max_depth, self.min_samples_leaf = criterion, max_depth, min_samples_leaf
        self.max_features, self.seed = max_features, seed

    def fit(self, X, y):
        self.X_ = np.asarray(X, dtype=np.float32)
        self.rng_ = np.random.default_rng(self.seed)
        if self.criterion == "gini":
            self.classes_, y_enc = np.unique(y, return_inverse=True)
            self.Y_ = np.eye(len(self.classes_))[y_enc]                     # one-hot for counting
        else:
            self.Y_ = np.asarray(y, float)[:, None]
        self.nodes_ = []                                                    # list of dicts
        self._grow(np.arange(len(self.X_)), depth=0)
        return self

    def _impurity_from_sums(self, s, s2, n):
        if self.criterion == "gini":
            return 1 - np.sum((s / n[..., None]) ** 2, axis=-1)
        return s2 / n - (s[..., 0] / n) ** 2                                 # variance = E[y²] - E[y]²

    def _best_split(self, idx):
        X, Y = self.X_[idx], self.Y_[idx]
        n = len(idx)
        Ysq = (Y[:, 0] ** 2) if self.criterion == "mse" else None
        tot, tot2 = Y.sum(0), (Ysq.sum() if Ysq is not None else 0.0)
        parent = self._impurity_from_sums(tot, tot2, np.array(float(n)))
        features = np.arange(X.shape[1])
        if self.max_features is not None:                                    # random forests: a random subset per node
            features = self.rng_.choice(features, self.max_features, replace=False)
        best = (None, None, -np.inf)
        m = self.min_samples_leaf
        for f in features:
            order = np.argsort(X[:, f], kind="stable")
            xs = X[order, f]
            cs = np.cumsum(Y[order], axis=0)[:-1]                            # sums on the left of each cut
            cs2 = np.cumsum(Ysq[order])[:-1] if Ysq is not None else np.zeros(n - 1)
            nl = np.arange(1, n, dtype=float)
            nr = n - nl
            valid = (xs[1:] > xs[:-1] + 1e-7) & (nl >= m) & (nr >= m)
            if not valid.any():
                continue
            imp_l = self._impurity_from_sums(cs, cs2, nl)
            imp_r = self._impurity_from_sums(tot - cs, tot2 - cs2, nr)
            gain = parent - (nl * imp_l + nr * imp_r) / n
            gain[~valid] = -np.inf
            i = int(np.argmax(gain))
            if gain[i] > best[2] + 1e-12:
                thr = float(xs[i]) / 2.0 + float(xs[i + 1]) / 2.0
                best = (int(f), thr, float(gain[i]))
        return best

    def _grow(self, idx, depth):
        node_id = len(self.nodes_)
        Y = self.Y_[idx]
        value = Y.mean(0)                                                    # class shares, or the mean of y
        node = {"value": value, "n": len(idx), "feature": None, "threshold": None, "left": None, "right": None}
        self.nodes_.append(node)
        pure = np.allclose(Y, Y[0])
        if pure or (self.max_depth is not None and depth >= self.max_depth) or len(idx) < 2 * self.min_samples_leaf:
            return node_id
        f, thr, gain = self._best_split(idx)
        if f is None:
            return node_id
        go_left = self.X_[idx, f] <= thr
        node.update(feature=f, threshold=thr)
        node["left"] = self._grow(idx[go_left], depth + 1)
        node["right"] = self._grow(idx[~go_left], depth + 1)
        return node_id

    def apply(self, X):
        X = np.asarray(X, dtype=np.float32)
        out = np.empty(len(X), dtype=int)
        for r in range(len(X)):
            i = 0
            while self.nodes_[i]["feature"] is not None:
                i = self.nodes_[i]["left"] if X[r, self.nodes_[i]["feature"]] <= self.nodes_[i]["threshold"] else self.nodes_[i]["right"]
            out[r] = i
        return out

    def predict_value(self, X):
        return np.array([self.nodes_[i]["value"] for i in self.apply(X)])

    def predict(self, X):
        v = self.predict_value(X)
        return self.classes_[np.argmax(v, axis=1)] if self.criterion == "gini" else v[:, 0]

def preorder(nodes, i=0):
    """(feature, threshold) of every split node, in pre-order: a fingerprint of the tree's structure."""
    nd = nodes[i]
    if nd["feature"] is None:
        return []
    return [(nd["feature"], round(nd["threshold"], 6))] + preorder(nodes, nd["left"]) + preorder(nodes, nd["right"])

def sk_preorder(t, i=0):
    if t.children_left[i] == -1:
        return []
    return [(int(t.feature[i]), round(float(t.threshold[i]), 6))] + sk_preorder(t, t.children_left[i]) + sk_preorder(t, t.children_right[i])
```

### 6.4 Matching scikit-learn

First on data where exact ties are very unlikely: five continuous features, a shallow tree.

```python run
rng = np.random.default_rng(5)
X_t = rng.normal(size=(600, 5))
y_t = ((X_t[:, 0] + X_t[:, 1] ** 2 - X_t[:, 2] * X_t[:, 3] + rng.normal(0, 0.5, 600)) > 0.8).astype(int)
Xt_tr, Xt_te, yt_tr, yt_te = X_t[:400], X_t[400:], y_t[:400], y_t[400:]
ours3 = TreeScratch("gini", max_depth=3).fit(Xt_tr, yt_tr)
sk3 = tree.DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xt_tr, yt_tr)
print("identical structure (every feature and threshold):", preorder(ours3.nodes_) == sk_preorder(sk3.tree_))
compare("depth-3 tree, predict_proba on new rows", ours3.predict_value(Xt_te), sk3.predict_proba(Xt_te), tol=1e-12)
print("first three splits (feature, threshold):", preorder(ours3.nodes_)[:3])
```
```text
identical structure (every feature and threshold): True
depth-3 tree, predict_proba on new rows    max |ours - sklearn| = 0.00e+00  -> MATCH
first three splits (feature, threshold): [(0, 0.247993), (1, -0.863531), (1, -1.486939)]
```

Every question and every threshold is the same, and so is every probability. Now grow deeper, and switch to the cancer data:

```python run
for name, (Xa, ya) in {"synthetic": (Xt_tr, yt_tr), "cancer": (Xc_tr, yc_tr)}.items():
    for depth, leaf in [(2, 1), (3, 1), (5, 5), (None, 1)]:
        o = TreeScratch("gini", max_depth=depth, min_samples_leaf=leaf).fit(Xa, ya)
        s = tree.DecisionTreeClassifier(max_depth=depth, min_samples_leaf=leaf, random_state=0).fit(Xa, ya)
        print(f"{name:9s} max_depth={str(depth):4s} min_samples_leaf={leaf}: identical structure {str(preorder(o.nodes_) == sk_preorder(s.tree_)):5s} | same training predictions {bool(np.all(o.predict(Xa) == s.predict(Xa)))}")
```
```text
synthetic max_depth=2    min_samples_leaf=1: identical structure True  | same training predictions True
synthetic max_depth=3    min_samples_leaf=1: identical structure True  | same training predictions True
synthetic max_depth=5    min_samples_leaf=5: identical structure False | same training predictions False
synthetic max_depth=None min_samples_leaf=1: identical structure False | same training predictions True
cancer    max_depth=2    min_samples_leaf=1: identical structure False | same training predictions True
cancer    max_depth=3    min_samples_leaf=1: identical structure False | same training predictions True
cancer    max_depth=5    min_samples_leaf=5: identical structure False | same training predictions True
cancer    max_depth=None min_samples_leaf=1: identical structure False | same training predictions True
```

### 6.5 When the structures differ: ties

Is our tree wrong when the structures differ? The test is to walk both trees side by side to the **first** node where they ask different questions, and compute the gain of *both* questions on the rows of that node. (Up to that node the trees are identical, so the node holds the same rows in both.)

```python run
def split_gain(y, mask, criterion="gini"):
    def imp(v):
        if criterion == "gini":
            p = np.bincount(v, minlength=2) / len(v)
            return 1 - np.sum(p ** 2)
        return np.var(v)
    n = len(y)
    return imp(y) - (mask.sum() * imp(y[mask]) + (~mask).sum() * imp(y[~mask])) / n

def first_difference(ours, sk_tree, X, y, i=0, j=0, idx=None):
    X32 = np.asarray(X, dtype=np.float32)
    idx = np.arange(len(X)) if idx is None else idx
    a, t = ours.nodes_[i], sk_tree
    if a["feature"] is None or t.children_left[j] == -1:
        return None
    fo, to = a["feature"], a["threshold"]
    fs, ts = int(t.feature[j]), float(t.threshold[j])
    if (fo, round(to, 6)) != (fs, round(ts, 6)):
        mo, ms = X32[idx, fo] <= to, X32[idx, fs] <= ts
        return {"node rows": len(idx), "ours": (fo, round(to, 4)), "sklearn": (fs, round(ts, 4)),
                "gain ours": split_gain(y[idx], mo), "gain sklearn": split_gain(y[idx], ms),
                "left sizes": (int(mo.sum()), int(ms.sum())), "same partition": bool(np.all(mo == ms) or np.all(mo == ~ms))}
    go = X32[idx, fo] <= to
    return (first_difference(ours, t, X, y, a["left"], t.children_left[j], idx[go])
            or first_difference(ours, t, X, y, a["right"], t.children_right[j], idx[~go]))

for name, (Xa, ya) in {"cancer, depth 2": (Xc_tr, yc_tr), "synthetic, full depth": (Xt_tr, yt_tr)}.items():
    depth = 2 if "depth 2" in name else None
    o = TreeScratch("gini", max_depth=depth).fit(Xa, ya)
    s = tree.DecisionTreeClassifier(max_depth=depth, random_state=0).fit(Xa, ya)
    d = first_difference(o, s.tree_, Xa, ya)
    print(f"{name}: first difference at a node of {d['node rows']} rows; ours asks {d['ours']}, sklearn asks {d['sklearn']}")
    print(f"    gain ours {d['gain ours']:.12f} | gain sklearn {d['gain sklearn']:.12f} | same partition of the rows: {d['same partition']}")
print("cancer feature 22 is", cancer.feature_names[22], "; feature 27 is", cancer.feature_names[27])
```
```text
cancer, depth 2: first difference at a node of 157 rows; ours asks (22, 115.35), sklearn asks (27, 0.1416)
    gain ours 0.067304182573 | gain sklearn 0.067304182573 | same partition of the rows: False
synthetic, full depth: first difference at a node of 14 rows; ours asks (2, -0.2631), sklearn asks (3, 0.7945)
    gain ours 0.040816326531 | gain sklearn 0.040816326531 | same partition of the rows: False
cancer feature 22 is worst perimeter ; feature 27 is worst concave points
```

The gains are identical to the last printed digit: two different questions are **equally good**, and the two programs simply picked different ones. Notice "same partition: False": the two questions send *different* rows left, but both produce children with exactly the same class counts (for example 35 rows with the same mix of labels on the left), and Gini looks only at counts. This happens all the time, because Gini values come from small integer counts: in a node of 14 rows there are only a few possible values, and many different cuts hit the same one. Correlated features (radius, perimeter and area of the same cell in the cancer data) make it even more likely.

scikit-learn itself does not give one answer. It visits features in a random order, so its own trees change with `random_state`:

```python run
fps = {rs: sk_preorder(tree.DecisionTreeClassifier(random_state=rs).fit(Xc_tr, yc_tr).tree_) for rs in range(5)}
print("scikit-learn fully grown trees with random_state 0..4: number of distinct structures =", len({tuple(v) for v in fps.values()}))
```
```text
scikit-learn fully grown trees with random_state 0..4: number of distinct structures = 5
```

So for trees, "matching scikit-learn" means: identical where the best split is unique, and a **proven tie** at the first place they part. That is the "structural" row of the table in section 1.2. After a tie the two trees continue on different rows, so they can grow differently below it; both are equally valid answers to the greedy rule, and on new data they disagree for a small share of rows.

### 6.6 Overfitting, depth and pruning

A tree with no limit grows until every leaf is pure: perfect on training data, poor on new data (ds.03). Limits (`max_depth`, `min_samples_leaf`) stop it early. **Cost-complexity pruning** grows the full tree and then removes branches whose gain does not pay for their size, controlled by `ccp_alpha`.

```python run
rows = []
for depth in [1, 2, 3, 4, 6, 8, None]:
    m = TreeScratch("gini", max_depth=depth).fit(Xc_tr, yc_tr)
    rows.append((str(depth), np.mean(m.predict(Xc_tr) == yc_tr), np.mean(m.predict(Xc_te) == yc_te), sum(nd["feature"] is None for nd in m.nodes_)))
print(pd.DataFrame(rows, columns=["max_depth", "train accuracy", "test accuracy", "leaves"]).to_string(index=False))
```
```text
max_depth  train accuracy  test accuracy  leaves
        1         0.93216        0.88889       2
        2         0.94221        0.90643       4
        3         0.97990        0.90643       8
        4         0.98995        0.91228      12
        6         1.00000        0.91813      16
        8         1.00000        0.91813      16
     None         1.00000        0.91813      16
```

### 6.7 A regression tree is the same code

Only the impurity changes (variance instead of Gini), and the leaf predicts the mean.

```python run
rng = np.random.default_rng(4)
X_reg = rng.uniform(-3, 3, (400, 2))
y_reg = np.sin(X_reg[:, 0]) * 2 + 0.5 * X_reg[:, 1] ** 2 + rng.normal(0, 0.3, 400)
r_ours = TreeScratch("mse", max_depth=4).fit(X_reg, y_reg)
r_sk = tree.DecisionTreeRegressor(max_depth=4, random_state=0).fit(X_reg, y_reg)
print("identical structure:", preorder(r_ours.nodes_) == sk_preorder(r_sk.tree_))
compare("regression tree depth 4, predictions", r_ours.predict(X_reg), r_sk.predict(X_reg), tol=1e-9)
```
```text
identical structure: True
regression tree depth 4, predictions       max |ours - sklearn| = 8.88e-16  -> MATCH
```

### 6.8 Try it

1. Change the criterion to entropy (`−Σ p log₂ p`) and match `DecisionTreeClassifier(criterion="entropy", max_depth=3)`.
2. Remove the float32 conversion in `fit` and `apply`. Does the depth-4 tree still match? (It often does; when it does not, the reason is a threshold that sits between two values that are equal in float32 and different in float64.)

## 7. Random forests

### 7.1 The idea: many noisy trees, averaged

A single deep tree has low bias and very high variance: change a few training rows and the tree changes a lot. Averaging many such trees cancels much of the variance, **if the trees make different mistakes**. A random forest makes them different in two ways:

1. **Bagging**: each tree is trained on a bootstrap sample (rows drawn with replacement).
2. **Feature subsampling**: at each split, only a random subset of features is considered (`max_features`, usually `√d` for classification).

Each tree is grown deep. The forest's prediction is the average of the trees' class shares.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a random forest as a data-flow diagram. One training set feeds three bootstrap samples (rows drawn with replacement, so some rows repeat and some are left out). Each sample trains a deep tree that, at every split, looks at only a random subset of features (about the square root of the number of features). Show each tree outputting class shares and a final box averaging them into the forest prediction."

### 7.2 Implementation with our tree

```python run
class ForestScratch:
    def __init__(self, n_trees=100, max_features="sqrt", min_samples_leaf=1, seed=0):
        self.n_trees, self.max_features, self.min_samples_leaf, self.seed = n_trees, max_features, min_samples_leaf, seed
    def fit(self, X, y):
        X, y = np.asarray(X), np.asarray(y)
        r = np.random.default_rng(self.seed)
        n, d = X.shape
        mf = int(np.sqrt(d)) if self.max_features == "sqrt" else self.max_features
        self.classes_ = np.unique(y)
        self.trees_, self.oob_masks_ = [], []
        for t in range(self.n_trees):
            boot = r.integers(0, n, n)                                       # a bootstrap sample
            oob = np.ones(n, bool); oob[boot] = False                        # rows this tree never saw
            tr = TreeScratch("gini", max_features=mf, min_samples_leaf=self.min_samples_leaf, seed=int(r.integers(1 << 31))).fit(X[boot], y[boot])
            self.trees_.append(tr); self.oob_masks_.append(oob)
        return self
    def _tree_proba(self, tr, X):
        v = tr.predict_value(X)                                              # shares over the classes present in that bootstrap
        full = np.zeros((len(X), len(self.classes_)))
        full[:, np.searchsorted(self.classes_, tr.classes_)] = v
        return full
    def predict_proba(self, X):
        return np.mean([self._tree_proba(tr, X) for tr in self.trees_], axis=0)
    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]
    def oob_score(self, X, y):
        acc = np.zeros((len(X), len(self.classes_))); cnt = np.zeros(len(X))
        for tr, oob in zip(self.trees_, self.oob_masks_):
            acc[oob] += self._tree_proba(tr, X[oob]); cnt[oob] += 1
        seen = cnt > 0
        return float(np.mean(self.classes_[np.argmax(acc[seen], 1)] == np.asarray(y)[seen]))

t0 = time.perf_counter()
rf_ours = ForestScratch(n_trees=60, seed=0).fit(Xc_tr, yc_tr)
t_ours = time.perf_counter() - t0
print(f"our forest: 60 trees in {t_ours:.1f} s | test accuracy {np.mean(rf_ours.predict(Xc_te) == yc_te):.4f} | out-of-bag accuracy {rf_ours.oob_score(Xc_tr, yc_tr):.4f}")
```
```text
our forest: 60 trees in 0.2 s | test accuracy 0.9415 | out-of-bag accuracy 0.9598
```

### 7.3 Matching statistically

Our random draws are not scikit-learn's, so the trees differ and only the **distribution** of results can match. Train both over several seeds and compare.

```python run
ours_acc, sk_acc = [], []
for seed in range(5):
    ours_acc.append(np.mean(ForestScratch(n_trees=40, seed=seed).fit(Xc_tr, yc_tr).predict(Xc_te) == yc_te))
    sk_acc.append(ensemble.RandomForestClassifier(n_estimators=40, random_state=seed, n_jobs=1).fit(Xc_tr, yc_tr).score(Xc_te, yc_te))
print("test accuracy over 5 seeds")
print(f"  ours   : mean {np.mean(ours_acc):.4f}, min {np.min(ours_acc):.4f}, max {np.max(ours_acc):.4f}")
print(f"  sklearn: mean {np.mean(sk_acc):.4f}, min {np.min(sk_acc):.4f}, max {np.max(sk_acc):.4f}")
t0 = time.perf_counter(); ensemble.RandomForestClassifier(n_estimators=60, random_state=0, n_jobs=1).fit(Xc_tr, yc_tr); t_sk = time.perf_counter() - t0
print(f"time for 60 trees: ours {t_ours:.2f} s, sklearn {t_sk:.2f} s (machine-specific)")
```
```text
test accuracy over 5 seeds
  ours   : mean 0.9392, min 0.9298, max 0.9532
  sklearn: mean 0.9462, min 0.9415, max 0.9532
time for 60 trees: ours 0.23 s, sklearn 0.06 s (machine-specific)
```

### 7.4 Why averaging helps: a measurement

```python run
single = [np.mean(tr.predict(Xc_te) == yc_te) for tr in rf_ours.trees_]
p_running = np.cumsum([rf_ours._tree_proba(tr, Xc_te) for tr in rf_ours.trees_], axis=0)
forest_acc = [np.mean(rf_ours.classes_[np.argmax(p, 1)] == yc_te) for p in p_running]
print(f"single trees: mean test accuracy {np.mean(single):.4f} (range {np.min(single):.4f} to {np.max(single):.4f})")
print("forest accuracy after 1, 5, 10, 30, 60 trees:", [round(float(forest_acc[i - 1]), 4) for i in [1, 5, 10, 30, 60]])
```
```text
single trees: mean test accuracy 0.9108 (range 0.8596 to 0.9474)
forest accuracy after 1, 5, 10, 30, 60 trees: [0.9357, 0.924, 0.9357, 0.9181, 0.9415]
```

The individual trees average about 0.91 and range widely; the forest of 60 is better than almost every single tree. Along the way the forest's accuracy wobbles by a percent or so, because the test set has only 171 rows (one row = 0.6%), so look at the trend, not each step. More trees never hurt accuracy in expectation (they only cost time); the improvement flattens.

### 7.5 Try it

1. Set `max_features=None` (every split sees all features: plain bagging). Does the forest get better or worse? Why would trees that see all features be more alike?
2. Compare the out-of-bag accuracy with 5-fold cross-validation accuracy of the same forest. Why is the OOB estimate essentially free?

## 8. Gradient boosting

### 8.1 The idea: fix the previous mistakes

A forest builds independent deep trees in parallel and averages them. **Boosting** builds shallow trees **one after another**, each trained to correct what the ensemble so far gets wrong. For squared error the recipe is very concrete:

1. Start with a constant prediction `F₀ = mean(y)`.
2. Compute the residuals `r = y − F`.
3. Fit a small regression tree to `r`.
4. Add a **shrunken** copy of it: `F ← F + η · tree(x)`, with learning rate `η` (for example 0.1).
5. Repeat.

Why "gradient"? The residual `y − F` is the negative gradient of the squared loss `½(y − F)²` with respect to `F`. For any other loss you fit the tree to the negative gradient of that loss instead. Boosting is gradient descent in the space of functions, where each step is a tree.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate gradient boosting for squared error on a 1D regression dataset, step by step. Start with a flat line F0 = mean(y). At each round, show the residuals y minus F as vertical bars, fit a small tree (a step function) to them, then add it times a learning rate of 0.1 to get the new curve F. Show rounds 1, 2, 3 and 20, with the curve slowly fitting the data."

### 8.2 Implementation, and an exact match

scikit-learn's `GradientBoostingRegressor` with squared error does exactly the five steps above with depth-3 trees. Using our own regression tree as the base learner:

```python run
class BoostScratch:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3, min_samples_leaf=1):
        self.n_estimators, self.learning_rate, self.max_depth, self.min_samples_leaf = n_estimators, learning_rate, max_depth, min_samples_leaf
    def fit(self, X, y):
        y = np.asarray(y, float)
        self.init_ = y.mean()
        F = np.full(len(y), self.init_)
        self.trees_ = []
        for m in range(self.n_estimators):
            resid = y - F                                                    # negative gradient of ½(y - F)²
            t = TreeScratch("mse", max_depth=self.max_depth, min_samples_leaf=self.min_samples_leaf).fit(X, resid)
            F += self.learning_rate * t.predict(X)
            self.trees_.append(t)
        return self
    def predict(self, X):
        return self.init_ + self.learning_rate * np.sum([t.predict(X) for t in self.trees_], axis=0)

Xb_tr, Xb_te, yb_tr, yb_te = model_selection.train_test_split(X_reg, y_reg, test_size=0.3, random_state=0)
for leaf in [1, 5]:
    t0 = time.perf_counter()
    gb_ours = BoostScratch(n_estimators=100, min_samples_leaf=leaf).fit(Xb_tr, yb_tr)
    el = time.perf_counter() - t0
    gb_sk = ensemble.GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, min_samples_leaf=leaf, random_state=0).fit(Xb_tr, yb_tr)
    print(f"min_samples_leaf={leaf} (ours: 100 trees in {el:.1f} s)")
    compare("   boosting, TRAINING predictions", gb_ours.predict(Xb_tr), gb_sk.predict(Xb_tr), tol=1e-9)
    compare("   boosting, TEST predictions", gb_ours.predict(Xb_te), gb_sk.predict(Xb_te), tol=1e-9)
print(f"test MSE: ours {np.mean((gb_ours.predict(Xb_te) - yb_te) ** 2):.5f} | sklearn {np.mean((gb_sk.predict(Xb_te) - yb_te) ** 2):.5f} | noise variance 0.09")
```
```text
min_samples_leaf=1 (ours: 100 trees in 0.1 s)
   boosting, TRAINING predictions          max |ours - sklearn| = 7.99e-15  -> MATCH
   boosting, TEST predictions              max |ours - sklearn| = 1.63e-01  -> DIFFERENT
min_samples_leaf=5 (ours: 100 trees in 0.1 s)
   boosting, TRAINING predictions          max |ours - sklearn| = 7.11e-15  -> MATCH
   boosting, TEST predictions              max |ours - sklearn| = 6.22e-15  -> MATCH
test MSE: ours 0.16378 | sklearn 0.16378 | noise variance 0.09
```

With `min_samples_leaf=1` the training predictions agree to the last digit, but some test predictions do not. The cause is the tie of section 6.5 in a new form: in one of the hundred trees, a node of 22 rows can split off its single most extreme point using either of the two features. Both choices separate the same rows (so the training fit is identical and every later residual stays identical), but a new point near that corner can fall on different sides. With `min_samples_leaf=5` a split may not isolate a single point, those ties disappear, and even the test predictions match exactly.

(scikit-learn's default split criterion for boosting is `friedman_mse`. For a split into groups of sizes `n_L`, `n_R` with means `μ_L`, `μ_R` it scores `n_L·n_R/(n_L+n_R)·(μ_L − μ_R)²`, which is algebraically the same as the reduction in squared error. Same splits, so the match is exact.)

### 8.3 Learning rate and number of trees

The learning rate and the number of trees trade against each other: a smaller rate needs more trees but usually generalises better. Too many trees overfit, so watch the validation error as trees are added. scikit-learn exposes the prediction after every stage with `staged_predict`.

```python run
rows = []
for lr in [1.0, 0.3, 0.1, 0.03]:
    g = ensemble.GradientBoostingRegressor(n_estimators=400, learning_rate=lr, max_depth=3, random_state=0).fit(Xb_tr, yb_tr)
    val = [np.mean((p - yb_te) ** 2) for p in g.staged_predict(Xb_te)]
    best = int(np.argmin(val))
    rows.append((lr, best + 1, val[best], val[-1]))
print(pd.DataFrame(rows, columns=["learning rate", "best number of trees", "best test MSE", "MSE after 400 trees"]).to_string(index=False))
```
```text
 learning rate  best number of trees  best test MSE  MSE after 400 trees
       1.00000                    13        0.30517              0.40369
       0.30000                    42        0.18483              0.20458
       0.10000                   131        0.15945              0.17042
       0.03000                   400        0.16778              0.16778
```

In practice you set a small learning rate and let **early stopping** (a held-out slice of the training data) pick the number of trees: `n_iter_no_change` in scikit-learn, `early_stopping_rounds` in XGBoost and LightGBM.

### 8.4 Boosting for classification

For binary classification the model predicts the **log-odds** `F`, and `p = σ(F)`. The negative gradient of the log loss with respect to `F` is again `y − p`. Each tree is fitted to `y − p`; then its leaf values are replaced by a **Newton step**, `Σ(y − p) / Σ p(1 − p)` over the rows in the leaf, which uses the curvature exactly as in section 3.3.

```python run
def boost_classifier(X, y, n_estimators=50, lr=0.1, max_depth=3, min_samples_leaf=1):
    p0 = y.mean()
    F = np.full(len(y), np.log(p0 / (1 - p0)))
    init = F[0]
    stages = []
    for m in range(n_estimators):
        p = sigmoid(F)
        g = y - p
        t = TreeScratch("mse", max_depth=max_depth, min_samples_leaf=min_samples_leaf).fit(X, g)
        leaves = t.apply(X)
        leaf_value = {}
        for leaf in np.unique(leaves):
            rows_ = leaves == leaf
            leaf_value[leaf] = g[rows_].sum() / max((p[rows_] * (1 - p[rows_])).sum(), 1e-300)
        F += lr * np.array([leaf_value[l] for l in leaves])
        stages.append((t, leaf_value))
    def decision(Xn):
        out = np.full(len(Xn), init)
        for t, lv in stages:
            out += lr * np.array([lv[l] for l in t.apply(Xn)])
        return out
    return decision, F

dec, dec_train = boost_classifier(Xt_tr, yt_tr.astype(float), n_estimators=50, min_samples_leaf=5)
gbc = ensemble.GradientBoostingClassifier(n_estimators=50, learning_rate=0.1, max_depth=3, min_samples_leaf=5, random_state=0).fit(Xt_tr, yt_tr)
compare("boosted classifier, decision function (training)", dec_train, gbc.decision_function(Xt_tr), tol=1e-6)
compare("boosted classifier, decision function (test)", dec(Xt_te), gbc.decision_function(Xt_te), tol=1e-6)
print("test accuracy:", round(np.mean((dec(Xt_te) > 0) == yt_te), 4))
```
```text
boosted classifier, decision function (training) max |ours - sklearn| = 1.78e-15  -> MATCH
boosted classifier, decision function (test) max |ours - sklearn| = 1.33e-15  -> MATCH
test accuracy: 0.845
```

If you rerun this with `min_samples_leaf=1`, the test decision function can differ for the reason explained under the regression version: tied splits that isolate the same few rows.

### 8.5 Histogram boosting, XGBoost and LightGBM

Exact split search sorts every feature at every node. On a million rows that is slow. **Histogram** methods first bucket each feature into at most 256 bins (once), then find splits by scanning bin totals, which is far cheaper. This is the core idea of **LightGBM**, and scikit-learn's `HistGradientBoostingClassifier/Regressor` implements the same approach (native missing-value support, early stopping, categorical features). **XGBoost** adds a second-order (Newton) objective with explicit L1/L2 penalties on leaf values, and also has a histogram mode.

```python run
X_big, y_big = datasets.make_friedman1(n_samples=20000, n_features=10, noise=1.0, random_state=0)
Xg_tr, Xg_te, yg_tr, yg_te = model_selection.train_test_split(X_big, y_big, test_size=0.25, random_state=0)
for name, est in [("GradientBoostingRegressor (exact splits)", ensemble.GradientBoostingRegressor(n_estimators=200, max_depth=3, random_state=0)),
                  ("HistGradientBoostingRegressor (256 bins)", ensemble.HistGradientBoostingRegressor(max_iter=200, max_depth=3, early_stopping=False, random_state=0))]:
    t0 = time.perf_counter(); est.fit(Xg_tr, yg_tr); el = time.perf_counter() - t0
    print(f"{name:42s} fit {el:5.2f} s | test MSE {np.mean((est.predict(Xg_te) - yg_te) ** 2):.4f}")
```
```text
GradientBoostingRegressor (exact splits)   fit  6.69 s | test MSE 1.2252
HistGradientBoostingRegressor (256 bins)   fit  0.10 s | test MSE 1.2166
```

The libraries follow the scikit-learn API, so they drop into the pipelines of ds.05:

```python
# Try it on your machine:  pip install xgboost lightgbm   (not installed here, so no output is shown)
import xgboost as xgb, lightgbm as lgb
xgb_model = xgb.XGBRegressor(n_estimators=2000, learning_rate=0.05, max_depth=4, subsample=0.8,
                             colsample_bytree=0.8, reg_lambda=1.0, early_stopping_rounds=50, eval_metric="rmse")
xgb_model.fit(Xg_tr, yg_tr, eval_set=[(Xg_te, yg_te)], verbose=False)      # use a validation split, not the test set, in real work
lgb_model = lgb.LGBMRegressor(n_estimators=2000, learning_rate=0.05, num_leaves=31, subsample=0.8, subsample_freq=1,
                              colsample_bytree=0.8, verbose=-1)
lgb_model.fit(Xg_tr, yg_tr, eval_set=[(Xg_te, yg_te)], callbacks=[lgb.early_stopping(50, verbose=False)])
print(xgb_model.best_iteration, lgb_model.best_iteration_)
```

| Parameter idea | scikit-learn `HistGradientBoosting` | XGBoost | LightGBM |
|---|---|---|---|
| number of trees | `max_iter` | `n_estimators` | `n_estimators` |
| step size | `learning_rate` | `learning_rate` (`eta`) | `learning_rate` |
| tree size | `max_leaf_nodes`, `max_depth` | `max_depth` | `num_leaves` |
| minimum leaf size | `min_samples_leaf` | `min_child_weight` (a Hessian sum) | `min_child_samples` |
| L2 on leaf values | `l2_regularization` | `reg_lambda` | `reg_lambda` |
| row / column sampling | (none / `max_features`) | `subsample`, `colsample_bytree` | `subsample`, `colsample_bytree` |
| early stopping | `early_stopping`, `n_iter_no_change` | `early_stopping_rounds` | `early_stopping` callback |

### 8.6 Try it

1. Add `subsample=0.5` to `BoostScratch` (each tree sees a random half of the rows; this is *stochastic* gradient boosting). Compare with `GradientBoostingRegressor(subsample=0.5)` statistically, over 5 seeds.
2. Replace the squared loss in `BoostScratch` by absolute loss: the negative gradient is `sign(y − F)`, and the best leaf value is the **median** residual in the leaf. Match `GradientBoostingRegressor(loss="absolute_error")`.


## 9. Support vector machines

### 9.1 The idea: the widest street

For two classes that a straight line can separate, there are infinitely many separating lines. A support vector machine picks the one with the **widest margin**: the widest "street" between the classes with no points on it. Only the points on the edges of the street (the **support vectors**) decide where it lies; every other point could move (without crossing the street) and the answer would not change.

Real data overlap, so the **soft-margin** SVM allows violations and pays for them with the **hinge loss**. With labels `y ∈ {−1, +1}` and score `f(x) = w·x + b`:

```text
objective(w, b) = ½ ‖w‖²  +  C · Σ max(0, 1 − y_i f(x_i))
```

The first term widens the street (the margin width is `2/‖w‖`). The hinge term is zero for points on the correct side beyond the margin, and grows linearly for points inside the street or on the wrong side. `C` sets the price of a violation: large `C` = few violations, narrow street, risk of overfitting; small `C` = wide street, more violations.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 2D scatter of two classes (red and blue) with a straight line separating them, the two margin lines parallel to it, and the 'street' between them shaded. Circle the support vectors on the street edges. Label the margin width as 2 divided by the length of w. Add a second smaller panel with overlapping classes showing a narrow street (large C) versus a wide street (small C), marking points that violate the margin."

### 9.2 From scratch: sub-gradient descent

The hinge has a corner at 1, so it has no gradient there; we use a **sub-gradient** (any slope between the two sides; we take the left one). For points with `y f(x) < 1` the hinge contributes `−C y x` to the slope of `w` and `−C y` to the slope of `b`. Because of the corner, plain steps never settle exactly; we shrink the step size over time and **average** the later iterates, a standard trick that converges to the optimum.

```python run
def linear_svm_subgradient(X, y, C=1.0, iters=20000):
    y = np.where(y > 0, 1.0, -1.0)
    w, b = np.zeros(X.shape[1]), 0.0
    w_avg, b_avg, count = np.zeros_like(w), 0.0, 0
    for t in range(1, iters + 1):
        margin = y * (X @ w + b)
        viol = margin < 1
        gw = w - C * (y[viol, None] * X[viol]).sum(0)
        gb = -C * y[viol].sum()
        step = 1.0 / (t + 100)
        w, b = w - step * gw, b - step * gb * 0.5
        if t > iters // 2:                                         # average the second half
            count += 1
            w_avg += (w - w_avg) / count
            b_avg += (b - b_avg) / count
    return w_avg, b_avg

def svm_objective(w, b, X, y, C):
    y = np.where(y > 0, 1.0, -1.0)
    return 0.5 * w @ w + C * np.maximum(0, 1 - y * (X @ w + b)).sum()

Xs_svm, ys_svm = datasets.make_blobs(n_samples=200, centers=[[-1.5, -1], [1.5, 1]], cluster_std=1.2, random_state=0)
C = 0.5
w_s, b_s = linear_svm_subgradient(Xs_svm, ys_svm, C=C)
svc = svm.SVC(kernel="linear", C=C, tol=1e-8).fit(Xs_svm, ys_svm)
w_k, b_k = svc.coef_[0], svc.intercept_[0]
print("ours    w, b:", w_s.round(4), round(b_s, 4), "| objective", round(svm_objective(w_s, b_s, Xs_svm, ys_svm, C), 5))
print("sklearn w, b:", w_k.round(4), round(b_k, 4), "| objective", round(svm_objective(w_k, b_k, Xs_svm, ys_svm, C), 5))
cos = w_s @ w_k / np.linalg.norm(w_s) / np.linalg.norm(w_k)
agree = np.mean(np.sign(Xs_svm @ w_s + b_s) == np.sign(Xs_svm @ w_k + b_k))
print(f"cosine between the weight vectors {cos:.6f} | training predictions agree {agree:.3f}")
```
```text
ours    w, b: [1.2195 0.7934] 0.1499 | objective 20.77634
sklearn w, b: [1.2195 0.7933] 0.1499 | objective 20.77633
cosine between the weight vectors 1.000000 | training predictions agree 1.000
```

This is the "approximate" row of the table in 1.2: a slow, non-smooth solver lands close to the optimum, with nearly the same objective value and the same predictions, but not to ten decimals. scikit-learn's `SVC` solves the **dual** problem with the SMO algorithm (libsvm), which converges exactly.

### 9.3 Support vectors

```python run
yy = np.where(ys_svm > 0, 1.0, -1.0)
m_ours = yy * (Xs_svm @ w_s + b_s)
print("points on or inside the margin (ours, y·f(x) ≤ 1.001):", int(np.sum(m_ours <= 1.001)))
print("support vectors reported by SVC                       :", int(svc.n_support_.sum()))
print("margin width 2/‖w‖ (sklearn):", round(2 / np.linalg.norm(w_k), 4))
```
```text
points on or inside the margin (ours, y·f(x) ≤ 1.001): 45
support vectors reported by SVC                       : 45
margin width 2/‖w‖ (sklearn): 1.3747
```

### 9.4 Two different "linear SVMs" in scikit-learn

`SVC(kernel="linear")` solves exactly the objective above. `LinearSVC` is a faster solver (liblinear) for large data, but by default it solves a **different** problem: squared hinge loss, and the intercept is penalised like a weight. So the two give different weights, and neither is wrong.

> **Predict the output.** `LinearSVC(C=0.5)` and `SVC(kernel="linear", C=0.5)` are both "linear SVMs with C = 0.5". Will they print the same weights?

<details><summary>Answer</summary>

No. The default `LinearSVC` gives weights about half the size (0.58 and 0.40 against 1.22 and 0.79) and an intercept near zero, because it minimises the *squared* hinge and penalises the intercept. With `loss="hinge"` and a large `intercept_scaling` it reproduces `SVC` to four decimals.

</details>

```python run
lsvc = svm.LinearSVC(C=C, max_iter=100000, tol=1e-10).fit(Xs_svm, ys_svm)
lsvc_hinge = svm.LinearSVC(C=C, loss="hinge", intercept_scaling=100, max_iter=200000, tol=1e-10).fit(Xs_svm, ys_svm)
print("SVC(kernel='linear')                    :", w_k.round(4), round(b_k, 4))
print("LinearSVC() default (squared hinge)     :", lsvc.coef_[0].round(4), round(lsvc.intercept_[0], 4))
print("LinearSVC(loss='hinge', intercept_scaling=100):", lsvc_hinge.coef_[0].round(4), round(lsvc_hinge.intercept_[0], 4))
```
```text
SVC(kernel='linear')                    : [1.2195 0.7933] 0.1499
LinearSVC() default (squared hinge)     : [0.5847 0.3995] 0.0061
LinearSVC(loss='hinge', intercept_scaling=100): [1.2195 0.7933] 0.1499
```

With the plain hinge and a large `intercept_scaling` (which makes the intercept's penalty negligible), `LinearSVC` approaches `SVC`. Always check *which* objective a solver minimises before comparing numbers.

### 9.5 Kernels: curved boundaries without new features

The dual form of the SVM uses the data only through **dot products** `x_i·x_j`. Replace the dot product by a **kernel** `K(x_i, x_j)`, a similarity, and the SVM draws a straight boundary in a hidden, larger feature space, which looks curved in the original one. The most used kernel is the **RBF** (Gaussian) `K(a, b) = exp(−γ‖a − b‖²)`. `γ` sets how local the similarity is: large `γ` = very local = wiggly boundary.

```python run
Xm, ym = datasets.make_moons(n_samples=400, noise=0.25, random_state=0)
Xm_tr, Xm_te, ym_tr, ym_te = model_selection.train_test_split(Xm, ym, test_size=0.3, random_state=0)
rows = []
for kernel, params in [("linear", {}), ("rbf", {"gamma": 0.1}), ("rbf", {"gamma": 1.0}), ("rbf", {"gamma": 10.0}), ("rbf", {"gamma": 100.0})]:
    for Cv in [0.1, 1, 100]:
        m = pipeline.make_pipeline(preprocessing.StandardScaler(), svm.SVC(kernel=kernel, C=Cv, **params)).fit(Xm_tr, ym_tr)
        rows.append((kernel, params.get("gamma", "-"), Cv, m.score(Xm_tr, ym_tr), m.score(Xm_te, ym_te), int(m[-1].n_support_.sum())))
print(pd.DataFrame(rows, columns=["kernel", "gamma", "C", "train acc", "test acc", "support vectors"]).to_string(index=False))
```
```text
kernel     gamma         C  train acc  test acc  support vectors
linear         -   0.10000    0.85357   0.90000              117
linear         -   1.00000    0.86071   0.90833              101
linear         - 100.00000    0.85714   0.90833               98
   rbf   0.10000   0.10000    0.84643   0.90833              166
   rbf   0.10000   1.00000    0.86786   0.91667              112
   rbf   0.10000 100.00000    0.92143   0.93333               74
   rbf   1.00000   0.10000    0.90357   0.93333              157
   rbf   1.00000   1.00000    0.92143   0.94167               81
   rbf   1.00000 100.00000    0.93929   0.93333               56
   rbf  10.00000   0.10000    0.92857   0.94167              275
   rbf  10.00000   1.00000    0.92857   0.94167              170
   rbf  10.00000 100.00000    0.98214   0.89167              108
   rbf 100.00000   0.10000    0.50357   0.49167              280
   rbf 100.00000   1.00000    0.98214   0.90000              263
   rbf 100.00000 100.00000    1.00000   0.93333              256
```

Read the table along both axes: large `γ` with large `C` reaches near-perfect training accuracy with a worse test score (γ=10, C=100: 0.98 on training, 0.89 on test), which is overfitting; tiny `γ` behaves almost like a linear model. The strangest row, γ=100 with C=0.1, scores 0.50: every point is similar only to itself, and the cheap violations let the SVM give up and predict one class. The best test scores sit in the middle (γ around 1, moderate C). Tune `C` and `γ` together with a grid search on a log scale (ds.05 section 9), and always scale the features, because the kernel uses distances.

### 9.6 When to use an SVM today

SVMs shine on small to medium data with many features (text, genomics) and when a clean margin exists. Kernel SVMs scale badly (training time grows between `n²` and `n³`), and they give no probabilities by default (`probability=True` adds an internal cross-validated calibration, which is slow). For large tabular data, gradient boosting usually wins; for very large linear problems, `LinearSVC` or `SGDClassifier(loss="hinge")`.

### 9.7 Try it

1. Compute the kernel matrix `K = exp(−γ‖x_i − x_j‖²)` yourself with `pairwise_sq_dist`, pass it to `SVC(kernel="precomputed")`, and check that the predictions equal those of `SVC(kernel="rbf", gamma=γ)`.
2. Run `linear_svm_subgradient` with `iters=2000` and `iters=200000`. How does the objective gap to scikit-learn change?

## 10. Clustering: k-means, DBSCAN, hierarchical

Clustering is unsupervised (ds.03 section 13): no labels, only structure. There is no single "right" answer, so the algorithms differ in what they *assume* a cluster is. Matching scikit-learn is a precise exercise here, because each algorithm is deterministic once its starting point is fixed.

### 10.1 k-means: the algorithm (Lloyd's)

k-means assumes a cluster is a round blob around a centre, and minimises the **inertia**, the total squared distance from each point to its centre. Lloyd's algorithm alternates two steps until nothing changes:

1. **Assign** each point to its nearest centre.
2. **Update** each centre to the mean of its points.

Each step can only lower the inertia, so the loop always stops, but at a **local** minimum that depends on the start.

```python run
def kmeans_lloyd(X, init_centres, max_iter=300):
    C = np.array(init_centres, float)
    for it in range(max_iter):
        labels = np.argmin(pairwise_sq_dist(X, C), axis=1)
        newC = np.array([X[labels == k].mean(0) if np.any(labels == k) else C[k] for k in range(len(C))])
        if np.allclose(newC, C, rtol=0, atol=0):
            break
        C = newC
    inertia = float(pairwise_sq_dist(X, C)[np.arange(len(X)), labels].sum())
    return labels, C, inertia, it + 1

Xk, yk = datasets.make_blobs(n_samples=600, centers=4, cluster_std=1.3, random_state=7)
init = Xk[[0, 1, 2, 3]]                                            # a fixed, deliberately naive start
lab_o, C_o, in_o, it_o = kmeans_lloyd(Xk, init)
km = cluster.KMeans(n_clusters=4, init=init, n_init=1, algorithm="lloyd", tol=0, max_iter=300).fit(Xk)
print(f"ours: {it_o} iterations, inertia {in_o:.6f} | sklearn: {km.n_iter_} iterations, inertia {km.inertia_:.6f}")
compare("k-means centres (same start)", C_o, km.cluster_centers_, tol=1e-9)
print("identical labels:", bool(np.all(lab_o == km.labels_)))
```
```text
ours: 5 iterations, inertia 1905.309456 | sklearn: 5 iterations, inertia 1905.309456
k-means centres (same start)               max |ours - sklearn| = 5.33e-15  -> MATCH
identical labels: True
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate Lloyd's k-means on 600 two-dimensional points from 4 blobs, starting from 4 centres placed on the first four data points. For each of the 5 iterations show two frames: points coloured by nearest centre (assign), then centres moved to the mean of their points (update). Draw centres as large crosses with short arrows showing how far they moved, and print the inertia under each iteration."

### 10.2 k-means++ and restarts

A bad start gives a bad local minimum. **k-means++** picks the first centre at random and each next centre with probability proportional to its **squared distance** from the nearest centre chosen so far, so the starting centres spread out. scikit-learn uses k-means++ by default and runs several starts (`n_init`), keeping the lowest inertia.

```python run
def kmeans_pp(X, k, seed=0):
    r = np.random.default_rng(seed)
    centres = [X[r.integers(len(X))]]
    for _ in range(k - 1):
        d2 = pairwise_sq_dist(X, np.array(centres)).min(1)
        centres.append(X[r.choice(len(X), p=d2 / d2.sum())])
    return np.array(centres)

rows = []
for seed in range(6):
    _, _, inertia_rand, _ = kmeans_lloyd(Xk, Xk[np.random.default_rng(seed).choice(len(Xk), 4, replace=False)])
    _, _, inertia_pp, _ = kmeans_lloyd(Xk, kmeans_pp(Xk, 4, seed))
    rows.append((seed, inertia_rand, inertia_pp))
print(pd.DataFrame(rows, columns=["seed", "inertia, random start", "inertia, k-means++ start"]).round(1).to_string(index=False))
```
```text
 seed  inertia, random start  inertia, k-means++ start
    0            1,905.30000               1,905.30000
    1            5,863.80000               1,905.30000
    2            1,905.30000               1,905.30000
    3           14,782.20000               1,905.30000
    4            5,863.80000               1,905.30000
    5            1,905.30000               1,905.30000
```

### 10.3 Where k-means fails

k-means draws straight boundaries halfway between centres. It cannot find curved clusters, and it splits big clusters to balance inertia.

> **Predict the output.** Two interleaving half-moons, k-means with two clusters. The adjusted Rand index is 1 for a perfect recovery of the moons and 0 for chance. Roughly what will k-means score?

<details><summary>Answer</summary>

About **0.27**: far from perfect. k-means draws a straight line halfway between two centres, so it cuts each moon in two and joins the halves, instead of following the curves. DBSCAN (next section) scores 1.0 on the same data.

</details>

```python run
Xmn, ymn = datasets.make_moons(n_samples=400, noise=0.06, random_state=0)
km2 = cluster.KMeans(n_clusters=2, n_init=10, random_state=0).fit(Xmn)
print("k-means on two moons, adjusted Rand index vs the true moons:", round(metrics.adjusted_rand_score(ymn, km2.labels_), 3), "(1 = perfect, 0 = chance)")
```
```text
k-means on two moons, adjusted Rand index vs the true moons: 0.274 (1 = perfect, 0 = chance)
```

### 10.4 DBSCAN: clusters as dense regions

**DBSCAN** says a cluster is a region where points are packed densely, separated by sparse regions. Two parameters: `eps` (a radius) and `min_samples`.

- A **core point** has at least `min_samples` points (itself included) within distance `eps`.
- Core points within `eps` of each other belong to the same cluster, and so do the points they reach in a chain.
- A non-core point within `eps` of a core point is a **border point** and joins that core's cluster.
- Everything else is **noise** (label −1).

No number of clusters is needed, any shape is possible, and outliers are labelled as such. The weak spot: one `eps` for the whole dataset, so clusters of very different density are hard.

To match scikit-learn exactly we copy its expansion order: visit points by index; from each unlabelled core point, grow a cluster with a **stack** (depth first). A border point near two clusters goes to whichever reaches it first, which is why the order matters.

```python run
def dbscan_scratch(X, eps, min_samples):
    d2 = pairwise_sq_dist(X, X)
    neigh = [np.flatnonzero(row <= eps * eps) for row in d2]
    core = np.array([len(nb) >= min_samples for nb in neigh])
    labels = np.full(len(X), -1)
    label = 0
    for i in range(len(X)):
        if labels[i] != -1 or not core[i]:
            continue
        stack = [i]
        while stack:
            p = stack.pop()
            if labels[p] == -1:
                labels[p] = label
                if core[p]:
                    stack.extend(v for v in neigh[p] if labels[v] == -1)
        label += 1
    return labels, core

lab_d, core_d = dbscan_scratch(Xmn, eps=0.2, min_samples=5)
db = cluster.DBSCAN(eps=0.2, min_samples=5).fit(Xmn)
print("clusters ours:", len(set(lab_d) - {-1}), "| sklearn:", len(set(db.labels_) - {-1}), "| noise points ours:", int(np.sum(lab_d == -1)), "sklearn:", int(np.sum(db.labels_ == -1)))
print("identical core points:", bool(np.array_equal(np.flatnonzero(core_d), db.core_sample_indices_)), "| identical labels:", bool(np.array_equal(lab_d, db.labels_)))
print("DBSCAN on two moons, adjusted Rand index:", round(metrics.adjusted_rand_score(ymn, lab_d), 3))
```
```text
clusters ours: 2 | sklearn: 2 | noise points ours: 0 sklearn: 0
identical core points: True | identical labels: True
DBSCAN on two moons, adjusted Rand index: 1.0
```

Choosing `eps`: compute every point's distance to its `min_samples`-th nearest neighbour, sort, and look for the "knee" where the curve bends upward; points beyond it are in sparse regions.

```python run
kd = np.sort(np.sqrt(np.sort(pairwise_sq_dist(Xmn, Xmn), axis=1)[:, 4]))
print("5th-neighbour distance at percentiles 50, 80, 90, 95, 99:", np.percentile(kd, [50, 80, 90, 95, 99]).round(3))
```
```text
5th-neighbour distance at percentiles 50, 80, 90, 95, 99: [0.064 0.087 0.105 0.118 0.149]
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the 'two moons' dataset (two interleaved crescents of points) and show DBSCAN with eps = 0.2 and min_samples = 5. Draw a circle of radius eps around a few points. Colour core points (at least 5 points inside the circle, itself included) as solid, border points as hollow, noise as grey crosses. Show how a cluster grows by chaining from core to core point until both crescents are found."

### 10.5 Hierarchical (agglomerative) clustering

Start with every point as its own cluster and repeatedly **merge the two closest clusters** until one remains. The full history of merges is a tree (a **dendrogram**); cutting it at a height or at `k` clusters gives a clustering. "Closest clusters" needs a **linkage** rule:

| Linkage | Distance between clusters A and B | Character |
|---|---|---|
| single | closest pair of points | follows chains; can link everything through a thin bridge |
| complete | farthest pair of points | compact clusters |
| average | mean of all pairwise distances | in between |
| Ward | increase in total within-cluster variance | like k-means, round clusters of similar size |

A naive implementation keeps a matrix of cluster distances and updates it after each merge. For average linkage, the distance from a new cluster `A∪B` to `C` is the size-weighted mean `(|A|·d(A,C) + |B|·d(B,C)) / (|A| + |B|)`.

```python run
def agglomerative_average(X):
    n = len(X)
    D = np.sqrt(pairwise_sq_dist(X, X))
    np.fill_diagonal(D, np.inf)
    size = {i: 1 for i in range(n)}
    active = list(range(n))
    members = {i: [i] for i in range(n)}
    Dfull = {(i, j): D[i, j] for i in range(n) for j in range(i + 1, n)}
    merges = []
    next_id = n
    def dist(a, b):
        return Dfull[(a, b)] if a < b else Dfull[(b, a)]
    while len(active) > 1:
        a, b = min(((a, b) for i, a in enumerate(active) for b in active[i + 1:]), key=lambda ab: dist(*ab))
        h = dist(a, b)
        for c in active:
            if c in (a, b):
                continue
            dnew = (size[a] * dist(a, c) + size[b] * dist(b, c)) / (size[a] + size[b])
            Dfull[(c, next_id)] = dnew
        size[next_id] = size[a] + size[b]
        members[next_id] = members[a] + members[b]
        merges.append((a, b, h, size[next_id]))
        active = [c for c in active if c not in (a, b)] + [next_id]
        next_id += 1
    return merges, members

Xh, yh = datasets.make_blobs(n_samples=60, centers=3, cluster_std=1.0, random_state=3)
merges, members = agglomerative_average(Xh)
Z = hierarchy.linkage(Xh, method="average")
compare("average linkage: merge heights vs scipy", np.array([m[2] for m in merges]), Z[:, 2], tol=1e-9)
lab_h = hierarchy.fcluster(Z, t=3, criterion="maxclust")
agg = cluster.AgglomerativeClustering(n_clusters=3, linkage="average").fit(Xh)
print("scipy cut at 3 clusters vs sklearn AgglomerativeClustering, adjusted Rand index:", round(metrics.adjusted_rand_score(lab_h, agg.labels_), 6))
# our own cut: undo the last two merges
last = merges[-1]
c1 = members[last[0]]; c2 = members[last[1]]
big = c1 if len(c1) > len(c2) else c2
prev = merges[-2]
ours3 = np.zeros(len(Xh), int)
for lbl, grp in enumerate([members[prev[0]], members[prev[1]], c2 if big is c1 else c1]):
    ours3[grp] = lbl
print("our cut at 3 clusters vs sklearn, adjusted Rand index:", round(metrics.adjusted_rand_score(ours3, agg.labels_), 6))
```
```text
average linkage: merge heights vs scipy    max |ours - sklearn| = 3.58e-14  -> MATCH
scipy cut at 3 clusters vs sklearn AgglomerativeClustering, adjusted Rand index: 1.0
our cut at 3 clusters vs sklearn, adjusted Rand index: 1.0
```

Our naive version is cubic in the number of points (fine for 60, hopeless for 60,000). Libraries use smarter algorithms, and still the memory for all pairwise distances limits hierarchical clustering to tens of thousands of points.

### 10.6 Single linkage chains

```python run
for link in ["single", "average", "ward"]:
    a = cluster.AgglomerativeClustering(n_clusters=2, linkage=link).fit(Xmn)
    print(f"{link:8s} linkage on two moons: adjusted Rand index {metrics.adjusted_rand_score(ymn, a.labels_):.3f}")
```
```text
single   linkage on two moons: adjusted Rand index 1.000
average  linkage on two moons: adjusted Rand index 0.329
ward     linkage on two moons: adjusted Rand index 0.239
```

On the moons the chaining that is usually a weakness of single linkage is exactly right; Ward, which likes round clusters, behaves like k-means. No linkage is best in general; each encodes a belief about what a cluster is.

### 10.7 Try it

1. Make three blobs with standard deviations 0.5, 1.0 and 3.0 and run DBSCAN with one `eps`. Which cluster breaks into noise? Try `cluster.HDBSCAN`, which adapts to varying density.
2. Change `agglomerative_average` to single linkage (the new distance is the **minimum** of the two old ones) and match `hierarchy.linkage(method="single")`.

## 11. PCA for compression and feature reduction

### 11.1 The idea

PCA finds new axes for the data: the first **principal component** is the direction along which the data vary most, the second is the direction of most remaining variance at right angles to the first, and so on (ds.01 built it from eigenvectors). Keeping only the first `k` components gives the best `k`-dimensional linear summary of the data, in the sense of the smallest squared reconstruction error.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 2D elongated cloud of points tilted at an angle. Overlay the first principal component as a long arrow along the direction of greatest variance, and the second at right angles to it, shorter. Then show each point projected straight onto the first axis, with little lines for the reconstruction error. Label 'PC1 = most variance' and 'projection keeps the position along PC1, drops the rest'."

### 11.2 Two routes to the same answer

1. **Eigen route**: centre the data, compute the covariance matrix `XcᵀXc / (n − 1)`, take its eigenvectors sorted by eigenvalue.
2. **SVD route** (what libraries use, more accurate): `Xc = U S Vᵀ`. The rows of `Vᵀ` are the components and `S² / (n − 1)` are the variances.

Each component is defined only up to its **sign** (`v` and `−v` describe the same axis), so two correct implementations can disagree by a factor of −1. scikit-learn fixes the sign so that the largest-magnitude entry of each component is positive; we copy that rule.

```python run
class PCAScratch:
    def __init__(self, n_components):
        self.n_components = n_components
    def fit(self, X):
        X = np.asarray(X, float)
        self.mean_ = X.mean(0)
        U, S, Vt = np.linalg.svd(X - self.mean_, full_matrices=False)
        signs = np.sign(Vt[np.arange(len(Vt)), np.argmax(np.abs(Vt), axis=1)])     # largest entry positive
        Vt = Vt * signs[:, None]
        self.components_ = Vt[: self.n_components]
        var = S ** 2 / (len(X) - 1)
        self.explained_variance_ = var[: self.n_components]
        self.explained_variance_ratio_ = (var / var.sum())[: self.n_components]
        return self
    def transform(self, X):
        return (np.asarray(X, float) - self.mean_) @ self.components_.T
    def inverse_transform(self, Z):
        return Z @ self.components_ + self.mean_

digits = datasets.load_digits()
Xd = digits.data                                              # 1,797 images of 8x8 pixels = 64 features
p_ours = PCAScratch(10).fit(Xd)
p_sk = decomposition.PCA(n_components=10, svd_solver="full").fit(Xd)
compare("PCA components (sign rule applied)", p_ours.components_, p_sk.components_, tol=1e-9)
compare("PCA explained variance", p_ours.explained_variance_, p_sk.explained_variance_, tol=1e-8)
compare("PCA transform", p_ours.transform(Xd[:50]), p_sk.transform(Xd[:50]), tol=1e-8)
# the eigen route gives the same variances
evals = np.sort(np.linalg.eigvalsh(np.cov(Xd, rowvar=False)))[::-1][:10]
compare("eigenvalues of the covariance matrix", evals, p_sk.explained_variance_, tol=1e-8)
```
```text
PCA components (sign rule applied)         max |ours - sklearn| = 5.80e-15  -> MATCH
PCA explained variance                     max |ours - sklearn| = 3.69e-13  -> MATCH
PCA transform                              max |ours - sklearn| = 3.99e-13  -> MATCH
eigenvalues of the covariance matrix       max |ours - sklearn| = 3.69e-13  -> MATCH
```

### 11.3 Compression

How many of the 64 pixel dimensions do the digit images really need?

```python run
p_all = PCAScratch(64).fit(Xd)
cum = np.cumsum(p_all.explained_variance_ratio_)
rows = []
for k in [2, 5, 10, 20, 30, 40]:
    pk = PCAScratch(k).fit(Xd)
    rec = pk.inverse_transform(pk.transform(Xd))
    rows.append((k, cum[k - 1], np.sqrt(np.mean((rec - Xd) ** 2)), 64 / k))
print(pd.DataFrame(rows, columns=["components", "variance kept", "RMS pixel error (0-16 scale)", "compression factor"]).round(3).to_string(index=False))
print("components needed for 95% of the variance:", int(np.searchsorted(cum, 0.95) + 1))
```
```text
 components  variance kept  RMS pixel error (0-16 scale)  compression factor
          2        0.28500                       3.66300            32.00000
          5        0.54500                       2.92300            12.80000
         10        0.73800                       2.21700             6.40000
         20        0.89400                       1.40900             3.20000
         30        0.95900                       0.87600             2.13300
         40        0.98800                       0.47100             1.60000
components needed for 95% of the variance: 29
```

### 11.4 Feature reduction before a model

PCA as a pipeline step (fitted inside each fold, ds.05) reduces 64 columns to a few dozen. It helps models that suffer from many correlated or noisy features (k-NN, section 4.5) and speeds up training; it can also throw away a low-variance direction that happens to be the predictive one, because PCA never looks at `y`.

```python run
rows = []
for k in [5, 10, 20, 40, None]:
    steps = [preprocessing.StandardScaler()] + ([decomposition.PCA(k)] if k else []) + [neighbors.KNeighborsClassifier(5)]
    t0 = time.perf_counter()
    acc = model_selection.cross_val_score(pipeline.make_pipeline(*steps), Xd, digits.target, cv=5).mean()
    rows.append((k or 64, acc, time.perf_counter() - t0))
print(pd.DataFrame(rows, columns=["dimensions given to k-NN", "CV accuracy", "seconds"]).round(4).to_string(index=False))
```
```text
 dimensions given to k-NN  CV accuracy  seconds
                        5      0.82750  0.04170
                       10      0.89260  0.05980
                       20      0.93660  0.39080
                       40      0.93880  0.26430
                       64      0.94440  0.09240
```

Read this table honestly: on the digits, k-NN does best with **all 64** pixel columns, and PCA only *matches* that once it keeps about 20 to 40 components. The 64 pixels here are few, clean and on the same scale, so there is little noise for PCA to remove. Its value in this case is compression (a third of the columns for under 1% of accuracy), not better predictions. PCA earns its place when there are hundreds of noisy, correlated columns.

### 11.5 Traps

- **Scale first** when columns have different units; otherwise the first component is just "the column with the biggest numbers".
- **Components are not features with meaning.** A component mixes all columns; interpreting it needs care (look at its largest loadings).
- **Variance is not importance for prediction.** A tiny direction can carry the whole signal.
- **Signs are arbitrary**; never compare components across runs or libraries without fixing the sign.

### 11.6 Try it

1. Fit PCA on the cancer data with and without `StandardScaler`. Print the share of variance of the first component and its largest loading in each case.
2. Build a 2-D dataset where class depends only on the *second* principal direction (small variance). Show that `PCA(1)` + logistic regression fails while logistic regression on the raw data succeeds.

## 12. t-SNE and UMAP: for looking, not for measuring

### 12.1 What they are for

t-SNE and UMAP squeeze high-dimensional data into 2-D for a picture in which **points that are neighbours in the original space stay neighbours**. They are excellent at that, and the pictures are striking, which is exactly the danger: people read them like maps, with distances, sizes and gaps. They are not maps.

### 12.2 How t-SNE works, briefly

1. In the original space, turn distances into **neighbour probabilities**: for each point `i`, a Gaussian centred on `i` gives each other point `j` a probability `p_j|i`. The width of that Gaussian is chosen **separately for every point** so that each point has about the same effective number of neighbours, the **perplexity** (typically 5 to 50).
2. In 2-D, define similar probabilities `q_ij`, but with a **heavy-tailed** Student-t distribution.
3. Move the 2-D points to make `q` match `p`, by minimising the KL divergence `Σ p_ij log(p_ij / q_ij)` with gradient descent from a random (or PCA) start.

Each of those three steps destroys a kind of distance information:

- Step 1 adapts the width to local density, so a **tight cluster and a loose cluster come out the same size**.
- Step 2's heavy tails push moderately distant points much further apart, so **gaps between clusters are exaggerated and arbitrary**.
- Step 3's KL divergence punishes putting true neighbours far apart, but barely cares about putting far points at any particular far distance, so **distances between clusters are not preserved**. The problem is also non-convex: different runs give different pictures.

### 12.3 An experiment with known geometry

Three clusters in 10 dimensions. A and B are close to each other; C is ten times further away. A is tight (spread 0.5), B is loose (spread 3).

> **Predict the output.** In the data below, cluster B is six times as wide as cluster A, and the gap A–C is ten times the gap A–B. After t-SNE, will B still look about six times wider than A?

<details><summary>Answer</summary>

No. In the t-SNE pictures B comes out only 1.2 to 2.7 times as wide as A, depending on the perplexity. t-SNE gives every point a neighbourhood of about the same *number* of neighbours, so dense and sparse clusters are drawn at similar sizes.

</details>

```python run
rng = np.random.default_rng(0)
dim = 10
centre = {"A": np.zeros(dim), "B": np.r_[5.0, np.zeros(dim - 1)], "C": np.r_[50.0, np.zeros(dim - 1)]}
spread = {"A": 0.5, "B": 3.0, "C": 1.0}
X_ts = np.vstack([centre[g] + rng.normal(0, spread[g], (150, dim)) for g in "ABC"])
g_ts = np.repeat(list("ABC"), 150)

def geometry(Y):
    cen = {g: Y[g_ts == g].mean(0) for g in "ABC"}
    size = {g: np.sqrt(((Y[g_ts == g] - cen[g]) ** 2).sum(1)).mean() for g in "ABC"}
    return {"dist A-B": np.linalg.norm(cen["A"] - cen["B"]), "dist A-C": np.linalg.norm(cen["A"] - cen["C"]),
            "ratio (A-B)/(A-C)": np.linalg.norm(cen["A"] - cen["B"]) / np.linalg.norm(cen["A"] - cen["C"]),
            "size A": size["A"], "size B": size["B"], "ratio size B/A": size["B"] / size["A"]}

rows = {"original 10-D": geometry(X_ts), "PCA 2-D": geometry(decomposition.PCA(2).fit_transform(X_ts))}
for perp in [5, 30, 100]:
    Y = manifold.TSNE(n_components=2, perplexity=perp, init="pca", random_state=0).fit_transform(X_ts)
    rows[f"t-SNE perplexity {perp}"] = geometry(Y)
print(pd.DataFrame(rows).T.round(2).to_string())
```
```text
                      dist A-B  dist A-C  ratio (A-B)/(A-C)   size A   size B  ratio size B/A
original 10-D          5.00000  50.01000            0.10000  1.52000  9.23000         6.07000
PCA 2-D                4.95000  50.01000            0.10000  0.62000  4.48000         7.20000
t-SNE perplexity 5    45.68000  67.86000            0.67000 17.26000 21.19000         1.23000
t-SNE perplexity 30   12.73000  49.18000            0.26000  5.32000  8.31000         1.56000
t-SNE perplexity 100   1.92000  30.23000            0.06000  0.90000  2.43000         2.69000
```

Read the columns:

- **Distances between clusters.** In the original data A–B is a tenth of A–C (ratio 0.10). PCA keeps that ratio. In the t-SNE pictures the ratio ranges from 0.06 to 0.67 depending only on the perplexity. One setting happens to land near the truth, but nothing in the picture tells you which one: without knowing the real geometry (which you never do with real data), the gap between clusters carries no reliable information.
- **Cluster sizes.** B is six times wider than A in reality. In t-SNE the two come out much closer in size, because each point's neighbourhood width was adapted to its local density.

### 12.4 What t-SNE does preserve: neighbours

```python run
from scipy.spatial.distance import pdist
Y30 = manifold.TSNE(n_components=2, perplexity=30, init="pca", random_state=0).fit_transform(X_ts)
Y_pca = decomposition.PCA(2).fit_transform(X_ts)
d_orig = pdist(X_ts)
for name, Y in [("PCA 2-D", Y_pca), ("t-SNE", Y30)]:
    rho = stats.spearmanr(d_orig, pdist(Y)).statistic
    tw = manifold.trustworthiness(X_ts, Y, n_neighbors=10)
    print(f"{name:8s} rank correlation of ALL pairwise distances {rho:.3f} | trustworthiness of 10 nearest neighbours {tw:.3f}")
```
```text
PCA 2-D  rank correlation of ALL pairwise distances 0.974 | trustworthiness of 10 nearest neighbours 0.839
t-SNE    rank correlation of ALL pairwise distances 0.780 | trustworthiness of 10 nearest neighbours 0.911
```

**Trustworthiness** (1 = perfect) measures whether the nearest neighbours in the picture were really near in the original space. t-SNE is designed to score high there; it is **not** designed to keep the global distances.

### 12.5 Different seeds, different pictures

```python run
for seed in [0, 1, 2]:
    Y = manifold.TSNE(n_components=2, perplexity=30, init="random", random_state=seed).fit_transform(X_ts)
    g = geometry(Y)
    print(f"seed {seed}: ratio (A-B)/(A-C) = {g['ratio (A-B)/(A-C)']:.2f}, size B/A = {g['ratio size B/A']:.2f}")
```
```text
seed 0: ratio (A-B)/(A-C) = 0.26, size B/A = 1.56
seed 1: ratio (A-B)/(A-C) = 0.24, size B/A = 1.65
seed 2: ratio (A-B)/(A-C) = 0.24, size B/A = 1.70
```

Here the summary numbers barely move between seeds, because this dataset is simple (three well-separated blobs). What changes is the layout itself: the picture is rotated, reflected and shifted. With real data that has many groups, whole groups also change places between runs. That is why the rule below asks for several seeds before trusting any global arrangement.

### 12.6 Rules for reading a t-SNE (or UMAP) plot

1. **Do** read: "these points are neighbours", "this group is separate from that group" (if it appears over many seeds and perplexities).
2. **Do not** read: the size of a cluster, the distance between clusters, the density inside a cluster, the meaning of the axes (they have none).
3. Run several perplexities and seeds; trust only what survives all of them.
4. Never cluster on t-SNE coordinates, and never feed them to a model as features; cluster in the original space (section 10) and use t-SNE only to *look*.
5. Random noise can show apparent "clusters" at low perplexity. Compare with a shuffled version of the data.

This is the outcome of the chapter: **distances in a t-SNE plot are not meaningful because the method adapts a separate neighbourhood width to each point's density (erasing sizes), uses heavy-tailed similarities in 2-D (exaggerating gaps), and optimises only how well neighbours are kept (ignoring far distances), from a random start (so the global layout changes between runs).**

### 12.7 UMAP

UMAP builds a nearest-neighbour graph in the original space and lays it out in 2-D so that the graph's structure is kept. It is faster than t-SNE, scales to millions of points, and often keeps somewhat more global structure, but the same rules apply: neighbourhoods are meaningful, distances and sizes are not. `n_neighbors` plays the role of perplexity and `min_dist` controls how tightly points are packed.

```python
# Try it on your machine:  pip install umap-learn   (not installed here, so no output is shown)
import umap
for nn in [5, 15, 50]:
    Y_u = umap.UMAP(n_neighbors=nn, min_dist=0.1, random_state=0).fit_transform(X_ts)
    print(nn, geometry(Y_u))
```

### 12.8 Try it

1. Run t-SNE on 450 points of pure noise (`rng.normal(size=(450, 10))`) with perplexity 5. Do you see "clusters"? Measure them with `geometry` using random group labels.
2. Run t-SNE on the digits data (`Xd`) and colour (or group) by the true digit. Which digits overlap? Then check whether the same digits are confused by the k-NN classifier of section 11.4.


## 13. Project: a from-scratch library checked against scikit-learn

### 13.1 The brief

Collect your implementations into a small library, **`scratchml`**, with the scikit-learn interface (`fit`, `predict`, `transform`, learned attributes ending in `_`), and prove with **automated tests** that each one matches scikit-learn on many random datasets, not just the one you happened to try. Then write a short comparison report: agreement level, speed, and what you learned from each disagreement.

The outcome of the chapter asks for three algorithms; the library below has five, each from a different family: an iterative optimiser (linear regression by gradient descent), a second-order optimiser (logistic regression by Newton's method), a probabilistic model (Gaussian Naive Bayes), a clustering algorithm (k-means) and a matrix decomposition (PCA). The decision tree of section 6 is the natural sixth; adding it, with a tie-aware test, is the first extension.

### 13.2 The library

```python run
import pathlib, tempfile, subprocess, os
proj = pathlib.Path(tempfile.mkdtemp()) / "scratchml_project"
proj.mkdir()
(proj / "scratchml.py").write_text('''"""scratchml: classic algorithms in NumPy, with the scikit-learn interface."""
import numpy as np
from scipy import special


def _sq_dist(A, B):
    return np.maximum((A ** 2).sum(1)[:, None] - 2 * A @ B.T + (B ** 2).sum(1)[None, :], 0)


class LinearRegressionGD:
    """Least squares by batch gradient descent on standardised features; weights reported in original units."""
    def __init__(self, learning_rate=0.1, max_iter=100000, tol=1e-10):
        self.learning_rate, self.max_iter, self.tol = learning_rate, max_iter, tol

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y, float)
        mu, sd = X.mean(0), X.std(0)
        sd[sd == 0] = 1.0
        Z = np.column_stack([np.ones(len(X)), (X - mu) / sd])
        theta = np.zeros(Z.shape[1])
        for self.n_iter_ in range(1, self.max_iter + 1):
            grad = 2 / len(y) * Z.T @ (Z @ theta - y)
            theta -= self.learning_rate * grad
            if np.max(np.abs(grad)) < self.tol:
                break
        self.coef_ = theta[1:] / sd
        self.intercept_ = theta[0] - np.sum(theta[1:] * mu / sd)
        return self

    def predict(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_


class LogisticRegressionNewton:
    """Binary logistic regression, objective 0.5*|w|^2 + C*sum(log loss), intercept not penalised."""
    def __init__(self, C=1.0, max_iter=50, tol=1e-10):
        self.C, self.max_iter, self.tol = C, max_iter, tol

    def fit(self, X, y):
        X = np.asarray(X, float)
        self.classes_, yb = np.unique(y, return_inverse=True)
        Xt = np.column_stack([np.ones(len(X)), X])
        theta = np.zeros(Xt.shape[1])
        reg = np.eye(Xt.shape[1]); reg[0, 0] = 0.0
        for self.n_iter_ in range(1, self.max_iter + 1):
            p = special.expit(Xt @ theta)
            grad = self.C * Xt.T @ (p - yb) + reg @ theta
            if np.max(np.abs(grad)) < self.tol:
                break
            H = self.C * (Xt.T * (p * (1 - p))) @ Xt + reg
            theta -= np.linalg.solve(H, grad)
        self.intercept_, self.coef_ = np.array([theta[0]]), theta[None, 1:]
        return self

    def decision_function(self, X):
        return np.asarray(X, float) @ self.coef_[0] + self.intercept_[0]

    def predict_proba(self, X):
        p = special.expit(self.decision_function(X))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return self.classes_[(self.decision_function(X) > 0).astype(int)]


class GaussianNB:
    def __init__(self, var_smoothing=1e-9):
        self.var_smoothing = var_smoothing

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y)
        self.classes_ = np.unique(y)
        eps = self.var_smoothing * np.var(X, axis=0).max()
        self.theta_ = np.array([X[y == c].mean(0) for c in self.classes_])
        self.var_ = np.array([X[y == c].var(0) for c in self.classes_]) + eps
        self.class_prior_ = np.array([np.mean(y == c) for c in self.classes_])
        return self

    def _jll(self, X):
        X = np.asarray(X, float)
        return (np.log(self.class_prior_) - 0.5 * np.sum(np.log(2 * np.pi * self.var_), 1)
                - 0.5 * (((X[:, None, :] - self.theta_) ** 2) / self.var_).sum(2))

    def predict_proba(self, X):
        j = self._jll(X)
        return np.exp(j - special.logsumexp(j, axis=1, keepdims=True))

    def predict(self, X):
        return self.classes_[np.argmax(self._jll(X), 1)]


class KMeans:
    """Lloyd's algorithm from given initial centres (or k-means++ with a seed)."""
    def __init__(self, n_clusters=8, init="k-means++", max_iter=300, seed=0):
        self.n_clusters, self.init, self.max_iter, self.seed = n_clusters, init, max_iter, seed

    def _plusplus(self, X):
        r = np.random.default_rng(self.seed)
        C = [X[r.integers(len(X))]]
        for _ in range(self.n_clusters - 1):
            d2 = _sq_dist(X, np.array(C)).min(1)
            C.append(X[r.choice(len(X), p=d2 / d2.sum())])
        return np.array(C)

    def fit(self, X):
        X = np.asarray(X, float)
        C = self._plusplus(X) if isinstance(self.init, str) else np.array(self.init, float)
        for self.n_iter_ in range(1, self.max_iter + 1):
            labels = np.argmin(_sq_dist(X, C), 1)
            newC = np.array([X[labels == k].mean(0) if np.any(labels == k) else C[k] for k in range(len(C))])
            if np.array_equal(newC, C):
                break
            C = newC
        self.cluster_centers_, self.labels_ = C, labels
        self.inertia_ = float(_sq_dist(X, C)[np.arange(len(X)), labels].sum())
        return self

    def predict(self, X):
        return np.argmin(_sq_dist(np.asarray(X, float), self.cluster_centers_), 1)


class PCA:
    def __init__(self, n_components):
        self.n_components = n_components

    def fit(self, X):
        X = np.asarray(X, float)
        self.mean_ = X.mean(0)
        _, S, Vt = np.linalg.svd(X - self.mean_, full_matrices=False)
        Vt = Vt * np.sign(Vt[np.arange(len(Vt)), np.argmax(np.abs(Vt), 1)])[:, None]
        var = S ** 2 / (len(X) - 1)
        self.components_ = Vt[: self.n_components]
        self.explained_variance_ = var[: self.n_components]
        self.explained_variance_ratio_ = (var / var.sum())[: self.n_components]
        return self

    def transform(self, X):
        return (np.asarray(X, float) - self.mean_) @ self.components_.T

    def inverse_transform(self, Z):
        return Z @ self.components_ + self.mean_
''', encoding="utf-8")
print("scratchml.py:", len((proj / "scratchml.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
scratchml.py: 141 lines
```

### 13.3 The match tests

Each test runs on **several random datasets** (pytest's `parametrize`), so a lucky agreement on one dataset cannot hide a bug. Every assertion message says which detail is the likely culprit, in the spirit of the problem tests in this course.

```python run
(proj / "test_scratchml.py").write_text('''import numpy as np, pytest
from sklearn import cluster, decomposition, linear_model, naive_bayes, datasets
import scratchml as sm

SEEDS = [0, 1, 2, 3, 4]

def regression_data(seed, n=300, d=4):
    r = np.random.default_rng(seed)
    X = r.normal(size=(n, d)) * r.uniform(0.1, 10, d) + r.uniform(-5, 5, d)
    return X, X @ r.normal(size=d) + r.normal() + r.normal(0, 0.5, n)

def classification_data(seed, n=300, d=4):
    r = np.random.default_rng(seed)
    X = r.normal(size=(n, d))
    return X, (r.random(n) < 1 / (1 + np.exp(-(X @ r.normal(size=d))))).astype(int)

@pytest.mark.parametrize("seed", SEEDS)
def test_linear_regression_gd(seed):
    X, y = regression_data(seed)
    ours, sk = sm.LinearRegressionGD().fit(X, y), linear_model.LinearRegression().fit(X, y)
    assert np.allclose(ours.coef_, sk.coef_, atol=1e-6), "weights differ: check the back-conversion from standardised units (divide by the std)"
    assert np.isclose(ours.intercept_, sk.intercept_, atol=1e-6), "intercept differs: it must absorb sum(w_z * mean / std)"

@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("C", [0.01, 1.0, 100.0])
def test_logistic_regression_newton(seed, C):
    X, y = classification_data(seed)
    ours = sm.LogisticRegressionNewton(C=C).fit(X, y)
    sk = linear_model.LogisticRegression(C=C, tol=1e-12, max_iter=10000).fit(X, y)
    assert np.allclose(ours.coef_, sk.coef_, atol=1e-6), "weights differ: is C multiplying the loss (not the penalty), and is the intercept unpenalised?"
    assert np.allclose(ours.predict_proba(X), sk.predict_proba(X), atol=1e-7)

@pytest.mark.parametrize("seed", SEEDS)
def test_gaussian_nb(seed):
    X, y = classification_data(seed)
    ours, sk = sm.GaussianNB().fit(X, y), naive_bayes.GaussianNB().fit(X, y)
    assert np.allclose(ours.var_, sk.var_, rtol=0, atol=1e-12), "variances differ: use ddof=0 and add var_smoothing * max variance"
    assert np.allclose(ours.predict_proba(X), sk.predict_proba(X), atol=1e-12)

@pytest.mark.parametrize("seed", SEEDS)
def test_kmeans_same_start(seed):
    X, _ = datasets.make_blobs(n_samples=400, centers=5, cluster_std=1.5, random_state=seed)
    init = X[:5]
    ours = sm.KMeans(5, init=init).fit(X)
    sk = cluster.KMeans(5, init=init, n_init=1, algorithm="lloyd", tol=0).fit(X)
    assert np.array_equal(ours.labels_, sk.labels_), "labels differ from the same start: check the assign/update order and the stopping rule"
    assert np.allclose(ours.cluster_centers_, sk.cluster_centers_, atol=1e-9)
    assert np.isclose(ours.inertia_, sk.inertia_, rtol=1e-10)

@pytest.mark.parametrize("seed", SEEDS)
def test_pca(seed):
    X, _ = regression_data(seed, d=6)
    ours, sk = sm.PCA(3).fit(X), decomposition.PCA(3, svd_solver="full").fit(X)
    assert np.allclose(ours.explained_variance_, sk.explained_variance_, rtol=1e-10), "variances differ: divide S**2 by n-1, not n"
    assert np.allclose(ours.components_, sk.components_, atol=1e-9), "components differ: apply the sign rule (largest entry positive)"
    Z = ours.transform(X)
    assert np.allclose(Z, sk.transform(X), atol=1e-8)
''', encoding="utf-8")
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_scratchml.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-600:] or res.stderr.strip()[-600:])
```
```text
...................................                                      [100%]
35 passed in 1.08s
```

### 13.4 The comparison report

The report is generated by code, never typed by hand: one row per algorithm with the agreement measured on a fresh dataset, and the time for both versions.

```python run
sys.path.insert(0, str(proj))
import importlib, scratchml as sm
importlib.reload(sm)

def timed(fn):
    t0 = time.perf_counter(); out = fn(); return out, time.perf_counter() - t0

rng = np.random.default_rng(42)
Xr_ = rng.normal(size=(5000, 8)) * rng.uniform(0.5, 5, 8); yr_ = Xr_ @ rng.normal(size=8) + rng.normal(0, 1, 5000)
Xc_ = rng.normal(size=(5000, 8)); yc_ = (rng.random(5000) < special.expit(Xc_ @ rng.normal(size=8))).astype(int)
Xk_, _ = datasets.make_blobs(n_samples=5000, centers=6, random_state=42)
rows = []
(o, to), (s, ts) = timed(lambda: sm.LinearRegressionGD().fit(Xr_, yr_)), timed(lambda: linear_model.LinearRegression().fit(Xr_, yr_))
rows.append(("linear regression (GD)", np.max(np.abs(o.coef_ - s.coef_)), to, ts, "exact (convex, same objective)"))
(o, to), (s, ts) = timed(lambda: sm.LogisticRegressionNewton(C=1.0).fit(Xc_, yc_)), timed(lambda: linear_model.LogisticRegression(C=1.0, tol=1e-12, max_iter=10000).fit(Xc_, yc_))
rows.append(("logistic regression (Newton)", np.max(np.abs(o.coef_ - s.coef_)), to, ts, "exact (convex, same objective)"))
(o, to), (s, ts) = timed(lambda: sm.GaussianNB().fit(Xc_, yc_)), timed(lambda: naive_bayes.GaussianNB().fit(Xc_, yc_))
rows.append(("Gaussian Naive Bayes", np.max(np.abs(o.predict_proba(Xc_) - s.predict_proba(Xc_))), to, ts, "exact (closed form)"))
init6 = Xk_[:6]
(o, to), (s, ts) = timed(lambda: sm.KMeans(6, init=init6).fit(Xk_)), timed(lambda: cluster.KMeans(6, init=init6, n_init=1, algorithm="lloyd", tol=0).fit(Xk_))
rows.append(("k-means (same start)", np.max(np.abs(o.cluster_centers_ - s.cluster_centers_)), to, ts, "exact (deterministic from the start)"))
(o, to), (s, ts) = timed(lambda: sm.PCA(4).fit(Xr_)), timed(lambda: decomposition.PCA(4, svd_solver="full").fit(Xr_))
rows.append(("PCA", np.max(np.abs(o.components_ - s.components_)), to, ts, "exact after the sign rule"))
report = pd.DataFrame(rows, columns=["algorithm", "max |difference|", "ours (s)", "sklearn (s)", "agreement level"]).set_index("algorithm")
report["max |difference|"] = report["max |difference|"].map(lambda v: f"{v:.1e}")
print(report.to_string(float_format=lambda v: f"{v:.4f}"))
```
```text
                             max |difference|  ours (s)  sklearn (s)                       agreement level
algorithm                                                                                                 
linear regression (GD)                3.9e-11    0.0046       0.0011        exact (convex, same objective)
logistic regression (Newton)          3.0e-08    0.0013       0.0031        exact (convex, same objective)
Gaussian Naive Bayes                  3.3e-15    0.0010       0.0015                   exact (closed form)
k-means (same start)                  1.2e-14    0.0139       0.0917  exact (deterministic from the start)
PCA                                   1.4e-15    0.0011       0.0020             exact after the sign rule
```

### 13.5 What to hand in

1. `scratchml.py` and `test_scratchml.py`, all tests passing.
2. The comparison report (13.4), regenerated on your machine.
3. For **each** algorithm, two or three sentences: which detail you had to get exactly right to match (for example "variances divide by n", "the intercept is not penalised", "PCA signs"), and how you found it.
4. One deliberate bug per algorithm, the failing test message it produced, and the fix. (Breaking your own code on purpose is how you check that a test can fail.)

### 13.6 Extensions

1. Add `DecisionTreeClassifier` from section 6 with a **tie-aware** test: require identical structure when `max_depth ≤ 3` on continuous data, and otherwise require that `first_difference` reports equal gains.
2. Add `DBSCAN` with an exact-labels test, and `BoostScratch` with a test that uses `min_samples_leaf=5`.
3. Add a `LinearSVM` (section 9) with an **approximate** test: objective within 0.1% of `SVC(kernel="linear")` and at least 99% prediction agreement.
4. Make `LinearRegressionGD` support mini-batches and an L2 penalty, and match `Ridge` (mind the mean-versus-sum scaling).
5. Add a `fit` timing benchmark over growing `n` and plot (or print) how each implementation scales. Which of yours grows fastest, and why?

## 14. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Gradient descent on unscaled features | crawls, or diverges at a larger step | standardise first, convert weights back (2.5) |
| Stopping on "small change in loss" | stops early on a flat stretch, answer off in the 6th digit | stop on the gradient size (2.4) |
| Penalising the intercept | intercept dragged toward 0, mismatch with libraries | leave the intercept out of the penalty (2.7, 3.1) |
| Confusing `C` with `α` | penalty applied the wrong way round | `C` multiplies the loss (bigger = weaker penalty), `α` multiplies the penalty (3.1) |
| Computing `log(sigmoid(z))` directly | `log(0)` = −inf for large `|z|` | use `logaddexp` / `expit` (3.2) |
| Comparing raw softmax weights | weights differ by a constant per class with identical predictions | compare predictions or probabilities (3.5) |
| k-NN without scaling | the largest-unit column decides everything | scale inside a pipeline (4.4) |
| k-NN with hundreds of features | all distances alike | fewer, better features; PCA first (4.5, 11.4) |
| Zero probabilities in Naive Bayes | one unseen word vetoes a class | Laplace smoothing `α` (5.4) |
| Trusting Naive Bayes probabilities | extreme over-confidence on correlated features | use the ranking; calibrate (5.3) |
| Calling a tree mismatch a bug (or "close enough") without checking | either a real bug is hidden or time is wasted | find the first differing node and compare gains (6.5) |
| Deep single trees | memorise the training set | limits, pruning, or a forest (6.6, 7) |
| Expecting a forest to match exactly | different random draws | compare distributions over seeds (7.3) |
| Too high a learning rate in boosting, no early stopping | overfitting after the best iteration | small rate + early stopping (8.3) |
| Comparing `LinearSVC` with `SVC(kernel="linear")` | different objectives (squared hinge, penalised intercept) | check the objective before comparing (9.4) |
| RBF SVM with large `γ` and `C` | memorises the training set | tune both on a log grid with scaling (9.5) |
| k-means on curved or unequal clusters | wrong groups with good-looking inertia | DBSCAN, agglomerative, or a mixture model (10.3, 10.4) |
| One `eps` for clusters of different density | dense clusters merge or sparse ones turn to noise | k-distance plot; HDBSCAN (10.4) |
| PCA without scaling | the first component is just the biggest-unit column | standardise first (11.5) |
| Comparing PCA components across runs | sign flips | fix the sign convention (11.2) |
| Reading t-SNE/UMAP distances or cluster sizes | invented conclusions | read neighbourhoods only; several seeds and perplexities (12.6) |
| Clustering or modelling on t-SNE coordinates | artefacts of the layout become "findings" | cluster in the original space (12.6) |

## 15. Summary

- **Implement, then match.** State the objective, implement it plainly, configure the library to solve the same problem, and compare at the right level: exact (deterministic, same objective), structural (ties), statistical (randomness) or approximate (early-stopped, non-smooth). A disagreement is understood only when you can name its cause.
- **Linear regression** has a closed form (least squares) and a gradient-descent form that needs scaled features and a sensible stopping rule; ridge adds `α‖w‖²` without penalising the intercept.
- **Logistic regression** maximises likelihood: the gradient is `Xᵀ(p − y)`, gradient descent works, and **Newton's method** converges in a handful of steps by using curvature. `C` is an inverse penalty. Softmax extends it to many classes.
- **k-NN** stores the data and votes among the nearest points; it needs scaling and few dimensions. **Naive Bayes** multiplies per-feature likelihoods under an independence assumption: fast, good at ranking, over-confident.
- **Decision trees** split greedily on the largest impurity reduction (Gini, entropy, variance); scikit-learn's details (float32, midpoints, random feature order) make exact matching possible except at **ties**, which are common with correlated features and small nodes. **Random forests** average decorrelated deep trees (bagging + feature subsampling) and give a free out-of-bag estimate. **Gradient boosting** adds shallow trees fitted to the negative gradient, scaled by a learning rate; with squared error it reproduces scikit-learn exactly. Histogram methods (LightGBM, `HistGradientBoosting`, XGBoost's hist mode) make it fast.
- **SVMs** maximise the margin with the hinge loss; `C` prices violations; kernels give curved boundaries; `SVC` and `LinearSVC` solve different objectives by default.
- **Clustering**: k-means (round clusters, depends on the start; k-means++ and restarts), DBSCAN (dense regions, noise, one density scale), hierarchical (a dendrogram; the linkage encodes what a cluster is).
- **PCA** finds orthogonal directions of maximum variance by SVD; it compresses (the digits keep most of their variance in a fraction of the dimensions) and reduces features for models, but never looks at the target.
- **t-SNE and UMAP** keep neighbourhoods and discard global geometry: per-point bandwidths erase cluster sizes, heavy tails exaggerate gaps, the objective ignores far distances, and every run differs.

You reached the outcomes: you **implemented algorithms from scratch and matched scikit-learn** (linear and logistic regression, Naive Bayes, k-NN, k-means, PCA and gradient boosting to about 1e-9 or better, decision trees structurally with proven ties, the SVM approximately), and you can **explain why distances in a t-SNE plot are not meaningful**, with an experiment whose true geometry you knew. Next, ds.07 turns to time-series forecasting, where the order of the rows is the whole point.
