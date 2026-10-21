from solution import count_vowels


def test_simple_word():
    assert count_vowels("hello") == 2, "'hello' has two vowels: e and o."


def test_empty_string():
    assert count_vowels("") == 0, "An empty string has no vowels, so the answer is 0."


def test_uppercase_counts():
    assert count_vowels("AEIOU") == 5, "Upper-case vowels count too. Convert with .lower() first."
    assert count_vowels("HeLLo") == 2, "Mixed case: only e and o are vowels in 'HeLLo'."


def test_y_is_not_a_vowel():
    assert count_vowels("rhythm") == 0, "'y' is not a vowel in this problem."


def test_repeated_vowels_all_count():
    assert count_vowels("banana") == 3, "Count every occurrence: 'banana' has three a's."


def test_spaces_and_punctuation():
    assert count_vowels("Why? Oh, my!") == 1, "Only the 'O' in 'Oh' is a vowel; spaces and punctuation are ignored."
