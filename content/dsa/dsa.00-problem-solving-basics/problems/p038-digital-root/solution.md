## Approach

A number has one digit exactly when it is less than 10. So the outer loop runs `while n >= 10`.
Each pass of the outer loop is one round: compute the digit sum with the usual inner loop
(`total += n % 10`, `n //= 10` until `n` is 0), put the sum back into `n`, and count the round.

The inner loop destroys `n` (it ends at 0), which is fine because we immediately replace `n` with `total`.
`total` must be reset to 0 at the start of every round.

## Trace

Input `99`:

| round | `n` at start | digits added | `total` | `n` after | `rounds` |
|---|---|---|---|---|---|
| 1 | 99 | 9, 9 | 18 | 18 | 1 |
| 2 | 18 | 8, 1 | 9 | 9 | 2 |
| - | 9 | outer loop stops (9 < 10) | | | 2 |

Output: `root 9`, `rounds 2`.

## Code

```python
n = int(input())
rounds = 0
while n >= 10:
    total = 0
    while n > 0:
        total += n % 10
        n //= 10
    n = total
    rounds += 1
print(f"root {n}")
print(f"rounds {rounds}")
```

## Complexity

A 100-digit number has digit sum at most 900. Numbers up to 900 have digit sum at most 26 (for 899),
those have digit sum at most 10 (for 19), and 10 becomes 1. So there are at most 4 rounds, and the first
one does nearly all the work: O(d) for d digits.

## Another way

There is a famous shortcut for the root alone: for `n > 0` the digital root is `1 + (n - 1) % 9`, and for
`n = 0` it is 0. It works because a number and its digit sum always leave the same remainder when divided by 9
(10 leaves remainder 1 when divided by 9, so every digit "counts as itself").
Prefer it when you only need the root. It does not tell you the number of rounds, so this problem still needs the loop.

## Edge cases

- `0`: the outer loop never runs; root 0, rounds 0.
- `9`: root 9, rounds 0. Only numbers 10 and above take a round.
- `10`: one round, root 1.
- `n` with 100 nines: 900 -> 9, two rounds.
