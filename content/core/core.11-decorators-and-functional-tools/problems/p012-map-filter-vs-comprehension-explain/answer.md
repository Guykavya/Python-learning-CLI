**1. Same result.** `filter(pred, nums)` keeps only the items where `pred(item)` is true: here 2, 4 and 6.
`map(f, items)` calls `f` on each item and gives the results: 4, 16 and 36. `list(...)` collects them. The
comprehension `[n * n for n in nums if n % 2 == 0]` does the same two steps in one expression: the `if`
part is the filter, and the expression at the front is the map.

**2. Why `[]` the second time.** `map` and `filter` do not build a list. They return **lazy iterators**:
each value is computed only when someone asks with `next()`. The first `list(squares)` pulls every value
and moves the iterator to its end. The second `list(squares)` finds nothing left, so it is empty, just like
a used-up generator. A list comprehension, in contrast, builds a real list that you can loop over many times.

**3. Which to use.** If you already have a named function, `map` is short and clear:
`map(str.strip, words)` reads as "strip every word". When you would need a `lambda`, or you combine a
transform and a condition, the comprehension is easier to read, because it shows the expression and the
condition directly, with no extra function. Rule of thumb: use `map`/`filter` with an existing function
name; use a comprehension when you would have to write `lambda`. If you only loop once over a big input,
the lazy `map` or a generator expression `(n * n for n in nums)` also saves memory.
