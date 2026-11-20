# Problem plan: ml.01 Deep learning fundamentals (40 problems)

Rules: [README.md](README.md) (shared rules R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ml.01.p001`…`p040`, folder `pNNN-slug`.
**Mix:** 14 drill, 14 applied, 9 deep, 3 challenge. **Kinds:** 28 code, 8 trace, 4 explain.
**assessment:** explain = p022, trace = p018, fix = p021, build = p040.
**★ core set (write first, 16):** p1, p5, p6, p9, p10, p13, p18, p19, p20, p21, p22, p23, p29, p33, p35, p40.

## Track notes for every ml plan (measured 2026-11-18 under the runner's limits)

These apply to ml.01–ml.07; each later plan points here. Measured with the course venv (Python 3.14, torch 2.x CPU),
`ulimit -v 1048576`, `MALLOC_ARENA_MAX=2 OMP_NUM_THREADS=2` (the runner's settings).

- **M1. torch and the 1 GiB address-space cap.** The cap limits *virtual* memory (VmPeak), not RSS. Measured VmPeak:
  `import torch` 626 MB; torch + creating any optimiser (`Adam`/`SGD` lazily import `torch._dynamo` → `sympy`) 721 MB;
  + onnxruntime 827 MB; + fastapi TestClient 783 MB; + pandas 974 MB; + scipy 899 MB; + transformers + peft + tiny BERT 994 MB;
  **+ any sklearn import 1.10 GB → MemoryError; + mlflow 1.26 GB → MemoryError; + `datasets` (pyarrow) → "failed to map segment".**
  The error shows at `Adam(...)` or at an unrelated import, which is very confusing for a learner.
  Rule: **a test file that imports torch never imports sklearn, scipy, mlflow, `datasets` or pandas** (and the solution may not either;
  say so in `problem.md`). NumPy is fine. Metrics (accuracy, confusion matrix, F1) are written in torch/NumPy in ml tests.
- **M2. `conftest.py` for every ml problem** (first lines, before any import of numpy):
  `os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")`, `HF_HUB_OFFLINE=1`, `TOKENIZERS_PARALLELISM=false`, `MLFLOW_DISABLE_AGENT_HINT=1`;
  and a fixture calling `torch.set_num_threads(1)` when torch is used. Measured: importing sklearn and then torch fails under the
  runner's env (OpenBLAS sizes its buffers by thread count); the same pytest run passes with this conftest.
- **M3. Digits data without sklearn.** Ship `fixtures/digits.npz` (45 KB: `X` uint8 (1797, 64) values 0–16, `y` uint8), made once with
  `np.loadtxt(<sklearn>/datasets/data/digits.csv.gz, delimiter=",")`. The test loads it with NumPy and passes tensors to the solution (R1).
  Synthetic tensors are the other source. torchvision is not installed.
- **M4. Measured speeds (1 thread):** small CNN (conv 1→8→16, pool, linear) on digits, 200 Adam steps batch 32: ~0.7 s per seed,
  test accuracy 0.947 / 0.907 / 0.917 on seeds 0/1/2 (split 1400/397) → safe threshold **0.80**. Tiny GPT (C=32, 2 heads, 2 layers, T=16)
  overfitting a 64-character text, 300 AdamW steps: ~2.4 s per seed, final loss 0.09 / 0.12 / 0.09 → threshold **0.3**.
- **M5.** Never hard-code a trained loss or accuracy. Check shapes, gradients (finite differences in float64, or
  `torch.autograd.gradcheck` on float64 inputs), loss decrease, "can overfit one batch", thresholds with margin on 3 seeds.

## Testing notes for ml.01

- **NumPy only.** The chapter uses PyTorch only as an optional "referee"; problems never need torch. sklearn is allowed here
  (`make_moons`, `make_circles`, `load_digits`) because torch is not imported (M1).
- Gradients are checked by central finite differences in float64 (`eps=1e-6`, relative error < 1e-6 for exact code,
  < 1e-4 when ReLU kinks are possible: keep test inputs away from 0 for ReLU).
- Reuse the chapter's names: `init_params`, `forward`, `softmax`, `cross_entropy_with_logits`, `numerical_grad`, `Optimizer/SGD/Adam`
  (`step(grads)` updates in place), `MLP(sizes, act, init, seed)`, `Value`, `Tensor`, `unbroadcast`, `Linear/Activation/Dropout/BatchNorm1d/Sequential`.

## A. From a linear model to a network (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Forward pass of a 2-layer network | drill | code | `forward(X, params, act)`; a 2×2 example worked by hand in the test; a batch of 5 equals 5 single rows stacked; output shape `(N, out)` |
| 2 | Why XOR needs a hidden layer | drill | explain | composition of linear maps is linear; a non-linearity bends the boundary; checklist: "linear boundary", "composition", "activation" |
| 3 | One neuron by hand | drill | trace | `⚠ HAND-TRACE` w = [0.5, -1], b = 0.25, three input rows; print `z` and `relu(z)` with `:.3f` |
| 4 | Count the parameters | drill | code | `n_params(sizes)`; [2, 8, 1] → 33; [784, 128, 10] → 101,770; one-layer list → 0 |

## B. Activation functions (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Activations and their derivatives | drill | code | sigmoid, tanh, relu, leaky_relu and `d_*`; each derivative checked by finite differences at 50 points; `sigmoid(±1000)` with `np.errstate(over="raise")` must not raise |
| 6 | Stable softmax | drill | code | rows sum to 1; `[1000, 1001]` gives no `nan`; adding a constant to a row changes nothing; works on 1-D and 2-D |
| 7 | Saturation in numbers | applied | trace | `⚠ HAND-TRACE` sigmoid derivative at z = 0, 2, 5, 10 (`:.4f`) and the product through 5 layers at z = 2 (`:.2e`) |
| 8 | Find the dead ReLU units | applied | code | `dead_units(H)` = fraction of hidden units that are 0 on every row; a layer with bias −10 gives 1.0; message: "a unit is dead only if it is zero for EVERY example" |

## C. Loss functions (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Cross-entropy from logits | drill | code | mean loss via log-sum-exp; logits of 1e3 give a finite number; equals `-log(softmax)[y]` on small inputs |
| 10 | The gradient is softmax minus one-hot | applied | code | `ce_grad(z, y)` = (softmax − one_hot) / N; finite differences on every entry; message names the missing `/ N` |
| 11 | The initial loss tells you something | drill | trace | `⚠ HAND-TRACE` loss with all-zero logits for 2, 10 and 100 classes (`ln C`, `:.3f`), and with one confident wrong logit |
| 12 | Huber against MSE on an outlier | applied | code | `huber(pred, y, delta)` and its gradient; with one outlier of 100 the Huber gradient is bounded by `delta / N`, the MSE one is not |

## D. Optimisers and schedules (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | SGD with momentum | drill | code | the chapter's `Optimizer` interface (`step(grads)` updates arrays in place); 3 steps on f(w) = w² worked by hand; `momentum=0` equals plain SGD; the same array objects are updated (no rebinding) |
| 14 | Two Adam steps by hand | applied | trace | `⚠ HAND-TRACE` w = 1, gradients 0.5 then 0.25, lr = 0.1, default betas: print m, v, m̂, v̂, w after each step (`:.5f`); first step ≈ lr |
| 15 | Adam from scratch | deep | code | `Adam(params, lr, betas, eps, weight_decay)` (decoupled decay) equals a slow dict-based version in the test over 50 steps on 3 arrays (tolerance 1e-12) |
| 16 | Learning-rate schedules | drill | code | `step_decay`, `cosine`, `warmup_cosine`; values at t = 0, warm−1, warm, T; non-increasing after warm-up |
| 17 | Batch size and noise | deep | explain | why small batches give noisy steps; what that noise can buy; why the learning rate moves with batch size; checklist of 4 points |

## E. Backpropagation (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 18 | Backpropagate a 2-2-1 network by hand | applied | trace | `assessment = "trace"`; `⚠ HAND-TRACE` given weights (different from Ch. 6.2), one input, tanh hidden, squared error: print every forward value and dL/dW2, dL/db2, dL/dW1, dL/db1 (`:.4f`); the code printing them is in `problem.md` |
| 19 | A gradient checker | drill | code | `grad_check(f, params, eps)` → max relative error; catches a planted wrong gradient (> 1e-3), passes a right one (< 1e-6); every param array is unchanged afterwards |
| 20 | Backward for an MLP | deep | code | `MLP.backward(dlogits)` for relu and tanh; finite differences on every parameter (rel. error < 1e-6, float64); grad shapes equal param shapes |
| 21 | Fix the bias gradient | applied | code | `assessment = "fix"`; given backward averages the bias gradient over the batch although the loss is already divided by N (`db = dout.mean(0)`); training "works" but slowly; the gradient check fails with a factor of N; message points at it |
| 22 | Why backpropagation and not numerical gradients | deep | explain | `assessment = "explain"`; cost of backprop ≈ a small multiple of one forward pass, numerical gradients 2P forward passes; why we still keep the numerical check; checklist: "chain rule", "reuse", "2P passes", "gradient check" |

## F. A tiny autograd engine (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | `Value`: add, mul, backward | drill | code | topological order; `a*a` gives grad 2a (gradients accumulate with `+=`); a node used in two branches |
| 24 | More operations for `Value` | applied | code | pow, tanh, exp, log, relu; sub, div, neg built from existing ops; `2 + v`, `2 * v` work; 10 expressions checked by finite differences |
| 25 | The order of backward | applied | trace | `⚠ HAND-TRACE` for `e = (a*b + c) * a` with labels, print the order backward visits the nodes and every grad |
| 26 | `unbroadcast` | deep | code | sums over broadcast axes: (4,3)→(3,), (4,3)→(1,3), (4,3)→(), (2,1,3)→(1,3); checked inside the Tensor engine by finite differences |
| 27 | A NumPy `Tensor` with matmul | deep | code | `__matmul__`, `relu`, `sum`, fused `cross_entropy` backward; gradients equal the hand-written `MLP` of p20 on the same weights |
| 28 | Overwrite instead of accumulate | deep | trace | `⚠ HAND-TRACE` print `x.grad` for `y = x*x + x` with a backward that writes `=` instead of `+=`, then with the fix |

## G. Training, initialisation, regularisation, batch norm (Ch. 8–11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | A training loop on two moons | applied | code | `train(net, X, y, Xv, yv, ...)` returns a history; `make_moons(noise=0.2)`: validation accuracy ≥ 0.90 on 3 seeds, beats the majority baseline, loss falls in the first 20 epochs |
| 30 | Xavier and He initialisation | drill | code | `init_weight(fan_in, fan_out, rule, rng)`; std within 5% of the formula on a 1000×1000 matrix; activations through 20 ReLU layers stay within [0.5, 2]× with He and collapse with std 0.01 |
| 31 | Variance through three layers | applied | trace | `⚠ HAND-TRACE` formula only (no randomness): output variance after each of 3 layers given fan-in, weight std and activation gain (`:.3f`) |
| 32 | Weight decay is not L2 in Adam | deep | code | `adam_first_step(w, g, lr, wd_decoupled)` against L2 added to the gradient; two hand-computed cases where they differ |
| 33 | Inverted dropout | applied | code | train mode keeps the mean (over 10⁵ values, ±1%); backward uses the same mask; eval mode is the identity; p = 0 is the identity |
| 34 | Early stopping with the best weights | drill | code | `early_stop(val_losses, patience)` → (stop epoch, best epoch); ties keep the earlier; patience 0 |
| 35 | BatchNorm1d forward and backward | challenge | code | running mean/var with momentum; eval uses running stats; backward by finite differences (rel. error < 1e-5); batch of 1 in train mode raises `ValueError` |
| 36 | When batch norm misleads you | deep | explain | train/eval mismatch, tiny batches, why layer norm exists; checklist of 4 points |

## H. Debugging (Ch. 12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 37 | Diagnose a network that will not learn | challenge | code | `diagnose(net, X, y)` → dict of checks (initial loss ≈ ln C, can overfit 20 examples, every grad non-zero, update/weight ratio ≈ 1e-3); four broken nets in the test (lr = 10, shuffled labels, all-zero init, no non-linearity) each raise the right flag |
| 38 | Hidden units that are copies | applied | code | `hidden_copies(net)` counts identical hidden columns; constant init gives all copies after training, He init gives 0 |

## I. Project: a NumPy neural-network library (Ch. 13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 39 | Save and load the library's state | applied | code | `save_state(net, path)` / `load_state(net, path)` with `np.savez` into `tmp_path`; predictions identical; a wrong shape raises `ValueError` naming the layer |
| 40 | Build: a NumPy NN library | challenge | code | `assessment = "build"`; `Linear, ReLU, Tanh, Dropout, BatchNorm1d, Sequential`, `SGD`, `Adam`, `train`; tests like Ch. 13.3: gradient check per layer, overfit one batch, initial loss ≈ ln 10, digits accuracy ≥ 0.90 on 2 seeds (`load_digits`, NumPy only, ≤ 15 s) |

## Counts check

Tiers: drill 1, 2, 3, 4, 5, 6, 9, 11, 13, 16, 19, 23, 30, 34 = 14; applied 7, 8, 10, 12, 14, 18, 21, 24, 25, 29, 31, 33, 38, 39 = 14;
deep 15, 17, 20, 22, 26, 27, 28, 32, 36 = 9; challenge 35, 37, 40 = 3. Total 40.
Trace (8): 3, 7, 11, 14, 18, 25, 28, 31. Explain (4): 2, 17, 22, 36. Code: 28. One of each assessment: 22, 18, 21, 40.

## Risks and open questions

- p29/p40 use sklearn datasets: fine here (no torch), but check the whole test file stays under 20 s on the reference.
- ReLU kinks make finite differences flaky: build test inputs with `|z| > 1e-3` for every pre-activation (assert it in the test helper).
- p37 depends on exact thresholds for "≈": state them in `problem.md` (e.g. |initial loss − ln C| < 0.3).
