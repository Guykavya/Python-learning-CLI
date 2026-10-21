# Competition ranking

Read `n`, then `n` lines of `name score`. Rank the players with **competition ranking**: a
player's rank is 1 plus the number of players with a **strictly higher** score. Equal scores
share a rank, and the next rank skips (1, 2, 2, 4).

Print the players sorted by score (highest first), ties by name:

```
<rank>. <name> <score>
```

Then print `Distinct scores: <k>`.

**Example**

Input:
```
5
ravi 70
asha 90
meena 85
john 90
zoe 85
```
Output:
```
1. asha 90
1. john 90
3. meena 85
3. zoe 85
5. ravi 70
Distinct scores: 3
```

The tests include 100,000 players. Counting higher scores separately for each player is O(n²).
