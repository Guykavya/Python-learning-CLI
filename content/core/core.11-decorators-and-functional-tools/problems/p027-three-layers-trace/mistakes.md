- Printing `make tag i` before `make tag b`. The decorator **expressions** are evaluated top to
  bottom; only the **application** goes bottom to top.
- Printing the `wrap ...` lines top to bottom. The decorator nearest to `def` is applied first.
- Writing `wrap b around word`. `tag("b")` receives the `twice` wrapper, which is named
  `wrapper` because `twice` does not use `wraps`.
- Writing `defined word`. `wraps` copies the name of the function it wraps, and that function
  was already named `wrapper`.
- Writing `b in ('hi')` or `b in hi`. `args` is a tuple; a one-item tuple prints as `('hi',)`.
- Printing `body hi` only once. `twice` calls the inner function two times.
- Putting `b out` before the second `i in`. The outer wrapper waits until `twice` has finished both calls.
