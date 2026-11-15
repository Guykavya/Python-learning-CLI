# Chapter 7 (ML): Model optimisation and deployment

In ml.06 you learned to ship a model as a reliable service. This chapter asks the next question: **is the model the right size and speed for the place where it has to run?** A model that scores 98 % on your laptop is useless if it needs 2 GB of RAM on a device that has 512 MB, or answers in 300 ms when the page must respond in 50 ms, or costs ten times more to host than the feature earns.

Optimisation is the craft of making a model **smaller**, **faster** or **cheaper** while giving up as little **accuracy** as possible. Nothing here is magic. Every technique trades something for something else, and the only honest way to know the price is to **measure size, latency and accuracy before and after**. That sentence is the syllabus outcome, and it is also the thread of the whole chapter.

You will meet four families of technique, each built by hand first so you know what the library does:

1. **Quantisation**: store and compute with fewer bits per number (32-bit float to 8-bit integer).
2. **Pruning**: remove weights or whole neurons that matter little.
3. **Export and a lean runtime** (ONNX and ONNX Runtime): leave the training framework behind and run a frozen graph, with batching and thread settings that matter more than most people expect.
4. **Small devices**: memory budgets, cold starts, and what changes when the target is a phone or a Raspberry Pi class board.

Prerequisites: ml.02 (PyTorch), ml.06 (serving and measuring a service), ds.04 (honest evaluation: never judge on the training data).

> **How this chapter is built.** The examples that carry the main lessons are real runs, with the output pasted exactly as the computer printed it (Python 3.14, PyTorch 2.15 CPU, ONNX 1.23, ONNX Runtime 1.32, all on this machine). Variations that would only repeat a lesson are **question → worked answer** boxes. A number appears in an answer only if it was really measured, and then it says so. Sections carry optional **Visualise it** prompts you can paste into any AI chat; the course never depends on them.
>
> **Your numbers will differ.** Accuracy is almost the same everywhere, but **latency depends on your CPU, the number of cores, other programs running, and even the temperature of the machine**. Do not compare my milliseconds with yours. Compare the *ratios* (int8 against float32 on the *same* machine), and trust the *direction* of each effect. Section 2 teaches how to measure so that your own ratios are believable.
>
> **What needs the internet.** Nothing at run time. The libraries (`onnx`, `onnxruntime`, `onnxscript`) were installed once with pip; the dataset (8x8 handwritten digits) ships inside scikit-learn. The whole chapter runs in roughly five to ten minutes on a laptop.

```python run
import os, sys, io, time, json, math, copy, zlib, pathlib, tempfile, platform, subprocess, warnings, contextlib, statistics
warnings.filterwarnings("ignore")
import numpy as np
import torch, torch.nn as nn, torch.nn.functional as F
import onnx, onnxruntime as ort
import sklearn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

np.set_printoptions(precision=4, suppress=True, linewidth=120)
ws = pathlib.Path(tempfile.mkdtemp(prefix="opt_ws_"))        # every file this chapter creates lives here
print("python  ", sys.version.split()[0], "|", platform.system())
print("numpy   ", np.__version__, "| scikit-learn", sklearn.__version__)
print("torch   ", torch.__version__, "| onnx", onnx.__version__, "| onnxruntime", ort.__version__)
print("cpu cores:", os.cpu_count(), "| torch threads:", torch.get_num_threads())
print("workspace:", ws.name)
```
```text
python   3.14.4 | Linux
numpy    2.5.4 | scikit-learn 1.9.1
torch    2.15.0+cpu | onnx 1.23.2 | onnxruntime 1.32.0
cpu cores: 8 | torch threads: 6
workspace: opt_ws_aju8oqwq
```

## Table of contents

1. [What "better" means: three budgets](#1-what-better-means-three-budgets)
2. [Measuring honestly: size, latency, accuracy](#2-measuring-honestly-size-latency-accuracy)
3. [Quantisation](#3-quantisation)
4. [Pruning, and why smaller architectures beat both](#4-pruning-and-why-smaller-architectures-beat-both)
5. [ONNX: export, verify, run, optimise](#5-onnx-export-verify-run-optimise)
6. [Batching and latency in a service](#6-batching-and-latency-in-a-service)
7. [Running on small devices](#7-running-on-small-devices)
8. [Choosing: the trade-off table and the Pareto front](#8-choosing-the-trade-off-table-and-the-pareto-front)
9. [Project: optimise a model and report the trade-off](#9-project-optimise-a-model-and-report-the-trade-off)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. What "better" means: three budgets

### 1.1 Size, latency, accuracy (and a few cousins)

"Make the model better" is not a task. "Make it fit and answer fast enough without losing accuracy" is. Every deployment has three **budgets**, and an optimisation is only a win when it respects all of them:

| Budget | What it measures | Who cares | Typical limit |
|---|---|---|---|
| **Size** | bytes on disk, bytes in RAM | app stores, phones, downloads, cold starts | "the app may grow by 20 MB" |
| **Latency** | time for **one** request, from input to answer | users waiting, real-time systems | "p95 under 50 ms" |
| **Throughput** | requests per second the machine can serve | cost of servers | "1,000 requests/s on 2 cores" |
| **Accuracy** | quality of the answers on data it has never seen | everyone | "no more than 1 point below the current model" |

Two cousins are worth naming. **Memory at run time** can be much more than the file size (activations, buffers, the runtime itself). **Energy** matters for phones and sensors: fewer bytes moved means less battery.

The budgets pull against each other. Smaller, faster models usually lose some accuracy; batching raises throughput but can raise the latency of each single request. There is no best model, only a **best choice for your limits**. That is why the project ends with a trade-off table, not one number.

> **Rule 1: start from a requirement.** If nobody told you "the model must be under 10 MB" or "p95 under 20 ms", ask. Without a target you cannot tell when to stop, and every extra optimisation adds risk and complexity for free.

### 1.2 Back-of-envelope arithmetic before any code

You can predict size and rough cost from the architecture alone. Do it first: it tells you which technique can even help.

- **Parameters** (weights and biases) times **bytes per number** gives the size. A float32 is 4 bytes. A model with 1,000,000 parameters is about 4 MB in float32, about 2 MB in float16, about 1 MB in int8.
- **Multiply-accumulates (MACs)** count the work. A fully connected layer from `n_in` to `n_out` does `n_in * n_out` MACs per sample. People often say **FLOPs** and mean about `2 x MACs` (one multiply and one add).
- **Memory-bound or compute-bound?** At batch size 1, every weight is read from memory once and used for **one** multiply. That is about 2 operations per 4 bytes read: the processor spends most of its time *waiting for memory*. With a batch of 64, each weight read serves 64 samples, so the same read does 64 times more arithmetic. This one fact explains why batching raises throughput and why int8 (4 times fewer bytes to read) can speed up a memory-bound layer.

Let us put numbers on the model we will use all chapter. It is deliberately **too big** for its task (that will matter in section 4): a three-layer fully connected network for 8x8 digit images.

```python run
X, y = load_digits(return_X_y=True)
X = (X / 16.0).astype(np.float32)                        # pixel values 0..16 -> 0..1
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
print("train", Xtr.shape, "test", Xte.shape, "| classes:", sorted(set(y.tolist())))

def make_mlp(hidden=1024):
    return nn.Sequential(nn.Linear(64, hidden), nn.ReLU(),
                         nn.Linear(hidden, hidden), nn.ReLU(),
                         nn.Linear(hidden, 10))

def count_params(model):
    return sum(p.numel() for p in model.parameters())

def count_macs(model):
    """Multiply-accumulates per sample for the Linear layers (the bulk of an MLP)."""
    return sum(l.in_features * l.out_features for l in model if isinstance(l, nn.Linear))

big = make_mlp(1024)
n, macs = count_params(big), count_macs(big)
print(f"parameters     : {n:,}")
print(f"MACs per sample: {macs:,}   (about {2*macs/1e6:.1f} MFLOPs)")
for name, nbytes in [("float32", 4), ("float16", 2), ("int8", 1), ("4-bit", 0.5)]:
    print(f"  size as {name:8s}: {n*nbytes/1e6:6.2f} MB")
print(f"bytes read per MAC at batch 1 : {4*n/macs:.2f}  -> memory-bound")
print(f"bytes read per MAC at batch 64: {4*n/(64*macs):.3f}")
```
```text
train (1257, 64) test (540, 64) | classes: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
parameters     : 1,126,410
MACs per sample: 1,124,352   (about 2.2 MFLOPs)
  size as float32 :   4.51 MB
  size as float16 :   2.25 MB
  size as int8    :   1.13 MB
  size as 4-bit   :   0.56 MB
bytes read per MAC at batch 1 : 4.01  -> memory-bound
bytes read per MAC at batch 64: 0.063
```

The size column is exact arithmetic, not a measurement: it is why **quantisation promises 4x**. Real files add a little for biases, names and format overhead; we will measure that in section 2.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 1024x1024 weight matrix as a big grid of squares, and a single input vector as a thin strip. Animate batch size 1: the processor fetches every square of the grid from memory (slow arrow) to do one multiply each. Then animate batch size 64: the same fetch of the grid feeds 64 input strips at once. Label the two pictures 'memory-bound, mostly waiting' and 'compute-bound, mostly working', and show the bytes-per-multiply number under each."

### 1.3 The order of attack

Cheap, safe wins come first. Accuracy-risking changes come last, and each must be measured.

| Step | Technique | Accuracy risk | Typical gain |
|---|---|---|---|
| 1 | **Right-size the architecture** (do you need 1,024 units?) | low, measurable by retraining | large |
| 2 | **Fast runtime** (ONNX Runtime, right thread count) | none (same maths) | 2x to 40x at batch 1 |
| 3 | **Batching** where requests allow it | none | large throughput |
| 4 | **Half precision** (float16 or bfloat16) | very low | 2x smaller |
| 5 | **Int8 quantisation** | low to medium, must test | 4x smaller, often faster |
| 6 | **Pruning** + fine-tuning | medium | smaller only with a sparse format or structure |
| 7 | **Distillation** (small model learns from a big one) | medium | small model, needs training |

Section 3 to 7 follow this order, roughly. The ranking holds for CPUs and small devices. On GPUs, the details change (tensor cores like float16), the principle does not.

### 1.4 Try it

1. A model has 25 million parameters in float32. How big is the file? How big in int8? Would it fit in a phone app limited to 10 MB? What about in 4-bit?
2. A request needs 1 million MACs. A core does about 1 billion MACs per second at best. What is the lowest possible latency of one request? Why is the *measured* latency usually higher?

<details><summary>Answer</summary>

1. float32: 25M x 4 = 100 MB. int8: 25 MB. 4-bit: about 12.5 MB. Even 4-bit does not fit in 10 MB, so you would need a smaller architecture (or pruning plus quantisation) too: quantisation alone is not enough.
2. 1,000,000 / 1,000,000,000 = 0.001 s = **1 ms** at the very best. Measured latency is higher because of memory waiting (section 1.2), framework overhead per call, Python, thread start-up and the other work in the request (parsing, preprocessing, network). Arithmetic gives a *floor*, never a promise.

</details>

## 2. Measuring honestly: size, latency, accuracy

### 2.1 The baseline model

Optimisation always compares against a **baseline**: the model as you have it today. Train it once, record all three numbers, keep the weights on disk. If you do not freeze the baseline, you will later wonder whether a "regression" came from the optimisation or from a different training run.

```python run
def train_mlp(hidden=1024, epochs=30, lr=1e-3, seed=0):
    """Train an MLP on the digits training split. Returns the model in eval mode."""
    torch.manual_seed(seed)
    model = make_mlp(hidden)
    opt = torch.optim.Adam(model.parameters(), lr)
    xt, yt = torch.from_numpy(Xtr), torch.from_numpy(ytr)
    for epoch in range(epochs):
        perm = torch.randperm(len(xt))
        for i in range(0, len(xt), 64):
            idx = perm[i:i + 64]
            opt.zero_grad()
            F.cross_entropy(model(xt[idx]), yt[idx]).backward()
            opt.step()
    return model.eval()

t0 = time.perf_counter()
base = train_mlp(1024)
print(f"trained in {time.perf_counter() - t0:.1f} s")
torch.save(base.state_dict(), ws / "base.pt")                    # freeze the baseline weights

def torch_predict(model):
    """Wrap a PyTorch model as a plain function: numpy array in, numpy logits out."""
    def predict(Xn):
        with torch.inference_mode():
            return model(torch.from_numpy(Xn)).numpy()
    return predict

def accuracy(predict, Xn=None, yn=None):
    Xn = Xte if Xn is None else Xn
    yn = yte if yn is None else yn
    return float((predict(Xn).argmax(1) == yn).mean())

def state_bytes(model):
    """Size of the saved weights in bytes (what you would ship)."""
    buf = io.BytesIO()
    torch.save(model.state_dict(), buf)
    return len(buf.getvalue())

print(f"test accuracy : {accuracy(torch_predict(base)):.4f}")
print(f"saved size    : {state_bytes(base)/1024:.0f} KB   (arithmetic said {count_params(base)*4/1024:.0f} KB of raw weights)")
```
```text
trained in 16.9 s
test accuracy : 0.9796
saved size    : 4403 KB   (arithmetic said 4400 KB of raw weights)
```

The saved file is about 3 KB bigger than the raw weights: names and format overhead. Good enough, and a reminder to **measure the file you ship**, not the one you imagine.

Notice the test split: the model never saw `Xte` during training, so the accuracy is honest. All later comparisons use the same split and the same function.

### 2.2 Latency: the naive way and the careful way

The obvious way to time a model is `t = time.time(); model(x); print(time.time() - t)`. It lies in four ways:

1. **The first call is slower** (memory is allocated, code paths are loaded, caches are cold). Throw it away: do a **warm-up**.
2. **One run is noise.** Operating-system scheduling, other programs and CPU frequency changes add random delays. Repeat many times.
3. **The average hides the bad tail.** A user feels the slow requests. Report the **median (p50)** and the **p95** (the value 95 % of runs beat), not the mean.
4. **`time.time()` is coarse.** Use `time.perf_counter()`, which is made for measuring short durations.

```python run
def bench(fn, x, warmup=20, repeat=200):
    """Time fn(x). Returns milliseconds: median, p95, min. Warm-up calls are not counted."""
    for _ in range(warmup):
        fn(x)
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(x)
        times.append((time.perf_counter() - t0) * 1e3)
    times.sort()
    return {"p50": times[len(times) // 2], "p95": times[int(len(times) * 0.95)], "min": times[0]}

predict = torch_predict(base)
x1 = Xte[:1]                                            # a single request: batch size 1

cold = []
for i in range(6):                                      # the naive view: just call it and look
    t0 = time.perf_counter(); predict(x1); cold.append((time.perf_counter() - t0) * 1e3)
print("first six calls (ms):", [round(v, 3) for v in cold])

r = bench(predict, x1)
print("careful: p50 %.3f ms | p95 %.3f ms | min %.3f ms" % (r["p50"], r["p95"], r["min"]))
```
```text
first six calls (ms): [1.123, 0.569, 0.484, 0.411, 0.36, 0.875]
careful: p50 0.312 ms | p95 0.437 ms | min 0.270 ms
```

Look at the first calls: the very first one is the slowest, and the rest wobble. The careful number is the one you can put in a report. (Your milliseconds will differ from mine; the *shape*, a slow first call then a steadier level, will be the same.)

### 2.3 How big is the noise? Measure it.

Before claiming "A is 10 % faster than B", you must know how much the *same* code varies from run to run. Repeat the whole benchmark several times and look at the spread of the medians.

```python run
meds = [bench(predict, x1, repeat=150)["p50"] for _ in range(7)]
print("seven medians of the SAME code (ms):", [round(v, 3) for v in meds])
spread = (max(meds) - min(meds)) / statistics.median(meds) * 100
print(f"spread between runs: {spread:.1f} % of the median")
```
```text
seven medians of the SAME code (ms): [0.303, 0.306, 0.303, 0.306, 0.3, 0.305, 0.322]
spread between runs: 7.4 % of the median
```

That spread is your **noise floor**. If an optimisation changes latency by less than the spread, you have measured nothing. Two habits keep comparisons fair:

- **Interleave** the candidates (measure A, B, A, B) instead of A five times then B five times, so that slow drift in machine state hits both.
- **Compare ratios on the same machine**, never absolute numbers from different days or computers.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot 200 timings of one model call as a histogram: most bars near 0.5 ms, a long thin tail out to 1.5 ms. Mark the median, the mean and the p95 with three vertical lines, and show that the mean is dragged right by the tail. Add a second histogram of a 'faster' model whose bars overlap the first one heavily, with the caption 'if the histograms overlap this much, you have not shown a speed-up'."

### 2.4 Latency is not throughput: batch size

One request at a time gives the lowest latency for that request. Many requests together gives the best **throughput** (samples per second), because each weight read serves many samples (section 1.2). Measure it:

```python run
print(f"{'batch':>6} {'p50 ms':>9} {'ms/sample':>10} {'samples/s':>10}")
for b in (1, 4, 16, 64, 256, 540):
    r = bench(predict, Xte[:b], repeat=100)
    print(f"{b:>6} {r['p50']:>9.3f} {r['p50']/b:>10.4f} {1000*b/r['p50']:>10.0f}")
```
```text
 batch    p50 ms  ms/sample  samples/s
     1     0.344     0.3443       2905
     4     0.540     0.1350       7406
    16     0.992     0.0620      16133
    64     3.010     0.0470      21265
   256     8.605     0.0336      29750
   540    14.785     0.0274      36524
```

The time for a batch rises much more slowly than the batch size, so the cost **per sample** falls. At the same time, a request that waits in a batch is waiting for its neighbours. Section 6 turns this into a design: collect requests for a few milliseconds, run them together. For now remember the pair: **latency is for one, throughput is for the machine**.

### 2.5 One function that gives the whole row

From now on every candidate model gets the same three measurements in one call. Build it once; the project reuses it.

```python run
def profile(name, predict, size_bytes, repeat=150):
    """Return one comparable row: size, accuracy, single-request latency, batch throughput."""
    one = bench(predict, Xte[:1], repeat=repeat)
    many = bench(predict, Xte[:64], repeat=max(repeat // 2, 30))
    return {"name": name, "size_kb": size_bytes / 1024, "acc": accuracy(predict),
            "p50_ms": one["p50"], "p95_ms": one["p95"], "samples_per_s": 64000 / many["p50"]}

def show(rows, base_name=None):
    """Print rows as a table. If base_name is given, add ratios against that row."""
    ref = next((r for r in rows if r["name"] == base_name), None)
    head = f"{'model':<24}{'size KB':>9}{'acc':>8}{'p50 ms':>9}{'p95 ms':>9}{'samples/s':>11}"
    if ref: head += f"{'size x':>8}{'speed x':>9}{'d acc':>8}"
    print(head)
    for r in rows:
        line = f"{r['name']:<24}{r['size_kb']:>9.0f}{r['acc']:>8.4f}{r['p50_ms']:>9.3f}{r['p95_ms']:>9.3f}{r['samples_per_s']:>11.0f}"
        if ref:
            line += f"{ref['size_kb']/r['size_kb']:>8.2f}{ref['p50_ms']/r['p50_ms']:>9.2f}{r['acc']-ref['acc']:>+8.4f}"
        print(line)

rows = [profile("float32 baseline", torch_predict(base), state_bytes(base))]
show(rows, "float32 baseline")
```
```text
model                     size KB     acc   p50 ms   p95 ms  samples/s  size x  speed x   d acc
float32 baseline             4403  0.9796    0.490    0.575      23399    1.00     1.00 +0.0000
```

This row is the **baseline** of the whole chapter. A claim of improvement always reads as "size x 4.0, speed x 1.6, accuracy change -0.001": three ratios, same machine, same data.

### 2.6 Try it

1. Why is the *minimum* of many timings not a good headline number, even though it is the least noisy?
2. You measured candidate A five times, then candidate B five times, and B was 8 % faster. Give two reasons the conclusion may be wrong.
3. Your service gets one request at a time from different users. Which number do you care about more, latency at batch 1 or throughput at batch 64?

<details><summary>Answer</summary>

1. The minimum is the best case you will almost never see; users experience the typical (p50) and the unlucky (p95) cases. The minimum is useful only as a floor and to estimate noise.
2. The machine state drifted between the two groups (another program started, the CPU warmed up and slowed down, the first group enjoyed a cold, fast CPU), and the 8 % may be inside the noise floor (section 2.3). Interleave the runs, repeat the whole comparison, and compare against the spread.
3. Latency at batch 1, unless you add micro-batching (section 6), which buys throughput by letting requests wait a few milliseconds. The right answer depends on the requirement, which is why you ask for one first.

</details>

## 3. Quantisation

### 3.1 The idea: fewer bits per number

A float32 can hold about 4 billion different values, spread over a huge range. A trained network does not need that much detail. If a weight is 0.0199 and we store 0.0199116 instead, the answers barely move. **Quantisation** stores each number as a small **integer** plus one shared **scale** that says how big a step is.

```
real value  ≈  integer  x  scale          (plus a "zero point" in the asymmetric version)
```

- **Symmetric** quantisation: the integer range is centred on zero (int8: -127 to 127). The scale comes from the largest absolute value: `scale = max|v| / 127`. Zero maps exactly to zero. Weights are usually done this way.
- **Affine (asymmetric)** quantisation: the range is any `[min, max]`, mapped to `0..255`. A **zero point** says which integer stands for the real 0. Good for activations that are never negative (after ReLU).

Do five numbers by hand before using any library:

```python run
def quant_symmetric(v, bits=8):
    """Symmetric: integers in [-qmax, qmax], one scale. Returns (int array, scale)."""
    qmax = 2 ** (bits - 1) - 1
    scale = np.abs(v).max() / qmax
    q = np.clip(np.round(v / scale), -qmax, qmax).astype(np.int8)
    return q, scale

def quant_affine(v, bits=8):
    """Affine: integers in [0, 2^bits - 1] with a zero point. Returns (int array, scale, zero_point)."""
    levels = 2 ** bits - 1
    scale = (v.max() - v.min()) / levels
    zero_point = int(round(-v.min() / scale))
    q = np.clip(np.round(v / scale) + zero_point, 0, levels).astype(np.uint8)
    return q, scale, zero_point

v = np.array([-0.30, -0.05, 0.00, 0.12, 0.45], dtype=np.float32)
q, s = quant_symmetric(v)
print("symmetric  scale = 0.45/127 = %.6f" % s)
print("  integers  :", q.tolist())
back = (q * s).astype(np.float64)
print("  back again:", back.round(4).tolist(), "  error:", np.abs(v - back).round(5).tolist())

qa, sa, zp = quant_affine(v)
print("affine     scale = 0.75/255 = %.6f, zero point = %d  (the integer that means 0.0)" % (sa, zp))
print("  integers  :", qa.tolist())
print("  back again:", ((qa.astype(np.int32) - zp) * sa).round(4).tolist())
```
```text
symmetric  scale = 0.45/127 = 0.003543
  integers  : [-85, -14, 0, 34, 127]
  back again: [-0.3012, -0.0496, 0.0, 0.1205, 0.45]   error: [0.00118, 0.00039, 0.0, 0.00047, 0.0]
affine     scale = 0.75/255 = 0.002941, zero point = 102  (the integer that means 0.0)
  integers  : [0, 85, 102, 143, 255]
  back again: [-0.3, -0.05, 0.0, 0.1206, 0.45]
```

Read the symmetric line: the biggest value 0.45 became exactly 127; 0 stayed 0; everything else was **rounded to the nearest multiple of the scale**. The rounding error of any single number is at most **half a step** (`scale / 2`). That one sentence is the whole theory of why 8-bit quantisation is usually harmless: 255 levels make the step tiny compared with typical weights.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a number line from -0.30 to 0.45 with the five values -0.30, -0.05, 0.00, 0.12, 0.45 as dots. Underneath, draw the 255 evenly spaced tick marks of the int8 grid (spacing 0.003543). Animate each dot snapping to its nearest tick, and show the small gap as a red segment labelled 'rounding error, at most half a step'. Then make the grid coarser (3 bits: only 7 ticks) so the red segments become large."

### 3.2 Quantising real weights

Now the middle layer of our model: 1,048,576 weights in float32. Quantise them to int8, dequantise, and measure what was lost.

```python run
w = base[2].weight.detach().numpy()                        # shape (1024, 1024), float32
q, scale = quant_symmetric(w)
err = np.abs(w - q.astype(np.float32) * scale)
print(f"weights  : {w.shape}, min {w.min():.4f}, max {w.max():.4f}")
print(f"scale    : {scale:.6f}   half step: {scale/2:.6f}")
print(f"error    : max {err.max():.6f}  mean {err.mean():.6f}   (max is exactly half a step)")
print(f"memory   : float32 {w.nbytes:,} bytes -> int8 {q.nbytes:,} bytes  ({w.nbytes // q.nbytes}x smaller)")
print("first four:", w[0, :4].round(5), "->", q[0, :4], "->", (q[0, :4] * scale).round(5))
```
```text
weights  : (1024, 1024), min -0.1791, max 0.2424
scale    : 0.001909   half step: 0.000954
error    : max 0.000954  mean 0.000477   (max is exactly half a step)
memory   : float32 4,194,304 bytes -> int8 1,048,576 bytes  (4x smaller)
first four: [-0.0436  0.0105  0.0086  0.0293] -> [-23   6   4  15] -> [-0.0439  0.0115  0.0076  0.0286]
```

A mean error of about 0.0005 on weights of size 0.02 is small noise, spread randomly over a million weights. Neural networks are remarkably tolerant of this kind of noise, because each output sums over many inputs and the random errors partly cancel.

**The outlier problem.** The scale is set by the *largest* absolute weight. One huge weight stretches the grid and makes every ordinary weight coarser. The cure is a **separate scale per output row** (called *per-channel* quantisation): an outlier in one row only hurts that row.

```python run
w_out = w.copy()
w_out[0, 0] = 5.0                                           # one wild weight, 25x larger than typical

def quant_rows(v, bits=8):
    """Symmetric quantisation with one scale per output row (per-channel)."""
    qmax = 2 ** (bits - 1) - 1
    scale = np.abs(v).max(axis=1, keepdims=True) / qmax
    q = np.clip(np.round(v / scale), -qmax, qmax).astype(np.int8)
    return q, scale

qt, st = quant_symmetric(w_out)
qr, sr = quant_rows(w_out)
print("per-tensor, no outlier  mean error: %.6f" % np.abs(w - quant_symmetric(w)[0] * quant_symmetric(w)[1]).mean())
print("per-tensor, one outlier mean error: %.6f   (scale grew from %.5f to %.5f)" % (np.abs(w_out - qt * st).mean(), scale, st))
print("per-row,    one outlier mean error: %.6f" % np.abs(w_out - qr * sr).mean())
print("cost of per-row: %d extra float32 scales = %d bytes" % (sr.size, sr.nbytes))
```
```text
per-tensor, no outlier  mean error: 0.000477
per-tensor, one outlier mean error: 0.010138   (scale grew from 0.00191 to 0.03937)
per-row,    one outlier mean error: 0.000205
cost of per-row: 1024 extra float32 scales = 4096 bytes
```

One outlier makes the per-tensor error about 20 times worse; per-row quantisation contains the damage (its error is even lower than the clean per-tensor one, because every row gets a scale that fits it) for the price of 4 KB. This is why real tools default to per-channel for weights.

### 3.3 How many bits can the whole model afford?

Quantise **every** Linear layer of the model and measure the test accuracy. We keep the computation in float32 and only round the weights (this is **fake quantisation**: the right accuracy, none of the speed). It answers the question "does the rounding hurt?" independently of any speed-up.

```python run
def fake_quantise(model, bits, per_row=False):
    """Copy of the model with every Linear weight rounded to `bits` bits (kept as float32)."""
    out = copy.deepcopy(model)
    with torch.no_grad():
        for layer in out:
            if isinstance(layer, nn.Linear):
                wn = layer.weight.detach().numpy()
                if per_row:
                    qn, sc = quant_rows(wn, bits)
                else:
                    qn, sc = quant_symmetric(wn, bits)
                layer.weight.copy_(torch.from_numpy(qn.astype(np.float32) * sc))
    return out.eval()

print(f"float32 reference accuracy: {accuracy(torch_predict(base)):.4f}\n")
print(f"{'bits':>5} {'levels':>7} {'per-tensor':>11} {'per-row':>9}")
for bits in (8, 6, 4, 3, 2):
    a1 = accuracy(torch_predict(fake_quantise(base, bits)))
    a2 = accuracy(torch_predict(fake_quantise(base, bits, per_row=True)))
    print(f"{bits:>5} {2**bits-1:>7} {a1:>11.4f} {a2:>9.4f}")
```
```text
float32 reference accuracy: 0.9796

 bits  levels  per-tensor   per-row
    8     255      0.9796    0.9796
    6      63      0.9778    0.9796
    4      15      0.9778    0.9833
    3       7      0.9704    0.9852
    2       3      0.1000    0.5426
```

Three things stand out. First, **8 bits and even 4 bits cost essentially nothing** on this task: the model is over-sized and the problem easy, so it has lots of slack. Second, there is a **cliff**: below some bit width accuracy collapses (at 2 bits there are only 3 levels, -1, 0, +1). The cliff, not the gentle slope before it, is what to fear. Third, **do not read meaning into differences of 0.002**: the test set has 540 images, so one image is 0.0019 of accuracy. The per-row 3-bit model scoring *above* the float32 reference is luck on a few images, not a miracle. Per-row scales also move the cliff: at 2 bits per-row keeps about half the accuracy while per-tensor falls to chance (0.1 is guessing among ten classes). And the position of the cliff depends on the model and the task: bigger language models survive 4 bits well; a small, tight vision model may break at 6. **Always measure on your own model.**

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot test accuracy (y axis, 0 to 1) against weight bit width (x axis: 8, 6, 4, 3, 2) for a neural network. The curve is flat near 0.98 for 8, 6 and 4 bits, drops a little at 3 bits, and falls off a cliff to 0.1 at 2 bits. Add a second plot below it: a histogram of weights with the quantisation grid lines drawn on top for 8 bits (hundreds of fine lines) and for 2 bits (three coarse lines), so the reader sees why 2 bits destroys the information."

### 3.4 Quantisation-aware training: rounding inside the training loop

The collapse at 2 bits came from rounding a model that had **never seen rounding**. **Quantisation-aware training (QAT)** repairs this: during fine-tuning the forward pass uses the rounded weights, so the network learns to work *with* the rounding. The backward pass pretends the rounding was the identity (the **straight-through estimator**, because `round` has zero gradient almost everywhere and would block learning). The weights we keep and update stay in float32; only the forward pass sees them rounded.

```python run
class RoundSTE(torch.autograd.Function):
    """round() in the forward pass, identity in the backward pass."""
    @staticmethod
    def forward(ctx, x):
        return torch.round(x)
    @staticmethod
    def backward(ctx, grad_out):
        return grad_out

def fake_quant_weight(weight, bits):
    qmax = 2 ** (bits - 1) - 1
    scale = weight.detach().abs().amax(dim=1, keepdim=True) / qmax          # per-row scale
    return torch.clamp(RoundSTE.apply(weight / scale), -qmax, qmax) * scale

class QATLinear(nn.Module):
    def __init__(self, linear, bits):
        super().__init__()
        self.linear, self.bits = linear, bits
    def forward(self, x):
        return F.linear(x, fake_quant_weight(self.linear.weight, self.bits), self.linear.bias)

def qat_finetune(model, bits, epochs=5, lr=3e-4, seed=1):
    wrapped = nn.Sequential(*[QATLinear(copy.deepcopy(l), bits) if isinstance(l, nn.Linear) else copy.deepcopy(l) for l in model])
    opt = torch.optim.Adam(wrapped.parameters(), lr)
    xt, yt = torch.from_numpy(Xtr), torch.from_numpy(ytr)
    torch.manual_seed(seed)
    for epoch in range(epochs):
        perm = torch.randperm(len(xt))
        for i in range(0, len(xt), 64):
            idx = perm[i:i + 64]
            opt.zero_grad()
            F.cross_entropy(wrapped(xt[idx]), yt[idx]).backward()
            opt.step()
    wrapped.eval()
    return wrapped

print(f"{'bits':>5} {'round after training':>21} {'QAT (5 epochs)':>16}")
for bits in (4, 3, 2):
    after = accuracy(torch_predict(fake_quantise(base, bits, per_row=True)))
    qat = qat_finetune(base, bits)
    print(f"{bits:>5} {after:>21.4f} {accuracy(torch_predict(qat)):>16.4f}")
```
```text
 bits  round after training   QAT (5 epochs)
    4                0.9833           0.9778
    3                0.9852           0.9778
    2                0.5426           0.9796
```

At 2 bits the model that was badly damaged by rounding after the fact recovers to its original accuracy after only five epochs of QAT. At 4 and 3 bits both columns are within the 0.002 noise of one test image, so there was nothing to repair. The lesson: **post-training quantisation (PTQ)** is free and works at 8 bits and usually 4-6; **QAT** costs a short training run and rescues the extreme cases. Real frameworks (`torch.ao.quantization`, TensorFlow's model optimisation toolkit) do the same thing with more bookkeeping, and also quantise the activations.

### 3.5 Activations: dynamic or static?

Weights are known when you quantise them. **Activations** (the numbers flowing between layers) depend on the input, so their range is not known in advance. Two strategies:

- **Dynamic quantisation**: at run time, look at the actual activations of this batch, compute the scale, quantise, multiply in int8, convert back. No calibration data needed. A bit of extra work per call. This is the easy option and common for Linear and recurrent layers.
- **Static quantisation**: before deployment, run a **calibration set** (a few hundred typical inputs) through the model, record the typical range of each activation, and **fix** the scales. Faster at run time (no scale computing), but the calibration data must look like real traffic.

To see why calibration matters, look at how much the range of one layer's activations changes from batch to batch:

```python run
acts = {}
hooks = [base[i].register_forward_hook(lambda mod, inp, out, name=n: acts.__setitem__(name, out.detach()))
         for i, n in ((1, "after ReLU 1"), (3, "after ReLU 2"))]
with torch.inference_mode():
    maxima = {"after ReLU 1": [], "after ReLU 2": []}
    for start in range(0, 256, 8):                          # 32 mini-batches of 8 samples
        base(torch.from_numpy(Xte[start:start + 8]))
        for name_i in maxima:
            maxima[name_i].append(float(acts[name_i].max()))
    base(torch.from_numpy(Xtr[:200]))                       # a "calibration set" of 200 inputs
    calib = {k: float(v.max()) for k, v in acts.items()}
for h in hooks:
    h.remove()
for k, vals in maxima.items():
    print(f"{k}: per-batch max ranges from {min(vals):.2f} to {max(vals):.2f}; calibration-set max = {calib[k]:.2f}")
```
```text
after ReLU 1: per-batch max ranges from 1.17 to 1.51; calibration-set max = 1.46
after ReLU 2: per-batch max ranges from 3.31 to 5.35; calibration-set max = 5.35
```

The per-batch maximum jumps around. A static scale picked from calibration data must cover the typical maximum, and if real traffic later produces larger values the numbers **clip** (saturate at the top of the range), which silently hurts accuracy. So: choose a calibration set that reflects production, and re-check accuracy on real data afterwards. We run a true static quantisation with ONNX Runtime in section 5.

### 3.6 Real tools: PyTorch dynamic quantisation and half precision

PyTorch ships dynamic int8 quantisation for Linear layers in one call. We measure it with the harness from section 2, next to float16 and bfloat16 (half-precision formats: 16 bits per number, a cheap 2x).

```python run
from torch.ao.quantization import quantize_dynamic

q_dyn = quantize_dynamic(base, {nn.Linear}, dtype=torch.qint8)
print(q_dyn[2])

def half_predict(model, dtype):
    m = copy.deepcopy(model).to(dtype)
    def predict(Xn):
        with torch.inference_mode():
            return m(torch.from_numpy(Xn).to(dtype)).float().numpy()
    return predict, m

p16, m16 = half_predict(base, torch.float16)
pbf, mbf = half_predict(base, torch.bfloat16)
size16 = sum(p.numel() * p.element_size() for p in m16.parameters())

rows = [profile("float32 baseline", torch_predict(base), state_bytes(base)),
        profile("torch int8 dynamic", torch_predict(q_dyn), state_bytes(q_dyn)),
        profile("float16", p16, size16),
        profile("bfloat16", pbf, size16)]
show(rows, "float32 baseline")
```
```text
DynamicQuantizedLinear(in_features=1024, out_features=1024, dtype=torch.qint8, qscheme=torch.per_tensor_affine)
model                     size KB     acc   p50 ms   p95 ms  samples/s  size x  speed x   d acc
float32 baseline             4403  0.9796    0.663    7.952      16176    1.00     1.00 +0.0000
torch int8 dynamic           1111  0.9796    0.694    3.214      19875    3.96     0.96 +0.0000
float16                      2200  0.9796    0.797    5.865       4509    2.00     0.83 +0.0000
bfloat16                     2200  0.9796    0.327    0.434       5122    2.00     2.03 +0.0000
```

How to read this table:

- **Size** follows the arithmetic: int8 about 4x, half precision about 2x.
- **Accuracy** barely moves, as the fake-quantisation experiment predicted.
- **Speed** is the surprise for newcomers: the gain is *much smaller than the size gain*, and can even be negative. Look at the `samples/s` column for the two half-precision rows: at batch 64 they are several times *slower* than float32 on this CPU, and their p95 is worse. This CPU has no fast half-precision arithmetic, so it converts on the fly. Speed depends on whether the **hardware has fast integer or half-precision instructions** (many CPUs have int8 dot-product instructions; few have fast float16 arithmetic, so a CPU may convert back to float32 internally). Size is guaranteed by arithmetic; **speed is a property of the machine**. Quantise for size with confidence; promise speed only after measuring on the target device.

### 3.7 Try it

1. Why is the rounding error at most `scale / 2` and not `scale`?
2. A weight tensor has values from -0.2 to 0.2 except one value, 3.0. You quantise per-tensor to int8. Roughly how many of the 255 levels are used by the ordinary weights, and what does that say about the outlier?
3. Dynamic quantisation needs no calibration data and static quantisation does. Name one risk of the static choice and one benefit.
4. Your int8 model is 3.9x smaller but only 1.1x faster. Is something broken?

<details><summary>Answer</summary>

1. Rounding moves a value to the nearest grid point. Grid points are `scale` apart, so the nearest one is never farther than half a step.
2. The scale is 3.0 / 127 = about 0.0236. The ordinary values span -0.2 to 0.2, which is about 0.4 / 0.0236 = **17 levels** out of 255. They are squeezed into 17 levels, so they are coarse. This is the outlier problem: use per-channel scales, clip or handle the outlier separately, or keep that layer in float.
3. Risk: if production inputs have larger activations than the calibration set, values clip and accuracy falls silently. Benefit: scales are fixed ahead of time, so no scale computation at run time, which is faster and gives a simpler deployed graph.
4. Probably not. Size is arithmetic; speed depends on hardware support and on whether the layer was memory-bound. Check the batch size (larger batches are compute-bound and gain differently), the thread count, and whether the runtime has a fast int8 path for your CPU. Measure on the target device.

</details>

## 4. Pruning, and why smaller architectures beat both

### 4.1 Pruning: remove what does not matter

Many weights in a trained network are close to zero and contribute little. **Pruning** sets them to exactly zero, or removes them. Two kinds:

- **Unstructured pruning**: zero individual weights anywhere (the ones with the smallest absolute value: **magnitude pruning**). Can reach very high sparsity, but the matrix keeps its shape. A normal dense matrix multiply still does every multiplication, including those by zero.
- **Structured pruning**: remove whole **neurons, channels or heads**, so the matrices really get smaller. Less flexible, but a smaller dense model is genuinely faster everywhere.

Let us prune by hand. Keep the largest weights in each layer, zero the rest, and measure accuracy **without any retraining first**.

```python run
def prune_magnitude(model, fraction):
    """Copy of the model with the smallest `fraction` of weights (by absolute value) set to zero, per layer."""
    out = copy.deepcopy(model)
    with torch.no_grad():
        for layer in out:
            if isinstance(layer, nn.Linear):
                k = int(layer.weight.numel() * fraction)
                if k:
                    threshold = layer.weight.abs().flatten().kthvalue(k).values
                    layer.weight[layer.weight.abs() <= threshold] = 0.0
    return out.eval()

def sparsity(model):
    zeros = sum((l.weight == 0).sum().item() for l in model if isinstance(l, nn.Linear))
    total = sum(l.weight.numel() for l in model if isinstance(l, nn.Linear))
    return zeros / total

print(f"dense reference accuracy: {accuracy(torch_predict(base)):.4f}\n")
print(f"{'prune':>6} {'sparsity':>9} {'accuracy, no retraining':>25}")
for frac in (0.5, 0.8, 0.9, 0.95, 0.98):
    p = prune_magnitude(base, frac)
    print(f"{frac:>6.2f} {sparsity(p):>9.3f} {accuracy(torch_predict(p)):>25.4f}")
```
```text
dense reference accuracy: 0.9796

 prune  sparsity   accuracy, no retraining
  0.50     0.500                    0.9759
  0.80     0.800                    0.8963
  0.90     0.900                    0.6222
  0.95     0.950                    0.1556
  0.98     0.980                    0.1000
```

Half the weights can go for free. Past about 80 % the accuracy falls quickly: **one-shot pruning has a cliff just like low-bit quantisation**.

### 4.2 Fine-tune after pruning

Pruning damages the network, but the surviving weights can **compensate** if they are allowed to keep learning. The recipe: prune, then train a few more epochs while **keeping the pruned weights at zero** (re-apply the mask after every optimiser step).

```python run
def prune_and_finetune(model, fraction, epochs=5, lr=3e-4, seed=1):
    pruned = prune_magnitude(model, fraction)
    masks = {i: (l.weight != 0).float() for i, l in enumerate(pruned) if isinstance(l, nn.Linear)}
    opt = torch.optim.Adam(pruned.parameters(), lr)
    xt, yt = torch.from_numpy(Xtr), torch.from_numpy(ytr)
    torch.manual_seed(seed)
    for epoch in range(epochs):
        perm = torch.randperm(len(xt))
        for i in range(0, len(xt), 64):
            idx = perm[i:i + 64]
            opt.zero_grad()
            F.cross_entropy(pruned(xt[idx]), yt[idx]).backward()
            opt.step()
            with torch.no_grad():
                for j, mask in masks.items():
                    pruned[j].weight.mul_(mask)             # keep pruned weights at zero
    return pruned.eval()

print(f"{'prune':>6} {'before fine-tune':>17} {'after fine-tune':>16}")
pruned_models = {}
for frac in (0.9, 0.95):
    before = accuracy(torch_predict(prune_magnitude(base, frac)))
    pruned_models[frac] = prune_and_finetune(base, frac)
    print(f"{frac:>6.2f} {before:>17.4f} {accuracy(torch_predict(pruned_models[frac])):>16.4f}")
```
```text
 prune  before fine-tune  after fine-tune
  0.90            0.6222           0.9704
  0.95            0.1556           0.9389
```

Five epochs of fine-tuning bring 90 % pruning back to near-original accuracy. Beyond that the network simply runs out of weights. The standard practice for aggressive pruning is **gradual** pruning: raise the sparsity in several small steps with fine-tuning between them, which survives higher sparsity than one big cut. We stop here; the shape of the lesson is clear.

PyTorch also has a built-in tool, `torch.nn.utils.prune`. It does not delete anything: it keeps the original weights in `weight_orig`, adds a `weight_mask` buffer, and computes `weight = weight_orig * weight_mask` on every forward pass. Call `prune.remove` to make the zeros permanent.

```python run
import torch.nn.utils.prune as prune
layer = copy.deepcopy(base[2])
prune.l1_unstructured(layer, name="weight", amount=0.9)
print("while pruned  : parameters", [n for n, _ in layer.named_parameters()], "| buffers", [n for n, _ in layer.named_buffers()])
prune.remove(layer, "weight")
print("after remove  : parameters", [n for n, _ in layer.named_parameters()], "| zeros: %.3f" % (layer.weight == 0).float().mean().item())
```
```text
while pruned  : parameters ['bias', 'weight_orig'] | buffers ['weight_mask']
after remove  : parameters ['bias', 'weight'] | zeros: 0.900
```

### 4.3 The catch: zeros do not make files smaller or matrices faster

You pruned 90 % of the weights. Did the model get smaller or faster? Measure.

```python run
p90 = pruned_models[0.9]
raw = lambda m: (lambda b: (torch.save(m.state_dict(), b), b.getvalue())[1])(io.BytesIO())
print(f"saved file size : dense {len(raw(base))/1024:.0f} KB | 90% pruned {len(raw(p90))/1024:.0f} KB   <- identical: zeros are stored as zeros")
print(f"after zlib      : dense {len(zlib.compress(raw(base), 9))/1024:.0f} KB | 90% pruned {len(zlib.compress(raw(p90), 9))/1024:.0f} KB   <- a compressor can find the zeros")
d = bench(torch_predict(base), Xte[:64], repeat=100)
s = bench(torch_predict(p90), Xte[:64], repeat=100)
print(f"latency batch 64: dense {d['p50']:.3f} ms | 90% pruned {s['p50']:.3f} ms   <- same multiplications, only noise apart")
```
```text
saved file size : dense 4403 KB | 90% pruned 4403 KB   <- identical: zeros are stored as zeros
after zlib      : dense 4081 KB | 90% pruned 688 KB   <- a compressor can find the zeros
latency batch 64: dense 3.475 ms | 90% pruned 3.194 ms   <- same multiplications, only noise apart
```

The latency difference is within the run-to-run noise measured in section 2.3: a dense multiply does every multiplication, including those by zero. This is the most common disappointment with pruning. **Unstructured sparsity shrinks a model only if the storage format and the runtime exploit it**: a compressed or sparse file format for size, a sparse matrix kernel (or special hardware) for speed. Without those, you get the accuracy loss and none of the gain. On ordinary CPUs and GPUs, unstructured pruning at 50 to 90 % rarely speeds up dense kernels.

### 4.4 Structured pruning, and the simplest idea of all

**Structured** pruning removes whole hidden neurons, so every matrix gets smaller and the speed-up is real. Rank the first hidden layer's neurons by the size of their incoming weights and keep the strongest. Removing neuron `j` of layer 1 means: drop row `j` of layer 1's weight, and drop column `j` of layer 2's weight.

```python run
def prune_neurons(model, keep):
    """Keep the `keep` hidden units of layer 1 with the largest incoming weight norm; shrink both affected matrices."""
    l0, l2, l4 = model[0], model[2], model[4]
    idx = l0.weight.norm(dim=1).argsort(descending=True)[:keep].sort().values
    new = nn.Sequential(nn.Linear(64, keep), nn.ReLU(), nn.Linear(keep, l2.out_features), nn.ReLU(), nn.Linear(l2.out_features, 10))
    with torch.no_grad():
        new[0].weight.copy_(l0.weight[idx]);   new[0].bias.copy_(l0.bias[idx])
        new[2].weight.copy_(l2.weight[:, idx]); new[2].bias.copy_(l2.bias)
        new[4].load_state_dict(l4.state_dict())
    return new.eval()

print(f"{'hidden-1 units':>15} {'params':>10} {'accuracy':>9} {'b64 p50 ms':>11}")
for keep in (1024, 512, 256, 128, 64):
    m = prune_neurons(base, keep)
    print(f"{keep:>15} {count_params(m):>10,} {accuracy(torch_predict(m)):>9.4f} {bench(torch_predict(m), Xte[:64], repeat=100)['p50']:>11.3f}")
```
```text
 hidden-1 units     params  accuracy  b64 p50 ms
           1024  1,126,410    0.9796       3.892
            512    568,842    0.9685       1.926
            256    290,058    0.9611       1.166
            128    150,666    0.9167       0.757
             64     80,970    0.6852       0.579
```

Parameters, file size and latency all fall in step, with no special runtime. Accuracy holds down to about 256 units (a 4x cut in parameters costs about 2 points) and then collapses at 64 (no retraining here; fine-tuning would recover some more).

Now the question this experiment raises: **if we can throw away 90 % of this network, why did we build it so big?** The simplest "optimisation" is to train a smaller architecture from the start:

```python run
t0 = time.perf_counter()
small = train_mlp(hidden=32, epochs=60)                         # 32 hidden units instead of 1024
print(f"trained in {time.perf_counter() - t0:.1f} s")
rows = [profile("big (1024 hidden)", torch_predict(base), state_bytes(base)),
        profile("small (32 hidden)", torch_predict(small), state_bytes(small))]
show(rows, "big (1024 hidden)")
print("parameters: big %s, small %s" % (f"{count_params(base):,}", f"{count_params(small):,}"))
```
```text
trained in 5.0 s
model                     size KB     acc   p50 ms   p95 ms  samples/s  size x  speed x   d acc
big (1024 hidden)            4403  0.9796    0.631    0.881      16921    1.00     1.00 +0.0000
small (32 hidden)              16  0.9611    0.216    0.246     233312  272.69     2.92 -0.0185
parameters: big 1,126,410, small 3,466
```

For this easy task, a model with over 300 times fewer parameters is within two points of the baseline and several times faster, with no quantisation, no pruning and no special runtime. **Rule 2: before compressing, ask whether the model was too big.** Optimisation tricks shine for models whose size the task really needs, such as modern image and language models, where the "small model" does lose real accuracy and compression is the only route.

### 4.5 Distillation: a student learns from a teacher

A third route to a small model is **knowledge distillation**: train a small **student** to imitate a big **teacher**. The student learns from the teacher's full probability vector (for example "70 % seven, 25 % one, 5 % nine"), which carries more information per example than the hard label "seven". The loss mixes both:

```
loss = alpha x KL( student(x)/T  ||  teacher(x)/T ) x T²   +   (1 - alpha) x cross_entropy(student(x), label)
```

`T` (temperature) softens both distributions so the small probabilities become visible; the `T²` factor keeps the gradient size comparable.

**Question.** On the digits task, a one-hidden-layer student with 16 units was trained plainly and with distillation from the 1024-unit teacher, five seeds each. Predict: does distillation help?

<details><summary>Answer</summary>

Not here. Measured in an earlier test run (T = 3, alpha = 0.7, 60 epochs, five seeds): the plain 16-unit student averaged about 0.974 test accuracy and the distilled one about 0.969, a small difference in the *wrong* direction and inside the seed-to-seed spread. The reason is that this task is easy and the labels are already clean, so the teacher has little extra to teach. Distillation pays when the task is hard (many classes that resemble each other, noisy labels) and the teacher is much stronger than any student trained directly. It is a tool, not a guaranteed win: **measure it against the plain student with several seeds.**

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 1024x1024 weight matrix as a grid of cells coloured by absolute value. Show three copies side by side: (a) unstructured pruning, 90% of cells randomly scattered blank, matrix still the same size; (b) structured pruning, a few whole rows and the matching columns of the next matrix removed so both matrices physically shrink; (c) the result as a smaller matrix multiply. Under each, write what happens to file size and to latency."

### 4.6 Try it

1. A colleague says "we pruned 80 % of the weights, so the model is 5x faster". What three questions do you ask?
2. Why must the mask be re-applied after every optimiser step during fine-tuning?
3. In structured pruning of hidden layer 1, why must you also change layer 2's weight matrix?
4. Your model has 500,000 parameters and is overfitting heavily. Is it a good pruning candidate, or a good candidate for a smaller architecture?

<details><summary>Answer</summary>

1. Did the **file size** change (what format)? Did the **latency** change on the target hardware, and with which runtime (does it use sparse kernels)? What happened to **accuracy**, measured on held-out data after fine-tuning? Sparsity is not speed.
2. The optimiser's update (Adam especially) changes every weight, including the zeros: a zeroed weight would become non-zero again and the sparsity would be lost. Multiplying by the mask puts them back to zero.
3. Removing a neuron from layer 1 removes one *output* of layer 1, which is one *input* of layer 2. Layer 2's weight matrix has one column per input, so that column must go too; otherwise the shapes do not match.
4. A smaller architecture (and probably regularisation, more data or early stopping). Overfitting means the model has more capacity than the data supports, so shrinking it loses little and often helps.

</details>

## 5. ONNX: export, verify, run, optimise

### 5.1 Why leave the training framework

PyTorch is made for **training**: it records operations as you run Python, supports debugging, and is large. For **serving**, you want something else: a **frozen graph** (the exact list of operations with fixed weights), a **small, fast runtime** with no Python model code, and the freedom to run on a server, a phone, a browser or a board.

**ONNX** (Open Neural Network Exchange) is a file format for exactly that: a graph of standard operations (`Gemm`, `Relu`, `Conv`, ...) with the weights stored inside, plus a list of **opsets** (versions of the operation definitions). **ONNX Runtime (ORT)** is a runtime that loads the file and executes it, after rewriting the graph to run faster.

```
 PyTorch model  --export-->  model.onnx  --load-->  ONNX Runtime  -->  predictions
 (Python code)              (graph + weights)       (fast, small, no PyTorch needed)
```

Benefits: a lighter deployment (the `onnxruntime` package is a fraction of the size of `torch`), graph optimisations, one file for many target languages (C++, Java, C#, JavaScript), and hardware back-ends ("execution providers") for CPU, GPU and accelerators. Costs: not every PyTorch operation exports; dynamic Python control flow needs care; and you add a **second implementation** of your model that you must verify (5.4).

### 5.2 Export, and the file-size trap

`torch.onnx.export` traces the model with an example input and writes the graph. Two arguments deserve care: `input_names` and `output_names` (the names callers use), and `dynamic_axes` (which dimensions may vary; without it the batch size is frozen to the example's, see 5.5).

The exporter in current PyTorch may store big weights in a **separate data file** next to the `.onnx` file. If you copy only the `.onnx` file, the model is broken. Look at what a default export creates:

```python run
@contextlib.contextmanager
def quiet():
    """Hide the progress chatter that the exporter and quantisation tools print."""
    with open(os.devnull, "w", encoding="utf-8") as dn, contextlib.redirect_stdout(dn), contextlib.redirect_stderr(dn):
        yield

def export_onnx(model, path, example, external_data=False, dynamic_batch=True):
    kwargs = {"dynamic_axes": {"x": {0: "batch"}, "logits": {0: "batch"}}} if dynamic_batch else {}
    with quiet():
        torch.onnx.export(model, (torch.from_numpy(example),), str(path),
                          input_names=["x"], output_names=["logits"], external_data=external_data, **kwargs)
    return path

def ls(folder):
    for f in sorted(pathlib.Path(folder).iterdir()):
        print(f"  {f.name:<22}{f.stat().st_size:>10,} bytes")

(ws / "export_default").mkdir()
export_onnx(base, ws / "export_default" / "mlp.onnx", Xte[:1], external_data=True)
print("external_data=True  (weights in a side file):")
ls(ws / "export_default")

(ws / "export_single").mkdir()
export_onnx(base, ws / "export_single" / "mlp.onnx", Xte[:1], external_data=False)
print("external_data=False (one self-contained file):")
ls(ws / "export_single")
```
```text
external_data=True  (weights in a side file):
  mlp.onnx                   7,376 bytes
  mlp.onnx.data          4,505,600 bytes
external_data=False (one self-contained file):
  mlp.onnx               4,512,688 bytes
```

With the side file, the `.onnx` is only a few KB: a *size report that looks at the wrong file would say 7 KB instead of 4.4 MB*. Always list the whole folder. We use the single-file form, which is easier to ship and to measure. (For models above 2 GB, ONNX's file format forces the side-file form.)

### 5.3 Look inside the file

An ONNX file is a protobuf message you can open and read with the `onnx` package. Verify what you shipped before you trust it:

```python run
onnx_path = ws / "export_single" / "mlp.onnx"
model_proto = onnx.load(str(onnx_path))
onnx.checker.check_model(model_proto)                       # raises if the file is malformed
def dims(t):
    return [d.dim_param or d.dim_value for d in t.type.tensor_type.shape.dim]
print("opset version :", model_proto.opset_import[0].version)
print("inputs        :", [(i.name, dims(i)) for i in model_proto.graph.input])
print("outputs       :", [(o.name, dims(o)) for o in model_proto.graph.output])
print("operations    :", [n.op_type for n in model_proto.graph.node])
print("weights stored:")
for init in model_proto.graph.initializer:
    print(f"  {init.name:<10} shape {list(init.dims)}")
```
```text
opset version : 20
inputs        : [('x', ['batch', 64])]
outputs       : [('logits', ['batch', 10])]
operations    : ['Gemm', 'Relu', 'Gemm', 'Relu', 'Gemm']
weights stored:
  0.weight   shape [1024, 64]
  0.bias     shape [1024]
  2.weight   shape [1024, 1024]
  2.bias     shape [1024]
  4.weight   shape [10, 1024]
  4.bias     shape [10]
```

Read it like a recipe: input `x` with a **named, variable** first dimension `batch` and 64 features; five operations (`Gemm` is a general matrix multiply plus bias, so one `Gemm` is one `nn.Linear`); six weight tensors. Nothing else: no Python, no class names, no optimiser. That small, readable graph is also why exported models are easy to optimise automatically.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the ONNX graph of a three-layer network as a vertical flowchart: an input box 'x [batch, 64]', then boxes Gemm (weights 1024x64) -> Relu -> Gemm (1024x1024) -> Relu -> Gemm (10x1024), then an output box 'logits [batch, 10]'. Show the weight tensors as small side boxes feeding each Gemm. Next to it draw the same network as PyTorch Python source code, to show that the graph keeps only the operations and weights."

### 5.4 Verify: the exported model must give the same answers

Never assume an export is faithful. Run both models on the same inputs and compare **numbers**, not just accuracy. Small float differences (1e-6) are normal, because the runtime orders the arithmetic differently. A large difference means a bug.

```python run
def onnx_predict(path, threads=None, opt_level=None):
    """Load an ONNX file in ONNX Runtime; return (predict function, session)."""
    so = ort.SessionOptions()
    if threads is not None:
        so.intra_op_num_threads = threads
    if opt_level is not None:
        so.graph_optimization_level = opt_level
    sess = ort.InferenceSession(str(path), so, providers=["CPUExecutionProvider"])
    return (lambda Xn: sess.run(None, {"x": Xn})[0]), sess

ort_fp32, sess = onnx_predict(onnx_path)
ref = torch_predict(base)(Xte)
got = ort_fp32(Xte)
print("max |torch - onnx| over all logits :", float(np.abs(ref - got).max()))
print("same predicted class on all inputs :", bool((ref.argmax(1) == got.argmax(1)).all()))
print("test accuracy, ONNX Runtime        :", accuracy(ort_fp32))
```
```text
max |torch - onnx| over all logits : 3.814697265625e-06
same predicted class on all inputs : True
test accuracy, ONNX Runtime        : 0.9796296296296296
```

The difference is around one millionth: floating-point reordering only. Turn this into a habit: **a parity check (max difference and same predicted class) after every export, quantisation or conversion**. In CI it is a one-line test (section 9).

### 5.5 The fixed-batch trap

If you export without `dynamic_axes`, the batch dimension is baked in as the example's size, and the model refuses any other.

```python run
(ws / "export_fixed").mkdir()
export_onnx(base, ws / "export_fixed" / "mlp.onnx", Xte[:1], dynamic_batch=False)
fixed, _ = onnx_predict(ws / "export_fixed" / "mlp.onnx")
print("batch of 1 :", fixed(Xte[:1]).shape)
try:
    fixed(Xte[:5])
except Exception as e:
    print("batch of 5 : ERROR ->", str(e).replace("\n", " ")[:150])
```
```text
batch of 1 : (1, 10)
batch of 5 : ERROR -> [ONNXRuntimeError] : 2 : INVALID_ARGUMENT : Got invalid dimensions for input: x for the following indices  index: 0 Got: 5 Expected: 1  Please fix eit
```

The message names the cause (`Expected: 1`), but it is easy to miss when the failure appears in production under real traffic. Rule: **test the exported model with a batch size different from the one you exported with**.

### 5.6 ONNX Runtime against PyTorch, and a fair instrument

Now the speed question. Both run the same maths on the same CPU. First the obvious way: interleave the candidates inside this Python process, as section 2.3 taught, using the `profile` row from section 2.5.

```python run
size_of_file = lambda p: pathlib.Path(p).stat().st_size
rows = [profile("torch float32", torch_predict(base), state_bytes(base)),
        profile("onnxruntime float32", ort_fp32, size_of_file(onnx_path)),
        profile("torch float32 (again)", torch_predict(base), state_bytes(base)),
        profile("onnxruntime float32 (again)", ort_fp32, size_of_file(onnx_path))]
show(rows, "torch float32")
```
```text
model                     size KB     acc   p50 ms   p95 ms  samples/s  size x  speed x   d acc
torch float32                4403  0.9796    0.338   14.953      20509    1.00     1.00 +0.0000
onnxruntime float32          4407  0.9796    0.206    0.778      34128    1.00     1.64 +0.0000
torch float32 (again)        4403  0.9796    0.752   27.875      15042    1.00     0.45 +0.0000
onnxruntime float32 (again)     4407  0.9796    0.263    3.278      32296    1.00     1.29 +0.0000
```

Look at the two `torch float32` rows: the same code, the same model, and yet the second measurement is far slower than the first, and the p95 values are enormous for a model that needs a fraction of a millisecond. Something in this process changed between the measurements. The likely cause: **PyTorch and ONNX Runtime each keep a pool of worker threads**, and two pools in one process compete for the same cores. (I did not trace the exact mechanism; what matters is that the numbers cannot be trusted.) This is a typical benchmark trap: **the act of measuring in a busy, long-lived process changes the result.**

The cure is a **fresh process per measurement**. A small probe script loads one model, warms up, times several batch sizes, and prints a JSON line. The parent only starts it and reads the answer. Nothing else is running inside the measured process, and every candidate gets the same treatment, PyTorch included.

```python run
probe_src = r'''
import sys, json, time
import numpy as np
def rss_mb():
    try:
        import psutil
        return psutil.Process().memory_info().rss / 2**20
    except ImportError:                                           # fall back to the peak, in KB on Linux
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
path, threads = sys.argv[1], int(sys.argv[2])
batches = [int(b) for b in sys.argv[3].split(",")]
repeat = int(sys.argv[4])
if path == "none":                                                # the runtime alone, no model
    import onnxruntime
    print(json.dumps({"load_ms": 0, "first_ms": 0, "p50": {}, "p95": {}, "rss_mb": round(rss_mb(), 1)}))
    sys.exit()
t0 = time.perf_counter()
if path.endswith(".pt"):                                          # a PyTorch state dict: rebuild the MLP and load it
    import torch, torch.nn as nn
    torch.set_num_threads(threads)
    state = torch.load(path)
    h = state["0.weight"].shape[0]
    net = nn.Sequential(nn.Linear(64, h), nn.ReLU(), nn.Linear(h, h), nn.ReLU(), nn.Linear(h, 10))
    net.load_state_dict(state); net.eval()
    def run(x):
        with torch.inference_mode():
            net(torch.from_numpy(x))
else:                                                             # an ONNX file
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = threads
    sess = ort.InferenceSession(path, so, providers=["CPUExecutionProvider"])
    run = lambda x: sess.run(None, {"x": x})
load_ms = (time.perf_counter() - t0) * 1e3
data = np.random.default_rng(0).random((max(batches), 64), dtype=np.float32)
t0 = time.perf_counter(); run(data[:batches[0]]); first_ms = (time.perf_counter() - t0) * 1e3
p50, p95 = {}, {}
for b in batches:
    x = data[:b]
    for _ in range(50):
        run(x)                                                    # warm-up
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter(); run(x); times.append((time.perf_counter() - t0) * 1e3)
    times.sort()
    p50[b], p95[b] = round(times[len(times) // 2], 4), round(times[int(len(times) * 0.95)], 4)
print(json.dumps({"load_ms": round(load_ms, 1), "first_ms": round(first_ms, 3), "p50": p50, "p95": p95, "rss_mb": round(rss_mb(), 1)}))
'''
(ws / "probe.py").write_text(probe_src, encoding="utf-8")

def probe(path, threads=2, batches=(1,), repeat=100):
    """Measure an ONNX file or a PyTorch .pt state dict in a FRESH Python process. Batch sizes become string keys."""
    out = subprocess.run([sys.executable, "-I", str(ws / "probe.py"), str(path), str(threads),
                          ",".join(map(str, batches)), str(repeat)], capture_output=True, text=True, timeout=300, encoding="utf-8")
    if out.returncode != 0:
        raise RuntimeError(out.stderr[-500:])
    return json.loads(out.stdout.strip().splitlines()[-1])

def profile_file(name, path, predict, threads=2):
    """Like profile(), but latency comes from a fresh process (probe) and accuracy from this process."""
    r = probe(path, threads=threads, batches=(1, 64), repeat=120)
    return {"name": name, "size_kb": size_of_file(path) / 1024, "acc": accuracy(predict),
            "p50_ms": r["p50"]["1"], "p95_ms": r["p95"]["1"], "samples_per_s": 64000 / r["p50"]["64"]}

torch.save(base.state_dict(), ws / "base.pt")
rows = [profile_file("torch float32", ws / "base.pt", torch_predict(base)),
        profile_file("onnxruntime float32", onnx_path, ort_fp32),
        profile_file("torch float32 (again)", ws / "base.pt", torch_predict(base)),
        profile_file("onnxruntime float32 (again)", onnx_path, ort_fp32)]
show(rows, "torch float32")
```
```text
model                     size KB     acc   p50 ms   p95 ms  samples/s  size x  speed x   d acc
torch float32                4403  0.9796    0.293    0.452      20273    1.00     1.00 +0.0000
onnxruntime float32          4407  0.9796    0.380    0.585      26523    1.00     0.77 +0.0000
torch float32 (again)        4403  0.9796    0.500    0.569       8712    1.00     0.59 +0.0000
onnxruntime float32 (again)     4407  0.9796    0.284    0.489      18129    1.00     1.03 +0.0000
```

The enormous p95 tails are gone: the tail was interference, not the models. (All four rows use 2 threads; `-I` runs Python in isolated mode, so no stray local files are imported.) But read the table without wishful thinking. The p50 values of the *same* model still differ by tens of percent from row to row, and at **batch 1 the two runtimes are not clearly different** for this tiny model: the gap is about as large as the noise. The clear difference is in the `samples/s` column at batch 64, where ONNX Runtime does more work per second, because it runs a prepared plan instead of walking Python objects layer by layer. The honest conclusion is a small, measured one: *no proven latency gain at batch 1 here, a throughput gain at batch 64*. On a model with many small layers, where per-call overhead is a larger share, the batch-1 gain is bigger; measure your own.

From here on, **every latency in a comparison table comes from a fresh process**.

### 5.7 What the runtime does to the graph, and thread settings

ORT rewrites the graph before running it ("graph optimisations": removing no-ops, folding constants, **fusing** operations such as Conv+BatchNorm+ReLU into one). It can save the rewritten graph so you can see it:

```python run
so = ort.SessionOptions()
so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
so.optimized_model_filepath = str(ws / "mlp_optimised.onnx")
ort.InferenceSession(str(onnx_path), so, providers=["CPUExecutionProvider"])
opt_proto = onnx.load(str(ws / "mlp_optimised.onnx"))
print("exported graph :", [n.op_type for n in model_proto.graph.node])
print("optimised graph:", [n.op_type for n in opt_proto.graph.node])
```
```text
exported graph : ['Gemm', 'Relu', 'Gemm', 'Relu', 'Gemm']
optimised graph: ['FusedGemm', 'FusedGemm', 'Gemm']
```

Five operations became three: each `Relu` was **fused** into the `Gemm` before it, so the activation is applied while the matrix result is still in the processor's cache instead of being written to memory and read back. On a convolutional network the gain is larger (Conv, BatchNorm and activation become one kernel). The principle is the same: **the runtime knows the whole graph, Python does not**. (ORT may print a warning that the saved optimised file is hardware-specific. That is true: we only saved it to look at it. Ship the original file and let each machine optimise on load.)

**Threads.** `intra_op_num_threads` is how many CPU threads one operation may use. More threads help big matrices, hurt tiny ones (the cost of waking threads exceeds the work), and compete with your own server's threads. Measure on your workload, with the fresh-process `probe`.

```python run
print(f"{'threads':>8} {'batch 1 ms':>11} {'batch 64 ms':>12} {'batch 540 ms':>13}")
for nth in (1, 2, 4, 8):
    r = probe(onnx_path, threads=nth, batches=(1, 64, 540), repeat=60)
    print(f"{nth:>8} {r['p50']['1']:>11.3f} {r['p50']['64']:>12.3f} {r['p50']['540']:>13.3f}")
```
```text
 threads  batch 1 ms  batch 64 ms  batch 540 ms
       1       0.597        4.596        35.950
       2       0.398        2.761        18.891
       4       0.243        2.192        20.388
       8       0.322        2.373        16.694
```

Typical pattern: more threads help big batches until the machine runs out of cores or memory bandwidth, after which extra threads only add overhead; batch 1 barely gains (there is not enough work to share). Here one thread is clearly the slowest and the other settings are close together, with differences inside the noise. In a service that handles many requests at once, **one or two threads per request and several workers** often beats **many threads per request**. Your machine decides; this table is how you find out. We use **2 threads** for the rest of the chapter: it is close to the best here and leaves cores free for the rest of a service.

### 5.8 Quantisation in ONNX Runtime: dynamic and static

ORT has quantisation tools that work on the exported file. **Dynamic** quantisation needs only the file. **Static** quantisation needs a **calibration reader**: an object that hands over some representative inputs, one at a time, so the tool can measure activation ranges (section 3.5).

```python run
from onnxruntime.quantization import quantize_dynamic, quantize_static, CalibrationDataReader, QuantType, QuantFormat

int8_dyn_path = ws / "mlp_int8_dynamic.onnx"
with quiet():
    quantize_dynamic(str(onnx_path), str(int8_dyn_path), weight_type=QuantType.QInt8)

class DigitsCalibration(CalibrationDataReader):
    """Feeds 200 training inputs, one per call, then None to say 'finished'."""
    def __init__(self, data):
        self._it = iter([{"x": data[i:i + 1]} for i in range(len(data))])
    def get_next(self):
        return next(self._it, None)

int8_static_path = ws / "mlp_int8_static.onnx"
with quiet():
    quantize_static(str(onnx_path), str(int8_static_path), DigitsCalibration(Xtr[:200]),
                    quant_format=QuantFormat.QDQ, weight_type=QuantType.QInt8,
                    activation_type=QuantType.QInt8, per_channel=True)

print("dynamic graph:", sorted(set(n.op_type for n in onnx.load(str(int8_dyn_path)).graph.node)))
print("static graph :", sorted(set(n.op_type for n in onnx.load(str(int8_static_path)).graph.node)))

ort_dyn, _ = onnx_predict(int8_dyn_path)
ort_sta, _ = onnx_predict(int8_static_path)

rows = [profile_file("torch float32", ws / "base.pt", torch_predict(base)),
        profile_file("ort float32", onnx_path, ort_fp32),
        profile_file("ort int8 dynamic", int8_dyn_path, ort_dyn),
        profile_file("ort int8 static", int8_static_path, ort_sta)]
show(rows, "torch float32")
```
```text
dynamic graph: ['Add', 'Cast', 'DynamicQuantizeLinear', 'MatMulInteger', 'Mul', 'Relu']
static graph : ['DequantizeLinear', 'Gemm', 'QuantizeLinear']
model                     size KB     acc   p50 ms   p95 ms  samples/s  size x  speed x   d acc
torch float32                4403  0.9796    0.297    0.472       8476    1.00     1.00 +0.0000
ort float32                  4407  0.9796    0.232    0.330      28014    1.00     1.28 +0.0000
ort int8 dynamic             1113  0.9796    0.154    0.619      31888    3.96     1.93 +0.0000
ort int8 static              1140  0.9796    0.163    0.206      48903    3.86     1.83 +0.0000
```

Read the graphs first. The dynamic graph contains `DynamicQuantizeLinear` (scale computed at run time) and `MatMulInteger`; the static graph contains `QuantizeLinear` and `DequantizeLinear` pairs (**QDQ format**: scales fixed in advance, the runtime fuses them into integer kernels). In the table the **size** drops about 4x as promised, accuracy stays within noise, and **latency** shows a real gain over the float32 file on this machine, because ORT has int8 kernels that use the CPU's integer instructions (dynamic and static quantisation differ in how much work happens at run time; which one wins depends on the model and the CPU). This is the same arithmetic as the PyTorch dynamic quantisation in 3.6, with a better runtime under it.

The tool prints a warning suggesting a **pre-processing** step (`quant_pre_process`: shape inference and graph clean-up before quantising). It is advisable on convolutional models; on this tiny MLP it changes nothing. If your run prints that warning, you have not done anything wrong.

### 5.9 The preprocessing contract (ml.06 again)

The model expects an 8x8 image, flattened row by row, with pixel values scaled to 0..1. What happens when a client breaks that contract? Try three realistic mistakes: sending the raw 0..16 sensor values, sending an inverted image (white on black instead of black on white), and sending the pixels column by column instead of row by row.

```python run
raw_pixels = Xte * 16.0                                          # what the sensor really produces (0..16)
inverted = 1.0 - Xte                                             # the other polarity
transposed = Xte.reshape(-1, 8, 8).transpose(0, 2, 1).reshape(-1, 64)    # column-major order
print(f"{'what the client sends':<42}{'accuracy':>9}")
print(f"{'the contract (0..1, row by row)':<42}{accuracy(ort_fp32):>9.4f}")
print(f"{'raw 0..16 values (scale forgotten)':<42}{accuracy(ort_fp32, raw_pixels):>9.4f}")
print(f"{'inverted image':<42}{accuracy(ort_fp32, inverted):>9.4f}")
print(f"{'pixels in column order':<42}{accuracy(ort_fp32, transposed):>9.4f}")
```
```text
what the client sends                      accuracy
the contract (0..1, row by row)              0.9796
raw 0..16 values (scale forgotten)           0.9778
inverted image                               0.0037
pixels in column order                       0.1000
```

Nothing crashed in any case; the model simply answers worse, the silent failure of ml.06 section 6 (training-serving skew). Notice the first mistake barely hurt: a network made of `Linear` and `ReLU` layers with small biases is almost **scale-invariant** (multiplying the input by 16 multiplies every logit by about 16 and the largest logit stays the largest). Do not count on that: a model with a normalisation layer, a sigmoid or a large bias would break, and the other two mistakes show what a real break looks like.

Two defences, one per kind of mistake:

1. **Put deterministic preprocessing inside the exported graph**, so callers cannot forget it. Here: the division by 16.
2. **Test the whole path with golden examples**: a few raw inputs and the answers the offline pipeline gave. An inverted or transposed input produces different answers, and the test fails.

```python run
class WithScaling(nn.Module):
    """Raw pixels (0..16) in, logits out: the division by 16 is part of the model."""
    def __init__(self, inner):
        super().__init__()
        self.inner = inner
    def forward(self, x):
        return self.inner(x / 16.0)

wrapped = WithScaling(base).eval()
(ws / "export_raw").mkdir()
raw_path = export_onnx(wrapped, ws / "export_raw" / "mlp_raw.onnx", raw_pixels[:1])
ort_raw, _ = onnx_predict(raw_path)
print("operations:", [n.op_type for n in onnx.load(str(raw_path)).graph.node])

golden_in, golden_out = raw_pixels[:50], torch_predict(base)(Xte[:50])      # answers from the offline pipeline
print("golden test, correct raw input   :", bool(np.allclose(ort_raw(golden_in), golden_out, atol=1e-4)))
bad = (16 - golden_in)                                                        # an inverted client
print("golden test, inverted raw input  :", bool(np.allclose(ort_raw(bad), golden_out, atol=1e-4)), " <- the test catches it")
```
```text
operations: ['Div', 'Gemm', 'Relu', 'Gemm', 'Relu', 'Gemm']
golden test, correct raw input   : True
golden test, inverted raw input  : False  <- the test catches it
```

A `Div` now opens the graph, and callers send raw sensor values. The golden test is five lines and catches the mistakes a range check cannot. The rule from ml.06 holds: **one artifact, preprocessing inside, parity test at the door.**

### 5.10 Try it

1. You export a model and find that the `.onnx` file is 8 KB while the PyTorch file was 40 MB. What happened, and what do you check?
2. After exporting, your parity test shows `max |torch - onnx| = 0.3` and a different predicted class for 4 of 540 inputs. Is that float noise?
3. Why does ONNX Runtime's gain over PyTorch shrink as the batch grows?
4. When would you pick static quantisation over dynamic?

<details><summary>Answer</summary>

1. The weights live in a side file (`*.onnx.data`) next to the `.onnx` file. List the whole folder, ship both files together, or export with `external_data=False`.
2. No. Float noise is around 1e-5 or smaller. A difference of 0.3 with changed predictions is a bug: wrong opset behaviour, a training-only layer (dropout, batch norm) left in train mode, a missing `model.eval()`, or a different preprocessing path. Fix before anything else.
3. The overhead per call is fixed, but the arithmetic grows with the batch. At large batches the arithmetic dominates, and both runtimes call similar fast kernels, so the fixed saving becomes a small fraction of the total.
4. When you have representative calibration data and want the fastest, simplest graph with no run-time scale computing (typical for convolutional vision models and mobile targets). Pick dynamic when you have no calibration data or the input range varies a lot (typical for Linear and recurrent models).

</details>

## 6. Batching and latency in a service

### 6.1 A cost model from real measurements

Section 2.4 showed that the time for a batch grows slowly with its size. A simple model often fits: **time(b) = a + c x b**, where `a` is the fixed cost per call (overhead, reading all the weights) and `c` is the extra cost per sample. Fit it from measurements of the ONNX Runtime file, taken in a fresh process with 2 threads:

```python run
sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256]
curve = probe(onnx_path, threads=2, batches=sizes, repeat=80)
meas = np.array([curve["p50"][str(b)] for b in sizes])
c_fit, a_fit = np.polyfit(sizes, meas, 1)
print(f"time(b) = {a_fit:.3f} ms + {c_fit:.4f} ms x b")
print(f"{'batch':>6} {'measured ms':>12} {'line ms':>9}")
for b, m_ in zip(sizes, meas):
    print(f"{b:>6} {m_:>12.3f} {a_fit + c_fit * b:>9.3f}")
cost = lambda b: a_fit + c_fit * b
print(f"\nserving one at a time costs {cost(1):.3f} ms each  -> capacity {1000 / cost(1):,.0f} requests/s")
print(f"serving 32 at a time costs {cost(32):.3f} ms per batch -> capacity {32000 / cost(32):,.0f} requests/s")
```
```text
time(b) = 0.285 ms + 0.0341 ms x b
 batch  measured ms   line ms
     1        0.551     0.320
     2        0.409     0.354
     4        0.277     0.422
     8        0.416     0.558
    16        1.016     0.831
    32        1.397     1.377
    64        2.316     2.470
   128        4.491     4.654
   256        9.133     9.022

serving one at a time costs 0.320 ms each  -> capacity 3,129 requests/s
serving 32 at a time costs 1.377 ms per batch -> capacity 23,231 requests/s
```

The line follows the measurements roughly (a real machine has bumps: caches, thread start-up). The fixed part `a` is what batching shares. If `a` is large compared with `c`, batching is a huge win (a GPU, or a heavy per-call overhead); if `a` is tiny, there is little to gain. The two capacity numbers at the bottom are the potential.

### 6.2 A simulator for a batching server

A request that arrives while the server is busy must wait. Batching lets the server take **everything waiting** (up to `max_batch`) in one go, and optionally **wait a little longer** (`max_wait`) hoping more arrive. Both options add to the wait of the first request in return for lower cost per request. We simulate one worker with the cost function above. First the code, then a trace you can verify by hand.

```python run
def simulate(arrivals, cost, max_batch=1, max_wait=0.0):
    """One worker, FIFO queue. arrivals: sorted times in ms. Returns per-request latency (ms) and the batch sizes used.
    The worker starts a batch when it is free and a request is waiting; it then takes the requests that
    arrive within `max_wait` ms of that moment, up to `max_batch`; a full batch starts as soon as it is full."""
    arrivals = np.asarray(arrivals, dtype=float)
    n = len(arrivals)
    latency = np.empty(n)
    sizes = []
    free_at, i = 0.0, 0
    while i < n:
        start = max(free_at, arrivals[i])
        j = i
        while j < n and j - i < max_batch and arrivals[j] <= start + max_wait:
            j += 1
        size = j - i
        begin = max(start, arrivals[j - 1]) if size == max_batch else start + max_wait
        done = begin + cost(size)
        latency[i:j] = done - arrivals[i:j]
        sizes.append(size)
        free_at, i = done, j
    return latency, sizes

# A tiny world we can check on paper: a batch of b costs 1 + 0.1*b ms. Requests arrive at 0, 0.2, 0.3 and 5 ms.
toy_cost = lambda b: 1 + 0.1 * b
toy_arrivals = [0, 0.2, 0.3, 5]
for label, kw in [("one at a time        ", dict(max_batch=1)),
                  ("take what is waiting", dict(max_batch=8)),
                  ("wait up to 1 ms     ", dict(max_batch=8, max_wait=1.0))]:
    lat, sizes = simulate(toy_arrivals, toy_cost, **kw)
    print(f"{label} latencies {np.round(lat, 2).tolist()} batch sizes {sizes}")
assert np.allclose(simulate(toy_arrivals, toy_cost, max_batch=1)[0], [1.1, 2.0, 3.0, 1.1])
assert np.allclose(simulate(toy_arrivals, toy_cost, max_batch=8)[0], [1.1, 2.1, 2.0, 1.1])
assert np.allclose(simulate(toy_arrivals, toy_cost, max_batch=8, max_wait=1.0)[0], [2.3, 2.1, 2.0, 2.1])
print("hand-traced values match")
```
```text
one at a time         latencies [1.1, 2.0, 3.0, 1.1] batch sizes [1, 1, 1, 1]
take what is waiting latencies [1.1, 2.1, 2.0, 1.1] batch sizes [1, 2, 1]
wait up to 1 ms      latencies [2.3, 2.1, 2.0, 2.1] batch sizes [3, 1]
hand-traced values match
```

Trace the middle line on paper. Request 0 arrives at 0 and the worker is free: batch of 1, cost 1.1, done at 1.1, latency 1.1. At 1.1 requests 1 (arrived 0.2) and 2 (0.3) are waiting, request 3 is not yet: batch of 2, cost 1.2, done at 2.3, latencies 2.3 - 0.2 = 2.1 and 2.3 - 0.3 = 2.0. Request 3 arrives at 5 to an idle worker: 1.1. The "wait up to 1 ms" line shows the price of waiting: request 0 now takes 2.3 instead of 1.1, because it waited for neighbours that came.

Now real arrival patterns. Requests from many independent users arrive as a **Poisson process** (random gaps with a fixed average rate). We test three load levels relative to the capacity at batch 1, and three policies, with the cost model fitted from the real model:

```python run
rng = np.random.default_rng(0)
cap1 = 1000 / cost(1)                                           # requests/s a one-at-a-time server can sustain
policies = [("one at a time", dict(max_batch=1)),
            ("take waiting, max 32", dict(max_batch=32)),
            ("wait 2 ms, max 32", dict(max_batch=32, max_wait=2.0))]
print(f"capacity when serving one at a time: {cap1:,.0f} requests/s\n")
print(f"{'load':>6} {'req/s':>8}  {'policy':<22}{'p50 ms':>9}{'p95 ms':>10}{'mean batch':>12}")
for load in (0.3, 0.9, 1.5):
    rate = load * cap1
    arrivals = np.cumsum(rng.exponential(1000 / rate, size=20000))          # gaps in ms
    for name, kw in policies:
        lat, sizes = simulate(arrivals, cost, **kw)
        print(f"{load:>5.1f}x {rate:>8,.0f}  {name:<22}{np.percentile(lat, 50):>9.2f}{np.percentile(lat, 95):>10.2f}{np.mean(sizes):>12.2f}")
    print()
```
```text
capacity when serving one at a time: 3,129 requests/s

  load    req/s  policy                   p50 ms    p95 ms  mean batch
  0.3x      939  one at a time              0.32      0.67        1.00
  0.3x      939  take waiting, max 32       0.32      0.59        1.04
  0.3x      939  wait 2 ms, max 32          1.98      2.63        2.96

  0.9x    2,816  one at a time              1.19      4.16        1.00
  0.9x    2,816  take waiting, max 32       0.45      0.67        1.33
  0.9x    2,816  wait 2 ms, max 32          1.89      2.98        7.33

  1.5x    4,694  one at a time           1055.08   2008.13        1.00
  1.5x    4,694  take waiting, max 32       0.53      0.74        1.83
  1.5x    4,694  wait 2 ms, max 32          2.12      3.38       12.78
```

This is a **simulation using measured costs**, not a measurement of a real server, but its message is the one real systems show:

- **Light load (0.3x)**: batching changes little, and *waiting* only adds delay. At low traffic, serve immediately.
- **Heavy load (0.9x)**: queues form and "take what is waiting" starts to pay for itself with no waiting at all.
- **Overload (1.5x)**: serving one at a time **cannot keep up**: the queue and the latency grow without bound. Batching is not an optimisation here; it is what keeps the service alive.

The p95 is the user's experience. Always report it next to the median.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate a checkout counter. Customers (requests) arrive at random times and queue. Version A: the cashier serves one customer at a time, taking 1 minute each; at high arrival rates the queue grows without limit. Version B: the cashier scans up to 8 waiting customers' baskets together, taking 1.8 minutes in total. Show the queue length over time for both, and mark the average waiting time. Add a third version where the cashier waits 2 minutes for more customers before starting, and show that at low traffic this only adds waiting."

### 6.3 A real micro-batcher

In a real service the same idea is a queue plus one worker task. Each request puts its input and a **future** (a placeholder for the answer) on the queue; the worker takes one item, then keeps collecting until the batch is full or the deadline passes, runs the model once, and fills in every future. Here it is with `asyncio`:

```python run
import asyncio

class MicroBatcher:
    """Collect concurrent requests for up to max_wait_ms, run them as one batch."""
    def __init__(self, predict, max_batch=32, max_wait_ms=2.0):
        self.predict, self.max_batch, self.max_wait = predict, max_batch, max_wait_ms / 1000
        self.queue, self.task, self.batch_sizes = None, None, []

    async def start(self):
        self.queue = asyncio.Queue()
        self.task = asyncio.create_task(self._worker())

    async def stop(self):
        self.task.cancel()

    async def infer(self, x):
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((x, future))
        return await future

    async def _worker(self):
        loop = asyncio.get_running_loop()
        while True:
            items = [await self.queue.get()]
            deadline = loop.time() + self.max_wait
            while len(items) < self.max_batch:
                timeout = deadline - loop.time()
                if timeout <= 0:
                    break
                try:
                    items.append(await asyncio.wait_for(self.queue.get(), timeout))
                except asyncio.TimeoutError:
                    break
            try:
                out = self.predict(np.stack([x for x, _ in items]))
                for (_, future), row in zip(items, out):
                    future.set_result(row)
                self.batch_sizes.append(len(items))
            except Exception as exc:                     # never leave a caller waiting forever
                for _, future in items:
                    future.set_exception(exc)

async def demo():
    batcher = MicroBatcher(ort_fp32, max_batch=32, max_wait_ms=2.0)
    await batcher.start()
    results = await asyncio.gather(*[batcher.infer(Xte[i]) for i in range(100)])      # 100 concurrent requests
    await batcher.stop()
    return np.array(results), batcher.batch_sizes

results, batch_sizes = asyncio.run(demo())
print("batch sizes used:", batch_sizes)
print("every request got its OWN answer:", bool((results.argmax(1) == ort_fp32(Xte[:100]).argmax(1)).all()))
print("max batch <= 32:", max(batch_sizes) <= 32, "| total handled:", sum(batch_sizes))
```
```text
batch sizes used: [32, 32, 32, 4]
every request got its OWN answer: True
max batch <= 32: True | total handled: 100
```

One hundred requests arrived at the same time and the model ran only a handful of times, yet each caller got its own answer. Production inference servers (NVIDIA Triton, TorchServe, BentoML, vLLM for language models) implement this **dynamic batching**, with many refinements (several queues, priorities, timeouts). The traps are always the same: forgetting to deliver an exception to the waiting callers (they would hang), unbounded queues (set a limit and return an error "busy" when full: **load shedding**), and a `max_wait` larger than your latency budget.

### 6.4 Try it

1. Your latency budget is 50 ms at p95 and the model takes 20 ms for a batch of 1 and 24 ms for a batch of 16. How long can `max_wait` be at most? Is batching worth it here?
2. Why does the mean batch size at low load stay close to 1 even when `max_batch` is 32?
3. Give two reasons not to make `max_wait` large "to get bigger batches".

<details><summary>Answer</summary>

1. A request can wait `max_wait` and then be served in a batch (up to 24 ms): worst case about `max_wait + 24`, plus any queueing behind a previous batch (up to another 24). To stay under 50 ms you need `max_wait + 24 + 24 <= 50`, so `max_wait <= 2 ms` in the worst case. Batching is worth it only if load is high enough that batches really fill: 16 requests for 24 ms rather than 320 ms of one-at-a-time work, a 13x throughput gain, so yes under load, no at low traffic.
2. Few requests arrive within the same short window, so the worker usually finds only one waiting. The batch size reflects the **traffic**, not the limit.
3. Every request pays the wait in latency, even when traffic is low and no extra request comes; and the budget p95 is shared with queueing and the model call, so a long wait leaves no slack for bursts.

</details>

## 7. Running on small devices

### 7.1 What changes when the target is small

A server has lots of memory, many cores, a fast network and a power socket. A phone, a Raspberry Pi class board, a camera or a sensor has less of everything. The constraints, in the order they usually bite:

| Constraint | Why it matters | Typical response |
|---|---|---|
| **Memory (RAM)** | the model, its activations and the runtime must all fit, with room for the rest of the application | quantise, smaller architecture, smaller runtime |
| **Storage / download size** | app-store limits, over-the-air updates over slow links | int8 or 4-bit weights, compression |
| **Compute** | few slow cores, often no GPU; some have an NPU (neural accelerator) | measure on the device, use its accelerator through the right runtime |
| **Cold start** | the process starts, loads the model, answers once; the user waits | small files, memory-mapped weights, lazy loading |
| **Power and heat** | speed drops when the chip gets hot; battery drains | fewer operations, batch work, run less often |
| **No network** | cannot call a server; must work alone | the model and a fallback must live on the device |

Rough orders of magnitude (they vary enormously, check the data sheet of *your* device): a phone has several GB of RAM; a Raspberry Pi class board has between half a GB and several GB; a microcontroller has tens to hundreds of **kilo**bytes, which is why microcontroller models (TinyML) are measured in tens of KB.

### 7.2 Measure what a device cares about: cold start, memory, one core

The averages from the benchmarks above are *warm, steady-state* numbers. A device cares about three more:

1. **Load time**: from "process starts" to "model ready".
2. **First-call time**: the first answer is slower than the next ones.
3. **Memory in use (RSS, resident set size)**: the RAM the process holds. Note that this includes the **runtime itself**.

We measure them with the `probe` of section 5.6: a **fresh process** per model (so numbers are not polluted by what the rest of the chapter did), with **one thread**, which imitates a single-core board. The row "runtime only" is a process that imported ONNX Runtime and loaded nothing.

```python run
print(f"{'process':<28}{'file KB':>9}{'load ms':>9}{'first ms':>9}{'p50 ms':>8}{'RSS MB':>9}")
for name, path in [("runtime only (no model)", "none"), ("ort float32, 1 thread", onnx_path),
                   ("ort int8 dynamic, 1 thread", int8_dyn_path), ("ort int8 static, 1 thread", int8_static_path)]:
    r = probe(path, threads=1, batches=(1,), repeat=200)
    kb = 0 if path == "none" else size_of_file(path) / 1024
    p50 = r["p50"].get("1", 0)
    print(f"{name:<28}{kb:>9.0f}{r['load_ms']:>9.1f}{r['first_ms']:>9.2f}{p50:>8.3f}{r['rss_mb']:>9.1f}")
```
```text
process                       file KB  load ms first ms  p50 ms   RSS MB
runtime only (no model)             0      0.0     0.00   0.000     57.4
ort float32, 1 thread            4407     84.2     1.19   0.386     78.9
ort int8 dynamic, 1 thread       1113     74.0     1.05   0.087     73.6
ort int8 static, 1 thread        1140     70.9     0.95   0.118     74.7
```

Read the last column carefully. The **runtime alone** (an empty process that only imported ONNX Runtime) already holds most of the memory. Loading the model adds about 20 MB for the float32 file and about 16 MB for the int8 files: more than the files themselves (4 MB and 1 MB), because the session keeps buffers and working copies of the weights, and the int8 model saves only about 5 MB of RAM although its file is 4 times smaller. That is the lesson of this section: **file size is not memory, and for small models the runtime dominates**. Shrinking a 4 MB model to 1 MB does not rescue a board with 32 MB of RAM if the runtime itself needs far more than that. On such targets you change the **runtime** (a mobile or micro build of the engine, TensorFlow Lite, a C++ runtime without Python) as much as the model.

The first-call time is the cost of the first answer after loading: the one a user waiting for a camera app to open actually feels. It is several times the steady-state p50. RSS here is the resident memory at the end of the run (a good stand-in for the peak). The `-I` flag runs the probe in isolated mode, so no stray local files get imported.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a stacked bar of the memory used by a process that runs a small neural network: a tall block for 'Python + ONNX Runtime libraries', a thin block for 'model weights (4 MB float32)', a thin block for 'activations and buffers'. Next to it draw the same bar after int8 quantisation: the weights block is a quarter as tall but the total bar barely changes. Add a dotted line at the RAM limit of a small board and show that only a smaller runtime, not a smaller model, gets under the line."

### 7.3 Formats and runtimes for small targets (reference, not run here)

None of the tools below were installed or run for this chapter; the table is a map for when you meet a real device. Always check the current documentation: these projects change quickly.

| Target | Common route | Notes |
|---|---|---|
| Server CPU / GPU | PyTorch, or ONNX Runtime, or TensorRT (NVIDIA GPUs), OpenVINO (Intel) | the chapter's route |
| Android / iOS | TensorFlow Lite (now **LiteRT**), Core ML (Apple), **ExecuTorch** (PyTorch on device), ONNX Runtime Mobile | int8 and float16 are the norm; use the phone's NPU through the vendor delegate |
| Raspberry Pi class boards | ONNX Runtime (ARM build from pip), TensorFlow Lite | a normal Linux with Python: the chapter's code runs; measure there |
| Browsers | ONNX Runtime Web (WebAssembly or WebGPU), TensorFlow.js | the model downloads to the user: size is page-load time |
| Microcontrollers | TensorFlow Lite for Microcontrollers, vendor SDKs | models of tens of KB, int8 only, no operating system |
| Large language models | **GGUF** files with `llama.cpp`, and 4-bit or 5-bit weight quantisation | the same idea as section 3 with groups of weights sharing a scale |

How a typical move to a Pi looks (illustrative, **not executed here**): copy `mlp_int8_static.onnx` and a small `predict.py` to the board; `pip install onnxruntime numpy` in a virtual environment; run the probe script of 7.2 **on the board** and compare with your laptop. The numbers you act on are the ones measured *on the target*.

### 7.4 Memory arithmetic before the device arrives

A quick estimate decides whether a model can fit at all:

```
memory  ≈  runtime  +  weights  +  activations (largest layer output x batch x bytes)  +  your application
```

For a convolutional network the **activations** are often larger than the weights (a 224x224 image makes feature maps of millions of numbers in the early layers), so batch size 1 and int8 activations matter as much as the weight format. For a language model the **KV cache** grows with the length of the conversation. For our MLP the largest activation is 1,024 numbers, 4 KB: negligible.

### 7.5 An on-device checklist

1. **Requirements first**: RAM available to the model, p95 latency, storage, battery per day.
2. **Measure on the device**, warm and cold, with the real input path (camera, microphone), not only the model call.
3. **Test accuracy after every conversion** on data from the device's own sensors: a phone camera is not your training set.
4. **Pin the runtime version** and keep the conversion script in git: tomorrow's converter may produce a different model.
5. **Plan updates and rollback**: how does a new model arrive (over the air), how do you check its hash, how do you go back (the registry and rollback ideas of ml.06 apply to a fleet of devices).
6. **Keep a fallback**: if the model fails to load or the answer is suspicious (out of range), the device still must do something sensible.
7. **Monitor what you can**: even a tiny anonymised counter of predictions and failures tells you about drift (ml.06 section 7).

### 7.6 Try it

1. Your model is 30 MB in float32 and must fit in a 10 MB download. List three things you would try, in order.
2. A board has 64 MB of RAM. The runtime needs 40 MB, your application 10 MB, the int8 model is 5 MB with 3 MB of activations. Does it fit? What is the margin, and is it comfortable?
3. Why is "it runs fast on my laptop" almost no evidence about a Raspberry Pi?

<details><summary>Answer</summary>

1. (a) Check whether a smaller architecture reaches the accuracy (section 4.4), because it helps size, speed and memory together. (b) int8 quantisation (about 7.5 MB, measure accuracy; QAT if the loss is too large). (c) If still too large, 4-bit weights, pruning with a sparse or compressed format, or distillation into a smaller student. Compress the download (zip) as well, since weights compress somewhat.
2. 40 + 10 + 5 + 3 = 58 MB of 64 MB, so it fits with a **6 MB margin, about 9 %**. That is uncomfortable: the operating system, memory fragmentation and a spike in the application can each use more than 6 MB. Aim for a margin of 25 % or more, or move the model out of RAM (memory-mapped weights).
3. Different CPU architecture (ARM against x86), clock speed, number and type of cores, memory bandwidth, cache sizes, vector instructions and thermal limits. The *ranking* of options usually carries over, the absolute numbers do not, and surprises (such as float16 being slow in 3.6) are decided by the hardware. Measure on the target.

</details>

## 8. Choosing: the trade-off table and the Pareto front

### 8.1 More candidates than one number can rank

By now you have many variants of the same model: float32 in PyTorch, a pruned copy, a small architecture, ONNX files in float32 and int8. Each has a size, an accuracy and a latency. Which is "best"? **There is no single answer**, because the three numbers pull in different directions. What you *can* do is throw away the candidates that are **beaten on every axis** by another one. A candidate **A dominates B** if A is at least as good as B on size, latency and accuracy, and strictly better on at least one. The candidates nobody dominates form the **Pareto front**: the only ones worth discussing.

Accuracy needs a tolerance: with 540 test images, one image is 0.0019, so differences smaller than that are noise (section 3.3). We treat accuracies within `acc_tol` as equal. Write it, with a toy example you can check by hand:

```python run
def dominates(a, b, acc_tol=0.0):
    """True if row a is at least as good as b everywhere (size, p50 latency, accuracy) and strictly better somewhere."""
    no_worse = (a["size_kb"] <= b["size_kb"] and a["p50_ms"] <= b["p50_ms"] and a["acc"] >= b["acc"] - acc_tol)
    better = (a["size_kb"] < b["size_kb"] or a["p50_ms"] < b["p50_ms"] or a["acc"] > b["acc"] + acc_tol)
    return no_worse and better

def pareto_front(rows, acc_tol=0.0):
    """Rows that no other row dominates."""
    return [r for r in rows if not any(dominates(o, r, acc_tol) for o in rows if o is not r)]

toy = [dict(name="A", size_kb=100, p50_ms=1.0, acc=0.95),
       dict(name="B", size_kb=200, p50_ms=2.0, acc=0.94),     # worse than A on every axis
       dict(name="C", size_kb=50,  p50_ms=1.5, acc=0.90),     # smaller than A, but less accurate and slower
       dict(name="D", size_kb=100, p50_ms=1.0, acc=0.951)]    # a hair more accurate than A (0.001)
print("tolerance 0     :", [r["name"] for r in pareto_front(toy)])
print("tolerance 0.002 :", [r["name"] for r in pareto_front(toy, acc_tol=0.002)])
assert [r["name"] for r in pareto_front(toy)] == ["C", "D"]
assert [r["name"] for r in pareto_front(toy, 0.002)] == ["A", "C", "D"]
```
```text
tolerance 0     : ['C', 'D']
tolerance 0.002 : ['A', 'C', 'D']
```

Check it by hand. B loses to A everywhere, so B is out. C survives because it is the smallest. With zero tolerance D beats A (same size and speed, 0.001 more accurate), so A is out; with a tolerance of 0.002 the difference of 0.001 is called noise, A and D are equal, and neither dominates the other. The tolerance **changes the answer**, which is why it must be chosen deliberately from the size of your test set.

### 8.2 The table for this chapter's model

Build the candidates on equal footing: every latency from a fresh process (`profile_file`), every accuracy from the same test set. Add two combinations: the small architecture exported to ONNX and quantised, and the 90 % pruned model whose file is compressed (its latency is that of a dense model; section 4.3).

```python run
torch.save(small.state_dict(), ws / "small.pt")
torch.save(pruned_models[0.9].state_dict(), ws / "pruned90.pt")

(ws / "export_small").mkdir()
small_onnx = export_onnx(small, ws / "export_small" / "small.onnx", Xte[:1])
small_int8 = ws / "small_int8.onnx"
with quiet():
    quantize_dynamic(str(small_onnx), str(small_int8), weight_type=QuantType.QInt8)
ort_small, _ = onnx_predict(small_onnx)
ort_small_q, _ = onnx_predict(small_int8)

candidates = [
    profile_file("torch float32", ws / "base.pt", torch_predict(base)),
    profile_file("torch small (32 units)", ws / "small.pt", torch_predict(small)),
    profile_file("torch pruned 90%", ws / "pruned90.pt", torch_predict(pruned_models[0.9])),
    profile_file("ort float32", onnx_path, ort_fp32),
    profile_file("ort int8 dynamic", int8_dyn_path, ort_dyn),
    profile_file("ort int8 static", int8_static_path, ort_sta),
    profile_file("ort small float32", small_onnx, ort_small),
    profile_file("ort small int8", small_int8, ort_small_q),
]
for r in candidates:                                              # the pruned file is only smaller if compressed
    if r["name"] == "torch pruned 90%":
        r["size_kb"] = len(zlib.compress((ws / "pruned90.pt").read_bytes(), 9)) / 1024
        r["name"] = "torch pruned 90% (zipped)"

front = pareto_front(candidates, acc_tol=0.002)
on_front = {r["name"] for r in front}
show(candidates, "torch float32")
print("\nPareto front (accuracy tolerance 0.002):", sorted(on_front))
print("dominated:", sorted(r["name"] for r in candidates if r["name"] not in on_front))
```
```text
model                     size KB     acc   p50 ms   p95 ms  samples/s  size x  speed x   d acc
torch float32                4403  0.9796    0.284    0.361      24390    1.00     1.00 +0.0000
torch small (32 units)         16  0.9611    0.055    0.060     830091  273.08     5.15 -0.0185
torch pruned 90% (zipped)      688  0.9704    0.288    0.343      24149    6.39     0.99 -0.0093
ort float32                  4407  0.9796    0.214    0.239      28368    1.00     1.33 +0.0000
ort int8 dynamic             1113  0.9796    0.153    0.174      34613    3.96     1.86 +0.0000
ort int8 static              1140  0.9796    0.196    0.221      37433    3.86     1.45 +0.0000
ort small float32              20  0.9611    0.031    0.041    1050903  215.84     9.17 -0.0185
ort small int8                 10  0.9630    0.020    0.031    1298174  434.95    14.00 -0.0167

Pareto front (accuracy tolerance 0.002): ['ort int8 dynamic', 'ort small int8', 'torch pruned 90% (zipped)']
dominated: ['ort float32', 'ort int8 static', 'ort small float32', 'torch float32', 'torch small (32 units)']
```

One warning before reading it: a row on the front is not automatically deployable. `torch pruned 90% (zipped)` is on the front only because we count its *compressed* size; to run it you must unzip it into a dense model, so its real memory and speed are those of the baseline. Check what a number means before you trust the front. Now read the table in three passes. First the **ratios against the baseline**: this is the "before and after" the syllabus asks for. Second the **front**: dominated rows can be dropped from the conversation immediately, whatever their other merits. Third the **trade-offs among the survivors**: the cheapest in size usually costs accuracy; the most accurate is bigger or slower. That last choice is a decision about your requirements, not a calculation.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Make a scatter plot with model size (KB, log scale) on the x axis and test accuracy on the y axis, one labelled dot per candidate: 'torch float32', 'torch small (32 units)', 'ort float32', 'ort int8 dynamic', 'ort small int8' and so on. Draw the Pareto front as a staircase line connecting the non-dominated dots, grey out the dominated ones, and shade the region that violates a requirement 'size under 2 MB and accuracy at least 0.97' so that the reader can see which dots are allowed."

### 8.3 Pick under constraints

A requirement turns the front into a decision: **filter** by what you must have, then **minimise** what you want least of. For example: "accuracy at most 1 point below the baseline, and size under 2 MB; among those pick the lowest p95 latency".

```python run
def choose(rows, min_acc, max_size_kb=None, minimise="p95_ms"):
    """Among rows meeting the constraints, return the one with the smallest `minimise` value (or None)."""
    ok = [r for r in rows if r["acc"] >= min_acc and (max_size_kb is None or r["size_kb"] <= max_size_kb)]
    return min(ok, key=lambda r: r[minimise]) if ok else None

base_acc = next(r["acc"] for r in candidates if r["name"] == "torch float32")
for label, kw in [("within 1 point, size <= 2 MB, fastest p95", dict(min_acc=base_acc - 0.01, max_size_kb=2048)),
                  ("within 3 points, size <= 100 KB, fastest p95", dict(min_acc=base_acc - 0.03, max_size_kb=100)),
                  ("within 0.5 points, size <= 100 KB (too strict?)", dict(min_acc=base_acc - 0.005, max_size_kb=100))]:
    pick = choose(candidates, **kw)
    print(f"{label:<50} -> {pick['name'] if pick else 'NOTHING qualifies'}")
```
```text
within 1 point, size <= 2 MB, fastest p95          -> ort int8 dynamic
within 3 points, size <= 100 KB, fastest p95       -> ort small int8
within 0.5 points, size <= 100 KB (too strict?)    -> NOTHING qualifies
```

When "nothing qualifies" is the answer, that is information too: either the requirement is unrealistic for this model family, or you need a technique from the less-travelled end (QAT, distillation, a different architecture). **State the requirement before looking at the table**, otherwise you will unconsciously choose the requirement that justifies the candidate you already like.

### 8.4 Try it

1. A candidate is 10 % smaller than the baseline and 5 % faster, but 0.003 less accurate on 540 test images. Is it a clear win?
2. Two candidates are on the Pareto front: X (1 MB, 0.5 ms, 0.97) and Y (4 MB, 0.3 ms, 0.98). Your requirement is "p95 under 1 ms, accuracy at least 0.975". Which do you pick, and what changes if the limit were "size under 2 MB"?
3. Why compute the front *after* fixing a tolerance for accuracy noise?

<details><summary>Answer</summary>

1. No. 0.003 is about 1.6 test images, which is noise, so the accuracy loss might be zero or might be real; the gains are modest. Re-measure on a larger test set or with several seeds before claiming anything.
2. Y: it is the only one with accuracy at least 0.975, and 0.3 ms satisfies the latency. With "size under 2 MB" instead, Y is out and X is the only candidate, but X fails "accuracy at least 0.975": so no candidate satisfies both, and you must relax a requirement or find another model.
3. Without a tolerance, tiny noisy differences decide who dominates whom, and the front changes from one random split to the next. The tolerance (about the size of one test image, or better a confidence interval) makes the front stable.

</details>

## 9. Project: optimise a model and report the trade-off

### 9.1 The brief

Take the digit classifier from this chapter and produce an **optimisation report**. The deliverable is one small, tested package plus a report:

1. **`opt_kit.py`**: a library with the tools of this chapter that can be tested without PyTorch: measuring with warm-up and percentiles, symmetric quantisation, magnitude pruning, dominance and Pareto front, constraint selection, a parity check, and a Markdown table writer.
2. **`run_project.py`**: trains the baseline, builds seven variants (smaller architecture, pruning with fine-tuning, ONNX float32, dynamic and static int8, a small int8 model), measures every one **in a fresh process**, checks **parity** of the export, and writes `report.md` and `results.json`.
3. **`test_opt_kit.py`**: pytest tests for the kit, including hand-checked values.

The report must answer, in numbers: how much smaller, how much faster, and how much accuracy did we give up, **and which variant do we ship under the stated requirement**.

### 9.2 The kit

The kit uses only NumPy, so its tests run in a fraction of a second. Notice that every function carries the reasoning of a section above.

```python run
proj = ws / "project"
proj.mkdir()
import shutil
shutil.copy(ws / "probe.py", proj / "probe.py")                  # the fresh-process instrument of section 5.6

(proj / "opt_kit.py").write_text(r'''"""opt_kit: measure and compare optimised variants of a model (size, latency, accuracy)."""
from __future__ import annotations

import time
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Row:
    """One candidate: how big, how accurate, how fast."""
    name: str
    size_kb: float
    acc: float
    p50_ms: float
    p95_ms: float


def bench(fn, x, warmup: int = 10, repeat: int = 100) -> dict:
    """Time fn(x) in milliseconds. The warm-up calls are made but not timed."""
    for _ in range(warmup):
        fn(x)
    times = []
    for _ in range(repeat):
        t0 = time.perf_counter()
        fn(x)
        times.append((time.perf_counter() - t0) * 1e3)
    times.sort()
    return {"p50": times[len(times) // 2], "p95": times[int(len(times) * 0.95)], "min": times[0]}


def quantise_symmetric(values: np.ndarray, bits: int = 8):
    """Map floats to integers in [-qmax, qmax] with one scale. Returns (int8 array, scale)."""
    qmax = 2 ** (bits - 1) - 1
    peak = float(np.abs(values).max())
    scale = peak / qmax if peak > 0 else 1.0
    q = np.clip(np.round(values / scale), -qmax, qmax).astype(np.int8)
    return q, scale


def dequantise(q: np.ndarray, scale: float) -> np.ndarray:
    """Integers back to float32."""
    return q.astype(np.float32) * np.float32(scale)


def prune_by_magnitude(weights: np.ndarray, fraction: float) -> np.ndarray:
    """Copy of `weights` with the smallest `fraction` (by absolute value) set to zero."""
    if not 0.0 <= fraction < 1.0:
        raise ValueError("fraction must be in [0, 1)")
    out = weights.copy()
    k = int(out.size * fraction)
    if k:
        order = np.argsort(np.abs(out), axis=None, kind="stable")[:k]
        out.flat[order] = 0.0
    return out


def sparsity(weights: np.ndarray) -> float:
    """Fraction of exactly-zero entries."""
    return float((weights == 0).mean())


def dominates(a: Row, b: Row, acc_tol: float = 0.0) -> bool:
    """a is at least as good as b on size, p50 latency and accuracy, and strictly better on one."""
    no_worse = a.size_kb <= b.size_kb and a.p50_ms <= b.p50_ms and a.acc >= b.acc - acc_tol
    better = a.size_kb < b.size_kb or a.p50_ms < b.p50_ms or a.acc > b.acc + acc_tol
    return no_worse and better


def pareto_front(rows: list, acc_tol: float = 0.0) -> list:
    """The rows that no other row dominates, in their original order."""
    return [r for r in rows if not any(dominates(o, r, acc_tol) for o in rows if o is not r)]


def choose(rows: list, min_acc: float, max_p95_ms: float | None = None, max_size_kb: float | None = None):
    """Smallest file among the rows that meet every constraint; ties go to the lower p95. None if nothing qualifies."""
    ok = [r for r in rows if r.acc >= min_acc
          and (max_p95_ms is None or r.p95_ms <= max_p95_ms)
          and (max_size_kb is None or r.size_kb <= max_size_kb)]
    return min(ok, key=lambda r: (r.size_kb, r.p95_ms)) if ok else None


def parity(reference: np.ndarray, candidate: np.ndarray, atol: float = 1e-3) -> dict:
    """Compare two logit arrays: largest absolute difference, whether argmax agrees everywhere, and a verdict."""
    diff = float(np.abs(reference - candidate).max())
    same = bool((reference.argmax(axis=1) == candidate.argmax(axis=1)).all())
    return {"max_abs_diff": diff, "same_classes": same, "ok": diff <= atol and same}


def to_markdown(rows: list, base_name: str, chosen: Row | None = None, front: list | None = None) -> str:
    """A table with ratios against the baseline row. Marks the chosen row with * and front members with +."""
    base = next(r for r in rows if r.name == base_name)
    front_names = {r.name for r in front} if front is not None else set()
    lines = ["| variant | size KB | size x | acc | d acc | p50 ms | p50 x | p95 ms | note |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in rows:
        note = ("chosen" if chosen is not None and r.name == chosen.name else "") + (" front" if r.name in front_names else "")
        lines.append(f"| {r.name} | {r.size_kb:.0f} | {base.size_kb / r.size_kb:.2f} | {r.acc:.4f} | {r.acc - base.acc:+.4f} "
                     f"| {r.p50_ms:.3f} | {base.p50_ms / r.p50_ms:.2f} | {r.p95_ms:.3f} | {note.strip()} |")
    return "\n".join(lines)
''', encoding="utf-8")
print("opt_kit.py:", len((proj / "opt_kit.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
opt_kit.py: 101 lines
```

### 9.3 Tests for the kit

Tests are the proof that the kit means what it says. Every assertion has a message naming the likely mistake. The values in `test_pareto_front` and `test_choose` were worked out on paper.

```python run
(proj / "test_opt_kit.py").write_text(r'''import numpy as np
import pytest

from opt_kit import (Row, bench, choose, dequantise, dominates, pareto_front, parity,
                     prune_by_magnitude, quantise_symmetric, sparsity, to_markdown)


def test_quantise_error_is_at_most_half_a_step():
    w = np.random.default_rng(0).normal(0, 0.05, size=(64, 64)).astype(np.float32)
    q, scale = quantise_symmetric(w)
    err = np.abs(w - dequantise(q, scale)).max()
    assert err <= scale / 2 + 1e-7, "rounding to the nearest grid point can never move a value by more than half a step"


def test_quantise_extremes_and_zero():
    v = np.array([-0.30, -0.05, 0.0, 0.12, 0.45], dtype=np.float32)
    q, scale = quantise_symmetric(v)
    assert q.tolist() == [-85, -14, 0, 34, 127], "scale = 0.45/127, so 0.45 -> 127 and 0 -> 0 (see section 3.1)"
    assert q.dtype == np.int8, "the integers must be stored as int8, otherwise there is no 4x saving"
    assert abs(scale - 0.45 / 127) < 1e-9


def test_quantise_all_zero_input_does_not_divide_by_zero():
    q, scale = quantise_symmetric(np.zeros((3, 3), dtype=np.float32))
    assert (q == 0).all() and scale == 1.0, "an all-zero tensor has no peak: use scale 1 instead of dividing by 0"


def test_fewer_bits_means_larger_error():
    w = np.random.default_rng(1).normal(0, 0.05, size=1000).astype(np.float32)
    errs = [np.abs(w - dequantise(*quantise_symmetric(w, bits))).mean() for bits in (8, 6, 4)]
    assert errs[0] < errs[1] < errs[2], "each bit removed doubles the step, so the error must grow"


def test_prune_exact_fraction_and_keeps_the_largest():
    w = np.array([[0.5, -0.1, 0.05, -0.9], [0.2, -0.02, 0.7, 0.01]], dtype=np.float32)
    p = prune_by_magnitude(w, 0.5)                          # 8 weights -> the 4 smallest by |value| go
    assert sparsity(p) == 0.5, "50% of 8 weights is exactly 4 zeros"
    assert p[0, 3] == -0.9 and p[1, 2] == 0.7, "the largest weights must survive"
    assert p[0, 2] == 0.0 and p[1, 1] == 0.0 and p[1, 3] == 0.0 and p[0, 1] == 0.0, "the four smallest |weights| are zeroed"
    assert w[0, 2] == 0.05, "pruning must return a copy and leave the input untouched"


def test_prune_rejects_bad_fraction():
    with pytest.raises(ValueError):
        prune_by_magnitude(np.ones(4, dtype=np.float32), 1.0)


R = lambda n, size, acc, p50: Row(n, size, acc, p50, p50 * 1.5)


def test_dominates_hand_cases():
    a, b = R("a", 100, 0.95, 1.0), R("b", 200, 0.94, 2.0)
    assert dominates(a, b), "a is smaller, faster and more accurate"
    assert not dominates(b, a)
    assert not dominates(a, a), "nothing dominates an identical row (needs one strict improvement)"
    c = R("c", 50, 0.90, 1.5)
    assert not dominates(a, c) and not dominates(c, a), "c is smaller but worse elsewhere: a trade-off, not dominance"


def test_pareto_front_hand_checked():
    rows = [R("A", 100, 0.95, 1.0), R("B", 200, 0.94, 2.0), R("C", 50, 0.90, 1.5), R("D", 100, 0.951, 1.0)]
    assert [r.name for r in pareto_front(rows)] == ["C", "D"], "B loses to A, A loses to D (0.001 more accurate)"
    assert [r.name for r in pareto_front(rows, acc_tol=0.002)] == ["A", "C", "D"], "0.001 is inside the tolerance"


def test_choose_picks_smallest_feasible_and_none_when_impossible():
    rows = [R("big", 4000, 0.98, 0.5), R("mid", 1000, 0.975, 0.4), R("tiny", 20, 0.90, 0.1)]
    assert choose(rows, min_acc=0.97).name == "mid", "tiny is too inaccurate; of big and mid the smaller file wins"
    assert choose(rows, min_acc=0.97, max_size_kb=500) is None, "nothing is both accurate enough and under 500 KB"
    assert choose(rows, min_acc=0.97, max_p95_ms=0.65).name == "mid", "R makes p95 = 1.5 x p50: big has 0.75 (too slow), mid has 0.6"
    assert choose(rows, min_acc=0.97, max_p95_ms=0.5) is None, "both accurate rows exceed a 0.5 ms p95 (0.75 and 0.6)"


def test_parity_detects_a_broken_export():
    ref = np.array([[2.0, 0.1], [0.2, 1.5]], dtype=np.float32)
    assert parity(ref, ref + 1e-5)["ok"], "tiny float noise is fine"
    swapped = ref[:, ::-1]
    res = parity(ref, swapped)
    assert not res["same_classes"] and not res["ok"], "swapped columns change every predicted class"


def test_bench_makes_warmup_plus_repeat_calls_and_orders_percentiles():
    calls = []
    out = bench(lambda x: calls.append(1), None, warmup=3, repeat=20)
    assert len(calls) == 23, "3 warm-up calls + 20 timed calls"
    assert out["min"] <= out["p50"] <= out["p95"], "percentiles must be ordered"


def test_markdown_has_ratios_and_marks():
    rows = [R("base", 4000, 0.98, 1.0), R("small", 1000, 0.97, 0.5)]
    md = to_markdown(rows, "base", chosen=rows[1], front=rows)
    assert "| small | 1000 | 4.00 | 0.9700 | -0.0100 | 0.500 | 2.00 |" in md, "size x = 4000/1000 and speed x = 1.0/0.5"
    assert "chosen front" in md, "the chosen row is also on the front"
''', encoding="utf-8")
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_opt_kit.py"],
                     cwd=proj, capture_output=True, text=True, encoding="utf-8")
print(res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr[-400:])
if res.returncode:
    print(res.stdout[-1500:])
```
```text
12 passed in 0.46s
```

Two of these tests carry hand arithmetic worth re-reading. In `test_choose...`, the helper `R` sets the p95 to 1.5 times the p50, so `big` has p95 0.75 and `mid` has 0.6: with a limit of 0.65 only `mid` qualifies, with 0.5 nobody does. In `test_pareto_front...`, the tolerance changes the answer exactly as in section 8.1. A test whose expected value you did not derive by hand is a test that may be wrong in the same way as the code.

### 9.4 The driver: build, measure, decide, report

The driver imports the kit for everything that can be tested without PyTorch (pruning, parity, the Pareto front, the decision, the table) and uses PyTorch and ONNX Runtime only to build the variants. Every latency comes from a fresh process through `probe.py`.

```python run
(proj / "run_project.py").write_text(r'''"""Optimise the digits MLP and write artifacts/report.md and artifacts/results.json."""
import contextlib, json, os, pathlib, subprocess, sys, time, warnings

warnings.filterwarnings("ignore")
import numpy as np
import onnx, onnxruntime as ort
import torch, torch.nn as nn, torch.nn.functional as F
from onnxruntime.quantization import CalibrationDataReader, QuantFormat, QuantType, quantize_dynamic, quantize_static
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

from opt_kit import Row, choose, parity, pareto_front, prune_by_magnitude, to_markdown

HERE = pathlib.Path(__file__).parent
OUT = HERE / "artifacts"
OUT.mkdir(exist_ok=True)
MAX_ACC_DROP = 0.01          # requirement 1: at most one point below the baseline
ACC_TOL = 0.002              # one test image is 1/540 = 0.0019: smaller differences are noise

X, y = load_digits(return_X_y=True)
X = (X / 16.0).astype(np.float32)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)


def mlp(hidden):
    return nn.Sequential(nn.Linear(64, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, 10))


def train(model, epochs, lr=1e-3, seed=0, masks=None):
    torch.manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr)
    xt, yt = torch.from_numpy(Xtr), torch.from_numpy(ytr)
    for _ in range(epochs):
        perm = torch.randperm(len(xt))
        for i in range(0, len(xt), 64):
            idx = perm[i:i + 64]
            opt.zero_grad()
            F.cross_entropy(model(xt[idx]), yt[idx]).backward()
            opt.step()
            if masks:
                with torch.no_grad():
                    for j, m in masks.items():
                        model[j].weight.mul_(m)
    return model.eval()


def torch_fn(model):
    def f(x):
        with torch.inference_mode():
            return model(torch.from_numpy(x)).numpy()
    return f


def onnx_fn(path):
    sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    return lambda x: sess.run(None, {"x": x})[0]


def export(model, path):
    with open(os.devnull, "w", encoding="utf-8") as dn, contextlib.redirect_stdout(dn), contextlib.redirect_stderr(dn):
        torch.onnx.export(model, (torch.from_numpy(Xte[:1]),), str(path), input_names=["x"], output_names=["logits"],
                          dynamic_axes={"x": {0: "batch"}, "logits": {0: "batch"}}, external_data=False)
    return path


def quantise_file(src, dst, static=False):
    class Reader(CalibrationDataReader):
        def __init__(self):
            self.it = iter([{"x": Xtr[i:i + 1]} for i in range(200)])
        def get_next(self):
            return next(self.it, None)
    with open(os.devnull, "w", encoding="utf-8") as dn, contextlib.redirect_stdout(dn), contextlib.redirect_stderr(dn):
        if static:
            quantize_static(str(src), str(dst), Reader(), quant_format=QuantFormat.QDQ, weight_type=QuantType.QInt8,
                            activation_type=QuantType.QInt8, per_channel=True)
        else:
            quantize_dynamic(str(src), str(dst), weight_type=QuantType.QInt8)
    return dst


def measure(name, path, predict):
    """One Row. Latency from a fresh process, accuracy from this one."""
    out = subprocess.run([sys.executable, "-I", str(HERE / "probe.py"), str(path), "2", "1", "120"],
                         capture_output=True, text=True, timeout=300, encoding="utf-8")
    r = json.loads(out.stdout.strip().splitlines()[-1])
    return Row(name, pathlib.Path(path).stat().st_size / 1024, float((predict(Xte).argmax(1) == yte).mean()),
               r["p50"]["1"], r["p95"]["1"])


t0 = time.perf_counter()
print("[1/5] training the baseline (1024 units) and a small model (32 units)")
base = train(mlp(1024), epochs=30)
small = train(mlp(32), epochs=60)

print("[2/5] pruning 90% of the baseline weights, then fine-tuning with the mask")
pruned = mlp(1024)
pruned.load_state_dict(base.state_dict())
masks = {}
with torch.no_grad():
    for j, layer in enumerate(pruned):
        if isinstance(layer, nn.Linear):
            layer.weight.copy_(torch.from_numpy(prune_by_magnitude(layer.weight.numpy(), 0.9)))
            masks[j] = (layer.weight != 0).float()
pruned = train(pruned, epochs=5, lr=3e-4, seed=1, masks=masks)

print("[3/5] exporting to ONNX and quantising")
for name, model in (("base", base), ("small", small)):
    torch.save(model.state_dict(), OUT / f"{name}.pt")
torch.save(pruned.state_dict(), OUT / "pruned.pt")
base_onnx, small_onnx = export(base, OUT / "base.onnx"), export(small, OUT / "small.onnx")
base_dyn = quantise_file(base_onnx, OUT / "base_int8_dynamic.onnx")
base_sta = quantise_file(base_onnx, OUT / "base_int8_static.onnx", static=True)
small_dyn = quantise_file(small_onnx, OUT / "small_int8_dynamic.onnx")

print("[4/5] parity check of the float32 export")
par = parity(torch_fn(base)(Xte), onnx_fn(base_onnx)(Xte), atol=1e-4)
assert par["ok"], f"the ONNX export disagrees with PyTorch: {par}"

print("[5/5] measuring every variant in a fresh process")
rows = [measure("torch float32", OUT / "base.pt", torch_fn(base)),
        measure("torch small (32 units)", OUT / "small.pt", torch_fn(small)),
        measure("torch pruned 90%", OUT / "pruned.pt", torch_fn(pruned)),
        measure("ort float32", base_onnx, onnx_fn(base_onnx)),
        measure("ort int8 dynamic", base_dyn, onnx_fn(base_dyn)),
        measure("ort int8 static", base_sta, onnx_fn(base_sta)),
        measure("ort small int8", small_dyn, onnx_fn(small_dyn))]

baseline = rows[0]
front = pareto_front(rows, acc_tol=ACC_TOL)
chosen = choose(rows, min_acc=baseline.acc - MAX_ACC_DROP, max_p95_ms=baseline.p95_ms)

lines = ["# Optimisation report: digits MLP", "",
         f"Requirement: accuracy within {MAX_ACC_DROP:.2f} of the baseline, p95 latency no worse than the baseline, "
         "smallest file wins. Latency is measured in a fresh process with 2 threads, batch size 1.", "",
         to_markdown(rows, baseline.name, chosen=chosen, front=front), "",
         f"Parity of the float32 export: max |torch - onnx| = {par['max_abs_diff']:.2e}, same classes: {par['same_classes']}.", ""]
if chosen is None:
    lines.append("Decision: no variant meets the requirement.")
else:
    lines.append(f"Decision: ship **{chosen.name}**. It is {baseline.size_kb / chosen.size_kb:.2f}x smaller, "
                 f"{baseline.p50_ms / chosen.p50_ms:.2f}x faster at p50, and its accuracy changes by {chosen.acc - baseline.acc:+.4f} "
                 f"({chosen.acc:.4f} against {baseline.acc:.4f}).")
report = "\n".join(lines)
(OUT / "report.md").write_text(report + "\n", encoding="utf-8")
(OUT / "results.json").write_text(json.dumps([r.__dict__ for r in rows], indent=2), encoding="utf-8")
print(f"\n(total {time.perf_counter() - t0:.0f} s)\n")
print(report)
''', encoding="utf-8")
t0 = time.perf_counter()
res = subprocess.run([sys.executable, "run_project.py"], cwd=proj, capture_output=True, text=True, timeout=900, encoding="utf-8")
print(res.stdout if res.returncode == 0 else res.stderr[-2000:])
```
```text
[1/5] training the baseline (1024 units) and a small model (32 units)
[2/5] pruning 90% of the baseline weights, then fine-tuning with the mask
[3/5] exporting to ONNX and quantising
[4/5] parity check of the float32 export
[5/5] measuring every variant in a fresh process

(total 44 s)

# Optimisation report: digits MLP

Requirement: accuracy within 0.01 of the baseline, p95 latency no worse than the baseline, smallest file wins. Latency is measured in a fresh process with 2 threads, batch size 1.

| variant | size KB | size x | acc | d acc | p50 ms | p50 x | p95 ms | note |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| torch float32 | 4403 | 1.00 | 0.9796 | +0.0000 | 0.288 | 1.00 | 0.352 |  |
| torch small (32 units) | 16 | 273.08 | 0.9648 | -0.0148 | 0.052 | 5.52 | 0.058 |  |
| torch pruned 90% | 4403 | 1.00 | 0.9556 | -0.0241 | 0.251 | 1.15 | 0.273 |  |
| ort float32 | 4407 | 1.00 | 0.9796 | +0.0000 | 0.353 | 0.82 | 0.545 |  |
| ort int8 dynamic | 1113 | 3.96 | 0.9796 | +0.0000 | 0.096 | 2.99 | 0.124 | chosen front |
| ort int8 static | 1140 | 3.86 | 0.9796 | +0.0000 | 0.213 | 1.36 | 0.246 |  |
| ort small int8 | 10 | 434.95 | 0.9667 | -0.0130 | 0.038 | 7.53 | 0.046 | front |

Parity of the float32 export: max |torch - onnx| = 3.81e-06, same classes: True.

Decision: ship **ort int8 dynamic**. It is 3.96x smaller, 2.99x faster at p50, and its accuracy changes by +0.0000 (0.9796 against 0.9796).
```

How to read the report: the table is the "before and after", the `front` mark shows which variants survive domination, and the decision line is the single sentence that goes into a ticket or a pull request. Notice what the project proves about this chapter:

- The **ONNX float32** export keeps the accuracy exactly and passes the parity check; its batch-1 speed is within the noise of PyTorch for this tiny model (section 5.6), though it has the better throughput.
- **int8** (dynamic) gives roughly 4x in size, a clear gain in speed, and no visible accuracy change on this task.
- **The 90 % pruned model** is not smaller or faster, and in this run a five-epoch fine-tune left it about two points below the baseline: it sits in the table to show the result of section 4.3 in your own measurements.
- The **small architecture** is the extreme on size and speed, and costs a measurable amount of accuracy that may or may not be acceptable: *you* decide with the requirement.

### 9.5 Extensions

1. **Add a requirement for memory.** Use the probe's `rss_mb` to reject any variant above a RAM limit, and see how the decision changes between 1 and 4 threads.
2. **Gradual pruning.** Prune 50 %, fine-tune, prune 75 %, fine-tune, then 90 %. Does it beat one-shot 90 % at the same fine-tuning budget?
3. **QAT to 4 bits.** Reuse `qat_finetune` from section 3.4 and add a 4-bit row (fake quantised, so only accuracy is meaningful). What accuracy does the file format need to preserve?
4. **A second dataset.** Swap in a harder task (for example the 20-newsgroups features, or a convolutional model on the digits as 8x8 images with `Conv2d`) and look at where the quantisation cliff moves.
5. **Statistical honesty.** Retrain the baseline with five seeds and report each accuracy as mean plus or minus its spread, so that an accuracy change of 0.002 can be called signal or noise.
6. **Serve it.** Put the chosen ONNX file behind the FastAPI service of ml.06, with the micro-batcher of section 6.3, and measure end-to-end p95 under load.

## 10. Common traps

1. **Optimising without a requirement** (1.1). Without "p95 under 20 ms" or "under 10 MB" you cannot tell when to stop.
2. **Timing one call, or the first call** (2.2). Warm up, repeat, report median and p95.
3. **Believing a difference smaller than the run-to-run spread** (2.3). Know your noise floor; interleave candidates.
4. **Benchmarking two runtimes in one long-lived process** (5.6). Thread pools interfere; measure in a fresh process.
5. **Trusting a difference of 0.002 accuracy on 540 test images** (3.3, 8.1). One image is 0.0019.
6. **Rounding below the cliff** (3.3). 8 bits is almost free, 2 bits collapses. Find the cliff for your model and stay above it, or use QAT (3.4).
7. **One outlier weight ruining a per-tensor scale** (3.2). Use per-channel scales.
8. **Static quantisation with unrepresentative calibration data** (3.5): values clip silently in production.
9. **Expecting speed from size** (3.6). Fewer bytes are guaranteed; faster arithmetic depends on the hardware's int8 or half-precision support.
10. **Pruning without a sparse format or runtime** (4.3). Zeros are stored and multiplied like any other number. Structured pruning, or a smaller architecture, is what actually shrinks a dense model.
11. **Never asking whether the model was simply too big** (4.4). Try the smaller architecture first.
12. **Forgetting `external_data`** (5.2): shipping a 7 KB `.onnx` without its weights file, or reporting its size as the model size.
13. **A frozen batch dimension** (5.5). Export with `dynamic_axes` and test with a different batch size.
14. **No parity check after a conversion** (5.4). Compare max difference and predicted classes after every export and quantisation.
15. **Preprocessing outside the artifact** (5.9). Put deterministic steps in the graph and add golden-example tests.
16. **Batching without a `max_wait` budget, or with an unbounded queue** (6.3). Latency suffers at low load; memory and latency explode at overload. Deliver exceptions to waiting callers, and shed load.
17. **Judging an edge device by your laptop** (7.2, 7.6). Measure on the target, cold and warm; remember the runtime's own memory.
18. **Optimising a model nobody monitors** (ml.06). A compressed model can drift or break on real inputs differently from the original: keep monitoring after the optimisation.

## 11. Summary

- **Optimisation trades size, latency and accuracy.** Start from a requirement, measure the baseline, and report ratios on the same machine: "4x smaller, 1.7x faster, accuracy -0.001".
- **Measure honestly**: warm-up, many repeats, median and p95, a noise floor, interleaved candidates, and a **fresh process** per measurement. Latency is for one request, throughput for the machine; batch size moves between them.
- **Quantisation** stores integers plus a scale (`x = q * scale`, error at most half a step). Per-channel scales contain outliers; 8 bits is nearly free, a cliff waits at low bit widths, and **QAT** (rounding in the forward pass, identity in the backward) rescues the extreme cases. Dynamic quantisation needs no calibration; static fixes activation ranges from calibration data.
- **Pruning** zeros weights; accuracy needs **fine-tuning with the mask**; but **unstructured sparsity does not shrink dense files or speed up dense kernels**. **Structured** pruning and **smaller architectures** do. Distillation is a tool, not a guarantee.
- **ONNX** freezes the model into a graph; verify with a **parity check**, export with dynamic batch axes, keep the weights with the file, put preprocessing inside the graph, and let **ONNX Runtime** fuse operations. Choose thread counts by measurement.
- **Batching** shares the fixed cost per call: a micro-batcher (queue, deadline, one model call, one future per request) turns overload into survivable latency; at low traffic, waiting only hurts.
- **Small devices** are constrained by RAM, storage, cold start, power and the runtime's own footprint, not only by the model's size. Measure on the device.
- **Decide with a table and a Pareto front** and a stated requirement; keep a tolerance for noise; report what was given up.

**Self-check (answer without looking back):**

1. A float32 model has 8 million parameters. What is its approximate size in float32, float16 and int8? Which of those sizes will you actually *measure* in a file, and why might it be slightly larger?
2. Why is the rounding error of symmetric quantisation at most `scale / 2`, and why does one huge weight hurt a per-tensor scheme but much less a per-channel scheme?
3. A teammate prunes 90 % of the weights and says the model is 10x faster. List the measurements you would ask for.
4. You export a model to ONNX and the parity check shows a maximum difference of 2e-6 and identical predicted classes. Is the export correct? What would a maximum difference of 0.4 tell you?
5. Under what traffic conditions does dynamic batching reduce latency, and under what conditions does it only add delay?
6. Your quantised model is 4x smaller on disk, but the process memory fell by only 5 MB out of 80 MB. Explain.
7. Two variants differ by 0.0015 in accuracy on a 540-image test set. How would you decide whether the difference is real?

<details><summary>Answer</summary>

1. float32: 8M x 4 = 32 MB; float16: 16 MB; int8: 8 MB. A saved file is slightly larger than the raw weights because of names, biases and format overhead (about 3 KB for a 4.4 MB file in this chapter), plus the per-channel scales and the int8 file's graph nodes.
2. Rounding goes to the nearest grid point and grid points are `scale` apart, so the error is at most half a step. The scale is set by the largest absolute value, so one outlier stretches the grid for every weight in the tensor; per-channel scales confine the outlier to its own row.
3. File size (and format: is it stored sparse or compressed?), latency on the target hardware with the runtime used in production (is there a sparse kernel?), batch size, accuracy on held-out data after fine-tuning, and the noise floor of the timing. Dense kernels multiply zeros like any other number.
4. A difference around 1e-6 is float reordering noise and identical classes mean the answers agree: the export is faithful for these inputs (also try other batch sizes and edge inputs). A maximum difference of 0.4 is a bug: a layer left in training mode, a missing preprocessing step, an unsupported operator replaced by something different.
5. It reduces latency when the server is busy: requests queue up and taking everything waiting amortises the fixed cost per call, so the queue drains faster (the 0.9x and 1.5x loads in 6.2). At low traffic there is nothing to share, and waiting for neighbours only adds delay.
6. The file is only part of the memory: the runtime and its libraries are a fixed cost, and the session keeps extra copies and buffers (for example pre-packed weights). Shrinking the weights shrinks only the weight part. Changing the runtime or loading weights lazily (memory-mapping) changes the rest.
7. 0.0015 is less than one image (0.0019), so on this test set it is not even measurable. Use a bigger test set, several seeds, or a paired comparison (count the images where the two variants disagree and who is right); only then call the difference real.

</details>
