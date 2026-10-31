import pytest

from solution import classify_imports, find_imports

EXAMPLE = '''
import os, sys
import numpy as np
from collections.abc import Iterable
from .helpers import tidy
import config

def load():
    import requests.adapters
    text = "import fake"    # a string, not an import
'''


def test_example_find():
    assert find_imports(EXAMPLE) == ["collections", "config", "numpy", "os", "requests", "sys"], "Top-level names of every absolute import, sorted, also the one inside load(). Strings and comments are not imports: use ast, not text search."


def test_example_classify():
    assert classify_imports(EXAMPLE, local={"config"}) == {
        "stdlib": ["collections", "os", "sys"],
        "third_party": ["numpy", "requests"],
        "local": [".helpers", "config"],
    }, "config is in local; .helpers is relative so local; os/sys/collections are in sys.stdlib_module_names; the rest is third party."


def test_top_level_name_only():
    assert find_imports("import xml.etree.ElementTree as ET\nfrom urllib.parse import urlparse\n") == ["urllib", "xml"], "Keep only the part before the first dot: xml.etree.ElementTree -> xml."


def test_several_names_in_one_import():
    assert find_imports("import json, csv, pathlib\n") == ["csv", "json", "pathlib"], "import a, b, c has three aliases in node.names. Loop over all of them."


def test_no_duplicates():
    assert find_imports("import os\nimport os.path\nfrom os import sep\n") == ["os"], "Each name once. Use a set."


def test_relative_not_in_find():
    assert find_imports("from . import x\nfrom .utils import y\nfrom ..core import z\n") == [], "find_imports lists only absolute imports (node.level == 0). node.module is None for 'from . import x'."


def test_relative_forms_in_classify():
    src = "from . import x\nfrom .utils import y\nfrom ..core.db import q\nfrom .utils import z\n"
    assert classify_imports(src)["local"] == [".", "..core.db", ".utils"], "Relative imports are local, written as '.' * level + module (module may be None). Sorted, no duplicates."


def test_text_tricks_are_not_imports():
    src = '# import secret\nmessage = "from evil import x"\ndoc = """\nimport hidden\n"""\n'
    assert find_imports(src) == [], "Comments and strings are not code. ast never sees them as Import nodes."


def test_local_wins_over_stdlib():
    out = classify_imports("import json\nimport random\n", local=["random"])
    assert out == {"stdlib": ["json"], "third_party": [], "local": ["random"]}, "A local file random.py would shadow the standard random, so a name in local is local first."


def test_local_accepts_any_iterable():
    out = classify_imports("import mytools\n", local=("mytools",))
    assert out["local"] == ["mytools"], "local can be a tuple, list or set."


def test_future_and_nested_stdlib():
    out = classify_imports("from __future__ import annotations\nimport importlib.metadata\nimport tomllib\n")
    assert out["stdlib"] == ["__future__", "importlib", "tomllib"], "__future__, importlib and tomllib are all in sys.stdlib_module_names."


def test_empty_and_all_keys():
    assert classify_imports("") == {"stdlib": [], "third_party": [], "local": []}, "Always return all three keys, even with nothing in them."
    assert find_imports("x = 1\n") == [], "No imports: empty list."


def test_imports_in_nested_blocks():
    src = "try:\n    import ujson as json\nexcept ImportError:\n    import json\nif True:\n    def f():\n        from yaml import safe_load\n"
    out = classify_imports(src)
    assert out == {"stdlib": ["json"], "third_party": ["ujson", "yaml"], "local": []}, "ast.walk visits every node, also inside try, if and def blocks."


def test_syntax_error():
    with pytest.raises(SyntaxError):
        find_imports("import (\n")
