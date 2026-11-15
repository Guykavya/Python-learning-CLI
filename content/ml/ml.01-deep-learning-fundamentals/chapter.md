# Chapter 1 (ML): Deep learning fundamentals

Every model so far in this course learned a function from data by choosing parameters. A **neural network** does the same thing, with one difference that changes everything: the function is built from many small, identical, differentiable pieces stacked in layers, and the parameters of *all* the layers are tuned together by following the gradient of one loss. That recipe (a stack of simple differentiable layers, a loss, and gradient descent) powers image recognition, speech, translation and the language models you will meet later in this track.

The recipe is short, and every part of it can be written in a few lines of NumPy. That is what this chapter does. You will build a neuron and a layer, learn the **activation functions** and **loss functions** that make them useful, implement the **optimisers** that train them, derive **backpropagation** by hand and prove it right with a numerical gradient check, write a **tiny automatic-differentiation engine** that does backpropagation for you, and then study what makes deep networks hard to train: **initialisation**, **regularisation** (weight decay, early stopping, dropout) and **batch normalisation**. By the end you reach the syllabus outcome: **implement backpropagation for a small network by hand**, and you will have built the project: a neural-network library in NumPy, tested against PyTorch.

Prerequisites: ds.06 (logistic regression and gradient descent, which are a one-neuron network), ds.01 (derivatives, the chain rule, matrices), ds.03 (overfitting, regularisation, validation). PyTorch is the subject of ml.02; here it appears only as an **independent referee** that checks our gradients and updates.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, scikit-learn's bundled datasets (`make_moons`, `make_circles`, `load_digits`) and, as a referee only, PyTorch (CPU build; if it is missing, the referee lines are skipped and everything else still runs). Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, json, itertools, warnings, platform
import numpy as np
import pandas as pd
import sklearn
from sklearn import datasets, linear_model, model_selection, preprocessing, metrics

try:
    import torch
    torch.set_default_dtype(torch.float64)                 # compare with NumPy in double precision
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

np.set_printoptions(precision=5, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.float_format", lambda v: f"{v:,.5f}")
warnings.filterwarnings("ignore")
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__)
print("sklearn", sklearn.__version__)
print("torch  ", torch.__version__ if HAS_TORCH else "not installed (referee checks are skipped)")
```
```text
python  3.14.4
numpy   2.5.4
sklearn 1.9.1
torch   2.15.0+cpu
```

## Table of contents

1. [From a linear model to a network](#1-from-a-linear-model-to-a-network)
2. [Neurons, layers and the forward pass](#2-neurons-layers-and-the-forward-pass)
3. [Activation functions](#3-activation-functions)
4. [Loss functions](#4-loss-functions)
5. [Gradient descent and optimisers](#5-gradient-descent-and-optimisers)
6. [Backpropagation by hand](#6-backpropagation-by-hand)
7. [A tiny autograd engine](#7-a-tiny-autograd-engine)
8. [Training a network end to end](#8-training-a-network-end-to-end)
9. [Initialisation](#9-initialisation)
10. [Regularisation: weight decay, early stopping and dropout](#10-regularisation-weight-decay-early-stopping-and-dropout)
11. [Batch normalisation](#11-batch-normalisation)
12. [Debugging a network that will not learn](#12-debugging-a-network-that-will-not-learn)
13. [Project: a neural-network library in NumPy](#13-project-a-neural-network-library-in-numpy)
14. [Common traps](#14-common-traps)
15. [Summary](#15-summary)

## 1. From a linear model to a network

### 1.1 What a linear model cannot do

Logistic regression draws one straight line (a hyperplane) between the classes. That fails the moment the classes are not separated by a straight line. The smallest example is **XOR**: the output is 1 when exactly one of the two inputs is 1.

```python run
X_xor = np.array([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=float)
y_xor = np.array([0, 1, 1, 0])
lr = linear_model.LogisticRegression(C=1e6).fit(X_xor, y_xor)
print("logistic regression predictions:", lr.predict(X_xor), "| truth:", y_xor, "| accuracy:", lr.score(X_xor, y_xor))
```
```text
logistic regression predictions: [0 0 0 0] | truth: [0 1 1 0] | accuracy: 0.5
```

No line puts (0,0) and (1,1) on one side and (0,1) and (1,0) on the other. A model with two **hidden units** solves it exactly. The first unit fires when *at least one* input is on, the second when *both* are on; the output says "first but not second". We write the weights by hand:

```python run
W1 = np.array([[1.0, 1.0],            # column 0 = unit "x1 OR x2", column 1 = unit "x1 AND x2"
               [1.0, 1.0]])
b1 = np.array([-0.5, -1.5])
w2 = np.array([1.0, -2.0])
b2 = -0.5
step = lambda z: (z > 0).astype(float)
hidden = step(X_xor @ W1 + b1)
out = step(hidden @ w2 + b2)
print("hidden units (OR, AND):"); print(hidden)
print("output:", out.astype(int), "| truth:", y_xor, "| solved:", bool((out == y_xor).all()))
```
```text
hidden units (OR, AND):
[[0. 0.]
 [1. 0.]
 [1. 0.]
 [1. 1.]]
output: [0 1 1 0] | truth: [0 1 1 0] | solved: True
```

The hidden layer **re-represents** the inputs in a space where the problem becomes linearly separable. This is the idea of the whole field: layers learn a useful representation, and the last layer is just a linear (or logistic) model on top of it.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the XOR problem. Plot the four points (0,0), (0,1), (1,0), (1,1) in the plane, coloured by class: (0,1) and (1,0) are class 1, (0,0) and (1,1) are class 0. Show that no single straight line separates them. Then draw a second plot in the hidden space (OR, AND), where the points become (0,0), (1,0), (1,0), (1,1) and one line separates the classes. Label both plots."

### 1.2 Why a non-linearity is essential

Stack two linear layers with nothing between them and you get one linear layer: `W₂(W₁x) = (W₂W₁)x`. Depth buys nothing unless every layer is followed by a **non-linear activation function**.

```python run
rng = np.random.default_rng(0)
W1_, W2_ = rng.normal(size=(5, 8)), rng.normal(size=(8, 3))
X_ = rng.normal(size=(10, 5))
two_layers = (X_ @ W1_) @ W2_
one_layer = X_ @ (W1_ @ W2_)
print("two linear layers equal ONE linear layer with weight W1 @ W2:", bool(np.allclose(two_layers, one_layer)))
print("with a ReLU between them it is no longer linear:", not np.allclose(np.maximum(X_ @ W1_, 0) @ W2_, one_layer))
```
```text
two linear layers equal ONE linear layer with weight W1 @ W2: True
with a ReLU between them it is no longer linear: True
```

### 1.3 A network on a real two-class problem

Two interleaved half-moons (a standard test). A logistic regression reaches about 84%; a small network, about 95% (the 5% left is mostly the overlap that the noise creates). We use scikit-learn's `MLPClassifier` here only to see the effect; we build our own in section 8.

```python run
from sklearn.neural_network import MLPClassifier
Xm, ym = datasets.make_moons(n_samples=1000, noise=0.2, random_state=0)
Xm_tr, Xm_te, ym_tr, ym_te = model_selection.train_test_split(Xm, ym, test_size=0.3, random_state=0)
lin = linear_model.LogisticRegression().fit(Xm_tr, ym_tr)
mlp = MLPClassifier(hidden_layer_sizes=(16, 16), max_iter=2000, random_state=0).fit(Xm_tr, ym_tr)
print(f"logistic regression test accuracy: {lin.score(Xm_te, ym_te):.3f}")
print(f"2 hidden layers of 16 units       : {mlp.score(Xm_te, ym_te):.3f}")
```
```text
logistic regression test accuracy: 0.837
2 hidden layers of 16 units       : 0.953
```

### 1.4 How much can one hidden layer represent

A famous result (the **universal approximation theorem**) says that a network with one hidden layer of enough units can approximate any reasonable function as closely as you like. It says nothing about how to find the weights or how many units are enough. A quick feel for it: fit `sin(x)` with a hidden layer of `k` random `tanh` units and solve only the output weights by least squares.

```python run
x_ = np.linspace(-3, 3, 400)[:, None]
target = np.sin(2 * x_[:, 0])
rows = []
for k in [1, 2, 4, 8, 16, 64]:
    r_ = np.random.default_rng(1)
    H = np.tanh(x_ @ r_.normal(0, 2.0, (1, k)) + r_.normal(0, 2.0, k))             # k random hidden units
    w, *_ = np.linalg.lstsq(np.c_[H, np.ones(len(x_))], target, rcond=None)
    pred = np.c_[H, np.ones(len(x_))] @ w
    rows.append((k, float(np.sqrt(np.mean((pred - target) ** 2)))))
print(pd.DataFrame(rows, columns=["hidden units", "RMSE fitting sin(2x)"]).to_string(index=False))
```
```text
 hidden units  RMSE fitting sin(2x)
            1               0.64819
            2               0.62888
            4               0.38626
            8               0.14602
           16               0.00143
           64               0.00000
```

The error falls steadily with width. Real networks do not use random hidden units: they **learn** them, which is far more efficient, and that learning is what the rest of the chapter is about. Depth (many layers) is usually a more efficient way to add expressive power than extreme width.

### 1.5 Try it

1. Build a network with hand-chosen weights that computes XNOR (the opposite of XOR). Which of your numbers changed?
2. Fit `sin(2x)` with `k=64` random units but *without* a bias in the hidden layer. Does the error change much?

## 2. Neurons, layers and the forward pass

### 2.1 One neuron

A neuron computes a weighted sum of its inputs plus a bias, then applies an activation function `φ`:

```text
z = w · x + b         a = φ(z)
```

A **layer** is many neurons looking at the same inputs. Stacking the weight vectors as columns gives a weight matrix `W` of shape `(d_in, d_out)`, and processing a whole **batch** of `N` examples at once is one matrix product:

```text
Z = X W + b      A = φ(Z)         X: (N, d_in)   W: (d_in, d_out)   b: (d_out,)   Z, A: (N, d_out)
```

**Batch-first shapes** (rows are examples) are used throughout the chapter and in PyTorch. Getting shapes right is most of the debugging in deep learning.

```python run
def init_params(sizes, seed=0, scale=0.5):
    r = np.random.default_rng(seed)
    return [(r.normal(0, scale, (a, b)), np.zeros(b)) for a, b in zip(sizes[:-1], sizes[1:])]

def forward(X, params, act=np.tanh):
    A = X
    for i, (W, b) in enumerate(params):
        Z = A @ W + b
        A = act(Z) if i < len(params) - 1 else Z                  # no activation on the last layer: it outputs raw scores ("logits")
    return A

sizes = [64, 32, 16, 10]
params = init_params(sizes)
Xd = np.random.default_rng(1).normal(size=(5, 64))
out = forward(Xd, params)
print("input", Xd.shape, "-> output", out.shape)
n_params = sum(W.size + b.size for W, b in params)
print("parameters per layer:", [W.size + b.size for W, b in params], "| total", n_params)
print("for the classic 784-128-64-10 network:", sum(a * b + b for a, b in zip([784, 128, 64], [128, 64, 10])), "parameters")
```
```text
input (5, 64) -> output (5, 10)
parameters per layer: [2080, 528, 170] | total 2778
for the classic 784-128-64-10 network: 109386 parameters
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a batch flowing through a network with layer sizes 64, 32, 16, 10. Show the input X as a grid of shape (5, 64), then each weight matrix W as a grid of shape (64, 32), (32, 16), (16, 10), with the output of shape (5, 10). Label every shape, mark the matrix product Z = X W + b at each step, and note that the last layer has no activation."

### 2.2 A forward pass worked by hand, checked by the referee

A 2-2-1 network with `tanh` in the middle. The numbers are chosen so you can follow them with a calculator.

```python run
x = np.array([[1.0, -2.0]])
W1 = np.array([[0.5, -1.0], [0.25, 0.75]]); b1 = np.array([0.1, -0.2])
W2 = np.array([[1.5], [-0.5]]); b2 = np.array([0.3])
z1 = x @ W1 + b1
a1 = np.tanh(z1)
z2 = a1 @ W2 + b2
print("z1 =", z1, "= [1*0.5 + (-2)*0.25 + 0.1, 1*(-1) + (-2)*0.75 - 0.2] = [0.1, -2.7]")
print("a1 = tanh(z1) =", a1)
print("z2 =", z2, "= 0.0997*1.5 + (-0.991)*(-0.5) + 0.3")
if HAS_TORCH:
    l1, l2 = torch.nn.Linear(2, 2), torch.nn.Linear(2, 1)
    with torch.no_grad():
        l1.weight.copy_(torch.tensor(W1.T)); l1.bias.copy_(torch.tensor(b1)); l2.weight.copy_(torch.tensor(W2.T)); l2.bias.copy_(torch.tensor(b2))
    ref = l2(torch.tanh(l1(torch.tensor(x)))).detach().numpy()
    print("PyTorch referee gives", ref, "| equal:", bool(np.allclose(ref, z2)))
```
```text
z1 = [[ 0.1 -2.7]] = [1*0.5 + (-2)*0.25 + 0.1, 1*(-1) + (-2)*0.75 - 0.2] = [0.1, -2.7]
a1 = tanh(z1) = [[ 0.09967 -0.99101]]
z2 = [[0.94501]] = 0.0997*1.5 + (-0.991)*(-0.5) + 0.3
PyTorch referee gives [[0.94501]] | equal: True
```

Note `l1.weight` is stored as `(d_out, d_in)`, the transpose of our `W`; that is a PyTorch convention (it computes `X Wᵀ + b`). Mixing the two up is a classic source of silent bugs.

### 2.3 Try it

1. Compute the number of parameters of a network `[100, 50, 50, 20, 1]` by hand and with `init_params`.
2. Change the batch size from 5 to 5,000 in the forward pass and time it. How does the time scale?

## 3. Activation functions

### 3.1 The catalogue

The activation `φ` supplies the non-linearity. What matters is its **shape** and its **derivative**, because the derivative is what gradients flow through.

| Name | Formula | Range | Notes |
|---|---|---|---|
| **Sigmoid** | `1/(1+e^-z)` | (0, 1) | probability-like; saturates (derivative ≤ 0.25); used at the output of binary classifiers |
| **tanh** | `(e^z - e^-z)/(e^z + e^-z)` | (-1, 1) | zero-centred; still saturates |
| **ReLU** | `max(0, z)` | [0, inf) | cheap, does not saturate for z>0; units can "die" |
| **Leaky ReLU** | `max(αz, z)`, α≈0.01 | (-inf, inf) | keeps a small slope for z<0 |
| **GELU** | `z·Φ(z)` | ≈(-0.17, inf) | smooth ReLU; standard in transformers |
| **Softplus** | `ln(1+e^z)` | (0, inf) | smooth ReLU; always positive |
| **Softmax** | `e^z_i / Σ_j e^z_j` | simplex | turns scores into class probabilities; output layer only |

```python run
def sigmoid(z):
    out = np.empty_like(z, dtype=float)
    pos = z >= 0
    out[pos] = 1 / (1 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1 + ez)                                           # stable for large negative z
    return out
def d_sigmoid(z):  s = sigmoid(z); return s * (1 - s)
def d_tanh(z):     return 1 - np.tanh(z) ** 2
relu = lambda z: np.maximum(z, 0.0)
d_relu = lambda z: (z > 0).astype(float)
leaky = lambda z, a=0.01: np.where(z > 0, z, a * z)
d_leaky = lambda z, a=0.01: np.where(z > 0, 1.0, a)
from math import erf, sqrt, pi
Phi = np.vectorize(lambda t: 0.5 * (1 + erf(t / sqrt(2))))
gelu = lambda z: z * Phi(z)
softplus = lambda z: np.logaddexp(0, z)
d_softplus = sigmoid

z = np.array([-6.0, -2.0, -0.5, 0.0, 0.5, 2.0, 6.0])
tab = pd.DataFrame({"z": z, "sigmoid": sigmoid(z), "tanh": np.tanh(z), "relu": relu(z), "leaky": leaky(z), "gelu": gelu(z), "softplus": softplus(z)}).set_index("z")
print(tab.round(4).to_string())
dtab = pd.DataFrame({"z": z, "d sigmoid": d_sigmoid(z), "d tanh": d_tanh(z), "d relu": d_relu(z), "d leaky": d_leaky(z)}).set_index("z")
print("\nderivatives:"); print(dtab.round(4).to_string())
```
```text
          sigmoid     tanh    relu    leaky     gelu  softplus
z                                                             
-6.00000  0.00250 -1.00000 0.00000 -0.06000 -0.00000   0.00250
-2.00000  0.11920 -0.96400 0.00000 -0.02000 -0.04550   0.12690
-0.50000  0.37750 -0.46210 0.00000 -0.00500 -0.15430   0.47410
0.00000   0.50000  0.00000 0.00000  0.00000  0.00000   0.69310
0.50000   0.62250  0.46210 0.50000  0.50000  0.34570   0.97410
2.00000   0.88080  0.96400 2.00000  2.00000  1.95450   2.12690
6.00000   0.99750  1.00000 6.00000  6.00000  6.00000   6.00250

derivatives:
          d sigmoid  d tanh  d relu  d leaky
z                                           
-6.00000    0.00250 0.00000 0.00000  0.01000
-2.00000    0.10500 0.07070 0.00000  0.01000
-0.50000    0.23500 0.78640 0.00000  0.01000
0.00000     0.25000 1.00000 0.00000  0.01000
0.50000     0.23500 0.78640 1.00000  1.00000
2.00000     0.10500 0.07070 1.00000  1.00000
6.00000     0.00250 0.00000 1.00000  1.00000
```

### 3.2 Saturation and vanishing gradients

Look at the sigmoid derivative: at most 0.25 (at `z=0`), and about 0.0025 at `z=±6`. Backpropagation multiplies derivatives layer after layer, so in a deep network of sigmoids the gradient reaching the early layers is a product of many numbers below 0.25. It **vanishes**: the first layers barely learn. ReLU has derivative exactly 1 on the active side, so it adds no shrinking factor of its own (section 9 measures the gradient through whole networks, where the weights matter too).

```python run
rng = np.random.default_rng(0)
L = 20
z_layers = rng.normal(0, 1.5, (1000, L))                                    # typical pre-activations at each of 20 layers
for name, d in [("sigmoid", d_sigmoid), ("tanh", d_tanh)]:
    prod = np.cumprod(d(z_layers), axis=1)                                  # product of the local derivatives down the stack
    print(f"{name:8s} median gradient factor after 5, 10, 20 layers: {np.median(prod[:, 4]):.2e}, {np.median(prod[:, 9]):.2e}, {np.median(prod[:, 19]):.2e}")
```
```text
sigmoid  median gradient factor after 5, 10, 20 layers: 1.26e-04, 1.17e-08, 1.03e-16
tanh     median gradient factor after 5, 10, 20 layers: 1.59e-03, 1.31e-06, 9.35e-13
```

> **Predict the output.** For 20 stacked layers with pre-activations spread around zero, roughly how big is the product of the local derivatives for sigmoid layers? And for tanh layers?

<details><summary>Answer</summary>

Through 20 sigmoid layers the factor is about 1e-16 (every layer multiplies by at most 0.25), and through 20 tanh layers about 1e-12. A signal that small is below the noise of any computation: the first layers of such a network receive essentially no learning signal. This is the **vanishing-gradient problem**, and it is the main reason ReLU replaced sigmoid and tanh as the default hidden activation.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot the sigmoid derivative against z from -8 to 8, with its peak of 0.25 at z=0 and about 0.0025 at z=6 marked. Beside it, draw a bar chart on a log axis of the gradient factor after 1 to 20 stacked sigmoid layers, where each layer multiplies by a number of at most 0.25. Highlight that after 20 layers the factor is about 1e-16."

### 3.3 The dead-unit problem

A ReLU unit whose pre-activation is negative for **every** input outputs 0 and has gradient 0: it can never recover. A large learning-rate step that pushes the bias very negative can kill units permanently.

```python run
Xs_ = np.random.default_rng(2).normal(size=(1000, 4))
w_ok, b_ok = np.array([0.5, -0.3, 0.8, 0.1]), 0.0
w_dead, b_dead = w_ok, -20.0                                                  # a bias pushed far negative
for name, w, b in [("healthy unit", w_ok, b_ok), ("unit with bias -20", w_dead, b_dead)]:
    pre = Xs_ @ w + b
    print(f"{name:20s} share of inputs for which the unit is active: {np.mean(pre > 0):.3f} | mean gradient through it: {d_relu(pre).mean():.3f}")
print("Leaky ReLU keeps a small gradient:", leaky(np.array([-3.0])), "slope", d_leaky(np.array([-3.0])))
```
```text
healthy unit         share of inputs for which the unit is active: 0.487 | mean gradient through it: 0.487
unit with bias -20   share of inputs for which the unit is active: 0.000 | mean gradient through it: 0.000
Leaky ReLU keeps a small gradient: [-0.03] slope [0.01]
```

### 3.4 Softmax and numerical stability

Softmax turns a vector of scores into probabilities. Computing `e^z` directly overflows for large scores; the fix is to subtract the maximum first, which leaves the result unchanged.

```python run
def softmax_naive(z):
    e = np.exp(z); return e / e.sum(axis=-1, keepdims=True)
def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True)); return e / e.sum(axis=-1, keepdims=True)
scores = np.array([[1000.0, 1001.0, 1002.0]])
print("naive softmax :", softmax_naive(scores), "(overflow -> nan)")
print("stable softmax:", softmax(scores))
print("shift invariance: softmax(z) == softmax(z + 7):", bool(np.allclose(softmax(np.array([[1.0, 2.0, 3.0]])), softmax(np.array([[8.0, 9.0, 10.0]])))))
```
```text
naive softmax : [[nan nan nan]] (overflow -> nan)
stable softmax: [[0.09003 0.24473 0.66524]]
shift invariance: softmax(z) == softmax(z + 7): True
```

### 3.5 Checking derivatives with the referee

Never trust a hand-written derivative until it has been checked. PyTorch's automatic differentiation is an independent implementation:

```python run
if HAS_TORCH:
    zt = torch.tensor(np.linspace(-4, 4, 9), requires_grad=True)
    for name, fn, d in [("sigmoid", torch.sigmoid, d_sigmoid), ("tanh", torch.tanh, d_tanh), ("relu", torch.relu, d_relu), ("softplus", torch.nn.functional.softplus, d_softplus)]:
        zt.grad = None
        fn(zt).sum().backward()
        print(f"{name:9s} max |hand-written derivative - autograd| = {np.max(np.abs(zt.grad.numpy() - d(zt.detach().numpy()))):.1e}")
```
```text
sigmoid   max |hand-written derivative - autograd| = 6.9e-18
tanh      max |hand-written derivative - autograd| = 5.1e-17
relu      max |hand-written derivative - autograd| = 0.0e+00
softplus  max |hand-written derivative - autograd| = 1.1e-16
```

### 3.6 Which activation where

| Place | Typical choice | Why |
|---|---|---|
| Hidden layers (most networks) | ReLU, or GELU/leaky ReLU | no saturation, cheap |
| Hidden layers of recurrent/old networks | tanh | zero-centred, bounded |
| Output, binary classification | sigmoid (inside the loss) | gives a probability |
| Output, multi-class | softmax (inside the loss) | probabilities over classes |
| Output, regression | none (identity) | unbounded real values |
| Output, positive quantity | softplus or exp | forces positivity |

### 3.7 Try it

1. Implement the derivative of GELU by finite differences and compare with PyTorch's.
2. Find the input range where `d_sigmoid(z) < 0.01`. What does it imply for inputs with large magnitude?

## 4. Loss functions

### 4.1 The loss measures how wrong the network is

A **loss** reduces predictions and targets to one number that training pushes down. It must be (almost everywhere) differentiable. The choice follows from the task, and from probability: most standard losses are the **negative log-likelihood** of a sensible noise model (ds.01, ds.06).

| Task | Loss | Formula (one example) | Output layer |
|---|---|---|---|
| Regression | **Mean squared error** | `½ (ŷ − y)²` | identity |
| Regression, outliers | **Huber** | quadratic for small errors, linear for large | identity |
| Binary classification | **Binary cross-entropy** | `−[y log p + (1−y) log(1−p)]` | sigmoid |
| Multi-class | **Categorical cross-entropy** | `−log p_true` | softmax |

### 4.2 Cross-entropy from the logits, stably

Computing `log(sigmoid(z))` or `log(softmax(z))` naively loses precision or returns infinity. Always compute the loss **from the raw scores** (logits) with the log-sum-exp trick.

```python run
def bce_with_logits(z, y):
    """Mean binary cross-entropy from logits z: max(z,0) - z*y + log(1 + exp(-|z|))."""
    return np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z))))

def log_softmax(z):
    m = z.max(axis=1, keepdims=True)
    return z - m - np.log(np.exp(z - m).sum(axis=1, keepdims=True))

def cross_entropy_with_logits(z, y):
    """Mean categorical cross-entropy from logits z (N, C) and integer labels y (N,)."""
    return -np.mean(log_softmax(z)[np.arange(len(y)), y])

mse = lambda pred, y: 0.5 * np.mean((pred - y) ** 2)

z_big = np.array([40.0, -40.0]); y_b = np.array([0.0, 1.0])
naive = -np.mean(y_b * np.log(sigmoid(z_big)) + (1 - y_b) * np.log(1 - sigmoid(z_big)))
print("two wildly wrong predictions: naive BCE =", naive, "| stable BCE from logits =", round(bce_with_logits(z_big, y_b), 4), "(= 40, as it should be)")
```
```text
two wildly wrong predictions: naive BCE = inf | stable BCE from logits = 40.0 (= 40, as it should be)
```

### 4.3 The beautiful gradient

For a sigmoid output with binary cross-entropy, and for a softmax output with categorical cross-entropy, the derivative of the loss with respect to the **logits** is simply

```text
∂L/∂z = p − y          (p = predicted probability, y = target; one-hot for several classes)
```

This is the same "prediction minus truth" you met in ds.06 for logistic regression, and it is why these pairings are used: the gradient is large when the prediction is badly wrong and small when it is nearly right, with no vanishing factor from the activation. We verify it numerically:

```python run
def numerical_grad(f, x, eps=1e-6):
    g = np.zeros_like(x, dtype=float)
    it = np.nditer(x, flags=["multi_index"])
    for _ in it:
        idx = it.multi_index
        old = x[idx]
        x[idx] = old + eps; fp = f()
        x[idx] = old - eps; fm = f()
        x[idx] = old
        g[idx] = (fp - fm) / (2 * eps)
    return g

rng = np.random.default_rng(3)
Z = rng.normal(size=(6, 4)); yc = rng.integers(0, 4, 6)
analytic = (softmax(Z) - np.eye(4)[yc]) / len(yc)                                    # (p - onehot)/N for the MEAN loss
num = numerical_grad(lambda: cross_entropy_with_logits(Z, yc), Z)
print("categorical cross-entropy: max |analytic - numerical| =", float(np.max(np.abs(analytic - num))))
zb = rng.normal(size=8); yb = rng.integers(0, 2, 8).astype(float)
analytic_b = (sigmoid(zb) - yb) / len(yb)
print("binary cross-entropy      : max |analytic - numerical| =", float(np.max(np.abs(analytic_b - numerical_grad(lambda: bce_with_logits(zb, yb), zb)))))
if HAS_TORCH:
    zt = torch.tensor(Z, requires_grad=True)
    torch.nn.functional.cross_entropy(zt, torch.tensor(yc)).backward()
    print("PyTorch referee, cross-entropy gradient equal:", bool(np.allclose(zt.grad.numpy(), analytic)))
```
```text
categorical cross-entropy: max |analytic - numerical| = 1.730572837810307e-10
binary cross-entropy      : max |analytic - numerical| = 4.3213738143421665e-11
PyTorch referee, cross-entropy gradient equal: True
```

### 4.4 A sanity check you will use all the time: the initial loss

If the network is not yet trained and its outputs are close to uniform, the cross-entropy over `C` classes should be about `ln C`. If the first loss you see is very different, something is wrong (a bug, or a badly scaled initialisation).

```python run
for C in [2, 10, 100]:
    print(f"{C:3d} classes: expected initial loss ln(C) = {math.log(C):.4f}")
Zinit = np.random.default_rng(4).normal(0, 0.01, (2000, 10)); yinit = np.random.default_rng(5).integers(0, 10, 2000)
print("a freshly initialised 10-class network (tiny logits) starts at", round(cross_entropy_with_logits(Zinit, yinit), 4))
Zbad = np.random.default_rng(4).normal(0, 5.0, (2000, 10))
print("the same task with badly scaled (large) logits starts at     ", round(cross_entropy_with_logits(Zbad, yinit), 4), "<- a warning sign")
```
```text
  2 classes: expected initial loss ln(C) = 0.6931
 10 classes: expected initial loss ln(C) = 2.3026
100 classes: expected initial loss ln(C) = 4.6052
a freshly initialised 10-class network (tiny logits) starts at 2.3023
the same task with badly scaled (large) logits starts at      7.7604 <- a warning sign
```

### 4.5 Mean squared error, Huber and the effect of outliers

```python run
def huber(pred, y, delta=1.0):
    e = pred - y
    return np.mean(np.where(np.abs(e) <= delta, 0.5 * e ** 2, delta * (np.abs(e) - 0.5 * delta)))
errors = np.array([0.1, -0.3, 0.2, 0.0, 8.0])                                  # four good predictions and one huge outlier
print("MSE loss   :", round(mse(errors, 0), 3), "| share of it from the outlier:", round(0.5 * 8.0 ** 2 / np.sum(0.5 * errors ** 2), 3))
print("Huber loss :", round(huber(errors, 0), 3), "| the outlier counts linearly, not quadratically")
```
```text
MSE loss   : 6.414 | share of it from the outlier: 0.998
Huber loss : 1.514 | the outlier counts linearly, not quadratically
```

### 4.6 Try it

1. Add class weights to `cross_entropy_with_logits` and check the gradient numerically.
2. Compute the cross-entropy of a model that predicts the class frequencies for every example, on `load_digits`. How does it relate to `ln 10`?

## 5. Gradient descent and optimisers

### 5.1 The basic step

Training means finding parameters `θ` that minimise the loss `L(θ)`. **Gradient descent** repeats `θ ← θ − η ∇L(θ)`, with learning rate `η`. In practice the gradient is computed on a small random **mini-batch** of examples, which is noisy but cheap (ds.06 section 2.6): this is **stochastic gradient descent (SGD)**. One pass through the data is an **epoch**.

Plain SGD has two problems: it crawls along narrow valleys (where curvature differs by direction) and the best `η` is hard to choose. Better **optimisers** fix this.

### 5.2 The optimisers

| Optimiser | Idea | Update (g = gradient) |
|---|---|---|
| **SGD** | step downhill | `θ -= η g` |
| **Momentum** | keep a running velocity: smooths noise, speeds up along consistent directions | `v = μv + g;  θ -= η v` |
| **Nesterov** | look ahead before computing the gradient | momentum with the gradient taken at `θ − ημv` |
| **RMSProp** | divide by a running average of squared gradients: per-parameter step size | `s = ρs + (1−ρ)g²;  θ -= η g/(√s+ε)` |
| **Adam** | momentum **and** RMSProp, with bias correction | `m = β₁m+(1−β₁)g; v = β₂v+(1−β₂)g²; θ -= η m̂/(√v̂+ε)` |
| **AdamW** | Adam with weight decay applied directly to the weights | `θ -= η(m̂/(√v̂+ε) + λθ)` |

```python run
class Optimizer:
    def __init__(self, params, lr): self.params, self.lr, self.t = params, lr, 0
    def step(self, grads):
        self.t += 1
        for i, (p, g) in enumerate(zip(self.params, grads)): p -= self._update(i, g)    # in-place

class SGD(Optimizer):
    def __init__(self, params, lr=0.01, momentum=0.0, nesterov=False):
        super().__init__(params, lr); self.mu, self.nesterov = momentum, nesterov
        self.v = [np.zeros_like(p) for p in params]
    def _update(self, i, g):
        self.v[i] = self.mu * self.v[i] + g
        return self.lr * (g + self.mu * self.v[i] if self.nesterov else self.v[i])

class RMSProp(Optimizer):
    def __init__(self, params, lr=0.01, rho=0.9, eps=1e-8):
        super().__init__(params, lr); self.rho, self.eps = rho, eps; self.s = [np.zeros_like(p) for p in params]
    def _update(self, i, g):
        self.s[i] = self.rho * self.s[i] + (1 - self.rho) * g ** 2
        return self.lr * g / (np.sqrt(self.s[i]) + self.eps)

class Adam(Optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0):
        super().__init__(params, lr); self.b1, self.b2, self.eps, self.wd = *betas, eps, weight_decay
        self.m = [np.zeros_like(p) for p in params]; self.v = [np.zeros_like(p) for p in params]
    def _update(self, i, g):
        self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
        self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * g ** 2
        mhat, vhat = self.m[i] / (1 - self.b1 ** self.t), self.v[i] / (1 - self.b2 ** self.t)          # bias correction: m and v start at 0
        return self.lr * (mhat / (np.sqrt(vhat) + self.eps) + self.wd * self.params[i])               # wd > 0 gives AdamW
```

### 5.3 An ill-conditioned valley

The function `f(x, y) = ½(x² + 100 y²)` is a long, thin valley: 100 times steeper in `y` than in `x`. A learning rate small enough to be stable along `y` crawls along `x`.

```python run
def run(opt_cls, steps=100, start=(10.0, 1.0), **kw):
    p = [np.array(start, dtype=float)]
    opt = opt_cls(p, **kw)
    hist = []
    for _ in range(steps):
        g = np.array([p[0][0], 100 * p[0][1]])                                   # gradient of 0.5*(x^2 + 100 y^2)
        opt.step([g]); hist.append(0.5 * (p[0][0] ** 2 + 100 * p[0][1] ** 2))
    return np.array(hist)

res = {
    "SGD lr=0.019 (max stable)": run(SGD, lr=0.019),
    "SGD lr=0.021 (too large)": run(SGD, lr=0.021),
    "SGD + momentum 0.9, lr=0.01": run(SGD, lr=0.01, momentum=0.9),
    "Nesterov 0.9, lr=0.01": run(SGD, lr=0.01, momentum=0.9, nesterov=True),
    "RMSProp lr=0.3": run(RMSProp, lr=0.3),
    "Adam lr=0.5": run(Adam, lr=0.5),
}
print(pd.DataFrame({k: v[[0, 9, 24, 49, 99]] for k, v in res.items()}, index=["step 1", "step 10", "step 25", "step 50", "step 100"]).T.to_string(float_format=lambda v: f"{v:.3g}"))
```
```text
                             step 1  step 10  step 25  step 50  step 100
SGD lr=0.019 (max stable)      88.6     40.1     19.4     7.34      1.08
SGD lr=0.021 (too large)        108      369 5.89e+03 6.89e+05   9.5e+09
SGD + momentum 0.9, lr=0.01      49     20.8     2.03    0.294  0.000438
Nesterov 0.9, lr=0.01          88.6       17   0.0306    0.123  2.51e-05
RMSProp lr=0.3                 41.1     14.3     2.13   0.0469      1.22
Adam lr=0.5                    57.6     14.7   0.0308    0.222   0.00183
```

Read it: SGD with the largest stable rate is still slow (the `x` direction barely moves in 100 steps); a rate just above the limit **diverges**; momentum and Nesterov converge much faster; RMSProp and Adam adapt a step size per coordinate. Adam's loss does not fall smoothly here because its aggressive rate overshoots: Adam is not magic and the learning rate still matters.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate gradient descent on the thin valley f(x, y) = 0.5 * (x^2 + 100 y^2), starting at (10, 1). Show contour lines and the path of three optimisers: plain SGD with lr=0.019 (slow, crawling along x), SGD with lr=0.021 (zigzag that diverges), and SGD with momentum 0.9 and lr=0.01 (fast). Show the loss per step beside the contour plot."

### 5.4 Proving the Adam implementation: the referee

```python run
if HAS_TORCH:
    rng = np.random.default_rng(0)
    p_np = [rng.normal(size=(3, 2)), rng.normal(size=2)]
    p_t = [torch.tensor(p.copy(), requires_grad=True) for p in p_np]
    ours = Adam(p_np, lr=0.01, weight_decay=0.0)
    theirs = torch.optim.Adam(p_t, lr=0.01, betas=(0.9, 0.999), eps=1e-8)
    for step in range(20):
        grads = [rng.normal(size=p.shape) for p in p_np]
        ours.step(grads)
        for p, g in zip(p_t, grads): p.grad = torch.tensor(g)
        theirs.step()
    print("after 20 steps, max |our Adam - torch.optim.Adam| =", max(float(np.max(np.abs(a - b.detach().numpy()))) for a, b in zip(p_np, p_t)))
    p2 = [np.array([1.0, -2.0, 3.0])]; t2 = [torch.tensor(p2[0].copy(), requires_grad=True)]
    m_ours = SGD(p2, lr=0.1, momentum=0.9); m_theirs = torch.optim.SGD(t2, lr=0.1, momentum=0.9)
    for _ in range(15):
        g = np.array([0.5, -1.0, 2.0]); m_ours.step([g.copy()]); t2[0].grad = torch.tensor(g); m_theirs.step()
    print("SGD with momentum: max difference", float(np.max(np.abs(p2[0] - t2[0].detach().numpy()))))
```
```text
after 20 steps, max |our Adam - torch.optim.Adam| = 0.0
SGD with momentum: max difference 0.0
```

### 5.5 Learning-rate schedules

A constant learning rate is a compromise: large at the start to make progress, small at the end to settle. A **schedule** varies it:

```python run
def step_decay(t, lr0=0.1, drop=0.5, every=30): return lr0 * drop ** (t // every)
def cosine(t, T=100, lr0=0.1, lr_min=0.0): return lr_min + 0.5 * (lr0 - lr_min) * (1 + math.cos(math.pi * t / T))
def warmup_cosine(t, T=100, warm=10, lr0=0.1): return lr0 * (t + 1) / warm if t < warm else cosine(t - warm, T - warm, lr0)
ts = [0, 5, 10, 20, 30, 50, 70, 90, 99]
print(pd.DataFrame({"t": ts, "step decay": [step_decay(t) for t in ts], "cosine": [cosine(t) for t in ts], "warm-up then cosine": [warmup_cosine(t) for t in ts]}).set_index("t").round(4).T.to_string())
```
```text
t                        0       5       10      20      30      50      70      90      99
step decay          0.10000 0.10000 0.10000 0.10000 0.05000 0.05000 0.02500 0.01250 0.01250
cosine              0.10000 0.09940 0.09760 0.09050 0.07940 0.05000 0.02060 0.00240 0.00000
warm-up then cosine 0.01000 0.06000 0.10000 0.09700 0.08830 0.05870 0.02500 0.00300 0.00000
```

**Warm-up** (starting small) protects Adam in the first steps, when its second-moment estimate is poor; **cosine decay** ends with tiny steps that settle the weights. Both are standard in modern training.

### 5.6 Mini-batch size and noise

```python run
Xd_, yd_ = datasets.load_digits(return_X_y=True)
Xd_ = Xd_ / 16.0
y2 = (yd_ >= 5).astype(float)                                                   # a binary task: digits 5-9 versus 0-4
def logreg_sgd(batch, lr, epochs=15, seed=0):
    r = np.random.default_rng(seed); w = np.zeros(64); b = 0.0; hist = []
    for ep in range(epochs):
        order = r.permutation(len(y2))
        for s in range(0, len(y2), batch):
            idx = order[s:s + batch]
            e = sigmoid(Xd_[idx] @ w + b) - y2[idx]
            w -= lr * Xd_[idx].T @ e / len(idx); b -= lr * e.mean()
        hist.append(bce_with_logits(Xd_ @ w + b, y2))
    return hist
print(pd.DataFrame({f"batch {bs}": [logreg_sgd(bs, lr)[i] for i in (0, 4, 14)] for bs, lr in [(1, 0.05), (32, 0.5), (len(y2), 1.0)]}, index=["epoch 1", "epoch 5", "epoch 15"]).round(4).T.to_string())
```
```text
            epoch 1  epoch 5  epoch 15
batch 1     0.32460  0.26530   0.25170
batch 32    0.46650  0.30000   0.28260
batch 1797  0.66420  0.57850   0.72650
```

Small batches update often but noisily; large batches are smoother and use hardware better but make fewer updates per epoch. A batch of 32 to 256 is a common default.

### 5.7 Try it

1. Add gradient clipping (scale the gradient if its norm exceeds a threshold) to `Optimizer` and show it rescues the diverging SGD run of 5.3.
2. Implement a learning-rate "range test": raise the rate exponentially while training for a few hundred steps and print the loss. Where does it start to diverge?


## 6. Backpropagation by hand

### 6.1 The idea in one sentence

**Backpropagation is the chain rule, applied from the output backwards, reusing the numbers computed during the forward pass.** To train we need the gradient of the loss with respect to *every* parameter. Writing a formula for each by hand would be hopeless in a deep network; the chain rule lets us compute them all in one backward sweep at about the cost of the forward pass.

Take a network with one hidden layer, in batch form (`N` examples):

```text
forward:   Z1 = X W1 + b1      A1 = φ(Z1)      Z2 = A1 W2 + b2 (the logits)      L = cross-entropy(Z2, y)
```

Start from the loss and move backwards, using one rule at each step. If a quantity `U` feeds a later one, the gradient of the loss with respect to `U` is the gradient arriving from above, passed through the local derivative.

```text
dZ2 = (softmax(Z2) − Y) / N          # derivative of the mean cross-entropy w.r.t. the logits (section 4.3)
dW2 = A1ᵀ dZ2                         # because Z2 = A1 W2: the weight gradient is (input)ᵀ × (gradient arriving)
db2 = sum of dZ2 over the batch       # the bias is added to every row
dA1 = dZ2 W2ᵀ                         # pass the gradient back to the layer's input
dZ1 = dA1 ⊙ φ'(Z1)                    # through the activation: multiply element by element by its derivative
dW1 = Xᵀ dZ1       db1 = sum of dZ1 over the batch
```

**Shape rule that catches most mistakes:** every gradient has exactly the shape of the quantity it differentiates (`dW1` has the shape of `W1`, `dA1` the shape of `A1`). If a matrix product does not produce that shape, a transpose is wrong.

### 6.2 A tiny network, worked fully by hand

The 2-2-1 network of section 2.2 with a squared-error loss `L = ½(ŷ − y)²` for the target `y = 1`. We carry out the backward pass line by line, then let the code and the referee confirm every number.

```python run
x = np.array([[1.0, -2.0]]); y_t = np.array([[1.0]])
W1 = np.array([[0.5, -1.0], [0.25, 0.75]]); b1 = np.array([0.1, -0.2])
W2 = np.array([[1.5], [-0.5]]); b2 = np.array([0.3])

# forward, keeping what the backward pass needs
z1 = x @ W1 + b1; a1 = np.tanh(z1); z2 = a1 @ W2 + b2
loss = 0.5 * np.mean((z2 - y_t) ** 2)

# backward, one line per step of the chain
dz2 = z2 - y_t                              # dL/dz2 for L = 1/2 (z2 - y)^2
dW2 = a1.T @ dz2;  db2 = dz2.sum(0)
da1 = dz2 @ W2.T
dz1 = da1 * (1 - a1 ** 2)                   # tanh'(z) = 1 - tanh(z)^2
dW1 = x.T @ dz1;  db1 = dz1.sum(0)

for name, val in [("loss", loss), ("dz2", dz2), ("dW2", dW2), ("db2", db2), ("da1", da1), ("dz1", dz1), ("dW1", dW1), ("db1", db1)]:
    print(f"{name:5s}", np.round(val, 6).tolist())
if HAS_TORCH:
    P = [torch.tensor(a, requires_grad=True) for a in (W1, b1, W2, b2)]
    out = torch.tanh(torch.tensor(x) @ P[0] + P[1]) @ P[2] + P[3]
    (0.5 * ((out - torch.tensor(y_t)) ** 2).mean()).backward()
    ok = all(np.allclose(p.grad.numpy(), g) for p, g in zip(P, [dW1, db1, dW2, db2]))
    print("PyTorch autograd gives the same four parameter gradients:", ok)
```
```text
loss  0.001512
dz2   [[-0.054994]]
dW2   [[-0.005481], [0.0545]]
db2   [-0.054994]
da1   [[-0.082491, 0.027497]]
dz1   [[-0.081672, 0.000492]]
dW1   [[-0.081672, 0.000492], [0.163344, -0.000985]]
db1   [-0.081672, 0.000492]
PyTorch autograd gives the same four parameter gradients: True
```

Check one by hand: `dz2 = 0.94501 − 1 = −0.05499`. `dW2 = a1ᵀ · dz2 = [0.09967, −0.99101]ᵀ × (−0.05499) = [−0.00548, 0.05450]`. Then `da1 = dz2 × W2ᵀ = −0.05499 × [1.5, −0.5] = [−0.08249, 0.02750]`, and `dz1 = da1 ⊙ (1 − a1²) = [−0.08249 × 0.99007, 0.02750 × 0.01790] = [−0.08167, 0.00049]`. The second hidden unit has almost no gradient: its `tanh` is saturated at −0.99 (section 3.2), so changing its input barely changes its output.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the computation graph of a tiny 2-2-1 network: input x = [1, -2], hidden z1 = x W1 + b1, a1 = tanh(z1), output z2 = a1 W2 + b2, loss L = 0.5 * (z2 - 1)^2. Use forward arrows for values and backward arrows for gradients (dz2 = -0.055, da1 = [-0.082, 0.027], dz1 = [-0.082, 0.0005]). Label each backward step with the chain-rule factor used."

### 6.3 Gradient checking: the test that makes backpropagation trustworthy

A hand-written backward pass is full of places for a small error (a missing transpose, a forgotten `1/N`, a wrong derivative) that still lets the loss go down a little and then stall. The cure is **gradient checking**: compare the analytic gradient to a numerical one computed by nudging each parameter up and down (the **central difference**):

```text
∂L/∂θ_i  ≈  [ L(θ_i + ε) − L(θ_i − ε) ] / (2ε)
```

The comparison uses the **relative error** `|a − n| / max(|a| + |n|, tiny)`, because absolute errors mean little for very small or very large gradients. In double precision, with `ε = 1e-6`, a correct implementation gives relative errors between about 1e-9 and 1e-5 (the smallest gradients are the hardest to compare); errors above 1e-3 mean a bug. (Do it in float64; float32 is too imprecise for this test.)

### 6.4 A general multi-layer network with backpropagation

Now the general case: any number of layers, ReLU or tanh in between, softmax cross-entropy at the end. The class below is the engine we will use in sections 8 to 12; it is short enough to read in one sitting.

```python run
ACTS = {"relu": (relu, d_relu), "tanh": (np.tanh, d_tanh), "sigmoid": (sigmoid, d_sigmoid), "leaky": (leaky, d_leaky)}

class MLP:
    def __init__(self, sizes, act="relu", init="he", seed=0):
        self.sizes, self.act = sizes, act
        r = np.random.default_rng(seed)
        self.W, self.b = [], []
        for fan_in, fan_out in zip(sizes[:-1], sizes[1:]):
            std = {"he": math.sqrt(2 / fan_in), "xavier": math.sqrt(2 / (fan_in + fan_out)), "small": 0.01, "zero": 0.0, "large": 1.0}[init]
            self.W.append(r.normal(0, std, (fan_in, fan_out))); self.b.append(np.zeros(fan_out))

    def params(self):
        return [p for pair in zip(self.W, self.b) for p in pair]            # W0, b0, W1, b1, ...

    def forward(self, X):
        f = ACTS[self.act][0]
        self.A, self.Z = [X], []
        for i, (W, b) in enumerate(zip(self.W, self.b)):
            Z = self.A[-1] @ W + b
            self.Z.append(Z)
            self.A.append(Z if i == len(self.W) - 1 else f(Z))              # the last layer outputs raw logits
        return self.A[-1]

    def backward(self, dlogits):
        """Given dL/d(logits), return the gradients of all parameters in the order of params()."""
        df = ACTS[self.act][1]
        grads = []
        dZ = dlogits
        for i in reversed(range(len(self.W))):
            grads += [dZ.sum(0), self.A[i].T @ dZ]                          # (db, dW) appended in reverse
            if i > 0:
                dZ = (dZ @ self.W[i].T) * df(self.Z[i - 1])
        grads.reverse()
        return grads

    def loss_and_grads(self, X, y):
        logits = self.forward(X)
        loss = cross_entropy_with_logits(logits, y)
        dlogits = (softmax(logits) - np.eye(logits.shape[1])[y]) / len(y)
        return loss, self.backward(dlogits)

    def predict(self, X):
        return self.forward(X).argmax(1)

net = MLP([64, 32, 16, 10], act="tanh", seed=0)
Xb, yb = Xd_[:8], datasets.load_digits(return_X_y=True)[1][:8]
loss, grads = net.loss_and_grads(Xb, yb)
print("loss", round(loss, 4), "(a He-initialised network starts near, not exactly at, ln(10) =", round(math.log(10), 4), ") | gradient shapes:", [g.shape for g in grads])
print("every gradient has the shape of its parameter:", all(g.shape == p.shape for g, p in zip(grads, net.params())))
```
```text
loss 2.7161 (a He-initialised network starts near, not exactly at, ln(10) = 2.3026 ) | gradient shapes: [(64, 32), (32,), (32, 16), (16,), (16, 10), (10,)]
every gradient has the shape of its parameter: True
```

### 6.5 Run the gradient check on every parameter

```python run
def grad_check(net, X, y, eps=1e-6):
    _, grads = net.loss_and_grads(X, y)
    worst = []
    for p, g in zip(net.params(), grads):
        num = numerical_grad(lambda: cross_entropy_with_logits(net.forward(X), y), p, eps)
        worst.append(float(np.max(np.abs(g - num) / np.maximum(np.abs(g) + np.abs(num), 1e-12))))
    return worst

for act in ["tanh", "sigmoid", "relu"]:
    n_ = MLP([64, 20, 12, 10], act=act, seed=1)
    errs = grad_check(n_, Xb, yb)
    print(f"{act:8s} worst relative error per parameter array: {np.array(errs).round(10).tolist()}")
print("a correct implementation is below 1e-4 everywhere (the larger values belong to the first layer, whose gradients are the smallest).")
```
```text
tanh     worst relative error per parameter array: [7.0067e-06, 7.13e-08, 1.423e-07, 4.6e-09, 8.18e-08, 5.3e-09]
sigmoid  worst relative error per parameter array: [6.0464e-05, 5.389e-07, 7.455e-07, 1.5e-08, 1.241e-07, 2.4e-09]
relu     worst relative error per parameter array: [4.363e-07, 2.44e-08, 2.101e-07, 7e-09, 5.705e-07, 7.4e-09]
a correct implementation is below 1e-4 everywhere (the larger values belong to the first layer, whose gradients are the smallest).
```

(ReLU has a kink at 0, so a numerical difference that straddles it can give a rare, small mismatch; if you see one parameter off in a ReLU network, rerun with a different seed before suspecting a bug.)

### 6.6 What a bug looks like

We introduce two classic mistakes and watch the check catch them: forgetting the activation derivative, and forgetting the `1/N`.

```python run
def buggy_backward_no_activation_derivative(self, dlogits):
    grads, dZ = [], dlogits
    for i in reversed(range(len(self.W))):
        grads += [dZ.sum(0), self.A[i].T @ dZ]
        if i > 0:
            dZ = dZ @ self.W[i].T                                          # BUG: missing * df(Z)
    grads.reverse(); return grads

def check_with(backward_fn, scale=1.0):
    n_ = MLP([64, 20, 12, 10], act="tanh", seed=1)
    logits = n_.forward(Xb)
    d = (softmax(logits) - np.eye(10)[yb]) / len(yb) * scale
    g = backward_fn(n_, d)
    num = [numerical_grad(lambda: cross_entropy_with_logits(n_.forward(Xb), yb), p) for p in n_.params()]
    return max(float(np.max(np.abs(a - b) / np.maximum(np.abs(a) + np.abs(b), 1e-12))) for a, b in zip(g, num))

print("correct backward                       : worst relative error %.1e" % check_with(MLP.backward))
print("forgot the activation derivative       : worst relative error %.1e  <- caught" % check_with(buggy_backward_no_activation_derivative))
print("forgot the 1/N in the loss derivative  : worst relative error %.1e  <- caught" % check_with(MLP.backward, scale=len(yb)))
```
```text
correct backward                       : worst relative error 7.0e-06
forgot the activation derivative       : worst relative error 1.0e+00  <- caught
forgot the 1/N in the loss derivative  : worst relative error 7.8e-01  <- caught
```

A bug that lowers the loss slowly is far more dangerous than one that crashes. **Never train a hand-written network before its gradients have passed the check.**

### 6.7 The referee on a deeper network

```python run
if HAS_TORCH:
    net = MLP([64, 40, 30, 10], act="relu", seed=2)
    loss, grads = net.loss_and_grads(Xd_[:50], datasets.load_digits(return_X_y=True)[1][:50])
    tp = [torch.tensor(p.copy(), requires_grad=True) for p in net.params()]
    A = torch.tensor(Xd_[:50])
    for i in range(3):
        A = A @ tp[2 * i] + tp[2 * i + 1]
        if i < 2: A = torch.relu(A)
    tl = torch.nn.functional.cross_entropy(A, torch.tensor(datasets.load_digits(return_X_y=True)[1][:50]))
    tl.backward()
    print("loss: ours %.8f | torch %.8f" % (loss, tl.item()))
    print("max |our gradient - torch autograd| over all 6 parameter arrays:", max(float(np.max(np.abs(g - p.grad.numpy()))) for g, p in zip(grads, tp)))
```
```text
loss: ours 2.50284663 | torch 2.50284663
max |our gradient - torch autograd| over all 6 parameter arrays: 4.85722573273506e-17
```

### 6.8 Cost: why backpropagation matters

The numerical gradient needs two forward passes **per parameter**. Backpropagation needs one forward and one backward pass in total, whatever the number of parameters.

```python run
n_ = MLP([64, 32, 16, 10], act="tanh", seed=0)
t0 = time.perf_counter(); n_.loss_and_grads(Xb, yb); t_bp = time.perf_counter() - t0
t0 = time.perf_counter(); grad_check(n_, Xb, yb); t_num = time.perf_counter() - t0
npar = sum(p.size for p in n_.params())
print(f"{npar:,} parameters | backpropagation {t_bp * 1000:.2f} ms | numerical gradient {t_num * 1000:.0f} ms | numerical is about {t_num / t_bp:,.0f} times slower")
print("for a model with 100 million parameters the numerical gradient would need 200 million forward passes per step; backpropagation still needs one pass back")
```
```text
2,778 parameters | backpropagation 0.21 ms | numerical gradient 193 ms | numerical is about 908 times slower
for a model with 100 million parameters the numerical gradient would need 200 million forward passes per step; backpropagation still needs one pass back
```

The price of backpropagation is **memory**: it keeps every layer's activations until the backward pass uses them (the `self.A` and `self.Z` lists). Large models trade compute for memory by recomputing some activations (*gradient checkpointing*).

### 6.9 Try it

1. Add a third activation, `leaky`, to a gradient check. Does it pass?
2. Make `backward` also return `dX` (the gradient with respect to the input) and check it numerically. Where in a real system is that gradient useful?

## 7. A tiny autograd engine

### 7.1 Why automate it

Deriving the backward pass by hand for each new layer is slow and error-prone. **Automatic differentiation (autograd)** records every operation during the forward pass as a node in a graph, together with a small function that knows its own local derivative, and then runs the chain rule backwards over the graph automatically. This is how PyTorch, TensorFlow and JAX work. We build the smallest honest version, first on **scalars** so every step is visible.

### 7.2 A scalar engine in 60 lines

Each `Value` stores its number (`data`), its gradient (`grad`), the values it was computed from (`_prev`) and a `_backward` function that pushes the gradient to those parents. Two details matter: the gradient is **accumulated** with `+=` (a value used twice receives gradient from both uses), and the backward pass visits nodes in **reverse topological order** (a node's gradient is complete before it passes anything on).

```python run
class Value:
    def __init__(self, data, _prev=(), _op=""):
        self.data, self.grad = float(data), 0.0
        self._prev, self._op, self._backward = set(_prev), _op, (lambda: None)

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")
        def _backward():
            self.grad += out.grad; other.grad += out.grad
        out._backward = _backward; return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")
        def _backward():
            self.grad += other.data * out.grad; other.grad += self.data * out.grad
        out._backward = _backward; return out

    def __pow__(self, k):
        out = Value(self.data ** k, (self,), f"**{k}")
        def _backward(): self.grad += k * self.data ** (k - 1) * out.grad
        out._backward = _backward; return out

    def tanh(self):
        t = math.tanh(self.data); out = Value(t, (self,), "tanh")
        def _backward(): self.grad += (1 - t ** 2) * out.grad
        out._backward = _backward; return out

    def relu(self):
        out = Value(max(0.0, self.data), (self,), "relu")
        def _backward(): self.grad += (out.data > 0) * out.grad
        out._backward = _backward; return out

    def exp(self):
        e = math.exp(self.data); out = Value(e, (self,), "exp")
        def _backward(): self.grad += e * out.grad
        out._backward = _backward; return out

    def log(self):
        out = Value(math.log(self.data), (self,), "log")
        def _backward(): self.grad += out.grad / self.data
        out._backward = _backward; return out

    def sigmoid(self):
        s = 1 / (1 + math.exp(-self.data)); out = Value(s, (self,), "sigmoid")
        def _backward(): self.grad += s * (1 - s) * out.grad
        out._backward = _backward; return out

    def backward(self):
        order, seen = [], set()
        def build(v):
            if v not in seen:
                seen.add(v)
                for p in v._prev: build(p)
                order.append(v)
        build(self)
        self.grad = 1.0                                                     # d(output)/d(output) = 1
        for v in reversed(order): v._backward()

    __neg__ = lambda self: self * -1
    __sub__ = lambda self, o: self + (-o if isinstance(o, Value) else Value(-o))
    __radd__ = lambda self, o: self + o
    __rmul__ = lambda self, o: self * o
    __truediv__ = lambda self, o: self * (o ** -1 if isinstance(o, Value) else Value(1 / o))
    __repr__ = lambda self: f"Value(data={self.data:.4f}, grad={self.grad:.4f})"

a, b, c = Value(2.0), Value(-3.0), Value(10.0)
f = (a * b + c) ** 2                                                         # f = (ab + c)^2 = 16
f.backward()
print("f =", f.data, "| df/da =", a.grad, "(by hand 2(ab+c)*b = -24) | df/db =", b.grad, "(2(ab+c)*a = 16) | df/dc =", c.grad, "(2(ab+c) = 8)")
x = Value(3.0); y = x * x + x                                                # x is used three times
y.backward(); print("y = x*x + x at x=3: dy/dx =", x.grad, "(2x + 1 = 7): accumulation with += handles a value used more than once")
```
```text
f = 16.0 | df/da = -24.0 (by hand 2(ab+c)*b = -24) | df/db = 16.0 (2(ab+c)*a = 16) | df/dc = 8.0 (2(ab+c) = 8)
y = x*x + x at x=3: dy/dx = 7.0 (2x + 1 = 7): accumulation with += handles a value used more than once
```

The reference check, on a longer expression with every operation:

```python run
def expr(v):                                                                  # works on Value and on torch tensors alike
    a, b = v
    return ((a * b).tanh() + (a - b).relu() * 0.5 + (a ** 2 + 1.0) ** -1) * (b * 0.3).exp()
av, bv = Value(0.7), Value(-0.4)
out = expr((av, bv)); out.backward()
print("our engine: value %.8f, d/da %.8f, d/db %.8f" % (out.data, av.grad, bv.grad))
if HAS_TORCH:
    ta, tb = torch.tensor(0.7, requires_grad=True), torch.tensor(-0.4, requires_grad=True)
    ref = ((ta * tb).tanh() + (ta - tb).relu() * 0.5 + (ta ** 2 + 1.0) ** -1) * (tb * 0.3).exp()
    ref.backward()
    print("torch     : value %.8f, d/da %.8f, d/db %.8f" % (ref.item(), ta.grad.item(), tb.grad.item()))
```
```text
our engine: value 0.84100976, d/da -0.44417982, d/db 0.38344828
torch     : value 0.84100976, d/da -0.44417982, d/db 0.38344828
```

### 7.3 A neural network out of Values

A neuron, a layer and an MLP are a few lines on top of `Value`. The scalar engine is slow (every multiplication is a Python object), so we use a small problem: the two moons, 100 points.

```python run
import random
class Neuron:
    def __init__(self, n_in, nonlin, rng):
        self.w = [Value(rng.uniform(-1, 1) * math.sqrt(2 / n_in)) for _ in range(n_in)]; self.b = Value(0.0); self.nonlin = nonlin
    def __call__(self, x):
        s = sum((wi * xi for wi, xi in zip(self.w, x)), self.b)
        return s.tanh() if self.nonlin else s
    def parameters(self): return self.w + [self.b]

class ScalarMLP:
    def __init__(self, sizes, seed=0):
        rng = random.Random(seed)
        self.layers = [[Neuron(a, i < len(sizes) - 2, rng) for _ in range(b)] for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:]))]
    def __call__(self, x):
        for layer in self.layers: x = [n(x) for n in layer]
        return x[0]
    def parameters(self): return [p for layer in self.layers for n in layer for p in n.parameters()]

Xs, ys = datasets.make_moons(n_samples=100, noise=0.1, random_state=1)
ys_pm = 2 * ys - 1                                                            # labels in {-1, +1}
model = ScalarMLP([2, 8, 8, 1], seed=0)
print("parameters:", len(model.parameters()))
t0 = time.perf_counter()
for epoch in range(40):
    scores = [model(list(map(Value, xi))) for xi in Xs]
    loss = sum(((1 + (-yi) * s).relu() for yi, s in zip(ys_pm, scores)), Value(0.0)) * (1 / len(Xs))       # hinge loss
    for p in model.parameters(): p.grad = 0.0
    loss.backward()
    lr = 0.5 * (1 - epoch / 60)
    for p in model.parameters(): p.data -= lr * p.grad
    if epoch % 10 == 0 or epoch == 39:
        acc = np.mean([(s.data > 0) == (yi > 0) for s, yi in zip(scores, ys_pm)])
        print(f"epoch {epoch:2d}: hinge loss {loss.data:.4f}, accuracy {acc:.2f}")
print(f"40 epochs on 100 points in {time.perf_counter() - t0:.1f} s: a scalar engine is clear, and slow")
```
```text
parameters: 105
epoch  0: hinge loss 0.8579, accuracy 0.70
epoch 10: hinge loss 0.3061, accuracy 0.85
epoch 20: hinge loss 0.2831, accuracy 0.87
epoch 30: hinge loss 0.2790, accuracy 0.87
epoch 39: hinge loss 0.2770, accuracy 0.88
40 epochs on 100 points in 4.0 s: a scalar engine is clear, and slow
```

### 7.4 The tensor version: a NumPy autograd

For real data we need operations on whole arrays. The only new difficulty is **broadcasting**: when a bias of shape `(d,)` is added to a matrix `(N, d)`, the forward pass copies it across rows, so the backward pass must **sum** the incoming gradient over those rows (the exact reverse). A helper `unbroadcast` does that.

```python run
def unbroadcast(grad, shape):
    while grad.ndim > len(shape): grad = grad.sum(0)
    for ax, n in enumerate(shape):
        if n == 1 and grad.shape[ax] != 1: grad = grad.sum(ax, keepdims=True)
    return grad

class Tensor:
    def __init__(self, data, _prev=(), requires_grad=True):
        self.data = np.asarray(data, dtype=float); self.grad = np.zeros_like(self.data)
        self._prev, self._backward, self.requires_grad = _prev, (lambda: None), requires_grad

    def _wrap(o): return o if isinstance(o, Tensor) else Tensor(o, requires_grad=False)

    def __add__(self, o):
        o = Tensor._wrap(o); out = Tensor(self.data + o.data, (self, o))
        def _b(): self.grad += unbroadcast(out.grad, self.data.shape); o.grad += unbroadcast(out.grad, o.data.shape)
        out._backward = _b; return out
    def __mul__(self, o):
        o = Tensor._wrap(o); out = Tensor(self.data * o.data, (self, o))
        def _b(): self.grad += unbroadcast(out.grad * o.data, self.data.shape); o.grad += unbroadcast(out.grad * self.data, o.data.shape)
        out._backward = _b; return out
    def __matmul__(self, o):
        out = Tensor(self.data @ o.data, (self, o))
        def _b(): self.grad += out.grad @ o.data.T; o.grad += self.data.T @ out.grad
        out._backward = _b; return out
    def relu(self):
        out = Tensor(np.maximum(self.data, 0), (self,))
        def _b(): self.grad += (self.data > 0) * out.grad
        out._backward = _b; return out
    def tanh(self):
        t = np.tanh(self.data); out = Tensor(t, (self,))
        def _b(): self.grad += (1 - t ** 2) * out.grad
        out._backward = _b; return out
    def sum(self):
        out = Tensor(self.data.sum(), (self,))
        def _b(): self.grad += np.ones_like(self.data) * out.grad
        out._backward = _b; return out
    def cross_entropy(self, y):                                       # fused softmax + cross-entropy, from logits
        ls = log_softmax(self.data); n = len(y)
        out = Tensor(-np.mean(ls[np.arange(n), y]), (self,))
        def _b(): self.grad += (np.exp(ls) - np.eye(self.data.shape[1])[y]) / n * out.grad
        out._backward = _b; return out
    def backward(self):
        order, seen = [], set()
        def build(v):
            if id(v) not in seen:
                seen.add(id(v))
                for p in v._prev: build(p)
                order.append(v)
        build(self); self.grad = np.ones_like(self.data)
        for v in reversed(order): v._backward()
    __radd__ = __add__; __rmul__ = __mul__
    __neg__ = lambda self: self * -1
    __sub__ = lambda self, o: self + (-Tensor._wrap(o))

# one dense layer + ReLU + dense, with a bias that must be un-broadcast
rng = np.random.default_rng(0)
X_ = rng.normal(size=(6, 5)); y_ = rng.integers(0, 3, 6)
W1_, b1_, W2_, b2_ = [Tensor(rng.normal(size=s)) for s in [(5, 4), (4,), (4, 3), (3,)]]
loss = ((Tensor(X_, requires_grad=False) @ W1_ + b1_).relu() @ W2_ + b2_).cross_entropy(y_)
loss.backward()
print("loss", round(float(loss.data), 6), "| bias gradient shape", b1_.grad.shape, "(the sum over the 6 rows of the batch)")
if HAS_TORCH:
    P = [torch.tensor(t.data.copy(), requires_grad=True) for t in (W1_, b1_, W2_, b2_)]
    tl = torch.nn.functional.cross_entropy(torch.relu(torch.tensor(X_) @ P[0] + P[1]) @ P[2] + P[3], torch.tensor(y_))
    tl.backward()
    print("max |our Tensor gradient - torch| over W1, b1, W2, b2:", max(float(np.max(np.abs(t.grad - p.grad.numpy()))) for t, p in zip((W1_, b1_, W2_, b2_), P)))
```
```text
loss 1.315642 | bias gradient shape (4,) (the sum over the 6 rows of the batch)
max |our Tensor gradient - torch| over W1, b1, W2, b2: 1.1102230246251565e-16
```

The Tensor engine produces the same gradients as PyTorch, and as our hand-derived `MLP.backward`, and now **we never have to derive a backward pass again**: adding a new operation only requires its local derivative.

```python run
net = MLP([64, 20, 10], act="relu", seed=3)
loss_manual, grads_manual = net.loss_and_grads(Xd_[:30], datasets.load_digits(return_X_y=True)[1][:30])
Wt = [Tensor(w.copy()) for w in net.W]; bt = [Tensor(b.copy()) for b in net.b]
yy = datasets.load_digits(return_X_y=True)[1][:30]
lt = ((Tensor(Xd_[:30], requires_grad=False) @ Wt[0] + bt[0]).relu() @ Wt[1] + bt[1]).cross_entropy(yy)
lt.backward()
auto = [Wt[0].grad, bt[0].grad, Wt[1].grad, bt[1].grad]
print("hand-derived backprop vs autograd engine: max |difference| =", max(float(np.max(np.abs(a - b))) for a, b in zip(grads_manual, auto)))
```
```text
hand-derived backprop vs autograd engine: max |difference| = 5.551115123125783e-17
```

### 7.5 What the real thing adds

PyTorch's `autograd` is this same idea with much more around it: hundreds of operations with hand-written fast kernels, support for GPUs, gradients of gradients (higher order), a **dynamic graph** built anew on each forward pass (so ordinary Python `if` and `for` work inside a model), in-place operation checks, and memory-saving options. The principle, the part that is hard to see without building it, fits on one page above. ml.02 uses the real thing.

### 7.6 Try it

1. Add `__rsub__` and a `sigmoid` method to the Tensor class and check the gradient against PyTorch.
2. In the scalar `Value`, remove the `+=` (use `=`) in `__mul__` and run `x * x`. What goes wrong?

## 8. Training a network end to end

### 8.1 The training loop

Everything so far fits into the loop that trains every deep network:

```text
for each epoch:
    shuffle the training examples and cut them into mini-batches
    for each mini-batch:
        forward pass -> loss -> backward pass -> optimiser step
    evaluate on a validation set (no gradient, no parameter change)
keep the best model by validation score
```

We train on the 8x8 digits (1,797 images, 64 inputs, 10 classes), with the `MLP`, our `Adam`, and a train/validation/test split. Inputs are scaled to [0,1] (neural networks are as sensitive to input scale as the models of ds.06).

```python run
Xd_all, yd_all = datasets.load_digits(return_X_y=True)
Xd_all = Xd_all / 16.0
X_tr, X_tmp, y_tr, y_tmp = model_selection.train_test_split(Xd_all, yd_all, test_size=0.4, random_state=0, stratify=yd_all)
X_val, X_te, y_val, y_te = model_selection.train_test_split(X_tmp, y_tmp, test_size=0.5, random_state=0, stratify=y_tmp)
mu_, sd_ = X_tr.mean(0), X_tr.std(0) + 1e-8
norm = lambda A: (A - mu_) / sd_                                                  # statistics from the TRAINING set only (ds.04)
X_tr, X_val, X_te = norm(X_tr), norm(X_val), norm(X_te)
print("train", X_tr.shape, "| validation", X_val.shape, "| test", X_te.shape)

def accuracy(net, X, y): return float(np.mean(net.predict(X) == y))

def train(net, X, y, Xv, yv, epochs=30, batch=32, lr=1e-3, optimiser="adam", seed=0, weight_decay=0.0, verbose=True):
    r = np.random.default_rng(seed)
    opt = Adam(net.params(), lr=lr, weight_decay=weight_decay) if optimiser == "adam" else SGD(net.params(), lr=lr, momentum=0.9)
    hist = []
    for ep in range(epochs):
        order = r.permutation(len(y))
        for s in range(0, len(y), batch):
            idx = order[s:s + batch]
            loss, grads = net.loss_and_grads(X[idx], y[idx])
            opt.step(grads)
        tr_loss = cross_entropy_with_logits(net.forward(X), y); va_loss = cross_entropy_with_logits(net.forward(Xv), yv)
        hist.append((ep + 1, tr_loss, va_loss, accuracy(net, X, y), accuracy(net, Xv, yv)))
    return pd.DataFrame(hist, columns=["epoch", "train loss", "val loss", "train acc", "val acc"]).set_index("epoch")

net = MLP([64, 64, 32, 10], act="relu", init="he", seed=0)
t0 = time.perf_counter()
hist = train(net, X_tr, y_tr, X_val, y_val, epochs=30, lr=2e-3)
print(f"30 epochs in {time.perf_counter() - t0:.1f} s")
print(hist.iloc[[0, 1, 2, 4, 9, 14, 19, 29]].round(4).to_string())
print(f"\ntest accuracy {accuracy(net, X_te, y_te):.4f}")
```
```text
train (1078, 64) | validation (359, 64) | test (360, 64)
30 epochs in 0.6 s
       train loss  val loss  train acc  val acc
epoch                                          
1         0.87000   0.94260    0.82650  0.77990
2         0.32790   0.40850    0.92300  0.88860
3         0.18490   0.28020    0.96380  0.91090
5         0.08240   0.16380    0.98980  0.94710
10        0.02230   0.10320    0.99910  0.96380
15        0.00860   0.08320    1.00000  0.96660
20        0.00450   0.07500    1.00000  0.97210
30        0.00180   0.07070    1.00000  0.97490

test accuracy 0.9694
```

Read the curves the way ds.03 taught: the training loss keeps falling, the validation loss falls and then flattens; accuracy on both is high. The network learns the digits in a few epochs.

### 8.2 Against the baselines

```python run
from sklearn.neural_network import MLPClassifier
base_lr = linear_model.LogisticRegression(max_iter=3000).fit(X_tr, y_tr)
sk_mlp = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, random_state=0).fit(X_tr, y_tr)
print(pd.DataFrame({"test accuracy": [base_lr.score(X_te, y_te), accuracy(net, X_te, y_te), sk_mlp.score(X_te, y_te)]}, index=["logistic regression", "our NumPy network (64-64-32-10)", "scikit-learn MLPClassifier (64-32)"]).round(4).to_string())
cm = metrics.confusion_matrix(y_te, net.predict(X_te))
worst = sorted(((cm[i, j], i, j) for i in range(10) for j in range(10) if i != j), reverse=True)[:3]
print("most frequent confusions (count, true digit, predicted digit):", worst)
```
```text
                                    test accuracy
logistic regression                       0.96390
our NumPy network (64-64-32-10)           0.96940
scikit-learn MLPClassifier (64-32)        0.95280
most frequent confusions (count, true digit, predicted digit): [(np.int64(2), 4, 8), (np.int64(1), 9, 5), (np.int64(1), 8, 1)]
```

On a small, clean problem like this, the gain over logistic regression is tiny: 0.969 against 0.964 on 360 test images is about two images, well inside the noise. A linear model is a strong baseline here, consistent with the course rule of building the baseline first. Deep networks pay off on large, raw data (images, text, audio).

### 8.3 What the learning rate does

```python run
rows = []
for lr in [1e-4, 1e-3, 1e-2, 3e-2, 1e-1, 3e-1]:
    n_ = MLP([64, 64, 32, 10], act="relu", seed=0)
    h = train(n_, X_tr, y_tr, X_val, y_val, epochs=8, lr=lr)
    rows.append((lr, h["train loss"].iloc[-1], h["val acc"].iloc[-1]))
print(pd.DataFrame(rows, columns=["learning rate (Adam)", "train loss after 8 epochs", "val accuracy"]).round(4).to_string(index=False))
```
```text
 learning rate (Adam)  train loss after 8 epochs  val accuracy
              0.00010                    1.75700       0.40390
              0.00100                    0.11790       0.93870
              0.01000                    0.00130       0.98610
              0.03000                    0.10780       0.93590
              0.10000                    1.55840       0.57380
              0.30000                    2.31980       0.10030
```

Too small (1e-4): the network has barely started after 8 epochs. Too large (0.1 and above): the loss stops improving and then training fails. The best values (0.01 to 0.03 here) lie in a broad range, and a quick sweep like this one finds it (the range test of the Try it in section 5).

### 8.4 Overfitting on small data

Give the same network only 150 training examples. It has more parameters than examples, so it can memorise.

```python run
idx = np.random.default_rng(0).choice(len(X_tr), 150, replace=False)
Xs_small, ys_small = X_tr[idx], y_tr[idx]
n_ = MLP([64, 128, 128, 10], act="relu", seed=0)
h = train(n_, Xs_small, ys_small, X_val, y_val, epochs=100, batch=32, lr=2e-3)
print(h.iloc[[0, 4, 9, 19, 49, 99]].round(4).to_string())
print(f"\nthe gap: training accuracy {h['train acc'].iloc[-1]:.2f} vs validation accuracy {h['val acc'].iloc[-1]:.2f}; validation loss started to RISE after epoch {int(h['val loss'].idxmin())}")
```
```text
       train loss  val loss  train acc  val acc
epoch                                          
1         1.33340   1.67660    0.61330  0.45130
5         0.12620   0.58390    0.99330  0.81890
10        0.01980   0.44560    1.00000  0.86070
20        0.00560   0.42740    1.00000  0.88300
50        0.00130   0.42020    1.00000  0.88860
100       0.00040   0.42680    1.00000  0.89420

the gap: training accuracy 1.00 vs validation accuracy 0.89; validation loss started to RISE after epoch 44
```

Training accuracy reaches 100%, validation stays lower, and the validation loss climbs while the training loss goes to zero: classic overfitting (ds.03 section 5). Section 10 fights it. First, section 9 deals with how training *starts*.

### 8.5 Try it

1. Train the network with SGD and momentum instead of Adam. Which learning rate works? How many epochs are needed?
2. Train for 100 epochs on the full training set and plot (as a table) the validation loss. When would early stopping have stopped?


## 9. Initialisation

### 9.1 Why the starting point matters

Gradient descent needs somewhere to start. Two bad choices ruin training before it begins.

**All weights equal (including zero): the symmetry problem.** If every hidden unit starts with the same weights, every unit computes the same output and receives the same gradient, so they stay identical for ever: a layer of 64 units behaves as one unit. Randomness breaks the symmetry.

```python run
def hidden_copies(net):
    W = net.W[0]
    return float(np.max(np.abs(W - W[:, [0]])))                                    # how different are the hidden units from the first one?

for init in ["zero", "small"]:
    n_ = MLP([64, 16, 10], act="tanh", init=init, seed=0)
    h = train(n_, X_tr, y_tr, X_val, y_val, epochs=10, lr=2e-3, verbose=False)
    print(f"init={init:6s} loss after 10 epochs {h['train loss'].iloc[-1]:.4f}, val acc {h['val acc'].iloc[-1]:.3f}, largest difference between hidden units {hidden_copies(n_):.4f}")
n_const = MLP([64, 16, 10], act="tanh", init="zero", seed=0)
for i in range(2): n_const.W[i][:] = 0.1                                           # all weights the SAME nonzero constant
h = train(n_const, X_tr, y_tr, X_val, y_val, epochs=10, lr=2e-3, verbose=False)
print(f"constant 0.1 init: val acc {h['val acc'].iloc[-1]:.3f}, largest difference between hidden units after training = {hidden_copies(n_const):.1e} (still identical copies)")
```
```text
init=zero   loss after 10 epochs 2.3025, val acc 0.100, largest difference between hidden units 0.0000
init=small  loss after 10 epochs 0.2342, val acc 0.930, largest difference between hidden units 0.7871
constant 0.1 init: val acc 0.223, largest difference between hidden units after training = 0.0e+00 (still identical copies)
```

Zero weights give no signal at all (the first layer's gradient is zero because the second layer's weights are zero); equal weights train but stay copies of one another. Random weights are required.

**Random weights of the wrong size: vanishing and exploding signals.** Each layer multiplies the signal by a random matrix. If the matrix is too small the signal shrinks to nothing after a few layers; if too large it explodes. Let us find the right size.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Illustrate why the starting weights matter. Draw a 64-16-10 network with 16 hidden units. Panel one: all weights zero or equal, so the 16 hidden units are identical copies and stay identical after training. Panel two: small random weights, so the units differ and learn different features. Show the validation accuracies 0.10 / 0.22 versus 0.93 and the size of the gap between hidden units."

### 9.2 Variance propagation: the idea behind Xavier and He

Take a layer `z = Σ_{j=1}^{n} w_j a_j` with `n = fan_in` inputs. If the weights and inputs are independent with zero mean, then

```text
Var(z) = n · Var(w) · Var(a)
```

To keep the signal's variance **the same from layer to layer** we need `n · Var(w) = 1`, that is `Var(w) = 1/n`. Two refinements give the standard rules:

| Rule | Variance of weights | For |
|---|---|---|
| **Xavier / Glorot** | `2 / (fan_in + fan_out)` (balances forward and backward signals) | tanh, sigmoid, linear |
| **He / Kaiming** | `2 / fan_in` (ReLU zeroes half of the signal, so double the variance) | ReLU and relatives |

We measure the effect in a deep, wide network: 20 layers of 256 units, random inputs, and the standard deviation of the activations at selected depths.

```python run
def activation_stats(act, std_rule, depth=20, width=256, seed=0, n=512):
    r = np.random.default_rng(seed)
    f = ACTS[act][0]
    a = r.normal(size=(n, width))
    stds = []
    for l in range(depth):
        s = {"0.01": 0.01, "1.0": 1.0, "xavier": math.sqrt(2 / (2 * width)), "he": math.sqrt(2 / width)}[std_rule]
        a = f(a @ r.normal(0, s, (width, width)))
        stds.append(a.std())
    return np.array(stds)

rows = {}
for act in ["tanh", "relu"]:
    for rule in ["0.01", "1.0", "xavier", "he"]:
        s = activation_stats(act, rule)
        rows[f"{act}, std {rule}"] = [s[0], s[4], s[9], s[19]]
print(pd.DataFrame(rows, index=["layer 1", "layer 5", "layer 10", "layer 20"]).T.to_string(float_format=lambda v: f"{v:.3g}"))
```
```text
                  layer 1  layer 5  layer 10  layer 20
tanh, std 0.01      0.156 0.000102  1.08e-08  1.14e-16
tanh, std 1.0       0.975    0.974     0.974     0.974
tanh, std xavier    0.629    0.321      0.23     0.154
tanh, std he        0.722    0.568     0.557     0.552
relu, std 0.01     0.0935 1.59e-05  3.05e-10  1.24e-19
relu, std 1.0        9.35 1.59e+05  3.05e+10  1.24e+21
relu, std xavier    0.585    0.152    0.0277   0.00103
relu, std he        0.827    0.859     0.887      1.05
```

Read the table. With `std = 0.01` the activations collapse to about zero by layer 5 in both nets (vanishing). With `std = 1.0` the `tanh` units saturate at ±1 (every unit stuck at the extremes, with near-zero derivative) and the ReLU activations explode by many orders of magnitude. **Xavier keeps tanh healthy; He keeps ReLU healthy; Xavier is too small for ReLU** (the signal decays by a factor of about √2 each layer, visible over 20 layers).

### 9.3 The same story backwards: gradients

The backward signal is multiplied by the transposed weights, so the same variance argument applies to the gradients that reach the early layers.

```python run
def gradient_norms(act, init, depth=12, width=128, seed=0):
    n_ = MLP([64] + [width] * depth + [10], act=act, init=init, seed=seed)
    n_.loss_and_grads(X_tr[:128], y_tr[:128])
    _, grads = n_.loss_and_grads(X_tr[:128], y_tr[:128])
    return [float(np.linalg.norm(g)) for g in grads[0::2]]                           # norm of dW for each layer, first layer first
rows = {}
for act, init in [("sigmoid", "xavier"), ("tanh", "xavier"), ("relu", "small"), ("relu", "xavier"), ("relu", "he"), ("relu", "large")]:
    g = gradient_norms(act, init)
    rows[f"{act} + {init}"] = [g[0], g[len(g) // 2], g[-1], g[0] / g[-1]]
print(pd.DataFrame(rows, index=["first layer", "middle", "last layer", "first / last"]).T.to_string(float_format=lambda v: f"{v:.2e}"))
```
```text
                  first layer   middle  last layer  first / last
sigmoid + xavier     6.18e-08 3.12e-04    1.26e+00      4.89e-08
tanh + xavier        6.03e-01 5.79e-01    4.45e-01      1.36e+00
relu + small         5.34e-14 5.70e-14    3.96e-14      1.35e+00
relu + xavier        1.66e-02 2.06e-02    1.05e-02      1.58e+00
relu + he            1.01e+00 3.88e+00    4.15e+00      2.43e-01
relu + large         8.45e+10 2.86e+11    3.93e+11      2.15e-01
```

Look at the absolute sizes as well as the ratio. For a healthy network the gradient norms are of order 1 and similar at all depths (tanh with Xavier, ReLU with He). The sigmoid stack loses the gradient before it reaches the first layer (ratio 5e-8). ReLU with a tiny init has a ratio near 1, which looks harmless, but **every** norm is about 1e-14: the whole network receives no signal, so the ratio alone would hide the problem. ReLU with Xavier is too small (norms around 1e-2), and a huge init makes the gradients explode (1e11). This is the numerical form of section 3.2.

### 9.4 Does it matter for the final result

```python run
rows = []
for init in ["small", "xavier", "he"]:
    for act in ["relu", "tanh"]:
        n_ = MLP([64] + [64] * 6 + [10], act=act, init=init, seed=0)
        h = train(n_, X_tr, y_tr, X_val, y_val, epochs=10, lr=2e-3)
        rows.append((act, init, h["train loss"].iloc[0], h["train loss"].iloc[-1], h["val acc"].iloc[-1]))
print(pd.DataFrame(rows, columns=["activation", "init", "loss after epoch 1", "loss after epoch 10", "val accuracy"]).round(4).to_string(index=False))
```
```text
activation   init  loss after epoch 1  loss after epoch 10  val accuracy
      relu  small             2.29940              0.96970       0.58220
      tanh  small             1.87570              1.56220       0.30360
      relu xavier             0.54110              0.00090       0.97210
      tanh xavier             0.32330              0.00400       0.97210
      relu     he             0.76660              0.00100       0.96100
      tanh     he             0.33490              0.00430       0.96380
```

A 7-layer network with a very small initialisation barely trains in 10 epochs; Xavier or He train quickly. (Adam masks part of the problem, because it rescales gradients; with plain SGD the difference is dramatic.) For shallow networks the choice matters little, which is why it was neglected for years, and for deep ones it decides everything.

### 9.5 The referee, and practical defaults

```python run
if HAS_TORCH:
    w = torch.empty(512, 256); torch.nn.init.kaiming_normal_(w, nonlinearity="relu")
    print("torch kaiming_normal_ std %.5f | our He sqrt(2/fan_in) = %.5f" % (w.std().item(), math.sqrt(2 / 256)))
    w = torch.empty(512, 256); torch.nn.init.xavier_normal_(w)
    print("torch xavier_normal_ std %.5f | our Xavier sqrt(2/(fan_in+fan_out)) = %.5f" % (w.std().item(), math.sqrt(2 / (256 + 512))))
```
```text
torch kaiming_normal_ std 0.08830 | our He sqrt(2/fan_in) = 0.08839
torch xavier_normal_ std 0.05114 | our Xavier sqrt(2/(fan_in+fan_out)) = 0.05103
```

| Situation | Initialisation |
|---|---|
| ReLU / leaky ReLU hidden layers | He (normal or uniform) |
| tanh / sigmoid / linear | Xavier |
| Biases | zeros (a small positive bias for ReLU is a rarely needed trick) |
| Last layer before softmax | small weights, so the first loss is near `ln C` |
| With batch normalisation (section 11) | much less sensitive; He is still fine |

Frameworks apply sensible defaults for you. Knowing why they exist tells you where to look when a deep network does not start learning.

### 9.6 Try it

1. Repeat the activation-statistics table with width 64 and width 1024. Does the best standard deviation change as the rule says?
2. Initialise a ReLU network with Xavier and train it with plain SGD (momentum 0.9). Compare with He.

## 10. Regularisation: weight decay, early stopping and dropout

### 10.1 A layer-based design for what comes next

Dropout and batch normalisation behave differently in training and in evaluation, and they sit *between* the linear layers. The tidy way to handle that is to make every building block a small object with a `forward(x, train)` and a `backward(dout)`, and to chain them. This is the design of PyTorch's `nn.Module` and of the project library of section 13. It computes exactly what the `MLP` did.

```python run
class Linear:
    def __init__(self, fan_in, fan_out, init="he", rng=None):
        rng = rng or np.random.default_rng(0)
        std = {"he": math.sqrt(2 / fan_in), "xavier": math.sqrt(2 / (fan_in + fan_out)), "small": 0.01}[init]
        self.W, self.b = rng.normal(0, std, (fan_in, fan_out)), np.zeros(fan_out)
        self.dW, self.db = np.zeros_like(self.W), np.zeros_like(self.b)
    def forward(self, x, train=True): self.x = x; return x @ self.W + self.b
    def backward(self, dout): self.dW, self.db = self.x.T @ dout, dout.sum(0); return dout @ self.W.T
    def params(self): return [self.W, self.b]
    def grads(self): return [self.dW, self.db]

class Activation:
    def __init__(self, name): self.f, self.df = ACTS[name]
    def forward(self, x, train=True): self.x = x; return self.f(x)
    def backward(self, dout): return dout * self.df(self.x)
    def params(self): return []
    def grads(self): return []

class Dropout:
    """Inverted dropout: zero each unit with probability p in training and scale the survivors by 1/(1-p), so evaluation needs no change."""
    def __init__(self, p=0.5, seed=0): self.p, self.rng, self.frozen, self.mask = p, np.random.default_rng(seed), False, None
    def forward(self, x, train=True):
        if not train or self.p == 0: self.mask = None; return x
        if not (self.frozen and self.mask is not None): self.mask = (self.rng.random(x.shape) >= self.p) / (1 - self.p)
        return x * self.mask
    def backward(self, dout): return dout if self.mask is None else dout * self.mask
    def params(self): return []
    def grads(self): return []

class Sequential:
    def __init__(self, layers): self.layers = layers
    def forward(self, x, train=True):
        for l in self.layers: x = l.forward(x, train)
        return x
    def backward(self, dout):
        for l in reversed(self.layers): dout = l.backward(dout)
        return dout
    def params(self): return [p for l in self.layers for p in l.params()]
    def grads(self): return [g for l in self.layers for g in l.grads()]
    def loss_and_grads(self, X, y, train=True):
        logits = self.forward(X, train)
        loss = cross_entropy_with_logits(logits, y)
        self.backward((softmax(logits) - np.eye(logits.shape[1])[y]) / len(y))
        return loss, self.grads()
    def predict(self, X): return self.forward(X, train=False).argmax(1)

def make_net(sizes, act="relu", init="he", dropout=0.0, seed=0, batchnorm=False):
    rng = np.random.default_rng(seed); layers = []
    for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
        layers.append(Linear(a, b, init, rng))
        if i < len(sizes) - 2:
            if batchnorm: layers.append(BatchNorm1d(b))
            layers.append(Activation(act))
            if dropout > 0: layers.append(Dropout(dropout, seed=seed + 100 + i))
    return Sequential(layers)

# the layer-based network and the plain MLP are the same function: copy the weights and compare
ref = MLP([64, 32, 10], act="tanh", seed=4)
lay = Sequential([Linear(64, 32), Activation("tanh"), Linear(32, 10)])
for L, W, b in zip([lay.layers[0], lay.layers[2]], ref.W, ref.b): L.W[:], L.b[:] = W, b
l1, g1 = ref.loss_and_grads(X_tr[:40], y_tr[:40]); l2, g2 = lay.loss_and_grads(X_tr[:40], y_tr[:40])
print("same loss:", np.isclose(l1, l2), "| max gradient difference:", max(float(np.max(np.abs(a - b))) for a, b in zip(g1, g2)))
```
```text
same loss: True | max gradient difference: 0.0
```

The trainer from section 8 needs a small generalisation to accept either kind of network (they share `params`, `loss_and_grads` and `predict`; the `Sequential` exposes `params()` as a method too).

```python run
def train2(net, X, y, Xv, yv, epochs=30, batch=32, lr=1e-3, weight_decay=0.0, l2=0.0, seed=0, optimiser="adam", patience=None):
    r = np.random.default_rng(seed)
    params = net.params()
    opt = Adam(params, lr=lr, weight_decay=weight_decay) if optimiser == "adam" else SGD(params, lr=lr, momentum=0.9)
    hist, best, best_params, bad = [], np.inf, None, 0
    for ep in range(epochs):
        order = r.permutation(len(y))
        for s in range(0, len(y), batch):
            idx = order[s:s + batch]
            loss, grads = net.loss_and_grads(X[idx], y[idx])
            if l2 > 0: grads = [g + l2 * p if p.ndim == 2 else g for g, p in zip(grads, params)]                # L2 penalty on weights, not biases
            opt.step(grads)
        va = cross_entropy_with_logits(net.forward(Xv, train=False), yv)
        hist.append((ep + 1, cross_entropy_with_logits(net.forward(X, train=False), y), va, float(np.mean(net.predict(X) == y)), float(np.mean(net.predict(Xv) == yv))))
        if patience is not None:
            if va < best - 1e-6: best, best_params, bad = va, [p.copy() for p in params], 0
            else: bad += 1
            if bad >= patience: break
    if best_params is not None:
        for p, q in zip(params, best_params): p[:] = q                                                       # restore the best weights
    return pd.DataFrame(hist, columns=["epoch", "train loss", "val loss", "train acc", "val acc"]).set_index("epoch")

# the overfitting setup of 8.4: 150 training examples, a wide network
def small_run(**kw):
    net = make_net([64, 128, 128, 10], seed=0, dropout=kw.pop("dropout", 0.0))
    h = train2(net, Xs_small, ys_small, X_val, y_val, epochs=kw.pop("epochs", 100), lr=2e-3, **kw)
    return net, h
net0, h0 = small_run()
print(f"no regularisation: train acc {h0['train acc'].iloc[-1]:.2f}, val acc {h0['val acc'].iloc[-1]:.3f}, val loss {h0['val loss'].iloc[-1]:.3f}, weight norm {np.sqrt(sum((w ** 2).sum() for w in net0.params() if w.ndim == 2)):.1f}")
```
```text
no regularisation: train acc 1.00, val acc 0.894, val loss 0.427, weight norm 23.9
```

### 10.2 Weight decay and L2 regularisation

Adding `(λ/2)‖W‖²` to the loss penalises large weights: the model must justify every large weight by a real reduction of the loss, which favours smooth, simple functions. The gradient of the penalty is `λW`, so the update shrinks ("decays") every weight a little at each step. Biases are usually not penalised.

```python run
rows = []
for lam in [0.0, 1e-4, 1e-3, 1e-2, 3e-2]:
    net_, h_ = small_run(l2=lam)
    rows.append((lam, h_["train acc"].iloc[-1], h_["val acc"].iloc[-1], h_["val loss"].iloc[-1], np.sqrt(sum((w ** 2).sum() for w in net_.params() if w.ndim == 2))))
print(pd.DataFrame(rows, columns=["L2 strength", "train acc", "val acc", "val loss", "weight norm"]).round(4).to_string(index=False))
```
```text
 L2 strength  train acc  val acc  val loss  weight norm
     0.00000    1.00000  0.89420   0.42680     23.93570
     0.00010    1.00000  0.89690   0.37970     22.02300
     0.00100    1.00000  0.89420   0.31780     15.91710
     0.01000    1.00000  0.88580   0.32030      6.76030
     0.03000    1.00000  0.88860   0.38450      5.65450
```

The penalty does what it should to the weights: the norm falls from 24 to 6, and the validation **loss** improves clearly (0.43 to 0.32). The validation **accuracy** hardly moves (0.89 throughout; differences of a point are noise on 359 images), because the loss measures confidence and accuracy only counts hard decisions. Too strong a penalty eventually underfits. Tune it on the validation loss, like any hyperparameter, and do not expect miracles on a problem this easy.

**L2 in the loss versus decoupled weight decay.** For plain SGD the two are the same. For Adam they are not: with L2 in the loss, the penalty gradient goes *through Adam's per-parameter rescaling*, so weights with large gradients are decayed less. **AdamW** applies the decay directly to the weights, outside the rescaling, and is the version in widespread use.

```python run
w0 = np.array([2.0, -1.0, 0.5]); g_loss = np.array([10.0, 0.01, 1.0]); lam, lr = 0.1, 0.01
sgd_l2 = w0 - lr * (g_loss + lam * w0); sgd_wd = w0 - lr * g_loss - lr * lam * w0
print("SGD: L2-in-loss and weight decay give identical updates:", bool(np.allclose(sgd_l2, sgd_wd)))
def adam_first_step(w, g, lr, wd_decoupled=0.0):                                       # one Adam step from zero state (bias-corrected m/sqrt(v) = sign(g) at the first step)
    return w - lr * (g / (np.abs(g) + 1e-8)) - lr * wd_decoupled * w
adam_l2 = adam_first_step(w0, g_loss + lam * w0, lr); adamw = adam_first_step(w0, g_loss, lr, wd_decoupled=lam)
print("Adam, L2 in the loss  : change of each weight", np.round(adam_l2 - w0, 5))
print("AdamW, decoupled decay: change of each weight", np.round(adamw - w0, 5), "<- decay proportional to the weight, independent of its gradient size")
```
```text
SGD: L2-in-loss and weight decay give identical updates: True
Adam, L2 in the loss  : change of each weight [-0.01  0.01 -0.01]
AdamW, decoupled decay: change of each weight [-0.012  -0.009  -0.0105] <- decay proportional to the weight, independent of its gradient size
```

### 10.3 Early stopping

Training error keeps falling, but validation error bottoms out and rises (8.4). **Early stopping** watches the validation loss and stops after it has failed to improve for `patience` epochs, then restores the best weights. It costs nothing and acts as a regulariser.

```python run
net_es, h_es = small_run(patience=8, epochs=200)
best_ep = int(h_es["val loss"].idxmin())
print(f"stopped after {len(h_es)} epochs; best validation loss at epoch {best_ep}; restored weights give val acc {float(np.mean(net_es.predict(X_val) == y_val)):.3f} (without stopping: {h0['val acc'].iloc[-1]:.3f})")
print(f"test accuracy with early stopping: {float(np.mean(net_es.predict(X_te) == y_te)):.3f} | without: {float(np.mean(net0.predict(X_te) == y_te)):.3f}")
```
```text
stopped after 52 epochs; best validation loss at epoch 44; restored weights give val acc 0.889 (without stopping: 0.894)
test accuracy with early stopping: 0.914 | without: 0.914
```

Here early stopping reaches the same accuracy (0.914 on test) in 52 epochs instead of 100, which is the usual benefit: the same result for half the work, and protection against training too long on harder problems. Keep the validation set separate from the test set (ds.03): early stopping uses the validation set to choose, so its score is slightly optimistic.

### 10.4 Dropout

During training, **dropout** randomly switches off each hidden unit with probability `p`. Units cannot rely on particular other units being there, so they must learn robust, redundant features, much as an ensemble of many thinned networks averages out individual errors. Two details are essential:

1. **Inverted scaling.** The survivors are multiplied by `1/(1−p)` during training so that the expected activation stays the same; at evaluation time dropout is simply switched off with no change of scale.
2. **Train versus evaluation mode.** Forgetting to switch it off at prediction time gives noisy, worse predictions.

```python run
rng = np.random.default_rng(0)
x_ = np.ones((200_000, 1)) * 3.0
d = Dropout(0.5, seed=1)
y_ = d.forward(x_, train=True)
print(f"training mode: about half the units are zero ({(y_ == 0).mean():.3f}), survivors are scaled to {y_[y_ > 0][0]:.1f}; mean output {y_.mean():.3f} (input mean 3.000)")
print("evaluation mode returns the input unchanged:", bool(np.array_equal(d.forward(x_, train=False), x_)))
# gradient check with the mask frozen, so the forward pass is deterministic during the numerical differences
net_g = make_net([64, 20, 10], act="tanh", dropout=0.3, seed=2)
for l in net_g.layers:
    if isinstance(l, Dropout): l.frozen = True
net_g.forward(X_tr[:10], train=True)
_, gr = net_g.loss_and_grads(X_tr[:10], y_tr[:10])
num = [numerical_grad(lambda: cross_entropy_with_logits(net_g.forward(X_tr[:10], train=True), y_tr[:10]), p) for p in net_g.params()]
print("gradient check through dropout (mask frozen): worst relative error %.1e" % max(float(np.max(np.abs(a - b) / np.maximum(np.abs(a) + np.abs(b), 1e-12))) for a, b in zip(gr, num)))
```
```text
training mode: about half the units are zero (0.501), survivors are scaled to 6.0; mean output 2.996 (input mean 3.000)
evaluation mode returns the input unchanged: True
gradient check through dropout (mask frozen): worst relative error 7.2e-07
```

> **Predict the output.** On the small-data overfitting problem, will dropout of 0.5 improve the validation accuracy of the big network, and what will happen to its *training* accuracy?

<details><summary>Answer</summary>

Less than you might hope. At `p = 0.5` the validation accuracy edges up (0.894 to 0.900) but the validation loss does not improve, `p = 0.7` is worse, and the training accuracy with dropout off stays at 100%. On one run of this small problem the differences are within noise. Dropout is a regulariser whose benefit shows up in averages over seeds (section 13.6 repeats the comparison five times and finds a clear gain), not in a single run. Never conclude from one seed.

```python run
rows = []
for p in [0.0, 0.2, 0.5, 0.7]:
    net_, h_ = small_run(dropout=p)
    rows.append((p, h_["train acc"].iloc[-1], h_["val acc"].iloc[-1], h_["val loss"].iloc[-1]))
print(pd.DataFrame(rows, columns=["dropout p", "train acc (dropout off)", "val acc", "val loss"]).round(4).to_string(index=False))
```
```text
 dropout p  train acc (dropout off)  val acc  val loss
   0.00000                  1.00000  0.89420   0.42680
   0.20000                  1.00000  0.89420   0.48960
   0.50000                  1.00000  0.89970   0.44370
   0.70000                  1.00000  0.87470   0.41290
```

</details>

The mistake to avoid: predicting with dropout still on.

```python run
net_d, _ = small_run(dropout=0.5)
logits_on = [net_d.forward(X_val, train=True) for _ in range(5)]
print("same input, 5 predictions with dropout left ON agree with each other on", round(float(np.mean([np.array_equal(logits_on[0].argmax(1), l.argmax(1)) for l in logits_on[1:]])) * 100), "% of runs")
print(f"accuracy with dropout ON at test time {float(np.mean(logits_on[0].argmax(1) == y_val)):.3f} vs OFF {float(np.mean(net_d.predict(X_val) == y_val)):.3f}")
```
```text
same input, 5 predictions with dropout left ON agree with each other on 0 % of runs
accuracy with dropout ON at test time 0.808 vs OFF 0.900
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate dropout with p = 0.5 on a hidden layer of 10 units. Over five training steps, randomly grey out about half the units and show the survivors scaled by 1/(1-p) = 2, so the mean output stays the same (for example input 3.0 becomes 6.0 or 0). Then show the evaluation step, with all units on and no scaling. Label train mode and eval mode."

### 10.5 Data augmentation and noise

More (varied) training data is the best regulariser. When you cannot collect more, you can **create** examples by applying label-preserving changes. For small digit images: shift by one pixel.

```python run
def augment(X, y, rng, copies=3):
    imgs = X.reshape(-1, 8, 8)
    outs, labs = [X], [y]
    for _ in range(copies):
        dx, dy = rng.integers(-1, 2, 2)
        outs.append(np.roll(imgs, (dy, dx), axis=(1, 2)).reshape(len(X), 64)); labs.append(y)
    return np.vstack(outs), np.concatenate(labs)
Xa, ya = augment(Xs_small, ys_small, np.random.default_rng(0), copies=4)
net_a = make_net([64, 128, 128, 10], seed=0)
h_a = train2(net_a, Xa, ya, X_val, y_val, epochs=60, lr=2e-3)
print(f"150 images: val acc {h0['val acc'].iloc[-1]:.3f}  |  750 images (150 shifted by up to a pixel): val acc {h_a['val acc'].iloc[-1]:.3f}")
rngn = np.random.default_rng(1)
Xn = np.vstack([Xs_small] + [Xs_small + rngn.normal(0, 0.3, Xs_small.shape) for _ in range(4)]); yn = np.tile(ys_small, 5)      # small pixel noise instead of shifts
net_n = make_net([64, 128, 128, 10], seed=0)
h_n = train2(net_n, Xn, yn, X_val, y_val, epochs=60, lr=2e-3)
print(f"750 images (150 with small random pixel noise added): val acc {h_n['val acc'].iloc[-1]:.3f}")
```
```text
150 images: val acc 0.894  |  750 images (150 shifted by up to a pixel): val acc 0.864
750 images (150 with small random pixel noise added): val acc 0.894
```

An augmentation helps only if the new examples look like variations that really occur. The images here are 8x8 and always centred, so a shift of one pixel (12% of the image) produces digits that the validation images never resemble: it moved the model's attention away from what the test data look like, and the accuracy went **down**. Adding mild pixel noise instead left the accuracy exactly where it was (0.894): harmless, and no gain on a problem this easy. Choose augmentations from knowledge of the data, and check each one on the validation set; do not assume that "more data" means "better".

### 10.6 Which regulariser when

| Technique | Cost | Typical use |
|---|---|---|
| **Weight decay** (AdamW) | none | nearly always, small value |
| **Early stopping** | validation set | always, as a safety net |
| **Dropout** | slower convergence | fully connected layers, small data |
| **Data augmentation** | design effort | images, audio: very effective |
| **Smaller or shallower network** | less capacity | first thing to try for overfitting |
| **More data** | collection effort | the best cure |

### 10.7 Try it

1. Combine dropout 0.3 with weight decay 1e-3 and early stopping. Is the result better than each alone?
2. Implement label smoothing (replace the one-hot target by 0.9 / 0.1 spread over the other classes) in the loss and check its gradient numerically.

## 11. Batch normalisation

### 11.1 The idea

Deep networks are hard to train because the distribution of the inputs to each layer keeps changing as the layers before it change, and because badly scaled activations make the loss surface a narrow ravine. **Batch normalisation** (batch norm) standardises each feature of a layer's input across the mini-batch, then lets the network rescale it:

```text
μ = mean over the batch      σ² = variance over the batch
x̂ = (x − μ) / sqrt(σ² + ε)   y = γ · x̂ + β          (γ and β are learned, one per feature)
```

Each feature now has mean 0 and variance 1 going into the activation, whatever the layers before did. The learned `γ` and `β` let the network undo the normalisation if that is best. In practice batch norm makes training faster, tolerates larger learning rates, makes the result less sensitive to initialisation, and has a mild regularising effect (the batch statistics are noisy).

At **evaluation time** the batch may be a single example, so statistics from the batch cannot be used. During training the layer therefore keeps **running averages** of the means and variances, and evaluation uses those.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a batch normalisation layer on one feature. Show a histogram of the feature values over a batch with some mean and spread, then a second histogram after x_hat = (x - mean) / sqrt(variance + eps), centred at 0 with variance 1, then a third after y = gamma * x_hat + beta. Add a note on the running averages that replace the batch statistics at evaluation time."

### 11.2 Backpropagation through batch norm

Every output in a batch depends on the batch mean and variance, so the backward pass has a coupling term. With `N` examples, `dx̂ = dy · γ`:

```text
dγ = Σ dy · x̂          dβ = Σ dy          dx = (1/N) · (1/σ) · [ N · dx̂ − Σ dx̂ − x̂ · Σ (dx̂ · x̂) ]
```

```python run
class BatchNorm1d:
    def __init__(self, n, momentum=0.1, eps=1e-5):
        self.gamma, self.beta = np.ones(n), np.zeros(n)
        self.dgamma, self.dbeta = np.zeros(n), np.zeros(n)
        self.running_mean, self.running_var = np.zeros(n), np.ones(n)
        self.momentum, self.eps = momentum, eps
    def forward(self, x, train=True):
        if train:
            mu, var = x.mean(0), x.var(0)                                   # biased variance, as used for normalising
            self.xhat = (x - mu) / np.sqrt(var + self.eps)
            self.inv_std = 1 / np.sqrt(var + self.eps)
            n = len(x)
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mu
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var * n / max(n - 1, 1)     # unbiased for the running estimate
        else:
            self.xhat = (x - self.running_mean) / np.sqrt(self.running_var + self.eps)
        return self.gamma * self.xhat + self.beta
    def backward(self, dout):
        n = len(dout)
        self.dgamma, self.dbeta = (dout * self.xhat).sum(0), dout.sum(0)
        dxhat = dout * self.gamma
        return self.inv_std / n * (n * dxhat - dxhat.sum(0) - self.xhat * (dxhat * self.xhat).sum(0))
    def params(self): return [self.gamma, self.beta]
    def grads(self): return [self.dgamma, self.dbeta]

rng = np.random.default_rng(0)
X_ = rng.normal(3.0, 2.0, (32, 6))
bn = BatchNorm1d(6); out = bn.forward(X_)
print("after normalisation: feature means", out.mean(0).round(6), "| feature stds", out.std(0).round(4))
up = rng.normal(size=out.shape)                                              # an arbitrary upstream gradient
dx = bn.backward(up)
f = lambda: float((BatchNorm1d(6).forward(X_) * up).sum())
print("backward check against finite differences: max |dx - numerical| =", float(np.max(np.abs(dx - numerical_grad(f, X_)))))
if HAS_TORCH:
    tb = torch.nn.BatchNorm1d(6, momentum=0.1, eps=1e-5).double()
    tx = torch.tensor(X_, requires_grad=True)
    ty = tb(tx); (ty * torch.tensor(up)).sum().backward()
    print("PyTorch referee: output equal", bool(np.allclose(ty.detach().numpy(), out)), "| dx equal", bool(np.allclose(tx.grad.numpy(), dx, atol=1e-10)),
          "| dgamma equal", bool(np.allclose(tb.weight.grad.numpy(), bn.dgamma)), "| running variance equal", bool(np.allclose(tb.running_var.numpy(), bn.running_var)))
    tb.eval(); bn_eval = bn.forward(X_[:3], train=False)
    print("evaluation mode (running statistics) equal to torch:", bool(np.allclose(tb(torch.tensor(X_[:3])).detach().numpy(), bn_eval)))
```
```text
after normalisation: feature means [-0. -0. -0. -0. -0.  0.] | feature stds [1. 1. 1. 1. 1. 1.]
backward check against finite differences: max |dx - numerical| = 3.601275201658982e-09
PyTorch referee: output equal True | dx equal True | dgamma equal True | running variance equal True
evaluation mode (running statistics) equal to torch: True
```

(PyTorch's running variance uses the unbiased estimate, `N/(N−1)` times the biased one; our implementation matches that detail, which is the sort of thing a referee reveals.)

### 11.3 What batch norm buys: deep networks and large learning rates

We train a deliberately awkward network: 8 hidden layers, a poor initialisation (standard deviation 0.05), and plain SGD with momentum at a fairly large learning rate. Then the same with batch norm.

> **Predict the output.** A 9-layer `tanh` network whose weights were initialised too small (standard deviation 0.05) is trained with SGD at three learning rates, once plainly and once with batch norm. Which of the six runs do you expect to learn something?

<details><summary>Answer</summary>

All three batch-norm runs learn (validation accuracy 0.87 to 0.96). None of the plain runs does: with weights that small the signal shrinks to nothing across nine layers, the gradient does the same on the way back, and the loss stays exactly at `ln 10` whatever the learning rate. Batch norm re-standardises the signal at every layer, so the shrinking never happens.

</details>

```python run
def awkward(batchnorm, lr, act="tanh", epochs=8, seed=0):
    net = make_net([64] + [64] * 8 + [10], act=act, init="small", seed=seed, batchnorm=batchnorm)
    for l in net.layers:
        if isinstance(l, Linear): l.W *= 5.0                                         # std 0.05
    h = train2(net, X_tr, y_tr, X_val, y_val, epochs=epochs, lr=lr, optimiser="sgd")
    return h
rows = []
for bnorm in [False, True]:
    for lr in [0.003, 0.03, 0.3]:
        h = awkward(bnorm, lr)
        rows.append(("with batch norm" if bnorm else "plain", lr, h["train loss"].iloc[-1], h["val acc"].iloc[-1]))
print(pd.DataFrame(rows, columns=["network", "SGD learning rate", "train loss after 8 epochs", "val accuracy"]).round(4).to_string(index=False))
```
```text
        network  SGD learning rate  train loss after 8 epochs  val accuracy
          plain            0.00300                    2.30250       0.10030
          plain            0.03000                    2.30210       0.10030
          plain            0.30000                    6.60950       0.19220
with batch norm            0.00300                    0.06470       0.95820
with batch norm            0.03000                    0.08140       0.94150
with batch norm            0.30000                    0.21790       0.87190
```

Without batch norm this 9-layer tanh network with a poor initialisation does not learn at all: the loss stays at `ln 10 = 2.30` and the accuracy at chance, at every learning rate. With batch norm it trains at all three rates (the best at the smaller ones; at 0.3 it is worse, 0.87, but it still learns). Batch norm turns a delicate optimisation into a robust one.

### 11.4 Where it sits, and its pitfalls

| Detail | Guidance |
|---|---|
| **Position** | after the linear layer, before the activation (the original recipe); some use it after the activation; test both |
| **Bias before BN** | redundant (BN's `β` replaces it) |
| **Small batches** | batch statistics get noisy; below about 16 examples batch norm hurts |
| **Train vs eval** | the single biggest source of bugs: call evaluation with the running statistics |
| **With dropout** | the two interact awkwardly (dropout changes the variance that BN estimates); many modern networks drop dropout when using BN |
| **Distribution shift** | the running statistics come from the training data; very different test data gets mis-normalised |
| **Recurrent / transformer models** | batch statistics are awkward for sequences; use layer normalisation |

**Layer normalisation** normalises across the *features of one example* instead of across the batch, so it needs no batch, no running averages and behaves identically in training and evaluation. It is the standard in transformers (ml.04).

```python run
def layer_norm(x, gamma, beta, eps=1e-5):
    mu, var = x.mean(1, keepdims=True), x.var(1, keepdims=True)
    return gamma * (x - mu) / np.sqrt(var + eps) + beta
Xl = np.random.default_rng(1).normal(2.0, 3.0, (4, 10))
out = layer_norm(Xl, np.ones(10), np.zeros(10))
print("each EXAMPLE has mean 0 / std 1 afterwards:", out.mean(1).round(6), out.std(1).round(4))
if HAS_TORCH:
    print("equal to torch.nn.LayerNorm:", bool(np.allclose(out, torch.nn.LayerNorm(10, eps=1e-5).double()(torch.tensor(Xl)).detach().numpy())))
print("a single example gives the same answer alone or inside a batch:", bool(np.allclose(layer_norm(Xl[:1], np.ones(10), np.zeros(10)), out[:1])))
```
```text
each EXAMPLE has mean 0 / std 1 afterwards: [-0.  0.  0. -0.] [1. 1. 1. 1.]
equal to torch.nn.LayerNorm: True
a single example gives the same answer alone or inside a batch: True
```

### 11.5 Try it

1. Add batch norm to the small-data overfitting experiment of 8.4. Does it help or hurt generalisation?
2. Call the batch-norm layer in evaluation mode *before* any training step (running mean 0, variance 1). What does it do to the input?

## 12. Debugging a network that will not learn

### 12.1 A systematic checklist

A neural network that silently trains badly is the normal outcome of the first attempt. The cure is a fixed sequence of cheap checks, run **before** long training:

| # | Check | What it catches |
|---|---|---|
| 1 | **Initial loss** equals `ln C` (classification) or the variance of the target (regression) | wrong output scale, a loss bug, wrong labels |
| 2 | **Overfit one small batch** to ~zero loss | a bug anywhere in the forward, backward or update; too little capacity |
| 3 | **Gradient check** on a tiny network | an incorrect backward pass |
| 4 | **Gradient norm per layer** at initialisation | vanishing or exploding gradients, a wrong initialisation |
| 5 | **Update-to-weight ratio** (about 1e-3 per step) | learning rate far too large or too small |
| 6 | **Dead units** (share of ReLU units that never fire) | too high a learning rate, bad bias |
| 7 | **Data checks**: inputs scaled, labels aligned, no leakage, train/validation split sane | the most common real cause of "it does not learn" |
| 8 | **Loss curve** shape (training and validation) | under/overfitting, instability |

```python run
def diagnose(net, X, y, n_classes=10, lr=1e-3):
    rep = {}
    loss0, grads = net.loss_and_grads(X[:256], y[:256])
    rep["initial loss (expect ln C = %.2f)" % math.log(n_classes)] = round(loss0, 3)
    gn = [float(np.linalg.norm(g)) for g in grads[0::2]]
    rep["gradient norm first / last layer"] = f"{gn[0]:.2e} / {gn[-1]:.2e}"
    wn = [float(np.linalg.norm(p)) for p in net.params()[0::2]]
    rep["update / weight ratio (lr * |grad| / |W|), first layer"] = f"{lr * gn[0] / max(wn[0], 1e-12):.1e}"
    net.forward(X[:256])
    dead = []
    for l in net.layers if hasattr(net, "layers") else []:
        if isinstance(l, Activation) and l.f is relu: dead.append(float(np.mean((l.x > 0).sum(0) == 0)))
    if dead: rep["share of dead ReLU units per layer"] = np.round(dead, 2).tolist()
    # overfit one batch
    b = 32; r = np.random.default_rng(0); idx = r.choice(len(X), b, replace=False)
    opt = Adam(net.params(), lr=lr * 5)
    for _ in range(150):
        _, g = net.loss_and_grads(X[idx], y[idx]); opt.step(g)
    rep["loss after trying to overfit ONE batch of 32 (expect ~0)"] = round(cross_entropy_with_logits(net.forward(X[idx], train=False), y[idx]), 4)
    return rep

healthy = make_net([64, 64, 32, 10], seed=0)
bad_labels = y_tr.copy(); np.random.default_rng(0).shuffle(bad_labels)
cases = {
    "healthy": (make_net([64, 64, 32, 10], seed=0), X_tr, y_tr, 1e-3),
    "zero initialisation": (Sequential([Linear(64, 64, "small"), Activation("relu"), Linear(64, 32, "small"), Activation("relu"), Linear(32, 10, "small")]), X_tr, y_tr, 1e-3),
    "unscaled inputs (x 20)": (make_net([64, 64, 32, 10], seed=0), X_tr * 20, y_tr, 1e-3),
    "learning rate 100x too high": (make_net([64, 64, 32, 10], seed=0), X_tr, y_tr, 0.1),
    "labels shuffled (a data bug)": (make_net([64, 64, 32, 10], seed=0), X_tr, bad_labels, 1e-3),
}
for name, (net_, X_, y_, lr_) in cases.items():
    if name == "zero initialisation":
        for l in net_.layers:
            if isinstance(l, Linear): l.W[:] = 0.0
    print(f"--- {name}")
    for k, v in diagnose(net_, X_, y_, lr=lr_).items(): print(f"    {k}: {v}")
```
```text
--- healthy
    initial loss (expect ln C = 2.30): 3.105
    gradient norm first / last layer: 1.29e+00 / 1.37e+00
    update / weight ratio (lr * |grad| / |W|), first layer: 1.1e-04
    share of dead ReLU units per layer: [0.0, 0.0]
    loss after trying to overfit ONE batch of 32 (expect ~0): 0.0003
--- zero initialisation
    initial loss (expect ln C = 2.30): 2.303
    gradient norm first / last layer: 0.00e+00 / 0.00e+00
    update / weight ratio (lr * |grad| / |W|), first layer: 0.0e+00
    share of dead ReLU units per layer: [1.0, 1.0]
    loss after trying to overfit ONE batch of 32 (expect ~0): 2.2633
--- unscaled inputs (x 20)
    initial loss (expect ln C = 2.30): 40.429
    gradient norm first / last layer: 3.12e+01 / 4.43e+01
    update / weight ratio (lr * |grad| / |W|), first layer: 2.8e-03
    share of dead ReLU units per layer: [0.0, 0.0]
    loss after trying to overfit ONE batch of 32 (expect ~0): 0.0
--- learning rate 100x too high
    initial loss (expect ln C = 2.30): 3.105
    gradient norm first / last layer: 1.29e+00 / 1.37e+00
    update / weight ratio (lr * |grad| / |W|), first layer: 1.1e-02
    share of dead ReLU units per layer: [0.0, 0.0]
    loss after trying to overfit ONE batch of 32 (expect ~0): 2.0225
--- labels shuffled (a data bug)
    initial loss (expect ln C = 2.30): 2.941
    gradient norm first / last layer: 7.47e-01 / 1.03e+00
    update / weight ratio (lr * |grad| / |W|), first layer: 6.6e-05
    share of dead ReLU units per layer: [0.0, 0.0]
    loss after trying to overfit ONE batch of 32 (expect ~0): 0.0008
```

Read each case against the table of symptoms. Zero initialisation: the gradient of the first layers is exactly zero and the single batch cannot be overfit. Unscaled inputs: an enormous initial loss (40 instead of about 2.3), caught by check 1; the single batch can still be memorised, so check 2 alone would not notice. A learning rate far too high: the update-to-weight ratio is huge and the one-batch test fails or diverges. **Shuffled labels**: the network *can* overfit one batch (it memorises 32 examples), but on the real task it learns nothing; test 2 alone would pass, which is why you must also compare the validation curve to a baseline.

Notes on the healthy case: the initial loss of a He-initialised network (3.1 here) is above `ln C = 2.30` because the logits are not small; that is acceptable. What matters is that it is of the same order, not 30 or 0.01. Every other number is in a sensible range, and the single batch is memorised (loss 0.0003).

### 12.2 The slow check: shuffled labels on the whole task

```python run
net_s = make_net([64, 64, 32, 10], seed=0)
h = train2(net_s, X_tr, bad_labels, X_val, y_val, epochs=30, lr=2e-3)
print(f"labels shuffled: train acc {h['train acc'].iloc[-1]:.2f} (the network memorises), val acc {h['val acc'].iloc[-1]:.2f} (chance is 0.10): memorisation without learning")
```
```text
labels shuffled: train acc 0.72 (the network memorises), val acc 0.11 (chance is 0.10): memorisation without learning
```

### 12.3 Loss curves, in words

| What you see | Likely cause | First action |
|---|---|---|
| Loss does not move from `ln C` | learning rate too small, zero gradients, dead network, labels wrong | one-batch overfit; gradient norms |
| Loss goes to `nan` or `inf` | learning rate too high, exploding gradients, `log(0)` | lower the rate; clip the gradient norm; stable loss |
| Training loss falls, validation flat or rising | overfitting | regularise, get more data, stop earlier |
| Both losses high and equal | underfitting | bigger model, train longer, better features |
| Loss jumps up periodically | a bad batch, a too-high rate late in training | lower the rate, schedule it |
| Training accuracy 100%, validation at chance | a data or split bug, memorisation | check labels and leakage |

### 12.4 Try it

1. Add a learning-rate range test to `diagnose` and print the rate at which the loss starts to climb.
2. Break the network in a way not listed (for example, apply dropout at test time) and see which check catches it.


## 13. Project: a neural-network library in NumPy

### 13.1 The brief

Assemble everything into a small, clean, **tested** library, `nnlib`, with the structure of a real framework:

1. **Layers** with `forward(x, train)` and `backward(dout)`: `Linear`, activations (`ReLU`, `LeakyReLU`, `Tanh`, `Sigmoid`), `Dropout`, `BatchNorm1d`, and a `Sequential` container.
2. **Losses** that return both the value and the gradient with respect to the network output: softmax cross-entropy, binary cross-entropy with logits, mean squared error.
3. **Optimisers**: SGD (momentum, Nesterov, weight decay), RMSProp, Adam/AdamW.
4. **A trainer** with mini-batches, a learning-rate schedule, early stopping and a fixed seed.
5. **Gradient checking, saving and loading.**
6. **Tests** that guard every property of this chapter: every layer's gradient passes the numerical check; the layers, losses and optimisers agree with PyTorch; dropout and batch norm behave differently in training and evaluation; the network can overfit one batch; a seed gives identical results; a saved model predicts identically.

The standard to meet: a reader should be able to trust any number that comes out of the library because a test would have caught the bug.

### 13.2 The library

```python run
import pathlib, tempfile, subprocess, os
proj = pathlib.Path(tempfile.mkdtemp()) / "nnlib_project"
proj.mkdir()
(proj / "nnlib.py").write_text('''"""nnlib: a small neural-network library in NumPy (layers, losses, optimisers, trainer, gradient check)."""
import math
import numpy as np


# ---------------- numerics ----------------
def sigmoid(z):
    z = np.asarray(z, float); out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1 / (1 + np.exp(-z[pos])); ez = np.exp(z[~pos]); out[~pos] = ez / (1 + ez)
    return out


def softmax(z):
    e = np.exp(z - z.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def log_softmax(z):
    m = z.max(axis=-1, keepdims=True)
    return z - m - np.log(np.exp(z - m).sum(axis=-1, keepdims=True))


# ---------------- layers ----------------
class Layer:
    def params(self): return []
    def grads(self): return []
    def state(self): return self.params()


class Linear(Layer):
    def __init__(self, fan_in, fan_out, init="he", rng=None):
        rng = rng if rng is not None else np.random.default_rng(0)
        std = {"he": math.sqrt(2 / fan_in), "xavier": math.sqrt(2 / (fan_in + fan_out)), "small": 0.01}[init]
        self.W, self.b = rng.normal(0, std, (fan_in, fan_out)), np.zeros(fan_out)
        self.dW, self.db = np.zeros_like(self.W), np.zeros_like(self.b)

    def forward(self, x, train=True):
        self.x = x
        return x @ self.W + self.b

    def backward(self, dout):
        self.dW, self.db = self.x.T @ dout, dout.sum(0)
        return dout @ self.W.T

    def params(self): return [self.W, self.b]
    def grads(self): return [self.dW, self.db]


class _Elementwise(Layer):
    def forward(self, x, train=True):
        self.x = x
        return self.f(x)

    def backward(self, dout):
        return dout * self.df(self.x)


class ReLU(_Elementwise):
    f = staticmethod(lambda x: np.maximum(x, 0.0))
    df = staticmethod(lambda x: (x > 0).astype(float))


class LeakyReLU(_Elementwise):
    def __init__(self, slope=0.01): self.slope = slope
    def f(self, x): return np.where(x > 0, x, self.slope * x)
    def df(self, x): return np.where(x > 0, 1.0, self.slope)


class Tanh(_Elementwise):
    f = staticmethod(np.tanh)
    df = staticmethod(lambda x: 1 - np.tanh(x) ** 2)


class Sigmoid(_Elementwise):
    f = staticmethod(sigmoid)
    df = staticmethod(lambda x: sigmoid(x) * (1 - sigmoid(x)))


class Dropout(Layer):
    """Inverted dropout. `frozen=True` re-uses the last mask (for gradient checks)."""
    def __init__(self, p=0.5, seed=0):
        self.p, self.rng, self.frozen, self.mask = p, np.random.default_rng(seed), False, None

    def forward(self, x, train=True):
        if not train or self.p == 0:
            self.mask = None
            return x
        if not (self.frozen and self.mask is not None):
            self.mask = (self.rng.random(x.shape) >= self.p) / (1 - self.p)
        return x * self.mask

    def backward(self, dout):
        return dout if self.mask is None else dout * self.mask


class BatchNorm1d(Layer):
    def __init__(self, n, momentum=0.1, eps=1e-5):
        self.gamma, self.beta = np.ones(n), np.zeros(n)
        self.dgamma, self.dbeta = np.zeros(n), np.zeros(n)
        self.running_mean, self.running_var = np.zeros(n), np.ones(n)
        self.momentum, self.eps = momentum, eps

    def forward(self, x, train=True):
        if train:
            mu, var = x.mean(0), x.var(0)
            self.inv_std = 1 / np.sqrt(var + self.eps)
            self.xhat = (x - mu) * self.inv_std
            n = len(x)
            self.running_mean = (1 - self.momentum) * self.running_mean + self.momentum * mu
            self.running_var = (1 - self.momentum) * self.running_var + self.momentum * var * n / max(n - 1, 1)
        else:
            self.xhat = (x - self.running_mean) / np.sqrt(self.running_var + self.eps)
        return self.gamma * self.xhat + self.beta

    def backward(self, dout):
        n = len(dout)
        self.dgamma, self.dbeta = (dout * self.xhat).sum(0), dout.sum(0)
        dxhat = dout * self.gamma
        return self.inv_std / n * (n * dxhat - dxhat.sum(0) - self.xhat * (dxhat * self.xhat).sum(0))

    def params(self): return [self.gamma, self.beta]
    def grads(self): return [self.dgamma, self.dbeta]
    def state(self): return [self.gamma, self.beta, self.running_mean, self.running_var]


class Sequential(Layer):
    def __init__(self, *layers): self.layers = list(layers)

    def forward(self, x, train=True):
        for l in self.layers: x = l.forward(x, train)
        return x

    def backward(self, dout):
        for l in reversed(self.layers): dout = l.backward(dout)
        return dout

    def params(self): return [p for l in self.layers for p in l.params()]
    def grads(self): return [g for l in self.layers for g in l.grads()]
    def state(self): return [s for l in self.layers for s in l.state()]
    def predict(self, X): return self.forward(X, train=False).argmax(1)


# ---------------- losses: __call__(output, target) -> (mean loss, d loss / d output) ----------------
class SoftmaxCrossEntropy:
    def __call__(self, logits, y):
        n = len(y)
        loss = -np.mean(log_softmax(logits)[np.arange(n), y])
        d = softmax(logits); d[np.arange(n), y] -= 1
        return float(loss), d / n


class BCEWithLogits:
    def __call__(self, logits, y):
        z = logits.reshape(-1); y = np.asarray(y, float).reshape(-1)
        loss = np.mean(np.maximum(z, 0) - z * y + np.log1p(np.exp(-np.abs(z))))
        return float(loss), ((sigmoid(z) - y) / len(y)).reshape(logits.shape)


class MSE:
    def __call__(self, pred, y):
        y = np.asarray(y, float).reshape(pred.shape)
        return float(0.5 * np.mean((pred - y) ** 2)), (pred - y) / pred.size


# ---------------- optimisers: step(grads) updates the parameter arrays IN PLACE ----------------
class Optimizer:
    def __init__(self, params, lr, weight_decay=0.0):
        self.params, self.lr, self.wd, self.t = params, lr, weight_decay, 0

    def step(self, grads):
        self.t += 1
        for i, (p, g) in enumerate(zip(self.params, grads)):
            p -= self._update(i, g)
            if self.wd and p.ndim >= 2:                         # decoupled weight decay, weights only (not biases / batch-norm parameters)
                p -= self.lr * self.wd * p


class SGD(Optimizer):
    def __init__(self, params, lr=0.01, momentum=0.0, nesterov=False, weight_decay=0.0):
        super().__init__(params, lr, weight_decay)
        self.mu, self.nesterov, self.v = momentum, nesterov, [np.zeros_like(p) for p in params]

    def _update(self, i, g):
        self.v[i] = self.mu * self.v[i] + g
        return self.lr * (g + self.mu * self.v[i] if self.nesterov else self.v[i])


class RMSProp(Optimizer):
    def __init__(self, params, lr=1e-3, rho=0.9, eps=1e-8, weight_decay=0.0):
        super().__init__(params, lr, weight_decay)
        self.rho, self.eps, self.s = rho, eps, [np.zeros_like(p) for p in params]

    def _update(self, i, g):
        self.s[i] = self.rho * self.s[i] + (1 - self.rho) * g ** 2
        return self.lr * g / (np.sqrt(self.s[i]) + self.eps)


class Adam(Optimizer):
    def __init__(self, params, lr=1e-3, betas=(0.9, 0.999), eps=1e-8, weight_decay=0.0):
        super().__init__(params, lr, weight_decay)
        self.b1, self.b2, self.eps = betas[0], betas[1], eps
        self.m, self.v = [np.zeros_like(p) for p in params], [np.zeros_like(p) for p in params]

    def _update(self, i, g):
        self.m[i] = self.b1 * self.m[i] + (1 - self.b1) * g
        self.v[i] = self.b2 * self.v[i] + (1 - self.b2) * g ** 2
        return self.lr * (self.m[i] / (1 - self.b1 ** self.t)) / (np.sqrt(self.v[i] / (1 - self.b2 ** self.t)) + self.eps)


def cosine_schedule(lr0, epochs, warmup=0):
    def f(epoch):
        if epoch < warmup: return lr0 * (epoch + 1) / warmup
        return 0.5 * lr0 * (1 + math.cos(math.pi * (epoch - warmup) / max(epochs - warmup, 1)))
    return f


# ---------------- training ----------------
def fit(model, loss, opt, X, y, epochs=20, batch_size=32, seed=0, X_val=None, y_val=None, patience=None, schedule=None, shuffle=True):
    rng = np.random.default_rng(seed)
    history = {"train_loss": [], "val_loss": [], "val_acc": []}
    best, best_state, bad = np.inf, None, 0
    for ep in range(epochs):
        if schedule is not None: opt.lr = schedule(ep)
        order = rng.permutation(len(y)) if shuffle else np.arange(len(y))
        total = 0.0
        for s in range(0, len(y), batch_size):
            idx = order[s:s + batch_size]
            l, d = loss(model.forward(X[idx], train=True), y[idx])
            model.backward(d)
            opt.step(model.grads())
            total += l * len(idx)
        history["train_loss"].append(total / len(y))
        if X_val is not None:
            out = model.forward(X_val, train=False)
            vl, _ = loss(out, y_val)
            history["val_loss"].append(vl)
            if out.ndim == 2 and out.shape[1] > 1: history["val_acc"].append(float(np.mean(out.argmax(1) == y_val)))
            if patience is not None:
                if vl < best - 1e-9: best, best_state, bad = vl, [s.copy() for s in model.state()], 0
                else:
                    bad += 1
                    if bad >= patience: break
    if best_state is not None:
        for s, b in zip(model.state(), best_state): s[...] = b
    return history


# ---------------- tools ----------------
def grad_check(model, loss, X, y, eps=1e-6, train=True):
    """Largest relative error between backpropagated and central-difference gradients over all parameters."""
    out = model.forward(X, train); _, d = loss(out, y); model.backward(d)
    worst = 0.0
    for p, g in zip(model.params(), [g.copy() for g in model.grads()]):
        num = np.zeros_like(p)
        for idx in np.ndindex(*p.shape):
            old = p[idx]
            p[idx] = old + eps; fp = loss(model.forward(X, train), y)[0]
            p[idx] = old - eps; fm = loss(model.forward(X, train), y)[0]
            p[idx] = old; num[idx] = (fp - fm) / (2 * eps)
        worst = max(worst, float(np.max(np.abs(g - num) / np.maximum(np.abs(g) + np.abs(num), 1e-12))))
    return worst


def save(model, path):
    np.savez(path, *model.state())


def load(model, path):
    data = np.load(path)
    for i, s in enumerate(model.state()): s[...] = data[f"arr_{i}"]
''', encoding="utf-8")
print("nnlib.py:", len((proj / "nnlib.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
nnlib.py: 271 lines
```

### 13.3 The tests

```python run
(proj / "test_nnlib.py").write_text('''import numpy as np, pytest
import nnlib as nn

rng = np.random.default_rng(0)
X = rng.normal(size=(12, 6)); y3 = rng.integers(0, 3, 12); y2 = rng.integers(0, 2, 12); yr = rng.normal(size=(12, 1))

def net(act, extra=()):
    return nn.Sequential(nn.Linear(6, 8, rng=np.random.default_rng(1)), *extra, act, nn.Linear(8, 3, rng=np.random.default_rng(2)))

@pytest.mark.parametrize("act", [nn.Tanh(), nn.Sigmoid(), nn.LeakyReLU(0.1), nn.ReLU()])
def test_every_activation_passes_the_gradient_check(act):
    assert nn.grad_check(net(act), nn.SoftmaxCrossEntropy(), X, y3) < 1e-4, "backward of the layer disagrees with finite differences"

def test_batchnorm_passes_the_gradient_check():
    m = net(nn.Tanh(), extra=(nn.BatchNorm1d(8),))
    assert nn.grad_check(m, nn.SoftmaxCrossEntropy(), X, y3) < 1e-4

def test_dropout_passes_the_gradient_check_with_a_frozen_mask():
    d = nn.Dropout(0.3, seed=3); d.frozen = True
    m = net(nn.Tanh(), extra=(d,)); m.forward(X, True)
    assert nn.grad_check(m, nn.SoftmaxCrossEntropy(), X, y3) < 1e-4

def test_every_loss_passes_the_gradient_check():
    assert nn.grad_check(nn.Sequential(nn.Linear(6, 1, rng=np.random.default_rng(1))), nn.BCEWithLogits(), X, y2) < 1e-4
    assert nn.grad_check(nn.Sequential(nn.Linear(6, 1, rng=np.random.default_rng(1))), nn.MSE(), X, yr) < 1e-4

def test_gradient_shapes_equal_parameter_shapes():
    m = net(nn.ReLU(), extra=(nn.BatchNorm1d(8),)); nn.SoftmaxCrossEntropy()
    out = m.forward(X); m.backward(nn.SoftmaxCrossEntropy()(out, y3)[1])
    assert all(p.shape == g.shape for p, g in zip(m.params(), m.grads()))

def test_the_initial_loss_is_ln_of_the_number_of_classes():
    m = nn.Sequential(nn.Linear(6, 5, init="small", rng=np.random.default_rng(1)), nn.Tanh(), nn.Linear(5, 4, init="small", rng=np.random.default_rng(2)))
    loss, _ = nn.SoftmaxCrossEntropy()(m.forward(X), rng.integers(0, 4, 12))
    assert loss == pytest.approx(np.log(4), abs=0.05), "a freshly initialised classifier should start near ln(C)"

def test_dropout_is_active_in_training_and_inactive_in_evaluation():
    d = nn.Dropout(0.5, seed=1); x = np.ones((20000, 1)) * 3
    out = d.forward(x, True)
    assert abs((out == 0).mean() - 0.5) < 0.02 and out.mean() == pytest.approx(3.0, rel=0.03), "inverted dropout must keep the expected activation"
    assert np.array_equal(d.forward(x, False), x), "evaluation mode must not drop anything"

def test_batchnorm_uses_batch_statistics_in_training_and_running_statistics_in_evaluation():
    bn = nn.BatchNorm1d(6); Xb = rng.normal(5, 3, (64, 6))
    out = bn.forward(Xb, True)
    assert np.allclose(out.mean(0), 0, atol=1e-8) and np.allclose(out.std(0), 1, atol=1e-3)
    for _ in range(200): bn.forward(Xb, True)
    assert np.allclose(bn.running_mean, Xb.mean(0), atol=1e-3), "the running mean must converge to the batch mean"
    assert np.allclose(bn.running_var, Xb.var(0) * 64 / 63, rtol=1e-3), "the running variance uses the UNBIASED estimate, like PyTorch"
    assert np.allclose(bn.forward(Xb, False), out, atol=0.05), "evaluation with running statistics must be close to training-mode output (they differ only by the n/(n-1) factor)"

def test_a_network_can_overfit_one_small_batch():
    m = nn.Sequential(nn.Linear(6, 32, rng=np.random.default_rng(1)), nn.ReLU(), nn.Linear(32, 3, rng=np.random.default_rng(2)))
    h = nn.fit(m, nn.SoftmaxCrossEntropy(), nn.Adam(m.params(), lr=1e-2), X, y3, epochs=300, batch_size=12)
    assert h["train_loss"][-1] < 0.01, "if one batch cannot be memorised there is a bug in forward, backward or the update"

def test_the_same_seed_gives_identical_results():
    def run():
        m = nn.Sequential(nn.Linear(6, 16, rng=np.random.default_rng(1)), nn.ReLU(), nn.Dropout(0.2, seed=5), nn.Linear(16, 3, rng=np.random.default_rng(2)))
        nn.fit(m, nn.SoftmaxCrossEntropy(), nn.Adam(m.params(), lr=1e-2), X, y3, epochs=5, batch_size=4, seed=7)
        return m.params()
    assert all(np.array_equal(a, b) for a, b in zip(run(), run()))

def test_save_and_load_round_trip(tmp_path):
    def build(): return nn.Sequential(nn.Linear(6, 8, rng=np.random.default_rng(1)), nn.BatchNorm1d(8), nn.ReLU(), nn.Linear(8, 3, rng=np.random.default_rng(2)))
    a = build(); nn.fit(a, nn.SoftmaxCrossEntropy(), nn.Adam(a.params(), lr=1e-2), X, y3, epochs=10, batch_size=4)
    nn.save(a, tmp_path / "m.npz"); b = build(); nn.load(b, tmp_path / "m.npz")
    assert np.array_equal(a.predict(X), b.predict(X)) and np.allclose(a.forward(X, False), b.forward(X, False)), "batch-norm running statistics must be saved too"

def test_weight_decay_shrinks_weights_but_not_biases():
    w, b = np.ones((3, 3)), np.ones(3)
    nn.SGD([w, b], lr=0.1, weight_decay=0.5).step([np.zeros((3, 3)), np.zeros(3)])
    assert np.allclose(w, 0.95) and np.allclose(b, 1.0)

# ---------- referee: PyTorch ----------
torch = pytest.importorskip("torch")

def test_layers_and_loss_agree_with_pytorch():
    m = net(nn.ReLU()); out = m.forward(X); loss, d = nn.SoftmaxCrossEntropy()(out, y3); m.backward(d)
    tp = [torch.tensor(p.copy(), dtype=torch.float64, requires_grad=True) for p in m.params()]
    t = torch.relu(torch.tensor(X) @ tp[0] + tp[1]) @ tp[2] + tp[3]
    tl = torch.nn.functional.cross_entropy(t, torch.tensor(y3)); tl.backward()
    assert loss == pytest.approx(tl.item()) and all(np.allclose(g, p.grad.numpy(), atol=1e-12) for g, p in zip(m.grads(), tp))

def test_batchnorm_agrees_with_pytorch_in_training_and_evaluation():
    bn = nn.BatchNorm1d(6); tb = torch.nn.BatchNorm1d(6, momentum=0.1, eps=1e-5).double()
    Xb = rng.normal(2, 3, (16, 6)); up = rng.normal(size=(16, 6))
    out = bn.forward(Xb, True); tx = torch.tensor(Xb, requires_grad=True); to = tb(tx); (to * torch.tensor(up)).sum().backward()
    dx = bn.backward(up)
    assert np.allclose(out, to.detach().numpy()) and np.allclose(dx, tx.grad.numpy(), atol=1e-10)
    tb.eval(); assert np.allclose(bn.forward(Xb[:4], False), tb(torch.tensor(Xb[:4])).detach().numpy())

@pytest.mark.parametrize("name", ["sgd", "momentum", "nesterov", "adam", "rmsprop"])
def test_optimisers_agree_with_pytorch_for_twenty_steps(name):
    r = np.random.default_rng(1); p = [r.normal(size=(3, 2))]; tp = [torch.tensor(p[0].copy(), requires_grad=True)]
    ours, theirs = {"sgd": (nn.SGD(p, lr=0.1), torch.optim.SGD(tp, lr=0.1)),
                    "momentum": (nn.SGD(p, lr=0.1, momentum=0.9), torch.optim.SGD(tp, lr=0.1, momentum=0.9)),
                    "nesterov": (nn.SGD(p, lr=0.1, momentum=0.9, nesterov=True), torch.optim.SGD(tp, lr=0.1, momentum=0.9, nesterov=True)),
                    "adam": (nn.Adam(p, lr=0.01), torch.optim.Adam(tp, lr=0.01)),
                    "rmsprop": (nn.RMSProp(p, lr=0.01, rho=0.9), torch.optim.RMSprop(tp, lr=0.01, alpha=0.9))}[name]
    for _ in range(20):
        g = r.normal(size=(3, 2)); ours.step([g.copy()]); tp[0].grad = torch.tensor(g); theirs.step()
    assert np.allclose(p[0], tp[0].detach().numpy(), atol=1e-10), f"{name} disagrees with torch.optim"
''', encoding="utf-8")
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "test_nnlib.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-900:] or res.stderr.strip()[-900:])
```
```text
......................                                                   [100%]
22 passed in 2.81s
```

### 13.4 Training with the library

```python run
sys.path.insert(0, str(proj))
import importlib, nnlib as nn
importlib.reload(nn)

def build(sizes=(64, 128, 64, 10), dropout=0.0, batchnorm=False, seed=0, act=nn.ReLU):
    rng = np.random.default_rng(seed); layers = []
    for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
        layers.append(nn.Linear(a, b, rng=rng))
        if i < len(sizes) - 2:
            if batchnorm: layers.append(nn.BatchNorm1d(b))
            layers.append(act())
            if dropout: layers.append(nn.Dropout(dropout, seed=seed + 10 + i))
    return nn.Sequential(*layers)

model = build()
print("gradient check of the full network, worst relative error: %.1e" % nn.grad_check(model, nn.SoftmaxCrossEntropy(), X_tr[:16], y_tr[:16]))
t0 = time.perf_counter()
hist = nn.fit(model, nn.SoftmaxCrossEntropy(), nn.Adam(model.params(), lr=3e-3, weight_decay=1e-2), X_tr, y_tr, epochs=40, batch_size=32, seed=0,
              X_val=X_val, y_val=y_val, patience=8, schedule=nn.cosine_schedule(3e-3, 40, warmup=3))
print(f"{len(hist['train_loss'])} epochs in {time.perf_counter() - t0:.1f} s | validation accuracy {hist['val_acc'][-1]:.4f} | TEST accuracy {np.mean(model.predict(X_te) == y_te):.4f}")
from sklearn.neural_network import MLPClassifier
print(f"scikit-learn MLPClassifier test accuracy {MLPClassifier((128, 64), max_iter=300, random_state=0).fit(X_tr, y_tr).score(X_te, y_te):.4f} | logistic regression {linear_model.LogisticRegression(max_iter=3000).fit(X_tr, y_tr).score(X_te, y_te):.4f}")
```
```text
gradient check of the full network, worst relative error: 1.1e-04
17 epochs in 0.9 s | validation accuracy 0.9638 | TEST accuracy 0.9667
scikit-learn MLPClassifier test accuracy 0.9694 | logistic regression 0.9639
```

Two honest remarks about this output. The full-network gradient check reports about 1e-4, at the edge of the usual pass level, because a 128-unit ReLU network has many kinks, and a finite-difference step that straddles one gives a small mismatch; the per-layer checks in the tests (with smooth activations, and ReLU on a small net) are far tighter. And the library reaches the same accuracy as scikit-learn's `MLPClassifier` and as logistic regression, within the noise of 360 test images: on a small clean problem, depth is not the point.

### 13.5 Exact parity with PyTorch on a whole training run

Individual layers agreeing is one thing; a whole **training run** agreeing is the strongest test. We copy the initial weights into an equivalent `torch.nn.Sequential`, feed both exactly the same mini-batches without shuffling, and compare the weights after one epoch.

```python run
if HAS_TORCH:
    ours = build((64, 32, 10), seed=1)
    tm = torch.nn.Sequential(torch.nn.Linear(64, 32), torch.nn.ReLU(), torch.nn.Linear(32, 10)).double()
    with torch.no_grad():
        for l_ours, l_t in [(ours.layers[0], tm[0]), (ours.layers[2], tm[2])]:
            l_t.weight.copy_(torch.tensor(l_ours.W.T)); l_t.bias.copy_(torch.tensor(l_ours.b))
    opt_t = torch.optim.SGD(tm.parameters(), lr=0.05, momentum=0.9)
    opt_o = nn.SGD(ours.params(), lr=0.05, momentum=0.9)
    lossf = nn.SoftmaxCrossEntropy()
    for s in range(0, 320, 32):
        xb, yb = X_tr[s:s + 32], y_tr[s:s + 32]
        l, d = lossf(ours.forward(xb), yb); ours.backward(d); opt_o.step(ours.grads())
        opt_t.zero_grad(); lt = torch.nn.functional.cross_entropy(tm(torch.tensor(xb)), torch.tensor(yb)); lt.backward(); opt_t.step()
    diffs = [float(np.max(np.abs(ours.layers[0].W.T - tm[0].weight.detach().numpy()))), float(np.max(np.abs(ours.layers[2].W.T - tm[2].weight.detach().numpy())))]
    print("10 mini-batch updates, SGD with momentum: max |our weights - torch weights| per layer =", diffs, "| last loss ours %.10f, torch %.10f" % (l, lt.item()))
```
```text
10 mini-batch updates, SGD with momentum: max |our weights - torch weights| per layer = [1.1102230246251565e-16, 1.1102230246251565e-16] | last loss ours 1.0872266232, torch 1.0872266232
```

Agreement to rounding error after ten updates, through the forward pass, the loss, the backward pass and the optimiser, means every part of the library is doing what PyTorch does.

### 13.6 The ablation report: which ingredients help, with an error bar

Does batch norm help? Dropout? Weight decay? One run of each is a single draw from a noisy process (ds.04). We repeat each configuration over five seeds on the small-data setting (150 training images, where regularisation matters) and report the mean and spread of the validation accuracy.

```python run
def run_cfg(seed, dropout=0.0, batchnorm=False, wd=0.0):
    m = build((64, 128, 128, 10), dropout=dropout, batchnorm=batchnorm, seed=seed)
    nn.fit(m, nn.SoftmaxCrossEntropy(), nn.Adam(m.params(), lr=2e-3, weight_decay=wd), Xs_small, ys_small, epochs=60, batch_size=32, seed=seed)
    return float(np.mean(m.predict(X_val) == y_val))
configs = {"plain": {}, "+ weight decay 1e-2": {"wd": 1e-2}, "+ dropout 0.3": {"dropout": 0.3}, "+ batch norm": {"batchnorm": True},
           "+ weight decay + dropout": {"wd": 1e-2, "dropout": 0.3}, "+ all three": {"wd": 1e-2, "dropout": 0.3, "batchnorm": True}}
rows = []
for name, cfg in configs.items():
    accs = [run_cfg(s, **cfg) for s in range(5)]
    rows.append((name, np.mean(accs), np.std(accs, ddof=1), min(accs), max(accs)))
report = pd.DataFrame(rows, columns=["configuration", "mean val accuracy", "std over 5 seeds", "min", "max"]).set_index("configuration")
print(report.round(4).to_string())
print("\ndifference to the plain network is meaningful only if it is larger than about 2 standard errors (std / sqrt(5)):")
base_mean = report.loc["plain", "mean val accuracy"]
print(((report["mean val accuracy"] - base_mean) / (report["std over 5 seeds"] / math.sqrt(5))).round(1).to_string())
```
```text
                          mean val accuracy  std over 5 seeds     min     max
configuration                                                                
plain                               0.87860           0.00610 0.87470 0.88860
+ weight decay 1e-2                 0.87800           0.00670 0.87190 0.88860
+ dropout 0.3                       0.89250           0.00890 0.88300 0.90530
+ batch norm                        0.89580           0.00940 0.88580 0.91090
+ weight decay + dropout            0.89250           0.00890 0.88300 0.90530
+ all three                         0.90080           0.01120 0.88860 0.91360

difference to the plain network is meaningful only if it is larger than about 2 standard errors (std / sqrt(5)):
configuration
plain                       0.00000
+ weight decay 1e-2        -0.20000
+ dropout 0.3               3.50000
+ batch norm                4.10000
+ weight decay + dropout    3.50000
+ all three                 4.40000
```

(Read the last column as a rough guide, not a formal test: five seeds and a shared validation set limit what can be claimed.) What the table says:

- **Dropout 0.3** and **batch norm** each improve the mean validation accuracy by about 1.5 points, well beyond the seed-to-seed spread. All three together give about 2 points. A single run (section 10.4) could not show that.
- **Weight decay 1e-2 did nothing measurable**, and the "weight decay + dropout" row is identical to the dropout row. The reason is arithmetic: decoupled decay shrinks each weight by `lr x wd = 2e-3 x 1e-2 = 2e-5` per step, and 60 epochs of 5 steps is only 300 steps, a total shrinkage of about 0.6%. A regulariser has to be strong enough to matter: tune its strength, and check that turning it on actually changes the weights.
- The spreads (0.006 to 0.011) are as large as some of the differences: report them every time.

### 13.7 What to hand in

1. `nnlib.py` and `test_nnlib.py`, all tests passing (the PyTorch tests may be skipped if PyTorch is not installed, and must pass where it is).
2. The training log of a model on `load_digits`, with test accuracy against logistic regression and `MLPClassifier`.
3. The whole-run parity check of 13.5 for **two** configurations (for example with Adam, and with batch norm in evaluation mode).
4. The ablation table of 13.6, with your reading of it in three sentences.
5. A "what I learned from the bugs" note: every bug your tests caught while you wrote the library, and the test that caught it.

### 13.8 Extensions

1. Add `Conv1d` or an embedding layer with their backward passes, and gradient-check them.
2. Add gradient clipping by global norm to the trainer and a test that it prevents divergence at a high learning rate.
3. Add a `LayerNorm` layer and compare batch norm and layer norm on the ablation.
4. Add learning-rate range testing (`find_lr`) to the library.
5. Port the same network to `torch.nn` (ml.02) and compare line counts, speed and accuracy. What does a framework save you?

## 14. Common traps

| Trap | What happens | Fix |
|---|---|---|
| A stack of linear layers without activations | the network is just one linear model | non-linearity after every hidden layer (1.2) |
| Sigmoid or tanh in deep hidden layers | vanishing gradients | ReLU-family activations; right initialisation (3.2, 9) |
| Unstable softmax or log | `nan` or `inf` losses | cross-entropy from logits, subtract the maximum (3.4, 4.2) |
| Applying softmax and then a loss that applies it again | squashed gradients, poor learning | pass raw logits to the fused loss (4.2) |
| Unverified hand-written backward pass | a network that trains badly for no visible reason | gradient check before any long run (6.3) |
| Wrong shapes or a missing transpose | silent mis-learning | the gradient has the parameter's shape (6.1) |
| Forgetting `1/N` in the loss gradient | the effective learning rate scales with the batch size | gradient check (6.6) |
| Gradient check in float32 or with a bad `eps` | false alarms or false passes | float64, `eps` about 1e-6 (6.3) |
| `grad +=` omitted in an autograd node | wrong gradients for reused values | accumulate (7.2) |
| Not summing over the batch for broadcast parameters | wrong bias gradients | `unbroadcast` (7.4) |
| Zero or constant initialisation | symmetric units that never differentiate | random weights (9.1) |
| Wrong initialisation scale for the activation | vanishing or exploding signals | He for ReLU, Xavier for tanh (9.2) |
| Unscaled inputs | slow or failed training | standardise with training statistics (8.1) |
| Learning rate too high or too low | divergence or crawling | sweep or range test (8.3) |
| Reporting training accuracy | overfitting hidden | validation and test sets (8.4) |
| Dropout left on at prediction time | noisy, worse predictions | `train=False` in evaluation (10.4) |
| Batch norm in evaluation using batch statistics | results that depend on the batch | use running statistics (11.2) |
| Batch norm with tiny batches | noisy statistics | larger batches, or layer norm (11.4) |
| Weight decay applied to biases and norm parameters | slower learning for no benefit | decay weights only (10.2) |
| L2 inside Adam when decoupled decay was meant | decay depends on gradient size | AdamW (10.2) |
| Trusting one run | seed luck mistaken for an effect | several seeds, an error bar (13.6) |
| Training a big model before a one-batch overfit | long wasted runs | the debugging checklist first (12) |

## 15. Summary

- A **neural network** is a stack of simple differentiable layers trained together by gradient descent on one loss. A linear model cannot do XOR; a hidden layer with a non-linearity can, because it re-represents the data. Without a non-linearity, depth adds nothing (two linear layers equal one).
- A **neuron** computes `φ(w·x + b)`; a **layer** on a batch is `φ(XW + b)` with batch-first shapes. Count parameters from the layer sizes.
- **Activations**: sigmoid and tanh saturate (derivatives at most 0.25 and 1) and cause vanishing gradients through depth (a product of 20 sigmoid derivatives was about 1e-16); **ReLU** and relatives do not saturate for positive inputs but can die. Softmax needs the max-subtraction trick. Check every derivative against an independent implementation.
- **Losses**: MSE and Huber for regression; **cross-entropy from logits** for classification, computed stably, with the gradient `p − y` with respect to the logits. A fresh classifier should start at `ln C`.
- **Optimisers**: SGD, momentum, Nesterov, RMSProp, **Adam** (with bias correction) and **AdamW**; our versions equal `torch.optim` to rounding error. Learning-rate **schedules** (step, cosine, warm-up) and mini-batch size shape the path. On an ill-conditioned valley, plain SGD crawls or diverges while momentum and adaptive methods converge.
- **Backpropagation** is the chain rule from the output backwards, reusing forward values: `dZ = dA ⊙ φ'(Z)`, `dW = Aᵀ dZ`, `db = Σ dZ`, `dA_prev = dZ Wᵀ`. **Gradient checking** with central differences in float64 is the test that makes a hand-written backward trustworthy: it caught a missing activation derivative and a missing `1/N` immediately. Backpropagation is about 500 times faster than numerical gradients for 2,778 parameters, at the price of storing activations.
- A **tiny autograd engine** (scalar `Value`, then NumPy `Tensor` with un-broadcasting) automates backpropagation and matches PyTorch to 1e-16. The key details: accumulate gradients, process nodes in reverse topological order, and sum over broadcast dimensions.
- **Initialisation**: zero or constant weights keep units identical; the scale of the weights must keep the variance of signals and gradients constant across layers: **Xavier** for tanh, **He** for ReLU. We measured activations and gradients through 12 to 20 layers.
- **Regularisation**: **weight decay** (AdamW decouples it from the gradient scale), **early stopping**, **dropout** (inverted scaling; off in evaluation), **data augmentation**, a smaller model, and more data. All were tested against an overfitting baseline.
- **Batch normalisation** standardises features per batch, then rescales with learned `γ`, `β`; uses running statistics at evaluation; its backward pass couples all examples in the batch. It made a badly initialised 9-layer network trainable at large learning rates. **Layer norm** removes the dependence on the batch.
- **Debugging**: initial loss `= ln C`; overfit one batch; gradient check; gradient norms by layer; update-to-weight ratio; dead units; data checks. A network trained on shuffled labels memorises one batch but learns nothing, so always compare with a baseline.
- The **project**, `nnlib`, is a layered library with losses, optimisers, a trainer, gradient check and save/load, with a test suite that includes whole-run parity with PyTorch, and an ablation report with error bars.

You reached the outcome of this chapter: you can **implement backpropagation for a small network by hand**, prove it correct with a numerical gradient check and an independent framework, and build a working network library around it. Next, ml.02 moves to PyTorch: tensors, `autograd`, `nn.Module`, `Dataset` and `DataLoader`, GPU use, and training loops, where the machinery you built here becomes a tool you trust rather than a mystery.
