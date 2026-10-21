## Approach

Validate the input first, then compute. `amount <= 0` is checked before `amount > balance`, so a negative amount reports "positive", never "insufficient". The boundary `amount == balance` is allowed, so the second test is a strict `>`.

## Code

```python
def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
```

## Complexity

O(1).

## Another way

Check `if not 0 < amount <= balance:` and decide the message afterwards. Two separate ifs are easier to read and give two different messages.
