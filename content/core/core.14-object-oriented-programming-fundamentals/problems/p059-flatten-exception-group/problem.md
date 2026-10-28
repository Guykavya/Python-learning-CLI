# Flatten a nested exception group

Exception groups can be nested: a group of uploads may contain a group per file, which contains the
errors of each chunk. To log or count them you need the **leaves** (the real exceptions) and where they
sit in the tree.

In `solution.py` write three functions. Each one takes an exception group `eg` (an `ExceptionGroup`,
or a `BaseExceptionGroup`, its parent class, which can also hold exceptions like
`KeyboardInterrupt`).

### `leaves(eg)`

Return a list of `(path, exc)` pairs, one for every leaf, in depth-first, left-to-right order.
`path` is a tuple of the indexes you follow through `.exceptions` from `eg` down to the leaf.
`exc` is the leaf exception object itself (not a copy).
If `eg` is not a `BaseExceptionGroup`, raise `TypeError("expected an exception group")`.

### `count_by_type(eg)`

Return a dict: class name of each leaf -> how many leaves have that class. Keys appear in the order the
class is first seen in `leaves(eg)`.

### `partition(eg, exc_type)`

Return a tuple `(matched, rest)` of two lists with the `str()` of the leaves, in leaf order: `matched`
for leaves that are instances of `exc_type` (subclasses count), `rest` for the others.
Use `eg.split(exc_type)`: it returns `(match_group, rest_group)`, and either part is `None` when it is
empty. A `None` part gives an empty list.

## Example

```python
eg = ExceptionGroup("upload", [
    ValueError("bad name"),                                   # path (0,)
    ExceptionGroup("file a", [                                # (1, ...)
        OSError("disk full"),                                 # (1, 0)
        ExceptionGroup("chunk 3", [ValueError("bad crc")]),   # (1, 1, 0)
    ]),
    KeyError("size"),                                         # (2,)
])

[(path, str(e)) for path, e in leaves(eg)]
# [((0,), 'bad name'), ((1, 0), 'disk full'), ((1, 1, 0), 'bad crc'), ((2,), "'size'")]

count_by_type(eg)
# {'ValueError': 2, 'OSError': 1, 'KeyError': 1}

partition(eg, ValueError)
# (['bad name', 'bad crc'], ['disk full', "'size'"])

partition(eg, LookupError)      # KeyError is a LookupError
# (["'size'"], ['bad name', 'disk full', 'bad crc'])

leaves(ValueError("x"))         # TypeError: expected an exception group
```
