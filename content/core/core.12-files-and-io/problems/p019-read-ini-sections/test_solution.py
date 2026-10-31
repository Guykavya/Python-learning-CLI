from solution import get_int, read_ini

INI = "[server]\nPort = 8080\nhost = example.org\n\n[user]\nname = Ravi\n"


def make(tmp_path, text=INI):
    p = tmp_path / "app.ini"
    p.write_text(text, encoding="utf-8")
    return p


def test_read_ini(tmp_path):
    p = make(tmp_path)
    assert read_ini(p) == {"server": {"port": "8080", "host": "example.org"}, "user": {"name": "Ravi"}}, "A dict of dicts with string values. Keys are lower case."


def test_values_are_plain_strings(tmp_path):
    result = read_ini(str(make(tmp_path)))
    assert type(result) is dict and type(result["server"]) is dict, "Return plain dicts, not parser objects: dict(cp[section])."


def test_missing_file(tmp_path):
    assert read_ini(tmp_path / "nope.ini") == {}, "A missing file gives an empty dict."


def test_unicode(tmp_path):
    p = make(tmp_path, "[a]\ncity = Zürich ₹\n")
    assert read_ini(p) == {"a": {"city": "Zürich ₹"}}, "Read with encoding='utf-8'."


def test_get_int(tmp_path):
    p = make(tmp_path)
    assert get_int(p, "server", "port", 80) == 8080, "The value must be an int, not '8080'."


def test_get_int_fallbacks(tmp_path):
    p = make(tmp_path)
    assert get_int(p, "server", "timeout", 30) == 30, "Missing option: return the fallback."
    assert get_int(p, "nosection", "port", 7) == 7, "Missing section: return the fallback."
    assert get_int(tmp_path / "nope.ini", "server", "port", 5) == 5, "Missing file: return the fallback."
