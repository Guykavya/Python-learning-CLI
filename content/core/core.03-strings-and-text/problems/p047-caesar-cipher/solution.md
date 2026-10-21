## Approach

1. `% 26` turns any shift into the range 0 to 25. In Python, `-3 % 26` is 23, so negative shifts work too (core.02: `%` takes the sign of the divisor).
2. `lower[k:] + lower[:k]` lines up with `lower` so that position 0 (`a`) maps to the letter `k` places on.
3. One `maketrans` call can map both alphabets: concatenate the "from" strings and the "to" strings in the same order.
4. `translate` changes only characters that are in the table.

## Code

```python
import string

k = int(input()) % 26
lower = string.ascii_lowercase
upper = string.ascii_uppercase
table = str.maketrans(lower + upper, lower[k:] + lower[:k] + upper[k:] + upper[:k])
print(input().translate(table))
```

## Why `translate` and not `replace`

Chaining `replace("a", "d")`, `replace("b", "e")`, ... breaks: after `a` becomes `d`, the later `replace("d", "g")` changes it again. `translate` looks up each original character once.

## Another way

With loops (core.07) you would compute `chr((ord(c) - ord("a") + k) % 26 + ord("a"))` for each letter. The table version is shorter and faster.
