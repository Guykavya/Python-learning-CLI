## Walkthrough

- `enumerate(word, start=10)` gives `10 s`, `11 p`, `12 a`, `13 m`.
- `zip("abc", range(1, 10))` stops after 3 pairs: `('a', 1)`, `('b', 2)`, `('c', 3)`.
- `list(pairs)` is `[]`: the `for` loop already used the iterator up.
- `zip("hello", reversed("hello"))` pairs h-o, e-l, l-l, l-e, o-h. Only the middle pair
  matches: `mirror l`.
- `next(e)` takes `(0, 'x')`. The loop continues from where the iterator is: `loop 1 y`.
- `zip()` with no arguments gives nothing: `[]`.
- `range(0, 10, 4)` is 0, 4, 8; reversed: `[8, 4, 0]`.
- `enumerate(..., 1)` starts at 1: `1 ac`, `2 bd`.
