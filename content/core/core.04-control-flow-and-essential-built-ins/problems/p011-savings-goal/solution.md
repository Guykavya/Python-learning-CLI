## Approach

A `while` loop that runs as long as the goal is not reached. Before it, rule out the cases
where the loop would run zero times or for ever.

## Code

```python
goal = int(input())
deposit = int(input())
rate = float(input())

if goal > 0 and deposit == 0:
    print("Goal not reachable")
else:
    balance = 0.0
    months = 0
    while balance < goal:
        balance += balance * rate / 100
        balance += deposit
        months += 1
    print(f"Months: {months}")
    print(f"Balance: {balance:.2f}")
```

## Why check for an infinite loop first

With a 0 deposit, the balance starts at 0, and 0 plus interest on 0 is still 0. The
condition `balance < goal` would stay true for ever. Before writing any `while` loop, ask:
"what guarantees this condition eventually becomes false?" Here, a positive deposit does.

## Why the goal of 0 needs no special code

`0 < 0` is false, so the loop runs zero times and prints `Months: 0`. The zero case falls
out of the loop naturally.
