## Approach

`product(sizes, colours)` is the same as two nested `for` loops, with `sizes` outside. It yields
pairs lazily. For each pair we skip the unavailable ones and yield the code in upper case.

The parameter is called `product`, and so is the itertools function. If you write
`from itertools import product`, the parameter **hides** the function inside `sku_codes`.
So import the module instead (`import itertools`) or import the function under another name.

## Code

```python
import itertools


def sku_codes(product, sizes, colours, unavailable=()):
    for size, colour in itertools.product(sizes, colours):
        if (size, colour) in unavailable:
            continue
        yield f"{product}-{size}-{colour}".upper()
```

## Complexity

O(len(sizes) * len(colours) * u) time, where u is the length of `unavailable`
(a `set(unavailable)` at the start makes each check O(1)). The generator itself needs O(1) memory.

## Another way

A generator expression:

```python
return (f"{product}-{s}-{c}".upper()
        for s, c in itertools.product(sizes, colours)
        if (s, c) not in unavailable)
```

A function that **returns** a generator expression is also lazy.
