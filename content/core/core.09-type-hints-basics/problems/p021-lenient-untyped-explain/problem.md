# Explain: mypy passed, so is it safe?

Nisha runs `python -m mypy shop.py` and gets:

```text
Success: no issues found in 1 source file
```

Here is `shop.py`:

```python
def apply_discount(price, percent):
    return price - price * percent / 100


def total(prices: list[float]) -> float:
    return sum(prices)


def average(prices: list[float]) -> float:
    return total(prices) / len(prices)


print(apply_discount("100", 10))
print(average([]))
```

She says: "mypy passed, so this file is safe." Both of those last two lines crash.

In `answer.md` (about 120 to 250 words), explain:

1. Why does mypy not report `apply_discount("100", 10)`? (Look at which functions have hints.)
2. Which mypy option would force Nisha to annotate every function, and what would she have to
   add to `apply_discount` for mypy to catch the bad call?
3. Why does mypy not report `average([])` even though it crashes? What kind of mistake is that,
   and which other tools from this course catch it?
4. Name two ways of switching mypy's checking off for a spot on purpose, and say why they are
   risky.
