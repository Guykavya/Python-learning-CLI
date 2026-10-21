## Approach

Each column depends only on its own two words, so a single `zip` loop can compute the width
and build both output lines at the same time.

## Code

```python
top = input().split()
bottom = input().split()
if len(top) != len(bottom):
    print("Lines have different word counts")
else:
    line1 = ""
    line2 = ""
    for a, b in zip(top, bottom):
        width = max(len(a), len(b))
        line1 += (f"{a:>{width}}" if a.isdigit() else f"{a:<{width}}") + "  "
        line2 += (f"{b:>{width}}" if b.isdigit() else f"{b:<{width}}") + "  "
    print(line1.rstrip())
    print(line2.rstrip())
```

## Why `rstrip()` at the end

Every column adds two separator spaces, and the last word may be padded. `rstrip()` removes
trailing spaces only, keeping the alignment inside the line.

## Why one loop is enough

The width of column `k` needs only `top[k]` and `bottom[k]`. If the task had many lines, you
would need one pass to find widths and a second to print; that needs lists of widths, from
the next chapter.
