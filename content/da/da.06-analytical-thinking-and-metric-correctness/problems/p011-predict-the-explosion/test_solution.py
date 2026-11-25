import random

import pandas as pd
import pytest

from solution import rows_after_join


def test_hand_counted_example():
    a = pd.DataFrame({"k": [1, 1, 2, 3]})            # key 1 twice, 2 once, 3 once (3 has no partner)
    b = pd.DataFrame({"k": [1, 2, 2, 2, 9]})         # key 1 once, 2 three times, 9 has no partner
    assert rows_after_join(a, b, "k") == 5, ("key 1: 2 x 1 = 2 rows; key 2: 1 x 3 = 3 rows; keys 3 and 9 have no partner. "
                                            "Total 5.")


def test_the_chapter_case_two_payments_three_lines():
    a = pd.DataFrame({"job_id": [7, 7]})
    b = pd.DataFrame({"job_id": [7, 7, 7]})
    assert rows_after_join(a, b, "job_id") == 6, "2 payments x 3 lines of the same job give 6 rows, not 5 and not 3."


def test_no_common_key_gives_zero():
    assert rows_after_join(pd.DataFrame({"k": [1, 2]}), pd.DataFrame({"k": [3]}), "k") == 0, "an inner join without a shared key has 0 rows."


def test_empty_side_gives_zero():
    assert rows_after_join(pd.DataFrame({"k": []}), pd.DataFrame({"k": [1]}), "k") == 0, "an empty table joins to nothing."


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_matches_a_real_merge_on_random_data(seed):
    rnd = random.Random(seed)
    a = pd.DataFrame({"k": [rnd.randint(0, 9) for _ in range(60)], "x": range(60)})
    b = pd.DataFrame({"k": [rnd.randint(4, 14) for _ in range(40)], "y": range(40)})
    assert rows_after_join(a, b, "k") == len(a.merge(b, on="k")), "the prediction must equal the real inner-join row count (seed %d)." % seed


def test_two_column_key():
    a = pd.DataFrame({"job_id": [1, 1, 2], "kind": ["deposit", "deposit", "full"]})      # (1, deposit) twice
    b = pd.DataFrame({"job_id": [1, 1, 2, 2], "kind": ["deposit", "balance", "full", "full"]})
    assert rows_after_join(a, b, ["job_id", "kind"]) == len(a.merge(b, on=["job_id", "kind"])) == 4, (
        "with a list of keys the PAIR must match: (1, deposit) 2 x 1, (2, full) 1 x 2 = 4.")


def test_missing_keys_match_each_other_like_pandas_does():
    a = pd.DataFrame({"k": [1.0, None]})
    b = pd.DataFrame({"k": [None, None, 1.0]})
    real = len(a.merge(b, on="k"))
    assert real == 3, "test data check: pandas joins missing keys with each other (1 + 2 rows)."
    assert rows_after_join(a, b, "k") == real, "pandas matches NaN with NaN in a merge, so count the missing keys as one more key value."


def test_it_does_not_merge(monkeypatch):
    def boom(*args, **kwargs):
        raise AssertionError("do not call merge: predict the row count from the key counts.")
    monkeypatch.setattr(pd.DataFrame, "merge", boom)
    monkeypatch.setattr(pd, "merge", boom)
    a = pd.DataFrame({"k": [1, 1]})
    b = pd.DataFrame({"k": [1]})
    assert rows_after_join(a, b, "k") == 2


def test_frames_are_not_changed():
    a = pd.DataFrame({"k": [1, 1, 2]})
    b = pd.DataFrame({"k": [1, 2, 2]})
    a0, b0 = a.copy(), b.copy()
    rows_after_join(a, b, "k")
    pd.testing.assert_frame_equal(a, a0)
    pd.testing.assert_frame_equal(b, b0)
