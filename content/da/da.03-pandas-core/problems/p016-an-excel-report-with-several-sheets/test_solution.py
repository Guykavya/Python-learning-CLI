import pandas as pd

from solution import write_report


def sheets():
    orders = pd.DataFrame({
        "order_id": [10, 11, 12],
        "customer": ["Asha", "Ben", "Chen"],
        "qty": [2, 5, 1],
        "price": [9.5, 4.0, 12.25],
        "date": pd.to_datetime(["2024-03-05", "2024-03-06", "2024-03-07"]),
    })
    customers = pd.DataFrame({"name": ["Asha", "Ben", "Chen"], "city": ["Pune", "Agra", "Delhi"]}, index=[7, 8, 9])
    summary = pd.DataFrame({"metric": ["orders", "units"], "value": [3, 8]})
    return {"orders": orders, "customers": customers, "summary": summary}


def test_every_frame_in_its_own_sheet(tmp_path):
    path = tmp_path / "report.xlsx"
    data = sheets()
    write_report(path, data)
    assert path.exists(), "the workbook was not written to the path given."
    back = pd.read_excel(path, sheet_name=None)
    assert list(back) == ["orders", "customers", "summary"], (
        "the workbook must have three sheets in this order; got %s. A new to_excel(path) per frame overwrites the file: use one pd.ExcelWriter." % list(back))


def test_index_is_not_written(tmp_path):
    path = tmp_path / "report.xlsx"
    write_report(path, sheets())
    back = pd.read_excel(path, sheet_name=None)
    for name, frame in back.items():
        assert not any(str(c).startswith("Unnamed") for c in frame.columns), (
            "sheet %r has an extra index column: pass index=False." % name)
    assert back["customers"].columns.tolist() == ["name", "city"], "the customers' index (7, 8, 9) must not become a column."


def test_values_round_trip(tmp_path):
    path = tmp_path / "report.xlsx"
    data = sheets()
    write_report(path, data)
    back = pd.read_excel(path, sheet_name=None)
    for name, frame in data.items():
        pd.testing.assert_frame_equal(
            back[name].reset_index(drop=True), frame.reset_index(drop=True), check_dtype=False,
            obj="sheet %s read back" % name)


def test_frames_not_changed(tmp_path):
    data = sheets()
    before = {k: v.copy() for k, v in data.items()}
    write_report(tmp_path / "r.xlsx", data)
    for name in data:
        pd.testing.assert_frame_equal(data[name], before[name], obj="frame %s" % name)


def test_a_single_sheet(tmp_path):
    path = tmp_path / "one.xlsx"
    write_report(path, {"only": pd.DataFrame({"a": [1, 2]})})
    back = pd.read_excel(path, sheet_name=None)
    assert list(back) == ["only"] and back["only"]["a"].tolist() == [1, 2]
