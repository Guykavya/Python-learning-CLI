## Approach

Track three dictionaries: `vars(c)`, `vars(Child)` and `vars(Base)`, plus `vars(Meta)`, which
only class reads can reach.

| print | Reasoning | Output |
|---|---|---|
| `Child.kind, Plain.kind` | Child's MRO reaches `Base.kind`; Plain's MRO has no `kind`, so the metaclass answers | `base meta` |
| `Child.describe(), Meta.describe(Plain)` | not in Child's MRO, found on Meta and bound to `Child`; the second is a plain function call | `class Child class Plain` |
| `hasattr(c, "describe"), hasattr(p, "kind"), hasattr(Plain, "kind")` | instance reads never search the metaclass; class reads do | `False False True` |
| `p.describe()` | same reason | `AttributeError` |
| `type(c).kind, c.kind` | both end at `Base.kind` | `base base` |
| after `c.kind = "instance"` | instance dict wins for `c`; classes unchanged | `instance base base` |
| after `c.shared.append(1)` | a read, then an in-place change of the class's list | `[1] False` |
| after `c.shared = [2]` | a write creates `vars(c)['shared']` | `[1] [2] True` |
| after `del c.kind` | instance entry gone, class value visible again | `base` |
| second `del c.kind` | `del` looks only in `vars(c)`, which has no `kind` now | `AttributeError` |
| after `Child.kind = "child"` | `vars(Child)` shadows `Base.kind` for Child and its instances | `child base child` |
| after `del Child.kind` | back to `Base.kind` | `base base` |
| `type(Child), type(Meta), type(c)` | Child's class is Meta; Meta's class is type | `Meta type Child` |
| `"describe" in vars(Meta)`, `... vars(Child)`, `"kind" in vars(Child)` | describe lives only in Meta; Child's `kind` was deleted | `True False False` |
| `Plain.describe is / == Plain.describe` | each read builds a new bound method; equal because same `__func__` and `__self__` | `False True` |
| `Plain.describe.__self__ is Plain` | bound to the class | `True` |

## Complexity

Not applicable (a trace). The lesson: `obj.x` and `type(obj).x` can differ, and metaclass
attributes are visible from classes only.

## Another way

Check any line yourself with `vars()` and `type(...).__mro__`. To see where a name is found,
loop over the MRO: `[k.__name__ for k in type(c).__mro__ if "kind" in vars(k)]`.
