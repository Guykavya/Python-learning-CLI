## Approach

Write the decorator stack as one expression:

```python
word = tag("b")(twice(2)(tag("i")(word)))
```

**Factory time.** The decorator expressions are evaluated top to bottom, before anything is
applied: `make tag b`, `make twice 2`, `make tag i`.

**Decoration time.** Decorators are applied bottom to top, closest to the function first:

- `tag("i")` gets the real `word`: `wrap i around word`. Thanks to `wraps`, its wrapper is also
  named `word`.
- `twice(2)` gets that wrapper, which is named `word`: `wrap twice around word`. `twice` does
  **not** use `wraps`, so its wrapper keeps the name `wrapper`.
- `tag("b")` gets the `twice` wrapper: `wrap b around wrapper`. `wraps` copies that name, so the
  final function is called `wrapper`: `defined wrapper`.

**Call time.** `word("hi")` runs the outermost layer first:

- `b in ('hi',)` (`args` is a tuple with one item, so it prints with a trailing comma).
- `twice in ('hi',)`, then twice: `i in ('hi',)`, `body hi`, `i out HI`. The inner `tag` returns
  `<i>HI</i>`.
- `twice` returns the list of the two results. `tag("b")` prints `b out [...]` with that list and
  returns it wrapped in `<b>...</b>`, which the final `print` shows.

## Output

```text
start
make tag b
make twice 2
make tag i
wrap i around word
wrap twice around word
wrap b around wrapper
defined wrapper
b in ('hi',)
twice in ('hi',)
i in ('hi',)
body hi
i out HI
i in ('hi',)
body hi
i out HI
b out ['<i>HI</i>', '<i>HI</i>']
<b>['<i>HI</i>', '<i>HI</i>']</b>
```

## Complexity

The body runs `times` = 2 times per call; each layer adds O(1) work.

## Another way

Add `@wraps(func)` to `twice` and run it again. Now the third decoration line becomes
`wrap b around word` and the final name is `word`. One missing `wraps` in the middle of a stack
loses the name for every decorator above it.
