# Chapter 7 (LLM): Shipping LLM Applications

A notebook that answers a question is not a product. A product answers a thousand questions an hour, from people who are not you, while the provider has a bad afternoon, the bill grows, a new model version arrives with a different personality, and your manager asks "how much did that cost last week, and is it getting slower?". **Shipping** is everything between "it works on my machine" and "it works for everyone, and I can prove it and fix it when it does not".

The syllabus outcome is: **run an LLM service with cost and latency tracked per request**. The project is to **deploy your RAG system with monitoring**.

You will learn, in this order:

1. What changes when you ship: the lifecycle of one request, and what must be true in production.
2. The **provider side**: pinned model versions, price and speed, and how to survive timeouts, outages and slowdowns (llm.02, in miniature).
3. **Caching responses**: what to key on, when an old answer is still right, and the cache stampede.
4. **Observability**: structured logs, **metrics** (counters, latency histograms, percentiles), **traces** (where did the time go?), cost per request, alerts and a dashboard.
5. **Serving with FastAPI**: validation, request ids, rate limiting, health and readiness, error mapping.
6. **Handling model and provider changes**: pinning, shadow comparison before anyone sees a new model, canary rollout with sticky users, rollback, and noticing silent drift.
7. **Operating it**: an incident drill (slowdown, outage, recovery), capacity planning, and deployment.
8. The project, with 47 tests.

Prerequisites: llm.04 (evaluation and gates), llm.02 (retries, timeouts, fallbacks), swe.05 (FastAPI) and swe.09 (deployment, CI).

> **How this chapter is built, and what it does NOT contain.** *No real provider, no real model, no real server is started.* The model endpoints are **`FakeBackend`** objects with a price, a speed and a *behaviour* per version, and **time is virtual**: a model call "takes" 0.77 seconds by advancing a `VirtualClock`, and a test can serve a day of traffic in a blink with every latency exactly reproducible. The FastAPI service is exercised in-process with `TestClient`, as in swe.05. The Docker and process-manager commands in section 7 are **shown for reference and not run** (they need a daemon and a network, as in ml.06).
>
> What is real: the cache, the metrics, the traces, the cost accounting, the alert rules, the circuit breaker, the router, the release gate, the HTTP service and the tests. What is not: the provider's behaviour. Prices and speeds are **illustrative placeholders** (put your provider's real figures in `models.toml`), and real providers fail in messier ways than a flag in a fake. Claims about real providers are marked *(general knowledge)*.
>
> Variations that would only repeat a lesson are **question → worked answer** boxes. Sections carry optional **Visualise it** prompts you can paste into any AI chat; the course never depends on them. The chapter runs in a few seconds.

```python run
import sys, platform, json, math, re, time, pathlib, tempfile, subprocess, collections, random, threading
from pathlib import Path
print("python  ", sys.version.split()[0], "|", platform.system())
ws = pathlib.Path(tempfile.mkdtemp(prefix="llm07_ws_"))        # every file this chapter creates lives here
pkg = ws / "pkg"
pkg.mkdir()
sys.path.insert(0, str(pkg))                                   # so `import backend` finds the files we write below
print("workspace:", ws.name)
```
```text
python   3.14.4 | Linux
workspace: llm07_ws_jgxy83t_
```

## Table of contents

1. [What changes when you ship](#1-what-changes-when-you-ship)
2. [The provider side: models, versions, failures](#2-the-provider-side-models-versions-failures)
3. [Caching responses](#3-caching-responses)
4. [Observability](#4-observability)
5. [Serving with FastAPI](#5-serving-with-fastapi)
6. [Handling model and provider changes](#6-handling-model-and-provider-changes)
7. [Operating it](#7-operating-it)
8. [Project: deploy the RAG system with monitoring](#8-project-deploy-the-rag-system-with-monitoring)
9. [Common traps](#9-common-traps)
10. [Summary](#10-summary)

## 1. What changes when you ship

### 1.1 The life of one request

```
 client --HTTP--> [ validate | rate limit | request id ]
                       |
                       v
                  [ cache lookup ] --hit--> answer (fast, free)
                       | miss
                       v
                  [ retrieve ] -> [ build prompt ] -> [ model call (retries, timeout, fallback) ] -> [ validate answer ]
                       |                                                                                  |
                       +---------------- trace spans, metrics, one JSON log line, cost -------------------+
                       v
                  answer + request id + cost + latency
```

Everything you built in earlier chapters is one box of this picture. Shipping adds the other boxes, and each exists because of a way production differs from a notebook:

| In production | So you need |
|---|---|
| many requests, many users | validation, **rate limits**, a stable **API contract** |
| the provider is slow, down or changed | **timeouts, retries, a circuit breaker, a fallback**, pinned model versions |
| every call costs money | **caching**, per-request **cost tracking**, **budgets and alerts** |
| you cannot watch it | **logs, metrics, traces**, **dashboards and alerts** |
| the model will be replaced | a **release process**: compare, canary, roll back |
| it must keep running | **health and readiness**, graceful deployment |

### 1.2 What "tracked per request" means

The outcome says *cost and latency tracked per request*. Concretely, for every request your service can answer: **which model version served it, how many input and output tokens, what it cost, how long it took in total and how long in each step, whether the cache answered, whether a fallback was used, and whether the answer was cited or refused**. With that one record you can answer almost every operational question: "why was it slow?", "why was Tuesday expensive?", "did the new model change anything?". Sections 4 and 5 build that record.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one request as a horizontal timeline with five coloured segments: 'validate' (tiny), 'cache lookup' (tiny), 'retrieve' (4 ms), 'model call' (770 ms, the long one) and 'validate answer' (tiny). Above the timeline, show the data attached to the request: request id, model version, tokens in/out, cost in dollars. Below it, draw three outputs fanning out: 'a JSON log line', 'metric counters and a latency histogram', 'a trace waterfall', all stamped with the same request id."

### 1.3 Try it

1. A user reports "the assistant was slow yesterday afternoon". What per-request data lets you find out why?
2. Why is the provider's published speed not enough to promise your users a latency?
3. What is the difference between knowing a request failed and knowing *why*?

<details><summary>Answer</summary>

1. Per-request latency broken down by step (retrieve, model call, validate), the model version, whether a retry, a fallback or the cache was involved, and the time of the request. With a trace per request you can see whether the model call was slow, the retrieval was slow, or retries piled up.
2. Your latency is retrieval plus prompt building plus the model call plus retries plus queueing plus validation, under your own load; a provider's quoted speed covers only one step, in good conditions, and says nothing about the tail (the p95 and p99 your unluckiest users see).
3. A failure count says something is wrong; the log line and trace (status, error, which step, which model, how many attempts) say what to fix. Counters tell you *that*, traces and logs tell you *why*.

</details>

## 2. The provider side: models, versions, failures

### 2.1 A model is an id, a version, a price and a speed

Treat every model as a **pinned, versioned dependency** with known properties. A `ModelSpec` carries the model name, an **exact version**, the price per million input and output tokens, the time to first token and the output speed (all from llm.01's cost model). The fake backends here add one more property you must plan for in real life: **behaviour**. Different versions of "the same" model answer differently: more verbose, cheaper, faster, quicker to refuse, worse at citing. We create three behaviours on purpose so that section 6 has something real to catch.

Three small files: virtual time, the demo library from earlier chapters (so the chapter runs alone), and the backends.

```python run
(pkg / "vclock.py").write_text(r'''"""vclock: virtual time. Everything that 'takes time' (a model call, a retry wait) advances this clock instead of really waiting,
so a test can serve a day of traffic in milliseconds and every latency is exactly reproducible."""
from __future__ import annotations

import threading


class VirtualClock:
    def __init__(self, start: float = 0.0):
        self._now, self._lock = start, threading.Lock()

    def time(self) -> float:
        with self._lock:
            return self._now

    def sleep(self, seconds: float) -> None:
        with self._lock:
            self._now += max(0.0, seconds)
''', encoding="utf-8")
print("wrote vclock.py:", 18, "lines")
```
```text
wrote vclock.py: 18 lines
```

```python run
(pkg / "kestrel_docs.py").write_text(r'''"""kestrel_docs: a small FICTIONAL document library (Kestrel Outdoor Gear) and test questions with known answers.

Every fact below is invented for this chapter. Each document is a list of sections; each section is (heading, text).
QUESTIONS lists (question, document id, a phrase the answer sentence must contain); questions with doc id None are
deliberately NOT answerable from the library.
"""

DOCS = [
    {"id": "returns-policy", "title": "Returns and Refunds Policy", "type": "policy", "year": 2025, "sections": [
        ("Return window", "You may return unused items in their original packaging within 30 days of delivery. Items that show signs of use cannot be accepted."),
        ("Refunds", "Approved returns are reimbursed to the original payment method within 7 business days of arrival at our warehouse. Refunds are never paid in cash."),
        ("Exceptions", "Items marked Final Sale cannot be returned. Return shipping is free for defective items; for any other return the customer pays a $6.95 shipping label.")]},
    {"id": "warranty", "title": "Warranty Terms", "type": "policy", "year": 2024, "sections": [
        ("Coverage", "Kestrel tents carry a 5-year limited warranty on frames and fabric. Sleeping bag zips are covered for 2 years. The warranty covers manufacturing defects, not normal wear or damage from misuse."),
        ("Making a claim", "To make a warranty claim, open a case in the support portal and include your order number and photos of the problem. We decide between repair and replacement within 10 days.")]},
    {"id": "shipping", "title": "Shipping and Delivery", "type": "policy", "year": 2025, "sections": [
        ("Domestic", "Standard shipping takes 3-5 business days. Express shipping takes 1-2 business days and is not available to PO boxes. Orders over $75 ship free with standard shipping."),
        ("International", "International orders take 8-14 business days. Customs duties and import taxes are the buyer's responsibility.")]},
    {"id": "tent-aurora-3", "title": "Aurora 3 Tent", "type": "product", "year": 2025, "sections": [
        ("Overview", "The Aurora 3 is a 3-person, 3-season tent weighing 2.9 kg. Its aluminium poles let one person pitch it in about 6 minutes."),
        ("Specifications", "Packed size is 48 x 16 cm. The fly has a waterproof rating of 3000 mm. A footprint groundsheet is sold separately.")]},
    {"id": "tent-summit-4", "title": "Summit 4 Tent", "type": "product", "year": 2024, "sections": [
        ("Overview", "The Summit 4 is a 4-person, 4-season expedition tent built for snow and high wind. It weighs 4.6 kg and uses a reinforced pole frame."),
        ("Specifications", "The fly has a waterproof rating of 5000 mm. The tent is rated for a snow load of 40 cm.")]},
    {"id": "sleeping-bag-ember", "title": "Ember Sleeping Bag", "type": "product", "year": 2025, "sections": [
        ("Warmth", "The Ember has a comfort rating of -5 C and is filled with 800 fill power goose down. It weighs 1.2 kg and has a hood and a draft tube along the zip."),
        ("Washing", "Wash the Ember in a front-loading machine with a down-specific detergent and dry it on low heat with clean tennis balls.")]},
    {"id": "care-guide", "title": "Gear Care Guide", "type": "guide", "year": 2023, "sections": [
        ("Tents", "Never machine wash a tent. Clean it with mild soap and lukewarm water, and let it dry completely before storage to prevent mildew."),
        ("Waterproofing", "Re-apply a waterproofing spray to the tent fly every season, or whenever water stops beading on the fabric.")]},
    {"id": "sizing-guide", "title": "Jacket Sizing Guide", "type": "guide", "year": 2024, "sections": [
        ("Choosing a size", "Measure your chest in centimetres and compare it with the chart. If you are between two sizes, size up so there is room for layers underneath.")]},
    {"id": "rain-jacket-nimbus", "title": "Nimbus Rain Jacket", "type": "product", "year": 2025, "sections": [
        ("Details", "The Nimbus is a 2.5 layer rain jacket weighing only 310 g. It has pit zips for ventilation, is made from recycled fabric and fits true to size.")]},
    {"id": "privacy-policy", "title": "Privacy Policy", "type": "policy", "year": 2025, "sections": [
        ("Data we keep", "We keep order records for 7 years to meet tax law. We never sell personal data. You can opt out of marketing emails at any time using the link in each email."),
        ("Contact", "Questions about your data can be sent to the privacy team at privacy@kestrel.example.")]},
    {"id": "loyalty-program", "title": "Trail Points Loyalty Programme", "type": "policy", "year": 2025, "sections": [
        ("Earning", "Members earn 1 point per $1 spent. Every 500 points can be exchanged for a $5 reward. Members get early access to seasonal sales."),
        ("Expiry", "Points expire after 18 months without any purchase.")]},
    {"id": "faq-general", "title": "Frequently Asked Questions", "type": "faq", "year": 2025, "sections": [
        ("Contact", "Support chat is open 8 am to 8 pm, Monday to Saturday. Gift cards never expire."),
        ("Prices and repairs", "We will match a competitor's advertised price within 14 days of purchase. A broken zip can be repaired by our workshop for a flat fee of $12.")]},
]


# Look-alike products make retrieval harder: the same sentence shapes with different names and numbers.
_TENTS = [("Aurora 2", "aurora-2", 2, "3-season", 2.1, 2000), ("Summit 2", "summit-2", 2, "4-season", 3.4, 4000), ("Summit 3", "summit-3", 3, "4-season", 4.0, 4500),
          ("Dune 4", "dune-4", 4, "3-season", 3.8, 3000)]
_BAGS = [("Cinder", "sleeping-bag-cinder", 0, 1.0, 650), ("Spark", "sleeping-bag-spark", 5, 0.9, 600), ("Frost", "sleeping-bag-frost", -15, 1.9, 850)]
_JACKETS = [("Squall", "rain-jacket-squall", 2.5, 340), ("Drizzle", "rain-jacket-drizzle", 2.0, 280), ("Gale", "rain-jacket-gale", 3.0, 520)]
for _name, _id, _p, _season, _kg, _mm in _TENTS:
    DOCS.append({"id": f"tent-{_id}", "title": f"{_name} Tent", "type": "product", "year": 2024, "sections": [
        ("Overview", f"The {_name} is a {_p}-person, {_season} tent weighing {_kg} kg."),
        ("Specifications", f"The fly has a waterproof rating of {_mm} mm.")]})
for _name, _id, _c, _kg, _fp in _BAGS:
    DOCS.append({"id": _id, "title": f"{_name} Sleeping Bag", "type": "product", "year": 2024, "sections": [
        ("Warmth", f"The {_name} has a comfort rating of {_c} C and is filled with {_fp} fill power down. It weighs {_kg} kg.")]})
for _name, _id, _layers, _g in _JACKETS:
    DOCS.append({"id": _id, "title": f"{_name} Rain Jacket", "type": "product", "year": 2024, "sections": [
        ("Details", f"The {_name} is a {_layers} layer rain jacket weighing {_g} g. It fits true to size.")]})

QUESTIONS = [
    ("How long do I have to return an unused item?", "returns-policy", "30 days"),
    ("Can I get my money back for a sale item?", "returns-policy", "Final Sale"),
    ("How long does a refund take to arrive?", "returns-policy", "7 business days"),
    ("Who pays for return postage when the item is faulty?", "returns-policy", "free for defective"),
    ("How long is the warranty on tents?", "warranty", "5-year"),
    ("What do I need to make a warranty claim?", "warranty", "order number"),
    ("Does free delivery apply to my $80 order?", "shipping", "over $75"),
    ("How many days does express shipping take?", "shipping", "1-2 business days"),
    ("Who pays customs duties on international orders?", "shipping", "Customs duties"),
    ("How much does the Aurora 3 tent weigh?", "tent-aurora-3", "2.9 kg"),
    ("What is the waterproof rating of the Summit 4?", "tent-summit-4", "5000 mm"),
    ("Which tent can handle snow and high wind?", "tent-summit-4", "snow"),
    ("How warm is the Ember sleeping bag?", "sleeping-bag-ember", "-5 C"),
    ("Can I put my tent in the washing machine?", "care-guide", "Never machine wash"),
    ("How often should I re-waterproof a tent?", "care-guide", "every season"),
    ("What size should I buy if I am between two sizes?", "sizing-guide", "size up"),
    ("How heavy is the Nimbus rain jacket?", "rain-jacket-nimbus", "310 g"),
    ("How long do you keep my order data?", "privacy-policy", "7 years"),
    ("How many Trail Points do I earn per dollar?", "loyalty-program", "1 point per $1"),
    ("When do my loyalty points expire?", "loyalty-program", "18 months"),
    ("What hours is the customer support chat open?", "faq-general", "8 am"),
    ("Do gift cards expire?", "faq-general", "never expire"),
    ("Will you match a competitor's price?", "faq-general", "match a competitor"),
    ("How much does a zip repair cost?", "faq-general", "$12"),
    # not answerable from this library
    ("Do you sell climbing ropes?", None, None),
    ("Who is the chief executive of Kestrel?", None, None),
    ("Does the Aurora 3 come in red?", None, None),
    ("How long does shipping to Antarctica take?", None, None),
    ("How much does the Summit 4 cost?", None, None),
    ("Is the Ember sleeping bag vegan?", None, None),
    ("Do you have a shop in Berlin?", None, None),
    ("What is a good recipe for chocolate cake?", None, None),
]


# Paraphrased questions: they share (almost) no content words with the passage that answers them.
HARD_QUESTIONS = [
    ("Is there a fee to send back a broken product?", "returns-policy", "free for defective"),
    ("Do I pay anything for delivery if I spend more than eighty dollars?", "shipping", "over $75"),
    ("How do I stop my shelter from going mouldy?", "care-guide", "mildew"),
    ("How do I get compensated when I send gear back?", "returns-policy", "reimbursed"),
    ("At what temperature will I stay comfortable in the Ember?", "sleeping-bag-ember", "-5 C"),
    ("Can I earn rewards for shopping with you?", "loyalty-program", "Members earn"),
    ("Is anyone available to chat at the weekend?", "faq-general", "Monday to Saturday"),
    ("Will you fix a snapped pole for free?", "warranty", "frames and fabric"),
    ("Can I throw my down bag in the dryer?", "sleeping-bag-ember", "dry it on low heat"),
    ("Which of your shelters suits a blizzard?", "tent-summit-4", "snow"),
    ("Who do I write to about my personal information?", "privacy-policy", "privacy@kestrel"),
    ("What does a mended zipper set me back?", "faq-general", "$12"),
]
''', encoding="utf-8")
print("wrote kestrel_docs.py:", 114, "lines")
```
```text
wrote kestrel_docs.py: 114 lines
```

```python run
(pkg / "ragsys.py").write_text(r'''"""ragsys: the llm.03 question-answering system in miniature, with knobs, so we can EVALUATE changes to it.

Pipeline: chunk -> keyword index (BM25) [+ LSA vectors, fused with RRF] -> optional rerank -> top-k sources ->
extractive answer, or a refusal if the best sentence covers too little of the question."""
from __future__ import annotations

import math
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace

import numpy as np

STOP = frozenset("a an the and or but if of to in on at by for with from as is are was were be been it its this that these those i you we they my your our me do does did can could will would should may might have has had not no what which who how any there here".split())


def stem(w):
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w


def tokenize(text):
    return [stem(w) for w in re.findall(r"-?\d+(?:\.\d+)?|[a-z]+", text.lower()) if w not in STOP]


QUESTION_WORDS = frozenset({"much", "many", "long", "often", "old", "big", "come", "get", "make", "need", "take", "buy", "hour", "day", "pay", "size", "match"})


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9$-])", text.strip()) if s.strip()]


@dataclass(frozen=True)
class Config:
    chunking: str = "section"          # "section" (one chunk per section) or "fixed" (blind cuts of `size` characters)
    size: int = 400
    with_title: bool = True            # add document title and heading to the INDEXED text
    retriever: str = "bm25+lsa"        # "bm25" or "bm25+lsa"
    rerank: bool = True
    top_k: int = 3                     # sources handed to the answerer
    min_coverage: float = 0.4          # refuse if the best sentence covers less of the question than this
    unknown_word_check: bool = False   # refuse if the question asks about a word that appears nowhere in the library


@dataclass
class Chunk:
    id: str
    doc_id: str
    text: str
    index_text: str
    title: str


@dataclass
class Result:
    answer: str
    refused: bool
    retrieved: list[str]                     # chunk ids of the sources, in order
    cited: list[str]                         # chunk ids the answer cites
    prompt_tokens: int
    latency_ms: float
    coverage: float = 0.0


def make_chunks(docs, cfg: Config) -> list[Chunk]:
    out = []
    for d in docs:
        pieces = []
        if cfg.chunking == "fixed":
            whole = " ".join(t for _, t in d["sections"])
            step = max(1, cfg.size - cfg.size // 4)
            pieces = [("", whole[i:i + cfg.size].strip()) for i in range(0, len(whole), step) if whole[i:i + cfg.size].strip()]
        else:
            pieces = list(d["sections"])
        for i, (heading, text) in enumerate(pieces):
            out.append(Chunk(f"{d['id']}:{i}", d["id"], text, f"{d['title']}. {heading}. {text}" if cfg.with_title else text, d["title"]))
    return out


class BM25:
    def __init__(self, texts, k1=1.5, b=0.75):
        self.k1, self.b, self.docs = k1, b, [tokenize(t) for t in texts]
        self.avg = sum(len(d) for d in self.docs) / max(1, len(self.docs))
        self.post = defaultdict(list)
        for i, d in enumerate(self.docs):
            for w, c in Counter(d).items():
                self.post[w].append((i, c))
        n = len(self.docs)
        self.idf = {w: math.log(1 + (n - len(p) + 0.5) / (len(p) + 0.5)) for w, p in self.post.items()}

    def rank(self, q, k):
        s = [0.0] * len(self.docs)
        for w in set(tokenize(q)):
            for i, tf in self.post.get(w, ()):
                s[i] += self.idf[w] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * len(self.docs[i]) / self.avg))
        return [i for i in sorted(range(len(s)), key=lambda i: -s[i])[:k] if s[i] > 0]


class LSA:
    def __init__(self, texts, dim=32):
        docs = [Counter(tokenize(t)) for t in texts]
        words = sorted(set().union(*[set(d) for d in docs]))
        self.vocab = {w: i for i, w in enumerate(words)}
        df = np.array([sum(w in d for d in docs) for w in words])
        self.idf = np.log((1 + len(texts)) / (1 + df)) + 1
        self.matrix = self._tfidf(docs)
        _, _, vt = np.linalg.svd(self.matrix, full_matrices=False)
        self.comp = vt[:dim]
        self.vecs = self._norm(self.matrix @ self.comp.T)

    def _tfidf(self, counters):
        m = np.zeros((len(counters), len(self.vocab)))
        for r, c in enumerate(counters):
            for w, n in c.items():
                if w in self.vocab:
                    m[r, self.vocab[w]] = (1 + math.log(n)) * self.idf[self.vocab[w]]
        return m

    @staticmethod
    def _norm(m):
        n = np.linalg.norm(m, axis=-1, keepdims=True)
        return m / np.where(n == 0, 1, n)

    def rank(self, q, k):
        qv = self._norm(self._tfidf([Counter(tokenize(q))]) @ self.comp.T)[0]
        return [int(i) for i in np.argsort(-(self.vecs @ qv))[:k]]


def rrf(rankings, k=60):
    s = {}
    for r in rankings:
        for pos, item in enumerate(r, start=1):
            s[item] = s.get(item, 0.0) + 1 / (k + pos)
    return [i for i, _ in sorted(s.items(), key=lambda p: -p[1])]


def rerank_score(q, text, title):
    qt, tt = tokenize(q), set(tokenize(text)) | set(tokenize(title))
    if not qt:
        return 0.0
    qs = set(qt)
    cov = sum(w in tt for w in qs) / len(qs)
    nums = {w for w in qs if w.lstrip("-")[:1].isdigit()}
    num = len(nums & tt) / len(nums) if nums else 0.0
    ttl = len(qs & set(tokenize(title))) / len(qs)
    return cov + 0.4 * ttl + 0.3 * num


class RagSystem:
    def __init__(self, docs, cfg: Config = Config()):
        self.cfg = cfg
        self.chunks = make_chunks(docs, cfg)
        texts = [c.index_text for c in self.chunks]
        self.vocab = {w for t in texts for w in tokenize(t)}
        self.bm25 = BM25(texts)
        self.lsa = LSA(texts) if cfg.retriever == "bm25+lsa" else None

    def retrieve(self, question, pool=20):
        lists = [self.bm25.rank(question, pool)]
        if self.lsa is not None:
            lists.append(self.lsa.rank(question, pool))
        order = rrf(lists)[:pool] if len(lists) > 1 else lists[0]
        if self.cfg.rerank:
            order = sorted(order[:10], key=lambda i: -rerank_score(question, self.chunks[i].text, self.chunks[i].title))
        return order[: self.cfg.top_k]

    def answer(self, question) -> Result:
        t0 = time.perf_counter()
        order = self.retrieve(question)
        src = [self.chunks[i] for i in order]
        q = set(tokenize(question))
        best = (0.0, None, "")
        for c in src:
            for s in sentences(c.text):
                cov = len(q & set(tokenize(s))) / len(q) if q else 0.0
                if cov > best[0]:
                    best = (cov, c.id, s)
        refused = best[1] is None or best[0] < self.cfg.min_coverage
        if self.cfg.unknown_word_check and not refused:
            unknown = [w for w in q if w not in self.vocab and w not in QUESTION_WORDS]
            refused = bool(unknown)                                   # "colour", "red", "vegan": the library never uses these words
        prompt_tokens = math.ceil((sum(len(c.text) for c in src) + len(question) + 400) / 4)        # sources + question + instructions
        return Result("" if refused else best[2], refused, [c.id for c in src], [] if refused else [best[1]], prompt_tokens,
                      (time.perf_counter() - t0) * 1e3, best[0])
''', encoding="utf-8")
print("wrote ragsys.py:", 187, "lines")
```
```text
wrote ragsys.py: 187 lines
```

```python run
(pkg / "backend.py").write_text(r'''"""backend: pretend model providers. A backend takes a prompt and returns text, token usage, and how long it 'took' (virtual time).
Each model version has a price, a speed and a BEHAVIOUR, so we can practise changing models without any real provider."""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass

from ragsys import sentences, tokenize


@dataclass(frozen=True)
class ModelSpec:
    name: str                 # e.g. "kestrel-chat"
    version: str              # e.g. "2025-03-01". ALWAYS pin an exact version.
    price_in_per_m: float     # dollars per million input tokens (illustrative)
    price_out_per_m: float
    ttft_s: float             # time to first token
    tokens_per_s: float
    behaviour: str = "v1"     # how the fake model answers: v1, v2 or v3bad

    @property
    def id(self) -> str:
        return f"{self.name}@{self.version}"


class BackendError(Exception):
    def __init__(self, message: str, status: int = 500, retryable: bool = True):
        super().__init__(message)
        self.status, self.retryable = status, retryable


class BackendTimeout(BackendError):
    def __init__(self, message: str = "the provider did not answer in time"):
        super().__init__(message, 504, True)


@dataclass(frozen=True)
class Completion:
    text: str
    input_tokens: int
    output_tokens: int
    latency_s: float
    model_id: str
    cost: float


def tokens_of(text: str) -> int:
    return math.ceil(len(text) / 4) if text else 0


REFUSAL = "I could not find that in the documents."


def _answer(spec: ModelSpec, user: str) -> str:
    """Answer from the <source n="..."> blocks of the prompt, extractively. The behaviour differs by model version."""
    question = user.rsplit("Question:", 1)[-1]
    q = set(tokenize(question))
    best = (0.0, 0, "")
    for m in re.finditer(r'<source n="(\d+)"[^>]*>\n(.*?)\n</source>', user, re.DOTALL):
        for sentence in sentences(m.group(2)):
            coverage = len(q & set(tokenize(sentence))) / len(q) if q else 0.0
            if coverage > best[0]:
                best = (coverage, int(m.group(1)), sentence.strip())
    need = {"v3bad": 0.6, "mini": 0.5}.get(spec.behaviour, 0.4)           # v3bad and mini refuse more: that is how a regression or a cheaper model looks
    if best[0] < need:
        return REFUSAL
    digest = int(hashlib.sha256((spec.id + question).encode()).hexdigest(), 16) % 100
    cite = "" if (spec.behaviour == "v3bad" and digest < 35) else f" [{best[1]}]"      # v3bad also forgets to cite
    if spec.behaviour == "v2":
        return f"Based on the documents, {best[2]}{cite} Let me know if you need anything else."
    return f"{best[2]}{cite}"


class FakeBackend:
    """A model endpoint. `slow_factor` multiplies latency (a provider slowdown); `fail_next` makes the next N calls fail; `down` fails every call."""

    def __init__(self, spec: ModelSpec, clock):
        self.spec, self.clock = spec, clock
        self.slow_factor, self.fail_next, self.down, self.calls = 1.0, 0, False, 0

    def complete(self, system: str, user: str, max_tokens: int = 300, timeout: float | None = None) -> Completion:
        self.calls += 1
        if self.down:
            self.clock.sleep(0.05)
            raise BackendError("provider unavailable (503)", 503)
        if self.fail_next > 0:
            self.fail_next -= 1
            self.clock.sleep(0.05)
            raise BackendError("temporary provider error (500)", 500)
        text = _answer(self.spec, user)
        n_in, n_out = tokens_of(system) + tokens_of(user), min(tokens_of(text), max_tokens)
        latency = (self.spec.ttft_s + n_out / self.spec.tokens_per_s) * self.slow_factor
        if timeout is not None and latency > timeout:
            self.clock.sleep(timeout)                          # we waited the whole timeout and gave up (the provider may still bill for it)
            raise BackendTimeout()
        self.clock.sleep(latency)
        cost = (n_in * self.spec.price_in_per_m + n_out * self.spec.price_out_per_m) / 1e6
        return Completion(text, n_in, n_out, latency, self.spec.id, cost)
''', encoding="utf-8")
print("wrote backend.py:", 100, "lines")
```
```text
wrote backend.py: 100 lines
```

A registry file keeps every model pinned in **configuration, not in code**. `load_registry` refuses an alias like `latest`: an alias means "whatever the provider decides today", which is exactly how a service changes behaviour overnight with no commit to blame.

```python run
(pkg / "models.toml").write_text(r'''# Every model is pinned to an exact version. Prices are ILLUSTRATIVE placeholders.
[models."kestrel-chat@2025-01-15"]
price_in_per_m = 1.0
price_out_per_m = 5.0
ttft_s = 0.40
tokens_per_s = 60
behaviour = "v1"

[models."kestrel-chat@2025-04-02"]
price_in_per_m = 0.5
price_out_per_m = 2.5
ttft_s = 0.25
tokens_per_s = 90
behaviour = "v2"

[models."kestrel-chat@2025-06-10"]
price_in_per_m = 0.5
price_out_per_m = 2.5
ttft_s = 0.25
tokens_per_s = 90
behaviour = "v3bad"

[models."kestrel-mini@2025-02-01"]
price_in_per_m = 0.2
price_out_per_m = 1.0
ttft_s = 0.15
tokens_per_s = 120
behaviour = "mini"
''', encoding="utf-8")
print("wrote models.toml:", 28, "lines")
```
```text
wrote models.toml: 28 lines
```

```python run
(pkg / "release.py").write_text(r'''"""release: changing the model (or the provider) without breaking the service. Pin versions, compare before switching, roll out gradually,
and keep a way back."""
from __future__ import annotations

import hashlib
import math
import tomllib
from dataclasses import dataclass

from backend import FakeBackend, ModelSpec, REFUSAL


def load_registry(path) -> dict[str, ModelSpec]:
    """models.toml: one [models."name@version"] table per model. A model without an exact version is refused ('latest' is not a version)."""
    with open(path, "rb") as f:
        data = tomllib.load(f)
    registry = {}
    for model_id, row in data["models"].items():
        name, _, version = model_id.partition("@")
        if not version or version.lower() in ("latest", "stable", "default"):
            raise ValueError(f"{model_id!r}: pin an exact version, not an alias")
        registry[model_id] = ModelSpec(name, version, float(row["price_in_per_m"]), float(row["price_out_per_m"]), float(row["ttft_s"]),
                                       float(row["tokens_per_s"]), row.get("behaviour", "v1"))
    return registry


def sticky_bucket(user_id: str, salt: str = "canary") -> int:
    """0..99, the same for the same user every time, so a user does not flip between model versions from one request to the next."""
    return int(hashlib.sha256((salt + user_id).encode()).hexdigest(), 16) % 100


class ModelRouter:
    """Chooses the model version for each user: the stable one, or the canary for a sticky `percent` of users."""

    def __init__(self, backends: dict[str, FakeBackend], stable: str, clock, fallback: str | None = None):
        self.backends, self.stable, self.clock = backends, stable, clock
        self.canary: str | None = None
        self.percent = 0
        self.fallback_id = fallback
        self._reliable: dict[str, ReliableBackend] = {}

    def _wrap(self, model_id: str):
        from resilience import ReliableBackend                      # imported here so this file can be read before resilience.py exists in the chapter
        if model_id not in self._reliable:
            fb = self.backends[self.fallback_id] if self.fallback_id and self.fallback_id != model_id else None
            self._reliable[model_id] = ReliableBackend(self.backends[model_id], fb, self.clock)
        return self._reliable[model_id]

    def model_for(self, user_id: str) -> str:
        if self.canary and sticky_bucket(user_id) < self.percent:
            return self.canary
        return self.stable

    def backend_for(self, user_id: str):
        mid = self.model_for(user_id)
        return self._wrap(mid), mid

    def start_canary(self, model_id: str, percent: int) -> None:
        if model_id not in self.backends:
            raise KeyError(model_id)
        self.canary, self.percent = model_id, percent

    def promote(self) -> None:
        if self.canary:
            self.stable, self.canary, self.percent = self.canary, None, 0

    def rollback(self) -> None:
        self.canary, self.percent = None, 0


# ---------------------------------------------------------------- compare two models on a golden set BEFORE any user sees the new one
def sign_test_p(improved: int, worsened: int) -> float:
    n = improved + worsened
    if n == 0:
        return 1.0
    k = min(improved, worsened)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def run_golden(rag, backend, cases) -> list[dict]:
    """cases: (question, gold_doc, gold_phrase); gold_doc None means the library cannot answer. Returns one result per case."""
    from rag import SYSTEM, build_prompt, parse_answer
    rows = []
    for question, doc, phrase in cases:
        order = rag.retrieve(question)
        sources = [{"n": i, "title": rag.chunks[c].title, "text": rag.chunks[c].text, "id": rag.chunks[c].id} for i, c in enumerate(order[:3], 1)]
        comp = backend.complete(SYSTEM, build_prompt(question, sources), 300)
        parsed = parse_answer(comp.text, sources)
        if doc is None:
            ok = parsed["refused"]
        else:
            ok = (not parsed["refused"]) and phrase.lower() in comp.text.lower()
        rows.append({"question": question, "answerable": doc is not None, "ok": ok, "refused": parsed["refused"], "cited": parsed["cited"], "latency_s": comp.latency_s,
                     "cost": comp.cost, "tokens_out": comp.output_tokens})
    return rows


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    answerable = [r for r in rows if r["answerable"]]
    answered = [r for r in rows if not r["refused"]]
    lat = sorted(r["latency_s"] for r in rows)
    return {"n": n, "ok": sum(r["ok"] for r in rows) / n, "wrong_refusal": sum(r["refused"] for r in answerable) / max(1, len(answerable)),
            "cited": sum(r["cited"] for r in answered) / max(1, len(answered)), "p95_latency_s": lat[max(0, math.ceil(0.95 * n) - 1)],
            "cost_per_1k": sum(r["cost"] for r in rows) / n * 1000}


def gate_release(old_rows: list[dict], new_rows: list[dict], max_cited_drop: float = 0.05, max_latency_increase: float = 0.25) -> dict:
    """May the new model replace the old one? Fails on a significant drop in correctness, a drop in citation rate, or a big latency increase."""
    old, new = summarise(old_rows), summarise(new_rows)
    improved = sum(1 for a, b in zip(old_rows, new_rows) if b["ok"] and not a["ok"])
    worsened = sum(1 for a, b in zip(old_rows, new_rows) if a["ok"] and not b["ok"])
    p = sign_test_p(improved, worsened)
    failures, warnings = [], []
    if worsened > improved and p < 0.05:
        failures.append(f"correctness got significantly worse ({worsened} cases worse, {improved} better, p = {p:.3f})")
    elif worsened > improved:
        warnings.append(f"correctness moved the wrong way ({worsened} worse, {improved} better) but not provably (p = {p:.2f})")
    if new["cited"] < old["cited"] - max_cited_drop:
        failures.append(f"citation rate fell from {old['cited']:.2f} to {new['cited']:.2f}")
    if new["p95_latency_s"] > old["p95_latency_s"] * (1 + max_latency_increase):
        failures.append(f"p95 latency rose from {old['p95_latency_s']:.2f}s to {new['p95_latency_s']:.2f}s")
    if new["wrong_refusal"] > old["wrong_refusal"] + 0.10:
        failures.append(f"wrong refusals rose from {old['wrong_refusal']:.2f} to {new['wrong_refusal']:.2f}")
    return {"passed": not failures, "failures": failures, "warnings": warnings, "old": old, "new": new, "improved": improved, "worsened": worsened,
            "cost_change_per_1k": new["cost_per_1k"] - old["cost_per_1k"]}
''', encoding="utf-8")
print("wrote release.py:", 126, "lines")
```
```text
wrote release.py: 126 lines
```

```python run
import backend as B
from release import load_registry
from vclock import VirtualClock
REGISTRY = load_registry(pkg / "models.toml")
print(f"{'model id (pinned)':<28}{'$ in/M':>8}{'$ out/M':>9}{'first token':>13}{'tokens/s':>10}  behaviour")
for mid, s in REGISTRY.items():
    print(f"{mid:<28}{s.price_in_per_m:>8.2f}{s.price_out_per_m:>9.2f}{s.ttft_s:>12.2f}s{s.tokens_per_s:>10.0f}  {s.behaviour}")

bad = pkg / "bad.toml"
bad.write_text('[models."kestrel-chat@latest"]\nprice_in_per_m = 1\nprice_out_per_m = 1\nttft_s = 1\ntokens_per_s = 1\n', encoding="utf-8")
try:
    load_registry(bad)
except ValueError as e:
    print("\nan alias is refused:", e)
```
```text
model id (pinned)             $ in/M  $ out/M  first token  tokens/s  behaviour
kestrel-chat@2025-01-15         1.00     5.00        0.40s        60  v1
kestrel-chat@2025-04-02         0.50     2.50        0.25s        90  v2
kestrel-chat@2025-06-10         0.50     2.50        0.25s        90  v3bad
kestrel-mini@2025-02-01         0.20     1.00        0.15s       120  mini

an alias is refused: 'kestrel-chat@latest': pin an exact version, not an alias
```

(`release.py` also holds the router and the release gate of section 6; we use only the registry for now.)

### 2.2 One call, with its numbers

```python run
clock = VirtualClock()
chat = B.FakeBackend(REGISTRY["kestrel-chat@2025-01-15"], clock)
user = ('<source n="1" title="Returns and Refunds Policy">\nYou may return unused items in their original packaging within 30 days of delivery.\n</source>\n\n'
        "Question: How long do I have to return an unused item?")
c = chat.complete("Answer only from the sources. Cite like [1].", user)
print("answer     :", c.text)
print(f"tokens     : {c.input_tokens} in, {c.output_tokens} out")
print(f"latency    : {c.latency_s * 1000:.1f} ms  (= first token {REGISTRY['kestrel-chat@2025-01-15'].ttft_s * 1000:.0f} ms + {c.output_tokens} tokens / {REGISTRY['kestrel-chat@2025-01-15'].tokens_per_s:.0f} per s)")
print(f"cost       : ${c.cost:.6f}  (= {c.input_tokens} x $1/M + {c.output_tokens} x $5/M)")
print(f"clock now  : {clock.time() * 1000:.1f} ms of virtual time elapsed")
```
```text
answer     : You may return unused items in their original packaging within 30 days of delivery. [1]
tokens     : 61 in, 22 out
latency    : 766.7 ms  (= first token 400 ms + 22 tokens / 60 per s)
cost       : $0.000171  (= 61 x $1/M + 22 x $5/M)
clock now  : 766.7 ms of virtual time elapsed
```

Every number the service will later track comes from here: tokens, latency, cost. **The first token dominates**: for a short answer the 400 ms before the first token is most of the 0.8 seconds, which is why a faster model or a cache changes latency far more than shortening the reply.

### 2.3 Surviving the provider

The provider will be slow, will fail, and will sometimes disappear for an hour. `ReliableBackend` wraps a backend with the machinery of llm.02: a **retry with jittered backoff** for transient failures, a **circuit breaker** (after N failures in a row, stop calling the sick provider and fail fast; try one request again after a cool-down), and a **fallback** model to serve while it is open. A **timeout** on every call prevents one slow request from holding a worker forever.

```python run
(pkg / "resilience.py").write_text(r'''"""resilience: retries with backoff, a circuit breaker, and a fallback model, around any backend (llm.02, in miniature)."""
from __future__ import annotations

import random

from backend import BackendError


class ReliableBackend:
    def __init__(self, primary, fallback, clock, *, max_attempts: int = 2, base_delay: float = 0.2, failure_threshold: int = 3, reset_after_s: float = 30.0,
                 rng: random.Random | None = None):
        self.primary, self.fallback, self.clock = primary, fallback, clock
        self.max_attempts, self.base_delay = max_attempts, base_delay
        self.threshold, self.reset_after = failure_threshold, reset_after_s
        self.rng = rng or random.Random(0)
        self.failures, self.opened_at = 0, None
        self.used_fallback = False

    @property
    def breaker_state(self) -> str:
        if self.opened_at is None:
            return "closed"
        return "half-open" if self.clock.time() - self.opened_at >= self.reset_after else "open"

    def complete(self, system: str, user: str, max_tokens: int = 300, timeout: float | None = None):
        """Returns a Completion. Sets .used_fallback so the caller can record that the primary was not used."""
        self.used_fallback = False
        if self.breaker_state != "open":
            for attempt in range(1, self.max_attempts + 1):
                try:
                    result = self.primary.complete(system, user, max_tokens, timeout)
                    self.failures, self.opened_at = 0, None
                    return result
                except BackendError as exc:
                    self.failures += 1
                    if self.failures >= self.threshold or self.breaker_state == "half-open":
                        self.opened_at = self.clock.time()
                    if not exc.retryable or attempt == self.max_attempts or self.breaker_state == "open":
                        break
                    self.clock.sleep(self.rng.uniform(0, self.base_delay * 2 ** (attempt - 1)))
        if self.fallback is None:
            raise BackendError("no provider available", 503)
        self.used_fallback = True
        return self.fallback.complete(system, user, max_tokens, timeout)
''', encoding="utf-8")
print("wrote resilience.py:", 44, "lines")
```
```text
wrote resilience.py: 44 lines
```

```python run
from resilience import ReliableBackend
clock = VirtualClock()
primary = B.FakeBackend(REGISTRY["kestrel-chat@2025-01-15"], clock)
fallback = B.FakeBackend(REGISTRY["kestrel-mini@2025-02-01"], clock)
rb = ReliableBackend(primary, fallback, clock, failure_threshold=3, reset_after_s=30)
print(f"{'situation':<34}{'served by':<26}{'breaker':<11}{'time (virtual s)':>17}")
def call(label):
    t0 = clock.time()
    out = rb.complete("Answer only from the sources.", user)
    print(f"{label:<34}{out.model_id:<26}{rb.breaker_state:<11}{clock.time() - t0:>17.2f}")
call("healthy")
primary.fail_next = 1
call("one transient failure (retried)")
primary.down = True
call("provider down: attempt 1")
call("provider down: attempt 2")
call("breaker opened: fails fast")
clock.sleep(31)
primary.down = False
call("after the cool-down, recovered")
```
```text
situation                         served by                 breaker     time (virtual s)
healthy                           kestrel-chat@2025-01-15   closed                  0.77
one transient failure (retried)   kestrel-chat@2025-01-15   closed                  0.99
provider down: attempt 1          kestrel-mini@2025-02-01   closed                  0.58
provider down: attempt 2          kestrel-mini@2025-02-01   open                    0.38
breaker opened: fails fast        kestrel-mini@2025-02-01   open                    0.33
after the cool-down, recovered    kestrel-chat@2025-01-15   closed                  0.77
```

Read the progression. One transient failure costs a retry and the user never knows. While the provider is down, the first requests pay for failed attempts before falling back (look at the time column); once the breaker opens, requests go **straight to the fallback**, no waiting. After the cool-down one trial call reaches the primary, succeeds, and the circuit closes. Note what the **fallback is**: a cheaper, faster model that is slightly worse (section 6). Falling back is a *quality and cost decision*, so a service must **record** every fallback (the `fallback_total` metric) rather than hide it.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a circuit breaker as a three-state machine with a request timeline underneath. States: CLOSED (green: requests go to the primary model), OPEN (red: requests skip the primary and go straight to the cheaper fallback), HALF-OPEN (amber: one trial request goes to the primary). Arrows: CLOSED -> OPEN 'three failures in a row', OPEN -> HALF-OPEN 'after 30 s', HALF-OPEN -> CLOSED 'trial succeeds', HALF-OPEN -> OPEN 'trial fails'. On the timeline show six requests with their latencies (0.77, 0.99 with a retry, 0.58, 0.38, 0.33, 0.77 s) and the model that served each."

### 2.4 Try it

1. Why pin `kestrel-chat@2025-01-15` rather than use `kestrel-chat`?
2. A request waits the whole 5-second timeout and then fails. Does it still cost money?
3. Why should falling back to a cheaper model be visible in metrics?

<details><summary>Answer</summary>

1. An unpinned name can point to a different model tomorrow, changing answers, cost and speed without any change in your code; you could not tell what you tested from what you run. A pinned version changes only when you change it, in a commit, after testing.
2. Possibly yes: the provider may have started generating and bill for tokens produced, even though you gave up *(general knowledge: billing for cancelled or timed-out requests depends on the provider)*. Track timeouts as a cost risk and keep timeouts proportionate to the expected latency.
3. The fallback is a different model with different quality and price. If it silently serves half your traffic during an incident, you would not know quality dropped or why the bill changed; the metric turns an invisible degradation into an alert.

</details>

## 3. Caching responses

### 3.1 Why and what

A model call costs money and takes time; many questions repeat. A **response cache** stores the answer to a question and returns it next time: **free, and in two milliseconds instead of 800**. The questions that matter are *when is a cached answer still correct*? That is decided by the **key**: everything that could change the answer must be in it.

For this service the answer depends on: the **question** (normalised, so case and punctuation do not split the cache), the **model version** (a new model answers differently), the **prompt version**, the **index version** (new documents mean new answers), and the **scope** (is the answer the same for every user, or personal?). Put them all in the key and the invalidation problem mostly solves itself: change any of them and the old entry is simply never found again.

Add a **TTL** (time to live) as a safety net for facts that age, and a **size limit with LRU eviction** (drop the least recently used) so memory is bounded.

```python run
(pkg / "cache.py").write_text(r'''"""cache: reuse an answer instead of paying for it again. The hard part is deciding when an old answer is still the right answer."""
from __future__ import annotations

import re
import threading
from collections import OrderedDict


def normalise_question(q: str) -> str:
    return " ".join(re.findall(r"[a-z0-9$.\-]+", q.lower()))


def cache_key(question: str, *, scope: str, model_id: str, prompt_version: str, index_version: str) -> str:
    """Everything that can change the answer is part of the key. Change any of them and the old entry is simply never found."""
    return "|".join([scope, model_id, prompt_version, index_version, normalise_question(question)])


class ResponseCache:
    def __init__(self, clock, ttl_s: float = 3600.0, max_items: int = 1000):
        self.clock, self.ttl_s, self.max_items = clock, ttl_s, max_items
        self._data: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self._lock = threading.Lock()
        self._key_locks: dict[str, threading.Lock] = {}
        self.hits = self.misses = self.evictions = 0

    def get(self, key: str):
        with self._lock:
            item = self._data.get(key)
            if item is None or self.clock.time() - item[0] > self.ttl_s:
                self._data.pop(key, None)
                self.misses += 1
                return None
            self._data.move_to_end(key)                       # most recently used
            self.hits += 1
            return item[1]

    def put(self, key: str, value) -> None:
        with self._lock:
            self._data[key] = (self.clock.time(), value)
            self._data.move_to_end(key)
            while len(self._data) > self.max_items:
                self._data.popitem(last=False)                # evict the least recently used
                self.evictions += 1

    def get_or_compute(self, key: str, compute):
        """Single-flight: if many requests miss the SAME key at once, only one computes; the others wait and share its result."""
        value = self.get(key)
        if value is not None:
            return value, True
        with self._lock:
            lock = self._key_locks.setdefault(key, threading.Lock())
        with lock:
            with self._lock:
                item = self._data.get(key)
                fresh = item is not None and self.clock.time() - item[0] <= self.ttl_s
            if fresh:
                with self._lock:
                    self.hits += 1
                return item[1], True
            value = compute()
            self.put(key, value)
            return value, False

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        return len(self._data)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0
''', encoding="utf-8")
print("wrote cache.py:", 74, "lines")
```
```text
wrote cache.py: 74 lines
```

```python run
from cache import ResponseCache, cache_key, normalise_question
base = dict(scope="public", model_id="kestrel-chat@2025-01-15", prompt_version="p1", index_version="idx-1")
k = cache_key("How long do I have to return an unused item?", **base)
print("normalised  :", normalise_question("  How LONG do I have to return an unused item??  "))
print("same key for a re-typed question:", k == cache_key("how long do I have to return an unused item", **base))
for field, other in [("scope", "user:ana"), ("model_id", "kestrel-chat@2025-04-02"), ("prompt_version", "p2"), ("index_version", "idx-2")]:
    print(f"different {field:<15} -> different key: {cache_key('How long do I have to return an unused item?', **{**base, field: other}) != k}")
```
```text
normalised  : how long do i have to return an unused item
same key for a re-typed question: True
different scope           -> different key: True
different model_id        -> different key: True
different prompt_version  -> different key: True
different index_version   -> different key: True
```

### 3.2 What caching buys: a traffic experiment

Real traffic is **skewed**: a few questions are asked very often and most are rare (a *Zipf* or "long tail" pattern *(general knowledge)*). Simulate 2,000 requests: 70 % from the 32 known questions with Zipf weights, 30 % from a long tail of product questions, spread over 200 users at one request every half second of virtual time. We need the pipeline (section 5 explains it); here is the minimum to run it. The two modules it imports are written now: the observability tools (section 4) and the request pipeline (section 5).

```python run
(pkg / "observability.py").write_text(r'''"""observability: logs say WHAT happened, metrics say HOW OFTEN and HOW SLOW, traces say WHERE the time went. All three, per request."""
from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field

BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile: the smallest value that at least p percent of the values do not exceed."""
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(p / 100 * len(ordered)) - 1)]


class Metrics:
    """Counters, gauges and histograms with labels, plus text exposition in the Prometheus format."""

    def __init__(self):
        self.counters: dict[tuple, float] = defaultdict(float)
        self.gauges: dict[tuple, float] = {}
        self.samples: dict[tuple, list[float]] = defaultdict(list)

    @staticmethod
    def _key(name: str, labels: dict | None):
        return (name, tuple(sorted((labels or {}).items())))

    def inc(self, name: str, amount: float = 1.0, **labels) -> None:
        self.counters[self._key(name, labels)] += amount

    def set(self, name: str, value: float, **labels) -> None:
        self.gauges[self._key(name, labels)] = value

    def observe(self, name: str, value: float, **labels) -> None:
        self.samples[self._key(name, labels)].append(value)

    def counter(self, name: str, **labels) -> float:
        return self.counters.get(self._key(name, labels), 0.0)

    def values(self, name: str, **labels) -> list[float]:
        return self.samples.get(self._key(name, labels), [])

    def render(self) -> str:
        lines = []
        fmt = lambda labels: "{" + ",".join(f'{k}="{v}"' for k, v in labels) + "}" if labels else ""
        for (name, labels), v in sorted(self.counters.items()):
            lines.append(f"{name}{fmt(labels)} {v:g}")
        for (name, labels), v in sorted(self.gauges.items()):
            lines.append(f"{name}{fmt(labels)} {v:g}")
        for (name, labels), vals in sorted(self.samples.items()):
            for b in BUCKETS:
                lines.append(f'{name}_bucket{fmt(labels + (("le", str(b)),))} {sum(1 for x in vals if x <= b)}')
            lines.append(f'{name}_bucket{fmt(labels + (("le", "+Inf"),))} {len(vals)}')
            lines.append(f"{name}_count{fmt(labels)} {len(vals)}")
            lines.append(f"{name}_sum{fmt(labels)} {sum(vals):g}")
        return "\n".join(lines) + "\n"


@dataclass
class Span:
    name: str
    start: float
    end: float = 0.0

    @property
    def duration(self) -> float:
        return self.end - self.start


class Trace:
    """The spans of one request. `with trace.span("llm"):` times a step using the (virtual) clock."""

    def __init__(self, clock, request_id: str):
        self.clock, self.request_id, self.spans = clock, request_id, []
        self.started = clock.time()

    def span(self, name: str):
        trace = self

        class _Span:
            def __enter__(self_):
                self_.s = Span(name, trace.clock.time())
                trace.spans.append(self_.s)
                return self_.s

            def __exit__(self_, *exc):
                self_.s.end = trace.clock.time()
                return False
        return _Span()

    @property
    def total(self) -> float:
        return self.clock.time() - self.started

    def waterfall(self, width: int = 40) -> str:
        total = max(self.total, 1e-9)
        rows = []
        for s in self.spans:
            lead = int((s.start - self.started) / total * width)
            bar = max(1, round(s.duration / total * width))
            rows.append(f"  {s.name:<10}{' ' * lead}{'#' * bar}  {s.duration * 1000:7.1f} ms")
        return "\n".join(rows)


EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def redact(text: str) -> str:
    return EMAIL.sub("[email]", text)


class JsonLogger:
    """One JSON object per line, personal data redacted, kept in memory (a real one would write to stdout or a file)."""

    def __init__(self):
        self.lines: list[str] = []

    def log(self, event: str, **fields) -> None:
        self.lines.append(redact(json.dumps({"event": event, **fields}, default=str)))

    def records(self) -> list[dict]:
        return [json.loads(l) for l in self.lines]


@dataclass
class RequestRecord:
    t: float
    ok: bool
    latency_s: float
    cost: float
    model_id: str
    cache_hit: bool
    refused: bool = False
    cited: bool = True
    fallback: bool = False


@dataclass(frozen=True)
class AlertRule:
    name: str
    metric: str                 # "p95_latency_s", "error_rate", "cost_per_1k", "citation_rate", "refusal_rate"
    op: str                     # ">" or "<"
    threshold: float
    min_requests: int = 20      # do not alert on a handful of requests


def window_stats(records: list[RequestRecord]) -> dict:
    n = len(records)
    if not n:
        return {"n": 0}
    answered = [r for r in records if r.ok]
    return {"n": n, "error_rate": 1 - len(answered) / n, "p50_latency_s": percentile([r.latency_s for r in records], 50),
            "p95_latency_s": percentile([r.latency_s for r in records], 95), "p99_latency_s": percentile([r.latency_s for r in records], 99),
            "cost_per_1k": sum(r.cost for r in records) / n * 1000, "cache_hit_rate": sum(r.cache_hit for r in records) / n,
            "citation_rate": (sum(r.cited for r in answered if not r.refused) / max(1, sum(1 for r in answered if not r.refused))),
            "refusal_rate": sum(r.refused for r in answered) / max(1, len(answered)), "fallback_rate": sum(r.fallback for r in records) / n}


def evaluate_alerts(records: list[RequestRecord], rules: list[AlertRule]) -> list[str]:
    stats = window_stats(records)
    fired = []
    for r in rules:
        if stats["n"] < r.min_requests:
            continue
        value = stats[r.metric]
        if (r.op == ">" and value > r.threshold) or (r.op == "<" and value < r.threshold):
            fired.append(f"{r.name}: {r.metric} = {value:.3f} {r.op} {r.threshold}")
    return fired
''', encoding="utf-8")
print("wrote observability.py:", 173, "lines")
```
```text
wrote observability.py: 173 lines
```

```python run
(pkg / "rag.py").write_text(r'''"""rag: the request pipeline. cache -> retrieve -> prompt -> model -> validate, with a trace span around every step."""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from backend import REFUSAL, BackendError, BackendTimeout
from cache import ResponseCache, cache_key
from observability import JsonLogger, Metrics, RequestRecord, Trace
from ragsys import RagSystem

SYSTEM = ("You answer questions using ONLY the sources. Cite the source number in square brackets, like [1]. "
          "If the sources do not contain the answer, say that you could not find it.")


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code = status, code


@dataclass(frozen=True)
class ServiceConfig:
    prompt_version: str = "p1"
    index_version: str = "idx-1"
    top_k: int = 3
    max_tokens: int = 300
    llm_timeout_s: float = 5.0
    retrieve_s: float = 0.004            # simulated retrieval time
    cache_hit_s: float = 0.002


def build_prompt(question: str, sources: list[dict]) -> str:
    blocks = [f'<source n="{s["n"]}" title="{s["title"]}">\n{s["text"].replace("</source>", "[/source]")}\n</source>' for s in sources]
    return "\n\n".join(blocks) + f"\n\nQuestion: {question}"


def parse_answer(text: str, sources: list[dict]) -> dict:
    refused = text.strip() == REFUSAL
    cited_numbers = [int(n) for n in re.findall(r"\[(\d+)\]", text)]
    valid = [n for n in cited_numbers if 1 <= n <= len(sources)]
    return {"refused": refused, "cited": bool(valid) or refused, "citations": sorted(set(valid))}


class Pipeline:
    def __init__(self, rag: RagSystem, backend_for, clock, metrics: Metrics, logger: JsonLogger, cache: ResponseCache | None, config: ServiceConfig = ServiceConfig()):
        """backend_for(user_id) -> (object with .complete(...), model id that WILL serve this user). The id is part of the cache key."""
        self.rag, self.backend_for, self.clock = rag, backend_for, clock
        self.metrics, self.logger, self.cache, self.cfg = metrics, logger, cache, config
        self.records: list[RequestRecord] = []

    def _answer(self, user_id: str, question: str, trace: Trace) -> dict:
        backend, model_id = self.backend_for(user_id)
        with trace.span("retrieve"):
            self.clock.sleep(self.cfg.retrieve_s)
            order = self.rag.retrieve(question)
            sources = [{"n": i, "title": self.rag.chunks[c].title, "text": self.rag.chunks[c].text, "id": self.rag.chunks[c].id} for i, c in enumerate(order[: self.cfg.top_k], 1)]
        with trace.span("prompt"):
            prompt = build_prompt(question, sources)
        with trace.span("llm"):
            completion = backend.complete(SYSTEM, prompt, self.cfg.max_tokens, self.cfg.llm_timeout_s)
        with trace.span("validate"):
            parsed = parse_answer(completion.text, sources)
        return {"text": completion.text, "sources": [{"n": s["n"], "title": s["title"], "id": s["id"]} for s in sources], "parsed": parsed,
                "model_id": completion.model_id, "input_tokens": completion.input_tokens, "output_tokens": completion.output_tokens, "cost": completion.cost,
                "fallback": getattr(backend, "used_fallback", False)}

    def ask(self, user_id: str, question: str, request_id: str) -> dict:
        trace = Trace(self.clock, request_id)
        m, cfg = self.metrics, self.cfg
        _, model_id = self.backend_for(user_id)
        key = cache_key(question, scope="public", model_id=model_id, prompt_version=cfg.prompt_version, index_version=cfg.index_version)
        cache_hit, result = False, None
        try:
            if self.cache is not None:
                with trace.span("cache"):
                    result = self.cache.get(key)
                    if result is not None:
                        self.clock.sleep(cfg.cache_hit_s)
                        cache_hit = True
            if result is None:
                result = self._answer(user_id, question, trace)
                if self.cache is not None and not result["fallback"]:
                    self.cache.put(key, result)                    # never cache an answer from the fallback model under the primary's key
        except BackendError as exc:
            status = 504 if isinstance(exc, BackendTimeout) else 503
            m.inc("requests_total", status=str(status))
            m.observe("request_latency_seconds", trace.total)
            self.records.append(RequestRecord(self.clock.time(), False, trace.total, 0.0, model_id, False))
            self.logger.log("request_failed", request_id=request_id, status=status, error=str(exc), latency_s=round(trace.total, 4))
            raise ServiceError(status, "timeout" if status == 504 else "provider_unavailable", "the language model is not available right now") from None
        cost = 0.0 if cache_hit else result["cost"]
        latency = trace.total
        p = result["parsed"]
        m.inc("requests_total", status="200")
        m.inc("cache_total", result="hit" if cache_hit else "miss")
        m.observe("request_latency_seconds", latency)
        if not cache_hit:
            m.inc("tokens_total", result["input_tokens"], kind="input", model=result["model_id"])
            m.inc("tokens_total", result["output_tokens"], kind="output", model=result["model_id"])
            m.inc("cost_dollars_total", cost, model=result["model_id"])
            if result["fallback"]:
                m.inc("fallback_total")
        if not p["cited"]:
            m.inc("answers_without_citation_total", model=result["model_id"])
        if p["refused"]:
            m.inc("refusals_total", model=result["model_id"])
        self.records.append(RequestRecord(self.clock.time(), True, latency, cost, result["model_id"], cache_hit, p["refused"], p["cited"], result["fallback"]))
        self.logger.log("request", request_id=request_id, user=hashlib.sha256(user_id.encode()).hexdigest()[:8], model=result["model_id"], cache_hit=cache_hit,
                        latency_ms=round(latency * 1000, 1), cost_usd=round(cost, 8), tokens_in=0 if cache_hit else result["input_tokens"],
                        tokens_out=0 if cache_hit else result["output_tokens"], refused=p["refused"], cited=p["cited"],
                        spans={s.name: round(s.duration * 1000, 1) for s in trace.spans})
        return {"request_id": request_id, "answer": result["text"], "refused": p["refused"], "citations": [s for s in result["sources"] if s["n"] in p["citations"]],
                "model": result["model_id"], "cache_hit": cache_hit, "latency_ms": round(latency * 1000, 1), "cost_usd": round(cost, 8),
                "tokens": {"input": 0 if cache_hit else result["input_tokens"], "output": 0 if cache_hit else result["output_tokens"]}, "trace": trace}
''', encoding="utf-8")
print("wrote rag.py:", 116, "lines")
```
```text
wrote rag.py: 116 lines
```

```python run
import kestrel_docs
from ragsys import RagSystem, Config
from cache import ResponseCache
from observability import Metrics, JsonLogger, window_stats
from rag import Pipeline, ServiceConfig, ServiceError
from release import ModelRouter

OLD, V2, V3, MINI = "kestrel-chat@2025-01-15", "kestrel-chat@2025-04-02", "kestrel-chat@2025-06-10", "kestrel-mini@2025-02-01"
RAG = RagSystem(kestrel_docs.DOCS, Config())

def make_service(cache_ttl=None, cache_size=1000, **cfg):
    clock = VirtualClock()
    backends = {m: B.FakeBackend(s, clock) for m, s in REGISTRY.items()}
    router = ModelRouter(backends, OLD, clock, fallback=MINI)
    metrics, logger = Metrics(), JsonLogger()
    cache = ResponseCache(clock, ttl_s=cache_ttl, max_items=cache_size) if cache_ttl else None
    return Pipeline(RAG, router.backend_for, clock, metrics, logger, cache, ServiceConfig(**cfg)), router, backends, clock, metrics, logger

base_questions = [q for q, _, _ in kestrel_docs.QUESTIONS]
products = ["Aurora 2", "Aurora 3", "Summit 2", "Summit 3", "Summit 4", "Dune 4", "Ember", "Cinder", "Spark", "Frost", "Nimbus", "Squall", "Drizzle", "Gale"]
tail = [f"How much does the {p} weigh?" for p in products] + [f"What is the waterproof rating of the {p}?" for p in products[:6]] + [f"What is the comfort rating of the {p}?" for p in products[6:10]]

def traffic(n, seed=1):
    rng = random.Random(seed)
    weights = [1 / (i + 1) for i in range(len(base_questions))]            # Zipf: the first question is asked most
    for i in range(n):
        q = rng.choices(base_questions, weights)[0] if rng.random() < 0.7 else rng.choice(tail)
        yield f"user{rng.randrange(200)}", q

def run_traffic(pipe, clock, n=2000, gap_s=0.5):
    for i, (user, q) in enumerate(traffic(n)):
        try:
            pipe.ask(user, q, f"r{i}")
        except ServiceError:
            pass
        clock.sleep(gap_s)

print(f"{'cache':<18}{'hit rate':>9}{'p50 ms':>8}{'p95 ms':>8}{'mean ms':>9}{'$ per 1,000':>13}{'total $':>9}{'model calls':>13}")
for label, ttl in [("off", None), ("on, ttl 60 s", 60), ("on, ttl 3600 s", 3600)]:
    pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=ttl)
    run_traffic(pipe, clock)
    s = window_stats(pipe.records)
    print(f"{label:<18}{s['cache_hit_rate']:>9.0%}{s['p50_latency_s'] * 1000:>8.0f}{s['p95_latency_s'] * 1000:>8.0f}{sum(r.latency_s for r in pipe.records) / len(pipe.records) * 1000:>9.0f}"
          f"{s['cost_per_1k']:>13.4f}{sum(r.cost for r in pipe.records):>9.3f}{sum(b.calls for b in backends.values()):>13}")
```
```text
cache              hit rate  p50 ms  p95 ms  mean ms  $ per 1,000  total $  model calls
off                      0%     671     871      679       0.2653    0.531         2000
on, ttl 60 s            65%       2     771      232       0.0868    0.174          695
on, ttl 3600 s          97%       2       2       20       0.0068    0.014           55
```

A cache with a 60-second memory already answers 65 % of the traffic for nothing, and one that remembers for an hour answers 97 %: the **hit rate** rises with the TTL because the popular questions are asked again before they expire, so the cost per thousand requests falls by about the same share (from 0.265 to 0.087 to 0.007 dollars) and the model is called 55 times instead of 2,000. Three cautions about reading this table. First, the **p95 barely moves until the hit rate passes 95 %**: with the 60-second TTL the typical request is a 2 ms hit, but the slowest 5 % are misses, so the p95 is still a model call (771 ms against 871 ms). The cache helps the typical user far more than the unluckiest one (a fact only a percentile shows, never an average). Second, the 97 % is a property of this **tiny pool of questions** (about 55 distinct ones): real traffic has a far longer tail. Third, the benefit **depends entirely on repetition**: with no repeated questions a cache is pure overhead.

### 3.4 What can go wrong

| Hazard | Example | Defense |
|---|---|---|
| **Stale answers** | the policy changed, the cache still says 30 days | index version in the key; sensible TTL; a way to clear the cache |
| **Serving the wrong user's answer** | a personalised answer ("your order shipped") cached for everyone | a `scope` in the key (`user:ana`); only cache **public** answers across users |
| **Poisoned entries** | a fallback model's weaker answer cached under the primary's key | never cache answers from the fallback (our pipeline refuses to) |
| **Cache stampede** | a popular entry expires and 500 simultaneous requests all miss and call the model | **single-flight**: one computes, the rest wait and share |
| **Hiding quality regressions** | the cache keeps serving good old answers while the new model is bad | cache hits are labelled; measure quality on misses (section 6) |
| **Unbounded memory** | one entry per user-typed question | size limit with LRU eviction; also bound the key length |

The stampede deserves a demonstration. Eight threads ask the same missing question at the same instant. Without protection all eight call the (expensive) model; `get_or_compute` lets one do the work:

```python run
def stampede(use_single_flight):
    clock = VirtualClock()
    cache = ResponseCache(clock)
    calls, gate = [], threading.Barrier(8)
    def expensive():
        calls.append(1)
        time.sleep(0.02)                         # a real model call takes real time; the other threads arrive meanwhile
        return "answer"
    def worker():
        gate.wait()
        if use_single_flight:
            cache.get_or_compute("hot question", expensive)
        elif cache.get("hot question") is None:
            cache.put("hot question", expensive())
    threads = [threading.Thread(target=worker) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    return len(calls)

print("8 simultaneous identical requests on an empty cache:")
print("  plain get/put      -> model calls made:", stampede(False))
print("  single-flight      -> model calls made:", stampede(True))
```
```text
8 simultaneous identical requests on an empty cache:
  plain get/put      -> model calls made: 8
  single-flight      -> model calls made: 1
```

The plain version typically pays for several calls to produce the same answer; single-flight pays for exactly one. (Exactly how many the plain version makes depends on thread timing, which is the point: you cannot rely on luck.)

A final note on a cousin of this cache *(general knowledge)*: some providers offer **prompt caching**, billing repeated long prefixes (a big system prompt, a document) at a reduced rate. That lowers the cost of a *miss*; it is separate from, and combines with, the response cache here. Our price table can express it as a lower input price for the cached share (llm.01).

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a cache as a shelf with labelled jars. Show a request arriving with a key tag made of five parts stuck together: 'public | kestrel-chat@2025-01-15 | p1 | idx-1 | how long do i have to return...'. A librarian checks the shelf: a jar with an exactly matching tag is a hit (answer in 2 ms, cost $0); otherwise a miss goes to the model (800 ms, $0.0003) and a new jar is added. Animate a policy update: the index version tag changes from idx-1 to idx-2 and every old jar becomes unreachable without being thrown away. Add a second panel showing 8 customers queuing at one jar: 'single-flight: one fetches, seven wait'."

### 3.5 Try it

1. The popular question is asked 100 times in a minute and your TTL is 1 hour. A policy document changes. What should you do?
2. Why is it wrong to cache "where is my order?" under a key without the user?
3. A cache with a 90 % hit rate has what effect on the p99 latency?

<details><summary>Answer</summary>

1. Bump the **index version** (part of the key) when you re-index: old entries become unreachable at once. A TTL alone would keep serving the old policy for up to an hour.
2. The answer depends on who is asking. Without the user in the key, the first customer's order status would be served to everyone: a data leak. Cache only answers that are the same for every user, or scope the key by user.
3. Little: the 10 % that miss still take the full model time, and the p99 is dominated by the slowest misses. A cache improves the typical request, not the tail; to improve the tail you need faster models, timeouts, fallbacks and less retrieval time.

</details>

## 4. Observability

### 4.1 Three kinds of evidence

When something goes wrong at 3 a.m. you will not have a debugger; you will have what the service recorded. *(general knowledge: the three "pillars" of observability.)*

| Evidence | Answers | Cost | In this chapter |
|---|---|---|---|
| **Logs** | *what happened* to one request, in detail | storage grows with traffic | one **JSON line** per request, personal data redacted |
| **Metrics** | *how often* and *how slow*, in aggregate | cheap: numbers, not events | counters, gauges, **latency histograms**, percentiles |
| **Traces** | *where the time went* inside one request | sampled in big systems | **spans** per step, a waterfall |

Plus the thing specific to LLM services: **cost**, recorded per request and per model, because tokens are money (llm.01).

### 4.2 Percentiles, not averages

Latency is skewed: most requests are fast and a few are very slow. The **average hides the slow ones**; **percentiles** show them. The **p50** is the typical user; **p95** is "1 request in 20 is slower than this"; **p99** is the unlucky one in a hundred. SLOs (service level objectives) are written in percentiles ("p95 under 2 seconds"). A **histogram** stores counts of requests per latency bucket, which is how monitoring systems compute percentiles cheaply. `observability.py` (written above) implements percentiles (nearest rank), counters, gauges, histograms with the Prometheus text format, traces with spans, a JSON logger with redaction, a window of request records and **alert rules**.

```python run
from observability import percentile
latencies = [0.1] * 90 + [5.0] * 10                    # 90 fast requests and 10 slow ones
print(f"100 requests: mean {sum(latencies) / len(latencies):.3f} s | p50 {percentile(latencies, 50)} s | p95 {percentile(latencies, 95)} s | p99 {percentile(latencies, 99)} s")
print("the mean (0.59 s) looks tolerable; 1 user in 10 waits 5 s, 50 times the typical request, and only the percentiles say so")
```
```text
100 requests: mean 0.590 s | p50 0.1 s | p95 5.0 s | p99 5.0 s
the mean (0.59 s) looks tolerable; 1 user in 10 waits 5 s, 50 times the typical request, and only the percentiles say so
```

### 4.3 One request, fully observed

Serve one cache miss and look at all three kinds of evidence for it. The trace's **waterfall** shows where the 770 ms went; the **log line** is what your log system would store; the **metrics** accumulate.

```python run
pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=3600)
out = pipe.ask("ana@example.com", "How long do I have to return an unused item?", "req-0001")
print("answer:", out["answer"], "| model:", out["model"], "| cost: $%.6f" % out["cost_usd"], "| latency: %.1f ms" % out["latency_ms"])
print("\ntrace waterfall:")
print(out["trace"].waterfall())
print("\nthe JSON log line:")
print(logger.lines[0])
pipe.ask("ana@example.com", "How long do I have to return an unused item?", "req-0002")
print("\nsecond, identical request is a hit:", logger.records()[1]["cache_hit"], "| latency", logger.records()[1]["latency_ms"], "ms | cost", logger.records()[1]["cost_usd"])
print("\nmetrics so far:")
print("\n".join(l for l in metrics.render().splitlines() if not l.startswith("request_latency_seconds_bucket")))
```
```text
answer: You may return unused items in their original packaging within 30 days of delivery. [1] | model: kestrel-chat@2025-01-15 | cost: $0.000321 | latency: 770.7 ms

trace waterfall:
  cache     #      0.0 ms
  retrieve  #      4.0 ms
  prompt    #      0.0 ms
  llm       ########################################    766.7 ms
  validate                                          #      0.0 ms

the JSON log line:
{"event": "request", "request_id": "req-0001", "user": "8e43ca37", "model": "kestrel-chat@2025-01-15", "cache_hit": false, "latency_ms": 770.7, "cost_usd": 0.000321, "tokens_in": 211, "tokens_out": 22, "refused": false, "cited": true, "spans": {"cache": 0.0, "retrieve": 4.0, "prompt": 0.0, "llm": 766.7, "validate": 0.0}}

second, identical request is a hit: True | latency 2.0 ms | cost 0.0

metrics so far:
cache_total{result="hit"} 1
cache_total{result="miss"} 1
cost_dollars_total{model="kestrel-chat@2025-01-15"} 0.000321
requests_total{status="200"} 2
tokens_total{kind="input",model="kestrel-chat@2025-01-15"} 211
tokens_total{kind="output",model="kestrel-chat@2025-01-15"} 22
request_latency_seconds_count 2
request_latency_seconds_sum 0.772667
```

Notice what the log line contains and what it **does not**: the request id, a **hash** of the user (never the raw id, which here is an email address), the model version, tokens, cost, latency per span, and flags (`cache_hit`, `refused`, `cited`). It does not contain the question text or the answer, which can carry personal data (llm.06). And notice that the model span is 99 % of the time: that is the first place to look for slowness.

### 4.4 Alerts: turn numbers into a signal

Nobody watches a dashboard all day. An **alert rule** says "tell me when this number crosses that line". Ours are evaluated over a **sliding window** of recent requests, require a **minimum number of requests** (so five unlucky requests do not page anyone), and include **LLM-specific signals** besides latency and errors: **cost per thousand requests**, the **citation rate** (answers that cite a source), and the **refusal rate**. Those last two matter because a changed model can keep returning HTTP 200 while quietly getting worse.

```python run
from observability import AlertRule, evaluate_alerts
RULES = [AlertRule("slow", "p95_latency_s", ">", 2.0), AlertRule("errors", "error_rate", ">", 0.05), AlertRule("expensive", "cost_per_1k", ">", 1.0),
         AlertRule("citations_dropped", "citation_rate", "<", 0.90), AlertRule("too_many_refusals", "refusal_rate", ">", 0.60)]
print(f"{'alert':<20}{'fires when':<36}")
for r in RULES:
    print(f"{r.name:<20}{r.metric + ' ' + r.op + ' ' + str(r.threshold):<36}(needs at least {r.min_requests} requests)")
```
```text
alert               fires when                          
slow                p95_latency_s > 2.0                 (needs at least 20 requests)
errors              error_rate > 0.05                   (needs at least 20 requests)
expensive           cost_per_1k > 1.0                   (needs at least 20 requests)
citations_dropped   citation_rate < 0.9                 (needs at least 20 requests)
too_many_refusals   refusal_rate > 0.6                  (needs at least 20 requests)
```

### 4.5 A text dashboard

A dashboard is a table of the numbers that matter, over a recent window. Here is the window summary of one minute of normal traffic, by model:

```python run
pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=3600)
run_traffic(pipe, clock, n=240, gap_s=0.25)
s = window_stats(pipe.records)
print(f"{'window':<22}requests {s['n']} | errors {s['error_rate']:.1%} | cache hits {s['cache_hit_rate']:.0%} | fallbacks {s['fallback_rate']:.0%}")
print(f"{'latency':<22}p50 {s['p50_latency_s'] * 1000:.0f} ms | p95 {s['p95_latency_s'] * 1000:.0f} ms | p99 {s['p99_latency_s'] * 1000:.0f} ms")
print(f"{'cost':<22}${s['cost_per_1k']:.4f} per 1,000 requests | ${sum(r.cost for r in pipe.records):.4f} in total")
print(f"{'quality signals':<22}citation rate {s['citation_rate']:.0%} | refusal rate {s['refusal_rate']:.0%}")
print("alerts firing:", evaluate_alerts(pipe.records, RULES) or "none")
```
```text
window                requests 240 | errors 0.0% | cache hits 78% | fallbacks 0%
latency               p50 2 ms | p95 704 ms | p99 871 ms
cost                  $0.0553 per 1,000 requests | $0.0133 in total
quality signals       citation rate 100% | refusal rate 16%
alerts firing: none
```

Cost per thousand requests, citation rate and refusal rate sit next to p95: that is the LLM-specific dashboard. A real deployment would graph these over days and compare them with last week; the numbers here are one minute.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a monitoring dashboard with six panels: 'requests per minute' (a line), 'latency p50/p95/p99' (three lines, with p95 much higher than p50 and a dashed horizontal SLO line at 2 s), 'error rate' (bars), 'cost per 1,000 requests' (a line, with a step down when a cheaper model was promoted), 'citation rate' (a line near 100%, dipping sharply after a bad rollout), and 'cache hit rate'. Mark one time on all panels with a vertical red line labelled 'new model version at 14:20'."

### 4.6 Try it

1. 99 requests take 0.1 s and one takes 10 s. What are the mean and p99?
2. Why does the log line hold a hash of the user id and not the question?
3. A new model version keeps returning HTTP 200 with fluent answers, but the citation rate falls from 100 % to 54 %. Which alert catches it?

<details><summary>Answer</summary>

1. The mean is (99 x 0.1 + 10) / 100 = 0.199 s, which looks healthy; the p99 (nearest rank) is 0.1 s because 99 of 100 values are at most 0.1, and the single 10-second request is the p100. Percentile choice matters: the slowest 1 % is exactly one request, so also watch a high percentile over a longer window or the maximum.
2. User ids and question text can contain personal data, and logs are copied, retained and read by many people (llm.06). The hash lets you count requests per user and follow one user's problems without storing who they are; the question and answer text are left out of routine logs.
3. The `citations_dropped` rule (citation rate below 0.90), or the refusal-rate rule if refusals rise. Error-rate and latency alerts would stay silent, because HTTP statuses and speed look fine: this is why quality signals belong on the dashboard.

</details>

## 5. Serving with FastAPI

### 5.1 The pipeline and the thin service

Two layers. The **pipeline** (`rag.py`, written above) does the work for one request, with a trace span around each step: cache lookup, retrieve, build the prompt, call the model (through the router and the reliable wrapper), validate the answer (does it cite a real source?), and record the metrics, the cost and the log line. It also decides what **not** to cache: answers served by the fallback model. The **service** (`app.py`) is deliberately thin: it is the HTTP boundary and does only HTTP things.

What the service adds, each for a reason:

| Feature | Why |
|---|---|
| **Pydantic request model** | invalid input is rejected with a 422 **before any model call costs money**: question length 1 to 500, user id characters restricted |
| **Request id** (`X-Request-ID`) | every response and every log line carries it, so a user's report ("request 8f3a...") finds the exact trace. An incoming id is kept only if it is safe (letters, digits, dash) and replaced otherwise: a header is attacker-controlled text |
| **Per-user rate limit** (token bucket) | one noisy client cannot exhaust your budget or the provider's limit; responds `429` with `Retry-After` |
| **Error mapping** | `503` when no provider is available, `504` on timeout: clear codes instead of stack traces, always with the request id |
| **`/health`** (liveness) | "the process is running": restart me if this fails |
| **`/ready`** (readiness) | "I can serve right now": `503` while a circuit breaker is open, so a load balancer stops sending traffic |
| **`/metrics`** | the Prometheus text for a scraper |
| **`/dashboard`** | the window summary and alerts, **HTML-escaped** |
| **`/admin/rollback`** | puts the stable model back, protected by a token |

```python run
(pkg / "app.py").write_text(r'''"""app: the HTTP service. Thin on purpose: validation, request ids, rate limiting and error mapping live here; the work lives in the pipeline."""
from __future__ import annotations

import html
import os
import re
import uuid

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from observability import AlertRule, evaluate_alerts, window_stats
from rag import Pipeline, ServiceError

DEFAULT_RULES = [AlertRule("slow", "p95_latency_s", ">", 2.0), AlertRule("errors", "error_rate", ">", 0.05),
                 AlertRule("expensive", "cost_per_1k", ">", 1.0), AlertRule("citations_dropped", "citation_rate", "<", 0.90),
                 AlertRule("too_many_refusals", "refusal_rate", ">", 0.60)]


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)
    user_id: str = Field(min_length=1, max_length=64, pattern=r"^[\w.@-]+$")


class TokenBucket:
    """A per-user rate limit: a burst of `capacity` requests, refilled at `rate` per second (virtual or real clock)."""

    def __init__(self, clock, capacity: float = 5, rate: float = 1.0):
        self.clock, self.capacity, self.rate = clock, capacity, rate
        self.levels: dict[str, tuple[float, float]] = {}

    def take(self, user: str) -> float:
        """0.0 if allowed, otherwise the seconds to wait."""
        now = self.clock.time()
        level, last = self.levels.get(user, (self.capacity, now))
        level = min(self.capacity, level + (now - last) * self.rate)
        if level >= 1:
            self.levels[user] = (level - 1, now)
            return 0.0
        self.levels[user] = (level, now)
        return (1 - level) / self.rate


def create_app(pipeline: Pipeline, router, clock, *, rate_limiter: TokenBucket | None = None, rules=DEFAULT_RULES, admin_token: str | None = None) -> FastAPI:
    app = FastAPI(title="Kestrel QA service")
    admin_token = admin_token or os.environ.get("ADMIN_TOKEN", "")

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        return JSONResponse(status_code=exc.status, content={"error": exc.code, "message": str(exc), "request_id": request.state.request_id},
                            headers={"X-Request-ID": request.state.request_id})

    @app.middleware("http")
    async def request_id(request: Request, call_next):
        incoming = request.headers.get("x-request-id", "")
        request.state.request_id = incoming if re.fullmatch(r"[\w-]{1,64}", incoming) else uuid.uuid4().hex[:12]     # never trust a header blindly
        response = await call_next(request)
        response.headers["X-Request-ID"] = request.state.request_id
        return response

    @app.post("/ask")
    def ask(body: AskRequest, request: Request):
        if rate_limiter is not None:
            wait = rate_limiter.take(body.user_id)
            if wait > 0:
                pipeline.metrics.inc("requests_total", status="429")
                raise HTTPException(status_code=429, detail="slow down", headers={"Retry-After": str(max(1, round(wait)))})
        out = pipeline.ask(body.user_id, body.question, request.state.request_id)
        trace = out.pop("trace")
        out["spans_ms"] = {s.name: round(s.duration * 1000, 1) for s in trace.spans}
        return out

    @app.get("/health")
    def health():
        return {"status": "ok"}                                    # liveness: the process is running

    @app.get("/ready")
    def ready():
        states = {mid: rb.breaker_state for mid, rb in router._reliable.items()}
        if any(s == "open" for s in states.values()):
            return JSONResponse(status_code=503, content={"status": "degraded", "breakers": states})
        return {"status": "ready", "breakers": states}              # readiness: able to serve right now

    @app.get("/metrics", response_class=PlainTextResponse)
    def metrics():
        return pipeline.metrics.render()

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard():
        stats = window_stats(pipeline.records[-200:])
        alerts = evaluate_alerts(pipeline.records[-200:], rules)
        rows = "".join(f"<tr><td>{html.escape(k)}</td><td>{html.escape(f'{v:.4g}' if isinstance(v, float) else str(v))}</td></tr>" for k, v in stats.items())
        return f"<h1>Kestrel QA</h1><table>{rows}</table><h2>Alerts</h2><ul>{''.join(f'<li>{html.escape(a)}</li>' for a in alerts) or '<li>none</li>'}</ul>"

    @app.post("/admin/rollback")
    def rollback(x_admin_token: str = Header(default="")):
        if not admin_token or x_admin_token != admin_token:
            raise HTTPException(status_code=403, detail="forbidden")
        router.rollback()
        return {"stable": router.stable, "canary": router.canary}

    return app
''', encoding="utf-8")
print("wrote app.py:", 103, "lines")
```
```text
wrote app.py: 103 lines
```

### 5.2 Calls through the real HTTP layer

```python run
from fastapi.testclient import TestClient
from app import create_app, TokenBucket
pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=3600)
client = TestClient(create_app(pipe, router, clock, rate_limiter=TokenBucket(clock, capacity=3, rate=1.0), admin_token="s3cret"))

r = client.post("/ask", json={"question": "How long do I have to return an unused item?", "user_id": "ana"})
body = r.json()
print("status", r.status_code, "| X-Request-ID:", r.headers["x-request-id"])
print(json.dumps({k: body[k] for k in ("answer", "model", "cache_hit", "latency_ms", "cost_usd", "tokens", "spans_ms", "citations")}, indent=1))

print("\nvalidation (no model call, no cost):")
for payload in [{"question": "", "user_id": "ana"}, {"question": "ok?", "user_id": "bad id!"}, {"question": "x" * 501, "user_id": "ana"}]:
    print("  ", client.post("/ask", json=payload).status_code, str(payload)[:50])
print("calls made to any model backend so far:", sum(b.calls for b in backends.values()), "(only the first request called one)")

print("\nrate limit: user 'bob' sends 5 requests at the same instant")
codes = [client.post("/ask", json={"question": "Do gift cards expire?", "user_id": "bob"}) for _ in range(5)]
print("  statuses:", [c.status_code for c in codes], "| Retry-After:", codes[-1].headers.get("retry-after"))
print("\nunsafe request id is replaced:", client.post("/ask", json={"question": "Do gift cards expire?", "user_id": "carol"}, headers={"X-Request-ID": "x y\tz"}).headers["x-request-id"])
print("/health :", client.get("/health").json(), "| /ready :", client.get("/ready").json())
```
```text
status 200 | X-Request-ID: 767ee63606ad
{
 "answer": "You may return unused items in their original packaging within 30 days of delivery. [1]",
 "model": "kestrel-chat@2025-01-15",
 "cache_hit": false,
 "latency_ms": 770.7,
 "cost_usd": 0.000321,
 "tokens": {
  "input": 211,
  "output": 22
 },
 "spans_ms": {
  "cache": 0.0,
  "retrieve": 4.0,
  "prompt": 0.0,
  "llm": 766.7,
  "validate": 0.0
 },
 "citations": [
  {
   "n": 1,
   "title": "Returns and Refunds Policy",
   "id": "returns-policy:0"
  }
 ]
}

validation (no model call, no cost):
   422 {'question': '', 'user_id': 'ana'}
   422 {'question': 'ok?', 'user_id': 'bad id!'}
   422 {'question': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
calls made to any model backend so far: 1 (only the first request called one)

rate limit: user 'bob' sends 5 requests at the same instant
  statuses: [200, 200, 200, 429, 429] | Retry-After: 1

unsafe request id is replaced: fb307ec2a1f1
/health : {'status': 'ok'} | /ready : {'status': 'ready', 'breakers': {'kestrel-chat@2025-01-15': 'closed'}}
```

The response carries everything section 1.2 promised: the **model version, tokens, cost, total latency and the span breakdown, cache flag and citations**, plus the request id in both the body and the header. Validation failures cost nothing; the rate limiter admits a burst of three and then returns `429` with a `Retry-After`; an unsafe request id is replaced rather than echoed.

### 5.3 The service in an outage

Break the provider and watch the contract hold:

```python run
backends[OLD].down = True
print("primary model down:")
for i in range(4):
    r = client.post("/ask", json={"question": f"How much does the Aurora 3 weigh? {i}", "user_id": f"dave{i}"})
    print(f"  request {i}: status {r.status_code} | served by {r.json()['model']} | {r.json()['latency_ms']:.0f} ms")
print("  /ready  ->", client.get("/ready").status_code, client.get("/ready").json()["breakers"])
print("  /health ->", client.get("/health").status_code, "(alive, but not ready: a load balancer would stop sending traffic here)")
for b in backends.values():
    b.down = True
r = client.post("/ask", json={"question": "Do you ship abroad?", "user_id": "erin"})
print("\nevery model down:", r.status_code, r.json())
for b in backends.values():
    b.down = False
```
```text
primary model down:
  request 0: status 200 | served by kestrel-mini@2025-02-01 | 556 ms
  request 1: status 200 | served by kestrel-mini@2025-02-01 | 337 ms
  request 2: status 200 | served by kestrel-mini@2025-02-01 | 287 ms
  request 3: status 200 | served by kestrel-mini@2025-02-01 | 287 ms
  /ready  -> 503 {'kestrel-chat@2025-01-15': 'open'}
  /health -> 200 (alive, but not ready: a load balancer would stop sending traffic here)

every model down: 503 {'error': 'provider_unavailable', 'message': 'the language model is not available right now', 'request_id': 'ebd58e563a6c'}
```

With the primary down, requests are served by the cheaper fallback (answered, a little worse, recorded as fallbacks). The first one pays for failed attempts and the later ones go straight to the fallback once the breaker opens; `/ready` turns 503 while `/health` stays 200. With **every** model down the service returns a clean `503` with a request id and a message that **does not leak provider details** (llm.06): a user is told to try later, the incident has a request id to investigate.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw the service as a building with three doors for health checks: '/health' (a heartbeat icon: 'am I running?'), '/ready' (a traffic light: 'should you send me traffic?', green when all circuit breakers are closed, red when one is open) and '/metrics' (a gauge panel). Outside, a load balancer routes cars (requests) only to buildings whose '/ready' light is green. Show a second building with a red light and an open circuit breaker: its cars are diverted, and a mechanic icon labelled 'do not restart: the process is alive, the provider is sick'."

### 5.4 Concurrency in the real thing *(general knowledge)*

Our fakes block the calling thread, which is fine for a demonstration. Real model calls are **network-bound and slow** (seconds), so a real service must not tie up a worker thread per request: use `async` handlers with an async HTTP client (llm.02, core.21) or a thread pool large enough for your concurrency, and set a **maximum number of concurrent model calls** (a semaphore) so a burst queues in your service, where you can shed load with a `429` or `503`, rather than overwhelming the provider. Section 7 turns this into arithmetic.

### 5.5 Try it

1. Why validate the request body before doing anything else?
2. What is the difference between `/health` and `/ready`, and why does the service need both?
3. Why does the service replace an unsafe `X-Request-ID` instead of echoing it?

<details><summary>Answer</summary>

1. A rejected request costs microseconds; an accepted one may cost a model call. Validation protects the budget and the provider's rate limit from malformed or oversized input, and it is the first line of defense against abuse (llm.06).
2. Liveness (`/health`) answers "should I restart this process?"; readiness (`/ready`) answers "should traffic be sent here right now?". A service whose circuit breaker is open is alive but should not receive traffic; restarting it would not help, and a load balancer routing to it would hand users errors.
3. A header is attacker-controlled text. Echoing arbitrary text into a response header or a log line enables header injection (`\r\n` sequences) and log forging. Accepting only a safe pattern and generating our own otherwise removes the risk.

</details>

## 6. Handling model and provider changes

### 6.1 The model under your service will change

Models and providers change on schedules you do not control *(general knowledge)*: versions are **deprecated and retired**, a provider ships a new default, prices move, rate limits tighten, an outage hits one region, a provider is acquired or changes its terms. Each is a **change to your product**, because the model's answers are part of what you ship. Sections 2 to 5 gave you the mechanisms; this section is the process.

| Practice | Why |
|---|---|
| **Pin exact versions** in configuration, never an alias | nothing changes without a commit |
| **A provider-neutral interface** (`complete(system, user, max_tokens, timeout)` returning text, token usage, model id) | switching providers changes one adapter, not the service |
| **Compare before switching**: run the candidate on a **golden set** (llm.04) and gate on quality, latency and cost | you find the regression before your users do |
| **Roll out gradually** to a **sticky** slice of users, watching the candidate against the stable version | a bad model reaches 5 % of users, not 100 % |
| **Roll back in one command** | recovery is faster than diagnosis |
| **Watch for silent change**: run the golden set on a schedule against what is in production | providers sometimes change behaviour behind an unchanged name |
| **Track deprecation dates** | a retirement date is a deadline, not a surprise |

### 6.2 Shadow comparison: the candidate meets the golden set first

The **golden set** is the evaluation set of llm.04: 32 questions with known answers (24 answerable, 8 not). Run the current model and each candidate over it, **without any user seeing the candidate**, and gate the result. `gate_release` fails a candidate on: a significantly worse correctness (paired sign test), a **citation rate** that falls by more than 5 points, **wrong refusals** that rise by more than 10 points, or a **p95 latency** more than 25 % higher. It also reports the **cost change**, because "cheaper" is a reason people ship regressions.

```python run
from release import run_golden, gate_release, summarise
cases = list(kestrel_docs.QUESTIONS)
clock = VirtualClock()
golden = {m: run_golden(RAG, B.FakeBackend(REGISTRY[m], clock), cases) for m in REGISTRY}
print(f"{'model':<26}{'correct':>8}{'wrong refusals':>16}{'cited':>7}{'p95 s':>7}{'$ per 1k':>10}   gate vs current")
for m in REGISTRY:
    s = summarise(golden[m])
    g = gate_release(golden[OLD], golden[m]) if m != OLD else None
    verdict = "(the baseline)" if g is None else ("PASS" if g["passed"] else "BLOCKED")
    print(f"{m:<26}{s['ok']:>8.2f}{s['wrong_refusal']:>16.2f}{s['cited']:>7.2f}{s['p95_latency_s']:>7.2f}{s['cost_per_1k']:>10.3f}   {verdict}")
for m in (V2, V3, MINI):
    g = gate_release(golden[OLD], golden[m])
    print(f"\n{m}: cost change {g['cost_change_per_1k']:+.3f} per 1,000 requests | {g['worsened']} cases worse, {g['improved']} better")
    for f in g["failures"]:
        print("   FAIL:", f)
    for w in g["warnings"]:
        print("   WARN:", w)
```
```text
model                      correct  wrong refusals  cited  p95 s  $ per 1k   gate vs current
kestrel-chat@2025-01-15       0.84            0.08   1.00   0.87     0.262   (the baseline)
kestrel-chat@2025-04-02       0.84            0.08   1.00   0.74     0.161   PASS
kestrel-chat@2025-06-10       0.66            0.46   0.54   0.56     0.126   BLOCKED
kestrel-mini@2025-02-01       0.78            0.21   1.00   0.38     0.052   BLOCKED

kestrel-chat@2025-04-02: cost change -0.101 per 1,000 requests | 0 cases worse, 0 better

kestrel-chat@2025-06-10: cost change -0.136 per 1,000 requests | 8 cases worse, 2 better
   FAIL: citation rate fell from 1.00 to 0.54
   FAIL: wrong refusals rose from 0.08 to 0.46
   WARN: correctness moved the wrong way (8 worse, 2 better) but not provably (p = 0.11)

kestrel-mini@2025-02-01: cost change -0.210 per 1,000 requests | 2 cases worse, 0 better
   FAIL: wrong refusals rose from 0.08 to 0.21
   WARN: correctness moved the wrong way (2 worse, 0 better) but not provably (p = 0.50)
```

Three candidates, three different decisions, and only one is easy:

- **`2025-04-02`** is **cheaper, faster, and as good**: it passes. (Its answers are slightly wordier and cost fewer dollars because the price per token is lower: ship it.)
- **`2025-06-10`** is also cheaper and faster, and **worse**: it forgets to cite on about half its answers and refuses more questions it should answer. HTTP status and latency would both look *better*, which is precisely how this kind of regression reaches production. The gate blocks it on the citation rate and the wrong refusals, even though correctness alone is only a "worse, not provable" warning (a 32-question set cannot prove a difference of a few questions; llm.04). **Gate on several signals, not one.**
- **`kestrel-mini`** costs a fifth of the baseline and refuses noticeably more answerable questions, so it is blocked **as a replacement**. That is a *product decision*, not a defect: it is a fine **fallback** (section 2.3) or a router for easy questions (llm.01's cascade), and a team could accept the trade by changing the gate's rules in a reviewed commit (llm.04 section 8.2).

### 6.3 Canary rollout: a sticky slice, watched by cohort

Even a candidate that passes the golden set deserves a gradual rollout, because the golden set is small and real traffic is not. A **canary** sends a percentage of users to the candidate. Two details make it work. **Stickiness**: each user is assigned by a hash of their id, so the same user always gets the same version (no flipping answers between requests, and a clean comparison). **Cohort comparison**: judge the canary by comparing its requests **against the stable version's requests in the same period**, not by looking at the global average, which a small canary barely moves.

```python run
from release import sticky_bucket
users = [f"user{i}" for i in range(5000)]
share = sum(sticky_bucket(u) < 20 for u in users) / len(users)
print(f"a 20% canary reaches {share:.1%} of 5,000 users; the same user always lands in the same group: {all(sticky_bucket(u) == sticky_bucket(u) for u in users[:100])}")

pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=None)         # cache off, so every request is a model call
router.start_canary(V3, 20)                                                                # the model the golden set already blocked
def cohort(records, model):
    rs = [r for r in records if r.model_id == model]
    ans = [r for r in rs if r.ok and not r.refused]
    return len(rs), (sum(r.cited for r in ans) / len(ans) if ans else 1.0)

print(f"\n{'requests so far':>16}{'global citation rate':>22}{'stable cohort':>16}{'canary cohort':>15}   decision")
rolled_back = False
for i, (user, q) in enumerate(traffic(900, seed=3), start=1):
    pipe.ask(user, q, f"c{i}")
    clock.sleep(0.5)
    if i % 100 == 0 and not rolled_back:
        recent = pipe.records[-200:]
        glob = window_stats(recent)["citation_rate"]
        (n_s, c_s), (n_c, c_c) = cohort(recent, OLD), cohort(recent, V3)
        bad = n_c >= 20 and c_c < c_s - 0.10
        if bad:
            router.rollback()
            rolled_back = True
        print(f"{i:>16}{glob:>22.0%}{f'{c_s:.0%} ({n_s})':>16}{f'{c_c:.0%} ({n_c})':>15}   {'ROLL BACK' if bad else 'continue'}")
print("canary after the rollout:", router.canary, "| stable:", router.stable)
```
```text
a 20% canary reaches 20.7% of 5,000 users; the same user always lands in the same group: True

 requests so far  global citation rate   stable cohort  canary cohort   decision
             100                   92%       100% (85)       30% (15)   continue
             200                   94%      100% (165)       47% (35)   ROLL BACK
canary after the rollout: None | stable: kestrel-chat@2025-01-15
```

Look at the first two columns. The **global** citation rate stays above the 0.90 alert threshold of section 4.4 for the whole experiment (a dashboard alert on the overall rate would have stayed silent), because the canary is only a fifth of the traffic. The **cohort** comparison shows the problem at once: the canary's citation rate is far below the stable cohort's, and the rule rolls back on the first check with enough canary requests. Lesson: **aggregate alerts hide a bad canary; always compare cohorts.**

### 6.4 Silent change: the same name, a different model

Pinning protects you from *your own* changes. It does not always protect you from the provider's, and some providers do adjust behaviour behind an unchanged name *(general knowledge)*. The defense is to run the **golden set on a schedule** (nightly, say) against the live configuration and alert on a drop. Simulate a silent change: the backend behind our pinned id starts behaving like the bad version.

```python run
import dataclasses
pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=None)
def nightly_golden():
    s = summarise(run_golden(RAG, backends[OLD], cases))
    return s
before = nightly_golden()
backends[OLD].spec = dataclasses.replace(backends[OLD].spec, behaviour="v3bad")          # the provider quietly changed what the name means
after = nightly_golden()
print(f"{'nightly golden-set check':<28}{'correct':>8}{'wrong refusals':>16}{'cited':>7}")
print(f"{'before the silent change':<28}{before['ok']:>8.2f}{before['wrong_refusal']:>16.2f}{before['cited']:>7.2f}")
print(f"{'after the silent change':<28}{after['ok']:>8.2f}{after['wrong_refusal']:>16.2f}{after['cited']:>7.2f}")
drops = [name for name, bad in [("correctness", after["ok"] < before["ok"] - 0.10), ("citation rate", after["cited"] < before["cited"] - 0.05), ("wrong refusals", after["wrong_refusal"] > before["wrong_refusal"] + 0.10)] if bad]
print("ALERT: the pinned model changed behaviour; dropped:", drops)
backends[OLD].spec = REGISTRY[OLD]
```
```text
nightly golden-set check     correct  wrong refusals  cited
before the silent change        0.84            0.08   1.00
after the silent change         0.66            0.46   0.85
ALERT: the pinned model changed behaviour; dropped: ['correctness', 'citation rate', 'wrong refusals']
```

The model id never changed, no deploy happened, HTTP statuses stayed 200, and yet citation rate and answer quality fell. Only a **scheduled quality check** sees that. The same check, run after *every* change to prompts, index or model, is your regression test (llm.04); run on a schedule, it is your **drift monitor**.

### 6.5 A migration checklist

| Step | Check |
|---|---|
| 1. Read the notice | the retirement date, the replacement, any price or limit changes |
| 2. Add the candidate to `models.toml` | exact version, price, speed |
| 3. **Golden-set comparison** | quality, citations, refusals, latency, cost: the gate |
| 4. Look at the **changed cases** | read them: they tell you what the new model does differently |
| 5. **Adjust prompts if needed**, then repeat 3 | prompts are tuned to a model; a new one may want different wording |
| 6. **Shadow** real traffic | run the candidate on copies of live requests, compare, show users nothing |
| 7. **Canary** a sticky slice, compare cohorts | roll back automatically on a cohort regression |
| 8. **Promote**; keep the old version available as a fallback or rollback until the deadline |
| 9. **Update** the cost forecast and alerts | prices and speeds changed the thresholds |
| 10. Keep the **provider-neutral adapter** honest | errors, usage and stop reasons are normalised in one place |

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a rollout as a pipeline of four gates for a new model version. Gate 1 'golden set' (32 cases, a table of quality/cited/refusals/latency/cost with a red X on the citation rate). Gate 2 'shadow traffic' (live requests copied to the candidate, users see nothing). Gate 3 'canary 5% -> 20% -> 50%' (a user-id hash ring where the same users always fall in the shaded slice; two lines on a chart, stable and canary citation rate, the canary line falling away). Gate 4 'promote' with a big red 'rollback' button beside it. Mark where each of the three candidates (04-02, 06-10, mini) is stopped or passed."

### 6.6 Try it

1. A candidate model is 40 % cheaper and passes every quality check except p95 latency, which is 30 % higher. What do you do?
2. Why compare the canary to the stable model in the same time window instead of to last week's numbers?
3. Your pinned model's retirement date is in 6 weeks. When should the work start?

<details><summary>Answer</summary>

1. It is a product decision with numbers on the table: is a 30 % higher p95 acceptable against 40 % lower cost, given the latency SLO? Options: accept (if the SLO still holds), mitigate (a higher cache hit rate, shorter prompts, streaming so the *perceived* latency is the time to first token), or choose a different candidate. The gate's job was to surface it; a person decides, and records why.
2. Traffic changes over time (different questions at different hours, a news event, a holiday), so last week's numbers differ for reasons unrelated to the model. A same-period comparison between cohorts holds everything else equal, so a difference is attributable to the model.
3. Now. Golden-set comparison, prompt adjustments, shadow and canary each take time, and a migration that discovers a problem in week 5 has no slack. Treat the retirement date as a deadline and work back from it.

</details>

## 7. Operating it

### 7.1 An incident drill

A service is defined by how it behaves on its bad days. Run ten virtual minutes of traffic with a scripted incident: minutes 1 to 3 normal, minutes 4 to 6 the provider is **four times slower**, minute 7 the provider is **down**, minutes 8 to 10 it has **recovered**. The cache is off so every request shows the provider's real behaviour. Each row summarises that minute from the per-request records, as a dashboard would:

```python run
pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=None)
rng = random.Random(7)
RULES10 = [dataclasses.replace(r, min_requests=10) for r in RULES]            # a slowdown cuts throughput, so a minute holds fewer requests: lower the floor
print(f"{'min':>3}  {'provider':<10}{'requests':>9}{'p50 ms':>8}{'p95 ms':>8}{'errors':>8}{'fallbacks':>10}{'$ / 1k':>9}{'breaker':>9}   alerts")
for minute in range(1, 11):
    state = "normal" if minute <= 3 or minute >= 8 else "slow x4" if minute <= 6 else "DOWN"
    for b in backends.values():
        b.slow_factor = 4.0 if state == "slow x4" else 1.0
    backends[OLD].down = (state == "DOWN")
    start = clock.time()
    end = start + 60
    n = 0
    while clock.time() < end:
        try:
            pipe.ask(f"user{rng.randrange(500)}", rng.choice(base_questions), f"m{minute}-{n}")
        except ServiceError:
            pass
        clock.sleep(1.0)
        n += 1
    window = [r for r in pipe.records if r.t > start]
    s = window_stats(window)
    alerts = [a.split(":")[0] for a in evaluate_alerts(window, RULES10)]
    print(f"{minute:>3}  {state:<10}{s['n']:>9}{s['p50_latency_s'] * 1000:>8.0f}{s['p95_latency_s'] * 1000:>8.0f}{s['error_rate']:>8.0%}{s['fallback_rate']:>10.0%}{s['cost_per_1k']:>9.3f}{router._reliable[OLD].breaker_state:>9}   {alerts or '-'}")
print("\nfallback requests in total:", int(metrics.counter("fallback_total")), "| requests by status:", {k[1][0][1]: int(v) for k, v in metrics.counters.items() if k[0] == "requests_total"})
```
```text
min  provider   requests  p50 ms  p95 ms  errors fallbacks   $ / 1k  breaker   alerts
  1  normal           36     671     871      0%        0%    0.271   closed   -
  2  normal           37     637     904      0%        0%    0.261   closed   -
  3  normal           37     637     871      0%        0%    0.256   closed   -
  4  slow x4          16    2671    3604      0%        0%    0.263   closed   ['slow']
  5  slow x4          17    2937    3604      0%        0%    0.267   closed   ['slow']
  6  slow x4          17    2471    3071      0%        0%    0.258   closed   ['slow']
  7  DOWN             47     287     387      0%      100%    0.053     open   -
  8  normal           37     671     904      0%        5%    0.255   closed   -
  9  normal           37     604     871      0%        0%    0.254   closed   -
 10  normal           37     637     871      0%        0%    0.263   closed   -

fallback requests in total: 49 | requests by status: {'200': 318}
```

Walk down the table as an on-call engineer would. Minutes 1 to 3 are the baseline. In minutes 4 to 6 the p95 climbs to around three and a half seconds and the **`slow` alert fires**, but **nothing else changes**: no errors, no fallbacks, no cost change; a slowdown with a green error rate is exactly why you alert on latency. One practical detail is hidden in the code: each minute holds only 16 or 17 requests during the slowdown (every request now takes three times longer, so fewer fit in a minute), which is *below* the 20-request floor of the default alert rules. The drill therefore lowers the floor to 10; with the default, **the slowdown itself would have silenced the alert**. Minimum-count floors prevent noisy alerts on a handful of requests, and they must be chosen with the worst case in mind. In minute 7 the provider is down: the first requests pay for failed attempts, the **breaker opens**, traffic goes to the fallback (the `fallbacks` column jumps), and the **error rate stays at zero** because the fallback is working: *the user-visible effect is a slightly worse answer, which only the `fallbacks` metric and the breaker reveal*. In minutes 8 to 10 the provider is back and, after the breaker's cool-down, traffic returns to it. Note the **cost per 1,000 requests**: it falls during the outage because the fallback model is cheaper. A cost dashboard alone would have looked like good news.

### 7.2 Capacity planning, with arithmetic

How many requests can one service instance handle, and how many model calls can you have in flight? **Little's law** (llm.01, swe.09): the average number of requests in the system equals the **arrival rate times the time each one spends**. Only cache **misses** reach the model, so the cache hit rate cuts the load on the provider directly:

```python run
peak_rps = 30                                  # requests per second at peak
model_latency_s = 0.77                         # measured above (p50 miss)
print(f"{'cache hit rate':>15}{'model calls / s':>17}{'concurrent model calls':>24}{'cost per hour ($)':>19}")
for hit in (0.0, 0.5, 0.8, 0.95):
    calls = peak_rps * (1 - hit)
    concurrent = calls * model_latency_s                   # Little's law: L = rate x time
    per_hour = calls * 3600 * 0.000321                     # cost of one miss measured above
    print(f"{hit:>15.0%}{calls:>17.1f}{concurrent:>24.1f}{per_hour:>19.2f}")
print("\nprovider limits to compare with (illustrative): 600 requests/minute = 10/s; at 0% hits you would need", peak_rps, "/s: over the limit")
```
```text
 cache hit rate  model calls / s  concurrent model calls  cost per hour ($)
             0%             30.0                    23.1              34.67
            50%             15.0                    11.6              17.33
            80%              6.0                     4.6               6.93
            95%              1.5                     1.2               1.73

provider limits to compare with (illustrative): 600 requests/minute = 10/s; at 0% hits you would need 30 /s: over the limit
```

At 30 requests per second with no cache you would need about 23 model calls in flight and 30 per second, beyond a (typical) provider limit of 10 per second: the service would be throttled before it ran out of CPU. A cache hit rate of 80 % cuts the load to 6 calls per second and about 4.6 in flight. The practical rules *(general knowledge)*: set a **concurrency limit** (a semaphore) for model calls slightly above your expected need; when it is full, **queue briefly, then shed load** (`429` or `503`) rather than letting latency grow without bound; and tie your **autoscaling** to the signals that matter (in-flight calls, queue length, p95), not CPU alone, because an LLM service spends its time *waiting*.

### 7.3 Deployment: what changes when it is more than one process *(shown, not run)*

Our service keeps its cache and metrics **in memory of one process**. That is the first thing that changes in production: with several worker processes or several machines, each has its own cache (hit rates fall) and its own counters (a scraper must read all of them). The standard answers: a **shared cache** (Redis, with the same key design), **metrics scraped per instance and aggregated** by the monitoring system, and **stateless** workers so any instance can serve any request. A container image, a process manager and a few settings (these commands are **for reference and were not executed in this chapter**: they need Docker and a network, as in ml.06):

```dockerfile
# Dockerfile (illustrative)
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt        # pinned versions, as in ml.06
COPY . .
ENV ADMIN_TOKEN="" MODELS_FILE=/srv/models.toml            # secrets come from the environment, never from the image
EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```bash
docker build -t kestrel-qa:2025-06-14 .
docker run -p 8000:8000 -e ADMIN_TOKEN="$ADMIN_TOKEN" kestrel-qa:2025-06-14
curl -s localhost:8000/ready          # readiness for the load balancer
curl -s localhost:8000/metrics        # scraped by the monitoring system
```

Operational rules that matter more than the commands: **graceful shutdown** (on `SIGTERM` stop accepting new requests, finish those in flight, then exit); **rolling deployments** (replace instances one at a time, waiting for `/ready`); **configuration and secrets from the environment**; **tag images with a version**, never `latest`; and treat a **model change as a deployment** with its own rollout (section 6), independent of code deploys.

### 7.4 A runbook

| Alert | First look | Likely cause | Action |
|---|---|---|---|
| `slow` (p95 up) | trace spans: which one grew? | provider slowdown; retrieval growth; more misses | shorter timeout, fallback, raise cache TTL; contact provider |
| `errors` (error rate up) | status codes, breaker state, `fallback_total` | provider outage; bad deploy | check `/ready`; roll back the deploy; confirm the fallback works |
| `expensive` (cost per 1k up) | tokens per request, hit rate, model mix | cache hit rate fell; longer prompts; a bigger model got more traffic | find what changed; fix or cap |
| `citations_dropped` / `too_many_refusals` | per-model cohort rates, last model or prompt change | a model change (planned or silent) | **roll back**; run the golden set; investigate |
| breaker open / `/ready` 503 | which model id | that provider is failing | fallback is serving; watch the provider status; do not restart blindly |

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a ten-minute incident timeline as a horizontal band split into three phases: 'minutes 1-3 normal' (green), 'minutes 4-6 provider 4x slower' (amber), 'minute 7 provider down' (red), 'minutes 8-10 recovered' (green). Above it plot p95 latency (rising to 3 s in the amber phase, dropping in the red phase because the fallback is faster), below it plot 'fallback share' (0% -> 100% in the red phase) and 'cost per 1,000 requests' (dipping in the red phase). Mark three events with arrows: 'slow alert fires', 'circuit breaker opens', 'breaker closes after cool-down'."

### 7.5 Try it

1. During the outage drill the error rate was 0 % and the cost fell. Is the service healthy?
2. Your cache hit rate drops from 80 % to 40 % at a constant request rate. What happens to cost, concurrency and latency?
3. Why does an LLM service need a concurrency limit on model calls?

<details><summary>Answer</summary>

1. It is *degraded*, not healthy: users get answers from a cheaper, slightly worse fallback model, which only `fallback_total`, the open breaker and a falling cost reveal. "No errors" is not the same as "working as intended"; alert on fallback share and on quality signals as well as errors.
2. The miss rate goes from 20 % to 60 %: model calls (and cost) triple, the number of model calls in flight triples (Little's law), average latency rises because more requests pay the model's time, and you may hit the provider's rate limit.
3. Model calls are slow and limited by the provider. Without a limit a burst creates thousands of simultaneous calls that exhaust connections, trigger provider throttling and make every request slower. A limit with a short queue and then load shedding keeps latency bounded and the failure explicit.

</details>

## 8. Project: deploy the RAG system with monitoring

### 8.1 The brief

Take the RAG system of llm.03 and run it as a service that you could put in front of users **and** operate: a documented HTTP API, caching, cost and latency tracked per request, a dashboard and alerts, protection against the provider's bad days, and a release process for model changes.

Requirements:

1. **`POST /ask`** with validation (422 before any model call), a request id in the header and the body, and a response with the **answer, citations, model version, cache flag, latency, per-span timings, tokens and cost**.
2. **A rate limit** per user (429 with `Retry-After`), and clean **503 and 504** mappings with no provider details.
3. **A response cache** whose key contains the question, model version, prompt version, index version and scope; TTL, LRU size limit and **single-flight**; fallback answers never cached.
4. **Observability**: one redacted JSON log line per request, counters and latency histograms in Prometheus text, a trace per request, and a window summary with **p50, p95, p99, error rate, cache hit rate, cost per 1,000 requests, citation rate and refusal rate**; **alert rules** with minimum request counts; an escaped HTML dashboard.
5. **Resilience**: timeout, retry with backoff, circuit breaker and a fallback model; `/health` and `/ready`.
6. **Releases**: pinned versions in `models.toml` (aliases refused), a **golden-set gate** (quality, citations, refusals, latency, cost), a **sticky canary** router, **promote and rollback**, and a token-protected admin rollback.
7. **47 tests**, including a stampede test with threads, hand-checked percentile and histogram values, and a test that a regressed model is blocked even though it is cheaper.

### 8.2 Tests

`test_cache_observability.py` (13 tests): key construction, TTL on the virtual clock, LRU, hit rate, the **single-flight** stampede with eight threads, percentiles checked by hand, metrics rendering and histogram buckets, trace spans and waterfall, redacting logger, window statistics and alert rules. `test_release.py` (15 tests): the registry refusing aliases, backend cost and latency checked by hand, timeouts, retry, fallback, the breaker's full cycle, sticky buckets and canary share, promote and rollback, the sign test, and the release gate on the cheaper-faster model (**passes**), the regressed model (**blocked despite being cheaper**) and the cheapest model (blocked on refusals). `test_service.py` (19 tests): the API contract, request-id safety, validation before any model call, cache hits that cost nothing, **no stale answers after a model or index change**, cost equal to tokens times price, metrics, logs without personal data, fallback not poisoning the cache, readiness during an outage, 503, 504, 429 with recovery, the slow-provider alert, a regressed canary visible on the dashboard with admin rollback, and HTML escaping.

```python run
(pkg / "test_cache_observability.py").write_text(r'''import json
import threading

import pytest

from cache import ResponseCache, cache_key, normalise_question
from observability import (AlertRule, JsonLogger, Metrics, RequestRecord, Trace, evaluate_alerts, percentile, redact, window_stats)
from vclock import VirtualClock


def test_question_normalisation():
    assert normalise_question("  How LONG is the   warranty?? ") == "how long is the warranty"
    assert normalise_question("Price: $75.00") == "price $75.00"


def test_every_input_that_changes_the_answer_changes_the_key():
    base = dict(scope="public", model_id="m@1", prompt_version="p1", index_version="i1")
    k = cache_key("How long?", **base)
    assert k == cache_key("how long", **base), "case and punctuation must not split the cache"
    for field, other in [("scope", "user:ana"), ("model_id", "m@2"), ("prompt_version", "p2"), ("index_version", "i2")]:
        assert cache_key("How long?", **{**base, field: other}) != k, f"a new {field} must never be served an old answer"


def test_ttl_uses_the_clock():
    clock = VirtualClock()
    cache = ResponseCache(clock, ttl_s=100)
    cache.put("k", "answer")
    clock.sleep(99)
    assert cache.get("k") == "answer"
    clock.sleep(2)
    assert cache.get("k") is None, "after the TTL the entry is gone"
    assert (cache.hits, cache.misses) == (1, 1)


def test_lru_eviction_keeps_recently_used():
    cache = ResponseCache(VirtualClock(), max_items=2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")                      # a is now the most recently used
    cache.put("c", 3)
    assert cache.get("b") is None and cache.get("a") == 1 and cache.get("c") == 3 and cache.evictions == 1, "b was the least recently used"


def test_hit_rate_and_clear():
    cache = ResponseCache(VirtualClock())
    cache.put("k", 1)
    for k in ("k", "k", "x", "y"):
        cache.get(k)
    assert cache.hit_rate == 0.5
    cache.clear()
    assert len(cache) == 0


def test_single_flight_one_computation_for_many_simultaneous_misses():
    cache = ResponseCache(VirtualClock())
    calls, gate, results = [], threading.Barrier(8), []

    def compute():
        calls.append(1)
        return "expensive answer"

    def worker():
        gate.wait()
        results.append(cache.get_or_compute("same question", compute))

    threads = [threading.Thread(target=worker) for _ in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert len(calls) == 1, "eight identical simultaneous requests must cost ONE model call (no cache stampede)"
    assert all(v == "expensive answer" for v, _ in results) and sum(hit for _, hit in results) == 7


def test_different_keys_compute_separately():
    cache = ResponseCache(VirtualClock())
    assert cache.get_or_compute("a", lambda: 1) == (1, False) and cache.get_or_compute("b", lambda: 2) == (2, False) and cache.get_or_compute("a", lambda: 99) == (1, True)


def test_percentile_nearest_rank_hand_checked():
    values = list(range(1, 101))
    assert percentile(values, 50) == 50 and percentile(values, 95) == 95 and percentile(values, 99) == 99 and percentile(values, 100) == 100
    assert percentile([7], 95) == 7 and percentile([], 95) == 0.0
    assert percentile([0.1, 0.1, 0.1, 5.0], 50) == 0.1 and percentile([0.1, 0.1, 0.1, 5.0], 95) == 5.0, "one slow request in four IS the p95: averages hide it"


def test_metrics_labels_counters_and_rendering():
    m = Metrics()
    m.inc("requests_total", status="200")
    m.inc("requests_total", status="200")
    m.inc("requests_total", status="503")
    m.set("breaker_open", 1, model="m@1")
    for v in (0.04, 0.2, 3.0):
        m.observe("latency_seconds", v)
    assert m.counter("requests_total", status="200") == 2 and m.counter("requests_total", status="500") == 0
    text = m.render()
    assert 'requests_total{status="200"} 2' in text and 'breaker_open{model="m@1"} 1' in text
    assert 'latency_seconds_bucket{le="0.05"} 1' in text and 'latency_seconds_bucket{le="0.25"} 2' in text and 'latency_seconds_bucket{le="5.0"} 3' in text
    assert 'latency_seconds_bucket{le="+Inf"} 3' in text and "latency_seconds_count 3" in text and "latency_seconds_sum 3.24" in text


def test_trace_spans_and_waterfall():
    clock = VirtualClock()
    trace = Trace(clock, "r1")
    with trace.span("retrieve"):
        clock.sleep(0.004)
    with trace.span("llm"):
        clock.sleep(0.5)
    assert [(s.name, round(s.duration, 3)) for s in trace.spans] == [("retrieve", 0.004), ("llm", 0.5)] and round(trace.total, 3) == 0.504
    assert "retrieve" in trace.waterfall() and "llm" in trace.waterfall() and "500.0 ms" in trace.waterfall()


def test_logger_writes_json_and_redacts_personal_data():
    log = JsonLogger()
    log.log("request", note="contact ana@example.com", n=3)
    assert "ana@example.com" not in log.lines[0] and json.loads(log.lines[0])["note"] == "contact [email]"
    assert redact("a@b.co and c@d.org") == "[email] and [email]"


def rec(latency, ok=True, cost=0.001, cited=True, refused=False, hit=False):
    return RequestRecord(0.0, ok, latency, cost, "m@1", hit, refused, cited)


def test_window_stats_hand_checked():
    records = [rec(0.1), rec(0.2), rec(0.3), rec(4.0), rec(0.0, ok=False, cost=0.0)]
    s = window_stats(records)
    assert s["n"] == 5 and s["error_rate"] == pytest.approx(0.2) and s["p50_latency_s"] == 0.2 and s["p95_latency_s"] == 4.0
    assert s["cost_per_1k"] == pytest.approx(0.004 / 5 * 1000)
    assert window_stats([]) == {"n": 0}


def test_alert_rules_need_enough_requests_and_respect_direction():
    slow = [rec(3.0) for _ in range(30)]
    rules = [AlertRule("slow", "p95_latency_s", ">", 2.0), AlertRule("citations", "citation_rate", "<", 0.9), AlertRule("cheap", "cost_per_1k", ">", 5.0)]
    assert [a.split(":")[0] for a in evaluate_alerts(slow, rules)] == ["slow"], "only the rule whose condition holds fires"
    assert evaluate_alerts(slow[:5], rules) == [], "five requests are too few to alert on"
    uncited = [rec(0.1, cited=False) for _ in range(30)]
    assert [a.split(":")[0] for a in evaluate_alerts(uncited, rules)] == ["citations"]
''', encoding="utf-8")
print("wrote test_cache_observability.py:", 136, "lines")
```
```text
wrote test_cache_observability.py: 136 lines
```

```python run
(pkg / "test_release.py").write_text(r'''import pytest

import kestrel_docs
from backend import BackendError, BackendTimeout, FakeBackend, ModelSpec, REFUSAL, tokens_of
from ragsys import Config, RagSystem
from release import ModelRouter, gate_release, load_registry, run_golden, sign_test_p, sticky_bucket, summarise
from resilience import ReliableBackend
from vclock import VirtualClock

REGISTRY = load_registry(__import__("pathlib").Path(__file__).parent / "models.toml")
OLD, V2, V3, MINI = "kestrel-chat@2025-01-15", "kestrel-chat@2025-04-02", "kestrel-chat@2025-06-10", "kestrel-mini@2025-02-01"


@pytest.fixture(scope="module")
def golden():
    rag = RagSystem(kestrel_docs.DOCS, Config())
    cases = list(kestrel_docs.QUESTIONS)
    clock = VirtualClock()
    return {m: run_golden(rag, FakeBackend(REGISTRY[m], clock), cases) for m in REGISTRY}


def backend(version=OLD, clock=None):
    return FakeBackend(REGISTRY[version], clock or VirtualClock())


def test_registry_pins_exact_versions_and_refuses_aliases(tmp_path):
    assert set(REGISTRY) == {OLD, V2, V3, MINI} and REGISTRY[V2].price_in_per_m == 0.5
    bad = tmp_path / "bad.toml"
    bad.write_text('[models."kestrel-chat@latest"]\nprice_in_per_m = 1\nprice_out_per_m = 1\nttft_s = 1\ntokens_per_s = 1\n', encoding="utf-8")
    with pytest.raises(ValueError, match="pin an exact version"):
        load_registry(bad)
    bad.write_text('[models."kestrel-chat"]\nprice_in_per_m = 1\nprice_out_per_m = 1\nttft_s = 1\ntokens_per_s = 1\n', encoding="utf-8")
    with pytest.raises(ValueError, match="pin an exact version"):
        load_registry(bad)


def test_backend_cost_and_latency_hand_checked():
    clock = VirtualClock()
    b = FakeBackend(ModelSpec("m", "1", 1.0, 5.0, ttft_s=0.4, tokens_per_s=50), clock)
    user = '<source n="1" title="t">\nThe tent weighs 2.9 kg.\n</source>\n\nQuestion: How much does the tent weigh?'
    c = b.complete("system", user)
    assert c.input_tokens == tokens_of("system") + tokens_of(user) and c.output_tokens == tokens_of("The tent weighs 2.9 kg. [1]")
    assert c.cost == pytest.approx((c.input_tokens * 1.0 + c.output_tokens * 5.0) / 1e6) and c.latency_s == pytest.approx(0.4 + c.output_tokens / 50)
    assert clock.time() == pytest.approx(c.latency_s), "the call advanced the clock by exactly its latency"


def test_timeout_raises_after_waiting_the_full_timeout():
    clock = VirtualClock()
    b = backend(clock=clock)
    b.slow_factor = 50
    with pytest.raises(BackendTimeout):
        b.complete("s", '<source n="1" title="t">\nA fact about tents here.\n</source>\n\nQuestion: tents?', timeout=2.0)
    assert clock.time() == pytest.approx(2.0)


def test_retry_recovers_from_a_single_failure_without_fallback():
    clock = VirtualClock()
    primary, fallback = backend(clock=clock), backend(MINI, clock)
    primary.fail_next = 1
    rb = ReliableBackend(primary, fallback, clock)
    rb.complete("s", "Question: x")
    assert primary.calls == 2 and fallback.calls == 0 and not rb.used_fallback and rb.breaker_state == "closed"


def test_fallback_serves_when_the_primary_is_down_and_the_breaker_opens():
    clock = VirtualClock()
    primary, fallback = backend(clock=clock), backend(MINI, clock)
    primary.down = True
    rb = ReliableBackend(primary, fallback, clock, failure_threshold=3)
    for _ in range(2):
        assert rb.complete("s", "Question: x").model_id == MINI and rb.used_fallback
    assert rb.breaker_state == "open"
    calls = primary.calls
    rb.complete("s", "Question: x")
    assert primary.calls == calls, "with the breaker open the sick primary is not even called"
    clock.sleep(31)
    assert rb.breaker_state == "half-open"
    primary.down = False
    rb.complete("s", "Question: x")
    assert rb.breaker_state == "closed" and not rb.used_fallback, "after the cool-down one trial succeeds and traffic returns"


def test_no_fallback_means_a_clean_error():
    clock = VirtualClock()
    primary = backend(clock=clock)
    primary.down = True
    with pytest.raises(BackendError) as info:
        ReliableBackend(primary, None, clock).complete("s", "q")
    assert info.value.status == 503


def test_sticky_buckets_are_deterministic_and_spread_evenly():
    assert sticky_bucket("ana") == sticky_bucket("ana") and 0 <= sticky_bucket("ana") < 100
    counts = [sticky_bucket(f"user{i}") < 10 for i in range(5000)]
    assert 0.08 < sum(counts) / 5000 < 0.12, "10 percent canary should reach about 10 percent of users"


def test_router_canary_promote_rollback():
    clock = VirtualClock()
    backends = {m: FakeBackend(s, clock) for m, s in REGISTRY.items()}
    router = ModelRouter(backends, OLD, clock, fallback=MINI)
    assert router.model_for("ana") == OLD
    router.start_canary(V3, 100)
    assert all(router.model_for(f"u{i}") == V3 for i in range(20))
    router.rollback()
    assert router.model_for("ana") == OLD and router.canary is None
    router.start_canary(V2, 100)
    router.promote()
    assert router.stable == V2 and router.canary is None
    with pytest.raises(KeyError):
        router.start_canary("nope@1", 10)


def test_a_user_never_flips_between_versions():
    clock = VirtualClock()
    router = ModelRouter({m: FakeBackend(s, clock) for m, s in REGISTRY.items()}, OLD, clock)
    router.start_canary(V2, 30)
    for user in (f"u{i}" for i in range(200)):
        assert len({router.model_for(user) for _ in range(5)}) == 1


def test_sign_test_hand_checked():
    assert sign_test_p(5, 0) == pytest.approx(0.0625) and sign_test_p(3, 3) == 1.0 and sign_test_p(0, 0) == 1.0


def test_baseline_model_quality_on_the_golden_set(golden):
    s = summarise(golden[OLD])
    assert s["n"] == 32 and s["ok"] >= 0.8 and s["cited"] == 1.0 and s["wrong_refusal"] <= 0.15


def test_a_cheaper_faster_model_with_the_same_quality_may_ship(golden):
    g = gate_release(golden[OLD], golden[V2])
    assert g["passed"] and g["cost_change_per_1k"] < 0 and g["new"]["p95_latency_s"] < g["old"]["p95_latency_s"], g


def test_a_regressed_model_is_blocked_with_reasons(golden):
    g = gate_release(golden[OLD], golden[V3])
    assert not g["passed"]
    assert any("citation rate fell" in f for f in g["failures"]) and any("wrong refusals rose" in f for f in g["failures"]), g["failures"]
    assert g["cost_change_per_1k"] < 0, "it is cheaper, which is exactly why a gate must look at quality too"


def test_the_cheapest_model_trades_quality_for_cost_and_the_gate_says_so(golden):
    g = gate_release(golden[OLD], golden[MINI])
    assert not g["passed"] and any("wrong refusals" in f for f in g["failures"]) and g["new"]["cost_per_1k"] < 0.25 * g["old"]["cost_per_1k"]


def test_comparing_a_model_with_itself_passes_and_changes_nothing(golden):
    g = gate_release(golden[OLD], golden[OLD])
    assert g["passed"] and g["improved"] == g["worsened"] == 0 and g["cost_change_per_1k"] == 0
''', encoding="utf-8")
print("wrote test_release.py:", 150, "lines")
```
```text
wrote test_release.py: 150 lines
```

```python run
(pkg / "test_service.py").write_text(r'''import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import kestrel_docs
from app import AlertRule, TokenBucket, create_app
from backend import FakeBackend
from cache import ResponseCache
from observability import JsonLogger, Metrics
from rag import Pipeline, ServiceConfig
from ragsys import Config, RagSystem
from release import ModelRouter, load_registry
from vclock import VirtualClock

REGISTRY = load_registry(Path(__file__).parent / "models.toml")
OLD, V3, MINI = "kestrel-chat@2025-01-15", "kestrel-chat@2025-06-10", "kestrel-mini@2025-02-01"
Q = "How long do I have to return an unused item?"
RAG = RagSystem(kestrel_docs.DOCS, Config())


def build(cache=True, limiter=None, rules=None, **kw):
    clock = VirtualClock()
    backends = {m: FakeBackend(s, clock) for m, s in REGISTRY.items()}
    router = ModelRouter(backends, OLD, clock, fallback=MINI)
    metrics, logger = Metrics(), JsonLogger()
    pipe = Pipeline(RAG, router.backend_for, clock, metrics, logger, ResponseCache(clock) if cache else None, ServiceConfig(**kw))
    extra = {"rules": rules} if rules is not None else {}
    app = create_app(pipe, router, clock, rate_limiter=limiter, admin_token="s3cret", **extra)
    return TestClient(app), pipe, router, backends, clock, metrics, logger


def ask(client, q=Q, user="ana", **headers):
    return client.post("/ask", json={"question": q, "user_id": user}, headers=headers)


def test_ask_contract_and_headers():
    client, *_ = build()
    r = ask(client)
    body = r.json()
    assert r.status_code == 200 and "30 days" in body["answer"] and body["citations"][0]["title"] == "Returns and Refunds Policy" and not body["refused"]
    assert set(body) >= {"request_id", "answer", "model", "cache_hit", "latency_ms", "cost_usd", "tokens", "spans_ms"} and r.headers["x-request-id"] == body["request_id"]
    assert body["model"] == OLD and body["cost_usd"] > 0 and set(body["spans_ms"]) >= {"retrieve", "llm"}


def test_incoming_request_id_is_kept_only_if_safe():
    client, *_ = build()
    assert ask(client, **{"X-Request-ID": "trace-abc-123"}).headers["x-request-id"] == "trace-abc-123"
    evil = ask(client, **{"X-Request-ID": "x\r\nSet-Cookie: a=b"}).headers["x-request-id"]
    assert re.fullmatch(r"[0-9a-f]{12}", evil), "a header value with control characters must be replaced, never echoed"


@pytest.mark.parametrize("payload", [{"question": "", "user_id": "ana"}, {"question": "x" * 501, "user_id": "ana"}, {"question": "ok?", "user_id": "bad id!"}, {"question": "ok?"}])
def test_input_validation_happens_before_any_model_call(payload):
    client, pipe, _, backends, *_ = build()
    assert client.post("/ask", json=payload).status_code == 422 and sum(b.calls for b in backends.values()) == 0


def test_second_identical_question_is_a_cache_hit_that_costs_nothing():
    client, pipe, *_ , metrics, logger = build()
    first, second = ask(client).json(), ask(client, "how LONG do I have to return an unused item").json()
    assert not first["cache_hit"] and second["cache_hit"] and second["cost_usd"] == 0 and second["tokens"] == {"input": 0, "output": 0}
    assert second["latency_ms"] < first["latency_ms"] / 50 and second["answer"] == first["answer"]
    assert metrics.counter("cache_total", result="hit") == 1 and metrics.counter("cache_total", result="miss") == 1


def test_changing_the_model_or_index_never_serves_the_old_answer():
    client, pipe, router, *_ = build()
    ask(client)
    router.start_canary(V3, 100)
    assert not ask(client).json()["cache_hit"], "a different model version has a different cache key"
    router.rollback()
    assert ask(client).json()["cache_hit"], "back on the old model the old entry is valid again"
    pipe.cfg = ServiceConfig(index_version="idx-2")
    assert not ask(client).json()["cache_hit"], "a rebuilt index invalidates everything"


def test_cost_is_tokens_times_price():
    client, *_ = build()
    b = ask(client).json()
    spec = REGISTRY[OLD]
    assert b["cost_usd"] == pytest.approx((b["tokens"]["input"] * spec.price_in_per_m + b["tokens"]["output"] * spec.price_out_per_m) / 1e6, abs=1e-8)


def test_metrics_endpoint_and_health():
    client, *_ = build()
    ask(client)
    ask(client)
    text = client.get("/metrics").text
    assert f'requests_total{{status="200"}} 2' in text and "request_latency_seconds_count 2" in text and "cost_dollars_total" in text
    assert client.get("/health").json() == {"status": "ok"}


def test_logs_have_what_you_need_and_no_personal_data():
    client, *_ , logger = build()
    ask(client, user="ana@example.com")
    line = logger.lines[0]
    assert "ana@example.com" not in line, "the user id is hashed, never logged raw"
    rec = logger.records()[0]
    assert rec["event"] == "request" and rec["model"] == OLD and rec["latency_ms"] > 0 and "llm" in rec["spans"] and "cost_usd" in rec


def test_provider_outage_falls_back_marks_it_and_does_not_poison_the_cache():
    client, pipe, router, backends, clock, metrics, _ = build()
    backends[OLD].down = True
    r = ask(client).json()
    assert r["model"] == MINI and metrics.counter("fallback_total") == 1
    backends[OLD].down = False
    router._reliable[OLD].opened_at = None
    again = ask(client).json()
    assert not again["cache_hit"] and again["model"] == OLD, "an answer from the fallback must not be cached under the primary's key"


def test_breaker_open_makes_the_service_not_ready_but_still_alive():
    client, pipe, router, backends, *_ = build()
    backends[OLD].down = True
    for i in range(4):
        ask(client, f"question {i} about tents?", user=f"u{i}")
    assert router._reliable[OLD].breaker_state == "open"
    ready = client.get("/ready")
    assert ready.status_code == 503 and ready.json()["breakers"][OLD] == "open" and client.get("/health").status_code == 200


def test_total_outage_is_a_clean_503_with_a_request_id():
    client, pipe, router, backends, *_ = build()
    for b in backends.values():
        b.down = True
    r = ask(client)
    assert r.status_code == 503 and r.json()["error"] == "provider_unavailable" and r.json()["request_id"] == r.headers["x-request-id"] and "language model" in r.json()["message"]


def test_timeout_is_a_504():
    client, pipe, router, backends, *_ = build(llm_timeout_s=0.1)
    for b in backends.values():
        b.slow_factor = 100
    assert ask(client).status_code == 504


def test_rate_limit_returns_429_with_retry_after_then_recovers():
    bucket_clock = VirtualClock()
    c, *_ = build(limiter=TokenBucket(bucket_clock, 2, 1.0))
    assert [ask(c, user="ana").status_code for _ in range(3)] == [200, 200, 429], "a burst of 2, then the third request is refused"
    r = ask(c, user="ana")
    assert r.status_code == 429 and int(r.headers["retry-after"]) >= 1
    assert ask(c, user="bob").status_code == 200, "another user has their own bucket"
    bucket_clock.sleep(2)
    assert ask(c, user="ana").status_code == 200, "after waiting, tokens have refilled"


def test_slow_provider_triggers_the_latency_alert():
    client, pipe, router, backends, *_ = build(cache=False)
    for b in backends.values():
        b.slow_factor = 5
    for i in range(25):
        ask(client, f"What is the warranty on tents? {i}", user=f"u{i}")
    page = client.get("/dashboard").text
    assert "slow: p95_latency_s" in page, page


def test_a_regressed_canary_is_visible_in_the_dashboard_and_the_admin_can_roll_back():
    client, pipe, router, backends, *_ = build(cache=False)
    router.start_canary(V3, 100)
    for q, *_ in kestrel_docs.QUESTIONS[:24]:
        ask(client, q, user="ana")
    page = client.get("/dashboard").text
    assert "citations_dropped" in page or "too_many_refusals" in page, page
    assert client.post("/admin/rollback").status_code == 403 and client.post("/admin/rollback", headers={"X-Admin-Token": "wrong"}).status_code == 403
    r = client.post("/admin/rollback", headers={"X-Admin-Token": "s3cret"})
    assert r.status_code == 200 and r.json() == {"stable": OLD, "canary": None}


def test_dashboard_escapes_html():
    client, *_ = build(rules=[AlertRule("<script>alert(1)</script>", "p95_latency_s", ">", 0.0001, min_requests=1)])
    ask(client)
    page = client.get("/dashboard").text
    assert "<script>" not in page and "&lt;script&gt;" in page
''', encoding="utf-8")
print("wrote test_service.py:", 177, "lines")
```
```text
wrote test_service.py: 177 lines
```

```python run
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=pkg, capture_output=True, text=True, encoding="utf-8")
print("\n".join(res.stdout.strip().splitlines()[-3:]) if res.stdout.strip() else res.stderr[-600:])
listing = subprocess.run([sys.executable, "-m", "pytest", "-q", "-q", "-p", "no:cacheprovider", "--collect-only"], cwd=pkg, capture_output=True, text=True, encoding="utf-8")
print({m.group(1): int(m.group(2)) for line in listing.stdout.splitlines() if (m := re.match(r"(\S+\.py): (\d+)", line))})
```
```text
...............................................                          [100%]
47 passed in 1.13s
{'test_cache_observability.py': 13, 'test_release.py': 15, 'test_service.py': 19}
```

### 8.3 The service after traffic: what an operator sees

Serve a few hundred requests through the real HTTP layer, then read what the operator pages show: the Prometheus text, and the dashboard.

```python run
pipe, router, backends, clock, metrics, logger = make_service(cache_ttl=3600)
client = TestClient(create_app(pipe, router, clock, admin_token="s3cret"))
rng = random.Random(11)
for i, (user, q) in enumerate(traffic(400, seed=5)):
    client.post("/ask", json={"question": q, "user_id": user})
    clock.sleep(0.5)
text = client.get("/metrics").text
print("\n".join(l for l in text.splitlines() if not l.startswith("request_latency_seconds_bucket") and not l.startswith("tokens_total"))[:900])
page = client.get("/dashboard").text
print("\ndashboard (HTML, shortened):")
print(re.sub(r"</tr>", "\n", re.sub(r"<[^>]+>", " ", page.replace("</td><td>", ": ")))[:700])
```
```text
cache_total{result="hit"} 346
cache_total{result="miss"} 54
cost_dollars_total{model="kestrel-chat@2025-01-15"} 0.013306
refusals_total{model="kestrel-chat@2025-01-15"} 59
requests_total{status="200"} 400
request_latency_seconds_count 400
request_latency_seconds_sum 36.2747

dashboard (HTML, shortened):
 Kestrel QA    n: 200    error_rate: 0    p50_latency_s: 0.002    p95_latency_s: 0.002    p99_latency_s: 0.6707    cost_per_1k: 0.01026    cache_hit_rate: 0.955    citation_rate: 1    refusal_rate: 0.145    fallback_rate: 0    Alerts   none  
```

### 8.4 Extensions

1. **A real provider.** Write one adapter with the `complete(system, user, max_tokens, timeout)` signature for a real API (llm.02's client); keep the pricing in `models.toml`. Nothing else in the service changes.
2. **A shared cache.** Replace the in-memory cache with Redis using the same key format and TTL; test that two service instances share hits.
3. **Streaming.** Add `POST /ask/stream` (server-sent events, llm.02) and record **time to first token** as its own metric and alert.
4. **Tracing standards.** Export the spans in a standard format (OpenTelemetry) and connect them to a tracing backend.
5. **Per-tenant budgets.** Track cost per API key and refuse requests when a tenant's daily budget is used up (llm.02).
6. **Shadow traffic.** Copy a sample of live requests to a candidate model and log the comparison without returning its answers.
7. **Evaluate in CI.** Run the golden-set gate in the pipeline on every change to prompts, index or models (llm.04), failing the build on a regression.

## 9. Common traps

1. **Unpinned models** (2.1, 6.1). An alias changes behaviour with no commit to blame; pin exact versions.
2. **Averages instead of percentiles** (4.2). The mean hides the slow tail; alert on p95 and p99.
3. **A cache key missing something that changes the answer** (3.1). Include model, prompt, index and scope in the key; a TTL alone is not invalidation.
4. **Caching a personalised answer for everyone** (3.4). Scope the key, or do not cache.
5. **Caching the fallback's answers under the primary's key** (3.4, 5.1). A temporary degradation becomes a lasting one.
6. **Ignoring the cache stampede** (3.4). One popular expiring entry can multiply your model bill; use single-flight.
7. **Logging personal data** (4.3). Hash user ids, leave out question and answer text, redact the rest (llm.06).
8. **Monitoring only errors and latency** (4.4, 6.3). A model regression returns 200 and fluent text; track citation rate, refusals and cost.
9. **Judging a canary by the global average** (6.3). Compare the canary cohort with the stable cohort in the same window.
10. **Skipping the golden-set comparison because the new model is cheaper** (6.2). Cheaper and faster is how regressions hide.
11. **Trusting that a pinned name never changes** (6.4). Run the golden set on a schedule to catch silent change.
12. **Hiding fallbacks** (2.3, 7.1). A cheaper fallback serving traffic is a quality change: record and alert on it.
13. **A readiness check that always says yes** (5.1). Report not-ready while a breaker is open so traffic is routed away.
14. **Echoing a client-supplied header into responses or logs** (5.1). Accept a safe pattern and generate your own otherwise.
15. **No concurrency limit on model calls** (5.4, 7.2). Bursts exhaust the provider's limits and turn latency into a queue.
16. **Per-process state behind several workers** (7.3). In-memory caches and counters multiply; share the cache and aggregate the metrics.

## 10. Summary

- **Shipping** adds everything around the model call: validation, rate limits, request ids, timeouts, retries, a circuit breaker and fallback, caching, observability, a release process, health checks and a deployment story. The outcome is a service whose **cost and latency are known per request**.
- A **model is a pinned, versioned dependency** with a price, a speed and a behaviour, declared in configuration; an alias is refused. Behind a provider-neutral interface, switching providers changes one adapter.
- **Resilience**: bounded timeouts, retry with jittered backoff, a **circuit breaker** that fails fast and recovers after a cool-down, and a **fallback** model whose use is recorded.
- **Caching**: the key holds everything that changes the answer (question, model, prompt, index, scope), with TTL, LRU and **single-flight** against stampedes; never cache personalised or fallback answers across keys. It helps the typical request far more than the tail, and only if traffic repeats.
- **Observability**: **logs** (one redacted JSON line per request), **metrics** (counters, histograms, **percentiles, not averages**) and **traces** (spans per step); **cost, citation rate and refusal rate** next to latency and errors; **alert rules** with minimum request counts; a dashboard.
- **FastAPI service**: validation before any model call, request ids (safe ones only), per-user rate limits, 503 and 504 mappings without provider details, `/health` (alive) versus `/ready` (can serve now), `/metrics`, an escaped dashboard, a token-protected rollback.
- **Model and provider changes**: pin, compare on a **golden set** and gate on quality, **citations, refusals**, latency and cost; **canary with sticky users and cohort comparison**; promote or roll back in one step; **schedule the golden set** to catch silent change; track deprecation dates.
- **Operating**: an incident drill shows that slowdowns, outages and fallbacks each show up in different metrics; capacity follows **Little's law** (misses reach the provider, so the hit rate sets the load); limit concurrency and shed load; in production share the cache and aggregate metrics.
- The project is a **monitored RAG service** with 47 tests.

**Self-check (answer without looking back):**

1. What does a per-request record need to contain so that you can answer "why was Tuesday expensive?" and "did the new model change anything?".
2. A cache key is `question`. List four ways that goes wrong.
3. Why do percentiles matter more than the mean, and what is p95?
4. A new model version is cheaper and faster. What do you do before routing any user to it, and which signals do you check besides correctness?
5. Your canary receives 10 % of traffic and the global citation rate barely moves, but the canary cohort's rate is 30 points below the stable cohort's. What do you conclude and do?
6. Explain the difference between `/health` and `/ready`, and when each should fail.
7. A provider outage shows 0 % errors and a lower bill. Is that good news?

<details><summary>Answer</summary>

1. The request id, time, model version, input and output tokens, cost, total latency and per-step latency, cache hit, fallback used, refused or cited, and the status. Group cost by day and model for "Tuesday"; compare quality signals (citations, refusals) and latency by model version around the change date for "did the model change anything".
2. Stale answers after a model, prompt or index change (those are not in the key); a personalised answer served to the wrong user (no scope); fallback answers cached as if from the primary; and an unbounded cache growing with unique questions. (Also: punctuation or case splitting the cache if the question is not normalised.)
3. Latency is skewed: most requests are fast and a few are very slow, and the mean hides them. The p95 is the latency that 95 % of requests do not exceed: one request in twenty is slower. SLOs are written in percentiles because users experience the tail.
4. Run it through the golden-set comparison (shadow) and gate: correctness, **citation rate**, **wrong refusals**, p95 latency and cost; read the changed cases; then canary with sticky users and compare cohorts. Cheaper and faster is exactly how a regression slips through, because status codes and latency look better.
5. The canary is probably bad, and the aggregate alert hid it because the canary is a small share. Roll it back (automatically, if you have a cohort rule), run the golden set on the candidate, and look at the changed cases to see what it does differently.
6. `/health` is liveness: fail it only if the process is broken and should be restarted. `/ready` is readiness: fail it when the service cannot serve usefully right now (a circuit breaker open, the index not loaded) so a load balancer stops sending traffic. A not-ready but alive service must not be restarted blindly.
7. No: it is degraded. The fallback model is serving cheaper, slightly worse answers, so errors are zero and cost falls, which looks fine on a dashboard that watches only errors and cost. The fallback share, the breaker state and the quality signals tell the true story.

</details>
