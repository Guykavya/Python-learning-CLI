import csv

from solution import write_rows


def read_back(p):
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.reader(f))


def test_quoting(tmp_path):
    p = tmp_path / "o.csv"
    n = write_rows(p, ["name", "note"], [["Doe, Jane", 'said "hi"'], ["Ravi", 2]])
    assert n == 2, "Return the number of data rows (the header is not counted)."
    text = p.read_bytes().decode("utf-8")
    assert text == 'name,note\r\n"Doe, Jane","said ""hi"""\r\nRavi,2\r\n', "Use csv.writer: it quotes commas and doubles inner quotes."


def test_no_double_carriage_return(tmp_path):
    p = tmp_path / "o.csv"
    write_rows(str(p), ["a"], [["x"], ["y"]])
    assert b"\r\r\n" not in p.read_bytes(), 'Open the file with newline="" so Python does not change the writer\'s line endings.'


def test_round_trip_with_newline_in_field(tmp_path):
    p = tmp_path / "o.csv"
    rows = [["line one\nline two", "b"], ["é, ₹", "d"]]
    write_rows(p, ["x", "y"], rows)
    assert read_back(p) == [["x", "y"]] + rows, "Fields with commas and line breaks must survive a write and read."


def test_numbers_become_text(tmp_path):
    p = tmp_path / "o.csv"
    write_rows(p, ["n", "f"], [[1, 2.5]])
    assert read_back(p) == [["n", "f"], ["1", "2.5"]], "The writer converts numbers to text for you."


def test_overwrites(tmp_path):
    p = tmp_path / "o.csv"
    write_rows(p, ["a"], [["1"], ["2"], ["3"]])
    assert write_rows(p, ["b"], []) == 0, "No rows gives 0."
    assert read_back(p) == [["b"]], "The second call must replace the file: mode 'w', not 'a'."
