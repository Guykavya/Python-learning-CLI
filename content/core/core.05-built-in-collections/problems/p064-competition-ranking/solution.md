## Approach

Sort `(-score, name)` tuples. In that order, everyone above position i has a higher or equal
score. The first position where a score appears is exactly 1 plus the number of strictly
higher scores, so it is that score's rank. Remember it in a dict.

## Code

```python
players = []
for _ in range(int(input())):
    name, score = input().split()
    players.append((-int(score), name))
players.sort()
rank_of = {}
for i, (neg, name) in enumerate(players, start=1):
    if neg not in rank_of:
        rank_of[neg] = i
    print(f"{rank_of[neg]}. {name} {-neg}")
print("Distinct scores:", len(rank_of))
```

## Complexity

O(n log n) for the sort and O(n) for the walk. Counting higher scores for each player is
O(n²): ten billion comparisons for 100,000 players.
