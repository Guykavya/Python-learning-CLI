# Reverse a string with a stack

Write `reverse_string(s)` that returns `s` reversed, **using a Python list as a stack** (chapter section 2, "Reversing with a stack"):

1. push every character of `s` onto the stack with `append`;
2. pop them all with `pop` and join them in the order they come off.

Because a stack is **last in, first out**, the last character you pushed is the first one you get back. Do not use slicing `s[::-1]`, `reversed` or `.reverse()`: the point is to see the stack do the work.

## Example

```python
>>> reverse_string("stack")
'kcats'
>>> reverse_string("")
''
>>> reverse_string("a")
'a'
```

## Constraints

- `0 <= len(s) <= 10**5`
- `s` may contain any characters, including spaces, accented letters and emoji.

## Think about

Why does the order come out reversed? Write the stack after pushing `"abc"` and then after each pop.
