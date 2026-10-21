# Explain: assert or raise?

A student wrote this for a canteen's prepaid card system:

```python
def pay(balance, amount_text):
    amount = int(amount_text)
    assert amount > 0, "amount must be positive"
    assert amount <= balance, "not enough balance"
    new_balance = balance - amount
    assert new_balance >= 0, "balance went negative"
    return new_balance
```

It passes all their tests. In production, the server runs Python with the `-O` flag.

In `answer.md`:

1. Say what `-O` does to this function, and what `pay(100, "-50")` and `pay(100, "500")` return
   in production. Why is that a real problem for the canteen?
2. Explain the rule for when to use `assert` and when to use `raise`. Use the words
   **programmer**, **invariant** (or **assumption**) and **user input**.
3. Rewrite `pay` correctly. Decide, for each of the three checks, whether it should stay an
   `assert`, become a `raise` (which exception type?), or disappear, and say why. Also deal with
   `amount_text` not being a number, with a message that tells the user what to do.
4. Name one more reason, besides `-O`, why `AssertionError` is the wrong exception for bad input.
5. Explain what is wrong with `assert (amount > 0, "amount must be positive")`.
