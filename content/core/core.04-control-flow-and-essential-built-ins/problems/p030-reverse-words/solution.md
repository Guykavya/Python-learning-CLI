## Approach

`reversed` works on any sequence: the list of words for line 1, each word's characters for
line 2.

## Code

```python
words = input().split()
if not words:
    print("(nothing)")
else:
    print(" ".join(reversed(words)))
    line = ""
    for word in words:
        backwards = ""
        for ch in reversed(word):
            backwards += ch
        line += backwards + " "
    print(line.strip())
```

## Why not just reverse the whole line

`"I love Python"[::-1]` is `"nohtyP evol I"`: both effects at once. The task asks for each
effect separately.

## Another way

Slicing: `word[::-1]` reverses a word, `words[::-1]` reverses the list. Both are common.
`reversed` does not build a copy, which matters for long sequences.
