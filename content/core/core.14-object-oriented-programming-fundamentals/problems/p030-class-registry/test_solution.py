import json

import pytest

from solution import CsvExporter, Exporter, JsonExporter

ROWS = [{"name": "pen", "qty": 3}, {"name": "ink", "qty": 1}]


@pytest.fixture(autouse=True)
def restore_registry():
    saved = dict(Exporter.registry)
    yield
    Exporter.registry.clear()
    Exporter.registry.update(saved)


def test_builtin_formats_registered():
    assert isinstance(CsvExporter, type), (
        "CsvExporter is not a class any more. The decorator returned by register() must end with `return klass`."
    )
    assert Exporter.formats() == ["csv", "json"], (
        "Decorate CsvExporter with @Exporter.register('csv') and JsonExporter with @Exporter.register('json')."
    )
    assert Exporter.registry["csv"] is CsvExporter, "registry maps the name to the class itself (not an object)."
    assert CsvExporter.format_name == "csv" and JsonExporter.format_name == "json", (
        "The decorator sets format_name on the class."
    )


def test_decorator_returns_the_class():
    @Exporter.register("upper")
    class UpperExporter(Exporter):
        def export(self, rows):
            return "X"

    assert isinstance(UpperExporter, type), (
        "The decorator must return the class. If it returns None, the name UpperExporter becomes None."
    )
    assert UpperExporter().export([]) == "X", "The returned class must be the same, working class."
    assert Exporter.registry["upper"] is UpperExporter, "The new class is stored under its name."
    assert "upper" in Exporter.formats(), "formats() lists every registered name."


def test_create_makes_an_object_with_options():
    e = Exporter.create("csv")
    assert isinstance(e, CsvExporter), "create('csv') returns a CsvExporter object."
    assert e.sep == ",", "Default options when none are given."
    e2 = Exporter.create("csv", sep=";")
    assert e2.sep == ";", "create passes **options on to the class: CsvExporter(sep=';')."
    assert isinstance(Exporter.create("json", indent=2), JsonExporter), "create('json') returns a JsonExporter."


def test_create_unknown_name():
    with pytest.raises(KeyError) as info:
        Exporter.create("xml")
    msg = str(info.value)
    assert "'xml'" in msg, "The KeyError message must name the unknown format, like 'xml'."
    assert "csv, json" in msg, "The message must list the known formats, sorted and joined with ', '."


def test_duplicate_name_raises():
    try:
        @Exporter.register("csv")
        class Another(Exporter):
            pass
    except ValueError:
        pass
    else:
        pytest.fail("Registering a second class as 'csv' must raise ValueError. Check `name in registry` first.")
    assert Exporter.registry["csv"] is CsvExporter, "A refused registration must not replace the old class."


def test_non_exporter_raises():
    with pytest.raises(TypeError):
        @Exporter.register("plain")
        class Plain:
            pass
    assert "plain" not in Exporter.registry, "A refused class must not be stored."


def test_base_export_not_implemented():
    with pytest.raises(NotImplementedError):
        Exporter().export(ROWS)


def test_csv_export():
    assert CsvExporter().export(ROWS) == "name,qty\npen,3\nink,1", "Header from the first row's keys, then one line per row."
    assert CsvExporter(sep=";").export(ROWS) == "name;qty\npen;3\nink;1", "Use self.sep between the values."
    assert CsvExporter().export([]) == "", "No rows gives an empty string (there are no keys for a header)."
    assert CsvExporter().export([{"a": 1.5, "b": None}]) == "a,b\n1.5,None", "Turn each value into text with str()."


def test_json_export():
    assert JsonExporter().export(ROWS[:1]) == '[{"name": "pen", "qty": 3}]', "Return json.dumps(rows, indent=self.indent)."
    assert JsonExporter(indent=2).export(ROWS) == json.dumps(ROWS, indent=2), "Pass indent on to json.dumps."
    assert JsonExporter().export([]) == "[]", "No rows is the JSON list []."


def test_registry_lives_on_exporter():
    @Exporter.register("tsv")
    class TsvExporter(CsvExporter):
        def __init__(self):
            super().__init__(sep="\t")

    assert Exporter.create("tsv").export(ROWS[:1]) == "name\tqty\npen\t3", (
        "A subclass of CsvExporter can be registered too, and create builds it."
    )
    assert "tsv" in Exporter.formats(), "All names go into the one registry on Exporter."
