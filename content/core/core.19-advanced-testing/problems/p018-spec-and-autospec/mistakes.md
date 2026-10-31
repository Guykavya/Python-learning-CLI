- `create_autospec(Bank)` without `instance=True` gives a mock of the **class**: calling
  `bank.withdraw("a", 5)` then needs the `self` argument and raises `TypeError`.
- `Mock(spec=Bank)` and thinking signatures are checked. They are not; only attribute names are.
- Calling `bank.deposit(...)` even when `withdraw` returned `False`: money appears from nowhere.
- Checking `amount <= 0` **after** the withdraw: the bank has already been called.
- Testing `if bank.withdraw(...) == True`: works, but `is True` or plain truthiness is the idiom;
  a mock with no `return_value` returns a (truthy) `Mock`, one more reason to set it.
