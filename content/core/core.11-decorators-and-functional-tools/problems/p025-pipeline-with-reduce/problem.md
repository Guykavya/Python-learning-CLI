# Build a pipeline of functions with reduce

A **pipeline** passes a value through a list of steps: the output of one step is the input of
the next. Write `pipeline(*funcs)` in `solution.py`. It returns a **new function** of one
argument that runs the steps **from left to right**.

Rules:

1. `pipeline(f, g, h)(x)` is `h(g(f(x)))`. The first function listed runs first.
2. `pipeline()` with no steps returns a function that gives back its input unchanged.
3. Check the steps **when the pipeline is built**: if any step is not callable, raise
   `TypeError` at once, not later at the first use. (`callable(x)` tells you if `x` can be called.)
4. Building the pipeline must not call any step.
5. The pipeline can be used many times, and a pipeline can be a step in another pipeline.
6. Use `functools.reduce` to apply the steps.

**Example**

```python
clean = pipeline(str.strip, str.lower, str.split)
clean("  Hello World ")      # ["hello", "world"]

count_words = pipeline(clean, len)
count_words(" a b c ")      # 3

pipeline()(42)              # 42
pipeline(len, "oops")       # TypeError: the second step is a string, not a function
```
