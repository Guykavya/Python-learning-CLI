from solution import tokens


def test_mixed_separators():
    assert tokens("red, green;blue  yellow") == ["red", "green", "blue", "yellow"], "Split on commas, semicolons AND whitespace: put all of them in one class [,;\\s]."


def test_runs_of_separators():
    assert tokens("a,,b") == ["a", "b"], "Two commas in a row must not give an empty token: use + so a run of separators is one split."
    assert tokens("a , ; b") == ["a", "b"], "A run of mixed separators is one split."


def test_leading_and_trailing():
    assert tokens(" ,a,,b; ") == ["a", "b"], "re.split gives '' at the start/end when the text starts/ends with a separator: drop empty strings."


def test_other_whitespace():
    assert tokens("x-ray\tv1.2\nend") == ["x-ray", "v1.2", "end"], "Tabs and newlines are whitespace (\\s). Hyphens and dots are NOT separators."


def test_empty_and_only_separators():
    assert tokens("") == [], "Empty input: no tokens. re.split(pattern, '') gives [''], so filter it out."
    assert tokens(" ,; \n") == [], "Only separators: no tokens."


def test_single_token():
    assert tokens("hello") == ["hello"], "No separators: one token."
