import pytest

from solution import append_log, rotate_logs


def names(folder):
    return sorted(p.name for p in folder.iterdir())


def test_full_rotation(tmp_path):
    for name, text in [("app.log", "live"), ("app.log.1", "one"), ("app.log.2", "two"), ("app.log.3", "three")]:
        (tmp_path / name).write_text(text)
    rotate_logs(tmp_path / "app.log", keep=3)
    assert names(tmp_path) == ["app.log.1", "app.log.2", "app.log.3"], "After rotating, app.log is gone, and there are exactly .1 .2 .3."
    assert (tmp_path / "app.log.1").read_text() == "live", "The live file becomes .1."
    assert (tmp_path / "app.log.2").read_text() == "one", "Old .1 becomes .2. Move the oldest file first so nothing is overwritten."
    assert (tmp_path / "app.log.3").read_text() == "two", "Old .2 becomes .3, and the old .3 is deleted."


def test_only_live_file(tmp_path):
    (tmp_path / "app.log").write_text("x")
    rotate_logs(tmp_path / "app.log")
    assert names(tmp_path) == ["app.log.1"], "With no old files, the live file just becomes .1."


def test_missing_live_file_still_shifts(tmp_path):
    (tmp_path / "app.log.1").write_text("one")
    rotate_logs(tmp_path / "app.log", keep=3)
    assert names(tmp_path) == ["app.log.2"], "If app.log does not exist, only the older files move. Do not crash."


def test_gap_is_fine(tmp_path):
    (tmp_path / "app.log").write_text("live")
    (tmp_path / "app.log.2").write_text("two")
    rotate_logs(tmp_path / "app.log", keep=3)
    assert names(tmp_path) == ["app.log.1", "app.log.3"], "A missing .1 is skipped. Old .2 goes to .3."
    assert (tmp_path / "app.log.3").read_text() == "two", "The content moves with the name."


def test_keep_one(tmp_path):
    (tmp_path / "app.log").write_text("new")
    (tmp_path / "app.log.1").write_text("old")
    rotate_logs(tmp_path / "app.log", keep=1)
    assert names(tmp_path) == ["app.log.1"], "With keep=1 only one old file survives."
    assert (tmp_path / "app.log.1").read_text() == "new", "The newest content is in .1."


def test_other_files_untouched(tmp_path):
    for name in ["app.log", "app.log.old", "other.log", "other.log.1", "notes.txt"]:
        (tmp_path / name).write_text(name)
    rotate_logs(tmp_path / "app.log")
    assert names(tmp_path) == ["app.log.1", "app.log.old", "notes.txt", "other.log", "other.log.1"], "Touch only app.log and app.log.<number>."
    assert (tmp_path / "other.log.1").read_text() == "other.log.1", "Other files keep their content."


def test_keep_must_be_positive(tmp_path):
    with pytest.raises(ValueError):
        rotate_logs(tmp_path / "app.log", keep=0)


def test_repeated_rotation_keeps_three(tmp_path):
    live = tmp_path / "app.log"
    for i in range(1, 6):
        live.write_text(f"v{i}")
        rotate_logs(live, keep=3)
    assert names(tmp_path) == ["app.log.1", "app.log.2", "app.log.3"], "After 5 rotations with keep=3 only 3 old files exist."
    assert [(tmp_path / f"app.log.{i}").read_text() for i in (1, 2, 3)] == ["v5", "v4", "v3"], "Newest first: .1 is the latest, .3 the oldest that is kept."


def test_append_creates_and_appends(tmp_path):
    live = tmp_path / "app.log"
    append_log(live, "first")
    append_log(live, "second")
    assert live.read_text() == "first\nsecond\n", "append_log adds one line with a newline each time."


def test_append_rotates_when_full(tmp_path):
    live = tmp_path / "app.log"
    for line in ["aaaa", "bbbb", "cccc"]:      # 5 bytes each with the newline
        append_log(live, line, max_bytes=10, keep=2)
    assert live.read_text() == "cccc\n", "The third line would make 15 bytes, so the file is rotated first and a new file starts."
    assert (tmp_path / "app.log.1").read_text() == "aaaa\nbbbb\n", "The full file moved to .1."
    append_log(live, "dddd", max_bytes=10, keep=2)
    assert live.read_text() == "cccc\ndddd\n", "10 bytes is not more than max_bytes, so no rotation yet."
    append_log(live, "eeee", max_bytes=10, keep=2)
    assert live.read_text() == "eeee\n", "Rotated again: a new live file starts."
    assert (tmp_path / "app.log.1").read_text() == "cccc\ndddd\n", "The newest old file is .1."
    assert (tmp_path / "app.log.2").read_text() == "aaaa\nbbbb\n", "The previous old file moved to .2."


def test_exactly_max_bytes_does_not_rotate(tmp_path):
    live = tmp_path / "app.log"
    append_log(live, "abcd", max_bytes=10)
    append_log(live, "efgh", max_bytes=10)     # 5 + 5 = 10, not bigger than 10
    assert names(tmp_path) == ["app.log"], "Rotate only when the size would be bigger than max_bytes."
    assert live.read_text() == "abcd\nefgh\n", "Both lines are in the live file."


def test_size_counts_bytes_not_characters(tmp_path):
    live = tmp_path / "app.log"
    append_log(live, "\u20b9\u20b9", max_bytes=8)      # 6 bytes + 1 newline = 7
    append_log(live, "x", max_bytes=8)                  # 7 + 2 = 9 > 8
    assert (tmp_path / "app.log.1").exists(), "Each rupee sign uses 3 bytes in UTF-8. Measure len(text.encode('utf-8'))."
