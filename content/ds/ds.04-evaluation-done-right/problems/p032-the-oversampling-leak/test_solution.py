import numpy as np
import pytest
from sklearn.tree import DecisionTreeClassifier

from conftest import make_fraud
from solution import cv_oversample_first, cv_oversample_inside, oversample


class SpyTree(DecisionTreeClassifier):
    predicted = []

    def predict_proba(self, X, check_input=True):
        SpyTree.predicted.append(len(X))
        return super().predict_proba(X, check_input)


@pytest.fixture(scope="module")
def fraud():
    f = make_fraud(20000, seed=0)
    return f.drop(columns="fraud").to_numpy(), f["fraud"].to_numpy()


def test_oversample_shape():
    X = np.arange(10).reshape(5, 2)
    y = np.array([0, 1, 0, 1, 0])
    Xo, yo = oversample(X, y, 3)
    assert len(yo) == 9 and yo.sum() == 6, "each of the 2 positives appears 3 times in total: 5 + 4 rows."
    assert np.array_equal(Xo[:5], X), "the original rows come first, unchanged."


def test_the_leak_is_far_too_good(fraud):
    X, y = fraud
    leak = cv_oversample_first(lambda: DecisionTreeClassifier(random_state=0), X, y, 20)
    honest = cv_oversample_inside(lambda: DecisionTreeClassifier(random_state=0), X, y, 20)
    assert leak > 0.9, f"oversampling before CV lets the tree recognise copies: AUC near 0.99, got {leak:.3f}."
    assert honest < 0.75, f"inside the folds the full tree has little real skill here (about 0.54), got {honest:.3f}."
    assert leak - honest > 0.25, "the gap between the two procedures is the size of the leak."


def test_validation_folds_are_never_oversampled(fraud):
    X, y = fraud
    SpyTree.predicted.clear()
    cv_oversample_inside(lambda: SpyTree(random_state=0), X, y, 20)
    assert len(SpyTree.predicted) == 5 and sum(SpyTree.predicted) == len(y), "the five validation folds together must hold exactly the original rows: oversample only the training part."


def test_the_leaky_version_validates_on_copies(fraud):
    X, y = fraud
    SpyTree.predicted.clear()
    cv_oversample_first(lambda: SpyTree(random_state=0), X, y, 20)
    assert sum(SpyTree.predicted) == len(y) + 19 * int(y.sum()), "the leaky version cross-validates the oversampled data (copies included)."
