## Approach

Start from one valid password, then change **one thing** per test so only a single rule fails. The length rule gets both borders: 7 characters must fail (catches a limit that is too low) and exactly 8 must pass (catches a limit that is too high). The other rules each need an input where that rule is the only reason to reject.

## Code

```python
from target import is_valid_password


def test_a_valid_password():
    assert is_valid_password("Abcdefg1") is True, "8 characters with upper, lower and digit is valid."


def test_seven_characters_is_too_short():
    assert is_valid_password("Abcdef1") is False, "7 characters is one too few."


def test_longer_passwords_are_fine():
    assert is_valid_password("Abcdefghij12") is True, "Longer than 8 is fine."


def test_digit_required():
    assert is_valid_password("Abcdefgh") is False, "No digit: must be rejected."


def test_upper_required():
    assert is_valid_password("abcdefg1") is False, "No upper-case letter: must be rejected."


def test_lower_required():
    assert is_valid_password("ABCDEFG1") is False, "No lower-case letter: must be rejected."


def test_space_not_allowed():
    assert is_valid_password("Abcd efg1") is False, "A space makes the password invalid."
```

## Complexity

Not applicable.

## Another way

A `parametrize` table of `(password, expected, reason)` rows, with the reason shown in the failure message.
