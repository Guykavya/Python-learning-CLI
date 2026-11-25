## Hint 1

Count the Python function calls: how many does `prices.apply(f)` make for 200,000 rows, and how many does `prices * 1.18` make? What does NumPy do instead of calling a function per row?

## Hint 2

```text
1. apply -> one Python call per row (axis=1: also one Series object per row); vectorised -> one C loop
2. map -> look-up in a dict; missing key -> NaN -> count or fill them
3. a case: a code parser with branches / a one-value library function; precautions: try .str first, test on a slice, check output
4. order: vectorised > map > apply > loop; measure
```
Write a short paragraph for each numbered question.
