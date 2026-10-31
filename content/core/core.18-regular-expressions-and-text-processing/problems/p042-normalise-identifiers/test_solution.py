from solution import normalise_ids


def test_example():
    got = normalise_ids(["inv-  0042 ", "PO 7", "Inv_123456", "ab12", "i-42", "inv--42", "INV-42"])
    assert got == ["INV-0042", "PO-0007", "INV-123456", "AB-0012"], "Strip, fullmatch, upper-case the prefix, pad the number with zfill(4), skip invalid lines and duplicates."


def test_each_separator():
    assert normalise_ids(["ab-1", "cd_2", "ef/3", "gh4", "ij 5"]) == ["AB-0001", "CD-0002", "EF-0003", "GH-0004", "IJ-0005"], "The separator is one of - _ / or nothing (spaces are allowed around it)."


def test_spaces_around_separator():
    assert normalise_ids(["ab  -  12"]) == ["AB-0012"], "Allow spaces before and after the separator: ' *[-_/]? *'."


def test_strip_outer_whitespace():
    assert normalise_ids(["\t  xy-9  \n"]) == ["XY-0009"], "Strip the line first (tabs and newlines too), then check it."


def test_prefix_length():
    assert normalise_ids(["a-1"]) == [], "A 1-letter prefix is invalid: use {2,4}."
    assert normalise_ids(["abcde-1"]) == [], "A 5-letter prefix is invalid. Without fullmatch, search() would find 'bcde-1' inside it."
    assert normalise_ids(["abcd-1"]) == ["ABCD-0001"], "4 letters is still valid."


def test_prefix_letters_only():
    assert normalise_ids(["a1-5", "ab_c-5", "äb-5"]) == [], "The prefix is ASCII letters only: [A-Za-z], not \\w (which also allows digits, '_' and letters like 'ä')."


def test_number_length():
    assert normalise_ids(["ab-1234567"]) == [], "More than 6 digits is invalid."
    assert normalise_ids(["ab-123456"]) == ["AB-123456"], "6 digits is valid and stays as it is (zfill only pads)."
    assert normalise_ids(["ab-"]) == [], "At least one digit is required."


def test_padding_keeps_leading_zeros():
    assert normalise_ids(["ab-000042"]) == ["AB-000042"], "Keep the digits as typed and only pad short numbers: do not convert with int(), which would drop the zeros of '000042'."


def test_one_separator_only():
    assert normalise_ids(["ab--1", "ab-_1", "ab - - 1"]) == [], "At most ONE separator: [-_/]? not [-_/]*."


def test_junk_lines():
    assert normalise_ids(["", "   ", "hello", "12-ab", "ab-12x", "ab 12 34"]) == [], "Empty, letters-only, reversed, trailing junk and two numbers are all invalid: the whole line must match."


def test_duplicates_after_normalising():
    assert normalise_ids(["po-7", "PO_0007", "Po 07", "po-8"]) == ["PO-0007", "PO-0008"], "Different spellings of the same id count as duplicates: compare the NORMALISED forms, keep the first."


def test_empty_input():
    assert normalise_ids([]) == [], "No lines, no ids."
