# Chapter 1 (DS): Mathematics for data science

Every machine-learning library hides a small amount of mathematics behind a friendly function. `LinearRegression().fit(X, y)` solves a system of equations. `PCA` finds the eigenvectors of a matrix. A neural network learns by following a gradient downhill. A confidence interval comes from a sampling distribution, and a p-value from a probability. When these things work you never see the mathematics. When they fail (a matrix that cannot be inverted, a gradient that explodes, an interval that does not mean what you thought) you must know what is underneath, or you are guessing.

This chapter teaches exactly that mathematics, in four parts: **linear algebra** (vectors, matrices, eigenvalues, the SVD), **calculus** (derivatives, partial derivatives, gradients), **probability** (random variables, Bayes' theorem, distributions) and **statistical inference** (confidence intervals, hypothesis tests, p-values, the bootstrap). The rule of the chapter is the last line of the syllabus entry: **every concept is implemented in NumPy**. We do not just state that the gradient of a function points uphill; we compute one by hand, compute it again numerically, and watch the two agree. We do not just state that a 95% interval covers the truth 95% of the time; we run ten thousand experiments and count.

By the end you reach two outcomes: **you can compute a gradient by hand and verify it numerically**, and **you can run a bootstrap and interpret its interval**. The project then asks you to build a small toolkit of these functions from scratch and test it against NumPy and SciPy.

Prerequisites: da.02 (NumPy arrays, shapes, broadcasting, axes). You do not need earlier mathematics beyond school algebra; every idea is built from a picture or a small computation first, and the formal statement comes second. Where a section uses a result without proving it (the central limit theorem, for example), the code shows it working, which is the kind of evidence a practitioner uses every day.

> **How to read this chapter.** Mathematics is learned with the pencil moving. Every "Predict" box has a closed answer; try on paper first. Do not skip the *checks*: a function that you have not compared with a trusted one is a guess.

> **Offline rule for this chapter.** Only NumPy is needed for the chapter itself; SciPy appears only to **check** what we built (it is installed in the course environment). Nothing is downloaded. All random data come from seeded generators (`np.random.default_rng(seed)`), so you get the same numbers I did. Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, itertools, tempfile, pathlib
import numpy as np

np.set_printoptions(precision=4, suppress=True, linewidth=100)
print("python", sys.version.split()[0])
print("numpy ", np.__version__)
try:
    import scipy
    from scipy import stats, linalg as sla
    print("scipy ", scipy.__version__, "(used only to check our own code)")
except ImportError:
    scipy = None
    print("scipy not installed: the SciPy checks will be skipped")
```
```text
python 3.14.4
numpy  2.5.4
scipy  1.18.1 (used only to check our own code)
```

## Table of contents

1. [Vectors](#1-vectors)
2. [Matrices](#2-matrices)
3. [Solving linear systems, rank and inverses](#3-solving-linear-systems-rank-and-inverses)
4. [Eigenvalues and eigenvectors](#4-eigenvalues-and-eigenvectors)
5. [The singular value decomposition](#5-the-singular-value-decomposition)
6. [Derivatives](#6-derivatives)
7. [Partial derivatives and gradients](#7-partial-derivatives-and-gradients)
8. [Gradient descent](#8-gradient-descent)
9. [Probability](#9-probability)
10. [Bayes' theorem](#10-bayes-theorem)
11. [Random variables and distributions](#11-random-variables-and-distributions)
12. [Sampling, the law of large numbers and the central limit theorem](#12-sampling-the-law-of-large-numbers-and-the-central-limit-theorem)
13. [Confidence intervals](#13-confidence-intervals)
14. [Hypothesis tests and p-values](#14-hypothesis-tests-and-p-values)
15. [The bootstrap](#15-the-bootstrap)
16. [Project: a statistics and linear-algebra toolkit](#16-project-a-statistics-and-linear-algebra-toolkit)
17. [Common traps](#17-common-traps)
18. [Summary](#18-summary)

## 1. Vectors

### 1.1 A list of numbers with a geometry

A **vector** is an ordered list of numbers. In data science a vector is almost always **one row of data**: a customer described by age, income and number of visits is the vector `[34, 52000, 7]`. Treating the row as a point (or an arrow) in space lets us use geometry: distance, angle and direction. Two customers who are close in this space are similar; this single idea sits behind nearest-neighbour search, clustering and recommendation.

In NumPy a vector is a one-dimensional array.

```python run
a = np.array([3.0, 4.0])
b = np.array([1.0, 2.0])

print("a + b      =", a + b)
print("a - b      =", a - b)
print("2 * a      =", 2 * a)
print("shape      =", a.shape, "| ndim =", a.ndim)
```
```text
a + b      = [4. 6.]
a - b      = [2. 2.]
2 * a      = [6. 8.]
shape      = (2,) | ndim = 1
```

Addition and scaling act **element by element**: these two operations (adding vectors, multiplying by a number) are all that "linear" means, and every result in this part of the chapter grows from them. A **linear combination** such as `2a - 3b` is built only with those two operations.

### 1.2 Length (the norm)

The **length** of a vector is found with Pythagoras: for `[3, 4]` it is the square root of `3² + 4²`, which is 5. In more dimensions the same rule applies: square every component, add, take the square root. This is the **L2 norm**, written ‖a‖.

```python run
def norm(v):
    """The L2 norm: the square root of the sum of squares."""
    v = np.asarray(v, dtype=float)
    return math.sqrt(float(np.sum(v * v)))


print("norm([3, 4])                 =", norm([3, 4]))
print("np.linalg.norm([3, 4])       =", np.linalg.norm([3, 4]))

v = np.array([1.0, -2.0, 2.0])
print("\nnorm([1, -2, 2])             =", norm(v))
print("L1 norm (sum of |v|)         =", np.abs(v).sum(), "  == np.linalg.norm(v, 1):", np.linalg.norm(v, 1))
print("max norm (largest |v|)       =", np.abs(v).max(), "  == np.linalg.norm(v, np.inf):", np.linalg.norm(v, np.inf))
```
```text
norm([3, 4])                 = 5.0
np.linalg.norm([3, 4])       = 5.0

norm([1, -2, 2])             = 3.0
L1 norm (sum of |v|)         = 5.0   == np.linalg.norm(v, 1): 5.0
max norm (largest |v|)       = 2.0   == np.linalg.norm(v, np.inf): 2.0
```

The L1 norm (the sum of absolute values) and the max norm are the other common measures of size. They matter later: the L2 norm is what least squares and ridge regression penalise; the L1 norm gives the lasso its tendency to set coefficients to exactly zero.

A **unit vector** has length 1. To get the **direction** of any non-zero vector, divide it by its length.

```python run
u = a / norm(a)
print("direction of a =", u, "| its length =", norm(u))
```
```text
direction of a = [0.6 0.8] | its length = 1.0
```

### 1.3 The dot product

The **dot product** of two vectors multiplies matching components and adds them up:

`a · b = a₁b₁ + a₂b₂ + … + aₙbₙ`

```python run
a = np.array([3.0, 4.0])
b = np.array([1.0, 2.0])
manual = sum(x * y for x, y in zip(a, b))
print("by hand      :", manual)
print("a @ b        :", a @ b)
print("np.dot(a, b) :", np.dot(a, b))
print("a * b, summed:", (a * b).sum())
```
```text
by hand      : 11.0
a @ b        : 11.0
np.dot(a, b) : 11.0
a * b, summed: 11.0
```

The dot product has a second meaning, and it is the more important one: 

`a · b = ‖a‖ ‖b‖ cos θ`, where θ is the angle between the vectors.

So the dot product measures **how much two vectors point the same way**. It is large and positive when they point together, zero when they are perpendicular (**orthogonal**), negative when they point apart. Rearranging gives the **cosine similarity**, the standard measure of similarity between two documents, users or embeddings, and the angle itself.

```python run
def cosine_similarity(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float(x @ y) / (norm(x) * norm(y))


pairs = {"same direction": ([1, 2], [2, 4]), "perpendicular": ([1, 0], [0, 5]), "opposite": ([1, 2], [-1, -2]), "a and b": ([3, 4], [1, 2])}
for name, (x, y) in pairs.items():
    c = cosine_similarity(x, y)
    print(f"{name:15} cos = {c:7.4f}   angle = {math.degrees(math.acos(max(-1.0, min(1.0, c)))):6.2f} degrees")
```
```text
same direction  cos =  1.0000   angle =   0.00 degrees
perpendicular   cos =  0.0000   angle =  90.00 degrees
opposite        cos = -1.0000   angle = 180.00 degrees
a and b         cos =  0.9839   angle =  10.30 degrees
```

Notice that `[1, 2]` and `[2, 4]` have cosine exactly 1 although their lengths differ: cosine similarity looks at **direction only**. That is why it suits word counts (a long and a short document about the same topic point the same way) and why it is the wrong tool when the size matters (a customer who spends ten times as much is similar in direction but not in value).

> **Predict the output.** What is the dot product of `[1, 2, 3]` with `[4, -5, 6]`? Are the two vectors closer to perpendicular, or to pointing together?

<details><summary>Answer</summary>

```python run
p, q = np.array([1, 2, 3]), np.array([4, -5, 6])
print(p @ q, "| cosine:", round(cosine_similarity(p, q), 4))
```
```text
12 | cosine: 0.3655
```

`1·4 + 2·(−5) + 3·6 = 4 − 10 + 18 = 12`. The cosine is small and positive: the vectors are closer to perpendicular than to parallel (the angle is about 69 degrees).

</details>

### 1.4 Distance, and why scale matters

The **Euclidean distance** between two points is the norm of their difference: `‖a − b‖`. Nearest-neighbour methods, k-means and many others are built on it. It has a trap: it adds up squared differences **of whatever units each column has**. If one column is income in rupees (tens of thousands) and another is age in years (tens), the distance is almost entirely income.

```python run
cust = np.array([[34, 52000.0, 7], [35, 52100.0, 7], [60, 52050.0, 7], [34, 90000.0, 7]])
names = ["A", "B", "C", "D"]


def distances_from_first(M):
    return [round(float(np.linalg.norm(M[0] - r)), 2) for r in M[1:]]


print("raw columns       -> distance of B, C, D from A:", distances_from_first(cust))

mu, sd = cust.mean(axis=0), cust.std(axis=0)
sd[sd == 0] = 1.0                                    # a constant column would divide by zero
z = (cust - mu) / sd
print("standardised cols -> distance of B, C, D from A:", distances_from_first(z))
```
```text
raw columns       -> distance of B, C, D from A: [100.0, 56.36, 38000.0]
standardised cols -> distance of B, C, D from A: [0.09, 2.34, 2.31]
```

On the raw columns, B (one year older, 100 rupees richer) seems *further* from A than C (26 years older) because the 100-rupee gap swamps the 26-year gap. After **standardising** (subtract the mean, divide by the standard deviation, so every column has mean 0 and spread 1) the ranking reflects what a person would call similar. This is why almost every distance-based method in ds.03 begins with scaling.

### 1.5 Projection and orthogonality

The **projection** of `a` onto a direction `d` is the part of `a` that lies along `d`. Its length is `a · d̂` (with `d̂` the unit direction) and the vector itself is `(a · d̂) d̂`. What is left over, `a − projection`, is **orthogonal** to `d`.

```python run
def project(a, d):
    d = np.asarray(d, float)
    return (a @ d) / (d @ d) * d


a = np.array([3.0, 4.0])
d = np.array([1.0, 0.0])
p = project(a, d)
resid = a - p
print("projection of [3, 4] onto the x axis:", p, "| residual:", resid)
print("residual . direction =", resid @ d, "(zero: orthogonal)")

d2 = np.array([1.0, 1.0])
p2 = project(a, d2)
print("\nprojection onto [1, 1]:", p2, "| residual:", a - p2, "| dot:", round(float((a - p2) @ d2), 12))
print("Pythagoras: |a|^2 =", norm(a) ** 2, "= |proj|^2 + |resid|^2 =", round(norm(p2) ** 2 + norm(a - p2) ** 2, 10))
```
```text
projection of [3, 4] onto the x axis: [3. 0.] | residual: [0. 4.]
residual . direction = 0.0 (zero: orthogonal)

projection onto [1, 1]: [3.5 3.5] | residual: [-0.5  0.5] | dot: 0.0
Pythagoras: |a|^2 = 25.0 = |proj|^2 + |resid|^2 = 25.0
```

Projection is not an exotic idea: it is **least squares**. Fitting a line to data means projecting the vector of outcomes onto the space spanned by the predictors, and the residuals are what is left, orthogonal to every predictor. Keep this picture; it returns in ds.02 and explains why residuals sum to zero.

## 2. Matrices

### 2.1 A table of numbers, and a machine

A **matrix** is a rectangular table of numbers. Two readings are both useful:

- **As data**: a matrix with *n* rows and *p* columns holds *n* observations of *p* features. This is the `X` of machine learning.
- **As a machine** (a **linear map**): a matrix takes a vector in and sends a vector out. It can rotate, stretch, shear, squash or project.

```python run
X = np.array([[1.0, 2.0, 3.0],
              [4.0, 5.0, 6.0]])
print("X:\n", X)
print("shape:", X.shape, "| rows:", X.shape[0], "| columns:", X.shape[1])
print("transpose X.T shape:", X.T.shape)
print("X.T:\n", X.T)
```
```text
X:
 [[1. 2. 3.]
 [4. 5. 6.]]
shape: (2, 3) | rows: 2 | columns: 3
transpose X.T shape: (3, 2)
X.T:
 [[1. 4.]
 [2. 5.]
 [3. 6.]]
```

The **transpose** swaps rows and columns. A vector times a matrix is the first machine reading:

```python run
A = np.array([[2.0, 0.0],
              [0.0, 3.0]])              # stretch x by 2 and y by 3
v = np.array([1.0, 1.0])
print("A @ v =", A @ v)

theta = math.radians(90)
Rot = np.array([[math.cos(theta), -math.sin(theta)],
                [math.sin(theta),  math.cos(theta)]])
print("rotate [1, 0] by 90 degrees:", np.round(Rot @ np.array([1.0, 0.0]), 10))
print("rotation preserves length:", norm(Rot @ np.array([3.0, 4.0])))
```
```text
A @ v = [2. 3.]
rotate [1, 0] by 90 degrees: [0. 1.]
rotation preserves length: 5.0
```

### 2.2 The matrix product, three ways

If `A` has shape `(m, n)` and `B` has shape `(n, p)`, then `A @ B` has shape `(m, p)`: the **inner dimensions must match** and disappear. Every entry is a dot product:

`(AB)[i, j] = (row i of A) · (column j of B)`

```python run
A = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])      # (3, 2)
B = np.array([[1.0, 0.0, 2.0], [0.0, 1.0, 3.0]])        # (2, 3)

def matmul(A, B):
    m, n = A.shape
    n2, p = B.shape
    if n != n2:
        raise ValueError(f"shapes {A.shape} and {B.shape}: inner dimensions {n} and {n2} differ")
    C = np.zeros((m, p))
    for i in range(m):
        for j in range(p):
            C[i, j] = sum(A[i, k] * B[k, j] for k in range(n))
    return C


C = matmul(A, B)
print("our loops:\n", C)
print("A @ B equal:", np.allclose(C, A @ B), "| shape:", (A @ B).shape)
try:
    matmul(A, A)
except ValueError as e:
    print("error:", e)
print("B @ A shape:", (B @ A).shape, "-> A @ B and B @ A are different matrices (even different shapes)")
```
```text
our loops:
 [[ 1.  2.  8.]
 [ 3.  4. 18.]
 [ 5.  6. 28.]]
A @ B equal: True | shape: (3, 3)
error: shapes (3, 2) and (3, 2): inner dimensions 2 and 3 differ
B @ A shape: (2, 2) -> A @ B and B @ A are different matrices (even different shapes)
```

Two further readings of the same product are worth knowing: each **column** of `AB` is `A` applied to a column of `B`; and `AB` is a **sum of outer products** (column k of A times row k of B). The first one explains why a matrix applied to many vectors at once is just a matrix product. The loops above are for understanding only: `@` calls optimised code that is typically hundreds of times faster.

```python run
rng = np.random.default_rng(0)
M1, M2 = rng.normal(size=(120, 120)), rng.normal(size=(120, 120))
t0 = time.perf_counter(); r_loop = matmul(M1, M2); t_loop = time.perf_counter() - t0
t0 = time.perf_counter(); r_np = M1 @ M2; t_np = time.perf_counter() - t0
print("same result:", np.allclose(r_loop, r_np))
print(f"loops {t_loop * 1000:.0f} ms | numpy {t_np * 1000:.2f} ms | ratio about {t_loop / t_np:,.0f}x (machine-specific)")
```
```text
same result: True
loops 327 ms | numpy 0.29 ms | ratio about 1,140x (machine-specific)
```

Three rules to remember: the product is **associative** `(AB)C = A(BC)`, **distributive** `A(B + C) = AB + AC`, and **not commutative** (`AB` is usually not `BA`). And `(AB)ᵀ = BᵀAᵀ`: the transpose reverses the order.

```python run
P, Q = rng.normal(size=(3, 4)), rng.normal(size=(4, 2))
print("(PQ)^T == Q^T P^T:", np.allclose((P @ Q).T, Q.T @ P.T))
S, T = rng.normal(size=(3, 3)), rng.normal(size=(3, 3))
print("ST == TS:", np.allclose(S @ T, T @ S), "(almost never)")
```
```text
(PQ)^T == Q^T P^T: True
ST == TS: False (almost never)
```

### 2.3 The identity, the diagonal and the symmetric matrix

- The **identity** `I` has ones on the diagonal and zeros elsewhere: `I v = v`. It does nothing.
- A **diagonal** matrix scales each axis separately.
- A **symmetric** matrix equals its transpose. Covariance matrices, `XᵀX` and many others are symmetric, and symmetric matrices have the best behaviour of all (section 4).

```python run
I3 = np.eye(3)
M = rng.normal(size=(3, 3))
print("I M == M:", np.allclose(I3 @ M, M), "| M I == M:", np.allclose(M @ I3, M))

Xd = rng.normal(size=(50, 3))
G = Xd.T @ Xd                                  # (3, 50) @ (50, 3) -> (3, 3)
print("X^T X shape:", G.shape, "| symmetric:", np.allclose(G, G.T))
print("diag(2, 3, 4):\n", np.diag([2.0, 3.0, 4.0]))
```
```text
I M == M: True | M I == M: True
X^T X shape: (3, 3) | symmetric: True
diag(2, 3, 4):
 [[2. 0. 0.]
 [0. 3. 0.]
 [0. 0. 4.]]
```

### 2.4 Data as a matrix: the covariance matrix

The matrix `X` (n observations, p features) becomes useful when we compute things from it. Centre each column (subtract its mean), call the result `Xc`; then 

`Cov = Xcᵀ Xc / (n − 1)` 

is the **covariance matrix**: a symmetric `p × p` table whose diagonal holds the variances and whose off-diagonal entries hold the covariances. Dividing each covariance by the two standard deviations gives the **correlation matrix**.

```python run
rng = np.random.default_rng(1)
n = 500
height = rng.normal(170, 8, n)
weight = 0.9 * (height - 170) + rng.normal(70, 6, n)
shoe = 0.25 * (height - 170) + rng.normal(41, 1.5, n)
X = np.column_stack([height, weight, shoe])

Xc = X - X.mean(axis=0)
cov = Xc.T @ Xc / (len(X) - 1)
print("covariance:\n", cov)
print("equals np.cov:", np.allclose(cov, np.cov(X, rowvar=False)))
sd = np.sqrt(np.diag(cov))
corr = cov / np.outer(sd, sd)
print("\ncorrelation:\n", corr)
print("equals np.corrcoef:", np.allclose(corr, np.corrcoef(X, rowvar=False)))
```
```text
covariance:
 [[53.4496 48.0839 13.7424]
 [48.0839 83.3424 13.2378]
 [13.7424 13.2378  6.0138]]
equals np.cov: True

correlation:
 [[1.     0.7204 0.7665]
 [0.7204 1.     0.5913]
 [0.7665 0.5913 1.    ]]
equals np.corrcoef: True
```

`rowvar=False` tells NumPy that columns are the variables, the usual layout in data science (`np.cov` defaults to the opposite). Forgetting it returns an `n × n` matrix, one of the classic silent shape errors.

## 3. Solving linear systems, rank and inverses

### 3.1 The problem behind linear regression

Most of data science reduces to one question: **find `x` such that `A x = b`**. A concrete case: three unknown prices and three shopping bills.

```python run
# 2 apples + 1 banana + 1 cherry = 9 ; 1 apple + 3 bananas + 2 cherries = 13 ; 1 apple + 1 banana + 4 cherries = 14
A = np.array([[2.0, 1.0, 1.0], [1.0, 3.0, 2.0], [1.0, 1.0, 4.0]])
b = np.array([9.0, 13.0, 14.0])
x = np.linalg.solve(A, b)
print("prices:", x, "| check A @ x == b:", np.allclose(A @ x, b))
```
```text
prices: [2.3125 1.9375 2.4375] | check A @ x == b: True
```

`np.linalg.solve` uses an elimination method (LU decomposition) that is both fast and numerically careful. Writing it by hand once shows what it does.

```python run
def gaussian_solve(A, b):
    """Solve A x = b by Gaussian elimination with partial pivoting."""
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    for col in range(n):
        pivot = col + int(np.argmax(np.abs(A[col:, col])))           # largest entry in this column: the stable choice
        if abs(A[pivot, col]) < 1e-12:
            raise np.linalg.LinAlgError("matrix is singular (no unique solution)")
        A[[col, pivot]], b[[col, pivot]] = A[[pivot, col]].copy(), b[[pivot, col]].copy()
        for row in range(col + 1, n):
            f = A[row, col] / A[col, col]
            A[row, col:] -= f * A[col, col:]
            b[row] -= f * b[col]
    x = np.zeros(n)
    for row in range(n - 1, -1, -1):                                  # back-substitution
        x[row] = (b[row] - A[row, row + 1:] @ x[row + 1:]) / A[row, row]
    return x


print("ours  :", gaussian_solve(A, b))
print("numpy :", np.linalg.solve(A, b))
```
```text
ours  : [2.3125 1.9375 2.4375]
numpy : [2.3125 1.9375 2.4375]
```

### 3.2 When there is no unique solution: rank and singular matrices

The **rank** of a matrix is the number of **independent** directions in it: how many of its columns cannot be built from the others. A square matrix of full rank is **invertible** and `A x = b` has exactly one solution. If one column is a combination of the others, the matrix is **singular**: it squashes space flat in one direction, information is lost, and there is either no solution or infinitely many.

```python run
# a third column that is just column1 + column2: no new information
S = np.array([[1.0, 2.0, 3.0], [2.0, 1.0, 3.0], [3.0, 4.0, 7.0]])
print("rank of the earlier A:", np.linalg.matrix_rank(A), "(full: 3)")
print("rank of S            :", np.linalg.matrix_rank(S), "(only 2 independent columns)")
print("determinant of A     :", round(float(np.linalg.det(A)), 6))
print("determinant of S     :", round(float(np.linalg.det(S)), 10), "(zero, up to rounding: singular)")
try:
    np.linalg.solve(S, np.array([1.0, 2.0, 3.0]))
except np.linalg.LinAlgError as e:
    print("solve(S, ...) ->", type(e).__name__ + ":", e)
```
```text
rank of the earlier A: 3 (full: 3)
rank of S            : 2 (only 2 independent columns)
determinant of A     : 16.0
determinant of S     : 0.0 (zero, up to rounding: singular)
```

This is not a curiosity; it is the **multicollinearity** of regression. If one feature is (nearly) a linear combination of others, the matrix `XᵀX` is (nearly) singular and the coefficients are unstable or undefined. It is also why we drop one dummy column when one-hot encoding with an intercept.

### 3.3 The condition number: nearly singular is nearly as bad

Real data are never exactly singular, but they can be nearly so, and then rounding errors are magnified. The **condition number** measures that magnification: roughly, how many digits of accuracy you lose when solving.

```python run
def make_near_singular(eps):
    return np.array([[1.0, 1.0], [1.0, 1.0 + eps]])


b2 = np.array([2.0, 2.0 + 1e-10])
for eps in (1.0, 1e-4, 1e-8, 1e-12):
    M = make_near_singular(eps)
    xs = np.linalg.solve(M, b2)
    print(f"eps = {eps:7.0e} | condition number = {np.linalg.cond(M):10.3e} | solution = {xs}")
```
```text
eps =   1e+00 | condition number =  6.854e+00 | solution = [2. 0.]
eps =   1e-04 | condition number =  4.000e+04 | solution = [2. 0.]
eps =   1e-08 | condition number =  4.000e+08 | solution = [1.99 0.01]
eps =   1e-12 | condition number =  3.999e+12 | solution = [-97.9911  99.9911]
```

As the second column approaches the first, the condition number explodes and the solution for the *same* right-hand side moves from a calm answer to nonsense. Rule of thumb: a condition number of 10^k costs about k digits. Above 10^8 or so with double precision (16 digits), the coefficients should not be trusted. In ds.02, `statsmodels` prints a warning when `XᵀX` is ill-conditioned for exactly this reason.

### 3.4 The inverse (and why you almost never compute it)

The **inverse** `A⁻¹` satisfies `A⁻¹ A = I`. The solution of `A x = b` is `x = A⁻¹ b`, which is how it is written in textbooks. In code, use `solve`: it is faster and more accurate than forming the inverse and multiplying.

```python run
rng = np.random.default_rng(2)
n = 600
Abig = rng.normal(size=(n, n))
bbig = rng.normal(size=n)

def best_of(f, reps=5):
    times = []
    for _ in range(reps):
        t0 = time.perf_counter(); out = f(); times.append(time.perf_counter() - t0)
    return out, min(times)


x1, t_solve = best_of(lambda: np.linalg.solve(Abig, bbig))
x2, t_inv = best_of(lambda: np.linalg.inv(Abig) @ bbig)
print("residual |A x - b|, solve:", float(np.linalg.norm(Abig @ x1 - bbig)))
print("residual |A x - b|, inv  :", float(np.linalg.norm(Abig @ x2 - bbig)))
print(f"time solve {t_solve * 1000:.0f} ms | inv then multiply {t_inv * 1000:.0f} ms (machine-specific)")
```
```text
residual |A x - b|, solve: 2.638792594580459e-12
residual |A x - b|, inv  : 6.592829141264477e-12
time solve 2 ms | inv then multiply 9 ms (machine-specific)
```

### 3.5 Least squares: when there are more equations than unknowns

In data science there are almost always more rows than unknowns (n observations, p coefficients), and no exact solution exists because of noise. The aim becomes: find the `x` that makes `A x` as close as possible to `b`, minimising the sum of squared errors `‖A x − b‖²`. The answer comes from the **normal equations**:

`AᵀA x = Aᵀb`

Geometrically (section 1.5), `A x` is the projection of `b` onto the columns of `A`, and the residual is orthogonal to every column.

```python run
rng = np.random.default_rng(3)
n = 200
hours = rng.uniform(0, 10, n)
marks = 35 + 5.0 * hours + rng.normal(0, 4, n)
A_ls = np.column_stack([np.ones(n), hours])                 # intercept column and the feature

x_normal = np.linalg.solve(A_ls.T @ A_ls, A_ls.T @ marks)    # the normal equations
x_lstsq = np.linalg.lstsq(A_ls, marks, rcond=None)[0]        # numpy's stable method
print("normal equations:", x_normal)
print("np.linalg.lstsq :", x_lstsq, "(true values: 35 and 5)")
resid = marks - A_ls @ x_normal
print("A^T residual (should be ~ 0):", A_ls.T @ resid)
print("the residuals sum to zero because the intercept column is in A:", round(float(resid.sum()), 10))
```
```text
normal equations: [35.4149  4.941 ]
np.linalg.lstsq : [35.4149  4.941 ] (true values: 35 and 5)
A^T residual (should be ~ 0): [-0. -0.]
the residuals sum to zero because the intercept column is in A: -0.0
```

This is linear regression in four lines, and the picture of projection is the reason the residuals are orthogonal to the predictors. (`lstsq` is preferred in practice: it uses the SVD of section 5 and avoids squaring the condition number as `AᵀA` does.)

```python run
Xill = np.column_stack([np.ones(n), hours, hours + rng.normal(0, 1e-6, n)])     # a nearly duplicate column
print("cond(A) =", f"{np.linalg.cond(Xill):.2e}", "| cond(A^T A) =", f"{np.linalg.cond(Xill.T @ Xill):.2e}", "(the square: digits lost twice)")
```
```text
cond(A) = 1.21e+07 | cond(A^T A) = 1.43e+14 (the square: digits lost twice)
```

## 4. Eigenvalues and eigenvectors

### 4.1 The directions a matrix does not turn

Most vectors change direction when a matrix acts on them. An **eigenvector** of a square matrix `A` is a special direction that is only **stretched**, not turned: `A v = λ v`. The stretch factor `λ` is the **eigenvalue**.

```python run
A = np.array([[2.0, 1.0], [1.0, 2.0]])
vals, vecs = np.linalg.eig(A)
print("dtype returned by eig:", vals.dtype, "(complex, because a general matrix may have complex eigenvalues)")
assert np.allclose(vals.imag, 0)                     # ours are real, so keep the real parts
vals, vecs = vals.real, vecs.real
print("eigenvalues :", vals)
print("eigenvectors (columns):\n", vecs)
for lam, v in zip(vals, vecs.T):
    print(f"A v = {A @ v}  and  lambda v = {lam * v}  -> equal: {np.allclose(A @ v, lam * v)}")
```
```text
dtype returned by eig: complex128 (complex, because a general matrix may have complex eigenvalues)
eigenvalues : [3. 1.]
eigenvectors (columns):
 [[ 0.7071 -0.7071]
 [ 0.7071  0.7071]]
A v = [2.1213 2.1213]  and  lambda v = [2.1213 2.1213]  -> equal: True
A v = [-0.7071  0.7071]  and  lambda v = [-0.7071  0.7071]  -> equal: True
```

For this matrix, the direction `[1, 1]` is stretched by 3 and `[1, −1]` by 1. Every other vector is a mix of these two and is bent towards the first. Two quick facts: the **trace** (sum of the diagonal) equals the **sum of the eigenvalues**, and the **determinant** equals their **product**.

```python run
print("trace", np.trace(A), "= sum of eigenvalues", vals.sum())
print("det  ", round(float(np.linalg.det(A)), 10), "= product of eigenvalues", round(float(vals.prod()), 10))
```
```text
trace 4.0 = sum of eigenvalues 4.0
det   3.0 = product of eigenvalues 3.0
```

### 4.2 Finding the biggest one: power iteration

How are eigenvalues computed? Real libraries use sophisticated algorithms, but the main idea fits in five lines. Apply `A` again and again to almost any starting vector, rescaling each time. Each application stretches the component along the strongest eigenvector most, so the vector turns towards it.

```python run
def power_iteration(A, steps=100, seed=0):
    v = np.random.default_rng(seed).normal(size=A.shape[0])
    v /= np.linalg.norm(v)
    history = []
    for _ in range(steps):
        w = A @ v
        v = w / np.linalg.norm(w)
        history.append(float(v @ A @ v))                 # the Rayleigh quotient estimates the eigenvalue
    return history[-1], v, history


lam, v, hist = power_iteration(A, steps=12)
print("estimates by step:", [round(h, 6) for h in hist[:6]], "...")
print("final eigenvalue :", round(lam, 8), "| numpy's largest:", vals.max())
print("final eigenvector:", v, "(sign is arbitrary: -v is equally valid)")
```
```text
estimates by step: [1.010943, 1.094353, 1.616501, 2.600838, 2.946084, 2.993862] ...
final eigenvalue : 2.99999999 | numpy's largest: 3.0
final eigenvector: [-0.7071 -0.7072] (sign is arbitrary: -v is equally valid)
```

### 4.3 Symmetric matrices: real values, perpendicular directions

For a **symmetric** matrix (covariance matrices, `XᵀX`) three good things always hold: the eigenvalues are real, the eigenvectors are **orthogonal**, and the matrix can be written `A = Q Λ Qᵀ` with `Q` holding the eigenvectors and `Λ` the eigenvalues on its diagonal. For symmetric matrices use `np.linalg.eigh`, which is faster, more accurate and returns the eigenvalues in ascending order.

```python run
rng = np.random.default_rng(4)
B = rng.normal(size=(4, 4))
Sym = B @ B.T                                       # any B B^T is symmetric and positive semi-definite
w, Q = np.linalg.eigh(Sym)
print("eigenvalues (ascending):", w)
print("Q^T Q == I (orthonormal):", np.allclose(Q.T @ Q, np.eye(4)))
print("Q diag(w) Q^T == Sym    :", np.allclose(Q @ np.diag(w) @ Q.T, Sym))
print("all eigenvalues >= 0    :", bool((w > -1e-12).all()), "(B B^T is positive semi-definite)")
```
```text
eigenvalues (ascending): [ 0.012   2.79    6.5843 10.2244]
Q^T Q == I (orthonormal): True
Q diag(w) Q^T == Sym    : True
all eigenvalues >= 0    : True (B B^T is positive semi-definite)
```

### 4.4 Principal components: the eigenvectors of the covariance matrix

Here is why eigenvectors matter in data science. Take the covariance matrix of the height, weight and shoe data of section 2.4. Its **eigenvectors** are the directions along which the data vary most, uncorrelated with each other. Its **eigenvalues** are the variances along those directions. This is **principal component analysis (PCA)**.

```python run
rng = np.random.default_rng(1)
n = 500
height = rng.normal(170, 8, n)
weight = 0.9 * (height - 170) + rng.normal(70, 6, n)
shoe = 0.25 * (height - 170) + rng.normal(41, 1.5, n)
X = np.column_stack([height, weight, shoe])
Xs = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)         # standardise so units do not decide
C = np.cov(Xs, rowvar=False)

w, Q = np.linalg.eigh(C)
order = np.argsort(w)[::-1]                                # largest first
w, Q = w[order], Q[:, order]
print("eigenvalues (variance along each component):", w)
print("share of the total variance:", w / w.sum())
print("first component (loadings on height, weight, shoe):", Q[:, 0])
scores = Xs @ Q                                            # the data in the new coordinates
print("scores are uncorrelated:", np.allclose(np.cov(scores, rowvar=False), np.diag(w)))
```
```text
eigenvalues (variance along each component): [2.3881 0.4117 0.2002]
share of the total variance: [0.796  0.1372 0.0667]
first component (loadings on height, weight, shoe): [-0.6039 -0.5565 -0.5706]
scores are uncorrelated: True
```

The first component is a "general body size" axis that loads on all three columns with the same sign (the overall sign of a component is arbitrary), and it carries the largest share of the variance. If you keep only the first one or two components you compress three columns into fewer with little loss. The trace rule appears again: the eigenvalues of a correlation matrix add up to the number of columns (here 3), because each standardised column has variance 1.

> **Predict the output.** A correlation matrix of 4 standardised columns has eigenvalues that sum to what number? And what do the eigenvalues look like if the 4 columns are completely uncorrelated?

<details><summary>Answer</summary>

```python run
print("sum of eigenvalues for a 4x4 correlation matrix:", np.linalg.eigvalsh(np.corrcoef(rng.normal(size=(300, 4)), rowvar=False)).sum())
print("uncorrelated columns, eigenvalues of the identity:", np.linalg.eigvalsh(np.eye(4)))
```
```text
sum of eigenvalues for a 4x4 correlation matrix: 4.0
uncorrelated columns, eigenvalues of the identity: [1. 1. 1. 1.]
```

The trace of a correlation matrix is the number of columns, so the eigenvalues add up to 4. If the columns are uncorrelated the correlation matrix is the identity, all eigenvalues are 1 and there is nothing to compress: PCA only helps when columns are correlated.

</details>

## 5. The singular value decomposition

### 5.1 Eigenvalues for every matrix

Eigenvalues are defined only for square matrices, and data matrices are rectangular (n rows, p columns). The **singular value decomposition (SVD)** works for any matrix. It writes

`X = U Σ Vᵀ`

where `U` and `V` have orthonormal columns (they are rotations) and `Σ` is diagonal with non-negative **singular values** sorted from large to small. Read it as: rotate, stretch each axis by its singular value, rotate again. Every matrix, however messy, is that simple.

```python run
rng = np.random.default_rng(5)
M = rng.normal(size=(6, 4))
U, s, Vt = np.linalg.svd(M, full_matrices=False)
print("shapes: U", U.shape, "| s", s.shape, "| Vt", Vt.shape)
print("singular values:", s)
print("rebuild  U diag(s) Vt == M:", np.allclose(U @ np.diag(s) @ Vt, M))
print("U^T U == I:", np.allclose(U.T @ U, np.eye(4)), "| V^T V == I:", np.allclose(Vt @ Vt.T, np.eye(4)))
```
```text
shapes: U (6, 4) | s (4,) | Vt (4, 4)
singular values: [3.5822 1.9934 1.5832 0.2375]
rebuild  U diag(s) Vt == M: True
U^T U == I: True | V^T V == I: True
```

### 5.2 The link to eigenvalues

The SVD and the eigendecomposition are the same story. The singular values of `X` are the square roots of the eigenvalues of `XᵀX`, and the columns of `V` are its eigenvectors. For centred data, the eigenvalues of the covariance matrix are `s² / (n − 1)`.

```python run
ev = np.sort(np.linalg.eigvalsh(M.T @ M))[::-1]
print("sqrt(eigenvalues of M^T M):", np.sqrt(ev))
print("singular values           :", s)

Xc = X - X.mean(axis=0)
Uc, sc, Vtc = np.linalg.svd(Xc, full_matrices=False)
print("\nPCA by SVD: variances s^2/(n-1):", sc ** 2 / (len(Xc) - 1))
print("PCA by eigh of the covariance :", np.sort(np.linalg.eigvalsh(np.cov(Xc, rowvar=False)))[::-1])
```
```text
sqrt(eigenvalues of M^T M): [3.5822 1.9934 1.5832 0.2375]
singular values           : [3.5822 1.9934 1.5832 0.2375]

PCA by SVD: variances s^2/(n-1): [121.807   18.6812   2.3175]
PCA by eigh of the covariance : [121.807   18.6812   2.3175]
```

This is how production PCA is done: the SVD of the centred data is more accurate than forming the covariance matrix, and it works even when there are more columns than rows.

### 5.3 Low-rank approximation: compression with a guarantee

Keep only the largest *k* singular values and you get the best possible rank-*k* approximation of the matrix (the **Eckart-Young theorem**: no other matrix of rank *k* is closer in the sum-of-squares sense). The error is exactly the discarded singular values.

We build a "ratings" matrix with a hidden structure: 80 users, 30 items, and only 3 underlying tastes, plus a little noise.

```python run
rng = np.random.default_rng(6)
users, items, k_true = 80, 30, 3
taste_u = rng.normal(size=(users, k_true))
taste_i = rng.normal(size=(items, k_true))
R = taste_u @ taste_i.T + rng.normal(0, 0.3, (users, items))

U, s, Vt = np.linalg.svd(R, full_matrices=False)
print("first 8 singular values:", s[:8])
print("cumulative share of energy (sum of s^2):", np.round(np.cumsum(s ** 2)[:8] / (s ** 2).sum(), 4))


def rank_k(U, s, Vt, k):
    return U[:, :k] @ np.diag(s[:k]) @ Vt[:k]


print("\n k | stored numbers | relative error (Frobenius) | error predicted by dropped s")
for k in (1, 2, 3, 5, 10, 30):
    Rk = rank_k(U, s, Vt, k)
    err = np.linalg.norm(R - Rk) / np.linalg.norm(R)
    pred = math.sqrt(float((s[k:] ** 2).sum())) / math.sqrt(float((s ** 2).sum()))
    stored = k * (users + items + 1)
    print(f"{k:2d} | {stored:14d} | {err:26.4f} | {pred:.4f}")
print("the full matrix stores", R.size, "numbers")
```
```text
first 8 singular values: [54.155  47.5372 43.2946  4.02    3.8191  3.5523  3.4708  3.3254]
cumulative share of energy (sum of s^2): [0.4043 0.7159 0.9743 0.9765 0.9785 0.9803 0.9819 0.9834]

 k | stored numbers | relative error (Frobenius) | error predicted by dropped s
 1 |            111 |                     0.7718 | 0.7718
 2 |            222 |                     0.5330 | 0.5330
 3 |            333 |                     0.1604 | 0.1604
 5 |            555 |                     0.1466 | 0.1466
10 |           1110 |                     0.1167 | 0.1167
30 |           3330 |                     0.0000 | 0.0000
the full matrix stores 2400 numbers
```

The three large singular values are the three hidden tastes; the rest are noise. With *k* = 3 we store a fraction of the numbers and lose almost nothing, and the measured error equals the one predicted from the discarded singular values to all printed digits. This is the idea behind recommender systems, latent semantic analysis, image compression and **noise removal**: the small singular values are mostly noise.

```python run
clean = taste_u @ taste_i.T
for k in (3, 30):
    Rk = rank_k(U, s, Vt, k)
    print(f"rank {k:2d}: distance to the noise-free truth = {np.linalg.norm(Rk - clean):.3f}   (distance of the noisy data itself: {np.linalg.norm(R - clean):.3f})")
```
```text
rank  3: distance to the noise-free truth = 5.529   (distance of the noisy data itself: 14.733)
rank 30: distance to the noise-free truth = 14.733   (distance of the noisy data itself: 14.733)
```

The rank-3 reconstruction is **closer to the truth than the data we were given**: truncating the SVD removed noise, not signal.

### 5.4 The pseudo-inverse

For a singular or rectangular matrix there is no inverse, but the SVD gives the best substitute, the **pseudo-inverse** `A⁺ = V Σ⁺ Uᵀ`, where `Σ⁺` inverts the non-zero singular values and leaves zeros alone. It solves least squares even when `AᵀA` is singular, returning the solution of **smallest norm**.

```python run
A_ls = np.column_stack([np.ones(10), np.arange(10.0), 2 * np.arange(10.0)])         # third column = 2 x second: rank 2
y_ls = 3 + 0.5 * np.arange(10.0)
print("rank:", np.linalg.matrix_rank(A_ls), "| cond(A^T A) is huge or infinite:", np.linalg.cond(A_ls.T @ A_ls))
x_pinv = np.linalg.pinv(A_ls) @ y_ls
print("pinv solution:", x_pinv, "| fit is exact:", np.allclose(A_ls @ x_pinv, y_ls))

U, s, Vt = np.linalg.svd(A_ls, full_matrices=False)
s_inv = np.where(s > 1e-10 * s.max(), 1 / np.where(s == 0, 1, s), 0.0)
print("by hand      :", (Vt.T * s_inv) @ (U.T @ y_ls))
```
```text
rank: 2 | cond(A^T A) is huge or infinite: 1.815427339095446e+33
pinv solution: [3.  0.1 0.2] | fit is exact: True
by hand      : [3.  0.1 0.2]
```

The two columns that duplicate each other share the slope between them: 0.1 on the first and 0.2 on the second (the second column is twice the first, so 0.1 + 2 x 0.2 = 0.5, the true slope), and the solution is the shortest of the infinitely many that fit. `lstsq` returns exactly this, which is why it does not crash on collinear data, while the normal equations do.


## 6. Derivatives

### 6.1 The slope at a point

A **derivative** answers one question: *if I nudge the input a tiny bit, how much does the output move?* For a function `f(x)` the derivative `f'(x)` is the slope of the curve at `x`. It is defined as a limit:

`f'(x) = lim (f(x + h) − f(x)) / h` as `h → 0`

We can compute that quotient with a small `h` and see it settle. Take `f(x) = x²`, whose derivative at `x = 3` we expect to be 6 (the rule is `d/dx x² = 2x`).

```python run
def f(x):
    return x ** 2


x0 = 3.0
print("   h        (f(x+h) - f(x)) / h     error from 6")
for h in (1.0, 0.1, 0.01, 0.001, 1e-6):
    q = (f(x0 + h) - f(x0)) / h
    print(f"{h:8.0e}   {q:18.8f}   {abs(q - 6):14.2e}")
```
```text
   h        (f(x+h) - f(x)) / h     error from 6
   1e+00           7.00000000         1.00e+00
   1e-01           6.10000000         1.00e-01
   1e-02           6.01000000         1.00e-02
   1e-03           6.00100000         1.00e-03
   1e-06           6.00000100         1.00e-06
```

As `h` shrinks, the quotient approaches 6. The derivative is what the quotient is heading towards.

### 6.2 A numerical derivative, and the step-size trap

A numerical derivative is the tool we will use all chapter to **check our hand-derived formulas**. Two forms: the **forward difference** above, and the more accurate **central difference** `(f(x+h) − f(x−h)) / 2h`, which cancels the first error term.

```python run
def num_deriv(f, x, h=1e-5):
    """Central difference: error shrinks like h^2."""
    return (f(x + h) - f(x - h)) / (2 * h)


print("error of forward vs central difference for f = exp at x = 1 (true derivative = e):")
print("      h         forward error     central error")
for h in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
    fwd = (math.exp(1 + h) - math.exp(1)) / h
    ctr = num_deriv(math.exp, 1.0, h)
    print(f"  {h:8.0e}   {abs(fwd - math.e):14.2e}   {abs(ctr - math.e):14.2e}")
```
```text
error of forward vs central difference for f = exp at x = 1 (true derivative = e):
      h         forward error     central error
     1e-01         1.41e-01         4.53e-03
     1e-02         1.36e-02         4.53e-05
     1e-03         1.36e-03         4.53e-07
     1e-04         1.36e-04         4.53e-09
     1e-05         1.36e-05         5.86e-11
```

The central difference is far more accurate for the same `h`. But do not make `h` as small as possible: two nearly equal numbers are subtracted, and **rounding error** grows as `h` shrinks.

```python run
print("      h      central-difference error (f = exp at 1)")
for h in (1e-3, 1e-5, 1e-7, 1e-9, 1e-11, 1e-13):
    print(f"  {h:8.0e}   {abs(num_deriv(math.exp, 1.0, h) - math.e):12.2e}")
```
```text
      h      central-difference error (f = exp at 1)
     1e-03       4.53e-07
     1e-05       5.86e-11
     1e-07       5.86e-11
     1e-09       6.60e-09
     1e-11       1.04e-05
     1e-13       4.56e-04
```

The error first falls (the formula improves) and then rises again (the arithmetic fails): a **sweet spot** between `h = 1e-5` and `1e-7` for central differences in double precision (the error there is about 6e-11). Remember this when a gradient check "fails" - the check itself has an error budget.

### 6.3 The rules you need

You never differentiate from the limit; you use rules. The few below cover everything in this course (and every neural network).

| Function | Derivative | Note |
|---|---|---|
| constant `c` | 0 | |
| `xⁿ` | `n xⁿ⁻¹` | power rule |
| `eˣ` | `eˣ` | the function that is its own slope |
| `ln x` | `1/x` | |
| `sin x`, `cos x` | `cos x`, `−sin x` | |
| `f + g` | `f' + g'` | sum rule |
| `c f` | `c f'` | constant factor |
| `f g` | `f' g + f g'` | product rule |
| `f(g(x))` | `f'(g(x)) · g'(x)` | **chain rule** |

The **chain rule** is the most important of all: it says how a nudge passes through a chain of functions, multiplying the slopes along the way. Backpropagation in a neural network is the chain rule applied systematically. Verify the rules numerically:

```python run
checks = {
    "x^3 at 2          (3x^2 = 12)":            (lambda x: x ** 3, lambda x: 3 * x ** 2, 2.0),
    "exp(2x) at 0.5    (2 exp(2x))":            (lambda x: math.exp(2 * x), lambda x: 2 * math.exp(2 * x), 0.5),
    "ln(x) at 4        (1/x)":                  (math.log, lambda x: 1 / x, 4.0),
    "x sin(x) at 1.3   (sin x + x cos x)":      (lambda x: x * math.sin(x), lambda x: math.sin(x) + x * math.cos(x), 1.3),
    "sin(x^2) at 0.7   (cos(x^2) * 2x)":        (lambda x: math.sin(x ** 2), lambda x: math.cos(x ** 2) * 2 * x, 0.7),
    "1/(1+exp(-x)) at 0.4 (s(1-s))":            (lambda x: 1 / (1 + math.exp(-x)), lambda x: (1 / (1 + math.exp(-x))) * (1 - 1 / (1 + math.exp(-x))), 0.4),
}
for name, (fn, dfn, x) in checks.items():
    num, exact = num_deriv(fn, x), dfn(x)
    print(f"{name:42} formula {exact:10.6f} | numerical {num:10.6f} | agree: {abs(num - exact) < 1e-6}")
```
```text
x^3 at 2          (3x^2 = 12)              formula  12.000000 | numerical  12.000000 | agree: True
exp(2x) at 0.5    (2 exp(2x))              formula   5.436564 | numerical   5.436564 | agree: True
ln(x) at 4        (1/x)                    formula   0.250000 | numerical   0.250000 | agree: True
x sin(x) at 1.3   (sin x + x cos x)        formula   1.311307 | numerical   1.311307 | agree: True
sin(x^2) at 0.7   (cos(x^2) * 2x)          formula   1.235266 | numerical   1.235266 | agree: True
1/(1+exp(-x)) at 0.4 (s(1-s))              formula   0.240261 | numerical   0.240261 | agree: True
```

The last function is the **sigmoid** `σ(x) = 1 / (1 + e⁻ˣ)`, the heart of logistic regression. Its derivative has the beautiful form `σ(x)(1 − σ(x))`, which you can derive with the chain rule and check numerically as above.

> **Predict the output.** Using the chain rule, what is the derivative of `(3x + 1)⁴` at `x = 1`? Check it numerically.

<details><summary>Answer</summary>

```python run
print("chain rule:", 4 * (3 * 1 + 1) ** 3 * 3, "| numerical:", round(num_deriv(lambda x: (3 * x + 1) ** 4, 1.0), 4))
```
```text
chain rule: 768 | numerical: 768.0
```

The outer function is `u⁴` with derivative `4u³`; the inner is `3x + 1` with derivative 3. At `x = 1`, `u = 4`, so the result is `4 · 4³ · 3 = 768`.

</details>

### 6.4 Where the slope is zero: minima and maxima

At the lowest point of a smooth curve the slope is zero. That is how we find the best value of a parameter: write the error as a function of the parameter, set the derivative to zero and solve. Consider the mean of a sample. Which single number `m` is closest to all of the data, in the sense of the smallest sum of squared distances `L(m) = Σ (xᵢ − m)²`?

`L'(m) = −2 Σ (xᵢ − m) = 0`  gives  `m = (Σ xᵢ) / n`

The mean is the minimiser of the squared error. We confirm it by scanning.

```python run
data = np.array([2.0, 3.0, 5.0, 10.0, 20.0])
grid = np.linspace(0, 25, 2501)
loss_sq = np.array([np.sum((data - m) ** 2) for m in grid])
loss_abs = np.array([np.sum(np.abs(data - m)) for m in grid])
print("data:", data)
print("minimiser of squared error :", grid[loss_sq.argmin()], "| mean:", data.mean())
print("minimiser of absolute error:", grid[loss_abs.argmin()], "| median:", np.median(data))
```
```text
data: [ 2.  3.  5. 10. 20.]
minimiser of squared error : 8.0 | mean: 8.0
minimiser of absolute error: 5.0 | median: 5.0
```

Squared error gives the mean; absolute error gives the **median**. This is not trivia: it explains why a squared-error model is pulled by outliers (the mean is) while an absolute-error model resists them (the median does), and it is the first hint of why the choice of loss function is a modelling decision.

### 6.5 The second derivative: bending

The derivative of the derivative, `f''(x)`, measures **curvature**. Positive: the curve bends up (a bowl, so a zero slope is a minimum). Negative: it bends down (a hill). It decides how fast gradient descent can go (section 8) and, in several dimensions, becomes the **Hessian** matrix whose eigenvalues (section 4) describe the shape of the bowl.

```python run
def second_deriv(f, x, h=1e-4):
    return (f(x + h) - 2 * f(x) + f(x - h)) / h ** 2


for name, fn, x in (("x^2 (always 2)", lambda x: x ** 2, 1.0), ("x^3 at 2 (6x = 12)", lambda x: x ** 3, 2.0), ("-x^2 (always -2)", lambda x: -x ** 2, 5.0)):
    print(f"{name:20} f'' = {second_deriv(fn, x):9.4f}")
```
```text
x^2 (always 2)       f'' =    2.0000
x^3 at 2 (6x = 12)   f'' =   12.0000
-x^2 (always -2)     f'' =   -2.0000
```

## 7. Partial derivatives and gradients

### 7.1 Many inputs, one slope per input

A model has many parameters: a regression with three coefficients has a loss `L(w₁, w₂, w₃)`. The **partial derivative** `∂L/∂wⱼ` is the slope along one parameter while the others are held fixed. You compute it exactly as before, treating the others as constants.

For `f(x, y) = x² y + 3y`:

- `∂f/∂x = 2xy` (treat `y` as a constant)
- `∂f/∂y = x² + 3` (treat `x` as a constant)

The **gradient** collects all the partial derivatives into one vector:

`∇f = [∂f/∂x, ∂f/∂y]`

It points in the direction of **steepest ascent**, and its length is the slope in that direction. To go downhill, go against it.

```python run
def f2(p):
    x, y = p
    return x ** 2 * y + 3 * y


def grad_f2(p):                                  # by hand
    x, y = p
    return np.array([2 * x * y, x ** 2 + 3])


def num_grad(f, p, h=1e-5):
    """Numerical gradient: a central difference along each coordinate in turn."""
    p = np.asarray(p, dtype=float)
    g = np.zeros_like(p)
    for i in range(len(p)):
        step = np.zeros_like(p)
        step[i] = h
        g[i] = (f(p + step) - f(p - step)) / (2 * h)
    return g


pt = np.array([2.0, 3.0])
print("by hand  :", grad_f2(pt))
print("numerical:", num_grad(f2, pt))
print("agree    :", np.allclose(grad_f2(pt), num_grad(f2, pt), atol=1e-6))
```
```text
by hand  : [12.  7.]
numerical: [12.  7.]
agree    : True
```

### 7.2 The gradient points uphill

A statement worth testing rather than trusting: take a small step in the direction of the gradient and the function should rise the most; in the opposite direction, fall the most; perpendicular, hardly change.

```python run
g = grad_f2(pt)
ghat = g / np.linalg.norm(g)
perp = np.array([-ghat[1], ghat[0]])
eps = 1e-3
print("f at the point                    :", f2(pt))
print("step along the gradient           : change", round(f2(pt + eps * ghat) - f2(pt), 6))
print("step against the gradient         : change", round(f2(pt - eps * ghat) - f2(pt), 6))
print("step perpendicular to the gradient: change", round(f2(pt + eps * perp) - f2(pt), 8))
print("gradient length (steepest slope)  :", round(float(np.linalg.norm(g)), 4), "-> change per unit step along it:", round((f2(pt + eps * ghat) - f2(pt)) / eps, 4))
print("random directions never beat it   :", max((f2(pt + eps * (u / np.linalg.norm(u))) - f2(pt)) for u in np.random.default_rng(0).normal(size=(1000, 2))) <= f2(pt + eps * ghat) - f2(pt) + 1e-12)
```
```text
f at the point                    : 21.0
step along the gradient           : change 0.013896
step against the gradient         : change -0.013888
step perpendicular to the gradient: change -9.8e-07
gradient length (steepest slope)  : 13.8924 -> change per unit step along it: 13.8964
random directions never beat it   : True
```

### 7.3 The gradient of a loss: linear regression by hand

Now a real gradient. A linear model predicts `ŷ = X w`. Its **mean squared error** (MSE) is

`L(w) = (1/n) Σ (ŷᵢ − yᵢ)² = (1/n) ‖X w − y‖²`

Differentiate with the chain rule. For one coefficient: `∂L/∂wⱼ = (2/n) Σ (ŷᵢ − yᵢ) Xᵢⱼ`. Stacked for all coefficients this is one matrix expression:

`∇L = (2/n) Xᵀ (X w − y)`

Read it: "the residuals, projected back onto each feature". It is zero exactly when the residual is orthogonal to every column of `X`, which is the normal equation of section 3.5. The same formula, derived two ways. Check it numerically on random data:

```python run
rng = np.random.default_rng(7)
n, p = 100, 3
Xr = np.column_stack([np.ones(n), rng.normal(size=(n, p - 1))])
true_w = np.array([2.0, -1.0, 0.5])
yr = Xr @ true_w + rng.normal(0, 0.3, n)


def mse(w):
    r = Xr @ w - yr
    return float(r @ r) / n


def mse_grad(w):
    return 2.0 / n * Xr.T @ (Xr @ w - yr)


w_test = np.array([0.5, 0.5, 0.5])
print("analytic gradient :", mse_grad(w_test))
print("numerical gradient:", num_grad(mse, w_test))
print("max abs difference:", float(np.abs(mse_grad(w_test) - num_grad(mse, w_test)).max()))
```
```text
analytic gradient : [-3.3702  2.8889  0.3711]
numerical gradient: [-3.3702  2.8889  0.3711]
max abs difference: 4.1317615995239976e-11
```

### 7.4 The gradient check: a habit for life

Computing a gradient by hand is error-prone: a missing factor of 2, a wrong sign, a transposed matrix. The cure is the **gradient check**: compare the formula with the numerical gradient and measure the relative error. Professionals do this for every new loss function. It catches bugs that no amount of staring finds, because a wrong gradient does not crash: the training simply stalls or wanders.

```python run
def grad_check(f, grad, p, h=1e-5):
    a, n_ = np.asarray(grad(p), float), num_grad(f, p, h)
    rel = float(np.linalg.norm(a - n_) / max(np.linalg.norm(a) + np.linalg.norm(n_), 1e-12))
    return rel


good = lambda w: 2.0 / n * Xr.T @ (Xr @ w - yr)
bug_factor = lambda w: 1.0 / n * Xr.T @ (Xr @ w - yr)               # forgot the 2 from the square
bug_sign = lambda w: -2.0 / n * Xr.T @ (Xr @ w - yr)                 # wrong sign
bug_transpose = lambda w: 2.0 / n * Xr.T @ (yr - Xr @ w) + 0.3 * w   # a stray extra term

for name, g_ in (("correct", good), ("missing factor 2", bug_factor), ("wrong sign", bug_sign), ("stray term", bug_transpose)):
    rel = grad_check(mse, g_, w_test)
    verdict = "OK" if rel < 1e-6 else "BUG"
    print(f"{name:18} relative error = {rel:10.2e}  -> {verdict}")
```
```text
correct            relative error =   5.35e-12  -> OK
missing factor 2   relative error =   3.33e-01  -> BUG
wrong sign         relative error =   1.00e+00  -> BUG
stray term         relative error =   1.00e+00  -> BUG
```

The rule of thumb: relative error below about `1e-6` means the gradient is right; above `1e-3` almost certainly a bug. In between, change `h` and look again.

### 7.5 The chain rule in many dimensions: logistic regression

The loss of **logistic regression** for labels `y ∈ {0, 1}` is the **cross-entropy**. With `z = X w` and the prediction `p = σ(z)`,

`L(w) = −(1/n) Σ [ yᵢ ln pᵢ + (1 − yᵢ) ln(1 − pᵢ) ]`

The chain rule runs through three links: the loss in `p`, `p` in `z` (the sigmoid derivative `p(1 − p)`) and `z` in `w`. The factors `p(1 − p)` cancel against the denominators and leave a result of striking simplicity:

`∇L = (1/n) Xᵀ (p − y)`

The same shape as the regression gradient: "prediction minus truth, projected back onto the features". Check it:

```python run
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


rng = np.random.default_rng(8)
n = 300
Xc_ = np.column_stack([np.ones(n), rng.normal(size=(n, 2))])
w_true = np.array([-0.5, 2.0, -1.0])
yc = (rng.uniform(size=n) < sigmoid(Xc_ @ w_true)).astype(float)


def logloss(w):
    pr = np.clip(sigmoid(Xc_ @ w), 1e-12, 1 - 1e-12)
    return float(-np.mean(yc * np.log(pr) + (1 - yc) * np.log(1 - pr)))


def logloss_grad(w):
    return Xc_.T @ (sigmoid(Xc_ @ w) - yc) / n


w0 = np.array([0.3, -0.2, 0.1])
print("analytic :", logloss_grad(w0))
print("numerical:", num_grad(logloss, w0))
print("relative error:", f"{grad_check(logloss, logloss_grad, w0):.2e}")
```
```text
analytic : [ 0.173  -0.3685  0.1778]
numerical: [ 0.173  -0.3685  0.1778]
relative error: 8.37e-12
```

You will use this formula, unchanged, in ds.02 and ds.03. Understanding where the clean `(p − y)` comes from means you are not surprised by it.

## 8. Gradient descent

### 8.1 The idea

We have a loss `L(w)` and its gradient `∇L(w)`. Gradient descent is the simplest algorithm in machine learning: **start anywhere, step against the gradient, repeat.**

`w ← w − η ∇L(w)`

The number `η` (eta) is the **learning rate**: how big each step is. We implement it once and reuse it.

```python run
def gradient_descent(grad, w0, lr, steps):
    w = np.array(w0, dtype=float)
    path = [w.copy()]
    for _ in range(steps):
        w = w - lr * grad(w)
        path.append(w.copy())
    return w, np.array(path)


# a bowl: L(w) = (w1 - 3)^2 + 10 (w2 + 1)^2, minimum at (3, -1)
bowl = lambda w: (w[0] - 3) ** 2 + 10 * (w[1] + 1) ** 2
bowl_grad = lambda w: np.array([2 * (w[0] - 3), 20 * (w[1] + 1)])
print("gradient check of the bowl:", f"{grad_check(bowl, bowl_grad, np.array([1.0, 2.0])):.1e}")

w_end, path = gradient_descent(bowl_grad, [0.0, 2.0], lr=0.05, steps=60)
print("start (0, 2) ->", np.round(path[1], 3), np.round(path[2], 3), "... ->", np.round(w_end, 4), "(minimum: (3, -1))")
print("loss along the path:", [round(float(bowl(p_)), 4) for p_ in path[:5]], "...", round(float(bowl(path[-1])), 8))
```
```text
gradient check of the bowl: 4.9e-12
start (0, 2) -> [ 0.3 -1. ] [ 0.57 -1.  ] ... -> [ 2.9946 -1.    ] (minimum: (3, -1))
loss along the path: [99.0, 7.29, 5.9049, 4.783, 3.8742] ... 2.906e-05
```

### 8.2 The learning rate decides everything

Too small and progress crawls; right and it converges; too large and it **overshoots and diverges**. The bowl above is steeper in one direction (`w₂`, curvature 20) than the other (`w₁`, curvature 2), a stretched bowl, and the steep direction limits the learning rate.

```python run
print("learning rate | distance from the minimum after 0, 10, 30, 100 steps")
target = np.array([3.0, -1.0])
for lr in (0.001, 0.01, 0.05, 0.09, 0.1, 0.11):
    with np.errstate(all="ignore"):
        _, path = gradient_descent(bowl_grad, [0.0, 2.0], lr, 100)
    d = [float(np.linalg.norm(path[k] - target)) for k in (0, 10, 30, 100)]
    if d[-1] > d[0]:
        tag = "diverges"
    elif abs(d[3] - d[2]) < 0.01 * d[2] and d[3] > 0.1:
        tag = "stuck: bounces forever"
    else:
        tag = "slow" if d[-1] > 0.1 else "converges"
    print(f"{lr:12.3f}  | " + "  ".join(f"{x:12.4g}" for x in d) + f"   {tag}")
```
```text
learning rate | distance from the minimum after 0, 10, 30, 100 steps
       0.001  |        4.243         3.828         3.265         2.488   slow
       0.010  |        4.243         2.472         1.636        0.3979   slow
       0.050  |        4.243         1.046        0.1272     7.968e-05   converges
       0.090  |        4.243        0.5233       0.00863     7.245e-09   converges
       0.100  |        4.243         3.017             3             3   stuck: bounces forever
       0.110  |        4.243         18.58         712.1     2.485e+08   diverges
```

For a quadratic bowl the exact rule is: each step multiplies the error along a direction by `(1 − η λ)`, where `λ` is the curvature in that direction. It shrinks if `|1 − η λ| < 1`, that is `η < 2/λ_max`. With a largest curvature of 20 the limit is `0.1`, and the table shows it: 0.09 converges, 0.11 explodes, and exactly 0.1 is the borderline where the steep coordinate flips sign with the same size at every step (the factor is exactly −1) and never settles. In the flat direction (curvature 2) the factor at 0.09 is still 0.82, which is why even the good rates need dozens of steps. The slowest direction (curvature 2) then needs many steps: this tension between the largest and the smallest eigenvalue of the Hessian is exactly the **condition number** of section 3.3, and it is why **scaling features** makes training faster.

### 8.3 Fitting a regression by descent

The regression gradient of section 7.3 plugs straight in. We compare the result with the exact least-squares solution.

```python run
w_gd, path = gradient_descent(mse_grad, [0.0, 0.0, 0.0], lr=0.1, steps=300)
w_exact = np.linalg.lstsq(Xr, yr, rcond=None)[0]
print("gradient descent:", w_gd)
print("exact lstsq     :", w_exact)
print("true weights    :", true_w)
print("loss at start / after 300 steps / at the exact minimum:", round(mse(path[0]), 4), round(mse(w_gd), 6), round(mse(w_exact), 6))
```
```text
gradient descent: [ 1.9635 -0.9962  0.5209]
exact lstsq     : [ 1.9635 -0.9962  0.5209]
true weights    : [ 2.  -1.   0.5]
loss at start / after 300 steps / at the exact minimum: 1.7631 0.03079 0.03079
```

Descent reaches the exact answer to several digits without ever inverting a matrix, which is why it scales to models with millions of parameters where the normal equations are out of the question.

### 8.4 Why scaling the features helps

If one feature has a huge scale, the loss is a long thin valley, the condition number is large, and the learning rate that is safe for the steep direction is far too small for the flat one. We compare the same regression with and without standardising.

```python run
rng = np.random.default_rng(9)
n = 400
age = rng.uniform(20, 60, n)
income = rng.uniform(20_000, 120_000, n)
y_ = 0.5 * age + 0.0002 * income + rng.normal(0, 1, n)
X_raw = np.column_stack([np.ones(n), age, income])
X_std = np.column_stack([np.ones(n), (age - age.mean()) / age.std(), (income - income.mean()) / income.std()])


def descent_on(X, y, lr, steps):
    g = lambda w: 2.0 / len(y) * X.T @ (X @ w - y)
    L = lambda w: float(np.mean((X @ w - y) ** 2))
    w, path = gradient_descent(g, np.zeros(X.shape[1]), lr, steps)
    return L, w, path


print("condition number of X^T X: raw", f"{np.linalg.cond(X_raw.T @ X_raw):.1e}", "| standardised", f"{np.linalg.cond(X_std.T @ X_std):.1e}")
L_s, w_s, p_s = descent_on(X_std, y_, 0.1, 100)
print("standardised, lr 0.1, 100 steps: loss", round(L_s(w_s), 4), "(the noise floor is about 1)")
for lr in (1e-3, 1e-9, 1e-10):
    with np.errstate(all="ignore"):                       # the diverging runs overflow on purpose
        L_r, w_r, p_r = descent_on(X_raw, y_, lr, 100)
        val = L_r(w_r)
    note = "   <- exploded" if not np.isfinite(val) or val > 1e6 else ("   <- far from converged" if val > 2 else "")
    print(f"raw, lr {lr:.0e}, 100 steps: loss {val:.4g}{note}")
```
```text
condition number of X^T X: raw 1.1e+11 | standardised 1.1e+00
standardised, lr 0.1, 100 steps: loss 1.0584 (the noise floor is about 1)
raw, lr 1e-03, 100 steps: loss nan   <- exploded
raw, lr 1e-09, 100 steps: loss 2.486e+201   <- exploded
raw, lr 1e-10, 100 steps: loss 93.34   <- far from converged
```

With raw features either the learning rate is so large that the income direction blows up, or so small that nothing moves in the age direction. After standardising, one rate (0.1) works for every column. This is the practical meaning of "ill-conditioned".

### 8.5 Local minima, and a taste of stochastic descent

A convex loss (a bowl) has one minimum, and descent finds it from anywhere. The losses of neural networks are not convex: there are valleys and ridges, and where you start matters. Linear and logistic regression losses are convex, which is part of why they are so reliable.

```python run
wavy = lambda x: np.sin(3 * x) + 0.3 * x ** 2
wavy_grad = lambda x: np.array([3 * np.cos(3 * x[0]) + 0.6 * x[0]])
print("start | end point | loss there")
for start in (-3.0, -1.0, 0.5, 2.5):
    end, _ = gradient_descent(wavy_grad, [start], 0.02, 400)
    print(f"{start:5.1f} | {end[0]:9.4f} | {wavy(end[0]):9.4f}")
```
```text
start | end point | loss there
 -3.0 |   -2.4475 |    0.9251
 -1.0 |   -0.4908 |   -0.9229
  0.5 |   -0.4908 |   -0.9229
  2.5 |    1.4712 |   -0.3064
```

Different starting points settle in different valleys with different final losses. **Stochastic** gradient descent computes the gradient on a random small batch of rows each step; it is noisy, much cheaper per step, and the noise helps it escape shallow valleys. The only change to the algorithm is where the gradient comes from.

```python run
def sgd(X, y, lr, epochs, batch, seed=0):
    rng = np.random.default_rng(seed)
    w = np.zeros(X.shape[1])
    n = len(y)
    for _ in range(epochs):
        idx = rng.permutation(n)
        for s in range(0, n, batch):
            b = idx[s:s + batch]
            w = w - lr * 2.0 / len(b) * X[b].T @ (X[b] @ w - y[b])
    return w


w_sgd = sgd(Xr, yr, lr=0.05, epochs=30, batch=10)
print("SGD, batch 10, 30 epochs:", w_sgd)
print("exact                   :", w_exact)
```
```text
SGD, batch 10, 30 epochs: [ 1.949  -0.9929  0.5245]
exact                   : [ 1.9635 -0.9962  0.5209]
```

SGD ends close to the exact answer but not on it: it keeps jittering around the minimum, which is why learning rates are usually decayed over time.

## 9. Probability

### 9.1 Probability as a long-run frequency

A **probability** is a number between 0 (impossible) and 1 (certain) that measures how likely an event is. The most useful way to understand it for a programmer: **the fraction of times it happens in a very long run of identical experiments**. That makes simulation a probability tool, and we will use it constantly: when the algebra is hard, simulate; when the algebra is done, simulate to check it.

```python run
rng = np.random.default_rng(10)
for n_rolls in (10, 100, 10_000, 1_000_000):
    rolls = rng.integers(1, 7, n_rolls)
    print(f"{n_rolls:>9,} rolls: fraction of sixes = {np.mean(rolls == 6):.4f}   (theory 1/6 = {1/6:.4f})")
```
```text
       10 rolls: fraction of sixes = 0.1000   (theory 1/6 = 0.1667)
      100 rolls: fraction of sixes = 0.1600   (theory 1/6 = 0.1667)
   10,000 rolls: fraction of sixes = 0.1660   (theory 1/6 = 0.1667)
1,000,000 rolls: fraction of sixes = 0.1672   (theory 1/6 = 0.1667)
```

Ten rolls tell you almost nothing; a million tell you a lot. This convergence has a name, the **law of large numbers** (section 12).

### 9.2 The rules

For events `A` and `B`:

- **Complement**: `P(not A) = 1 − P(A)`.
- **Union**: `P(A or B) = P(A) + P(B) − P(A and B)` (subtract the overlap, or it is counted twice).
- **Independence**: `A` and `B` are independent if `P(A and B) = P(A) P(B)`; knowing one tells nothing about the other.
- **Conditional probability**: `P(A | B) = P(A and B) / P(B)`: the probability of `A` among the cases where `B` holds.

We check each with two dice, by enumerating all 36 equally likely outcomes.

```python run
space = list(itertools.product(range(1, 7), repeat=2))          # all 36 outcomes
prob = lambda event: sum(1 for o in space if event(o)) / len(space)

A_ = lambda o: o[0] + o[1] == 7                    # the sum is 7
B_ = lambda o: o[0] == 3                           # the first die shows 3
C_ = lambda o: o[0] % 2 == 0                       # the first die is even
D_ = lambda o: o[1] > 4                            # the second die is 5 or 6

print("P(sum is 7)             =", prob(A_), "= 6/36")
print("P(not sum 7)            =", prob(lambda o: not A_(o)), "= 1 - P(A):", 1 - prob(A_))
print("P(first=3 or sum 7)     =", round(prob(lambda o: A_(o) or B_(o)), 4), "| P(A) + P(B) - P(A and B) =", round(prob(A_) + prob(B_) - prob(lambda o: A_(o) and B_(o)), 4))
print("independent? P(A and B) =", round(prob(lambda o: A_(o) and B_(o)), 4), "| P(A) P(B) =", round(prob(A_) * prob(B_), 4), "-> independent:", math.isclose(prob(lambda o: A_(o) and B_(o)), prob(A_) * prob(B_)))
print("independent? P(C and D) =", round(prob(lambda o: C_(o) and D_(o)), 4), "| P(C) P(D) =", round(prob(C_) * prob(D_), 4), "-> independent:", math.isclose(prob(lambda o: C_(o) and D_(o)), prob(C_) * prob(D_)))
cond = prob(lambda o: A_(o) and B_(o)) / prob(B_)
print("P(sum 7 | first = 3)    =", round(cond, 4), "(by counting: 1 of the 6 outcomes with first=3)")
```
```text
P(sum is 7)             = 0.16666666666666666 = 6/36
P(not sum 7)            = 0.8333333333333334 = 1 - P(A): 0.8333333333333334
P(first=3 or sum 7)     = 0.3056 | P(A) + P(B) - P(A and B) = 0.3056
independent? P(A and B) = 0.0278 | P(A) P(B) = 0.0278 -> independent: True
independent? P(C and D) = 0.1667 | P(C) P(D) = 0.1667 -> independent: True
P(sum 7 | first = 3)    = 0.1667 (by counting: 1 of the 6 outcomes with first=3)
```

"Sum is 7" and "first die is 3" are independent: whatever the first die shows, the chance of reaching 7 is the same 1/6. A different sum would not be independent. Independence has to be checked, not assumed; assuming it wrongly is behind many errors in risk models.

### 9.3 Counting: arrangements and combinations

Many probabilities reduce to counting. The number of ways to **order** `k` items out of `n` is `n! / (n − k)!` (permutations); the number of ways to **choose** a set of `k` without regard to order is `n! / (k! (n − k)!)`, written `C(n, k)`.

```python run
print("5! =", math.factorial(5), "| permutations of 3 from 10:", math.perm(10, 3), "| combinations of 3 from 10:", math.comb(10, 3))
total = math.comb(52, 5)
flush = 4 * math.comb(13, 5)
print(f"\n5-card hands: {total:,}; flushes (any suit, incl. straight flushes): {flush:,} -> probability {flush / total:.5f}")

rng = np.random.default_rng(11)
deck = np.arange(52)                                # card c has suit c // 13
hits = 0
trials = 200_000
for _ in range(trials):
    hand = rng.choice(52, 5, replace=False)
    hits += len(set(hand // 13)) == 1
print(f"simulation, {trials:,} hands: {hits / trials:.5f}")
```
```text
5! = 120 | permutations of 3 from 10: 720 | combinations of 3 from 10: 120

5-card hands: 2,598,960; flushes (any suit, incl. straight flushes): 5,148 -> probability 0.00198
simulation, 200,000 hands: 0.00199
```

The simulation agrees with the count to about three digits - the sampling noise that we will quantify in section 12.

### 9.4 Counting that surprises: the birthday problem

In a room of 23 people, what is the probability that two share a birthday? Intuition says "small"; the algebra says otherwise. The complement is easier: the probability that **all** birthdays differ is `(365/365)(364/365)(363/365)…`.

```python run
def p_shared_birthday(k):
    p_all_different = 1.0
    for i in range(k):
        p_all_different *= (365 - i) / 365
    return 1 - p_all_different


rng = np.random.default_rng(12)
def simulate_birthday(k, trials=20_000):
    days = rng.integers(0, 365, (trials, k))
    srt = np.sort(days, axis=1)
    return float(np.mean((np.diff(srt, axis=1) == 0).any(axis=1)))


print(" people | exact | simulation")
for k in (10, 23, 40, 70):
    print(f"{k:7d} | {p_shared_birthday(k):.4f} | {simulate_birthday(k):.4f}")
```
```text
 people | exact | simulation
     10 | 0.1169 | 0.1157
     23 | 0.5073 | 0.5044
     40 | 0.8912 | 0.8905
     70 | 0.9992 | 0.9990
```

With 23 people it is already above a half: there are `C(23, 2) = 253` pairs, and each is a chance. The lesson for data work: the number of *comparisons* grows faster than the number of items, which is also why testing many hypotheses finds "significant" results by luck (section 14.6).

## 10. Bayes' theorem

### 10.1 Reversing a conditional

`P(A | B)` and `P(B | A)` are different things, and confusing them is one of the most expensive mistakes in data work. "If a person has the disease, the test is positive 99% of the time" is `P(positive | disease)`. What a patient wants is `P(disease | positive)`. **Bayes' theorem** converts one into the other:

`P(A | B) = P(B | A) P(A) / P(B)`

and `P(B)` is found by the **law of total probability**: `P(B) = P(B | A) P(A) + P(B | not A) P(not A)`.

Take a screening test: the condition affects 1% of people (the **prior**, or base rate); the test detects 99% of cases (**sensitivity**) and wrongly flags 5% of healthy people (**false-positive rate**).

```python run
def bayes_posterior(prior, sensitivity, false_positive_rate):
    p_pos = sensitivity * prior + false_positive_rate * (1 - prior)          # law of total probability
    return sensitivity * prior / p_pos


post = bayes_posterior(0.01, 0.99, 0.05)
print(f"P(disease | positive test) = {post:.4f}")
print("Most people guess 0.99 or 0.95. The truth is about one in six.")
```
```text
P(disease | positive test) = 0.1667
Most people guess 0.99 or 0.95. The truth is about one in six.
```

### 10.2 Why: count people instead of probabilities

Imagine 10,000 people. 100 have the condition and 99 of them test positive. Of the 9,900 healthy people, 5% (495) also test positive. So 594 people test positive and only 99 of them are really ill.

```python run
N = 10_000
ill = int(N * 0.01)
true_pos = round(ill * 0.99)
false_pos = round((N - ill) * 0.05)
print(f"ill: {ill} | positive and ill: {true_pos} | positive and healthy: {false_pos} | all positives: {true_pos + false_pos}")
print(f"share of positives who are ill: {true_pos / (true_pos + false_pos):.4f}")

rng = np.random.default_rng(13)
people_ill = rng.uniform(size=2_000_000) < 0.01
positive = np.where(people_ill, rng.uniform(size=2_000_000) < 0.99, rng.uniform(size=2_000_000) < 0.05)
print(f"simulated, 2 million people: P(ill | positive) = {people_ill[positive].mean():.4f}")
```
```text
ill: 100 | positive and ill: 99 | positive and healthy: 495 | all positives: 594
share of positives who are ill: 0.1667
simulated, 2 million people: P(ill | positive) = 0.1675
```

The false positives from the huge healthy group swamp the true positives from the small ill group. **When the condition is rare, even an accurate test produces mostly false alarms.** This is the base-rate fallacy, and it applies to fraud detection, spam filters, security alerts and medical screening alike: an alert from a rare-event detector must be judged against the base rate.

### 10.3 How the answer moves with the base rate

```python run
print("prior (base rate) | P(ill | positive)")
for prior in (0.0001, 0.001, 0.01, 0.1, 0.5):
    print(f"{prior:17.4f} | {bayes_posterior(prior, 0.99, 0.05):.4f}")
print("\nbetter test (false-positive rate 0.5%), prior 1%:", round(bayes_posterior(0.01, 0.99, 0.005), 4))
```
```text
prior (base rate) | P(ill | positive)
           0.0001 | 0.0020
           0.0010 | 0.0194
           0.0100 | 0.1667
           0.1000 | 0.6875
           0.5000 | 0.9519

better test (false-positive rate 0.5%), prior 1%: 0.6667
```

### 10.4 Updating step by step: evidence accumulates

Bayes' theorem is a machine for **updating belief**. After one positive test the posterior is 0.17; if we test again (independently), that posterior becomes the new prior.

```python run
belief = 0.01
print("tests that came back positive | P(ill)")
print(f"{0:29d} | {belief:.4f}")
for k in range(1, 5):
    belief = bayes_posterior(belief, 0.99, 0.05)
    print(f"{k:29d} | {belief:.4f}")
```
```text
tests that came back positive | P(ill)
                            0 | 0.0100
                            1 | 0.1667
                            2 | 0.7984
                            3 | 0.9874
                            4 | 0.9994
```

Each independent positive result multiplies the odds by the **likelihood ratio** `0.99 / 0.05 ≈ 20`. Independence matters: two tests that share the same flaw are not two pieces of evidence.

> **Predict the output.** A spam filter flags 98% of spam and wrongly flags 1% of good email. Spam is 20% of all email. What fraction of flagged email is really spam? (Do it with counts of 1,000 emails.)

<details><summary>Answer</summary>

```python run
print(round(bayes_posterior(0.20, 0.98, 0.01), 4))
```
```text
0.9608
```

Of 1,000 emails, 200 are spam and 196 are flagged; of the 800 good emails 8 are flagged. So 196 of the 204 flagged are spam: about 96%. Because spam is common here (a high prior), the filter is trustworthy, unlike the rare-disease test with similar accuracy.

</details>

### 10.5 The Monty Hall problem: simulation settles an argument

You pick one of three doors; a prize is behind one. The host, who knows where it is, opens a different door that has no prize and offers you a switch. Should you? Many people (including professional mathematicians, historically) say it makes no difference. Simulate.

```python run
rng = np.random.default_rng(14)
trials = 200_000
prize = rng.integers(0, 3, trials)
pick = rng.integers(0, 3, trials)
stay_wins = switch_wins = 0
for t in range(trials):
    options = [d for d in range(3) if d != pick[t] and d != prize[t]]       # doors the host may open
    opened = options[rng.integers(0, len(options))]
    switch_to = 3 - pick[t] - opened                                          # the one door left (0 + 1 + 2 = 3)
    stay_wins += pick[t] == prize[t]
    switch_wins += switch_to == prize[t]
print(f"stay   wins: {stay_wins / trials:.4f}   (theory 1/3)")
print(f"switch wins: {switch_wins / trials:.4f}   (theory 2/3)")
```
```text
stay   wins: 0.3347   (theory 1/3)
switch wins: 0.6653   (theory 2/3)
```

Your first pick is right one time in three and that does not change. The host's move gives no new information about your door, but all the remaining probability (2/3) now sits on the one other closed door. Switching wins exactly when the first pick was wrong. Bayes' theorem gives the same answer: the host is forced to avoid the prize, so seeing him open a door is evidence about where the prize is *not*.


## 11. Random variables and distributions

### 11.1 A number that depends on chance

A **random variable** is a number produced by a random process: the roll of a die, the number of customers who arrive in an hour, the height of a person chosen at random. Its **distribution** says which values are possible and how likely each is. Two kinds:

- **Discrete**: a countable set of values, each with a probability. The list of probabilities is the **probability mass function (PMF)**.
- **Continuous**: any value in a range. The probability of an exact value is zero; instead a **density** (PDF) gives probability per unit length, and probability comes from **area** under it. The **cumulative distribution function (CDF)** `F(x) = P(X ≤ x)` works for both.

### 11.2 Expectation and variance

The **expected value** `E[X]` is the probability-weighted average, the long-run mean. The **variance** `Var[X] = E[(X − μ)²]` is the expected squared distance from the mean, and the **standard deviation** is its square root, in the original units.

```python run
values = np.arange(1, 7)
pmf = np.full(6, 1 / 6)                                  # a fair die
mean_die = float((values * pmf).sum())
var_die = float(((values - mean_die) ** 2 * pmf).sum())
print(f"fair die: E[X] = {mean_die}, Var[X] = {var_die:.4f}, SD = {math.sqrt(var_die):.4f}")

rng = np.random.default_rng(20)
rolls = rng.integers(1, 7, 1_000_000)
print(f"simulated: mean = {rolls.mean():.4f}, var = {rolls.var():.4f}")

loaded = np.array([0.5, 0.1, 0.1, 0.1, 0.1, 0.1])
m2 = float((values * loaded).sum())
print(f"\nloaded die (half of the rolls are 1): E[X] = {m2:.2f}, Var[X] = {float(((values - m2) ** 2 * loaded).sum()):.4f}")
```
```text
fair die: E[X] = 3.5, Var[X] = 2.9167, SD = 1.7078
simulated: mean = 3.5014, var = 2.9132

loaded die (half of the rolls are 1): E[X] = 2.50, Var[X] = 3.2500
```

Two properties are used everywhere. **Expectation is linear**: `E[aX + bY] = a E[X] + b E[Y]`, always, even if `X` and `Y` depend on each other. **Variance** of a sum adds *only if they are independent*: `Var[X + Y] = Var[X] + Var[Y]`, and `Var[aX] = a² Var[X]`.

```python run
rng = np.random.default_rng(21)
X1 = rng.integers(1, 7, 500_000)
X2 = rng.integers(1, 7, 500_000)
print(f"E[X1 + X2] = {np.mean(X1 + X2):.4f}  vs  E[X1] + E[X2] = {X1.mean() + X2.mean():.4f}")
print(f"Var[X1 + X2] = {np.var(X1 + X2):.4f}  vs  Var[X1] + Var[X2] = {X1.var() + X2.var():.4f}  (independent: they add)")
Y = X1 + rng.integers(0, 2, 500_000)                    # Y depends strongly on X1
print(f"Var[X1 + Y] = {np.var(X1 + Y):.4f}  vs  Var[X1] + Var[Y] = {X1.var() + Y.var():.4f}  (dependent: they do not)")
print(f"Var[3 X1] = {np.var(3 * X1):.4f}  vs  9 Var[X1] = {9 * X1.var():.4f}")
```
```text
E[X1 + X2] = 7.0061  vs  E[X1] + E[X2] = 7.0061
Var[X1 + X2] = 5.8337  vs  Var[X1] + Var[X2] = 5.8353  (independent: they add)
Var[X1 + Y] = 11.9284  vs  Var[X1] + Var[Y] = 6.0892  (dependent: they do not)
Var[3 X1] = 26.2650  vs  9 Var[X1] = 26.2650
```

The average of `n` independent measurements has variance `σ²/n` (the sum has variance `nσ²`, dividing by `n` divides the variance by `n²`). So the standard deviation of a mean falls like `σ/√n`: **to halve the uncertainty you need four times the data**. This is the single most useful formula in statistics, and section 12 verifies it.

### 11.3 The Bernoulli and binomial distributions

A **Bernoulli** trial is a yes/no experiment with success probability `p`; mean `p`, variance `p(1−p)`. Counting successes in `n` independent trials gives the **binomial** distribution:

`P(X = k) = C(n, k) pᵏ (1 − p)ⁿ⁻ᵏ`

```python run
def binom_pmf(k, n, p):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


n_, p_ = 10, 0.3
ks = np.arange(n_ + 1)
pm = np.array([binom_pmf(int(k), n_, p_) for k in ks])
print("k    :", ks)
print("P(k) :", np.round(pm, 4))
print("sums to 1:", round(float(pm.sum()), 10), "| mean:", round(float((ks * pm).sum()), 6), "(n p =", n_ * p_, ") | variance:", round(float(((ks - n_ * p_) ** 2 * pm).sum()), 6), "(n p (1-p) =", n_ * p_ * (1 - p_), ")")

rng = np.random.default_rng(22)
sim = rng.binomial(n_, p_, 500_000)
print("simulation of P(k):", np.round(np.bincount(sim, minlength=n_ + 1) / len(sim), 4))
print("P(at least 5 successes) =", round(float(pm[5:].sum()), 4), "| simulated:", round(float(np.mean(sim >= 5)), 4))
```
```text
k    : [ 0  1  2  3  4  5  6  7  8  9 10]
P(k) : [0.0282 0.1211 0.2335 0.2668 0.2001 0.1029 0.0368 0.009  0.0014 0.0001 0.    ]
sums to 1: 1.0 | mean: 3.0 (n p = 3.0 ) | variance: 2.1 (n p (1-p) = 2.0999999999999996 )
simulation of P(k): [0.0284 0.1216 0.2333 0.2672 0.1992 0.1028 0.037  0.009  0.0013 0.0002 0.    ]
P(at least 5 successes) = 0.1503 | simulated: 0.1503
```

Examples of the binomial: how many of 100 emails are spam, how many of 50 customers click. Note that the code uses exactly what we derived: the count `C(n, k)` of arrangements times the probability of each arrangement.

### 11.4 The Poisson distribution: counting rare events

When events arrive independently at a steady average rate `λ` per interval (calls per hour, typos per page, server errors per day), the count in an interval follows the **Poisson** distribution:

`P(X = k) = e^(−λ) λᵏ / k!`

Its mean and its variance are both `λ`. That equality is a useful test: count data whose variance is much larger than its mean are **overdispersed** and are not Poisson (ds.02 returns to this).

```python run
def poisson_pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


lam = 4.0
ks = np.arange(0, 15)
pm = np.array([poisson_pmf(int(k), lam) for k in ks])
rng = np.random.default_rng(23)
sim = rng.poisson(lam, 500_000)
print("k    :", ks[:9])
print("exact:", np.round(pm[:9], 4))
print("sim  :", np.round(np.bincount(sim, minlength=15)[:9] / len(sim), 4))
print("mean and variance of the simulation:", round(sim.mean(), 3), round(sim.var(), 3), "(both close to lambda = 4)")

# Poisson as the limit of a binomial with many trials and a small p
n_big = 2000
print("\nbinomial(2000, 0.002) vs Poisson(4) at k = 0..4:")
print(" binomial:", np.round([binom_pmf(k, n_big, 4 / n_big) for k in range(5)], 5))
print(" poisson :", np.round([poisson_pmf(k, 4.0) for k in range(5)], 5))
```
```text
k    : [0 1 2 3 4 5 6 7 8]
exact: [0.0183 0.0733 0.1465 0.1954 0.1954 0.1563 0.1042 0.0595 0.0298]
sim  : [0.0181 0.0735 0.1471 0.195  0.1953 0.1559 0.104  0.06   0.0298]
mean and variance of the simulation: 4.0 4.002 (both close to lambda = 4)

binomial(2000, 0.002) vs Poisson(4) at k = 0..4:
 binomial: [0.0182 0.0731 0.1464 0.1955 0.1956]
 poisson : [0.0183 0.0733 0.1465 0.1954 0.1954]
```

### 11.5 The uniform and exponential distributions

The **uniform** distribution on `[a, b]` makes every value in the range equally likely (mean `(a+b)/2`, variance `(b−a)²/12`). It is the raw material for simulation: nearly every random-number generator starts from uniform numbers.

The **exponential** distribution models the *waiting time* between Poisson events. Its density is `λ e^(−λx)` for `x ≥ 0`, with mean `1/λ`. It is **memoryless**: given that you have already waited 5 minutes, the remaining wait has the same distribution as a fresh one.

```python run
rng = np.random.default_rng(24)
lam = 0.5                                                     # events per minute -> mean wait 2 minutes
waits = rng.exponential(1 / lam, 1_000_000)
print(f"mean wait {waits.mean():.4f} (theory {1 / lam}) | SD {waits.std():.4f} (theory {1 / lam})")
t_ = 3.0
print(f"P(wait > {t_}) = {np.mean(waits > t_):.4f} | theory e^(-lambda t) = {math.exp(-lam * t_):.4f}")
long_waits = waits[waits > 5.0]
print(f"memoryless: P(wait > 5 + {t_} | wait > 5) = {np.mean(long_waits > 5.0 + t_):.4f}  (same as P(wait > {t_}))")
```
```text
mean wait 2.0004 (theory 2.0) | SD 1.9974 (theory 2.0)
P(wait > 3.0) = 0.2230 | theory e^(-lambda t) = 0.2231
memoryless: P(wait > 5 + 3.0 | wait > 5) = 0.2213  (same as P(wait > 3.0))
```

An important technique follows from the CDF `F(x) = 1 − e^(−λx)`: solving `u = F(x)` for `x` turns a uniform `u` into an exponential `x = −ln(1 − u)/λ`. This **inverse transform** converts uniform numbers into any distribution whose CDF we can invert.

```python run
u = rng.uniform(size=1_000_000)
x_inv = -np.log(1 - u) / lam
print(f"inverse-transform sample: mean {x_inv.mean():.4f}, SD {x_inv.std():.4f}, P(> {t_}) = {np.mean(x_inv > t_):.4f}")
```
```text
inverse-transform sample: mean 1.9981, SD 1.9979, P(> 3.0) = 0.2231
```

### 11.6 The normal distribution

The **normal** (Gaussian) distribution, the bell curve, has density

`f(x) = (1 / (σ √(2π))) exp(−(x − μ)² / (2σ²))`

It is described completely by its mean `μ` and standard deviation `σ`. It earns its place from the central limit theorem (section 12): sums and averages of many small independent effects are close to normal, whatever the individual effects look like. Implemented with NumPy and `math.erf` (the CDF has no closed form but is a function of `erf`):

```python run
def normal_pdf(x, mu=0.0, sigma=1.0):
    x = np.asarray(x, dtype=float)
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * math.sqrt(2 * math.pi))


def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1.0 + np.vectorize(math.erf)((np.asarray(x, dtype=float) - mu) / (sigma * math.sqrt(2.0))))


print("pdf at 0:", float(normal_pdf(0.0)), "(1/sqrt(2 pi) = 0.3989)")
for k in (1, 2, 3):
    print(f"P(|Z| < {k}) = {float(normal_cdf(k) - normal_cdf(-k)):.4f}")
print("P(|Z| < 1.96) =", round(float(normal_cdf(1.96) - normal_cdf(-1.96)), 4), "<- the famous 95%")
if scipy is not None:
    print("matches scipy.stats.norm:", np.allclose(normal_cdf([-2, -0.5, 0, 1.3]), stats.norm.cdf([-2, -0.5, 0, 1.3])))
```
```text
pdf at 0: 0.3989422804014327 (1/sqrt(2 pi) = 0.3989)
P(|Z| < 1) = 0.6827
P(|Z| < 2) = 0.9545
P(|Z| < 3) = 0.9973
P(|Z| < 1.96) = 0.95 <- the famous 95%
matches scipy.stats.norm: True
```

The **68-95-99.7 rule** is these numbers: about 68% of a normal population lies within one standard deviation of the mean, 95% within two (1.96 to be exact) and 99.7% within three. The inverse of the CDF, the **quantile function**, answers "what value cuts off the bottom 97.5%?"; we find it by bisection, since the CDF is increasing.

```python run
def normal_ppf(q, mu=0.0, sigma=1.0):
    """Quantile function by bisection on the CDF."""
    lo, hi = -40.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if float(normal_cdf(mid)) < q:
            lo = mid
        else:
            hi = mid
    return mu + sigma * (lo + hi) / 2


print("z for 97.5% :", round(normal_ppf(0.975), 6), "(1.959964)")
print("z for 99.5% :", round(normal_ppf(0.995), 6), "(2.575829)")
print("z for 95%   :", round(normal_ppf(0.95), 6), "(1.644854, a one-sided 95%)")
```
```text
z for 97.5% : 1.959964 (1.959964)
z for 99.5% : 2.575829 (2.575829)
z for 95%   : 1.644854 (1.644854, a one-sided 95%)
```

A **z-score** `z = (x − μ)/σ` says how many standard deviations a value is from the mean. A student who scores 78 in a class with mean 65 and SD 8 has `z = 1.625`, about the 95th percentile (the fraction of the class below): `normal_cdf(1.625) ≈ 0.948`.

### 11.7 Looking at a distribution: histograms and Q-Q checks

To see whether data look normal, compare the sample quantiles with the theoretical ones (a Q-Q plot, here as numbers) and check the shape numbers: **skewness** (asymmetry, zero for a normal) and **excess kurtosis** (tail weight, zero for a normal).

```python run
def skewness(x):
    x = np.asarray(x, float); z = (x - x.mean()) / x.std()
    return float(np.mean(z ** 3))


def excess_kurtosis(x):
    x = np.asarray(x, float); z = (x - x.mean()) / x.std()
    return float(np.mean(z ** 4) - 3)


rng = np.random.default_rng(25)
samples = {"normal": rng.normal(size=100_000), "exponential": rng.exponential(size=100_000), "uniform": rng.uniform(size=100_000), "t with 3 df (heavy tails)": rng.standard_t(3, size=100_000)}
qs = (0.01, 0.05, 0.5, 0.95, 0.99)
print(f"{'':28} skew  ex.kurt |  sample quantiles standardised at " + ", ".join(f"{q:.0%}" for q in qs))
print(f"{'normal quantiles':28} {'':14} |  " + "  ".join(f"{normal_ppf(q):6.2f}" for q in qs))
for name, x in samples.items():
    z = (x - x.mean()) / x.std()
    print(f"{name:28} {skewness(x):5.2f} {excess_kurtosis(x):8.2f} |  " + "  ".join(f"{np.quantile(z, q):6.2f}" for q in qs))
```
```text
                             skew  ex.kurt |  sample quantiles standardised at 1%, 5%, 50%, 95%, 99%
normal quantiles                            |   -2.33   -1.64   -0.00    1.64    2.33
normal                       -0.01     0.02 |   -2.34   -1.65    0.00    1.64    2.34
exponential                   2.04     6.60 |   -0.99   -0.94   -0.31    1.99    3.58
uniform                      -0.00    -1.20 |   -1.70   -1.56    0.00    1.56    1.70
t with 3 df (heavy tails)    -4.01   377.20 |   -2.59   -1.35   -0.00    1.37    2.65
```

Skew shows up as unequal tails (the exponential's upper quantiles are far out, its lower ones squashed); heavy tails show up as extreme quantiles beyond the normal's with a large excess kurtosis. The heavy-tailed `t` distribution is the reason "3 standard deviations" is not a safe outlier rule in every dataset.

## 12. Sampling, the law of large numbers and the central limit theorem

### 12.1 A sample is one draw from many possible samples

We almost never see the whole **population**; we see a **sample**, and we use it to learn about the population. A statistic (the sample mean, say) computed from the sample is itself a random variable: draw another sample and you get another value. The distribution of the statistic over all possible samples is its **sampling distribution**. Everything in inference is about this distribution.

To study it we need a population we fully control. Take 200,000 incomes with a heavy right skew (log-normal).

```python run
rng = np.random.default_rng(30)
population = rng.lognormal(mean=10.5, sigma=0.8, size=200_000)
mu_pop, sd_pop = population.mean(), population.std()
print(f"population: mean {mu_pop:,.0f} | SD {sd_pop:,.0f} | median {np.median(population):,.0f} | skewness {skewness(population):.2f}")
```
```text
population: mean 49,978 | SD 47,298 | median 36,237 | skewness 3.75
```

### 12.2 The law of large numbers

The **law of large numbers**: as the sample grows, the sample mean converges to the population mean. We watch one growing sample.

```python run
stream = rng.choice(population, size=100_000)
running = np.cumsum(stream) / np.arange(1, len(stream) + 1)
for n_ in (10, 100, 1_000, 10_000, 100_000):
    print(f"n = {n_:>7,}: running mean {running[n_ - 1]:>10,.0f} | error {abs(running[n_ - 1] - mu_pop) / mu_pop:7.2%}")
```
```text
n =      10: running mean     53,095 | error   6.24%
n =     100: running mean     49,317 | error   1.32%
n =   1,000: running mean     49,880 | error   0.20%
n =  10,000: running mean     50,133 | error   0.31%
n = 100,000: running mean     50,154 | error   0.35%
```

The error falls, but slowly, and not smoothly (it can bounce). Convergence has a rate, and the next result gives it. One warning first: for some distributions there is no mean to converge to (the Cauchy distribution), and then the running mean never settles.

```python run
cauchy = rng.standard_cauchy(100_000)
run_c = np.cumsum(cauchy) / np.arange(1, len(cauchy) + 1)
print("Cauchy running mean at n = 100, 1,000, 10,000, 100,000:", np.round(run_c[[99, 999, 9999, 99999]], 3), "(no convergence: it has no mean)")
```
```text
Cauchy running mean at n = 100, 1,000, 10,000, 100,000: [-0.745  2.652  1.427 -1.623] (no convergence: it has no mean)
```

### 12.3 The sampling distribution of the mean

Take many samples of size `n`, compute each mean, and look at the spread of the means. The theory (section 11.2) predicts a standard deviation of `σ/√n`: the **standard error**.

```python run
def sample_means(n, reps=20_000, seed=0):
    r = np.random.default_rng(seed)
    return r.choice(population, size=(reps, n)).mean(axis=1)


print("   n | mean of means | SD of means | theory sigma/sqrt(n) | skewness of means")
for n_ in (1, 5, 30, 200, 1000):
    m = sample_means(n_)
    print(f"{n_:4d} | {m.mean():13,.0f} | {m.std():11,.0f} | {sd_pop / math.sqrt(n_):20,.0f} | {skewness(m):8.2f}")
```
```text
   n | mean of means | SD of means | theory sigma/sqrt(n) | skewness of means
   1 |        49,549 |      49,042 |               47,298 |     6.09
   5 |        49,739 |      21,509 |               21,152 |     1.95
  30 |        50,016 |       8,638 |                8,635 |     0.71
 200 |        50,024 |       3,326 |                3,344 |     0.26
1000 |        49,988 |       1,492 |                1,496 |     0.09
```

Three facts are visible. The mean of the sample means equals the population mean (the sample mean is **unbiased**). The spread matches `σ/√n`. And the **shape** changes: for `n = 1` it is the skewed population itself, but the skewness falls towards zero as `n` grows.

### 12.4 The central limit theorem

That last observation is the **central limit theorem (CLT)**: for almost any population with a finite variance, the sampling distribution of the mean becomes **normal** as `n` grows, with mean `μ` and standard deviation `σ/√n`. This is the theorem that makes confidence intervals and tests work for data that are not themselves normal. Check how normal the means really are: what fraction fall within 1.96 standard errors of the true mean? A normal distribution would say 95%.

```python run
print("   n | share of sample means within 1.96 SE of the true mean (normal says 0.95)")
for n_ in (2, 5, 30, 200, 1000):
    m = sample_means(n_)
    print(f"{n_:4d} | {np.mean(np.abs(m - mu_pop) < 1.96 * sd_pop / math.sqrt(n_)):.4f}")
```
```text
   n | share of sample means within 1.96 SE of the true mean (normal says 0.95)
   2 | 0.9573
   5 | 0.9563
  30 | 0.9538
 200 | 0.9520
1000 | 0.9509
```

Notice that this check looks reassuring even for tiny `n`: a symmetric interval around the centre hides the problem. The failure of normality sits in the **shape**, the skewness column of the previous table (0.71 at `n = 30`, still 0.26 at 200), and in the **tails**: the coverage of the interval of section 13.2 is still only 0.89 at `n = 30`. So how large must `n` be? There is no magic 30. It depends on the skew of the population: the more skewed or heavy-tailed, the larger `n` must be. For a heavy right skew like this one, several hundred is comfortable. For a symmetric population, small samples already work.

> **Predict the output.** A population has SD 20. How large a sample is needed to bring the standard error of the mean down to 1? And down to 0.5?

<details><summary>Answer</summary>

```python run
for target in (1.0, 0.5):
    print(f"standard error {target}: n = {(20 / target) ** 2:.0f}")
```
```text
standard error 1.0: n = 400
standard error 0.5: n = 1600
```

`σ/√n = 1` gives `n = 400`; halving the standard error to 0.5 needs `n = 1,600`, four times as many. Precision is expensive: every extra digit of accuracy costs a hundred times more data.

</details>

### 12.5 Not everything has a standard error as simple as `σ/√n`

The formula is for the **mean**. For a median, a ratio, a correlation or a percentile there is no equally simple formula. We can still see the sampling distribution by simulation, and this is what motivates the bootstrap (section 15).

```python run
n_ = 100
meds = np.array([np.median(np.random.default_rng(s).choice(population, n_)) for s in range(4000)])
means = sample_means(n_, reps=4000, seed=1)
print(f"n = {n_}: SD of the sample mean   = {means.std():10,.0f} (theory {sd_pop / math.sqrt(n_):,.0f})")
print(f"n = {n_}: SD of the sample median = {meds.std():10,.0f} (no simple formula; here smaller, as the median resists the long tail)")
```
```text
n = 100: SD of the sample mean   =      4,714 (theory 4,730)
n = 100: SD of the sample median =      3,645 (no simple formula; here smaller, as the median resists the long tail)
```

## 13. Confidence intervals

### 13.1 What the interval is

We have one sample and want to say where the population mean is. A **confidence interval** is a range computed from the sample, built so that the procedure captures the true value in a stated fraction (the **confidence level**, say 95%) of repeated samples. By the CLT the sample mean is approximately normal around `μ` with standard deviation `σ/√n`, and `σ` is estimated by the sample SD `s`:

`x̄ ± z · s/√n`, with `z = 1.96` for 95%

```python run
def mean_ci_z(x, level=0.95):
    x = np.asarray(x, float)
    se = x.std(ddof=1) / math.sqrt(len(x))
    z = normal_ppf(0.5 + level / 2)
    return x.mean() - z * se, x.mean() + z * se, se


rng = np.random.default_rng(31)
one = rng.choice(population, 200)
lo, hi, se = mean_ci_z(one)
print(f"one sample of 200: mean {one.mean():,.0f} | standard error {se:,.0f} | 95% CI ({lo:,.0f}, {hi:,.0f})")
print(f"the true population mean is {mu_pop:,.0f}: inside the interval: {lo <= mu_pop <= hi}")
```
```text
one sample of 200: mean 53,084 | standard error 3,923 | 95% CI (45,396, 60,772)
the true population mean is 49,978: inside the interval: True
```

`ddof=1` divides by `n − 1` rather than `n` (Bessel's correction): the sample variance computed around the sample's own mean is on average slightly too small, and `n − 1` repairs it. Check it by simulation:

```python run
rng = np.random.default_rng(32)
small = rng.normal(0, 2, size=(200_000, 5))                    # true variance 4
print("true variance 4 | divide by n:", round(small.var(axis=1, ddof=0).mean(), 4), "| divide by n-1:", round(small.var(axis=1, ddof=1).mean(), 4))
```
```text
true variance 4 | divide by n: 3.2041 | divide by n-1: 4.0051
```

### 13.2 What "95%" means: a coverage experiment

The 95% belongs to the **procedure**, not to the one interval in front of you. Repeat the experiment many times and count how often the interval captures the truth.

```python run
def coverage(ci_fn, n, reps=4000, seed=0):
    r = np.random.default_rng(seed)
    hit = 0
    widths = []
    for _ in range(reps):
        lo, hi = ci_fn(r.choice(population, n))[:2]
        hit += lo <= mu_pop <= hi
        widths.append(hi - lo)
    return hit / reps, float(np.mean(widths))


print("   n | coverage of the 95% z-interval | mean width")
for n_ in (10, 30, 100, 400):
    cov, w = coverage(mean_ci_z, n_)
    print(f"{n_:4d} | {cov:30.3f} | {w:12,.0f}")
```
```text
   n | coverage of the 95% z-interval | mean width
  10 |                          0.841 |       50,363
  30 |                          0.892 |       31,620
 100 |                          0.930 |       18,050
 400 |                          0.952 |        9,181
```

For large samples the coverage is close to 95%. For small samples it falls short: the interval is too narrow because `s` is itself uncertain and the sample mean of a skewed population is not yet normal. The first problem has a standard remedy.

A picture in numbers: 20 intervals from 20 samples.

```python run
r = np.random.default_rng(33)
misses = 0
for i in range(20):
    lo, hi, _ = mean_ci_z(r.choice(population, 100))
    ok = lo <= mu_pop <= hi
    misses += (not ok)
    print(f"sample {i + 1:2d}: ({lo:9,.0f}, {hi:9,.0f})  {'captures' if ok else 'MISSES the true mean'}")
print(f"{misses} of 20 miss: about one in twenty is what 95% means; no single interval can tell you which kind it is")
```
```text
sample  1: (   35,798,    53,127)  captures
sample  2: (   34,628,    51,926)  captures
sample  3: (   38,238,    55,118)  captures
sample  4: (   38,184,    50,850)  captures
sample  5: (   36,891,    53,413)  captures
sample  6: (   42,341,    55,706)  captures
sample  7: (   40,806,    60,261)  captures
sample  8: (   41,490,    60,323)  captures
sample  9: (   34,926,    48,053)  MISSES the true mean
sample 10: (   37,238,    52,282)  captures
sample 11: (   44,801,    68,460)  captures
sample 12: (   47,373,    69,696)  captures
sample 13: (   39,640,    54,621)  captures
sample 14: (   45,837,    62,771)  captures
sample 15: (   38,393,    50,997)  captures
sample 16: (   44,574,    62,445)  captures
sample 17: (   37,864,    52,233)  captures
sample 18: (   38,486,    57,593)  captures
sample 19: (   35,140,    54,838)  captures
sample 20: (   36,699,    53,634)  captures
1 of 20 miss: about one in twenty is what 95% means; no single interval can tell you which kind it is
```

### 13.3 The t-distribution for small samples

When `n` is small, replace the normal's 1.96 with a larger number from the **t-distribution** with `n − 1` degrees of freedom. It looks like a normal with fatter tails, and approaches the normal as `n` grows. Its density is

`f(t) = Γ((ν+1)/2) / (√(νπ) Γ(ν/2)) · (1 + t²/ν)^(−(ν+1)/2)`

We build its CDF by numerical integration and its quantile by bisection, in NumPy, and check against SciPy.

```python run
def t_pdf(x, df):
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    return c * (1 + np.asarray(x, float) ** 2 / df) ** (-(df + 1) / 2)


def t_cdf(x, df, steps=2001):
    """CDF by integrating the density from 0 to |x| (the density is symmetric)."""
    grid = np.linspace(0.0, abs(x), steps)
    area = np.trapezoid(t_pdf(grid, df), grid)
    return 0.5 + math.copysign(area, x)


def t_ppf(q, df):
    lo, hi = -200.0, 200.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


print(" df | our t quantile (97.5%) | scipy" + ("" if scipy is not None else " (skipped)"))
for df in (2, 5, 9, 29, 99, 1000):
    ours = t_ppf(0.975, df)
    ref = f"{stats.t.ppf(0.975, df):.4f}" if scipy is not None else "-"
    print(f"{df:3d} | {ours:22.4f} | {ref}")
print("normal 1.9600: the t quantile approaches it as the degrees of freedom grow")
```
```text
 df | our t quantile (97.5%) | scipy
  2 |                 4.3027 | 4.3027
  5 |                 2.5706 | 2.5706
  9 |                 2.2622 | 2.2622
 29 |                 2.0452 | 2.0452
 99 |                 1.9842 | 1.9842
1000 |                 1.9623 | 1.9623
normal 1.9600: the t quantile approaches it as the degrees of freedom grow
```

With 9 degrees of freedom (a sample of 10) the multiplier is 2.26 rather than 1.96: the interval is 15% wider, an honest allowance for not knowing `σ`.

```python run
def mean_ci_t(x, level=0.95):
    x = np.asarray(x, float)
    se = x.std(ddof=1) / math.sqrt(len(x))
    q = t_ppf(0.5 + level / 2, len(x) - 1)
    return x.mean() - q * se, x.mean() + q * se, se


print("   n | coverage z-interval | coverage t-interval  (normal data, true mean 0, so the CLT is not the issue)")
rr = np.random.default_rng(34)
for n_ in (5, 10, 30):
    hz = ht = 0
    reps = 3000
    for _ in range(reps):
        s_ = rr.normal(0, 1, n_)
        a, b, _ = mean_ci_z(s_); hz += a <= 0 <= b
        a, b, _ = mean_ci_t(s_); ht += a <= 0 <= b
    print(f"{n_:4d} | {hz / reps:19.3f} | {ht / reps:19.3f}")
```
```text
   n | coverage z-interval | coverage t-interval  (normal data, true mean 0, so the CLT is not the issue)
   5 |               0.882 |               0.953
  10 |               0.925 |               0.954
  30 |               0.939 |               0.948
```

On normal data the t-interval has the promised coverage even for 5 observations, and the z-interval does not. When the data are strongly skewed and the sample small, neither is perfect, and the bootstrap (section 15) is a good second opinion.

### 13.4 Width: precision costs data

The interval's half-width is `z · s/√n`: it falls with the square root of `n` and grows with the spread `s` and the confidence level. Higher confidence means a wider interval. Always.

```python run
sample = np.random.default_rng(35).normal(100, 15, 400)
print("confidence | half-width of the interval for the mean (n = 400, s about 15)")
for level in (0.80, 0.90, 0.95, 0.99, 0.999):
    a, b, _ = mean_ci_z(sample, level)
    print(f"{level:10.3f} | {(b - a) / 2:7.3f}")
print("\nsample size needed for a half-width of 1 at 95% (SD 15):", math.ceil((1.96 * 15 / 1) ** 2))
```
```text
confidence | half-width of the interval for the mean (n = 400, s about 15)
     0.800 |   0.945
     0.900 |   1.213
     0.950 |   1.445
     0.990 |   1.899
     0.999 |   2.426

sample size needed for a half-width of 1 at 95% (SD 15): 865
```

### 13.5 Proportions

For a proportion (the share of users who click), the data are 0/1 and the SD is `√(p(1−p))`: the interval `p̂ ± z √(p̂(1−p̂)/n)`. The **Wilson interval** is better when `p̂` is near 0 or 1 or `n` is small: it never leaves `[0, 1]` and has better coverage.

```python run
def prop_ci_wald(k, n, level=0.95):
    p = k / n; z = normal_ppf(0.5 + level / 2); h = z * math.sqrt(p * (1 - p) / n)
    return p - h, p + h


def prop_ci_wilson(k, n, level=0.95):
    p = k / n; z = normal_ppf(0.5 + level / 2)
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


for k, n_ in ((12, 100), (0, 20), (3, 25)):
    w, ws = prop_ci_wald(k, n_), prop_ci_wilson(k, n_)
    print(f"{k:2d} successes of {n_:3d}: Wald ({w[0]:6.3f}, {w[1]:6.3f}) | Wilson ({ws[0]:6.3f}, {ws[1]:6.3f})")
print("0 of 20: the Wald interval collapses to a single point (width zero), clearly wrong; Wilson still allows rates up to about 16%")
```
```text
12 successes of 100: Wald ( 0.056,  0.184) | Wilson ( 0.070,  0.198)
 0 successes of  20: Wald ( 0.000,  0.000) | Wilson ( 0.000,  0.161)
 3 successes of  25: Wald (-0.007,  0.247) | Wilson ( 0.042,  0.300)
0 of 20: the Wald interval collapses to a single point (width zero), clearly wrong; Wilson still allows rates up to about 16%
```

## 14. Hypothesis tests and p-values

### 14.1 The logic

A **hypothesis test** asks whether data are consistent with a boring explanation, the **null hypothesis** `H₀` ("no effect", "the coin is fair", "the two groups have the same mean"). We choose a **test statistic** that measures how far the data are from `H₀`, and compute the **p-value**:

> the probability, **assuming H₀ is true**, of getting a statistic at least as extreme as the one we observed.

A small p-value says: *if there were really no effect, data like these would be rare.* It is a statement about the data given the hypothesis, **not** the probability that the hypothesis is true (the confusion of section 10).

### 14.2 A first test by hand: is the coin fair?

We toss 100 times and see 61 heads. Under `H₀` (fair coin) the count is binomial(100, 0.5). The two-sided p-value adds the probability of 61 or more heads **and** 39 or fewer (equally extreme in the other direction).

```python run
n_, k_obs = 100, 61
pmf_ = np.array([binom_pmf(k, n_, 0.5) for k in range(n_ + 1)])
p_two = float(pmf_[k_obs:].sum() + pmf_[:n_ - k_obs + 1].sum())
print(f"P(61 or more heads) = {pmf_[k_obs:].sum():.4f}")
print(f"two-sided p-value   = {p_two:.4f}")
if scipy is not None:
    print("scipy.stats.binomtest:", round(float(stats.binomtest(k_obs, n_, 0.5).pvalue), 4))

rng = np.random.default_rng(40)
sim = rng.binomial(n_, 0.5, 1_000_000)
print("simulated:", round(float(np.mean(np.abs(sim - 50) >= 11)), 4), "(share of fair-coin experiments at least as far from 50 as 61)")
```
```text
P(61 or more heads) = 0.0176
two-sided p-value   = 0.0352
scipy.stats.binomtest: 0.0352
simulated: 0.0352 (share of fair-coin experiments at least as far from 50 as 61)
```

A p-value of about 0.035 is below the usual 0.05, so we "reject `H₀` at the 5% level". Understand what that does and does not mean: if the coin were fair, an imbalance this large would happen in about 3.5% of experiments; it does *not* say the coin is biased with probability 96.5%.

### 14.3 The p-value is uniform when nothing is going on

The cleanest way to understand a p-value is to look at its behaviour when `H₀` is **true**. We compare two groups drawn from the *same* distribution, run a test, and repeat many times.

First the test itself. The two-sample **t statistic** (Welch's version, which does not assume equal variances):

`t = (x̄₁ − x̄₂) / √(s₁²/n₁ + s₂²/n₂)`

```python run
def welch_t(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    t = (a.mean() - b.mean()) / math.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))          # Welch-Satterthwaite degrees of freedom
    p = 2 * (1 - t_cdf(abs(t), df))
    return t, df, p


rng = np.random.default_rng(41)
g1, g2 = rng.normal(50, 10, 40), rng.normal(56, 12, 35)
t, df, p = welch_t(g1, g2)
print(f"means {g1.mean():.2f} vs {g2.mean():.2f} | t = {t:.3f} | df = {df:.1f} | p = {p:.4f}")
if scipy is not None:
    ref = stats.ttest_ind(g1, g2, equal_var=False)
    print(f"scipy ttest_ind(equal_var=False): t = {ref.statistic:.3f} | p = {ref.pvalue:.4f}")
```
```text
means 49.83 vs 57.01 | t = -3.166 | df = 70.4 | p = 0.0023
scipy ttest_ind(equal_var=False): t = -3.166 | p = 0.0023
```

Now the experiment under a true `H₀`.

```python run
rng = np.random.default_rng(42)
pvals = np.array([welch_t(rng.normal(0, 1, 30), rng.normal(0, 1, 30))[2] for _ in range(4000)])
print("4000 comparisons of two samples from the SAME population")
print("share of p-values below 0.05:", round(float(np.mean(pvals < 0.05)), 4), "| below 0.01:", round(float(np.mean(pvals < 0.01)), 4), "| below 0.5:", round(float(np.mean(pvals < 0.5)), 4))
hist, _ = np.histogram(pvals, bins=10, range=(0, 1))
print("p-value histogram (10 bins, each should hold about 10%):", np.round(hist / len(pvals), 3))
```
```text
4000 comparisons of two samples from the SAME population
share of p-values below 0.05: 0.0467 | below 0.01: 0.0075 | below 0.5: 0.4983
p-value histogram (10 bins, each should hold about 10%): [0.096 0.106 0.092 0.104 0.1   0.102 0.103 0.1   0.099 0.097]
```

When there is nothing to find, p-values are **uniformly distributed**: 5% fall below 0.05 and 1% below 0.01. That is the meaning of the "5% significance level": it is the false-positive rate you accept. It is built in, not a flaw, and it is why one significant result among many tests means little.

### 14.4 When there is a real effect: power

If the groups truly differ, the test should reject more often. The **power** is the probability of rejecting `H₀` when it is false. It rises with the effect size, the sample size and a lower noise level.

```python run
def power(n, diff, sd=1.0, reps=1500, seed=0):
    r = np.random.default_rng(seed)
    return float(np.mean([welch_t(r.normal(0, sd, n), r.normal(diff, sd, n))[2] < 0.05 for _ in range(reps)]))


print("difference in SDs |  n=10    n=30    n=100")
for diff in (0.0, 0.2, 0.5, 0.8):
    print(f"{diff:17.1f} | " + "  ".join(f"{power(n_, diff):6.3f}" for n_ in (10, 30, 100)))
```
```text
difference in SDs |  n=10    n=30    n=100
              0.0 |  0.046   0.049   0.059
              0.2 |  0.055   0.121   0.292
              0.5 |  0.161   0.467   0.931
              0.8 |  0.367   0.849   1.000
```

The first row is the false-positive rate, about 5% whatever the sample size. A **small effect with a small sample** (0.2 SD with 10 per group) is almost never detected: a non-significant result in such a study says nothing about the effect. The standard target is a power of 0.8; for a 0.5 SD effect the table shows it lies between 30 and 100 per group (the usual formula gives about 64).

### 14.5 Statistical against practical significance

With enough data, any difference, however tiny and unimportant, becomes "significant". The p-value measures *detectability*, not *size*. Report the effect size and an interval.

```python run
rng = np.random.default_rng(43)
for n_ in (100, 10_000, 1_000_000):
    a_ = rng.normal(100.0, 15, n_)
    b_ = rng.normal(100.3, 15, n_)                    # a real but trivial difference: 0.3 on a scale with SD 15 (0.02 SD)
    t, df, p = welch_t(a_, b_)
    print(f"n = {n_:>9,} per group: difference {b_.mean() - a_.mean():6.3f} | p = {p:.2e} | Cohen's d = {(b_.mean() - a_.mean()) / 15:6.3f}")
```
```text
n =       100 per group: difference  1.412 | p = 5.24e-01 | Cohen's d =  0.094
n =    10,000 per group: difference  0.400 | p = 6.02e-02 | Cohen's d =  0.027
n = 1,000,000 per group: difference  0.335 | p = 1.96e-10 | Cohen's d =  0.022
```

A difference of two hundredths of a standard deviation is practically nothing, but with a million per group the p-value is tiny. The effect size (Cohen's d, the difference in standard deviations) is the number to report: 0.2 is small, 0.5 medium, 0.8 large, by common convention.

### 14.6 Many tests, many false alarms

Run 20 tests on pure noise and the chance that at least one gives `p < 0.05` is `1 − 0.95²⁰`, about 64%. The simplest guard is the **Bonferroni correction**: with `m` tests, declare significance only below `0.05/m`.

```python run
print("chance of at least one false positive in m independent tests at 5%:")
for m in (1, 5, 20, 100):
    print(f"  m = {m:3d}: {1 - 0.95 ** m:.3f}")

rng = np.random.default_rng(44)
m_tests, reps = 20, 600
any_raw = any_bonf = 0
for _ in range(reps):
    pv = np.array([welch_t(rng.normal(0, 1, 25), rng.normal(0, 1, 25))[2] for _ in range(m_tests)])
    any_raw += (pv < 0.05).any()
    any_bonf += (pv < 0.05 / m_tests).any()
print(f"\n{m_tests} tests of pure noise, {reps} repeats: at least one 'significant' -> uncorrected {any_raw / reps:.3f} | Bonferroni {any_bonf / reps:.3f}")
```
```text
chance of at least one false positive in m independent tests at 5%:
  m =   1: 0.050
  m =   5: 0.226
  m =  20: 0.642
  m = 100: 0.994

20 tests of pure noise, 600 repeats: at least one 'significant' -> uncorrected 0.658 | Bonferroni 0.053
```

Searching through many columns, subgroups or metrics until something is significant is "p-hacking"; the result is almost certainly noise. State how many comparisons you made, and correct for them.

### 14.7 A test without formulas: the permutation test

If `H₀` says the group labels do not matter, we can **shuffle** the labels and recompute the statistic many times. The shuffled statistics are what the statistic looks like under `H₀`, and the p-value is the share at least as extreme as the real one. No normality is assumed.

```python run
def permutation_test(a, b, stat=lambda x, y: x.mean() - y.mean(), reps=20_000, seed=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(seed)
    obs = stat(a, b)
    pooled = np.concatenate([a, b])
    count = 0
    for _ in range(reps):
        rng.shuffle(pooled)
        count += abs(stat(pooled[:len(a)], pooled[len(a):])) >= abs(obs) - 1e-12
    return obs, (count + 1) / (reps + 1)                       # the +1 counts the observed arrangement itself


obs, p_perm = permutation_test(g1, g2)
print(f"difference in means {obs:.3f} | permutation p = {p_perm:.4f} | Welch p = {welch_t(g1, g2)[2]:.4f}")

skew_a = np.random.default_rng(45).exponential(10, 25)
skew_b = np.random.default_rng(46).exponential(16, 25)
obs, p_med = permutation_test(skew_a, skew_b, stat=lambda x, y: np.median(x) - np.median(y))
print(f"\nskewed data, difference in MEDIANS {obs:.3f} | permutation p = {p_med:.4f}   (no textbook formula needed)")
```
```text
difference in means -7.182 | permutation p = 0.0021 | Welch p = 0.0023

skewed data, difference in MEDIANS -1.045 | permutation p = 0.6818   (no textbook formula needed)
```

The permutation test works for any statistic (a median, a ratio, a correlation) and is the better choice for small or odd samples. The ideas of this section and of the next belong together: **resample to see what chance can do.**

## 15. The bootstrap

### 15.1 The idea

We want the sampling distribution of a statistic but have only one sample. The bootstrap's trick: treat the sample as if it were the population, and **resample from it with replacement**, drawing `n` values from a sample of `n`. Some values appear twice or more, others not at all. Compute the statistic on each resample; the spread of those values approximates the sampling distribution.

```python run
rng = np.random.default_rng(50)
sample = rng.choice(population, 80)
print("the sample: n =", len(sample), "| mean", round(sample.mean()), "| median", round(float(np.median(sample))))

resample = rng.choice(sample, size=len(sample), replace=True)
unique_share = len(np.unique(resample)) / len(sample)
print(f"one resample: {len(np.unique(resample))} distinct values out of {len(sample)} drawn ({unique_share:.0%}); theory: about 1 - 1/e = {1 - 1 / math.e:.0%}")

def bootstrap_stats(x, stat, reps=10_000, seed=0):
    r = np.random.default_rng(seed)
    idx = r.integers(0, len(x), size=(reps, len(x)))           # all resamples at once
    return np.array([stat(x[i]) for i in idx])


boot_means = bootstrap_stats(sample, np.mean)
print(f"bootstrap SE of the mean: {boot_means.std():,.0f} | formula s/sqrt(n): {sample.std(ddof=1) / math.sqrt(len(sample)):,.0f}")
```
```text
the sample: n = 80 | mean 45064 | median 31850
one resample: 51 distinct values out of 80 drawn (64%); theory: about 1 - 1/e = 63%
bootstrap SE of the mean: 4,255 | formula s/sqrt(n): 4,290
```

For the mean the bootstrap reproduces the textbook standard error, which is reassuring. Its value is that the same code works for statistics with no formula.

### 15.2 The percentile interval

The 2.5th and 97.5th percentiles of the bootstrap statistics form a 95% **percentile interval**.

```python run
def bootstrap_ci(x, stat=np.mean, level=0.95, reps=10_000, seed=0):
    b = bootstrap_stats(np.asarray(x, float), stat, reps, seed)
    a = (1 - level) / 2
    return float(np.quantile(b, a)), float(np.quantile(b, 1 - a)), b


for name, stat in (("mean", np.mean), ("median", np.median), ("90th percentile", lambda v: np.quantile(v, 0.9)), ("coefficient of variation", lambda v: v.std(ddof=1) / v.mean())):
    lo, hi, _ = bootstrap_ci(sample, stat)
    truth = stat(population)
    print(f"{name:25} estimate {stat(sample):12,.3f} | 95% CI ({lo:12,.3f}, {hi:12,.3f}) | population value {truth:12,.3f} | inside: {lo <= truth <= hi}")
```
```text
mean                      estimate   45,063.615 | 95% CI (  37,317.660,   54,015.338) | population value   49,978.481 | inside: True
median                    estimate   31,850.258 | 95% CI (  25,992.548,   44,903.816) | population value   36,236.889 | inside: True
90th percentile           estimate   87,069.928 | 95% CI (  68,266.188,  116,367.903) | population value  101,440.899 | inside: True
coefficient of variation  estimate        0.851 | 95% CI (       0.664,        1.019) | population value        0.946 | inside: True
```

### 15.3 How to interpret it

The bootstrap interval says: *the statistic varied over about this range in resamples of my data, so a similarly noisy procedure applied to the true population would plausibly land in a range of that width.* The **95% is a property of the procedure** (section 13.2), not a 95% probability that the one interval contains the truth. And the interval describes **sampling noise only**: it cannot repair bias in how the sample was collected. If the 80 incomes came from a biased survey, the interval is a precise statement about the wrong population.

Does the procedure really cover about 95%? Test it, as before.

```python run
def boot_coverage(n, stat, truth, reps=400, boot_reps=1000, seed=0):
    r = np.random.default_rng(seed)
    hit = 0
    for i in range(reps):
        x = r.choice(population, n)
        lo, hi, _ = bootstrap_ci(x, stat, reps=boot_reps, seed=i)
        hit += lo <= truth <= hi
    return hit / reps


t0 = time.perf_counter()
print("   n | coverage, mean | coverage, median   (400 experiments each, 95% nominal)")
for n_ in (20, 80, 300):
    print(f"{n_:4d} | {boot_coverage(n_, np.mean, mu_pop):14.3f} | {boot_coverage(n_, np.median, np.median(population)):16.3f}")
print(f"({time.perf_counter() - t0:.0f} s, machine-specific)")
```
```text
   n | coverage, mean | coverage, median   (400 experiments each, 95% nominal)
  20 |          0.845 |            0.922
  80 |          0.927 |            0.960
 300 |          0.953 |            0.938
(14 s, machine-specific)
```

The coverage of the mean approaches 95% as the sample grows but falls short in small samples of skewed data (the median column wobbles around 0.92 to 0.96; with 400 experiments each, a coverage figure is only accurate to about one percentage point): the bootstrap is not magic, and it inherits the poor picture that a small sample gives of the population. It is best with at least a few dozen observations.

### 15.4 Bootstrapping a difference and a correlation

The bootstrap handles comparisons the same way: resample **within each group** (for two groups) or resample **whole rows** (for pairs, to keep the pairing).

```python run
rng = np.random.default_rng(51)
a_ = rng.exponential(10, 60)
b_ = rng.exponential(14, 60)
diffs = []
for _ in range(10_000):
    diffs.append(np.median(rng.choice(b_, 60)) - np.median(rng.choice(a_, 60)))
lo, hi = np.quantile(diffs, [0.025, 0.975])
print(f"difference in medians: observed {np.median(b_) - np.median(a_):.2f} | 95% bootstrap CI ({lo:.2f}, {hi:.2f}) | contains zero: {lo <= 0 <= hi}")

x_ = rng.normal(size=70)
y_ = 0.4 * x_ + rng.normal(size=70)
rows = np.column_stack([x_, y_])
corrs = []
for _ in range(10_000):
    r_ = rows[rng.integers(0, 70, 70)]                         # resample whole ROWS to keep each (x, y) pair together
    corrs.append(np.corrcoef(r_[:, 0], r_[:, 1])[0, 1])
lo, hi = np.quantile(corrs, [0.025, 0.975])
print(f"correlation: observed {np.corrcoef(x_, y_)[0, 1]:.3f} | 95% bootstrap CI ({lo:.3f}, {hi:.3f}) | true value {0.4 / math.sqrt(1.16):.3f}")
```
```text
difference in medians: observed 3.49 | 95% bootstrap CI (-0.78, 6.41) | contains zero: True
correlation: observed 0.513 | 95% bootstrap CI (0.302, 0.671) | true value 0.371
```

### 15.5 When the bootstrap fails

The bootstrap needs a statistic that changes smoothly with the data. It fails for the **maximum** (or minimum): a resample can never exceed the sample's own maximum, so the bootstrap distribution piles up at the observed maximum and badly understates the uncertainty.

```python run
rng = np.random.default_rng(52)
sample_u = rng.uniform(0, 100, 50)                              # the true maximum is 100
boot_max = bootstrap_stats(sample_u, np.max, reps=5000)
print(f"observed maximum {sample_u.max():.2f} | true population maximum 100")
print(f"share of bootstrap maxima exactly equal to the observed maximum: {np.mean(boot_max == sample_u.max()):.2%} (theory about 1 - 1/e = {1 - 1 / math.e:.0%})")
print(f"bootstrap 95% interval: ({np.quantile(boot_max, 0.025):.2f}, {np.quantile(boot_max, 0.975):.2f}) -> the true value 100 is outside it")
```
```text
observed maximum 99.72 | true population maximum 100
share of bootstrap maxima exactly equal to the observed maximum: 63.64% (theory about 1 - 1/e = 63%)
bootstrap 95% interval: (96.83, 99.72) -> the true value 100 is outside it
```

It also fails for **heavy-tailed** data with infinite variance, for **dependent** data (a time series needs a block bootstrap that resamples chunks), and for tiny samples.

> **Predict the output.** A bootstrap with 10,000 resamples gives a 95% interval for a median. You rerun with a different seed and the interval limits change in the third digit. Is something wrong? What would you change to make the limits more stable?

<details><summary>Answer</summary>

Nothing is wrong. The bootstrap uses random resamples, so the limits carry *Monte Carlo* noise on top of the sampling uncertainty of the data. More resamples reduce the Monte Carlo noise (not the sampling uncertainty): 10,000 is plenty for a 95% interval, and 1,000 may be marginal. Fix the seed so that a reported result can be reproduced.

```python run
for seed in (1, 2, 3):
    lo, hi, _ = bootstrap_ci(sample, np.median, reps=10_000, seed=seed)
    print(f"seed {seed}: ({lo:,.0f}, {hi:,.0f})")
```
```text
seed 1: (26,107, 44,904)
seed 2: (26,107, 44,904)
seed 3: (25,993, 44,904)
```

</details>

## 16. Project: a statistics and linear-algebra toolkit

### 16.1 The brief

Write one module, `mathkit.py`, that gathers what this chapter built, **with NumPy only** (and `math`), plus a test file that checks every function against NumPy or SciPy, or against a result worked out by hand. Why a toolkit? Writing a function is not understanding it, but a function that you have written, tested, and used on three problems is yours for life.

| Group | Functions |
|---|---|
| Linear algebra | `norm`, `cosine_similarity`, `project`, `solve` (Gaussian elimination), `least_squares`, `power_iteration`, `pca` (via SVD), `low_rank` |
| Calculus | `num_grad`, `grad_check`, `gradient_descent` |
| Probability | `bayes_posterior`, `normal_cdf`, `normal_ppf`, `binom_pmf` |
| Inference | `mean_ci`, `welch_t`, `permutation_test`, `bootstrap_ci` |

### 16.2 The module

The whole file, written to a temporary folder here, so you can see it is real code that imports and runs. Everything is composed of the pieces above; the tidy versions below are what you would keep.

```python run
tmp = pathlib.Path(tempfile.mkdtemp(prefix="mathkit_"))
MATHKIT = r'''"""mathkit: linear algebra, calculus and inference from scratch with NumPy."""
import math
import numpy as np

# ---------- linear algebra ----------
def norm(v):
    v = np.asarray(v, dtype=float)
    return math.sqrt(float(np.sum(v * v)))

def cosine_similarity(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float(x @ y) / (norm(x) * norm(y))

def project(a, d):
    a, d = np.asarray(a, float), np.asarray(d, float)
    return (a @ d) / (d @ d) * d

def solve(A, b):
    """Gaussian elimination with partial pivoting."""
    A = np.array(A, dtype=float); b = np.array(b, dtype=float); n = len(b)
    for col in range(n):
        piv = col + int(np.argmax(np.abs(A[col:, col])))
        if abs(A[piv, col]) < 1e-12:
            raise np.linalg.LinAlgError("singular matrix")
        A[[col, piv]], b[[col, piv]] = A[[piv, col]].copy(), b[[piv, col]].copy()
        for row in range(col + 1, n):
            f = A[row, col] / A[col, col]
            A[row, col:] -= f * A[col, col:]
            b[row] -= f * b[col]
    x = np.zeros(n)
    for row in range(n - 1, -1, -1):
        x[row] = (b[row] - A[row, row + 1:] @ x[row + 1:]) / A[row, row]
    return x

def least_squares(A, b):
    """Minimum-norm least squares through the SVD (works for rank-deficient A)."""
    U, s, Vt = np.linalg.svd(np.asarray(A, float), full_matrices=False)
    s_inv = np.where(s > 1e-10 * s.max(), 1.0 / np.where(s == 0, 1.0, s), 0.0)
    return (Vt.T * s_inv) @ (U.T @ np.asarray(b, float))

def power_iteration(A, steps=500, seed=0):
    v = np.random.default_rng(seed).normal(size=A.shape[0]); v /= np.linalg.norm(v)
    for _ in range(steps):
        w = A @ v; v = w / np.linalg.norm(w)
    return float(v @ A @ v), v

def pca(X, k):
    """Returns (scores, components, explained_variance) from the SVD of the centred data."""
    Xc = np.asarray(X, float) - np.mean(X, axis=0)
    U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
    return Xc @ Vt[:k].T, Vt[:k], (s ** 2 / (len(Xc) - 1))[:k]

def low_rank(M, k):
    U, s, Vt = np.linalg.svd(M, full_matrices=False)
    return U[:, :k] @ np.diag(s[:k]) @ Vt[:k]

# ---------- calculus ----------
def num_grad(f, p, h=1e-5):
    p = np.asarray(p, dtype=float); g = np.zeros_like(p)
    for i in range(len(p)):
        step = np.zeros_like(p); step[i] = h
        g[i] = (f(p + step) - f(p - step)) / (2 * h)
    return g

def grad_check(f, grad, p, h=1e-5):
    a, n_ = np.asarray(grad(p), float), num_grad(f, p, h)
    return float(np.linalg.norm(a - n_) / max(np.linalg.norm(a) + np.linalg.norm(n_), 1e-12))

def gradient_descent(grad, w0, lr, steps):
    w = np.array(w0, dtype=float)
    for _ in range(steps):
        w = w - lr * grad(w)
    return w

# ---------- probability ----------
def bayes_posterior(prior, sensitivity, false_positive_rate):
    return sensitivity * prior / (sensitivity * prior + false_positive_rate * (1 - prior))

def normal_cdf(x, mu=0.0, sigma=1.0):
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2.0))))

def normal_ppf(q, mu=0.0, sigma=1.0):
    lo, hi = -40.0, 40.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if normal_cdf(mid) < q else (lo, mid)
    return mu + sigma * (lo + hi) / 2

def binom_pmf(k, n, p):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)

# ---------- inference ----------
def t_cdf(x, df, steps=2001):
    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
    grid = np.linspace(0.0, abs(x), steps)
    area = np.trapezoid(c * (1 + grid ** 2 / df) ** (-(df + 1) / 2), grid)
    return 0.5 + math.copysign(area, x)

def t_ppf(q, df):
    lo, hi = -200.0, 200.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if t_cdf(mid, df) < q else (lo, mid)
    return (lo + hi) / 2

def mean_ci(x, level=0.95):
    x = np.asarray(x, float); se = x.std(ddof=1) / math.sqrt(len(x))
    q = t_ppf(0.5 + level / 2, len(x) - 1)
    return float(x.mean() - q * se), float(x.mean() + q * se)

def welch_t(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    t = (a.mean() - b.mean()) / math.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    return t, df, 2 * (1 - t_cdf(abs(t), df))

def permutation_test(a, b, stat=lambda x, y: x.mean() - y.mean(), reps=10000, seed=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    rng = np.random.default_rng(seed); obs = stat(a, b); pooled = np.concatenate([a, b]); count = 0
    for _ in range(reps):
        rng.shuffle(pooled)
        count += abs(stat(pooled[:len(a)], pooled[len(a):])) >= abs(obs) - 1e-12
    return obs, (count + 1) / (reps + 1)

def bootstrap_ci(x, stat=np.mean, level=0.95, reps=5000, seed=0):
    x = np.asarray(x, float); rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(reps, len(x)))
    b = np.array([stat(x[i]) for i in idx]); a = (1 - level) / 2
    return float(np.quantile(b, a)), float(np.quantile(b, 1 - a))
'''
(tmp / "mathkit.py").write_text(MATHKIT)
print("written:", (tmp / "mathkit.py").name, "|", len(MATHKIT.splitlines()), "lines |", sum(l.startswith("def ") for l in MATHKIT.splitlines()), "functions")
sys.path.insert(0, str(tmp))
import mathkit as mk
print("imported:", [n for n in dir(mk) if not n.startswith("_") and callable(getattr(mk, n)) and getattr(getattr(mk, n), "__module__", "") == "mathkit"][:6], "...")
```
```text
written: mathkit.py | 130 lines | 21 functions
imported: ['bayes_posterior', 'binom_pmf', 'bootstrap_ci', 'cosine_similarity', 'grad_check', 'gradient_descent'] ...
```

### 16.3 The tests

Each test compares the function with a trusted reference. A test that cannot fail is worthless, so the last block breaks a function on purpose to confirm the suite notices.

```python run
rng = np.random.default_rng(60)
Ar = rng.normal(size=(5, 5)); br = rng.normal(size=5)
Xd = rng.normal(size=(300, 4)) @ rng.normal(size=(4, 4))
Sym = Ar @ Ar.T
lam_ref = np.linalg.eigvalsh(Sym).max()
xx, yy = rng.normal(size=40), rng.normal(size=40) + 0.3


def tests(m):
    T = {}
    T["norm"] = lambda: np.isclose(m.norm([3, 4, 12]), 13.0)
    T["cosine_similarity"] = lambda: np.isclose(m.cosine_similarity([1, 0], [1, 1]), 1 / math.sqrt(2))
    T["project"] = lambda: np.allclose(m.project([3, 4], [1, 0]), [3, 0]) and np.isclose((np.array([3, 4]) - m.project([3, 4], [1, 1])) @ [1, 1], 0)
    T["solve"] = lambda: np.allclose(m.solve(Ar, br), np.linalg.solve(Ar, br))
    T["least_squares (full rank)"] = lambda: np.allclose(m.least_squares(Xd, Xd @ [1, 2, 3, 4]), [1, 2, 3, 4])
    T["least_squares (rank deficient)"] = lambda: np.allclose(m.least_squares(np.c_[np.ones(10), np.arange(10.0), 2 * np.arange(10.0)], 3 + 0.5 * np.arange(10.0)), [3, 0.1, 0.2])
    T["power_iteration"] = lambda: np.isclose(m.power_iteration(Sym)[0], lam_ref)
    T["pca variances"] = lambda: np.allclose(m.pca(Xd, 4)[2], np.sort(np.linalg.eigvalsh(np.cov(Xd, rowvar=False)))[::-1])
    T["low_rank (Eckart-Young error)"] = lambda: np.isclose(np.linalg.norm(Xd - m.low_rank(Xd, 2)), math.sqrt(float((np.linalg.svd(Xd, compute_uv=False)[2:] ** 2).sum())))
    T["num_grad"] = lambda: np.allclose(m.num_grad(lambda p: p[0] ** 2 * p[1] + 3 * p[1], [2.0, 3.0]), [12, 7], atol=1e-6)
    T["grad_check flags a bug"] = lambda: m.grad_check(lambda p: float(p @ p), lambda p: 2 * p, np.array([1.0, 2.0])) < 1e-6 and m.grad_check(lambda p: float(p @ p), lambda p: 3 * p, np.array([1.0, 2.0])) > 0.1
    T["gradient_descent"] = lambda: np.allclose(m.gradient_descent(lambda w: 2 * (w - np.array([3.0, -1.0])), [0, 0], 0.1, 200), [3, -1])
    T["bayes_posterior"] = lambda: np.isclose(m.bayes_posterior(0.01, 0.99, 0.05), 99 / 594)
    T["normal_cdf / ppf round trip"] = lambda: np.isclose(m.normal_cdf(m.normal_ppf(0.975)), 0.975) and np.isclose(m.normal_ppf(0.975), 1.959964, atol=1e-5)
    T["binom_pmf sums to 1 and has mean np"] = lambda: np.isclose(sum(m.binom_pmf(k, 12, 0.3) for k in range(13)), 1) and np.isclose(sum(k * m.binom_pmf(k, 12, 0.3) for k in range(13)), 3.6)
    T["t_ppf vs known values"] = lambda: np.isclose(m.t_ppf(0.975, 9), 2.262157, atol=1e-4) and np.isclose(m.t_ppf(0.975, 29), 2.045230, atol=1e-4)
    T["mean_ci contains the mean"] = lambda: m.mean_ci(xx)[0] < xx.mean() < m.mean_ci(xx)[1]
    T["welch_t"] = lambda: (lambda r: np.isclose(m.welch_t(xx, yy)[0], r.statistic) and np.isclose(m.welch_t(xx, yy)[2], r.pvalue, atol=1e-4))(stats.ttest_ind(xx, yy, equal_var=False)) if scipy is not None else True
    T["permutation_test gives a p-value in (0, 1]"] = lambda: 0 < m.permutation_test(xx, yy, reps=4000)[1] <= 1 and m.permutation_test(xx, xx + 5, reps=2000)[1] < 0.01
    T["bootstrap_ci brackets the estimate"] = lambda: (lambda lo, hi: lo < np.median(xx) < hi)(*m.bootstrap_ci(xx, np.median, reps=2000))
    out = {}
    for name, fn in T.items():
        try:
            out[name] = bool(fn())
        except Exception as e:
            out[name] = f"error: {type(e).__name__}"
    return out


res = tests(mk)
for name, ok in res.items():
    print(f"{'PASS' if ok is True else 'FAIL'}  {name}" + ("" if ok is True else f"  ({ok})"))
print(f"\n{sum(v is True for v in res.values())} of {len(res)} tests pass")
```
```text
PASS  norm
PASS  cosine_similarity
PASS  project
PASS  solve
PASS  least_squares (full rank)
PASS  least_squares (rank deficient)
PASS  power_iteration
PASS  pca variances
PASS  low_rank (Eckart-Young error)
PASS  num_grad
PASS  grad_check flags a bug
PASS  gradient_descent
PASS  bayes_posterior
PASS  normal_cdf / ppf round trip
PASS  binom_pmf sums to 1 and has mean np
PASS  t_ppf vs known values
PASS  mean_ci contains the mean
PASS  welch_t
PASS  permutation_test gives a p-value in (0, 1]
PASS  bootstrap_ci brackets the estimate

20 of 20 tests pass
```

The tests pass. Now the important test of the tests: put a bug into a function (a classic one: dividing by `n` instead of `n − 1` inside a standard error, a wrong sign in the gradient, a missing square root in the norm) and check that the suite notices.

```python run
import types

def _ascend(grad, w0, lr, steps):
    w = np.array(w0, dtype=float)
    for _ in range(steps):
        w = w + lr * grad(w)                       # the sign error
    return w


def with_bug(name, replacement):
    m = types.ModuleType("mathkit_bugged")
    m.__dict__.update({k: v for k, v in vars(mk).items() if not k.startswith("__")})
    m.__dict__[name] = replacement
    return m


bugs = {
    "norm without the square root": ("norm", lambda v: float(np.sum(np.asarray(v, float) ** 2))),
    "cosine using dot product only": ("cosine_similarity", lambda x, y: float(np.asarray(x, float) @ np.asarray(y, float))),
    "bayes ignoring the false positives": ("bayes_posterior", lambda p, s, f: s * p / (s * p + f * p)),
    "normal_cdf with sqrt(2) forgotten": ("normal_cdf", lambda x, mu=0.0, sigma=1.0: 0.5 * (1.0 + math.erf((x - mu) / sigma))),
    "gradient descent that ascends": ("gradient_descent", lambda grad, w0, lr, steps: _ascend(grad, w0, lr, steps)),
}
for label, (fname, fn) in bugs.items():
    r = tests(with_bug(fname, fn))
    failed = [k for k, v in r.items() if v is not True]
    print(f"{label:38} -> caught by {len(failed)} test(s): {failed[:3]}")
```
```text
norm without the square root           -> caught by 1 test(s): ['norm']
cosine using dot product only          -> caught by 1 test(s): ['cosine_similarity']
bayes ignoring the false positives     -> caught by 1 test(s): ['bayes_posterior']
normal_cdf with sqrt(2) forgotten      -> caught by 1 test(s): ['normal_cdf / ppf round trip']
gradient descent that ascends          -> caught by 1 test(s): ['gradient_descent']
```

Every injected bug is caught by at least one test. If a mutation survives, a test is missing. This habit (mutation testing) is how you find out whether a test suite protects you, and it is exactly the property you want in numerical code, where a bug rarely crashes: it quietly gives a wrong number.

### 16.4 Using the toolkit on a small problem

A last demonstration that the pieces compose: a regression fitted three ways (solve, least-squares, gradient descent), a PCA, and a bootstrap interval for the slope, all through `mathkit`.

```python run
rng = np.random.default_rng(61)
n = 150
Xp = np.column_stack([np.ones(n), rng.uniform(0, 10, n)])
yp = 4.0 + 2.5 * Xp[:, 1] + rng.normal(0, 3, n)

w_solve = mk.solve(Xp.T @ Xp, Xp.T @ yp)
w_ls = mk.least_squares(Xp, yp)
Xs_ = np.column_stack([np.ones(n), (Xp[:, 1] - Xp[:, 1].mean()) / Xp[:, 1].std()])
grad = lambda w: 2.0 / n * Xs_.T @ (Xs_ @ w - yp)
loss = lambda w: float(np.mean((Xs_ @ w - yp) ** 2))
print("gradient check of the loss gradient:", f"{mk.grad_check(loss, grad, np.array([1.0, 1.0])):.1e}")
w_gd = mk.gradient_descent(grad, [0, 0], 0.2, 300)
slope_gd = w_gd[1] / Xp[:, 1].std()                             # undo the standardisation to compare slopes
print(f"slope by normal equations {w_solve[1]:.4f} | by least_squares {w_ls[1]:.4f} | by gradient descent {slope_gd:.4f} (true 2.5)")

boot_slopes = []
for i in range(3000):
    idx = rng.integers(0, n, n)
    boot_slopes.append(mk.least_squares(Xp[idx], yp[idx])[1])
lo, hi = np.quantile(boot_slopes, [0.025, 0.975])
print(f"bootstrap 95% CI for the slope: ({lo:.3f}, {hi:.3f}) | contains the true 2.5: {lo <= 2.5 <= hi}")
scores, comps, ev = mk.pca(np.column_stack([Xp[:, 1], yp]), 2)
print("PCA of (x, y): explained variance", np.round(ev, 2), "| first component", np.round(comps[0], 3), "(the direction of the cloud)")
```
```text
gradient check of the loss gradient: 7.8e-11
slope by normal equations 2.4989 | by least_squares 2.4989 | by gradient descent 2.4989 (true 2.5)
bootstrap 95% CI for the slope: (2.312, 2.687) | contains the true 2.5: True
PCA of (x, y): explained variance [75.04  1.31] | first component [0.324 0.946] (the direction of the cloud)
```

### 16.5 What to hand in, for your own version

1. `mathkit.py`, NumPy only, every function with a docstring that states its input shapes.
2. A test file that compares each function with NumPy/SciPy or a hand-worked case, including **edge cases**: a singular matrix, a constant column, `n = 1`, an empty array.
3. At least three **mutation checks** like the ones above, proving the tests can fail.
4. A one-page note: for each of the three methods that surprised you (condition number, base rate, bootstrap failure), a small experiment and what it taught.
5. Extend it: add the Wilson interval, the Mann-Whitney U test or a k-means loop, each with its own tests.

## 17. Common traps

| Trap | What happens | Fix |
|---|---|---|
| `np.cov` on an `(n, p)` matrix without `rowvar=False` | an `n × n` covariance of the rows | `rowvar=False` (2.4) |
| Euclidean distance on unscaled columns | the largest-scale column decides everything | standardise first (1.4) |
| Inverting a matrix to solve a system | slower and less accurate | `np.linalg.solve` or `lstsq` (3.4) |
| Normal equations on collinear or ill-conditioned `X` | a singular matrix, or garbage coefficients | check the rank and condition number; use `lstsq`/SVD (3.2, 3.3) |
| Using `eig` on a symmetric matrix | complex dtype, unsorted values | `eigh` (4.3) |
| Reading eigenvector signs as meaningful | `v` and `−v` are the same direction | compare up to a sign |
| A hand-derived gradient never checked | training stalls and nobody knows why | `grad_check` against `num_grad` (7.4) |
| A numerical derivative with `h` too small | rounding noise dominates | `h` about 1e-5 with a central difference (6.2) |
| Learning rate above `2/λ_max` | the loss grows to infinity or NaN | lower the rate; scale the features (8.2, 8.4) |
| Unscaled features in gradient descent | extremely slow, or divergence | standardise (8.4) |
| Treating `P(A\|B)` as `P(B\|A)` | wildly wrong risk estimates | Bayes' theorem with the base rate (10) |
| Ignoring the base rate for a rare event | a "99% accurate" alert that is mostly false alarms | count people (10.2) |
| Assuming independence | variances that do not add; double-counted evidence | check it (9.2, 11.2) |
| Dividing by `n` for a sample variance | an estimate that is systematically too small | `ddof=1` (13.1) |
| Reading "95%" as "95% probability for this interval" | an overconfident statement | it describes the procedure (13.2) |
| z-interval on a small sample | coverage below 95% | the t-interval, or the bootstrap (13.3) |
| p-value read as the probability that `H₀` is true | wrong conclusions | the p-value assumes `H₀` (14.1) |
| Significant therefore important | trivial effects celebrated | report effect size and interval (14.5) |
| Many tests, one reported | false positives | count the tests, correct them (14.6) |
| Bootstrapping the maximum, or dependent data | intervals that are too narrow | other methods; block bootstrap (15.5) |
| Random results that change on every run | irreproducible reports | `default_rng(seed)` always |

## 18. Summary

- **Vectors** are rows of data with a geometry: the **norm** is length, the **dot product** measures alignment, **cosine similarity** compares direction, and **projection** is the part of one vector along another. Distances depend on scale, so standardise first.
- **Matrices** are tables and linear maps; the product combines inner dimensions, is not commutative, and `XᵀX` is symmetric. The **covariance matrix** is `XcᵀXc/(n−1)`.
- A **linear system** `Ax = b` has a unique solution only for a full-rank matrix. **Rank**, the **determinant** and the **condition number** tell you when a problem is singular or nearly so; **least squares** projects `b` onto the columns of `A`, and its normal equations are the formula behind linear regression. Prefer `solve`, `lstsq` and `pinv` to forming an inverse.
- **Eigenvectors** are directions a matrix only stretches; for a symmetric matrix they are orthogonal. The eigenvectors of the covariance matrix are the **principal components**. The **SVD** `X = UΣVᵀ` exists for every matrix, gives PCA more accurately, gives the best low-rank approximation (which removes noise) and the pseudo-inverse.
- A **derivative** is a limit of slopes, found by rules (power, product, chain) and verified numerically with a central difference. A **gradient** collects partial derivatives and points uphill. The gradients of squared error, `(2/n)Xᵀ(Xw − y)`, and of cross-entropy, `(1/n)Xᵀ(p − y)`, are derived by the chain rule. Always **gradient-check** a hand-derived formula.
- **Gradient descent** steps against the gradient; the learning rate must stay below `2/λ_max`, and scaling features improves the conditioning. Convex losses have one minimum; stochastic descent trades exactness for cheap steps.
- **Probability** is a long-run frequency: complement, union, independence and conditioning follow from counting. **Bayes' theorem** reverses a conditional and exposes the **base-rate fallacy**; evidence updates a prior through the likelihood ratio.
- **Distributions** give shape to chance: the binomial (counts of successes), Poisson (counts of rare events), uniform, exponential (waits) and normal. Expectation is linear; variances of independent sums add; the standard deviation of a mean is `σ/√n`. The **law of large numbers** and the **central limit theorem** are why averages are stable and approximately normal.
- A **confidence interval** is a procedure that captures the truth in a stated share of repetitions; the **t-interval** corrects for estimating `s`; width falls only as `1/√n` and rises with confidence. A **p-value** is the probability of data at least this extreme if `H₀` were true: uniform when `H₀` holds, not the probability that `H₀` is true, and not a measure of size. Power, effect size, multiple testing and the **permutation test** complete the picture.
- The **bootstrap** resamples the sample with replacement to see the sampling distribution of any statistic and to form a percentile interval. Its 95% is a property of the procedure; it describes sampling noise, not bias; it fails for extremes and dependent data.

You reached the two outcomes of this chapter: you can **compute a gradient by hand and verify it numerically** (sections 6-8 and the `grad_check` that rejected three deliberately wrong formulas), and you can **run a bootstrap and interpret its interval** (section 15, with its coverage measured and its failure shown). The toolkit of section 16 carries both into ds.02, where regression, logistic regression and their diagnostics are built on exactly these pieces.
