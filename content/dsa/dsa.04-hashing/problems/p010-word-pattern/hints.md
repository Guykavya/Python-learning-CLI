## Hint 1

This is the isomorphic-strings idea again: letters on one side, words on the other. What are the two rules?

## Hint 2

First compare the lengths. Then keep `letter_to_word` and `word_to_letter`, and check each pair against both.

## Hint 3

```
words = line.split()
if len(words) != len(pattern): NO
for ch, w in zip(pattern, words): same two-way check
```
