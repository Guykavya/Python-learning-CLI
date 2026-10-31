from solution import parse_query


def test_example():
    got = parse_query('author:"Jane Doe" tag:py tag:re free words')
    assert got == {"author": ["Jane Doe"], "tag": ["py", "re"], "_": ["free", "words"]}, "Filters key:value, quoted values without quotes, repeated keys collect values, free words under '_'."


def test_free_words_only():
    assert parse_query("hello world") == {"_": ["hello", "world"]}, "Terms without key: are free words, stored under '_'."


def test_empty_query():
    assert parse_query("") == {}, "Empty query: empty dict (no '_' key with an empty list)."
    assert parse_query("   \t ") == {}, "Only whitespace: empty dict."


def test_key_lowercased_value_kept():
    assert parse_query("Lang:Python") == {"lang": ["Python"]}, "Keys are case-insensitive (store lower case); values keep their case."


def test_quoted_free_phrase():
    assert parse_query('"exact phrase" x') == {"_": ["exact phrase", "x"]}, "A quoted phrase without a key is ONE free term, without its quotes. Try the quoted alternative before \\S+."


def test_quoted_keeps_inner_spaces_and_empty():
    assert parse_query('title:"  two  spaces  "') == {"title": ["  two  spaces  "]}, "Keep everything between the quotes exactly."
    assert parse_query('note:""') == {"note": [""]}, "An empty quoted value is allowed: use [^\"]* not [^\"]+."


def test_dangling_key_is_free_word():
    assert parse_query("tag: py") == {"_": ["tag:", "py"]}, "'tag:' followed by a space has no value, so the whole term 'tag:' is a free word and 'py' is another one."
    assert parse_query("x tag:") == {"_": ["x", "tag:"]}, "'tag:' at the end is a free word too."


def test_unclosed_quote():
    assert parse_query('author:"Jane Doe') == {"author": ['"Jane'], "_": ["Doe"]}, "With no closing quote, the quote is an ordinary character: the value is the run of non-space characters '\"Jane'."


def test_key_order_first_seen():
    got = parse_query("b:1 a:2 b:3 free")
    assert list(got) == ["b", "a", "_"], "Keys must appear in the order they are first seen. A plain dict keeps insertion order."
    assert got == {"b": ["1", "3"], "a": ["2"], "_": ["free"]}, "Repeated keys collect values in order."


def test_value_may_contain_colon():
    assert parse_query("url:http://x.org time:10:30") == {"url": ["http://x.org"], "time": ["10:30"]}, "Only the FIRST colon after the key splits; the value is the rest of the term (\\S+), colons included."


def test_returns_plain_dict():
    got = parse_query("a:1")
    assert type(got) is dict, "Return a plain dict (convert a defaultdict with dict(...) before returning)."
