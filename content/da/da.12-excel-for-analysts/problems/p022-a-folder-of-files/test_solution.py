import numpy as np
import pandas as pd
import pytest

from solution import combine_folder


def write(folder, name, text):
    (folder / name).write_text(text, encoding="utf-8")


def test_stack_with_source_and_text_values(tmp_path):
    write(tmp_path, "orders_02.csv", "order_id,units,code\nO3,7,007\n")
    write(tmp_path, "orders_01.csv", "order_id,units,code\nO1,3,001\nO2,5,002\n")
    got = combine_folder(tmp_path)
    assert got["order_id"].tolist() == ["O1", "O2", "O3"], "files are read in sorted name order."
    assert got["source"].tolist() == ["orders_01.csv", "orders_01.csv", "orders_02.csv"] and list(got.columns)[-1] == "source", "source column last, with the file name."
    assert got["code"].tolist() == ["001", "002", "007"], "values stay text: '007' must not become 7."
    assert list(got.index) == [0, 1, 2]


def test_empty_file_and_repeated_header_are_skipped(tmp_path):
    write(tmp_path, "a.csv", "order_id,units\nO1,3\n")
    write(tmp_path, "b.csv", "")
    write(tmp_path, "c.csv", "order_id,units\norder_id,units\nO2,4\n")
    got = combine_folder(tmp_path)
    assert got["order_id"].tolist() == ["O1", "O2"], f"the empty file and the repeated header row must disappear; got {got['order_id'].tolist()}"
    assert set(got["source"]) == {"a.csv", "c.csv"}


def test_column_order_may_differ_but_names_may_not(tmp_path):
    write(tmp_path, "a.csv", "order_id,units\nO1,3\n")
    write(tmp_path, "b.csv", "units,order_id\n4,O2\n")
    got = combine_folder(tmp_path)
    assert list(got.columns) == ["order_id", "units", "source"] and got["units"].tolist() == ["3", "4"], "use the column order of the first file."
    write(tmp_path, "c.csv", "order_id,qty\nO3,1\n")
    with pytest.raises(ValueError, match="columns differ in c.csv"):
        combine_folder(tmp_path)


def test_empty_folder(tmp_path):
    assert len(combine_folder(tmp_path)) == 0, "no usable file: an empty DataFrame."
    write(tmp_path, "only_empty.csv", "")
    assert len(combine_folder(tmp_path)) == 0
