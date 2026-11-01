import ast
from pathlib import Path

import pytest

import solution
from solution import CsvExporter, JsonExporter, Money, create_exporter, register_exporter

ROWS = [{"name": "Ana", "score": 90}, {"name": "Bo", "score": 75}]


def test_factory_builds_the_right_class():
    assert isinstance(create_exporter("json"), JsonExporter), "create_exporter('json') must return a JsonExporter."
    assert isinstance(create_exporter("csv"), CsvExporter), "create_exporter('csv') must return a CsvExporter."


def test_factory_returns_a_new_object_each_time():
    assert create_exporter("json") is not create_exporter("json"), (
        "Each call must build a new exporter (call the class), not hand out one shared instance."
    )


def test_exporters_still_work():
    assert create_exporter("json").export(ROWS) == '[{"name": "Ana", "score": 90}, {"name": "Bo", "score": 75}]', (
        "JSON output changed. Keep JsonExporter exactly as it was."
    )
    assert create_exporter("csv").export(ROWS) == "name,score\nAna,90\nBo,75", "CSV output changed."
    assert create_exporter("csv").export([]) == "", "CSV of no rows is the empty string."


def test_unknown_format_lists_the_known_ones():
    with pytest.raises(ValueError) as info:
        create_exporter("xml")
    message = str(info.value)
    assert "xml" in message, f"The message {message!r} should name the bad format 'xml'."
    assert "csv" in message and "json" in message, (
        f"The message {message!r} should list the known formats (csv, json) so the caller can fix the typo."
    )
    assert message.index("csv") < message.index("json"), "List the known formats sorted: csv, json."


def test_new_exporter_without_editing_the_factory():
    @register_exporter("shout")
    class ShoutExporter:
        def export(self, rows):
            return "!".join(str(r["name"]).upper() for r in rows)

    exporter = create_exporter("shout")
    assert isinstance(exporter, ShoutExporter), "A class registered with @register_exporter must be creatable by name."
    assert exporter.export(ROWS) == "ANA!BO", "The new exporter's own export must be used."
    with pytest.raises(ValueError) as info:
        create_exporter("nope")
    assert "shout" in str(info.value), "The list of known formats must include newly registered ones."


def test_factory_has_no_if_chain():
    tree = ast.parse(Path(solution.__file__).read_text())
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "create_exporter")
    ifs = [n for n in ast.walk(fn) if isinstance(n, ast.If)]
    assert len(ifs) <= 1, (
        f"create_exporter has {len(ifs)} 'if' statements. Look the class up in a registry dict instead of an if/elif chain."
    )


def test_from_string():
    assert Money.from_string("12.50 EUR") == Money(1250, "EUR"), "'12.50 EUR' is 1250 cents of EUR."
    assert Money.from_string("3") == Money(300), "No cents and no currency: 300 cents, default USD."
    assert Money.from_string("7.5 GBP") == Money(750, "GBP"), "'7.5' means 7.50 (pad the cents), not 7.05."
    assert Money.from_string("0.05") == Money(5), "'0.05' is 5 cents."


def test_from_dict():
    assert Money.from_dict({"cents": 305, "currency": "GBP"}) == Money(305, "GBP"), "from_dict reads 'cents' and 'currency'."
    assert Money.from_dict({"cents": 99}) == Money(99, "USD"), "A missing currency defaults to USD."


def test_constructors_are_inheritance_safe():
    class Euro(Money):
        pass

    a = Euro.from_string("1.00 EUR")
    b = Euro.from_dict({"cents": 5})
    assert type(a) is Euro and type(b) is Euro, (
        f"Euro.from_string gave {type(a).__name__}. Inside a classmethod build the object with cls(...), "
        "not Money(...), so subclasses get their own type."
    )
    assert type(Money.from_string("1")) is Money, "Money.from_string must still return a Money."
