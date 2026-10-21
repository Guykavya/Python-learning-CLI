## Hint 1

A dict from letter to a **list** of words. What do you do the first time you see a letter?

## Hint 2

`groups.setdefault(letter, []).append(word)` creates the list when needed and appends either way.

## Hint 3

The key is `word[0].lower()`. Print with `for letter, ws in groups.items():`.
