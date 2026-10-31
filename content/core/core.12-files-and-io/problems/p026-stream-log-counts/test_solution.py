import builtins


class Guard:
    """Wraps a real file. Bulk reads are refused, so the function must go line by line."""

    def __init__(self, real):
        self._real = real

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *exc):
        return self._real.__exit__(*exc)

    def __iter__(self):
        return iter(self._real)

    def __next__(self):
        return next(self._real)

    def readline(self, *args):
        return self._real.readline(*args)

    def read(self, *args):
        raise AssertionError("Do not call f.read(). Loop over the file (for line in f) so only one line is in memory.")

    def readlines(self, *args):
        raise AssertionError("Do not call f.readlines(). Loop over the file (for line in f) so only one line is in memory.")

    def close(self):
        self._real.close()


def guard_open(monkeypatch):
    real_open = builtins.open

    def fake_open(*args, **kwargs):
        return Guard(real_open(*args, **kwargs))

    monkeypatch.setattr(builtins, "open", fake_open)

import pytest

from solution import count_levels


def write(tmp_path, text):
    path = tmp_path / "app.log"
    path.write_text(text, encoding="utf-8")
    return path


def test_small_log(tmp_path):
    path = write(tmp_path, "2024-05-01 10:15:02 INFO started\n"
                           "2024-05-01 10:15:03 ERROR disk full: ERROR 28\n"
                           "broken line\n"
                           "\n"
                           "2024-05-01 10:15:04 INFO stopped\n")
    assert count_levels(path) == {"INFO": 2, "ERROR": 1}, "The level is the third word. Skip lines with fewer than 3 words, and do not count words inside the message."


def test_empty_file(tmp_path):
    assert count_levels(write(tmp_path, "")) == {}, "An empty file has no lines, so the result is an empty dict."


def test_last_line_without_newline(tmp_path):
    path = write(tmp_path, "2024-05-01 10:15:02 WARN a\n2024-05-01 10:15:03 WARN b")
    assert count_levels(path) == {"WARN": 2}, "The last line has no newline. It still counts."


def test_message_with_level_word(tmp_path):
    path = write(tmp_path, "2024-05-01 10:15:02 INFO ERROR ERROR ERROR\n")
    assert count_levels(path) == {"INFO": 1}, "Count only the third word, not every word that looks like a level."


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        count_levels(tmp_path / "nope.log")


def test_big_file_streams(tmp_path, monkeypatch):
    levels = ["INFO", "WARN", "ERROR", "DEBUG"]
    lines = [f"2024-05-01 10:15:02 {levels[i % 4]} message number {i}\n" for i in range(50000)]
    lines[10] = "\n"
    lines[20] = "oops\n"
    path = write(tmp_path, "".join(lines))
    guard_open(monkeypatch)
    result = count_levels(path)
    expected = {"INFO": 12500, "WARN": 12500, "ERROR": 12500, "DEBUG": 12500}
    expected["ERROR"] -= 1   # index 10 was blanked
    expected["INFO"] -= 1    # index 20 was broken
    assert result == expected, "Check the counts on the big file: skip the blank and the broken line, and count every other line."
