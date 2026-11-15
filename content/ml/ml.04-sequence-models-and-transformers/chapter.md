# Chapter 4 (ML): Sequence Models and Transformers

In ml.03 the input was a grid of pixels. Here the input is a **sequence**: text, a time series, DNA, a stream of clicks. Sequences differ from images in two ways: they have **variable length**, and **order matters**, and what comes far back can matter. This chapter follows the road the field took: turn text into numbers (**tokenisation and embeddings**), read it one step at a time with a memory (**RNNs, GRUs and LSTMs**), and finally let every position look at every other position directly (**attention and the transformer**), which is the architecture behind modern language models.

You will learn **tokenisation** (characters, words, byte-pair encoding written from scratch), **embeddings** (a lookup table, what it learns, why padding needs care), **language modelling** (next-token prediction, cross-entropy, perplexity, and how to beat honest count-based baselines), **RNNs** written by hand and checked against PyTorch, **why they forget** (measured), **LSTM and GRU gates**, **scaled dot-product attention** with every tensor shape, **masks**, **multi-head attention**, **positional encodings**, the **transformer block**, **sampling** (temperature, top-k, top-p) and a **KV cache**. The syllabus outcome is: **implement self-attention and explain each tensor shape.** The chapter ends with a project: a small **character-level transformer that generates text**, packaged and tested.

Prerequisites: ml.01 (backpropagation, vanishing gradients, normalisation), ml.02 (tensors, `nn.Module`, the training loop, saving and loading).

> **Offline rule for this chapter.** Everything runs with no internet on the **CPU build** of PyTorch (2.15). There are no pretrained weights and no tokenizer libraries here, so tokenisers are written by hand, and the training text is a real English corpus that ships with Python itself: the text of the Python language reference (`pydoc_data.topics`, about 580,000 characters). Models are small (tens of thousands to a few hundred thousand parameters) so that they train in seconds to a few minutes on a laptop CPU. A model this small writes text that *looks* like the reference (words, punctuation, code-like fragments) but does not *understand* it; that gap is part of the lesson. Every output block below was produced by running the code above it, in one session from top to bottom. The corpus text depends on your Python version, so exact losses and generated samples will differ slightly on yours; timings are machine-specific.

```python run
import sys, math, time, re, copy, collections, pathlib, tempfile, subprocess, warnings, platform
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

warnings.filterwarnings("ignore")
np.set_printoptions(precision=4, suppress=True, linewidth=120)
pd.set_option("display.width", 130)
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__)
print("torch  ", torch.__version__, "| CUDA available:", torch.cuda.is_available(), "| threads:", torch.get_num_threads())

import pydoc_data.topics as _topics
raw = "\n\n".join(_topics.topics[k] for k in sorted(_topics.topics))
text = raw.encode("ascii", "ignore").decode("ascii")                     # keep plain ASCII so the vocabulary stays small
print(f"corpus: {len(raw):,} characters, {len(text):,} after dropping non-ASCII, {len(set(text))} distinct characters")
print("a slice:", repr(text[3000:3160]))
```
```text
python  3.14.4
numpy   2.5.4
torch   2.15.0+cpu | CUDA available: False | threads: 6
corpus: 577,618 characters, 576,774 after dropping non-ASCII, 96 distinct characters
a slice: 'm left to\n    right, to the targets before the starred target.  The final items\n    of the iterable are assigned to the targets after the starred\n    target.  A'
```

## Table of contents

1. [Tokenisation: from text to integers](#1-tokenisation-from-text-to-integers)
2. [Embeddings](#2-embeddings)
3. [Language modelling and honest baselines](#3-language-modelling-and-honest-baselines)
4. [Recurrent networks from scratch](#4-recurrent-networks-from-scratch)
5. [Why RNNs forget, and LSTM and GRU](#5-why-rnns-forget-and-lstm-and-gru)
6. [Attention](#6-attention)
7. [The transformer](#7-the-transformer)
8. [Training and generating](#8-training-and-generating)
9. [Project: a character-level transformer that writes text](#9-project-a-character-level-transformer-that-writes-text)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. Tokenisation: from text to integers

### 1.1 Why we need tokens

A neural network takes numbers. Text must first be cut into pieces, **tokens**, and each token mapped to an integer id from a fixed list, the **vocabulary**. The choice of piece is a design decision with real consequences:

| Token | Vocabulary size | Sequence length | Weakness |
|---|---|---|---|
| characters | tiny (about 100) | very long | the model must learn spelling and long-range structure |
| words | huge (100,000+) | short | never-seen words (**out of vocabulary**, OOV); no sharing between `run` and `running` |
| **subwords** (BPE) | you choose (1,000 to 100,000) | in between | slightly harder to implement |

Modern language models use subwords. We build all three, because seeing the trade-off on your own data is the best way to remember it.

### 1.2 A character tokeniser

```python run
class CharTokenizer:
    PAD, UNK = "<pad>", "<unk>"
    def __init__(self, text):
        chars = sorted(set(text))
        self.itos = [self.PAD, self.UNK] + chars                          # id 0 = padding, id 1 = unknown
        self.stoi = {c: i for i, c in enumerate(self.itos)}
    def __len__(self): return len(self.itos)
    def encode(self, s): return [self.stoi.get(c, 1) for c in s]            # unseen character -> <unk>
    def decode(self, ids): return "".join(self.itos[i] for i in ids if i > 1)

tok = CharTokenizer(text)
s = "x = [i**2 for i in range(3)]"
ids = tok.encode(s)
print("vocabulary size:", len(tok), "| first symbols:", tok.itos[:12])
print("ids:", ids)
print("round trip is lossless:", tok.decode(ids) == s)
print("an unseen character becomes <unk> (id 1) and is lost:", tok.encode("aéb"), "->", repr(tok.decode(tok.encode("aéb"))))
```
```text
vocabulary size: 98 | first symbols: ['<pad>', '<unk>', '\n', ' ', '!', '"', '#', '$', '%', '&', "'", '(']
ids: [91, 3, 32, 3, 62, 76, 13, 13, 21, 3, 73, 82, 85, 3, 76, 3, 76, 81, 3, 85, 68, 81, 74, 72, 11, 22, 12, 64]
round trip is lossless: True
an unseen character becomes <unk> (id 1) and is lost: [68, 1, 69] -> 'ab'
```

### 1.3 A word tokeniser, and the out-of-vocabulary problem

Split on words and punctuation. Build the vocabulary from the **first half** of the text and look at what fraction of tokens in the **second half** are unknown. That is what a deployed model sees: new text.

```python run
word_re = re.compile(r"[A-Za-z_]+|\d+|[^\sA-Za-z_\d]")
words = word_re.findall(text)
half = len(words) // 2
train_w, test_w = words[:half], words[half:]
counts = collections.Counter(train_w)
print(f"{len(words):,} word tokens, {len(counts):,} distinct in the first half")
rows = []
for vocab_size in (500, 2000, 8000, len(counts)):
    vocab = {w for w, _ in counts.most_common(vocab_size)}
    oov = np.mean([w not in vocab for w in test_w])
    rows.append([vocab_size, f"{100 * oov:.2f}%"])
print(pd.DataFrame(rows, columns=["vocabulary size", "OOV rate on unseen second half"]).to_string(index=False))
print("examples of test words never seen in training:", [w for w in dict.fromkeys(test_w) if w not in counts][:10])
```
```text
142,845 word tokens, 3,519 distinct in the first half
 vocabulary size OOV rate on unseen second half
             500                         13.62%
            2000                          5.81%
            8000                          3.79%
            3519                          3.79%
examples of test words never seen in training: ['unparenthesized', 'constrain', 'delivered', 'Raising', 'raise_stmt', 'RuntimeError', 'BaseException', '__traceback__', 'with_traceback', 'tracebackobj']
```

Even with the full training vocabulary a few percent of the new tokens are unknown, and every one of them is replaced by `<unk>`, which throws the word away. Rare words are exactly the informative ones (names, technical terms).

### 1.4 Byte-pair encoding (BPE), from scratch

**BPE** keeps the character tokeniser's guarantee (nothing is ever unknown, because single characters are always in the vocabulary) and gains the word tokeniser's compactness: it repeatedly **merges the most frequent adjacent pair** of symbols into a new symbol. Common words end up as one token; rare words are split into familiar pieces.

The algorithm, on a word-frequency table (a word is a tuple of symbols):

```
1. start: every word is a tuple of characters; vocabulary = all characters
2. count every adjacent pair of symbols, weighted by word frequency
3. merge the most frequent pair everywhere into one new symbol; record the merge
4. repeat 2-3 until the vocabulary has the size you want
```

To encode new text, split it into words, start from characters, and apply the recorded merges **in the order they were learned**.

```python run
pretok = re.compile(r" ?[A-Za-z]+| ?\d+| ?[^\sA-Za-z\d]+|\s+")             # a leading space belongs to the word that follows it
def train_bpe(text, n_merges):
    word_freq = collections.Counter(pretok.findall(text))
    vocab = {w: tuple(w) for w in word_freq}                                 # word -> tuple of symbols
    merges = []
    for _ in range(n_merges):
        pairs = collections.Counter()
        for w, syms in vocab.items():
            f = word_freq[w]
            for a, b in zip(syms, syms[1:]): pairs[(a, b)] += f
        if not pairs: break
        best = max(pairs, key=lambda p: (pairs[p], p))                       # ties broken deterministically
        merges.append(best)
        merged = best[0] + best[1]
        for w, syms in vocab.items():
            if best[0] not in syms: continue
            out, i = [], 0
            while i < len(syms):
                if i + 1 < len(syms) and (syms[i], syms[i + 1]) == best: out.append(merged); i += 2
                else: out.append(syms[i]); i += 1
            vocab[w] = tuple(out)
    return merges

class BPETokenizer:
    def __init__(self, base_chars, merges):
        self.merges = merges
        self.rank = {m: i for i, m in enumerate(merges)}
        self.itos = list(base_chars) + [a + b for a, b in merges]
        self.stoi = {s: i for i, s in enumerate(self.itos)}
        self.cache = {}
    def __len__(self): return len(self.itos)
    def _word(self, w):
        if w in self.cache: return self.cache[w]
        syms = list(w)
        while len(syms) > 1:
            pairs = [(self.rank.get((a, b), 1e9), i) for i, (a, b) in enumerate(zip(syms, syms[1:]))]
            r, i = min(pairs)
            if r == 1e9: break                                               # no learned merge applies any more
            syms[i:i + 2] = [syms[i] + syms[i + 1]]
        self.cache[w] = [self.stoi[s] for s in syms]
        return self.cache[w]
    def encode(self, s): return [t for w in pretok.findall(s) for t in self._word(w)]
    def decode(self, ids): return "".join(self.itos[i] for i in ids)

train_text, held_out = text[:300_000], text[300_000:]
t0 = time.time()
merges = train_bpe(train_text, 400)
print(f"learned {len(merges)} merges in {time.time() - t0:.1f}s | first 12 merges:", [a + b for a, b in merges[:12]])
print("later merges (longer pieces):", [a + b for a, b in merges[300:310]])
base = sorted(set(text))
bpe = BPETokenizer(base, merges)
sample = "The expression is evaluated and the exception is raised."
pieces = [bpe.itos[i] for i in bpe.encode(sample)]
print("vocabulary size:", len(bpe), "| sample pieces:", pieces)
print("lossless on unseen text:", bpe.decode(bpe.encode(held_out[:50_000])) == held_out[:50_000])
print("a made-up word is split into known pieces, never <unk>:", [bpe.itos[i] for i in bpe.encode(" florbnaxify")])
```
```text
learned 400 merges in 4.5s | first 12 merges: ['  ', ' t', ' a', 'he', 'in', '    ', 'on', '--', 'te', 're', ' the', 'or']
later merges (longer pieces): ['For', ' oper', 'tin', 'ses', 'ill', 'ated', ' other', ' version', ' ne', ' un']
vocabulary size: 496 | sample pieces: ['The', ' expression', ' is', ' evalu', 'ated', ' and', ' the', ' exception', ' is', ' rais', 'ed', '.']
lossless on unseen text: True
a made-up word is split into known pieces, never <unk>: [' f', 'l', 'or', 'b', 'n', 'ax', 'if', 'y']
```

> **Predict the output.** Training text is 300,000 characters. After 400 merges, will the unseen text `held_out[:50_000]` be about 50,000 tokens, about 25,000, or about 15,000? Roughly how many characters does one token cover on average?

<details><summary>Answer</summary>

Fewer than the 50,000 characters, since every merge lets one token stand for two or more characters. The next block gives the exact count: about 20,000 tokens, i.e. 2.5 characters per token. More merges mean fewer tokens per text but a bigger vocabulary (a bigger embedding table and output layer), and that is the trade-off in the table of 1.1.

</details>

```python run
chunk = held_out[:50_000]
rows = [["characters", len(base), len(chunk)]]
for n in (100, 400):
    b = BPETokenizer(base, merges[:n]); rows.append([f"BPE, {n} merges", len(b), len(b.encode(chunk))])
rows.append(["words (see 1.3)", len(counts), len(word_re.findall(chunk))])
df = pd.DataFrame(rows, columns=["tokenisation", "vocabulary size", "tokens for 50,000 characters"])
df["characters per token"] = (len(chunk) / df["tokens for 50,000 characters"]).round(2)
print(df.to_string(index=False))
```
```text
   tokenisation  vocabulary size  tokens for 50,000 characters  characters per token
     characters               96                         50000                  1.00
BPE, 100 merges              196                         29119                  1.72
BPE, 400 merges              496                         20035                  2.50
words (see 1.3)             3519                         11899                  4.20
```

In production the idea is the same with these differences: BPE usually runs on **bytes** (so any text in any language can be encoded), uses 30,000 to 200,000 merges, and special tokens (`<|endoftext|>`) are reserved. A byte-level tokenizer never needs `<unk>`; you can see why bytes matter below.

```python run
for s in ("a", "é", "中", "\U0001F600"):
    print(f"{s!r}: {len(s)} character, {len(s.encode('utf-8'))} UTF-8 bytes -> {list(s.encode('utf-8'))}")
```
```text
'a': 1 character, 1 UTF-8 bytes -> [97]
'é': 1 character, 2 UTF-8 bytes -> [195, 169]
'中': 1 character, 3 UTF-8 bytes -> [228, 184, 173]
'😀': 1 character, 4 UTF-8 bytes -> [240, 159, 152, 128]
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate byte-pair encoding on a tiny word-frequency table, for example low x5, lower x2, newest x6, widest x3, each word split into characters. At each step highlight the most frequent adjacent pair (weighted by word frequency), merge it everywhere into a new symbol, and show the updated words and the growing vocabulary. Run about six merges, and show a counter of tokens needed for the whole text falling."

### 1.5 Try it

1. Add a special `<eos>` (end of sequence) token to `CharTokenizer`, append it when encoding a document, and make `decode` drop it. Why does a model that generates text need such a token?
2. Run `train_bpe` on only the first 20,000 characters, and compare the first 12 merges with those above. Are they the same? Why or why not?
3. Count how many distinct tokens of the 400-merge vocabulary are actually used when encoding `held_out`. What does an unused token cost?

## 2. Embeddings

### 2.1 An embedding is a lookup table

A token id is just a label; there is no meaning in "id 17 is bigger than id 5". An **embedding** replaces each id by a learned vector of `D` numbers. `nn.Embedding(V, D)` is a matrix `W` of shape `(V, D)`; looking up id `i` returns row `i`. That is *exactly* the same as multiplying a one-hot vector by `W`, only without building the mostly-zero vector.

```python run
torch.manual_seed(0)
V, D = 6, 4
emb = nn.Embedding(V, D)
ids = torch.tensor([[2, 5, 2], [0, 1, 3]])                       # a batch of 2 sequences, each 3 tokens: shape (B, T)
out = emb(ids)
print("ids", tuple(ids.shape), "-> embeddings", tuple(out.shape), "= (B, T, D)")
print("parameters:", sum(p.numel() for p in emb.parameters()), "= V x D =", V * D)
one_hot = F.one_hot(ids, V).float()                              # (B, T, V)
print("one_hot @ W equals the lookup:", bool(torch.allclose(one_hot @ emb.weight, out)))
print("the same id gives the same vector wherever it appears:", bool(torch.equal(out[0, 0], out[0, 2])))
out.sum().backward()
print("gradient is non-zero only for rows that were used (ids 0,1,2,3,5):", (emb.weight.grad.abs().sum(1) > 0).tolist())
```
```text
ids (2, 3) -> embeddings (2, 3, 4) = (B, T, D)
parameters: 24 = V x D = 24
one_hot @ W equals the lookup: True
the same id gives the same vector wherever it appears: True
gradient is non-zero only for rows that were used (ids 0,1,2,3,5): [True, True, True, True, False, True]
```

Notice the last line. In a big vocabulary only a few rows get a gradient on each step, which is why embedding layers are sometimes trained with sparse updates or a different learning rate, and why **weight decay** applied to the whole table also shrinks the rows of tokens that were not seen in this batch (AdamW does exactly that).

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw an embedding table as a grid W with V=6 rows (ids 0 to 5) and D=4 columns. Show the batch ids [[2,5,2],[0,1,3]] of shape (B,T)=(2,3) as arrows picking rows 2, 5, 2 and 0, 1, 3, producing an output cube of shape (2,3,4). Colour row 2 the same in both places it is used, and grey out row 4, which is never used and gets no gradient."

### 2.2 Padding

Sequences in a batch must have the same length, so shorter ones are **padded** with a special id (here 0). Two things must then hold: the pad positions must not contribute to the loss, and the pad embedding should not learn anything. `padding_idx` freezes that row at zero and stops its gradient; the loss mask is separate.

```python run
torch.manual_seed(0)
emb = nn.Embedding(6, 4, padding_idx=0)
batch = [[3, 4, 5], [2, 1], [4]]
T = max(map(len, batch))
padded = torch.tensor([s + [0] * (T - len(s)) for s in batch])
lengths = torch.tensor([len(s) for s in batch])
mask = torch.arange(T)[None, :] < lengths[:, None]                       # True for real tokens
print("padded batch:\n", padded)
print("mask:\n", mask.int())
print("row 0 of the table is all zeros:", emb.weight[0].tolist())
emb(padded).sum().backward()
print("gradient on the pad row:", emb.weight.grad[0].tolist())
# masked mean of the embeddings: do not average in the padding
x = emb(padded)
masked_mean = (x * mask[..., None]).sum(1) / lengths[:, None]
naive_mean = x.mean(1)
print("masked mean vs naive mean for the shortest sequence (1 real token):")
print("  masked:", masked_mean[2].detach().numpy().round(3), "\n  naive :", naive_mean[2].detach().numpy().round(3), "(diluted by two pads)")
```
```text
padded batch:
 tensor([[3, 4, 5],
        [2, 1, 0],
        [4, 0, 0]])
mask:
 tensor([[1, 1, 1],
        [1, 1, 0],
        [1, 0, 0]], dtype=torch.int32)
row 0 of the table is all zeros: [0.0, 0.0, 0.0, 0.0]
gradient on the pad row: [0.0, 0.0, 0.0, 0.0]
masked mean vs naive mean for the shortest sequence (1 real token):
  masked: [0.932 1.259 2.005 0.054] 
  naive : [0.311 0.42  0.668 0.018] (diluted by two pads)
```

### 2.3 What do embeddings learn? Vectors from counting

Embeddings are trained so that the model does well on its task, and as a by-product tokens used in similar contexts get similar vectors. You can see the same effect without any neural network. Count, for each word, which words appear within two positions of it (a **co-occurrence matrix**), transform the counts into **positive pointwise mutual information** (PPMI; how much more often two words co-occur than chance predicts), and compress with an SVD. The rows of the result are word vectors.

```python run
lw = [w.lower() for w in words if w.isalpha()]
top = [w for w, _ in collections.Counter(lw).most_common(1500)]
widx = {w: i for i, w in enumerate(top)}
C = np.zeros((len(top), len(top)))
ids_ = [widx.get(w, -1) for w in lw]
for off in (1, 2):
    a, b = np.array(ids_[:-off]), np.array(ids_[off:])
    ok = (a >= 0) & (b >= 0)
    np.add.at(C, (a[ok], b[ok]), 1); np.add.at(C, (b[ok], a[ok]), 1)
total = C.sum(); pw = C.sum(1, keepdims=True) / total; pc = C.sum(0, keepdims=True) / total
with np.errstate(divide="ignore", invalid="ignore"):
    ppmi = np.maximum(np.log((C / total) / (pw @ pc)), 0)
ppmi[~np.isfinite(ppmi)] = 0
U, S, Vt = np.linalg.svd(ppmi, full_matrices=False)
vec = U[:, :50] * np.sqrt(S[:50])
vec /= np.linalg.norm(vec, axis=1, keepdims=True) + 1e-12
def neighbours(w, k=6):
    sims = vec @ vec[widx[w]]
    return [top[i] for i in np.argsort(-sims)[1:k + 1]]
for w in ("class", "exception", "string", "function", "import", "true"):
    print(f"{w:<10} -> {neighbours(w)}")
```
```text
class      -> ['meta', 'object', 'instance', 'method', 'classmethod', 'classs']
exception  -> ['raised', 'typeerror', 'attributeerror', 'raises', 'eg', 'raise']
string     -> ['raw', 'template', 'triple', 'literals', 'quoted', 'literal']
function   -> ['generator', 'coroutine', 'definition', 'returns', 'asynchronous', 'functions']
import     -> ['baz', 'bar', 'falls', 'imported', 'feature', 'foo']
true       -> ['false', 'isalpha', 'isnumeric', 'isalnum', 'isdecimal', 'isupper']
```

These neighbours come from counting alone. The point: **meaning-like structure is a consequence of context statistics**, and a trained `nn.Embedding` ends up with the same kind of structure. Cosine similarity (the dot product of unit vectors) is the standard way to compare them.

### 2.4 Try it

1. Change the window from 2 to 5 and the dimension from 50 to 10. How do the neighbours of `class` change?
2. Why does `nn.Embedding(50_000, 768)` have 38 million parameters while the rest of a small model may have fewer? What does this suggest about the cost of a large vocabulary?
3. An `nn.Embedding` is applied to a tensor of shape `(8, 128)` of ids. What is the output shape? What if the ids have shape `(8, 128, 4)`?

## 3. Language modelling and honest baselines

### 3.1 The task: predict the next token

A **language model** assigns a probability to the next token given all the previous ones, `P(x_t | x_1 … x_{t-1})`. Training needs no labels beyond the text itself: the target is the input **shifted by one position**.

```
text:    h  e  l  l  o
input x: h  e  l  l        position t sees x_t
target y:   e  l  l  o        and must predict y_t = x_{t+1}
```

The loss is the cross-entropy of the predicted distribution against the true next token, averaged over positions. Exponentiated, it is the **perplexity**: the effective number of tokens the model is "choosing between" at each step. A model that knows nothing has perplexity equal to the vocabulary size.

```python run
data = torch.tensor(tok.encode(text))                           # character ids
n_val = len(data) // 10
train_data, val_data = data[:-n_val], data[-n_val:]              # contiguous split: the validation text comes AFTER the training text
V = len(tok)
print(f"{len(train_data):,} training characters, {len(val_data):,} validation characters, vocabulary {V}")

def get_batch(d, B, T, gen):
    ix = torch.randint(0, len(d) - T - 1, (B,), generator=gen)
    x = torch.stack([d[i:i + T] for i in ix]); y = torch.stack([d[i + 1:i + T + 1] for i in ix])
    return x, y
x, y = get_batch(train_data, 2, 8, torch.Generator().manual_seed(0))
print("x[0]:", repr(tok.decode(x[0].tolist())), "\ny[0]:", repr(tok.decode(y[0].tolist())), "<- the same text, shifted by one")
print(f"uniform guess: loss ln({V}) = {math.log(V):.3f}, perplexity {V}")
```
```text
519,097 training characters, 57,677 validation characters, vocabulary 98
x[0]: 'ular att' 
y[0]: 'lar attr' <- the same text, shifted by one
uniform guess: loss ln(98) = 4.585, perplexity 98
```

Why split by position and not at random? Text is strongly correlated across nearby positions; a random split would put almost the same sentences in train and validation and make the model look better than it is (ds.04). Splitting the end of the text off is the honest version.

### 3.2 Count-based baselines (n-gram models)

Before any neural network, the honest baseline: estimate `P(next | previous n−1 characters)` by counting, with **additive smoothing** `k` so that unseen events do not get probability zero: `p = (count(context, next) + k) / (count(context) + k·V)`.

```python run
tr, va = train_data.numpy(), val_data.numpy()
def ngram_val_loss(train, val, n, k):
    c = n - 1                                                         # context length
    def codes(arr):
        ctx = np.zeros(len(arr) - c, dtype=np.int64)
        for j in range(c): ctx = ctx * V + arr[j:len(arr) - c + j]
        return ctx, arr[c:].astype(np.int64)
    ctx_t, nxt_t = codes(train)
    uj, cj = np.unique(ctx_t * V + nxt_t, return_counts=True)
    uc, cc = np.unique(ctx_t, return_counts=True)
    ctx_v, nxt_v = codes(val)
    def look(u, cnt, q):
        pos = np.clip(np.searchsorted(u, q), 0, len(u) - 1)
        return np.where(u[pos] == q, cnt[pos], 0)
    nj, nc = look(uj, cj, ctx_v * V + nxt_v), look(uc, cc, ctx_v)
    return float(-np.log((nj + k) / (nc + k * V)).mean())

rows = []
for n in range(1, 7):
    losses = {k: ngram_val_loss(tr, va, n, k) for k in (1.0, 0.1, 0.01)}
    kbest = min(losses, key=losses.get)
    rows.append([f"{n}-gram (context {n - 1})", *[round(v, 3) for v in losses.values()], kbest, round(math.exp(losses[kbest]), 2)])
ngram_table = pd.DataFrame(rows, columns=["model", "val loss k=1", "k=0.1", "k=0.01", "best k", "best perplexity"])
print(ngram_table.to_string(index=False))
BASELINE = min(min(r[1:4]) for r in rows)
print(f"\nbest count-based validation loss: {BASELINE:.3f} (perplexity {math.exp(BASELINE):.2f}) | the target every neural model below must beat")
```
```text
             model  val loss k=1  k=0.1  k=0.01  best k  best perplexity
1-gram (context 0)         3.220  3.220   3.220    0.01            25.02
2-gram (context 1)         2.352  2.349   2.354    0.10            10.48
3-gram (context 2)         1.833  1.751   1.763    0.10             5.76
4-gram (context 3)         1.774  1.499   1.483    0.01             4.41
5-gram (context 4)         2.047  1.592   1.523    0.01             4.59
6-gram (context 5)         2.398  1.845   1.719    0.01             5.58

best count-based validation loss: 1.483 (perplexity 4.41) | the target every neural model below must beat
```

> **Predict the output.** As the order `n` grows, will the validation loss keep falling? Why or why not?

<details><summary>Answer</summary>

It falls at first (more context predicts the next character better), reaches a minimum at the 4-gram (3 characters of context), and then **rises**: with a long context almost every context in the validation text has never been seen in training (count 0), and the smoothed estimate falls back to a near-uniform guess. This is overfitting of a count table: more parameters than the data can support. Neural language models get around this because they *share statistical strength* between similar contexts instead of memorising each exact context. See the table above for the numbers.

</details>

### 3.3 The simplest neural language model is the bigram table

Make the model `logits = W[x_t]` with `W` a `(V, V)` embedding table: the row for the current character holds the scores for the next character. Train it by gradient descent with cross-entropy. It must converge to the bigram counts, so its loss should match `ngram_val_loss(…, n=2)`. That match is a check that our loss, batching and training loop are right.

```python run
class BigramLM(nn.Module):
    def __init__(self, V):
        super().__init__(); self.table = nn.Embedding(V, V)
    def forward(self, x): return self.table(x)                         # (B, T) -> (B, T, V)

@torch.no_grad()
def eval_loss(model, d, T=64, B=64, n_batches=40, seed=123):
    model.eval(); gen = torch.Generator().manual_seed(seed); tot = 0.0
    for _ in range(n_batches):
        x, y = get_batch(d, B, T, gen)
        tot += F.cross_entropy(model(x).reshape(-1, V), y.reshape(-1)).item()
    return tot / n_batches

torch.manual_seed(0)
bigram = BigramLM(V)
opt = torch.optim.Adam(bigram.parameters(), lr=0.05)
gen = torch.Generator().manual_seed(0)
for step in range(601):
    x, y = get_batch(train_data, 64, 64, gen)
    loss = F.cross_entropy(bigram(x).reshape(-1, V), y.reshape(-1))
    opt.zero_grad(); loss.backward(); opt.step()
    if step in (0, 100, 300, 600): print(f"step {step:>3}  train loss {loss.item():.3f}")
count_bigram = ngram_val_loss(tr, va, 2, 0.1)
print(f"neural bigram validation loss {eval_loss(bigram, val_data):.3f} | count-based bigram {count_bigram:.3f} (they agree up to sampling noise)")
```
```text
step   0  train loss 5.101
step 100  train loss 2.493
step 300  train loss 2.459
step 600  train loss 2.418
neural bigram validation loss 2.348 | count-based bigram 2.349 (they agree up to sampling noise)
```

### 3.4 Try it

1. Explain why the bigram model cannot beat its count-based twin however long you train, but a model with more context can.
2. Compute the perplexity of the neural bigram on the validation text, and say in one sentence what it means.
3. Use `ngram_val_loss` with `k=0` for order 3. What goes wrong, and why does the loss become infinite?

## 4. Recurrent networks from scratch

### 4.1 The idea: one cell, applied step by step, with a memory

A fully connected network has no notion of order. A **recurrent neural network (RNN)** reads the sequence one token at a time and carries a **hidden state** `h`, a vector that summarises everything seen so far. The same small network (the *cell*) is reused at every step:

```
h_t = tanh( W_xh · x_t + W_hh · h_(t-1) + b )
```

`x_t` is the embedding of token `t` (size `D`), `h_t` has size `H`, so `W_xh` is `(H, D)` and `W_hh` is `(H, H)`. The weights are **shared across time**: a sequence of any length uses the same parameters, just as a convolution reuses one filter across positions. To predict the next token, a `Linear(H, V)` reads `h_t`.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Make a step-by-step animation of a recurrent neural network unrolled over 5 time steps. Show inputs x_1 to x_5 (size D) entering the same cell box, with the hidden state h (size H) passing as an arrow from each step to the next, and the same weights W_xh and W_hh labelled as shared. Add the formula h_t = tanh(W_xh x_t + W_hh h_(t-1) + b) under the cell and a Linear(H,V) output on top."

### 4.2 The cell written by hand, checked against `nn.RNN`

PyTorch stores the weights as `weight_ih_l0` `(H, D)`, `weight_hh_l0` `(H, H)` and two biases. We copy them into our loop and compare.

```python run
def rnn_forward(x, w_ih, w_hh, b_ih, b_hh, h0=None):
    """x: (B, T, D). Returns outputs (B, T, H) and the last hidden state (B, H)."""
    B, T, _ = x.shape
    h = torch.zeros(B, w_hh.shape[0]) if h0 is None else h0
    outs = []
    for t in range(T):                                                  # the loop IS the recurrence
        h = torch.tanh(x[:, t] @ w_ih.T + b_ih + h @ w_hh.T + b_hh)
        outs.append(h)
    return torch.stack(outs, dim=1), h

torch.manual_seed(0)
B_, T_, D_, H_ = 3, 5, 4, 6
rnn = nn.RNN(D_, H_, batch_first=True)                                  # batch_first: inputs are (B, T, D)
x = torch.randn(B_, T_, D_)
ours, ours_h = rnn_forward(x, rnn.weight_ih_l0, rnn.weight_hh_l0, rnn.bias_ih_l0, rnn.bias_hh_l0)
theirs, theirs_h = rnn(x)
print("parameter shapes:", {n: tuple(p.shape) for n, p in rnn.named_parameters()})
print("outputs", tuple(theirs.shape), "= (B, T, H) | last hidden state", tuple(theirs_h.shape), "= (num_layers, B, H)")
print("hand-written recurrence equals nn.RNN:", bool(torch.allclose(ours, theirs, atol=1e-6)), bool(torch.allclose(ours_h, theirs_h[0], atol=1e-6)))
print("the last output step is the last hidden state:", bool(torch.equal(theirs[:, -1], theirs_h[0])))
```
```text
parameter shapes: {'weight_ih_l0': (6, 4), 'weight_hh_l0': (6, 6), 'bias_ih_l0': (6,), 'bias_hh_l0': (6,)}
outputs (3, 5, 6) = (B, T, H) | last hidden state (1, 3, 6) = (num_layers, B, H)
hand-written recurrence equals nn.RNN: True True
the last output step is the last hidden state: True
```

Shapes to remember: `outputs` has one vector per time step, `(B, T, H)`; `h_n` is only the *last* state for each layer, `(layers, B, H)` (note: layers first, even with `batch_first=True`).

### 4.3 Backpropagation through time, and why gradients vanish

Unrolled over `T` steps, an RNN is a network `T` layers deep with **the same weight matrix `W_hh` at every layer**. Backpropagation through time multiplies the gradient by (roughly) `W_hh^T · diag(1 − h²)` once per step going backwards. You saw in ml.01 what repeated multiplication by a matrix does: if its largest singular value is below 1 the gradient shrinks exponentially, above 1 it blows up.

Measure it. We take a randomly initialised tanh RNN, backpropagate from the loss at the **last** step, and print the norm of the gradient arriving at the input of each earlier step. The recurrent matrix is scaled so that its **spectral radius** (largest absolute eigenvalue) equals a chosen `gain`.

```python run
def grad_vs_distance(gain, T=80, D=8, H=32, seed=0, cell="rnn"):
    torch.manual_seed(seed)
    if cell == "rnn":
        m = nn.RNN(D, H, batch_first=True)
        if gain is not None:                                             # gain=None keeps PyTorch's default initialisation
            with torch.no_grad():
                w = torch.randn(H, H)
                m.weight_hh_l0.copy_(w * gain / torch.linalg.eigvals(w).abs().max())      # rescale to the chosen spectral radius
    else:
        m = {"gru": nn.GRU, "lstm": nn.LSTM}[cell](D, H, batch_first=True)
    x = torch.randn(1, T, D, requires_grad=True)
    out, _ = m(x)
    out[0, -1].sum().backward()                                          # a loss that depends only on the LAST step
    return x.grad[0].norm(dim=1)                                         # (T,) gradient norm at each input position

dists = [1, 5, 10, 20, 40, 79]
rows = []
for gain in (0.5, 1.0, 1.5):
    g = grad_vs_distance(gain)
    rows.append([f"tanh RNN, spectral radius {gain}", *[f"{g[-1 - d].item():.1e}" for d in dists]])
print(pd.DataFrame(rows, columns=["model", *[f"{d} steps back" for d in dists]]).to_string(index=False))
```
```text
                        model 1 steps back 5 steps back 10 steps back 20 steps back 40 steps back 79 steps back
tanh RNN, spectral radius 0.5      6.1e-01      2.2e-02       2.6e-04       4.2e-08       5.8e-15       0.0e+00
tanh RNN, spectral radius 1.0      1.1e+00      4.9e-01       1.1e-01       6.9e-03       2.2e-05       2.9e-09
tanh RNN, spectral radius 1.5      1.3e+00      2.8e+00       1.5e+00       2.4e-01       5.2e-02       2.4e-01
```

> **Predict the output.** With spectral radius 0.5, how many steps back does the gradient still carry a usable signal? What changes with radius 1.5, and why does tanh stop the explosion from being as bad as with a linear RNN?

<details><summary>Answer</summary>

With radius 0.5 the gradient shrinks by a factor of about 5 to 50 per step: by 10 steps back it is 2.6e-4 and by 40 steps back it is 6e-15, numerically nothing. The model **cannot learn** that the loss depends on something 40 steps ago, because the signal that would tell it so never arrives. With radius 1.0 it still decays, more slowly (2.2e-5 at 40 steps). With radius 1.5 the gradient does **not** vanish (2.8 at 5 steps, 0.05 to 0.24 at 40 to 79 steps), and it can be large: the matrix amplifies. Why not an explosion here? tanh saturates (its derivative is near 0 for large inputs), which caps the growth. In a linear or ReLU RNN nothing caps it, which is why gradient clipping (4.4) is standard practice.

</details>

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot gradient norm (log scale y axis, 1e-15 to 10) against steps back from the loss (x axis 0 to 80) for a tanh RNN at three spectral radii. Use roughly these points (1, 5, 10, 20, 40 steps back): radius 0.5: 0.61, 2.2e-2, 2.6e-4, 4.2e-8, 5.8e-15; radius 1.0: 1.1, 0.49, 0.11, 6.9e-3, 2.2e-5; radius 1.5: 1.3, 2.8, 1.5, 0.24, 0.052. Label the vanishing region."

### 4.4 Exploding gradients: clipping

Vanishing is a *modelling* problem (the next section's gates); exploding is a numerical one, with a cheap cure: if the global gradient norm exceeds a threshold, rescale it to that threshold. The direction is kept, only the step size is bounded. Here a ReLU RNN with spectral radius 2 produces a gradient norm of tens of thousands.

```python run
torch.manual_seed(0)
m = nn.RNN(8, 32, batch_first=True, nonlinearity="relu")               # ReLU RNN: nothing stops the growth
with torch.no_grad():
    w = torch.randn(32, 32); m.weight_hh_l0.copy_(w * 2.0 / torch.linalg.eigvals(w).abs().max())
x = torch.randn(4, 60, 8)
out, _ = m(x)
out[:, -1].pow(2).mean().backward()
total = torch.nn.utils.clip_grad_norm_(m.parameters(), max_norm=1.0)       # returns the norm BEFORE clipping
after = torch.sqrt(sum(p.grad.pow(2).sum() for p in m.parameters()))
print(f"gradient norm before clipping {total.item():.3e}, after clip_grad_norm_(max_norm=1.0): {after.item():.3f}")
```
```text
gradient norm before clipping 1.765e+04, after clip_grad_norm_(max_norm=1.0): 1.000
```

### 4.5 A character-level language model with a recurrent core

The model: `Embedding(V, D) → RNN/GRU/LSTM(D, H) → Linear(H, V)`. It outputs logits for the next character at every position. One training function serves every model in this chapter (it only assumes `model(x)` maps `(B, T)` ids to `(B, T, V)` logits), with the habits that matter: AdamW, linear warm-up then cosine decay, gradient clipping at 1.0, and a validation loss on fixed batches.

```python run
class RecurrentLM(nn.Module):
    def __init__(self, V, kind="lstm", D=48, H=128, layers=1):
        super().__init__()
        self.emb = nn.Embedding(V, D)
        core = {"rnn": nn.RNN, "gru": nn.GRU, "lstm": nn.LSTM}[kind]
        self.rnn = core(D, H, num_layers=layers, batch_first=True)
        self.out = nn.Linear(H, V)
    def forward(self, x):
        h, _ = self.rnn(self.emb(x))                                    # (B, T, H)
        return self.out(h)                                              # (B, T, V)

def n_params(m): return sum(p.numel() for p in m.parameters())

def train_lm(model, steps, lr=3e-3, B=64, T=64, seed=0, clip=1.0, wd=0.0, warmup=50, log_every=0):
    gen = torch.Generator().manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=wd)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / warmup) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * s / steps))))
    t0, hist = time.time(), []
    for step in range(steps):
        model.train()
        x, y = get_batch(train_data, B, T, gen)
        loss = F.cross_entropy(model(x).reshape(-1, V), y.reshape(-1))
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
        opt.step(); sched.step()
        hist.append(loss.item())
        if log_every and (step + 1) % log_every == 0:
            print(f"  step {step + 1:>5}  train loss {np.mean(hist[-log_every:]):.3f}  val loss {eval_loss(model, val_data):.3f}")
    return {"val_loss": eval_loss(model, val_data), "train_loss": float(np.mean(hist[-50:])), "seconds": time.time() - t0, "params": n_params(model)}

torch.manual_seed(0)
m = RecurrentLM(V, "lstm")
x, y = get_batch(train_data, 4, 16, torch.Generator().manual_seed(0))
print("logits shape:", tuple(m(x).shape), "= (B, T, V) | untrained loss", round(F.cross_entropy(m(x).reshape(-1, V), y.reshape(-1)).item(), 3), "vs ln V =", round(math.log(V), 3))
```
```text
logits shape: (4, 16, 98) = (B, T, V) | untrained loss 4.59 vs ln V = 4.585
```

## 5. Why RNNs forget, and LSTM and GRU

### 5.1 The gates

The fix for vanishing gradients is to give the network an **additive** memory path and let it *choose* when to write, keep and read. The **LSTM** (long short-term memory) keeps a second vector, the **cell state** `c`, and controls it with three **gates**: sigmoid layers whose outputs in `(0, 1)` act as soft switches.

```
i = σ(W_i·[x_t, h_(t-1)])     input gate:  how much new information to write
f = σ(W_f·[x_t, h_(t-1)])     forget gate: how much of the old cell to keep
g = tanh(W_g·[x_t, h_(t-1)])  candidate:   the new information
o = σ(W_o·[x_t, h_(t-1)])     output gate: how much of the cell to expose
c_t = f ⊙ c_(t-1) + i ⊙ g      <-- the additive path: the cell changes by "keep a fraction, add a bit"
h_t = o ⊙ tanh(c_t)
```

If `f ≈ 1` and `i ≈ 0` the cell is copied unchanged, and the gradient flows back along `c` multiplied only by `f`, not by a weight matrix and a tanh derivative at every step. The **GRU** is a lighter cousin with two gates and no separate cell. Both are checked against PyTorch below; PyTorch stacks the gates in the order `i, f, g, o` (LSTM) and `r, z, n` (GRU).

```python run
def lstm_forward(x, w_ih, w_hh, b_ih, b_hh):
    B, T, _ = x.shape
    H = w_hh.shape[1]
    h = torch.zeros(B, H); c = torch.zeros(B, H); outs = []
    for t in range(T):
        gates = x[:, t] @ w_ih.T + b_ih + h @ w_hh.T + b_hh              # (B, 4H): all four gates in one matmul
        i, f, g, o = gates.chunk(4, dim=1)
        i, f, g, o = torch.sigmoid(i), torch.sigmoid(f), torch.tanh(g), torch.sigmoid(o)
        c = f * c + i * g
        h = o * torch.tanh(c)
        outs.append(h)
    return torch.stack(outs, 1), (h, c)

def gru_forward(x, w_ih, w_hh, b_ih, b_hh):
    B, T, _ = x.shape
    H = w_hh.shape[1]
    h = torch.zeros(B, H); outs = []
    for t in range(T):
        gi = x[:, t] @ w_ih.T + b_ih; gh = h @ w_hh.T + b_hh
        i_r, i_z, i_n = gi.chunk(3, dim=1); h_r, h_z, h_n = gh.chunk(3, dim=1)
        r = torch.sigmoid(i_r + h_r)                                     # reset gate
        z = torch.sigmoid(i_z + h_z)                                     # update gate
        n = torch.tanh(i_n + r * h_n)                                    # candidate (the reset gate scales the recurrent part)
        h = (1 - z) * n + z * h
        outs.append(h)
    return torch.stack(outs, 1), h

torch.manual_seed(0)
x = torch.randn(3, 7, 4)
lstm, gru = nn.LSTM(4, 6, batch_first=True), nn.GRU(4, 6, batch_first=True)
o1, (h1, c1) = lstm_forward(x, lstm.weight_ih_l0, lstm.weight_hh_l0, lstm.bias_ih_l0, lstm.bias_hh_l0)
o2, h2 = gru_forward(x, gru.weight_ih_l0, gru.weight_hh_l0, gru.bias_ih_l0, gru.bias_hh_l0)
t1, (th1, tc1) = lstm(x); t2, th2 = gru(x)
print("LSTM by hand equals nn.LSTM:", bool(torch.allclose(o1, t1, atol=1e-6)), bool(torch.allclose(c1, tc1[0], atol=1e-6)), "| weight_ih shape", tuple(lstm.weight_ih_l0.shape), "= (4H, D)")
print("GRU  by hand equals nn.GRU :", bool(torch.allclose(o2, t2, atol=1e-6)), "| weight_ih shape", tuple(gru.weight_ih_l0.shape), "= (3H, D)")
print("parameters for D=48, H=128: RNN", n_params(nn.RNN(48, 128)), "| GRU", n_params(nn.GRU(48, 128)), "| LSTM", n_params(nn.LSTM(48, 128)), "(1x, 3x, 4x the recurrent weights)")
```
```text
LSTM by hand equals nn.LSTM: True True | weight_ih shape (24, 4) = (4H, D)
GRU  by hand equals nn.GRU : True | weight_ih shape (18, 4) = (3H, D)
parameters for D=48, H=128: RNN 22784 | GRU 68352 | LSTM 91136 (1x, 3x, 4x the recurrent weights)
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one LSTM cell at time t as a diagram. Inputs are x_t, h_(t-1) and c_(t-1). Show the forget gate f, input gate i, candidate g and output gate o as small boxes, with the cell state c running along the top as a highway where c_t = f*c_(t-1) + i*g. Highlight the additive path, and show h_t = o*tanh(c_t) leaving at the bottom. Label gate values between 0 and 1 as valves."

### 5.2 Gradient flow, compared

Repeat the measurement of 4.3 with the gated cells, all at PyTorch's **default initialisation**, and add the common trick of initialising the LSTM **forget-gate bias** to a positive number (so that the cell starts out remembering). For a fair comparison the plain RNN appears twice: with its default initialisation, and with the carefully tuned spectral radius 1.0 of 4.3.

```python run
def lstm_forget_bias(seed=0, T=80, D=8, H=32, bias=1.0):
    torch.manual_seed(seed)
    m = nn.LSTM(D, H, batch_first=True)
    with torch.no_grad():
        m.bias_ih_l0[H:2 * H] = bias; m.bias_hh_l0[H:2 * H] = 0.0          # the forget-gate slice is the second quarter
    x = torch.randn(1, T, D, requires_grad=True)
    out, _ = m(x); out[0, -1].sum().backward()
    return x.grad[0].norm(dim=1)

rows = []
for name, g in {"tanh RNN, default init": grad_vs_distance(None), "tanh RNN, tuned radius 1.0": grad_vs_distance(1.0),
                "GRU, default init": grad_vs_distance(None, cell="gru"), "LSTM, default init": grad_vs_distance(None, cell="lstm"),
                "LSTM, forget bias = 1": lstm_forget_bias(bias=1.0), "LSTM, forget bias = 3": lstm_forget_bias(bias=3.0)}.items():
    rows.append([name, *[f"{g[-1 - d].item():.1e}" for d in dists]])
print(pd.DataFrame(rows, columns=["model", *[f"{d} steps back" for d in dists]]).to_string(index=False))
```
```text
                     model 1 steps back 5 steps back 10 steps back 20 steps back 40 steps back 79 steps back
    tanh RNN, default init      9.5e-01      1.0e-01       2.7e-03       4.7e-06       6.4e-12       3.7e-23
tanh RNN, tuned radius 1.0      1.1e+00      4.9e-01       1.1e-01       6.9e-03       2.2e-05       2.9e-09
         GRU, default init      5.2e-01      2.1e-02       2.1e-03       1.5e-05       9.0e-10       4.6e-18
        LSTM, default init      1.9e-01      2.1e-02       2.5e-03       1.6e-05       6.5e-10       1.7e-17
     LSTM, forget bias = 1      2.6e-01      9.8e-02       4.0e-02       3.2e-03       6.8e-05       4.2e-08
     LSTM, forget bias = 3      1.4e-01      1.1e-01       7.9e-02       3.8e-02       2.0e-02       1.3e-02
```

Read it carefully, because it corrects a common belief. At **default initialisation the gated cells do better than the default plain RNN** (1e-17 against 1e-23 at 79 steps), but all of them still decay exponentially, and a *tuned* plain RNN (radius 1.0) is better than the default GRU and LSTM. The gates start near 0.5, so the cell forgets about half of its content at every step. What the gates really give you is the *possibility* to hold memory: when the forget gate is pushed toward 1, the cell is copied almost unchanged and the gradient survives. The forget-bias rows show it: with bias 3 the gradient at 79 steps back is 1.3e-2, about **twenty orders of magnitude** larger than the default LSTM's. Whether training *finds* that setting is the question the next experiment answers.

### 5.3 A memory test the plain RNN fails

A task built to need long memory: the input is a sequence of random digits in `0..9`, the **label is the first digit**, and the model reads the whole sequence and answers at the end. The first digit must be remembered for `L−1` steps of noise.

```python run
def memory_task(kind, L, steps=1500, H=48, seed=0, forget_bias=0.0):
    torch.manual_seed(seed)
    emb = nn.Embedding(10, 16)
    core = {"rnn": nn.RNN, "gru": nn.GRU, "lstm": nn.LSTM}[kind](16, H, batch_first=True)
    if forget_bias:
        with torch.no_grad(): core.bias_ih_l0[H:2 * H] = forget_bias
    head = nn.Linear(H, 10)
    params = list(emb.parameters()) + list(core.parameters()) + list(head.parameters())
    opt = torch.optim.Adam(params, lr=5e-3)
    g = torch.Generator().manual_seed(seed + 1)
    def batch(B):
        x = torch.randint(0, 10, (B, L), generator=g); return x, x[:, 0]
    for _ in range(steps):
        x, y = batch(64)
        h, _ = core(emb(x)); loss = F.cross_entropy(head(h[:, -1]), y)
        opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(params, 1.0); opt.step()
    with torch.no_grad():
        x, y = batch(1000); h, _ = core(emb(x))
        return (head(h[:, -1]).argmax(1) == y).float().mean().item()

t0 = time.time()
rows = []
for name, kind, fb in [("RNN", "rnn", 0.0), ("GRU", "gru", 0.0), ("LSTM", "lstm", 0.0), ("LSTM, forget bias 1", "lstm", 1.0)]:
    rows.append([name, *[round(memory_task(kind, L, forget_bias=fb), 3) for L in (5, 10, 20)]])
print(pd.DataFrame(rows, columns=["model (1,500 steps each)", "accuracy, L=5", "L=10", "L=20"]).to_string(index=False))
print(f"chance level is 0.100 | {time.time() - t0:.0f}s")
```
```text
model (1,500 steps each)  accuracy, L=5  L=10  L=20
                     RNN            1.0 0.888 0.276
                     GRU            1.0 1.000 1.000
                    LSTM            1.0 1.000 0.112
     LSTM, forget bias 1            1.0 1.000 0.793
chance level is 0.100 | 182s
```

> **Predict the output.** Before reading the table: does the plain RNN keep up as `L` grows? Which of the three gated variants do you expect to solve `L=20`? Would you bet that the LSTM beats the GRU?

<details><summary>Answer</summary>

The plain RNN solves `L=5`, is already imperfect at `L=10` (0.89), and is far from solving `L=20` (0.28): it cannot carry the digit reliably through the noise. The GRU solves all three lengths. The **default LSTM stays at chance at `L=20`** (about 0.11) in this budget, although it solved `L=10`; with the forget-gate bias set to 1 it learns the task (about 0.8 here, and still improving). So the LSTM does *not* automatically beat the GRU: with default initialisation it may take far longer to discover that it should keep its cell, which is exactly the reason the forget-bias trick became standard. These are single runs (one seed each) with a fixed budget of 1,500 steps; read them as an illustration of *how hard it is to learn to remember*, not as a ranking of architectures.

</details>

### 5.4 Padding, packing and the last hidden state

Real batches contain sequences of different lengths, padded to the longest. A plain RNN reads the padding too, so its "last hidden state" for a short sequence has been updated by many meaningless pad steps. Two correct options: pick the output at the **true last position** `lengths-1`, or use `pack_padded_sequence`, which makes the RNN skip the pads and return the right final state.

```python run
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
torch.manual_seed(0)
emb = nn.Embedding(10, 8, padding_idx=0)
gru = nn.GRU(8, 16, batch_first=True)
seqs = [[3, 4, 5, 6, 7], [2, 1, 4], [5, 9]]
lengths = torch.tensor([len(s) for s in seqs])
padded = torch.tensor([s + [0] * (5 - len(s)) for s in seqs])
with torch.no_grad():
    out, h_last = gru(emb(padded))
    naive = h_last[0]                                                          # last STEP, i.e. after the pads
    picked = out[torch.arange(3), lengths - 1]                                 # output at the true last token
    packed = pack_padded_sequence(emb(padded), lengths, batch_first=True, enforce_sorted=False)
    _, h_packed = gru(packed)
    alone = torch.stack([gru(emb(torch.tensor([s])))[1][0, 0] for s in seqs])  # each sequence run on its own: the reference
print("naive last state equals the sequence run alone?   ", [bool(torch.allclose(naive[i], alone[i], atol=1e-6)) for i in range(3)])
print("picking position length-1 equals it?              ", [bool(torch.allclose(picked[i], alone[i], atol=1e-6)) for i in range(3)])
print("pack_padded_sequence's final state equals it?     ", [bool(torch.allclose(h_packed[0][i], alone[i], atol=1e-6)) for i in range(3)])
```
```text
naive last state equals the sequence run alone?    [True, False, False]
picking position length-1 equals it?               [True, True, True]
pack_padded_sequence's final state equals it?      [True, True, True]
```

### 5.5 Layers, directions and shapes

| Option | Effect | Output shape (`batch_first=True`) |
|---|---|---|
| `num_layers=L` | stack L recurrent layers; layer k reads layer k−1's outputs | `out (B,T,H)`, `h_n (L,B,H)` |
| `bidirectional=True` | a second RNN reads the sequence backwards; outputs are concatenated | `out (B,T,2H)`, `h_n (2L,B,H)` |
| `dropout=p` | dropout between layers (not after the last) | same |

A **bidirectional** model sees the future, so it is fine for *classifying* a whole sentence and **wrong for next-token prediction**: the answer would be in its input. This is the same leakage idea as ds.04, in a new place.

```python run
m = nn.LSTM(10, 7, num_layers=2, bidirectional=True, batch_first=True)
out, (h, c) = m(torch.randn(3, 9, 10))
print("out", tuple(out.shape), "= (B, T, 2H) | h_n", tuple(h.shape), "= (layers x directions, B, H)")
```
```text
out (3, 9, 14) = (B, T, 2H) | h_n (4, 3, 7) = (layers x directions, B, H)
```

### 5.6 The recurrent language models against the count baseline

Same data, same training budget (1,500 steps of 64 sequences of 64 characters), three cores, hidden size chosen to keep the parameter counts comparable.

```python run
results = {}
for name, kind, H in [("RNN", "rnn", 160), ("GRU", "gru", 96), ("LSTM", "lstm", 80)]:
    torch.manual_seed(0)
    m = RecurrentLM(V, kind, D=48, H=H)
    results[name] = train_lm(m, steps=1500, lr=3e-3)
    results[name]["model"] = m
tbl = pd.DataFrame({k: {kk: vv for kk, vv in v.items() if kk != "model"} for k, v in results.items()}).T
tbl["val perplexity"] = np.exp(tbl["val_loss"])
print(tbl.round(3).to_string())
print(f"\nbest count-based model (4-gram): val loss {BASELINE:.3f}, perplexity {math.exp(BASELINE):.2f}")
```
```text
      val_loss  train_loss  seconds   params  val perplexity
RNN      1.392       1.289  102.698  54082.0           4.022
GRU      1.377       1.306  165.926  56258.0           3.962
LSTM     1.522       1.511   75.550  54242.0           4.579

best count-based model (4-gram): val loss 1.483, perplexity 4.41
```

Read the table with care. The RNN and the GRU both beat the best count-based model (4-gram, 1.483); their difference (1.392 against 1.377) is far smaller than what a second seed would change, so do not rank them. The LSTM is behind (1.522), and its training loss (about 1.51) is as high as its validation loss: it is **under-trained**, not over-fit, with this hidden size and budget. This does not show that LSTMs are worse; it shows that the same step budget favours different cells differently, and that a single run per architecture cannot rank them (the memory experiment of 5.3 shows the opposite pattern on a different task).

### 5.7 Try it

1. Initialise `weight_hh_l0` of the tanh RNN as the identity matrix times 0.9 and re-run the distance table of 4.3. What do you see, and why is it a (limited) fix?
2. Change `memory_task` so that the label is the *last* digit. Which model solves it, and why is this easy even for the plain RNN?
3. In 5.4, what happens to the gradient of the loss with respect to the padded positions when you use `pack_padded_sequence`?

## 6. Attention

### 6.1 The idea

An RNN squeezes everything it has read into one vector `h`, and information from far back has to survive many steps. **Attention** removes the bottleneck: to compute the representation of position `t`, look *directly* at every other position and take a **weighted average** of what they hold, with weights that depend on how relevant each one is to `t`.

Think of a dictionary lookup made soft. Each position produces three vectors:

- a **query** `q`: "what am I looking for?"
- a **key** `k`: "what do I contain, for matching purposes?"
- a **value** `v`: "what do I hand over if I am chosen?"

The match score between position `i` (asking) and position `j` (answering) is the dot product `q_i · k_j`. A softmax over `j` turns the scores into weights that sum to 1, and the output for `i` is the weighted sum of the values:

```
out_i = Σ_j  softmax_j( q_i · k_j / √d )  ·  v_j
```

In **self-attention** all three come from the same sequence `x` through three learned matrices: `q = x·W_q`, `k = x·W_k`, `v = x·W_v`.

### 6.2 A tiny case by hand

Three tokens, vectors of size 2. Everything is small enough to check with a pencil.

```python run
q = torch.tensor([[1., 0.], [0., 1.], [1., 1.]])
k = torch.tensor([[1., 0.], [0., 1.], [1., 1.]])
v = torch.tensor([[10., 0.], [0., 10.], [5., 5.]])
scores = q @ k.T                                                    # (3, 3): scores[i, j] = q_i . k_j
print("scores q @ k^T:\n", scores)
w = F.softmax(scores / math.sqrt(2), dim=-1)                        # each row sums to 1
print("weights (row i = how much position i listens to each position):\n", w.numpy().round(3))
print("row sums:", w.sum(1).tolist())
print("output = weights @ v:\n", (w @ v).numpy().round(3))
print("position 0 (query [1,0]) gives equal top weight to positions 0 and 2, whose keys [1,0] and [1,1] both match it: weights", w[0].numpy().round(3))
print("position 2 (query [1,1]) mixes the values and lands on [5, 5], the midpoint of the first two:", (w @ v)[2].numpy().round(2))
```
```text
scores q @ k^T:
 tensor([[1., 0., 1.],
        [0., 1., 1.],
        [1., 1., 2.]])
weights (row i = how much position i listens to each position):
 [[0.401 0.198 0.401]
 [0.198 0.401 0.401]
 [0.248 0.248 0.503]]
row sums: [1.0, 1.0, 1.0]
output = weights @ v:
 [[6.017 3.983]
 [3.983 6.017]
 [5.    5.   ]]
position 0 (query [1,0]) gives equal top weight to positions 0 and 2, whose keys [1,0] and [1,1] both match it: weights [0.401 0.198 0.401]
position 2 (query [1,1]) mixes the values and lands on [5, 5], the midpoint of the first two: [5. 5.]
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw attention for 3 tokens with 2-dim vectors: q = k = [[1,0],[0,1],[1,1]], v = [[10,0],[0,10],[5,5]]. Show the 3x3 score matrix q k^T = [[1,0,1],[0,1,1],[1,1,2]], then the softmax weights (scores divided by sqrt(2)) as a heatmap with rows summing to 1: [.401,.198,.401], [.198,.401,.401], [.248,.248,.503]. Finish with arrows showing outputs [6.02,3.98], [3.98,6.02], [5,5] as weighted mixes of v."

### 6.3 Self-attention with every shape

Now batched, with learned projections. Read the shapes in the comments; this is the single most important block of the chapter.

```python run
class SelfAttention(nn.Module):
    """Single head. x: (B, T, C)  ->  (B, T, d_v).  `causal=True` forbids looking at later positions."""
    def __init__(self, C, d, causal=False):
        super().__init__()
        self.Wq, self.Wk, self.Wv = nn.Linear(C, d, bias=False), nn.Linear(C, d, bias=False), nn.Linear(C, d, bias=False)
        self.causal, self.d = causal, d
    def forward(self, x, return_weights=False):
        B, T, C = x.shape
        q, k, v = self.Wq(x), self.Wk(x), self.Wv(x)                    # each (B, T, d)
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.d)            # (B, T, d) @ (B, d, T) -> (B, T, T)
        if self.causal:
            mask = torch.tril(torch.ones(T, T, dtype=torch.bool))        # lower triangle = allowed
            scores = scores.masked_fill(~mask, float("-inf"))            # forbidden -> -inf -> weight exactly 0 after softmax
        w = F.softmax(scores, dim=-1)                                   # (B, T, T): each ROW sums to 1
        out = w @ v                                                     # (B, T, T) @ (B, T, d) -> (B, T, d)
        return (out, w) if return_weights else out

torch.manual_seed(0)
B_, T_, C_, d_ = 2, 5, 16, 8
x = torch.randn(B_, T_, C_)
att = SelfAttention(C_, d_, causal=False)
out, w = att(x, return_weights=True)
print(f"x            {tuple(x.shape)}   (batch, tokens, model width C)")
print(f"q, k, v      {tuple(att.Wq(x).shape)}   (batch, tokens, head width d)")
print(f"scores/weights {tuple(w.shape)}   (batch, query position, key position): T x T per sequence")
print(f"output       {tuple(out.shape)}   (batch, tokens, d): one new vector per token")
print("every weight row sums to 1:", bool(torch.allclose(w.sum(-1), torch.ones(B_, T_))))
ref = F.scaled_dot_product_attention(att.Wq(x), att.Wk(x), att.Wv(x))
print("equals PyTorch's F.scaled_dot_product_attention:", bool(torch.allclose(out, ref, atol=1e-6)))
print("parameters:", n_params(att), "= 3 x (C x d) =", 3 * C_ * d_, "<- independent of the sequence length T")
```
```text
x            (2, 5, 16)   (batch, tokens, model width C)
q, k, v      (2, 5, 8)   (batch, tokens, head width d)
scores/weights (2, 5, 5)   (batch, query position, key position): T x T per sequence
output       (2, 5, 8)   (batch, tokens, d): one new vector per token
every weight row sums to 1: True
equals PyTorch's F.scaled_dot_product_attention: True
parameters: 384 = 3 x (C x d) = 384 <- independent of the sequence length T
```

### 6.4 Why divide by √d?

If the entries of `q` and `k` have variance 1, the dot product of two `d`-dimensional vectors has variance `d`, so its standard deviation is `√d`. With large `d` the scores become huge, the softmax saturates into an almost one-hot vector, and its gradient is nearly zero. Dividing by `√d` brings the variance back to 1. Measure it.

```python run
torch.manual_seed(0)
rows = []
for d in (4, 64, 1024):
    q = torch.randn(10_000, d); k = torch.randn(10_000, d)
    raw = (q * k).sum(-1)
    row = torch.randn(1000, 16, d) @ torch.randn(1000, d, 1)               # 1000 softmax rows over 16 keys
    for name, s in (("unscaled", row.squeeze(-1)), ("scaled", row.squeeze(-1) / math.sqrt(d))):
        p = F.softmax(s, -1)
        rows.append([d, name, round(s.std().item(), 2), round(p.max(-1).values.mean().item(), 3), round(-(p * p.clamp_min(1e-12).log()).sum(-1).mean().item(), 3)])
print(pd.DataFrame(rows, columns=["d", "scores", "std of scores", "mean max weight", "mean entropy (max ln 16 = 2.773)"]).to_string(index=False))
```
```text
   d   scores  std of scores  mean max weight  mean entropy (max ln 16 = 2.773)
   4 unscaled           1.98            0.422                             1.774
   4   scaled           0.99            0.232                             2.387
  64 unscaled           7.95            0.852                             0.393
  64   scaled           0.99            0.251                             2.354
1024 unscaled          32.30            0.965                             0.086
1024   scaled           1.01            0.252                             2.345
```

At `d=1024` the unscaled softmax is almost always one-hot (max weight near 1, entropy near 0): the layer has stopped averaging and the gradient through it has vanished. The scaled version stays in the same healthy range at every `d`.

### 6.5 Masks

Two kinds of mask change which positions may attend to which.

- **Causal mask** (language models): position `t` may look at positions `≤ t` only, because at generation time the future does not exist. Without it the model would simply read the answer off its input.
- **Padding mask**: keys at pad positions must get weight zero.

Both are implemented by setting forbidden scores to `-inf` *before* the softmax. We test the causal mask the way one should test it: **change a future token and check that earlier outputs do not move.**

```python run
torch.manual_seed(0)
att_c = SelfAttention(16, 8, causal=True)
x = torch.randn(1, 6, 16)
out, w = att_c(x, return_weights=True)
print("causal weights (row = query position; zero above the diagonal):\n", w[0].detach().numpy().round(2))
x2 = x.clone(); x2[0, 4:] = torch.randn(2, 16)                          # change tokens 4 and 5 only
out2 = att_c(x2)
print("outputs at positions 0-3 unchanged when tokens 4-5 change:", bool(torch.allclose(out[0, :4], out2[0, :4], atol=1e-6)))
print("outputs at positions 4-5 do change:", not bool(torch.allclose(out[0, 4:], out2[0, 4:])))

# padding mask for the keys: the last 2 of 6 positions are padding
scores = torch.randn(1, 6, 6)
pad = torch.tensor([[False, False, False, False, True, True]])
wp = F.softmax(scores.masked_fill(pad[:, None, :], float("-inf")), -1)
print("weight given to the two padding keys:", wp[0, :, 4:].abs().max().item())
# the classic trap: a row where EVERY key is masked
bad = F.softmax(torch.full((1, 3), float("-inf")), -1)
print("softmax of an all -inf row:", bad.tolist(), "<- NaN poisons the whole network; always leave at least one allowed key")
```
```text
causal weights (row = query position; zero above the diagonal):
 [[1.   0.   0.   0.   0.   0.  ]
 [0.41 0.59 0.   0.   0.   0.  ]
 [0.3  0.46 0.24 0.   0.   0.  ]
 [0.45 0.16 0.21 0.18 0.   0.  ]
 [0.3  0.16 0.13 0.23 0.19 0.  ]
 [0.12 0.2  0.17 0.19 0.16 0.15]]
outputs at positions 0-3 unchanged when tokens 4-5 change: True
outputs at positions 4-5 do change: True
weight given to the two padding keys: 0.0
softmax of an all -inf row: [[nan, nan, nan]] <- NaN poisons the whole network; always leave at least one allowed key
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 6x6 attention weight heatmap for a causal mask. Rows are query positions 0 to 5, columns are key positions 0 to 5. Fill the lower triangle with weights (row 0 is [1], row 1 is [.41,.59], row 5 is about [.12,.2,.17,.19,.16,.15]) and show the upper triangle as blocked (-inf before softmax, weight 0). Add a side animation where changing token 4 does not change outputs at positions 0 to 3."

### 6.6 Self-attention has no sense of order

Attention averages over positions with weights computed from content. Shuffle the tokens and every token gets the same output, just in a shuffled position: the layer is **permutation-equivariant**. A model built only from it would treat "dog bites man" and "man bites dog" identically. Order must be injected into the input.

```python run
torch.manual_seed(0)
att0 = SelfAttention(16, 8, causal=False)
x = torch.randn(1, 6, 16)
perm = torch.tensor([3, 0, 5, 1, 4, 2])
y, y_perm = att0(x), att0(x[:, perm])
print("attention(shuffled x) == shuffled attention(x):", bool(torch.allclose(y[:, perm], y_perm, atol=1e-6)), "<- no notion of order")
```
```text
attention(shuffled x) == shuffled attention(x): True <- no notion of order
```

### 6.7 Positional encodings

Give each position an extra vector added to the token embedding. Two standard choices:

- **Learned**: an `nn.Embedding(block_size, C)` indexed by position. Simple, works, cannot extrapolate beyond `block_size`.
- **Sinusoidal** (the original transformer): fixed vectors, `PE[t, 2i] = sin(t / 10000^(2i/C))` and `PE[t, 2i+1] = cos(…)`. Each pair of dimensions is a wave of a different wavelength; a position is a unique "clock reading".

(Modern models mostly use *rotary* embeddings (RoPE), which rotate queries and keys by an angle that depends on position; the idea is the same, to make `q·k` depend on the relative offset.)

```python run
def sinusoidal(T, C):
    pos = torch.arange(T)[:, None].float()
    i = torch.arange(0, C, 2).float()
    angle = pos / (10000 ** (i / C))
    pe = torch.zeros(T, C); pe[:, 0::2] = torch.sin(angle); pe[:, 1::2] = torch.cos(angle)
    return pe

pe = sinusoidal(64, 32)
print("shape (T, C):", tuple(pe.shape), "| values stay in [-1, 1]:", float(pe.min()), float(pe.max()))
print("first positions, first 6 dims:\n", pe[:4, :6].numpy().round(3))
# the dot product of two positions depends (almost) only on the OFFSET between them
for off in (1, 5):
    dots = [float(pe[t] @ pe[t + off]) for t in (0, 10, 30)]
    print(f"pe[t] . pe[t+{off}] at t = 0, 10, 30:", [round(v, 3) for v in dots])
# with positions added, shuffling the tokens now changes the result
yp = att0(x + sinusoidal(6, 16))                                          # encode, then attend
y_shuffled_then_pos = att0(x[:, perm] + sinusoidal(6, 16))                # shuffle the tokens, then add positions to the new slots
print("with positions, 'attend then shuffle' differs from 'shuffle then attend':", not bool(torch.allclose(yp[:, perm], y_shuffled_then_pos, atol=1e-4)), "<- order now matters")
```
```text
shape (T, C): (64, 32) | values stay in [-1, 1]: -1.0 1.0
first positions, first 6 dims:
 [[ 0.     1.     0.     1.     0.     1.   ]
 [ 0.841  0.54   0.533  0.846  0.311  0.95 ]
 [ 0.909 -0.416  0.902  0.431  0.591  0.807]
 [ 0.141 -0.99   0.993 -0.116  0.813  0.583]]
pe[t] . pe[t+1] at t = 0, 10, 30: [15.314, 15.314, 15.314]
pe[t] . pe[t+5] at t = 0, 10, 30: [11.777, 11.777, 11.777]
with positions, 'attend then shuffle' differs from 'shuffle then attend': True <- order now matters
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot sinusoidal positional encoding for a sequence of 64 positions and 32 dimensions as a heatmap (x axis dimension, y axis position, values between -1 and 1). Next to it, draw lines of the first four dimension pairs against position, showing sin and cos waves of increasing wavelength. Highlight that every position gets a unique pattern, like clock hands."

### 6.8 Multi-head attention

One attention head produces one weighted average, so it can only pursue one kind of relationship at a time. **Multi-head attention** runs `h` heads in parallel, each with its own projections, in smaller subspaces of size `d = C/h`, and concatenates the results. The total cost is the same as one big head. The reshaping is where bugs live, so every step is annotated.

```python run
class MultiHeadAttention(nn.Module):
    def __init__(self, C, n_heads, causal=True):
        super().__init__()
        assert C % n_heads == 0, "model width must be divisible by the number of heads"
        self.h, self.d, self.causal = n_heads, C // n_heads, causal
        self.qkv = nn.Linear(C, 3 * C)                                  # q, k, v for ALL heads in one matmul
        self.proj = nn.Linear(C, C)                                     # mixes the heads after concatenation
    def forward(self, x, return_weights=False):
        B, T, C = x.shape
        q, k, v = self.qkv(x).split(C, dim=2)                           # three tensors (B, T, C)
        q, k, v = (t.view(B, T, self.h, self.d).transpose(1, 2) for t in (q, k, v))   # (B, T, C) -> (B, T, h, d) -> (B, h, T, d)
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.d)            # (B, h, T, d) @ (B, h, d, T) -> (B, h, T, T)
        if self.causal:
            scores = scores.masked_fill(~torch.tril(torch.ones(T, T, dtype=torch.bool)), float("-inf"))
        w = F.softmax(scores, dim=-1)                                   # (B, h, T, T)
        y = (w @ v).transpose(1, 2).contiguous().view(B, T, C)          # (B, h, T, d) -> (B, T, h, d) -> (B, T, C): heads concatenated
        y = self.proj(y)                                                # (B, T, C)
        return (y, w) if return_weights else y

torch.manual_seed(0)
mha = MultiHeadAttention(C=32, n_heads=4)
x = torch.randn(2, 10, 32)
y, w = mha(x, return_weights=True)
print("input (B,T,C)", tuple(x.shape), "-> output", tuple(y.shape), "| attention weights (B,h,T,T)", tuple(w.shape))
print("parameters:", n_params(mha), "= qkv (32x96+96) + proj (32x32+32) =", 32 * 96 + 96 + 32 * 32 + 32)

# referee: nn.MultiheadAttention with our weights copied in
ref = nn.MultiheadAttention(32, 4, batch_first=True)
with torch.no_grad():
    ref.in_proj_weight.copy_(mha.qkv.weight); ref.in_proj_bias.copy_(mha.qkv.bias)
    ref.out_proj.weight.copy_(mha.proj.weight); ref.out_proj.bias.copy_(mha.proj.bias)
causal_mask = torch.triu(torch.ones(10, 10, dtype=torch.bool), diagonal=1)           # True = NOT allowed
ry, rw = ref(x, x, x, attn_mask=causal_mask, average_attn_weights=False)
print("matches nn.MultiheadAttention (output and per-head weights):", bool(torch.allclose(y, ry, atol=1e-5)), bool(torch.allclose(w, rw, atol=1e-5)))
```
```text
input (B,T,C) (2, 10, 32) -> output (2, 10, 32) | attention weights (B,h,T,T) (2, 4, 10, 10)
parameters: 4224 = qkv (32x96+96) + proj (32x32+32) = 4224
matches nn.MultiheadAttention (output and per-head weights): True True
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the tensor shapes in multi-head attention with B=2, T=10, C=32 and 4 heads (d=8). Show a step-by-step flow: x (2,10,32), then qkv, then q,k,v each (2,10,32), then reshape to (2,4,10,8), then scores (2,4,10,10), then softmax weights times v back to (2,4,10,8), then concatenated (2,10,32) and projection. Colour each head differently so the split and re-join are clear."

### 6.9 The price of attention: the T × T matrix

The score matrix has `T²` entries per head. Doubling the context quadruples the memory and compute of this part, which is why long contexts are expensive and why methods such as FlashAttention (compute exactly the same thing without storing the full matrix) matter.

```python run
for T in (64, 1024, 8192, 131072):
    mb = 4 * T * T / 1e6
    print(f"T = {T:>7,}: one head's float32 score matrix = {mb:>12,.1f} MB" + ("  <- per head, per sequence, per layer" if T == 131072 else ""))
```
```text
T =      64: one head's float32 score matrix =          0.0 MB
T =   1,024: one head's float32 score matrix =          4.2 MB
T =   8,192: one head's float32 score matrix =        268.4 MB
T = 131,072: one head's float32 score matrix =     68,719.5 MB  <- per head, per sequence, per layer
```

### 6.10 Try it

1. In `SelfAttention`, set `d=1` and `C=16`. What do the weights look like, and what is the output shape?
2. Why is the output of attention a *convex combination* of the value vectors? What does that imply about its range?
3. Make the causal test fail on purpose by applying the mask *after* the softmax instead of before. Which of the two printed checks catches the bug?

## 7. The transformer

### 7.1 The block

A transformer is a stack of identical **blocks**. Each block has two sub-layers, each wrapped in a **residual connection** (the idea from ml.03) and a **layer normalisation**:

```
x = x + Attention( LayerNorm(x) )      <- tokens exchange information
x = x + MLP( LayerNorm(x) )            <- each token is processed on its own
```

The attention sub-layer *mixes across positions*; the MLP (`Linear(C, 4C) → GELU → Linear(4C, C)`) *transforms each position independently*. Putting the norm *before* each sub-layer ("pre-norm") makes deep stacks train reliably.

**LayerNorm vs BatchNorm.** Batch norm normalises each feature across the batch and needs batch statistics; this fails for sequences of varying length and small batches. Layer norm normalises across the **features of each token separately**, so its result does not depend on the other examples in the batch, and it behaves the same in training and evaluation.

```python run
torch.manual_seed(0)
ln = nn.LayerNorm(16)
x = torch.randn(4, 7, 16) * 3 + 5                                        # (B, T, C)
y = ln(x)
print(f"each token vector is normalised on its own: largest |mean| over tokens {y.mean(-1).abs().max().item():.1e} | mean std {y.std(-1, unbiased=False).mean().item():.4f}")
print("output for sample 0 does not depend on the other samples:", bool(torch.allclose(ln(x[:1]), y[:1], atol=1e-6)))
bn = nn.BatchNorm1d(16).train()
yb = bn(x.reshape(-1, 16)).reshape(4, 7, 16)
print("batch norm's output for sample 0 DOES depend on the batch:", not bool(torch.allclose(bn(x[:1].reshape(-1, 16)).reshape(1, 7, 16), yb[:1], atol=1e-3)))
```
```text
each token vector is normalised on its own: largest |mean| over tokens 1.4e-07 | mean std 1.0000
output for sample 0 does not depend on the other samples: True
batch norm's output for sample 0 DOES depend on the batch: True
```

### 7.2 A small GPT

Putting the pieces together: token embedding plus position embedding, `N` blocks, a final layer norm, and a linear layer to vocabulary logits. The output layer **shares its weights with the token embedding** ("weight tying"): the embedding maps a token to a vector, and the output layer maps a vector to token scores, which are the same relationship in two directions; tying saves `V×C` parameters and usually helps small models.

The attention class also supports a **cache** for fast generation (section 8.5). During training the cache is `None` and the code is exactly the multi-head attention of 6.8.

```python run
class CausalSelfAttention(nn.Module):
    def __init__(self, C, n_heads):
        super().__init__()
        self.h, self.d = n_heads, C // n_heads
        self.qkv, self.proj = nn.Linear(C, 3 * C), nn.Linear(C, C)
    def forward(self, x, cache=None):
        B, T, C = x.shape
        q, k, v = (t.view(B, T, self.h, self.d).transpose(1, 2) for t in self.qkv(x).split(C, dim=2))      # (B, h, T, d)
        if cache is not None:                                           # generation: x holds only the NEW tokens
            if cache["k"] is not None:
                k, v = torch.cat([cache["k"], k], dim=2), torch.cat([cache["v"], v], dim=2)
            cache["k"], cache["v"] = k, v
        S = k.shape[2]                                                  # number of keys = past + new
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.d)            # (B, h, T, S)
        allowed = torch.arange(S)[None, :] <= (torch.arange(T)[:, None] + S - T)   # query i sits at absolute position S-T+i
        w = F.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
        return self.proj((w @ v).transpose(1, 2).contiguous().view(B, T, C))

class Block(nn.Module):
    def __init__(self, C, n_heads, p_drop=0.0):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(C), nn.LayerNorm(C)
        self.attn = CausalSelfAttention(C, n_heads)
        self.mlp = nn.Sequential(nn.Linear(C, 4 * C), nn.GELU(), nn.Linear(4 * C, C))
        self.drop = nn.Dropout(p_drop)
    def forward(self, x, cache=None):
        x = x + self.drop(self.attn(self.ln1(x), cache))
        return x + self.drop(self.mlp(self.ln2(x)))

class GPT(nn.Module):
    def __init__(self, V, block_size=64, C=64, n_heads=4, n_layers=2, p_drop=0.0):
        super().__init__()
        self.block_size = block_size
        self.tok, self.pos = nn.Embedding(V, C), nn.Embedding(block_size, C)
        self.blocks = nn.ModuleList([Block(C, n_heads, p_drop) for _ in range(n_layers)])
        self.ln_f = nn.LayerNorm(C)
        self.head = nn.Linear(C, V, bias=False)
        self.head.weight = self.tok.weight                              # weight tying
        self.apply(self._init)
        for n, p in self.named_parameters():                            # scale residual-branch outputs: keeps the stream's variance bounded
            if n.endswith("proj.weight") or n.endswith("mlp.2.weight"):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * n_layers))
    @staticmethod
    def _init(m):
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, std=0.02)
            if m.bias is not None: nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, std=0.02)
    def forward(self, idx, caches=None):
        B, T = idx.shape
        start = 0 if caches is None or caches[0]["k"] is None else caches[0]["k"].shape[2]
        assert start + T <= self.block_size, f"sequence of {start + T} exceeds block_size {self.block_size}"
        x = self.tok(idx) + self.pos(torch.arange(start, start + T))     # (B, T, C)
        for i, blk in enumerate(self.blocks):
            x = blk(x, None if caches is None else caches[i])
        return self.head(self.ln_f(x))                                  # (B, T, V)

torch.manual_seed(0)
gpt = GPT(V, block_size=64, C=64, n_heads=4, n_layers=2)
x, y = get_batch(train_data, 8, 64, torch.Generator().manual_seed(0))
logits = gpt(x)
print("logits", tuple(logits.shape), "= (B, T, V)")
print(f"initial loss {F.cross_entropy(logits.reshape(-1, V), y.reshape(-1)).item():.3f} vs ln V = {math.log(V):.3f}   <- a correct, untrained model is uniformly unsure")
print("weights tied:", gpt.head.weight is gpt.tok.weight, "| total parameters:", n_params(gpt))
```
```text
logits (8, 64, 98) = (B, T, V)
initial loss 4.530 vs ln V = 4.585   <- a correct, untrained model is uniformly unsure
weights tied: True | total parameters: 110464
```

### 7.3 Where do the parameters live?

With model width `C`, one block has `4C²` weights in attention (`qkv` is `3C²`, `proj` is `C²`) and `8C²` in the MLP, so about `12C²` per layer, plus the embeddings.

```python run
def param_breakdown(m, C, L):
    emb = n_params(m.tok) + n_params(m.pos)
    attn = sum(n_params(b.attn) for b in m.blocks); mlp = sum(n_params(b.mlp) for b in m.blocks)
    norms = sum(n_params(b.ln1) + n_params(b.ln2) for b in m.blocks) + n_params(m.ln_f)
    return {"embeddings": emb, "attention": attn, "mlp": mlp, "layer norms": norms, "total": n_params(m), "12*C^2*L estimate": 12 * C * C * L}
print(pd.Series(param_breakdown(gpt, 64, 2)).to_string())
for C, L in [(64, 2), (96, 4), (768, 12)]:
    print(f"C={C:>3}, layers={L:>2}: blocks hold about {12 * C * C * L:>12,} parameters" + ("   <- GPT-2 small, plus a 50,257-token embedding" if C == 768 else ""))
```
```text
embeddings            10368
attention             33280
mlp                   66176
layer norms             640
total                110464
12*C^2*L estimate     98304
C= 64, layers= 2: blocks hold about       98,304 parameters
C= 96, layers= 4: blocks hold about      442,368 parameters
C=768, layers=12: blocks hold about   84,934,656 parameters   <- GPT-2 small, plus a 50,257-token embedding
```

### 7.4 Tests a transformer must pass

Three cheap tests find most implementation bugs. You already saw the first (initial loss ≈ ln V). The other two:

```python run
# 1. Causality: the loss at position t must not depend on tokens AFTER t. Check with gradients.
gpt.eval()
x, _ = get_batch(train_data, 1, 32, torch.Generator().manual_seed(1))
emb_in = gpt.tok(x).detach().requires_grad_(True)
def forward_from_embeddings(e):
    h = e + gpt.pos(torch.arange(e.shape[1]))
    for blk in gpt.blocks: h = blk(h)
    return gpt.head(gpt.ln_f(h))
t = 10
forward_from_embeddings(emb_in)[0, t].sum().backward()
g = emb_in.grad[0].abs().sum(-1)
print(f"gradient of the output at position {t} w.r.t. input positions > {t}: max = {g[t + 1:].max().item():.1e}  (must be exactly 0)")
print(f"... and w.r.t. positions <= {t}: min = {g[:t + 1].min().item():.1e}  (must be > 0)")

# 2. It can overfit one small batch (loss -> ~0): if not, something is broken
torch.manual_seed(0)
m = GPT(V, 64, 64, 4, 2)
opt = torch.optim.Adam(m.parameters(), lr=3e-3)
xb, yb = get_batch(train_data, 4, 32, torch.Generator().manual_seed(2))
for step in range(151):
    loss = F.cross_entropy(m(xb).reshape(-1, V), yb.reshape(-1))
    opt.zero_grad(); loss.backward(); opt.step()
    if step in (0, 50, 100, 150): print(f"step {step:>3}  loss {loss.item():.4f}")
```
```text
gradient of the output at position 10 w.r.t. input positions > 10: max = 0.0e+00  (must be exactly 0)
... and w.r.t. positions <= 10: min = 1.7e+01  (must be > 0)
step   0  loss 4.3865
step  50  loss 0.0790
step 100  loss 0.0122
step 150  loss 0.0067
```

### 7.5 RNN against transformer: the trade-off

| | RNN / LSTM | Transformer |
|---|---|---|
| Steps that must run one after another | `T` (inherently sequential) | 1 per layer: all positions in parallel |
| Path from token `j` to token `i` | `|i−j|` steps | 1 step (direct attention) |
| Memory of the past | a fixed-size state `h` | all past keys and values: grows with `T` |
| Cost per layer | `O(T·H²)` | `O(T²·C + T·C²)` |
| Generating one new token | `O(1)` with the state | `O(T)` with a KV cache |
| Needs positional information | no (order is built in) | yes |

Parallelism is what let transformers train on vastly more data and become the dominant architecture; the price is the `T²` term and a memory that grows with the context.

### 7.6 Try it

1. Change `n_layers` from 2 to 4 and recompute the breakdown. Which component scales with the number of layers, which does not?
2. Remove weight tying (comment out the `self.head.weight = self.tok.weight` line). By how much does the parameter count change and does it equal `V × C`?
3. Replace the pre-norm block by post-norm (`x = ln(x + attn(x))`). Make the overfit-one-batch test deeper (8 layers) and compare how fast the loss falls.

## 8. Training and generating

### 8.1 Train the transformer against everything so far

Same data, same optimiser and schedule, same 1,500 steps of 64 sequences of 64 characters. Parameter counts differ (the transformer is larger), and that is part of the honest comparison.

```python run
torch.manual_seed(0)
gpt = GPT(V, block_size=64, C=64, n_heads=4, n_layers=2)
print("parameters:", n_params(gpt))
res_gpt = train_lm(gpt, steps=1500, lr=3e-3, log_every=500)
rows = [["4-gram counts (best k)", "table", BASELINE, math.exp(BASELINE), np.nan]]
for name, r in results.items():
    rows.append([name + " (recurrent)", r["params"], r["val_loss"], math.exp(r["val_loss"]), r["seconds"]])
rows.append(["GPT (2 layers, C=64)", res_gpt["params"], res_gpt["val_loss"], math.exp(res_gpt["val_loss"]), res_gpt["seconds"]])
print(pd.DataFrame(rows, columns=["model", "parameters", "val loss", "val perplexity", "train seconds"]).round(3).to_string(index=False))
```
```text
parameters: 110464
  step   500  train loss 2.140  val loss 1.557
  step  1000  train loss 1.392  val loss 1.347
  step  1500  train loss 1.222  val loss 1.287
                 model parameters  val loss  val perplexity  train seconds
4-gram counts (best k)      table     1.483           4.406            NaN
       RNN (recurrent)      54082     1.392           4.022        102.698
       GRU (recurrent)      56258     1.377           3.962        165.926
      LSTM (recurrent)      54242     1.522           4.579         75.550
  GPT (2 layers, C=64)     110464     1.287           3.623        234.446
```

> **Predict the output.** Does the 110k-parameter transformer beat the 54k-parameter recurrent models after the same number of steps? If it does not, what would you check before concluding that attention is worse?

<details><summary>Answer</summary>

The transformer wins here: validation loss 1.287 (perplexity 3.62) against 1.377 for the best recurrent model and 1.483 for the count-based baseline, even though it also has twice the parameters, which is part of why it wins. It is also the slowest to train per step (234 s against 75 to 166 s). Two cautions. First, the comparison is neither parameter-matched nor tuned, and it is one seed, so a margin of 0.09 in loss is encouraging but not a verdict on architectures. Second, transformers are famous for *scaling* with data and compute; at 110k parameters and 1,500 steps the lead is modest. If a transformer is not ahead in your own experiment, check (1) is the training loss still falling (under-trained), (2) learning rate and warm-up (try `1e-3` and `6e-3`), (3) the sanity tests of 7.4, (4) a large train-validation gap (over-fitting: dropout, weight decay, more data).

</details>

### 8.2 Sampling: from probabilities to text

The model outputs a probability distribution over the next character. **Generation** picks one, appends it, and repeats (autoregressive decoding). How you pick matters as much as the model:

- **Greedy** (`temperature=0`): always the most likely token. Deterministic, and prone to repetitive loops.
- **Temperature** `τ`: divide the logits by `τ` before the softmax. `τ<1` sharpens the distribution (safer, more repetitive), `τ>1` flattens it (more varied, more errors).
- **Top-k**: keep only the `k` most likely tokens, renormalise.
- **Top-p (nucleus)**: keep the smallest set of tokens whose probabilities add up to at least `p`. The set adapts to the model's confidence: few tokens when it is sure, more when it is not.

```python run
def next_token_probs(logits, temperature=1.0, top_k=None, top_p=None):
    """logits: (B, V). Returns the distribution the next token is drawn from after all filters."""
    logits = logits / temperature
    if top_k is not None:
        kth = logits.topk(min(top_k, logits.shape[-1])).values[:, -1, None]
        logits = logits.masked_fill(logits < kth, float("-inf"))
    if top_p is not None:
        sl, si = logits.sort(descending=True)
        p = F.softmax(sl, -1)
        drop = (p.cumsum(-1) - p) > top_p                                  # tokens that come AFTER the nucleus is already full
        logits = torch.full_like(logits, float("-inf")).scatter(-1, si, sl.masked_fill(drop, float("-inf")))
    return F.softmax(logits, -1)

@torch.no_grad()
def sample(model, prompt_ids, n_new, temperature=1.0, top_k=None, top_p=None, seed=0):
    model.eval()
    g = torch.Generator().manual_seed(seed)
    ids = torch.tensor([prompt_ids])
    for _ in range(n_new):
        logits = model(ids[:, -model.block_size:])[:, -1]                  # (1, V): only the LAST position predicts the next token
        if temperature == 0: nxt = logits.argmax(-1, keepdim=True)
        else: nxt = torch.multinomial(next_token_probs(logits, temperature, top_k, top_p), 1, generator=g)
        ids = torch.cat([ids, nxt], dim=1)
    return ids[0].tolist()

toy = torch.tensor([[4.0, 3.0, 2.0, 1.0, 0.0, -1.0]])
print("logits:", toy[0].tolist())
for name, kw in [("temperature 1.0", {}), ("temperature 0.5", dict(temperature=0.5)), ("temperature 2.0", dict(temperature=2.0)),
                 ("top-k 2", dict(top_k=2)), ("top-p 0.9", dict(top_p=0.9))]:
    print(f"{name:<16}", next_token_probs(toy, **kw)[0].numpy().round(3))
print("greedy picks token", int(toy.argmax()), "| top_k=1 leaves a single token:", next_token_probs(toy, top_k=1)[0].numpy().round(3))
```
```text
logits: [4.0, 3.0, 2.0, 1.0, 0.0, -1.0]
temperature 1.0  [0.634 0.233 0.086 0.032 0.012 0.004]
temperature 0.5  [0.865 0.117 0.016 0.002 0.    0.   ]
temperature 2.0  [0.414 0.251 0.152 0.092 0.056 0.034]
top-k 2          [0.731 0.269 0.    0.    0.    0.   ]
top-p 0.9        [0.665 0.245 0.09  0.    0.    0.   ]
greedy picks token 0 | top_k=1 leaves a single token: [1. 0. 0. 0. 0. 0.]
```

Now real text. The prompt is `"The "`; each setting uses the same random seed so that differences come from the setting.

```python run
prompt = tok.encode("The ")
for name, kw in [("greedy (temperature 0)", dict(temperature=0)), ("temperature 0.7", dict(temperature=0.7)),
                 ("temperature 1.0", dict(temperature=1.0)), ("temperature 1.5", dict(temperature=1.5)),
                 ("temperature 1.0, top-p 0.9", dict(temperature=1.0, top_p=0.9))]:
    print(f"--- {name}")
    print(tok.decode(sample(gpt, prompt, 220, seed=1, **kw)))
```
```text
--- greedy (temperature 0)
The statement is a contained in the same as a class of the standard to the
                                                                                                                                                     
--- temperature 0.7
The module
    string and the format all statement
is not iterated.


The "type" statement is changed for the "except" that clause of a means withough
   keywords the case attribute for an "__getattribute__()" is mand "__ini
--- temperature 1.0
The multiple
  still name an assignment changed, as upporting only be scoped
spresed. The type happers completed and egat inh type of functions for genis-plements
     as upporty as for set is modules upoint noked as
   "0.0
--- temperature 1.5
The multiple
prseur of "__letem__()" aexcepts, and it: ! [0ffN', laz6'" show
spresed, or debuwls 1@Frj" class, so

beegrs incl| breError(C)
obKufbut=Ne).__ge_bo>>[, Q, atNure}")

Ystrings: +58; doe, f<MEPython is mosd("Or0.c
--- temperature 1.0, top-p 0.9
The multiple
  string the lettic functions for and it specification object to
presed in the class defaults pownernabenger including any means withoughes debuggers
     attributes_nots_or_(self, other)
object.__ilitem__(self,
```

Reading a few samples by eye is useful, but it does not scale and it is easy to fool oneself. Two numbers that can be measured automatically:

- **valid word rate**: the fraction of generated alphabetic words that occur in the training text (a model that invents spelling scores low);
- **diversity**: the fraction of distinct 8-character windows (a model stuck in a loop scores low).

```python run
train_words = set(w.lower() for w in re.findall(r"[A-Za-z]+", text[:len(train_data)]))
def text_stats(s):
    ws = re.findall(r"[A-Za-z]+", s)
    windows = [s[i:i + 8] for i in range(len(s) - 8)]
    return np.mean([w.lower() in train_words for w in ws]), len(set(windows)) / len(windows)

rows = []
real = val_data.tolist()
vstats = [text_stats(tok.decode(real[i:i + 1000])) for i in range(0, 5000, 1000)]
rows.append(["real validation text", *np.mean(vstats, 0)])
for name, kw in [("greedy", dict(temperature=0)), ("temperature 0.5", dict(temperature=0.5)), ("temperature 0.8", dict(temperature=0.8)),
                 ("temperature 1.0", dict(temperature=1.0)), ("temperature 1.3", dict(temperature=1.3)), ("temperature 1.0, top-p 0.9", dict(temperature=1.0, top_p=0.9))]:
    st = [text_stats(tok.decode(sample(gpt, tok.encode("The "), 800, seed=s, **kw)[4:])) for s in range(2)]
    rows.append([name, *np.mean(st, 0)])
print(pd.DataFrame(rows, columns=["text from", "valid word rate", "distinct 8-grams"]).round(3).to_string(index=False))
```
```text
                 text from  valid word rate  distinct 8-grams
      real validation text            0.948             0.574
                    greedy            1.000             0.091
           temperature 0.5            0.973             0.432
           temperature 0.8            0.816             0.974
           temperature 1.0            0.720             0.982
           temperature 1.3            0.553             0.994
temperature 1.0, top-p 0.9            0.844             0.808
```

> **Predict the output.** Which setting gives the highest valid-word rate, and which gives the lowest diversity? Is there a setting that is good on both?

<details><summary>Answer</summary>

The two numbers pull in opposite directions. Greedy decoding has the best valid-word rate (1.000) and by far the worst diversity (0.091: it falls into a loop and repeats). Temperature 1.3 is diverse (0.994) but only 55% of its words exist in the training text. The real text sits at 0.948 valid and 0.574 distinct. No setting matches both: temperature 0.5 is close on words (0.973) but too repetitive (0.432); temperature 0.8 has 0.816 valid words but is almost *too* diverse (0.974). That the diversity of generated text is higher than real text is itself informative: real text repeats phrases ("of the", "is a") far more than a small model that is inventing character sequences. Top-p 0.9 at temperature 1.0 (0.844 valid, 0.808 distinct) is a good compromise between its two neighbours. The practical rule is: choose the setting on held-out measurements against the real text, not by taste.

</details>

### 8.3 The KV cache

In the sampling loop above, every new token re-runs the whole model over the entire context, although the keys and values of all earlier positions have not changed. A **KV cache** stores them: at each step only the *new* token is processed, its key and value are appended to the cache, and its query attends to all cached keys. The result must be **identical**; the cost per new token drops from `O(T)` positions to one. Our `CausalSelfAttention` already supports it (the `cache` argument of 7.2). We first prove equality, then time it.

```python run
@torch.no_grad()
def sample_cached(model, prompt_ids, n_new, temperature=1.0, top_k=None, top_p=None, seed=0):
    model.eval()
    g = torch.Generator().manual_seed(seed)
    assert len(prompt_ids) + n_new <= model.block_size, "the cached version cannot slide the window: prompt + new tokens must fit in block_size"
    caches = [{"k": None, "v": None} for _ in model.blocks]
    ids = list(prompt_ids)
    logits = model(torch.tensor([ids]), caches)[:, -1]                      # the prompt is processed ONCE, filling the caches
    for _ in range(n_new):
        if temperature == 0: nxt = logits.argmax(-1, keepdim=True)
        else: nxt = torch.multinomial(next_token_probs(logits, temperature, top_k, top_p), 1, generator=g)
        ids.append(int(nxt))
        logits = model(nxt, caches)[:, -1]                                  # ONE token in, one set of logits out
    return ids

# 1. The logits are the same as a full re-computation
gpt.eval()
ids = torch.tensor([tok.encode("The expression list is evaluated")])
with torch.no_grad():
    full = gpt(ids)
    caches = [{"k": None, "v": None} for _ in gpt.blocks]
    parts = [gpt(ids[:, :10], caches)] + [gpt(ids[:, t:t + 1], caches) for t in range(10, ids.shape[1])]
print("incremental logits equal full-sequence logits:", bool(torch.allclose(full, torch.cat(parts, dim=1), atol=1e-5)), "| max abs difference", float((full - torch.cat(parts, 1)).abs().max()))

# 2. The sampled text is the same
a = sample(gpt, tok.encode("The "), 59, temperature=0.8, seed=3)
b = sample_cached(gpt, tok.encode("The "), 59, temperature=0.8, seed=3)
print("same seed, same text from the cached and uncached samplers:", a == b)

# 3. The speed: at 64 tokens the difference is small; the benefit grows with the context length.
#    A random-weight model with a 512-token window is enough to time it (speed does not depend on the weights).
torch.manual_seed(0)
big = GPT(V, block_size=512, C=64, n_heads=4, n_layers=2).eval()
rows = []
for n_new in (60, 200, 450):
    t0 = time.time(); u = sample(big, [5, 6, 7, 8], n_new, temperature=1.0, seed=0); t_full = time.time() - t0
    t0 = time.time(); c_ = sample_cached(big, [5, 6, 7, 8], n_new, temperature=1.0, seed=0); t_cached = time.time() - t0
    rows.append([n_new, u == c_, f"{t_full:.2f}s", f"{t_cached:.2f}s", f"{t_full / t_cached:.1f}x", sum(4 + i for i in range(n_new)), 4 + n_new])
print(pd.DataFrame(rows, columns=["new tokens", "same text", "full recompute", "KV cache", "speed-up", "positions processed (full)", "(cached)"]).to_string(index=False))
c = caches[0]
print(f"cache for ONE layer, batch 1: k {tuple(c['k'].shape)} = (B, heads, T, d); all layers, k and v: {2 * len(caches) * c['k'].numel()} floats")
```
```text
incremental logits equal full-sequence logits: True | max abs difference 1.049041748046875e-05
same seed, same text from the cached and uncached samplers: True
 new tokens  same text full recompute KV cache speed-up  positions processed (full)  (cached)
         60       True          0.25s    0.19s     1.3x                        2010        64
        200       True          1.19s    0.66s     1.8x                       20700       204
        450       True          4.40s    1.53s     2.9x                      102825       454
cache for ONE layer, batch 1: k (1, 4, 32, 16) = (B, heads, T, d); all layers, k and v: 8192 floats
```

At 60 new tokens the cached sampler is only 1.3x faster (Python overhead dominates a tiny model); at 450 tokens it is 2.9x faster, and the gap keeps growing, because the uncached sampler's work grows with the square of the number of tokens (102,825 positions processed against 454). The text is identical in every row.

The cache is a trade of memory for time: it grows linearly with the context, per layer, per head. For a large model with a long context it is the dominant memory cost at inference, which is why techniques that shrink it (fewer key/value heads, quantisation) are a major engineering topic.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate a KV cache during text generation. Show 6 steps of one attention layer. At each step the new token produces one query, key and value; its key and value are appended to a growing cache of rectangles, and the query attends to all cached keys. Next to it, show the no-cache version recomputing every earlier position. Add a counter: positions processed, 102,825 versus 454 for 450 new tokens."

### 8.4 Does the model copy its training text?

A language model can memorise. Check by taking generated text and finding, for each start position, the longest stretch that appears **verbatim** in the training text. The yardstick is real *unseen* text: even human-written validation text shares many common phrases with the training text.

```python run
train_text = text[:len(train_data)]
def mean_longest_match(s, step=10, cap=80):
    best = []
    for i in range(0, len(s) - cap, step):
        n = 5
        while n < cap and s[i:i + n + 1] in train_text: n += 1
        best.append(n if s[i:i + n] in train_text else 0)
    return float(np.mean(best))

val_text = text[len(train_data):]
gen_text = tok.decode(sample(gpt, tok.encode("The "), 600, temperature=0.8, seed=5)[4:])
print(f"unseen real text: average longest verbatim match with the training text {mean_longest_match(val_text[:2000]):.1f} characters")
print(f"generated text  : average longest verbatim match with the training text {mean_longest_match(gen_text):.1f} characters")
```
```text
unseen real text: average longest verbatim match with the training text 36.0 characters
generated text  : average longest verbatim match with the training text 7.7 characters
```

The generated text matches the training text over 7.7 characters on average, against 36 for real unseen text: the model is not reciting, it is inventing. (Real text scores high because common phrases and code-like fragments genuinely repeat.) If the generated value were far above the real-text yardstick, the model would be reciting. With 110k parameters and 500k characters of training text, a small model cannot store the corpus; with a huge model and a small corpus, it can, which is a privacy and copyright concern, not just a quality one.

### 8.5 Try it

1. Train the GPT for 3,000 steps instead of 1,500. By how much does the validation loss change, and does it still beat the 4-gram baseline by a wider margin?
2. Change the `block_size` from 64 to 32 (the model sees less context). What happens to the validation loss, and what does that tell you about how much the model uses long context on this corpus?
3. Implement **repetition penalty**: before sampling, divide the logit of every token already generated in the last 20 positions by 1.3. Does the distinct-8-gram number improve? Does the valid-word rate fall?

## 9. Project: a character-level transformer that writes text

### 9.1 The brief

Build a small, honest, **end-to-end character-level language model** in a module someone else could run and trust:

1. **Tokeniser**: a character vocabulary that can be saved, with *strict* encoding (an unknown character in a prompt is an error, not a silent `<unk>`).
2. **Model**: the GPT of section 7 with a KV cache, configurable size.
3. **Training**: AdamW with warm-up and cosine decay, weight decay only on matrices, gradient clipping, a contiguous validation split, a fixed seed.
4. **Generation**: temperature, top-k, top-p, reproducible given a seed, with and without the cache.
5. **Evaluation**: validation loss and perplexity against the 4-gram count baseline, generated samples, valid-word rate.
6. **A deployable artefact**: one file holding weights, configuration and vocabulary, loadable into a `Writer` object.
7. **Tests** for the properties that matter: shapes, initial loss, causality, overfitting a batch, determinism, save/load equivalence, cache equivalence, sampling rules, input validation.

### 9.2 The module

```python run
proj = pathlib.Path(tempfile.mkdtemp()) / "charlm_project"; proj.mkdir()
(proj / "charlm.py").write_text('''"""charlm: a small character-level GPT (PyTorch)."""
import dataclasses, math, random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclasses.dataclass
class Config:
    block_size: int = 64
    n_layers: int = 3
    n_heads: int = 4
    width: int = 80
    steps: int = 2000
    batch_size: int = 32
    lr: float = 3e-3
    weight_decay: float = 0.01
    warmup: int = 50
    clip: float = 1.0
    seed: int = 0


class CharVocab:
    """Characters seen in the training text. Encoding is STRICT: an unknown character raises ValueError."""
    def __init__(self, chars):
        self.itos = list(chars)
        self.stoi = {c: i for i, c in enumerate(self.itos)}

    @classmethod
    def fit(cls, text):
        return cls(sorted(set(text)))

    def __len__(self):
        return len(self.itos)

    def encode(self, s):
        unknown = sorted({c for c in s if c not in self.stoi})
        if unknown:
            raise ValueError(f"characters not in the vocabulary: {unknown}")
        return [self.stoi[c] for c in s]

    def decode(self, ids):
        return "".join(self.itos[i] for i in ids)


# ---------- model ----------
class CausalSelfAttention(nn.Module):
    def __init__(self, C, n_heads):
        super().__init__()
        if C % n_heads:
            raise ValueError(f"width {C} must be divisible by n_heads {n_heads}")
        self.h, self.d = n_heads, C // n_heads
        self.qkv, self.proj = nn.Linear(C, 3 * C), nn.Linear(C, C)

    def forward(self, x, cache=None):
        B, T, C = x.shape
        q, k, v = (t.view(B, T, self.h, self.d).transpose(1, 2) for t in self.qkv(x).split(C, dim=2))
        if cache is not None:
            if cache["k"] is not None:
                k, v = torch.cat([cache["k"], k], dim=2), torch.cat([cache["v"], v], dim=2)
            cache["k"], cache["v"] = k, v
        S = k.shape[2]
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.d)
        allowed = torch.arange(S)[None, :] <= (torch.arange(T)[:, None] + S - T)
        w = F.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
        return self.proj((w @ v).transpose(1, 2).contiguous().view(B, T, C))


class Block(nn.Module):
    def __init__(self, C, n_heads):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(C), nn.LayerNorm(C)
        self.attn = CausalSelfAttention(C, n_heads)
        self.mlp = nn.Sequential(nn.Linear(C, 4 * C), nn.GELU(), nn.Linear(4 * C, C))

    def forward(self, x, cache=None):
        x = x + self.attn(self.ln1(x), cache)
        return x + self.mlp(self.ln2(x))


class GPT(nn.Module):
    def __init__(self, vocab_size, cfg):
        super().__init__()
        C, L = cfg.width, cfg.n_layers
        self.block_size = cfg.block_size
        self.tok, self.pos = nn.Embedding(vocab_size, C), nn.Embedding(cfg.block_size, C)
        self.blocks = nn.ModuleList([Block(C, cfg.n_heads) for _ in range(L)])
        self.ln_f = nn.LayerNorm(C)
        self.head = nn.Linear(C, vocab_size, bias=False)
        self.head.weight = self.tok.weight
        self.apply(self._init)
        for n, p in self.named_parameters():
            if n.endswith("proj.weight") or n.endswith("mlp.2.weight"):
                nn.init.normal_(p, mean=0.0, std=0.02 / math.sqrt(2 * L))

    @staticmethod
    def _init(m):
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, std=0.02)

    def new_caches(self):
        return [{"k": None, "v": None} for _ in self.blocks]

    def forward(self, idx, caches=None):
        B, T = idx.shape
        start = 0 if caches is None or caches[0]["k"] is None else caches[0]["k"].shape[2]
        if start + T > self.block_size:
            raise ValueError(f"sequence of {start + T} tokens exceeds block_size {self.block_size}")
        x = self.tok(idx) + self.pos(torch.arange(start, start + T))
        for i, blk in enumerate(self.blocks):
            x = blk(x, None if caches is None else caches[i])
        return self.head(self.ln_f(x))


# ---------- training ----------
def seed_everything(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def get_batch(data, B, T, gen):
    ix = torch.randint(0, len(data) - T - 1, (B,), generator=gen)
    return torch.stack([data[i:i + T] for i in ix]), torch.stack([data[i + 1:i + T + 1] for i in ix])


@torch.no_grad()
def eval_loss(model, data, T, B=64, n_batches=40, seed=123):
    model.eval()
    gen = torch.Generator().manual_seed(seed)
    total = 0.0
    for _ in range(n_batches):
        x, y = get_batch(data, B, T, gen)
        total += F.cross_entropy(model(x).reshape(-1, model.tok.num_embeddings), y.reshape(-1)).item()
    return total / n_batches


def make_optimizer(model, cfg):
    decay = [p for p in model.parameters() if p.dim() >= 2]               # matrices and embeddings
    no_decay = [p for p in model.parameters() if p.dim() < 2]             # biases and layer-norm parameters
    return torch.optim.AdamW([{"params": decay, "weight_decay": cfg.weight_decay}, {"params": no_decay, "weight_decay": 0.0}], lr=cfg.lr)


def train(model, train_data, val_data, cfg, log_every=0):
    seed_everything(cfg.seed)
    gen = torch.Generator().manual_seed(cfg.seed)
    opt = make_optimizer(model, cfg)
    lr_at = lambda s: min(1.0, (s + 1) / cfg.warmup) * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * s / cfg.steps)))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_at)
    V, hist = model.tok.num_embeddings, []
    for step in range(cfg.steps):
        model.train()
        x, y = get_batch(train_data, cfg.batch_size, cfg.block_size, gen)
        loss = F.cross_entropy(model(x).reshape(-1, V), y.reshape(-1))
        opt.zero_grad(); loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), cfg.clip)
        opt.step(); sched.step()
        hist.append(loss.item())
        if log_every and (step + 1) % log_every == 0:
            print(f"  step {step + 1:>5}  train {np.mean(hist[-log_every:]):.3f}  val {eval_loss(model, val_data, cfg.block_size):.3f}")
    return hist


# ---------- generation ----------
def next_token_probs(logits, temperature=1.0, top_k=None, top_p=None):
    if temperature <= 0:
        raise ValueError("temperature must be > 0 (use greedy=True for argmax decoding)")
    logits = logits / temperature
    if top_k is not None:
        kth = logits.topk(min(top_k, logits.shape[-1])).values[:, -1, None]
        logits = logits.masked_fill(logits < kth, float("-inf"))
    if top_p is not None:
        sl, si = logits.sort(descending=True)
        p = F.softmax(sl, -1)
        drop = (p.cumsum(-1) - p) > top_p
        logits = torch.full_like(logits, float("-inf")).scatter(-1, si, sl.masked_fill(drop, float("-inf")))
    return F.softmax(logits, -1)


@torch.no_grad()
def generate(model, prompt_ids, n_new, greedy=False, temperature=1.0, top_k=None, top_p=None, seed=0, use_cache=True):
    """Returns prompt + n_new ids. With use_cache the total length must fit in block_size; without it the window slides."""
    if not prompt_ids:
        raise ValueError("the prompt must contain at least one token")
    model.eval()
    g = torch.Generator().manual_seed(seed)
    ids = list(prompt_ids)
    caches = model.new_caches() if use_cache else None
    if use_cache and len(ids) + n_new > model.block_size:
        raise ValueError(f"prompt + new tokens ({len(ids) + n_new}) exceed block_size {model.block_size}; use use_cache=False")
    logits = model(torch.tensor([ids if use_cache else ids[-model.block_size:]]), caches)[:, -1]
    for _ in range(n_new):
        if greedy:
            nxt = logits.argmax(-1, keepdim=True)
        else:
            nxt = torch.multinomial(next_token_probs(logits, temperature, top_k, top_p), 1, generator=g)
        ids.append(int(nxt))
        if use_cache:
            logits = model(nxt, caches)[:, -1]
        else:
            logits = model(torch.tensor([ids[-model.block_size:]]))[:, -1]
    return ids


# ---------- the artefact ----------
def save_artifact(path, model, vocab, cfg):
    torch.save({"state_dict": model.state_dict(), "chars": vocab.itos, "config": dataclasses.asdict(cfg)}, path)


class Writer:
    """Loads an artefact and writes text. Validates the prompt."""
    def __init__(self, path):
        a = torch.load(path, weights_only=True)
        self.cfg = Config(**a["config"])
        self.vocab = CharVocab(a["chars"])
        self.model = GPT(len(self.vocab), self.cfg)
        self.model.load_state_dict(a["state_dict"])
        self.model.eval()

    def write(self, prompt, n_chars=100, **kw):
        ids = generate(self.model, self.vocab.encode(prompt), n_chars, **kw)
        return self.vocab.decode(ids)
''', encoding="utf-8")
print("wrote", (proj / "charlm.py").name, "|", len((proj / "charlm.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
wrote charlm.py | 225 lines
```

### 9.3 Train it

The project model is a little bigger than the one in section 8 (3 layers, width 80) and trains for 2,000 steps with batches of 32. It is deliberately small enough for a laptop CPU.

```python run
sys.path.insert(0, str(proj))
import importlib, charlm
importlib.reload(charlm)

vocab = charlm.CharVocab.fit(text)
ids_all = torch.tensor(vocab.encode(text))
n_val = len(ids_all) // 10
tr_ids, va_ids = ids_all[:-n_val], ids_all[-n_val:]
cfg = charlm.Config(steps=2000)
charlm.seed_everything(cfg.seed)
model = charlm.GPT(len(vocab), cfg)
print("vocabulary", len(vocab), "| parameters", n_params(model), "| initial validation loss", round(charlm.eval_loss(model, va_ids, cfg.block_size), 3), "vs ln V =", round(math.log(len(vocab)), 3))
t0 = time.time()
hist = charlm.train(model, tr_ids, va_ids, cfg, log_every=500)
final = charlm.eval_loss(model, va_ids, cfg.block_size)
print(f"trained {cfg.steps} steps in {time.time() - t0:.0f}s | validation loss {final:.3f}, perplexity {math.exp(final):.2f}")
print(f"count-based 4-gram baseline: loss {BASELINE:.3f} (perplexity {math.exp(BASELINE):.2f})")
```
```text
vocabulary 96 | parameters 246480 | initial validation loss 4.43 vs ln V = 4.564
  step   500  train 2.199  val 1.660
  step  1000  train 1.482  val 1.402
  step  1500  train 1.257  val 1.295
  step  2000  train 1.137  val 1.252
trained 2000 steps in 264s | validation loss 1.252, perplexity 3.50
count-based 4-gram baseline: loss 1.483 (perplexity 4.41)
```

The 3-layer, width-80 model (246k parameters, 2,000 steps) reaches validation loss 1.252 (perplexity 3.50), better than the section 8 model (1.287), the best recurrent model (1.377) and the 4-gram baseline (1.483). The gain per extra parameter is modest: the curve is still falling slowly at step 2,000, which is the signature of an under-trained small model, not of a saturated one.

### 9.4 Write something

```python run
for name, kw in [("temperature 0.7", dict(temperature=0.7)), ("temperature 1.0, top-p 0.9", dict(temperature=1.0, top_p=0.9))]:
    print(f"--- {name}, prompt 'The ', 60 new characters, with the KV cache")
    print(vocab.decode(charlm.generate(model, vocab.encode("The "), 59, seed=2, **kw)))
long = vocab.decode(charlm.generate(model, vocab.encode("An expression "), 400, seed=4, temperature=0.8, use_cache=False))
print("--- 400 characters, sliding window (no cache), temperature 0.8")
print(long)
st = text_stats(long)
print(f"\nvalid word rate {st[0]:.3f}, distinct 8-grams {st[1]:.3f} | for comparison real validation text: {np.mean(vstats, 0).round(3).tolist()}")
```
```text
--- temperature 0.7, prompt 'The ', 60 new characters, with the KV cache
The statement is protocol be that positional and expressions.


--- temperature 1.0, top-p 0.9, prompt 'The ', 60 new characters, with the KV cache
The statement is protocol be that expression of an instance if 
--- 400 characters, sliding window (no cache), temperature 0.8
An expression raw with ran "True" will base separator.  For a class are assolume filled in
operators.

If decimal characters than the target for appropriate to expression of this
  representation strings for the "frameterishb" exception is a block
Python matchine is an expression is evaluated arguments to the name is not
"^=" attribute the module.

See also:

  * C:
***Python implementation function modules may

valid word rate 0.935, distinct 8-grams 0.968 | for comparison real validation text: [0.948, 0.574]
```

Read the text as an engineer: it has the *shape* of the language reference (indentation, punctuation, technical words, sentence rhythm) but the content is not true or meaningful. Fluent-looking text from a language model is **not evidence of understanding or of correctness**, and that fact scales: the large models are the same machine with far more data and parameters.

### 9.5 Package it and use it

```python run
art = proj / "writer.pt"
charlm.save_artifact(art, model, vocab, cfg)
writer = charlm.Writer(art)
print(f"artefact: {art.name}, {art.stat().st_size / 1024:.0f} KB")
a = writer.write("The ", 40, temperature=0.8, seed=11)
orig = vocab.decode(charlm.generate(model, vocab.encode("The "), 40, temperature=0.8, seed=11))
print("loaded writer reproduces the in-memory model's output exactly:", a == orig)
print(repr(a))
for bad, why in [("café", "character outside the vocabulary"), ("", "empty prompt")]:
    try: writer.write(bad, 10)
    except ValueError as e: print(f"rejected ({why}):", e)
try: writer.write("x" * 60, 10)
except ValueError as e: print("rejected (too long for the cache):", e)
```
```text
artefact: writer.pt, 975 KB
loaded writer reproduces the in-memory model's output exactly: True
'The values nested enfined the sequences is a'
rejected (character outside the vocabulary): characters not in the vocabulary: ['é']
rejected (empty prompt): the prompt must contain at least one token
rejected (too long for the cache): prompt + new tokens (70) exceed block_size 64; use use_cache=False
```

### 9.6 Tests for the properties that matter

```python run
(proj / "test_charlm.py").write_text('''import math
import pytest
import torch
import torch.nn.functional as F
import charlm

TEXT = ("the quick brown fox jumps over the lazy dog. " * 40) + "pack my box with five dozen liquor jugs. " * 20


@pytest.fixture(scope="module")
def setup():
    vocab = charlm.CharVocab.fit(TEXT)
    ids = torch.tensor(vocab.encode(TEXT))
    cfg = charlm.Config(block_size=32, n_layers=2, n_heads=2, width=32, steps=60, batch_size=8, seed=1)
    return vocab, ids, cfg


def make(setup):
    vocab, ids, cfg = setup
    charlm.seed_everything(cfg.seed)
    return charlm.GPT(len(vocab), cfg)


def test_vocab_roundtrip_and_strictness(setup):
    vocab = setup[0]
    assert vocab.decode(vocab.encode("the dog")) == "the dog"
    with pytest.raises(ValueError, match="not in the vocabulary"):
        vocab.encode("the d\\u00f6g")


def test_output_shape_and_initial_loss(setup):
    vocab, ids, cfg = setup
    m = make(setup)
    x, y = charlm.get_batch(ids, 4, 16, torch.Generator().manual_seed(0))
    logits = m(x)
    assert logits.shape == (4, 16, len(vocab)), "logits must be (B, T, V): one score per vocabulary entry at every position"
    loss = F.cross_entropy(logits.reshape(-1, len(vocab)), y.reshape(-1)).item()
    assert abs(loss - math.log(len(vocab))) < 0.15, f"initial loss {loss:.3f} should be about ln V = {math.log(len(vocab)):.3f}: check initialisation and the loss"


def test_causality_no_leak_from_future(setup):
    vocab, ids, cfg = setup
    m = make(setup).eval()
    x = ids[:20][None].clone()
    base = m(x)
    x2 = x.clone(); x2[0, 12:] = (x2[0, 12:] + 1) % len(vocab)               # change only the tokens from position 12
    changed = m(x2)
    assert torch.allclose(base[0, :12], changed[0, :12], atol=1e-6), "outputs before position 12 changed: the model reads the future (check the causal mask)"
    assert not torch.allclose(base[0, 12:], changed[0, 12:]), "outputs after the change should differ"


def test_can_overfit_one_batch(setup):
    vocab, ids, cfg = setup
    m = make(setup)
    opt = torch.optim.Adam(m.parameters(), lr=1e-2)
    x, y = charlm.get_batch(ids, 4, 16, torch.Generator().manual_seed(3))
    for _ in range(120):
        loss = F.cross_entropy(m(x).reshape(-1, len(vocab)), y.reshape(-1))
        opt.zero_grad(); loss.backward(); opt.step()
    assert loss.item() < 0.1, f"loss {loss.item():.3f} after 120 steps: a correct model memorises one batch (check labels shift, zero_grad, mask)"


def test_training_is_deterministic(setup):
    vocab, ids, cfg = setup
    a, b = make(setup), make(setup)
    charlm.train(a, ids, ids, cfg); charlm.train(b, ids, ids, cfg)
    for (n, pa), (_, pb) in zip(a.state_dict().items(), b.state_dict().items()):
        assert torch.equal(pa, pb), f"{n} differs between two identical runs: seed every source of randomness"


def test_kv_cache_matches_full_forward(setup):
    vocab, ids, cfg = setup
    m = make(setup).eval()
    x = ids[:24][None]
    with torch.no_grad():
        full = m(x)
        caches = m.new_caches()
        parts = [m(x[:, :8], caches)] + [m(x[:, t:t + 1], caches) for t in range(8, 24)]
    assert torch.allclose(full, torch.cat(parts, 1), atol=1e-5), "cached logits differ from full recomputation: position offsets or mask in the cache path are wrong"


def test_generation_rules(setup):
    vocab, ids, cfg = setup
    m = make(setup)
    p = vocab.encode("the ")
    assert charlm.generate(m, p, 10, seed=5) == charlm.generate(m, p, 10, seed=5), "same seed must give the same text"
    assert charlm.generate(m, p, 10, seed=5) == charlm.generate(m, p, 10, seed=5, use_cache=False), "cached and uncached generation must agree"
    assert charlm.generate(m, p, 10, top_k=1, seed=1) == charlm.generate(m, p, 10, greedy=True), "top_k=1 is greedy decoding"
    out = charlm.generate(m, p, 10)
    assert len(out) == len(p) + 10 and all(0 <= i < len(vocab) for i in out)
    with pytest.raises(ValueError):
        charlm.generate(m, p, 100)                                              # longer than block_size with the cache
    with pytest.raises(ValueError):
        charlm.generate(m, p, 5, temperature=0.0)
    with pytest.raises(ValueError):
        charlm.generate(m, [], 5)


def test_top_p_keeps_the_nucleus():
    probs = charlm.next_token_probs(torch.tensor([[3.0, 2.0, 1.0, 0.0]]), top_p=0.5)[0]
    assert probs[0] == 1.0 and probs[1:].sum() == 0, "a very small p must keep only the most likely token (the first token is always kept)"


def test_artifact_roundtrip(setup, tmp_path):
    vocab, ids, cfg = setup
    m = make(setup)
    charlm.save_artifact(tmp_path / "w.pt", m, vocab, cfg)
    w = charlm.Writer(tmp_path / "w.pt")
    x = torch.tensor([vocab.encode("the quick")])
    with torch.no_grad():
        assert torch.allclose(m.eval()(x), w.model(x), atol=1e-6), "loaded model must give the same logits as the saved one"
    assert w.write("the ", 8, seed=2) == vocab.decode(charlm.generate(m, vocab.encode("the "), 8, seed=2))
''', encoding="utf-8")
import subprocess
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_charlm.py"], cwd=proj, capture_output=True, text=True, encoding="utf-8")
print((r.stdout + r.stderr).strip()[-1200:])
```
```text
.........                                                                [100%]
9 passed in 11.42s
```

Each test exists because of a real failure mode: a mask that lets the model read the future (the most common transformer bug, and invisible in the loss because the loss gets *better*), a position offset wrong in the cache path, a missing seed, a top-k that is not greedy at `k=1`, a saved model that differs from the trained one.

### 9.7 Extensions

1. **Dropout and weight decay**: add `p_drop=0.1` and compare validation loss at 4,000 steps. Does the train-validation gap shrink?
2. **A BPE tokeniser**: replace the character vocabulary with the BPE of section 1.4 (400 merges). Loss per *token* is not comparable to loss per *character*; convert both to **bits per character** to compare.
3. **Learned vs sinusoidal positions** (section 6.7): swap them and compare.
4. **Relative scale**: double the width and halve the steps, then double the layers. Which change buys more validation loss for the same compute?
5. **Another corpus**: train on your own text. Write `train.py` as a command-line script with `argparse`, and save a checkpoint every 500 steps so a crash does not lose the run (ml.02, section 7).

## 10. Common traps

1. **A causal mask that leaks.** The training loss falls suspiciously fast and generation is nonsense. Always test that changing a future token leaves earlier outputs unchanged (6.5, 7.4).
2. **Masking after the softmax** instead of before: the rows no longer sum to 1, and the masked positions already took probability mass.
3. **A row of all `-inf`** (every key masked) gives NaN in the softmax, and NaN spreads everywhere (6.5).
4. **Forgetting `√d`**: attention saturates at large widths (6.4).
5. **`view` after `transpose`**: needs `.contiguous()`; and mixing up `(B, T, h, d)` with `(B, h, T, d)` runs without error and gives wrong results. Compare against `nn.MultiheadAttention` (6.8).
6. **Padding treated as real tokens**: in a mean, in an RNN's last state, in attention keys, in the loss (2.2, 5.4, 6.5).
7. **A bidirectional model for next-token prediction**: the answer is in its input (5.5).
8. **A random train/validation split** on text: neighbouring sentences leak. Split by position (3.1).
9. **Comparing losses across tokenisations**: loss per token is not loss per character. Convert to bits per character (9.7).
10. **Judging a language model by a few fluent samples.** Measure on held-out text, and measure generated text against real text (8.2, 8.4).
11. **Sampling bugs**: temperature applied after top-k, or `top_p` implemented so that it can remove every token (keep the first one, 8.2).
12. **The KV cache not matching the full forward**: wrong position offset or wrong mask for the new tokens. Test it (8.3).
13. **Unequal comparisons**: a bigger model, a longer budget, or an untuned learning rate compared with a baseline. State the budget (5.3, 8.1).

## 11. Summary

- Text becomes integers by **tokenisation**: characters (tiny vocabulary, long sequences), words (short sequences, OOV problem), or **subwords/BPE** (repeatedly merge the most frequent pair; nothing is ever unknown). Real tokenisers work on bytes.
- An **embedding** is a `(V, D)` lookup table (= one-hot times a matrix). Padding rows and masks must be handled explicitly. Similar contexts give similar vectors.
- A **language model** predicts the next token; the targets are the inputs shifted by one. Loss is cross-entropy, **perplexity** is `exp(loss)`; a model that knows nothing has loss `ln V`. Always compare with a **count-based n-gram baseline**, and split validation text by position.
- An **RNN** carries a hidden state through time with shared weights; backpropagation through time multiplies by `W_hh` at every step, so gradients vanish or explode (measured). **Clip** gradients. **LSTM/GRU** gates give an additive memory path, but at default initialisation they are not better; the forget-bias trick and training make the memory usable. Pack or index around padding.
- **Attention** computes `softmax(QKᵀ/√d)·V`: shapes `(B,T,d) → scores (B,T,T) → output (B,T,d)`. `√d` keeps the softmax from saturating. **Masks** go in before the softmax; the causal mask is tested by changing future tokens. Self-attention is permutation-equivariant, so **positional encodings** are added. **Multi-head** attention splits the width into `h` heads of `C/h`: `(B,T,C) → (B,h,T,d) → (B,h,T,T) → (B,T,C)`. The score matrix costs `T²`.
- A **transformer block** is `x + Attn(LN(x))` then `x + MLP(LN(x))`; a GPT adds token and position embeddings, a final norm and a (tied) output layer. Roughly `12C²` parameters per layer. Tests: initial loss ≈ `ln V`, causality, overfit one batch.
- **Generation** is autoregressive: greedy, temperature, top-k, top-p. The **KV cache** reuses past keys and values and must reproduce the full forward exactly. Measure generated text (valid-word rate, diversity, copying), do not just read it.
- A finished project has a strict tokeniser, a tested model, a seeded training run, comparison with a baseline on the same footing, an artefact carrying its own vocabulary and configuration, and tests for each property above.

**Self-check (answer without looking back):**

1. `x` has shape `(8, 128, 256)` and the model has 4 heads. Give the shapes of `q`, the scores, the attention output before and after the output projection.
2. Why divide by `√d` and not by `d`?
3. Why can a plain RNN not learn that the label depends on the first token of a 100-token sequence, and what are two things that help?
4. A colleague's language model reaches loss 0.02 after 100 steps on real text. What do you suspect first, and how do you test it?
5. What does the KV cache save, what does it cost, and how do you test that it is correct?
6. Name the difference between BPE with 400 merges and 40,000 merges for a model's embedding table and sequence length.

<details><summary>Answer</summary>

1. `q`: `(8, 4, 128, 64)` (heads move before the time axis); scores `(8, 4, 128, 128)`; output before the projection `(8, 128, 256)` after concatenating the heads, and the same shape after the projection.
2. The dot product of two unit-variance `d`-vectors has standard deviation `√d`, so dividing by `√d` restores unit variance; dividing by `d` would make the scores too small and the softmax nearly uniform.
3. The gradient from the loss shrinks (or explodes) exponentially over the 100 steps it travels back, so there is no signal to learn the dependency. Helpful: gated cells (GRU/LSTM) with a forget bias, gradient clipping and a good learning rate, a shorter path (truncate or shorten the sequence), or attention.
4. A leak: the model can see the target. Test by changing a future token and checking that earlier outputs do not change; also check that the targets are shifted by one and that the validation set is separate.
5. It saves recomputing keys and values of past positions (cost per new token from `O(T)` positions to one). It costs memory growing with context × layers × heads. Test: logits from incremental decoding equal the full forward.
6. More merges: a bigger vocabulary (larger embedding and output layer) but shorter sequences (less attention cost, more text per context window). Fewer merges: the opposite.

</details>
