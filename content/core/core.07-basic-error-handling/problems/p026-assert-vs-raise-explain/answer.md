**1. What -O does.** Running `python -O` removes every `assert` statement before the program
runs, as if the lines were not there. In production `pay` becomes just `int`, a subtraction and a
return. `pay(100, "-50")` returns `150`: a negative payment **adds** money to the card.
`pay(100, "500")` returns `-400`: the student buys food they cannot pay for. Both are money lost,
and nothing is reported. The tests passed only because tests run without `-O`.

**2. The rule.** `assert` is for **programmer** mistakes: it states an **invariant** or
**assumption** that is true whenever **my own code** is correct ("this list is sorted here",
"a discount never makes the price bigger"). If it fails, there is a bug to fix. It may be switched
off, so a correct program must not depend on it. Anything that can legitimately be wrong at run
time, **user input**, file contents, arguments from other people's code, must be checked with
`if ...: raise ...`, which always runs.

**3. The rewrite.**

```python
def pay(balance, amount_text):
    try:
        amount = int(amount_text)
    except ValueError:
        raise ValueError(f"amount must be a whole number of rupees, like 40, got {amount_text!r}") from None
    if amount <= 0:
        raise ValueError(f"amount must be more than 0, got {amount}")
    if amount > balance:
        raise ValueError(f"not enough balance: card has {balance}, payment is {amount}; top up first")
    new_balance = balance - amount
    assert new_balance >= 0, "balance went negative despite the check above"
    return new_balance
```

- `amount > 0` comes from the user: it must be a `raise`, and `ValueError` is the right type (the
  type, a number, is fine; the value is not).
- `amount <= balance` is a business rule about input: also `raise ValueError` with a message that
  says what to do (top up).
- `new_balance >= 0` can only fail if **my** code is wrong (the check above already guarantees
  it), so it is a genuine invariant: it may stay an `assert`. Removing it would also be fine.
- A non-number `amount_text` already raises `ValueError` from `int`, but with a technical message;
  translating it (with `from None`) tells the user what to type.

**4. Wrong exception type.** Callers that handle bad input catch `ValueError` (or `TypeError`).
An `AssertionError` says "the program has a bug", so a caller's `except ValueError` would not catch
it and a user's typo would crash the program with a message meant for programmers. Catching
`AssertionError` in normal code to handle input would be confusing and fragile.

**5. The tuple trap.** The parentheses make one **tuple** `(amount > 0, "amount must be positive")`.
A non-empty tuple is always truthy, so the assertion can **never** fail, whatever `amount` is.
Python 3.14 even warns: "assertion is always true, perhaps remove parentheses?". Write
`assert amount > 0, "message"` without parentheses around the pair.

Key ideas to check: `-O` removes asserts; the two concrete wrong results; assert for programmer
invariants, raise for input; the right exception types and messages; the internal invariant may
stay an assert; `AssertionError` is the wrong signal for callers; the tuple is always truthy.
