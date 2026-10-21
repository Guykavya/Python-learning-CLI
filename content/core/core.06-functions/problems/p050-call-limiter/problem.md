# Allow only N calls

Write `limit_calls(func, max_calls)` that returns a **wrapper** function. The wrapper accepts any
arguments and:

- for the first `max_calls` calls, calls `func` with exactly those arguments and returns its
  result;
- after that, does **not** call `func` at all and returns `None`.

Separate wrappers have separate limits.

**Example**

```python
def greet(name, punct="!"):
    return "Hi " + name + punct

g = limit_calls(greet, 2)
g("Asha")                  # 'Hi Asha!'
g("Ravi", punct="?")       # 'Hi Ravi?'
g("Meena")                 # None   (greet is not called)
```
