## Hint 1

The prefix can never be longer than the **shortest** word. Which word should you walk through?

## Hint 2

For position `i` and character `ch` of the shortest word, the prefix continues only if every
word has `ch` at position `i`: `all(w[i] == ch for w in words)`.

## Hint 3

`break` at the first position where `all(...)` is false: the prefix is `shortest[:i]`. If the
loop never breaks, the whole shortest word is the prefix: that is the loop's `else`.
