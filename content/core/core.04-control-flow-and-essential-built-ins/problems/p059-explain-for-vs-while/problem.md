# Choosing for or while

Write an explanation in `answer.md`, for a classmate who writes every loop as a `while` loop
with a counter, like this:

```python
i = 0
while i < len(word):
    print(word[i])
    i += 1
```

Cover:

1. What a `for` loop does that this `while` loop does by hand, and the three things the
   `while` version must get right that `for` gets right automatically.
2. Rewrite the example with `for`, and again with `enumerate` if the position is needed.
3. Two kinds of task where `while` is genuinely the right choice, with a short example of each.
4. Why `range` excludes its stop, and how that helps avoid off-by-one errors.
5. A simple rule of thumb for choosing.
