## Approach

`Data` defines `__set__`, so it is a data descriptor. `NonData` defines only `__get__`, so it is
a non-data descriptor. `plain` is an ordinary string.

| Code | Reasoning | Printed |
|---|---|---|
| `t.d, t.n, t.plain` | empty instance dict; both descriptors' `__get__` run, the plain attribute is read from the class | `from Data from NonData class attr` |
| `t.d = 1` | data descriptor: `Data.__set__` runs and stores nothing | `Data.__set__ 1` |
| `t.n = 2`, `t.plain = 3` | no `__set__`: both go into `vars(t)` | nothing |
| `t.d, t.n, t.plain` | `d` still goes to `Data`; `n` and `plain` now found in the instance dict first | `from Data 2 3` |
| `sorted(vars(t))` | only `n` and `plain` were stored | `['n', 'plain']` |
| `t.__dict__["d"] = 99` then read | writing to `__dict__` skips `__set__`, but the data descriptor still wins on reads | `from Data 99` |
| `del t.n`, `t.n` | removes the instance value; the non-data descriptor shows again | `from NonData` |
| `del t.d` | `d` is a data descriptor, so Python looks for `Data.__delete__`; there is none | `AttributeError` |
| `Thing.d, Thing.n` | class access calls `__get__(None, Thing)` | `Data on class NonData on class` |
| `Thing.d = "replaced"`, `t.d` | the descriptor is replaced by a plain string, so the instance dict (99) wins now | `99` |
| `del t.d`, `t.d` | no descriptor any more, so `del` removes the instance entry; the class value shows | `replaced` |
| `del t.plain`, `t.plain, Thing.plain` | instance value removed | `class attr class attr` |

## Full output

```
from Data from NonData class attr
Data.__set__ 1
from Data 2 3
['n', 'plain']
from Data 99
from NonData
AttributeError
Data on class NonData on class
99
replaced
class attr class attr
```

## Complexity

Each read walks the class MRO once (to find a descriptor) and does one instance-dict lookup.

## Another way

Ask the objects directly: `hasattr(type(Thing.__dict__["d"]), "__set__")` tells you whether an
attribute is a data descriptor. Methods are non-data descriptors (functions have only
`__get__`), which is why you can shadow a method with an instance attribute, and `property` is a
data descriptor (it always has `__set__`), which is why you cannot shadow a property.
