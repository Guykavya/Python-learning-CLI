import ast
from pathlib import Path

import pytest

import solution
from solution import shipping_cost

# (weight_kg, zone, express, extras) -> price. Values come from the ORIGINAL function.
TABLE = [
    ((0.5, "local", False, None), 5.0),
    ((1, "local", False, None), 5.0),
    ((1.01, "local", False, None), 7.5),
    ((3, "national", False, None), 10.5),
    ((5, "national", False, None), 10.5),
    ((5.5, "national", False, None), 15.5),
    ((20, "world", False, None), 27.5),
    ((20.5, "world", False, None), 36.05),
    ((3, "national", True, None), 15.75),
    ((0.5, "world", True, None), 30.0),
    ((3, "local", False, ["fragile"]), 10.5),
    ((3, "local", False, ["fragile", "signature", "fragile"]), 12.0),
    ((3, "national", False, ["insured"]), 10.81),
    ((3, "national", True, ["insured", "fragile"]), 19.22),
    ((7, "local", True, ["insured"]), 19.31),
    ((30, "world", False, None), 36.05),
    ((2, "local", False, ["gift"]), 7.5),
    ((4, "world", True, ["signature"]), 35.25),
    ((10, "national", False, ["insured"]), 15.96),
    ((1.5, "local", True, ["insured"]), 11.59),
]


@pytest.mark.parametrize("args,expected", TABLE, ids=[str(a) for a, _ in TABLE])
def test_characterization_table(args, expected):
    weight, zone, express, extras = args
    extra_args = {} if extras is None else {"extras": list(extras)}
    got = shipping_cost(weight, zone, express, **extra_args)
    assert got == expected, (
        f"shipping_cost{args} returned {got}, the original returned {expected}. "
        "Compare with the table in the statement: check rounding, the <= boundaries and the extras."
    )


def test_rounding_is_round_not_truncate():
    assert shipping_cost(1.5, "local", True, ["insured"]) == 11.59, (
        "The exact price is 11.5875. The original ROUNDS to 2 decimals (11.59); the refactor truncated to 11.58. "
        "Use round(total, 2)."
    )


def test_weight_limits_are_inclusive():
    assert shipping_cost(1, "local") == 5.0, "A 1 kg parcel is in the first band: the limit is 'weight <= 1'."
    assert shipping_cost(5, "national") == 10.5, "Exactly 5 kg still belongs to the 5 kg band (<=, not <)."
    assert shipping_cost(20, "world") == 27.5, "Exactly 20 kg is NOT heavy, so no heavy fee and no auto insurance."


def test_callers_extras_list_is_not_modified():
    extras = ["fragile"]
    shipping_cost(30, "world", False, extras)
    assert extras == ["fragile"], (
        f"The caller's list is now {extras}. A function must not append to its argument: "
        "copy it into a new set or list first."
    )
    flags = ("signature",)
    shipping_cost(25, "local", False, flags)
    assert flags == ("signature",), "A tuple cannot be changed, so this call must not fail with AttributeError (no .append on the argument)."


def test_default_argument_is_not_shared_between_calls():
    first = shipping_cost(30, "world")
    second = shipping_cost(2, "local")
    assert second == 7.5, (
        f"A light local parcel cost {second} (expected 7.5) after a heavy parcel was priced. "
        "The default extras=[] is ONE list shared by all calls and the heavy call put 'insured' in it. Use None as the default."
    )
    assert shipping_cost(30, "world") == first, "The same heavy parcel must cost the same each time."


def test_light_calls_stay_independent_of_history():
    results = [shipping_cost(3, "national") for _ in range(3)]
    shipping_cost(25, "national")
    results.append(shipping_cost(3, "national"))
    assert results == [10.5] * 4, f"Prices changed over time: {results}. Something is remembered between calls."


def test_explicit_none_still_means_no_extras():
    assert shipping_cost(3, "national", False, None) == 10.5, "extras=None must still mean 'no extras'."


def test_unknown_zone_still_raises():
    with pytest.raises(ValueError):
        shipping_cost(1, "moon")


def _chain_length(node):
    length = 1
    while len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
        node = node.orelse[0]
        length += 1
    return length


def test_structure_is_still_table_driven():
    tree = ast.parse(Path(solution.__file__).read_text())
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "shipping_cost")
    longest = max((_chain_length(n) for n in ast.walk(fn) if isinstance(n, ast.If)), default=0)
    assert longest <= 3, (
        f"Found an if/elif chain of length {longest}. Keep the table-driven structure (RATES, WEIGHT_FEES, ...); "
        "fix the four behaviors without going back to if/elif ladders."
    )
    size = fn.end_lineno - fn.lineno + 1
    assert size <= 30, f"shipping_cost is {size} lines; the cleaned-up version was shorter. Keep it that way."
    dicts = [n for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.value, (ast.Dict, ast.List))]
    assert len(dicts) >= 3, "Keep the module-level tables (RATES, WEIGHT_FEES, FLAT_EXTRAS): that is the clean design."
