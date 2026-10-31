from solution import commas, commas_indian


def test_commas_basic():
    assert commas(1234567) == "1,234,567", "A comma goes where the digits to the right are a multiple of 3: (?=(?:\\d{3})+$)."
    assert commas(1000) == "1,000", "One comma for a four-digit number."
    assert commas(1000000) == "1,000,000", "Zeros are digits too: groups of three from the right."


def test_commas_needs_end_anchor():
    assert commas(12345678) == "12,345,678", "Without $ in the lookahead, ANY gap followed by 3 digits gets a comma ('1,2,3,4,5,678')."


def test_commas_no_comma_at_start():
    assert commas(999) == "999", "No comma before the first digit: add a lookbehind (?<=\\d) so the gap must have a digit on its left."
    assert commas(123456) == "123,456", "Six digits: no leading comma (',123,456' means the lookbehind is missing)."
    assert commas(100) == "100", "Three digits need no comma."


def test_commas_small_and_zero():
    assert commas(0) == "0", "0 stays '0'."
    assert commas(7) == "7", "One digit stays as it is."


def test_commas_negative():
    assert commas(-1000) == "-1,000", "The minus stays in front."
    assert commas(-123) == "-123", "No comma after the minus sign: (?<=\\d) rejects the gap after '-'."
    assert commas(-1234567) == "-1,234,567", "Negative numbers group like positive ones."


def test_commas_huge():
    assert commas(10**18) == "1,000,000,000,000,000,000", "Python ints can be huge; the pattern does not care about size."


def test_indian_basic():
    assert commas_indian(1234567) == "12,34,567", "Indian grouping: last three digits, then pairs: (?=(?:\\d\\d)*\\d{3}$)."
    assert commas_indian(100000) == "1,00,000", "One lakh is 1,00,000."
    assert commas_indian(10000000) == "1,00,00,000", "One crore is 1,00,00,000."


def test_indian_small():
    assert commas_indian(1000) == "1,000", "Up to 99,999 Indian and Western grouping agree."
    assert commas_indian(12345) == "12,345", "Five digits: one comma before the last three."
    assert commas_indian(999) == "999", "Three digits: no comma (do you have the (?<=\\d) lookbehind?)."
    assert commas_indian(0) == "0", "0 stays '0'."


def test_indian_negative():
    assert commas_indian(-12345) == "-12,345", "No comma after the minus sign."
    assert commas_indian(-123456) == "-1,23,456", "Negative lakhs."
