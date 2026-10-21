## Approach

A list keeps order but answers `in` slowly; a set answers `in` fast but has no order. Use each for what it is
good at. The set is only for the question "seen before?"; the list holds the answer.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

seen = set()
result = []
for x in a:
    if x not in seen:
        seen.add(x)
        result.append(x)
print(len(result))
print(" ".join(str(x) for x in result))
```

## Complexity

- Time: O(n) on average. Each value costs one set lookup and maybe one set add and one list append, all O(1)
  (append is amortised O(1)). The starter is O(n * d), where `d` is the number of different values: O(n^2)
  when they are all different, but fast when there are only a few. That is why the "many repeats" test passes
  even with the starter, and the "all different" one does not.
- Space: O(d) for the set and the list.

## Another way

`list(dict.fromkeys(a))`. A dict keeps keys in insertion order (guaranteed since Python 3.7), and repeated
keys are stored once, so this gives exactly the first-appearance order in one O(n) line. Knowing *why* it
works matters more than the trick: it is the same "hash table plus order" idea.
