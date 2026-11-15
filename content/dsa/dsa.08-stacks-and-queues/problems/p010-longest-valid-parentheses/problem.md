# Longest valid parentheses

`s` contains only `(` and `)`. Write `longest_valid(s)` that returns the **longest substring** of `s` (consecutive characters) whose parentheses are balanced. If there are several of the same maximum length, return the one that starts **first**. If there is none, return `""`.

The chapter (section 5, variant 3) computes only the **length** with a stack of indices and a sentinel `-1`. Here you also need to know **where** the best run starts.

## Example

```python
>>> longest_valid(")()())")
'()()'
>>> longest_valid("(()")
'()'
>>> longest_valid("()(())")
'()(())'
>>> longest_valid("())(())")
'(())'
>>> longest_valid("))((")
''
```

In `")()())"` the best run is from index 1 to index 4. In `"())(())"` there are runs `"()"` (length 2) and `"(())"` (length 4).

## Constraints

- `0 <= len(s) <= 10**5`; your solution must be `O(n)` (the last test uses 100,000 characters).
- The tests compare with a slow, obviously correct version on 1,500 random strings.

## Think about

When you pop a matching `(` at index `i`, the stack top is the index **just before** the current valid run. So the run starts at `stack[-1] + 1`. Why must you use `>` and not `>=` when you update the best run, to keep the earliest one on a tie?
