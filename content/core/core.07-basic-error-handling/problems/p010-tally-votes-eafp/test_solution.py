import ast
from pathlib import Path

from solution import tally

TREE = ast.parse(Path(__file__).with_name("solution.py").read_text())


def test_example():
    got = tally(["Asha", " ravi", "ASHA", "", "Meena ", "asha", "   "])
    assert got == {"asha": 3, "ravi": 1, "meena": 1}, (
        f"Got {got}. Clean with .strip().lower(), skip empty votes, count the rest.")


def test_empty_list():
    assert tally([]) == {}, "No votes: return an empty dict."


def test_only_blank_votes():
    assert tally(["", "  ", "\t"]) == {}, "Votes that are empty after strip() must be skipped."


def test_first_vote_counts_one():
    assert tally(["zoya"]) == {"zoya": 1}, "A candidate's first vote must give a count of 1, not 0."


def test_new_dict_each_call():
    tally(["a"])
    assert tally(["b"]) == {"b": 1}, "Create a new dict inside the function on every call."


def test_eafp_style():
    handlers = [n for n in ast.walk(TREE) if isinstance(n, ast.ExceptHandler)]
    assert any(h.type is not None and ast.unparse(h.type) == "KeyError" for h in handlers), (
        "Use try: counts[name] += 1 / except KeyError: counts[name] = 1.")
    methods = {n.func.attr for n in ast.walk(TREE) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "get" not in methods and "setdefault" not in methods, "This problem practises the try form: no .get or .setdefault."
    ins = [n for n in ast.walk(TREE) if isinstance(n, ast.Compare) and any(isinstance(o, (ast.In, ast.NotIn)) for o in n.ops)]
    assert not ins, "Do not test `name in counts` first: that is LBYL. Let the KeyError tell you."
