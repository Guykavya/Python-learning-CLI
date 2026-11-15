## Approach

The stack holds the reduced prefix. A new character can only form a pair with the last surviving character, the top. If they are equal, both disappear (pop, and count a pair); this may expose an older character, which the next character can cancel with, exactly like the chain `abba` -> `aa` -> nothing.

## Code

```python
def remove_duplicates(s):
    stack = []
    pairs = 0
    for ch in s:
        if stack and stack[-1] == ch:
            stack.pop()
            pairs += 1
        else:
            stack.append(ch)
    return ("".join(stack), pairs)
```

## Complexity

`O(n)` time and `O(n)` memory. Every character is pushed at most once and popped at most once. The number of pairs is also `(len(s) - len(result)) // 2`, so you could compute it at the end.

## Another way

The "obvious" way repeats `s = s.replace(pair, "")` for every doubled letter until nothing changes. It is correct but each round copies the whole string, and a string like `"abc...cba"` needs one round per pair: `O(n^2)`.
