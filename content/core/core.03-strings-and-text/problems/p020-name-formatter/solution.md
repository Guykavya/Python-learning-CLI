## Approach

1. `split()` with no argument removes all the messy spacing and gives a list of words.
2. `words[0]` and `words[-1]` pick the first and last words, whatever is in between.
3. `capitalize()` gives "first letter upper, rest lower".
4. The initials are the first character of each fixed name.

## Code

```python
words = input().split()
first = words[0].capitalize()
last = words[-1].capitalize()
print(f"{last}, {first}")
print(f"Initials: {first[0]}.{last[0]}.")
```

## Why `capitalize()` and not `title()`

For `o'brien`, `title()` gives `O'Brien` and `capitalize()` gives `O'brien`. The task asks for `capitalize()`, so the output is predictable. Neither is right for every name; real systems let people type their own name exactly.

## Another way

`first, *middle, last = input().split()` unpacks the words directly. You will meet the `*` form with lists in core.05.
