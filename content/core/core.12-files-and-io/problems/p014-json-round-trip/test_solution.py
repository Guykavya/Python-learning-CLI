from solution import load_json, save_json


def test_exact_text(tmp_path):
    p = tmp_path / "c.json"
    save_json(p, {"b": 1, "a": ["x", "é"]})
    expected = '{\n  "a": [\n    "x",\n    "é"\n  ],\n  "b": 1\n}\n'
    assert p.read_bytes() == expected.encode("utf-8"), "Use indent=2, sort_keys=True, ensure_ascii=False, UTF-8, and a final newline."


def test_round_trip(tmp_path):
    data = {"name": "Zoë", "tags": ["a", "b"], "n": {"x": 1.5, "y": None, "ok": True}}
    p = tmp_path / "d.json"
    save_json(str(p), data)
    assert load_json(str(p)) == data, "load_json must give back the same data."


def test_keys_sorted(tmp_path):
    p = tmp_path / "k.json"
    save_json(p, {"zeta": 1, "alpha": 2, "mid": 3})
    keys = [line.split('"')[1] for line in p.read_text(encoding="utf-8").splitlines()[1:-1]]
    assert keys == ["alpha", "mid", "zeta"], "Pass sort_keys=True so the keys come out in order."


def test_unicode_kept(tmp_path):
    p = tmp_path / "u.json"
    save_json(p, {"city": "₹ Pune"})
    assert "\\u" not in p.read_text(encoding="utf-8"), "Non-ASCII must not be escaped. Use ensure_ascii=False."


def test_overwrites(tmp_path):
    p = tmp_path / "o.json"
    save_json(p, {"long": "x" * 200})
    save_json(p, {"a": 1})
    assert load_json(p) == {"a": 1}, "The second save must replace the first (mode 'w')."
