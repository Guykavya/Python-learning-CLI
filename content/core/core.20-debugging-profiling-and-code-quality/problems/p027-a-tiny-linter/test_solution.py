import textwrap

from solution import find_issues


def lint(src):
    return find_issues(textwrap.dedent(src))


EXAMPLE = '''\
import os
import sys, json
from typing import Any as A

def load(path, cache={}, *, seen=list()):
    try:
        return json.loads(open(path).read())
    except:
        return None
'''


def test_example():
    got = find_issues(EXAMPLE)
    assert got == [(1, "F401"), (2, "F401"), (3, "F401"), (5, "B006"), (5, "B006"), (8, "E722")], (
        f"Got {got}. os, sys and A are unused (json is read on line 7), line 5 has two mutable defaults "
        "(one keyword-only: look in args.kw_defaults too) and line 8 is a bare except."
    )


def test_clean_code():
    src = '''
    import os
    from collections import Counter

    def count(words, extra=None, *, limit=10):
        try:
            return Counter(words).most_common(limit), os.sep
        except (ValueError, TypeError):
            return extra
    '''
    assert lint(src) == [], f"Clean code must give no issues, got {lint(src)}."


def test_returns_list_of_tuples():
    got = find_issues("import os\n")
    assert got == [(1, "F401")] and isinstance(got, list) and isinstance(got[0], tuple), f"Return a list of (line, code) tuples, got {got!r}."


def test_attribute_use_counts_as_use():
    assert lint("import os.path\nprint(os.path.join('a', 'b'))\n") == [], (
        "`import os.path` binds the name os, and os.path.join(...) reads os. Use alias.name.split('.')[0]."
    )


def test_alias_is_the_bound_name():
    src = "import numpy as np\nfrom math import pi as PI, tau\nprint(numpy, pi, tau)\n"
    assert lint(src) == [(1, "F401"), (2, "F401")], (
        f"Got {lint(src)}. With `as`, the bound name is the alias: np and PI are unused even though "
        "numpy and pi are mentioned; tau is used."
    )


def test_one_report_per_unused_name():
    assert lint("from os import sep, getcwd, path\nprint(path)\n") == [(1, "F401"), (1, "F401")], (
        "Two names of the same import are unused: report F401 twice for line 1."
    )


def test_store_is_not_use():
    assert lint("import json\njson = None\n") == [(1, "F401")], (
        "Assigning to the name (json = None) does not READ the import. Count only ast.Name nodes with ast.Load context."
    )


def test_use_inside_function_counts():
    src = '''
    import re

    def f(s):
        return re.sub("a", "b", s)
    '''
    assert lint(src) == [], "A name read anywhere in the module (also inside a function) counts as used: walk the whole tree."


def test_future_and_star_ignored():
    assert lint("from __future__ import annotations\nfrom os.path import *\n") == [], "Ignore `from __future__ import ...` and star imports."


def test_bare_except_only():
    src = '''
    try:
        pass
    except ValueError:
        pass
    except:
        pass
    try:
        pass
    except Exception:
        pass
    '''
    assert lint(src) == [(6, "E722")], f"Only `except:` with no type is E722 (here line 6), got {lint(src)}."


def test_mutable_default_kinds():
    src = '''
    def a(x=[], y={}, z={1}, w=(), v=None, u=0):
        pass

    def b(p=dict(), q=set(), r=list(), s=tuple(), t=frozenset()):
        pass

    f = lambda items=[]: items
    '''
    assert lint(src) == [(2, "B006"), (2, "B006"), (2, "B006"), (5, "B006"), (5, "B006"), (5, "B006"), (8, "B006")], (
        f"Got {lint(src)}. Mutable: [] {{}} {{1}} and the calls dict() set() list(), also in a lambda. "
        "Not mutable: (), None, 0, tuple(), frozenset()."
    )


def test_methods_and_async():
    src = '''
    class Box:
        def add(self, item, into=[]):
            into.append(item)

    async def fetch(urls=set()):
        return urls
    '''
    assert lint(src) == [(3, "B006"), (6, "B006")], f"Methods and async functions have defaults too, got {lint(src)}."


def test_multiline_default_line():
    src = '''
    def f(
        a,
        b=[
            1,
        ],
    ):
        return a, b
    '''
    assert lint(src) == [(4, "B006")], f"Report B006 at the line of the default value itself (default.lineno), got {lint(src)}."


def test_sorted_by_line_then_code():
    src = '''
    def f(x=[]):
        try:
            pass
        except:
            pass
    import os
    '''
    assert lint(src) == [(2, "B006"), (5, "E722"), (7, "F401")], f"Sort the issues by line, then code; got {lint(src)}."


def test_syntax_error():
    got = find_issues("x = 1\ndef broken(:\n    pass\n")
    assert got == [(2, "E999")], f"Unparseable source gives [(line, 'E999')] from the SyntaxError's lineno; got {got}. Do not let the error escape."
