import numpy as np
import pytest
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

from solution import honest_selection_score


def leaky_selection_score(X, y, k=20):
    Xs = SelectKBest(f_classif, k=k).fit_transform(X, y)
    return cross_val_score(LogisticRegression(max_iter=2000), Xs, y, cv=5, scoring="roc_auc").mean()


def noise(seed):
    rng = np.random.default_rng(seed)
    return rng.normal(size=(200, 2000)), rng.integers(0, 2, 200)


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_pure_noise_scores_at_chance(seed):
    X, y = noise(seed)
    s = honest_selection_score(X, y, 20)
    assert 0.30 < s < 0.65, f"AUC {s:.3f} on pure noise: with selection inside the folds there is nothing to find (about 0.5). Is SelectKBest inside the Pipeline?"


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_leaky_recipe_is_far_higher(seed):
    X, y = noise(seed)
    leak = leaky_selection_score(X, y, 20)
    assert leak > 0.75, "sanity check of the test: selecting on all rows invents signal."
    assert leak - honest_selection_score(X, y, 20) > 0.2, "your score should be far below the leaky one."


def test_real_signal_is_still_found():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(300, 200))
    y = (X[:, 0] + X[:, 1] + rng.normal(size=300) > 0).astype(int)
    assert honest_selection_score(X, y, 5) > 0.8, "with two truly informative columns the honest pipeline finds them."
