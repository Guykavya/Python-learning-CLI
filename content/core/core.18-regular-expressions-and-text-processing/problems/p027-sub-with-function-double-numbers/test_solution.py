from solution import double_numbers


def test_recipe():
    assert double_numbers("2 eggs, 150 g flour, 1 cup milk") == "4 eggs, 300 g flour, 2 cup milk", "Pass a function to re.sub: it gets each Match and returns str(int(m.group()) * 2)."


def test_returns_string_with_rest_unchanged():
    assert double_numbers("no numbers here!") == "no numbers here!", "Text without integers must come back unchanged."
    assert double_numbers("") == "", "Empty string stays empty."


def test_multi_digit_and_carry():
    assert double_numbers("999 and 5") == "1998 and 10", "Double the whole number (int of the full match), not digit by digit."


def test_negative():
    assert double_numbers("Cool to -4 degrees") == "Cool to -8 degrees", "Doubling 4 behind the '-' gives '-8', which is exactly double of -4."
    assert double_numbers("-10") == "-20", "A negative number at the very start."
    assert double_numbers("(-3)") == "(-6)", "A '-' after '(' is a minus sign."


def test_minus_between_numbers_is_subtraction():
    assert double_numbers("5-3") == "10-6", "'-' is not a word character, so both 5 and 3 are integers."
    assert double_numbers("x-1") == "x-2", "'1' is preceded by '-', not by a letter, so it is a separate integer."


def test_digits_inside_words_untouched():
    assert double_numbers("mp3 player") == "mp3 player", "Digits glued to letters are part of a word: use (?<![\\w.]) before and (?!\\w...) after."
    assert double_numbers("the 3rd try") == "the 3rd try", "'3rd' is a word, not a number."
    assert double_numbers("a1b2") == "a1b2", "Digits inside a word are left alone."
    assert double_numbers("x_9 9_x") == "x_9 9_x", "'_' is a word character too."


def test_decimals_untouched():
    assert double_numbers("2.5 kg") == "2.5 kg", "A decimal number is not an integer: neither part may be doubled. Reject '.digit' after and '.' before."
    assert double_numbers("pi is 3.14159") == "pi is 3.14159", "Longer decimals are left alone too."


def test_sentence_full_stop_is_fine():
    assert double_numbers("buy 7.") == "buy 14.", "A full stop that is NOT followed by a digit just ends the sentence: 7 is an integer."
    assert double_numbers("1, 2, 3.") == "2, 4, 6.", "Commas and a final full stop do not stop numbers from matching."


def test_leading_zeros():
    assert double_numbers("agent 007") == "agent 14", "int('007') is 7, doubled 14."
