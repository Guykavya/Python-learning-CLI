## Approach

Greedy scan with a counter of open brackets. A `)` closes an open `(` if there is one; if not, it is unmatched and needs an inserted `(`. The `(` still open at the end each need an inserted `)`. These two kinds of fixes are independent, so the minimum is exactly the two counts.

## Code

```python
def brackets_to_add(s):
    opens = 0              # ( we must insert
    open_count = 0         # ( that are open right now
    for ch in s:
        if ch == "(":
            open_count += 1
        elif open_count:
            open_count -= 1
        else:
            opens += 1
    return (opens, open_count)
```

## Complexity

`O(n)` time, `O(1)` memory.

## Another way

With a stack you would push each `(` and pop on `)`; an empty stack at a `)` counts one insert, and the final stack size is the other count. It works, but the stack only ever holds `(`, so its length is all you use: the counter is the stack with the contents thrown away. Bonus: the repaired string `"(" * opens + s + ")" * closes` is always balanced.
