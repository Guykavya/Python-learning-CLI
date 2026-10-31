import pytest

from solution import sum_column


def write(tmp_path, text):
    p = tmp_path / "t.csv"
    p.write_bytes(text.encode("utf-8"))
    return p


def test_example(tmp_path):
    p = write(tmp_path, 'name,amount\n"Doe, Jane",10\nRavi, 2.5\nMeera,\n')
    result = sum_column(p, "amount")
    assert result == 12.5, "Expected 12.5: a quoted comma is part of the name, a blank cell is skipped, spaces around numbers are fine."
    assert isinstance(result, float), "Return a float."


def test_other_column(tmp_path):
    p = write(tmp_path, "a,b,c\n1,2,3\n4,5,6\n")
    assert sum_column(str(p), "c") == 9.0, "Use the header name, not a fixed position."
    assert sum_column(p, "a") == 5.0, "Column a is 1 + 4."


def test_column_order_does_not_matter(tmp_path):
    p = write(tmp_path, "amount,name\n7,x\n3,y\n")
    assert sum_column(p, "amount") == 10.0, "Look the column up by name."


def test_header_only(tmp_path):
    p = write(tmp_path, "name,amount\n")
    result = sum_column(p, "amount")
    assert result == 0.0 and isinstance(result, float), "No rows gives 0.0 (a float)."


def test_missing_column(tmp_path):
    p = write(tmp_path, "name,amount\nx,1\n")
    with pytest.raises(KeyError):
        sum_column(p, "price")


def test_quoted_newline_inside_field(tmp_path):
    p = write(tmp_path, 'note,amount\n"line one\nline two",4\nplain,6\n')
    assert sum_column(p, "amount") == 10.0, 'A quoted field can contain a line break. Open with newline="" and use the csv module.'


def test_unicode_and_windows_endings(tmp_path):
    p = write(tmp_path, "name,amount\r\nZoë,1.5\r\nÅke,2\r\n")
    assert sum_column(p, "amount") == 3.5, "Use encoding='utf-8'. CRLF line endings must work."
