import typing
from dataclasses import dataclass
from typing import get_args, get_type_hints

import pytest

import solution
from solution import Plugin, PluginRegistry


class Upper:
    name = "upper"
    version = 2

    def run(self, text):
        return text.upper()


class Exclaim:
    def __init__(self):
        self.name = "exclaim"
        self.version = 1

    def run(self, text):
        return text + "!"


@dataclass
class Strip:
    name: str = "strip"
    version: int = 3

    def run(self, text):
        return text.strip()


def test_plugin_is_a_protocol_with_three_members():
    assert typing.is_protocol(Plugin), "Plugin must inherit from Protocol."
    assert typing.get_protocol_members(Plugin) == frozenset({"name", "version", "run"}), (
        "Plugin has three members: the attributes name and version, and the method run."
    )
    assert get_type_hints(Plugin) == {"name": str, "version": int}, "Declare name: str and version: int in the class body (no values)."
    assert get_type_hints(Plugin.run) == {"text": str, "return": str}, "run(self, text: str) -> str."


def test_registry_hints():
    R = PluginRegistry
    assert get_type_hints(R.register) == {"plugin": Plugin, "return": type(None)}, "register(self, plugin: Plugin) -> None."
    assert get_type_hints(R.names) == {"return": list[str]}, "names -> list[str]."
    h = get_type_hints(R.get)
    assert h["name"] is str and set(get_args(h["return"])) == {Plugin, type(None)}, "get(self, name: str) -> Plugin | None."
    assert get_type_hints(R.run_all) == {"text": str, "return": str}, "run_all(self, text: str) -> str."
    assert get_type_hints(R.describe) == {"return": list[str]}, "describe -> list[str]."


def test_register_and_names_in_order():
    reg = PluginRegistry()
    reg.register(Exclaim())
    reg.register(Upper())
    reg.register(Strip())
    assert reg.names() == ["exclaim", "upper", "strip"], "names() keeps the registration order."


def test_run_all_in_order():
    reg = PluginRegistry()
    reg.register(Upper())
    reg.register(Exclaim())
    assert reg.run_all("hi") == "HI!", "Pass the text through each plugin in order: upper, then exclaim."
    reg2 = PluginRegistry()
    reg2.register(Exclaim())
    reg2.register(Upper())
    assert reg2.run_all("hi") == "HI!", "Exclaim then Upper: 'hi!' becomes 'HI!'."
    reg3 = PluginRegistry()
    reg3.register(Strip())
    reg3.register(Exclaim())
    assert reg3.run_all("  x ") == "x!", "The output of one plugin is the input of the next: strip, then exclaim."


def test_run_all_with_no_plugins():
    assert PluginRegistry().run_all("same") == "same", "No plugins: return the text unchanged."


def test_describe():
    reg = PluginRegistry()
    reg.register(Upper())
    reg.register(Exclaim())
    reg.register(Strip())
    assert reg.describe() == ["upper v2", "exclaim v1", "strip v3"], "One string per plugin: '<name> v<version>'."
    assert PluginRegistry().describe() == [], "No plugins: empty list."


def test_get():
    reg = PluginRegistry()
    u = Upper()
    reg.register(u)
    assert reg.get("upper") is u, "get returns the registered object itself."
    assert reg.get("nope") is None, "Unknown name: None."


def test_duplicate_name_rejected():
    reg = PluginRegistry()
    first = Upper()
    reg.register(first)
    with pytest.raises(ValueError, match="duplicate plugin: upper"):
        reg.register(Upper())
    assert reg.get("upper") is first and reg.names() == ["upper"], "A rejected plugin must not replace the first one."


def test_registries_are_independent():
    a, b = PluginRegistry(), PluginRegistry()
    a.register(Upper())
    assert b.names() == [], "Each registry needs its own dict, created in __init__."
