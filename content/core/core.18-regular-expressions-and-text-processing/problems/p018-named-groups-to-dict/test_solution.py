from solution import parse_kv


def test_simple():
    assert parse_kv("port = 8080") == {"key": "port", "value": "8080"}, "Use named groups (?P<key>...) and (?P<value>...), then m.groupdict()."
    assert parse_kv("port=8080") == {"key": "port", "value": "8080"}, "Spaces around '=' are optional: use \\s*, not a literal space."


def test_returns_plain_dict_with_two_keys():
    result = parse_kv("a = b")
    assert isinstance(result, dict), "Return a dict (m.groupdict()), not the Match object."
    assert set(result) == {"key", "value"}, "Name the groups exactly 'key' and 'value'."


def test_whitespace_trimmed():
    assert parse_kv("  title = Hello World  ") == {"key": "title", "value": "Hello World"}, "Spaces at the ends are removed, the space INSIDE the value stays. A greedy (?P<value>.*) keeps the trailing spaces: try .*? followed by \\s*."
    assert parse_kv("\tname\t=\tKavya\n") == {"key": "name", "value": "Kavya"}, "Tabs and a trailing newline count as whitespace too (\\s)."


def test_value_may_contain_equals():
    assert parse_kv("url=http://x.in/?a=1") == {"key": "url", "value": "http://x.in/?a=1"}, "Split at the FIRST '=': the key cannot contain '=', so the rest belongs to the value."
    assert parse_kv("expr = a == b") == {"key": "expr", "value": "a == b"}, "Extra '=' signs belong to the value."


def test_empty_value():
    assert parse_kv("debug =") == {"key": "debug", "value": ""}, "An empty value is allowed: the value group should use *, not +."
    assert parse_kv("debug =   ") == {"key": "debug", "value": ""}, "Only spaces after '=' is still an empty value."


def test_bad_keys():
    assert parse_kv("1st = no") is None, "A key starts with a letter or '_': [A-Za-z_]\\w*."
    assert parse_kv("my key = 1") is None, "A key has no spaces. Did you use re.search, which finds 'key = 1' inside?"
    assert parse_kv("= 5") is None, "The key cannot be empty."
    assert parse_kv("_private = yes") == {"key": "_private", "value": "yes"}, "A key may start with '_'."
    assert parse_kv("max_size2 = 10") == {"key": "max_size2", "value": "10"}, "Digits are fine after the first character."


def test_not_a_pair():
    assert parse_kv("no equals here") is None, "No '=' means not a key/value line: return None."
    assert parse_kv("") is None, "An empty line is not a pair."
    assert parse_kv("   ") is None, "A blank line is not a pair."
