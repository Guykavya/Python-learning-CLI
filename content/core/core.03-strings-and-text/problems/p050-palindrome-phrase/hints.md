## Hint 1

You need to delete two groups of characters at once. Which constants in the `string` module hold them?

## Hint 2

`str.maketrans("", "", string.punctuation + string.whitespace)` deletes both groups. Casefold, then compare the result with its reverse.

## Hint 3

```
import string
table = str.maketrans("", "", string.punctuation + string.whitespace)
cleaned = input().translate(table).casefold()
print("Cleaned:", cleaned)
print("Palindrome:", cleaned == cleaned[::-1])
```
