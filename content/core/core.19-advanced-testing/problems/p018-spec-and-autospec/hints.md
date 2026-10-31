## Hint 1

Which function of `unittest.mock` builds a mock from a real class? What does the argument `instance=True`
change (are you faking the class itself or an object made from it)?

## Hint 2

A mock's `return_value` is set per method: `bank.withdraw.return_value = True`. For `transfer`, which
check must come **first**, and when exactly is `deposit` allowed to run?

## Hint 3

```
make_bank(cls): bank = create_autospec(cls, instance=True); bank.withdraw.return_value = True; bank.balance.return_value = 100; return bank
transfer: if amount <= 0: raise ValueError
          if bank.withdraw(src, amount): bank.deposit(dst, amount); return True
          return False
```
