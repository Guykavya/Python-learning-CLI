import numpy as np
import pandas as pd
import pytest

from solution import decide

OK = {"returns": (-0.4, 0.3, -1.0), "on_time": (-0.2, 0.1, -0.5)}


def test_ship():
    assert decide((0.8, 1.9), OK, 0.5) == ("ship", "the whole interval is above the minimum effect and the guardrails hold")


def test_whole_interval_below_the_minimum_effect():
    assert decide((-0.2, 0.3), OK, 0.5) == ("do not ship", "the whole interval is below the minimum effect"), "an interval that ends below the minimum effect cannot pay."


def test_interval_contains_the_minimum_effect():
    assert decide((-0.3, 2.1), OK, 0.5) == ("extend the test", "the interval contains the minimum effect"), "a point estimate of +0.9 does not decide: the interval contains 0.5."


def test_a_breached_guardrail_blocks_even_a_big_win():
    assert decide((2.0, 3.0), {"refunds": (-2.5, -1.4, -1.0), **OK}, 0.5) == ("do not ship", "guardrail refunds is below its limit"), "check guardrails first."


def test_unclear_guardrail_means_extend():
    got = decide((0.8, 1.9), {"on_time": (-0.1, 0.1, -0.5), "returns": (-1.6, 0.2, -1.0)}, 0.5)
    assert got == ("extend the test", "guardrail returns is not yet clear"), f"a guardrail interval that straddles its limit is not clear; got {got}"


def test_boundaries():
    assert decide((0.5, 0.9), {}, 0.5)[0] == "extend the test", "lo == mei is not above it."
    assert decide((0.6, 0.9), {"g": (-1.0, 0.0, -1.0)}, 0.5)[0] == "ship", "lo == limit still holds (>=)."
    assert decide((0.1, 0.5), {}, 0.5)[0] == "extend the test", "hi == mei is not below it."
