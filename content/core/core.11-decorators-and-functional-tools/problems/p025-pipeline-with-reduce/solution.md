## Approach

`reduce` walks through the steps and keeps one running value. The running value starts as the
input. For each step, the new running value is `step(old value)`. Passing the input as the third
argument of `reduce` also makes the empty pipeline work: with no steps, `reduce` returns the
start value.

The check for callables happens in `pipeline`, before `run` is created, so the error appears
where the mistake was made.

## Code

```python
from functools import reduce


def pipeline(*funcs):
    for step in funcs:
        if not callable(step):
            raise TypeError(f"pipeline step {step!r} is not callable")

    def run(value):
        return reduce(lambda acc, step: step(acc), funcs, value)
    return run
```

## Complexity

Building is O(k) for k steps. Each run is O(k) calls plus the cost of the steps themselves.

## Another way

A plain loop:

```python
def run(value):
    for step in funcs:
        value = step(value)
    return value
```

It does the same thing and many people find it easier to read. `reduce` shines when you think
of the job as "fold a list into one value", which is exactly what a pipeline is.
Right-to-left composition (`compose(f, g)(x) == f(g(x))`) is the same code over `reversed(funcs)`.
