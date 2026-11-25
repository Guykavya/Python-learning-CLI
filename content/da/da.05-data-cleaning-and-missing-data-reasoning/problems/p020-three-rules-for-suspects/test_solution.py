import pandas as pd

from solution import flag_iqr, flag_mad, flag_z

TOY = [10, 11, 9, 10, 12, 11, 10, 500, 600, 550]


def where_true(flags):
    return [i for i, f in zip(flags.index.tolist(), flags.tolist()) if f]


def test_iqr_example_with_a_missing_value():
    x = pd.Series([10, 12, 11, 13, 12, 11, 50, None, -30])
    flags = flag_iqr(x)
    assert flags.tolist() == [False] * 6 + [True, False, True], (
        "quartiles of the 8 present values are 10.75 and 12.25, IQR 1.5, fences 8.5 and 14.5: only 50 and -30 are "
        "suspects, and the missing value is never flagged. Got %s." % flags.tolist())


def test_iqr_values_on_the_fence_are_not_flagged():
    x = pd.Series(range(1, 10))
    assert flag_iqr(x, k=0.5).tolist() == [False] * 9, (
        "Q1 = 3, Q3 = 7, IQR = 4, with k = 0.5 the fences are 1 and 9: the values 1 and 9 sit ON a fence, not beyond it.")
    assert flag_iqr(x, k=0.4).tolist() == [True] + [False] * 7 + [True], "with k = 0.4 the fences are 1.4 and 8.6."


def test_iqr_k_changes_the_fences():
    x = pd.Series([10, 12, 11, 13, 12, 11, 50, -30])
    assert flag_iqr(x, k=100).sum() == 0, "a huge k gives wide fences: nothing is flagged."
    assert flag_iqr(x, k=0).sum() > 2, "k = 0 uses Q1 and Q3 themselves as fences: many values are outside."


def test_z_finds_a_clear_outlier_in_a_big_sample():
    x = pd.Series([0] * 20 + [100])
    assert where_true(flag_z(x)) == [20], "z of the 100 is about 4.4 (> 3); the zeros are near 0.2."
    assert flag_z(x, t=5).sum() == 0, "with t = 5 the same value (z about 4.4) is not flagged."


def test_masking_z_misses_what_mad_finds():
    toy = pd.Series(TOY)
    assert flag_z(toy).sum() == 0, (
        "the three large values inflate the mean (172.3) and std (261.7); 600 is only 1.6 std away, so z flags nothing.")
    assert where_true(flag_mad(toy)) == [7, 8, 9], (
        "median 11, MAD 1: the robust z of 500, 600, 550 is huge, the others are small. Got %s." % where_true(flag_mad(toy)))


def test_iqr_is_also_stretched_by_many_outliers():
    assert flag_iqr(pd.Series(TOY)).sum() == 0, "Q3 is pulled up to 378 by the large values: the upper fence is 930."


def test_mad_threshold():
    toy = pd.Series(TOY)
    assert flag_mad(toy, t=1000).sum() == 0, "a huge t flags nothing."
    assert where_true(flag_mad(toy, t=1)) == [2, 7, 8, 9], (
        "with t = 1 the value 9 (robust z = 0.6745 * (9 - 11) / 1 = -1.35) is also a suspect. Got %s." % where_true(flag_mad(toy, t=1)))


def test_missing_values_are_never_flagged_and_index_is_kept():
    x = pd.Series([0.0] * 20 + [100.0, None], index=list("abcdefghijklmnopqrstuv"))
    for name, flags in (("flag_z", flag_z(x)), ("flag_iqr", flag_iqr(x, k=1.5)), ("flag_mad", flag_mad(pd.Series(TOY + [None], index=range(11))))):
        assert flags.dtype == bool, "%s must return a Boolean Series, got dtype %s." % (name, flags.dtype)
    assert flag_z(x).index.tolist() == x.index.tolist(), "keep the index of x."
    assert not flag_z(x)["v"], "the missing value must be False."
    assert where_true(flag_z(x)) == ["u"]
    m = flag_mad(pd.Series(TOY + [None]))
    assert where_true(m) == [7, 8, 9] and not m.iloc[10], "MAD ignores the missing value and never flags it."


def test_constant_column_has_no_suspects():
    c = pd.Series([7.0] * 6)
    for flags in (flag_iqr(c), flag_z(c), flag_mad(c)):
        assert flags.sum() == 0, "a constant column has no suspects. Got %s." % flags.tolist()


def test_mad_zero_flags_nothing_but_iqr_does_see_it():
    x = pd.Series([5, 5, 5, 5, 100])
    assert flag_mad(x).tolist() == [False] * 5, "MAD is 0 here (most values equal the median): the score is undefined, flag nothing."
    assert flag_iqr(x).tolist() == [False] * 4 + [True], "the IQR is 0, fences are 5 and 5: the 100 is beyond them."


def test_input_is_not_changed():
    x = pd.Series([1.0, 2.0, None, 400.0])
    before = x.copy()
    flag_iqr(x), flag_z(x), flag_mad(x)
    pd.testing.assert_series_equal(x, before)
