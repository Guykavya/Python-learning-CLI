import gc
import warnings

from solution import append_summary

LOG = "10:01 INFO start\n10:02 ERROR disk full\n10:03 WARN slow\n10:04 ERROR timeout\n"


def test_returns_count_and_writes(tmp_path):
    src = tmp_path / "app.log"
    src.write_text(LOG)
    dst = tmp_path / "report.txt"
    assert append_summary(src, dst) == 2, "Count every line that contains ERROR, also when it is not the first word."
    assert dst.read_text() == "errors=2\n", "The summary line is 'errors=2' followed by a newline."


def test_appends_and_keeps_history(tmp_path):
    src = tmp_path / "app.log"
    src.write_text(LOG)
    dst = tmp_path / "report.txt"
    dst.write_text("errors=0\n")
    append_summary(str(src), str(dst))
    assert dst.read_text() == "errors=0\nerrors=2\n", "Old lines must stay: open the summary file with 'a', not 'w'."


def test_second_call_does_not_glue_lines(tmp_path):
    src = tmp_path / "app.log"
    src.write_text("ERROR a\n")
    dst = tmp_path / "report.txt"
    append_summary(src, dst)
    append_summary(src, dst)
    assert dst.read_text() == "errors=1\nerrors=1\n", "End the summary with a newline, or the next one is glued to it."


def test_no_errors(tmp_path):
    src = tmp_path / "app.log"
    src.write_text("10:01 INFO fine\n")
    dst = tmp_path / "report.txt"
    assert append_summary(src, dst) == 0, "No ERROR lines gives 0."
    assert dst.read_text() == "errors=0\n", "Still append errors=0."


def test_files_are_closed(tmp_path):
    src = tmp_path / "app.log"
    src.write_text(LOG)
    dst = tmp_path / "report.txt"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        append_summary(src, dst)
        gc.collect()
        gc.collect()
    leaks = [w for w in caught if issubclass(w.category, ResourceWarning)]
    assert not leaks, "A file was not closed (ResourceWarning). Use `with open(...) as f:` for both files."
