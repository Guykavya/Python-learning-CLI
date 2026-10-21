## Approach

- `strip()` removes whitespace at the ends and leaves the middle alone.
- `split()` with no argument splits on runs of whitespace and drops empty pieces. Joining the pieces with `" "` gives exactly one space between words.

## Code

```python
text = input()
print(f"[{text.strip()}]")
print(f"[{' '.join(text.split())}]")
```

## Why not `replace("  ", " ")`?

`replace` makes one pass. Four spaces become two, not one, and tabs are not touched at all. `split()` handles any amount and any kind of whitespace in one step.

## Another way

There is no single built-in method for collapsing spaces. `" ".join(text.split())` is the standard idiom; you will see it in real code.
