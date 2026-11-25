import numpy as np
import pytest
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score

from solution import tune_and_report

ALPHAS = np.logspace(-3, 3, 13)


def gen(seed, n=40, k=20):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(2 * n, k))
    b = np.zeros(k)
    b[:5] = 1
    y = X @ b + 3 * rng.normal(size=2 * n)
    return X[:n], y[:n], X[n:], y[n:]


@pytest.mark.parametrize("seed", [0, 1, 3, 4])
def test_alpha_is_chosen_by_cross_validation_on_train_only(seed):
    Xa, ya, Xb, yb = gen(seed)
    cv = [np.mean(cross_val_score(Ridge(alpha=a), Xa, ya, cv=5)) for a in ALPHAS]
    expected_alpha = ALPHAS[int(np.argmax(cv))]
    test_scores = [Ridge(alpha=a).fit(Xa, ya).score(Xb, yb) for a in ALPHAS]
    assert ALPHAS[int(np.argmax(test_scores))] != expected_alpha, "test-data sanity check: the leaky choice differs from the CV choice on this data."
    alpha, score = tune_and_report(Xa, ya, Xb, yb, ALPHAS)
    assert alpha == pytest.approx(expected_alpha), f"alpha {alpha:.3g} was not chosen by 5-fold cross-validation on the TRAINING rows (expected {expected_alpha:.3g})."


@pytest.mark.parametrize("seed", [0, 1, 3, 4])
def test_reported_score_is_the_honest_single_test_score(seed):
    Xa, ya, Xb, yb = gen(seed)
    alpha, score = tune_and_report(Xa, ya, Xb, yb, ALPHAS)
    honest = Ridge(alpha=alpha).fit(Xa, ya).score(Xb, yb)
    assert score == pytest.approx(honest, rel=1e-9), "report the test R2 of the model refitted on the training set with the chosen alpha."
    best_possible = max(Ridge(alpha=a).fit(Xa, ya).score(Xb, yb) for a in ALPHAS)
    assert score < best_possible - 1e-6, "the honest score is below the best-of-13 test score: if they are equal you are still selecting on the test set."


def test_changing_the_test_labels_cannot_change_the_chosen_alpha():
    Xa, ya, Xb, yb = gen(0)
    a1, _ = tune_and_report(Xa, ya, Xb, yb, ALPHAS)
    a2, _ = tune_and_report(Xa, ya, Xb, -yb, ALPHAS)
    assert a1 == a2, "the test set must not influence the choice of alpha."
