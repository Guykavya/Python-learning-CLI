from solution import all_constants, is_folded

NESTED = """
def seconds_per_week():
    return 7 * 86400

class Pricing:
    def tax(self, amount):
        return amount * (0.25 * 0.5)

square_feet = lambda m: m * 10.7639
"""


def test_arithmetic_on_literals_is_folded():
    assert is_folded("24 * 60 * 60", 86400) is True, "24 * 60 * 60 is computed at compile time: 86400 is a constant."
    assert is_folded("1.5 * 4", 6.0) is True, "Float arithmetic on literals is folded too."
    assert is_folded("60 * 60 * x", 3600) is True, "(60 * 60) * x: the literal part on the left is folded first."


def test_strings_are_folded():
    assert is_folded('"py" + "thon"', "python") is True, "Adding two string literals is folded."
    assert is_folded('"ab" * 3', "ababab") is True, "Repeating a short string literal is folded."


def test_tuple_and_membership_constants():
    assert is_folded("(1, 2, 3)", (1, 2, 3)) is True, "A tuple of literals becomes a single tuple constant."
    assert is_folded("x in [1, 2, 3]", (1, 2, 3)) is True, "After 'in', a list of literals becomes a constant tuple."
    assert is_folded("x in {1, 2, 3}", frozenset({1, 2, 3})) is True, "After 'in', a set of literals becomes a frozenset constant."


def test_names_and_calls_are_not_folded():
    assert is_folded("len('abcd') * 1000", 4000) is False, "A call is never run at compile time, so 4000 is not a constant."
    assert is_folded("x * 60 * 60", 3600) is False, "(x * 60) * 60 has x on the left, so 60 * 60 is never computed alone."


def test_type_must_match():
    assert is_folded("2.0 * 500", 1000.0) is True, "2.0 * 500 folds to the float 1000.0."
    assert is_folded("2.0 * 500", 1000) is False, (
        "1000.0 == 1000 is True, but the constant is a float. Compare type(const) is type(value) as well as ==."
    )


def test_all_constants_top_level():
    consts = all_constants("rate = 0.18\nname = 'shop'\n")
    assert isinstance(consts, list), "all_constants must return a list."
    assert 0.18 in consts and "shop" in consts, "Top-level literals are in the module's co_consts."


def test_all_constants_finds_nested_code():
    consts = all_constants(NESTED)
    assert 604800 in consts, "7 * 86400 is folded inside seconds_per_week's own code object: look inside nested code objects."
    assert 0.125 in consts, "(0.25 * 0.5) is folded inside Pricing.tax, two levels deep (class body, then method): search recursively."
    assert 10.7639 in consts, "A lambda has its own code object in co_consts too."


def test_code_objects_not_included():
    consts = all_constants(NESTED)
    assert not any(type(c).__name__ == "code" for c in consts), (
        "Do not put code objects in the result; open them and collect their constants instead."
    )


def test_eval_mode_is_used():
    assert is_folded("100 * 1000", 100000) is True, "Compile expr in 'eval' mode."
