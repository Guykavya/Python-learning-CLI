## Approach

Walk through the numbers and keep a set of the values seen so far. If the current value is already in the set, a repeat
exists. Otherwise add it and move on.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

seen = set()
answer = "NO"
for x in a:
    if x in seen:
        answer = "YES"
        break
    seen.add(x)
print(answer)
```

## Complexity

O(n) time on average (set lookups and inserts are O(1) on average), O(n) memory in the worst case.

## Another way

`print("YES" if len(set(a)) < len(a) else "NO")`: a set drops duplicates, so it is shorter than the list exactly when
a value repeats. It builds the whole set first, while the loop can stop early. Sorting and comparing neighbours is
O(n log n) and needs no extra set.
