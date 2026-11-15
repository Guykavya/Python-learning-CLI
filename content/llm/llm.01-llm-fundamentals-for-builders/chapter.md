# Chapter 1 (LLM): LLM Fundamentals for Builders

You are about to build software that *calls* a large language model (LLM): a support-reply drafter, a document summariser, a code helper. Before you write the first call, you need a clear picture of what the thing is, what it costs, how long it takes and where it fails. Teams that skip this build a feature, get the first bill or the first angry user, and then discover that the idea was never affordable, or never fast enough, or relied on something models are bad at.

This chapter gives you that picture, and one habit that goes with it: **estimate before you build**. The syllabus outcome is *estimate the cost and latency of a feature before building it*, and the project is a **token and cost calculator for prompts**.

You will learn, in this order:

1. What an LLM is *to a program*: a stateless function from a list of messages to text, charged by the token.
2. **Tokens**: what they are, built by hand (a tiny byte-pair-encoding tokenizer), and why the same sentence costs different amounts in English, code, numbers and Hindi.
3. **Context windows**: why long conversations get expensive, and three ways to keep them in check.
4. **Sampling settings**: temperature, top-k and top-p, built from scratch on a toy language model you can inspect.
5. **Cost and latency**: a back-of-envelope method you can do on paper in five minutes.
6. **Choosing a model**: size tiers, routing and a break-even calculation.
7. **What models are bad at**: hallucination, arithmetic, counting, stale knowledge, and the cheap ways to defend against each.

Prerequisites: swe.02 (HTTP and JSON, because every provider is an HTTP API) and core.09 (type hints and dataclasses, which we use for the client).

> **How this chapter is built, and what it does NOT contain.** *No real LLM is called anywhere in this chapter or its tests.* Everything runs offline, for free, with a **`FakeLLM`** class that has the same shape as a real provider client (messages in; text, token usage and a stop reason out) but replies from a script. This is deliberate: your course must keep working with no internet, no key and no subscription, and tests must give the same answer every time.
>
> That has one honest consequence. **Statements about how real models behave** (they hallucinate, they miscount letters, their quality depends on size) are general knowledge from the literature and from everyday use, and are marked *(general knowledge)*. They are **not measured here**. Everything else, every number printed under a code block, is a real run: the tokenisers, the sampling experiments, the cost arithmetic and the project. **Prices and speeds in the examples are illustrative placeholders, not any provider's real figures.** The calculator reads them from a file you edit, so you put today's real prices there.
>
> Variations that would only repeat a lesson are **question → worked answer** boxes. Sections carry optional **Visualise it** prompts you can paste into any AI chat; the course never depends on them. When you are ready to try a real provider, section 1.4 shows how little code changes.

```python run
import sys, platform, math, re, json, time, random, textwrap, importlib, pathlib, tempfile, subprocess, statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
print("python  ", sys.version.split()[0], "|", platform.system())
ws = pathlib.Path(tempfile.mkdtemp(prefix="llm01_ws_"))        # every file this chapter creates lives here
print("workspace:", ws.name)
```
```text
python   3.14.4 | Linux
workspace: llm01_ws_c2lq7zw7
```

## Table of contents

1. [An LLM as a function: messages in, text and a bill out](#1-an-llm-as-a-function-messages-in-text-and-a-bill-out)
2. [Tokens](#2-tokens)
3. [Context windows and conversations](#3-context-windows-and-conversations)
4. [Sampling settings](#4-sampling-settings)
5. [Estimating cost and latency before you build](#5-estimating-cost-and-latency-before-you-build)
6. [Choosing a model](#6-choosing-a-model)
7. [What models are bad at](#7-what-models-are-bad-at)
8. [Project: token and cost calculator for prompts](#8-project-token-and-cost-calculator-for-prompts)
9. [Common traps](#9-common-traps)
10. [Summary](#10-summary)

## 1. An LLM as a function: messages in, text and a bill out

### 1.1 What it is, for a program

A language model is trained on huge amounts of text to do one thing: given the text so far, give a **probability for every possible next piece of text** (a *token*, section 2). Generating a reply is a loop: pick a next token from those probabilities (section 4), append it, ask again, until the model emits a stop signal or a length limit is hit. *(general knowledge)*

Everything a builder needs follows from that loop:

- **It is a function, and a stateless one.** Each call carries the whole conversation. The model remembers nothing between calls; if you want it to "remember", **you** send the history again, and **you** pay for it again (section 3).
- **Output is sampled, not computed.** The same input can produce different outputs (section 4). Plan for variation.
- **It continues text plausibly; it does not look facts up.** Fluent and true are different properties (section 7).
- **You are charged by the token, input and output separately, and the output is the slow part.** Each output token needs one trip around the loop (section 5).

### 1.2 The shape of a call

Every major provider uses the same ideas with different field names:

| Part | What it is |
|---|---|
| `model` | which model (a name string chosen from the provider's list) |
| `system` | optional instructions that frame the whole conversation ("You are a polite support agent.") |
| `messages` | a list of `{"role": "user" \| "assistant", "content": "..."}` in order |
| `max_tokens` | the longest reply you will accept (a **cap**, and a cost control) |
| `temperature` (and friends) | how random the sampling is |
| **response**: `text`, `usage` (input and output token counts), `stop_reason` | what you get back, and what you are billed for |

`stop_reason` matters more than beginners expect. `"end_turn"` means the model finished by itself. `"max_tokens"` means **your cap cut the reply off mid-sentence**: a truncated answer that looks fine until a JSON parser chokes on it. Always check it.

### 1.3 A stand-in with the same shape: `FakeLLM`

We build the fake client now and use it all chapter. It counts tokens (with a rough rule, replaced by a better counter in section 2), enforces a **context window** (raising an error like a real API when the input is too long), honours `max_tokens` (truncating and reporting `"max_tokens"`), and reports a **simulated latency** from two knobs: time to the first token and output tokens per second. It can also fail on purpose, which later modules use to teach retries.

```python run
class ContextTooLong(Exception):
    """The input does not fit in the model's context window (real APIs answer HTTP 400)."""

class RateLimited(Exception):
    """Too many requests (real APIs answer HTTP 429). Used from llm.02 on to teach retries."""

def estimate_tokens(text):
    """Rule of thumb for English: about 4 characters per token. Replaced by a better counter in section 2."""
    return math.ceil(len(text) / 4) if text else 0

FRAMING = 4          # extra tokens each message costs for roles and separators (illustrative)

def input_tokens(messages, system=None, counter=estimate_tokens):
    total = sum(counter(m["content"]) + FRAMING for m in messages)
    return total + (counter(system) + FRAMING if system else 0)

@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int

@dataclass(frozen=True)
class Reply:
    text: str
    usage: Usage
    stop_reason: str                 # "end_turn" or "max_tokens"
    latency_s: float                 # SIMULATED, from the model's speed settings

class FakeLLM:
    """Same shape as a provider client. Replies come from a script (a list that cycles, or a function)."""
    def __init__(self, replies=("OK.",), *, context_window=8000, ttft_s=0.4, tokens_per_s=60.0,
                 counter=estimate_tokens, fail_first=()):
        self.replies, self.context_window = replies, context_window
        self.ttft_s, self.tokens_per_s, self.counter = ttft_s, tokens_per_s, counter
        self.fail_first = list(fail_first)       # exceptions to raise on the first calls, then work
        self.calls = []                          # every call is recorded, so tests can inspect them
        self._n = 0

    def complete(self, messages, *, system=None, max_tokens=256, temperature=1.0):
        if self.fail_first:
            raise self.fail_first.pop(0)
        n_in = input_tokens(messages, system, self.counter)
        if n_in > self.context_window:
            raise ContextTooLong(f"input is {n_in} tokens but the context window is {self.context_window}")
        text = self.replies(messages) if callable(self.replies) else self.replies[self._n % len(self.replies)]
        self._n += 1
        stop = "end_turn"
        if self.counter(text) > max_tokens:                   # the cap cuts the reply off
            text, stop = text[: max_tokens * 4], "max_tokens"
        n_out = self.counter(text)
        reply = Reply(text, Usage(n_in, n_out), stop, self.ttft_s + n_out / self.tokens_per_s)
        self.calls.append(reply)
        return reply

llm = FakeLLM(replies=["A token is a small piece of text, often a word or part of a word, that a model reads and writes."])
r = llm.complete([{"role": "user", "content": "In one sentence, what is a token?"}], max_tokens=100)
print("text       :", r.text)
print("usage      :", r.usage)
print("stop_reason:", r.stop_reason, "| simulated latency: %.2f s" % r.latency_s)

cut = llm.complete([{"role": "user", "content": "Tell me about tokens."}], max_tokens=5)
print("\nwith max_tokens=5  ->", repr(cut.text), "| stop_reason:", cut.stop_reason)
try:
    FakeLLM(context_window=50).complete([{"role": "user", "content": "x" * 400}])
except ContextTooLong as e:
    print("too long ->", e)
```
```text
text       : A token is a small piece of text, often a word or part of a word, that a model reads and writes.
usage      : Usage(input_tokens=13, output_tokens=24)
stop_reason: end_turn | simulated latency: 0.80 s

with max_tokens=5  -> 'A token is a small p' | stop_reason: max_tokens
too long -> input is 104 tokens but the context window is 50
```

Look at the cut-off reply: five tokens of a sentence, and `stop_reason` is the **only** signal that it is incomplete. Build the habit now: *a reply is not finished unless `stop_reason == "end_turn"`*.

### 1.4 Moving to a real provider later

A real client is a thin layer with the same shape: an HTTP POST (swe.02) with the model name, the messages and your key from an **environment variable** (never in code, never in git); the JSON response holds the text, the usage and the stop reason. Your code that calls `llm.complete(...)` would not change; only the class behind it does. That is the reason to hide the provider behind a small interface of your own, the idea llm.02 builds on. This chapter does not run that step: it needs a paid key.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a conversation with a language model as four separate HTTP calls. In call 1 the client sends [system, user1]; in call 2 it sends [system, user1, assistant1, user2]; in call 3 it sends all five messages plus user3; and so on. Show each box growing, and write the number of input tokens billed under each call (60, 270, 480, 690). Emphasise with an arrow that the model itself remembers nothing between calls: the client re-sends everything."

### 1.5 Try it

1. A reply ends with the words "and the total comes to" and nothing else. What is the first thing you check?
2. Why does a stateless API make long chats expensive?
3. Why hide the provider behind your own small class instead of calling the provider's library everywhere?

<details><summary>Answer</summary>

1. `stop_reason`. If it is `"max_tokens"`, your cap cut the reply off: raise the cap, shorten what you ask for, or detect and handle truncation.
2. Each call re-sends the whole history, so call *n* is billed for everything said so far. The total input billed over a chat grows much faster than the length of the chat (section 3 measures it).
3. One place to change providers, add retries and logging, count usage and swap in a fake for tests. A provider's library scattered through the code makes all of those painful.

</details>

## 2. Tokens

### 2.1 Why not characters or words?

The model works on **tokens**: pieces of text from a fixed **vocabulary** (typically tens of thousands to a few hundred thousand entries). Why not characters? A text would become very long and each step would carry little meaning. Why not whole words? The vocabulary would need every word in every language, plus every name and typo, and anything unseen could not be represented at all. **Subword tokens** are the compromise: common words are one token, rare words split into pieces, and the worst case falls back to single characters or bytes. *(general knowledge)*

For you, three consequences:

- **You pay per token, not per word.** Cost and latency estimates start with a token count.
- **The same meaning costs different amounts** in different languages, in code, and in numbers.
- **The model sees tokens, not letters.** That explains several of its failures (section 7).

### 2.2 Build a tokenizer: byte-pair encoding from scratch

The most common recipe is **byte-pair encoding (BPE)**: start with single characters, then repeatedly **merge the most frequent adjacent pair** into a new symbol. After many merges, frequent words become one symbol. The merges, in order, *are* the tokenizer. Here is a small one, trained on a short paragraph:

```python run
corpus = """
a token is a small piece of text. a model reads tokens and writes tokens. the model reads the text token by token.
a long text has many tokens and a short text has few tokens. the cost of a call depends on the number of tokens.
the price of a token is small but a lot of tokens cost a lot. tokens are not words. a word can be one token or many tokens.
the tokenizer splits the text into tokens and the model reads the tokens. a good tokenizer makes the text short.
"""

END = "_"                                     # marks the end of a word, so "token_" and "token" inside "tokenizer" differ

def merge_pair(symbols, pair):
    """Replace every adjacent occurrence of `pair` in a list of symbols with the joined symbol."""
    out, i = [], 0
    while i < len(symbols):
        if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == pair:
            out.append(symbols[i] + symbols[i + 1]); i += 2
        else:
            out.append(symbols[i]); i += 1
    return out

def train_bpe(text, n_merges):
    """Learn merges. Returns the ordered list of merged pairs."""
    words = Counter(w + END for w in text.split())           # frequency of each whitespace-separated word
    vocab = {w: list(w) for w in words}                      # each word as a list of single characters
    merges = []
    for _ in range(n_merges):
        pairs = Counter()
        for w, symbols in vocab.items():
            for a, b in zip(symbols, symbols[1:]):
                pairs[(a, b)] += words[w]
        if not pairs:
            break
        best = max(pairs, key=lambda p: (pairs[p], p))       # most frequent pair; ties broken alphabetically
        merges.append(best)
        vocab = {w: merge_pair(s, best) for w, s in vocab.items()}
    return merges

def bpe_encode(text, merges):
    """Tokenise text: split into words, then apply the learned merges in the order they were learned."""
    tokens = []
    for w in text.split():
        symbols = list(w + END)
        for pair in merges:
            symbols = merge_pair(symbols, pair)
        tokens.extend(symbols)
    return tokens

merges = train_bpe(corpus, 60)
print("first 12 merges:", [a + "+" + b for a, b in merges[:12]])
test = "the tokenizer reads tokens"
for k in (0, 5, 20, 60):
    toks = bpe_encode(test, merges[:k])
    print(f"{k:>3} merges -> {len(toks):>2} tokens: {toks}")
```
```text
first 12 merges: ['t+o', 'k+e', 'to+ke', 'toke+n', 's+_', 'e+_', 't+_', 'a+_', 't+h', 'th+e_', '.+_', 't+e']
  0 merges -> 27 tokens: ['t', 'h', 'e', '_', 't', 'o', 'k', 'e', 'n', 'i', 'z', 'e', 'r', '_', 'r', 'e', 'a', 'd', 's', '_', 't', 'o', 'k', 'e', 'n', 's', '_']
  5 merges -> 17 tokens: ['t', 'h', 'e', '_', 'token', 'i', 'z', 'e', 'r', '_', 'r', 'e', 'a', 'd', 's_', 'token', 's_']
 20 merges -> 13 tokens: ['the_', 'token', 'i', 'z', 'e', 'r', '_', 'r', 'e', 'a', 'd', 's_', 'tokens_']
 60 merges ->  4 tokens: ['the_', 'tokenizer_', 'reads_', 'tokens_']
```

Watch the count fall: with **0 merges** every character is a token (27 symbols: 23 letters and 4 end markers). Each merge fuses a frequent pair, and after enough of them, `the` and `tokens` are single symbols. The first merges are the *most* frequent pairs, so the biggest savings come first and flatten out later: the tokens-per-text curve is a diminishing-returns curve, which is why real vocabularies stop at tens of thousands of merges rather than millions.

Notice also what the corpus decides. The tokenizer learned `token` because our corpus is about tokens. Words from a domain it never saw split into many small pieces:

```python run
for sample in ["the tokenizer reads tokens", "quantum chromodynamics", "xylophone zebra"]:
    toks = bpe_encode(sample, merges)
    chars = len(sample.replace(" ", ""))
    print(f"{sample:<28} {chars:>2} letters -> {len(toks):>2} tokens  ({len(toks) / chars:.2f} tokens per letter)")
```
```text
the tokenizer reads tokens   23 letters ->  4 tokens  (0.17 tokens per letter)
quantum chromodynamics       21 letters -> 21 tokens  (1.00 tokens per letter)
xylophone zebra              14 letters -> 13 tokens  (0.93 tokens per letter)
```

A tokenizer is cheap on the text it was trained on, and expensive on text far from it. Real vocabularies are trained on enormous mixed corpora, but the same effect shows up wherever their training mix is thin: other languages, rare scripts, source code in unusual styles, long numbers. *(general knowledge; the next section measures a real tokenizer)*

### 2.3 Bytes: the worst-case floor

Many modern tokenizers start from **bytes** rather than characters, so any text can be encoded, even text never seen. The count of bytes is therefore the *upper bound* on the number of tokens, and it differs a lot between scripts, because UTF-8 uses 1 byte for common English letters but 2 to 4 for others.

```python run
for name, s in [("English", "How are you?"), ("code", "def add(a, b): return a + b"), ("Hindi", "नमस्ते, आप कैसे हैं?"),
                ("emoji", "😀😀😀"), ("digits", "3141592653589793")]:
    print(f"{name:<8} {len(s):>3} characters  {len(s.encode('utf-8')):>3} bytes   {s!r}")
```
```text
English   12 characters   12 bytes   'How are you?'
code      27 characters   27 bytes   'def add(a, b): return a + b'
Hindi     20 characters   50 bytes   'नमस्ते, आप कैसे हैं?'
emoji      3 characters   12 bytes   '😀😀😀'
digits    16 characters   16 bytes   '3141592653589793'
```

A Hindi sentence of 20 characters is 50 bytes; an emoji is 4 bytes each (12 bytes for three). A tokenizer whose vocabulary has few Hindi pieces will spend somewhere between one token per character and one per byte there, while English words are one token each. *(general knowledge: this is why the same content typically costs more in less-represented languages.)*

### 2.4 A real tokenizer, offline (optional)

A real, trained subword vocabulary is available on this machine if you did ml.05: the DistilBERT **WordPiece** tokenizer is in the Hugging Face cache. It is not the tokenizer of any chat model (those differ in vocabulary and method), but it is real, it is trained on real text, and it shows the effect honestly. This block runs only if the `transformers` library and that cached file exist, and **never touches the network**:

```python run
import os
os.environ["HF_HUB_OFFLINE"] = "1"                                   # never download anything from this block
try:
    from transformers import AutoTokenizer
    wp = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased")
except Exception as e:
    wp = None
    print("real tokenizer not available here (needs the ml extra and the ml.05 download):", type(e).__name__)

if wp is not None:
    samples = [("English", "The quick brown fox jumps over the lazy dog."),
               ("code", "def add(a, b):\n    return a + b"),
               ("digits", "3.14159265358979 2718281828"),
               ("Hindi", "नमस्ते, आप कैसे हैं?"),
               ("one long word", "strawberry")]
    print(f"{'text':<14}{'chars':>6}{'tokens':>8}{'chars/token':>13}")
    for name, s in samples:
        ids = wp(s, add_special_tokens=False)["input_ids"]
        print(f"{name:<14}{len(s):>6}{len(ids):>8}{len(s) / len(ids):>13.2f}")
    print()
    print("digits ->", wp.convert_ids_to_tokens(wp("3.14159265358979", add_special_tokens=False)["input_ids"]))
    print("Hindi  ->", wp.convert_ids_to_tokens(wp("नमस्ते", add_special_tokens=False)["input_ids"]))
```
```text
text           chars  tokens  chars/token
English           44      10         4.40
code              31      12         2.58
digits            27      15         1.80
Hindi             20      11         1.82
one long word     10       1        10.00

digits -> ['3', '.', '141', '##59', '##26', '##53', '##58', '##9', '##7', '##9']
Hindi  -> ['न', '##म', '##स', '##त']
```

Read the table in the unit that matters for a bill, **characters per token**. Common English is about one token per word (4.4 characters per token); the digit string splits into many small pieces (`141`, `##59`, `##26`...) so a long number costs far more than its length suggests (1.8 characters per token); the Hindi sentence is similar, about 1.8 characters per token, so the same amount of text costs more than twice as many tokens; and a whole word like `strawberry` is a *single* token, so the model never sees the letters inside it (section 7 uses this). The `##` prefix marks a piece that continues a word.

The practical lessons:

1. **Count tokens for your own data.** Do not guess from the number of words. Take 20 typical inputs, count them, and look at the spread.
2. **The ratio varies by content.** The rule "one token is about four characters of English" is an average; code, numbers and other languages can be far worse. *(general knowledge: rules of thumb quoted by providers are about 3 to 4 characters, or 0.75 words, per token for English.)*
3. **Use the provider's own counter for exact numbers.** Providers publish a token-counting call or library for their tokenizer; use it in production code. Our estimate is for planning.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Show the sentence 'the tokenizer reads tokens' as a row of letter boxes with the end marker. Animate byte-pair encoding: highlight the most frequent adjacent pair in the training paragraph ('t'+'o', then 'to'+'k', then 'tok'+'e', ...), merge the two boxes into one wider box, and update a counter 'tokens: 24 -> 23 -> 22 ...'. At the end show the same row for 'quantum chromodynamics' which stays as many narrow boxes, with the caption 'a tokenizer is cheap on the text it was trained on'."

### 2.5 Try it

1. A prompt has 3,000 words of English. Roughly how many tokens? What changes if it is 3,000 words of source code?
2. Why does BPE learn `token` as one symbol in our corpus?
3. Your app is billed per token and your users write in Hindi. What would you do before promising a price?

<details><summary>Answer</summary>

1. With the usual rule of about 0.75 words per token, roughly 4,000 tokens. Source code usually has more tokens per word-like chunk because of symbols, indentation and identifiers, so expect more, and count a real sample.
2. The pair of characters inside `token` occurs many times in the corpus, so those merges are the most frequent ones and happen early; the more often a pair occurs, the sooner it is fused.
3. Take real Hindi samples, count them with the provider's tokenizer, compare against English samples of the same meaning, and price from **those** counts. The English estimate would under-state the cost.

</details>

## 3. Context windows and conversations

### 3.1 The window is a budget for input plus output

A model can only look at a limited number of tokens at once: its **context window**. The input (system prompt, history, documents you paste in) **and** the reply must fit together. Providers quote windows from a few thousand to hundreds of thousands of tokens, and the number changes with every model generation, so read the current one from the provider's model list rather than memorising it. *(general knowledge)*

```
 context window  =  system prompt  +  history  +  new input  +  room for the reply (max_tokens)
```

Three things go wrong near the limit:

1. **The call fails** with a "too long" error (our `ContextTooLong`).
2. **You pay for tokens that help little.** Most of a long input may be irrelevant.
3. **Quality can drop with very long inputs**: models can miss details placed in the middle of a long context. *(general knowledge from published evaluations; not measured here.)* A bigger window is capacity, not a guarantee that every part is used well.

### 3.2 Conversations re-send everything

Section 1 said the API is stateless. Measure what that costs. We simulate a 20-turn chat with `FakeLLM`: each user message is about 60 tokens and each reply about 150 tokens. Three history strategies:

- **full**: send the whole history every time,
- **window**: send only the last 6 messages,
- **summary**: send a 200-token summary of the old part plus the last 4 messages.

```python run
def fake_text(n_tokens, word="word"):
    """A reply of about n_tokens tokens (4 characters per token)."""
    return (word + " ") * (n_tokens // 1 * 4 // (len(word) + 1))

def run_chat(strategy, turns=20, user_tokens=60, reply_tokens=150, window=4000, keep=6):
    llm = FakeLLM(replies=lambda msgs: fake_text(reply_tokens), context_window=window)
    history, billed_in, billed_out, failed_at = [], [], 0, None
    summary = {"role": "user", "content": fake_text(200)}                 # a pretend 200-token summary
    for turn in range(1, turns + 1):
        history.append({"role": "user", "content": fake_text(user_tokens)})
        if strategy == "full":
            sent = history
        elif strategy == "window":
            sent = history[-keep:]
        else:                                                               # "summary"
            sent = ([summary] if len(history) > 4 else []) + history[-4:]
        try:
            r = llm.complete(sent, max_tokens=reply_tokens + 50)
        except ContextTooLong:
            failed_at = turn
            break
        history.append({"role": "assistant", "content": r.text})
        billed_in.append(r.usage.input_tokens)
        billed_out += r.usage.output_tokens
    return billed_in, billed_out, failed_at

print(f"{'strategy':<9}{'turns done':>11}{'input tokens billed':>21}{'last call input':>17}{'first failure':>15}")
for strategy in ("full", "window", "summary"):
    bi, bo, failed = run_chat(strategy)
    print(f"{strategy:<9}{len(bi):>11}{sum(bi):>21,}{bi[-1]:>17,}{str(failed or '-'):>15}")
```
```text
strategy  turns done  input tokens billed  last call input  first failure
full              19               38,494            3,988             20
window            20               11,964              654              -
summary           20               11,866              640              -
```

The **full** strategy fails at turn 20, when the history alone (4,206 tokens, see the table below) exceeds the 4,000-token window: a hard wall (our window is small on purpose; real windows are larger, the shape is the same). Before it fails, it has already billed about 38,500 input tokens over 19 turns, **3.2 times** what the two bounded strategies bill for 20 turns (about 12,000), and its last call is six times bigger than theirs. The bounded strategies keep a flat per-call input. Work out the full history's growth on paper to see why:

```python run
u, a = 60 + FRAMING, 150 + FRAMING                  # tokens added per user message and per reply, with framing
print(f"{'turn n':>7}{'input tokens this call':>24}{'total input so far':>20}")
total = 0
for n in (1, 2, 5, 10, 11, 20):
    this = n * u + (n - 1) * a                      # all n user messages and n-1 earlier replies
    total = sum(k * u + (k - 1) * a for k in range(1, n + 1))
    print(f"{n:>7}{this:>24,}{total:>20,}")
```
```text
 turn n  input tokens this call  total input so far
      1                      64                  64
      2                     282                 346
      5                     936               2,500
     10                   2,026              10,450
     11                   2,244              12,694
     20                   4,206              42,700
```

Call *n* sends `n` user messages and `n - 1` replies, so its input grows **linearly** with *n*, and the **total** billed over *n* turns grows with *n squared* (the sum of 1, 2, 3, ... n). Doubling the length of a chat roughly **quadruples** its input bill. This single fact explains most "why is our chat feature so expensive" surprises.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot, for a 20-turn chat, the number of input tokens sent on each call (y axis) against the turn number (x axis) for three strategies: 'full history' (a straight line rising steeply and crossing a horizontal line labelled 'context window 4000' at turn 20), 'last 6 messages' (flat after turn 3) and 'summary + last 4' (flat from turn 5). Shade the area under each line and print its total in the legend: that area is the bill."

### 3.3 Keeping the history in check

| Strategy | Idea | Costs and risks |
|---|---|---|
| **Sliding window** | keep the last *k* messages | simple and cheap; forgets everything older, including the user's first instruction |
| **Summarise** | replace old messages with a short summary written by a model | keeps the gist; costs an extra call, and a bad summary silently loses facts |
| **Retrieve** | store old messages or documents outside, fetch only the relevant pieces per call | best for large knowledge; needs a search system (a later module) |
| **Pin the essentials** | always keep the system prompt and a few key facts, and window the rest | protects instructions from falling out of the window |
| **Cap per request** | reject or truncate inputs above a limit | protects the budget from one huge paste |

Two details worth knowing *(general knowledge)*: providers offer **prompt caching**, where a repeated, unchanged beginning of the prompt (a long system prompt, a document) is billed at a reduced rate on later calls; and the **system prompt** is part of every call, so a 2,000-token system prompt on a feature that gets 100,000 calls a day is 200 million input tokens a day before anyone has typed a word.

### 3.4 Try it

1. A feature sends a 3,000-token system prompt and a 200-token question per call. What fraction of the input is the system prompt? What does it tell you to optimise?
2. In the 20-turn run, "window" and "summary" bill almost the same (about 11,960 and 11,870 input tokens). If cost is the same, why would you choose summary?
3. You use a sliding window of 6 messages and users complain "it forgot my name". Name two fixes.

<details><summary>Answer</summary>

1. 3,000 / 3,200 = 94 %. Any saving on the system prompt (shorten it, cache it, share it) matters far more than shortening the user's question.
2. Summary sends 200 tokens of summary plus 4 recent messages; window sends 6 recent messages, and a recent message is about 64 (user) or 154 (reply) tokens, so both come to roughly 650 per call. The benefit of summary is **quality** (it keeps the gist of old turns) rather than cost; and note the model call that *wrote* the summary is not in this count, so its real cost is a little higher.
3. Pin the essentials (keep the name in a pinned "facts" message that is always sent), or summarise the dropped messages into a running summary; or store "user facts" outside the chat and add them to the system prompt.

</details>

## 4. Sampling settings

### 4.1 From scores to a choice

At each step the model produces a **score (logit)** for every token in its vocabulary. These are turned into probabilities by the **softmax** function, and the next token is **drawn at random** from that distribution. The settings you control, **temperature**, **top-k** and **top-p**, reshape the distribution before the draw. To see exactly what each does, we need a model small enough to inspect. We build one: a **bigram language model** over a tiny corpus (it predicts the next *word* from the previous *word* by counting). It is a toy and real LLMs are vastly more capable, but the sampling step after the scores is the same maths.

```python run
text = """
the cat sat on the mat . the cat chased the mouse . the dog sat on the rug . the dog chased the cat .
the mouse ate the cheese . the cat ate the fish . the dog ate the bone . a mouse sat on a mat .
the cat saw the dog . the dog saw the mouse . the mouse saw the cat . the cat slept on the rug .
the dog slept on the mat . the fish was in the bowl . the cat chased the fish . the dog chased the mouse .
"""
words = text.split()
nxt = defaultdict(Counter)
for a, b in zip(words, words[1:]):
    nxt[a][b] += 1                                       # how often word b follows word a

def logits_after(word):
    """Scores for every possible next word: the log of the counts (a stand-in for a neural network's output)."""
    return {w: math.log(c) for w, c in nxt[word].items()}

def softmax(scores, temperature=1.0):
    """Turn scores into probabilities. Temperature divides the scores first."""
    t = max(temperature, 1e-6)
    m = max(scores.values())
    exps = {w: math.exp((s - m) / t) for w, s in scores.items()}          # subtract the max for numerical safety
    z = sum(exps.values())
    return {w: e / z for w, e in exps.items()}

def show(dist, top=6):
    for w, p in sorted(dist.items(), key=lambda kv: -kv[1])[:top]:
        print(f"    {w:<8}{p:6.3f}  {'#' * round(p * 40)}")

print("vocabulary:", len(set(words)), "words | pairs seen:", sum(len(c) for c in nxt.values()))
print("after 'the' the model scores:", {w: round(s, 2) for w, s in sorted(logits_after('the').items())})
for t in (1.0,):
    print(f"\nnext word after 'the', temperature {t}:")
    show(softmax(logits_after("the"), t))
```
```text
vocabulary: 20 words | pairs seen: 45
after 'the' the model scores: {'bone': 0.0, 'bowl': 0.0, 'cat': 2.08, 'cheese': 0.0, 'dog': 1.95, 'fish': 1.1, 'mat': 0.69, 'mouse': 1.61, 'rug': 0.69}

next word after 'the', temperature 1.0:
    cat      0.267  ###########
    dog      0.233  #########
    mouse    0.167  #######
    fish     0.100  ####
    mat      0.067  ###
    rug      0.067  ###
```

The probabilities mirror how often each word followed `the` in the corpus: `cat`, `dog`, `mouse` are common, `bone` and `bowl` rare. That is all "knowledge" this toy has. A real model learned far richer patterns, but its output is the same kind of object: a probability for every token.

### 4.2 Temperature

**Temperature** divides the scores before the softmax. A **low** temperature sharpens the distribution (the favourite gets almost all the probability); a **high** one flattens it (rare choices become likely); at temperature **0** providers use **greedy** decoding (always the top token).

```python run
for t in (0.2, 1.0, 2.0):
    print(f"temperature {t}:")
    show(softmax(logits_after("the"), t), top=4)

def entropy(dist):
    return -sum(p * math.log2(p) for p in dist.values() if p > 0)
print("\nentropy of the choice (bits; higher = more random):",
      {t: round(entropy(softmax(logits_after('the'), t)), 2) for t in (0.2, 0.5, 1.0, 2.0, 5.0)})
```
```text
temperature 0.2:
    cat      0.618  #########################
    dog      0.317  #############
    mouse    0.059  ##
    fish     0.005  
temperature 1.0:
    cat      0.267  ###########
    dog      0.233  #########
    mouse    0.167  #######
    fish     0.100  ####
temperature 2.0:
    cat      0.185  #######
    dog      0.173  #######
    mouse    0.146  ######
    fish     0.113  #####

entropy of the choice (bits; higher = more random): {0.2: 1.24, 0.5: 2.12, 1.0: 2.77, 2.0: 3.06, 5.0: 3.15}
```

At 0.2 the top word takes most of the probability; at 2.0 the choices are nearly even. The entropy line shows the dial in one number. Notice that temperature never *adds* knowledge: it only changes how greedily the model follows what it already believes.

### 4.3 Top-k and top-p (nucleus) sampling

Two other filters cut off the unlikely tail *before* drawing:

- **top-k**: keep only the *k* most probable tokens, renormalise.
- **top-p** (nucleus): keep the smallest set of tokens whose probabilities add up to at least *p*, renormalise. The set size adapts: small when the model is confident, large when it is unsure.

```python run
def top_k_filter(dist, k):
    keep = dict(sorted(dist.items(), key=lambda kv: -kv[1])[:k])
    z = sum(keep.values())
    return {w: p / z for w, p in keep.items()}

def top_p_filter(dist, p):
    keep, total = {}, 0.0
    for w, pr in sorted(dist.items(), key=lambda kv: -kv[1]):
        keep[w] = pr
        total += pr
        if total >= p:
            break
    z = sum(keep.values())
    return {w: pr / z for w, pr in keep.items()}

base = softmax(logits_after("the"), 1.0)
print("all words      :", len(base))
print("top-k  k=3     :", {w: round(p, 2) for w, p in top_k_filter(base, 3).items()})
print("top-p  p=0.8   :", {w: round(p, 2) for w, p in top_p_filter(base, 0.8).items()})
print("top-p  p=0.8 after 'sat' (a confident spot):", {w: round(p, 2) for w, p in top_p_filter(softmax(logits_after('sat'), 1.0), 0.8).items()})
```
```text
all words      : 9
top-k  k=3     : {'cat': 0.4, 'dog': 0.35, 'mouse': 0.25}
top-p  p=0.8   : {'cat': 0.32, 'dog': 0.28, 'mouse': 0.2, 'fish': 0.12, 'mat': 0.08}
top-p  p=0.8 after 'sat' (a confident spot): {'on': 1.0}
```

After `the` the model is unsure, so top-p 0.8 keeps several words; after `sat` it is nearly certain (`on`), so the same p keeps one or two. That adaptivity is why top-p is a popular default. Providers usually say to change **temperature or top-p, not both**, since both reshape the same distribution. *(general knowledge)*

### 4.4 Generating text, and what changes between runs

Now run the whole loop: start from `the`, pick a word, repeat until a full stop. A `random.Random(seed)` makes the draws repeatable, which is how you get reproducible tests.

```python run
def generate(start="the", temperature=1.0, top_p=1.0, seed=0, max_words=12):
    rng = random.Random(seed)
    out, word = [start], start
    for _ in range(max_words):
        dist = softmax(logits_after(word), temperature)
        if temperature <= 0.01:
            word = max(dist, key=dist.get)                         # greedy: always the most likely word
        else:
            dist = top_p_filter(dist, top_p)
            word = rng.choices(list(dist), weights=list(dist.values()))[0]
        out.append(word)
        if word == ".":
            break
    return " ".join(out)

print("greedy (T~0), three seeds :", [generate(temperature=0, seed=s) for s in range(3)])
print("T=1.0, same seed twice    :", generate(seed=7), "|", generate(seed=7))
for t in (0.3, 1.0, 2.0):
    print(f"T={t}:")
    for s in range(3):
        print("   ", generate(temperature=t, seed=s))

def diversity(t, n=200):
    return len({generate(temperature=t, seed=s) for s in range(n)})
print("\ndistinct sentences in 200 samples:", {t: diversity(t) for t in (0.2, 0.7, 1.0, 2.0)})
```
```text
greedy (T~0), three seeds : ['the cat chased the cat chased the cat chased the cat chased the', 'the cat chased the cat chased the cat chased the cat chased the', 'the cat chased the cat chased the cat chased the cat chased the']
T=1.0, same seed twice    : the dog chased the cat sat on the mouse . | the dog chased the cat sat on the mouse .
T=0.3:
    the dog ate the cat .
    the cat sat on the cat .
    the mouse ate the cat sat on the cat .
T=1.0:
    the rug .
    the cat saw the cat .
    the bone .
T=2.0:
    the cheese .
    the cat saw the dog ate the mat .
    the bowl .

distinct sentences in 200 samples: {0.2: 53, 0.7: 118, 1.0: 111, 2.0: 90}
```

Three things to take away:

1. **Greedy is deterministic**, and look at what it does: the same sentence for every seed, and a **loop** (`the cat chased the cat chased ...`). Always taking the single most likely word can trap a model in a repeating cycle; some randomness is what lets text move on. Low temperature (0.2) gives few distinct sentences. The last line counts distinct sentences in 200 draws: it rises from 53 at T=0.2 to 118 at T=0.7, but then *falls* (111, then 90), because at high temperature the full stop `.` becomes likely early, so many samples are short and the same (`the rug .`, `the bowl .`). Variety is not a simple function of temperature.
2. **A seed makes sampling reproducible**, here with Python's `random`. Many hosted APIs do not let you fix the seed and say outputs may still vary even at temperature 0; for tests you use a fake (like ours), not a real call. *(general knowledge)*
3. **Fluent does not mean true.** Look at the sentences: `the mouse ate the cat sat on the cat .` and `the cat saw the cat .` are *new recombinations* that follow the word statistics and were never in the corpus (and the first is not even grammatical: the toy only sees one word of context). Some others may happen to be in the corpus. A real model has a far longer context and far better statistics, so its recombinations are far more convincing, which is the dangerous part. The model produces what is statistically plausible, not what is true. That is the seed of hallucination (section 7).

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a bar chart of the probabilities of the next word after 'the' (cat, dog, mouse, fish, mat, rug, cheese, bone, bowl). Animate three sliders. Temperature: low makes the tallest bar swallow the others, high levels all bars. Top-k: bars beyond the k-th fade out and the rest grow to sum to 1. Top-p: bars fade out once the running total passes p. Show the entropy in bits next to the chart."

### 4.5 Which setting for which job?

*(general knowledge, as practice rather than measurement)*

| Task | Setting direction | Why |
|---|---|---|
| Extraction, classification, JSON output | low temperature (0 to 0.3) | you want the same, most likely answer |
| Code generation, factual Q&A | low to moderate | wrong creative leaps are bugs |
| Brainstorming, naming, varied copy | moderate to high | variety is the point |
| Anything you must test | temperature 0 plus a **fake** for unit tests | determinism for your own code |

Low temperature does **not** make the model truthful. It makes it more *consistent*, including consistently wrong.

### 4.6 Try it

1. At temperature 0 you ask the same question twice and get slightly different answers from a real API. Is something broken?
2. After `sat`, the model puts 90 % on `on`. What does top-p = 0.8 keep? What does top-k = 3 keep?
3. Why is a high temperature a poor choice for extracting an invoice number from text?

<details><summary>Answer</summary>

1. Not necessarily. Many hosted models do not guarantee bit-identical outputs even at temperature 0 (batching and hardware effects can change tiny numeric details and flip close choices). Design for it: validate outputs, do not assume identical text. *(general knowledge)*
2. Top-p 0.8 keeps only `on` (it alone already reaches 0.9 >= 0.8). Top-k 3 keeps the top three words, however unlikely the second and third are, so it is less adaptive.
3. Extraction wants the single most likely correct string; randomness only adds chances of a wrong digit. Use low temperature and validate the result (section 7).

</details>

## 5. Estimating cost and latency before you build

### 5.1 The five-minute method

You do not need a prototype to know whether a feature is affordable and fast enough. Five steps on paper:

1. **Describe one call**: how many input tokens (system prompt + retrieved context + user text + history) and how many output tokens.
2. **Price it**: `cost = input_tokens x input price + output_tokens x output price`. Providers quote prices **per million tokens**, and **output tokens cost several times more than input tokens**. *(general knowledge)*
3. **Time it**: `latency = time to first token + output_tokens / tokens per second`. The first term is the wait before anything appears; the second is the speed of writing.
4. **Multiply by traffic**: calls per day, and the **peak** rate, not just the average.
5. **Compare with the limits**: a monthly budget and a latency target, and write down the assumptions you were least sure of.

> **The numbers below are illustrative placeholders**, chosen to be easy to calculate with, not any provider's real prices or speeds. Real ones change often: read the provider's current price page and put the real figures into the calculator's config file (section 8).

```python run
@dataclass(frozen=True)
class Price:
    """Dollars per MILLION tokens."""
    input_per_m: float
    output_per_m: float
    cached_input_per_m: float = None          # price for input tokens served from a prompt cache, if any

@dataclass(frozen=True)
class Speed:
    ttft_s: float                              # time to first token
    tokens_per_s: float                        # output speed

TIERS = {                                      # ILLUSTRATIVE numbers only
    "small":  (Price(1.0, 5.0, 0.10),   Speed(0.3, 120)),
    "medium": (Price(3.0, 15.0, 0.30),  Speed(0.5, 70)),
    "large":  (Price(15.0, 75.0, 1.50), Speed(1.0, 40)),
}

def call_cost(in_tok, out_tok, price, cached_tok=0):
    """Dollars for one call. cached_tok of the input tokens are billed at the cached rate."""
    cached_rate = price.cached_input_per_m if price.cached_input_per_m is not None else price.input_per_m
    fresh = in_tok - cached_tok
    return (fresh * price.input_per_m + cached_tok * cached_rate + out_tok * price.output_per_m) / 1e6

def call_latency(out_tok, speed):
    return speed.ttft_s + out_tok / speed.tokens_per_s

# One call of a "support reply drafter": 600 system + 1500 retrieved help-centre text + 100 customer message
in_tok, out_tok = 600 + 1500 + 100, 250
print(f"one call: {in_tok} tokens in, {out_tok} tokens out\n")
print(f"{'tier':<8}{'cost per call':>15}{'input share':>13}{'latency (s)':>13}{'first token (s)':>17}")
for name, (price, speed) in TIERS.items():
    c_in, c_out = in_tok * price.input_per_m / 1e6, out_tok * price.output_per_m / 1e6
    print(f"{name:<8}${c_in + c_out:>13.5f}{c_in / (c_in + c_out):>12.0%}{call_latency(out_tok, speed):>13.2f}{speed.ttft_s:>17.2f}")
```
```text
one call: 2200 tokens in, 250 tokens out

tier      cost per call  input share  latency (s)  first token (s)
small   $      0.00345         64%         2.38             0.30
medium  $      0.01035         64%         4.07             0.50
large   $      0.05175         64%         7.25             1.00
```

Two observations to take from one small table. First, the **input** is 88 % of the tokens but only 64 % of the cost (the input share column), because output tokens are priced higher: shortening the reply is a bigger lever per token than shortening the prompt, though both matter. Second, **latency is dominated by the writing**: 250 output tokens at 40 tokens per second is over six seconds for the large tier. If you **stream** the reply (tokens appear as they are generated), the user sees the first words after `ttft`, which is much shorter, so *perceived* latency and *total* latency are different numbers; choose which one your requirement is about.

### 5.2 From one call to a monthly bill and a peak load

```python run
def estimate(calls_per_day, in_tok, out_tok, price, speed, *, cached_share=0.0, retry_overhead=0.05, peak_factor=8, days=30):
    """Monthly cost, per-call latency and peak concurrency for one feature. All inputs are assumptions you state."""
    cached = int(in_tok * cached_share)
    per_call = call_cost(in_tok, out_tok, price, cached) * (1 + retry_overhead)          # retries and failures cost money too
    latency = call_latency(out_tok, speed)
    avg_rate = calls_per_day / 86400                                                      # calls per second, averaged over the day
    peak_rate = avg_rate * peak_factor
    return {"per_call": per_call, "per_day": per_call * calls_per_day, "per_month": per_call * calls_per_day * days,
            "latency_s": latency, "peak_per_s": peak_rate, "peak_concurrent": peak_rate * latency}      # Little's law: L = rate x time

print(f"{'tier':<8}{'$ per month':>13}{'latency s':>11}{'peak calls/s':>14}{'concurrent calls at peak':>26}")
for name, (price, speed) in TIERS.items():
    e = estimate(2000, in_tok, out_tok, price, speed)
    print(f"{name:<8}{e['per_month']:>13,.2f}{e['latency_s']:>11.2f}{e['peak_per_s']:>14.2f}{e['peak_concurrent']:>26.2f}")

print("\nsensitivity on the medium tier (monthly dollars):")
price, speed = TIERS["medium"]
for label, kw in [("as planned", {}), ("replies twice as long (500 tokens)", {"out_tok": 500}),
                  ("traffic x5 (10,000 calls/day)", {"calls_per_day": 10000}),
                  ("2,100 of the input tokens cached", {"cached_share": 2100 / 2200})]:
    args = dict(calls_per_day=2000, in_tok=in_tok, out_tok=out_tok); args.update({k: v for k, v in kw.items() if k in args})
    e = estimate(args["calls_per_day"], args["in_tok"], args["out_tok"], price, speed, **{k: v for k, v in kw.items() if k not in args})
    print(f"  {label:<38}${e['per_month']:>9,.2f}")
```
```text
tier      $ per month  latency s  peak calls/s  concurrent calls at peak
small          217.35       2.38          0.19                      0.44
medium         652.05       4.07          0.19                      0.75
large        3,260.25       7.25          0.19                      1.34

sensitivity on the medium tier (monthly dollars):
  as planned                            $   652.05
  replies twice as long (500 tokens)    $   888.30
  traffic x5 (10,000 calls/day)         $ 3,260.25
  2,100 of the input tokens cached      $   294.84
```

Read the second block as a **sensitivity analysis**: which assumption moves the bill most? Doubling the reply length is costly because output tokens are expensive; five times the traffic is five times the bill, naturally; and caching the repeated 2,100 input tokens (if the provider supports it and the prefix really is identical on every call) cuts the input side sharply. *(The discount rate is an illustrative parameter.)* If an assumption you are unsure of changes the verdict, that is where to spend your next hour measuring.

The last column uses **Little's law**: the average number of calls in flight equals the arrival rate times the time each call takes. At peak this tells you how many concurrent requests your code and your provider account must handle, which links to rate limits (llm.02).

### 5.3 A budget check, and a written estimate

An estimate is only useful if it is compared with a requirement. Compose the pieces into a verdict you can paste into a design document:

```python run
def verdict(name, e, budget_month, max_latency_s):
    ok_cost, ok_lat = e["per_month"] <= budget_month, e["latency_s"] <= max_latency_s
    flags = ("cost OK" if ok_cost else f"cost x{e['per_month'] / budget_month:.1f} over") + ", " + \
            ("latency OK" if ok_lat else f"latency {e['latency_s']:.1f}s > {max_latency_s}s")
    return f"{name:<7} ${e['per_month']:>8,.2f}/month, {e['latency_s']:.1f}s  ->  {flags}"

for name, (price, speed) in TIERS.items():
    print(verdict(name, estimate(2000, in_tok, out_tok, price, speed), budget_month=300, max_latency_s=5))
```
```text
small   $  217.35/month, 2.4s  ->  cost OK, latency OK
medium  $  652.05/month, 4.1s  ->  cost x2.2 over, latency OK
large   $3,260.25/month, 7.2s  ->  cost x10.9 over, latency 7.2s > 5s
```

With a budget of $300 a month and a 5-second answer, only some tiers pass: the verdict depends on **both** limits, and the tier that is cheap enough may be too weak for the task (section 6), while the tier that is good enough may be too slow or too expensive. That tension is the whole subject of the next section.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one LLM call as a timeline: a long input block (2,200 tokens, grey) is read, then a gap labelled 'time to first token', then 250 small output blocks appear one by one at a steady rate. Under it draw a price tag per block: input blocks are cheap, output blocks five times more expensive. Show three rows for the tiers small, medium, large, each with its total time and cost at the end of the timeline, so the reader sees cost and time as areas."

### 5.4 Try it

1. A feature runs 50,000 calls a day, each with 400 tokens in and 100 out, on a tier priced at $1 per million input and $5 per million output tokens. Monthly cost?
2. The same feature adds a 1,500-token system prompt. By how much does the monthly input cost rise?
3. Peak load is 20 calls per second and each call takes 3 seconds. How many calls are in flight at peak?

<details><summary>Answer</summary>

1. Per call: 400 x 1/1e6 + 100 x 5/1e6 = $0.0004 + $0.0005 = $0.0009. Per day: 50,000 x 0.0009 = $45. Per month (30 days): **$1,350**. Output is 56 % of the cost although it is only 20 % of the tokens.
2. 1,500 extra input tokens x $1/1e6 = $0.0015 per call; x 50,000 calls x 30 days = **$2,250 more per month**: the prompt is now larger than the whole previous bill. This is why long system prompts need caching, trimming or both.
3. 20 x 3 = **60 calls in flight** (Little's law). Check your provider's concurrency and rate limits against it.

</details>

## 6. Choosing a model

### 6.1 Tiers, and what they trade

Providers offer a **family** of models at several sizes. In general *(general knowledge)*: bigger models are more capable on hard tasks (long reasoning, subtle instructions, rare knowledge), slower and more expensive; smaller models are fast and cheap and good enough for many well-defined tasks (classification, extraction, short rewrites, routing). Names and numbers change with every release, so a chapter cannot give you "the best model". What lasts is the **method**:

1. **Write the task and a small evaluation set**: 50 to 200 real examples with the answer you would accept. No benchmark score replaces this.
2. **Run each candidate tier on the set** and record accuracy (or a rubric score), tokens used, cost and latency.
3. **Pick the cheapest tier that clears your quality bar**, with margin.
4. **Re-run when the model, the prompt or the data changes.** Quality is a measurement, not a property you read off a leaderboard.

Compare with **cost per correct answer** = cost per call / accuracy. A model twice as expensive and much more accurate can be cheaper per *correct* answer, and a wrong answer often has its own cost (a human fixes it, a customer is annoyed).

### 6.2 Routing: ask the small model first

If a cheap model is right most of the time and *knows when it is unsure*, you can use it first and **escalate** only the hard cases to the big model. The saving depends on two numbers: how often you escalate, and how much more the big one costs. A simulation makes this concrete. **The accuracies and confidences here are made-up assumptions (a simulation of the arithmetic), not measurements of any real model.**

```python run
rng = random.Random(1)
N = 2000                                                              # simulated labelled requests

def simulate_model(accuracy, rng):
    """Return (correct, confidence). A model is more confident, on average, when it is right."""
    correct = rng.random() < accuracy
    conf = rng.uniform(0.6, 1.0) if correct else rng.uniform(0.3, 0.8)
    return correct, conf

small_price, big_price = TIERS["small"][0], TIERS["large"][0]
c_small = call_cost(in_tok, out_tok, small_price)
c_big = call_cost(in_tok, out_tok, big_price)
ACC_SMALL, ACC_BIG = 0.85, 0.96                                       # assumptions

rows = []
for threshold in (None, 0.9, 0.8, 0.7, 0.5):                            # None = always the small model
    correct = cost = escalated = 0
    r = random.Random(7)                                                 # same requests for every policy
    for _ in range(N):
        ok_s, conf = simulate_model(ACC_SMALL, r)
        ok_b, _ = simulate_model(ACC_BIG, r)
        cost += c_small
        if threshold is not None and conf < threshold:
            escalated += 1
            cost += c_big
            correct += ok_b
        else:
            correct += ok_s
    rows.append((threshold, correct / N, cost / N, escalated / N))

print(f"cost per call: small ${c_small:.5f}, large ${c_big:.5f}  ({c_big / c_small:.0f}x)")
print(f"{'policy':<22}{'accuracy':>9}{'$ per call':>12}{'escalated':>11}{'$ per correct':>15}")
print(f"{'always large':<22}{ACC_BIG:>9.3f}{c_big:>12.5f}{'100%':>11}{c_big / ACC_BIG:>15.5f}")
for threshold, acc, cost, esc in rows:
    label = "always small" if threshold is None else f"small, escalate <{threshold}"
    print(f"{label:<22}{acc:>9.3f}{cost:>12.5f}{esc:>11.0%}{cost / acc:>15.5f}")
print(f"\nbreak-even: a cascade beats 'always large' on cost only if the escalation rate is below {1 - c_small / c_big:.0%}")
```
```text
cost per call: small $0.00345, large $0.05175  (15x)
policy                 accuracy  $ per call  escalated  $ per correct
always large              0.960     0.05175       100%        0.05391
always small              0.858     0.00345         0%        0.00402
small, escalate <0.9      0.968     0.04358        78%        0.04505
small, escalate <0.8      0.975     0.03321        57%        0.03406
small, escalate <0.7      0.963     0.02053        33%        0.02132
small, escalate <0.5      0.915     0.00658         6%        0.00719

break-even: a cascade beats 'always large' on cost only if the escalation rate is below 93%
```

The break-even line is a one-line derivation: the cascade costs `c_small + e x c_big` per call (the small model always runs; the big one only on the escalated fraction `e`); it beats `c_big` when `e < 1 - c_small / c_big`. With a large price gap the allowed escalation rate is high, so routing is attractive; if the tiers cost nearly the same it is not. In the table, a lower threshold means fewer escalations and lower cost but lower accuracy: a **dial**. (Look at the 0.8 row: the cascade scores *higher* than always-large. That is an artifact of the assumptions I invented, in which the small model's confidence is informative and it is right on the cases where it is sure; a real model may or may not behave like that, which is exactly why the dial must be set from your quality bar on **real** evaluation data.) What decides everything is the real relationship between a model's confidence and its correctness, and a model's stated confidence is often poorly calibrated. *(general knowledge)*

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a request router. Every request goes to a small cheap model first, which returns an answer and a confidence between 0 and 1. A gate asks 'confidence below the threshold?'. If yes, the request continues to the large model; if no, the small model's answer is returned. Show 2,000 dots (requests) flowing through, coloured green when the final answer is correct and red when wrong, with a slider for the threshold (0.5 to 0.9) and live counters for 'escalated %', 'accuracy' and '$ per call'."

### 6.3 Beyond price and quality: other criteria

| Question | Why it matters |
|---|---|
| **Context window** | does your input fit, with room for the reply? |
| **Latency and streaming** | first-token time for interactive features; total time for batch jobs |
| **Rate limits** | requests and tokens per minute on your account: a hard cap on throughput |
| **Structured output and tool support** | needed by the features of llm.02 to llm.04 |
| **Data handling** | where your inputs go, how long they are kept, whether they train models: **never** send secrets or personal data to a provider you have not checked against your policy |
| **Reliability and lock-in** | outages happen; keep your own interface (section 1.4) so you can switch or fall back |
| **Batch or offline pricing** | many providers discount non-urgent bulk jobs *(general knowledge)* |

### 6.4 Try it

1. Model A costs $0.002 per call and is 90 % accurate; model B costs $0.004 per call and is 98 % accurate. Which is cheaper per correct answer? What else would you need to know to decide?
2. A cascade escalates 30 % of calls. The big model costs 12 times the small one. Cheaper than always-big?
3. Why is a public benchmark score a poor substitute for your own evaluation set?

<details><summary>Answer</summary>

1. A: 0.002 / 0.90 = $0.00222. B: 0.004 / 0.98 = $0.00408. A is cheaper per correct answer. You also need the cost of a *wrong* answer: if each error costs a human 5 minutes, B's 8 fewer errors per 100 may be worth far more than its extra price.
2. Allowed escalation rate is 1 - 1/12 = 92 %. At 30 % escalation, the cascade costs 1 + 0.3 x 12 = 4.6 units against 12 for always-big: **much cheaper** (if the accuracy is acceptable).
3. The benchmark measures other tasks, on other inputs and often with other prompts; models may have seen it in training; and a general average hides the specific case your product depends on. Your set contains your actual inputs and your own definition of correct.

</details>

## 7. What models are bad at

### 7.1 The honest list

*(general knowledge, from the literature and everyday experience; the demonstrations below are measured on code, not on a real model.)*

| Weakness | What it looks like | Why (briefly) | Defence |
|---|---|---|---|
| **Hallucination** | confident, fluent statements that are false: invented facts, citations, function names, quotes | the model produces *plausible* continuations; truth is not what it was trained to guarantee (section 4.4) | give it the source text, verify with code, require citations and check them |
| **Exact arithmetic** | wrong products and sums of long numbers | it predicts digits as text pieces; it is not running a calculator | call a calculator or run code |
| **Counting and spelling** | miscounted letters or words | it sees tokens, not letters (section 2) | do it in code |
| **Stale knowledge** | does not know recent events or new library versions | training stopped at a cutoff date | supply current documents; do not assume freshness |
| **No memory between calls** | "forgets" earlier chats | stateless API (section 1) | you manage history and stored facts |
| **Following long or conflicting instructions** | skips a rule buried in a long prompt | attention is finite; instructions compete | short clear prompts, put key rules first and last, test with real cases |
| **Inconsistency** | different answers to the same question | sampling and hardware effects (section 4) | low temperature, validation, majority checks for important answers |
| **Sycophancy** | agrees with a wrong premise from the user | trained to be agreeable | ask neutral questions; verify claims independently |
| **Prompt injection** | text in a document tells the model to ignore its instructions | the model cannot tell data from instructions | treated seriously in a later LLM module |

### 7.2 Why it cannot see letters or digits: tokens again

In section 2.4, `strawberry` was one token. If a model's vocabulary holds a word as a single unit, "how many r's does it contain" asks about something *inside* a token that the model never sees as separate characters. Long numbers are cut into arbitrary chunks, so digit-by-digit arithmetic has no clean basis either. The exact answer for such things is one line of ordinary code:

```python run
print("letters r in 'strawberry':", "strawberry".count("r"), "(by code, always right)")
print("48271 * 69313 =", 48271 * 69313, "(by code, always right)")
if wp is not None:
    pieces = wp.convert_ids_to_tokens(wp("48271*69313 and strawberry", add_special_tokens=False)["input_ids"])
    print("what a model with this vocabulary actually sees:", pieces)
```
```text
letters r in 'strawberry': 3 (by code, always right)
48271 * 69313 = 3345807823 (by code, always right)
what a model with this vocabulary actually sees: ['48', '##27', '##1', '*', '69', '##31', '##3', 'and', 'strawberry']
```

That is the pattern for every exact task: **do not ask the model to be a calculator; give it a calculator** (a *tool*, a later module). Let the model decide *what* to compute, and let code do the computing.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Show the word 'strawberry' in two ways. Top: as the user sees it, ten letter boxes s-t-r-a-w-b-e-r-r-y with the three r's highlighted. Bottom: as a model with a whole-word vocabulary sees it, one single box labelled token #29,000 with no letters visible inside. Add a second example: '48271*69313' cut into chunks '48', '##27', '##1', '*', '69', '##31', '##3'. Caption: 'asking for the letters inside a token is asking about something the model never saw'."

### 7.3 Verifying with code: catching an invented function

Hallucination is not rare noise you can ignore: for questions at the edge of what it knows, a model may confidently describe something that does not exist. A cheap and powerful defence is to **check what you can with code**. Here a scripted `FakeLLM` stands in for a model that was asked "What does `statistics.harmonic_median` do?" (there is no such function) and answers fluently anyway. A checker looks up every `module.function(` name it mentions and tests whether it exists:

```python run
bad_answer = ("statistics.harmonic_median(data) returns the median of the harmonic means of the data. "
              "It works like statistics.median(data) but uses statistics.harmonic_mean(data) as a tie-breaker.")
llm = FakeLLM(replies=[bad_answer])
reply = llm.complete([{"role": "user", "content": "What does statistics.harmonic_median do?"}])

def referenced_functions(text):
    """Find dotted names that look like module.function( in a piece of text."""
    return sorted(set(re.findall(r"\b([a-z_][a-z_0-9]*)\.([a-z_][a-z_0-9]*)\(", text)))

def check_exists(module_name, func_name):
    try:
        return callable(getattr(importlib.import_module(module_name), func_name, None))
    except ImportError:
        return False

print("model said:", reply.text[:90] + "...")
for module_name, func_name in referenced_functions(reply.text):
    print(f"  {module_name}.{func_name:<16} exists: {check_exists(module_name, func_name)}")
```
```text
model said: statistics.harmonic_median(data) returns the median of the harmonic means of the data. It ...
  statistics.harmonic_mean    exists: True
  statistics.harmonic_median  exists: False
  statistics.median           exists: True
```

The fluent answer mentions two real functions (`statistics.median`, `statistics.harmonic_mean`) and one invented one (`harmonic_median`), and nothing in the *tone* tells you which is which. Code found it in microseconds. Apply the same idea wherever the answer can be checked: a JSON reply against a schema, a number against a range, a quoted passage against the source document (is it really there?), an SQL query against the database (does the column exist?), a URL against a fetch.

### 7.4 A retry-with-validation wrapper

Because checks are cheap and calls are not free, a common pattern is: call, **validate**, and if the check fails, try again with the error message, up to a limit; if it still fails, hand over to a fallback or a human. The fake client lets us test this without any model:

```python run
def checked_call(llm, messages, validate, tries=3):
    """Call the model, validate the reply, retry with feedback. Returns (reply or None, attempts used, total input tokens billed)."""
    msgs, billed = list(messages), 0
    for attempt in range(1, tries + 1):
        reply = llm.complete(msgs, max_tokens=100)
        billed += reply.usage.input_tokens
        problem = validate(reply)
        if problem is None:
            return reply, attempt, billed
        msgs = msgs + [{"role": "assistant", "content": reply.text}, {"role": "user", "content": f"That was invalid: {problem}. Reply with valid JSON only."}]
    return None, tries, billed

def validate_json(reply):
    if reply.stop_reason != "end_turn":
        return "the reply was cut off (max_tokens)"
    try:
        data = json.loads(reply.text)
    except json.JSONDecodeError as e:
        return f"not JSON ({e.msg})"
    return None if isinstance(data.get("total"), (int, float)) else "missing numeric field 'total'"

flaky = FakeLLM(replies=["Sure! The total is 42.", '{"total": "42"}', '{"total": 42}'])
reply, attempts, billed = checked_call(flaky, [{"role": "user", "content": "Extract the total as JSON."}], validate_json)
print("result:", reply.text, "| attempts:", attempts, "| input tokens billed:", billed)

hopeless = FakeLLM(replies=["no idea"])
reply, attempts, billed = checked_call(hopeless, [{"role": "user", "content": "Extract the total as JSON."}], validate_json)
print("hopeless model -> reply:", reply, "| attempts:", attempts, "| input tokens billed:", billed)
```
```text
result: {"total": 42} | attempts: 3 | input tokens billed: 130
hopeless model -> reply: None | attempts: 3 | input tokens billed: 120
```

Notice that **each retry re-sends and re-bills the growing conversation** (section 3). A wrapper that retries three times on every failure can triple the cost of exactly the requests that fail most. Decide limits deliberately, and track the retry rate as a metric: a rising rate is the early warning that a prompt or model change made things worse. Reliable structured output, with real schemas, is the subject of llm.02.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a pipeline with four boxes: 'user question' -> 'model draft' -> 'checker (code)' -> 'answer or fallback'. Under 'checker' list four example checks: JSON schema valid, number in range, quoted text found in the source, function name exists. Draw a loop arrow from 'checker' back to 'model draft' labelled 'invalid: retry with the error message, max 3 times' and an arrow from the loop to 'human review' labelled 'still invalid'. Colour the model box orange ('can be wrong, fluently') and the checker box green ('deterministic')."

### 7.5 Also remember

- **Privacy and policy.** Anything you send to a hosted model leaves your machine. Do not send passwords, keys or personal data unless you have checked the provider's data policy and your own.
- **Responsibility stays with you.** If the feature gives wrong medical, legal or financial advice, "the model said so" is not a defence. High-stakes outputs need a human check.
- **Do not promise what you did not measure.** "It's 95 % accurate" needs an evaluation set you built; "it hallucinates sometimes" is something to design around, not to hope away.

### 7.6 Try it

1. A colleague says "set the temperature to 0 so it stops hallucinating". Is that right?
2. You ask a model for the source of a quote, and it gives a book title, chapter and page. List two ways to check it before showing it to a user.
3. Which of these are better done by code than by a model: sorting 500 numbers, deciding whether a customer email is angry, summing an invoice, rewriting a paragraph politely?

<details><summary>Answer</summary>

1. No. Temperature 0 makes the output *consistent*, not *true*: it picks the most likely continuation every time, including a likely-sounding falsehood. Ground the answer in a source and verify it.
2. Search for the book in a catalogue or search API and check the title exists; fetch the text if you have it and check the quote is really on that page; require the model to quote from a document *you* supplied and string-match it. If a check cannot be done, show it as unverified.
3. Sorting and summing are exact tasks: code. Judging anger and polite rewriting are language tasks: a model, with a check (for the sum, you might also let the model *read* the amounts and then add them with code).

</details>

## 8. Project: token and cost calculator for prompts

### 8.1 The brief

Build the tool you wish you had before your first LLM bill: a small, tested Python package and command-line program that answers, **before any call is made**:

> *"For this prompt design and this traffic, on each candidate model: how many tokens, how much per call, per day and per month, how long does one call take, how many calls are in flight at peak, does it fit the context window, and does it meet my budget and latency target?"*

Requirements:

1. **`llmcost.py`**: a library with token estimation (three methods, with a low-expected-high range), per-call cost with cached tokens, latency, a monthly estimate with retries and peak concurrency (Little's law), a closed-form cost of a growing conversation, model configuration loaded from a **TOML file** (prices are data you edit, never hard-coded), comparison and a verdict against a budget and a latency target.
2. **A command-line interface**: `python llmcost.py spec.json --models models.toml --budget 300 --max-latency 5`, which prints a table and **exits with status 1 if no model meets the limits** (so it can sit in a script or CI check).
3. **`test_llmcost.py`**: pytest tests with hand-checked values and messages that name the likely mistake.
4. **Honesty built in**: the config file says whether its prices are `illustrative`, and the output warns loudly if they are. The tool must never present placeholder prices as real.

### 8.2 The library

```python run
proj = ws / "project"
proj.mkdir()
(proj / "llmcost.py").write_text(r'''"""llmcost: estimate the tokens, cost and latency of an LLM feature before building it."""
from __future__ import annotations

import argparse
import json
import math
import sys
import tomllib
from dataclasses import dataclass


# ---------------------------------------------------------------- tokens
def estimate_tokens(text: str, method: str = "chars4") -> int:
    """Rough token count. 'chars4': ~4 characters per token (English). 'words': ~0.75 words per token.
    'bytes': one token per UTF-8 byte, an upper bound for byte-level tokenisers."""
    if not text:
        return 0
    if method == "chars4":
        return math.ceil(len(text) / 4)
    if method == "words":
        return math.ceil(len(text.split()) / 0.75)
    if method == "bytes":
        return len(text.encode("utf-8"))
    raise ValueError(f"unknown method {method!r}; use chars4, words or bytes")


def token_range(text: str) -> tuple[int, int, int]:
    """(low, expected, high). Low: about one token per word. Expected: 4 characters per token. High: one per byte."""
    low = len(text.split())
    expected = estimate_tokens(text, "chars4")
    high = estimate_tokens(text, "bytes")
    return min(low, expected), expected, max(high, expected)


# ---------------------------------------------------------------- models
@dataclass(frozen=True)
class Model:
    name: str
    input_per_m: float                 # dollars per million input tokens
    output_per_m: float                # dollars per million output tokens
    ttft_s: float                      # seconds to the first token
    tokens_per_s: float                # output speed
    context_window: int
    cached_input_per_m: float | None = None


def load_models(path) -> tuple[list[Model], bool]:
    """Read models from a TOML file. Returns (models, illustrative). Raises ValueError on bad data."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    models = []
    for name, row in data.get("models", {}).items():
        try:
            m = Model(name, float(row["input_per_m"]), float(row["output_per_m"]), float(row["ttft_s"]),
                      float(row["tokens_per_s"]), int(row["context_window"]),
                      float(row["cached_input_per_m"]) if "cached_input_per_m" in row else None)
        except KeyError as exc:
            raise ValueError(f"model {name!r} is missing the field {exc.args[0]!r}") from None
        if min(m.input_per_m, m.output_per_m, m.ttft_s) < 0 or m.tokens_per_s <= 0 or m.context_window <= 0:
            raise ValueError(f"model {name!r} has a negative price or a non-positive speed or window")
        models.append(m)
    if not models:
        raise ValueError("no [models.*] tables found in the file")
    return models, bool(data.get("illustrative", False))


# ---------------------------------------------------------------- one call
def call_cost(model: Model, input_tokens: int, output_tokens: int, cached_tokens: int = 0) -> float:
    """Dollars for one call. cached_tokens of the input are billed at the cached rate (if the model has one)."""
    if not 0 <= cached_tokens <= input_tokens:
        raise ValueError("cached_tokens must be between 0 and input_tokens")
    rate = model.cached_input_per_m if model.cached_input_per_m is not None else model.input_per_m
    return ((input_tokens - cached_tokens) * model.input_per_m + cached_tokens * rate + output_tokens * model.output_per_m) / 1e6


def call_latency(model: Model, output_tokens: int) -> float:
    """Seconds: time to first token plus the time to write the reply."""
    return model.ttft_s + output_tokens / model.tokens_per_s


# ---------------------------------------------------------------- a feature
@dataclass(frozen=True)
class Spec:
    """A prompt design plus traffic. Token counts per call, from your own samples."""
    system_tokens: int = 0
    context_tokens: int = 0
    user_tokens: int = 0
    history_tokens: int = 0
    output_tokens: int = 0
    calls_per_day: int = 0
    cached_share: float = 0.0          # fraction of the input served from a prompt cache (0 to 1)
    retry_overhead: float = 0.0        # extra calls from retries, as a fraction (0.05 = 5 %)
    peak_factor: float = 1.0           # peak call rate divided by the daily average rate

    @property
    def input_tokens(self) -> int:
        return self.system_tokens + self.context_tokens + self.user_tokens + self.history_tokens


def estimate(spec: Spec, model: Model, days: int = 30) -> dict:
    """Cost, latency, load and context fit of a feature on one model."""
    if not 0.0 <= spec.cached_share <= 1.0:
        raise ValueError("cached_share must be between 0 and 1")
    cached = int(spec.input_tokens * spec.cached_share)
    per_call = call_cost(model, spec.input_tokens, spec.output_tokens, cached) * (1 + spec.retry_overhead)
    latency = call_latency(model, spec.output_tokens)
    peak_rate = spec.calls_per_day / 86400 * spec.peak_factor
    return {"model": model.name, "per_call": per_call, "per_day": per_call * spec.calls_per_day,
            "per_month": per_call * spec.calls_per_day * days, "latency_s": latency,
            "peak_per_s": peak_rate, "peak_concurrent": peak_rate * latency,          # Little's law: L = rate x time
            "fits_context": spec.input_tokens + spec.output_tokens <= model.context_window}


def full_history_tokens(turns: int, user_tokens: int, reply_tokens: int) -> int:
    """Total input tokens billed over a chat that re-sends the whole history every turn.
    Call n carries n user messages and n-1 replies, so the total is u*n(n+1)/2 + a*n(n-1)/2."""
    return user_tokens * turns * (turns + 1) // 2 + reply_tokens * turns * (turns - 1) // 2


# ---------------------------------------------------------------- compare and decide
def compare(spec: Spec, models: list[Model]) -> list[dict]:
    """One row per model, cheapest per month first."""
    return sorted((estimate(spec, m) for m in models), key=lambda r: r["per_month"])


def verdict(row: dict, budget_month: float | None = None, max_latency_s: float | None = None) -> tuple[bool, str]:
    """(ok, reasons). A row passes only if it fits the context and meets every limit that is given."""
    problems = []
    if not row["fits_context"]:
        problems.append("does not fit the context window")
    if budget_month is not None and row["per_month"] > budget_month:
        problems.append(f"over budget (${row['per_month']:,.2f} > ${budget_month:,.2f})")
    if max_latency_s is not None and row["latency_s"] > max_latency_s:
        problems.append(f"too slow ({row['latency_s']:.1f}s > {max_latency_s}s)")
    return (not problems), ("ok" if not problems else "; ".join(problems))


def format_table(rows: list[dict], budget_month=None, max_latency_s=None) -> str:
    head = f"{'model':<10}{'$/call':>10}{'$/day':>10}{'$/month':>11}{'latency s':>11}{'peak conc.':>11}  verdict"
    lines = [head]
    for r in rows:
        ok, why = verdict(r, budget_month, max_latency_s)
        lines.append(f"{r['model']:<10}{r['per_call']:>10.5f}{r['per_day']:>10.2f}{r['per_month']:>11,.2f}"
                     f"{r['latency_s']:>11.2f}{r['peak_concurrent']:>11.2f}  {'PASS' if ok else 'FAIL'}: {why}")
    return "\n".join(lines)


# ---------------------------------------------------------------- command line
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Estimate the cost and latency of an LLM feature.")
    ap.add_argument("spec", help="JSON file with the fields of Spec")
    ap.add_argument("--models", required=True, help="TOML file with [models.<name>] tables")
    ap.add_argument("--budget", type=float, help="monthly budget in dollars")
    ap.add_argument("--max-latency", type=float, help="latency limit in seconds")
    args = ap.parse_args(argv)
    with open(args.spec, encoding="utf-8") as f:
        spec = Spec(**json.load(f))
    models, illustrative = load_models(args.models)
    rows = compare(spec, models)
    if illustrative:
        print("WARNING: the prices in this models file are ILLUSTRATIVE placeholders. Put real prices in it before deciding anything.\n")
    print(f"input {spec.input_tokens} tokens + output {spec.output_tokens} tokens per call, {spec.calls_per_day} calls/day\n")
    print(format_table(rows, args.budget, args.max_latency))
    passing = [r for r in rows if verdict(r, args.budget, args.max_latency)[0]]
    print(f"\n{len(passing)} of {len(rows)} models meet the limits" + (f"; cheapest: {passing[0]['model']}" if passing else ""))
    return 0 if passing else 1


if __name__ == "__main__":
    sys.exit(main())
''', encoding="utf-8")
print("llmcost.py:", len((proj / "llmcost.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
llmcost.py: 170 lines
```

### 8.3 Tests

Every assertion names the likely mistake. The hand-checked numbers come from the examples of sections 3 and 5.

```python run
(proj / "test_llmcost.py").write_text(r'''import json
import subprocess
import sys

import pytest

import llmcost as lc

M = lc.Model("m", input_per_m=1.0, output_per_m=5.0, ttft_s=0.5, tokens_per_s=50.0, context_window=10_000, cached_input_per_m=0.1)


def test_estimate_tokens_methods():
    assert lc.estimate_tokens("") == 0, "empty text is zero tokens"
    assert lc.estimate_tokens("abcd") == 1 and lc.estimate_tokens("abcde") == 2, "chars4 rounds UP: 5 characters need 2 tokens"
    assert lc.estimate_tokens("one two three", "words") == 4, "3 words / 0.75 = 4 tokens"
    assert lc.estimate_tokens("नमस्ते", "bytes") == 18, "this Hindi word is 18 UTF-8 bytes"
    with pytest.raises(ValueError):
        lc.estimate_tokens("x", "magic")


def test_token_range_is_ordered_and_bytes_dominate_for_hindi():
    low, expected, high = lc.token_range("नमस्ते, आप कैसे हैं?")
    assert low <= expected <= high, "low <= expected <= high"
    assert high == 50, "20 characters of Hindi are 50 bytes: the byte count is the upper bound"


def test_call_cost_hand_checked():
    assert lc.call_cost(M, 1000, 500) == pytest.approx((1000 * 1 + 500 * 5) / 1e6), "input and output are priced separately, per MILLION tokens"
    assert lc.call_cost(M, 1000, 0, cached_tokens=1000) == pytest.approx(1000 * 0.1 / 1e6), "cached tokens use the cached rate"
    assert lc.call_cost(M, 1000, 100, cached_tokens=500) < lc.call_cost(M, 1000, 100), "caching must make the call cheaper"


def test_call_cost_rejects_impossible_cache():
    with pytest.raises(ValueError):
        lc.call_cost(M, 100, 10, cached_tokens=200)


def test_cached_without_cached_price_costs_the_same():
    no_cache = lc.Model("n", 1.0, 5.0, 0.5, 50.0, 10_000)
    assert lc.call_cost(no_cache, 1000, 100, cached_tokens=900) == lc.call_cost(no_cache, 1000, 100), "no cached rate means full price"


def test_latency_formula():
    assert lc.call_latency(M, 100) == pytest.approx(0.5 + 100 / 50), "latency = time to first token + output tokens / speed = 2.5 s"


def test_estimate_monthly_hand_checked():
    spec = lc.Spec(user_tokens=1000, output_tokens=500, calls_per_day=1000)
    e = lc.estimate(spec, M)
    assert e["per_call"] == pytest.approx(0.0035), "(1000 x 1 + 500 x 5) / 1e6 = 0.0035"
    assert e["per_month"] == pytest.approx(0.0035 * 1000 * 30), "monthly = per call x calls per day x 30"


def test_retry_overhead_scales_cost():
    base = lc.estimate(lc.Spec(user_tokens=1000, output_tokens=100, calls_per_day=10), M)["per_call"]
    more = lc.estimate(lc.Spec(user_tokens=1000, output_tokens=100, calls_per_day=10, retry_overhead=0.5), M)["per_call"]
    assert more == pytest.approx(base * 1.5), "50% retries make each logical call cost 1.5x"


def test_littles_law_peak_concurrency():
    fast = lc.Model("f", 1, 5, ttft_s=0.0, tokens_per_s=50.0, context_window=10_000)
    spec = lc.Spec(user_tokens=10, output_tokens=100, calls_per_day=86_400, peak_factor=10)     # 1 call/s average, 10/s peak
    e = lc.estimate(spec, fast)
    assert e["peak_per_s"] == pytest.approx(10.0), "86,400 calls a day is 1 per second; peak factor 10 gives 10 per second"
    assert e["latency_s"] == pytest.approx(2.0)
    assert e["peak_concurrent"] == pytest.approx(20.0), "rate x time = 10/s x 2 s = 20 calls in flight"


def test_context_fit():
    spec = lc.Spec(system_tokens=9_000, user_tokens=900, output_tokens=200, calls_per_day=1)
    assert lc.estimate(spec, M)["fits_context"] is False, "9,900 input + 200 output = 10,100 > 10,000: the reply must fit too"
    assert lc.estimate(lc.Spec(user_tokens=100, output_tokens=100, calls_per_day=1), M)["fits_context"] is True


def test_full_history_closed_form_matches_brute_force():
    def brute(turns, u, a):
        return sum(n * u + (n - 1) * a for n in range(1, turns + 1))
    assert lc.full_history_tokens(3, 10, 20) == 120, "10+0 + 20+20 + 30+40 = 120"
    for turns in (1, 2, 7, 20):
        assert lc.full_history_tokens(turns, 64, 154) == brute(turns, 64, 154), f"closed form disagrees at {turns} turns"


def test_history_cost_is_quadratic():
    assert lc.full_history_tokens(40, 60, 150) > 3.5 * lc.full_history_tokens(20, 60, 150), "doubling the turns should roughly quadruple the bill"


def test_cached_share_validation():
    with pytest.raises(ValueError):
        lc.estimate(lc.Spec(user_tokens=10, calls_per_day=1, cached_share=1.5), M)


def test_compare_sorts_by_monthly_cost_and_verdict_reasons():
    cheap = lc.Model("cheap", 1, 5, 0.3, 120.0, 100_000)
    dear = lc.Model("dear", 15, 75, 1.0, 40.0, 100_000)
    spec = lc.Spec(user_tokens=2200, output_tokens=250, calls_per_day=2000)
    rows = lc.compare(spec, [dear, cheap])
    assert [r["model"] for r in rows] == ["cheap", "dear"], "rows must be cheapest first"
    ok, why = lc.verdict(rows[1], budget_month=300, max_latency_s=5)
    assert not ok and "over budget" in why and "too slow" in why, "the dear model breaks both limits and the reason must say so"
    assert lc.verdict(rows[0], budget_month=300, max_latency_s=5)[0], "the cheap model passes both"


def write_files(tmp_path, illustrative=True):
    (tmp_path / "models.toml").write_text(
        ("illustrative = true\n" if illustrative else "") +
        "[models.small]\ninput_per_m = 1.0\noutput_per_m = 5.0\nttft_s = 0.3\ntokens_per_s = 120\ncontext_window = 16000\n"
        "[models.large]\ninput_per_m = 15.0\noutput_per_m = 75.0\nttft_s = 1.0\ntokens_per_s = 40\ncontext_window = 200000\n", encoding="utf-8")
    (tmp_path / "spec.json").write_text(json.dumps({"system_tokens": 600, "context_tokens": 1500, "user_tokens": 100,
                                                    "output_tokens": 250, "calls_per_day": 2000}), encoding="utf-8")


def test_load_models_validates(tmp_path):
    write_files(tmp_path)
    models, illustrative = lc.load_models(tmp_path / "models.toml")
    assert [m.name for m in models] == ["small", "large"] and illustrative is True
    (tmp_path / "bad.toml").write_text("[models.x]\ninput_per_m = 1.0\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing the field"):
        lc.load_models(tmp_path / "bad.toml")
    (tmp_path / "neg.toml").write_text("[models.x]\ninput_per_m = -1\noutput_per_m = 1\nttft_s = 1\ntokens_per_s = 1\ncontext_window = 10\n", encoding="utf-8")
    with pytest.raises(ValueError, match="negative"):
        lc.load_models(tmp_path / "neg.toml")


def run_cli(tmp_path, *extra):
    return subprocess.run([sys.executable, "-I", lc.__file__, str(tmp_path / "spec.json"), "--models", str(tmp_path / "models.toml"), *extra],
                          capture_output=True, text=True, encoding="utf-8")


def test_cli_passes_warns_and_exits_zero(tmp_path):
    write_files(tmp_path)
    r = run_cli(tmp_path, "--budget", "500", "--max-latency", "5")
    assert r.returncode == 0, "at least one model meets the limits, so the exit code must be 0: " + r.stdout
    assert "ILLUSTRATIVE" in r.stdout, "placeholder prices must be flagged in the output"
    assert "cheapest: small" in r.stdout


def test_cli_exits_one_when_nothing_qualifies(tmp_path):
    write_files(tmp_path, illustrative=False)
    r = run_cli(tmp_path, "--budget", "1", "--max-latency", "0.1")
    assert r.returncode == 1, "no model can meet $1 a month and 0.1 s, so the exit code must be 1"
    assert "ILLUSTRATIVE" not in r.stdout, "the warning must only appear when the file says illustrative = true"
''', encoding="utf-8")
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "test_llmcost.py"], cwd=proj, capture_output=True, text=True, encoding="utf-8")
print(res.stdout.strip().splitlines()[-1] if res.stdout.strip() else res.stderr[-400:])
if res.returncode:
    print(res.stdout[-2500:])
```
```text
17 passed in 0.21s
```

### 8.4 Run the calculator

Write a models file with placeholder prices, a spec for the support-reply drafter of section 5, and run the command-line tool the way you would in a design review.

```python run
(proj / "models.toml").write_text('''# ILLUSTRATIVE placeholders. Replace with the current prices and limits from your provider's pages.
illustrative = true

[models.small]
input_per_m = 1.0
output_per_m = 5.0
cached_input_per_m = 0.10
ttft_s = 0.3
tokens_per_s = 120
context_window = 16000

[models.medium]
input_per_m = 3.0
output_per_m = 15.0
cached_input_per_m = 0.30
ttft_s = 0.5
tokens_per_s = 70
context_window = 200000

[models.large]
input_per_m = 15.0
output_per_m = 75.0
cached_input_per_m = 1.50
ttft_s = 1.0
tokens_per_s = 40
context_window = 200000
''', encoding="utf-8")
(proj / "spec.json").write_text(json.dumps({"system_tokens": 600, "context_tokens": 1500, "user_tokens": 100, "output_tokens": 250,
                                            "calls_per_day": 2000, "retry_overhead": 0.05, "peak_factor": 8}, indent=2), encoding="utf-8")
for label, extra in [("budget $300, latency 5 s", ["--budget", "300", "--max-latency", "5"]),
                      ("budget $100, latency 1 s (impossible)", ["--budget", "100", "--max-latency", "1"])]:
    out = subprocess.run([sys.executable, "-I", "llmcost.py", "spec.json", "--models", "models.toml", *extra], cwd=proj, capture_output=True, text=True, encoding="utf-8")
    print(f"$ llmcost spec.json --models models.toml {' '.join(extra)}      # {label}")
    print(out.stdout.rstrip())
    print(f"(exit status {out.returncode})\n")
```
```text
$ llmcost spec.json --models models.toml --budget 300 --max-latency 5      # budget $300, latency 5 s
WARNING: the prices in this models file are ILLUSTRATIVE placeholders. Put real prices in it before deciding anything.

input 2200 tokens + output 250 tokens per call, 2000 calls/day

model         $/call     $/day    $/month  latency s peak conc.  verdict
small        0.00362      7.25     217.35       2.38       0.44  PASS: ok
medium       0.01087     21.73     652.05       4.07       0.75  FAIL: over budget ($652.05 > $300.00)
large        0.05434    108.67   3,260.25       7.25       1.34  FAIL: over budget ($3,260.25 > $300.00); too slow (7.2s > 5.0s)

1 of 3 models meet the limits; cheapest: small
(exit status 0)

$ llmcost spec.json --models models.toml --budget 100 --max-latency 1      # budget $100, latency 1 s (impossible)
WARNING: the prices in this models file are ILLUSTRATIVE placeholders. Put real prices in it before deciding anything.

input 2200 tokens + output 250 tokens per call, 2000 calls/day

model         $/call     $/day    $/month  latency s peak conc.  verdict
small        0.00362      7.25     217.35       2.38       0.44  FAIL: over budget ($217.35 > $100.00); too slow (2.4s > 1.0s)
medium       0.01087     21.73     652.05       4.07       0.75  FAIL: over budget ($652.05 > $100.00); too slow (4.1s > 1.0s)
large        0.05434    108.67   3,260.25       7.25       1.34  FAIL: over budget ($3,260.25 > $100.00); too slow (7.2s > 1.0s)

0 of 3 models meet the limits
(exit status 1)
```

Notice what the second run teaches: when **no** model meets the limits, the tool says so with a non-zero exit status, and the table shows *why* each fails (cost, speed or both). That is the useful output of an estimate: not "the answer is $652", but "no option satisfies these two requirements, so change the design, the budget or the target".

### 8.5 Extensions

1. **Real token counts.** Add a `--tokenizer` option that uses the provider's token-counting library when you install it, and falls back to the estimate, printing which one was used.
2. **Read prompts from files.** Let the spec point at text files and count the tokens of each (system prompt, retrieved context sample) with `token_range`, printing low, expected and high costs, so the verdict has an error bar.
3. **History strategies.** Add the window and summary strategies of section 3 to `full_history_tokens` and show the saving for a given chat length.
4. **Routing.** Add the cascade formula of section 6.2: given an escalation rate, the cost and the break-even point.
5. **Real measurements.** When you have a key, log real usage numbers and compare them with the estimate: how far off were your assumptions? A feedback loop is how estimates get good.

## 9. Common traps

1. **Estimating from words, not tokens** (2.4). Count tokens for your own data; non-English text, code and numbers cost more.
2. **Ignoring `stop_reason`** (1.2). A reply cut by `max_tokens` looks fine and breaks parsers.
3. **Forgetting that the API is stateless** (1, 3). Every call re-sends and re-bills the history; a chat's cost grows with the square of its length.
4. **A giant system prompt on a high-traffic feature** (3.3, 5.4). It is billed on every call; trim it or cache it.
5. **Output tokens are the expensive and the slow part** (5.1). Ask for short replies, set `max_tokens`, and stream if the user is waiting.
6. **Estimating the average, not the peak** (5.2). Capacity and rate limits are about the peak: use peak factor and Little's law.
7. **Hard-coding prices.** They change; keep them in a config file with a date and a source, and never present placeholder numbers as real.
8. **Believing low temperature means true** (4.5, 7.6). It means consistent.
9. **Choosing a model from a leaderboard** (6.1). Evaluate on your own examples and compute cost per correct answer.
10. **Trusting the model for exact tasks** (7.2). Arithmetic, counting, sorting and lookups belong to code.
11. **No verification of facts that can be checked** (7.3). Existence of functions, columns, URLs, quotes and numeric ranges can be tested in microseconds.
12. **Unbounded retries** (7.4). Each retry re-bills the conversation; cap them and track the retry rate.
13. **Sending secrets or personal data to a provider** (6.3, 7.5). Check the data policy first; redact what you can.
14. **No fallback when the model fails or is too slow** (6.3). Keep your own interface so you can switch, time out and degrade gracefully.

## 10. Summary

- An LLM is a **stateless function** from messages to text, sampled one token at a time, billed per input and output token. A reply is complete only if `stop_reason` says so. **You** manage history, and re-pay for it every call.
- **Tokens** are subword pieces from a trained vocabulary. **BPE** merges frequent adjacent pairs; a tokenizer is cheap on text like its training data and costly on rare scripts, code and long numbers. Count tokens for your real inputs; use the provider's counter for exact numbers.
- The **context window** is shared by input and reply. A chat that re-sends its history costs **quadratically** in its length; keep it in check with sliding windows, summaries, retrieval, pinned essentials and input caps.
- **Sampling**: softmax turns scores into probabilities; **temperature** reshapes them; **top-k** and **top-p** cut the tail. Greedy decoding is deterministic and can loop; randomness gives variety and fluent nonsense. Low temperature gives consistency, not truth.
- **Estimate before you build**: tokens per call, price per million tokens (output costs more), latency = first token + output tokens / speed, traffic, **peak** and Little's law, then compare with a budget and a latency target, with a sensitivity analysis.
- **Choose by measurement**: a small evaluation set of your own, cost per correct answer, and routing by break-even (`e < 1 - c_small / c_big`) when a cheap model can tell when it is unsure.
- **Models are bad at** exact arithmetic, counting, fresh facts, long conflicting instructions and truthfulness. The defences are **grounding, tools for exact work, verification by code, bounded retries and human review** for high stakes.
- The project is a small **tested calculator** whose output is a verdict you can put in a design review, and whose config says honestly when its prices are placeholders.

**Self-check (answer without looking back):**

1. Name three things a call to an LLM API contains and three things it returns that a builder must pay attention to.
2. Why does a 40-turn chat cost about four times as much input as a 20-turn chat?
3. Your feature needs 20,000 input tokens and 500 output tokens per call, 10,000 calls a day, at $2 per million input and $10 per million output. Monthly cost?
4. A model gives a fluent answer citing a function you do not recognise. What is the quickest check, and why must you not rely on the tone of the answer?
5. When is a small-first cascade cheaper than always using the large model?
6. Why is "set temperature to 0" an incomplete fix for unreliable output?
7. What did this chapter *not* measure, and how did it say so?

<details><summary>Answer</summary>

1. Sent: the model name, the messages (and system prompt), `max_tokens` and sampling settings. Returned: the text, the **usage** (input and output tokens: the bill), and the **`stop_reason`** (finished or cut off); also watch latency.
2. Call *n* sends everything said so far, so its input grows linearly with *n*; the total over *n* turns is the sum 1 + 2 + ... + n, which grows with *n squared*. Doubling *n* multiplies the total by about four.
3. Per call: 20,000 x 2/1e6 = $0.04 input, 500 x 10/1e6 = $0.005 output, total $0.045. Per day: 10,000 x 0.045 = $450. Per month: **$13,500**. The input side is 89 % of the cost, so trimming the 20,000-token input (or caching it) is the lever.
4. Check by code that it exists (import and `hasattr`, search the docs). Tone is not evidence: models produce fluent text whether or not the content is true.
5. When the escalation rate `e` is below `1 - c_small / c_big`: the cascade costs `c_small + e x c_big` per call, against `c_big` for always-large. It also has to keep accuracy at your bar, which needs real evaluation data.
6. Temperature 0 gives the most likely continuation every time, so it is consistent but may be consistently wrong. You still need grounding, verification and tests; hosted models may also not be bit-for-bit deterministic.
7. It did not call any real LLM. Claims about real model behaviour are marked *(general knowledge)*, prices and speeds are labelled illustrative, and the cascade accuracies are labelled as assumptions. Every printed number comes from a real run of code in this chapter.

</details>
