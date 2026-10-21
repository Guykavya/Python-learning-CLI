from solution import format_price


def test_defaults():
    assert format_price(1234.5) == "Rs 1,234.50", "Default: currency 'Rs', 2 decimals, thousands commas."


def test_currency_positional():
    assert format_price(1234.5, "USD") == "USD 1,234.50", "The second positional argument is the currency."


def test_decimals_keyword():
    assert format_price(1234.5, decimals=0) == "Rs 1,234", (
        "decimals=0 means no decimal point at all. Are you using the decimals parameter, not a fixed .2f?")
    assert format_price(2.71828, decimals=3) == "Rs 2.718"


def test_no_thousands():
    assert format_price(1234567.891, thousands=False) == "Rs 1234567.89", "thousands=False: no commas."


def test_big_number_grouping():
    assert format_price(1234567.891) == "Rs 1,234,567.89", "Commas every three digits from the right."


def test_negative():
    assert format_price(-12) == "-Rs 12.00", (
        "The minus sign goes before the currency. Format abs(amount) and add the sign yourself.")
    assert format_price(-1500.256, "USD") == "-USD 1,500.26"


def test_all_keywords():
    assert format_price(0.5, currency="EUR", decimals=1) == "EUR 0.5"
    assert format_price(amount=7, thousands=False, currency="$") == "$ 7.00"
