import numpy as np
import pytest
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline

from solution import shuffled_label_check

rng = np.random.default_rng(0)
X = rng.normal(size=(200, 1000))
Y = rng.integers(0, 2, 200)


def honest_eval(y):
    pipe = make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=2000))
    return cross_val_score(pipe, X, y, cv=5, scoring="roc_auc").mean()


def leaky_eval(y):
    Xs = SelectKBest(f_classif, k=20).fit_transform(X, y)          # selection on ALL rows: a leak
    return cross_val_score(LogisticRegression(max_iter=2000), Xs, y, cv=5, scoring="roc_auc").mean()


def test_honest_procedure_scores_at_chance():
    m, s = shuffled_label_check(honest_eval, Y, repeats=5, seed=1)
    assert 0.38 < m < 0.62, f"mean {m:.3f}: an honest procedure on shuffled labels sits at about 0.5."


def test_leaky_procedure_is_caught():
    m, s = shuffled_label_check(leaky_eval, Y, repeats=5, seed=1)
    assert m > 0.7, f"mean {m:.3f}: selecting features on all rows finds 'signal' even in shuffled labels. Did you shuffle y before each call?"


def test_each_repeat_gets_a_new_permutation():
    seen = []

    def spy(y):
        seen.append(tuple(y))
        return 0.5

    shuffled_label_check(spy, np.arange(30), repeats=4, seed=2)
    assert len(seen) == 4, "call evaluate once per repeat."
    assert len(set(seen)) == 4, "each repeat must see a different permutation (one generator, permutation inside the loop)."
    assert all(sorted(t) == list(range(30)) for t in seen), "a permutation keeps every label once."


def test_mean_and_std():
    vals = iter([0.4, 0.6, 0.5])
    m, s = shuffled_label_check(lambda y: next(vals), np.arange(10), repeats=3, seed=0)
    assert m == pytest.approx(0.5) and s == pytest.approx(np.std([0.4, 0.6, 0.5])), "return the mean and the population std (ddof=0)."
