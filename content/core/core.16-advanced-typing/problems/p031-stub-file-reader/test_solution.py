from pathlib import Path
from typing import get_type_hints

import pytest

import solution
from solution import stub_classes, stub_functions, stub_untyped, stub_variables

GEOMETRY = Path(__file__).parent / "fixtures" / "geometry.pyi"


def write(tmp_path, text):
    p = tmp_path / "x.pyi"
    p.write_text(text, encoding="utf-8")
    return p


def test_hints():
    assert get_type_hints(stub_variables)["return"] == dict[str, str], "stub_variables returns dict[str, str]."
    assert get_type_hints(stub_functions)["return"] == dict[str, list[str]], "stub_functions returns dict[str, list[str]]."
    assert get_type_hints(stub_untyped)["return"] == list[str], "stub_untyped returns list[str]."
    assert get_type_hints(stub_classes)["return"] == dict[str, list[str]], "stub_classes returns dict[str, list[str]]."


def test_variables():
    assert stub_variables(GEOMETRY) == {
        "PI": "Final[float]",
        "VERSION": "str",
        "DEBUG": "bool",
        "registry": "dict[str, Shape]",
    }, "Module-level AnnAssign nodes only; value is ast.unparse(node.annotation). Class attributes (name, radius) are not included."


def test_variables_accepts_str_path():
    assert "PI" in stub_variables(str(GEOMETRY)), "path may be a str or a Path: use Path(path).read_text()."


def test_functions_plain_signatures():
    f = stub_functions(GEOMETRY)
    assert f["area"] == ["(width: float, height: float) -> float"], "'(' + ast.unparse(node.args) + ') -> ' + ast.unparse(node.returns)."
    assert f["scale"] == ["(factor: float, *, shape: str=...) -> float"], "unparse(node.args) already writes the '*' and the default (note: ast.unparse writes 'str=...' with no spaces)."
    assert f["describe"] == ["(shape: Shape) -> str"], "A class name in a hint is just text."


def test_functions_overloads_are_collected_in_order():
    f = stub_functions(GEOMETRY)
    assert f["parse"] == ["(text: str) -> int", "(text: str, as_float: bool) -> float"], (
        "An overloaded function appears twice in the stub: collect both signatures, in file order, in one list."
    )


def test_functions_without_return_annotation():
    assert stub_functions(GEOMETRY)["legacy"] == ["(x, y=...)"], (
        "No return annotation: leave off ' -> ...' completely (node.returns is None)."
    )


def test_functions_async():
    assert stub_functions(GEOMETRY)["fetch"] == ["async (url: str, timeout: float=...) -> bytes"], (
        "An async def gets the prefix 'async ' (check isinstance(node, ast.AsyncFunctionDef))."
    )


def test_methods_are_qualified_and_keep_self():
    f = stub_functions(GEOMETRY)
    assert f["Shape.__init__"] == ["(self, name: str) -> None"], "Methods are keyed 'Class.method' and keep 'self' in the text."
    assert f["Shape.area"] == ["(self) -> float"], "Shape.area is a method; the module-level 'area' is a different key."
    assert f["Shape.label"] == ["(self) -> str"], "A @property is still a FunctionDef."
    assert f["Shape.scaled"] == ["(self, factor: float) -> Shape"], "Return annotation 'Shape' is text."
    assert f["Circle.unit"] == ["(cls) -> Circle"], "A classmethod keeps 'cls'."
    assert f["Circle.__init__"] == ["(self, radius: float) -> None"], "Circle has its own __init__."


def test_all_function_keys():
    assert list(stub_functions(GEOMETRY)) == [
        "area", "scale", "legacy", "describe", "parse", "fetch",
        "Shape.__init__", "Shape.area", "Shape.label", "Shape.scaled", "Shape.helper",
        "Circle.__init__", "Circle.unit",
    ], "Every module-level function and every method of a module-level class, once each, in file order."


def test_untyped():
    assert stub_untyped(GEOMETRY) == ["legacy", "Shape.helper"], (
        "legacy has no annotations at all; Shape.helper has an unannotated 'n'. "
        "self/cls need no annotation; '-> None' counts as an annotation."
    )


def test_classes():
    assert stub_classes(GEOMETRY) == {"Shape": [], "Circle": ["Shape"]}, (
        "Class name -> list of base classes as text; no bases gives []."
    )


def test_variables_and_functions_on_a_custom_stub(tmp_path):
    p = write(tmp_path, "X: int\nY = 3\nclass K:\n    Z: str\ndef f(a: int, /, b: str, *args: int, **kw: str) -> None: ...\n")
    assert stub_variables(p) == {"X": "int"}, (
        "Only annotated names at module level: 'Y = 3' has no annotation, and K.Z is inside a class."
    )
    assert stub_functions(p) == {"f": ["(a: int, /, b: str, *args: int, **kw: str) -> None"]}, (
        "ast.unparse(node.args) must be used so that '/', '*args' and '**kw' come out right."
    )
    assert stub_untyped(p) == [], "Everything is annotated (including *args and **kw)."


def test_untyped_detects_every_kind_of_parameter(tmp_path):
    p = write(
        tmp_path,
        "def a(x, /) -> None: ...\n"
        "def b(*args) -> None: ...\n"
        "def c(*, k) -> None: ...\n"
        "def d(**kw) -> None: ...\n"
        "def e() -> None: ...\n"
        "def f(x: int): ...\n"
        "class C:\n"
        "    def m(self, y: int) -> int: ...\n"
        "    def n(self, y) -> int: ...\n"
        "    def o(self): ...\n",
    )
    assert stub_untyped(p) == ["a", "b", "c", "d", "f", "C.n", "C.o"], (
        "A function is untyped if any parameter (positional-only, *args, keyword-only, **kwargs) "
        "or the return is unannotated. e() and C.m are fully typed."
    )


def test_nested_names_are_not_confused(tmp_path):
    p = write(tmp_path, "class A:\n    def run(self) -> None: ...\nclass B:\n    def run(self, x: int) -> int: ...\ndef run() -> str: ...\n")
    assert stub_functions(p) == {
        "A.run": ["(self) -> None"],
        "B.run": ["(self, x: int) -> int"],
        "run": ["() -> str"],
    }, "The same method name in different classes must stay separate: key is 'Class.method'."


def test_does_not_import_the_stub():
    assert not hasattr(solution, "geometry"), "Do not import the stub module; it is data to parse, not code to run."
