## Approach

Count the magazine as the available **stock** of each letter. Then spend one unit of stock per note letter. If the
stock for a needed letter is 0, the note cannot be made.

## Code

```python
note = input().strip()
magazine = input().strip()

stock = {}
for ch in magazine:
    stock[ch] = stock.get(ch, 0) + 1

answer = "YES"
for ch in note:
    if stock.get(ch, 0) == 0:
        answer = "NO"
        break
    stock[ch] -= 1
print(answer)
```

## Complexity

O(len(note) + len(magazine)) time, O(1) memory for 26 letters.

## Another way

With `Counter`: `not (Counter(note) - Counter(magazine))`. Subtracting counters keeps only positive leftovers, so an
empty result means the magazine had enough of everything.
