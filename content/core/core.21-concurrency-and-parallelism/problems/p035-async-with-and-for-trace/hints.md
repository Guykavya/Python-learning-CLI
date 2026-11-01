## Hint 1

Split the program into five parts: door `a`, door `b`, door `c`, the full `async for`, and the
`async for` with `break`. For each door ask two questions: what type reaches `__aexit__`, and
does `__aexit__` return `True` for it? A swallowed exception means the next line after the
`async with` block runs; a not-swallowed one jumps to the nearest `except`.

## Hint 2

For the generators, walk the body yourself:

```
numbers(2):  print yield 0 -> pause -> loop prints got 0
             print yield 1 -> pause -> loop prints got 1
             range ends -> print "generator finished" -> finally -> loop ends
numbers(5) with break at 1:
             ... got 1 -> break  (generator still paused at "yield 1"; finally NOT run)
             print "after break"
             await gen.aclose() -> GeneratorExit at the paused yield -> finally runs
             print "closed"
```
