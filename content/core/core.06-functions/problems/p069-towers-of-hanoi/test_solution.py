import pytest
from solution import hanoi
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


def simulate(n, moves, source="A", target="C", spare="B"):
    pegs = {source: list(range(n, 0, -1)), target: [], spare: []}
    for i, (a, b) in enumerate(moves):
        assert pegs[a], f"Move {i + 1} {a}->{b} takes a disc from an empty peg."
        disc = pegs[a].pop()
        assert not pegs[b] or pegs[b][-1] > disc, (
            f"Move {i + 1} {a}->{b} puts disc {disc} on the smaller disc {pegs[b][-1]}.")
        pegs[b].append(disc)
    return pegs


def test_small():
    assert hanoi(0) == [], "Zero discs need no moves: that is the base case."
    assert hanoi(1) == [("A", "C")]
    assert hanoi(2) == [("A", "B"), ("A", "C"), ("B", "C")]


def test_custom_pegs():
    assert hanoi(2, source="X", target="Y", spare="Z") == [("X", "Z"), ("X", "Y"), ("Z", "Y")]


@pytest.mark.parametrize("n", [3, 5, 10])
def test_legal_and_minimal(n):
    moves = hanoi(n)
    assert len(moves) == 2 ** n - 1, f"{n} discs need exactly {2 ** n - 1} moves; got {len(moves)}."
    pegs = simulate(n, moves)
    assert pegs["C"] == list(range(n, 0, -1)), "At the end every disc must be on the target peg, in order."


def test_called_twice():
    first = hanoi(2)
    second = hanoi(1)
    assert second == [("A", "C")] and len(first) == 3, "Each call must build its own list of moves."


def test_recursive():
    assert calls_itself("hanoi")
