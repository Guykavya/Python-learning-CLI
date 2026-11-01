## Approach

Track the instance dictionaries and the class dictionary. Reads look in the instance first and
fall back to the class. Writes and deletes only ever touch the instance.

| Line | Reasoning | Output |
|---|---|---|
| `a.kind, b.kind` | neither instance has `kind`, both read `Dog.kind` | `canine canine` |
| after `a.kind = "wolf"` | the write goes into `vars(a)`; `b` and `Dog` unchanged | `wolf canine canine` |
| `vars(a)` | `name` from `__init__`, then the new `kind` | `{'name': 'Rex', 'kind': 'wolf'}` |
| after `del a.kind` | removes the instance entry, the class value shows again | `canine {'name': 'Rex'}` |
| after `a.tricks.append("sit")` | a **read** of `a.tricks` finds the class list; `append` changes that single shared list | `['sit'] ['sit']` |
| after `b.tricks = ["roll"]` | an assignment: `b` gets its own list, which shadows the class list for `b` only | `['sit'] ['roll'] ['sit']` |
| `sorted(vars(b))` | keys of `b`'s dict | `['name', 'tricks']` |
| after `Dog.kind = "dog"` | neither instance has its own `kind` now, both see the new class value | `dog dog` |
| `"kind" in vars(a)`, `"kind" in vars(Dog)` | the instance has none, the class has one | `False True` |
| second `del a.kind` | `del` on an instance only looks at the instance dict, which has no `kind` | `AttributeError` |
| `hasattr(a, "tricks")`, `"tricks" in vars(a)` | readable (from the class) but not stored on `a` | `True False` |

## Full output

```
canine canine
wolf canine canine
{'name': 'Rex', 'kind': 'wolf'}
canine {'name': 'Rex'}
['sit'] ['sit']
['sit'] ['roll'] ['sit']
['name', 'tricks']
dog dog
False True
AttributeError
True False
```

## Complexity

Each lookup checks at most the instance dict and the class (and its bases): O(1) dictionary
lookups per class in the MRO.

## Another way

Check yourself by printing `vars(a)`, `vars(b)` and `{k: v for k, v in vars(Dog).items() if not k.startswith("__")}`
after every line. The fix for the shared `tricks` list is the usual one: create the list in
`__init__` (`self.tricks = []`) so every dog gets its own.
