import pandas as pd
import pytest

from solution import completion_by_tech, paradox


def build(groups):
    """groups: (tech, job_type, n_jobs, n_completed) -> one row per job."""
    rows = []
    for tech, job_type, n, done in groups:
        for i in range(n):
            rows.append((tech, job_type, "completed" if i < done else "failed"))
    df = pd.DataFrame(rows, columns=["tech", "job_type", "status"])
    df.insert(0, "job_id", range(1, len(df) + 1))
    return df


def simpson():
    # A: mostly hard jobs, B: mostly easy jobs.  A wins both kinds, B wins overall.
    return build([("A", "easy", 2, 2),      # A easy: 2/2   = 1.000
                  ("A", "hard", 8, 5),      # A hard: 5/8   = 0.625   -> A overall 7/10 = 0.7
                  ("B", "easy", 8, 7),      # B easy: 7/8   = 0.875
                  ("B", "hard", 2, 1)])     # B hard: 1/2   = 0.500   -> B overall 8/10 = 0.8


def test_overall_rates():
    got = completion_by_tech(simpson())["overall"]
    assert got == pytest.approx({"A": 0.7, "B": 0.8}), "overall = completed jobs / all jobs of the technician: A 7/10, B 8/10. Got %s." % got


def test_rates_by_job_type():
    got = completion_by_tech(simpson())["by_type"]
    want = {"easy": {"A": 1.0, "B": 0.875}, "hard": {"A": 0.625, "B": 0.5}}
    assert set(got) == set(want), "one entry per job type (easy, hard). Got %s." % list(got)
    for job_type, rates in want.items():
        assert got[job_type] == pytest.approx(rates), "job type %s: easy A 2/2, B 7/8; hard A 5/8, B 1/2. Got %s." % (job_type, got[job_type])


def test_the_paradox_is_detected():
    assert paradox(simpson(), "A", "B") is True, "A is better in the easy jobs AND in the hard jobs, yet B is better overall: that is the paradox."


def test_the_other_direction_is_not_a_paradox():
    assert paradox(simpson(), "B", "A") is False, "B does not win every job type, so there is no paradox for the pair (B, A)."


def test_consistent_data_is_no_paradox():
    clean = build([("A", "easy", 5, 5), ("A", "hard", 5, 4), ("B", "easy", 5, 3), ("B", "hard", 5, 2)])
    assert paradox(clean, "A", "B") is False, "A wins both types and also overall: the groups agree, there is nothing paradoxical."


def test_a_type_only_one_tech_worked_on_is_skipped_in_the_comparison():
    df = build([("A", "easy", 4, 4), ("B", "easy", 4, 2), ("A", "rare", 6, 0)])      # only A did 'rare' jobs
    out = completion_by_tech(df)
    assert out["by_type"]["rare"] == pytest.approx({"A": 0.0}), "a job type worked by one technician still appears, with only that technician."
    assert paradox(df, "A", "B") is True, (
        "the only shared type is 'easy' (A 4/4 beats B 2/4), and overall A is 4/10 against B 2/4, so A wins every shared type "
        "and loses overall. 'rare' has no partner to compare with: skip it in the 'wins every type' test.")


def test_no_shared_type_is_false():
    df = build([("A", "easy", 2, 1), ("B", "hard", 2, 2)])
    assert paradox(df, "A", "B") is False, "without a job type in common there is nothing to compare: False."


def test_returns_plain_floats_and_bool():
    out = completion_by_tech(simpson())
    assert all(type(v) is float for v in out["overall"].values()), "return plain floats."
    assert type(paradox(simpson(), "A", "B")) is bool, "paradox returns a plain bool."


def test_frame_is_not_changed():
    j = simpson()
    before = j.copy()
    completion_by_tech(j)
    paradox(j, "A", "B")
    pd.testing.assert_frame_equal(j, before)
