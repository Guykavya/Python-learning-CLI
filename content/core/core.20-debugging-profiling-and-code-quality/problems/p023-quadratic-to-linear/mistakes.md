- **Building the set inside the loop** (`if x in set(b)`). That rebuilds it for every `x`, which
  is even slower than the list scan.
- **Returning `list(set(a) & set(b))`.** Fast, but the order is whatever the set gives, not the
  order of `a`.
- **Fixing the order with `key=a.index` or checking duplicates with `result.count(x)`.** Both are
  hidden list scans: the code looks short, but it is quadratic again.
- **Keeping only a set and no list.** Sets have no order you can rely on.
- **Sorting the result.** "Same results" includes order; sorting also fails for items of mixed
  types.
- **Measuring with tiny inputs.** With 10 items both versions take microseconds. The difference
  appears as the input grows, which is why the tests count work for growing inputs.
