# Chapter 8 (DS): Other special data: text and recommendations

Up to now every table had numbers and a few categories in tidy columns. Two kinds of data do not fit that mould, and both are everywhere in industry. **Text** (reviews, support tickets, emails, documents) is a sequence of words with no columns at all, and a vocabulary of tens of thousands of possible "features". **Interactions** (which user watched, bought or rated which item) form a huge table that is almost entirely empty, because each person touches a tiny fraction of the catalogue. Both need a first step that turns the raw material into a matrix a model can use, and both punish the habits of ds.04: leakage hides in new places, and the honest baseline is harder to beat than it looks.

This chapter has two halves. In the first you learn **text features**: how to split text into tokens, count them (**bag of words**), reweight the counts so that rare, informative words matter more (**TF-IDF**), build a **text classifier**, and, the outcome of the syllabus, **explain its errors**. In the second you learn **recommender system basics**: popularity and bias baselines, neighbourhood methods, **matrix factorisation**, and how to evaluate a recommender without fooling yourself. The project builds a small **movie recommender** with an honest offline evaluation.

Prerequisites: ds.05 (pipelines), ds.06 (logistic regression, Naive Bayes, SVD/PCA, k-NN), ds.04 (leakage, splits, baselines), ds.03 (metrics). Everything here is built from ideas you already own, with a sparse matrix as the new data structure.

> **Offline rule for this chapter.** Everything runs with no internet, using NumPy, pandas, SciPy and scikit-learn. No text corpus can be downloaded, and NLTK, spaCy, gensim and Surprise are **not installed**, so the data are **synthetic and seeded**: support tickets and product reviews generated from word lists with deliberate difficulties (ambiguous words, typos, negation, a misleading shortcut), and a ratings matrix generated from hidden tastes. Because we wrote the generators, we know what a good model should find. Every output block was produced by running the code above it, in one session from top to bottom. Timings are machine-specific.

```python run
import sys, math, time, json, re, warnings, platform
import numpy as np
import pandas as pd
import scipy
import sklearn
from scipy import sparse, stats
from sklearn import (feature_extraction, linear_model, metrics, model_selection, naive_bayes, pipeline, preprocessing,
                     svm, decomposition, dummy, ensemble)
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer, ENGLISH_STOP_WORDS

np.set_printoptions(precision=4, suppress=True, linewidth=110)
pd.set_option("display.width", 130)
pd.set_option("display.max_columns", 30)
pd.set_option("display.max_colwidth", 90)
pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
warnings.filterwarnings("ignore")
print("python ", sys.version.split()[0])
print("numpy  ", np.__version__)
print("scipy  ", scipy.__version__)
print("pandas ", pd.__version__)
print("sklearn", sklearn.__version__)
```
```text
python  3.14.4
numpy   2.5.4
scipy   1.18.1
pandas  3.1.1
sklearn 1.9.1
```

## Table of contents

1. [Text is different](#1-text-is-different)
2. [From text to tokens](#2-from-text-to-tokens)
3. [Bag of words](#3-bag-of-words)
4. [TF-IDF](#4-tf-idf)
5. [A text classifier](#5-a-text-classifier)
6. [Explaining a text classifier's errors](#6-explaining-a-text-classifiers-errors)
7. [Beyond bag of words](#7-beyond-bag-of-words)
8. [Recommender systems: the problem and the data](#8-recommender-systems-the-problem-and-the-data)
9. [Evaluating a recommender](#9-evaluating-a-recommender)
10. [Baselines: popularity and bias](#10-baselines-popularity-and-bias)
11. [Neighbourhood methods](#11-neighbourhood-methods)
12. [Matrix factorisation](#12-matrix-factorisation)
13. [Implicit feedback, cold start and popularity bias](#13-implicit-feedback-cold-start-and-popularity-bias)
14. [Project: a movie recommender with an honest evaluation](#14-project-a-movie-recommender-with-an-honest-evaluation)
15. [Common traps](#15-common-traps)
16. [Summary](#16-summary)

## 1. Text is different

### 1.1 Why a table of words is a hard table

Imagine turning 10,000 support tickets into a table with one column per distinct word. You would get something like 20,000 columns, and each ticket would have a value in only 10 or 20 of them. Three consequences follow from this shape, and they shape everything in this chapter:

| Property | Consequence |
|---|---|
| **Very wide** (many more columns than a person can look at, often more than rows) | overfitting is easy; regularisation is not optional (ds.03) |
| **Sparse** (nearly all entries are zero) | store only the non-zero entries (`scipy.sparse`); dense arrays would not fit in memory |
| **Heavy-tailed word frequencies** (a few words appear everywhere, most appear once or twice) | the common words carry little information; the rare words are informative but unreliable |

Language also has structure that a column-per-word table throws away: word order ("dog bites man" is not "man bites dog"), negation ("not good"), meaning shared between different words ("refund", "reimbursement"). The simplest representation ignores all of it, and still works surprisingly well, which is why it remains the baseline you must beat before using anything fancier.

### 1.2 The pipeline of every text model

```text
raw text  ->  tokens  ->  counts  ->  weights (TF-IDF)  ->  model  ->  predictions
 "Can't log in!"  ["can","log","in"]   sparse matrix    reweighted     logistic regression
```

Each arrow is a decision with consequences. We take them one at a time. And, because of ds.04, every arrow that *learns* something (the vocabulary, the word weights) must be fitted on the training data only.

### 1.3 Two datasets we control

**Support tickets.** Four categories: billing, login, shipping, bug. Each category has its own words, but there are deliberate difficulties: words shared between categories ("account", "order"), generic filler words, tickets that mix two categories, and typos.

**Product reviews.** Positive or negative, built from sentiment words with **negation** ("not good", "not bad") that a plain word count misreads.

```python run
CLASS_WORDS = {
    "billing":  "invoice charge charged refund payment card billing receipt subscription price overcharged coupon renewal".split(),
    "login":    "password login log signin locked reset username verification email code otp access blocked".split(),
    "shipping": "delivery shipped courier tracking parcel package delayed address arrived warehouse dispatch shipment".split(),
    "bug":      "crash error freezes screen button loads slow bug broken update fails glitch stuck".split(),
}
SHARED = "account order app website customer please help issue problem support team".split()
FILLER = "the my i is a to and it for with on this that have has not can you we please thanks hello hi since today yesterday again".split()

def typo(w, r):
    """About 12% of longer words get a typing slip: swapped neighbours, a dropped letter or a doubled letter."""
    if len(w) > 4 and r.random() < 0.12:
        i = int(r.integers(1, len(w) - 2))
        kind = r.integers(3)
        if kind == 0:
            return w[:i] + w[i + 1] + w[i] + w[i + 2:]
        if kind == 1:
            return w[:i] + w[i + 1:]
        return w[:i] + w[i] + w[i:]
    return w

def make_tickets(n=2400, seed=0, agent_shortcut=None):
    """agent_shortcut: dict class -> probability that the ticket is handled by that class's 'usual' agent (a spurious signal)."""
    r = np.random.default_rng(seed)
    classes = list(CLASS_WORDS)
    agents = {"billing": "agent_asha", "login": "agent_ben", "shipping": "agent_chen", "bug": "agent_dev"}
    rows = []
    for _ in range(n):
        c = classes[r.integers(4)]
        other = classes[r.integers(4)]
        words = []
        for _ in range(r.integers(7, 16)):
            u = r.random()
            if u < 0.40:   words.append(r.choice(CLASS_WORDS[c]))
            elif u < 0.50: words.append(r.choice(CLASS_WORDS[other]))               # a second topic leaks in
            elif u < 0.65: words.append(r.choice(SHARED))
            else:          words.append(r.choice(FILLER))
        words = [typo(w, r) for w in words]
        text = " ".join(words).capitalize() + "."
        if agent_shortcut is not None:
            names = list(agents.values())
            a = agents[c] if r.random() < agent_shortcut else names[r.integers(4)]
            text += f" Handled by {a}"
        rows.append((text, c))
    return pd.DataFrame(rows, columns=["text", "label"])

tickets = make_tickets()
print(tickets.shape, "|", tickets["label"].value_counts().to_dict())
print(tickets.head(6).to_string())
```
```text
(2400, 2) | {'shipping': 618, 'login': 606, 'bug': 588, 'billing': 588}
                                                                                                text     label
0                                  Screen freezes hlelo team problem it fails has the error support.       bug
1  Again hi email verification issue reeset have has website code verification locked access acount.     login
2                                                 Email verification today to email order this this.     login
3                  Code app otp thanks please charge please since the hi renewal with tooday locked.   billing
4                                                    For the support shipment can delivery dispatch.  shipping
5                                           Fails website problem problem lods this issue stuck app.       bug
```

```python run
POS = "good great excellent love amazing perfect fantastic reliable smooth happy".split()
NEG = "bad terrible awful hate broken useless poor slow disappointing annoying".split()
NEUTRAL = "the a this product item it was is very really quite overall bought delivery price quality battery screen".split()

def make_reviews(n=3000, seed=0):
    r = np.random.default_rng(seed)
    rows = []
    for _ in range(n):
        positive = r.random() < 0.5
        words = list(r.choice(NEUTRAL, r.integers(3, 8)))
        for _ in range(r.integers(1, 4)):
            u = r.random()
            if u < 0.22:                                                       # negation: flips the meaning of the next word
                w = r.choice(NEG if positive else POS)
                words += ["not", w]                                            # "not bad" is positive, "not good" is negative
            elif u < 0.30:                                                     # a misleading word of the other sentiment
                words.append(r.choice(NEG if positive else POS))
            else:
                words.append(r.choice(POS if positive else NEG))
        rows.append((" ".join(words), int(positive)))
    return pd.DataFrame(rows, columns=["text", "positive"])

reviews = make_reviews()
print(reviews.head(5).to_string())
```
```text
                                                                             text  positive
0                                                 item it the a the disappointing         0
1  delivery overall really quite battery item price bad not reliable not reliable         0
2                                                really a it not amazing not good         0
3               item overall delivery was very screen annoying disappointing poor         0
4                                    bought quality really was it amazing perfect         1
```

## 2. From text to tokens

### 2.1 Tokenisation

A **token** is the unit the model counts, usually a word. The default scikit-learn rule is a regular expression: lower-case the text, then take every run of two or more letters, digits or underscores. Punctuation disappears and one-letter words are dropped.

```python run
pattern = re.compile(r"(?u)\b\w\w+\b")
def tokenize(text):
    return pattern.findall(text.lower())
sample = "I can't log in!! My Password isn't working, order #4412 failed."
print(tokenize(sample))
print("sklearn's analyzer gives the same:", CountVectorizer().build_analyzer()(sample) == tokenize(sample))
```
```text
['can', 'log', 'in', 'my', 'password', 'isn', 'working', 'order', '4412', 'failed']
sklearn's analyzer gives the same: True
```

Look at what happened: "can't" became `can` (the `'t` is a one-letter token and is dropped), "isn't" became `isn`, and the number lost its `#`. These are decisions, and they can matter: **dropping "not"-like pieces changes meaning**, which is exactly the trap of the review data (section 6). Better tokenisers keep contractions, emoticons or hashtags; for English-language tickets this default is a reasonable start.

### 2.2 Lower-casing, stop words, stemming

| Step | What it does | Gain | Risk |
|---|---|---|---|
| **Lower-case** | `Refund` = `refund` | fewer rare variants | loses "US" versus "us" |
| **Stop words** | drop very common words (`the`, `and`, `of`) | smaller matrix | removes "not", "no" (in some lists!), which matter for meaning |
| **Stemming / lemmatising** | `charged`, `charging` -> `charg` | merges variants | wrong merges ("university"/"universe"); needs a language tool |
| **Numbers, URLs, emails** | replace by a placeholder token | avoids thousands of one-off tokens | information lost |

scikit-learn ships a list of English stop words. Check what is in it before you use it.

```python run
print("scikit-learn English stop words:", len(ENGLISH_STOP_WORDS))
for w in ["the", "and", "not", "no", "never", "nor", "cannot", "good", "bad", "refund", "please", "help", "problem"]:
    print(f"  {w:8s} in the list: {w in ENGLISH_STOP_WORDS}")
```
```text
scikit-learn English stop words: 318
  the      in the list: True
  and      in the list: True
  not      in the list: True
  no       in the list: True
  never    in the list: True
  nor      in the list: True
  cannot   in the list: True
  good     in the list: False
  bad      in the list: False
  refund   in the list: False
  please   in the list: True
  help     in the list: False
  problem  in the list: False
```

Standard lists contain `not`, `no`, `never` and `nor`. Removing them **deletes the negations** that decide the meaning of a review. For sentiment, do not use that list blindly.

A crude stemmer (real ones, such as Porter's, are more careful; NLTK is not installed here) shows both the benefit and the risk:

```python run
def crude_stem(w):
    for suf in ("ing", "ed", "es", "ly", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[: -len(suf)]
    return w
for w in ["charged", "charging", "charges", "delivery", "delivered", "delivering", "news", "bus", "glitches", "slowly"]:
    print(f"{w:10s} -> {crude_stem(w)}")
```
```text
charged    -> charg
charging   -> charg
charges    -> charg
delivery   -> delivery
delivered  -> deliver
delivering -> deliver
news       -> new
bus        -> bus
glitches   -> glitch
slowly     -> slow
```

`charged`, `charging` and `charges` all become `charg`, so they count together (good). But `news` becomes `new` and `bus` is spared only because it is too short (bad): stemming trades precision for coverage.

### 2.3 n-grams: a little word order

An **n-gram** is `n` consecutive tokens. Bigrams (`n = 2`) recover local order: "not good" becomes the single feature `not good`, separate from `good` alone. The price is a vocabulary that grows rapidly.

```python run
doc = "the screen is not good"
for ngr in [(1, 1), (1, 2), (2, 2), (1, 3)]:
    print(ngr, CountVectorizer(ngram_range=ngr).fit([doc]).get_feature_names_out().tolist())
v_uni = CountVectorizer().fit(reviews["text"]); v_bi = CountVectorizer(ngram_range=(1, 2)).fit(reviews["text"]); v_tri = CountVectorizer(ngram_range=(1, 3)).fit(reviews["text"])
print("vocabulary size on the reviews: unigrams", len(v_uni.vocabulary_), "| up to bigrams", len(v_bi.vocabulary_), "| up to trigrams", len(v_tri.vocabulary_))
```
```text
(1, 1) ['good', 'is', 'not', 'screen', 'the']
(1, 2) ['good', 'is', 'is not', 'not', 'not good', 'screen', 'screen is', 'the', 'the screen']
(2, 2) ['is not', 'not good', 'screen is', 'the screen']
(1, 3) ['good', 'is', 'is not', 'is not good', 'not', 'not good', 'screen', 'screen is', 'screen is not', 'the', 'the screen', 'the screen is']
vocabulary size on the reviews: unigrams 38 | up to bigrams 1121 | up to trigrams 10087
```

### 2.4 Character n-grams: robust to typos

Instead of words, use overlapping pieces of letters. A misspelling such as `passwrod` still shares most of its character pieces with `password`, while as whole words they are different tokens with nothing in common.

```python run
def cos_sim(a, b, **kw):
    X = CountVectorizer(**kw).fit_transform([a, b]).astype(float)
    X = X.toarray()
    return float(X[0] @ X[1] / (np.linalg.norm(X[0]) * np.linalg.norm(X[1]) + 1e-12))
print("word tokens   : 'password' vs 'passwrod' similarity", round(cos_sim("password", "passwrod"), 3))
print("char 3-grams  : 'password' vs 'passwrod' similarity", round(cos_sim("password", "passwrod", analyzer="char_wb", ngram_range=(3, 3)), 3))
print("char 2-4-grams: 'password' vs 'passwrod' similarity", round(cos_sim("password", "passwrod", analyzer="char_wb", ngram_range=(2, 4)), 3))
```
```text
word tokens   : 'password' vs 'passwrod' similarity 0.0
char 3-grams  : 'password' vs 'passwrod' similarity 0.5
char 2-4-grams: 'password' vs 'passwrod' similarity 0.542
```

### 2.5 Try it

1. Add `token_pattern=r"(?u)\b\w+\b"` to a `CountVectorizer` and tokenise `"I can't log in"`. What changes, and which tokens now appear?
2. Pick any five words from the ticket vocabularies and see which ones your `crude_stem` merges wrongly.

## 3. Bag of words

### 3.1 The idea

A **bag of words** represents a document by how many times each vocabulary word occurs in it, and throws away the order. With a vocabulary of `V` words and `N` documents we get an `N × V` matrix of counts, stored sparse.

```python run
docs = ["Refund my card payment", "Cannot login password reset", "Refund for the payment please", "Password reset code not working"]
cv = CountVectorizer()
Xc = cv.fit_transform(docs)
print("type:", type(Xc).__name__, "| shape", Xc.shape, "| stored non-zero entries", Xc.nnz)
print(pd.DataFrame(Xc.toarray(), columns=cv.get_feature_names_out(), index=[f"doc{i}" for i in range(4)]).to_string())
```
```text
type: csr_matrix | shape (4, 14) | stored non-zero entries 18
      cannot  card  code  for  login  my  not  password  payment  please  refund  reset  the  working
doc0       0     1     0    0      0   1    0         0        1       0       1      0    0        0
doc1       1     0     0    0      1   0    0         1        0       0       0      1    0        0
doc2       0     0     0    1      0   0    0         0        1       1       1      0    1        0
doc3       0     0     1    0      0   0    1         1        0       0       0      1    0        1
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a diagram of bag of words. Four short documents: 'Refund my card payment', 'Cannot login password reset', 'Refund for the payment please', 'Password reset code not working'. Show each sentence on the left, an arrow to a 4 x 14 table of word counts (one column per vocabulary word, such as refund, payment, password, reset), and highlight that word order is thrown away and most cells are 0. Mark the 18 non-zero cells in colour."

### 3.2 From scratch, matching scikit-learn

The algorithm: tokenise every document; build the vocabulary as the **sorted** set of all tokens; for each document count each token's occurrences.

```python run
def bow_scratch(docs):
    toks = [tokenize(d) for d in docs]
    vocab = sorted({t for ts in toks for t in ts})
    index = {w: j for j, w in enumerate(vocab)}
    rows, cols, vals = [], [], []
    for i, ts in enumerate(toks):
        counts = {}
        for t in ts:
            counts[t] = counts.get(t, 0) + 1
        for t, c in counts.items():
            rows.append(i); cols.append(index[t]); vals.append(c)
    return sparse.csr_matrix((vals, (rows, cols)), shape=(len(docs), len(vocab))), vocab

M_ours, vocab_ours = bow_scratch(tickets["text"])
cv_t = CountVectorizer().fit(tickets["text"])
M_sk = cv_t.transform(tickets["text"])
print("same vocabulary:", vocab_ours == cv_t.get_feature_names_out().tolist(), "| vocabulary size", len(vocab_ours))
print("same matrix    :", (M_ours != M_sk).nnz == 0)
```
```text
same vocabulary: True | vocabulary size 636
same matrix    : True
```

### 3.3 Sparsity and memory

```python run
n, v = M_sk.shape
dense_bytes = n * v * 8
sparse_bytes = M_sk.data.nbytes + M_sk.indices.nbytes + M_sk.indptr.nbytes
print(f"tickets matrix {n} x {v}: share of non-zero entries {M_sk.nnz / (n * v):.4%}")
print(f"dense float64: {dense_bytes / 1e6:.1f} MB | sparse (CSR): {sparse_bytes / 1e6:.2f} MB | ratio {dense_bytes / sparse_bytes:.0f}x")
big = 1_000_000 * 50_000 * 8 / 1e9
print(f"a dense matrix for 1,000,000 documents and 50,000 words would take {big:,.0f} GB; the sparse one is limited by the number of non-zero entries only")
```
```text
tickets matrix 2400 x 636: share of non-zero entries 1.5341%
dense float64: 12.2 MB | sparse (CSR): 0.29 MB | ratio 42x
a dense matrix for 1,000,000 documents and 50,000 words would take 400 GB; the sparse one is limited by the number of non-zero entries only
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw one picture of a dense matrix versus a sparse CSR matrix for a 2400 x 636 tickets table. Show the dense grid as a big block of 12.2 MB, with about 1.5% of cells coloured as non-zero. Beside it show three small arrays (data, indices, indptr) totalling 0.29 MB. Label the 42x memory saving and explain how indptr marks where each row starts."

### 3.4 Word frequencies are heavy-tailed (Zipf's law)

Real text has a few very common words and a long tail of rare ones. Our synthetic text is much flatter than real language, but even here the document frequency (the number of documents containing a word) varies hugely.

```python run
df_ = np.asarray((M_sk > 0).sum(0)).ravel()
vocab_arr = cv_t.get_feature_names_out()
top = pd.Series(df_, index=vocab_arr).sort_values(ascending=False)
print("most common words (document frequency):", top.head(8).to_dict())
print("words that appear in only 1-3 tickets:", int((df_ <= 3).sum()), "of", len(df_), "(mostly typos)")
```
```text
most common words (document frequency): {'please': 523, 'app': 342, 'that': 339, 'to': 338, 'have': 335, 'help': 334, 'and': 334, 'the': 327}
words that appear in only 1-3 tickets: 319 of 636 (mostly typos)
```

The words that appear in just one to three tickets are mostly **typos**. They are useless as features (a classifier cannot learn from a word it sees once) and can only help it memorise training rows. `min_df` removes them:

```python run
for min_df in [1, 2, 5, 10]:
    print(f"min_df={min_df:2d}: vocabulary {len(CountVectorizer(min_df=min_df).fit(tickets['text']).vocabulary_)}")
for max_df in [1.0, 0.2, 0.15]:
    print(f"max_df={max_df}: vocabulary {len(CountVectorizer(max_df=max_df).fit(tickets['text']).vocabulary_)} (drops words that appear in more than that share of the tickets)")
```
```text
min_df= 1: vocabulary 636
min_df= 2: vocabulary 528
min_df= 5: vocabulary 238
min_df=10: vocabulary 104
max_df=1.0: vocabulary 636 (drops words that appear in more than that share of the tickets)
max_df=0.2: vocabulary 635 (drops words that appear in more than that share of the tickets)
max_df=0.15: vocabulary 635 (drops words that appear in more than that share of the tickets)
```

### 3.5 Binary and counted features

`binary=True` records only presence. For short texts (tickets, tweets) presence is usually as good as the count; for long documents the count matters.

### 3.6 Try it

1. Compute the matrix with `ngram_range=(1, 2)` and compare the share of non-zero entries and the memory.
2. What does `CountVectorizer(vocabulary=["refund", "password"])` produce? Why would a fixed vocabulary be useful in production?

## 4. TF-IDF

### 4.1 The idea: rare words are more informative

Raw counts have a problem: a word like `please` can appear many times in every ticket, yet says nothing about the category. A word like `refund` appears in few documents, and when it does, it is informative. **TF-IDF** (term frequency x inverse document frequency) rescales each count by how rare the word is across the whole collection.

```text
tf(t, d)   = count of term t in document d
idf(t)     = ln( (1 + N) / (1 + df(t)) ) + 1          (scikit-learn's smoothed form)
tfidf(t,d) = tf(t, d) * idf(t)
then each document row is scaled to have Euclidean length 1  (L2 normalisation)
```

`N` is the number of documents and `df(t)` the number of documents containing `t`. The `+1` inside the fraction avoids division by zero, and the final `+1` keeps words that appear in every document from getting weight 0. The row normalisation makes long and short documents comparable, and makes the **dot product of two rows equal their cosine similarity**.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Make a step-by-step diagram of TF-IDF on a small collection of N documents. Use the formula idf(t) = ln((1+N)/(1+df(t))) + 1. Show two words: 'please' (in almost every document) and 'refund' (in few). Draw a bar chart of count versus tf-idf weight for each, showing the rare word grows relatively larger. Then show the row being scaled to Euclidean length 1."

### 4.2 From scratch, matching scikit-learn exactly

```python run
def tfidf_scratch(count_matrix, smooth=True, sublinear=False):
    X = count_matrix.astype(float).tocsr()
    N = X.shape[0]
    df = np.asarray((X > 0).sum(0)).ravel()
    idf = np.log((1 + N) / (1 + df)) + 1 if smooth else np.log(N / df) + 1
    if sublinear:
        X.data = 1 + np.log(X.data)
    X = X.multiply(idf).tocsr()
    norms = np.sqrt(np.asarray(X.multiply(X).sum(1)).ravel())
    return sparse.diags(1 / norms) @ X, idf

T_ours, idf_ours = tfidf_scratch(M_sk)
tf_sk = TfidfVectorizer().fit(tickets["text"])
T_sk = tf_sk.transform(tickets["text"])
print("idf vectors equal :", np.allclose(idf_ours, tf_sk.idf_))
print("matrices equal    :", np.abs((T_ours - T_sk)).max() < 1e-12, "(max difference %.1e)" % np.abs((T_ours - T_sk)).max())
T_sub, _ = tfidf_scratch(M_sk, sublinear=True)
print("sublinear_tf=True also matches:", np.abs(T_sub - TfidfVectorizer(sublinear_tf=True).fit_transform(tickets["text"])).max() < 1e-12)
```
```text
idf vectors equal : True
matrices equal    : True (max difference 2.2e-16)
sublinear_tf=True also matches: True
```

### 4.3 What the weights look like

```python run
idf_series = pd.Series(tf_sk.idf_, index=tf_sk.get_feature_names_out())
common = idf_series.sort_values().head(6)
rare = idf_series[df_ >= 20].sort_values(ascending=False).head(6)
print("lowest idf (appear in most tickets):", common.round(2).to_dict())
print("highest idf among words in 20+ tickets:", rare.round(2).to_dict())
doc_i = tickets["text"].iloc[0]
row = pd.Series(T_sk[0].toarray().ravel(), index=tf_sk.get_feature_names_out())
print("\nticket:", doc_i)
print("its largest TF-IDF weights:", row[row > 0].sort_values(ascending=False).head(5).round(3).to_dict())
```
```text
lowest idf (appear in most tickets): {'please': 2.52, 'app': 2.95, 'that': 2.95, 'to': 2.96, 'have': 2.97, 'help': 2.97}
highest idf among words in 20+ tickets: {'error': 3.61, 'subscription': 3.6, 'price': 3.59, 'fails': 3.59, 'access': 3.57, 'crash': 3.54}

ticket: Screen freezes hlelo team problem it fails has the error support.
its largest TF-IDF weights: {'hlelo': 0.534, 'error': 0.297, 'fails': 0.295, 'screen': 0.29, 'freezes': 0.286}
```

> **Predict the output.** In `FILLER` we included the word `not`, and in `CLASS_WORDS` the word `refund`. Which will have the higher IDF in the tickets data: `not` (it appears in tickets of every class) or `refund` (billing only)? And what is the TF-IDF-based cosine similarity between a billing ticket and a login ticket, compared with two billing tickets?

<details><summary>Answer</summary>

`refund` has the higher IDF, because it appears in a small share of the tickets while `not` appears in most of them. Similarly, same-class tickets share rare, informative words and so have a higher cosine similarity than tickets of different classes.

```python run
print("idf  not: %.3f | refund: %.3f" % (idf_series["not"], idf_series["refund"]))
lab = tickets["label"].to_numpy()
S = (T_sk[:400] @ T_sk[:400].T).toarray()
same = S[(lab[:400, None] == lab[None, :400]) & ~np.eye(400, dtype=bool)].mean()
diff = S[lab[:400, None] != lab[None, :400]].mean()
print("mean cosine similarity: same category %.3f | different category %.3f" % (same, diff))
```
```text
idf  not: 3.000 | refund: 3.451
mean cosine similarity: same category 0.149 | different category 0.052
```

</details>

### 4.4 Cosine similarity and search

Because rows are length-1, the dot product of two TF-IDF rows is their cosine similarity: 1 for identical direction, 0 for no shared words. A tiny **search engine** is just this: turn the query into a vector with the *same fitted vectorizer*, and rank documents by similarity.

```python run
def search(query, k=3):
    q = tf_sk.transform([query])
    sims = (T_sk @ q.T).toarray().ravel()
    top = np.argsort(-sims)[:k]
    return [(round(float(sims[i]), 3), tickets["label"].iloc[i], tickets["text"].iloc[i][:70]) for i in top]
for hit in search("refund for the charge on my card"):
    print(hit)
```
```text
(0.531, 'billing', 'Overcharged hi card yesterday snice subscription receipt on charge pro')
(0.489, 'billing', 'Card card please yesterday my to refund overcharged that.')
(0.446, 'billing', 'Refund a card reset customer have to card order charge charge porblem ')
```

Note the discipline: the **query is transformed, never fitted**. `tf_sk.transform(...)` applies the vocabulary and IDF learned from the collection; a word not in the vocabulary is silently ignored.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a 2D picture of cosine similarity as angles between vectors. Show a query vector 'refund for the charge on my card' and three document vectors of length 1 (all billing tickets) with similarities 0.531, 0.489 and 0.446. Draw the angle between each pair, and label that for unit-length rows the dot product equals the cosine, with 1 meaning same direction and 0 meaning no shared words."

### 4.5 Which weighting when

| Choice | Effect |
|---|---|
| `sublinear_tf=True` | `1 + ln(tf)` damps repeated words; good for long documents |
| `use_idf=False` | plain normalised counts; sometimes as good for short texts |
| `norm="l2"` (default) | removes the effect of document length |
| `smooth_idf=True` | avoids zero-division for words in every document |
| `binary=True` | presence only |

### 4.6 Try it

1. Use `TfidfVectorizer(use_idf=False)` and check by hand that each row is just the L2-normalised count vector.
2. Remove the L2 normalisation (`norm=None`) and compute the cosine similarity of two tickets yourself. How would you have to change `search`?


## 5. A text classifier

### 5.1 The pipeline, and the baseline first

A text classifier is exactly the pipeline of ds.05 with a vectoriser as its first step. The vectoriser **learns** a vocabulary and IDF weights, so it must live inside the pipeline: then cross-validation refits it on each fold's training rows and the test rows never influence the vocabulary (ds.04 section 3).

We split once, keep a sealed test set, and compare with the baseline that always predicts the most common class.

```python run
tk_dev, tk_test = model_selection.train_test_split(tickets, test_size=0.25, random_state=0, stratify=tickets["label"])
print("development:", len(tk_dev), "| sealed test:", len(tk_test))
cv5 = model_selection.StratifiedKFold(5, shuffle=True, random_state=0)

def cv_report(est, X=tk_dev["text"], y=tk_dev["label"]):
    acc = model_selection.cross_val_score(est, X, y, cv=cv5, scoring="accuracy")
    f1 = model_selection.cross_val_score(est, X, y, cv=cv5, scoring="f1_macro")
    return acc.mean(), acc.std(), f1.mean()

base = dummy.DummyClassifier(strategy="most_frequent")
a, s, f = cv_report(pipeline.make_pipeline(CountVectorizer(), base))
print(f"majority-class baseline: accuracy {a:.3f} +- {s:.3f}, macro-F1 {f:.3f}   (four balanced classes -> 0.25)")

lr_pipe = pipeline.make_pipeline(TfidfVectorizer(), linear_model.LogisticRegression(max_iter=2000))
a, s, f = cv_report(lr_pipe)
print(f"TF-IDF + logistic regression: accuracy {a:.3f} +- {s:.3f}, macro-F1 {f:.3f}")
```
```text
development: 1800 | sealed test: 600
majority-class baseline: accuracy 0.258 +- 0.001, macro-F1 0.102   (four balanced classes -> 0.25)
TF-IDF + logistic regression: accuracy 0.935 +- 0.010, macro-F1 0.935
```

### 5.2 Which classifier?

Text matrices are wide and sparse, a setting where **linear models** and **Naive Bayes** are the usual first choices: with this many features a straight-line boundary is usually enough, and trees (which split on one feature at a time) are slower to train.

```python run
cands = {
    "Naive Bayes (counts)":            pipeline.make_pipeline(CountVectorizer(), naive_bayes.MultinomialNB()),
    "Naive Bayes (TF-IDF)":            pipeline.make_pipeline(TfidfVectorizer(), naive_bayes.MultinomialNB()),
    "Logistic regression (TF-IDF)":    pipeline.make_pipeline(TfidfVectorizer(), linear_model.LogisticRegression(max_iter=2000)),
    "Linear SVM (TF-IDF)":             pipeline.make_pipeline(TfidfVectorizer(), svm.LinearSVC()),
    "SGD, hinge loss (TF-IDF)":        pipeline.make_pipeline(TfidfVectorizer(), linear_model.SGDClassifier(random_state=0, max_iter=50, tol=None)),
    "Random forest (counts)":          pipeline.make_pipeline(CountVectorizer(), ensemble.RandomForestClassifier(n_estimators=150, n_jobs=1, random_state=0)),
}
rows = []
for name, est in cands.items():
    t0 = time.perf_counter()
    a, s, f = cv_report(est)
    rows.append((name, a, s, f, time.perf_counter() - t0))
print(pd.DataFrame(rows, columns=["model", "CV accuracy", "std", "macro-F1", "seconds (10 CV fits)"]).set_index("model").round(3).to_string())
print("(differences of about 0.01 are within the fold standard deviation: Naive Bayes, logistic regression and the linear SVM are tied here)")
```
```text
                              CV accuracy    std  macro-F1  seconds (10 CV fits)
model                                                                           
Naive Bayes (counts)               0.9430 0.0120    0.9430                0.1990
Naive Bayes (TF-IDF)               0.9440 0.0090    0.9440                0.1670
Logistic regression (TF-IDF)       0.9350 0.0100    0.9350                0.3600
Linear SVM (TF-IDF)                0.9360 0.0100    0.9360                0.2400
SGD, hinge loss (TF-IDF)           0.9270 0.0110    0.9270                0.2800
Random forest (counts)             0.9210 0.0100    0.9210                4.5160
(differences of about 0.01 are within the fold standard deviation: Naive Bayes, logistic regression and the linear SVM are tied here)
```

### 5.3 Tuning the text step and the model together

The vectoriser's own settings are hyperparameters: n-gram range, `min_df`, sublinear TF, even the analyser. Tune them with the model, as one pipeline (ds.05 section 9).

```python run
pipe = pipeline.Pipeline([("tfidf", TfidfVectorizer()), ("clf", linear_model.LogisticRegression(max_iter=3000))])
grid = {"tfidf__ngram_range": [(1, 1), (1, 2)], "tfidf__min_df": [1, 2, 5], "tfidf__sublinear_tf": [False, True],
        "tfidf__analyzer": ["word", "char_wb"], "clf__C": [0.3, 1, 3, 10, 30]}
grid_small = {**grid, "tfidf__analyzer": ["word"]}
gs = model_selection.GridSearchCV(pipe, grid_small, cv=cv5, scoring="accuracy", n_jobs=1).fit(tk_dev["text"], tk_dev["label"])
cvr = pd.DataFrame(gs.cv_results_)
print("best:", gs.best_params_, "| CV accuracy", round(gs.best_score_, 4))
cols = ["param_tfidf__ngram_range", "param_tfidf__min_df", "param_tfidf__sublinear_tf", "param_clf__C", "mean_test_score", "std_test_score"]
print(cvr.sort_values("mean_test_score", ascending=False)[cols].head(6).round(4).to_string(index=False))
print("lowest candidate:", round(cvr["mean_test_score"].min(), 4), "| default pipeline of 5.1 was", round(cv_report(lr_pipe)[0], 4))
```
```text
best: {'clf__C': 1, 'tfidf__analyzer': 'word', 'tfidf__min_df': 2, 'tfidf__ngram_range': (1, 2), 'tfidf__sublinear_tf': False} | CV accuracy 0.9378
param_tfidf__ngram_range  param_tfidf__min_df  param_tfidf__sublinear_tf  param_clf__C  mean_test_score  std_test_score
                  (1, 2)                    2                      False        1.0000           0.9378          0.0122
                  (1, 2)                    2                       True        1.0000           0.9372          0.0105
                  (1, 2)                    1                       True        0.3000           0.9367          0.0103
                  (1, 2)                    2                       True        0.3000           0.9367          0.0087
                  (1, 1)                    2                       True        1.0000           0.9367          0.0118
                  (1, 2)                    1                      False        1.0000           0.9367          0.0131
lowest candidate: 0.9144 | default pipeline of 5.1 was 0.935
```

Read this honestly: the best candidate beats the untuned pipeline of 5.1 by well under one fold standard deviation, and many candidates tie within noise. The worst candidates (a very small or very large `C`) are a few points lower, so a sensible default is already close to the best here. Tuning matters more when the data are small or the classes are hard to separate; do not expect a large gain from it on easy text.

### 5.4 The shortcut trap: a classifier that learned the wrong thing

A text model can score very well for the wrong reason. In many real datasets some token **correlates with the label in the training period but not in deployment**: the name of the agent who handled the ticket, a template header, the name of the labelling team, a watermark. Cross-validation on the same data cannot see it, because the shortcut is present in every fold.

We simulate it: in the development data, 90% of each category's tickets were handled by that category's "usual agent", and the agent's name is appended to the text. In deployment the assignment is random.

```python run
sc_dev = make_tickets(n=2400, seed=11, agent_shortcut=0.9)
sc_new = make_tickets(n=1200, seed=12, agent_shortcut=0.25)             # 0.25 = agent unrelated to the category
print(sc_dev["text"].iloc[0]); print(sc_new["text"].iloc[0])

m_sc = pipeline.make_pipeline(TfidfVectorizer(), linear_model.LogisticRegression(max_iter=2000))
cv_sc = model_selection.cross_val_score(m_sc, sc_dev["text"], sc_dev["label"], cv=cv5, scoring="accuracy").mean()
m_sc.fit(sc_dev["text"], sc_dev["label"])
print(f"cross-validated accuracy on the development data: {cv_sc:.3f}")
print(f"accuracy on the new period (agents assigned at random): {m_sc.score(sc_new['text'], sc_new['label']):.3f}")
```
```text
Please billing is receipt is support customer again refund and issue hi has payment. Handled by agent_asha
Shipmeent delayed parcel you is hello account arrived signin otp that delayed to this today. Handled by agent_chen
cross-validated accuracy on the development data: 0.980
accuracy on the new period (agents assigned at random): 0.882
```

**Detect it** with the same detective work as in ds.04 section 4: look at the words the model relies on most.

```python run
def top_words(pipe, k=6):
    vec, clf = pipe[0], pipe[-1]
    names = vec.get_feature_names_out()
    out = {}
    for ci, cls in enumerate(clf.classes_):
        order = np.argsort(-clf.coef_[ci])[:k]
        out[cls] = [(names[j], round(float(clf.coef_[ci][j]), 2)) for j in order]
    return out
for cls, ws in top_words(m_sc).items():
    print(f"{cls:9s}", ws)
```
```text
billing   [('agent_asha', 6.12), ('card', 2.4), ('refund', 2.33), ('price', 2.1), ('overcharged', 2.07), ('billing', 2.07)]
bug       [('agent_dev', 5.7), ('slow', 2.29), ('screen', 2.29), ('error', 2.24), ('bug', 2.19), ('glitch', 2.12)]
login     [('agent_ben', 6.14), ('otp', 2.56), ('password', 2.44), ('blocked', 2.28), ('code', 2.14), ('log', 2.14)]
shipping  [('agent_chen', 5.68), ('shipment', 2.47), ('arrived', 2.44), ('tracking', 2.31), ('courier', 2.27), ('delayed', 2.16)]
```

The agent tokens (`agent_asha`, `agent_ben`...) are among the strongest features of every class. A domain expert would immediately say "that is not what a billing ticket is about". **Fix**: remove the token (a custom preprocessor), or better, remove the signature at the data-collection step.

```python run
def strip_signature(text):
    return re.sub(r"handled by agent_\w+", "", text, flags=re.I)
clean_pipe = pipeline.make_pipeline(TfidfVectorizer(preprocessor=lambda t: strip_signature(t).lower()), linear_model.LogisticRegression(max_iter=2000))
cv_clean = model_selection.cross_val_score(clean_pipe, sc_dev["text"], sc_dev["label"], cv=cv5, scoring="accuracy").mean()
clean_pipe.fit(sc_dev["text"], sc_dev["label"])
print(f"signature removed: CV accuracy {cv_clean:.3f} (lower, but honest) | accuracy on the new period {clean_pipe.score(sc_new['text'], sc_new['label']):.3f}")
print("model with the shortcut, CV accuracy:", round(cv_sc, 3), "-> new period:", round(m_sc.score(sc_new['text'], sc_new['label']), 3))
```
```text
signature removed: CV accuracy 0.936 (lower, but honest) | accuracy on the new period 0.935
model with the shortcut, CV accuracy: 0.98 -> new period: 0.882
```

Two lessons. A lower CV score after the fix is the *true* score. And any time a text model looks too good, read its top features before anything else.

### 5.5 The sealed test

Finally, the tuned pipeline on the sealed test set, once.

```python run
final = gs.best_estimator_
pred = final.predict(tk_test["text"])
print("sealed test accuracy: %.3f | macro-F1 %.3f" % (metrics.accuracy_score(tk_test["label"], pred), metrics.f1_score(tk_test["label"], pred, average="macro")))
print(metrics.classification_report(tk_test["label"], pred, digits=3))
```
```text
sealed test accuracy: 0.920 | macro-F1 0.920
              precision    recall  f1-score   support

     billing      0.918     0.918     0.918       147
         bug      0.918     0.912     0.915       147
       login      0.919     0.901     0.910       152
    shipping      0.924     0.948     0.936       154

    accuracy                          0.920       600
   macro avg      0.920     0.920     0.920       600
weighted avg      0.920     0.920     0.920       600
```

### 5.6 Try it

1. Add `class_weight="balanced"` and check whether it changes anything on these balanced classes. When would it matter?
2. Use `char_wb` n-grams (2 to 5) in the pipeline of 5.1. Does the CV accuracy move beyond the fold standard deviation? Why might it help on typos?

## 6. Explaining a text classifier's errors

This section is the outcome of the chapter. A classifier is only useful if you can say **why it is wrong and what to do about it**. Text models are friendly to this because the features are words, and a linear model's reasoning can be read off exactly.

### 6.1 Step 1: a confusion matrix and a list of mistakes

```python run
labels = sorted(tickets["label"].unique())
cm = pd.DataFrame(metrics.confusion_matrix(tk_test["label"], pred, labels=labels), index=[f"true {l}" for l in labels], columns=[f"pred {l}" for l in labels])
print(cm.to_string())
wrong = tk_test.assign(pred=pred)[pred != tk_test["label"]]
print("\nerrors:", len(wrong), "of", len(tk_test), f"({len(wrong) / len(tk_test):.1%})")
print(wrong.head(6).to_string())
```
```text
               pred billing  pred bug  pred login  pred shipping
true billing            135         5           4              3
true bug                  4       134           5              4
true login                5         5         137              5
true shipping             3         2           3            146

errors: 48 of 600 (8.0%)
                                                                              text     label      pred
2317  Again can not emaail locked hi since for can refund with toay you to bloked.     login   billing
979                            Isue broken the and courier crsah hi arrved brkoen.       bug  shipping
639                                    Since a hello yesterday thanks receipt and.  shipping   billing
1640                                       Crash glitch login blocked i have code.       bug     login
2291                  Today hi again charged glitch a is is not refund my account.       bug   billing
1346            Broken payment freezes slow renewal please chagred have is poblem.   billing       bug
```

Always read the mistakes. Numbers say *how many*; sentences say *why*. Look for patterns: do the wrong tickets have two topics? Are they very short? Do they contain typos? Is the label itself doubtful?

### 6.2 Step 2: what does the model think each class looks like

For a linear model, each class has a weight per word, and the largest weights are the model's idea of the class.

```python run
for cls, ws in top_words(final, k=7).items():
    print(f"{cls:9s}", [w for w, _ in ws])
print("\nthe largest NEGATIVE weights for class 'billing' (words that argue against it):")
clf, vec = final[-1], final[0]
ci = list(clf.classes_).index("billing")
print([vec.get_feature_names_out()[j] for j in np.argsort(clf.coef_[ci])[:6]])
```
```text
billing   ['card', 'renewal', 'coupon', 'billing', 'invoice', 'payment', 'charge']
bug       ['bug', 'update', 'button', 'glitch', 'freezes', 'crash', 'slow']
login     ['username', 'otp', 'email', 'log', 'signin', 'code', 'blocked']
shipping  ['shipped', 'warehouse', 'package', 'delayed', 'tracking', 'parcel', 'delivery']

the largest NEGATIVE weights for class 'billing' (words that argue against it):
['shipped', 'button', 'package', 'password', 'bug', 'address']
```

### 6.3 Step 3: explain one prediction exactly

In a linear model on TF-IDF features the score of class `c` for a document is `intercept_c + Σ_j coef_cj · x_j`, a sum of one contribution per word. The decomposition is not an approximation: it is exact, and you can check it against `decision_function`.

```python run
def explain(pipe, text, true_label=None, k=5):
    vec, clf = pipe[0], pipe[-1]
    x = vec.transform([text])
    names = vec.get_feature_names_out()
    coefs, inters = clf.coef_, clf.intercept_
    if coefs.shape[0] == 1:                                           # binary model: one weight vector for the positive class
        coefs, inters = np.vstack([-coefs[0], coefs[0]]), np.array([-inters[0], inters[0]])
    scores = inters + np.asarray(x @ coefs.T).ravel()
    best = int(np.argmax(scores))
    idx = x.indices
    contrib = x.data * coefs[best][idx]
    recon = inters[best] + contrib.sum()
    assert np.isclose(recon, scores[best]), "contributions must add up to the decision score"
    order = np.argsort(-contrib)
    return {"text": text, "predicted": clf.classes_[best], "true": true_label, "score": round(float(scores[best]), 3),
            "for": [(names[idx[i]], round(float(contrib[i]), 3)) for i in order[:k] if contrib[i] > 0],
            "against": [(names[idx[i]], round(float(contrib[i]), 3)) for i in order[::-1][:k] if contrib[i] < 0]}

row = wrong.iloc[0]
e = explain(final, row["text"], row["label"])
for key in ["text", "true", "predicted", "score", "for", "against"]:
    print(f"{key:9s}", e[key])
print("\nthe two highest class scores:", np.round(np.sort(final.decision_function([row['text']])[0])[::-1][:2], 3))
```
```text
text      Again can not emaail locked hi since for can refund with toay you to bloked.
true      login
predicted billing
score     0.334
for       [('refund', 0.361), ('with', 0.067), ('can refund', 0.064), ('refund with', 0.046), ('hi', 0.038)]
against   [('locked', -0.119), ('toay', -0.03), ('emaail', -0.027), ('to', -0.024), ('since', -0.022)]

the two highest class scores: [0.334 0.139]
```

The `for` list is why the model chose its answer; the words of the true class that were missing, misspelled or outnumbered by words of another class explain the mistake.

### 6.4 Step 4: slice the errors

Write down hypotheses about what makes a ticket hard and test each with a slice table (ds.04 section 12). Here: the **length** of the ticket, the **share of unknown words** (typos the model has never seen), and how **decisive** the model was.

```python run
vocab_set = set(final[0].get_feature_names_out())
def unknown_share(t):
    toks = tokenize(t)
    return float(np.mean([w not in vocab_set for w in toks])) if toks else 0.0
ev = tk_test.assign(pred=pred)
ev["wrong"] = (ev["pred"] != ev["label"]).astype(int)
ev["length"] = pd.cut(ev["text"].str.split().str.len(), [0, 8, 11, 100], labels=["short (<=8)", "medium (9-11)", "long (12+)"])
ev["unknown words"] = pd.cut(ev["text"].map(unknown_share), [-0.01, 0.0, 0.15, 1.0], labels=["none", "up to 15%", "more than 15%"])
conf = np.sort(final.predict_proba(ev["text"]), axis=1)
ev["confidence gap"] = pd.cut(conf[:, -1] - conf[:, -2], [-0.01, 0.1, 0.3, 1.0], labels=["close call (<0.1)", "medium", "decisive (>0.3)"])
for col in ["length", "unknown words", "confidence gap"]:
    print(ev.groupby(col, observed=True)["wrong"].agg(rows="size", error_rate="mean").round(3).to_string()); print()
```
```text
               rows  error_rate
length                         
short (<=8)     135      0.1260
medium (9-11)   188      0.0900
long (12+)      277      0.0510

               rows  error_rate
unknown words                  
none            485      0.0820
up to 15%       105      0.0670
more than 15%    10      0.1000

                   rows  error_rate
confidence gap                     
close call (<0.1)    36      0.6390
medium               47      0.1910
decisive (>0.3)     517      0.0310
```

Read each table as a hypothesis test: a slice with a clearly higher error rate (and enough rows to trust it) is a finding. Two hypotheses are **supported**: short tickets are harder (about 13% errors against 5% for long ones: too few words to decide), and the model's own **confidence** is an excellent signal (close calls are wrong most of the time, decisive predictions almost never), so low-confidence predictions can be routed to a human. One hypothesis is **not supported**: tickets with unseen (misspelt) words are *not* clearly worse (similar error rates, and the worst slice has only 10 rows), because a ticket usually has several correct keywords left. A null result is a result: it tells you not to spend effort on spelling correction for this data.

### 6.5 A second dataset where the mistake has a name: negation

The tickets' errors are mostly ambiguity. The reviews have a specific, famous failure: a bag of words cannot tell "good" from "not good". We train on single words, find the errors, and **test the hypothesis** that negation is the cause.

```python run
rv_dev, rv_test = model_selection.train_test_split(reviews, test_size=0.3, random_state=0, stratify=reviews["positive"])
uni = pipeline.make_pipeline(TfidfVectorizer(), linear_model.LogisticRegression(max_iter=2000)).fit(rv_dev["text"], rv_dev["positive"])
p_uni = uni.predict(rv_test["text"])
print("unigram model: sealed test accuracy", round(metrics.accuracy_score(rv_test["positive"], p_uni), 3))
ev = rv_test.assign(pred=p_uni, wrong=(p_uni != rv_test["positive"]).astype(int))
ev["has negation"] = ev["text"].str.contains(r"\bnot\b")
ev["misleading word"] = False
print(ev.groupby("has negation")["wrong"].agg(rows="size", error_rate="mean").round(3).to_string())
print("\nsome errors:")
print(ev[ev["wrong"] == 1][["text", "positive", "pred"]].head(5).to_string())
```
```text
unigram model: sealed test accuracy 0.714
              rows  error_rate
has negation                  
False          569      0.0930
True           331      0.6160

some errors:
                                                text  positive  pred
2748      battery overall very quite excellent awful         1     0
2410  it it overall quite quality disappointing love         1     0
2881       really a product very price very not love         0     1
257   bought very screen really annoying not useless         1     0
2645         product screen item love awful not poor         1     0
```

The error rate for reviews with negation is far higher. The hypothesis is confirmed by the slice, and the top-word view shows how the unigram model misreads the words:

```python run
vec, clf = uni[0], uni[-1]
w = pd.Series(clf.coef_[0], index=vec.get_feature_names_out()).sort_values()
print("weights for 'positive' (unigram model): not =", round(float(w["not"]), 3), "| good =", round(float(w["good"]), 3), "| bad =", round(float(w["bad"]), 3))
e = explain(uni, "the item was not bad", 1)
print("\n'the item was not bad' (a positive review):", e["predicted"], "| for:", e["for"], "| against:", e["against"])
```
```text
weights for 'positive' (unigram model): not = 0.087 | good = 1.522 | bad = -1.317

'the item was not bad' (a positive review): 0 | for: [('bad', 0.778), ('item', 0.198), ('was', 0.097), ('the', 0.071)] | against: [('not', -0.03)]
```

`not` itself has little weight, and `bad` pulls toward negative. The model has no way to represent "not bad".

### 6.6 Fix, then re-measure

The fix follows from the diagnosis: add **bigrams**, so `not bad` becomes its own feature. The check is that the error rate on the negation slice falls.

```python run
bi = pipeline.make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), linear_model.LogisticRegression(max_iter=2000, C=5)).fit(rv_dev["text"], rv_dev["positive"])
p_bi = bi.predict(rv_test["text"])
ev["pred_bi"] = p_bi
ev["wrong_bi"] = (p_bi != rv_test["positive"]).astype(int)
tab = ev.groupby("has negation")[["wrong", "wrong_bi"]].mean().rename(columns={"wrong": "unigram error rate", "wrong_bi": "bigram error rate"})
print(tab.round(3).to_string())
print("overall accuracy: unigram %.3f -> bigram %.3f" % (metrics.accuracy_score(rv_test["positive"], p_uni), metrics.accuracy_score(rv_test["positive"], p_bi)))
e = explain(bi, "the item was not bad", 1)
print("'the item was not bad' with bigrams:", e["predicted"], "| for:", e["for"][:3], "| against:", e["against"][:3])
```
```text
              unigram error rate  bigram error rate
has negation                                       
False                     0.0930             0.0930
True                      0.6160             0.0360
overall accuracy: unigram 0.714 -> bigram 0.928
'the item was not bad' with bigrams: 1 | for: [('not bad', 2.609), ('was not', 0.633), ('the', 0.054)] | against: [('bad', -1.089), ('item', -0.176), ('was', -0.046)]
```

What remains wrong after the fix? Reviews whose text really mixes both sentiments (we built in a misleading word for the other sentiment); some of that error cannot be removed with a bag of n-grams, and it is worth estimating how much.

```python run
left = ev[ev["wrong_bi"] == 1]
print("errors left:", len(left), "of", len(ev), f"({len(left) / len(ev):.1%}); with negation: {int(left['has negation'].sum())}, without: {int((~left['has negation']).sum())}")
print(left[["text", "positive"]].head(4).to_string())
```
```text
errors left: 65 of 900 (7.2%); with negation: 12, without: 53
                                                  text  positive
264  very really quite quite product great not perfect         0
714        item was battery really price annoying love         1
799     this bought is quality price really bought bad         1
909       overall item it delivery screen battery love         1
```

### 6.7 An error report that someone can act on

Write the analysis in a fixed shape: **what, how many, why, what to do, how much it should help.**

| Finding | Evidence | Cause | Action | Expected effect |
|---|---|---|---|---|
| Reviews with negation are misclassified | error rate on the negation slice far above the rest | unigram features cannot express "not good" | add bigrams | the negation-slice error falls (measured above) |
| Short tickets are the hardest | slice table 6.4 | too few words to decide | route low-confidence tickets to a person; ask the user for more detail | human review only for the close calls |
| Typos (hypothesis tested) | share of unknown words | a misspelt keyword is not in the vocabulary | **no action now**: error rate is not clearly higher, and the slice is tiny | revisit if more data show an effect |
| The model uses agent names | top-word view (5.4) | spurious correlation in the training period | remove the signature at the source | lower CV, higher deployed accuracy |

### 6.8 Try it

1. Apply `explain` to the three most confident wrong predictions of the ticket model. What words misled it?
2. Add trigrams to the review model. Does the negation-slice error improve further, or does the vocabulary just grow?

## 7. Beyond bag of words

### 7.1 Hashing: no vocabulary to store

A `CountVectorizer` keeps a dictionary of every word, which can be huge and must be saved with the model. The **hashing trick** assigns each token to a column with a hash function (`column = hash(token) mod n_features`). There is no vocabulary to learn or store; the price is that different words can **collide** into the same column.

```python run
rows = []
for nf in [2 ** 6, 2 ** 8, 2 ** 10, 2 ** 16]:
    hv = HashingVectorizer(n_features=nf, alternate_sign=False, norm="l2")
    m = pipeline.make_pipeline(hv, linear_model.LogisticRegression(max_iter=2000))
    rows.append((nf, len(set(hv.transform(tk_dev["text"]).indices)), model_selection.cross_val_score(m, tk_dev["text"], tk_dev["label"], cv=cv5).mean()))
print(pd.DataFrame(rows, columns=["n_features", "columns actually used", "CV accuracy"]).round(3).to_string(index=False))
print("distinct tokens in the tickets:", len(CountVectorizer().fit(tk_dev['text']).vocabulary_))
```
```text
 n_features  columns actually used  CV accuracy
         64                     64       0.8610
        256                    237       0.9200
       1024                    452       0.9310
      65536                    599       0.9330
distinct tokens in the tickets: 602
```

With far fewer columns than words, collisions hurt. With enough columns (2^16) the hashed model matches the vocabulary model, with nothing to store and no `fit` of the vocabulary, which suits streaming and very large corpora. But you cannot map a column back to a word, so the word-level explanations of section 6 are lost.

### 7.2 Latent semantic analysis: a few dense dimensions

Truncated SVD of the TF-IDF matrix (ds.06 section 11) finds a few directions that capture most of the structure: words that occur together load on the same direction. This is **latent semantic analysis (LSA)**. Documents become short dense vectors, useful for compression, for similarity that survives different wording, and for visualisation (with the cautions of ds.06 section 12).

```python run
from sklearn import cluster
Xtf = TfidfVectorizer(min_df=3).fit_transform(tickets["text"])
for k in [2, 4, 8]:
    svd = decomposition.TruncatedSVD(n_components=k, random_state=0).fit(Xtf)
    Z = svd.transform(Xtf)
    km_labels = cluster.KMeans(4, n_init=10, random_state=0).fit_predict(Z / np.linalg.norm(Z, axis=1, keepdims=True).clip(1e-9))
    print(f"k={k}: variance kept {svd.explained_variance_ratio_.sum():.3f} | k-means (4 clusters) vs true categories, adjusted Rand index {metrics.adjusted_rand_score(tickets['label'], km_labels):.3f}")
svd4 = decomposition.TruncatedSVD(n_components=4, random_state=0).fit(Xtf)
names = TfidfVectorizer(min_df=3).fit(tickets["text"]).get_feature_names_out()
for i in range(4):
    print(f"component {i}:", [names[j] for j in np.argsort(-np.abs(svd4.components_[i]))[:6]])
```
```text
k=2: variance kept 0.038 | k-means (4 clusters) vs true categories, adjusted Rand index 0.383
k=4: variance kept 0.103 | k-means (4 clusters) vs true categories, adjusted Rand index 0.843
k=8: variance kept 0.150 | k-means (4 clusters) vs true categories, adjusted Rand index 0.843
component 0: ['please', 'app', 'that', 'to', 'and', 'help']
component 1: ['dispatch', 'shipped', 'package', 'tracking', 'delayed', 'warehouse']
component 2: ['locked', 'otp', 'invoice', 'coupon', 'verification', 'overcharged']
component 3: ['button', 'slow', 'bug', 'update', 'glitch', 'stuck']
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Animate or draw truncated SVD (LSA) on a TF-IDF matrix of 2400 support tickets. Show the large sparse matrix being replaced by a dense 2400 x k matrix, for k = 2, 4 and 8. Add a small table of variance kept (0.038, 0.103, 0.150) and k-means adjusted Rand index (0.383, 0.843, 0.843). Highlight that k = 4 matches the four ticket categories well."

### 7.3 Embeddings and transformers (what comes next)

Modern systems replace the count matrix by **embeddings**: dense vectors, learned from huge corpora, in which words (or whole sentences) with similar meanings are near each other, so "refund" and "reimbursement" are close even though they share no letters. Pretrained transformer models produce such vectors and can be fine-tuned for classification. That is the subject of ml.04 and ml.05; no such model is installed or downloadable here.

| Method | Understands | Cost | Explainable | Start here when |
|---|---|---|---|---|
| Bag of words / TF-IDF + linear | which words occur | tiny, fast | yes, word by word | always, as the baseline |
| Char n-grams | spelling variants | small | partly | typos, many languages |
| Hashing | same as BoW, no vocabulary | tiny | no | huge or streaming data |
| LSA | co-occurrence | small | weakly | compression, similarity |
| Pretrained embeddings / transformers | meaning, context, word order | large | hard | the baseline is not enough, and you can afford it |

```python
# Try it on your machine:  pip install sentence-transformers   (not installed here, so no output is shown)
from sentence_transformers import SentenceTransformer
enc = SentenceTransformer("all-MiniLM-L6-v2")                       # downloads a small pretrained model
Z = enc.encode(tk_dev["text"].tolist())                             # dense vectors: (rows, 384)
clf = linear_model.LogisticRegression(max_iter=2000).fit(Z, tk_dev["label"])
```

The rule of this course applies again: **build the TF-IDF baseline first**, then see whether the heavier model buys enough to justify its cost, its slowness and the loss of word-level explanations.

### 7.4 Try it

1. In the hashing experiment, count how many distinct tokens share a column when `n_features = 256`. Which words collide?
2. Compute the cosine similarity between two tickets of the same class in LSA space with `k = 4` and in raw TF-IDF space. Which separates the classes better?


## 8. Recommender systems: the problem and the data

### 8.1 The problem

A recommender answers one question: **"Of the things this person has not seen yet, which will they like most?"** It drives the shelves of every shop, video service and music app. Two flavours:

| Task | Output | Typical metric |
|---|---|---|
| **Rating prediction** | the rating a user would give an item | RMSE, MAE |
| **Top-N recommendation** | a ranked list of `N` items for a user | precision@k, recall@k, NDCG@k, hit rate |

Real products care almost entirely about the second; the first is easier to study and still appears in textbooks. We do both and point out where they disagree.

### 8.2 Families of methods

| Family | Idea | Needs | Weakness |
|---|---|---|---|
| **Non-personalised** | recommend what is popular or highly rated | counts | same list for everyone |
| **Content-based** | recommend items similar (in features) to what the user liked | item features (genre, text) | needs good features; narrow |
| **Collaborative filtering (neighbourhood)** | users who agreed in the past will agree again; or items rated alike | interactions only | sparse data, cold start |
| **Matrix factorisation** | represent users and items by short vectors whose dot product predicts the rating | interactions only | cold start, needs tuning |
| **Hybrid** | combine the above | both | more machinery |

And two kinds of signal. **Explicit feedback** (star ratings) says how much a user liked something, but few people give it. **Implicit feedback** (clicks, views, purchases, skips) is abundant but ambiguous: a view is not a like, and a missing view does not mean dislike. Section 13 treats it.

### 8.3 A dataset with hidden tastes

We generate 600 users and 300 movies. Each movie has a hidden vector of "genre loadings" and each user a hidden vector of tastes; a rating combines a user bias (some people rate generously), an item bias (some movies are just better), and the taste-by-genre match. Three realistic features are built in: users rate **popular movies far more often** (and movies they expect to like), activity is heavy-tailed (a few users rate a lot), and movies have **release dates** so late releases arrive with no history (cold start).

```python run
GENRES = ["Action", "Comedy", "Drama", "Sci-Fi"]

def make_ratings(n_users=600, n_items=300, seed=0):
    r = np.random.default_rng(seed)
    k = len(GENRES)
    P, Q = r.normal(0, 1, (n_users, k)), r.normal(0, 1, (n_items, k))               # hidden tastes and hidden genre loadings
    bu, bi = r.normal(0, 0.35, n_users), r.normal(0, 0.5, n_items)
    pop = np.exp(r.normal(0, 1.0, n_items))                                          # some movies are far more visible
    release = r.integers(0, 330, n_items); release[:90] = 0                          # 90 old movies, the rest released during the year
    release[-24:] = r.integers(345, 362, 24)                                          # 24 movies arrive in the last three weeks: they will be cold
    activity = np.clip(r.lognormal(np.log(25), 0.7, n_users).astype(int), 5, 150)
    rows = []
    for u in range(n_users):
        aff = Q @ P[u]
        w = pop * np.exp(0.5 * aff)                                                   # people watch popular movies and movies they expect to like
        chosen = r.choice(n_items, size=min(activity[u], n_items), replace=False, p=w / w.sum())
        for i in chosen:
            t = int(r.integers(release[i], 365))
            rating = np.clip(np.round(3.4 + bu[u] + bi[i] + aff[i] / np.sqrt(k) + r.normal(0, 0.45)), 1, 5)
            rows.append((u, int(i), int(rating), t))
    df = pd.DataFrame(rows, columns=["user", "item", "rating", "ts"])
    items = pd.DataFrame({"item": np.arange(n_items), "genre": [GENRES[g] for g in Q.argmax(1)], "release": release})
    return df, items

ratings, items = make_ratings()
n_users, n_items = ratings["user"].nunique(), 300
print(ratings.shape, "| users", n_users, "| items", ratings["item"].nunique(), "of", n_items)
print(ratings.head(5).to_string(index=False))
```
```text
(18779, 4) | users 600 | items 300 of 300
 user  item  rating  ts
    0   179       3 336
    0    88       4 337
    0     5       4  68
    0     4       2 321
    0   115       4 255
```

### 8.4 Look before you model

```python run
density = len(ratings) / (n_users * n_items)
print(f"density of the user x item matrix: {density:.2%} (so {1 - density:.1%} of it is empty)")
print("rating distribution:", ratings["rating"].value_counts(normalize=True).sort_index().round(3).to_dict(), "| mean", round(ratings["rating"].mean(), 3))
per_item = ratings.groupby("item").size().sort_values(ascending=False)
top10 = per_item.head(n_items // 10).sum() / per_item.sum()
print(f"the most-rated 10% of movies receive {top10:.0%} of all ratings; {int((per_item.reindex(range(n_items)).fillna(0) < 5).sum())} movies have fewer than 5 ratings")
per_user = ratings.groupby("user").size()
print("ratings per user: min %d, median %d, 90th percentile %d, max %d" % (per_user.min(), per_user.median(), per_user.quantile(.9), per_user.max()))
print("mean rating by genre of the movie:", ratings.merge(items, on="item").groupby("genre")["rating"].mean().round(2).to_dict())
```
```text
density of the user x item matrix: 10.43% (so 89.6% of it is empty)
rating distribution: {1: 0.013, 2: 0.078, 3: 0.231, 4: 0.31, 5: 0.368} | mean 3.941
the most-rated 10% of movies receive 27% of all ratings; 2 movies have fewer than 5 ratings
ratings per user: min 5, median 25, 90th percentile 62, max 150
mean rating by genre of the movie: {'Action': 3.86, 'Comedy': 3.9, 'Drama': 3.92, 'Sci-Fi': 4.09}
```

Three facts to carry forward. The matrix is extremely **sparse**. A few items collect most of the ratings (a **long tail** of items with almost no data). And ratings are **not missing at random**: people choose what to rate, so the observed ratings are biased toward things they expected to like. That last fact makes offline evaluation treacherous (section 9).

## 9. Evaluating a recommender

### 9.1 Split by time, per user

A random split of ratings has two flaws. It lets the model train on a user's *later* ratings and be tested on *earlier* ones (the future leaking, ds.04 section 7), and it may put almost all of a user's ratings in training or none at all. The honest protocol mimics deployment: **for every user, hide their most recent `k` ratings** and recommend them from everything before.

```python run
def split_leave_last(df, k=3):
    d = df.sort_values(["user", "ts", "item"])
    from_end = d.groupby("user").cumcount(ascending=False)
    return d[from_end >= k].reset_index(drop=True), d[from_end < k].reset_index(drop=True)

train, test = split_leave_last(ratings, k=3)
print(f"train {len(train)} ratings | test {len(test)} ratings ({test['user'].nunique()} users, last 3 each)")
print("every test rating is later than that user's training ratings:", bool((test.groupby("user")["ts"].min() >= train.groupby("user")["ts"].max().reindex(test['user'].unique()).to_numpy()).all()))
unseen_items = set(test["item"]) - set(train["item"])
print(f"test ratings on movies with NO training ratings (cold items): {test['item'].isin(unseen_items).mean():.1%}")
```
```text
train 16979 ratings | test 1800 ratings (600 users, last 3 each)
every test rating is later than that user's training ratings: True
test ratings on movies with NO training ratings (cold items): 0.0%
```

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw a timeline for three users. Each user's ratings are dots in time order. Colour all but the last 3 dots as train, and the last 3 dots as test. Mark a vertical line per user where the split falls. Contrast it with a random split where test dots appear before train dots, and label that as future leakage. Total: 600 users, 16979 train and 1800 test ratings."

(`from_end >= k` keeps all but the last `k` in training; ties in `ts` are broken by the item id so the split is deterministic.)

### 9.2 Metrics for top-N

For a user, the model returns a ranked list of `k` items **that the user has not rated in training**. An item in the user's test set with rating at least 4 is **relevant**. With `rel` the set of relevant items:

| Metric | Definition | Reads as |
|---|---|---|
| **precision@k** | hits in the list / k | how much of the list is good |
| **recall@k** | hits / number of relevant items | how much of the good was found |
| **hit rate@k** | 1 if any hit else 0 | did we find at least one |
| **NDCG@k** | discounted gain of hits by position, divided by the best possible | rewards putting hits near the top |
| **MAP@k** | average of the precision at each hit position | like NDCG, rank-sensitive |
| **coverage** | share of the catalogue that is ever recommended | does it recommend widely |
| **novelty** | average `−log2(popularity)` of recommended items | does it go beyond the obvious |

```python run
def dcg(hits):                                              # hits: list of 0/1 by position (position 1 first)
    return sum(h / math.log2(pos + 2) for pos, h in enumerate(hits))

def user_metrics(rec, relevant, k):
    hits = [1 if i in relevant else 0 for i in rec[:k]]
    n_rel = len(relevant)
    ideal = dcg([1] * min(n_rel, k))
    ap = sum((sum(hits[: j + 1]) / (j + 1)) for j, h in enumerate(hits) if h) / min(n_rel, k) if n_rel else 0.0
    return {"precision": sum(hits) / k, "recall": sum(hits) / n_rel if n_rel else 0.0, "hit": float(sum(hits) > 0),
            "ndcg": dcg(hits) / ideal if ideal else 0.0, "map": ap}

# a hand-checkable example: 3 relevant items {A, B, C}; the model lists [A, X, B, Y, Z] for k = 5
m = user_metrics(["A", "X", "B", "Y", "Z"], {"A", "B", "C"}, 5)
print({k_: round(v, 4) for k_, v in m.items()})
print("by hand: precision 2/5 = 0.4 | recall 2/3 = 0.6667 | NDCG = (1/log2(2) + 1/log2(4)) / (1/log2(2) + 1/log2(3) + 1/log2(4)) =",
      round((1 + 0.5) / (1 + 0.63093 + 0.5), 4))
```
```text
{'precision': 0.4, 'recall': 0.6667, 'hit': 1.0, 'ndcg': 0.7039, 'map': 0.5556}
by hand: precision 2/5 = 0.4 | recall 2/3 = 0.6667 | NDCG = (1/log2(2) + 1/log2(4)) / (1/log2(2) + 1/log2(3) + 1/log2(4)) = 0.7039
```

### 9.3 The evaluator

```python run
def build_matrix(df, shape=(n_users, n_items), value="rating"):
    return sparse.csr_matrix((df[value].astype(float), (df["user"], df["item"])), shape=shape)

REL = 4
test_rel = test[test["rating"] >= REL].groupby("user")["item"].apply(set).to_dict()
eval_users = np.array(sorted(test_rel))
train_seen = build_matrix(train) > 0
print(f"{len(eval_users)} users have at least one relevant (rating >= {REL}) test movie")

def recommend_from_scores(scores, users, k=10):
    S = scores[users].copy()
    S[train_seen[users].toarray()] = -np.inf                       # never recommend what the user already rated
    top = np.argpartition(-S, k, axis=1)[:, :k]
    order = np.take_along_axis(S, top, axis=1).argsort(axis=1)[:, ::-1]
    return np.take_along_axis(top, order, axis=1)

def evaluate_topn(scores, k=10, users=eval_users):
    recs = recommend_from_scores(scores, users, k)
    per_user = pd.DataFrame([user_metrics(list(recs[n]), test_rel[u], k) for n, u in enumerate(users)], index=users)
    item_pop = np.asarray((train_seen).sum(0)).ravel() + 1
    novelty = float(np.mean(-np.log2(item_pop[recs] / n_users)))
    summary = per_user.mean().to_dict() | {"coverage": len(np.unique(recs)) / n_items, "novelty": novelty}
    return summary, per_user

def evaluate_rmse(predict_pairs, df=test):
    p = predict_pairs(df["user"].to_numpy(), df["item"].to_numpy())
    return float(np.sqrt(np.mean((p - df["rating"].to_numpy()) ** 2))), float(np.mean(np.abs(p - df["rating"].to_numpy())))
```
```text
560 users have at least one relevant (rating >= 4) test movie
```

### 9.4 Offline evaluation is biased, and what to do about it

Three warnings before any numbers:

1. **Exposure bias.** Your logged data only contain ratings of items the old system (or the users' own browsing) exposed. An item never shown has no rating, so it cannot be "relevant" in the test set even if the user would have loved it. Offline metrics systematically favour recommenders that resemble the old system, popularity above all.
2. **Relevance threshold.** Counting only ratings of 4 or more as relevant ignores that an unrated item may be liked.
3. **The truth is online.** The real test of a recommender is an experiment with real users (ds.09), where the metric is what they do next. Offline evaluation is a filter to discard bad ideas cheaply, not proof that a good one works.

## 10. Baselines: popularity and bias

### 10.1 Non-personalised top-N

> **Predict the output.** Four non-personalised recommenders: random, "most popular" (by number of ratings), "highest rated" (raw average rating) and "highest rated" with the average shrunk toward the global mean. Rank them by NDCG@10. Where do you expect the raw average to land?

<details><summary>Answer</summary>

Popularity is clearly first (NDCG 0.056). The raw average is the worst of the four (0.019), no better than random (0.022): a movie rated once with five stars tops the list. Shrinking the average helps a little (0.024) but "highest rated" lists remain far behind popularity. People really do watch what is popular, so a recommender has to beat that, not random.

</details>

```python run
cnt = np.asarray(train_seen.sum(0)).ravel().astype(float)                      # number of training ratings per item
item_sum = np.asarray(build_matrix(train).sum(0)).ravel()
mu = train["rating"].mean()

def shrunk_mean(C=10):
    return (item_sum + C * mu) / (cnt + C)                                      # item mean pulled toward the global mean when data are few

rng = np.random.default_rng(0)
models_scores = {
    "random": rng.random((n_users, n_items)),
    "most popular (count)": np.tile(cnt, (n_users, 1)),
    "highest rated (raw mean)": np.tile(np.where(cnt > 0, item_sum / np.maximum(cnt, 1), 0), (n_users, 1)),
    "highest rated (shrunk mean)": np.tile(shrunk_mean(10), (n_users, 1)),
}
rows = {n: evaluate_topn(s)[0] for n, s in models_scores.items()}
print(pd.DataFrame(rows).T[["precision", "recall", "hit", "ndcg", "coverage", "novelty"]].round(4).to_string())
```
```text
                             precision  recall    hit   ndcg  coverage  novelty
random                          0.0080  0.0396 0.0786 0.0220    1.0000   3.8865
most popular (count)            0.0202  0.0997 0.1946 0.0562    0.1733   1.7951
highest rated (raw mean)        0.0066  0.0318 0.0661 0.0194    0.0633   3.5808
highest rated (shrunk mean)     0.0086  0.0411 0.0857 0.0237    0.0800   2.9249
```

Three results to take in. **Random** is the floor. The **raw mean** is terrible: a movie rated once with 5 stars tops the list. **Shrinking** the mean toward the global mean (the same idea as ridge and as the smoothing of Naive Bayes) helps, but only a little: "highest rated" lists are weak recommenders either way. And **popularity** is a very strong top-N baseline in this data, since people really do watch what is popular. Every personalised method in this chapter has to beat it, and the honest ones will show by how little.

### 10.2 The bias model for rating prediction

A rating is roughly `global mean + how generous the user is + how good the item is`:

```text
r̂(u, i) = μ + b_u + b_i
```

Fit `b_u` and `b_i` by regularised least squares with alternating updates: each item bias is the (shrunk) mean of `r − μ − b_u` over its ratings, and each user bias likewise. The regularisation `λ` shrinks the biases of items or users with few ratings toward 0.

```python run
class BiasModel:
    def __init__(self, lam_i=10.0, lam_u=15.0, iters=15):
        self.lam_i, self.lam_u, self.iters = lam_i, lam_u, iters
    def fit(self, df):
        u, i, r = df["user"].to_numpy(), df["item"].to_numpy(), df["rating"].to_numpy(float)
        self.mu_ = r.mean()
        self.bu_, self.bi_ = np.zeros(n_users), np.zeros(n_items)
        for _ in range(self.iters):
            self.bi_ = np.bincount(i, r - self.mu_ - self.bu_[u], n_items) / (np.bincount(i, minlength=n_items) + self.lam_i)
            self.bu_ = np.bincount(u, r - self.mu_ - self.bi_[i], n_users) / (np.bincount(u, minlength=n_users) + self.lam_u)
        return self
    def predict_pairs(self, u, i):
        return np.clip(self.mu_ + self.bu_[u] + self.bi_[i], 1, 5)
    def score_matrix(self):
        return self.mu_ + self.bu_[:, None] + self.bi_[None, :]

glob = lambda u, i: np.full(len(u), mu)
item_mean_ = shrunk_mean(10)
user_sum = np.bincount(train["user"], train["rating"], n_users); user_cnt = np.bincount(train["user"], minlength=n_users)
user_mean = (user_sum + 5 * mu) / (user_cnt + 5)
bias = BiasModel().fit(train)
rows = []
for name, fn in [("global mean", glob), ("item mean (shrunk)", lambda u, i: item_mean_[i]), ("user mean (shrunk)", lambda u, i: user_mean[u]), ("bias model: mu + b_u + b_i", bias.predict_pairs)]:
    rmse, mae_ = evaluate_rmse(fn)
    rows.append((name, rmse, mae_))
print(pd.DataFrame(rows, columns=["rating predictor", "test RMSE", "test MAE"]).set_index("rating predictor").round(4).to_string())
```
```text
                            test RMSE  test MAE
rating predictor                               
global mean                    1.0458    0.8406
item mean (shrunk)             0.8892    0.7377
user mean (shrunk)             0.9897    0.8077
bias model: mu + b_u + b_i     0.8213    0.6655
```

The bias model is the baseline to beat for RMSE. Notice that it has **no personalisation of taste**: it cannot say that this user likes comedies. Everything personalised is judged by how much it improves on `μ + b_u + b_i`.

```python run
sc_bias = bias.score_matrix()
res_bias = evaluate_topn(sc_bias)[0]
pop_top = evaluate_topn(models_scores["most popular (count)"])[0]
print("top-10 ranking by mu + b_u + b_i: precision %.4f, NDCG %.4f | popularity: precision %.4f, NDCG %.4f" % (res_bias["precision"], res_bias["ndcg"], pop_top["precision"], pop_top["ndcg"]))
```
```text
top-10 ranking by mu + b_u + b_i: precision 0.0082, NDCG 0.0270 | popularity: precision 0.0202, NDCG 0.0562
```

### 10.3 Try it

1. Change `C` in `shrunk_mean` to 0, 3, 30, 300. Which gives the best ranking? What does very large `C` converge to?
2. Fit the bias model on a *random* split of the ratings instead of the time split. Does the RMSE look better? Why is that number not trustworthy?

## 11. Neighbourhood methods

### 11.1 The idea: people (or items) who agree

**Item-based collaborative filtering** says: two movies are similar if the same people rated them alike. To score movie `i` for user `u`, look at the other movies `u` has rated, weigh each by its similarity to `i`, and combine. It needs no knowledge of what the movies are about.

Steps:

1. Remove the biases (subtract the baseline prediction) so that "this user rates everything high" is not mistaken for agreement.
2. Compute the **cosine similarity** between item columns of the centred rating matrix.
3. Shrink similarities that rest on few common raters (a similarity from two people is noise).
4. Predict `r̂(u,i) = baseline(u,i) + Σ_j s_ij · (r_uj − baseline(u,j)) / Σ_j |s_ij|` over the `k` most similar items `j` that `u` rated.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw item-based collaborative filtering on a small user x item rating matrix with many empty cells. Show four steps: subtract the baseline from each rating, take cosine similarity between two item columns, shrink it if few people rated both, then predict for user u and item i by a weighted average of that user's centred ratings on the k most similar items. Highlight the columns being compared and the predicted cell."

### 11.2 Implementation, checked against scikit-learn

```python run
from sklearn.metrics.pairwise import cosine_similarity

R = build_matrix(train)
resid = train.assign(res=train["rating"] - bias.predict_pairs(train["user"].to_numpy(), train["item"].to_numpy()))
Rc = build_matrix(resid, value="res")                                                # residual matrix (sparse, 0 = unobserved)
S_raw = cosine_similarity(Rc.T, dense_output=True)                                    # item-item cosine on the residuals
np.fill_diagonal(S_raw, 0)

# the same by hand: columns are item vectors
Rd = Rc.toarray()
norms = np.linalg.norm(Rd, axis=0).clip(1e-12)
S_hand = (Rd.T @ Rd) / np.outer(norms, norms)
np.fill_diagonal(S_hand, 0)
print("our cosine matrix equals scikit-learn's:", bool(np.allclose(S_hand, S_raw, atol=1e-12)), "| shape", S_hand.shape)

co = (R > 0).T.astype(float) @ (R > 0).astype(float)                                  # number of users who rated both items
def shrink(S, shrinkage=10):
    c = co.toarray()
    return S * np.where(c > 0, c / (c + shrinkage), 0.0)
for sh in [0, 10, 40]:
    S_ = shrink(S_raw, sh)
    print(f"shrinkage {sh:2d}: mean |similarity| {np.abs(S_).mean():.4f}, largest {S_.max():.3f}")
```
```text
our cosine matrix equals scikit-learn's: True | shape (300, 300)
shrinkage  0: mean |similarity| 0.0543, largest 0.477
shrinkage 10: mean |similarity| 0.0232, largest 0.270
shrinkage 40: mean |similarity| 0.0101, largest 0.216
```

```python run
class ItemKNN:
    def __init__(self, k=30, shrinkage=10):
        self.k, self.shrinkage = k, shrinkage
    def fit(self, df, base):
        self.base = base
        self.R = build_matrix(df)
        res = df.assign(res=df["rating"] - base.predict_pairs(df["user"].to_numpy(), df["item"].to_numpy()))
        Rc = build_matrix(res, value="res").toarray()
        nrm = np.linalg.norm(Rc, axis=0).clip(1e-12)
        S = (Rc.T @ Rc) / np.outer(nrm, nrm)
        np.fill_diagonal(S, 0)
        seen = (self.R > 0).astype(float)
        co = (seen.T @ seen).toarray()
        self.S = S * co / (co + self.shrinkage)
        self.Rc = Rc
        # keep only the k strongest neighbours of each item
        drop = np.argsort(-np.abs(self.S), axis=1)[:, self.k:]
        np.put_along_axis(self.S, drop, 0.0, axis=1)
        return self
    def predict_pairs(self, u, i):
        num = np.einsum("nj,nj->n", self.Rc[u], self.S[i])                       # sum of s_ij * residual_uj over the user's rated j
        den = np.einsum("nj,nj->n", (self.Rc[u] != 0).astype(float), np.abs(self.S[i]))
        return np.clip(self.base.predict_pairs(u, i) + num / np.maximum(den, 1e-9), 1, 5)
    def score_matrix(self):
        # ranking score: how strongly the items the user liked (positive residual) point at the candidate
        return np.maximum(self.Rc, 0) @ np.maximum(self.S, 0)

for k_nn in [10, 30, 100]:
    knn = ItemKNN(k=k_nn).fit(train, bias)
    rmse, mae_ = evaluate_rmse(knn.predict_pairs)
    top = evaluate_topn(knn.score_matrix())[0]
    print(f"item-kNN k={k_nn:3d}: test RMSE {rmse:.4f} | top-10 precision {top['precision']:.4f}, ndcg {top['ndcg']:.4f}")
print("bias model alone: RMSE %.4f" % evaluate_rmse(bias.predict_pairs)[0])
```
```text
item-kNN k= 10: test RMSE 0.8201 | top-10 precision 0.0411, ndcg 0.1253
item-kNN k= 30: test RMSE 0.7898 | top-10 precision 0.0493, ndcg 0.1508
item-kNN k=100: test RMSE 0.7579 | top-10 precision 0.0520, ndcg 0.1565
bias model alone: RMSE 0.8213
```

### 11.3 What the neighbours look like

A neighbourhood method is **explainable**: "we recommend movie 17 because you liked movies 4, 88 and 203". And the neighbours should make sense. Our hidden genres let us check:

```python run
knn = ItemKNN(k=30).fit(train, bias)
same = []
for i in range(n_items):
    nb = np.argsort(-knn.S[i])[:5]
    same.append(np.mean(items["genre"].to_numpy()[nb] == items["genre"].iloc[i]))
print(f"share of an item's 5 nearest neighbours that have the SAME hidden genre: {np.mean(same):.2f} (chance would be about 0.25)")
i0 = int(per_item.index[0])
print("most-rated movie", i0, items.loc[i0, "genre"], "-> nearest neighbours:", [(int(j), items.loc[j, "genre"], round(float(knn.S[i0, j]), 3)) for j in np.argsort(-knn.S[i0])[:4]])
```
```text
share of an item's 5 nearest neighbours that have the SAME hidden genre: 0.57 (chance would be about 0.25)
most-rated movie 3 Action -> nearest neighbours: [(215, 'Action', 0.263), (117, 'Action', 0.225), (149, 'Action', 0.193), (256, 'Action', 0.188)]
```

### 11.4 User-based and the cost of neighbourhoods

**User-based** collaborative filtering uses the same recipe with the roles swapped (find similar users, average what they liked). Item-based is usually preferred because items are more stable than users and the catalogue is smaller than the user base. Cost: the similarity matrix has `items²` entries. At a million items that is a trillion entries, so large systems use approximate nearest-neighbour search or factorisation (next section).

### 11.5 Try it

1. Rebuild `ItemKNN` using *raw* ratings instead of residuals for the similarity. Does the test RMSE get worse? What does the user bias do to the similarities?
2. Vary `shrinkage` from 0 to 100 and print RMSE. Which value is best, and what happens at 0?

## 12. Matrix factorisation

### 12.1 The idea: short vectors whose dot product is the rating

Give every user `u` a vector `p_u` and every item `i` a vector `q_i`, each with `k` numbers (the **latent factors**), and predict

```text
r̂(u, i) = μ + b_u + b_i + p_u · q_i
```

If we are lucky the `k` numbers capture things like "how much action", "how much comedy", never named by anyone. The model fits the vectors to the *observed* ratings by minimising squared error plus a penalty (regularisation, as ridge in ds.06) so that it does not memorise:

```text
minimise  Σ_(u,i observed) ( r_ui − μ − b_u − b_i − p_u·q_i )²  +  λ ( ‖p_u‖² + ‖q_i‖² + b_u² + b_i² )
```

The matrix of all predictions has rank `k`: a huge, mostly-empty matrix is replaced by two thin ones. Compare with the truncated SVD of ds.06 section 11: SVD needs a complete matrix, and ours is 98% empty, so we fit only to the observed entries.

> **Visualise it** *(optional; paste into any AI chat that can draw diagrams or code a small animation. The chapter works without it.)*
> "Draw matrix factorisation for a recommender. Show a large, mostly empty users x items rating matrix (about 98% empty) equal to a thin users x k matrix P times a thin k x items matrix Q, plus biases. Pick one user vector p_u and one item vector q_i with k = 2 and show their dot product plus mu + b_u + b_i giving the predicted rating. Highlight that only observed cells are fitted."

### 12.2 Stochastic gradient descent

Loop over the observed ratings (shuffled) and nudge the five things involved in each prediction against the gradient of its squared error. For error `e = r − r̂`:

```text
b_u += lr·(e − λ·b_u)         b_i += lr·(e − λ·b_i)
p_u += lr·(e·q_i − λ·p_u)     q_i += lr·(e·p_u − λ·q_i)      (using the old p_u, q_i in both lines)
```

```python run
class MF_SGD:
    def __init__(self, k=8, lr=0.02, reg=0.05, epochs=30, seed=0):
        self.k, self.lr, self.reg, self.epochs, self.seed = k, lr, reg, epochs, seed
    def fit(self, df, val=None):
        r_ = np.random.default_rng(self.seed)
        u, i, y = df["user"].to_numpy(), df["item"].to_numpy(), df["rating"].to_numpy(float)
        self.mu_ = y.mean()
        self.bu_, self.bi_ = np.zeros(n_users), np.zeros(n_items)
        self.P, self.Q = r_.normal(0, 0.1, (n_users, self.k)), r_.normal(0, 0.1, (n_items, self.k))
        self.history_ = []
        for ep in range(self.epochs):
            for n in r_.permutation(len(y)):
                a, b = u[n], i[n]
                e = y[n] - (self.mu_ + self.bu_[a] + self.bi_[b] + self.P[a] @ self.Q[b])
                self.bu_[a] += self.lr * (e - self.reg * self.bu_[a])
                self.bi_[b] += self.lr * (e - self.reg * self.bi_[b])
                pa = self.P[a].copy()
                self.P[a] += self.lr * (e * self.Q[b] - self.reg * self.P[a])
                self.Q[b] += self.lr * (e * pa - self.reg * self.Q[b])
            tr = np.sqrt(np.mean((self.predict_pairs(u, i) - y) ** 2))
            self.history_.append((tr, np.sqrt(np.mean((self.predict_pairs(val["user"].to_numpy(), val["item"].to_numpy()) - val["rating"].to_numpy()) ** 2)) if val is not None else np.nan))
        return self
    def predict_pairs(self, u, i):
        return np.clip(self.mu_ + self.bu_[u] + self.bi_[i] + np.einsum("nk,nk->n", self.P[u], self.Q[i]), 1, 5)
    def score_matrix(self):
        return self.mu_ + self.bu_[:, None] + self.bi_[None, :] + self.P @ self.Q.T

# a validation slice for tuning: the user's LAST rating before the test ratings (never touching the test set)
train_core, val = split_leave_last(train, k=1)
t0 = time.perf_counter()
mf = MF_SGD(k=8, lr=0.02, reg=0.05, epochs=30).fit(train_core, val=val)
print(f"30 epochs of SGD in {time.perf_counter() - t0:.1f} s")
h = pd.DataFrame(mf.history_, columns=["train RMSE", "validation RMSE"], index=range(1, 31))
print(h.iloc[[0, 1, 2, 4, 9, 14, 19, 29]].round(4).to_string())
bias_tc = BiasModel().fit(train_core)
print('bias model on the same validation ratings: RMSE %.4f' % np.sqrt(np.mean((bias_tc.predict_pairs(val['user'].to_numpy(), val['item'].to_numpy()) - val['rating'].to_numpy()) ** 2)))
```
```text
30 epochs of SGD in 3.9 s
    train RMSE  validation RMSE
1       0.8188           0.8376
2       0.7903           0.8144
3       0.7802           0.8083
5       0.7674           0.8036
10      0.7020           0.7854
15      0.5863           0.7322
20      0.5093           0.6979
30      0.4459           0.6644
bias model on the same validation ratings: RMSE 0.8075
```

The training error keeps falling, and the **validation** error follows it down more slowly: by epoch 30 the model fits the training ratings at 0.45 RMSE but unseen ratings at 0.66. That gap is overfitting (ds.03 section 5); it is a healthy sign here only because the validation error is still falling and is far below the bias model's 0.81. SGD with a small step needs many passes before it finds the taste signal, so a run of 5 or 10 epochs would have wrongly concluded that factorisation does not help. We tune on `val` (an earlier slice of the training data) so that the test set stays sealed.

### 12.3 Choosing `k` and the regularisation

```python run
rows = []
for k_, reg in [(1, 0.05), (4, 0.05), (16, 0.05), (16, 0.2)]:
    m = MF_SGD(k=k_, lr=0.02, reg=reg, epochs=20).fit(train_core, val=val)
    rows.append((k_, reg, m.history_[-1][0], m.history_[-1][1], min(h_[1] for h_ in m.history_)))
print(pd.DataFrame(rows, columns=["factors k", "reg", "train RMSE", "val RMSE (last)", "val RMSE (best epoch)"]).round(4).to_string(index=False))
```
```text
 factors k    reg  train RMSE  val RMSE (last)  val RMSE (best epoch)
         1 0.0500      0.7333           0.7971                 0.7954
         4 0.0500      0.4665           0.6237                 0.6237
        16 0.0500      0.4631           0.6998                 0.6998
        16 0.2000      0.7626           0.7977                 0.7977
```

The pattern is the usual bias-variance trade-off. One factor is too little (validation 0.80, no better than biases alone). Four factors are best (0.62). Sixteen factors fit the training data as well as four but generalise worse (0.70): variance. And a heavy penalty (0.2) shrinks the vectors so much that the model underfits (0.80). The hidden truth has four genres, and the validation curve found it.

### 12.4 Alternating least squares (ALS)

If we hold all item vectors fixed, finding the best vector for **one user** is an ordinary ridge regression (ds.06 section 2): the ratings that user gave are the targets, the item vectors of those items are the features. The solution is closed-form. So alternate: solve every user's vector with the items fixed, then every item's vector with the users fixed. Each half-step **cannot increase** the objective, so the objective falls at every step, with no learning rate to tune. This is how most large implementations work, and each solve is independent, hence parallel.

For simplicity we factorise the residuals of the bias model (`r − μ − b_u − b_i`).

```python run
def als_fit(df, base, k=8, lam=0.05, iters=12, seed=0):
    u_, i_ = df["user"].to_numpy(), df["item"].to_numpy()
    y = df["rating"].to_numpy(float) - base.predict_pairs(u_, i_)
    r_ = np.random.default_rng(seed)
    P, Q = r_.normal(0, 0.1, (n_users, k)), r_.normal(0, 0.1, (n_items, k))
    by_user = [np.flatnonzero(u_ == a) for a in range(n_users)]
    by_item = [np.flatnonzero(i_ == b) for b in range(n_items)]
    obj = []
    len_u, len_i = np.bincount(u_, minlength=n_users), np.bincount(i_, minlength=n_items)
    for it in range(iters):
        for a in range(n_users):
            idx = by_user[a]
            if len(idx) == 0: continue
            A = Q[i_[idx]]
            P[a] = np.linalg.solve(A.T @ A + lam * len(idx) * np.eye(k), A.T @ y[idx])           # ridge, penalty scaled by the number of ratings
        for b in range(n_items):
            idx = by_item[b]
            if len(idx) == 0: continue
            A = P[u_[idx]]
            Q[b] = np.linalg.solve(A.T @ A + lam * len(idx) * np.eye(k), A.T @ y[idx])
        pred = np.einsum("nk,nk->n", P[u_], Q[i_])
        obj.append(np.sum((y - pred) ** 2) + lam * (np.sum(len_u[:, None] * P ** 2) + np.sum(len_i[:, None] * Q ** 2)))
    return P, Q, obj

P_als, Q_als, obj = als_fit(train, bias)
print("ALS objective after each full iteration:", np.round(obj, 1))
print("never increases:", bool(np.all(np.diff(obj) <= 1e-8)))
```
```text
ALS objective after each full iteration: [9028.2 7130.9 6513.5 6277.1 6110.1 5957.2 5837.9 5771.1 5741.2 5727.5 5720.  5714.9]
never increases: True
```

A check of the closed form: the solved vector for one user must satisfy the ridge normal equations, and equals `lstsq` on the augmented system.

```python run
a = 7
idx = np.flatnonzero(train["user"].to_numpy() == a)
yy = train["rating"].to_numpy(float)[idx] - bias.predict_pairs(train["user"].to_numpy()[idx], train["item"].to_numpy()[idx])
A = Q_als[train["item"].to_numpy()[idx]]
lam, k_ = 0.05, 8
aug_A = np.vstack([A, np.sqrt(lam * len(idx)) * np.eye(k_)]); aug_y = np.r_[yy, np.zeros(k_)]
via_lstsq = np.linalg.lstsq(aug_A, aug_y, rcond=None)[0]
print("user", a, "has", len(idx), "ratings | max |solve - lstsq on the augmented system| =", float(np.max(np.abs(np.linalg.solve(A.T @ A + lam * len(idx) * np.eye(k_), A.T @ yy) - via_lstsq))))
```
```text
user 7 has 12 ratings | max |solve - lstsq on the augmented system| = 6.106226635438361e-16
```

### 12.5 Compare everything on the sealed test set

> **Predict the output.** Four models are compared next: the bias model, item-kNN, matrix factorisation by SGD, and by ALS. Which will have the lowest RMSE (rating prediction), and which the highest NDCG@10 (top-N ranking)? Will they be the same model?

<details><summary>Answer</summary>

Not the same. The **SGD matrix factorisation** has the lowest RMSE (0.67, against 0.82 for the bias model), but **item-kNN** has the highest NDCG@10 (0.15, against 0.09 for the factorisation and 0.06 for popularity). The bias model predicts ratings well but ranks worse than popularity (NDCG 0.03). Rating accuracy and ranking quality are different goals.

</details>

```python run
class ALSModel:
    def __init__(self, P, Q, base): self.P, self.Q, self.base = P, Q, base
    def predict_pairs(self, u, i): return np.clip(self.base.predict_pairs(u, i) + np.einsum("nk,nk->n", self.P[u], self.Q[i]), 1, 5)
    def score_matrix(self): return self.base.score_matrix() + self.P @ self.Q.T

als_model = ALSModel(P_als, Q_als, bias)
mf_full = MF_SGD(k=8, lr=0.02, reg=0.05, epochs=30).fit(train)
cands = {"bias model": bias, "item-kNN (k=30)": ItemKNN(k=30).fit(train, bias), "matrix factorisation, SGD": mf_full, "matrix factorisation, ALS": als_model}
rows = []
for name, m in cands.items():
    rmse, mae_ = evaluate_rmse(m.predict_pairs)
    top = evaluate_topn(m.score_matrix())[0]
    rows.append((name, rmse, mae_, top["precision"], top["recall"], top["ndcg"], top["coverage"]))
pop = evaluate_topn(models_scores["most popular (count)"])[0]
rows.append(("(popularity, top-N only)", np.nan, np.nan, pop["precision"], pop["recall"], pop["ndcg"], pop["coverage"]))
print(pd.DataFrame(rows, columns=["model", "RMSE", "MAE", "precision@10", "recall@10", "NDCG@10", "coverage"]).set_index("model").round(4).to_string())
```
```text
                            RMSE    MAE  precision@10  recall@10  NDCG@10  coverage
model                                                                              
bias model                0.8213 0.6655        0.0082     0.0396   0.0270    0.0767
item-kNN (k=30)           0.7898 0.5877        0.0493     0.2259   0.1508    0.7200
matrix factorisation, SGD 0.6730 0.5188        0.0286     0.1318   0.0870    0.6133
matrix factorisation, ALS 0.7025 0.5249        0.0295     0.1318   0.0764    0.6800
(popularity, top-N only)     NaN    NaN        0.0202     0.0997   0.0562    0.1733
```

Read the two halves of the table separately. For **rating prediction** the factorisation models are the clear winners: RMSE falls from 0.82 (bias model) to 0.67 (SGD) and 0.70 (ALS), and item-kNN sits in between (0.79); that is the taste signal being found. For **top-N ranking** the order is different: item-kNN is best (NDCG 0.15), followed by the two factorisation models (0.09 and 0.08), then popularity (0.06), and the bias model is *worse than popularity* (0.03) even though it predicts ratings well. A model that is good at guessing the rating of a movie the user has already chosen to watch is not the same as a model that picks which movie to put on screen. The kNN ranking score, built from "movies similar to the ones this user liked", carries information about what people tend to watch, which the squared-error objective of the factorisation never sees. **Choose the metric to fit the product**: RMSE for "predict the star rating shown on the page", ranking metrics for "fill the home page".

### 12.6 Try it

1. Add a stopping rule to `MF_SGD`: stop when the validation RMSE has not improved for 3 epochs, and report the best epoch.
2. In `als_fit`, change the penalty from `lam * len(idx)` to a constant `lam`. What happens to the vectors of users with 5 ratings?

## 13. Implicit feedback, cold start and popularity bias

### 13.1 Implicit feedback

Most real systems have no star ratings. They have **interactions**: viewed, clicked, bought, listened. Treat them as a binary matrix `p_ui = 1` if the interaction happened, and unobserved otherwise. A missing entry is **not** a negative: it means "unknown, perhaps not exposed". The standard approach (Hu, Koren and Volinsky) fits all entries with **confidence weights**: observed interactions get high confidence `c = 1 + α·count`, unobserved ones confidence 1, and the target is 0/1. Because *every* entry now has a target, it needs the full matrix, and ALS makes it cheap with the identity `QᵀCᵤQ = QᵀQ + Qᵀ(Cᵤ − I)Q`.

```python run
def implicit_als(Rbin, k=16, lam=1.0, alpha=20.0, iters=10, seed=0):
    r_ = np.random.default_rng(seed)
    n_u, n_i = Rbin.shape
    P, Q = r_.normal(0, 0.1, (n_u, k)), r_.normal(0, 0.1, (n_i, k))
    Rd = Rbin.toarray()
    for _ in range(iters):
        QtQ = Q.T @ Q
        for a in range(n_u):
            obs = np.flatnonzero(Rd[a])
            Qo = Q[obs]
            A = QtQ + alpha * Qo.T @ Qo + lam * np.eye(k)                            # Q'Q + Q'(C-I)Q + lam I, with C-I = alpha on observed items
            P[a] = np.linalg.solve(A, (1 + alpha) * Qo.sum(0))                       # Q' C p with p = 1 on observed
        PtP = P.T @ P
        for b in range(n_i):
            obs = np.flatnonzero(Rd[:, b])
            Po = P[obs]
            A = PtP + alpha * Po.T @ Po + lam * np.eye(k)
            Q[b] = np.linalg.solve(A, (1 + alpha) * Po.sum(0))
    return P, Q

Ib = (build_matrix(train) > 0).astype(float)                                        # every rating counts as "watched"
t0 = time.perf_counter()
Pi, Qi = implicit_als(sparse.csr_matrix(Ib))
print(f"implicit ALS in {time.perf_counter() - t0:.1f} s")
rows = {"popularity": evaluate_topn(models_scores["most popular (count)"])[0], "implicit ALS (binary 'watched')": evaluate_topn(Pi @ Qi.T)[0],
        "explicit MF (SGD)": evaluate_topn(mf_full.score_matrix())[0]}
print(pd.DataFrame(rows).T[["precision", "recall", "ndcg", "coverage", "novelty"]].round(4).to_string())
```
```text
implicit ALS in 0.2 s
                                 precision  recall   ndcg  coverage  novelty
popularity                          0.0202  0.0997 0.0562    0.1733   1.7951
implicit ALS (binary 'watched')     0.0325  0.1518 0.0909    0.8533   2.7924
explicit MF (SGD)                   0.0286  0.1318 0.0870    0.6133   4.1122
```

The implicit model beats popularity and is close to the explicit factorisation on NDCG (0.09 against 0.09), with much higher coverage (0.85 against 0.61). It learns from *what users watched* (the exposure pattern), which is a signal that predicts what they watch next, and it needs no rating at all. The cost shows up in the next two sections.

### 13.2 Cold start

A collaborative model knows an item or a user only through interactions. A **new item** (no ratings) has no vector; a **new user** has no history. To measure it cleanly we **construct** the situation: the 24 movies added in the last three weeks are treated as brand new, so all their ratings are removed from the training data, the models are refit without them, and we ask how many of the ratings of 4 or more that these movies later received appear in the users' top-10.

```python run
cold_items = items.index[items["release"] >= 345].to_numpy()                          # the 24 newest movies
train_nc = train[~train["item"].isin(cold_items)]                                      # as if they had just been added: no history at all
new_rel = ratings[ratings["item"].isin(cold_items) & (ratings["rating"] >= REL)]       # what users later thought of them
print(f"{len(cold_items)} cold movies; they later received {len(new_rel)} ratings of 4 or more (from {new_rel['user'].nunique()} users)")

seen_nc = (build_matrix(train_nc) > 0).toarray()
cnt_nc = seen_nc.sum(0).astype(float)
bias_nc = BiasModel().fit(train_nc)
knn_nc = ItemKNN(k=30).fit(train_nc, bias_nc)
Pn, Qn = implicit_als(sparse.csr_matrix(seen_nc.astype(float)))
liked_nc = build_matrix(train_nc[train_nc["rating"] >= REL]) > 0
G = pd.get_dummies(items["genre"]).to_numpy(float)                                   # item x genre: known on the day an item is added
ug = liked_nc.astype(float) @ G
ug = ug / ug.sum(1, keepdims=True).clip(1)
content_score = ug @ G.T

def cold_hit_rate(scores, k=10):
    S = scores.astype(float).copy()
    S[seen_nc] = -np.inf
    top = np.argpartition(-S, k, axis=1)[:, :k]
    sets = [set(row) for row in top]
    return float(np.mean([i in sets[u] for u, i in zip(new_rel["user"], new_rel["item"])]))

rows = [("random (chance level)", cold_hit_rate(np.random.default_rng(1).random((n_users, n_items)))),
        ("popularity", cold_hit_rate(np.tile(cnt_nc, (n_users, 1)))),
        ("item-kNN", cold_hit_rate(knn_nc.score_matrix())),
        ("implicit ALS", cold_hit_rate(Pn @ Qn.T)),
        ("content-based (genre profile)", cold_hit_rate(content_score))]
print(pd.DataFrame(rows, columns=["model", "share of the later 4+ ratings of cold movies that were in the top 10"]).set_index("model").round(4).to_string())
```
```text
24 cold movies; they later received 759 ratings of 4 or more (from 374 users)
                               share of the later 4+ ratings of cold movies that were in the top 10
model                                                                                              
random (chance level)                                                                        0.0316
popularity                                                                                   0.0000
item-kNN                                                                                     0.0000
implicit ALS                                                                                 0.0000
content-based (genre profile)                                                                0.2134
```

Collaborative models cannot recommend a movie they have never seen interactions for: its score is zero for every user, so it never reaches the top 10. Only the content-based model, which needs just the genre the day the movie is added, finds any of them.

The content-based model finds some of the cold movies (well above chance) but is far from perfect: a genre is a coarse feature, and about 75 movies share each genre, so it cannot pick among them. That is the point of content-based methods: **item features known on day one** let you score a brand-new movie at all. Practical systems blend the two (a hybrid): expose a new item through content, reserve a few slots for exploration, and let the item enter the collaborative model once it has interactions.

### 13.3 Popularity bias and what accuracy hides

Collaborative models inherit the habits of the data: popular items get most of the interactions, so the model recommends popular items, which get more interactions. Three consequences: low **coverage** (only a small part of the catalogue is ever shown), low **novelty**, and a **feedback loop** that starves the long tail. Measure it.

```python run
def gini(x):
    x = np.sort(np.asarray(x, float)); n = len(x)
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum())) if x.sum() > 0 else 0.0
rows = []
for name, sc in [("random", models_scores["random"]), ("popularity", models_scores["most popular (count)"]), ("bias model", sc_bias),
                 ("item-kNN", cands["item-kNN (k=30)"].score_matrix()), ("MF (SGD)", mf_full.score_matrix()), ("implicit ALS", Pi @ Qi.T)]:
    recs = recommend_from_scores(sc, np.arange(n_users), 10)
    exposure = np.bincount(recs.ravel(), minlength=n_items)
    share_top = exposure[np.argsort(-cnt)[: n_items // 10]].sum() / exposure.sum()
    rows.append((name, (exposure > 0).mean(), gini(exposure), share_top))
print(pd.DataFrame(rows, columns=["model", "share of catalogue ever recommended", "Gini of exposure (1 = all on a few)", "share of slots on the top-10% popular items"]).set_index("model").round(3).to_string())
```
```text
              share of catalogue ever recommended  Gini of exposure (1 = all on a few)  share of slots on the top-10% popular items
model                                                                                                                              
random                                     1.0000                               0.1330                                       0.0880
popularity                                 0.1770                               0.9470                                       0.9890
bias model                                 0.0800                               0.9610                                       0.1590
item-kNN                                   0.7200                               0.6570                                       0.2700
MF (SGD)                                   0.6170                               0.7830                                       0.0590
implicit ALS                               0.8570                               0.5330                                       0.3130
```

Levers: re-rank to add diversity or novelty, boost new items, cap how often an item can appear, and evaluate with metrics beyond accuracy. All of them cost some offline accuracy and can raise long-run satisfaction. That trade-off is a product decision, to be tested online.

Reading the table: popularity concentrates almost all slots (0.99) on the top 10% of movies and recommends only 18% of the catalogue, with an exposure Gini near 0.95. The bias model is the opposite trap: it recommends rarely-rated movies with high estimated biases (few slots on popular movies, but only 8% of the catalogue). Item-kNN and the implicit model spread exposure widely (72% and 86% of the catalogue). The factorisation sits in between. Accuracy and exposure are different axes, and a team should look at both.

### 13.4 Try it

1. Add `alpha=1` and `alpha=100` to `implicit_als`. How do precision and coverage move?
2. Build a hybrid that adds `0.5` times the implicit-ALS score (min-max normalised) to the popularity score. Does it keep popularity's accuracy while increasing coverage? Then reserve two of the ten slots for the content-based top items among the newest movies and re-run the cold-start table of 13.2.


## 14. Project: a movie recommender with an honest evaluation

### 14.1 The brief

A streaming service wants "movies you might like" on the home page. Build a small recommender library, **`recsys`**, that:

1. splits the interactions **by time, per user**, and refuses to leak the future into training,
2. offers the models of this chapter behind one interface: **popularity**, the **bias model**, **item-based collaborative filtering** and **matrix factorisation**,
3. serves recommendations through a class that **never recommends what the user already saw** and has a sensible **cold-start** fallback,
4. produces a report in which every personalised model is judged against **popularity** with a paired bootstrap over users, and says plainly when the evidence is not enough,
5. comes with **tests** that guard against the failures of this chapter.

### 14.2 The library

```python run
import pathlib, tempfile, subprocess, os
proj = pathlib.Path(tempfile.mkdtemp()) / "recsys_project"
proj.mkdir()
(proj / "recsys.py").write_text('''"""recsys: a small recommender library with an honest, time-based offline evaluation."""
import math
import numpy as np
import pandas as pd
from scipy import sparse


def split_leave_last(df, k=3):
    """Hide each user's last k ratings (by time) for testing; train on everything before."""
    d = df.sort_values(["user", "ts", "item"])
    from_end = d.groupby("user").cumcount(ascending=False)
    return d[from_end >= k].reset_index(drop=True), d[from_end < k].reset_index(drop=True)


def to_matrix(df, n_users, n_items, value="rating"):
    return sparse.csr_matrix((df[value].astype(float), (df["user"], df["item"])), shape=(n_users, n_items))


# ---------------- models: fit(train, n_users, n_items); predict_pairs(u, i); score_matrix() -> users x items ----------------
class Popularity:
    def fit(self, train, n_users, n_items):
        self.count_ = np.bincount(train["item"], minlength=n_items).astype(float)
        self.n_users, self.mu_ = n_users, train["rating"].mean()
        return self

    def predict_pairs(self, u, i):
        return np.full(len(u), self.mu_)

    def score_matrix(self):
        return np.tile(self.count_, (self.n_users, 1))


class BiasModel:
    def __init__(self, lam_i=10.0, lam_u=15.0, iters=15):
        self.lam_i, self.lam_u, self.iters = lam_i, lam_u, iters

    def fit(self, train, n_users, n_items):
        u, i, r = train["user"].to_numpy(), train["item"].to_numpy(), train["rating"].to_numpy(float)
        self.mu_ = r.mean()
        self.bu_, self.bi_ = np.zeros(n_users), np.zeros(n_items)
        for _ in range(self.iters):
            self.bi_ = np.bincount(i, r - self.mu_ - self.bu_[u], n_items) / (np.bincount(i, minlength=n_items) + self.lam_i)
            self.bu_ = np.bincount(u, r - self.mu_ - self.bi_[i], n_users) / (np.bincount(u, minlength=n_users) + self.lam_u)
        return self

    def predict_pairs(self, u, i):
        return np.clip(self.mu_ + self.bu_[u] + self.bi_[i], 1, 5)

    def score_matrix(self):
        return self.mu_ + self.bu_[:, None] + self.bi_[None, :]


class ItemKNN:
    def __init__(self, k=30, shrinkage=10):
        self.k, self.shrinkage = k, shrinkage

    def fit(self, train, n_users, n_items):
        self.base_ = BiasModel().fit(train, n_users, n_items)
        u, i = train["user"].to_numpy(), train["item"].to_numpy()
        res = train.assign(res=train["rating"].to_numpy() - self.base_.predict_pairs(u, i))
        Rc = to_matrix(res, n_users, n_items, "res").toarray()
        seen = (to_matrix(train, n_users, n_items) > 0).astype(float)
        nrm = np.linalg.norm(Rc, axis=0).clip(1e-12)
        S = (Rc.T @ Rc) / np.outer(nrm, nrm)
        np.fill_diagonal(S, 0)
        co = (seen.T @ seen).toarray()
        S = S * co / (co + self.shrinkage)
        np.put_along_axis(S, np.argsort(-np.abs(S), axis=1)[:, self.k:], 0.0, axis=1)
        self.S_, self.Rc_ = S, Rc
        return self

    def predict_pairs(self, u, i):
        num = np.einsum("nj,nj->n", self.Rc_[u], self.S_[i])
        den = np.einsum("nj,nj->n", (self.Rc_[u] != 0).astype(float), np.abs(self.S_[i]))
        return np.clip(self.base_.predict_pairs(u, i) + num / np.maximum(den, 1e-9), 1, 5)

    def score_matrix(self):
        return np.maximum(self.Rc_, 0) @ np.maximum(self.S_, 0)


class BiasMF:
    """r_hat = mu + b_u + b_i + p_u . q_i, fitted by SGD."""
    def __init__(self, k=8, lr=0.02, reg=0.05, epochs=30, seed=0):
        self.k, self.lr, self.reg, self.epochs, self.seed = k, lr, reg, epochs, seed

    def fit(self, train, n_users, n_items):
        rng = np.random.default_rng(self.seed)
        u, i, y = train["user"].to_numpy(), train["item"].to_numpy(), train["rating"].to_numpy(float)
        self.mu_ = y.mean()
        self.bu_, self.bi_ = np.zeros(n_users), np.zeros(n_items)
        self.P, self.Q = rng.normal(0, 0.1, (n_users, self.k)), rng.normal(0, 0.1, (n_items, self.k))
        for _ in range(self.epochs):
            for n in rng.permutation(len(y)):
                a, b = u[n], i[n]
                e = y[n] - (self.mu_ + self.bu_[a] + self.bi_[b] + self.P[a] @ self.Q[b])
                self.bu_[a] += self.lr * (e - self.reg * self.bu_[a])
                self.bi_[b] += self.lr * (e - self.reg * self.bi_[b])
                pa = self.P[a].copy()
                self.P[a] += self.lr * (e * self.Q[b] - self.reg * self.P[a])
                self.Q[b] += self.lr * (e * pa - self.reg * self.Q[b])
        return self

    def predict_pairs(self, u, i):
        return np.clip(self.mu_ + self.bu_[u] + self.bi_[i] + np.einsum("nk,nk->n", self.P[u], self.Q[i]), 1, 5)

    def score_matrix(self):
        return self.mu_ + self.bu_[:, None] + self.bi_[None, :] + self.P @ self.Q.T


# ---------------- evaluation ----------------
def _dcg(hits):
    return sum(h / math.log2(p + 2) for p, h in enumerate(hits))


def user_metrics(rec, relevant, k):
    hits = [1 if i in relevant else 0 for i in rec[:k]]
    n_rel = len(relevant)
    ideal = _dcg([1] * min(n_rel, k))
    return {"precision": sum(hits) / k, "recall": sum(hits) / n_rel if n_rel else 0.0,
            "ndcg": _dcg(hits) / ideal if ideal else 0.0}


def recommend(scores, seen, users, k=10):
    """Top-k unseen items per user. `seen` is a boolean (users x items) matrix of training interactions."""
    S = scores[users].copy()
    S[seen[users]] = -np.inf
    top = np.argpartition(-S, k, axis=1)[:, :k]
    return np.take_along_axis(top, np.take_along_axis(S, top, axis=1).argsort(axis=1)[:, ::-1], axis=1)


def evaluate_topn(scores, train, test, n_users, n_items, k=10, rel=4):
    seen = (to_matrix(train, n_users, n_items) > 0).toarray()
    relevant = test[test["rating"] >= rel].groupby("user")["item"].apply(set).to_dict()
    users = np.array(sorted(relevant))
    recs = recommend(scores, seen, users, k)
    per_user = pd.DataFrame([user_metrics(list(recs[n]), relevant[u], k) for n, u in enumerate(users)], index=users)
    out = per_user.mean().to_dict()
    out["coverage"] = len(np.unique(recs)) / n_items
    return out, per_user


def paired_gain_ci(per_user_model, per_user_base, column="ndcg", n_boot=3000, seed=0):
    """Bootstrap over USERS (the unit of independence) of the mean difference in a metric."""
    d = (per_user_model[column] - per_user_base[column].reindex(per_user_model.index)).to_numpy()
    idx = np.random.default_rng(seed).integers(0, len(d), (n_boot, len(d)))
    lo, hi = np.percentile(d[idx].mean(1), [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def verdict(gain):
    mean, lo, hi = gain
    word = "BEATS" if lo > 0 else ("LOSES TO" if hi < 0 else "not distinguishable from")
    return f"gain {mean:+.4f} [{lo:+.4f}, {hi:+.4f}] -> {word} popularity"


def compare(models, train, test, n_users, n_items, k=10, base="popularity"):
    fitted = {name: m.fit(train, n_users, n_items) for name, m in models.items()}
    rows, per = {}, {}
    for name, m in fitted.items():
        rows[name], per[name] = evaluate_topn(m.score_matrix(), train, test, n_users, n_items, k)
        p = m.predict_pairs(test["user"].to_numpy(), test["item"].to_numpy())
        rows[name]["rmse"] = float(np.sqrt(np.mean((p - test["rating"].to_numpy()) ** 2)))
    table = pd.DataFrame(rows).T[["rmse", "precision", "recall", "ndcg", "coverage"]]
    verdicts = {n: verdict(paired_gain_ci(per[n], per[base])) for n in models if n != base}
    return table, verdicts, fitted


# ---------------- serving ----------------
class Recommender:
    """Serve a fitted model: unseen items only, popularity for unknown users."""
    def __init__(self, model, train, n_users, n_items):
        self.scores = model.score_matrix()
        self.seen = (to_matrix(train, n_users, n_items) > 0).toarray()
        self.popularity = np.bincount(train["item"], minlength=n_items).astype(float)
        self.n_users = n_users

    def recommend(self, user, k=10):
        known = isinstance(user, (int, np.integer)) and 0 <= user < self.n_users and self.seen[user].any()
        s = self.scores[user].copy() if known else self.popularity.copy()
        if known:
            s[self.seen[user]] = -np.inf
        return [int(i) for i in np.argsort(-s)[:k]], ("personalised" if known else "popularity fallback (unknown or new user)")
''', encoding="utf-8")
print("recsys.py:", len((proj / "recsys.py").read_text(encoding="utf-8").splitlines()), "lines")
```
```text
recsys.py: 182 lines
```

### 14.3 The tests

```python run
(proj / "test_recsys.py").write_text('''import math
import numpy as np, pandas as pd, pytest
import recsys as rs

def make_df(n_users=80, n_items=40, seed=0):
    r = np.random.default_rng(seed)
    P, Q = r.normal(size=(n_users, 3)), r.normal(size=(n_items, 3))
    bu, bi = r.normal(0, 0.5, n_users), r.normal(0, 0.6, n_items)             # generous users and good movies, as in real data
    pop = np.exp(r.normal(0, 1, n_items))
    rows = []
    for u in range(n_users):
        items = r.choice(n_items, 14, replace=False, p=pop / pop.sum())
        for t, i in enumerate(items):
            rating = int(np.clip(np.round(3.3 + bu[u] + bi[i] + 0.8 * (P[u] @ Q[i]) / 1.7 + r.normal(0, 0.4)), 1, 5))
            rows.append((u, int(i), rating, t))
    return pd.DataFrame(rows, columns=["user", "item", "rating", "ts"]), n_users, n_items

def test_the_test_set_is_strictly_later_than_the_training_set():
    df, _, _ = make_df()
    train, test = rs.split_leave_last(df, 3)
    last_train = train.groupby("user")["ts"].max()
    first_test = test.groupby("user")["ts"].min()
    assert (first_test.values > last_train.reindex(first_test.index).values).all(), "every user's test ratings must come after their training ratings"
    assert not set(zip(train.user, train.item)) & set(zip(test.user, test.item)), "no (user, item) pair may be in both sets"

def test_metrics_match_a_hand_calculation():
    m = rs.user_metrics(["A", "X", "B", "Y", "Z"], {"A", "B", "C"}, 5)
    assert m["precision"] == pytest.approx(0.4) and m["recall"] == pytest.approx(2 / 3)
    expected = (1 + 1 / math.log2(4)) / (1 + 1 / math.log2(3) + 1 / math.log2(4))
    assert m["ndcg"] == pytest.approx(expected), "NDCG: discount hits by 1/log2(position+1), divide by the ideal ranking"

def test_recommendations_never_include_items_the_user_already_rated():
    df, nu, ni = make_df()
    train, _ = rs.split_leave_last(df, 3)
    model = rs.BiasModel().fit(train, nu, ni)
    reco = rs.Recommender(model, train, nu, ni)
    for u in range(nu):
        items, _ = reco.recommend(u, 10)
        assert not set(items) & set(train[train.user == u].item), f"user {u} was recommended something already rated"

def test_popularity_ranks_by_training_count():
    df, nu, ni = make_df()
    train, _ = rs.split_leave_last(df, 3)
    pop = rs.Popularity().fit(train, nu, ni)
    assert (pop.score_matrix()[0] == np.bincount(train.item, minlength=ni)).all()

def test_unknown_user_gets_the_popularity_fallback():
    df, nu, ni = make_df()
    train, _ = rs.split_leave_last(df, 3)
    reco = rs.Recommender(rs.BiasModel().fit(train, nu, ni), train, nu, ni)
    items, how = reco.recommend(10_000, 5)
    assert "popularity" in how and len(items) == 5

def test_models_never_see_the_test_ratings():
    df, nu, ni = make_df()
    train, test = rs.split_leave_last(df, 3)
    changed = df.copy()
    last = changed.sort_values(["user", "ts", "item"]).groupby("user").tail(3).index
    changed.loc[last, "rating"] = 1                                           # sabotage only the hidden ratings
    train2, _ = rs.split_leave_last(changed, 3)
    for model_cls in (rs.Popularity, rs.BiasModel, rs.ItemKNN):
        a = model_cls().fit(train, nu, ni).score_matrix()
        b = model_cls().fit(train2, nu, ni).score_matrix()
        assert np.allclose(a, b), f"{model_cls.__name__} scores changed when only hidden test ratings changed: the test set leaks into training"

def test_matrix_factorisation_is_deterministic_for_a_seed():
    df, nu, ni = make_df()
    train, _ = rs.split_leave_last(df, 3)
    a = rs.BiasMF(seed=3, epochs=3).fit(train, nu, ni).score_matrix()
    b = rs.BiasMF(seed=3, epochs=3).fit(train, nu, ni).score_matrix()
    assert np.array_equal(a, b)

def test_the_bias_model_beats_the_global_mean_on_rmse():
    df, nu, ni = make_df()
    train, test = rs.split_leave_last(df, 3)
    bias = rs.BiasModel().fit(train, nu, ni)
    rmse_bias = np.sqrt(np.mean((bias.predict_pairs(test.user.values, test.item.values) - test.rating.values) ** 2))
    rmse_mean = np.sqrt(np.mean((train.rating.mean() - test.rating.values) ** 2))
    assert rmse_bias < rmse_mean

def test_random_scores_are_not_declared_better_than_popularity():
    df, nu, ni = make_df()
    train, test = rs.split_leave_last(df, 3)
    pop = rs.Popularity().fit(train, nu, ni)
    class RandomModel:
        def fit(self, *a): return self
        def score_matrix(self): return np.random.default_rng(0).random((nu, ni))
        def predict_pairs(self, u, i): return np.full(len(u), 3.0)
    _, per_pop = rs.evaluate_topn(pop.score_matrix(), train, test, nu, ni)
    _, per_rand = rs.evaluate_topn(RandomModel().score_matrix(), train, test, nu, ni)
    assert "BEATS" not in rs.verdict(rs.paired_gain_ci(per_rand, per_pop)), "random recommendations must never be reported as beating popularity"
''', encoding="utf-8")
env = {**os.environ, "PYTHONPATH": str(proj)}
res = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore", "test_recsys.py"], cwd=proj, env=env, capture_output=True, text=True, timeout=280, encoding="utf-8")
print(res.stdout.strip()[-700:] or res.stderr.strip()[-700:])
```
```text
.........                                                                [100%]
9 passed in 0.57s
```

### 14.4 Run it on the movie data

```python run
sys.path.insert(0, str(proj))
import importlib, recsys as rs
importlib.reload(rs)

t0 = time.perf_counter()
tr_, te_ = rs.split_leave_last(ratings, 3)
table, verdicts, fitted = rs.compare({"popularity": rs.Popularity(), "bias model": rs.BiasModel(), "item-kNN": rs.ItemKNN(k=30), "matrix factorisation": rs.BiasMF(k=8, lr=0.02, epochs=30)},
                                     tr_, te_, n_users, n_items)
print(f"compared 4 models on {len(tr_)} training ratings in {time.perf_counter() - t0:.0f} s")
print(table.round(4).to_string())
print()
for name, v in verdicts.items():
    print(f"{name:22s} NDCG@10 {v}")
```
```text
compared 4 models on 16979 training ratings in 4 s
                       rmse  precision  recall   ndcg  coverage
popularity           1.0458     0.0202  0.0997 0.0562    0.1733
bias model           0.8213     0.0082  0.0396 0.0270    0.0767
item-kNN             0.7898     0.0493  0.2259 0.1508    0.7200
matrix factorisation 0.6730     0.0286  0.1318 0.0870    0.6133

bias model             NDCG@10 gain -0.0292 [-0.0430, -0.0143] -> LOSES TO popularity
item-kNN               NDCG@10 gain +0.0946 [+0.0762, +0.1129] -> BEATS popularity
matrix factorisation   NDCG@10 gain +0.0308 [+0.0138, +0.0486] -> BEATS popularity
```

### 14.5 Serve it

```python run
reco = rs.Recommender(fitted["matrix factorisation"], tr_, n_users, n_items)
u0 = 17
seen_u = set(tr_[tr_.user == u0].item)
top, how = reco.recommend(u0, 5)
print(f"user {u0}: {how}; has {len(seen_u)} rated movies. recommended:", [(i, items.loc[i, 'genre']) for i in top])
print("none already seen:", not (set(top) & seen_u))
fav = tr_[tr_.user == u0].merge(items, on="item").query("rating >= 4")["genre"].value_counts().to_dict()
print("genres the user rated 4+ in training:", fav)
top_new, how_new = reco.recommend(99999, 5)
print("an unknown user:", how_new, top_new)
```
```text
user 17: personalised; has 98 rated movies. recommended: [(174, 'Sci-Fi'), (193, 'Drama'), (232, 'Sci-Fi'), (29, 'Drama'), (274, 'Sci-Fi')]
none already seen: True
genres the user rated 4+ in training: {'Action': 25, 'Drama': 24, 'Sci-Fi': 22, 'Comedy': 1}
an unknown user: popularity fallback (unknown or new user) [3, 251, 93, 114, 225]
```

### 14.6 What to hand in

1. `recsys.py` and `test_recsys.py`, all tests passing.
2. The comparison table and the verdicts on **two datasets** (different seeds and sizes from `make_ratings`).
3. A paragraph on each model: what it adds over popularity, what it costs, where it fails (cold items and users, popularity bias).
4. The **coverage and exposure** analysis of section 13.3 for your final model, and one concrete change that would raise coverage (a re-ranking rule).
5. A one-page recommendation: which model to ship, what the offline evaluation can and cannot tell you, and the online experiment (ds.09) you would run before trusting it.

### 14.7 Extensions

1. Add `ImplicitALS` (section 13.1) as a model and evaluate it as a top-N method on a "watched" matrix.
2. Add a **content-based** model using the genres and wire it into `Recommender` as the fallback for new items and new users.
3. Add a re-ranker that limits any item to a share of the slots and report the accuracy-versus-coverage trade-off curve.
4. Replace the global time split by a **rolling** one (several cut dates) and report the spread of the NDCG gain over popularity across cuts.
5. Evaluate on **sampled negatives** (rank the test item among 100 random unseen items) and show how much that easier protocol inflates every metric and reorders the models.

## 15. Common traps

| Trap | What happens | Fix |
|---|---|---|
| Text: fitting the vectoriser (vocabulary, IDF) on all data | information from test texts leaks into features | vectoriser inside the pipeline (5, ds.04) |
| Removing "not" with a stop-word list | sentiment meaning flips | check the list; keep negations; use bigrams (2.2, 6.5) |
| A token that predicts the label only in the training period | great CV, poor deployment | read the top features; remove signatures, agent names, headers (5.4) |
| Judging a text model by accuracy only | the mistakes stay unexplained | confusion matrix, error list, slices, per-prediction explanation (6) |
| Believing an explanation without testing it | a story, not a finding | turn each hypothesis into a slice table; report null results (6.4) |
| Dense arrays for text | out of memory | sparse matrices, hashing (3.3, 7.1) |
| Hashing with too few columns | collisions hurt accuracy | enough columns; check against the vocabulary model (7.1) |
| Jumping to embeddings first | cost and opacity without knowing the gain | TF-IDF + linear baseline first (7.3) |
| Random split of ratings | the future trains the model; users in both sets | per-user, time-ordered leave-last-k (9.1) |
| Raw item average as a "best rated" list | one 5-star rating tops the list | shrink toward the global mean (10.1) |
| Skipping the popularity baseline | a "personalised" model that is not better | always report popularity, with an interval (10, 14) |
| Recommending what the user already rated | useless lists, inflated hit rates | exclude training items (9.3) |
| Bias ignored in similarities | "generous users" look like agreement | centre ratings first (11.1) |
| Similarity from two common raters | noisy neighbours | shrink by the number of co-raters (11.2) |
| Matrix factorisation without validation | overfits; training RMSE keeps falling | validation slice, regularisation, early stopping (12.2, 12.3) |
| Treating missing as dislike | the model learns exposure, not taste | confidence weighting for implicit data (13.1) |
| Ignoring cold items and users | a share of the catalogue never recommended | content-based or popularity fallback (13.2) |
| Optimising accuracy alone | popularity bias, low coverage, feedback loops | measure coverage, novelty, exposure; re-rank (13.3) |
| Trusting offline metrics as proof | exposure bias; favours the old system | offline to filter, online experiment to decide (9.4, ds.09) |

## 16. Summary

- **Text** becomes data by **tokenising**, counting (**bag of words**, a sparse matrix) and reweighting (**TF-IDF**: `tf × (ln((1+N)/(1+df)) + 1)`, rows scaled to length 1, so a dot product is a cosine similarity). Our from-scratch versions match scikit-learn exactly. **min_df** removes the typos and one-off words; **n-grams** recover a little order; **character n-grams** survive misspellings; **hashing** removes the vocabulary; **LSA** compresses.
- A **text classifier** is a pipeline: vectoriser inside, linear model or Naive Bayes as the learner. Tune the vectoriser and the model together, look at the spread, and keep a sealed test. Beware **shortcut tokens** that correlate with the label only in the training period: read the top features.
- **Explaining errors** is a method: confusion matrix and the list of mistakes; the model's top words per class; an **exact per-prediction explanation** (coefficient × TF-IDF, which sums to the decision score); **slice tables** that test each hypothesis (negation, length, typos, confidence), including null results; a fix chosen by the diagnosis (bigrams for negation) and **re-measured**; and a report with finding, evidence, cause, action and expected effect.
- **Recommenders** answer "what has this person not seen that they will like?" Families: non-personalised, content-based, collaborative (neighbourhood, factorisation), hybrid; signals: explicit ratings or implicit interactions. The data are very sparse, heavy-tailed, and **not missing at random**.
- **Evaluate** with a per-user **time split** (hide each user's last items), metrics for the task (RMSE for ratings; precision, recall, NDCG, hit rate, coverage, novelty for top-N), never recommend seen items, and remember **exposure bias**: offline accuracy is a filter, the online experiment is the test.
- **Baselines are strong.** Popularity is hard to beat for top-N; the **bias model** `μ + b_u + b_i` is the bar for RMSE. Shrink small-sample averages.
- **Item-based neighbourhoods**: centred cosine similarity with shrinkage, explainable. **Matrix factorisation** (SGD or ALS, whose closed-form solves are ridge regressions and whose objective never increases) finds latent tastes and lowers RMSE; validate, regularise, stop early. **Implicit feedback** uses confidence weighting. **Cold start** needs content or popularity fallbacks. **Popularity bias** shrinks coverage and feeds back on itself; measure it and re-rank.
- The **project** packages the recommender with a leak-proof split, one interface for the models, a serving class with fallbacks, a report with a paired bootstrap against popularity, and tests that prove the guards work.

You reached the outcome of this chapter: you can **build a text classifier with TF-IDF and explain its errors**, from per-prediction contributions to slice tests and a measured fix, and you know the shape of a recommender and how to judge one honestly. Next, ds.09 turns to experimentation and causal inference: how to run the online test that offline evaluation can only prepare for.
