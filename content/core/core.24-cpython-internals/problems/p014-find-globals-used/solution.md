## Approach

The compiler decides at compile time how each name is loaded: `LOAD_FAST` for locals,
`LOAD_DEREF` for closure variables, `LOAD_ATTR` for `obj.name`, and `LOAD_GLOBAL` for
everything else. So the set of `argval`s of `LOAD_GLOBAL` instructions is exactly "the global
and builtin names this code reads". Nested functions, lambdas and generator expressions have
their own code objects, stored in `co_consts`, so we search those recursively.

At run time `LOAD_GLOBAL` looks in the function's module dictionary (`func.__globals__`) and
then in the builtins. A name found in neither would raise `NameError` when that line runs.

## Code

```python
import builtins
import dis
import types


def _global_loads(code):
    names = {ins.argval for ins in dis.get_instructions(code) if ins.opname == "LOAD_GLOBAL"}
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            names |= _global_loads(const)
    return names


def globals_used(func):
    return sorted(_global_loads(func.__code__))


def undefined_globals(func):
    known_builtins = vars(builtins)
    return [
        name for name in globals_used(func)
        if name not in func.__globals__ and name not in known_builtins
    ]
```

## Complexity

O(I + C) for I instructions and C constants across all code objects, plus O(G log G) to sort
G names.

## Another way

Use the `ast` module instead of bytecode: walk the tree and collect `ast.Name` nodes in
`Load` context, minus names assigned in each scope. That works on source text you have not
imported, but you then have to re-implement Python's scoping rules (locals, `global`,
`nonlocal`, closures, comprehension scopes). Bytecode gives you the compiler's decision for
free, which is why this solution reads it. `inspect.getclosurevars(func)` also reports globals
and builtins, but it uses `co_names`, so it lists attribute names as well, and it does not look
inside nested functions.

Note that the check is static: a name inside an `if False:` branch that was not removed, or a
global created later at run time with `globals()["x"] = ...`, can make the report wrong in both
directions. Real linters accept the same limits.
