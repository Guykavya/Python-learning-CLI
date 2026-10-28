from solution import compact_numbers, log_block, outline, pretty, pretty_sorted

CFG = {"name": "learn", "version": 3, "paths": ["content", "my-work", "data"], "db": {"file": "progress.db", "timeout": 5}}


def test_pretty_wraps_and_keeps_order():
    expected = "\n".join([
        "{'name': 'learn',",
        " 'version': 3,",
        " 'paths': ['content',",
        "           'my-work',",
        "           'data'],",
        " 'db': {'file': 'progress.db',",
        "        'timeout': 5}}",
    ])
    assert pretty(CFG) == expected, (
        "Use pprint.pformat(data, width=width, sort_dicts=False). Without sort_dicts=False pprint SORTS the keys; "
        "with print() or pprint.pprint() you print instead of returning the text."
    )


def test_pretty_wide_fits_on_one_line():
    assert pretty(CFG, width=120) == (
        "{'name': 'learn', 'version': 3, 'paths': ['content', 'my-work', 'data'], "
        "'db': {'file': 'progress.db', 'timeout': 5}}"
    ), "When everything fits in `width` characters, pformat writes one line, like repr(). Pass width on."


def test_pretty_sorted():
    expected = "\n".join([
        "{'db': {'file': 'progress.db',",
        "        'timeout': 5},",
        " 'name': 'learn',",
        " 'paths': ['content',",
        "           'my-work',",
        "           'data'],",
        " 'version': 3}",
    ])
    assert pretty_sorted(CFG) == expected, "pprint's default (sort_dicts=True) sorts dict keys: db, name, paths, version."


def test_outline_depth():
    assert outline(CFG, 1) == "{'name': 'learn', 'version': 3, 'paths': [...], 'db': {...}}", (
        "depth=1 shows only the top level; deeper containers become [...] and {...}. Keep insertion order."
    )
    assert outline({"a": [1, [2, [3]]]}, 2) == "{'a': [1, [...]]}", "depth=2 shows two levels of nesting."


def test_compact_numbers():
    expected = "\n".join([
        "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9,",
        " 10, 11, 12, 13, 14, 15, 16,",
        " 17, 18, 19]",
    ])
    assert compact_numbers(list(range(20))) == expected, (
        "compact=True fills each line with as many items as fit in the width, instead of one item per line."
    )


def test_log_block_indents_every_line():
    assert log_block("config", {"b": 1, "a": [1, 2]}) == "config:\n    {'b': 1, 'a': [1, 2]}", (
        "First line 'title:', then the pretty text indented by 4 spaces, joined with '\\n' (no newline at the end)."
    )
    got = log_block("config", CFG).split("\n")
    assert got[0] == "config:" and len(got) == 8, "The title line plus the 7 lines of pretty(CFG)."
    assert all(line.startswith("    ") for line in got[1:]), "EVERY line of the pretty text is indented, not only the first."
    assert got[3] == "     'paths': ['content',", "Indent each line by exactly 4 spaces, keeping pprint's own alignment."


def test_returns_text_and_prints_nothing(capsys):
    pretty(CFG)
    pretty_sorted(CFG)
    outline(CFG, 1)
    compact_numbers([1, 2])
    log_block("x", CFG)
    assert capsys.readouterr().out == "", "These functions RETURN strings (pformat); they must not print (pprint)."


def test_input_not_changed():
    data = {"b": 2, "a": 1}
    pretty_sorted(data)
    assert list(data) == ["b", "a"], "pformat sorts only in its output; the dict itself keeps its order."
