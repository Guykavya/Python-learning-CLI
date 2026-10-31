from solution import doubled_words


def test_simple():
    assert doubled_words("Paris in the the spring") == ["the"], "Capture a word with (\\w+), then match \\s+ and the same text again with \\1."
    assert doubled_words("no repeats here") == [], "No word is repeated, so the list is empty."


def test_returns_the_word_not_the_pair():
    assert doubled_words("go go") == ["go"], "Return the word itself (group 1), not the whole match 'go go'."


def test_ignores_case():
    assert doubled_words("The the cat") == ["The"], "Compare ignoring case (re.IGNORECASE also makes \\1 ignore case) and report the FIRST copy's spelling."


def test_several_in_order():
    assert doubled_words("The the cat sat on on the mat") == ["The", "on"], "Find every doubled word, in order: use finditer or findall."


def test_whole_words_only_at_the_end():
    assert doubled_words("the theory") == [], "'the' followed by 'the...' inside 'theory' is not a repeat. Put \\b after \\1."
    assert doubled_words("is island") == [], "\\1 must end at a word boundary: add \\b after \\1."


def test_whole_words_only_at_the_start():
    assert doubled_words("this is the test") == [], "Without \\b before the group, (\\w+) can start inside 'this' and match 'is is'. Start with \\b."


def test_across_newline_and_tabs():
    assert doubled_words("a line ending in\nin the next") == ["in"], "The two copies may be split by a newline: use \\s+, not a literal space."
    assert doubled_words("x\t\tx") == ["x"], "Tabs are whitespace too."


def test_triple_reported_once():
    assert doubled_words("go go go now") == ["go"], "After matching 'go go', the search continues after it; ' go' alone is not a pair. One report is expected."


def test_digits_and_underscore_are_word_chars():
    assert doubled_words("call 911 911 now") == ["911"], "A word is \\w+, which includes digits."


def test_empty():
    assert doubled_words("") == [], "Empty text has no doubled words."
