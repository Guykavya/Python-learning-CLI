from solution import count_word


def test_whole_words_only():
    assert count_word("The theme of the other THE", "the") == 3, "Count only WHOLE words: 'theme' and 'other' contain 'the' but do not count. Put \\b on both sides."


def test_ignore_case():
    assert count_word("Cat CAT cat cAt", "cat") == 4, "Ignore case: pass re.IGNORECASE (or use (?i))."
    assert count_word("python", "PYTHON") == 1, "The case of the WORD argument does not matter either."


def test_boundary_both_sides():
    assert count_word("cats cat scat", "cat") == 1, "\\b is needed on BOTH sides: 'cats' fails at the end, 'scat' at the start."


def test_special_characters_escaped():
    assert count_word("node.js, nodexjs and NODE.JS", "node.js") == 2, "The '.' in 'node.js' must be literal. Without re.escape it matches any character, so 'nodexjs' is wrongly counted."
    assert count_word("c+d, C+D and ccd", "c+d") == 2, "'+' must be literal too: use re.escape(word). Unescaped, 'c+d' means 'one or more c, then d': it misses 'c+d' and matches 'ccd' instead."


def test_hyphen_and_underscore():
    assert count_word("well-known well", "well") == 2, "A hyphen is not a word character, so 'well' in 'well-known' is a whole word."
    assert count_word("the_end", "the") == 0, "Underscore IS a word character (\\w), so 'the' in 'the_end' is not a whole word."


def test_punctuation_around():
    assert count_word("(go) go! go, 'go'", "go") == 4, "Brackets, punctuation and quotes are word boundaries."


def test_digits_are_word_chars():
    assert count_word("2024 20245 x2024", "2024") == 1, "Digits are word characters: '20245' and 'x2024' do not contain 2024 as a whole word."


def test_none_found():
    assert count_word("", "x") == 0, "Empty text: 0."
    assert count_word("nothing here", "cat") == 0, "Word not present: 0."
