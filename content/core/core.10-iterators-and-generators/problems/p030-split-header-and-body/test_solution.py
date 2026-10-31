from solution import split_message

MSG = ["From: ann@x.in", "Subject: Meeting", "Time: 10:30", "", "Hi team,", "", "see you at 10:30."]


def test_basic():
    headers, body = split_message(MSG)
    assert headers == {"From": "ann@x.in", "Subject": "Meeting", "Time": "10:30"}, "Headers are the lines before the first blank line. Split at the FIRST ':' and strip."
    assert body == ["Hi team,", "", "see you at 10:30."], "The body is everything after the first blank line, with its own blank lines kept."


def test_separator_not_in_body():
    _, body = split_message(["A: 1", "", "text"])
    assert body == ["text"], "The separating blank line belongs to neither part."


def test_spaces_only_line_is_blank():
    headers, body = split_message(["A: 1", "   ", "text"])
    assert headers == {"A": "1"} and body == ["text"], "A line with only spaces is blank too: test line.strip()."


def test_no_blank_line():
    assert split_message(["A: 1", "B: 2"]) == ({"A": "1", "B": "2"}, []), "No blank line: all lines are headers and the body is []."


def test_no_headers():
    assert split_message(["", "body"]) == ({}, ["body"]), "A blank first line means no headers."


def test_empty():
    assert split_message([]) == ({}, []), "Empty input gives ({}, [])."


def test_body_unchanged():
    _, body = split_message(["A: 1", "", "  indented  "])
    assert body == ["  indented  "], "Do not strip or change the body lines."


def test_generator_input():
    gen = (line for line in MSG)
    headers, body = split_message(gen)
    assert headers["Subject"] == "Meeting", "Must work when lines is a generator."
    assert body == ["Hi team,", "", "see you at 10:30."], "lines may be a generator you can read only once. Use ONE iterator for both parts."
