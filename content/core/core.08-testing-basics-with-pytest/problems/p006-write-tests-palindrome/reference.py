from target import is_palindrome


def test_plain_palindrome():
    assert is_palindrome("level") is True, "'level' reads the same backwards."


def test_plain_non_palindrome():
    assert is_palindrome("python") is False, "'python' is not a palindrome."


def test_ignores_case():
    assert is_palindrome("Level") is True, "Upper and lower case must be treated the same."


def test_ignores_spaces():
    assert is_palindrome("nurses run") is True, "Spaces are ignored: 'nursesrun' is a palindrome."


def test_not_only_the_ends():
    assert is_palindrome("abca") is False, "First and last letters match, but the middle does not."


def test_empty_and_single_letter():
    assert is_palindrome("") is True, "The empty text reads the same backwards."
    assert is_palindrome("x") is True, "One letter is a palindrome."


def test_two_letters_different():
    assert is_palindrome("ab") is False, "Two different letters are not a palindrome."
