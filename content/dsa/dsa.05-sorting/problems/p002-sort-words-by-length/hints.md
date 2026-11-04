## Hint 1

You do not want to sort the words alphabetically, only by length. Which argument of `sorted` tells it what to compare?

## Hint 2

`sorted(words, key=len)`. Python's sort is stable, so equal keys keep the input order. Do not add the word to the key: that would break ties alphabetically.

## Hint 3

```
words = input().split()
print(' '.join(sorted(words, key=len)))
```
