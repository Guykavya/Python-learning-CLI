## Hint 1

Run the tests against a simple version (`text.split()` and a counting loop). Which tests fail, and what does each message tell you to add: lower-casing, or stripping punctuation?

## Hint 2

`word.strip(chars)` removes any of those characters from both ends only. Which characters? `string.punctuation` was not taught, so write the characters yourself or use `isalnum()` on the ends.

## Hint 3

```
counts = {}
for raw in text.lower().split():
    word = raw.strip(PUNCTUATION)
    if word == "":
        continue
    counts[word] = counts.get(word, 0) + 1
return counts
```
