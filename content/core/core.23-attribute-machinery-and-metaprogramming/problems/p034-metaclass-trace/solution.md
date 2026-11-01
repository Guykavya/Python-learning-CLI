## Approach

First decide which metaclass builds each class, because that decides which `__new__` and
`__call__` run. Then trace class creation (with `__init_subclass__`) and instance creation (with
`MetaB.__call__` and `type.__call__`).

## Trace

**Choosing metaclasses.**

| Class | Candidates | Chosen |
|---|---|---|
| `A` | `MetaA` | `MetaA` |
| `B` | `MetaB` | `MetaB` |
| `C(A, B)` | `MetaA`, `MetaB` | `MetaB` (it is a subclass of `MetaA`, so it is the most derived) |
| `D(C)` | `MetaB` | `MetaB` |
| `E(A, metaclass=Other)` | `Other`, `MetaA` | neither is a subclass of the other: `TypeError` |

**Class creation.**

- `A`: `MetaA.__new__ mcls=MetaA class=A`. No `__init_subclass__` print: the hook on `A` is for subclasses.
- `B`: `MetaB` has no `__new__`, so the inherited `MetaA.__new__` runs with `mcls=MetaB`:
  `MetaA.__new__ mcls=MetaB class=B`. `B`'s parent is `object`, nothing else prints.
- `C`: `MetaA.__new__ mcls=MetaB class=C`, then inside `type.__new__`, `A.__init_subclass__`
  gets `prefix="x-"`: `init_subclass C label=x-C`.
- `D`: `MetaA.__new__ mcls=MetaB class=D`, then `A.__init_subclass__` with the default
  `prefix=""`: `init_subclass D label=D`. The class keyword is **not** inherited.
- `E`: the conflict is found before any hook runs, so the only line is `E failed: TypeError`.

**Inspecting.** `MetaA MetaB MetaB MetaB`, then `x-C D True` (`MetaB` is a subclass of
`MetaA`, so `C` is an instance of `MetaA` too).

**Instances.**

- `C(5)`: `MetaB.__call__ C(5,)`, then `type.__call__` runs `C.__new__ 5`; the result is a `C`,
  so `C.__init__ 5` runs; `got C`.
- `C(-1)`: `MetaB.__call__ C(-1,)`, `C.__new__ -1` returns the string `"negative"`. A string is
  not a `C`, so `__init__` is **skipped**; `got str`. Then `negative False` (no `n` was set).
- `D(2)`: `MetaB.__call__ D(2,)`, `C.__new__ 2`, `C.__init__ 2`, `got D`, and finally `D 2 D`.

## Another way

Print `type(C).__mro__` to see `(MetaB, MetaA, type, object)`, which is why `MetaA.__new__`
runs for `C`. To fix the conflict for `E`, write `class Other(MetaA)`: then `Other` is the
most derived metaclass and `E` is created normally.
