from solution import censor


def test_example():
    assert censor("Darn it, DARN this darned cat!", ["darn", "cat"]) == ("**** it, **** this darned ***!", 3), "Whole words, any case, same number of stars as letters; return (text, count) from re.subn."


def test_returns_count():
    new, count = censor("bad bad bad", ["bad"])
    assert new == "*** *** ***", "Every occurrence is replaced, not just the first."
    assert count == 3, "The second value is how many replacements were made: re.subn gives it to you."


def test_case_insensitive_but_length_kept():
    assert censor("Heck HECK hEcK", ["heck"]) == ("**** **** ****", 3), "Use re.IGNORECASE so every spelling is matched."


def test_whole_words_only():
    assert censor("cat catalog bobcat cat.", ["cat"]) == ("*** catalog bobcat ***.", 2), "Wrap the alternatives in \\b ... \\b so 'catalog' and 'bobcat' are left alone."


def test_alternation_grouped():
    assert censor("xa ax a", ["a", "x"]) == ("xa ax *", 1), "Put the alternatives in a group: \\b(?:a|x)\\b. Without the group, \\ba|x\\b means '\\ba' OR 'x\\b' and censors pieces of words."


def test_star_count_matches_each_word():
    assert censor("no and nope", ["no", "nope"]) == ("** and ****", 2), "Each match gets len(match) stars. Use a function replacement: lambda m: '*' * len(m.group())."


def test_empty_words():
    assert censor("nothing to see", []) == ("nothing to see", 0), "An empty word list must change nothing. Careful: the pattern \\b(?:)\\b matches the EMPTY string at every word edge, so check for an empty list first."


def test_special_characters_escaped():
    assert censor("a.b axb a.b", ["a.b"]) == ("*** axb ***", 2), "Use re.escape on each word: unescaped, '.' matches any character and 'axb' would be censored too."


def test_text_without_matches():
    assert censor("clean words only", ["dirty"]) == ("clean words only", 0), "No match: same text and a count of 0."
