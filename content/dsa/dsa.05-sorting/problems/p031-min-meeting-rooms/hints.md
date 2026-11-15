## Hint 1

At any moment, how many rooms are busy? What changes that number: starts or ends? What is the answer in terms of that number over time?

## Hint 2

Sort starts and ends separately. Walk `i` over the starts. Before using a new start `s`, free every room whose end is `<= s` (move the end pointer). The busy count is `(i + 1) - freed`; the answer is its maximum.

## Hint 3

```
starts.sort(); ends.sort(); j = 0; best = 0
for i, s in enumerate(starts):
    while ends[j] <= s: j += 1
    best = max(best, i + 1 - j)
```
