# Make the failing tests pass: withdraw

The tests specify `withdraw(balance, amount)`. Read `test_solution.py` and write the function.

What the tests say, in words:

- a normal withdrawal returns the **new balance**;
- withdrawing the whole balance is allowed and gives `0`;
- an `amount` that is zero or negative raises `ValueError` with a message containing
  `"positive"`;
- an `amount` larger than the balance raises `ValueError` with a message containing
  `"insufficient"` (the tests use `pytest.raises(..., match=...)`).

**Examples**

```python
withdraw(100, 30)    # 70
withdraw(100, 100)   # 0
withdraw(100, 0)     # raises ValueError("amount must be positive")
withdraw(100, 500)   # raises ValueError("insufficient funds")
```
