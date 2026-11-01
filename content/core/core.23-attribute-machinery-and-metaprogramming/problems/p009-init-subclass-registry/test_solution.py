import pytest

from solution import Plugin


class CsvExporter(Plugin, key="csv"):
    def __init__(self, sep=","):
        self.sep = sep


class JsonExporter(Plugin, key="json"):
    pass


def test_subclass_is_registered_under_its_key():
    assert Plugin.registry["csv"] is CsvExporter, (
        "class CsvExporter(Plugin, key='csv') must register the CLASS itself in Plugin.registry['csv']."
    )
    assert Plugin.registry["json"] is JsonExporter, "Every subclass with a key is registered."


def test_key_is_stored_on_the_class():
    assert CsvExporter.key == "csv", "Store the key on the new class too: cls.key = key."


def test_base_is_not_registered():
    assert Plugin not in Plugin.registry.values(), "__init_subclass__ runs for subclasses only; Plugin itself is never registered."


def test_one_shared_registry():
    assert CsvExporter.registry is Plugin.registry, (
        "There must be ONE registry dict, on Plugin. Do not create cls.registry = {} for each subclass."
    )


def test_no_key_means_not_registered():
    before = dict(Plugin.registry)

    class BaseExporter(Plugin):
        pass

    assert Plugin.registry == before, "A subclass created without key= is a helper base and must not be registered."

    class XmlExporter(BaseExporter, key="xml-t1"):
        pass

    assert Plugin.registry["xml-t1"] is XmlExporter, "A grandchild with a key is registered too."


def test_duplicate_key_is_refused_at_class_creation():
    with pytest.raises(ValueError) as info:
        class OtherCsv(Plugin, key="csv"):
            pass
    assert "csv" in str(info.value), "The error message must name the duplicate key."
    assert Plugin.registry["csv"] is CsvExporter, "A refused duplicate must not replace the first registered class."


def test_create_builds_an_instance():
    exporter = Plugin.create("csv", sep=";")
    assert isinstance(exporter, CsvExporter), "create(key) must look the class up and call it."
    assert exporter.sep == ";", "create must pass the remaining arguments on to the class."
    assert isinstance(Plugin.create("json"), JsonExporter)


def test_create_unknown_key():
    with pytest.raises(KeyError) as info:
        Plugin.create("pdf")
    assert "pdf" in str(info.value), "An unknown key raises KeyError naming it."


def test_other_keywords_are_passed_up_the_chain():
    class Tagged:
        def __init_subclass__(cls, /, tag=None, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.tag = tag

    try:
        class Yaml(Plugin, Tagged, key="yaml-t2", tag="text"):
            pass
    except TypeError:
        pytest.fail(
            "Plugin.__init_subclass__ must accept **kwargs and pass them to super().__init_subclass__(**kwargs), "
            "so other bases (here Tagged) get their own keywords."
        )
    assert (Yaml.tag, Plugin.registry["yaml-t2"]) == ("text", Yaml), "Both bases must have done their job."


def test_unknown_keyword_still_fails():
    with pytest.raises(TypeError):
        class Bad(Plugin, key="bad-t3", colour="red"):
            pass
