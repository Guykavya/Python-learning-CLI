# Explain: why a quality pipeline?

Your team lead proposes this for every Python repository:

```text
on every commit (pre-commit):   ruff check --fix  ->  ruff format  ->  mypy
on every push (CI server):      the same three    ->  pytest with coverage
```

A teammate objects: "That's four tools doing the same job. The tests already prove the code
works. Just run pytest."

Here is a small file to think with. **Each numbered line has a different problem.**

```python
import os                                   # 1
from typing import Optional


def average(values: list[int]) -> float:
    return sum(values) / len(values)        # 2


def find(users: dict[str, int], name: str) -> Optional[int]:
    return users.get(name)


def describe(users, name):
    age: int = find(users, name)            # 3
    try:
        return "adult" if age >= 18 else "child"
    except:                                 # 4
        return "unknown"


def total_price(prices):
    return sum(prices)*1.18                 # 5   (18% tax; prices in rupees)
```

Write `answer.md` (about 400 to 600 words) that answers:

1. For each of the numbered lines 1 to 5, which tool in the pipeline would **report** it (ruff
   lint, ruff format, mypy, pytest, or none), and why. Assume the ruff rules `E, F, W, I, B, UP`,
   `mypy --strict`, and tests that call each function with normal inputs.
2. What does **each** tool catch that the others cannot, and what does each one **miss**? Make
   at least one point per tool, including what tests catch that no static tool can.
3. Why this **order**: fixers (ruff --fix, format) before the type checker, and the slow test
   suite last / on the CI server rather than on every commit?
4. What is the **cost** of the pipeline (time per commit, false alarms, setup) and how do teams
   keep it low? Answer the teammate in one or two sentences at the end.

**Example of the level of detail expected** (for a line that is not in the file):

> `def f(x=[]):` is reported by **ruff** (B006, mutable default). mypy is happy because the type
> is fine, and tests only catch it if one of them calls `f` twice and notices the shared list.
