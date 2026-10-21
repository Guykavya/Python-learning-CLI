## Hint 1

How do you get the words without worrying about the extra spaces? Which index is the last word, however many words there are?

## Hint 2

`words = text.split()` gives the words. `words[0]` is the first and `words[-1]` is the last. `capitalize()` fixes the case of each one.

## Hint 3

```
words = input().split()
first = words[0].capitalize()
last = words[-1].capitalize()
print(f"{last}, {first}")
print(f"Initials: {first[0]}.{last[0]}.")
```
