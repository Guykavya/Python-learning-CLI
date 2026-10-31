## Approach

1. `import a` runs `a.py`, which imports `registry` (prints `registry runs`) and calls `add("a")`:
   items `['a']`, count `1`.
2. `import b`: `registry` is cached, so nothing prints. `b` copies three bindings: `items` (the same
   list), `count` (the int `1`) and `add`. `add("b")` changes the shared list and makes
   `registry.count` 2. `items.append("b2")` changes the same list. `count += 100` only rebinds
   `b.count` to `1 + 100 = 101`.
3. `import registry` and the second `import a` are cache hits: nothing runs, nothing prints.
4. `main` sees the shared list `['a', 'b', 'b2']` and `registry.count` 2. `b.count` is 101, and the
   lists are the same object.
5. `reload` runs `registry.py` again in the same module object: `registry runs`, a new empty list,
   count 0. `add("c")` gives `['c']` and 1.
6. `b.items` still points at the old list. `b.add` is the old function, but a function looks up its
   globals by name at call time in its module's dictionary, which is the same dictionary that now holds
   the new list. So `b.add("d")` appends to the new list.

## Output

```text
registry runs
a sees ['a'] 1
b sees ['a', 'b', 'b2'] 101
main sees ['a', 'b', 'b2'] 2
b.count = 101 | same list? True
registry runs
after reload: ['c'] 1
b still has ['a', 'b', 'b2'] | same list? False
b.add went to ['c', 'd'] | b.items is ['a', 'b', 'b2']
```

## Complexity

Not applicable.

## Another way

The lesson for real code: to share changing state between modules, use `import registry` and
always write `registry.items` / `registry.count`. A `from registry import count` gives you a frozen copy of
the value at import time, and `reload` breaks every `from`-imported name. Avoid `reload` outside an
interactive session.
