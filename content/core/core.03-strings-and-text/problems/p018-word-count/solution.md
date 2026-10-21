## Code

```python
text = input()
print(f"Words: {len(text.split())}")
print(f"Spaces: {text.count(' ')}")
```

## Why not count spaces plus one?

"Spaces + 1" only works when there is exactly one space between words and none at the ends. The example has 8 spaces and 4 words.

## Why `split()` and not `split(" ")`

`"a  b".split(" ")` is `['a', '', 'b']`: three pieces for two words. And `"".split(" ")` is `['']`, one piece for no words. `split()` with no argument has neither problem.
