# Stone game (interval)

Piles of stones stand in a row: `piles[i]` stones in pile `i`. Two players take turns; the first player starts. On a turn, a player takes the **whole first pile or the whole last pile** of the row that is left. When no piles are left, each player's score is the number of stones they took. Both players play **perfectly**: each one tries to make their own score minus the other's as large as possible.

Write `stone_game(piles)` that returns **the first player's score minus the second player's score** under perfect play.

## Example

```python
>>> stone_game([3, 9, 1, 2])     # first takes 2; whatever the second takes, the first gets the 9
7
>>> stone_game([5, 3, 4, 5])
1
>>> stone_game([2, 7, 3])        # 7 always goes to the second player
-2
>>> stone_game([7])
7
>>> stone_game([])
0
```

In `[3, 9, 1, 2]` the first player takes 2. If the second takes 3, the first takes 9 and the second gets 1; if the second takes 1, the first takes 9 and the second gets 3. Either way: 11 against 4, a difference of 7.

## Constraints

- `0 <= len(piles) <= 500`, `1 <= piles[i] <= 1000`.
- `O(n^2)` time. Trying every sequence of moves is `2^n`.
- (LeetCode's "Stone Game" asks only whether the first player wins: that is `stone_game(piles) > 0`.)

## Think about

After any number of moves, the piles left are always a **contiguous** range `piles[i..j]`. So the state is a range, as in section 17. Here is the trick that removes "whose turn is it" from the state: let `f(i, j)` be the best difference **for the player about to move**, on the range `i..j`. If that player takes `piles[i]`, the opponent then moves on `i+1..j` and gets the difference `f(i+1, j)` for themself. What is the mover's difference then?
