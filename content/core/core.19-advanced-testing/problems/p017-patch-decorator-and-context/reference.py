from unittest.mock import patch

import pytest

from target import backup

P = "/home/you/notes.txt"


@patch("target.shutil.copy")
@patch("target.os.path.exists", return_value=True)
def test_copies_to_bak_and_returns_the_new_path(exists_mock, copy_mock):
    assert backup(P) == P + ".bak", "backup must return the path of the copy."
    copy_mock.assert_called_once_with(P, P + ".bak")


def test_missing_file_raises_and_copies_nothing():
    with patch("target.os.path.exists", return_value=False):
        with patch("target.shutil.copy") as copy_mock:
            with pytest.raises(FileNotFoundError):
                backup(P)
            copy_mock.assert_not_called()


@patch("target.shutil.copy")
@patch("target.os.path.exists", return_value=True)
def test_exists_is_asked_about_the_original(exists_mock, copy_mock):
    backup(P)
    exists_mock.assert_called_once_with(P)


def test_copy_failure_is_not_hidden():
    with patch("target.os.path.exists", return_value=True):
        with patch("target.shutil.copy", side_effect=PermissionError("no")):
            with pytest.raises(PermissionError):
                backup(P)
