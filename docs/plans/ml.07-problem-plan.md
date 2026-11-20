# Problem plan: ml.07 Model optimisation and deployment (20 problems)

Rules: [README.md](README.md), table format of [dsa.07-problem-plan.md](dsa.07-problem-plan.md), **ml track notes M1–M5 in
[ml.01-problem-plan.md](ml.01-problem-plan.md)**. Function style. Ids `ml.07.p001`…`p020`.
**Mix:** 7 drill, 7 applied, 4 deep, 2 challenge. **Kinds:** 14 code, 4 trace, 2 explain.
**assessment:** explain = p011, trace = p006, fix = p015, build = p020.
**★ core set (8):** p2, p5, p6, p10, p11, p14, p15, p20.

## Testing notes

- torch + onnx + onnxruntime (VmPeak 827 MB with an optimiser, M1). No sklearn. Digits from `fixtures/digits.npz` (M3) when a trained
  model is needed; most problems use NumPy arrays or a tiny untrained model.
- Measured in this session: legacy export `torch.onnx.export(model, (x,), buf, input_names=["x"], output_names=["y"],
  dynamic_axes={"x": {0: "n"}}, dynamo=False)` + `onnxruntime.InferenceSession(buf.getvalue())` + `quantize_dynamic` on Linear layers:
  2.8 s, 293 MB RSS. **Without `dynamic_axes`, a batch of 3 fails:** `INVALID_ARGUMENT : Got invalid dimensions for input: x for the
  following indices index: 0 Got: 3 Expected: 1` — the exact message for p15.
- Latency is never asserted in milliseconds. `bench` takes an injected clock (p3), and real-timing tests compare ratios with wide margins.
- File sizes: `state_bytes(model)` = length of `torch.save(state_dict)` into a `BytesIO`; compare ratios (int8 ≥ 3× smaller), not exact bytes.
- Reuse the kit's names (Ch. 9.2): `Row`, `bench`, `quantise_symmetric`, `dequantise`, `prune_by_magnitude`, `sparsity`, `dominates`,
  `pareto_front`, `choose`; and `count_params`, `count_macs`, `quant_affine`, `quant_rows`, `RoundSTE`, `QATLinear`, `prune_neurons`,
  `export_onnx`, `onnx_predict`, `WithScaling`, `simulate`, `MicroBatcher`.

## A. Budgets and honest measurement (Ch. 1–2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Back-of-envelope budget | drill | trace | `⚠ HAND-TRACE` for an MLP 64 → 1024 → 10: parameters, fp32 bytes, int8 bytes, multiply-accumulates per example; print each |
| 2 | Count parameters and MACs | drill | code | `count_params(model)` and `count_macs(model, input_shape)` for Linear and Conv2d stacks; equal the formulas; bias counted in params, not MACs |
| 3 | A fair benchmark | applied | code | `bench(fn, x, warmup, repeat, clock)` → mean, p50, p95 in ms; warm-up calls are not timed; with a fake clock the percentiles are exact (nearest-rank) |
| 4 | Latency is not throughput | drill | explain | batching raises throughput and raises per-request latency; which one a user feels; checklist of 3 points |

## B. Quantisation (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Symmetric int8 quantisation | drill | code | `quantise_symmetric(values, bits)` → (int array, scale) and `dequantise`; max error ≤ scale / 2; 0 maps to 0; an all-zero array does not divide by zero; input not modified |
| 6 | Rounding by hand | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` values [-1.0, 0.3, 0.5, 2.54], 8 bits: the scale (2.54 / 127), each integer and each dequantised value (`:.4f`) |
| 7 | Affine quantisation by hand | applied | trace | `⚠ HAND-TRACE` values [0.0, 0.5, 1.0, 3.0] with a zero point (uint8): scale, zero point, integers, dequantised values; then why affine wins for non-negative data |
| 8 | Fake quantisation with a straight-through estimator | deep | code | `RoundSTE`: forward rounds, backward passes the gradient unchanged (grad of `RoundSTE.apply(x).sum()` is all ones); `QATLinear` forward equals a matmul with the fake-quantised weight |
| 9 | PyTorch dynamic quantisation | applied | code | `quantise_model(model)` with `quantize_dynamic` on Linear; `state_bytes` ≥ 3× smaller; outputs within 0.1 of the float model on 100 inputs |

## C. Pruning and distillation (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Magnitude pruning | drill | code | `prune_by_magnitude(weights, fraction)` zeroes exactly `round(fraction · n)` smallest-magnitude weights (ties by index, as in the kit); `sparsity`; input not modified |
| 11 | Why zeros do not shrink the file | deep | explain | `assessment = "explain"`; dense storage keeps zeros; dense matmul does not skip them; structured pruning and smaller architectures do; checklist of 4 points |
| 12 | Remove whole neurons | applied | code | `prune_neurons(model, keep)` builds smaller Linear layers keeping the neurons with the largest weight norms; `keep = all` gives identical outputs; parameter count falls as computed |
| 13 | A distillation loss | applied | code | `kd_loss(student_logits, teacher_logits, y, T, alpha)`; `alpha = 1` equals cross-entropy; the soft term is multiplied by T²; gradients finite and checked by `gradcheck` (float64) |

## D. ONNX and ONNX Runtime (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 14 | Export and verify | applied | code | `export_onnx(model, path, example, dynamic_batch=True)` and `onnx_predict(path)`; outputs equal PyTorch (allclose 1e-5) for batch 1 and 7 |
| 15 | Fix the fixed-batch export | applied | code | `assessment = "fix"`; the given export has no `dynamic_axes`, so a batch of 3 fails with "Got invalid dimensions for input"; fix it; the test runs batches 1, 3 and 64 |
| 16 | The preprocessing contract | deep | code | `WithScaling(model, mean, std)` puts normalisation inside the graph; the exported model on raw pixel values equals the PyTorch pipeline that normalises outside |

## E. Batching and serving (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | A batching simulator | challenge | code | `simulate(arrivals, cost, max_batch, max_wait)` → per-request latency; `max_batch = 1` is a plain FIFO queue; a 6-request schedule `⚠ HAND-TRACE`d in the test |
| 18 | Trace a micro-batcher | deep | trace | `⚠ HAND-TRACE` 5 arrivals, cost(b) = 2 + b ms, `max_batch = 3`, `max_wait = 1` ms: which requests go in each batch and each latency |

## F. Choosing (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | The Pareto front | drill | code | `dominates(a, b, acc_tol)`, `pareto_front(rows, acc_tol)`, `choose(rows, min_acc, max_size_kb, minimise)`; `None` when nothing fits; equal rows do not dominate each other |

## G. Project: optimise a model and report the trade-off (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | Build: the optimisation kit and report | challenge | code | `assessment = "build"`; `optimise_and_report(model, X, y, clock)` builds rows for fp32, int8 (dynamic), 50% pruned and ONNX; returns the rows and a Markdown table marking the Pareto front; tests with a tiny trained digits model: every candidate present, accuracy within 0.05 of fp32 for int8, sizes in the right order, front computed by `pareto_front`; ≤ 20 s |

## Counts check

Tiers: drill 1, 2, 4, 5, 6, 10, 19 = 7; applied 3, 7, 9, 12, 13, 14, 15 = 7; deep 8, 11, 16, 18 = 4; challenge 17, 20 = 2. Total 20.
Trace (4): 1, 6, 7, 18. Explain (2): 4, 11. Code: 14. One of each assessment: 11, 6, 15, 20.

## Risks and open questions

- `torch.onnx.export(..., dynamo=False)`: the legacy exporter may be removed in a future torch; the chapter uses `export_onnx` with the
  dynamo exporter (needs onnxscript, installed). Write p14/p15 with whatever the chapter's `export_onnx` uses and re-check the error text for p15.
- `torch.ao.quantization.quantize_dynamic` is marked for migration to torchao in newer torch; it works today (measured). Note it in `mistakes.md`.
- p17/p18 hand traces: state exactly when a batch starts (at `max_wait` after the first request, or when full, whichever first) and
  whether a request arriving at the same instant joins the batch.
