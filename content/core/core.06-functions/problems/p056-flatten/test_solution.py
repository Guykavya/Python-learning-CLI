import copy
from solution import flatten
import ast
from pathlib import Path

SOURCE = Path(__file__).with_name("solution.py").read_text()
TREE = ast.parse(SOURCE)


def called_names():
    """Names of every plain function called in your code, e.g. {'print', 'len'}."""
    return {n.func.id for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def function_node(name):
    return next(n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == name)


def calls_itself(name):
    """True if the function with this name contains a call to itself."""
    fn = function_node(name)
    return any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == name
               for c in ast.walk(fn))


def has_loop(name):
    return any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(function_node(name)))


def test_called_twice_no_leftovers():
    first = list(flatten([1, [2]]))
    second = flatten([3])
    assert first == [1, 2] and second == [3], (
        "The second call contains items from the first. Is the result list a default argument? Create it inside.")


def test_example():
    assert flatten([1, [2, [3, 4]], 5, [[6]], []]) == [1, 2, 3, 4, 5, 6], (
        "Extend with the flattened sub-list; do not append it as one item. If the result also holds items "
        "from earlier calls, your result list is a shared mutable default.")


def test_empty_shapes():
    assert flatten([]) == []
    assert flatten([[[]]]) == []


def test_strings_and_tuples_are_items():
    assert flatten(["ab", ["cd", ("e", "f")]]) == ["ab", "cd", ("e", "f")], "Only lists are nested; keep strings and tuples whole."


def test_deep():
    data = 1
    for _ in range(50):
        data = [data]
    assert flatten(data) == [1]


def test_input_unchanged():
    data = [1, [2, [3]], [4]]
    before = copy.deepcopy(data)
    flatten(data)
    assert data == before


def test_is_recursive():
    assert calls_itself("flatten"), "flatten should call itself on nested lists."
