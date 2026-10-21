## Approach

A search with an early exit. `enumerate` supplies the position; `break` stops at the first
match; the loop's `else` handles "not found".

## Code

```python
word = input().strip()
for pos, ch in enumerate(word):
    if ch.lower() in "aeiou":
        print(f"First vowel '{ch}' at position {pos}")
        break
else:
    print("No vowels")
```

## Why `break` matters

Without it, the loop would print every vowel, not just the first. And the `else` depends on
it: the `else` runs only when the loop finished without `break`, which means "no vowel".

## Another way

A flag variable `found = False`, set to `True` before `break`, and `if not found:` after the loop.
