# Maximum score taking cards from both ends

Cards lie in a row; card `i` is worth `a[i]` points. You take exactly `k` cards, one at a time, and each time you
must take the card at the **left end** or at the **right end** of the row. What is the highest total you can get?

Whatever order you choose, you end up taking some `x` cards from the left and `k - x` from the right. Look at it the
other way round: the cards you **leave** are a block of `n - k` **consecutive** cards in the middle. So

```
best score = total of all cards - (smallest sum of n - k consecutive cards)
```

and the smallest window sum of a fixed size is a fixed sliding window. (A greedy "take the bigger end each time" is
wrong: see the example.)

## Input

- Line 1: `n` and `k`.
- Line 2: `n` integers.

## Output

One line: the maximum total.

## Example

Input:

```
7 3
1 2 3 4 5 6 1
```

Output:

```
12
```

Take the three cards on the right: `6 + 5 + 1 = 12`. The cards left behind are `1 2 3 4` (sum 10), the cheapest block
of 4 consecutive cards.

Why greedy fails: `6 1 1 100 1 5` with `k = 3`. Greedy takes 6 (bigger than 5), then 5 (bigger than 1), then a 1:
total 12. The best is to take the three cards on the right, `100 + 1 + 5 = 106`: the cheapest block of 3 to leave is
`6 1 1`.

## Constraints

- `1 <= k <= n <= 200000`
- `1 <= a[i] <= 10^4`

Use `input()` without a prompt message.
