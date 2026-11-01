import ast

import pytest

from solution import ConstantFolder, fold


def same_code(a, b):
    """Compare two pieces of source by their syntax trees (spacing and quotes do not matter)."""
    return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))


def test_simple_fold():
    source, folds = fold("x = 24 * 60 * 60")
    assert same_code(source, "x = 86400"), f"24 * 60 * 60 should become 86400, got {source!r}."
    assert folds == 2, "Two BinOp nodes were folded: (24 * 60) first, then (1440 * 60)."


def test_returns_source_text():
    source, _ = fold("y = 2 + 3")
    assert isinstance(source, str) and "5" in source, "fold returns ast.unparse(new_tree): a string of Python code."


def test_bottom_up():
    source, folds = fold("z = (1 + 2) * (3 + 4)")
    assert same_code(source, "z = 21"), (
        "Visit the children first (self.generic_visit(node)), then fold the node: the inner sums become "
        "literals, and only then is the multiplication foldable."
    )
    assert folds == 3


def test_left_associativity():
    assert same_code(fold("v = 1 + 2 + x")[0], "v = 3 + x"), "1 + 2 + x is (1 + 2) + x: the left part folds."
    source, folds = fold("u = x + 1 + 2")
    assert same_code(source, "u = x + 1 + 2") and folds == 0, (
        "x + 1 + 2 is (x + 1) + 2: no BinOp has two literals, so nothing folds. (Rewriting it as x + 3 would "
        "change the meaning if x were, say, a string with a custom __add__.)"
    )


@pytest.mark.parametrize("source, why", [
    ("w = x * 2 + 3", "a name is not a literal"),
    ("t = 'a' + 'b'", "only numbers are folded, not strings"),
    ("s = True + 1", "bool is a subclass of int, but True is not a number literal here: check type(), not isinstance()"),
    ("q = 7 / 2", "/ is not one of + - *"),
    ("p = 2 ** 10", "** is not one of + - *"),
    ("r = 7 // 2", "// is not one of + - *"),
    ("m = 7 % 2", "% is not one of + - *"),
    ("n = f(2) + 3", "a call is not a literal"),
])
def test_left_alone(source, why):
    new, folds = fold(source)
    assert same_code(new, source) and folds == 0, f"{source!r} must not change: {why}."


def test_negative_literals_are_numbers():
    assert same_code(fold("z = 2 * -3 + x")[0], "z = -6 + x"), (
        "The parser writes -3 as UnaryOp(USub, Constant(3)). Treat that as the number -3 when it is an operand."
    )


def test_negative_result_keeps_precedence():
    source, _ = fold("y = (1 - 4) ** 2")
    namespace = {}
    exec(source, namespace)
    assert namespace["y"] == 9, (
        f"Got {source!r}, which computes {namespace['y']}. If you return ast.Constant(-3), ast.unparse writes "
        "'-3 ** 2', which Python reads as -(3 ** 2). Build a negative result as UnaryOp(USub, Constant(3)), "
        "the same shape the parser uses."
    )
    assert same_code(source, "y = (-3) ** 2")


def test_folds_inside_any_node():
    source = "def f(n):\n    return n * (60 * 60)\nitems = [1 + 1, 2 * 3]\nprint(10 - 3 - 2)\no = 2 ** (1 - 3)"
    expected = "def f(n):\n    return n * 3600\nitems = [2, 6]\nprint(5)\no = 2 ** -2"
    new, folds = fold(source)
    assert same_code(new, expected), (
        "NodeTransformer visits the whole tree: folds happen inside functions, lists, calls and the operands "
        f"of other operators. Got:\n{new}"
    )
    assert folds == 6, "60 * 60, 1 + 1, 2 * 3, (10 - 3) and then 7 - 2, and 1 - 3: six folds."


def test_floats():
    source, _ = fold("r = 0.5 * 4 - 0.25")
    namespace = {}
    exec(source, namespace)
    assert namespace["r"] == 1.75 and same_code(source, "r = 1.75"), "Floats are numbers too."


@pytest.mark.parametrize("expr", [
    "1 + 2 * 3 - 4", "(1 - 10) * (2 - 3)", "x - (2 - 5)", "(2 - 5) * x", "-(2 * 3) + x",
    "2 - -3 * 4", "(3 - 7) ** 2 + x", "x ** (1 - 3)", "1.5 * 2 - 10",
])
def test_meaning_is_unchanged(expr):
    folded, _ = fold(expr)
    env = {"x": 7}
    assert eval(folded, dict(env)) == eval(expr, dict(env)), (
        f"Folding must never change the result: {expr!r} became {folded!r}."
    )


def test_counter_on_the_transformer():
    folder = ConstantFolder()
    assert folder.folds == 0, "A new ConstantFolder starts with folds = 0."
    tree = folder.visit(ast.parse("a = 1 + 1\nb = c + 1"))
    assert folder.folds == 1, "Count one fold per BinOp you replace."
    assert isinstance(tree, ast.Module), "visit() on the Module returns the (changed) Module."
