## Hint 1

What does the alphabet look like after rotating it 3 places? How can you build that with two slices of `string.ascii_lowercase`?

## Hint 2

`lower[k:] + lower[:k]` is the alphabet rotated by `k`. Make `k = shift % 26` first, so 29 becomes 3 and -3 becomes 23. Build one table that maps both the lowercase and uppercase alphabets.

## Hint 3

```
import string
k = int(input()) % 26
lower = string.ascii_lowercase
upper = string.ascii_uppercase
table = str.maketrans(lower + upper, lower[k:] + lower[:k] + upper[k:] + upper[:k])
print(input().translate(table))
```
