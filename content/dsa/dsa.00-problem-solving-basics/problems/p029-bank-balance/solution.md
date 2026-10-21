## Approach

This is a **simulation**: keep the state (the balance) in one variable and update it step by step.

Each operation reads exactly two lines, always, so the input stays in step even when an operation is refused.
Then one `if / elif` chain applies the rules in the stated order. The order matters: an unknown letter with
amount `-5` must print `unknown operation`, not `invalid amount`, and a withdrawal of `-5` must print
`invalid amount`, not `balance 15`. Only the final `else` changes the balance, so refused operations
leave it untouched automatically.

## Trace

First example (opening balance 100):

| op | amount | rule that fires | balance after | printed |
|---|---|---|---|---|
| W | 30 | apply | 70 | `balance 70` |
| W | 100 | 100 > 70, declined | 70 | `declined` |
| D | 50 | apply | 120 | `balance 120` |
| W | 120 | apply (120 is not > 120) | 0 | `balance 0` |
| (end) | | | 0 | `final 0` |

## Code

```python
balance = int(input())
n = int(input())

for _ in range(n):
    op = input()
    amount = int(input())
    if op != "D" and op != "W":
        print("unknown operation")
    elif amount <= 0:
        print("invalid amount")
    elif op == "W" and amount > balance:
        print("declined")
    else:
        if op == "D":
            balance += amount
        else:
            balance -= amount
        print("balance", balance)

print("final", balance)
```

## Complexity

Constant work per operation: O(n) time, O(1) space.

## Another way

**Branch on the letter first.** Write `if op == "D": ... elif op == "W": ... else: print("unknown operation")`,
and inside each branch check the amount (and, for `W`, the balance). This groups the logic by operation type and
is a good shape when the operations differ a lot (for example if transfers or interest were added later). The
cost is that the "invalid amount" check is repeated in two branches. The flat chain above is shorter when the
rules are shared.

## Edge cases

- `n = 0`: only `final` and the opening balance.
- Withdrawing exactly the balance is allowed and leaves 0.
- An amount of 0 is invalid for both deposits and withdrawals.
- Lowercase `d` or `w` is an unknown operation.
