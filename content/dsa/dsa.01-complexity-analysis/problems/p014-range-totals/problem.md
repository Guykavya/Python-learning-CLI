# Range totals

A shop recorded its sales for `n` days. The manager asks `q` questions of the form "what were the total sales from
day `l` to day `r`, inclusive?" (days are numbered from 1).

`starter.py` answers each question with `sum(a[l - 1:r])`. That is correct, but each slice copies up to `n`
numbers and `sum` adds them all: O(n) per question, O(n * q) in total. With 100000 days and 100000 questions it
takes about a minute. Make it fast.

## Input

- Line 1: `n`.
- Line 2: `n` integers, the sales of each day.
- Line 3: `q`.
- Then `q` lines, each with two integers `l r` (`1 <= l <= r <= n`).

## Output

`q` lines, each with one integer: the total for that question.

## Example

Input:

```
5
3 -1 4 1 5
3
1 3
2 5
4 4
```

Output:

```
6
9
1
```

(3 - 1 + 4 = 6; -1 + 4 + 1 + 5 = 9; day 4 alone is 1.)

## Constraints

- `1 <= n, q <= 100000`
- sales are between `-10^9` and `10^9` (refunds make some days negative)

Use `input()` without a prompt message.

## Before you code

Suppose you had a list `before` where `before[k]` is the total of the first `k` days. How would you get the total
of days 2 to 5 from two values of `before`?
