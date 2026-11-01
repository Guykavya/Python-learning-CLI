- Replacing `range(len(a))` with `range(len(a))` inside a helper or a variable (`n = len(a)`): the
  habit stays. Loop over the items instead.
- Using `zip` but forgetting it stops at the shorter list: that is the wanted behaviour here, so no
  extra `min(len(a), len(b))` is needed.
- `enumerate(lines)` without `start=1`: the numbers are off by one.
- `any([n < 0 for n in numbers])` with square brackets builds the whole list first and cannot stop early.
  Drop the brackets.
- Writing `return True if x else False` around `any(...)`. `any` already returns a bool.
- Keeping a `for` loop and only renaming the flag variable. The goal is to say "any" or "sum" directly.
