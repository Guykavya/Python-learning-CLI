from solution import call_all, CHECKS, describe


def test_call_all():
    assert call_all([abs, str], -4) == [4, "-4"], "Call EACH function on the same value, in order."


def test_empty():
    assert call_all([], 10) == []


def test_same_value_each_time():
    seen = []
    def a(x):
        seen.append(x)
        return x + 1
    call_all([a, a, a], 1)
    assert seen == [1, 1, 1], "Each function gets the original value, not the previous result."


def test_checks_holds_functions():
    assert CHECKS == [len, str.upper, str.isdigit], (
        "CHECKS should hold the functions themselves: [len, str.upper, str.isdigit].")


def test_describe():
    assert describe("abc") == [3, "ABC", False]
    assert describe("2026") == [4, "2026", True]
