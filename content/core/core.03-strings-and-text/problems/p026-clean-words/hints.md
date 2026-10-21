## Hint 1

Removing many different characters at once: which pair of tools from section 24 does that in one pass?

## Hint 2

`str.maketrans("", "", string.punctuation)` builds a table that deletes every punctuation character. Then `text.translate(table)`.

## Hint 3

```
import string
table = str.maketrans("", "", string.punctuation)
words = input().translate(table).casefold().split()
print("Words:", len(words))
print(" ".join(words))
```
