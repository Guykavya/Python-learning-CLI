# When is `apply` the right answer?

Chapter sections 15.1 to 15.5. Three ways to add 18% tax to the prices of a table are a Python loop, `Series.apply`
and one array expression. A learner says: "`apply` is pandas, so it must be fast." Another says: "Never use `apply`."
Both are wrong in a useful way.

```python
prices = df["unit_price"]
a = prices.apply(lambda p: p * 1.18)    # calls a Python function once per row
m = prices.map(zone_dict)               # a look-up
v = prices * 1.18                       # one vectorised operation
```

Explain in `answer.md`, in about 200 to 300 words:

1. What does `apply` really do for each row, and why is it slow on a big table? Compare it with the vectorised line.
2. What is `map` good for, and what happens to a key that is not in the dictionary?
3. Describe **one concrete case** where `apply(axis=1)` (or a Python function per row) is the right answer, and say
   what you would still do to keep it safe.
4. What is the order of things to try?

## Example

A start: "`apply` hides the loop, it does not remove it. For every row pandas builds a small object, calls my Python
function and collects the results, so the cost grows with the number of rows times the cost of a Python call..."
