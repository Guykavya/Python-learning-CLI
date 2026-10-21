from solution import run_pipeline


def test_text():
    assert run_pipeline("  Hello World ", str.strip, str.lower, str.split) == ["hello", "world"]


def test_order_left_to_right():
    assert run_pipeline(3, lambda n: n + 1, lambda n: n * 10) == 40, (
        "Left to right: (3 + 1) * 10 = 40. Each step gets the previous step's result.")


def test_collect():
    assert run_pipeline(3, lambda n: n + 1, lambda n: n * 10, collect=True) == [3, 4, 40], (
        "collect=True returns every value, starting with the original.")


def test_no_steps():
    assert run_pipeline(7) == 7
    assert run_pipeline(7, collect=True) == [7]


def test_collect_is_keyword_only():
    double = lambda n: n * 2
    assert run_pipeline(1, double, double, double) == 8, (
        "All positional arguments after value are steps; collect must be keyword-only (after *steps).")
