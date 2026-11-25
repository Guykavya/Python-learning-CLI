import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import GroupShuffleSplit

from solution import group_split


def visits(n_patients=80, per=15, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({"patient_id": np.repeat(np.arange(n_patients), per), "x": rng.normal(size=n_patients * per)})


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_no_patient_on_both_sides(seed):
    df = visits()
    tr, te = group_split(df, "patient_id", 0.25, seed)
    assert not set(df.patient_id.iloc[tr]) & set(df.patient_id.iloc[te]), "a patient must never appear in both sets."
    assert sorted(np.concatenate([tr, te]).tolist()) == list(range(len(df))), "every row in exactly one set."
    assert tr.tolist() == sorted(tr.tolist()) and te.tolist() == sorted(te.tolist()), "sorted position arrays."


def test_about_a_quarter_of_the_patients():
    df = visits()
    _, te = group_split(df, "patient_id", 0.25, 0)
    assert df.patient_id.iloc[te].nunique() == 20, "test_size is a fraction of the GROUPS: 25% of 80 patients = 20."


def test_matches_group_shuffle_split():
    df = visits(seed=3)
    tr, te = group_split(df, "patient_id", 0.3, 7)
    a, b = next(GroupShuffleSplit(1, test_size=0.3, random_state=7).split(df, groups=df["patient_id"]))
    assert np.array_equal(te, np.sort(b)), "use GroupShuffleSplit(n_splits=1, test_size=test_frac, random_state=seed)."
