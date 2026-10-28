import pytest

from solution import User, _hash


def test_username_is_stripped_and_checked():
    assert User(" asha ", "mango2024").username == "asha", "Store the username after strip()."
    for bad in ("", "   ", None):
        with pytest.raises(ValueError):
            User(bad, "mango2024")


def test_right_and_wrong_password():
    u = User("asha", "mango2024")
    assert u.check_password("mango2024") is True, "The right password returns True."
    assert u.check_password("Mango2024") is False, "Passwords are case-sensitive."


def test_reading_password_raises():
    u = User("asha", "mango2024")
    with pytest.raises(AttributeError, match="write-only"):
        u.password


def test_only_the_hash_is_stored():
    u = User("asha", "mango2024")
    assert u._password_hash == _hash("mango2024"), "Store _hash(password) in the attribute _password_hash."
    assert "mango2024" not in vars(u).values(), (
        "The plain password is stored in the object. Keep only the hash."
    )
    assert "password" not in vars(u), (
        "There is an instance attribute called 'password'. Make `password` a property on the class, "
        "and set it with self.password = ... so the setter runs."
    )


def test_init_uses_the_setter_checks():
    for bad in ("short1", "abcdefgh", "12345678", 12345678):
        try:
            User("asha", bad)
        except ValueError:
            continue
        pytest.fail(
            f"User('asha', {bad!r}) was accepted. In __init__ write self.password = password, "
            "so the setter's checks run for new users too."
        )


def test_setting_a_new_password():
    u = User("asha", "mango2024")
    u.password = "kiwi-kiwi-7"
    assert u.check_password("kiwi-kiwi-7") is True, "After u.password = new, the new password works."
    assert u._password_hash == _hash("kiwi-kiwi-7"), "The setter stores the new hash."


def test_bad_new_password_keeps_old_one():
    u = User("asha", "mango2024")
    for bad in ("short1", "abcdefghij", "1234567890"):
        with pytest.raises(ValueError):
            u.password = bad
    assert u.check_password("mango2024") is True, "A rejected password must not replace the old one."


def test_locks_after_three_wrong_in_a_row():
    u = User("asha", "mango2024")
    assert u.is_locked is False, "A new user is not locked."
    u.check_password("a")
    u.check_password("b")
    assert u.is_locked is False, "Two wrong attempts are not enough to lock."
    u.check_password("c")
    assert u.is_locked is True, "The third wrong attempt in a row locks the user."
    assert u.check_password("mango2024") is False, "A locked user gets False even for the right password."


def test_right_attempt_resets_the_count():
    u = User("asha", "mango2024")
    u.check_password("a")
    u.check_password("b")
    assert u.check_password("mango2024") is True, "Not locked yet, so the right password works."
    u.check_password("c")
    u.check_password("d")
    assert u.is_locked is False, (
        "A right attempt resets the wrong count to 0. Only 3 wrong attempts IN A ROW lock the user."
    )


def test_unlock():
    u = User("asha", "mango2024")
    for _ in range(3):
        u.check_password("x")
    u.unlock()
    assert u.is_locked is False, "unlock() clears the lock."
    u.check_password("x")
    u.check_password("x")
    assert u.is_locked is False, "unlock() must also reset the wrong count; two new wrong attempts do not lock."
    assert u.check_password("mango2024") is True, "After unlock the right password works again."


def test_is_locked_is_read_only():
    u = User("asha", "mango2024")
    with pytest.raises(AttributeError):
        u.is_locked = True


def test_change_password():
    u = User("asha", "mango2024")
    with pytest.raises(PermissionError):
        u.change_password("wrong", "newpass99")
    assert u.check_password("mango2024") is True, "A refused change keeps the old password."
    u.change_password("mango2024", "newpass99")
    assert u.check_password("newpass99") is True, "change_password sets the new password."
    with pytest.raises(ValueError):
        u.change_password("newpass99", "weak")
