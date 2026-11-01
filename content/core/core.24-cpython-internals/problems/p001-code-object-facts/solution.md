## Approach

A code object is a plain object with read-only attributes, so the whole job is reading the right
five attributes and normalising the two that are not stable across versions: sort the name
tuples, and drop `None` from the constants.

## Code

```python
def code_facts(func):
    code = func.__code__
    return {
        "name": code.co_name,
        "argcount": code.co_argcount,
        "locals": sorted(code.co_varnames),
        "names": sorted(code.co_names),
        "constants": [c for c in code.co_consts if c is not None],
    }
```

## Complexity

O(k log k) where k is the number of names (for sorting). Reading the attributes is O(1).

## Another way

Drive it from a table, which also shows that every key is just `co_` plus a name:

```python
def code_facts(func):
    code = func.__code__
    facts = {key: getattr(code, "co_" + attr) for key, attr in
             [("name", "name"), ("argcount", "argcount"), ("locals", "varnames"), ("names", "names")]}
    facts["locals"] = sorted(facts["locals"])
    facts["names"] = sorted(facts["names"])
    facts["constants"] = [c for c in code.co_consts if c is not None]
    return facts
```

**Version note.** In 3.12+ a list comprehension is compiled *inline* (PEP 709), so its loop
variable shows up in the function's `co_varnames`; in 3.11 it lived in a separate nested code
object. In 3.14 small ints such as `1` are often loaded with `LOAD_SMALL_INT` and need not be in
`co_consts`. That is why the tests avoid comprehensions and small-int constants.
