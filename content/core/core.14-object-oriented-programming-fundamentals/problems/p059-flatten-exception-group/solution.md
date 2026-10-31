## Approach

An exception group is a tree (chapter section 19): inner nodes are groups, leaves are ordinary
exceptions. `leaves` is a recursive walk that builds the path on the way back up: a leaf at index `i`
has path `(i,)`; a leaf with path `p` inside the sub-group at index `i` has path `(i,) + p`.

`count_by_type` and `partition` reuse `leaves`. `split` already does the hard work of matching leaves
at every depth (with `isinstance`, so subclasses and tuples of types work); we only flatten its two
results and turn `None` into an empty list.

## Code

```python
def leaves(eg):
    if not isinstance(eg, BaseExceptionGroup):
        raise TypeError("expected an exception group")
    result = []
    for i, exc in enumerate(eg.exceptions):
        if isinstance(exc, BaseExceptionGroup):
            for path, leaf in leaves(exc):
                result.append(((i,) + path, leaf))
        else:
            result.append(((i,), exc))
    return result


def count_by_type(eg):
    counts = {}
    for _, exc in leaves(eg):
        name = type(exc).__name__
        counts[name] = counts.get(name, 0) + 1
    return counts


def _messages(group):
    if group is None:
        return []
    return [str(exc) for _, exc in leaves(group)]


def partition(eg, exc_type):
    match, rest = eg.split(exc_type)
    return _messages(match), _messages(rest)
```

## Complexity

O(n · d) for n leaves at depth up to d: every leaf's path is rebuilt once per level. `split` is O(size of
the tree).

## Another way

Write `leaves` as a generator with a `path` parameter: `def walk(eg, path=()):` and
`yield from walk(exc, path + (i,))` for groups, `yield path + (i,), exc` for leaves. It builds each path
once instead of once per level. `count_by_type` can use `collections.Counter`, which also keeps
first-seen order.
