## Hint 1

How many times does `registry.py` run before the reload? `a` is imported twice in `main.py`; does the
second `import a` print anything?

When `b.py` runs `from registry import items, count, add`, what is `registry.count` at that moment?
After `count += 100` in `b`, which module's `count` changed?

## Hint 2

Keep a small table:

```text
registry.items -> L1 (a list),  registry.count -> int
b.items        -> L1 (same list),  b.count -> its own int
b.add          -> the old function; it looks up items/count in registry's globals dict
```

`reload` makes `registry.items` a new empty list L2 and `registry.count` 0, in the **same**
globals dict. `b.items` still points at L1. The old function `b.add` reads `items` from that globals
dict at call time, so which list does it append to now?
