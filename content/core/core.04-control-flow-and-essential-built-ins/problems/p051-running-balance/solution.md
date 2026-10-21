## Approach

A loop-and-a-half with two exits: `end` and a decline. Invalid lines are skipped with
`continue`. The final balance is printed after the loop in every case.

## Code

```python
balance = int(input())
count = 0
while True:
    line = input().strip()
    if line == "end":
        break
    if not (len(line) >= 2 and line[0] in "+-" and line[1:].isdigit()):
        print(f"Skipped: {line}")
        continue
    count += 1
    amount = int(line[1:])
    if line[0] == "-" and amount > balance:
        print(f"#{count} declined: balance {balance}, needed {amount}")
        break
    balance += amount if line[0] == "+" else -amount
    print(f"#{count} OK, balance {balance}")
print(f"Final balance: {balance}")
```

## Why stopping is part of correctness

After a decline, a real system would stop the batch for review. Processing later lines (like
`+50`) would print a different final balance, and reading lines that are not there would crash
with `EOFError`.

## Why `amount > balance` and not `>=`

Withdrawing exactly the whole balance is allowed; it leaves 0.
