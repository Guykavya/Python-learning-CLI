## Approach

Walk along the shortest word. At each position, ask whether every word agrees. Stop at the
first disagreement.

## Code

```python
words = input().split()
if not words:
    print("No words")
else:
    shortest = min(words, key=len)
    for i, ch in enumerate(shortest):
        if not all(w[i] == ch for w in words):
            prefix = shortest[:i]
            break
    else:
        prefix = shortest
    print(f"Prefix: {prefix if prefix else '(none)'}")
    print(f"Length: {len(prefix)}")
```

## Why the shortest word

Every word has at least `len(shortest)` characters, so `w[i]` is always safe. Walking a longer
word would index past the end of the short ones.

## Why the loop `else` is natural here

The loop is a search for the first disagreement. Not finding one (no `break`) means the
whole shortest word is shared. That is exactly "else runs when the loop did not break".

## Another way

Start with `prefix = words[0]` and, for each other word, shorten the prefix with a `while`
loop until the word starts with it (`w.startswith(prefix)`). It is correct but does more work.
