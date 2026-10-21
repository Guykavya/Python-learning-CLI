## Hint 1

`input().split()` gives a list of words. Which index is always the first? Which negative index is always the last?

## Hint 2

`words[0]`, `words[-1]` and `words[len(words) // 2]`.

## Hint 3

`words[::-1]` is a reversed copy. Join it back into text with `" ".join(...)`.
