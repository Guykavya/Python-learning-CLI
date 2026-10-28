# Implement C3 linearization

Python computes every class's MRO with the **C3 linearization** algorithm. In this problem you
implement it yourself, for classes described only by their names.

Write `mro(cls_name, bases_map)` in `solution.py`.

- `bases_map` is a dict: class name -> list (or tuple) of its direct base names, in order.
  `{"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}` describes the diamond `class D(B, C)`.
- An empty list means the class inherits only from `object`. You may also write `"object"`
  explicitly; it is never a key of `bases_map`.
- Return the MRO as a list of names that **ends with `"object"`**:
  `mro("D", m)` -> `["D", "B", "C", "A", "object"]`. `mro("object", m)` -> `["object"]`.
- A base name that is not in `bases_map` (and is not `"object"`): let the `KeyError` happen.
- The same base listed twice (`"X": ["A", "A"]`): raise `TypeError(f"duplicate base class {name}")`.
- If C3 cannot find an order, raise
  `TypeError(f"Cannot create a consistent method resolution order (MRO) for bases {names}")`. This is
  Python's own message, and `names` are the classes that are stuck: the **heads** of the lists that are
  still not empty when the merge fails, each name only once, in the order of those lists, joined with
  `", "`.
- You may assume there are no cycles (a class never inherits from itself).

## The algorithm

```text
L(object) = [object]
L(C)      = [C] + merge(L(B1), L(B2), ..., L(Bn), [B1, B2, ..., Bn])     for class C(B1, ..., Bn)
            (with no bases: [C, object])

merge(lists):
    result = []
    while some list is not empty:
        for each non-empty list, in order:
            head = its first item
            if head is not in the TAIL (everything after the first item) of any list:
                good head found -> stop looking
        if no good head: fail (inconsistent hierarchy)
        append head to result, and remove it from the FRONT of every list where it is first
    return result
```

## Example

```python
m = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
mro("D", m)        # ['D', 'B', 'C', 'A', 'object']
mro("A", m)        # ['A', 'object']

bad = {"X": [], "Y": ["X"], "Z": ["X", "Y"]}     # class Z(X, Y): X before its own subclass Y
mro("Z", bad)      # TypeError: Cannot create a consistent method resolution order (MRO) for bases X, Y
# merge([X, object], [Y, X, object], [X, Y]) is stuck at once: the heads are X, Y, X -> "X, Y"

bad2 = {"A": [], "B": [], "AB": ["A", "B"], "BA": ["B", "A"], "Bad": ["AB", "BA"]}
mro("Bad", bad2)   # TypeError: ... for bases A, B
# AB and BA are taken first; then [A, B, object] and [B, A, object] are stuck: heads A, B
```

The tests build the same classes in real Python with `type(name, bases, {})` and compare your result
with `__mro__`, also for randomly generated hierarchies.
