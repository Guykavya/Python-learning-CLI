# Explain: bound, constraints or a plain union?

Three ways to say "this function takes an `int` or a `str`" look similar. They are not the same.

```python
from typing import TypeVar

A = TypeVar("A", int, str)             # constraints
B = TypeVar("B", bound=int | str)      # bound
# and no TypeVar at all:

def double_a(x: A) -> A:
    return x + x

def double_b(x: B) -> B:
    return x + x           # does the checker accept this?

def double_u(x: int | str) -> int | str:
    return x + x

class MyInt(int):
    pass
```

In `answer.md` (about 200 to 350 words), explain:

1. What does the checker infer for `double_a(5)`, `double_a("ab")`, and for the result of
   `double_u(5)`? Why is the union version weaker?
2. What happens when `double_a(MyInt(3))` is called (what is `A` solved as)? What would
   `double_b(MyInt(3))` give?
3. Why does the checker accept `x + x` in `double_a` but complain about the same line in
   `double_b` and (in a different way) in `double_u`? (Hint: how many times is the body checked
   for a constrained TypeVar?)
4. Give one situation for each: when you would choose a **bound**, when **constraints**, when
   a plain **union** (and no TypeVar).
