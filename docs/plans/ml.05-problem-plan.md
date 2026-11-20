# Problem plan: ml.05 Fine-tuning pretrained models (30 problems)

Rules: [README.md](README.md), table format of [dsa.07-problem-plan.md](dsa.07-problem-plan.md), **ml track notes M1–M5 in
[ml.01-problem-plan.md](ml.01-problem-plan.md)**. Function style. Ids `ml.05.p001`…`p030`.
**Mix:** 11 drill, 11 applied, 6 deep, 2 challenge. **Kinds:** 23 code, 4 trace, 3 explain.
**assessment:** explain = p022, trace = p016, fix = p013, build = p030.
**★ core set (12):** p1, p2, p3, p6, p8, p11, p13, p16, p17, p22, p24, p30.

## Testing notes

- **No Hub, ever.** The chapter downloads ~310 MB once; the problems do not. Models come from a small config built in the test or
  solution: `BertConfig(vocab_size=len(vocab), hidden_size=32, num_hidden_layers=2, num_attention_heads=2, intermediate_size=64,
  max_position_embeddings=16, num_labels=2)` → `BertForSequenceClassification(cfg)`. `conftest.py` sets `HF_HUB_OFFLINE=1` (M2) and
  monkeypatches `from_pretrained` to raise in p1, so a solution that tries to download fails with a clear message.
- Tokenisers: a `tokenizers` WordLevel model with a `Whitespace` pre-tokeniser wrapped in `PreTrainedTokenizerFast`. Measured: 2.0 s,
  72 MB; `padding=True` gives e.g. `{'input_ids': [[4, 6, 0, 0], [5, 5, 6, 1]], 'attention_mask': [[1, 1, 0, 0], [1, 1, 1, 1]]}` for
  vocab `[PAD]=0, [UNK]=1, [CLS]=2, [SEP]=3, good=4, bad=5, film=6` and texts "good film", "bad bad film here".
- Data: a synthetic sentiment set generated in the test (filler words + exactly one positive or negative word, seeded `random.Random`).
  Measured: the tiny BERT above, 150 AdamW steps (lr 3e-3, batch 32) on 200 examples → held-out accuracy 1.0 on seeds 0, 1, 2;
  ~1.3 s per seed after a ~5 s import; whole script 9.8 s, RSS 436 MB.
- **Memory is tight (M1):** torch + transformers + tiny BERT + optimiser reached **VmPeak 994 MB** (cap 1,024 MB). Rules:
  never import `datasets` in a torch test (measured: pyarrow "failed to map segment" → ImportError); no sklearn, scipy or pandas with torch;
  import `peft` only in p19 (the parent session measured tiny BERT + peft LoRA at 455 MB RSS, 8 s). `datasets` alone is fine
  (VmPeak 563 MB), so p4 is a torch-free problem.
- Evaluation problems (p23–p28) work on NumPy arrays of predictions given by the test: no model, no torch, so sklearn is allowed there.
- Reuse the chapter's names: `n_params`, `stratified_subset`, `count_overlap`, `encode`, `make_batch(ids, labels, idx, pad_id)`,
  `_is_head`, `build_model(cfg)`, `n_trainable`, `predict_proba`, `train`, `LoRALinear`, `add_lora`, `memory_gb`, `paired`, `ece_table`,
  `report`, `save_artifact`, `Classifier`.

## A. The Hugging Face stack, offline (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | A tiny model from a config | drill | code | `tiny_classifier(vocab_size, num_labels, seed)`; < 100,000 parameters; logits `(N, num_labels)`; same seed same weights; `from_pretrained` is never called |
| 2 | A local tokeniser | drill | code | `make_tokenizer(words)` → `PreTrainedTokenizerFast`; special tokens with fixed ids; unknown word → `[UNK]`; `padding=True`, `truncation`, `max_length` |
| 3 | Padding and the attention mask | drill | trace | `⚠ HAND-TRACE` `input_ids` and `attention_mask` for three sentences with the vocabulary in `problem.md`; print the lists |
| 4 | A `datasets.Dataset` from Python data | applied | code | `Dataset.from_dict`, `map(batched=True)`, `train_test_split(seed=...)`; no `load_dataset`; no torch in this problem (memory) |

## B. Data and honest baselines (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 5 | Majority and keyword baselines | drill | code | `majority_baseline(y_train, y_test)` and `keyword_baseline(texts, pos_words, neg_words)` accuracies on inline data |
| 6 | Leaks between train and test | applied | code | `count_overlap(train_texts, other_texts)` after normalising (lower case, collapsed spaces); exact duplicates counted once |
| 7 | A stratified subset | drill | code | `stratified_subset(y, n, seed)`; class shares kept (±1 example); deterministic; n larger than the data raises |

## C. Frozen features (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 8 | Mean pooling with a mask | applied | code | `masked_mean(hidden, mask)`; adding padding does not change a sentence's vector; equals the unpadded mean |
| 9 | The base model is not a classifier yet | drill | explain | the head is new and random; what "newly initialized" warnings mean; why a linear probe comes first; checklist of 3 points |

## D. Fine-tuning and what goes wrong (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Batches with dynamic padding | drill | code | `make_batch(ids, labels, idx, pad_id)` pads to the longest sequence in the batch, not the global maximum; mask matches |
| 11 | A fine-tuning loop | applied | code | `fit_classifier(model, data, epochs, lr, seed)` with AdamW, linear warm-up and clipping; overfits 16 examples to accuracy 1.0; held-out accuracy ≥ 0.9 on the synthetic set (measured 1.0 on 3 seeds) |
| 12 | Warm-up then decay | drill | trace | `⚠ HAND-TRACE` learning rate at steps 0–9 for linear warm-up over 2 steps, linear decay to 0 at step 10, peak 1e-3 (`:.6f`); the formula is given in `problem.md` (do not rely on a library function's off-by-one) |
| 13 | Fix: training on sorted data | applied | code | `assessment = "fix"`; the given loop iterates label-sorted data without shuffling, so batches hold one class and accuracy swings; fix with a seeded shuffle; the test checks mixed labels in the first batches and held-out accuracy ≥ 0.9 |
| 14 | A learning rate that destroys the model | deep | explain | why too large a rate wipes out what pretraining learned and why too small does nothing; warm-up; checklist of 4 points |
| 15 | Freeze all but the head | applied | code | `freeze_body(model)` using `_is_head(name)`; trainable count equals the classifier's parameters; the optimiser gets only trainable ones |
| 16 | Trainable parameters by hand | deep | trace | `assessment = "trace"`; `⚠ HAND-TRACE` for the tiny config: total parameters, head only, and LoRA r = 4 on query and value in 2 layers (2 · L · r · (d_in + d_out)); print each count |

## E. LoRA and parameter-efficient fine-tuning (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | `LoRALinear` from scratch | applied | code | B starts at zero so the output equals the base layer; only A and B train; scale = alpha / r; `merge()` gives the same outputs (allclose 1e-6) |
| 18 | Add LoRA to BERT | deep | code | `add_lora(model, targets, r, alpha)` replaces `query`/`value` Linear modules in place by name; forward unchanged at init; trainable fraction < 10% |
| 19 | Our LoRA against `peft` | challenge | code | same trainable count as `get_peft_model(LoraConfig(r, target_modules=["query", "value"], task_type="SEQ_CLS"))` minus the head; after copying A and B, the same logits (atol 1e-5); the only problem that imports peft |
| 20 | Adapters are small files | applied | code | `save_adapter(model, path)` stores only LoRA and head weights; the file is < 10% of the full state dict; loading into a fresh base reproduces the logits |
| 21 | Memory arithmetic | drill | trace | `⚠ HAND-TRACE` `memory_gb(n_total, n_trainable)` (4 bytes per weight + 12 per trainable weight) for 67M parameters, full fine-tuning against LoRA with 0.6M trainable (`:.2f`) |
| 22 | Why LoRA works | deep | explain | `assessment = "explain"`; a low-rank update, the frozen base, the zero-initialised B, the choice of rank and targets; checklist of 4 points |

## F. Evaluating a fine-tuned model (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | Metrics from predictions | drill | code | accuracy and macro-F1 by hand (NumPy) equal sklearn's; a class with no predictions gives F1 0 without a warning |
| 24 | Is A really better than B? | applied | code | `paired(pa, pb, y, n_boot, seed)` → difference and 95% interval; identical models → interval [0, 0]; a clearly better model → lower bound > 0 |
| 25 | Discordant pairs by hand | deep | code | `discordant(correct_a, correct_b)` → (A right B wrong, A wrong B right) and the accuracy difference; equals a loop; explains in `problem.md` why only discordant pairs matter |
| 26 | Expected calibration error | applied | code | `ece_table(conf, correct, bins)`; a hand-checked 10-example case; the bin edge rule (right-inclusive) stated and tested |
| 27 | Behavioural tests | deep | code | `invariance_failures(predict, pairs)` and `directional_failures(predict, pairs, expected)`; the test passes fake `predict` functions with known failures |
| 28 | Look at the most confident errors | drill | code | `top_errors(texts, probs, y, k)` sorted by confidence, ties by index; returns text, label, prediction, confidence |

## G. Project: a fine-tuned classifier (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | Package it and predict | applied | code | `save_artifact(dir, model, tokenizer, cfg, metrics)` and `Classifier.load(dir).predict(texts)` → labels and probabilities; padding a batch does not change any logit (Ch. 9.7) |
| 30 | Build: fine-tune and prove it beats the base | challenge | code | `assessment = "build"`; on the synthetic set: majority baseline, frozen-body linear probe, full fine-tuning; a report dict with each held-out accuracy and the paired interval of fine-tuned vs probe; tests: report keys, fine-tuned ≥ majority + 0.3, interval computed on the held-out split only; ≤ 20 s |

## Counts check

Tiers: drill 1, 2, 3, 5, 7, 9, 10, 12, 21, 23, 28 = 11; applied 4, 6, 8, 11, 13, 15, 17, 20, 24, 26, 29 = 11; deep 14, 16, 18, 22, 25, 27 = 6;
challenge 19, 30 = 2. Total 30.
Trace (4): 3, 12, 16, 21. Explain (3): 9, 14, 22. Code: 23. One of each assessment: 22, 16, 13, 30.
For a fifth trace, turn p25 into one (print the discordant counts and the accuracy difference for 8 given examples).

## Risks and open questions

- **Biggest risk in the ml track:** 994 MB VmPeak leaves ~50 MB. A newer transformers or torch could push it over the cap and every
  model test would fail with a confusing MemoryError. Suggested engine change (ask Kavya): a per-problem memory setting in
  `problem.toml` (e.g. `memory_mb = 2048`) read by `runner.py`; ml.05 would use it. Plans do not depend on it.
- p19 (peft) VmPeak not measured with the optimiser: measure before writing; drop to "same trainable count only" if it exceeds the cap.
- p30 thresholds: synthetic data is easy (1.0 measured); make it harder (two sentiment words, one negated) if the comparison should be interesting.
