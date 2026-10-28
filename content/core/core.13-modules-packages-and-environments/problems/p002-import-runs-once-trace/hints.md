## Hint 1

The first `import counter` runs every line of `counter.py`. Where does Python store the finished module,
and what does it check first on the second `import counter`?

## Hint 2

Walk it in order: first import prints `loading counter` and sets `count = 0`. Two `add()` calls give 1 and 2,
and the second import prints nothing. `reload` runs the file **again inside the same module object**: the
print happens again and `count` is set back to 0. Is the object new or the same one?
