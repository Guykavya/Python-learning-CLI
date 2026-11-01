## Approach

`co_consts` of a module holds the constants of the module body, and each `def`, `class` body
and `lambda` appears there as a code object with its own `co_consts`. So collecting constants is
a tree walk over code objects. Folding is then detected simply by looking for the *answer* among
the constants, compared by type and value, because `==` alone treats `1000`, `1000.0` and
`True`/`1` as equal.

## Code

```python
CodeType = type(compile("", "<src>", "exec"))


def all_constants(source, mode="exec"):
    found = []
    todo = [compile(source, "<src>", mode)]
    while todo:
        code = todo.pop()
        for const in code.co_consts:
            if isinstance(const, CodeType):
                todo.append(const)
            else:
                found.append(const)
    return found


def is_folded(expr, value):
    for const in all_constants(expr, "eval"):
        if type(const) is type(value) and const == value:
            return True
    return False
```

## Complexity

Compiling is linear in the source; the walk is O(total number of constants).

## Another way

A recursive generator reads well for tree walks (`types.CodeType` is the same class as
`CodeType` above):

```python
def _walk(code):
    for const in code.co_consts:
        if isinstance(const, CodeType):
            yield from _walk(const)
        else:
            yield const


def all_constants(source, mode="exec"):
    return list(_walk(compile(source, "<src>", mode)))
```

You can also see folding from the *AST* side: in 3.11 to 3.13 the AST optimizer did it, and in
3.14 most folding moved into the bytecode compiler's later stage. Either way, `ast.parse` shows
the unfolded `BinOp`, and only the compiled code holds the answer. Folding has size limits (for
example a huge `"a" * 10**6` is not folded) that also differ between versions.
