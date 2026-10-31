from solution import to_camel, to_snake


def test_snake_simple():
    assert to_snake("camelCase") == "camel_case", "Insert '_' between a lower-case letter and a capital, then lower-case it all."
    assert to_snake("getUserName") == "get_user_name", "Every lower->upper boundary gets an underscore (re.sub replaces all of them)."
    assert to_snake("Simple") == "simple", "A capital at the very start gets no underscore in front."


def test_snake_acronyms():
    assert to_snake("HTTPServer") == "http_server", "End of an acronym: ([A-Z]+)([A-Z][a-z]) -> r'\\1_\\2'. Without it you get 'httpserver'."
    assert to_snake("getHTTPResponseCode") == "get_http_response_code", "Both rules are needed: 'tH' (lower->upper) and 'PR' + 'e' (end of acronym)."
    assert to_snake("parseXML") == "parse_xml", "An acronym at the end: only the lower->upper rule applies."
    assert to_snake("ABC") == "abc", "All capitals and nothing after: no boundary inside."


def test_snake_digits():
    assert to_snake("version2Update") == "version2_update", "A digit followed by a capital is a boundary too: ([a-z0-9])([A-Z])."
    assert to_snake("utf8") == "utf8", "Digits after letters are not a boundary."


def test_snake_already_snake():
    assert to_snake("already_snake") == "already_snake", "Already snake_case: nothing to change."
    assert to_snake("_privateVar") == "_private_var", "A leading underscore stays."
    assert to_snake("") == "", "Empty name stays empty."


def test_camel_simple():
    assert to_camel("get_http_response_code") == "getHttpResponseCode", "Each '_x' becomes 'X': a replacement FUNCTION can call .upper() on the group."
    assert to_camel("camel_case") == "camelCase", "Remove the underscore and upper-case the next letter."
    assert to_camel("word") == "word", "No underscores: nothing changes."


def test_camel_digits():
    assert to_camel("version2_update") == "version2Update", "An underscore after a digit also joins words."
    assert to_camel("utf_8") == "utf8", "A digit after '_' stays a digit (its upper() is itself), the '_' is removed."


def test_camel_leading_underscore():
    assert to_camel("_private_var") == "_privateVar", "A leading '_' is not between two word parts: keep it. Use a lookbehind (?<=[a-z0-9])."
    assert to_camel("__init__") == "__init__", "Dunder names: no '_' sits between two letters/digits, so nothing changes."
    assert to_camel("") == "", "Empty name stays empty."


def test_round_trip():
    for name in ["camelCase", "getUserName", "version2Update"]:
        assert to_camel(to_snake(name)) == name, f"to_camel(to_snake({name!r})) should give the name back."
