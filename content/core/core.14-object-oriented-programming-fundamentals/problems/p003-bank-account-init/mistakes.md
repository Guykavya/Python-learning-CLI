- Subtracting first and checking afterwards. When the check fails, the balance is already wrong.
- Checking `amount > self.balance` before `amount <= 0`. A negative withdrawal then increases the balance.
- Using `balance <= 0` for the opening check. An account may open with 0 rupees.
- Returning nothing (`None`) from `deposit`/`withdraw`. The problem asks for the new balance.
- Using `print("insufficient funds")` instead of `raise`. The caller cannot tell that it failed, and
  the code keeps running.
- Checking only `owner == ""`. A name of only spaces is empty too; use `owner.strip()`.
