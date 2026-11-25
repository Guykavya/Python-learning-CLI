import numpy as np
import pytest
from sklearn.model_selection import GroupKFold, StratifiedKFold, TimeSeriesSplit

from solution import choose_cv


def test_types_and_split_counts():
    assert isinstance(choose_cv("groups"), GroupKFold), "'groups' -> GroupKFold."
    assert isinstance(choose_cv("time"), TimeSeriesSplit), "'time' -> TimeSeriesSplit."
    assert isinstance(choose_cv("classes"), StratifiedKFold), "'classes' -> StratifiedKFold."
    assert choose_cv("groups", 3).get_n_splits() == 3 and choose_cv("time", 4).get_n_splits() == 4, "n_splits must be passed on."


def test_no_group_on_both_sides():
    rng = np.random.default_rng(0)
    groups = np.repeat(np.arange(20), 5)                 # 20 people, 5 rows each
    X = rng.normal(size=(100, 2))
    y = rng.integers(0, 2, 100)
    for train, test in choose_cv("groups").split(X, y, groups):
        assert not set(groups[train]) & set(groups[test]), "a person (group) must never appear in both the training and the validation rows."


def test_time_folds_never_train_on_the_future():
    X = np.arange(60).reshape(-1, 1)
    folds = list(choose_cv("time").split(X))
    assert len(folds) == 5, "five time-ordered splits."
    for train, test in folds:
        assert train.max() < test.min(), "every training index must come before every test index."


def test_stratified_folds_keep_the_class_share():
    rng = np.random.default_rng(1)
    y = (rng.random(500) < 0.1).astype(int)              # 10% positives
    X = rng.normal(size=(500, 2))
    for train, test in choose_cv("classes").split(X, y):
        assert abs(y[test].mean() - y.mean()) < 0.02, "each validation fold should hold about the overall share of positives."


def test_unknown_kind():
    with pytest.raises(ValueError):
        choose_cv("random")
