import pytest

from solution import pipeline


def add_one(x):
    return x + 1


def double(x):
    return x * 2


def test_left_to_right():
    assert pipeline(add_one, double)(5) == 12, "Run the FIRST step first: double(add_one(5)) = 12, not add_one(double(5)) = 11."
    assert pipeline(double, add_one)(5) == 11, "Order matters: add_one(double(5)) = 11."


def test_text_steps():
    clean = pipeline(str.strip, str.lower, str.split)
    assert clean("  Hello World ") == ["hello", "world"], "Each step gets the result of the previous one."


def test_empty_pipeline_is_identity():
    assert pipeline()(42) == 42, "No steps: give back the input. reduce with a start value handles this."
    data = [1, 2]
    assert pipeline()(data) is data, "No steps: return the very same object."


def test_one_step():
    assert pipeline(len)("abc") == 3


def test_reusable_and_nested():
    clean = pipeline(str.strip, str.split)
    count_words = pipeline(clean, len)
    assert count_words(" a b c ") == 3, "A pipeline is a function, so it can be a step of another pipeline."
    assert count_words("x y") == 2, "The pipeline must work again on a second call."
    assert clean(" p q ") == ["p", "q"], "Using clean inside count_words must not change clean."


def test_checks_steps_early():
    with pytest.raises(TypeError):
        pipeline(len, "oops")


def test_does_not_call_steps_while_building():
    calls = []

    def spy(x):
        calls.append(x)
        return x

    p = pipeline(spy, spy)
    assert calls == [], "Building the pipeline must not call any step."
    assert p(7) == 7
    assert calls == [7, 7], "Each step runs once per use."
