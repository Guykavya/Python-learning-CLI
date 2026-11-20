# Problem plan: ml.03 Computer vision (25 problems)

Rules: [README.md](README.md), table format of [dsa.07-problem-plan.md](dsa.07-problem-plan.md), **ml track notes M1–M5 in
[ml.01-problem-plan.md](ml.01-problem-plan.md)**. Function style. Ids `ml.03.p001`…`p025`.
**Mix:** 8 drill, 9 applied, 5 deep, 3 challenge. **Kinds:** 17 code, 5 trace, 3 explain.
**assessment:** explain = p010, trace = p007, fix = p015, build = p025.
**★ core set (10):** p4, p5, p7, p9, p10, p11, p14, p15, p22, p25.

## Testing notes

- torch only, plus Pillow for PNG files (p2, p25). No torchvision (not installed), no sklearn (M1). Digits from `fixtures/digits.npz` (M3).
- "Pretrained" networks are pretrained **by the test** (as the chapter does in Ch. 8.2): a small CNN trained ~150 steps on digits 0–4 (~0.5 s),
  then adapted to 5–9. Never a downloaded model.
- Image folders for p2/p25 are written by the test into `tmp_path` with Pillow, then the path is passed to the solution (R1).
- Reuse the chapter's names: `out_size`, `conv2d_naive(x, weight, bias, padding, stride)`, `receptive_field_formula`, `shape_table`,
  `ResBlock`, `TinyResNet`, `random_shift`, `random_hflip`, `add_noise`, `cutout`, `compose`, `predict_proba(model, X, tta)`, `grad_cam`,
  `freeze_features`, `train_mode(model, bn_fixed)`, `ImageFolderDataset`, `split_indices`, `Predictor`.
- Grad-CAM (p20) is tested on a synthetic task whose answer is known (the class is decided by a bright 2×2 square in one quadrant).
  Not measured yet: check the reference reaches the 80% "peak in the right quadrant" rate on 3 seeds before shipping.

## A. Images as tensors (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | NCHW and per-channel normalisation | drill | code | `to_nchw(batch_hwc_uint8)`; `channel_stats(train)` and `normalise(x, mean, std)`; statistics from the training split only (the test passes train and val separately) |
| 2 | Read real image files | applied | code | `load_image(path, size)` with Pillow → float tensor `(3, H, W)` in [0, 1]; grey (L) and RGBA files become 3 channels; resize to `size`; round trip with a PNG the test wrote |

## B. Convolution, pooling, normalisation (Ch. 2–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 3 | The output-size formula | drill | trace | `⚠ HAND-TRACE` `out_size(n, k, p, s, d)` for five layer specs (including stride 2 and dilation 2); print the sizes |
| 4 | Multi-channel convolution by hand | applied | code | `conv2d_naive(x, weight, bias, padding, stride)` equals `F.conv2d` on random float64 input (batch 2, 3→4 channels, stride 1 and 2) |
| 5 | The receptive field | deep | code | `receptive_field_formula(layers)` equals the field measured by the test (gradient of one output pixel w.r.t. the input) for 3 stacks |
| 6 | Parameter counts by hand | drill | trace | `⚠ HAND-TRACE` parameters of a 3×3 conv, a 1×1 conv, a depthwise conv (`groups = C`) and a bias-free conv; print the counts |
| 7 | A shape table | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` the chapter's `shape_table` output for a given stack (conv, BatchNorm2d, ReLU, MaxPool, conv, AdaptiveAvgPool, Flatten, Linear) on a `(2, 1, 8, 8)` input |
| 8 | What BatchNorm2d averages over | applied | trace | `⚠ HAND-TRACE` per-channel mean and variance over (N, H, W) of a `(2, 2, 2, 2)` tensor given in full (`:.2f`) |

## C. Architectures (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | A residual block | applied | code | `ResBlock(c_in, c_out, stride)` with a 1×1 projection when shape changes; output shapes; with the conv weights zeroed the block is identity + ReLU |
| 10 | Why residual connections help | deep | explain | `assessment = "explain"`; gradient flow through the skip path, plain vs residual at depth 30 (Ch. 4.4); checklist: "identity path", "gradient", "depth", "degradation" |
| 11 | TinyResNet within a budget | challenge | code | ≤ 20,000 parameters; output `(N, 10)`; trained by the test for ≤ 300 steps: digits accuracy ≥ 0.85 on 3 seeds (measure the reference first) |

## D. Training a CNN (Ch. 5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 12 | Overfit one batch first | drill | code | `overfit_check(model, xb, yb, steps, lr)` → final loss; a healthy CNN goes below 0.05, one with a frozen first layer and a 1-unit bottleneck does not |
| 13 | Read the curves | applied | code | `curve_verdict(train_loss, val_loss)` → "underfit" / "overfit" / "good" / "diverged"; 8 hand-made curves with the rules stated in `problem.md` |

## E. Data augmentation (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 14 | Augmentations as tensor functions | drill | code | `random_shift`, `random_hflip`, `add_noise`, `cutout`, `compose` with a `torch.Generator`; shape and dtype kept; same seed same output; a shift fills with zeros |
| 15 | Augment the training set only | applied | code | `assessment = "fix"`; the given dataset applies augmentation in every split, so validation scores change between calls; fix it; the test calls validation twice and requires identical results |
| 16 | Not every augmentation keeps the label | deep | explain | why horizontal flips harm digit recognition but help photos of cats; how to choose augmentations; checklist of 3 points |
| 17 | Mixup | applied | code | `mixup(x, y, alpha, gen)` → mixed x, soft targets that sum to 1; λ in [0, 1]; the soft-target loss equals λ·CE(a) + (1−λ)·CE(b) |
| 18 | Test-time augmentation | applied | code | `predict_proba(model, X, tta)` averages probabilities over the original and flipped images; rows sum to 1; for a flip-invariant model TTA changes nothing |

## F. Looking inside a network (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Capture feature maps | drill | code | `feature_maps(model, x, layer_name)` with a forward hook; right shape; the hook is removed; an unknown name raises `KeyError` listing valid names |
| 20 | Grad-CAM | challenge | code | heat map has the feature map's spatial size, is ≥ 0, max 1; on the synthetic quadrant task the peak lies in the deciding quadrant for ≥ 80% of test images |
| 21 | Grad-CAM by hand | deep | trace | `⚠ HAND-TRACE` two 2×2 feature maps and their gradients: channel weights (mean gradient), weighted sum, ReLU; print rows |

## G. Transfer learning (Ch. 8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 22 | Replace the head and freeze | drill | code | `adapt(model, n_classes, freeze)`: new head with the right `out_features`; feature parameters `requires_grad=False`; frozen BatchNorm stays in eval mode inside `train_mode(model, bn_fixed=True)` |
| 23 | Different learning rates per part | applied | code | `param_groups(model, lr_body, lr_head)`; every trainable parameter in exactly one group; frozen ones in none |
| 24 | When transfer learning fails | deep | explain | source and target too different, tiny data, BatchNorm statistics; what to try; checklist of 4 points |

## H. Project: a fine-tuned classifier for a custom dataset (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 25 | Build: fine-tune on an image folder | challenge | code | `assessment = "build"`; `ImageFolderDataset(root)`, stratified `split_indices`, `fit` with a given "pretrained" checkpoint, `Predictor`; the test writes 20 PNGs per class for 5 classes into `tmp_path` and pretrains the source model itself; checks: split disjoint and stratified, only the head trains in frozen mode, accuracy ≥ a threshold set from 3 reference runs, artefact reloads with equal predictions; ≤ 20 s |

## Counts check

Tiers: drill 1, 3, 6, 7, 12, 14, 19, 22 = 8; applied 2, 4, 8, 9, 13, 15, 17, 18, 23 = 9; deep 5, 10, 16, 21, 24 = 5; challenge 11, 20, 25 = 3. Total 25.
Trace (5): 3, 6, 7, 8, 21. Explain (3): 10, 16, 24. Code: 17. One of each assessment: 10, 7, 15, 25.

## Risks and open questions

- p11, p20, p25 thresholds are not measured yet: run the reference on 3 seeds and set the threshold well below the worst run.
- p25 is the heaviest test (Pillow + torch + pretraining): keep images 8×8 or 16×16 and time it; split the build if it passes 20 s.
- Pillow + torch VmPeak not measured: check it stays under the cap (expect ~750 MB).
