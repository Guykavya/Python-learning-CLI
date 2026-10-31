from solution import swap_names


def test_one_line():
    assert swap_names("Baghel, Kavya") == "Kavya Baghel", "Capture last and first names and replace with r'\\2 \\1'."


def test_no_space_and_many_spaces():
    assert swap_names("Sharma,Ravi") == "Ravi Sharma", "The space after the comma is optional: use [ \\t]*, not a single required space."
    assert swap_names("Rao,   \tMeera") == "Meera Rao", "Several spaces or tabs after the comma are allowed."


def test_every_line():
    text = "Baghel, Kavya\nSharma, Ravi\nRao, Meera"
    assert swap_names(text) == "Kavya Baghel\nRavi Sharma\nMeera Rao", "Every line is swapped: use re.MULTILINE so ^ and $ work per line."


def test_keeps_final_newline():
    assert swap_names("Doe, Jane\n") == "Jane Doe\n", "The newline at the end must stay. Do not let \\s* or the pattern swallow it."


def test_apostrophe_hyphen_and_middle_names():
    assert swap_names("O'Brien, Conan") == "Conan O'Brien", "A name may contain an apostrophe: [\\w'-]+."
    assert swap_names("Smith-Jones, Anna Maria") == "Anna Maria Smith-Jones", "First names can be several words separated by single spaces."
    assert swap_names("Iyer, Ananya ") == "Ananya Iyer", "Trailing spaces on the line are dropped."


def test_unicode_letters():
    assert swap_names("Müller, Jürgen") == "Jürgen Müller", "\\w matches letters from any language."


def test_other_lines_unchanged():
    text = "Teacher: Mrs Rao\nBaghel, Kavya\nno comma here"
    assert swap_names(text) == "Teacher: Mrs Rao\nKavya Baghel\nno comma here", "Lines without the 'Last, First' shape stay exactly as they are."
    assert swap_names("a, b, c") == "a, b, c", "Two commas: not a 'Last, First' line. Anchor both ends of the line with ^ and $."
    assert swap_names("Van Dyke, Dick") == "Van Dyke, Dick", "The last name is ONE name with no space, so this line does not fit and stays."


def test_does_not_join_lines():
    assert swap_names("Doe,\nJane") == "Doe,\nJane", "\\s* after the comma also eats the newline and joins two lines. Use [ \\t]* (spaces and tabs only)."


def test_empty():
    assert swap_names("") == "", "Empty text stays empty."
