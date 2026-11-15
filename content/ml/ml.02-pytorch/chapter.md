# Chapter 2 (ML): PyTorch

In ml.01 you built a neural-network library from scratch: layers with `forward` and `backward`, losses, optimisers, a trainer, and an autograd engine. That was to understand it. In practice nobody writes this by hand, because **PyTorch** gives you the same ideas, tested by millions of users, fast on CPUs and GPUs, with hundreds of ready-made layers. This chapter teaches you to use it fluently, and to do so with the mind of someone who knows what is underneath.

You will learn **tensors** (PyTorch's arrays, and the shape, dtype and memory rules that cause most bugs), **autograd** (the engine you built, now the real one), **`nn.Module`** (layers, parameters, `state_dict`), **`Dataset` and `DataLoader`** (feeding data), **optimisers and schedulers**, the **training loop**, **saving and loading**, **devices and reproducibility**, and **convolutional layers** for images. The syllabus outcome ties it together: **write a training loop from memory and diagnose a model that does not learn.** The chapter ends with a project: an **image classifier trained end to end** and tested, with a gallery of ten classic training bugs that you will learn to recognise.

Prerequisites: ml.01 (backpropagation, initialisation, regularisation, batch norm, the debugging checklist), ds.05 and ds.06 (data splits, pipelines). Every claim about PyTorch is checked by running it.

> **Offline rule for this chapter.** Everything runs with no internet, on the **CPU build** of PyTorch (2.15) installed in this course's environment, using the 8x8 digit images bundled with scikit-learn as the image dataset. There is no GPU here, so GPU-specific code (`cuda`, mixed precision) is written in the device-agnostic style, runs on the CPU, and the GPU-only parts are shown as *Try it on your machine* with no invented output. `torchvision` is not installed and not needed: convolutional layers are part of core PyTorch. Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, json, os, platform, tempfile, pathlib, warnings
import numpy as np
import pandas as pd
import sklearn
from sklearn import datasets, model_selection, linear_model
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, TensorDataset, random_split, WeightedRandomSampler

warnings.filterwarnings("ignore")
np.set_printoptions(precision=5, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.float_format", lambda v: f"{v:,.5f}")
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__)
print("torch  ", torch.__version__, "| CUDA available:", torch.cuda.is_available(), "| CPU threads:", torch.get_num_threads())
```
```text
python  3.14.4
numpy   2.5.4
torch   2.15.0+cpu | CUDA available: False | CPU threads: 6
```

## Table of contents

1. [Tensors](#1-tensors)
2. [Autograd](#2-autograd)
3. [nn.Module: layers, parameters and state](#3-nnmodule-layers-parameters-and-state)
4. [Data: Dataset and DataLoader](#4-data-dataset-and-dataloader)
5. [Optimisers, schedulers and gradient clipping](#5-optimisers-schedulers-and-gradient-clipping)
6. [The training loop](#6-the-training-loop)
7. [Saving, loading and resuming](#7-saving-loading-and-resuming)
8. [Devices, speed and reproducibility](#8-devices-speed-and-reproducibility)
9. [Convolutional networks for images](#9-convolutional-networks-for-images)
10. [Debugging training problems: ten classic bugs](#10-debugging-training-problems-ten-classic-bugs)
11. [Project: an image classifier trained end to end](#11-project-an-image-classifier-trained-end-to-end)
12. [Common traps](#12-common-traps)
13. [Summary](#13-summary)

## 1. Tensors

### 1.1 What a tensor is

A **tensor** is an n-dimensional array, like a NumPy array, with three extra abilities: it can live on a GPU, it can track operations for automatic differentiation (section 2), and it plugs into `torch.nn`. Three properties describe it, and almost every PyTorch error is about one of them: its **shape**, its **dtype** (the number type) and its **device** (CPU or GPU).

```python run
a = torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
print("shape", a.shape, "| dtype", a.dtype, "| device", a.device, "| ndim", a.ndim, "| numel", a.numel())
print("a Python list of ints gives:", torch.tensor([1, 2, 3]).dtype, "| of floats:", torch.tensor([1.0, 2.0]).dtype, "| default float is float32 (NumPy's is float64)")
for name, t in [("zeros", torch.zeros(2, 3)), ("ones", torch.ones(2, 3)), ("arange", torch.arange(0, 6).reshape(2, 3)), ("linspace", torch.linspace(0, 1, 5)),
                ("eye", torch.eye(3)), ("randn", torch.randn(2, 2)), ("full", torch.full((2, 2), 7.0))]:
    print(f"{name:9s}", tuple(t.shape), t.dtype)
```
```text
shape torch.Size([2, 3]) | dtype torch.float32 | device cpu | ndim 2 | numel 6
a Python list of ints gives: torch.int64 | of floats: torch.float32 | default float is float32 (NumPy's is float64)
zeros     (2, 3) torch.float32
ones      (2, 3) torch.float32
arange    (2, 3) torch.int64
linspace  (5,) torch.float32
eye       (3, 3) torch.float32
randn     (2, 2) torch.float32
full      (2, 2) torch.float32
```

### 1.2 dtype: the quiet source of bugs

Labels for classification must be **integers of type `long` (int64)**; inputs and weights must be **floats**. Mixing types either raises an error or, worse, silently changes the meaning.

```python run
print("int / int in torch  :", torch.tensor([7]) / torch.tensor([2]), "(true division gives a float, as in Python 3)")
print("int // int          :", torch.tensor([7]) // torch.tensor([2]))
x = torch.tensor([1.5, 2.5, 3.5])
print("float32 -> int64    :", x.long(), "(truncates toward zero)")
print("float32 sum of 0.1 ten times:", torch.full((10,), 0.1).sum().item(), "| float64:", torch.full((10,), 0.1, dtype=torch.float64).sum().item())
try:
    torch.randn(2, 3) @ torch.randn(2, 3).double().t()
except RuntimeError as e:
    print("float32 @ float64   : RuntimeError:", str(e)[:70])
```
```text
int / int in torch  : tensor([3.5000]) (true division gives a float, as in Python 3)
int // int          : tensor([3])
float32 -> int64    : tensor([1, 2, 3]) (truncates toward zero)
float32 sum of 0.1 ten times: 1.0000001192092896 | float64: 1.0
float32 @ float64   : RuntimeError: expected m1 and m2 to have the same dtype, but got: float != double
```

### 1.3 Shapes, views and copies

Many operations return a **view**: a new tensor object that shares the same memory. Changing one changes the other. That is fast and a classic source of surprises. `reshape`/`view` need compatible memory layout; `transpose` changes strides without moving data; `clone()` makes a true copy.

```python run
t = torch.arange(6).reshape(2, 3)
v = t.view(3, 2); v[0, 0] = 100
print("a view shares memory with its parent: t[0,0] =", t[0, 0].item(), "(changed through the view)")
c = t.clone(); c[0, 0] = -1
print("a clone does not: t[0,0] =", t[0, 0].item())
tt = t.t()
print("transpose is a view with different strides:", tt.stride(), "| contiguous:", tt.is_contiguous())
try:
    tt.view(6)
except RuntimeError as e:
    print("view on a non-contiguous tensor fails:", str(e)[:58], "...")
print("reshape copies when it must:", tt.reshape(6).tolist(), "| or .contiguous().view(6):", tt.contiguous().view(6).tolist())
```
```text
a view shares memory with its parent: t[0,0] = 100 (changed through the view)
a clone does not: t[0,0] = 100
transpose is a view with different strides: (1, 3) | contiguous: False
view on a non-contiguous tensor fails: view size is not compatible with input tensor's size and s ...
reshape copies when it must: [100, 3, 1, 4, 2, 5] | or .contiguous().view(6): [100, 3, 1, 4, 2, 5]
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a diagram of PyTorch memory sharing. Start with t = torch.arange(6).reshape(2, 3): one row of 6 memory cells holding 0..5, with t as a 2x3 grid pointing to it, strides (3, 1). Show v = t.view(3, 2) pointing to the SAME cells, so v[0,0] = 100 changes t[0,0]. Show t.t() with strides (1, 3) reading the same cells in a different order, and clone() as a separate copy of the cells. Use colours for shared versus copied memory."

### 1.4 Indexing, broadcasting and reductions

These follow NumPy's rules (ds.06 and da.02), with the same broadcasting: shapes are compared from the right, and a dimension of size 1 is stretched.

```python run
X = torch.arange(12.0).reshape(3, 4)
print("row 1:", X[1].tolist(), "| column 2:", X[:, 2].tolist(), "| X[X > 6]:", X[X > 6].tolist())
col = torch.tensor([[1.0], [2.0], [3.0]]); row = torch.tensor([[10.0, 20.0, 30.0, 40.0]])
print("(3,1) + (1,4) broadcasts to", (col + row).shape)
print("mean over rows (dim=0):", X.mean(0).tolist(), "| over columns, keepdim:", X.sum(1, keepdim=True).shape, "| argmax per row:", X.argmax(1).tolist())
print("matmul: (3,4) @ (4,2) ->", (X @ torch.ones(4, 2)).shape, "| einsum equivalent equal:", bool(torch.allclose(X @ torch.ones(4, 2), torch.einsum('ij,jk->ik', X, torch.ones(4, 2)))))
```
```text
row 1: [4.0, 5.0, 6.0, 7.0] | column 2: [2.0, 6.0, 10.0] | X[X > 6]: [7.0, 8.0, 9.0, 10.0, 11.0]
(3,1) + (1,4) broadcasts to torch.Size([3, 4])
mean over rows (dim=0): [4.0, 5.0, 6.0, 7.0] | over columns, keepdim: torch.Size([3, 1]) | argmax per row: [3, 3, 3]
matmul: (3,4) @ (4,2) -> torch.Size([3, 2]) | einsum equivalent equal: True
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a broadcasting diagram in PyTorch. Show col with shape (3,1) holding [1,2,3] and row with shape (1,4) holding [10,20,30,40]. Show col stretched across 4 columns and row stretched down 3 rows, then the result grid of shape (3,4) where each cell is col[i] + row[j]. Label the shapes compared from the right, and mark the stretched copies in a lighter colour."

### 1.5 NumPy interoperability, and a trap

`torch.from_numpy` and `.numpy()` **share memory** with no copy (on the CPU). `torch.tensor(array)` copies.

```python run
n = np.arange(5.0)
shared, copied = torch.from_numpy(n), torch.tensor(n)
n[0] = 99.0
print("after changing the NumPy array: from_numpy sees", shared[0].item(), "| torch.tensor (a copy) sees", copied[0].item())
print("NumPy float64 -> torch keeps float64:", torch.from_numpy(n).dtype, "| convert to float32 for a network with .float()")
```
```text
after changing the NumPy array: from_numpy sees 99.0 | torch.tensor (a copy) sees 0.0
NumPy float64 -> torch keeps float64: torch.float64 | convert to float32 for a network with .float()
```

### 1.6 In-place operations

Methods ending in `_` (`add_`, `zero_`, `clamp_`) change a tensor in place. They save memory but can break autograd (section 2) because the original value may be needed for the backward pass.

```python run
w = torch.ones(3); w.mul_(2).add_(1)
print("in place: ones * 2 + 1 =", w.tolist())
```
```text
in place: ones * 2 + 1 = [3.0, 3.0, 3.0]
```

### 1.7 Speed: a tensor operation is a NumPy-speed operation

```python run
A = np.random.default_rng(0).normal(size=(1500, 1500)).astype(np.float32); TA = torch.from_numpy(A)
for name, f in [("NumPy", lambda: A @ A), ("PyTorch", lambda: TA @ TA)]:
    f(); t0 = time.perf_counter()
    for _ in range(5): f()
    print(f"{name:8s} 1500x1500 float32 matmul: {(time.perf_counter() - t0) / 5 * 1000:.1f} ms")
```
```text
NumPy    1500x1500 float32 matmul: 51.3 ms
PyTorch  1500x1500 float32 matmul: 55.6 ms
```

On the CPU the two are comparable (both call optimised BLAS routines). The point of PyTorch is not faster NumPy; it is gradients, GPUs and the `nn` toolbox.

### 1.8 Try it

1. Create a `(2, 3, 4)` tensor and use `permute` to make it `(4, 2, 3)`. Is the result contiguous? What does `.contiguous()` do?
2. Predict then check: `torch.tensor([1, 2, 3]) * 1.5` has which dtype?

## 2. Autograd

### 2.1 The engine you built in ml.01

When a tensor has `requires_grad=True`, PyTorch records every operation applied to it as a node in a graph. Calling `.backward()` on a scalar walks the graph in reverse and fills the `.grad` attribute of every **leaf** tensor (a tensor you created yourself) with the gradient of that scalar. That is exactly the `Tensor` class of ml.01 section 7, with a great deal more engineering.

```python run
x = torch.tensor([2.0, 3.0], requires_grad=True)
y = (x ** 2).sum()                                   # y = x0^2 + x1^2
print("y =", y.item(), "| y.grad_fn:", y.grad_fn.name(), "| x is a leaf:", x.is_leaf, "| y is a leaf:", y.is_leaf)
y.backward()
print("dy/dx =", x.grad.tolist(), "(= 2x)")
```
```text
y = 13.0 | y.grad_fn: SumBackward0 | x is a leaf: True | y is a leaf: False
dy/dx = [4.0, 6.0] (= 2x)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the autograd graph for x = [2.0, 3.0] with requires_grad=True, then x ** 2, then .sum() giving y = 13.0. Label x as a leaf, the PowBackward and SumBackward0 nodes, and show the backward arrows ending with x.grad = [4, 6] (which is 2x). Add a small second picture where .grad is a box that grows when backward is called again."

### 2.2 Gradients accumulate

Each `.backward()` **adds** to `.grad`. That is useful (accumulating over several mini-batches) and the origin of the commonest training bug: forgetting to zero the gradients between steps (bug 1 of section 10).

> **Predict the output.** `x = [2, 3]` and `y = (x**2).sum()`, so one `backward()` gives `x.grad = [4, 6]`. If we call `(x**2).sum().backward()` three times in a row without clearing, what is `x.grad` after the third call?

<details><summary>Answer</summary>

`[12, 18]`: each call **adds** its gradient to the existing one (4, 8, 12 for the first entry). This accumulation is deliberate, and forgetting to clear it every step is the commonest training bug.

</details>

```python run
x = torch.tensor([2.0, 3.0], requires_grad=True)
for k in range(3):
    (x ** 2).sum().backward()
    print(f"after backward #{k + 1}: x.grad = {x.grad.tolist()}")
x.grad.zero_(); (x ** 2).sum().backward(); print("after zero_ and one backward:", x.grad.tolist())
```
```text
after backward #1: x.grad = [4.0, 6.0]
after backward #2: x.grad = [8.0, 12.0]
after backward #3: x.grad = [12.0, 18.0]
after zero_ and one backward: [4.0, 6.0]
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Make a step-by-step animation or table of x.grad for x = [2.0, 3.0] and y = (x**2).sum(). Each backward() call adds [4, 6] into the .grad box, so the box shows [4,6], then [8,12], then [12,18]. Then show x.grad.zero_() followed by one backward giving [4,6] again. Label each step and highlight the value that is added each time."

### 2.3 Non-scalar outputs, detach and no_grad

`backward()` needs a scalar. For a vector output you pass the upstream gradient (here ones, which sums the outputs). To stop gradients from flowing, use `.detach()` (a tensor cut out of the graph) or the `torch.no_grad()` context (no graph is recorded at all, which saves memory during evaluation).

```python run
x = torch.tensor([1.0, 2.0, 3.0], requires_grad=True)
y = x ** 2
y.backward(torch.ones_like(y)); print("vector output with upstream gradient of ones:", x.grad.tolist())
z = (x.detach() ** 2); print("detached result tracks gradients:", z.requires_grad)
with torch.no_grad():
    w = x * 2
print("inside no_grad:", w.requires_grad, "| grad_fn:", w.grad_fn)
```
```text
vector output with upstream gradient of ones: [2.0, 4.0, 6.0]
detached result tracks gradients: False
inside no_grad: False | grad_fn: None
```

### 2.4 The referee of ml.01, now the real thing

The 2-2-1 network of ml.01 section 6.2, in double precision. PyTorch's `backward()` reproduces the gradients we derived by hand.

```python run
x = torch.tensor([[1.0, -2.0]], dtype=torch.float64)
W1 = torch.tensor([[0.5, -1.0], [0.25, 0.75]], dtype=torch.float64, requires_grad=True); b1 = torch.tensor([0.1, -0.2], dtype=torch.float64, requires_grad=True)
W2 = torch.tensor([[1.5], [-0.5]], dtype=torch.float64, requires_grad=True); b2 = torch.tensor([0.3], dtype=torch.float64, requires_grad=True)
loss = 0.5 * ((torch.tanh(x @ W1 + b1) @ W2 + b2 - 1.0) ** 2).mean()
loss.backward()
print("loss", round(loss.item(), 6), "| dW2", W2.grad.flatten().tolist(), "| dW1", W1.grad.flatten().tolist())
print("by hand in ml.01: dW2 [-0.005481, 0.0545], dW1 [-0.081672, 0.000492, 0.163344, -0.000985]  (they agree)")
```
```text
loss 0.001512 | dW2 [-0.00548116972538784, 0.05449974260216634] | dW1 [-0.08167197604316839, 0.000492315040610833, 0.16334395208633679, -0.000984630081221666]
by hand in ml.01: dW2 [-0.005481, 0.0545], dW1 [-0.081672, 0.000492, 0.163344, -0.000985]  (they agree)
```

### 2.5 Derivatives of derivatives, and gradient checking

`torch.autograd.grad(..., create_graph=True)` keeps the graph of the gradient itself, so you can differentiate again. And `torch.autograd.gradcheck` automates the finite-difference test of ml.01 section 6.3 for any function (it needs double precision).

```python run
x = torch.tensor(2.0, requires_grad=True)
f = x ** 3
g, = torch.autograd.grad(f, x, create_graph=True)                  # 3x^2
h, = torch.autograd.grad(g, x)                                      # 6x
print("f = x^3 at x=2: f' =", g.item(), "(3x^2 = 12) | f'' =", h.item(), "(6x = 12)")

class Square(torch.autograd.Function):                              # a custom operation with a hand-written backward
    @staticmethod
    def forward(ctx, x):
        ctx.save_for_backward(x); return x ** 2
    @staticmethod
    def backward(ctx, grad_out):
        x, = ctx.saved_tensors; return 2 * x * grad_out
xi = torch.randn(5, dtype=torch.float64, requires_grad=True)
print("gradcheck of the custom Square function:", torch.autograd.gradcheck(Square.apply, (xi,)))
class BadSquare(Square):
    @staticmethod
    def backward(ctx, grad_out):
        x, = ctx.saved_tensors; return 3 * x * grad_out               # a deliberate bug
try:
    torch.autograd.gradcheck(BadSquare.apply, (xi,))
except RuntimeError as e:
    print("gradcheck catches the wrong backward:", str(e).splitlines()[0][:80])
```
```text
f = x^3 at x=2: f' = 12.0 (3x^2 = 12) | f'' = 12.0 (6x = 12)
gradcheck of the custom Square function: True
gradcheck catches the wrong backward: Jacobian mismatch for output 0 with respect to input 0,
```

### 2.6 What autograd cannot do for you

An in-place change to a tensor that autograd saved for the backward pass is caught at `backward()` time:

```python run
a = torch.tensor([1.0, 2.0], requires_grad=True)
b = torch.exp(a)                                     # exp saves its OUTPUT for the backward pass
b.add_(1.0)                                          # ... and we overwrite it
try:
    b.sum().backward()
except RuntimeError as e:
    print("RuntimeError:", str(e)[:95], "...")
```
```text
RuntimeError: one of the variables needed for gradient computation has been modified by an inplace operation: ...
```

### 2.7 Try it

1. Compute the gradient of `sigmoid(w·x + b)` for one example with autograd and with the formula `σ(1−σ)x`. Do they agree?
2. Call `backward()` twice on the same graph without `retain_graph=True`. What error do you get, and why?

## 3. nn.Module: layers, parameters and state

### 3.1 A module is a container of parameters and a `forward`

Every layer and every model in PyTorch is a subclass of `nn.Module`. Assigning an `nn.Module` or an `nn.Parameter` as an attribute **registers** it, so that `parameters()`, `state_dict()`, `.to(device)`, `.train()` and `.eval()` all find it automatically. You write `forward`; autograd supplies `backward`.

```python run
class MLP(nn.Module):
    def __init__(self, sizes, dropout=0.0):
        super().__init__()
        layers = []
        for i, (a, b) in enumerate(zip(sizes[:-1], sizes[1:])):
            layers.append(nn.Linear(a, b))
            if i < len(sizes) - 2:
                layers += [nn.ReLU()] + ([nn.Dropout(dropout)] if dropout else [])
        self.net = nn.Sequential(*layers)
    def forward(self, x):
        return self.net(x)

torch.manual_seed(0)
model = MLP([64, 32, 16, 10])
print(model)
n_params = sum(p.numel() for p in model.parameters())
print("parameters:", n_params, "| ml.01 counted 2,778 for the same sizes:", n_params == 2778)
print("state_dict keys:", list(model.state_dict().keys()))
```
```text
MLP(
  (net): Sequential(
    (0): Linear(in_features=64, out_features=32, bias=True)
    (1): ReLU()
    (2): Linear(in_features=32, out_features=16, bias=True)
    (3): ReLU()
    (4): Linear(in_features=16, out_features=10, bias=True)
  )
)
parameters: 2778 | ml.01 counted 2,778 for the same sizes: True
state_dict keys: ['net.0.weight', 'net.0.bias', 'net.2.weight', 'net.2.bias', 'net.4.weight', 'net.4.bias']
```

### 3.2 Parameters, buffers, train and eval

- **Parameters** are tensors with `requires_grad=True` that the optimiser updates (weights, biases, batch-norm `γ` and `β`).
- **Buffers** are tensors that belong to the model's state but are **not** trained: batch norm's running mean and variance. They are saved in `state_dict` but not returned by `parameters()`.
- **`model.train()` / `model.eval()`** switch layers like dropout and batch norm between their two behaviours (ml.01 sections 10 and 11). `torch.no_grad()` is separate: it stops graph recording. Evaluation needs both.

```python run
bn_model = nn.Sequential(nn.Linear(4, 6), nn.BatchNorm1d(6), nn.ReLU(), nn.Dropout(0.5))
print("parameters:", [n for n, _ in bn_model.named_parameters()])
print("buffers   :", [n for n, _ in bn_model.named_buffers()])
x = torch.randn(32, 4)
bn_model.train(); a1, a2 = bn_model(x), bn_model(x)
bn_model.eval(); b1, b2 = bn_model(x), bn_model(x)
print("train mode: same input, two calls identical?", bool(torch.equal(a1, a2)), "(dropout is random)")
print("eval  mode: same input, two calls identical?", bool(torch.equal(b1, b2)))
print("module flags: training =", bn_model.training, "| submodule dropout.training =", bn_model[3].training)
```
```text
parameters: ['0.weight', '0.bias', '1.weight', '1.bias']
buffers   : ['1.running_mean', '1.running_var', '1.num_batches_tracked']
train mode: same input, two calls identical? False (dropout is random)
eval  mode: same input, two calls identical? True
module flags: training = False | submodule dropout.training = False
```

### 3.3 Initialisation, checked against ml.01

PyTorch's `nn.Linear` initialises weights uniformly in `[-1/√fan_in, 1/√fan_in]` (a scaled Kaiming scheme), which has standard deviation `1/√(3·fan_in)`. You can override with `torch.nn.init`.

```python run
lin = nn.Linear(256, 100)
print(f"default nn.Linear weight std {lin.weight.std().item():.5f} | formula 1/sqrt(3*fan_in) = {1 / math.sqrt(3 * 256):.5f} | bias is also random (not zero as in ml.01): std {lin.bias.std().item():.4f}")
nn.init.kaiming_normal_(lin.weight, nonlinearity="relu"); nn.init.zeros_(lin.bias)
print(f"after kaiming_normal_: std {lin.weight.std().item():.5f} | ml.01 He sqrt(2/fan_in) = {math.sqrt(2 / 256):.5f}")
```
```text
default nn.Linear weight std 0.03599 | formula 1/sqrt(3*fan_in) = 0.03608 | bias is also random (not zero as in ml.01): std 0.0368
after kaiming_normal_: std 0.08791 | ml.01 He sqrt(2/fan_in) = 0.08839
```

### 3.4 Losses are modules too, and their conventions matter

| Loss | Input | Target | Notes |
|---|---|---|---|
| `nn.CrossEntropyLoss` | raw **logits** `(N, C)` | class indices, **`long`**, shape `(N,)` | applies log-softmax itself: **never put a softmax before it** |
| `nn.BCEWithLogitsLoss` | raw logits `(N,)` or `(N, 1)` | floats in {0, 1}, same shape | stable fused sigmoid + BCE |
| `nn.MSELoss` | predictions | targets of the **same shape** | a shape mismatch silently broadcasts (bug 9) |
| `nn.NLLLoss` | **log**-probabilities | class indices | what `CrossEntropyLoss` is built on |

```python run
logits = torch.randn(4, 3); y = torch.tensor([0, 2, 1, 2])
ce = nn.CrossEntropyLoss()(logits, y)
manual = -F.log_softmax(logits, dim=1)[torch.arange(4), y].mean()                   # the formula of ml.01 section 4.2
print("CrossEntropyLoss", round(ce.item(), 6), "| our formula", round(manual.item(), 6), "| equal:", bool(torch.isclose(ce, manual)))
try:
    nn.CrossEntropyLoss()(logits, y.int())
except RuntimeError as e:
    print("labels of the wrong dtype raise:", str(e)[:70])
wrong = nn.CrossEntropyLoss()(F.softmax(logits, dim=1), y)
print("softmax BEFORE cross-entropy: loss", round(wrong.item(), 4), "vs correct", round(ce.item(), 4), "(no error: just a worse, squashed gradient)")
```
```text
CrossEntropyLoss 1.951258 | our formula 1.951258 | equal: True
labels of the wrong dtype raise: expected target dtype to be Long or Byte, but got Int
softmax BEFORE cross-entropy: loss 1.303 vs correct 1.9513 (no error: just a worse, squashed gradient)
```

### 3.5 Hooks: look inside without changing the model

A **forward hook** is a function called with a layer's input and output every time it runs. Use it to inspect activations (dead units, scale) while debugging.

```python run
stats = {}
def make_hook(name):
    def hook(module, inp, out): stats[name] = (out.detach().mean().item(), out.detach().std().item(), (out.detach() == 0).float().mean().item())
    return hook
m = MLP([64, 64, 64, 10])
handles = [layer.register_forward_hook(make_hook(f"layer {i}")) for i, layer in enumerate(m.net) if isinstance(layer, nn.ReLU)]
m(torch.randn(256, 64))
print(pd.DataFrame(stats, index=["mean", "std", "share exactly zero"]).T.round(3).to_string())
for h in handles: h.remove()                                                          # always remove hooks you no longer need
```
```text
           mean     std  share exactly zero
layer 1 0.22500 0.33000             0.50100
layer 3 0.08600 0.13400             0.53100
```

### 3.6 Try it

1. Write a module `Residual(nn.Module)` that returns `x + f(x)` for an inner `nn.Sequential`. Check that its parameters are registered.
2. Freeze the first layer (`p.requires_grad_(False)`) and confirm that its gradient stays `None` after a backward pass.

## 4. Data: Dataset and DataLoader

### 4.1 Two small abstractions

A **`Dataset`** says how many examples there are (`__len__`) and how to fetch the `i`-th (`__getitem__`). A **`DataLoader`** wraps a dataset and serves **shuffled mini-batches**, optionally with several worker processes. Separating the two keeps data code testable.

```python run
Xd, yd = datasets.load_digits(return_X_y=True)
X_tr_np, X_te_np, y_tr_np, y_te_np = model_selection.train_test_split(Xd / 16.0, yd, test_size=0.25, random_state=0, stratify=yd)
mu, sd = X_tr_np.mean(0), X_tr_np.std(0) + 1e-8                                       # statistics from the TRAINING set only
X_tr = torch.tensor((X_tr_np - mu) / sd, dtype=torch.float32); y_tr = torch.tensor(y_tr_np)
X_te = torch.tensor((X_te_np - mu) / sd, dtype=torch.float32); y_te = torch.tensor(y_te_np)
ds = TensorDataset(X_tr, y_tr)
print(len(ds), "examples | one item:", ds[0][0].shape, ds[0][1].dtype)
loader = DataLoader(ds, batch_size=64, shuffle=True)
xb, yb = next(iter(loader))
print("a batch:", xb.shape, yb.shape, "| batches per epoch:", len(loader), "(the last one has", len(ds) - 64 * (len(loader) - 1), "examples; use drop_last=True to drop it)")
```
```text
1347 examples | one item: torch.Size([64]) torch.int64
a batch: torch.Size([64, 64]) torch.Size([64]) | batches per epoch: 22 (the last one has 3 examples; use drop_last=True to drop it)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the data flow of a DataLoader. On the left, a TensorDataset of 1347 digit examples, each with a feature vector of 64 numbers and an integer label. In the middle, a shuffle step. On the right, a stack of mini-batches: 21 batches of shape (64, 64) with labels (64,), and a last batch of only 3 examples. Label len(loader) = 22 and show the effect of drop_last=True."

### 4.2 Shuffling and reproducibility

`shuffle=True` draws a new random order each epoch. To make runs reproducible, pass a seeded `generator`.

```python run
def first_labels(seed):
    g = torch.Generator().manual_seed(seed)
    return next(iter(DataLoader(ds, batch_size=8, shuffle=True, generator=g)))[1].tolist()
print("seed 0 twice:", first_labels(0) == first_labels(0), "| seed 0 vs seed 1:", first_labels(0) == first_labels(1))
sorted_loader = DataLoader(TensorDataset(X_tr[y_tr.argsort()], y_tr.sort().values), batch_size=64, shuffle=False)
print("a SORTED dataset without shuffling serves single-class batches:", [len(set(b[1].tolist())) for b in list(sorted_loader)[:4]], "<- number of distinct classes in each of the first four batches")
```
```text
seed 0 twice: True | seed 0 vs seed 1: False
a SORTED dataset without shuffling serves single-class batches: [1, 1, 2, 1] <- number of distinct classes in each of the first four batches
```

### 4.3 A custom Dataset, with a transform

For images you often apply a random transformation each time an example is fetched (data augmentation), which is why the per-item `__getitem__` exists.

```python run
class DigitImages(Dataset):
    """Items are (1, 8, 8) image tensors and integer labels; `augment` applies a random one-pixel shift."""
    def __init__(self, X, y, augment=False, seed=0):
        self.X, self.y, self.augment = X.reshape(-1, 1, 8, 8), y, augment
        self.rng = np.random.default_rng(seed)
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        img = self.X[i]
        if self.augment:
            dy, dx = self.rng.integers(-1, 2, 2)
            img = torch.roll(img, shifts=(int(dy), int(dx)), dims=(1, 2))
        return img, self.y[i]
di = DigitImages(X_tr, y_tr, augment=True)
print("item shape", di[0][0].shape, "| two fetches of the same item differ (random shift):", not bool(torch.equal(di[0][0], di[0][0])))
```
```text
item shape torch.Size([1, 8, 8]) | two fetches of the same item differ (random shift): True
```

### 4.4 Splitting, class imbalance and `collate_fn`

```python run
train_set, val_set = random_split(ds, [1000, len(ds) - 1000], generator=torch.Generator().manual_seed(0))
print("random_split sizes:", len(train_set), len(val_set))
y_imb = torch.cat([torch.zeros(900, dtype=torch.long), torch.ones(100, dtype=torch.long)])
weights = (1.0 / torch.bincount(y_imb).float())[y_imb]                                  # rarer class -> larger sampling weight
sampler = WeightedRandomSampler(weights, num_samples=len(y_imb), replacement=True, generator=torch.Generator().manual_seed(0))
batch_y = torch.cat([b[1] for b in DataLoader(TensorDataset(torch.zeros(1000, 1), y_imb), batch_size=100, sampler=sampler)])
print("class balance in the data: 10% positive | in the weighted batches:", round(batch_y.float().mean().item(), 3))
def pad_collate(batch):                                                                  # variable-length sequences -> one padded tensor
    seqs, labels = zip(*batch)
    return nn.utils.rnn.pad_sequence(seqs, batch_first=True), torch.tensor(labels)
seq_ds = [(torch.ones(n), 0) for n in (3, 5, 2, 4)]
print("padded batch shape from sequences of lengths 3,5,2,4:", next(iter(DataLoader(seq_ds, batch_size=4, collate_fn=pad_collate)))[0].shape)
```
```text
random_split sizes: 1000 347
class balance in the data: 10% positive | in the weighted batches: 0.5
padded batch shape from sequences of lengths 3,5,2,4: torch.Size([4, 5])
```

### 4.5 `num_workers`: when does loading matter

With `num_workers > 0`, worker processes prepare batches in parallel with training. For tiny in-memory data like ours it only adds start-up cost; it matters when each item needs file reading or heavy augmentation.

### 4.6 Try it

1. Time one epoch of `DataLoader` over `TensorDataset` for batch sizes 8, 64, 512. Why is it slower with small batches even before any model runs?
2. Write a `Dataset` that returns both an image and its noisy copy (for a denoising task).

## 5. Optimisers, schedulers and gradient clipping

### 5.1 Optimisers

`torch.optim` contains the optimisers of ml.01 (`SGD` with `momentum`/`nesterov`, `RMSprop`, `Adam`, `AdamW`, and more). They take the parameters and implement `step()` and `zero_grad()`. **Parameter groups** give different learning rates to different parts (a common fine-tuning pattern, ml.03 and ml.05).

```python run
m = MLP([64, 32, 10])
opt = torch.optim.AdamW([{"params": m.net[0].parameters(), "lr": 1e-4}, {"params": m.net[2].parameters(), "lr": 1e-2}], weight_decay=1e-2)
print("learning rates per group:", [g["lr"] for g in opt.param_groups], "| weight decay:", opt.param_groups[0]["weight_decay"], "(AdamW: decoupled, as in ml.01 section 10.2)")
```
```text
learning rates per group: [0.0001, 0.01] | weight decay: 0.01 (AdamW: decoupled, as in ml.01 section 10.2)
```

### 5.2 Learning-rate schedulers

A scheduler changes the learning rate over time. Call `scheduler.step()` **once per epoch** (or per batch for `OneCycleLR`), **after** `optimizer.step()`.

```python run
def lr_trace(make, n=10):
    p = [nn.Parameter(torch.zeros(1))]; o = torch.optim.SGD(p, lr=0.1); s = make(o); out = []
    for _ in range(n):
        out.append(o.param_groups[0]["lr"]); o.step(); s.step()
    return out
S = torch.optim.lr_scheduler
print(pd.DataFrame({"StepLR(step=3, gamma=0.5)": lr_trace(lambda o: S.StepLR(o, 3, 0.5)), "CosineAnnealingLR(T_max=10)": lr_trace(lambda o: S.CosineAnnealingLR(o, 10)),
                    "OneCycleLR(max_lr=0.1, 10 steps)": lr_trace(lambda o: S.OneCycleLR(o, 0.1, total_steps=10))}, index=range(10)).round(4).T.to_string())
```
```text
                                       0       1       2       3       4       5       6       7       8       9
StepLR(step=3, gamma=0.5)        0.10000 0.10000 0.10000 0.05000 0.05000 0.05000 0.02500 0.02500 0.02500 0.01250
CosineAnnealingLR(T_max=10)      0.10000 0.09760 0.09050 0.07940 0.06550 0.05000 0.03450 0.02060 0.00950 0.00240
OneCycleLR(max_lr=0.1, 10 steps) 0.00400 0.05200 0.10000 0.09500 0.08120 0.06110 0.03890 0.01880 0.00500 0.00000
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot the learning rate against step (0 to 9) for three PyTorch schedulers starting at lr 0.1: StepLR(step=3, gamma=0.5) giving a staircase 0.1, 0.05, 0.025, 0.0125; CosineAnnealingLR(T_max=10) falling smoothly towards 0.0024 at step 9; and OneCycleLR(max_lr=0.1, 10 steps) starting at 0.004, peaking at 0.1 at step 2, then decaying to 0. Use labelled axes and a legend."

### 5.3 Gradient clipping

If a batch produces an enormous gradient, one step can wreck the model. **Clipping** rescales the gradient so its global norm does not exceed a limit. Call it after `backward()` and before `step()`.

```python run
p = nn.Parameter(torch.tensor([3.0, 4.0])); (p * torch.tensor([300.0, 400.0])).sum().backward()
print("gradient before clipping", p.grad.tolist(), "norm", p.grad.norm().item())
total = nn.utils.clip_grad_norm_([p], max_norm=1.0)
print("clip_grad_norm_ returns the ORIGINAL norm", round(total.item(), 1), "| gradient after:", [round(v, 4) for v in p.grad.tolist()], "norm", round(p.grad.norm().item(), 4))
```
```text
gradient before clipping [300.0, 400.0] norm 500.0
clip_grad_norm_ returns the ORIGINAL norm 500.0 | gradient after: [0.6, 0.8] norm 1.0
```

### 5.4 Try it

1. Replace `AdamW` by `SGD(momentum=0.9)` on the digits problem of section 6. What learning rate works?
2. Use `ReduceLROnPlateau` and print when it cuts the learning rate.


## 6. The training loop

### 6.1 The loop you must be able to write from memory

Every PyTorch training script, from this toy to a large language model, is the same loop. It has five steps in a fixed order inside the batch loop, and it is worth memorising them as one sentence: **zero the gradients, forward, loss, backward, step.**

```text
for epoch in range(epochs):
    model.train()                                  # dropout on, batch norm uses batch statistics
    for xb, yb in train_loader:
        xb, yb = xb.to(device), yb.to(device)
        optimizer.zero_grad()                      # 1. clear the old gradients (they accumulate!)
        logits = model(xb)                         # 2. forward pass
        loss = loss_fn(logits, yb)                 # 3. loss
        loss.backward()                            # 4. backward pass: fills p.grad for every parameter
        optimizer.step()                           # 5. update the parameters
    scheduler.step()                               # once per epoch (after the optimiser step)
    model.eval()                                   # dropout off, batch norm uses running statistics
    with torch.no_grad():                          # no graph: faster, less memory
        ... evaluate on the validation set ...
```

Below is the same loop written as two reusable functions. One function runs an epoch in either mode, because the only differences between training and evaluation are the optimiser step and the gradient setting.

```python run
def run_epoch(model, loader, loss_fn, optimizer=None, device="cpu"):
    training = optimizer is not None
    model.train(training)
    total_loss, correct, n = 0.0, 0, 0
    with torch.set_grad_enabled(training):
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            logits = model(xb)
            loss = loss_fn(logits, yb)
            if training:
                optimizer.zero_grad(set_to_none=True)
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * len(yb)                           # .item() -> a plain number, no graph kept
            correct += (logits.argmax(1) == yb).sum().item()
            n += len(yb)
    return total_loss / n, correct / n

def fit(model, train_loader, val_loader, epochs=20, lr=2e-3, weight_decay=1e-2, patience=None, device="cpu", seed=None):
    model.to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs)
    loss_fn = nn.CrossEntropyLoss()
    hist, best, best_state, bad = [], float("inf"), None, 0
    for ep in range(epochs):
        tl, ta = run_epoch(model, train_loader, loss_fn, opt, device)
        vl, va = run_epoch(model, val_loader, loss_fn, None, device)
        sched.step()
        hist.append((ep + 1, tl, vl, ta, va))
        if patience:
            if vl < best - 1e-6: best, best_state, bad = vl, {k: v.clone() for k, v in model.state_dict().items()}, 0
            else:
                bad += 1
                if bad >= patience: break
    if best_state is not None: model.load_state_dict(best_state)
    return pd.DataFrame(hist, columns=["epoch", "train loss", "val loss", "train acc", "val acc"]).set_index("epoch")

def seed_everything(seed):
    import random
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)

val_loader = DataLoader(val_set, batch_size=256)
test_loader = DataLoader(TensorDataset(X_te, y_te), batch_size=256)
seed_everything(0)
train_loader = DataLoader(train_set, batch_size=32, shuffle=True, generator=torch.Generator().manual_seed(0))
model = MLP([64, 64, 32, 10])
t0 = time.perf_counter()
hist = fit(model, train_loader, val_loader, epochs=25)
print(f"25 epochs in {time.perf_counter() - t0:.1f} s")
print(hist.iloc[[0, 1, 2, 4, 9, 14, 24]].round(4).to_string())
print(f"\nTEST accuracy {run_epoch(model, test_loader, nn.CrossEntropyLoss())[1]:.4f}  (the NumPy network of ml.01 reached 0.969)")
```
```text
25 epochs in 0.9 s
       train loss  val loss  train acc  val acc
epoch                                          
1         1.94480   1.32240    0.51800  0.77230
2         0.80780   0.46780    0.82500  0.91640
3         0.28820   0.22820    0.93200  0.93950
5         0.09260   0.16700    0.98600  0.95970
10        0.02250   0.14770    0.99800  0.96830
15        0.01080   0.14600    1.00000  0.96830
25        0.00750   0.14600    1.00000  0.96540

TEST accuracy 0.9711  (the NumPy network of ml.01 reached 0.969)
```

### 6.2 What each line is for, and what breaks if it is missing

| Line | Purpose | If missing |
|---|---|---|
| `model.train()` / `model.eval()` | switch dropout and batch norm between their two behaviours | dropout stays on during evaluation (noisy, worse) or off during training (no regularisation) |
| `.to(device)` | model and data on the same device | `RuntimeError: Expected all tensors to be on the same device` |
| `optimizer.zero_grad()` | clear stale gradients | gradients accumulate across steps; training becomes erratic (bug 1, section 10) |
| `loss.backward()` | compute gradients | the parameters never change |
| `optimizer.step()` | apply the update | the parameters never change |
| `torch.no_grad()` | no graph during evaluation | memory use and time grow for nothing |
| `.item()` on the loss | a number instead of a tensor | keeping `loss` tensors alive keeps every batch's graph in memory (bug 10) |
| `scheduler.step()` | move the learning-rate schedule | the learning rate never changes |

### 6.3 Gradient accumulation: a bigger batch than fits in memory

Because gradients **add** into `.grad`, you can process several small batches and step once. If you divide each loss by the number of accumulated batches, the result equals one large batch.

```python run
torch.manual_seed(1)
m = MLP([64, 32, 10]); xb, yb = X_tr[:64], y_tr[:64]
lf = nn.CrossEntropyLoss()
m.zero_grad(); lf(m(xb), yb).backward()
g_big = [p.grad.clone() for p in m.parameters()]
m.zero_grad()
for k in range(4):
    (lf(m(xb[16 * k:16 * (k + 1)]), yb[16 * k:16 * (k + 1)]) / 4).backward()                 # four batches of 16, each loss divided by 4
g_acc = [p.grad.clone() for p in m.parameters()]
print("one batch of 64 vs four accumulated batches of 16: max |gradient difference| =", max((a - b).abs().max().item() for a, b in zip(g_big, g_acc)))
```
```text
one batch of 64 vs four accumulated batches of 16: max |gradient difference| = 1.4901161193847656e-08
```

(With batch norm the two differ, because the batch statistics change with the batch size.)

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a diagram comparing one big batch of 64 examples with four accumulated batches of 16. In the first, one forward and backward pass gives a gradient. In the second, four passes each have their loss divided by 4, and their gradients are added into the same .grad box, with optimizer.step() called once at the end. Show that the two final gradients are equal (difference about 1e-8)."

### 6.4 Evaluation beyond accuracy

```python run
model.eval()
with torch.no_grad():
    pred = model(X_te).argmax(1)
cm = pd.crosstab(pd.Series(y_te.numpy(), name="true"), pd.Series(pred.numpy(), name="predicted"))
print("errors:", int((pred != y_te).sum()), "of", len(y_te), "| most confused pairs (true, predicted, count):",
      sorted([(i, j, int(cm.loc[i, j])) for i in cm.index for j in cm.columns if i != j and cm.loc[i, j] > 0], key=lambda t: -t[2])[:3])
```
```text
errors: 13 of 450 | most confused pairs (true, predicted, count): [(8, 1, 2), (0, 6, 1), (1, 5, 1)]
```

### 6.5 Try it

1. Write the loop again on a blank page without looking, for a regression task with `MSELoss`. What changes (hint: `argmax` and accuracy)?
2. Add gradient clipping to `run_epoch` with an argument `clip=None`.

## 7. Saving, loading and resuming

### 7.1 Save the state, not the object

A model's learned knowledge is its **`state_dict`**: an ordered dictionary of parameter and buffer tensors. The recommended practice is to save the `state_dict` and to recreate the model from code before loading it. Saving the whole model object with pickle ties the file to the exact class definition and file layout, and loading pickles from untrusted sources can run arbitrary code: recent PyTorch defaults to `weights_only=True` for this reason.

```python run
path = pathlib.Path(tempfile.mkdtemp()) / "mlp.pt"
torch.save(model.state_dict(), path)
fresh = MLP([64, 64, 32, 10])
fresh.load_state_dict(torch.load(path, weights_only=True))
fresh.eval()
with torch.no_grad():
    same = torch.equal(model(X_te), fresh(X_te))
print(f"saved {path.stat().st_size / 1024:.1f} KB | the reloaded model gives identical outputs: {same}")
bad = MLP([64, 32, 10])
try:
    bad.load_state_dict(torch.load(path, weights_only=True))
except RuntimeError as e:
    print("loading into a different architecture fails loudly:", str(e).splitlines()[0][:60], "...")
```
```text
saved 28.3 KB | the reloaded model gives identical outputs: True
loading into a different architecture fails loudly: Error(s) in loading state_dict for MLP: ...
```

### 7.2 Checkpoints: resume training exactly

To resume you need more than the weights: the **optimiser state** (Adam's moving averages), the **scheduler**, the **epoch**, and control of the randomness (shuffling, dropout). With those, stopping and resuming gives exactly the same result as one uninterrupted run. We prove it with per-epoch seeded loaders.

```python run
def make_state(seed=0):
    torch.manual_seed(seed)
    m = MLP([64, 32, 10]); o = torch.optim.AdamW(m.parameters(), lr=3e-3); s = torch.optim.lr_scheduler.CosineAnnealingLR(o, T_max=6)
    return m, o, s
def train_epochs(m, o, s, start, end):
    lf = nn.CrossEntropyLoss()
    for ep in range(start, end):
        for xb, yb in DataLoader(train_set, batch_size=32, shuffle=True, generator=torch.Generator().manual_seed(1000 + ep)):    # the order depends on the epoch only
            m.train(); o.zero_grad(); lf(m(xb), yb).backward(); o.step()
        s.step()

m1, o1, s1 = make_state(); train_epochs(m1, o1, s1, 0, 6)                         # one uninterrupted run of 6 epochs
m2, o2, s2 = make_state(); train_epochs(m2, o2, s2, 0, 3)                         # 3 epochs, then stop and checkpoint
ckpt = {"model": m2.state_dict(), "optimizer": o2.state_dict(), "scheduler": s2.state_dict(), "epoch": 3}
ckpt_path = path.parent / "ckpt.pt"; torch.save(ckpt, ckpt_path)
m3, o3, s3 = make_state(seed=123)                                                 # a NEW process: different random init, then restore everything
c = torch.load(ckpt_path, weights_only=True)
m3.load_state_dict(c["model"]); o3.load_state_dict(c["optimizer"]); s3.load_state_dict(c["scheduler"])
train_epochs(m3, o3, s3, c["epoch"], 6)
print("max |weights: uninterrupted - resumed| =", max((a - b).abs().max().item() for a, b in zip(m1.parameters(), m3.parameters())))
m4, o4, s4 = make_state(seed=123); m4.load_state_dict(c["model"]); train_epochs(m4, o4, s4, 3, 6)             # forgetting the optimiser and scheduler state
print("max |weights| difference if the optimiser state is NOT restored =", max((a - b).abs().max().item() for a, b in zip(m1.parameters(), m4.parameters())))
```
```text
max |weights: uninterrupted - resumed| = 0.0
max |weights| difference if the optimiser state is NOT restored = 0.1487094759941101
```

A difference of exactly zero shows that the checkpoint holds everything needed. Forgetting the optimiser state (a very common shortcut) changes the trajectory.

### 7.3 Practical rules

| Rule | Reason |
|---|---|
| Save `state_dict`s, not whole models | portability; safe loading |
| Save the config (sizes, hyperparameters) next to the weights | the code must rebuild the same architecture |
| Save the best-so-far model by validation score, and the last checkpoint for resuming | two different purposes |
| Use `map_location="cpu"` when loading a GPU checkpoint on a CPU machine | otherwise it tries to find the GPU |
| Record the library version in the checkpoint | state dicts change across versions occasionally |
| Never `torch.load` a file you do not trust (without `weights_only=True`) | pickle can execute code |
| Store only plain Python types (numbers, strings, lists, dicts) beside the tensors | `weights_only=True` refuses custom classes, even `torch.__version__` (a `TorchVersion` object): wrap it with `str()` |

## 8. Devices, speed and reproducibility

### 8.1 Device-agnostic code

The training code should not hard-code `"cuda"`. Choose a device once, move the model and each batch to it, and the same script runs on a laptop or a GPU server.

```python run
device = "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
print("chosen device:", device)
m = MLP([64, 32, 10]).to(device)
print("model parameters live on:", next(m.parameters()).device, "| a batch must be moved too: xb.to(device), yb.to(device)")
print("the CPU has", torch.get_num_threads(), "intra-op threads;", end=" ")
A_ = torch.randn(1200, 1200)
for th in [1, 6]:
    torch.set_num_threads(th); A_ @ A_; t0 = time.perf_counter()
    for _ in range(5): A_ @ A_
    print(f"{th} thread(s): {(time.perf_counter() - t0) / 5 * 1000:.0f} ms per matmul;", end=" ")
torch.set_num_threads(6); print()
```
```text
chosen device: cpu
model parameters live on: cpu | a batch must be moved too: xb.to(device), yb.to(device)
the CPU has 6 intra-op threads; 1 thread(s): 55 ms per matmul; 6 thread(s): 29 ms per matmul; 
```

On a GPU, the points that matter are: keep the data pipeline from starving the GPU (`num_workers`, `pin_memory=True`), avoid `.item()` or `.cpu()` inside the inner loop (each forces a synchronisation), and use mixed precision. Those parts need a GPU to demonstrate, so they appear as code you can run on your machine:

```python
# Try it on your machine (needs an NVIDIA GPU; no output is shown here)
device = "cuda"
model = MLP([64, 128, 10]).to(device)
scaler = torch.amp.GradScaler("cuda")
for xb, yb in DataLoader(train_set, batch_size=256, shuffle=True, pin_memory=True, num_workers=2):
    xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
    with torch.autocast("cuda", dtype=torch.float16):          # run the forward pass in half precision
        loss = nn.CrossEntropyLoss()(model(xb), yb)
    opt.zero_grad(); scaler.scale(loss).backward(); scaler.step(opt); scaler.update()      # scale the loss to avoid float16 underflow
```

### 8.2 Vectorise: never loop over examples

```python run
m = MLP([64, 64, 10]).eval()
t0 = time.perf_counter()
with torch.no_grad():
    for i in range(300): m(X_tr[i:i + 1])
t_loop = time.perf_counter() - t0
t0 = time.perf_counter()
with torch.no_grad():
    m(X_tr[:300])
t_vec = time.perf_counter() - t0
print(f"300 predictions one at a time: {t_loop * 1000:.1f} ms | as one batch: {t_vec * 1000:.2f} ms | {t_loop / t_vec:.0f}x faster batched")
```
```text
300 predictions one at a time: 7.4 ms | as one batch: 0.11 ms | 64x faster batched
```

### 8.3 Reproducibility

Training uses randomness in the initial weights, the shuffling and dropout. Fix the seeds (`seed_everything`) for repeatable experiments, and remember that exact repeatability on a GPU also needs deterministic algorithm settings (`torch.use_deterministic_algorithms(True)`), at some cost in speed.

```python run
def one_run(seed, epochs=8):
    seed_everything(seed)
    tl = DataLoader(train_set, batch_size=32, shuffle=True, generator=torch.Generator().manual_seed(seed))
    m = MLP([64, 64, 32, 10]); h = fit(m, tl, val_loader, epochs=epochs)
    return h["val acc"].iloc[-1], m
a1, ma = one_run(0); a2, mb = one_run(0)
print("same seed twice -> identical accuracy:", a1 == a2, "| identical weights:", all(torch.equal(p, q) for p, q in zip(ma.parameters(), mb.parameters())))
accs = [one_run(s)[0] for s in range(6)]
print(f"six different seeds: val accuracy mean {np.mean(accs):.4f}, std {np.std(accs, ddof=1):.4f}, range {min(accs):.3f} to {max(accs):.3f}")
```
```text
same seed twice -> identical accuracy: True | identical weights: True
six different seeds: val accuracy mean 0.9577, std 0.0043, range 0.951 to 0.963
```

Report **the spread over seeds**, not the best seed (ds.04 section 13). A difference between two models smaller than that spread is not a difference.

### 8.4 Try it

1. Time `DataLoader` with `num_workers=0` versus 2 on the digits data. Which is faster, and why?
2. Does `torch.manual_seed(0)` alone make `np.random` calls repeatable? Test it.

## 9. Convolutional networks for images

### 9.1 Why not a fully connected layer for images

An image has structure: nearby pixels are related, and the same pattern (an edge, a loop) can appear anywhere. A fully connected layer treats every pixel position separately: an enormous number of weights, and a pattern learned in one corner is useless in another. A **convolutional layer** slides a small filter (a `k×k` grid of weights) across the image, computing the same weighted sum at every position:

- **Few parameters**: the filter is shared across all positions.
- **Translation equivariance**: a pattern shifted in the input produces a response shifted in the output.
- **Local connectivity**: each output depends on a small neighbourhood.

Tensors for images are `(N, C, H, W)`: batch, channels, height, width. For an `H`-pixel dimension, kernel `k`, padding `p` and stride `s`, the output size is `floor((H + 2p − k)/s) + 1`.

```python run
conv = nn.Conv2d(in_channels=1, out_channels=8, kernel_size=3, padding=1)
x = torch.randn(5, 1, 8, 8)
print("input", tuple(x.shape), "-> conv(1->8, k=3, p=1)", tuple(conv(x).shape), "-> maxpool(2)", tuple(nn.MaxPool2d(2)(conv(x)).shape))
print("conv parameters:", sum(p.numel() for p in conv.parameters()), "= 8 filters x (1 channel x 3 x 3) + 8 biases | a Linear layer from 64 pixels to 8x8x8 outputs would have", 64 * 512 + 512)
for k, p, s in [(3, 0, 1), (3, 1, 1), (3, 1, 2), (5, 2, 1)]:
    print(f"H=8, k={k}, p={p}, s={s}: formula {(8 + 2 * p - k) // s + 1}, PyTorch {nn.Conv2d(1, 1, k, stride=s, padding=p)(x).shape[-1]}")
```
```text
input (5, 1, 8, 8) -> conv(1->8, k=3, p=1) (5, 8, 8, 8) -> maxpool(2) (5, 8, 4, 4)
conv parameters: 80 = 8 filters x (1 channel x 3 x 3) + 8 biases | a Linear layer from 64 pixels to 8x8x8 outputs would have 33280
H=8, k=3, p=0, s=1: formula 6, PyTorch 6
H=8, k=3, p=1, s=1: formula 8, PyTorch 8
H=8, k=3, p=1, s=2: formula 4, PyTorch 4
H=8, k=5, p=2, s=1: formula 8, PyTorch 8
```

### 9.2 A convolution written by hand, and the referee

```python run
def conv2d_naive(img, kernel):                                           # one channel, no padding, stride 1 ("valid" cross-correlation, as PyTorch does)
    H, W = img.shape; k = kernel.shape[0]
    return torch.tensor([[(img[i:i + k, j:j + k] * kernel).sum() for j in range(W - k + 1)] for i in range(H - k + 1)])
img = torch.randn(8, 8); ker = torch.randn(3, 3)
ours = conv2d_naive(img, ker); theirs = F.conv2d(img[None, None], ker[None, None])[0, 0]
print("hand-written convolution equals F.conv2d:", bool(torch.allclose(ours, theirs, atol=1e-5)), "| output", tuple(ours.shape))
edge = torch.tensor([[-1.0, 0.0, 1.0]] * 3)                              # a vertical-edge detector
step_img = torch.zeros(6, 6); step_img[:, 3:] = 1
print("vertical edge filter on an image with a step at column 3:"); print(F.conv2d(step_img[None, None], edge[None, None])[0, 0])
```
```text
hand-written convolution equals F.conv2d: True | output (6, 6)
vertical edge filter on an image with a step at column 3:
tensor([[0., 3., 3., 0.],
        [0., 3., 3., 0.],
        [0., 3., 3., 0.],
        [0., 3., 3., 0.]])
```

A filter is a learned feature detector. Stacking convolutional layers builds up from edges to strokes to digit parts.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate a 3x3 convolution filter sliding over a 6x6 image with stride 1 and no padding. The image is 0 in columns 0-2 and 1 in columns 3-5. The filter has rows [-1, 0, 1] repeated three times. Show the window at each position, the dot product written into a 4x4 output grid, and the final output where the two middle columns are 3 and the outer columns are 0, marking where the vertical edge is."

### 9.3 A small CNN for the 8x8 digits, against the MLP

> **Predict the output.** A small CNN and an MLP with a similar number of parameters (about 6,000 each) are trained on centred 8x8 digits, then tested on the same test images shifted by one pixel. Which loses more accuracy?

<details><summary>Answer</summary>

The MLP. On centred test images the two are close (0.982 and 0.971). After a one-pixel shift the CNN falls to 0.731 and the MLP to 0.536. The CNN's filters are shared across positions, so a shifted pattern still activates them; the MLP's weights are tied to pixel positions.

</details>

```python run
class SmallCNN(nn.Module):
    def __init__(self, channels=(16, 32), n_classes=10, dropout=0.0):
        super().__init__()
        c1, c2 = channels
        self.features = nn.Sequential(
            nn.Conv2d(1, c1, 3, padding=1), nn.BatchNorm2d(c1), nn.ReLU(), nn.MaxPool2d(2),            # 8x8 -> 4x4
            nn.Conv2d(c1, c2, 3, padding=1), nn.BatchNorm2d(c2), nn.ReLU(), nn.MaxPool2d(2))           # 4x4 -> 2x2
        self.head = nn.Sequential(nn.Flatten(), nn.Dropout(dropout), nn.Linear(c2 * 2 * 2, n_classes))
    def forward(self, x): return self.head(self.features(x))

img = lambda X: X.reshape(-1, 1, 8, 8)
train_img = TensorDataset(img(X_tr), y_tr)
tr_set_i, va_set_i = random_split(train_img, [1000, len(X_tr) - 1000], generator=torch.Generator().manual_seed(0))
tl_i = DataLoader(tr_set_i, batch_size=32, shuffle=True, generator=torch.Generator().manual_seed(0)); vl_i = DataLoader(va_set_i, batch_size=256)
seed_everything(0); cnn = SmallCNN()
seed_everything(0); mlp_ = MLP([64, 64, 32, 10])
print("parameters: CNN", sum(p.numel() for p in cnn.parameters()), "| MLP", sum(p.numel() for p in mlp_.parameters()))
h_c = fit(cnn, tl_i, vl_i, epochs=25)
h_m = fit(mlp_, DataLoader(train_set, batch_size=32, shuffle=True, generator=torch.Generator().manual_seed(0)), val_loader, epochs=25)
def test_acc(model, X):
    model.eval()
    with torch.no_grad(): return (model(X).argmax(1) == y_te).float().mean().item()
shift = lambda X, dx: torch.roll(X.reshape(-1, 1, 8, 8), shifts=dx, dims=3)
print(pd.DataFrame({"CNN": [test_acc(cnn, img(X_te)), test_acc(cnn, shift(X_te, 1))], "MLP": [test_acc(mlp_, X_te), test_acc(mlp_, shift(X_te, 1).reshape(-1, 64))]},
                   index=["test accuracy, centred digits", "test accuracy, every image shifted one pixel"]).round(4).to_string())
```
```text
parameters: CNN 6186 | MLP 6570
                                                 CNN     MLP
test accuracy, centred digits                0.98220 0.97110
test accuracy, every image shifted one pixel 0.73110 0.53560
```

On centred digits the two are close (the data are easy). The CNN's advantage appears when the digits move: shifting every test image by one pixel costs the CNN about 25 points (0.98 to 0.73) but the MLP about 43 (0.97 to 0.54), because the CNN's filters are shared across positions. Neither is robust, which is why augmentation (the project) matters. That difference, and not raw accuracy on a clean benchmark, is why convolutional layers dominate vision.

### 9.4 Try it

1. Add a third convolution to `SmallCNN`. What is the spatial size at the end, and why does `Flatten`'s output size matter for the final `Linear`?
2. Compute the receptive field of one output unit of the second convolution (kernel 3, after a 2x2 pool).

## 10. Debugging training problems: ten classic bugs

### 10.1 A method

ml.01 section 12 gave the checklist; here it is as code, and then applied to the **ten bugs that account for most "my model does not learn" questions**. For each, we run a deliberately broken version, measure the symptom, and name the check that finds it. All use the same small digits problem so the baseline is clear.

> **Predict the output.** Four of the bugs tested below are about training mechanics: forgetting `zero_grad()`, a softmax before the cross-entropy, a learning rate 100 times too high, and unshuffled sorted data. Which is the most damaging, and which is the mildest?

<details><summary>Answer</summary>

Forgetting `zero_grad()` is the most damaging: the loss ends near 307 and the test accuracy is 10% (chance). A learning rate 100 times too high, unshuffled sorted data and unnormalised inputs also end at chance. The softmax before the cross-entropy is the mildest: it still reaches 94.2% (against 97.3% for the correct code) and gives no error at all, which is exactly why it survives in real code.

</details>

```python run
def diagnose(model, loader, loss_fn=None, n_classes=10):
    """Cheap pre-flight checks on a model and a data loader. Returns a dict of findings."""
    loss_fn = loss_fn or nn.CrossEntropyLoss()
    rep = {}
    xb, yb = next(iter(loader))
    rep["labels: dtype, min, max"] = (str(yb.dtype), int(yb.min()), int(yb.max()))
    rep["inputs: mean, std, finite"] = (round(xb.float().mean().item(), 3), round(xb.float().std().item(), 3), bool(torch.isfinite(xb).all()))
    model.train(); model.zero_grad()
    out = model(xb)
    loss = loss_fn(out, yb); loss.backward()
    rep[f"initial loss (expect ln C = {math.log(n_classes):.2f})"] = round(loss.item(), 3)
    rep["parameters with NO gradient"] = [n for n, p in model.named_parameters() if p.grad is None]
    rep["parameters with ZERO gradient"] = [n for n, p in model.named_parameters() if p.grad is not None and p.grad.abs().max() == 0]
    gn = [p.grad.norm().item() for p in model.parameters() if p.grad is not None and p.ndim > 1]
    rep["gradient norm first / last weight"] = (f"{gn[0]:.1e}", f"{gn[-1]:.1e}") if gn else "n/a"
    opt = torch.optim.Adam(model.parameters(), lr=1e-2)
    for _ in range(100):                                                           # try to overfit ONE batch
        opt.zero_grad(); l = loss_fn(model(xb), yb); l.backward(); opt.step()
    rep["loss after 100 steps on ONE batch (expect ~0)"] = round(l.item(), 4)
    return rep

def run_variant(name, epochs=8, lr=0.05, **flags):
    """Train a small MLP with one deliberate bug; return a one-line summary."""
    seed_everything(0)
    model = MLP([64, 64, 32, 10], dropout=flags.get("dropout", 0.0))
    data_X = X_tr * flags.get("scale", 1.0)
    ds_ = TensorDataset(data_X, y_tr)
    if flags.get("sorted"): idx = y_tr.argsort(); ds_ = TensorDataset(data_X[idx], y_tr[idx])
    loader = DataLoader(ds_, batch_size=32, shuffle=not flags.get("sorted"), generator=torch.Generator().manual_seed(0))
    opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
    lf = nn.CrossEntropyLoss(); losses = []
    for ep in range(epochs):
        model.train()
        for xb, yb in loader:
            if not flags.get("no_zero_grad"): opt.zero_grad()
            out = model(xb)
            if flags.get("softmax_first"): out = F.softmax(out, dim=1)
            if flags.get("detached"):
                h = xb
                for layer in model.net[:-1]: h = layer(h)
                out = model.net[-1](h.detach())
            loss = lf(out, yb); loss.backward(); opt.step(); losses.append(loss.item())
    model.eval()
    with torch.no_grad():
        acc = (model(X_te * flags.get("scale", 1.0)).argmax(1) == y_te).float().mean().item()
    return {"bug": name, "final train loss": float(np.mean(losses[-10:])), "test accuracy": acc, "any NaN": bool(np.isnan(losses).any())}

rows = [run_variant("0. correct code"),
        run_variant("1. forgot optimizer.zero_grad()", no_zero_grad=True),
        run_variant("2. softmax before CrossEntropyLoss", softmax_first=True),
        run_variant("5. learning rate 100x too high", lr=5.0),
        run_variant("6. sorted data, no shuffling", sorted=True),
        run_variant("7. unnormalised inputs (x 50)", scale=50.0),
        run_variant("8. .detach() inside forward", detached=True)]
print(pd.DataFrame(rows).set_index("bug").round(4).to_string())
```
```text
                                    final train loss  test accuracy  any NaN
bug                                                                         
0. correct code                              0.00310        0.97330    False
1. forgot optimizer.zero_grad()            306.81570        0.10000    False
2. softmax before CrossEntropyLoss           1.51800        0.94220    False
5. learning rate 100x too high               2.57480        0.10220    False
6. sorted data, no shuffling                 2.80220        0.10000    False
7. unnormalised inputs (x 50)                2.30460        0.10220    False
8. .detach() inside forward                  1.47930        0.70440    False
```

### 10.2 Reading the table: symptoms and checks

| # | Bug | Symptom seen above | The check that finds it |
|---|---|---|---|
| 1 | forgot `zero_grad()` | gradients pile up: erratic or diverging loss, worse accuracy | print `p.grad.norm()` twice in a row; it doubles |
| 2 | softmax before `CrossEntropyLoss` | trains, but slowly and to a worse accuracy | the loss stays high even on an easy task; compare with the correct pairing |
| 5 | learning rate far too high | loss stuck high or `nan`, accuracy at chance | lower the rate; the update-to-weight ratio of ml.01 section 12 |
| 6 | sorted data, no shuffle | each batch holds one class: the model oscillates | print the labels of the first batches |
| 7 | unnormalised inputs | huge initial loss and unstable steps | print `xb.mean(), xb.std()` (the `diagnose` helper does) |
| 8 | `.detach()` in forward | the early layers receive no gradient and never learn | the "parameters with NO gradient" line |

Now bugs 3, 4, 9 and 10, which show up as errors, warnings or hidden costs rather than as a bad loss.

```python run
# Bug 3: labels of the wrong dtype or shape
try: nn.CrossEntropyLoss()(torch.randn(4, 3), torch.tensor([0.0, 1.0, 2.0, 1.0]))
except RuntimeError as e: print("3a. float class indices ->", str(e)[:75])
print("3b. float labels of shape (N, C) are treated as PROBABILITIES, silently:", nn.CrossEntropyLoss()(torch.randn(4, 3), torch.softmax(torch.randn(4, 3), 1)).item() > 0, "(no error: soft labels are a feature, so a one-hot float by accident also 'works')")

# Bug 4: evaluating in train mode (dropout stays on)
seed_everything(0); mdrop = MLP([64, 64, 10], dropout=0.5)
hd = fit(mdrop, DataLoader(train_set, 32, shuffle=True, generator=torch.Generator().manual_seed(0)), val_loader, epochs=15)
with torch.no_grad():
    mdrop.train(); acc_train_mode = (mdrop(X_te).argmax(1) == y_te).float().mean().item()
    mdrop.eval(); acc_eval_mode = (mdrop(X_te).argmax(1) == y_te).float().mean().item()
print(f"4.  same model, same data: accuracy with dropout ON {acc_train_mode:.3f} vs OFF {acc_eval_mode:.3f}; forgetting model.eval() costs accuracy and makes results random")

# Bug 9: MSELoss with mismatched shapes broadcasts silently
pred = torch.tensor([[1.0], [2.0], [3.0], [4.0]]); target = torch.tensor([1.0, 2.0, 3.0, 4.0])            # (4,1) against (4,)
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always"); bad = nn.MSELoss()(pred, target)
print(f"9.  MSELoss of a perfect prediction with shapes (4,1) vs (4,): {bad.item():.3f} (should be 0), warned: {len(w) > 0} -> {str(w[0].message)[:60] if w else ''}...")
print("    fixed with target.view(-1, 1):", nn.MSELoss()(pred, target.view(-1, 1)).item())

# Bug 10: accumulating loss tensors keeps every batch's graph alive
total_bad, total_good = 0.0, 0.0
m10 = MLP([64, 16, 10])
for i in range(5):
    l = nn.CrossEntropyLoss()(m10(X_tr[i * 32:(i + 1) * 32]), y_tr[i * 32:(i + 1) * 32])
    total_bad = total_bad + l; total_good += l.item()
print(f"10. running total as tensors keeps the graph: grad_fn = {type(total_bad.grad_fn).__name__} (memory grows every batch) | with .item(): a plain {type(total_good).__name__}")
```
```text
3a. float class indices -> expected target dtype to be Long or Byte, but got Float
3b. float labels of shape (N, C) are treated as PROBABILITIES, silently: True (no error: soft labels are a feature, so a one-hot float by accident also 'works')
4.  same model, same data: accuracy with dropout ON 0.931 vs OFF 0.953; forgetting model.eval() costs accuracy and makes results random
9.  MSELoss of a perfect prediction with shapes (4,1) vs (4,): 2.500 (should be 0), warned: True -> Using a target size (torch.Size([4])) that is different to t...
    fixed with target.view(-1, 1): 0.0
10. running total as tensors keeps the graph: grad_fn = AddBackward0 (memory grows every batch) | with .item(): a plain float
```

### 10.3 The pre-flight check finds most of them

```python run
def broken(name):
    seed_everything(0); m = MLP([64, 64, 32, 10])
    if name == "healthy": return m, DataLoader(train_set, 32, shuffle=True)
    if name == "detached":
        class Det(MLP):
            def forward(self, x):
                h = x
                for layer in self.net[:-1]: h = layer(h)
                return self.net[-1](h.detach())
        return Det([64, 64, 32, 10]), DataLoader(train_set, 32, shuffle=True)
    if name == "unnormalised": return m, DataLoader(TensorDataset(X_tr * 50, y_tr), 32, shuffle=True)
    if name == "labels shifted by one": return m, DataLoader(TensorDataset(X_tr, (y_tr + 1) % 10), 32, shuffle=True)
for name in ["healthy", "detached", "unnormalised", "labels shifted by one"]:
    model, loader = broken(name)
    print(f"--- {name}")
    for k, v in diagnose(model, loader).items(): print(f"    {k}: {v}")
```
```text
--- healthy
    labels: dtype, min, max: ('torch.int64', 0, 9)
    inputs: mean, std, finite: (-0.03, 0.863, True)
    initial loss (expect ln C = 2.30): 2.31
    parameters with NO gradient: []
    parameters with ZERO gradient: []
    gradient norm first / last weight: ('2.3e-01', '1.7e-01')
    loss after 100 steps on ONE batch (expect ~0): 0.0
--- detached
    labels: dtype, min, max: ('torch.int64', 0, 9)
    inputs: mean, std, finite: (0.02, 0.965, True)
    initial loss (expect ln C = 2.30): 2.311
    parameters with NO gradient: ['net.0.weight', 'net.0.bias', 'net.2.weight', 'net.2.bias']
    parameters with ZERO gradient: []
    gradient norm first / last weight: ('2.2e-01', '2.2e-01')
    loss after 100 steps on ONE batch (expect ~0): 0.9982
--- unnormalised
    labels: dtype, min, max: ('torch.int64', 0, 9)
    inputs: mean, std, finite: (-2.045, 44.284, True)
    initial loss (expect ln C = 2.30): 3.979
    parameters with NO gradient: []
    parameters with ZERO gradient: []
    gradient norm first / last weight: ('1.3e+01', '7.9e+00')
    loss after 100 steps on ONE batch (expect ~0): 0.0
--- labels shifted by one
    labels: dtype, min, max: ('torch.int64', 0, 9)
    inputs: mean, std, finite: (-0.041, 0.886, True)
    initial loss (expect ln C = 2.30): 2.327
    parameters with NO gradient: []
    parameters with ZERO gradient: []
    gradient norm first / last weight: ('2.5e-01', '1.4e-01')
    loss after 100 steps on ONE batch (expect ~0): 0.0
```

The `detached` network is exposed by the lines "parameters with NO gradient" and the failure to overfit one batch (it can only move its last layer). The unnormalised inputs show up in the input statistics (a standard deviation of 44 instead of about 1) and a high initial loss (4.0 instead of 2.3), although the network can still memorise one batch. Shifted labels are a **consistent** relabelling, which a network learns perfectly well: no check inside the training code can see it, which is why labels must be checked against the data source, outside the code.

### 10.4 The loop to follow when a model does not learn

1. **Reproduce at small scale**: a tiny subset, a few epochs.
2. **Overfit one batch.** If you cannot, there is a bug in the model, loss, labels or update. This single test finds most bugs.
3. **Check the first loss** against `ln C`.
4. **Check shapes, dtypes and devices** at the loss line.
5. **Look at gradients**: any `None`, zero, `nan` or wildly different norm across layers.
6. **Look at the data**: print a batch, its labels, its statistics; check the split.
7. **Lower the learning rate by 10x**; if it now learns, the rate was the problem.
8. **Only then** change the architecture.

### 10.5 Try it

1. Add `torch.autograd.set_detect_anomaly(True)` to a run with a `log(0)` in the loss. What does it print, and what is its cost?
2. Write a bug of your own (for example, applying `model.eval()` and never switching back) and extend `run_variant` to expose it.


## 11. Project: an image classifier trained end to end

### 11.1 The brief

Build a small, honest, **end-to-end image classifier** for the 8x8 digit images, in a module you could hand to someone else:

1. **Data**: a train/validation/test split that is stratified and seeded, normalisation statistics taken from the **training** images only, an optional augmentation that applies to training data only.
2. **Model and training**: a convolutional network, the training loop of section 6 with a scheduler, early stopping and a fixed seed.
3. **Evaluation and error analysis**: test accuracy, per-class recall, a confusion summary, and a look at the actual mistakes.
4. **A deployable artefact**: one file holding the weights, the configuration and the normalisation, loadable into a `Predictor` that **validates its input** and returns a class and a confidence.
5. **A record** of the run: configuration, data fingerprint, environment, metrics.
6. **Tests** for the properties that matter: shapes, gradient flow, ability to overfit a batch, train/eval behaviour, determinism, save/load equivalence, input validation, absence of leakage.

### 11.2 The module

```python run
import subprocess
proj = pathlib.Path(tempfile.mkdtemp()) / "imgclf_project"; proj.mkdir()
(proj / "imgclf.py").write_text('''"""imgclf: an end-to-end image classifier for the 8x8 digit images (PyTorch)."""
import dataclasses, hashlib, json, math, platform, random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset, TensorDataset
from sklearn import datasets, model_selection


@dataclasses.dataclass
class Config:
    seed: int = 0
    epochs: int = 20
    lr: float = 3e-3
    weight_decay: float = 1e-2
    batch_size: int = 32
    augment: bool = False
    channels: tuple = (16, 32)
    dropout: float = 0.2
    patience: int = 6


def seed_everything(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def load_data(seed=0):
    """Stratified train/validation/test split; normalisation statistics come from the TRAINING images only."""
    X, y = datasets.load_digits(return_X_y=True)
    X = X / 16.0
    X_dev, X_te, y_dev, y_te = model_selection.train_test_split(X, y, test_size=0.25, random_state=seed, stratify=y)
    X_tr, X_va, y_dev_tr, y_va = model_selection.train_test_split(X_dev, y_dev, test_size=0.25, random_state=seed, stratify=y_dev)
    y_tr = y_dev_tr
    mean, std = float(X_tr.mean()), float(X_tr.std())
    to_t = lambda A: torch.tensor(((A - mean) / std).reshape(-1, 1, 8, 8), dtype=torch.float32)
    return {"train": (to_t(X_tr), torch.tensor(y_tr)), "val": (to_t(X_va), torch.tensor(y_va)), "test": (to_t(X_te), torch.tensor(y_te)), "mean": mean, "std": std,
            "fingerprint": hashlib.sha256(np.ascontiguousarray(X).tobytes()).hexdigest()[:16]}


class ImageDataset(Dataset):
    """(image, label) items; when `augment` is true each fetch applies a random shift of up to one pixel (training data only)."""
    def __init__(self, X, y, augment=False, seed=0):
        self.X, self.y, self.augment, self.rng = X, y, augment, np.random.default_rng(seed)
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        img = self.X[i]
        if self.augment:
            dy, dx = (int(v) for v in self.rng.integers(-1, 2, 2))
            img = torch.roll(img, shifts=(dy, dx), dims=(1, 2))
        return img, self.y[i]


class SmallCNN(nn.Module):
    def __init__(self, channels=(16, 32), n_classes=10, dropout=0.0):
        super().__init__()
        c1, c2 = channels
        self.features = nn.Sequential(nn.Conv2d(1, c1, 3, padding=1), nn.BatchNorm2d(c1), nn.ReLU(), nn.MaxPool2d(2),
                                      nn.Conv2d(c1, c2, 3, padding=1), nn.BatchNorm2d(c2), nn.ReLU(), nn.MaxPool2d(2))
        self.head = nn.Sequential(nn.Flatten(), nn.Dropout(dropout), nn.Linear(c2 * 4, n_classes))
    def forward(self, x): return self.head(self.features(x))


def run_epoch(model, loader, loss_fn, optimizer=None):
    training = optimizer is not None
    model.train(training)
    total, correct, n = 0.0, 0, 0
    with torch.set_grad_enabled(training):
        for xb, yb in loader:
            logits = model(xb); loss = loss_fn(logits, yb)
            if training:
                optimizer.zero_grad(set_to_none=True); loss.backward(); optimizer.step()
            total += loss.item() * len(yb); correct += (logits.argmax(1) == yb).sum().item(); n += len(yb)
    return total / n, correct / n


def train_model(cfg, data=None):
    seed_everything(cfg.seed)
    data = data or load_data(cfg.seed)
    Xtr, ytr = data["train"]; Xva, yva = data["val"]
    loader = DataLoader(ImageDataset(Xtr, ytr, cfg.augment, cfg.seed), batch_size=cfg.batch_size, shuffle=True, generator=torch.Generator().manual_seed(cfg.seed))
    val_loader = DataLoader(TensorDataset(Xva, yva), batch_size=256)
    model = SmallCNN(cfg.channels, dropout=cfg.dropout)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=cfg.epochs)
    lf = nn.CrossEntropyLoss()
    hist, best, best_state, bad = [], float("inf"), None, 0
    for ep in range(cfg.epochs):
        tl, ta = run_epoch(model, loader, lf, opt); vl, va = run_epoch(model, val_loader, lf)
        sched.step(); hist.append({"epoch": ep + 1, "train_loss": tl, "val_loss": vl, "train_acc": ta, "val_acc": va})
        if vl < best - 1e-6: best, best_state, bad = vl, {k: v.clone() for k, v in model.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= cfg.patience: break
    model.load_state_dict(best_state)
    return model, hist, data


def evaluate(model, X, y):
    model.eval()
    with torch.no_grad():
        p = torch.softmax(model(X), 1)
    pred, conf = p.argmax(1), p.max(1).values
    cm = np.zeros((10, 10), int)
    for t, q in zip(y.numpy(), pred.numpy()): cm[t, q] += 1
    wrong = [(int(i), int(y[i]), int(pred[i]), float(conf[i])) for i in torch.nonzero(pred != y).flatten()]
    return {"accuracy": float((pred == y).float().mean()), "per_class_recall": (cm.diagonal() / cm.sum(1)).round(3).tolist(), "confusion": cm,
            "mistakes": sorted(wrong, key=lambda t: -t[3])}


def save_artifact(model, cfg, data, path):
    torch.save({"state": model.state_dict(), "config": dataclasses.asdict(cfg), "mean": data["mean"], "std": data["std"], "torch": str(torch.__version__)}, path)      # plain types only: weights_only=True refuses custom classes


class Predictor:
    """Validates its input, applies the training normalisation, and returns (class, confidence)."""
    def __init__(self, model, mean, std):
        self.model, self.mean, self.std = model.eval(), mean, std
    @classmethod
    def load(cls, path):
        a = torch.load(path, weights_only=True)
        cfg = Config(**{**a["config"], "channels": tuple(a["config"]["channels"])})
        m = SmallCNN(cfg.channels, dropout=cfg.dropout); m.load_state_dict(a["state"])
        return cls(m, a["mean"], a["std"])
    def predict(self, images):
        a = np.asarray(images, dtype=float)
        if a.shape == (8, 8): a = a[None]
        if a.ndim != 3 or a.shape[1:] != (8, 8): raise ValueError(f"expected images of shape (8, 8) or (N, 8, 8), got {np.asarray(images).shape}")
        if not np.isfinite(a).all() or a.min() < 0 or a.max() > 16: raise ValueError("pixel values must be finite and between 0 and 16")
        x = torch.tensor(((a / 16.0 - self.mean) / self.std)[:, None], dtype=torch.float32)
        with torch.no_grad(): p = torch.softmax(self.model(x), 1)
        return p.argmax(1).numpy(), p.max(1).values.numpy()


def experiment_record(cfg, data, metrics):
    return {"config": dataclasses.asdict(cfg), "data_fingerprint": data["fingerprint"], "metrics": metrics,
            "environment": {"python": platform.python_version(), "torch": str(torch.__version__), "numpy": np.__version__}}
''', encoding="utf-8")
print("imgclf.py:", len((proj / "imgclf.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
imgclf.py: 136 lines
```

### 11.3 The tests

```python run
(proj / "test_imgclf.py").write_text('''import numpy as np, pytest, torch, torch.nn as nn
import imgclf as ic

DATA = ic.load_data(0)

def small_model(seed=0):
    torch.manual_seed(seed); return ic.SmallCNN((8, 16), dropout=0.2)

def test_output_shape_is_batch_by_classes():
    assert small_model()(torch.randn(5, 1, 8, 8)).shape == (5, 10)

def test_every_parameter_receives_a_gradient():
    m = small_model(); nn.CrossEntropyLoss()(m(DATA["train"][0][:16]), DATA["train"][1][:16]).backward()
    assert all(p.grad is not None and p.grad.abs().sum() > 0 for p in m.parameters()), "a parameter with no gradient is cut off from the loss"

def test_the_initial_loss_is_near_ln_of_the_number_of_classes():
    m = small_model().eval()
    loss = nn.CrossEntropyLoss()(m(DATA["train"][0][:256]), DATA["train"][1][:256]).item()
    assert 1.8 < loss < 3.2, f"initial loss {loss:.2f} is far from ln 10 = 2.30"

def test_the_network_can_overfit_one_batch():
    m = small_model(); x, y = DATA["train"][0][:32], DATA["train"][1][:32]
    opt = torch.optim.Adam(m.parameters(), lr=1e-2); lf = nn.CrossEntropyLoss(); m.train()
    for _ in range(150):
        opt.zero_grad(); loss = lf(m(x), y); loss.backward(); opt.step()
    assert loss.item() < 0.05, "if one batch cannot be memorised, there is a bug in the model, the loss or the update"

def test_train_mode_is_random_and_eval_mode_is_deterministic():
    m = small_model(); x = DATA["train"][0][:16]
    m.train(); assert not torch.equal(m(x), m(x)), "dropout should make two training-mode passes differ"
    m.eval(); assert torch.equal(m(x), m(x))

def test_batched_and_single_predictions_agree_in_eval_mode():
    m = small_model().eval(); x = DATA["test"][0][:8]
    with torch.no_grad():
        batch = m(x); single = torch.cat([m(x[i:i + 1]) for i in range(8)])
    assert torch.allclose(batch, single, atol=1e-5), "batch norm must use running statistics in eval mode"

def test_the_same_seed_gives_identical_weights_and_different_seeds_do_not():
    cfg = ic.Config(epochs=2, patience=5)
    a, _, _ = ic.train_model(cfg, DATA); b, _, _ = ic.train_model(cfg, DATA); c, _, _ = ic.train_model(ic.Config(seed=1, epochs=2), DATA)
    assert all(torch.equal(p, q) for p, q in zip(a.parameters(), b.parameters())), "same seed must reproduce the run exactly"
    assert not all(torch.equal(p, q) for p, q in zip(a.parameters(), c.parameters()))

def test_the_splits_are_disjoint_and_normalisation_uses_training_data_only():
    d = ic.load_data(0)
    tr, va, te = (d[k][0].reshape(len(d[k][1]), -1) for k in ("train", "val", "test"))
    assert abs(tr.mean().item()) < 1e-4 and abs(tr.std().item() - 1) < 1e-3, "training images are standardised exactly"
    assert abs(va.mean().item()) > 1e-4 or abs(te.mean().item()) > 1e-4, "validation/test images are NOT re-standardised with their own statistics"
    keys = [set(map(lambda r: tuple(np.round(r.numpy(), 4)), t[:200])) for t in (tr, va, te)]
    assert not (keys[0] & keys[1]) and not (keys[0] & keys[2]), "no image may appear in two splits"

def test_augmentation_applies_to_training_data_only():
    x, y = DATA["train"]
    plain = ic.ImageDataset(x, y, augment=False); aug = ic.ImageDataset(x, y, augment=True, seed=3)
    assert torch.equal(plain[0][0], plain[0][0]) and torch.equal(plain[0][0], x[0])
    assert any(not torch.equal(aug[i][0], x[i]) for i in range(30))

def test_save_load_round_trip_and_input_validation(tmp_path):
    cfg = ic.Config(epochs=2); m, _, d = ic.train_model(cfg, DATA); path = tmp_path / "a.pt"; ic.save_artifact(m, cfg, d, path)
    pr = ic.Predictor.load(path)
    raw = np.random.default_rng(0).integers(0, 17, (6, 8, 8)).astype(float)
    cls, conf = pr.predict(raw); cls2, conf2 = ic.Predictor(m, d["mean"], d["std"]).predict(raw)
    assert (cls == cls2).all() and np.allclose(conf, conf2, atol=1e-6), "a reloaded model must predict exactly like the original"
    for bad in [np.zeros((7, 7)), np.zeros((2, 8, 9)), np.full((8, 8), 99.0), np.full((8, 8), np.nan)]:
        with pytest.raises(ValueError): pr.predict(bad)
    assert pr.predict(raw[0])[0].shape == (1,)
''', encoding="utf-8")
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "test_imgclf.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-900:] or res.stderr.strip()[-900:])
```
```text
..........                                                               [100%]
10 passed in 6.26s
```

### 11.4 Train, evaluate, analyse the errors

```python run
sys.path.insert(0, str(proj))
import importlib, imgclf as ic
importlib.reload(ic)

cfg = ic.Config(epochs=25, augment=False)
data = ic.load_data(cfg.seed)
t0 = time.perf_counter()
model_p, hist_p, _ = ic.train_model(cfg, data)
print(f"trained {len(hist_p)} epochs in {time.perf_counter() - t0:.1f} s (early stopping patience {cfg.patience})")
print(pd.DataFrame(hist_p).set_index("epoch").iloc[[0, 1, 2, 4, 9, -1]].round(4).to_string())
res = ic.evaluate(model_p, *data["test"])
print(f"\nTEST accuracy {res['accuracy']:.4f} on {len(data['test'][1])} images | errors {len(res['mistakes'])}")
print("recall per digit:", dict(enumerate(res["per_class_recall"])))
```
```text
trained 25 epochs in 2.8 s (early stopping patience 6)
       train_loss  val_loss  train_acc  val_acc
epoch                                          
1         1.30670   0.63460    0.64060  0.90500
2         0.38490   0.24030    0.91780  0.96140
3         0.20300   0.14060    0.95350  0.98220
5         0.09900   0.09600    0.98220  0.97920
10        0.03160   0.05610    0.99600  0.98520
25        0.01120   0.04440    0.99800  0.98220

TEST accuracy 0.9933 on 450 images | errors 3
recall per digit: {0: 1.0, 1: 1.0, 2: 0.977, 3: 0.978, 4: 1.0, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.0, 9: 0.978}
```

The mistakes are the most informative output. Each entry is `(index, true digit, predicted digit, confidence)`, sorted so that the **most confident wrong predictions** come first. We draw the worst one as text.

```python run
print("most confident mistakes (index, true, predicted, confidence):", [(i, t, p, round(c, 3)) for i, t, p, c in res["mistakes"][:4]])
i, t, p, c = res["mistakes"][0]
raw_img = (data["test"][0][i, 0] * data["std"] + data["mean"]) * 16
print(f"\ntest image {i}: true digit {t}, predicted {p} with confidence {c:.2f}")
for row in raw_img.round().int().tolist():
    print("   " + "".join(" .:-=+*#%@"[min(9, max(0, v * 9 // 16))] * 2 for v in row))
```
```text
most confident mistakes (index, true, predicted, confidence): [(64, 2, 1, 0.878), (66, 9, 1, 0.636), (299, 3, 7, 0.623)]

test image 64: true digit 2, predicted 1 with confidence 0.88
           **%%::  
         ..@@@@**  
         ==##@@**  
         ::++@@--  
       --**@@##    
     ++@@@@##      
     ..==##@@++    
           **@@**  
```

An error analysis starts here: look at the image, ask whether a person would also hesitate, and note whether the confidently wrong cases are clustered (in one pair of digits, one writing style). A model that is wrong but unsure is a different problem from one that is wrong and sure.

### 11.5 Does augmentation help? Three seeds

```python run
rows = []
for aug in [False, True]:
    accs = []
    for seed in range(3):
        c = ic.Config(seed=seed, epochs=20, augment=aug)
        m, _, d = ic.train_model(c)
        accs.append(ic.evaluate(m, *d["test"])["accuracy"])
    rows.append(("with random one-pixel shifts" if aug else "no augmentation", np.mean(accs), np.std(accs, ddof=1), min(accs), max(accs)))
print(pd.DataFrame(rows, columns=["training", "mean test accuracy", "std over 3 seeds", "min", "max"]).set_index("training").round(4).to_string())
```
```text
                              mean test accuracy  std over 3 seeds     min     max
training                                                                          
no augmentation                          0.99110           0.00220 0.98890 0.99330
with random one-pixel shifts             0.98220           0.00890 0.97330 0.99110
```

As in ml.01, judge it against the spread over seeds, and remember that the test images here are all centred: augmentation helps when the deployed data will vary in ways the training set does not show, and costs a little when it does not.

### 11.6 The deployable artefact

```python run
art = proj / "digits_cnn.pt"
ic.save_artifact(model_p, cfg, data, art)
pred = ic.Predictor.load(art)
raw, labels = datasets.load_digits(return_X_y=True)                                  # raw pixel values 0..16, as a user would supply them
raw = raw.reshape(-1, 8, 8)                                                             # (N, 8, 8): passing the flat (N, 64) rows is rejected by the validation below
cls, conf = pred.predict(raw[:12])
print(f"artefact {art.stat().st_size / 1024:.0f} KB | 12 raw digits -> {cls.tolist()} | truth {labels[:12].tolist()} | confidences {np.round(conf, 2).tolist()}")
for name, bad in [("wrong shape (flat rows)", raw[:3].reshape(3, 64)), ("wrong shape", np.zeros((7, 7))), ("pixel values out of range", np.full((8, 8), 255.0)), ("not a number", np.full((8, 8), np.nan))]:
    try: pred.predict(bad)
    except ValueError as e: print(f"{name:26s} -> ValueError: {e}")
print(json.dumps(ic.experiment_record(cfg, data, {"test_accuracy": round(res["accuracy"], 4)}), indent=1)[:700])
```
```text
artefact 31 KB | 12 raw digits -> [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1] | truth [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1] | confidences [1.0, 1.0, 0.9900000095367432, 1.0, 1.0, 0.9200000166893005, 1.0, 0.9900000095367432, 1.0, 0.9800000190734863, 1.0, 1.0]
wrong shape (flat rows)    -> ValueError: expected images of shape (8, 8) or (N, 8, 8), got (3, 64)
wrong shape                -> ValueError: expected images of shape (8, 8) or (N, 8, 8), got (7, 7)
pixel values out of range  -> ValueError: pixel values must be finite and between 0 and 16
not a number               -> ValueError: pixel values must be finite and between 0 and 16
{
 "config": {
  "seed": 0,
  "epochs": 25,
  "lr": 0.003,
  "weight_decay": 0.01,
  "batch_size": 32,
  "augment": false,
  "channels": [
   16,
   32
  ],
  "dropout": 0.2,
  "patience": 6
 },
 "data_fingerprint": "23a53393488b04f9",
 "metrics": {
  "test_accuracy": 0.9933
 },
 "environment": {
  "python": "3.14.4",
  "torch": "2.15.0+cpu",
  "numpy": "2.5.4"
 }
}
```

(While writing this project the first version of `save_artifact` stored `torch.__version__` directly. `torch.load(..., weights_only=True)` then **refused to load the file**, because that value is a `TorchVersion` object, not a plain string. The safe loader accepts only tensors and plain Python types; the fix is `str(torch.__version__)`. A good reminder that safe loading is strict on purpose, and that a round-trip test catches this on the day you write the code.)

### 11.7 What to hand in

1. `imgclf.py` and `test_imgclf.py`, all tests passing.
2. The training log and the test result for the default configuration.
3. An error analysis: the confusion pairs, the five most confident mistakes drawn as text, your explanation of two of them.
4. The three-seed comparison of **two** design choices of your own (for example channel widths, dropout, augmentation) with your reading of it.
5. A one-paragraph "model card": intended input, performance, limits (what happens on digits that are rotated or drawn on a different grid).
6. The ten-bug table of section 10, with one new bug of your own that your tests or `diagnose` would catch.

### 11.8 Extensions

1. Add mixed precision and `pin_memory` (guarded by `torch.cuda.is_available()`) and test that the CPU path still works.
2. Export the model with `torch.onnx.export` or `torch.jit.trace` (ml.06) and check it gives the same outputs.
3. Add a calibration check (ds.04 section 11) and temperature scaling, and report the Brier score before and after.
4. Replace the CNN by the `MLP` of this chapter inside the same pipeline and compare, including on shifted test images.
5. Use `torch.utils.data.DataLoader(num_workers=2)` and measure whether it helps on this tiny dataset (it will not; explain why).

## 12. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Labels of the wrong dtype | an error, or a silent change of meaning (soft labels) | `long` class indices for `CrossEntropyLoss` (3.4) |
| Softmax before `CrossEntropyLoss` | trains slowly and worse | pass raw logits (3.4, 10) |
| Forgetting `optimizer.zero_grad()` | gradients accumulate; erratic training | zero them every step (2.2, 6.2) |
| Forgetting `model.eval()` | dropout stays on, batch norm uses batch statistics | switch modes explicitly (3.2, 10) |
| Forgetting `model.train()` after evaluating | dropout and batch norm stay in eval mode while training | switch back, or use `run_epoch` which sets it (6.1) |
| Evaluating without `torch.no_grad()` | wasted memory and time | `no_grad` or `inference_mode` (2.3) |
| Accumulating `loss` instead of `loss.item()` | every batch's graph stays in memory | `.item()` (10) |
| Views silently sharing memory | changing one tensor changes another | `clone()` when you need a copy (1.3) |
| NumPy and torch sharing memory | an array changed by a tensor | `torch.tensor(array)` copies (1.5) |
| float32 versus float64, int versus float | errors, or slight numeric differences | check `dtype` at the boundaries (1.2) |
| In-place operations on saved tensors | `RuntimeError` at `backward()` | avoid `_` ops on tensors autograd needs (2.6) |
| Wrong tensor shape, silent broadcasting | wrong loss, no error | assert shapes at the loss; `target.view(-1, 1)` (10) |
| No shuffling of sorted data | one-class batches | `shuffle=True` for training (4.2) |
| Normalisation statistics from all the data | leakage (ds.04) | statistics from the training set only (4.1, 11.2) |
| Saving the whole model object | fragile and unsafe to load | save `state_dict` and the config (7.1) |
| Resuming without the optimiser state | a different training path | checkpoint model, optimiser, scheduler, epoch (7.2) |
| Hard-coded `"cuda"` | code fails on machines without a GPU | device-agnostic code (8.1) |
| Looping over examples | 100 times slower | batch (8.2) |
| Comparing models on one seed | luck mistaken for improvement | several seeds, report the spread (8.3, 11.5) |
| `scheduler.step()` before `optimizer.step()` | a warning, and the first learning rate skipped | optimiser first, scheduler after (5.2) |
| Not overfitting one batch before a long run | long wasted runs | the pre-flight check first (10.4) |

## 13. Summary

- **Tensors** are PyTorch's arrays, described by shape, dtype and device. Labels are `long`; inputs and weights are floats (default float32). Many operations return **views** that share memory (`view`, slicing, `transpose`, `from_numpy`); `clone()` copies. Broadcasting, indexing and reductions follow NumPy's rules.
- **Autograd** records operations on tensors with `requires_grad=True` and `backward()` fills `.grad` on the leaves, which **accumulates** until you zero it. `detach()` and `no_grad()` stop tracking; `autograd.grad` with `create_graph=True` gives higher derivatives; `gradcheck` is the finite-difference test; in-place changes to saved tensors fail at `backward()`. It reproduced the gradients we derived by hand in ml.01.
- **`nn.Module`** registers parameters, buffers and submodules; `state_dict` holds the parameters and buffers (batch norm's running statistics); `train()` and `eval()` switch layer behaviour; hooks inspect activations; the default `nn.Linear` initialisation is a scaled Kaiming scheme. Loss conventions matter: `CrossEntropyLoss` takes raw logits and `long` indices.
- **`Dataset` and `DataLoader`** separate how to fetch one item from how to batch, shuffle and parallelise; seeded generators make shuffling reproducible; `WeightedRandomSampler` and `collate_fn` handle imbalance and variable lengths.
- **Optimisers** (`SGD`, `Adam`, `AdamW`) with parameter groups; **schedulers** (`StepLR`, cosine, `OneCycleLR`) stepped after the optimiser; **gradient clipping** between `backward()` and `step()`.
- **The training loop**: `zero_grad`, forward, loss, backward, step; `model.train()` and `model.eval()` around `no_grad` evaluation; `.item()` for logging. Gradient accumulation equals a larger batch (without batch norm).
- **Saving**: save `state_dict` plus config; checkpoint the optimiser, scheduler and epoch to **resume exactly** (we proved a difference of zero; omitting the optimiser state changes the path); `weights_only=True` for safe loading.
- **Devices and reproducibility**: write device-agnostic code, batch everything, seed everything, report the spread over seeds. GPU-only features (mixed precision, pinned memory) are shown as code to run on your machine.
- **Convolutional layers** share small filters across positions: few parameters and equivariance to shifts. The output size is `floor((H + 2p − k)/s) + 1`. The hand-written convolution equals `F.conv2d`, and a small CNN stayed far more accurate on shifted images than an MLP.
- **Debugging**: overfit one batch; check the initial loss, the gradients, the labels and the inputs. Ten classic bugs were reproduced and measured, and a `diagnose` helper found the structural ones (detached graph, unnormalised inputs). Consistent label errors cannot be seen from inside the training code.
- **The project** `imgclf` is a tested, loadable, input-validating image classifier with a run record, whose behaviour (shapes, gradient flow, overfitting, train/eval, determinism, no leakage, save/load) is guarded by tests.

You reached the outcome of this chapter: you can **write a training loop from memory and diagnose a model that does not learn**, with a method (the pre-flight checks and the bug table) rather than guesses. Next, ml.03 uses convolutional networks on real images: transfer learning with pretrained models, augmentation and fine-tuning, which needs `torchvision` (to be installed when you reach it).
