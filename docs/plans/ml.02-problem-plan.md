# Problem plan: ml.02 PyTorch (40 problems)

Rules: [README.md](README.md), table format of [dsa.07-problem-plan.md](dsa.07-problem-plan.md), **ml track notes M1–M5 in
[ml.01-problem-plan.md](ml.01-problem-plan.md)**. Function style. Ids `ml.02.p001`…`p040`.
**Mix:** 15 drill, 14 applied, 8 deep, 3 challenge. **Kinds:** 30 code, 7 trace, 3 explain.
**assessment:** explain = p034, trace = p037, fix = p033, build = p040.
**★ core set (16):** p1, p8, p10, p13, p15, p21, p22, p25, p26, p31, p32, p33, p34, p36, p37, p40.

## Testing notes

- torch only (+ NumPy). **No sklearn, pandas or scipy in any test or solution** (M1: torch + sklearn + an optimiser exceeds the cap).
  Accuracy, confusion matrix and recall are computed in torch. Images: `fixtures/digits.npz` loaded by the test (M3).
- `conftest.py` per M2; `torch.manual_seed` and `torch.set_num_threads(1)` in a fixture.
- Measured: small CNN, 200 steps, ~0.7 s per seed, test accuracy 0.91–0.95 on 3 seeds (M4). Training tests use ≤ 300 steps.
- Exact-resume test (p26) compares with `torch.equal`; it is exact on CPU with one thread and the same data order (seeded `Generator`).
  If it ever flakes on another CPU, relax to `allclose(atol=1e-6)` and say so in the message.
- Reuse the chapter's names: `MLP(sizes, dropout)`, `DigitImages`, `pad_collate`, `run_epoch`, `fit`, `seed_everything`,
  `conv2d_naive`, `SmallCNN`, `diagnose`, `Config`, `train_model`, `evaluate`, `save_artifact`, `Predictor`.

## A. Tensors (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | From uint8 pixels to a float batch | drill | code | `to_batch(X_uint8)` → float32 `(N, 1, 8, 8)` scaled to [0, 1]; dtype and shape messages; the input array is not modified |
| 2 | Views, copies and `contiguous` | drill | trace | `⚠ HAND-TRACE` `view`, `reshape`, `t()`, `clone()` and an in-place `add_`; print `.tolist()` and `is_contiguous()` |
| 3 | Broadcasting without loops | drill | code | `standardise(x, dim)` with `keepdim`; `pairwise_sq_dists(a, b)` equals a double loop on small inputs |
| 4 | The NumPy bridge shares memory | applied | trace | `⚠ HAND-TRACE` `torch.from_numpy` vs `torch.tensor` after changing the array; print both `.tolist()` |

## B. Autograd (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Gradients accumulate | drill | trace | `⚠ HAND-TRACE` two `backward()` calls without zeroing; print `w.grad` after each and after `grad = None` |
| 6 | Let autograd do ml.01's work | drill | code | `grads(params, X, y)` for the ml.01 2-layer net via autograd; equals the hand formula given in the test |
| 7 | `no_grad` for a moving average | applied | code | `ema_update(target, online, tau)` under `torch.no_grad()`; target values right; no graph on target; online grads untouched |
| 8 | A custom `autograd.Function` | deep | code | `ClampSTE` (forward clamps, backward passes the gradient inside the range, 0 outside); `gradcheck` on float64 points away from the edges |
| 9 | Things autograd cannot see | deep | explain | `.item()`, NumPy round-trips, in-place on a leaf, `detach`; checklist of 4 cases with what breaks |

## C. `nn.Module` (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | An MLP module | drill | code | `MLP(sizes, dropout)`; parameter count; output shape; layers registered (a plain Python list hides parameters: the count catches it) |
| 11 | Parameters and buffers | applied | code | a `RunningMean` module with `register_buffer`; buffer in `state_dict`, not in `parameters()`; updates only in train mode |
| 12 | `train()` and `eval()` | drill | trace | `⚠ HAND-TRACE` `.training` of each submodule after `model.eval()` then `model.head.train()`; whether two eval forwards are equal |
| 13 | Loss conventions | applied | code | `loss_for(task, logits, target)`: CrossEntropy on raw logits with long targets, BCEWithLogits with float targets of the same shape; raises on `(N, 1)` vs `(N,)` instead of broadcasting |
| 14 | Forward hooks | applied | code | `activation_stats(model, x)` → {layer name: (mean, std)} via hooks; all hooks removed afterwards (`_forward_hooks` empty) |

## D. Data (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | A `Dataset` with a transform | drill | code | `DigitImages(X, y, augment, seed)`: `len`, item shapes and dtypes, augmentation only when asked, same seed same item |
| 16 | Reproducible shuffling | applied | code | `make_loader(ds, batch, seed)` with a `torch.Generator`; same seed same order, different seed different; last batch size; `drop_last` |
| 17 | `collate_fn` for sequences | applied | code | `pad_collate(batch)` → padded tensor, lengths, labels; pad value 0; lengths unsorted kept in order |
| 18 | Sampling for imbalance | deep | code | weights for `WeightedRandomSampler` from labels; over 2,000 draws the positive share is 0.5 ± 0.05 when the data have 10% |

## E. Optimisers, schedulers, clipping (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Learning rate per step | drill | trace | `⚠ HAND-TRACE` `StepLR(step_size=2, gamma=0.5)` for 6 steps, `optimizer.step()` before `scheduler.step()`; print the lr (`:.4f`) |
| 20 | Clip, then step | applied | code | `clip_and_step(model, opt, max_norm)` returns the pre-clip norm; total norm after ≤ max_norm (+1e-6); no clip when below |

## F. The training loop (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 21 | The loop from memory | applied | code | `run_epoch(model, loader, loss_fn, optimizer=None)` → (mean loss, accuracy) weighted by batch size; evaluation runs in eval mode with no grad; checked on a fixed model with hand-computable loss |
| 22 | `fit` with early stopping | deep | code | restores the best weights (equal to a deep copy saved at the best epoch); digits accuracy ≥ 0.80 on 3 seeds within 300 steps |
| 23 | Gradient accumulation | deep | code | k micro-batches give the same gradient as one big batch (float64, `allclose` 1e-10); the message names the missing `/ k` |
| 24 | Evaluation beyond accuracy | drill | code | `confusion(pred, y, n)` and per-class recall in torch; equals a Python loop; a class never predicted gives recall 0, not `nan` |

## G. Saving and resuming (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Save the state, not the object | drill | code | `save(model, path)` / `load(path, sizes)` with `state_dict` in `tmp_path`; same predictions; wrong architecture raises with a clear message |
| 26 | Resume exactly | challenge | code | checkpoint model, optimiser, scheduler and generator state at epoch 3; resume to epoch 6 gives weights `torch.equal` to an uninterrupted run |

## H. Devices, speed, reproducibility (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Device-agnostic helpers | drill | code | `to_device(obj, device)` recursively for tensors in dict/list/tuple (non-tensors untouched); `pick_device()` with `torch.cuda.is_available` monkeypatched returns `"cuda"`/`"cpu"` |
| 28 | Never loop over examples | applied | code | `batch_predict(model, X)` equals per-row predictions and runs 10,000 rows in < 0.5 s; the starter loops |
| 29 | `seed_everything` | drill | code | same seed → identical init and identical first batch; different seeds differ |

## I. Convolutional networks (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 30 | Shapes through a CNN | drill | trace | `⚠ HAND-TRACE` 1×8×8 input through conv3 pad1 → pool2 → conv3 → pool2 → flatten; print each shape |
| 31 | A convolution by hand | applied | code | `conv2d_naive(img, kernel)` equals `F.conv2d` (cross-correlation, kernel not flipped); padding 0 |
| 32 | `SmallCNN` on the digits | applied | code | `SmallCNN(channels, n_classes, dropout)`; trained by the test with its own loop; accuracy ≥ 0.80 on 3 seeds; parameter count below a stated budget |

## J. Debugging training (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 33 | Fix the training loop | applied | code | `assessment = "fix"`; the given loop never calls `optimizer.zero_grad()`; the test records each step's gradient with a hook and compares it with a fresh backward on the same batch; plus accuracy ≥ 0.80 |
| 34 | Symptom to bug | deep | explain | `assessment = "explain"`; six training stories in words (loss `nan`, stuck at ln 10, train ≫ val, oscillating per batch, early layers frozen, slow and worse) → the bug and the check that finds it; checklist from Ch. 10.2 |
| 35 | A pre-flight check | challenge | code | `preflight(model, loader, n_classes)` → list of flags (initial loss far from ln C, parameters without grad, unnormalised inputs, labels out of range, single-class batches); 5 broken setups each raise exactly their flag |
| 36 | Overfit one batch | drill | code | `can_overfit(model, xb, yb, steps)` → True when the loss falls below 0.05; a model with `.detach()` inside returns False |
| 37 | Which parameters got a gradient? | deep | trace | `assessment = "trace"`; `⚠ HAND-TRACE` a model with `.detach()` after layer 2 and a frozen bias; print each parameter name and whether `.grad is None` |
| 38 | Unnormalised inputs | deep | explain | why ×50 inputs give a huge initial loss and unstable steps; what normalising with training statistics fixes; checklist of 3 points |

## K. Project: an image classifier end to end (Ch. 11)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 39 | The deployable artefact | applied | code | `save_artifact(model, cfg, mean, std, path)`; `Predictor.load(path).predict(uint8 images)` applies the same normalisation; predictions equal the in-memory model |
| 40 | Build: image classifier end to end | challenge | code | `assessment = "build"`; `train_model(cfg, data)`, `evaluate`, `Predictor`; tests from Ch. 11.3: output shape, every parameter gets a gradient, initial loss ≈ ln 10, overfit one batch, eval deterministic, batched = single, seeds, splits disjoint and normalisation from training data only; accuracy ≥ 0.85 |

## Counts check

Tiers: drill 1, 2, 3, 5, 6, 10, 12, 15, 19, 24, 25, 27, 29, 30, 36 = 15; applied 4, 7, 11, 13, 14, 16, 17, 20, 21, 28, 31, 32, 33, 39 = 14;
deep 8, 9, 18, 22, 23, 34, 37, 38 = 8; challenge 26, 35, 40 = 3. Total 40.
Trace (7): 2, 4, 5, 12, 19, 30, 37. Explain (3): 9, 34, 38. Code: 30. Fewer explain than the usual 5 because the debugging outcome is
tested better by code (p33, p35, p36); add p27 as an explain variant ("why `.to(device)` returns a new tensor for tensors but not modules") if wanted.

## Risks and open questions

- p40 trains in the test: keep it ≤ 300 steps and one seed for the accuracy check (~1 s), 3 seeds only for the cheap checks.
- p26 exactness depends on deterministic CPU kernels; verify on Windows if possible.
- p28 timing thresholds: use a ratio against the vectorised reference measured in the same test, not an absolute time, if 0.5 s flakes.
