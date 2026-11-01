import ast
import builtins
import dataclasses
import io
from datetime import date
from pathlib import Path

import pytest

import solution
from solution import COMMANDS, Record, build_report, main, parse_records, register_command

TODAY = date(2025, 6, 15)

DATA_A = 'sku,name,qty,price,expires\nA100,Widget,40,2.50,2025-12-01\nB200,Gadget,3,19.99,\nC300,Gizmo Pro,0,120.00,2025-01-31\nD400,widget deluxe,12,7.25,2025-06-15\nE500,Cable,5,1.10,2025-06-14\nthis line is broken\nF600,Bolt,x,0.10,\nG700,Nut,100,0.05,2025-13-45\n\nH800,Spring,8,3.00,2025-06-16\nJ900,Lamp,2,30.00,\n'
DATA_B = 'sku,name,qty,price,expires\n'
FILES = {"a.csv": DATA_A, "b.csv": DATA_B}

# (file, command lines typed, lines that must be written). Expected output = real output of the legacy script.
SCRIPTS = [
    ('A', ['list', 'quit'],
     ['loaded 7 records', 'skipped 3 bad line(s): 7, 8, 9', 'A100   Widget         40     2.50', 'B200   Gadget          3    19.99', 'C300   Gizmo Pro       0   120.00', 'D400   widget deluxe   12     7.25', 'E500   Cable           5     1.10', 'H800   Spring          8     3.00', 'J900   Lamp            2    30.00', 'bye']),
    ('A', ['low', 'low 10', 'low x', 'low 0', 'low 3 4'],
     ['loaded 7 records', 'skipped 3 bad line(s): 7, 8, 9', 'C300   Gizmo Pro       0   120.00', 'J900   Lamp            2    30.00', 'B200   Gadget          3    19.99', 'C300   Gizmo Pro       0   120.00', 'J900   Lamp            2    30.00', 'B200   Gadget          3    19.99', 'E500   Cable           5     1.10', 'H800   Spring          8     3.00', 'error: low needs a whole number', 'nothing low on stock', 'C300   Gizmo Pro       0   120.00', 'J900   Lamp            2    30.00']),
    ('A', ['expired', 'quit'],
     ['loaded 7 records', 'skipped 3 bad line(s): 7, 8, 9', 'C300   Gizmo Pro    expired 2025-01-31', 'E500   Cable        expired 2025-06-14', 'bye']),
    ('A', ['value', 'find gad', 'find WIDGET', 'find   ', 'find zzz', 'find pro'],
     ['loaded 7 records', 'skipped 3 bad line(s): 7, 8, 9', 'total value: 336.47', 'B200   Gadget          3    19.99', 'A100   Widget         40     2.50', 'D400   widget deluxe   12     7.25', 'error: find needs some text', 'no match', 'C300   Gizmo Pro       0   120.00']),
    ('A', ['report'],
     ['loaded 7 records', 'skipped 3 bad line(s): 7, 8, 9', 'INVENTORY REPORT 2025-06-15', 'items: 7  units: 70  value: 336.47', 'low stock (<5): B200, C300, J900', 'expired: C300, E500', 'most valuable: A100 Widget (100.00)']),
    ('A', ['help', 'bogus', 'LIST', '  low 1  ', '', 'Exit', 'list'],
     ['loaded 7 records', 'skipped 3 bad line(s): 7, 8, 9', 'commands: expired, find, help, list, low, quit, report, value', 'unknown command: bogus (try help)', 'A100   Widget         40     2.50', 'B200   Gadget          3    19.99', 'C300   Gizmo Pro       0   120.00', 'D400   widget deluxe   12     7.25', 'E500   Cable           5     1.10', 'H800   Spring          8     3.00', 'J900   Lamp            2    30.00', 'C300   Gizmo Pro       0   120.00', 'bye']),
    ('B', ['list', 'low', 'expired', 'value', 'report', 'find a'],
     ['loaded 0 records', 'no records', 'nothing low on stock', 'nothing expired', 'total value: 0.00', 'INVENTORY REPORT 2025-06-15', 'items: 0  units: 0  value: 0.00', 'low stock (<5): none', 'expired: none', 'most valuable: none', 'no match']),
    ('A', ['quit', 'list'],
     ['loaded 7 records', 'skipped 3 bad line(s): 7, 8, 9', 'bye']),
]
MISSING_FILE_OUTPUT = ['error: cannot open nofile.csv']

RECORDS_A = [
    Record("A100", "Widget", 40, 2.5, date(2025, 12, 1)),
    Record("B200", "Gadget", 3, 19.99, None),
    Record("C300", "Gizmo Pro", 0, 120.0, date(2025, 1, 31)),
    Record("D400", "widget deluxe", 12, 7.25, date(2025, 6, 15)),
    Record("E500", "Cable", 5, 1.1, date(2025, 6, 14)),
    Record("H800", "Spring", 8, 3.0, date(2025, 6, 16)),
    Record("J900", "Lamp", 2, 30.0, None),
]


class Session:
    """Fake read/write/opener. Nothing real is touched."""

    def __init__(self, filename, lines, today=TODAY):
        self.filename, self.lines, self.today = filename, list(lines), today
        self.written, self.prompts, self.opened = [], [], []

    def read(self, prompt=""):
        self.prompts.append(prompt)
        if not self.lines:
            raise EOFError
        return self.lines.pop(0)

    def write(self, text=""):
        self.written.append(text)

    def opener(self, path, *args, **kwargs):
        self.opened.append(path)
        if path not in FILES:
            raise FileNotFoundError(path)
        return io.StringIO(FILES[path])

    def run(self):
        code = main([self.filename], read=self.read, write=self.write, today=lambda: self.today, opener=self.opener)
        return code


@pytest.fixture
def no_real_io(monkeypatch):
    def forbidden(name):
        def fail(*args, **kwargs):
            raise AssertionError(
                f"The code called the real {name}(). Only main may touch the outside world, and even main must use "
                "the read/write/opener it was given."
            )
        return fail

    for name in ("input", "open", "print"):
        monkeypatch.setattr(builtins, name, forbidden(name))


# ---- the pure core -----------------------------------------------------------

def test_record_is_a_dataclass():
    assert dataclasses.is_dataclass(Record), "Record must be a dataclass (@dataclass)."
    names = [f.name for f in dataclasses.fields(Record)]
    assert names[:5] == ["sku", "name", "qty", "price", "expires"], f"Record fields are {names}; expected sku, name, qty, price, expires."
    assert Record("A", "n", 1, 2.0, None) == Record("A", "n", 1, 2.0, None), "Dataclass records with equal fields must be equal."


def test_parse_records_returns_records_and_bad_line_numbers(no_real_io):
    records, bad = parse_records(DATA_A)
    assert records == RECORDS_A, f"Parsed records differ: {records}"
    assert bad == [7, 8, 9], f"Bad line numbers must be 1-based file lines, expected [7, 8, 9], got {bad}."


def test_parse_records_edge_cases(no_real_io):
    assert parse_records("") == ([], []), "Empty text has no records and no bad lines."
    assert parse_records("sku,name,qty,price,expires\n") == ([], []), "A header line is skipped."
    records, bad = parse_records("X1, Nut ,2, 0.5 , 2025-01-02 \n\n  \nX2,Bolt,-1,1,\nX3,Cap,1,-2,\nX4,Pin,1,1,2025-02-30\nX5,Too,many,fields,here,now")
    assert records == [Record("X1", "Nut", 2, 0.5, date(2025, 1, 2))], f"Fields must be stripped; got {records}."
    assert bad == [4, 5, 6, 7], f"Negative numbers, impossible dates and wrong field counts are bad lines (blank lines are not): {bad}."


def test_build_report_is_pure_and_exact(no_real_io):
    expected = (
        "INVENTORY REPORT 2025-06-15\n"
        "items: 7  units: 70  value: 336.47\n"
        "low stock (<5): B200, C300, J900\n"
        "expired: C300, E500\n"
        "most valuable: A100 Widget (100.00)"
    )
    assert build_report(RECORDS_A, TODAY) == expected, "build_report(records, today) must return exactly this text (no trailing newline)."
    assert build_report([], TODAY) == (
        "INVENTORY REPORT 2025-06-15\nitems: 0  units: 0  value: 0.00\nlow stock (<5): none\nexpired: none\nmost valuable: none"
    ), "Report of no records is wrong."


def test_build_report_uses_the_given_date(no_real_io):
    report = build_report(RECORDS_A, date(2026, 1, 1))
    assert report.splitlines()[0] == "INVENTORY REPORT 2026-01-01", "The title uses the date passed in."
    assert "expired: A100, C300, D400, E500, H800" in report, (
        "With today = 2026-01-01 every record with an expiry date has expired. Never call date.today() in the core."
    )


# ---- main and the commands -----------------------------------------------------

@pytest.mark.parametrize("filename,lines,expected", SCRIPTS, ids=[" | ".join(s[1])[:40] for s in SCRIPTS])
def test_command_scripts_match_the_legacy_output(filename, lines, expected, no_real_io):
    session = Session("a.csv" if filename == "A" else "b.csv", lines)
    code = session.run()
    assert session.written == expected, (
        "Output differs from the legacy script.\n--- expected ---\n" + "\n".join(expected) +
        "\n--- got ---\n" + "\n".join(session.written)
    )
    assert code == 0, f"main must return 0 after a normal session, got {code!r}."


def test_prompt_and_eof(no_real_io):
    session = Session("a.csv", ["value"])
    session.run()
    assert session.prompts == ["> ", "> "], f"main must call read('> ') for every command and stop on EOFError; prompts were {session.prompts}."


def test_missing_file_and_usage(no_real_io):
    session = Session("nofile.csv", ["list"])
    assert session.run() == 1, "A file that cannot be opened makes main return 1."
    assert session.written == MISSING_FILE_OUTPUT, f"Expected {MISSING_FILE_OUTPUT}, got {session.written}."
    assert session.prompts == [], "No commands are read when the file cannot be opened."
    quiet = Session("a.csv", [])
    out = []
    code = main([], read=quiet.read, write=out.append, today=lambda: TODAY, opener=quiet.opener)
    assert code == 2 and out == ["usage: inventory FILE"], f"No arguments: write 'usage: inventory FILE' and return 2, got {code}, {out}."
    assert quiet.opened == [], "With no arguments nothing may be opened."


def test_file_is_opened_through_the_injected_opener(no_real_io):
    session = Session("a.csv", ["quit"])
    session.run()
    assert session.opened == ["a.csv"], f"main must open argv[0] with opener(path); calls were {session.opened}."


def test_today_is_injected_and_read_per_command(no_real_io):
    session = Session("a.csv", ["expired"], today=date(2026, 1, 1))
    session.run()
    assert [l.split()[0] for l in session.written[2:]] == ["C300", "E500", "D400", "H800", "A100"], (
        f"'expired' must use the injected today and sort by expiry date then sku. Got {session.written[2:]}"
    )


def test_two_runs_do_not_share_state(no_real_io):
    first = Session("a.csv", ["list"])
    first.run()
    second = Session("b.csv", ["list"])
    second.run()
    assert second.written == ["loaded 0 records", "no records"], (
        f"The second run shows {second.written}. Records (or bad-line numbers) leaked from the first run: no module-level data."
    )


def test_registry_has_the_commands_and_accepts_new_ones(no_real_io):
    for name in ("list", "low", "expired", "value", "find", "report", "help"):
        assert name in COMMANDS, f"COMMANDS is missing {name!r}. Register each command with @register_command('{name}')."

    @register_command("count")
    def cmd_count(records, args, today):
        return [f"{len(records)} records"]

    try:
        assert COMMANDS["count"] is cmd_count, "register_command must store the function in COMMANDS and return it unchanged."
        session = Session("a.csv", ["count", "help"])
        session.run()
        assert session.written[2] == "7 records", f"A new registered command must be runnable by main, got {session.written}."
        assert "count" in session.written[3], f"'help' must list registered commands, got {session.written[3]!r}."
    finally:
        COMMANDS.pop("count", None)


# ---- structure -------------------------------------------------------------------

def _chain_length(node):
    length = 1
    while len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
        node = node.orelse[0]
        length += 1
    return length


def _tree():
    return ast.parse(Path(solution.__file__).read_text())


def _functions(tree):
    return [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]


def test_no_function_is_longer_than_20_lines():
    for fn in _functions(_tree()):
        size = fn.end_lineno - fn.lineno + 1
        assert size <= 20, f"{fn.name} is {size} lines (limit 20, counting def and decorators' body). Split it into smaller named functions."


def test_no_module_level_mutable_state_except_the_registry():
    tree = _tree()
    makers = {"list", "dict", "set", "defaultdict", "Counter", "deque", "OrderedDict"}
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) else []
        value = getattr(node, "value", None)
        if not targets or value is None:
            continue
        mutable = isinstance(value, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)) or (
            isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in makers
        )
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        assert not (mutable and names != ["COMMANDS"]), (
            f"Module-level mutable object {names} on line {node.lineno}. Data belongs in function arguments and return values; "
            "only the COMMANDS registry may live at module level."
        )
    assert not any(isinstance(n, ast.Global) for n in ast.walk(tree)), "Do not use 'global': pass the data in and return it."


def test_print_input_open_are_called_only_inside_main():
    tree = _tree()
    for fn in _functions(tree):
        if fn.name == "main":
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"print", "input", "open"}:
                raise AssertionError(
                    f"{fn.name} calls {node.func.id}(). Only main may talk to the outside world; "
                    "the other functions take what they need and return strings or lists."
                )
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            assert node.value.func.id not in {"print", "input", "open"}, "No I/O at module level."


def test_nobody_calls_today_directly():
    for node in ast.walk(_tree()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "today":
            raise AssertionError("date.today() is called directly. Take 'today' as a parameter (main's default may be date.today, uncalled).")


def test_commands_are_registered_with_the_decorator_not_an_if_chain():
    tree = _tree()
    decorated = 0
    for fn in _functions(tree):
        for deco in fn.decorator_list:
            if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name) and deco.func.id == "register_command":
                decorated += 1
    assert decorated >= 7, f"Only {decorated} functions use @register_command(...). Each command (list, low, expired, value, find, report, help) must register itself."
    for fn in _functions(tree):
        for node in ast.walk(fn):
            if isinstance(node, ast.If) and _chain_length(node) >= 3:
                raise AssertionError(f"{fn.name} still has an if/elif chain of 3 or more branches. Look commands up in the COMMANDS registry.")


def test_record_uses_the_dataclass_decorator():
    cls = next(n for n in _tree().body if isinstance(n, ast.ClassDef) and n.name == "Record")
    names = []
    for deco in cls.decorator_list:
        target = deco.func if isinstance(deco, ast.Call) else deco
        names.append(target.attr if isinstance(target, ast.Attribute) else getattr(target, "id", ""))
    assert "dataclass" in names, "Decorate Record with @dataclass."
