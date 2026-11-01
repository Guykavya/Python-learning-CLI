## Hint 1

Draw each cell as a small box. For every call of an outer function, ask: how many boxes does
this call create, and which inner functions point at them? Then read every line with these
questions:

- Is the name assigned in this function *and* used by an inner function? Then it is a cellvar here.
- Is it used here but assigned in an enclosing function? Then it is a freevar here, even if this
  function only passes it on to a deeper function.
- A loop does not create a new variable on each turn. How many `n` boxes does one call of
  `make_adders` create? What is in that box when the loop ends?

## Hint 2

```
make_counter():  count -> cell (step uses it)      => cellvars ('count',), freevars ()
step:            reads count from the cell         => freevars ('count',)
each make_counter() call -> a NEW cell; c and d never share one
cell_contents = 100 -> the next c() returns 101

outer(x): x is a cell (inner needs it)
middle:   does not use x itself, but must carry it to inner => freevars ('x',), cellvars ()

make_adders: one cell for n, shared by all three lambdas; after the loop n == 2
fixed version: n=n copies the CURRENT value into a default; no closure at all

early: the cell exists before `later` is assigned, but it is empty
    reading cell_contents -> ValueError, calling show() -> NameError
```
