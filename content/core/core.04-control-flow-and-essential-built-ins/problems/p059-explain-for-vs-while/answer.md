**What `for` does for you.** A `for` loop asks the sequence for its items one by one (through
`iter()` and `next()`) and stops by itself when they run out. The `while` version does that by
hand, so it has three chances to go wrong:

1. **Start** the counter at the right value (`i = 0`, not 1).
2. **Compare** correctly (`<`, not `<=`, which would crash with `IndexError` on the last step).
3. **Increase** the counter, in the right place (forget it and the loop never ends).

A `for` loop has none of these moving parts.

**Rewrites.**

```python
for ch in word:
    print(ch)

for i, ch in enumerate(word):     # when the position is needed
    print(i, ch)
```

**When `while` is right.** When you cannot know the number of iterations before you start:

```python
# Reading until a sentinel: how many lines? Unknown.
while True:
    line = input()
    if line == "done":
        break
    ...

# Repeating until a condition changes: how many halvings? Depends on n.
steps = 0
while n > 1:
    n //= 2
    steps += 1
```

Other examples: asking until the input is valid, and walking two sequences at different
speeds (as in merging two sorted lines), where each step moves only one of two positions.

**Why `range` excludes its stop.** `range(a, b)` has exactly `b - a` numbers, `range(n)` has
exactly `n`, and `range(len(s))` gives exactly the valid positions of `s` (0 to len - 1).
Ranges also join without overlap: `range(0, 5)` then `range(5, 10)`. When you need 1 to n
inclusive, write `range(1, n + 1)` once, deliberately, instead of fiddling with `<` and `<=`
in a `while` condition.

**Rule of thumb.** If you can say *what* you are looping over (these characters, these
words, these numbers), use `for`. If you are looping *until something happens*, use `while`.
And if you catch yourself writing `i = 0 ... while i < len(x) ... i += 1`, that is a `for`
loop written the long way.

Key ideas to check: three manual steps; for and enumerate rewrites; sentinel and
until-condition examples; half-open range benefits; the rule of thumb.
