from learn import model


def test_clean_solve_is_full_quality():
    assert model.quality(0, 0, False) == 1.0


def test_hints_and_failures_lower_quality():
    assert model.quality(2, 0, False) < model.quality(1, 0, False) < 1.0
    assert model.quality(0, 3, False) < 1.0


def test_viewing_solution_caps_quality():
    assert model.quality(0, 0, True) == model.SOLUTION_CAP


def test_quality_never_below_minimum():
    assert model.quality(20, 20, False) == model.MIN_QUALITY


def test_intervals_grow_on_good_reviews_and_reset_on_bad():
    first = model.next_interval(None, 1.0, False)
    second = model.next_interval(first, 1.0, True)
    assert second > first
    assert model.next_interval(second, 0.4, True) == 2.0
    assert model.next_interval(None, 0.2, False) == 1.0


def test_beating_a_hard_problem_raises_rating_more():
    easy_gain = model.update_ratings(1000, 600, 1.0)[0] - 1000
    hard_gain = model.update_ratings(1000, 1400, 1.0)[0] - 1000
    assert hard_gain > easy_gain > 0


def test_mastery_needs_coverage_quality_and_assessments():
    p = model.ModuleProgress(10, 8, 0.9, {"explain"}, {"explain", "build"})
    assert not p.mastered
    p.assessments_done.add("build")
    assert p.mastered
    assert model.ModuleProgress(0, 0, 0, set(), set()).status == "no-content"
