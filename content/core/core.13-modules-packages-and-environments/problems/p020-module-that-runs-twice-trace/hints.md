## Hint 1

When `python counter.py` starts, which name does the running module get in `sys.modules`? When
`helper.py` says `import counter`, does Python find `"counter"` in `sys.modules`?

## Hint 2

There are two separate module objects made from the same file: `__main__` and `counter`. Each has
its own `hits` list. Count the lines:

```text
run counter.py as __main__       -> prints "loading counter as __main__"
  import helper                  -> helper first does import counter
      counter.py runs again       -> prints "loading counter as counter" (the if block is skipped)
  helper prints "loading helper"
  hit("main")  uses __main__.hits
  helper.go()  uses counter.hits (twice)
```
