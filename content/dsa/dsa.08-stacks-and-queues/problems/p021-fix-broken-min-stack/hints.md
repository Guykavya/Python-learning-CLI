## Hint 1

Trace it: after `push(5)`, `mins = [5]`. After `push(3)`, `mins = [5, 3]`. After the second `push(3)`, is `3 < 3`? What is `mins` now? Now `pop()` returns `3`: what does it do to `mins`?

## Hint 2

Every value that `pop` will remove from `mins` must have been pushed onto `mins`. An equal value must therefore be recorded again. Change one character in `push`: `x < self.mins[-1]` becomes `x <= self.mins[-1]`.
