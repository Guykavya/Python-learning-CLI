# Lookbehind: pull out prices in rupees

A shopping message says *"Shirt ₹499, jeans Rs. 1,299.50, delivery Rs.40. Total about $25."*
You want the rupee amounts as numbers. A **lookbehind** `(?<=...)` checks what comes *before*
the current position without making it part of the match, so `findall` returns only the
number, never the symbol.

Write `prices(text: str) -> list[float]` in `solution.py`.

- A price is a number written **directly after** one of these four markers:
  `₹`, `₹ ` (with one space), `Rs.`, `Rs. ` (with one space). `Rs.` is case-sensitive.
- The number starts with a digit and continues with digits and commas (Indian `1,20,000` or
  Western `120,000` grouping, both fine), optionally followed by a decimal point and one or
  more digits.
- A full stop or comma **after** the number that is not followed by a digit is punctuation, not
  part of the number: `Rs.40.` is `40.0`, `₹499, jeans` is `499.0`.
- Remove the commas and return the amounts as `float`s, in order.
- Numbers without a rupee marker (`$25`, `3 shirts`) are ignored.

**Example**

```python
prices("Shirt ₹499, jeans Rs. 1,299.50, delivery Rs.40. Total about $25.")
# [499.0, 1299.5, 40.0]
prices("₹ 1,20,000 only")   # [120000.0]
prices("2 items for 300")   # []
```

**Watch out:** Python's lookbehind must have a **fixed width**. `(?<=₹|Rs\.)` raises
`re.error` because the two choices have different lengths. How can you get around that?
