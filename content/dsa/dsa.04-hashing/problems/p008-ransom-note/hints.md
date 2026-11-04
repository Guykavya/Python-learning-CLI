## Hint 1

The question is about **how many** of each letter. What structure stores counts?

## Hint 2

Count the magazine letters. For each letter of the note, take one away. If a count is 0 (or missing) when you need one, the answer is `NO`.

## Hint 3

```
stock = counts of magazine
for ch in note:
    if stock.get(ch, 0) == 0: NO
    stock[ch] -= 1
YES
```
