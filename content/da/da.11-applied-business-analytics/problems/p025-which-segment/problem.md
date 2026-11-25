# Which segment?

Chapter section 5.3. The segment rules are checked **in order**: the first one that matches wins. That makes the order part of the definition.

```python
def segment(r, f):
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "New / promising"
    if r <= 2 and f >= 3:
        return "At risk"
    if r <= 2 and f <= 2:
        return "Hibernating"
    return "Needs attention"


for r, f in [(5, 4), (4, 3), (3, 3), (3, 2), (4, 2), (2, 3), (2, 2), (3, 1)]:
    print(f"({r}, {f}) {segment(r, f)}")
```

Hand-trace the program, then write **every line it prints**, in order, in `answer.txt`. Do not run the code before you have written your answer.

## Example

`(5, 5)` would print `(5, 5) Champions`.

## After you answer

- Why is `(4, 3)` a Loyal customer and not "New / promising"?
- Which two pairs fall through to "Needs attention", and what do they have in common?
