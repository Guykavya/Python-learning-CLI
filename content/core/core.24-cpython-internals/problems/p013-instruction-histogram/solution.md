## Approach

`dis.get_instructions` already decodes the bytecode, so the histogram is a `Counter` over the
`opname` of each instruction. Nested functions are separate code objects stored as constants of
the enclosing code, so the recursive version walks `co_consts`, picks out the code objects and
calls itself on each one. Recursion handles any depth, because a nested code object has its
own `co_consts`.

`by_prefix` is plain string work: `name.split("_", 1)[0]` keeps the text before the first
underscore, and the counts of names with the same prefix are added.

## Code

```python
import dis
import types
from collections import Counter


def opcode_histogram(obj, recursive=False):
    code = obj if isinstance(obj, types.CodeType) else obj.__code__
    hist = Counter(ins.opname for ins in dis.get_instructions(code))
    if recursive:
        for const in code.co_consts:
            if isinstance(const, types.CodeType):
                hist += opcode_histogram(const, recursive=True)
    return hist


def by_prefix(hist):
    grouped = Counter()
    for name, count in hist.items():
        grouped[name.split("_", 1)[0]] += count
    return grouped
```

`Counter + Counter` adds counts key by key. (It also drops keys whose count is zero or less,
which cannot happen here.)

## Complexity

O(I) for I instructions in all the code objects visited, plus O(C) to scan their constants.
`by_prefix` is O(K) for K distinct opnames.

## Another way

Use an explicit stack of code objects instead of recursion:

```python
def opcode_histogram(obj, recursive=False):
    start = obj if isinstance(obj, types.CodeType) else obj.__code__
    hist, todo = Counter(), [start]
    while todo:
        code = todo.pop()
        hist.update(ins.opname for ins in dis.Bytecode(code))
        if recursive:
            todo.extend(c for c in code.co_consts if isinstance(c, types.CodeType))
    return hist
```

`dis.Bytecode(code)` is an iterable of the same `Instruction` objects.

**A version note.** Before Python 3.12 a list comprehension was compiled into its own hidden
code object, so on 3.11 its instructions show up only with `recursive=True`. From 3.12 on
comprehensions are inlined into the enclosing function (PEP 709), so the flat histogram
already includes them. The recursive histogram sees them on every version. Generator
expressions and lambdas are still separate code objects on every version.
