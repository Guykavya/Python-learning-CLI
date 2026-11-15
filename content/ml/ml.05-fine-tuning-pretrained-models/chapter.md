# Chapter 5 (ML): Fine-Tuning Pretrained Models

In ml.04 you built a language model from scratch and saw how much data and compute it takes to get even a small one to write plausible text. In practice almost nobody trains such a model from zero. They start from a **pretrained model**: a network that already read a huge amount of text (or images, or audio), and **adapt** it to their own task with a few thousand labelled examples. This is called **fine-tuning**, and it is the everyday workflow of applied machine learning today. This chapter teaches it properly: not "call `Trainer` and hope", but what is being loaded, what is being changed, what it costs, and above all **how to show that it worked**.

You will learn the **Hugging Face stack** (`transformers`, `datasets`, tokenisers, the Hub), how to **check your data and set honest baselines** before touching a neural network, **full fine-tuning** with a plain PyTorch loop and with `Trainer`, the failure modes (learning rate, seeds, data order), **parameter-efficient fine-tuning** with **LoRA** (written from scratch, then compared with the `peft` library), and **evaluation**: confidence intervals, paired tests, calibration, error analysis and behavioural tests. The syllabus outcome is: **fine-tune a small model and show it beats the base model on a held-out set.** The chapter ends with a project that does exactly that, packaged and tested.

Prerequisites: ml.02 (PyTorch training loop), ml.04 (tokenisation, transformers, attention), ds.04 (honest evaluation).

> **How this chapter is built.** The examples that carry the main lessons are real runs, with the output pasted exactly as the computer printed it. Experiments that would only repeat a lesson (long sweeps, many seeds) are written as **question → worked answer** boxes instead, with no invented numbers; where a number is quoted there, it was measured in a test run on this machine and is labelled so. Some sections end with a **Visualise it** prompt: an optional text you can paste into any AI chat to get a picture or small animation of the idea. The course never depends on it.
>
> **Network rule for this chapter.** Unlike the earlier ML chapters, this one needs the internet **once**: the first run downloads the dataset and the pretrained weights from the Hugging Face Hub (about 310 MB in total) into `~/.cache/huggingface`. After that everything runs offline; set the environment variable `HF_HUB_OFFLINE=1` to be sure (and to see a clear error instead of a hang if something is missing). The project tests of section 9 use a tiny randomly initialised model and need no download at all. Models and data are small by design: a CPU with 6 threads fine-tunes the 11-million-parameter model in about a minute and the 67-million-parameter one in a few minutes. Every output block was produced by running the code above it, in one session from top to bottom, with `transformers` 5.x, `datasets` 5.x and `peft` 0.21. Library APIs in this area change quickly; where a name differs in your version, the error message and the library's own documentation are the reference. Accuracies are of course specific to these seeds and this machine.

```python run
import sys, math, time, os, re, copy, json, collections, pathlib, tempfile, subprocess, warnings, random
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
warnings.filterwarnings("ignore")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
import transformers, datasets, peft, sklearn
transformers.logging.set_verbosity_error()
datasets.disable_progress_bars()
from transformers import AutoTokenizer, AutoConfig, AutoModel, AutoModelForSequenceClassification, get_linear_schedule_with_warmup

np.set_printoptions(precision=4, suppress=True, linewidth=120)
pd.set_option("display.width", 130)
print("python       ", sys.version.split()[0])
print("torch        ", torch.__version__, "| threads", torch.get_num_threads())
print("transformers ", transformers.__version__, "| datasets", datasets.__version__, "| peft", peft.__version__, "| scikit-learn", sklearn.__version__)
```
```text
python        3.14.4
torch         2.15.0+cpu | threads 6
transformers  5.22.2 | datasets 5.2.0 | peft 0.21.2 | scikit-learn 1.9.1
```

## Table of contents

1. [The Hugging Face stack](#1-the-hugging-face-stack)
2. [Know the data, set honest baselines](#2-know-the-data-set-honest-baselines)
3. [What a "base model" gives you: frozen features](#3-what-a-base-model-gives-you-frozen-features)
4. [Full fine-tuning](#4-full-fine-tuning)
5. [When fine-tuning goes wrong](#5-when-fine-tuning-goes-wrong)
6. [LoRA and parameter-efficient fine-tuning](#6-lora-and-parameter-efficient-fine-tuning)
7. [Evaluating a fine-tuned model](#7-evaluating-a-fine-tuned-model)
8. [Beyond classification, and what to do at scale](#8-beyond-classification-and-what-to-do-at-scale)
9. [Project: a fine-tuned sentiment classifier](#9-project-a-fine-tuned-sentiment-classifier)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. The Hugging Face stack

### 1.1 What is on the Hub, and what `from_pretrained` loads

The **Hugging Face Hub** is a website that hosts model weights, tokenisers and datasets as git repositories. A model is identified by `"owner/name"`. `from_pretrained(name)` downloads (once) and loads the pieces of a model repository:

| File | Holds | Loaded by |
|---|---|---|
| `config.json` | the architecture: layer count, width, heads, vocabulary size | `AutoConfig` |
| `model.safetensors` | the weights (a safe, fast format; no code can hide inside it, unlike Python `pickle`) | `AutoModel…` |
| `vocab.txt` / `tokenizer.json` | the tokeniser | `AutoTokenizer` |

The `Auto…` classes look at `config.json` and build the right architecture. We use two pretrained models, both BERT-style encoders trained on English text with masked-word prediction:

- **BERT-mini** (`google/bert_uncased_L-4_H-256_A-4`): 4 layers, width 256, 11 million parameters. Fast enough for experiments.
- **DistilBERT** (`distilbert/distilbert-base-uncased`): 6 layers, width 768, 67 million parameters. A realistic small model.

```python run
MINI = "google/bert_uncased_L-4_H-256_A-4"
DISTIL = "distilbert/distilbert-base-uncased"
cfg = AutoConfig.from_pretrained(MINI)
print({k: getattr(cfg, k) for k in ("model_type", "num_hidden_layers", "hidden_size", "num_attention_heads", "intermediate_size", "vocab_size", "max_position_embeddings")})

body = AutoModel.from_pretrained(MINI)                                         # the pretrained network WITHOUT a task head
clf = AutoModelForSequenceClassification.from_pretrained(MINI, num_labels=2)   # body + a NEW, randomly initialised classification head
def n_params(m, trainable_only=False): return sum(p.numel() for p in m.parameters() if p.requires_grad or not trainable_only)
parts = {"embeddings": body.embeddings, "encoder (4 transformer blocks)": body.encoder, "pooler": body.pooler}
for name, m in parts.items(): print(f"{name:<32}{n_params(m):>12,}  ({100 * n_params(m) / n_params(body):.1f}% of the body)")
print(f"{'classification head (new)':<32}{n_params(clf.classifier) :>12,}  <- the only part that is NOT pretrained")
print("body parameters", f"{n_params(body):,}", "| whole classifier", f"{n_params(clf):,}")
print("\na few parameter names (these names are what LoRA's `target_modules` matches):")
for n, p in list(clf.named_parameters())[8:8 + 8]: print(f"  {n:<58} {tuple(p.shape)}")
```
```text
{'model_type': 'bert', 'num_hidden_layers': 4, 'hidden_size': 256, 'num_attention_heads': 4, 'intermediate_size': 1024, 'vocab_size': 30522, 'max_position_embeddings': 512}
embeddings                         7,945,728  (71.1% of the body)
encoder (4 transformer blocks)     3,159,040  (28.3% of the body)
pooler                                65,792  (0.6% of the body)
classification head (new)                514  <- the only part that is NOT pretrained
body parameters 11,170,560 | whole classifier 11,171,074

a few parameter names (these names are what LoRA's `target_modules` matches):
  bert.encoder.layer.0.attention.self.key.bias               (256,)
  bert.encoder.layer.0.attention.self.value.weight           (256, 256)
  bert.encoder.layer.0.attention.self.value.bias             (256,)
  bert.encoder.layer.0.attention.output.dense.weight         (256, 256)
  bert.encoder.layer.0.attention.output.dense.bias           (256,)
  bert.encoder.layer.0.attention.output.LayerNorm.weight     (256,)
  bert.encoder.layer.0.attention.output.LayerNorm.bias       (256,)
  bert.encoder.layer.0.intermediate.dense.weight             (1024, 256)
```

Two things to notice. Most of the parameters of this model sit in the **embeddings** (30,522 word pieces × 256), not in the transformer blocks. And the classification head is tiny and *new*: the line "newly initialized" that `transformers` prints when you load a classifier (hidden here by `set_verbosity_error`) means exactly this. Until you train it, the head's output is noise.

### 1.2 The tokeniser

BERT uses **WordPiece**, a cousin of the BPE you wrote in ml.04: a fixed vocabulary of word pieces, rare words split into pieces, with `##` marking "continues the previous word". The tokeniser also adds the special tokens the model was trained with: `[CLS]` at the start (its final vector is used for classification), `[SEP]` at the end, `[PAD]` for padding. **You must use the tokeniser that matches the model**; the two models here share a vocabulary, but that is a coincidence of history, not a rule.

```python run
tok = AutoTokenizer.from_pretrained(DISTIL)
print("same vocabulary as BERT-mini:", tok.vocab_size, "==", cfg.vocab_size, "|", type(tok).__name__)
s = "The cinematography was breathtaking, but the screenplay is unwatchable!"
enc = tok(s)
print("tokens :", tok.convert_ids_to_tokens(enc["input_ids"]))
print("ids    :", enc["input_ids"])
print("special:", tok.cls_token, tok.sep_token, tok.pad_token, tok.unk_token, "| lower-cased, accents stripped (uncased model)")
print("decode :", tok.decode(enc["input_ids"]))
print("a rare word is split into known pieces:", tok.tokenize("unwatchable"), tok.tokenize("kubernetes"))

batch = tok(["good", "a considerably longer sentence than the first one", "ok fine"], padding=True, truncation=True, max_length=8, return_tensors="pt")
print("\nbatch keys:", list(batch.keys()))
print("input_ids\n", batch["input_ids"])
print("attention_mask (1 = real token, 0 = padding)\n", batch["attention_mask"])
```
```text
same vocabulary as BERT-mini: 30522 == 30522 | BertTokenizer
tokens : ['[CLS]', 'the', 'cinematography', 'was', 'breath', '##taking', ',', 'but', 'the', 'screenplay', 'is', 'un', '##watch', '##able', '!', '[SEP]']
ids    : [101, 1996, 16434, 2001, 3052, 17904, 1010, 2021, 1996, 9000, 2003, 4895, 18866, 3085, 999, 102]
special: [CLS] [SEP] [PAD] [UNK] | lower-cased, accents stripped (uncased model)
decode : [CLS] the cinematography was breathtaking, but the screenplay is unwatchable! [SEP]
a rare word is split into known pieces: ['un', '##watch', '##able'] ['ku', '##ber', '##net', '##es']

batch keys: ['input_ids', 'token_type_ids', 'attention_mask']
input_ids
 tensor([[ 101, 2204,  102,    0,    0,    0,    0,    0],
        [ 101, 1037, 9839, 2936, 6251, 2084, 1996,  102],
        [ 101, 7929, 2986,  102,    0,    0,    0,    0]])
attention_mask (1 = real token, 0 = padding)
 tensor([[1, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 0, 0, 0]])
```

The **attention mask** tells the model which positions are real. Forget it and the padding is treated as content (ml.04, section 6.5). Test it:

```python run
clf.eval()
one = tok(["good"], return_tensors="pt")
padded = tok(["good"], padding="max_length", max_length=16, return_tensors="pt")
with torch.no_grad():
    a = clf(**one).logits
    b = clf(**padded).logits                                                           # padded AND masked: same answer
    c = clf(input_ids=padded["input_ids"]).logits                                      # padded, mask forgotten
print("logits, no padding          :", a[0].numpy().round(4))
print("logits, padded + mask       :", b[0].numpy().round(4), "-> equal:", bool(torch.allclose(a, b, atol=1e-5)))
print("logits, padded, MASK FORGOTTEN:", c[0].numpy().round(4), "-> changed by padding alone")
```
```text
logits, no padding          : [0.332  0.2489]
logits, padded + mask       : [0.332  0.2489] -> equal: True
logits, padded, MASK FORGOTTEN: [0.1638 0.1509] -> changed by padding alone
```

> **Predict the output.** Is the model's answer for a one-word input the same when you pad it to 16 tokens and pass the attention mask? And when you pad it and *forget* the mask?

<details><summary>Answer</summary>

With the mask the answer is the same (up to floating-point noise, about 1e-6): masked positions get attention weight exactly zero, so they cannot influence the real tokens. Without the mask, the 15 `[PAD]` tokens are read like words, and the logits change visibly. This is a silent bug: nothing crashes, the numbers are just worse. When you pad, always pass the whole tokeniser output (`**batch`), not just `input_ids`.

</details>


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a diagram of a sentence going through a BERT tokeniser: words, then word pieces with ## marks, then [CLS] and [SEP], then ids, then an attention-mask row where padding is 0. Then show a second diagram of what the attention matrix looks like with and without the mask on padded positions."

### 1.3 The `datasets` library

`datasets` loads data from the Hub or from local files (CSV, JSON, Parquet) into **Apache Arrow** tables stored on disk and memory-mapped, so a dataset bigger than your RAM still works. It gives you `map` (transform in batches, cached), `filter`, `select`, `shuffle`, and `train_test_split`. Our task: **Rotten Tomatoes**, 10,662 one-sentence movie reviews labelled positive (1) or negative (0), already split into train, validation and test.

```python run
from datasets import load_dataset
ds = load_dataset("cornell-movie-review-data/rotten_tomatoes")
print(ds)
print("features:", ds["train"].features)
print("one example:", ds["train"][1])
txt = {k: list(ds[k]["text"]) for k in ds}                                         # plain Python lists are easiest to work with
lab = {k: np.array(ds[k]["label"]) for k in ds}
print("\nthe FIRST 100 training rows have these labels:", np.bincount(lab["train"][:100], minlength=2).tolist(), "<- the file is SORTED by label")
print("the last 100:", np.bincount(lab["train"][-100:], minlength=2).tolist())
```
```text
DatasetDict({
    train: Dataset({
        features: ['text', 'label'],
        num_rows: 8530
    })
    validation: Dataset({
        features: ['text', 'label'],
        num_rows: 1066
    })
    test: Dataset({
        features: ['text', 'label'],
        num_rows: 1066
    })
})
features: {'text': Value('string'), 'label': ClassLabel(names=['neg', 'pos'])}
one example: {'text': 'the gorgeously elaborate continuation of " the lord of the rings " trilogy is so huge that a column of words cannot adequately describe co-writer/director peter jackson\'s expanded vision of j . r . r . tolkien\'s middle-earth .', 'label': 1}

the FIRST 100 training rows have these labels: [0, 100] <- the file is SORTED by label
the last 100: [100, 0]
```

That sorted order is a trap that has ruined many experiments: `ds["train"].select(range(1000))` is a training set with **one class only**. Always shuffle before taking a subset. `map` applies a function to every example (batched, so the tokeniser's fast Rust code runs on many texts at once):

```python run
def tokenize(batch): return tok(batch["text"], truncation=True, max_length=64)
tokd = ds.map(tokenize, batched=True)
print(tokd["train"].column_names, "| tokens in example 1:", len(tokd["train"][1]["input_ids"]))
sub = ds["train"].shuffle(seed=0).select(range(1000))
print("a shuffled 1000-example subset has labels", np.bincount(sub["label"]).tolist(), "| first example is now", repr(sub[0]["text"][:50]))
print("filter + len:", len(ds["train"].filter(lambda ex: len(ex["text"].split()) > 40)), "training reviews have more than 40 words")
```
```text
['text', 'label', 'input_ids', 'token_type_ids', 'attention_mask'] | tokens in example 1: 52
a shuffled 1000-example subset has labels [513, 487] | first example is now "this is pure , exciting moviemaking . you won't ex"
filter + len: 230 training reviews have more than 40 words
```

### 1.4 Try it

1. Tokenise `"Don't stop believin'"` and `"naïve café"`. What happens to the apostrophes and accents, and why does it matter that the *same* normalisation is used in training and in deployment?
2. Load `AutoModel` for DistilBERT and compare its parameter count to `AutoModelForSequenceClassification`. Which part differs?
3. What would `tok(["a", "b"], return_tensors="pt")` do, and why does it need `padding=True` for texts of different lengths?

## 2. Know the data, set honest baselines

Before any neural network: look at the data, check for leakage, and establish what a **cheap classical model** achieves. "The fine-tuned model reaches 82%" means nothing until you know what a logistic regression reaches, and what guessing reaches.

### 2.1 Look at the data

```python run
for k in ("train", "validation", "test"):
    print(f"{k:<11} {len(txt[k]):>6} reviews, positive share {lab[k].mean():.3f}")
words = np.array([len(t.split()) for t in txt["train"]])
ntok = np.array([len(x) for x in tokd["train"]["input_ids"]])
print(f"words per review: median {np.median(words):.0f}, 95th percentile {np.percentile(words, 95):.0f}, max {words.max()}")
print(f"tokens (truncated at 64): median {np.median(ntok):.0f}, share of reviews cut off at the 64-token limit: {np.mean(ntok == 64):.3%}")
print("\nrandom examples:")
rng = np.random.default_rng(1)
for i in rng.choice(len(txt["train"]), 4, replace=False): print(f"  [{lab['train'][i]}] {txt['train'][i][:110]}")

# leakage checks: exact duplicates inside train, and between splits
norm = lambda t: " ".join(t.lower().split())
tr_set = {norm(t) for t in txt["train"]}
print(f"\nexact duplicate reviews inside train: {len(txt['train']) - len(tr_set)}")
for k in ("validation", "test"):
    overlap = sum(norm(t) in tr_set for t in txt[k])
    print(f"{k} reviews that also appear in train: {overlap}")
print("validation reviews that also appear in test:", len({norm(t) for t in txt['validation']} & {norm(t) for t in txt['test']}))
```
```text
train         8530 reviews, positive share 0.500
validation    1066 reviews, positive share 0.500
test          1066 reviews, positive share 0.500
words per review: median 20, 95th percentile 37, max 59
tokens (truncated at 64): median 27, share of reviews cut off at the 64-token limit: 0.117%

random examples:
  [0] the story's so preposterous that i didn't believe it for a second , despite the best efforts of everyone invol
  [0] the gags , and the script , are a mixed bag .
  [0] co-writer/director jonathan parker's attempts to fashion a brazil-like , hyper-real satire fall dreadfully sho
  [1] nice piece of work .

exact duplicate reviews inside train: 0
validation reviews that also appear in train: 0
test reviews that also appear in train: 0
validation reviews that also appear in test: 0
```

Cheap checks like these are the first line of defence: a duplicate between training and test data makes the test score a measure of memorisation. Here the overlap is negligible; on web-scraped text it is often not.

### 2.2 Baselines

Three reference points: **guessing** (the majority class: 50%), the **random-head pretrained model** (section 3), and a **TF-IDF + logistic regression** model: counts of words and word pairs, weighted by rarity, fed to a linear classifier. It is fast, strong on sentiment, and trained on the *same* labelled examples as the neural model. We train it on shuffled subsets of increasing size to see how data-hungry it is.

```python run
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
perm = np.random.default_rng(0).permutation(len(txt["train"]))
def tfidf_acc(n, split="validation", C=10.0):
    ii = perm[:n]
    v = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    clf_ = LogisticRegression(C=C, max_iter=2000).fit(v.fit_transform([txt["train"][i] for i in ii]), lab["train"][ii])
    return clf_.score(v.transform(txt[split]), lab[split]), (v, clf_)
rows = []
for n in (100, 300, 1000, 3000, len(perm)):
    acc, _ = tfidf_acc(n); rows.append([n, round(acc, 4)])
print(pd.DataFrame(rows, columns=["training reviews", "TF-IDF + logistic regression: validation accuracy"]).to_string(index=False))
n_val = len(txt["validation"]); acc_full = rows[-1][1]
half = 1.96 * math.sqrt(acc_full * (1 - acc_full) / n_val)
print(f"\nwith {n_val} validation reviews, an accuracy of {acc_full:.3f} has a 95% interval of about ±{half:.3f}: differences below ~{2 * half:.2f} between two models are hard to see")
```
```text
 training reviews  TF-IDF + logistic regression: validation accuracy
              100                                             0.5938
              300                                             0.6229
             1000                                             0.6679
             3000                                             0.7233
             8530                                             0.7570

with 1066 validation reviews, an accuracy of 0.757 has a 95% interval of about ±0.026: differences below ~0.05 between two models are hard to see
```

> **Predict the output.** How much of its final accuracy does TF-IDF + logistic regression already reach with 1,000 reviews (12% of the data)? What does that suggest about how much a neural model has to beat?

<details><summary>Answer</summary>

The learning curve climbs from 0.59 with 100 reviews to 0.67 with 1,000 (12% of the data), 0.72 with 3,000 and 0.757 with all 8,530: this classical model is data-hungry and keeps improving with more data. So at 1,000 reviews it is about 9 points below its own best, and every neural result must be judged against these numbers **at the same training size**. The strongest argument for fine-tuning is the left side of this curve: a pretrained model already "knows English", so it should need far fewer labelled examples to reach a given accuracy.

</details>

### 2.3 Try it

1. Try `ngram_range=(1, 1)` and `(1, 3)` in `tfidf_acc`. How much does the choice change the full-data accuracy? Is the change bigger than the ±2.6 point interval?
2. Find five validation reviews your TF-IDF model gets wrong. Is the model wrong, or is the label arguable?
3. Why is it wrong to pick `C` by looking at the *test* split? Which split did we use?

## 3. What a "base model" gives you: frozen features

### 3.1 The base model is not a classifier yet

"Fine-tuning beats the base model" needs a precise meaning of *base model*. The pretrained **body** knows language but has never been asked to judge sentiment, and the classification **head** is randomly initialised. Evaluated as it stands, it is a coin flip. We build the data helpers used for the rest of the chapter first: dynamic padding (pad each batch only to its longest member) and an evaluation function.

```python run
MAXLEN = 64
ids_all = {k: tok(txt[k], truncation=True, max_length=MAXLEN)["input_ids"] for k in txt}          # lists of token ids, no padding yet

def make_batch(split, idx):
    """Pad a batch to ITS OWN longest member. Returns input_ids, attention_mask, labels."""
    seqs = [ids_all[split][i] for i in idx]
    L = max(map(len, seqs))
    x = torch.zeros(len(seqs), L, dtype=torch.long); m = torch.zeros(len(seqs), L, dtype=torch.long)
    for j, s in enumerate(seqs):
        x[j, :len(s)] = torch.tensor(s); m[j, :len(s)] = 1
    return x, m, torch.tensor(lab[split][list(idx)])

@torch.no_grad()
def predict_logits(model, split, bs=128):
    model.eval()
    n = len(lab[split])
    return torch.cat([model(input_ids=x, attention_mask=m).logits for x, m, _ in (make_batch(split, range(i, min(i + bs, n))) for i in range(0, n, bs))])

def accuracy(model, split="validation"):
    return (predict_logits(model, split).argmax(1).numpy() == lab[split]).mean()

def new_model(name=MINI, seed=0, num_labels=2):
    torch.manual_seed(seed)                                                        # the head's random initial weights depend on this seed
    return AutoModelForSequenceClassification.from_pretrained(name, num_labels=num_labels)

t0 = time.time()
base_clf = new_model()
print(f"pretrained body + random head, validation accuracy: {accuracy(base_clf):.4f}  (chance = 0.5000) | {time.time() - t0:.1f}s")
x, m, y = make_batch("validation", range(4))
print("a dynamic batch:", tuple(x.shape), "(longest of 4 reviews) | mask row sums =", m.sum(1).tolist())
```
```text
pretrained body + random head, validation accuracy: 0.5047  (chance = 0.5000) | 5.6s
a dynamic batch: (4, 30) (longest of 4 reviews) | mask row sums = [26, 12, 30, 25]
```

### 3.2 Frozen features and a linear classifier (a "linear probe")

The cheapest way to use a pretrained model: run it **once** over the texts, keep the output vectors as features, and train an ordinary classifier (logistic regression) on top. No gradients flow into the network, no GPU is needed, and the result tells you how much sentiment information the pretrained representation already contains. Two ways to turn the per-token outputs into one vector per review: take the `[CLS]` token's vector, or **average** all real tokens (a mask-aware mean, as in ml.04, section 2.2).

```python run
@torch.no_grad()
def extract(body_model, split, pooling="mean", bs=128):
    body_model.eval()
    n, feats = len(lab[split]), []
    for i in range(0, n, bs):
        x, m, _ = make_batch(split, range(i, min(i + bs, n)))
        h = body_model(input_ids=x, attention_mask=m).last_hidden_state               # (B, T, C)
        feats.append(h[:, 0] if pooling == "cls" else (h * m[..., None]).sum(1) / m.sum(1, keepdim=True))
    return torch.cat(feats).numpy()

t0 = time.time()
feats = {(pool, k): extract(body, k, pool) for pool in ("cls", "mean") for k in ("train", "validation")}
print(f"features extracted for {sum(len(v) for v in feats.values()):,} texts in {time.time() - t0:.0f}s | shape of one set: {feats[('mean', 'train')].shape}")
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
rows = []
for pool in ("cls", "mean"):
    for n in (1000, len(perm)):
        ii = perm[:n]
        probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000)).fit(feats[(pool, "train")][ii], lab["train"][ii])
        rows.append([f"frozen BERT-mini, {pool} pooling + logistic regression", n, round(probe.score(feats[(pool, "validation")], lab["validation"]), 4)])
rows += [["TF-IDF + logistic regression (section 2.2)", n, a] for n, a in [(1000, tfidf_acc(1000)[0]), (len(perm), tfidf_acc(len(perm))[0])]]
print(pd.DataFrame(rows, columns=["model", "training reviews", "validation accuracy"]).round(4).to_string(index=False))
```
```text
features extracted for 19,192 texts in 134s | shape of one set: (8530, 256)
                                               model  training reviews  validation accuracy
 frozen BERT-mini, cls pooling + logistic regression              1000               0.7092
 frozen BERT-mini, cls pooling + logistic regression              8530               0.7139
frozen BERT-mini, mean pooling + logistic regression              1000               0.7017
frozen BERT-mini, mean pooling + logistic regression              8530               0.7355
          TF-IDF + logistic regression (section 2.2)              1000               0.6679
          TF-IDF + logistic regression (section 2.2)              8530               0.7570
```

Mean pooling is a little better than the `[CLS]` vector here (0.736 against 0.714 with all the data), which is common for models not trained to put a summary in `[CLS]`.

BERT-mini was pretrained with *masked-word prediction* (guess a hidden word from its context), not sentiment, and it is tiny. Its frozen features are informative but **not specialised**: with 1,000 labelled reviews the linear classifier on top of them is a few points ahead of TF-IDF (0.70 against 0.67), but with all the data TF-IDF catches up and passes it (0.757 against 0.736). This is the typical picture for frozen features from a model that was not trained for the task, and it is exactly the gap that fine-tuning closes: let the network itself change so that the features separate positive from negative.

## 4. Full fine-tuning

### 4.1 The recipe

**Full fine-tuning** keeps the architecture, starts from the pretrained weights, adds a new head, and trains **all** parameters on the labelled data with a small learning rate. The defaults that work across most text-classification tasks, and the reason for each:

| Setting | Typical value | Why |
|---|---|---|
| learning rate | `2e-5` to `1e-4` (smaller for bigger models) | the weights are already good: a large step destroys them |
| epochs | 2 to 4 | the model overfits small data fast |
| warm-up | first 5% to 10% of steps, linear rise | the random head produces large, noisy gradients at first |
| schedule | linear decay to 0 | settles into a minimum at the end |
| weight decay | 0.01, **not** on biases and layer-norm parameters | regularise matrices only |
| batch size | 16 to 32 | |
| gradient clipping | max norm 1.0 | protects against rare large gradients |

### 4.2 One training function, written out

This is the PyTorch loop of ml.02 plus the recipe above. It returns a per-epoch history so we can read the curves, and it accepts a list of parameters so that later sections can train only a subset.

```python run
def make_optimizer(model, lr, wd=0.01, params=None):
    named = [(n, p) for n, p in model.named_parameters() if p.requires_grad] if params is None else params
    decay = [p for n, p in named if p.ndim >= 2]                                     # weight matrices
    no_decay = [p for n, p in named if p.ndim < 2]                                   # biases, LayerNorm
    return torch.optim.AdamW([{"params": decay, "weight_decay": wd}, {"params": no_decay, "weight_decay": 0.0}], lr=lr)

def fit_classifier(model, train_idx, epochs=3, lr=1e-4, bs=32, seed=0, warmup=0.1, clip=1.0, wd=0.01, params=None, track_train_acc=False, verbose=False):
    g = np.random.default_rng(seed)
    torch.manual_seed(seed)                                                          # dropout masks
    train_idx = np.asarray(train_idx)
    opt = make_optimizer(model, lr, wd, params)
    steps = epochs * math.ceil(len(train_idx) / bs)
    sched = get_linear_schedule_with_warmup(opt, int(warmup * steps), steps)
    hist, t0 = [], time.time()
    for ep in range(epochs):
        model.train()
        order = g.permutation(train_idx)
        tot, n_ok = 0.0, 0
        for i in range(0, len(order), bs):
            x, m, y = make_batch("train", order[i:i + bs])
            logits = model(input_ids=x, attention_mask=m).logits
            loss = F.cross_entropy(logits, y)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_([p for _, p in model.named_parameters() if p.requires_grad], clip)
            opt.step(); sched.step()
            tot += loss.item() * len(y); n_ok += (logits.argmax(1) == y).sum().item()
        row = {"epoch": ep + 1, "train_loss": tot / len(order), "train_acc_running": n_ok / len(order), "val_acc": accuracy(model), "seconds": time.time() - t0}
        hist.append(row)
        if verbose: print({k: round(v, 4) for k, v in row.items()})
    return pd.DataFrame(hist)

n1000 = perm[:1000]                                                                  # a shuffled 1,000-review subset (never the first 1,000 rows!)
m_ft = new_model()
h = fit_classifier(m_ft, n1000, epochs=3, lr=1e-4)
print(h.round(4).to_string(index=False))
print(f"\nfull fine-tuning, 1,000 reviews: validation accuracy {h.val_acc.iloc[-1]:.4f} | TF-IDF at 1,000 reviews: {tfidf_acc(1000)[0]:.4f} | random head: {accuracy(base_clf):.4f}")
```
```text
 epoch  train_loss  train_acc_running  val_acc  seconds
     1      0.6744              0.579   0.6276  36.5393
     2      0.6023              0.674   0.7036  70.4044
     3      0.5105              0.775   0.7092 103.6582

full fine-tuning, 1,000 reviews: validation accuracy 0.7092 | TF-IDF at 1,000 reviews: 0.6679 | random head: 0.5047
```

Look at the table as a diagnostic. `train_acc_running` is the accuracy on the batches seen *while the weights were changing* (so it lags), and `val_acc` is the quantity that matters. A gap that grows from epoch to epoch means over-fitting.

### 4.3 The learning curve: does pretraining save data?

Fine-tune on 300, 1,000 and 3,000 reviews and put the TF-IDF model (same data, same sizes) next to it. One run per size, one seed, so read the *shape*, not the third digit.

```python run
t0 = time.time()
rows, curve_models = [], {}
for n in (300, 1000, 3000):
    mdl = new_model()
    hh = fit_classifier(mdl, perm[:n], epochs=3 if n >= 1000 else 6, lr=1e-4)
    rows.append([n, round(hh.val_acc.iloc[-1], 4), round(tfidf_acc(n)[0], 4), round(hh.seconds.iloc[-1])])
    if n == 3000: curve_models["ft_mini_3000"] = mdl
curve = pd.DataFrame(rows, columns=["training reviews", "fine-tuned BERT-mini", "TF-IDF + logistic regression", "fine-tune seconds"])
curve["difference"] = (curve.iloc[:, 1] - curve.iloc[:, 2]).round(4)
print(curve.to_string(index=False))
print(f"{time.time() - t0:.0f}s in total")
```
```text
 training reviews  fine-tuned BERT-mini  TF-IDF + logistic regression  fine-tune seconds  difference
              300                0.6567                        0.6229                 94      0.0338
             1000                0.7092                        0.6679                108      0.0413
             3000                0.7552                        0.7233                275      0.0319
483s in total
```

> **Predict the output.** Does the fine-tuned model beat TF-IDF at every training size? Where is the gap largest, and is it large compared with the ±2.6-point interval of validation accuracy?

<details><summary>Answer</summary>

Read the table above. The expected picture: the fine-tuned model is ahead of TF-IDF at the larger sizes, by a few points, which is **comparable to the width of the validation interval** (about ±2.6 points). So with these data, this small model and one run per cell, "fine-tuning wins" is suggested, not proven; section 7 shows how to test it properly with a paired test on the same examples. Do not expect the dramatic gaps reported for large models: they come from models with 100x more parameters pretrained on 1000x more text. The mechanism is the same, the size of the effect is not.

</details>

### 4.4 The same thing with `Trainer`

Hugging Face's `Trainer` packages the loop above: batching, padding (a *collator*), optimiser, schedule, evaluation and checkpoints, configured by `TrainingArguments`. It is the tool you meet in tutorials and most codebases. It does not do anything you could not write, and knowing the loop is what lets you debug it.

*Shown, not run here: it repeats the training of 4.2 and its output would teach nothing new.*

```python
from transformers import Trainer, TrainingArguments, DataCollatorWithPadding
from datasets import Dataset

sub_ds = Dataset.from_dict({"text": [txt["train"][i] for i in n1000], "label": lab["train"][n1000].tolist()}).map(tokenize, batched=True)
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    return {"accuracy": float((logits.argmax(-1) == labels).mean())}

args = TrainingArguments(output_dir="trainer_out", num_train_epochs=3, per_device_train_batch_size=32, per_device_eval_batch_size=128,
                         learning_rate=1e-4, weight_decay=0.01, warmup_steps=0.1, lr_scheduler_type="linear", eval_strategy="epoch",
                         save_strategy="no", logging_strategy="no", report_to="none", seed=0, use_cpu=True, disable_tqdm=True)
trainer = Trainer(model=new_model(), args=args, train_dataset=sub_ds, eval_dataset=tokd["validation"],
                  data_collator=DataCollatorWithPadding(tok), compute_metrics=compute_metrics)
trainer.train()
print(trainer.evaluate())
```

Line by line, this is our loop: `TrainingArguments` holds the recipe of 4.1 (learning rate, epochs, warm-up, schedule, weight decay, seed); `DataCollatorWithPadding` is our `make_batch` (dynamic padding, with the attention mask); `compute_metrics` is our `accuracy`; `trainer.train()` is `fit_classifier`. In `transformers` 4.x the warm-up fraction was called `warmup_ratio`; in 5.x `warmup_steps` also accepts a float below 1 as a fraction. Argument names like this are the most common reason a tutorial fails to run: read the error message and the current documentation. *Measured in an earlier run on this machine:* it gave 0.725 against our loop's 0.709, a 1.6-point difference between two correct implementations of the same recipe, which is the run-to-run noise of section 5 in action.


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate fine-tuning as a ball rolling downhill on a loss landscape: the pretrained weights start near a good valley; a small learning rate settles in; a large one bounces out. Add a second panel plotting learning rate versus step for warm-up followed by linear decay."

### 4.5 Try it

1. In `fit_classifier`, remove the warm-up (`warmup=0`) and the clipping (`clip=1e9`). Does 1,000-review training still work? Try three seeds.
2. Evaluate on the validation set *before* training and after each epoch; the first number should be near 0.5. Why is it useful to log it?
3. Switch to `epochs=1`. How much of the final accuracy do you already have?

## 5. When fine-tuning goes wrong

Fine-tuning is simple to run and surprisingly easy to get wrong without noticing. Five experiments, all on 1,000 reviews with BERT-mini.

### 5.1 The learning rate

**Question.** You fine-tune BERT-mini on 1,000 reviews with learning rates `1e-5, 5e-5, 1e-4, 1e-3, 3e-3`. What do you expect at the two ends, and what does a rate that is far too high look like?

<details><summary>Answer</summary>

- **Too low** (`1e-5`): the weights barely move in three epochs. The training loss is still high at the end (0.679 in that run) and accuracy is well below what the model can do. Not a bug, just an under-trained model.
- **A wide middle range** works about equally well, and the very top of it can be the best: *measured in an earlier run on this machine with exactly the loop of 4.2* (BERT-mini, 1,000 reviews, 3 epochs), `1e-5` gave 0.618, `5e-5` gave 0.680, `1e-4` gave 0.709 and `1e-3` gave 0.716 validation accuracy.
- **Far too high** (`3e-3` in that run) is quiet rather than dramatic: the loss did not explode, it ended at 0.696, which is `ln 2 = 0.693` (the model collapsed to predicting one class for everything), and validation accuracy was exactly 0.500.

The lesson: do not trust a default. Look at the training-loss curve and compare with a baseline.

</details>


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Show three training-loss curves for the same model with a learning rate that is too low, about right, and too high. Mark where the too-high curve flatlines at ln(2) = 0.693 and explain in one sentence why that means 'predicting the same class every time'."

### 5.2 The random seed

**Question.** You run the same configuration four times, changing only the seed (head initialisation, data order, dropout). Will the four validation accuracies be identical? Why does that matter for a blog post that says "method A beats method B by one point"?

<details><summary>Answer</summary>

They differ. The head starts from different random weights, the data arrive in a different order and dropout masks differ, so the model ends up somewhere slightly different each time. On small data the spread across seeds is commonly 1 to 3 points, **as large as many reported improvements**. Together with the ±2.6-point sampling interval of a 1,066-review validation set, a one-point gap tells you nothing. A method is only better if it wins across seeds: report a mean and a standard deviation over several runs, or use a paired test (section 7.2). *Measured in an earlier run on this machine* (4 seeds, BERT-mini, 1,000 reviews, 3 epochs, `lr=1e-4`): 0.709, 0.725, 0.709 and 0.689 validation accuracy, a mean of 0.708 with a standard deviation of 0.015 and a range of 3.7 points. *To see it yourself:* loop over `seed in range(4)` with `new_model(seed=seed)` and `fit_classifier(..., seed=seed)`; about a minute per seed.

</details>

### 5.3 Training on sorted data

The training file is sorted by label. Train on its first 1,000 rows instead of a shuffled sample:

```python run
t0 = time.time()
mdl = new_model()
bad = fit_classifier(mdl, np.arange(1000), epochs=3, lr=1e-4)
print(f"first 1,000 rows (labels: {np.bincount(lab['train'][:1000]).tolist()}): train loss {bad.train_loss.iloc[-1]:.4f}, validation accuracy {bad.val_acc.iloc[-1]:.4f} | {time.time() - t0:.0f}s")
print("predictions on the validation set:", np.bincount(predict_logits(mdl, "validation").argmax(1).numpy(), minlength=2).tolist(), "(negative, positive)")
```
```text
first 1,000 rows (labels: [0, 1000]): train loss 0.0088, validation accuracy 0.5000 | 108s
predictions on the validation set: [0, 1066] (negative, positive)
```

The training loss is nearly zero (the model learned "always positive") and the validation accuracy is 0.5. **A low training loss is not evidence of anything on its own**; this is why you print the label distribution of any subset you train on.

### 5.4 Too many epochs on too little data

**Question.** You train on only 300 reviews for 8 epochs and watch both curves. What happens to the training loss and to the validation accuracy, and what do you keep?

<details><summary>Answer</summary>

The training loss keeps falling (the model starts to memorise the 300 reviews) while the validation accuracy flattens or even drops. *Measured in an earlier run on this machine* (BERT-mini, 300 reviews, 8 epochs): the training loss fell from 0.70 to 0.39, while the validation accuracy rose to 0.674 at epoch 6 and then slipped to 0.660 at epoch 8. The remedy is to **keep the checkpoint of the best validation epoch** (early stopping), not necessarily the last one. The cost: choosing the best epoch on the validation set makes the validation score slightly optimistic, which is one more reason the final number must come from the untouched **test** set (section 7).

</details>


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw training loss and validation accuracy against epoch for a small dataset: training loss keeps falling, validation accuracy peaks and then flattens. Mark the best epoch and shade the region where the model is memorising."

### 5.5 Freezing part of the model

Most of this model's parameters are the word embeddings (section 1.1). Freezing parts of the model removes trainable parameters, and with Adam every trainable parameter also carries two moment estimates. This block only *counts* (no training), so the numbers are real and instant:

```python run
def trainable_report(model):
    tr = sum(p.numel() for p in model.parameters() if p.requires_grad); total = sum(p.numel() for p in model.parameters())
    return tr, total

rows = []
for name, freeze in [("train everything", None), ("freeze word embeddings", "embeddings"), ("freeze embeddings + first 2 blocks", "lower"), ("train only the new head (+pooler)", "all_but_head")]:
    mdl = new_model()
    for n_, p in mdl.named_parameters():
        if freeze == "embeddings" and "embeddings" in n_: p.requires_grad = False
        if freeze == "lower" and ("embeddings" in n_ or any(f"encoder.layer.{k}." in n_ for k in (0, 1))): p.requires_grad = False
        if freeze == "all_but_head" and not (n_.startswith("classifier") or "pooler" in n_): p.requires_grad = False
    tr, total = trainable_report(mdl)
    rows.append([name, f"{tr:,}", f"{100 * tr / total:.1f}%", f"{(4 * total + 12 * tr) / 1e6:.0f} MB"])
print(pd.DataFrame(rows, columns=["what is trained", "trainable parameters", "share", "weights + Adam state (float32)"]).to_string(index=False))
```
```text
                   what is trained trainable parameters  share weights + Adam state (float32)
                  train everything           11,171,074 100.0%                         179 MB
            freeze word embeddings            3,225,346  28.9%                          83 MB
freeze embeddings + first 2 blocks            1,645,826  14.7%                          64 MB
 train only the new head (+pooler)               66,306   0.6%                          45 MB
```

**Question.** Does freezing the embeddings hurt accuracy? And what happens if only the head is trained with the *same* learning rate as the full model?

<details><summary>Answer</summary>

Freezing the word-embedding table costs little or nothing (the vector of each word piece is already good; the work is done in the transformer blocks) while removing 71% of the trainable parameters. *Measured in an earlier run on this machine* (BERT-mini, 1,000 reviews, 3 epochs, `lr=1e-4`): training everything 0.709, freezing the embeddings 0.706, freezing the embeddings and the first two blocks 0.700, training only the head and pooler 0.643. Training only the head with `lr=1e-4` is clearly worse: the head sits on top of fixed features that are not specialised (section 3.2), and a head alone needs a larger learning rate (about `1e-2`) than a whole network. *To see it yourself:* pass each frozen model to `fit_classifier(mdl, n1000, epochs=3, lr=1e-4)`; about a minute each.

</details>

### 5.6 A checklist before you trust a fine-tuning run

1. Printed the label distribution of the training subset (and shuffled).
2. Compared with a classical baseline **at the same training size**.
3. Evaluated the starting point (random head ≈ chance) to be sure the evaluation code works.
4. Looked at the loss curve: falling, not stuck at `ln(classes)`.
5. Repeated with at least 3 seeds; reported mean ± std.
6. Chosen the learning rate and epochs on the **validation** set, used the **test** set once at the end.
7. Checked train/validation/test for duplicates.

## 6. LoRA and parameter-efficient fine-tuning

### 6.1 Why full fine-tuning gets expensive

Training with Adam needs, for every **trainable** parameter, its gradient and two moment estimates, on top of the weight itself. In `float32` (4 bytes) that is `4 + 4 + 8 = 16` bytes per trainable parameter; a frozen parameter costs only its 4 bytes. And every task you fine-tune for produces a **full copy** of the model to store and serve.

```python run
def memory_gb(n_total, n_trainable): return (4 * n_total + 12 * n_trainable) / 1e9           # weights + (grad + 2 Adam moments) for trainable ones
rows = []
for name, n in [("BERT-mini", 11.2e6), ("DistilBERT", 67e6), ("a 1-billion-parameter model", 1e9), ("a 7-billion-parameter model", 7e9)]:
    rows.append([name, f"{n / 1e6:,.0f} M", f"{memory_gb(n, n):,.2f} GB", f"{memory_gb(n, 0.005 * n):,.2f} GB"])
print(pd.DataFrame(rows, columns=["model", "parameters", "memory for weights + optimiser, full fine-tuning", "same, training 0.5% of parameters"]).to_string(index=False))
print("(activations and the data come on top of this; the table is the part that parameter-efficient methods remove)")
```
```text
                      model parameters memory for weights + optimiser, full fine-tuning same, training 0.5% of parameters
                  BERT-mini       11 M                                          0.18 GB                           0.05 GB
                 DistilBERT       67 M                                          1.07 GB                           0.27 GB
a 1-billion-parameter model    1,000 M                                         16.00 GB                           4.06 GB
a 7-billion-parameter model    7,000 M                                        112.00 GB                          28.42 GB
(activations and the data come on top of this; the table is the part that parameter-efficient methods remove)
```

**Parameter-efficient fine-tuning (PEFT)** freezes the pretrained weights and trains a small number of *new* parameters. The result is a small file per task (an *adapter*) that is combined with one shared copy of the base model.

### 6.2 LoRA: a low-rank update

A weight matrix `W` of shape `(d, k)` is changed during fine-tuning by some update `ΔW`. The **LoRA** (Low-Rank Adaptation) hypothesis: the useful update has low rank. So instead of learning all `d·k` numbers, learn two thin matrices:

```
ΔW = (α / r) · B · A         B: (d, r)   A: (r, k)   r much smaller than d and k
output = W x + (α / r) · B (A x)
```

- `A` is initialised randomly, **`B` is initialised to zero**, so at the start `ΔW = 0` and the model behaves exactly like the pretrained one. Training moves away from there.
- `r` is the **rank**, `α` a scaling constant (the effective step size of the update is `α/r`).
- Trainable parameters per adapted matrix: `r·(d + k)` instead of `d·k`. For `d = k = 256`, `r = 8`: 4,096 against 65,536.
- After training, `W + ΔW` can be **merged** into a single matrix: inference costs exactly the same as the original model.


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a big weight matrix W (256x256) as a grid next to two thin matrices B (256x8) and A (8x256). Show x flowing through W and, in parallel, through A then B, with the two results added. Label the parameter counts: 65,536 versus 4,096. Add a note that B starts as zeros."

Written from scratch (about 15 lines), and checked:

```python run
class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r=8, alpha=16, dropout=0.0):
        super().__init__()
        self.base = base
        for p in self.base.parameters(): p.requires_grad = False                    # the pretrained weights stay fixed
        self.r, self.scale = r, alpha / r
        self.A = nn.Parameter(torch.empty(r, base.in_features)); nn.init.kaiming_uniform_(self.A, a=math.sqrt(5))
        self.B = nn.Parameter(torch.zeros(base.out_features, r))                    # zero: delta W starts at 0
        self.drop = nn.Dropout(dropout)
    def forward(self, x):
        return self.base(x) + (self.drop(x) @ self.A.T @ self.B.T) * self.scale
    def merged(self):
        lin = nn.Linear(self.base.in_features, self.base.out_features)
        with torch.no_grad():
            lin.weight.copy_(self.base.weight + self.scale * self.B @ self.A); lin.bias.copy_(self.base.bias)
        return lin

torch.manual_seed(0)
base_lin = nn.Linear(256, 256)
lora = LoRALinear(base_lin, r=8, alpha=16)
x = torch.randn(5, 256)
print("at initialisation the LoRA layer equals the base layer:", bool(torch.allclose(lora(x), base_lin(x))))
print(f"trainable parameters: {sum(p.numel() for p in lora.parameters() if p.requires_grad):,} = 8 x (256 + 256) | the full matrix has {base_lin.weight.numel():,}")
lora(x).pow(2).sum().backward()
print("gradients after one backward pass -> base weight:", base_lin.weight.grad, "| A:", round(lora.A.grad.abs().max().item(), 6), "| B:", round(lora.B.grad.abs().max().item(), 4))
```
```text
at initialisation the LoRA layer equals the base layer: True
trainable parameters: 4,096 = 8 x (256 + 256) | the full matrix has 65,536
gradients after one backward pass -> base weight: None | A: 0.0 | B: 11.6827
```

Why is `A`'s gradient exactly zero at the start? Because `∂loss/∂A` passes through `B`, which is zero. `B` gets a gradient first, becomes non-zero, and only then does `A` start learning. This asymmetric initialisation is deliberate.

```python run
with torch.no_grad():                                                                  # pretend training happened: give B some values
    lora.B.normal_(0, 0.05)
m = lora.merged()
print("merged single matrix equals base + low-rank path:", bool(torch.allclose(lora(x), m(x), atol=1e-5)))
print("rank of the update delta W:", torch.linalg.matrix_rank(lora.scale * lora.B @ lora.A).item(), "<= r = 8 (a 256x256 matrix could have rank 256)")
```
```text
merged single matrix equals base + low-rank path: True
rank of the update delta W: 8 <= r = 8 (a 256x256 matrix could have rank 256)
```

### 6.3 LoRA inside BERT, and the `peft` library

We wrap the **query** and **value** projections of every attention layer (the choice of the original paper), freeze everything else except the new classifier head, and train.

```python run
def add_lora(model, targets=("query", "value"), r=8, alpha=16, dropout=0.1):
    for p in model.parameters(): p.requires_grad = False
    for name, mod in list(model.named_modules()):
        for child_name, child in list(mod.named_children()):
            if child_name in targets and isinstance(child, nn.Linear):
                setattr(mod, child_name, LoRALinear(child, r, alpha, dropout))
    for p in model.classifier.parameters(): p.requires_grad = True                  # the new head must be trained
    return model

def trainable_params(model): return [(n, p) for n, p in model.named_parameters() if p.requires_grad]

t0 = time.time()
ours = add_lora(new_model())
tr, total = trainable_report(ours)
print(f"our LoRA: trainable {tr:,} of {total:,} ({100 * tr / total:.2f}%)")
h_ours = fit_classifier(ours, n1000, epochs=3, lr=3e-3, params=trainable_params(ours))
print(f"validation accuracy {h_ours.val_acc.iloc[-1]:.4f} | {time.time() - t0:.0f}s | full fine-tuning at 1,000 reviews (section 4.2): {h.val_acc.iloc[-1]:.4f}")

# the same with the peft library
from peft import LoraConfig, get_peft_model, TaskType
t0 = time.time()
pm = get_peft_model(new_model(), LoraConfig(r=8, lora_alpha=16, target_modules=["query", "value"], lora_dropout=0.1, task_type=TaskType.SEQ_CLS))
pm.print_trainable_parameters()
h_peft = fit_classifier(pm, n1000, epochs=3, lr=3e-3, params=trainable_params(pm))
print(f"peft LoRA: validation accuracy {h_peft.val_acc.iloc[-1]:.4f} | {time.time() - t0:.0f}s")
```
```text
our LoRA: trainable 33,282 of 11,203,842 (0.30%)
validation accuracy 0.7214 | 48s | full fine-tuning at 1,000 reviews (section 4.2): 0.7092
trainable params: 33,282 || all params: 11,204,356 || trainable%: 0.2970
peft LoRA: validation accuracy 0.7205 | 45s
```

The trainable counts agree, as they must: the same matrices, the same rank, the same head. The accuracies are close but not identical (different random initialisation of `A`), and both are in the neighbourhood of full fine-tuning while training **0.3% of the parameters**.

Note the learning rate: `3e-3`, thirty times the full-fine-tuning value.

**Question.** Why does LoRA want a much larger learning rate than full fine-tuning, and what happens if you use the full-fine-tuning value?

<details><summary>Answer</summary>

The new parameters start from nothing (`B = 0`), and the frozen base cannot be damaged by big steps, so LoRA needs larger updates to move far enough. With the full-fine-tuning rate it does not train at all. *Measured in an earlier run on this machine* (BERT-mini, 1,000 reviews, r=8): learning rate `1e-4` left the model at 0.544 validation accuracy with a training loss of 0.692 (still `ln 2`), while `3e-3` reached 0.721. A rate that is safe for pretrained weights is too timid for fresh adapter weights.

</details>

### 6.4 Rank and target modules

The two knobs: how big is the update (`r`), and which matrices get one. Counting what each choice costs needs no training, so the numbers below are real and instant:

```python run
rows = []
all_linear = ("query", "key", "value", "dense")                                       # attention.output.dense, intermediate.dense, output.dense too
for label, targets, r in [("query,value, r=1", ("query", "value"), 1), ("query,value, r=4", ("query", "value"), 4), ("query,value, r=8", ("query", "value"), 8),
                          ("query,value, r=32", ("query", "value"), 32), ("all linear layers, r=8", all_linear, 8)]:
    mdl = add_lora(new_model(), targets, r=r, alpha=2 * r)
    tr, total = trainable_report(mdl)
    rows.append([label, f"{tr:,}", f"{100 * tr / total:.2f}%"])
print(pd.DataFrame(rows, columns=["LoRA configuration", "trainable parameters", "share of the model"]).to_string(index=False))
```
```text
    LoRA configuration trainable parameters share of the model
      query,value, r=1                4,610              0.04%
      query,value, r=4               16,898              0.15%
      query,value, r=8               33,282              0.30%
     query,value, r=32              131,586              1.16%
all linear layers, r=8              152,066              1.34%
```

**Question.** On a task as simple as this one, which matters more for accuracy: raising the rank from 8 to 32, or adapting all linear layers instead of only query and value?

<details><summary>Answer</summary>

Accuracy is not very sensitive to the rank, and adapting more matrices did **not** help here. *Measured in an earlier run on this machine* (BERT-mini, 1,000 reviews, 3 epochs, `lr=3e-3`): query and value with r=1 gave 0.698, r=4 gave 0.711, r=8 gave 0.721, r=32 gave 0.708, and all linear layers with r=8 gave 0.705. All of these are within about two points, which is inside the seed noise of section 5.2. The usual advice (r between 4 and 16; adapt all linear layers for harder tasks) is a starting point, not a law: on an easy task nothing beats the cheap configuration, and the right choice has to be tuned on the validation set with several seeds. *To see it yourself:* train each configuration with `fit_classifier(mdl, n1000, epochs=3, lr=3e-3, params=trainable_params(mdl))`; about 40 seconds each.

</details>


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot a curve of validation accuracy against LoRA rank r (1, 4, 8, 32, 64) for an easy task and for a hard task. Show that the easy task saturates at a small rank while the hard task keeps improving, and mark the parameter count on a second axis."

### 6.5 Adapters are small files

```python run
adir = tmp / "adapter_mini"
pm.save_pretrained(adir)
full_dir = tmp / "full_mini"
new_model().save_pretrained(full_dir)
size = lambda d: sum(f.stat().st_size for f in pathlib.Path(d).rglob("*") if f.is_file()) / 1e6
print("files in the adapter folder:", sorted(f.name for f in adir.iterdir()))
print(f"adapter: {size(adir):.2f} MB | full model: {size(full_dir):.1f} MB  ({size(full_dir) / size(adir):.0f}x larger)")

from peft import PeftModel
fresh = PeftModel.from_pretrained(new_model(seed=123), adir)                              # base with a DIFFERENT random head, adapter restores the trained one
pm.eval(); fresh.eval()
x_, m_, _ = make_batch("validation", range(16))
with torch.no_grad(): same = torch.allclose(pm(input_ids=x_, attention_mask=m_).logits, fresh(input_ids=x_, attention_mask=m_).logits, atol=1e-5)
print("a base model + the saved adapter reproduces the trained model's logits:", bool(same))
merged = pm.merge_and_unload()
with torch.no_grad(): same2 = torch.allclose(merged(input_ids=x_, attention_mask=m_).logits, fresh(input_ids=x_, attention_mask=m_).logits, atol=1e-4)
print("after merge_and_unload() the plain model gives the same logits (no adapter overhead at inference):", bool(same2), "|", type(merged).__name__)
```
```text
files in the adapter folder: ['README.md', 'adapter_config.json', 'adapter_model.safetensors']
adapter: 0.14 MB | full model: 44.7 MB  (315x larger)
a base model + the saved adapter reproduces the trained model's logits: True
after merge_and_unload() the plain model gives the same logits (no adapter overhead at inference): True | BertForSequenceClassification
```

One base model and one small adapter per task is how a single deployment can serve hundreds of fine-tuned variants.

### 6.6 DistilBERT: full fine-tuning against LoRA at a realistic size

On the 67-million-parameter model the differences in cost start to matter. Same 1,000 reviews, 2 epochs. This takes a few minutes per model on a CPU.

```python run
t0 = time.time()
dres = {}
mdl_d_full = new_model(DISTIL)
tr, total = trainable_report(mdl_d_full)
hd = fit_classifier(mdl_d_full, n1000, epochs=2, lr=5e-5)
dres["full fine-tuning"] = dict(trainable=tr, total=total, acc=hd.val_acc.iloc[-1], seconds=hd.seconds.iloc[-1])

pm_d = get_peft_model(new_model(DISTIL), LoraConfig(r=8, lora_alpha=16, target_modules=["q_lin", "v_lin"], lora_dropout=0.1, task_type=TaskType.SEQ_CLS))
tr, total = trainable_report(pm_d)
hl = fit_classifier(pm_d, n1000, epochs=2, lr=1e-3, params=trainable_params(pm_d))
dres["LoRA r=8 (q, v)"] = dict(trainable=tr, total=total, acc=hl.val_acc.iloc[-1], seconds=hl.seconds.iloc[-1])

rows = [[k, f"{v['trainable']:,}", f"{100 * v['trainable'] / v['total']:.2f}%", round(v["acc"], 4), round(v["seconds"]), f"{memory_gb(v['total'], v['trainable']):.2f} GB"] for k, v in dres.items()]
print(pd.DataFrame(rows, columns=["method (DistilBERT, 1,000 reviews)", "trainable parameters", "share", "validation accuracy", "seconds", "weights + optimiser"]).to_string(index=False))
pm_d.save_pretrained(tmp / "adapter_distil"); mdl_d_full.save_pretrained(tmp / "full_distil")
print(f"adapter on disk {size(tmp / 'adapter_distil'):.2f} MB | full model on disk {size(tmp / 'full_distil'):.0f} MB")
print(f"for reference: TF-IDF at 1,000 reviews {tfidf_acc(1000)[0]:.4f} | BERT-mini full fine-tuning {h.val_acc.iloc[-1]:.4f} | {time.time() - t0:.0f}s in total")
```
```text
method (DistilBERT, 1,000 reviews) trainable parameters   share  validation accuracy  seconds weights + optimiser
                  full fine-tuning           66,955,010 100.00%               0.8189      364             1.07 GB
                   LoRA r=8 (q, v)              739,586   1.09%               0.8236      303             0.28 GB
adapter on disk 2.97 MB | full model on disk 268 MB
for reference: TF-IDF at 1,000 reviews 0.6679 | BERT-mini full fine-tuning 0.7092 | 671s in total
```

> **Predict the output.** Does LoRA match full fine-tuning here? Is it *faster* in wall-clock time on this CPU? What is it that LoRA clearly saves?

<details><summary>Answer</summary>

Read the table above. LoRA matches full fine-tuning (0.824 against 0.819, a difference far inside the seed noise of section 5.2) with 1.1% of the trainable parameters. It is a little faster here (about 17%), not dramatically: the forward pass is the same size, and the backward pass still has to pass gradients through every layer to reach the early adapters; what disappears is the weight-gradient work for frozen matrices and the optimiser update. On a GPU the large savings are in **memory** (the optimiser state and the gradient buffers) and in **storage and serving** (a 2 MB adapter against a 255 MB model). For a model that does not fit in memory for full fine-tuning, that difference decides whether you can train at all.

</details>

Both DistilBERT models are far ahead of BERT-mini and TF-IDF at 1,000 reviews, which is the whole point of starting from a better pretrained model. We keep these two for the evaluation in the next section.

### 6.7 Other parameter-efficient methods

| Method | Idea | Trainable |
|---|---|---|
| **LoRA** | low-rank updates to chosen weight matrices; mergeable | ~0.1% to 1% |
| **Adapters** | small bottleneck layers inserted after attention and MLP | ~1% |
| **Prefix / prompt tuning** | learn extra "virtual token" embeddings, prepended to the input | ~0.01% to 0.1% |
| **IA³** | learn per-channel scaling vectors | ~0.01% |
| **BitFit** | train only the bias terms | ~0.1% |
| **QLoRA** | LoRA on top of a base model stored in 4-bit precision | as LoRA, base memory ÷ 4 |

All except QLoRA run on this machine through `peft`. QLoRA needs a GPU and the `bitsandbytes` library, so it is described here, not run.

### 6.8 Try it

1. Change `alpha` from `2r` to `r/2` in the rank sweep (a smaller effective step). What happens to accuracy at the same learning rate, and what does it say about `α` and the learning rate being partly interchangeable?
2. Apply LoRA to **only the classifier's input layer** (`pooler.dense`). Is it enough?
3. Implement **BitFit** with `requires_grad` (train only parameters whose name ends in `bias`, plus the head). Where does it land in the table?

## 7. Evaluating a fine-tuned model

The syllabus outcome is a *claim*: "the fine-tuned model beats the base model on a held-out set." This section is about making that claim true, and showing it.

### 7.1 Metrics

Accuracy is the share of correct predictions. For two classes the **confusion matrix** counts the four outcomes, from which come **precision** (of the reviews called positive, how many are?), **recall** (of the positive reviews, how many were found?) and their harmonic mean **F1**. Accuracy is fine when the classes are balanced and errors cost the same; with a 95/5 imbalance, a model that always says "negative" scores 95% accuracy and is useless, and recall on the rare class is the number to watch. Here the classes are balanced.

```python run
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, accuracy_score
def probs_of(model, split): return F.softmax(predict_logits(model, split), 1).numpy()
P = {"val": probs_of(mdl_d_full, "validation")}
pred = P["val"].argmax(1)
cm = confusion_matrix(lab["validation"], pred)
p_, r_, f_, _ = precision_recall_fscore_support(lab["validation"], pred, labels=[1])
print("confusion matrix on the validation set (rows = true, columns = predicted; order negative, positive):\n", cm)
print(f"accuracy {accuracy_score(lab['validation'], pred):.4f} | positive class: precision {p_[0]:.4f}, recall {r_[0]:.4f}, F1 {f_[0]:.4f}")
```
```text
confusion matrix on the validation set (rows = true, columns = predicted; order negative, positive):
 [[425 108]
 [ 85 448]]
accuracy 0.8189 | positive class: precision 0.8058, recall 0.8405, F1 0.8228
```

### 7.2 Is model A really better than model B? A paired test

Two models evaluated on the **same** test reviews can be compared much more sharply than by two separate confidence intervals, because most reviews are right or wrong for both. Only the reviews where they *disagree* carry information. Let `b` = reviews A gets right and B wrong, `c` = the reverse. If the models were equally good, `b` and `c` would be like heads and tails of a fair coin: the **exact McNemar test** is the binomial test of `b` against `b + c` trials with probability ½. A **bootstrap** over test reviews gives a confidence interval for the accuracy difference.


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Explain McNemar's test with a 2x2 grid: rows = model A right/wrong, columns = model B right/wrong, 1,066 test reviews as dots. Colour the two disagreement cells, and show how only those dots decide whether A is really better, like counting heads and tails of a fair coin."

Here are all models on the test set, with the *test* split touched for the first time in this chapter. The list of models was fixed on the validation set, and we report all of them, whatever the result.

```python run
from scipy.stats import binomtest
y_te = lab["test"]
v_t, clf_t = tfidf_acc(len(perm))[1]
probe = make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=2000)).fit(feats[("mean", "train")], lab["train"])
feats_test = extract(body, "test", "mean")
preds = {
    "random head (BERT-mini)":            predict_logits(base_clf, "test").argmax(1).numpy(),
    "TF-IDF + logistic reg. (8,530)":     clf_t.predict(v_t.transform(txt["test"])),
    "TF-IDF + logistic reg. (3,000)":     tfidf_acc(3000)[1][1].predict(tfidf_acc(3000)[1][0].transform(txt["test"])),
    "frozen BERT-mini + logistic reg.":   probe.predict(feats_test),
    "BERT-mini, full FT (3,000)":         predict_logits(curve_models["ft_mini_3000"], "test").argmax(1).numpy(),
    "DistilBERT, full FT (1,000)":        predict_logits(mdl_d_full, "test").argmax(1).numpy(),
    "DistilBERT, LoRA r=8 (1,000)":       predict_logits(pm_d, "test").argmax(1).numpy(),
}
rows = []
for k, p in preds.items():
    a = (p == y_te).mean(); half = 1.96 * math.sqrt(a * (1 - a) / len(y_te))
    rows.append([k, round(a, 4), f"±{half:.3f}"])
print(pd.DataFrame(rows, columns=["model", "TEST accuracy", "95% interval"]).to_string(index=False))

def paired(pa, pb, y, n_boot=2000, seed=0):
    ca, cb = pa == y, pb == y
    b, c = int((ca & ~cb).sum()), int((~ca & cb).sum())
    p = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    rng = np.random.default_rng(seed); idx = rng.integers(0, len(y), (n_boot, len(y)))
    diffs = ca[idx].mean(1) - cb[idx].mean(1)
    return dict(diff=ca.mean() - cb.mean(), only_A=b, only_B=c, p_value=p, ci=(np.percentile(diffs, 2.5), np.percentile(diffs, 97.5)))

pairs = [("DistilBERT, full FT (1,000)", "random head (BERT-mini)"), ("DistilBERT, full FT (1,000)", "TF-IDF + logistic reg. (8,530)"),
         ("DistilBERT, full FT (1,000)", "DistilBERT, LoRA r=8 (1,000)"), ("BERT-mini, full FT (3,000)", "TF-IDF + logistic reg. (3,000)"),
         ("DistilBERT, LoRA r=8 (1,000)", "BERT-mini, full FT (3,000)")]
rows = []
for a_, b_ in pairs:
    r = paired(preds[a_], preds[b_], y_te)
    rows.append([f"{a_}  vs  {b_}", f"{r['diff']:+.4f}", f"[{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}]", f"{r['only_A']} / {r['only_B']}", f"{r['p_value']:.2g}"])
print()
print(pd.DataFrame(rows, columns=["A  vs  B", "accuracy A - B", "95% bootstrap interval", "only A right / only B right", "McNemar p"]).to_string(index=False))
```
```text
                           model  TEST accuracy 95% interval
         random head (BERT-mini)         0.5056       ±0.030
  TF-IDF + logistic reg. (8,530)         0.7908       ±0.024
  TF-IDF + logistic reg. (3,000)         0.7542       ±0.026
frozen BERT-mini + logistic reg.         0.7233       ±0.027
      BERT-mini, full FT (3,000)         0.7580       ±0.026
     DistilBERT, full FT (1,000)         0.8227       ±0.023
    DistilBERT, LoRA r=8 (1,000)         0.8180       ±0.023

                                                       A  vs  B accuracy A - B 95% bootstrap interval only A right / only B right McNemar p
       DistilBERT, full FT (1,000)  vs  random head (BERT-mini)        +0.3171       [+0.281, +0.356]                    428 / 90     1e-53
DistilBERT, full FT (1,000)  vs  TF-IDF + logistic reg. (8,530)        +0.0319       [+0.003, +0.063]                   145 / 111     0.039
  DistilBERT, full FT (1,000)  vs  DistilBERT, LoRA r=8 (1,000)        +0.0047       [-0.011, +0.021]                     39 / 34      0.64
 BERT-mini, full FT (3,000)  vs  TF-IDF + logistic reg. (3,000)        +0.0038       [-0.025, +0.032]                   127 / 123      0.85
   DistilBERT, LoRA r=8 (1,000)  vs  BERT-mini, full FT (3,000)        +0.0600       [+0.033, +0.089]                    146 / 82   2.7e-05
```

How to read the paired table:

- A difference is **credible** when the bootstrap interval excludes 0 and the p-value is small. The interval says *how large* the advantage may be, the p-value only says it is probably not zero.
- A **non-significant** result (large p, interval around 0) is not "the models are equal": it says this test set cannot tell them apart. LoRA against full fine-tuning is the typical case.
- Every comparison above uses the **same 1,066 test reviews**. That quantifies the uncertainty from the *test sample*, not from training randomness (the seed noise of section 5.2): to claim "method A is better than B" in general you need several training seeds as well.
- Running many comparisons inflates false positives (the multiple-comparisons problem of ds.09): we pre-specified five.

That table is the evidence for the syllabus claim, and it has three different readings:

- Fine-tuned DistilBERT against the **base model with a random head**: +0.317 (interval +0.28 to +0.36), `p ≈ 1e-53`. Overwhelming.
- Against **TF-IDF trained on 8× more reviews**: +0.032, interval **+0.003 to +0.063**, `p = 0.039`. The advantage is probably real but barely: the lower end of the interval is almost zero. Honest wording: "slightly better, with eight times less labelled data".
- **BERT-mini fine-tuned on 3,000 reviews against TF-IDF on the same 3,000**: +0.004, interval −0.025 to +0.032, `p = 0.85`. On the validation set (4.3) this model looked 3 points ahead; on the test set the advantage **did not replicate**. That is not a failure of the method, it is exactly why the test set exists: a 3-point gap on one validation sample was inside the noise.

LoRA against full fine-tuning: +0.005, `p = 0.64`: indistinguishable, which is the usual result.


> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a reliability diagram: confidence (x axis, 0.5 to 1) against actual accuracy (y axis) with the diagonal as perfect calibration. Show an over-confident model's curve below the diagonal and how dividing the logits by a temperature T>1 pulls it toward the diagonal without changing any predicted class."

### 7.3 Calibration

A classifier says "positive, 91% confident". Is it right 91% of the time among such predictions? **Calibration** compares the stated confidence with the observed accuracy, per confidence bin; the **expected calibration error** (ECE) is the weighted average gap. Fine-tuned transformers often turn out **over-confident**, especially after many epochs. A cheap fix is **temperature scaling**: divide the logits by one number `T`, chosen on the validation set to minimise the log loss. It does not change the predicted class, only the confidence.

```python run
def ece_table(conf, correct, bins=5):
    edges = np.linspace(0.5, 1.0, bins + 1); rows, ece = [], 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (conf >= lo) & (conf < hi + (1e-9 if hi == 1.0 else 0))
        if sel.sum(): rows.append([f"{lo:.1f}-{hi:.1f}", int(sel.sum()), round(conf[sel].mean(), 3), round(correct[sel].mean(), 3)]); ece += sel.mean() * abs(conf[sel].mean() - correct[sel].mean())
    return pd.DataFrame(rows, columns=["confidence bin", "n", "mean confidence", "accuracy"]), ece

lg_val, lg_test = predict_logits(mdl_d_full, "validation"), predict_logits(mdl_d_full, "test")
conf = F.softmax(lg_test, 1).max(1).values.numpy(); ok = (lg_test.argmax(1).numpy() == y_te)
tbl, ece0 = ece_table(conf, ok)
print(tbl.to_string(index=False)); print(f"expected calibration error on TEST: {ece0:.4f}")

# temperature scaling: fit T on VALIDATION by minimising negative log-likelihood
T = torch.ones(1, requires_grad=True)
opt = torch.optim.LBFGS([T], lr=0.1, max_iter=100)
yv = torch.tensor(lab["validation"])
def closure():
    opt.zero_grad(); loss = F.cross_entropy(lg_val / T, yv); loss.backward(); return loss
opt.step(closure)
conf1 = F.softmax(lg_test / T.detach(), 1).max(1).values.numpy()
_, ece1 = ece_table(conf1, ok)
print(f"temperature T = {T.item():.3f} (fitted on validation) | ECE on TEST after scaling {ece1:.4f} | predicted classes unchanged: {bool((lg_test / T.detach()).argmax(1).numpy().tolist() == lg_test.argmax(1).numpy().tolist())}")
```
```text
confidence bin   n  mean confidence  accuracy
       0.5-0.6  69            0.552     0.536
       0.6-0.7  98            0.651     0.663
       0.7-0.8 141            0.760     0.695
       0.8-0.9 356            0.861     0.840
       0.9-1.0 402            0.921     0.940
expected calibration error on TEST: 0.0249
temperature T = 1.030 (fitted on validation) | ECE on TEST after scaling 0.0265 | predicted classes unchanged: True
```

Here the model is already **well calibrated**: an ECE of 0.025, and in each bin the accuracy is close to the stated confidence. The fitted temperature is 1.03, almost 1, and scaling does not improve the ECE (0.0265). The lesson is to *measure* before correcting: two epochs on 1,000 reviews did not make this model over-confident, so temperature scaling has nothing to fix. (Calibration of the project model in section 9 is slightly worse, 0.032, with the same conclusion.)

### 7.4 Look at the errors

A single accuracy number hides *where* the model fails. Two habits: read the most confident mistakes, and compute accuracy on **slices** of the data (with the sample size of each slice, since small slices are noisy).

```python run
conf_all = F.softmax(lg_test, 1); pred_t = lg_test.argmax(1).numpy()
wrong = np.where(pred_t != y_te)[0]
worst = wrong[np.argsort(-conf_all.max(1).values.numpy()[wrong])][:6]
print("most confident mistakes on the test set (true label, confidence):")
for i in worst: print(f"  [{y_te[i]}] {conf_all[i].max().item():.2f}  {txt['test'][i][:120]}")

neg_words = re.compile(r"\b(not|no|never|nothing|n't|neither|nor|hardly|barely)\b|n't")
length_q = pd.qcut([len(t.split()) for t in txt["test"]], 4, labels=["shortest 25%", "25-50%", "50-75%", "longest 25%"])
slices = {"contains a negation word": np.array([bool(neg_words.search(t.lower())) for t in txt["test"]]),
          "no negation word": np.array([not neg_words.search(t.lower()) for t in txt["test"]])}
slices.update({f"length: {q}": np.array(length_q == q) for q in length_q.categories})
rows = []
for name, sel in slices.items():
    a = (pred_t[sel] == y_te[sel]).mean(); rows.append([name, int(sel.sum()), round(a, 4), f"±{1.96 * math.sqrt(a * (1 - a) / sel.sum()):.3f}"])
print("\n" + pd.DataFrame(rows, columns=["slice of the test set", "n", "accuracy", "95% interval"]).to_string(index=False))
```
```text
most confident mistakes on the test set (true label, confidence):
  [1] 0.93  at its worst , the movie is pretty diverting ; the pity is that it rarely achieves its best .
  [0] 0.93  the beautiful , unusual music is this film's chief draw , but its dreaminess may lull you to sleep .
  [0] 0.93  more successful at relating history than in creating an emotionally complex , dramatically satisfying heroine
  [0] 0.93  a very familiar tale , one that's been told by countless filmmakers about italian- , chinese- , irish- , latin- , indian
  [0] 0.93  though its rather routine script is loaded with familiar situations , the movie has a cinematic fluidity and sense of in
  [0] 0.92  one regards reign of fire with awe . what a vast enterprise has been marshaled in the service of such a minute idea .

   slice of the test set   n  accuracy 95% interval
contains a negation word 243    0.8313       ±0.047
        no negation word 823    0.8202       ±0.026
    length: shortest 25% 281    0.8434       ±0.042
          length: 25-50% 261    0.8391       ±0.045
          length: 50-75% 257    0.8288       ±0.046
     length: longest 25% 267    0.7790       ±0.050
```

Read the error list as an annotator: some "mistakes" are sarcasm, some are reviews that talk about a bad film in a positive tone, some are label noise. The slice table shows whether the weakness is concentrated. Here negation is *not* a weak spot (0.83 with a negation word, 0.82 without, inside each other's intervals), but the **longest quarter of the reviews** is the weakest (0.78 against about 0.84 for the shortest), which suggests that long, mixed reviews are where more data or a longer `max_length` should be tried first. Note the intervals: with 250 reviews per slice they are ±4 to 5 points, so this is a lead to investigate, not a finding.

### 7.5 Behavioural tests

A held-out set measures average performance on *the same distribution as the training data*. **Behavioural tests** (the CheckList idea) probe specific capabilities with small hand-written inputs where the right answer is clear. Three kinds: **minimum functionality** (obvious cases), **invariance** (a change that must not alter the answer, like a different movie name), and **directional** (a change that must move the score in a known direction).

```python run
@torch.no_grad()
def p_pos(model, sentences):
    enc_ = tok(sentences, padding=True, truncation=True, max_length=64, return_tensors="pt")
    model.eval(); return F.softmax(model(input_ids=enc_["input_ids"], attention_mask=enc_["attention_mask"]).logits, 1)[:, 1].numpy()
mft = [("this movie is wonderful", 1), ("a brilliant , moving film", 1), ("i loved every minute of it", 1), ("a dull , lifeless mess", 0),
       ("this is the worst film of the year", 0), ("i hated it", 0), ("an utter waste of time", 0), ("a delightful surprise", 1)]
neg = [("this movie is not good", 0), ("this movie is not bad", 1), ("i did not enjoy a single minute", 0), ("it is not boring at all", 1)]
inv_base = "the acting in {} was {}"
inv = [(inv_base.format(n, adj), l) for n in ("titanic", "casablanca", "the new film by jim jarmusch") for adj, l in (("superb", 1), ("terrible", 0))]
tests = {"minimum functionality": mft, "negation": neg, "name invariance": inv}
clf_pred = lambda s: clf_t.predict_proba(v_t.transform(s))[:, 1]
rows = []
for tname, cases in tests.items():
    sents, labels = [c[0] for c in cases], np.array([c[1] for c in cases])
    for mname, fn in (("TF-IDF + LR", clf_pred), ("DistilBERT full FT", lambda s: p_pos(mdl_d_full, s))):
        rows.append([tname, mname, len(cases), f"{((fn(sents) > 0.5).astype(int) != labels).mean():.0%}"])
print(pd.DataFrame(rows, columns=["test type", "model", "cases", "failure rate"]).to_string(index=False))
base_s = ["the film was good", "a fun and charming movie", "the plot is clever"]
up = [s + " but the ending is terrible" for s in base_s]
for mname, fn in (("TF-IDF + LR", clf_pred), ("DistilBERT full FT", lambda s: p_pos(mdl_d_full, s))):
    print(f"directional ({mname}): adding 'but the ending is terrible' lowers P(positive) in {np.mean(fn(up) < fn(base_s)):.0%} of cases")
```
```text
            test type              model  cases failure rate
minimum functionality        TF-IDF + LR      8           0%
minimum functionality DistilBERT full FT      8           0%
             negation        TF-IDF + LR      4          50%
             negation DistilBERT full FT      4          50%
      name invariance        TF-IDF + LR      6          50%
      name invariance DistilBERT full FT      6           0%
directional (TF-IDF + LR): adding 'but the ending is terrible' lowers P(positive) in 100% of cases
directional (DistilBERT full FT): adding 'but the ending is terrible' lowers P(positive) in 100% of cases
```

On these tiny suites both models pass the obvious cases; both fail half of the negation cases (so "not good" and "not bad" are genuinely hard for them); TF-IDF fails half of the name-invariance cases while DistilBERT fails none; and both respond in the right direction to a negative clause. The failure rates are rough, because the suites are tiny. What matters is the method: a held-out accuracy of 0.84 coexists with specific blind spots, and a few dozen well-chosen cases find them. Real projects keep such suites in version control and run them like unit tests on every new model.

### 7.6 A checklist for "it beats the base model"

1. The comparison models are named and include a **non-neural baseline** and the **untuned starting point**.
2. All were evaluated on the **same** held-out data, touched once, after every choice was made on validation data.
3. The difference is reported with an **interval** and a **paired test**, not two bare numbers.
4. Run-to-run variation (seeds) was measured, not assumed.
5. Calibration, slices and a behavioural suite were looked at, not only accuracy.
6. The test data were checked for **overlap with the training data**, and, for pretrained models, you considered whether the pretraining corpus may have contained them (**contamination**: a pretrained model that has memorised the benchmark inflates every score).

### 7.7 Try it

1. Compute the paired comparison between full DistilBERT and LoRA with the **validation** set instead of the test set. Do the conclusions agree?
2. Add a fifth bin to the reliability table with `bins=10`. What changes, and why are the lower-confidence bins noisy?
3. Write ten more negation test cases. Does the failure rate of either model change by more than the sampling noise of such a small suite?

## 8. Beyond classification, and what to do at scale

### 8.1 Other heads, same recipe

The body is shared; the head and the loss change with the task. `transformers` ships an `AutoModelFor…` class for each.

| Task | Class | Output | Loss |
|---|---|---|---|
| text classification | `AutoModelForSequenceClassification` | one vector per text | cross-entropy |
| token classification (named entities) | `AutoModelForTokenClassification` | one vector per token | cross-entropy per token |
| extractive question answering | `AutoModelForQuestionAnswering` | start and end position scores | cross-entropy on two positions |
| text generation | `AutoModelForCausalLM` | next-token logits (as in ml.04) | next-token cross-entropy |
| translation, summarisation | `AutoModelForSeq2SeqLM` | encoder-decoder | next-token cross-entropy |

Fine-tuning a causal language model on instruction–answer pairs is **instruction tuning**; adapting it further with human preference data is what produces assistant-style models (that is the subject of the llm.* modules).

### 8.2 Scaling tricks, and one you can verify here

Real fine-tuning runs use: **mixed precision** (`bf16`/`fp16`: half the memory and faster matrix products on a GPU), **gradient accumulation** (simulate a big batch with several small ones), **gradient checkpointing** (recompute activations to save memory), **data/model parallelism** (`accelerate`, DDP, FSDP) and **quantisation** (4-bit base weights, QLoRA). Most of these need a GPU. **Gradient accumulation** can be tested right here: the mathematics says that summing the gradients of 4 micro-batches of 8, each loss divided by 4, equals the gradient of one batch of 32.

```python run
mdl = new_model(seed=0); mdl.eval()                                                 # eval mode: no dropout, so the two computations are comparable
x32, m32, y32 = make_batch("train", perm[:32])
mdl.zero_grad()
F.cross_entropy(mdl(input_ids=x32, attention_mask=m32).logits, y32).backward()
g_full = {n: p.grad.clone() for n, p in mdl.named_parameters() if p.grad is not None}
mdl.zero_grad()
for k in range(4):
    xs, ms, ys = make_batch("train", perm[8 * k:8 * k + 8])
    (F.cross_entropy(mdl(input_ids=xs, attention_mask=ms).logits, ys) / 4).backward()   # .backward() ADDS to .grad
worst_diff = max((g_full[n] - p.grad).abs().max().item() for n, p in mdl.named_parameters() if n in g_full)
print("gradient of 1 batch of 32 == accumulated gradient of 4 micro-batches of 8:", worst_diff < 1e-5, f"(max difference {worst_diff:.1e})")
print("note: the micro-batches are padded to different lengths than the big batch; the attention mask makes that irrelevant")
```
```text
gradient of 1 batch of 32 == accumulated gradient of 4 micro-batches of 8: True (max difference 1.8e-07)
note: the micro-batches are padded to different lengths than the big batch; the attention mask makes that irrelevant
```

The trap hidden in this identity: it holds for the loss as a **mean over examples**. If you accumulate a loss that is a *sum over tokens* (language modelling with different numbers of tokens per micro-batch), dividing by the number of micro-batches is not enough.

### 8.3 On your machine: the same fine-tuning in a GPU environment

*Not run here (needs a GPU). The recipe is what you have learned; only the device and the precision change.*

```python
args = TrainingArguments(output_dir="out", num_train_epochs=3, per_device_train_batch_size=16, gradient_accumulation_steps=2,
                         learning_rate=5e-5, bf16=True, eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
                         metric_for_best_model="accuracy", report_to="none", seed=0)
# Trainer(...) exactly as in section 4.4; device placement and mixed precision are handled for you
```

## 9. Project: a fine-tuned sentiment classifier

### 9.1 The brief

Build a small, honest, **end-to-end fine-tuning pipeline** in a module a colleague could run and trust:

1. **Data hygiene**: stratified, seeded training subset; duplicate check between training and evaluation data; labels and label names kept together.
2. **Model**: a pretrained body from the Hub (or from a local folder) with a new head, trained by `full` fine-tuning, `lora`, or `head`-only, selected by configuration.
3. **Training**: the recipe of section 4 (warm-up, linear decay, weight decay on matrices only, clipping), a fixed seed, **best-epoch selection on the validation set**.
4. **Evaluation**: accuracy, precision, recall, F1, confusion matrix, calibration error; a paired comparison with the baselines on the same test reviews.
5. **A deployable artefact**: a folder with the (merged) model, the tokeniser, the label names, the configuration, the metrics and the library versions, loadable into a `Classifier` that **validates its input**.
6. **Tests** that need **no internet and no pretrained download**: they build a tiny random "pretrained" model and tokeniser in a temporary folder and check the properties that matter.

### 9.2 The module

```python run
proj = pathlib.Path(tempfile.mkdtemp()) / "ftclf_project"; proj.mkdir()
(proj / "ftclf.py").write_text('''"""ftclf: fine-tune a pretrained transformer for text classification (Hugging Face + PyTorch)."""
import copy, dataclasses, json, math, platform, random
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
import transformers
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup


@dataclasses.dataclass
class Config:
    model_name: str = "distilbert/distilbert-base-uncased"      # a Hub name or a local folder
    method: str = "full"                                        # "full" | "lora" | "head"
    labels: tuple = ("negative", "positive")
    max_len: int = 64
    epochs: int = 2
    lr: float = 5e-5
    batch_size: int = 32
    warmup: float = 0.1
    weight_decay: float = 0.01
    clip: float = 1.0
    lora_r: int = 8
    lora_alpha: int = 16
    lora_targets: tuple = ("q_lin", "v_lin")
    seed: int = 0


def seed_everything(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


# ---------- data ----------
def stratified_subset(y, n, seed=0):
    """About n indices with the class proportions of y, reproducible, sorted."""
    y = np.asarray(y)
    rng = np.random.default_rng(seed)
    chosen = []
    for c in np.unique(y):
        idx = np.where(y == c)[0]
        k = min(len(idx), max(1, round(n * len(idx) / len(y))))
        chosen += rng.choice(idx, k, replace=False).tolist()
    return np.array(sorted(chosen))


def _norm(t):
    return " ".join(t.lower().split())


def count_overlap(train_texts, other_texts):
    """How many texts in `other_texts` also occur (after lower-casing and whitespace normalisation) in the training texts."""
    seen = {_norm(t) for t in train_texts}
    return sum(_norm(t) in seen for t in other_texts)


def encode(tokenizer, texts, max_len):
    return tokenizer(list(texts), truncation=True, max_length=max_len)["input_ids"]


def make_batch(ids, labels, idx, pad_id):
    seqs = [ids[i] for i in idx]
    L = max(map(len, seqs))
    x = torch.full((len(seqs), L), pad_id, dtype=torch.long)
    m = torch.zeros((len(seqs), L), dtype=torch.long)
    for j, s in enumerate(seqs):
        x[j, :len(s)] = torch.tensor(s); m[j, :len(s)] = 1
    y = None if labels is None else torch.tensor(np.asarray(labels)[list(idx)])
    return x, m, y


# ---------- model ----------
def _is_head(name):
    return "classifier" in name or "pooler" in name


def build_model(cfg):
    if cfg.method not in ("full", "lora", "head"):
        raise ValueError(f"unknown method {cfg.method!r}")
    seed_everything(cfg.seed)                                              # the new head's initial weights depend on the seed
    model = AutoModelForSequenceClassification.from_pretrained(cfg.model_name, num_labels=len(cfg.labels))
    if cfg.method == "head":
        for n, p in model.named_parameters():
            p.requires_grad = _is_head(n)
    elif cfg.method == "lora":
        from peft import LoraConfig, TaskType, get_peft_model
        model = get_peft_model(model, LoraConfig(r=cfg.lora_r, lora_alpha=cfg.lora_alpha, target_modules=list(cfg.lora_targets),
                                                 lora_dropout=0.1, task_type=TaskType.SEQ_CLS))
    return model


def n_trainable(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


@torch.no_grad()
def predict_proba(model, ids, pad_id, bs=128):
    model.eval()
    out = []
    for i in range(0, len(ids), bs):
        x, m, _ = make_batch(ids, None, range(i, min(i + bs, len(ids))), pad_id)
        out.append(F.softmax(model(input_ids=x, attention_mask=m).logits, dim=1))
    return torch.cat(out).numpy()


def train(model, tr_ids, tr_y, va_ids, va_y, cfg, pad_id):
    """Fine-tune; after each epoch evaluate on the validation set; return (history, best_epoch). Restores the best epoch's trainable weights."""
    seed_everything(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    named = [(n, p) for n, p in model.named_parameters() if p.requires_grad]
    opt = torch.optim.AdamW([{"params": [p for _, p in named if p.ndim >= 2], "weight_decay": cfg.weight_decay},
                             {"params": [p for _, p in named if p.ndim < 2], "weight_decay": 0.0}], lr=cfg.lr)
    steps = cfg.epochs * math.ceil(len(tr_ids) / cfg.batch_size)
    sched = get_linear_schedule_with_warmup(opt, int(cfg.warmup * steps), steps)
    history, best, best_state = [], -1.0, None
    for ep in range(cfg.epochs):
        model.train()
        order = rng.permutation(len(tr_ids))
        total = 0.0
        for i in range(0, len(order), cfg.batch_size):
            x, m, y = make_batch(tr_ids, tr_y, order[i:i + cfg.batch_size], pad_id)
            loss = F.cross_entropy(model(input_ids=x, attention_mask=m).logits, y)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_([p for _, p in named], cfg.clip)
            opt.step(); sched.step()
            total += loss.item() * len(y)
        acc = float((predict_proba(model, va_ids, pad_id).argmax(1) == np.asarray(va_y)).mean())
        history.append({"epoch": ep + 1, "train_loss": total / len(order), "val_acc": acc})
        if acc > best:
            best, best_state = acc, {n: p.detach().clone() for n, p in named}
    with torch.no_grad():
        for n, p in named:
            p.copy_(best_state[n])
    return history, int(np.argmax([h["val_acc"] for h in history])) + 1


# ---------- evaluation ----------
def report(y, probs, labels, bins=5):
    y, probs = np.asarray(y), np.asarray(probs)
    pred = probs.argmax(1)
    conf = probs.max(1)
    cm = np.zeros((len(labels), len(labels)), dtype=int)
    for t, p in zip(y, pred):
        cm[t, p] += 1
    per = {}
    for c, name in enumerate(labels):
        tp = cm[c, c]; prec = tp / max(1, cm[:, c].sum()); rec = tp / max(1, cm[c].sum())
        per[name] = {"precision": float(prec), "recall": float(rec), "f1": float(2 * prec * rec / max(1e-12, prec + rec))}
    edges = np.linspace(1 / len(labels), 1.0, bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (conf >= lo) & ((conf < hi) | (hi == 1.0))
        if sel.any():
            ece += sel.mean() * abs(conf[sel].mean() - (pred[sel] == y[sel]).mean())
    return {"accuracy": float((pred == y).mean()), "n": int(len(y)), "per_class": per, "confusion": cm.tolist(), "ece": float(ece)}


# ---------- the artefact ----------
def save_artifact(directory, model, tokenizer, cfg, metrics):
    d = Path(directory); d.mkdir(parents=True, exist_ok=True)
    model = copy.deepcopy(model)
    if hasattr(model, "merge_and_unload"):
        model = model.merge_and_unload()                                    # a plain model: no adapter code needed to serve it
    model.save_pretrained(d); tokenizer.save_pretrained(d)
    meta = {"config": dataclasses.asdict(cfg), "metrics": metrics,
            "versions": {"python": platform.python_version(), "torch": torch.__version__, "transformers": transformers.__version__}}
    (d / "ftclf.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")


class Classifier:
    """Loads an artefact folder and classifies texts. Validates its input."""
    MAX_CHARS = 5000

    def __init__(self, directory):
        d = Path(directory)
        meta = json.loads((d / "ftclf.json").read_text(encoding="utf-8"))
        self.labels, self.max_len = list(meta["config"]["labels"]), meta["config"]["max_len"]
        self.tokenizer = AutoTokenizer.from_pretrained(d)
        self.model = AutoModelForSequenceClassification.from_pretrained(d)
        self.model.eval()

    def predict(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        if not isinstance(texts, (list, tuple)) or not texts:
            raise ValueError("texts must be a string or a non-empty list of strings")
        for t in texts:
            if not isinstance(t, str):
                raise ValueError(f"every text must be a string, got {type(t).__name__}")
            if not t.strip():
                raise ValueError("empty text")
            if len(t) > self.MAX_CHARS:
                raise ValueError(f"text of {len(t)} characters exceeds the limit of {self.MAX_CHARS}")
        ids = encode(self.tokenizer, texts, self.max_len)
        probs = predict_proba(self.model, ids, self.tokenizer.pad_token_id)
        full_len = [len(x) for x in self.tokenizer(list(texts))["input_ids"]]
        return [{"label": self.labels[int(p.argmax())], "confidence": float(p.max()), "probs": p.round(4).tolist(), "truncated": n > self.max_len}
                for p, n in zip(probs, full_len)]
''', encoding="utf-8")
print("wrote", (proj / "ftclf.py").name, "|", len((proj / "ftclf.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
wrote ftclf.py | 197 lines
```

### 9.3 Data first, then the baselines

```python run
sys.path.insert(0, str(proj))
import importlib, ftclf
importlib.reload(ftclf)

N_TRAIN = 1000
tr_idx = ftclf.stratified_subset(lab["train"], N_TRAIN, seed=0)
tr_txt, tr_y = [txt["train"][i] for i in tr_idx], lab["train"][tr_idx]
print(f"training subset: {len(tr_idx)} reviews, class counts {np.bincount(tr_y).tolist()} (the full file is {len(txt['train']):,} reviews, sorted by label)")
again = ftclf.stratified_subset(lab["train"], N_TRAIN, seed=0)
print("subset is reproducible:", bool((again == tr_idx).all()), "| different seed gives a different subset:", not bool((ftclf.stratified_subset(lab['train'], N_TRAIN, seed=1) == tr_idx).all()))
print("overlap with validation:", ftclf.count_overlap(tr_txt, txt["validation"]), "| with test:", ftclf.count_overlap(tr_txt, txt["test"]))

# baselines on the SAME 1,000 reviews
v2 = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True); clf2 = LogisticRegression(C=10, max_iter=1000).fit(v2.fit_transform(tr_txt), tr_y)
print(f"TF-IDF + logistic regression on these {N_TRAIN} reviews: validation accuracy {clf2.score(v2.transform(txt['validation']), lab['validation']):.4f}")

cfg_p = ftclf.Config(model_name=DISTIL, method="full", epochs=2, lr=5e-5, seed=0)
pad_id = tok.pad_token_id
enc_tr, enc_va, enc_te = (ftclf.encode(tok, t, cfg_p.max_len) for t in (tr_txt, txt["validation"], txt["test"]))
model_0 = ftclf.build_model(cfg_p)                                           # the STARTING POINT: pretrained body, random head
p0 = ftclf.predict_proba(model_0, enc_va, pad_id)
print(f"base model (pretrained body + random head), validation accuracy {(p0.argmax(1) == lab['validation']).mean():.4f}")
```
```text
training subset: 1000 reviews, class counts [500, 500] (the full file is 8,530 reviews, sorted by label)
subset is reproducible: True | different seed gives a different subset: True
overlap with validation: 0 | with test: 0
TF-IDF + logistic regression on these 1000 reviews: validation accuracy 0.6792
base model (pretrained body + random head), validation accuracy 0.5028
```

### 9.4 Fine-tune

```python run
t0 = time.time()
model_p = ftclf.build_model(cfg_p)
print(f"trainable parameters: {ftclf.n_trainable(model_p):,}")
history, best_ep = ftclf.train(model_p, enc_tr, tr_y, enc_va, lab["validation"], cfg_p, pad_id)
print(pd.DataFrame(history).round(4).to_string(index=False))
print(f"best epoch by validation accuracy: {best_ep} | {time.time() - t0:.0f}s")
```
```text
trainable parameters: 66,955,010
 epoch  train_loss  val_acc
     1      0.6088   0.8011
     2      0.3362   0.8058
best epoch by validation accuracy: 2 | 419s
```

### 9.5 The held-out evaluation: the claim, with evidence

The test set is opened **once**, now that the configuration is fixed. The starting point (`model_0`), the classical baseline trained on the same 1,000 reviews, and the fine-tuned model are compared on the same 1,066 reviews, with the paired tools of section 7.

```python run
probs_te = ftclf.predict_proba(model_p, enc_te, pad_id)
rep = ftclf.report(lab["test"], probs_te, cfg_p.labels)
print(f"TEST accuracy {rep['accuracy']:.4f} on {rep['n']} reviews | expected calibration error {rep['ece']:.4f}")
print("confusion (rows true negative/positive, columns predicted):", rep["confusion"])
print("per class:", {k: {m: round(v, 3) for m, v in d.items()} for k, d in rep["per_class"].items()})

p_base = ftclf.predict_proba(model_0, enc_te, pad_id).argmax(1)
p_tfidf = clf2.predict(v2.transform(txt["test"]))
p_ft = probs_te.argmax(1)
rows = []
for name, other in (("the base model (random head)", p_base), ("TF-IDF + logistic regression (same 1,000 reviews)", p_tfidf)):
    r = paired(p_ft, other, lab["test"])
    rows.append([name, round((other == lab["test"]).mean(), 4), f"{r['diff']:+.4f}", f"[{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}]", f"{r['only_A']} / {r['only_B']}", f"{r['p_value']:.1e}"])
print()
print(pd.DataFrame(rows, columns=["fine-tuned model compared with", "its accuracy", "difference", "95% bootstrap interval", "only fine-tuned right / only other right", "McNemar p"]).to_string(index=False))
```
```text
TEST accuracy 0.8265 on 1066 reviews | expected calibration error 0.0324
confusion (rows true negative/positive, columns predicted): [[434, 99], [86, 447]]
per class: {'negative': {'precision': 0.835, 'recall': 0.814, 'f1': 0.824}, 'positive': {'precision': 0.819, 'recall': 0.839, 'f1': 0.829}}

                   fine-tuned model compared with  its accuracy difference 95% bootstrap interval only fine-tuned right / only other right McNemar p
                     the base model (random head)        0.5235    +0.3030       [+0.265, +0.341]                                 416 / 93   9.0e-50
TF-IDF + logistic regression (same 1,000 reviews)        0.6717    +0.1548       [+0.122, +0.189]                                 249 / 84   4.1e-20
```

That table is the project's result. The sentence a reader is entitled to is the one the data support: **"the fine-tuned model is better than the base model and than a TF-IDF classifier trained on the same 1,000 reviews, on 1,066 held-out reviews, by the margins shown, with the intervals shown."** It does not say the method is better in general (one seed, one dataset), nor that the model is calibrated (see the ECE).

### 9.6 Package it and use it

```python run
art = proj / "sentiment_model"
ftclf.save_artifact(art, model_p, tok, cfg_p, rep)
print("files:", sorted(f.name for f in art.iterdir()), f"| {sum(f.stat().st_size for f in art.iterdir()) / 1e6:.0f} MB")
meta = json.loads((art / "ftclf.json").read_text(encoding="utf-8"))
print("recorded versions:", meta["versions"], "| recorded test accuracy:", round(meta["metrics"]["accuracy"], 4))

clf_ready = ftclf.Classifier(art)
demo = ["a gorgeous , moving film that earns every tear", "dull and badly acted , i wanted to leave", "it is not good , and it is not bad either"]
for t, r in zip(demo, clf_ready.predict(demo)): print(f"  {r['label']:<8} {r['confidence']:.2f}  {t}")
print("predictions equal the in-memory model's:", bool(np.allclose(np.array([r["probs"] for r in clf_ready.predict(txt["test"][:64])]), ftclf.predict_proba(model_p, enc_te[:64], pad_id), atol=1e-3)))
for bad, why in [("", "empty text"), (["fine", 3], "non-string item"), ([], "empty list"), ("x" * 6000, "too long")]:
    try: clf_ready.predict(bad)
    except ValueError as e: print(f"rejected ({why}):", str(e)[:70])
print("a very long review is flagged as truncated:", clf_ready.predict("good " * 100)[0]["truncated"])
```
```text
files: ['config.json', 'ftclf.json', 'model.safetensors', 'tokenizer.json', 'tokenizer_config.json'] | 269 MB
recorded versions: {'python': '3.14.4', 'torch': '2.15.0+cpu', 'transformers': '5.22.2'} | recorded test accuracy: 0.8265
  positive 0.95  a gorgeous , moving film that earns every tear
  negative 0.92  dull and badly acted , i wanted to leave
  negative 0.90  it is not good , and it is not bad either
predictions equal the in-memory model's: True
rejected (empty text): empty text
rejected (non-string item): every text must be a string, got int
rejected (empty list): texts must be a string or a non-empty list of strings
rejected (too long): text of 6000 characters exceeds the limit of 5000
a very long review is flagged as truncated: True
```

### 9.7 Tests that need no internet

The tests build a tiny random BERT and a 20-word tokeniser in a temporary folder and use that folder *as if* it were a downloaded pretrained model. Everything the module does with `from_pretrained` works the same on a folder and on a Hub name, which is exactly what makes the tests fast and offline.

```python run
(proj / "test_ftclf.py").write_text('''import json
import numpy as np
import pytest
import torch
from transformers import BertConfig, BertModel, BertTokenizer
import ftclf

WORDS = ["great", "wonderful", "fine", "love", "good", "bad", "awful", "boring", "hate", "poor", "movie", "film", "the", "a", "is", "was", "not", "very"]
POS, NEG = ["great", "wonderful", "love", "good"], ["bad", "awful", "boring", "hate"]


def make_data(n, seed=0):
    rng = np.random.default_rng(seed)
    texts, y = [], []
    for i in range(n):
        label = i % 2
        w = rng.choice(POS if label else NEG)
        texts.append(f"the {rng.choice(['movie', 'film'])} is {w}"); y.append(label)
    return texts, np.array(y)


@pytest.fixture(scope="session")
def pre(tmp_path_factory):
    d = tmp_path_factory.mktemp("pretrained")
    vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"] + WORDS
    tok = BertTokenizer(vocab={w: i for i, w in enumerate(vocab)}, do_lower_case=True)
    torch.manual_seed(0)
    BertModel(BertConfig(vocab_size=len(vocab), hidden_size=32, num_hidden_layers=2, num_attention_heads=2, intermediate_size=64, max_position_embeddings=32)).save_pretrained(d)
    tok.save_pretrained(d)
    return str(d), tok


def cfg_for(pre, **kw):
    base = dict(model_name=pre[0], max_len=16, epochs=8, lr=3e-3, batch_size=8, lora_targets=("query", "value"), seed=1)
    base.update(kw)
    return ftclf.Config(**base)


def data(pre, cfg, n=32):
    texts, y = make_data(n)
    return ftclf.encode(pre[1], texts, cfg.max_len), y, texts


def test_batch_padding_and_mask(pre):
    ids = [[2, 5, 3], [2, 5, 6, 7, 3]]
    x, m, _ = ftclf.make_batch(ids, None, [0, 1], pad_id=0)
    assert x.shape == (2, 5) and m.tolist() == [[1, 1, 1, 0, 0], [1, 1, 1, 1, 1]], "padding must be on the right with mask 0"


def test_padding_does_not_change_logits(pre):
    cfg = cfg_for(pre)
    model = ftclf.build_model(cfg).eval()
    a, _, _ = ftclf.make_batch([[2, 5, 6, 3]], None, [0], 0)
    ids = [[2, 5, 6, 3], [2, 5, 6, 7, 8, 9, 10, 3]]
    x, m, _ = ftclf.make_batch(ids, None, [0, 1], 0)
    with torch.no_grad():
        alone, padded = model(input_ids=a).logits[0], model(input_ids=x, attention_mask=m).logits[0]
    assert torch.allclose(alone, padded, atol=1e-5), "padded + masked must equal the unpadded answer: the attention mask is wrong or missing"


def test_head_has_one_output_per_label(pre):
    model = ftclf.build_model(cfg_for(pre, labels=("a", "b", "c")))
    x, m, _ = ftclf.make_batch([[2, 5, 3]], None, [0], 0)
    assert model(input_ids=x, attention_mask=m).logits.shape == (1, 3), "the new head must have len(labels) outputs"


def test_split_helpers():
    y = np.array([0] * 80 + [1] * 20)
    idx = ftclf.stratified_subset(y, 50, seed=3)
    assert abs(y[idx].mean() - 0.2) < 0.05 and (idx == ftclf.stratified_subset(y, 50, seed=3)).all(), "subset must keep proportions and be reproducible"
    assert ftclf.count_overlap(["Hello  World", "x"], ["hello world", "y"]) == 1, "duplicates must be found after lower-casing and whitespace normalisation"


def test_can_overfit_and_learn(pre):
    cfg = cfg_for(pre)
    ids, y, _ = data(pre, cfg)
    model = ftclf.build_model(cfg)
    hist, best = ftclf.train(model, ids, y, ids, y, cfg, pre[1].pad_token_id)
    acc = (ftclf.predict_proba(model, ids, pre[1].pad_token_id).argmax(1) == y).mean()
    assert acc == 1.0, f"accuracy {acc:.2f} on a trivially learnable set after {cfg.epochs} epochs: check labels, mask, learning rate, zero_grad"
    assert hist[-1]["train_loss"] < hist[0]["train_loss"], "loss must fall"


def test_head_only_freezes_the_body(pre):
    cfg = cfg_for(pre, method="head", epochs=2)
    ids, y, _ = data(pre, cfg)
    model = ftclf.build_model(cfg)
    before = {n: p.detach().clone() for n, p in model.named_parameters()}
    ftclf.train(model, ids, y, ids, y, cfg, pre[1].pad_token_id)
    for n, p in model.named_parameters():
        if "classifier" in n or "pooler" in n:
            continue
        assert torch.equal(before[n], p), f"{n} changed although the body should be frozen"
    assert not torch.equal(before["classifier.weight"], model.classifier.weight), "the head must have been trained"


def test_lora_parameter_count_and_frozen_base(pre):
    cfg = cfg_for(pre, method="lora", lora_r=4, lora_alpha=8, epochs=2)
    model = ftclf.build_model(cfg)
    expected = 2 * 2 * 4 * (32 + 32) + (32 * 2 + 2)                                # layers x (query, value) x r x (d + k) + classifier
    assert ftclf.n_trainable(model) == expected, f"{ftclf.n_trainable(model)} trainable parameters, expected {expected}"
    ids, y, _ = data(pre, cfg)
    base_w = model.base_model.model.bert.encoder.layer[0].attention.self.query.base_layer.weight.detach().clone()
    ftclf.train(model, ids, y, ids, y, cfg, pre[1].pad_token_id)
    assert torch.equal(base_w, model.base_model.model.bert.encoder.layer[0].attention.self.query.base_layer.weight), "the base weights must not change under LoRA"


def test_training_is_deterministic(pre):
    cfg = cfg_for(pre, epochs=2)
    ids, y, _ = data(pre, cfg)
    ms = []
    for _ in range(2):
        m = ftclf.build_model(cfg); ftclf.train(m, ids, y, ids, y, cfg, pre[1].pad_token_id); ms.append(m)
    for (n, a), (_, b) in zip(ms[0].state_dict().items(), ms[1].state_dict().items()):
        assert torch.equal(a, b), f"{n} differs between two runs with the same seed"


def test_report_numbers():
    probs = np.array([[0.9, 0.1], [0.2, 0.8], [0.6, 0.4], [0.3, 0.7]])
    r = ftclf.report([0, 1, 1, 1], probs, ("n", "p"))
    assert r["accuracy"] == 0.75 and r["confusion"] == [[1, 0], [1, 2]]
    assert abs(r["per_class"]["p"]["recall"] - 2 / 3) < 1e-9 and r["per_class"]["p"]["precision"] == 1.0


@pytest.mark.parametrize("method", ["full", "lora"])
def test_artifact_roundtrip_and_validation(pre, tmp_path, method):
    cfg = cfg_for(pre, method=method, epochs=2)
    ids, y, texts = data(pre, cfg)
    model = ftclf.build_model(cfg)
    ftclf.train(model, ids, y, ids, y, cfg, pre[1].pad_token_id)
    ftclf.save_artifact(tmp_path / "art", model, pre[1], cfg, {"accuracy": 1.0})
    clf = ftclf.Classifier(tmp_path / "art")
    want = ftclf.predict_proba(model, ids[:6], pre[1].pad_token_id)
    got = np.array([r["probs"] for r in clf.predict(texts[:6])])
    assert np.allclose(want, got, atol=1e-3), "the loaded artefact must give the same probabilities as the trained model (merged LoRA included)"
    assert json.loads((tmp_path / "art" / "ftclf.json").read_text(encoding="utf-8"))["config"]["method"] == method
    for bad in ["", "   ", [], ["ok", 3], "x" * 6000, 5]:
        with pytest.raises(ValueError):
            clf.predict(bad)
    assert clf.predict("good " * 30)[0]["truncated"] is True
''', encoding="utf-8")
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", "test_ftclf.py"], cwd=proj, capture_output=True, text=True, env={**os.environ, "HF_HUB_OFFLINE": "1"}, encoding="utf-8")
print((r.stdout + r.stderr).strip()[-1500:])
```
```text
...........                                                              [100%]
11 passed in 8.58s
```

Each test guards a failure mode named earlier in the chapter: forgotten attention masks, a head with the wrong number of outputs, a "frozen" body that moves, a LoRA that touches the base weights or has the wrong parameter count, a run that cannot be reproduced, a merged adapter that disagrees with the unmerged one, and a service that accepts an empty string.

### 9.8 Extensions

1. **Seeds**: train with seeds 0 to 4 and report the mean and standard deviation of the test accuracy; put a confidence interval on the improvement over TF-IDF that includes training randomness (a paired *t*-test over seeds, or a bootstrap over seeds).
2. **LoRA at scale**: run `method="lora"` for DistilBERT with `lr=1e-3` and compare accuracy, trainable parameters and artefact size with the full run (section 6.6).
3. **More data**: use all 8,530 training reviews and 3 epochs. How much of the gap to TF-IDF is *data* and how much is *pretraining*?
4. **A different task**: swap the dataset for `stanfordnlp/imdb` (long reviews, `max_len=256`) or a 3-class dataset (`labels=("negative", "neutral", "positive")`). What in the module needs to change? (Hint: nothing in the code, only the configuration; that is the point of the design.)
5. **Error-driven iteration**: take the five most confident test mistakes of section 7.4, decide whether they are label noise, and write what you would collect next.

## 10. Common traps

1. **Using a model with the wrong tokeniser**, or a different `max_length` or lower-casing at serving time than at training time (1.2).
2. **Padding without the attention mask** (1.2), or averaging over padding.
3. **Training on a sorted file** or an unshuffled subset: one class only, near-zero loss, 50% accuracy (1.3, 5.3).
4. **Not looking at a classical baseline** at the same training size (2.2).
5. **Reporting a single run** as the result: seed noise is as large as many "improvements" (5.2).
6. **A learning rate copied from another model**: too high collapses the model to the majority class (loss `ln 2`), too low leaves it untrained (5.1). LoRA wants a much higher rate than full fine-tuning (6.3).
7. **Using the last epoch** instead of the best validation epoch, then reporting the validation score as if it were the test score (5.4).
8. **Believing `requires_grad=False` is a free lunch**: frozen parts that are also in train mode (batch norm, dropout) behave differently (ml.03), and a head trained at the full-model learning rate under-trains (5.5).
9. **Comparing two models by two intervals** instead of a paired test on the same examples (7.2); calling a non-significant difference "equal" (7.2).
10. **Trusting confidence scores unchecked**: fine-tuned transformers are often over-confident; measure calibration and fit a temperature only if it helps (7.3, where it did not).
11. **Only looking at average accuracy**: slices, the worst mistakes and behavioural tests find the blind spots (7.4, 7.5).
12. **Contamination and duplicates** between training data, evaluation data, and the pretraining corpus (2.1, 7.6).
13. **Accumulating gradients with a loss that is a sum**, not a mean, over a variable number of items (8.2).
14. **An unreproducible environment**: library APIs in this area change monthly. Record versions with the artefact (9.6) and pin them.

## 11. Summary

- **Fine-tuning** starts from a pretrained body, adds a new randomly initialised head, and trains on your labelled data with a small learning rate. The pretrained body is not a classifier: with a random head it is at chance (3.1).
- The **Hugging Face stack**: `AutoConfig / AutoTokenizer / AutoModel…` load from a Hub name or a local folder; the tokeniser must match the model; always pass the **attention mask**; `datasets` gives memory-mapped, cached, batched `map`; shuffle before taking a subset.
- **Before the model**: look at the data, check duplicates and sizes, and train a **classical baseline** at several training sizes (TF-IDF + logistic regression here). A pretrained model's advantage is largest where labelled data are scarcest.
- **Frozen features** plus a linear model are a cheap first step; fine-tuning lets the network itself specialise.
- The **recipe**: learning rate `2e-5` to `1e-4`, 2 to 4 epochs, warm-up then linear decay, weight decay on matrices only, gradient clipping, batch 16 to 32, best-epoch selection on validation. `Trainer` packages this; knowing the loop lets you debug it.
- **Failure modes** you can now recognise: learning rate too high (stuck at `ln 2`) or too low, seed variance, sorted data, over-fitting small data, wrong learning rate for a frozen-body head.
- **LoRA**: freeze `W`, learn `ΔW = (α/r)·B·A` with `B` initialised to zero, `r·(d+k)` parameters per matrix instead of `d·k`. It matches full fine-tuning here with about 1% of the trainable parameters, saves memory and storage (a 2 MB adapter on a shared base), merges away for inference, and wants a higher learning rate. QLoRA adds a 4-bit base model (GPU).
- **Evaluation** turns a number into a claim: the held-out set touched once; accuracy with an interval; a **paired test** (McNemar, bootstrap) against baselines on the same examples; seeds measured; **calibration** (ECE, and temperature scaling when it helps); error analysis and slices; **behavioural tests**; checks for overlap and contamination.
- A finished project has a hygienic split, a documented configuration, a result stated with its uncertainty, an artefact that carries its tokeniser, labels, metrics and library versions, a predictor that validates input, and tests that run offline on a tiny model.

**Self-check (answer without looking back):**

1. Why is a pretrained body with a random head at chance accuracy, and what exactly does "fine-tuning beats the base model" compare?
2. A fine-tuned model scores 0.84 on 1,066 test reviews and a TF-IDF model 0.80. What would you compute before calling it an improvement?
3. A `Linear(768, 768)` is adapted with LoRA of rank 8. How many trainable parameters does the adapter add, and why is `B` initialised to zero?
4. Training loss is stuck at 0.693 on a two-class problem. Name three causes.
5. Why does LoRA usually use a larger learning rate than full fine-tuning?
6. What is the problem with picking the best epoch on the validation set and then reporting that validation accuracy?

<details><summary>Answer</summary>

1. The head's weights are random, so its output carries no information about sentiment; the pretrained body only provides features. The claim compares the *adapted* model with that unadapted starting point (and, to be meaningful, also with a classical baseline), on held-out data.
2. A paired test on the same examples (McNemar) and a bootstrap interval for the difference, and the run-to-run variation over several seeds. A 4-point gap on ~1,000 examples is near the edge of what the sample can resolve.
3. `r·(d + k) = 8 × (768 + 768) = 12,288` parameters (against 589,824 in the matrix). `B = 0` makes `ΔW = 0` at the start, so the adapted model begins identical to the pretrained one and training departs from a good point.
4. Learning rate too high (collapse to the majority class); sorted or single-class training data; labels shuffled or misaligned with the texts (also: a frozen body with a head that is not training, or a missing `zero_grad` / forgotten optimiser step).
5. Its new parameters start at (or near) zero, and the frozen base cannot be damaged by large steps, so it needs bigger updates to move far enough; a rate that is right for destabilising pretrained weights is too small.
6. The selection used the validation labels, so the validation score is optimistically biased (you picked its maximum). Report the **test** accuracy of the selected checkpoint, computed once.

</details>
