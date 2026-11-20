# Problem plan: ds.08 Other special data: text and recommenders (30 problems)

Rules: [README.md](README.md) (shared rules, R1–R5) and [dsa.07-problem-plan.md](dsa.07-problem-plan.md) (table format).
Function style (`from solution import f`). Ids `ds.08.p001` … `p030`, folder `pNNN-slug`. Requires ds.05. Libraries: NumPy, pandas,
SciPy (sparse), scikit-learn. **NLTK, spaCy, gensim, Surprise are not installed**; no corpus downloads.

**Mix:** 10 drill, 10 applied, 7 deep, 3 challenge. **Kinds:** 21 code, 6 trace, 3 explain.
**assessment:** explain = p014, trace = p006, fix = p012, build = p030.
**★ core set (write first, 12):** 1, 4, 6, 7, 10, 12, 14, 18, 20, 23, 26, 30. Outcome (TF-IDF classifier and explain its errors):
p10–p15.

**Testing notes**
- Data: the chapter's generators in `conftest.py`: `make_tickets(n, seed, agent_shortcut)` and `make_reviews(n, seed)` (synthetic
  support tickets and reviews with typos, negation and a planted shortcut), `make_ratings(n_users, n_items, seed)` (ratings from hidden
  tastes). Small sizes: ≤ 1,200 documents, ≤ 300 users × 150 items, so every file stays ≤ ~15 s.
- From-scratch text features match scikit-learn **exactly** (`CountVectorizer(token_pattern=..., lowercase=True)` with the same tokeniser,
  `TfidfTransformer(smooth_idf=True, sublinear_tf=...)`, L2 norm) — compare dense arrays with `atol=1e-12` and vocabularies as dicts.
- Recommenders are checked against **slow obvious versions** (nested loops over a tiny matrix) and against properties (no already-seen
  items recommended, top-N length, metrics in [0, 1]); matrix factorisation by loss decrease and by beating the bias model on held-out
  RMSE on 2 seeds (margins measured by the author), never by fixed numbers (R3).
- Evaluation split is per user, by time: `split_leave_last(df, k)`; the test checks no user's test rating is earlier than their train ratings.

## A. Text to tokens to vectors (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Tokenise | drill | code | `tokenize(text)` lower-cases and keeps `[a-z0-9']+` tokens, as §2.1; punctuation, digits, apostrophes, empty string |
| 2 | A crude stemmer | drill | trace | `⚠ HAND-TRACE` given `crude_stem` (the chapter suffix list, §2.2), print the stem of 8 words (`running`, `studies`, `cats`, `is`, `happily` …); the solution shows two words the stemmer merges wrongly
| 3 | Word and character n-grams | drill | trace | `⚠ HAND-TRACE` print the word bigrams of `"not good at all"` and the character 3-grams (with `analyzer="char_wb"` boundary spaces) of `"cat"` |
| 4 | Bag of words from scratch | applied | code | `bow_scratch(docs)` returns `(vocab, sparse count matrix)`; equals `CountVectorizer` with the same token pattern (vocab and matrix) |
| 5 | Zipf's law, measured | deep | code | `zipf_slope(docs)` fits log(frequency) on log(rank) for the top 200 words; slope between −1.3 and −0.7 on the reviews; a uniform random text gives a flatter slope |

## B. TF-IDF and search (Ch. 4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 6 | Trace TF-IDF by hand | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` three 3-word documents: print the smoothed idf of each word and the L2-normalised tf-idf row of document 1, to 3 decimals |
| 7 | TF-IDF from scratch | applied | code | `tfidf_scratch(count_matrix, smooth, sublinear)`; equals `TfidfTransformer` for all four switch combinations |
| 8 | Cosine search | applied | code | `search(query, docs, k)` returns the top-k document indices by cosine similarity of TF-IDF vectors; an exact duplicate ranks first; query words not in the vocabulary are ignored |
| 9 | Sparse memory | applied | explain | why the TF-IDF matrix must stay sparse: estimate the dense size of 100,000 documents × 50,000 words in float64 against a CSR matrix with 60 non-zeros per row (worked numbers), and name the operations that silently densify (`.toarray()`, centring, `StandardScaler()` without `with_mean=False`); checklist

## C. A text classifier and its errors (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 10 | Baseline first, then TF-IDF + linear model | applied | code | `ticket_classifier()` returns a pipeline (`TfidfVectorizer` + `LogisticRegression`); CV macro-F1 beats `DummyClassifier` by a clear margin |
| 11 | Tune text step and model together | applied | code | `tune_text(X, y)` with a grid over `ngram_range` and `C` (≤ 8 candidates, 3 folds); best pipeline refits |
| 12 | Fix the shortcut classifier | applied | code | `assessment = "fix"`; given a classifier trained on tickets whose agent signature leaks the label (`agent_shortcut=True`); fix: `strip_signature` inside the pipeline; tests: accuracy on a test set **without** the signature recovers (band), and the top words no longer contain agent names |
| 13 | Top words per class | drill | code | `top_words(pipe, k)` reads the coefficients with feature names; returns a dict class → k words; the planted keywords appear |
| 14 | Explain the classifier's mistakes | deep | explain | `assessment = "explain"`; the outcome: from a printed confusion matrix, a list of 6 mistakes and `explain(pipe, text)` output (in `problem.md`), explain the two main error causes (negation, typos/unknown words) and what you would change; checklist |
| 15 | Explain one prediction exactly | deep | code | `explain(pipe, text, k)` returns the k words with the largest contribution (tf-idf × coefficient) to the predicted class; contributions + intercept equal the decision function (exact) |
| 16 | Negation | challenge | code | `negation_features(text)` marks words after "not"/"never" until punctuation (`not_good`); with it, accuracy on negated reviews improves over plain unigrams (re-measured with the same folds) |

## D. Beyond bag of words (Ch. 7)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 17 | Hashing trick | drill | trace | `⚠ HAND-TRACE` given a fixed toy hash (sum of character codes mod 8, inline), print the bucket of 6 words and which ones collide |
| 18 | Latent semantic analysis | deep | code | `lsa(X, k, seed)` with `TruncatedSVD`; two documents that share no word but share topic words' neighbours become more similar in LSA space than in TF-IDF space |

## E. Recommenders: data, split, metrics (Ch. 8–9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 19 | Split by time per user | drill | code | `split_leave_last(df, k)` holds out each user's last k ratings by timestamp; users with ≤ k ratings stay in train |
| 20 | Precision, recall and NDCG at k | drill | code | `user_metrics(rec, relevant, k)` with `dcg`; perfect ranking → NDCG 1; inline hand-computed cases |
| 21 | Trace NDCG | drill | trace | `⚠ HAND-TRACE` hits `[1, 0, 1, 0, 0]` with 2 relevant items: print DCG, ideal DCG and NDCG to 3 decimals |
| 22 | Offline evaluation is biased | applied | explain | why held-out ratings over-reward popular items (missing not at random) and what an evaluation can do about it; checklist |

## F. Baselines, neighbours, factorisation (Ch. 10–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 23 | Popularity top-N | drill | code | `Popularity().fit(train).recommend(users, k)` never returns already-seen items; ties broken by item id |
| 24 | The bias model | applied | code | `BiasModel(reg)` with global mean + shrunk user and item biases (`shrunk_mean(C)`); RMSE beats the global mean on the test split |
| 25 | Item-kNN with shrinkage | applied | code | `ItemKNN(k, shrinkage)` with cosine item similarities shrunk by `n/(n + shrinkage)`; equals a slow loop implementation on a 6×5 matrix; no seen items recommended |
| 26 | Matrix factorisation by SGD | deep | code | `MF_SGD(k, lr, reg, epochs, seed)` on residuals of the bias model; training loss decreases every epoch; held-out RMSE beats the bias model on 2 seeds |
| 27 | ALS in closed form | challenge | code | `als_fit(df, base, k, lam, iters, seed)`; each half-step solves ridge problems exactly (check one user vector against `np.linalg.solve`); loss never increases |
| 28 | Cold start and popularity bias | deep | trace | `⚠ HAND-TRACE` given recommendation lists for 4 users (inline), print catalogue coverage and the `gini` of item exposure, to 3 decimals |

## G. Project (Ch. 13–14)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 29 | Implicit feedback evaluation | deep | code | `hit_rate_at_k(scores, test, k)` for implicit data and `cold_hit_rate` (§13.2) for users with ≤ 3 train items; checked on tiny inline matrices |
| 30 | The movie recommender library | challenge | code | `assessment = "build"`; the §14 library: `Popularity`, `BiasModel`, `ItemKNN`, `BiasMF` with a shared `fit/recommend/predict` interface plus `evaluate(models, train, test, k)` returning a table of RMSE, precision@k, NDCG@k and coverage; tests: interface, no seen items, the ordering bias < popularity on RMSE, MF ≥ bias on NDCG on 2 seeds |

## Counts check

Tiers: drill 10 (1, 2, 3, 6, 13, 17, 19, 20, 21, 23), applied 10 (4, 7, 8, 9, 10, 11, 12, 22, 24, 25),
deep 7 (5, 14, 15, 18, 26, 28, 29), challenge 3 (16, 27, 30).
Kinds: trace 6 (2, 3, 6, 17, 21, 28), explain 3 (9, 14, 22), code 21.
Assessment: explain p014, trace p006, fix p012, build p030 — exactly one each.

## Risks and open questions

- `CountVectorizer`'s default token pattern drops 1-character tokens; p004's `problem.md` must give the exact pattern used by both sides.
- `make_tickets(agent_shortcut=...)` signature: copy from the chapter (§1.3) exactly; p012 depends on it.
- MF results vary with seeds; margins in p026/p030 must be measured on the reference with 3 seeds.
