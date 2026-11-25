import random

import pandas as pd

from solution import best_copy


def sample():
    return pd.DataFrame({
        "id": [1, 1, 2, 2, 2, 3],
        "phone": [None, "98", "97", None, "97", None],
        "city": ["Pune", None, "Delhi", "Delhi", "Delhi", None],
        "updated_at": ["2024-01-01", "2024-02-01", "2024-01-10", "2024-03-01", "2024-02-01", "2024-01-01"],
    })


def slow_best(df, key):
    """The obvious loop: for each key, the best (filled, updated_at, position)."""
    best = {}
    for pos, (_, row) in enumerate(df.iterrows()):
        filled = int(row.notna().sum())
        score = (filled, row["updated_at"], pos)
        k = row[key]
        if k not in best or score > best[k][0]:
            best[k] = (score, df.index[pos])
    return sorted(label for _, label in best.values())


def test_example():
    out = best_copy(sample(), "id")
    assert out.index.tolist() == [1, 4, 5], (
        "id 1: tie on 3 filled cells, newer wins (row 1). id 2: rows 2 and 4 have 4 filled cells, row 4 is newer. "
        "id 3: only one row. Got %s." % out.index.tolist())


def test_more_complete_beats_newer():
    out = best_copy(sample(), "id")
    assert 3 not in out.index, "row 3 is the newest copy of id 2 but has a missing phone: completeness comes first."


def test_ties_on_everything_go_to_the_later_row():
    df = pd.DataFrame({"id": [7, 7], "x": [1, 1], "updated_at": ["2024-01-01", "2024-01-01"]})
    assert best_copy(df, "id").index.tolist() == [1], "identical completeness and date: the later row wins."


def test_original_order_labels_and_columns_are_kept():
    df = sample()
    df.index = [50, 40, 30, 20, 10, 0]
    out = best_copy(df, "id")
    assert out.index.tolist() == [40, 10, 0], "keep the original labels and row order. Got %s." % out.index.tolist()
    assert list(out.columns) == ["id", "phone", "city", "updated_at"], "the helper column must not leak into the result."


def test_one_row_per_key():
    out = best_copy(sample(), "id")
    assert out["id"].is_unique and sorted(out["id"].tolist()) == [1, 2, 3]


def test_timestamps_and_numbers_as_updated_at():
    df = pd.DataFrame({
        "k": ["a", "a"], "v": [None, None],
        "updated_at": pd.to_datetime(["2024-05-01", "2024-04-01"]),
    })
    assert best_copy(df, "k").index.tolist() == [0], "equal completeness: the later timestamp wins."
    df2 = pd.DataFrame({"k": ["a", "a"], "v": [1, None], "updated_at": [9, 10]})
    assert best_copy(df2, "k").index.tolist() == [0], "row 0 has the value; the newer row 1 has not: completeness first."


def test_agrees_with_the_slow_loop_on_random_tables():
    for seed in (1, 2, 3):
        rng = random.Random(seed)
        rows = []
        for _ in range(80):
            rows.append({
                "k": rng.randrange(12),
                "a": rng.choice([None, 1, 2]),
                "b": rng.choice([None, "x", "y"]),
                "c": rng.choice([None, 0.5]),
                "updated_at": rng.randrange(6),
            })
        df = pd.DataFrame(rows)
        df.index = [i * 3 + 1 for i in range(len(df))]
        got = best_copy(df, "k").index.tolist()
        assert got == slow_best(df, "k"), "seed %d: kept rows differ from the slow loop.\nexpected %s\ngot      %s" % (
            seed, slow_best(df, "k"), got)


def test_input_is_not_changed():
    df = sample()
    best_copy(df, "id")
    pd.testing.assert_frame_equal(df, sample(), obj="the input frame (no helper column left behind)")
