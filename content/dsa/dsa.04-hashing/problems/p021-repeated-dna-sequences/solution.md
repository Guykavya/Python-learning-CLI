## Approach

There are `n - L + 1` windows. A window is a repeat if it was seen before. Put the second-and-later sightings into
`repeated`, which is a set, so each segment is reported once however many times it occurs. Sort at the end.

## Code

```python
s = input().strip()
L = int(input())

seen = set()
repeated = set()
for i in range(len(s) - L + 1):
    seg = s[i:i + L]
    if seg in seen:
        repeated.add(seg)
    else:
        seen.add(seg)

result = sorted(repeated)
print(len(result))
print(*result)
```

## Complexity

O(n * L) time: each slice and each hash costs `L`. Fine for `L <= 20`. O(n * L) memory for the stored segments.

## Another way

Encode each letter in two bits, so a segment of 10 letters is one 20-bit number; a **rolling** update shifts the number
and adds the next letter in O(1). Then the sets hold small integers. With a very long `L` use a rolling hash (this
module, section 8).
