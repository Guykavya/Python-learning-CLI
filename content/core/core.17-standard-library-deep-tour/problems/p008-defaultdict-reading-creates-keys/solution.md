## Walkthrough

1. `stock["apple"] += 3` reads `stock["apple"]` (missing, so `int()` gives 0 and it is stored), then writes 3. Output `1 {'apple': 3}`.
2. `if stock["pear"] > 0:` is "only looking", but `stock["pear"]` is a `d[key]` read: `pear` is created with 0. The test is false, nothing printed. Output `2 {'apple': 3, 'pear': 0}`.
3. `in` and `.get()` never call the default factory: `False None 2`.
4. `groups` gets `a: [ant, ape]` and `b: [bee]`. Then `groups["c"]` creates `c: []` and returns it: `[] 3`.
5. The repr shows all three keys in insertion order, including the empty `c`.
6. `counts[key]` for `y` and `z` creates both with 0. `total` is 1 + 0 + 0 = 1, and the keys are now `['x', 'y', 'z']`.
7. `plain` is an ordinary dict copy; `plain.get("w", "missing")` returns the default. `"w" in counts` is `False`: neither line creates anything.
8. With `default_factory = None` a missing key is no longer filled in: `counts["w"]` raises `KeyError('w')`, printed as `KeyError 'w'`.
9. The loop starts with `k = "a"` and reads `seen["a!"]`, which **adds** a key. When the loop asks for the next key, the dict has changed size: `RuntimeError`. Only `a!` was added, so `['a', 'b', 'a!']`.

## The exact output

```text
1 {'apple': 3}
2 {'apple': 3, 'pear': 0}
False None 2
[] 3
defaultdict(<class 'list'>, {'a': ['ant', 'ape'], 'b': ['bee'], 'c': []})
1 ['x', 'y', 'z']
missing False
KeyError 'w'
RuntimeError: dictionary changed size during iteration
['a', 'b', 'a!']
```

**Lesson:** on a defaultdict, use `key in d` or `d.get(key)` when you only want to look. Return
`dict(d)` to callers, and never index a dict you are looping over unless you are sure the key exists.
