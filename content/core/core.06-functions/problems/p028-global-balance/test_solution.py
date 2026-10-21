import solution


def setup_function():
    solution.balance = 0     # every test starts with an empty wallet


def test_deposit_returns_and_stores():
    assert solution.deposit(100) == 100, "deposit should return the new balance."
    assert solution.deposit(50) == 150
    assert solution.balance == 150, (
        "The module-level balance did not change. Declare `global balance` inside the function.")


def test_withdraw():
    solution.deposit(100)
    assert solution.withdraw(30) == 70
    assert solution.balance == 70


def test_withdraw_too_much():
    solution.deposit(20)
    assert solution.withdraw(500) is None, "Not enough money: return None."
    assert solution.balance == 20, "A refused withdrawal must not change the balance."


def test_withdraw_exact():
    solution.deposit(40)
    assert solution.withdraw(40) == 0, "Withdrawing exactly the balance is allowed and leaves 0."
    assert solution.withdraw(1) is None
