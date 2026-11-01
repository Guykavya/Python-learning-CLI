import ast
import io
from pathlib import Path

import solution
from solution import add_word, display_name, get_port, parse_int, read_or_default

TREE = ast.parse(Path(solution.__file__).read_text())


class CountingDict(dict):
    """A dict that counts every lookup or write made through it."""

    accesses = 0

    def __getitem__(self, key):
        self.accesses += 1
        return super().__getitem__(key)

    def __contains__(self, key):
        self.accesses += 1
        return super().__contains__(key)

    def get(self, key, default=None):
        self.accesses += 1
        return super().get(key, default)

    def setdefault(self, key, default=None):
        self.accesses += 1
        return super().setdefault(key, default)

    def __setitem__(self, key, value):
        self.accesses += 1
        super().__setitem__(key, value)


class FakeFS:
    def __init__(self, files, error=None):
        self.files, self.error = files, error
        self.exists_calls = 0
        self.open_calls = 0

    def exists(self, path):
        self.exists_calls += 1
        return path in self.files

    def open(self, path):
        self.open_calls += 1
        if self.error:
            raise self.error
        if path not in self.files:
            raise FileNotFoundError(path)
        return io.StringIO(self.files[path])


class Named:
    def __init__(self, name):
        self._name = name
        self.reads = 0

    @property
    def name(self):
        self.reads += 1
        return self._name


def _func(name):
    for node in ast.walk(TREE):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name} is missing")


def test_get_port_behavior():
    assert get_port({"port": "9000"}) == 9000, "A string port must be converted with int()."
    assert get_port({"port": 9000}) == 9000, "An int port stays an int."
    assert get_port({}) == 8080, "Missing key: default 8080."
    assert get_port({"port": 0}) == 0, "port 0 is a real value."


def test_get_port_looks_up_once():
    hit = CountingDict(port="1")
    get_port(hit)
    assert hit.accesses == 1, f"{hit.accesses} lookups on a hit. 'if key in d' then 'd[key]' looks twice: use d.get(key, default)."
    miss = CountingDict()
    get_port(miss)
    assert miss.accesses == 1, f"{miss.accesses} lookups on a miss. Use one d.get('port', 8080)."


def test_add_word_behavior():
    index = {}
    add_word(index, "a", 1)
    add_word(index, "b", 2)
    add_word(index, "a", 5)
    assert index == {"a": [1, 5], "b": [2]}, "Each word maps to the list of its line numbers, in order."


def test_add_word_touches_dict_once_on_hit():
    index = CountingDict(a=[1])
    add_word(index, "a", 2)
    assert index["a"] == [1, 2]
    index.accesses = 0
    add_word(index, "a", 3)
    assert index.accesses == 1, (
        f"{index.accesses} dict accesses for a word that is already there. "
        "'if word not in index' + 'index[word]' is two or three; use setdefault(word, []) or try/except KeyError."
    )
    index2 = CountingDict()
    add_word(index2, "z", 1)
    assert index2.accesses <= 2, "A new word should take at most two accesses (setdefault: one)."


def test_read_or_default():
    fs = FakeFS({"a.txt": "hello"})
    assert read_or_default(fs, "a.txt") == "hello", "An existing file returns its text."
    assert read_or_default(fs, "b.txt") == "", "Missing file: default ''."
    assert read_or_default(fs, "b.txt", default="none") == "none", "Missing file: the given default."


def test_read_or_default_does_not_ask_exists():
    fs = FakeFS({"a.txt": "x"})
    read_or_default(fs, "a.txt")
    read_or_default(fs, "nope")
    assert fs.exists_calls == 0, (
        "Do not call fs.exists(): the file can vanish between the check and the open. "
        "Just open it and catch FileNotFoundError."
    )
    assert fs.open_calls == 2, "Open exactly once per call."


def test_permission_error_is_not_hidden():
    fs = FakeFS({"a.txt": "x"}, error=PermissionError("denied"))
    try:
        read_or_default(fs, "a.txt")
    except PermissionError:
        return
    raise AssertionError("PermissionError was swallowed. Catch only FileNotFoundError: other errors are real problems.")


def test_display_name():
    assert display_name(Named("ada")) == "ADA", "Upper-case the name."
    assert display_name(object()) == "ANON", "No name attribute: 'ANON'."


def test_display_name_reads_once():
    obj = Named("ada")
    display_name(obj)
    assert obj.reads == 1, (
        f"name was read {obj.reads} times. hasattr(obj, 'name') reads it once and obj.name reads again. "
        "Use getattr(obj, 'name', None) or try/except AttributeError."
    )


def test_parse_int():
    assert parse_int("42") == 42, "Plain digits."
    assert parse_int("-5") == -5, "Negative numbers are numbers: '-5'.isdigit() is False, so do not pre-check."
    assert parse_int("+3") == 3, "int() accepts a plus sign."
    assert parse_int(" 7 ") == 7, "int() ignores surrounding spaces."
    assert parse_int("abc") is None, "Not a number: None."
    assert parse_int("") is None, "Empty text: None."
    assert parse_int("4.2") is None, "4.2 is not a whole number: None."


def test_no_check_before_use_calls():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Name) and f.id == "hasattr":
                raise AssertionError("hasattr() found. Ask forgiveness: getattr(obj, 'name', None) or try/except AttributeError.")
            if isinstance(f, ast.Attribute) and f.attr in ("isdigit", "isnumeric", "isdecimal", "exists"):
                raise AssertionError(f".{f.attr}() found. Do not check first: try int(...) / open(...) and catch the error.")


def test_no_in_check_for_dict_functions():
    for name in ("get_port", "add_word"):
        for node in ast.walk(_func(name)):
            if isinstance(node, ast.Compare) and any(isinstance(op, (ast.In, ast.NotIn)) for op in node.ops):
                raise AssertionError(
                    f"{name} still uses 'in' / 'not in' before the lookup. Use dict.get(key, default), "
                    "dict.setdefault(key, []) or try/except KeyError."
                )
