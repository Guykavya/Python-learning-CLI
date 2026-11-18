## Hint 1

First, for each letter, find the index of its **last** occurrence (one pass, a dictionary). The piece that starts at index 0 must stretch at least to `last[s[0]]`. Every letter inside it stretches it further, to that letter's last occurrence.

## Hint 2

Walk from left to right keeping `end`: the furthest last-occurrence of any letter seen in the current piece. When the index `i` reaches `end`, nothing in the piece appears later, so you can cut here: the piece is as short as possible. That is the greedy choice: cut **as early as allowed**, which leaves the most string for the remaining pieces.

## Hint 3

```
last = {ch: i for i, ch in enumerate(s)}      # later indices overwrite earlier ones
sizes = []; start = 0; end = 0
for i, ch in enumerate(s):
    end = max(end, last[ch])
    if i == end:
        sizes.append(i - start + 1)
        start = i + 1
return sizes
```
