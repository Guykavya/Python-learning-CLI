import ast
import copy
from pathlib import Path

import solution
from solution import parse_order, price_order, process_order, validate_order

TREE = ast.parse(Path(solution.__file__).read_text())

BAD = "apple,3\n,2,1.0\nfig,0,2\nfig,x,2\nkiwi,1,-1\nkiwi,1,abc\nok,1,1"


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def test_parse_order():
    assert parse_order("a, 2 ,1\n\n b,1,0 \n") == [["a", "2", "1"], ["b", "1", "0"]], (
        "parse_order splits lines on commas, strips spaces and skips blank lines. It returns lists of strings."
    )
    assert parse_order("") == [], "Empty text: no rows."
    assert parse_order("\n\n") == [], "Only blank lines: no rows."
    assert parse_order("a,1") == [["a", "1"]], "parse_order must not judge the rows (a short row is still a row)."


def test_validate_order():
    rows = parse_order(BAD)
    assert validate_order(rows) == [
        "row 1: expected 3 fields, found 2",
        "row 2: name is empty",
        "row 3: quantity must be a whole number above 0",
        "row 4: quantity must be a whole number above 0",
        "row 5: price must be a number, 0 or more",
        "row 6: price must be a number, 0 or more",
    ], "One message per bad row, numbered from 1 among the non-blank rows."
    assert validate_order([["a", "1", "0"]]) == [], "A price of 0 is allowed."
    assert validate_order([]) == [], "No rows, no errors."
    assert validate_order([["a", "1", "2", "3"]]) == ["row 1: expected 3 fields, found 4"], "Too many fields."


def test_validate_does_not_change_rows():
    rows = parse_order(BAD)
    before = copy.deepcopy(rows)
    validate_order(rows)
    assert rows == before, "validate_order must only look at the rows, not change them."


def test_price_order():
    assert price_order([["a", "3", "0.50"], ["b", "2", "1.25"]]) == 4.0, "Sum of qty * price."
    assert price_order([["a", "2", "1.005"]]) == 2.01, "Round the total to 2 decimals."
    assert price_order([]) == 0.0, "No rows: 0.0."
    assert price_order([["x", "10", "19.99"]]) == 199.9, "10 * 19.99, rounded."


def test_process_order_results():
    assert process_order("apple,3,0.50\npear,2,1.25\n") == "OK: 2 lines, total 4.00", "Valid order: 'OK: N lines, total T'."
    assert process_order("") == "OK: 0 lines, total 0.00", "An empty order is valid."
    assert process_order("  a , 2 , 1.005 \n\nb,1,0\n") == "OK: 2 lines, total 2.01", "Spaces and blank lines are ignored."
    assert process_order("a,1,2,3") == "row 1: expected 3 fields, found 4\nINVALID: 1 problem(s)", (
        "Invalid order: the error lines, then 'INVALID: N problem(s)', joined by newlines."
    )
    assert process_order(BAD).splitlines()[-1] == "INVALID: 6 problem(s)", "The last line counts the problems."
    assert process_order(BAD).count("\n") == 6, "6 error lines plus the summary line."


def test_nothing_is_printed(capsys):
    for text in ("a,1,1", BAD, ""):
        result = process_order(text)
        assert isinstance(result, str), "process_order must RETURN the text (a str), not print it and return None."
    parse_order(BAD)
    validate_order(parse_order(BAD))
    price_order([["a", "1", "1"]])
    assert capsys.readouterr().out == "", "Nothing should be printed. Return strings; let the caller print."


def test_no_print_or_input_anywhere():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("print", "input"):
            raise AssertionError(f"{node.func.id}() found. Keep I/O out of the logic: build a string and return it.")


def test_process_order_is_thin():
    f = _func("process_order")
    length = f.end_lineno - f.lineno + 1
    assert length <= 10, f"process_order is {length} lines. It should only call the three functions and format the result (10 lines max)."
    called = {n.func.id for n in ast.walk(f) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    missing = {"parse_order", "validate_order", "price_order"} - called
    assert not missing, f"process_order must call {sorted(missing)}: it only wires the three steps together."


def test_every_function_is_short():
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef):
            length = node.end_lineno - node.lineno + 1
            assert length <= 15, f"{node.name} is {length} lines (max 15). Split it: one function, one job."
