import ast
import inspect

import pytest

import solution
from solution import summarise_orders


# The original, unchanged. Your function must agree with it on every input.
def s(r):
    d={}
    for x in r:
        if not x or x[0]=='#': continue
        p=x.split(',')
        if len(p)!=3: continue
        try: q=int(p[1]);c=float(p[2])
        except: continue
        if q<=0: continue
        k=p[0].strip().lower()
        d[k]=d.get(k,[0,0.0]); d[k][0]+=q; d[k][1]+=q*c
    return sorted(((k,v[0],round(v[1],2)) for k,v in d.items()),key=lambda t:(-t[2],t[0]))


CASES = {
    "example": ["# name,qty,price", "Pen,3,10.5", "book,1,120", "pen,2,10.5", "", "eraser,two,5"],
    "empty list": [],
    "only skipped rows": ["", "#", "# a,1,2", "a,b", "a,1,2,3", "x,0,5", "y,-2,5", "z,1,abc"],
    "comment needs # in first column": [" #x,1,2", "#y,1,2"],
    "spaces around numbers": ["pen, 2 ,3.5", "pen,2, 3.5 "],
    "spaces kept inside name": ["red pen,1,2", " Red Pen ,1,2", "redpen,1,2"],
    "quantity must be an int": ["pen,2.0,3", "pen,2,3", "pen,1e2,1"],
    "price may be any float text": ["a,1,1e2", "b,2,.5", "c,1,-3"],
    "case-insensitive names": ["Pen,1,1", "pen,1,1", "PEN,1,1"],
    "ties sorted by name": ["b,1,5", "a,1,5", "c,5,1"],
    "sort uses the rounded revenue": ["b,1,5", "a,1,5", "aa,1,4.999", "c,1,4.994"],
    "rounding at the end": ["x,1,0.1", "x,1,0.2", "x,1,0.3", "y,3,0.1", "z,1,0.004", "z,1,0.004", "z,1,0.004"],
    "rounding half cases": ["p,1,0.125", "q,1,0.135", "r,3,0.335"],
    "unicode digits and names": ["ćaj,२,3", "Ćaj,1,1.5"],
    "empty name": [",1,2", " ,1,3"],
    "semicolons are not commas": ["a;1;2", "a,1;2,3"],
}


@pytest.mark.parametrize("label", list(CASES))
def test_same_as_original(label):
    rows = CASES[label]
    expected = s(rows)
    got = summarise_orders(list(rows))
    assert got == expected, (
        f"Case '{label}': the original returns {expected!r}, yours {got!r}. Run the original on "
        "these rows in the REPL and find which rule (skip, strip, round, sort) differs."
    )


def test_result_items_are_tuples():
    got = summarise_orders(["a,1,2"])
    assert got and type(got[0]) is tuple, "Each item should be a (name, quantity, revenue) tuple."
    assert type(got[0][1]) is int and type(got[0][2]) is float, "Quantity is an int, revenue a float."


def test_does_not_change_rows():
    rows = ["Pen,3,10.5", "", "book,1,120"]
    before = list(rows)
    summarise_orders(rows)
    assert rows == before, "Do not change the caller's list."


def test_has_a_docstring():
    doc = inspect.getdoc(summarise_orders) or ""
    assert len(doc.split()) >= 8 and "TODO" not in doc, (
        "Write a real docstring: what a row looks like, which rows are skipped, what is returned."
    )


def test_no_bare_except():
    tree = ast.parse(inspect.getsource(solution))
    bare = [node.lineno for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler) and node.type is None]
    assert not bare, (
        f"Bare 'except:' on line(s) {bare}. int() and float() on a string raise ValueError; "
        "catch exactly that."
    )
    broad = [
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler)
        and isinstance(node.type, ast.Name) and node.type.id in ("Exception", "BaseException")
    ]
    assert not broad, f"'except Exception' on line(s) {broad} is almost as broad. Catch ValueError."
