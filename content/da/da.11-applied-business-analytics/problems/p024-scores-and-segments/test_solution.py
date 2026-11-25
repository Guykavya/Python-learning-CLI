import numpy as np
import pandas as pd
import pytest

from solution import score_quantile, segment


def test_scores_are_balanced_even_with_heavy_ties():
    f = pd.Series([1] * 80 + [2] * 10 + [3] * 6 + [4] * 3 + [9], index=range(100))
    sc = score_quantile(f)
    assert sc.value_counts().sort_index().tolist() == [20, 20, 20, 20, 20], "five equal groups of 20, although 80 customers have F = 1 (rank first breaks the ties)."
    assert sc.dtype.kind == "i" and list(sc.index) == list(range(100)), "int scores, same index."
    assert sc.iloc[-1] == 5 and sc.iloc[0] == 1, "the largest F gets 5; the first of the tied customers gets 1."


def test_small_recency_gets_the_best_score():
    r = pd.Series([3, 400, 30, 90, 200, 12, 60, 150, 5, 300], index=list("abcdefghij"))
    sc = score_quantile(r, higher_is_better=False)
    assert sc["a"] == 5 and sc["i"] == 5, "the two smallest recencies (3 and 5 days) get score 5."
    assert sc["b"] == 1 and sc["j"] == 1, "the two largest recencies get score 1."


def test_other_number_of_groups():
    sc = score_quantile(pd.Series(range(12)), n=3)
    assert sc.tolist() == [1] * 4 + [2] * 4 + [3] * 4


@pytest.mark.parametrize("r,f,label", [(5, 5, "Champions"), (4, 4, "Champions"), (4, 3, "Loyal"), (3, 3, "Loyal"), (5, 1, "New / promising"),
                                       (4, 2, "New / promising"), (2, 5, "At risk"), (1, 1, "Hibernating"), (3, 2, "Needs attention"), (3, 1, "Needs attention")])
def test_segment_rules(r, f, label):
    assert segment(r, f) == label, f"segment({r}, {f}) should be {label!r}."


def test_every_pair_gets_exactly_one_label():
    labels = {segment(r, f) for r in range(1, 6) for f in range(1, 6)}
    assert labels == {"Champions", "Loyal", "New / promising", "At risk", "Hibernating", "Needs attention"}, f"the six labels must all be used, got {labels}"
