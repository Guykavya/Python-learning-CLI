import csv
import json

from solution import csv_to_json, json_to_csv


def put_csv(tmp_path, text):
    path = tmp_path / "in.csv"
    path.write_text(text, encoding="utf-8", newline="")
    return path


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_example_with_types(tmp_path):
    src = put_csv(tmp_path, 'name,age,city\nAsha,31,"Pune, MH"\nBo,,Delhi\n')
    out = tmp_path / "out.json"
    assert csv_to_json(src, out, types={"age": int}) == 2, "Return the number of records."
    assert load(out) == [
        {"name": "Asha", "age": 31, "city": "Pune, MH"},
        {"name": "Bo", "age": None, "city": "Delhi"},
    ], "age is converted with int, an empty cell becomes None, and the quoted comma stays in the city."


def test_no_types_keeps_text(tmp_path):
    src = put_csv(tmp_path, "a,b\n1,2\n")
    out = tmp_path / "out.json"
    csv_to_json(src, out)
    assert load(out) == [{"a": "1", "b": "2"}], "Without types every value stays a string."


def test_float_and_unknown_column(tmp_path):
    src = put_csv(tmp_path, "item,price\npen,2.5\nink,\n")
    out = tmp_path / "out.json"
    csv_to_json(src, out, types={"price": float, "missing": int})
    assert load(out) == [{"item": "pen", "price": 2.5}, {"item": "ink", "price": None}], "float works the same way. A column in types that is not in the file is ignored."


def test_header_only(tmp_path):
    src = put_csv(tmp_path, "a,b\n")
    out = tmp_path / "out.json"
    assert csv_to_json(src, out) == 0, "A header with no rows gives 0 records."
    assert load(out) == [], "The JSON file holds an empty list."


def test_unicode_and_embedded_newline(tmp_path):
    src = put_csv(tmp_path, 'name,note\nZo\u00eb,"line1\nline2"\n')
    out = tmp_path / "out.json"
    csv_to_json(src, out)
    assert load(out) == [{"name": "Zo\u00eb", "note": "line1\nline2"}], "Open the csv with newline='' and encoding='utf-8'."


def test_json_to_csv_basic(tmp_path):
    src = tmp_path / "in.json"
    src.write_text(json.dumps([{"a": 1, "b": "x, y"}, {"a": 2, "b": None}]), encoding="utf-8")
    out = tmp_path / "out.csv"
    assert json_to_csv(src, out) == 2, "Return the number of records."
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows == [["a", "b"], ["1", "x, y"], ["2", ""]], "Header first, then the rows. None becomes an empty cell, and the comma is quoted by the csv module."


def test_json_to_csv_missing_keys_and_order(tmp_path):
    src = tmp_path / "in.json"
    src.write_text(json.dumps([{"id": 1}, {"id": 2, "tag": "t"}, {"tag": "u", "extra": 5}]), encoding="utf-8")
    out = tmp_path / "out.csv"
    json_to_csv(src, out)
    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["id", "tag", "extra"], "The columns are all keys of all records, in the order they are first seen."
    assert rows[1:] == [["1", "", ""], ["2", "t", ""], ["", "u", "5"]], "A key that is missing in a record is an empty cell (restval='')."


def test_round_trip(tmp_path):
    src = put_csv(tmp_path, 'n,v\nA,1\nB,2\n')
    mid = tmp_path / "mid.json"
    back = tmp_path / "back.csv"
    csv_to_json(src, mid, types={"v": int})
    json_to_csv(mid, back)
    with open(back, newline="", encoding="utf-8") as f:
        assert list(csv.DictReader(f)) == [{"n": "A", "v": "1"}, {"n": "B", "v": "2"}], "CSV to JSON to CSV must give the same table."
