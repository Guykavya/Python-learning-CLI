import ast
from pathlib import Path
from typing import Protocol

import solution
from solution import Reader, Writer, copy_all, dump, save_all

TREE = ast.parse(Path(solution.__file__).read_text())


class Source:
    """Can only read."""

    def __init__(self, data):
        self.data = dict(data)

    def read(self, key):
        return self.data[key]

    def keys(self):
        return list(self.data)


class Sink:
    """Can only write."""

    def __init__(self):
        self.entries = []

    def write(self, key, value):
        self.entries.append((key, value))


class Both:
    def __init__(self):
        self.data = {}

    def read(self, key):
        return self.data[key]

    def keys(self):
        return list(self.data)

    def write(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]


class OnlyRead:
    def read(self, key):
        return key


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def _annotation(func, arg):
    for a in func.args.args:
        if a.arg == arg and a.annotation is not None:
            node = a.annotation
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.Attribute):
                return node.attr
    return None


def test_copy_all_with_partial_classes():
    src, dst = Source({"a": "1", "b": "2"}), Sink()
    assert copy_all(src, dst) == 2, "copy_all returns the number of keys copied."
    assert dst.entries == [("a", "1"), ("b", "2")], "A class that only writes must work as the destination; a class that only reads as the source."


def test_dump_and_save_all():
    assert dump(Source({"x": "9", "y": "8"})) == {"x": "9", "y": "8"}, "dump reads every key from a read-only source."
    sink = Sink()
    assert save_all(sink, {"p": "1", "q": "2"}) == 2, "save_all returns how many items it wrote."
    assert sink.entries == [("p", "1"), ("q", "2")], "save_all writes every item to a write-only sink."


def test_full_storage_still_works():
    a, b = Both(), Both()
    a.write("k", "v")
    assert copy_all(a, b) == 1 and b.data == {"k": "v"}, "A class with all the methods works too."
    assert dump(b) == {"k": "v"}, "dump works on a class that also writes."
    assert copy_all(Source({}), Sink()) == 0, "Nothing to copy: 0."


def test_protocols_are_real_protocols():
    assert Protocol in Reader.__mro__ and Protocol in Writer.__mro__, (
        "Reader and Writer must be typing.Protocol classes: class Reader(Protocol): ..."
    )


def test_runtime_checks():
    assert isinstance(Source({}), Reader), "A class with read() and keys() is a Reader (mark the Protocol @runtime_checkable)."
    assert not isinstance(Source({}), Writer), "A read-only class is not a Writer."
    assert isinstance(Sink(), Writer), "A class with write() is a Writer."
    assert not isinstance(Sink(), Reader), "A write-only class is not a Reader."
    assert isinstance(Both(), Reader) and isinstance(Both(), Writer), "A class with everything is both."
    assert not isinstance(OnlyRead(), Reader), "Reader needs BOTH read and keys: OnlyRead lacks keys."


def test_protocols_are_small():
    def methods(cls):
        return {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}

    classes = {n.name: n for n in ast.walk(TREE) if isinstance(n, ast.ClassDef)}
    assert methods(classes["Reader"]) == {"read", "keys"}, "Reader should declare exactly read and keys (no delete, no lock)."
    assert methods(classes["Writer"]) == {"write"}, "Writer should declare exactly write."


def test_functions_ask_for_what_they_need():
    assert _annotation(_func("copy_all"), "src") == "Reader", "copy_all: annotate src as Reader (it only reads)."
    assert _annotation(_func("copy_all"), "dst") == "Writer", "copy_all: annotate dst as Writer (it only writes)."
    assert _annotation(_func("dump"), "src") == "Reader", "dump: annotate src as Reader."
    assert _annotation(_func("save_all"), "dst") == "Writer", "save_all: annotate dst as Writer."


def test_the_fat_interface_is_gone():
    for node in ast.walk(TREE):
        if isinstance(node, ast.ClassDef):
            bases = {b.id for b in node.bases if isinstance(b, ast.Name)}
            assert "ABC" not in bases, "No class may inherit ABC any more: the fat Storage interface should be removed."
            assert not any(isinstance(n, ast.FunctionDef) and any(
                isinstance(d, ast.Name) and d.id == "abstractmethod" for d in n.decorator_list) for n in node.body), (
                "No abstract methods any more: small Protocols replace the fat ABC."
            )
    assert not any(isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call) and getattr(n.exc.func, "id", "") == "NotImplementedError"
                   for n in ast.walk(TREE)), "No method should be a stub that raises NotImplementedError."
