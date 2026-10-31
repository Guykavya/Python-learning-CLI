from solution import prices


def test_rupee_sign():
    assert prices("Shirt ₹499 only") == [499.0], "A number right after ₹ is a price. Return floats."
    assert prices("₹ 250") == [250.0], "One space after ₹ is allowed: add a (?<=₹ ) alternative."


def test_rs_marker():
    assert prices("delivery Rs.40 extra") == [40.0], "A number right after 'Rs.' is a price. Escape the dot: Rs\\."
    assert prices("pay Rs. 75 now") == [75.0], "One space after 'Rs.' is allowed: add a (?<=Rs\\. ) alternative."


def test_returns_floats():
    result = prices("₹10")
    assert result == [10.0] and isinstance(result[0], float), "Convert each match with float(...), after removing commas."


def test_commas_removed():
    assert prices("₹ 1,20,000 only") == [120000.0], "Commas group digits (Indian style here): remove them before float()."
    assert prices("Rs.120,000") == [120000.0], "Western grouping works too."


def test_decimals():
    assert prices("jeans Rs. 1,299.50 today") == [1299.5], "A decimal part is a dot followed by digits: (?:\\.\\d+)?"


def test_trailing_punctuation_not_part_of_number():
    assert prices("delivery Rs.40.") == [40.0], "A full stop at the end of a sentence is not a decimal point: the decimal part needs digits after the dot."
    assert prices("Shirt ₹499, jeans") == [499.0], "A comma followed by a space is punctuation. float('499,'.replace(',', '')) handles a comma eaten by [\\d,]*."


def test_full_message():
    text = "Shirt ₹499, jeans Rs. 1,299.50, delivery Rs.40. Total about $25."
    assert prices(text) == [499.0, 1299.5, 40.0], "Find every price in order, and ignore $25 (no rupee marker)."


def test_symbol_not_included_and_others_ignored():
    assert prices("2 items for 300") == [], "Numbers without ₹ or Rs. are not prices."
    assert prices("$25 and 25 rs.") == [], "'rs.' is lower case: the marker is case-sensitive."
    assert prices("Rs.  50") == [], "Two spaces after the marker do not count: the lookbehind widths are fixed."
    assert prices("Rs.abc ₹") == [], "A marker not followed by a digit gives nothing."


def test_two_prices_back_to_back():
    assert prices("₹5₹6") == [5.0, 6.0], "Two markers in a row: each number is found on its own."
    assert prices("") == [], "Empty text, no prices."
