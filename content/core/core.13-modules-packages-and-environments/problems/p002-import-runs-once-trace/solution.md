## Approach

The first `import counter` finds `counter.py`, creates a module object, stores it in
`sys.modules["counter"]`, and runs the file top to bottom: `loading counter` is printed and `count = 0`.
`add()` returns 1.

The second `import counter` finds `"counter"` in `sys.modules` and just binds the name again. Nothing is
printed and `count` keeps its value, so `add()` returns 2. The cache entry is the same object as our name,
so both checks print `True`.

`importlib.reload(counter)` runs the source again **in the same module object**. The print appears
again, and `count = 0` resets the counter. `reload` returns that same object, so `counter is old` is `True`.
The next `add()` returns 1.

## Output

```text
start
loading counter
1
2
True
True
loading counter
0
True
1
```

## Complexity

O(1).

## Another way

Add `print(id(counter))` after each import and after the reload. All three numbers are the same
(the numbers themselves differ on every machine).
