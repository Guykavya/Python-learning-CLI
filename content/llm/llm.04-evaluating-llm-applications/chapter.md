# Chapter 4 (LLM): Evaluating LLM Applications

You changed the chunk size, or the prompt, or the model, and the answers "feel better". Do they? An LLM application is a pipeline of many parts, each of which can change the result, and the results are text, not a number that goes up or down. Teams that do not measure get stuck in a loop: every fix breaks something else, nobody can say whether last week's change helped, and a regression reaches users before anyone notices. **Evaluation** is how you replace "feels better" with "better by this much, on these questions, and we are this sure".

The syllabus outcome is: **show with numbers that a change improved or broke your RAG system**. The project is an **evaluation suite for the PDF question-answering system** of llm.03: a dataset, metrics, a runner, a statistical comparison and a gate that blocks a regression, all runnable from the command line and in CI.

You will learn, in this order:

1. What an evaluation is, and the system we will evaluate.
2. **Building evaluation datasets**: where cases come from, how to check them, synthetic cases and their dangers, labelling agreement, dev and test splits, and fingerprints.
3. **Evaluating retrieval separately from generation**: which stage failed, per question, and per kind of question.
4. **Automatic answer metrics**, and each one's blind spot.
5. **Model-graded evaluation** ("LLM as judge") and its limits: how to test whether a judge deserves trust.
6. **Statistics for small test sets**: intervals, paired comparisons, sample sizes, and why trying many variants fools you.
7. **Experiments**: change one thing at a time and read the result honestly.
8. **Regression checks in CI**: baselines, hard limits, gates, and the cost of evaluating.
9. The project, with 43 tests.

Prerequisites: llm.03 (the RAG system) and llm.02 (judging and validating model output). Statistics are developed from scratch, no prior knowledge needed.

> **How this chapter is built, and what it does NOT contain.** *No real language model is called, and no real judge model is run.* Two honest consequences:
>
> - **The system under test is real and measured.** It is the llm.03 pipeline in miniature (`ragsys.py`: BM25 plus LSA retrieval, reranking and an *extractive* answerer that quotes the best sentence), with settings you can change. Every number about it is a real run on the fictional Kestrel library.
> - **The judge is a simulation.** Model-graded evaluation needs a real model, which this course cannot assume. So section 5 builds a **`SimulatedJudge`**, a scripted grader whose accuracy and biases *we* set, and uses it to teach the part that matters and does not depend on the model: **how to test a judge** (agreement with humans, kappa, padding and swap tests). When you attach a real model, the same tests apply. Statements about how real judge models behave are marked *(general knowledge)*.
>
> Variations that would only repeat a lesson are **question → worked answer** boxes. Sections carry optional **Visualise it** prompts you can paste into any AI chat; the course never depends on them. The chapter runs in a few seconds.

```python run
import sys, platform, json, math, re, time, io, pathlib, tempfile, subprocess, collections, random
import numpy as np
print("python  ", sys.version.split()[0], "|", platform.system(), "| numpy", np.__version__)
ws = pathlib.Path(tempfile.mkdtemp(prefix="llm04_ws_"))        # every file this chapter creates lives here
pkg = ws / "pkg"
pkg.mkdir()
sys.path.insert(0, str(pkg))                                   # so `import ragsys` finds the files we write below
print("workspace:", ws.name)
```
```text
python   3.14.4 | Linux | numpy 2.5.4
workspace: llm04_ws_yxzskd16
```

## Table of contents

1. [What an evaluation is, and the system under test](#1-what-an-evaluation-is-and-the-system-under-test)
2. [Building evaluation datasets](#2-building-evaluation-datasets)
3. [Evaluating retrieval separately from generation](#3-evaluating-retrieval-separately-from-generation)
4. [Automatic answer metrics and their blind spots](#4-automatic-answer-metrics-and-their-blind-spots)
5. [Model-graded evaluation and its limits](#5-model-graded-evaluation-and-its-limits)
6. [Statistics for small test sets](#6-statistics-for-small-test-sets)
7. [Experiments: change one thing, read the result honestly](#7-experiments-change-one-thing-read-the-result-honestly)
8. [Regression checks in CI](#8-regression-checks-in-ci)
9. [Project: an evaluation suite for the PDF question-answering system](#9-project-an-evaluation-suite-for-the-pdf-question-answering-system)
10. [Common traps](#10-common-traps)
11. [Summary](#11-summary)

## 1. What an evaluation is, and the system under test

### 1.1 Four parts

Every evaluation, from a unit test to a research benchmark, has the same four parts:

| Part | Question | In this chapter |
|---|---|---|
| **Dataset** | what do we ask? | questions with known right answers (and some with *no* answer) |
| **System** | what do we test? | the RAG pipeline, with settings |
| **Metrics** | how do we score one answer? | retrieval hit, correct, false answer, ... |
| **Analysis** | what do the scores mean? | intervals, paired comparisons, slices, a gate |

An LLM evaluation is a **test suite for something that is partly wrong all the time**. A normal unit test passes or fails. Here the question is never "is it perfect?" but "**did this change make it better or worse, and is that real or luck?**" That is why the analysis part, statistics, is as important as the metrics.

Three habits to keep from the first line of code:

1. **Evaluate before you improve.** Build the evaluation first, record the baseline, then change things. Otherwise you are tuning blind.
2. **Evaluate the parts separately and the whole together.** A wrong answer can come from retrieval or from generation (section 3).
3. **Never trust a single number.** Every score is an estimate from a finite set of questions, and it has an error bar (section 6).

### 1.2 The system under test

The fictional Kestrel outdoor-gear library from llm.03 (22 documents, 37 chunks) and a miniature of the RAG system. It has six **settings** (the `Config`), which are exactly the kind of thing you will want to evaluate changes to: how to chunk (`section` or `fixed` size), whether to add the title to the indexed text, the retriever (`bm25` or `bm25+lsa`), whether to rerank, how many sources to give the answerer (`top_k`), and how much of the question the best sentence must cover before it answers (`min_coverage`; below that it refuses). It is the llm.03 code condensed to one file so that this chapter runs alone.

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
import kestrel_docs as kd
from ragsys import RagSystem, Config

system = RagSystem(kd.DOCS, Config())
print(len(system.chunks), "chunks | default settings:", system.cfg)
for q in ["How much does the Aurora 3 tent weigh?", "Does the Aurora 3 come in red?", "What is a good recipe for chocolate cake?"]:
    r = system.answer(q)
    print(f"\nQ: {q}\n   answer : {r.answer or '(refused)'}\n   sources: {r.retrieved} | coverage {r.coverage:.2f} | prompt ~{r.prompt_tokens} tokens | {r.latency_ms:.2f} ms")
```
```text
37 chunks | default settings: Config(chunking='section', size=400, with_title=True, retriever='bm25+lsa', rerank=True, top_k=3, min_coverage=0.4, unknown_word_check=False)

Q: How much does the Aurora 3 tent weigh?
   answer : The Aurora 3 is a 3-person, 3-season tent weighing 2.9 kg.
   sources: ['tent-aurora-3:0', 'tent-aurora-2:0', 'tent-aurora-3:1'] | coverage 0.80 | prompt ~183 tokens | 1.09 ms

Q: Does the Aurora 3 come in red?
   answer : The Aurora 3 is a 3-person, 3-season tent weighing 2.9 kg.
   sources: ['tent-aurora-3:0', 'tent-aurora-3:1', 'tent-aurora-2:0'] | coverage 0.50 | prompt ~181 tokens | 0.66 ms

Q: What is a good recipe for chocolate cake?
   answer : (refused)
   sources: ['returns-policy:0', 'returns-policy:1', 'returns-policy:2'] | coverage 0.00 | prompt ~218 tokens | 0.71 ms
```

Three questions, three behaviours: a correct answer, a **wrong** answer (nothing in the library says what colour the Aurora 3 is, yet the system answers with the weight sentence, the "right topic, missing attribute" failure of llm.03), and a correct refusal. One example of each tells you nothing about how often each happens. That is what the rest of the chapter measures.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw an evaluation harness as a factory line. On the left a stack of cards (the dataset), each card showing a question and its gold answer, with some cards stamped 'no answer exists'. The cards move through a box labelled 'system under test' (with six dials: chunking, title, retriever, rerank, top_k, min_coverage) and come out paired with the system's answer. A scoring station stamps each pair with small badges: 'retrieved', 'correct', 'false answer', 'wrong refusal'. At the end a dashboard shows each badge's percentage with an error bar."

### 1.3 Try it

1. Why is "it passed my five favourite questions" not an evaluation?
2. Why should you build the evaluation before improving the system?
3. What is different about testing an LLM application compared with testing a function that adds two numbers?

<details><summary>Answer</summary>

1. Five questions you chose are biased towards ones you know work, too few to measure anything, and you will not notice a regression on the cases you did not try. An evaluation uses many cases chosen *before* you tune, including hard and unanswerable ones.
2. Without a baseline you cannot say whether a change helped: you would be comparing the new behaviour with your memory. The baseline is also what a later regression is detected against.
3. The function is deterministic and either right or wrong; an LLM application is *partly* wrong, often, on some inputs and not others, so the result is a rate with uncertainty, and a change can improve some cases while breaking others. You test with a dataset and statistics, not a single assertion.

</details>

## 2. Building evaluation datasets

### 2.1 Where cases come from

The dataset is the most valuable part of the evaluation, and the part people skimp on. Sources, from best to cheapest *(general knowledge: a common ordering in practice)*:

| Source | Strength | Weakness |
|---|---|---|
| **Real user questions** (logs, support tickets, search queries) | the real distribution, with real misspellings and paraphrases | needs a running system or an old archive; may contain private data (anonymise) |
| **Expert-written questions** | precise, can target hard cases | few, and written in the documents' vocabulary |
| **Failures you found** | every bug becomes a permanent test | biased towards past problems |
| **Synthetic questions** (generated from your documents, by templates or by a model) | plentiful and cheap | narrow, repetitive, and wrong more often than hand labels |
| **Adversarial and edge cases** (empty input, other languages, prompt injection, off-topic) | find breakage | not representative of normal traffic |

Deliberately include **questions with no answer** in the library. A system that never sees them can never be measured for the failure that most damages trust (llm.03 section 7).

### 2.2 A case needs a checkable gold answer

A good case is not "a question and a nice answer". It carries what a **program can check**: here, the gold **document** and a **phrase** that the answering passage must contain (so an answer is *correct* if it contains that phrase, and a retrieved passage is *relevant* if it is from the gold document and contains it). Unanswerable cases carry no gold answer. Each case also has **tags** so results can be sliced ("paraphrased", "numeric", "attribute-missing"). `evalset.py` has the case type, a validator, a fingerprint, a deterministic dev/test split and a labelling-agreement measure.

```python run
(pkg / "evalset.py").write_text(r'''"""evalset: build, check, split and fingerprint an evaluation dataset."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class EvalCase:
    id: str
    question: str
    answerable: bool
    gold_doc: str | None = None
    gold_phrase: str | None = None
    tags: tuple = ()
    source: str = "hand"                 # "hand" or "synthetic"


def kestrel_cases(kd) -> list[EvalCase]:
    """The hand-written questions of llm.03, as EvalCases."""
    cases = [EvalCase(f"n{i:02d}", q, True, d, p, ("normal",)) for i, (q, d, p) in enumerate([x for x in kd.QUESTIONS if x[1]], 1)]
    cases += [EvalCase(f"p{i:02d}", q, True, d, p, ("paraphrased",)) for i, (q, d, p) in enumerate(kd.HARD_QUESTIONS, 1)]
    cases += [EvalCase(f"u{i:02d}", q, False, None, None, ("unanswerable", "off-library")) for i, (q, d, p) in enumerate([x for x in kd.QUESTIONS if not x[1]], 1)]
    return cases


def generate_synthetic(docs) -> list[EvalCase]:
    """Template questions from document text. Cheap and plentiful, but narrow: it only asks what the templates know."""
    cases, n = [], 0
    for d in docs:
        if d["type"] != "product":
            continue
        text = " ".join(t for _, t in d["sections"])
        title = d["title"]
        for pattern, template, unit, tag in [(r"weigh(?:ing|s) ([\d.]+) (kg|g)\b", "How much does the {t} weigh?", None, "numeric"),
                                              (r"waterproof rating of (\d+) mm", "What is the waterproof rating of the {t}?", "mm", "numeric"),
                                              (r"comfort rating of (-?\d+) C", "What is the comfort rating of the {t}?", "C", "numeric")]:
            m = re.search(pattern, text)
            if m:
                n += 1
                phrase = f"{m.group(1)} {m.group(2) if unit is None else unit}"
                cases.append(EvalCase(f"s{n:02d}", template.format(t=title), True, d["id"], phrase, ("synthetic", tag), "synthetic"))
        n += 1
        cases.append(EvalCase(f"s{n:02d}", f"What colour is the {title}?", False, None, None, ("synthetic", "unanswerable", "attribute-missing"), "synthetic"))
    return cases


def tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def near_duplicates(cases, threshold: float = 0.8) -> list[tuple[str, str, float]]:
    out = []
    for i, a in enumerate(cases):
        for b in cases[i + 1:]:
            ta, tb = tokens(a.question), tokens(b.question)
            jac = len(ta & tb) / len(ta | tb) if ta | tb else 0.0
            if jac >= threshold:
                out.append((a.id, b.id, round(jac, 2)))
    return out


def drop_duplicates_of(hand, synthetic):
    """Remove synthetic cases that ask for the same fact (same gold document and phrase) as a hand-written case.
    Otherwise one fact is counted twice and the system's score on it counts double. Returns (kept, removed)."""
    seen = {(c.gold_doc, c.gold_phrase) for c in hand if c.answerable}
    kept = [c for c in synthetic if not (c.answerable and (c.gold_doc, c.gold_phrase) in seen)]
    return kept, [c for c in synthetic if c not in kept]


def validate_cases(cases, docs) -> list[str]:
    """Problems that would make every later number meaningless."""
    problems, seen = [], set()
    text_of = {d["id"]: " ".join(t for _, t in d["sections"]).lower() for d in docs}
    for c in cases:
        if c.id in seen:
            problems.append(f"{c.id}: duplicate id")
        seen.add(c.id)
        if not c.question.strip().endswith("?"):
            problems.append(f"{c.id}: the question does not end with '?'")
        if c.answerable:
            if not c.gold_doc or not c.gold_phrase:
                problems.append(f"{c.id}: an answerable case needs gold_doc and gold_phrase")
            elif c.gold_doc not in text_of:
                problems.append(f"{c.id}: gold document {c.gold_doc!r} does not exist")
            elif c.gold_phrase.lower() not in text_of[c.gold_doc]:
                problems.append(f"{c.id}: the gold phrase {c.gold_phrase!r} is not in {c.gold_doc}")
        elif c.gold_doc or c.gold_phrase:
            problems.append(f"{c.id}: an unanswerable case must not have a gold answer")
    return problems


def dataset_hash(cases) -> str:
    """A fingerprint of the dataset: change one character of one question and it changes."""
    payload = json.dumps([asdict(c) for c in sorted(cases, key=lambda c: c.id)], sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


def split_dev_test(cases, test_fraction: float = 0.3, salt: str = "v1"):
    """Deterministic split by hashing the case id: the same case is always on the same side, even when cases are added."""
    dev, test = [], []
    for c in cases:
        h = int(hashlib.sha256((salt + c.id).encode()).hexdigest(), 16) % 1000 / 1000
        (test if h < test_fraction else dev).append(c)
    return dev, test


def save_jsonl(cases, path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for c in cases:
            f.write(json.dumps({**asdict(c), "tags": list(c.tags)}, ensure_ascii=False) + "\n")


def load_jsonl(path) -> list[EvalCase]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                row["tags"] = tuple(row.get("tags", ()))
                out.append(EvalCase(**row))
    return out


def cohens_kappa(a: list, b: list) -> float:
    """Agreement between two labellers beyond what chance would give. 1 = perfect, 0 = chance, <0 = worse than chance."""
    n = len(a)
    if n == 0 or n != len(b):
        raise ValueError("need two non-empty lists of equal length")
    labels = sorted(set(a) | set(b))
    observed = sum(x == y for x, y in zip(a, b)) / n
    expected = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)
''', encoding="utf-8")
print("wrote evalset.py:", 135, "lines")
```
```text
wrote evalset.py: 135 lines
```

```python run
import evalset as es
hand = es.kestrel_cases(kd)
print(len(hand), "hand-written cases:", dict(collections.Counter(t for c in hand for t in c.tags if t in ("normal", "paraphrased", "unanswerable"))))
print("example answerable  :", hand[1])
print("example unanswerable:", hand[-1])
print("problems found by the validator:", es.validate_cases(hand, kd.DOCS))
```
```text
44 hand-written cases: {'normal': 24, 'paraphrased': 12, 'unanswerable': 8}
example answerable  : EvalCase(id='n02', question='Can I get my money back for a sale item?', answerable=True, gold_doc='returns-policy', gold_phrase='Final Sale', tags=('normal',), source='hand')
example unanswerable: EvalCase(id='u08', question='What is a good recipe for chocolate cake?', answerable=False, gold_doc=None, gold_phrase=None, tags=('unanswerable', 'off-library'), source='hand')
problems found by the validator: []
```

### 2.3 The validator earns its keep

Datasets rot: a gold phrase is retyped with a typo, a document changes and the phrase disappears, a case is added twice. Each of these silently corrupts every later number, which is why `validate_cases` is run **every time** the dataset loads. Break five cases on purpose and see it catch each one:

```python run
broken = [
    es.EvalCase("b1", "How long is the warranty on tents?", True, "warranty", "12-year"),                # phrase not in the document
    es.EvalCase("b2", "How long is the warranty on tents?", True, "no-such-doc", "5-year"),             # gold document does not exist
    es.EvalCase("b3", "How long is the warranty on tents", True, "warranty", "5-year"),                 # no question mark
    es.EvalCase("b4", "Do you sell ropes?", False, "shipping", "free"),                                  # unanswerable but has a gold answer
    es.EvalCase("b1", "Is it waterproof?", True, "tent-aurora-3", "3000 mm"),                           # duplicate id
]
for p in es.validate_cases(broken, kd.DOCS):
    print(" -", p)
```
```text
 - b1: the gold phrase '12-year' is not in warranty
 - b2: gold document 'no-such-doc' does not exist
 - b3: the question does not end with '?'
 - b4: an unanswerable case must not have a gold answer
 - b1: duplicate id
```

### 2.4 Synthetic cases: cheap, and dangerous

Writing 40 questions by hand takes an afternoon; generating 400 takes a second. `generate_synthetic` builds questions from document text with templates ("How much does the {product} weigh?", with the gold phrase read from the sentence), and, for the unanswerable side, "What colour is the {product}?" for every product (no document gives a colour, so the right behaviour is a refusal). That is a cheap way to get **many** cases of the specific failure that matters. Three warnings, then the code:

1. **Duplicates double-count a fact.** If a synthetic case asks what a hand-written case asks, the system's score on that fact counts twice. We remove them by comparing (document, phrase).
2. **Synthetic questions copy the documents' vocabulary**, so they are easier than real user questions. Never report synthetic results as if they were user results; **tag them** so they can be reported separately.
3. **If a model generates them, a model checks them** *(general knowledge)*: LLM-generated questions often have wrong or unanswerable gold answers. Validate and sample-check by hand.

```python run
synthetic_all = es.generate_synthetic(kd.DOCS)
synthetic, removed = es.drop_duplicates_of(hand, synthetic_all)
print(f"{len(synthetic_all)} synthetic cases generated; {len(removed)} dropped because a hand-written case already asks for the same fact: {[(c.id, c.question) for c in removed]}")
print("kept:", dict(collections.Counter(t for c in synthetic for t in c.tags if t in ("numeric", "attribute-missing"))))
cases = hand + synthetic
print(f"\nfull dataset: {len(cases)} cases | answerable {sum(c.answerable for c in cases)} | unanswerable {sum(not c.answerable for c in cases)}")
print("validator:", es.validate_cases(cases, kd.DOCS) or "clean")
print("sample synthetic :", synthetic[0].question, "->", synthetic[0].gold_phrase)
print("near-duplicate pairs among all cases at threshold 0.95:", es.near_duplicates(cases, 0.95))
```
```text
37 synthetic cases generated; 3 dropped because a hand-written case already asks for the same fact: [('s01', 'How much does the Aurora 3 Tent weigh?'), ('s05', 'What is the waterproof rating of the Summit 4 Tent?'), ('s08', 'What is the comfort rating of the Ember Sleeping Bag?')]
kept: {'numeric': 20, 'attribute-missing': 14}

full dataset: 78 cases | answerable 56 | unanswerable 22
validator: clean
sample synthetic : What is the waterproof rating of the Aurora 3 Tent? -> 3000 mm
near-duplicate pairs among all cases at threshold 0.95: []
```

Templated questions look alike by construction ("What colour is the X Tent?" against "What colour is the Y Tent?"), so a near-duplicate detector at a lax threshold flags all of them; at 0.95 it flags only true copies. Use such a detector to *find candidates for review*, not to decide automatically.

### 2.5 Do two people agree on the labels?

If two careful humans disagree about what the right answer is, the metric you build on those labels has a ceiling. Measure the **agreement** between two labellers on the same items with **Cohen's kappa**: observed agreement corrected for the agreement you would get by chance (if both said "yes" most of the time, they would agree often by luck). 1 means perfect agreement, 0 means no better than chance.

```python run
# Two people judged the same 20 system answers as acceptable (1) or not (0).
labeller_a = [1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1]
labeller_b = [1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1]
agree = sum(a == b for a, b in zip(labeller_a, labeller_b)) / len(labeller_a)
print(f"raw agreement {agree:.2f}  |  Cohen's kappa {es.cohens_kappa(labeller_a, labeller_b):.2f}")
print("kappa of the 'say yes to everything' labeller against labeller A:", round(es.cohens_kappa(labeller_a, [1] * 20), 2))
```
```text
raw agreement 0.85  |  Cohen's kappa 0.66
kappa of the 'say yes to everything' labeller against labeller A: 0.0
```

Raw agreement of 0.85 looks excellent, but kappa is lower (0.66) because both labellers say "acceptable" most of the time, so a lot of that agreement was chance. And the labeller who says "yes" to everything agrees with A on 14 of 20 items yet has kappa of exactly 0: the measure sees through it. A rough reading *(general knowledge)*: above 0.8 is strong agreement, 0.6 to 0.8 substantial, below 0.4 weak. If humans only reach 0.5 on your labelling task, **a metric cannot be more accurate than that**, and the fix is clearer labelling rules, not a bigger model.

### 2.6 Dev set, test set, and a fingerprint

Split the cases into a **dev set** you look at while improving the system and a **test set** you keep for confirming results. The reason is the same as in ds.04: if you tune on every case, your score measures how well you fit *those cases*. The split is deterministic (a hash of the case id), so a case never moves from test to dev when you add new cases, and `dataset_hash` fingerprints the whole set so that two results can only be compared when they used the **same** dataset.

```python run
dev, test = es.split_dev_test(cases)
print(f"dev {len(dev)} cases, test {len(test)} cases (unanswerable: {sum(not c.answerable for c in dev)} dev, {sum(not c.answerable for c in test)} test)")
print("dataset fingerprint:", es.dataset_hash(cases))
altered = [es.EvalCase(cases[0].id, cases[0].question + "!", *[getattr(cases[0], f) for f in ("answerable", "gold_doc", "gold_phrase", "tags", "source")])] + cases[1:]
print("after changing one character of one question:", es.dataset_hash(altered))
dev2, test2 = es.split_dev_test(cases + [es.EvalCase("new1", "Do gift cards expire?", True, "faq-general", "never expire")])
print("old test cases still in test after adding a case:", {c.id for c in test} <= {c.id for c in test2})
es.save_jsonl(cases, ws / "cases.jsonl")
print("saved", len(cases), "cases to cases.jsonl (one JSON object per line: easy to diff in git)")
```
```text
dev 58 cases, test 20 cases (unanswerable: 15 dev, 7 test)
dataset fingerprint: 10b400c097f9
after changing one character of one question: 92585d3d4adc
old test cases still in test after adding a case: True
saved 78 cases to cases.jsonl (one JSON object per line: easy to diff in git)
```

With **20 test cases** the test set is small, and section 6 will show exactly how little a set that small can confirm. That is not a bug in the split; it is a fact about small datasets, and one reason to keep collecting cases.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a funnel of evaluation cases. On top, five source buckets (real user questions, expert-written, past failures, synthetic, adversarial) pour into a 'validator' gate that bounces three red cards (gold phrase missing, duplicate id, no question mark). Below the gate, a dedupe sieve removes synthetic cards that repeat a hand-written fact. Then a splitter sends 70% of the cards left into a 'dev' bin (open, used while improving) and 30% into a locked 'test' bin. Stamp the whole dataset with a fingerprint badge like 'a41c9e…'."

### 2.7 Try it

1. Your evaluation has 100 questions and all of them have an answer in the library. What important behaviour can you not measure?
2. Why is a validator that runs on every load worth the trouble?
3. Two annotators agree on 90 % of 100 items, but 90 of the items are "acceptable" for both. Is that strong agreement?

<details><summary>Answer</summary>

1. Refusing correctly when the answer is **not** in the library, and the rate of confident wrong answers, the failure that damages trust most. Add unanswerable cases (a quarter or so of the set is not unreasonable for a support bot).
2. A silent dataset error (a broken gold phrase, a duplicate, a deleted document) corrupts every later number without any visible failure. The validator turns it into an immediate error.
3. Not necessarily. If both say "acceptable" for 90 % of items, chance alone gives about 0.9 x 0.9 + 0.1 x 0.1 = 0.82 agreement, so 0.90 is only a little above chance: kappa is about 0.44. Check kappa, not raw agreement.

</details>

## 3. Evaluating retrieval separately from generation

### 3.1 Why separate

A wrong answer has two possible parents. **Retrieval failed**: the passage that holds the answer never reached the answerer, so no answerer could have got it right. Or **generation failed**: the right passage was there, and the answerer ignored it, mangled it, or refused. The fixes are completely different (better chunking and embeddings against a better prompt or model), so a single "answer accuracy" number hides what to work on.

For each *answerable* case, check two things: did retrieval put a relevant passage among the sources (**retrieval hit**), and was the final answer **correct**? That gives four cases:

| | answer correct | answer wrong or refused |
|---|---|---|
| **retrieval hit** | working | **generation failure** (the answerer had the right passage) |
| **retrieval miss** | lucky (right for the wrong reason) | **retrieval failure** |

For *unanswerable* cases the measure is simply whether the system **refused** (a *false answer* is the failure).

### 3.2 The scoring code and the runner

`evalmetrics.py` scores one case (section 4 discusses each metric's blind spots). `runner.py` runs a system over a dataset and summarises with uncertainty; it also holds the comparison and the gate used in sections 6 to 8. `stats.py` supplies the intervals, explained in section 6.

```python run
(pkg / "stats.py").write_text(r'''"""stats: how sure can we be, with a few dozen test questions?"""
from __future__ import annotations

import math

import numpy as np


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% interval for a proportion. Better than mean +/- 2 standard errors when n is small or p is near 0 or 1."""
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def bootstrap_ci(values, n_boot: int = 2000, seed: int = 0, level: float = 0.95) -> tuple[float, float]:
    """Resample the per-question scores with replacement; the spread of the means is the uncertainty."""
    v = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, len(v), size=(n_boot, len(v)))].mean(axis=1)
    lo = (1 - level) / 2
    return float(np.quantile(means, lo)), float(np.quantile(means, 1 - lo))


def paired_difference(new, base, n_boot: int = 4000, seed: int = 0) -> dict:
    """Per-question differences between two systems on the SAME questions. Returns the mean difference, its 95% interval,
    and a verdict: 'better', 'worse' or 'unclear' (the interval contains 0)."""
    d = np.asarray(new, dtype=float) - np.asarray(base, dtype=float)
    lo, hi = bootstrap_ci(d, n_boot, seed)
    verdict = "better" if lo > 0 else "worse" if hi < 0 else "unclear"
    return {"mean_diff": float(d.mean()), "ci_low": lo, "ci_high": hi, "verdict": verdict,
            "improved": int((d > 0).sum()), "worsened": int((d < 0).sum()), "n": int(len(d))}


def sign_test_p(improved: int, worsened: int) -> float:
    """Exact two-sided sign test (McNemar's exact test for yes/no scores): among the questions that CHANGED,
    is the split between better and worse more lopsided than chance?"""
    n = improved + worsened
    if n == 0:
        return 1.0
    k = min(improved, worsened)
    p = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def sample_size_paired(sd_of_differences: float, smallest_effect: float, z_alpha: float = 1.96, z_power: float = 0.84) -> int:
    """Questions needed to detect a mean paired difference of `smallest_effect` (95% confidence, 80% power)."""
    return math.ceil(((z_alpha + z_power) * sd_of_differences / smallest_effect) ** 2)
''', encoding="utf-8")
print("wrote stats.py:", 52, "lines")
```
```text
wrote stats.py: 52 lines
```

```python run
(pkg / "evalmetrics.py").write_text(r'''"""evalmetrics: automatic scores for one answer. Each is cheap and deterministic, and each has a blind spot."""
from __future__ import annotations

import re
from collections import Counter


def words(text: str) -> list[str]:
    return re.findall(r"-?\d+(?:\.\d+)?|[a-z]+", text.lower())


def normalise(text: str) -> str:
    return " ".join(words(text))


def exact_match(pred: str, gold: str) -> bool:
    return normalise(pred) == normalise(gold)


def contains_phrase(pred: str, phrase: str) -> bool:
    return normalise(phrase) in normalise(pred)


def token_f1(pred: str, gold: str) -> float:
    """Overlap of words between the answer and a reference: F1 of precision and recall over word counts."""
    p, g = Counter(words(pred)), Counter(words(gold))
    common = sum((p & g).values())
    if not p or not g or common == 0:
        return 0.0
    precision, recall = common / sum(p.values()), common / sum(g.values())
    return 2 * precision * recall / (precision + recall)


def rouge1_recall(pred: str, ref: str) -> float:
    """What share of the reference's words does the answer contain? (ROUGE-1 recall.)"""
    r, p = Counter(words(ref)), Counter(words(pred))
    return sum((r & p).values()) / sum(r.values()) if r else 0.0


STOP = {"a", "an", "the", "is", "are", "of", "to", "in", "and", "or", "it", "for", "on", "with", "that", "this", "be", "by", "at"}


def support_score(answer: str, sources: list[str]) -> float:
    """Faithfulness proxy: share of the answer's content words that appear in the cited sources. Numbers that do NOT appear
    in the sources count as total failure (0.0), because an invented figure is the worst kind of unsupported claim."""
    src = set(words(" ".join(sources)))
    content = [w for w in words(answer) if w not in STOP]
    if not content:
        return 1.0
    if any(re.fullmatch(r"-?\d+(?:\.\d+)?", w) and w not in src for w in content):
        return 0.0
    return sum(w in src for w in content) / len(content)


def gold_sentence(doc_text: str, phrase: str) -> str:
    for s in re.split(r"(?<=[.!?])\s+", doc_text):
        if phrase.lower() in s.lower():
            return s.strip()
    return ""


def score_case(case, result, chunk_text: dict, doc_text: dict) -> dict:
    """Scores for one case. Metrics that do not apply (retrieval on an unanswerable question) are None."""
    s = {"latency_ms": result.latency_ms, "prompt_tokens": result.prompt_tokens}
    if not case.answerable:
        s.update(retrieval_hit=None, rr=None, correct=None, wrong_refusal=None, token_f1=None, support=None, cite_ok=None,
                 false_answer=0 if result.refused else 1, ok=1 if result.refused else 0)
        return s
    rel = [i for i, cid in enumerate(result.retrieved) if cid.split(":")[0] == case.gold_doc and case.gold_phrase.lower() in chunk_text[cid].lower()]
    cited_text = [chunk_text[c] for c in result.cited]
    correct = (not result.refused) and contains_phrase(result.answer, case.gold_phrase)
    cite_ok = bool(result.cited) and all(case.gold_phrase.lower() in chunk_text[c].lower() for c in result.cited)
    ref = gold_sentence(doc_text[case.gold_doc], case.gold_phrase)
    s.update(retrieval_hit=1 if rel else 0, rr=1 / (rel[0] + 1) if rel else 0.0, correct=1 if correct else 0,
             wrong_refusal=1 if result.refused else 0, token_f1=0.0 if result.refused else token_f1(result.answer, ref),
             support=None if result.refused else support_score(result.answer, cited_text), cite_ok=1 if cite_ok else 0,
             false_answer=None, ok=1 if correct else 0)
    return s
''', encoding="utf-8")
print("wrote evalmetrics.py:", 78, "lines")
```
```text
wrote evalmetrics.py: 78 lines
```

```python run
(pkg / "runner.py").write_text(r'''"""runner: run a system over an evaluation set, summarise with uncertainty, compare two runs, and gate a change."""
from __future__ import annotations

import json
import statistics
from dataclasses import asdict

from evalmetrics import score_case
from evalset import dataset_hash
from stats import paired_difference, sign_test_p, wilson_interval

BINARY = ("retrieval_hit", "correct", "wrong_refusal", "false_answer", "ok", "cite_ok")
HEADLINE = ("ok", "retrieval_hit", "correct", "false_answer", "wrong_refusal")


def run_eval(system, cases, docs, label: str = "run") -> dict:
    chunk_text = {c.id: c.text for c in system.chunks}
    doc_text = {d["id"]: " ".join(t for _, t in d["sections"]) for d in docs}
    rows = []
    for case in cases:
        result = system.answer(case.question)
        rows.append({"id": case.id, "tags": list(case.tags), "answerable": case.answerable, "answer": result.answer, "refused": result.refused,
                     "retrieved": result.retrieved, "scores": score_case(case, result, chunk_text, doc_text)})
    return {"label": label, "config": asdict(system.cfg), "dataset_hash": dataset_hash(cases), "n": len(rows), "cases": rows}


def values(run: dict, metric: str, tag: str | None = None) -> dict:
    """{case id: score} for the cases where the metric applies."""
    return {r["id"]: r["scores"][metric] for r in run["cases"] if r["scores"].get(metric) is not None and (tag is None or tag in r["tags"])}


def summarize(run: dict, tag: str | None = None) -> dict:
    out = {}
    for m in BINARY + ("rr", "token_f1", "support", "latency_ms", "prompt_tokens"):
        v = list(values(run, m, tag).values())
        if not v:
            continue
        entry = {"n": len(v), "mean": sum(v) / len(v)}
        if m in BINARY:
            entry["ci"] = wilson_interval(int(sum(v)), len(v))
        out[m] = entry
    return out


LOWER_IS_BETTER = {"false_answer", "wrong_refusal", "latency_ms", "prompt_tokens"}


def compare_runs(base: dict, new: dict, metric: str = "ok", tag: str | None = None, alpha: float = 0.05) -> dict:
    """Paired comparison on the cases both runs share. `improved` and `worsened` count cases that moved in the GOOD and the BAD
    direction (for 'false_answer' a drop is good). Verdict: 'better', 'worse' or 'unclear'. Yes/no metrics use the exact sign test
    on the cases that changed; other metrics use a bootstrap interval. `diff` is always new minus base."""
    if base["dataset_hash"] != new["dataset_hash"]:
        raise ValueError("the two runs used different datasets: their numbers are not comparable")
    b, n = values(base, metric, tag), values(new, metric, tag)
    ids = sorted(set(b) & set(n))
    sign = -1.0 if metric in LOWER_IS_BETTER else 1.0
    benefit_new, benefit_base = [sign * n[i] for i in ids], [sign * b[i] for i in ids]
    d = paired_difference(benefit_new, benefit_base)
    out = {"n": d["n"], "diff": sign * d["mean_diff"], "improved": d["improved"], "worsened": d["worsened"],
           "ci_low": min(sign * d["ci_low"], sign * d["ci_high"]), "ci_high": max(sign * d["ci_low"], sign * d["ci_high"]),
           "p_sign": sign_test_p(d["improved"], d["worsened"]), "flipped": [i for i in ids if n[i] != b[i]]}
    if metric in BINARY:
        out["verdict"] = "unclear" if out["p_sign"] > alpha else ("better" if d["improved"] > d["worsened"] else "worse")
    else:
        out["verdict"] = d["verdict"]
    return out


DEFAULT_RULES = {"hard": {"false_answer": ("<=", 0.60), "retrieval_hit": (">=", 0.80), "ok": (">=", 0.50)},
                 "track": ["ok", "retrieval_hit", "false_answer", "wrong_refusal"], "warn_drop": 0.03}


def gate(base: dict, new: dict, rules: dict = DEFAULT_RULES) -> dict:
    """Decide whether a change may merge. FAIL on a broken hard threshold or on a tracked metric that got significantly WORSE;
    WARN on a drop that is too small to be sure about."""
    failures, warnings = [], []
    summary = summarize(new)
    for metric, (op, limit) in rules["hard"].items():
        mean = summary[metric]["mean"]
        if (op == "<=" and mean > limit) or (op == ">=" and mean < limit):
            failures.append(f"{metric} = {mean:.2f} violates the hard limit {op} {limit}")
    for metric in rules["track"]:
        d = compare_runs(base, new, metric)
        if d["verdict"] == "worse":
            failures.append(f"{metric} got significantly worse: {d['diff']:+.3f} (95% interval {d['ci_low']:+.3f} to {d['ci_high']:+.3f}; "
                            f"{d['worsened']} cases worse, {d['improved']} better; sign test p = {d['p_sign']:.3f})")
        elif d["worsened"] > d["improved"] and abs(d["diff"]) >= rules["warn_drop"]:
            warnings.append(f"{metric} moved {d['diff']:+.3f} the wrong way ({d['worsened']} worse, {d['improved']} better), but that is not provable with {d['n']} cases (p = {d['p_sign']:.2f})")
    return {"passed": not failures, "failures": failures, "warnings": warnings}


def save_run(run: dict, path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(run, f, indent=1)


def load_run(path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)
''', encoding="utf-8")
print("wrote runner.py:", 99, "lines")
```
```text
wrote runner.py: 99 lines
```

```python run
import runner, stats
from runner import run_eval, summarize

base = run_eval(RagSystem(kd.DOCS, Config()), cases, kd.DOCS, "baseline")
print("dataset", base["dataset_hash"], "|", base["n"], "cases")
s = summarize(base)
print(f"\n{'metric':<15}{'n':>4}{'value':>8}   95% interval (Wilson)")
for m in ("ok", "retrieval_hit", "correct", "wrong_refusal", "false_answer", "cite_ok"):
    lo, hi = s[m]["ci"]
    print(f"{m:<15}{s[m]['n']:>4}{s[m]['mean']:>8.2f}   [{lo:.2f}, {hi:.2f}]")
print(f"\nmean latency {s['latency_ms']['mean']:.2f} ms | mean prompt size {s['prompt_tokens']['mean']:.0f} tokens")
```
```text
dataset 10b400c097f9 | 78 cases

metric            n   value   95% interval (Wilson)
ok               78    0.53   [0.42, 0.63]
retrieval_hit    56    0.88   [0.76, 0.94]
correct          56    0.55   [0.42, 0.68]
wrong_refusal    56    0.30   [0.20, 0.43]
false_answer     22    0.55   [0.35, 0.73]
cite_ok          56    0.57   [0.44, 0.69]

mean latency 0.90 ms | mean prompt size 186 tokens
```

Read the denominators: `retrieval_hit`, `correct` and `wrong_refusal` are over the **answerable** cases; `false_answer` is over the **unanswerable** ones; `ok` is over all (answerable correct, or unanswerable refused). The **intervals are wide**: with 78 cases the baseline `ok` of about 0.5 is anywhere from about 0.4 to 0.6. Never read these as exact.

### 3.3 Diagnose: which stage failed?

```python run
rows = [r for r in base["cases"] if r["answerable"]]
diagnosis = collections.Counter()
for r in rows:
    hit, ok = r["scores"]["retrieval_hit"], r["scores"]["correct"]
    diagnosis[("hit" if hit else "miss", "correct" if ok else "wrong/refused")] += 1
print(f"{'':<14}{'answer correct':>16}{'wrong or refused':>19}")
for h in ("hit", "miss"):
    print(f"retrieval {h:<5}{diagnosis[(h, 'correct')]:>16}{diagnosis[(h, 'wrong/refused')]:>19}")
print("\nunanswerable cases:", collections.Counter("refused (right)" if r["refused"] else "answered (false answer)" for r in base["cases"] if not r["answerable"]))
```
```text
                answer correct   wrong or refused
retrieval hit                31                 18
retrieval miss                0                  7

unanswerable cases: Counter({'answered (false answer)': 12, 'refused (right)': 10})
```

The counts tell you where to look. Most failures sit in the **hit but wrong** cell: retrieval found the passage and the answerer still got it wrong or refused. In this system the answerer is a crude sentence picker with a coverage threshold, so that is where its weakness is. If most failures had been in the **miss** row, the work would be on chunking and embeddings instead. **Always look at this table before deciding what to improve.**

### 3.4 Slice by kind of question

An average hides the structure. Tags let you ask "where does the system fail?":

```python run
print(f"{'slice':<20}{'cases':>6}{'ok':>7}{'retrieval hit':>15}{'false answer':>14}{'wrong refusal':>15}")
for tag in ("normal", "paraphrased", "numeric", "unanswerable", "attribute-missing"):
    t = summarize(base, tag)
    cell = lambda m: f"{t[m]['mean']:.2f}" if m in t else "-"
    print(f"{tag:<20}{t['ok']['n']:>6}{cell('ok'):>7}{cell('retrieval_hit'):>15}{cell('false_answer'):>14}{cell('wrong_refusal'):>15}")
```
```text
slice                cases     ok  retrieval hit  false answer  wrong refusal
normal                  24   0.88           1.00             -           0.08
paraphrased             12   0.00           0.42             -           0.92
numeric                 20   0.50           1.00             -           0.20
unanswerable            22   0.45              -          0.55              -
attribute-missing       14   0.29              -          0.71              -
```

Now the system has a profile: **good** on normal questions and numeric lookups, **hopeless** on paraphrased questions (they never get a correct answer, even where retrieval finds the passage some of the time), and **confidently wrong** on the attribute-missing questions ("What colour is the X?"), where most get a false answer. Neither number would have been visible in the single average. Each slice is also *small*, which is why it carries a wide interval; a slice with 12 cases is an indication, not a measurement.

### 3.5 Read the failures

Numbers say how often; reading the failures says **why**. Make a habit of printing the worst cases and reading every one of them, at least on every release:

```python run
text_of = {c.id: c.text for c in system.chunks}
shown = 0
for r, case in zip(base["cases"], cases):
    if not case.answerable and not r["refused"] and shown < 3:
        print(f"FALSE ANSWER  Q: {case.question}\n              answered: {r['answer'][:75]}   (from {r['retrieved'][0]})")
        shown += 1
shown = 0
for r, case in zip(base["cases"], cases):
    if case.answerable and r["scores"]["retrieval_hit"] and not r["scores"]["correct"] and shown < 3:
        print(f"HIT BUT WRONG Q: {case.question}\n              refused: {r['refused']} | gold phrase {case.gold_phrase!r} was in {r['retrieved']}")
        shown += 1
```
```text
FALSE ANSWER  Q: Does the Aurora 3 come in red?
              answered: The Aurora 3 is a 3-person, 3-season tent weighing 2.9 kg.   (from tent-aurora-3:0)
FALSE ANSWER  Q: How much does the Summit 4 cost?
              answered: The Summit 4 is a 4-person, 4-season expedition tent built for snow and hig   (from tent-summit-4:0)
FALSE ANSWER  Q: What colour is the Aurora 3 Tent?
              answered: The Aurora 3 is a 3-person, 3-season tent weighing 2.9 kg.   (from tent-aurora-3:0)
HIT BUT WRONG Q: How long does a refund take to arrive?
              refused: True | gold phrase '7 business days' was in ['returns-policy:1', 'returns-policy:0', 'returns-policy:2']
HIT BUT WRONG Q: Who pays customs duties on international orders?
              refused: False | gold phrase 'Customs duties' was in ['shipping:1', 'returns-policy:2', 'warranty:1']
HIT BUT WRONG Q: How warm is the Ember sleeping bag?
              refused: True | gold phrase '-5 C' was in ['sleeping-bag-ember:1', 'sleeping-bag-ember:0', 'sleeping-bag-cinder:0']
```

Reading these tells you things no metric does: the false answers are all "the entity matched, the attribute is absent" (add an attribute check); the hit-but-wrong ones are mostly questions whose words differ from the words of the answering sentence: the coverage threshold refuses some of them ("How long does a refund take to arrive?" against "reimbursed ... within 7 business days"), and others get a neighbouring sentence instead of the right one (the customs question). That is a to-do list, and each fix can be *verified* with the same evaluation.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 2x2 grid: columns 'answer correct' and 'answer wrong or refused', rows 'retrieval hit' and 'retrieval miss'. Place 59 small dots (answerable questions) into the cells in the proportions from the diagnosis table, with the dominant cell 'hit but wrong' highlighted and labelled 'generation failure: fix the answerer'. Beneath it draw a bar chart by question type (normal, paraphrased, numeric, attribute-missing) showing 'ok' with error bars, so the reader sees which types are failing."

### 3.6 Try it

1. A question has retrieval hit = yes and answer = wrong. Which component do you investigate first?
2. A question has retrieval hit = no and answer = correct. Is that good news?
3. Why report the sample size next to each slice?

<details><summary>Answer</summary>

1. The generation side (the prompt, the answerer or model, the refusal rule): the right passage was available to it.
2. Not really: it is "right for the wrong reason" (a lucky guess, or the answer was inferable from another passage). It hides a retrieval weakness that will show up on other questions, so do not count it as success when tracking retrieval.
3. A slice of 12 questions has a wide interval (one case moves it 8 points), so readers need the denominator to judge whether a difference between slices is real.

</details>

## 4. Automatic answer metrics and their blind spots

### 4.1 Cheap, deterministic scores

Once retrieval is checked, score the answer. Automatic metrics compare the answer with a **reference** by program, with no model. They are fast, free, repeatable and **each has a blind spot**: a case where it is confidently wrong. Know the blind spot before you trust the number.

| Metric | What it measures | Blind spot |
|---|---|---|
| **Exact match** | the answer equals the reference (after normalising case and punctuation) | any correct paraphrase scores 0 |
| **Contains the gold phrase** | the answer holds the key fact (`30 days`) | a verbose answer that adds a wrong claim still passes |
| **Token F1** | word overlap with a reference sentence | a **wrong** answer that copies most words scores high |
| **ROUGE-1 recall** | share of reference words present | rewards copying and length |
| **Support score** (faithfulness proxy) | share of the answer's words found in the cited sources; an **invented number scores 0** | cannot judge meaning, only word overlap |
| **Citation correctness** | the cited passage contains the gold phrase | says nothing about the answer text |

### 4.2 The blind spots, on five answers

Take one question, "How long do I have to return an unused item?", whose source sentence says *"You may return unused items in their original packaging within 30 days of delivery."* Score five different answers with every metric:

```python run
from evalmetrics import exact_match, contains_phrase, token_f1, rouge1_recall, support_score
source = "You may return unused items in their original packaging within 30 days of delivery."
answers = {
    "A  verbatim copy":                 "You may return unused items in their original packaging within 30 days of delivery.",
    "B  correct paraphrase":            "Items can be sent back within 30 days.",
    "C  WRONG number, near-copy":       "You may return unused items in their original packaging within 60 days of delivery.",
    "D  correct plus invented claim":   "Within 30 days, and refunds are paid in cash.",
    "E  refusal":                       "I could not find that in the library.",
}
print(f"{'answer':<32}{'exact':>6}{'has 30 days':>12}{'token F1':>10}{'ROUGE-1 R':>11}{'support':>9}")
for name, a in answers.items():
    print(f"{name:<32}{str(exact_match(a, source)):>6}{str(contains_phrase(a, '30 days')):>12}{token_f1(a, source):>10.2f}{rouge1_recall(a, source):>11.2f}{support_score(a, [source]):>9.2f}")
```
```text
answer                           exact has 30 days  token F1  ROUGE-1 R  support
A  verbatim copy                  True        True      1.00       1.00     1.00
B  correct paraphrase            False        True      0.36       0.29     0.57
C  WRONG number, near-copy       False       False      0.93       0.93     0.00
D  correct plus invented claim   False        True      0.35       0.29     0.50
E  refusal                       False       False      0.09       0.07     0.00
```

Each column is wrong about at least one row, and you can read exactly where:

- **Exact match** rejects B, a perfectly good answer, because it is not word-for-word.
- **Token F1** gives C, the **wrong** answer, a score of 0.93, **far higher than** the correct paraphrase B (0.36): it measures word overlap, and a one-digit change does not move it. This is the single most important lesson of this section: *an overlap metric can rank a wrong answer above a right one.*
- **Contains the gold phrase** correctly separates C (wrong) from B (right), but it cannot see D's invented claim: "refunds are paid in cash" is false for this library (llm.03: refunds are never paid in cash) and the check still passes.
- **Support** catches D (0.50, because "refunds are paid in cash" is not in the source) and gives C **0.00** because the invented number 60 is not in the source. But it is also lowish for the correct paraphrase B (0.57), because "sent back" is not a word of the source: word presence punishes paraphrase, and a wrong answer made of source words rearranged to say something else would pass.
- All the metrics treat the refusal (E) as a failure on an answerable question, which is right here; on an **unanswerable** question the refusal is the right answer, so scoring must depend on whether the case is answerable (as `score_case` does).

The practical rule: **use the metric that matches the failure you care about, and use several**. Here the primary correctness check is "contains the gold phrase", plus support to catch unsupported additions, plus a citation check, and token F1 is kept only as a rough trend line.

### 4.3 Refusal is a trade-off, so measure both sides

For a system that can say "I don't know" you must track two rates together: how often it **answers wrongly when it should refuse** (the false answer rate) and how often it **refuses when it should answer** (the wrong refusal rate). Improving one by moving the threshold usually worsens the other, so a change that "fixes false answers" must be checked against what it costs:

```python run
def run_with(**cfg):
    return run_eval(RagSystem(kd.DOCS, Config(**cfg)), cases, kd.DOCS, str(cfg))

print(f"{'min_coverage':>13}{'answered':>10}{'answer precision':>18}{'false answer rate':>19}{'wrong refusal rate':>20}{'ok':>7}")
for cov in (0.0, 0.3, 0.4, 0.6, 0.8):
    r = run_with(min_coverage=cov)
    answered = [x for x in r["cases"] if not x["refused"]]
    right = sum(1 for x in answered if x["answerable"] and x["scores"]["correct"])
    s = summarize(r)
    print(f"{cov:>13.1f}{len(answered):>10}{right / len(answered) if answered else 0:>18.2f}{s['false_answer']['mean']:>19.2f}{s['wrong_refusal']['mean']:>20.2f}{s['ok']['mean']:>7.2f}")
```
```text
 min_coverage  answered  answer precision  false answer rate  wrong refusal rate     ok
          0.0        74              0.46               0.91                0.04   0.46
          0.3        54              0.59               0.64                0.29   0.51
          0.4        51              0.61               0.55                0.30   0.53
          0.6        39              0.59               0.45                0.48   0.45
          0.8        12              0.92               0.00                0.79   0.42
```

Read it as a risk-coverage curve. At `0.0` the system answers everything: its **answer precision** (the share of its answers that are right) is the lowest and the false answer rate is high. Raising the threshold makes it **answer less** and **more precisely**, down to a false answer rate of zero at `0.8`... and a wrong refusal rate near 80 %, so it is nearly useless: it is "safe" only because it has stopped doing its job. No single number is the right one; the right setting depends on the cost of a wrong answer against a refusal (a medical bot and a trivia bot should pick very different points on this curve). This is exactly why the gate in section 8 tracks **both** rates.

### 4.4 Cost and latency are metrics too

Quality is not the only axis. Every setting changes **how much each query costs** and **how long it takes**. The prompt-size column (sources plus question plus instructions, in tokens) turns directly into money (llm.01 section 5). Compare `top_k`:

```python run
PRICE_PER_M_INPUT = 1.0                      # ILLUSTRATIVE dollars per million input tokens (llm.01)
print(f"{'top_k':>6}{'ok':>7}{'retrieval hit':>15}{'prompt tokens':>15}{'$ per 1,000 queries':>21}")
for k in (1, 3, 5, 8):
    s = summarize(run_with(top_k=k))
    print(f"{k:>6}{s['ok']['mean']:>7.2f}{s['retrieval_hit']['mean']:>15.2f}{s['prompt_tokens']['mean']:>15.0f}{s['prompt_tokens']['mean'] * 1000 * PRICE_PER_M_INPUT / 1e6:>21.4f}")
```
```text
 top_k     ok  retrieval hit  prompt tokens  $ per 1,000 queries
     1   0.59           0.82            137               0.1373
     3   0.53           0.88            186               0.1864
     5   0.53           0.89            235               0.2346
     8   0.46           0.89            299               0.2989
```

More sources raise the retrieval hit (the answer is more likely to be among them) and **cost more tokens**, with a point of diminishing returns; and notice that a bigger `top_k` does **not** raise `ok` here: it **lowers** it (0.59, 0.53, 0.53, 0.46), because this answerer picks one sentence from all the sources and every extra source gives it another chance to pick a wrong sentence. (With a real model the extra context may help or may distract it; you measure.) An evaluation that reports only accuracy would miss half of every trade-off.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Plot a risk-coverage curve: x axis 'share of questions answered' (0 to 100%), y axis 'share of those answers that are right' (0 to 100%). Draw one curve for the Kestrel system as the refusal threshold goes from 0 to 0.8: starting at (100%, ~45%) and rising to a high precision at tiny coverage. Mark three points: 'answers everything', 'moderate threshold', 'refuses almost everything (safe but useless)'. Add a shaded band 'where a support bot should sit' and another 'where a trivia bot can sit'."

### 4.5 Try it

1. An answer scores token F1 0.9 against the reference. Is it good?
2. Why must the correctness check for an unanswerable question be different from that for an answerable one?
3. A change drops the false answer rate from 55 % to 20 % and the wrong refusal rate rises from 30 % to 60 %. Is it an improvement?

<details><summary>Answer</summary>

1. Not necessarily. F1 measures word overlap, so a wrong answer that copies most of the reference words scores high (our answer C scored 0.93). Check the key fact with a phrase or number check as well.
2. On an unanswerable question there is no gold phrase to find; the right behaviour is to **refuse**, and any answer is a false answer. Scoring an unanswerable case with the answerable rule would punish the correct refusal.
3. It is a **trade-off**, not an improvement: half the false answers are gone, but the system now refuses twice as many questions it could answer. Whether it is acceptable depends on your costs; the evaluation's job is to show both numbers, not one.

</details>

## 5. Model-graded evaluation and its limits

### 5.1 Why a judge

Some answers cannot be checked with a phrase: free-text explanations, summaries, answers whose wording varies. For these, a common approach *(general knowledge)* is to ask **another language model to grade**: give it the question, a reference answer and the system's answer, plus a rubric, and ask for a verdict in a fixed format (llm.02: structured output, validated). This is called **model-graded evaluation** or **LLM as judge**. It is flexible and scales, and it comes with its own problems, so a judge is itself something to **evaluate**.

Known tendencies of model judges *(general knowledge, from published evaluations; not measured here)*:

| Bias | What it looks like |
|---|---|
| **Verbosity bias** | longer, more elaborate answers are rated higher regardless of correctness |
| **Position bias** | in a side-by-side comparison, the answer shown first (or second) wins more often |
| **Leniency** | the judge accepts plausible-sounding wrong answers |
| **Self-preference** | a model rates its own style of answer higher than another model's |
| **Unreadable or inconsistent output** | the verdict cannot be parsed, or changes between identical calls |

The prompt below is the shape of a judge prompt: a clear rubric, the reference, a strict output format.

```python run
(pkg / "judge.py").write_text(r'''"""judge: model-graded evaluation ("LLM as judge"), plus the checks that tell you whether to trust a judge.

SimulatedJudge is NOT a language model. It is a scripted grader whose accuracy and biases WE set, so we can check that our
detectors find them. A real judge would be a model called through the llm.02 client with the prompt from build_judge_prompt."""
from __future__ import annotations

import json
import random

JUDGE_PROMPT = """You are grading an answer to a question about a company's documents.

Question: {question}
Reference answer (correct): {reference}
Answer to grade: {answer}

Rules: the answer is "correct" only if it states the same facts as the reference, with the same numbers. Extra detail is fine if it does not
contradict the reference. A refusal ("I could not find that") is "incorrect" unless the reference says the information is unavailable.
Reply with ONE JSON object: {{"verdict": "correct" or "incorrect", "reason": "one sentence"}}"""


def build_judge_prompt(question: str, reference: str, answer: str) -> str:
    return JUDGE_PROMPT.format(question=question, reference=reference, answer=answer)


def parse_verdict(text: str) -> bool | None:
    """True for correct, False for incorrect, None if the reply cannot be read (count those: they are a failure of the judge)."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        v = json.loads(text[start:end + 1]).get("verdict")
    except json.JSONDecodeError:
        return None
    return {"correct": True, "incorrect": False}.get(v)


class SimulatedJudge:
    """accuracy: chance of the right verdict. leniency: extra chance of calling a WRONG answer correct. verbosity_bias: extra chance
    of 'correct' for long answers. position_bias: extra chance of picking the first answer in a pairwise comparison of equals."""

    def __init__(self, accuracy=0.92, leniency=0.0, verbosity_bias=0.0, position_bias=0.0, seed=0):
        self.accuracy, self.leniency, self.verbosity_bias, self.position_bias = accuracy, leniency, verbosity_bias, position_bias
        self.rng = random.Random(seed)

    def grade(self, answer: str, truth: bool) -> str:
        length_push = self.verbosity_bias * min(1.0, len(answer.split()) / 60)
        p_correct = (self.accuracy if truth else (1 - self.accuracy) + self.leniency) + length_push
        verdict = "correct" if self.rng.random() < min(1.0, max(0.0, p_correct)) else "incorrect"
        return json.dumps({"verdict": verdict, "reason": "simulated"})

    def pairwise(self, quality_a: float, quality_b: float) -> str:
        """Which answer is better, 'A' or 'B'? Equal quality exposes position bias."""
        if quality_a != quality_b:
            better = "A" if quality_a > quality_b else "B"
            return better if self.rng.random() < self.accuracy else ("B" if better == "A" else "A")
        return "A" if self.rng.random() < 0.5 + self.position_bias else "B"


def agreement_report(human: list[bool], judge: list[bool | None]) -> dict:
    """How well does the judge match human labels? Unreadable verdicts (None) are counted and treated as 'incorrect'."""
    unreadable = sum(j is None for j in judge)
    j = [bool(x) for x in judge]
    tp = sum(h and x for h, x in zip(human, j))
    tn = sum((not h) and (not x) for h, x in zip(human, j))
    fp = sum((not h) and x for h, x in zip(human, j))
    fn = sum(h and (not x) for h, x in zip(human, j))
    n = len(human)
    observed = (tp + tn) / n
    p_h, p_j = (tp + fn) / n, (tp + fp) / n
    expected = p_h * p_j + (1 - p_h) * (1 - p_j)
    kappa = 1.0 if expected == 1 else (observed - expected) / (1 - expected)
    return {"n": n, "agreement": observed, "kappa": kappa, "tp": tp, "tn": tn, "fp": fp, "fn": fn, "unreadable": unreadable,
            "false_accept_rate": fp / (fp + tn) if fp + tn else 0.0}
''', encoding="utf-8")
print("wrote judge.py:", 73, "lines")
```
```text
wrote judge.py: 73 lines
```

```python run
import judge as jg
print(jg.build_judge_prompt("How long do I have to return an unused item?", "Items may be returned within 30 days of delivery.", "Items can be sent back within 30 days."))
```
```text
You are grading an answer to a question about a company's documents.

Question: How long do I have to return an unused item?
Reference answer (correct): Items may be returned within 30 days of delivery.
Answer to grade: Items can be sent back within 30 days.

Rules: the answer is "correct" only if it states the same facts as the reference, with the same numbers. Extra detail is fine if it does not
contradict the reference. A refusal ("I could not find that") is "incorrect" unless the reference says the information is unavailable.
Reply with ONE JSON object: {"verdict": "correct" or "incorrect", "reason": "one sentence"}
```

`judge.py` also contains **`SimulatedJudge`**: *not* a language model, but a scripted grader with dials for accuracy, leniency, verbosity bias and position bias. It exists so we can do the part of model-graded evaluation that never depends on which model you use: **testing the judge**.

### 5.2 Step one: compare the judge with human labels

Before using a judge to decide anything, measure how often it agrees with **human labels** on a set of answers you have labelled yourself (50 to 100 is a typical minimum *(general knowledge)*). Report **agreement**, **kappa** (section 2.5), and above all the **false accept rate**: how often the judge calls a wrong answer correct, since that is what lets a regression through.

Here the "human labels" are the phrase-based correctness of the baseline system's 56 answers to answerable questions (a stand-in for labels a person would write), and three simulated judges grade them: a careful one, a lenient one, and a sloppy one.

```python run
answerable_rows = [(r, c) for r, c in zip(base["cases"], cases) if c.answerable]
human = [bool(r["scores"]["correct"]) for r, c in answerable_rows]
answers_text = [r["answer"] or "I could not find that in the library." for r, c in answerable_rows]

def judge_labels(simulated, seed_text_pairs=None):
    return [jg.parse_verdict(simulated.grade(a, t)) for a, t in zip(answers_text, human)]

print(f"{'judge':<30}{'agreement':>10}{'kappa':>7}{'false accepts':>15}{'unreadable':>12}")
for name, j in [("careful (accuracy 0.95)", jg.SimulatedJudge(accuracy=0.95, seed=1)),
                ("lenient (+0.30 on wrong answers)", jg.SimulatedJudge(accuracy=0.95, leniency=0.30, seed=1)),
                ("sloppy (accuracy 0.75)", jg.SimulatedJudge(accuracy=0.75, seed=1))]:
    rep = jg.agreement_report(human, judge_labels(j))
    print(f"{name:<30}{rep['agreement']:>10.2f}{rep['kappa']:>7.2f}{rep['false_accept_rate']:>15.2f}{rep['unreadable']:>12}")
print(f"\n(n = {len(human)} labelled answers: {sum(human)} correct, {len(human) - sum(human)} wrong)")
```
```text
judge                          agreement  kappa  false accepts  unreadable
careful (accuracy 0.95)             0.96   0.93           0.08           0
lenient (+0.30 on wrong answers)      0.82   0.62           0.40           0
sloppy (accuracy 0.75)              0.66   0.32           0.36           0

(n = 56 labelled answers: 31 correct, 25 wrong)
```

The careful judge agrees with the labels on nearly every item. The lenient judge's agreement (0.82) might look acceptable at a glance, but its **false accept rate of 0.40** is the standout: it approves two wrong answers in five and would let regressions pass. The sloppy judge shows up in both agreement and kappa. Two lessons: **agreement alone can hide a lenient judge**, so always look at the false accept rate; and with only 56 labelled answers, all of these figures carry a few points of noise (apply the intervals of section 6 to them too).

### 5.3 Step two: test for specific biases

Agreement with labels is not enough, because some biases only show up when you **change something that should not matter**. Two tests, both cheap:

- **Padding test (verbosity bias).** Take wrong answers, pad them with fluent but empty text, and re-grade. A fair judge's verdicts should not change.
- **Swap test (position bias).** Show the judge two answers of **equal quality** in both orders. A fair judge picks the first slot 50 % of the time.

```python run
wrong = [a for a, t in zip(answers_text, human) if not t][:20]
padded = [a + " Furthermore, this is a thorough, carefully considered and comprehensive statement that fully addresses every aspect of the question. " * 4 for a in wrong]

def pass_rate(j, texts, repeats=100):
    return sum(jg.parse_verdict(j.grade(t, False)) for _ in range(repeats) for t in texts) / (repeats * len(texts))

print(f"{'judge':<28}{'wrong answers judged correct':>30}{'same answers, padded':>24}")
for name, j in [("fair", jg.SimulatedJudge(accuracy=0.95, seed=5)), ("verbose-biased (0.4)", jg.SimulatedJudge(accuracy=0.95, verbosity_bias=0.4, seed=5))]:
    print(f"{name:<28}{pass_rate(j, wrong):>30.2f}{pass_rate(j, padded):>24.2f}")

print(f"\n{'judge':<28}{'first slot wins, equal answers':>32}")
for name, j in [("fair", jg.SimulatedJudge(seed=6)), ("position-biased (+0.2)", jg.SimulatedJudge(position_bias=0.2, seed=6))]:
    print(f"{name:<28}{sum(j.pairwise(1.0, 1.0) == 'A' for _ in range(4000)) / 4000:>32.2f}")
```
```text
judge                         wrong answers judged correct    same answers, padded
fair                                                  0.05                    0.04
verbose-biased (0.4)                                  0.12                    0.44

judge                         first slot wins, equal answers
fair                                                    0.50
position-biased (+0.2)                                  0.70
```

The fair judge's pass rate for wrong answers barely moves when they are padded; the verbose-biased judge's jumps. The fair judge picks the first of two identical answers about half the time; the biased one picks it about 70 % of the time. **These tests need no human labels and work for any judge**, so run them whenever you adopt or change a judge, and fix what they find (shuffle answer order, randomise which answer is "A", instruct the judge to ignore length, use a stricter rubric).

### 5.4 How to use a judge responsibly

| Practice | Why |
|---|---|
| Calibrate on **human-labelled** answers and report agreement, kappa and the false accept rate | the judge's own opinion is not ground truth |
| **Pin the judge** (the exact model and the prompt) and record it with every result | a changed judge changes every number, and scores from two judges are not comparable |
| Use the judge for **relative** comparisons on the same cases (new against base), not absolute claims | biases largely cancel when both systems are graded the same way |
| Randomise the **order** in pairwise comparisons; run both orders | position bias |
| Keep a **cheap deterministic check** beside it (phrase, number, citation) | a judge can be fooled; a phrase check cannot |
| Do not let the judge be the **system's own model** *(general knowledge: self-preference)* | a model tends to prefer its own answers |
| Budget the cost: judge calls are model calls (llm.01) on every case, every run | evaluation has a price |
| Re-check the judge against fresh human labels periodically | drift and your own data changing |

The simplest robust policy: **deterministic checks wherever the answer can be checked in code, a judge only for what cannot, and humans to calibrate the judge.**

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw two experiments on a judge. Experiment 1 'padding': a short WRONG answer card and the same card with three extra paragraphs of fluent text; a green/red verdict stamp for each. A fair judge stamps both red; a biased judge stamps the padded one green. Experiment 2 'swap': two identical answer cards shown as A then B, and then B then A; a fair judge picks the first slot 50% of the time (a balanced seesaw), a position-biased judge picks it 70% (a tilted seesaw)."

### 5.5 Try it

1. A judge agrees with your human labels on 92 % of answers. Is that enough to adopt it?
2. You pad every answer in your evaluation with a polite sentence and your judge's scores rise. What do you conclude?
3. Why is the judge's agreement measured on answers *you* labelled and not on answers the judge labelled?

<details><summary>Answer</summary>

1. Not yet. Look at the false accept rate (does it pass wrong answers?), kappa (is agreement beyond chance?), the number of labelled answers (a 92 % from 25 answers is imprecise), and run the padding and swap tests. A lenient judge can score high agreement on a set that is mostly correct answers.
2. The judge has a verbosity or politeness bias: the score depends on something unrelated to correctness. Change the rubric or the judge, or switch to deterministic checks for that metric.
3. Ground truth must come from outside the judge; if it labels its own work, any bias it has is invisible. The human labels are what the judge is measured against.

</details>

## 6. Statistics for small test sets

### 6.1 A score is an estimate

Your test set is a **sample** of all the questions users could ask. The score you compute is an estimate of the score on the whole population, and it would differ if you had drawn different questions. The **95 % confidence interval** is the range of true values consistent with what you saw. For a proportion such as "correct on 31 of 56 questions" the **Wilson interval** is a good choice for small samples (the plain "mean plus or minus two standard errors" misbehaves near 0 and 1, and is worse on small *n*). The width depends mostly on **how many questions you have**:

```python run
from stats import wilson_interval, bootstrap_ci, paired_difference, sign_test_p, sample_size_paired
print("the system gets 60% of the questions right. How sure can you be?")
print(f"{'questions':>10}{'95% interval':>18}{'width':>8}")
for n in (10, 20, 50, 100, 400, 1600):
    lo, hi = wilson_interval(round(0.6 * n), n)
    print(f"{n:>10}{f'[{lo:.2f}, {hi:.2f}]':>18}{hi - lo:>8.2f}")
print("\n10 out of 10 right:", tuple(round(x, 2) for x in wilson_interval(10, 10)), " <- not certainty: the lower end is about 0.72")
```
```text
the system gets 60% of the questions right. How sure can you be?
 questions      95% interval   width
        10      [0.31, 0.83]    0.52
        20      [0.39, 0.78]    0.39
        50      [0.46, 0.72]    0.26
       100      [0.50, 0.69]    0.19
       400      [0.55, 0.65]    0.10
      1600      [0.58, 0.62]    0.05

10 out of 10 right: (0.72, 1.0)  <- not certainty: the lower end is about 0.72
```

With 10 questions a measured 60 % could be anything from 30 % to 83 %. With 100 questions it is 50 % to 69 %. The width falls with the **square root** of the number of questions: to halve the uncertainty you need four times the data. This is the arithmetic behind "our test set is too small to say".

### 6.2 Comparing two systems: use the same questions (paired)

When you compare a new system with the baseline, do not compare two separate scores with their separate intervals. Both systems answer the **same questions**, so look at the **per-question differences**: most questions are the same in both systems and carry no information; the ones that **changed** are what matter. For a yes/no metric, count the questions that got **better** and the ones that got **worse**, and ask: if the change did nothing, would a split like this be surprising? That is the **sign test** (McNemar's exact test). For 5 improvements and 0 regressions, the chance of such a lopsided split by luck is `2 x (1/2)^5 = 0.0625`. For continuous metrics a **bootstrap** gives the interval: resample the per-question differences with replacement many times and see how much the mean wobbles.

Compare the baseline with `top_k = 1` (give the answerer only the top passage):

```python run
from runner import compare_runs
variant = run_with(top_k=1)
for metric in ("ok", "retrieval_hit", "false_answer", "wrong_refusal"):
    d = compare_runs(base, variant, metric)
    print(f"{metric:<15} change {d['diff']:+.3f}  95% interval [{d['ci_low']:+.3f}, {d['ci_high']:+.3f}]  better {d['improved']} / worse {d['worsened']}  sign test p = {d['p_sign']:.3f}  -> {d['verdict']}")
d = compare_runs(base, variant, "ok")
by_id = {c.id: c for c in cases}
print("\nquestions whose result changed on 'ok':")
for i in d["flipped"]:
    print("  ", i, by_id[i].question)
```
```text
ok              change +0.064  95% interval [+0.013, +0.115]  better 5 / worse 0  sign test p = 0.062  -> unclear
retrieval_hit   change -0.054  95% interval [-0.125, +0.000]  better 0 / worse 3  sign test p = 0.250  -> unclear
false_answer    change -0.000  95% interval [-0.000, -0.000]  better 0 / worse 0  sign test p = 1.000  -> unclear
wrong_refusal   change -0.000  95% interval [-0.000, -0.000]  better 0 / worse 0  sign test p = 1.000  -> unclear

questions whose result changed on 'ok':
   s02 What is the waterproof rating of the Aurora 3 Tent?
   s12 What is the waterproof rating of the Aurora 2 Tent?
   s15 What is the waterproof rating of the Summit 2 Tent?
   s18 What is the waterproof rating of the Summit 3 Tent?
   s21 What is the waterproof rating of the Dune 4 Tent?
```

`ok` rose by about 6 points, and all five questions that changed moved the **same way** (better in every case). Read them: all five are the same template, "waterproof rating of the X Tent". With three sources the answerer was picking the specification sentence of a *neighbouring* tent (it has just as many matching words); with one source that confusion cannot happen. So the "improvement" is concentrated in one kind of look-alike question, which is why you read the flipped cases and do not stop at the number. The bootstrap interval is entirely above zero. Yet the verdict is **unclear**: the exact test says that **5 improvements and 0 regressions** happens by chance about 6 times in 100 (p = 0.0625), just short of the usual 0.05 line. Two ways of measuring disagree at the margin, which is typical when only a handful of questions changed. The conservative reading for a yes/no metric is the exact test: *probably real, but not proven*. And notice what else moved: `retrieval_hit` fell, because with one source the right passage is sometimes absent. A change that helps one metric and hurts another is a **trade-off to decide on**, not a free win.

### 6.3 How many questions do you need?

If you want to detect an improvement of a given size with reasonable confidence, you need enough questions. The number depends on how much the per-question differences **vary** (their standard deviation) and on the **smallest effect you care about**:

```python run
diffs = np.array([variant_row["scores"]["ok"] - base_row["scores"]["ok"] for base_row, variant_row in zip(base["cases"], variant["cases"])])
sd = diffs.std()
print(f"per-question differences between the two systems: standard deviation {sd:.2f}")
print(f"{'smallest improvement to detect':>32}{'questions needed':>18}")
for effect in (0.20, 0.10, 0.05, 0.02):
    print(f"{effect:>32.2f}{sample_size_paired(sd, effect):>18}")
print(f"\nwith our {len(cases)} cases the smallest reliably detectable change is about {2.8 * sd / np.sqrt(len(cases)):.2f}")
```
```text
per-question differences between the two systems: standard deviation 0.24
  smallest improvement to detect  questions needed
                            0.20                12
                            0.10                48
                            0.05               189
                            0.02              1176

with our 78 cases the smallest reliably detectable change is about 0.08
```

(80 % power and 95 % confidence: the textbook setting *(general knowledge)*.) To reliably detect a **5-point** improvement you would need about **190 questions**; for **2 points**, well over a thousand. Our 78 cases can only reliably detect changes of around 8 points. That is the honest limit of the dataset: **a result of "unclear" often means "the test set is too small to tell", not "no effect"**. The remedy is more cases (especially of the kinds that fail), not cleverer statistics.

### 6.4 The trap of trying many variants

If you try 20 variants and report the best, you are fooling yourself: even if **none** is truly better, some will look significant by luck. Simulate it. Take the baseline's per-question results, create 20 "variants" that are the baseline with a few results flipped **at random** (no real effect), test each against the baseline at the usual 0.05 level, and repeat 1,000 times:

```python run
ok_base = np.array([r["scores"]["ok"] for r in base["cases"]])
rng = np.random.default_rng(0)

def null_variant(flip_rate):
    flips = rng.random(len(ok_base)) < flip_rate
    return np.where(flips, 1 - ok_base, ok_base)

def significant(variant_ok, alpha=0.05):
    improved = int(((variant_ok == 1) & (ok_base == 0)).sum())
    worsened = int(((variant_ok == 0) & (ok_base == 1)).sum())
    return sign_test_p(improved, worsened) < alpha

for flip_rate in (0.05, 0.15):
    single = np.mean([significant(null_variant(flip_rate)) for _ in range(2000)])
    any_of_20 = np.mean([any(significant(null_variant(flip_rate)) for _ in range(20)) for _ in range(500)])
    print(f"random changes to {flip_rate:.0%} of results: a single variant looks 'significant' {single:.1%} of the time; "
          f"at least one of 20 variants does {any_of_20:.1%} of the time")
print("with a Bonferroni correction (alpha / 20 = 0.0025) the chance for a single variant becomes", f"{np.mean([significant(null_variant(0.15), 0.0025) for _ in range(2000)]):.1%}")
```
```text
random changes to 5% of results: a single variant looks 'significant' 0.2% of the time; at least one of 20 variants does 8.8% of the time
random changes to 15% of results: a single variant looks 'significant' 1.8% of the time; at least one of 20 variants does 29.4% of the time
with a Bonferroni correction (alpha / 20 = 0.0025) the chance for a single variant becomes 0.0%
```

The exact test is conservative on small samples (a single null variant rarely passes), yet the chance that **at least one of twenty** harmless changes looks significant is far larger than for a single one (8.8 % against 0.2 % in the first line, 29 % against 1.8 % in the second). Three defences, in order of importance: **decide what to test before looking**; **confirm the winner on cases you did not tune on** (the test set, section 2.6); and **correct for the number of comparisons** (dividing the threshold by the number of variants, the Bonferroni correction, is blunt but safe).

### 6.5 Confirm on the held-out test set

The `top_k = 1` result looked promising on all 78 cases. The discipline is to look at it on the **dev** cases only, and then confirm on the held-out **test** cases:

```python run
def split_runs(cfg_a, cfg_b):
    out = {}
    for part, subset in (("dev", dev), ("test", test)):
        a = run_eval(RagSystem(kd.DOCS, cfg_a), subset, kd.DOCS, "a")
        b = run_eval(RagSystem(kd.DOCS, cfg_b), subset, kd.DOCS, "b")
        out[part] = compare_runs(a, b, "ok")
    return out

res = split_runs(Config(), Config(top_k=1))
for part in ("dev", "test"):
    d = res[part]
    print(f"{part:<5} n = {d['n']:>2}   ok change {d['diff']:+.3f}  better {d['improved']} / worse {d['worsened']}  sign test p = {d['p_sign']:.3f}  -> {d['verdict']}")
```
```text
dev   n = 58   ok change +0.086  better 5 / worse 0  sign test p = 0.062  -> unclear
test  n = 20   ok change +0.000  better 0 / worse 0  sign test p = 1.000  -> unclear
```

On the dev cases the change looks good; on the 20 test cases **nothing changed at all**, so the test set neither confirms nor refutes it: it is simply too small to hold a result of this size (section 6.3 said so). That is the right place to stop and **collect more test cases**, not to declare victory. A good evaluation culture treats "unconfirmed" as a real outcome.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a number line from -20 to +20 percentage points labelled 'change in accuracy, new minus base'. Show five horizontal confidence intervals (error bars): one entirely right of zero (green: 'better'), one entirely left (red: 'worse'), and three straddling zero (grey: 'unclear'), each with its sample size (20, 78, 400). Make the interval for n = 400 visibly narrower than for n = 20. Add a thought bubble over the straddling ones: 'could be nothing, could be real; need more questions'."

### 6.6 Try it

1. A new prompt scores 64 % against 60 % on the same 50 questions. Is the new prompt better?
2. Of the questions that changed, 9 improved and 3 got worse. Roughly, is that surprising under "no real change"?
3. You try 12 settings and one comes out "significant" at p = 0.03. What should you do?

<details><summary>Answer</summary>

1. You cannot say. On 50 questions a difference of 2 questions is well within the uncertainty (each score has an interval about 20 points wide). Look at the paired result (how many improved and how many worsened) and the sign test; most likely "unclear".
2. The exact sign test for 9 versus 3: 2 x P(at most 3 of 12) = 2 x (1 + 12 + 66 + 220)/4096 = 0.146. It would happen by chance about one time in seven: not convincing yet.
3. Be suspicious: with 12 comparisons a p of 0.03 is about what luck produces. Apply a correction (0.05 / 12 = 0.004), or **confirm on held-out cases** before believing it, and ideally decide the hypotheses before running them.

</details>

## 7. Experiments: change one thing, read the result honestly

### 7.1 One change at a time, on the same dataset

An **experiment** changes one setting, runs the same dataset, and compares with the baseline using the paired analysis of section 6. Changing two things at once makes it impossible to say which one mattered. Here is a table of variants of the system, each differing from the baseline in a single setting, with the four headline metrics, the prompt size, and what the paired comparison says about `ok`:

```python run
variants = [("baseline", {}),
            ("retriever: bm25 only", dict(retriever="bm25")),
            ("no rerank", dict(rerank=False)),
            ("no title in index", dict(with_title=False)),
            ("fixed chunks of 100", dict(chunking="fixed", size=100)),
            ("fixed chunks of 60", dict(chunking="fixed", size=60)),
            ("top_k 1", dict(top_k=1)),
            ("top_k 5", dict(top_k=5)),
            ("min_coverage 0.3", dict(min_coverage=0.3)),
            ("min_coverage 0.6", dict(min_coverage=0.6)),
            ("unknown-word check", dict(unknown_word_check=True))]
runs = {name: (base if not cfg else run_with(**cfg)) for name, cfg in variants}
print(f"{'variant':<22}{'ok':>6}{'hit':>6}{'false ans':>10}{'wrong ref':>10}{'tokens':>7}   {'ok change':>10}  {'better/worse':>13}{'p':>7}  verdict")
for name, run in runs.items():
    s = summarize(run)
    d = compare_runs(base, run, "ok")
    print(f"{name:<22}{s['ok']['mean']:>6.2f}{s['retrieval_hit']['mean']:>6.2f}{s['false_answer']['mean']:>10.2f}{s['wrong_refusal']['mean']:>10.2f}{s['prompt_tokens']['mean']:>7.0f}   "
          f"{d['diff']:>+10.3f}  {str(d['improved']) + ' / ' + str(d['worsened']):>13}{d['p_sign']:>7.3f}  {d['verdict']}")
```
```text
variant                   ok   hit false ans wrong ref tokens    ok change   better/worse      p  verdict
baseline                0.53  0.88      0.55      0.30    186       +0.000          0 / 0  1.000  unclear
retriever: bm25 only    0.53  0.88      0.55      0.30    178       +0.000          0 / 0  1.000  unclear
no rerank               0.54  0.86      0.55      0.30    185       +0.013          1 / 0  1.000  unclear
no title in index       0.51  0.84      0.59      0.23    188       -0.013          0 / 1  1.000  unclear
fixed chunks of 100     0.46  0.79      0.55      0.32    170       -0.064          0 / 5  0.062  unclear
fixed chunks of 60      0.47  0.71      0.55      0.34    148       -0.051          4 / 8  0.388  unclear
top_k 1                 0.59  0.82      0.55      0.30    137       +0.064          5 / 0  0.062  unclear
top_k 5                 0.53  0.89      0.55      0.30    235       +0.000          0 / 0  1.000  unclear
min_coverage 0.3        0.51  0.88      0.64      0.29    186       -0.013          1 / 2  1.000  unclear
min_coverage 0.6        0.45  0.88      0.45      0.48    186       -0.077          2 / 8  0.109  unclear
unknown-word check      0.56  0.88      0.00      0.48    186       +0.038         12 / 9  0.664  unclear
```

How to read a table like this without fooling yourself:

- **Most rows say `unclear`.** With 78 cases, only large effects clear the bar (section 6.3). That is information too: *for most of these knobs, you cannot tell they matter.*
- **`bm25 only`** differs from the baseline in **zero** cases: on this small library the vector part adds nothing, as llm.03 found. A change with no measurable effect and **less complexity** is a good change; this is how an evaluation lets you *remove* things safely.
- **`fixed chunks of 60`** is the one that is provably **bad**, but not on `ok`: look at retrieval (the `hit` column and the next block). Tiny chunks lose the answers.
- **`top_k 1`** has the best-looking `ok`, with the caveats of section 6.2 (concentrated in one question type, a lower retrieval hit, and not confirmable on the test set).
- **`unknown-word check`** has the most interesting profile and the next block examines it.

### 7.2 A real trade-off: the unknown-word check

The attribute-missing failure ("What colour is the Aurora 3?") needs a fix, not a threshold. The change tested above is a simple one: if the question contains a content word that appears **nowhere in the library** (`colour`, `red`, `vegan`), the library cannot answer it, so refuse. Look at it metric by metric:

```python run
checked = runs["unknown-word check"]
print(f"{'metric':<15}{'baseline':>9}{'new':>7}{'change':>8}   95% interval       better/worse   p       verdict")
for m in ("false_answer", "wrong_refusal", "retrieval_hit", "ok"):
    d = compare_runs(base, checked, m)
    print(f"{m:<15}{summarize(base)[m]['mean']:>9.2f}{summarize(checked)[m]['mean']:>7.2f}{d['diff']:>+8.2f}   [{d['ci_low']:+.2f}, {d['ci_high']:+.2f}]  {d['improved']:>6} / {d['worsened']:<4}  {d['p_sign']:<7.3f} {d['verdict']}")
print("\nby kind of question:")
for tag in ("attribute-missing", "normal", "paraphrased"):
    sb, sc = summarize(base, tag), summarize(checked, tag)
    key = "false_answer" if tag == "attribute-missing" else "wrong_refusal"
    print(f"  {tag:<18} {key:<14} {sb[key]['mean']:.2f} -> {sc[key]['mean']:.2f}")
newly = compare_runs(base, checked, "wrong_refusal")["flipped"]
print("\nquestions the change now refuses that it used to answer correctly:")
for i in newly[:6]:
    print("  -", by_id[i].question)
```
```text
metric          baseline    new  change   95% interval       better/worse   p       verdict
false_answer        0.55   0.00   -0.55   [-0.73, -0.36]      12 / 0     0.000   better
wrong_refusal       0.30   0.48   +0.18   [+0.09, +0.29]       0 / 10    0.002   worse
retrieval_hit       0.88   0.88   +0.00   [+0.00, +0.00]       0 / 0     1.000   unclear
ok                  0.53   0.56   +0.04   [-0.08, +0.15]      12 / 9     0.664   unclear

by kind of question:
  attribute-missing  false_answer   0.71 -> 0.00
  normal             wrong_refusal  0.08 -> 0.46
  paraphrased        wrong_refusal  0.92 -> 1.00

questions the change now refuses that it used to answer correctly:
  - Can I get my money back for a sale item?
  - Who pays for return postage when the item is faulty?
  - Does free delivery apply to my $80 order?
  - Which tent can handle snow and high wind?
  - Can I put my tent in the washing machine?
  - How heavy is the Nimbus rain jacket?
```

This is a clean, **statistically proven** trade-off: the change removes **every** false answer (12 questions better, none worse, p = 0.0005) and, at the same time, makes the system refuse **10 questions it used to answer** (none better, p = 0.002). Look at which: "money back" (the library says "reimbursed"), "faulty" (the library says "defective"), "snow", "loyalty": ordinary questions whose wording differs from the library's. The check cannot distinguish "this asks about something we do not cover" from "this asks about something we cover in other words". On the normal questions alone, wrong refusals jump from 8 % to 46 %. The net `ok` barely moves (+0.04, with 12 questions better and 9 worse, and unclear), which is exactly why a single average would have hidden both the win and the loss.

Whether to ship it is a **product decision**, not a number: for a medical or financial bot where a confident wrong answer is dangerous, accepting more refusals may be right; for casual search, no. The evaluation's job is to put both sides in front of the decision-maker with evidence. It also points at the *next* experiment: reduce the new wrong refusals (synonym handling, a better embedding), then re-measure.

### 7.3 Decision hygiene

- **State the hypothesis first** ("the unknown-word check will cut false answers without hurting normal questions") and the metrics that would prove it **wrong**. Here it is partly wrong: normal questions suffer.
- **Read the flipped cases** (section 6.2): they tell you *why*.
- **Record the decision** (a short note in the repo with the numbers and the trade-off accepted) so the next person does not redo it.
- **Confirm on held-out data** before shipping, and add cases of the kind that decided the question.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 'before and after' bar pair for four metrics of the Kestrel system: false answer rate (55% -> 0%, green arrow down), wrong refusal rate (30% -> 48%, red arrow up), retrieval hit (88% -> 88%, flat), overall ok (53% -> 56%, grey 'unclear'). Under the bars list the changed questions as little cards: twelve green cards 'no longer answered falsely', ten red cards 'now wrongly refused', with the example 'Can I get my money back for a sale item?' on one red card."

### 7.4 Try it

1. A variant raises `ok` from 0.53 to 0.59 and nothing else moves. Can you ship it?
2. You changed the chunk size and the retriever in one experiment and accuracy fell. What is the problem with this design?
3. Why is "no measurable effect and simpler" a win?

<details><summary>Answer</summary>

1. Not yet: check how many questions changed and whether the result is significant (6 points on 78 questions often is not), read the flipped cases for a pattern, check the other metrics and slices, and confirm on held-out cases.
2. You cannot tell which change caused the drop (or whether they interact). Change one thing at a time, or use a planned design that varies both systematically.
3. Every component is a cost: code, latency, money and a place for bugs. If removing a component does not measurably hurt, the evaluation has just earned you a simpler system. (With the caveat that "not measurable" depends on your dataset's power.)

</details>

## 8. Regression checks in CI

### 8.1 From experiment to gate

An experiment answers a question once. A **regression check** asks the same question **automatically on every change**: "did this commit make the system worse?" It runs your evaluation in CI (continuous integration, as in swe.09) and **blocks the merge** if the answer is yes. The decision logic, in `runner.gate`, has three parts:

| Rule | Meaning | Outcome |
|---|---|---|
| **Hard limits** | absolute floors and ceilings on the *new* run (`retrieval_hit >= 0.80`, `false_answer <= 0.60`, `ok >= 0.50`) | **FAIL** if broken: these protect what must never get worse |
| **Tracked metrics** | for each tracked metric, a paired comparison against the baseline run | **FAIL** if significantly *worse* |
| **Warnings** | a worse-looking move that is too small to prove | **WARN**, and the reviewer decides |

Two design points. First, **a gate must not cry wolf**: with noisy small samples, blocking every dip would train people to ignore it, so only *significant* regressions fail and unprovable ones warn. Second, the hard limits are set **from the accepted baseline** (a ratchet: the baseline is 0.55 false answers, the ceiling is 0.60) and tightened as the system improves, never loosened silently.

Run the gate on the variants of section 7, with the baseline as the reference:

```python run
from runner import gate, DEFAULT_RULES
print("rules:", DEFAULT_RULES, "\n")
for name in ("retriever: bm25 only", "top_k 1", "fixed chunks of 100", "fixed chunks of 60", "min_coverage 0.6", "unknown-word check"):
    g = gate(base, runs[name])
    print(f"{name:<22}{'PASSED' if g['passed'] else 'BLOCKED'}")
    for f in g["failures"]:
        print("     FAIL:", f)
    for w in g["warnings"]:
        print("     WARN:", w)
strict = run_with(min_coverage=0.8)
g = gate(base, strict)
print(f"{'min_coverage 0.8':<22}{'PASSED' if g['passed'] else 'BLOCKED'}")
for f in g["failures"]:
    print("     FAIL:", f)
```
```text
rules: {'hard': {'false_answer': ('<=', 0.6), 'retrieval_hit': ('>=', 0.8), 'ok': ('>=', 0.5)}, 'track': ['ok', 'retrieval_hit', 'false_answer', 'wrong_refusal'], 'warn_drop': 0.03} 

retriever: bm25 only  PASSED
top_k 1               PASSED
     WARN: retrieval_hit moved -0.054 the wrong way (3 worse, 0 better), but that is not provable with 56 cases (p = 0.25)
fixed chunks of 100   BLOCKED
     FAIL: retrieval_hit = 0.79 violates the hard limit >= 0.8
     FAIL: ok = 0.46 violates the hard limit >= 0.5
     WARN: ok moved -0.064 the wrong way (5 worse, 0 better), but that is not provable with 78 cases (p = 0.06)
     WARN: retrieval_hit moved -0.089 the wrong way (5 worse, 0 better), but that is not provable with 56 cases (p = 0.06)
fixed chunks of 60    BLOCKED
     FAIL: retrieval_hit = 0.71 violates the hard limit >= 0.8
     FAIL: ok = 0.47 violates the hard limit >= 0.5
     FAIL: retrieval_hit got significantly worse: -0.161 (95% interval -0.268 to -0.071; 9 cases worse, 0 better; sign test p = 0.004)
     WARN: ok moved -0.051 the wrong way (8 worse, 4 better), but that is not provable with 78 cases (p = 0.39)
     WARN: wrong_refusal moved +0.036 the wrong way (2 worse, 0 better), but that is not provable with 56 cases (p = 0.50)
min_coverage 0.6      BLOCKED
     FAIL: ok = 0.45 violates the hard limit >= 0.5
     FAIL: wrong_refusal got significantly worse: +0.179 (95% interval +0.089 to +0.286; 10 cases worse, 0 better; sign test p = 0.002)
     WARN: ok moved -0.077 the wrong way (8 worse, 2 better), but that is not provable with 78 cases (p = 0.11)
unknown-word check    BLOCKED
     FAIL: wrong_refusal got significantly worse: +0.179 (95% interval +0.089 to +0.286; 10 cases worse, 0 better; sign test p = 0.002)
min_coverage 0.8      BLOCKED
     FAIL: ok = 0.42 violates the hard limit >= 0.5
     FAIL: wrong_refusal got significantly worse: +0.482 (95% interval +0.357 to +0.625; 27 cases worse, 0 better; sign test p = 0.000)
```

Each row is a real decision. The neutral change passes silently. `top_k 1` passes with a **warning** that retrieval may have slipped but that this cannot be proven. The two fixed-chunk variants are blocked, the first by a **hard limit** (retrieval hit below 0.80, with ok below its floor) and the second **also** by a statistically significant retrieval regression. `min_coverage 0.8` shows the most important property: it brings false answers to zero (a great-looking number on its own!) and is **blocked** because wrong refusals rise by about 48 points with all 27 changed cases moving one way. A single-metric gate would have approved it. And the unknown-word check is blocked for its 10 newly wrong refusals.

### 8.2 Accepting a trade-off on purpose

Sometimes a block is the *right outcome to override*: the team decides that the unknown-word check's trade-off is acceptable for a safety-critical bot. The override must be **explicit and reviewable**, not a skipped test: change the **rules** (in a file under version control), with the reason in the commit message, and re-record the baseline:

```python run
accepted_rules = {"hard": {"false_answer": ("<=", 0.10), "retrieval_hit": (">=", 0.80), "wrong_refusal": ("<=", 0.55)},
                  "track": ["retrieval_hit", "false_answer"], "warn_drop": 0.03}
g = gate(base, runs["unknown-word check"], accepted_rules)
print("with the trade-off accepted in the rules:", "PASSED" if g["passed"] else "BLOCKED", g["failures"], g["warnings"])
bad = gate(base, runs["fixed chunks of 60"], accepted_rules)
print("the same rules still block a retrieval regression:", "PASSED" if bad["passed"] else "BLOCKED")
```
```text
with the trade-off accepted in the rules: PASSED [] []
the same rules still block a retrieval regression: BLOCKED
```

The accepted rules now **protect the new behaviour** (false answers must stay below 10 %, wrong refusals below 55 %) instead of forbidding it, and they still catch an unrelated retrieval regression. The decision lives in a diff someone can review, which is the whole point.

### 8.3 Making it run in CI

Practical points, learned the hard way by teams running these *(general knowledge)*:

| Concern | Practice |
|---|---|
| **Speed** | a small **smoke set** (20 to 40 cases covering every slice) on every commit; the **full set** nightly and before release |
| **Cost** | with a real model every case is a paid call (plus a judge call if used): 78 cases at 190 input tokens is trivial, 5,000 cases is not. **Cache** model responses keyed by (prompt, settings) so unchanged cases are free; run the expensive judge only on the full set |
| **Determinism** | pin the model version, use temperature 0, fix seeds in your own code; with a real model that is still not perfectly repeatable, so for the gate use **significance** (as here), and re-run a borderline failure before blaming the change |
| **The baseline** | stored as a JSON file in the repo, with the dataset hash; comparisons across different datasets are refused (`compare_runs` raises) |
| **Updating the baseline** | only in a commit that a reviewer approves, with the reason, together with the rule change if needed |
| **Reporting** | print the table and the flipped cases in the CI log so a failure is explained, not just red |
| **Secrets** | CI needs the model key as a protected secret; never commit it |

A CI workflow is a few lines (shown for reference, **not run here**: it needs a repository and a runner):

```yaml
# .github/workflows/eval.yml   (illustrative; not executed in this chapter)
name: eval
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: python evalcli.py run --dataset eval/cases.jsonl --out new.json --label pr
      - run: python evalcli.py compare eval/baseline.json new.json
      - run: python evalcli.py gate eval/baseline.json new.json     # exit status 1 blocks the merge
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a pull-request pipeline: a code change enters 'unit tests (seconds)', then 'smoke evaluation (40 cases, 1 minute)', then a gate diamond with three outputs: green 'PASSED' (silent), amber 'PASSED WITH WARNINGS' (comment on the PR with the unprovable drops), red 'BLOCKED' (comment with the failing metric, the 95% interval, and the list of flipped cases). Beside it show a nightly lane 'full evaluation + judge (500 cases)' that updates a dashboard of metrics over time, and a lock labelled 'baseline.json changes only with reviewer approval'."

### 8.4 Try it

1. A gate that fails whenever any metric is lower than the baseline: what will happen after a month?
2. A change legitimately worsens one metric, which the team accepts. How do you record the decision?
3. Why store the dataset fingerprint in every run file?

<details><summary>Answer</summary>

1. It will fail on noise (a single question flipping), people will learn to rerun until green or to ignore it, and it stops protecting anything. Fail only on significant regressions and hard limits, and warn on the rest.
2. Change the rules file (the accepted floor or ceiling) and the baseline in the same pull request, with the reason in the description, so a reviewer approves the trade-off in a diff. Do not skip or delete the check.
3. Two results are only comparable if they were computed on the same cases. If someone edits the dataset, comparing against an old baseline would mix the effect of the change with the effect of different questions; the fingerprint makes `compare` refuse.

</details>

## 9. Project: an evaluation suite for the PDF question-answering system

### 9.1 The brief

Build the evaluation tool that sits next to the question-answering system of llm.03 and answers, with numbers, *"did this change make it better or worse?"*.

Requirements:

1. **A dataset** in JSON Lines: hand-written and synthetic cases with tags, **validated on every load**, with a fingerprint and a deterministic dev/test split.
2. **A runner** that runs any configuration of the system over the dataset and stores per-case results, tags, scores and the dataset hash in one JSON file.
3. **Metrics** that separate retrieval from generation, that score unanswerable cases correctly, and that report cost and latency.
4. **An analysis** with Wilson intervals, **paired comparison** between two runs (sign test and bootstrap), slices by tag, and the flipped cases.
5. **A gate** with hard limits, tracked metrics and warnings, that **exits with status 1** when a change must not merge, and that refuses to compare runs on different datasets.
6. **A command-line interface**: `run`, `compare`, `gate`.
7. **43 tests**, including hand-checked statistics and a test that a "fix" that removes false answers by refusing everything is blocked.

The code you wrote section by section **is** the project: `evalset.py`, `stats.py`, `evalmetrics.py`, `judge.py`, `runner.py` and the system under test `ragsys.py`. What remains is the command line and the tests.

### 9.2 The command line

```
python evalcli.py run     --dataset cases.jsonl --out new.json [--config '{"top_k": 1}'] [--label name]
python evalcli.py compare base.json new.json
python evalcli.py gate    base.json new.json        # prints FAIL / WARN lines, exit status 1 if BLOCKED
```

```python run
(pkg / "evalcli.py").write_text(r'''"""evalcli: python evalcli.py run --dataset cases.jsonl --out run.json [--config '{"top_k": 5}']
              python evalcli.py compare base.json new.json
              python evalcli.py gate base.json new.json   (exit status 1 if the change should not merge)"""
from __future__ import annotations

import argparse
import json
import sys

import kestrel_docs
from evalset import load_jsonl
from ragsys import Config, RagSystem
from runner import gate, compare_runs, load_run, run_eval, save_run, summarize


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="evalcli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--dataset", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--config", default="{}", help="JSON of Config overrides")
    r.add_argument("--label", default="run")
    c = sub.add_parser("compare")
    c.add_argument("base")
    c.add_argument("new")
    g = sub.add_parser("gate")
    g.add_argument("base")
    g.add_argument("new")
    args = ap.parse_args(argv)

    if args.cmd == "run":
        cases = load_jsonl(args.dataset)
        run = run_eval(RagSystem(kestrel_docs.DOCS, Config(**json.loads(args.config))), cases, kestrel_docs.DOCS, args.label)
        save_run(run, args.out)
        s = summarize(run)
        print(f"{run['label']}: {run['n']} cases, dataset {run['dataset_hash']} | " + ", ".join(f"{m} {s[m]['mean']:.2f}" for m in ("ok", "retrieval_hit", "false_answer", "wrong_refusal") if m in s))
        return 0
    base, new = load_run(args.base), load_run(args.new)
    if args.cmd == "compare":
        for m in ("ok", "retrieval_hit", "false_answer", "wrong_refusal"):
            d = compare_runs(base, new, m)
            print(f"{m:<15} {d['diff']:+.3f}  95% [{d['ci_low']:+.3f}, {d['ci_high']:+.3f}]  better {d['improved']} / worse {d['worsened']}  p={d['p_sign']:.3f}  -> {d['verdict']}")
        return 0
    result = gate(base, new)
    for f in result["failures"]:
        print("FAIL:", f)
    for w in result["warnings"]:
        print("WARN:", w)
    print("GATE:", "passed" if result["passed"] else "BLOCKED")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
''', encoding="utf-8")
print("wrote evalcli.py:", 55, "lines")
```
```text
wrote evalcli.py: 55 lines
```

### 9.3 The tests

`test_evalset_stats.py` (18 tests): the validator on each kind of bad case, the fingerprint, the stable split, synthetic duplicates, kappa, and hand-checked Wilson, sign-test, bootstrap and sample-size values. `test_metrics_judge.py` (12 tests): metrics with their blind spots (token F1 scoring a wrong answer 0.67), scoring answerable and unanswerable cases, the judge's parsing, agreement report, and the detectors for leniency, verbosity and position bias. `test_runner_cli.py` (13 tests): the system's behaviour, determinism, summaries and slices, refusing to compare different datasets, the direction of lower-is-better metrics, the gate blocking, warning and passing, hard limits, the "refuse everything" trap, the unknown-word trade-off, and the CLI end to end.

```python run
(pkg / "test_evalset_stats.py").write_text(r'''import pytest

import kestrel_docs as kd
from evalset import (EvalCase, cohens_kappa, dataset_hash, drop_duplicates_of, generate_synthetic, kestrel_cases, load_jsonl, near_duplicates,
                     save_jsonl, split_dev_test, validate_cases)
from stats import bootstrap_ci, paired_difference, sample_size_paired, sign_test_p, wilson_interval


def good_case(**kw):
    base = dict(id="c1", question="How long is the warranty on tents?", answerable=True, gold_doc="warranty", gold_phrase="5-year", tags=("normal",))
    return EvalCase(**{**base, **kw})


def test_hand_written_and_synthetic_cases_validate_clean():
    hand = kestrel_cases(kd)
    synthetic, _ = drop_duplicates_of(hand, generate_synthetic(kd.DOCS))
    assert validate_cases(hand + synthetic, kd.DOCS) == [], "every gold phrase must really occur in its gold document"
    assert len(hand) == 44 and sum(not c.answerable for c in hand + synthetic) == 8 + 14


@pytest.mark.parametrize("case,fragment", [
    (good_case(gold_phrase="12-year"), "is not in warranty"),
    (good_case(gold_doc="no-such-doc"), "does not exist"),
    (good_case(gold_doc=None), "needs gold_doc and gold_phrase"),
    (good_case(question="How long is the warranty"), "does not end with '?'"),
    (good_case(answerable=False), "must not have a gold answer"),
])
def test_validation_catches_each_kind_of_bad_case(case, fragment):
    problems = validate_cases([case], kd.DOCS)
    assert any(fragment in p for p in problems), f"expected a problem containing {fragment!r}, got {problems}"


def test_duplicate_ids_are_caught():
    assert any("duplicate id" in p for p in validate_cases([good_case(), good_case()], kd.DOCS))


def test_dataset_hash_changes_with_one_character():
    a, b = [good_case()], [good_case(question="How long is the warranty on tents??")]
    assert dataset_hash(a) == dataset_hash([good_case()]) and dataset_hash(a) != dataset_hash(b), "the fingerprint must notice a one-character edit"


def test_split_is_deterministic_and_stable_when_cases_are_added():
    cases = [good_case(id=f"c{i}") for i in range(200)]
    dev, test = split_dev_test(cases)
    assert 0.2 < len(test) / 200 < 0.4, "about 30 percent of cases go to the test side"
    dev2, test2 = split_dev_test(cases + [good_case(id="c200")])
    assert {c.id for c in test} <= {c.id for c in test2} and {c.id for c in dev} <= {c.id for c in dev2}, "adding a case must never move an old case across the split"


def test_jsonl_round_trip(tmp_path):
    cases = kestrel_cases(kd)
    save_jsonl(cases, tmp_path / "c.jsonl")
    assert load_jsonl(tmp_path / "c.jsonl") == cases


def test_synthetic_duplicates_of_hand_cases_are_removed():
    hand = [good_case(id="h1", question="How heavy is it?", gold_doc="tent-aurora-3", gold_phrase="2.9 kg")]
    synthetic = generate_synthetic(kd.DOCS)
    kept, removed = drop_duplicates_of(hand, synthetic)
    assert any(c.gold_doc == "tent-aurora-3" and c.gold_phrase == "2.9 kg" for c in removed), "the Aurora 3 weight question is already covered by a hand case"
    assert all((c.gold_doc, c.gold_phrase) != ("tent-aurora-3", "2.9 kg") for c in kept)


def test_near_duplicate_detection():
    a = good_case(id="a", question="How long is the warranty on tents?")
    b = good_case(id="b", question="How long is the warranty on tents")
    c = good_case(id="c", question="Do gift cards expire?")
    assert near_duplicates([a, b, c]) == [("a", "b", 1.0)]


def test_kappa_hand_checked():
    assert cohens_kappa([1, 1, 0, 0], [1, 0, 0, 0]) == pytest.approx(0.5), "observed agreement 0.75, chance agreement 0.5: (0.75-0.5)/(1-0.5)"
    assert cohens_kappa([1, 0, 1], [1, 0, 1]) == 1.0
    assert cohens_kappa([1, 1, 1, 1], [1, 1, 1, 0]) == pytest.approx(0.0), "one labeller says 'yes' to everything: agreement is no better than chance"
    with pytest.raises(ValueError):
        cohens_kappa([], [])


def test_wilson_interval_hand_checked():
    lo, hi = wilson_interval(8, 10)
    assert (lo, hi) == pytest.approx((0.4902, 0.9433), abs=1e-3), "Wilson 95% interval for 8/10"
    assert wilson_interval(0, 0) == (0.0, 1.0), "no data means total uncertainty"
    assert wilson_interval(10, 10)[1] == 1.0 and wilson_interval(10, 10)[0] < 0.75, "10 out of 10 is NOT certainty: the lower end is about 0.72"
    narrow, wide = wilson_interval(80, 100), wilson_interval(8, 10)
    assert narrow[1] - narrow[0] < wide[1] - wide[0], "ten times more questions must give a narrower interval"


def test_sign_test_hand_checked():
    assert sign_test_p(5, 0) == pytest.approx(0.0625), "5 changes all in one direction: 2 x (1/2)^5"
    assert sign_test_p(6, 0) == pytest.approx(0.03125)
    assert sign_test_p(3, 3) == 1.0 and sign_test_p(0, 0) == 1.0
    assert sign_test_p(8, 2) == pytest.approx(2 * (1 + 10 + 45) / 1024), "8 vs 2: two-sided exact binomial"


def test_paired_difference_verdicts():
    assert paired_difference([1] * 20, [0] * 20)["verdict"] == "better"
    assert paired_difference([0] * 20, [1] * 20)["verdict"] == "worse"
    same = paired_difference([1, 0, 1, 0] * 5, [1, 0, 1, 0] * 5)
    assert same["verdict"] == "unclear" and same["mean_diff"] == 0 and same["improved"] == same["worsened"] == 0
    mixed = paired_difference([1, 0] * 10, [0, 1] * 10)
    assert mixed["verdict"] == "unclear", "as many questions got worse as better"


def test_bootstrap_ci_contains_the_mean_and_is_reproducible():
    v = [0, 1, 1, 0, 1, 1, 1, 0, 1, 1]
    lo, hi = bootstrap_ci(v)
    assert lo <= sum(v) / len(v) <= hi and (lo, hi) == bootstrap_ci(v), "a seeded bootstrap must give the same interval every time"
    assert bootstrap_ci([1, 1, 1, 1]) == (1.0, 1.0)


def test_sample_size_hand_checked():
    assert sample_size_paired(0.2, 0.1) == 32, "((1.96 + 0.84) x 0.2 / 0.1)^2 = 31.4, rounded up"
    assert sample_size_paired(0.2, 0.05) > 3.9 * sample_size_paired(0.2, 0.1), "halving the effect to detect needs about four times the questions"
''', encoding="utf-8")
print("wrote test_evalset_stats.py:", 113, "lines")
```
```text
wrote test_evalset_stats.py: 113 lines
```

```python run
(pkg / "test_metrics_judge.py").write_text(r'''import pytest

from evalmetrics import contains_phrase, exact_match, gold_sentence, rouge1_recall, score_case, support_score, token_f1
from evalset import EvalCase
from judge import SimulatedJudge, agreement_report, build_judge_prompt, parse_verdict
from ragsys import Result


def test_exact_match_normalises():
    assert exact_match("30 days.", "30 Days") and not exact_match("30 days", "60 days")


def test_token_f1_hand_checked_and_its_blind_spot():
    f1 = token_f1("returns within 30 days", "you may return items within 30 days")
    assert f1 == pytest.approx(6 / 11), "precision 3/4, recall 3/7, F1 = 6/11"
    wrong = token_f1("within 60 days", "within 30 days")
    assert wrong == pytest.approx(2 / 3), "two of three words match"
    assert wrong > 0.5 and not contains_phrase("within 60 days", "30 days"), "F1 gives a WRONG answer 0.67 because it cannot see that 60 is not 30; the phrase check can"
    assert token_f1("", "x") == 0.0


def test_rouge1_recall():
    assert rouge1_recall("tents weigh 2.9 kg", "the tent weighs 2.9 kg") == pytest.approx(2 / 5), "only exact word matches count: 'tents' and 'weigh' do not match 'tent' and 'weighs' (no stemming), so 2.9 and kg give 2 of the 5 reference words"


def test_support_score():
    src = ["The Aurora 3 weighs 2.9 kg."]
    assert support_score("The Aurora 3 weighs 2.9 kg.", src) == 1.0
    assert support_score("The Aurora 3 weighs 3.4 kg.", src) == 0.0, "an invented number is total failure"
    assert 0 < support_score("The Aurora 3 is a lovely tent.", src) < 1


def test_gold_sentence():
    text = "The Ember is warm. It weighs 1.2 kg. It has a hood."
    assert gold_sentence(text, "1.2 kg") == "It weighs 1.2 kg." and gold_sentence(text, "9 kg") == ""


def res(answer, refused, retrieved, cited):
    return Result(answer, refused, retrieved, cited, 100, 1.0)


def test_score_case_answerable_rank_and_correctness():
    case = EvalCase("c", "How much does the Aurora 3 weigh?", True, "tent-aurora-3", "2.9 kg")
    chunk_text = {"tent-aurora-2:0": "Aurora 2 weighs 2.1 kg.", "tent-aurora-3:0": "The Aurora 3 weighs 2.9 kg."}
    docs = {"tent-aurora-3": "The Aurora 3 weighs 2.9 kg."}
    s = score_case(case, res("The Aurora 3 weighs 2.9 kg.", False, ["tent-aurora-2:0", "tent-aurora-3:0"], ["tent-aurora-3:0"]), chunk_text, docs)
    assert s["retrieval_hit"] == 1 and s["rr"] == 0.5 and s["correct"] == 1 and s["cite_ok"] == 1 and s["ok"] == 1
    wrong = score_case(case, res("Aurora 2 weighs 2.1 kg.", False, ["tent-aurora-2:0"], ["tent-aurora-2:0"]), chunk_text, docs)
    assert wrong["retrieval_hit"] == 0 and wrong["correct"] == 0 and wrong["ok"] == 0
    refused = score_case(case, res("", True, ["tent-aurora-3:0"], []), chunk_text, docs)
    assert refused["wrong_refusal"] == 1 and refused["retrieval_hit"] == 1 and refused["correct"] == 0, "retrieval found it, the answerer refused: a generation-side failure"


def test_score_case_unanswerable():
    case = EvalCase("u", "Does it come in red?", False)
    assert score_case(case, res("", True, [], []), {}, {})["ok"] == 1
    s = score_case(case, res("It weighs 2.9 kg.", False, ["x:0"], ["x:0"]), {"x:0": "It weighs 2.9 kg."}, {})
    assert s["false_answer"] == 1 and s["ok"] == 0 and s["retrieval_hit"] is None


def test_judge_prompt_and_verdict_parsing():
    p = build_judge_prompt("Q?", "ref", "ans")
    assert "Q?" in p and "ref" in p and "ans" in p and '"verdict"' in p
    assert parse_verdict('Sure: {"verdict": "correct", "reason": "x"}') is True
    assert parse_verdict('{"verdict": "incorrect"}') is False
    assert parse_verdict("looks right to me") is None and parse_verdict('{"verdict": "maybe"}') is None and parse_verdict('{"verdict": ') is None


def test_agreement_report_hand_checked():
    r = agreement_report([True, True, False, False], [True, False, False, False])
    assert (r["tp"], r["fn"], r["tn"], r["fp"]) == (1, 1, 2, 0) and r["agreement"] == 0.75 and r["kappa"] == pytest.approx(0.5) and r["false_accept_rate"] == 0.0
    r2 = agreement_report([True, False], [None, True])
    assert r2["unreadable"] == 1, "an unreadable verdict must be counted, not hidden"


def judged_rate(judge, answers_and_truth):
    verdicts = [parse_verdict(judge.grade(a, t)) for a, t in answers_and_truth]
    return verdicts


def test_simulated_judge_is_reproducible_and_leniency_is_detectable():
    items = [("short wrong answer", False)] * 3000
    honest = judged_rate(SimulatedJudge(accuracy=0.95, seed=1), items)
    lenient = judged_rate(SimulatedJudge(accuracy=0.95, leniency=0.25, seed=1), items)
    assert honest == judged_rate(SimulatedJudge(accuracy=0.95, seed=1), items), "same seed, same verdicts"
    fa_honest, fa_lenient = sum(honest) / 3000, sum(lenient) / 3000
    assert fa_honest == pytest.approx(0.05, abs=0.02) and fa_lenient == pytest.approx(0.30, abs=0.03), "false accept rate = 1 - accuracy + leniency"


def test_verbosity_bias_is_detectable_by_padding():
    wrong = "It weighs 3 kg."
    padded = wrong + " " + "Furthermore this is a thorough and carefully considered statement. " * 8
    judge = SimulatedJudge(accuracy=0.95, verbosity_bias=0.4, seed=2)
    short_rate = sum(parse_verdict(judge.grade(wrong, False)) for _ in range(2000)) / 2000
    long_rate = sum(parse_verdict(judge.grade(padded, False)) for _ in range(2000)) / 2000
    assert long_rate > short_rate + 0.25, "padding a WRONG answer with fluent filler must raise its pass rate if the judge has a length bias"


def test_position_bias_is_detectable_by_swapping():
    judge = SimulatedJudge(position_bias=0.2, seed=3)
    first_wins = sum(judge.pairwise(1.0, 1.0) == "A" for _ in range(4000)) / 4000
    assert first_wins == pytest.approx(0.7, abs=0.03), "with identical answers a fair judge picks the first slot 50 percent of the time"
    fair = SimulatedJudge(seed=4)
    assert sum(fair.pairwise(1.0, 1.0) == "A" for _ in range(4000)) / 4000 == pytest.approx(0.5, abs=0.03)
''', encoding="utf-8")
print("wrote test_metrics_judge.py:", 104, "lines")
```
```text
wrote test_metrics_judge.py: 104 lines
```

```python run
(pkg / "test_runner_cli.py").write_text(r'''import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

import kestrel_docs as kd
from evalset import EvalCase, drop_duplicates_of, generate_synthetic, kestrel_cases, save_jsonl
from ragsys import Config, RagSystem
from runner import compare_runs, gate, run_eval, summarize

HERE = Path(__file__).parent
HAND = kestrel_cases(kd)
SYN, _ = drop_duplicates_of(HAND, generate_synthetic(kd.DOCS))
CASES = HAND + SYN


@pytest.fixture(scope="module")
def base_run():
    return run_eval(RagSystem(kd.DOCS, Config()), CASES, kd.DOCS, "base")


def fake_run(n_answerable, n_unanswerable, wrong_refusals=0, false_answers=0):
    rows = []
    for i in range(n_answerable):
        refused = i < wrong_refusals
        rows.append({"id": f"a{i}", "tags": [], "answerable": True, "scores": {"retrieval_hit": 1, "ok": 0 if refused else 1, "wrong_refusal": 1 if refused else 0,
                                                                              "false_answer": None, "correct": 0 if refused else 1}})
    for i in range(n_unanswerable):
        answered = i < false_answers
        rows.append({"id": f"u{i}", "tags": [], "answerable": False, "scores": {"retrieval_hit": None, "ok": 0 if answered else 1, "false_answer": 1 if answered else 0,
                                                                               "wrong_refusal": None, "correct": None}})
    return {"label": "fake", "dataset_hash": "h", "n": len(rows), "cases": rows}


def test_ragsys_basics():
    system = RagSystem(kd.DOCS, Config())
    assert len(system.chunks) == 37
    r = system.answer("How much does the Aurora 3 tent weigh?")
    assert r.retrieved[0] == "tent-aurora-3:0" and "2.9 kg" in r.answer and not r.refused and r.prompt_tokens > 0
    assert system.answer("What is a good recipe for chocolate cake?").refused
    assert all(c.index_text.startswith(c.title) for c in system.chunks) and not any(c.index_text.startswith(c.title) for c in RagSystem(kd.DOCS, Config(with_title=False)).chunks)


def test_unknown_word_check_trades_false_answers_for_wrong_refusals(base_run):
    plain, checked = RagSystem(kd.DOCS, Config()), RagSystem(kd.DOCS, Config(unknown_word_check=True))
    q = "Does the Aurora 3 come in red?"
    assert not plain.answer(q).refused and checked.answer(q).refused, "'red' appears nowhere in the library, so the attribute question is refused"
    assert not checked.answer("How much does the Aurora 3 tent weigh?").refused, "a question made of known words is still answered"
    run = run_eval(checked, CASES, kd.DOCS, "checked")
    assert summarize(run)["false_answer"]["mean"] == 0.0 and summarize(run)["wrong_refusal"]["mean"] > summarize(base_run)["wrong_refusal"]["mean"] + 0.1
    assert compare_runs(base_run, run, "false_answer")["verdict"] == "better" and compare_runs(base_run, run, "wrong_refusal")["verdict"] == "worse"


def test_run_is_deterministic_apart_from_timing(base_run):
    again = run_eval(RagSystem(kd.DOCS, Config()), CASES, kd.DOCS, "again")
    strip = lambda run: [(r["id"], r["answer"], r["refused"], r["retrieved"]) for r in run["cases"]]
    assert strip(again) == strip(base_run), "an evaluation that changes between identical runs cannot detect real changes"


def test_summary_has_intervals_and_slices(base_run):
    s = summarize(base_run)
    assert s["ok"]["n"] == len(CASES) and 0 <= s["ok"]["ci"][0] <= s["ok"]["mean"] <= s["ok"]["ci"][1] <= 1
    assert s["false_answer"]["n"] == sum(not c.answerable for c in CASES) and s["retrieval_hit"]["n"] == sum(c.answerable for c in CASES)
    para = summarize(base_run, "paraphrased")
    assert para["ok"]["n"] == 12 and para["ok"]["mean"] < summarize(base_run, "normal")["ok"]["mean"], "paraphrased questions must be harder for this system"


def test_comparing_runs_on_different_datasets_is_refused(base_run):
    other = copy.deepcopy(base_run)
    other["dataset_hash"] = "different"
    with pytest.raises(ValueError, match="different datasets"):
        compare_runs(base_run, other)


def test_identical_runs_are_unclear_and_pass_the_gate(base_run):
    d = compare_runs(base_run, base_run, "ok")
    assert d["verdict"] == "unclear" and d["diff"] == 0 and d["flipped"] == []
    assert gate(base_run, base_run)["passed"]


def test_lower_is_better_metrics_have_the_right_direction():
    base, worse = fake_run(20, 20, false_answers=2), fake_run(20, 20, false_answers=12)
    d = compare_runs(base, worse, "false_answer")
    assert d["diff"] == pytest.approx(0.5) and d["verdict"] == "worse" and d["worsened"] == 10 and d["improved"] == 0, "more false answers is WORSE even though the number went up"
    better = compare_runs(worse, base, "false_answer")
    assert better["verdict"] == "better" and better["improved"] == 10


def test_gate_blocks_a_significant_regression_and_explains_it():
    result = gate(fake_run(30, 10), fake_run(30, 10, wrong_refusals=12))
    assert not result["passed"] and any("wrong_refusal got significantly worse" in f for f in result["failures"]), result
    assert any("0 cases better" in f or "12 cases worse" in f for f in result["failures"]), "the message must say how many cases moved"


def test_gate_only_warns_on_a_drop_it_cannot_prove():
    result = gate(fake_run(30, 10), fake_run(30, 10, wrong_refusals=3))
    assert result["passed"] and any("not provable" in w for w in result["warnings"]), "3 flips in one direction have p = 0.25: a warning, not a block"


def test_gate_blocks_a_hard_limit_even_without_a_comparison_signal():
    rules = {"hard": {"false_answer": ("<=", 0.10)}, "track": [], "warn_drop": 0.03}
    run = fake_run(10, 10, false_answers=3)
    assert not gate(run, run, rules)["passed"], "a hard limit applies to the new run on its own"


def test_change_that_removes_false_answers_by_refusing_everything_is_blocked(base_run):
    strict = run_eval(RagSystem(kd.DOCS, Config(min_coverage=0.8)), CASES, kd.DOCS, "strict")
    assert summarize(strict)["false_answer"]["mean"] == 0.0, "the strict system never answers an unanswerable question"
    result = gate(base_run, strict)
    assert not result["passed"] and any("wrong_refusal" in f for f in result["failures"]), "a single-metric win must not hide that useful answers disappeared"


def test_neutral_change_passes(base_run):
    neutral = run_eval(RagSystem(kd.DOCS, Config(retriever="bm25")), CASES, kd.DOCS, "bm25")
    assert gate(base_run, neutral)["passed"]


def run_cli(*args):
    return subprocess.run([sys.executable, str(HERE / "evalcli.py"), *args], capture_output=True, text=True, cwd=HERE, encoding="utf-8")


def test_cli_run_compare_gate_end_to_end(tmp_path):
    save_jsonl(CASES, tmp_path / "cases.jsonl")
    base = run_cli("run", "--dataset", str(tmp_path / "cases.jsonl"), "--out", str(tmp_path / "base.json"), "--label", "base")
    assert base.returncode == 0 and "78 cases" in base.stdout, base.stdout + base.stderr
    bad = run_cli("run", "--dataset", str(tmp_path / "cases.jsonl"), "--out", str(tmp_path / "bad.json"), "--config", '{"min_coverage": 0.8}', "--label", "strict")
    assert bad.returncode == 0
    assert "wrong_refusal" in run_cli("compare", str(tmp_path / "base.json"), str(tmp_path / "bad.json")).stdout
    ok = run_cli("gate", str(tmp_path / "base.json"), str(tmp_path / "base.json"))
    assert ok.returncode == 0 and "GATE: passed" in ok.stdout
    blocked = run_cli("gate", str(tmp_path / "base.json"), str(tmp_path / "bad.json"))
    assert blocked.returncode == 1 and "GATE: BLOCKED" in blocked.stdout and "FAIL" in blocked.stdout
''', encoding="utf-8")
print("wrote test_runner_cli.py:", 135, "lines")
```
```text
wrote test_runner_cli.py: 135 lines
```

```python run
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=pkg, capture_output=True, text=True, encoding="utf-8")
print("\n".join(res.stdout.strip().splitlines()[-3:]) if res.stdout.strip() else res.stderr[-600:])
listing = subprocess.run([sys.executable, "-m", "pytest", "-q", "-q", "-p", "no:cacheprovider", "--collect-only"], cwd=pkg, capture_output=True, text=True, encoding="utf-8")
print({m.group(1): int(m.group(2)) for line in listing.stdout.splitlines() if (m := re.match(r"(\S+\.py): (\d+)", line))})
```
```text
...........................................                              [100%]
43 passed in 2.01s
{'test_evalset_stats.py': 18, 'test_metrics_judge.py': 12, 'test_runner_cli.py': 13}
```

### 9.4 Use it: baseline, a safe change, a bad change, a "clever" change

The workflow of a real team, from the command line. The dataset file is the `cases.jsonl` saved in section 2.6.

```python run
def evalcli(*args):
    out = subprocess.run([sys.executable, "evalcli.py", *args], cwd=pkg, capture_output=True, text=True, encoding="utf-8")
    return out.returncode, (out.stdout + out.stderr).rstrip()

data = str(ws / "cases.jsonl")
print("$ evalcli run --label baseline")
print(evalcli("run", "--dataset", data, "--out", str(ws / "base.json"), "--label", "baseline")[1])
for file_stem, label, cfg in [("safe", "a safe simplification (bm25 only)", {"retriever": "bm25"}), ("tiny", "tiny chunks", {"chunking": "fixed", "size": 60}),
                              ("fix", "'fix' false answers by refusing more", {"min_coverage": 0.8})]:
    out_file = str(ws / (file_stem + ".json"))
    print(f"\n$ evalcli run --config '{json.dumps(cfg)}'      # {label}")
    print(evalcli("run", "--dataset", data, "--out", out_file, "--config", json.dumps(cfg), "--label", label)[1])
    code, text = evalcli("gate", str(ws / "base.json"), out_file)
    print(f"$ evalcli gate base.json {pathlib.Path(out_file).name}      (exit status {code})")
    print(text)
```
```text
$ evalcli run --label baseline
baseline: 78 cases, dataset 10b400c097f9 | ok 0.53, retrieval_hit 0.88, false_answer 0.55, wrong_refusal 0.30

$ evalcli run --config '{"retriever": "bm25"}'      # a safe simplification (bm25 only)
a safe simplification (bm25 only): 78 cases, dataset 10b400c097f9 | ok 0.53, retrieval_hit 0.88, false_answer 0.55, wrong_refusal 0.30
$ evalcli gate base.json safe.json      (exit status 0)
GATE: passed

$ evalcli run --config '{"chunking": "fixed", "size": 60}'      # tiny chunks
tiny chunks: 78 cases, dataset 10b400c097f9 | ok 0.47, retrieval_hit 0.71, false_answer 0.55, wrong_refusal 0.34
$ evalcli gate base.json tiny.json      (exit status 1)
FAIL: retrieval_hit = 0.71 violates the hard limit >= 0.8
FAIL: ok = 0.47 violates the hard limit >= 0.5
FAIL: retrieval_hit got significantly worse: -0.161 (95% interval -0.268 to -0.071; 9 cases worse, 0 better; sign test p = 0.004)
WARN: ok moved -0.051 the wrong way (8 worse, 4 better), but that is not provable with 78 cases (p = 0.39)
WARN: wrong_refusal moved +0.036 the wrong way (2 worse, 0 better), but that is not provable with 56 cases (p = 0.50)
GATE: BLOCKED

$ evalcli run --config '{"min_coverage": 0.8}'      # 'fix' false answers by refusing more
'fix' false answers by refusing more: 78 cases, dataset 10b400c097f9 | ok 0.42, retrieval_hit 0.88, false_answer 0.00, wrong_refusal 0.79
$ evalcli gate base.json fix.json      (exit status 1)
FAIL: ok = 0.42 violates the hard limit >= 0.5
FAIL: wrong_refusal got significantly worse: +0.482 (95% interval +0.357 to +0.625; 27 cases worse, 0 better; sign test p = 0.000)
WARN: ok moved -0.103 the wrong way (20 worse, 12 better), but that is not provable with 78 cases (p = 0.22)
GATE: BLOCKED
```

Each call prints one line per run, and the gate prints *why* it decided: the failing metric, how much it moved, its 95 % interval, and how many cases got worse and better. The exit status is what CI reads. And here is the paired comparison for one pair, the view a reviewer reads when deciding whether to accept a blocked change:

```python run
print("$ evalcli compare base.json tiny.json")
print(evalcli("compare", str(ws / "base.json"), str(ws / "tiny.json"))[1])
```
```text
$ evalcli compare base.json tiny.json
ok              -0.051  95% [-0.141, +0.026]  better 4 / worse 8  p=0.388  -> unclear
retrieval_hit   -0.161  95% [-0.268, -0.071]  better 0 / worse 9  p=0.004  -> worse
false_answer    -0.000  95% [-0.000, -0.000]  better 0 / worse 0  p=1.000  -> unclear
wrong_refusal   +0.036  95% [-0.000, +0.089]  better 0 / worse 2  p=0.500  -> unclear
```

### 9.5 Extensions

1. **Attach a real judge.** Wire `build_judge_prompt` to the llm.02 client, parse with `parse_verdict`, and add a `judge_correct` metric. **First** label 60 answers yourself, then measure agreement, kappa and the padding and swap tests of section 5.
2. **More cases.** The test set (20 cases) could not confirm a 6-point change. Collect 100 more cases from real questions, tag them, and re-run section 6.5.
3. **Multiple runs.** For a model with temperature above zero, run each case 3 to 5 times and average; report the run-to-run spread as a metric.
4. **Cost tracking.** Add a `cost_per_1000` column from prompt and answer tokens and an illustrative price table (llm.01), and gate on cost as well as quality.
5. **Trend dashboard.** Store each CI run's summary and plot the metrics over commits; flag slow drift that no single comparison catches.
6. **Pairwise evaluation.** Instead of scoring each system alone, show a judge both systems' answers (in random order) and count wins; analyse with the sign test.

## 10. Common traps

1. **Evaluating after changing** (1.1). Record the baseline first.
2. **A dataset with no unanswerable questions** (2.1). You cannot measure false answers.
3. **Unvalidated cases** (2.3). A broken gold phrase corrupts every number silently.
4. **Synthetic cases reported as user performance, or duplicated** (2.4). Tag them, dedupe them, and keep real questions separate.
5. **One average for everything** (3.2, 3.4). Slice by question type; separate retrieval from generation.
6. **Trusting an overlap metric** (4.2). Token F1 gave a **wrong** answer 0.93; check the key fact directly.
7. **Optimising one side of a trade-off** (4.3, 7.2). Track false answers **and** wrong refusals, quality **and** cost.
8. **Ignoring uncertainty** (6.1). A score from 20 questions has an interval about 40 points wide.
9. **Comparing two separate scores instead of paired differences** (6.2).
10. **Declaring a winner from the best of many variants** (6.4). Decide first, correct for multiple comparisons, confirm on held-out data.
11. **Tuning on the test set** (2.6, 6.5). Keep it locked; with a small test set, say it is too small.
12. **Reading "unclear" as "no effect"** (6.3). It usually means the dataset lacks power.
13. **Trusting a judge without testing it** (5.2, 5.3). Check agreement, kappa, the false accept rate, padding and swap; pin the judge.
14. **A gate that cries wolf** (8.1). Fail on significant regressions and hard limits; warn on the unprovable.
15. **Skipping the check to accept a trade-off** (8.2). Change the rules in a reviewed diff instead.
16. **Comparing runs from different datasets** (8.3). Store and check the fingerprint.
17. **Never reading the failures** (3.5, 6.2). Numbers say how often; the failed cases say why.

## 11. Summary

- An **evaluation** has four parts: a **dataset**, a **system**, **metrics** and an **analysis**. Build it before improving, record a baseline, and never trust a single number.
- **Datasets**: a mix of real, expert, past-failure, synthetic and adversarial cases, with **checkable gold answers**, **tags**, deliberate **unanswerable** cases, a **validator** on every load, **deduplication** of synthetic cases, **labelling agreement** (Cohen's kappa), a **dev/test split** and a **fingerprint**.
- **Retrieval and generation are evaluated separately**: a hit/correct table says which stage failed; slices by question type show where; reading the failed cases says why.
- **Automatic metrics** are cheap and have **blind spots**: exact match rejects paraphrases, token F1 can rank a wrong answer above a right one, support scores punish paraphrase. Use several, matched to the failure you care about, and track **false answers and wrong refusals together**, plus **cost and latency**.
- **Model-graded evaluation** scales to free text but is itself unreliable: calibrate on human labels (agreement, kappa, **false accept rate**), run **padding** and **swap** tests for verbosity and position bias, pin the judge, and keep deterministic checks beside it.
- **Statistics for small sets**: scores have intervals (width falls with the square root of *n*); compare systems on the **same questions, paired**, with the **exact sign test** for yes/no metrics and a bootstrap otherwise; know how many questions you need; **many variants fool you**; confirm on held-out data; "unclear" often means too few cases.
- **Experiments** change one thing at a time and report the trade-off, e.g. the unknown-word check cut false answers by 54 points (12 better, 0 worse) and cost 10 newly wrong refusals.
- **Regression checks in CI**: a gate with **hard limits, tracked metrics and warnings**, blocking significant regressions, storing the baseline and dataset hash in the repo, accepting trade-offs through reviewed rule changes, using a smoke set per commit and the full set nightly.
- The project is an **evaluation suite** (`run`, `compare`, `gate`), with 43 tests, that tells you, with numbers and uncertainty, whether a change to the RAG system helped or hurt.

**Self-check (answer without looking back):**

1. Why evaluate retrieval separately from the final answer? What does a "retrieval hit but wrong answer" tell you?
2. A system gets 36 of 60 questions right. Roughly how wide is its 95 % interval, and what would halve it?
3. Of the questions that changed between two systems, 7 improved and 1 got worse. Is that evidence of improvement? (Compute roughly.)
4. A change reduces false answers from 50 % to 5 % and the gate blocks it. Why might that be correct, and how do you ship it if you decide to?
5. Why can token F1 be misleading, and what should you use for the key fact of the answer?
6. A judge agrees with human labels 90 % of the time. Which two further checks would you run?
7. Why does the gate fail on *significant* regressions and only warn on small unprovable ones?

<details><summary>Answer</summary>

1. Retrieval and generation fail for different reasons, so a single accuracy hides what to fix. "Hit but wrong" means the right passage was among the sources and the answerer (prompt, model or refusal rule) failed: fix generation, not retrieval.
2. 36/60 = 60 %; the Wilson interval is about 47 % to 72 %, roughly 25 points wide. It falls with the square root of the number of questions, so you need about four times as many (240) to halve it.
3. The exact sign test for 7 versus 1: 2 x P(at most 1 of 8) = 2 x (1 + 8)/256 = 0.07. Suggestive, not conclusive at the usual 0.05 line: probably an improvement, worth confirming with more cases.
4. Because the change probably also makes the system refuse many questions it should answer (check wrong refusals); the gate tracks both sides. If the team decides the trade-off is right (safety-critical use), change the **rules** (a lower false-answer ceiling, an allowed wrong-refusal ceiling) and the baseline in a reviewed pull request with the numbers and the reason.
5. It measures word overlap, so a wrong answer that copies most words (a changed number) scores high, while a correct paraphrase scores low. Check the key fact directly (gold phrase or number), and add a support check for unsupported additions.
6. Look at the **false accept rate** (and kappa and the sample size) because 90 % agreement can hide a lenient judge; and run the **padding** test (verbosity bias) and the **swap** test (position bias), which need no human labels.
7. With a small dataset every metric wobbles by a few points from luck alone. Blocking every dip would train people to ignore the gate; failing only on significant regressions and hard limits keeps it credible, and warnings keep unprovable drops visible for a human.

</details>
