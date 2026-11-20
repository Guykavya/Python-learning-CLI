# Problem plan: ml.04 Sequence models and transformers (35 problems)

Rules: [README.md](README.md), table format of [dsa.07-problem-plan.md](dsa.07-problem-plan.md), **ml track notes M1–M5 in
[ml.01-problem-plan.md](ml.01-problem-plan.md)**. Function style. Ids `ml.04.p001`…`p035`.
**Mix:** 12 drill, 13 applied, 7 deep, 3 challenge. **Kinds:** 25 code, 7 trace, 3 explain.
**assessment:** explain = p023, trace = p020, fix = p029, build = p035.
**★ core set (14):** p1, p4, p9, p13, p14, p16, p20, p21, p22, p23, p26, p29, p30, p35.

## Testing notes

- torch only (+ NumPy and the standard library). Text: short strings inline in the test; a longer corpus, when needed, from
  `pydoc_data.topics` (standard library, as in the chapter), sliced to ≤ 20,000 characters.
- Hand-written cells (RNN, LSTM, attention) are compared with `nn.RNN`, `nn.LSTM`, `F.scaled_dot_product_attention` after copying
  weights, in float64 (`atol=1e-10`). LSTM gate order in PyTorch is i, f, g, o: state it in `problem.md`.
- Measured: tiny GPT (C=32, 2 heads, 2 layers, T=16) overfits a 64-character text in 300 AdamW steps, ~2.4 s per seed,
  final loss 0.09 / 0.12 / 0.09 → threshold 0.3 (M4).
- Measured: gradient reaching step 0 of an 80-step sequence, ratio |grad at t=0| / |grad at t=79| at init (D=8, H=32, batch 16):
  RNN ~2–4e-22, LSTM ~1.5–6e-17, LSTM with forget-gate bias 1.0 ~1.4–3.6e-7 on seeds 0–2 (2.3 s total). Orders of magnitude are
  stable, so p15/p17 can assert "LSTM with forget bias 1 > 1e5 × plain RNN".
- **Not usable as a test:** the chapter's "remember the first token" memory task. Measured: an LSTM (H=48) stays at chance (0.12–0.13)
  after 400 steps with L=20; the chapter needs ~1,500 steps. The plan uses the gradient-ratio check instead.
- Reuse the chapter's names: `CharTokenizer`, `train_bpe`, `BPETokenizer`, `get_batch(d, B, T, gen)`, `BigramLM`, `rnn_forward`,
  `lstm_forward`, `gru_forward`, `SelfAttention`, `sinusoidal`, `MultiHeadAttention`, `CausalSelfAttention`, `Block`, `GPT`,
  `param_breakdown`, `next_token_probs`, `sample`, `sample_cached`, `mean_longest_match`, `CharVocab`, `Writer`.

## A. Tokenisation (Ch. 1)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | A character tokeniser | drill | code | `CharTokenizer(text)`: sorted vocabulary, `encode`/`decode` round trip, unknown character raises `KeyError` naming it |
| 2 | A word tokeniser with `<unk>` | drill | code | `min_freq`; rare and unseen words map to the `<unk>` id; `unk_rate(texts)` on held-out text |
| 3 | BPE merges by hand | drill | trace | `⚠ HAND-TRACE` pair counts and the first 3 merges on a 4-word corpus; use the chapter's tie rule and print it in `problem.md` |
| 4 | Train BPE | applied | code | `train_bpe(text, n_merges)` → merges; `encode` applies merges in learned order; `decode(encode(s)) == s`; more merges never give more tokens on the training text |
| 5 | Characters, words or subwords? | drill | explain | vocabulary size, sequence length, unknown words; checklist of 3 trade-offs |

## B. Embeddings (Ch. 2)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | An embedding is a lookup | drill | code | `embed(ids, table)` equals `one_hot(ids) @ table` and `nn.Embedding` with the same weight; only used rows receive a gradient |
| 7 | Padding and masks | applied | code | `pad_batch(seqs, pad_id)` → ids and mask; `masked_mean(emb, mask)` ignores padding (equals the unpadded mean); `padding_idx` row gets no gradient |
| 8 | Vectors from counting | applied | code | co-occurrence counts in a window → PPMI → cosine nearest neighbour; a 6-sentence corpus where the neighbour is clear by hand |

## C. Language modelling and baselines (Ch. 3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Batches for next-token prediction | drill | code | `get_batch(data, B, T, gen)`: `y` is `x` shifted by one; never reads past the end; same generator seed, same batch |
| 10 | An n-gram model with add-k | applied | code | validation loss of an add-k n-gram model equals a hand computation on a tiny text; unseen contexts use the chapter's fallback rule |
| 11 | Bigram loss by hand | drill | trace | `⚠ HAND-TRACE` counts table and average loss for the text "abab" + "ba" held out (`:.4f`) |
| 12 | The bigram table, learned | applied | code | `BigramLM` trained by the solution reaches the count-based bigram loss within 0.02 on a short text |

## D. Recurrent networks, LSTM, GRU (Ch. 4–5)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 13 | An RNN cell by hand | applied | code | `rnn_forward(x, w_ih, w_hh, b_ih, b_hh, h0)` equals `nn.RNN` (batch_first) with copied weights, float64 |
| 14 | The shapes of `nn.RNN` and `nn.LSTM` | drill | trace | `⚠ HAND-TRACE` output and hidden shapes for batch_first, 2 layers, bidirectional; print the tuples |
| 15 | Why plain RNNs forget | deep | explain | repeated multiplication by the recurrent Jacobian; the additive cell path of the LSTM; the forget-gate bias; checklist of 4 points (uses the measured ratios above as the worked example) |
| 16 | An LSTM cell by hand | deep | code | `lstm_forward` equals `nn.LSTM` with copied weights (gate order i, f, g, o); float64 |
| 17 | Forget-gate bias and gradient flow | applied | code | `grad_ratio(cell, forget_bias, seed)` → |grad at t=0| / |grad at t=T−1|; the test asserts LSTM with bias 1 > 1e5 × RNN on 3 seeds |
| 18 | The last real hidden state | deep | code | `last_states(outputs, lengths)` gathers each sequence's last non-pad step; equals `h_n` from `pack_padded_sequence` |
| 19 | Clipping stops an explosion | challenge | code | `train_steps(model, data, clip)`; with recurrent weights scaled ×3 the loss becomes `inf`/`nan` without clipping and stays finite with `clip=1.0` over 50 steps |

## E. Attention (Ch. 6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | Attention by hand | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` 2 tokens, d = 2: scores, scaled scores, softmax weights, output (`:.3f`) |
| 21 | Scaled dot-product attention | drill | code | `attention(q, k, v, mask=None)` equals `F.scaled_dot_product_attention`; shapes `(B, T, d)` and `(B, h, T, d)` |
| 22 | The causal mask | applied | code | future positions get weight 0; rows sum to 1; changing token t+1 does not change output t |
| 23 | Why divide by √d | deep | explain | `assessment = "explain"`; the variance of a dot product grows with d; softmax saturates; gradients vanish; checklist of 3 points |
| 24 | Sinusoidal positions | applied | code | `sinusoidal(T, C)` values at known positions; sin on even, cos on odd columns; the dot product of positions p and p+k depends only on k |
| 25 | Attention ignores order | deep | trace | `⚠ HAND-TRACE` permute the input rows of self-attention without positions; print which output rows equal which (booleans) |
| 26 | Multi-head attention | applied | code | split and merge heads; equals running single-head attention per head and concatenating; output shape `(B, T, C)` |

## F. The transformer, training and generating (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | A pre-norm transformer block | applied | code | `Block(C, n_head, T)`; residual shapes; `param_breakdown(C, L)` equals the module's real count |
| 28 | Count GPT's parameters | drill | trace | `⚠ HAND-TRACE` parameters of `GPT(V=50, C=32, L=2, T=16)` by part (embeddings, attention, MLP, norms, head); print each |
| 29 | Fix the leaking transformer | applied | code | `assessment = "fix"`; the given mask uses the wrong triangle, so the model sees the future and its training loss is suspiciously low; the causality test (Ch. 9.6) must pass after the fix |
| 30 | Temperature, top-k, top-p | applied | code | `next_token_probs(logits, temperature, top_k, top_p)`: sums to 1; top_k keeps k; top_p keeps the smallest set reaching p; temperature → 0 approaches argmax |
| 31 | Top-p by hand | drill | trace | `⚠ HAND-TRACE` probabilities [0.5, 0.2, 0.15, 0.1, 0.05], top_p = 0.8: the kept tokens and renormalised probabilities (`:.4f`) |
| 32 | A KV cache | challenge | code | `sample_cached` with greedy decoding produces the same tokens as `sample` without a cache; the cache grows by one step per token |
| 33 | Does it copy its training text? | deep | code | `mean_longest_match(s, train, step)` equals a brute-force version on short strings |
| 34 | Generating past the block size | deep | code | `generate` crops the context to the last T tokens; generating 3·T tokens works and equals feeding only the last T by hand |

## G. Project: a character-level transformer (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Build: a character-level transformer writer | challenge | code | `assessment = "build"`; `CharVocab`, `GPT`, `train`, `generate`, `Writer.save/load`; tests from Ch. 9.6: vocabulary round trip and strictness, output shape and initial loss ≈ ln V, causality, overfits a 64-character text below loss 0.3 in ≤ 300 steps, greedy generation deterministic, save/load gives the same text |

## Counts check

Tiers: drill 1, 2, 3, 5, 6, 9, 11, 14, 20, 21, 28, 31 = 12; applied 4, 7, 8, 10, 12, 13, 17, 22, 24, 26, 27, 29, 30 = 13;
deep 15, 16, 18, 23, 25, 33, 34 = 7; challenge 19, 32, 35 = 3. Total 35.
Trace (7): 3, 11, 14, 20, 25, 28, 31. Explain (3): 5, 15, 23. Code: 25. One of each assessment: 23, 20, 29, 35.

## Risks and open questions

- p3: BPE tie-breaking differs between implementations; the problem must print the chapter's exact rule and use the chapter's code.
- p19: check that ×3 recurrent weights really overflow within 50 steps without clipping on all 3 seeds; otherwise use a larger factor.
- p35 is the heaviest test (~3 s of training): one seed for the overfit check.
